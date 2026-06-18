# Group Research: group_1036_linux_stable_sources_os_linux_linux_stable_fs_nilfs2_mdt_h_sources__7e5313611609

Scope: `Docs/research_subset_a.md`, NILFS2 files under `sources/os/linux/linux-stable/fs/nilfs2`.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/mdt.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/mdt.h

`mdt.h` declares NILFS metadata-file support. It defines `struct nilfs_mdt_info`, stored in `inode->i_private`, with metadata operation locking (`mi_sem`), per-blockgroup locks, entry sizing, persistent allocator cache, shadow mapping, and block grouping fields.

It also defines `struct nilfs_shadow_map`, used to hold shadow bmap/page-cache state and frozen buffers during metadata operations such as GC DAT shadowing. The header exposes block access and lifecycle operations: `nilfs_mdt_get_block`, `nilfs_mdt_find_block`, delete/forget/fetch-dirty helpers, init/clear/destroy, entry-size setup, and shadow-map save/restore/clear/freeze APIs.

The inline helpers establish key conventions: metadata-file inodes are identified by non-NULL `i_private`; metadata dirty state is tracked with `NILFS_I_DIRTY`; `nilfs_mdt_cno()` reads the filesystem checkpoint number from `the_nilfs`; and `nilfs_mdt_bgl_lock()` retrieves per-blockgroup lock pointers. `NILFS_MDT_GFP` uses reclaim, IO, and highmem allocation flags for metadata pages.

This header is foundational for `sufile.c`, cpfile/dat/ifile code, and segment construction. It abstracts metadata files as ordinary inodes with extra private state and shadow-copy support.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/mdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/namei.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/namei.c

`namei.c` implements NILFS pathname and namespace inode operations. It is derived from ext2/minix namei patterns but wraps all mutating operations in NILFS transactions so namespace updates become part of log construction.

Lookup validates `NILFS_NAME_LEN`, resolves directory entries through `nilfs_inode_by_name()`, loads target inodes with `nilfs_iget()`, treats stale deleted-inode references as filesystem errors, and returns aliases through `d_splice_alias()`. Creation paths (`create`, `mknod`, `symlink`, `mkdir`) allocate inodes with `nilfs_new_inode()`, install proper inode/file/address-space operations, mark inodes dirty, add directory links, and commit or abort the transaction.

Deletion and rename paths use directory helpers from `dir.c`: `nilfs_find_entry`, `nilfs_delete_entry`, `nilfs_dotdot`, `nilfs_set_link`, and `nilfs_empty_dir`. `nilfs_do_unlink()` validates that the directory entry inode matches the dentry inode, repairs zero-link anomalies with a warning, deletes the entry, and drops the target link. `rmdir` requires an empty directory and updates parent/child link counts. `rename` supports only `RENAME_NOREPLACE`, handles target replacement, cross-directory dotdot updates, directory link counts, ctime updates, and dirty marking of affected inodes/directories.

The file also implements export/NFS support. File handles encode checkpoint number, inode number, generation, and optional parent identity in `struct nilfs_fid`; `fh_to_dentry` and `fh_to_parent` resolve through `nilfs_lookup_root()` and `nilfs_iget()`. This checkpoint-aware handle format is important because NILFS snapshots expose historical roots.

Published operation tables are `nilfs_dir_inode_operations`, `nilfs_special_inode_operations`, `nilfs_symlink_inode_operations`, and `nilfs_export_ops`. The directory operations surface standard VFS entry points plus NILFS file attributes and fiemap hooks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/nilfs.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/nilfs.h

`nilfs.h` is the local central header for NILFS. It defines `struct nilfs_inode_info`, embedding the VFS inode plus NILFS state: flags, inode type, dynamic state bits, bmap storage, xattr pointer, directory lookup hint, GC checkpoint number, associated inode for btree/shadow caches, dirty-list node, optional xattr semaphore, raw inode buffer, and current root pointer.

The dynamic inode state enum tracks lifecycle and segment-constructor coordination: new, dirty, queued, busy, collected, updated, inode-sync blocked, and bmap-attached states. In-memory inode type flags distinguish normal, GC, btree-node-cache, and shadow-cache inodes. Inode-number macros define metadata/system/private inode classification and validate user/system inode ranges.

The header defines NILFS transaction context (`struct nilfs_transaction_info`) stored in `current->journal_info`. Flags indicate dynamic allocation, sync construction request, GC context, segment-constructor writer context, and whether a commit happened. Inline helpers expose transaction flag setting/testing and convenience checks for GC/construction contexts.

It declares cross-file APIs for directory operations, file sync, ioctls, inode allocation/loading/dirtying/truncation/fiemap, superblock management, GC inode reads, sysfs, operation tables, and filesystem type registration. It also centralizes logging macros (`nilfs_msg`, `nilfs_error`, severity wrappers) and inode flag inheritance/masking rules.

Important mount/filesystem constants include `NILFS_MAX_VOLUME_NAME`, `NILFS_ATIME_DISABLE`, superblock commit flags, and inherited file flags. This header is the common dependency tying VFS, metadata files, segment writer, recovery, and mount code together.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/page.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/page.c

`page.c` implements NILFS-specific folio and buffer-head handling. It provides buffer grabbing, state copying, dirty clearing, shadow-cache page copying, and discovery of delayed/uncommitted extents.

`nilfs_grab_buffer()` grabs or creates the folio for a block offset, creates buffers as needed, waits on the selected buffer, sets its block device, and returns the buffer. `nilfs_forget_buffer()` clears uptodate/dirty/mapped/async/write/delay/NILFS-specific state bits, resets the block number, clears folio uptodate/mapped state, and drops the buffer reference. `nilfs_copy_buffer()` copies data and inherent buffer state while updating destination folio uptodate/mapped state based on all buffers in the folio.

For shadow metadata handling, `nilfs_copy_dirty_pages()` copies dirty tagged folios from one mapping to another, preserving dirty buffer states; `nilfs_copy_back_pages()` copies or moves folios from a shadow mapping back into the original mapping without adding pages during the process. These functions are used by metadata shadow-map code in `mdt.c`.

Dirty-state cleanup is deliberately careful. `nilfs_clear_dirty_pages()` iterates dirty tagged folios and calls `nilfs_clear_folio_dirty()` only if the folio still belongs to the mapping. `nilfs_clear_folio_dirty()` refuses to clear busy/locked buffer sets until after invalidating bh LRUs, clears NILFS buffer state bits, resets folio state, and calls `__nilfs_clear_folio_dirty()`, which updates xarray dirty tags under the mapping lock before clearing dirty-for-IO.

`nilfs_find_uncommitted_extent()` scans contiguous cached folios for buffers marked delayed, returning the first extent length and start block. This is used by inode/writeback logic to reason about uncommitted delayed allocation ranges.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/page.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/page.h

`page.h` declares NILFS buffer/folio helper APIs and extended buffer-head state bits. Custom bits start at `BH_PrivateStart`: allocated, NILFS node, volatile, checked, and redirected. It creates buffer flag helpers for node, volatile, checked, and redirected states.

The exported functions cover buffer acquisition and disposal (`nilfs_grab_buffer`, `nilfs_forget_buffer`), buffer copying, folio cleanliness checks, diagnostic bug output, dirty-page copying and copy-back, dirty-state clearing, clean-buffer counting in a byte range, and delayed/uncommitted extent scanning.

The `NILFS_FOLIO_BUG` macro prints detailed folio/buffer diagnostics via `nilfs_folio_bug()` and then triggers `BUG()`. This header is consumed by metadata, btree node, inode, segment, and recovery code that needs NILFS-specific buffer state handling.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/page.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/recovery.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/recovery.c

`recovery.c` implements mount-time log validation, latest-super-root search, and roll-forward recovery of data-sync logs written after the latest checkpoint. It defines internal segment validation result codes and recovery work records for data blocks.

Checksum and validation flow is central. `nilfs_compute_checksum()` computes CRC32 across one or more contiguous blocks. `nilfs_read_super_root_block()` reads and optionally validates a super-root block checksum. `nilfs_validate_log()` checks segment summary magic, sequence number, block-count bounds, and full-log checksum. Validation failures are translated to warnings or errors by `nilfs_warn_segment_error()`.

Summary parsing helpers walk segment summary blocks across block boundaries. `nilfs_scan_dsync_log()` parses file info and virtual block info entries for data-sync logs, creating `nilfs_recovery_block` records with inode, physical block, virtual block, and file block offset. `nilfs_recover_dsync_blocks()` loads each inode from the recovered root, prepares a write_begin path, copies old log data into the page cache, marks files dirty, and counts salvaged blocks.

`nilfs_search_super_root()` starts from the superblock’s last partial segment, validates partial segments in sequence, follows `ss_next` across full segments, records used segments, and updates `the_nilfs` cursor fields (`ns_pseg_offset`, `ns_seg_seq`, `ns_segnum`, `ns_cno`, `ns_ctime`, `ns_nextnum`) when it finds a valid super root. If newer logs without a super root are found after the last checkpoint, it records roll-forward bounds in `nilfs_recovery_info`.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint, performs roll-forward if needed, prepares segment usage state for recovery, attaches a temporary log writer, constructs a recovery segment, detaches the writer, and post-cleans the roll-forward start block when appropriate. Failed roll-forward aborts by purging dirty recovery inodes from `ns_dirty_files`.

Segment preparation interacts heavily with `sufile`: it frees the obsolete next segment, scraps segments written after the latest super root so they are not immediately reused, allocates a fresh segment for recovery output, and advances sequence state. This file is the bridge between on-disk log scanning and normal segment construction.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segbuf.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/segbuf.c

`segbuf.c` implements segment-buffer allocation, mapping, summary construction, CRC insertion, and BIO submission. A segment buffer represents one partial segment: summary buffers, payload buffers, optional super-root buffer, disk location, block counts, next segment pointer, and asynchronous BIO completion/error state.

Mapping helpers place a segment buffer either at a full segment and offset (`nilfs_segbuf_map`) or immediately after a previous partial segment (`nilfs_segbuf_map_cont`). `nilfs_segbuf_set_next_segnum()` stores the next full segment’s block address in the in-memory summary. Reset and extend helpers allocate summary/payload buffers from the block device mapping and update in-memory counts.

`nilfs_segbuf_fill_in_segsum()` writes the raw segment summary header fields: magic, bytes, flags, sequence, creation time, next block, block counts, file info count, summary byte count, padding, and checkpoint number. CRC helpers compute separate summary, data, and super-root checksums. Data CRC covers summary blocks and payload blocks by temporarily mapping payload folios.

Log list helpers clear/truncate/destroy segment buffers and write/wait across a list. `nilfs_add_checksums_on_logs()` applies all relevant checksums after payload writeback has been prepared by the segment constructor.

BIO submission uses `struct nilfs_write_info` to pack buffers into block-device write BIOs. Each BIO completion increments `sb_err` on failure and completes `sb_bio_event`. `nilfs_segbuf_write()` submits summary buffers followed by payload buffers, marking the final BIO `REQ_SYNC`; `nilfs_segbuf_wait()` waits for all outstanding BIOs and reports a log-write I/O error with start block, block count, and segment number.

This file does not decide what to write; `segment.c` builds the segment content and uses `segbuf.c` to serialize it to disk.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segbuf.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/segbuf.h

`segbuf.h` defines in-memory segment summary and segment buffer structures. `struct nilfs_segsum_info` tracks flags, file-info count, block counts, summary bytes, file block count, segment sequence, checkpoint number, creation time, and next segment block. `struct nilfs_segment_buffer` adds superblock back pointer, list linkage, segment numbers/ranges, partial segment start, remaining blocks, summary/payload buffer lists, optional super-root buffer, and BIO completion/error fields.

The header provides list macros for segment buffers and buffer-head traversal through `b_assoc_buffers`. Inline helpers classify a partial segment as simplex (`LOGBGN|LOGEND`) or empty, and add summary, payload, and file buffers while updating block counters. File-buffer addition takes an extra buffer reference and increments the file-block count.

Declared APIs cover segment-buffer allocation/freeing, mapping, next-segment setup, reset, extension, summary fill, log-list cleanup/truncation/destruction, write/wait, and checksum application. It also declares the slab cache `nilfs_segbuf_cachep`, created in `super.c`.

This header is shared primarily by `segment.c`, `recovery.c`, and `segbuf.c`, defining the transport object for NILFS log writes.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segment.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/segment.c

`segment.c` is the NILFS segment constructor and log-writer implementation. It owns transaction locking, dirty-file collection, segment summary construction, physical block assignment, writeback preparation/completion, checkpoint finalization, GC segment cleaning, synchronous fsync/dsync paths, and the background `segctord` kernel thread.

Transactions use `current->journal_info` with `struct nilfs_transaction_info`. `nilfs_transaction_begin()` nests correctly, starts an internal write, takes `ns_segctor_sem` read-locked, and optionally checks disk fullness. `nilfs_transaction_commit()` marks commits, schedules or forces segment construction depending on dirty state/watermark/sync flags, releases the semaphore, and triggers `nilfs_construct_segment()` when needed. Writer-side construction uses write locking through `nilfs_transaction_lock()`/`unlock()` and marks GC or writer context flags.

Segment construction is stage based: init, GC files, regular files, ifile, cpfile, sufile, DAT, super root, dsync, done. `struct nilfs_sc_operations` abstracts how file, DAT, and dsync blocks are collected and how their binfo entries are serialized. Dirty data buffers come from page-cache dirty tags; dirty btree/node buffers come from associated btnode caches and bmap lookup. Each collected file gets `finfo` and per-block `binfo` entries in the segment summary.

`nilfs_segctor_begin_construction()` creates the initial segment buffer, maps it to current segment position, shifts to a new segment if too little space remains, marks current segment usage dirty, and allocates the next segment if starting a new full segment. Retry logic in `nilfs_segctor_collect()` extends segment-buffer capacity when the logical segment grows too large after metadata stages, doubling added segments up to `SC_MAX_SEGDELTA`, and cancels provisional sufile frees if it must retry.

Block assignment is delayed until after collection. `nilfs_segctor_update_payload_blocknr()` walks segment payload buffers, assigns physical log block numbers through bmap, replaces redirected buffers when needed, and fills binfo entries using the appropriate file/DAT/dsync writer. `nilfs_segctor_assign()` then fills raw segment summary headers.

Write preparation is cautious: payload folios are put into writeback before checksums are calculated, summary and super-root buffers are dirtied and put into writeback, and then checksums are added. `nilfs_segctor_write()` submits logs through `segbuf.c`; `nilfs_segctor_wait()` waits and completes. Completion clears dirty/delay/volatile/redirected bits, ends folio writeback, drops collected inode state, advances `the_nilfs` segment cursor, updates checkpoint number and last segment when a super root was written, and clears metadata dirty state. Abort paths wait for in-flight logs, redirty affected inodes, cancel segment usage updates, free incomplete allocations, and destroy segment buffers.

`nilfs_segctor_do_construct()` is the main construction loop. It collects dirty files, decides if there is work, builds one or more partial segments, finalizes checkpoint metadata when producing a super-root log, fills the super root, updates sufile segment usage, writes logs, and may wait immediately for blocksize less than page size to avoid double-buffering issues.

The public APIs are `nilfs_construct_segment()` for synchronous full logical segment construction, `nilfs_construct_dsync_segment()` for data-only fsync-style logs, `nilfs_clean_segments()` for GC, `nilfs_attach_log_writer()` and `nilfs_detach_log_writer()` for writer lifecycle, plus `nilfs_relax_pressure_in_lock()` for reclaim pressure. The background thread waits on timer/request/flush conditions, chooses flush-file, flush-DAT, or super-root modes, handles freezer state, and marks discontinued superblock state when needed.

This is the operational core of NILFS’s log-structured design. It coordinates VFS dirty state, metadata files, segment usage allocation, checkpoint creation, log checksums, asynchronous block writes, and recovery-visible cursor updates.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segment.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/segment.h

`segment.h` declares recovery state and segment-constructor state. `struct nilfs_recovery_info` stores whether recovery is needed, last super-root block/checkpoint, roll-forward bounds and sequence, used segment list, last partial segment location, sequence, current segment number, and next segment number. Recovery flags distinguish super-root update detection from completed roll-forward.

`struct nilfs_cstage` stores collection stage count, flags, and cursor pointers for dirty-file and GC-inode iteration. `struct nilfs_sc_info` is the full segment-constructor object: superblock/root, block increments, dirty/GC/iput lists, freeseg array, dsync target/range, segment-buffer lists, current segment, summary-entry cursors, block counters, checkpoint/time fields, internal flags, request state, wait queues, request sequence counters, sync flag, timing/watermark settings, timer, and thread pointer.

Constructor flags track dirty metadata, unclosed logical segments, whether the latest segment has a super root, prior flush pressure, and whether a checkpoint has changes beyond core metadata/GC movement. State includes `NILFS_SEGCTOR_COMMIT`.

The header declares default timeout, super-root frequency, watermark, cleanup retry count, and external APIs implemented in `segment.c` and `recovery.c`: construction, dsync construction, GC cleaning, log-writer attach/detach, super-root reading/searching, orphan-log salvage, and segment-list disposal.

This header is the state contract between mount/recovery/superblock code and the segment writer.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/segment.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sufile.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/sufile.c

`sufile.c` implements the NILFS segment usage metadata file. It tracks clean/dirty/error segment state, allocation ranges, live block counts, modification times, resize behavior, user-visible suinfo queries/updates, and discard trimming of clean segments.

`struct nilfs_sufile_info` embeds `nilfs_mdt_info` and adds cached clean-segment count plus allocatable segment bounds. Helpers compute the metadata block and entry offset for a segment number, account for the header block’s first-entry offset, and retrieve header or segment-usage blocks through `nilfs_mdt_get_block()`.

Update primitives serialize on `NILFS_MDT(sufile)->mi_sem`. `nilfs_sufile_update()` and `nilfs_sufile_updatev()` validate segment numbers, fetch the header and affected usage blocks, then invoke operation callbacks. Callback primitives implement cancel-free, scrap, free, and set-error semantics while keeping on-disk header counters and cached `ncleansegs` consistent.

Allocation scans from `sh_last_alloc + 1`, wraps through the configured alloc range and then the rest of the segment space as allowed, finds clean segment entries, marks them dirty, updates clean/dirty counters and last allocation, marks metadata dirty, and returns `-ENOSPC` if none are available. `nilfs_sufile_mark_dirty()` marks an existing segment dirty but refuses erroneous active segments. `nilfs_sufile_set_segment_usage()` updates live block count and optional modification time after a write.

Resize is guarded by the metadata semaphore and checks reserved-segment/free-space constraints. Shrinking calls `nilfs_sufile_truncate_range()`, which rejects dirty or active segments, clears error flags to clean when possible, deletes complete metadata blocks as holes, updates counters, and tightens allocation bounds immediately to prevent allocation into truncated space. Expansion adjusts clean segment count and global segment count.

User-facing information APIs include `nilfs_sufile_get_stat()`, `nilfs_sufile_get_suinfo()`, and `nilfs_sufile_set_suinfo()`. `get_suinfo` projects the active flag dynamically rather than reading it from disk. `set_suinfo` validates update flags and block counts, strips the virtual active flag before writing, and updates header counters based on clean/dirty transitions.

`nilfs_sufile_trim_fs()` implements fstrim over clean segments. It maps byte ranges to segment ranges, coalesces contiguous clean segments into discard extents, clamps to the requested range, honors `minlen`, and writes the discarded byte count back to `range->len`.

`nilfs_sufile_read()` loads the sufile inode, initializes metadata-file private state, validates segment usage entry size, reads the header, caches clean count, and initializes allocation range to all segments. This file is central to segment allocation by `segment.c`, recovery preparation by `recovery.c`, resize by `super.c`, and ioctls.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sufile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sufile.h -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/sufile.h

`sufile.h` declares the segment usage file interface. It exposes segment count/clean count accessors, allocation range setup, single-segment allocation, dirty marking, segment usage updates, stats and suinfo get/set operations, resize, sufile inode loading, and fstrim handling.

The generic update APIs accept callbacks that receive the sufile inode, segment number, header block, and usage block. The header declares callback primitives for scrap, free, cancel-free, and set-error operations.

Inline wrappers define the common operations used elsewhere: `nilfs_sufile_scrap()` makes a segment garbage/dirty, `nilfs_sufile_free()` frees one segment, `nilfs_sufile_freev()` frees multiple segments, `nilfs_sufile_cancel_freev()` re-dirties segments whose freeing is being rolled back, and `nilfs_sufile_set_error()` permanently marks a segment erroneous.

The comments make the error model explicit for `set_error`: invalid segment, metadata I/O/corruption, and allocation failure. The header depends on `mdt.h` because sufile is implemented as a NILFS metadata file.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/sufile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/super.c -->
# File Research: sources/os/linux/linux-stable/fs/nilfs2/super.c

`super.c` implements NILFS module registration, slab cache setup, superblock operations, mount context parsing, mount/reconfigure flow, filesystem resize, dual-superblock commit logic, snapshot attachment, and error handling.

Logging and error handling are centralized through `__nilfs_msg()` and `__nilfs_error()`. Metadata corruption calls set `NILFS_ERROR_FS` on on-disk superblocks, may remount read-only for `errors=remount-ro`, and may panic for `errors=panic`. `nilfs_alloc_inode()` initializes NILFS-specific inode fields; `nilfs_free_inode()` destroys metadata-private state before returning the inode object to the slab.

Superblock persistence uses two superblocks. `nilfs_prepare_super()` repairs/copies from the valid twin if one magic is bad and can flip active superblocks. `nilfs_commit_super()` updates write time and CRC, optionally both copies, clears dirty state, marks the device flushed, and calls `nilfs_sync_super()`. `nilfs_sync_super()` uses barriers/FUA when enabled, falls back to the alternate superblock after I/O failure, and updates GC protection sequence. `nilfs_cleanup_super()` restores clean state on unmount/remount-ro/freeze and commits one or both copies depending on checkpoint alignment.

`nilfs_resize_fs()` validates requested size against device size and minimum constraints, takes the segment-constructor write lock while resizing sufile segment count, forces segment construction, relocates the secondary superblock, updates device size and segment count in both superblocks, commits all, and only then expands the allocatable segment range. That ordering protects the secondary superblock location during expansion.

Super operations include inode allocation/free, dirty/evict hooks, put_super, sync_fs, freeze/unfreeze, statfs, and show_options. `nilfs_sync_fs()` may construct a segment, commits dirty superblock state, and flushes the block device. `nilfs_statfs()` computes blocks from segment geometry, subtracts reserved segment blocks from available space, and queries ifile for inode counts with an `-ERANGE` fallback.

Mount options are parsed through fs_context: `errors=`, `barrier/nobarrier`, `cp=`, `order=relaxed|strict`, `norecovery`, and `discard/nodiscard`. `cp=` is invalid on remount and requires read-only mounting. Default options are `errors=remount-ro` and barrier enabled.

Mounting flows through `nilfs_get_tree()` and `nilfs_fill_super()`. `nilfs_fill_super()` allocates and initializes `the_nilfs`, installs super/export operations, loads NILFS metadata, sets UUID/sysfs name, attaches the latest checkpoint, starts the log writer for read-write mounts, builds the root dentry, and marks the superblock mounted/dirty as needed. Snapshot mounts validate that the checkpoint is a snapshot and attach a root dentry for that checkpoint. Existing superblocks are reused carefully, rejecting conflicting read-only/read-write mounts when the live tree is busy.

Reconfiguration handles read-write to read-only by syncing and cleaning the superblock, and read-only to read-write by checking unsupported read-only-compatible features, clearing `SB_RDONLY`, attaching the log writer, and setting up the superblock. It refuses remount when recovery is incomplete.

The bottom of the file registers `nilfs_fs_type`, allocates/destroys slab caches for inodes, transaction contexts, segment buffers, and btree paths, initializes sysfs, registers/unregisters the filesystem, and provides module init/exit.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/nilfs2/super.c -->