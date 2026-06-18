# sources/distributed-fs/lizardfs/src/mount/group_cache.h

## Purpose
`GroupCache` caches sets of primary/secondary Unix groups and maps each set to a compact integer id that can be sent to the master instead of resending the full group vector on every request.

## Important APIs, Types, And Functions
`GroupCache::Groups` aliases the protocol credentials group container. `GroupHash` hashes every group id with `hash_combine()`. `find()` returns `{index, found}` for a group vector. `put()` increments a wrapping id counter below `2^31`, inserts the group vector into a 1024-entry `GenericLruCache`, and returns the id. `findByIndex()` reverse-lookups the group vector by id. `reset()` clears cache and counter. Constants include `kMaxGroupId` and `kDefaultGroupsSize`.

## Control Flow
All public operations take a mutex, making cache operations safe for concurrent FUSE requests. `LizardClient::updateGroups()` uses `find()`/`put()` and sends newly assigned group sets to the master; reconnect handling calls `reset()`.

## State And Persistence
The cache stores group-vector-to-index mappings and a monotonically incremented, wrapping index. It is in-memory only and is reset when the master connection is lost.

## Dependencies And Integration Points
It depends on `GenericLruCache`, `small_vector`, and `cltoma::updateCredentials` protocol definitions. It integrates with request context conversion in `mfs_fuse.cc` and credential registration in `lizard_client.cc`.

## Risks And Test Signals
Risks include id reuse after wraparound, eviction causing master re-registration, reverse lookup misses, and dependence on vector ordering. Test signals should cover repeated group sets, eviction behavior, reset on reconnect, and concurrent access.
