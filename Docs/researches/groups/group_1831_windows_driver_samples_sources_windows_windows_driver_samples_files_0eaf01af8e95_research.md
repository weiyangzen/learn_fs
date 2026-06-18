# Group Research: group_1831_windows_driver_samples_sources_windows_windows_driver_samples_files_0eaf01af8e95

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/windows-driver-samples`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/close.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/close.c

CDFS close handling for FSD/FSP dispatch, including immediate, async, and delayed close processing.

Key responsibilities:
- Implements `CdCommonClose`, the FSD close entry point.
- Implements `CdFspClose`, the worker-side queue drain routine.
- Maintains async and delayed close queues through `CdQueueClose` and `CdRemoveClose`.
- Deletes CCBs once file objects are decoded.
- Decrements FCB/user references and calls teardown logic through `CdCommonClosePrivate`.
- Starts the close work item when async work exists or delayed-close thresholds need reduction.
- Coordinates possible VCB teardown/dismount after the last cleanup/user references disappear.

Important behavior:
- Closes always complete and return `STATUS_SUCCESS` to the I/O manager once CDFS has captured the needed FCB/reference data.
- Delayed close is used for last references to user files/directories on mounted volumes, preserving recently used FCBs up to `CdData` thresholds.
- Async close is used when resources cannot be acquired without violating close recursion/locking constraints.
- Delayed close stores a compact `IRP_CONTEXT_LITE`; async close reuses the original `IRP_CONTEXT` with the FCB and user-reference count packed into existing fields.
- `CdFspClose(Vcb)` drains all close items for a specific volume; `CdFspClose(NULL)` drains async work first and then delayed work only while reduction is active.
- VCB teardown checks are deliberately repeated under `CdData` synchronization because initial condition checks are unsafe but cheap.

Dependencies:
- Depends on CDFS object decoding, CCB allocation/free, VCB/FCB resources, reference accounting, teardown, dismount checks, `CdData` global close queues, and the filesystem work item `CdData.CloseItem`.
- Uses Windows filesystem entry/exit bracketing via `FsRtlEnterFileSystem` and `FsRtlExitFileSystem`.

Notable risks:
- The async queue encodes close state in `IrpContext->Irp` and `IrpContext->ExceptionStatus`, which is compact but easy to misuse.
- The delayed-close mechanism intentionally keeps FCB references alive, so volume dismount can be deferred until queue draining catches up.
- Correct lock ordering is central: the file comments explicitly call out recursive close and potential VCB/FCB acquisition-order issues.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/create.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/create.c

CDFS create/open implementation for volume, file, directory, relative, name-based, and file-ID opens.

Key responsibilities:
- Implements `CdCommonCreate`, the common FSD/FSP create path.
- Rejects unsupported create modes: paging file opens, target-directory opens, EAs, true create operations, and Win7+ `FILE_OPEN_REQUIRING_OPLOCK`.
- Normalizes and stores full names in the file object with `CdNormalizeFileNames`.
- Handles volume DASD opens, open-by-file-ID, prefix-table matches, path-table directory traversal, short-name lookup, and final directory scans.
- Creates or finds FCBs and inserts prefix entries for exact-case and case-insensitive lookup.
- Completes user opens through `CdCompleteFcbOpen`, including access checks, oplock checks, share access, CCB creation, file-object setup, cache flags, and reference/cleanup count updates.

Important behavior:
- CDFS is read-only for normal file creation semantics: only `FILE_OPEN` and `FILE_OPEN_IF` are accepted for existing files/directories/volumes.
- Empty name plus no file ID is treated as a volume open and acquires the VCB exclusively.
- `CdNormalizeFileNames` handles double leading backslashes, trailing backslashes, related file objects, open-by-ID validation, wildcard rejection, and retry behavior through `IRP_CONTEXT_FLAG_FULL_NAME`.
- Directory discovery primarily uses the ISO path table; file discovery uses directory enumeration. A directory found in a directory scan but absent from the path table is treated as disk corruption.
- Short-name matches are supported by decoding embedded short-name offsets and then resolving back to long-name/path-table state when needed.
- `CdOpenByFileId` reconstructs parent directory state from encoded path-table and dirent offsets, validating offsets against path-table and directory-stream bounds.
- `CdCompleteFcbOpen` expands `MAXIMUM_ALLOWED`, handles exclusive volume-lock opens by purging and forcing delayed closes, checks batch/exclusive oplocks, checks share access, and assigns `FO_CACHE_SUPPORTED` or `FO_NO_INTERMEDIATE_BUFFERING`.

Dependencies:
- Depends on CDFS FCB table, prefix table, path table, directory enumeration contexts, file-ID encoding helpers, CCB allocation, VCB/FCB locking, oplock callbacks, share-access APIs, and volume purge/close-drain support.
- Uses `try/finally` cleanup heavily to release FCBs, VCBs, compound path entries, and file contexts across normal, pending, and exceptional exits.

Notable risks:
- The file is lock-order sensitive: it often references an FCB under the VCB lock, drops the VCB, acquires the FCB, then reacquires the VCB to adjust references.
- File-object name buffers are mutated and may be reallocated; retry correctness depends on `IRP_CONTEXT_FLAG_FULL_NAME`.
- Open-by-ID trusts encoded offsets only after explicit validation; malformed media can otherwise drive unusual path-table and directory scans.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/devctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/devctrl.c

CDFS filesystem device-control dispatch support for volume opens.

Key responsibilities:
- Implements `CdCommonDevControl`.
- Accepts device-control requests only on `UserVolumeOpen` file objects.
- Verifies the VCB for TOC reads and disk-type queries.
- Handles `IOCTL_CDROM_DISK_TYPE` directly from `Vcb->DiskFlags`.
- Passes other accepted IOCTLs through to the target CD-ROM device object.
- Provides `CdDevCtrlCompletionRoutine` to preserve pending state on pass-through completion.

Important behavior:
- Non-volume opens receive `STATUS_INVALID_PARAMETER`.
- `IOCTL_CDROM_DISK_TYPE` requires an output buffer large enough for `CDROM_DISK_DATA`; otherwise it returns `STATUS_BUFFER_TOO_SMALL`.
- Pass-through requests copy the current IRP stack location to the next stack location and call `IoCallDriver`.
- After passing the IRP down, CDFS completes only its IRP context, not the IRP itself.

Dependencies:
- Depends on `CdDecodeFileObject`, `CdVerifyVcb`, `CdCompleteRequest`, and the mounted VCB target device object.
- Uses normal Windows completion-routine pending propagation via `IoMarkIrpPending`.

Notable risks:
- The accepted IOCTL surface is intentionally narrow at the filesystem layer; most semantics are delegated to the lower CD-ROM stack.
- The completion routine returns `STATUS_SUCCESS`, so lower-driver completion continues normally after pending-state fixup.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/devctrl.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/deviosup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/cdfs/deviosup.c

Low-level CDFS device-I/O support for sector reads/writes, raw XA/audio reads, directory-sector caching, MDL handling, associated IRPs, and completion routines.

Key responsibilities:
- Defines `IO_RUN`, the internal description of disk extents, user buffers, transfer buffers, MDLs, and associated IRPs.
- Implements cooked noncached reads with `CdNonCachedRead`.
- Implements raw/XA/audio noncached reads with `CdNonCachedXARead`.
- Implements volume DASD writes with `CdVolumeDasdWrite`.
- Provides synchronous sector reads for mount/verify via `CdReadSectors`.
- Builds MDLs for user buffers with `CdCreateUserMdl`.
- Sends internal/external device controls with `CdPerformDevIoCtrlEx` and `CdPerformDevIoCtrl`.
- Prepares and finishes transfer buffers with `CdPrepareBuffers`, `CdPrepareXABuffers`, and `CdFinishBuffers`.
- Issues single and multiple lower-device I/O through `CdSingleAsync`, `CdMultipleAsync`, and `CdMultipleXAAsync`.
- Handles sync/async completion for single and associated IRPs.
- Implements a directory sector cache with `CdReadDirDataThroughCache` and `CdFreeDirCache`.
- Synthesizes pseudo path-table/root-directory data for audio disks with `CdReadAudioSystemFile`.
- Converts LBN to MSF with `CdLbnToMmSsFf`.
- Reuses an existing IRP to send a lower-device flush through `CdHijackIrpAndFlushDevice`.

Important behavior:
- Cooked reads operate in 2048-byte sectors and split work into up to `MAX_PARALLEL_IOS` runs.
- Unaligned cooked reads allocate nonpaged scratch buffers and copy the requested bytes back after the lower read completes.
- Async cooked reads are not allowed for unaligned or too-large multi-pass cases; those paths raise/post with `STATUS_CANT_WAIT`.
- XA/raw reads prepend synthetic RIFF/audio headers and translate raw 2352-byte sector offsets to cooked 2048-byte device offsets.
- XA raw reads are synchronous only and can retry Mode2 Form2 reads as Yellow Book Mode2 for known malformed media cases.
- `CdFinishBuffers` walks runs backward so shifting/copying within the user buffer does not overwrite later data.
- The VCB may cache one XA sector (`XASector`/`XADiskOffset`) to satisfy later partial raw-sector reads.
- Directory FCB reads can be satisfied through a chunked sector cache, with LRU replacement and synchronous lower reads into cache chunks.
- Audio disks get synthesized path-table and root-directory entries for tracks rather than ordinary ISO directory data.
- Async completion transfers resource ownership from the issuing thread to the I/O context so locks can be released safely after completion.

Dependencies:
- Depends on CDFS allocation lookup, VCB geometry/limits, TOC data, XA/audio constants, cache resources, I/O context allocation, FCB node types, target device object, and Windows IRP/MDL APIs.
- Uses `IoMakeAssociatedIrp`, partial MDLs, completion routines, `KeWaitForSingleObject`, `KeFlushIoBuffers`, `MmProbeAndLockPages`, and `MmBuildMdlForNonPagedPool`.

Notable risks:
- Buffer, MDL, and associated-IRP ownership is intricate; cleanup depends on `CleanupRunCount`, `SavedIrp`, `TransferMdl`, and whether the transfer buffer is the original user MDL or an allocated scratch page.
- Raw-sector math has separate raw/cooked offsets and 32-bit fast paths, making boundary correctness important.
- Directory-sector cache reads reuse a VCB-owned IRP and MDL and must always unlock/free MDLs and release cache resources.
- Async completion must release resources and free I/O contexts exactly once; resource-owner pointer handoff is subtle but required for thread lifetime safety.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/cdfs/deviosup.c -->