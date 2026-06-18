# sources/distributed-fs/ceph-client/fs/exfat/cache.c

## Purpose
`cache.c` provides a small per-inode LRU cache for logical-file-cluster to physical-disk-cluster runs. exFAT can represent a file as either a contiguous no-FAT chain or an explicit FAT chain; this cache accelerates repeated FAT-chain walks for non-contiguous files.

## Important APIs, types, and functions
`struct exfat_cache` stores one run: file-cluster start, disk-cluster start, and number of contiguous clusters. `struct exfat_cache_id` carries a candidate run and cache generation id while walking. `exfat_cache_init()` and `exfat_cache_shutdown()` manage the `exfat_cachep` slab. `exfat_cache_inval_inode()` drops all cached runs and increments `ei->cache_valid_id`.

Internal helpers include `exfat_cache_lookup()`, `exfat_cache_merge()`, `exfat_cache_add()`, `exfat_cache_update_lru()`, `cache_init()`, and `cache_contiguous()`. The exported mapping entry point is `exfat_get_cluster()`.

## Control flow
`exfat_get_cluster()` starts at `ei->start_clu`, handles empty and EOF chains, and returns immediately for the first cluster. It seeds a candidate cache entry, asks `exfat_cache_lookup()` for the best cached run covering or preceding the requested file cluster, and stops the target range at the next known cache boundary. If the cache covers the requested range, it returns the physical cluster and contiguous count.

On a cache miss or partial hit, `exfat_get_cluster()` reads FAT entries with `exfat_ent_get()` until the requested logical cluster is reached, resetting the candidate when the next physical cluster is not contiguous. It then scans forward while FAT entries remain physically contiguous to report the largest mappable extent. Discovered runs are inserted or merged under `cache_lru_lock`; stale candidate ids are ignored after invalidation.

## State and persistence behavior
The cache is purely in-memory and per inode. `struct exfat_inode_info` owns `cache_lru`, `nr_caches`, `cache_lru_lock`, and `cache_valid_id`. Persistent FAT entries are not changed here; this file only reads them. Invalidations occur on truncate and other chain-structure changes to prevent stale physical mappings from being reused.

## Dependencies and integration points
The cache depends on `exfat_ent_get()` for FAT reads, `exfat_inode_info` fields from `exfat_fs.h`, and slab/list/spinlock primitives. It is used by `exfat_map_cluster()` in `inode.c` for buffered I/O, direct I/O, bmap, and readahead.

## Risks and test signals
Risks include stale cache use after allocation/free/truncate, off-by-one errors in `nr_contig` semantics, LRU races during allocation failure and invalidation, and incorrect mapping if a corrupted FAT chain loops or points outside the volume. Tests should cover repeated random reads on fragmented files, truncate followed by read/write, extension that converts no-FAT to FAT chain, direct I/O and bmap after cache hits, concurrent invalidation under lockdep/KCSAN, and fault injection for slab allocation failure.
