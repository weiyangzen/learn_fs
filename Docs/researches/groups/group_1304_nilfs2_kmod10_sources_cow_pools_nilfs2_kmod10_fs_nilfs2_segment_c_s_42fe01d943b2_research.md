# Group Research: group_1304_nilfs2_kmod10_sources_cow_pools_nilfs2_kmod10_fs_nilfs2_segment_c_s_42fe01d943b2

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.c

## Summary
Implements the NILFS2 segment constructor and log writer. It coordinates filesystem transactions, dirty buffer collection, logical segment construction, super-root creation, data-sync segment writes, cleaner-driven segment migration, writeback completion, and segctord lifecycle.

## Main Responsibilities
- Provides transaction begin/commit/abort locking around NILFS metadata updates.
- Runs the `segctord` kernel thread and request/timer machinery.
- Collects dirty file, metadata, DAT, checkpoint, sufile, and GC inode blocks into segment buffers.
- Builds segment summaries, finfo/binfo records, super-root blocks, and segment usage updates.
- Allocates, extends, truncates, cancels, or frees segment buffers through sufile state.
- Assigns final block numbers through bmap/DAT machinery before writeout.
- Handles fsync-style data-only logical segments and full checkpoint-forming logical segments.
- Implements cleaner entry point `nilfs_clean_segments()`.

## Key APIs
- `nilfs_transaction_begin()`, `nilfs_transaction_commit()`, `nilfs_transaction_abort()`.
- `nilfs_relax_pressure_in_lock()`.
- `nilfs_construct_segment()`.
- `nilfs_construct_dsync_segment()`.
- `nilfs_flush_segment()`.
- `nilfs_clean_segments()`.
- `nilfs_attach_log_writer()`, `nilfs_detach_log_writer()`.

## Important Behavior
The segment constructor is staged through `NILFS_ST_INIT`, GC, file, ifile, cpfile, sufile, DAT, super-root, dsync, and done stages. Stage changes go through wrapper helpers so tracepoints are emitted.

Normal checkpoint construction uses `SC_LSEG_SR`; data-only operations use `SC_LSEG_DSYNC`, `SC_FLUSH_FILE`, or `SC_FLUSH_DAT`. Full checkpoint construction creates a checkpoint, writes metadata files, optionally frees cleaned segments, writes DAT, appends a super root, updates sufile usage, and advances `ns_cno`.

If the current set of segment buffers fills after checkpoint metadata collection begins, collection can retry after extending the segment chain. If segment construction fails, it redirties affected inodes, cancels pending sufile frees, frees incomplete logs, and marks failed segments or discontinuity as needed.

`nilfs_segctor_update_payload_blocknr()` assigns physical block numbers after collection and writes the proper binfo format for normal files, DAT, or dsync mode. The write path marks folios/buffers for writeback, adds checksums, submits logs, then completes or aborts folio/buffer state.

The background thread waits on commit, explicit sync, flush, and timer conditions. It can choose between full checkpoint construction and lightweight file/DAT flush depending on unclosed logical segment state and pending flush bits.

## State and Synchronization
Uses `ns_segctor_sem` as the primary exclusion boundary between transactions and the writer. Normal file operations take it read-side; segment construction takes it write-side. Per-task transaction context lives in `current->journal_info`.

`sc_state_lock` protects segctord request state, timer state, flush bits, and request sequence counters. `ns_inode_lock` protects dirty inode queues. Completion to synchronous callers is handled by sequence-numbered wait requests on `sc_wait_request`.

## Risks
This file is one of the most concurrency-sensitive parts of NILFS2. Correctness depends on pairing transaction begin/commit/abort, not calling synchronous construction from inside a transaction, preserving collection stage state across retries, and canceling sufile changes on every failure path.

Segment allocation and write failure handling are delicate: partial writes can discontinue the log chain, mark segments erroneous, or require fallback superblock behavior. Folio writeback handling has special cases for split b-tree node buffers and blocksize smaller than page size.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.h

## Summary
Defines segment-constructor state, recovery cursor state, collection stage state, segment summary pointer helpers, constants, and public segment/recovery interfaces.

## Main Contents
- `struct nilfs_recovery_info` for mount-time super-root search and roll-forward state.
- `struct nilfs_cstage` for dirty block collection stage tracking.
- `struct nilfs_segsum_pointer` for current segment-summary buffer/offset.
- `struct nilfs_sc_info` for segctord and active segment construction state.
- Segment-constructor flags and defaults.
- Prototypes for construction, dsync, cleaner, writer attach/detach, and recovery helpers.

## Important Details
`nilfs_sc_info` ties together dirty file lists, GC inode lists, pending iput work, sufile free vectors, dsync target range, current segment buffers, write logs, stage cursors, summary pointers, checkpoint/time counters, request queues, sequence counters, timer, and segctord task pointer.

`NILFS_SC_DIRTY`, `NILFS_SC_UNCLOSED`, `NILFS_SC_SUPER_ROOT`, `NILFS_SC_PRIOR_FLUSH`, and `NILFS_SC_HAVE_DELTA` describe segment-constructor state across checkpoint and lightweight flush operations.

Default behavior is set by `NILFS_SC_DEFAULT_TIMEOUT`, `NILFS_SC_DEFAULT_SR_FREQ`, and `NILFS_SC_DEFAULT_WATERMARK`.

## Risks
Consumers must respect the locking comments: `nilfs_segctor_destroy()` expects the segment semaphore to be held, and `sc_stage.scnt` should be accessed through the wrappers in `segment.c` so tracing remains consistent.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/segment.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.c

## Summary
Implements the NILFS segment usage metadata file. It tracks clean, dirty, active, and erroneous segment state, allocates clean segments, frees or cancels freed segments, reports segment statistics, resizes the segment array, supports user-driven suinfo updates, and implements discard/trim over clean segments.

## Main Responsibilities
- Maintains in-memory sufile private state: clean segment count and allocation range.
- Converts segment numbers to sufile metadata block offsets and entry offsets.
- Updates sufile entries singly or in vectors under `mi_sem`.
- Allocates clean segments using last-allocation and allocation-range scanning.
- Marks segments dirty, clean/free, garbage/scrap, or erroneous.
- Reports `nilfs_sustat` and per-segment `nilfs_suinfo`.
- Applies ioctl-provided `nilfs_suinfo_update` arrays.
- Resizes the segment usage array during filesystem resize.
- Issues discard for clean segment extents for fstrim.
- Reads and initializes the sufile inode from the super-root raw inode.

## Key APIs
- `nilfs_sufile_get_ncleansegs()`.
- `nilfs_sufile_updatev()`, `nilfs_sufile_update()`.
- `nilfs_sufile_set_alloc_range()`.
- `nilfs_sufile_alloc()`.
- `nilfs_sufile_mark_dirty()`.
- `nilfs_sufile_set_segment_usage()`.
- `nilfs_sufile_get_stat()`.
- `nilfs_sufile_get_suinfo()`, `nilfs_sufile_set_suinfo()`.
- `nilfs_sufile_resize()`.
- `nilfs_sufile_trim_fs()`.
- `nilfs_sufile_read()`.

## Important Behavior
`nilfs_sufile_alloc()` scans from the last allocated segment, first inside the configured allocation range and then outside it as needed. It only chooses entries whose segment usage is clean, marks them dirty, updates header clean/dirty counters, updates `sui->ncleansegs`, marks metadata dirty, and emits allocation tracepoints.

`nilfs_sufile_freev()` and cancel-free wrappers are built on `nilfs_sufile_updatev()`, which groups operations by metadata block and returns the number of completed entries for rollback.

`nilfs_sufile_mark_dirty()` rejects unreadable hole blocks and active segments marked erroneous. `nilfs_sufile_set_segment_usage()` updates live block count and optionally last-modified time; timestamped updates warn if the entry is in error.

Resize shrinking verifies the truncated range has no dirty or active segments, converts error-only entries back to clean, deletes whole sufile blocks when possible, updates clean counters, and narrows the allocation range before returning.

`nilfs_sufile_set_suinfo()` validates segment numbers, update field masks, and block counts, masks out the virtual active flag before writing, and adjusts header clean/dirty counts according to flag transitions.

## State and Synchronization
All sufile metadata changes are serialized with `NILFS_MDT(sufile)->mi_sem`. Header counters on disk and the cached `ncleansegs` counter must move together. The file uses local folio mappings for entry access and marks both sufile blocks and metadata dirty after changes.

## Risks
Counter consistency is critical: clean and dirty counters are updated in several primitive operations and must match flag transitions. Hole blocks are tolerated in read paths but treated as corruption in some update paths. The active flag is virtual, derived from `the_nilfs`, and must not be persisted by suinfo updates.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.h

## Summary
Declares the segment usage file interface and provides small wrappers around generic sufile update primitives.

## Main Contents
- Inline `nilfs_sufile_get_nsegments()`.
- Declarations for allocation, dirty marking, usage updates, stats, suinfo get/set, resize, read, and trim.
- Primitive update callbacks for scrap, free, cancel-free, and set-error.
- Inline wrappers: `nilfs_sufile_scrap()`, `nilfs_sufile_free()`, `nilfs_sufile_freev()`, `nilfs_sufile_cancel_freev()`, `nilfs_sufile_set_error()`.

## Important Details
The inline wrappers centralize sufile state transitions on `nilfs_sufile_update()` and `nilfs_sufile_updatev()`, passing the appropriate callback. This keeps segment constructor code from manipulating sufile entry buffers directly.

## Risks
Callers must choose the correct `create` mode indirectly through the wrapper. Free and cancel-free operate on existing entries, while scrap allows creating the containing metadata block.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sufile.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/super.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/super.c

## Summary
Implements NILFS2 module registration, superblock operations, mount/remount logic, checkpoint/snapshot attachment, filesystem resize, superblock commit/cleanup, error handling, statfs, and slab cache lifecycle.

## Main Responsibilities
- Registers the `nilfs2` filesystem type and module init/exit hooks.
- Owns slab caches for NILFS inodes, transaction contexts, segment buffers, and btree paths.
- Provides VFS `super_operations`.
- Parses fs_context mount parameters.
- Loads the current checkpoint or a read-only snapshot checkpoint.
- Attaches/detaches the log writer for read-write mounts.
- Commits primary and secondary superblocks with CRCs and barrier-aware sync.
- Handles remount read-only/read-write transitions.
- Resizes the filesystem and relocates the secondary superblock.
- Reports filesystem stats and mount options.

## Key APIs
- `__nilfs_msg()`, `__nilfs_error()`.
- `nilfs_alloc_inode()`.
- `nilfs_set_log_cursor()`.
- `nilfs_prepare_super()`, `nilfs_commit_super()`, `nilfs_cleanup_super()`.
- `nilfs_resize_fs()`.
- `nilfs_attach_checkpoint()`.
- `nilfs_checkpoint_is_mounted()`.
- `nilfs_read_super_block()`.
- `nilfs_store_magic()`.
- `nilfs_check_feature_compatibility()`.

## Important Behavior
Superblock writes calculate CRC over the valid superblock byte range after clearing `s_sum`. `nilfs_sync_super()` writes the active superblock with optional preflush/FUA and can fall back to the spare superblock on primary `-EIO`.

`nilfs_prepare_super()` repairs an invalid copy from the valid one when possible and optionally swaps the active superblock. `nilfs_sb_will_flip()` in `the_nilfs.h` controls periodic flipping to spread superblock writes.

Mount parsing supports `errors=`, `barrier`/`nobarrier`, `cp=`, `order=relaxed|strict`, `norecovery`, and `discard`/`nodiscard`. Snapshot mounts require `cp=` plus read-only mode.

`nilfs_fill_super()` allocates and initializes `the_nilfs`, loads metadata and recovery state, creates the sysfs device group, attaches the current checkpoint, starts the log writer for writable mounts, builds the root dentry, and marks the filesystem mounted/dirty on disk.

`nilfs_get_tree()` supports shared superblocks for the current tree and additional snapshot roots. It rejects incompatible read/write reuse and attaches checkpoint roots under `mounted_snapshots`.

Resize first adjusts sufile segment count under segment-constructor exclusion, constructs a checkpoint, moves the secondary superblock, updates on-disk size and segment count, commits both superblocks, then widens the allocatable segment range.

## State and Synchronization
`ns_sem` protects shared superblock fields and on-disk superblock preparation/commit. `ns_segctor_sem` excludes resize, checkpoint attachment metadata reads, and writer operations. Snapshot mounting is serialized by `ns_snapshot_mount_mutex`.

## Risks
Mount/remount behavior depends on preserving `SB_RDONLY` and recovery state carefully. Superblock fallback and dual-copy synchronization are subtle, especially during resize. Snapshot mounts share the block superblock but attach different checkpoint roots, so dentry/root lifetime checks are important.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/super.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.c

## Summary
Implements NILFS2 sysfs exposure under `/sys/fs/nilfs2`. It creates global feature attributes, per-device groups, mounted snapshot groups, and read/write controls for selected runtime tunables.

## Main Responsibilities
- Creates the top-level NILFS kset and `features` group.
- Creates per-device kobjects named by `sb->s_id`.
- Creates per-device subgroups: `mounted_snapshots`, `checkpoints`, `segments`, `superblock`, and `segctor`.
- Creates snapshot kobjects for current checkpoint and mounted read-only snapshots.
- Exposes checkpoint, segment, segctor, superblock, and device statistics.
- Provides a writable `superblock/sb_update_frequency` attribute.
- Performs kobject cleanup on group creation failure and device teardown.

## Exposed Data
Snapshot attributes:
- `inodes_count`, `blocks_count`, `README`.

Checkpoint attributes:
- `checkpoints_number`, `snapshots_number`, `last_seg_checkpoint`, `next_checkpoint`, `README`.

Segment attributes:
- `segments_number`, `blocks_per_segment`, `clean_segments`, `dirty_segments`, `README`.

Segctor attributes:
- Last/current segment block, sequence, checkpoint, next segment, partial segment offset, write times, non-GC write times, dirty data block count, and `README`.

Superblock attributes:
- `sb_write_time`, `sb_write_time_secs`, `sb_write_count`, `sb_update_frequency`, `README`.

Device attributes:
- `revision`, `blocksize`, `device_size`, `free_blocks`, `uuid`, `volume_name`, `README`.

Feature attributes:
- Driver revision and `README`.

## Important Behavior
Most attributes are read-only and use `sysfs_emit()`. `sb_update_frequency` parses an unsigned integer, clamps values below `NILFS_SB_FREQ` to the minimum, and updates `ns_sb_update_freq` under `ns_sem`.

The helper macros generate sysfs ops, kobj types, create functions, and delete functions for internal per-device subgroups. Snapshot kobjects are parented either directly under the device as `current_checkpoint` or under `mounted_snapshots/<checkpoint>`.

## State and Synchronization
Reads use the relevant NILFS locks: `ns_sem` for superblock fields, `ns_segctor_sem` for segment-constructor state, `ns_last_segment_lock` for latest segment cursor fields, and metadata semaphores where sufile/cpfile stats are queried.

## Risks
Kobject lifetime must be paired correctly with group creation failure paths and device deletion. Some sysfs reads call into metadata stat functions and can return kernel errors directly. `volume_name` formatting uses the raw fixed-size superblock field and truncation semantics should be treated carefully.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.h

## Summary
Defines NILFS2 sysfs constants, subgroup kobject storage, and macro helpers for typed sysfs attributes.

## Main Contents
- `NILFS_ROOT_GROUP_NAME` set to `nilfs2`.
- `struct nilfs_sysfs_dev_subgroups` containing kobjects and unregister completions for per-device subgroups.
- Attribute wrapper struct macros for global feature attrs, device attrs, internal subgroup attrs, and checkpoint/snapshot attrs.
- Attribute construction macros for info, read-only, and read-write sysfs files.
- Attribute-list helper macros for group arrays.

## Important Details
The macros encode the expected callback signatures:
- Feature attrs receive `struct kobject *`.
- Device/subgroup attrs receive `struct the_nilfs *`.
- Snapshot attrs receive `struct nilfs_root *`.

This keeps `sysfs.c` concise while still allowing type-specific show/store functions.

## Risks
The macro layer hides callback type differences. New attributes must use the matching macro family or callbacks will have incompatible signatures.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/sysfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.c -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.c

## Summary
Implements lifecycle, loading, recovery orchestration, disk layout validation, superblock selection, segment geometry, discard, free-space accounting, and checkpoint-root management for the shared `struct the_nilfs`.

## Main Responsibilities
- Allocates and initializes `struct the_nilfs`.
- Releases superblock buffers and NILFS state.
- Loads DAT, cpfile, and sufile from the latest super root.
- Searches for the latest valid super root and runs roll-forward recovery when required.
- Selects between primary and secondary superblocks using CRC validity and checkpoint recency.
- Validates on-disk layout fields from the superblock.
- Tracks latest segment cursor and superblock dirty state.
- Provides segment count, reserved segment, block range, free-space, and near-full helpers.
- Maintains the rb-tree of mounted checkpoint roots.

## Key APIs
- `nilfs_set_last_segment()`.
- `alloc_nilfs()`, `destroy_nilfs()`.
- `load_nilfs()`.
- `nilfs_nrsvsegs()`, `nilfs_set_nsegments()`.
- `init_nilfs()`.
- `nilfs_discard_segments()`.
- `nilfs_count_free_blocks()`, `nilfs_near_disk_full()`.
- `nilfs_lookup_root()`, `nilfs_find_or_create_root()`, `nilfs_put_root()`.
- `nilfs_fall_back_super_block()`, `nilfs_swap_super_block()`.

## Important Behavior
`init_nilfs()` reads superblocks at the primary and computed secondary locations, chooses the valid/newest copy, checks feature compatibility, possibly changes VFS blocksize, validates disk layout, stores mount state, and initializes the log cursor.

`load_nilfs()` searches for the latest super root from the stored cursor. If the search fails with `-EINVAL`, it can fall back to the spare superblock, reinitialize cursor state, drop the clean flag, and retry. When the filesystem is not clean, it either skips recovery for read-only `norecovery`, temporarily enables writes for recovery, or rejects recovery if the device is physically read-only or unsupported read-only-compatible features are present.

Recovery loads the super-root metadata files, creates sysfs device state, salvages orphan logs, marks the filesystem clean, and commits the superblock. On failure it unwinds sysfs and metadata inodes.

Superblock validation checks magic, byte size, and CRC while treating the checksum field as zero. Secondary superblock validation rejects positions that would lie inside the segment area.

Checkpoint roots are cached in `ns_cptree` by checkpoint number. Creation initializes refcounts and counters, links the rb-tree node, and creates a sysfs snapshot group.

## State and Synchronization
`ns_last_segment_lock` protects latest super-root cursor fields. `ns_sem` protects mount-state checks and superblock fields. `ns_cptree_lock` protects checkpoint-root lookup, insertion, erasure, and refcount final decrement.

## Risks
Superblock selection and recovery fallback are correctness-critical. The code must keep VFS `sb->s_flags` restored after temporary recovery writes. Checkpoint-root creation has a subtle ordering issue: after rb-tree insertion, sysfs creation failure frees the new root without erasing it from the tree in this file’s current flow.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.h

## Summary
Defines the central NILFS shared state object, checkpoint-root object, NILFS state flags, mount-option helpers, segment geometry helpers, and public `the_nilfs` interfaces.

## Main Contents
- `enum` flags for initialization, discontinued log chain, GC running, dirty superblock, and purging.
- `struct the_nilfs`, the per-device shared NILFS supervisor object.
- Generated inline flag helpers such as `set_nilfs_init()` and `nilfs_sb_dirty()`.
- Mount option bit helpers.
- `struct nilfs_root` for mounted checkpoint/snapshot roots.
- Superblock update constants and helpers.
- Segment geometry helpers and flush helper.

## Important Details
`struct the_nilfs` contains:
- VFS and block-device references.
- Primary and secondary superblock buffers/pointers.
- Superblock write time/count/state/update frequency.
- Current segment constructor cursor: segment sequence, current/next full segment, partial segment offset, next checkpoint, last write times, dirty block count.
- Latest super-root cursor and GC protection sequence.
- Log writer pointer and segment-constructor semaphore.
- Metadata inode pointers for DAT, cpfile, and sufile.
- Checkpoint root rb-tree and dirty inode/GC lists.
- Mount options, reserved uid/gid, checkpoint interval, watermark, disk geometry, inode size, CRC seed, and sysfs kobjects.

`nilfs_flush_device()` issues a block-device flush only when barriers are enabled and volatile data is not already marked flushed. It uses a write memory barrier around `ns_flushed_device`.

## Risks
Several fields have different locking rules: some are immutable after initialization, some are under `ns_sem`, some under `ns_segctor_sem`, and latest segment fields under `ns_last_segment_lock`. Callers need to follow those ownership boundaries to avoid stale sysfs output, incorrect segment allocation, or superblock cursor corruption.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/the_nilfs.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/include/trace/events/nilfs2.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/include/trace/events/nilfs2.h

## Summary
Defines NILFS2 tracepoints for segment construction stages, transaction transitions, segment usage allocation/free checks, and metadata block operations.

## Trace Events
- `nilfs2_collection_stage_transition`: logs `nilfs_sc_info` pointer and collection stage symbol.
- `nilfs2_transaction_transition`: logs superblock pointer, transaction info pointer, nesting count, flags, and transition state.
- `nilfs2_segment_usage_check`: logs sufile pointer, segment number, and allocation scan count.
- `nilfs2_segment_usage_allocated`: logs allocated segment number.
- `nilfs2_segment_usage_freed`: logs freed segment number.
- `nilfs2_mdt_insert_new_block`: logs metadata inode, inode number, and block.
- `nilfs2_mdt_submit_block`: logs metadata inode, inode number, block offset, and request op mode.

## Important Details
The collection stage symbolic names mirror the stage enum in `segment.c`, so enum changes there must stay aligned with this header. Transaction transition states are defined only outside `TRACE_HEADER_MULTI_READ`.

`nilfs2_mdt_submit_block` uses `__field_struct(enum req_op, mode)` to avoid signedness handling problems with the bitwise request-op enum.

## Risks
Tracepoint fields dereference `struct nilfs_sc_info` members, so this header depends on the concrete segment-constructor layout being visible at tracepoint instantiation. Stage enum drift between `segment.c` and this file would produce misleading traces.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/include/trace/events/nilfs2.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/include/uapi/linux/nilfs2_api.h -->
# File Research: sources/cow-pools/nilfs2-kmod10/include/uapi/linux/nilfs2_api.h

## Summary
Defines the NILFS2 user-space ABI: checkpoint, segment usage, cleaner, virtual block, disk block descriptor structures, flag helpers, and ioctl numbers.

## Main ABI Structures
- `struct nilfs_cpinfo`: checkpoint metadata returned to userspace.
- `struct nilfs_suinfo`: segment usage metadata.
- `struct nilfs_suinfo_update`: selective segment usage update descriptor.
- `struct nilfs_cpmode`: checkpoint/snapshot mode changes.
- `struct nilfs_argv`: generic pointer/count/size/index argument vector.
- `struct nilfs_period`: checkpoint-number interval.
- `struct nilfs_cpstat`: checkpoint totals.
- `struct nilfs_sustat`: segment usage totals and protection sequence.
- `struct nilfs_vinfo`: virtual block lookup result.
- `struct nilfs_vdesc`: virtual block descriptor for cleaner queries.
- `struct nilfs_bdesc`: disk block descriptor for cleaner block moves.

## Flags and Helpers
Checkpoint flags include snapshot, invalid, sketch, and minor. Segment usage flags include active, dirty, and error. Update flags select last modification time, block count, and flags fields inside `nilfs_suinfo_update`.

The header provides inline helper predicates and set/clear functions for these flag fields.

## Ioctls
Defines ioctl identity `'n'` and commands for:
- Changing checkpoint mode.
- deleting checkpoints.
- Getting checkpoint info/statistics.
- Getting and setting segment usage info/statistics.
- Looking up virtual block info.
- Getting block descriptors.
- Cleaning segments.
- Syncing.
- Resizing.
- Setting segment allocation range.

## Important Details
`NILFS_IOCTL_CLEAN_SEGMENTS` takes an array of five `nilfs_argv` structures, matching the cleaner path that passes multiple vectors into kernel segment cleaning. `nilfs_argv.v_base` is a 64-bit userspace pointer value to keep the ABI fixed across architectures.

The active segment usage flag is exposed through `nilfs_suinfo` but is virtual in kernel state; sufile update code clears it before writing flags to disk.

## Risks
This is a stable UAPI header. Field sizes, alignment padding, ioctl numbers, and struct layouts must not be changed casually. Kernel internals must continue to validate sizes/counts from `nilfs_argv` before trusting userspace buffers.
<!-- END FILE RESEARCH: sources/cow-pools/nilfs2-kmod10/include/uapi/linux/nilfs2_api.h -->