# subset-b-005654 Research

Grouped source research for ext4 extent movement, directory namespace operations, orphan tracking, page writeback, readpage bio assembly, and online resize. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/move_extent.c -->
# sources/distributed-fs/ceph-client/fs/ext4/move_extent.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/move_extent.c` implements ext4 online defragmentation through `ext4_move_extents()`. It swaps mapped extents between an original file and a donor file, optionally preserving original data by copying page-cache contents across the newly swapped mapping. The source was read as a complete 658-line file.

## Important APIs, Types, and Functions

The public entry point is `ext4_move_extents(struct file *o_filp, struct file *d_filp, __u64 orig_blk, __u64 donor_blk, __u64 len, __u64 *moved_len)`. Shared locking helpers `ext4_double_down_write_data_sem()` and `ext4_double_up_write_data_sem()` serialize extent-tree mutations across the two inodes by address order. `struct mext_data` carries the original inode, donor inode, current original mapping, and donor logical block.

Core helpers are `mext_check_validity()` for filesystem and inode constraints, `mext_check_adjust_range()` for block range alignment and EOF trimming, `mext_move_extent()` for one folio-bounded move, `mext_move_begin()` for double folio locking and mapping revalidation, `mext_folio_mkuptodate()` for reading source buffers into cache, and `mext_folio_mkwrite()` for rebuilding buffer mappings and committing dirty data after the swap.

## Control Flow

`ext4_move_extents()` locks both non-directory inodes against truncate, validates that files are regular, extent-based, same-filesystem, non-DAX, non-encrypted, non-journal-data, non-swap, non-quota, and non-empty, waits for direct I/O, adjusts the requested range, then loops over original mappings from `ext4_map_blocks()`. Holes and delayed allocations are skipped; mapped or unwritten ranges are handed to `mext_move_extent()`.

`mext_move_extent()` starts a move-extents journal transaction and marks fast commit ineligible. `mext_move_begin()` locks the relevant folios in stable inode order, waits for writeback, verifies that the original extent-status sequence still matches the mapping observed before folio locking, trims the move to folio and donor mapping boundaries, then classifies the work as skip, pure extent move, or data copy. For data-copy moves, the original folio range is made uptodate before buffer mappings are released. The code then write-locks both `i_data_sem` locks and calls `ext4_swap_extents()`. If original data must survive, it remaps the original folio buffers through `mext_folio_mkwrite()` and pins the written range to the transaction with `ext4_jbd2_inode_add_write()`.

Short progress is folded into the outer loop. `-ESTALE` retries after extent-status sequence changes, `-ENOSPC` uses `ext4_should_retry_alloc()`, and `-EBUSY` can force a nested journal commit before retrying. If data copy fails after a swap, the repair branch swaps the moved extent back; failure to repair is escalated with `ext4_error_inode_block()`.

## State and Persistence Behavior

Persistent changes are extent-tree swaps between the original and donor inode plus possible data writes to the original file after the swap. The operation dirties journal metadata and explicitly excludes fast commit because extent movement cannot be replayed by the fast-commit path. For data-copy cases, page-cache data is preserved by reading before the swap and committing writes after the mapping replacement. `*moved_len` accumulates successfully swapped blocks, and successful moves discard both inodes' preallocations to avoid stale allocation hints.

Transient state includes locked folios, buffer heads, current `ext4_map_blocks` records, journal credits sized from `ext4_chunk_trans_extent()`, and retry counters.

## Dependencies and Integration Points

This file depends on ext4 extents (`ext4_map_blocks()`, `ext4_swap_extents()`), the extent status sequence (`i_es_seq`), JBD2 transaction handling, folio and buffer-head cache operations, direct-I/O exclusion, quota-file detection, mount feature checks, and ext4 tracepoints `trace_ext4_move_extent_enter/exit`. It is called by the defragmentation ioctl path and coordinates with writeback, truncate, and allocation retry logic.

## Risks and Edge Cases

High-risk areas are stale mapping detection, folio order and inode lock ordering, data preservation after extent swap, and repair after partial failure. The range must share the same page offset in both files, so unaligned donor/original starts are rejected. Bigalloc, DAX, encrypted files, journaled-data mode, swap files, and quota files are rejected because the swap/copy semantics are unsafe or unsupported. If `filemap_release_folio()` fails, the move returns `-EBUSY`; this protects against buffers that cannot be invalidated before the extent tree is swapped.

## Test Signals

Useful tests include online defrag of mapped, unwritten, sparse, and mixed extents; donor holes; EOF-shortened ranges; concurrent writeback causing `-ESTALE`; direct-I/O wait coverage; `-ENOSPC` retry; `-EBUSY` retry after journal commit; and fault injection around `ext4_swap_extents()`, folio read, and post-swap write. Signals include `trace_ext4_move_extent_*`, changed `moved_len`, journal abort or ext4 error logs on failed repair, and verification that original file data remains intact.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/move_extent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/namei.c -->
# sources/distributed-fs/ceph-client/fs/ext4/namei.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/namei.c` implements ext4 directory and namespace operations. It covers directory block reads and checksums, htree indexed lookup and insertion, linear directory scanning, casefolded and encrypted filename matching, directory entry creation/deletion, create/mknod/tmpfile/mkdir/rmdir/unlink/symlink/link, normal rename, whiteout rename, exchange rename, and inode operation tables. The source was read as a complete 4249-line file.

## Important APIs, Types, and Functions

The exported or externally used directory helpers include `ext4_dirblock_csum_verify()`, `ext4_handle_dirty_dirblock()`, `ext4_htree_fill_tree()`, `ext4_fname_setup_ci_filename()`, `ext4_search_dir()`, `ext4_find_dest_de()`, `ext4_insert_dentry()`, `ext4_generic_delete_entry()`, `ext4_init_dirblock()`, `ext4_init_new_dir()`, `ext4_empty_dir()`, `__ext4_unlink()`, `__ext4_link()`, `ext4_get_parent()`, and the operation tables `ext4_dir_inode_operations` and `ext4_special_inode_operations`.

Important htree types are `struct dx_root`, `struct dx_node`, `struct dx_entry`, `struct dx_countlimit`, `struct dx_frame`, `struct dx_map_entry`, and `struct dx_tail`. Directory mutation centers on `add_dirent_to_buf()`, `__ext4_add_entry()`, `ext4_dx_add_entry()`, `make_indexed_dir()`, `do_split()`, `ext4_delete_entry()`, and `ext4_rename*()` helpers. Filename matching flows through `struct ext4_filename`, `ext4_fname_setup_filename()`, `ext4_fname_prepare_lookup()`, `ext4_match()`, fscrypt helpers, and Unicode casefold helpers.

## Control Flow

Directory block reads go through `ext4_read_dirblock()`, which rejects reads past `i_size`, handles simulated failures, distinguishes htree index blocks from leaf blocks, verifies metadata checksums when enabled, and returns buffer heads only after format checks appropriate to the expected block type. Lookup first tries inline data, then htree lookup for indexed directories, then a readahead-assisted linear scan. Htree lookup uses `dx_probe()` to validate the root, compute or reuse filename hash, walk index levels by binary search, detect cycles, and return a leaf frame. `ext4_dx_find_entry()` scans the selected leaf and follows hash continuations with `ext4_htree_next_block()`.

Insertion starts in `__ext4_add_entry()`. Inline directories are tried first. Indexed directories use `ext4_dx_add_entry()`, which locates a leaf, tries direct insertion, splits full leaves with `do_split()`, and may split or grow index levels. Non-indexed directories scan blocks for space, convert a single-block directory to htree with `make_indexed_dir()` when the dir_index feature is available, or append a new block with `ext4_append()`. `add_dirent_to_buf()` obtains journal access, inserts the dirent, updates directory ctime/mtime and i_version, updates the dx flag, and dirties the checksummed directory block.

Creation operations allocate a new inode inside an ext4 journal handle, set inode operations and address-space operations, then attach it using `ext4_add_nondir()` or directory-specific setup. `ext4_mkdir()` initializes `.` and `..` through inline or block-backed directory initialization and updates parent directory link counts. `ext4_unlink()` and `ext4_rmdir()` find and delete dirents, update timestamps and link counts, add zero-link inodes to the orphan machinery, and track fast-commit unlink records. Symlink creation prepares fscrypt disk names, chooses fast symlink storage or an allocated data block, then inserts the entry. Hard links increment link count, add a dirent, and remove tmpfiles from the orphan list when first linked.

Rename builds `struct ext4_renament` records for source and destination. Normal rename validates source and target, optionally creates a whiteout inode, prepares `..` updates for moved directories, replaces or creates the target dirent, deletes or whiteouts the old entry, updates link counts and timestamps, and either tracks fast-commit operations or marks directory renames ineligible. `ext4_cross_rename()` handles `RENAME_EXCHANGE` by swapping two existing dirents and updating both `..` entries and parent link counts when directory-ness differs.

## State and Persistence Behavior

Persistent state includes directory data blocks, inline directory data, htree index roots/nodes, directory block checksum tails, dirent hash fields for casefolded encrypted directories, inode link counts, inode timestamps, inode versions, `i_size` and `i_disksize` for directories and symlinks, orphan list membership for failed or unlinked inode cleanup, and fast-commit tracking records. Metadata updates are journaled with JBD2 write access before mutation and dirty metadata calls afterward. Checksum setters are called through `ext4_handle_dirty_dirblock()` and `ext4_handle_dirty_dx_node()` before buffers are committed.

In-memory state includes lookup start hints (`i_dir_start_lookup`), htree frames and temporary hash maps for splitting, fscrypt filename buffers, casefold buffers, inline-data state flags, and dentry cache effects such as `d_splice_alias()`, `d_instantiate_new()`, `d_tmpfile()`, and CI dentry invalidation.

## Dependencies and Integration Points

The file integrates VFS inode operations with ext4 inode allocation, JBD2, ext4 inline data, fscrypt, fsverity-adjacent encryption context checks, Unicode casefolding, quota initialization, fast commits, orphan handling, buffer-head directory I/O, htree readdir storage, project quotas, and ext4 error reporting. It also consumes mount features including metadata checksums, dir_index, filetype, large directory depth, hash-in-dirent, inline data, and fast commit.

## Risks and Edge Cases

Directory code is corruption-sensitive. It must reject invalid rec_len loops, bad checksum tails, htree count/limit mismatches, htree cycles, invalid `.` or `..`, bad inode numbers, and incompatible encryption contexts. Htree insertion must keep leaf blocks balanced, maintain continuation hash bits, and update checksums for both leaves and index nodes. Inline directory conversion during rename can move the dirent being deleted, so rename has a forced reread path. Casefolded encrypted lookup can fall back to linear search when hashes cannot be trusted, and negative dentry caching is avoided for current CI limitations.

Namespace operations have multi-object consistency risks: link counts, orphaning, parent `..`, fast commit records, and directory block updates must stay transactionally aligned. Whiteout rename has rollback logic that resets the source entry and orphans the whiteout if later work fails. Directory renames disable fast commit because replay cannot update `..` entries.

## Test Signals

Relevant signals include fstests for encrypted, casefolded, inline, indexed, metadata-checksummed, and large directories; lookup of hash-collision names; readdir htree ordering; directory split and index growth; mkdir/rmdir link-count limits; unlink orphan recovery; tmpfile link; fast symlink and long symlink paths; normal, whiteout, no-replace, and exchange renames; cross-directory directory renames; project quota inheritance failures; and fault injection for directory block EIO/CRC, journal access failures, inode allocation ENOSPC, and inline-to-block conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/orphan.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/orphan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/page-io.c -->
# sources/distributed-fs/ceph-client/fs/ext4/page-io.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/page-io.c` implements ext4 buffered writeback bio submission and write I/O completion. It manages `ext4_io_end` lifetime, encrypted bounce-page writes, buffer-head completion, deferred conversion of unwritten extents, and journal abort behavior on data write errors. The source was read as a complete 613-line file.

## Important APIs, Types, and Functions

Initialization and teardown are `ext4_init_pageio()` and `ext4_exit_pageio()`, which create caches for `struct ext4_io_end` and `struct ext4_io_end_vec`. I/O end helpers include `ext4_init_io_end()`, `ext4_get_io_end()`, `ext4_put_io_end()`, `ext4_put_io_end_defer()`, `ext4_alloc_io_end_vec()`, and `ext4_last_io_end_vec()`. Completion helpers are `ext4_end_bio()`, `ext4_finish_bio()`, `ext4_end_io_end()`, `ext4_add_complete_io()`, `ext4_do_flush_completed_IO()`, and workqueue entry `ext4_end_io_rsv_work()`. Submission APIs are `ext4_io_submit_init()`, `ext4_io_submit()`, and `ext4_bio_write_folio()`.

## Control Flow

`ext4_bio_write_folio()` is called with a locked, non-writeback folio. It zeroes bytes past the requested length, walks buffer_heads to decide which buffers can be submitted, clears dirty bits, marks async-write buffers, and redirties or preserves the TOWRITE tag when buffers cannot yet be written. If nothing can be submitted, it cycles writeback state to update xarray tags. For encrypted files, it encrypts the relevant page-cache blocks into a bounce folio, using nonblocking allocation when appending to an existing bio and retrying safely for sync writeback.

The second loop starts folio writeback and sends each async-write buffer to `io_submit_add_bh()`. That helper starts a new bio when physical blocks are non-contiguous or fscrypt contexts cannot merge, attaches an `ext4_io_end` reference, and accounts cgroup ownership. `ext4_io_submit()` sets `REQ_SYNC` for `WB_SYNC_ALL` and submits through `blk_crypto_submit_bio()`.

`ext4_end_bio()` records write errors, sets `EXT4_IO_END_FAILED`, and either chains the bio onto a deferred `io_end` list or finishes the bio immediately. Deferred completion is required for unwritten extent conversion or data-error journal abort handling. `ext4_end_io_end()` converts unwritten extents via `ext4_convert_unwritten_io_end_vec()` on success; on failure it frees a reserved handle and may abort the journal when `DATA_ERR_ABORT` is enabled. `ext4_finish_bio()` clears buffer async-write state, marks buffer write I/O errors, frees encryption bounce pages, and ends folio writeback once no buffers in the folio remain under I/O.

## State and Persistence Behavior

Persistent effects are data writes and, after successful I/O to unwritten extents, metadata conversion from unwritten to written extents. I/O errors are persisted indirectly through mapping error state and optionally journal aborts. The file maintains transient `ext4_io_end` objects with reference counts, bio chains, conversion vectors, flags, reserved journal handles, and inode completion-list links. Per-inode deferred completions live on `i_rsv_conversion_list` and are drained by `rsv_conversion_wq`.

## Dependencies and Integration Points

The code depends on Linux bio, writeback control, buffer_heads, folios, blk-crypto, fscrypt pagecache bounce pages, cgroup writeback accounting, JBD2 reserved handles, ext4 unwritten extent conversion, per-inode completed I/O lists, and mount option `DATA_ERR_ABORT`. It is used by ext4 writepage/writepages paths that prepare mapped buffers and `ext4_io_submit` state.

## Risks and Edge Cases

Completion ordering is subtle. All buffers in a folio must be marked async before any bio can complete, otherwise writeback could end early. Deferred bios can complete concurrently and are atomically chained through `xchg(&io_end->bio, bio)`. Bounce-page lifetime depends on detecting fscrypt bounce folios and freeing them only when folio writeback finishes. Failed writes to unwritten extents must not convert extents, or stale data could be exposed. Encryption allocation can deadlock if blocking mempool allocation is used for non-first bio pages, so the retry logic submits existing bios or uses nofail only when safe.

## Test Signals

Test coverage should include buffered writeback to mapped, delayed, hole, and unwritten buffers; encrypted file writeback; multi-buffer folios; writeback with block discontinuities; sync and async writeback; I/O error injection; `DATA_ERR_ABORT`; unwritten extent conversion; and concurrent bio completion races. Signals include mapping errors, buffer write I/O error logs, journal aborts, delayed conversion workqueue activity, and absence of stuck folio writeback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/page-io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/readpage.c -->
# sources/distributed-fs/ceph-client/fs/ext4/readpage.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/readpage.c` implements ext4 buffered read and readahead bio assembly for pages/folios without buffer heads in the common contiguous-block case. It also manages post-read processing for fscrypt decryption and fsverity verification. The source was read as a complete 455-line file.

## Important APIs, Types, and Functions

Public entry points are `ext4_read_folio()`, `ext4_readahead()`, `ext4_init_post_read_processing()`, and `ext4_exit_post_read_processing()`. Internal post-read state is `struct bio_post_read_ctx`, with step bits from `enum bio_post_read_step`: `STEP_DECRYPT` and `STEP_VERITY`. Main helpers include `ext4_mpage_readpages()`, `mpage_end_io()`, `bio_post_read_processing()`, `decrypt_work()`, `verity_work()`, `__read_end_io()`, `bio_post_read_required()`, `ext4_set_bio_post_read_ctx()`, and `ext4_readpage_limit()`.

## Control Flow

`ext4_read_folio()` first handles inline data through `ext4_readpage_inline()`. For non-inline reads inside file size, it obtains fsverity info and triggers fsverity metadata readahead, then calls `ext4_mpage_readpages()` for one folio. `ext4_readahead()` skips inline-data files, optionally gets fsverity info, performs fsverity readahead, and passes the readahead control to the same mpage helper.

`ext4_mpage_readpages()` iterates folios from either readahead or a single-folio caller. It refuses folios that already have buffer heads and falls back to `block_read_full_folio()` for unusual layouts. For each folio it uses cached and fresh `ext4_map_blocks()` results to identify mapped contiguous blocks, records the first hole, zeroes holes at EOF or in fully sparse folios, sets mapped-to-disk when fully mapped, and batches contiguous physical blocks into read bios. If a folio has a hole followed by data, non-contiguous blocks, existing buffers, or a mapping error, the code submits any pending bio and falls back to buffer-head read or zero/error handling.

Bio completion runs through `mpage_end_io()`. If fscrypt or fsverity post-read work is required and the bio succeeded, `bio_post_read_processing()` advances steps in order. Decryption is queued to the fscrypt decrypt workqueue. Verity is queued to the fsverity workqueue and frees the mempool context before verification to avoid recursive allocation deadlocks. `__read_end_io()` ends all folio reads with success or failure, frees the post-read context if still attached, and releases the bio.

## State and Persistence Behavior

This file does not modify persistent filesystem metadata. It populates page-cache folios from disk, zero-fills holes, sets folio uptodate or error state through `folio_end_read()`, sets `folio_set_mappedtodisk()` for fully mapped folios, and attaches transient post-read contexts to bios. The post-read context cache and mempool are global runtime resources sized by `NUM_PREALLOC_POST_READ_CTXS`.

## Dependencies and Integration Points

Dependencies include `ext4_map_blocks()`, inline-data read helpers, buffer-head fallback read, folio and readahead APIs, bio allocation/submission, blk-crypto submission, fscrypt bio crypt contexts and decryption workqueues, fsverity info/readahead/verification, and ext4 read tracepoints. The code is wired into ext4 address-space operations through read_folio and readahead hooks.

## Risks and Edge Cases

The optimized path deliberately handles only simple contiguous mappings. Correct fallback is required for blocksize smaller than page size, holes before later mapped blocks, non-contiguous extents, existing buffers, and mapping errors. Verity changes the read limit to `s_maxbytes` so metadata beyond `i_size` can be verified correctly. Post-read ordering must decrypt before verity. The mempool free-before-verity behavior is important because fsverity may initiate nested reads that also need decryption contexts.

## Test Signals

Tests should cover reads and readahead of contiguous files, sparse files with EOF holes, hole-then-data layouts that force fallback, inline data, encrypted files, verity files, encrypted verity files, mapping EIO, folios with preexisting buffers, and large folios. Signals include `trace_ext4_read_folio`, successful folio uptodate state, correct zero-filled holes, fscrypt/fsverity failure propagation, and no mempool deadlocks under nested verity metadata reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/readpage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/resize.c -->
# sources/distributed-fs/ceph-client/fs/ext4/resize.c

## Purpose

`sources/distributed-fs/ceph-client/fs/ext4/resize.c` implements online growth of mounted ext4 filesystems. It validates resize requests, initializes metadata for new block groups and flex groups, updates group descriptor tables and backups, manages the resize inode or conversion to `meta_bg`, extends the final partial group, and publishes new groups to in-memory allocation structures and the on-disk superblock. The source was read as a complete 2192-line file.

## Important APIs, Types, and Functions

Public entry points include `ext4_resize_begin()`, `ext4_resize_end()`, `ext4_group_add()`, `ext4_group_extend()`, `ext4_resize_fs()`, `ext4_kvfree_array_rcu()`, and `ext4_list_backups()`. The key planning type is `struct ext4_new_flex_group_data`, which wraps an array of `struct ext4_new_group_data`, group flags, resize allocation capacity, and count.

Important helpers include `verify_group_input()`, `alloc_flex_gd()`, `ext4_alloc_group_tables()`, `setup_new_flex_group_blocks()`, `verify_reserved_gdb()`, `add_new_gdb()`, `add_new_gdb_meta_bg()`, `reserve_backup_gdb()`, `update_backups()`, `ext4_add_new_descs()`, `ext4_set_bitmap_checksums()`, `ext4_setup_new_descs()`, `ext4_update_super()`, `ext4_flex_group_add()`, `ext4_setup_next_flex_gd()`, `ext4_group_extend_no_check()`, `ext4_convert_meta_bg()`, and bitmap helpers such as `set_flexbg_block_bitmap()`.

## Control Flow

`ext4_resize_begin()` enforces `CAP_SYS_RESOURCE`, checks resize-inode consistency, rejects resizing from a backup superblock, refuses filesystems mounted with errors or `sparse_super2`, and sets `EXT4_FLAGS_RESIZING`. `ext4_resize_end()` clears the flag and optionally refreshes overhead accounting.

`ext4_resize_fs()` is the main grow-to-size path. It first verifies the target block exists on the device and trims bigalloc requests to a cluster boundary. It rejects shrink, no-op, and inode-count overflow cases, computes old/new group and descriptor counts, opens the resize inode when needed, and may convert to `meta_bg` if descriptor growth cannot use resize-inode reservations. It ensures the last group has enough room for required metadata, extends the current last group if only partial capacity remains, allocates flex group and multiblock allocator arrays, then repeatedly plans the next flex group, allocates its metadata block locations, and commits it through `ext4_flex_group_add()`.

`ext4_flex_group_add()` initializes new metadata blocks in one transaction series before exposing the group: backup superblocks/GDTs, inode tables, block bitmaps, inode bitmaps, and bitmap bits for group tables. It then journals superblock access, adds any needed group descriptor blocks, writes descriptors, adds in-memory groupinfo, updates superblock counts and allocation counters, and finally updates backup superblocks and GDT copies. `ext4_group_add()` is the older single-group interface and wraps the same flex-add machinery after validating user-provided group layout. `ext4_group_extend()` only extends the current last group without adding descriptors.

## State and Persistence Behavior

Persistent state includes `s_blocks_count`, free block and inode counters, total inode count, reserved block count, overhead clusters, feature flags (`resize_inode`, `meta_bg`), `s_first_meta_bg`, `s_reserved_gdt_blocks`, group descriptor blocks, backup superblocks/GDTs, block and inode bitmaps, inode tables, resize inode block pointers and `i_blocks`, and group descriptor checksums. In-memory state includes `s_groups_count`, `s_blockfile_groups`, RCU-protected `s_group_desc` arrays, flex group counters, multiblock allocator groupinfo, free cluster and inode percpu counters, and the resizing flag.

The code uses write memory barriers before publishing `s_groups_count`, with comments specifying that readers must pair with read barriers before consuming dependent group data. Replacement group descriptor arrays are freed through RCU via `ext4_kvfree_array_rcu()`.

## Dependencies and Integration Points

This file depends on ext4 superblock and group descriptor formats, JBD2 resize transactions, block bitmap manipulation, inode table zeroing, backup-super selection, resize inode layout, metadata checksums, RCU array publication, multiblock allocator setup, flex_bg accounting, bigalloc cluster math, feature flags, and block-device reads/zeroout. It integrates with ioctl/remount resize paths, mount feature validation, allocator visibility, and backup metadata used by e2fsck.

## Risks and Edge Cases

Online resize cannot roll back arbitrary metadata once journaled, so most helpers validate inputs and allocate memory before mutating on-disk structures. Group geometry must avoid overlaps among bitmaps, inode tables, GDTs, and data space. Descriptor growth must distinguish reserved-GDT resize-inode mode from `meta_bg` mode and convert only when safe. Backup update failure is nonfatal for the resize but marks the filesystem not valid to force fsck. Publishing `s_groups_count` before descriptors and counters are ready would expose invalid allocation space, hence the ordering barriers.

Other edge cases include sparse backup group sequences, non-sparse filesystems reaching descriptor boundaries, bigalloc cluster alignment, partial final groups, inode count overflow, block count overflow, resize inode corruption, memory allocation failures for large flex groups, journal credit exhaustion requiring restarts, and resizing attempts on filesystems with errors or unsupported `sparse_super2`.

## Test Signals

Tests should cover online growth within the last group, adding one group, adding many flex groups, descriptor block boundary crossings, reserved-GDT consumption, conversion to `meta_bg`, bigalloc growth, metadata checksum filesystems, flex_bg accounting, backup superblock/GDT updates, ENOSPC or EIO reading target last block, journal credit batching, and fault injection during bitmap/table/descriptor initialization. Signals include mount logs for resize progress, updated `s_groups_count`, allocator visibility of new groups, valid group descriptor checksums, fsck-clean backup metadata, and forced-fsck state when backup updates fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ext4/resize.c -->
