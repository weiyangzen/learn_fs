<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h -->
# sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h

Purpose: Declares the concrete RADOS-backed user service.

Important APIs, types, and functions: `RGWSI_User_RADOS` derives from `RGWSI_User`, owns a `user_info_cache_entry` chained cache, RADOS pointer, and service dependency struct. It declares helper methods for bucket object naming, secondary-index lookup, UID/index removals, lifecycle startup, and all base user service overrides.

Control flow: Service graph initializes dependencies, startup creates the chained cache, and public methods read/write/remove user metadata and resolve secondary indexes.

State and persistence: Header state is in-memory cache and service pointers. Persistent user data lives in RADOS pools selected from zone params and is maintained by implementation.

Dependencies and integration points: Depends on user base, RGW bucket header for subclass dependency, mdlog/zone/sysobj/cache services, and `RGWChainedCacheImpl`.

Risks and test signals: Friend `PutOperation` accesses internals, so store logic is tightly coupled to the class state. Tests should verify all virtual user service operations through a `RGWSI_User*` reference and cache behavior through secondary lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/rgw/services/svc_user_rados.h -->
