# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.h

## Purpose
`common.h` defines the shared RTLA data model and APIs used by osnoise, hwnoise, timerlat, top, hist, and action handling modes.

## Important APIs, Types, and Functions
`struct osnoise_context` tracks original/current tracefs osnoise settings for restoration. `struct hist_params` stores output shape flags and bucket sizing. `struct common_params` holds shared CLI state: CPU sets, trace events, buffers, timing, stop thresholds, scheduler/cgroup controls, workload choices, output formatting, action lists, and timerlat userspace parameters. `struct osnoise_tool` combines tool ops, trace instance, context, runtime data, params, start time, and auxiliary record/auto-analysis tools. `struct tool_ops` is the polymorphic command interface used by `run_tool()`.

## Control Flow and Integration
Mode modules supply a `tool_ops` table; `common.c` calls parse/init/apply/enable/main/print/analyze/free through that table. The `for_each_monitored_cpu` macro uses `common_params` CPU masks and global `nr_cpus`. Inline `should_continue_tracing()` checks threshold action state.

## State and Persistence
The header describes all persistent tracefs settings that must be saved/restored and all runtime parameters that can produce external effects such as trace files, cgroup moves, scheduler changes, and workload threads.

## Dependencies and Integration Points
It includes `actions.h`, `timerlat_u.h`, `trace.h`, and `utils.h`, so it sits at the center of RTLA's local helper stack and external tracefs/libtraceevent integration.

## Risks and Edge Cases
Large structs are shared mutable state across modules; initialization relies on zeroed allocations and sentinel constants used by `osnoise.c`. `for_each_monitored_cpu` treats a NULL `cpus` string as all CPUs even when `monitored_cpus` contents are not initialized, which is intentional but must be preserved. Adding fields requires updating parsers, cleanup, and restore paths.

## Test Signals
Compile all RTLA modes after struct changes, run mode parsers, validate CPU mask iteration, and check save/restore behavior for all `osnoise_context` fields under partial configuration.
