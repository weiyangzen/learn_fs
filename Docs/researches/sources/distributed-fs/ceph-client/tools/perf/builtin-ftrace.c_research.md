<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c -->
# sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c

## Purpose
Implements `perf ftrace`, a wrapper around kernel ftrace tracefs/debugfs facilities. It supports the default trace subcommand, function latency histograms, and function profiling, while sharing perf target parsing for PID/TID/CPU/workload selection.

## Important APIs, Types, and Functions
The entry point is `cmd_ftrace()`. Runtime command paths are `__cmd_ftrace()` for live trace_pipe streaming, `__cmd_latency()` for function or event-pair latency histograms, and `__cmd_profile()` for per-function duration aggregation. Important setup and tracefs helpers include `check_ftrace_capable()`, `is_ftrace_supported()`, `init_tracing_instance()`, `exit_tracing_instance()`, `get_tracing_instance_file()`, `write_tracing_file()`, `append_tracing_file()`, `read_tracing_file_to_stdout()`, `read_tracing_file_by_line()`, `reset_tracing_files()`, `reset_tracing_options()`, `set_tracing_options()`, and `select_tracer()`.

Filtering and option helpers include `parse_filter_func()`, `parse_filter_event()`, `parse_buffer_size()`, `parse_func_tracer_opts()`, `parse_graph_tracer_opts()`, `parse_sort_key()`, and `opt_list_avail_functions()`. Latency/profile helpers include `make_histogram()`, `display_histogram()`, `prepare_func_latency()`, `start_func_latency()`, `stop_func_latency()`, `cleanup_func_latency()`, `prepare_func_profile()`, `parse_func_duration()`, `add_func_duration()`, `cmp_profile_data()`, and `print_profile_result()`. BPF latency integration is selected through `perf_ftrace__latency_*_bpf()` when available and requested.

## Control Flow
`cmd_ftrace()` initializes filter lists, installs signal handlers, checks CAP_PERFMON or CAP_SYS_ADMIN/root capability, verifies ftrace support by probing `set_ftrace_pid`, loads `ftrace.tracer` config, chooses the `trace`, `latency`, or `profile` option table, and parses target/workload options. If no target or workload is supplied, it defaults to system-wide tracing. It validates target constraints, creates an evlist and maps, optionally prepares a workload, and dispatches to the selected command function.

`__cmd_ftrace()` creates a per-run trace instance under `tracing/instances/perf-ftrace-XXXXXX`, resets files/options, clears the trace buffer, writes filters/options, selects `current_tracer`, opens `trace_pipe` nonblocking, prints trace headers, enables tracing immediately or after the requested delay, starts the workload, polls trace_pipe until a signal marks `done`, disables tracing, drains remaining output, and removes the trace instance.

`__cmd_latency()` prepares ftrace function_graph or BPF latency measurement, allocates histogram buckets, starts tracing, runs the workload, parses function_graph duration lines into buckets with `make_histogram()`, optionally reads BPF buckets, and prints a histogram plus aggregate stats. `__cmd_profile()` forces function_graph with tail comments, parses every duration line into a hashmap keyed by function name, sorts by total/avg/max/count/name, prints results, frees profile entries, and removes the trace instance.

## State and Persistence Behavior
Global state includes `workload_exec_errno`, `done`, `latency_stats`, and `tracing_instance`. Command state lives in `struct perf_ftrace`, which carries tracer selection, target, evlist, filter lists, graph/function options, latency bucket settings, BPF flag, and profile hashmap. Trace configuration is written into a temporary tracefs instance and should be removed at exit; the command also resets common ftrace files and options before each run. Output is streamed to stdout or pager; no perf.data is written.

## Dependencies and Integration Points
Depends on Linux tracing filesystem APIs via `api/fs/tracing_path.h`, perf target/evlist/thread/cpumap utilities, capability helpers, stat helpers, strfilter, hashmap, parse-sublevel-options, units parsing, and optional BPF skeleton support. It integrates with the kernel's `function` and `function_graph` tracers, tracefs option files, CPU masks, `set_ftrace_pid`, function filters, graph filters, trace_pipe, and `available_filter_functions`.

## Risks and Edge Cases
This snapshot contains duplicated lines and an extra brace in local helper code (`strncpy(tracing_instance, ...)`, duplicated buffer-reset comment, and a stray `}` after `parse_filter_func()`), which are compile-time risk signals in this source copy. Runtime risks include tracefs option availability varying by kernel; some resets intentionally ignore errors for older files; `exit_tracing_instance()` only removes the instance directory and logs on failure; signal-driven `done` state also handles workload exec failures; and ftrace text parsing assumes function_graph output format and `" us"` duration units. `__write_tracing_file()` duplicates `val` with `strdup()` and then writes `val_copy[size] = '\n'`, which relies on the NUL terminator slot as spare capacity and is easy to misread.

Latency event-pair mode requires BPF, while function latency can use function_graph. CPU masks and PID filters are mutually shaped by `target__has_cpu()`. Buffer size parsing enforces at least 1 KiB. Profile mode stores dynamically allocated function-name keys and data in a hashmap that must be freed after printing.

## Test Signals
Test `perf ftrace trace`, legacy no-subcommand invocation, `latency`, and `profile` with PID, TID, CPU, all-CPU, workload, and delayed-start targets. Verify function filters, notrace filters, graph filters, graph options (`depth`, `thresh`, `args`, `retval`, `retaddr`, `tail`, `verbose`, `noirqs`, `nosleep-time`), function options (`call-graph`, `irq-info`), buffer sizes, list-functions filtering, profile sort keys, latency bucket/min/max validation, BPF and non-BPF paths, cleanup of trace instances after errors, and workload exec error reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/builtin-ftrace.c -->
