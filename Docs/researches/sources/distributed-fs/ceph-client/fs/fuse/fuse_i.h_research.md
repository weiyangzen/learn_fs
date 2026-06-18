# sources/distributed-fs/ceph-client/fs/fuse/fuse_i.h

## Purpose
`fuse_i.h` is the private core header for the FUSE client. It declares the main in-kernel objects (`fuse_conn`, `fuse_mount`, `fuse_inode`, `fuse_file`, request queues, request args, I/O state), feature flags and constants, inline accessors, and cross-file function prototypes. It is the contract binding directory, file, inode, device, ioctl, xattr, ACL, DAX, passthrough, io_uring, and control filesystem code.

## Important APIs, Types, And Functions
Constants define request/page limits, filename limits, control dentries, timeout cadence, `FUSE_NOWRITE`, direct-I/O flags, and statx invalidation masks. `struct fuse_inode` extends `struct inode` with FUSE nodeid, lookup count, FORGET allocation, attribute timeout and invalidation mask, original mode/ino, birth time, attr version, regular-file writeback state, directory readdir-cache state, state bits, serialization locks, optional DAX, submount lookup, passthrough backing, and cached block bits.

`struct fuse_file` stores the connection mount, open/release argument storage, kernel and userspace handles, nodeid, refcount, open flags, writeback linkage, readdir state, poll RB node and waitqueue, I/O mode, passthrough file/cred, and flock state. `struct fuse_args`, `struct fuse_args_pages`, `struct fuse_io_args`, `struct fuse_io_priv`, and `struct fuse_req` define the request construction and completion model. `struct fuse_iqueue`, `struct fuse_pqueue`, and `struct fuse_dev` define pending/processing queues and device instances.

`struct fuse_conn` is the largest state object: it stores locking/refcounting, epoch work, users/namespaces, negotiated maxima, input and background queues, initialization/blocking state, connection feature bits, no-op fallbacks, cache policy, permissions, submount/syncfs/security/passthrough/io_uring flags, wait counters, active mounts/devices, attr/evict counters, timeout work, DAX state, backing maps, and writeback sync buckets. `struct fuse_mount` associates a potentially shared connection with one superblock.

Inline helpers include `get_fuse_mount*()`, `get_fuse_conn*()`, `get_fuse_inode()`, `get_node_id()`, `invalid_nodeid()`, `fuse_get_attr_version()`, `fuse_get_evict_ctr()`, stale/bad inode helpers, folio descriptor allocation/initialization, and `fuse_sync_bucket_dec()`.

## Control Flow
The header does not execute top-level logic but defines the data flow used by the implementation. VFS operations build `struct fuse_args` or `struct fuse_args_pages`, fill opcode/nodeid/input/output arrays, then send through simple or background request helpers. Inode and dentry code use connection feature flags negotiated during `FUSE_INIT` to select protocol operations, local fallback, cache invalidation policy, and permissions model. File code uses `fuse_file` and `fuse_inode` regular-file substate to coordinate open lifetime, cached I/O, direct I/O, writeback, mmap, and syncfs.

The queue model separates pending input (`fuse_iqueue`) from processing (`fuse_pqueue`) and background throttling (`fuse_conn` background fields). Device implementations attach `fuse_dev` instances to a connection and use the input queue ops for normal requests, forgets, and interrupts.

## State And Persistence Behavior
All persistent in-kernel FUSE state described by this subset is declared here. Lookup persistence is `nlookup` plus queued FORGET messages. Metadata persistence is timeout/invalidation/attribute-version state. File persistence is handle/refcount/open flag state. Connection persistence is negotiated capabilities, queue counters, mount/device membership, background congestion limits, timeout policy, and abort/disconnect state.

The header also encodes concurrency expectations: spinlocks protect queue and inode write fields, `killsb` protects mount-list superblock access, refcounts protect files/connections/backing files/submount lookups, and RCU protects connection release and sync buckets.

## Dependencies And Integration Points
`fuse_i.h` includes Linux FUSE UAPI, VFS, mount, wait, memory-management, backing-device, locking, poll, workqueue, xattr, pid/user namespace, and refcount headers. It declares integration points for `dir.c`, `file.c`, `inode.c`, device code, DAX, ioctl, iomode, xattr, ACL, readdir, control filesystem, sysctl, passthrough, and backing-file support.

## Risks And Edge Cases
Because this header is the shared ABI inside the module, layout and semantic changes have broad blast radius. Bitfields in `fuse_conn` are used as negotiated feature and negative-cache state; setting a `no_*` flag too early or too late changes externally visible behavior. The union in `fuse_inode` requires correct mode-specific initialization so regular-file writeback state and directory readdir-cache state are not confused. Request argument arrays have small fixed sizes, so extension insertion must respect bounds. Locking and lifetime comments are part of the correctness contract; violating them risks use-after-free, deadlock, lost FORGETs, or stale cache exposure.

## Test Signals
Test signals include compile coverage across config combinations (`CONFIG_FUSE_DAX`, `CONFIG_FUSE_PASSTHROUGH`, `CONFIG_FUSE_IO_URING`, `CONFIG_BLOCK`, `CONFIG_SYSCTL`), mount negotiation of every feature bit, inode mode initialization, connection abort and refcount release, queue state under background congestion, sync bucket accounting, request timeout behavior, FORGET accounting, passthrough/DAX disabled stubs, and idmapped mount permission combinations.
