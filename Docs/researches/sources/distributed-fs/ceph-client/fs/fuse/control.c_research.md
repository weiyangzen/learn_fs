# sources/distributed-fs/ceph-client/fs/fuse/control.c

## Purpose
`control.c` implements the `fusectl` pseudo-filesystem that exposes live FUSE connection controls and counters under per-connection directories.

## Important APIs, Types, and Functions
- `fuse_ctl_add_conn()` creates a directory named by connection device id with `waiting`, `abort`, `max_background`, and `congestion_threshold` files.
- `fuse_ctl_remove_conn()` removes that directory and clears inode-private connection pointers.
- `fuse_conn_abort_write()` aborts a connection.
- `fuse_conn_waiting_read()` reports `fc->num_waiting`.
- limit readers/writers expose and adjust `max_background` and `congestion_threshold`.
- `fuse_ctl_init()`/`fuse_ctl_cleanup()` register and unregister the `fusectl` filesystem.

## Control Flow
Mounting `fusectl` creates a singleton superblock with `simple_fill_super()`, records it under `fuse_mutex`, and adds existing connections. Connection add/remove is also serialized by `fuse_mutex`. File operations acquire a temporary `fuse_conn` reference from inode private data, perform the read/write operation, and drop it. Writes to `max_background` update `fc->blocked` under `bg_lock` and wake blocked waiters when limits allow progress.

## State and Persistence
State is in the singleton `fuse_control_sb`, persistent dentries/inodes in the pseudo-filesystem, inode `i_private` pointers to `fuse_conn`, and live connection counters/limits. Values are not persistent across unmount or connection teardown.

## Dependencies and Integration Points
This file integrates with FUSE connection registration, `simple_fill_super`, `get_tree_single`, `kill_anon_super`, `fuse_abort_conn()`, and global tunables `max_user_bgreq`/`max_user_congthresh`.

## Risks
The singleton superblock and borrowed dentry references require `fuse_mutex` discipline. Limit writes from unprivileged users are clamped by global limits; privileged writes can set up to 65535. Stale control files must clear `i_private` during removal to avoid use-after-free.

## Test Signals
Mount/unmount `fusectl`, create and destroy FUSE mounts while mounted, read counters, adjust limits as privileged and unprivileged users, abort a hung connection, and run lockdep during concurrent connection teardown.
