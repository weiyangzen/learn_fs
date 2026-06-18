# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.c

## Purpose
`funnel-requestqueue.c` implements a UDS request queue using funnel queues and a worker thread. It batches request processing with adaptive wait times, prioritizes retry requests over new requests as a hint, and supports dormant sleep/wakeup behavior for idle periods.

## Important APIs, Types, And Functions
- `struct uds_request_queue` contains wait queue, processor callback, main and retry funnel queues, worker thread handle, lifecycle flags, and dormant atomic flag.
- `poll_queues()` checks retry queue before main queue.
- `are_queues_idle()` combines funnel idle checks.
- `dequeue_request()` returns a request, shutdown signal, or sleep indication.
- `wait_for_request()` sleeps either indefinitely in dormant mode or with an hrtimer timeout.
- `request_queue_worker()` processes requests, adapts batching wait time, exits on shutdown, and drains remaining requests.
- Public APIs are `uds_make_request_queue()`, `uds_request_queue_enqueue()`, and `uds_request_queue_finish()`.

## Control Flow And Data Flow
Queue creation allocates the structure, initializes two funnel queues, sets `running`, and creates a named worker thread. Enqueue chooses `retry_queue` if `request->requeued` is set, otherwise `main_queue`, then wakes the worker if the queue is dormant or the request is `unbatched`.

The worker waits for a request, processes it through the caller-supplied `processor`, and tracks batch size. If the previous wait produced too small a batch, it increases the wait time up to `MAXIMUM_WAIT_TIME`, then enters dormant mode. If batches grow too large, it decreases the wait time down to `MINIMUM_WAIT_TIME`. On finish, `running` is cleared with a write barrier, the worker wakes and joins, then remaining queued requests are drained before freeing queue structures.

## State And Persistence Behavior
The queue is transient runtime state. It preserves request objects owned by callers and returns ownership to the processor callback. The `running`, `started`, and `dormant` flags govern worker lifecycle and sleep mode, not persisted state.

## Dependencies And Integration Points
It uses the generic VDO funnel queue plus Linux waitqueue/atomic primitives, UDS thread utilities, logging, and memory allocation. It is created by index session/index code for callback, index, and triage request processing.

## Risks
- Retry-first ordering is not guaranteed because funnel queues can be in transition states.
- Dormant wakeup correctness relies on memory barriers in funnel enqueue and waitqueue sleep preparation.
- `uds_request_queue_finish()` processes remaining requests after shutdown; processors must tolerate finish-time callbacks.
- `wait_event_interruptible*` return values/signals are ignored, which is acceptable only if loop predicates remain authoritative.

## Test Signals
Tests should cover batching adaptation, dormant entry and wakeup, unbatched immediate wakeup, retry queue preference, finish while requests are pending, enqueue/finish races, and processor invocation count/order under concurrent producers.
