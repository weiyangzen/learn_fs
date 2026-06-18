# sources/distributed-fs/ceph-client/fs/ext2/super.c

## Purpose

`fs/ext2/super.c` is the ext2 VFS mount, superblock, quota, statistics, sync, freeze, remount, NFS export, inode-cache, and module-registration implementation. It turns an on-disk ext2 superblock and group descriptor table into an initialized `struct super_block`, validates core geometry and feature bits, wires ext2 operation tables into VFS, and persists mount-state transitions back to disk. It is the central integration point for ext2 block-device mounting in this source tree.

## Important APIs, types, and functions

- `ext2_error()`, `ext2_msg()`, and `ext2_msg_fc()` report filesystem and mount-context diagnostics. `ext2_error()` also marks the on-disk superblock with `EXT2_ERROR_FS`, syncs it, and optionally panics or remounts read-only according to `errors=`.
- `ext2_update_dynamic_rev()` upgrades revision-zero filesystems when newer compat features are enabled.
- `ext2_put_super()` releases quota state, xattr cache, group descriptor buffers, counters, DAX device references, and `struct ext2_sb_info`.
- `ext2_alloc_inode()`, `ext2_free_in_core_inode()`, `init_once()`, `init_inodecache()`, and `destroy_inodecache()` manage the `ext2_inode_cache` slab.
- `ext2_show_options()` reconstructs mount options for `/proc/mounts`.
- `ext2_sops` publishes VFS superblock callbacks: inode allocation/free, write/evict inode, put super, sync, freeze/unfreeze, statfs, show options, and optional quota IO.
- `ext2_export_ops`, `ext2_nfs_get_inode()`, `ext2_fh_to_dentry()`, and `ext2_fh_to_parent()` provide stable NFS file-handle lookup.
- `struct ext2_fs_context`, `ext2_param_spec`, and `ext2_parse_param()` implement the modern `fs_context` option parser for `sb=`, `errors=`, `dax`, `xip`, quotas, ACLs, user xattrs, reservation, grouping, uid/gid reservation, and legacy ignored options.
- `ext2_fill_super()` is the main mount routine. It allocates `ext2_sb_info`, reads the superblock, checks features and geometry, reads group descriptors, initializes counters/caches/reservation trees, reads the root inode, and installs VFS operations.
- `ext2_sync_super()`, `ext2_sync_fs()`, `ext2_freeze()`, `ext2_unfreeze()`, and `ext2_write_super()` keep superblock counters, timestamps, and validity state coherent on disk.
- `ext2_reconfigure()` implements remount option changes and read-only/read-write transitions.
- `ext2_statfs()` computes and caches metadata overhead and reports capacity/free inode data.
- Optional quota helpers `ext2_quota_read()`, `ext2_quota_write()`, `ext2_quota_on()`, and `ext2_quota_off()` expose quota file IO without pagecache locking assumptions.

## Control flow

Mount begins in `ext2_init_fs_context()`, which allocates parser state, seeds default reservation behavior for new mounts, or copies current options for reconfigure. `ext2_get_tree()` calls `get_tree_bdev()` with `ext2_fill_super()`. `ext2_fill_super()` then chooses an initial block size, reads the on-disk superblock at `ctx->s_sb_block`, verifies magic, applies parsed/default mount options, rejects unsupported incompat or read-write ro-compat features, handles DAX capability checks, rereads the superblock after block-size adjustment if needed, validates inode size, group sizes, block counts, inode counts, and descriptor placement, allocates descriptor arrays and free-count counters, creates the EA block cache, installs operation tables, reads and validates the root inode, warns for ext3 journal compat, updates mount counts/state, and writes the superblock.

Failure paths unwind in reverse order through labeled exits, releasing descriptor buffers, counters, xattr cache, superblock buffer, DAX references, and `sbi`. Unmount enters `ext2_put_super()`, which disables quotas, destroys the EA cache, restores `s_state` to the saved mount state for clean read-write unmount, syncs the superblock, and frees in-core structures.

Remount via `ext2_reconfigure()` first syncs the filesystem, builds a new option snapshot, refuses live DAX toggles, handles read-write to read-only by suspending quotas and restoring a valid on-disk state when appropriate, handles read-only to read-write by checking ro-compat features and rerunning setup, then commits option and POSIX ACL flag changes under `s_lock`.

## State and persistence behavior

Persistent state is centered on `struct ext2_super_block`: mount state, mount count, free block/inode counters, write time, feature bits, default mount options, reserved uid/gid, and UUID-backed fsid. Group descriptors persist bitmap and inode table locations and free counts maintained elsewhere. In-memory `ext2_sb_info` caches parsed options, descriptor buffers, group counts, overhead computations, reservation windows, percpu counters, xattr cache, DAX references, and lock state. `ext2_sync_fs()` intentionally clears `EXT2_VALID_FS` during normal mounted operation so an unclean shutdown is visible to fsck. `ext2_freeze()` restores the saved valid state only when there are no open unlinked files.

Quota persistence is through hidden quota files, with direct block IO through `ext2_get_block()` and explicit dirtying of quota file buffers and inode metadata. Xattr feature persistence is delegated to `xattr.c`, but this file creates and destroys the per-superblock mbcache and advertises `sb->s_xattr`.

## Dependencies and integration points

This file depends on Linux VFS superblock, inode, mount, `fs_context`, exportfs, quota, DAX, buffer-head, percpu-counter, seq_file, and block-device APIs. It integrates with ext2-specific inode/block helpers from `ext2.h`, xattr handlers from `xattr.h`, ACL mount options from `acl.h`, and NFS export parent lookup via `ext2_get_parent()`. It also surfaces module metadata through `file_system_type`, `module_init()`, and `module_exit()`.

## Risks and edge cases

The highest-risk paths are mount-time validation and remount transitions. Bad geometry, descriptor table locations, unsupported feature bits, invalid inode size, too-small groups, or device-size mismatches must fail before operation tables are exposed. `sb=` is ignored on remount by design, so tests must not expect it to move the superblock after initial mount. DAX is deprecated for ext2 and is disabled if the block device or block size is unsuitable. Error handling changes persistent state immediately, so `errors=panic`, `errors=remount-ro`, and failed superblock writes have visible operational consequences. Quota file IO bypasses normal pagecache expectations and depends on quota serialization.

## Test signals

Useful signals include mounting valid and deliberately malformed ext2 images; exercising rev0 images with feature bits; read-only and read-write mounts with unsupported ro-compat/incompat flags; DAX-capable and non-DAX devices; `errors=` behavior after injected metadata errors; freeze/unfreeze with and without unlinked open files; remount read-only/read-write with quota state; `statfs` overhead under sparse-super and non-sparse layouts; NFS file-handle stale generation checks; and quota read/write paths over holes, partial blocks, and sync inodes.
