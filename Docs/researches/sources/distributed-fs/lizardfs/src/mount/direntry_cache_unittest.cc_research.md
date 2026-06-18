# sources/distributed-fs/lizardfs/src/mount/direntry_cache_unittest.cc

## Purpose
`direntry_cache_unittest.cc` contains GoogleTest coverage for `DirEntryCache` ordering and update behavior.

## Important APIs, Types, And Functions
- `DirEntryCacheIntrospect` derives from `DirEntryCache` and exposes begin/end iterators for lookup, index, and inode containers.
- `TEST(DirEntryCache, Basic)` verifies insertion, overwrite, credential separation, index ordering, lookup ordering, and inode multiset lookup.
- `TEST(DirEntryCache, Repetitions)` exercises repeated insertion of the same name/index followed by oldest removal.
- `TEST(DirEntryCache, RandomOrder)` verifies updates when readdir entries arrive in nonsequential index/name order.

## Control Flow
Tests create dummy `Attributes`, insert vectors of `DirectoryEntry` under specific contexts and parent inodes, then compare intrusive-container traversal against expected tuples. `Basic` also checks that inode lookup returns entries with expected attribute bytes.

## State And Persistence
All state is in-memory test cache state. No filesystem or persistent resources are used.

## Dependencies And Integration Points
It depends on GoogleTest, `mount/direntry_cache.h`, `LizardClient::Context`, and `DirectoryEntry` constructors.

## Risks
- Tests do not cover expiration, locking, invalidation, stale inserts, or parent/inode invalidation paths.
- `Repetitions` has no assertions beyond not crashing.
- No tests exercise credential-specific lookup misses.

## Test Signals
These tests are strong signals for intrusive set ordering and overwrite correctness. Coverage should be extended around timeout and invalidation behavior for confidence in cache consistency.
