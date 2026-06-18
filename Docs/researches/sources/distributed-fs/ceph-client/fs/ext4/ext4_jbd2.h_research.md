# sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.h

## Purpose
`ext4_jbd2.h` is the public ext4-internal journaling interface. It declares transaction credit formulas, handle operation type identifiers, inode dirtying entry points, wrapper macros that capture callsite information, no-journal handle semantics, transaction start/stop/restart helpers, fsync transaction tracking, data journaling mode predicates, revoke-credit calculations, dioread-nolock eligibility, and journal teardown.

## Important APIs, types, and constants
`EXT4_JOURNAL(inode)` retrieves `EXT4_SB(inode->i_sb)->s_journal`. Transaction credit macros include `EXT4_SINGLEDATA_TRANS_BLOCKS()`, `EXT4_XATTR_TRANS_BLOCKS`, `EXT4_DATA_TRANS_BLOCKS()`, `EXT4_META_TRANS_BLOCKS()`, `EXT4_MAX_TRANS_DATA`, `EXT4_RESERVE_TRANS_BLOCKS`, `EXT4_INDEX_EXTRA_TRANS_BLOCKS`, quota credit macros, and `EXT4_MAXQUOTAS_*` aggregations. These formulas encode how many journal credits typical data, xattr, quota, directory-index, and metadata operations should reserve.

Handle type constants `EXT4_HT_*` classify transaction callers for logging and diagnostics. Inode write APIs include `ext4_reserve_inode_write()`, `ext4_mark_iloc_dirty()`, `ext4_mark_inode_dirty()`, `__ext4_mark_inode_dirty()`, and `ext4_expand_extra_isize()`.

The core wrapper declarations correspond to implementations in `ext4_jbd2.c`: `__ext4_journal_get_write_access()`, `__ext4_forget()`, `__ext4_journal_get_create_access()`, `__ext4_handle_dirty_metadata()`, `__ext4_journal_start_sb()`, `__ext4_journal_stop()`, `__ext4_journal_start_reserved()`, and `__ext4_journal_ensure_credits()`. Macros such as `ext4_journal_get_write_access()`, `ext4_forget()`, and `ext4_handle_dirty_metadata()` attach `__func__` and `__LINE__`.

Inline helpers cover handle validation, sync marking, abort testing, revoke credit calculation, starting transactions from a superblock or inode, extending/restarting transactions, ensuring credits with optional cleanup callback, querying blocks per folio, forcing commits, registering inode write/wait ranges with JBD2, tracking fsync transaction ids, checking data journaling mode, computing data revoke credits, checking direct-IO read no-lock eligibility, and destroying a journal.

## Control flow
Callers normally use `ext4_journal_start()`, `ext4_journal_start_sb()`, `ext4_journal_start_with_reserve()`, or `ext4_journal_start_with_revoke()` to obtain a handle with typed credits and default revoke credits. The wrappers funnel into `__ext4_journal_start_sb()` in the `.c` file. Metadata buffers are protected with access wrappers and finalized with `ext4_handle_dirty_metadata()`. Long operations use `ext4_journal_ensure_credits()` or `ext4_journal_ensure_credits_fn()` to extend or restart transactions when credits run low.

`ext4_journal_ensure_credits_fn()` is a control-flow macro with a local label. It first calls `__ext4_journal_ensure_credits()`. If the current handle has enough credits or extension succeeds, it returns that status. If a restart is needed, it executes the caller-provided cleanup expression, restarts the journal with the requested credits, and returns `1` on successful restart.

`ext4_journal_destroy()` coordinates teardown by setting `EXT4_MF_JOURNAL_DESTROY`, forcing a commit, flushing pending superblock update work, destroying the JBD2 journal, and clearing `sbi->s_journal`.

## State and persistence behavior
This header defines how ext4 accounts for journal capacity before persistent metadata changes. The credit formulas are conservative persistence contracts: they reserve space for inode blocks, bitmaps, group descriptors, superblock summaries, xattrs, quotas, extent tree levels, and revoke records. `ext4_free_metadata_revoke_credits()` scales revoke credits by cluster ratio because freeing metadata blocks may free clusters under bigalloc.

`ext4_update_inode_fsync_trans()` stores the current transaction id in `i_sync_tid` and optionally `i_datasync_tid`, linking inode fsync behavior to JBD2 transaction persistence. `ext4_jbd2_inode_add_write()` and `ext4_jbd2_inode_add_wait()` register byte ranges that JBD2 must write or wait on for ordered semantics.

No-journal handles are explicitly treated as invalid by `ext4_handle_valid()`, allowing most wrappers to become no-ops while keeping callers structurally identical. Data journaling mode predicates drive persistence ordering: full data journaling writes data through the journal, ordered mode orders data before commit, and writeback mode does not provide data-before-metadata ordering.

## Dependencies and integration points
The header depends on Linux VFS and JBD2 headers plus `ext4.h`. It integrates with inode, xattr, directory, truncate, quota, resize, migrate, move-extents, writepage, and extent-conversion code through handle type constants and credit formulas. It also coordinates with superblock error update work and mount flags for journal destruction.

## Risks and review notes
Transaction credit formulas are easy to under-maintain when metadata formats evolve. Adding extent tree levels, quota behavior, xattr writes, or directory-index operations without updating credits can cause hard-to-reproduce ENOSPC or journal restart failures. Conversely, over-reserving credits reduces concurrency and journal capacity.

The handle validity scheme depends on no-journal pseudo-handles being small integer values and real JBD2 pointers not occupying that range. Callers must use `ext4_handle_valid()` before dereferencing a handle. `ext4_should_dioread_nolock()` deliberately rejects non-regular, non-extent, journal-data, and non-delalloc cases because those paths conflict with direct IO assumptions and JBD2 use of `b_private`.

`ext4_journal_destroy()` assumes only the commit thread and superblock update work can still operate on the journal at teardown. Reordering that sequence could leave queued work using a destroyed journal.

## Test signals
Useful tests cover credit formulas under extents vs indirect files, quota enabled/disabled, revoke credit calculations with bigalloc cluster ratios, no-journal handle validation, `ext4_journal_ensure_credits_fn()` restart behavior, fsync transaction id updates, `ext4_should_dioread_nolock()` gating, data journaling predicates, and journal destroy ordering with pending superblock update work.
