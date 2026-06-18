# sources/distributed-fs/ceph-client/drivers/usb/dwc3/trace.h

Purpose: declares the DWC3 trace event classes and concrete events used to inspect role changes, register IO, raw events, control requests, USB requests, gadget commands, endpoint commands, TRBs, and endpoint state.

Important APIs/types/functions: event classes include `dwc3_log_set_prtcap`, `dwc3_log_io`, `dwc3_log_event`, `dwc3_log_ctrl`, `dwc3_log_request`, `dwc3_log_generic_cmd`, `dwc3_log_gadget_ep_cmd`, `dwc3_log_trb`, and `dwc3_log_ep`. Concrete events include `dwc3_set_prtcap`, `dwc3_readl`, `dwc3_writel`, `dwc3_event`, `dwc3_ctrl_req`, `dwc3_alloc_request`, `dwc3_free_request`, `dwc3_ep_queue`, `dwc3_ep_dequeue`, `dwc3_gadget_giveback`, `dwc3_gadget_generic_cmd`, `dwc3_gadget_ep_cmd`, `dwc3_prepare_trb`, `dwc3_complete_trb`, `dwc3_gadget_ep_enable`, and `dwc3_gadget_ep_disable`.

Control flow: each trace call snapshots selected fields into trace ring buffers using `TP_fast_assign`, then formats them with helper decoders from `debug.h` and USB helper decoders. The header ends with `TRACE_INCLUDE_PATH`, `TRACE_INCLUDE_FILE`, and `trace/define_trace.h` integration.

State and persistence: trace entries are transient tracing data, but the event formats form a user-visible diagnostics contract. Captured fields include base address, endpoint name, request pointers, lengths/status, command parameters/status, TRB ring indices, flags, direction, and raw event words.

Dependencies and integration: depends on Linux tracepoint macros, byteorder helpers, `core.h`, and `debug.h`. It is included by normal source files for declarations and by `trace.c` with `CREATE_TRACE_POINTS` for definitions.

Risks: trace format strings dereference DWC3, endpoint, request, and TRB fields, so trace calls must pass live objects. Verbose register IO tracing can be expensive. Format changes can break scripts. Pointer printing and base addresses are useful for debugging but require normal kernel tracing access controls.

Test signals: enabling individual events while running gadget enumeration or transfers should show coherent command, TRB, request, and event sequences. Build failures here usually indicate trace macro misuse or type mismatches.
