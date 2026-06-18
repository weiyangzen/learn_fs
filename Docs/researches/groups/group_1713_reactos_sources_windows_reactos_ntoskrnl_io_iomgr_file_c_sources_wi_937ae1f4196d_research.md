# Group Research: group_1713_reactos_sources_windows_reactos_ntoskrnl_io_iomgr_file_c_sources_wi_937ae1f4196d

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/file.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/file.c

This file implements ReactOS I/O manager file-object handling: file creation/open parsing, file object cleanup/delete/close, security descriptor access, name queries, stream file objects, share-access accounting, open cancellation, file-origin flags, and several Nt/Zw file syscalls.

Core open path:
- `IopCreateFile` is the main common implementation behind `IoCreateFile`, `IoCreateFileSpecifyDeviceObjectHint`, `NtCreateFile`, `NtOpenFile`, named pipe creation, and mailslot creation.
- It validates create parameters, probes user outputs, captures optional allocation size, copies and validates EA buffers, fills an `OPEN_PACKET`, calls `ObOpenObjectByName`, then reconciles Object Manager status with `OpenPacket.FinalStatus`.
- `IopParseDevice` is the main Object Manager parse routine for device/file opens. It builds an `IRP_MJ_CREATE`, `IRP_MJ_CREATE_NAMED_PIPE`, or `IRP_MJ_CREATE_MAILSLOT`, allocates a real `FILE_OBJECT` or a stack dummy object for query/delete-only paths, sends the IRP to the chosen device stack, waits when pending, and handles successful opens, failures, and reparses.
- `IopParseFile` handles relative opens through an existing file object by setting `OpenPacket->RelatedFileObject` and delegating to `IopParseDevice`.

Device/volume routing:
- `IopCheckDeviceAndDriver` rejects initializing, unloading, deleting, or removing device objects, enforces exclusive-device opens, and increments the device reference count on success.
- `IopParseDevice` handles related file objects, mounted VPBs, attached devices, direct device opens, volume opens, and optional top-level device hints.
- `IopCheckTopDeviceHint` validates hint use only for filesystem device stacks and rejects hints for direct opens or devices not found on the verified stack.
- Reparse traversal is bounded by `IOP_MAX_REPARSE_TRAVERSAL`; mount-point reparses can set `OpenPacket->TraversedMountPoint` and restart open processing.

Security and privilege handling:
- `IopCheckBackupRestorePrivilege` handles `FILE_OPEN_FOR_BACKUP_INTENT`, checking `SeBackupPrivilege` and `SeRestorePrivilege`, updating `ACCESS_STATE`, and clearing the backup-intent create option if neither privilege applies.
- `IopParseDevice` performs device security checks, traverse checks, secure-open checks, audit calls, and generic access mapping before creating the lower IRP.
- `IopGetSetSecurityObject` handles security query/set/assign/delete for both device objects and file objects. Device security can be read or changed directly; file security is sent down as `IRP_MJ_QUERY_SECURITY` or `IRP_MJ_SET_SECURITY`.
- `IopSetDeviceSecurityDescriptor` updates cached security descriptors under `IopSecurityResource`, retrying if another thread swaps the descriptor concurrently.
- `IopSetDeviceSecurityDescriptors` applies device security along the PDO-to-upper-device chain when a PDO is available.

File object lifetime:
- `IopDeleteFile` sends `IRP_MJ_CLOSE`, optionally sends cleanup first if no handle was created, adjusts VPB/device references, frees `FileName`, releases completion-port context, tears down per-file-object filter contexts, and dereferences the device object.
- `IopCloseFile` runs on handle close. It unlocks outstanding byte-range locks for the process, then sends `IRP_MJ_CLEANUP` on the last system handle.
- `IoCancelFileOpen` sends cleanup for an open that is being cancelled before `FO_HANDLE_CREATED`; calling it after a handle exists bugchecks with `INVALID_CANCEL_OF_FILE_OPEN`.

Name and attribute query helpers:
- `IopQueryNameInternal` combines the device/object name and filesystem `FileNameInformation`, optionally converting the volume device to a DOS name. Network filesystems get a simple root separator for DOS-name queries instead of mount-manager lookup.
- `IoQueryFileDosDeviceName` loops with increasing buffers until `IopQueryNameInternal` succeeds or fails for a reason other than `STATUS_BUFFER_OVERFLOW`.
- `IopQueryAttributesFile`, `NtQueryAttributesFile`, `NtQueryFullAttributesFile`, and `IoFastQueryNetworkAttributes` use dummy file objects and create parsing to obtain basic or network-open information without returning a real handle.

Stream file objects and extensions:
- `IoCreateStreamFileObjectEx`, `IoCreateStreamFileObject`, and `IoCreateStreamFileObjectLite` create internal stream file objects tied to a device or existing file object, mark them `FO_STREAM_FILE`, initialize events, and manage VPB/device references.
- `IopCreateFile` can allocate a `FILE_OBJECT_EXTENSION` for top-device hints.
- `IoGetFileObjectFilterContext` and `IoChangeFileObjectFilterContext` expose atomic get/define/clear behavior for extension filter contexts.

Share access and origin APIs:
- `IoCheckShareAccess`, `IoSetShareAccess`, `IoUpdateShareAccess`, and `IoRemoveShareAccess` implement standard read/write/delete share accounting against `SHARE_ACCESS`.
- `IoSetFileOrigin` toggles `FO_REMOTE_ORIGIN`; `IoIsFileOriginRemote` reads it.

Nt entry points:
- `NtCreateFile` and `NtOpenFile` delegate to `IoCreateFile`.
- `NtCreateMailslotFile` and `NtCreateNamedPipeFile` capture timeout parameters and pass create-specific parameter blocks through `IoCreateFile`.
- `NtCancelIoFile` cancels all IRPs in the current thread whose original file object matches the supplied handle, then waits until they leave the thread IRP list.
- `NtDeleteFile` opens with a dummy object, `FILE_DELETE_ON_CLOSE`, and delete-only semantics.
- `NtFlushWriteBuffer` wraps `KeFlushWriteBuffer`.

Research notes:
- `IoCheckQuerySetFileInformation` and `IoCheckQuotaBufferValidity` are explicit unimplemented stubs.
- `IoCreateFileSpecifyDeviceObjectHint` is marked `@unimplemented` in the comment but contains a working wrapper around `IopCreateFile` with file-object-extension and top-device-hint flags.
- The open path carefully distinguishes Object Manager parse status from the lower I/O status in `OpenPacket.FinalStatus`; callers generally use the lower status only after `ParseCheck` is set.
- Reparse handling is central and delicate: `IopDoNameTransmogrify` validates mount-point reparse data, rewrites `FileObject->FileName`, preserves a reserved suffix, and frees driver-supplied auxiliary reparse data.
- The share-access routines currently bypass checks/updates for any file object with `FO_FILE_OBJECT_HAS_EXTENSION` because the intended `IO_IGNORE_SHARE_ACCESS_CHECK` test is commented out.
- In the device `SetSecurityDescriptor` branch of `IopGetSetSecurityObject`, the function computes `Status` from the descriptor update path but returns `STATUS_SUCCESS`, which may hide device security update failures.
- Manual reference-count and cleanup ordering is a major correctness concern throughout this file: device references, VPB references, file-object references, IRP queueing, dummy file objects, and reparse retry paths all interact.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/file.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iocomp.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iocomp.c

This file implements ReactOS I/O completion objects, modeled as Object Manager objects backed by kernel queues. It also provides completion-packet allocation/freeing and an unload-safe completion routine wrapper.

Global state:
- `IoCompletionType` is the Object Manager type for I/O completion objects.
- `IoCompletionPacketLookaside` is declared for completion packet allocation support.
- `IopCompletionMapping` maps generic rights to `IO_COMPLETION_QUERY_STATE`, `IO_COMPLETION_MODIFY_STATE`, `SYNCHRONIZE`, and `IO_COMPLETION_ALL_ACCESS`.
- `IoCompletionInfoClass` describes `IoCompletionBasicInformation` query validation.

Internal helpers:
- `IopUnloadSafeCompletion` wraps a caller completion routine for `IoSetCompletionRoutineEx`. It references the device object before invoking the real completion routine, dereferences afterward, frees the wrapper context, and returns the real routine status.
- `IopFreeMiniPacket` returns mini completion packets to the per-processor P lookaside list, then the L lookaside list, and finally frees to pool if both lists are at depth.
- `IopDeleteIoCompletion` runs down the queue at object deletion. It frees queued IRP-backed packets with `IoFreeIrp` and non-IRP mini packets through `IopFreeMiniPacket`.

Completion insertion:
- `IoSetIoCompletion` allocates an `IOP_MINI_COMPLETION_PACKET` from the current processor lookaside lists or nonpaged pool, fills key context, APC context, status, and information, then inserts it into the target `KQUEUE`.
- The `Quota` parameter is accepted but not used in the implementation.

Unload-safe completion routines:
- `IoSetCompletionRoutineEx` allocates an `IO_UNLOAD_SAFE_COMPLETION_CONTEXT`, stores the target device, user context, and completion routine, then installs `IopUnloadSafeCompletion` as the IRP completion routine.

Nt entry points:
- `NtCreateIoCompletion` probes the output handle for user callers, creates an `IoCompletionType` object sized as a `KQUEUE`, initializes the queue with the requested concurrency count, inserts the object, and returns the handle.
- `NtOpenIoCompletion` opens an existing completion object by name and returns a handle.
- `NtQueryIoCompletion` validates query buffers, references the completion object with `IO_COMPLETION_QUERY_STATE`, returns queue depth as `IO_COMPLETION_BASIC_INFORMATION.Depth`, and optionally writes the result length.
- `NtRemoveIoCompletion` references the queue with `IO_COMPLETION_MODIFY_STATE`, removes the next queued entry with optional timeout, distinguishes timeout/user APC status from real list entries, handles both IRP-backed completion packets and mini packets, writes key/APC/status results, and dereferences the queue.
- `NtSetIoCompletion` references the queue with modify access and delegates packet insertion to `IoSetIoCompletion`.

Research notes:
- The queue stores two packet shapes: IRP-backed entries where `IRP.Tail.Overlay.ListEntry` is embedded, and standalone `IOP_MINI_COMPLETION_PACKET` entries allocated from lookaside/pool.
- `NtRemoveIoCompletion` frees IRPs after extracting completion data, so ownership transfers to the completion port queue before removal.
- User buffer probing and result writes are consistently wrapped in SEH.
- The implementation depends on per-processor lookaside accounting fields (`TotalAllocates`, `AllocateMisses`, `TotalFrees`, `FreeMisses`) being updated manually.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/iocomp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/ioevent.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/ioevent.c

This file provides I/O manager wrappers for creating named executive event objects.

Internal helper:
- `IopCreateEvent` builds kernel object attributes with `OBJ_OPENIF | OBJ_KERNEL_HANDLE`, calls `ZwCreateEvent` with `EVENT_ALL_ACCESS`, references the resulting event object with `ObReferenceObjectByHandle`, then immediately drops the extra object reference while returning both the object pointer and the kernel handle.
- If event creation or object referencing fails, it returns `NULL`; on reference failure it also closes the handle.

Public APIs:
- `IoCreateNotificationEvent` calls `IopCreateEvent` with `NotificationEvent`.
- `IoCreateSynchronizationEvent` calls `IopCreateEvent` with `SynchronizationEvent`.

Research notes:
- Events are created initially signaled (`TRUE` in `ZwCreateEvent`).
- Returned handles are kernel handles because the helper always sets `OBJ_KERNEL_HANDLE`.
- The object pointer remains valid by virtue of the returned handle holding the object alive, despite the helper dereferencing the temporary object reference before returning.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/ioevent.c -->