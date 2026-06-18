# sources/distributed-fs/ceph-client/drivers/soc/qcom/trace-aoss.h

## Purpose

`trace-aoss.h` defines tracepoints for Qualcomm AOSS message transactions. It is a trace header rather than executable driver logic and lets AOSS code record outgoing messages and their completion status.

## Important APIs, Types, and Functions

The header sets `TRACE_SYSTEM` to `qcom_aoss` and declares two `TRACE_EVENT`s: `aoss_send(const char *msg)` and `aoss_send_done(const char *msg, int ret)`. Both store the message string with `__string`; completion also stores an integer result. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation back to this header.

## Control Flow

Including code calls the generated `trace_aoss_send()` before sending a message and `trace_aoss_send_done()` after the operation completes. The trace subsystem expands the macros into static tracepoint definitions where `CREATE_TRACE_POINTS` is set.

## State and Persistence Behavior

No driver state is stored here. Trace records are transient ftrace/perf events controlled by tracing infrastructure and persist only in active trace buffers.

## Dependencies and Integration Points

It depends on `<linux/tracepoint.h>` and the kernel trace event build machinery. Integration is compile-time: the include path and file name must match how the AOSS implementation includes the trace header.

## Risks and Edge Cases

Trace headers are sensitive to include guards, `TRACE_HEADER_MULTI_READ`, and `TRACE_INCLUDE_PATH`; moving the file without updating these macros breaks generated trace code. Message strings must be valid at trace assignment time.

## Test Signals

Build with tracing enabled and ensure trace events appear under `events/qcom_aoss`. Exercise successful and failing AOSS sends and verify printed message/result fields.
