# Group Research: NILFS2 metadata, namespace, page-cache, segment, recovery, and superblock paths

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/mdt.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/mdt.h

`mdt.h` defines the shared in-memory framework for NILFS metadata files such as DAT, cpfile, sufile, and ifile. `struct nilfs_mdt_info` is stored in `inode->i_private` and carries the metadata operation semaphore, per-blockgroup locks, entry sizing, persistent allocator cache, optional shadow mapping, and group geometry.

The header also defines `struct nilfs_shadow_map`, used when metadata updates need a recoverable shadow copy of bmap state and page cache contents. This is central to cleaner/GC flows that must stage metadata changes and roll them back on failure.

Important interfaces include metadata block lookup/allocation/deletion (`nilfs_mdt_get_block`, `nilfs_mdt_find_block`, `nilfs_mdt_delete_block`, `nilfs_mdt_forget_block`), dirty detection (`nilfs_mdt_fetch_dirty`), lifecycle (`nilfs_mdt_init`, `nilfs_mdt_clear`, `nilfs_mdt_destroy`), entry layout setup, and shadow-map save/restore/clear/freeze helpers.

The inline helpers mark or clear `NILFS_I_DIRTY` on the owning NILFS inode, expose the current checkpoint number via `nilfs_mdt_cno()`, and return blockgroup locks for palloc-style metadata. The design assumes only metadata inodes have non-NULL `i_private`; `nilfs_is_metadata_file_inode()` is used by inode destruction in `super.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/mdt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/namei.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/namei.c

`namei.c` implements NILFS VFS pathname operations and NFS export file-handle support. The implementation follows ext2/minix-style directory manipulation, but every mutating namespace operation is wrapped in NILFS transactions so changes become part of log construction.

Core operations include lookup, create, mknod, symlink, hard link, mkdir, unlink, rmdir, and rename. Creation paths allocate a NILFS inode, install inode/file/address-space operations, mark it dirty, then link it into the directory with `nilfs_add_link()`. `nilfs_add_nondir()` centralizes the success path (`d_instantiate_new`) and failure cleanup for non-directory objects.

Removal and rename use directory-entry helpers from `dir.c`: `nilfs_find_entry`, `nilfs_delete_entry`, `nilfs_set_link`, `nilfs_dotdot`, and `nilfs_empty_dir`. Link counts and ctime are adjusted explicitly. `nilfs_rename()` supports only `RENAME_NOREPLACE`; other flags return `-EINVAL`. Directory renames update `..` when crossing parent directories.

Symlinks are stored through `page_symlink()` with `nilfs_aops`; names longer than one filesystem block are rejected. Lookup rejects names longer than `NILFS_NAME_LEN`, resolves inode numbers via `nilfs_inode_by_name()`, and treats `-ESTALE` from `nilfs_iget()` as on-disk inconsistency.

Export support encodes checkpoint number, inode number, generation, and optional parent identity in `struct nilfs_fid`. `nilfs_get_dentry()` resolves handles through `nilfs_lookup_root()` and `nilfs_iget()`, which makes exported snapshots/checkpoints addressable by checkpoint number.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/namei.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/nilfs.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/nilfs.h

`nilfs.h` is the main private header for NILFS. It defines `struct nilfs_inode_info`, the filesystem-specific inode wrapper containing inode flags, dynamic NILFS inode state, bmap storage, xattr state, dirty-list linkage, on-disk inode buffer pointer, root pointer, and embedded VFS inode.

It defines dynamic inode state bits such as `NILFS_I_DIRTY`, `NILFS_I_QUEUED`, `NILFS_I_BUSY`, `NILFS_I_COLLECTED`, `NILFS_I_UPDATED`, `NILFS_I_INODE_SYNC`, and `NILFS_I_BMAP`. These are heavily used by `segment.c` to move inodes through dirty collection, writeback, and cleanup. It also defines inode type flags for normal, GC, btree-node-cache, and shadow-cache inodes.

The header contains inode-number classification macros for metadata/system/private inodes, including DAT, cpfile, sufile, ifile, root, atime, and sketch inode ranges. These macros gate validity checks, mount behavior, and export handling.

`struct nilfs_transaction_info` and transaction flag definitions support the log-construction transaction model. Helpers inspect current task `journal_info` to detect GC or writer context.

The file declares cross-subsystem APIs for directory operations, file sync, ioctl, inode read/write/dirty/truncate/fiemap, superblock operations, GC inode access, sysfs groups, and VFS operation tables. POSIX ACL support is explicitly disabled with a compile-time error if configured, while the fallback `nilfs_init_acl()` applies umask for non-symlink inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/page.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/page.c

`page.c` implements NILFS-specific folio and buffer-head handling. It manages buffer states beyond the generic buffer flags, copies buffers between normal and shadow mappings, clears dirty state safely, and locates delayed/uncommitted extents.

`nilfs_grab_buffer()` grabs or creates the folio containing a logical block offset, returns the requested buffer head, waits on it, and assigns the filesystem block device. `nilfs_forget_buffer()` clears mapping/dirty/uptodate/delay/NILFS-specific state, resets `b_blocknr`, updates folio state, and releases the buffer.

`nilfs_copy_buffer()` and the internal `nilfs_copy_folio()` copy data and selected buffer flags while preserving page-level uptodate/mappedtodisk consistency. `nilfs_copy_dirty_pages()` copies dirty folios from one address space to another, preserving dirty buffers; `nilfs_copy_back_pages()` copies or moves shadow-cache folios back into the original mapping.

Dirty cleanup is careful around buffer references. `nilfs_clear_folio_dirty()` clears a folio only after confirming buffers are not busy, retrying after invalidating buffer-head LRU state. `__nilfs_clear_folio_dirty()` directly updates the xarray dirty tag and folio dirty state, supporting cases where NILFS must cancel dirty accounting outside ordinary writeback.

`nilfs_find_uncommitted_extent()` scans contiguous cached folios for `BH_Delay` buffers and returns the first delayed extent length and block offset. This is used to find data not yet committed into a NILFS log.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/page.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/page.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/page.h

`page.h` declares NILFS buffer/folio helpers and defines NILFS-specific buffer-head state bits starting at `BH_PrivateStart`: allocated, node, volatile, checked, and redirected. Generated `BUFFER_FNS` helpers expose node, volatile, checked, and redirected predicates/setters.

The declared API covers buffer acquisition, forgetting, copying, clean-buffer checks, dirty-page copying between mappings, shadow-copy restoration, dirty-page clearing, counting clean buffers over a folio byte range, and finding uncommitted delayed extents.

`NILFS_FOLIO_BUG()` prints detailed folio/buffer diagnostics via `nilfs_folio_bug()` and then triggers `BUG()`. This is used when NILFS detects impossible page-cache state during metadata/data copying.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/page.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/recovery.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/recovery.c

`recovery.c` validates NILFS logs, finds the newest usable super root, and optionally rolls forward orphan data-sync logs written after the last checkpoint. It is the mount-time recovery companion to segment construction.

The file defines internal segment validation results and maps them to warnings or errors. `nilfs_compute_checksum()` calculates CRCs over contiguous log blocks. `nilfs_read_super_root_block()` reads and optionally verifies a super root checksum. `nilfs_validate_log()` checks segment summary magic, sequence number, block-count bounds, and full-log data checksum.

Summary parsing helpers walk segment summary blocks across block boundaries. `nilfs_scan_dsync_log()` extracts per-file data block records from data-sync logs into `struct nilfs_recovery_block` entries, recording inode number, disk block, virtual block, and file block offset.

`nilfs_search_super_root()` starts from the superblock’s last partial segment and follows segment summaries, validating each log, tracking sequence numbers, next segment numbers, latest checkpoint number, and possible newer orphan logical segments. It updates `the_nilfs` cursor fields such as `ns_pseg_offset`, `ns_seg_seq`, `ns_segnum`, `ns_cno`, `ns_ctime`, and `ns_nextnum`.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint, scans newer data-sync logs, copies recoverable data blocks back into files with `block_write_begin()`/`block_write_end()`, prepares fresh segments, constructs a recovery segment, and then zeroes the old roll-forward start block when needed. Failure paths abort roll-forward by purging dirty recovery inodes.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/recovery.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segbuf.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/segbuf.c

`segbuf.c` implements segment-buffer allocation, mapping, segment-summary construction, checksum filling, log BIO submission, and write completion waiting. Segment buffers are the in-memory representation of one partial segment being written.

`nilfs_segbuf_new()` allocates from `nilfs_segbuf_cachep`, initializes summary/payload lists, completion state, and I/O counters. Mapping helpers place a segment buffer either at a full segment plus offset or immediately after a previous partial segment. `nilfs_segbuf_reset()` starts a fresh summary block and initializes flags, checkpoint number, creation time, and counters.

`nilfs_segbuf_fill_in_segsum()` serializes the in-memory summary into the first summary block. CRC helpers compute and store summary checksum, payload checksum, and super-root checksum. Data CRC includes segment summary blocks and all payload buffer data.

Payload and summary buffer lists are released by `nilfs_clear_logs()` and `nilfs_truncate_logs()`. `nilfs_add_checksums_on_logs()` walks all logs and fills super-root, summary, and data checksums before write submission.

The write path batches sequential segment buffers into BIOs using `bio_alloc()`, `bio_add_folio()`, and `submit_bio()`. Completion increments `sb_err` on I/O failure and signals `sb_bio_event`; `nilfs_segbuf_wait()` waits for all BIOs and returns `-EIO` if any failed.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segbuf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segbuf.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/segbuf.h

`segbuf.h` declares segment-buffer structures and list helpers. `struct nilfs_segsum_info` stores the in-memory summary fields later serialized into `struct nilfs_segment_summary`: flags, file-info count, total blocks, summary blocks, summary byte count, file-block count, segment sequence, checkpoint number, creation time, and next-segment block.

`struct nilfs_segment_buffer` tracks the mapped full segment, partial segment start, remaining blocks, summary buffers, payload buffers, optional super-root buffer, outstanding BIO count, error status, and completion event.

The header provides list macros for segment buffers and buffer-head lists, plus inline helpers for checking whether a log is “simplex” (`LOGBGN|LOGEND`), empty, and for adding summary, payload, or file buffers. Adding a file buffer takes an extra buffer reference and increments file-block accounting.

Public functions cover segment-buffer lifecycle, mapping, next-segment setup, summary/payload extension, summary serialization, log cleanup/truncation/destruction, log writing/waiting, and checksum insertion.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segment.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/segment.c

`segment.c` is the NILFS segment constructor and log-writer implementation. It coordinates transactions, dirty inode collection, metadata checkpointing, segment allocation, log summary generation, payload block assignment, BIO submission, completion cleanup, GC segment cleaning, and the background `segctord` thread.

The transaction layer stores `struct nilfs_transaction_info` in `current->journal_info`, supports nesting, and serializes ordinary filesystem operations against segment construction using `ns_segctor_sem`. Commits schedule the constructor timer or force synchronous construction depending on flags and dirty pressure.

Log construction is stage-based: GC inodes, dirty files, ifile, cpfile, sufile, DAT, super root, and data-sync stages. `nilfs_segctor_collect_blocks()` advances through these stages, collecting dirty data buffers, btree node buffers, and bmap buffers via operation tables for normal files, DAT, and dsync logs.

Segment buffers are allocated and extended as needed. The constructor marks current/next segments dirty in sufile, allocates additional next segments, writes file-info and block-info entries into segment summaries, assigns physical block numbers through bmaps, finalizes checkpoints, fills the super root, updates segment usage live-block counts, computes checksums, and writes logs.

Write completion clears dirty/writeback/delay/volatile/redirected buffer state, updates `the_nilfs` next-segment cursor, advances checkpoint state when a super root is written, drops collected inode state, and clears metadata dirty bits. Abort paths cancel segment usage, free incomplete allocations, restore freed segments when needed, redirty collected inodes, and preserve consistency after I/O or construction failure.

Public entry points include `nilfs_construct_segment()` for synchronous checkpoint/log construction, `nilfs_construct_dsync_segment()` for data-only fsync-style logs, `nilfs_clean_segments()` for cleaner-driven GC with DAT shadow-map rollback support, and `nilfs_attach_log_writer()`/`nilfs_detach_log_writer()` for lifecycle.

The background `segctord` thread waits on requests, timers, and flush bits, chooses between full checkpoint, file flush, and DAT flush modes, handles freezer integration, and ensures outstanding waiters are awakened during teardown.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segment.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/segment.h

`segment.h` defines the public structures and interfaces for NILFS recovery and segment construction. `struct nilfs_recovery_info` stores search/recovery state: recovery flags, latest super-root block/checkpoint, roll-forward range, starting sequence, used-segment list, last partial segment location, sequence, segment number, and next segment number.

`struct nilfs_cstage` tracks the segment constructor’s collection stage, including the stage counter, collection flags, current dirty-file pointer, and current GC-inode pointer. Stage transitions are instrumented from `segment.c`.

`struct nilfs_sc_info` is the complete segment-constructor state object. It stores root/superblock pointers, dirty and GC inode lists, deferred iput work, segments to free, dsync target/range, active and writing segment-buffer lists, summary write cursors, block counters, checkpoint and time state, constructor flags, wait queues, request sequence counters, flush state, timer, thread pointer, interval, checkpoint frequency, and watermark.

The header defines constructor flags (`NILFS_SC_DIRTY`, `NILFS_SC_UNCLOSED`, `NILFS_SC_SUPER_ROOT`, `NILFS_SC_PRIOR_FLUSH`, `NILFS_SC_HAVE_DELTA`), request state (`NILFS_SEGCTOR_COMMIT`), cleanup retry count, default constructor timeout, super-root frequency, and dirty-buffer watermark.

Declared interfaces connect superblock/recovery code to segment construction: synchronous segment construction, dsync construction, cleaner segment cleaning, log-writer attach/detach, super-root search, roll-forward salvage, and segment-list disposal.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/segment.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sufile.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/sufile.c

`sufile.c` implements the NILFS segment usage metadata file. It tracks clean, dirty, active, and erroneous segments; allocates new segments; frees/scraps/cancels segments; exposes usage stats to ioctl callers; supports resize; and issues discard/TRIM over clean segment ranges.

`struct nilfs_sufile_info` embeds `nilfs_mdt_info` and adds cached clean-segment count plus an allocatable segment-number range. Helpers map segment numbers to metadata block offsets and entry offsets using metadata entry sizing from `mdt.h`.

Update helpers serialize changes under `NILFS_MDT(sufile)->mi_sem`. `nilfs_sufile_update()` and `nilfs_sufile_updatev()` fetch the header and relevant usage blocks, then invoke primitive operations such as scrap, free, cancel-free, or set-error. Header clean/dirty counters and the cached `ncleansegs` value are kept in sync.

`nilfs_sufile_alloc()` scans from the last allocation within the configured range, wraps through the range and fallback regions, finds a clean segment, marks it dirty, decrements clean count, increments dirty count, stores `sh_last_alloc`, marks metadata dirty, and returns the selected segment. `nilfs_sufile_mark_dirty()` protects active or allocated segments and rejects erroneous active segments.

`nilfs_sufile_resize()` grows or shrinks the segment array. Shrinking verifies the truncated range contains only clean/error segments and no active segments, deletes full usage blocks as holes, updates counters, and adjusts allocation bounds before publishing the new segment count.

`nilfs_sufile_get_suinfo()` and `nilfs_sufile_set_suinfo()` implement bulk user-visible segment-usage inspection/update, masking the active flag on disk because active is a runtime projection. `nilfs_sufile_trim_fs()` coalesces clean contiguous segment ranges and calls `blkdev_issue_discard()`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sufile.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sufile.h -->
# File Research: sources/os/linux/linux/fs/nilfs2/sufile.h

`sufile.h` declares the segment usage file API. It exposes segment count/clean count queries, allocation range control, segment allocation, dirty marking, usage live-block/time updates, stats retrieval, bulk suinfo get/set, resize, read/init, and TRIM support.

The update API allows callers to apply primitive operations to one or many segment numbers while holding the sufile metadata semaphore. Primitive functions include scrap, free, cancel-free, and set-error.

Inline wrappers provide semantic operations: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, and `nilfs_sufile_set_error()`. Their comments document expected error classes for invalid segment numbers, I/O/corruption, and allocation failures.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/sufile.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/super.c -->
# File Research: sources/os/linux/linux/fs/nilfs2/super.c

`super.c` implements NILFS module setup, slab caches, filesystem registration, superblock commit/cleanup, mount/remount/freeze/sync/statfs behavior, snapshot mounting, checkpoint attachment, and resize.

Error handling is centralized through `__nilfs_error()`, which logs metadata inconsistency, sets `NILFS_ERROR_FS` on disk, optionally remounts read-only for `errors=remount-ro`, and can panic for `errors=panic`. Ordinary messages go through `__nilfs_msg()`.

Superblock commit code alternates/falls back between primary and secondary NILFS superblocks. `nilfs_prepare_super()` repairs one in-memory superblock copy from the other if needed and optionally flips active copies. `nilfs_commit_super()` updates write time, CRC, dirty state, flushed-device state, and calls `nilfs_sync_super()`, which uses barriers/FUA when enabled and updates GC protection sequence.

Resize updates sufile segment count, constructs a segment, moves the secondary superblock to its new end-of-device-derived location, commits both superblocks, and only then widens the allocatable segment range so log writes do not overwrite the migrating secondary superblock.

Mount setup uses the fs_context API. Supported options include `errors=`, `barrier`/`nobarrier`, read-only snapshot checkpoint `cp=`, `order=relaxed|strict`, `norecovery`, and `discard`/`nodiscard`. Snapshot mounts require read-only mode and verify the checkpoint is marked as a snapshot.

`nilfs_fill_super()` allocates and initializes `the_nilfs`, loads on-disk metadata, attaches the latest checkpoint, starts the log writer for read-write mounts, obtains the root dentry, and marks the filesystem not-clean on writable mount. Failure paths detach the writer, drop metadata inodes, delete sysfs groups, and destroy NILFS state.

The file also defines VFS `super_operations`, `file_system_type nilfs_fs_type`, cache constructors for NILFS inodes and segment buffers, module init/exit, sysfs init/exit, and registration under filesystem name `nilfs2`.
<!-- END FILE RESEARCH: sources/os/linux/linux/fs/nilfs2/super.c -->