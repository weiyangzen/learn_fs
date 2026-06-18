# sources/distributed-fs/seaweedfs/weed/filer/leveldb2/leveldb2_store_test.go

## Purpose

`leveldb2_store_test.go` validates basic filer behavior on the sharded LevelDB2 store. It mirrors the single-LevelDB smoke tests while initializing two database partitions.

## Important APIs, Types, and Functions

The tests call `LevelDB2Store.initialize`, `filer.NewFiler`, `SetStore`, `CreateEntry`, `FindEntry`, and `ListDirectoryEntries`.

## Control Flow

`TestCreateAndFind` creates a nested file through the filer, verifies it can be found, lists the containing directory, and verifies the root listing contains one top-level child. `TestEmptyRoot` ensures listing root in a fresh store returns no entries and no error.

## State and Persistence Behavior

Temp directories isolate the two LevelDB partition folders per test. The tests exercise partition selection indirectly through path hashing but do not assert which partition is used.

## Dependencies and Integration Points

The file depends on SeaweedFS filer behavior and local LevelDB storage. It verifies that LevelDB2 satisfies the same basic contract as LevelDB.

## Risks and Edge Cases

Coverage is shallow: no delete, KV, partition distribution, read-only mode, db-count migration, or hash collision behavior is tested. Assertions focus on counts and path identity.

## Test Signals

The key signals are successful nested create/find, correct one-entry listings for parent and root, and empty-root behavior with a two-partition store.
