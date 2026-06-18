<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h

Purpose: Declares the virtual backend contract for system-object operations and the default RADOS core implementation.

Important APIs, types, and functions: `RGWSI_SysObj_Core` derives from `RGWServiceInstance`, owns RADOS and zone pointers, provides `core_init()`, object resolution, virtual raw/stat/read/write/remove/attr/omap/notify/list operations, and `get_zone_svc()`.

Control flow: `RGWSI_SysObj` facade calls these protected virtual methods. Cached backends override selected methods and call base core on misses or after cache handling.

State and persistence: The core stores only dependency pointers. Persistent state is owned by backend RADOS operations.

Dependencies and integration points: Depends on sysobj facade and core type headers, RGW service base, RADOS, and zone service.

Risks and test signals: The virtual interface is broad, so derived classes must preserve version tracker and error semantics. Tests should run shared sysobj behavior against both core and cached implementations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_sys_obj_core.h -->
