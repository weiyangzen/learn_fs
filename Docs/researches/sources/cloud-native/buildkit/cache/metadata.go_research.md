# sources/cloud-native/buildkit/cache/metadata.go

## Purpose

`metadata.go` adapts the generic Bolt-backed metadata store from `cache/metadata` into cache-specific `RefMetadata` and internal `cacheMetadata` operations. It defines all cache metadata keys, public metadata methods, search helpers, chain/blobchain indexes, queued setters, typed getters, image ref tracking, usage tracking, and external metadata access.

## Important APIs, Types, and Functions

- Constants define persisted keys such as `snapshot.size`, `cache.equalMutable`, `cache.cachePolicy`, `snapshot.committed`, parent keys, diff/chain/blob keys, image refs, deletion marker, blob size, media type, and URLs.
- `MetadataStore` exposes `Search`; `RefMetadata` exposes the public metadata API included in `Ref`.
- `cacheManager.Search`, `search`, `getMetadata`, `searchBlobchain`, and `searchChain` bridge manager locking with metadata store lookups.
- `cacheMetadata` wraps `*metadata.StorageItem` and provides typed cache operations.
- Setters and queued setters include `queueDescription`, `queueCommitted`, `queueSnapshotID`, `queueDiffID`, `queueChainID`, `queueBlobChainID`, `queueBlob`, `queueBlobOnly`, `queueDeleted`, parent setters, `queueSize`, `queueBlobSize`, and cache policy operations.
- Generic helpers include `queueValue`, `setValue`, `SetString`, `ClearValueAndIndex`, `GetString`, `GetStringSlice`, `getTime`, `getBool`, `getInt64`, `appendStringSlice`, and `updateLastUsed`.

## Control Flow

Public searches acquire the manager lock and call metadata store `Search`. The manager-level `search` converts storage items to cache metadata, prefers already cached storage items through `getMetadata`, warns when an index points to missing metadata, and filters records marked deleted.

Metadata updates use two patterns. Immediate setters call `StorageItem.Update` through `setValue` or `setTime`. Queued setters add Bolt-bucket operations to the storage item queue and require a later `commitMetadata`. This batching is used when creating refs so related parent/blob/chain/commit fields become persistent together.

Usage updates increment the cached usage count and last-used timestamp in one transaction. String-slice appends deduplicate new values against existing values and skip writes when nothing changes.

## State and Persistence Behavior

The file defines the durable schema for cache records. Chain indexes (`chainid:`) and blobchain indexes (`blobchainid:`) are stored as metadata value indexes and are used by `GetByBlob` to reuse existing records. Snapshot ID falls back to record ID for older BuildKit metadata. Deletion is a persisted boolean so startup or prune can complete cleanup after a crash. Last-used state is updated when refs release and no other last-used-triggering ref remains.

## Dependencies and Integration Points

This wrapper depends on the `cache/metadata` package for storage, Bolt transactions for low-level operations, BuildKit client usage record types, OCI digests, and BuildKit logging. Public `RefMetadata` methods are consumed by external cache users and refs. Internal metadata is heavily consumed by `manager.go`, `refs.go`, and remote descriptor generation.

## Risks and Edge Cases

- `initializeMetadata` in `manager.go` skips initialization if `CreatedAt` is already set, so missing or corrupt creation timestamps can affect whether parent metadata is refreshed.
- `ClearValueAndIndex` must manually clear old index entries; stale indexes can otherwise return missing or wrong records.
- Typed getters silently return zero values on unmarshal errors, which favors resilience but can hide metadata corruption.
- `appendStringSlice` deduplicates through a map, so appended order is not deterministic.
- Public and internal getters share the same underlying storage item, so callers must respect manager/record locking expectations where applicable.

## Test Signals

`manager_test.go` indirectly validates these keys and indexes through blob reuse, chain/blobchain equality, lazy commit recovery, disk usage, prune, image/non-distributable metadata, and last-used pruning. The lower-level store behavior is covered by `cache/metadata/metadata_test.go`.
