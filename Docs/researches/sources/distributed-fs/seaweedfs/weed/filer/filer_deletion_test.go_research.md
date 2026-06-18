<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go

## Purpose
Unit tests the deletion retry queue and retryability classifier.

## Important APIs and Functions
Tests cover `NewDeletionRetryQueue`, `AddOrUpdate`, `GetReadyItems`, `RequeueForRetry`, `calculateBackoff`, `isRetryableError`, heap ordering, max attempts, overflow protection, and duplicate handling.

## Control Flow and State
The tests directly mutate queue internals under lock where needed to force readiness or heap order. They verify that newly added items are not immediately ready, backoff doubles and caps, max attempts are discarded after the final retry, and duplicate adds update the error without incrementing retry count.

## Persistence Behavior
No persistence. The tests exercise the in-memory queue, matching the production limitation documented in `filer_deletion.go`.

## Dependencies and Integration Points
Uses `container/heap`, `time`, and package retry constants. It protects the async deletion loop's failure handling but does not invoke actual volume deletion.

## Risks
Timing assertions allow 100 ms variance and could be sensitive on extremely slow CI. Because tests reach into unexported fields, internal representation changes require test updates.

## Test Signals
Good signal for queue mechanics and retry classifier strings. Missing signal for `processDeletionBatch`, `deleteFilesAndClassify`, manifest deletion, and integration with `fileIdDeletionQueue`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion_test.go -->
