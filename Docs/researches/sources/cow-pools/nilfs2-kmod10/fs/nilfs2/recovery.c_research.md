# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/recovery.c

## Purpose

Implements NILFS2 mount-time recovery: validating segment logs, locating the latest valid super root, salvaging data-sync logs after the latest checkpoint, preparing segments for recovery writes, and cleaning up failed roll-forward attempts.

## Main Responsibilities

- Validates segment summaries and super roots with magic, sequence, consistency, and CRC checks.
- Reads summary records across summary blocks.
- Scans data-sync logs for recoverable data blocks.
- Replays recoverable data blocks into current inodes using normal block write helpers.
- Searches forward from the superblock’s last partial segment to find the latest valid super root and records orphan log ranges.
- Allocates/scraps/free segments in sufile so recovery can safely write a new checkpoint after roll-forward.
- Aborts roll-forward by dropping dirty inodes if recovery fails.

## Important Types

- Segment check result enum classifies validation failures.
- `struct nilfs_recovery_block` records inode number, disk block number, virtual block number, and file block offset for a salvaged data block.
- `struct nilfs_segment_entry` records segment numbers found while scanning.

## Important Functions

- `nilfs_warn_segment_error()` maps internal segment validation failures to logs and errno.
- `nilfs_compute_checksum()` computes CRC across contiguous disk blocks, starting at a byte offset in the first block.
- `nilfs_read_super_root_block()` reads and optionally validates a super root block checksum.
- `nilfs_validate_log()` checks segment summary magic, sequence, block count, and full payload checksum.
- `nilfs_read_summary_info()` and `nilfs_skip_summary_info()` walk variable-length summary data across summary blocks.
- `nilfs_scan_dsync_log()` extracts recoverable data block descriptors from data-sync log summaries.
- `nilfs_prepare_segment_for_recovery()` frees/scraps affected segments and allocates a new segment for the recovery checkpoint.
- `nilfs_recover_dsync_blocks()` loads target inodes, writes salvaged block contents into page cache, marks files dirty, and completes block writes.
- `nilfs_do_roll_forward()` scans orphan logs after the latest super root and replays complete data-sync logs.
- `nilfs_salvage_orphan_logs()` attaches the latest checkpoint root, performs roll-forward, writes a recovery segment if needed, and detaches the writer.
- `nilfs_search_super_root()` scans partial segments to find the latest valid super root and populate recovery info.

## Dependencies and Interactions

- Uses `kern_feature.h` compatibility write helpers for roll-forward writes.
- Uses `nilfs_get_block()`, `nilfs_write_failed()`, and `nilfs_set_file_dirty()` from `inode.c`.
- Uses sufile APIs to free, scrap, and allocate recovery segments.
- Uses segment writer APIs to attach/detach log writer and construct the recovery segment.
- Uses `segbuf.h` for segment-buffer/log concepts and NILFS on-disk segment summary structures.

## Notable Behaviors and Edge Cases

- Super root checksum validates only `sr_bytes`, and invalid byte counts are treated as checksum failure.
- Segment log validation bounds `ss_nblocks` by blocks per segment before CRC reads.
- Roll-forward only accepts data-sync logs without super roots; unexpected super-root flags or non-data-sync continuation cause `-EINVAL`.
- Data recovery is best-effort per block; individual failures are logged and the first error is returned after processing.
- If roll-forward salvages blocks, recovery writes a new segment and then zeroes the old first orphan-log block when it shares the super-root segment.
- `nilfs_search_super_root()` performs readahead across current and next full segments while scanning.
- A mounted clean filesystem can stop at the first valid super root; an unclean state scans newer logs to detect needed recovery.
