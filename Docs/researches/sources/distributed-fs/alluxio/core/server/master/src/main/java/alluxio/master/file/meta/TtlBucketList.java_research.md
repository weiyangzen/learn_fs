# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/TtlBucketList.java

## Purpose
`TtlBucketList` manages the sorted set of non-empty `TtlBucket` instances for inode TTL processing. It maps inode expiration times into checker intervals, supports polling expired intervals, and persists enough checkpoint state to rebuild the list after restart.

## Important APIs, types, and functions
The constructor takes a `ReadOnlyInodeStore`. `insert(Inode)` and `insert(Inode, int)` place valid-TTL inodes into interval buckets. `remove(InodeView)` removes an inode from its current bucket. `pollExpiredBuckets(long)` atomically removes and returns all buckets whose start time is no later than `time - interval`. `getNumBuckets()` and `getNumInodes()` expose accounting. As a `Checkpointed` implementation, it returns `CheckpointName.TTL_BUCKET_LIST`, writes inode ids as a `CheckpointType.LONGS` checkpoint, and restores by reloading inodes from the inode store.

## Control flow
Insertion skips `Constants.NO_TTL`, looks for an existing containing bucket using `floor`, and creates a new bucket at `(ttlEnd / interval) * interval` or exactly `ttlEndTimeMs` when interval is zero. If another thread concurrently adds the same bucket, insertion retries. After adding the inode, insertion verifies the bucket still exists in the skip-list; if the TTL checker polled it concurrently, insertion repeats so the inode is not missed. Polling repeatedly removes the first bucket while it is expired.

## State and persistence behavior
The durable checkpoint contains only inode ids, not bucket start times or retry counts. Restore clears the set, reads ids until EOF, reloads each inode from `mInodeStore`, and calls `insert`, which recomputes buckets from current inode metadata. Retry counts are therefore reset to defaults across checkpoint restore. Missing inode ids are logged as errors and skipped.

## Dependencies and integration points
This class depends on `TtlBucket`, `ReadOnlyInodeStore`, checkpoint streams, checkpoint names/types, and inode metadata. It is consumed by TTL checker code that polls expired buckets and processes `TtlBucket.getInodeExpiries()`.

## Risks
The `loadInode` helper uses `orElseGet(null)`, which is suspicious because `Optional.orElseGet` expects a supplier; if compiled in this source state it should be reviewed. Checkpoint restore drops remaining retry counts. `getBucketContaining` has subtle boundary logic around exact interval-end timestamps and zero interval. Empty buckets are not removed by `remove`, so callers may leave zero-size buckets unless the checker polls them.

## Test signals
Tests should exercise insert/remove across boundaries, exact end-time behavior, zero interval behavior, concurrent insert-versus-poll races, checkpoint write/restore with deleted inodes, retry-count restore expectations, and accounting for empty buckets after removals.
