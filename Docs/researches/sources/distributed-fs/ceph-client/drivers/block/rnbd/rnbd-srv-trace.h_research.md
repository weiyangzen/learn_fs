# sources/distributed-fs/ceph-client/drivers/block/rnbd/rnbd-srv-trace.h

## Purpose
Declares tracepoints for the RNBD server: session creation/destruction, I/O processing, session-info negotiation, open messages, and close messages.

## Important APIs, types, and functions
- `DECLARE_EVENT_CLASS(rnbd_srv_link_class)` captures session name and queue depth.
- `DEFINE_LINK_EVENT(create_sess)` and `DEFINE_LINK_EVENT(destroy_sess)` instantiate session lifecycle events.
- `TRACE_EVENT(process_rdma)` captures direction, protocol version, device id, sector, flags, size, priority, RDMA data length, and user header length.
- `TRACE_EVENT(process_msg_sess_info)`, `process_msg_open`, and `process_msg_close` capture admin protocol details.
- `TRACE_DEFINE_ENUM()` and `show_rnbd_access_mode()` make access-mode values readable in trace output.

## Control flow
Server core calls these tracepoints before or during message handling. The trace system records fields using fast assignment macros and formats them through `TP_printk` when read.

## State and persistence behavior
No RNBD state is stored. The events snapshot selected fields at trace time. Strings are copied into trace records through `__string`/`__assign_str`.

## Dependencies and integration points
Includes Linux tracepoint support and relies on forward-declared RNBD/RTRS types plus constants from `rnbd-proto.h`. `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation at this local header.

## Risks and test signals
Trace events dereference message and session fields, so call sites must only pass validated buffers. Test by enabling each event and exercising session connect/disconnect, open, close, I/O, and old-version session info to confirm useful fields and no trace format breakage.
