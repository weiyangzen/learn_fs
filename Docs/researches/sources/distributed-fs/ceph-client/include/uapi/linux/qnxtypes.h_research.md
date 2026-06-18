<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h

Purpose: defines fixed-width QNX4 on-disk scalar types and extent representation used by the QNX4 filesystem ABI.

Important APIs and types: typedefs define QNX4 extent count, file type, mode, uid, gid, offset, and link count widths. `qnx4_xtnt_t` stores little-endian block and size fields for an extent.

Control flow: no control flow exists. QNX4 filesystem code uses these types while decoding on-disk metadata from `qnx4_fs.h`.

State and persistence: these typedefs describe persistent disk layout widths and endian choices; they do not own runtime state.

Dependencies and integration points: depends on Linux fixed integer types and integrates only with QNX4 filesystem structures and tools.

Risks and test signals: risks include widening/sign changes that would corrupt disk ABI, endian conversion mistakes, and extent-size overflow. Test compile layout assertions, QNX4 image mount/read, and cross-endian metadata decoding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/qnxtypes.h -->
