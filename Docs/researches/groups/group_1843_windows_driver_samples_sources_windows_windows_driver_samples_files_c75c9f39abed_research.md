# Group Research: group_1843_windows_driver_samples_sources_windows_windows_driver_samples_files_c75c9f39abed

Scope verified against `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included in subset A. The listed FastFAT files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/lockctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/lockctrl.c

## Purpose
Implements FAT byte-range lock control for both IRP dispatch and Fast I/O callbacks. It bridges Windows file-lock APIs to `FsRtl` lock routines while preserving FAT FCB synchronization and oplock semantics.

## Main Entry Points
- `FatFsdLockControl`: FSD dispatch routine for `IRP_MJ_LOCK_CONTROL`.
- `FatCommonLockControl`: common IRP path for lock and unlock operations.
- `FatFastLock`: Fast I/O lock callback.
- `FatFastUnlockSingle`: Fast I/O single-range unlock callback.
- `FatFastUnlockAll`: Fast I/O unlock-all callback.
- `FatFastUnlockAllByKey`: Fast I/O unlock-all-by-key callback.

## Behavior
`FatFsdLockControl` enters the filesystem, establishes top-level IRP state, creates an IRP context with wait behavior based on the IRP, and delegates to `FatCommonLockControl`. Exceptions are routed through FAT’s standard exception filter and processor.

All lock operations are valid only for `UserFileOpen`. Volume, directory, metadata, or unrecognized opens are rejected with `STATUS_INVALID_PARAMETER`.

The Fast I/O paths decode the file object, acquire or use FCB synchronization as needed, check whether oplocks allow the fast operation, then call the matching `FsRtlFast*` file-lock helper. On success they recompute `Fcb->Header.IsFastIoPossible` via `FatIsFastIoPossible`.

`FatCommonLockControl` acquires the FCB shared, checks oplocks, calls `FsRtlProcessFileLock`, updates Fast I/O eligibility, and completes the IRP context unless the IRP was posted by oplock handling.

## Synchronization And Oplocks
- Uses shared FCB acquisition for common IRP lock control.
- Fast lock uses `ExAcquireResourceSharedLite` directly on `Fcb->Header.Resource`.
- Fast unlock single checks oplock state but does not acquire the FCB resource in this file, unlike unlock-all variants.
- For Windows 8 and later, oplock checks are narrowed to lock operations within allocation size or unlock operations that may unblock waiting locks.
- Oplock-posted IRPs are not completed in the local finally path.

## Dependencies
- `FatDecodeFileObject`
- `FatCreateIrpContext`
- `FatAcquireSharedFcb`
- `FatFsdPostRequest`
- `FatGetFcbOplock`
- `FatOplockComplete`
- `FatCompleteRequest`
- `FsRtlFastLock`
- `FsRtlFastUnlockSingle`
- `FsRtlFastUnlockAll`
- `FsRtlFastUnlockAllByKey`
- `FsRtlProcessFileLock`
- `FsRtlCheckOplock`

## Important Notes
This file is almost entirely policy glue around `FsRtl` byte-range locking. The FAT-specific parts are open-type validation, FCB resource management, oplock mediation, request posting, and Fast I/O eligibility refresh.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/lockctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/namesup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/namesup.c

## Purpose
Provides FAT name conversion and selection support: wildcard matching, 8.3 conversion, long-name reconstruction, OEM/Unicode conversion, generated short-name selection, and case-bit handling.

## Main Entry Points
- `FatIsNameInExpression`: wildcard expression match for upcased OEM names.
- `FatStringTo8dot3`: converts an OEM string into the 11-byte FAT 8.3 directory-entry format.
- `Fat8dot3ToString`: converts a FAT 8.3 dirent name back into an OEM string, optionally restoring case.
- `FatGetUnicodeNameFromFcb`: obtains the Unicode long name for an FCB, or manufactures one from the short name.
- `FatSetFullFileNameInFcb`: lazily builds and stores the full Unicode path in an FCB.
- `FatUnicodeToUpcaseOem`: converts Unicode to upcased OEM with fallback allocation.
- `FatSelectNames`: chooses whether to use an input OEM name directly, generate an 8.3 short name, and/or create an LFN.
- `FatEvaluateNameCase`: decides whether FAT case flags are enough or an LFN is required.
- `FatSpaceInName`: detects spaces in a Unicode name.
- `FatUnicodeRestoreShortNameCase`: downcases 8.3 name and extension segments based on FAT NT case flags.

## Behavior
`FatStringTo8dot3` starts with an 11-byte space-filled output, copies the base name until a dot or length limit, then copies the extension into bytes 8 through 10. It translates a first byte of `0xe5` to FAT’s special `0x05` stored representation.

`Fat8dot3ToString` trims trailing spaces from base and extension fields, inserts a dot if an extension exists, restores the special first-character `0x05` back to `0xe5`, and optionally downcases base or extension letters using `Dirent->NtByte` flags. It carefully skips DBCS lead-byte sequences when applying ASCII case restoration.

`FatGetUnicodeNameFromFcb` locates the directory entry for an FCB, validates the located offset, and returns an LFN if present. If no LFN exists, it converts the restored short OEM name to Unicode. If the expected LFN/dirent relationship is inconsistent, it raises `STATUS_FILE_INVALID`.

`FatSetFullFileNameInFcb` lazily constructs a full path by walking parent DCBs toward the root. It reuses an ancestor’s cached full name when available, allocates a full-name buffer, then fills path components backward using `FatGetUnicodeNameFromFcb`.

`FatUnicodeToUpcaseOem` first tries conversion into caller-provided storage. If the buffer is too small, it lets the runtime allocate. Unmappable characters are represented by setting destination length to zero; other failures are normalized and raised.

`FatSelectNames` determines whether the proposed OEM name can be stored directly as a FAT short name. It forces short-name generation if the OEM name is empty, invalid as short OEM, or if the Unicode name contains a space. It optionally tries a caller-supplied short-name candidate before using `RtlGenerate8dot3Name`, checking each candidate against the parent directory with `FatLocateSimpleOemDirent`.

`FatEvaluateNameCase` implements the Chicago-mode case optimization decision: if the Unicode name is otherwise 8.3-compatible and case can be represented by the base/extension lowercase bits, no LFN is needed. Mixed case within a component or code-page invariant non-ASCII cases force LFN creation.

## Dependencies
- `FsRtlIsDbcsInExpression`
- `FsRtlIsLeadDbcsCharacter`
- `RtlGenerate8dot3Name`
- `RtlUnicodeStringToCountedOemString`
- `RtlUpcaseUnicodeStringToCountedOemString`
- `RtlOemStringToCountedUnicodeString`
- `RtlDowncaseUnicodeString`
- `FatLocateDirent`
- `FatLocateSimpleOemDirent`
- `FatIsNameShortOemValid`
- `FatUnpinBcb`

## Important Notes
This file encodes several FAT compatibility details: the deleted-entry `0xe5` escape, DBCS-safe case restoration, Chicago-mode case flags, generated short-name collision checks, and full-path lazy caching. It is a core dependency for create, lookup, directory enumeration, and rename behavior.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/namesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/nodetype.h -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/nodetype.h

## Purpose
Defines common FAT node type codes, bugcheck file IDs, ASCII control constants, and pool allocation tags. This header provides shared identity and diagnostics metadata for the FastFAT implementation.

## Main Definitions
- `NODE_TYPE_CODE`: `USHORT` type used as the first field of major FAT structures.
- `NODE_BYTE_SIZE`: byte-size type paired with `NODE_TYPE_CODE`.
- `NodeType(Ptr)`: macro that reads the leading node type code from a structure.
- FAT node codes:
  - `FAT_NTC_DATA_HEADER`
  - `FAT_NTC_VCB`
  - `FAT_NTC_FCB`
  - `FAT_NTC_DCB`
  - `FAT_NTC_ROOT_DCB`
  - `FAT_NTC_CCB`
  - `FAT_NTC_IRP_CONTEXT`

## Bugcheck Support
Defines per-source-file bugcheck ID high words such as:
- `FAT_BUG_CHECK_LOCKCTRL`
- `FAT_BUG_CHECK_NAMESUP`
- `FAT_BUG_CHECK_PNP`
- `FAT_BUG_CHECK_READ`
- `FAT_BUG_CHECK_RESRCSUP`
- `FAT_BUG_CHECK_SHUTDOWN`
- `FAT_BUG_CHECK_SPLAYSUP`

`FatBugCheck(A,B,C)` calls `KeBugCheckEx` with `FAT_FILE_SYSTEM` and combines the file-specific `BugCheckFileId` with `__LINE__`, giving crash diagnostics both file and line identity.

## Constants And Tags
The file defines byte constants for ASCII control characters from `UCHAR_NUL` through `UCHAR_SP`.

When not building the filesystem debugger extension, it defines pool tags for key allocations:
- Control structures: `TAG_CCB`, `TAG_FCB`, `TAG_FCB_NONPAGED`, `TAG_IRP_CONTEXT`
- Cache and metadata buffers: `TAG_BCB`, `TAG_DIRENT`, `TAG_FAT_BITMAP`, `TAG_FILENAME_BUFFER`
- I/O contexts and buffers: `TAG_FAT_IO_CONTEXT`, `TAG_IO_RUNS`, `TAG_IO_BUFFER`, `TAG_IO_USER_BUFFER`
- Verification and defrag helpers: `TAG_VERIFY_BOOTSECTOR`, `TAG_VERIFY_ROOTDIR`, `TAG_DEFRAG_BUFFER`

## Important Notes
Most FastFAT structures rely on the convention documented here: the first fields are node type and node byte size. Many files use `NodeType` for defensive runtime validation before casting generic filesystem pointers to VCB/FCB/DCB/CCB structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/nodetype.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/pnp.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/pnp.c

## Purpose
Implements Plug and Play handling for mounted FAT volumes. It responds to query remove, remove, surprise remove, cancel remove, and passes unknown PnP minors to the lower storage stack.

## Main Entry Points
- `FatFsdPnp`: FSD dispatch routine for `IRP_MJ_PNP`.
- `FatCommonPnp`: validates the volume device object and dispatches by PnP minor function.
- `FatPnpQueryRemove`: handles `IRP_MN_QUERY_REMOVE_DEVICE`.
- `FatPnpRemove`: handles `IRP_MN_REMOVE_DEVICE`.
- `FatPnpSurpriseRemove`: handles `IRP_MN_SURPRISE_REMOVAL`.
- `FatPnpCancelRemove`: handles `IRP_MN_CANCEL_REMOVE_DEVICE`.
- `FatPnpAdjustVpbRefCount`: adjusts VPB reference count under VPB spin lock.
- `FatPnpCompletionRoutine`: signals synchronous waiters and returns `STATUS_MORE_PROCESSING_REQUIRED`.

## Behavior
`FatFsdPnp` sets up filesystem entry, top-level IRP state, and an IRP context. PnP normally lacks a file object, so it usually forces waitable processing.

`FatCommonPnp` forces `IRP_CONTEXT_FLAG_WAIT`, acquires the global FAT resource exclusively, validates that the device object is a FastFAT volume device object with a valid VCB node type, and dispatches based on the minor function. Unknown minor functions release the global resource, skip the current stack location, call the lower device, and delete the IRP context without completing the IRP locally.

`FatPnpQueryRemove` locks the volume, temporarily bumps the VPB reference count while dropping and reacquiring locks in the required order, flushes and cleans the volume, sends the query down synchronously, and if lower drivers succeed initiates forced dismount through `FatCheckForDismount`.

`FatPnpRemove` unlocks the volume if necessary, forwards the remove IRP synchronously, flushes/cleans without flushing storage (`NoFlush`), then attempts forced dismount. This can be the first notification after some storage-stack failure paths.

`FatPnpSurpriseRemove` forwards the surprise removal synchronously, cleans what it can without flushing, and initiates dismount. It assumes the physical device may already be gone.

`FatPnpCancelRemove` reacquires the VCB, releases the global resource, unlocks the volume benignly, and passes the cancel IRP down without installing a completion routine because FAT does not need to observe completion.

## Synchronization
- Global resource protects against volume teardown while locating and validating the VCB.
- Query/remove/surprise paths acquire the VCB exclusively.
- Query remove deliberately releases and reacquires global/VCB resources to maintain lock ordering.
- VPB reference count changes are protected by `IoAcquireVpbSpinLock`.
- Forwarded PnP IRPs that FAT must observe are sent with a completion routine and waited on via `KEVENT`.

## Dependencies
- `FatAcquireExclusiveGlobal`
- `FatAcquireExclusiveVcb`
- `FatLockVolumeInternal`
- `FatUnlockVolumeInternal`
- `FatFlushAndCleanVolume`
- `FatCheckForDismount`
- `IoCallDriver`
- `IoCopyCurrentIrpStackLocationToNext`
- `IoSkipCurrentIrpStackLocation`
- `IoSetCompletionRoutine`

## Important Notes
The file is primarily about safe teardown ordering. Query remove is the strongest path: FAT locks, flushes, passes the query down, and then tries to dismount immediately. Surprise and remove paths avoid relying on successful media access and use `NoFlush`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/read.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/read.c

## Purpose
Implements all FastFAT read handling: dispatch entry, stack-overflow fallback, paging-file reads, cached reads, noncached reads, volume reads, directory/EA metadata reads, MDL reads, EOF/VDL trimming, and completion behavior.

## Main Entry Points
- `FatFsdRead`: dispatch routine for `IRP_MJ_READ`.
- `FatCommonRead`: common read implementation for FSD/FSP paths.
- `FatPostStackOverflowRead`: posts low-stack reads to a special stack-overflow worker.
- `FatStackOverflowRead`: worker routine for posted low-stack reads.
- `FatOverflowPagingFileRead`: low-stack paging-file read worker.

## Dispatch Behavior
`FatFsdRead` first handles paging-file I/O as a special fast path before creating an IRP context. Paging-file reads are marked pending and sent to `FatPagingFileIo`, or posted to `FsRtlPostPagingFileStackOverflow` when remaining stack is below `OVERFLOW_READ_THRESHHOLD`.

For normal reads it sets top-level IRP state, creates an IRP context, handles MDL-complete requests through `FatCompleteMdl`, checks for stack overflow risk, and calls `FatCommonRead`.

## Stack Overflow Handling
`FatPostStackOverflowRead` preacquires the resource that `FatCommonRead` will need, prepares the IRP for posting, marks verify-read context when needed, posts to `FsRtlPostStackOverflow`, waits for the worker to reach the safe point, then releases the preacquired resource.

`FatStackOverflowRead` forces waitable processing, temporarily substitutes `Vcb->VerifyThread` for verify-driven reads, calls `FatCommonRead`, maps `STATUS_FILE_DELETED` to EOF in that special path, restores verify-thread state, and signals the waiting event.

## Read Classification
`FatCommonRead` decodes the file object into:
- `VirtualVolumeFile`
- `UserVolumeOpen`
- `UserFileOpen`
- `DirectoryFile`
- `EaFile`
- `UserDirectoryOpen`

Zero-length reads complete immediately with success.

Raw volume opens are forced noncached. Virtual volume reads and user volume reads are translated to LBO-based lower-device reads with `FatSingleAsync`.

User directory opens reject read with `STATUS_INVALID_PARAMETER`.

## User Volume Reads
For `UserVolumeOpen`, the code:
- Verifies the VCB unless the CCB indicates complete dismount or format-unit state.
- Sets override-verify for format-unit follow-up I/O.
- Performs a one-time DASD flush unless the volume is locked.
- Trims reads to volume size unless extended DASD I/O is allowed.
- Locks the user buffer and sends one async lower-device read.
- Updates disk accounting on newer Windows when enabled.
- Updates current byte offset for synchronous nonpaging reads.

## User File Reads
For user files, the code:
- Rejects high-part offsets beyond FAT’s supported range with EOF.
- Flushes cached data before noncached nonpaging reads when a data section exists.
- Acquires paging I/O resource for paging reads, otherwise the main FCB resource.
- Uses `FatAcquireSharedFcbWaitForEx` for async noncached reads to avoid starving exclusive waiters.
- Verifies the FCB.
- Checks oplocks for nonpaging reads.
- Checks byte-range locks via `FsRtlCheckLockForReadAccess`.
- Trims reads to file size and treats reads starting at or beyond EOF as EOF.

## Noncached User File Reads
The noncached path:
- Determines sector size.
- Raises effective VDL to at least `ValidDataToDisk`.
- Zeroes portions beyond valid data length.
- Completes entirely from zeroing if the read starts beyond VDL.
- Trims physical read length to VDL, then rounds to sector boundary.
- Uses `FatNonCachedNonAlignedRead` for misaligned reads or when sector rounding would exceed caller buffer length.
- Uses `FatNonCachedIo` for aligned reads.
- Reports the original requested byte count constrained to file size, not just the physical byte count.

## Cached And MDL Reads
The cached path initializes the cache map lazily if needed, checking allocation size first and raising corruption if file size exceeds allocation. Normal cached reads use `CcCopyRead` or `CcCopyReadEx`; if the cache manager cannot wait and the IRP context is nonwaitable, the request is posted. MDL reads use `CcMdlRead` and require waitable processing.

## Directory And EA Reads
Directory and EA file reads are expected to be noncached paging I/O and sector-aligned. They are constrained to allocation size, return success with zero bytes when starting beyond allocation, and use `FatNonCachedIo`.

## Completion And Cleanup
The common finally path:
- Releases acquired FCB or paging resources.
- Posts requests through `FatFsdPostRequest` unless oplock handling already posted them.
- Updates synchronous file position for completed nonpaging reads.
- Marks `FO_FILE_FAST_IO_READ` on successful nonpaging reads so access time can be updated later.
- Frees stack `FAT_IO_CONTEXT` zero MDLs if the operation exits before normal async completion.
- Completes the IRP unless it was posted or already handed to async I/O.

## Important Notes
This is one of the central FastFAT data paths. Its critical invariants are EOF/VDL correctness, sector alignment for noncached I/O, resource choice between main and paging I/O resources, oplock and byte-range lock enforcement, and careful handling of low-stack conditions.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/resrcsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/resrcsup.c

## Purpose
Implements FastFAT resource acquisition/release helpers for VCBs, FCBs, cache-manager callbacks, read-ahead, lazy writer, Cc flush, no-op cache callbacks, and section synchronization.

## Main Entry Points
- `FatAcquireExclusiveVcb_Real`
- `FatAcquireSharedVcb`
- `FatAcquireExclusiveFcb`
- `FatAcquireSharedFcb`
- `FatAcquireSharedFcbWaitForEx`
- `FatAcquireFcbForLazyWrite`
- `FatReleaseFcbFromLazyWrite`
- `FatAcquireFcbForReadAhead`
- `FatReleaseFcbFromReadAhead`
- `FatAcquireForCcFlush`
- `FatReleaseForCcFlush`
- `FatNoOpAcquire`
- `FatNoOpRelease`
- `FatFilterCallbackAcquireForCreateSection`

## VCB Acquisition
Exclusive and shared VCB acquisition use `ExAcquireResource*Lite` with wait behavior from `IRP_CONTEXT_FLAG_WAIT`. After acquisition they call `FatVerifyOperationIsLegal` unless explicitly suppressed. If verification raises, the resource is released in the abnormal-termination path.

## FCB Acquisition
Exclusive and shared FCB acquisition retry around outstanding async noncached writes. If `OutstandingAsyncWrites` is nonzero and the current operation should not proceed concurrently, the code waits on `OutstandingAsyncEvent`, releases the FCB, and retries acquisition.

`FatAcquireSharedFcbWaitForEx` is a specialized nonwaitable, noncached path that uses `ExAcquireSharedWaitForExclusive` so exclusive waiters are honored before the shared read proceeds.

## Lazy Writer And Read Ahead
`FatAcquireFcbForLazyWrite` acquires the paging I/O resource for normal files, but the main resource for the EA file. It marks the current thread as the FCB lazy writer thread and sets `IoGetTopLevelIrp` to `FSRTL_CACHE_TOP_LEVEL_IRP` so reentrant cache-manager activity is treated correctly.

`FatReleaseFcbFromLazyWrite` clears the lazy writer marker, releases the matching resource, and clears the top-level IRP sentinel.

`FatAcquireFcbForReadAhead` acquires the main resource shared to synchronize with purges and also sets the cache top-level IRP sentinel. The release routine clears the sentinel and releases the main resource.

## Cc Flush Handling
`FatAcquireForCcFlush` installs the cache top-level IRP sentinel if none exists, decodes the file object, and acquires resources in a way that avoids FAT’s lock-order inversion risk. The file comments explicitly state FAT lock order as main resource, then BCB, then paging I/O resource. Directories and EA files avoid taking main in this path; regular files may take both main and paging.

`FatReleaseForCcFlush` clears the sentinel when appropriate and releases the resources acquired for flush.

## No-op Cache Callbacks
`FatNoOpAcquire` and `FatNoOpRelease` do not acquire a resource. They only set and clear `FSRTL_CACHE_TOP_LEVEL_IRP`, used where cache callbacks require a shape-compatible acquire/release pair but no actual resource synchronization.

## Section Synchronization
`FatFilterCallbackAcquireForCreateSection` handles MM/filter acquire-for-section synchronization. It acquires the FCB main resource exclusive and returns:
- `STATUS_FSFILTER_OP_COMPLETED_SUCCESSFULLY` for non-create-section sync types.
- `STATUS_FILE_LOCKED_WITH_ONLY_READERS` when no writers are present.
- `STATUS_FILE_LOCKED_WITH_WRITERS` when write handles exist.

The comment notes that the default FSRTL release routine is expected because this routine acquires only the main resource.

## Important Notes
This file centralizes many resource ordering rules that other FastFAT paths rely on. The top-level IRP sentinel behavior is as important as the resource operations: it prevents cache-manager and memory-manager reentry from being mistaken for ordinary user filesystem recursion.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/resrcsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/shutdown.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/shutdown.c

## Purpose
Implements FastFAT filesystem shutdown. It flushes mounted volumes, marks clean volumes clean, sends shutdown IRPs to lower storage devices, dismounts where possible, unregisters filesystem device objects, and completes the shutdown IRP.

## Main Entry Points
- `FatFsdShutdown`: dispatch routine for `IRP_MJ_SHUTDOWN`.
- `FatCommonShutdown`: common shutdown implementation.

## Behavior
`FatFsdShutdown` enters the filesystem, establishes top-level IRP state, creates a waitable IRP context, and calls `FatCommonShutdown`. Exceptions are handled through FAT’s normal exception path.

`FatCommonShutdown` disables popups and forces write-through behavior on the IRP context. It sets `FatData.ShutdownStarted`, acquires the global FAT resource exclusively, then iterates all VCBs on `FatData.VcbQueue`.

For each mounted, good, not-yet-shutdown volume:
- Acquires the volume exclusively.
- Attempts to flush the volume.
- If the mounted-dirty flag is not set, purges the volume file cache section and marks the volume clean.
- Builds and sends a synchronous `IRP_MJ_SHUTDOWN` to the target device object.
- Marks the VCB with `VCB_STATE_FLAG_SHUTDOWN`.
- Calls `FatCheckForDismount`.
- Releases the volume if the VCB was not deleted.

Exceptions during flush or lower-device shutdown are caught locally, reset in the IRP context, and do not prevent sending shutdown to the target device or processing subsequent volumes.

The final block releases the global resource, unregisters disk and CD-ROM filesystem device objects, deletes those device objects, and completes the original IRP with `STATUS_SUCCESS`.

## Dependencies
- `FatAcquireExclusiveGlobal`
- `FatAcquireExclusiveVolume`
- `FatFlushVolume`
- `FatMarkVolume`
- `FatCheckForDismount`
- `IoBuildSynchronousFsdRequest`
- `IoCallDriver`
- `IoUnregisterFileSystem`
- `IoDeleteDevice`
- `CcPurgeCacheSection`

## Important Notes
Shutdown is deliberately synchronous and global. It favors best-effort cleanup: even if flushing a volume raises, the code still tries to notify the lower storage stack with shutdown so device caches can be flushed.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/splaysup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/splaysup.c

## Purpose
Implements name lookup support using RTL splay trees. It inserts, removes, finds, and compares FAT file-name nodes used by DCB directory children.

## Main Entry Points
- `FatInsertName`: inserts a `FILE_NAME_NODE` into an OEM-name splay tree.
- `FatRemoveNames`: removes an FCB’s short and long names from parent DCB splay trees.
- `FatFindFcb`: searches a splay tree by name and splays the found node to root.
- `FatCompareNames`: deterministic bytewise name comparison.

## Behavior
`FatInsertName` initializes the new node’s splay links and walks the current root comparing OEM names with `CompareNames`. It inserts as a left child when the existing node is greater, otherwise as a right child. If an equal name already exists, it treats this as serious unless the existing FCB is no longer good. For stale duplicate names, it marks the old FCB bad, removes its names, and restarts insertion so the new name wins.

`FatRemoveNames` removes the FCB short name from the parent’s OEM splay tree. If OEM long-name and Unicode long-name nodes are present, it removes those from the appropriate parent roots, frees their allocated string buffers, clears state flags, and finally clears `FCB_STATE_NAMES_IN_SPLAY_TREE`.

`FatFindFcb` searches the tree with `CompareNames`. On a match, it splays the matching node to the root, optionally returns whether the matched node represents a DOS filename, and returns the node’s FCB. Missing names return `NULL`.

`FatCompareNames` compares two counted byte strings by `RtlCompareMemory`, then length. It is intentionally case-sensitive and byte-oriented; comments note that whether the bytes represent OEM or Unicode does not matter for deterministic tree ordering.

## Data Structures
- `PRTL_SPLAY_LINKS`: tree links.
- `FILE_NAME_NODE`: contains splay links, name, FCB pointer, and DOS-name marker.
- Parent DCB roots:
  - `Parent->Specific.Dcb.RootOemNode`
  - `Parent->Specific.Dcb.RootUnicodeNode`

## Dependencies
- `RtlInitializeSplayLinks`
- `RtlInsertAsLeftChild`
- `RtlInsertAsRightChild`
- `RtlDelete`
- `RtlSplay`
- `RtlLeftChild`
- `RtlRightChild`
- `RtlFreeOemString`
- `RtlFreeUnicodeString`
- `FatMarkFcbCondition`
- `FatBugCheck`

## Important Notes
This file maintains the in-memory directory-name index. Correct removal of all short/OEM-long/Unicode-long nodes is essential before rename, teardown, or stale-media recovery. Duplicate-name handling explicitly accounts for removable media changing underneath still-open handles.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/splaysup.c -->