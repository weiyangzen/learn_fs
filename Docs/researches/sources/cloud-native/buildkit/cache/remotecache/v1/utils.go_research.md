# sources/cloud-native/buildkit/cache/remotecache/v1/utils.go

## Purpose

This file provides helper logic for deterministic cache config ordering, link key creation, remote chain marshaling, item marshaling, and sub-remote comparison.

## Important APIs, Types, and Functions

- `sortConfig` sorts layers and records and rewrites all index references to their new positions.
- `outputKey` derives per-output cache key digests from a digest and output index.
- `nlink` is the normalized internal link lookup key used by cache storage.
- `marshalState` tracks layers, descriptor providers, chain IDs, records, and item-to-record indexes while marshaling.
- `marshalRemote` converts a `solver.Remote` descriptor chain into `CacheLayer` entries and descriptor providers.
- `marshalItem` recursively emits parent records and the current item's best result.
- `isSubRemote` checks whether one remote's descriptor sequence is a prefix of another.

## Control Flow and State

`sortConfig` first sorts layers by blob digest and parent index, assigns new layer indexes, and rewrites parent indexes. It then sorts records by digest, input count, input group lengths, selectors, and input record digest, assigns new record indexes, rewrites result layer indexes and input link indexes, and sorts inputs within each input group by link index.

`marshalRemote` validates provider availability via `Info` when a provider exists, recursively marshals parent descriptors, registers the last descriptor in the descriptor map, and appends a `CacheLayer` if the descriptor chain ID is new. `marshalItem` uses `recordsByItem` as a recursion sentinel, recursively marshals parents, records input links, marshals the best result if present, and appends the cache record.

State is transient during marshal but determines persisted remote cache config bytes, so determinism matters for digest-addressed exports.

## Dependencies and Integration Points

The helpers depend on solver remotes, OCI digests, containerd error definitions, and the v1 schema types. They are called by `CacheChains.Marshal` and later consumed by cache storage and parser code.

## Risks and Edge Cases

`sortConfig` does not rewrite `ChainedResults.LayerIndexes`, so configs containing chained results could keep stale layer indexes after layer sorting. Record sorting compares input link target digests, not full recursively sorted identity, which may be insufficient for complex ties. `marshalRemote` returns an empty ID if provider info fails with anything other than not-implemented, causing a result to be skipped silently. `marshalItem` drops parents still marked `-1`, which is used to break cycles or incomplete recursion.

## Test Signals

`chains_test.go` exercises simple layer sorting, record sorting, result layer index rewrite, and parse/marshal shape. It does not cover chained result index rewrites, provider `Info` failures, complex record sort ties, or `isSubRemote` directly.
