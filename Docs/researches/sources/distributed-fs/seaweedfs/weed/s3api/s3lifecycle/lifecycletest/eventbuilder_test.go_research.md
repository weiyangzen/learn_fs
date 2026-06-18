# sources/distributed-fs/seaweedfs/weed/s3api/s3lifecycle/lifecycletest/eventbuilder_test.go

Purpose: validates the main lifecycle event fixture builder surface.

Important tests: create/delete/update constructors populate the expected entry sides and default mtimes; nested and directory keys produce filer-style leaf names; shard id matches production `ShardID`. Options set size, mtime, TTL, version id, extended keys, chunks, shard override, old-entry size/chunks/mtime on update, and no-op behavior of old options on create. Later options override earlier ones. `MetaLogClock` tests default/custom step, peek behavior, and concurrent unique timestamps.

Control flow/state: tests option application order and target-entry selection. Clock tests exercise mutex-protected mutable state.

Dependencies/integration: uses filer protobuf chunks, S3 constants, lifecycle shard hashing, and testify.

Risks/gaps: builder tests do not validate every downstream router interpretation, but they ensure fixtures are shaped correctly for those tests. Concurrent clock test requires race detector for full data-race signal, but uniqueness/deadlock is checked normally.

Test signals: broad confidence that test fixtures mirror production event anatomy, especially for directory keys and update old/new separation.
