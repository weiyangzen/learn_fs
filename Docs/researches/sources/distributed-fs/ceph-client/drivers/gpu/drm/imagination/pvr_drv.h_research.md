# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_drv.h

Purpose: declares driver identity/version constants and generic UAPI object copy helpers/macros for PowerVR ioctl compatibility.

Important APIs/types: constants define name `powervr`, description, and interface version `1.0.0`. Functions copy single user objects and arrays with stride/min-size handling. `PVR_UOBJ_MIN_SIZE()` uses `_Generic` mappings to derive minimum supported sizes for specific UAPI structs. Macros `PVR_UOBJ_GET`, `PVR_UOBJ_SET`, `PVR_UOBJ_GET_ARRAY`, and `PVR_UOBJ_SET_ARRAY` wrap helper calls with type-derived sizes.

Control flow and state: no persistent state. Ioctl handlers use these macros to accept older/larger user structs while enforcing required mandatory fields.

Dependencies and integration: includes UAPI `pvr_drm.h` and compiler attributes. The `_Generic` list is a central compatibility registry for query/job/sync/heap/static-data structures.

Risks: any UAPI struct used with the macros must be listed or compilation fails. Choosing the wrong last mandatory field changes ABI acceptance. Array copy helpers depend on correct stride semantics.

Test signals: compile coverage for every macro use and UAPI compatibility tests with minimum-size, exact-size, and extended-size structs/arrays.
