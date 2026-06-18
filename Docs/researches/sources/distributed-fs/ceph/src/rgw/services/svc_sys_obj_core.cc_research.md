<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc

Purpose: Implements the uncached RADOS backend for RGW system-object operations.

Important APIs, types, and functions: `RGWSI_SysObj_Core_GetObjState::get_rados_obj()` lazily resolves a `rgw_rados_ref`. Core methods include `get_rados_obj()`, `raw_stat()`, `stat()`, `read()`, `get_attr()`, `set_attrs()`, `omap_get_vals()`, `omap_get_all()`, `omap_set()`, `omap_del()`, `notify()`, `remove()`, `write()`, `write_data()`, and pool listing methods.

Control flow: Each operation resolves an object or IoCtx, builds a `librados::ObjectReadOperation` or `ObjectWriteOperation`, applies version tracker hooks when provided, executes via RADOS helpers, and returns negative errno or data length. Reads track the RADOS operation version in read state and return `-ECANCELED` if a later read on the same state observes a different version. Full writes remove and recreate nonexclusive objects, set mtime, write data and attrs, and apply write versions.

State and persistence: Persistent state is RADOS object data, xattrs, omap entries, and object versions. The core holds RADOS and zone service pointers. Pool listing context stores IoCtx, prefix filter, and marker.

Dependencies and integration points: Depends on `rgw_get_rados_ref()`, `rgw_rados_operate()`, `rgw_init_ioctx()`, `rgw_list_pool()`, `RGWObjVersionTracker`, RGW attr filtering, and librados operations. It underlies both direct sysobj service use and the cache backend.

Risks and test signals: Empty object ids return `-EINVAL`. Nonexclusive `write()` replaces the whole object, so callers must choose `write_data()` or attr writes carefully. `get_attr()` ignores the per-op `rval` and returns success if the object operation succeeds, which relies on librados operation error propagation. Tests should cover version race detection, xattr filtering, omap pagination, exclusive create, remove ENOENT behavior, notify, and pool marker progression.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.cc -->
