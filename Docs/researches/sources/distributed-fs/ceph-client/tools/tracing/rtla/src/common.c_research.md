# sources/distributed-fs/ceph-client/tools/tracing/rtla/src/common.c

## Purpose
`common.c` implements shared RTLA command execution: option parsing for common flags, signal handling, tool initialization/configuration, tracer enablement, workload setup, main-loop execution, threshold/end actions, cleanup, and shared top/hist loops.

## Important APIs, Types, and Functions
Key globals are `trace_inst`, `stop_tracing`, and `nr_cpus`. Important functions include `getopt_auto()`, `common_parse_options()`, `common_apply_config()`, `common_threshold_handler()`, `run_tool()`, `top_main_loop()`, `hist_main_loop()`, `osn_set_stop()`, and `common_usage()`. Signal helpers set `SIGINT` and optional `SIGALRM` to stop trace instances and event iteration.

## Control Flow
`run_tool()` sets `nr_cpus`, calls the mode parser and initializer, stores ops/params, applies config, enables the requested tracer, optionally adjusts scheduling/cgroup placement, creates auxiliary trace instances for trace-output actions, starts userspace timerlat workload threads when requested, enables the tool, installs stop signals, runs the mode main loop, stops user workload, prints stats, performs end actions, detects whether tracing stopped due to thresholds, optionally runs analysis, then frees everything and exits with pass/fail/error status. `top_main_loop()` and `hist_main_loop()` sleep between reads, iterate raw trace events, handle threshold stops, optionally restart tracing when a continue action was configured, and break when userspace workload exits.

## State and Persistence
The file mutates global stop state and may change process affinity, scheduling, cgroup membership, trace instances, trace buffers, event enables, and action output files. Cleanup destroys trace events and tools, action lists, and params.

## Dependencies and Integration Points
It depends on `common.h`, tracefs/libtraceevent wrappers, utilities for CPU parsing, scheduler/cgroup helpers, timerlat userspace dispatcher, and each mode's `tool_ops` implementation.

## Risks and Edge Cases
`run_tool()` exits directly, so callers cannot recover. The `out_trace` path calls `trace_events_destroy(&tool->record->trace, params->events)` even when `tool->record` is NULL in some failure paths; this relies on paths reaching that label only after record creation or on macro/function tolerance elsewhere. Cgroup error handling uses `if (!retval)` as failure, so the helper's return convention must match exactly. Signal handling uses global `trace_inst`, which supports only one active primary tool per process. Threshold continue restarts record/aa instances but assumes prior action side effects completed successfully.

## Test Signals
Exercise common options (`--cpus`, `--duration`, `--event`, filters/triggers via mode parsers, `--priority`, `--house-keeping`, `--cgroup`), signal and duration stop paths, trace-output/end actions, continue-on-threshold behavior, user workload exit, and cleanup after partial initialization failures.
