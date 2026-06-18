# sources/distributed-fs/glusterfs/xlators/features/marker/src/marker-quota.c

## Purpose
`marker-quota.c` implements quota xattr maintenance for the marker translator. It keeps directory size/file/dir-count xattrs and per-parent contribution xattrs consistent after creates, writes, renames, deletes, and lookup-driven self-heal.

## Important APIs, Types, And Functions
The central exported APIs are `mq_req_xattr`, `mq_xattr_state`, `mq_initiate_quota_txn`, `mq_initiate_quota_blocking_txn`, `mq_create_xattrs_txn`, `mq_reduce_parent_size_txn`, and `mq_forget`. Supporting operations include context status setters, `mq_build_ancestry`, `quota_dict_set_size_meta`, metadata math (`mq_compute_delta`, `mq_add_meta`, `mq_sub_meta`), xattr checks and creation (`mq_are_xattrs_set`, `mq_create_size_xattrs`), locking (`mq_lock`), dirty flag operations, metadata reads, contribution/size updates, synctask wrappers, transaction prevalidation, dirty-directory rebuild, and xattr inspection for files and directories.

## Control Flow
Quota updates are usually asynchronous synctasks. `mq_prevalidate_txn` rejects unsupported inode types, DHT linkfiles, missing gfids, and missing contexts, then copies a `loc_t` and resolves parent state. `mq_create_xattrs_txn` serializes create-xattr work using `create_status`, possibly creates a contribution node, and runs `mq_create_xattrs_task`; that task locks directories, checks existing xattrs, creates missing size xattrs, and starts a blocking quota transaction if needed.

`mq_initiate_quota_task` walks from a changed child up to root. At each level it resolves/validates the parent, locks the parent with an inode lock, gets or creates the child contribution node, computes delta between current size and contribution, marks the parent dirty with get-and-set xattrop, updates the child contribution xattr, updates the parent size xattr, clears dirty when safe, unlocks, then repeats upward. `mq_reduce_parent_size_task` handles unlink/rename removal by subtracting a child contribution from its old parent and optionally removing the contribution xattr. `mq_update_dirty_inode_task` heals a dirty directory by scanning children with `readdirp`, summing their contribution xattrs, comparing with the directory size xattr, and applying the delta.

Lookup inspection flows through `mq_xattr_state`. It ensures contribution nodes exist, inspects directory or file xattrs, seeds in-memory quota context from trusted xattrs, creates missing xattrs, triggers dirty healing, or starts quota updates when contribution and size diverge.

## State And Persistence Behavior
In-memory quota state is stored in `quota_inode_ctx_t` and `inode_contribution_t`. Persistent state is in trusted xattrs: size metadata under `QUOTA_SIZE_KEY` with optional version suffix, contribution metadata under `trusted.glusterfs.quota.<parent-gfid>.contri`, and dirty state under `trusted.glusterfs.quota.dirty`. Size and contribution metadata use endian-converted `quota_meta_t` arrays with xattrop add semantics. Dirty flags allow lookup-time repair after partial failures.

## Dependencies And Integration Points
The file depends on GlusterFS dict, syncop lookup/xattrop/setxattr/removexattr/inodelk/readdirp/opendir APIs, quota common utilities, marker private config (`marker_conf_t`), inode/path helpers, synctasks, call stubs, and helper APIs from `marker-quota-helper.c`. It integrates with `marker.c`, which calls these transaction functions from FOP callbacks.

## Risks And Edge Cases
The hardest risks are concurrency and partial updates across ancestor chains. Parent changes during rename are explicitly revalidated after locking, but races with parallel removes can still abort and rely on later healing. Dirty flag cleanup is subtle: failures clear in-memory dirty status so future lookup can retry. Rollback after parent size update failure only rolls back contribution xattrs, so error handling depends on dirty repair. Hard-link behavior is acknowledged as needing revisit. Long key generation, missing parent locs, stale inodes, and versioned quota keys are additional edge cases.

## Test Signals
High-value tests include create-xattr bootstrapping for files and directories, write delta propagation to root, unlink and rename parent reduction, hard-link contributions, dirty directory rebuild via readdirp, upgrade cases without inode-quota xattrs, DHT linkfile skips, parent-change races, and failure injection around xattrop/removexattr/lock acquisition.
