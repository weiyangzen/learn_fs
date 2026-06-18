# sources/distributed-fs/orangefs/src/kernel/linux-2.6/downcall.h

Purpose: Defines the kernel-module side of OrangeFS/PVFS2 downcall response structures, the typed payloads that userspace client-core returns to completed VFS upcalls.

Important APIs and types: `pvfs2_downcall_t` is the top-level response envelope containing `type`, `status`, optional trailer size/buffer, and a union of operation-specific responses. Key payloads include `pvfs2_io_response_t`, `pvfs2_iox_response_t`, `pvfs2_lookup_response_t`, `pvfs2_create_response_t`, `pvfs2_symlink_response_t`, `pvfs2_getattr_response_t`, `pvfs2_readdir_response_t`, `pvfs2_readdirplus_response_t`, `pvfs2_statfs_response_t`, `pvfs2_fs_mount_response_t`, xattr responses, parameter/performance/fs-key responses, and `pvfs2_features_response_t`. `struct pvfs2_dirent` duplicates enough system-interface dirent shape for trailer decoding without extra allocations.

Control flow: This header has no executable control flow. It establishes the memory contract read by operation-specific kernel code after `service_operation` returns. Inline response fields are used directly for small fixed-size results, while large variable-size results such as readdir and readdirplus are represented by `trailer_size` and `trailer_buf` and decoded by callers such as `dir.c`.

State and persistence: No state is stored by the header itself. Instances are embedded in `pvfs2_kernel_op_t` objects and live only for the lifetime of an in-flight operation. The definitions are ABI-sensitive between kernel module and client-core; field order, padding fields, and alignment wrappers are part of that transient IPC contract.

Dependencies and integration points: Includes `pvfs2-sysint.h` for `PVFS_object_kref`, `PVFS_sys_attr`, `PVFS_error`, `PVFS_ds_position`, `PVFS_fs_id`, and size/name constants. The response union is consumed across file I/O, name lookup/create, inode getattr/setattr, directory reads, superblock mount/statfs, xattr handling, fsync, cancellation, feature negotiation, and perf counter paths.

Risks: This is a protocol layout header, so accidental field reordering or size changes can break 32/64-bit interoperability with client-core. Some responses are commented out of the union because they are blank or trailer-only; code must not assume those payloads exist inline. Fixed-size buffers for xattrs, performance counts, and fs keys require caller-side length validation. Readdirplus comments explicitly warn not to change field order unless the base readdir layout changes.

Test signals: Validate kernel/client-core structure-size and offset compatibility on 32-bit and 64-bit builds. Exercise every union member through its corresponding VFS operation, including blank-response operations. Add trailer-size mismatch tests for readdir/readdirplus and boundary tests for maximum xattr, listxattr, perf-count, and fs-key payload lengths.
