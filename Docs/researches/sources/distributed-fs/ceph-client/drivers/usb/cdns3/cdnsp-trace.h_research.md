# sources/distributed-fs/ceph-client/drivers/usb/cdns3/cdnsp-trace.h

Purpose: defines Linux tracepoints for the Cadence CDNSP gadget-side controller, covering endpoint state, control requests, TRBs, rings, contexts, requests, port status, streams, bounce buffers, and miscellaneous lifecycle messages.

Important APIs/types/functions: declares `TRACE_SYSTEM cdnsp-dev`, `CDNSP_MSG_MAX`, multiple `DECLARE_EVENT_CLASS` blocks, and concrete events such as `cdnsp_tr_drbl`, `cdnsp_handle_event`, `cdnsp_request_enqueue`, `cdnsp_ep_disabled`, `cdnsp_ring_alloc`, `cdnsp_handle_port_status`, and `cdnsp_stream_number`. It depends on CDNSP gadget/debug helpers such as `cdnsp_decode_trb`, `cdnsp_trb_virt_to_dma`, and USB decode helpers.

Control flow: this header has no runtime control flow of its own; compile-time tracepoint macros generate event call sites and formatters. Fast-assign blocks snapshot selected object fields before `TP_printk` decodes them for ftrace consumers.

State and persistence: trace events persist only in kernel tracing buffers. They snapshot DMA addresses, request metadata, ring pointers, stream counters, and context words but do not own controller state.

Dependencies and integration: included by CDNSP gadget implementation files with `CREATE_TRACE_POINTS` in one translation unit. The trailing `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` block is required by the kernel tracepoint build system.

Risks: tracepoint formatters dereference nested objects passed by callers, so call sites must pass valid endpoint, ring, request, context, and state pointers. Large decode strings are bounded by `CDNSP_MSG_MAX`; very detailed TRBs or control requests may be truncated.

Test signals: useful validation comes from enabling ftrace events under the `cdnsp-dev` system during enumeration, endpoint enable/disable, transfer completion, stream setup, and port-status changes; build coverage must ensure the generated trace header compiles exactly once.
