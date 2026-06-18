<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go -->
# sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go

## Purpose

This test file exercises the utility worker pools under success, failure, and mismatched worker/job counts.

## Important APIs, Types, and Functions

`queueJob` implements `RJob` and injects an error when `before == 1500`. `TestQueueWorkerPool1` and `TestQueueWorkerPool2` validate ordered result channels and stopping on job error. `TestWorkerPool1` through `TestWorkerPool5` validate unordered worker-pool completion and first-error delivery.

## Control Flow

Queue tests enqueue many jobs and consume `Waiter` channels in index order. Worker pool tests enqueue sleeping jobs, close the queue through `Waiter`, and inspect the first receive from the returned error channel and `Err`.

## State and Persistence Behavior

All state is in memory. The tests rely on sleeps to allow concurrent jobs to overlap and expose first-error behavior.

## Dependencies and Integration Points

The tests use `testify/require`, `time`, and formatted errors. They document expected API behavior for callers: `Waiter` both closes and waits for `WorkerPool`, while `QueueWorkerPool.Waiter` only exposes result channels.

## Risks and Test Signals

The tests are concurrency-sensitive and would benefit from race-detector execution. They do not assert that all goroutines exit after early errors or that blocked `Put` calls are impossible under error conditions.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/contrib/nydusify/pkg/utils/worker_test.go -->
