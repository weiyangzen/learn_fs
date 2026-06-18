# Group Research: group_747_linux_sources_os_linux_linux_fs_f2fs_data_c_sources_os_linux_linux_f_6ee6cdd42bdb

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/data.c -->
# File Research: sources/os/linux/linux/fs/f2fs/data.c

## Summary
Implements F2FS data I/O, block mapping, read/write folio operations, writeback, direct-I/O iomap mapping, fiemap, swapfile activation, and BIO lifecycle handling. It is the main bridge between the F2FS logical block tree, page cache folios, compression/encryption/verity post-processing, and block-device BIO submission.

## Main Responsibilities
- Allocates, merges, submits, and completes read/write BIOs.
- Handles post-read decrypt, decompress, and fs-verity verification steps.
- Maps logical file blocks to physical blocks for buffered I/O, DIO, bmap, fiemap, precache, and allocation paths.
- Reads normal, compressed, inline, and large folio data.
- Writes data pages through in-place update or out-of-place update policies.
- Implements `address_space_operations` for data files.
- Supports swapfile activation by validating and migrating extents to section-aligned pinned blocks.
- Initializes/destroys BIO, post-read, and large-folio state caches.

## Key APIs
- BIO/cache lifecycle: `f2fs_init_bioset()`, `f2fs_destroy_bioset()`, `f2fs_init_post_read_processing()`, `f2fs_init_bio_entry_cache()`.
- Submission: `f2fs_submit_page_bio()`, `f2fs_submit_page_write()`, `f2fs_submit_read_bio()`, `f2fs_submit_merged_write()`, `f2fs_flush_merged_writes()`.
- Mapping/allocation: `f2fs_map_blocks()`, `f2fs_get_block_locked()`, `f2fs_reserve_block()`, `f2fs_update_data_blkaddr()`.
- Reads: `f2fs_get_read_data_folio()`, `f2fs_find_data_folio()`, `f2fs_get_lock_data_folio()`, `f2fs_get_new_data_folio()`.
- Writeback: `f2fs_do_write_data_page()`, `f2fs_write_single_data_page()`, `f2fs_write_data_pages()`, `f2fs_write_failed()`.
- Exported operations: `f2fs_dblock_aops`, `f2fs_iomap_ops`.

## Important Behavior
Read completion calls `f2fs_finish_read_bio()`, which updates page accounting, handles compressed page completion, validates node-page footers, and ends folio reads. Reads may be routed through `f2fs_post_read_work()` for fscrypt decryption and compressed cluster decompression, then through fs-verity verification work.

Write completion handles fscrypt bounce folios, compressed write completion, checkpoint failure escalation for CP data, node footer sanity checks, fsync node list cleanup, page-count accounting, and writeback completion.

`f2fs_map_blocks()` is the central logical-to-physical mapper. It consults the read extent cache, walks dnodes, validates block addresses, optionally reserves or allocates blocks, handles holes/`NEW_ADDR`/`COMPRESS_ADDR`, updates read extent cache during precache, supports multi-device DIO translation, and waits on writeback for direct I/O mappings.

Buffered reads use `f2fs_mpage_readpages()` and `f2fs_read_single_page()`, with special paths for inline data, compressed clusters, fs-verity, readahead, and immutable large folios. Compressed reads assemble cluster state and read compressed pages into a decompression context rather than marking pagecache pages directly up-to-date per BIO.

Writeback uses a customized `write_cache_pages` loop to handle hot/cold data policy, compression clusters, sync-vs-async write serialization, dirty folio collection, retry on checkpoint races, merged BIO submission, and IPU BIO flushing.

`f2fs_write_begin()` reserves or finds blocks, converts inline data when needed, handles atomic-file COW inode writes, prepares compressed overwrites, waits for writeback, and reads partial existing data unless the block is newly allocated. `f2fs_write_end()` marks folios dirty, updates atomic flags and file size, and delegates compressed overwrite completion.

## State and Synchronization
Uses per-type write merge state in `sbi->write_io`, per-BIO post-read contexts from a mempool, BIO entry slabs for IPU write tracking, and per-large-folio `f2fs_folio_state` for partial read completion. Synchronization includes F2FS operation locks, dnode/node folio writeback waits, BIO list locks, writepage serialization mutexes, checkpoint/writeback counters, folio locks, invalidate locks, and zoned-device completions.

## Risks
The file has many paths where block-address validity, dnode lifetime, and page-cache state must agree. Compression, encryption, fs-verity, atomic COW writes, multi-device DIO, zoned devices, and checkpoint-disabled modes all alter normal I/O behavior. Incorrect lock ordering around folio locks, node locks, and `f2fs_lock_op()` can deadlock. Extent-cache hits must still honor writeback waits and device translation. Large folio read accounting depends on `read_pages_pending` being incremented before BIO submission and decremented exactly once per completed subpage.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/debug.c -->
# File Research: sources/os/linux/linux/fs/f2fs/debug.c

## Summary
Implements F2FS debug/statistics collection and the debugfs `f2fs/status` report. It tracks per-mounted-filesystem state, segment distribution, cache sizes, dirty/writeback counters, checkpoint/GC metrics, extent-cache hit rates, and memory footprint estimates.

## Main Responsibilities
- Maintains the global `f2fs_stat_list`.
- Builds and destroys per-superblock `f2fs_stat_info`.
- Computes segment validity distribution and bimodal distribution factor.
- Aggregates multi-device segment/section usage.
- Reports dirty pages, inode counts, cache counters, checkpoint counters, GC activity, discard/flush state, and memory estimates.
- Creates/removes the debugfs root and `status` file when `CONFIG_DEBUG_FS` is enabled.

## Key APIs
- `f2fs_update_sit_info()`.
- `f2fs_build_stats()`.
- `f2fs_destroy_stats()`.
- `f2fs_create_root_stats()`.
- `f2fs_destroy_root_stats()`.

## Important Behavior
`update_general_status()` refreshes most live counters from `sbi`, NAT/SIT managers, dirty-page counters, extent-cache statistics, discard and flush controllers, checkpoint merge state, curseg positions, GC counters, and multi-device data.

`stat_show()` locks the global stats list, iterates all mounted F2FS instances, updates each status snapshot, and emits a large human-readable status report through `seq_file`.

`update_mem_info()` estimates static metadata memory, cache memory, extent-tree memory, and page-cache memory for node/meta/compression inode mappings.

## State and Synchronization
The global stats list is protected by `f2fs_stat_lock`. Checkpoint timing fields use `sbi->cprc_info.stat_lock`. Debugfs output reads many live counters atomically or through helper APIs, but it is primarily diagnostic and snapshot-oriented.

## Risks
The debug report combines values from many subsystems without taking all subsystem locks, so it should be treated as approximate live telemetry. Memory footprint estimates are manually maintained and can drift as F2FS structures evolve. Multi-device stats depend on segment-to-device boundary calculations staying consistent with resize and device layout state.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/dir.c -->
# File Research: sources/os/linux/linux/fs/f2fs/dir.c

## Summary
Implements F2FS directory lookup, filename preparation, dentry insertion/deletion, directory initialization, emptiness checks, and readdir. It supports encrypted filenames, casefolded Unicode lookup, inline dentries, hashed directory levels, and regular dentry blocks.

## Main Responsibilities
- Prepares `struct f2fs_filename` from VFS names using fscrypt and optional Unicode casefolding.
- Searches inline and regular directory entries by hash bucket or linear fallback.
- Adds, updates, and deletes directory entries.
- Initializes inode metadata and `.` / `..` entries for new directories.
- Maintains parent directory metadata, link counts, orphan handling, and directory depth.
- Emits directory entries for `iterate_shared`.
- Provides `f2fs_dir_operations`.

## Key APIs
- Filename setup: `f2fs_setup_filename()`, `f2fs_prepare_lookup()`, `f2fs_free_filename()`.
- Lookup: `f2fs_find_target_dentry()`, `f2fs_find_entry()`, `f2fs_parent_dir()`, `f2fs_inode_by_name()`.
- Mutation: `f2fs_add_dentry()`, `f2fs_do_add_link()`, `f2fs_delete_entry()`, `f2fs_set_link()`.
- Creation helpers: `f2fs_init_inode_metadata()`, `f2fs_do_make_empty_dir()`, `f2fs_do_tmpfile()`.
- Readdir: `f2fs_fill_dentries()`, `f2fs_dir_operations`.

## Important Behavior
Directory layout is hash-level based. `dir_buckets()`, `bucket_blocks()`, and `dir_block_index()` compute where a filename hash should be searched or inserted. `find_in_level()` searches the relevant bucket, records cached hash/level hints when room is found, and can fall back to linear search for casefold compatibility modes.

Filename setup wraps fscrypt preparation and computes the F2FS hash. For encrypted no-key names, the hash is decoded from the name. For casefolded directories, Unicode names may be casefolded into `cf_name`; strict encoding failures return `-EINVAL`, while non-strict failures fall back to opaque byte matching.

Insertion first tries inline dentries, then regular dentry blocks. `f2fs_add_regular_entry()` allocates dentry pages, finds free slots, initializes inode metadata if needed, writes the dentry, updates parent metadata, and manages directory depth.

Deletion clears the dentry bitmap slots, may truncate an emptied dentry block, updates parent timestamps, and drops the target inode link count. Directory emptiness ignores `.` and `..` in block zero and scans all other dentry bits.

`f2fs_fill_dentries()` validates name lengths, handles encrypted name conversion, emits entries with `dir_emit()`, optionally readaheads inode node pages, and marks the filesystem for fsck on corrupted zero-length or oversized dirents.

## State and Synchronization
Directory mutation uses folio locks, writeback waits, inode `i_sem` for inode metadata updates, `i_xattr_sem` for inline dentry insertion lock ordering, and F2FS operation locking supplied by callers where required. The directory inode caches a recent failed-lookup task and hash/level hint to speed create-after-lookup.

## Risks
Correctness depends on matching bitmap slot counts with encoded filename lengths. Casefold compatibility fallback can search without hashes, so callers must handle both hash and linear modes. Error handling during new inode metadata creation must clear link state and release orphan/tmpfile state correctly. Readdir corruption checks are defensive, but malformed on-disk dirents can still interrupt iteration with `-EFSCORRUPTED`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/f2fs/extent_cache.c -->
# File Research: sources/os/linux/linux/fs/f2fs/extent_cache.c

## Summary
Implements F2FS in-memory extent caches. It maintains read extents for logical-to-physical block lookups and block-age extents for hot/warm/cold data-age decisions. Extents are stored per inode in cached red-black trees with global LRU-style lists and shrinker support.

## Main Responsibilities
- Validates on-disk inode read extent metadata.
- Creates, initializes, looks up, updates, merges, splits, shrinks, drops, and destroys extent trees.
- Supports two extent types: `EX_READ` and `EX_BLOCK_AGE`.
- Maintains largest read extent, cached extent-node hits, rb-tree hits, and global extent counters.
- Handles compressed read extents and device-aliasing constraints.
- Initializes/destroys extent cache slabs and per-superblock extent-cache state.

## Key APIs
- Validation/init: `sanity_check_extent_cache()`, `f2fs_init_read_extent_tree()`, `f2fs_init_age_extent_tree()`, `f2fs_init_extent_tree()`, `f2fs_init_extent_cache_info()`.
- Read cache: `f2fs_lookup_read_extent_cache()`, `f2fs_lookup_read_extent_cache_block()`, `f2fs_update_read_extent_cache()`, `f2fs_update_read_extent_cache_range()`.
- Age cache: `f2fs_lookup_age_extent_cache()`, `f2fs_update_age_extent_cache()`, `f2fs_update_age_extent_cache_range()`.
- Reclaim/lifetime: `f2fs_shrink_read_extent_tree()`, `f2fs_shrink_age_extent_tree()`, `f2fs_destroy_extent_node()`, `f2fs_drop_extent_tree()`, `f2fs_destroy_extent_tree()`.
- Slabs: `f2fs_create_extent_cache()`, `f2fs_destroy_extent_cache()`.

## Important Behavior
Read extent trees are enabled for regular files when the mount option permits them, plus special device-aliasing handling. Block-age trees are enabled for regular files and directories when age caching is enabled, but not for compressed or cold files.

Lookups first test the largest read extent, then the cached extent node, then the rb-tree. Hits update statistics and move extent nodes to the tail of the global extent list.

Updates invalidate overlapping ranges, split existing extents when large enough, merge compatible adjacent extents, insert new nodes, update the largest extent, and mark the inode dirty when the persisted largest extent changes. Small repeated splits can disable read extent caching by setting `FI_NO_EXTENT`.

Block-age updates compute age from `allocated_data_blocks` and previous age records using a weighted average. Invalid age updates can remove or skip age-cache entries.

Shrinking first frees zombie extent trees from evicted inodes, then removes LRU extent nodes from live trees using trylocks to avoid blocking heavily contended trees.

## State and Synchronization
Each extent tree has an rwlock for rb-tree and cached-largest state. Each extent type has a radix tree protected by `extent_tree_lock`, a global extent-node list protected by `extent_lock`, and zombie-tree accounting. Nodes and trees are allocated from dedicated slabs. Per-inode pointers in `F2FS_I(inode)->extent_tree[]` keep active trees reachable until inode eviction.

## Risks
Extent updates are sensitive to overlap, split, and merge boundaries. Read extents must never cache invalid physical addresses, compressed clusters incorrectly, or cross-device mappings that DIO cannot use. Device-aliasing inodes bypass normal read-cache lookup behavior and require strict extent validation. Shrinker and eviction paths must keep radix-tree entries, zombie lists, node lists, and counters synchronized.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/f2fs/extent_cache.c -->