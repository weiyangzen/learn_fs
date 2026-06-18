## sources/distributed-fs/ceph-client/fs/orangefs/devorangefs-req.c

### Purpose
This file implements the `/dev/pvfs2-req` character device that connects the kernel VFS client to the OrangeFS userspace client daemon. Kernel operations are read by userspace as upcalls and completed by writes containing downcalls.

### Important APIs, types, and functions
- `orangefs_devreq_open()` enforces a single nonblocking opener in `init_user_ns`.
- `orangefs_devreq_read()` dequeues a waiting `orangefs_kernel_op_s`, copies protocol version, magic, tag, and upcall to userspace, and moves the op to the in-progress hash table.
- `orangefs_devreq_write_iter()` validates version/magic/tag, removes the matching op from the hash table, copies the downcall and optional readdir trailer, and completes the waiter.
- `orangefs_devreq_release()` handles daemon shutdown, finalizes bufmap state, marks mounts pending, purges waiting and in-progress ops, and resets version/open state.
- `dispatch_ioctl_command()` handles device metadata, bufmap mapping, remount-all, upstream marker, and debug mask ioctls.
- `orangefs_dev_init()` and `orangefs_dev_cleanup()` register and unregister the character device.

### Control flow
Userspace opens the device with `O_NONBLOCK`, queries sizes and maps shared buffers through ioctls, then polls/reads. Read skips purged/given-up operations and operations whose filesystem is pending remount, copies the upcall header and payload, then marks the op in progress. Write receives the downcall header and body, verifies protocol compatibility and stable userspace version, finds the op by tag, optionally copies a readdir trailer into kernel memory, sets error status on malformed input, and wakes the original VFS waiter.

### State and persistence behavior
Runtime state includes `open_access_count`, `orangefs_userspace_version`, in-progress op hash tables, pending mount flags on superblocks, and bufmap lifetime. There is no on-disk persistence, but release has distributed consistency effects because it marks existing mounts pending and forces remount/retry semantics after daemon restart.

### Dependencies and integration points
Depends on operation lists and hash tables from `orangefs-mod.c`, bufmap APIs, debugfs APIs, superblock list state, waitqueue purge functions, and protocol structs from `orangefs-dev-proto.h`, `upcall.h`, and `downcall.h`. VFS operations throughout OrangeFS depend on this device path through `service_operation()`.

### Risks
This is a trust boundary. Size, magic, protocol version, trailer length, and tag validation protect kernel state from malformed daemon writes. Single-opener enforcement is required because multiple daemons could otherwise race operation ownership. Release/purge paths must avoid use-after-free while marking ops purged or completing cancellations. Large readdir trailers allocate with `vzalloc()` and must be freed by directory code or error paths.

### Test signals
Exercise daemon open rejection, blocking open/read rejection, ioctl size queries, bufmap mapping, read/write protocol mismatch, readdir trailer validation, daemon crash/restart purging, remount-all, poll readiness, and compat ioctl mapping from 32-bit userspace.
