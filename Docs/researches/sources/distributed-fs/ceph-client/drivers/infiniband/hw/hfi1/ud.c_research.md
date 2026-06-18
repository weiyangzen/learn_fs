# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/ud.c

## Purpose
`ud.c` implements Unreliable Datagram send construction, local loopback delivery, receive validation, pkey lookup, and CNP response construction for hfi1. It supports both 9B InfiniBand-style and 16B OPA-style headers, including special 16B fabric-management packets for QP0/QP1.

## Important APIs and Functions
Core send APIs are `hfi1_make_ud_req()`, `hfi1_make_ud_req_9B()`, and `hfi1_make_ud_req_16B()`. Receive and utility APIs include `hfi1_ud_rcv()`, `hfi1_lookup_pkey_idx()`, `return_cnp()`, and `return_cnp_16B()`. Internal helpers include `ud_loopback()` for same-port delivery, `hfi1_make_bth_deth()` for BTH/DETH setup, and `opa_smp_check()` for OPA SMP management packet validation.

## Control Flow
`hfi1_make_ud_req()` allocates a tx request, handles flushes, fetches the current WQE, computes the destination header type, and detects local loopback. Loopback bypasses hardware after DMA ordering checks, delivers through `ud_loopback()`, and completes the send. Non-loopback sends populate SGE state, static rate, header fields, SDMA engine, send context, and reset AHG state. The 9B builder creates LRH/BTH/DETH, optional GRH, SL/SC, permissive LID handling, and P_Key insertion. The 16B builder handles management versus regular datagram headers, OPA LIDs, optional multicast GRH, bypass padding, and 16B length-in-flits.

Receive flow extracts pkey, L4 type, permissive-LID status, source QP, and solicited state. It validates packet length, permissive LIDs, qkey, pkeys, and management-packet constraints. It then consumes or reuses an RWQE, ensures the posted buffer can hold the mandatory GRH plus payload, copies a real, synthesized, or skipped GRH, copies payload, and posts `IB_WC_RECV`.

## State, Persistence, and Dependencies
UD send state lives in QP send indices, WQE SGEs, `hfi1_qp_priv` header type/SC/SDE/send context/AHG, and port SL-to-SC mappings. Receive state uses QP receive SGEs and `RVT_R_REUSE_SGE` for oversized packets. Port state includes LID, LMC, pkeys, counters, partition enforcement, and management capability flags. Dependencies include rdmavt QP/CQ helpers, `mad.h`, `trace_ibhdrs.h`, `verbs_txreq.h`, and OPA/IB header helper functions.

## Integration Points
`verbs.c` dispatches UD opcodes to `hfi1_ud_rcv()` and calls `hfi1_make_ud_req()` for send progress. MAD/SMA behavior integrates with management QPs and `hfi1_process_mad()`. P_Key failures integrate with `hfi1_bad_pkey()` and port constraint counters. CNP return paths use PIO send contexts and congestion-processing helpers.

## Risks and Test Signals
Risks include incorrect permissive-LID handling on QP0 versus other QPs, qkey mismatches leaking packets, pkey table corner cases for full/limited management keys, 16B GRH/GID transformation errors, loopback ordering relative to pending DMA, and wrong completion metadata for GSI/SMI pkey indexes. Test signals include UD send/receive with and without immediate data, GSI/SMI MAD traffic, multicast with required GRH, loopback traffic, invalid qkey/pkey/permissive-LID drops, 16B management packets, CNP generation, and counters for `n_pkt_drops`, `n_vl15_dropped`, and `n_loop_pkts`.
