# sources/distributed-fs/ceph-client/fs/fat/fatent.c

## Purpose
`fatent.c` implements low-level FAT table entry access for FAT12, FAT16, and FAT32, plus cluster allocation, cluster freeing, free-space counting, and discard/trim support. It is the persistence engine for file cluster chains.

## Important APIs, Types, and Functions
- `struct fatent_operations` abstracts FAT variant behavior: entry block calculation, pointer setup, buffer reads, get/put, and next-entry iteration.
- FAT12-specific access uses `fat12_entry_lock` because 12-bit entries can straddle bytes and block boundaries.
- `fat_ent_access_init()` selects `fat12_ops`, `fat16_ops`, or `fat32_ops` and initializes `sbi->fat_lock`.
- `fat_ent_read()` reads a specific FAT entry, reusing buffers where possible.
- `fat_ent_write()` writes one entry, optionally syncs buffers, and mirrors changes to backup FATs.
- `fat_alloc_clusters()` scans for free entries, builds an EOF-terminated chain, updates free-space accounting, and mirrors dirty FAT buffers.
- `fat_free_clusters()` walks a chain, marks entries free, optionally issues discard, and updates FSINFO state.
- `fat_count_free_clusters()` and `fat_trim_fs()` perform full FAT scans with readahead.

## Control Flow
All modifying cluster operations take `sbi->fat_lock`. Entry reads compute the FAT sector and byte offset, then either update the current `fat_entry` pointer if the same buffer still contains the entry or read new buffer heads. Writes call the variant `ent_put()` function, sync if requested, then copy dirty FAT sectors to all mirrored FAT tables.

Allocation starts near `sbi->prev_free + 1`, wraps at `max_cluster`, and scans until enough `FAT_ENT_FREE` entries are found or the table is exhausted. Each found entry is immediately marked EOF, and the previous allocated entry is pointed to the new entry to form a chain. On error after partial allocation, the new chain is freed. Freeing reads the next link, optionally batches discard, marks the current entry free, mirrors/syncs batched buffers, and stops at EOF.

## State and Persistence
Persistent state is the FAT table and its mirrors. Volatile superblock state includes `prev_free`, `free_clusters`, and `free_clus_valid`; when changed for FAT32, `mark_fsinfo_dirty()` marks the FSINFO inode for later writeback. FAT12/16/32 EOF marker encodings are normalized to `FAT_ENT_EOF` on read and translated back on write.

## Dependencies and Integration Points
This file depends on `fat.h`, buffer-head IO, block discard APIs, scheduler signal/resched checks, and metadata buffer tracking. It is used by `cache.c` for chain reads, `misc.c` for appending chains, `file.c` and `inode.c` for truncate/allocation, `dir.c` for directory growth, and `fat_generic_ioctl(FITRIM)` for discard.

## Risks and Test Signals
FAT12 entries crossing block boundaries require two buffer heads and careful locking. Mirrored FAT updates can fail after the primary FAT was changed, causing possible on-disk inconsistency. The allocation scan is linear and can be expensive on fragmented or nearly full volumes. Tests should cover FAT12/16/32 allocation/truncate, mirrored FATs, fsck after simulated sync failures, fallocate rollback, and `fstrim`.
