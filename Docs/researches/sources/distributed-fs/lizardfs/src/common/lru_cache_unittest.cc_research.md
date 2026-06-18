<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc -->
# sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc

## Purpose
Exercises the generic cache for memoization, explicit erase, max age, max size, and optional multithreaded operation. The source was read completely for this report.

## Important APIs, Types, And Functions
Defines hash/non-reentrant and tree/reentrant cache typedefs and uses gtest plus `std::async` when available.

## Control Flow
Tests recursively compute Fibonacci through the cache, record calls for erase/expiry/capacity behavior, and concurrently get/erase ranges.

## State And Persistence Behavior
All state is local test cache instances and vectors of observed arguments.

## Dependencies And Integration Points
Depends on `lru_cache.h`, `massert`, gtest, and optional `std::future` support.

## Risks And Edge Cases
Multithreaded test does not wait explicitly in the shown snippet by calling `get` on futures, so failures may rely on future destructor behavior depending on standard/library behavior.

## Test Signals
Passing tests indicate the common cache policies work for expected single-threaded and reentrant use cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache_unittest.cc -->
