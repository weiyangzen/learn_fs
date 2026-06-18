# Group Research: group_1853_windows_driver_samples_sources_windows_windows_driver_samples_files_5895a84907c0

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/simrep/simrep.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/simrep/simrep.c

## Scope And Role

`simrep.c` is a Windows Filter Manager mini-filter sample that demonstrates simulated reparse behavior. It redirects creates from a configured `OldMapping` path to a configured `NewMapping` path by replacing the target `FILE_OBJECT->FileName` and completing the create with `STATUS_REPARSE`.

The file is not a full namespace virtualization layer. Its own header explicitly frames it as a sample for returning `STATUS_REPARSE`; callers and upper filters can still observe the redirected target after create/rename/link completion.

Read coverage: full file, 3,177 lines.

## Main State

The central global is `SIMREP_GLOBAL_DATA Globals`, containing:

- `Filter`: registered `PFLT_FILTER`.
- `Mapping.OldName` and `Mapping.NewName`: registry-driven redirect path pair.
- `ReplaceFileNameFunction`: dynamically resolved `IoReplaceFileObjectName`, or fallback `SimRepReplaceFileObjectName`.
- `QueryDirectoryFileFunction`: dynamically resolved `FltQueryDirectoryFile`, or fallback callback-data implementation.
- `RemapRenamesAndLinks`: registry-controlled option that changes callback registration and enables name-provider behavior.
- `DebugLevel` in DBG builds.

Pool tags are split between string allocations (`SIMREP_STRING_TAG`) and registry value buffers (`SIMREP_REG_TAG`).

## Registration And Initialization

`DriverEntry` initializes pool NX opt-in, default globals, dynamically resolves `IoReplaceFileObjectName` and `FltQueryDirectoryFile`, reads configuration, registers with Filter Manager, and starts filtering.

There are two registration tables:

- `FilterRegistration`: create and network-query-open callbacks only.
- `FilterRegistrationWithRename`: create, network-query-open, set-information callbacks, plus pass-through name-provider callbacks.

`SimRepSetConfiguration` opens the service `Parameters` key using `IoOpenDriverRegistryKey` when available, with a `ZwOpenKey` fallback for older systems. It reads:

- `DebugLevel` in DBG builds.
- `RemapRenamesAndLinks`.
- `OldMapping`.
- `NewMapping`.

It validates that old/new mappings agree on trailing-backslash semantics, preventing a directory mapping from being paired with a file-style mapping or vice versa.

## Create Redirection Flow

`SimRepPreCreate` is the main IRP create path:

1. Ignores paging-file opens, volume opens, and open-by-file-id creates.
2. Avoids `SL_OPEN_TARGET_DIRECTORY` reparsing unless rename/link remapping is enabled.
3. Gets opened name information, using `FLT_FILE_NAME_QUERY_FILESYSTEM_ONLY` for target-directory opens to avoid polluting the name cache.
4. Parses the name.
5. Calls `SimRepMungeName` to replace the old mapping prefix with the new mapping prefix.
6. Replaces the target file object's name through `Globals.ReplaceFileNameFunction`.
7. Completes the operation with `STATUS_REPARSE` and `IO_REPARSE`.

The mapping comparison is prefix-based but path-boundary aware. `SimRepCompareMapping` treats a match as exact if the post-volume path length equals the mapping length, or as a child match if the next character is `\`. This avoids treating `\a\b` as matching `\a\bc`.

## Network Query Open Flow

`SimRepPreNetworkQueryOpen` handles `IRP_MJ_NETWORK_QUERY_OPEN`, which arrives as Fast I/O. Since Fast I/O cannot return `STATUS_REPARSE`, the callback only checks whether the path matches the old mapping. If it does, it returns `FLT_PREOP_DISALLOW_FASTIO`, forcing the I/O manager to reissue the operation as a normal IRP create where `SimRepPreCreate` can return `STATUS_REPARSE`.

It rejects/ignores paging files, volume opens, file-id opens, and asserts target-directory opens should not arrive on this path.

## Rename And Hardlink Remapping

When `RemapRenamesAndLinks` is enabled, `SimRepPreSetInformation` handles:

- `FileRenameInformation`
- `FileRenameInformationEx`
- `FileLinkInformation`

It ignores all other listed information classes and asserts on unknown ones in test builds.

The callback obtains destination name information via `FltGetDestinationFileNameInformation` using `FLT_FILE_NAME_REQUEST_FROM_CURRENT_PROVIDER`, then parses the result. Stream destinations are passed through. For matching destinations, it builds a replacement rename/link information buffer with a munged absolute target path and issues `FltSetInformationFile` itself, then completes the original operation.

A special exact-match fallback handles destinations that overlap the old mapping exactly, because parent-directory name resolution may not reparse in that case.

## Name Provider Support

Rename/link support requires SimRep to participate in name resolution. The file implements a pass-through name provider:

- `SimRepGenerateFileName` clears `FLT_FILE_NAME_REQUEST_FROM_CURRENT_PROVIDER` to avoid recursion, then delegates name retrieval below itself using `FltGetFileNameInformation` or `FltGetFileNameInformationUnsafe`.
- It copies the returned name into the provided `FLT_NAME_CONTROL`.
- It only allows caching once `FileObject->FsContext` is non-NULL.

`SimRepNormalizeNameComponent` and Vista+ `SimRepNormalizeNameComponentEx` open the parent directory, query a single `FileNamesInformation` entry for the component, and return the long/normalized component name. The Vista+ variant propagates transaction context from the target file object through `FltCreateFileEx2`.

`SimRepQueryDirectoryFile` calls `FltQueryDirectoryFile` when exported; otherwise it builds and performs an `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_QUERY_DIRECTORY` callback-data request manually.

## Resource Handling

The file uses explicit allocation/free helpers for `UNICODE_STRING` values. Configuration cleanup frees partially initialized mapping strings on failure. Unload unregisters the filter and frees global mapping strings.

Name/query structures are released with `FltReleaseFileNameInformation`; directory/file objects from normalization are closed/dereferenced on cleanup paths.

The fallback `SimRepReplaceFileObjectName` either reuses the existing file-name buffer if large enough or allocates a new one and replaces the file object's name buffer directly. The header notes this fallback can trigger Driver Verifier pool-leak complaints on systems without `IoReplaceFileObjectName`.

## Important Risks And Edge Cases

- Debug-only null dereference risk: in the `SL_OPEN_TARGET_DIRECTORY` branch of `SimRepPreCreate`, the debug trace references `&nameInfo->Name` immediately after clearing the flag, before `nameInfo` is populated. With the relevant debug trace flag enabled, this can dereference an invalid `UNICODE_STRING`.
- Mapping semantics are intentionally simple and do not account for NT short names.
- The sample does not honor `FILE_OPEN_REPARSE_POINT`; it always treats the configured mapping as filter-owned behavior rather than an object that can itself be opened/deleted.
- Open-by-file-id is skipped because the path intent cannot be inferred.
- Rename/link redirection is only consistent when the filter is registered as a name provider; without `RemapRenamesAndLinks`, target-directory opens are deliberately passed through.
- The fallback manual file-object name replacement is compatibility code with verifier/unload caveats.
- The directory-query fallback manually constructs callback data and depends on synchronous completion semantics.

## Integration Points

This file integrates deeply with Filter Manager and NT kernel APIs:

- Registration/start: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`.
- Name queries: `FltGetFileNameInformation`, `FltParseFileNameInformation`, `FltGetDestinationFileNameInformation`.
- Reparse behavior: target file-object name replacement plus `STATUS_REPARSE` / `IO_REPARSE`.
- Rename/link replay: `FltSetInformationFile`.
- Name provider callbacks for generated and normalized names.
- Registry configuration through `IoOpenDriverRegistryKey` or `ZwOpenKey`.

## Testing Notes

Useful focused tests would cover:

- Create under old mapping returns `STATUS_REPARSE` and targets new mapping.
- Non-matching creates pass through.
- Boundary case `\oldpath2` does not match mapping `\oldpath`.
- Case-sensitive vs case-insensitive opens.
- Fast I/O network query open under old mapping returns `FLT_PREOP_DISALLOW_FASTIO`.
- `SL_OPEN_TARGET_DIRECTORY` behavior with `RemapRenamesAndLinks` both disabled and enabled.
- Rename/link destination remapping for old mapping exact match, child match, new mapping overlap, stream names, and non-matching destinations.
- Downlevel behavior where `IoReplaceFileObjectName` or `FltQueryDirectoryFile` is unavailable.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/simrep/simrep.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/swapBuffers/swapBuffers.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/swapBuffers/swapBuffers.c

## Scope And Role

`swapBuffers.c` is a Windows Filter Manager mini-filter sample showing how to replace user I/O buffers with filter-owned buffers for read, write, and directory-control operations, then copy data back or free state in post-operation callbacks.

The sample is mostly about correct buffer handling across IRP, Fast I/O, MDL, system-buffer, arbitrary user-buffer, cached, and non-cached paths.

Read coverage: full file, 2,325 lines.

## Main State

Global state includes:

- `gFilterHandle`: registered filter handle.
- `Pre2PostContextList`: nonpaged lookaside list for passing state from pre-op to post-op.

Key structures:

- `VOLUME_CONTEXT`: per-volume context with display name and sector size.
- `PRE_2_POST_CONTEXT`: holds the referenced volume context and swapped buffer pointer for post-op cleanup.

Pool tags identify buffer swaps, volume contexts, names, and pre/post state.

## Registration And Volume Setup

The filter registers callbacks for:

- `IRP_MJ_READ`: `SwapPreReadBuffers` / `SwapPostReadBuffers`
- `IRP_MJ_WRITE`: `SwapPreWriteBuffers` / `SwapPostWriteBuffers`
- `IRP_MJ_DIRECTORY_CONTROL`: `SwapPreDirCtrlBuffers` / `SwapPostDirCtrlBuffers`

`InstanceSetup` attaches broadly to volumes. It allocates a volume context, reads volume properties, stores a sector size with a minimum of `0x200`, and tries to derive a display name:

1. Prefer DOS name from `IoVolumeDeviceToDosName`.
2. Fall back to real device name or filesystem device name from `FLT_VOLUME_PROPERTIES`.
3. Append `:` to fallback names for display.

`CleanupVolumeContext` frees the allocated name buffer. `InstanceQueryTeardown` always allows detach.

`DriverEntry` initializes pool NX opt-in, reads `DebugFlags`, initializes the lookaside list, registers the filter, and starts filtering. `FilterUnload` unregisters and deletes the lookaside list.

## Read Buffer Swap Flow

`SwapPreReadBuffers`:

1. Skips zero-length reads.
2. Gets the volume context.
3. Rounds non-cached read length up to the volume sector size.
4. Allocates an aligned nonpaged replacement buffer with `FltAllocatePoolAlignedWithTag`.
5. Builds an MDL for IRP operations, but not Fast I/O.
6. Allocates a pre/post context.
7. Replaces `ReadBuffer` and `MdlAddress`, calls `FltSetCallbackDataDirty`, and requests a post callback.

`SwapPostReadBuffers`:

- If the read failed or returned zero bytes, it only cleans up.
- If the original request has an MDL, it maps it with `MmGetSystemAddressForMdlSafe`.
- If the original buffer is a system buffer or Fast I/O buffer, it copies directly with exception handling.
- For arbitrary user buffers without MDLs, it calls `FltDoCompletionProcessingWhenSafe` and delegates to `SwapPostReadBuffersWhenSafe`.

`SwapPostReadBuffersWhenSafe` locks the user buffer with `FltLockUserBuffer`, maps the resulting MDL, copies data from the swapped buffer, and frees all pre/post state.

## Directory Control Buffer Swap Flow

`SwapPreDirCtrlBuffers` handles query-directory buffers:

1. Skips zero-length query-directory buffers.
2. Gets the volume context.
3. Allocates a zeroed nonpaged replacement buffer with `ExAllocatePoolZero`.
4. Always builds an MDL because directory-control operations are IRP-based.
5. Replaces `DirectoryBuffer` and `MdlAddress`, marks callback data dirty, stores pre/post state, and asks for a post callback.

`SwapPostDirCtrlBuffers` mirrors the read post path, with MDL/system/Fast I/O/arbitrary-user-buffer handling and safe-post fallback.

A notable sample behavior: for directory-control copy-back, it copies the original query buffer length rather than `IoStatus.Information`. The comments say this works around a FASTFAT bug where the information length can be short, but also call out the security implication: the replacement buffer must be clean before calling the filesystem to avoid exposing stale data. This implementation uses `ExAllocatePoolZero`, satisfying that sample constraint.

`SwapPostDirCtrlBuffersWhenSafe` performs the safe-IRQL arbitrary-buffer copy-back after `FltLockUserBuffer`.

## Write Buffer Swap Flow

`SwapPreWriteBuffers`:

1. Skips zero-length writes.
2. Gets the volume context.
3. Rounds non-cached write length up to sector size.
4. Allocates an aligned replacement buffer.
5. Builds an MDL for IRP operations.
6. Resolves the original write buffer from its MDL when present, otherwise uses `WriteBuffer`.
7. Copies user data into the replacement buffer inside `try/except`.
8. Replaces `WriteBuffer` and `MdlAddress`, marks callback data dirty, stores pre/post state, and requests a post callback.

If it cannot map the original MDL or copying raises an exception, it completes the operation with failure from the pre-op path.

`SwapPostWriteBuffers` does not copy data back. It logs, frees the aligned swapped buffer, releases the volume context, frees the lookaside context, and finishes processing.

## Resource Handling

The file consistently cleans up allocations when a pre-op path decides not to request a post callback. Post callbacks own cleanup once `FLT_PREOP_SUCCESS_WITH_CALLBACK` is returned.

Important ownership rules visible in the implementation:

- Filter-allocated aligned read/write buffers are freed with `FltFreePoolAlignedWithTag`.
- Directory-control buffers allocated with `ExAllocatePoolZero` are freed with `ExFreePool`.
- MDLs allocated for replacement buffers are generally left for Filter Manager to free after swapped I/O completion, matching the sample comments.
- Volume contexts are acquired in pre-op and released in post-op because post-op may run at DPC where acquiring the context would be unsafe, but releasing is allowed.
- The pre/post context is allocated from and returned to `Pre2PostContextList`.

## Important Risks And Edge Cases

- The read/write non-cached path rounds the allocated buffer length up to sector size. For writes, the code copies `writeLen` bytes from the original buffer after rounding. If the original supplied buffer is only the unrounded length, this sample pattern can read past the logical caller buffer unless the I/O contract guarantees sector-sized backing for non-cached writes.
- Directory-control post deliberately copies the full original query length rather than `IoStatus.Information`. This depends on the swapped buffer being zero-filled, which this file does, but the pattern is risky if reused with uninitialized buffers.
- The code asserts no chained MDLs for read/write original buffers. It is sample-level behavior and may not cover all production stack cases.
- Fast I/O paths avoid replacement MDLs because the Fast I/O interface has no MDL parameter, so correctness depends on direct buffer validity and exception handling.
- Arbitrary user-buffer copy-back depends on `FltDoCompletionProcessingWhenSafe`; if safe posting is unavailable, the operation is failed.
- Logging is controlled by `DebugFlags` but defaults to disabled.

## Integration Points

The file demonstrates several Filter Manager buffer APIs and kernel memory APIs:

- `FltAllocatePoolAlignedWithTag` / `FltFreePoolAlignedWithTag`.
- `FltSetCallbackDataDirty`.
- `FltDoCompletionProcessingWhenSafe`.
- `FltLockUserBuffer`.
- `FltGetVolumeContext`, `FltSetVolumeContext`, `FltReleaseContext`.
- `MmGetSystemAddressForMdlSafe`, `IoAllocateMdl`, `MmBuildMdlForNonPagedPool`.
- Registry debug flag reads through `ZwOpenKey` and `ZwQueryValueKey`.

## Testing Notes

Useful focused tests would cover:

- Cached and non-cached read/write buffer swaps.
- Zero-length read/write/query-directory pass-through.
- IRP path with replacement MDL creation.
- Fast I/O path without replacement MDL.
- Original buffer with MDL, system buffer, and arbitrary user buffer.
- Safe-post copy-back path via `FltDoCompletionProcessingWhenSafe`.
- Failure paths for allocation, MDL allocation, MDL mapping, and user-buffer locking.
- Directory-control copy-back with short `IoStatus.Information` and zero-filled tail behavior.
- Multiple instances/volumes and volume-context cleanup on detach/unload.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/swapBuffers/swapBuffers.c -->