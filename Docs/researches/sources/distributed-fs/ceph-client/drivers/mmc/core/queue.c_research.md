<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c

## Purpose
`queue.c` bridges MMC block requests to the Linux blk-mq layer. It creates request queues and gendisks, classifies requests for synchronous, direct-command, and asynchronous issue, maps scatterlists, dispatches requests to `mmc_blk_mq_issue_rq()`, handles CQE/HSQ recovery and timeouts, and manages queue suspend/resume/cleanup.

## Important APIs, Types, And Functions
Public functions are `mmc_init_queue()`, `mmc_cleanup_queue()`, `mmc_queue_suspend()`, `mmc_queue_resume()`, `mmc_queue_map_sg()`, `mmc_cqe_check_busy()`, `mmc_cqe_recovery_notifier()`, and `mmc_issue_type()`. Important internals include `mmc_mq_queue_rq()`, `mmc_mq_timed_out()`, `mmc_cqe_timed_out()`, `mmc_mq_recovery_handler()`, `mmc_mq_init_request()`, `mmc_mq_exit_request()`, `mmc_alloc_disk()`, `mmc_queue_setup_discard()`, and `mmc_get_max_segments()`. `mmc_mq_ops` is the blk-mq operation table.

## Control Flow
`mmc_init_queue()` initializes queue state, configures a blk-mq tag set, detects DMA merge capability, allocates tags, then calls `mmc_alloc_disk()` to build queue limits and allocate the disk. `mmc_mq_queue_rq()` rejects removed cards, classifies the request, checks recovery/busy state, applies CQE DCMD and HSQ-depth throttling, marks the queue busy, increments in-flight counts, gets the card for the first outstanding request, starts the blk request, and calls `mmc_blk_mq_issue_rq()`. Failed starts decrement in-flight counts and may put the card. CQE timeouts delegate to host CQE timeout handling and schedule recovery when requested. Recovery work claims the card context, invokes CQE or normal recovery, clears recovery state, finishes HSQ recovery if needed, releases the card, and reruns hardware queues.

## State And Persistence
`struct mmc_queue` stores card pointer, context, tag set, request queue, lock, in-flight counters per issue type, CQE busy flags, busy/recovery/in_recovery booleans, work items, waits, completion fields, and block data pointer. Per-request private data stores the MMC request, commands, data, scatterlist pointer, driver-operation metadata, retries, and flags. Queue limits persist in the block queue: discard/secure erase/write zeroes limits, logical block size, max hardware sectors, max segments, max segment size or virt boundary, timeout, and crypto configuration.

## Dependencies And Integration Points
The file integrates Linux blk-mq, request queues, gendisks, DMA merge boundaries, scatterlists, workqueues, MMC block implementation (`mmc_blk_mq_issue_rq`, completion, recovery), CQE host operations, crypto queue setup, erase/discard capability helpers, and host/card capability fields. The block driver consumes the initialized gendisk and queue, while host drivers affect queue depth, merging, timeouts, and CQE behavior.

## Risks And Edge Cases
Concurrency is guarded by spinlocks, busy flags, workqueues, and in-flight counters; mistakes can stall requests, over-release the card, or run recovery while new work is dispatched. CQE direct commands are limited to one in flight. Synchronous requests get large timeouts because the core cannot abort them through a host API. Queue limits must match host DMA and card capabilities or data corruption/performance regressions can result. Cleanup must cancel recovery and flush completion work after freeing tags to avoid use-after-free. The file contains a trailing whitespace line near `mq->card = card`, but it is harmless behaviorally.

## Test Signals
Signals include successful block device creation, correct queue depths for CQE and non-CQE hosts, discard/secure erase/write zeroes limits, logical block size 512/4096 handling, DMA merge behavior, stable read/write/flush/discard/ioctl dispatch, CQE DCMD throttling, timeout-triggered CQE recovery, HSQ recovery finish, suspend quiescing with no outstanding requests, resume unquiescing, and cleanup under card removal during recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/core/queue.c -->
