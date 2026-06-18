<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h

## Purpose
`queue.h` defines the MMC block queue data structures and helper prototypes shared between `queue.c` and the MMC block implementation. It is the typed contract for blk-mq private request state, queue state, driver operations, and issue classification.

## Important APIs, Types, And Functions
The header defines `enum mmc_issued`, `enum mmc_issue_type`, `enum mmc_drv_op`, `struct mmc_blk_request`, `struct mmc_queue_req`, and `struct mmc_queue`. Inline helpers convert between `struct request` and `struct mmc_queue_req`, compute total in-flight request count with `mmc_tot_in_flight()`, and compute CQE queue count with `mmc_cqe_qcnt()`. It declares queue lifecycle, scatterlist mapping, CQE busy/recovery notification, and issue-type classification functions.

## Control Flow
The header itself has only inline conversion and counter helpers. Runtime control flow is implemented by `queue.c` and block code using the structures declared here: blk-mq allocates request PDUs as `struct mmc_queue_req`, block code fills the embedded `struct mmc_blk_request`, and queue code dispatches according to `enum mmc_issue_type`.

## State And Persistence
The persistent queue state includes card/context/tag-set pointers, block queue pointer, in-flight counts, CQE busy flags, recovery state, waiting/completion state, and work items. Per-request state includes command/request data, scatterlist pointer, driver operation type and result, ioctl metadata, retry count, and flags such as `MQRQ_XFER_SINGLE_BLOCK`.

## Dependencies And Integration Points
It depends on Linux block, blk-mq, MMC core, and MMC host headers. It is consumed by `queue.c`, `block.c`, CQE completion/recovery paths, and ioctl/RPMB/boot write-protect paths. The issue-type enum aligns with the in-flight counter array and queue/CQE scheduling policy.

## Risks And Edge Cases
The `in_flight` array size and `enum mmc_issue_type` values must remain synchronized. Request/private-data conversion assumes blk-mq `cmd_size` is set to `sizeof(struct mmc_queue_req)`. New driver operations must update all switch statements in block and queue code. Incorrect use of the inline counters can affect card lifetime management and CQE retuning decisions.

## Test Signals
Compile coverage across queue/block code is critical. Runtime signals include correct request PDU allocation, ioctl and RPMB operations using the expected `drv_op`, in-flight counters returning to zero after requests, CQE queue counts matching dispatched DCMD/async requests, and no type or structure mismatch under blk-mq debug options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.h -->
