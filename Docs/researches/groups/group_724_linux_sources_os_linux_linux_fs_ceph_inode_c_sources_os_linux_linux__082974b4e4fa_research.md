# Group Research: group_724_linux_sources_os_linux_linux_fs_ceph_inode_c_sources_os_linux_linux__082974b4e4fa

Scope source tree: `sources/os/linux/linux` from `Docs/research_subset_a.md`.

Files researched completely:
- `sources/os/linux/linux/fs/ceph/inode.c`
- `sources/os/linux/linux/fs/ceph/io.c`
- `sources/os/linux/linux/fs/ceph/io.h`
- `sources/os/linux/linux/fs/ceph/ioctl.c`
- `sources/os/linux/linux/fs/ceph/ioctl.h`
- `sources/os/linux/linux/fs/ceph/locks.c`

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/inode.c -->
# File Research: sources/os/linux/linux/fs/ceph/inode.c

## Purpose

`inode.c` is the central CephFS inode implementation. It allocates, initializes, fills, updates, evicts, and shuts down `struct ceph_inode_info` instances and wires CephFS inode state into the Linux VFS inode, dentry, readdir, getattr, setattr, symlink, fscrypt, fscache, quota, snapshot, capability, and MDS reply paths.

The file is primarily responsible for translating authoritative metadata returned by MDS replies into local kernel state while respecting Ceph capability ownership. It also maintains directory fragment routing metadata, dentry leases, readdir cache state, deferred page-cache invalidation/truncation work, and synchronous or local setattr decisions.

## Major Interfaces

- `ceph_new_inode()` preallocates a VFS inode for create-like operations, prepares ACL/security context, and prepares fscrypt context except for snapdir children.
- `ceph_as_ctx_to_req()` transfers prepared ACL/security/fscrypt context into an MDS request.
- `ceph_get_inode()` finds or inserts an inode by Ceph virtual inode number (`struct ceph_vino`), using `iget5_locked()`/`inode_insert5()` and `ceph_ino_compare`.
- `ceph_get_snapdir()` creates or returns the synthetic `.snap` directory inode associated with a real directory.
- `ceph_alloc_inode()`, `ceph_free_inode()`, and `ceph_evict_inode()` implement inode cache lifecycle and cleanup of Ceph-specific state.
- `ceph_fill_inode()` assimilates a parsed MDS inode record into a live inode, including caps, layout, xattrs, size/time, symlink target, directory stats, snapshots, encryption state, and inline data.
- `ceph_fill_trace()` assimilates an MDS reply trace into parent, target inode, and dentry cache state.
- `ceph_readdir_prepopulate()` prepopulates inode/dentry cache and optional page-backed readdir cache from MDS readdir replies.
- `ceph_inode_set_size()` updates size and reports whether size should be sent to the MDS.
- `ceph_queue_inode_work()` schedules deferred inode work on `fsc->inode_wq`.
- `__ceph_do_pending_vmtruncate()` and `ceph_do_invalidate_pages()` perform deferred page-cache truncation and invalidation.
- `__ceph_setattr()` and `ceph_setattr()` implement local-vs-remote setattr logic.
- `__ceph_do_getattr()`, `ceph_getattr()`, `ceph_do_getvxattr()`, and `ceph_permission()` implement metadata refresh and VFS stat/permission behavior.
- `ceph_try_to_choose_auth_mds()` chooses auth MDS for operations that should avoid stale replicas.
- `ceph_inode_shutdown()` purges caps and marks an inode unusable after shutdown.

## Notes

This report was written to `Docs/researches/groups/group_724_linux_sources_os_linux_linux_fs_ceph_inode_c_sources_os_linux_linux__082974b4e4fa_research.md` and validated for all 6 BEGIN/END marker pairs.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/inode.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/io.c -->
# File Research: sources/os/linux/linux/fs/ceph/io.c

## Purpose

`io.c` provides synchronization helpers that coordinate buffered and direct I/O on a Ceph inode. It uses `inode->i_rwsem` plus `CEPH_I_ODIRECT` in `ci->i_ceph_flags` to prevent unsafe overlap between buffered page-cache I/O and direct I/O.

## Major Interfaces

- `ceph_start_io_read()` / `ceph_end_io_read()`
- `ceph_start_io_write()` / `ceph_end_io_write()`
- `ceph_start_io_direct()` / `ceph_end_io_direct()`

The start helpers return `0` or an interrupt error from killable rwsem acquisition and must be checked.

## Control Flow

Buffered read starts with a shared `i_rwsem`; if direct I/O is active, it upgrades through the write lock, clears `CEPH_I_ODIRECT`, waits for direct I/O with `inode_dio_wait()`, then downgrades.

Buffered write takes the write lock, clears direct I/O mode, and waits for outstanding direct I/O.

Direct I/O starts with a shared `i_rwsem`; if buffered mode is active, it upgrades through the write lock, sets `CEPH_I_ODIRECT`, and waits for buffered writeback via `filemap_write_and_wait()`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/io.h -->
# File Research: sources/os/linux/linux/fs/ceph/io.h

## Purpose

`io.h` declares the CephFS buffered/direct I/O coordination helpers implemented in `io.c`.

## Public API

- `int __must_check ceph_start_io_read(struct inode *inode);`
- `void ceph_end_io_read(struct inode *inode);`
- `int __must_check ceph_start_io_write(struct inode *inode);`
- `void ceph_end_io_write(struct inode *inode);`
- `int __must_check ceph_start_io_direct(struct inode *inode);`
- `void ceph_end_io_direct(struct inode *inode);`

The `__must_check` annotation is significant: callers must not call the matching end helper after a failed start.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/io.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/ioctl.c -->
# File Research: sources/os/linux/linux/fs/ceph/ioctl.c

## Purpose

`ioctl.c` implements CephFS file ioctl handling. It supports layout inspection and changes, data-location queries, lazy/sync I/O mode flags, and forwarding fscrypt policy/key ioctls with Ceph-specific MDS feature checks.

## Major Interfaces

- `ceph_ioctl()` dispatches all supported ioctls.
- `ceph_ioctl_get_layout()` returns layout fields.
- `ceph_ioctl_set_layout()` sends `CEPH_MDS_OP_SETLAYOUT`.
- `ceph_ioctl_set_layout_policy()` sends `CEPH_MDS_OP_SETDIRLAYOUT`.
- `ceph_ioctl_get_dataloc()` maps a file offset to Ceph object and OSD location.
- `ceph_ioctl_lazyio()` marks a file descriptor lazy and triggers cap recheck.
- `ceph_ioctl_syncio()` sets `CEPH_F_SYNC`.
- `ceph_set_encryption_policy()` wraps fscrypt policy setup with Ceph validation.

## Risks

- User-copy failures return `-EFAULT`; invalid layouts return `-EINVAL`.
- `vet_mds_for_fscrypt()` checks active MDS feature support before fscrypt operations.
- Data-location mapping depends on valid layout state and OSD-map locking.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/ioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/ioctl.h -->
# File Research: sources/os/linux/linux/fs/ceph/ioctl.h

## Purpose

`ioctl.h` defines the userspace ABI for CephFS-specific ioctl commands and argument structures.

## ABI Definitions

`CEPH_IOCTL_MAGIC` is `0x97`.

`struct ceph_ioctl_layout` contains stripe unit, stripe count, object size, data pool, and obsolete `preferred_osd`.

Layout ioctls:
- `CEPH_IOC_GET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT`
- `CEPH_IOC_SET_LAYOUT_POLICY`

`struct ceph_ioctl_dataloc` carries input `file_offset` and outputs object offset, object number, object size, object name, block offset, block size, OSD id, and OSD address.

Mode ioctls:
- `CEPH_IOC_LAZYIO`
- `CEPH_IOC_SYNCIO`

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/ceph/locks.c -->
# File Research: sources/os/linux/linux/fs/ceph/locks.c

## Purpose

`locks.c` implements CephFS POSIX byte-range locks and BSD-style flock locks by coordinating Linux local file locks with MDS-distributed lock state. It also serializes local lock state for recovery and reconnect paths.

## Major Interfaces

- `ceph_flock_init()` initializes the per-boot random lock secret.
- `ceph_lock()` handles POSIX/fcntl locks.
- `ceph_flock()` handles flock locks.
- `ceph_count_locks()` counts current local fcntl and flock locks.
- `ceph_encode_locks_to_buffer()` converts local locks to Ceph wire format.
- `ceph_locks_to_pagelist()` appends serialized lock data to a Ceph pagelist.

## Core Behavior

`secure_addr()` masks kernel lock-owner pointers with a random secret and sets the high bit so the MDS can identify owners without raw kernel addresses.

`ceph_lock_message()` creates MDS file-lock requests, encodes owner/pid/range/type/wait state, waits for completion, and converts `GETFILELOCK` replies back into Linux `struct file_lock`.

For successful remote set-lock operations, the code installs the lock locally. If local installation fails, it sends a remote unlock to roll back MDS state.

## Risks

Blocking locks have complex interrupt handling: interrupted requests may need abort marking plus a separate interrupt unlock request before safe completion. Lock replay encoding can race with local lock changes between count and encode; overflow is detected with `-ENOSPC`.

<!-- END FILE RESEARCH: sources/os/linux/linux/fs/ceph/locks.c -->