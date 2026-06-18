# Research: subset-b-006074

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_irqsoff.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_irqsoff.c

## Purpose
Implements the `irqsoff`, `preemptoff`, and combined `preemptirqsoff` latency tracers. The file measures critical sections where hard IRQs and/or preemption are disabled, records the worst observed latency into the max trace buffer, and optionally records function or function-graph context around the critical window.

## APIs, Control Flow, and State
The main exported hooks are `start_critical_timings()`, `stop_critical_timings()`, `tracer_hardirqs_on/off()`, and `tracer_preempt_on/off()`, which are called by low-level IRQ/preempt instrumentation. The tracer instances are registered from `init_irqsoff_tracer()` through `register_tracer()` with callbacks for init, reset, start, stop, header printing, per-line printing, option changes, and optional ftrace selftests.

Important state includes the active `irqsoff_trace` `trace_array`, global `tracer_enabled`, `trace_type`, saved trace flags, `irqsoff_busy`, `function_enabled`, per-CPU `tracing_cpu`, and the `max_sequence` plus `max_trace_lock` pair used to serialize max-latency updates. Per-CPU `trace_array_cpu` fields store `preempt_timestamp`, `critical_start`, `critical_end`, `critical_sequence`, and recursion-disable counters. Init forces overwrite, latency formatting, and pause-on-trace because max latency tracers depend on a stable overwrite buffer and must not mix two concurrent maximum updates.

The core flow is `start_critical_timing()` capturing timestamp and call site, then `stop_critical_timing()` clearing the per-CPU active flag and calling `check_critical_timing()`. That function computes the elapsed time, filters through `tracing_thresh` or `tr->max_latency`, locks `max_trace_lock`, records ending function and stack context, checks `critical_sequence`, updates `tr->max_latency`, and calls `update_max_tr_single()`. Function tracing is attached by `register_irqsoff_function()` and uses `irqsoff_tracer_call()`. Function graph mode uses `fgraph_ops`, reserves per-call return data, and prints through graph-specific output when `TRACE_ITER(DISPLAY_GRAPH)` is set.

## Dependencies, Integration, Risks, and Tests
The file depends on ftrace, function graph tracing, kprobes `NOKPROBE_SYMBOL`, preempt/IRQ trace hooks, `trace_array` max-buffer helpers, `trace/events/preemptirq.h`, and trace options such as `FUNCTION`, `DISPLAY_GRAPH`, `OVERWRITE`, `LATENCY_FMT`, and `PAUSE_ON_TRACE`. It integrates tightly with `trace_preemptirq.c`, lockdep/IRQ flag instrumentation, tracefs current tracer selection, latency formatting in `trace_output.c`, and ftrace selftests.

Risks are mostly concurrency and instrumentation recursion: stale `tracing_cpu` state can suppress or leak tracing, wrong flag restoration can alter the user's trace instance, max trace updates must avoid concurrent buffer mutation, and graph/function tracer registration must match the active trace mode. The code also has configuration-sensitive paths, so behavior changes when function graph tracing, function tracing, IRQSOFF, or PREEMPT tracers are absent. Test signals include enabling each tracer from tracefs, toggling function and graph options, verifying max latency updates and stack entries, checking that reset restores original flags, running `trace_selftest_startup_irqsoff/preemptoff/preemptirqsoff`, and exercising IRQ/preempt transitions under load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_irqsoff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kdb.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_kdb.c

## Purpose
Adds a KDB command, `ftdump`, that dumps the ftrace ring buffer from the kernel debugger. It gives crash/debug sessions a safe way to inspect tracing data without relying on normal tracefs reads.

## APIs, Control Flow, and State
The file keeps a static `trace_iterator iter` and a per-CPU `buffer_iter[]` array. `kdb_ftrace_register()` installs `ftdump` through `kdb_register()` at `late_initcall`. The command accepts an optional skip count and optional CPU number; a negative skip means "show only the last N entries" after computing totals with `trace_total_entries()` or `trace_total_entries_cpu()`.

`kdb_ftdump()` initializes the global iterator, points it at `buffer_iter`, disables tracing for the target trace array, translates negative skips, calls `ftrace_dump_buf()`, then re-enables tracing. `ftrace_dump_buf()` temporarily clears `TRACE_ITER(SYM_USEROBJ)` to avoid user-memory lookups in panic/debugger context, starts ring-buffer iterators for all tracing CPUs or one CPU using `GFP_ATOMIC`, repeatedly calls `trace_find_next_entry_inc()`, formats each entry with `print_trace_line()`, emits with `trace_printk_seq()`, and cleans up each `ring_buffer_read_start()` with `ring_buffer_read_finish()`.

## Dependencies, Integration, Risks, and Tests
This file depends on KGDB/KDB, ftrace iterator internals, ring buffer iterators, trace output formatting, and `trace_output.h`. It integrates with the global top trace array via `trace_init_global_iter()` and uses KDB's `kdb_printf()` and interrupt flag handling.

Risks include debugger-context constraints: allocations must use atomic context, user-object symbolization is disabled deliberately, and the static iterator makes the command non-reentrant. CPU validation must reject offline or out-of-range CPUs, and tracing must be restored after early exits. Test signals include invoking `ftdump`, `ftdump <skip>`, `ftdump -N`, and `ftdump <skip> <cpu>` from KDB, validating empty-buffer output, interrupting a dump with KDB command interrupt, and confirming tracing resumes after command completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kdb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe.c

## Purpose
Implements dynamic tracing events backed by kprobes and kretprobes. It parses user and kernel-generated kprobe event commands, registers events in the dynamic event framework, attaches kprobe/kretprobe handlers, records trace and perf/BPF samples, supports boot-time `kprobe_event=` setup, and exposes tracefs control/profiling files.

## APIs, Control Flow, and State
The central object is `struct trace_kprobe`, which embeds `struct dyn_event`, `struct kretprobe` (using `rp.kp` for plain kprobes), per-CPU hit counters, an optional target symbol string, and a `struct trace_probe` containing event metadata and parsed fetch arguments. Dynamic event operations are provided through `trace_kprobe_ops`: create, show, busy check, free, and match. Public kernel helpers include `kprobe_event_cmd_init()`, `__kprobe_event_gen_cmd_start()`, `__kprobe_event_add_fields()`, `kprobe_event_delete()`, and, for perf local events, `create_local_trace_kprobe()` / `destroy_local_trace_kprobe()`.

Command parsing starts in `trace_kprobe_create()` and `trace_kprobe_create_internal()`. It accepts `p[:[GRP/][EVENT]] [MOD:]KSYM[+OFFS]|KADDR [FETCHARGS]`, return probes via `r[MAXACTIVE]...` or `%return`, validates maxactive against `KRETPROBE_MAXACTIVE_MAX`, validates symbols and module-qualified targets, expands BTF/meta and dentry arguments, allocates the trace probe, parses fetch arguments, assigns print formats, and registers the event. Existing events can have sibling probes appended if argument types and names match; identical probe definitions are rejected.

Registration is split between `register_kprobe_event()` for trace-event metadata and `__register_trace_kprobe()` for the actual kprobe/kretprobe. `__register_trace_kprobe()` checks lockdown policy, rejects notrace functions when dynamic ftrace metadata says a function is not traceable, updates fetch arguments, and registers the probe disabled or enabled depending on trace-probe flags. `enable_trace_kprobe()` and `disable_trace_kprobe()` are called from `kprobe_register()` for ftrace event enable/disable and perf registration, maintaining trace-file links and the profile flag. The kprobe dispatcher increments `nhit`, emits ftrace ring-buffer records when `TP_FLAG_TRACE` is set, and emits perf/BPF records when `TP_FLAG_PROFILE` is set. Kretprobe entry handling can store entry arguments in `ri->data`, while the return dispatcher records return IP and function address.

The file also owns tracefs interfaces. `kprobe_events` lists, creates, deletes, or truncates all kprobe dynamic events after lockdown checks. `kprobe_profile` reports event name, hit count, and missed counts from kprobe and kretprobe state. Boot setup stores early command-line definitions in `kprobe_boot_events_buf`, registers the dynamic event type at `core_initcall`, creates tracefs files at `fs_initcall`, then enables boot events in the top trace array. Module notifier support re-registers deferred module probes when a matching module comes online.

## Dependencies, Integration, Risks, and Tests
Dependencies include kprobes/kretprobes, kallsyms, module notifier and module kallsyms, lockdown/security hooks, ftrace event registration, dyn events, `trace_probe` parsing and fetch op execution, BTF/meta argument expansion, perf events, BPF trace calls, error-injection metadata, and tracefs. Integration points are `/sys/kernel/tracing/kprobe_events`, `/sys/kernel/tracing/kprobe_profile`, perf probe events, BPF kprobe attachments, boot command-line probes, dynamic event deletion, and module load/unload behavior.

Major risks are incorrect command parsing, ambiguous or deferred module symbols, probing notrace or invalid instruction boundaries, mismatched sibling event argument layouts, races between unregister and kretprobe trampoline execution, lockdown bypasses, BPF programs modifying instruction pointer in kprobe context, missing synchronization when event files are removed, and resource leaks across deferred module registration. Test signals include kprobe trace selftests, creating entry and return probes with register/stack/retval/entry args, duplicate and incompatible sibling rejection, module-qualified probes before and after module load, tracefs truncation deletion, perf/BPF kprobe attach tests, `kprobe_profile` hit/miss accounting, boot-time `kprobe_event=` definitions, and lockdown denial tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.c

## Purpose
Provides the out-of-line target function used by kprobe tracing startup selftests. Keeping the target in a separate compilation unit ensures it can be built with the ftrace-friendly flags needed for reliable probing.

## APIs, Control Flow, and State
The file defines one function, `kprobe_trace_selftest_target(int a1, int a2, int a3, int a4, int a5, int a6)`, which returns the sum of its six arguments. It has no persistent state and no internal branching. `trace_kprobe.c` installs entry and return probes on this symbol during `CONFIG_FTRACE_STARTUP_TEST`, calls it with `1..6`, expects result `21`, and verifies both probes hit exactly once.

## Dependencies, Integration, Risks, and Tests
It depends only on `trace_kprobe_selftest.h`. Its integration point is the kprobe startup selftest, where it must remain visible and probeable. Risks are compiler optimization or build-flag changes eliminating, inlining, renaming, or making the function unsuitable for kprobe attachment. Test signals are the boot log line from `kprobe_trace_self_tests_init()` reporting `Testing kprobe tracing: OK`, plus failures in probe creation, hit counts, or return-value probing if this target stops behaving as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.h

## Purpose
Declares the kprobe selftest target function implemented in `trace_kprobe_selftest.c`.

## APIs, Control Flow, and State
The header contains a single prototype for `kprobe_trace_selftest_target(int a1, int a2, int a3, int a4, int a5, int a6)`. It has no executable control flow, no macros, and no persistent state.

## Dependencies, Integration, Risks, and Tests
The header integrates the selftest target with `trace_kprobe.c`. Risks are limited to signature drift between declaration and definition or accidental removal that breaks selftest builds. Test signals are compile coverage with kprobe startup tests enabled and successful execution of the kprobe tracing selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_kprobe_selftest.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_mmiotrace.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_mmiotrace.c

## Purpose
Implements the `mmiotrace` tracer, which records memory-mapped I/O reads, writes, maps, unmaps, PCI device metadata, and textual marks in a custom text format consumed by MMIO tracing tools.

## APIs, Control Flow, and State
The tracer is registered by `init_mmio_trace()` as `mmiotrace` with init, reset, start, pipe-open, close, read, and print-line callbacks. `mmio_trace_init()` stores the active `trace_array`, resets overrun state, and calls `enable_mmiotrace()`. Reset disables mmiotrace, clears data, and drops the active trace array. Export-facing recording functions are `mmio_trace_rw()`, `mmio_trace_mapping()`, and `mmio_trace_printk()`, which append `TRACE_MMIO_RW`, `TRACE_MMIO_MAP`, or `TRACE_PRINT` records.

State includes `mmio_trace_array`, `overrun_detected`, `prev_overruns`, atomic `dropped_count`, and per-reader `struct header_iter` stored in `iter->private` for iterating PCI devices. `mmio_pipe_open()` emits the format version and starts PCI enumeration. `mmio_read()` first reports ring-buffer or reservation losses as `MARK ... Lost N events`, then prints one `PCIDEV` line per PCI device until enumeration completes. Event formatting is handled by `mmio_print_rw()`, `mmio_print_map()`, and `mmio_print_mark()`; unknown event types are ignored to keep the stream parser-compatible.

## Dependencies, Integration, Risks, and Tests
The file depends on the architecture MMIO tracing backend, PCI enumeration, the tracing ring buffer, `trace_output.h`, and `trace_vprintk()`. It integrates with tracefs current tracer selection, `trace_pipe`, PCI resource reporting, and MMIO instrumentation that calls the recording hooks.

Risks include a NULL or stale `mmio_trace_array` if record hooks are called outside the enabled tracer lifetime, event loss under high MMIO rates, the noted close-path caveat for pipe readers, PCI device reference leaks if iteration is not destroyed, and strict output-format compatibility with existing parsers. Test signals include enabling/disabling `mmiotrace`, reading the version and `PCIDEV` header stream, generating MMIO read/write/map/unmap records, forcing buffer overruns to see loss markers, and checking that PCI device references are released when the pipe closes or enumeration ends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_mmiotrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_nop.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_nop.c

## Purpose
Defines the `nop` tracer, the baseline tracer that performs no tracing work but provides a valid current-tracer target and a small tracer-option callback example.

## APIs, Control Flow, and State
The global `nop_trace` `struct tracer` names the tracer `nop`, provides init/reset callbacks, optional selftest hook, tracer flags, set-flag callback, and allows tracing instances. `nop_trace_init()` stores the active `trace_array` in `ctx_trace` and calls an empty start function; reset calls an empty stop function. Two options are declared: `test_nop_accept`, which `nop_set_flag()` accepts, and `test_nop_refuse`, which it rejects with `-EINVAL`. The tracing framework updates `nop_flags.val` only when the callback succeeds.

## Dependencies, Integration, Risks, and Tests
This file depends on core ftrace tracer registration structures from `trace.h`. It is usually registered by common tracing initialization rather than an initcall in this file. Integration points are `current_tracer`, trace instances, trace option display, and ftrace startup selftests.

Risks are intentionally low, but the file is useful as a sentinel: if the `nop` tracer cannot initialize or reset cleanly, the tracing subsystem's baseline state is broken. Test signals include switching to `nop`, toggling `test_nop_accept` and observing it persist, toggling `test_nop_refuse` and observing `-EINVAL`, instance support, and `trace_selftest_startup_nop` when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_nop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_osnoise.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_osnoise.c

## Purpose
Implements the `osnoise` tracer and, when configured, the `timerlat` tracer. `osnoise` measures operating-system interference observed by a sampling thread, accounting for hardware-like gaps, NMIs, IRQs, softirqs, and competing threads. `timerlat` measures latency from a pinned high-resolution timer interrupt to kernel or user thread execution.

## APIs, Control Flow, and State
The file registers tracer instances with `register_tracer()` at `late_initcall`, creates an `osnoise/` tracefs control directory, and optionally creates per-CPU `timerlat_fd` files for user-space timerlat mode. Important runtime entry points are `trace_osnoise_callback()` for NMI entry/exit, `osnoise_trace_irq_entry/exit()` for IRQ instrumentation, tracepoint callbacks for IRQ, softirq, scheduler switch, and scheduler migration events, plus tracer callbacks for init/reset/start/stop.

Global configuration lives in `osnoise_data`: sample period/runtime, stop thresholds, timerlat period/alignment, stack-print threshold, active timerlat flag, and taint status. Options live in `osnoise_options` and include workload mode, panic-on-stop, preempt-disable, IRQ-disable, and timerlat alignment. Active trace arrays are tracked in an RCU-protected `osnoise_instances` list. Per-CPU `osnoise_variables` hold the sampling kthread, sampled PID, sampling flag, NMI/IRQ/softirq/thread counters and timing windows, and an interrupt counter used to take interference-safe timestamps. Per-CPU `timerlat_variables` hold hrtimer state, period tracking, tracing-thread state, activation count, and user-thread migration flags.

The `osnoise` workload starts once for the first registered instance. It resets per-CPU variables, hooks IRQ/softirq/thread events, enables NMI callbacks with ordering barriers, and starts per-CPU kthreads if workload mode requires them. `run_osnoise()` samples `trace_clock_local()` in a loop for `runtime_us`, optionally with IRQs or preemption disabled, records gaps above `tracing_thresh` or 1 us, differentiates hardware-like noise from interrupt/thread interference using the interrupt counter, records a `TRACE_OSNOISE` event into each active instance, updates max latency, and stops tracing when configured thresholds are exceeded. `timerlat_main()` arms an `HRTIMER_MODE_ABS_PINNED_HARD` timer, records IRQ and thread latency samples, optionally dumps saved IRQ stacks, and updates max latency. User-mode timerlat opens per-CPU `timerlat_fd`, verifies CPU pinning, arms the timer in `read()`, records `THREAD_CONTEXT` and `THREAD_URET` samples, and kills or rejects migrated user threads.

Tracefs controls are serialized by `trace_types_lock`, `interface_lock`, and CPU hotplug read locks. `period_us` and `runtime_us` use `trace_min_max_fops` with mutual bounds. `cpus` parses and prints CPU lists. `options` accepts option names, `NO_` prefixes, and `DEFAULTS`, stopping and restarting workloads around changes. CPU hotplug support starts and stops per-CPU workers for allowed CPUs. Stop paths unregister instances first and only unhook events/stop workers when the last instance is gone.

## Dependencies, Integration, Risks, and Tests
Dependencies include tracefs, kthreads, hrtimers, CPU hotplug, cpumasks, scheduler and IRQ tracepoints, optional arch IRQ-vector hooks, NMI entry/exit callbacks, stacktrace support, trace-array printing, trace events from `trace/events/osnoise.h`, and standard output handlers in `trace_output.c`. Integration points are `current_tracer` values `osnoise` and `timerlat`, `osnoise/*` tracefs files, generated `TRACE_OSNOISE`, `TRACE_TIMERLAT`, and stack events, latency fsnotify, and panic/trace-off behavior for threshold violations.

Risks are high because the tracer deliberately runs near scheduler, IRQ, NMI, and hotplug boundaries. Bugs can mis-account nested interference, race with NMI callbacks despite barriers, leave per-CPU kthreads pinned or stopped incorrectly, mishandle CPU hotplug, allow invalid runtime/period combinations, mis-handle user-space timerlat migration, or stop tracing for all instances unexpectedly. Timerlat stack capture must avoid printing from IRQ context and must handle missing stacktrace support. Test signals include enabling/disabling both tracers across multiple instances, changing every tracefs knob while running, CPU hotplug while active, workload and no-workload modes, user timerlat with correct and incorrect CPU affinity, stop threshold and panic-on-stop behavior, stack dump threshold behavior, PREEMPT_RT and non-RT softirq accounting, and validation of `TRACE_OSNOISE`/`TRACE_TIMERLAT` output against expected latency events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_osnoise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_output.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_output.c

## Purpose
Provides the central trace event output registry and the standard printers for built-in ftrace event record types. It formats flags, symbols, arrays, bitmasks, contexts, latency headers, function records, scheduler records, stack traces, printk records, osnoise/timerlat records, raw data, and function-repeat records.

## APIs, Control Flow, and State
The global event registry is `event_hash`, protected by `trace_event_sem`, with dynamic event IDs allocated from `trace_event_ida`. Public registry APIs are `register_trace_event()`, `unregister_trace_event()`, `__unregister_trace_event()`, `ftrace_find_event()`, `trace_event_read_lock()`, and `trace_event_read_unlock()`. `init_events()` registers built-in `TRACE_FN`, `TRACE_CTX`, `TRACE_WAKE`, `TRACE_STACK`, `TRACE_USER_STACK`, `TRACE_BPUTS`, `TRACE_BPRINT`, `TRACE_PRINT`, `TRACE_HWLAT`, `TRACE_OSNOISE`, `TRACE_TIMERLAT`, `TRACE_RAW_DATA`, and `TRACE_FUNC_REPEATS` event descriptors.

Formatting helpers include `trace_print_flags_seq()`, `trace_print_symbols_seq()`, 32-bit-only u64 variants, `trace_print_bitmask_seq()`, `trace_print_hex_seq()`, `trace_print_array_seq()`, `trace_print_hex_dump_seq()`, `trace_raw_output_prep()`, `trace_event_printf()`, `trace_output_call()`, `trace_seq_print_sym()`, `seq_print_ip_sym()`, `trace_print_lat_fmt()`, `trace_print_context()`, and `trace_print_lat_context()`. With `CONFIG_FUNCTION_TRACE_ARGS`, `print_function_args()` uses BTF function prototypes to print ftrace-captured arguments.

Control flow for output is table-driven. Each `struct trace_event` has `trace_event_functions`; missing raw/hex/binary handlers default to `trace_nop_print()`. Built-in handlers convert the ring-buffer entry at `iter->ent` into human-readable, raw, hex, or binary forms. `print_event_fields()` walks event field metadata and prints structured fields safely, including bounds checks for dynamic string/array offsets and fallback representations for invalid or non-printable data. Context and latency printers compute task names, TGIDs, CPU IDs, IRQ/preempt state flags, timestamps, relative latency marks, and symbolized instruction pointers.

## Dependencies, Integration, Risks, and Tests
This file depends on the trace ring-buffer iterator model, kallsyms, ftrace, kprobes for kretprobe trampoline detection, scheduler/user memory helpers, BTF/BPF for argument printing, IDA allocation, and trace event field metadata. It is integrated by almost every tracing consumer: tracefs `trace`, `trace_pipe`, event `format` interpretation, kprobe/uprobe output, trace_printk output, osnoise/timerlat tracers, hwlat tracer, stack tracing, and dynamic event registration.

Risks include output buffer overflow handling, event type collisions, forgetting to hold `trace_event_sem` while looking up or printing event fields, unsafe user VMA lookup for user stacks, malformed dynamic string offsets, printing adjusted addresses incorrectly for relocated buffers, BTF lifetime handling, and ABI-like formatting changes that break tracing tools. Test signals include registering and unregistering dynamic events, dumping each built-in event in normal/raw/hex/binary modes, fuzzing dynamic string field sizes, printing user stacks with and without `SYM_USEROBJ`, BTF argument formatting on functions with simple and complex types, 32-bit and 64-bit builds, and verifying osnoise/timerlat/trace_printk records render correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_output.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_output.h

## Purpose
Declares the trace output helper APIs shared by trace output producers and printers.

## APIs, Control Flow, and State
The header exports prototypes for printk-message-only printers, symbol/IP printing, context printing, latency context printing, event-field printing, trace event registry locking and lookup, no-op printing, latency flag formatting, and module unregister support. It exposes `trace_event_sem` for module-side unregister paths. It also defines `SEQ_PUT_FIELD()` and `SEQ_PUT_HEX_FIELD()` helpers for binary/hex output, plus the `print_function_args()` declaration or a stub that prints `()` when function-argument tracing is disabled.

The inline helpers `seq_print_ip_sym_offset()` and `seq_print_ip_sym_no_offset()` wrap `seq_print_ip_sym()` while forcing or clearing `TRACE_ITER(SYM_OFFSET)`. There is no persistent state owned by the header; state is owned by `trace_output.c` and caller trace iterators.

## Dependencies, Integration, Risks, and Tests
The header depends on `trace_seq.h` and local `trace.h`. It integrates standard output helpers into kprobe, mmiotrace, KDB ftrace dump, event printers, and modules unregistering trace events. Risks are declaration drift with `trace_output.c`, misuse of `trace_event_sem`, and differing behavior of `print_function_args()` across configurations. Test signals are compile coverage across configurations with and without `CONFIG_FUNCTION_TRACE_ARGS`, module event unregister paths, and output users that include this header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_output.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_pid.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_pid.c

## Purpose
Implements helper logic for tracing PID filters: membership checks, ignore decisions, fork/exit propagation, seq_file iteration, and user writes that construct new PID filter lists atomically.

## APIs, Control Flow, and State
`trace_find_filtered_pid()` wraps `trace_pid_list_is_set()`. `trace_ignore_this_task()` applies include and exclude lists: a task is ignored if an include list exists and lacks the PID, or if an exclude list contains the PID. `trace_filter_add_remove_task()` propagates PID filters across forks when the parent is included and removes PIDs on exit when `self` is NULL.

Seq-file helpers are `trace_pid_start()`, `trace_pid_next()`, and `trace_pid_show()`. They iterate `trace_pid_list` bitsets while returning `pid + 1` as the cursor so PID 0 can be represented without colliding with NULL. `trace_pid_write()` parses user input with a `trace_parser`, builds a completely new `trace_pid_list`, copies existing filtered PIDs first, parses numeric PIDs from the write buffer, and only publishes the new list through `*new_pid_list` if the whole write succeeds. An empty successful write clears the list by returning NULL.

## Dependencies, Integration, Risks, and Tests
The file depends on `trace_pid_list` helpers, `trace_parser`, user-copy helpers in tracing code, task PIDs, and seq_file. It integrates with tracefs PID filter files such as tracing PID include/exclude controls and fork/exit tracing propagation.

Risks include partial-write semantics, PID truncation from unsigned long to `pid_t`, memory allocation failures, all-or-nothing list replacement expectations, and cursor arithmetic around PID 0. Tests should cover adding multiple PIDs, clearing lists, malformed input rollback, copying an existing list while adding more PIDs, include/exclude precedence, fork propagation only from listed parents, exit removal, and seq iteration including PID 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_preemptirq.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_preemptirq.c

## Purpose
Provides the low-level tracepoint glue for hard IRQ enable/disable and preempt enable/disable transitions. It emits `preemptirq` trace events and forwards transitions to latency tracers such as `irqsoff` and `preemptoff`.

## APIs, Control Flow, and State
The file defines tracepoints from `trace/events/preemptirq.h` via `CREATE_TRACE_POINTS`. With `CONFIG_TRACE_IRQFLAGS`, it exports `trace_hardirqs_on_prepare()`, `trace_hardirqs_on()`, `trace_hardirqs_off_finish()`, and `trace_hardirqs_off()`. A per-CPU `tracing_irq_cpu` flag suppresses redundant hardirq-off/on transitions. The "prepare" and "finish" variants omit lockdep calls for low-level entry code ordering; the full variants also call `lockdep_hardirqs_on_prepare()`, `lockdep_hardirqs_on()`, or `lockdep_hardirqs_off()`.

With `CONFIG_TRACE_PREEMPT_TOGGLE`, `trace_preempt_on()` and `trace_preempt_off()` emit `preempt_enable` / `preempt_disable` tracepoints and call `tracer_preempt_on/off()`. The local `trace(point, args)` wrapper is configuration-sensitive: noinstr-capable architectures use regular tracepoint calls, while older architectures avoid NMI context and temporarily enter/exit RCU watching for idle tasks so tracepoint execution is legal.

## Dependencies, Integration, Risks, and Tests
Dependencies include hardirq/lockdep state tracking, context tracking RCU helpers, NMI checks, preemptirq trace events, kprobe `NOKPROBE_SYMBOL`, and the tracer hooks implemented in `trace_irqsoff.c`. Integration points are architecture entry/exit code, lockdep, tracepoints visible to ftrace/perf/BPF, and latency tracers.

Risks are ordering-sensitive: tracing must not run when RCU is not watching unless it explicitly enters context tracking, NMI contexts are excluded on older paths, lockdep ordering differs between prepare/finish and full APIs, and missing per-CPU state transitions can duplicate or drop IRQ state events. Test signals include IRQ flag tracepoint enablement, lockdep IRQ state validation, idle-path IRQ tracing, preempt toggle tracepoints, `irqsoff`/`preemptoff` latency tracer interaction, and architecture builds with and without `CONFIG_ARCH_WANTS_NO_INSTR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_preemptirq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_printk.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_printk.c

## Purpose
Implements `trace_printk()` and related tracing-print helpers. It records formatted debugging messages into tracing ring buffers, supports binary-format printk records, tracks format strings for user-space decoding, creates `printk_formats`, and provides instance-safe `trace_array_printk()` APIs.

## APIs, Control Flow, and State
User-facing exported helpers include `__trace_bprintk()`, `__ftrace_vbprintk()`, `__trace_printk()`, `__ftrace_vprintk()`, `__trace_puts()`, `__trace_bputs()`, `trace_vbprintk()`, `trace_vprintk()`, `trace_array_printk()`, `trace_array_vprintk()`, `trace_array_init_printk()`, `trace_array_printk_buf()`, `trace_printk_init_buffers()`, `trace_printk_control()`, and command-line recording helpers. `trace_is_tracepoint_string()` checks the `__tracepoint_str` section.

For modules, the file maintains `trace_bprintk_fmt_list` under `btrace_mutex`. The module notifier copies module `__trace_printk_fmt` strings into stable kernel memory on `MODULE_STATE_COMING`, so binary printk events remain decodable after module unload. The `printk_formats` seq file iterates core `__trace_bprintk_fmt`, `__tracepoint_str`, and saved module formats, escaping newlines, tabs, backslashes, and quotes. Opening this file is blocked by `security_locked_down(LOCKDOWN_TRACEFS)`.

Runtime message state includes `trace_printk_enabled`, per-CPU `trace_percpu_buffer` with four nesting slots of `TRACE_BUF_SIZE`, and `buffers_allocated`. `trace_printk_init_buffers()` allocates the per-CPU buffers, prints the prominent debug-kernel warning, expands tracing buffers, and starts command-line recording if the system is already running. `get_trace_buf()` and `put_trace_buf()` provide lockless nested formatting storage with barriers. Binary paths (`__trace_bputs()`, `trace_vbprintk()`) fall back to text for boot-mapped trace arrays because binary format pointers are unsafe across boots. Text paths reserve `TRACE_PRINT` entries, copy formatted strings, and optionally add stack traces.

## Dependencies, Integration, Risks, and Tests
Dependencies include trace arrays and ring buffers, trace options (`TRACE_ITER(PRINTK)`), module notifiers, linker sections for printk and tracepoint strings, per-CPU allocation, security lockdown, command-line recording, graph tracing pause/unpause, and `trace_output.c` printers for `TRACE_PRINT`, `TRACE_BPRINT`, and `TRACE_BPUTS`. Integration points are kernel debugging call sites using `trace_printk()`, trace instances that call `trace_array_printk()`, module load/unload, tracefs `printk_formats`, and mmiotrace marks through `trace_vprintk()`.

Risks include using `trace_printk()` in production kernels, format-string pointer lifetime after module unload, binary records in boot-persistent buffers, recursion/nesting overflow in per-CPU buffers, tracing while disabled or during selftests, graph trace pollution, and global-buffer noise from code that should use instance-specific `trace_array_printk()`. Test signals include binary and text printk events in trace output, module format string persistence after unload, `printk_formats` content and lockdown denial, nested trace_printk calls up to the buffer limit, boot-buffer fallback to text printing, instance-only `trace_array_printk()` behavior, and command-line recording starting once buffers are allocated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_printk.c -->
