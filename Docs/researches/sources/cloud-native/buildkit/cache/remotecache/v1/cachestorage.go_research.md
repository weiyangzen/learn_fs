# sources/cloud-native/buildkit/cache/remotecache/v1/cachestorage.go

## Purpose

This file converts in-memory `CacheChains` into immutable solver cache key and result storage for imported remote caches. It lets the solver query remote cache keys, links, result IDs, and lazily load remote worker refs.

## Important APIs, Types, and Functions

- `NewCacheKeyStorage` computes item IDs, walks cache-chain leaves, and returns `solver.CacheKeyStorage` plus `solver.CacheResultStorage`.
- `addItemToStorage` recursively registers items, outgoing links, and result-to-key reverse indexes.
- `cacheKeyStorage` implements existence, walking, result lookup, link walking, backlinks, and result-to-key lookup.
- `cacheResultStorage` implements immutable result loading from remote descriptors.
- `LoadWithParents` materializes a selected result and any parent/sub-remote results needed by solver callers.
- `LoadRemotes` returns raw remote descriptors, optionally filtered by compression.
- `remoteID` creates a non-stable ID by hashing the sequence of remote descriptor digests.

## Control Flow and State

`NewCacheKeyStorage` computes deterministic item IDs in the cache graph and registers every leaf recursively. `addItemToStorage` uses `byItem` as both a deduplication table and recursion-loop sentinel. For each parent link, it records an outgoing link from the source item to the target item using normalized link data. For each result, it derives a remote result ID and records which cache key IDs provide that result.

The key storage is read-only: mutation methods such as `AddResult`, `Release`, and `AddLink` are no-ops because imported caches are immutable. Link walking maps solver link requests through the internal `nlink` key, including the output-key digest form. Result storage loads remotes by asking the worker to convert `solver.Remote` descriptors into worker refs. On partial failure in `LoadWithParents`, already loaded refs are released.

All state is in-memory. Persisted cache state remains in the remote backend that supplied descriptors and providers.

## Dependencies and Integration Points

The storage implements BuildKit solver cache interfaces and depends on worker `FromRemote`, BuildKit session groups, compression filtering, and the `CacheChains` item graph from `chains.go`. Remote cache importers call it after parsing a backend-specific manifest.

## Risks and Edge Cases

`remoteID` is explicitly not stable, so it must not be used as a persisted identifier. `Load` assumes `byResultID` returns a non-nil item and would panic if called with an unknown result ID; callers typically check existence first, but this is a sharp edge. `Walk` map iteration order is nondeterministic. `LoadRemotes` compression filtering is best effort and can return nil rather than an error when no matching remote exists. Add/release mutation methods silently do nothing, which is correct for imports but easy to misunderstand in generic cache code.

## Test Signals

There are no direct tests for `cachestorage.go` in this subset. It is indirectly exercised by v1 parse/marshal tests and all cache importer integrations that produce solver cache managers.
