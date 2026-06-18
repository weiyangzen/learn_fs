# sources/distributed-fs/ceph-client/fs/btrfs/tree-log.h

## Purpose

`tree-log.h` declares the public interface and per-fsync context for Btrfs tree logging. It is the boundary between the tree-log implementation in `tree-log.c` and the rest of the Btrfs filesystem code that needs to start safe dentry logging, sync/free/recover log trees, update logs after namespace operations, or mark cases that require a full transaction commit.

## Important APIs, types, and constants

- `BTRFS_NO_LOG_SYNC` is the special positive return value from `btrfs_log_dentry_safe()` meaning the target was already safely logged or no log sync is required.
- `BTRFS_LOG_FORCE_COMMIT` is a negative sentinel below normal errno space. It signals that the tree log cannot be used safely and the caller must commit the full transaction. The negative value is intentionally compatible with helpers that return error/false/true style results.
- `struct btrfs_log_ctx` carries one logging operation's mutable state:
  - `log_ret` and `log_transid` communicate the result and transaction ID of a log commit to waiters.
  - `log_new_dentries`, `logging_new_name`, and `logging_new_delayed_dentries` coordinate recursive logging of new names and delayed directory items.
  - `logged_before` caches whether the inode had already been logged in the current transaction.
  - `inode` is the primary inode being logged.
  - `list` links the context into a root's `log_ctxs[]` wait/result list.
  - `ordered_extents` tracks ordered extents included by fast fsync until they can be marked/logged and referenced correctly.
  - `conflict_inodes`, `num_conflict_inodes`, and `logging_conflict_inodes` track conflicting inodes found while logging names so the implementation can log them once without unbounded recursion.
  - `scratch_eb` is an optional reusable cloned/dummy extent buffer used while copying items to avoid allocation and lock-order hazards inside log transactions.
- `btrfs_init_log_ctx()`, `btrfs_init_log_ctx_scratch_eb()`, and `btrfs_release_log_ctx_extents()` initialize, optimize, and clean up the context.
- `btrfs_set_log_full_commit()` records that the current transaction must use a full commit for logging correctness.
- `btrfs_need_log_full_commit()` tests whether the current transaction has been marked for full commit.

## Exported control flow

The typical fsync caller creates and initializes a `btrfs_log_ctx`, prepares any ordered extent state, then calls `btrfs_log_dentry_safe()`. That routine may return `0` for a log that should be synced, `BTRFS_NO_LOG_SYNC` when no sync is needed, `BTRFS_LOG_FORCE_COMMIT` when a full transaction commit is required, or a real error. If logging succeeds and needs persistence, the caller invokes `btrfs_sync_log()` with the same context.

Namespace operations call the other exported hooks:

- `btrfs_del_dir_entries_in_log()` removes a logged directory entry after unlink/rename when the directory had already been logged.
- `btrfs_del_inode_ref_in_log()` removes logged inode backrefs/extrefs for an unlinked old name.
- `btrfs_record_unlink_dir()` marks an unlink/rename event before the tree is updated so later fsync decisions know when parent logging or full commit is required.
- `btrfs_record_snapshot_destroy()` and `btrfs_record_new_subvolume()` mark parent directories so snapshot/subvolume operations do not get represented by an unsafe partial log.
- `btrfs_log_new_name()` updates the log after link/rename adds a new name.

Transaction/mount integration uses:

- `btrfs_sync_log()` to commit a root log and update on-disk superblock log pointers.
- `btrfs_free_log()` and `btrfs_free_log_root_tree()` to discard log trees during full transaction commit cleanup.
- `btrfs_recover_log_trees()` to replay log trees during mount recovery.
- `btrfs_pin_log_trans()` and `btrfs_end_log_trans()` to hold off log sync while related log updates must be made atomically.

## State and persistence behavior

The header exposes both persisted-log operations and volatile coordination state. The log context itself is not persisted; it is a per-operation in-memory carrier used to connect log writers to log commit waiters and to preserve intermediate lists of ordered extents or conflicting inodes. Persistent effects happen through the implementation: copied log tree items, log root items, checksum items, superblock log-root pointers, and recovery replay into subvolume trees.

The inline full-commit flag helpers operate on `trans->fs_info->last_trans_log_full_commit`. This is an in-memory transaction-wide gate. Once set to the current transaction ID, subsequent logging attempts or log sync checks must fall back to a full transaction commit.

## Dependencies and integration points

The header depends on Linux list/VFS/fscrypt types and `transaction.h`, and forward-declares the Btrfs inode/root/transaction/ordered extent structures needed by callers. It is included by the tree-log implementation and by filesystem paths that perform fsync, transaction commit cleanup, mount recovery, unlink/rename/link handling, snapshot destruction, and subvolume creation.

## Risks and usage constraints

- Callers must interpret `BTRFS_LOG_FORCE_COMMIT` distinctly from normal errno values and must not attempt to sync an unsafe tree log after it is returned or after `btrfs_set_log_full_commit()` has been called.
- `btrfs_log_ctx` lists must be initialized before use and ordered extents must be released with `btrfs_release_log_ctx_extents()` on cleanup paths that collected them.
- The pin/end pair must be balanced. Failing to call `btrfs_end_log_trans()` after `btrfs_pin_log_trans()` or a joined log transaction can block log sync waiters.
- Namespace hooks rely on being called at the documented time relative to metadata updates. For example, record hooks that must run before unlink/snapshot/subvolume mutations lose correctness if called after the tree state has already changed.
- `scratch_eb` is an optimization and deadlock-avoidance aid owned by the context; callers that initialize it must ensure the implementation or final cleanup releases the extent buffer.

## Test signals

Header-level behavior is best tested through integration paths:

- fsync paths that return `BTRFS_NO_LOG_SYNC`, successful log sync, and `BTRFS_LOG_FORCE_COMMIT`.
- balanced initialization/cleanup of `btrfs_log_ctx` with ordered extents collected by fast fsync.
- rename/link/unlink tests that call the delete/new-name hooks and verify replay preserves only expected names.
- snapshot destroy and subvolume creation followed by parent fsync, verifying a full commit fallback.
- concurrent log pinning and sync tests that ensure `btrfs_pin_log_trans()`/`btrfs_end_log_trans()` coordination does not deadlock and waiters observe the correct `log_ret`.
