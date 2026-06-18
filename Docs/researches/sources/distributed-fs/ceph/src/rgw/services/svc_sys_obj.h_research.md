<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h

Purpose: Declares the system-object service abstraction used by RGW metadata code to avoid direct RADOS operations at call sites.

Important APIs, types, and functions: `RGWSI_SysObj` derives from `RGWServiceInstance` and declares nested `Obj`, `Obj::ROp`, `Obj::WOp`, `Obj::OmapOp`, `Obj::WNOp`, `Pool`, `Pool::Op`, and list context types. The API provides setters for version trackers, attrs, mtime, exclusive create, raw attrs, refresh versions, cache info, omap must-exist, and pool listing markers/prefixes.

Control flow: Service graph initializes `RGWSI_SysObj` with a RADOS pointer and concrete `RGWSI_SysObj_Core`. Consumers get an object or pool handle and build operation objects for read/write/list operations.

State and persistence: The service holds RADOS and core pointers only. Operation structs hold transient call configuration and use `static_ptr` to host backend-specific state.

Dependencies and integration points: Depends on RGW service base, sysobj type headers, core type headers, `rgw_raw_obj`, `rgw_pool`, and cache entry info. It is a central integration point for most RGW service metadata persistence.

Risks and test signals: Backend-specific state size in `static_ptr` must remain large enough for derived state types. Tests should compile with all backend state types and exercise operation APIs through `RGWSysObj` alias.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj.h -->
