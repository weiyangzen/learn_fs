# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/uc.c

## Purpose
`uc.c` implements Unreliable Connected transport packet construction and receive processing for hfi1. It handles UC SEND and RDMA WRITE work requests, segments them by PMTU, advances QP send state, builds 9B or 16B RUC headers through shared verbs helpers, and processes incoming UC packets without ACK/retry semantics.

## Important APIs and Functions
The exported entry points are `hfi1_make_uc_req(struct rvt_qp *, struct hfi1_pkt_state *)` and `hfi1_uc_rcv(struct hfi1_packet *)`. `hfi1_make_uc_req()` consumes SQ WQEs, handles local invalidation/registration completions, chooses UC opcodes (`UC_OP(SEND_FIRST)`, `SEND_MIDDLE`, `RDMA_WRITE_ONLY_WITH_IMMEDIATE`, etc.), sets immediate data or RETH fields, initializes `ps->s_txreq`, and calls `hfi1_make_ruc_header()`. `hfi1_uc_rcv()` validates headers with `hfi1_ruc_check_hdr()`, handles ECN, checks PSN sequencing with `cmp_psn()`, copies SEND payload into receive WQEs, performs RDMA WRITE rkey checks through `rvt_rkey_ok()`, and reports receive completions through `rvt_recv_cq()`.

## Control Flow
Send flow starts by allocating a verbs tx request. If the QP cannot send but is flushing, it completes pending WQEs with `IB_WC_WR_FLUSH_ERR` when no DMA is pending. Normal flow chooses a header layout from `priv->hdr_type`, fetches the current WQE, initializes SGE cursors, then enters an opcode/state switch. First packets set base state and optional RETH/immediate headers; middle packets reuse remaining length; last packets attach immediate data and advance `s_cur`. The receive flow first drops invalid RUC headers and processes ECN, then compares incoming PSN to `qp->r_psn`. Sequence or opcode errors rewind/clear receive SGEs and drop or restart at a valid first/only opcode. Valid SEND packets consume a receive WQE and post `IB_WC_RECV`; valid RDMA WRITE packets validate access and write to the remote MR, posting `IB_WC_RECV_RDMA_WITH_IMM` only for WRITE_WITH_IMM.

## State, Persistence, and Dependencies
UC state lives in `struct rvt_qp`: `s_cur`, `s_head`, `s_last`, `s_state`, `s_psn`, `s_len`, `s_sge`, `s_wqe`, `r_psn`, `r_state`, `r_sge`, `r_rcv_len`, and `r_aflags`. hfi1-private fields provide header type, SDMA engine, send context, AHG state, and iowait status. The file depends on `hfi.h`, `verbs_txreq.h`, `qp.h`, rdmavt queue/SGL helpers, and common verbs header builders.

## Integration Points
`verbs.c` dispatches UC opcodes to `hfi1_uc_rcv()` and calls `hfi1_make_uc_req()` from the send engine. `verbs_txreq.c` supplies tx request allocation and wait-list behavior. Shared RC/UC helpers provide RUC header building and header validation. CQ completions and MR/rkey checks are delegated to rdmavt.

## Risks and Test Signals
Key risks are off-by-one PSN transitions, incorrect SGE rewind after malformed multi-packet messages, length/padding mismatch between 9B and 16B paths, flushing while DMA is pending, and accepting RDMA writes without proper remote-write permissions. Test signals include UC SEND/WRITE single and multi-packet transfers at PMTU boundaries, immediate-data completions, forced packet loss/reordering with silent drops and no retry, invalid rkey/access drops, flush behavior in error state, and ECN/CNP interactions.
