# subset-b-006075 Research

Grouped source research for trace probe parsing, remote trace buffers, scheduler tracing helpers, trace sequence formatting, snapshots, stack tracing, stat tracefs output, synthetic event declarations, and ftrace selftests. Each source file has a marker-delimited section for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_probe.c

## Purpose

`trace_probe.c` is the shared implementation for dynamic probe events used by kprobes, uprobes, fprobes, and event probes. It parses user probe arguments into a compact fetch-instruction program, resolves symbols and BTF arguments, defines trace event fields, builds print formats, manages shared `trace_probe_event` lifetime, and logs parser errors through the tracing error log. The complete 2284-line file was read.

## Important APIs, Types, and Functions

Important exported or shared functions include `trace_probe_log_init()`, `trace_probe_log_clear()`, `trace_probe_log_set_index()`, `traceprobe_split_symbol_offset()`, `traceprobe_parse_event_name()`, `traceprobe_parse_probe_arg()`, `traceprobe_expand_meta_args()`, `traceprobe_expand_dentry_args()`, `traceprobe_finish_parse()`, `traceprobe_update_arg()`, `traceprobe_set_print_fmt()`, `traceprobe_define_arg_fields()`, `trace_probe_init()`, `trace_probe_cleanup()`, `trace_probe_append()`, `trace_probe_unlink()`, `trace_probe_register_event_call()`, `trace_probe_add_file()`, `trace_probe_remove_file()`, `trace_probe_compare_arg_type()`, `trace_probe_match_command_args()`, `trace_probe_create()`, and `trace_probe_print_args()`. Config-gated BTF helpers map BTF integer, enum, pointer, field, and bitfield metadata onto probe fetch types. Config-gated entry-data helpers store function-entry arguments for return probes.

## Control Flow

Probe creation starts by splitting a raw command into argv, parsing group/event names, expanding `$arg*` or dentry `%p[dD]` shortcuts, and then parsing each argument body. Argument parsing recognizes `$` variables, registers, immediates, memory references, nested dereferences, BTF variable names, arrays, explicit types, bitfields, strings, user strings, and symbol strings. The result is a bounded `FETCH_INSN_MAX` program ending in `FETCH_OP_END`. Registration then creates the trace event call and fields. Runtime printing walks argument metadata and delegates each stored field to its type-specific print function.

## State and Persistence Behavior

State is mostly dynamic kernel memory attached to `struct trace_probe`, `struct trace_probe_event`, and per-argument `struct fetch_insn` arrays. Event flags use acquire/release helpers in the header. File links are RCU-delayed on removal. Parser error state is global and protected by `dyn_event_ops_mutex`. BTF references are held in the parse context and released by `traceprobe_finish_parse()`. Return-probe entry-data programs persist with the probe until cleanup.

## Dependencies and Integration Points

The file depends on trace event registration, tracefs dynamic event locking, BTF lookup, kallsyms, ftrace field definitions, perf-local probe creation declarations, and architecture register/function-argument access helpers. It is the common parser and event-lifetime layer beneath `trace_kprobe.c`, `trace_uprobe.c`, `trace_eprobe.c`, and fprobe-style consumers.

## Risks and Edge Cases

The highest risks are parser offset reporting drift, incorrect cleanup of `FETCH_NOP_SYMBOL` or immediate-string allocations on partial parse failure, overflow of `MAX_PROBE_EVENT_SIZE`, BTF reference leaks, invalid entry-argument offsets for return probes, field-name collisions with common trace fields, and symbol resolution changes between parse and registration. String and array handling is subtle because dynamic data sizes are computed before storage and data-location fields must stay consistent.

## Test Signals

Useful signals include dynamic event selftests for kprobe/uprobe/eprobe syntax, BTF `$arg*` expansion, dentry `%p[dD]` expansion, invalid parser diagnostics, duplicate event and argument conflicts, return-probe entry arguments, symbol updates after module load, tracefs enable/disable of probe files, and perf local probe creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_probe.h

## Purpose

`trace_probe.h` defines the common contracts for probe-based dynamic events: fetch operations, fetch types, probe argument descriptors, probe event lifetime structures, parser context, parser flags, error codes, and helper prototypes. The complete 596-line header was read.

## Important APIs, Types, and Functions

Key constants include `MAX_TRACE_ARGS`, `MAX_ARGSTR_LEN`, `MAX_ARRAY_LEN`, `MAX_STRING_SIZE`, `MAX_PROBE_EVENT_SIZE`, `FIELD_STRING_IP`, `FIELD_STRING_RETIP`, and `FIELD_STRING_FUNC`. `enum fetch_op` defines the fetch VM stages from source loading through dereference, store, bitfield modification, and array looping. Core types are `struct fetch_insn`, `struct fetch_type`, `struct probe_arg`, `struct probe_entry_arg`, `struct trace_probe_event`, `struct trace_probe`, `struct event_file_link`, and `struct traceprobe_parse_context`. Inline helpers expose data-location encoding, event flag access, event-call conversion, sibling/file-list checks, and parser flag checks.

## Control Flow

The header does not implement full control flow, but it defines the lifecycle used by implementation files: initialize a `trace_probe`, parse arguments into `probe_arg.code`, register a `trace_event_call`, add trace event files as the event is enabled, fetch and store runtime arguments, print fields, and eventually remove files and clean up allocations.

## State and Persistence Behavior

`struct trace_probe_event` owns the trace event class, call, files list, probes list, and optional uprobe filter. Multiple `trace_probe` instances can share one event as siblings. `event->flags` records trace/profile enablement with acquire/release semantics. `probe_arg` state persists user-visible field names, original command text, type, array count, offsets, and generated formats.

## Dependencies and Integration Points

The header includes tracing internals, trace output, tracefs, kprobes, BTF, perf, ptrace, uaccess, and architecture bit-width definitions. It is included by the probe implementations and by fetch helper templates.

## Risks and Edge Cases

This header is a cross-subsystem ABI inside ftrace. Changing enum order, struct ownership, flag semantics, or max sizes can break all dynamic probe implementations. Data-location helpers assume `u32` `__data_loc` layout. Parser flags have mutually exclusive combinations that callers must respect. Some prototypes compile to no-ops when config options such as kprobe events, perf events, or function argument access are disabled.

## Test Signals

Compile coverage across config matrices is important. Runtime tests should cover trace/profile enable flags, sibling probes sharing an event, event file add/remove, parser flag combinations, max argument limits, dynamic string fields, and return-probe entry data on architectures with and without argument access APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe_kernel.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_probe_kernel.h

## Purpose

`trace_probe_kernel.h` supplies kernel and user memory fetch primitives for probe argument storage. It is intentionally dependent on `trace_probe.h` but cannot include it because `trace_probe_tmpl.h` is included by multiple probe users. The complete 119-line header was read.

## Important APIs, Types, and Functions

Important helpers are `fetch_store_strlen_user()`, `fetch_store_strlen()`, `set_data_loc()`, `fetch_store_string_user()`, `fetch_store_string()`, `probe_mem_read_user()`, and `probe_mem_read()`. They use nofault string and memory copy APIs and update probe `__data_loc` fields with `make_data_loc()`.

## Control Flow

String length helpers compute required dynamic storage first. Runtime storage helpers expect the destination data-location field to already encode the max dynamic length and offset. They copy user or kernel strings, set a zero-length location on fault, and return the copy result. Memory reads select user access when an architecture has non-overlapping address spaces and the address lies below `TASK_SIZE`.

## State and Persistence Behavior

The header owns no persistent state. It mutates destination trace record fields and dynamic data buffers supplied by callers.

## Dependencies and Integration Points

It depends on `MAX_STRING_SIZE`, data-location helpers, `copy_from_kernel_nofault()`, `strncpy_from_kernel_nofault()`, `copy_from_user_nofault()`, `strncpy_from_user_nofault()`, `strnlen_user_nofault()`, and architecture address-space configuration. It is consumed by the generic fetch template and kernel-side probe implementations.

## Risks and Edge Cases

Faulting memory must not crash tracing paths. String contents can change between the sizing pass and the storage pass. `set_data_loc()` converts negative copy results into zero length, so downstream printing shows a fault marker rather than stale data. User/kernel address selection is architecture-dependent and must not classify kernel pointers as user pointers incorrectly.

## Test Signals

Tests should cover valid and invalid kernel strings, valid and invalid user strings, dynamic string truncation at max length, address-space classification on supported architectures, and faulted memory reads producing safe trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe_kernel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe_tmpl.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_probe_tmpl.h

## Purpose

`trace_probe_tmpl.h` is the reusable inline runtime for executing a parsed probe fetch program. Callers define source-specific `process_fetch_insn()` and memory/string helpers, then include this template to handle common store, dynamic data sizing, bitfield, and array behavior. The complete 275-line file was read.

## Important APIs, Types, and Functions

Important helpers are `fetch_store_raw()`, `fetch_apply_bitfield()`, `fetch_store_symstrlen()`, `fetch_store_symstring()`, `process_common_fetch_insn()`, `process_fetch_insn_bottom()`, `__get_data_size()`, and `store_trace_args()`. The template expects `struct fetch_insn`, `struct trace_probe`, `struct probe_arg`, `FETCH_OP_*`, and type/data-location helpers from `trace_probe.h`.

## Control Flow

`process_fetch_insn_bottom()` implements the common fetch VM tail. It walks optional dereference operations, stores raw values, memory, user memory, kernel strings, user strings, or symbol strings, applies an optional bitfield transform, and repeats for arrays. A sizing call with `dest == NULL` computes dynamic string storage requirements without writing. `store_trace_args()` primes each dynamic argument's `__data_loc`, runs the fetch program, and advances the dynamic data pointer by the consumed length.

## State and Persistence Behavior

The template owns no global state. It mutates the trace record payload and relies on caller-provided record, entry-data, and base pointers. Dynamic data placement is transient per trace record.

## Dependencies and Integration Points

It integrates with kprobe, uprobe, fprobe, and event-probe fetch front ends. It depends on kallsyms for symbol strings, current task state for `$comm`, trace probe type metadata, and caller-provided nofault memory access functions.

## Risks and Edge Cases

The fetch VM is intentionally compact and order-sensitive. Risks include advancing past `FETCH_OP_END`, array loops over mixed string and non-string storage, stale `loc` values after string faults, bitfield shifts with wrong base size, dynamic length mismatch between sizing and storage, and silent nofault read errors for raw memory stores where callers do not inspect the result.

## Test Signals

Useful tests include scalar loads, nested dereferences, user dereferences, string arrays, non-string arrays, bitfields, symbol strings, `$comm`, immediate strings, dynamic data overflow boundaries, and malformed instruction streams returning `-EILSEQ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_probe_tmpl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_recursion_record.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_recursion_record.c

## Purpose

`trace_recursion_record.c` records ftrace callbacks that triggered recursion and exposes them through tracefs as `recursed_functions`. The complete 233-line file was read.

## Important APIs, Types, and Functions

The main public API is `ftrace_record_recursion(unsigned long ip, unsigned long parent_ip)`, exported GPL. Internal types and functions include `struct recursed_functions`, the `recursed_functions[]` fixed array, `nr_records`, `cached_function`, seq operations for reading records, `recursed_function_open()`, `recursed_function_write()`, and the `fs_initcall()` that creates the tracefs file.

## Control Flow

When recursion is detected, `ftrace_record_recursion()` first checks a racy cached IP, then reads `nr_records`, searches existing entries, and uses `cmpxchg()` to reserve a free slot. If another writer races, it advances to another slot rather than spinning indefinitely. Opening the tracefs file with write and truncate clears records by setting `nr_records` to `-1`, zeroing the array, and restoring the count to zero. Reads format parent and child symbols through `trace_seq`.

## State and Persistence Behavior

Records persist in a fixed-size global array until the tracefs file is truncated. `nr_records == -1` temporarily blocks writers during clear. `cached_function` is deliberately racy as a performance cache. Read-side formatting uses a global `tseq` protected by `recursed_function_lock`.

## Dependencies and Integration Points

This file integrates with ftrace recursion protection, tracefs, seq_file, kallsyms symbol formatting, and `trace_output.h` helpers.

## Risks and Edge Cases

Recording is best-effort. Concurrent writers may skip duplicates, consume the next slot, or observe clearing in progress. The array can fill and then silently stop recording. The clear path can race with writers, but the code accepts a possible zero entry because future recursion can record it again. Reads allocate a `trace_seq` after locking; allocation failure returns `ERR_PTR(-ENOMEM)`.

## Test Signals

Signals include ftrace recursion selftests, reading `recursed_functions`, truncating the file to clear records, concurrent recursion events from multiple CPUs, array-full behavior, and symbol formatting for parent and child IPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_recursion_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_remote.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_remote.c

## Purpose

`trace_remote.c` implements tracefs support for remote trace producers such as firmware or a hypervisor that write into a trace-compatible ring buffer while the kernel acts as reader. It registers `remotes/<name>` tracefs controls, creates eventfs metadata for remote events, lazily loads and unloads remote ring buffers, and provides consuming `trace_pipe` and non-consuming `trace` readers. The complete 1384-line file was read.

## Important APIs, Types, and Functions

Public APIs are `trace_remote_register()`, `trace_remote_alloc_buffer()`, and `trace_remote_free_buffer()`. Core internal types are `struct trace_remote` and `struct trace_remote_iterator`. Important helpers include `trace_remote_load()`, `trace_remote_try_unload()`, `trace_remote_enable_tracing()`, `trace_remote_disable_tracing()`, `trace_remote_reset()`, `trace_remote_get()`, `trace_remote_put()`, iterator allocation/free/read/move/print functions, tracefs file operations for `tracing_on`, `buffer_size_kb`, `trace_pipe`, and `trace`, and eventfs operations for `events/<remote>/<event>/{enable,id,format}` plus directory `enable`, `header_page`, and `header_event`.

## Control Flow

Registration allocates a `trace_remote`, initializes locks and defaults, creates the tracefs hierarchy, attaches a sorted event table, creates eventfs event directories, and invokes the optional callback init. Enabling tracing loads the remote buffer through callbacks and calls `enable_tracing(true)`. Readers also load the buffer and increment `nr_readers`. `trace_pipe` consumes events after polling/waiting, while `trace` builds ring-buffer iterators for non-consuming chronological reads. When tracing is off, there are no readers, and the ring buffer is empty, `trace_remote_try_unload()` frees the buffer and calls the remote unload callback.

## State and Persistence Behavior

`struct trace_remote` persists after registration and owns callback pointers, private data, tracefs dentries, eventfs state, event metadata, default buffer size, poll interval, tracing state, reader count, and locks. Buffer memory is loaded lazily and can be unloaded. Event enable state is stored in the caller-provided `remote_event` array. Per-reader iterators hold trace sequence buffers, ring buffer iterators, delayed polling work, position, CPU selection, and last event metadata.

## Dependencies and Integration Points

This file depends on `linux/trace_remote.h`, ring buffer remote APIs, tracefs, eventfs, seq_file, delayed work, CPU trace file helpers, and caller-provided callbacks for buffer load/unload, reader-page swapping, reset, tracing enable, and event enable. The event format output mirrors local trace event format files.

## Risks and Edge Cases

Important risks include incomplete cleanup on registration failures after tracefs creation, unsorted or duplicate event IDs breaking binary search lookup, reader count overflow, per-CPU lock allocation failure, `buffer_size_kb` changes while loaded returning `-EBUSY`, delayed poll work lifetime for consuming readers, partial event printing overflow, missing CPUs in remote buffer descriptors, and bulk event enable ignoring per-event errors in the loop.

## Test Signals

Tests should register a fake remote, validate tracefs and eventfs files, toggle tracing and events, resize buffer only while unloaded, read `trace` and `trace_pipe`, exercise per-CPU readers, inject lost events, confirm unknown event ID output, verify sorted-event validation, and check lazy unload after tracing stops and data drains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_remote.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_sched_switch.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_sched_switch.c

## Purpose

`trace_sched_switch.c` records task command names and TGIDs for trace output correlation. It registers scheduler tracepoint probes on demand, maintains saved command-line and TGID caches, and exposes tracefs file operations for saved command lines, command-line cache size, and saved TGIDs. The complete 665-line file was read.

## Important APIs, Types, and Functions

Public functions include `tracing_start_cmdline_record()`, `tracing_stop_cmdline_record()`, `tracing_start_tgid_record()`, `tracing_stop_tgid_record()`, `trace_create_savedcmd()`, `trace_save_cmdline()`, `trace_find_cmdline()`, `trace_find_tgid()`, `tracing_record_taskinfo()`, `tracing_record_taskinfo_sched_switch()`, `tracing_record_cmdline()`, `tracing_record_tgid()`, `trace_alloc_tgid_map()`, and `trace_free_saved_cmdlines_buffer()`. Exported file operation objects are `tracing_saved_tgids_fops`, `tracing_saved_cmdlines_fops`, and `tracing_saved_cmdlines_size_fops`.

## Control Flow

Start/stop helpers reference count whether command names or TGIDs are needed. The first reference registers `sched_wakeup`, `sched_wakeup_new`, and `sched_switch` tracepoints; the last unregisters them. Tracepoint probes record both sides of switches and wakeups when enabled. Command-line recording maps PID modulo `PID_MAX_DEFAULT` to a rotating command cache under `trace_cmdline_lock`. TGID recording writes into a dynamically allocated PID-indexed map. Seq readers iterate non-empty entries.

## State and Persistence Behavior

Global state includes scheduler tracepoint refcounts, `tgid_map`, `tgid_map_max`, and `savedcmd`. Saved command lines are a fixed-size rotating buffer whose size can be changed through tracefs. TGID map size follows `init_pid_ns.pid_max`. Per-CPU `trace_taskinfo_save` suppresses repeated recording until needed again.

## Dependencies and Integration Points

The file depends on scheduler tracepoints, task structs, tracing per-CPU flags, tracefs open helpers, seq_file, kmemleak annotations, and ftrace output paths that call `trace_find_cmdline()` or `trace_find_tgid()`.

## Risks and Edge Cases

The command-line cache is lossy due to PID hashing and rotation. `trace_save_cmdline()` intentionally uses trylock in scheduler context and may skip updates. TGID map publication uses release/acquire ordering with `tgid_map_max`; callers must allocate before enabling TGID recording. Stop reference counts assume balanced start/stop calls. Resizing command-line storage swaps the global pointer while readers and writers are protected by preemption disable plus spinlock.

## Test Signals

Useful signals include saved command-line tracefs reads, cache resize reads/writes, TGID map allocation and reads, balanced reference counting, scheduler tracepoint register/unregister errors, PID reuse, idle task handling, and tracing output showing command names and TGIDs after sched events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_sched_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_sched_wakeup.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_sched_wakeup.c

## Purpose

`trace_sched_wakeup.c` implements the `wakeup`, `wakeup_rt`, and `wakeup_dl` latency tracers. These tracers capture the time between a task wakeup and the task actually being scheduled, optionally recording function or function-graph trace context around the latency. The complete 830-line file was read.

## Important APIs, Types, and Functions

Important tracer callbacks include `wakeup_tracer_init()`, `wakeup_rt_tracer_init()`, `wakeup_dl_tracer_init()`, `wakeup_tracer_reset()`, `wakeup_tracer_start()`, `wakeup_tracer_stop()`, `wakeup_flag_changed()`, `wakeup_trace_open()`, `wakeup_trace_close()`, `wakeup_print_line()`, and `wakeup_print_header()`. Runtime probes include `probe_wakeup()`, `probe_wakeup_sched_switch()`, and `probe_wakeup_migrate_task()`. Function tracing helpers include `wakeup_tracer_call()`, `register_wakeup_function()`, `unregister_wakeup_function()`, and config-gated graph entry/return callbacks.

## Control Flow

Tracer initialization saves flags, forces overwrite and latency output, sets the active trace array, initializes ftrace ops, registers scheduler tracepoints, resets state, and starts optional function tracing. A wakeup probe filters candidates according to tracer mode and priority, records the wakeup event, stack, and function call, stores `wakeup_task`, CPU, priority, and timestamp. The sched-switch probe detects when that task is scheduled, records the switch and stack, computes latency, compares it to threshold or max latency, updates the max trace snapshot, and resets wakeup state.

## State and Persistence Behavior

The tracer uses global singleton state: `wakeup_trace`, `tracer_enabled`, `wakeup_task`, CPUs, priority, RT/DL mode flags, `tracing_dl`, `wakeup_lock`, saved trace flags, `function_enabled`, and `wakeup_busy`. `wakeup_task` holds a task reference until reset. Only one wakeup tracer instance can be active at a time.

## Dependencies and Integration Points

The file integrates with scheduler tracepoints, latency snapshot buffers, function and function-graph tracers, stack tracing, tracing thresholds, command-line recording, trace arrays, and tracer registration through `core_initcall()`.

## Risks and Edge Cases

The code is race-sensitive around global task state, migration, and tracer enable ordering. Memory barriers guard stale `wakeup_task` visibility. Deadline tasks suppress replacement until completion. Locking occurs in scheduler and IRQ-disabled paths, so recursion and latency overhead matter. Function graph mode requires careful toggling when `DISPLAY_GRAPH` changes. Reset must always drop the task reference.

## Test Signals

Signals include ftrace selftest startup for wakeup tracers, synthetic deadline wakeup tests, max latency updates, trace output for `wakeup`, `wakeup_rt`, and `wakeup_dl`, task migration during wakeup, graph display toggles, tracing threshold behavior, and clean refusal when another wakeup tracer is busy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_sched_wakeup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_selftest.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_selftest.c

## Purpose

`trace_selftest.c` is included into `trace.c` and provides boot/runtime selftests for ftrace and tracer implementations. It validates trace buffer entries, dynamic ftrace filters, recursion protection, saved regs support, function graph tracing, graph private storage, irqsoff/preemptoff latency tracers, wakeup tracers, nop tracer, and branch tracer. The complete 1567-line file was read.

## Important APIs, Types, and Functions

Major entry points are `trace_selftest_startup_function()`, `trace_selftest_startup_function_graph()`, `trace_selftest_startup_irqsoff()`, `trace_selftest_startup_preemptoff()`, `trace_selftest_startup_preemptirqsoff()`, `trace_selftest_startup_nop()`, `trace_selftest_startup_wakeup()`, and `trace_selftest_startup_branch()`. Helper families include `trace_test_buffer()`, dynamic ftrace probe callbacks and counters, `trace_selftest_ops()`, `trace_selftest_startup_dynamic_tracing()`, recursion tests, regs tests, fgraph storage fixtures, and the graph hang watchdog.

## Control Flow

Most tests initialize a tracer, generate activity, stop tracing, consume trace buffers to validate entry types and counts, reset the tracer, and restart global tracing. Dynamic ftrace tests apply filters to known test functions, register several `ftrace_ops`, call the functions, and verify exact counters. Function graph tests register a watchdog graph callback, sleep to collect data, validate buffers, optionally test direct-call coexistence, then test per-call graph storage sizes. Latency tests deliberately disable IRQs or preemption. Wakeup tests create a deadline kthread, wake it, and verify snapshot output.

## State and Persistence Behavior

State is test-local static counters, fixture arrays, temporary ftrace ops, and saved global settings such as `ftrace_enabled` and `tr->max_latency`. Tests deliberately consume ring buffer contents. On severe failure, function tracing may be killed or graph tracing stopped to protect the kernel.

## Dependencies and Integration Points

This file depends on numerous config options, ftrace dynamic filtering, function graph tracing, direct calls, tracer init/reset/start/stop methods, ring buffer consumption, scheduler deadline support, kthreads, completions, and known noinline test functions from `trace_selftest_dynamic.c`.

## Risks and Edge Cases

Selftests run in fragile contexts and must restore global tracing state. Hard-coded count expectations can vary with architecture features, recursion context transitions, command-line filters, and ftrace availability. Buffer validation consumes data and disables tracing while checking to avoid infinite loops. The graph watchdog protects against runaway graph tracing. Wakeup tests can be timing-sensitive on virtual machines, so they wait on completions where possible.

## Test Signals

The file itself is the test signal. Kernel boot logs should show PASS/FAIL progress for enabled tracer configs. Additional useful signals are no ftrace kill, no graph watchdog trigger, expected trace buffer counts, successful graph storage retrieval for 1/2/4/8 byte data, and no residual callbacks after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_selftest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_selftest_dynamic.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_selftest_dynamic.c

## Purpose

`trace_selftest_dynamic.c` defines two stable noinline functions used as dynamic ftrace test targets. The complete 15-line file was read.

## Important APIs, Types, and Functions

The only functions are `DYN_FTRACE_TEST_NAME()` and `DYN_FTRACE_TEST_NAME2()`. Both are marked `noinline __noclone`, return zero, and exist to produce mcount/ftrace call sites.

## Control Flow

There is no meaningful local control flow. Selftests call these functions after applying ftrace filters and registering callbacks.

## State and Persistence Behavior

The file owns no state. Its persistence value is symbol stability for ftrace filtering.

## Dependencies and Integration Points

It includes `trace.h` for macro names and integrates directly with `trace_selftest.c` dynamic ftrace, recursion, regs, and graph tests.

## Risks and Edge Cases

If the compiler inlines, clones, removes, or renames these functions, dynamic ftrace selftests can fail. The attributes are therefore central despite the trivial bodies. Architecture-specific symbol prefixes are handled by wildcard filters in the selftest code.

## Test Signals

Successful dynamic ftrace selftests prove these functions were emitted and filterable. Build symbol inspection can also confirm that both functions remain present and traceable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_selftest_dynamic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_seq.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_seq.c

## Purpose

`trace_seq.c` implements `struct trace_seq`, the tracing-specific string/byte formatting buffer used by trace output code before data is copied into seq_file or user buffers. It wraps `seq_buf` with no-partial-write semantics and exported helper functions. The complete 457-line file was read.

## Important APIs, Types, and Functions

Important exports include `trace_print_seq()`, `trace_seq_printf()`, `trace_seq_bitmask()`, `trace_seq_bitmask_list()`, `trace_seq_vprintf()`, `trace_seq_bprintf()`, `trace_seq_puts()`, `trace_seq_putc()`, `trace_seq_putmem()`, `trace_seq_putmem_hex()`, `trace_seq_path()`, `trace_seq_to_user()`, `trace_seq_hex_dump()`, and `trace_seq_acquire()`. Internal `__trace_seq_init()` lazily initializes zeroed objects.

## Control Flow

Each write helper exits early if the sequence is already full, lazily initializes the buffer, saves the old length, attempts a `seq_buf` operation, and restores the old length plus marks `full` on overflow. `trace_print_seq()` moves contents to a `seq_file` and resets only on success. `trace_seq_to_user()` copies from the current read position and advances it on successful copy.

## State and Persistence Behavior

State is contained in the caller-owned `struct trace_seq`: underlying `seq_buf`, `full` flag, and read position. The file owns no global state. Overflow is sticky until the caller reinitializes the sequence.

## Dependencies and Integration Points

It depends on `linux/trace_seq.h`, `seq_buf`, seq_file, uaccess, path formatting, bitmap formatting, binary printf support, and trace event printers throughout ftrace.

## Risks and Edge Cases

The key contract is all-or-nothing visible writes. Any helper that forgets to restore `seq.len` on overflow can expose partial output. `trace_seq_acquire()` assumes callers checked available space and warns if not. `trace_seq_to_user()` returns `-EBUSY` when the current buffer has been fully read, which readers use as a signal to refill.

## Test Signals

Tests should cover overflow rollback for printf, bprintf, bitmask, path, hex dump, puts/putc/mem boundaries, repeated `trace_seq_to_user()` reads, zero-initialized sequences, and `trace_print_seq()` reset only after successful seq_file copy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_seq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_snapshot.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_snapshot.c

## Purpose

`trace_snapshot.c` manages ftrace snapshot and max-latency buffers. It handles boot snapshot parameters, manual snapshot tracefs operations, conditional snapshots, max trace updates, snapshot mmap exclusion, ftrace snapshot commands, and boot-time snapshot capture. The complete 1066-line file was read.

## Important APIs, Types, and Functions

Important APIs include `tracing_snapshot_instance()`, `tracing_snapshot_cond()`, `tracing_cond_snapshot_data()`, `resize_buffer_duplicate_size()`, `tracing_alloc_snapshot_instance()`, `free_snapshot()`, `tracing_arm_snapshot_locked()`, `tracing_arm_snapshot()`, `tracing_disarm_snapshot()`, `tracing_snapshot_alloc()`, `tracing_snapshot_cond_enable()`, `tracing_snapshot_cond_disable()`, `trace_create_maxlat_file()`, `update_max_tr()`, `update_max_tr_single()`, `print_snapshot_help()`, `get_snapshot_map()`, `put_snapshot_map()`, `register_snapshot_cmd()`, `trace_allocate_snapshot()`, `do_allocate_snapshot()`, and `ftrace_boot_snapshot()`. File operations include `snapshot_fops` and `snapshot_raw_fops`.

## Control Flow

Boot parameters `alloc_snapshot` and `ftrace_boot_snapshot` request early allocation or named-instance snapshots. Manual writes to `snapshot` allocate, swap, clear, reset, or free buffers depending on the value and CPU scope. Snapshot updates verify allocation, NMI context, mapped buffers, active latency tracers, and conditional snapshot callbacks before swapping buffers under `max_lock`. Function-filter snapshot commands arm snapshot accounting before registering ftrace probes and disarm on unregister or failure.

## State and Persistence Behavior

Per-trace-array state includes `allocated_snapshot`, `snapshot_buffer`, `snapshot` arm count, `mapped` count, `cond_snapshot`, `max_latency`, max trace task metadata, and optional fsnotify work. Global boot state tracks allocation requests and boot snapshot names. Snapshot buffers persist until freed or resized to one entry.

## Dependencies and Integration Points

The file integrates with ring buffer resize/swap APIs, trace array locking, tracefs file operations, raw tracing buffers, latency tracers, ftrace function commands, fsnotify/irq_work, boot `__setup` parsing, and snapshot-compatible tracer policy.

## Risks and Edge Cases

Snapshots are mutually exclusive with mapped buffers, active snapshot-using tracers, and conditional snapshot updates. Per-CPU swaps can fail with commit or resize in progress. Manual snapshot writes must arm and disarm snapshot counters correctly on all paths. Conditional snapshot callbacks run under `max_lock`. Boot name matching is subtle and can allocate for all instances if no names are supplied.

## Test Signals

Tests should cover boot allocation parameters, manual `snapshot` writes for 0/1/other values, per-CPU snapshot behavior with and without swap support, raw snapshot reads, conditional snapshot enable/disable/update, mmap exclusion via `get_snapshot_map()`, ftrace `:snapshot` commands with counts, and max-latency file updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_snapshot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stack.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_stack.c

## Purpose

`trace_stack.c` implements the kernel stack tracer. It uses ftrace callbacks to measure current stack depth, records the largest observed stack with symbol locations and per-frame sizes, exposes tracefs files for the maximum and stack trace, supports dynamic ftrace filtering, and registers a sysctl to enable or disable tracing. The complete 600-line file was read.

## Important APIs, Types, and Functions

Important functions include `check_stack()`, `stack_trace_call()`, `stack_max_size_read()`, `stack_max_size_write()`, seq operations for `stack_trace`, `stack_trace_filter_open()`, `stack_trace_sysctl()`, boot parser `enable_stacktrace()`, init function `stack_trace_init()`, and sysctl init `init_trace_stack_sysctls()`. Global state includes `stack_dump_trace[]`, `stack_trace_index[]`, `stack_trace_nr_entries`, `stack_trace_max_size`, `stack_trace_max_lock`, per-CPU `disable_stack_tracer`, `stack_sysctl_mutex`, and `stack_tracer_enabled`.

## Control Flow

When enabled, ftrace calls `stack_trace_call()`, which disables preemption, increments a per-CPU recursion guard, verifies RCU watching, adjusts the IP, and calls `check_stack()`. `check_stack()` computes stack usage from a local variable address, ignores non-task stacks and NMI context, locks, records a new max, saves stack entries, maps saved return addresses back to stack offsets, handles architecture shift rules, and BUGs on stack-end corruption. Tracefs seq reads lock and print the stored max stack.

## State and Persistence Behavior

The maximum stack record persists globally until overwritten or reset through `stack_max_size`. `stack_tracer_enabled` persists through sysctl and boot command-line setup. Optional filter text from `stacktrace_filter=` is stored in initdata and applied during init.

## Dependencies and Integration Points

The file depends on ftrace, stacktrace APIs, task stack helpers, tracefs, security lockdown checks, sysctl, kallsyms symbol formatting, command-line setup, and dynamic ftrace filtering.

## Risks and Edge Cases

Stack tracing runs from ftrace and must avoid recursion, NMI deadlocks, non-task stacks, and RCU-off contexts. Frame-size calibration is architecture-sensitive. Stack walking can miss return addresses, so the code tolerates gaps. Locking disables interrupts and increments recursion guards when writing the max size. Incorrect filter or enable ordering can register callbacks too early or leave them active.

## Test Signals

Signals include booting with `stacktrace`, toggling `/proc/sys/kernel/stack_tracer_enabled`, reading `stack_trace`, resetting `stack_max_size`, applying `stack_trace_filter`, verifying no output when disabled and no max seen, and architecture stack-shift behavior under deep call chains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stat.c -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_stat.c

## Purpose

`trace_stat.c` provides tracefs infrastructure for one-shot tracer statistics. A tracer registers a `struct tracer_stat`, and this file creates a `trace_stat/<name>` file that snapshots, sorts, and displays the tracer's current statistic entries on each open. The complete 358-line file was read.

## Important APIs, Types, and Functions

Public APIs are `register_stat_tracer()` and `unregister_stat_tracer()`. Internal types are `struct stat_node` and `struct stat_session`. Important helpers include `__reset_stat_session()`, `reset_stat_session()`, `destroy_session()`, `insert_stat()`, `dummy_cmp()`, `stat_seq_init()`, seq operations, `tracing_stat_open()`, `tracing_stat_release()`, `tracing_stat_init()`, and `init_stat_file()`.

## Control Flow

Registration validates callbacks, rejects duplicate tracer pointers, allocates a session, creates the `trace_stat` directory if needed, creates a tracefs file, and links the session globally. Opening a stat file checks lockdown, clears old snapshot data, iterates the tracer callbacks, inserts each entry into an rb-tree sorted by the tracer comparator or `dummy_cmp`, then serves seq_file reads from the tree. Release clears the tree to avoid stale memory. Unregister removes the file and destroys the session.

## State and Persistence Behavior

Global state is `all_stat_sessions` plus `stat_dir`. Each session persists the tracer pointer, rb-tree snapshot, mutex, and file dentry. Statistic entries are transient per open; `stat_release` is called when snapshots are reset or destroyed.

## Dependencies and Integration Points

The file depends on `trace_stat.h`, tracefs, seq_file, rbtrees, security lockdown, and tracer-provided callbacks. It is generic infrastructure for tracers that want sorted text statistics without implementing their own tracefs plumbing.

## Risks and Edge Cases

If insertion fails mid-open, already captured entries must be released. The comparator sorts descending by treating `result >= 0` as left. `dummy_cmp()` mutates `ts->stat_cmp`, which means a tracer without a comparator gets permanently assigned the dummy. Duplicate detection is by `tracer_stat` pointer, not by name, so name collisions rely on tracefs creation failure.

## Test Signals

Tests should register a fake stat tracer, read headers and sorted rows, exercise no-entry output, force allocation failure paths if possible, unregister while idle, verify `stat_release` calls, and confirm lockdown blocks open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stat.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_stat.h

## Purpose

`trace_stat.h` declares the tracer statistics registration interface used by `trace_stat.c`. The complete 34-line header was read.

## Important APIs, Types, and Functions

The central type is `struct tracer_stat`, with fields for file name, iteration callbacks `stat_start` and `stat_next`, optional comparator `stat_cmp`, row printer `stat_show`, optional entry release `stat_release`, and optional header printer `stat_headers`. Public functions are `register_stat_tracer()` and `unregister_stat_tracer()`.

## Control Flow

The header defines a pull-based contract. A tracer supplies callbacks; the trace stat infrastructure calls `stat_start()`, repeatedly calls `stat_next()`, sorts entries if a comparator is present, optionally prints headers, and calls `stat_show()` for each entry.

## State and Persistence Behavior

The header owns no state. A registered `tracer_stat` object must outlive its registration. Any per-entry state returned by the tracer is released through `stat_release()` if supplied.

## Dependencies and Integration Points

It includes `linux/seq_file.h` for output and relies on `cmp_func_t` from kernel headers. It is consumed by tracing subsystems that expose one-shot statistics through tracefs.

## Risks and Edge Cases

Callback ownership must be clear: entries returned during a session may be cached until file release. Missing required callbacks are rejected by the implementation. Name uniqueness is not expressed in the type and is enforced only indirectly by tracefs file creation.

## Test Signals

Compile tests for users of `struct tracer_stat`, plus runtime registration, sorted output, headers, release callbacks, and unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_synth.h -->
# sources/distributed-fs/ceph-client/kernel/trace/trace_synth.h

## Purpose

`trace_synth.h` declares the in-kernel structures for synthetic trace events, including fields, dynamic string metadata, event registration state, and lookup by name. The complete 41-line header was read.

## Important APIs, Types, and Functions

Constants are `SYNTH_SYSTEM`, `SYNTH_FIELDS_MAX`, and `STR_VAR_LEN_MAX`. `struct synth_field` stores type/name strings, size, offset, field position, signed/string/dynamic/stack flags. `struct synth_event` embeds `struct dyn_event`, reference count, name, field arrays, dynamic field arrays, `n_u64`, event class, event call, tracepoint pointer, and module pointer. The public lookup is `find_synth_event(const char *name)`.

## Control Flow

The header has no executable flow. Synthetic event implementation code creates `synth_event` objects, populates fields, registers trace event metadata, exposes dynamic events, and uses `find_synth_event()` to resolve references by name.

## State and Persistence Behavior

Synthetic event state is represented by `struct synth_event` and persists while the dynamic event is registered or referenced. Reference count and module pointer indicate lifetime integration with modules and users.

## Dependencies and Integration Points

It includes `trace_dynevent.h` and integrates with dynamic events, trace event classes/calls, tracepoints, modules, filters, and histogram/synthetic event users.

## Risks and Edge Cases

Field limits and string length limits must match trace event encoding and filter expectations. Dynamic fields require correct offsets and `n_u64` sizing. Module-backed synthetic events must not outlive their module. Lookup by name must handle references and deletion races in the implementation.

## Test Signals

Tests should create synthetic events with scalar and dynamic string fields, hit `SYNTH_FIELDS_MAX`, validate format files, emit events, delete referenced events, and use `find_synth_event()` through histogram or dynamic event paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/kernel/trace/trace_synth.h -->
