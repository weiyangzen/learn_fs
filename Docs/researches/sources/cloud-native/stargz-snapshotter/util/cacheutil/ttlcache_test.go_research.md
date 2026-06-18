<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go -->
# sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go

## Purpose
Validates TTL cache insertion, retrieval, removal, expiration, and reference-gated cleanup.

## Important APIs, Types, And Functions
- Tests include `TestTTLAdd`, `TestTTLGet`, `TestTTLRemove`, `TestTTLRemoveOverwritten`, `TestTTLEviction`, and `TestTTLQuickDone`.
- Use small TTLs and explicit done callbacks to assert visibility and eviction timing.

## Control Flow
Each test creates a cache, adds keys, checks cached vs new values, invokes done callbacks with eviction flags, sleeps/polls across TTL boundaries, and validates whether entries remain accessible.

## State And Persistence
State is in-memory cache maps and timers. No files are touched.

## Dependencies And Integration Points
Directly covers `ttlcache.go`; behavior is relevant wherever entries represent resources needing delayed cleanup.

## Risks And Edge Cases
Timing-based tests can be flaky under heavy load. They do not fully cover concurrent access races.

## Test Signals
Passing shows duplicate add preservation, get success, explicit remove/overwrite behavior, TTL expiration after references drain, and safe quick release.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/util/cacheutil/ttlcache_test.go -->
