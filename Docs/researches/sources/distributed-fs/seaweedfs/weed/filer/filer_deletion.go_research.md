<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go -->
# sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go

## Purpose
Runs asynchronous deletion of volume file IDs and retries transient failures with bounded exponential backoff.

## Important APIs and Types
`DeletionRetryItem`, `retryHeap`, and `DeletionRetryQueue` implement retry state. Constants define max attempts, delays, polling intervals, and batch sizes. Key methods are `AddOrUpdate`, `RequeueForRetry`, `GetReadyItems`, `Remove`, `Size`, `loopProcessingDeletion`, `processDeletionBatch`, `deleteFilesAndClassify`, `classifyDeletionOutcome`, `loopProcessingDeletionRetry`, `processRetryBatch`, `DeleteChunks`, `doDeleteChunks`, and `deleteChunksIfNotNew`.

## Control Flow and State
`NewFiler` starts `loopProcessingDeletion`. The loop consumes file IDs from an unbounded queue every 1123 ms, deduplicates batches, deletes through volume lookup, classifies each file ID, and adds retryable or missing-result failures to `DeletionRetryQueue`. A separate retry loop polls ready items every minute and requeues retryable failures until `MaxRetryAttempts` is exceeded.

## Persistence Behavior
Retry state is explicitly in-memory only and lost on filer restart. The durable metadata deletion has usually already occurred; this file handles eventual volume garbage cleanup. Manifest chunks are resolved before enqueuing data chunks plus manifest chunk IDs.

## Dependencies and Integration Points
Uses master volume lookup, `operation.DeleteFileIdsWithLookupVolumeId`, volume server delete results, storage deleted errors, filer config rules (`DisableChunkDeletion`), and chunk manifest resolution.

## Risks
In-memory retry queue can lose cleanup work after restart. Retryable classification is string-pattern based and brittle. `DeleteChunksNotRecursive` does not resolve manifests. Failed manifest resolution logs but still enqueues the manifest ID. Very large deletion batches can produce operational load.

## Test Signals
`filer_deletion_test.go` covers queue ordering, backoff, overflow protection, max attempts, retryable string matching, and duplicate file IDs. It does not mock volume server deletion classification in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/seaweedfs/weed/filer/filer_deletion.go -->
