# Research: subset-b-007762

Work item `subset-b-007762` covers OpenAFS client daemon startup glue under `src/afsd` and AFS monitor build/output/log parsing code under `src/afsmonitor`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd.c -->
# sources/distributed-fs/openafs/src/afsd/afsd.c

## Purpose

`afsd.c` is the common implementation of the OpenAFS client startup daemon. It parses command-line and `cacheinfo` configuration, computes cache sizing parameters, prepares and sanitizes the workstation cache, pushes configuration into the kernel cache manager through AFSOP syscalls, starts the required cache-manager daemons, and optionally starts user-space support helpers such as AFSDB lookup, background operation helpers, socket proxy handlers, and `rmtsys`.

The file is intentionally platform-neutral at the daemon-policy level. Platform-specific syscall, mount, fork, priority, and daemonization behavior is abstracted through declarations in `afsd.h` and implemented by backends such as `afsd_kernel.c` or the FUSE/libuafs path.

## Important APIs, Types, and Globals

- Public entry points are `afsd_init()`, `afsd_parse(int argc, char **argv)`, and `afsd_run()`.
- Cache preparation helpers include `ParseCacheInfoFile()`, `PartSizeOverflow()`, `CheckCacheBaseDir()`, `SweepAFSCache()`, `CreateCacheFile()`, `GetVFileNumber()`, and `GetDDirNumber()`.
- Kernel setup is funneled through the private variadic `afsd_syscall()` and process/thread launch wrappers `fork_syscall()`, `fork_rx_syscall()`, and, on Sun RX listener builds, `fork_rx_syscall_wait()`.
- `struct afsd_file_list` records cache files that must be moved out of overfull cache subdirectories.
- `struct afs_cacheParams cparams` is populated immediately before `AFSOP_CACHEINIT`.
- Global configuration state includes `cacheBlocks`, `cacheFiles`, `cacheStatEntries`, `dCacheSize`, `vCacheSize`, `chunkSize`, `cacheBaseDir`, `afsd_cacheMountDir`, `confDir`, `rootVolume`, `cacheFlags`, feature booleans such as `enable_afsdb`, `enable_dynroot`, `enable_fakestat`, `enable_backuptree`, `enable_nomount`, `enable_splitcache`, and debug flags `afsd_verbose` and `afsd_debug`.
- Disk-cache bookkeeping uses `cache_dir_list`, `cache_dir_filelist`, `dir_for_V`, and, on non-Linux/non-path-cache builds, `inode_for_V`.
- `enum optionsList` defines stable option offsets used by `cmd_AddParmAtOffset()` and later `cmd_Option*()` lookups.

## Control Flow

Startup begins with `afsd_init()`, which registers the command syntax and all options with the OpenAFS `cmd` package. `afsd_parse()` then parses argv and delegates validation and side effects to `CheckOptions()`. `CheckOptions()` sets globals from options, handles immediate `-shutdown` by issuing `AFSOP_SHUTDOWN`, validates enum-like options such as `-atsys`, parses split-cache percentages, opens the command config file, sets defaults such as `confDir`, and finally reads `cacheinfo` through `ParseCacheInfoFile()`.

`afsd_run()` performs the actual client boot. It opens the cell configuration, loads the local cell name, checks the mount point unless `-nomount` is set, auto-tunes memcache or disk-cache parameters, optionally allocates the cache inode table, builds full cache file pathnames, validates the cache filesystem, and starts kernel services. It then sets the local cell, seeds kernel Rx entropy, advises interface addresses from NetInfo/NetRestrict files, adjusts priorities, starts Rx listener/callback/event daemons, starts AFSDB and socket proxy helpers when enabled, calls `AFSOP_BASIC_INIT`, and sends `AFSOP_CACHEINIT`.

For disk caches, `afsd_run()` sweeps the cache directory up to `MAX_CACHE_LOOPS`. `SweepAFSCache()` initializes directory bookkeeping and calls `doSweepAFSCache()`, which recursively scans top-level `D<number>` cache subdirectories, creates missing metadata files, deletes unknown cache entries, creates or moves `V<number>` data cache files into the appropriate subdirectories, rebalances overfull directories, removes obsolete directories, and records each cache file location or inode. After this, `afsd_run()` provides `CacheItems`, `CellItems`, `VolumeItems`, and every cache file path or inode to the kernel.

After cache setup, `afsd_run()` applies optional kernel settings such as split-cache bucket percentages, close synchronization, Rx fragment/MTU limits, inode calculation mode, dynroot, fakestat, backup-tree mode, volume TTL, and `@sys` behavior. It pushes all configured cells and aliases via `ConfigCell()` and `ConfigCellAlias()`, starts AFS/checkserver/background/truncation daemons, optionally sets a root volume, calls `AFSOP_GO`, mounts AFS unless disabled, and starts `rmtsys` support if requested.

Optional helper loops are long-running. `AfsdbLookupHandler()` waits for kernel AFSDB lookup requests, resolves cells with `afsconf_GetAfsdbInfo()`, returns server addresses and TTL, and exits on shutdown. `BkgHandler()` services `AFSOP_BKG_HANDLER` user-space background requests, including Darwin cross-device move emulation. Socket proxy builds create UDP sockets based on kernel requests and run separate send/receive loops through `AFSOP_SOCKPROXY_HANDLER`.

## State and Persistence Behavior

Most state is process-global and accumulated before the main initialization sequence. Persistent state is primarily the disk cache tree: `CacheItems`, `VolumeItems`, `CellItems`, cache subdirectories `D<number>`, and cache data files `V<number>`. The sweep can create, move, chmod, set Darwin no-backup attributes on, or delete filesystem entries. The code also reads persistent client configuration from `cacheinfo`, `ThisCell`, `CellServDB`, cell aliases, and NetInfo/NetRestrict paths via `afsconf`.

Once startup syscalls succeed, significant state moves into the kernel cache manager: local cell, interface addresses, cache parameters, cell list, cache file handles/inodes, volume/cell metadata file paths, behavior flags, and daemon activity. The file itself does not implement durable metadata formats for cache contents; it prepares filenames and hands them to the kernel.

## Dependencies and Integration Points

`afsd.c` depends on OpenAFS headers and libraries for command parsing, cell configuration, syscalls, cache parameter structures, Rx/kernel opcodes, user-space cache manager support, and utility macros. It also uses roken, hcrypto `RAND_bytes`, libc/POSIX filesystem APIs, directory iteration, stat/statfs/statvfs, fork/wait/signal, and platform frameworks on Darwin for network/power events.

The main external integration is the AFS kernel module through AFSOP syscalls. The exact syscall ABI is backend-provided by `afsd_call_syscall()`. It also integrates with `afsd_mount_afs()`, `afsd_check_mount()`, `afsd_fork()`, `afsd_daemon()`, and priority setters declared in `afsd.h`.

## Risks and Edge Cases

- Many path buffers are fixed at 1024 bytes and constructed with `sprintf()` in several places, so overly long cache/config paths are a persistent risk.
- Cache sweeping deletes unknown files from the cache directory. Misconfigured `cacheBaseDir` can cause destructive cleanup in the wrong directory.
- Cache directory balancing is complex and relies on global arrays initialized for the computed `cacheFiles`/`nFilesPerDir` values; off-by-one or stale directory state could strand cache files.
- `CreateCacheFile()` treats file descriptor `0` as failure (`cfd <= 0`), which is conservative but can mis-handle a valid descriptor if stdin is closed.
- Several helper loops sleep and retry indefinitely after syscall errors, which is appropriate for daemon helpers but can hide persistent configuration or kernel ABI failures.
- `afsd_syscall_populate()` must remain synchronized with all AFSOP argument shapes. A missing or misclassified opcode corrupts the syscall argument ABI.
- Some options are deprecated or ignored, and some behavior is compile-time platform dependent, making test coverage across platforms important.

## Test Signals

Useful test signals include option parsing tests for mutually constrained options (`-memcache`, `-dcache`, `-blocks`, `-atsys`, `-splitcache`), cacheinfo parsing, disk cache sweeps with missing, extra, top-level, and overfull cache files, platform builds that exercise `AFSOP_CACHEFILE` and `AFSOP_CACHEINODE` fallbacks, and startup integration tests that verify the ordered syscall sequence through a mocked `afsd_call_syscall()`. Manual/system tests should include disk cache startup, memcache startup, `-nomount`, `-shutdown`, AFSDB-enabled startup, and path length/misconfiguration failure modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd.h -->
# sources/distributed-fs/openafs/src/afsd/afsd.h

## Purpose

`afsd.h` defines the shared interface between the common daemon logic in `afsd.c` and platform/runtime backends. It exposes the daemon lifecycle functions, global debug/mount variables, callback type used by `afsd_fork()`, portable syscall argument typing, and the backend operations that `afsd.c` requires but does not implement.

## Important APIs and Types

- `extern int afsd_debug`, `extern int afsd_verbose`, and `extern char *afsd_cacheMountDir` expose daemon state to backend files.
- `afsd_init()`, `afsd_parse()`, and `afsd_run()` are the common lifecycle API.
- `typedef void* (*afsd_callback_func)(void *rock)` is the function signature for work launched by `afsd_fork()`.
- `afsd_syscall_param_t` abstracts syscall parameter width. Darwin 10 uses `user_addr_t`, Darwin 8 uses `unsigned int`, and other platforms use `long`.
- `CAST_SYSCALL_PARAM()` handles pointer/integer casting for syscall transport, using `CAST_USER_ADDR_T()` on newer Darwin.
- `struct afsd_syscall_args` carries the opcode, up to seven syscall parameters, a routine name for logging, and an `rxpri` flag.
- Backend-required functions include `afsd_mount_afs()`, `afsd_check_mount()`, `afsd_set_rx_rtpri()`, `afsd_set_afsd_rtpri()`, `afsd_call_syscall()`, `afsd_fork()`, and `afsd_daemon()`.

## Control Flow and Integration

The header establishes a two-part design. `afsd.c` builds the command, cache, and kernel-setup plan, then calls functions declared here to perform platform-sensitive work. `afsd_kernel.c` provides the native kernel-backed implementation and `afsd_fuse.c` provides a FUSE/libuafs entry path that includes this header for shared parsing semantics.

## State and Persistence Behavior

The header itself persists no state. Its definitions determine how pointer and integer parameters are represented when persisted into a syscall request structure and handed to platform code. That ABI is critical because the kernel side interprets the positional `params[]` array.

## Dependencies and Risks

The central risk is ABI drift. `afsd_syscall_param_t`, `CAST_SYSCALL_PARAM()`, and `struct afsd_syscall_args` must match platform kernel expectations and every caller in `afsd.c`. If a platform changes pointer width or syscall transport semantics, silent truncation or invalid kernel pointers are possible. The header also centralizes backend obligations, so any alternative runtime must implement every declared function with matching semantics.

## Test Signals

Compile tests across supported platform macro sets are the most important signal. Runtime tests should mock `afsd_call_syscall()` and confirm that `afsd.c` populates `struct afsd_syscall_args` correctly for pointer-heavy and integer-heavy opcodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd_fuse.c -->
# sources/distributed-fs/openafs/src/afsd/afsd_fuse.c

## Purpose

`afsd_fuse.c` implements `afsd.fuse`, a FUSE frontend that connects FUSE filesystem callbacks to the OpenAFS user-space cache manager (`libuafs`). Instead of mounting and configuring a kernel cache manager, it starts libuafs, translates FUSE-visible paths to `/afs/...` paths, routes file operations to `uafs_*` calls, and splits command-line arguments between OpenAFS `cmd`/afsd options and FUSE options.

## Important APIs and Functions

- `afs_path()` converts a FUSE path such as `/cell/path` to a libuafs path `/afs/cell/path` and returns heap storage.
- `fuafsd_init()` starts libuafs with `uafs_Run()` and sets the mount directory to `/afs`.
- FUSE operation wrappers include `fuafsd_getattr()`, `fuafsd_opendir()`, `fuafsd_readdir()`, `fuafsd_releasedir()`, `fuafsd_create()`, `fuafsd_open()`, `fuafsd_read()`, `fuafsd_readlink()`, `fuafsd_mkdir()`, `fuafsd_unlink()`, `fuafsd_rmdir()`, `fuafsd_symlink()`, `fuafsd_rename()`, `fuafsd_link()`, `fuafsd_chmod()`, `fuafsd_truncate()`, `fuafsd_write()`, `fuafsd_statvfs()`, `fuafsd_release()`, and `fuafsd_destroy()`.
- `fuafsd_oper` registers those wrappers with FUSE.
- `fuafsd_cmd_check()` and `split_args()` classify argv entries as OpenAFS command options or FUSE options.
- `main()` initializes libuafs, splits arguments, parses afsd/libuafs options, adds FUSE defaults, and calls `fuse_main()`.

## Control Flow

`main()` constructs separate `fuse_args` and `afsd_args` vectors. It adds FUSE options for inode preservation and `fsname=AFS`, adds `allow_other` for root, calls `uafs_Setup("/afs")`, and runs `split_args()`. The split logic temporarily redirects stderr to `/dev/null` while probing each argument with `cmd_Dispatch()`, using a `cmd` before-proc to detect accepted OpenAFS options. After parsing afsd arguments via `uafs_ParseArgs()`, it appends `--` and the libuafs mount directory to the FUSE argument list and enters `fuse_main()`.

During filesystem operation, FUSE calls `fuafsd_init()`, which starts libuafs and fixes the internal mount directory. Each file operation translates paths when needed, calls the corresponding `uafs_*` API, maps failures to negative `errno`, and stores directory pointers or file descriptors in `struct fuse_file_info::fh`.

## State and Persistence Behavior

The file keeps process-local global argument vectors (`afsd_args`, `fuse_args`) and transient parser state (`fuafsd_cmd_accept`, `nullfd`, `stderr_save`). Open file and directory handles are persisted only in FUSE file handles for the duration of operations. Durable filesystem state changes are delegated to libuafs operations, which perform the AFS semantics for creates, writes, removes, links, renames, chmods, and truncates.

## Dependencies and Integration Points

The file depends on libfuse API version 31, OpenAFS user-space APIs from `afs_usrops.h`, OpenAFS command parsing, and normal POSIX allocation/open/dup/close behavior. It integrates with the same afsd command vocabulary by calling `uafs_ParseArgs()` after using `cmd_Dispatch()` as the option classifier.

## Risks and Edge Cases

- `fuafsd_readlink()` writes `buf[code] = '\0'` without checking that `code < len`; this depends on `uafs_readlink()` respecting the buffer length in a way that leaves room for termination.
- `fuafsd_write()` copies the FUSE const buffer into a mutable heap buffer before `uafs_pwrite()`, increasing memory pressure for large writes.
- `split_args()` classifies options by probing the OpenAFS command parser. Options accepted by both FUSE and OpenAFS will be routed to OpenAFS.
- FUSE rename flags other than zero are rejected with `-EINVAL`, so newer FUSE rename semantics are unsupported.
- The code assumes `fi->fh` can safely carry `usr_DIR *` and integer file descriptors through `uintptr_t`.

## Test Signals

Useful tests include argument splitting with afsd-only, FUSE-only, and option-with-argument cases; FUSE operation tests against a mocked libuafs layer; error mapping checks that return `-errno`; readlink boundary tests; rename flag rejection; and startup tests that verify `uafs_Setup()`, `uafs_ParseArgs()`, `uafs_MountDir()`, and `fuse_main()` are called in order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd_fuse.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd_kernel.c -->
# sources/distributed-fs/openafs/src/afsd/afsd_kernel.c

## Purpose

`afsd_kernel.c` is the native kernel-backed backend for the common `afsd.c` daemon logic. It implements platform-specific AFS syscall transport, syscall tracing, mount handling, mtab/DiskArbitration integration, process forking, daemonization, priority adjustment, mountpoint validation, and the native `main()` function for the standard `afsd` binary.

## Important APIs and Functions

- `afsd_init_syscall_opcodes()` initializes a table that maps AFSOP numeric opcodes to names for debug tracing.
- `afsd_set_rx_rtpri()` and `afsd_set_afsd_rtpri()` apply platform priority policy. SGI uses realtime scheduling; Linux lowers nice value for Rx work.
- `os_syscall()` is implemented differently for Linux `/proc` ioctl, Darwin syscall device ioctls including a 64-bit variant, Solaris ioctl helper, SGI `afs_syscall`, AIX `syscall`, and the generic `AFS_SYSCALL` path.
- `afsd_call_syscall()` calls `os_syscall()` and optionally prints debug traces with opcode names.
- AIX-specific `vmountdata()` and `aix_vmount()` build `struct vmount` payloads.
- `HandleMTab()` updates `/etc/mtab` or platform mount registries where needed and pings Darwin DiskArbitration on older macOS.
- `afsd_mount_afs()` performs the platform-specific mount call and records the mount.
- `afsd_fork()`, `afsd_daemon()`, and `afsd_check_mount()` implement backend services required by `afsd.c`.
- `main()` wires everything together: unbuffered stdout/stderr, syscall opcode table, common init/parse, help handling, and `afsd_run()`.

## Control Flow

Startup through this backend enters `main()`, initializes tracing names, registers common command syntax, parses options, and delegates the boot sequence to `afsd_run()`. During that sequence, every `afsd_syscall()` from `afsd.c` reaches `afsd_call_syscall()`, which invokes the platform-specific `os_syscall()` implementation selected at compile time.

Mounting is similarly delegated. `afsd_mount_afs()` computes mount flags, selects the appropriate OS `mount()` or AIX `vmount()` call, exits on failure, then calls `HandleMTab()` so system mount listings reflect AFS where required. `afsd_check_mount()` rejects missing, non-directory, and relative mountpoints before startup reaches the kernel mount operation.

## State and Persistence Behavior

The file owns only transient process state except for mount-table updates. `afsd_syscalls[]` is process-local debug metadata. `HandleMTab()` can append an AFS entry to `/etc/mtab` on Linux/SGI/HPUX-style systems or notify DiskArbitration on Darwin. `afsd_mount_afs()` changes kernel mount state. `afsd_fork()` creates long-lived child daemon processes requested by the common code.

## Dependencies and Integration Points

This backend is tightly coupled to OS kernel interfaces: `/proc` AFS syscall devices and `VIOC_SYSCALL` on Linux, `/dev` syscall ioctls on Darwin, Solaris `ioctl_sun_afs_syscall`, AIX `vmount`, and generic syscall numbers elsewhere. It also depends on OpenAFS opcode definitions, `afsd.h`, mount table APIs, and POSIX fork/wait/daemon/stat.

## Risks and Edge Cases

- The syscall ABI is highly platform-specific and parameter-width sensitive. Darwin 64-bit handling mitigates one case, but unsupported macro combinations can still truncate or misroute arguments.
- `afsd_fork()` asserts `fork()` success and exits child processes with status `1` after callbacks return, assuming callbacks normally do not return.
- `HandleMTab()` appends mount entries with limited locking/commented locking support; concurrent mount table updates may race.
- Mount failure exits the process directly, so callers cannot recover after `afsd_mount_afs()` fails.
- Debug tracing only prints the first parameter value, which helps identify calls but not full argument state.

## Test Signals

Build matrix coverage across platform macro sets is essential. Unit-level tests can mock `os_syscall()` to verify debug opcode mapping and return handling. Integration tests should verify mountpoint rejection, mount invocation parameters per platform, mtab entry formatting, `CMD_HELP` returning success, and native startup with a mocked kernel syscall interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/afsd_kernel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/vsys.c -->
# sources/distributed-fs/openafs/src/afsd/vsys.c

## Purpose

`vsys.c` is a small diagnostic utility for invoking an AFS syscall directly from the command line. It parses numeric and string arguments into six syscall parameters, calls `syscall(AFS_SYSCALL, ...)` when available, and prints the returned code.

## Important APIs and Functions

- `main()` is the only function.
- Numeric arguments are parsed with `atoi()`.
- The `-s` switch makes the next argument be passed as a string pointer, cast through `intptr_t`.
- `parms[0]` is the syscall call number or top-level syscall selector, and `parms[1]` through `parms[5]` are passed as remaining arguments to `syscall()`.

## Control Flow

The program requires at least one argument. It iterates argv from index 1, toggling between numeric and string parsing. Unknown switches cause immediate exit. After parameter collection it calls the AFS syscall if `AFS_SYSCALL` is defined; otherwise it reports `-1`. It always prints `code <value>` before returning success.

## State and Persistence Behavior

The utility keeps only stack-local argument state. Any durable or kernel state changes are entirely determined by the syscall number and parameters supplied by the user.

## Dependencies and Integration Points

It depends on OpenAFS syscall definitions from `afs/afssyscalls.h` and `afs/afs_args.h`, libc `syscall()`, and the generated component version file. It is effectively a low-level integration/debug hook for the kernel AFS syscall surface.

## Risks and Edge Cases

- `parms` has six slots but there is no bounds check on `counter`, so too many arguments can overflow the stack buffer.
- `atoi()` provides weak validation and silently maps invalid numeric input to zero.
- Passing arbitrary string pointers to kernel syscalls is unsafe unless the caller knows the exact ABI.
- The program returns `0` even when the syscall returns an error code.

## Test Signals

Tests should cover usage output, unknown switch handling, numeric parsing, `-s` pointer placement, too-many-argument hardening if changed, and builds with and without `AFS_SYSCALL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsd/vsys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/Makefile.in -->
# sources/distributed-fs/openafs/src/afsmonitor/Makefile.in

## Purpose

`Makefile.in` defines the automake-style build rules for `afsmonitor` and the auxiliary `afsmon-parselog` parser in the OpenAFS `src/afsmonitor` directory. It gathers required OpenAFS headers, links against xstat, gtx UI, rxkad, fsint, cmd, util, opr, lwp compatibility, and volser libraries, and provides install/dest/clean targets.

## Important Targets and Variables

- `INCLS` lists public and local headers that should trigger object rebuilds, including GTX UI headers, keys/cellconfig/cmd, `xstat_fs.h`, `xstat_cm.h`, `afsmonitor.h`, and `afsmon-labels.h`.
- `LT_deps` lists libtool archive dependencies for xstat, UI, authentication, filesystem interface, command, utility, and volume support.
- `EXTRA_LIBS` adds curses and X libraries.
- `all` builds `afsmonitor`.
- Object rules declare dependencies for `afsmon-output.o`, `afsmon-win.o`, and `afsmonitor.o`.
- `afsmonitor` links the main monitor from three objects and the library set.
- `afsmon-parselog` links the standalone log parser.
- `install` and `dest` install `afsmonitor` into configured binary destinations.
- `clean` removes libtool outputs, object files, binary, and generated component version source.

## Control Flow

Configure substitutes `@srcdir@`, top object directory, and included make fragments. A normal build compiles object files, links a static libtool binary for `afsmonitor`, and optionally builds `afsmon-parselog`. Install rules create destination directories before copying the monitor binary.

## State and Persistence Behavior

The file governs generated build artifacts in the source/object directory and installed binaries under `${DESTDIR}${bindir}` or `${DEST}/bin`. It includes `Makefile.version`, which generates or tracks `AFS_component_version_number.c` for version embedding.

## Dependencies and Integration Points

The monitor depends on OpenAFS xstat collection libraries, GTX display support, curses/X libraries, command parsing, Rx/Rxkad, filesystem interfaces, and utility libraries. The parser target reuses much of the same link set despite being a standalone log reader.

## Risks and Edge Cases

- The `afsmon-parselog` target compiles/links `afsmon-parselog.c` directly in the link command rather than using the listed `afsmon-parselog.o`, which is unusual and can diverge from normal object handling.
- Header dependency lists are manual; adding a new local include without updating `INCLS` can produce stale builds.
- Build behavior depends heavily on top-level make fragments and libtool variables.

## Test Signals

Useful signals include `make afsmonitor`, `make afsmon-parselog`, `make clean`, staged `make install DESTDIR=...`, and rebuild tests after touching `afsmon-labels.h`, `afsmonitor.h`, and xstat headers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/Makefile.in -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-labels.h -->
# sources/distributed-fs/openafs/src/afsmonitor/afsmon-labels.h

## Purpose

`afsmon-labels.h` is a declarative data table for `afsmonitor`. It defines variable names, three-row display labels, and category/group ranges for file server and cache manager xstat data. The monitor uses these arrays to map positional xstat values to names, headings, sections, and display groupings.

## Important Data Structures

- `fs_varNames[]` lists file server statistic variable names, covering performance counters, vnode cache, directory package, Rx, host module, busies, RPC operation timings, transfer timings, and callback counters.
- `fs_labels[]` provides matching display labels split by slash separators into up to three rows.
- `fs_categories[]` defines named sections and groups with inclusive positional index ranges into `fs_varNames[]`.
- `cm_varNames[]` lists cache manager statistic names, covering cache usage, server up/down records, FS/VL RPC timings and errors, transfer timing, CM callback RPC timing, authentication/PAG state, and replicated access counters.
- `cm_labels[]` provides matching display labels for cache manager data.
- `cm_categories[]` defines cache manager display sections and positional ranges.

## Control Flow and Integration

There are no functions in this header. Its control role is positional: consumers include the header, then use array indices from xstat result data to look up names and labels. Category strings encode both hierarchy and index ranges, e.g. `PerfStats_section 6` followed by group entries. The monitor must parse or otherwise interpret those strings consistently.

## State and Persistence Behavior

The arrays are static program data after compilation. They do not persist runtime state, but they define the persistent interpretation of monitor output columns and UI groupings. Any change to array order or category ranges changes the meaning of displayed or logged data.

## Dependencies and Integration Points

The header includes `afsmonitor.h` and is tied to the field order and sizes of `xstat_fs.h`, `xstat_cm.h`, and the structures printed by `afsmon-output.c`. It is also tied to UI code that expects slash-delimited labels and category strings with section/group suffixes.

## Risks and Edge Cases

- The file relies on parallel arrays. `*_varNames`, `*_labels`, and `*_categories` must remain synchronized with xstat struct layout and with each other.
- Category ranges are hard-coded numeric indices. Adding, removing, or reordering variables without updating ranges will misclassify data.
- Several labels contain historical abbreviations and typographical inconsistencies; changing them may break scripts that parse display labels, while not changing them can confuse users.
- The arrays are defined in a header, not declared `extern`, so including this file in multiple translation units would create duplicate definitions unless the build intentionally includes it once.

## Test Signals

Tests should validate array counts against expected xstat collection lengths, ensure each category range is within bounds, verify label and variable-name arrays have matching lengths, and exercise UI rendering for long labels and section/group parsing. Any xstat structure change should require a test or generator check that fails until these tables are updated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-labels.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-output.c -->
# sources/distributed-fs/openafs/src/afsmonitor/afsmon-output.c

## Purpose

`afsmon-output.c` writes `afsmonitor` probe results to output files. It appends compact rows containing timestamp, hostname, host type, and raw xstat longwords, and optionally writes detailed human-readable decodes of file server and cache manager statistics.

## Important APIs and Functions

- Public output entry points are `afsmon_fsOutput(char *a_outfile, int a_detOutput)` and `afsmon_cmOutput(char *a_outfile, int a_detOutput)`.
- File server decode helpers include `Print_fs_OverallPerfInfo()`, `Print_fs_OpTiming()`, `Print_fs_XferTiming()`, `Print_fs_DetailedPerfInfo()`, `Print_fs_FullPerfInfo()`, and `Print_fs_CallBackStats()`.
- Cache manager helpers include `Print_cm_UpDownStats()`, `Print_cm_OverallPerfInfo()`, `Print_cm_PerfInfo()`, `Print_cm_OpTiming()`, `Print_cm_XferTiming()`, `Print_cm_ErrInfo()`, `Print_cm_RPCPerfInfo()`, and `Print_cm_FullPerfInfo()`.
- Static name tables `fsOpNames`, `cmOpNames`, `xferOpNames`, and `CbCounterStrings` supply human-readable labels for repeated timing/error arrays.
- The code consumes global `xstat_fs_Results` and `xstat_cm_Results` from the xstat libraries and monitor runtime.

## Control Flow

`afsmon_fsOutput()` opens the target file in append mode, writes a leading compact record prefix of `ctime`, hostname, and `FS`, checks `probeOK`, writes `-1` for failed probes, otherwise writes all collected file-server longwords. If detailed output is requested, it dispatches based on collection number: full performance data is decoded with `xstat_fs_DecodeFullPerfStats()` before printing, while callback stats are printed as bounded counter values.

`afsmon_cmOutput()` follows the same compact-row pattern for `CM` records. It writes all cache-manager collection longwords and, when detailed output is requested, calls `Print_cm_FullPerfInfo()`. The detailed CM path checks that the received longword count matches `sizeof(struct afs_stats_CMFullPerf) >> 2`, casts the result buffer, and prints overall, RPC, authentication, and replicated-access sections.

## State and Persistence Behavior

The only persistent behavior is appending to the user-specified output file. Static `FILE *` variables `fs_outFD` and `cm_outFD` are used by helper print routines while a record is being written. The compact format is intentionally parseable later by `afsmon-parselog.c`, so field order and count are part of an informal on-disk log contract.

## Dependencies and Integration Points

The file depends on `xstat_fs.h`, `xstat_cm.h`, `afsmonitor.h`, global monitor error/debug variables (`afsmon_debug`, `debugFD`, `errMsg`), and `afsmon_Exit()`. It must stay synchronized with xstat structure layouts, operation-count constants such as `FS_STATS_NUM_RPC_OPS`, and the parser in `afsmon-parselog.c`.

## Risks and Edge Cases

- The code appends without file locking despite a comment noting that CM output needs locking; concurrent monitor writers can interleave records.
- Compact output uses `ctime()` text split by spaces, so parser assumptions depend on the exact ctime format.
- Detailed CM output always calls `Print_cm_FullPerfInfo()` regardless of collection number, unlike the FS path, so non-full CM collections would hit size mismatch behavior.
- Many print formats use `%d` for values that may evolve in width with xstat structures.
- The parser and label table duplicate operation-name knowledge; drift can produce inconsistent human-readable output.

## Test Signals

Tests should create synthetic FS and CM xstat result buffers and verify compact rows, failed-probe `-1` rows, detailed full-performance output, callback stat truncation to known labels, size mismatch messages, append behavior, and compatibility with `afsmon-parselog.c` for generated compact rows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-parselog.c -->
# sources/distributed-fs/openafs/src/afsmonitor/afsmon-parselog.c

## Purpose

`afsmon-parselog.c` is a standalone parser for compact output generated by `afsmonitor -output`. It reads records containing a ctime-style timestamp, hostname, host type (`FS` or `CM`), and raw longword statistics, then prints a readable decode. The file intentionally clones much of `afsmon-output.c` so it can be distributed independently to users who need to inspect monitor logs.

## Important APIs and Functions

- `XSTAT_CM_FULLPERF_RESULTS_LEN` and `XSTAT_FS_FULLPERF_RESULTS_LEN` define expected compact record lengths.
- File server print helpers mirror the monitor output code: `Print_fs_OverallPerfInfo()`, `Print_fs_OpTiming()`, `Print_fs_XferTiming()`, `Print_fs_DetailedPerfInfo()`, and `Print_fs_FullPerfInfo()`.
- Cache manager print helpers include `Print_cm_UpDownStats()`, `Print_cm_OverallPerfInfo()`, `Print_cm_OpTiming()`, `Print_cm_XferTiming()`, `Print_cm_ErrInfo()`, `Print_cm_RPCPerfInfo()`, and `Print_cm_FullPerfInfo()`.
- Static `fsOpNames`, `cmOpNames`, and `xferOpNames` label repeated stats arrays.
- K&R-style `main(argc, argv)` opens the input file, parses each compact record line, converts text values to `long`, casts the buffer to the expected xstat structure, and prints sections.

## Control Flow

The program exits with usage text for missing help-like arguments. It opens the input file, allocates one line buffer and one `long` buffer sized from the larger CM result length, then loops over `fgets()`. Short lines are skipped. For each record it parses seven leading fields (`day month date time year hostname hosttype`), advances a character pointer past those fields, checks for `-1` failed probes, selects the expected number of longwords based on `hosttype`, scans that many values, and dispatches to CM or FS detailed printing if the count matches.

## State and Persistence Behavior

The parser has no persistent output besides stdout/stderr. It reads the compact monitor log as an informal persistent format and assumes the stored longword sequence exactly matches the compiled xstat structure definitions and the hard-coded result lengths.

## Dependencies and Integration Points

The file depends on `xstat_fs.h`, `xstat_cm.h`, libc stdio/allocation/string functions, and the compact row format emitted by `afsmon-output.c`. It also relies on structure layout compatibility between the machine that produced the log and the machine compiling/running the parser.

## Risks and Edge Cases

- The expected result lengths are hard-coded and explicitly marked as needing manual updates when xstat structures change.
- The parser uses fixed-size buffers for timestamp fields and hostname; malformed or long input can overflow via `sscanf("%s")`.
- Pointer advancement after the timestamp assumes single-space field separation and ctime-like layout.
- It scans exactly the expected number of values without robustly detecting line truncation before advancing by `strlen(tmpstr) + 1`.
- The allocated `long` buffer is cast directly to xstat structures, making the parser sensitive to word size, alignment, endianness, and structure packing.
- The program omits an explicit final `return` from `main()` and uses older K&R function definitions.

## Test Signals

Useful tests include round-tripping compact records emitted by `afsmon-output.c`, failed-probe lines, malformed host types, truncated records, overlong hostnames, result-length changes, and cross-architecture log compatibility checks. Static analysis should flag unchecked `sscanf()` widths and direct struct casts from text-parsed buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afsmonitor/afsmon-parselog.c -->
