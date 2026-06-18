# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace_icc-bwmon.h

## Purpose

`trace_icc-bwmon.h` provides a single tracepoint for Qualcomm interconnect bandwidth monitor updates. It records the monitored node name, measured bandwidth, and computed up/down thresholds.

## Important APIs, Types, and Functions

The `qcom_bwmon_update(const char *name, unsigned int meas_kbps, unsigned int up_kbps, unsigned int down_kbps)` trace event stores a string name and three unsigned bandwidth values. `TRACE_INCLUDE_PATH` is set to the driver-relative qcom path and `TRACE_INCLUDE_FILE` uses the underscore/hyphen file name.

## Control Flow

The bandwidth monitor driver calls the generated trace function whenever it recalculates or applies bandwidth thresholds. The tracepoint copies values into the trace entry and formats them as kilobits per second.

## State and Persistence Behavior

The header has no runtime state beyond trace buffers controlled by the kernel tracing subsystem.

## Dependencies and Integration Points

It depends on `<linux/tracepoint.h>` and the trace event generator. It integrates with the Qualcomm ICC BWMON driver and with ftrace/perf user-space tooling.

## Risks and Edge Cases

The nonstandard include file name `trace_icc-bwmon` and relative include path are easy to break when moving files. Callers should pass stable names during trace assignment.

## Test Signals

Enable the `icc_bwmon/qcom_bwmon_update` trace event, trigger bandwidth threshold updates, and confirm measured/up/down values match the driver's calculations.
