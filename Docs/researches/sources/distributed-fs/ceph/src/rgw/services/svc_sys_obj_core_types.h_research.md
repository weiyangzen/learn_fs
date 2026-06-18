<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h

Purpose: Defines backend-specific state structures used by `RGWSI_SysObj_Core` operations.

Important APIs, types, and functions: `RGWSI_SysObj_Core_GetObjState` extends the generic object read state with cached `rgw_rados_ref`, `has_rados_obj`, and `last_ver`, plus `get_rados_obj()`. `RGWSI_SysObj_Core_PoolListImplInfo` extends pool-list state with `librados::IoCtx`, `rgw::AccessListFilter`, and marker.

Control flow: Read operations keep a core get-state object inside `static_ptr`; pool list operations keep list context inside `static_ptr`.

State and persistence: These structures are transient per-operation/per-list state. They do not own persistent data.

Dependencies and integration points: Depends on RGW RADOS tools, service base, sysobj generic state, librados, and access-list filters.

Risks and test signals: `static_ptr` sizing in `svc_sys_obj.h` must accommodate these types. Tests should compile and execute repeated reads and paginated listings that reuse the state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core_types.h -->
