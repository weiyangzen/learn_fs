# sources/distributed-fs/ceph-client/fs/exfat/inode.c

## Purpose
`inode.c` implements exFAT inode writeback, logical-to-physical block mapping, buffered/direct address-space operations, inode hash lookup by on-disk directory position, inode construction from directory entries, and inode eviction. It is the bridge between VFS page-cache I/O and exFAT cluster allocation semantics.

## Important APIs, types, and functions
Metadata writeback APIs are `__exfat_write_inode()`, `exfat_write_inode()`, and `exfat_sync_inode()`. Mapping helpers are `exfat_map_cluster()`, `exfat_get_block()`, and `exfat_block_truncate_page()`. Address-space callbacks include `exfat_read_folio()`, `exfat_readahead()`, `exfat_writepages()`, `exfat_write_begin()`, `exfat_write_end()`, `exfat_direct_IO()`, and `exfat_aop_bmap()`.

Inode cache helpers are `exfat_hash_inode()`, `exfat_unhash_inode()`, `exfat_iget()`, `exfat_fill_inode()`, `exfat_build_inode()`, and `exfat_evict_inode()`. `exfat_aops` binds exFAT block mapping to the VFS page cache.

## Control flow
`__exfat_write_inode()` skips root and deleted inodes, marks the volume dirty, fetches the inode's on-disk entry set, writes attributes and create/modify/access times, serializes `i_size` and `valid_size`, writes stream flags/start cluster or zero-size values, refreshes the entry checksum, and writes the dentry buffers. `exfat_write_inode()` wraps it in `s_lock`.

`exfat_get_block()` serializes through `s_lock`, rejects unmapped reads beyond EOF, asks `exfat_map_cluster()` for the cluster backing the requested block, maps contiguous sectors into `bh_result`, and enforces valid-data-length behavior. Reads beyond valid size are left unmapped or partially read and zero-filled; creates mark new buffers and extend `ei->valid_size`. `exfat_map_cluster()` handles no-FAT chains directly, consults `exfat_get_cluster()` for FAT chains, allocates missing clusters when `create` is true, appends them to the existing chain, converts to FAT-chain mode when allocation is no longer contiguous, and updates bmap hints.

Buffered and direct I/O use the common mapper. `exfat_write_begin()` allocates blocks through `block_write_begin()`, `exfat_write_end()` updates `valid_size` and archive attribute, and `exfat_direct_IO()` uses locking direct I/O plus explicit valid-size updates/zeroing around partial written blocks. Readahead avoids multi-page readahead across a valid-size boundary. Bmap takes `truncate_lock` to avoid races with truncate.

## State and persistence behavior
Persistent state includes directory entry timestamps/attrs/checksums, stream size/valid size/start cluster/flags, FAT links, and allocation bitmap changes triggered by mapping. Runtime inode state includes page cache, `i_blocks`, `i_size`, `ei->valid_size`, `ei->start_clu`, `ei->flags`, bmap hints, inode hash table membership keyed by `i_pos`, `i_generation`, and VFS operation pointers. Eviction truncates unlinked files under `s_lock`, clears page cache, invalidates cluster caches, and removes inode hash entries.

## Dependencies and integration points
This file depends on `file.c` truncate helpers, `fatent.c` allocation and FAT I/O, `cache.c` cluster cache, directory entry-set APIs, time/attribute helpers, VFS address-space and buffer-head helpers, direct-I/O infrastructure selected by Kconfig, and superblock inode allocation in `super.c`. `namei.c` calls `exfat_build_inode()` after lookups and updates inode hashes after rename.

## Risks and test signals
Risks include stale data beyond valid size, block mapping races with truncate, invalid cache hints after chain mutation, incorrect `i_blocks`, writeback of deleted entries, direct-I/O zeroing mistakes, and inode aliasing if `i_pos` hashing is wrong. Tests should cover buffered/direct/mmap writes across valid-size boundaries, bmap during truncate, read beyond valid size, eviction of unlinked open files, rename followed by lookup using old/new positions, root inode special cases, fragmented files with cache hits, and fault injection in directory entry writeback and cluster allocation.
