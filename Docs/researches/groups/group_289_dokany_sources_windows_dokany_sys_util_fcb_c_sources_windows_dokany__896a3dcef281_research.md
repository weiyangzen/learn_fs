# Group Research: group_289_dokany_sources_windows_dokany_sys_util_fcb_c_sources_windows_dokany__896a3dcef281

Scope checked against `Docs/research_subset_a.md`: all files are under `sources/windows/dokany`, which is included in subset A. Every listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/fcb.c -->
# File Research: sources/windows/dokany/sys/util/fcb.c

Dokan FCB lifetime, lookup, rename, and garbage-collection implementation for the Windows kernel driver.

Key responsibilities:
- Defines special internal filenames for keepalive and notification streams.
- Initializes `DokanFCB` objects with `FSRTL_ADVANCED_FCB_HEADER`, paging resources, oplock storage, CCB list state, file size defaults, metrics, and special-file flags.
- Finds or creates FCBs through the per-volume `RTL_AVL_TABLE`, keyed by `UNICODE_STRING` filename.
- Owns open-count decrement and final FCB release through immediate deletion or deferred garbage collection.
- Manages the FCB garbage list, grace-period aging, forced collection, and the dedicated system thread.
- Provides AVL callbacks for filename comparison and node allocation.
- Handles rename-table updates and conflicts with already-existing FCBs.

Important behavior:
- `DokanGetFCB` takes ownership of the filename buffer passed by the caller; new FCBs keep it, failed lookup/init frees it, and existing FCB lookup hands it to `DokanCancelFcbGarbageCollection`.
- Existing FCB reuse cancels pending garbage collection and may update filename casing so case-insensitive lookups do not pin an old case spelling.
- `DokanFreeFCB` first decrements `OpenCount` without the VCB lock so non-final closes can happen safely during nested cache-manager cleanup. Final release then locks VCB and FCB before scheduling or deleting.
- `DokanDeleteFcb` expects VCB and FCB locks to already be held, removes the FCB from the table when requested, frees the filename, tears down oplocks/per-stream contexts/resources, marks the identifier as `FREED_FCB`, unlocks the FCB, and returns it to the lookaside list.
- Deferred GC gives each FCB at least one timer interval of reuse opportunity before deletion. Forced GC deletes all currently scheduled FCBs immediately.
- Rename conflict handling deletes a conflicting FCB if it is already pending GC; otherwise it marks the conflicting FCB `ReplacedByRename` and replaces the AVL table entry.

Dependencies:
- Uses `DokanVCB` state from `dokan.h`: `FcbTable`, `FcbGarbageList`, `FcbGarbageCollectorThread`, `FcbGarbageListNotEmpty`, metrics, and `ValidFcbMask`.
- Depends on global lookaside lists for FCBs and ERESOURCEs.
- Uses Windows kernel primitives: `FsRtlSetupAdvancedHeader`, `FsRtlInitializeOplock`, `RtlInsertElementGenericTableAvl`, `KeWaitForMultipleObjects`, `PsCreateSystemThread`, and resource locks.
- Uses Dokan helpers for VCB/FCB locking, logging, string wrapping, allocation, and identifier checks.

Notable risks:
- The lock contract is strict: deletion paths assume VCB and FCB are locked, while non-final `DokanFreeFCB` intentionally avoids VCB locking.
- `ValidFcbMask` is only a heuristic for rejecting obviously bogus FCB addresses; it cannot prove the pointer is safe.
- GC scheduling uses `NextGarbageCollectableFcb.Flink != NULL` as the “scheduled” marker, so list-entry initialization and clearing are part of the correctness contract.
- Filename buffer ownership is subtle across create, lookup, cancel-GC, rename, and delete paths.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/fcb.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/fcb.h -->
# File Research: sources/windows/dokany/sys/util/fcb.h

Public utility header for Dokan FCB lookup, release, garbage collection, AVL callbacks, and rename support.

Key responsibilities:
- Declares special internal filename constants: `g_KeepAliveFileName` and `g_NotificationFileName`.
- Exposes `DokanGetFCB` and `DokanFreeFCB` as the main FCB acquisition/release API.
- Declares garbage-collection lifecycle helpers: start, schedule, cancel, force, and delete.
- Declares AVL table comparison/allocation/free callbacks used by each volume’s FCB table.
- Declares `DokanRenameFcb` for updating table membership after a rename.

Important behavior documented by the header:
- `DokanFreeFCB` decrements `OpenCount` and either deletes or schedules GC when it reaches zero.
- GC start is optional; callers check whether `Vcb->FcbGarbageCollectorThread` remains `NULL`.
- Schedule, cancel, force, and delete operations require the VCB lock; delete also requires the FCB lock and must not be followed by an unlock of the freed FCB.
- `DokanCancelFcbGarbageCollection` always deletes or takes ownership of `NewFileName->Buffer`.
- `DokanRenameFcb` requires VCB and FCB acquisition before the call.

Dependencies:
- Includes `../dokan.h` for core Dokan types and Windows kernel declarations.
- Function contracts align with the `fcb.c` implementation and volume setup in `fscontrol.c`.

Notable risks:
- The comments encode important ownership and locking rules; violating them can cause use-after-free, leaked filename buffers, or recursive lock deadlocks.
- A typo in the rename comment says “priore,” but the intended contract is clear.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/fcb.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/irp_buffer_helper.c -->
# File Research: sources/windows/dokany/sys/util/irp_buffer_helper.c

IRP input/output buffer discovery and size-management helpers for Dokan dispatch code.

Key responsibilities:
- Determines provided input and output buffer sizes from the current IRP stack location.
- Selects the correct input buffer for buffered/direct/neither IOCTL and FSCTL methods.
- Selects the correct output buffer for IOCTL, FSCTL, directory, query information, security, and volume information IRPs.
- Probes user-mode Type3/UserBuffer pointers before kernel access.
- Prepares fixed-size output structures by zeroing and setting `IoStatus.Information`.
- Extends already-prepared output buffers for variable-sized trailing data.
- Appends `UNICODE_STRING` data into variable-sized output structures.

Important behavior:
- For `METHOD_NEITHER` device/file-system controls, input uses `Type3InputBuffer`; output uses `Irp->UserBuffer`.
- Query security and directory control output paths also use user buffers, with directory control preferring an MDL mapping when present.
- `PrepareOutputWithSize` returns `NULL` on undersized buffers and optionally reports the required size through `IoStatus.Information`.
- `ExtendOutputBufferBySize` treats `IoStatus.Information` as the currently reserved size.
- `AppendVarSizeOutputString` validates that `Dest` lies inside the reserved output buffer, extends if needed, and can optionally copy a whole-character partial string like NTFS behavior.

Dependencies:
- Includes `../dokan.h` and `irp_buffer_helper.h`.
- Uses Windows IRP stack structures, `ProbeForRead`, `ProbeForWrite`, MDL mapping, `RtlZeroMemory`, `RtlCopyMemory`, and Dokan exception filtering.

Notable risks:
- `AppendVarSizeOutputString` relies on prior correct reservation via `PrepareOutputWithSize` or equivalent.
- Size arithmetic combines `ULONG`, `ULONG_PTR`, and pointer offsets; call sites must avoid impossible output layouts and reuse of the same destination.
- Probing protects user buffers, but callers still need correct method-specific assumptions about the IRP they are handling.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/irp_buffer_helper.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/irp_buffer_helper.h -->
# File Research: sources/windows/dokany/sys/util/irp_buffer_helper.h

Header and macro layer for safe Dokan IRP buffer extraction, validation, and output construction.

Key responsibilities:
- Declares input-buffer helpers `GetProvidedInputSize` and `GetInputBuffer`.
- Defines generic input buffer validation macros with configurable exit behavior.
- Defines size-comparison macros for fixed structs and variable-sized structs such as `MOUNTDEV_NAME`, `DOKAN_NOTIFY_PATH_INTERMEDIATE`, and `DOKAN_UNICODE_STRING_INTERMEDIATE`.
- Provides `GET_IRP_BUFFER*` macro variants that return, break, leave, or no-op on failure.
- Declares output helpers for fixed reservation, incremental extension, and variable-length string append.
- Provides `PREPARE_OUTPUT`, a typed convenience macro around `PrepareOutputWithSize`.

Important behavior:
- The input macros fetch the actual buffer through `GetInputBuffer`, assert it is non-null, validate that the provided size fits the expected structure, log invalid sizes, and invoke the selected exit macro.
- Variable-sized input checks validate both fixed header size and embedded length fields against the provided buffer length.
- `DOKAN_UNICODE_STRING_INTERMEDIATE_SIZE_COMPARE` additionally rejects `Length > MaximumLength`.
- The output helper comments define the `IoStatus.Information` convention used by the implementation.

Dependencies:
- Includes `<ntifs.h>` and `../public.h`.
- Used broadly by Dokan dispatch files such as access, device, event, fscontrol, notification, timeout, volume, and fileinfo handlers.

Notable risks:
- The macros assume local variables such as `status` exist for `DOKAN_EXIT_LEAVE` and `DOKAN_EXIT_BREAK`.
- Macro arguments are evaluated in generated blocks and should be simple lvalues.
- The header guard name is `STRUCT_HELPER_H_`, which does not match the filename but is functionally unique in this file.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/irp_buffer_helper.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/log.c -->
# File Research: sources/windows/dokany/sys/util/log.c

Dokan kernel logging implementation for debug prints, Windows Event Log entries, stringification helpers, and cached driver-log delivery to user mode.

Key responsibilities:
- Defines global debug/cache state: `g_Debug`, `g_DokanDriverLogCacheEnabled`, `g_DokanVcbDriverLogCacheCount`, and `g_DokanLogEntryList`.
- Writes formatted wide-character messages to the Windows Event Log via `IO_ERROR_LOG_PACKET`.
- Provides `DokanLogError` and `DokanLogInfo`.
- Captures compact stack traces for diagnostic logging.
- Converts NTSTATUS, IRP major/minor codes, file information classes, filesystem information classes, identifier types, create results, and IOCTLs to readable strings.
- Caches formatted driver log messages and dispatches them to userland as `DOKAN_IRP_LOG_MESSAGE` events.
- Cleans cached log entries associated with a volume during teardown.

Important behavior:
- Event Log messages are capped at `DOKAN_LOG_MAX_CHAR_COUNT` and split into multiple `IO_ERROR_LOG_PACKET`s when they exceed one packet’s string capacity.
- Event Log writing is skipped above `PASSIVE_LEVEL`.
- Cached log entries are capped at 1024; when full, the oldest entry is dropped.
- `PushDokanLogEntry` skips per-volume logs when the volume did not request driver log dispatch.
- `PopDokanLogEntry` sends both global logs and logs for the target VCB, then removes sent entries from the global cache.
- `IsLogCacheEnabled` avoids expensive log formatting unless global or per-volume caching is active.
- `CleanDokanLogEntry` decrements the active cached-log VCB count and removes all cached entries tied to that volume.

Dependencies:
- Includes `log.h`, Dokan core headers, mount/storage Windows headers, and generated include files `ntstatus_log.inc` and `ioctl.inc`.
- Uses Dokan allocation, resource locking, event context allocation, and `DokanEventNotification`.
- Uses Windows kernel routines such as `IoAllocateErrorLogEntry`, `IoWriteErrorLogEntry`, `RtlStringCchVPrintfW`, `RtlStringCchVPrintfExA`, `RtlCaptureStackBackTrace`, and time/query helpers through macros.

Notable risks:
- Cached logging requires `PASSIVE_LEVEL`; high-IRQL callers only debug-print.
- `PopDokanLogEntry` returns without removing entries if event allocation fails, leaving later retry possible but delaying dispatch.
- The global cache mixes global entries and VCB-specific entries, so correct VCB cleanup is important during teardown.
- Stringification tables are manually curated plus generated includes; unknown values fall back to `"Unknown"` or related sentinel strings.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/log.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/log.h -->
# File Research: sources/windows/dokany/sys/util/log.h

Dokan logging API, global cache types, debug macros, IRP logging macros, Event Log helpers, and compact backtrace declarations.

Key responsibilities:
- Defines debug bit flags for normal, lock, and oplock logging.
- Declares global debug state and the `DOKAN_LOG_CACHE`/`DOKAN_LOG_ENTRY` structures.
- Declares cached-log functions: push, clean, enable-check, and active-VCB count increment.
- Defines `DDbgPrint`, timestamped cache push, cached log, no-cache log, and request-aware logging macros.
- Provides IRP-specific logging helpers for begin/end dispatch, IOCTL names, major/minor function names, device-extension type, completion, and status.
- Declares stringification functions implemented in `log.c`.
- Defines `DOKAN_LOGGER`, its initializer macro, Event Log functions, and compact `DokanBackTrace`.

Important behavior:
- `DOKAN_CACHED_LOG` debug-prints when `g_Debug` is enabled and pushes into the cache only at `PASSIVE_LEVEL` when caching is enabled.
- `DOKAN_LOG_INTERNAL` respects `RequestContext->DoNotLogActivity`.
- `DOKAN_LOG_END_MJ` may complete the IRP unless `DoNotComplete` is set or the status is pending.
- `DOKAN_LOG_VCB` synthesizes a temporary `REQUEST_CONTEXT` so VCB-level logs can reuse request-aware caching.
- `DOKAN_DENIED_LOG_EVENT` suppresses noisy event-pull FSCTL logging.

Dependencies:
- Includes `<ntifs.h>` and relies on Dokan types included before/around it in core compilation units.
- Macros call functions from `log.c` and core Dokan completion/event code.

Notable risks:
- Many logging helpers are macros with side effects; call sites must pass valid request contexts and avoid arguments with unwanted repeated evaluation.
- `DOKAN_LOG_END_MJ` is not only logging; it can complete an IRP, so it is part of dispatch control flow.
- Cached logging format paths depend on variadic macro correctness and function-scope `__FUNCTION__`.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/log.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/mountmgr.c -->
# File Research: sources/windows/dokany/sys/util/mountmgr.c

Mount Manager integration helpers for Dokan volume arrival, mount point creation/deletion, delete-point requests, and AutoMount control.

Key responsibilities:
- Sends arbitrary IOCTLs to `\Device\MountPointManager`.
- Notifies Mount Manager about directory mount point creation/deletion for persistent symbolic links.
- Sends volume-arrival notifications for Dokan device names.
- Creates explicit mount points for device names.
- Deletes mount points by symbolic link, device name, or both.
- Queries and sets Mount Manager AutoMount state.
- Provides wrappers for directory mount point created/deleted notifications.

Important behavior:
- `DokanSendIoContlToMountManager` opens the mount manager device, builds a synchronous device-control IRP, waits if pending, uses `iosb.Status`, and dereferences the file object.
- Mount point notification packs `MOUNTMGR_VOLUME_MOUNT_POINT` with source mount point and target persistent symbolic link in a single allocated buffer.
- Volume arrival packs a `MOUNTMGR_TARGET_NAME` with the Dokan device name.
- Delete-points packs optional symbolic link and optional device name into `MOUNTMGR_MOUNT_POINT`, and allocates a small output buffer for deleted points.
- Create-point logs success/failure to the Windows Event Log using `DokanLogInfo`/`DokanLogError`.
- The file comments warn that deleting by drive-letter mount point without a device name can create a Mount Manager database record suppressing future auto-assignment for that drive letter.

Dependencies:
- Includes `mountmgr.h`, which includes Dokan core types and `<mountmgr.h>`.
- Uses Mount Manager IOCTL structures and constants.
- Uses Dokan allocation/logging helpers and Windows I/O routines: `IoGetDeviceObjectPointer`, `IoBuildDeviceIoControlRequest`, `IoCallDriver`, `KeWaitForSingleObject`, and `ObDereferenceObject`.

Notable risks:
- `DokanSendIoContlToMountManager` returns early on `IoBuildDeviceIoControlRequest` failure without dereferencing `mountFileObject`, which is a potential leak on that error path.
- Packing Mount Manager variable-length structures depends on exact byte lengths and offsets.
- The function name `DokanSendIoContlToMountManager` appears to contain a typo, but the declaration and implementation match.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/mountmgr.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/util/mountmgr.h -->
# File Research: sources/windows/dokany/sys/util/mountmgr.h

Header for Dokan Mount Manager helper APIs.

Key responsibilities:
- Declares mount point notification helpers for persistent volume symbolic links.
- Declares AutoMount query and set helpers.
- Declares volume-arrival notification.
- Declares the generic Mount Manager IOCTL send helper.
- Declares directory mount point created/deleted wrappers.
- Declares explicit mount point create and delete-point operations.

Dependencies:
- Includes `../dokan.h` for Dokan device/control block types.
- Includes `<mountmgr.h>` for Mount Manager constants and structures.
- Implemented by `mountmgr.c` and called from mount initialization and teardown paths.

Notable risks:
- Comments contain spelling issues such as “persistante” and “MountManage,” but the API intent is clear.
- The generic IOCTL helper exposes raw buffers and lengths, so callers must construct Mount Manager variable-length structures exactly.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/util/mountmgr.h -->