<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h

Purpose: Provides generic empty base types for sysobj backend state.

Important APIs, types, and functions: `RGWSI_SysObj_Obj_GetObjState` and `RGWSI_SysObj_Pool_ListInfo` are marker/base structs.

Control flow: Concrete backend state types inherit these bases and are stored by the sysobj facade without exposing backend implementation details.

State and persistence: No owned state or persistence.

Dependencies and integration points: Depends only on RGW service base. Used by sysobj facade and core/cache backends.

Risks and test signals: Because the base types are empty, all behavior depends on correct static casting to concrete types by the active backend. Compile-time and backend integration tests are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_types.h -->
