# sources/distributed-fs/ceph-client/fs/ntfs/aops.c

## Purpose

`aops.c` implements NTFS address-space operations and page-cache handling. It provides folio read, readahead, writeback, block mapping, swap activation, and NTFS-specific read completion zeroing around initialized size, mostly through Linux iomap helpers.

## Important APIs, Types, and Functions

Important functions are `ntfs_read_folio()`, `ntfs_bmap()`, `ntfs_readahead()`, `ntfs_writepages()`, `ntfs_swap_activate()`, and the read completion helpers `ntfs_iomap_read_end_io()` and `ntfs_iomap_bio_submit_read()`. Exported operation tables are `ntfs_aops` and `ntfs_mft_aops`. The file defines `ntfs_iomap_bio_read_ops` to plug NTFS-specific bio completion into generic iomap read logic.

## Control Flow

Reads call `ntfs_read_folio()`, which rejects encrypted attributes, delegates compressed nonresident data streams to `ntfs_read_compressed_block()`, and otherwise calls `iomap_read_folio()` with NTFS read iomap ops. Submitted bios complete through `ntfs_iomap_read_end_io()`, which converts block status, iterates folios, zeroes bytes beyond `initialized_size` within partially initialized ranges, and finalizes folio read state. Readahead skips resident and compressed files, then calls `iomap_readahead()`. Writeback rejects shutdown volumes, ignores resident attributes, rejects encrypted files, and calls `iomap_writepages()`. `ntfs_bmap()` maps initialized, nonresident, nonencrypted, non-MST-protected data blocks from VCN to LCN under the runlist lock and returns device block numbers or zero for holes/errors.

## State and Persistence Behavior

The file operates on page-cache folios and NTFS inode state. It reads `initialized_size` and `i_size` under `size_lock`, reads runlists under `runlist.lock`, and uses volume geometry to convert clusters to block units. It does not persist metadata itself, but writeback through `ntfs_writeback_ops` persists dirty page-cache data. `ntfs_mft_aops` uses `ntfs_mft_writepages` for MFT-specific persistence.

## Dependencies and Integration Points

It depends on NTFS inode/volume helpers, runlist mapping, compression support, debug logging, iomap read/writeback/swap helpers, Linux writeback, folio, bio, and address-space APIs. Operation tables are installed on NTFS inodes by the broader NTFS inode/superblock code.

## Risks and Edge Cases

Encrypted I/O is unsupported and must fail consistently. Compressed streams bypass generic iomap read and lack readahead here. Reads crossing initialized size must zero the uninitialized tail to avoid stale data exposure. `bmap()` cannot distinguish holes from errors or a real physical block zero, so it logs and returns zero. Large physical block numbers can truncate on narrow `sector_t`. Writeback during volume shutdown returns `-EIO`.

## Test Signals

Signals include generic fsx/xfstests-style buffered read/writeback, sparse file reads, initialized-size boundary reads, compressed file reads, encrypted-file error paths, readahead behavior on resident/compressed/nonresident files, `bmap()` on allocated/hole/out-of-range blocks, swapfile activation, MFT writeback, shutdown writeback failure, and KASAN/KMSAN checks for stale data after partial reads.
