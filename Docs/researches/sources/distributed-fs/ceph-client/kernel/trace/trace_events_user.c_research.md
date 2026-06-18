# sources/distributed-fs/ceph-client/kernel/trace/trace_events_user.c

## Purpose
Implements the `user_events` ABI that lets user space define trace events dynamically, register per-process enable bits, and write event payloads into ftrace and perf. It provides tracefs files for data and status, a dynamic-event provider for persistent user events, and lifecycle hooks for copying enablement metadata across fork/clone and cleaning it up on exit or exec.

## Important APIs, Types, And Functions
Key types are `struct user_event_group`, `struct user_event`, `struct user_event_enabler`, `struct user_event_refs`, `struct user_event_file_info`, and `struct user_event_validator`. `init_group` stores the default namespace group with a hash table of registered events. `current_user_events` and `max_user_events` enforce a global event cap.

Registration and parsing flow through `user_events_ioctl()`, `user_events_ioctl_reg()`, `user_reg_get()`, `user_event_parse_cmd()`, `user_event_parse()`, `find_user_event()`, `user_event_trace_register()`, and `user_events_ref_add()`. Payload writes use `user_events_write()`, `user_events_write_iter()`, and `user_events_write_core()`. Event output is handled by `user_event_ftrace()` and, when enabled, `user_event_perf()`. Dynamic events use `user_event_dops` with `user_event_create()`, `user_event_show()`, `user_event_free()`, and `user_event_match()`.

Enable-bit tracking is implemented by `user_event_enabler_create()`, `user_event_enabler_write()`, `user_event_enabler_update()`, async fault helpers, and mm lifecycle helpers `user_event_mm_dup()` and `user_event_mm_remove()`. Tracefs setup is in `create_user_tracefs()`, and initialization is in `trace_events_user_init()`.

## Control Flow
Opening `user_events_data` allocates `user_event_file_info` for the file. `DIAG_IOCSREG` validates the user ABI struct, checks enable address size/alignment/bit range/accessibility, prevents duplicate enable bits in the same mm, copies the event description, parses or finds a matching event, stores an immutable event pointer in the file's RCU-protected refs array, creates an enabler, and returns the write index to user space.

Event descriptions have the form `name[:flags] field;field...`. Parsing rejects text flags, enforces capability for persistent events, splits fields, computes field offsets starting after `struct trace_entry`, validates supported scalar/array/dynamic-location types, builds validators for `__data_loc` and `__rel_loc` strings, creates the `print_fmt`, populates `trace_event_call` and `trace_event_class`, registers the trace event, adds it to dyn events and the group hash, and increments the global count.

Writes begin with a 32-bit event index, look up the immutable `user_event` from the file refs under sched RCU, enforce minimum payload size, and only proceed when the tracepoint static key is enabled. Each registered tracepoint function gets an independent iov iterator copy. Ftrace writes reserve a trace event buffer, copy payload data with pagefaults disabled, validate dynamic locations, and commit or discard. Perf writes allocate a perf trace buffer and follow the same copy/validation pattern.

Enable state changes originate from trace event registration callbacks in `user_event_reg()`. Successful ftrace/perf registration takes a user-event reference, computes status bits by inspecting tracepoint functions, and updates all registered user mm enable bits. Unregister clears status and drops the reference. Enable writes pin the user page with `FOLL_NOFAULT`; if the page is absent and fixup is allowed, async work faults it in and retries under `event_mutex`.

## State And Persistence
Events live in the group hash and dynamic-event list while referenced. Non-persistent events auto-delete when the last reference drops; persistent events keep an extra self-reference and require capability to delete. File-local refs persist until `user_events_release()`. Per-mm enablers live in `task_struct->user_event_mm`, are globally discoverable through `user_event_mms`, are duplicated on fork/clone, and are removed on mm teardown after RCU/workqueue delay.

The event payload format is not copied into private storage beyond field metadata and validators; user writes must match the declared layout. `user->status` records internal ftrace/perf/other attachment state and is surfaced in `user_events_status`. `max_user_events` is tunable through `/proc/sys/kernel/user_events_max` under `event_mutex`.

## Dependencies And Integration Points
This file integrates tracefs (`user_events_data`, `user_events_status`), dyn events, tracepoints, trace event registration, perf events, RCU, workqueues, user memory pinning/faulting, mm lifecycle hooks, sysctl, and capability checks. It relies on `trace_event_call` visibility changes under temporary root fs credentials so tracefs event files can be added or removed even when the originating process lacks direct tracefs management permissions.

## Risks
The riskiest areas are user memory enable-bit writes, dynamic event lifetime, and payload validation. Incorrect locking around `event_mutex`, group `reg_mutex`, RCU refs, or mmap locks can race with unregister, fork/exec, or mm teardown. Async fault handling must respect `ENABLE_VAL_FAULTING_BIT` and `ENABLE_VAL_FREEING_BIT` to avoid use-after-free. Dynamic string validators must reject out-of-bounds or non-null-terminated data before tracing. Persistent-event capability checks must remain consistent across create and delete paths. The `current_user_events` cap must stay balanced with all destroy paths.

## Test Signals
Strong signals include registering events through ioctl and dyn_events, writing payloads to ftrace and perf, toggling consumers and observing user enable bits, unregistering enable bits, deleting busy versus idle events, and reading `user_events_status`. Negative tests should cover malformed ABI sizes, bad enable alignment, duplicate enable bits, oversized descriptions, unknown field types, invalid dynamic locations, missing null terminators, and exceeding `user_events_max`. Stress tests should fork/exit while enabling/disabling events and run with KASAN/KCSAN/lockdep/RCU diagnostics.
