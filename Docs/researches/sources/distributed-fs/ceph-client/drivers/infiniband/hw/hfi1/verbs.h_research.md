# sources/distributed-fs/ceph-client/drivers/infiniband/hw/hfi1/verbs.h

## Purpose
`verbs.h` is the central hfi1 verbs header. It defines OPA/IB header wrappers, QP-private state, packet send state, opcode stats, port/device verbs structures, PSN helpers, TID RDMA accessors, and prototypes shared by RC/UC/UD/TID, QP, MAD, send, receive, and registration code.

## Important APIs and Types
Key types include `struct opa_16b_mgmt`, `struct hfi1_16b_header`, `struct hfi1_opa_header`, `struct hfi1_ahg_info`, `struct hfi1_sdma_header`, `struct hfi1_qp_priv`, `struct hfi1_swqe_priv`, `struct hfi1_ack_priv`, `struct hfi1_pkt_state`, `struct hfi1_opcode_stats`, `struct hfi1_opcode_stats_perctx`, `struct hfi1_ibport`, and `struct hfi1_ibdev`. Important inline helpers are `inc_opstats()`, `to_idev()`, `iowait_to_qp()`, `cmp_psn()`, `mask_psn()`, `delta_psn()`, `wqe_to_tid_req()`, `ack_to_tid_req()`, `__full_flow_psn()`, `full_flow_psn()`, `opa_bth_is_migration()`, and `hfi1_trdma_send_complete()`. It declares all major transport and registration APIs used across the hfi1 verbs subsystem.

## Control Flow
The header supports flow rather than implementing it. Send code fills `hfi1_pkt_state`, transport builders populate `verbs_txreq`/headers, `hfi1_verbs_send()` chooses egress, and completion paths call back into RC/TID helpers. Receive code decodes headers into `hfi1_packet` and dispatches to declared handlers. QP private fields hold send-context, SDMA, iowait, TID RDMA, OPFN, flow, retry, and pending-resource state used across those flows.

## State, Persistence, and Dependencies
`hfi1_qp_priv` is the largest persistent state definition in this subset, including AHG, SDMA engine, send context, receive context, TID timers/lists, OPFN data, TID RDMA parameters, flow state, retry/NACK flags, send/receive TID queues, counters, and read/write segment accounting. `hfi1_ibdev` stores rdmavt device info, wait-list locks, txreq cache, timers, counters, and optional debugfs/fault state. Dependencies include Linux lock/work/timer/slab headers, RDMA core/rdmavt headers, `iowait.h`, `tid_rdma.h`, and `opfn.h`.

## Integration Points
All researched C files include or depend on this header directly or indirectly. `verbs.c` implements many prototypes and uses the structures for registration and TX/RX dispatch. `uc.c`/`ud.c` use PSN/header helpers and `hfi1_pkt_state`. `verbs_txreq.c` uses `hfi1_ibdev`, `hfi1_qp_priv`, and `iowait_to_qp()`. Trace headers inspect these structures for diagnostics.

## Risks and Test Signals
Risks include cross-file ABI drift, cacheline-sensitive structure changes, PSN helper changes breaking wraparound comparisons, TID RDMA state misinterpretation, duplicate or stale prototypes, and changing `HFI1_UVERBS_ABI_VERSION` requirements when userspace ABI changes. Test signals include full driver compile, sparse/lockdep on QP/iowait usage, RC/UC/UD/TID traffic, PSN wrap tests, QP reset/error paths, registration/unregistration, and tracepoint compilation after structure edits.
