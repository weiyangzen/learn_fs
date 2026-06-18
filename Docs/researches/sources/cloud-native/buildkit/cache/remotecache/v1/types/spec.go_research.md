# sources/cloud-native/buildkit/cache/remotecache/v1/types/spec.go

## Purpose

This file defines the serialized v1 BuildKit remote cache config schema.

## Important APIs, Types, and Functions

- `CacheConfigMediaTypeV0` is the OCI media type for BuildKit cache config blobs.
- `CacheConfig` contains `Layers` and `Records`.
- `CacheLayer` records blob digest, parent index, and optional annotations.
- `LayerAnnotations` stores media type, uncompressed diff ID, size, and creation time.
- `CacheRecord` stores result layer references, explicit chained results, cache key digest, and input links.
- `CacheResult`, `ChainedResult`, and `CacheInput` encode result and dependency references by index.

## Control Flow and State

There is no executable logic. These types are marshaled by v1 exporters, embedded inline by image exporters, stored in external cache backends, read by importers, and parsed back into solver cache records. Parent indexes in `CacheLayer` use `-1` for roots. `CacheResult.LayerIndex` refers to a top layer whose parents are loaded transitively, while `ChainedResult.LayerIndexes` lists exact layer indexes without following parents.

## Dependencies and Integration Points

The schema depends on OCI digest types and Go `time.Time`. It is consumed by all cache backends in this subset and by `remotecache/import.go` for inline cache handling.

## Risks and Edge Cases

`LayerAnnotations.CreatedAt` lacks `omitempty`, so zero times serialize as the zero timestamp when annotations are present. Index-based references require stable sorting and careful rewrites during marshal. Schema compatibility is important because remote caches may outlive the BuildKit process that produced them.

## Test Signals

`chains_test.go` checks basic `CacheConfig` field shape after marshal. There are no schema-compatibility or golden JSON tests in this subset.
