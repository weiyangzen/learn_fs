<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h -->
# sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h

Purpose: this header defines file mode constants for non-glibc or kernel contexts and the `statx(2)` ABI for extended file metadata.

Important APIs/types: it defines `S_IF*`, `S_IS*`, and permission bits when appropriate. `struct statx_timestamp` and `struct statx` expose mask, block size, attributes, ownership, mode, inode, size, blocks, timestamps, device IDs, mount ID, direct-I/O alignments, subvolume ID, atomic-write limits, and spare space. `STATX_*` masks request/result fields, and `STATX_ATTR_*` exposes file attributes like compressed, immutable, append-only, encrypted, automount, mount-root, verity, DAX, and atomic-write support.

Control flow: userspace calls `statx()` with a mask; the kernel fills fields it supports and reports valid fields in `stx_mask`. The comments document synchronization behavior and compatibility fallback for basic stats.

State and persistence: returned metadata reflects filesystem/inode state and mount state at call time. Layout reserves space for future ABI expansion.

Dependencies/integration: depends on `linux/types.h`; integrated by filesystems, libc fallbacks, backup/indexing tools, direct-I/O users, and distributed filesystem clients that need mount IDs or alignment data.

Risks and test signals: risks include assuming requested fields are always returned, confusing `STATX_MNT_ID` vs unique mount ID, alignment fields availability, and treating deprecated `STATX_ALL` as complete. Test masks individually across filesystems, symlinks, device nodes, DAX/verity/encrypted files, and unsupported fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/uapi/linux/stat.h -->
