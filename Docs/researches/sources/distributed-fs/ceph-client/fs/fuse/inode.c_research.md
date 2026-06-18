# sources/distributed-fs/ceph-client/fs/fuse/inode.c

## Purpose
`inode.c` implements FUSE module, filesystem, mount, superblock, connection, inode, export, statfs, syncfs, and initialization-negotiation logic. It is the spine that creates `fuse_conn`/`fuse_mount`, parses mount options, installs `/dev/fuse` devices, negotiates protocol features through `FUSE_INIT`, creates and evicts FUSE inodes, handles submounts and NFS export file handles, and tears everything down at unmount/module exit.

## Important APIs, Types, And Functions
Allocation and inode lifecycle are handled by `fuse_alloc_inode()`, `fuse_free_inode()`, `fuse_evict_inode()`, `fuse_init_inode()`, `fuse_iget()`, `fuse_ilookup()`, `fuse_reverse_inval_inode()`, and `fuse_try_prune_one_inode()`. Attribute application is centralized in `fuse_change_attributes_common()`, `fuse_change_attributes_i()`, and `fuse_change_attributes()`, with `fuse_get_cache_mask()` preserving local writeback-cache size/mtime/ctime.

Mount and connection APIs include `fuse_conn_init()`, `fuse_conn_put()`, `fuse_conn_get()`, `fuse_mount_remove()`, `fuse_conn_destroy()`, `fuse_mount_destroy()`, `fuse_fill_super_common()`, `fuse_fill_super()`, `fuse_get_tree()`, and submount-specific `fuse_init_fs_context_submount()`/`fuse_fill_super_submount()`. Device helpers are `fuse_dev_alloc()`, `fuse_dev_install()`, `fuse_dev_alloc_install()`, and `fuse_dev_put()`.

Negotiation is built around `struct fuse_init_args`, `fuse_new_init()`, `fuse_send_init()`, `process_init_reply()`, `process_init_limits()`, and request-timeout setup. Filesystem registration and module lifecycle are handled by `fuse_fs_init()`, `fuse_fs_cleanup()`, `fuse_sysfs_init()`, `fuse_sysfs_cleanup()`, `fuse_init()`, and `fuse_exit()`.

## Control Flow
Mount setup begins with `fuse_init_fs_context()`, which allocates `struct fuse_fs_context` and installs parser ops. `fuse_parse_param()` validates `fd`, `rootmode`, `user_id`, `group_id`, `default_permissions`, `allow_other`, `max_read`, `blksize`, and subtype. `fuse_get_tree()` allocates a new connection and mount, initializes the connection with `/dev/fuse` input queue ops, and either reuses an existing initialized connection for an already-installed device or creates a new nodev/block superblock.

`fuse_fill_super_common()` applies superblock defaults, allocates the syncfs bucket, handles block size and DAX setup, creates a private backing device info, sets mount policy into `fuse_conn`, creates the root inode and dentry, adds the connection to fusectl/global lists, and installs the fuse device if present. `fuse_fill_super()` then sends `FUSE_INIT`.

`fuse_new_init()` advertises supported kernel features. `fuse_send_init()` sends the init request synchronously or in the background depending on `sync_init`. `process_init_reply()` validates protocol major version, processes background limits, interprets feature flags, sets capability bits and no-op fallbacks, configures DAX/passthrough/idmap/io_uring/request-timeout support, adjusts readahead/max write/max pages/name length/time granularity, marks the connection initialized or errored, and wakes waiters blocked on initialization.

Inode lookup flows through `fuse_iget()`: submount points may get unhashed automount inodes with shared `fuse_submount_lookup`; normal inodes use `iget5_locked()` keyed by nodeid, initialize operations by file type, reject stale reused nodeids by marking old inodes bad and retrying, increment `nlookup`, and apply attributes. Eviction truncates pages, clears the inode, queues `FORGET` for accumulated lookups, drops submount lookup references, bumps `evict_ctr` for non-deleted inodes, and asserts regular-file writeback state is clean.

Unmount removes mounts from `fc->mounts`; the last mount sends optional `FUSE_DESTROY`, aborts the connection, waits for abort completion, removes fusectl/global list state, and drops the connection. Module init registers inode caches, fuse/fuseblk filesystems, sysctl, device, sysfs, fusectl, and dentry invalidation; exit reverses those steps.

## State And Persistence Behavior
This file owns the long-lived kernel state for the FUSE client. The inode cache stores `struct fuse_inode`. `fuse_conn_list` and `fuse_mutex` track active connections and fusectl visibility. `fuse_conn` persists negotiated capabilities, queues, device/mount membership, user namespace credentials, request timeout work, syncfs bucket, attr/evict counters, and abort state until all references drop through RCU.

Lookup persistence is maintained through `fi->nlookup` and queued `FORGET` messages. Attribute persistence is timeout/version based; writeback cache causes local size/mtime/ctime to override server replies. Submount lookup state uses shared refcounts to prevent premature final FORGET for auto-submount roots. Syncfs persistence uses a generation bucket so syncfs can wait for writepages submitted before the sync boundary.

## Dependencies And Integration Points
`inode.c` integrates the rest of the FUSE subsystem: `fuse_i.h`, `fuse_dev_i.h`, `dev_uring_i.h`, device operations, dentry operations from `dir.c`, file initialization from `file.c`, xattr handlers, DAX, passthrough backing files, fusectl, sysctl, sysfs, exportfs, fs_context, block-device mounting, pid/user namespaces, and Linux superblock/inode/page-cache APIs.

It registers `fuse_fs_type` and `fuseblk_fs_type`, exposes module aliases, and implements `super_operations` and export operations. It also supplies `fuse_umount_begin()`, `fuse_statfs()`, and `fuse_sync_fs()` to the VFS.

## Risks And Edge Cases
Mount and init negotiation are security-sensitive: `/dev/fuse` must come from the same user namespace, idmapped mounts are only allowed with default permissions, passthrough is refused with writeback cache or invalid stack depth, and unprivileged background limits are capped. Feature-flag interpretation changes behavior across many files, so incorrect negotiation can silently select unsafe cache, permission, DAX, or passthrough modes.

Lifecycle races include device close during mount, reused nodeids, inode eviction racing with lookup/readdirplus replies, submount duplicate roots, abort while background requests are outstanding, and RCU release of connections/mounts/buckets. `fuse_change_attributes_common()` must avoid accepting stale replies across evictions and must not overwrite locally authoritative writeback-cache fields. Module cleanup must flush RCU inode frees before destroying the cache.

## Test Signals
Important tests include mount option validation, wrong user namespace fd rejection, normal fuse and fuseblk mount/unmount, initialized-device remount reuse, FUSE_INIT feature negotiation for each flag, sync and async init paths, background limit clamping for unprivileged users, request timeout setup, root inode creation, nodeid reuse stale-inode behavior, FORGET accounting on eviction, reverse inode invalidation, NFS export handle encode/decode, auto-submount creation and teardown, syncfs bucket waiting, forced unmount abort behavior, DAX/passthrough/idmap combinations, and module init/exit cleanup ordering.
