# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FSDirTruncateOp.java

## Purpose
`FSDirTruncateOp` implements file truncation, including validation, lease recovery, snapshot-aware block collection, quota adjustment, edit-log replay, and scheduling block recovery when truncation cuts through the last block.

## Important APIs, Types, And Functions
- `truncate` is the checked operation returning `TruncateResult`.
- `unprotectedTruncate` has replay/public internal and private mutation variants.
- `prepareFileForTruncate` converts a file to under-construction and prepares copy-on-truncate or in-place truncate recovery.
- Helpers include `verifyQuotaForTruncate` and `shouldCopyOnTruncate`.

## Control Flow
The checked path asserts global FS write lock, resolves with `WRITE`, checks write permission, rejects striped files and lazy-persist files, detects an existing identical truncate recovery, recovers the lease, rejects expansion, calls private `unprotectedTruncate` to record snapshot modification and collect blocks beyond the new length, and if truncating inside a block calls `prepareFileForTruncate`. It updates quota deltas, logs `logTruncate`, and returns whether the client must wait for recovery. Replay applies the same truncation, prepares the truncate block from the edit, deletes obsolete old blocks if needed, and removes collected blocks from the block manager.

## State And Persistence Behavior
Truncate changes file length/block list immediately, collects removed blocks, updates mtime, may convert the file to under construction, creates a lease, creates or updates a truncate block with a new generation stamp, updates block maps, and adjusts quotas. Persistence is the truncate edit containing path/client/new length/mtime/truncate block; recovery completion is driven later by block recovery reports.

## Dependencies And Integration Points
It uses `FSNamesystem` global lock and lease recovery, `FSDirectory` write/read locks and quota checks, `BlockManager` block map/generation stamp/recovery APIs, `INodeFile` snapshot-aware block retention, `BlockUnderConstructionFeature`, and `RecoverLeaseOp.TRUNCATE_FILE`.

## Risks And Edge Cases
Truncating on a block boundary returns immediate success; truncating inside a block makes the file under recovery. Copy-on-truncate is mandatory during rolling/unfinished upgrades or when the last block is in the latest snapshot. Replay must match the stored truncate block exactly. Lazy-persist and striped files are unsupported. Duplicate truncate requests with the same target length are treated idempotently.

## Test Signals
Tests should cover equal length idempotence, expansion rejection, striped/lazy-persist rejection, on-boundary vs in-block return values, duplicate truncate under recovery, lease recovery interactions, quota deltas, snapshot last-block copy-on-truncate, rolling upgrade copy behavior, edit-log replay block matching, and block map removal.
