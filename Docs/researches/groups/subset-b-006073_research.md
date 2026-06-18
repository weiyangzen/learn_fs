# subset-b-006073 Research

Grouped research for Linux kernel tracing files under the Ceph client source mirror. Each section preserves its source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_trigger.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_events_trigger.c

## Purpose
Implements trace event trigger infrastructure for tracefs event `trigger` files. It lets users attach commands such as `traceon`, `traceoff`, `snapshot`, `stacktrace`, `enable_event`, `disable_event`, and histogram-related commands to trace events, optionally with counts and filters. Runtime trigger dispatch is integrated into tracepoint event emission so triggers can fire before or after an event is committed.

## Important APIs, Types, And Functions
The central state is `struct event_trigger_data`, owned by a per-event `trace_event_file->triggers` RCU list and configured by `struct event_command` operations. The file maintains a global `trigger_commands` registry protected by `trigger_cmd_mutex`, a global `named_triggers` list for shared named trigger data, and a deferred free path using `trigger_data_free_list`, `trigger_data_kthread_mutex`, and `trigger_kthread`.

Primary exported or shared APIs include `event_triggers_call()`, `event_triggers_post_call()`, `__trace_trigger_soft_disabled()`, `trigger_process_regex()`, `register_event_command()`, `unregister_event_command()`, `event_trigger_count()`, `event_trigger_init()`, `trace_event_trigger_enable_disable()`, `clear_event_triggers()`, `update_cond_flag()`, `trigger_data_alloc()`, `event_trigger_parse_num()`, `set_trigger_filter()`, named-trigger helpers, and enable/disable trigger helpers. `event_trigger_fops` wires the event `trigger` file to open/read/write/release callbacks.

## Control Flow
When a trace event fires, `event_triggers_call()` walks `file->triggers` under RCU. It skips paused entries, checks optional event filters against the just-created record, executes immediate triggers through `data_ops_trigger()`, and returns a bitmask for post triggers. `event_triggers_post_call()` later walks the same list and executes triggers whose `trigger_type` bit was returned. `__trace_trigger_soft_disabled()` is the fast-path gate for events that are otherwise soft-disabled but still need trigger-mode evaluation.

User configuration enters through tracefs `trigger` writes. `event_trigger_regex_write()` copies a bounded user buffer, locks `event_mutex`, resolves the `trace_event_file`, and calls `trigger_process_regex()`. The parser splits command name, optional removal prefix `!`, colon parameters, and optional `if` filters. Generic `event_trigger_parse()` allocates trigger data, parses count values, installs filters, bumps temporary references, and calls the command-specific register function. Removal paths create a temporary match object and call the command-specific unregister operation.

Registration adds trigger data to `file->triggers` with `list_add_rcu()`, updates `EVENT_FILE_FL_TRIGGER_COND` when filters/post triggers/record-dependent commands require deferred evaluation, and toggles trigger mode by incrementing `tm_ref` through `trace_event_trigger_enable_disable()`. Enable/disable-event triggers also hold a reference to the target event call and enable soft mode on that target.

## State And Persistence
Trigger definitions persist in kernel memory while present in the tracefs event trigger list. Counts are stored in `event_trigger_data->count`, with `-1` meaning unlimited. Filters are RCU-published via `event_trigger_data->filter` and mirrored as printable `filter_str`. `tm_ref`, `sm_ref`, and event file flags record trigger-mode and soft-mode state. Named triggers share common data by storing a first owner in `named_triggers` and pointing later entries at it through `named_data`.

Freeing is intentionally deferred. `trigger_data_free()` clears filters, queues data on an llist, and wakes the `trigger_data_free` kthread, which calls `tracepoint_synchronize_unregister()` before `kfree()`. Boot-time failures are handled by queuing and draining later in `trigger_data_free_init()` or synchronously if kthread creation fails.

## Dependencies And Integration Points
The file depends on trace core types in `trace.h`, trace event filters, tracefs file lifetimes, RCU list traversal, tracepoint unregister synchronization, the tracing snapshot subsystem, stack tracing, dynamic ftrace histogram support, and event module reference helpers. It integrates with trace event emission paths, event file flags, `tracing_on`, snapshot buffers, stack capture, and cross-event enable/disable behavior.

## Risks
The main risks are lifetime and concurrency bugs: trigger data is read from tracepoint context while users can remove triggers, so RCU and `tracepoint_synchronize_unregister()` ordering is critical. Filter replacement must not expose partially initialized filters or leak failed filters. Register/unregister paths must keep `tm_ref`, target event references, and soft-mode flags balanced, especially on partial failures. Counted triggers execute on multiple CPUs without strong serialization beyond the trigger data operations, so count semantics are best-effort for concurrent hits. Named triggers share data across entries, making pause/unpause and deletion correctness dependent on consistent `name` handling.

## Test Signals
Useful signals are tracefs trigger smoke tests: writing valid/invalid commands, removing with `!`, reading back available and active triggers, and checking `traceon`, `traceoff`, `stacktrace`, `snapshot`, and enable/disable behavior. Filter tests should verify `if` syntax, failed filter cleanup, and conditional post-trigger execution. Concurrency tests should repeatedly add/remove triggers while generating the event and watching for KASAN/KCSAN/RCU warnings, leaked event references, and stale trigger-mode flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_user.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_events_user.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_export.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_export.c

## Purpose
Builds exported trace event descriptors for core ftrace events from `trace_entries.h`. It uses repeated macro redefinition to generate compile-time structure checks, field metadata arrays, `trace_event_class` objects, `trace_event_call` objects, and `_ftrace_events` section entries.

## Important APIs, Types, And Functions
The only ordinary function is `ftrace_event_is_function()`, which identifies the `event_function` trace event. `ftrace_event_register()` is a stub registration callback used for entries with triggers. Most behavior is macro-driven through `FTRACE_ENTRY`, `FTRACE_ENTRY_REG`, `FTRACE_ENTRY_DUP`, field macros such as `__field`, `__array`, and `__dynamic_array`, and the included `trace_entries.h`.

## Control Flow
The file includes `trace_entries.h` three times with different macro meanings. The first pass emits temporary `____ftrace_*` structs and `____ftrace_check_*()` functions that force the printk format strings to compile against the entry structure. The second pass emits `ftrace_event_fields_*` arrays used by trace event formatting and filtering. The third pass emits `trace_event_class` and `trace_event_call` definitions and places pointers in the `_ftrace_events` linker section for discovery by the trace core.

## State And Persistence
All generated event metadata is static kernel data. There is no runtime mutable state in this file except trace-core state attached to the generated `trace_event_call` instances elsewhere. Generated calls are marked `TRACE_EVENT_FL_IGNORE_ENABLE`, so their enable semantics are special to ftrace internals.

## Dependencies And Integration Points
This file depends on `trace_entries.h`, `trace_output.h`, kallsyms/stringification helpers, filter type constants, and the trace event linker-section discovery mechanism. It is a bridge between low-level ftrace ring-buffer entry definitions and user-visible trace event metadata consumable by tracefs and perf.

## Risks
The macro layering is brittle: changing a field macro in one pass without matching the others can create mismatched C structs, field metadata, or print formats. Packed fields, dynamic arrays, and special filter types such as `FILTER_TRACE_FN` must preserve the ABI expected by filtering and output code. Since most definitions are generated at compile time, failures can appear as build errors or subtle runtime formatting/filtering mismatches.

## Test Signals
Primary signals are successful kernel build, no printk format warnings from generated check functions, and trace event registration of ftrace events at boot. Runtime smoke tests include reading ftrace event format files, filtering on function fields, enabling perf access to generated events that use registration functions, and verifying `ftrace_event_is_function()` consumers detect the function event correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_export.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_fprobe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_fprobe.c

## Purpose
Implements fprobe-backed dynamic tracing events. Users can create fentry probes, fexit probes, and tracepoint probes with fetch arguments; the resulting events can feed ftrace and perf and can be managed through the dynamic-event interface.

## Important APIs, Types, And Functions
The main object is `struct trace_fprobe`, containing a `dyn_event`, `struct fprobe`, target symbol name, tracepoint-probe flag, optional `tracepoint_user`, and embedded `struct trace_probe`. `struct tracepoint_user` tracks tracepoint names, loaded tracepoint pointers, and references so tracepoint probes can survive module load/unload transitions.

Dynamic-event operations are in `trace_fprobe_ops`: create, show, busy check, free, and match. Runtime handlers include `fentry_dispatcher()`, `fexit_dispatcher()`, `trace_fprobe_entry_handler()`, `fentry_trace_func()`, `fexit_trace_func()`, and perf equivalents. Registration helpers include `register_trace_fprobe_event()`, `append_trace_fprobe_event()`, `__register_trace_fprobe()`, `__unregister_trace_fprobe()`, `enable_trace_fprobe()`, `disable_trace_fprobe()`, and the trace event `.reg` callback `fprobe_register()`.

## Control Flow
Creation starts at `trace_fprobe_create()`, which tokenizes the raw command and calls `trace_fprobe_create_internal()`. Supported command forms are fentry (`f:`), fexit (`f... %return` or `$retval` fetch), and tracepoint (`t:`). Parsing derives group/event names, validates symbols or tracepoint names, expands BTF/meta/dentry arguments, parses fetch arguments into trace-probe instructions, configures return-probe entry data when needed, builds a print format, and registers or appends the probe event under `event_mutex`.

When an event is enabled by ftrace or perf, `fprobe_register()` calls `enable_trace_fprobe()`. The first enable of a trace-probe event registers each sibling fprobe. Normal function probes call `register_fprobe()`, while tracepoint probes find or create a `tracepoint_user`, register the tracepoint probestub if loaded, and then register an fprobe against the probestub address. Disable removes file links or perf flags; when no consumers remain, it unregisters fprobes and releases tracepoint users.

On hit, fentry and fexit dispatchers inspect trace-probe flags and send data to ftrace and/or perf. They compute dynamic data size, reserve the right buffer, store the entry IP or return IP/function pair, evaluate fetch instructions from `ftrace_regs` and optional entry data, and commit. The return path can capture selected entry arguments into fprobe entry data for later use by fexit fetch instructions.

## State And Persistence
Dynamic fprobe events persist in the dyn-event registry until explicitly removed and not busy. Sibling probes can share one trace event when group/event names and argument types match. `tracepoint_user_list` persists tracepoint-name users across modules; entries can have a null `tpoint` when the tracepoint is not currently loaded. Module notifiers re-register tracepoint users and fprobes when modules come and unregister fprobes before tracepoint memory disappears.

## Dependencies And Integration Points
This file depends on fprobe, trace probes, dyn events, trace event registration, tracepoint iteration, module notifiers, kallsyms, perf events, lockdown checks (`LOCKDOWN_KPROBES`), and fetch-argument helpers from `trace_probe`. It integrates with tracefs dynamic event commands, ftrace event enabling, perf event registration, and module load/unload notifications.

## Risks
Important risks are target lifetime and probe registration ordering. Function probes are verified before registration but module lifetime is not locked for ordinary symbols, so registration can still fail later. Tracepoint probes depend on notifier ordering: the tracepoint-user notifier must update `tpoint` before the fprobe notifier registers or unregisters the probestub fprobe. Return probes with entry data must enforce `MAX_FPROBE_DATA_SIZE`. Fetch instruction processing runs in probe context and must not fault unexpectedly. Busy checks must prevent removing events that ftrace/perf still reference.

## Test Signals
Tests should create fentry, fexit, and tracepoint probes through dynamic events; fetch `$argN`, `$retval`, `$stack`, symbol memory, and aliases; enable through ftrace and perf; and verify output formats and field definitions. Negative tests should cover bad event names, tracepoint names with illegal characters, `$retval` on tracepoint probes, too many args, oversized entry data, duplicate same probes, and locked-down environments. Module tests should load/unload a module with a tracepoint while a tracepoint probe exists and check for correct rebind and no stale fprobe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_fprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_functions.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_functions.c

## Purpose
Implements the ring-buffer based `function` tracer and dynamic ftrace function commands. It records function-entry events, optionally records arguments, stack traces, or repeat compression, and lets users attach per-function commands such as `traceon`, `traceoff`, `stacktrace`, `dump`, and `cpudump` through ftrace filters.

## Important APIs, Types, And Functions
Tracer setup uses `ftrace_allocate_ftrace_ops()`, `ftrace_create_function_files()`, `function_trace_init()`, `function_trace_reset()`, `function_trace_start()`, `func_set_flag()`, and `init_function_trace()`. Runtime callbacks include `function_trace_call()`, `function_args_trace_call()`, `function_stack_trace_call()`, `function_no_repeats_trace_call()`, and `function_stack_no_repeats_trace_call()`.

Options are stored in `func_flags` with bits for stack traces, no repeats, and argument capture. Per-instance ftrace operations live in `trace_array->ops`; repeat compression uses per-CPU `trace_func_repeats`. Dynamic command callbacks are represented by `struct ftrace_func_command` and `struct ftrace_probe_ops`.

## Control Flow
Initialization selects the callback matching current tracer options, allocates repeat state if required, initializes ftrace array ops, records the current CPU, starts command-line recording, and registers the ftrace function. On callback, the tracer checks `function_enabled`, applies recursion protection or per-CPU disabled counters for stack cases, resolves true parent IP when the function graph return trampoline is involved, builds trace context, and calls `trace_function()`.

The no-repeat callbacks compare current IP/parent IP against per-CPU last state. Repeated calls update timestamps and counts instead of emitting every event; the next different function flushes the repeat summary through `trace_last_func_repeats()`. Stack variants emit `__trace_stack()` after function tracing. Option changes while the function tracer is active unregister the old ftrace function, swap `ops->func`, and re-register.

Dynamic ftrace commands are registered when `CONFIG_DYNAMIC_FTRACE` is enabled. Writing commands through ftrace filter infrastructure invokes callbacks that parse optional counts, register or unregister per-function probes, and use mapper-backed counters when counts are requested. Probe callbacks toggle tracing, dump all or current CPU buffers, or emit stack traces.

## State And Persistence
Function tracer state is attached to each `trace_array`: ftrace ops, current flags, `function_enabled`, repeat buffers, and filter files. Dynamic command state persists in ftrace function probe registrations and optional `ftrace_func_mapper` count storage. `tracing_on` changes are global or trace-array scoped through tracer helpers; command counters are mutable and decrement on hits.

## Dependencies And Integration Points
This file integrates with the ftrace core, trace arrays and instances, function graph support for parent IP correction and graph ops allocation, stack tracing, command-line recording, ring-buffer trace functions, dynamic ftrace command registration, and ftrace filter files. It also participates in ftrace selftests when configured.

## Risks
Callback context is hot and recursion-prone, so recursion guards, IRQ state handling, and per-CPU disabled counters are critical. Switching callbacks while tracing must unregister/register in the right order. Repeat compression intentionally has weak synchronization around interrupts and can lose exact counts, as noted in the source comment. Counted function commands use pointer-cast counts and mapper state, so registration/free paths must stay balanced. Stack tracing from ftrace callbacks is especially sensitive to skip counts and unwinder configuration.

## Test Signals
Signals include enabling the `function` tracer, toggling `func_stack_trace`, `func-no-repeats`, and `func-args`, validating output and repeat summaries, and using instance-specific filters. Dynamic command tests should write `traceon`, `traceoff`, `stacktrace`, `dump`, and `cpudump` commands with and without counts to `set_ftrace_filter`, then remove them with `!`. Stress signals include concurrent option changes, ftrace filter updates, and lockdep/recursion warnings under high function-call load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_functions.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_functions_graph.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_functions_graph.c

## Purpose
Implements the `function_graph` tracer. It records function entry and return events, computes durations, optionally captures arguments, return values, and return addresses, filters IRQ and sleep-time accounting, and formats nested graph output for trace and pipe readers.

## Important APIs, Types, And Functions
Important per-open state is `struct fgraph_data` with per-CPU `struct fgraph_cpu_data` for last pid, nesting depth, IRQ depth, ignored events, and entered functions. Runtime graph hooks are `graph_entry()`, `trace_graph_entry()`, `trace_graph_entry_args()`, `trace_graph_return()`, and `trace_graph_thresh_return()`. Ring-buffer writers are `__trace_graph_entry()`, `__trace_graph_retaddr_entry()`, and `__trace_graph_return()`.

Tracer lifecycle uses `allocate_fgraph_ops()`, `free_fgraph_ops()`, `init_array_fgraph_ops()`, `graph_trace_init()`, `graph_trace_reset()`, `graph_trace_update_thresh()`, `graph_trace_open()`, `graph_trace_close()`, and `func_graph_set_flag()`. Output uses `print_graph_function_flags()` and helpers for leaf/nested entries, returns, comments, headers, absolute/relative time, CPU/proc columns, IRQ markers, duration, retval, and retaddr.

## Control Flow
On function entry, `graph_entry()` checks task-local notrace state, graph address filters, IRQ filtering, and optional sleep-time accounting. It reserves fgraph per-task data to save call time and optionally sleep timestamp. If `tracing_thresh` is active it records only return events. Otherwise it writes an entry event, using a retaddr entry type when configured and requested. On return, `trace_graph_return()` retrieves saved call data, adjusts call time to exclude sleep if requested, and writes a return event. The threshold return path suppresses returns below `tracing_thresh`.

Starting the tracer selects argument or non-argument entry function, selects threshold or normal return function, increments global counters for IRQ skipping and no-sleep-time behavior, uses a memory barrier to publish ops, registers ftrace graph callbacks, and starts command-line recording. Reset decrements the global counters, stops command-line recording, and unregisters graph callbacks. Flag changes while active update global counters or restart graph callbacks when argument capture changes.

Trace reading allocates `fgraph_data` in `graph_trace_open()` and frees it in `graph_trace_close()`. Formatting detects leaf calls by peeking at the next return event, prints compact `func();` lines for leaves, nested braces for non-leaves, explicit function names on mismatched/lost returns, comments for non-graph trace entries, and optional headers. The tracefs `max_graph_depth` file reads/writes the global `fgraph_max_depth`.

## State And Persistence
Persistent tracer state includes global options, `ftrace_graph_skip_irqs`, `fgraph_no_sleep_time`, `fgraph_max_depth`, and global event registrations for graph entry/return events. Per-trace-array state lives in `tr->gops` and tracer flags. Per-open formatting state is allocated for readers and tracks pid/depth continuity across consumed events; it also saves entry/return data when seq output overflows so formatting can resume safely.

## Dependencies And Integration Points
This file depends on function graph ftrace support, ring-buffer trace events, trace output helpers, task fgraph data, command-line recording, tracefs, optional function retval/retaddr/argument configs, and selftests. It shares graph ops allocation with `trace_functions.c` for trace instances and registers graph event types for the trace core.

## Risks
Graph tracing is sensitive to function entry/return pairing. Lost entries, seq-buffer partial writes, IRQ filtering, and notrace ranges can make output misleading if depth tracking is wrong. Global counters for IRQ skipping and no-sleep accounting must remain balanced across init/reset and option changes. `fgraph_reserve_data()`/`fgraph_retrieve_data()` sizing must match whether sleep time is tracked. Argument, retval, and retaddr output depends on config-specific event sizes and architecture support.

## Test Signals
Test by enabling `function_graph`, reading `trace` and `trace_pipe`, changing `max_graph_depth`, toggling options such as `funcgraph-irqs`, `sleep-time`, `funcgraph-args`, `funcgraph-retaddr`, and `funcgraph-retval`, and setting `tracing_thresh`. Output should show balanced braces, plausible durations, proper leaf compaction, IRQ markers only when expected, and stable headers. Stress with small trace buffers and `ftrace_dump()` to exercise partial-line recovery and atomic allocation paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_functions_graph.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_hwlat.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_hwlat.c

## Purpose
Implements the `hwlat` tracer, a hardware/firmware latency detector. It deliberately runs high-priority sampling loops with interrupts disabled to detect time discontinuities that can indicate SMIs or other hardware-induced stalls invisible to the OS.

## Important APIs, Types, And Functions
Persistent configuration is held in `hwlat_data`, which contains a mutex, total sample count, sample window, sample width, and thread mode. `struct hwlat_kthread_data` stores the active kthread and NMI timing counters, either globally for single-thread modes or per CPU. `struct hwlat_sample` is converted into `TRACE_HWLAT` ring-buffer entries by `trace_hwlat_sample()`.

Core sampling is in `get_sample()`, with NMI accounting in `trace_hwlat_callback()`. Thread management uses `kthread_fn()`, `start_single_kthread()`, `stop_single_kthread()`, `start_per_cpu_kthreads()`, `stop_per_cpu_kthreads()`, and CPU-specific helpers. Tracefs controls are created by `init_tracefs()` and include `hwlat_detector/window`, `hwlat_detector/width`, and `hwlat_detector/mode`. Tracer lifecycle is handled by `hwlat_tracer_init()`, `hwlat_tracer_start()`, `hwlat_tracer_stop()`, and `hwlat_tracer_reset()`.

## Control Flow
When the tracer initializes, it enforces single active use through `hwlat_busy`, records the trace array, resets counters and max latency, saves the previous `tracing_thresh`, and installs a default threshold if none is set. If tracing is already on, it starts sampler threads. Start chooses one kthread for `none` and `round-robin` modes or one kthread per allowed CPU for `per-cpu` mode.

Each sampler iteration optionally migrates to the next allowed CPU, disables local interrupts, calls `get_sample()`, re-enables interrupts, and sleeps for the inactive part of the sampling window. `get_sample()` repeatedly reads `trace_clock_local()` during the active width, compares inner and outer loop deltas against the threshold, tracks the largest observed latency, records NMI time/counts while callback collection is enabled, and emits a sample if the threshold was exceeded. It also updates `tr->max_latency` and notifies latency watchers.

Mode writes stop the tracer if busy, update `hwlat_data.thread_mode` under lock, and restart it. Round-robin mode pins the single thread to successive CPUs in the tracing cpumask; if user affinity changes unexpectedly, it switches to `none`. Per-CPU mode starts/stops CPU-bound kthreads and integrates with CPU hotplug callbacks to start a new thread on online CPUs and stop on dying CPUs.

## State And Persistence
Configuration persists globally in tracefs variables: sample width, sample window, thread mode, and remembered threshold. `last_tracing_thresh` preserves user threshold across tracer runs while `save_tracing_thresh` restores the prior global threshold on reset. `hwlat_busy` prevents more than one active tracer instance. Counts reset at init; max latency resets per run. Active kthread pointers persist in either `hwlat_single_cpu_data` or per-CPU storage until stop/reset/hotplug teardown.

## Dependencies And Integration Points
The tracer depends on trace arrays and ring buffers, tracefs, kthreads, CPU masks, CPU hotplug, local IRQ control, scheduler clock/trace clock, NMI trace callbacks, latency fsnotify, and generic `trace_min_max_fops`. It integrates with the global `tracing_thresh` value and the tracing cpumask.

## Risks
The tracer intentionally introduces latency and should not run in production low-latency environments. Incorrect width/window bounds can lead to excessive CPU hogging, though generic min/max controls constrain width versus window. CPU hotplug and mode changes must coordinate `trace_types_lock`, `hwlat_data.lock`, and CPU read locks to avoid orphaned kthreads. NMI timing depends on scheduler clock safety and is disabled for generic sched clock. Round-robin affinity changes by users can degrade mode behavior and force `none`.

## Test Signals
Smoke tests include selecting the `hwlat` tracer, changing width/window/mode files, observing `TRACE_HWLAT` entries after induced latency, and confirming `tracing_thresh` is restored after reset. Per-CPU mode should start one `hwlatd/%u` thread per allowed online CPU and handle CPU hotplug. Negative tests should reject overlong or unknown mode strings and invalid width/window bounds. Runtime diagnostics should check for stuck kthreads, unexpected max-latency updates, and lockdep issues during mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_hwlat.c -->
