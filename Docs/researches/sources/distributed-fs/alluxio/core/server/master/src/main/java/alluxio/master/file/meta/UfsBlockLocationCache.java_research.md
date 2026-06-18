# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsBlockLocationCache.java

## Purpose
`UfsBlockLocationCache` abstracts caching for under-file-system block locations. It lets file block metadata lookups reuse UFS locality information keyed by Alluxio block id.

## Important APIs, types, and functions
`get(long)` returns cached locations or null. `get(long, AlluxioURI, long)` returns cached locations or loads them from UFS for a file URI and block offset, caching only successful results. `invalidate(long)` removes a cached mapping. `Factory.create(MountTable)` instantiates `LazyUfsBlockLocationCache`.

## Control flow
The interface defines read-through cache behavior: a plain `get` is non-loading, while the overloaded `get` can consult the UFS through the mount table. Failed UFS lookup returns null and should not populate cache state.

## State and persistence behavior
No state is persisted through this interface. Implementations cache location lists in memory and can discard them on invalidation or restart.

## Dependencies and integration points
The abstraction depends on `AlluxioURI`, `MountTable`, and the `LazyUfsBlockLocationCache` implementation. It integrates with file block info generation where UFS locations are merged with Alluxio worker locations for clients and web UI display.

## Risks
The null-on-miss contract is easy to misuse; callers must distinguish no cached entry, UFS lookup failure, and valid empty location lists. Cached UFS locality can become stale after external UFS changes unless invalidation is wired correctly.

## Test signals
Tests should cover non-loading misses, load success and load failure, invalidation, repeated lookup caching, mount table resolution errors, and empty-location results.
