# Group Research: group_290_dokany_sources_windows_dokany_sys_util_ntstatus_log_inc_sources_wind_1c1dbba9a67a

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/dokany`.

Read validation: every listed source file was read completely. The checked content totals 3,749 lines across 5 files in the working tree; prompt metadata differs by one line for the first three files, likely due line-ending/final-newline counting.

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/ntstatus_log.inc -->
# File Research: sources/windows/dokany/sys/util/ntstatus_log.inc

## Purpose
Large generated-style switch-body include used by Dokany kernel logging to turn `NTSTATUS`-family values into readable symbolic names.

## Main Behavior
- Contains 2,692 `case <STATUS>: return "<STATUS>";` entries and no enclosing function, switch, or default case.
- Included directly inside `DokanGetNTSTATUSStr(NTSTATUS Status)` in `sources/windows/dokany/sys/util/log.c`.
- Maps standard success, informational, warning, error, debug, RPC, ACPI, filter manager, Side-by-Side, cluster, transaction, log, graphics, BitLocker/FVE, Windows Filtering Platform, NDIS, TPM, Hyper-V, volume manager, VHD, Storage Spaces, SMB, secure boot, and app execution status constants.
- Unknown statuses fall through to `DokanGetNTSTATUSStr`'s enclosing `"Unknown"` return in `log.c`.

## Integration Points
- Used by `DOKAN_LOG_END_MJ`, mount manager logging, create/oplock logging, notification logging, and other diagnostic paths that call `DokanGetNTSTATUSStr`.
- Registered in the Visual Studio project as a non-compiling include item.
- Depends on Windows kernel headers defining every referenced status macro for the selected WDK target.

## Risks and Notes
- The file is data for diagnostics only; it does not affect IRP completion status values.
- Because entries are raw `case` labels, undefined constants or duplicate constant values become compile-time failures in the including translation unit.
- Several returned strings are visibly truncated compared with their case names, for example some names ending in `FULL`, `FAIL`, `LEVEL`, or `DLL`. That can make logs imprecise but not semantically wrong for control flow.
- There are no conditional guards for version-specific status constants, so WDK version compatibility is tied to the status set captured in this file.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/ntstatus_log.inc -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/str.c -->
# File Research: sources/windows/dokany/sys/util/str.c

## Purpose
Implements Dokany kernel-mode Unicode string helpers for allocation, duplication, prefix checks/replacement, mount-point classification, and simple character search.

## Main Behavior
- Defines global prefix constants:
  - `g_DosDevicesPrefix` as `\DosDevices\`
  - `g_VolumeGuidPrefix` as `\??\Volume{`
  - `g_ObjectManagerPrefix` as `\??\`
- `DokanAllocateUnicodeString()` allocates a `UNICODE_STRING` plus copied null-terminated buffer, validates with `RtlUnicodeStringInitEx`, and frees on failure.
- `DokanFreeUnicodeString()` frees both the buffer and wrapper struct.
- `DokanAllocDuplicateString()` and `DokanDuplicateUnicodeString()` deep-copy an existing `UNICODE_STRING`, replacing any existing destination buffer.
- `StartsWith()` performs a case-sensitive prefix test, with empty/null prefix treated as success.
- `ChangePrefix()` optionally requires an existing prefix, allocates a new string, copies a replacement prefix, then appends the original suffix.
- `IsMountPointDriveLetter()` recognizes mount points shaped like `\DosDevices\C:`, with or without a trailing null in `Length`.
- Search helpers scan for `WCHAR` values either backward from an offset or forward across a byte-length string.

## Integration Points
- Used by mount/device setup and FS control paths to classify drive-letter mount points, volume GUID mount points, and object-manager paths.
- `ChangePrefix()` is used by reparse/open-by-id style FS control handling to convert `\DosDevices\...` paths into `\??\...`.
- Search helpers are used by file info, create, event, and path handling code to locate stream separators, slashes, mount-point separators, and file-name offsets.
- Allocation helpers are used by initialization/device code for DCB names, symbolic links, mount points, UNC names, and mount manager names.

## Risks and Notes
- Prefix matching walks until a null terminator in the prefix buffer rather than strictly using `Prefix->Length`; this is safe for the defined constant strings but assumes valid null-terminated prefix buffers.
- `DokanDuplicateUnicodeString()` copies `MaximumLength`, not only `Length`, preserving trailing null/storage but requiring `Src->Buffer` and `Src->MaximumLength` to be valid.
- `DokanSearchWcharinUnicodeStringWithUlong()` compares `offsetPosition` to `MaximumLength` but then indexes `Buffer[offsetPosition]` as WCHAR units; callers need to pass offsets consistently.
- `ChangePrefix()` sets `MaximumLength` equal to the exact resulting byte length without reserving an extra terminator beyond the composed string.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/str.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/str.h -->
# File Research: sources/windows/dokany/sys/util/str.h

## Purpose
Header for Dokany kernel-mode string utilities implemented in `str.c`, plus an inline wrapper for borrowing raw buffers as `UNICODE_STRING`.

## Main Behavior
- Declares the shared prefix constants for DOS devices, volume GUID object paths, and object-manager paths.
- Declares allocation/free helpers for owned `UNICODE_STRING` objects.
- Declares deep-copy helpers for both allocated destination structs and caller-owned destination structs.
- Defines `DokanWrapUnicodeString(Buffer, Length)` inline, returning a non-owning `UNICODE_STRING` with `Length == MaximumLength`.
- Documents and declares backward and forward WCHAR search helpers.
- Declares prefix-checking helpers, drive-letter mount-point detection, and prefix replacement.

## Integration Points
- Included wherever Dokany needs path/mount string handling in kernel code.
- The inline wrapper is used by create, device, FCB, fileinfo, and string prefix replacement paths where buffers are already owned elsewhere.
- The declared helpers support mount manager integration, initialization, path parsing, stream detection, and FS control translation.

## Risks and Notes
- `DokanWrapUnicodeString()` is non-owning; consumers must not free the wrapped buffer through `DokanFreeUnicodeString`.
- The API mixes byte lengths (`UNICODE_STRING.Length`) with some offset parameters named generically, so caller discipline matters.
- Prefix checks are case-sensitive and do not perform Windows path normalization.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/str.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/volume.c -->
# File Research: sources/windows/dokany/sys/volume.c

## Purpose
Handles `IRP_MJ_QUERY_VOLUME_INFORMATION` and `IRP_MJ_SET_VOLUME_INFORMATION` for Dokany volumes, including early default responses before user-mode event processing is ready.

## Main Behavior
- `DokanDispatchQueryVolumeInformation()` validates the VCB and file object, logs the requested `FS_INFORMATION_CLASS`, then handles volume information classes.
- Before `Vcb->HasEventWait` is true, it returns hard-coded defaults for selected queries:
  - `FileFsVolumeInformation`: zero creation time, fixed serial number, default `VOLUME_LABEL`.
  - `FileFsSizeInformation`: 1 GiB total, 512 MiB free, default allocation unit and sector size.
  - `FileFsAttributeInformation`: hard links, case-sensitive search, preserved names, `NTFS` filesystem name.
  - `FileFsFullSizeInformation`: same default space values with caller/actual available fields.
- `FileFsDeviceInformation` is always answered in-kernel from DCB device type and characteristics.
- Once user-mode processing is available, selected query classes are packaged into an `EVENT_CONTEXT` and registered as pending IRPs for user-mode completion.
- `DokanCompleteQueryVolumeInformation()` validates returned buffer size, optionally adds `FILE_READ_ONLY_VOLUME`, overrides volume label from `Dcb->VolumeLabel`, copies user-mode data to the IRP output buffer, and sets final status/information.
- `DokanDispatchSetVolumeInformation()` supports `FileFsLabelInformation` by replacing `Dcb->VolumeLabel` under the DCB resource lock.

## Integration Points
- Dispatched from `dispatch.c` for query volume IRPs and completed from `event.c`.
- Uses `AllocateEventContext()` and `DokanRegisterPendingIrp()` for user-mode round trips.
- Uses `DokanGetFsInformationClassStr()` for logging and `PREPARE_OUTPUT` for structured output preparation.
- Reads and updates DCB/VCB fields including `HasEventWait`, `DeviceType`, `DeviceCharacteristics`, `VolumeLabel`, and read-only device flags.
- User-mode volume callbacks live in the Dokany library side and fill `EVENT_INFORMATION`.

## Risks and Notes
- Early mount-time defaults are intentional compatibility behavior for filter drivers issuing queries before user-mode worker threads are available.
- `DokanCompleteQueryVolumeInformation()` rejects returned data when `EventInfo->BufferLength` exceeds the IRP buffer length, using `STATUS_INSUFFICIENT_RESOURCES`.
- Volume-label override truncates to caller buffer capacity and updates `EventInfo->BufferLength` to the copied label structure size.
- `FileFsLabelInformation` allocation failure returns while holding the DCB resource lock; that path should be reviewed if modifying label handling.
- Only volume label setting is implemented; other set-volume classes return `STATUS_INVALID_PARAMETER`.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/write.c -->
# File Research: sources/windows/dokany/sys/write.c

## Purpose
Implements Dokany write IRP dispatch and completion, bridging kernel write requests to user-mode filesystem callbacks while handling cache, oplock, paging I/O, large payload, and file-size update concerns.

## Main Behavior
- `DokanDispatchWrite()` logs write parameters, immediately succeeds zero-length writes, validates file object/VCB/CCB, and rejects directory writes.
- Resolves the write buffer from an MDL via `MmGetSystemAddressForMdlNormalSafe()` or from `Irp->UserBuffer`.
- Detects write-to-end-of-file, paging I/O, noncached I/O, and synchronous I/O flags.
- For non-paging writes with a data section, flushes and purges cache around the write range, using Dokany paging I/O locks.
- Rejects paging I/O write-to-EOF as a no-op success because paging writes require concrete offsets.
- Builds an `EVENT_CONTEXT` containing write metadata, file name, and copied write bytes. It guards event length with a 64-bit calculation to avoid overflow.
- For normal-size events, performs oplock checks and registers the full event context as a pending IRP.
- For large writes exceeding `EVENT_CONTEXT_MAX_SIZE`, stores the full event context in `DriverContext[DRIVER_CONTEXT_EVENT]`, sends a smaller request containing metadata and requested full length, and lets later event retrieval copy the larger context.
- Marks event flags for paging, synchronous, noncached, and write-to-EOF cases; resolves `FILE_USE_FILE_POINTER_POSITION` against `FileObject->CurrentByteOffset` for synchronous I/O.
- `DokanCompleteWrite()` propagates user context, status, and written byte count; on success it updates file size when the reported current byte offset grows, reports size change notifications, marks last-write change, sets `FO_FILE_MODIFIED` for non-paging writes, and advances `CurrentByteOffset` for synchronous non-paging writes.

## Integration Points
- Dispatched from `dispatch.c` for `IRP_MJ_WRITE` and completed from `event.c`.
- Consumed by user-mode write handling in `sources/windows/dokany/dokan/write.c`, including the large-write `RequestLength` path.
- Uses FCB/CCB helpers, oplock helpers, cache manager APIs, paging I/O locks, event allocation/registration, and notification reporting.
- Shares large-event cleanup and retrieval behavior with `event.c` via `DRIVER_CONTEXT_EVENT`.

## Risks and Notes
- The function copies the entire write payload into nonpaged/event memory before handing it to user mode; the large-write path mitigates event queue size but still stores a full kernel-side event context.
- Correct cleanup depends on `DriverContext[DRIVER_CONTEXT_EVENT]` being cleared or freed by the event path for oversized writes.
- Cache flush/purge before user-mode completion is important for coherency with mapped sections and should be treated carefully.
- Oplock checks differ slightly between normal and large paths: normal path uses `DokanCheckOplock`, while the large path calls `FsRtlCheckOplock` directly.
- Completion trusts user-mode `EventInfo->Operation.Write.CurrentByteOffset` for file size and current offset updates.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/write.c -->