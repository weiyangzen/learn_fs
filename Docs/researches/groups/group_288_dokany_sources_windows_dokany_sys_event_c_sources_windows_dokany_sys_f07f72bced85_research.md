# Group Research: group_288_dokany_sources_windows_dokany_sys_event_c_sources_windows_dokany_sys_f07f72bced85

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/event.c -->
# File Research: sources/windows/dokany/sys/event.c

Implements Dokan's central kernel/user event IPC path: pending IRP registration, cancellation, completion from user mode, mount start, replacement-drive handling, and large write event handoff.

Key entry points:
- `DokanRegisterPendingIrp()` registers a filesystem IRP on `Dcb->PendingIrp`, assigns a serial number, installs the cancel routine, and queues an `EVENT_CONTEXT` for user mode.
- `RegisterPendingIrpMain()` is the shared registration helper for normal pending IRPs, retry IRPs, and async create failures.
- `DokanCompleteIrp()` consumes one or more `EVENT_INFORMATION` replies from user mode, matches them by serial number, removes pending IRPs, handles forced-canceled create races, and dispatches to per-major completion routines.
- `DokanDispatchCompletion()` routes completed events to read, write, create, cleanup, query/set information, volume, lock, flush, and security completion handlers.
- `DokanEventStart()` handles `FSCTL_EVENT_START`, validates the user-mode version and mount inputs, creates a disk/network device, inserts a mount entry, starts notification support, verifies/mounts the volume, and returns `EVENT_DRIVER_INFO`.
- `DokanEventWrite()` provides the second-stage transfer path for large write event contexts.
- `DokanCreateIrpCancelRoutine()` and `DokanIrpCancelRoutine()` handle create-specific cancellation via timeout wakeup and non-create cancellation directly.
- `DokanOplockComplete()` and `DokanPrePostIrp()` bridge FsRtl oplock completion back into Dokan's pending-event flow.

Core mechanics:
- Pending IRPs carry `IRP_ENTRY` records linked into `IRP_LIST` instances with a timeout tick, serial number, copied `REQUEST_CONTEXT`, and async status.
- Create IRP cancellation is intentionally deferred to the timeout path because create cleanup is too complex for an arbitrary cancel-routine context.
- Non-create cancellation removes the IRP from its list, frees any saved write `EVENT_CONTEXT`, optionally executes cleanup at passive level, and completes with `STATUS_CANCELLED`.
- Completion batching is allowed only when `Dcb->AllowIpcBatching` is enabled; replies must be sorted by serial number.
- Invalid batched replies, oversized replies, or unexpected batching are treated as DLL misuse and can trigger unmount to avoid permanently hung requests.
- Mount startup normalizes drive-letter mount points to `\DosDevices\X:`, supports current-session mounts, mount-manager integration, write-protect/removable flags, case-sensitivity flags, alternate streams, user-mode file locks, driver log dispatch, IPC batching, and optional volume security descriptors.
- Existing Dokan drive replacement is allowed only when the old and new device owners match.

Important invariants:
- IRP state and driver-context pointers are initialized before a cancel routine is installed.
- Unmount state is checked before and after list locking to avoid registering IRPs that can never complete.
- The event context size must not exceed `EVENT_CONTEXT_MAX_SIZE`, except write uses a special two-step path.
- Once a cancel routine is observed as already running, ownership transfers to that routine or to forced-cancel handling.
- Mount entries are protected by global and per-entry resources and must be released in the right order.

Filesystem relevance:
- This file is the heart of Dokan's FUSE-like bridge. It decides when kernel filesystem IRPs are converted into user-mode operations, how replies complete original IRPs, and how a user-mode filesystem instance becomes a mounted Windows volume.

Notable risks:
- Completion batching is delicate: bad serial ordering or size calculation can leave requests unmatched, so the driver unmounts on detected misuse.
- Create cancellation has multiple race paths between user-mode reply, cancel routine, and timeout thread.
- Mount replacement depends on security descriptor owner comparison and mount-entry removal being accurate.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/event.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/except.c -->
# File Research: sources/windows/dokany/sys/except.c

Provides Dokan's structured exception filter and fallback IRP completion handler for expected NTSTATUS exceptions.

Key entry points:
- `DokanExceptionFilter()` logs exception and context records, catches only exceptions considered expected by `FsRtlIsNtstatusExpected()`, and otherwise continues exception search.
- `DokanExceptionHandler()` validates the target VCB, maps unmount state to `STATUS_NO_SUCH_DEVICE`, and completes the IRP unless the exception status is `STATUS_PENDING`.

Core mechanics:
- Expected filesystem exceptions are converted into normal handler execution.
- Unexpected exceptions are deliberately passed to a higher-level handler.
- IRPs are completed with zero `IoStatus.Information` on handled failures.
- Invalid/missing VCB state maps to `STATUS_INVALID_PARAMETER`.

Filesystem relevance:
- This is defensive kernel-driver error containment around Dokan IRP dispatch paths.

Notable risks:
- It assumes `DeviceObject->DeviceExtension` is a VCB for handled IRPs; unusual device-object contexts fall back to invalid parameter.
- `STATUS_PENDING` is not completed, preserving ownership semantics for paths where another component owns the IRP.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/except.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/fileinfo.c -->
# File Research: sources/windows/dokany/sys/fileinfo.c

Implements `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION` dispatch/completion, including local answers for name/position classes, user-mode metadata requests, cache flushing, rename event construction, FCB rename updates, and file-change notifications.

Key entry points:
- `DokanDispatchQueryInformation()` handles query classes directly where possible and otherwise sends `FILEINFO_CONTEXT` to user mode.
- `DokanCompleteQueryInformation()` copies returned file information to the IRP buffer, updates FCB allocation/file size for standard/all/network-open information, and fills name/delete-pending fields for local consistency.
- `DokanDispatchSetInformation()` validates set-information requests, handles position locally, checks truncation against mapped sections, flushes cache around EOF/rename, builds `SETFILE_CONTEXT`, performs oplock checks, and registers the IRP.
- `DokanCompleteSetInformation()` applies successful delete-pending and rename results to FCB/file-object state and emits directory/file notifications.
- `FillNameInformation()` populates `FILE_NAME_INFORMATION`, including UNC/device path prefixing for network filesystems.
- `FlushFcb()`, `FlushIfDescendant()`, and `FlushAllCachedFcb()` flush and purge cache mappings for files or descendant files before rename-sensitive operations.
- `PopulateRenameEventInformations()` converts Windows rename inputs into Dokan's architecture-neutral rename payload.
- `GetParentDirectoryEndingIndex()` and `IsInSameDirectory()` classify rename notifications as same-directory rename versus remove/add.

Core mechanics:
- `FileNameInformation`, `FileNormalizedNameInformation`, `FilePositionInformation`, and `FileNetworkPhysicalNameInformation` are served in kernel when possible.
- Alternate stream queries are rejected unless `Dcb->UseAltStream` is set.
- User-mode query events include the file information class, requested output buffer length, user context, and FCB filename.
- Set-information events include the original file info buffer or a packed `DOKAN_RENAME_INFORMATION` buffer for rename operations.
- Rename construction handles simple same-directory rename, fully qualified target file objects, relative rename with `RootDirectory`, alternate-stream rename, and trailing slash cleanup.
- Delete-pending state is mirrored between FCB flags and `FileObject->DeletePending` after user mode succeeds.
- Rename completion updates the FCB name through `DokanRenameFcb()` and reports old/new name notifications, or remove/add notifications when crossing directories.

Important invariants:
- FCB locks protect filename reads, metadata changes, and cache flush decisions.
- VCB is locked before FCB during successful rename completion to match create-path lookup locking.
- Truncation is rejected with `STATUS_USER_MAPPED_FILE` when `MmCanFileBeTruncated()` says mapped views prevent it.
- Rename event sizes are dry-run calculated before allocation to avoid overflow.

Filesystem relevance:
- This file is Dokan's main metadata bridge for stat-like queries, size/allocation changes, delete disposition, rename, timestamp/attribute updates, and resulting change notifications.

Notable risks:
- `IsInSameDirectory()` is explicitly case-sensitive even when the mounted filesystem may be case-insensitive.
- Rename handling is structurally complex because Windows exposes multiple rename forms and 32/64-bit incompatible `FILE_RENAME_INFORMATION`.
- Cache purge/flush ordering matters for mapped files and directory subtree renames.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/fileinfo.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/flush.c -->
# File Research: sources/windows/dokany/sys/flush.c

Implements `IRP_MJ_FLUSH_BUFFERS` dispatch and completion.

Key entry points:
- `DokanDispatchFlush()` validates the file object/CCB, builds a `FLUSH_CONTEXT` with the target filename, uninitializes the cache map, performs an oplock check, and registers the IRP for user mode.
- `DokanCompleteFlush()` updates the CCB user context and completes with the status returned by user mode.

Core mechanics:
- Invalid or missing file context is treated as success, matching flush permissiveness for some close/volume edge cases.
- The FCB is locked read-only while the event context is built.
- `CcUninitializeCacheMap()` is called before the flush is forwarded to user mode.
- Oplock checks can post the IRP pending before normal Dokan registration.

Filesystem relevance:
- Flush connects Windows flush semantics to the user-mode filesystem and cache manager state.

Notable risks:
- Flush completion trusts user-mode status and does not itself force data persistence.
- The FCB unlock in `finally` assumes `fcb` was set only after locking; current flow satisfies that.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/flush.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/fscontrol.c -->
# File Research: sources/windows/dokany/sys/fscontrol.c

Implements filesystem-control dispatch: oplock FSCTLs, Dokan global/volume/disk user FSCTL routing, event-pull batching, mount-volume creation, VPB initialization, and directory reparse-point FSCTL helpers.

Key entry points:
- `DokanDispatchFileSystemControl()` routes mount-volume and user filesystem requests.
- `DokanUserFsRequest()` chooses global, volume, or disk request handling based on the request context.
- `DokanGlobalUserFsRequest()` handles driver-wide controls such as event start/release, debug mode, version, mount list, and session cleanup.
- `DokanVolumeUserFsRequest()` handles keepalive activation, path notification, oplocks, simple volume controls, and selected network FSCTL forwarding.
- `DokanDiskUserFsRequest()` handles event process-and-pull, event release/write, volume metrics, timeout reset, and access token retrieval.
- `DokanProcessAndPullEvents()` completes an optional prior event reply, waits for queued work, and fills the current IOCTL buffer with queued `EVENT_CONTEXT` items.
- `PullEvents()` drains the notify queue into the user-mode output buffer, respecting IPC batching.
- `DokanOplockRequest()` validates and services oplock FSCTLs through `FsRtlOplockFsctrl()`.
- `DokanMountVolume()` creates the VCB volume device for a Dokan disk device and registers it with mount manager / UNC provider paths.
- `CreateSetReparsePointRequest()`, `CreateRemoveReparsePointRequest()`, and `SendDirectoryFsctl()` manage directory mount-point reparse data.
- `DokanInitVpb()` initializes VPB fields for a mounted volume.

Core mechanics:
- Oplock request handling validates CCB/FCB/VCB/DCB identity, rejects invalid directory oplocks, checks delete-pending state, and may include byte-range lock state in `oplockCount`.
- `FSCTL_REQUEST_OPLOCK` input/output sizes are explicitly validated for modern oplock requests.
- `FSCTL_ACTIVATE_KEEPALIVE` activates only the special keepalive FCB and prevents multiple active keepalive handles.
- `FSCTL_NOTIFY_PATH` lets user mode inject a path change notification and cleans all waiters on invalid object-name status.
- Event pulling uses `Dcb->NotifyIrpEventQueue` as the waitable signal and `Dcb->NotifyEvent.ListHead` as the actual work queue.
- Mount-volume walks lower device objects to find a DCB even if a filter wraps the Dokan disk device.
- Mounting creates the VCB, initializes FCB table, notify state, advanced FCB header, VPB, direct I/O, mount-entry volume pointer, timeout thread, mount-manager arrival, and network UNC provider registration.

Important invariants:
- After `FsRtlOplockFsctrl()`, Dokan no longer owns the IRP and sets `DoNotComplete`.
- Event-pull output must have room for at least `EVENT_CONTEXT`.
- The notify queue is reflagged when events remain after a partial pull.
- Mount entries must exist when `DokanMountVolume()` links a VCB to the DCB.
- Directory mount-point reparse operations temporarily clear top-level IRP state to avoid recursive filesystem issues.

Filesystem relevance:
- This file connects Dokan to Windows filesystem-control infrastructure, including mount recognition, oplocks, change notification injection, driver control IOCTLs, and the main event-pull loop used by user-mode filesystems.

Notable risks:
- Oplock and byte-range-lock interactions depend on exact lock ordering and FsRtl ownership semantics.
- Mount-volume lower-device probing intentionally reduces noise after a first successful mount but can obscure startup failures.
- Event-pull batching must preserve queued items when the current user buffer is too small.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/fscontrol.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/init.c -->
# File Research: sources/windows/dokany/sys/init.c

Implements global driver device creation, per-mount disk device creation, mount-entry management, mount-point symbolic links, UNC provider registration, device-delete delay handling, and teardown staging.

Key entry points:
- `DokanCreateGlobalDiskDevice()` creates the global control device, disk/CD filesystem recognizer devices, symbolic link, resources, mount/delete lists, and delayed-delete thread.
- `DokanCreateDiskDevice()` creates a per-mount disk device, names it from a generated GUID, initializes its DCB, IRP/event queues, resources, cache callbacks, mount point, UNC name, symbolic link, and output `DOKAN_CONTROL`.
- `DokanDeleteDeviceObject()` removes mount entries, disables interfaces, deregisters network provider, logs allocation counters, and queues disk/volume devices for delayed deletion.
- `DokanDeleteDeviceThread()` and `DeleteDeviceDelayed()` periodically delete volume/disk device objects once reference counts drain.
- `InsertMountEntry()`, `RemoveMountEntry()`, `FindMountEntry()`, `FindMountEntryByName()`, and `DokanGetMountPointList()` manage the global mount table.
- `InsertDeviceToDelete()`, `InsertDcbToDelete()`, and `FindDeviceForDeleteBySessionId()` manage delayed deletion records and session cleanup.
- `IsMounted()`, `IsDeletePending()`, `IsUnmountPending()`, and `IsUnmountPendingVcb()` centralize lifecycle state checks.
- `DokanCreateMountPoint()`, `DokanDeleteMountPoint()`, `DeleteMountPointSymbolicLink()`, and system-thread helper routines create/delete drive-letter or directory mount links.
- `DokanRegisterUncProvider()` and `DokanDeregisterUncProvider()` register network filesystems with MUP.
- `DokanSetVolumeSecurity()` applies an optional DACL to the created volume device.

Core mechanics:
- The global device registers Dokan filesystem devices with `IoRegisterFileSystem()` and marks them for direct I/O and low-priority filesystem ordering.
- Disk device creation distinguishes disk and network filesystems, disables mount manager for network filesystems, and normalizes mount-point strings under `\DosDevices\`.
- DCB initialization creates pending IRP, notify event, and pending retry lists; initializes remove lock, kill/release/force-timeout events, resources, and cache-manager no-op callbacks.
- Mount entries have a global list lock and per-entry resource. Lookup can match by mount point/session or disk device name.
- Non-admin mount list retrieval filters out mount points from other sessions.
- Delayed deletion waits several cycles and requires reference counts to drop before deleting symbolic links and device objects.
- Mount-manager removal differs for drive-letter versus directory mount points: drive letters use volume delete points, directories delete reparse points and notify mount manager.

Important invariants:
- Delayed deletion avoids deleting device objects while outstanding references remain.
- Mount-point list and mount-entry resources must be acquired in consistent order; `RemoveMountEntry()` refetches under list lock for this reason.
- Session-specific mount cleanup keeps deletion entries alive until the session mount-point link has been removed.
- Network UNC provider operations run in a system thread.
- DCB names are freed only after symbolic link/device teardown has reached the delayed-delete stage.

Filesystem relevance:
- This file is Dokan's lifecycle and namespace foundation: it creates Windows-visible devices and mount points, tracks active mounts, and safely tears down volume/disk objects after unmount.

Notable risks:
- `RemoveMountEntry()` returns early without releasing `MountPointListLock` if the entry is already removed; that path is worth auditing.
- Device deletion relies on reference counts and a fixed minimum delay before deleting objects.
- Mount-manager and directory reparse-point paths are sensitive to reentrant mount operations and global automount state.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/init.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/lock.c -->
# File Research: sources/windows/dokany/sys/lock.c

Implements byte-range lock control, either in-kernel through FsRtl or forwarded to user mode when configured.

Key entry points:
- `DokanDispatchLock()` validates file context, locks the FCB, chooses kernel versus user-mode lock handling, and builds `LOCK_CONTEXT` for user-mode file lock mode.
- `DokanCommonLockControl()` handles normal kernel file locks with oplock coordination and `FsRtlProcessFileLock()`.
- `DokanCompleteLock()` completes user-mode lock requests with the returned status.

Core mechanics:
- Directories reject byte-range lock requests.
- In kernel-lock mode, Dokan checks whether the operation can interfere with oplocks, waits/breaks oplocks when needed, then calls `FsRtlProcessFileLock()`.
- After `FsRtlProcessFileLock()`, Dokan sets `DoNotComplete` because FsRtl owns IRP completion.
- In user-mode lock mode, the event includes byte offset, length, key, user context, and filename.
- `Length == NULL` is tolerated with logging.

Filesystem relevance:
- This file controls Windows byte-range locking semantics for Dokan filesystems and determines whether lock correctness is enforced by the kernel or delegated to the user-mode filesystem.

Notable risks:
- Oplock interaction is conditional on Windows version helper availability and allocation-size checks.
- User-mode file lock mode shifts correctness responsibility out of the kernel.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/notification.c -->
# File Research: sources/windows/dokany/sys/notification.c

Implements event context allocation, notify queue insertion, pending IRP release/retry helpers, the retry notification thread, change-notification cleanup, FCB garbage collector stop, volume event release/unmount, and global mount-point release.

Key entry points:
- `AllocateEventContextRaw()` and `AllocateEventContext()` allocate driver-owned event records and initialize common event fields.
- `SetCommonEventContext()` fills mount id, major/minor IRP function, flags, file flags, and process id.
- `DokanEventNotification()` enqueues an event for user-mode pulling and signals `NotifyIrpEventQueue`.
- `MoveIrpList()` safely drains an `IRP_LIST`, filtering canceled IRPs and preserving forced-canceled create entries for later completion.
- `ReleasePendingIrp()`, `ReleaseNotifyEvent()`, and `RetryIrps()` cancel pending IRPs, free queued notification events, or redispatch retry IRPs.
- `NotificationThread()` waits for release or retry work and redispatches pending retry IRPs.
- `DokanStartEventNotificationThread()` and `DokanStopEventNotificationThread()` manage the retry notification thread.
- `DokanCleanupAllChangeNotificationWaiters()` wraps `FsRtlNotifyCleanupAll()`.
- `DokanEventRelease()` performs the core unmount/release sequence for a mounted volume.
- `DokanGlobalEventRelease()` resolves a mount point to a mounted volume and invokes `DokanEventRelease()`.
- `GetCurrentSessionId()` reads the requestor session id.

Core mechanics:
- `DRIVER_EVENT_CONTEXT` embeds `EVENT_CONTEXT`; allocation size accounts for variable-length operation payloads.
- Notification events are protected by spin locks, while user-mode waiters block on a kernel queue.
- Release cancels pending normal/retry IRPs, frees notification events, stops timeout and notification threads, rundowns the event queue, stops FCB garbage collection, clears mounted state, deletes lookaside lists, cleans directory notification waiters, drains the remove lock, and queues device deletion.
- Global release accepts a mount-point intermediate string, normalizes drive letters to `\DosDevices\X:`, session-scopes lookup, verifies mounted state, and rejects busy/not-mounted devices.

Important invariants:
- Event contexts are freed by converting back to containing `DRIVER_EVENT_CONTEXT`.
- Forced-canceled create IRPs must not be dropped when draining lists; they still require create-cancel completion.
- Unmount sets both `VCB_DISMOUNT_PENDING` and `DCB_DELETE_PENDING` before releasing queues and stopping threads.
- Remove lock is acquired before release work and released with wait before device deletion.

Filesystem relevance:
- This is the teardown and event-notification control plane for Dokan volumes. It ensures user-mode events, retries, directory notifications, and pending IRPs are drained when a filesystem exits or unmounts.

Notable risks:
- Unmount ordering is complex; mount-point deletion must happen before pending IRP release for mount-manager interactions.
- `DokanStopEventNotificationThread()` only waits when `KeSetEvent()` reports previous signal state greater than zero, which may deserve scrutiny.
- Global release depends on mount-entry volume pointers being populated after successful mount.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/notification.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/public.h -->
# File Research: sources/windows/dokany/sys/public.h

Defines Dokan's public kernel/user ABI: IOCTL/FSCTL codes, driver version, event context structures, event reply structures, mount/start flags, driver-info flags, mount-point info, and special names.

Key contents:
- Version and limits: `DOKAN_DRIVER_VERSION`, `EVENT_CONTEXT_MAX_SIZE`, `VOLUME_SECURITY_DESCRIPTOR_MAX_SIZE`, default sector/allocation/disk sizes, default event-info buffer sizes.
- FSCTL codes: version/debug, event start/release/write/process-and-pull, timeout reset, access token, mount-point list/cleanup, keepalive activation, path notification, volume metrics.
- File/CCB/FCB flags: directory, deleted/opened, delete-on-close, paging/synchronous/nocache, retry create, notify-list use, last-write change, delete-pending.
- Mount device types: disk filesystem and network filesystem.
- Special FCB names: keepalive and notification files.
- Intermediate structures for variable strings, notify path, access state, IO security context, and create security payloads.
- Operation payload structs: create, cleanup, close, directory, read, write, file info, set file, volume, lock, flush, unmount, query security, set security.
- `EVENT_CONTEXT`: variable-length kernel-to-user request envelope with common fields and operation union.
- `EVENT_INFORMATION`: user-to-kernel reply envelope with serial number, status, operation-specific result union, context, buffer length, pull timeout, and inline buffer.
- `VOLUME_METRICS`: counters for FCB garbage collection, allocations/deletions, cancellations, and oversized IRP registration cancellation.
- Mount options: alternate streams, write-protect, removable, mount manager, current session, user-mode file locks, case-sensitive, network unmount, driver log dispatch, IPC batching, drive-letter-in-use.
- `EVENT_DRIVER_INFO` and mount result flags describing forced mount, auto-assign request, old-drive replacement, no mount point, and reparse-point failure.
- `EVENT_START`: user-mode mount request, including device type, flags, mount point, UNC name, timeout, FCB GC interval, and optional volume security descriptor.
- `DOKAN_RENAME_INFORMATION`: architecture-neutral rename payload.
- `DOKAN_MOUNT_POINT_INFO`: mount-list record returned to callers.
- `DOKAN_LOG_MESSAGE`: driver log message payload dispatched through the event mechanism.

Core mechanics:
- The ABI uses fixed headers plus trailing variable arrays to marshal file names, security descriptors, read/write buffers, search patterns, and rename targets.
- Several intermediate structures replace kernel pointer-rich types with offsets for safe cross-boundary copying.
- `WRITE_MAX_SIZE` reserves room for `EVENT_CONTEXT` and a conservative filename allowance inside the maximum event context size.
- `DOKAN_EVENT_INFO_DEFAULT_SIZE` pools page-sized reply buffers for common read/write replies.

Filesystem relevance:
- This header is the contract between the Dokan kernel driver and user-mode filesystem library. Any layout or flag change affects IPC compatibility.

Notable risks:
- Structure packing, pointer-size differences, and offset alignment are central ABI concerns, especially rename and security payloads.
- Fixed-size mount/UNC/device arrays constrain path lengths.
- Driver/user version mismatch is explicitly checked at mount start.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/public.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/read.c -->
# File Research: sources/windows/dokany/sys/read.c

Implements `IRP_MJ_READ` dispatch and completion.

Key entry points:
- `DokanDispatchRead()` validates read requests, handles special recognizer/complete cases, creates MDLs when needed, checks cache/oplocks/byte-range locks, builds `READ_CONTEXT`, and registers the pending IRP.
- `DokanCompleteRead()` maps the target buffer, copies user-mode data into it, updates synchronous current byte offset, sets status/information, and frees Dokan-allocated MDLs.

Core mechanics:
- Zero-length reads complete immediately.
- `IRP_MN_COMPLETE` clears `MdlAddress` and succeeds.
- File-system recognizer reads with no `FileObject` but an MDL are treated as successful and report the requested length.
- `FILE_USE_FILE_POINTER_POSITION` uses `FileObject->CurrentByteOffset`; otherwise the IRP byte offset is used.
- If the IRP has no MDL, Dokan allocates one so completion can occur in another thread context.
- Directories reject reads.
- Paging, synchronous, and no-cache state is reflected into event file flags.
- Non-paging reads flush cache for existing data sections before dispatch, then perform oplock and byte-range lock checks.
- Completion copies `EventInfo->Buffer` to the MDL or user buffer and updates `FO_SYNCHRONOUS_IO` current byte offset only for successful non-paging reads with data.

Important invariants:
- Read buffer length must be at least the returned user-mode buffer length.
- FCB filename is read under FCB lock while building the event.
- Oplock failure frees the event context unless the IRP has been posted pending.
- Dokan frees only MDLs it allocated, tracked by `DOKAN_MDL_ALLOCATED`.

Filesystem relevance:
- This is Dokan's main data-read path from Windows callers to user-mode filesystem implementation and back into the original IRP buffer.

Notable risks:
- Completion trusts user mode's returned current byte offset for synchronous reads.
- Recognizer reads are stubbed as success rather than returning real boot-sector data.
- Cache flush before non-paging read is conservative and may affect performance.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/security.c -->
# File Research: sources/windows/dokany/sys/security.c

Implements security descriptor query and set dispatch/completion for files.

Key entry points:
- `DokanDispatchQuerySecurity()` validates file context, builds a `SECURITY_CONTEXT`, optionally creates an MDL for the caller's security output buffer, and registers the request.
- `DokanCompleteQuerySecurity()` validates returned relative security descriptors, copies them to the caller buffer, reports overflow sizes, updates context, and frees allocated MDLs.
- `DokanDispatchSetSecurity()` packages a self-relative security descriptor into `SET_SECURITY_CONTEXT` with aligned buffer offset and registers the request.
- `DokanCompleteSetSecurity()` updates context, reports security change notifications on success, and completes with user-mode status.

Core mechanics:
- Query logs requested owner/group/DACL/SACL/label security information flags.
- Query uses the original requested security buffer length and an MDL when `UserBuffer` is present.
- Returned descriptors are accepted only if `RtlValidRelativeSecurityDescriptor()` validates them for the requested security information.
- Buffer overflow is reported with `IoStatus.Information` set to the needed returned length.
- Set assumes the incoming descriptor is self-relative and uses `RtlLengthSecurityDescriptor()` for payload size.
- Set aligns the security descriptor buffer offset to a 4-byte boundary for Win32 compatibility.
- Oversized set-security events beyond `EVENT_CONTEXT_MAX_SIZE` are rejected.

Filesystem relevance:
- This file bridges Windows security descriptor operations to user-mode filesystems while preserving descriptor validation and change notification behavior.

Notable risks:
- Set-security currently has no large-buffer fallback path; oversized descriptors fail.
- Query completion only copies through an MDL-mapped buffer, so buffer setup must be correct.
- Security descriptor validity is checked on query replies, but set payload validity is mostly assumed from the incoming kernel parameter.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/security.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/sys/timeout.c -->
# File Research: sources/windows/dokany/sys/timeout.c

Implements pending IRP timeout handling, timeout reset, timeout worker thread lifecycle, and unmount-on-timeout behavior.

Key entry points:
- `DokanUnmount()` invokes `DokanEventRelease()` for the DCB's VCB.
- `ReleaseTimeoutPendingIrp()` scans pending IRPs, removes timed-out or async-failed entries, cancels/finishes them, and may unmount before keepalive activation.
- `DokanResetPendingIrpTimeout()` updates a pending IRP timeout from a user-mode `EVENT_INFORMATION` reset request.
- `DokanTimeoutThread()` waits on kill, force-timeout, or periodic timer events and runs timeout release unless the system appears to have resumed from sleep.
- `DokanStartCheckThread()` and `DokanStopCheckThread()` manage the timeout thread.
- `DokanUpdateTimeout()` converts a millisecond timeout into a future tick count.

Core mechanics:
- Pending IRPs normally time out when current tick count reaches `IRP_ENTRY.TickCount`.
- `AsyncStatus` allows async operations such as cancellation/oplock failure to reuse timeout cleanup with a specific failure status.
- Forced-canceled create IRPs are always effectively canceled in this timeout path.
- Non-create IRPs race with cancel routines through `IoSetCancelRoutine(NULL)`; if cancellation is already running, memory ownership is handed to the cancel routine.
- Timed-out create IRPs call `DokanCancelCreateIrp()` with `STATUS_CANCELLED` if explicitly canceled or `STATUS_INSUFFICIENT_RESOURCES` if timed out.
- Timed-out cleanup IRPs execute cleanup before completion.
- If any IRP times out before keepalive activation, Dokan unmounts the filesystem to avoid repeated Explorer delays.
- Sleep/resume detection skips timeout processing when the periodic timer was delayed far beyond the check interval.

Important invariants:
- Pending list scanning is protected by `Dcb->PendingIrp.ListLock`.
- Cancel routines are cleared before completing IRPs outside the list.
- `DRIVER_CONTEXT_IRP_ENTRY` is cleared before completion to prevent later cancel-routine action.
- Timeout reset caps values at `DOKAN_IRP_PENDING_TIMEOUT_RESET_MAX`.
- Stop waits for the timeout thread and dereferences its object.

Filesystem relevance:
- This file enforces liveness for user-mode filesystem operations. It prevents abandoned pending IRPs from hanging indefinitely and triggers unmount when the user-mode side fails during startup.

Notable risks:
- Timeout completion paths overlap with user-mode replies and cancel routines, making ownership transitions subtle.
- Sleep detection intentionally avoids false timeout storms after resume.
- Pre-keepalive unmount changes mount lifecycle based on early operation timeouts.
<!-- END FILE RESEARCH: sources/windows/dokany/sys/timeout.c -->