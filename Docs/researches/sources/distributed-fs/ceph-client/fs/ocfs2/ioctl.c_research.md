# sources/distributed-fs/ceph-client/fs/ocfs2/ioctl.c

## Purpose
`ioctl.c` implements OCFS2 user-visible ioctl handling and file attribute get/set support. It dispatches space reservation, online resize group operations, reflink, information queries, trim, and extent movement. It also implements the `OCFS2_IOC_INFO` multiplexed query API for filesystem geometry, labels, features, journal size, free inode counts, and free-fragmentation statistics.

## Important APIs, types, and functions
- `ocfs2_fileattr_get()` and `ocfs2_fileattr_set()` bridge VFS fileattr operations to OCFS2 inode attributes with cluster locking and journaling.
- `ocfs2_ioctl()` is the main unlocked ioctl dispatcher.
- `ocfs2_compat_ioctl()` handles 32-bit compat argument forms for reflink and info requests before delegating compatible commands.
- `ocfs2_info_handle()` validates an `ocfs2_info` request array and dispatches each `ocfs2_info_request`.
- `ocfs2_info_handle_*()` functions fill specific info structures: block size, cluster size, max slots, label, UUID, features, journal size, free inode stats, and free fragmentation stats.
- Free-inode and free-fragment helpers optionally use coherent cluster-locked reads or non-coherent raw block reads depending on `OCFS2_INFO_FL_NON_COHERENT`.

## Control flow
Attribute set first locks the inode exclusively, masks unsupported or immutable flags, repeats capability checks while the cluster lock is held, starts a small transaction, updates `ip_attr`, VFS inode flags, ctime, and marks the dinode dirty. The ioctl dispatcher copies small argument structures from userspace, checks capabilities and write access for mutating operations, calls the relevant OCFS2 subsystem, then drops write access.

`OCFS2_IOC_INFO` first copies the header, validates request count and pointer array, then copies each request header and dispatches by `ir_code` and `ir_size`. Known handlers set `OCFS2_INFO_FL_FILLED`; unknown requests clear the filled bit without failing the whole API. Free-inode scans iterate per-slot inode allocator system files. Free-fragment scans walk global bitmap chain records and group descriptors, building a histogram and aggregate chunk statistics.

## State and persistence behavior
Most info ioctls are read-only. Attribute set persists inode flags through `ocfs2_mark_inode_dirty()`. Resize group add/extend, reserve/unreserve space, reflink, trim, and move-extents delegate persistence to their subsystem implementations. Info handlers write result flags and data back to userspace; on per-request failures some handlers best-effort set `OCFS2_INFO_FL_ERROR` in the user request.

## Dependencies and integration points
This file integrates with VFS fileattr APIs, Linux ioctl/compat/capability helpers, OCFS2 inode locking and journaling, resize, reflink/refcount tree, file space management, sysfile lookup, suballocator and group descriptor readers, discard/trim, and `move_extents.c`.

## Risks and edge cases
- Non-coherent info scans intentionally read raw disk blocks without cluster locks; they include extra validation for group descriptor bitmap bounds but can return racing data.
- Request-array handling depends on userspace pointers stored as `u64`; compat paths must use `compat_ptr()` where appropriate.
- Mutating ioctls must hold `mnt_want_write_file()` and enforce capability checks. Missing one would allow write operations on read-only mounts or without privilege.
- Unknown info requests are non-fatal for forward/backward compatibility, which tests should not treat as a hard error.

## Test signals
Exercise normal and compat ioctl paths, `OCFS2_IOC_INFO` arrays with mixed known/unknown requests, coherent and non-coherent free-inode/free-frag queries, invalid magic/size/count/pointers, immutable/append fileattr changes with and without `CAP_LINUX_IMMUTABLE`, group resize privilege checks, FITRIM capability and discard support, and move-extents dispatch on invalid/non-regular files.
