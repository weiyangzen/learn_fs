# subset-b-005706 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/mdt.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/mdt.h

## Purpose

`mdt.h` defines the common in-memory contract for NILFS2 metadata files. These files are ordinary-looking inodes from the VFS perspective, but their private state is specialized around metadata block access, persistent allocation entries, per-blockgroup locking, and the segment constructor's shadow-copy mechanism. The header is shared by concrete metadata files such as the DAT, checkpoint file, segment usage file, and ifile.

## Important APIs, Types, and Functions

`struct nilfs_mdt_info` is the private `inode->i_private` payload for metadata inodes. It contains `mi_sem` for read/write metadata operations, `mi_bgl` for blockgroup-scoped locking, entry layout fields (`mi_entry_size`, `mi_first_entry_offset`, `mi_entries_per_block`), a persistent allocator cache, optional `mi_shadow`, and grouping geometry.

`struct nilfs_shadow_map` carries the shadow bmap state, a shadow inode whose page cache holds copied metadata pages, and a list of frozen buffers. This is central to garbage collection and rollback-style DAT handling.

The main exported helpers are `nilfs_mdt_get_block()`, `nilfs_mdt_find_block()`, `nilfs_mdt_delete_block()`, `nilfs_mdt_forget_block()`, `nilfs_mdt_fetch_dirty()`, initialization/destruction helpers, entry sizing, and the shadow-map operations. Inline helpers identify metadata inodes, mark or clear `NILFS_I_DIRTY`, retrieve the current checkpoint number with `nilfs_mdt_cno()`, and get a per-blockgroup spinlock with `nilfs_mdt_bgl_lock()`.

## Control Flow

Callers initialize a metadata inode with `nilfs_mdt_init()`, set its entry format with `nilfs_mdt_set_entry_size()`, then access metadata blocks through `nilfs_mdt_get_block()` or lookup-only variants. Concrete metadata files layer their own entry indexing on top of these calls. Segment construction and metadata mutation mark dirty state through `nilfs_mdt_mark_dirty()`, and later the log writer detects metadata work with `nilfs_mdt_fetch_dirty()`.

Shadow-map flow is explicit: setup, save original metadata pages/bmap into the shadow state, use frozen buffers while the operation proceeds, then either restore, clear, or destroy the shadow map. This lets GC prepare complex changes without permanently committing partial DAT state.

## State and Persistence Behavior

The header models volatile metadata-file state. Persistence occurs indirectly when dirty metadata blocks are collected into NILFS logs and checkpoint/super-root records. `mi_sem` protects logical metadata updates, while `mi_bgl` narrows allocator-style contention. Dirty state is stored in `NILFS_I(inode)->i_state`, not the VFS inode's generic dirtiness alone.

The shadow map deliberately separates tentative metadata state from the original mapping. `nilfs_mdt_restore_from_shadow_map()` can roll back in-memory metadata after failed GC preparation, while later log construction persists only the selected dirty buffers.

## Dependencies and Integration Points

`mdt.h` depends on `nilfs.h`, `page.h`, buffer heads, and blockgroup locks. It is consumed by allocator-like metadata modules (`sufile.c`, `cpfile.c`, `dat.c`, `ifile.c`, palloc helpers) and by the segment constructor in `segment.c`, which queries metadata dirtiness and clears metadata dirty flags after super-root completion.

## Risks and Edge Cases

Metadata-file identity is inferred from non-NULL `inode->i_private`; code that sets private data incorrectly can make normal inodes look like metadata files. Entry layout must match on-disk metadata sizes, or block/offset calculations in concrete metadata files will corrupt entries. Shadow-map handling is a rollback-sensitive path: leaked frozen buffers or forgotten restore/clear calls can leave stale pages or incorrect bmap state.

## Test Signals

Useful coverage includes metadata inode initialization/destruction, missing metadata blocks, dirty flag propagation into segment construction, shadow-map save/restore after injected allocation failures, and blockgroup lock use under concurrent metadata updates. GC tests should exercise DAT shadow-map rollback and successful commit paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/mdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/namei.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/namei.c

## Purpose

`namei.c` implements NILFS2 pathname and directory inode operations plus NFS export file-handle support. It adapts conventional ext2-style directory manipulation to NILFS2's transactional, log-structured update model: every mutating namespace operation begins a NILFS transaction, updates directory entries and inode link counts, marks affected inodes dirty, then commits or aborts the transaction.

## Important APIs, Types, and Functions

The directory operation implementations are `nilfs_lookup()`, `nilfs_create()`, `nilfs_mknod()`, `nilfs_symlink()`, `nilfs_link()`, `nilfs_mkdir()`, `nilfs_unlink()`, `nilfs_rmdir()`, and `nilfs_rename()`. `nilfs_add_nondir()` is a helper for new non-directory objects that either instantiates the dentry or unwinds link count and new-inode state.

Export helpers are `nilfs_get_parent()`, `nilfs_get_dentry()`, `nilfs_fh_to_dentry()`, `nilfs_fh_to_parent()`, and `nilfs_encode_fh()`. They preserve both inode number and NILFS checkpoint number (`root->cno`) in `struct nilfs_fid`, which matters because snapshots expose historical trees.

The file exports `nilfs_dir_inode_operations`, `nilfs_special_inode_operations`, `nilfs_symlink_inode_operations`, and `nilfs_export_ops`.

## Control Flow

Lookup rejects names longer than `NILFS_NAME_LEN`, asks `nilfs_inode_by_name()` for an inode number, and loads that inode from the directory's root object via `nilfs_iget()`. A stale deleted inode reference is promoted to a filesystem error signal and returns `-EIO`.

Creation, mknod, symlink, link, mkdir, unlink, rmdir, and rename all wrap their changes in `nilfs_transaction_begin()` and `nilfs_transaction_commit()` or `nilfs_transaction_abort()`. New files set inode operation/file operation/address-space operation tables before insertion. Directory creation increments the parent link count, initializes `.` and `..`, links the child, then commits. Failure paths carefully drop link counts, dirty inodes that had link changes, unlock new inodes, and `iput()` abandoned objects.

Unlink looks up the directory entry, verifies that it points to the expected inode number, deletes the entry, drops the target link count, and marks both directory and target dirty. Rmdir adds an empty-directory check and drops both child and parent directory links. Rename supports only `RENAME_NOREPLACE`; it handles overwrite, cross-directory directory moves by rewriting `..`, ctime changes, and all relevant link-count transitions.

NFS export decoding looks up the checkpoint root with `nilfs_lookup_root()`, loads the inode, checks generation when provided, and returns aliases through the VFS dentry helpers.

## State and Persistence Behavior

Namespace persistence is checkpointed by NILFS log construction after transactions mark directories and inodes dirty. Link counts, ctime, directory entries, symlink page contents, and root/checkpoint file handles are all represented in normal inode and directory metadata and become durable through later segment construction.

`nilfs_encode_fh()` includes `root->cno`, so file handles can refer to snapshot roots rather than only the mutable current tree. This is a NILFS-specific persistence detail for exportability across checkpoints.

## Dependencies and Integration Points

The file depends on directory helpers from `dir.c`, inode allocation/loading from `inode.c`, transaction APIs from `segment.c`, file/address-space operation tables, file attribute and fiemap handlers, and `export.h`'s NILFS file-handle layout. It integrates directly with the VFS inode operation and export operation tables.

## Risks and Edge Cases

Rename is the highest-risk path because it combines old-entry deletion, optional new-entry replacement, directory `..` updates, and link-count corrections. Any missed dirty mark can defer or lose metadata updates in the log. `nilfs_do_unlink()` repairs a zero-link target by resetting it to one before dropping the link, but that also signals prior metadata inconsistency. Snapshot file-handle decoding must reject invalid system inode numbers and stale generations to avoid exposing wrong historical objects.

## Test Signals

Test signals include create/link/unlink/mkdir/rmdir/symlink/mknod under crash-recovery workloads, cross-directory rename of directories, rename over files and empty directories, unsupported rename flags, long names, stale directory entries, and NFS export encode/decode for current and snapshot checkpoints. Transaction abort fault injection should verify link counts and dentries are unwound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/namei.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/nilfs.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/nilfs.h

## Purpose

`nilfs.h` is the local umbrella header for the NILFS2 filesystem implementation. It defines the in-memory NILFS inode wrapper, dynamic inode state bits, transaction context layout, inode-number classification macros, mount/error message helpers, and prototypes for major internal subsystems.

## Important APIs, Types, and Functions

`struct nilfs_inode_info` embeds `struct inode` and stores NILFS-specific state: file flags and type bits, dynamic state bits, bmap storage, xattr block pointer, directory lookup cursor, GC checkpoint number, associated cache inode, dirty-list linkage, optional xattr semaphore, raw inode buffer, root pointer, and VFS inode.

`NILFS_I()` and `NILFS_BMAP_I()` convert from generic VFS/bmap objects to NILFS-private structures. `NILFS_I_*` state bits describe new, dirty, queued, busy, collected, updated, inode-sync, and bmap-cache state. `NILFS_I_TYPE_*` distinguishes normal, GC, btree-node-cache, and shadow-cache inodes.

`struct nilfs_transaction_info` tracks nested NILFS transactions in `current->journal_info`, with flags for dynamic allocation, synchronous construction, GC context, commit occurrence, and writer context. Prototypes expose `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, and `nilfs_transaction_abort()`.

The header also declares internal operations from directory, file, ioctl, inode, superblock, GC inode, sysfs, address-space, and filesystem registration modules. Message macros wrap `__nilfs_msg()` and `__nilfs_error()`.

## Control Flow

Most mutating filesystem code includes this header and follows the transaction pattern defined here: begin a transaction, mutate inode/directory/metadata state, mark inodes dirty, then commit or abort. Segment construction tests transaction flags such as `NILFS_TI_GC` and `NILFS_TI_WRITER` to decide whether writes are normal, GC, or constructor-owned.

Inode code uses `NILFS_VALID_INODE()`, `NILFS_MDT_INODE()`, and `NILFS_PRIVATE_INODE()` to distinguish user-visible files, root/system files, metadata files, and private inodes. Superblock and mount code use the declared `nilfs_read_super_block()`, feature checks, log cursor, commit, cleanup, resize, checkpoint attach, and checkpoint mount-test helpers.

## State and Persistence Behavior

The header separates volatile inode state (`i_state`, dirty lists, associated cache inodes) from persistent inode fields stored in `struct nilfs_inode` on disk. `i_bh` pins the buffer containing a dirty on-disk inode while the segment constructor collects and writes it.

Transaction state is per-task and not persistent; its role is to serialize modifications against segment construction and to trigger eventual log writing. Persistent effects are committed through the segment constructor and superblock routines declared here.

## Dependencies and Integration Points

`nilfs.h` pulls in Linux kernel, buffer-head, block-device, filesystem, NILFS on-disk API, `the_nilfs.h`, and bmap definitions. It is included by almost every NILFS2 implementation file and ties VFS operations, metadata files, block mapping, checkpoint/root management, sysfs, ioctl, and log writing together.

## Risks and Edge Cases

Because this is a central header, type or flag changes have wide blast radius. `current->journal_info` reuse must preserve any foreign filesystem pointer via `ti_save`; errors there can corrupt unrelated filesystem state in stacked paths. The inode-number macros rely on constants fitting in bit operations for low system inode numbers. The disabled POSIX ACL block explicitly errors if enabled, so configuration drift can break builds.

## Test Signals

Build coverage across NILFS2 configs is essential. Runtime tests should watch dirty/busy/queued inode state transitions, nested transaction begin/commit/abort, GC transaction flags, system inode validation, mount option error handling, and message/error behavior that sets `NILFS_ERROR_FS` through `nilfs_error()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/nilfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/page.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/page.c

## Purpose

`page.c` contains NILFS2-specific folio and buffer-head management. It supports metadata shadow copies, buffer state copying, dirty-page cleanup, delayed/uncommitted extent discovery, and debugging of inconsistent folio state. These helpers are used by metadata files, btree/node caches, DAT shadow maps, and segment construction.

## Important APIs, Types, and Functions

`nilfs_grab_buffer()` obtains and locks/grabs a folio-backed buffer for a logical block offset. `nilfs_forget_buffer()` clears mapping, dirty, async, volatile, checked, redirected, and delay state from a buffer. `nilfs_copy_buffer()` copies one buffer's data and inherent state.

`nilfs_copy_dirty_pages()` copies dirty folios from one mapping to a shadow mapping, preserving dirty buffer state. `nilfs_copy_back_pages()` copies or moves pages back from shadow mapping to the original mapping. `nilfs_clear_folio_dirty()`, `nilfs_clear_dirty_pages()`, and `__nilfs_clear_folio_dirty()` clear dirty state while coordinating xarray dirty tags and buffer states.

`nilfs_page_count_clean_buffers()` counts clean buffers in a byte range. `nilfs_find_uncommitted_extent()` scans for contiguous `BH_Delay` buffers. Debug support is provided by `nilfs_folio_bug()`.

## Control Flow

`nilfs_grab_buffer()` calculates the folio index from a block offset, grabs a folio from the given mapping, creates empty buffers if needed, waits on the target buffer, and assigns the superblock device.

Shadow copy flow starts with dirty folio iteration on the source mapping. For each dirty source folio, `nilfs_copy_dirty_pages()` locks the source, grabs the destination folio, copies data and buffer states with `nilfs_copy_folio()`, marks the destination dirty, and releases both folios. Copy-back either overwrites an existing destination folio or moves the folio's xarray entry between mappings, preserving dirty tags.

Dirty cleanup first invalidates buffer LRU references if buffers are busy, then clears buffer state and folio uptodate/mapped/checked/dirty state. `__nilfs_clear_folio_dirty()` clears the mapping's dirty xarray mark under lock before calling `folio_clear_dirty_for_io()`.

Uncommitted extent discovery scans contiguous folios and their buffers from a starting block, begins an extent at the first delayed buffer, and stops when a non-delayed buffer or bufferless folio follows an active extent.

## State and Persistence Behavior

The file operates entirely on in-memory page-cache and buffer-head state. It controls which dirty or delayed buffers are later collected into NILFS logs. Clearing or copying these flags affects persistence indirectly by changing what the segment constructor sees as pending work.

The inherent buffer bit mask intentionally copies only stable state such as uptodate, mapped, NILFS node, volatile, and checked; redirected/dirty/delay state is selectively copied depending on the call path.

## Dependencies and Integration Points

Dependencies include Linux folio, page cache, buffer-head, writeback, highmem mapping, xarray, and swap/LRU helpers. Integration points include `mdt.c` shadow maps, btree node cache handling, DAT copy-back during GC, and `segment.c` writeback cleanup through `nilfs_folio_buffers_clean()` and `__nilfs_clear_folio_dirty()`.

## Risks and Edge Cases

This code manipulates low-level xarray entries in `nilfs_copy_back_pages()`, so mapping/nrpages/tag accounting must remain exact. Busy buffer cleanup can leave state intact after one invalidation pass, which callers must tolerate. `nilfs_copy_buffer()` and `nilfs_copy_folio()` assume buffer sizes/layouts are compatible. Debug paths call `BUG()` through `NILFS_FOLIO_BUG`, so inconsistent dirty state can become a hard failure.

## Test Signals

Good tests include metadata shadow save/restore, copy-back with existing and absent destination folios, dirty xarray tag preservation, busy buffer invalidation, delayed extent discovery across folio boundaries, block sizes smaller than page size, and injected allocation failures in destination folio creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/page.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/page.h

## Purpose

`page.h` declares NILFS2's page-cache and buffer-head helpers and defines NILFS-specific buffer state bits. It is the interface between low-level folio/buffer manipulation in `page.c`, metadata file code, btree/node caches, and the segment constructor.

## Important APIs, Types, and Functions

The extended buffer states begin at `BH_PrivateStart`: `BH_NILFS_Allocated`, `BH_NILFS_Node`, `BH_NILFS_Volatile`, `BH_NILFS_Checked`, and `BH_NILFS_Redirected`. `BUFFER_FNS()` generates accessors for node, volatile, checked, and redirected states. These bits distinguish btree node buffers, temporary or volatile buffers, verified buffers, and buffers redirected to copies during construction.

The declared helpers cover buffer acquisition (`nilfs_grab_buffer()`), forgetting/copying buffers, folio cleanliness and bug diagnostics, copying dirty pages to shadow mappings, copying pages back, clearing folio/page dirty state, counting clean buffers, and finding uncommitted delayed extents.

## Control Flow

Callers include the header when they need to tag buffers for NILFS-specific writeback or manipulate metadata shadows. Segment construction sets and clears async/volatile/redirected states through helpers declared here. Metadata code uses the dirty copy/restore helpers while GC or DAT operations need rollback-capable state.

## State and Persistence Behavior

The buffer bits are volatile state, but they control persistence decisions. `BH_NILFS_Node` changes how folio writeback completion handles split btree node pages. `BH_NILFS_Volatile` and `BH_NILFS_Redirected` are cleared after successful log write. `BH_Delay` discovery identifies data not yet committed to a segment.

## Dependencies and Integration Points

The header depends on Linux buffer heads and `nilfs.h`. It is included by `mdt.h`, `segment.c`, `segbuf.c`, recovery code, and likely bmap/btree modules that need NILFS buffer annotations.

## Risks and Edge Cases

Adding or reordering private buffer bits can collide with other buffer-head users if `BH_PrivateStart` assumptions change. Callers must not treat NILFS-specific flags as durable metadata. Correct handling of node buffers is important because btree node folios can be split and completed more than once during a log write.

## Test Signals

Test signals include state-bit transitions during btree updates, redirected-buffer cleanup after successful and failed construction, uncommitted delayed-buffer search, and dirty-page clearing in both data and metadata mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/page.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/recovery.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/recovery.c

## Purpose

`recovery.c` implements NILFS2 mount-time log recovery. It validates segment summaries and super-root checksums, searches for the latest valid super root starting from superblock cursors, records newer orphan logs, and optionally rolls forward data-sync partial segments written after the latest checkpoint.

## Important APIs, Types, and Functions

Public functions are `nilfs_read_super_root_block()`, `nilfs_search_super_root()`, `nilfs_salvage_orphan_logs()`, and `nilfs_dispose_segment_list()`.

Internal helpers include `nilfs_compute_checksum()`, `nilfs_validate_log()`, summary-entry readers/skippers, `nilfs_scan_dsync_log()`, `nilfs_prepare_segment_for_recovery()`, `nilfs_recover_dsync_blocks()`, `nilfs_do_roll_forward()`, `nilfs_finish_roll_forward()`, and `nilfs_abort_roll_forward()`.

`struct nilfs_recovery_block` records a data block from a data-sync log: owning inode, physical block, virtual block number, file block offset, and list link. `struct nilfs_segment_entry` tracks full segments that should be marked active or disposed.

## Control Flow

`nilfs_search_super_root()` starts at `nilfs->ns_last_pseg` and `ns_last_seq`, reads segment summaries, validates magic, sequence, block count, and full-log CRC, then follows partial segments within a full segment and `ss_next` into subsequent segments. When it sees a valid super-root partial segment, it updates recovery info and the in-memory log cursor. If the filesystem was not clean, it scans newer logs to determine whether the super root was updated or whether roll-forward regions exist.

`nilfs_salvage_orphan_logs()` attaches the latest checkpoint root, calls `nilfs_do_roll_forward()`, and if data blocks were salvaged, prepares fresh recovery segments, attaches the log writer, constructs a new segment, then post-cleans the old recovery start block.

Roll-forward accepts only synchronous data logs (`NILFS_SS_SYNDT`) without super roots. It scans finfo/binfo records into recovery-block entries, then at log-end loads target inodes, performs `block_write_begin()`, copies saved block data from disk into the folio, marks the file dirty, and completes the write through normal block write paths. On failure, dirty recovery inodes are abandoned.

## State and Persistence Behavior

Recovery updates `struct the_nilfs` cursors: current segment number, next segment, segment sequence, checkpoint number, last super-root position, creation times, and pseg offset. It also manipulates the sufile to free invalidated next segments, scrap segments written after the latest super root, and allocate fresh segments for recovery output.

Roll-forward turns orphan data-sync log contents back into normal dirty file pages and persists them by constructing a new segment. `nilfs_finish_roll_forward()` zeros the old roll-forward start block when it shares the super-root segment, reducing the chance that stale orphan logs are replayed again.

## Dependencies and Integration Points

The file depends on buffer-head IO, block write helpers, CRC32, `segment.h`, `sufile.h`, `page.h`, `segbuf.h`, checkpoint/root attach, inode lookup, bmap write paths through `nilfs_get_block()`, and the log writer. It is part of mount/load flow invoked before the filesystem is fully available.

## Risks and Edge Cases

CRC and range checks bound reads, but summary parsing assumes valid `sumbytes`, finfo counts, and block counts once the log is accepted. Roll-forward only recovers data-sync logs; other orphan logs are ignored or treated as confusing. `nilfs_prepare_segment_for_recovery()` changes sufile state before constructing the recovery segment; later failure relies on destruction/abort cleanup rather than restoring the old sufile. Sequence/next-segment corruption can cause early termination or `-EINVAL` mount failure.

## Test Signals

Tests should include clean and unclean mounts, corrupted summary magic, sequence mismatch, bad full CRC, bad super-root CRC, truncated summary blocks, orphan data-sync logs with multiple files, roll-forward allocation failure, I/O failure while copying recovered blocks, and recovery after the next segment or active segment has an inconsistent sufile entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/recovery.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.c

## Purpose

`segbuf.c` implements the physical segment-buffer abstraction used by the NILFS2 segment constructor. A segment buffer represents one partial segment: its summary blocks, payload blocks, optional super-root block, disk mapping, CRCs, and asynchronous BIO write state.

## Important APIs, Types, and Functions

`nilfs_segbuf_new()` and `nilfs_segbuf_free()` allocate from `nilfs_segbuf_cachep`. Mapping helpers are `nilfs_segbuf_map()`, `nilfs_segbuf_map_cont()`, and `nilfs_segbuf_set_next_segnum()`. Capacity helpers extend summary or payload storage with `nilfs_segbuf_extend_segsum()` and `nilfs_segbuf_extend_payload()`.

`nilfs_segbuf_reset()` initializes a partial segment summary, while `nilfs_segbuf_fill_in_segsum()` writes the on-disk segment summary header. CRC helpers fill summary, data, and super-root checksums. Log-list helpers are `nilfs_clear_logs()`, `nilfs_truncate_logs()`, `nilfs_write_logs()`, `nilfs_wait_on_logs()`, and `nilfs_add_checksums_on_logs()`.

BIO submission is handled by `nilfs_segbuf_write()`, `nilfs_segbuf_submit_bh()`, `nilfs_segbuf_submit_bio()`, `nilfs_end_bio_write()`, and `nilfs_segbuf_wait()`.

## Control Flow

The constructor maps a new segment buffer to a full segment and offset, extends at least one summary block, appends summary and payload buffers as dirty blocks are collected, then fills summary fields and checksums. `nilfs_write_logs()` iterates segment buffers and submits writes.

BIO submission walks summary buffers first, then payload buffers. Buffers are coalesced into bios up to `BIO_MAX_VECS` or until `bio_add_folio()` fails, at which point the current bio is submitted and a new one is allocated. The last bio is tagged `REQ_SYNC`. Completion increments `sb_err` on bio failure and signals `sb_bio_event`; `nilfs_segbuf_wait()` waits for all outstanding bios and reports `-EIO` with the segment range if any failed.

CRC order matters: super-root CRC is embedded first if present, then segment-summary CRC, then full data CRC across summaries and payload buffers. Payload CRC maps folios with `kmap_local_folio()` and assumes block size is not larger than page size.

## State and Persistence Behavior

Segment buffers are volatile staging objects, but their contents are the exact bytes written to the log. `sb_sum` mirrors on-disk segment summary state; `sb_segnum`, `sb_nextnum`, `sb_pseg_start`, and `sb_rest_blocks` define disk placement. `sb_nbio`, `sb_err`, and `sb_bio_event` track asynchronous persistence completion.

After writes complete, `segment.c` finalizes buffer and folio state and advances filesystem cursors. On abort, log buffers are cleared or marked failed by the segment constructor, not by `segbuf.c` itself.

## Dependencies and Integration Points

The file depends on buffer-heads, writeback, CRC32, BIO APIs, block devices, and `page.h`/`segbuf.h`. It is driven almost entirely by `segment.c`; recovery reads the on-disk format that this file writes.

## Risks and Edge Cases

`bio_alloc()` return is not explicitly NULL-checked in `nilfs_segbuf_submit_bh()`, so allocation failure behavior depends on the kernel API contract. CRC calculations assume summary size and block list consistency already enforced by the constructor. `nilfs_segbuf_wait()` uses a single completion repeatedly; completions must match `sb_nbio` exactly. Block sizes larger than page size are explicitly unsupported for payload CRC mapping.

## Test Signals

Test coverage should include multi-bio partial segments, summary-block extension, super-root CRC validation by recovery, injected BIO errors, bio vector boundary behavior, blocksize less than page size, continued partial segments, and abort paths after partial submission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.h

## Purpose

`segbuf.h` declares NILFS2 segment-buffer structures and helpers. It is the public interface between the segment constructor and the lower-level log buffer/BIO writer implemented in `segbuf.c`.

## Important APIs, Types, and Functions

`struct nilfs_segsum_info` is the in-memory summary for a partial segment: flags, finfo count, total block count, summary block count, summary byte count, file block count, segment sequence, checkpoint number, creation time, and next-segment block.

`struct nilfs_segment_buffer` stores list linkage, summary info, segment mapping (`sb_segnum`, `sb_nextnum`, full segment start/end, partial segment start, remaining blocks), summary and payload buffer lists, optional super-root buffer, and async IO state (`sb_nbio`, `sb_err`, completion).

List and iterator macros walk segment buffers and buffers inside segment-buffer lists. Inline helpers classify a simplex log, detect empty logs, and add summary, payload, or file buffers while updating block counters. File-buffer insertion takes a reference and increments `nfileblk`.

Exports cover allocation/freeing, mapping, reset, summary/payload extension, summary filling, log clearing/truncation/destruction, writing, waiting, and checksum insertion.

## Control Flow

`segment.c` allocates and maps segment buffers, appends dirty buffers through the inline add helpers, fills summary entries, sets next segment numbers, and finally calls `nilfs_add_checksums_on_logs()`, `nilfs_write_logs()`, and `nilfs_wait_on_logs()`.

The header's macros encode assumptions used throughout the constructor: segment buffers are list-linked by `sb_list`, buffer heads are list-linked by `b_assoc_buffers`, and the last segment buffer may carry the super-root block.

## State and Persistence Behavior

The structures are in-memory staging state for persistent NILFS logs. Fields in `sb_sum` are copied to on-disk `struct nilfs_segment_summary`. Payload and summary buffer lists are the ordered write set for a partial segment. IO state records whether persistence succeeded, but the constructor is responsible for updating global filesystem cursors and sufile accounting after success.

## Dependencies and Integration Points

The header depends on filesystem, buffer-head, BIO, and completion APIs. It declares `nilfs_segbuf_cachep`, which is created in `super.c`. It integrates tightly with `segment.c` and with recovery's expectations for segment-summary layout and checksums.

## Risks and Edge Cases

The iterator macros assume non-empty lists when used; misuse on empty logs can dereference list heads as objects. `nilfs_segbuf_simplex()` depends on correct `NILFS_SS_LOGBGN` and `NILFS_SS_LOGEND` flag management. Counters must remain synchronized with list contents or CRC and write lengths will mismatch recovery validation.

## Test Signals

Tests should validate empty/simplex/multi-partial logs, list truncation after failed construction, file buffer reference accounting, summary and payload block counts, and super-root placement in the last segment buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segbuf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segment.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/segment.c

## Purpose

`segment.c` is NILFS2's segment constructor and log-writer implementation. It serializes filesystem transactions, collects dirty file and metadata buffers, creates segment-summary records, assigns physical log block numbers through bmaps, writes partial segments, finalizes checkpoints and super roots, manages background segctord wakeups, and provides the GC segment-cleaning write path.

## Important APIs, Types, and Functions

Public entry points are `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, `nilfs_transaction_abort()`, `nilfs_relax_pressure_in_lock()`, `nilfs_construct_segment()`, `nilfs_construct_dsync_segment()`, `nilfs_clean_segments()`, `nilfs_attach_log_writer()`, and `nilfs_detach_log_writer()`.

The key state object is `struct nilfs_sc_info` from `segment.h`, holding dirty-file lists, GC inodes, segment buffers, write logs, freed segment arrays, collection stage, summary pointers, counters, checkpoint number, flags, request queues, timer, and segctord task.

Internal flow is split across dirty-buffer discovery (`nilfs_lookup_dirty_data_buffers()`, `nilfs_lookup_dirty_node_buffers()`), collection (`nilfs_segctor_collect_blocks()`), segment allocation/extension (`nilfs_segctor_begin_construction()`, `nilfs_segctor_extend_segments()`), bmap assignment (`nilfs_segctor_update_payload_blocknr()`), write preparation and completion (`nilfs_prepare_write_logs()`, `nilfs_segctor_write()`, `nilfs_segctor_wait()`, `nilfs_segctor_complete_write()`), and abort cleanup.

## Control Flow

Ordinary filesystem updates call `nilfs_transaction_begin()` to enter a read side of `ns_segctor_sem`, then commit marks the transaction committed, starts the background timer, and may request immediate flush when dirty blocks exceed a watermark. A synchronous transaction flag calls `nilfs_construct_segment()` after leaving the transaction.

Segctord or a direct caller obtains the writer transaction lock, accepts pending requests, determines a mode (`SC_LSEG_SR`, `SC_LSEG_DSYNC`, `SC_FLUSH_FILE`, or `SC_FLUSH_DAT`), and calls `nilfs_segctor_do_construct()`. Construction first moves globally queued dirty inodes into `sc_dirty_files`, pins their ifile buffers, marks metadata dirty if needed, and exits early if there is no work.

Collection progresses through explicit stages: GC inodes, normal files, ifile, checkpoint file, sufile/free-segment updates, DAT, and optional super root. Each scanned file collects dirty data buffers, node buffers, and bmap buffers using operation tables that differ for normal files, DAT, and dsync logs. If a segment buffer fills, construction may extend with more full segments, cancel provisional sufile frees, reset stage state, and retry.

After collection, payload buffers are assigned physical log block numbers through `nilfs_bmap_assign()`, binfo records are written into the segment summaries, segment summaries and optional super root are filled, sufile usage is updated, folios are put into writeback state, CRCs are calculated, and logs are submitted. Completion clears dirty/async/delay/volatile/redirected bits, ends folio writeback, drops collected inode state, advances `ns_segnum`, `ns_nextnum`, `ns_pseg_offset`, `ns_seg_seq`, timestamps, and if a super root was written, advances the last checkpoint and clears metadata dirty flags.

Abort waits for submitted logs, redirties collected inodes when needed, cancels provisional segment usage and free-segment changes, marks failed segments discontinued or erroneous, and destroys logs.

## State and Persistence Behavior

This file is the main persistence engine for NILFS2. Persistent state affected includes file data, btree nodes, ifile entries, cpfile checkpoints, sufile segment states, DAT translations, super roots, superblock log cursors, and checkpoint numbers. It also maintains volatile coordination state: dirty inode lists, `NILFS_I_BUSY/COLLECTED/UPDATED`, `NILFS_SC_UNCLOSED`, request sequence counters, flush bitmaps, and construction stage cursors.

Data-sync construction can write data-only logical segments without a super root unless strict ordering, an unclosed segment, or discontinued state forces a full checkpoint-style construction. GC construction uses shadow DAT state and freed segment arrays, and discards segments after successful cleaning if the mount option is enabled.

## Dependencies and Integration Points

`segment.c` integrates with nearly every NILFS2 subsystem: bmaps, btree node caches, metadata file dirty tracking, ifile/cpfile/sufile/DAT, GC ioctls, superblock commit logic, page/buffer helpers, segment buffers, kernel threads, timers, wait queues, freezer support, block device discard, and tracepoints.

## Risks and Edge Cases

This is a high-risk concurrency and crash-consistency file. Correctness depends on stage retry logic, sufile cancellation on failures, exact folio writeback begin/end pairing, dirty inode list state, and checkpoint finalization ordering. The code has special handling for block sizes smaller than page size because folios spanning segments can otherwise be double-buffered incorrectly. `nilfs_construct_segment()` deliberately BUGs if called inside a NILFS transaction to avoid deadlock. Segment allocation failures, BIO failures, bmap assignment replacements, and GC shadow-map failures all need exact cleanup.

## Test Signals

Core tests should cover ordinary buffered writes, fsync/data-sync ranges, strict-order mounts, background timer checkpointing, dirty-block watermark flushes, blocksize smaller than page size, super-root checkpoint creation, metadata-only updates, interrupted sync waits, writer teardown with pending work, ENOSPC, injected bmap assignment errors, injected BIO errors, and GC cleaning with DAT shadow rollback and discard failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segment.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segment.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/segment.h

## Purpose

`segment.h` declares NILFS2's log-writer, recovery, and segment-construction state interfaces. It is the shared contract between transaction users, the segment constructor implementation, recovery, superblock management, and garbage collection.

## Important APIs, Types, and Functions

`struct nilfs_recovery_info` records recovery results: whether recovery is needed, last super-root block/checkpoint, roll-forward scan range and starting sequence, used segments, last partial segment position, sequence, segment number, and next segment. Flags distinguish super-root update from completed roll-forward.

`struct nilfs_cstage` stores collection stage count, stage flags, and cursors into dirty-file and GC-inode lists. `struct nilfs_segsum_pointer` points into a segment summary buffer while finfo/binfo entries are written.

`struct nilfs_sc_info` is the complete log-writer object: superblock/root, block counters, dirty/GC/iput lists, segments to free, dsync range, active segment buffers, write-log buffers, current segment, stage, summary pointers and counters, checkpoint/timestamp/flag state, request queues and sequence counters, flush request bitmap, timing parameters, timer, and segctord task.

Public prototypes expose transaction construction, dsync construction, GC cleaning, log writer attach/detach, recovery scanning, super-root reading, orphan-log salvage, and segment-list disposal.

## Control Flow

The header describes the state consumed by `segment.c`: file operations enter transactions; segctord tracks requests and stages in `nilfs_sc_info`; recovery fills `nilfs_recovery_info`; superblock mount code attaches or detaches the log writer. Stages progress from init through GC, files, metadata files, DAT, super root, dsync, and done.

## State and Persistence Behavior

`nilfs_sc_info` is volatile, but it stages persistent changes to checkpoints, segment usage, DAT, and super roots. `sc_freesegs` and `sc_nfreesegs` represent segments that will become free only after a super-root log containing sufile changes is successfully written. `sc_cno`, `sc_seg_ctime`, and `sc_flags` connect in-memory construction to durable checkpoint identity.

`nilfs_recovery_info` bridges persistent on-disk log scanning and in-memory repair. It determines which segments must be scrapped or reallocated and whether a recovery segment must be constructed.

## Dependencies and Integration Points

The header depends on Linux fs, buffer heads, workqueues, and `nilfs.h`. It is included by `segment.c`, `super.c`, `recovery.c`, and callers that request log construction or cleaning.

## Risks and Edge Cases

Request sequence counters are 32-bit and use wrap-aware comparison in the implementation; changing their type or semantics can break waiters. `sc_stage` cursors must only be manipulated through wrappers in `segment.c` so tracepoints stay accurate. Public construction functions are not safe inside active transactions unless explicitly designed for that mode.

## Test Signals

Tests should verify recovery info population on clean/dirty mounts, wait-request wakeups under sequence wrap-like conditions, dsync range state, GC freed segment arrays, log-writer attach/detach lifecycle, and stage transitions observed through tracepoints.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/segment.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sufile.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/sufile.c

## Purpose

`sufile.c` implements the NILFS2 segment usage metadata file. The sufile records whether each segment is clean, dirty, active, or erroneous, how many live blocks it contains, and its last modification time. It provides segment allocation/freeing, accounting, resizing, suinfo ioctl access, and fstrim discard of clean segments.

## Important APIs, Types, and Functions

`struct nilfs_sufile_info` extends `struct nilfs_mdt_info` with cached `ncleansegs` and allocation range limits `allocmin`/`allocmax`.

Core mutation APIs are `nilfs_sufile_alloc()`, `nilfs_sufile_free()`/`freev()`, `nilfs_sufile_scrap()`, `nilfs_sufile_cancel_freev()`, `nilfs_sufile_mark_dirty()`, `nilfs_sufile_set_segment_usage()`, and `nilfs_sufile_set_error()`. Generic update wrappers `nilfs_sufile_update()` and `nilfs_sufile_updatev()` obtain header and entry blocks under `mi_sem` and call primitive update functions.

Management APIs include `nilfs_sufile_set_alloc_range()`, `nilfs_sufile_resize()`, `nilfs_sufile_get_stat()`, `nilfs_sufile_get_suinfo()`, `nilfs_sufile_set_suinfo()`, `nilfs_sufile_trim_fs()`, and `nilfs_sufile_read()`.

## Control Flow

Allocation reads the header's last allocation, chooses a start segment within the configured allocation range, wraps through the range and then outside it if needed, scans segment usage entries block by block, and marks the first clean entry dirty. It updates header clean/dirty counters, cached clean count, last allocation, buffer dirty state, and metadata dirty state.

Free/scrap/cancel/error operations are small primitives invoked under the generic update wrappers. Free makes an allocated segment clean and adjusts counters. Scrap makes a segment dirty garbage with zero blocks, used for recovery and GC protection. Cancel-free re-dirties a segment after provisional freeing. Set-error marks a segment erroneous and removes it from clean counts if needed.

Resize takes the metadata semaphore, checks reserved-space constraints, truncates trailing segments only if they are clean or error-only and inactive, converts full usage blocks to holes, updates counters and the global segment count, and clamps allocation range after shrink.

Suinfo get/set iterates segment usage entries for ioctl users. Get synthesizes the active flag from `nilfs_segment_is_active()` rather than reading it from disk. Set validates segment numbers, update flags, and block counts, updates selected fields, drops virtual active flags, and adjusts header counters.

Trim computes block/segment ranges from byte input, groups contiguous clean segments into discard extents, issues `blkdev_issue_discard()`, and reports discarded bytes through `range->len`.

## State and Persistence Behavior

Sufile entries and header counters are persistent metadata and are written through normal NILFS segment construction. The cached `ncleansegs` and allocation limits are volatile accelerators and policy state. Active segment status is not stored in entries; it is derived from current `the_nilfs` segment cursors.

Segment frees are often provisional until a log with a super root commits the sufile update. `segment.c` cancels frees if construction fails. Erroneous segments are intended to be permanently avoided by allocation.

## Dependencies and Integration Points

The file depends on `mdt.h`, segment usage on-disk helpers from NILFS headers, tracepoints, block discard APIs, and `the_nilfs` geometry helpers. It is used by segment construction, recovery, GC, statfs/free-block counting, resize, ioctl, and trim paths.

## Risks and Edge Cases

Counter correctness is critical: header clean/dirty counters and cached `ncleansegs` must stay synchronized across allocate/free/scrap/error/resize/set_suinfo. Hole blocks in the sufile are valid in some ranges but can indicate corruption for required entries. Resize must reject dirty or active segments in the truncated range. Trim holds a read lock while issuing discards, which can be slow. User-driven suinfo updates can create dangerous states if validation misses flag combinations.

## Test Signals

Tests should cover allocation wraparound with restricted ranges, ENOSPC, free/cancel-free failure rollback, recovery scrap, active erroneous segment detection, resize expansion/shrink with dirty/active/error segments, suinfo ioctl counter changes, holes in usage blocks, fstrim minlen/range clipping, discard failure handling, and crash recovery after provisional frees.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sufile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sufile.h -->
# sources/distributed-fs/ceph-client/fs/nilfs2/sufile.h

## Purpose

`sufile.h` declares the segment usage file interface for NILFS2. It exposes allocation, freeing, error marking, statistics, suinfo ioctl access, resizing, trim, and read initialization helpers used by the segment constructor, recovery, GC, ioctl, and mount code.

## Important APIs, Types, and Functions

`nilfs_sufile_get_nsegments()` derives the segment count from `the_nilfs`. `nilfs_sufile_get_ncleansegs()` returns the cached clean count.

Allocation and state APIs include `nilfs_sufile_set_alloc_range()`, `nilfs_sufile_alloc()`, `nilfs_sufile_mark_dirty()`, `nilfs_sufile_set_segment_usage()`, `nilfs_sufile_updatev()`, `nilfs_sufile_update()`, and primitive callbacks `nilfs_sufile_do_scrap()`, `do_free()`, `do_cancel_free()`, and `do_set_error()`.

Inline wrappers provide semantic operations: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, and `nilfs_sufile_set_error()`. Other exports provide resize, read, stat, suinfo get/set, and trim.

## Control Flow

Callers generally use the semantic inline wrappers rather than calling update primitives directly. Segment construction allocates and marks active segments dirty, updates live block counts, and frees old segments through `freev()`. Recovery scraps or frees invalidated segments and allocates replacement segments. IOCTL paths call suinfo get/set and trim.

## State and Persistence Behavior

The header exposes persistent segment usage changes without embedding policy. The implementation writes changes to the sufile metadata blocks and marks the metadata inode dirty; those changes become durable with log construction. Active status remains a runtime projection.

## Dependencies and Integration Points

`sufile.h` depends on VFS, buffer heads, and `mdt.h`. It is included by `segment.c`, `recovery.c`, `super.c`, and likely ioctl/statfs helpers that inspect segment state.

## Risks and Edge Cases

The update primitives assume the caller supplied valid header and entry buffers under the sufile semaphore. External callers should prefer wrappers to avoid bypassing locking and counter updates. `nilfs_sufile_set_error()` permanently removes a segment from normal allocation, so accidental calls are persistent and high impact.

## Test Signals

Test signals include wrapper behavior for single and vector frees, cancel-free counts, error marking, invalid segment numbers, resize and trim public calls, and read initialization with malformed segment usage entry sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/sufile.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/super.c -->
# sources/distributed-fs/ceph-client/fs/nilfs2/super.c

## Purpose

`super.c` implements NILFS2 module initialization, superblock lifecycle, mount/remount parsing, checkpoint and snapshot attachment, superblock commit/cleanup, resize, statfs, freeze/unfreeze, inode slab allocation, and filesystem type registration. It is the top-level integration layer between NILFS2 internals and the VFS mount API.

## Important APIs, Types, and Functions

Global caches are `nilfs_inode_cachep`, `nilfs_transaction_cachep`, `nilfs_segbuf_cachep`, and `nilfs_btree_path_cache`. Exported functions include `__nilfs_msg()`, `__nilfs_error()`, `nilfs_alloc_inode()`, `nilfs_set_log_cursor()`, `nilfs_prepare_super()`, `nilfs_commit_super()`, `nilfs_cleanup_super()`, `nilfs_resize_fs()`, `nilfs_attach_checkpoint()`, `nilfs_checkpoint_is_mounted()`, `nilfs_read_super_block()`, `nilfs_store_magic()`, and `nilfs_check_feature_compatibility()`.

VFS operations are collected in `nilfs_sops`; filesystem context parsing uses `nilfs_parse_param()`, `nilfs_get_tree()`, `nilfs_reconfigure()`, `nilfs_free_fc()`, and `nilfs_init_fs_context()`. Mount options include barrier/nobarrier, checkpoint snapshot `cp=`, error mode, order mode, norecovery, and discard/nodiscard.

## Control Flow

Module init creates slabs, initializes sysfs support, and registers `nilfs_fs_type`. Mount setup allocates a `the_nilfs`, initializes it, copies parsed options, sets super operations/export operations, loads on-disk NILFS state, attaches the latest checkpoint root, attaches the log writer for read-write mounts, creates the root dentry, and marks the superblock dirty/unclean for read-write operation.

`nilfs_get_tree()` supports shared superblocks and snapshot mounts. A `cp=` mount must be read-only and attaches a snapshot root after verifying the checkpoint is a snapshot. Existing device mounts can be reused or reconfigured when the current tree is not busy.

Superblock commit flow prepares a valid primary/secondary superblock pair, optionally flips the active copy, sets log cursor fields, recalculates CRC, writes with optional barrier/FUA, falls back to the secondary on primary write failure, and updates protected sequence state. Cleanup marks the filesystem valid/clean again when unmounting or remounting read-only.

Resize locks segment construction, resizes the sufile segment array, constructs a segment to persist metadata changes, moves the secondary superblock, updates device size and segment count in both superblocks, commits both, and only then expands the allocation range to include newly available segments.

## State and Persistence Behavior

Persistent state includes superblock clean/error flags, mount counts/times, write times, free block count, last segment sequence, last partial segment, last checkpoint, device size, segment count, and checksum. The file also manages volatile mount options, roots, sysfs groups, slab caches, and `sb->s_fs_info`.

`__nilfs_error()` marks `NILFS_ERROR_FS` on disk for metadata incoherence, optionally remounts read-only or panics depending on mount options. Freeze writes a clean superblock; unfreeze marks it unclean again for writable operation.

## Dependencies and Integration Points

`super.c` integrates Linux module, fs_context, block device, VFS super operations, seq_file option display, sysfs, NILFS metadata files (`cpfile`, `sufile`, `ifile`, `dat`), segment writer, recovery/load code through `load_nilfs()`, snapshot roots, btree/path caches, and export operations.

## Risks and Edge Cases

Superblock dual-copy handling is delicate: fallback, flipping, CRC calculation, and secondary relocation must maintain at least one valid copy. Resize ordering protects the secondary superblock from allocation until migration completes. Remount from read-only to read-write must reject unsupported read-only-compatible features. Snapshot mounts must avoid writable access. Error handling paths in `nilfs_fill_super()` and module cache creation must release partially initialized metadata inodes, sysfs groups, and caches.

## Test Signals

Tests should cover clean and unclean read-write mounts, read-only snapshot mounts, invalid `cp=` combinations, remount RO/RW, unsupported feature bits, superblock CRC failures and fallback, error modes (`continue`, `remount-ro`, `panic` where feasible), freeze/unfreeze, statfs counts, resize shrink/expand including secondary superblock movement, module init/exit, and fault injection through mount failure stages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/nilfs2/super.c -->
