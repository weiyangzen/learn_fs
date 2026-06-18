# subset-b-007802 OpenAFS scout/sys/tests research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/scout.c -->
# sources/distributed-fs/openafs/src/scout/scout.c

## Purpose
`scout.c` implements the OpenAFS `scout` monitoring command, a terminal GTX/curses dashboard that periodically probes one or more file servers and displays current connections, fetch/store counters, workstation counts, and per-partition free-space lights. It is a standalone user-facing monitoring program layered over `fsprobe`.

## Important APIs, types, and functions
The display model is built from `struct mini_screen`, `struct mini_line`, and `struct scout_disk`. A `mini_line` owns GTX light objects for connection/fetch/store/workstation/server-name columns plus a fixed `VOLMAXPARTS` disk pool split into used and free linked lists. Important functions are `main`, `scoutInit`, `execute_scout`, `FS_Handler`, `init_mini_line`, `mini_initLightObject`, `mini_justify`, `mini_PrintDiskStats`, `scout_FindUsedDisk`, `scout_RecomputeLightLocs`, `scout_SetNonDiskLightLine`, `scout_SetColumnWidths`, and `scout_AdoptThresholds`.

## Control flow
`main` defines the `cmd` syntax and dispatches to `scoutInit`. `scoutInit` parses servers, basename, probe frequency, hostname display, attention thresholds, debug file, and column widths, then calls `execute_scout`. `execute_scout` initializes soft signals and GTX, resolves server names into port-7000 socket entries, creates banner and per-server light objects, initializes `fsprobe_Init` with `FS_Handler`, starts the GTX input server, and then waits forever in `fsprobe_Wait`. Each probe callback recomputes window width, walks `fsprobe_Results` for each server, updates labels and highlight state, calls `mini_PrintDiskStats`, and redraws the frame.

## State and persistence behavior
State is process-local global UI and threshold state: `scout_screen`, `scout_frame`, `scout_frameDims`, column widths, debug flags, and attention thresholds. Persistent external effects are limited to opening a requested debug log and network probing of file servers. The disk list is maintained in memory across probe cycles so newly seen `/vicep*` partitions get light objects and existing lights can be reused.

## Dependencies and integration points
The file integrates OpenAFS GTX window/object/frame packages, `cmd` command parsing, `fsprobe` file-server statistics, `hostutil_GetHostByName`, and platform signal behavior. It relies on `ProbeViceStatistics` layout, `ViceDisk` names such as `/vicepa`, GTX light object private data, and curses-style window operations.

## Risks
The code is old C with many fixed-size buffers and `sprintf`/`strcpy` style operations; server names, banners, and threshold strings need bounded inputs. `scout_RemoveInactiveDisk` is effectively a stub, so inactive disk records are detected but not fully removed from display/list state. Width calculations can produce zero disk lights per line on very narrow terminals, risking poor layout behavior. Threshold parsing uses `atoi` without validation, and `%` disk threshold parsing mutates the command item string. Many globals make the command non-reentrant and difficult to unit test.

## Test signals
Useful tests include command parsing for required `-server`, basename expansion, debug-file failure, malformed threshold pairs, disk percent versus min-free modes, custom column widths including too many widths, resize handling in `FS_Handler`, probe failure blanking, first-seen and repeated disk partition updates, and integration runs against reachable and unreachable file servers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/scout/scout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/splint.cfg -->
# sources/distributed-fs/openafs/src/splint.cfg

## Purpose
`splint.cfg` configures lightweight static analysis for the OpenAFS source tree with Splint. It deliberately asks for weak checking and disables checks that are noisy for this codebase.

## Important APIs, types, and functions
There are no code APIs. The important settings are `-weak`, `-name-checks`, `+unix-lib`, `-D__signed__=signed`, `-fixed-formal-array`, and `+match-any-integral`.

## Control flow
The file is consumed by Splint when analysis is run. Options relax namespace and array-formal warnings, model standard Unix library behavior, and normalize the old Red Hat `__signed__` keyword issue.

## State and persistence behavior
No runtime state is created. Its persistent effect is on static-analysis diagnostics and therefore on developer gating.

## Dependencies and integration points
It depends on Splint option syntax and historical system headers. It integrates with any developer or CI target invoking Splint from `src`.

## Risks
`-weak` and `+match-any-integral` can hide meaningful type and integer-conversion issues. The config is intentionally permissive, so it should not be treated as a strong memory-safety proof.

## Test signals
Validation is a Splint invocation over representative OpenAFS files, confirming the config is accepted and suppresses intended legacy warnings without masking build-breaker parser errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/splint.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/Makefile.in -->
# sources/distributed-fs/openafs/src/sys/Makefile.in

## Purpose
`src/sys/Makefile.in` builds the OpenAFS user-space syscall shim libraries, RMTSYS RPC support, exported syscall headers, and small inode-operation test utilities.

## Important APIs, types, and functions
Key targets are `libsys.a`, `liboafs_sys.la`, `libafsrpc_sys.la`, `libsys_pic.la`, `rmtsysd`, `depinstall`, `install`, `dest`, `generated`, and `tests`. Generated artifacts come from `rmtsys.xg` through `RXGEN`: `rmtsys.cs.c`, `rmtsys.ss.c`, `rmtsys.xdr.c`, `rmtsys.h`, and kernel variants `Krmtsys.*`.

## Control flow
The default `all` target builds libraries, daemon, headers, export files, and generated install-tree copies. Platform-specific cases select AIX export handling, real assembly syscall stubs for SGI/AIX/HP-UX, or a touched empty `syscall.c` elsewhere. Test programs compile individual tools such as `iinc`, `idec`, `icreate`, `iopen`, `iread`, `iwrite`, `istat`, and `fixit` against `LIBS`.

## State and persistence behavior
The makefile writes generated RX files, libtool archives, static archives, export stubs, component version files, installed headers under `TOP_INCDIR`, libraries under `TOP_LIBDIR`, and install/dest tree content. `clean` removes generated code, libraries, test binaries, syscall placeholders, and export files.

## Dependencies and integration points
It includes `Makefile.config`, `Makefile.lwp`, and `Makefile.lwptool`, links RX/LWP/OPR/roken/hcrypto support, uses `RXGEN`, libtool rules, install macros, and AIX export lists. It provides `liboafs_sys` to many higher-level OpenAFS tools and servers.

## Risks
Platform case logic is easy to regress because syscall glue differs sharply by AIX, SGI, HP-UX, and generic Unix. A typo or ordering change can produce archives missing `syscall.o` or AIX export data. Generated RX files must be in sync with `rmtsys.xg`, and clean rules are broad enough to remove all generated outputs.

## Test signals
Test by running `make generated`, `make libsys.a`, `make liboafs_sys.la`, and platform-specific `depinstall`/`install` dry runs where possible. On legacy platforms, verify `syscall.lo` and export-file selection; on generic Unix, verify the placeholder syscall object is harmless.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/afssyscalls.c -->
# sources/distributed-fs/openafs/src/sys/afssyscalls.c

## Purpose
`afssyscalls.c` provides user-space wrappers around OpenAFS inode-related kernel calls and helper routines for reading, writing, and printing AFS vice inodes. It is compiled into the sys libraries used by server and utility code on non-namei configurations.

## Important APIs, types, and functions
Exported routines include `icreate`, `iopen`, `iinc`, `idec`, SGI XFS variants `icreatename64`, `iopen64`, `iinc64`, `idec64`, `ilistinode64`, optional `afs_init_kernel_config`, `inode_read`, `inode_write`, and `PrintInode`. Debug builds add `debug_icreatename64`, `debug_iopen64`, `debug_iinc64`, `debug_idec64`, and internal `check_iops`.

## Control flow
Platform conditionals select direct AFS syscall numbers on SGI, a shared `AFS_SYSCALL` entry with `AFSCALL_*` operation numbers elsewhere, or no code on AIX where system calls look like normal calls. Some calls pack parameters into `struct iparam` to fit syscall argument limits. `inode_read`/`inode_write` open an inode through `IOPEN`, seek, transfer bytes, close, and return the byte count or `-1`.

## State and persistence behavior
The wrappers mutate kernel AFS inode state through create/open/increment/decrement calls and ordinary file reads/writes after `IOPEN`. In debug builds, global arrays remember file/line call sites already logged to `inode_debug_log`.

## Dependencies and integration points
The file depends on `afs_args.h`, `afssyscalls.h`, platform syscall numbers, SGI XFS attribute support, and AFS inode macro selection. It underpins utilities in `src/sys`, salvager/fileserver inode code, and compatibility with legacy inode-based partition storage.

## Risks
The code is heavily controlled by platform macros; untested platform combinations can silently compile the wrong syscall path. Debug `realloc(*iops, ...)` is suspicious because `*iops` is an element, not the pointer variable, making debug-only allocation fragile. `inode_read` and `inode_write` compare `lseek` results against an unsigned offset via `int code`, which can be wrong for large offsets.

## Test signals
Build with and without `AFS_NAMEI_ENV`, with `AFS_64BIT_IOPS_ENV`, and for SGI XFS if supported. Runtime tests should exercise `ICREATE`, `IOPEN`, `IINC`, `IDEC`, `inode_read`, `inode_write`, and debug logging on a controlled vice partition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/afssyscalls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/afssyscalls.h -->
# sources/distributed-fs/openafs/src/sys/afssyscalls.h

## Purpose
`afssyscalls.h` declares the OpenAFS syscall shim API and defines the `Inode` type and convenience macros used by inode-based server utilities.

## Important APIs, types, and functions
It defines `Inode`, `afs_ino_str_t`, `AFS_INO_STR_LENGTH`, `VALID_INO`, `AFS_DEBUG_IOPS_LOG`, and macros `ICREATE`, `IDEC`, `IINC`, and `IOPEN`. It declares SGI XFS 64-bit inode operations, `inode_read`, `inode_write`, `PrintInode`, optional `proc_afs_syscall`, `afs_init_kernel_config`, and local syscall wrappers `lsetpag`/`lpioctl`.

## Control flow
There is no runtime control flow, but preprocessor flow selects inode width and macro targets based on `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_SGI_XFS_IOPS_ENV`, and `AFS_DEBUG_IOPS`.

## State and persistence behavior
The header exposes debug log state via `inode_debug_log` in debug builds. Otherwise it defines only compile-time interfaces to kernel-backed inode state.

## Dependencies and integration points
It includes `afs/param.h` and is consumed by syscall wrappers, server inode code, and test utilities. AIX also gets a broad `int syscall()` declaration because OpenAFS exports a syscall-like function with variable arguments.

## Risks
Macro indirection hides whether callers are invoking 32-bit, 64-bit, debug, or SGI XFS paths. The non-64-bit declarations for `inode_read`/`inode_write` are old-style and lose type checking. AIX's generic `syscall()` prototype is intentionally imprecise.

## Test signals
Compile representative consumers under strict warnings for namei/non-namei, 32-bit/64-bit inode, debug IOPS, SGI XFS, Linux, and AIX configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/afssyscalls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/fixit.c -->
# sources/distributed-fs/openafs/src/sys/fixit.c

## Purpose
`fixit.c` is a root-only repair utility for legacy inode vice partitions. It increments reference counts for `#<inode>` files moved into `lost+found` by a non-AFS fsck so those inodes are not freed before the AFS fsck can reconcile them.

## Important APIs, types, and functions
The only routine is K&R-style `main`. It uses `stat`, `opendir`, `readdir`, `geteuid`, `atoi`, and OpenAFS `IINC`.

## Control flow
The command verifies effective UID 0, stats the supplied directory to get the device number, opens that directory, parses the volume id from `argv[2]`, and iterates directory entries. Every entry whose name starts with `#` is passed to `IINC(dev, d_ino, volid)`; failures are printed but do not abort the scan.

## State and persistence behavior
The utility mutates kernel/filesystem inode reference counts. It does not write files itself but is intended to be run before unmounting and running AFS-aware fsck.

## Dependencies and integration points
It depends on inode-based OpenAFS partitions, `afssyscalls.h`, kernel IOPS support, and the operational salvage/fsck procedure documented in the file header.

## Risks
There is no argc validation before using `argv[1]` and `argv[2]`. It assumes `d_ino` is the target inode and that all `#` entries under the supplied directory belong to the supplied volume. Running it against the wrong partition or volume id can corrupt reference counts.

## Test signals
Only test on disposable inode partitions. Check root enforcement, missing arguments, unreadable lost+found, entries with and without `#`, and expected `IINC` failures for unrelated volume ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/fixit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/glue.c -->
# sources/distributed-fs/openafs/src/sys/glue.c

## Purpose
`glue.c` supplies C-level platform glue for invoking OpenAFS kernel syscalls through proc/ioctl mechanisms when a direct syscall stub is not sufficient.

## Important APIs, types, and functions
Platform exports are `proc_afs_syscall` for Linux, `ioctl_afs_syscall` for Darwin 8+ with optional 64-bit Darwin handling, and `ioctl_sun_afs_syscall` for Solaris 11. Each accepts an OpenAFS syscall opcode, up to six parameters where supported, and returns an ioctl/syscall result separately from the kernel-returned error.

## Control flow
Linux opens `/proc` syscall files, fills `struct afsprocdata`, and issues `VIOC_SYSCALL`. Darwin opens `SYSCALL_DEV_FNAME`, selects `VIOC_SYSCALL` or `VIOC_SYSCALL64`, performs ioctl, and extracts the returned value. Solaris chooses a 32-bit or native argument struct, opens `SYSCALL_DEV_FNAME`, and issues the appropriate ioctl.

## State and persistence behavior
No durable state is stored. The functions open device/proc files, call into the loaded AFS kernel module, and close the descriptors.

## Dependencies and integration points
It depends on `afs_args.h`, `sys_prototypes.h`, syscall device path macros, and platform kernel-module ioctl ABIs. `setpag.c` and `pioctl.c` call these functions as fallback or primary local syscall transport.

## Risks
ABI struct mismatches break all local pioctl/setpag operations for a platform. Linux fallback behavior depends on both OpenAFS and Arla proc names. Darwin's pointer-size branch is compile/runtime sensitive, and Solaris must match ILP32/native ioctl numbers.

## Test signals
Exercise `lsetpag` and `lpioctl` on Linux with proc syscall available and absent, Darwin 32/64-bit builds, and Solaris ILP32/native builds. Verify file descriptors close on both success and failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/glue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/icreate.c -->
# sources/distributed-fs/openafs/src/sys/icreate.c

## Purpose
`icreate.c` is a small diagnostic test program for the legacy `icreate` inode syscall.

## Important APIs, types, and functions
The K&R-style `main` parses vnode, uniquifier, and data-version values, stats `/vicepa`, calls `icreate(status.st_dev, 0, 17, vnode, unique, datav)`, and prints the returned inode.

## Control flow
It stats a hard-coded vice partition, converts three arguments with `atoi`, invokes the syscall wrapper, reports errors with `perror`, and exits success or failure.

## State and persistence behavior
Successful execution creates a vice inode on the `/vicepa` device, altering filesystem/kernel inode state.

## Dependencies and integration points
It depends on non-namei inode support and the syscall wrappers built by `src/sys/Makefile.in`.

## Risks
No argument count validation appears before `argv[1..3]`, `/vicepa` is hard-coded, and magic parameter `17` is unexplained in the tool. It is unsafe outside disposable legacy test partitions.

## Test signals
Run only in a controlled legacy inode test environment. Validate missing args, absent `/vicepa`, and successful creation followed by inspection with `iopen`/`istat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/icreate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/idec.c -->
# sources/distributed-fs/openafs/src/sys/idec.c

## Purpose
`idec.c` is a diagnostic command that decrements a vice inode reference count on a specified partition.

## Important APIs, types, and functions
The only routine is K&R-style `main`, using `stat`, `atoi`, and the `IDEC` macro from `afssyscalls.h`.

## Control flow
The command checks for at least two positional arguments, stats the partition path to obtain `st_dev`, prints the operation, calls `IDEC(st_dev, inode, 17)`, reports failure, and exits.

## State and persistence behavior
It mutates kernel/filesystem inode reference state and can make an inode eligible for deletion.

## Dependencies and integration points
It requires legacy inode IOPS support through `libsys.a` and is built as a `tests` target from `src/sys/Makefile.in`.

## Risks
The volume/id parameter is hard-coded to `17`, the error message says `iopen` on `IDEC` failure, and misuse can destroy data on a vice partition.

## Test signals
Use only disposable vice partitions; test missing args, invalid partition, invalid inode, and decrement behavior paired with `iinc`/`istat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/idec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iinc.c -->
# sources/distributed-fs/openafs/src/sys/iinc.c

## Purpose
`iinc.c` is a diagnostic command that increments a vice inode reference count on a specified partition.

## Important APIs, types, and functions
The K&R-style `main` uses `stat`, `atoi`, and the `IINC` macro from `afssyscalls.h`.

## Control flow
It validates two positional arguments, stats the partition, prints device/inode details, calls `IINC(st_dev, inode, 17)`, reports failure, and exits.

## State and persistence behavior
Successful execution increments kernel/filesystem inode reference state for the selected vice inode.

## Dependencies and integration points
It is one of the sys test utilities and depends on the same legacy inode syscall path as fileserver salvage tooling.

## Risks
The volume/id parameter is hard-coded to `17`, the failure label says `iopen`, and arbitrary increments can leak or misassociate inodes.

## Test signals
Use with disposable test inodes; pair with `idec` and `istat` to verify link/reference changes and error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iinc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iopen.c -->
# sources/distributed-fs/openafs/src/sys/iopen.c

## Purpose
`iopen.c` is a diagnostic utility that opens a vice inode by number and dumps its contents to stdout.

## Important APIs, types, and functions
It defines `Usage` and K&R-style `main`. Important APIs are `stat`, `strtoull` or `atoi` depending on `AFS_64BIT_IOPS_ENV`, `PrintInode`, `IOPEN`, `read`, and `write`.

## Control flow
The command requires `<partition> <inode>`, obtains the partition device, parses the inode with the correct width, prints the planned open, calls `IOPEN(dev, ino, O_RDONLY)`, then reads five-byte chunks and writes them to stdout until EOF.

## State and persistence behavior
It opens and reads kernel inode state but does not intentionally modify data.

## Dependencies and integration points
It depends on `afssyscalls.h`, inode width macros, and the syscall wrappers in `libsys.a`.

## Risks
Output is raw file content, so binary data may corrupt terminal output. `printf("ino=%" AFS_INT64_FMT)` can be mismatched when `Inode` is not 64-bit. Direct inode reads bypass normal file authorization and should be restricted to repair/test contexts.

## Test signals
Verify behavior for 32-bit and 64-bit inode builds, invalid inode strings, missing partition, unreadable inode, and known small test files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iopen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iread.c -->
# sources/distributed-fs/openafs/src/sys/iread.c

## Purpose
`iread.c` is a legacy diagnostic program that reads bytes from an inode on hard-coded `/vicepa` using the old `xiread` interface.

## Important APIs, types, and functions
The only routine is K&R-style `main`, calling `stat`, `xiread`, `atoi`, and printing the returned buffer.

## Control flow
It stats `/vicepa`, expects three arguments after decrementing `argc`, calls `xiread(dev, inode, 17, offset, buf, count)`, then prints the count and data.

## State and persistence behavior
It reads vice inode contents without modifying persistent state.

## Dependencies and integration points
It depends on legacy exported `xiread` syscall symbols and the `/vicepa` test partition convention.

## Risks
The fixed 50,000-byte buffer is not bounds-checked against the requested count. `/vicepa` and parameter `17` are hard-coded. It prints data as a C string even if the read data is not NUL-terminated.

## Test signals
Run on disposable legacy builds with small read sizes, invalid offsets/counts, missing `/vicepa`, and binary payloads to verify output safety.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/istat.c -->
# sources/distributed-fs/openafs/src/sys/istat.c

## Purpose
`istat.c` opens a vice inode and reports link count and size through `fstat`.

## Important APIs, types, and functions
The K&R-style `main` uses `stat`, `xiopen`, `fstat`, and `printf`.

## Control flow
It stats the partition path in `argv[1]`, parses `argv[2]` as an inode, opens it read-only with `xiopen`, calls `fstat` on the returned descriptor, and prints `st_nlink` and `st_size`.

## State and persistence behavior
It reads inode metadata and does not intentionally modify state.

## Dependencies and integration points
It depends on legacy `xiopen` symbols and is built as part of sys test utilities.

## Risks
No argc validation before dereferencing arguments. Uses `int` for inode and prints sizes with `%d`, which can truncate on modern platforms.

## Test signals
Check missing args, invalid partition, invalid inode, large files, and comparison with `iopen`/filesystem metadata on controlled partitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/istat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iwrite.c -->
# sources/distributed-fs/openafs/src/sys/iwrite.c

## Purpose
`iwrite.c` is a legacy diagnostic program that writes a string into an inode on hard-coded `/vicepa` through the old `xiwrite` interface.

## Important APIs, types, and functions
The only routine is K&R-style `main`, using `stat`, `xiwrite`, and `atoi`.

## Control flow
It stats `/vicepa`, expects inode, offset, string, and count arguments, invokes `xiwrite(dev, inode, 17, offset, argv[3], count)`, then prints the byte count.

## State and persistence behavior
Successful execution modifies vice inode contents.

## Dependencies and integration points
It depends on legacy syscall exports, `/vicepa`, and sys test build linkage.

## Risks
It can corrupt data, has no argc check before hard-coded positional use beyond the decremented count test, hard-codes parameter `17`, and can request more bytes than the supplied string contains.

## Test signals
Use only disposable inodes; verify short writes, out-of-range offsets, oversized counts, missing `/vicepa`, and read-back through `iread`/`iopen`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/iwrite.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl.c -->
# sources/distributed-fs/openafs/src/sys/pioctl.c

## Purpose
`pioctl.c` implements `lpioctl`, the local pioctl syscall wrapper. Remote dispatch is handled elsewhere by `rmtsysc.c`; this file exists separately so small shared libraries can include only the local pioctl entry point.

## Important APIs, types, and functions
The exported function is `lpioctl(char *path, int cmd, void *cmarg, int follow)`. Platform-specific paths use direct `syscall(AFS_PIOCTL)` on SGI, Linux `proc_afs_syscall` with fallback to `AFS_SYSCALL`, Darwin `ioctl_afs_syscall`, Solaris `ioctl_sun_afs_syscall`, or generic `syscall(AFS_SYSCALL, AFSCALL_PIOCTL, ...)`.

## Control flow
The Linux path first attempts `/proc` ioctl glue and falls back to the AFS syscall number if available. The generic path ignores `SIGSYS` around the syscall so missing kernel support does not kill the process, restoring the handler afterward. Darwin/Solaris keep ioctl return status and kernel error status distinct.

## State and persistence behavior
The wrapper itself stores no state but forwards pioctl requests that may read or mutate cache-manager state, tokens, mountpoints, ACLs, cells, or cache configuration.

## Dependencies and integration points
It depends on `afs_args.h`, `afssyscalls.h`, `sys_prototypes.h`, and platform glue in `glue.c`. User tools such as `fs`, token utilities, and RMTSYS server code depend on this local entry point.

## Risks
Signal-handler manipulation is process-global and not thread-safe. Platform return conventions differ, so error precedence can regress. `void *cmarg` must match `struct ViceIoctl` expectations for the kernel opcode.

## Test signals
Exercise representative pioctls through `lpioctl` on Linux proc and syscall fallback, Darwin, Solaris, SGI, and a system without loaded AFS support to confirm graceful errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl_nt.c -->
# sources/distributed-fs/openafs/src/sys/pioctl_nt.c

## Purpose
`pioctl_nt.c` implements Windows `pioctl` and `pioctl_utf8` by translating Unix-style ViceIoctl calls into SMB redirector or AFS redirector ioctl file transactions. It locates an AFS ioctl path, marshals opcode/path/input data, sends it to the cache manager, and copies output data back to the caller.

## Important APIs, types, and functions
Important helpers include `CMtoUNIXerror`, `InitFSRequest`, `IoctlDebug`, `RDR_Ready`, `DisableServiceManagerCheck`, `GetServiceStatus`, `UnicodeToANSI`, `GetLSAPrincipalName`, `DriveSubstitution`, `DriveIsMappedToAFS`, `DriveIsGlobalAutoMapped`, `GetIoctlHandle`, `Transceive`, `MarshallLong`, `UnmarshallLong`, `MarshallString`, `fs_GetFullPath`, `pioctl_int`, `pioctl_utf8`, and `pioctl`.

## Control flow
`pioctl`/`pioctl_utf8` delegate to `pioctl_int`. For mountpoint and symlink creation in Freelance root paths, `pioctl_int` may rewrite UNC paths through `\afs\all`. It obtains an ioctl handle with `GetIoctlHandle`, marshals opcode, normalized full path, optional UTF-8 marker, and input bytes into an `fs_ioctlRequest_t`, calls `Transceive`, unmarshals the cache-manager return code, maps CM errors to errno, and copies output bytes. `GetIoctlHandle` verifies service/redirector readiness, resolves NetBIOS name, drive mappings, SUBST drives, UNC paths, global automaps, and may establish SMB connections with Explorer, LSA Kerberos, or SAM-compatible usernames before opening the hidden ioctl file.

## State and persistence behavior
The file reads Windows registry settings under OpenAFS client keys, service status, drive mappings, current directory, LSA Kerberos ticket cache, and network resources. It can establish SMB connections with `WNetAddConnection2`. Its primary persistent effect is cache-manager pioctl state mutation based on opcode.

## Dependencies and integration points
It integrates with Windows Win32 APIs, Service Control Manager, registry, LSA/Kerberos package APIs, Network Provider APIs, OpenAFS redirector structures and ioctl numbers, SMB ioctl filenames, lana helper code, and cache-manager error definitions.

## Risks
The code contains many fixed-size `char` buffers and unbounded `sprintf`/`strcat` paths; long UNC paths, NetBIOS names, or current directories can overflow or truncate. `fs_GetFullPath` temporarily changes process current directory, which is process-global and unsafe for multithreaded callers. Authentication retry logic is complex and may leak environment-specific behavior. `follow` is accepted but not visibly marshalled. Error mapping is lossy and uses several hack errno values.

## Test signals
Test local drive mappings, UNC `\afs\all`, Freelance root mountpoint/symlink creation, SUBST drives, global automaps, redirector-ready and SMB fallback modes, disabled service-manager checks, registry debug toggles, UTF-8 paths, long paths, sharing-violation retry, and CM error-to-errno mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl_nt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl_nt.h -->
# sources/distributed-fs/openafs/src/sys/pioctl_nt.h

## Purpose
`pioctl_nt.h` declares the Windows pioctl interface and the Windows-local `ViceIoctl` block shape.

## Important APIs, types, and functions
It defines `struct ViceIoctl`/`viceIoctl_t` with `in_size`, `out_size`, `in`, and `out` fields, includes NT errno mappings, and declares `pioctl` and `pioctl_utf8`.

## Control flow
There is no runtime control flow; this header supplies the ABI used by Windows callers and `pioctl_nt.c`.

## State and persistence behavior
No state is stored here. The structure describes caller-owned in/out buffers passed to cache-manager pioctls.

## Dependencies and integration points
It depends on `afs_int32` definitions from surrounding OpenAFS headers and `afs/errmap_nt.h`. Windows tools include it to call the pioctl implementation.

## Risks
The use of `long` for sizes ties ABI assumptions to Windows compiler data models. Callers must keep buffers alive and correctly sized.

## Test signals
Compile all Windows pioctl consumers and run ANSI/UTF-8 pioctl calls with zero, input-only, output-only, and bidirectional buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/pioctl_nt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysc.c -->
# sources/distributed-fs/openafs/src/sys/rmtsysc.c

## Purpose
`rmtsysc.c` is the client-side RMTSYS implementation. It lets user programs call `setpag` and `pioctl` against a remote AFS client host over RX, falling back to local syscalls when no remote host is configured/reachable.

## Important APIs, types, and functions
Exports include `setpag`, `pioctl`, `GetAfsServerAddr`, `rx_connection`, `afs_get_pag_from_groups`, and `afs_get_groups_from_pag`. Internal `SetClientCreds` captures uid and group state. Global state caches `afs_server`, `server_name`, `hostAddr`, and `hostAddrLookup`.

## Control flow
`GetAfsServerAddr` resolves the remote client from `AFSSERVER`, `$HOME/.AFSSERVER`, or `/.AFSSERVER` and caches the host address. `rx_connection` initializes RX and opens a null-security connection to `AFSCONF_RMTSYSPORT`. `setpag` tries the remote `RMTSYS_SetPag`, converts the returned PAG into two group slots, shifts existing groups if necessary, calls `setgroups`, and resets effective uid; if remote setup fails, it calls `lsetpag`. `pioctl` marshals input data, converts opcode-specific input to network order, expands relative paths, calls `RMTSYS_Pioctl`, converts output back to host order, and falls back to `lpioctl` when no remote connection is available.

## State and persistence behavior
It reads environment and `.AFSSERVER` files, caches remote host lookup, creates RX connections, mutates process groups/PAG via `setgroups`, and forwards pioctls that can mutate cache-manager state on the remote AFS client.

## Dependencies and integration points
It depends on RX, `rmtsys` generated stubs, pioctl conversion routines from `rmtsysnet.c`, local syscall wrappers, group/PAG encoding conventions, and Unix privilege behavior for `setgroups`.

## Risks
Remote calls use RX null security and trust client-supplied credentials encoded in the request. Path buffers are fixed at 256 bytes with `strcpy`/`strcat`. `rx_Init(0)` is called per connection path and global RX lifecycle is not managed here. `setpag` requires setuid-root behavior and can fail or alter group ordering unexpectedly.

## Test signals
Test `AFSSERVER`/home/root fallback resolution, DNS failure, local fallback, remote setpag group insertion when a PAG exists or not, `NGROUPS_MAX` overflow, relative and absolute remote pioctl paths, opcode conversion round trips, and remote errno propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysd.c -->
# sources/distributed-fs/openafs/src/sys/rmtsysd.c

## Purpose
`rmtsysd.c` is the standalone daemon main for the RMTSYS service, which exposes remote `setpag` and `pioctl` over RX for AFS client hosts.

## Important APIs, types, and functions
The only routine is `main`. It uses `rx_Init`, `rxnull_NewServerSecurityObject`, `rx_NewService`, `rx_SetMaxProcs`, `rx_StartServer`, and generated `RMTSYS_ExecuteRequest`.

## Control flow
On AIX it enables full core dumps for abort/segv. It initializes RX on `AFSCONF_RMTSYSPORT`, creates a null-security RX service with `RMTSYS_SERVICEID` and `AFSCONF_RMTSYSSERVICE`, limits server procs to two, and donates the process to the RX server loop.

## State and persistence behavior
The daemon opens a listening RX endpoint and runs indefinitely. It does not persist data directly; server request handlers mutate local cache-manager/PAG state.

## Dependencies and integration points
It depends on RX, generated RMTSYS RPC code, `rmtsyss.c` request handlers, and afsd or service management that starts the daemon.

## Risks
Only null security is configured, so exposure must be controlled by deployment assumptions. Startup failure paths call `rmt_Quit` and exit. The fixed max-procs value may limit throughput or hide concurrency bugs.

## Test signals
Start the daemon on an isolated port/client, verify RX service registration, remote `pioctl` and `setpag` calls, startup failure when port is in use, and AIX signal setup in platform builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysnet.c -->
# sources/distributed-fs/openafs/src/sys/rmtsysnet.c

## Purpose
`rmtsysnet.c` converts selected pioctl input and output buffers between host byte order and network byte order for RMTSYS RPC transport.

## Important APIs, types, and functions
It defines local `struct Acl`, `struct AclEntry`, and `struct ClearToken`. Exported helpers are `RSkipLine`, `RParseAcl`, `RAclToString`, `RCleanAcl`, `RFetchVolumeStatus_conversion`, `RClearToken_convert`, `inparam_conversion`, and `outparam_conversion`.

## Control flow
ACL conversion parses textual ACLs into linked lists, writes them back, and frees temporary entries. Token conversions walk length-prefixed secret-ticket and clear-token regions and convert embedded integer fields. Volume-status conversion swaps fields in `AFSFetchVolumeStatus`. The in/out conversion switches inspect `cmd & 0xffff` and convert only older pioctls that were not already network-order clean.

## State and persistence behavior
No durable state is stored. It mutates the caller-provided buffer in place before or after an RX call.

## Dependencies and integration points
It depends on pioctl opcode definitions from `venus.h`, AFS volume/token structures, XDR/RX integer conventions, and is called by `rmtsysc.c` and `rmtsyss.c`.

## Risks
Parsing and serialization use fixed buffers, `sscanf`, `sprintf`, and `strcat` into pioctl-sized buffers, so malformed or oversized ACLs can overflow or truncate. Token conversion trusts embedded lengths and can walk outside the buffer if the caller supplies malformed data. New pioctls default to no conversion, which is correct only if their wire format is already network order.

## Test signals
Round-trip ACL, token, volume-status, cache-params, and scalar pioctl buffers through host-to-network and network-to-host conversion. Include malformed ACL counts, long names, bad token lengths, and unknown opcode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsysnet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsyss.c -->
# sources/distributed-fs/openafs/src/sys/rmtsyss.c

## Purpose
`rmtsyss.c` implements the server-side RMTSYS RPC handlers used by `rmtsysd` or afsd-started RMTSYS service to perform local `setpag` and `pioctl` on behalf of remote clients.

## Important APIs, types, and functions
Exports include `rmtsysd`, `SRMTSYS_SetPag`, `SRMTSYS_Pioctl`, and `rmt_Quit`. Important macros are `SETCLIENTCONTEXT`, `PIOCTL_HEADER`, `PSETPAG`, `PSetClientContext`, and `NFS_EXPORTER`.

## Control flow
`rmtsysd` starts the RX service with null security. `SRMTSYS_SetPag` builds a context blob from RX peer host and supplied uid/groups, calls local `lpioctl` with `_VICEIOCTL(PSetClientContext)`, and interprets `errno == PSETPAG` as a returned PAG. `SRMTSYS_Pioctl` prepends the same context blob to converted input data, maps `NIL_PATHP` to a null local path, calls local `lpioctl`, converts output to network order on success, and returns pioctl errno through an out parameter while keeping the RPC return value zero.

## State and persistence behavior
Handlers do not persist their own state, but they forward requests that mutate local AFS cache-manager state and PAG/token context. Allocated pioctl input buffers are freed per request.

## Dependencies and integration points
It depends on RX call peer inspection, generated RMTSYS server stubs, local `lpioctl`, pioctl conversion routines, and kernel support for `PSetClientContext`.

## Risks
The service uses null security and trusts client-provided credential fields. Input length plus header allocation must fit memory and local pioctl expectations. Returning zero for pioctl failures is protocol-dependent and easy for callers to mishandle.

## Test signals
Test remote setpag success/failure, returned PAG extraction, NIL and non-NIL paths, pioctl errno propagation, conversion of token/ACL/status pioctls, allocation failure, and concurrent RX requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/rmtsyss.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/setpag.c -->
# sources/distributed-fs/openafs/src/sys/setpag.c

## Purpose
`setpag.c` implements `lsetpag`, the local setpag syscall wrapper. The higher-level `setpag` symbol is provided by RMTSYS client logic so it can choose remote or local behavior.

## Important APIs, types, and functions
The exported function is `lsetpag(void)`. Platform implementations call SGI `syscall(AFS_SETPAG)`, Linux `proc_afs_syscall` with fallback to `AFS_SYSCALL`, Darwin/Solaris ioctl glue, or generic `syscall(AFS_SYSCALL, AFSCALL_SETPAG)`.

## Control flow
Conditional compilation selects the local syscall transport. Linux uses proc glue first, then syscall fallback. Darwin and Solaris keep ioctl transport return separate from kernel error value. AIX has no body in the non-AIX block because its calls are linker-exported differently.

## State and persistence behavior
The wrapper itself stores no state. Successful calls create or change the caller's PAG/token namespace in the kernel/cache manager.

## Dependencies and integration points
It depends on `afs_args.h`, platform syscall definitions, `glue.c`, and `afssyscalls.h`. Authentication tools call this through local or RMTSYS paths.

## Risks
Behavior is platform-specific and depends on loaded kernel support. Missing syscall numbers return `-1` without detailed mapping in some builds. PAG creation affects process credential behavior and can interact with setuid flows.

## Test signals
Exercise `lsetpag` on each supported local transport, with and without the AFS kernel module loaded, and verify token isolation after PAG creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/setpag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/sys_prototypes.h -->
# sources/distributed-fs/openafs/src/sys/sys_prototypes.h

## Purpose
`sys_prototypes.h` centralizes prototypes for syscall glue, local pioctl/setpag wrappers, RMTSYS client/server functions, and conversion helpers in `src/sys`.

## Important APIs, types, and functions
It declares platform glue (`proc_afs_syscall`, `ioctl_afs_syscall`, `ioctl_sun_afs_syscall`), `lpioctl`, RMTSYS client `pioctl`/`setpag`, conversion functions `inparam_conversion`/`outparam_conversion`, server helpers `rmt_Quit`/`rmtsysd`, and `lsetpag`.

## Control flow
There is no runtime control flow. Preprocessor conditionals expose only platform-relevant glue prototypes.

## State and persistence behavior
No state is stored here; it defines cross-file interfaces for stateful syscall/RPC operations.

## Dependencies and integration points
It depends on OpenAFS integer types and `struct ViceIoctl`. It ties together `glue.c`, `pioctl.c`, `rmtsysc.c`, `rmtsysnet.c`, `rmtsyss.c`, and `setpag.c`.

## Risks
Prototype drift from implementation signatures can cause subtle ABI bugs, especially for pointer-sized Solaris/Darwin parameters. Broad declarations of `setpag`/`pioctl` can collide with platform/library names.

## Test signals
Compile `src/sys` with strict prototype warnings on Linux, Darwin, Solaris, and generic Unix configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/sys_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/syscall.s -->
# sources/distributed-fs/openafs/src/sys/syscall.s

## Purpose
`syscall.s` provides platform assembly syscall stubs or placeholders for legacy OpenAFS syscall entry points.

## Important APIs, types, and functions
It contains an AIX dummy csect placeholder, an HP PA-RISC `dummysysc` entry, an SGI/MIPS `afs_syscall` leaf routine, and a Linux ELF `.note.GNU-stack` marker.

## Control flow
On SGI, `afs_syscall` loads `AFS_SYSCALL`, executes the kernel syscall instruction, branches to `_cerror` on error, and returns on success. Other platform sections are placeholders or ABI-specific dummy entries selected by macros.

## State and persistence behavior
No persistent state is stored. Executed stubs cross into kernel syscall handling.

## Dependencies and integration points
It includes `afs/param.h` with `IGNORE_STDS_H`, uses assembler macros/register headers on SGI, and is built by `src/sys/Makefile.in` into `syscall.o` on selected platforms.

## Risks
Assembly is highly ABI-specific. Wrong preprocessing or assembler invocation can produce unusable syscall stubs, while missing `.note.GNU-stack` can affect executable stack metadata on Linux.

## Test signals
Build `syscall.lo` for SGI, AIX, HP-UX, and generic Linux. On SGI, run a simple `lpioctl` or inode syscall through `afs_syscall` and verify errno behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/syscall.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/xfsattrs.h -->
# sources/distributed-fs/openafs/src/sys/xfsattrs.h

## Purpose
`xfsattrs.h` defines SGI XFS extended-attribute structures used to represent OpenAFS vice inodes and directory markers under `AFS_SGI_XFS_IOPS_ENV`.

## Important APIs, types, and functions
Important definitions include `afs_inode_params_t`, `AFS_XFS_ATTR`, `AFS_XFS_ATTR_VERS`, name-version constants, `AFS_INODE_DIR_NAME`, `afs_xfs_attr_t`, `SIZEOF_XFS_ATTR_T`, link/magic helpers, `AFS_XFS_DATTR`, `afs_xfs_dattr_t`, `vice_inode_info_t`, and `i_list_inode_t`.

## Control flow
There is no runtime control flow. Conditional compilation exposes the definitions only for SGI XFS IOPS builds.

## State and persistence behavior
The structures describe persistent XFS inode attributes: volume/vnode/uniquifier/data-version parameters, parent inode, name scheme version, link count encoded in mode bits, clipped volume ids, directory attributes, and list-inode records.

## Dependencies and integration points
It depends on `<sys/attributes.h>` and must match kernel XFS attribute handling, salvager `ViceInodeInfo`, and utilities such as ListViceInodes and XFS inode repair code.

## Risks
Packed size assumptions are critical; comments note XFS attribute size constraints and `SIZEOF_XFS_ATTR_T` intentionally differs from `sizeof`. Any field layout change can make existing vice inodes unreadable. Kernel/user `ino_t` width differences are handled by conditional fields.

## Test signals
Build SGI XFS IOPS paths, create/list/fix vice inodes, verify attribute sizes and offsets, and run salvager/ListViceInodes compatibility checks for both name-version schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/sys/xfsattrs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbozo/Makefile.in -->
# sources/distributed-fs/openafs/src/tbozo/Makefile.in

## Purpose
`src/tbozo/Makefile.in` builds pthread/libtool variants of bosserver, `bos`, `bos_util`, and the BOS RPC support by reusing sources from `src/bozo`.

## Important APIs, types, and functions
Key targets are `all`, `generated`, `liboafs_bos.la`, `bosserver`, `bos`, `bos_util`, `install`, `dest`, and `clean`. Generated files include `bosint.cs.c`, `bosint.ss.c`, `bosint.xdr.c`, `bosint.h`, `bnode.h`, and `boserr.c`.

## Control flow
The makefile includes pthread and libtool config, runs `RXGEN` and `COMPILE_ET`, compiles selected `../bozo` C sources with `AFS_CCRULE`, links command/server binaries against auth, kauth, volser, rx, rxkad, rxstat, cmd, util, opr, LWP compatibility, sys, and process-management libraries, and installs only when `ENABLE_PTHREADED_BOS` is yes.

## State and persistence behavior
It writes generated RPC/error headers and C files, libtool objects, binaries, libraries, and install-tree files. `clean` removes generated BOS interface files and built products.

## Dependencies and integration points
It depends on the canonical bozo sources and `.xg`/`.et` files, top include/lib directories, pthread config, libtool, RXGEN, and compile_et. Outputs are part of the BOS administration/server toolchain.

## Risks
This shadow makefile must stay synchronized with `src/bozo` source lists and headers. Conditional install means builds can succeed without packaging pthreaded BOS if the configure flag is off. Library ordering is nontrivial.

## Test signals
Run `make generated`, build `bosserver`, `bos`, and `bos_util`, verify generated headers match `src/bozo`, and test install/dest with `ENABLE_PTHREADED_BOS` enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbozo/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbudb/Makefile.in -->
# sources/distributed-fs/openafs/src/tbudb/Makefile.in

## Purpose
`src/tbudb/Makefile.in` builds the pthread/libtool backup database server (`budb_server` installed as `buserver`) and associated `libbudb.a` artifacts from sources in `src/budb`.

## Important APIs, types, and functions
Key targets are `all`, `budb_server`, `libbudb.a`, generated `budb_errs.[ch]`, `budb.cs.c`, `budb.ss.c`, `budb.xdr.c`, and `budb.h`, plus `install`, `dest`, and `clean`.

## Control flow
The makefile generates error and RX files from `budb_errs.et` and `budb.rg`, compiles common database objects and server objects from `../budb`, links `budb_server` against bubasics, ubik, sys, rxkad, LWP compatibility, cmd, opr, and util libraries, and installs only when `ENABLE_PTHREADED_UBIK` is yes.

## State and persistence behavior
It creates generated RPC/error files, object files, static archives, the `budb_server` binary, installed headers, and install/dest server binaries. `clean` removes generated files and products.

## Dependencies and integration points
It integrates backup database sources, UBIK, RX/RXKAD, OpenAFS command/util libraries, compile_et, RXGEN, and top-level configured install paths.

## Risks
The makefile contains a likely typo `${LT_INSTALl_PROGRAM}` with a lowercase `l`, which can break install. It must stay synchronized with budb source dependencies and generated headers. Conditional install can hide packaging issues in normal builds.

## Test signals
Run generation, build `libbudb.a` and `budb_server`, exercise `make install` with `ENABLE_PTHREADED_UBIK=yes`, and verify generated headers are consumed by all listed objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbudb/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbutc/Makefile.in -->
# sources/distributed-fs/openafs/src/tbutc/Makefile.in

## Purpose
`src/tbutc/Makefile.in` builds the pthread backup tape coordinator `butc` and the local `libbutm.a` media library from butc, butm, bucoord, and volser sources.

## Important APIs, types, and functions
Key targets are `all`, `butc`, `libbutm.a`, object rules for butc modules (`tcmain`, `tcprocs`, `dump`, `lwps`, `dbentries`, `recoverDb`, `tcstatus`, XBSA support), bucoord helpers, volser helpers, `install`, `dest`, and `clean`.

## Control flow
The makefile compiles selected source files from sibling directories with `AFS_CCRULE`, applies `CFLAGS_NOERROR` to `tcudbprocs.o`, archives `libbutm.a`, and links `butc` against budb, bubasics, butm, kauth, volser, vldb, ubik, rxkad, cmd, util, opr, usd, LWP compatibility, sys, and process-management libraries.

## State and persistence behavior
It writes object files, `libbutm.a`, `butc`, component version output, and install/dest copies under configured server binary locations. `clean` removes build outputs.

## Dependencies and integration points
It integrates the backup tape coordinator with backup database, volume server, ubik, rxkad, USD, XBSA flags, and configured top include/lib directories.

## Risks
Cross-directory source ownership makes dependency drift easy. Library ordering and optional XBSA flags can break only in specific configurations. Suppressing errors for `tcudbprocs.o` may hide warnings that should be fixed.

## Test signals
Build with and without XBSA flags, run `make butc`, verify `libbutm.a`, and test install/dest paths. Functional signals include backup dump/restore smoke tests against a test cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tbutc/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/Makefile.in -->
# sources/distributed-fs/openafs/src/tests/Makefile.in

## Purpose
`src/tests/Makefile.in` builds the OpenAFS regression test programs and generates runtime path configuration modules/scripts used by the test harness.

## Important APIs, types, and functions
Important targets are `all`, `check`, `check-fast`, `run-tests`, every `TEST_PROGRAMS` binary, `OpenAFS/Dirpath.pm`, `OpenAFS/Dirpath.sh`, `hello-world`, `mountpoint`, `clean`, and `TAGS`. Library groups include `SYS_LIBS`, `AUTH_LIBS`, `INT_LIBS`, and `COMMON_LIBS`.

## Control flow
The default target creates `run-tests`, generated OpenAFS path modules, and many filesystem behavior test binaries. Individual rules link test objects with common err/warn compatibility objects and the appropriate OpenAFS libraries. `OpenAFS/Dirpath.pm` and `.sh` are generated at make time from autoconf variables and distinguish Transarc versus modern paths. `check` and `check-fast` run `./run-tests`.

## State and persistence behavior
It creates executable tests, generated Perl/shell configuration files, and transient objects. Tests themselves may create files, directories, mountpoints, tokens, and cache state when run. `clean` removes generated test artifacts and binaries.

## Dependencies and integration points
It depends on configured OpenAFS libraries, the test harness `run-tests.in`, many C test sources, `fs_lib`, generated dirpath files, and OpenAFS Perl modules under `OpenAFS/`.

## Risks
The long source/object/program lists can drift; `test-parallel1.o` appears twice in `TEST_OBJS`. Generated path files embed installation assumptions and must be regenerated after configure changes. Empty `install`/`dest` targets intentionally avoid installing tests but may surprise packaging automation.

## Test signals
Run `make all`, `make check`, and `make check-fast`; verify `OpenAFS/Dirpath.pm` and `.sh` contain expected configured paths; build with strict dependency checks for every listed test binary.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Heimdal.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Heimdal.pm

## Purpose
`Auth-Heimdal.pm` is a small legacy Perl authentication helper for Heimdal-style test cells. It reads the local cell, derives an uppercase realm, and provides admin/user authentication commands.

## Important APIs, types, and functions
The package is `OpenAFS::Auth`. It defines `getcell`, `getrealm`, `authadmin`, and `authuser`.

## Control flow
`getcell` opens `$openafsdirpath->{'afsconfdir'}/ThisCell`, reads and chomps the cell name, and returns it. `getrealm` repeats the read and uppercases the cell name. `authadmin` and `authuser` build `kinit -k -t /usr/afs/etc/krb5.keytab <principal>@REALM ; afslog` command strings and execute them with `system`.

## State and persistence behavior
It reads `ThisCell`, reads a fixed keytab path, obtains Kerberos credentials, and obtains AFS tokens through `afslog`. It does not persist module-local state.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, Heimdal `kinit`, `afslog`, a keytab at `/usr/afs/etc/krb5.keytab`, and the test harness expecting an `OpenAFS::Auth` package.

## Risks
Commands are executed through the shell without return-code checks. Realm derivation by uppercasing the cell is simplistic. The keytab path is hard-coded and the module name collides with other `OpenAFS::Auth` implementations.

## Test signals
Verify `ThisCell` missing/readable cases, uppercase realm derivation, successful admin/user keytab login, and failure propagation expectations in the harness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Heimdal.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Kaserver.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Kaserver.pm

## Purpose
`Auth-Kaserver.pm` is a small legacy Perl authentication helper for kaserver-based test cells.

## Important APIs, types, and functions
The package is `OpenAFS::Auth`. It defines `getcell`, `getrealm`, `authadmin`, and `authuser`.

## Control flow
`getcell` and `getrealm` read `ThisCell` from the configured AFS config directory, with `getrealm` uppercasing the result. `authadmin` and `authuser` execute `echo "Proceeding w/o authentication"|klog -pipe <principal>@REALM` via `system`.

## State and persistence behavior
It reads local cell configuration and obtains AFS tokens with `klog`; no Perl state persists beyond function calls.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `klog`, kaserver-era authentication semantics, and test harness code loading `OpenAFS::Auth`.

## Risks
The shell pipeline feeds a constant string rather than a real password, return codes are ignored, and the module is insecure/obsolete by modern Kerberos standards. Package-name reuse can conflict with `Auth.pm`.

## Test signals
Test readable/missing `ThisCell`, admin/user login command construction, `klog` failures, and compatibility only in kaserver test environments.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth-Kaserver.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/Auth.pm

## Purpose
`Auth.pm` is the newer Perl authentication abstraction for OpenAFS tests. It creates backend-specific authentication objects for MIT Kerberos, Heimdal, or kaserver, generates Kerberos/OpenAFS key material where supported, and obtains test credentials.

## Important APIs, types, and functions
Package `OpenAFS::Auth` exposes `create`, `new`, `_lookup_cell_name`, `make_keyfile`, `make_krb_config`, `debug`, and `check_program`. Subpackages `OpenAFS::Auth::MIT`, `OpenAFS::Auth::Heimdal`, and `OpenAFS::Auth::Kaserver` implement `_sanity_check`, `make_keyfile`, and `authorize`; MIT additionally has `_prepare_make_keyfile`.

## Control flow
`create` maps a type to a backend class and constructs it. `new` fills defaults such as admin principal, AFS principal, kvno, keytab, and realm, blesses the object, and runs backend sanity checks. `make_krb_config` writes a krb5 config file for the test realm/cell. MIT keyfile setup checks programs, initializes kadmin state, adds principals, extracts keytabs, ensures AFS config files exist, and runs `asetkey`. `authorize` paths run `kinit` plus `aklog`, Heimdal's `afslog`, or kaserver `klog`.

## State and persistence behavior
The object stores backend configuration in memory. It writes Kerberos config, creates Kerberos principals/keytabs, writes OpenAFS KeyFile material through `asetkey` or `bos addkey`, and obtains Kerberos tickets/AFS tokens in the user's credential cache/PAG context.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `OpenAFS::ConfigUtils::run`, OpenAFS tools (`asetkey`, `aklog`, `tokens`, `kas`, `klog`, `bos`), Kerberos tools (`kadmin.local`, `kdb5_util`, `kinit`), and generated test path configuration.

## Risks
Most commands are shell strings composed from object fields, so quoting and spaces in paths/principals are unsafe. Several operations are privileged and destructive to test Kerberos/OpenAFS state. Heimdal `make_keyfile` is explicitly unimplemented. Backend selection and duplicated legacy modules can confuse loaders.

## Test signals
Test `create` for MIT/Heimdal/kaserver and invalid types, missing program/keytab/realm checks, krb5 config output, MIT principal/keytab/keyfile creation in a disposable realm, authorization flows, debug output, and failure rollback expectations through `ConfigUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/Auth.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/CMU_copyright.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/CMU_copyright.pm

## Purpose
`CMU_copyright.pm` centralizes the Carnegie Mellon AFStools copyright and redistribution notice for the Perl test modules.

## Important APIs, types, and functions
It defines package `AFS::CMU_copyright` and returns true. There are no functions.

## Control flow
Loading the module only evaluates the copyright text and package declaration.

## State and persistence behavior
No runtime state or persistent effects are created.

## Dependencies and integration points
`OpenAFS::afsconf` imports this module to keep the license notice associated with the AFStools-derived Perl modules.

## Risks
The package namespace is `AFS::CMU_copyright`, while the file lives under `OpenAFS/`; this is intentional historical naming but can surprise module loaders.

## Test signals
Verify Perl can `use OpenAFS::CMU_copyright`/load the file through the harness and that dependent modules compile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/CMU_copyright.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/ConfigUtils.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/ConfigUtils.pm

## Purpose
`ConfigUtils.pm` provides small Perl utility functions for the OpenAFS test setup modules: command execution, debug printing, and an unwind stack.

## Important APIs, types, and functions
Package `OpenAFS::ConfigUtils` exports `@unwinds`, `run`, and `unwind`; it also has package global `$debug`.

## Control flow
`run` accepts either a code reference or shell command string. Code references are executed under `eval` and die on exceptions; shell strings optionally print when `$debug` is true, run with `system`, and die on nonzero return. `unwind` pushes a cleanup command or code reference onto `@unwinds`.

## State and persistence behavior
It stores cleanup entries in package global `@unwinds` and debug mode in `$debug`. Shell commands can have arbitrary external side effects.

## Dependencies and integration points
It depends on Perl `Exporter` and is used by authentication and OS setup modules to run OpenAFS/Kerberos/system commands.

## Risks
Shell string execution has quoting/injection risks and only reports raw `$?`. The unwind stack is only collected here; execution policy must be implemented by callers. Global debug state is shared across all users.

## Test signals
Unit tests should cover successful/failed shell commands, successful/failing code refs, debug output, and unwind stack ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/ConfigUtils.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS-LINUX.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/OS-LINUX.pm

## Purpose
`OS-LINUX.pm` is an older OS-specific Perl configuration module that exports Linux init command strings for OpenAFS tests.

## Important APIs, types, and functions
Package `OpenAFS::OS` exports `$openafsinitcmd`, a hashref mapping client and fileserver lifecycle names to `/etc/init.d` commands.

## Control flow
Loading the module initializes the hash and returns true. There are no functions.

## State and persistence behavior
The only module state is the exported hashref. The command strings, when used, start/stop/restart OpenAFS client and fileserver services.

## Dependencies and integration points
It depends on SysV-style `/etc/init.d/openafs-client` and `/etc/init.d/openafs-fileserver` scripts and older harness code expecting `$openafsinitcmd`.

## Risks
Hard-coded init paths do not work on systemd-only or custom-install systems. The package name overlaps `OS.pm`, so load order matters.

## Test signals
Verify module load/export, expected keys, and command availability on target Linux test hosts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS-LINUX.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS-SOLARIS.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/OS-SOLARIS.pm

## Purpose
`OS-SOLARIS.pm` is an older OS-specific Perl configuration module that exports Solaris OpenAFS lifecycle command strings for tests.

## Important APIs, types, and functions
Package `OpenAFS::OS` exports `$openafsinitcmd`, mapping client/fileserver lifecycle actions to `modload`, `afsd`, `bosserver`, `bos shutdown`, and `pkill` command strings.

## Control flow
Loading the module initializes the hashref. Some actions are placeholders that echo unsupported stop/restart behavior.

## State and persistence behavior
Module state is the exported hashref. Executing commands can load kernel modules, start afsd/bosserver, or shut down/kill server processes.

## Dependencies and integration points
It depends on Solaris paths under `/usr/vice/etc` and `/usr/afs/bin`, plus older harness code using `$openafsinitcmd`.

## Risks
Hard-coded paths and `pkill` patterns are broad. Client stop/restart are explicitly unsupported. Package-name overlap with other OS modules can cause load-order confusion.

## Test signals
Verify module load/export and command behavior on a disposable Solaris OpenAFS test host.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS-SOLARIS.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/OS.pm

## Purpose
`OS.pm` is the newer Perl OS abstraction for OpenAFS tests. It constructs platform-specific command providers and contains Unix/Linux implementations for starting/stopping servers, configuring clients, and force-stopping kernel client state.

## Important APIs, types, and functions
Package `OpenAFS::OS` exposes `create`, `new`, `_get_class`, and `command`. `OpenAFS::OS::Unix` provides `remove`, `fileserver_start`, `fileserver_stop`, `fileserver_restart`, `find_pids`, and `number_running`. `OpenAFS::OS::Linux` provides `get_commands`, `configure_client`, `client_forcestop`, and `list_modules`.

## Control flow
`create` chooses an implementation from configured `ostype`; currently only Linux is accepted. `new` stores paths, debug flag, sysconfig path, and command table. `command` retrieves a command or wraps a code reference with parameters. Linux `configure_client` writes an afs.rc configuration file from `OpenAFS::Dirpath` paths, creates cache and `/afs` directories, and `client_forcestop` tries unmount, afsd shutdown, kernel-module removal, and stale lock cleanup.

## State and persistence behavior
Objects store command tables and configuration paths. The module writes `test-afs-rc.conf`, creates/chmods cache directories and `/afs`, starts/stops bosserver, kills processes, removes kernel modules, and removes `/var/lock/subsys/afs`.

## Dependencies and integration points
It depends on `OpenAFS::Dirpath`, `OpenAFS::ConfigUtils::run`, init scripts, bos/bosserver/afsd paths, `/sbin/lsmod`, `/sbin/rmmod`, `ps`, and root privileges for client/server operations.

## Risks
Only Linux is supported despite separate older Solaris module. `fileserver_restart` calls `fileserver_stop()` and `fileserver_start()` without `$self->`, which is likely a bug under strict subs. Shell command strings are unquoted, and `find_pids` can match unintended command names. Force-stop operations are destructive on the host.

## Test signals
Test class selection, command lookup and parameter appending for strings and code refs, client config file content, cache/afs directory creation, module listing, force-stop idempotence, and fileserver stop behavior with zero/multiple bosserver processes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/OS.pm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/afsconf.pm -->
# sources/distributed-fs/openafs/src/tests/OpenAFS/afsconf.pm

## Purpose
`afsconf.pm` is a Perl AFStools-derived module that reads local AFS configuration files and exposes the local cell, canonical cell names, cell servers, known cells, and cache configuration.

## Important APIs, types, and functions
Package `OpenAFS::afsconf` exports `AFS_conf_localcell`, `AFS_conf_canoncell`, `AFS_conf_listcells`, `AFS_conf_cellservers`, and `AFS_conf_cacheinfo`. Internal `_confpath` locates configuration files and `_findcell` parses `CellServDB`.

## Control flow
`_confpath` checks a cached `%conf_paths`, a configured `confdir`, and a default config directory. `AFS_conf_localcell` reads the first line of `ThisCell`. `_findcell` escapes the requested prefix, scans `CellServDB` for a unique matching `>` cell stanza, optionally collects server hostnames/IPs while in that stanza, caches canonical names, and dies on ambiguity or absence. `AFS_conf_listcells` scans every `>` stanza. `AFS_conf_cacheinfo` parses `cacheinfo` colon fields and translator host from `AFSSERVER`, `$HOME/.AFSSERVER`, or `/.AFSSERVER`.

## State and persistence behavior
It reads config files and environment variables, and caches configuration paths and canonical cell names in package globals inherited from the broader AFStools config/util environment. It does not write files.

## Dependencies and integration points
It depends on `OpenAFS::CMU_copyright`, `OpenAFS::config`, `OpenAFS::util`, `%AFS_Parms`, `%AFS_Help`, `%conf_paths`, `$def_ConfDir`, and standard OpenAFS config file formats.

## Risks
Prefix matching for cell names can be ambiguous. `CellServDB` parsing is old and primarily recognizes dotted numeric server entries, so modern hostname/comment variants may not parse as intended. `_confpath` dies when files are absent, while some callers expect optional behavior. Translator lookup relies on `$ENV{HOME}`.

## Test signals
Use fixture config directories for `ThisCell`, `CellServDB`, and `cacheinfo`; test canonical prefix success, ambiguous prefix failure, missing files, server list parsing, cell listing, cache hard limit parsing, and translator environment/file precedence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/tests/OpenAFS/afsconf.pm -->
