# sources/distributed-fs/ceph-client/fs/ceph/super.h

## Purpose
`super.h` is the central CephFS client contract header. It defines mount options, per-mount client state, inode/cap/xattr/snap data structures, inline helpers, constants, and cross-file function declarations.

## Important APIs, Types, And Functions
Major types include `struct ceph_mount_options`, `struct ceph_fs_client`, `struct ceph_cap`, `struct ceph_cap_flush`, `struct ceph_cap_snap`, `struct ceph_inode_xattr`, `struct ceph_inode_xattrs_info`, `struct ceph_inode_info`, `struct ceph_file_info`, `struct ceph_dir_file_info`, `struct ceph_rw_context`, and `struct ceph_snap_realm`. Inline helpers cover option tests, inode/client conversions, vino presentation, inode lookup, cap checks, dir completeness, workqueue scheduling, quota updates, and shutdown checks.

## Control Flow
The header establishes how implementation files coordinate: superblock code constructs `ceph_fs_client`; inode/file/dir/xattr/cap/snap code mutates fields in `ceph_inode_info`; snap code uses `ceph_snap_realm`; and workqueue helpers schedule asynchronous inode actions by setting work bits.

## State, Persistence, And Dependencies
All declarations describe in-kernel state. Persistent authoritative state remains on MDS/OSD servers. Dependencies span VFS, netfs, fscache, fscrypt, libceph, exportfs, mempools, atomics, waitqueues, rb-trees, and Ceph protocol headers.

## Integration Points
This header is included by most CephFS client source files and is the glue for VFS operations, MDS requests, OSD data IO, snapshots, quotas, caps, ACL/security labels, fscrypt, debugfs, and export support.

## Risks
Because it is shared, field lifetime and lock rules are critical. `i_ceph_lock`, session mutexes, snap semaphores, and dirty/flushing lists must be used consistently. Structure changes can silently affect slab sizes, cache initialization, on-stack assumptions, or cross-file invariants.

## Test Signals
Build all CephFS config combinations, run sparse/lockdep/KCSAN, exercise mount/open/read/write/xattr/snapshot/quota/readdir paths, and use fault injection around cap flushes, snap contexts, and workqueue shutdown.
