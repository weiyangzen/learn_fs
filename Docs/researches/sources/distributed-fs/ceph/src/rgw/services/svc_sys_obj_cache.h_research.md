<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h

Purpose: Declares the cached sysobj backend and generic chained cache helper.

Important APIs, types, and functions: `RGWSI_SysObj_Cache` derives from `RGWSI_SysObj_Core`, owns notify service pointer, `ObjectCache`, callback, and `ASocketHandler`. It overrides core read/write/stat/attr/remove paths and exposes `chain_cache_entry()`, `register_chained_cache()`, and `unregister_chained_cache()`. `RGWChainedCacheImpl<T>` stores keyed entries with optional expiry, registers with sysobj cache, supports `find()`, `put()`, `chain_cb()`, `invalidate()`, and `invalidate_all()`.

Control flow: Backend methods cache sysobj operations and use notify callbacks for coherency. Chained caches are populated only while the object cache lock can safely invoke chain callbacks, preserving lock ordering.

State and persistence: `ObjectCache` and chained cache maps are in memory. Entries may expire based on `rgw_cache_expiry_interval`. Persistent system-object state remains in RADOS.

Dependencies and integration points: Depends on `ObjectCache`, `RGWChainedCache`, `RWLock`, notify service, sysobj core, and admin socket support. Policy and user-index caches use `RGWChainedCacheImpl`.

Risks and test signals: Lock ordering and expiry are key correctness points. Tests should cover chained cache registration/unregistration, expiry, invalidation on source object changes, and cache admin commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_cache.h -->
