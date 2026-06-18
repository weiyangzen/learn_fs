# sources/distributed-fs/ceph-client/drivers/ufs/core/ufs_trace.h

## Purpose

`ufs_trace.h` defines tracepoints for UFS core observability: clock gating/scaling, auto background operations, profiling, PM transitions, SCSI command lifecycle, UIC commands, UPIU payloads, and exception events.

## Important APIs, Types, and Functions

Trace events include `ufshcd_clk_gating`, `ufshcd_clk_scaling`, `ufshcd_auto_bkops_state`, profiling events, `ufshcd_system_suspend/resume`, runtime and WL PM events, `ufshcd_init`, `ufshcd_command`, `ufshcd_uic_command`, `ufshcd_upiu`, and `ufshcd_exception_event`. String mapping macros define symbolic output for link states, power modes, clock states, command phases, and TSF types.

## Control Flow

The header uses standard Linux tracepoint macros. When included with `CREATE_TRACE_POINTS` in `ufshcd.c`, it emits tracepoint definitions; other includes get declarations. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this header.

## State and Persistence Behavior

Tracepoints do not persist state. They snapshot selected runtime fields into ring buffers when enabled.

## Dependencies and Integration Points

It depends on Linux tracing, UFS enums from `<ufs/ufs.h>`, and local trace enums from `ufs_trace_types.h`. It integrates UFS driver internals with ftrace/perf/tracefs tooling.

## Risks and Test Signals

Risks include trace ABI field changes, unsafe pointers in trace payloads, string mapping drift, and payload copying of UPIU headers/TSFs with wrong sizes. Test signals include enabling each tracepoint, decoding symbolic fields, command lifecycle correlation, PM profiling durations, and trace generation builds.
