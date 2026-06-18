# sources/distributed-fs/ceph-client/sound/hda/controllers/intel_trace.h

## Purpose
`intel_trace.h` declares tracepoints for Intel HDA controller system and runtime power-management transitions.

## Important APIs, Types, and Functions
It defines trace system `hda_intel`, event class `hda_pm`, and events `azx_suspend`, `azx_resume`, `azx_runtime_suspend`, and `azx_runtime_resume`. Each event records `chip->dev_index`.

## Control Flow
`intel.c` defines `CREATE_TRACE_POINTS` before including this header, generating tracepoint definitions. PM callbacks call the trace events after suspend/resume actions.

## State and Persistence Behavior
No persistent driver state is created. Trace records are transient ftrace/perf data keyed by card index.

## Dependencies and Integration Points
It depends on Linux tracepoint infrastructure and `struct azx`. `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE intel_trace` must match the controller Makefile include path.

## Risks
Tracepoint ABI names are observable by tooling; renaming events can break scripts. Include guard and `define_trace.h` placement must remain in the standard tracepoint pattern.

## Test Signals
Compile with tracing enabled, verify generated trace events under `/sys/kernel/tracing/events/hda_intel/`, and confirm events fire during system and runtime suspend/resume.
