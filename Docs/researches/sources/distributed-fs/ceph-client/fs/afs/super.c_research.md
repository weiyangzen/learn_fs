<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/super.c -->
# sources/distributed-fs/ceph-client/fs/afs/super.c

## Purpose
Implements AFS filesystem registration, mount parameter parsing, superblock creation/reuse, inode slab lifecycle, mount option display, and statfs.

## Important APIs, Types, And Functions
Defines `afs_fs_type`, `afs_net_id`, `afs_super_ops`, `afs_fs_init()`, and `afs_fs_exit()`. Internal functions parse `source`, `dyn`, `autocell`, and `flock`, validate mount context, allocate/destroy `afs_super_info`, fill superblocks, allocate/free/destroy `afs_vnode` inodes, and issue volume status for `statfs`.

## Control Flow
Mount initialization creates an `afs_fs_context` defaulting to the workstation cell and RO volume type. `source` parsing determines cell, volume, suffix, and forced RW/RO/BK semantics. Validation gets a key, detects cell aliases, creates a volume, and makes non-RW mounts read-only with local flock. `sget_fc()` reuses matching volume superblocks or creates dynroot superblocks; root inode setup activates the volume.

## State And Persistence
State includes filesystem registration, inode kmem cache, active inode counter, superblock private data, mount context refs, volume activation, and `volume->sb` pointer. No durable local state is written.

## Dependencies And Integration Points
Integrates VFS fs_context, net namespaces, AFS cell/volume creation, alias detection, key lookup, dynroot, inode/root lookup, xattrs, netfs writeback, mountpoint expiry, and statfs RPCs.

## Risks And Edge Cases
Mount source parsing controls security and semantics; mistakes can mount wrong cell/volume type. Alias switching requires key reacquisition. Inode slab reuse must reset all sensitive fields. Superblock reuse must match netns, cell, and volume ID exactly.

## Test Signals
Mount `%`/`#` sources with cell-qualified and default-cell names, `.readonly`, `.backup`, trailing `.`, dynroot, alias cells, non-RW read-only behavior, inode leak checks on unload, and statfs volume status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/afs/super.c -->
