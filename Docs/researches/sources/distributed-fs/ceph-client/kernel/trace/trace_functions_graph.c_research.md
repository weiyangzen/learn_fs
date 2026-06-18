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
