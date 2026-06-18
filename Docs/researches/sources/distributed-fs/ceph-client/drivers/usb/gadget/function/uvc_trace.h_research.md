# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_trace.h

## Purpose

`uvc_trace.h` declares tracepoints for UVC gadget USB request queueing and completion. The events expose request pointer, request length, and the current queued-request count.

## Important APIs, Types, and Functions

`DECLARE_EVENT_CLASS(uvcg_video_req, ...)` defines the shared event payload for `struct usb_request *req` and `u32 queued`. `DEFINE_EVENT()` creates `uvcg_video_complete` and `uvcg_video_queue`. The trace header also sets `TRACE_SYSTEM` to `uvcg` and configures `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` for `define_trace.h`.

## Control Flow

Callers invoke generated functions such as `trace_uvcg_video_queue(req, count)` and `trace_uvcg_video_complete(req, count)`. When tracing is disabled, static-key machinery keeps overhead low. When enabled, the fast assignment copies `req`, `req->length`, and `queued` into the trace record.

## State and Persistence Behavior

The header defines trace event schema, not device state. Event records are transient tracing data controlled by kernel tracing consumers.

## Dependencies and Integration Points

It depends on `linux/tracepoint.h`, USB gadget request definitions, and `trace/define_trace.h`. It integrates with `uvc_video.c` request lifecycle instrumentation and with userspace ftrace/perf tooling.

## Risks and Test Signals

Risks include dereferencing `req->length` after invalid request lifetime if trace calls are moved, mismatched trace include path, and ABI expectations from existing tracing tools. Test signals are enabling the tracepoints during UVC streaming and observing queue/complete counts track `atomic queued`.
