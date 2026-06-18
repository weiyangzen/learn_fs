# Group Research: group_1873_xfsprogs_sources_local_fs_xfsprogs_libxfs_rdwr_c_sources_local_fs_x_3d4d0546de7f

Scope: `Docs/research_subset_a.md`, specifically the `sources/local-fs/xfsprogs` source tree. All listed source files were read completely.

This grouped report contains 13 exact BEGIN/END file research blocks for the requested sources.

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/rdwr.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/rdwr.c

## Role

`rdwr.c` is the userspace libxfs buffer-cache, block-device I/O, and log-formatting layer. It adapts kernel-style `xfs_buf` usage to xfsprogs, including cache lookup, buffer locking, verifier dispatch, dirty writeback, delayed-write submission, raw device zeroing, and clean-log initialization.

The file explicitly documents that userspace buffer error semantics differ from the kernel: many callers leave `bp->b_error` uncleared, so release and dirty-mark paths clear stale errors to avoid leaking old read/write failures into later cache hits.

## Major Responsibilities

- Zero device ranges with `fallocate(FALLOC_FL_ZERO_RANGE)` when possible, falling back to aligned zero-buffer writes.
- Fetch primary and realtime superblock buffers through `libxfs_getsb` and `libxfs_getrtsb`.
- Implement cache hashing, key comparison, allocation, release, bulk release, flushing, purging, and overflow checks for `xfs_buf`.
- Allocate and initialize cached, mapped, discontiguous, and uncached buffers.
- Provide optional pthread-based buffer locking with recursion detection for userspace repair paths.
- Read and verify buffers via single-map or multi-map I/O, including salvage mode for callers that want corrupt buffers returned.
- Write dirty buffers through verifiers and `pwrite`, including discontiguous-map writes and mem-backed targets.
- Maintain dirty/stale/unchecked/uptodate buffer state and prevent stale buffers from being written.
- Submit or cancel delayed-write buffer lists synchronously.
- Format a clean/unmount log image with `libxfs_log_clear` and `libxfs_log_header`.
- Verify 16-bit and 32-bit metadata magic values against buffer verifier tables.
- Flush device write caches through `platform_flush_device`.
- Mark buffers corrupt for non-verifier relationship corruption with `__xfs_buf_mark_corrupt`.

## Buffer Cache Flow

The cache key is `struct xfs_bufkey`, containing target, start block, length, and optional maps. `libxfs_bhash` hashes by disk block, and `libxfs_bcompare` returns hit only if both block and length match. A same-block length mismatch can purge the old entry, with optional diagnostics under `IO_BCOMPARE_CHECK`.

Allocation reuses buffers from `xfs_buf_freelist` when possible. `__libxfs_getbufr` prefers a freelist buffer of matching byte size; otherwise it reuses another buffer after freeing its data and non-inline map storage, or allocates a new cache object. `__initbuf` resets core fields, allocates aligned memory, zeros contents, initializes lock state, and sets a single default map unless discontiguous maps are supplied.

`__cache_lookup` obtains or allocates a cache node, then optionally locks the buffer. If the caller requests `LIBXFS_GETBUF_TRYLOCK`, lock contention returns `-EAGAIN`; recursive locking by the same thread increments `b_recur` after warning.

## Read And Verify Path

`libxfs_buf_read_map` first finds a cached buffer. If it is already uptodate or dirty and marked `LIBXFS_B_UNCHECKED`, supplied verifier ops are run before returning it. On a cache miss it reads with `libxfs_readbufr` or `libxfs_readbufr_map`, sets `LIBXFS_B_UPTODATE` on successful reads, and calls `libxfs_readbuf_verify`.

The `LIBXFS_READBUF_SALVAGE` flag allows a buffer to be returned even if verification fails. This is important for repair-style callers that need to inspect damaged metadata.

## Writeback Path

`libxfs_bwrite` refuses to write stale buffers, runs an optional mount writeback hook, clears stale preexisting errors, runs write verifiers, and writes either a single contiguous buffer or each discontiguous map. Successful writes mark buffers uptodate and clear dirty/unchecked flags; failed writes print block, length, and verifier-name diagnostics.

`libxfs_buf_mark_dirty` clears stale errors, clears the stale flag, and marks the buffer dirty and uptodate. Dirty cached buffers are written by cache flush or during release of uncached buffers.

## Log Formatting

`libxfs_log_clear` zeroes an on-disk or memory log, writes the initial clean log record, and optionally fills the rest of the log with previous-cycle records so kernel log head/tail discovery sees a clean log. `libxfs_log_header` builds v1/v2 log record headers, extended cycle headers for large v2 records, an unmount transaction record, cycle-data packing, and cycle-stamped padding blocks.

## Notable Assumptions

- Memory buftargs skip physical reads and writes.
- Uncached buffers are recognized by an empty cache-node hash list and a direct refcount.
- Release paths clear `b_error` to compensate for legacy userspace callers.
- Dirty buffers reaching the free list are treated as lost/corrupt write evidence and set buftarg flags.
- Several allocation and I/O failures print diagnostics and `exit(1)`, reflecting xfsprogs utility behavior rather than kernel-style propagation.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/rdwr.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/topology.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/topology.c

## Role

`topology.c` provides mkfs/libxfs device probing and default geometry selection. It calculates default data allocation-group and realtime-group sizes, detects preexisting signatures before overwrite, and gathers logical/physical sector, stripe, and atomic-write topology for data, realtime, and log devices.

## Major Responsibilities

- Calculate default AG size/count with `calc_default_ag_geometry`.
- Calculate default realtime group size/count with `calc_default_rtgroup_geometry`.
- Probe a target path with blkid to detect existing filesystems or partition tables in `check_overwrite`.
- Read blkid topology fields for block devices: logical sector size, physical sector size, minimum I/O size, optimal I/O size, and alignment offset.
- Reject misaligned block devices unless forced.
- Read Linux `statx` atomic write unit bounds when available.
- Handle regular-file targets by deriving direct-I/O sector requirements with `platform_findsizes`.
- Populate `struct fs_topology` for data, realtime, and log subvolumes.

## Geometry Heuristics

`calc_default_ag_geometry` uses size thresholds and storage parallelism to choose a target AG size. Filesystems at or above 32 TiB use the maximum AG size. Single-device filesystems at or above 4 TiB also use the maximum; single-device filesystems from 128 MiB to 4 TiB target four AGs. Multidisk configurations use a higher AG count, reducing the shift for smaller filesystems. The final AG size rounds up if the filesystem size is not evenly divisible.

`calc_default_rtgroup_geometry` mirrors the single-device portion for realtime devices: 4 TiB or larger uses `XFS_MAX_RGBLOCKS`; 128 MiB to 4 TiB targets four realtime groups; smaller devices round similarly.

## Device Probing

`check_overwrite` opens the device, obtains its size, skips zero-length targets, and runs a full blkid probe with partition probing enabled. It reverses blkid's success convention so callers receive `1` for detected content, `0` for nothing, and `-1` for probe/internal failure. Diagnostics distinguish filesystem signatures, partition tables, and unknown blkid detections.

`blkid_get_topology` converts blkid minimum/optimal I/O values from bytes to 512-byte units, suppresses stripe values equal to physical sector size, and handles nonzero alignment offsets. `get_device_topology` chooses between regular-file sizing and block-device blkid/statx probing, then ensures a physical sector size is present.

## Notable Assumptions

- `libxfs_get_topology` silently skips absent optional subvolumes.
- Stripe unit/width are stored in basic-block counts after blkid probing.
- Misalignment can abort the process directly unless the caller requested force overwrite.
- Atomic write unit fields are optional and remain zero when `statx` support or device reporting is absent.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/topology.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/topology.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/topology.h

## Role

`topology.h` declares the userspace topology data structures and helpers used by mkfs/libxfs to derive filesystem geometry and to decide whether a target can be overwritten safely.

## Interface

- `struct device_topology` stores logical sector size, physical sector size, stripe unit, stripe width, and min/max atomic write unit values.
- `struct fs_topology` groups topology for data, realtime, and log devices.
- `libxfs_get_topology` fills an `fs_topology` from a `libxfs_init` device description.
- `calc_default_ag_geometry` computes data AG size/count defaults.
- `calc_default_rtgroup_geometry` computes realtime group size/count defaults.
- `check_overwrite` probes a device for existing signatures or partition tables.

## Notable Assumptions

The header is userspace-facing and does not define policy; all threshold logic, blkid probing, regular-file handling, and force-overwrite behavior live in `topology.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/topology.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/trans.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/trans.c

## Role

`trans.c` implements the userspace libxfs transaction facade. It preserves the kernel transaction/log item model enough for shared metadata code to run in xfsprogs, but commits by applying superblock deltas and writing dirty buffers/inodes directly through libxfs rather than writing an active journal.

## Major Responsibilities

- Initialize transaction reservation tables with `libxfs_trans_init`.
- Allocate, reserve, roll, commit, cancel, and free transactions.
- Attach and detach buffer and inode log items to transactions.
- Implement transaction-aware buffer get/read/superblock lookup paths.
- Track buffer recursion counts and hold flags while buffers are joined to a transaction.
- Mark buffers dirty, log byte ranges, invalidate buffers, and tag inode-allocation buffers.
- Track superblock counter deltas and reservation usage.
- Run item precommit callbacks in a stable sorted order.
- Finish deferred operations on final permanent-transaction commit.
- Flush inode log items through `libxfs_iflush_int` and mark buffer log items dirty.
- Provide convenience transaction allocation for inode and directory updates.
- Allow clean transactions to reserve more blocks after metadata analysis.

## Transaction Lifecycle

`libxfs_trans_alloc` allocates a zeroed transaction, initializes item/defer lists, and reserves blocks, realtime extents, and log reservation metadata. Userspace reservation checks compare requested data blocks against `sb_fdblocks` and realtime extents against `sb_rextents`, but do not perform quota reservations.

`libxfs_trans_roll` duplicates the transaction's permanent reservation state, commits the current transaction with `regrant=true`, and reserves the log space for the next transaction. The duplicate inherits unused block reservation and deferred ops; the original is prevented from allocating further by reducing its block reservation to what it already used.

`libxfs_trans_cancel` aborts if the transaction is dirty, because userspace has no journal recovery path for a dirty cancellation. Deferred ops on cancel are treated as dirty and cancelled only after assertions/diagnostics.

## Buffer Item Handling

`libxfs_trans_get_buf_map` and `libxfs_trans_read_buf_map` first search for a matching buffer already joined to the transaction. A hit increments `bli_recur`; a miss obtains or reads a normal libxfs buffer and joins it with `_libxfs_trans_bjoin`.

`libxfs_trans_brelse` only releases clean, non-stale, non-dirty buffers whose recursion count is zero. Dirty or invalidated buffers stay attached until commit. `libxfs_trans_bdetach` forcibly removes a completely clean, unheld buffer from a transaction while leaving the caller's locked reference intact.

`libxfs_trans_log_buf` marks the transaction and buffer item dirty and records the logged byte range. `libxfs_trans_binval` stales a buffer, cancels delayed write, clears dirty state, marks the log item cancel/stale, and dirties the transaction.

## Commit Path

`__xfs_trans_commit` runs precommit callbacks, finishes deferred ops on the final commit of permanent transactions, reruns precommits for the final deferred-op transaction, applies superblock deltas, calls `xfs_log_sb`, and then completes every log item. Buffer items are marked dirty and released unless held. Inode items flush inode core/fork state through `libxfs_iflush_int`, dirty the backing inode buffer on success, and release it.

On precommit or defer errors, the transaction items are detached/unlocked and the transaction is freed. Dirty commit failures force shutdown via the same shared XFS mechanisms used by kernel-derived code.

## Superblock Accounting

`libxfs_trans_mod_sb` tracks only fields needed in userspace: free data blocks, inode count, free inode count, and free realtime extents. Negative free-block and realtime deltas consume transaction reservations and assert if usage exceeds reservation. `XFS_TRANS_SB_RES_FDBLOCKS` is ignored because it only affects on-disk reservation accounting in this userspace model.

## Notable Assumptions

- Userspace does not need real log space but still maintains permanent-log-reservation flags to satisfy shared-code assertions.
- Dirty transaction cancellation is fatal.
- Ordered buffers are treated like ordinary logged dirty buffers because userspace commits directly.
- Precommit item sorting uses optional `iop_sort` callbacks; unsortable items are moved later.
- `libxfs_trans_alloc_dir` always sets `nospace_error` to zero because userspace does not support kernel reservationless creation fallback.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/trans.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/util.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/util.c

## Role

`util.c` collects userspace libxfs support routines that do not fit neatly into the buffer or transaction layer: log reservation sizing, reproducible timestamps, simple incore superblock modification, file-space allocation, verifier/corruption diagnostics, userspace LSN tracking, health stubs, extent zeroing, and mapped file writes.

## Major Responsibilities

- Calculate worst-case log unit reservations with `xfs_log_calc_unit_res`.
- Provide `current_time`, honoring `SOURCE_DATE_EPOCH` through `current_fixed_time`.
- Modify incore free-block counters with `libxfs_mod_incore_sb`.
- Allocate file space with `libxfs_alloc_file_space`.
- Emit verifier diagnostics for buffers and inodes.
- Track the largest metadata LSN seen by userspace repair in `xfs_log_check_lsn`.
- Initialize generic log items with `xfs_log_item_init`.
- Choose data vs realtime buftarg for inode extents and zero extents via `libxfs_zero_extent`.
- Provide minimal filesystem/group/inode sickness hooks for userspace.
- Write data through mapped filesystem extents with `libxfs_file_write`.

## Allocation Flow

`libxfs_alloc_file_space` validates positive length, converts byte range to filesystem blocks, honors realtime inodes and extent-size hints, and loops until the requested range is allocated. Each iteration computes bounded data/realtime reservations, allocates and joins an inode transaction, extends extent-count capacity, calls `xfs_bmapi_write`, sets the preallocation flag, logs the inode core, commits, and unlocks the inode. If `xfs_bmapi_write` returns no mappings for a delalloc conversion attempt, the loop retries the same offset.

## Diagnostics And LSN Tracking

`xfs_verifier_error`, `xfs_inode_verifier_error`, and `xfs_buf_corruption_error` emit concise metadata corruption/CRC messages without kernel stack dumping. `xfs_log_check_lsn` always returns true because userspace lacks an active log current-LSN source, but it records the largest non-null LSN seen under a pthread mutex for repair validation.

## File Write Helper

`libxfs_file_write` maps file offsets to data-device extents in chunks up to 1 MiB, rejects holes and unwritten extents, gets the underlying data-device buffer, copies caller data into the correct block offset, zero-fills partial leading/trailing regions within the buffer, marks it dirty, and releases it.

## Notable Assumptions

- Only `XFS_TRANS_SB_FDBLOCKS` is supported by `libxfs_mod_incore_sb`.
- Health marking is mostly stubbed in userspace; `xfs_fs_mark_healthy` updates fs-level sick/checked bits, while most mark-sick helpers are empty.
- `xfs_log_check_lsn` validates nothing against an active log and is intentionally permissive.
- `libxfs_file_write` requires fully mapped, written extents and treats holes/unwritten extents as caller errors.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/util.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfblob.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfblob.c

## Role

`xfblob.c` implements append-only blob storage on top of `xfile`. It stores each blob behind a small metadata key and returns the byte offset as an opaque cookie for later load/free operations.

## Major Responsibilities

- Create a blob store backed by an unlimited private `xfile`.
- Store blobs by appending an `xb_key` header followed by payload bytes.
- Return the header offset as `xfblob_cookie`.
- Load blobs by validating the magic value and stored offset, then reading the payload.
- Free individual blobs by punching out their header and payload range.
- Truncate all blobs by discarding from `PAGE_SIZE` to the last appended offset and resetting append position.

## Storage Format

Each blob starts with packed `struct xb_key`: `xb_magic`, `xb_size`, and `xb_offset`. The magic constant is `XB_KEY_MAGIC`. `xfblob_create` initializes `last_offset` to `PAGE_SIZE`, leaving the first page unused; all blob offsets advance monotonically by header size plus payload size.

## Error Handling

`xfblob_load` and `xfblob_free` validate that the header magic matches and that `xb_offset` equals the supplied cookie. Bad cookies assert and return `-ENODATA`; an undersized load buffer asserts and returns `-EFBIG`. If payload store fails after the header write, the header range is discarded before returning the error.

## Notable Assumptions

- Cookies are trusted offsets into the xfile but still checked against the stored header.
- Freed blobs are not reused; only storage backing is discarded.
- `xfblob_truncate` assumes `last_offset` is at or beyond `PAGE_SIZE`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfblob.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfblob.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfblob.h

## Role

`xfblob.h` declares the cookie-addressed blob storage wrapper used by xfsprogs code that needs temporary variable-sized object storage over an `xfile`.

## Interface

- `struct xfblob` contains the backing `struct xfile` and next append offset.
- `xfblob_cookie` is a `loff_t` offset cookie.
- `xfblob_create` and `xfblob_destroy` manage the blob store.
- `xfblob_store` appends a blob and returns its cookie.
- `xfblob_load` retrieves a blob into a caller buffer.
- `xfblob_free` discards one stored blob range.
- `xfblob_truncate` discards all blob ranges and resets append state.

## Notable Assumptions

The header exposes no iterator or reuse mechanism. Allocation, validation, free-space punching, and append offset management are implemented in `xfblob.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfblob.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfile.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfile.c

## Role

`xfile.c` implements swappable temporary memory for offline checking and repair. It backs indexed scratch data with memfd or temporary files so large staging datasets can be paged by the kernel instead of requiring resident heap memory.

## Major Responsibilities

- Create close-on-exec scratch file descriptors, preferring `memfd_create`.
- Fall back from `MFD_NOEXEC_SEAL` to plain memfd, then `O_TMPFILE` in `/dev/shm` or `/tmp`, then `mkostemp`.
- Remove unwanted mode bits with `fchmod(0600)`.
- Manage shared file control blocks (`xfile_fcb`) and reference counts.
- Partition a backing fd into page-aligned ranges when callers provide `maxbytes`.
- Load and store data with `pread` and `pwrite`.
- Report actual allocated bytes for private or partitioned xfiles.
- Punch holes with `fallocate(FALLOC_FL_PUNCH_HOLE | FALLOC_FL_KEEP_SIZE)`.

## File Control Blocks

An `xfile_fcb` owns a file descriptor, refcount, and list linkage. A caller with `maxbytes == 0` receives a private backing file at offset zero. Bounded xfiles are page-rounded and can share a backing fd; `xfile_fcb_find` scans existing fds, extends one if it can append the requested partition, or creates and tracks a new fd.

`xfile_fcb_irele` closes private fcbs without locking. Shared fcbs are refcounted under `fcb_mutex`; the final user removes the fcb and closes the fd. When a non-final user releases the last partition at the end of the file, the backing fd can be truncated down to free address space.

## Load, Store, And Accounting

`xfile_load` treats short reads and out-of-range reads as memory-allocation failures, returning `-ENOMEM`. `xfile_store` treats oversize writes as `-E2BIG`, out-of-partition writes as `-EFBIG`, and short writes as `-ENOMEM`.

`xfile_bytes` returns allocated disk blocks for private xfiles. For partitioned xfiles, `xfile_partition_bytes` walks `SEEK_DATA`/`SEEK_HOLE` within the partition and falls back to `maxbytes` on unexpected seek errors.

## Notable Assumptions

- xfiles are "memory" abstractions, so I/O errors are mapped to memory-style failures where appropriate.
- Callers provide all concurrency control; xfile operations do not lock file ranges.
- Backing files are close-on-exec and intended never to be shared with child processes.
- `xfile_discard` ignores the result of hole punching.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfile.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfile.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfile.h

## Role

`xfile.h` declares the memfd/tmpfile-backed scratch storage abstraction used by offline libxfs code.

## Interface

- `struct xfile_fcb` owns shared backing-file state: list node, fd, and refcount.
- `struct xfile` references an fcb and records its partition start and maximum writable bytes.
- `xfile_create` creates a private xfile when `maxbytes` is zero, or a bounded partition otherwise.
- `xfile_destroy` releases the partition/fcb.
- `xfile_load` and `xfile_store` read/write byte ranges relative to the xfile partition.
- `xfile_bytes` reports allocated backing bytes.
- `xfile_discard` punches out a byte range.

## Notable Assumptions

The header intentionally exposes a small byte-addressed API. Backing implementation choices, sharing policy, accounting, and fallback creation strategies live in `xfile.c`.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfile.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag.c

## Role

`xfs_ag.c` implements allocation-group infrastructure for userspace libxfs: per-AG initialization and teardown, incore counter rebuilding, AG/inode geometry helpers, new AG header construction for growfs, tail-AG shrink/extend operations, growfs delta computation, and AG geometry reporting.

## Major Responsibilities

- Rebuild incore superblock inode/free-block counters by reading every AGF/AGI.
- Allocate and insert `struct xfs_perag` objects into the generic xfs group table.
- Free per-AG resources over a specified AG range.
- Calculate AG block counts, including the shorter final AG.
- Calculate valid AG inode-number ranges based on AGFL location and inode cluster alignment.
- Update the previous last AG size after growfs recovery.
- Initialize secondary superblocks, AGF, AGFL, AGI, and root btree blocks for new AGs.
- Shrink the final AG after validating inode and free-space constraints.
- Compute growfs block delta and resulting AG count.
- Extend the final AG and free the newly added space.
- Return AG geometry and health information.

## Per-AG Initialization

`xfs_initialize_perag` allocates per-AG objects from the old AG count to the new AG count. `xfs_perag_alloc` allocates the structure, initializes its buffer cache, computes block count and minimum group block number, precalculates valid inode range, and inserts it through `xfs_group_insert`. On failure, new perags are unwound with `xfs_free_perag_range`.

`xfs_initialize_perag_data` reads each AGF and AGI to populate perag counters, sums free inodes, total inodes, free blocks, freelist blocks, and btree blocks, validates the totals against the superblock, updates incore counters under `m_sb_lock`, and reinitializes percpu counters.

## New AG Header Initialization

`xfs_ag_init_headers` prepares uncached buffers for all headers and root blocks required by a new AG. It initializes secondary superblock, AGF, AGFL, AGI, bnobt/cntbt roots, inobt/finobt roots, rmapbt root records, and refcountbt root when enabled. Prepared buffers are queued to the caller's delayed-write list.

## Shrink And Extend

`xfs_ag_shrink_space` only applies to the last AG. It reads AGI/AGF, checks matching lengths and nonzero remaining length, verifies the new end will not overlap inode clusters, frees per-AG reservations, allocates the to-be-removed tail extent exactly out of free-space btrees, tries to reinitialize reservations against the shorter AG, updates AGI/AGF lengths and perag geometry, and logs header length fields.

`xfs_ag_extend_space` also targets the last AG. It increases AGI and AGF lengths, logs both, removes the new space from rmap as skipped-update space, frees the extent into normal free space accounting, and updates perag block count and inode range.

## Geometry Reporting

`xfs_ag_get_geometry` locks AGI and AGF via read helpers, fills `struct xfs_ag_geometry` with AG number, inode counts, length, and free blocks. Reported free blocks include free, freelist, and btree blocks minus needed per-AG reservations, then health state is attached through `xfs_ag_geom_health`.

## Notable Assumptions

- AG shrink/extend is restricted to the current last AG.
- New AG headers are written through uncached buffers because they can be beyond current valid filesystem address space.
- The growfs code relies on `sb_inprogress` in secondary superblocks to detect incomplete activation.
- Rmap initialization during grow does not account for internal log space except where explicitly present in an AG.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag.h

## Role

`xfs_ag.h` defines the userspace-visible per-allocation-group structures, state flags, reference helpers, validation helpers, iteration macros, growfs header initialization data, and AG geometry function prototypes shared by libxfs AG code.

## Major Definitions

- `struct xfs_ag_resv` tracks original reserved blocks, current reserved blocks, and requested reservation size.
- `struct xfs_perag` embeds `struct xfs_group` and caches AGF/AGI-derived counts, btree levels, freelist/free-space state, inode counts, inode allocation search hints, refcount btree height, metadata and rmapbt reservations, and precalculated valid inode range.
- `XFS_AGSTATE_*` bit positions represent AGF initialized, AGI initialized, metadata-preferred AG, inode-allowed AG, and AGFL-needs-reset state.
- `aghdr_init_data` carries per-AG and per-header state for initializing new AG headers during growfs.

## Reference And Iteration Helpers

The header wraps generic group references with AG-specific helpers: `xfs_perag_get`, `xfs_perag_put`, `xfs_perag_hold`, `xfs_perag_grab`, `xfs_perag_rele`, `xfs_perag_next_range`, `xfs_perag_next_from`, `xfs_perag_next`, `xfs_perag_next_wrap`, and `for_each_perag_wrap*`.

## Validation And Conversion Helpers

`xfs_verify_agbno` and `xfs_verify_agbext` defer to generic group block validation. `xfs_verify_agino` checks that an AG inode number lies within precalculated `agino_min`/`agino_max`; `xfs_verify_agino_or_null` also accepts `NULLAGINO`.

`xfs_ag_contains_log` detects an AG containing the internal log. `xfs_agbno_to_fsb`, `xfs_agbno_to_daddr`, and `xfs_agino_to_ino` convert AG-relative block/inode values to filesystem block, disk address, and absolute inode number.

## Public Operations Declared

The header declares perag initialization/freeing, perag data initialization, final-AG size update, AG block count and inode range helpers, AG header initialization, AG shrink/extend, growfs delta computation, and AG geometry retrieval.

## Notable Assumptions

- Kernel-only fields are guarded by `__KERNEL__`; xfsprogs uses the shared structure prefix plus userspace-safe fields.
- AG operational state helpers are generated by macro and test atomic bit state in `pag_opstate`.
- The inline `xfs_perag_next_wrap` releases the current active AG reference before attempting the next one.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag.h -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.c -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.c

## Role

`xfs_ag_resv.c` manages per-allocation-group block reservations for metadata structures whose future btree growth must be protected from ENOSPC. It is especially important for reflink/refcountbt and rmapbt behavior in nearly full AGs.

## Major Responsibilities

- Determine when a per-AG reservation is critically low.
- Report how many reserved blocks must remain unavailable to ordinary allocation.
- Initialize metadata and rmapbt reservations from calculated btree needs.
- Free reservations and return hidden blocks to global free-block accounting.
- Charge allocations against reservation pools or normal free-block counters.
- Return freed extents to reservation pools before normal counters.

## Reservation Model

The file describes reservations as virtual allocations maintained with incore accounting. The allocator's usable space is reduced, global `fdblocks` is adjusted, and each AG tracks remaining reserved blocks. This avoids requiring on-disk cleanup after a crash while keeping expansion space available for metadata btrees.

There are two active reservation pools:

- `XFS_AG_RESV_METADATA` for metadata btrees such as refcountbt and finobt where used blocks are already accounted as allocated, so only unused reservation is hidden.
- `XFS_AG_RESV_RMAPBT` for rmapbt blocks that live in free space, so the full reservation is hidden from `fdblocks`.

## Initialization And Freeing

`xfs_ag_resv_init` calculates metadata reservation needs with `xfs_refcountbt_calc_reserves` and `xfs_finobt_calc_reserves`, then rmapbt needs with `xfs_rmapbt_calc_reserves`. If the combined finobt/refcount reservation fails, it sets `m_finobt_nores` and retries with only refcountbt needs for backward compatibility with filesystems created before finobt reservations.

`__xfs_ag_resv_init` subtracts hidden space from `fdblocks`, adjusts `m_ag_max_usable` for AG 0, and records asked/original/current reservation values. `xfs_ag_resv_free` frees rmapbt and metadata reservations, restoring `m_ag_max_usable` for AG 0 and adding reserved blocks back to `fdblocks`.

After creating reservations, `xfs_ag_resv_init` ensures AGF data is initialized and checks that remaining reservation does not exceed AG free blocks plus AGFL blocks; if it does, it reports `-ENOSPC` while leaving policy decisions to callers.

## Allocation And Free Charging

`xfs_ag_resv_alloc_extent` handles reservation-aware allocation accounting. AGFL and metafile reservations do nothing here. Metadata/rmapbt allocations consume `ar_reserved` first; metadata allocations update reserved-freeblock accounting for reserved portions and normal freeblock accounting for any excess. Rmapbt reserved allocations do not update the superblock because their full reservation was hidden up front. Non-reserved allocations update normal freeblock counters.

`xfs_ag_resv_free_extent` refills reservation pools up to `ar_asked` before crediting normal free blocks. Rmapbt frees only refill the pool; metadata frees update reserved counters for the refilled portion and normal counters for leftovers.

## Criticality

`xfs_ag_resv_critical` treats a reservation as critically low when available blocks fall below 10 percent of the original asked amount, below maximum AG btree height, or the `XFS_ERRTAG_AG_RESV_CRITICAL` fault-injection tag triggers.

## Notable Assumptions

- Reservation type dispatch asserts on unexpected types but gracefully treats `XFS_AG_RESV_NONE` as normal accounting.
- AG 0 is used to adjust the filesystem-wide `m_ag_max_usable`, assuming it is not less hungry than other AGs.
- Initialization can intentionally leave callers with `-ENOSPC` after partial setup so higher-level grow/shrink/mount code can decide whether to continue.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.h -->
# File Research: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.h

## Role

`xfs_ag_resv.h` declares the per-AG reservation interface used by allocation and AG management code.

## Interface

- `xfs_ag_resv_free` releases both metadata and rmapbt reservations for an AG.
- `xfs_ag_resv_init` calculates and creates reservations for an AG.
- `xfs_ag_resv_critical` reports whether a reservation pool is dangerously low.
- `xfs_ag_resv_needed` returns reserved blocks that must be withheld from ordinary allocation.
- `xfs_ag_resv_alloc_extent` charges an allocation to a reservation or normal accounting.
- `xfs_ag_resv_free_extent` returns freed blocks to a reservation or normal accounting.
- `xfs_perag_resv` maps `XFS_AG_RESV_METADATA` and `XFS_AG_RESV_RMAPBT` to the corresponding fields inside `struct xfs_perag`.

## Notable Assumptions

`xfs_perag_resv` returns `NULL` for unsupported reservation types; callers in `xfs_ag_resv.c` validate types before dereferencing. The header depends on `struct xfs_perag`, `struct xfs_trans`, `struct xfs_alloc_arg`, and reservation enum definitions supplied by surrounding libxfs headers.
<!-- END FILE RESEARCH: sources/local-fs/xfsprogs/libxfs/xfs_ag_resv.h -->