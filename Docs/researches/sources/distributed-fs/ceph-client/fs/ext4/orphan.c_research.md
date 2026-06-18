# sources/distributed-fs/ceph-client/fs/ext4/orphan.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/orphan.c` implements crash-safe tracking and recovery of unlinked or truncating inodes. It supports both the legacy superblock singly linked orphan list and the newer orphan file feature, where orphan inode numbers live in checksummed blocks. The source was read as a complete 659-line file.

## Important APIs, Types, and Functions

The main public functions are `ext4_orphan_add()`, `ext4_orphan_del()`, `ext4_orphan_cleanup()`, `ext4_release_orphan_info()`, `ext4_orphan_file_block_trigger()`, `ext4_init_orphan_info()`, and `ext4_orphan_file_empty()`. Internal orphan-file helpers are `ext4_orphan_file_add()`, `ext4_orphan_file_del()`, `ext4_orphan_block_tail()`, and `ext4_orphan_file_block_csum_verify()`. `ext4_process_orphan()` performs the actual truncate or delete action during recovery.

## Control Flow

`ext4_orphan_add()` is called for zero-link inodes or inodes undergoing truncation. It skips non-journaled or bad inodes, asserts the caller has the needed inode serialization, and returns immediately if already tracked. If the orphan file is configured, `ext4_orphan_file_add()` first tries to reserve a free slot by decrementing per-block `ob_free_entries`, starting from a CPU-derived block index. It journals the chosen orphan-file block, atomically installs the inode number into a free slot, records `i_orphan_idx`, sets `EXT4_STATE_ORPHAN_FILE`, and dirties the block. If the orphan file is full, the code falls back to the legacy list by journaling the superblock and inode, linking the inode at `s_last_orphan`, and adding the inode to the in-memory `s_orphan` list under `s_orphan_lock`.

`ext4_orphan_del()` removes an inode from whichever format tracks it. For orphan-file entries, `ext4_orphan_file_del()` clears the slot, increments the free-entry counter, dirties the orphan-file block, clears state, and reinitializes the in-memory list node. For legacy entries, it removes the inode from the in-memory list, updates either `s_last_orphan` or the previous inode's `NEXT_ORPHAN`, clears the current inode link pointer, and marks metadata dirty.

`ext4_orphan_cleanup()` runs during mount recovery. It refuses cleanup without write access, with unsupported ro-compatible features, or on filesystems already in error state. It temporarily clears read-only state if needed and enables quotas so deletes and truncates account correctly. It walks the legacy `s_last_orphan` chain using `ext4_orphan_get()`, links each inode into the in-core list, then calls `ext4_process_orphan()`. It separately scans every nonzero orphan-file slot, restores orphan-file state into the inode, and processes it. Linked orphan inodes are truncated to `i_size`; zero-link inodes are deleted by the final `iput()`.

## State and Persistence Behavior

Legacy persistent state is `es->s_last_orphan` plus each orphan inode's `NEXT_ORPHAN` field. Orphan-file persistent state is the special orphan inode named by `s_orphan_file_inum`; its data blocks contain little-endian inode numbers and an `ext4_orphan_block_tail` with magic and optional checksum. In memory, `s_orphan_info.of_binfo[]` pins buffer_heads and atomic free counters for each orphan-file block, while each inode carries `i_orphan`, `i_orphan_idx`, and `EXT4_STATE_ORPHAN_FILE`.

Checksum updates for orphan-file blocks are integrated with JBD2 through `ext4_orphan_file_block_trigger()`, which computes a checksum from the orphan file checksum seed, disk block number, and slot array.

## Dependencies and Integration Points

This file depends on JBD2 metadata access, superblock checksum updates, ext4 inode lookup through `ext4_orphan_get()` and `ext4_iget()`, quota initialization and quota-on-mount, truncate/delete paths, orphan feature bits, metadata checksums, buffer-head lifetime management, and mount recovery. It is called by unlink, rmdir, truncate, tmpfile, failed-create cleanup, and mount setup/teardown.

## Risks and Edge Cases

The orphan file add path uses atomic free counters and `cmpxchg()` on slots; corrupt blocks or heavy concurrent slot churn can exhaust retry loops and intentionally fall back to the legacy list. Legacy list updates must not leave stray in-memory entries if journaling fails, because unmount checks can panic. Recovery must avoid clearing valid state on read-only or error mounts. A corrupt orphan file is rejected during `ext4_init_orphan_info()` if the file is too large, has bad block magic, or fails checksum verification.

## Test Signals

Useful tests include crash recovery after unlink of open files, crash during truncate, orphan-file and legacy-list mounts, orphan-file full fallback, quota-accounted orphan cleanup, readonly mount behavior, bad orphan block checksum or magic, ENOSPC during orphan add, and journal access failure during orphan delete. Observable signals are mount log counts for deleted orphan inodes and cleaned truncates, `EXT4_STATE_ORPHAN_FILE` transitions, empty orphan-file checks, and fsck cleanliness after forced crashes.
