<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc

Purpose: Implements the cached system-object backend, including object cache reads/writes, distributed cache update/invalidation through notify service, chained cache support, and admin-socket cache inspection commands.

Important APIs, types, and functions: `RGWSI_SysObj_Cache_CB` adapts notify callbacks. `do_start()` starts admin socket, core, notify service, and registers callback. Overrides include `remove()`, `read()`, `get_attr()`, `set_attrs()`, `write()`, `write_data()`, and `raw_stat()`. `distribute_cache()` sends `RGWCacheNotifyInfo`. `watch_cb()` applies incoming `UPDATE_OBJ` or `INVALIDATE_OBJ`. Chained cache functions register, unregister, and chain entries. `RGWSI_SysObj_Cache_ASocketHook` and `ASocketHandler` implement `cache list`, `cache inspect`, `cache erase`, and `cache zap`.

Control flow: Reads with offset zero try the object cache first using requested flags for data, obj version, metadata, and xattrs. Cache miss falls through to core read, then caches complete data unless the read probably truncated at `end + 1`. Writes/removes execute the core operation first, then update or invalidate local cache and distribute a notify message. Incoming notifications update or invalidate local cache. Admin socket calls iterate, inspect, erase, or clear cache entries.

State and persistence: In-memory `ObjectCache` stores data, xattrs, metadata, status, and object versions keyed by normalized `pool+namespace+oid`. Persistent metadata remains in RADOS via core operations. Notify control objects carry transient invalidation/update messages. Chained cache entries are invalidated with their source cache entries.

Dependencies and integration points: Depends on `RGWSI_SysObj_Core`, `RGWSI_Notify`, `ObjectCache`, `RGWCacheNotifyInfo`, admin socket framework, and zone params for object normalization when oid is empty. Bucket sync and user services use chained caches through this service.

Risks and test signals: Cache coherency depends on successful notify distribution, but distribution failures are logged and nonfatal after local writes. Partial reads and refresh-version checks affect caching behavior. Tests should cover cache hit/miss, ENOENT negative caching, write/update propagation, remove invalidation, raw/stat xattr filtering, watcher callback decode errors, chained cache invalidation, and admin socket commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.cc -->
