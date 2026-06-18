# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_qp.c

Implements ERDMA QP state transitions and kernel post-send/post-recv paths, including iWARP LLP close/drop, RoCEv2 modify/reset/error behavior, QP refs, SQE/RQE construction, doorbells, inline/SGL handling, and reflush scheduling.

Important functions include `erdma_qp_llp_close`, `erdma_get_ibqp`, `erdma_modify_qp_state_iwarp`, `erdma_modify_qp_state_rocev2`, `erdma_qp_get`, `erdma_qp_put`, `erdma_modify_qp_state_to_rts`, `erdma_modify_qp_state_to_stop`, `modify_qp_cmd_rocev2`, `erdma_reset_qp`, `erdma_post_send`, `erdma_push_one_sqe`, `fill_inline_data`, `fill_sgl`, `kick_sq_db`, `erdma_post_recv`, and `erdma_post_recv_one`.

iWARP RTS transition validates LLP/MPA attrs, reads socket addresses and TCP sequence numbers, builds a modify-QP command, adjusts passive-side send sequence for MPA reply, and stores ORD/IRD/CC. Stop/error transitions post modify commands, drop CM state, and schedule reflush. RoCEv2 modify posts attr-mask commands and updates cached state/qkey/destination/AV. Posting send locks the QP, checks SQ space, formats opcode-specific SQEs, updates WR ID tables, advances PI, and rings SQ DB. Posting recv writes zero-or-one-SGE RQEs and rings RQ DB.

Persistent state includes protocol state, CC, ORD/IRD, CEP pointer, kref/safe-free completion, SQ/RQ indices, WR ID tables, queue buffers, DB records, flags, and delayed reflush work. Dependencies include CM, verbs, CMDQ modify opcodes, CQ cleanup, RDMA WR formats, TCP socket state, AH data, MR data, and device reflush workqueue.

Risks include dense WQE formatting, WQEBB count/offset corruption, RQ full checks not visible in this file, atomic/RDMA read SGE assumptions, CM/QP teardown races, and inline data bounds. Test signals include all send opcodes, inline sends, SQ full handling, post-recv validation, QP reset CQE cleanup, iWARP active/passive RTS, RoCEv2 state changes, and destroy during flushing.
