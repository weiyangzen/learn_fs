# Group Research: ReactOS ntoskrnl I/O manager IRP, volume, rawfs, and PnP arbiters

Scope: `Docs/research_subset_a.md`, source tree `sources/windows/reactos`.

This group covers ReactOS kernel I/O-manager code around IRP allocation/completion, interrupt wrappers, boot ramdisk setup, RawFS fallback mounting, remove locks, object-manager symbolic links, general I/O utility APIs, volume/file-system registration and mounting, PnP resource dump declarations, and new root arbiter skeletons.

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/irp.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/irp.c

## Role

`irp.c` implements core Windows-compatible IRP lifecycle services: allocation and lookaside reuse, construction helpers for FSD and IOCTL requests, synchronous forwarding, cancellation, thread IRP list management, completion unwinding, APC-based final completion, associated IRPs, reserve IRP handling, and requestor identity helpers. It is one of the central I/O-manager files because nearly every filesystem or storage path eventually relies on `IofCallDriver()` and `IofCompleteRequest()`.

## Main entry points and behavior

- `IoAllocateIrp()` allocates an IRP either from per-processor small/large lookaside lists or nonpaged pool, sets quota/fixed-size/lookaside allocation flags, initializes the packet with `IoInitializeIrp()`, and records allocation metadata for `IoFreeIrp()` (lines 610-709).
- `IoFreeIrp()` validates that the packet is detached from the thread IRP list and has advanced past the stack, then returns it to pool or the correct lookaside list, including quota return and lookaside-float accounting (lines 1661-1741).
- `IopInitializeReserveIrp()`, `IopAllocateReserveIrp()`, and `IopFreeReserveIrp()` provide a single preallocated reserve IRP with stack size 20, serialized through an interlocked in-use flag and event (lines 547-606). Completion of reserve synchronous paging IRPs returns the packet to the reserve allocator instead of freeing it (lines 1488-1502).
- `IoBuildAsynchronousFsdRequest()` creates read/write/flush/shutdown/PnP/power style IRPs and prepares buffered, direct, or neither I/O according to target device flags. It sets read/write byte offsets and stores caller `IO_STATUS_BLOCK` and thread (lines 745-874).
- `IoBuildSynchronousFsdRequest()` wraps the asynchronous builder, adds the caller event, and queues the IRP on the requestor thread cleanup/cancel list (lines 1064-1094).
- `IoBuildDeviceIoControlRequest()` builds external or internal device-control IRPs, handling `METHOD_BUFFERED`, direct methods, and `METHOD_NEITHER`, with MDL probing for direct output buffers and cleanup on probe failure (lines 876-1062).
- `IofCallDriver()` advances the IRP stack, stores the target device in the next stack location, and dispatches to the driver major-function table. It bugchecks on stack exhaustion (lines 1253-1288).
- `IofCompleteRequest()` is the completion engine. It detects double completion, walks stack locations upward, invokes completion routines according to success/error/cancel flags, propagates pending state, handles associated IRPs and master completion, preserves mount-point reparse buffers, releases auxiliary buffers, handles paging/close completion, unlocks MDL pages, supports deferred completion, and queues a kernel APC to run `IopCompleteRequest()` in the requestor thread (lines 1303-1607).
- `IopCompleteRequest()` is the final APC routine. It copies buffered input data back to user buffers, frees system buffers and MDLs, writes the user IOSB, signals user/file-object events, updates transfer counters, unqueues the IRP from the thread list, posts user APCs or completion-port packets, and releases file-object references (lines 236-545).
- `IoCancelIrp()` sets `Irp->Cancel`, atomically removes the cancel routine under the cancel spin lock, and calls it with `CancelIrql` if present; invalid completed-state cancellation bugchecks (lines 1096-1139).
- `IoCancelThreadIo()` cancels all IRPs on the current thread's list, waits for completion, and after a retry budget disassociates a broken-driver IRP through `IopDisassociateThreadIrp()` (lines 1141-1210).
- `IopDisassociateThreadIrp()` removes a stuck IRP from the current thread, clears its owner, logs an `IO_DRIVER_CANCEL_TIMEOUT` against the current stack's device if possible, and leaves the IRP detached (lines 113-187).
- `IoForwardIrpSynchronously()` copies the current stack to the next stack, installs a completion routine that signals an event, calls the next device, and waits if the result is pending (lines 1609-1659).
- `IoMakeAssociatedIrp()` allocates a child IRP, marks `IRP_ASSOCIATED_IRP`, copies the owner thread, and points back to the master IRP (lines 1920-1947).
- Requestor helpers include `IoGetRequestorProcess()`, `IoGetRequestorProcessId()`, `IoGetRequestorSessionId()`, `IoGetTopLevelIrp()`, `IoSetTopLevelIrp()`, and paging priority selection (lines 1743-1847, 1995-2004).

## Data, ownership, and synchronization

- The file uses per-processor lookaside lists through `KeGetCurrentPrcb()->PPLookasideList[]` and tracks quota interactions with `LookasideIrpFloat`.
- Thread-associated synchronous IRPs are protected by raising to APC level and by queued spin locks for I/O completion and cancellation paths.
- Completion is split between high-level stack unwinding in `IofCompleteRequest()` and passive-thread finalization in `IopCompleteRequest()` using `KAPC`.
- `IopDeadIrp` is a global diagnostic pointer for the latest disassociated stuck IRP.
- MDLs may be freed in builder error paths, associated-IRP completion, final APC cleanup, or explicit cleanup; locked pages are unlocked in `IofCompleteRequest()` before final APC queuing.

## Filesystem and storage relevance

This file defines the mechanics used by filesystem drivers to forward requests, split paging I/O, complete direct/buffered I/O, process reparse mount points, and wait for synchronous device and filesystem control operations. Any filesystem research in this tree depends on these completion and cancellation semantics.

## Implementation gaps and risks

- Asynchronous non-synchronous paging write completion is explicitly unimplemented and breaks into the debugger under the compiled path (lines 1505-1524).
- `IoIsValidNameGraftingBuffer()` is unimplemented and always returns `FALSE`, so name-grafting validation is absent (lines 1908-1918).
- `IoIs32bitProcess()` is unimplemented on `_WIN64` (lines 2006-2015).
- `IopAllocateIrpMustSucceed()` retries for a very large finite count after 10 ms sleeps, which approximates must-succeed behavior but is not a true guaranteed allocator (lines 711-743).
- `IoCancelThreadIo()` ignores its `Thread` parameter and always operates on the current thread, matching the local comment but surprising for callers expecting the signature semantics (lines 1146-1157).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/irp.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/irq.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/irq.c

## Role

`irq.c` implements I/O-manager wrappers for kernel interrupt objects. It maps the legacy `IoConnectInterrupt()` API and the newer `IoConnectInterruptEx()`/`IoDisconnectInterruptEx()` forms onto kernel interrupt initialization and connection primitives.

## Main entry points and behavior

- `IoConnectInterrupt()` counts CPUs in `ProcessorEnableMask & KeActiveProcessors`, allocates one `IO_INTERRUPT` wrapper plus extra `KINTERRUPT` storage for additional processors, initializes a caller-provided or internal spin lock, initializes one interrupt object per enabled processor, and connects each with `KeConnectInterrupt()` (lines 21-135).
- If connection fails on the first processor, the wrapper allocation is freed; if failure occurs after the first connection, `IoDisconnectInterrupt()` unwinds all connected interrupts (lines 101-118).
- `IoDisconnectInterrupt()` recovers the owning `IO_INTERRUPT` from the first interrupt object, disconnects the first and any stored additional interrupts, and frees the wrapper with `TAG_IO_INTERRUPT` (lines 137-170).
- `IopConnectInterruptExFullySpecific()` adapts `CONNECT_FULLY_SPECIFIED` parameters to `IoConnectInterrupt()` and logs failure (lines 172-195).
- `IoConnectInterruptEx()` supports fully specified and fully specified group connections by using the same fallback. Message-based and line-based forms only log `FIXME` and return success (lines 197-220).
- `IoDisconnectInterruptEx()` currently only disconnects `ConnectionContext.InterruptObject` if present (lines 222-232).

## Data and synchronization

The per-connection wrapper owns an internal spin lock when the caller did not provide one. The additional interrupt object pointers are stored in `IoInterrupt->Interrupt[]`, while the first object is embedded as `FirstInterrupt`.

## Implementation gaps and risks

- `CONNECT_MESSAGE_BASED` and `CONNECT_LINE_BASED` are unimplemented but `IoConnectInterruptEx()` falls through to `STATUS_SUCCESS`, which can mislead callers expecting a connected interrupt (lines 211-219).
- `CONNECT_FULLY_SPECIFIED_GROUP` ignores processor groups and reuses the non-group path (lines 208-210).
- The allocation size uses `(Count - 1) * sizeof(KINTERRUPT) + sizeof(IO_INTERRUPT)` while subsequent code also stores pointers in `IoInterrupt->Interrupt[(UCHAR)Count]`; correctness depends on the exact `IO_INTERRUPT` layout defined elsewhere (lines 59-63, 127-129).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/irq.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/ramdisk.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/ramdisk.c

## Role

`ramdisk.c` contains boot-time RAM disk startup support. It finds a loader-provided XIP ROM memory descriptor, asks the RAM disk driver to create a boot disk, creates ARC and drive-letter symbolic links, initializes `NtSystemRoot`, and waits for PnP enumeration.

## Main entry point and behavior

- `IopStartRamdisk()` scans `LoaderBlock->MemoryDescriptorListHead` for a `LoaderXIPRom` descriptor. Missing data causes `RAMDISK_BOOT_INITIALIZATION_FAILED` with `RD_NO_XIPROM_DESCRIPTOR` (lines 23-78).
- It populates `RAMDISK_CREATE_INPUT` for a fixed `RAMDISK_BOOT_DISK`, using descriptor base page and page count, `RAMDISK_BOOTDISK_GUID`, and a hardcoded drive letter `C` (lines 80-92).
- Loader command-line options are uppercased in place and parsed for `RDIMAGEOFFSET` and `RDIMAGELENGTH`, adjusting disk offset and length (lines 94-146).
- It opens `\Device\Ramdisk`, sends `FSCTL_CREATE_RAM_DISK`, and bugchecks if the driver open or IOCTL fails (lines 148-203).
- It converts the disk GUID to a string, builds a `\Device\Ramdisk{guid}` target, and creates `\ArcName\ramdisk(0)` as a symbolic link to it (lines 205-248).
- A ReactOS-specific block creates an `X:` drive-letter symlink to the RAM disk device and writes `SharedUserData->NtSystemRoot` as `X:` plus the loader boot path (lines 250-275).
- It waits on `PiEnumerationFinished` before returning success (lines 277-287).

## Dependencies and side effects

The function depends on the loader memory descriptor format, the RAM disk device and FSCTL contract from `ntddrdsk.h`, object-manager symbolic links, and the PnP enumeration event exported as `PiEnumerationFinished`.

## Implementation gaps and risks

- Failure paths are hard bugchecks because this is boot-critical code.
- Command-line parsing mutates `LoaderBlock->LoadOptions` with `_strupr()` and uses simple `strstr()`/`atol()` parsing without validating numeric bounds or underflow when subtracting the offset from disk length (lines 96-143).
- The drive-letter handling is explicitly called a ReactOS hack; it hardcodes `X:` and bypasses mount manager policy (lines 250-275).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/ramdisk.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/rawfs.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/rawfs.c

## Role

`rawfs.c` implements the RAW filesystem driver used when no real filesystem recognizes a volume. It creates raw disk/CD/tape filesystem device objects, mounts a volume device object around an underlying device, provides minimal open/close/cleanup, forwards read/write/device-control IRPs, handles basic lock/dismount FSCTLs, and returns minimal volume information.

## Key structures and globals

- `VCB` tracks the target device, public VPB, temporary local VPB, state flags, open count, share access, mutex, bytes per sector, and sector count (lines 17-30).
- `VOLUME_DEVICE_OBJECT` embeds a `DEVICE_OBJECT` plus the RAW VCB (lines 32-36).
- State flags are `VCB_STATE_LOCKED` and `VCB_STATE_DISMOUNTED` (lines 38-39).
- Global filesystem device objects are `RawDiskDeviceObject`, `RawCdromDeviceObject`, and `RawTapeDeviceObject` (line 43).

## Mount and VPB lifecycle

- `RawInitializeVcb()` zeroes the VCB, stores the target device and VPB, initializes the mutex, and allocates a local VPB used during later dismount transitions (lines 47-76).
- `RawCheckForDismount()` must run with the VCB mutex held. It locks the VPB spin lock, decides whether references allow deletion, may install a local VPB on the real device while marking the current VPB persistent, or clears the mounted state and deletes the RAW volume device when the last reference is gone (lines 78-158).
- `RawMountVolume()` creates a `FILE_DEVICE_DISK_FILE_SYSTEM` volume device, initializes its VCB using the mount VPB, sets dummy serial/label fields, sets stack size/sector size/direct I/O, creates a stream file object for notification, emits `FSRTL_VOLUME_MOUNT`, and drops temporary open-count inflation used to avoid immediate dismount during notification (lines 379-461).

## IRP handling

- `RawDispatch()` distinguishes the filesystem control device object from RAW volume device objects. On the filesystem device object it only succeeds create/cleanup/close stubs unless processing a mount request. On volume device objects it enters filesystem context and dispatches to per-major handlers (lines 1045-1153).
- `RawCreate()` permits only an unnamed non-directory `FILE_OPEN`, rejects locked or dismounted volumes, enforces share access, increments open count, attaches the file object to the VPB, marks `FO_NO_INTERMEDIATE_BUFFERING`, and attempts dismount if the open fails and no opens remain (lines 227-336).
- `RawClose()` ignores stream file objects, otherwise decrements open count under the VCB mutex and may dismount on the final close (lines 187-225).
- `RawCleanup()` removes share access and, if the VCB is dismounted, calls dismount handling while asserting one open remains (lines 1010-1043).
- `RawReadWriteDeviceControl()` immediately succeeds zero-length read/write requests, otherwise copies the stack to the next device, sets `SL_OVERRIDE_VERIFY_VOLUME`, installs `RawCompletionRoutine()`, and forwards to the target device (lines 338-377).
- `RawCompletionRoutine()` updates synchronous file-object byte offsets for successful reads and writes and propagates pending state (lines 160-185).

## FSCTL and information support

- `RawUserFsCtrl()` implements oplock requests as `STATUS_NOT_IMPLEMENTED`, `FSCTL_LOCK_VOLUME`, `FSCTL_UNLOCK_VOLUME`, and `FSCTL_DISMOUNT_VOLUME`, and emits corresponding `FsRtlNotifyVolumeEvent()` notifications (lines 463-573).
- `RawFileSystemControl()` handles user FSCTLs, mount volume, and verify volume. Verify returns `STATUS_WRONG_VOLUME`, clears `DO_VERIFY_VOLUME`, and may dismount (lines 575-639).
- `RawQueryInformation()` and `RawSetInformation()` only support `FilePositionInformation`, including alignment validation on set (lines 641-733).
- `RawQueryFsVolumeInfo()` returns an empty label and the VPB serial number (lines 735-754).
- `RawQueryFsSizeInfo()` queries drive geometry and, for non-floppy devices, partition information to fill `FILE_FS_SIZE_INFORMATION` (lines 756-893).
- `RawQueryFsDeviceInfo()` reports `FILE_DEVICE_DISK` and target characteristics (lines 895-920).
- `RawQueryFsAttributeInfo()` reports filesystem name `RAW` and no attributes (lines 922-948).
- `RawQueryVolumeInformation()` dispatches the supported filesystem information classes and completes the IRP with consumed length (lines 950-1008).

## Driver initialization and teardown

- `RawFsDriverEntry()` creates `\Device\RawDisk`, `\Device\RawCdRom`, and `\Device\RawTape`, marks them direct-I/O, installs the dispatch table, registers shutdown/unload, and registers all three file systems (lines 1190-1279).
- `RawShutdown()` contains disabled unregister/delete logic due to a shutdown freeze comment and currently only completes success (lines 1155-1176).
- `RawUnload()` is effectively disabled because the unload path is not expected to run (lines 1178-1188).

## Implementation gaps and risks

- RAW is intentionally minimal: no directory/file namespace, no allocation accounting beyond whole-device size, no real volume label, and limited information classes.
- `RawQueryFsDeviceInfo()` always reports `FILE_DEVICE_DISK` even when the RAW filesystem instance is for CD-ROM or tape (lines 912-916).
- `RawUserFsCtrl()` returns success for dismount when locked but does not set `VCB_STATE_DISMOUNTED` in that branch, so actual dismount semantics are incomplete (lines 528-542).
- Shutdown unregister/delete is disabled under `#if 0`, leaving lifetime mostly static (lines 1155-1170).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/rawfs.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/remlock.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/remlock.c

## Role

`remlock.c` implements WDM remove-lock helpers. Remove locks prevent device removal while I/O is active and optionally track debug acquisition tags, source locations, high-water marks, and lock hold duration.

## Main entry points and behavior

- `IoInitializeRemoveLockEx()` initializes either a debug remove lock or common remove lock, setting signature, high watermark, maximum locked ticks, allocation tag, spin lock, tracking list, removed flag, initial `IoCount` of 1, and the remove event (lines 31-73).
- `IoAcquireRemoveLockEx()` increments `IoCount`; if the device is not removed and debug tracking is enabled, it allocates a tracking block tagged with the caller's tag/file/line and acquisition tick count, linking it under the debug spin lock. If already removed, it undoes the increment, signals the event if count becomes zero, and returns `STATUS_DELETE_PENDING` (lines 78-142).
- `IoReleaseRemoveLockEx()` removes one matching debug tracking block for the tag, checks all tracked blocks for excessive hold time, accounts for low-memory tracking failures, decrements `IoCount`, and signals `RemoveEvent` when the count reaches zero after removal (lines 147-236).
- `IoReleaseRemoveLockAndWaitEx()` marks the lock removed, decrements the count, waits for outstanding holders, and releases the final debug tracking block (lines 241-288).

## Data and synchronization

Debug tracking blocks are singly linked through `Lock->Dbg.Blocks` and protected by `Lock->Dbg.Spin`. The common lock count is maintained with interlocked operations. `RemoveEvent` is a synchronization event signaled when the outstanding count reaches zero.

## Implementation gaps and risks

- `IoInitializeRemoveLockEx()` intentionally falls through from the debug-size case into common initialization; this matches the structure layout pattern but lacks an explicit `break`, so future edits must preserve this dependency (lines 52-72).
- `IoReleaseRemoveLockAndWaitEx()` decrements `IoCount` twice: once into `LockValue`, then again in the wait condition (lines 254-260). This is a high-risk semantic detail because the usual remove-lock algorithm releases the caller's acquisition and waits for remaining counts without accidentally dropping an extra reference.
- The debug tag mismatch assertion in `IoReleaseRemoveLockAndWaitEx()` asserts `TrackingBlock->Tag != Tag` after detecting inequality, which appears inverted for a failure assertion and would not catch the mismatch in the usual way (lines 277-283).
- When debug tracking allocation fails, release attempts consume `LowMemoryCount` instead of requiring a matching tag; this is intentional fallback behavior but can hide tag-pairing mistakes during memory pressure (lines 103-109, 208-221).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/remlock.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/symlink.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/symlink.c

## Role

`symlink.c` provides I/O-manager wrappers for creating and deleting object-manager symbolic links, including a protected default form and an unprotected NULL-DACL form.

## Main entry points and behavior

- `IoCreateSymbolicLink()` initializes permanent, kernel-handle, case-insensitive object attributes using `SePublicDefaultSd`, calls `ZwCreateSymbolicLinkObject()`, closes the handle on success, and returns the status (lines 21-45).
- `IoCreateUnprotectedSymbolicLink()` builds a security descriptor with a present NULL DACL, creates the permanent symbolic link with that descriptor, closes on success, and returns the status (lines 50-87).
- `IoDeleteSymbolicLink()` opens the symbolic-link object for `DELETE`, calls `ZwMakeTemporaryObject()` to remove permanence, closes the handle only when that succeeds, and returns the status (lines 92-116).

## Filesystem and device relevance

These wrappers are used by boot and storage code to expose kernel device objects through namespace aliases such as ARC names, DOS device names, and RAM disk links.

## Implementation gaps and risks

- `IoCreateUnprotectedSymbolicLink()` deliberately creates a NULL-DACL object, so callers must ensure the target namespace is intended to be broadly accessible.
- `IoDeleteSymbolicLink()` closes the opened handle only when `ZwMakeTemporaryObject()` succeeds. If `ZwMakeTemporaryObject()` fails after a successful open, the handle is not closed in this implementation (lines 107-112).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/symlink.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/util.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/util.c

## Role

`util.c` contains miscellaneous I/O-manager helper APIs for cancel-lock acquisition, stack limit discovery, process/thread queries, WDM version checks, access validation, EA buffer validation, and verify-device bookkeeping.

## Main entry points and behavior

- `IoComputeDesiredAccessFileObject()` verifies the object type is `IoFileObjectType` and computes write/append desired access, omitting `FILE_APPEND_DATA` for named pipes to avoid conflict with pipe-instance creation (lines 24-47).
- `IoAcquireCancelSpinLock()` and `IoReleaseCancelSpinLock()` wrap queued spin lock operations on `LockQueueIoCancelLock` (lines 51-60, 145-154).
- `IoGetInitialStack()` returns the current thread TCB initial stack (lines 62-71).
- `IoGetStackLimits()` reads normal stack limits through `RtlpGetStackLimits()` and substitutes DPC stack limits if the current stack address is outside the normal range while running an active DPC at dispatch level or higher (lines 73-108).
- `IoIsSystemThread()`, `IoGetCurrentProcess()`, and `IoThreadToProcess()` are thin wrappers around thread/process fields or process-manager helpers (lines 110-119, 134-143, 156-165).
- `IoIsWdmVersionAvailable()` reports support up to WDM 1.30 (Windows Server 2003) using simple major/minor comparison (lines 121-132).
- `IoCheckDesiredAccess()` maps generic file-object access and checks requested access against granted access (lines 167-184).
- `IoCheckEaBufferValidity()` walks a `FILE_FULL_EA_INFORMATION` chain, validating base size, name/value bounds, null-terminated names, aligned next offsets, positive offsets, and remaining length. On failure it returns `STATUS_EA_LIST_INCONSISTENT` and reports the failing offset (lines 186-269).
- `IoSetDeviceToVerify()`, `IoSetHardErrorOrVerifyDevice()`, and `IoGetDeviceToVerify()` store or retrieve the thread's device-to-verify pointer; the IRP form ignores IRPs with no associated thread (lines 299-340).

## Implementation gaps and risks

- `IoCheckFunctionAccess()`, `IoValidateDeviceIoControlAccess()`, and `IoCheckQuerySetVolumeInformation()` are unimplemented and return `STATUS_NOT_IMPLEMENTED` (lines 271-297, 342-353).
- `IoCheckDesiredAccess()` uses `(~(*DesiredAccess) & GrantedAccess)` to decide denial (lines 181-183). That expression is unusual for testing whether all desired bits are granted; readers should verify it against the intended Windows semantics before relying on it.
- `IoIsWdmVersionAvailable()` does not compare major/minor as a lexicographic version; it returns true only when `MajorVersion <= 1 && MinorVersion <= 0x30`, which is fine for the current advertised support but not a general version predicate (lines 124-131).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/util.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/volume.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/volume.c

## Role

`volume.c` implements volume and filesystem I/O support: VPB creation/reference/freeing, filesystem registration queues, mount probing, verify-volume handling, shutdown dispatch to filesystem drivers, filesystem notification registration, system-partition registry storage, VPB spin-lock wrappers, and conversion from a volume device object to a DOS path via MountMgr.

## Globals and queues

- `IopDatabaseResource` guards filesystem registration and notification queues.
- Queue heads track disk, network, CD-ROM, tape filesystems, and filesystem-change notification entries (lines 18-24).
- `IopFsRegistrationOps` increments on filesystem register/unregister and lets the mount loop detect list mutation while locks were dropped (lines 24, 614-664).

## VPB and device reference helpers

- `IopDecrementDeviceObjectRef()` decrements a device object's reference count under `LockQueueIoDatabaseLock` and calls `IopUnloadDevice()` when the count reaches zero and unload/delete/remove conditions apply (lines 28-58).
- `IopDecrementDeviceObjectHandleCount()` is a wrapper that does not force unload (lines 60-69).
- `IopCreateVpb()` allocates and initializes a nonpaged VPB, linking it to the real device (lines 153-179).
- `IopDereferenceVpbAndFree()` decrements a VPB reference and frees it if unreferenced, still attached to the real device, and not persistent (lines 181-209).
- `IopReferenceVerifyVpb()` references a mounted VPB and returns its filesystem device object for verify operations (lines 214-245).
- `IopMountInitializeVpb()` marks a VPB mounted, optionally raw, adjusts the mounted filesystem device stack size, stores the VPB in the device extension, and references it (lines 247-278).
- `IoAcquireVpbSpinLock()` and `IoReleaseVpbSpinLock()` wrap `LockQueueIoVpbLock` (lines 1199-1219).

## Mount and verify flow

- `IopCheckVpbMounted()` loops until a device VPB is mounted. It computes whether raw mount is allowed from an empty remaining name with no related file object, calls `IopMountVolume()`, handles alert/user APC interruption as `STATUS_WRONG_VOLUME`, and references an already mounted VPB unless locked (lines 71-151).
- `IopMountVolume()` serializes on the device lock unless already locked, acquires `IopDatabaseResource`, skips mounted/remove-pending devices, chooses the filesystem queue from the real device type, and iterates registered filesystems until one accepts `IRP_MN_MOUNT_VOLUME` (lines 460-778).
- During mount probing, it finds the top attached target device, allocates an IRP with storage-stack plus filesystem-stack overhead, sets `IRP_MJ_FILE_SYSTEM_CONTROL/IRP_MN_MOUNT_VOLUME`, passes the VPB and target device, drops the database lock while calling the filesystem, and reacquires it after completion (lines 503-636).
- Mount success calls `IopMountInitializeVpb()`. Failures handle user-induced errors, concurrent registration changes, `STATUS_FS_DRIVER_REQUIRED` by calling `IopLoadFileSystemDriver()` and restarting, raw-mount restrictions, and total device failures (lines 637-743).
- On boot partition mount failure before initialization phase 2, `IopMountVolume()` bugchecks with `INACCESSIBLE_BOOT_DEVICE` (lines 763-774).
- `IoVerifyVolume()` locks the device, sends `IRP_MN_VERIFY_VOLUME` to the current filesystem stack when mounted, dereferences the VPB, and if it gets `STATUS_WRONG_VOLUME` creates a new VPB and tries to mount again with raw-mount allowance from the caller (lines 872-980).

## Filesystem registration and notification

- `IoRegisterFileSystem()` selects the queue by filesystem device type, inserts high-priority filesystems at the head and low-priority ones near the tail, increments registration operations, clears `DO_DEVICE_INITIALIZING`, notifies registered listeners, releases the resource, and increments the device reference count to prevent unload (lines 982-1049).
- `IoUnregisterFileSystem()` removes a queued filesystem, notifies listeners inactive, increments registration operations, and decrements the unload-prevention reference (lines 1051-1082).
- `IopNotifyFileSystemChange()` walks `IopFsNotifyChangeQueueHead` and calls each registered notification procedure (lines 280-306).
- `IoRegisterFsRegistrationChange()` rejects an immediately repeated registration from the same driver/routine pair, allocates a notification entry, inserts it, notifies the caller about already registered network/CD/disk/tape filesystems, references the driver object, and returns success (lines 1084-1150).
- `IoUnregisterFsRegistrationChange()` removes the matching notification entry and dereferences the driver object (lines 1152-1197).
- `IoEnumerateRegisteredFiltersList()` returns the registered notification driver objects, referencing each object copied into the caller buffer and reporting `STATUS_BUFFER_TOO_SMALL` if the supplied array is insufficient (lines 819-870).

## Shutdown and filesystem loading

- `IopShutdownBaseFileSystems()` walks a filesystem queue, references each top attached device, builds an `IRP_MJ_SHUTDOWN`, calls the driver, waits if pending, clears the event, and releases references (lines 344-402).
- `IopLoadFileSystemDriver()` sends an `IRP_MN_LOAD_FILE_SYSTEM` filesystem-control IRP to the top attached device for an FsRec-like recognizer. A reference decrement call is commented out because it broke second-stage boot (lines 407-455).

## Other public APIs

- `IoSetSystemPartition()` stores a `REG_SZ` `SystemPartition` value under `HKLM\SYSTEM\Setup` using the provided volume-name string (lines 1221-1272).
- `IoVolumeDeviceToDosName()` queries the volume device for its mountdev name, opens MountMgr, queries `IOCTL_MOUNTMGR_QUERY_DOS_VOLUME_PATH` first for size and then for data, allocates a caller-owned buffer, moves the first multi-string DOS path into the returned `UNICODE_STRING`, and dereferences the MountMgr file object (lines 1274-1430).

## Implementation gaps and risks

- `IopDecrementDeviceObjectRef()` is marked half-implemented (lines 28-30).
- `IopLoadFileSystemDriver()` builds a device-control IRP using `IRP_MJ_DEVICE_CONTROL` as the IOCTL code and then overwrites the stack to filesystem-control/load-filesystem. This works with the local builder but is non-obvious and should be treated as a compatibility shim (lines 426-444).
- `IoRegisterFileSystem()` uses `InsertTailList(FsList->Blink, ...)` for low-priority insertion (lines 1021-1031). This is unusual because `InsertTailList()` normally takes the list head; verify list ordering assumptions before changing it.
- Several code paths drop and reacquire `IopDatabaseResource` while preserving a local restart list. Mount behavior is sensitive to registration races and reference-count correctness (lines 614-722).
- `IoRegisterFsRegistrationChange()` duplicate detection only checks the current tail entry rather than the full notification list (lines 1099-1116).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/iomgr/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpio.h -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpio.h

## Role

`pnpio.h` is a small internal PnP I/O helper header. It declares debug/dump helpers for CM resource lists, IO resource requirement lists, individual descriptors, and device-node trees.

## Contents

- Dump flags define which device-node/resource views to print: all nodes, allocated resources, requirements, and translated resources (lines 4-8).
- Declared helpers include `PipDumpCmResourceList()`, `PipGetNextCmPartialDescriptor()`, `PipDumpCmResourceDescriptor()`, `PipDumpResourceRequirementsList()`, `PipDumpIoResourceDescriptor()`, and `PipDumpDeviceNodes()` (lines 10-52).

## Dependencies and use

The declarations use kernel PnP and resource types such as `PCM_RESOURCE_LIST`, `PCM_PARTIAL_RESOURCE_DESCRIPTOR`, `PIO_RESOURCE_REQUIREMENTS_LIST`, `PIO_RESOURCE_DESCRIPTOR`, and `PDEVICE_NODE`. Implementations are expected in PnP debug support code, not this header.

## Implementation gaps and risks

This file is declarations only. The only notable constraint is that callers depend on consistent flag meanings across the implementations.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpio.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbbus.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbbus.c

## Role

`arbbus.c` defines the root bus-number arbiter instance wiring for the PnP manager. It is a skeleton for unpacking, packing, unpacking assigned resources, and scoring bus-number requirements.

## Main entry points and behavior

- `IopArbBusNumberUnpackRequirements()`, `IopArbBusNumberPackResource()`, `IopArbBusNumberUnpackResource()`, and `IopArbBusNumberScoreRequirement()` log their parameters, call `UNIMPLEMENTED`, and return `STATUS_NOT_IMPLEMENTED` or score `0` (lines 20-86).
- `IopArbBusNumberInitialize()` fills `IopRootBusNumberArbiter` with name `RootBusNumber` and the callback pointers above, then calls `ArbInitializeArbiterInstance()` for `CmResourceTypeBusNumber` on root path `Root` (lines 88-123).

## Dependencies

The file depends on the global `IopRootBusNumberArbiter` defined elsewhere and the arbiter library function `ArbInitializeArbiterInstance()`.

## Implementation gaps and risks

All resource translation/scoring callbacks are stubs, so the arbiter can be initialized but cannot correctly arbitrate bus-number requirements until those callbacks are implemented.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbbus.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbdma.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbdma.c

## Role

`arbdma.c` defines root DMA arbiter callback wiring for the PnP manager. Its intended job is DMA-channel resource requirement unpacking, resource packing/unpacking, and requirement scoring.

## Main entry points and behavior

- `IopArbDmaUnpackRequirements()`, `IopArbDmaPackResource()`, `IopArbDmaUnpackResource()`, and `IopArbDmaScoreRequirement()` are stubs that log inputs, call `UNIMPLEMENTED`, and return `STATUS_NOT_IMPLEMENTED` or score `0` (lines 20-86).
- `IopArbDmaInitialize()` names the arbiter `RootDma`, installs the DMA callbacks, and calls `ArbInitializeArbiterInstance()` (lines 88-113).

## Implementation gaps and risks

- The callback logic is unimplemented, so DMA resource arbitration cannot make meaningful decisions.
- The initializer passes `CmResourceTypeBusNumber` to `ArbInitializeArbiterInstance()` instead of a DMA resource type (lines 101-106). This looks copied from the bus-number initializer and is likely incorrect for a DMA arbiter.
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbdma.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbirq.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbirq.c

## Role

`arbirq.c` defines root IRQ arbiter callback wiring for the PnP manager. It is intended to arbitrate interrupt-line resources.

## Main entry points and behavior

- `IopArbIrqUnpackRequirements()`, `IopArbIrqPackResource()`, `IopArbIrqUnpackResource()`, and `IopArbIrqScoreRequirement()` are unimplemented stubs with debug logging (lines 20-86).
- `IopArbIrqInitialize()` names the arbiter `RootIRQ`, installs the IRQ callbacks, and initializes the arbiter instance (lines 88-113).

## Implementation gaps and risks

- The actual IRQ translation and scoring logic is absent.
- The initializer passes `CmResourceTypeBusNumber` rather than an interrupt resource type, and the failure log message says `IopArbDmaInitialize`, both indicating copy-paste defects (lines 101-109).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbirq.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbmem.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbmem.c

## Role

`arbmem.c` defines root memory-resource arbiter callback wiring for the PnP manager. Its intended scope is memory-window requirement unpacking, resource descriptor packing/unpacking, and scoring.

## Main entry points and behavior

- `IopArbMemUnpackRequirements()`, `IopArbMemPackResource()`, `IopArbMemUnpackResource()`, and `IopArbMemScoreRequirement()` are debug-logged stubs returning `STATUS_NOT_IMPLEMENTED` or `0` (lines 20-86).
- `IopArbMemInitialize()` names the arbiter `RootMemory`, installs the memory callbacks, and initializes the arbiter instance (lines 88-113).

## Implementation gaps and risks

- Memory arbitration is not implemented beyond instance registration.
- The initializer passes `CmResourceTypeBusNumber` instead of a memory resource type, and the failure log names the DMA initializer, suggesting copy-paste errors (lines 101-109).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbmem.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbport.c -->
# File Research: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbport.c

## Role

`arbport.c` defines root I/O port arbiter callback wiring for the PnP manager. It is intended to handle port-range resource requirement unpacking, assignment packing/unpacking, and scoring.

## Main entry points and behavior

- `IopPortMemUnpackRequirements()`, `IopPortMemPackResource()`, `IopPortMemUnpackResource()`, and `IopPortMemScoreRequirement()` are unimplemented stubs with debug logging (lines 20-86).
- `IopArbPortInitialize()` names the arbiter `RootPort`, installs those callbacks, and calls `ArbInitializeArbiterInstance()` (lines 88-113).

## Implementation gaps and risks

- I/O port arbitration behavior is absent.
- Callback names include `PortMem`, which may be a naming error for port resources.
- The initializer passes `CmResourceTypeBusNumber` instead of a port resource type, and the failure log names the DMA initializer, both likely copy-paste defects (lines 95-109).
<!-- END FILE RESEARCH: sources/windows/reactos/ntoskrnl/io/pnpmgr/arb/arbport.c -->