# sources/distributed-fs/ceph-client/fs/ocfs2/journal.h

## Purpose
`journal.h` defines OCFS2 journaling state, transaction APIs, recovery entry points, checkpoint helpers, journal access types, and credit calculation helpers. It is the central header for mutation accounting and JBD2 integration across OCFS2.

## Important APIs, types, and functions
- `enum ocfs2_journal_state` models free, loaded, and shutdown journal states.
- `struct ocfs2_journal` stores the JBD2 journal pointer, journal inode, journal dinode buffer, transaction counters, transaction barrier, checkpoint waitqueue, and recovery cleanup work.
- `struct ocfs2_recovery_map` records node numbers pending recovery.
- Inline helpers `ocfs2_inc_trans_id()`, `ocfs2_set_ci_lock_trans()`, `ocfs2_ci_fully_checkpointed()`, `ocfs2_ci_is_new()`, `ocfs2_inode_is_new()`, and `ocfs2_ci_set_new()` manage transaction ids on metadata caches.
- Prototypes cover journal lifecycle, recovery, transaction handling, journal access variants, dirtying, and orphan scan setup.
- Credit macros and inline calculators define worst-case metadata credits for inode updates, quotas, allocation, truncation, mkdir/link/unlink/rename, xattrs, directory indexes, refcount trees, extent extension, symlink creation, and block group allocation.
- `ocfs2_jbd2_inode_add_write()`, `ocfs2_begin_ordered_truncate()`, and `ocfs2_update_inode_fsync_trans()` wrap ordered-data and fsync tracking hooks.

## Control flow
Callers start a transaction with `ocfs2_start_trans()` using a credit count from this header, request access through the typed `ocfs2_journal_access_*()` helper matching the metadata block type, modify the buffer, mark it dirty, and commit. Metadata locks consult transaction ids maintained here to decide when it is safe to downconvert or release locks. Inode clear can call `ocfs2_checkpoint_inode()` to kick the commit thread and wait until the inode cache transaction is fully checkpointed.

## State and persistence behavior
The header defines in-memory journal state and transaction-id bookkeeping rather than disk layout, but the APIs declared here are responsible for persisting all metadata updates through JBD2. Credit macros indirectly protect persistent consistency by ensuring transactions reserve enough space before mutating related disk structures.

## Dependencies and integration points
It includes Linux `fs.h` and `jbd2.h` and relies on OCFS2 inode and metadata cache helpers from surrounding includes. It is used by inode, allocation, xattr, directory, refcount, quota, resize, mmap, and ioctl/move-extents code.

## Risks and edge cases
- Incorrect credit calculations can cause transaction extension/restart in paths that hold locks, increasing deadlock risk.
- `trans_inc_lock` serializes transaction id observations and updates; callers must not bypass helpers.
- `ocfs2_checkpoint_inode()` can wait longer than expected if new metadata is added after the single checkpoint kick, which is called out in comments.
- Typed journal access should be used whenever metadata ECC applies; generic access leaves checksum management to the caller.

## Test signals
Compile and runtime tests should exercise credit helpers on different block/cluster sizes, metadata ECC trigger coverage for each typed access function, transaction id wrap avoidance, checkpoint waits for dirty inode caches, ordered truncate/write tracking, and quota feature combinations in credit calculations.
