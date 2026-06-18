# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/trace_tid.h

## Purpose
`trace_tid.h` defines the Linux tracepoint surface for hfi1 TID and TID RDMA behavior. It is observability-only code: it does not drive packet handling, but it captures expected receive TID registration/unregistration/invalidation, OPFN negotiation, TID RDMA flow/request state, responder and sender queue state, receive errors, SGE alignment checks, write responder/sender state, TID ACKs, and KDETH eflags errors. It is included through the kernel `TRACE_EVENT` mechanism and finishes with `TRACE_INCLUDE_FILE trace_tid`.

## Important APIs, Types, and Events
The file declares helper decoders `hfi1_trace_get_tid_ctrl()`, `hfi1_trace_get_tid_len()`, and `hfi1_trace_get_tid_idx()` for compact TID entry fields. Important event classes include `hfi1_exp_tid_reg_unreg`, `hfi1_opfn_state_template`, `hfi1_opfn_data_template`, `hfi1_opfn_param_template`, `hfi1_msg_template`, `hfi1_tid_flow_template`, `hfi1_tid_node_template`, `hfi1_tid_entry_template`, `hfi1_responder_info_template`, `hfi1_sender_info_template`, `hfi1_tid_rdma_request_template`, `hfi1_rc_rcv_err_template`, `hfi1_sge_template`, `hfi1_tid_write_rsp_template`, `hfi1_tid_write_sender_template`, `hfi1_tid_ack_template`, and `hfi1_kdeth_eflags_error_template`. Concrete events are named by lifecycle points such as `hfi1_exp_tid_reg`, `hfi1_exp_tid_unreg`, `hfi1_exp_tid_inval`, `hfi1_tid_flow_alloc`, `hfi1_tid_req_rcv_write_data`, `hfi1_tid_write_sender_retry_timeout`, and `hfi1_eflags_err_write`.

## Control Flow
Tracepoint control flow is declarative. Call sites in expected receive and TID RDMA code pass QP, flow, request, node, SGE, or scalar state into the trace macros. The trace classes use `TP_fast_assign` to snapshot state from `struct rvt_qp`, `struct hfi1_qp_priv`, `struct tid_rdma_flow`, and `struct tid_rdma_request`, then format stable strings via shared `*_PRN` macros. The event family is organized so one template covers several state-machine transitions, which makes probe output comparable across allocation, build, receive, retry, timeout, and ACK paths.

## State, Persistence, and Dependencies
The file persists no runtime state of its own. It snapshots live state from QP private fields such as `s_tid_cur`, `r_tid_head`, `flow_state.generation`, `sync_pt`, retry flags, ACK queues, TID offsets, and page-set counts. Dependencies include `linux/tracepoint.h`, `linux/trace_seq.h`, `hfi.h`, and structures from `tid_rdma.h` and `verbs.h` that are reachable through `hfi.h`. The trace helpers are an integration contract: changing TID field encodings or QP private structures must keep these events compiling and meaningful.

## Integration Points
Expected receive code uses `hfi1_exp_tid_reg`, `hfi1_exp_tid_unreg`, `hfi1_put_tid`, and `hfi1_exp_tid_inval`. TID RDMA sender/responder implementation uses the request, flow, responder, sender, write, ACK, and eflags events to diagnose protocol progress. OPFN negotiation code uses the OPFN state/data/param/message events. Debug and performance investigations rely on these event names and field order, so they are part of the driver's diagnostic ABI even though they are not userspace uAPI.

## Risks and Test Signals
Risks are compile-time drift from structure layout changes, dereferencing trace arguments that are invalid at call time, and misleading diagnostics if fields are sampled before or after state updates. Test signals include successful kernel tracepoint compilation, `trace-cmd`/ftrace visibility for the `hfi1_tid` system, expected events during user expected receive setup/clear/invalidation, TID RDMA read/write traffic showing monotonic flow/request progress, and error injection producing receive-error or eflags traces.
