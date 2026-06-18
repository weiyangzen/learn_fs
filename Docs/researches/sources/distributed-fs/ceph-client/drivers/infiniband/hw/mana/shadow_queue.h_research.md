# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mana/shadow_queue.h

## Purpose
`shadow_queue.h` provides a small software ring used to remember posted UD/GSI work requests until hardware completions can be converted into RDMA work completions.

## Important APIs, Types, And Functions
`struct shadow_wqe_header` stores opcode, error code, posted WQE size, and `wr_id`. `ud_rq_shadow_wqe` adds receive byte length and source QPN; `ud_sq_shadow_wqe` is send-only. `struct shadow_queue` tracks unmasked producer, consumer, and next-to-complete indexes plus length, stride, and buffer. Inline helpers create/destroy the buffer, check full/empty, get producer/consumer/next-to-complete entries, and advance indexes.

## Control Flow
Post-send/recv writes the producer entry and advances `prod_idx`. CQE handling updates the next-to-complete entry and advances `next_to_complete_idx`. CQ polling consumes completed entries from `cons_idx` up to `next_to_complete_idx`.

## State And Persistence
The queue is memory-only state embedded in `mana_ib_qp`. Indexes are intentionally unmasked and wrap only by integer overflow; element access masks via modulo `length`. No state persists beyond QP lifetime.

## Dependencies And Integration Points
It uses `kvmalloc_array()`/`kvfree()` and is consumed by `wr.c`, `cq.c`, and `qp.c` for kernel UD/GSI completions.

## Risks
`create_shadow_queue()` initializes buffer, length, and stride but does not explicitly zero indexes, relying on the containing QP being zero-initialized by RDMA core. A zero `length` would make modulo invalid; callers must pass nonzero WR counts. There is no locking inside helpers; CQ locks and post serialization must provide safety.

## Test Signals
Test full/empty boundaries, index wrap behavior, create failure, zero length rejection by callers, producer/complete/consumer ordering, and concurrent post versus poll synchronization through the CQ/QP paths.
