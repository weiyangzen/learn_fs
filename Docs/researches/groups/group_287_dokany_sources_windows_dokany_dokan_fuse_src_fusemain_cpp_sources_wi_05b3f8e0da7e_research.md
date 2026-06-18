# Group Research: group_287_dokany_sources_windows_dokany_dokan_fuse_src_fusemain_cpp_sources_wi_05b3f8e0da7e

Scope checked against `Docs/research_subset_a.md`: `sources/windows/dokany` is included in subset A. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fusemain.cpp -->
# File Research: sources/windows/dokany/dokan_fuse/src/fusemain.cpp

## Role

Implements the Dokan-to-FUSE compatibility bridge for `dokan_fuse`. It translates Dokan callback semantics, Windows paths, sharing, locking, and file metadata into FUSE operation callbacks.

## Main Components

- Thread-local FUSE context stack:
  - `cur_impl_chain_link`
  - `impl_chain_guard`
  - `fuse_get_context`
- `impl_fuse_context`:
  - Wraps `fuse_operations`.
  - Runs `init`/`destroy`.
  - Implements Dokan operation handlers such as create/open/read/write/flush/stat/delete/rename/lock/time/volume info.
- Directory enumeration:
  - `find_files`
  - `walk_directory`
  - `walk_directory_getdir`
  - Supports both modern `readdir` and older `getdir`.
- File/share/byte-range lock tracking:
  - `impl_file_locks`
  - `impl_file_lock`
  - `impl_file_handle`

## Behavior

The file maps Windows/Dokan operations onto FUSE callbacks:

- `create_file`:
  - Resolves UTF-16 Windows path to UTF-8 Unix-style path.
  - Uses `getattr` to decide whether to create, open, truncate, supersede, or reject.
  - Handles directories and symlinks.
- `read_file` and `write_file`:
  - Use stored `impl_file_handle` state rather than the incoming path, because opens may have followed symlinks.
  - Enforce byte-range locks before dispatch.
  - `read_file` chunks reads by `max_read_`.
  - `write_file` honors `conn_info_.max_write`.
- `cleanup`:
  - Deletes pending files/directories on cleanup when Dokan marks `DeletePending`.
- `move_file`:
  - Implements rename with optional target replacement and updates internal lock table names.
- `set_file_time`:
  - Supports `win_set_times`, `utimens`, or `utime`.
- `get_disk_free_space` and `get_volume_information`:
  - Expose FUSE `statfs` and configured volume/filesystem names.

## Important Details

- Symlink handling uses `getattr` plus `readlink`, then resolves relative symlink targets with `extract_dir_name`.
- Directory listing attempts UTF-8 conversion first, then falls back to ANSI conversion and may rename malformed entries if possible.
- `convert_flags` reduces Windows desired access to `O_RDONLY`, `O_WRONLY`, or `O_RDWR`.
- Share access is approximated in userspace by checking prior handles for the same file.
- Local byte-range lock tracking is used when FUSE `lock` is unavailable.
- `impl_file_handle::~impl_file_handle` removes the handle from the shared lock table.

## Dependencies

- Dokan callback types and `PDOKAN_FILE_INFO`.
- FUSE types and callbacks from `fusemain.h`.
- Path/time/stat conversion helpers from `utils.h`.
- Windows constants, NT status values, POSIX errno/stat conventions.

## Notes and Risks

- Several comments identify race conditions around cleanup/delete and open files.
- Share and lock semantics are approximations of Windows behavior over FUSE callbacks.
- `do_delete_directory` refuses deletion when a handle exists, unlike Unix unlink semantics.
- Symlink relative-path normalization is marked TODO and is incomplete.
- `impl_file_locks::renamed_file` has a TODO for renaming onto an existing tracked name.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fusemain.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/resource.h -->
# File Research: sources/windows/dokany/dokan_fuse/src/resource.h

## Role

Defines the Windows resource identifier used by the Dokan FUSE resource script.

## Contents

- `IDR_VERSION2` is defined as resource ID `101`.
- Includes Visual Studio resource editor default-value macros under `APSTUDIO_INVOKED`.

## Dependencies

- Used by `dokanfuse.rc`.
- No runtime code or filesystem behavior.

## Notes

This is generated-style resource metadata and has no direct interaction with Dokan/FUSE logic.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/utils.cpp -->
# File Research: sources/windows/dokany/dokan_fuse/src/utils.cpp

## Role

Provides conversion utilities for the Dokan FUSE bridge: string encoding, path normalization, FILETIME/unix time conversion, NTSTATUS/errno mapping, and argument conversion.

## Main Functions

- Encoding:
  - `utf8_to_wchar_buf`
  - `utf8_to_wchar_buf_old`
  - `wchar_to_utf8_cstr`
- Paths:
  - `unixify`
  - `extract_file_name`
  - `extract_dir_name`
- Time:
  - `unixTimeToFiletime`
  - `filetimeToUnixTime`
  - `is_filetime_set`
- Errors:
  - `ntstatus_error_to_errno`
  - `errno_to_ntstatus_error`
- CLI argument conversion:
  - `convert_args`
  - `free_converted_args`

## Behavior

- Converts UTF-8 to UTF-16 using `MultiByteToWideChar(CP_UTF8)`.
- Treats replacement character `U+FFFD` as conversion failure.
- Falls back to ANSI codepage conversion in `utf8_to_wchar_buf_old`.
- Normalizes Windows backslashes to Unix slashes and removes trailing slash except for root.
- Maps common NTSTATUS values to POSIX errno values and back.
- Converts `wchar_t **argv` to heap-allocated UTF-8 `char **argv`.

## Dependencies

- Windows APIs:
  - `MultiByteToWideChar`
  - `WideCharToMultiByte`
  - `FILETIME`
- NTSTATUS constants.
- POSIX errno constants.

## Notes and Risks

- The NTSTATUS/errno mapping is limited and defaults unknown errors to `EINVAL` or `STATUS_NOT_IMPLEMENTED`.
- `wchar_to_utf8` allocates with `malloc`; callers must free through provided wrappers or equivalent.
- `utf8_to_wchar_buf_old` uses ACP fallback, which may be lossy but supports legacy filenames.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/utils.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/access.c -->
# File Research: sources/windows/dokany/sys/access.c

## Role

Implements `DokanGetAccessToken`, a kernel IOCTL helper that returns an access token handle for a pending create IRP.

## Main Function

- `DokanGetAccessToken(PREQUEST_CONTEXT RequestContext)`

## Behavior

- Requires the IOCTL to come from user mode.
- Validates the output buffer is exactly `sizeof(EVENT_INFORMATION)`.
- Looks up a pending IRP by `SerialNumber` in `Dcb->PendingIrp`.
- Expects the target pending IRP to be an `IRP_MJ_CREATE` with a security context.
- Extracts the subject token from the create IRP access state.
- Opens a kernel handle to the token using `ObOpenObjectByPointer`.
- Returns that handle in `eventInfo->Operation.AccessToken.Handle`.

## Dependencies

- `dokan.h`
- `util/irp_buffer_helper.h`
- Pending IRP list locking via spin lock.
- Windows security APIs:
  - `SeQuerySubjectContextToken`
  - `ObOpenObjectByPointer`
  - `SeTokenObjectType`

## Notes and Risks

- Protects pending IRP list traversal with `PendingIrp.ListLock`.
- Explicitly avoids accessing `SeTokenObjectType` while holding the spin lock because that caused BSODs on Windows XP.
- Failure to find the matching pending IRP leaves status as `STATUS_INVALID_PARAMETER`.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/access.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/cleanup.c -->
# File Research: sources/windows/dokany/sys/cleanup.c

## Role

Handles `IRP_MJ_CLEANUP`, including share-access removal, file-lock cleanup, delete-on-close transfer, directory notification cleanup, keepalive-triggered unmounting, and optional user-mode cleanup dispatch.

## Main Functions

- `DokanExecuteCleanup`
- `DokanDispatchCleanup`
- `DokanCompleteCleanup`

## Behavior

- `DokanExecuteCleanup`:
  - Validates file object, VCB/DCB, and CCB.
  - Checks the CCB belongs to the current mount.
  - Decrements `fcb->UncleanCount`.
  - Removes share access.
  - Checks oplocks.
  - Unlocks all outstanding file locks for the file object/process.
- `DokanDispatchCleanup`:
  - Transfers `DOKAN_DELETE_ON_CLOSE` from CCB to FCB delete-pending state.
  - Reports file/directory removal notifications when the last unclean handle is closing.
  - Calls `FsRtlNotifyCleanup` for directories.
  - Handles keepalive file cleanup by triggering unmount.
  - If unmount is pending or user-mode dispatch is blocked, executes cleanup locally.
  - Otherwise flushes FCB state, builds an `EVENT_CONTEXT`, and registers a pending IRP for user mode.
- `DokanCompleteCleanup`:
  - Runs `DokanExecuteCleanup`.
  - Sets final IRP status from user-mode `EVENT_INFORMATION`.

## Dependencies

- `dokan.h`
- FCB/CCB flags and locks.
- FsRtl file locks and change notifications.
- User-mode event pipeline through `AllocateEventContext` and `DokanRegisterPendingIrp`.

## Notes and Risks

- Delete-on-close is deliberately delayed until cleanup and only acted on when the last handle closes.
- Comments call out a race where create may succeed while delete-pending state is being established.
- Keepalive cleanup can force unmount if the owning process exits.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/close.c -->
# File Research: sources/windows/dokany/sys/close.c

## Role

Handles `IRP_MJ_CLOSE`, releases kernel per-open state, and sends a best-effort close notification to user mode.

## Main Function

- `DokanDispatchClose`

## Behavior

- Validates file object and context.
- If CCB validation fails but a CCB exists, frees CCB and FCB defensively.
- If user-mode dispatch is blocked for the FCB, frees CCB/FCB and returns success.
- Otherwise:
  - Allocates an `EVENT_CONTEXT`.
  - Copies CCB user context and FCB filename into the close event.
  - Frees the CCB and FCB immediately.
  - Sends a notification with `DokanEventNotification`.
- Close IRPs are never registered as pending.

## Dependencies

- `dokan.h`
- `util/fcb.h`
- CCB/FCB allocation lifecycle.
- User-mode notification queue.

## Notes and Risks

- Close is always completed synchronously from the kernel side.
- If event allocation fails, the code still frees kernel state and returns success, so close notification can be lost.
- Distinct from cleanup: cleanup handles semantic close from user handles; close releases object references.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/close.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/create.c -->
# File Research: sources/windows/dokany/sys/create.c

## Role

Implements `IRP_MJ_CREATE`, the central Dokan open/create path. It normalizes names, manages FCB/CCB creation, handles related-file opens, validates write/share/oplock constraints, packages security metadata, and dispatches create requests to user mode.

## Main Functions

- CCB lifecycle:
  - `DokanAllocateCCB`
  - `DokanFreeCCB`
- Helpers:
  - `DokanGetParentDir`
  - `FixFileNameForReparseMountPoint`
  - `SetFileObjectForVCB`
  - `IsDokanProcessFiles`
  - `DokanCheckShareAccess`
  - `DokanRetryCreateAfterOplockBreak`
- Create path:
  - `DokanDispatchCreate`
  - `DokanCompleteCreate`

## Behavior

`DokanDispatchCreate` performs:

- Early rejection for missing file objects, unmounted volumes, unsupported paging files, and read-only write attempts.
- Reparse mount-point filename case repair on older Windows versions.
- Volume-open handling for empty filenames.
- Related-file-object path composition.
- Trailing and duplicated slash normalization.
- UNC prefix stripping.
- Alternate data stream rejection unless enabled.
- Parent-directory extraction for `SL_OPEN_TARGET_DIRECTORY`.
- FCB lookup/allocation and CCB allocation.
- File object binding:
  - `FsContext` to FCB advanced header.
  - `FsContext2` to CCB.
  - `SectionObjectPointer` to FCB section pointers.
- Security descriptor assignment and packaging into an event buffer.
- Share access checking through `IoCheckShareAccess`, `IoSetShareAccess`, and `IoUpdateShareAccess`.
- Oplock checks, break/retry handling, and atomic create-with-oplock support.
- Pending IRP registration for user mode.

`DokanCompleteCreate`:

- Copies user context into CCB.
- Sets IRP status and create information.
- Handles read-only `FILE_OPEN_IF` substitution result.
- Marks directory FCBs.
- Marks CCB as opened.
- Records delete-on-close for cleanup.
- Increments `UncleanCount` on success.
- Sends create notifications.
- On failure, backs out atomic oplock, removes share access, frees CCB/FCB, and clears file-object contexts.

## Dependencies

- `dokan.h`
- `util/fcb.h`
- `util/str.h`
- Windows I/O manager create parameters.
- Security APIs:
  - `SeAssignSecurity`
  - `SeDeassignSecurity`
- FsRtl oplock APIs.
- FCB AVL/cache management via `DokanGetFCB` and `DokanFreeFCB`.

## Important State

- `fcb->OpenCount`
- `fcb->UncleanCount`
- `fcb->ShareAccess`
- `ccb->UserContext`
- `ccb->AtomicOplockRequestPending`
- FCB flags:
  - directory
  - delete pending
  - block user-mode dispatch

## Notes and Risks

- This file is the highest-risk concurrency path in the group.
- Several paths require careful unwind of CCB/FCB/share/oplock state.
- The code comments document races around delete-pending and create completion.
- Filename manipulation supports multiple Windows edge cases: related opens, reparse mount points, UNC redirector paths, root alternate streams, and target-directory opens.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/create.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/device.c -->
# File Research: sources/windows/dokany/sys/device.c

## Role

Handles device and volume control requests for Dokan disk, volume, mount-manager, storage, and network redirector behavior.

## Main Functions

- `GlobalDeviceControl`
- `DokanPopulateDiskGeometry`
- `DokanPopulatePartitionInfo`
- `DokanPopulatePartitionInfoEx`
- `DiskDeviceControl`
- `DiskDeviceControlWithLock`
- `IsVolumeOpen`
- `DokanGetVolumeMetrics`
- `VolumeDeviceControl`
- `DokanDispatchDeviceControl`

## Behavior

Supports IOCTL families for:

- Disk geometry and length:
  - `IOCTL_DISK_GET_DRIVE_GEOMETRY`
  - `IOCTL_DISK_GET_LENGTH_INFO`
- Partition and layout information:
  - `IOCTL_DISK_GET_DRIVE_LAYOUT`
  - `IOCTL_DISK_GET_DRIVE_LAYOUT_EX`
  - `IOCTL_DISK_GET_PARTITION_INFO`
  - `IOCTL_DISK_GET_PARTITION_INFO_EX`
- Write protection:
  - `IOCTL_DISK_IS_WRITABLE`
  - `IOCTL_VOLUME_GET_GPT_ATTRIBUTES`
- Storage media/hotplug:
  - `IOCTL_STORAGE_GET_HOTPLUG_INFO`
  - `IOCTL_STORAGE_CHECK_VERIFY`
  - `IOCTL_STORAGE_GET_MEDIA_TYPES_EX`
  - `IOCTL_STORAGE_GET_DEVICE_NUMBER`
  - `IOCTL_STORAGE_QUERY_PROPERTY`
- Mount manager:
  - `IOCTL_MOUNTDEV_QUERY_DEVICE_NAME`
  - `IOCTL_MOUNTDEV_QUERY_UNIQUE_ID`
  - `IOCTL_MOUNTDEV_QUERY_SUGGESTED_LINK_NAME`
  - `IOCTL_MOUNTDEV_LINK_CREATED`
  - `IOCTL_MOUNTDEV_LINK_DELETED`
- Network redirector path checks:
  - `IOCTL_REDIR_QUERY_PATH`
  - `IOCTL_REDIR_QUERY_PATH_EX`
- Volume metrics:
  - `DokanGetVolumeMetrics`

## Dependencies

- `dokan.h`
- `util/irp_buffer_helper.h`
- `util/str.h`
- Windows headers:
  - `mountdev.h`
  - `mountmgr.h`
  - `ntddvol.h`
  - `storduid.h`

## Important Details

- Uses remove locks in `DiskDeviceControlWithLock`.
- Rejects requests for deleted or unmounted devices.
- Maintains actual mount point after mount-manager link creation.
- Can trigger unmount when a mount-manager link is externally deleted.
- Volume-level mountdev controls require opening the volume, not a normal file handle.
- UNC redirector handling validates path prefixes and reports accepted UNC length.

## Notes and Risks

- Many storage responses are synthetic defaults, not real disk layout data.
- Mount-manager behavior must stay synchronized with DCB global mount entries.
- Device deletion and unmount pending checks guard against use-after-removal paths.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/device.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/directory.c -->
# File Research: sources/windows/dokany/sys/directory.c

## Role

Implements directory control dispatch for directory enumeration and change notification.

## Main Functions

- `DokanDispatchDirectoryControl`
- `DokanQueryDirectory`
- `DokanNotifyChangeDirectory`
- `DokanCompleteDirectoryControl`

## Behavior

- Dispatches minor functions:
  - `IRP_MN_QUERY_DIRECTORY`
  - `IRP_MN_NOTIFY_CHANGE_DIRECTORY`
- `DokanQueryDirectory`:
  - Validates CCB/VCB.
  - Allocates an MDL for user buffer if needed.
  - Initializes or reuses per-CCB search pattern.
  - Tracks enumeration index in `ccb->Context`.
  - Builds `EVENT_CONTEXT` with directory name, search pattern, requested information class, buffer length, and index.
  - Registers the request as pending for user mode.
- `DokanNotifyChangeDirectory`:
  - Requires the FCB to be a directory and not delete-pending.
  - Marks debug flags.
  - Registers the IRP with `FsRtlNotifyFullChangeDirectory`.
  - Sets `DoNotComplete` because FsRtl owns/completes the IRP.
- `DokanCompleteDirectoryControl`:
  - Copies user-mode directory data back to the IRP buffer.
  - Updates enumeration index and user context.
  - Frees allocated MDL if this path allocated it.

## Dependencies

- `dokan.h`
- FsRtl directory notification APIs.
- MDL helpers from core Dokan functions.
- User-mode event completion contract through `EVENT_INFORMATION`.

## Notes and Risks

- Search pattern lifetime is per CCB and freed when CCB is freed.
- The code notes that writing `ccb->Context` may need locking.
- Directory notification stores a pointer to the FCB filename in FsRtl state, so FCB lifetime and notification cleanup are important.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/directory.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/dispatch.c -->
# File Research: sources/windows/dokany/sys/dispatch.c

## Role

Provides top-level IRP dispatch wrapping, request-context construction, read-only enforcement, exception handling, and routing to per-major-function handlers.

## Main Functions

- `DokanBuildRequest`
- `DokanCancelCreateIrp`
- `DokanBuildRequestContext`
- `DokanDispatchRequest`

## Behavior

- `DokanBuildRequest`:
  - Enters filesystem context with `FsRtlEnterFileSystem`.
  - Sets top-level IRP when needed.
  - Calls `DokanDispatchRequest`.
  - Handles exceptions through Dokan exception filter/handler.
- `DokanBuildRequestContext`:
  - Captures device object, IRP, stack location, process ID, top-level status.
  - Resolves device extension type into global/DCB/VCB pointers.
  - Initializes `IoStatus.Information` to zero.
- `DokanDispatchRequest`:
  - Rejects most operations if the device is unmounted.
  - Enforces read-only volume behavior for write-like major functions.
  - Routes major functions to the corresponding `DokanDispatch*` handler.
- `DokanCancelCreateIrp`:
  - Completes a create IRP with a synthesized `EVENT_INFORMATION` status from a safe filesystem context.

## Dependencies

- `dokan.h`
- All per-operation dispatch functions.
- FsRtl top-level IRP conventions.
- Dokan exception handling and logging.

## Notes and Risks

- This is the common choke point for all IRP major functions.
- `REQUEST_CONTEXT` exists to avoid reading IRP stack/device state later after cancellation or ownership transfer.
- Read-only enforcement here is broad, while create-specific read-only checks live in `create.c`.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/dispatch.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/dokan.c -->
# File Research: sources/windows/dokany/sys/dokan.c

## Role

Core Dokan driver initialization and shared kernel utilities. It sets driver dispatch tables, Fast I/O callbacks, lookaside lists, filesystem filter callbacks, lock debugging, oplock debugging, change notification helpers, MDL helpers, and global cleanup.

## Main Areas

- Driver lifecycle:
  - `DriverEntry`
  - `DokanUnload`
  - `CleanupGlobalDiskDevice`
  - `InitMultiVersionResources`
- Fast I/O and cache callbacks:
  - `DokanFastIoCheckIfPossible`
  - `DokanFastIoRead`
  - `DokanAcquireForCreateSection`
  - `DokanReleaseForCreateSection`
  - `DokanAcquireForCcFlush`
  - `DokanReleaseForCcFlush`
  - `DokanFilterCallbackAcquireForCreateSection`
- Allocation helpers:
  - `DokanLookasideCreate`
- Notification:
  - `DokanNotifyReportChange0`
  - `DokanNotifyReportChange`
- Request/context helpers:
  - `DokanCheckCCB`
  - `IsCcbAndDcbSameMount`
  - `DokanAllocateMdl`
  - `DokanFreeMdl`
  - `PointerAlignSize`
- Lock debugging:
  - `DokanLockWarn`
  - `DokanLockNotifyResolved`
  - `DokanResourceLockWithDebugInfo`
  - `DokanResourceUnlockWithDebugInfo`
  - `DokanVCBTryLockRW`
- Oplock debugging:
  - `GetOplockControlDebugInfoBit`
  - `OplockDebugRecord*`
- Misc:
  - `DokanDispatchShutdown`
  - `DokanNoOpAcquire`
  - `DokanNoOpRelease`
  - `DokanCheckOplock`
  - `DokanCompleteIrpRequest`
  - `RunAsSystem`

## Driver Initialization

`DriverEntry`:

- Creates global disk device.
- Assigns all supported `MajorFunction` entries to `DokanBuildRequest`.
- Initializes Fast I/O dispatch:
  - Uses FsRtl copy read/write and MDL helpers.
  - Hooks section and cache flush acquisition/release.
- Initializes version-dependent resources and optional FsRtl routine pointers.
- Initializes IRP entry and CCB/FCB/ERESOURCE lookaside lists.
- Registers filesystem filter callbacks.
- Detects whether reparse mount-point filename repair is needed.

## Notifications

`DokanNotifyReportChange0`:

- Converts stream notifications when filenames contain `:`.
- Computes filename offset after the final backslash.
- Calls `FsRtlNotifyFullReportChange`.
- Catches access violations around notification state and logs structured errors.

## Locking

The file provides debug-aware ERESOURCE acquisition:

- Repeatedly attempts nonblocking acquisition.
- Emits periodic warnings after long waits.
- Tracks exclusive owner thread and call site.
- Clears debug owner state on final unlock.

## Dependencies

- `dokan.h`
- `util/str.h`
- `mountmgr.h`
- Windows kernel FsRtl, cache manager, object/thread, and resource APIs.

## Notes and Risks

- Fast I/O mostly delegates to FsRtl cache helpers or returns false.
- Notification exception handlers suggest rare real-world invalid notify-list/file-name cases.
- `RunAsSystem` creates a system thread and waits synchronously.
- Lock debug mode can materially change acquisition behavior by polling and logging.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/dokan.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/dokan.h -->
# File Research: sources/windows/dokany/sys/dokan.h

## Role

Primary internal kernel header for the Dokan filesystem driver. It defines global constants, allocation helpers, core device/volume/file/open structures, lock macros, request context structures, function declarations, and flag helpers.

## Major Definitions

- Device names:
  - global Dokan control device
  - filesystem disk/CD device names
  - redirector device names
  - disk symbolic link prefixes
- Allocation:
  - pool tag `TAG`
  - `DokanAlloc`
  - `DokanAllocZero`
  - lookaside list declarations
- Timeouts:
  - pending IRP timeout
  - timeout reset maximum
  - check interval
- Identifier types:
  - `DGL`
  - `DCB`
  - `VCB`
  - `FCB`
  - `CCB`
  - `FREED_FCB`

## Core Structures

- `DOKAN_GLOBAL`:
  - Global driver/device state.
  - Mount list and mount-manager lock.
  - Global filesystem device objects.
- `DokanDCB`:
  - Per mounted disk/device state.
  - Pending IRP queues, notify queue, retry queue.
  - Device names, mount point, UNC name, volume label.
  - Threads, events, mount options, batching and logging options.
- `DOKAN_CONTROL` and `MOUNT_ENTRY`:
  - User-visible mount control and global mount-list entry.
- `DokanVCB`:
  - Per volume state.
  - FCB AVL table, notify list, allocation counters, volume flags, keepalive state, FCB garbage collection, volume metrics.
- `DokanFCB`:
  - Per file/directory control block.
  - Advanced FCB header, section pointers, paging resource, CCB list, open counts, flags, share access, filename, file locks, oplock state, debug state, keepalive/block-dispatch markers.
- `DokanCCB`:
  - Per open context.
  - FCB pointer, user context, search pattern, flags, mount ID, keepalive state, atomic oplock pending state, creating process ID.
- `REQUEST_CONTEXT`:
  - Stable per-IRP snapshot containing device, IRP, stack location, DCB/VCB/global pointers, flags, process ID, and completion/logging state.
- `IRP_ENTRY`:
  - Pending IRP queue node.
- `DEVICE_ENTRY` and `DRIVER_EVENT_CONTEXT`:
  - Device deletion/session and driver-log/event queue helpers.
- `SYMLINK_ECP_CONTEXT`:
  - Undocumented ECP structure used for reparse mount-point filename case repair.

## Locking Interface

Defines debug-aware macros:

- `DokanFCBLockRW`
- `DokanFCBLockRO`
- `DokanFCBUnlock`
- `DokanPagingIoLockRW`
- `DokanPagingIoLockRO`
- `DokanPagingIoUnlock`
- `DokanVCBLockRW`
- `DokanVCBLockRO`
- `DokanVCBUnlock`
- `DokanVCBTryLockRW`

When lock debugging is enabled, macros call `DokanResourceLockWithDebugInfo` and track call sites and owner threads.

## Oplock Support

- Declares dynamic routine pointers:
  - `DokanFsRtlCheckLockForOplockRequest`
  - `DokanFsRtlAreThereWaitingFileLocks`
- Defines `DokanGetFcbOplock` compatibility macro for Win8 and older.
- Defines `DokanOplockDebugInfo` and `DOKAN_OPLOCK_DEBUG_*` flags.
- Declares `DokanCheckOplock`, `DokanOplockRequest`, and debug record helpers.

## Function Declarations

The header declares driver-wide functions for:

- IRP dispatch and completion.
- Create/cleanup/close/read/write/query/set/flush/directory/security/lock handlers.
- Event and pending IRP management.
- Device creation/deletion and mount point operations.
- Reparse point FSCTL payload helpers.
- UNC provider registration.
- MDL allocation/freeing.
- FCB flushing, CCB allocation/freeing, mount lookup, unmount, session cleanup.
- Notification reporting and cleanup.
- Oplock tracking.

## Flag Helpers

Provides atomic flag helpers:

- `DokanSetFlag`
- `DokanClearFlag`
- FCB flag access macros.
- CCB flag aliases over FCB-style flag helpers.
- `DokanFCBIsPendingDeletion`.

## Dependencies

- Windows kernel headers:
  - `ntifs.h`
  - `ntdddisk.h`
  - `ntstrsafe.h`
- Dokan public contract:
  - `public.h`
- Logging:
  - `util/log.h`

## Notes and Risks

- This header defines most cross-file contracts; changes here affect the whole driver.
- Several structure fields include explicit locking comments, but some are marked FIXME.
- CCB flag macros alias FCB flag macros, relying on both structures having a compatible `Flags` field.
- Static SDDL grants broad access to system, administrators, world, and restricted code with different permissions.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/dokan.h -->