# Group Research: group_1833_windows_driver_samples_sources_windows_windows_driver_samples_files_6d0baed59b74

Scope confirmed against `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included. All twelve listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/lockctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/lockctrl.c

## Purpose

Implements CDFS byte-range lock handling for both regular IRP dispatch and Fast I/O lock callbacks.

## Main Entry Points

- `CdCommonLockControl`
- `CdFastLock`
- `CdFastUnlockSingle`
- `CdFastUnlockAll`
- `CdFastUnlockAllByKey`

## Key Behavior

`CdCommonLockControl` accepts only `UserFileOpen`. It checks oplock state with `FsRtlCheckOplock`, verifies the FCB, lazily creates `Fcb->FileLock`, then delegates byte-range lock processing to `FsRtlProcessFileLock`. After lock processing it recomputes `Fcb->IsFastIoPossible`.

The fast-path routines decode the file object with `CdFastDecodeFileObject`, reject non-user-file opens with `STATUS_INVALID_PARAMETER`, and avoid the fast path when `CdVerifyFcbOperation(NULL, Fcb)` fails. They wrap FsRtl lock calls in `FsRtlEnterFileSystem` / `FsRtlExitFileSystem`.

`CdFastLock` checks that oplocks permit fast I/O, creates the file-lock object without raising, calls `FsRtlFastLock`, and updates fast-I/O state when needed.

The unlock fast paths return `STATUS_RANGE_NOT_LOCKED` immediately when the FCB has no file-lock package. Otherwise they check oplock fast-I/O eligibility and call the matching FsRtl unlock primitive.

## Dependencies

This module depends on CDFS file-object decode helpers, FCB verification, file-lock allocation in `strucsup.c`, oplock completion/prepost helpers, and FsRtl file-lock APIs.

## Notes and Risks

The fast unlock routines reference `IrpContext` in `CdLockFcb(IrpContext, Fcb)` / `CdUnlockFcb(IrpContext, Fcb)` despite not declaring an `IrpContext` local. In this source as read, that is a compile-time issue unless hidden by non-obvious macro behavior outside this file. The analogous fast-lock routine uses `NULL` there.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/lockctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/namesup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/namesup.c

## Purpose

Provides CDFS name manipulation support: ISO/Joliet byte conversion, name/version splitting, upcasing, path component dissection, legal-name checks, 8.3 short-name generation, wildcard matching, embedded short-name offset decoding, and lexical name comparison.

## Main Entry Points

- `CdConvertNameToCdName`
- `CdConvertBigToLittleEndian`
- `CdUpcaseName`
- `CdDissectName`
- `CdIsLegalName`
- `CdIs8dot3Name`
- `CdGenerate8dot3Name`
- `CdIsNameInExpression`
- `CdShortNameDirentOffset`
- `CdFullCompareNames`

## Key Behavior

`CdConvertNameToCdName` splits a Unicode file name at `;`, making the suffix after the separator the version string when present.

`CdConvertBigToLittleEndian` converts Joliet big-endian Unicode bytes into little-endian form and raises `STATUS_DISK_CORRUPT_ERROR` on odd byte counts.

`CdUpcaseName` upcases both filename and version portions using `RtlUpcaseUnicodeString`. When producing a separate destination, it lays the version string after the filename and inserts the `;` separator.

`CdDissectName` removes one backslash-delimited path component from a remaining name and returns that component as `FinalName`.

`CdIsLegalName` validates characters against HPFS legality, while allowing `"`, `<`, `>`, and `|` for CDFS compatibility.

`CdIs8dot3Name` enforces short-name shape: limited length, no spaces, at most one dot, base length constraints, and OEM/FAT legality via `FsRtlIsFatDbcsLegal`.

`CdGenerate8dot3Name` calls `RtlGenerate8dot3Name`, then biases the result with a `~` plus a hexadecimal dirent-offset-derived value. It accounts for DBCS byte width when deciding how much base name can precede the suffix.

`CdIsNameInExpression` compares CDFS names against search expressions. It supports wildcard matching independently for file name and version string, and can skip version checking when requested.

`CdShortNameDirentOffset` parses a `~HEX` sequence before the dot and returns the decoded offset bucket, or `MAXULONG` if no valid sequence exists.

`CdFullCompareNames` performs a case-sensitive binary lexical comparison used by prefix splay trees.

## Dependencies

Uses `RtlGenerate8dot3Name`, Unicode/OEM conversion routines, FsRtl name-expression matching, FAT/HPFS legality helpers, and CDFS `CD_NAME` conventions shared with directory and prefix lookup code.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/namesup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/nodetype.h -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/nodetype.h

## Purpose

Defines CDFS node type codes, node-size conventions, node-type access macros, and per-source bugcheck IDs.

## Key Definitions

The file declares `NODE_TYPE_CODE`, `PNODE_TYPE_CODE`, and `NODE_BYTE_SIZE`. It assigns stable codes for core CDFS runtime objects:

- `CDFS_NTC_DATA_HEADER`
- `CDFS_NTC_VCB`
- `CDFS_NTC_FCB_PATH_TABLE`
- `CDFS_NTC_FCB_INDEX`
- `CDFS_NTC_FCB_DATA`
- `CDFS_NTC_FCB_NONPAGED`
- `CDFS_NTC_CCB`
- `CDFS_NTC_IRP_CONTEXT`
- `CDFS_NTC_IRP_CONTEXT_LITE`

`NodeType(P)` safely returns `NTC_UNDEFINED` for null pointers. `SafeNodeType(Ptr)` directly reads the first node-type field.

The bugcheck constants give each CDFS source file a high-word identifier. `CdBugCheck(A,B,C)` calls `KeBugCheckEx(CDFS_FILE_SYSTEM, BugCheckFileId | __LINE__, A, B, C)` so crashes encode both module and source line.

## Integration

All major CDFS structures are expected to begin with `NodeTypeCode` and `NodeByteSize`. Runtime code uses these codes to distinguish VCBs, FCB variants, CCBs, and IRP contexts during decode, teardown, PnP, and assertions.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/nodetype.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/pathsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/pathsup.c

## Purpose

Implements path-table support for CDFS. The path table is used as a compact breadth-first directory index, enabling directory lookup by parent ordinal and path-table offset.

## Main Entry Points

- `CdLookupPathEntry`
- `CdLookupNextPathEntry`
- `CdFindPathEntry`
- `CdMapPathTableBlock`
- `CdUpdatePathEntryFromRawPathEntry`
- `CdUpdatePathEntryName`

## Path Table Walking

`CdLookupPathEntry` maps the path-table sector containing a known offset, positions the enumeration context, and converts the raw entry into a `PATH_ENTRY`.

`CdLookupNextPathEntry` advances by the current path-entry length, remaps when the cursor moves into the second sector of a mapped two-sector block, detects EOF in the last block, and converts the next raw entry.

`CdFindPathEntry` searches child directory entries under a parent FCB. It starts from the cached first-child offset when available, otherwise from the parent path-table entry. It caches `ChildPathTableOffset` and `ChildOrdinal` once discovered. It raises corruption if a parent ordinal exceeds the 16-bit on-disk parent backpointer limit.

## Mapping and Validation

`CdMapPathTableBlock` maps two sectors at a time through the cache manager. If the two-sector range crosses a VACB view boundary, it allocates an auxiliary buffer, maps each sector separately, copies them together, and unpins each map.

`CdUpdatePathEntryFromRawPathEntry` reads raw name length, disk offset, XAR adjustment, parent ordinal, entry length, and raw directory-name pointer. It validates bounds in the last data block. A zero-length name is normally corruption, but the code treats it as EOF when the last path-table block length is block-aligned, preserving compatibility with some Video CD media.

## Name Handling

`CdUpdatePathEntryName` converts a raw path-table directory id into `CD_NAME` fields. It handles self-entry name `0` as a hard-coded directory name, converts OEM to Unicode for non-Joliet media, converts big-endian Unicode for Joliet, strips a trailing period, and optionally builds an uppercase comparison name.

## Dependencies

Uses path-table raw macros, cache-manager mapping, CDFS name conversion, path-entry memory management, VCB Joliet state, and FCB child-offset caching.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/pathsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/pnp.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/pnp.c

## Purpose

Handles Plug and Play IRPs for mounted CDFS volumes: query remove, remove, surprise removal, and cancel remove.

## Main Entry Points

- `CdCommonPnp`
- `CdPnpQueryRemove`
- `CdPnpRemove`
- `CdPnpSurpriseRemove`
- `CdPnpCancelRemove`
- `CdPnpCompletionRoutine`

## Dispatch Behavior

`CdCommonPnp` locates the VCB from the volume device object, validates that the device object is a CDFS volume object, forces synchronous operation, and dispatches by PnP minor code. Unknown minor codes and already-torn-down volumes are passed through with `IoSkipCurrentIrpStackLocation`.

## Remove Paths

`CdPnpQueryRemove` acquires the VCB, temporarily references it, tries to lock the volume, passes the query to the lower device stack synchronously, then initiates forced dismount on success. If the VCB remains due to lingering references, it returns `STATUS_DEVICE_BUSY`.

`CdPnpRemove` unlocks the volume if previously locked, marks the VCB invalid if no lock existed, forwards the remove IRP synchronously, and forces dismount.

`CdPnpSurpriseRemove` immediately marks the VCB invalid, forwards the surprise removal synchronously, then attempts forced dismount.

`CdPnpCancelRemove` reacquires the VCB, unlocks any previous query-remove volume lock, releases the VCB, and passes the cancel request down without a completion routine.

`CdPnpCompletionRoutine` signals a stack event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the caller can resume after synchronous lower-stack completion.

## Dependencies

Relies on global `CdData` locking, VCB exclusive acquisition, internal volume lock/unlock helpers, VCB condition updates, lower-device IRP forwarding, and `CdCheckForDismount`.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/pnp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/prefxsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/prefxsup.c

## Purpose

Maintains per-directory prefix lookup trees for fast path resolution. Each directory FCB owns exact-case and ignore-case splay-tree roots.

## Main Entry Points

- `CdInsertPrefix`
- `CdRemovePrefix`
- `CdFindPrefix`
- `CdFindNameLink`
- `CdInsertNameLink`

## Prefix Insertion and Removal

`CdInsertPrefix` inserts long-name or short-name prefix entries for an FCB under its parent. It allocates a `PREFIX_ENTRY` for short-name matches when needed, allocates a larger name buffer when the embedded buffer is too small, splits storage into exact-case and ignore-case names, and inserts the selected name into the parent’s matching splay tree.

`CdRemovePrefix` removes both short-name and long-name entries from the parent’s exact-case and ignore-case trees, clears in-tree flags, and frees any allocated long-name prefix buffer.

## Lookup

`CdFindPrefix` walks from a starting FCB through as many path components as are already present in prefix trees. It dissects the remaining path one component at a time, searches the appropriate splay tree, and descends to the matched child FCB. For ignore-case lookups, it copies the exact-case spelling back into the caller’s buffer. It carefully handles child acquisition failures by temporarily referencing the child, releasing the parent, then acquiring the child.

`CdFindNameLink` searches a splay tree using `CdFullCompareNames` and splays successful hits to the root.

`CdInsertNameLink` inserts a `NAME_LINK` into a splay tree and rejects duplicate names.

## Dependencies

Uses CDFS name comparison/dissection helpers, FCB resources and VCB reference accounting, RTL splay tree routines, and `PREFIX_ENTRY` fields embedded in FCBs.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/prefxsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/read.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/read.c

## Purpose

Implements common CDFS read handling for cached, noncached, paging, MDL, user-file, stream-file, and volume reads.

## Main Entry Point

- `CdCommonRead`

## Key Behavior

Zero-length reads complete immediately with success. Reads are rejected for unopened file objects and directory handles. Volume DASD reads are forced noncached.

The routine extracts waitability, paging I/O, noncached I/O, synchronous I/O, starting offset, and byte count. Paging I/O acquires the file shared with starvation of exclusive waiters; other reads acquire shared normally.

For user-file reads, it checks oplocks through `FsRtlCheckOplock` and verifies byte-range locks with `FsRtlCheckLockForReadAccess` for non-paging I/O.

EOF handling returns `STATUS_END_OF_FILE` when starting beyond EOF and truncates reads that extend past EOF, except for extended DASD volume opens.

## Noncached Reads

Noncached reads align to block boundaries. If an unaligned request needs waiting and the caller cannot wait, it raises `STATUS_CANT_WAIT`. It initializes `CD_IO_CONTEXT` either on the stack or from allocated storage, then calls `CdNonCachedXARead` for raw-sector/XA files or `CdNonCachedRead` otherwise.

On completion it normalizes unexpected I/O errors, raises user-induced errors, zero-fills any padding region when an aligned read returned more than logical bytes, and updates the synchronous file position on success.

## Cached Reads

Cached reads initialize the private cache map with `CcInitializeCacheMap` and a 64 KiB read-ahead granularity. Normal cached reads map the user buffer and call `CcCopyRead`; MDL reads call `CcMdlRead`. Successful synchronous non-paging reads advance `CurrentByteOffset`.

`STATUS_CANT_WAIT` posts the request to the FSP; other statuses complete the IRP directly.

## Dependencies

Uses CDFS FCB verification, oplock helpers, file-lock package, cache-manager callbacks, user-buffer mapping, noncached I/O helpers, XA/raw-sector flags, and CDFS request posting/completion helpers.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/resrcsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/resrcsup.c

## Purpose

Centralizes resource acquisition helpers and cache-manager / memory-manager synchronization callbacks.

## Main Entry Points

- `CdAcquireResource`
- `CdAcquireForCache`
- `CdReleaseFromCache`
- `CdNoopAcquire`
- `CdNoopRelease`
- `CdFilterCallbackAcquireForCreateSection`
- `CdReleaseForCreateSection`

## Key Behavior

`CdAcquireResource` wraps `ERESOURCE` acquisition for exclusive, shared, and shared-starve-exclusive modes. It decides whether to wait from `IRP_CONTEXT_FLAG_WAIT` unless `IgnoreWait` is set. If it cannot acquire and waiting was required, it raises `STATUS_CANT_WAIT`.

`CdAcquireForCache` and `CdReleaseFromCache` are cache-manager lazy-writer callbacks. The acquire path takes the FCB resource shared and sets top-level IRP to `FSRTL_CACHE_TOP_LEVEL_IRP`; release clears the top-level IRP and releases the resource.

`CdNoopAcquire` and `CdNoopRelease` are no-op callbacks for cases where synchronization is intentionally unnecessary.

`CdFilterCallbackAcquireForCreateSection` handles section synchronization. It acquires the nonpaged FCB resource exclusively, then takes the main file resource shared with starve-exclusive behavior to avoid create-section/read-cache deadlocks. Because CDFS is read-only, create-section synchronization reports `STATUS_FILE_LOCKED_WITH_ONLY_READERS`.

`CdReleaseForCreateSection` releases the resources acquired for section creation.

## Dependencies

Uses kernel `ERESOURCE` APIs, FsRtl cache top-level IRP conventions, FS filter section callbacks, and FCB resource layout from CDFS structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/resrcsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/shutdown.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/shutdown.c

## Purpose

Implements CDFS shutdown handling. It purges mounted volumes, forwards shutdown to underlying storage stacks, attempts dismount, and unregisters the filesystem device.

## Main Entry Point

- `CdCommonShutdown`

## Key Behavior

The routine disables popups, marks global CDFS shutdown state, acquires global CDFS data, and walks the global VCB queue. It skips volumes already shut down or not mounted.

For each mounted volume, it acquires the VCB exclusively, purges the volume, builds a synchronous `IRP_MJ_SHUTDOWN` for the target device stack, calls the target driver, waits if pending, clears the event, marks the VCB shutdown, and calls `CdCheckForDismount`.

After all volumes are processed, it releases global CDFS data, unregisters and deletes the filesystem device object, then completes the original shutdown IRP with success.

## Dependencies

Uses global VCB queue locking, purge/dismount support, synchronous FSD request construction, lower-device dispatch, and filesystem registration cleanup.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/shutdown.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/strucsup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/strucsup.c

## Purpose

Implements CDFS in-memory structure lifecycle: VCB initialization/deletion, FCB creation/initialization/teardown, CCB allocation, IRP context allocation/reuse, FCB table operations, TOC processing, file-lock creation, and audio-disc pseudo-volume support.

## Main Entry Points

- `CdInitializeVcb`
- `CdUpdateVcbFromVolDescriptor`
- `CdDeleteVcb`
- `CdCreateFcb`
- `CdInitializeFcbFromPathEntry`
- `CdInitializeFcbFromFileContext`
- `CdCreateCcb`
- `CdDeleteCcb`
- `CdCreateFileLock`
- `CdCreateIrpContext`
- `CdCleanupIrpContext`
- `CdInitializeStackIrpContext`
- `CdTeardownStructures`
- `CdLookupFcbTable`
- `CdGetNextFcb`
- `CdProcessToc`

## VCB Lifecycle

`CdInitializeVcb` zeroes the embedded VCB, initializes node type, notify synchronization, backup VPB, resources, mutexes, generic FCB table, target device reference, removable-media state, TOC fields, block factor, media change count, and initial mount reference counts. Audio-only media set audio/CD-XA state.

`CdUpdateVcbFromVolDescriptor` finalizes block geometry and creates internal FCBs. For data discs it creates the path-table stream, root directory index, and volume DASD FCB, initializes mappings and stream files, detects XA media, and sets sizes/attributes. For audio discs it creates pseudo path-table/root structures, synthesizes root directory size from track count, sets a hard-coded audio label, computes a TOC-derived serial, and exposes an ISO-like pseudo-root.

`CdDeleteVcb` frees the swap/current VPB as appropriate, dereferences the target device, frees XA and sector-cache state, removes the VCB from the global queue, deletes resources, frees TOC storage, uninitializes notify sync, and deletes the volume device object.

## FCB and CCB Lifecycle

`CdCreateFcb` looks up an existing FCB by file ID or allocates an index/path-table/data FCB, initializes common fields, MCB state, nonpaged FCB state, advanced header, and oplock state for data FCBs.

`CdInitializeFcbFromPathEntry` initializes directory FCBs from path-table entries, assigns stream offsets, ordinals, one-sector provisional sizes, initial allocation, directory attributes, parent linkage, references, and FCB-table insertion.

`CdInitializeFcbFromFileContext` initializes file FCBs from dirent enumeration results. It sets size/allocation, readonly/hidden attributes, creation time, XA/raw extent state, loads all extents into the MCB, marks the FCB initialized, links to the parent, increments parent references, and inserts into the FCB table.

`CdDeleteFcb` tears down per-stream contexts, MCBs, nonpaged state, prefix buffers, short-name prefix storage, file locks, oplocks, internal VCB pointers, and type-specific FCB allocations. System FCB deletion decrements VCB reference counts.

`CdCreateCcb` and `CdDeleteCcb` allocate, initialize, and free per-open CCBs, including any search-expression buffer.

## IRP Context Lifecycle

`CdCreateIrpContext` validates filesystem-device-object IRP patterns, reuses an IRP context from a private lookaside list when available, initializes operation fields, real device, VCB pointer, major/minor codes, and wait/force-post flags.

`CdCleanupIrpContext` restores thread context, frees allocated I/O context, and either returns the IRP context to the private lookaside list or frees it. For posted/retry work it clears the appropriate transient flags.

`CdInitializeStackIrpContext` builds a stack-resident IRP context for close processing from a lightweight context.

## Teardown and Tables

`CdTeardownStructures` walks from a starting FCB toward the root, deleting internal streams and unreferenced FCBs until it reaches a live node. It uses a top-level teardown flag to prevent recursion, removes prefixes, unlinks from parent queues, removes FCB-table entries, decrements parent references, and returns whether the starting FCB was removed.

`CdLookupFcbTable`, `CdGetNextFcb`, `CdFcbTableCompare`, `CdAllocateFcbTable`, and `CdDeallocateFcbTable` wrap the RTL generic table keyed by `FILE_ID`.

## TOC Processing

`CdProcessToc` reads CD TOC data using `IOCTL_CDROM_READ_TOC_EX` with fallback to `IOCTL_CDROM_READ_TOC`, validates returned track bounds, classifies audio/data tracks, hides the data track for CD+ style discs after audio lead-in, and updates the visible TOC length. `CdTocSerial` computes an audio-disc serial number from track addresses.

## Dependencies

This file is the central lifecycle provider for the rest of CDFS. It depends on allocation helpers, VPB spin locks, cache/internal stream creation, raw volume descriptor macros, dirent/path initialization, MCB allocation mapping, device I/O control helpers, FsRtl oplock/file-lock APIs, and global CDFS state.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/strucsup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/verfysup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/verfysup.c

## Purpose

Implements volume verification, FCB operation verification, dismount checks, and VCB dismount mechanics for CDFS.

## Main Entry Points

- `CdPerformVerify`
- `CdCheckForDismount`
- `CdMarkDevForVerifyIfVcbMounted`
- `CdVerifyVcb`
- `CdVerifyFcbOperation`
- `CdDismountVcb`

## Verification

`CdPerformVerify` handles `STATUS_VERIFY_REQUIRED` recovery. It avoids recursive verification for mount/verify FSCTLs, calls `IoVerifyVolume`, reconciles the result with current `VcbCondition`, triggers dismount when the old VCB is no longer valid and only residual references remain, reparses top-level creates after successful remount/wrong-volume outcomes, raises user-induced errors for hard-error UI, and posts the original request back to the FSP when verification succeeds.

`CdVerifyVcb` validates volume state before operations. On removable media, it checks `IOCTL_CDROM_CHECK_VERIFY`, compares media change count, detects raw/empty device outcomes, marks the real device for verify when still mounted, and forces root creates on unmounted/dismounting volumes through the verify path. It raises `STATUS_VERIFY_REQUIRED`, `STATUS_WRONG_VOLUME`, `STATUS_FILE_INVALID`, or `STATUS_VOLUME_DISMOUNTED` as appropriate.

`CdVerifyFcbOperation` is the per-file fast/common operation gate. It rejects most operations on cleaned-up file objects, fails invalid/dismounting volumes, raises verify-required when the real device is marked, allows mounted/mount-in-progress volumes, and raises wrong-volume for not-mounted VCBs in IRP paths. In fast-I/O calls it returns `FALSE` instead of raising.

## Dismount

`CdCheckForDismount` acquires the VCB exclusively, drains pending closes, starts dismount when user references are residual or force is requested, and deletes the VCB when dismount is already in progress and both VCB and VPB references allow it.

`CdDismountVcb` marks dismount in progress, frees XA sector state, removes internal FCB references, purges volume cache, drains close queues, drops the mount reference, and coordinates VPB replacement/deletion under the VPB spin lock. It may swap in the saved VPB so the real device can be remounted while the old VCB survives due to references.

`CdMarkDevForVerifyIfVcbMounted` safely marks the real device for verify only if the VCB’s VPB is still the active VPB for the device; otherwise it records that the VPB is no longer on the device.

## Dependencies

Uses CDFS global/VCB locks, VPB spin-lock protocol, device verify flags, mount/dismount state, close-queue draining, purge logic, IoVerifyVolume, and CDFS exception/posting helpers.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/verfysup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/volinfo.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/volinfo.c

## Purpose

Implements `IRP_MJ_QUERY_VOLUME_INFORMATION` handling for CDFS.

## Main Entry Points

- `CdCommonQueryVolInfo`
- `CdQueryFsVolumeInfo`
- `CdQueryFsSizeInfo`
- `CdQueryFsDeviceInfo`
- `CdQueryFsAttributeInfo`
- `CdQueryFsSectorSizeInfo` for Windows 8+ builds

## Key Behavior

`CdCommonQueryVolInfo` decodes the file object, rejects unopened file objects, acquires the VCB shared, verifies the VCB, dispatches by `FsInformationClass`, records bytes written as original length minus remaining length, releases the VCB, and completes the IRP.

Supported classes are:

- `FileFsSizeInformation`
- `FileFsVolumeInformation`
- `FileFsDeviceInformation`
- `FileFsAttributeInformation`
- `FileFsSectorSizeInformation` when built for NTDDI Windows 8 or later

## Query Helpers

`CdQueryFsVolumeInfo` returns volume creation time from the volume DASD FCB, VPB serial number, `SupportsObjects = FALSE`, and as much of the VPB volume label as fits. It returns `STATUS_BUFFER_OVERFLOW` for truncated labels.

`CdQueryFsSizeInfo` reports total allocation units from the volume DASD allocation size, zero available units, one sector per allocation unit, and 2048-byte sectors.

`CdQueryFsDeviceInfo` reports target device characteristics and `FILE_DEVICE_CD_ROM`.

`CdQueryFsAttributeInfo` reports read-only CDFS attributes: case-sensitive search, read-only volume, and open-by-file-ID support. Joliet volumes also report `FILE_UNICODE_ON_DISK` and a shorter maximum component length. The filesystem name returned is `CDFS`, truncated with `STATUS_BUFFER_OVERFLOW` if needed.

`CdQueryFsSectorSizeInfo` delegates to `FsRtlGetSectorSizeInformation` on the real device and consumes the sector-size-info structure length on success.

## Dependencies

Uses CDFS file-object decoding, VCB verification, VPB volume metadata, volume DASD FCB sizing, VCB Joliet state, target/real device objects, and standard Windows filesystem information structures.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/volinfo.c -->