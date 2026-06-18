<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc

Purpose: Implements the high-level fluent system-object facade that forwards read, write, omap, notify, and pool-list operations to the configured core backend.

Important APIs, types, and functions: `RGWSI_SysObj::get_obj()` creates an `Obj`. `Obj::ROp` methods call `stat()`, `read()`, and `get_attr()` on the core. `Obj::WOp` methods call `remove()`, `write()`, `write_data()`, `set_attrs()`, and single-attr writes. `Obj::OmapOp` methods call omap get/set/delete. `Obj::WNOp::notify()` forwards notify. `Pool` and `Pool::Op` forward prefix-list and paginated list operations. `get_zone_svc()` exposes the core's zone service.

Control flow: Callers construct lightweight operation objects from `Obj` or `Pool`, set optional parameters on the operation object, then call the terminal method. The operation object collects parameters and delegates to the backend core, which may be cached or uncached.

State and persistence: Operation objects hold transient pointers to version trackers, attrs, flags, and list contexts. Persistent state is in RADOS system objects managed by the core backend.

Dependencies and integration points: Depends on `RGWSI_SysObj_Core`, zone service, RGW raw object and pool types, `RGWObjVersionTracker`, and cache info. This facade is used by user, mdlog, bucket sync, zone, and other RGW metadata services.

Risks and test signals: Because operations store raw pointers supplied by callers, lifetime is caller-managed. Tests should exercise fluent setters, stat/read/write attr behavior, omap operations, notify, and paginated pool listing through both core and cache backends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.cc -->
