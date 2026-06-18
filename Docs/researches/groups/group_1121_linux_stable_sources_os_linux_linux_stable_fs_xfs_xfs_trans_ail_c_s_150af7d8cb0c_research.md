# Group Research: group_1121_linux_stable_sources_os_linux_linux_stable_fs_xfs_xfs_trans_ail_c_s_150af7d8cb0c

Scope: `Docs/research_subset_a.md` only. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_ail.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_ail.c

## Purpose

Implements XFS Active Item List (AIL) management. The AIL tracks committed but not-yet-written log items in LSN order so the log tail can advance only after metadata reaches stable storage.

## Main Responsibilities

- Maintains the sorted AIL list and minimum/tail LSN queries.
- Provides cursor-safe AIL traversal for pushers and other scanners.
- Inserts, moves, and deletes log items while updating log tail space.
- Runs the `xfsaild` kernel thread to push dirty metadata items toward disk.
- Handles failed buffer resubmission through delayed-write queues.
- Implements push-all synchronization for unmount/quiesce paths.
- Initializes and destroys the per-mount AIL state.

## Important Invariants

- AIL ordering is by ascending `li_lsn`.
- Cursors must be invalidated when pointed-at items are removed or moved.
- Push callbacks can drop and reacquire the AIL lock, so callers must not dereference items after push.
- Log tail updates happen only when the minimum AIL LSN changes or when explicitly forced.
- Failed buffer items must be queued for I/O before clearing failed state to avoid transient zero-reference use-after-free hazards.
- The push daemon backs off when too many items are pinned, locked, or already flushing.

## Dependencies

Uses XFS log, CIL, buffer delayed-write, log item ops, stats, tracepoints, shutdown state, and kernel kthread/freezer infrastructure.

## Research Notes

This is correctness-critical for log-space reclamation. The most important behavior is preserving AIL order while allowing concurrent item removal and push callbacks that temporarily drop locks.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_ail.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_buf.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_buf.c

## Purpose

Implements transaction integration for XFS metadata buffers. It joins buffers to transactions, tracks logged byte ranges, manages buffer recursion/holds, and marks buffer log items for recovery.

## Main Responsibilities

- Finds buffers already attached to a transaction.
- Gets, reads, locks, and joins buffers to transactions.
- Handles superblock and realtime superblock buffer joins.
- Releases or forcibly detaches clean buffers from transactions.
- Marks buffers dirty, stale, ordered, inode-buffer, inode-allocation-buffer, or dquot-buffer.
- Logs byte ranges through buffer log items.
- Assigns buffer type metadata for log recovery.

## Important Invariants

- Joined buffers must be locked and have a valid buffer log item.
- Recursive buffer lookups increment `bli_recur` instead of relocking.
- Dirty or stale buffers remain attached until transaction commit/cancel.
- Stale buffers set cancel flags so recovery ignores older logged copies.
- Ordered buffers cannot already have dirty logged format ranges.
- Buffer type flags are recovery-facing and must match the on-disk metadata contents.

## Dependencies

Uses XFS buffer cache, buffer log item code, transaction item lists, verifier ops, shutdown handling, and recovery buffer type definitions.

## Research Notes

The high-risk logic is around buffer lifetime and state transitions: recursion counts, stale cancellation, ordered-buffer semantics, and verifier failure shutdown behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_buf.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_dquot.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_dquot.c

## Purpose

Implements transactional quota accounting for XFS dquots. It records quota deltas in transactions, reserves quota resources, applies committed changes, and unwinds reservations on abort.

## Main Responsibilities

- Joins locked dquots to transactions and marks them dirty.
- Duplicates quota reservation state across rolling transactions.
- Tracks per-transaction block, realtime block, inode, delayed allocation, and reservation deltas.
- Applies dquot deltas at commit time.
- Releases reservations when transactions abort.
- Checks hard/soft quota limits and emits quota warnings.
- Reserves quotas by dquot set, by inode blocks, and for inode creation.
- Supports live quota hooks for online checking when configured.

## Important Invariants

- Per-transaction dquot arrays are sequential, not sparse.
- Dquots are locked before committed counter updates.
- Reservation counters must never fall below actual usage counters.
- User, group, and project quota reservations follow all-or-nothing unwind semantics.
- Project quota fatal reservation failures return `-ENOSPC`; user/group generally return `-EDQUOT`.
- Live hook installation/removal order preserves complete update sequences.

## Dependencies

Uses XFS quota manager, dquot locks, transaction item handling, health marking, warning delivery, live hooks, and quota default limit/timer adjustment.

## Research Notes

This file is the transactional boundary for quota consistency. The subtle parts are reservation carry-forward, delayed allocation accounting, and rollback after partial multi-dquot reservation failure.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_dquot.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_priv.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_trans_priv.h

## Purpose

Defines private XFS transaction and AIL structures and helper declarations shared by transaction implementation files.

## Main Responsibilities

- Declares private transaction helper functions.
- Defines `struct xfs_ail_cursor`.
- Defines `struct xfs_ail` and AIL state fields.
- Provides inline AIL helpers for minimum item, push, push-all, target reads, and tail assignment.
- Declares AIL cursor, update, insert, delete, and init-facing helpers.
- Provides architecture-aware 64-bit LSN copy helper.

## Important Invariants

- AIL cursor invalidation uses the low bit of the item pointer.
- `ail_lock` protects AIL list, cursor list, target, and tail-update coordination.
- `xfs_trans_ail_update` and related helpers release `ail_lock`.
- 32-bit platforms lock while copying 64-bit LSN values.

## Dependencies

Depends on XFS log item, transaction, AIL, mount, and Linux list/spinlock/waitqueue primitives.

## Research Notes

This header captures the private contract between the transaction core and AIL implementation. The cursor invalidation scheme is the key design detail.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_trans_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.c

## Purpose

Implements the XFS media verification ioctl. It reads device ranges to detect media/protection errors and optionally reports data loss through health monitoring and reverse mapping.

## Main Responsibilities

- Validates user-supplied verification request fields.
- Selects data, log, or realtime target device.
- Verifies logical-sector-aligned disk ranges with synchronous read bios.
- Chooses verification I/O size, up to a requested/user-limited maximum.
- Reports media, protection, and I/O failures to health monitoring.
- Uses reverse mapping to notify affected inodes of lost file data.
- Updates the request start address to the verified progress point.

## Important Invariants

- Start and end disk addresses must align to the target logical sector size.
- End address is exclusive and is clamped to device size.
- Errors before any verified byte are returned to userspace.
- Only protection, medium, and generic I/O failures are treated as data-loss reports.
- Rmap-based file loss reporting requires rmapbt support.
- Verification can be interrupted by fatal signals between bios.

## Dependencies

Uses Linux bios/folios, XFS btrees, rmap/rtrmap, allocation groups, realtime groups, inode lookup, healthmon, and ioctl copy helpers.

## Research Notes

This file is diagnostic and reporting code, not repair code. Its most important behavior is mapping physical verification failures back to affected file ranges when rmap metadata exists.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.h

## Purpose

Declares the XFS media verification ioctl entry point.

## Main Responsibilities

- Forward-declares `struct xfs_verify_media`.
- Declares `xfs_ioc_verify_media`.

## Important Invariants

- Keeps the ioctl implementation interface isolated from callers.

## Dependencies

Depends on `struct file` and the UAPI media verification structure.

## Research Notes

Small public-private header for wiring ioctl dispatch to `xfs_verify_media.c`.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_verify_media.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.c

## Purpose

Provides XFS VFS extended attribute integration. It maps Linux xattr namespaces to XFS attribute operations and implements listxattr formatting.

## Main Responsibilities

- Enables log-assisted xattrs for debug/LARP configurations when supported.
- Performs xattr set/create/replace/remove through `xfs_attr_change`.
- Attaches quotas before attribute updates.
- Provides user, trusted, and security xattr handlers.
- Converts VFS xattr flags into XFS attribute update operations.
- Lists xattrs with namespace prefixes.
- Hides private namespaces and gates trusted entries behind `CAP_SYS_ADMIN`.
- Translates legacy ACL xattr names to system POSIX ACL names.

## Important Invariants

- Shutdown filesystems reject xattr changes with `-EIO`.
- Attribute fork zap state rejects get/list operations.
- Root/security namespaces may use reserved blocks to avoid ENOSPC failures for critical metadata.
- Logged xattrs require a compatible filesystem feature set.
- `listxattr` returns `-ERANGE` if the caller buffer is too small.

## Dependencies

Uses XFS attr/libxfs code, DA args, quota attach, ACL helpers, VFS xattr handlers, and incompat log feature management.

## Research Notes

This is mostly an adapter layer. The high-risk behavior is enabling logged xattrs and correctly translating namespace exposure and ACL names.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.h

## Purpose

Declares XFS xattr change and handler interfaces.

## Main Responsibilities

- Forward-declares `enum xfs_attr_update`.
- Declares `xfs_attr_change`.
- Exposes `xfs_xattr_handlers`.

## Important Invariants

- Keeps VFS xattr registration separate from implementation details.

## Dependencies

Depends on XFS DA args and Linux xattr handler declarations.

## Research Notes

Small header used to connect XFS inode/VFS setup to the xattr implementation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.c

## Purpose

Implements the XFS zoned realtime allocator. It manages open zones, allocates write placement for zoned data I/O, maps completed writes into files, tracks reclaimable zones, and initializes zone state at mount.

## Main Responsibilities

- Maintains `struct xfs_open_zone` references and RCU freeing.
- Tracks free, open, GC, full, and reclaimable zones.
- Buckets reclaimable fully written zones by used-block percentage.
- Selects open zones based on write lifetime hints, LRU/MRU policy, and small-file packing.
- Opens new zones subject to open-zone and GC reserve limits.
- Allocates physical blocks from open zones for iomap writeback.
- Submits zone append or conventional write bios.
- Converts completed zoned writes into data fork mappings.
- Frees zoned blocks by decrementing per-zone rmap used counters.
- Reconstructs zone write pointers and open/free/reclaimable state at mount.
- Calculates open-zone limits and initializes/tears down zoned mount state.

## Important Invariants

- `oz_allocated` is protected by `oz_alloc_lock`.
- `oz_written` is protected by the realtime group rmap inode lock.
- `oz_written <= oz_allocated`.
- A full open zone is removed from open-zone accounting and may become reclaimable.
- Empty zones are marked `XFS_RTG_FREE`.
- Sequential zones use hardware write pointers; conventional zones infer the write pointer from rmap.
- Zoned filesystems require realtime groups, rmapbt, `rextsize == 1`, and a minimum zone count.
- Completed GC writes must not overwrite newer user writes; old startblock comparison detects races.

## Dependencies

Uses XFS realtime groups, rmap inodes, iomap ioends, bmap/refcount/free extent logic, free counters, zone validation, GC hooks, write hints, and block-device zone APIs.

## Research Notes

This is the core zoned XFS allocator. The most subtle paths are write completion remapping, open-zone reference caching in inodes, reclaimable accounting transitions, and mount-time recovery of zone state after power loss.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.h

## Purpose

Declares the public zoned XFS allocation, reservation, I/O completion, and GC-control interfaces.

## Main Responsibilities

- Defines `struct xfs_zone_alloc_ctx`.
- Defines reservation flags: greedy, nowait, and reserved-pool use.
- Declares zoned space reserve/unreserve helpers.
- Declares zoned write allocation/submission and end-I/O mapping helpers.
- Declares zoned block free, wake, stats, mount, unmount, and GC control functions.
- Provides no-RT fallback stubs for mount/GC functions.

## Important Invariants

- Allocation contexts track both reserved blocks and a held open-zone reference.
- Zoned mount support requires `CONFIG_XFS_RT`.
- Reserved and nowait flags affect both user capacity and immediately available capacity accounting.

## Dependencies

Exposes interfaces used by XFS writeback, realtime allocation, free-space accounting, and mount code.

## Research Notes

This header is the main cross-file API for the zoned allocator stack.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_alloc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_gc.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_gc.c

## Purpose

Implements garbage collection for zoned XFS. GC evacuates live extents from partially used zones into GC target zones, remaps files to the new locations, and resets empty zones for reuse.

## Main Responsibilities

- Determines when GC is needed from available/free realtime counters and low-space policy.
- Allocates GC state, scratch folios, bioset, and rmap lookahead records.
- Selects victim zones from reclaimable used-block buckets.
- Queries victim-zone rmap records and sorts them by inode/offset.
- Reads live file extents into scratch buffers.
- Allocates GC target blocks from reserved pools.
- Writes chunks using zone append or conventional writes, splitting at hardware append limits.
- Finishes chunks by breaking layouts, waiting for DIO, and calling `xfs_zoned_end_io`.
- Resets empty zones after flushing the realtime device and forcing rmap inode logs.
- Runs the `xfs-zone-gc` kthread with park/unpark, freezer, stop, and wakeup support.

## Important Invariants

- GC zones use reserved capacity to avoid deadlock with user writers waiting for GC.
- Victim zones with active GC references are skipped.
- GC I/O completions are processed in order to preserve sorted remap behavior.
- Reflink is not supported on zoned filesystems because GC would break sharing.
- Zone reset is issued only after used blocks reach zero and relevant metadata is forced.
- Failed GC I/O forces metadata I/O shutdown.

## Dependencies

Uses XFS rtrmap btrees, inode cache, realtime group references, zoned allocator APIs, bio/bioset APIs, block queue limits, free counters, log forcing, and kthread/freezer infrastructure.

## Research Notes

This is a speculative copy-and-remap collector. The central safety property is that `xfs_zoned_end_io` verifies mappings have not changed before remapping newly copied data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_gc.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_info.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_info.c

## Purpose

Provides debug/stat reporting for XFS zoned allocation state.

## Main Responsibilities

- Converts write lifetime hints to short strings.
- Prints open-zone state including write pointer, written count, used blocks, hint, and GC marker.
- Prints distribution of fully written reclaimable zones by used-block bucket.
- Prints zoned free counters, reservation state, GC-needed state, zone counts, and open-zone counts.

## Important Invariants

- Open-zone list output is protected by `zi_open_zones_lock`.
- Used-bucket distribution output is protected by `zi_used_buckets_lock`.
- “100%” bucket is derived from total zones minus free/open/GC/reclaimable zones.

## Dependencies

Uses seq_file, XFS free counters, zoned allocator private state, realtime group/rmap state, and GC need checks.

## Research Notes

This file is observability-only and helps diagnose allocator/GC pressure and zone placement behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_info.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_priv.h -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_priv.h

## Purpose

Defines private data structures and helper declarations shared by XFS zoned allocator and GC implementation files.

## Main Responsibilities

- Defines `struct xfs_open_zone`.
- Defines `XFS_ZONE_USED_BUCKETS`.
- Defines `struct xfs_zone_info`.
- Declares open-zone, reset, GC, reclaimable, and reservation wake helpers.

## Important Invariants

- `oz_allocated` is protected by `oz_alloc_lock`.
- `oz_written` is protected by the rmap inode lock.
- `oz_rtg` remains constant for the open-zone lifetime.
- Open-zone list/counts are protected by `zi_open_zones_lock`.
- Reclaimable bucket bitmaps/counts are protected by `zi_used_buckets_lock`.
- Reservation waiters are protected by `zi_reservation_lock`.

## Dependencies

Used internally by `xfs_zone_alloc.c`, `xfs_zone_gc.c`, `xfs_zone_info.c`, and `xfs_zone_space_resv.c`.

## Research Notes

This header captures the private concurrency contract for zoned allocation.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_priv.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_space_resv.c -->
# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_zone_space_resv.c

## Purpose

Implements zoned XFS space reservation accounting. It reserves both user-visible realtime extents and immediately available write space, coordinating waiters with GC.

## Main Responsibilities

- Calculates default reserved blocks for realtime extents and immediately available blocks.
- Maintains per-task reservation waiters.
- Wakes reservation waiters on shutdown or new available space.
- Adds newly available blocks and wakes waiters in reservation order.
- Reserves immediately available blocks, waiting for GC when needed.
- Implements greedy partial reservation for short writes.
- Reserves and unreserves zoned allocation contexts.

## Important Invariants

- Zoned allocator treats realtime extents and filesystem blocks interchangeably because `rextsize > 1` is unsupported.
- `XC_FREE_RTEXTENTS` is user capacity; `XC_FREE_RTAVAILABLE` is instantly writable capacity.
- Waiters are queued under `zi_reservation_lock`.
- Reserved-pool callers bypass the waiter list.
- NOWAIT callers return `-EAGAIN` instead of sleeping.
- Failed available-space reservation returns the user-visible extent reservation.

## Dependencies

Uses XFS free counters, inodegc flushing, zoned GC state, reclaimable checks, reservation waitqueues, and open-zone ref release.

## Research Notes

This file bridges logical filesystem ENOSPC behavior and the physical constraint that zoned filesystems may need GC before free space is immediately writable.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/xfs/xfs_zone_space_resv.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/Kconfig -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/Kconfig

## Purpose

Defines the kernel configuration option for zonefs.

## Main Responsibilities

- Adds `CONFIG_ZONEFS_FS`.
- Requires block-layer support and zoned block devices.
- Selects iomap and CRC32 support.
- Describes zonefs as exposing zones of a zoned block device as files.

## Important Invariants

- zonefs cannot be built without `BLK_DEV_ZONED`.
- iomap and CRC32 are required implementation dependencies.

## Dependencies

Kernel Kconfig system, block layer, zoned block device support, iomap, CRC32.

## Research Notes

Build-time entry point for enabling zonefs.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/Kconfig -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/Makefile -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/Makefile

## Purpose

Defines zonefs build objects.

## Main Responsibilities

- Adds local include path.
- Builds `zonefs.o` under `CONFIG_ZONEFS_FS`.
- Links `super.o`, `file.o`, and `sysfs.o`.

## Important Invariants

- `trace.h` is included through local source include path.
- zonefs is built as a single composite object.

## Dependencies

Kernel kbuild and `CONFIG_ZONEFS_FS`.

## Research Notes

Minimal kbuild wiring for the zonefs module/filesystem.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/file.c -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/file.c

## Purpose

Implements zonefs regular file operations and address-space operations. Each file maps directly to a zone or aggregated conventional zones.

## Main Responsibilities

- Provides iomap mappings for reads, writes, writeback, and direct I/O.
- Supports buffered I/O only for conventional zone files.
- Enforces direct-only sequential-zone writes.
- Enforces append/write-pointer ordering for sequential zones.
- Handles truncate-to-zero as zone reset and truncate-to-capacity as zone finish.
- Updates inode size and zone write pointer on direct write completion.
- Handles fsync via page-cache writeback for conventional files and block flush.
- Supports mmap with shared writable mappings only for conventional files.
- Handles read, splice read, write, llseek, open, release, and swap activation.
- Implements explicit zone open/close accounting for sequential write opens.

## Important Invariants

- Sequential zone files accept writes only at `z_wpoffset`.
- Sequential direct writes must be block aligned.
- Sequential files cannot use buffered writes or shared writable mmap.
- Truncate is allowed only to 0 or zone capacity and only for sequential files.
- Async NOWAIT direct writes to sequential files are rejected to avoid reordering.
- Successful sequential write completion can advance inode size because preceding writes must also have completed.
- Explicit-open files must close zones on last writer close, but close errors are not returned from `close(2)`.

## Dependencies

Uses iomap buffered/direct/writeback APIs, block device flush and zone management via super.c helpers, inode locks, invalidate locks, mmap VM ops, and zonefs tracepoints.

## Research Notes

This is the central zonefs I/O enforcement layer. The key correctness property is keeping VFS inode size, `z_wpoffset`, and device write pointer consistent across writes, truncates, and error recovery.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/file.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/super.c -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/super.c

## Purpose

Implements zonefs mount, superblock parsing, zone discovery, inode/directory construction, statfs, mount options, error recovery, and module registration.

## Main Responsibilities

- Registers zonefs filesystem type and inode cache.
- Parses mount options: `errors=` and `explicit-open`.
- Reads and validates the zonefs on-disk superblock, CRC, features, UID/GID, permissions, and UUID.
- Reports block-device zones and builds conventional/sequential zone groups.
- Creates root, zone group directory, and zone file inodes.
- Aggregates contiguous conventional zones when the feature is enabled.
- Tracks used blocks and active/open sequential zone counts.
- Executes zone management operations.
- Handles runtime I/O errors by re-reporting zone condition and updating inode mode/size/write pointer.
- Implements lookup/readdir for the generated namespace.
- Handles remount option updates and unmount cleanup.

## Important Invariants

- zonefs can mount only zoned block devices.
- First zone contains the zonefs superblock and is not exposed as a file.
- File names are decimal zone-group indices without leading zeroes.
- Sequential zone active/open accounting excludes conventional zones.
- Offline zones become unreadable/unwritable immutable files.
- Read-only zones become immutable and lose write permissions.
- `explicit-open` is ignored if the device reports no open or active zone limits.
- The filesystem block size is set to device zone write granularity.

## Dependencies

Uses Linux fs_context, block zoned APIs, CRC32, inode cache, dentry/inode helpers, sysfs registration, iomap-facing file ops, and zonefs tracepoints.

## Research Notes

This file synthesizes a filesystem namespace from block device zone state. Its most important runtime behavior is error recovery, where zone condition and write pointer are re-read to prevent exposing invalid data.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/super.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/sysfs.c -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/sysfs.c

## Purpose

Implements zonefs sysfs attributes under the global `fs/zonefs` kobject.

## Main Responsibilities

- Defines read-only sysfs attributes for max/current write-open sequential files.
- Defines read-only sysfs attributes for max/current active sequential files.
- Registers a per-superblock kobject named after the superblock id.
- Unregisters and waits for kobject release during teardown.
- Initializes and exits the global zonefs sysfs root.

## Important Invariants

- Per-superblock sysfs unregister waits for release completion.
- Attribute show dispatch uses container lookup from kobject and attribute.
- Registration state prevents double unregister.

## Dependencies

Uses sysfs/kobject APIs, superblock sysfs naming, and zonefs superblock info fields.

## Research Notes

Small observability layer for device open/active zone resource tracking.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/sysfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/trace.h -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/trace.h

## Purpose

Defines zonefs tracepoints for zone management, direct append writes, and iomap mappings.

## Main Responsibilities

- Declares `zonefs_zone_mgmt` trace event.
- Declares `zonefs_file_dio_append` trace event.
- Declares `zonefs_iomap_begin` trace event.
- Sets trace include path and includes `trace/define_trace.h`.

## Important Invariants

- Trace events record device major/minor and inode/zone identifying data.
- Zone management traces derive file inode number from zone sector and zone-size shift.
- Iomap traces capture address, offset, and length.

## Dependencies

Linux tracepoint infrastructure, block operation string helpers, and zonefs structures.

## Research Notes

Tracing support for diagnosing zone management and block mapping behavior.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/trace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/zonefs.h -->
# File Research: sources/os/linux/linux-stable/fs/zonefs/zonefs.h

## Purpose

Defines the primary zonefs in-memory and on-disk structures, constants, feature flags, mount options, helper functions, and cross-file declarations.

## Main Responsibilities

- Defines zone types, flags, and type helpers.
- Defines per-zone, per-zone-group, per-inode, on-disk superblock, and per-superblock structures.
- Defines feature flags for conventional aggregation, UID, GID, and permissions.
- Defines mount option flags for error handling and explicit zone opens.
- Provides inline helpers for inode/private zone access and I/O error locking.
- Declares super, file, and sysfs interfaces.

## Important Invariants

- Zonefs file names need only fit group names and decimal zone numbers.
- Sequential zones include both required and preferred sequential zone block types.
- `i_truncate_mutex` serializes truncate, iomap begin, private zone state, write refcount, and sequential size updates.
- Offline/read-only state is tracked in zone flags and reflected into inode mode.
- On-disk superblock size is fixed at 4096 bytes.
- Defined feature bits are strictly enumerated.

## Dependencies

Uses Linux VFS, magic numbers, UUIDs, mutex/rwsem/kobject APIs, block zone definitions, and iomap-facing file declarations.

## Research Notes

This header is the architectural map for zonefs: zone files are synthetic inodes backed directly by block-device zone geometry and write-pointer state.
<!-- END FILE RESEARCH: sources/os/linux/linux-stable/fs/zonefs/zonefs.h -->