# sources/distributed-fs/ceph-client/drivers/infiniband/hw/erdma/erdma_cq.c

Implements ERDMA kernel CQ notification, CQE polling, CQE-to-`ib_wc` translation, UD metadata extraction, and CQE cleanup for QP reset/destroy.

Important functions include `erdma_req_notify_cq`, `erdma_poll_cq`, `erdma_poll_one_cqe`, `erdma_process_ud_cqe`, and `erdma_remove_cqes_of_qp`. Static tables map ERDMA opcodes and hardware statuses to RDMA core opcodes/statuses and vendor errors.

Polling locks the CQ, checks owner bits against CI, advances CI, issues `dma_rmb`, resolves QP by QPN, selects send or receive WR ID table, updates SQ CI for send completions, maps opcode/status, fills immediate or invalidate fields, and returns completed WCs. Notification rings a CQ doorbell with CQN, CI, command serial, arm/solicited bits, and notify index.

Persistent state includes CQ buffer, CI, notify count, command serial, DB record, CQN, and QP WR ID tables. Dependencies include hardware CQE formats, RDMA core CQ APIs, xarray lookup helpers, and CEQ event handling.

Risks include consuming invalid CQEs for missing QPs, opcode table bounds assumptions, CQE compaction preserving owner bits, and receive queue overposting interactions with `erdma_qp.c`. Test signals include completion mapping for all opcodes, notification/missed-event behavior, UD GRH metadata, polling during QP destroy, and CQE cleanup on reset/error.
