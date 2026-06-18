# sources/distributed-fs/juicefs/pkg/meta/redis_batchclone_test.go

## Purpose

`redis_batchclone_test.go` is an integration test suite for Redis `BatchClone` behavior. It verifies that Redis batch cloning handles shared chunk references, mixed file/symlink entries, duplicate names, filesystem space/inode accounting, multi-chunk files, deleted sources, and a known partial-failure mode.

## Important APIs, Types, and Functions

`newTestRedisMeta` creates a Redis metadata engine against `127.0.0.1:6379/<db>`, resets it, initializes the test format, and registers cleanup. `redisSliceRefCount` reads Redis `sliceRef` values directly. Test cases call public metadata APIs such as `Mkdir`, `Mknod`, `NewSlice`, `Write`, `Link`, `Symlink`, `Readdir`, `Lookup`, `ReadLink`, `Unlink`, `StatFS`, and `m.getBase().BatchClone`.

## Control Flow

Each test builds source and destination directories in a fresh Redis DB, creates representative entries, obtains source directory entries through `Readdir`, filters out `.` and `..`, invokes `BatchClone`, and checks cloned count plus Redis-visible side effects. Shared chunk tests hard-link two names to one source inode and require slice ref increments for both cloned files. Mixed tests verify file and symlink cloning. Duplicate-name tests pass a synthetic batch with duplicate destination names and expect one clone. Space accounting waits briefly for `StatFS` deltas to match expected aligned sizes and inode counts. The deleted-source test passes 1001 entries to exercise batching and verifies a source unlinked after listing is skipped. The partial-failure test changes `sliceRef` to the wrong Redis type and documents that a failed clone can still leave a visible destination entry and accounting changes.

## State and Persistence Behavior

Tests use Redis DBs 7, 9, and 11 through 15 and call `Reset`, so they mutate a live local Redis instance. They inspect persistent Redis hashes/lists through the production key helpers. The partial-failure test intentionally corrupts the `sliceRef` key type and expects persisted clone state to remain after failure.

## Dependencies and Integration Points

The suite depends on a local Redis server, the non-`noredis` build, JuiceFS test config/format helpers, and Redis backend implementation in `redis.go`. It is tightly coupled to Redis slice reference semantics and to `BatchClone` aggregation in `baseMeta`.

## Risks and Edge Cases

Tests are integration-style and will fail if Redis is unavailable or if the selected DBs are used concurrently by other tests. `newTestRedisMeta` resets the database, so it must never run against a non-test Redis DB. Directory listing order is not assumed except for counts. The partial-failure test is intentionally a current-behavior test, not a success guarantee; it records a consistency risk that should be revisited if Redis batch clone is made atomic.

## Test Signals

These tests provide strong signals for slice ref accounting, hard-link flattening to independent cloned files, symlink target preservation, duplicate entry filtering, multi-chunk list copying, batch boundaries above 1000 entries, and state after Redis command failures. Missing coverage includes ACL/xattr preservation in batch clone, quota enforcement, case-insensitive destinations, directories being skipped, and concurrent destination conflicts.
