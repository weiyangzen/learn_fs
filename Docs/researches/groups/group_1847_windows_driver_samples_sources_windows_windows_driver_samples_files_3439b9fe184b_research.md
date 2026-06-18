# Group Research: group_1847_windows_driver_samples_sources_windows_windows_driver_samples_files_3439b9fe184b

Scope: `Docs/research_subset_a.md` includes `sources/windows/windows-driver-samples`. Both listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirnotify.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirnotify.c

## Scope

This file implements directory change notification handling for the Windows Driver Samples NameChanger minifilter. The driver exposes a user-visible mapping path while backing it with a separate real path, so directory notifications need to hide, translate, split, merge, buffer, cancel, and reissue notifications depending on the relationship between the watched directory and the user/real mappings.

## APIs and Entry Points

- `NcPreNotifyDirectory` is the main pre-operation callback for `IRP_MJ_DIRECTORY_CONTROL / IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- `NcPostNotifyDirectory` is the post-operation callback that defers pageable work to `NcPostNotifyDirectorySafe` with `FltDoCompletionProcessingWhenSafe`.
- `NcPostNotifyDirectoryReal` is the shared completion engine for user requests and internally generated subrequests.
- `NcDirNotifyTranslateBuffers` rewrites `FILE_NOTIFY_INFORMATION` chains from filesystem-visible names to user-visible names and suppresses entries that should not be exposed.
- `NcBuildSubNotifyRequest` and `NcCleanupSubNotifyRequest` allocate, initialize, and tear down internal notify callback data.
- `NcAllocateNotifyRequestContext` and `NcFreeNotifyRequestContext` manage per-subrequest context references.
- `NcGetDestinationNotifyBuffer` maps or validates notify output buffers for MDL, system-buffered, and direct user-buffer cases.
- `NcNotifyCancelCallback` handles cancellation of a pended user notification.
- `NcNotifyAbort` is shared by cancellation and handle cleanup.
- `NcReissueNotifyRequestWorkerRoutine` reissues an internal notify request from passive-level work item context.
- `NcCloseHandleWorkerRoutine` closes the real mapping parent handle from a work item when inline close is not appropriate.
- `NcStreamHandleContextNotCreate`, `NcStreamHandleContextNotCleanup`, and `NcStreamHandleContextNotClose` initialize and tear down the directory notification portion of a stream-handle context.

## Control Flow

`NcPreNotifyDirectory` classifies the watched path against both mappings with `NcComparePath`:

- If the watched directory is inside either mapping, notifications are already relative to that handle and the request passes through.
- If the watched directory is unrelated to both mappings, the request passes through.
- If it is a non-recursive watch on an ancestor that is not a direct parent, the request passes through.
- If the watch is an ancestor or parent of the real mapping but not the user mapping, the context enters `Filter` mode. The user request is pended, a shadow request is sent to the filesystem, and completions suppress entries under the hidden real mapping.
- If the watch covers a common ancestor or common parent of both mappings, the context enters `Munge` mode. The user request goes to the filesystem with a post callback, and returned real-mapping paths are translated to user-mapping paths.
- If the watch covers the user mapping side but not the real mapping side, the context enters `Merge` mode. The driver opens the real mapping parent, issues one request on the user's handle and one on the real parent handle, then completes the user's pended request when either side produces visible data.

`NcPostNotifyDirectoryReal` processes completions under the stream-handle context lock. It handles cleanup and cancel states first, copies nonvolatile notification data into pool, translates entries through `NcDirNotifyTranslateBuffers`, completes the user request, buffers a second merge completion if no user request is waiting, or records `STATUS_NOTIFY_ENUM_DIR` for the next user call when output was insufficient.

If translation removes every entry from a `Filter` or `Merge` subrequest, the file reuses and reissues that subrequest on a passive-level work item instead of completing the user request with an empty success.

## State and Data Flow

The file depends heavily on `NC_DIR_NOT_CONTEXT` stored in the stream-handle context. Important fields are:

- `Mode`: `Uninitialized`, `Filter`, `Munge`, or `Merge`.
- `CancelSeen` and `CleanupSeen`: prevent stale completions from returning data after cancellation or cleanup.
- `InsufficientBufferSeen`: records that the next caller should receive `STATUS_NOTIFY_ENUM_DIR`.
- `UserRequestName` and `MappingParentName`: saved opened names used to reconstruct full paths from relative notification entries.
- `UserRequest`, `ShadowRequest`, and `MappingRequest`: the pended user request and up to two internal requests.
- `RealParentHandle`, `RealParentFileObject`, and `RealParentCloseWorkItem`: merge-mode access to the real mapping parent.
- `BufferToFree` and `BufferLength`: one held-over translated notification buffer for merge completions that arrive when no user request is pending.

`NcDirNotifyTranslateBuffers` consumes a source `FILE_NOTIFY_INFORMATION` chain, constructs full paths from `OpenedName + "\\" + FileName`, checks overlap with the real mapping, optionally constructs a user-mapping path with `NcConstructPath`, then emits relative names under `UserRequestName`. Output entries are aligned to 8 bytes and linked with `NextEntryOffset`.

## Dependencies

- Includes `nc.h` and uses the NameChanger mapping helpers, especially `NcComparePath`, `NcConstructPath`, `NcGetFileNameInformation`, `NcCreateFileHelper`, `NcSetCancelCompletion`, and `NcExceptionFilter`.
- Uses Filter Manager callback-data APIs: `FltAllocateCallbackData`, `FltFreeCallbackData`, `FltPerformAsynchronousIo`, `FltCompletePendedPreOperation`, `FltDoCompletionProcessingWhenSafe`, `FltReuseCallbackData`, `FltCancelIo`, `FltLockUserBuffer`, `FltClearCancelCompletion`, and context reference APIs.
- Uses MDL and buffer mapping APIs: `MmGetSystemAddressForMdlSafe`, `ProbeForWrite`, and optional `NcGetNewSystemBufferAddress`.
- Uses pool allocation tags `NC_TAG` and `NC_GENERATE_NAME_TAG`.
- Uses Windows notification structures and statuses: `FILE_NOTIFY_INFORMATION`, `STATUS_NOTIFY_CLEANUP`, `STATUS_NOTIFY_ENUM_DIR`, `STATUS_CANCELLED`, `STATUS_INVALID_USER_BUFFER`, and related NTSTATUS values.

## Risks and Edge Cases

- The code intentionally supports only one outstanding user notify request per handle; a second active user request asserts and fails with `STATUS_UNSUCCESSFUL`.
- Notification buffers are treated as untrusted even after copying because they may originate from user-mode memory. The translation helper uses safe arithmetic, explicit bounds checks, and exception handling.
- Zero-length buffers and buffers too small for translated output result in `STATUS_NOTIFY_ENUM_DIR`, requiring callers to rescan.
- Merge mode stores only one deferred buffer. The comments acknowledge cancellation races where multiple completions can arrive, and cancellation is allowed to discard buffered data.
- Cleanup and cancellation are lock-sensitive. `NcNotifyAbort` may drop the stream-handle lock before completing user requests, cancelling child requests, or queueing handle-close work.
- `Munge` mode relies on post-operation processing of the user's original request. During filter draining, the code frees the request context but cannot return `STATUS_NOTIFY_ENUM_DIR` because it no longer owns the request.
- Internal reissue depends on work item allocation and passive-level execution; allocation failure turns into request failure.
- The code has compatibility branches for systems with and without `FltGetNewSystemBufferAddress`; incorrect assumptions about buffer ownership would be dangerous in kernel mode.

## Research Notes

This file is the notification counterpart to NameChanger's create/name mapping logic. It preserves the illusion that the user mapping is the real namespace by either hiding real-path events, rewriting common-ancestor events, or merging notifications from the user's opened path and the real mapping parent.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncdirnotify.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfileinfo.c -->
# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfileinfo.c

## Scope

This file implements NameChanger handling for query-file-information and set-file-information operations whose payloads contain paths, link names, short names, delete disposition, or rename targets. Its purpose is to keep returned names user-visible and to prevent operations that would expose, overwrite, delete, rename, or destabilize the hidden real mapping and the visible user mapping.

## APIs and Entry Points

- `NcPostQueryName` rewrites returned `FileNameInformation`, `FileNormalizedNameInformation`, and `FileAllInformation` names from real mapping paths to user mapping paths.
- `NcPreQueryAlternateName` intercepts alternate-name queries for the mapping itself and returns the user mapping short final component.
- `NcPostQueryHardLinks` rewrites hard-link entries that refer to the real mapping link so they appear under the user mapping parent and name.
- `NcPreSetShortName` blocks short-name changes that target the mapping, mapping ancestors, or names reserved by the user mapping.
- `NcPreSetDisposition` blocks delete disposition on ancestors of either mapping.
- `NcPreSetLinkInformation` redirects hard-link creation inside the user mapping to the corresponding real mapping path and blocks links into the hidden real mapping.
- `NcPreRename` validates source and target overlap, blocks unsafe ancestor or hidden-real operations, and redirects renames into the user mapping to the real mapping path.

## Control Flow

`NcPostQueryName` runs after successful name queries, or after `STATUS_BUFFER_OVERFLOW`. It gets the instance mapping, finds the returned name inside the user buffer, checks overlap with the real mapping, adjusts `FileNameLength` and `IoStatus.Information`, then copies the user mapping path and optional remainder into the caller's buffer. On buffer overflow it biases the required name length when the user mapping is longer than the real mapping.

`NcPreQueryAlternateName` gets the opened name and only handles the mapping object itself. Non-mapping objects pass through. For the mapping, it returns `UserMapping.ShortNamePath.FinalComponentName` directly if the caller's buffer is large enough.

`NcPostQueryHardLinks` takes a copy of the filesystem's `FILE_LINKS_INFORMATION` result, opens both real and user mapping parent directories, queries their file IDs, then walks each link entry. Entries whose parent ID and final component match the real mapping long or short final component are rewritten to the user mapping parent ID and long final component.

`NcPreSetShortName` skips filesystems without short names, then denies short-name changes on the mapping, either mapping's ancestors, invalid oversized names, or peer names that collide with the user mapping long or short final component. Other requests pass through.

`NcPreSetDisposition` ignores attempts to clear delete disposition. For delete requests, it gets the opened name and denies deletion of ancestors of either the real or user mapping.

`NcPreSetLinkInformation` resolves the destination with `FltGetDestinationFileNameInformation`. It denies linking to the real mapping itself, rejects unexpected links inside the real mapping, denies replace-over-existing on mapping ancestors, passes through destinations outside the user mapping, and redirects destinations inside the user mapping by constructing the equivalent real mapping name and issuing `FltSetInformationFile` itself.

`NcPreRename` validates both source and target. It denies renaming an ancestor of either mapping, denies targets inside the real mapping, denies replace-over-existing on mapping ancestors, passes through targets outside the user mapping, and redirects non-stream renames into the user mapping by issuing a new rename request to the corresponding real mapping target.

## State and Data Flow

The file uses `PNC_INSTANCE_CONTEXT->Mapping`, especially:

- `UserMapping.LongNamePath.VolumelessName`
- `UserMapping.LongNamePath.ParentPath`
- `UserMapping.LongNamePath.FinalComponentName`
- `UserMapping.ShortNamePath.FinalComponentName`
- `RealMapping.LongNamePath.VolumelessName`
- `RealMapping.LongNamePath.ParentPath`
- `RealMapping.LongNamePath.FinalComponentName`
- `RealMapping.ShortNamePath.FinalComponentName`

Path comparisons use `NcComparePath` to obtain `Match`, `InMapping`, `Ancestor`, `Parent`, `Peer`, and remainder information. Redirection uses `NcConstructPath` to combine a target remainder under the real mapping.

For redirected link and rename operations, the file allocates a fresh `FILE_LINK_INFORMATION` or `FILE_RENAME_INFORMATION`, sets `RootDirectory = NULL`, copies the constructed full target path, issues `FltSetInformationFile`, and completes the original callback data without passing the original operation down.

## Dependencies

- Includes `nc.h` and uses shared NameChanger helpers for mapping comparison, path construction, name query, file open, and exception cleanup.
- Uses Filter Manager APIs: `FltGetInstanceContext`, `FltReleaseContext`, `FltGetDestinationFileNameInformation`, `FltParseFileNameInformation`, `FltReleaseFileNameInformation`, `FltQueryInformationFile`, `FltSetInformationFile`, and `FltClose`.
- Uses `NcCreateFileHelper` to open mapping parent directories while ignoring share access checks where required.
- Uses Windows file information structures: `FILE_NAME_INFORMATION`, `FILE_ALL_INFORMATION`, `FILE_LINKS_INFORMATION`, `FILE_LINK_ENTRY_INFORMATION`, `FILE_LINK_INFORMATION`, `FILE_RENAME_INFORMATION`, `FILE_DISPOSITION_INFORMATION`, and `FILE_DISPOSITION_INFORMATION_EX`.
- Uses allocation tags `NC_TAG`, `NC_SET_LINK_BUFFER_TAG`, and `NC_RENAME_BUFFER_TAG`.

## Risks and Edge Cases

- `NcPostQueryName` must preserve Windows name-query overflow semantics: `STATUS_BUFFER_OVERFLOW` is not success, but `IoStatus.Information` still reports copied bytes and `FileNameLength` reports the needed name length.
- Hard-link enumeration can report an inaccurate required size on an initial filesystem overflow because the filter cannot transform a full result it does not yet have; the comments explicitly accept a second-call correction.
- Hard-link rewriting depends on parent file IDs plus final component comparison. If parent ID queries fail, the operation fails rather than returning partially transformed data.
- Alternate-name behavior intentionally differs from NTFS for open-by-ID and potential multiple alternate names.
- Short-name setting is denied for mapping-sensitive cases because the mapping's long/short name pairings are treated as read-only.
- Rename and link redirection cannot safely mutate the original callback buffer because filesystems may use target-directory state from earlier `OPEN_TARGET_DIRECTORY` processing; the file issues its own operation instead.
- Stream rename targets beginning with `:` are passed through even if the containing path overlaps the user mapping, because only the stream name changes.
- The code handles `FileRenameInformationEx` and `FileDispositionInformationEx` flag forms as well as older boolean fields.

## Research Notes

This file enforces NameChanger's metadata invariants for user-visible file information. Query paths are rewritten from real to user view; mutation paths are either denied when they would damage mapping structure or redirected from user mapping targets to the real backing path.
<!-- END FILE RESEARCH: sources/windows/windows-driver-samples/filesys/miniFilter/NameChanger/ncfileinfo.c -->