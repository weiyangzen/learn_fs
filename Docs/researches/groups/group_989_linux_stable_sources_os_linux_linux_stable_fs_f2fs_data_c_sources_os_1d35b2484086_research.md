# Group Research: group_989_linux_stable_sources_os_linux_linux_stable_fs_f2fs_data_c_sources_os_1d35b2484086

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/os/linux/linux-stable`, which is included in subset A. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/data.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/data.c

`data.c` is the main F2FS data I/O implementation. It wires the address-space operations for file data, direct-I/O iomap mapping, buffered write begin/end, read/readahead, writeback, swapfile activation, page-cache invalidation, and the BIO allocation/merge/submit paths used by data, node, and metadata writes.

Major owned resources include the F2FS bioset, BIO entry slab, large-folio state slab, post-read context slab/mempool, and per-mount post-read workqueue. Read completion can run post-processing steps for fscrypt decryption, F2FS decompression, and fs-verity verification; compressed folios are finished at cluster granularity rather than just per BIO.

The low-level I/O path resolves multi-device block addresses with `f2fs_target_device()` and `f2fs_target_device_index()`, builds BIOs with the right op flags, crypt context, write hints, and iostat context, then submits through blk-crypto. Write BIO completion handles bounce pages, compressed write completion, checkpoint-data failure policy, node footer sanity checks, fsync-node removal, page-count accounting, GC flag cleanup, and folio writeback completion.

Write merging is split between normal merged write BIOs in `sbi->write_io[type][temp]` and an IPU BIO list for inplace-update writes. Mergeability checks require contiguous blocks, same target block device, compatible op flags, and compatible encryption DUN/crypt context. Zoned-device support forces submission at sequential zone boundaries and waits on pending zone BIO completion.

Block mapping centers on `f2fs_map_blocks()`. It consults the read extent cache, walks dnodes, validates physical block addresses, creates blocks for pre-AIO/pre-DIO/DIO callers, tracks holes, delalloc/NEW_ADDR, multi-device DIO bdev remapping, LFS direct-write behavior, next extent/page hints, and read extent cache population. `f2fs_get_read_data_folio()`, `f2fs_find_data_folio()`, `f2fs_get_lock_data_folio()`, and `f2fs_get_new_data_folio()` are the page-cache-facing helpers used by directories, GC, and normal file I/O.

Read paths cover single-page reads, readahead, compressed cluster reads, and large folios. Normal reads use `f2fs_read_single_page()` and merged BIOs; compressed reads use `f2fs_read_multi_pages()` and `decompress_io_ctx`; large folios maintain `read_pages_pending` in private folio state so a large folio is completed only after all subpage reads finish. Holes and EOF ranges are zero-filled and fs-verity is applied where relevant.

Writeback uses `f2fs_write_cache_pages()`, a customized `write_cache_pages()` variant that batches dirty folios, handles compressed clusters, prioritizes WB_SYNC requests, retries checkpoint races, submits merged OPU/IPU BIOs, and updates writeback indexes. `f2fs_do_write_data_page()` chooses IPU versus OPU based on pinned/cold files, LFS mode, atomic writes, checkpoint-disabled state, compression, directory/quota policy, and filesystem flags.

Buffered writes are implemented by `f2fs_write_begin()` and `f2fs_write_end()`. They handle inline-data conversion/readout, block reservation, partial-page read-before-write, atomic-write COW inode handling, compression overwrite preparation, dirtying, i_size updates, and failure truncation through `f2fs_write_failed()`.

FIEMAP and bmap support include xattr fiemap, inline data/dentry fiemap delegation, compressed-cluster FIEMAP encoding, delalloc/unwritten reporting, and block lookup for compressed and uncompressed files. Swap activation requires regular writable files, rejects unsupported LFS cases, disables compression, flushes data, precaches extents, rejects holes, migrates unaligned extents into pinned aligned sections when possible, and pins the swapfile inode until deactivate.

Important cross-file dependencies are `node.c` dnode/node-info routines, `segment.c` allocation/write placement, `extent_cache.c` read-extent lookups and updates, compression helpers, inline-data helpers, fscrypt/fsverity, iostat, tracepoints, and checkpoint/GC state. The primary invariants are valid block-address checks before I/O, lock ordering around folio/node/op locks, correct page-count accounting, and clean separation of checkpoint-guaranteed data from ordinary writeback.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/data.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/debug.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/debug.c

`debug.c` implements F2FS runtime statistics collection and the debugfs status report. It maintains a global `f2fs_stat_list` protected by `f2fs_stat_lock`; each mounted filesystem that builds stats contributes one `f2fs_stat_info`.

`f2fs_update_sit_info()` computes segment-distribution diagnostics, including the bimodal distribution factor and average valid blocks across dirty sections. With debugfs enabled, `update_multidevice_stats()` classifies each device’s segments, and sections for large-section filesystems, into in-use, dirty, full, free, and prefree buckets.

`update_general_status()` snapshots a broad set of live counters into `f2fs_stat_info`: superblock layout, extent-cache hits and object counts, dirty page/inode counts, direct I/O and writeback counts, flush/discard queues, checkpoint merge timing, valid/free/prefree/dirty segment counts, inline/compressed/swapfile inode counters, NAT/SIT/free-NID state, GC skip counts, current segment positions, metadata block counts, checkpoint call counts, SSR/LFS block counts, and inplace-update count.

`update_mem_info()` estimates F2FS memory footprint. It separates base/static filesystem structures, cached metadata structures such as NAT/SIT/dirty/free maps and extent cache nodes, and mapped page-cache memory for node/meta/compress inodes.

`stat_show()` is the debugfs `.show` callback. It locks the global stat list, updates each mounted filesystem’s status, and emits a human-readable report covering partition state, checkpoint state, SBI flags, layout, mount time, IPU policy, utilization, inode/data breakdown, curseg positions, multidevice stats, checkpoint and GC activity, extent-cache ratios, async I/O pressure, dirty data distribution, SSR/LFS/IPU counts, segment BDF, and memory usage.

`f2fs_build_stats()` allocates and initializes per-mount stat state, initializes stat counters on `sbi`, attaches the entry to the global list, and stores it in `sbi->stat_info`. `f2fs_destroy_stats()` removes and frees it. `f2fs_create_root_stats()` creates `/sys/kernel/debug/f2fs/status`, and `f2fs_destroy_root_stats()` removes the debugfs tree.

This file is observability-focused: it does not implement filesystem mutation paths, but it reads many live F2FS subsystem counters. Its main safety concerns are locking around the global list, checkpoint timing stat lock, extent/multidevice data consistency during reporting, and keeping debugfs-only code behind `CONFIG_DEBUG_FS`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/debug.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/dir.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/dir.c

`dir.c` implements F2FS directory lookup, dentry insertion/deletion, empty-directory checks, readdir, and directory file operations. It supports inline dentry directories, regular hashed directory blocks, encrypted names, and Unicode casefolded lookup.

Filename setup wraps fscrypt name preparation and adds F2FS-specific casefolding and hash calculation. `f2fs_setup_filename()` and `f2fs_prepare_lookup()` populate `struct f2fs_filename`; no-key encrypted names reuse the decoded hash, while normal names may allocate a casefold buffer and compute the F2FS dirhash. `f2fs_free_filename()` releases crypto and casefold buffers.

Directory layout helpers compute block counts, bucket counts, bucket sizes, and logical block indexes for F2FS’s level/bucket hash directory scheme. Lookup searches inline dentries first, then each hash level and bucket through `find_in_level()`. Casefolded directories may fall back to a linear search depending on the `lookup_mode` and superblock compatibility fallback state.

`f2fs_find_target_dentry()` scans a dentry bitmap, skips unused slots, validates nonzero name length, optionally filters by hash, matches names through Unicode casefold or fscrypt matching, and tracks maximum free slot runs for create acceleration. Missed lookups remember the current task on the directory inode to optimize the subsequent create path while still rechecking for stackable-filesystem races when needed.

Creation paths allocate or initialize inode metadata, create `.` and `..` for new directories, initialize ACL/security/encryption context, copy dentry name metadata into the inode page for recovery, handle encrypted+casefold hash storage or `LOST_PINO`, and update parent timestamps/depth/link counts. `f2fs_add_dentry()` prefers inline insertion and falls back to regular hashed-directory insertion.

Deletion clears the relevant bitmap slots, handles inline dentry deletion separately, truncates now-empty regular dentry blocks, clears dirty/page-cache state when a dentry page is deallocated, updates parent metadata, and drops the target inode link count. Directory emptiness scans inline or regular blocks, ignoring `.` and `..` in block zero.

`f2fs_fill_dentries()` is the core readdir scanner. It validates dentry name lengths and slot bounds, marks corruption and `SBI_NEED_FSCK` on invalid entries, converts encrypted disk names to user names, emits entries through `dir_emit()`, and optionally triggers node-page readahead for emitted inode numbers. `f2fs_readdir()` handles encrypted readdir setup, inline directories, page-cache readahead, fatal signal interruption, and trace reporting.

The exported `f2fs_dir_operations` provide llseek, generic directory read, shared iterate, fsync, ioctl/compat ioctl, and lease operations. Key dependencies are `data.c` folio read/new/truncate helpers, inline dentry helpers, inode/node update routines, fscrypt, Unicode casefold support, ACL/security initialization, orphan handling, and tracepoints.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/dir.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/extent_cache.c -->
# File Research: sources/os/linux/linux-stable/fs/f2fs/extent_cache.c

`extent_cache.c` implements F2FS in-memory extent caching. It supports two extent types: read extents mapping file offsets to physical blocks, and block-age extents used to estimate data temperature from allocation age. Per-inode extent trees are stored in radix trees under each `extent_tree_info`, while each inode tree uses an rb-tree plus a cached node and, for read extents, a separately tracked largest extent.

`sanity_check_extent_cache()` validates the on-disk inode read extent against block-address validity and device-aliasing constraints. Device alias extents must match a non-meta device range and must not alias a zoned block device.

Extent-tree eligibility is controlled by mount options, inode type, `FI_NO_EXTENT`, compressed/cold-file restrictions, readonly compression handling, device aliasing, and whether the mount has registered shrinker/list state. Initialization either grabs/creates an extent tree or drops invalid on-disk largest-extent metadata and marks `FI_NO_EXTENT`.

Lookup first checks the read cache’s largest extent, then the per-inode cached node, then the rb-tree. Hits update statistics, move nodes to the global LRU list, and refresh the cached node. Insert/update paths use neighbor-aware rb-tree lookup so new ranges can merge with adjacent extents or split/delete overlapping extents.

`__update_extent_tree_range()` is the central invalidation/update routine. It rejects zero-length updates, drops overlapping largest extents, finds the first overlapping node, splits surviving left/right portions when large enough, removes fully invalidated nodes, then inserts or merges the new read or block-age extent. Small fragmented read-cache updates can disable future read extents for the inode by setting `FI_NO_EXTENT`.

Compressed read extent updates store logical length and compressed length so compressed clusters can be cached without being merged incorrectly with incompatible extents. Block-age updates compute a weighted age from `allocated_data_blocks`, prior age, and last allocation count, with invalidation support through `F2FS_EXTENT_AGE_INVALID`.

Shrinking first reclaims zombie extent trees left by evicted but still-linked inodes, then reclaims LRU extent nodes using trylocks to avoid blocking. Destroy/drop paths either free all nodes immediately, move live trees to the zombie list, remove radix-tree entries, or clear read largest-extent state and mark the inode dirty when persistent inode extent metadata changed.

Public operations include read extent lookup/block lookup/update/range update/shrink, age extent lookup/update/range invalidation/shrink, per-inode node/tree destroy, per-inode drop, per-mount extent-cache info initialization, and global slab-cache create/destroy. The file’s key invariants are rb-tree non-overlap, correct global LRU membership, radix-tree lifetime under `extent_tree_lock`, per-tree updates under `et->lock`, and global node-list changes under `extent_lock`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/f2fs/extent_cache.c -->