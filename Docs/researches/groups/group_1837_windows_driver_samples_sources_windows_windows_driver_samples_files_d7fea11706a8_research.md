# Group Research: group_1837_windows_driver_samples_sources_windows_windows_driver_samples_files_d7fea11706a8

Subset scope confirmed in `Docs/research_subset_a.md`: `sources/windows/windows-driver-samples` is included in Subset A. Both listed FastFAT files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/deviosup.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/deviosup.c

Read fully: 3,801 lines.

This file implements FastFAT’s low-level device I/O support. It is the bridge between filesystem-level VBO operations and lower storage-stack LBO reads/writes, handling noncached I/O, paging-file I/O, multi-run request splitting, MDL setup, completion routines, device control requests, and disk accounting.

Core responsibilities:
- Translate file allocation runs from the FCB/DCB MCB into disk I/O runs.
- Dispatch single-run and multi-run read/write IRPs to `Vcb->TargetDeviceObject`.
- Manage synchronous versus asynchronous completions through `FAT_IO_CONTEXT`.
- Lock, map, and snapshot user buffers when FastFAT cannot rely on I/O manager direct-buffer setup.
- Support special paging-file I/O paths that cannot use the normal cached/noncached flow.
- Handle partial-sector noncached reads using an intermediate nonpaged buffer.
- Issue internal storage IOCTLs such as media-removal prevention.
- Build efficient zero MDLs for writing repeated zero pages.

Major routines:
- `FatPagingFileIo` maps paging-file VBOs through `Fcb->Mcb`, sends one IRP directly for a single contiguous run, or splits multi-run requests into associated IRPs and partial MDLs. It sets `SL_OVERRIDE_VERIFY_VOLUME` because paging I/O cannot tolerate normal verify processing. It uses a reserve MDL fallback and can reuse the master IRP synchronously when associated IRP allocation is constrained.
- `FatUpdateDiskStats` charges disk I/O to an originating process/thread on Windows 8+ builds, distinguishing reads and writes and avoiding double-accounting recursive/cache-manager activity.
- `FatNonCachedIo` is the main noncached read/write path. It locks the user buffer, optionally sets up a completion-time zeroing MDL for trailing bytes beyond `UserByteCount`, finds allocation runs, chooses a single-run fast path through `FatSingleAsync`, or builds an `IO_RUN` array and dispatches `FatMultipleAsync`.
- `FatNonCachedNonAlignedRead` handles non-sector-aligned reads by reading the leading and trailing sectors into a cache-aligned nonpaged buffer, copying only requested bytes to the user buffer, then delegating the aligned middle to `FatNonCachedIo`.
- `FatMultipleAsync` creates associated IRPs for each run, builds partial MDLs from the master MDL, installs sync or async multi-completion routines, handles write-through and override-verify flags, transfers async resource ownership when needed, and issues all lower-device IRPs.
- `FatSingleAsync` prepares the original IRP for a single contiguous lower-device request and installs either sync or async completion logic.
- `FatSingleNonAlignedSync` temporarily replaces the IRP MDL with an MDL over a nonpaged bounce buffer, sends a synchronous single-sector request, waits, then restores the original MDL.
- `FatWaitSync` waits on and clears the synchronous completion event in `IrpContext->FatIoContext`.
- Completion routines include `FatMultiSyncCompletionRoutine`, `FatMultiAsyncCompletionRoutine`, `FatSingleSyncCompletionRoutine`, `FatSingleAsyncCompletionRoutine`, `FatPagingFileCompletionRoutine`, and `FatPagingFileCompletionRoutineCatch`.
- `FatPagingFileErrorHandler` tries to mark the volume dirty with recovery requested after paging-file media errors, using a critical work item when possible.
- `FatLockUserBuffer`, `FatMapUserBuffer`, and `FatBufferUserBuffer` provide FastFAT’s explicit MDL/user-buffer handling.
- `FatToggleMediaEjectDisable` sends `IOCTL_DISK_MEDIA_REMOVAL` and tracks `VCB_STATE_FLAG_REMOVAL_PREVENTED`.
- `FatPerformDevIoCtrl` builds and waits for internal or external device-control IRPs, with optional verify override.
- `FatBuildZeroMdl` constructs an MDL that maps many pages to FastFAT’s single zero page, reducing memory needed for zero writes.

Important implementation details:
- The file treats allocation lookup failure for paging-file I/O as fatal corruption and bugchecks, because paging-file mappings are expected to be resident and valid.
- Multi-run paging I/O has careful master-IRP lifetime control: `AssociatedIrp.IrpCount` is manipulated so the master cannot complete before all child I/O is launched or drained.
- Async completion releases held resources, updates outstanding async-write counters, marks the master IRP pending, and frees the `FAT_IO_CONTEXT`.
- `STATUS_VERIFY_REQUIRED` is reposted only for suitable top-level async IRPs so volume verification can happen outside recursive completion context.
- `FatDoCompletionZero` zeroes a completion-time MDL only after successful I/O, then frees the MDL.
- Disk statistics are updated both for FastFAT per-volume counters and Windows process counter paths when enabled.
- The lower I/O dispatch macro currently maps directly to `IoCallDriver`, but keeps a named abstraction point for low-level read/write routing.

Research relevance:
This file is a compact study of Windows filesystem noncached I/O mechanics: MCB-to-LBO translation, associated IRPs, partial MDLs, paging-file constraints, completion-routine ownership, volume-verify handling, and storage-stack IOCTL issuance.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/deviosup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dirctrl.c -->
# File Research: sources/windows/windows-driver-samples/filesys/fastfat/dirctrl.c

Read fully: 1,608 lines.

This file implements FastFAT directory-control dispatch. It handles `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`, including wildcard query template setup, short-name and long-name matching support, output buffer packing for multiple Windows directory information classes, FAT timestamp conversion, and registration of directory-change notifications.

Core responsibilities:
- Dispatch directory-control IRPs from FSD entry to common worker logic.
- Validate directory opens and query parameters.
- Maintain per-handle enumeration state in the CCB.
- Convert query patterns into uppercase Unicode and OEM/8.3 forms.
- Iterate matching FAT directory entries with `FatLocateDirent`.
- Format directory entries into caller-selected information structures.
- Register change-notification requests through FsRtl notify support.

Major routines:
- `FatFsdDirectoryControl` is the FSD dispatch entry. It enters filesystem context, establishes top-level IRP state, creates an IRP context using synchronous wait capability, calls `FatCommonDirectoryControl`, and routes exceptions through FastFAT exception processing.
- `FatCommonDirectoryControl` switches on the minor function and calls `FatQueryDirectory` or `FatNotifyChangeDirectory`; unsupported minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.
- `FatQueryDirectory` is the main enumeration engine. It validates `UserDirectoryOpen`, maps the user buffer, acquires the DCB shared or exclusive depending on initial/restart query state, builds or resets the CCB query template, scans directory entries, formats results, updates `Ccb->OffsetToStartSearchFrom`, and completes the IRP.
- `FatGetDirTimes` fills `FILE_DIRECTORY_INFORMATION` timestamps from a FAT dirent. It always computes last-write time and, in Chicago mode, also derives creation and last-access times with fast paths for common same-date/time cases and defaults to Jan 1, 1980 when FAT fields are zero.
- `FatNotifyChangeDirectory` validates a directory open, acquires the DCB exclusively, ensures the full name is present, rejects delete-pending directories, and passes the request to `FsRtlNotifyFullChangeDirectory`.

Directory query behavior:
- Initial query or restart scan acquires the DCB exclusively because it may mutate the CCB’s search template.
- Subsequent scans use `Ccb->OffsetToStartSearchFrom` unless `SL_INDEX_SPECIFIED` or `SL_RESTART_SCAN` changes the starting VBO.
- Match-all is selected for no filename, empty filename, `*`, or DOS `????????.???`.
- Non-match-all templates are upcased and stored as Unicode, with a best-fit OEM representation when possible.
- If the query contains extended Unicode that cannot map to OEM, FastFAT skips short-name comparison instead of failing for `STATUS_UNMAPPABLE_CHARACTER`.
- For non-wildcard OEM names, the template is converted to an 8.3 constant with `FatStringTo8dot3`.
- Wildcards retain the OEM wildcard string in `Ccb->OemQueryTemplate.Wild`.

Supported output classes:
- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileNamesInformation`
- `FileBothDirectoryInformation`
- `FileIdBothDirectoryInformation`

Output formatting details:
- The routine computes each class’s base structure length using `FIELD_OFFSET(..., FileName[0])`.
- For short-name-only entries, it converts the FAT 8.3 OEM name to Unicode with `RtlOemToUnicodeN`.
- For long-name entries, it copies the located long Unicode filename directly.
- Both-directory classes also include the converted short name in `ShortName`.
- Full-directory classes attempt to read EA size with `FatGetEaLength`; corrupt EA failures are swallowed and reported as `EaSize = 0` so enumeration continues.
- File ID classes fill `FileId` with `FatGenerateFileIdFromDirentAndOffset`.
- `NextEntryOffset` is written into the previous record, entries are quad-aligned, and buffer-overflow behavior follows Windows directory-query rules: a too-large first record may return partial name plus `STATUS_BUFFER_OVERFLOW`, while later non-fitting records are left for the next query.

Important implementation details:
- The code protects user-buffer writes with exception handling because directory queries are not necessarily buffered by the I/O manager.
- `UpdateCcb` is suppressed on exceptions or end-of-directory failures where the enumeration position should not advance.
- `InitialQuery` returning no match produces `STATUS_NO_SUCH_FILE`; later exhaustion produces `STATUS_NO_MORE_FILES`.
- Directory allocation size is reported as zero for directories and cluster-rounded file size for ordinary files.
- Dirents with no attributes are reported as `FILE_ATTRIBUTE_NORMAL`.
- The notify path stores no result buffer itself; once FsRtl owns the IRP, FastFAT completes only the IRP context and returns `STATUS_PENDING`.

Research relevance:
This file shows the Windows FAT directory-control contract in detail: persistent per-handle enumeration state, DOS/Unicode name matching, 8.3 and long-name result formatting, precise query-buffer packing semantics, FAT timestamp adaptation, and FsRtl-based directory notification integration.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/fastfat/dirctrl.c -->