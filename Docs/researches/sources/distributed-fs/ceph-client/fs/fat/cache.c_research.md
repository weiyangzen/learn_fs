# sources/distributed-fs/ceph-client/fs/fat/cache.c

## Purpose
`cache.c` implements per-inode cluster-chain lookup caching and logical-to-physical block mapping for FAT files. FAT stores file extents as linked lists of cluster numbers in the FAT table, so random access otherwise requires walking from the first cluster. This file keeps a small LRU of contiguous logical file cluster to disk cluster runs and provides the mapping path used by buffered IO, direct IO, directory iteration, and `bmap`.

## Important APIs, Types, and Functions
- `struct fat_cache` is an in-memory cache record for one contiguous run: file cluster `fcluster`, disk cluster `dcluster`, and `nr_contig`.
- `struct fat_cache_id` is a temporary lookup/build accumulator tagged with `cache_valid_id` so stale walkers do not install entries after invalidation.
- `fat_cache_init()` / `fat_cache_destroy()` create and destroy the `fat_cache` slab.
- `fat_cache_lookup()`, `fat_cache_merge()`, `fat_cache_add()`, and `fat_cache_inval_inode()` manage the per-inode LRU under `MSDOS_I(inode)->cache_lru_lock`.
- `fat_get_cluster()` walks the FAT chain to resolve a logical cluster and updates the cache with contiguous runs.
- `fat_get_mapped_cluster()` and `fat_bmap()` translate VFS sectors to physical block numbers and mapped block counts.

## Control Flow
Lookup starts in `fat_bmap()`. FAT12/16 root directories are a special fixed-area case and map directly from `sbi->dir_start`; all other files call `fat_get_mapped_cluster()` after EOF bounds are checked. `fat_get_mapped_cluster()` computes the logical cluster and sector offset, calls `fat_bmap_cluster()`, then returns the physical sector from `fat_clus_to_blknr()`.

`fat_get_cluster()` validates the inode start cluster, handles cluster zero immediately, attempts an LRU lookup, and then iterates FAT entries through `fat_ent_read()`. It stops on the requested cluster, EOF, free-entry corruption, read error, or a chain-loop guard based on `s_maxbytes`. During iteration, `cache_contiguous()` detects whether the next disk cluster extends the current run; otherwise `cache_init()` starts a new run. The final run is installed with `fat_cache_add()`.

## State and Persistence
The cache itself is volatile per-inode state. Persistent state is not written here except indirectly through dependencies that read FAT entries. `cache_valid_id` is incremented during invalidation so a walker that observed old state cannot repopulate invalid entries. `fat_bmap()` consults `i_size`, `i_blocks`, and `MSDOS_I(inode)->mmu_private` to avoid mapping beyond logical EOF unless allocation is in progress.

## Dependencies and Integration Points
This file depends on FAT entry access from `fatent.c`, geometry and helpers from `fat.h`, corruption reporting from `misc.c`, and inode fields initialized in `inode.c`. It is called by address-space operations in `inode.c`, directory readers in `dir.c`, truncation paths in `file.c`, and export/rebuild logic that scans directories.

## Risks and Test Signals
Corrupt chains can present invalid start clusters, free entries inside a file, EOF before the requested cluster, or loops; this file reports those as FAT filesystem errors and usually returns `-EIO`. The cache is intentionally tiny (`FAT_MAX_CACHE` 8), so workloads with many seeks still walk the FAT. Useful tests include filesystem IO across fragmented chains, truncate/unlink invalidation, directory traversal, `bmap`, fallocate keep-size, and corruption images with broken cluster chains.
