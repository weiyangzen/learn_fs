# Group Research: group_1694_reactos_sources_windows_reactos_drivers_filesystems_nfs_nfs41_drive_45347d82c10f

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.c -->
# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.c

This file implements the ReactOS/Windows NFSv4.1 client mini-redirector driver entry points on top of RDBSS. It is not a standalone NFS protocol implementation; the kernel driver translates Windows file-system operations into serialized upcalls to a user-mode daemon, then consumes matching downcall replies. The file covers the entire mini-redirector lifecycle: driver registration, device IOCTL control, RDBSS server/netroot/vnetroot creation, open/close, directory/file/volume/EA/security queries and sets, low I/O read/write/locks, reparse-point symlink handling, cache coherency, and unload.

The top of the file defines driver-wide state, pool tags, debug/timing switches, device globals, synchronization primitives, and wire-format helpers. Important persistent globals include `nfs41_ops` for the `MINIRDR_DISPATCH` table, `nfs41_dev` for the RDBSS device object, `upcall` and `downcall` lists protected by fast mutexes, an `upcallEvent`, an interlocked transaction id `xid`, and an `openlist` used by a background coherency thread. The code defines RDBSS-managed extension records for net roots, virtual net roots, FCBs, FOBXs, and the device extension. These extensions hold NFS session handles, mount attributes/options, cached basic/standard file information, change attributes, open state handles, ACL cache state, delegation/caching flags, and shared-memory handles.

The central cross-boundary object is `nfs41_updowncall_entry`. Each entry stores version, xid, opcode, status, Windows error value, state, event, client security context, session/open handles, filename, buffer metadata, change time, and a union of opcode-specific payloads. The opcode union handles mount, read/write, lock/unlock, open/close, directory query, file query/set, EA get/set, symlink, volume, and ACL operations. `nfs41_UpcallCreate` allocates and initializes an entry, captures or reuses a client security context, assigns an xid, and normalizes filenames to slash or empty constants when needed. `nfs41_UpcallWaitForReply` queues the entry, wakes the daemon-side reader, then waits with timeout and special non-interruptible handling for close/unlock. Interrupted or timed-out waits mark entries as no longer waited on so late downcalls can clean resources.

Marshalling functions serialize each operation into the output buffer supplied by daemon IOCTL reads. Strings are converted from UTF-16 to UTF-8 with a stored maximum length. Read/write, directory-query, and create-EA paths map MDLs into user-mode-visible buffers using `MmMapLockedPagesSpecifyCache` inside SEH guards. The daemon returns replies through IOCTL writes; `nfs41_downcall` unmarshals the common header, finds the matching xid in the downcall list, updates state/status, unmarshals opcode-specific data, unmaps any mapped pages, signals synchronous waiters, or completes asynchronous read/write operations through `RxLowIoCompletion`. Late downcalls for abandoned entries explicitly unmap/free operation buffers before dropping the entry.

Device control is implemented by `nfs41_DevFcbXXXControlFile`. It handles `IOCTL_NFS41_READ` as daemon upcall retrieval, `IOCTL_NFS41_WRITE` as daemon reply delivery, `IOCTL_NFS41_START`/`STOP` to start and stop the mini-redirector, `IOCTL_NFS41_GETSTATE`, `IOCTL_NFS41_ADDCONN`/`DELCONN` for tree connection management, and `IOCTL_NFS41_INVALCACHE` to force buffering-state changes for a server open. Start creates a named shared-memory section with a permissive DACL; stop closes it. Connection add/delete parses RDBSS connection buffers, opens tree connections, checks active FCB counts, and finalizes connections through RDBSS.

Mount and name-resolution logic is concentrated around RDBSS server-call and vnetroot callbacks. `_nfs41_CreateSrvCall` validates/copies the server name into an `NFS41_SERVER_ENTRY` and reports completion through the RDBSS callback; `nfs41_CreateSrvCall` dispatches that work to the RDBSS process context when necessary and returns the RDBSS-expected pending status. `nfs41_CreateVNetRoot` only claims paths of the form `\\server\nfs4\...`, parses mount EAs (`ro`, `writethru`, `nocache`, `timeout`, `rsize`, `wsize`, `srvname`, `mntpt`, `sec`), maps security flavors (`sys`, `krb5`, `krb5i`, `krb5p`), tracks sessions per logon LUID and security flavor, sends the daemon mount upcall, stores returned filesystem attributes/version/session, and captures a mount security context. Finalizers unmount every session in the mount list, clear pending upcall/downcall entries with failure statuses, free server entries, and delete saved security contexts.

Create/open handling is substantial. `check_nfs41_create_args` validates netroot type, paging-file exclusion, established mount state, alternate data stream rejection, read-only access rules, delete-pending/share semantics, filename component length, Windows create option constraints, and EA support. `nfs41_Create` builds an `NFS41_OPEN` upcall with desired access, share access, file attributes, create options/disposition, open owner id, cygwin/NFSv3 EA mode information, optional symlink target EA, and optional EA MDL. On success it handles daemon-reported symlink reparses by constructing an absolute RDBSS path and invoking `RxPrepareToReparseSymbolicLink`; otherwise it creates a FOBX, stores open state/security/delegation data, initializes or refreshes the FCB, sets delete-pending state, selects buffering flags based on delegation/write-through/no-cache/data access, may add non-delegated opens to the coherency `openlist`, sets returned create information, and updates the IRP status.

Close and cleanup-adjacent paths send `NFS41_CLOSE` with the server-open pointer, delete/remove flags, and rename state. The driver maps close errors, drops non-delegated FCB coherency entries when the last open closes, and frees cached FOBX ACL memory during FOBX deallocation. `nfs41_ExtendForCache` adjusts allocation and EOF pessimistically by adding 8192 bytes to requested file size, reflecting RDBSS cache-extension needs.

Directory, volume, file-information, EA, and security operations follow the same pattern: validate Windows-side arguments, build an upcall, wait for a reply, map daemon/Win32 errors to NTSTATUS, update RDBSS accounting, and refresh local metadata/change attributes. Directory query supports common directory information classes and uses an MDL for the output buffer. Volume query returns cached synthetic volume information for `FileFsVolumeInformation`, local device info for `FileFsDeviceInformation`, cached root attributes for root `FileFsAttributeInformation`, and daemon-backed size/full-size/attribute queries otherwise. File query handles EA size locally and daemon-backed basic, standard, internal, attribute-tag, and network-open info; standard info is merged with locally extended allocation/EOF and delete-pending state.

EA support includes normal daemon-backed EAs plus cygwin compatibility. The driver recognizes `NfsV3Attributes`, `NfsSymlinkTargetName`, and `NfsActOnLink`. It can synthesize NFSv3-style attributes from cached FCB metadata, use EAs to set POSIX mode, reject symlink/action EAs outside create, and query symlink targets through the symlink upcall. EA set/get paths enforce EA access masks and read-only mount behavior and update change attributes and coherency tracking after successful changes.

Security descriptor support rejects SACL/label requests, sends DACL/owner/group-style query/set operations to the daemon, and keeps a short-lived cached ACL buffer on a buffer-overflow query so a subsequent appropriately sized query can be satisfied without another upcall. Set-security validates DACL presence when DACL security information is requested, sends the security descriptor bytes to the daemon, and updates change attributes/coherency state on success.

Read/write low I/O uses MDL-backed upcalls with optional asynchronous completion. The timeout is adjusted using a simple transfer-time estimate on top of the mount timeout. Successful reads set returned byte counts and may re-enable read caching for data-access non-paging I/O. Successful writes update cached EOF/change attributes, return byte counts, may re-enable write caching when write-through/no-cache is not in effect, and update coherency tracking for non-delegated opens. Error mapping distinguishes EOF, lock conflicts, access denial, invalid parameters, network-name deletion, and generic network write faults.

Locking supports shared/exclusive lock upcalls and unlock/unlock-multiple upcalls. Zero-length locks are rejected before the daemon because NFS lock length zero is invalid. Blocking locks retry on daemon `ERROR_LOCK_FAILED` using exponential backoff between polls, then map lock errors to NTSTATUS. Unlock multiple serializes the linked `LOWIO_LOCK_LIST` count and byte ranges.

Reparse-point handling implements `FSCTL_SET_REPARSE_POINT` and `FSCTL_GET_REPARSE_POINT` for symbolic links. Set validates access, read-only state, root-directory exclusion, buffer sizes, reparse tag validity, and symlink tag matching, then sends the print-name target to the daemon. Get validates output buffer and reparse attribute state, asks the daemon for the target, then fills a `REPARSE_DATA_BUFFER` using the same target as substitute and print name with `SYMLINK_FLAG_RELATIVE`.

Cache coherency is split between direct buffering-state changes and a background polling thread. `nfs41_ComputeNewBufferingState` applies disable/read/write/read-write caching flags to server-open buffering flags. `enable_caching` re-enables buffering after successful non-paging I/O and maintains the `openlist`. `fcbopen_main` wakes every 30 seconds, queries basic information for tracked non-delegated opens, compares returned change time, and invalidates buffering for all data-access server opens on an FCB when change time differs.

`nfs41_init_ops` fills the RDBSS mini-redirector dispatch table. It declares that RDBSS manages netroot, vnetroot, FCB, and FOBX extensions; wires start/stop/device control; name-resolution callbacks; create/close/cache/deallocate callbacks; directory/volume/EA/security/file query and set callbacks; low I/O read/write/lock/unlock/fsctl callbacks; buffering-state callbacks; and leaves truncate, zero-extend, file aliasing, quota, and set-volume operations unimplemented.

`DriverEntry` calls `RxDriverEntry`, initializes the dispatch table, registers the mini-redirector with `RxRegisterMinirdr`, creates the user-visible symbolic link, initializes queues/locks/events, starts the open-list coherency system thread, assigns `nfs41_FsdDispatch` to every IRP major function, and computes the Windows-to-Unix time delta. `nfs41_FsdDispatch` validates the target device and delegates to `RxFsdDispatch`. `nfs41_driver_unload` creates an RDBSS context, stops the mini-redirector, deletes device and pipe symbolic links, and calls `RxUnload`.

Notable risks and implementation details:
- The driver trusts a user-mode daemon for most filesystem semantics and maps daemon-returned Win32-style errors to NTSTATUS locally.
- Shared memory is created with a null DACL, explicitly granting broad access.
- There are many SEH-wrapped MDL map/unmap paths; abandoned or late downcalls have custom cleanup cases.
- Mount-session reuse is per LUID and security flavor, but some flavor branches appear easy to audit carefully because similar `gss`/`gssi` names are used.
- Several operations are intentionally unsupported: paging files, alternate streams, quotas, set-volume info, truncate/zero-extend, file alias detection, non-symlink reparse tags, SACL/label security, and some information classes.
- The file contains ReactOS compatibility conditionals around calling conventions, worker wrappers, MDL cache type, prefix-table diagnostics, IO status behavior, and RDBSS APIs.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.h -->
# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.h

This header defines public names, IOCTLs, daemon opcodes, security flavors, and driver lifecycle states for the NFSv4.1 Windows/ReactOS mini-redirector.

It declares kernel and user-visible device names for the main driver (`\Device\nfs41_driver`, `\\.\nfs41_driver`), a pipe device (`\Device\nfs41_pipe`), provider display names (`NFS41 Network`), and shared-memory object names (`\BaseNamedObjects\nfs41_shared_memory`, `Global\nfs41_shared_memory`).

The `_RDR_CTL_CODE` macro creates network-redirector IOCTL codes. Defined IOCTLs are:
- `IOCTL_NFS41_START`
- `IOCTL_NFS41_STOP`
- `IOCTL_NFS41_GETSTATE`
- `IOCTL_NFS41_ADDCONN`
- `IOCTL_NFS41_DELCONN`
- `IOCTL_NFS41_READ`
- `IOCTL_NFS41_WRITE`
- `IOCTL_NFS41_INVALCACHE`

The `nfs41_opcodes` enum is the kernel/daemon request vocabulary used by `nfs41_driver.c`: mount, unmount, open, close, read, write, lock, unlock, directory query, file query/set, EA get/set, symlink, volume query, ACL query/set, shutdown, and an invalid sentinel.

`rpcsec_flavors` names supported authentication/security modes: AUTH_SYS and Kerberos `krb5`, `krb5i`, `krb5p`.

Two lifecycle enums track initialization and runtime start state. `nfs41_init_driver_state` distinguishes startable, start-in-progress, and started initialization. `nfs41_start_driver_state` distinguishes startable, start-in-progress, started, and stopped runtime states. These states are used by the device-control path to report/start/stop the mini-redirector.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/CMakeLists.txt -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/CMakeLists.txt

This CMake file defines the ReactOS NPFS named-pipe filesystem kernel-mode driver module.

It appends all NPFS source files and the `npfs.h` header to the `SOURCE` list: cleanup, close, create, data support, file info, file object support, flush, fsctl, main, prefix support, read/read support, security support, security info, state support, structure support, volume info, wait support, write/write support, and the main header.

The build creates `npfs` as a module library with `npfs.rc`, marks it as a `kernelmodedriver`, links it with `${PSEH_LIB}`, imports `ntoskrnl` and `hal`, and configures `npfs.h` as the precompiled header for the source set.

Installation/packaging directives add the built driver to `reactos/system32/drivers` for all builds and register `npfs_reg.inf`. This file is purely build metadata; it contains no runtime NPFS logic.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/cleanup.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/cleanup.c

This file implements cleanup IRP handling for the ReactOS Named Pipe FileSystem.

`NpCommonCleanup` obtains the current IRP stack location, initializes a deferred IRP list, acquires the NPFS VCB exclusively, and decodes the file object with `NpDecodeFileObject`. If the decoded object is a CCB, cleanup performs endpoint-specific state updates:
- For the server end, it asserts `ServerOpenCount` is nonzero and decrements it.
- It calls `NpSetClosingPipeState` with the CCB, IRP, named-pipe end, and deferred list so pipe state transitions and blocked waiters can be handled consistently.

After releasing the VCB, it completes deferred IRPs through `NpCompleteDeferredIrps` and returns `STATUS_SUCCESS`.

`NpFsdCleanup` is the FSD entry wrapper. It enters filesystem context with `FsRtlEnterFileSystem`, calls `NpCommonCleanup`, exits with `FsRtlExitFileSystem`, and completes the IRP unless the common path returned `STATUS_PENDING`. Completion stores the status in `Irp->IoStatus.Status` and uses `IO_NAMED_PIPE_INCREMENT`.

The key behavior is that cleanup closes pipe state and wakes deferred operations, but does not free the CCB itself. Object destruction is handled by close processing.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/cleanup.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/close.c -->
# File Research: sources/windows/reactos/drivers/filesystems/npfs/close.c

This file implements close IRP handling for the ReactOS Named Pipe FileSystem.

`NpCommonClose` gets the current IRP stack location, initializes a deferred IRP list, acquires the NPFS VCB exclusively, and decodes the file object into FCB/CCB/end information. It handles two decoded node types:
- `NPFS_NTC_ROOT_DCB`: decrements the pipe FCB’s `CurrentInstances` count and deletes the CCB with `NpDeleteCcb`, passing the deferred list for any IRPs released by deletion.
- `NPFS_NTC_VCB`: decrements the global `NpVcb->ReferenceCount`.

It then releases the VCB, completes deferred IRPs, marks the close IRP successful, completes it with `IO_NAMED_PIPE_INCREMENT`, and returns `STATUS_SUCCESS`.

`NpFsdClose` is the filesystem-dispatch wrapper. It enters filesystem context, calls `NpCommonClose`, exits filesystem context, and returns the status. Unlike cleanup, the common close path always completes the IRP itself.

The file’s role is final reference teardown: cleanup transitions pipe state, while close releases per-open CCB/root references and VCB references.
<!-- END FILE RESEARCH: sources/windows/reactos/drivers/filesystems/npfs/close.c -->