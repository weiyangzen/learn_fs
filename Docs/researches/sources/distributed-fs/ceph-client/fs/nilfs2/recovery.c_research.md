# sources/distributed-fs/ceph-client/fs/nilfs2/recovery.c

## Purpose

`recovery.c` implements NILFS2 mount-time log recovery. It validates segment summaries and super-root checksums, searches for the latest valid super root starting from superblock cursors, records newer orphan logs, and optionally rolls forward data-sync partial segments written after the latest checkpoint.

## Important APIs, Types, and Functions

Public functions are `nilfs_read_super_root_block()`, `nilfs_search_super_root()`, `nilfs_salvage_orphan_logs()`, and `nilfs_dispose_segment_list()`.

Internal helpers include `nilfs_compute_checksum()`, `nilfs_validate_log()`, summary-entry readers/skippers, `nilfs_scan_dsync_log()`, `nilfs_prepare_segment_for_recovery()`, `nilfs_recover_dsync_blocks()`, `nilfs_do_roll_forward()`, `nilfs_finish_roll_forward()`, and `nilfs_abort_roll_forward()`.

`struct nilfs_recovery_block` records a data block from a data-sync log: owning inode, physical block, virtual block number, file block offset, and list link. `struct nilfs_segment_entry` tracks full segments that should be marked active or disposed.

## Control Flow

`nilfs_search_super_root()` starts at `nilfs->ns_last_pseg` and `ns_last_seq`, reads segment summaries, validates magic, sequence, block count, and full-log CRC, then follows partial segments within a full segment and `ss_next` into subsequent segments. When it sees a valid super-root partial segment, it updates recovery info and the in-memory log cursor. If the filesystem was not clean, it scans newer logs to determine whether the super root was updated or whether roll-forward regions exist.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint root, calls `nilfs_do_roll_forward()`, and if data blocks were salvaged, prepares fresh recovery segments, attaches the log writer, constructs a new segment, then post-cleans the old recovery start block.

Roll-forward accepts only synchronous data logs (`NILFS_SS_SYNDT`) without super roots. It scans finfo/binfo records into recovery-block entries, then at log-end loads target inodes, performs `block_write_begin()`, copies saved block data from disk into the folio, marks the file dirty, and completes the write through normal block write paths. On failure, dirty recovery inodes are abandoned.

## State and Persistence Behavior

Recovery updates `struct the_nilfs` cursors: current segment number, next segment, segment sequence, checkpoint number, last super-root position, creation times, and pseg offset. It also manipulates the sufile to free invalidated next segments, scrap segments written after the latest super root, and allocate fresh segments for recovery output.

Roll-forward turns orphan data-sync log contents back into normal dirty file pages and persists them by constructing a new segment. `nilfs_finish_roll_forward()` zeros the old roll-forward start block when it shares the super-root segment, reducing the chance that stale orphan logs are replayed again.

## Dependencies and Integration Points

The file depends on buffer-head IO, block write helpers, CRC32, `segment.h`, `sufile.h`, `page.h`, `segbuf.h`, checkpoint/root attach, inode lookup, bmap write paths through `nilfs_get_block()`, and the log writer. It is part of mount/load flow invoked before the filesystem is fully available.

## Risks and Edge Cases

CRC and range checks bound reads, but summary parsing assumes valid `sumbytes`, finfo counts, and block counts once the log is accepted. Roll-forward only recovers data-sync logs; other orphan logs are ignored or treated as confusing. `nilfs_prepare_segment_for_recovery()` changes sufile state before constructing the recovery segment; later failure relies on destruction/abort cleanup rather than restoring the old sufile. Sequence/next-segment corruption can cause early termination or `-EINVAL` mount failure.

## Test Signals

Tests should include clean and unclean mounts, corrupted summary magic, sequence mismatch, bad full CRC, bad super-root CRC, truncated summary blocks, orphan data-sync logs with multiple files, roll-forward allocation failure, I/O failure while copying recovered blocks, and recovery after the next segment or active segment has an inconsistent sufile entry.
