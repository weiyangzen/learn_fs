# sources/cloud-native/nydus/service/src/blob_cache.rs

## Purpose
`blob_cache.rs` manages RAFS metadata and data blob cache configuration for the service block-device paths. It converts API blob cache entries into scoped metadata/data blob objects, validates local paths and cache settings, loads RAFSv6 bootstrap metadata, and exposes async read/fetch wrappers around metadata files and data blob cache objects.

## Important APIs, Types, And Functions
`generate_blob_key(domain_id, blob_id)` scopes blobs as `domain/blob` unless the domain is empty. `MetaBlobConfig` stores bootstrap id/path/config, referenced data blobs, extra RAFS blob info, and TARFS mode. `DataBlobConfig` stores `BlobInfo`, config, scoped id, and reference count. `BlobConfig` wraps either config type. `BlobCacheMgr` provides `add_blob_entry()`, `add_blob_list()`, `remove_blob_entry()`, and `get_config()`. Runtime access wrappers are `MetaBlob::new()/blocks()/async_read()` and `DataBlob::new()/async_fetch()/async_read()`.

## Control Flow
Adding a meta blob validates the API entry, canonicalizes `metadata_path`, validates fscache/filecache work dirs, converts to `ConfigV2`, and marks blobs accessible. `add_meta_object()` loads `RafsSuper`, rejects RAFSv5, creates the meta config, adds it to the locked state, then adds each referenced data blob and associates it with the meta config. Data blobs are reference-counted; duplicate metadata blobs are rejected. Removal can delete an entire domain or one meta/data object, decrementing referenced data blob counts.

## State, Persistence, And Dependencies
`BlobCacheMgr` state is an in-memory `Mutex<HashMap<String, BlobConfig>>`. Persistent data remains in bootstrap/blob files and the cache backend; `DataBlob::async_fetch()` delegates persistence/population to `BlobObject::fetch_range_uncompressed()`. `MetaBlob` and `DataBlob` wrap `tokio_uring::fs::File` for async reads, and `DataBlob::new()` duplicates the underlying blob object fd.

## Integration Points
The manager consumes `nydus_api` cache entries, loads `nydus_rafs` metadata, creates caches through `nydus_storage::factory::BLOB_FACTORY`, and feeds `BlockDevice`. TARFS and mapped block addresses are taken from RAFS superblock extra info.

## Risks
`BlobCacheState::try_add()` increments duplicate data ref counts but does not update config fields, so callers rely on identical scoped blob configuration. `add_meta_object()` partially mutates state and performs rollback only for data-add failure after meta insertion. `DataBlob::async_fetch()` uses `spawn_blocking`, so heavy misses can consume blocking pool capacity. The id splitter `/` is forbidden in domain/blob ids for meta entries.

## Test Signals
Tests cover key generation, entry parsing, invalid ids and metadata paths, add/remove/reference behavior across domains, metadata async reads, fd getters, zero-length fetch, and data fetch/read with fixture blobs. They exercise localfs/filecache/fscache-style config paths but not remote backend failure modes.
