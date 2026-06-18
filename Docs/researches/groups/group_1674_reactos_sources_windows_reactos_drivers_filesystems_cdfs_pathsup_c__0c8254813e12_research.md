# Group Research: group_1674_reactos_sources_windows_reactos_drivers_filesystems_cdfs_pathsup_c__0c8254813e12

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/pathsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/pathsup.c

Implements CDFS ISO-9660 path-table traversal. The path table is used as a compact breadth-first directory index, with directory ordinals and parent ordinals used to locate children without scanning full directory contents first.

Key entry points:
- `CdLookupPathEntry()` maps the path-table block containing a known entry offset and decodes the raw entry into a `PATH_ENTRY`.
- `CdLookupNextPathEntry()` advances by the current entry length, remaps the next two-sector window when needed, and decodes the next ordinal.
- `CdFindPathEntry()` scans child path-table entries for a parent directory, caches the first-child offset/ordinal in the parent FCB, converts candidate names, and compares them against the requested directory name.
- `CdMapPathTableBlock()` maps two sectors through cache manager, or copies two one-sector mappings into an auxiliary buffer when the window crosses a VACB boundary.
- `CdUpdatePathEntryFromRawPathEntry()` validates and translates raw path-table fields into the common in-memory representation.
- `CdUpdatePathEntryName()` converts raw directory names into `CD_NAME` structures for ISO/OEM or Joliet big-endian Unicode names.

Core mechanics:
- Path-table entries are read in two-sector windows because entries can span sector boundaries.
- `LastDataBlock` and `DataLength` bound parsing of the final mapped path-table block.
- Parent ordinals drive child-range scanning; children of a parent are contiguous because the table is breadth-first.
- The parent FCB caches `ChildPathTableOffset` and `ChildOrdinal` after the first child is found, avoiding repeat scans from the parent entry.
- ISO names are converted with `RtlOemToUnicodeN`; Joliet names are byte-swapped from big-endian to little-endian.
- The self/root entry with one zero byte is mapped to the hard-coded directory name.

Important invariants:
- Path-table parent ordinals are 16-bit on disk, so searching children of an FCB with ordinal greater than `MAXUSHORT` raises disk corruption.
- A zero-length path-table name is normally corrupt, except for a compatibility workaround when the final table block is padded to a block boundary.
- Parsed `PathEntryLength` is word-aligned.
- Directory path-table names have no version string.

Filesystem relevance:
- This file is the fast directory-discovery layer used before full directory-entry enumeration.
- Correct path-table parsing controls directory opens and the construction of directory FCBs.

Notable risks:
- Corrupt path-table bounds, zero-length records, or illegal parent ordinals raise hard disk-corruption statuses.
- Auxiliary path-table buffers must be freed/remapped correctly when crossing cache view boundaries.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/pathsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/pnp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/pnp.c

Handles Plug and Play IRPs delivered to CDFS volume device objects, including query-remove, remove, surprise-remove, and cancel-remove.

Key entry points:
- `CdCommonPnp()` validates the target as a CDFS volume device object, forces synchronous handling, finds the VCB, dispatches known minor functions, and passes unknown requests down the stack.
- `CdPnpQueryRemove()` locks the volume, sends the query down synchronously, and starts forced dismount if lower drivers accept removal.
- `CdPnpRemove()` unlocks or invalidates the volume, passes the remove IRP down, then forces dismount.
- `CdPnpSurpriseRemove()` marks the VCB invalid immediately, passes surprise removal down, then attempts dismount.
- `CdPnpCancelRemove()` reverses a prior query-remove by unlocking the volume and passing the cancel down.
- `CdPnpCompletionRoutine()` signals a stack-local event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can finish synchronously.

Core mechanics:
- PnP requests have no file object, so the VCB is recovered from the volume device object.
- `CdData.DataResource` serializes PnP handling against mount, verify, and teardown paths.
- Query/remove/surprise paths copy the current stack location, install a completion event, call the target device, and wait for completion when pending.
- Query-remove keeps a temporary VCB reference while dropping and reacquiring locks around `CdLockVolumeInternal()`.
- Successful query-remove depends on CDFS internal streams closing and dropping their target-device references.

Important invariants:
- `IRP_CONTEXT_FLAG_WAIT` is set so all PnP work is synchronous.
- If the VCB has already been disconnected (`Vpb == NULL`), the request is passed through.
- Query-remove may fail with `STATUS_DEVICE_BUSY` if dismount began but references still remain.
- Surprise-remove has no recovery path; it marks the VCB invalid.

Filesystem relevance:
- Coordinates volume teardown with Windows storage-stack device removal.
- Protects CDFS from stale volume access after media/device removal.

Notable risks:
- Query-remove correctness depends on subtle reference-count behavior of internal stream file objects and outside holders such as tracing components.
- Pass-through uses `Vcb->TargetDeviceObject`; the code relies on the VCB still being valid for the pass-through path after validation.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/prefxsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/prefxsup.c

Implements per-directory prefix/name caches for CDFS FCBs using exact-case and case-insensitive splay trees.

Key entry points:
- `CdInsertPrefix()` inserts an FCB name, and optionally a short-name prefix, into the parent directory's exact or ignore-case tree.
- `CdRemovePrefix()` removes long-name and short-name prefix entries from the parent trees and frees any allocated long-name buffer.
- `CdFindPrefix()` walks component-by-component from a starting directory FCB, following the longest cached prefix while acquiring child FCBs and releasing parents.
- `CdFindNameLink()` searches and splays a tree around a matching `NAME_LINK`.
- `CdInsertNameLink()` inserts a `NAME_LINK` into the ordered splay tree, ignoring duplicates.

Core mechanics:
- Each directory FCB owns `ExactCaseRoot` and `IgnoreCaseRoot` splay roots.
- A `PREFIX_ENTRY` stores both exact-case and ignore-case names, sharing either an embedded buffer or one allocated buffer split into two halves.
- Short-name entries are allocated lazily as a separate `PREFIX_ENTRY`.
- `CdFindPrefix()` updates the caller's remaining path and, on ignore-case lookup, copies exact-case spelling back into the caller's buffer.
- Child acquisition first tries nonblocking; if it cannot acquire and waiting is allowed, it temporarily references the child, drops the parent, then acquires the child.

Important invariants:
- Prefix entry insertion/removal assumes the parent FCB relationship is stable.
- Duplicate case-insensitive inserts are harmlessly ignored by `CdInsertNameLink()`.
- `CdFindPrefix()` returns with only the lowest matched FCB acquired.
- Teardown recursion is avoided elsewhere, but prefix removal must remain synchronized with FCB tree teardown.

Filesystem relevance:
- Speeds path resolution by caching already discovered child FCB names under their parent directory.
- Preserves exact-case name spelling for case-insensitive opens.

Notable risks:
- Allocation failure in `CdInsertPrefix()` quietly skips cache insertion rather than failing the open.
- Buffer ownership is split between embedded and allocated storage; freeing depends on pointer comparison against the embedded buffer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/prefxsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/read.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/read.c

Implements the common CDFS read path for user files, stream files, and volume/DASD handles.

Key entry points:
- `CdCommonRead()` validates the open type, verifies the FCB/VCB state, checks oplocks and byte-range locks for user files, handles EOF truncation, and performs cached or noncached reads.

Core mechanics:
- Zero-length reads complete successfully immediately.
- Directories and unopened file objects reject reads with `STATUS_INVALID_DEVICE_REQUEST`.
- Volume reads are forced noncached.
- Paging I/O acquires the file shared with starve-exclusive behavior to reduce deadlock risk.
- Noncached reads allocate or reuse a `CD_IO_CONTEXT`, align byte counts to block boundaries, and dispatch to `CdNonCachedRead()` or `CdNonCachedXARead()` for raw-sector/XA files.
- Cached reads initialize the private cache map on first use, set 64 KiB read-ahead, then use `CcCopyRead()` or `CcMdlRead()`.
- Synchronous non-paging reads advance `CurrentByteOffset`.

Important invariants:
- Unaligned noncached reads require a waitable path; otherwise the request is posted.
- Reads past EOF return `STATUS_END_OF_FILE`; reads crossing EOF are truncated unless extended DASD I/O is allowed.
- If aligned noncached I/O reads extra bytes beyond logical EOF/truncated length, the extra user-buffer range is zeroed under SEH.
- Pending noncached I/O retains the file resource through the asynchronous I/O context.

Filesystem relevance:
- This is the primary data path for file reads, directory stream reads, metadata stream reads, and raw volume reads.
- It integrates CDFS file verification, cache manager use, oplock package callbacks, file locks, and XA-sector reads.

Notable risks:
- Noncached raw/XA reads are sensitive to sector alignment, buffer probing, and whether the caller can block.
- User-buffer zeroing is protected, but invalid user buffers still translate into raised `STATUS_INVALID_USER_BUFFER`.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/resrcsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/resrcsup.c

Provides resource-acquisition wrappers and cache-manager/memory-manager synchronization callbacks for CDFS.

Key entry points:
- `CdAcquireResource()` centralizes exclusive, shared, and shared-starve-exclusive acquisition with wait/nowait behavior driven by the IRP context.
- `CdAcquireForCache()` and `CdReleaseFromCache()` are cache-manager lazy-writer callbacks for acquiring/releasing an FCB resource shared.
- `CdNoopAcquire()` and `CdNoopRelease()` are no-op callbacks for streams that do not need resource synchronization.
- `CdFilterCallbackAcquireForCreateSection()` acquires resources for section creation through the FS filter callback path.
- `CdReleaseForCreateSection()` releases resources acquired for section creation.

Core mechanics:
- `CdAcquireResource()` raises `STATUS_CANT_WAIT` when nonblocking acquisition fails and `IgnoreWait` is not set.
- Cache acquisition sets `IoGetTopLevelIrp()` to `FSRTL_CACHE_TOP_LEVEL_IRP` and release clears it.
- Section synchronization takes the nonpaged FCB resource exclusive and the file resource shared-starve-exclusive.
- For create-section synchronization, CDFS returns `STATUS_FILE_LOCKED_WITH_ONLY_READERS`, reflecting the read-only filesystem.

Important invariants:
- Resource callbacks must maintain lock order compatible with cache manager and memory manager paths.
- Lazy-writer callbacks expect no top-level IRP on entry and restore it on release.
- Section-acquire takes both `FcbResource` and `Resource`; release must drop both.

Filesystem relevance:
- These callbacks are required for safe cached I/O, mapped sections, and synchronization with CDFS read-only file state.

Notable risks:
- Deadlock avoidance relies on shared-starve-exclusive acquisition for create-section paths.
- No-op callbacks must only be used where synchronization is intentionally unnecessary.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/resrcsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/shutdown.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/shutdown.c

Implements filesystem shutdown handling for CDFS.

Key entry points:
- `CdCommonShutdown()` marks global shutdown, walks all mounted VCBs, purges each active mounted volume, sends `IRP_MJ_SHUTDOWN` to each target device stack, marks the VCB shut down, and attempts dismount.

Core mechanics:
- Popups are disabled during shutdown.
- The global CDFS data resource is acquired while walking `CdData.VcbQueue`.
- Already-shut-down or non-mounted volumes are skipped.
- A fresh synchronous shutdown IRP is built for each target stack because stack sizes can differ.
- After volume processing, the filesystem device object is unregistered and deleted; ReactOS also unregisters/deletes the HDD filesystem device object.

Important invariants:
- The next VCB list link is captured before processing because the current VCB can be deleted during dismount.
- Shutdown should only process each mounted VCB once.
- `CdCheckForDismount()` decides whether the VCB remains and whether its resource must be released.

Filesystem relevance:
- Coordinates final cache purge and lower-device shutdown during system shutdown.

Notable risks:
- The file system device objects are deleted at the end of shutdown; subsequent dispatch must not target them.
- Any failure to allocate a per-stack shutdown IRP is silently skipped for that volume stack.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/strucsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/strucsup.c

Implements CDFS in-memory structure creation, initialization, lookup, teardown, and deletion for VCBs, FCBs, CCBs, IRP contexts, FCB tables, and audio-CD TOC metadata.

Key entry points:
- `CdInitializeVcb()` zeros and initializes a VCB, resources, notification state, swap VPB, target-device reference, FCB table, TOC fields, removable/audio flags, block factor, and media-change count.
- `CdUpdateVcbFromVolDescriptor()` completes mount-time VCB initialization from an ISO/Joliet volume descriptor or creates pseudo structures for audio disks.
- `CdDeleteVcb()` frees VCB-owned auxiliary state, resources, TOC, notify state, target reference, VPBs, and deletes the containing volume device object.
- `CdCreateFcb()` looks up or allocates an FCB by file ID and node type, initializes common fields, MCB, nonpaged FCB, advanced header, and oplock state for data FCBs.
- `CdInitializeFcbFromPathEntry()` initializes a directory/index FCB from a path-table entry.
- `CdInitializeFcbFromFileContext()` initializes a file/data FCB from one or more directory extents and loads its allocation map.
- `CdCreateCcb()` and `CdDeleteCcb()` allocate/free per-open context structures.
- `CdCreateFileLock()` lazily attaches an FsRtl file-lock object to a data FCB.
- `CdCreateIrpContext()`, `CdCleanupIrpContext()`, and `CdInitializeStackIrpContext()` manage request contexts and the private lookaside list.
- `CdTeardownStructures()` walks from an FCB toward the root, removing unreferenced FCBs from parent queues, prefix trees, and the FCB table.
- `CdLookupFcbTable()` and `CdGetNextFcb()` access the generic-table index by `FILE_ID`.
- `CdProcessToc()` reads and normalizes CD-ROM TOC data, with fallback from `IOCTL_CDROM_READ_TOC_EX` to `IOCTL_CDROM_READ_TOC`.
- `CdTocSerial()` computes an audio-disk serial number from TOC track addresses.

Core mechanics:
- A generic table maps `FILE_ID` values to FCBs using `CdFcbTableCompare()`.
- Mount initialization creates internal stream FCBs for the path table, root directory, and volume DASD file.
- ISO/Joliet mounts reject block sizes other than `SECTOR_SIZE`.
- The path-table FCB is backed by the on-disk path-table extent; the root directory FCB is initialized from a pseudo path entry built from the root dirent.
- The DASD FCB maps the full logical volume and is marked read-only.
- Audio-only disks are exposed through pseudo ISO-like structures: a synthetic path table, root directory entries for tracks, an audio label, and a TOC-derived serial number.
- File FCB initialization walks multi-extent dirents until the final extent and adds each allocation into the FCB MCB.
- Teardown deletes internal stream file objects for index/path-table FCBs once user references reach zero, then removes unreferenced FCBs bottom-up.

Important invariants:
- VCB initialization keeps residual references so the VCB cannot vanish during mount/error cleanup.
- Internal FCBs hold VCB references until dismount removes them.
- FCBs must leave the FCB table before deletion if `FCB_STATE_IN_FCB_TABLE` is set.
- Directory/index FCBs must have empty child queues and no stream file object when deleted.
- `CdTeardownStructures()` uses a top-level teardown flag to avoid recursive teardown.
- `CdCleanupIrpContext()` distinguishes normal deletion, posting, retry, stack contexts, allocated I/O contexts, and lookaside reuse.

Filesystem relevance:
- This is the structural backbone for CDFS mount, open, close, cached I/O, directory hierarchy, and dismount behavior.
- It connects on-disk ISO/Joliet descriptors and CD-ROM TOC data to the runtime VCB/FCB model.

Notable risks:
- Mount and dismount paths depend on precise VCB, VPB, internal-stream, and target-device reference accounting.
- The audio-disk pseudo filesystem path has separate size/label/serial behavior and does not permit raw reads through the zero-sized DASD FCB.
- `CdProcessToc()` mutates the returned TOC for mixed CD+ media by hiding the data track after lead-in audio.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/strucsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/verfysup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/verfysup.c

Implements volume verification, dismount checks, VCB validation, FCB-operation validation, and VCB dismount initiation for CDFS.

Key entry points:
- `CdPerformVerify()` calls `IoVerifyVolume()`, reconciles the result with the current VCB condition, may trigger dismount, reparses successful top-level creates, or posts the original IRP for retry.
- `CdCheckForDismount()` decides whether to start dismount or delete a VCB when references drop to residual values.
- `CdMarkDevForVerifyIfVcbMounted()` marks the real device for verification only if the VCB's VPB is still mounted on that device.
- `CdVerifyVcb()` checks invalid/dismount state, removable-media change state, verify-required state, and raises appropriate verify/wrong-volume/file-invalid statuses.
- `CdVerifyFcbOperation()` validates per-FCB operations, including cleaned-up file objects, invalid/dismount state, real-device verify state, and wrong-volume handling.
- `CdDismountVcb()` transitions a VCB into dismount-in-progress, drops internal FCB references, purges the volume, drains close queues, swaps or clears VPBs, and deletes the VCB if final references are gone.

Core mechanics:
- Verify skips recursive mount/verify FSCTL deadlocks by posting mount/verify requests instead of calling `IoVerifyVolume()`.
- Removable media verification uses `IOCTL_CDROM_CHECK_VERIFY`, media change count comparison, raw-device status, and device verify flags.
- Create requests against unmounted/dismounting volumes can be forced through verify so name opens are rerouted to the currently mounted volume.
- Dismount first tears down internal references, purges cache/sections, drains closes, then handles VPB ownership under the VPB spin lock.
- If outstanding references remain, `CdDismountVcb()` swaps in the preallocated `SwapVpb` so the real device can accept a new mount.

Important invariants:
- `CdCheckForDismount()` requires exclusive global CDFS data ownership.
- VCB deletion only occurs after both VCB references and VPB references reach the expected final counts.
- Dismount may leave the VCB alive if user/file/VPB references remain.
- Fast I/O validation returns `FALSE` instead of raising when no IRP context is present.

Filesystem relevance:
- This file controls media-change detection, wrong-volume handling, create reparsing after remount, forced dismount, and safe volume deletion.

Notable risks:
- VPB swapping and final-reference logic are delicate and depend on holding the correct locks.
- Media-change count is intentionally updated only after an actual verify completes, not when a possible change is detected.
- Operations on cleaned-up file objects are mostly rejected, with narrow exceptions for paging I/O, close, query information, and MDL read completion.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/verfysup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/volinfo.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/volinfo.c

Implements `IRP_MJ_QUERY_VOLUME_INFORMATION` support for CDFS.

Key entry points:
- `CdCommonQueryVolInfo()` decodes the file object, acquires the VCB shared, verifies the VCB, dispatches by filesystem information class, records bytes returned, and completes the IRP.
- `CdQueryFsVolumeInfo()` returns creation time, serial number, object-support flag, and volume label.
- `CdQueryFsSizeInfo()` returns total allocation units, zero available units, one sector per allocation unit, and sector size.
- `CdQueryFsDeviceInfo()` returns target-device characteristics and device type.
- `CdQueryFsAttributeInfo()` returns filesystem attributes, component-name limits, and the filesystem name `CDFS`.
- `CdQueryFsSectorSizeInfo()` returns sector-size information through `FsRtlGetSectorSizeInformation()` when available for the build target.

Core mechanics:
- ReactOS zeroes the caller's system buffer before filling query output.
- Volume labels are copied partially with `STATUS_BUFFER_OVERFLOW` if the buffer is too small.
- File system attributes always include case-sensitive search, read-only volume, and open-by-file-ID support.
- Joliet volumes add `FILE_UNICODE_ON_DISK` and use a 110-character maximum component length; non-Joliet uses 221.
- Size information derives total allocation units from the volume DASD FCB allocation size.

Important invariants:
- Query volume rejects unopened file objects.
- All query classes run after `CdVerifyVcb()`.
- Returned `IoStatus.Information` is computed from the original length minus remaining length.

Filesystem relevance:
- Exposes CDFS volume metadata to user mode and system callers.
- Reports CDFS as read-only and distinguishes Joliet Unicode-on-disk capability.

Notable risks:
- Helper routines subtract fixed structure sizes from `Length`; callers rely on the I/O manager and dispatch path to provide adequate fixed-size buffers.
- `FileFsSectorSizeInformation` is compiled only for NTDDI targets that define the class.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/volinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/workque.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/workque.c

Implements request posting and overflow work-queue handling for CDFS FSD-to-FSP transitions and oplock completion.

Key entry points:
- `CdFsdPostRequest()` prepares an IRP for pending processing and queues it to the FSP work queue.
- `CdPrePostIrp()` locks user buffers where needed, performs create-path teardown cleanup, cleans the IRP context for posting, and marks the IRP pending.
- `CdOplockComplete()` resumes oplock-blocked IRPs by queueing successful ones or completing failed ones.
- `CdAddToWorkque()` sends work to an executive worker thread or a per-volume overflow queue.

Core mechanics:
- Posted creates may carry a `TeardownFcb`; this is torn down before the request is posted so create cleanup will not release stale state.
- Read, write, and query-directory requests lock the user buffer before returning pending, unless the operation is MDL-based.
- `IRP_CONTEXT_FLAG_MORE_PROCESSING` keeps the IRP context alive across posting while clearing per-thread/top-level state.
- Per-volume throttling sends more than two active posted requests to an overflow queue protected by `OverflowQueueSpinLock`.
- Work items are queued to `CriticalWorkQueue` and dispatch through `CdFspDispatch`.

Important invariants:
- User buffers must be locked before `STATUS_PENDING` returns to the caller.
- Posted request accounting is per volume device object when a file object is present.
- Oplock completion may run outside the original dispatch context and must either queue or complete the IRP.

Filesystem relevance:
- Provides the async/blocking escape path for operations that cannot complete in the current FSD thread.
- Integrates oplock waits with normal CDFS worker-thread dispatch.

Notable risks:
- Overflow queue draining is handled elsewhere; this file only enqueues overflow work.
- Read and write buffer locking both reference `IrpSp->Parameters.Read.Length`; this relies on the read/write parameter union layout.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/workque.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/write.c -->
# File Research: sources/windows/reactos/drivers/filesystems/cdfs/write.c

Implements the limited CDFS write path. CDFS is read-only for files, so writes are only accepted for volume/DASD handles.

Key entry points:
- `CdCommonWrite()` validates a write request, permits only `UserVolumeOpen`, verifies the volume unless dismount-on-close is set, bounds/alignment-adjusts the request, prepares a `CD_IO_CONTEXT`, marks the file object modified, and dispatches to `CdVolumeDasdWrite()`.

Core mechanics:
- Zero-length writes complete successfully.
- Non-volume writes fail with `STATUS_INVALID_DEVICE_REQUEST`.
- Writes beyond EOF return `STATUS_END_OF_FILE`; writes crossing EOF are truncated unless extended DASD I/O is allowed.
- Byte counts are block-aligned, but unaligned writes require a waitable path; otherwise the request is posted with `STATUS_CANT_WAIT`.
- Pending noncached writes hold the file resource through the async I/O context.
- Successful synchronous writes update `CurrentByteOffset`.
- If alignment caused extra bytes to be touched, the extra user-buffer range is zeroed and reported bytes are reduced to the logical byte count.

Important invariants:
- CDFS does not write regular file data; all writes are raw volume writes.
- `FO_FILE_MODIFIED` is set conservatively so close will trigger verification.
- User-induced errors are raised for normal hard-error handling; other failures are normalized to unexpected I/O error.

Filesystem relevance:
- Supports raw DASD access scenarios such as volume-management or dismount workflows while preserving normal read-only filesystem semantics.

Notable risks:
- The write path shares noncached alignment/posting patterns with read, so buffer validity and sector alignment are critical.
- Raw volume writes can invalidate assumptions about mounted media; the code intentionally marks the handle modified to force later verify behavior.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/cdfs/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/CMakeLists.txt

Build definition for the ReactOS `ext2fs` kernel-mode filesystem driver.

Key behavior:
- Adds include directories for ReactOS driver headers and the local `inc` directory.
- Builds `ext2fs` as a module from ext2/ext3/ext4, JBD, NLS, core dispatch, cache, I/O, PnP, shutdown, read, write, and `inc/ext2fs.h` sources.
- Defines `_CRT_NON_CONFORMING_SWPRINTFS` on the target.
- Suppresses compiler-specific warnings for MSVC, GCC, and Clang.
- Links `memcmp` and `${PSEH_LIB}`.
- Adds global definitions `__KERNEL__`, `_CRT_NO_POSIX_ERROR_CODES`, and `_CRT_DECLARE_NONSTDC_NAMES=1`.
- Sets the module type to `kernelmodedriver`, imports `ntoskrnl` and `hal`, and uses `inc/ext2fs.h` as the precompiled header.
- Installs the driver into `reactos/system32/drivers` and registers `ext2fs_reg.inf`.

Build invariants:
- The driver vendors or directly builds many Linux-like compatibility sources and NLS tables into one kernel driver target.
- GNU and Clang warning suppressions indicate the code intentionally relies on pointer-sign conversions, unused functions/variables, packed-member addresses, and other compatibility patterns.

Filesystem/build relevance:
- This is the complete ReactOS build recipe for the bundled Ext2Fsd-derived ext2/ext3/ext4 filesystem driver.

Notable risks:
- `add_definitions()` applies the listed definitions directory-wide rather than only to `ext2fs`.
- The large static source list means adding/removing Ext2Fsd components requires manual CMake maintenance.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/page.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/page.h

Empty compatibility header.

Key behavior:
- Contains no declarations, macros, includes, comments, or guards.

Filesystem/build relevance:
- Exists to satisfy Linux-style include paths that expect `asm/page.h` while building the ReactOS ext2 filesystem driver.

Notable risks:
- Any source expecting Linux page macros from this header must receive them elsewhere or avoid using them in this port.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/page.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/semaphore.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/semaphore.h

Empty compatibility header.

Key behavior:
- Contains no declarations, macros, includes, comments, or guards.

Filesystem/build relevance:
- Exists to satisfy Linux-style include paths that expect `asm/semaphore.h` while building the ReactOS ext2 filesystem driver.

Notable risks:
- Any Linux semaphore abstractions needed by this port must be provided by other compatibility headers or source-local definitions.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/semaphore.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/uaccess.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/uaccess.h

Empty compatibility header.

Key behavior:
- Contains no declarations, macros, includes, comments, or guards.

Filesystem/build relevance:
- Exists to satisfy Linux-style include paths that expect `asm/uaccess.h` while building the ReactOS ext2 filesystem driver.

Notable risks:
- Any source expecting Linux user-access helpers from this header must be adapted elsewhere in the ReactOS ext2 compatibility layer.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/asm/uaccess.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/common.h -->
# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/common.h

Defines public/common Ext2Fsd IOCTL payloads, performance-statistics layouts, volume-property structures, and mount-point management structures.

Key contents:
- Global application IOCTLs: `IOCTL_APP_VOLUME_PROPERTY`, `IOCTL_APP_QUERY_PERFSTAT`, and `IOCTL_APP_MOUNT_POINT`.
- Performance-statistic slot IDs for IRP contexts, VCBs, FCBs, CCBs, MCBs, extents, read/write contexts, VPBs, names, directory entries, disk buffers, inodes, dentries, and buffer heads.
- `EXT2_STAT_ARRAY_V1` and `EXT2_STAT_ARRAY_V2` unions for named and indexed memory/stat counters.
- `EXT2_PERF_STATISTICS_V1` and `EXT2_PERF_STATISTICS_V2` layouts, including per-major-function processed/current IRP counts and allocation statistics.
- Volume-property command constants for querying/setting versions and property generations.
- `EXT2_VOLUME_PROPERTY`, `EXT2_VOLUME_PROPERTY2`, and `EXT2_VOLUME_PROPERTY3`, covering read-only/ext2/ext3 flags, codepage, UUID, drive letter, bitmap checks, hiding patterns, automount, and user/group IDs.
- `EXT2_VOLUME_PROPERTY_VERSION` for version/time/date reporting.
- `EXT2_QUERY_PERFSTAT` and size macros for V1/V2 perf-stat queries.
- `EXT2_MOUNT_POINT` plus add/delete DOS symlink commands for mount-point management.

Important invariants:
- Magic constants identify expected payload types: performance statistics, volume properties, and mount-point requests.
- V2 performance stats expand the slot array from `0x10` to `0x30` and add inode/name-entry/buffer-head counters.
- ReactOS uses `1ULL` for 64-bit `EXT2_VPROP3_*` flags; non-ReactOS uses MSVC-style `1ui64`.
- C++ builds model property generations through inheritance-like struct syntax, while C builds embed the previous structure as an anonymous field.

Filesystem relevance:
- This header defines the user/kernel control ABI for ReactOS ext2 volume properties, statistics, and drive-letter/mount-point operations.
- It is shared infrastructure for Ext2Fsd management tools and the kernel driver.

Notable risks:
- Several comments contain legacy typos, but the ABI field order and sizes are the important compatibility contract.
- Anonymous embedded struct usage and C++ inheritance-style declarations are compiler-sensitive.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/ext2/inc/common.h -->