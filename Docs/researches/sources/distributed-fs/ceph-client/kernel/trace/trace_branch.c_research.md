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
