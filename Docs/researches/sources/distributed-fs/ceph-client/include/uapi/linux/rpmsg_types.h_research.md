<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h

Purpose: provides bitwise-annotated rpmsg integer typedefs for protocol fields whose endian or transport representation should not be mixed with normal integers.

Important APIs, types, and functions: `__rpmsg16`, `__rpmsg32`, and `__rpmsg64` are `__bitwise` wrappers over `__u16`, `__u32`, and `__u64`.

Control flow: rpmsg protocol headers and transports use these typedefs so sparse and reviewers can catch accidental mixing of raw CPU integers and rpmsg-formatted fields.

State and persistence behavior: no state exists here; the typedefs affect compile-time type checking.

Dependencies and integration points: depends on `linux/types.h` and integrates with rpmsg core/protocol headers that need annotated fields.

Risks and edge cases: the annotations only help when sparse or compatible checking is used. They do not encode conversion semantics by themselves, so callers must still use the proper endian/format helpers.

Test signals: sparse builds should report bad assignments, while normal builds should compile protocol structs using the annotated aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/rpmsg_types.h -->
