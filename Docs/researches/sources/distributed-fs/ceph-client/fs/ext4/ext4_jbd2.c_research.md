# sources/distributed-fs/ceph-client/fs/ext4/ext4_jbd2.c

## Purpose
`ext4_jbd2.c` implements ext4's concrete wrappers around the JBD2 journal. It chooses per-inode data journaling mode, starts and stops transactions, handles no-journal mounts, reserves and extends credits, obtains metadata write/create access, forgets or revokes freed blocks, detects block-device writeback errors in no-journal mode, and dirties metadata buffers.

## Important APIs and functions
`ext4_inode_journal_mode()` returns one of `EXT4_INODE_JOURNAL_DATA_MODE`, `EXT4_INODE_ORDERED_DATA_MODE`, or `EXT4_INODE_WRITEBACK_DATA_MODE`. It falls back to writeback when no journal exists; selects full data journaling for non-regular files, EA inodes, journal-data mount mode, or per-inode journal-data flag without delayed allocation; downgrades encrypted regular-file data to ordered mode; and otherwise follows the mount data mode.

`__ext4_journal_start_sb()` checks mount/journal state, traces the start event, then either returns a no-journal pseudo-handle or calls `jbd2__journal_start()`. `__ext4_journal_stop()` drops no-journal pseudo-handles, stops real JBD2 handles, and reports transaction errors through `__ext4_std_error()`. `__ext4_journal_start_reserved()` starts a pre-reserved handle after rechecking mount state. `__ext4_journal_ensure_credits()` verifies available buffer and revoke credits and extends the transaction when needed.

`__ext4_journal_get_write_access()` and `__ext4_journal_get_create_access()` wrap JBD2 buffer access calls and attach metadata checksum triggers when requested and supported. `__ext4_forget()` chooses between buffer forget and journal revoke based on no-journal mode, metadata/data classification, full data journaling, and per-inode data journaling. `__ext4_handle_dirty_metadata()` marks buffers metadata/prioritized/uptodate and either journals them or directly marks/syncs them dirty on no-journal filesystems.

Internal helpers include `ext4_get_nojournal()` and `ext4_put_nojournal()`, which encode a nested no-journal reference count in `current->journal_info`; `ext4_journal_check_start()`, which rejects emergency, read-only, frozen, or aborted-journal states; `ext4_journal_abort_handle()`, which records `h_err` and aborts the JBD2 handle; and `ext4_check_bdev_write_error()`, which advances the block device errseq and reports asynchronous metadata writeback errors.

## Control flow
The normal mutation path starts by calling a macro from `ext4_jbd2.h`, which supplies function/line metadata and reaches `__ext4_journal_start_sb()`. That function calls `ext4_journal_check_start()`. If the filesystem has no journal or is in fast-commit replay, it creates/increments a no-journal pseudo-handle; otherwise it starts a JBD2 transaction with GFP_NOFS allocation and the caller's credit request.

Metadata update paths then call write/create access wrappers before changing buffer contents, optionally install checksum triggers, and later call `ext4_handle_dirty_metadata()` to journal or dirty the buffer. On any JBD2 access error, `ext4_journal_abort_handle()` records the error on the handle and aborts the transaction. Finally `ext4_journal_stop()` stops the handle and reports errors to the superblock error path.

Freeing blocks flows through `__ext4_forget()`. Without a valid handle, it clears and forgets the buffer after waiting for IO. With a real journal, full data journaling and non-journaled data blocks use `jbd2_journal_forget()`, while metadata and journaled data use `jbd2_journal_revoke()` so old metadata cannot be replayed after reuse.

## State and persistence behavior
Real JBD2 transactions persist metadata updates through the journal and track errors in `handle->h_err`. No-journal pseudo-handles provide a common calling convention but do not journal; direct dirtying and synchronous buffer writeback are used where required. The pseudo-handle refcount is stored in `current->journal_info` as a small integer, making nested no-journal scopes cheap but requiring strict balance.

Checksum trigger installation persists correct metadata checksums during journal commit for trigger types such as orphan-file blocks. Revoke records are persistence-critical: they prevent stale journal contents from resurrecting freed metadata/data blocks after crash recovery. Block-device errseq checking protects no-journal metadata writes from silently reusing stale buffers after asynchronous writeback errors.

## Dependencies and integration points
The file includes `ext4_jbd2.h` and `trace/events/ext4.h`, and calls into JBD2 APIs such as `jbd2__journal_start()`, `jbd2_journal_stop()`, `jbd2_journal_start_reserved()`, `jbd2_journal_extend()`, `jbd2_journal_get_write_access()`, `jbd2_journal_get_create_access()`, `jbd2_journal_forget()`, `jbd2_journal_revoke()`, and `jbd2_journal_dirty_metadata()`. It uses ext4 helpers from `ext4.h` for mount options, emergency state, metadata checksum features, buffer metadata tracking, error reporting, and inode flags.

## Risks and review notes
The journaling mode decision must stay aligned with delayed allocation, encryption, and data mode constraints. Accidentally enabling full data journaling with delayed allocation or encrypted regular files would violate assumptions elsewhere. No-journal pseudo-handles are pointer-like values below `EXT4_NOJOURNAL_MAX_REF_COUNT`; code must never pass NULL or arbitrary small values as real handles.

Credit handling is a common correctness risk. Underestimating buffer or revoke credits can force restart paths at unsafe points or fail metadata updates. Forget/revoke decisions are crash-consistency critical, especially for metadata blocks and journaled data. Error paths must preserve the first meaningful `h_err` and propagate failures to ext4's error machinery.

## Test signals
Important test signals include journal mode selection across mount modes, encrypted files, EA inodes, delayed allocation, and no-journal filesystems; nested no-journal start/stop balancing; aborted journal startup rejection; access wrapper trigger installation when metadata checksums are enabled; revoke vs forget behavior for metadata and data blocks; dirty metadata behavior with and without handles; and errseq-driven writeback error reporting.
