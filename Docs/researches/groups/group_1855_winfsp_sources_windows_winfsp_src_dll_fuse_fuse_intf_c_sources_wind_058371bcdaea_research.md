# Group Research: WinFsp DLL FUSE and Mount/Network Provider Sources

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_intf.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse_intf.c

This is the central WinFsp-to-FUSE adapter. It implements `FSP_FILE_SYSTEM_INTERFACE fsp_fuse_intf`, translating WinFsp filesystem requests into FUSE 2 callbacks and converting results back into NTSTATUS, Win32 file information, security descriptors, reparse buffers, directory buffers, and extended attributes.

Key responsibilities:
- Operation guard hooks: `fsp_fuse_op_enter` / `fsp_fuse_op_leave` establish per-request `fuse_context`, map Windows paths to POSIX paths, derive uid/gid/pid from access tokens, and apply coarse/fine SRW locking around namespace-sensitive operations.
- File metadata: `fsp_fuse_intf_GetFileInfoFunnel` converts `getattr`/`fgetattr` data into `FSP_FSCTL_FILE_INFO`, including directory/reparse classification, allocation rounding, timestamps, inode index, dot-hidden handling, and optional `stat_ex` flags.
- Security translation: POSIX uid/gid/mode are merged into Windows security descriptors; set-security maps modified descriptors back into chmod/chown operations.
- Create/open/lifecycle: implements create, open, overwrite, cleanup, close, read, write, flush, file info, basic info, and file-size paths using the relevant FUSE callbacks.
- Directory enumeration: builds WinFsp directory buffers via `readdir`/legacy `getdir`; supports readdir-plus metadata fast path and post-fixes entries with `getattr` when needed.
- Delete/rename: checks delete access, verifies directory emptiness through enumeration, and maps Windows rename semantics including collision checks.
- Reparse points: maps POSIX symlinks and special files to Windows symlink/NFS reparse points; setting reparse points creates hidden temporary FUSE nodes and renames them over the placeholder.
- EAs/xattrs: maps Windows extended attributes to FUSE xattr operations.
- Device control: maps WinFsp control codes into Linux-compatible FUSE ioctl command values.
- Token utility: `fsp_fuse_get_token_uidgid` maps Windows token user/owner/primary group SIDs to POSIX uid/gid.

Important dependencies:
- Internal types and macros from `dll/fuse/library.h`.
- WinFsp APIs for path conversion, operation context, directory buffers, reparse resolution, security descriptor conversion, and filesystem dispatch.
- FUSE callback table `struct fuse_operations`.

Filesystem relevance:
- This file is the behavioral core for exposing a FUSE filesystem through the Windows filesystem stack.
- It documents many semantic impedance mismatches: Windows delete-on-close vs FUSE unlink, Windows symlink directory/file distinction, Windows ACLs vs POSIX permissions, EAs vs xattrs, and reparse-point creation over an already-created placeholder.

Notable watchpoints:
- `SetReparsePoint` is explicitly described as unreliable/error-prone because it must create a hidden object and rename it over the placeholder.
- Some Windows attribute merge behavior in overwrite is intentionally incomplete.
- Cleanup paths in complex security/reparse functions should be audited carefully because several allocations and descriptor lifetimes are conditional.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_intf.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_loop.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse_loop.c

This file starts, runs, and stops the WinFsp dispatcher for a FUSE filesystem.

Key responsibilities:
- Starts a minimal WinFsp service thread via `FspServiceRun`.
- Initializes FUSE context and calls the filesystem `init` callback with a FUSE 2.8-like protocol view.
- Advertises WinFsp-specific capabilities such as readdir-plus, read-only, stat-ex, delete-access, and case-insensitive support.
- Probes `statfs`, root `getattr`, `readlink`, slash-dot symlink behavior, delete-access support, and xattr/EA support.
- Normalizes volume parameters including sector size, allocation unit, max component length, creation time, and serial number.
- Creates the `FSP_FILE_SYSTEM`, attaches `fsp_fuse_intf`, sets operation guards/debug logging, sets the mount point, and starts the dispatcher.
- Provides single-threaded and multithreaded loop entry points:
  - `fsp_fuse_loop` uses coarse operation guarding.
  - `fsp_fuse_loop_mt` uses fine operation guarding.
- Stops dispatcher and calls FUSE `destroy` during cleanup.
- Provides a Cygwin signal handler bridge.

Filesystem relevance:
- This file is where a user-mode FUSE instance becomes a live WinFsp filesystem.
- Capability probing here directly changes how `fuse_intf.c` behaves, especially for case sensitivity, symlink handling, EAs, and delete semantics.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_loop.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_main.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse_main.c

This file implements the FUSE 2-style main entry flow.

Key responsibilities:
- Defines command-line options for help, debug/foreground, foreground, and single-thread mode.
- `fsp_fuse_parse_cmdline` extracts the mountpoint and returns multithread/foreground decisions while preserving or forwarding relevant options.
- `fsp_fuse_main_real` performs the standard lifecycle:
  1. Parse command line.
  2. Mount/create a `fuse_chan`.
  3. Create a `struct fuse`.
  4. Daemonize if needed.
  5. Install signal handlers.
  6. Run `fsp_fuse_loop` or `fsp_fuse_loop_mt`.
  7. Tear down signal handlers, fuse object, channel, mountpoint, and args.

Filesystem relevance:
- This is the compatibility entry point for FUSE applications that expect `fuse_main`-like behavior on Windows.
- It is orchestration glue; real filesystem behavior is delegated to `fuse_loop.c`, `fuse_intf.c`, and the application callback table.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_main.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_opt.c -->
# File Research: sources/windows/winfsp/src/dll/fuse/fuse_opt.c

This file implements libfuse-compatible option parsing and argument manipulation.

Key responsibilities:
- Matches option templates against command-line arguments, including exact matches, value-in-same-arg matches, and value-in-next-arg matches.
- Supports `%` conversion specs for integer and string options, with platform-specific handling for `long` width on Cygwin64 vs Win64.
- Parses `-o` comma-separated option lists, including escaped comma/backslash support.
- Calls user option processors with FUSE keys such as `FUSE_OPT_KEY_KEEP`, `FUSE_OPT_KEY_DISCARD`, `FUSE_OPT_KEY_OPT`, and `FUSE_OPT_KEY_NONOPT`.
- Preserves unknown/kept options into output args, grouping `-o` options as expected by FUSE.
- Provides public helpers:
  - `fsp_fuse_opt_parse`
  - `fsp_fuse_opt_add_arg`
  - `fsp_fuse_opt_insert_arg`
  - `fsp_fuse_opt_free_args`
  - `fsp_fuse_opt_add_opt`
  - `fsp_fuse_opt_add_opt_escaped`
  - `fsp_fuse_opt_match`

Filesystem relevance:
- This enables Unix/FUSE-style mount option parsing in the Windows DLL environment.
- It is foundational for `fuse_main.c`, core option parsing, and FUSE3 compatibility setup.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/fuse_opt.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/library.h -->
# File Research: sources/windows/winfsp/src/dll/fuse/library.h

This is the internal header for the WinFsp FUSE 2 layer.

Key contents:
- Includes DLL internals plus FUSE public headers.
- Defines `FSP_FUSE_LIBRARY_NAME`, context-header conversion macros, symlink capability macros, Cygwin/MSVC `ENOSYS` mapping, and NFS reparse constants.
- Defines internal `struct fuse`, holding:
  - Environment pointer.
  - Parsed mount/permission options.
  - FUSE operations and private data.
  - Capability flags and initialized state.
  - Volume parameters, label, mountpoint, loop event, WinFsp filesystem pointer.
  - FUSE3 backpointer and base file security descriptor.
- Defines per-thread `fsp_fuse_context_header`, open-file descriptor state, and directory enumeration handle state.
- Provides allocation helpers `fsp_fuse_obj_alloc` / `fsp_fuse_obj_free`.
- Declares TLS context access, core option data, core parser, operation guards, directory filler helpers, token uid/gid helper, and `fsp_fuse_intf`.

Filesystem relevance:
- This header defines the private state shared by all FUSE 2 adapter files.
- The context-header layout is important: per-request POSIX path storage is placed immediately before `struct fuse_context`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse/library.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse2to3.c -->
# File Research: sources/windows/winfsp/src/dll/fuse3/fuse2to3.c

This file adapts FUSE3 APIs to the existing FUSE2-based WinFsp implementation.

Key responsibilities:
- Converts `fuse_file_info` between FUSE2 and FUSE3 shapes.
- Converts FUSE2 connection info to FUSE3 connection/config structures, advertising a FUSE 3.2-era protocol view.
- Defines wrappers for most FUSE3 operations, forwarding through the active `struct fuse3` callback table:
  - metadata, namespace, file I/O, directory I/O, xattr, lifecycle, access, locking, ioctl, poll, buf I/O, flock, fallocate.
- Converts FUSE3 `readdir` filler semantics into the FUSE2 directory filler helpers in `fuse_intf.c`, including readdir-plus flags.
- Calls FUSE3 `init` with a `fuse3_config`, then maps wanted capabilities back into the FUSE2 `conn->want`.
- Copies and preflights arguments with core FUSE option parsing.
- Implements `fsp_fuse3_new`, `fsp_fuse3_new_30`, `fsp_fuse3_destroy`, `fsp_fuse3_mount`, and `fsp_fuse3_unmount`.
- Mounting builds a FUSE2 operation table of wrapper functions, creates a FUSE2 `struct fuse`, frees the temporary channel/args, and links `fuse` and `fuse3` objects together.

Filesystem relevance:
- FUSE3 support is not a separate backend; it is a compatibility layer over the FUSE2 WinFsp path.
- Any FUSE3 filesystem ultimately reaches `fuse_loop.c` and `fuse_intf.c` after callback adaptation.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse2to3.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3.c -->
# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3.c

This file exposes higher-level FUSE3 entry points.

Key responsibilities:
- `fsp_fuse3_main_real` mirrors the FUSE2 main flow: parse command line, create FUSE3 object, mount it through the adapter, daemonize, install signal handlers, run loop, then unmount/destroy.
- `fsp_fuse3_lib_help` triggers core option help handling.
- Loop APIs delegate to FUSE2 loop functions:
  - `fsp_fuse3_loop`
  - `fsp_fuse3_loop_mt_31`
  - `fsp_fuse3_loop_mt`
- `fsp_fuse3_exit` delegates to `fsp_fuse_exit`.
- `fsp_fuse3_get_context` aliases the FUSE2 context after static layout checks.
- Connection-info option parsing/apply functions are stub-compatible.
- Version helpers return configured FUSE version/package version.

Filesystem relevance:
- This is the public FUSE3 lifecycle facade.
- Its loop and context APIs prove that FUSE3 execution shares the same runtime state as the FUSE2 adapter.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3.pc.in -->
# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3.pc.in

This is the pkg-config template for the WinFsp FUSE3-compatible API.

Key fields:
- `prefix=${pcfiledir}/..`
- headers under `inc/fuse3`
- import library path pointing at `bin/winfsp-${arch}.dll`
- package name `fuse3`
- description `WinFsp FUSE3 compatible API`
- version `3.2`
- URL `https://winfsp.dev`
- emits `Libs` and `Cflags` for consumers.

Filesystem relevance:
- Build/distribution metadata only; no runtime filesystem logic.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3.pc.in -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3_compat.c -->
# File Research: sources/windows/winfsp/src/dll/fuse3/fuse3_compat.c

This file exports plain `fuse3_*` compatibility symbols.

Key responsibilities:
- Includes `dll/library.h`.
- Redefines `FSP_FUSE_API` and `FSP_FUSE_SYM` so included FUSE3 headers emit exported forwarding implementations.
- The comment states these symbols are for FFI consumers such as fusepy or jnr-fuse, not normal C/C++ code; headers expose `fsp_fuse3_*` wrapped by macros for C/C++ consumers.

Filesystem relevance:
- ABI compatibility shim for external FFI callers.
- Runtime behavior is delegated to the default `fsp_fuse_env` and the `fsp_fuse3_*` implementation.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/fuse3_compat.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/library.h -->
# File Research: sources/windows/winfsp/src/dll/fuse3/library.h

This is the internal header for the FUSE3 compatibility layer.

Key contents:
- Includes the FUSE2 internal header, then undefines FUSE2 include/version/main guards before including `fuse3/fuse.h`.
- Defines `struct fuse3` with copied args, FUSE3 operations, user data, and a backpointer to the adapted FUSE2 `struct fuse`.

Filesystem relevance:
- Keeps FUSE2 and FUSE3 headers coexisting in one translation unit.
- Defines the bridge object used by `fuse2to3.c` and `fuse3.c`.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/fuse3/library.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/launch.c -->
# File Research: sources/windows/winfsp/src/dll/launch.c

This file implements client-side launcher communication and launcher registry record management.

Key responsibilities:
- `FspLaunchCallLauncherPipe` / `FspLaunchCallLauncherPipeEx` serialize a command and UTF-16 arguments into the launcher named-pipe protocol, call `FspCallNamedPipeSecurelyEx`, parse success/failure responses, and return launcher Win32 error codes separately from NTSTATUS transport errors.
- `FspLaunchStart`, `FspLaunchStartEx`, `FspLaunchStop`, `FspLaunchGetInfo`, and `FspLaunchGetNameList` are typed wrappers around launcher commands.
- `FspLaunchRegSetRecord` writes or deletes launcher class records under the WinFsp launcher registry key. It handles string fields such as executable, command line, run-as, security, auth package, stderr, and integer fields such as job control, credentials, auth package id, and recovery.
- `FspLaunchRegGetRecord` reads a launcher class record, optionally filters by agent, validates registry types/termination, packs strings into one allocated record buffer, and applies default job-control behavior.
- `FspLaunchRegFreeRecord` frees records allocated by `FspLaunchRegGetRecord`.

Filesystem relevance:
- Launcher records and pipe commands are used by mount/network-provider flows to start and stop managed user-mode filesystems.
- Secret/credential-aware start paths are important for network provider integration.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/launch.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/ldap.c -->
# File Research: sources/windows/winfsp/src/dll/ldap.c

This file wraps a small subset of Windows LDAP APIs used by WinFsp.

Key responsibilities:
- `FspLdapConnect` initializes an LDAP connection, enables signing/encryption, and binds with negotiated authentication.
- `FspLdapClose` unbinds the connection.
- `FspLdapGetValue` performs a synchronous search for one attribute and copies the first value into WinFsp-allocated memory.
- `FspLdapGetDefaultNamingContext` reads `defaultNamingContext` from the root DSE.
- `FspLdapGetTrustPosixOffset` searches trusted domain records under `CN=System,<context>` and returns `trustPosixOffset`, matching by flat name or DNS-style name.

Filesystem relevance:
- Supports identity mapping / domain trust integration for POSIX uid/gid behavior in Windows environments.
- No filesystem dispatch logic is here; it is directory-service support.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/ldap.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/library.c -->
# File Research: sources/windows/winfsp/src/dll/library.c

This file contains DLL entry and COM-style self-registration hooks.

Key responsibilities:
- Stores `DllInstance` on process attach.
- On process detach, finalizes FUSE, service, filesystem, event log, POSIX, and well-known SID subsystems, passing whether detach is dynamic.
- On thread detach, finalizes per-thread FUSE state.
- Provides `_DllMainCRTStartup` as a minimal CRT startup alias to `DllMain`.
- `DllRegisterServer` registers the WinFsp fsctl device, network provider, and event log, treating fsctl registration as critical and later registrations as non-critical.
- `DllUnregisterServer` unregisters the same components.

Filesystem relevance:
- This is lifecycle and installation glue for the WinFsp DLL.
- Correct finalization matters because FUSE context storage is thread-local and cleaned during thread detach.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/library.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/library.h -->
# File Research: sources/windows/winfsp/src/dll/library.h

This is the shared internal header for the WinFsp DLL.

Key contents:
- Enables `WINFSP_DLL_INTERNAL` and includes public WinFsp headers, launcher API, minimal runtime support, `strsafe`, and configuration.
- Defines `LIBRARY_NAME`, debug logging/test macros, and finalize/register function declarations.
- Declares subsystem helpers for SxS suffixing, well-known SIDs, Mount Manager calls, LDAP calls, diagnostics, directory creation, module version/path lookup, adaptive locks, directory buffer peeking, service stop/control handling.
- Provides path helpers:
  - `FspPathSuffixIndex`
  - `FspPathIsDrive`
  - `FspPathIsMountmgrMountPoint`
  - `FspPathIsMountmgrDrive`
- Defines `FSP_NEXT_EA` for EA walking.

Filesystem relevance:
- Central declaration surface for the DLL implementation files in this group.
- The mount path helpers are used directly by `mount.c` and network/mount workflows.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/library.h -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/mount.c -->
# File Research: sources/windows/winfsp/src/dll/mount.c

This file implements mount-point creation and removal for WinFsp volumes.

Key responsibilities:
- Initializes optional `ntdll` symbolic-link functions and registry-controlled mount behavior:
  - `MountDoNotUseLauncher`
  - `MountBroadcastDriveChange`
  - `MountUseMountmgrFromFSD`
- Supports Mount Manager drive and directory mount flows, either through user-mode Mount Manager calls or by delegating to the FSD depending on registry configuration.
- Supports DOS drive-letter mounts via `DefineDosDeviceW`; when in a non-LocalSystem service context, can ask the launcher to define/remove global drive symlinks.
- Makes drive symbolic links temporary with `NtMakeTemporaryObject` when possible.
- Broadcasts device change notifications in a detached thread to avoid Explorer/shell hangs.
- Notifies shell on drive removal to clear stale navigation entries.
- Creates directory mount points by creating a directory handle with delete-on-close and setting an `IO_REPARSE_TAG_MOUNT_POINT` reparse buffer.
- Rejects directory mount points that point to network-style volume names, since Windows junctions cannot target network filesystems.
- `FspMountSet_Internal` handles automatic drive selection for `*:` and dispatches by mountpoint type.
- `FspMountSet` optionally sends an early `Transact0` workaround for drive mounts under `FSP_CFG_REJECT_EARLY_IRP`.
- `FspMountRemove` dispatches removal and sends shell cleanup notification for drives.

Filesystem relevance:
- This is the Windows namespace attachment layer for WinFsp volumes.
- It handles the difference between DOS drive symlinks, Mount Manager drive letters, Mount Manager directory mount points, and raw directory junction-style mount points.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/mount.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/np.c -->
# File Research: sources/windows/winfsp/src/dll/np.c

This file implements the Windows Network Provider API for WinFsp network-style filesystems.

Key responsibilities:
- `NPGetCaps` advertises connection, enumeration, provider type, spec version, and startup capabilities.
- Parses local drive names and WinFsp remote names of the form `\\Class\Instance`.
- Calls launcher pipe commands for start/stop/info operations, optionally allowing impersonation for suitable launcher records.
- Reads launcher registry records to determine auth package, credential requirements, and impersonation behavior.
- Supports credential prompting via CredUI, optional credential manager reads/writes, and password/user-password credential modes.
- `FspNpCheckRemoteVolume` probes an existing UNC path and verifies it is a WinFsp volume via `FSP_FSCTL_QUERY_WINFSP`.
- `NPGetConnection` maps a local drive letter back to a WinFsp remote name by comparing DOS device targets to the WinFsp network volume list.
- `NPAddConnection` validates names, gathers credentials, starts the filesystem through the launcher, waits for the root path to become accessible, and handles already-running instances.
- `NPAddConnection3` adds interactive prompting/retry behavior and optional credential persistence.
- `NPCancelConnection` resolves a drive or remote name and asks the launcher to stop the instance.
- `NPGetUniversalName` converts local drive paths to UNC/universal name structures.
- `NPOpenEnum`, `NPEnumResource`, and `NPCloseEnum` enumerate connected/context network resources by walking the WinFsp network volume list and associating drive letters where possible.
- `FspNpRegister` creates service/network-provider registry keys, writes provider metadata/path/device name, and inserts `WinFsp.Np` into `ProviderOrder` first.
- `FspNpUnregister` removes the provider from `ProviderOrder` and deletes its service registry tree.

Filesystem relevance:
- This is the integration layer that makes WinFsp UNC-style filesystems appear as Windows network resources.
- It connects the launcher service, credential UI/storage, MPR network-provider callbacks, and WinFsp volume enumeration.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/np.c -->

<!-- BEGIN FILE RESEARCH: sources/windows/winfsp/src/dll/ntstatus.c -->
# File Research: sources/windows/winfsp/src/dll/ntstatus.c

This file maps between Win32 errors and NTSTATUS values.

Key responsibilities:
- Lazily resolves `RtlNtStatusToDosError` from `ntdll.dll`.
- `FspNtStatusFromWin32` uses generated mappings from `ntstatus.i`; unknown 16-bit Win32 errors become `FACILITY_NTWIN32` HRESULT-style NTSTATUS values, while larger unknown errors become `STATUS_ACCESS_DENIED`.
- `FspWin32FromNtStatus` delegates to `RtlNtStatusToDosError`, returning `ERROR_MR_MID_NOT_FOUND` if unavailable.

Filesystem relevance:
- Error translation is used throughout the DLL when bridging Windows API failures, launcher/provider errors, and NTSTATUS-returning WinFsp APIs.
<!-- END FILE RESEARCH: sources/windows/winfsp/src/dll/ntstatus.c -->