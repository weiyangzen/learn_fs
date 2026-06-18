<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c

## Purpose

Implements PVRDMA queue-pair lifecycle and work request posting: create/destroy/query/modify QPs, reset queue state, flush CQEs, and translate send/receive WRs into backend WQEs.

## Important APIs, Types, And Functions

Public handlers are `pvrdma_create_qp()`, `pvrdma_destroy_qp()`, `pvrdma_modify_qp()`, `pvrdma_query_qp()`, `pvrdma_post_send()`, and `pvrdma_post_recv()`. Internal helpers cover CQ lock ordering, queue sizing, QP reset, QP free, command destroy, WQE address computation, and fast-reg segment setup.

## Control Flow

Create validates flags, QP type, SRQ support, and port, reserves a QP counter, sets up user umems or kernel queue pages, builds a page directory, posts `PVRDMA_CMD_CREATE_QP`, stores returned qpn/handle based on device version, registers the QP in `dev->qp_tbl`, and returns handles to userspace. Modify validates standard state transitions through `ib_modify_qp_is_ok()`, copies attributes to the PVRDMA command, posts modify, and resets local rings/CQEs if moving to RESET. Query either returns RESET locally or asks the backend.

Send posting requires at least RTS, checks SQ space and SGE counts, validates opcode/type compatibility, fills UD or RC WQE fields, handles fast-reg WRs, writes SGEs, uses a write barrier, advances the producer tail, and rings the QP send doorbell after a successful batch. Receive posting rejects RESET and SRQ-associated QPs, fills RQ WQEs, advances the producer tail, and rings the receive doorbell.

## State And Persistence Behavior

Each QP tracks backend handle, qkey, send/receive rings, optional user umems, page directory, optional SRQ, page counts, state, port, mutex, refcount, and completion. Device-level state tracks active QPs in `qp_tbl` and `num_qps`. Kernel rings are coherent memory; user rings are pinned user memory.

## Dependencies And Integration Points

Integrates RDMA core QP state rules, CQ flushing from `pvrdma_cq.c`, SRQ objects, MR fast-reg page directories, PVRDMA command ABI, page-directory helpers, UAR doorbells, and async event handlers.

## Risks And Edge Cases

The destroy/free paths clear table entries by raw handle while create/event paths often use modulo. `pvrdma_post_send()` checks `qp_type != UD && qp_type != RC && wr->opcode != SEND`, which means unsupported non-UD/RC types could pass if opcode is SEND before later switch rejection; the switch still protects correctness. User QP support requires larger output ABI for QP handle on newer devices. CQ lock ordering by handle prevents deadlock during reset/flush.

## Test Signals

Test QP create for RC/UD/GSI, unsupported types/flags, SRQ and non-SRQ paths, user/kernel rings, device-version handle responses, state-transition validation, RESET flushing, send opcode/type matrix, full SQ/RQ rings, fast-reg WRs, bad AHs, receive on SRQ QPs, query after RESET and active states, and destroy with concurrent events/completions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/vmw_pvrdma/pvrdma_qp.c -->
