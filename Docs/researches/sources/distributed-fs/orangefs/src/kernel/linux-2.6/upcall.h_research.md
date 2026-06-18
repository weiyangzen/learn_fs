<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h -->
# sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h

## Purpose
Defines the sanitized kernel-to-client-core upcall request ABI for OrangeFS Linux kernel operations. It collects fixed-width request payload structs and the top-level `pvfs2_upcall_t` union used by the kernel device/request queue to describe work for user-space servicing.

## Important APIs, Types, and Functions
The header declares request structs for I/O, lookup, create, symlink, getattr, setattr, remove, mkdir, readdir, readdirplus, rename, statfs, truncate, readahead flush, fs mount/unmount, xattr get/set/list/remove, cancel, fsync, runtime parameter get/set, performance counters, filesystem key lookup, and feature negotiation. `pvfs2_upcall_t` contains caller identity fields (`type`, `uid`, `gid`, `pid`, `tgid`), optional trailer metadata for extended I/O, and a union named `req`. Enums `pvfs2_param_request_type`, `pvfs2_param_request_op`, and `pvfs2_perf_count_request_type` define ioctl/control-plane request classes.

## Control Flow
Kernel VFS paths allocate `pvfs2_kernel_op_t` objects, fill `op->upcall.req.<operation>`, and hand them to `service_operation`. The device side exposes these fixed-layout structs to client-core, which performs the remote OrangeFS system call and later returns a matching downcall. This header does not implement flow itself; it defines the memory contract that flow depends on.

## State and Persistence
No persistent state is kept in the header. Layout is state-critical: fixed-width integers, explicit padding fields, `PVFS2_ALIGN_VAR` around trailer pointers, and bounded inline arrays such as `PVFS2_NAME_LEN` and `PVFS_MAX_XATTR_NAMELEN` are used to stabilize 32/64-bit kernel-user interactions.

## Dependencies and Integration Points
Includes `pvfs2-sysint.h` and uses shared protocol types including `PVFS_object_kref`, `PVFS_sys_attr`, `PVFS_ds_position`, `PVFS_fs_id`, `PVFS_keyval_pair`, uid/gid types, and `PVFS_size`. It is consumed by kernel operation setup code, the device file implementation, waitqueue servicing, and client-core downcall matching.

## Risks
This is an ABI-sensitive file: changing field order, type width, padding, enum values, or array sizes can break kernel/client-core compatibility. Pointer-bearing fields such as `trailer_buf` require careful translation and cannot be treated as stable user-space addresses. Request structs with inline names depend on callers enforcing NUL termination and length limits.

## Test Signals
Compile and run 32-bit kernel with 64-bit client-core compatibility tests where supported, validate each operation's upcall size and field offsets, fuzz boundary-length names/xattr keys, test parameter and perf-count requests, and exercise cancel and trailer-based readx/writex requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/kernel/linux-2.6/upcall.h -->
