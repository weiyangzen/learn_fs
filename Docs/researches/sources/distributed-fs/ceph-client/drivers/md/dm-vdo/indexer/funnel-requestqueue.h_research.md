# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/funnel-requestqueue.h

## Purpose
`funnel-requestqueue.h` declares the UDS request queue abstraction used to serialize and batch index requests on a worker thread.

## Important APIs, Types, And Functions
- `struct uds_request_queue` is opaque.
- `uds_request_queue_processor_fn` is the callback type invoked for each `struct uds_request`.
- `uds_make_request_queue()` creates a named queue with a processor.
- `uds_request_queue_enqueue()` submits a request.
- `uds_request_queue_finish()` stops the worker, drains remaining work, and frees resources.

## Control Flow And Data Flow
Callers allocate/own `struct uds_request` objects containing the queue link and flags such as `requeued` and `unbatched`. Enqueue transfers the request to the worker queue; the processor callback handles it later on the queue thread.

## State And Persistence Behavior
The interface exposes no persistent metadata. It coordinates transient index-session request state and shutdown.

## Dependencies And Integration Points
The header depends on `indexer.h` for `struct uds_request`. It is used by index-session and index code to build serialized request-processing lanes.

## Risks
- Request objects must remain valid from enqueue until processor callback.
- Finish drains pending work, so callers must not free request state prematurely during shutdown.
- The API does not expose cancellation; shutdown semantics are drain-and-process.

## Test Signals
Tests should verify queue creation failure handling, callback invocation after enqueue, requeued/unbatched behavior through the implementation, and safe finish with empty and non-empty queues.
