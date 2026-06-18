# sources/distributed-fs/ceph/src/rgw/rgw_cache.h

Purpose: declares object cache data structures, flags, cache notification payloads, chained-cache interface, and `ObjectCache`.

Important APIs/types/functions: operation enum values `UPDATE_OBJ` and `INVALIDATE_OBJ`; flags `CACHE_FLAG_DATA`, `XATTRS`, `META`, `MODIFY_XATTRS`, `OBJV`; `ObjectMetaInfo`; `ObjectCacheInfo`; `RGWCacheNotifyInfo`; `RGWChainedCache`; `ObjectCacheEntry`; and `ObjectCache`.

Control flow: declarations expose `get()`, optional-return `get()`, `for_each()`, `put()`, invalidation, context setup, chained-cache registration, and enable/disable. Inline `for_each()` reads under shared lock and filters by enabled/expiry.

State/persistence: structs are buffer-encoded for notifications and test instances. `ObjectCache` live state is an unordered map plus LRU list, counters, expiry, and chained cache registry.

Dependencies/integration: Ceph mutex/time/assert, cls version types, `rgw_common`, bufferlist, and RGW cache entry info. Used by RADOS/object metadata layers to cache object data/xattrs/meta.

Risks: `ObjectCacheInfo::time_added` is not encoded; restored notifications do not carry cache age. `for_each()` expiry condition may be inverted or too restrictive for zero-expiry cases. Chained entries store raw cache pointers and string keys, so unregister ordering matters.

Test signals: encode/decode for cache notification structs, flag merge semantics, `for_each()` with expiry zero/nonzero, chain registration/unregistration, and cache_info generation lifetime.
