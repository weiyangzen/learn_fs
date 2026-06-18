<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache.h -->
# sources/distributed-fs/lizardfs/src/common/lru_cache.h

## Purpose
Defines a generic time- and capacity-bounded cache over one or more key fields, with optional hash/tree map and optional internal locking. The source was read completely for this report.

## Important APIs, Types, And Functions
`LruCacheOption`, `LruCache`, `get`, `cleanup`, `erase`, range `erase`, `clear`, and atomic counters `cacheHit/cacheExpired/cacheMiss/maxTime_ms` are the public contract.

## Control Flow
`get` checks for an unexpired key, releases the mutex before obtaining missing values, inserts new values, and performs bounded cleanup of expired or over-capacity oldest entries. A set keyed by timestamp and key-pointer tracks eviction order.

## State And Persistence Behavior
Runtime state is key-to-(timestamp,value) map plus time-to-key-pointer set. No persistence. Reentrant mode serializes internal mutation with a mutex.

## Dependencies And Integration Points
Depends on tuple hashing, `massert`, and `time_utils`. Used for memoized metadata/status computations and similar hot paths.

## Risks And Edge Cases
LRU naming is approximate: hits do not refresh timestamps, so eviction is insertion-time/expiry based. Concurrent misses can compute duplicate values; races return the just-computed value without updating the cache.

## Test Signals
`lru_cache_unittest.cc` covers memoization, erase, expiry, capacity behavior, and optional multithreaded access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/common/lru_cache.h -->
