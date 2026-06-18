<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h

## Purpose

Defines the `powernv_throttle` tracepoint used by the PowerNV cpufreq driver to report chip-level throttling and unthrottling events.

## APIs, Types, And Functions

The `TRACE_EVENT(powernv_throttle)` prototype accepts chip id, reason string, and Pmax value. It records `chip_id`, a dynamic string `reason`, and `pmax`, then formats them for tracing. `TRACE_SYSTEM` is set to `power`, and `TRACE_INCLUDE_FILE` points back to `powernv-trace`.

## Control Flow

The header is included with `CREATE_TRACE_POINTS` by `powernv-cpufreq.c`, generating tracepoint definitions. Runtime calls occur from `powernv_cpufreq_throttle_check()` when Pmax capping state changes.

## State And Persistence

The header stores no state. Trace buffers hold emitted events according to ftrace/perf configuration.

## Dependencies And Integration Points

Depends on Linux tracepoint infrastructure and must keep the include guard plus `trace/define_trace.h` outside the guard as required by trace event headers.

## Risks And Test Signals

The main risk is trace-header misuse causing duplicate or missing trace definitions. Test signals include a build with `CREATE_TRACE_POINTS`, visibility of `power:powernv_throttle`, and emitted events containing the chip id, reason, and Pmax during OCC/PMSR throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h -->
