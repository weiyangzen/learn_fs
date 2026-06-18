# sources/distributed-fs/ceph-client/drivers/mmc/core/block.h

## Purpose
Private interface between MMC block request policy and queue/blk-mq support.

## Important APIs, Types, And Functions
- Declares `mmc_blk_mq_issue_rq()`, `mmc_blk_mq_complete()`, `mmc_blk_mq_recovery()`, `mmc_blk_mq_complete_work()`, and `mmc_blk_cqe_recovery()`.
- Forward declares `struct mmc_queue`, `struct request`, `struct work_struct`, and `enum mmc_issued`.

## Control Flow
Queue code calls these functions to issue requests, complete requests, and run recovery work. `block.c` implements the policy.

## State And Persistence
No state is owned by the header. Implementations mutate `mmc_queue`, requests, and card/host state.

## Dependencies And Integration Points
Integrates `block.c` with `queue.c` and Linux blk-mq.

## Risks And Edge Cases
Prototype drift breaks the `mmc_block` build. `enum mmc_issued` must be defined for users that inspect return values.

## Test Signals
Compile `mmc_block-objs := block.o queue.o`; runtime queue dispatch and recovery validate the contract.
