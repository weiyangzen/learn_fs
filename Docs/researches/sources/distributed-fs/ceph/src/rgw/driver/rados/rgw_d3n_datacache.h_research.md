# sources/distributed-fs/ceph/src/rgw/driver/rados/rgw_d3n_datacache.h

## Purpose

Declares the D3N RGW data-cache structures and the `D3nRGWDataCache<T>` wrapper that overrides RADOS object-iteration reads to consult the local file cache. It is both the cache object's public contract and the template hook that changes RGW read behavior when the D3N backend is selected.

## Important APIs, Types, and Functions

`D3nChunkDataInfo` describes one cached chunk: Ceph context, size, access time, address, digest oid, completion flag, and LRU links. `D3nCacheAioWriteRequest` owns a pending file write (`oid`, copied data buffer, file descriptor, `aiocb`, back-pointer to `D3nDataCache`, and context). `D3nDataCache` declares cache maps, outstanding write tracking, locks, capacity counters, cache path, `get()`, `put()`, sync and async write helpers, completion callback, eviction functions, `init()`, and inline LRU list operations. `D3nRGWDataCache<T>` derives from an RGW RADOS implementation and overrides `get_obj_iterate_cb()` while leaving `init_rados()` as a pass-through.

## Control Flow and Data Flow

The template `get_obj_iterate_cb()` preserves the normal head-object flow: it applies the atomic test, serves inline head data from `astate->data` when possible, and otherwise schedules a normal librados read. For non-head objects, it builds a librados read op and obtains a RADOS ref. It bypasses cache population when the read is not from offset zero, when logical size differs from accounted size, or when compression/encryption attrs are present. If the read is cacheable, it calls `d->rgwrados->d3n_data_cache->get(oid, len)`. A hit schedules `rgw::Aio::d3n_cache_op()` so data is read from the local cache file; a miss schedules a normal librados read, after which `get_obj_data::flush()` can populate the cache.

## State and Persistence Behavior

The header declares in-memory cache ownership and intrusive LRU list state. `D3nDataCache` owns `D3nChunkDataInfo` entries and deletes them through eviction/destruction. `D3nCacheAioWriteRequest` owns allocated write buffers and the `aiocb`. File persistence is implemented in the `.cc` file; the header exposes `cache_location` so AIO read code can locate digest-named files.

## Dependencies and Integration Points

The header depends on `rgw_rados.h`, curl headers indirectly used by RGW, POSIX signal/unistd headers, Ceph context and LRU helpers, `rgw_common.h`, and `rgw_d3n_cacherequest.h`. It integrates with `get_obj_data`, `RGWObjState`, `rgw_get_rados_ref()`, `librados::ObjectReadOperation`, `rgw::Aio::librados_op()`, `rgw::Aio::d3n_cache_op()`, and object attrs `RGW_ATTR_COMPRESSION` and `RGW_ATTR_CRYPT_MODE`. `rgw_sal.cc` instantiates `D3nRGWDataCache<RGWRados>` for the `"d3n"` store path.

## Risks and Edge Cases

`get_obj_iterate_cb()` dereferences `astate` in the non-head path to inspect attrs and sizes, so callers must supply valid object state. Cacheability is intentionally narrow: only full, offset-zero, uncompressed, unencrypted non-head chunks are eligible. The cache hit path trusts `D3nDataCache::get()` to validate local file presence and length, but not content integrity. The inline LRU helpers are not internally synchronized and must be called under the correct lock. `D3nChunkDataInfo::dump()` and `D3nDataCache::add_io()` are declared here but not implemented in the paired `.cc`, indicating either dead declarations or implementations elsewhere; they should be checked during build/link changes. `D3nCacheAioWriteRequest` destructor assumes `cb` is non-null and resets `cb->aio_buf`, so partially constructed request cleanup is fragile.

## Test Signals

Read-path tests should cover head-object inline data, head-object RADOS fallback, non-head cache miss and later population, non-head cache hit through `d3n_cache_op`, bypass for partial reads, size/accounted-size mismatch, compression attrs, encryption attrs, RADOS ref failures, `flush()` errors after cache reads, and ordering through AIO ids based on logical object offset. Cache-structure tests should validate LRU head/tail operations, destructor eviction, async request cleanup, and build/link coverage for declared helper methods.
