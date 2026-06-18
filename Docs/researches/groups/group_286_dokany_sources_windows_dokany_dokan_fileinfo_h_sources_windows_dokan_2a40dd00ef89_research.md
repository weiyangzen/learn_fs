# Group Research: group_286_dokany_sources_windows_dokany_dokan_fileinfo_h_sources_windows_dokan_2a40dd00ef89

Scope: `Docs/research_subset_a.md`, covering Dokany user-mode/kernel API support files and the Dokan FUSE compatibility layer under `sources/windows/dokany`.

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/fileinfo.h -->
# File Research: sources/windows/dokany/dokan/fileinfo.h

Defines Windows NT file-system interface constants and structures used by Dokan user-mode dispatch code.

Key contents:
- IRP major/minor constants for create, read, write, query/set information, volume information, security, lock, cleanup, and PnP style operations.
- `FILE_INFORMATION_CLASS` and `FS_INFORMATION_CLASS` enums mirroring Windows kernel information classes.
- Struct definitions for file metadata, directory enumeration, rename/link/disposition, streams, volume labels, size/attribute info, network open info, and `UNICODE_STRING`.
- Flexible trailing array structs such as `FILE_NAME_INFORMATION`, `FILE_DIRECTORY_INFORMATION`, `FILE_RENAME_INFORMATION`, and volume/file-system name records.
- Alignment helpers: `ALIGN_DOWN`, `ALIGN_UP`, pointer alignment variants, word/long/quad alignment, and quad-alignment check.
- Create/open disposition and option flag constants copied from WDM-style definitions.
- Delete disposition flags, including POSIX semantics and on-close behavior.

Important behavior:
- This is a compatibility contract header, not executable logic.
- Many structures are consumed by `setfile.c`, `volume.c`, and other dispatchers to interpret buffers coming from the Dokan driver.
- Several definitions overlap Windows SDK/DDK types, allowing Dokan’s user-mode component to compile with the needed NT structures available.

Risks and notes:
- Many structs use one-element trailing arrays and require careful buffer-length accounting by callers.
- The file intentionally redefines low-level NT concepts; mismatches with newer Windows headers would affect ABI interpretation.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/fileinfo.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/flush.c -->
# File Research: sources/windows/dokany/dokan/flush.c

Implements `DispatchFlush`, the user-mode event handler for flush buffer requests.

Key behavior:
- Validates/logs the flush target path via `CheckFileName`.
- Initializes the dispatch result with `CreateDispatchCommon` and no output payload.
- Calls `DokanOperations->FlushFileBuffers` if the filesystem supplied it.
- Treats `STATUS_NOT_IMPLEMENTED` as successful flush completion.
- Converts other non-success callback statuses to `STATUS_NOT_SUPPORTED`.
- Completes the request with `EventCompletion`.

Role in architecture:
- Bridges Dokan driver flush requests to the filesystem’s `FlushFileBuffers` callback.
- Keeps flush optional, matching common filesystem behavior where no explicit flush hook is required.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/flush.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/list.h -->
# File Research: sources/windows/dokany/dokan/list.h

Provides inline Windows-style doubly and singly linked-list helpers.

Key contents:
- Doubly linked-list helpers: `InitializeListHead`, `IsListEmpty`, `RemoveEntryList`, `RemoveHeadList`, `RemoveTailList`, `InsertTailList`, `InsertHeadList`, `AppendTailList`.
- Singly linked-list helpers: `PopEntryList`, `PushEntryList`.
- Uses `LIST_ENTRY` and `SINGLE_LIST_ENTRY` from Windows headers.

Important behavior:
- `IsListEmpty` treats `NULL` as empty.
- `RemoveEntryList(NULL)` returns `TRUE`, assuming an empty-list case.
- No locking is provided; callers must synchronize if lists are shared.

Role in architecture:
- Supplies kernel-style list primitives for user-mode Dokan code without depending on DDK inline definitions.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/list.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/lock.c -->
# File Research: sources/windows/dokany/dokan/lock.c

Implements `DispatchLock`, mapping lock-control requests to filesystem callbacks.

Key behavior:
- Initializes dispatch result and defaults status to `STATUS_NOT_IMPLEMENTED`.
- Handles:
  - `IRP_MN_LOCK`: calls `DokanOperations->LockFile`; non-success maps to `STATUS_LOCK_NOT_GRANTED`.
  - `IRP_MN_UNLOCK_SINGLE`: calls `DokanOperations->UnlockFile`; any implemented result is reported as success.
  - `IRP_MN_UNLOCK_ALL` and `IRP_MN_UNLOCK_ALL_BY_KEY`: no implementation in this layer.
- Logs unknown minor functions.
- Completes through `EventCompletion`.

Role in architecture:
- Provides byte-range lock/unlock plumbing between the driver and user callbacks.
- Ignores lock keys; code comments show key fields are intentionally not passed through.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/lock.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/makefile -->
# File Research: sources/windows/dokany/dokan/makefile

Minimal Windows NT DDK makefile shim.

Key contents:
- Warns that source membership should be edited elsewhere.
- Includes `$(NTMAKEENV)\makefile.def`.
- Sets `C_DEFINES = /DUNICODE`.

Role:
- Legacy DDK build integration for the Dokan component.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/makefile -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/mount.c -->
# File Research: sources/windows/dokany/dokan/mount.c

Implements service, registry, mount-point, unmount, and shell notification support for Dokan.

Key areas:
- Defines a local `REPARSE_DATA_BUFFER` for mount-point reparse point creation.
- Service helpers:
  - `DokanServiceExists`
  - `DokanServiceControl`
  - `DokanServiceInstall`
  - `DokanServiceDelete`
- Event log registry install/uninstall:
  - `DokanDriverEventLogInstall`
  - `DokanDriverEventLogUninstall`
- Network provider registry install/uninstall:
  - `DokanNetworkProviderInstall`
  - `DokanNetworkProviderUninstall`
- Mount-point helpers:
  - `CreateMountPoint`
  - `DeleteMountPoint`
  - `DokanMount`
  - `GenerateUnmountPoint`
  - `DokanRemoveMountPoint`
  - `DokanNotifyUnmounted`
- Drive-letter broadcast helpers:
  - `EnableTokenPrivilege`
  - `DokanBroadcastCallback`
  - `DokanBroadcastLink`

Important behavior:
- Directory mount points are created as `IO_REPARSE_TAG_MOUNT_POINT` reparse points pointing at `\??<DeviceName>\`.
- Drive-letter mounts notify applications and Explorer with `BroadcastSystemMessage` and `SHChangeNotify`.
- Non-drive mount cleanup removes the mount point unless mount manager was used.
- `DokanRemoveMountPoint` sends a global release IRP rather than directly deleting the reparse point.
- Unmount notification calls the filesystem’s `Unmounted` callback if present.

Risks and notes:
- Registry updates require admin rights and write under `HKLM`.
- Network provider order editing manipulates comma-delimited provider strings.
- Broadcast work is asynchronous via threadpool work to avoid hangs in message receivers.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/ntstatus.c -->
# File Research: sources/windows/dokany/dokan/ntstatus.c

Maps Win32 error codes to NTSTATUS values.

Key behavior:
- `DokanNtStatusFromWin32(DWORD Error)` uses generated include `ntstatus.i` inside a switch.
- Unknown Win32 errors are logged and mapped to `STATUS_ACCESS_DENIED`.

Role:
- Used where Win32 API failures must be returned through Dokan’s NTSTATUS-oriented protocol, such as write request handling.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/ntstatus.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/read.c -->
# File Research: sources/windows/dokany/dokan/read.c

Implements `DispatchRead`, the read request dispatcher.

Key behavior:
- Allocates an output buffer sized to the requested read length using `CreateDispatchCommon` with extra memory pool enabled.
- Calls `DokanOperations->ReadFile` with filename, output buffer, requested length, offset, and `DOKAN_FILE_INFO`.
- Defaults status to `STATUS_NOT_IMPLEMENTED`.
- On success:
  - zero bytes read becomes `STATUS_END_OF_FILE`;
  - nonzero bytes set `BufferLength`;
  - updates `CurrentByteOffset`.
- Completes through `EventCompletion`.

Role:
- Bridges kernel read events to user filesystem read callbacks and packages returned bytes for the driver.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/read.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/resource.h -->
# File Research: sources/windows/dokany/dokan/resource.h

Visual Studio generated resource header for `dokan.rc`.

Key contents:
- `#pragma once`
- Default AP Studio values guarded by `APSTUDIO_INVOKED`.
- No runtime code or filesystem behavior.

Role:
- Supports Windows resource compilation.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/resource.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/security.c -->
# File Research: sources/windows/dokany/dokan/security.c

Implements security descriptor query/set dispatch and a default security descriptor provider.

Key behavior:
- `DefaultGetFileSecurity`:
  - obtains current process user and first group SID;
  - builds SDDL owner/group text;
  - grants authenticated users full access, with directory inheritance flags for directories;
  - converts requested security information to a binary security descriptor;
  - returns `STATUS_BUFFER_OVERFLOW` with required length if the output buffer is too small.
- `DispatchQuerySecurity`:
  - calls filesystem `GetFileSecurity` if available;
  - falls back to `DefaultGetFileSecurity` on `STATUS_NOT_IMPLEMENTED`;
  - sets output buffer length on success or overflow.
- `DispatchSetSecurity`:
  - obtains the descriptor from an offset inside `EventContext`;
  - calls filesystem `SetFileSecurity` if available;
  - maps any non-success to `STATUS_INVALID_PARAMETER`.

Risks and notes:
- Some error paths in `DefaultGetFileSecurity` return before freeing all allocated SDDL strings/descriptors.
- Default ACL behavior is permissive toward authenticated users and intended as a fallback for UI/context-menu compatibility.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/security.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/setfile.c -->
# File Research: sources/windows/dokany/dokan/setfile.c

Implements file information mutation dispatch for allocation size, basic info, disposition, EOF, rename, and valid data length.

Key helpers:
- `DokanSetAllocationInformation`: calls `SetAllocationSize`.
- `DokanSetBasicInformation`: calls `SetFileAttributes`, then `SetFileTime`.
- `DokanSetDispositionInformation`: interprets classic and extended disposition structures, checks read-only attributes when possible, sets `DeletePending`, and calls `DeleteFile` or `DeleteDirectory`.
- `DokanSetEndOfFileInformation`: calls `SetEndOfFile`.
- `DokanSetRenameInformation`: copies the variable-length new name to a null-terminated buffer and calls `MoveFile`.
- `DokanSetValidDataLengthInformation`: delegates to `SetEndOfFile`.

`DispatchSetInformation`:
- Allocates result buffer for rename cases so the new name can be echoed back.
- Switches on `FileInformationClass`.
- Reports delete-pending state for successful disposition requests.
- Copies rename target into result buffer on successful rename.
- Completes through `EventCompletion`.

Important behavior:
- `FilePositionInformation` is intentionally left to the driver and returns `STATUS_NOT_IMPLEMENTED`.
- Unknown information classes leave `STATUS_INVALID_PARAMETER`.
- Deletion is rejected as `STATUS_CANNOT_DELETE` for read-only files when attributes can be queried.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/setfile.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/timeout.c -->
# File Research: sources/windows/dokany/dokan/timeout.c

Implements `DokanResetTimeout`, allowing user callbacks to extend/reset a pending operation timeout.

Key behavior:
- Retrieves the active `DOKAN_IO_EVENT` from `FileInfo->DokanContext`.
- Validates event context and instance.
- Allocates an `EVENT_INFORMATION`, fills serial number and requested timeout.
- Sends `FSCTL_RESET_TIMEOUT` to the raw device name.
- Frees the event info and returns the `SendToDevice` result.
- Sets `ERROR_INVALID_PARAMETER` or `ERROR_OUTOFMEMORY` on local validation/allocation failures.

Role:
- Lets long-running filesystem callbacks keep the driver-side request from timing out.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/timeout.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/version.c -->
# File Research: sources/windows/dokany/dokan/version.c

Exposes user library and driver version queries.

Key behavior:
- `DokanVersion()` returns compile-time `DOKAN_VERSION`.
- `DokanDriverVersion()` sends `FSCTL_GET_VERSION` to `DOKAN_GLOBAL_DEVICE_NAME`.
- On device query failure, logs and returns `0`.

Role:
- Supports runtime compatibility checks between user-mode library and installed Dokan driver.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/version.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/volume.c -->
# File Research: sources/windows/dokany/dokan/volume.c

Handles volume information queries and default volume/free-space callbacks.

Key behavior:
- Default disk space: 1 GiB total, 512 MiB available/free.
- Default volume information:
  - volume name `DOKAN`;
  - serial `0x19831116`;
  - max component length `256`;
  - flags for case sensitivity/preservation, remote storage, and Unicode;
  - filesystem name `NTFS`.
- `DokanGetVolumeInformation` calls user callback if present, otherwise default.
- Implements query handlers for:
  - `FileFsVolumeInformation`
  - `FileFsSizeInformation`
  - `FileFsAttributeInformation`
  - `FileFsFullSizeInformation`
- Size handlers convert bytes to allocation units using `DokanOptions->AllocationUnitSize` and `SectorSize`.
- `DispatchQueryVolumeInformation` allocates the result buffer and dispatches by `FsInformationClass`.

Risks and notes:
- Buffer truncation is handled for string-style results; attribute info returns `STATUS_BUFFER_OVERFLOW` if the filesystem name is truncated.
- Default filesystem identity is NTFS-like even though backing semantics are supplied by user code.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/volume.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan/write.c -->
# File Research: sources/windows/dokany/dokan/write.c

Implements write dispatch, including a second driver round trip when the write payload is larger than the initial event batch.

Key behavior:
- `SendWriteRequest`:
  - uses pooled batch buffer for small contexts;
  - mallocs a larger `DOKAN_IO_BATCH` for large write event contexts;
  - sends `FSCTL_EVENT_WRITE` to fetch the full write payload from the driver.
- `DispatchWrite`:
  - initializes a no-output dispatch result;
  - if `RequestLength > 0`, retrieves a larger write context first;
  - maps `ERROR_OPERATION_ABORTED` to `STATUS_CANCELLED`;
  - maps other Win32 errors through `DokanNtStatusFromWin32`;
  - calls filesystem `WriteFile` with payload, length, offset, and file info;
  - on success, reports bytes written and updated `CurrentByteOffset`;
  - returns any temporary batch buffer to pool or frees it.

Role:
- Handles Dokan’s split write protocol where large write payloads are fetched on demand.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan/write.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/CMakeLists.txt -->
# File Research: sources/windows/dokany/dokan_fuse/CMakeLists.txt

Build definition for the Dokan FUSE 2 compatibility DLL.

Key contents:
- Requires CMake 3.22.1 and project name `dokanfuse2`.
- Defaults build type to `Release`.
- Enables optional `FUSE_PKG_CONFIG` generation.
- Adds C++ flags `-std=c++11 -mwin32 -Wall` and `_FILE_OFFSET_BITS=64`.
- Includes local `include` and Dokan `sys` headers.
- Builds shared library `dokanfuse2` from `src/*.cpp`, `src/*.c`, and `src/*.rc`.
- Installs FUSE compatibility headers under `${includedir}/fuse`, old compatibility header under `${includedir}`, optional `fuse.pc`, and library artifacts.

Role:
- Packages Dokan’s FUSE API adapter as a libfuse-compatible Windows library.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/CMakeLists.txt -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/dokanfuse.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/dokanfuse.h

Private C++ definitions for the Dokan FUSE compatibility layer.

Key contents:
- `FUSE_THREAD_COUNT` and `DOKAN_DLL` naming macro.
- `printf` format macros for `DWORD`/`ULONG` across LP64 and LLP64 environments.
- `fuse_config` storing parsed FUSE/Dokan options: masks, names, debug, mount manager, read-only, timeout, removable/network flags, allocation unit, sector size, and max read.
- `fuse_session` and `fuse_chan`.
- `fuse_chan` dynamically loads Dokan DLL functions: `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanUnmount`, `DokanRemoveMountPoint`.
- `fuse` object storing loop state, channel/session, config, operations, and user data.

Role:
- Holds the bridge’s runtime state and dynamic linking boundary to `dokan*.dll`.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/dokanfuse.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fuse.h

Public high-level FUSE 2.x API compatibility header adapted for Windows.

Key contents:
- Includes `fuse_win.h` on Windows and defines `FUSE_OFF_T`/`FUSE_STAT` abstractions.
- Defaults `FUSE_USE_VERSION` to 27.
- Defines `fuse_fill_dir_t`, deprecated directory types, `fuse_operations`, and `fuse_context`.
- `fuse_operations` covers classic FUSE high-level callbacks:
  - metadata: `getattr`, `fgetattr`, `access`, `chmod`, `chown`, times;
  - namespace: `mknod`, `mkdir`, `unlink`, `rmdir`, `rename`, links;
  - file I/O: `open`, `read`, `write`, `flush`, `release`, `fsync`;
  - directory I/O: `opendir`, `readdir`, `releasedir`, `fsyncdir`;
  - xattrs, `statfs`, locking, `bmap`, init/destroy.
- Adds Windows-specific extension callbacks:
  - `win_get_attributes`
  - `win_set_attributes`
  - `win_set_times`
- Declares main/setup/loop API: `fuse_main`, `fuse_new`, `fuse_loop`, `fuse_loop_mt`, `fuse_exit`, `fuse_setup`, `fuse_teardown`.
- Declares stacking/module APIs and per-operation `fuse_fs_*` wrappers.
- Includes compatibility macro remapping for older FUSE API versions.

Role:
- Allows FUSE-style filesystem programs to compile against Dokan’s Windows adapter.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_common.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fuse_common.h

Common public FUSE definitions shared by high-level and low-level headers.

Key contents:
- Enforces inclusion through `fuse.h` or `fuse_lowlevel.h`.
- Defines FUSE version as 2.7.
- Enforces `_FILE_OFFSET_BITS=64` outside MSVC.
- Defines `fuse_file_info` with flags, direct I/O/cache bits, flush marker, file handle, and lock owner.
- Defines `fuse_conn_info` with protocol version, async read flag, max write, max readahead, and reserved fields.
- Declares mount/unmount, command-line parsing, daemonize, version, and signal handler APIs.
- Provides compatibility remaps for older FUSE API versions.

Role:
- Supplies stable libfuse 2 common ABI declarations used by the compatibility implementation.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_common.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_opt.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fuse_opt.h

Public FUSE option parsing API.

Key contents:
- Defines `struct fuse_opt` templates with offset/value actions.
- Defines `FUSE_OPT_KEY`, `FUSE_OPT_END`, and `struct fuse_args`.
- Defines option processing keys:
  - `FUSE_OPT_KEY_OPT`
  - `FUSE_OPT_KEY_NONOPT`
  - `FUSE_OPT_KEY_KEEP`
  - `FUSE_OPT_KEY_DISCARD`
- Declares `fuse_opt_parse`, argument insertion/add/free helpers, option list helper, and matcher.
- Uses `_strdup` on MSVC and `strdup` elsewhere via `STRDUP`.

Role:
- Lets callers and the Dokan FUSE layer parse libfuse-style command-line and `-o` option groups.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_opt.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_sem_fix.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fuse_sem_fix.h

Cygwin-only semaphore compatibility shim.

Key contents:
- Under `__CYGWIN__`, declares `my_sem_init`, `my_sem_destroy`, `my_sem_post`, and `my_sem_wait`.
- Redefines `sem_init`, `sem_destroy`, `sem_wait`, and `sem_post` to those wrappers.

Role:
- Lets Cygwin builds use Windows semaphore-backed implementations supplied in `fuse_helpers.c`.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_sem_fix.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_win.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fuse_win.h

Windows portability header for FUSE compatibility.

Key contents:
- Defaults `FUSE_USE_VERSION` to 27.
- Defines default volume and filesystem names.
- Declares errno/NTSTATUS translation helpers and MSVC wide-argument conversion helpers.
- Declares global wide strings for Dokan filesystem and volume names.
- Fills missing POSIX-ish types and structs for MinGW/MSVC:
  - `gid_t`, `uid_t`, `pid_t`, `nlink_t`, `blksize_t`, `blkcnt_t`, `uint64_t`;
  - `timespec` when absent;
  - `statvfs`;
  - `flock`.
- Forces wide offset mode with `FUSE_OFF_T __int64`.
- Defines `stat64_cygwin` as the adapter’s `FUSE_STAT`.
- Defines simple locking constants `F_WRLCK`, `F_UNLCK`, `F_SETLK`.

Role:
- Provides enough Unix type surface for FUSE code to compile on Windows toolchains.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fuse_win.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fusemain.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/fusemain.h

Private C++ bridge declarations mapping FUSE operations to Dokan callbacks.

Key contents:
- Includes Dokan public API, FUSE API, and utility helpers.
- Defines `CHECKED` and `MAX_READ_SIZE`.
- Declares:
  - `impl_file_locks`: global map of open path lock state guarded by `CRITICAL_SECTION`.
  - `impl_chain_link` and `impl_chain_guard`: per-thread call context stack for `fuse_get_context`.
  - `win_error`: errno-to-NTSTATUS wrapper.
  - `impl_fuse_context`: main adapter object holding FUSE ops, connection info, masks, names, max read, and lock manager.
  - `impl_file_lock`: per-path open-handle and byte-range lock coordinator.
  - `impl_file_handle`: per-open state with flags, FUSE file handle, share mode, and locks.
- `impl_fuse_context` declares adapters for nearly every Dokan operation: create/open, directory enumeration, cleanup, close, read/write, flush, metadata, delete, move, locks, truncation, times, volume, mounted/unmounted.

Role:
- Defines the in-memory model for Dokan FUSE: stateful open handles, context propagation, and callback translation.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/fusemain.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/old/fuse.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/old/fuse.h

Compatibility include for older software expecting `<fuse.h>` from a different include layout.

Key contents:
- Documentation comment tells users to prefer `pkg-config --cflags fuse`.
- Includes `"fuse/fuse.h"`.

Role:
- Installed at the include root to forward old include patterns to the modern `fuse/` subdirectory.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/old/fuse.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/utils.h -->
# File Research: sources/windows/dokany/dokan_fuse/include/utils.h

Utility declarations and stat-to-Windows-find-data conversion template for Dokan FUSE.

Key contents:
- UTF-8/wide conversion declarations.
- Unix/FileTime conversion helpers.
- C++ string path helpers: `wchar_to_utf8_cstr`, `unixify`, `extract_file_name`, `extract_dir_name`.
- `convertStatlikeBuf` template:
  - maps directory mode to `FILE_ATTRIBUTE_DIRECTORY`, otherwise normal;
  - maps 64-bit size to high/low Windows fields;
  - converts ctime/atime/mtime to creation/access/write FILETIMEs;
  - marks files read-only when no write bits are set;
  - marks dotfiles hidden.

Role:
- Shared utility surface for converting FUSE stat-style data into Dokan/Win32 metadata.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/include/utils.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/pkg-config.pc.in -->
# File Research: sources/windows/dokany/dokan_fuse/pkg-config.pc.in

Template for installing a libfuse-compatible `fuse.pc`.

Key contents:
- Uses configured install prefix, libdir, and includedir.
- Reports name `Dokan FUSE`.
- Describes the library as FUSE API compatibility for Dokan.
- Reports version `2.6.0` to match the advertised libfuse compatibility level rather than Dokan’s own version.
- Emits link flag `-l@PROJECT_NAME@`.
- Emits include path and `_FILE_OFFSET_BITS=64`.

Role:
- Lets existing FUSE build systems discover Dokan FUSE via pkg-config.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/pkg-config.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/dokanfuse.cpp -->
# File Research: sources/windows/dokany/dokan_fuse/src/dokanfuse.cpp

Implements the high-level Dokan FUSE runtime wrapper and Dokan callback table.

Key areas:
- DLL initialization stores module instance and disables per-thread attach notifications.
- Defines `the_impl` to recover `impl_fuse_context` from `DokanOptions->GlobalContext`.
- Static Dokan callbacks wrap operations with `impl_chain_guard`, debug logging, and errno-to-NTSTATUS conversion:
  - create/open, cleanup, close;
  - read/write/flush;
  - get file info, find files;
  - delete file/directory;
  - move, lock/unlock;
  - set EOF/allocation/attributes/times;
  - disk free space, volume info;
  - mounted/unmounted.
- `dokanOperations` table wires those callbacks into Dokan.
- `do_fuse_loop`:
  - computes file/dir masks;
  - creates `impl_fuse_context`;
  - fills `DOKAN_OPTIONS`;
  - maps FUSE options to Dokan options such as mount manager, removable, network, write protect, debug, stderr, IPC batching;
  - converts mountpoint to wide string;
  - dynamically loads Dokan through `fuse_chan::init`;
  - calls `DokanMain`.
- `fuse_chan::init`:
  - loads `dokan<major>.dll`;
  - checks `DokanVersion`;
  - resolves `DokanInit`, `DokanShutdown`, `DokanMain`, `DokanUnmount`, and `DokanRemoveMountPoint`;
  - calls `DokanInit`.
- FUSE API emulation:
  - parses library options through `fuse_opt_parse`;
  - implements `fuse_mount`, `fuse_unmount`, `fuse_new`, `fuse_exit`, `fuse_destroy`, `fuse_setup`, `fuse_teardown`, `fuse_loop`, `fuse_loop_mt`, `fuse_main_real`.
- `fuse_session_exit` unmounts the attached Dokan mount.

Important behavior:
- Dokan DLL loading is deferred until the main loop to avoid Cygwin fork/daemonization issues.
- `fuse_interrupted` is a stub returning `0`.
- `FuseSetAllocationSize` truncates EOF only when requested allocation size is less than current file size; otherwise it succeeds without allocating.
- `fuse_exit` unmounts to force `DokanMain` loop termination.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/dokanfuse.cpp -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fuse_helpers.c -->
# File Research: sources/windows/dokany/dokan_fuse/src/fuse_helpers.c

Implements FUSE helper command-line parsing, daemonization, version reporting, signal handling, and Cygwin semaphore wrappers.

Key behavior:
- Parses helper options:
  - `-d`, `debug`, `-f`, `-s`, `fsname=`;
  - help/version keys;
  - first non-option as mountpoint.
- `fuse_parse_cmdline`:
  - runs option parsing;
  - adds default `-ofsname=<program basename>` if none supplied;
  - returns mountpoint, multithreaded flag, and foreground flag.
- `fuse_daemonize`:
  - on Cygwin, calls `daemon(0, 0)`;
  - elsewhere on Windows, detaches with `FreeConsole`.
- `fuse_version` returns `FUSE_VERSION`.
- Cygwin signal support stores a global session and exits it on HUP/INT/TERM, ignores PIPE, and restores defaults on removal.
- Non-Cygwin signal handlers are no-ops.
- Cygwin semaphore wrappers map POSIX-like calls to Windows semaphore handles.

Risks and notes:
- Mountpoint handling deliberately avoids `realpath` because Cygwin paths do not match Dokan’s expectations.
- Non-Cygwin “daemonize” can fail if `FreeConsole` fails.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fuse_helpers.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fuse_opt.c -->
# File Research: sources/windows/dokany/dokan_fuse/src/fuse_opt.c

Implements libfuse-style option parsing.

Key behavior:
- Manages allocated `fuse_args` with add, insert, and free helpers.
- Supports comma-separated `-o` option groups.
- Matches option templates with exact, `=`, or space-separated parameter forms.
- Handles template actions:
  - direct integer assignment by struct offset;
  - formatted parameter assignment, including allocated `%s`;
  - callback invocation with special keys;
  - keep/discard semantics.
- Converts two-argument options into single logical option strings for processing.
- Preserves non-options and handles `--` non-option marker.
- Re-inserts collected `-o` options into output args.
- `fuse_opt_match` tests a single option against an option table.

Role:
- Core parser used by both helper parsing and Dokan-specific FUSE option parsing.
<!-- END FILE RESEARCH: sources/windows/dokany/dokan_fuse/src/fuse_opt.c -->