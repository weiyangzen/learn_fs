# sources/cloud-native/nydus/storage/src/cache/dedup/mod.rs

## Purpose
`dedup/mod.rs` implements the in-process content-addressable storage manager used by file cache entries when the `dedup` feature is enabled. It converts blob/chunk metadata into stable chunk keys, records ready chunks in `CasDb`, copies matching chunks from existing cache files into new cache files, maintains an open-file cache, and garbage-collects stale database records.

## Important APIs, Types, And Functions
`CasError` wraps IO, rusqlite, and r2d2 errors. `CasMgr` owns a `CasDb` and an `RwLock<HashMap<String, Arc<File>>>` of open source files. A global `CAS_MGR` singleton can be installed and retrieved with `set_singleton` and `get_singleton`. `dedup_chunk` is the reuse path: compute chunk key, look up `(path, offset)`, open/cache the source file, copy bytes with `copy_file_range`, and report success/failure. `record_chunk` canonicalizes a cache file path and records a chunk key/path/offset through `record_chunk_raw`. `chunk_key` combines the blob digest algorithm name with the chunk digest, skipping default/empty digests. `gc` removes database and fd-cache entries for source files that no longer exist.

## Control Flow
When a cache miss is about to fetch from backend, `FileCacheEntry` may call `CasMgr::dedup_chunk`. If a matching chunk key exists, the manager finds a source blob file, opens it on demand or reuses an `Arc<File>`, validates that cached file metadata still exists, and copies `chunk.uncompressed_size()` bytes from the recorded offset to the destination chunk’s uncompressed offset. After successful cache persistence, `FileCacheEntry` calls `record_chunk`, which writes the blob path and chunk key mapping to SQLite. On drop of a dedup-enabled `FileCacheEntry`, `gc` scans all database blob paths and removes missing ones.

## State And Persistence Behavior
Persistent dedup metadata is in the SQLite database managed by `CasDb`; process-local state is the singleton and open source-file cache. Paths are canonicalized before recording in normal `record_chunk`, but `record_chunk_raw` accepts caller-provided paths for tests or lower-level use. Stale paths are cleaned lazily when `dedup_chunk` notices missing metadata or during `gc`.

## Dependencies And Integration Points
The module depends on `CasDb`, `BlobInfo`, `BlobChunkInfo`, `RafsDigest`, `copy_file_range`, and standard file/open/path synchronization primitives. It integrates with `cachedfile.rs` behind the `dedup` feature for pre-backend copy reuse and post-persist recording.

## Risks And Edge Cases
Dedup silently returns false on most lookup/open/copy failures so the caller can fall back to backend reads. This is operationally resilient but can hide persistent CAS issues unless logs are monitored. The global singleton is simple and process-wide; replacing it while readers exist could change behavior across mounts. `chunk_key` ignores default digests, so chunks without real digests are never deduplicated. `dedup_chunk` treats `metadata().is_err()` on a cached open file as stale and deletes DB rows for that path. `record_chunk` requires path canonicalization, so recording fails if the cache file path is not yet visible.

## Test Signals
Tests cover error formatting/conversions, manager creation and singleton access, empty and valid chunk-key generation, raw recording, successful copy-based dedup, failure for empty digest and nonexistent source, record no-op for empty key, garbage collection for missing files, and preserving records for existing files.
