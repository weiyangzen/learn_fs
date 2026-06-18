# Research: subset-b-005659

Work item `subset-b-005659` covers six F2FS files under `sources/distributed-fs/ceph-client/fs/f2fs/`. Each section preserves the source path and is wrapped for deterministic reconciliation into the corresponding source-tree-aligned per-file report.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/file.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/file.c

## Purpose

`file.c` is the main VFS-facing regular-file implementation for F2FS. It provides the `f2fs_file_operations` and `f2fs_file_inode_operations` tables, plus the implementation behind mmap faults, fsync, llseek with `SEEK_DATA`/`SEEK_HOLE`, open/release/flush, fallocate range operations, ioctls, direct and buffered read/write iterators, file attributes, project quota changes, pinned-file control, compression management, secure trim, and advisory behavior. The file is also a coordination point between page cache state, node/data block mappings, checkpoints, roll-forward recovery, quota, fscrypt, fsverity, compression, GC, and multi-device/zoned-device constraints.

## Important APIs, Types, and Functions

- `f2fs_file_operations` wires the VFS file surface: `llseek`, `read_iter`, `write_iter`, `iopoll`, `open`, `release`, `mmap_prepare`, `flush`, `fsync`, `fallocate`, ioctls, splice, fadvise, and lease support.
- `f2fs_file_inode_operations` provides file inode methods: `getattr`, `setattr`, ACL operations, xattrs, fiemap, and fileattr get/set.
- `f2fs_do_sync_file()` and `f2fs_sync_file()` implement F2FS fsync/fdatasync policy. They choose between checkpoint-based consistency and roll-forward node persistence using inode flags, written-data ino lists, parent inode state, compression, hardlinks, strict fsync mode, and barrier flushing.
- `f2fs_vm_page_mkwrite()` handles writable mmap faults. It converts inline data, allocates or looks up blocks, rejects unsupported large-folio writable mappings, waits on data and GC writeback, zeros partial EOF, and marks the folio dirty.
- `f2fs_llseek()` and `f2fs_seek_block()` implement `SEEK_DATA` and `SEEK_HOLE`, including inline-data and compressed-cluster handling.
- Truncation and range manipulation are split across `f2fs_truncate_data_blocks_range()`, `f2fs_do_truncate_blocks()`, `f2fs_truncate_blocks()`, `f2fs_truncate()`, `f2fs_truncate_hole()`, `f2fs_punch_hole()`, `f2fs_collapse_range()`, `f2fs_zero_range()`, `f2fs_insert_range()`, and `f2fs_expand_inode_data()`.
- Block exchange helpers `__read_out_blkaddrs()`, `__clone_blkaddrs()`, `__exchange_data_block()`, and rollback logic support collapse/insert/move-range semantics and handle checkpointed versus non-checkpointed blocks.
- `f2fs_fallocate()` validates supported modes and dispatches to punch, collapse, zero, insert, or preallocation paths.
- `__f2fs_ioctl()` dispatches F2FS and generic fs ioctls for atomic write, shutdown, trim, encryption keys/policies, GC, checkpoint, defrag, move range, flush device, features, pinning, resize, verity, labels, compression block accounting, secure trim, compression options, full-file compress/decompress, device alias detection, and IO priority.
- `f2fs_file_read_iter()`, `f2fs_file_splice_read()`, `f2fs_file_write_iter()`, `f2fs_dio_read_iter()`, `f2fs_dio_write_iter()`, and `f2fs_buffered_write_iter()` provide the hot data I/O path.
- `f2fs_should_use_dio()` centralizes direct-I/O eligibility. `f2fs_force_buffered_io()` rejects DIO for unsupported encryption, verity, compression, inline reads, unaligned multi-device layouts, zoned writes that are not pinned, and checkpoint-disabled mode.
- Compression management includes `release_compress_blocks()`, `reserve_compress_blocks()`, `f2fs_release_compress_blocks()`, `f2fs_reserve_compress_blocks()`, `f2fs_ioc_compress_file()`, `f2fs_ioc_decompress_file()`, option get/set, and compressed block count retrieval.

## Control Flow and State Behavior

The fsync path first writes dirty file data with possible in-place-update hints for fdatasync or small dirty ranges. It then decides whether a checkpoint is required through `need_do_checkpoint()`. Non-regular files, compressed files, hardlinks, superblock checkpoint demand, wrong parent inode, lack of roll-forward space, uncheckpointed parent nodes, fastboot, strict recovery of parent dentries, and xattr-dir writes force checkpointing. Otherwise, `f2fs_fsync_node_pages()` persists node pages for roll-forward recovery, optionally using atomic ordering. On success it removes the inode from APPEND/UPDATE/FLUSH ino tracking and may issue a flush unless nobarrier mode or atomic ordering avoids it.

Writable mmap faults follow a block-mapping path separate from normal write iterators. The code rejects immutable files and writable large-folio mappings, checks checkpoint readiness and compression backend readiness, converts inline data, optionally balances free space before allocation, locks the page-cache invalidation range, verifies the folio still belongs to the inode, allocates or validates the data block, waits for folio and GC-meta writeback, zeros EOF tail if needed, and dirties the folio. Pinned files do not allocate in this path; they require an existing valid block.

Truncation walks dnodes from the first freed block, clears data block addresses, batches contiguous invalidations, updates compressed-block counts, invalidates extent cache ranges, decrements valid block counts, and zeros the partial page at the new EOF. Compressed files are truncated at cluster boundaries and may need partial-cluster cleanup. Inline data is handled by clearing bytes directly in the inode page. Device-aliasing inodes use extent information and reject partial truncation.

Fallocate and move-range operations serialize with `inode_lock()`, direct-I/O completion, `i_gc_rwsem`, `filemap_invalidate_lock()`, and `f2fs_lock_op()` as needed. Full-block hole punching and zeroing alter dnode block addresses; partial pages are zero-filled through page cache. Collapse and insert exchange block mappings within the same file, while move-range can exchange blocks between two regular files on the same mount and superblock if unencrypted, uncompressed, unpinned, and block-aligned.

Read/write iterators choose direct versus buffered I/O per request. Direct reads increment `F2FS_DIO_READ`, hold `i_gc_rwsem[READ]`, and use iomap. Direct writes may also hold `i_gc_rwsem[READ]` in LFS/out-of-place mode, convert inline data, preallocate when useful, submit via iomap with F2FS write hints, update size on extension, and fall back to buffered write for partial direct I/O. Buffered writes go through `generic_perform_write()`. Failed or short preallocation is cleaned by truncating blocks beyond `i_size`.

Atomic write ioctls create or reuse a COW tmpfile inode, write back dirty pages, store original size, optionally truncate the visible inode for atomic replace, and commit through `f2fs_commit_atomic_write()` followed by an atomic fsync. Abort paths are called from explicit ioctl, release, and flush-on-exiting-owner.

## Persistence, Locking, and Integration Points

This file persists state through inode node pages, dnode block addresses, SIT valid-block counts, extent caches, superblock fields, checkpoint/roll-forward inode lists, quota files, compression counters, and on-disk inode flags. It uses `f2fs_lock_op()` for filesystem metadata transactions, `i_gc_rwsem[READ/WRITE]` to coordinate with GC and DIO, `filemap_invalidate_lock()` to protect page-cache invalidation, `inode_dio_wait()` before block removal, and mount write references for mutating ioctls.

Major dependencies are `f2fs.h`, `node.h`, `segment.h`, `xattr.h`, `acl.h`, `gc.h`, `iostat.h`, VFS helpers, iomap, fscrypt, fsverity, quota, block discard/zeroout, compression backends, and F2FS tracepoints. User-visible ioctl constants come from `uapi/linux/f2fs.h`. GC integration is explicit through `f2fs_gc()`, `gc_lock`, `f2fs_gc_range()`, pinned file state, and flush-device relocation.

## Risks and Edge Cases

High-risk areas are ordering and rollback around fsync, direct-write fallback, block exchange, compressed-cluster accounting, and ioctls that mutate filesystem-wide metadata. The code is defensive about checkpoint errors, checkpoint-disabled mode, unsupported compression backends, immutable/append-only restrictions, pinned-file alignment, device aliasing, malformed block addresses, and interrupted long operations. Several partial-progress compression operations can set `SBI_NEED_FSCK` if reservation or release only partly succeeds. Direct I/O has subtle compatibility rules: some O_DIRECT requests intentionally fall back to buffered I/O, then flush and invalidate the page cache to preserve expected semantics.

## Test Signals

Useful tests include xfstests-style coverage for fsync recovery, fdatasync, strict/nobarrier modes, mmap write faults, inline-to-block conversion, truncation around EOF, fallocate punch/collapse/zero/insert, DIO alignment fallback, O_DIRECT partial write fallback, encrypted/verity/compressed exclusions, atomic write commit/abort/recovery, project quota transfer, GC and GC-range ioctls, resize refusal paths, secure trim on single and multi-device filesystems, pinned file behavior on zoned and non-zoned devices, and full-file compression/decompression interrupted by signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/gc.c

## Purpose

`gc.c` implements F2FS garbage collection, victim selection, block relocation, background GC thread management, GC ioctl entry support, age-threshold GC management, section pinning, and filesystem shrink support. It is responsible for selecting dirty sections or segments, validating that summarized blocks are still live, migrating live node/data blocks elsewhere, freeing sections, coordinating with checkpoints, and handling special layouts such as large sections, zoned devices, multi-device filesystems, pinned files, atomic COW files, and metadata-backed data movement.

## Important APIs, Types, and Functions

- `f2fs_start_gc_thread()` and `f2fs_stop_gc_thread()` allocate, start, wake, stop, and free `struct f2fs_gc_kthread`.
- `gc_thread_func()` is the background daemon loop. It sleeps adaptively, reacts to foreground-merge waiters, urgent modes, zoned-device one-time GC, idle detection, freeze/read-only states, and calls `f2fs_gc()`.
- Victim policy is implemented by `select_gc_type()`, `select_policy()`, `get_max_cost()`, `get_cb_cost()`, `get_gc_cost()`, `check_bg_victims()`, age-tree helpers, and `f2fs_get_victim()`.
- Age-threshold GC uses `struct victim_entry`, an rb-tree ordered by mtime, and helpers `add_victim_entry()`, `atgc_lookup_victim()`, `atssr_lookup_victim()`, `lookup_victim_by_age()`, and `release_victim_entry()`.
- Pinned-section handling is provided by `f2fs_pin_section()`, `f2fs_pinned_section_exists()`, `f2fs_section_is_pinned()`, `f2fs_unpin_all_sections()`, and `f2fs_gc_pinned_control()`.
- Liveness and relocation helpers include `check_valid_map()`, `gc_node_segment()`, `f2fs_start_bidx_of_node()`, `is_alive()`, `ra_data_block()`, `move_data_block()`, `move_data_page()`, and `gc_data_segment()`.
- `do_garbage_collect()` migrates all selected segments in a section/window and submits merged writes.
- `f2fs_gc()` is the central GC control loop. It handles foreground escalation, prefree checkpoint reclamation, repeated victim selection, skipped-lock accounting, checkpoint fallback, pinned-section retries, and lock release.
- Initialization and cache hooks are `f2fs_create_garbage_collection_cache()`, `f2fs_destroy_garbage_collection_cache()`, `init_atgc_management()`, and `f2fs_build_gc_manager()`.
- Range and resize support is implemented by `f2fs_gc_range()`, `free_segment_range()`, `update_sb_metadata()`, `update_fs_metadata()`, and `f2fs_resize_fs()`.

## Control Flow and State Behavior

The background GC thread waits on its normal GC waitqueue, foreground-GC merge waitqueue, or explicit `gc_wake`. It skips work on read-only or frozen superblocks and acquires a write hold before checking whether GC should run. Urgent and foreground-merged paths take `gc_lock` directly. Normal background GC tries the lock, requires I/O idleness, then adjusts sleep time upward or downward based on free/invalid block pressure. It sets a `f2fs_gc_control` structure and calls `f2fs_gc()`, then wakes foreground waiters and runs background filesystem balancing.

Victim selection starts under `dirty_i->seglist_lock`. `select_policy()` chooses dirty bitmaps, search limits, granularity, and scan offsets based on LFS versus SSR allocation, GC type, segment type, large-section mode, random segment needs, and urgent/idle GC modes. Greedy GC minimizes valid block count, cost-benefit GC considers utilization and age, and ATGC/AT_SSR builds a temporary rb-tree of old candidate sections before choosing by age/utilization. Background victims can be remembered in `victim_secmap` for later foreground collection.

Data relocation is multi-phase. `gc_data_segment()` first readaheads NAT blocks, then node pages, then validates data liveness through `is_alive()`, then readaheads or pins inodes/data pages, and finally moves blocks. Liveness is checked by comparing summary entries, NAT node info, node page address slots, node versions, and valid maps. Regular data usually moves through page cache via `move_data_page()`, while metadata-inode or COW-related data can move through `META_MAPPING` via `move_data_block()` to preserve encrypted data and on-disk block contents. Node relocation in `gc_node_segment()` similarly verifies NAT addresses before moving node folios.

`f2fs_gc()` loops until enough sections are free or no useful victim remains. If free space is below thresholds, it escalates to foreground GC and may checkpoint to reclaim prefree segments. It tracks skipped rounds caused by inode GC semaphores and can checkpoint after excessive skip ratios. It clears current-victim state, unpins sections after foreground GC, releases `gc_lock`, drops cached GC inodes, and returns `-EAGAIN` for ioctl-style callers when no section was actually freed despite a skipped-error policy.

Resize flow first validates shrink size and feature constraints, then performs a dry-run segment evacuation while GC and checkpointing are locked. It freezes the superblock, repeats free-space checks, migrates live blocks out of the target range, updates raw superblock metadata, commits the superblock, adjusts in-memory FS metadata and checkpoint user block counts, writes a resize checkpoint, and rolls back metadata or marks `SBI_NEED_FSCK` on failure.

## Persistence, Locking, and Integration Points

GC mutates SIT valid maps, summary-derived block ownership, NAT-validated node/data locations, current segment allocation, victim history, pinned-section bitmaps, inode dirty/writeback state, and checkpoint state. It coordinates through `gc_lock`, `seglist_lock`, `sentry_lock`, `i_gc_rwsem`, `io_order_lock`, block plugs, page locks, mount freeze/write protection, and `cp_global_sem` during resize.

Dependencies include `f2fs.h`, `node.h`, `segment.h`, `gc.h`, `iostat.h`, NAT/SIT/SSA metadata, page cache and meta mapping, kthreads/freezer, blk plug, tracepoints, and F2FS allocation/writeback helpers. `file.c` calls into this file through GC ioctls, flush-device, resize, pinned file behavior, and free-space balancing. Segment allocation code calls `f2fs_get_victim()` for SSR-style target selection.

## Risks and Edge Cases

The hardest correctness risks are stale summaries, NAT/node mismatches, pinned files preventing relocation, races with SSR allocation making segments fully valid again, deadlocks between summary-page locks and SIT locks, and partial resize metadata updates. The code mitigates these with phase-separated readahead/validation/migration, valid-map rechecks, explicit lock ordering comments, pinned-section retry policy, checkpoint fallback, and `SBI_NEED_FSCK` on corruption. Zoned-device capacity differences and large-section migration windows complicate free-space accounting and victim progression.

## Test Signals

Important tests include background GC under idle and busy I/O, urgent GC modes, GC_MERGE foreground waiters, zoned-device one-time/boosted GC, ATGC and cost-benefit victim selection, SSR victim selection, pinned-file GC failures and unpin retry, corrupted summary/NAT mismatch handling, compressed and atomic-COW data migration, metadata inode GC, foreground GC under low-space pressure, checkpoint fallback after skipped locks, `F2FS_IOC_GARBAGE_COLLECT_RANGE`, flush-device relocation, and shrink/resize dry-run plus rollback failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.h -->
# sources/distributed-fs/ceph-client/fs/f2fs/gc.h

## Purpose

`gc.h` defines garbage-collection constants, thresholds, lightweight data structures, and inline predicates used by F2FS GC and free-space pressure logic. It is included by GC callers and exposes the sleep-tuning and free-space heuristics that govern background GC behavior, zoned-device behavior, age-threshold GC, pinned-file failure limits, and victim search scale.

## Important APIs, Types, and Functions

- Sleep constants include normal and zoned minimum, maximum, urgent, and no-GC wait times.
- ATGC constants define age threshold, candidate ratio, maximum candidate count, age weight, valid-block threshold for one-time GC, and accuracy class.
- Space-pressure constants include invalid-block and free-block percentage limits, zoned no-GC and boost-GC thresholds, migration window granularity, boost multiplier, pinned-section count, pinned-file failure limits, maximum victim search, and checkpoint reserve sections.
- `struct f2fs_gc_kthread` stores the GC task, waitqueues, sleep times, wake flag, GC_MERGE foreground waitqueue, zoned thresholds, one-time valid threshold, and boost policy.
- `struct gc_inode_list` stores inodes pinned during GC in both list and radix-tree form to avoid duplicate `iget()` references.
- `struct victim_entry` represents ATGC candidates in an rb-tree and linked list, keyed by section mtime and segment number.
- `free_segs_blk_count_zoned()` sums usable blocks for free segments on zoned devices where zone capacity may be smaller than zone size.
- `free_segs_blk_count()`, `free_user_blocks()`, `limit_invalid_user_blocks()`, and `limit_free_user_blocks()` derive reclaimable user-space pressure metrics.
- `increase_sleep_time()` and `decrease_sleep_time()` adjust daemon wait time within configured bounds.
- `has_enough_free_blocks()`, `has_enough_invalid_blocks()`, and `need_to_boost_gc()` implement the high-level pressure predicates used by `gc.c`.

## Control Flow and State Behavior

The inline functions are intentionally simple and lock only where needed. Zoned free-block counting walks the free segment bitmap under `free_i->segmap_lock` and uses `f2fs_usable_blks_in_seg()` to avoid counting unusable blocks that span past zone capacity. Non-zoned free blocks are calculated from free segments. User-free blocks subtract overprovisioned blocks and clamp at zero.

Sleep time grows by the minimum sleep interval up to the maximum, unless the thread is already in no-GC sleep. Sleep time shrinks by the minimum interval down to the minimum, with a transition from no-GC sleep back to maximum sleep first. The boost predicate differs by device type: zoned devices boost when free sections fall below `boost_zoned_gc_percent`, while conventional devices boost when invalid blocks are high and free user blocks are low.

## Persistence, Locking, and Integration Points

This header does not persist state by itself, but its structures live in `struct f2fs_sb_info` and are mutated by `gc.c`, mount-option setup, sysfs tuning, and filesystem lifecycle code. Its calculations depend on `FREE_I(sbi)`, `MAIN_SEGS`, `free_segments()`, `free_sections()`, overprovisioning, `written_block_count()`, and zoned-usable-block helpers.

## Risks and Edge Cases

The key risk is pressure miscalculation: overcounting free blocks on zoned media can delay GC until allocation fails, while overly aggressive thresholds can increase write amplification. `free_user_blocks()` explicitly handles overprovisioned space exceeding free blocks. Percentage arithmetic uses `long`/`block_t` style calculations, so tests around very large devices and unusual zone capacities are useful.

## Test Signals

Tests should cover conventional and zoned free-block accounting, no-GC and boost thresholds, invalid-block pressure triggering, sleep-time boundary behavior, sysfs/mount tuning of GC thread fields, large device counts, and zone-capacity values not aligned to segment size.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/gc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/hash.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/hash.c

## Purpose

`hash.c` computes F2FS directory entry name hashes. It uses the ext3-derived TEA name hash for ordinary names, but switches input strings for casefolded directories and uses fscrypt siphash for encrypted casefolded plaintext names. The resulting hash is stored in `struct f2fs_filename` and used by directory lookup and insertion code.

## Important APIs, Types, and Functions

- `TEA_transform()` is the 16-round transform that updates a two-word hash buffer from four input words using the TEA delta constant.
- `str2hashbuf()` packs up to `num * 4` filename bytes into 32-bit words with a length-derived pad value.
- `TEA_hash_name()` initializes the legacy ext hash seed, processes 16-byte chunks, and clears `F2FS_HASH_COL_BIT` in the returned value.
- `f2fs_hash_filename()` is the exported function. It expects `fname->disk_name` for all directories, and for casefolded directories it expects `usr_fname` and optionally `cf_name`.

## Control Flow and State Behavior

`.` and `..` hash to zero. For normal directories, the on-disk name bytes are passed to `TEA_hash_name()` and stored little-endian in `fname->hash`. For casefolded directories with Unicode support, the function prefers the precomputed folded name. If no folded name exists, it falls back to the user plaintext name rather than the disk name, which matters for encrypted directories because the disk name may be ciphertext. For encrypted casefolded directories, it uses `fscrypt_fname_siphash()` on the plaintext qstr and returns immediately.

## Persistence, Locking, and Integration Points

The hash value is persisted in F2FS directory entries and consumed by inline and block directory lookup/insert paths. The function integrates with Unicode casefolding, fscrypt filename handling, F2FS directory setup (`f2fs_setup_filename()`), and dentry search code. It has no internal locking and operates only on caller-prepared name buffers.

## Risks and Edge Cases

The main compatibility risk is hashing the wrong representation of a name. Casefolded encrypted directories must not hash ciphertext for fallback names, or lookups would not match plaintext user input. Invalid Unicode casefold fallback must remain stable. The collision bit is cleared from TEA hashes, so collision handling elsewhere can use that bit. The function warns if expected name pointers are absent but otherwise relies on callers to prepare `struct f2fs_filename` correctly.

## Test Signals

Tests should cover normal ASCII names, long names spanning multiple 16-byte chunks, `.` and `..`, hash stability across endian conversions, casefolded valid Unicode names, casefolded invalid Unicode fallback, encrypted plus casefolded plaintext hashing, and lookup/insert behavior under deliberate hash collisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inline.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/inline.c

## Purpose

`inline.c` implements F2FS inline data and inline dentry handling. Inline data stores small regular-file or symlink contents directly in the inode node page. Inline dentries store small directory entry sets in the inode node page. The file provides read, write, truncate, conversion, recovery, lookup, add/delete, empty-dir, readdir, and fiemap support for these inline layouts.

## Important APIs, Types, and Functions

- `support_inline_data()` and `f2fs_may_inline_data()` decide whether an inode can keep inline data, excluding atomic-write use, unsupported modes, oversize data, and post-read-required files such as encrypted/verity cases.
- `f2fs_sanity_check_inline_data()` validates that inline-data inodes do not also have data blocks or node children and flags invalid feature combinations.
- `f2fs_may_inline_dentry()` checks whether a directory can use inline dentries based on mount options and mode.
- `f2fs_do_read_inline_data()`, `f2fs_read_inline_data()`, and `f2fs_write_inline_data()` copy inline file data between page cache folios and inode node pages.
- `f2fs_truncate_inline_inode()` zeros inline bytes after a truncation point and clears `FI_DATA_EXIST` when truncating to zero.
- `f2fs_convert_inline_folio()` and `f2fs_convert_inline_inode()` reserve a real block, write inline data out-of-place, mark roll-forward state, clear inline data, and clear inline flags.
- `f2fs_recover_inline_data()` reconciles inline-data state during recovery when previous and next inode pages disagree.
- Inline directory functions include `f2fs_find_in_inline_dir()`, `f2fs_make_empty_inline_dir()`, `f2fs_try_convert_inline_dir()`, `f2fs_add_inline_entry()`, `f2fs_delete_inline_entry()`, `f2fs_empty_inline_dir()`, and `f2fs_read_inline_dir()`.
- Conversion helpers `f2fs_move_inline_dirents()`, `f2fs_add_inline_entries()`, `f2fs_move_rehashed_dirents()`, and `do_convert_inline_dir()` handle moving inline dentries into block-based directory pages.
- `f2fs_inline_data_fiemap()` reports inline extents to fiemap callers.

## Control Flow and State Behavior

Inline file reads fetch the inode folio, verify the inode still has inline data, then either copy inline bytes into page index 0 or zero nonzero pages. Inline writes fetch the inode folio, wait for node writeback, copy page-cache bytes into the inline region, clear page-cache dirty state, and set `FI_APPEND_WRITE` and `FI_DATA_EXIST` for recovery. Truncation waits for node writeback, zeros the tail in-place, dirties the inode folio, and clears existence state when all inline data is removed.

Conversion from inline data to block data grabs page-cache folio 0 and the inode folio under `f2fs_lock_op()`. If data exists, it reserves logical block 0, validates that the reserved address is `NEW_ADDR`, reads inline bytes into the folio, marks it dirty, writes it out-of-place with hot-data state, waits for writeback, marks the inode for append recovery, clears inline bytes, clears the inline marker in the node folio, decrements inline stats, and clears `FI_INLINE_DATA`. Corrupt non-`NEW_ADDR` mappings set `SBI_NEED_FSCK`, log a warning, call `f2fs_handle_error()`, and return `-EFSCORRUPTED`.

Inline recovery encodes a four-way policy: if both old and new states are inline, copy new inline bytes into the current inode page; if old is inline and new is not, remove inline data and recover blocks; if old is not inline and new is inline, truncate blocks and restore inline data; if neither is inline, leave block recovery to the normal path.

Inline directories use `make_dentry_ptr_inline()` to treat the inline region as a directory bitmap, dir_entry array, and filename area. Adding an entry searches for slots and either initializes a new inode plus dentry in-place or converts the directory if no room remains. Conversion for non-hashed inline directories reserves block 0, zeros the new dentry block, copies bitmap/dentries/names, clears inline state, updates depth and size, and releases backward-compatible inline-xattr reservation when possible. Rehashed directories copy inline data to a temporary buffer, clear inline state, then re-add entries through normal directory insertion; on failure they restore the inline buffer.

## Persistence, Locking, and Integration Points

Inline state is persisted in inode node pages via inline flags, inline data bytes, inline dentry bytes, inode size/depth, `i_inline_xattr_size`, and dnode block address 0 during conversion. The code coordinates with node writeback, page-cache folios, `f2fs_lock_op()`, dnode reservation, extent/block truncation, and recovery flags. It integrates with `file.c` truncation and fallocate conversion, `inode.c` sanity/recovery, directory lookup/insertion code, fiemap, and statistics counters.

## Risks and Edge Cases

Inline conversion has several corruption-sensitive points: inode folio and page-cache folio state must agree, reserved block 0 must be `NEW_ADDR`, unused dentry block bytes must be zeroed to avoid leaking memory, and rollback for rehashed directory conversion must restore inline bytes and size/depth. Inline data is incompatible with encryption/verity/compression post-read behavior and with atomic-write usage. Directory conversion must preserve names, hashes, inode numbers, file types, parent metadata, and xattr reservation compatibility.

## Test Signals

Tests should cover small regular files and symlinks staying inline, conversion when growing past inline capacity, truncate-to-zero and partial truncate, recovery across inline/block transitions, inline directory create/delete/readdir/empty checks, conversion of inline directories with and without hash levels, no-room insertion fallback, corruption detection for unexpected block address 0, fiemap reporting of inline extents, encrypted/verity/compressed rejection, and rollback after simulated conversion failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inode.c -->
# sources/distributed-fs/ceph-client/fs/f2fs/inode.c

## Purpose

`inode.c` loads, validates, updates, writes, evicts, and cleans up F2FS inodes. It translates on-disk `struct f2fs_inode` fields into in-memory Linux inode and `struct f2fs_inode_info` state, assigns inode operation tables, verifies feature-dependent metadata, computes inode checksums, serializes inode state back to node pages, handles final deletion/truncation, and repairs bookkeeping after failed inode creation.

## Important APIs, Types, and Functions

- `f2fs_mark_inode_dirty_sync()` marks an inode dirty unless it is new, read-only, already dirtied, or an uncommitted atomic file.
- `f2fs_set_inode_flags()` maps F2FS flags and encryption/verity/casefold state to VFS inode flags.
- `__get_inode_rdev()` and `__set_inode_rdev()` decode/encode special device numbers in inline address slots.
- `__recover_inline_status()` restores inline data flags if inline bytes exist but in-memory state says no data exists.
- `f2fs_enable_inode_chksum()`, `f2fs_inode_chksum()`, `f2fs_inode_chksum_verify()`, and `f2fs_inode_chksum_set()` implement optional inode checksums over inode number, generation, and inode payload with the checksum field zeroed.
- `sanity_check_compress_inode()` validates compression algorithm, compressed-block count, cluster size, and compression level against configured backend support.
- `sanity_check_inode()` validates block count, inode footer identity, xattr nid, directory link count, extra attr sizing, feature flag consistency, inline data/dentry validity, casefold support, device alias invariants, and xattr nid range.
- `do_read_inode()` hydrates in-memory inode fields from the inode node page and initializes extent trees, timestamps, project quota, compression fields, inline stats, and disk-time snapshots.
- `f2fs_iget()` and `f2fs_iget_retry()` instantiate inodes and assign operation/address-space methods for meta, node, compression, regular, directory, symlink, and special inodes.
- `f2fs_update_inode()` serializes in-memory inode state back into the inode node folio.
- `f2fs_update_inode_page()` fetches the inode folio with retry/stop-checkpoint behavior and calls `f2fs_update_inode()`.
- `f2fs_write_inode()` is the VFS writeback hook for inode metadata.
- `f2fs_remove_donate_inode()`, `f2fs_evict_inode()`, and `f2fs_handle_failed_inode()` clean up donate lists, truncate/delete final inodes, maintain orphan/NID state, and handle failed new inode creation.

## Control Flow and State Behavior

`f2fs_iget()` first uses `iget_locked()`. Existing non-new metadata inodes are treated as corruption if externally requested; existing normal inodes are returned. New normal inodes are read with `do_read_inode()`, while metadata inodes skip disk hydration and receive special address-space operations. Operation tables are selected by mode: regular files use `f2fs_file_inode_operations`, `f2fs_file_operations`, and `f2fs_dblock_aops`; directories use directory ops; encrypted symlinks get encrypted symlink ops; special files use `init_special_inode()`.

`do_read_inode()` reads the inode node folio, converts all scalar fields from little-endian disk form, resets F2FS in-memory flags, loads inline info, computes inline xattr reservation compatibility, runs sanity checks, recovers inline existence if needed, repairs cold-node status for non-directories, decodes `i_rdev`, initializes project id and creation time extra attributes, loads compression fields and sets `FI_COMPRESSED_FILE`, snapshots disk timestamps, validates extent-cache state, and initializes read and age extent trees.

`f2fs_update_inode()` waits for node writeback, dirties the node folio, marks the inode synced, writes mode, ownership, links, block count, size except for uncommitted atomic files, largest read extent, inline flags, timestamps, directory depth or GC failure count, xattr nid, F2FS flags, parent ino, generation, dir level, extra attributes, project id, creation time, compression fields, and special-device encoding. Deleted inodes clear inline state. With check-fs enabled, it updates the inode checksum.

`f2fs_write_inode()` skips node/meta inodes, ignores pure lazytime updates when the inode is otherwise clean, returns errors for checkpoint failure or checkpoint-not-ready states, updates the inode page, and balances the filesystem when writeback requests actual writing. `f2fs_update_inode_page()` retries inode folio fetches for transient memory or I/O issues and stops checkpointing if it cannot safely update metadata.

`f2fs_evict_inode()` aborts atomic writes, drops COW inode links, truncates page cache, invalidates compression cache for live/bad compressed inodes, skips deletion for meta inodes, removes dirty/donate/extent state, and for unlinked inodes initializes quota, removes recovery ino entries, protects against freeze, sets `FI_NO_ALLOC`, truncates data blocks, removes the inode node page under `f2fs_lock_op()`, retries on `-ENOMEM`, and updates or flags repair state on failure. It drops quotas and stats, verifies dirty state when safe, removes the inode from dirty metadata lists, invalidates node mapping pages, re-adds recovery entries for still-linked append/update writes, returns failed free NIDs, releases fscrypt info, and clears the VFS inode.

Failed new inode handling clears nlink, updates and syncs the inode page, unlocks the new inode without marking it bad, acquires or records orphan inode state before unlocking the filesystem operation, finalizes or frees the nid based on NAT block address, and drops the inode with `iput()`.

## Persistence, Locking, and Integration Points

Inode persistence is through F2FS node pages in `NODE_MAPPING`, on-disk inode extra attributes, inline areas, extent fields, checksum fields, NAT block addresses, orphan tracking, quota state, and recovery ino lists. The file integrates with `file.c`, `dir.c`, symlink operations, node and segment managers, xattrs, compression address-space operations, fscrypt, fsverity, quota, checkpointing, extent caches, and error handling. Locking includes node folio locks/writeback waits, `f2fs_lock_op()` for inode-page removal and failed inode orphan registration, `sb_start_intwrite()` during eviction, and internal inode/donate locks.

## Risks and Edge Cases

The most sensitive areas are accepting corrupted on-disk inode fields, preserving compatibility for extra attributes and inline xattr sizing, keeping atomic-write inode size semantics correct, avoiding dirty-inode assertions during failed eviction, and not losing orphan inode records after failed creation. Feature flags must agree with superblock features, compression settings must match compiled backend support, device aliasing requires pinned files, and inline data/dentry combinations must be mode-appropriate. Eviction has many partial-failure paths that intentionally set `SBI_NEED_FSCK` or quota repair flags.

## Test Signals

Tests should cover inode checksum verification/set, malformed inode footers/block counts/xattr nids, feature-flag mismatch images, compression option validation across algorithms and levels, inline status recovery, regular/dir/symlink/special inode operation assignment, project quota and crtime extra attributes, lazytime writeback, checkpoint-error write_inode behavior, eviction of linked, unlinked, bad, compressed, atomic, COW, and device-aliasing inodes, orphan handling after failed inode creation, and fault injection for truncate/remove inode page failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/f2fs/inode.c -->
