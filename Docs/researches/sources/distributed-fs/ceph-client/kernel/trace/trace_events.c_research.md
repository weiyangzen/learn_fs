# sources/distributed-fs/ceph-client/kernel/trace/trace_events.c

## Purpose
`trace_events.c` is the core event-tracing manager for the kernel trace subsystem copy in the distributed-fs/Ceph-client source tree. It registers `struct trace_event_call` definitions, creates per-trace-array `struct trace_event_file` instances, builds the tracefs/eventfs `events/` hierarchy, exposes enable/filter/format/id/trigger/PID-control files, and coordinates event enablement with tracepoint registration, perf, triggers, modules, early boot tracing, and self-tests.

Although this path sits under the Ceph-client source mirror, the file is generic Linux tracing infrastructure. It is relevant to distributed filesystem observability because Ceph client tracepoints use this common machinery for runtime enablement, filtering, formatting, tracefs control, and module lifetime handling.

## Important APIs, Types, and Functions
- Global state: `event_mutex`, `ftrace_events`, `ftrace_generic_fields`, `ftrace_common_fields`, `event_subsystems`, `module_strings`, `field_cachep`, `file_cachep`, and `eventdir_initialized` hold registered event calls, shared field definitions, subsystem descriptors, module-owned replacement strings, slab caches, and tracefs initialization state.
- Field management: `trace_define_field()`, `trace_define_field_ext()`, `trace_define_generic_fields()`, `trace_define_common_fields()`, `trace_destroy_fields()`, `trace_event_get_offsets()`, `event_define_fields()`, `trace_find_event_field()`, and `update_event_fields()` build the `format` metadata and filterable field list.
- Print-format validation and updating: `test_event_printk()`, `process_pointer()`, `process_string()`, `handle_dereference_arg()`, `update_event_printk()`, and `trace_event_update_all()` validate unsafe `%p*`/`%s` dereferences and replace enum/eval names with numeric values.
- Event registration: `trace_event_raw_init()`, `event_init()`, `__register_event()`, `trace_add_event_call()`, `trace_remove_event_call()`, `event_remove()`, and `__trace_remove_event_call()` register/unregister event calls and their trace event IDs.
- Event enablement: `trace_event_reg()`, `__ftrace_event_enable_disable()`, `trace_event_enable_disable()`, `ftrace_event_enable_disable()`, `ftrace_set_clr_event()`, `trace_set_clr_event()`, and `trace_array_set_clr_event()` translate tracefs writes and in-kernel requests into tracepoint probe registration/unregistration.
- Ring-buffer entry path: `trace_event_buffer_reserve()` reserves trace records after PID-filter checks and initializes `struct trace_event_buffer`.
- Tracefs/eventfs interfaces: file operations for `available_events`, `set_event`, `show_event_filters`, `show_event_triggers`, `set_event_pid`, `set_event_notrace_pid`, event `enable`, event `format`, event `filter`, subsystem `filter`, subsystem `enable`, and header files connect user-visible tracefs files to seq-file/read/write handlers.
- PID filters: `event_pid_write()`, `register_pid_events()`, `unregister_pid_events()`, `trace_event_follow_fork()`, scheduler hooks, `ignore_task_cpu()`, and `trace_event_ignore_this_pid()` maintain per-trace-array include/exclude PID lists.
- Directory and lifetime handling: `event_subsystem_dir()`, `event_create_dir()`, `remove_event_file_dir()`, `event_file_get()`, `event_file_put()`, `event_trace_add_tracer()`, and `event_trace_del_tracer()` manage eventfs hierarchy, subsystem refcounts, and per-instance file lifetime.
- Module support: `event_mod_load`, `cache_mod()`, `update_mod_cache()`, `trace_module_add_events()`, `trace_module_remove_events()`, and `trace_module_notify()` support module event registration and deferred `set_event:mod:` enablement.
- Dynamic ftrace event commands: under `CONFIG_DYNAMIC_FTRACE`, `event_enable_func()` and associated probe ops implement `enable_event`/`disable_event` ftrace function commands.
- Initialization and tests: `trace_event_init()`, `event_trace_enable()`, `event_trace_init()`, `early_enable_events()`, `event_trace_enable_again()`, `event_trace_self_tests_init()`, and helpers for `CONFIG_EVENT_TRACE_STARTUP_TEST`.

## Control Flow
Initialization starts in `trace_event_init()`. It creates slab caches, initializes syscall trace events, runs `event_trace_enable()` to register static trace event calls from the linker section, creates early `trace_event_file` descriptors for the top trace array, applies `trace_event=` boot parameters, starts trace-printk command recording, and registers ftrace event commands. `event_trace_init_fields()` then defines common and generic filter fields. Later, `event_trace_init()` creates the user-visible tracefs files, attaches event directories to the early descriptors, registers the module notifier, and marks event directories initialized.

When a trace event call is registered, `event_init()` invokes its raw init hook, `__register_event()` links it into `ftrace_events`, and `__add_event_to_tracers()` creates matching `trace_event_file` entries for every existing trace array. `trace_create_new_event()` filters by `tr->system_names`, allocates a `trace_event_file`, copies PID-filter state into flags, initializes trigger lists and reference counts, and appends the file to `tr->events`. If eventfs is live, `event_create_dir()` creates `events/<system>/<event>/` entries and defines fields; otherwise early boot only defines fields.

Enable writes flow through either global `set_event`, subsystem `enable`, per-event `enable`, or in-kernel APIs. `ftrace_set_clr_event()` parses `<system>:<event>` and optional `:mod:<module>` forms. `__ftrace_set_clr_event_nolock()` walks matching `trace_event_file` entries, skips ignored or non-registerable events, and calls `ftrace_event_enable_disable()`. The lower-level `__ftrace_event_enable_disable()` controls command/TGID recording side effects, soft-disable reference counts, `EVENT_FILE_FL_ENABLED`, `EVENT_FILE_FL_SOFT_DISABLED`, and calls the event class `reg()` hook. For tracepoint events, `trace_event_reg()` maps this to `tracepoint_probe_register()` or `tracepoint_probe_unregister()`, with perf-specific register operations when enabled.

Runtime event recording normally enters generated tracepoint code, which calls `trace_event_buffer_reserve()`. This checks `EVENT_FILE_FL_PID_FILTER` and the per-CPU `ignore_pid` state, computes tracing context, reserves a ring-buffer event via `trace_event_buffer_lock_reserve()`, and returns the event payload pointer to the generated assign/commit path.

Filter and trigger visibility is split across this file and filter/trigger helpers. Per-event `filter` writes call `apply_event_filter()` from `trace_events_filter.c`; subsystem `filter` writes call `apply_subsystem_event_filter()`. `show_event_filters` and `show_event_triggers` iterate enabled metadata under `event_mutex` and print event-qualified filter or trigger strings.

PID filtering is driven by writes to `set_event_pid` and `set_event_notrace_pid`. `event_pid_write()` updates the appropriate `trace_pid_list`, sets `EVENT_FILE_FL_PID_FILTER` on every file in the trace array, registers scheduler tracepoint probes when needed, synchronizes and frees old lists, and runs `ignore_task_cpu()` on each CPU to seed current per-CPU ignore state. Scheduler hooks update `ignore_pid` before and after sched switch and wakeup events so event probes can cheaply reject records from ignored tasks.

On module load, `trace_module_notify()` adds module trace events under `event_mutex` and `trace_types_lock`, then applies cached `:mod:` requests. On module unload it removes matching event calls, frees module-owned field type strings created by enum/eval replacement, and resets online CPU buffers to avoid stale ring-buffer records being interpreted with reused event IDs.

## State and Persistence
The file has no durable storage. State is in kernel memory, trace arrays, eventfs dentries/inodes, module notifier state, and boot-parameter buffers. Key persistent-for-runtime structures are `struct trace_event_call` in `ftrace_events`, `struct trace_event_file` per trace array, `struct event_subsystem` shared by same-named systems, `struct trace_subsystem_dir` per trace array/system, per-event filters and triggers, PID include/exclude lists, and module-deferred event requests in `tr->mod_events`.

Reference counts protect subsystem directories and event files: subsystem refs are incremented on open and when reused across trace arrays; event files are refcounted for eventfs file lifetime and freed after `EVENT_FILE_FL_FREED` is set. RCU is used for PID lists and filters, while tracepoint synchronization ensures old probes and filters are no longer executing before memory is freed.

Boot state includes `bootup_event_buf` for `trace_event=` and `bootup_triggers` for `trace_trigger=`. These are applied during early initialization so events can be active before tracefs exists, then later attached to real eventfs directories.

## Dependencies and Integration Points
This file depends on the tracing core (`trace.h`, `trace_output.h`, trace arrays, trace buffers, trace parser, trace flags), eventfs/tracefs, tracepoints, perf events, syscall tracing, ftrace function probes, trigger and histogram files, PID list helpers, ring-buffer formatting, module notifiers, security lockdown checks, RCU, SRCU/tracepoint synchronization, lockdep, workqueues, kthreads, and boot parameter parsing.

Important integration points include generated `TRACE_EVENT` descriptors, `trace_events_filter.c` for parsing/applying filters, trigger code for `trigger` and boot triggers, perf for `id` files and event profile filters, module lifecycle hooks for load/unload, scheduler tracepoints for PID filters, and function tracing commands for function-probe-based event enable/disable.

## Risks
- Lock ordering is delicate: many paths require `event_mutex`; directory creation/removal also uses `trace_types_lock` and `trace_event_sem`; module notifications nest these locks. Reordering can deadlock.
- Enable/disable and soft-disable behavior is subtle. Soft mode keeps tracepoints registered while suppressing event recording, so removal paths must explicitly reject enabled files and not rely only on normal disable calls.
- RCU-protected filters and PID lists require delayed freeing and tracepoint synchronization. Freeing too early risks use-after-free in active tracepoint probes.
- Module unload can leave stale event IDs in ring buffers, so reset behavior is required. Missing it can cause later decoding with the wrong event format.
- Field metadata is shared by event classes. Defining, updating, and destroying fields must account for class reuse and module-owned strings.
- `test_event_printk()` is a heuristic validator, not a full C expression parser. It catches common unsafe dereferences but can allow or warn on unusual formatting expressions.
- Tracefs write handlers mutate user buffers after parsing to restore separators; callers that reuse strings must tolerate this convention.

## Test Signals
Useful signals include successful creation of `available_events`, `set_event`, `events/<system>/<event>/format`, `enable`, `filter`, and `trigger` files; boot with `trace_event=` and `trace_trigger=`; enabling/disabling individual, subsystem, and all events; writes to `set_event_pid` and `set_event_notrace_pid`; module load/unload with `:mod:` cached enablement; `show_event_filters` and `show_event_triggers` output; tracefs lockdown denial paths; perf event ID availability; and `CONFIG_EVENT_TRACE_STARTUP_TEST` logs showing per-event, per-subsystem, all-event, and function-tracer-combined tests passing.
