# sources/distributed-fs/seaweedfs/weed/filer/leveldb3/leveldb3_store_bucket.go

## Purpose

`leveldb3_store_bucket.go` provides the bucket lifecycle hooks for `LevelDB3Store`, making it explicitly implement SeaweedFS's `filer.BucketAware` interface.

## Important APIs, Types, and Functions

The file declares the interface assertion and implements `OnBucketCreation`, `OnBucketDeletion`, and `CanDropWholeBucket`.

## Control Flow

Bucket creation calls `createDB(bucket)` to ensure the per-bucket LevelDB is opened. Bucket deletion closes the DB if present, then removes the bucket directory from the store root. `CanDropWholeBucket` returns true, advertising that the store can cheaply delete all metadata for a bucket as a unit.

## State and Persistence Behavior

Creation opens or creates a persistent LevelDB folder named after the bucket. Deletion removes that folder recursively. The default `_main` DB is unaffected.

## Dependencies and Integration Points

The hooks are called by higher-level bucket lifecycle code through `filer.BucketAware`. They depend on `leveldb3_store.go` map locking and DB loading/closing behavior.

## Risks and Edge Cases

The deletion path guards only against an empty bucket string; bucket names with path separators or unexpected characters rely on upstream validation. `RemoveAll` is irreversible at the filesystem level. Errors from `createDB` in `OnBucketCreation` are ignored because the interface has no return value.

## Test Signals

Tests should verify interface implementation, DB map changes on create/delete, on-disk directory removal, empty bucket no-op behavior, and upstream validation of bucket names.
