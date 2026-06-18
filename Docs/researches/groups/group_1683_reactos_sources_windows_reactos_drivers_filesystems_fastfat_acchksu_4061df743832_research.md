# Group Research: ReactOS FastFAT allocation, cache, and access support

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/reactos` is included in subset A. The three listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/acchksup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/acchksup.c

## Purpose

`acchksup.c` implements access-check support for the ReactOS FastFAT driver. FAT has no per-file ACLs, so this file enforces FAT attribute-based restrictions and performs device/volume-level privilege checks through Windows security APIs.

## Main Responsibilities

- Reject user access to FAT volume-label and device directory entries.
- Validate requested file access masks against the subset FastFAT understands.
- Enforce read-only file restrictions while allowing directory-specific operations when appropriate.
- Check `SE_MANAGE_VOLUME_PRIVILEGE`.
- Determine whether a caller has explicit access to the underlying device object, excluding access obtained only through the Everyone SID.
- Build a restricted token with the Everyone SID disabled for deny-only use.

## Key Functions

`FatCheckFileAccess`

- Inputs: FAT dirent attributes and desired access mask.
- Denies access to `FAT_DIRENT_ATTR_VOLUME_ID` and `FAT_DIRENT_ATTR_DEVICE`.
- Rejects unknown access bits outside the allowed set.
- For read-only entries, blocks write-data/append-like access while still allowing metadata/security-style access such as `READ_CONTROL`, `WRITE_DAC`, `WRITE_OWNER`, `SYNCHRONIZE`, EA access, and attribute access.
- If the read-only object is a directory, it still allows add-file/add-subdirectory/delete-child style directory operations.
- Uses SEH-style cleanup only for tracing/unwind consistency; no complex resource cleanup occurs.

`FatCheckManageVolumeAccess`

- Constructs a one-privilege `PRIVILEGE_SET` containing `SE_MANAGE_VOLUME_PRIVILEGE`.
- Calls `SePrivilegeCheck` against the access state's subject security context.
- Returns boolean privilege possession.

`FatExplicitDeviceAccessGranted`

- Fast path succeeds if `PreviouslyGrantedAccess` includes any specific right except pure `FILE_TRAVERSE`.
- Also succeeds for callers with manage-volume privilege.
- Otherwise locks the subject context, finds the effective token manually, creates a restricted token with Everyone disabled, temporarily swaps that token into the subject context, and calls `SeAccessCheck` against the device object's security descriptor.
- Restores the original token, unlocks the subject context, dereferences the restricted token, and returns the status from `SeAccessCheck`.

`FatCreateRestrictEveryoneToken`

- Creates a restricted token using `SeFilterToken`.
- Disables `SeWorldSid` by placing it in a one-entry `TOKEN_GROUPS` list.
- The caller must dereference the returned token with `ObDereferenceObject`.

## Dependencies and Interactions

- Depends on `fatprocs.h` for driver-wide types, flags, tracing, and FAT attribute constants.
- Uses NT security manager APIs: `SePrivilegeCheck`, `SeLockSubjectContext`, `SeReleaseSubjectContext`, `SeAccessCheck`, `SeFilterToken`.
- Uses object manager cleanup via `ObDereferenceObject`.
- `IoGetFileObjectGenericMapping()` supplies the generic mapping for device security checks.

## Invariants and Safety Notes

- `FatExplicitDeviceAccessGranted` must always restore the original effective token after the restricted-token check.
- Subject context locking spans the temporary token substitution and access check.
- `FatCreateRestrictEveryoneToken` initializes `*RestrictedToken` to `NULL` before calling `SeFilterToken`.
- Access decisions are deliberately coarse because FAT stores attributes, not ACLs.

## Error and Edge Cases

- If restricted token creation fails, `FatExplicitDeviceAccessGranted` releases the subject context before returning the failure status.
- If access was granted only through Everyone, the restricted-token recheck should fail unless another explicit ACE grants access.
- Read-only handling is attribute-based, not ACL-based, so it cannot express richer security semantics.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/acchksup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/allocsup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/allocsup.c

## Purpose

`allocsup.c` implements FastFAT allocation support: FAT scanning, free-space bitmap setup, cluster allocation/deallocation, file allocation lookup, MCB maintenance, FAT entry reads/writes, bad cluster tracking, FAT32 windowing, and dirty FAT tracking.

## Main Responsibilities

- Derive volume allocation geometry from the BPB.
- Build and maintain free-cluster bitmaps.
- Support FAT12, FAT16, and FAT32 entry formats.
- Split FAT32 free-space tracking into windows when the volume is too large for one bitmap.
- Map file VBOs to LBOs by combining cached MCB runs with on-disk FAT chain traversal.
- Allocate, extend, truncate, merge, split, and deallocate cluster chains.
- Keep FAT contents, in-memory MCBs, free-cluster counts, dirty FAT ranges, and dirent first-cluster fields coherent.
- Mark bad clusters in `BadBlockMcb`.
- Handle maximal 32-bit FAT file-size edge cases.

## Core Data Structures and Macros

- `FreeClusterBitMap`: RTL bitmap for the current allocation window.
- `FAT_WINDOW`: tracks `FirstCluster`, `LastCluster`, and `ClustersFree`.
- `MAX_CLUSTER_BITMAP_SIZE`: caps a bitmap window at 65536 clusters.
- `FatWindowOfCluster`: maps a cluster number to its FAT32 window.
- `DirtyFatMcb`: records dirty FAT sectors for later mirroring/flush behavior.
- Allocation macros wrap common operations:
  - `FatReserveClusters` sets bitmap bits and advances `ClusterHint`.
  - `FatUnreserveClusters` clears bits and may move `ClusterHint` backward.
  - `FatAllocateClusters` writes FAT links or last markers.
  - `FatFreeClusters` writes available markers.
  - `FatFindFreeClusterRun` optimizes single-cluster lookup before using `RtlFindClearBits`.

## Key Functions

`FatSelectBestWindow`

- Chooses a FAT32 allocation window.
- Prefers the first window with at least 50% free clusters.
- Otherwise prefers the first completely empty window.
- Otherwise selects the window with the greatest free count.

`FatSetupAllocationSupport`

- Computes root directory LBO/size, file area LBO, number of clusters, FAT entry width, and sector/cluster log sizes.
- Caps `NumberOfClusters` to the number describable by the FAT, handling malformed DOS-format volumes and FAT32 too.
- Initializes the virtual volume file cache map for the reserved area and FAT.
- Allocates FAT windows, scans FAT entries, initializes the current free-space bitmap, and sets `ClusterHint`.
- For large FAT32 volumes, first scans all windows for free counts, then selects and materializes one current bitmap window.

`FatTearDownAllocationSupport`

- Frees the windows array and free-cluster bitmap buffer.
- Clears `DirtyFatMcb`.

`FatLookupFileAllocation`

- Looks up a VBO in the file's MCB first.
- If missing, walks the FAT chain from the last known MCB run or the file's first cluster.
- Adds contiguous runs to the MCB while scanning.
- Detects corrupt chains: available/reserved/bad entries inside a file chain, VBO wraparound, or chain length beyond volume size.
- Handles `MAXULONG - 1` lookup sentinel used by `FatLookupFileAllocationSize`.
- Reports `EndOnMax` for the maximal FAT file case.

`FatAddFileAllocation`

- Ensures real allocation size is known before extending.
- For first allocation, obtains the dirent, allocates disk space into the file MCB, updates `FirstClusterOfFile` and the dirent low/high first-cluster fields.
- For extension, allocates into a temporary MCB using the last allocated cluster as a hint, grows cache-manager file sizes, then merges the new allocation into the file MCB.
- Has detailed unwind paths for cache-size growth failure, dirent update failure, MCB failure, and FAT update failure.

`FatTruncateFileAllocation`

- Rounds requested size to a cluster boundary unless truncating to zero.
- No-ops when requested allocation is already satisfied.
- For truncation to zero, updates the dirent first-cluster fields to zero before deallocating clusters.
- For partial truncation, splits the existing MCB at the target VBO and deallocates the remainder.
- Notes deliberate leak-tolerant behavior in some failure cases: consistent in-memory/on-disk metadata is preferred over risky reallocation.

`FatLookupFileAllocationSize`

- Calls `FatLookupFileAllocation` with sentinel `MAXULONG - 1`.
- Fills in the true allocation size after FAT chain traversal.
- Raises corruption if recorded file size exceeds discovered allocation size.

`FatAllocateDiskSpace`

- Rounds requested bytes to clusters and handles the 4 GiB minus 1 maximal allocation case.
- Reserves global free-cluster count under `ChangeBitMapResource` and the bitmap mutex before searching.
- Honors an absolute cluster hint when possible, including FAT32 window switches.
- Supports exact-match allocation for callers such as defrag/move operations.
- Allocates either one contiguous run or multiple fragmented runs, chaining them in the FAT and describing them in the output MCB.
- On failures, unwinds bitmap reservations, free-cluster counts, MCB runs, and FAT allocations.

`FatDeallocateDiskSpace`

- Optionally zeroes the disk allocation before freeing, using MDL-backed synchronous write-through IRPs capped at `MAX_ZERO_MDL_SIZE`.
- Writes `FAT_CLUSTER_AVAILABLE` into each FAT run first.
- Only after FAT updates succeed does it clear bitmap bits and update per-window/global free counts.
- Handles deallocations spanning FAT32 windows.
- On abnormal termination before bitmap/free-count updates, attempts to reconstruct FAT chains from the MCB.

`FatSplitAllocation`

- Moves all MCB runs from `SplitAtVbo` onward into `RemainingMcb`, rebasing them to VBO zero.
- Writes `FAT_CLUSTER_LAST` into the last cluster of the retained chain.
- On failure, moves runs back into the original MCB.

`FatMergeAllocation`

- Appends zero-based runs from `SecondMcb` to the end of `Mcb`.
- Links the old last cluster to the first cluster of `SecondMcb`.
- On failure, removes appended MCB runs from the first MCB.

`FatInterpretClusterType`

- Normalizes FAT12/FAT16/FAT32 entries and classifies them as available, next, reserved, bad, or last.
- Masks FAT32 entries with `FAT32_ENTRY_MASK`.

`FatLookupFatEntry`

- Reads one FAT entry using cache-manager mappings.
- FAT12 pins the whole FAT because 12-bit entries can cross page boundaries.
- FAT16/FAT32 pin and reuse one page through `FAT_ENUMERATION_CONTEXT`.
- Validates indices before reading.

`FatSetFatEntry`

- Writes one FAT entry.
- Special-cases `FAT_DIRTY_BIT_INDEX` to set FAT clean/dirty volume state and temporarily disables normal dirty-volume semantics.
- Updates `DirtyFatMcb` for affected sectors.
- Preserves FAT32 reserved high bits for normal file-heap entries.
- Uses write-through unpinning for clean-volume updates or mount-in-progress corruption-sensitive writes.

`FatSetFatRun`

- Bulk-writes a contiguous cluster range as either a chained allocation or free entries.
- FAT12 pins the whole FAT and updates 12-bit entries under the free-cluster bitmap mutex.
- FAT16 pins all needed pages for the range.
- FAT32 processes chunks capped by `MAXCOUNTCLUS` to avoid pinning huge FAT spans.
- FAT32 unwind walks backward and restores changed entries when a later chunk fails.

`FatLogOf`

- Computes log2 for powers of two.
- Bugchecks if given a non-power-of-two value.

`FatExamineFatEntries`

- Scans FAT entries to initialize or refresh free-space data.
- Modes:
  - setup FAT32 windows and total free count,
  - switch the current bitmap window,
  - fill caller-provided bitmap for arbitrary FAT32 volume bitmap queries.
- Reads FAT12 whole, FAT16/FAT32 page by page, optionally prefetching pages on newer NTDDI.
- Tracks free/allocated runs, sets or clears bitmap bits, updates window free counts, tracks total free clusters when requested, and populates bad-block MCB entries.
- Swaps in a newly built bitmap only after a successful scan.

## Synchronization Model

- Free-cluster bitmap access is protected by `FreeClusterBitMapMutex`.
- Allocation/deallocation also uses `ChangeBitMapResource`, shared for normal bitmap/free-count changes and exclusive for FAT32 window switches.
- Many public allocation routines require the global critical region and are annotated with `_Requires_lock_held_(_Global_critical_region_)`.
- `FatSetFatEntry` and `FatSetFatRun` contain architecture-specific locking for non-atomic narrow writes on ALPHA.
- FAT32 current-window changes are designed to be atomic from the perspective of allocation state: build a temporary bitmap, then swap it into `Vcb`.

## Error Handling and Recovery

- The file relies heavily on SEH-style `try/finally` unwind blocks.
- Allocation paths reserve free counts before writing FAT entries and carefully restore them on failure.
- Deallocation writes FAT entries before clearing bitmap bits so clusters are not reused until disk state says they are free.
- Some truncate failure cases intentionally tolerate leaked clusters to avoid making metadata less consistent.
- Corrupt FAT chains raise `STATUS_FILE_CORRUPT_ERROR` and call `FatPopUpFileCorrupt`.

## Important Edge Cases

- FAT12 12-bit entries can straddle bytes/sectors/pages.
- FAT32 entries preserve reserved high bits.
- A file allocation size may be initially unknown and represented by `FCB_LOOKUP_ALLOCATIONSIZE_HINT`.
- Maximal FAT file size can wrap 32-bit byte counts; several paths special-case `0xFFFFFFFF` and VBO wrap.
- FAT32 large volumes may require switching allocation windows before satisfying a hint.
- Exact-match requests can fail without raising when contiguous placement is impossible.

## ReactOS-Specific Notes

- `FatSelectBestWindow` is marked `static` under `__REACTOS__`.
- Some FAT32 scan pointer arithmetic differs under `__REACTOS__` because `FatBuffer` is a `PUSHORT` while reading 32-bit entries.
- The file is largely derived from Microsoft FastFAT style code, with ReactOS compatibility conditionals.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/allocsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/cachesup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/fastfat/cachesup.c

## Purpose

`cachesup.c` wraps Windows Cache Manager operations used by FastFAT for volume FAT access, directory-file access, EA-file access, dirty pinned BCB tracking, repinned BCB writeback, zeroing, MDL completion, cache uninitialization, and optional page prefetching.

## Main Responsibilities

- Initialize cache maps with FastFAT callbacks and optional disk I/O accounting.
- Map or pin volume-file FAT/reserved-sector data.
- Map, pin, extend, and zero cached directory data.
- Create and cache internal stream file objects for directories and EA data.
- Mark BCBs dirty and schedule volume dirty/clean state transitions.
- Repin BCBs for reversible metadata operations and later unpin/write them through.
- Purge cache on write-through errors for removable/deferred-flush media.
- Provide MDL read/write completion helpers.
- Synchronize cache uninitialization for teardown.
- Prefetch FAT pages on supported NTDDI versions.

## Key Functions

`FatInitializeCacheMap`

- Calls `CcInitializeCacheMap`.
- On Windows 8+ builds, enables Cache Manager disk I/O accounting when `FatDiskAccountingEnabled` is set.

`FatReadVolumeFile`

- Maps bytes from the virtual volume file.
- Used for boot/reserved/FAT regions where VBO equals LBO.
- Asserts accesses remain within the BPB/FAT area, with a mount-time exception for offset zero.
- Raises `STATUS_CANT_WAIT` if nonblocking cache mapping would block.

`FatPrepareWriteVolumeFile`

- Pins volume-file bytes for metadata writes.
- Optionally zeroes the pinned buffer.
- Marks the BCB dirty through `FatSetDirtyBcb`, optionally reversible.
- Unpins on abnormal termination.

`FatReadDirectoryFile`

- Ensures a directory stream file object and cache map exist via `FatOpenDirectoryFile`.
- Handles zero-byte reads and EOF.
- Truncates reads at allocation size.
- Uses either `CcPinRead` or `CcMapData` depending on the caller's `Pin` argument.
- Raises `STATUS_CANT_WAIT` for nonblocking cache misses.

`FatPrepareWriteDirectoryFile`

- Ensures directory cache state exists.
- Extends directory allocation if the write exceeds current allocation, except non-FAT32 root directories which cannot grow.
- Updates cache-manager sizes after extension.
- Ensures the free-dirent bitmap is large enough.
- Pins in page-sized chunks inside the original request, then can use `VACB_MAPPING_GRANULARITY` chunks beyond it to avoid OBCB/repin problems.
- Zeroes newly allocated directory clusters and dirties them.
- On failure, unpins buffers and truncates back to the initial allocation when this routine allocated new disk space.

`FatIsCurrentOperationSynchedForDcbTeardown` debug-only

- Verifies the current operation has enough synchronization to safely attach an internal directory file object to a DCB.
- Accepts mount operations, held VCB resources, parent-by-child contexts, or file objects that refer to the DCB or descendants.
- Can be bypassed by `FatDisableParentCheck` in debug builds.

`FatOpenDirectoryFile`

- Resolves unknown allocation size if necessary.
- Ensures the directory free-dirent bitmap exists.
- Lazily creates an internal stream file object under the directory-file mutex.
- Sets FastFAT file object type to `DirectoryFile`, increments internal/residual opens, assigns section object pointers, and grants read/write/delete access.
- Initializes the directory cache map with no-op cache callbacks.
- Asserts synchronization against DCB teardown in debug builds.

`FatOpenEaFile`

- Creates an internal stream file object for EA data.
- Preallocates close context, sets file object type to `EaFile`, increments internal/residual opens, assigns section object pointers, and initializes cache map with normal FastFAT callbacks.
- Sets additional cache attributes for the EA stream.

`FatCloseEaFile`

- Requires exclusive VCB ownership.
- Optionally flushes the EA file cache.
- Clears `VirtualEaFile`, empties the EA FCB MCB, synchronously uninitializes the cache map, and dereferences the stream file object.

`FatSetDirtyBcb`

- Optionally repins the BCB for reversible metadata changes.
- Calls `CcSetDirtyPinnedData`.
- Unless dirty marking is disabled, marks non-FAT12 volumes dirty.
- Uses throttling based on `LastFatMarkVolumeDirtyCall`.
- Sets or refreshes a clean-volume timer: shorter for deferred-flush/hot-plug volumes, longer otherwise.
- If transitioning to dirty, writes physical dirty state through `FatMarkVolume`, sets `VCB_STATE_FLAG_VOLUME_DIRTY`, and disables eject for removable media.

`FatRepinBcb`

- Maintains a dense linked list of repinned BCB arrays inside `IrpContext`.
- Avoids duplicate repinning of the same BCB.
- Allocates additional `REPINNED_BCBS` records as needed.

`FatUnpinRepinnedBcbs`

- Walks all repinned BCBs and calls `CcUnpinRepinnedBcb`.
- Determines write-through behavior from request flags and deferred-flush media.
- Captures the first writeback error.
- For deferred-flush removable media write failures, may purge the affected file cache after unpinning other BCBs for the same file to avoid deadlock.
- Avoids purging for cleanup, flush, set-information, and a specific create/verify-required case where create rollback handles the state.
- Forces volume verify on serious write-through failures and raises normalized status unless raising is disabled.

`FatZeroData`

- Aligns zeroing to sector boundaries because this helper exists for non-sector-aligned limitations.
- Returns success for purely partial-sector ranges that require no whole-sector zeroing.
- Calls `CcZeroData` with the current wait policy.

`FatCompleteMdl`

- Completes MDL read or write requests.
- Uses `CcMdlReadComplete` for reads and `CcMdlWriteComplete` for writes.
- Clears `Irp->MdlAddress` and completes the IRP.
- Bugchecks on unsupported major functions.

`FatSyncUninitializeCacheMap`

- Calls `CcUninitializeCacheMap` with a completion event and waits for it.
- Used when teardown must know cache/Mm purge processing has completed.

`FatPinMappedData`

- Pins previously mapped directory data with `CcPinMappedData`.
- Raises `STATUS_CANT_WAIT` on nonblocking cache miss.

`FatPrefetchPages`

- Windows 8+ helper.
- Retrieves I/O priority from the originating IRP.
- Builds a `READ_LIST` and calls `MmPrefetchPages`.
- Caps behavior to nonzero page counts and frees the read list on cleanup.

## Dependencies and Interactions

- Depends on Cache Manager APIs: `CcInitializeCacheMap`, `CcMapData`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinRepinnedBcb`, `CcPurgeCacheSection`, `CcZeroData`, `CcMdlReadComplete`, `CcMdlWriteComplete`, and `CcUninitializeCacheMap`.
- Interacts closely with allocation support through `FatAddFileAllocation`, `FatTruncateFileAllocation`, `FatLookupFileAllocationSize`, and MCB manipulation.
- Uses FastFAT volume state and timers to coordinate dirty/clean volume transitions.
- Creates internal stream file objects with `IoCreateStreamFileObject`.
- Relies on section object pointers stored in FCB/DCB nonpaged state.

## Synchronization Model

- Directory stream file creation is protected by `FatAcquireDirectoryFileMutex` / `FatReleaseDirectoryFileMutex`.
- Several routines require the global critical region.
- `FatCloseEaFile` requires exclusive VCB ownership.
- Dirty volume timer state is guarded with `FatData.GeneralSpinLock`.
- Repinned BCB cleanup is serialized through the owning `IrpContext`.

## Error Handling and Recovery

- Cache miss without wait raises `STATUS_CANT_WAIT`.
- Directory extension failures unwind pinned BCBs and newly allocated disk space.
- EA file open dereferences the stream file object on abnormal termination.
- Repinned BCB write failures preserve the first error and may purge cache plus force verify.
- Synchronous cache uninitialization asserts successful wait completion.

## Important Edge Cases

- Non-FAT32 root directories cannot be extended.
- Directory write preparation pins page-granular chunks initially to avoid OBCBs that cannot be safely repinned.
- Partial-sector zeroing may intentionally be a no-op.
- FAT12 volumes are excluded from dirty-volume bit processing.
- Deferred-flush/removable media paths are stricter about write-through and verify handling.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/fastfat/cachesup.c -->