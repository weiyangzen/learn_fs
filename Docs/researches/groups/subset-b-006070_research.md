# subset-b-006070 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace.h

## Purpose
`trace.h` is the private umbrella header for the kernel tracing core. It defines ring-buffer entry types, the central `trace_array` instance object, tracer callback contracts, trace output option bits, event-filter and event-trigger plumbing, function-graph helpers, snapshot hooks, dynamic tracefs helpers, and many cross-file prototypes used by the `kernel/trace` implementation. It is not Ceph-specific despite living under this source snapshot; it provides the infrastructure that Ceph and other subsystems can consume through tracepoints, ftrace, perf, and tracefs.

## Important APIs, types, and functions
Important types include `enum trace_type`, `struct trace_array_cpu`, `struct array_buffer`, `struct trace_array`, `struct tracer`, `struct tracer_flags`, `struct trace_parser`, `struct ftrace_event_field`, `struct event_filter`, `struct trace_subsystem_dir`, `struct event_trigger_data`, `struct event_command`, and `struct trace_min_max_param`. `trace_array` is the persistence and lifecycle hub: it owns live and snapshot buffers, tracefs dentries, enabled events, system lists, PID filters, clock choice, flags, ftrace ops, function-graph ops, error logs, histogram variables, saved command maps, and per-instance reference counts.

Key APIs declared here include trace instance lookup (`trace_array_find_get()`), buffer reservation and commit (`trace_buffer_lock_reserve()`, `trace_buffer_unlock_commit_regs()`), trace file open/release helpers, PID filter operations, tracer registration (`register_tracer()`), event filter application, event trigger registration, snapshot controls, function trace controls, trace option parsing, ring-buffer resizing, and perf ftrace registration. Inline helpers such as `trace_assign_type()`, `tracer_tracing_is_on_cpu()`, `event_trigger_unlock_commit()`, `trace_event_setup()`, and `ftrace_trace_stack()` provide fast paths used by many trace writers.

## Control flow and integration
The header is included by most tracing C files and mediates several flows. Event writers reserve a `ring_buffer_event`, call `trace_event_setup()` or `tracing_generic_entry_update()`, fill an entry structure generated from `trace_entries.h`, then commit through `trace_buffer_unlock_commit()` or `event_trigger_unlock_commit()`. Trigger-aware writers call `__event_trigger_test_discard()`, which runs conditional triggers, filter predicates, soft-disabled checks, and PID filters before committing or discarding. Tracers implement `struct tracer` callbacks and register with the core so tracefs `current_tracer` can call their `init`, `reset`, `start`, `stop`, output, and option handlers.

The file also drives macro expansion. It includes `trace_entries.h` once with `FTRACE_ENTRY` defined to create concrete C structures, then later redefines `FTRACE_ENTRY` to declare the matching `trace_event_call` objects. That two-pass use ties binary ring-buffer layouts to user-visible format metadata.

## State and persistence behavior
Most state referenced here is in-memory kernel state exposed through tracefs. `trace_array` instances persist until trace instances are removed; buffers keep event history, snapshot buffers keep max-latency or user snapshots, and lists such as `events`, `systems`, `err_log`, `hist_vars`, and PID filters retain configuration. The header uses RCU pointers for PID lists and event filters, mutexes for global trace/event list mutation, per-CPU storage for buffers and repeat tracking, and config-gated stubs so callers compile even when tracing features are disabled.

## Dependencies
This header depends on Linux tracing, ftrace, ring buffer, trace events, tracepoint, BPF/BTF-adjacent event definitions, tracefs/eventfs, lock/RCU primitives, workqueues, per-CPU data, and configuration symbols such as `CONFIG_FUNCTION_TRACER`, `CONFIG_FUNCTION_GRAPH_TRACER`, `CONFIG_TRACER_SNAPSHOT`, `CONFIG_EVENT_TRACING`, `CONFIG_HIST_TRIGGERS`, `CONFIG_PERF_EVENTS`, and syscall tracing.

## Risks
The highest risks are ABI layout drift in `trace_entries.h` macro expansion, reference/lifetime mistakes for dynamic `trace_event_file` objects, recursion in trace paths, and locking-order mistakes around `event_mutex`, `trace_types_lock`, `max_lock`, RCU lists, and per-CPU buffers. The inline discard/commit logic is central: a missed filter or PID check can leak data, while a wrong discard can silently drop events. Config-gated stubs reduce ifdef noise but can hide feature-dependent behavior in tests.

## Test signals
Useful signals include booting with tracing selftests, toggling tracers through tracefs, enabling event filters and triggers, exercising snapshots, validating generated event `format` files, running perf tracepoint sampling, and checking lockdep/RCU diagnostics while repeatedly creating and deleting trace instances and dynamic events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.c

## Purpose
`trace_benchmark.c` implements the runtime side of the `benchmark_event` tracepoint. When that tracepoint is enabled, it starts a kernel thread that continuously emits the tracepoint and measures the time spent writing it, producing rolling latency statistics in the next tracepoint payload.

## Important APIs, types, and functions
The main functions are `trace_do_benchmark()`, `benchmark_event_kthread()`, `trace_benchmark_reg()`, `trace_benchmark_unreg()`, and `ok_to_run_trace_benchmark()`. Global state includes `bm_event_thread`, the formatted payload buffer `bm_str`, counters and accumulators (`bm_total`, `bm_totalsq`, `bm_last`, `bm_max`, `bm_min`, `bm_first`, `bm_cnt`, `bm_avg`, `bm_std`, `bm_stddev`), and `ok_to_run`.

## Control flow
`TRACE_EVENT_FN` in the header wires tracepoint registration to `trace_benchmark_reg()` and unregistration to `trace_benchmark_unreg()`. Registration refuses command-line startup before `early_initcall` sets `ok_to_run`, then starts `event_benchmark`. The thread waits 100 ms, then loops until `kthread_should_stop()`, calling `trace_do_benchmark()` and `cond_resched_tasks_rcu_qs()`. The benchmark path checks that the tracepoint is enabled and tracing is on, disables local IRQs, records `trace_clock_local()` before and after `trace_benchmark_event()`, then updates statistics and formats the next message.

## State and persistence behavior
All benchmark statistics are static in-memory state. `trace_benchmark_unreg()` stops the thread and resets the payload and counters, so disabling the tracepoint clears history. The first sample is treated separately as cold-cache data and is not folded into the hot-path average.

## Dependencies and integration points
The file depends on `trace_benchmark.h`, tracepoint generated helpers, kthreads, local trace clock, `tracing_is_on()`, scheduler quiescent-state reporting for RCU tasks, and module/kernel thread infrastructure. It integrates with tracefs through the tracepoint enable count rather than its own files.

## Risks
This intentionally burns CPU while enabled; incorrect enable checks could create unexpected load. Statistics can overflow or become meaningless after very large sample counts, so the code freezes average/stddev updates after `bm_cnt > UINT_MAX`. IRQ disabling around the tracepoint narrows the measured region but also makes recursion and latency behavior important.

## Test signals
Enable `benchmark:benchmark_event`, read `trace_pipe`, confirm the kthread appears and disappears on enable/disable, verify the first payload is marked cold cached, and check that `last`, `max`, `min`, `avg`, and `std` evolve without warnings or stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.h

## Purpose
`trace_benchmark.h` declares the `benchmark` tracepoint system and defines the `benchmark_event` trace event used by `trace_benchmark.c` to measure tracepoint write overhead.

## Important APIs, types, and functions
It declares `trace_benchmark_reg()` and `trace_benchmark_unreg()`, defines `BENCHMARK_EVENT_STRLEN` as 128, and uses `TRACE_EVENT_FN(benchmark_event, ...)` with two fields: a fixed string payload `str[128]` and a `u64 delta`. The event print format is `"%s delta=%llu"`.

## Control flow
The `TRACE_EVENT_FN` macro generates the normal tracepoint enable, emit, and format code while binding enable/disable callbacks to the registration functions. `TP_fast_assign` copies the provided string into the event record and stores the measured delta. The include path/footer selects this local file as the trace include and includes `<trace/define_trace.h>` outside the guard, which is required for tracepoint definition generation.

## State and persistence behavior
The header itself holds no mutable state. It defines the ABI and generated code contract for the event record stored in ring buffers and exposed through tracefs event format files.

## Dependencies and integration points
It depends on `<linux/tracepoint.h>` and the trace event macro framework. The registration callbacks integrate with `trace_benchmark.c`, and the generated event appears under the `benchmark` tracepoint system.

## Risks
Changing field names, sizes, or print format would change user-visible tracefs ABI. The fixed string copy uses the full 128-byte payload, so producers must provide a buffer of at least that size, as `trace_benchmark.c` does with `bm_str`.

## Test signals
Build-time trace event generation is the main signal. At runtime, `/sys/kernel/tracing/events/benchmark/benchmark_event/format` should expose the `str` and `delta` fields, and enabling the event should call the registration hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_benchmark.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_boot.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_boot.c

## Purpose
`trace_boot.c` applies bootconfig-driven tracing setup during early boot. It parses the `ftrace` bootconfig tree and configures the global trace array plus named instances: options, tracing state, clocks, buffer sizes, CPU masks, events, kprobes, synthetic events, histogram triggers, filters, ftrace filters, tracers, and snapshots.

## Important APIs, types, and functions
Core functions include `trace_boot_set_instance_options()`, `trace_boot_enable_events()`, `trace_boot_add_kprobe_event()`, `trace_boot_add_synth_event()`, histogram command builders (`append_printf()`, `trace_boot_hist_add_array()`, `trace_boot_hist_add_handlers()`, `trace_boot_compose_hist_cmd()`), `trace_boot_init_one_event()`, `trace_boot_init_events()`, `trace_boot_set_ftrace_filter()`, `trace_boot_enable_tracer()`, `trace_boot_init_one_instance()`, `trace_boot_init_instances()`, and `trace_boot_init()`.

## Control flow
`core_initcall_sync(trace_boot_init)` runs after the top trace array exists. It finds the `ftrace` bootconfig node, configures the global trace array, then iterates `ftrace.instance.*` nodes and calls `trace_array_get_by_name()` for each instance. Per-instance setup first applies generic options, then configures individual events, then enables event lists, then enables ftrace filters/tracers/snapshots. Event setup can create kprobe or synthetic events before looking up the resulting `trace_event_file`; it then applies filters, actions, hist triggers, and final enablement under `event_mutex`.

## State and persistence behavior
Configuration persists in the target `trace_array` state after boot: ring-buffer size, clock, cpumask, trace options, enabled events, filters, triggers, and tracer selection. Boot-created dynamic events are inserted into the normal dynamic event registries. If boot tracing is active, the code disables tracing selftests to avoid conflicting boot-time activity.

## Dependencies and integration points
The file depends on bootconfig (`xbc_*` APIs), trace array controls from `trace.h`, dynamic event command generation for kprobes and synthetic events, histogram trigger parsing, event filters, ftrace filter APIs, tracefs event enable helpers, and configuration symbols for event tracing, kprobe events, synthetic events, histogram triggers, and dynamic ftrace.

## Risks
Most buffers are bounded by `MAX_BUF_LEN` 256, so long bootconfig strings are rejected or can produce truncated command failures. Histogram command composition is string-heavy and must preserve tracefs trigger syntax exactly. Locking is sensitive because event lookup, filter application, trigger processing, and enablement occur under `event_mutex`. Feature-disabled builds log errors for unsupported kprobes/synthetic events/actions rather than silently configuring them.

## Test signals
Boot with representative `ftrace` bootconfig entries for global and instance tracing; verify tracefs options, `current_tracer`, buffers, cpumasks, enabled events, dynamic events, filters, and hist triggers after boot. Negative tests should include too-long strings, missing hist keys/actions, unsupported feature configs, and invalid event names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_boot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_branch.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_branch.c

## Purpose
`trace_branch.c` implements branch profiling support for annotated `likely()`/`unlikely()` sites. With `CONFIG_BRANCH_TRACER`, it provides a live `branch` tracer that records branch correctness into the trace ring buffer; independently, it exports statistics over annotated and optionally all branch profile sections.

## Important APIs, types, and functions
Important functions include `probe_likely_condition()`, `trace_likely_condition()`, `enable_branch_tracing()`, `disable_branch_tracing()`, `branch_trace_init()`, `branch_trace_reset()`, `trace_branch_print()`, `ftrace_likely_update()`, `get_incorrect_percent()`, `branch_stat_process_file()`, and stat tracer callbacks for annotated/all branch profile sections. Global state includes `branch_tracer`, `branch_tracing_enabled`, and `branch_tracing_mutex`.

## Control flow
Compiler instrumentation calls exported `ftrace_likely_update()`, which saves user access state, handles constant branches, optionally records a trace event through `trace_likely_condition()`, then increments correct/incorrect counters. When branch tracing is enabled, `probe_likely_condition()` protects against recursion with `TRACE_BRANCH_BIT`, disables IRQs, checks per-CPU tracing state, reserves a `TRACE_BRANCH` entry, copies function/file/line data, records whether the branch matched expectation, and commits without stack tracing. Initialization registers the `TRACE_BRANCH` event and the `branch` tracer at core init.

## State and persistence behavior
Per-site branch counters live in linker sections `__start_annotated_branch_profile` and, when configured, `__start_branch_profile`. Live branch events go to the selected trace array while the branch tracer is enabled. Enable/disable is refcount-like through `branch_tracing_enabled`, guarded by a mutex; `branch_tracer` points to the current trace array.

## Dependencies and integration points
The file integrates with compiler-generated branch profiling data from `<linux/compiler.h>`, ftrace tracer registration, ring-buffer event output, trace stat registration, kallsyms/seq output, and trace event formatting from `trace_entries.h`.

## Risks
The source notes that branch correct/incorrect increments are not atomic, so stats can race on SMP. Module lifetime is handled by copying file/function strings into ring-buffer events rather than storing pointers, but truncation to fixed sizes is possible. The branch tracer global pointer and enable count must stay ordered; the code uses `smp_wmb()` before enabling.

## Test signals
Enable `current_tracer=branch`, exercise likely/unlikely-heavy workloads, and inspect trace output for `ok`/`MISS` records. Read branch stat files to confirm sorting and percentages. Lockdep/RCU and recursion warnings are important when branch tracing is enabled during heavy tracepoint activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_btf.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_btf.c

## Purpose
`trace_btf.c` provides small BTF lookup helpers for trace probe argument parsing. It lets trace probe code find function prototypes, enumerate function parameters, and resolve struct/union members including members inside anonymous nested aggregates.

## Important APIs, types, and functions
The exported helpers are `btf_find_func_proto()`, `btf_get_func_param()`, and `btf_find_struct_member()`. Internal support includes `BTF_ANON_STACK_MAX` and `struct btf_anon_stack`, which tracks type IDs and accumulated offsets while walking anonymous nested structs/unions.

## Control flow
`btf_find_func_proto()` calls `bpf_find_btf_id()` for a function name, validates that the result is `BTF_KIND_FUNC`, follows its `type` to the corresponding `BTF_KIND_FUNC_PROTO`, and returns both the BTF object and type. On failure after acquiring BTF, it calls `btf_put()`. `btf_get_func_param()` validates that its input is a function prototype, sets the parameter count, and returns the parameter array or NULL for no parameters. `btf_find_struct_member()` allocates a fixed-depth stack, scans members by name, pushes anonymous aggregate members for later traversal, and returns the found member plus accumulated anonymous offset.

## State and persistence behavior
This file maintains no persistent global state. It acquires BTF references through the BPF/BTF core and transfers release responsibility to callers on success.

## Dependencies and integration points
It depends on `<linux/btf.h>`, BPF BTF ID lookup, slab allocation, and trace probe code that uses BTF context for typed fetch arguments. Cross-reference searches show use from `trace_probe.c` and trace output code.

## Risks
Callers must call `btf_put()` after successful `btf_find_func_proto()`. Anonymous aggregate traversal is bounded to 16 pending nodes; deeply nested anonymous structures beyond that limit may be missed. `btf_find_struct_member()` returns error pointers for invalid input or allocation failure, and callers must distinguish those from NULL not-found results.

## Test signals
Use fprobe/kprobe trace probe arguments that rely on BTF function parameters and nested struct members. Validate success paths, missing functions, non-prototype types, no-parameter functions, anonymous union/struct member offsets, and allocation-failure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_btf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_btf.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_btf.h

## Purpose
`trace_btf.h` is the local declaration header for BTF helpers used by trace probe parsing and output code.

## Important APIs, types, and functions
It includes `<linux/btf.h>` and declares `btf_find_func_proto()`, `btf_get_func_param()`, and `btf_find_struct_member()`. The signatures expose BTF object lifetime transfer, function prototype parameter counts, and optional anonymous-member offset reporting.

## Control flow
The header has no runtime control flow. It gives other trace files access to the implementation in `trace_btf.c`.

## State and persistence behavior
No state is stored here. The declared APIs operate on BTF objects owned by the BTF core or returned with caller-managed references.

## Dependencies and integration points
Its only direct dependency is the kernel BTF type API. Integration points are trace probe parser code that maps user fetch expressions to typed kernel arguments and members.

## Risks
Because this header lacks include guards, duplicate inclusion in one translation unit would rely on identical prototype redeclaration being harmless. The prototypes also require callers to understand error-pointer versus NULL behavior documented in the C file.

## Test signals
Build coverage is the primary signal. Runtime signal comes from BTF-enabled trace probe tests that include this header through `trace_probe.c` or related files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_btf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_clock.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_clock.c

## Purpose
`trace_clock.c` implements trace timestamp providers with different precision, ordering, and overhead tradeoffs: CPU-local, medium/global-ish, jiffies, globally monotonic, and pure counter clocks.

## Important APIs, types, and functions
Exported functions are `trace_clock_local()`, `trace_clock()`, `trace_clock_jiffies()`, `trace_clock_global()`, and `trace_clock_counter()`. Important state includes `trace_clock_struct`, which stores `prev_time` and an `arch_spinlock_t` in the same cache line, and the atomic `trace_counter`.

## Control flow
`trace_clock_local()` disables preemption and reads `sched_clock()`. `trace_clock()` returns `local_clock()`, accepting small inter-CPU jitter. `trace_clock_jiffies()` converts jiffies since `INITIAL_JIFFIES`. `trace_clock_global()` disables local IRQs, reads the previous global timestamp with barriers, reads `sched_clock_cpu()`, clamps backward movement, and tries to update `prev_time` under an arch spin trylock; in NMI context it avoids locking and returns the clamped time. `trace_clock_counter()` atomically increments and returns a strict ordering counter.

## State and persistence behavior
The global clock persists the last returned timestamp in static memory. The counter clock persists a monotonically increasing `atomic64_t`. Other clocks store no state in this file.

## Dependencies and integration points
The file depends on scheduler clocks, jiffies, spinlocks, IRQ state helpers, per-CPU CPU IDs, NMI detection, atomics, and `<linux/trace_clock.h>`. Tracers and event code select these clocks through trace array clock configuration.

## Risks
The local and medium clocks are intentionally not fully coherent across CPUs. The jiffies clock has a documented small 32-bit safety window. The global clock avoids lockups by using trylock and bypassing locking in NMI, so it is best-effort globally ordered rather than a hard serialization in every context.

## Test signals
Switch trace clocks via tracefs and verify event timestamp monotonicity expectations per clock. Stress with cross-CPU events, idle transitions, NMI-heavy paths, and counter-clock ordering checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.c

## Purpose
`trace_dynevent.c` implements the generic dynamic event control layer behind tracefs `dynamic_events`. It manages dynamic event type registration, creation dispatch, deletion, listing, reference checks, and a command-building helper API used by kprobe and synthetic event generators.

## Important APIs, types, and functions
Key globals are `dyn_event_ops_mutex`, `dyn_event_ops_list`, and `dyn_event_list`. Public functions include `trace_event_dyn_try_get_ref()`, `trace_event_dyn_put_ref()`, `trace_event_dyn_busy()`, `dyn_event_register()`, `dyn_event_release()`, `dyn_event_create()`, `dyn_events_release_all()`, sequence callbacks, and dynevent command helpers (`dynevent_cmd_init()`, `dynevent_arg_init()`, `dynevent_arg_add()`, `dynevent_arg_pair_init()`, `dynevent_arg_pair_add()`, `dynevent_str_add()`, `dynevent_create()`).

## Control flow
Tracefs writes to `dynamic_events` call `trace_parse_run_command()` with `create_dyn_event()`. Commands beginning with `-` or `!` route to `dyn_event_release()`; otherwise `create_dyn_event()` walks registered dynamic event operation providers until one accepts the command or reports a non-cancel error. Reads iterate `dyn_event_list` under `event_mutex` and call each event type's `show()` method. Opening with write-truncate releases all dynamic events after lockdown and trace open checks.

## State and persistence behavior
Dynamic event providers are registered in `dyn_event_ops_list`; live dynamic events are linked in `dyn_event_list` and tied to `trace_event_call` objects marked `TRACE_EVENT_FL_DYNAMIC`. Reference counts on dynamic trace events prevent unsafe deletion while users hold references. Command builders use caller-supplied buffers and `seq_buf` state rather than allocating persistent command storage.

## Dependencies and integration points
The file depends on tracefs/debugfs infrastructure, security lockdown checks, `event_mutex`, `trace_event_sem`, `ftrace_events`, `trace_parse_run_command()`, error logging, and type-specific providers such as kprobes, uprobes, fprobes, eprobes, and synthetic events.

## Risks
Deletion parsing is subtle because commands can match event-only, system/event, and extra arguments through type-specific `match()` functions. `dyn_events_release_all()` aborts on busy events and may partially release events on other errors. Locking boundaries matter: operation registration is protected by `dyn_event_ops_mutex`, live event mutation by `event_mutex`, and reference lookup by `trace_event_sem`.

## Test signals
Exercise `dynamic_events` create/list/delete/truncate flows for every registered provider. Verify busy deletion returns `-EBUSY`, malformed commands produce trace errors, lockdown blocks open, command-builder tests reject oversized buffers, and repeated create/delete leaves no events in `dyn_event_list`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.h

## Purpose
`trace_dynevent.h` defines the shared interface for dynamic event providers and command builders used by the generic dynamic events implementation.

## Important APIs, types, and functions
Core types are `struct dyn_event_operations`, `struct dyn_event`, `struct dynevent_arg`, and `struct dynevent_arg_pair`. The operations table requires `create`, `show`, `is_busy`, `free`, and `match` callbacks. Inline helpers include `dyn_event_init()`, `dyn_event_add()`, and `dyn_event_remove()`. Iteration macros `for_each_dyn_event` and `for_each_dyn_event_safe` wrap the global list.

## Control flow
Providers register a `dyn_event_operations` object, embed `struct dyn_event` in their event-specific object, initialize it with `dyn_event_init()`, and add it to the global list with `dyn_event_add()` while holding `event_mutex`. The generic tracefs layer later invokes provider callbacks through this contract for create, display, match, busy checks, and deletion. Command helper declarations support building type-specific tracefs command strings safely into a `dynevent_cmd`.

## State and persistence behavior
The header declares `dyn_event_list` but stores no state itself. `dyn_event_add()` marks the associated `trace_event_call` dynamic and links the event into persistent in-memory dynamic event state; `dyn_event_remove()` unlinks it.

## Dependencies and integration points
It depends on list, mutex, seq file, kernel utility headers, and `trace.h` for `event_mutex`, `trace_event_call`, and `dynevent_cmd` definitions. Providers such as eprobes, kprobes, uprobes, fprobes, and synthetic events include this header.

## Risks
The inline add/remove helpers assert `event_mutex` but do not acquire it, so callers must satisfy locking. Providers must implement every required callback; missing callbacks are rejected by registration, but incorrect match/free semantics can still cause leaks or wrong deletion.

## Test signals
Build all dynamic event providers, create and delete events from each provider, verify `dynamic_events` listing uses each `show()` implementation, and run lockdep while mutating dynamic events concurrently with trace event enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_dynevent.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_entries.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_entries.h

## Purpose
`trace_entries.h` is the macro source of truth for built-in ftrace ring-buffer entry layouts and their user-visible print formats. It is repeatedly included with different `FTRACE_ENTRY*` macro definitions to generate C structs, trace event call declarations, and format metadata.

## Important APIs, types, and functions
It defines entries for function calls, function graph entry/return, optional function graph return address/retval fields, context switch and wakeup, kernel and user stacks, trace printk variants (`bprint`, `print`, `bputs`), raw data, MMIO trace records, branch records, hardware latency, function repeats, OS noise, and timer latency. It also defines helper field groups such as `FTRACE_CTX_FIELDS`, `FTRACE_STACK_ENTRIES`, branch field sizes, and `FUNC_REPEATS_GET_DELTA_TS()`.

## Control flow
There is no direct runtime control flow. Instead, the included macros expand into declarations consumed by writer and printer paths. `FTRACE_ENTRY_DUP` creates format metadata for `wakeup` while reusing the context-switch structure. `FTRACE_ENTRY_REG` attaches registration hooks to entries such as function tracing and `trace_print`.

## State and persistence behavior
The file defines binary layouts that become persistent within ring-buffer records and visible through tracefs `format` files. These layouts form an ABI for tooling that reads trace data.

## Dependencies and integration points
It depends on macro definitions supplied by including files, especially `trace.h` and trace event generation code. The entry IDs must align with `enum trace_type`, and field structures must match internal helper structures such as `struct ftrace_graph_ent`, `struct ftrace_graph_ret`, `struct mmiotrace_rw`, and `struct mmiotrace_map`.

## Risks
Layout drift is the main risk. Changing fields, packing, dynamic array use, or print format can break trace tooling. Conditional entries must preserve compatibility across configs; for example, function graph retval and return-address variants change layouts under specific config symbols. Stack entry handling deliberately exposes a fixed historical caller array while using dynamic storage internally.

## Test signals
Compile-time macro expansion catches some structure mismatches. Runtime validation should inspect tracefs format files, emit each built-in event type where possible, parse output with trace-cmd/perf tooling, and compare event IDs against `enum trace_type`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_entries.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_eprobe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_eprobe.c

## Purpose
`trace_eprobe.c` implements event probes: dynamic events that attach to an existing trace event and emit a new event populated from selected fields of the original event. It reuses trace probe parsing and event trigger infrastructure but hides the trigger from user-controlled trigger files.

## Important APIs, types, and functions
Key types are `struct trace_eprobe` and `struct eprobe_data`. Important functions include dynamic-event callbacks (`eprobe_dyn_event_create()`, `eprobe_dyn_event_show()`, `eprobe_dyn_event_release()`, `eprobe_dyn_event_is_busy()`, `eprobe_dyn_event_match()`), lifecycle helpers (`alloc_event_probe()`, `unregister_trace_eprobe()`, `trace_event_probe_cleanup()`), field/print helpers (`eprobe_event_define_fields()`, `print_eprobe_event()`), fetch helpers (`get_event_field()`, `get_eprobe_size()`, `process_fetch_insn()`), trigger glue (`new_eprobe_trigger()`, `enable_eprobe()`, `disable_eprobe()`), registration (`eprobe_register()`), parsing (`trace_eprobe_parse_filter()`, `__trace_eprobe_create()`), and early registration (`trace_events_eprobe_init_early()`).

## Control flow
Dynamic event creation accepts commands like `e[:[GRP/]ENAME] SYSTEM.EVENT [FETCHARGS] [if FILTER]`. Parsing resolves the target event under `event_mutex`, allocates a trace probe object, optionally validates a filter against the original event, parses fetch args in `TPARG_FL_TEVENT` context, sets print format, registers a trace event call, and adds it to the dynamic event list. When the eprobe event is enabled, `enable_trace_eprobe()` creates hidden event-trigger data on the target event. When the target event fires, `eprobe_trigger_func()` receives the original record, `__eprobe_trace_func()` reserves a new eprobe event record, copies fetched args, and commits it.

## State and persistence behavior
Each eprobe stores the attached event system/name, a reference to the target `trace_event_call`, optional filter string, dynamic-event node, and trace probe metadata. Enablement state lives through trace probe file links and hidden trigger entries in the target event's trigger list. Disabling removes the trigger, synchronizes tracepoint unregister, frees filters and private data, and may unregister the eprobe event call when no siblings remain.

## Dependencies and integration points
The file depends on dynamic events, trace probe parsing, event filters, event triggers, trace event registration, ring-buffer event buffer helpers, and `event_mutex`. It integrates with perf registration only as no-op cases in `eprobe_register()`, while normal trace enable/disable attaches and detaches hidden triggers.

## Risks
Lifetime management is complex: target events require references, hidden trigger private data must survive concurrent tracepoints until `tracepoint_synchronize_unregister()`, and unregister must reject enabled or ftrace/perf-used probes. Field fetching handles dynamic, relative dynamic, static, pointer string, integer, long-sized, and array fields; incorrect offset/type handling can corrupt output or leak data. Rollback in partial enable failures warns if non-ENOMEM failures occur after earlier probes succeeded.

## Test signals
Create eprobes against normal events with integer, string, dynamic string, and array fields; apply `if` filters; enable and disable via tracefs; delete by event-only, system/event, attached event, and full command matching. Stress concurrent target event firing during deletion and run with lockdep/KASAN to catch lifetime errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_eprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_event_perf.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_event_perf.c

## Purpose
`trace_event_perf.c` bridges trace events to perf events. It handles permission checks, tracepoint event registration for perf, per-CPU perf event lists, temporary raw trace buffers, kprobe/uprobe perf-local events, add/delete hooks, and special handling for function-trace perf events.

## Important APIs, types, and functions
Important globals are `perf_trace_buf[PERF_NR_CONTEXTS]` and `total_ref_count`. Core functions include `perf_trace_event_perm()`, `perf_trace_event_reg()`, `perf_trace_event_unreg()`, `perf_trace_event_open()`, `perf_trace_event_close()`, `perf_trace_event_init()`, `perf_trace_init()`, `perf_trace_destroy()`, `perf_kprobe_init()/destroy()`, `perf_uprobe_init()/destroy()`, `perf_trace_add()`, `perf_trace_del()`, `perf_trace_buf_alloc()`, `perf_trace_buf_update()`, and, with function tracing, `perf_ftrace_event_register()` plus ftrace callback registration helpers.

## Control flow
`perf_trace_init()` looks up a trace event by perf config/event ID under `event_mutex`, takes a trace event reference, checks permissions, allocates per-event and global per-context buffers if needed, calls the event class `reg()` hooks for perf register/open, and stores the trace event on the perf event. `perf_trace_add()` starts sampling period state and either lets the event class handle add or links the perf event into the current CPU's RCU hlist. `perf_trace_del()` mirrors removal. Destroy paths close, unregister, synchronize tracepoint callbacks, free per-CPU lists and global buffers when last user exits, and drop trace event references.

## State and persistence behavior
Perf trace state persists while perf events are open. Each trace event has `perf_refcount` and per-CPU `perf_events` hlist storage. Global raw buffers are allocated only while at least one trace event is registered for perf. `perf_trace_buf_alloc()` uses perf recursion contexts and per-CPU buffers, returning memory valid for the current submission path.

## Dependencies and integration points
The file depends on perf core APIs, trace event classes and registration hooks, event mutex/refcounting, security/perf permission helpers, local kprobe/uprobe trace event creation, ftrace recursion guards, BPF/perf submission helpers declared in trace event headers, and per-CPU allocation.

## Risks
Permission handling is security-critical because raw tracepoint payloads can expose kernel data. Function trace perf events require root-like tracepoint permission and reject user callchains/user stacks for sampling. Buffer size is capped by `PERF_MAX_TRACE_SIZE`; oversize records are warned and dropped. Registration failure paths must unwind partially allocated per-CPU resources without corrupting refcounts.

## Test signals
Open perf tracepoint events with and without raw samples, as root and non-root, including task-attached events with `TRACE_EVENT_FL_CAP_ANY`. Test perf kprobe/uprobe creation, ftrace function sampling restrictions, concurrent add/delete on multiple CPUs, oversized record warnings, and final cleanup of per-CPU buffers after the last event closes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_event_perf.c -->
