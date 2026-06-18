# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.cc

## Purpose

Implements the local L1 data-cache backing store for RGW D3N. The cache writes whole RADOS object chunks to files under a configured persistent path, tracks cached chunks in memory, services cache-hit reads through `D3nL1CacheRequest`/AIO integration, and evicts cached files by LRU or random policy when configured capacity is exhausted.

## Important APIs, Types, and Functions

`D3nCacheAioWriteRequest::d3n_libaio_prepare_write_op()` prepares an async file write by opening the digest-named cache file, allocating a copy of the bufferlist data, and filling an `aiocb`. `D3nDataCache::init()` initializes capacity, path, eviction policy, optional startup directory eviction, directory creation/permissions, and libaio tuning. `d3n_io_write()` provides a synchronous file-write path and inserts a cache-map entry. `d3n_libaio_create_write_request()` submits async writes, `d3n_libaio_write_cb()` bridges SIGEV_THREAD completion into the cache object, and `d3n_libaio_write_completion_cb()` records the completed chunk and updates capacity/LRU state. `put()` deduplicates writes, evicts as needed, and starts async population. `get()` validates a cache-map entry against an on-disk file of the requested length and refreshes its LRU position. `random_eviction()` and `lru_eviction()` remove entries and delete backing files.

## Control Flow and Data Flow

Initialization normalizes `rgw_d3n_l1_datacache_persistent_path` to a trailing slash, optionally removes existing directory contents when `rgw_d3n_l1_evict_cache_on_start` is enabled, creates the directory when absent, and maps `rgw_d3n_l1_eviction_policy` to LRU or random. Cache population starts in `put()`: the RADOS object id is hashed with `D3nL1CacheRequest::generate_oid_digest()`, existing cached/outstanding writes are skipped, capacity is checked against `free_data_cache_size - outstanding_write_size + freed_size`, and evictions run until enough room appears. The async write request owns a copied buffer; completion erases the outstanding marker, allocates `D3nChunkDataInfo`, inserts it into `d3n_cache_map`, subtracts bytes from free capacity, subtracts bytes from outstanding size, inserts the chunk at the LRU head, and deletes the request object. Reads call `get()` with the original RADOS oid and requested length; a hit requires an in-memory map entry plus an on-disk file whose `stat()` size exactly matches the requested length.

## State and Persistence Behavior

Durable cache contents are plain files named by digest under `cache_location`. They are persistent across daemon restart only as files; the in-memory index is not rebuilt from disk during `init()`, so old files are either removed at startup when configured or left orphaned until external cleanup. Runtime state includes `d3n_cache_map`, `d3n_outstanding_write_list`, two mutexes, `free_data_cache_size`, `outstanding_write_size`, and the LRU `head`/`tail` chain. The destructor repeatedly calls `lru_eviction()` until no LRU entries remain, deleting known cache files and metadata but not scanning for orphan files.

## Dependencies and Integration Points

This implementation depends on POSIX file APIs (`open`, `fopen`, `fwrite`, `aio_write`, `stat`, `remove`, `posix_fadvise`), C++ filesystem APIs, Ceph config/logging, `bufferlist`, `D3nL1CacheRequest`, and `rgw_d3n_datacache.h`. The cache object is allocated from `RGWRados::init_rados()` when `use_datacache` is set. D3N store selection happens in `rgw_sal.cc` when `rgw_d3n_l1_local_datacache_enabled` is true, the max chunk size equals object stripe size, and Beast async/yield support is enabled. Cache writes are triggered from `get_obj_data::flush()` after RADOS read completion when the result is at most `rgw_get_obj_max_req_size` and no bypass flag was set. Cache reads are dispatched through `rgw::Aio::d3n_cache_op()`.

## Risks and Edge Cases

The async write completion path does not call `aio_error()` or `aio_return()`, so failed or partial async writes may be indexed as successful. `D3nCacheAioWriteRequest` cleanup assumes `cb` is allocated and closes `fd` even when it may be `-1`; early prepare failures can leak or dereference depending on how far initialization progressed. Lock ordering is inconsistent: `get()` takes `d3n_cache_lock` then `d3n_eviction_lock`, while `lru_eviction()` takes `d3n_eviction_lock` then `d3n_cache_lock`, creating a deadlock risk. `random_eviction()` removes map entries without updating the LRU chain, so later LRU operations can see stale pointers after random eviction. Empty-cache `random_eviction()` returns `size_t(-1)`, but `put()` only treats zero as eviction failure. Existing persistent files are not indexed on startup. File paths are digest-derived but still share one flat directory, so very large caches can stress directory operations. There is no checksum validation beyond size match, so stale or corrupted local files can be served if the digest name and length match.

## Test Signals

Tests should cover directory creation and startup eviction, invalid or unwritable cache path handling, LRU and random eviction under capacity pressure, capacity accounting with outstanding writes, duplicate `put()` suppression, cache-hit read only after async completion, stale file size mismatch removal, partial/failed `aio_write()` behavior, concurrent `get()` plus eviction lock ordering, random eviction followed by LRU destruction, restart behavior with orphan persistent files, and integration reads for full uncompressed/unencrypted chunks versus bypassed partial, compressed, or encrypted reads.
