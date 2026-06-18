# sources/distributed-fs/ceph-client/drivers/mmc/host/mmc_hsq.c

## Purpose

`mmc_hsq.c` implements MMC host software queue support using the MMC CQE interface. It allows hosts without hardware command queueing to accept tagged CQE requests and pump them serially to normal `mmc_host_ops->request` or `request_atomic`, with a small adjustable queue depth.

## Important APIs, Types, And Functions

- `mmc_hsq_retry_handler()` retries a request in process context after `request_atomic()` reports `-EBUSY`.
- `mmc_hsq_modify_threshold()` changes `mmc->hsq_depth` from normal depth 2 to performance depth 5 when it observes two queued 4 KiB write requests.
- `mmc_hsq_pump_requests()` selects `next_tag`, sets `hsq->mrq`, decrements queue count, and submits to the underlying host.
- `mmc_hsq_update_next_tag()` advances the linked tag queue or invalidates head/tail when empty.
- `mmc_hsq_finalize_request()` is exported for host drivers to complete the active software-queued request; it validates the active request, clears the slot, calls `mmc_cqe_request_done()`, and pumps the next request.
- CQE callbacks implement recovery halt/resume, queueing, post_req forwarding, wait-for-idle, enable, and disable.
- `mmc_hsq_init()` allocates slots, assigns `mmc->cqe_ops`, stores `cqe_private`, initializes tags, work, spinlock, and wait queue.
- `mmc_hsq_suspend()`/`mmc_hsq_resume()` disable and enable the queue for PM.

## Control Flow And State

The CQE core calls `mmc_hsq_request()` with a tagged request. The driver stores it in `slot[tag]`, links the tag at the queue tail using `tag_slot`, increments `qcnt`, and tries to pump. Pumping is serialized by `hsq->mrq`: only one request is submitted to the hardware host at a time. On completion the host driver calls `mmc_hsq_finalize_request()`, which clears the active slot, completes to the CQE core, clears `hsq->mrq`, advances `next_tag`, wakes waiters if idle, and pumps the next queued request unless recovery is halted.

Recovery state is controlled by `recovery_halt`. While set, new CQE queueing returns `-EBUSY`, pumping stops, and wait-for-idle reports `-EBUSY`. Disable waits up to 500 ms for idle before setting `enabled = false`.

## Dependencies And Integration Points

The file depends on MMC card/host core and `mmc_hsq.h`. Host drivers integrate by embedding `struct mmc_hsq`, calling `mmc_hsq_init()`, exposing CQE support to the core, and calling `mmc_hsq_finalize_request()` when their underlying request completes. It also forwards `post_req` to underlying `mmc->ops->post_req` when available.

## Risks And Edge Cases

- `mmc_hsq_pump_requests()` assumes `next_tag` indexes a valid queued slot whenever `qcnt` is nonzero; tag linking bugs would dereference an invalid slot.
- The performance-depth heuristic is very specific to two queued 4 KiB writes and may not generalize.
- `request_atomic()` fallback schedules work only for `-EBUSY`; other errors are warned but left for the host driver to handle.
- Disable timeout only warns and returns without forcibly clearing enabled state if the queue cannot stop.
- The queue serializes hardware execution despite accepting CQE-style tags, so it improves software queueing but not true parallel command execution.

## Test Signals

Tests should cover CQE enable/disable, queueing multiple tagged requests, tag order preservation, finalize of the active request, reject/fallback when disabled or recovery halted, retry work on `request_atomic == -EBUSY`, wait-for-idle wakeups, suspend/resume, post_req forwarding, and depth changes under repeated 4 KiB writes.
