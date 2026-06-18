<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h -->
# sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h

## Purpose

`hv_trace_balloon.h` declares the Hyper-V balloon driver tracepoint used to observe guest memory pressure reports and dynamic-memory accounting.

## Important APIs, Types, and Functions

- `TRACE_SYSTEM hyperv` places the event in the Hyper-V trace system.
- `TRACE_EVENT(balloon_status)` records available pages, committed pages, raw `vm_memory_committed()`, pages ballooned, pages hot-added, and pages onlined.
- Generated `trace_balloon_status()` is called by `post_status()` in `hv_balloon.c`.

## Control Flow

The header follows the standard trace-event pattern with a multi-read guard, field declarations, fast assignment, print formatting, `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and an out-of-guard include of `<trace/define_trace.h>`. `hv_balloon.c` defines `CREATE_TRACE_POINTS` before including this header, so the balloon tracepoint is instantiated in the balloon module/object rather than `hv_trace.c`.

## State and Persistence Behavior

The tracepoint owns no balloon state. It snapshots counters passed by `hv_balloon.c` at pressure-report time and leaves buffering, enablement, and persistence to the tracing subsystem.

## Dependencies and Integration Points

This file depends on Linux tracepoint infrastructure and the accounting semantics in `hv_balloon.c`. It is useful with debugfs counters from the balloon driver to correlate host pressure reports with internal counters.

## Risks and Edge Cases

Field units must stay aligned with the caller. `hv_balloon.c` passes page counts before converting the VMBus status message to Hyper-V page units, so trace consumers should interpret values as Linux page counts except where named otherwise. Moving `CREATE_TRACE_POINTS` could cause duplicate or missing tracepoint definitions.

## Test Signals

Enable `hyperv:balloon_status`, trigger periodic pressure reports, balloon-up, unballoon, and hot-add activity, and verify trace records match debugfs `hv-balloon` counters and host status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hv/hv_trace_balloon.h -->
