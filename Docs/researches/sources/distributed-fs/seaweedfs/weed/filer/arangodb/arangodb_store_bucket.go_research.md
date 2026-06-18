# sources/distributed-fs/seaweedfs/weed/filer/arangodb/arangodb_store_bucket.go

## Purpose
This file implements `filer.BucketAware` behavior for the ArangoDB filer store, allowing bucket creation and deletion to create or drop the corresponding ArangoDB collection.

## Important APIs, Types, and Functions
- Compile-time interface assertion `var _ filer.BucketAware = (*ArangodbStore)(nil)`.
- `OnBucketCreation` ensures a bucket collection with a 10-second context timeout.
- `OnBucketDeletion` ensures/opens the collection, removes it, and deletes it from the in-memory cache.
- `CanDropWholeBucket` returns true.

## Control Flow and State
Bucket creation delegates to `ensureBucket`, which creates the collection and indexes if absent. Bucket deletion obtains the collection, removes it unless already missing, and updates `store.buckets` under lock.

## State and Persistence Behavior
Persistent state is the ArangoDB collection per bucket. Dropping a bucket deletes the entire collection and therefore all metadata for that bucket.

## Dependencies and Integration Points
It uses ArangoDB driver errors, `context.WithTimeout`, SeaweedFS `BucketAware`, and helper cache/index management from `helpers.go`.

## Risks and Edge Cases
- `OnBucketDeletion` calls `ensureBucket`, which can create a missing collection immediately before deleting it.
- Errors are logged but not returned, so callers cannot react to bucket collection failures.
- Bucket name to collection name transformation must stay consistent between creation, deletion, and path extraction.

## Test Signals
Tests should verify collection creation, deletion, cache invalidation, idempotent deletion, and behavior when ArangoDB returns not found. No local tests are listed.
