# sources/distributed-fs/ceph-client/fs/ext4/fsync.c

## Purpose
`fsync.c` implements ext4's `fsync`, `fdatasync`, and msync-backed file synchronization path. It chooses between no-journal metadata flushing and journal/fast-commit synchronization, handles parent directory persistence for just-created entries in no-journal mode, and issues block-device cache flushes when required for ordering.

## Important APIs, types, and functions
The exported entry point is `ext4_sync_file`. Internal helpers are `ext4_sync_parent`, `ext4_fsync_nojournal`, and `ext4_fsync_journal`. The implementation uses `mmb_fsync_noflush`, `mmb_sync`, `sync_inode_metadata`, `ext4_write_inode`, `file_write_and_wait_range`, `ext4_fc_commit`, `ext4_force_commit`, `jbd2_trans_will_send_data_barrier`, `blkdev_issue_flush`, and `file_check_and_advance_wb_err`.

## Control flow
`ext4_sync_file()` first rejects emergency state, asserts that the caller has no open journal handle, traces entry, and returns quickly for read-only filesystems except for writeback-error reporting. Without a journal, it syncs metadata buffer lists for the target range, forces inode-table writeout, recursively syncs freshly created parent directories while `EXT4_STATE_NEWENTRY` remains set, and requests a cache flush if barriers are enabled. With a journal, it writes and waits file data for the requested range, then calls `ext4_fsync_journal()`. Regular files can use `ext4_fc_commit()` for the relevant sync or datasync tid; directories and special files force a full commit because fast commit does not support them. If JBD2 will not send a data barrier for the transaction, ext4 issues its own flush.

## State and persistence behavior
Persistent ordering is the whole purpose of this file. No-journal mode explicitly writes metadata buffers, inode table blocks, and parent directory metadata to reduce crash windows for new entries. Journal mode persists data before metadata commit and relies on JBD2 or fast commit to make inode changes durable. `file_check_and_advance_wb_err()` advances per-file writeback error cursors so delayed I/O errors are reported once.

## Dependencies and integration points
It integrates VFS fsync, ext4 metadata buffer tracking, inode state flags, JBD2 transactions, fast commit, block-device flushes, and tracepoints. It is referenced by `ext4_file_operations.fsync` in `file.c`.

## Risks and test signals
Risks include missing parent syncs in no-journal mode, overusing fast commit for unsupported inode types, incorrect datasync versus full-sync tid selection, missing flushes when barriers are enabled, and lost writeback errors. Test signals include fsync/fdatasync on regular files, directories, symlinks and special files, no-journal newly-created files with nested fresh parents, barrier and nobarrier mounts, external journal behavior, fast-commit enabled/disabled/ineligible paths, forced shutdown/emergency state, and delayed writeback error propagation.
