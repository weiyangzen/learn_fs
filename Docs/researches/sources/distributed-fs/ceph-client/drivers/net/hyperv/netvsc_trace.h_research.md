# sources/distributed-fs/ceph-client/drivers/net/hyperv/netvsc_trace.h

Purpose: Declares ftrace trace events for Hyper-V netvsc RNDIS and NVSP control/data messages. It gives operators symbolic visibility into RNDIS request/response types, NVSP message types, packet queue IDs, and send-buffer section use without adding ad hoc logging to hot paths.

Important APIs, types, and functions: `TRACE_SYSTEM netvsc` names the trace namespace. `TRACE_DEFINE_ENUM()` exports RNDIS and NVSP constants so traces can print stable symbolic values. `show_rndis_type()` and `show_nvsp_type()` map message numeric types to readable labels. `DECLARE_EVENT_CLASS(rndis_msg_class)` defines common fields for RNDIS send/receive events: netdev name, queue, request ID, message type, and length. `DEFINE_EVENT()` instantiates `rndis_send` and `rndis_recv`. `TRACE_EVENT(nvsp_send)`, `TRACE_EVENT(nvsp_send_pkt)`, and `TRACE_EVENT(nvsp_recv)` record NVSP message types, subchannel IDs, channel type, and send-buffer section metadata.

Control flow: Driver call sites pass `struct net_device`, optional `struct vmbus_channel`, and RNDIS/NVSP message pointers to generated `trace_*` helpers. The trace fast-assign blocks snapshot the device name and selected header fields into the tracing ring buffer, and `TP_printk` formats them for userspace tracing tools.

State and persistence behavior: The header does not own device state. Trace records persist only as long as the tracing backend retains them. The generated event format is a user-visible diagnostic ABI, so field names and meanings should be treated conservatively.

Dependencies and integration points: It depends on Linux tracepoint infrastructure and on `hyperv_net.h` types such as `struct rndis_message`, `struct nvsp_message`, `struct nvsp_1_message_send_rndis_packet`, and `struct vmbus_channel`. `TRACE_INCLUDE_PATH ../../drivers/net/hyperv` directs `<trace/define_trace.h>` to this header when compiled from the generated trace file context.

Risks and edge cases: The RNDIS event class reads `msg->msg.init_req.req_id` for all RNDIS messages, relying on request ID placement being common across request/response shapes; packet or indication messages may print a field that is meaningful only for control messages. Trace fast-assign code must not dereference invalid message buffers, so call sites must validate or only trace trusted in-kernel constructed messages. Symbol tables need updates when new NVSP/RNDIS message types are added.

Test signals: Build-test with `CREATE_TRACE_POINTS` in `netvsc_trace.c`; enable each trace event through tracefs; exercise RNDIS init/query/set, NVSP init/subchannel/RSS, and packet send paths; verify event format files expose the expected fields and symbolic names.
