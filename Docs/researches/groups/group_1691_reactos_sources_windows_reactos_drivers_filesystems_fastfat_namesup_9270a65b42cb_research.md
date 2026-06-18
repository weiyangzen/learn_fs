# Group Research: group_1691_reactos_sources_windows_reactos_drivers_filesystems_fastfat_namesup_9270a65b42cb

Scope: `Docs/research_subset_a.md` includes `sources/windows/reactos`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/namesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/namesup.c

This file implements FastFAT name conversion, matching, case restoration, long-name lookup, full-path construction, and short-name selection.

Key responsibilities:
- Match upcased OEM names against wildcard expressions with `FsRtlIsDbcsInExpression`.
- Convert between user-visible OEM names and FAT on-disk 8.3 directory-entry format.
- Restore lowercase display case from FAT `NtByte` case bits in Chicago compatibility mode.
- Locate and synthesize Unicode names for existing FCBs, using LFN entries when present and short-name conversion otherwise.
- Lazily build `Fcb->FullFileName` by walking parent DCBs and reusing ancestor full names when available.
- Convert Unicode names to upcased OEM names, allocating dynamically on buffer overflow and treating unmappable characters as zero-length OEM names.
- Decide whether create paths can use a supplied 8.3 name directly or must generate a collision-free short name with `RtlGenerate8dot3Name`.
- Decide whether a long filename entry is required based on mixed case, spaces, extended characters, and code-page invariance.
- Restore Unicode 8.3 case segments from separate base-name and extension lowercase flags.

Important functions:
- `FatIsNameInExpression`: wildcard matching for already-upcased OEM names.
- `FatStringTo8dot3`: packs a legal short OEM string into the 11-byte FAT dirent name field, including the special leading `0xe5` to `0x05` translation.
- `Fat8dot3ToString`: expands a FAT 8.3 dirent name into an OEM string, trims padding, adds the dot when needed, restores `0xe5`, and optionally lowercases base/extension from case bits.
- `FatGetUnicodeNameFromFcb`: rereads the directory entry for an FCB and returns the exact Unicode LFN or a Unicode-converted short name.
- `FatSetFullFileNameInFcb`: constructs a full path from parent components and caches it in the FCB.
- `FatUnicodeToUpcaseOem`: wrapper around `RtlUpcaseUnicodeStringToCountedOemString` with retry allocation and FAT-specific error handling.
- `FatSelectNames`: chooses the short name and whether an LFN must be created, trying a suggested short name before generated names.
- `FatEvaluateNameCase`: calculates lowercase case-bit eligibility and whether an LFN is required.
- `FatSpaceInName`: detects spaces that force short-name generation.
- `FatUnicodeRestoreShortNameCase`: downcases base and/or extension portions of a Unicode short name.

Notable behavior and risks:
- Name handling depends on global compatibility flags `FatData.ChicagoMode` and `FatData.CodePageInvariant`.
- LFN reconstruction validates that the located dirent offset matches the FCB’s expected dirent; mismatches raise `STATUS_FILE_INVALID`.
- `FatSetFullFileNameInFcb` allocates a temporary max-LFN buffer and frees partially built full names on abnormal unwind.
- Short-name generation loops until `FatLocateSimpleOemDirent` proves a candidate does not exist in the parent directory.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/namesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/nodetype.h -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/nodetype.h

This header defines FastFAT node type codes, bugcheck identifiers, ASCII control constants, and pool allocation tags.

Key responsibilities:
- Assign stable `NODE_TYPE_CODE` values to core in-memory records:
  - data header
  - VCB
  - FCB
  - DCB
  - root DCB
  - CCB
  - IRP context
- Provide the `NodeType(Ptr)` macro used throughout the driver to validate object identity.
- Define per-source-file bugcheck IDs used by `FatBugCheck`.
- Define `FatBugCheck(A,B,C)` as a wrapper around `KeBugCheckEx(FAT_FILE_SYSTEM, ...)`.
- Provide `UCHAR_*` constants for ASCII/control characters used in FAT name handling.
- Define pool tags for FastFAT allocations: FCBs, CCBs, ERESOURCEs, IRP contexts, BCBs, dirents, bitmaps, EA data, close contexts, I/O contexts, VPBs, dynamic name buffers, and related buffers.

Important constants:
- `FAT_NTC_VCB`, `FAT_NTC_FCB`, `FAT_NTC_DCB`, `FAT_NTC_ROOT_DCB`, `FAT_NTC_CCB`, `FAT_NTC_IRP_CONTEXT`.
- `FAT_BUG_CHECK_NAMESUP`, `FAT_BUG_CHECK_PNP`, `FAT_BUG_CHECK_READ`, `FAT_BUG_CHECK_RESRCSUP`, `FAT_BUG_CHECK_SHUTDOWN`, `FAT_BUG_CHECK_SPLAYSUP`, `FAT_BUG_CHECK_STRUCSUP`, `FAT_BUG_CHECK_TIMESUP`.
- Allocation tags such as `TAG_FCB`, `TAG_CCB`, `TAG_FCB_NONPAGED`, `TAG_ERESOURCE`, `TAG_IRP_CONTEXT`, `TAG_FILENAME_BUFFER`, `TAG_FAT_IO_CONTEXT`, and `TAG_DYNAMIC_NAME_BUFFER`.

Notable behavior and risks:
- The node-type convention assumes the first field of major structures is a `NODE_TYPE_CODE`.
- The bugcheck macro combines each file’s `BugCheckFileId` with `__LINE__`, making source line numbers part of crash diagnostics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/nodetype.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/pnp.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/pnp.c

This file implements FastFAT Plug and Play dispatch for mounted volume device objects.

Key responsibilities:
- Dispatch `IRP_MJ_PNP` through `FatFsdPnp` and `FatCommonPnp`.
- Validate that the target device object is a FastFAT volume device with a VCB.
- Serialize PnP against teardown with the global resource.
- Handle query-remove, remove, surprise-remove, and cancel-remove minor functions.
- Pass unhandled PnP IRPs down to the storage stack.
- Coordinate volume locking, flushing, VPB reference protection, dismount initiation, and lower-driver completion waiting.

Important functions:
- `FatFsdPnp`: FSD wrapper that enters the filesystem, establishes top-level IRP state, creates an IRP context, and routes exceptions through `FatProcessException`.
- `FatCommonPnp`: forces wait semantics, finds the VCB from the device object, takes the global lock, validates object shape, and dispatches by minor function.
- `FatPnpAdjustVpbRefCount`: adjusts VPB reference counts under the VPB spin lock.
- `FatPnpQueryRemove`: locks the volume, flushes and cleans it, sends query-remove down synchronously, then initiates forced dismount on success.
- `FatPnpRemove`: unlocks any volume lock, passes remove down, flushes/cleans without flushing, and forces dismount.
- `FatPnpSurpriseRemove`: passes surprise-remove down, cleans local state without flushing, and forces dismount.
- `FatPnpCancelRemove`: unlocks a previously query-locked volume and forwards the cancel-remove IRP.
- `FatPnpCompletionRoutine`: signals a caller event and returns `STATUS_MORE_PROCESSING_REQUIRED`.

Important interactions:
- Uses `FatAcquireExclusiveGlobal`, `FatAcquireExclusiveVcb`, `FatReleaseGlobal`, and `FatReleaseVcb` for teardown ordering.
- Uses `FatLockVolumeInternal` and `FatUnlockVolumeInternal` around query/cancel remove.
- Uses `FatFlushAndCleanVolume` before dismount where appropriate.
- Uses `FatCheckForDismount(..., TRUE)` to disconnect or delete the VCB.
- Synchronous lower-driver calls copy the current stack location, install `FatPnpCompletionRoutine`, call `IoCallDriver`, and wait if pending.

Notable behavior and risks:
- Query-remove temporarily increments the VPB reference count while resources are dropped and reacquired in the correct order.
- Remove and surprise-remove both continue local dismount processing even when the lower storage stack is already gone.
- Cancel-remove may arrive even if FAT did not see or complete the original query, so the unlock is intentionally benign.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/read.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/read.c

This file implements FastFAT `IRP_MJ_READ` handling for user files, directories, EA files, volume/DASD handles, virtual volume file reads, paging-file reads, cached reads, noncached reads, MDL reads, and low-stack overflow recovery.

Key responsibilities:
- Dispatch reads through `FatFsdRead` and `FatCommonRead`.
- Fast-path paging-file reads directly to `FatPagingFileIo`.
- Post low-stack reads to filesystem stack-overflow workers.
- Decode file-object open type and route read behavior accordingly.
- Enforce EOF, valid-data-length, sector-alignment, locking, oplock, cache, and DASD rules.
- Initialize `FAT_IO_CONTEXT` for noncached I/O.
- Maintain per-processor read statistics.
- Update synchronous file positions and mark successful nonpaging reads for access-time update.

Important functions:
- `FatFsdRead`: top-level read dispatch, including paging-file fast path, MDL-complete handling, low-stack detection, IRP context creation, and exception processing.
- `FatPostStackOverflowRead`: preacquires the resource needed by the read path, posts the read to `FsRtlPostStackOverflow`, and waits until the worker has started/completed the protected section.
- `FatStackOverflowRead`: runs `FatCommonRead` with wait semantics on a safer stack, including verify-thread substitution when needed.
- `FatCommonRead`: main read engine.
- `FatOverflowPagingFileRead`: stack-overflow helper for paging-file reads.

Main read flows:
- Zero-length reads complete successfully with zero information.
- `UserVolumeOpen` and `VirtualVolumeFile` reads become noncached LBO reads through `FatSingleAsync`.
- DASD reads verify the VCB unless complete-dismount or format-unit flags allow bypass, flush the volume once per CCB, trim to volume size unless extended DASD I/O is allowed, and lock the user buffer.
- Normal user-file reads acquire the FCB or paging I/O resource, check oplocks and byte-range locks, trim to file size, then choose cached or noncached transfer.
- Noncached user-file reads zero data beyond valid data length, reduce physical I/O to VDL, round physical reads to sector boundaries, and use special handling for unaligned reads.
- Cached user-file reads lazily initialize the cache map, verify allocation size, use `CcCopyRead`/`CcCopyReadEx`, or `CcMdlRead` for MDL reads.
- Directory and EA file reads are expected to be noncached paging I/O, sector aligned, and within allocation size.
- User directory reads fail with `STATUS_INVALID_PARAMETER`.

Important interactions:
- Uses `FatAcquireSharedFcb`, `FatAcquireSharedFcbWaitForEx`, and paging I/O resources depending on read type.
- Uses `FsRtlCheckOplock` and `FsRtlCheckLockForReadAccess` for nonpaging file reads.
- Uses `CcFlushCache` before noncached reads when a data section exists, avoiding stale cached data.
- Uses `FatNonCachedIo`, `FatNonCachedNonAlignedRead`, `FatSingleAsync`, and `FatWaitSync` for physical I/O.
- Uses `FatMapUserBuffer`, `FatLockUserBuffer`, and guarded zeroing for user buffers.

Notable behavior and risks:
- Reads with nonzero high offset parts on regular files return EOF because FAT file sizes are 32-bit.
- Noncached reads that extend past VDL may partially zero the caller buffer while only physically reading valid sectors.
- Async noncached reads may detach the IRP context and return `STATUS_PENDING`.
- Stack-allocated `FAT_IO_CONTEXT` cleanup must free any zero MDL before returning on exceptional paths.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/resrcsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/resrcsup.c

This file implements FastFAT resource acquisition helpers and cache-manager/filter synchronization callbacks.

Key responsibilities:
- Acquire VCB and FCB resources in shared or exclusive mode with wait/no-wait semantics.
- Verify operation legality immediately after resource acquisition and release on abnormal unwind.
- Coordinate normal FCB resources with outstanding asynchronous noncached writes.
- Provide cache-manager callbacks for lazy writer, read-ahead, Cc flush, and no-op cache maps.
- Provide the filesystem-filter callback used when memory manager creates or synchronizes sections.

Important functions:
- `FatAcquireExclusiveVcb_Real`: exclusively acquires `Vcb->Resource`, optionally skipping legality checks.
- `FatAcquireSharedVcb`: shared VCB acquisition with legality verification.
- `FatAcquireExclusiveFcb`: exclusive FCB acquisition; waits for outstanding async writes when needed, then retries.
- `FatAcquireSharedFcb`: shared FCB acquisition with similar async-write coordination.
- `FatAcquireSharedFcbWaitForEx`: no-wait shared acquisition that gives exclusive waiters priority for noncached async I/O.
- `FatAcquireFcbForLazyWrite` / `FatReleaseFcbFromLazyWrite`: cache-manager lazy-writer acquire/release.
- `FatAcquireFcbForReadAhead` / `FatReleaseFcbFromReadAhead`: cache-manager read-ahead acquire/release.
- `FatAcquireForCcFlush` / `FatReleaseForCcFlush`: Fast I/O Cc flush preacquire/release callbacks.
- `FatNoOpAcquire` / `FatNoOpRelease`: callbacks for cache maps that do not need real locking.
- `FatFilterCallbackAcquireForCreateSection`: FS filter callback that acquires main exclusively and reports whether writers exist.

Important interactions:
- Uses `ExAcquireResource*Lite`, `ExAcquireSharedWaitForExclusive`, and `ExReleaseResourceLite`.
- Sets `IoSetTopLevelIrp(FSRTL_CACHE_TOP_LEVEL_IRP)` in cache-manager callbacks to prevent recursive verification/hard-error behavior.
- Lazy writer normally acquires paging I/O resource, but uses the main resource for the EA file.
- Cc flush respects FAT lock ordering: main -> BCB -> paging I/O, and deliberately avoids taking main for directory/EA cases where it would invert ordering.
- Section synchronization returns `STATUS_FILE_LOCKED_WITH_ONLY_READERS` or `STATUS_FILE_LOCKED_WITH_WRITERS` for create-section sync.

Notable behavior and risks:
- FCB acquisition can loop while outstanding async writes drain, preventing conflicting cached/noncached operations from racing.
- Cache-manager callbacks assume they are called in safe system/APC-disabled contexts.
- `FatFilterCallbackAcquireForCreateSection` relies on the default FSRTL release path; changing acquired resources would require a paired custom release.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/resrcsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/shutdown.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/shutdown.c

This file implements FastFAT filesystem shutdown handling.

Key responsibilities:
- Dispatch `IRP_MJ_SHUTDOWN` through `FatFsdShutdown`.
- Serialize shutdown with the global filesystem resource.
- Flush and clean every mounted FAT volume that has not already been shut down.
- Send shutdown IRPs to underlying target devices.
- Mark VCBs as shut down and try to dismount them.
- Unregister and delete the FastFAT disk and CD-ROM filesystem device objects.

Important functions:
- `FatFsdShutdown`: FSD wrapper that enters the filesystem, creates a waitable IRP context, calls `FatCommonShutdown`, and handles exceptions.
- `FatCommonShutdown`: core shutdown routine.

Shutdown flow:
1. Set `IRP_CONTEXT_FLAG_DISABLE_POPUPS` and `IRP_CONTEXT_FLAG_WRITE_THROUGH`.
2. Set `FatData.ShutdownStarted = TRUE`.
3. Acquire the global resource exclusively.
4. Iterate `FatData.VcbQueue`.
5. Skip already-shutdown or non-good VCBs.
6. Acquire each volume exclusively.
7. Flush the volume and mark it clean when not mounted dirty.
8. Build and send a synchronous `IRP_MJ_SHUTDOWN` to the target device.
9. Set `VCB_STATE_FLAG_SHUTDOWN`.
10. Call `FatCheckForDismount`.
11. Release the volume if it survived.
12. Release global, unregister filesystems, delete filesystem device objects, and complete the original IRP.

Notable behavior and risks:
- Flush exceptions are swallowed after resetting exception state, because the lower storage stack still needs shutdown notification.
- The volume file cache is purged before marking the volume clean to avoid stale BPB state.
- The routine unregisters and deletes global filesystem device objects from the shutdown path.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/splaysup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/splaysup.c

This file implements FastFAT’s in-memory filename splay-tree support for cached FCB lookup.

Key responsibilities:
- Insert short and long name nodes into per-directory splay trees.
- Remove all name nodes associated with an FCB.
- Find an FCB by OEM or Unicode name tree lookup and splay the found node to the root.
- Compare name byte strings deterministically.

Important functions:
- `FatInsertName`: inserts a `FILE_NAME_NODE` into a splay tree rooted at a parent DCB field.
- `FatRemoveNames`: removes the short name and any OEM/Unicode long names from the parent DCB’s trees, freeing allocated long-name strings.
- `FatFindFcb`: searches a name tree, splays a match to root, and optionally reports whether the matched node was a DOS/short-name entry.
- `FatCompareNames`: case-sensitive byte comparison used for both OEM and Unicode tree ordering.

Important interactions:
- Parent DCBs maintain separate roots for OEM and Unicode name trees.
- `FatConstructNamesInFcb` inserts names through this file, while deletion/rename paths remove them through `FatRemoveNames`.
- `FatFindFcb` updates `*RootNode` with `RtlSplay(Links)` to improve locality for repeated lookups.

Notable behavior and risks:
- Duplicate insertion normally bugchecks, but the code handles stale bad FCBs caused by removable-media changes: it marks the old FCB bad, removes its names, and restarts insertion.
- `FatRemoveNames` tolerates FCBs that no longer have tree entries, because rename and stale-branch cleanup can revisit partially torn-down children.
- `FatCompareNames` is byte-order deterministic rather than locale-aware; callers must supply appropriately normalized names.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/splaysup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/strucsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/strucsup.c

This file implements FastFAT in-memory structure allocation, initialization, teardown, traversal, dismount, name-node construction, directory free-dirent bitmap management, close-context pooling, dynamic string buffers, and CD data-track probing.

Key responsibilities:
- Allocate/free CCBs, FCBs, nonpaged FCB extensions, ERESOURCEs, and IRP contexts.
- Initialize VCBs during mount, including target-device references, hotplug/deferred-flush flags, stream file objects, cache maps, MCBs, VPB swap storage, statistics, close queues, and advanced FCB headers.
- Tear down and delete VCBs, including internal stream files, EA file, root DCB tree, notification sync, allocation support, MCBs, timers, tunnel cache, target-device references, and VPBs.
- Create root DCBs, regular FCBs, and directory DCBs from FAT dirents.
- Delete FCB/DCB/root DCB records and their locks, oplocks, file locks, names, MCBs, directory bitmaps, per-stream contexts, and child links.
- Create/delete CCBs and their query-template strings.
- Create/delete IRP contexts and attached `FAT_IO_CONTEXT` state.
- Enumerate FCB trees bottom-up or top-down for lock ordering and teardown.
- Swap VPBs and check whether a volume can be dismounted/deleted.
- Construct short/long name nodes in FCBs and insert them into parent splay trees.
- Grow free-dirent bitmaps as directory allocation grows.
- Check whether all user handles are closed.
- Preallocate and consume close contexts from the global SList.
- Manage reusable string buffers safely across stack/pool buffers.
- Read CD-ROM TOC data to avoid mounting audio-only media as FAT.

Important functions:
- `FatInitializeVcb`: mount-time VCB initialization with extensive abnormal-unwind cleanup.
- `FatTearDownVcb`: closes internal stream/cache objects and marks the VCB bad.
- `FatDeleteVcb`: removes a VCB from global state and frees all subordinate structures.
- `FatCreateRootDcb`: builds the root directory object, with FAT12/16 fixed-root mapping or FAT32 cluster-chain lookup.
- `FatCreateFcb`: builds a file FCB, including timestamps, allocation hints, file lock, oplock, MCB, resources, and names.
- `FatCreateDcb`: builds a directory DCB, including child queue, bitmap state, resources, MCB, oplock, and names.
- `FatDeleteFcb`: deletes file or directory objects once open count reaches zero.
- `FatCreateCcb`, `FatDeallocateCcbStrings`, `FatDeleteCcb`: CCB lifetime helpers.
- `FatCreateIrpContext`, `FatDeleteIrpContext_Real`: IRP-context lifetime helpers.
- `FatGetNextFcbBottomUp`, `FatGetNextFcbTopDown`: tree traversal helpers for lock acquisition and teardown.
- `FatSwapVpb`: replaces the mounted VPB with the saved spare VPB during forced disconnect.
- `FatCheckForDismount`: checks VPB/open counts, tears down internal opens, drains closes, deletes the volume device when possible, or swaps VPB on force.
- `FatConstructNamesInFcb`: builds short and long name nodes, chooses OEM vs Unicode LFN prefix storage, and inserts names into splay trees.
- `FatCheckFreeDirentBitmap`: grows a directory’s free-dirent bitmap under the directory-file mutex.
- `FatIsHandleCountZero`: walks the tree to determine whether user handle counts are gone.
- `FatAllocateCloseContext`, `FatPreallocateCloseContext`: close-context SList helpers.
- `FatEnsureStringBufferEnough`, `FatFreeStringBuffer`: dynamic string buffer helpers.
- `FatScanForDataTrack`: reads CD TOC and returns true only for a single data track or PD-media special failures.

Notable behavior and risks:
- VCB initialization has many partial-allocation unwind paths; leaked close context balancing is handled specially when stream file creation fails.
- Root DCB allocation uses nonpaged pool, while ordinary FCB/DCB allocation uses paged pool except for paging files.
- Directory DCBs are inserted at the head and file FCBs at the tail so child directories precede files for bottom-up lock-order traversal.
- `FatCheckForDismount` depends on VPB reference counts matching residual/internal opens and may either delete the volume device or only disconnect it.
- Unicode LFN prefix storage is conservative: extended-character LFNs are generally kept in Unicode to avoid OEM best-fit collisions.
- `FatFreeStringBuffer` detects stack-backed buffers via `IoGetStackLimits` and only frees non-stack buffers.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/strucsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/timesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/timesup.c

This file implements conversion between NT system time and FAT date/time formats.

Key responsibilities:
- Convert NT `LARGE_INTEGER` timestamps to FAT date/time stamps.
- Convert FAT dates and FAT date/time stamps back to NT time.
- Preserve FAT’s local-time semantics by converting between system and local time.
- Handle FAT’s 2-second timestamp granularity and optional 10-millisecond creation-time field.
- Return the current time in FAT timestamp format.

Important functions:
- `FatNtTimeToFatTime`: converts NT GMT time to local FAT date/time, optionally rounding up to the next FAT 2-second boundary. It can also return the 10-millisecond remainder for creation times.
- `FatFatDateToNtTime`: converts a FAT date-only value to NT GMT midnight local date.
- `FatFatTimeToNtTime`: converts a full FAT timestamp plus 10-millisecond creation subfield to NT GMT time.
- `FatGetCurrentFatTime`: queries current system time, converts to local time, rounds up to FAT 2-second granularity, and returns a FAT timestamp.

Notable behavior and risks:
- FAT timestamp range is limited to 1980 through 2107; `FatNtTimeToFatTime` returns false outside that range.
- `FatNtTimeToFatTime` mutates the input `NtTime` to the rounded/truncated representable value.
- Invalid FAT date/time fields convert to zero NT time.
- Seconds greater than 59 after applying the 10-millisecond field are truncated to zero.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/timesup.c -->