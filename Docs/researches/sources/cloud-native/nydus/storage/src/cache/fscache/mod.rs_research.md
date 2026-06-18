# sources/cloud-native/nydus/storage/src/cache/fscache/mod.rs

Purpose: implements Linux `FsCacheMgr`, a `BlobCacheMgr` variant that uses a file supplied by the kernel fscache subsystem as the backing data file while reusing `FileCacheEntry` for blob cache behavior. It is Linux-only via the parent module gate and is intended for uncompressed cache mode.

Important APIs and control flow: `FsCacheMgr::new` rejects compressed cache mode, reads fscache work_dir, creates metrics and worker manager, and starts the global factory manager checker. Its cache-entry lookup/insertion mirrors `FileCacheMgr`. `check_stat` scans all entries; after all blobs report ready for the configured number of checks, it stops prefetch workers and marks metrics `data_all_ready`. `FileCacheEntry::new_fs_cache` rejects RAFS v5 without extended blob table and tarfs, requires `BlobInfo::get_fscache_file`, gets data and optional separate-meta readers, loads RAFS metadata through `FileCacheMeta`, creates a non-persistent `IndexedChunkMap`, restores readiness from sparse-file holes, and returns a direct-IO-capable entry.

State and persistence behavior: data is held by the external fscache file rather than a file opened by this module. The chunk map is opened with `persist=false`, so the temporary bitmap file is removed after mapping. `restore_chunk_map` walks the fscache file with `lseek64(..., SEEK_HOLE)` using metadata offsets and marks chunk ranges ready for allocated regions until a hole or file end is reached.

Dependencies and integration points: integrates with `BlobInfo` fscache file handles, `FileCacheMeta`, `BlobStateMap<IndexedChunkMap>`, kernel sparse-file semantics, async prefetch workers, global `BLOB_FACTORY` checker, metrics, backend readers, and optional CAS.

Risks and test signals: correctness depends on kernel `SEEK_HOLE` behavior and metadata offset-to-chunk mapping. It does not support compressed mode, tarfs, v5 no-ext-table, or blobs without blob meta info. A failed hole seek stops recovery and leaves later chunks not ready. Tests construct config, mock backend, a texture-derived ZRan blob info, an fscache file, manager init/get/gc/check/destroy paths.
