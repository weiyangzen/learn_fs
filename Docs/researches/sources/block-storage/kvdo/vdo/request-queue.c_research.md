# File Research: sources/block-storage/kvdo/vdo/request-queue.c

Implements a UDS request-processing worker queue over two lock-free funnel queues.

Architecture:
- `struct uds_request_queue` owns a Linux wait queue, processor callback, main queue, retry queue, worker thread, lifecycle flags, and an atomic dormant flag.
- Retry/requeued requests generally have priority over normal requests, but the file explicitly documents a race where a producer can enqueue retry then normal and have them processed in reverse order.

Worker behavior:
- `poll_queues()` checks retry queue first, then main queue.
- `dequeue_request()` returns a request, shutdown, or “must wait”.
- `request_queue_worker()` alternates between timed waiting and dormant indefinite waiting.
- Batch size feedback adjusts wait timeout:
  - small batches increase timeout,
  - large batches decrease timeout,
  - very long timeout switches to dormant mode.
- Dormant mode relies on enqueue-side wakeups and memory ordering around funnel-queue insertion and `dormant`.

Lifecycle:
- `make_uds_request_queue()` allocates the queue, creates both funnel queues, starts the worker thread, and publishes the queue after a memory barrier.
- `uds_request_queue_enqueue()` places the request on retry or main queue based on `request->requeued`, then wakes the worker if dormant or if `request->unbatched`.
- `uds_request_queue_finish()` marks the queue dead with ordering barriers, wakes and joins the worker, drains any remaining queued requests, and frees resources.

Concurrency notes:
- The code relies on funnel-queue barriers, explicit `smp_mb()`, `smp_wmb()`, and `smp_rmb()` to ensure shutdown and sleep/wakeup visibility.
- Shutdown still processes requests fully enqueued before `alive` is cleared.
