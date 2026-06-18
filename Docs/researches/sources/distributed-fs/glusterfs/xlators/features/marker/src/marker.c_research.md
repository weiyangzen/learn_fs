# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker.c

## Purpose

`marker.c` implements the GlusterFS marker translator. It sits above one child translator and augments successful filesystem operations with quota accounting metadata and geo-replication xtime markers. It is responsible for maintaining quota xattrs, converting public quota keys to versioned internal keys, filtering internal marker xattrs from ordinary clients and healers, exposing the volume mark timestamp to geo-replication, and driving background or foreground quota transactions after namespace and file-size changes.

## Important APIs, Types, and Functions

The public translator entry points are the `fops` table: `marker_lookup`, `marker_create`, `marker_mkdir`, `marker_writev`, `marker_truncate`, `marker_ftruncate`, `marker_symlink`, `marker_link`, `marker_unlink`, `marker_rmdir`, `marker_rename`, `marker_mknod`, `marker_setxattr`, `marker_fsetxattr`, `marker_setattr`, `marker_fsetattr`, `marker_removexattr`, `marker_getxattr`, `marker_readdirp`, `marker_fallocate`, `marker_discard`, and `marker_zerofill`. Lifecycle hooks are `init`, `reconfigure`, `fini`, `mem_acct_init`, and inode cleanup through `marker_forget`.

Key helpers include `marker_key_replace_with_ver` and `marker_key_set_ver` for quota xattr version mapping, `marker_filter_internal_xattrs` and `marker_filter_gsyncd_xattrs` for response filtering, `marker_xtime_update_marks` and `marker_start_setxattr` for recursive xtime stamping, `marker_do_xattr_cleanup` and `quota_xattr_cleaner` for privileged quota cleanup, and the multi-step rename helpers `marker_get_oldpath_contribution`, `marker_do_rename`, `marker_rename_cbk`, `marker_rename_unwind`, and `marker_rename_done`.

## Control Flow

Most fops follow the same pattern: if marker features are disabled they wind straight to `FIRST_CHILD(this)`; otherwise they allocate `marker_local_t`, copy the relevant `loc_t` or synthesize one from an fd inode, wind the child fop, unwind to the caller in the callback, and only then run quota or xtime side effects. Create-like operations allocate quota inode context and create quota xattrs. Write/truncate/fallocate/discard/zerofill call `mq_initiate_quota_txn` with post-operation stat data. Link and create add contribution xattrs, while unlink and rmdir often run `mq_reduce_parent_size_txn` in the foreground using a callback stub so the caller is not unwound before accounting completes.

Rename is the most complex path. With quota enabled it allocates locals for old and new paths, takes an inode lock on the old parent using a separate root-uid frame, reads the old contribution xattr, performs the rename, removes the old-parent contribution xattr from the renamed inode, unwinds the original rename, releases the old-parent lock, subtracts old and overwritten-destination contributions, and finally creates a new contribution under the destination parent. The in-file comment explicitly documents this ordering to avoid stale parent contribution updates while inode parentage changes.

Xtime flow is asynchronous. After a successful mutation, `marker_xtime_update_marks` skips defrag and ordinary gsyncd calls unless `gsync-force-xtime` is enabled, records current seconds/useconds in network order, refs the local, creates a new frame, sets the marker xattr on the current location, and recursively traverses parent locations until root.

## State and Persistence Behavior

Persistent state is stored as extended attributes under `trusted.glusterfs`, including quota size/limit keys and per-volume xtime keys of the form `trusted.glusterfs.<volume-uuid>.xtime`. The volume mark exposed to geo-replication is derived from the configured `timestamp-file` mtime. `call_from_sp_client_to_reset_tmfile` lets the gsyncd client reset that timestamp by setting `trusted.glusterfs.volume-mark` to empty or `RESET`.

In-memory state includes `marker_conf_t` in `this->private`, the `marker_local_t` pool for inflight fops and nested marker frames, and inode context that stores quota state. `marker_local_unref` owns cleanup of copied locs, held xdata, nested lock frames, and chained operation locals. Quota versioning is controlled by the `quota-version` option; positive versions rewrite external xattr names to versioned internal keys before winding requests and rewrite them back on callback.

## Dependencies and Integration Points

This file integrates tightly with `marker-quota.h`, `marker-quota-helper.h`, `marker-common.h`, `libxlator.h`, syncop helpers, Gluster dict/xattr APIs, call stubs, inode contexts, frame ownership, and default unwind/wind infrastructure. It depends on child translators supporting ordinary fops, `getxattr`/`setxattr`/`removexattr`, `inodelk`, `readdirp`, and syncop list/remove xattr calls. Geo-replication is identified by `GF_CLIENT_PID_GSYNCD`; quota and heal integration use request/response xdata such as link-count keys and internal quota patterns.

## Risks and Edge Cases

The main risks are ordering and ownership bugs around asynchronous side effects. Rename relies on precise lock, xattr-removal, inode-table unwind, and contribution-update ordering. Several paths unwind to the caller before background quota or xtime work, so failures can leave delayed repair needs. `marker_error_handler` treats ENOSPC during marker xattr propagation as indexing corruption and removes the timestamp file, forcing geo-replication revalidation. Root, gsyncd, defrag, DHT linkfile, hardlink, and `GLUSTERFS_MARKER_DONT_ACCOUNT_KEY` cases all alter accounting behavior. Dictionary ownership is also sensitive because requests may be copied, refed, rewritten, or newly allocated.

## Test Signals

Useful tests include translator initialization/reconfigure with quota, inode-quota, xtime, gsync-force-xtime, bad UUID, and quota-version values; create/mkdir/mknod/symlink/link/write/truncate/unlink/rmdir/rename accounting with xattr inspection; rename under concurrent writes and existing destination files; gsyncd volume-mark get/set behavior; non-gsyncd filtering of xtime and internal quota xattrs; quota cleanup command permission checks; ENOSPC and missing-parent fault injection; and readdirp/lookup paths that create inode quota contexts and request versioned xattrs.
