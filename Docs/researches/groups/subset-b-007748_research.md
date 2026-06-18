# subset-b-007748 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/nbio.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/nbio.c

Purpose: Windows torture-test I/O engine derived from Samba nbio code, adapted to exercise OpenAFS/Windows filesystem behavior through Win32 APIs and shell utilities. It implements scriptable operations such as create, read, write, close, unlink, rename, directory tree cleanup, locker attach/detach, copy/move, path/file queries, and filesystem free-space queries.

Important APIs and functions: `FindHandle` resolves logical script handles in thread-local `ftable`; `nb_createx`, `nb_writex`, `nb_readx`, `nb_close`, `nb_unlink`, `nb_rmdir`, `nb_rename`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_deltree`, and `nb_cleanup` implement the command surface declared in `proto.h`. `CreateObject`, `GetFileList`, `WinFindFirstFile`, `WinFindNextFile`, `GetPathInfo`, `GetFileInfo`, `nb_read`, and `nb_write` are local Win32 shims.

Control flow: each command prepends `AfsLocker` where appropriate, starts timing with `StartFirstTimer`, performs a Win32 or `system` operation, then records success/error timing with `EndFirstTimer`. Failures call `LeaveThread`, which increments command error counts, formats the last error, writes per-thread logs, optionally dumps AFS trace data, and clears `*pThreadStatus`.

State and persistence: most operational state is thread-local: process number, command counters, open-file table, I/O buffer, active locker path, host name, exit status, and timing ticks. Persistent effects are real filesystem mutations under the locker path plus log files under `logNNNNN/<host>/Thread_XXXXX.log`.

Dependencies and integration: depends on `common.h` command IDs/types, `includes.h` Win32 definitions, `output.c` logging, the torture script runner that dispatches `nb_*` functions, and external MIT `attach`/`detach`, DOS `copy`, `xcopy`, `move`, `del`, `mkdir`, and `rmdir` tools.

Risks and test signals: fixed-size buffers and unquoted shell command construction are fragile for long paths and spaces. `nb_qpathinfo` has compatibility flags encoded as magic `Type` values. `GetFileInfo` appears to set `rc = 0` when optional `size` or `mode` outputs are requested, so callers with those arguments must be checked carefully. Positive test signals are command counters, per-command latency/error statistics, Win32 `GetLastError` logs, and optional AFS trace dumps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/nbio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/output.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/output.c

Purpose: reporting and logging support for the Windows torture harness. It converts per-command `cmd_struct` counters into readable statistics, serializes thread/process log writes, dumps AFS client trace logs, and builds aggregate master statistics files.

Important APIs and functions: `LogStats` prints tabular command latency, count, cost, and error summaries. `LogMessage` appends timestamped messages to per-thread logs and optionally a chronological `Chron.log`. `DumpAFSLog` runs `fs trace -dump`, moves `%WINDIR%\TEMP\afsd.log` into the current run's log directory, and renames it with host/iteration context. `UpdateMasterLog` reads, merges, and rewrites a raw numeric accumulator file. `BuildMasterStatLog` rolls a numeric accumulator into a formatted statistics report.

Control flow: callers pass command counters from worker threads or processes. `LogStats` zeroes a temporary aggregate, folds supplied counters, emits headers, and prints one row per `cmd_names` entry. `LogMessage` conditionally guards chronological logging with `ChronMutexHandle`; master-log updates use `FileMutexHandle`.

State and persistence: writes under `log%05d` directories in the process working directory. The raw master log persists seven numeric lines per command entry, while the formatted stat log is rebuilt by `BuildMasterStatLog`.

Dependencies and integration: uses globals from the stress runner (`ChronLog`, `CurrentLoop`, mutex handles), command metadata from `common.h`, Win32 file/mutex APIs, and the OpenAFS `fs trace` command.

Risks and test signals: formatting uses fixed 512/1024 byte buffers and assumes log directories exist. Several `fopen` and `system` results are not fully checked. Correct operation is visible through stable chronological ordering, merged master counts, and generated `afsd_<host>_iterationN.log` trace files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Source/output.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/StopStressTest/StopStressTest.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/StopStressTest/StopStressTest.c

Purpose: small interactive console controller for a running Windows torture stress test. It signals global named events so other processes can pause, continue, or end.

Important APIs and functions: `main` opens standard input and creates `AfsShutdownEvent`, `AfsPauseEvent`, and `AfsContinueEvent`. `GetConsoleInput` reads console `KEY_EVENT` records and maps `p`, `c`, `e`, and `q` to requests. `ProcessRequest` sets/resets the named events and prevents continue/pause after an end request.

Control flow: the program loops prompting the operator, blocks in `ReadConsoleInput`, exits immediately on `q`, and calls `ProcessRequest` for recognized stress-control commands. End sets shutdown, clears pause, and sets continue so paused workers can notice shutdown.

State and persistence: no file persistence. State is carried by named Win32 manual-reset event objects and a local static `LastRequest`.

Dependencies and integration: integrates with the torture/stress processes by event names only; all participants must agree on `AfsShutdownEvent`, `AfsPauseEvent`, and `AfsContinueEvent`.

Risks and test signals: `CreateEvent` failures are not checked, and `GetConsoleInput` reads only one record despite a 128-record buffer. Good test signals are visible console messages plus worker processes actually pausing, resuming, or shutting down when the events are set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/StopStressTest/StopStressTest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/StdAfx.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/StdAfx.h

Purpose: Visual C++ precompiled-header placeholder for the `Stress` launcher project.

Important APIs and types: only an include guard and optional `#pragma once` for MSVC versions greater than 1000 are active. The body contains the standard Visual Studio insertion marker for project-specific includes.

Control flow: none at runtime.

State and persistence: none.

Dependencies and integration: included by older Visual Studio project configurations to satisfy PCH build settings. It deliberately does not pull in Windows headers; `Stress.c` includes its own dependencies.

Risks and test signals: low code risk, but project settings may depend on this file existing. Build success of the legacy VC project is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/StdAfx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/Stress.c -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/Stress.c

Purpose: Windows process fan-out launcher for the torture executable. It starts multiple minimized `wintorture.exe` processes against distinct target directories while preserving most command-line switches.

Important APIs and functions: `main` parses options with an embedded BSD-style `getopt`, finds an unused `LogNNNNN` directory number, validates `-f` target directory and `-d` process count, and launches children with `CreateProcess`. `usage`, `_progname`, and `getopt` provide command-line support.

Control flow: after option parsing, the launcher scans `Log00000` through `Log00099`, then constructs each child command by copying original arguments while rewriting the argument after `-f` to append a zero-padded directory index. It appends `-g <LogID>`, starts `wintorture.exe`, stores the process handle, and sleeps the requested delay between starts.

State and persistence: persistent effects are child processes and whatever `wintorture.exe` writes under the selected log directory and per-process target directories. The local `hArray` stores handles but does not wait for or close them.

Dependencies and integration: depends on the adjacent `wintorture.exe`, Windows process APIs, and the torture command-line contract. It passes through many switches without interpreting them.

Risks and test signals: there is a missing `break` after `case 'd'`, intentionally or accidentally falling through into switch pass-through cases. Command construction is unquoted and fixed-size. Successful fan-out is indicated by minimized child consoles, distinct `-f` target suffixes, and a shared `-g` log ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/Stress/Stress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/ResolveLocker.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/ResolveLocker.h

Purpose: public header for a locker attach/detach helper library used by the Windows torture environment.

Important APIs and types: `USER_OPTIONS` captures attach/detach settings, including Hesiod output, mount type, UNC behavior, host/user/password, disk drive, locker/submount names, path update flags, force dismount, and output controls. It declares `attach(USER_OPTIONS, int addtoPath, int addtoFront, char *appName)` and `detach(USER_OPTIONS, int DeleteFromPath, char *appName)`.

Control flow: none in this header; callers populate `USER_OPTIONS` and invoke the library.

State and persistence: state is passed by value in `USER_OPTIONS`. The implementation is expected to alter drive mappings, submounts, and optionally PATH entries.

Dependencies and integration: integrates with the MIT-style locker model referenced by `nb_Attach`, `nb_Detach`, and `nb_SetLocker`.

Risks and test signals: fixed-size credential/path buffers require bounded copying by the implementation. Test signals should include correct attach/detach behavior, expected drive/UNC mappings, and path update side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/ResolveLocker.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/common.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/common.h

Purpose: shared constants, data structures, and command metadata for the Windows torture harness.

Important APIs and types: defines path buffer sizes, file attribute bits, Open/Create option bits, command IDs from `CMD_CLOSE` through `CMD_NONAFS`, `NTSTATUS`, `pstring`, `fstring`, `file_info`, `cmd_struct`, `EXIT_STATUS`, `PARAMETERLIST`, and `FTABLE`. `cmd_names[]` maps command IDs to report names, disable-option names, and underlying API descriptions.

Control flow: no runtime control flow, but command IDs drive dispatch, timing, logging, and statistics aggregation across `nbio.c` and `output.c`.

State and persistence: `cmd_struct` stores count, error count, millisecond remainder, min/max/total seconds, sum of squares, and error time. `FTABLE` persists logical script handle to Win32 `HANDLE` mappings for each thread.

Dependencies and integration: included by `includes.h`, `proto.h`, `nbio.c`, and `output.c`. `CMD_MAX_CMD` must remain synchronized with `cmd_names` and command arrays.

Risks and test signals: `cmd_names` is defined `static` in the header, so every translation unit gets its own copy. Off-by-one errors are possible because loops run `i <= CMD_MAX_CMD` and `cmd_names` has a null sentinel. Statistics output consistency is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/includes.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/includes.h

Purpose: central portability include for the Windows torture code.

Important APIs and types: sets `_WIN32_WINNT` to `0x0500` if unset, includes Windows, CRT, process, I/O, and time headers, undefines `HAVE_KRB5`, maps `uint16` to `int` and `uint32` to `DWORD`, then includes `proto.h`.

Control flow: none.

State and persistence: none.

Dependencies and integration: intended as the first shared include for `nbio.c` and related torture sources. The mutual include relationship with `proto.h` is guarded by include guards.

Risks and test signals: the local typedef macros can conflict with modern fixed-width integer headers. `_WIN32_WINNT` locks feature availability to Windows 2000-era APIs unless overridden. Build success and prototype visibility are the useful checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/includes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/proto.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/torture/include/proto.h

Purpose: function prototype header for the scriptable `nb_*` operation layer.

Important APIs and functions: declares create/delete/copy/move/attach/detach/locker functions; low-level `nb_read`, `nb_write`, and `nb_close1`; logical command wrappers such as `nb_writex`, `nb_readx`, `nb_qpathinfo`, `nb_qfileinfo`, `nb_qfsinfo`, `nb_findfirst`, `nb_deltree`, `nb_cleanup`, and `nb_lock`.

Control flow: no implementation; this header establishes the callable surface for the torture parser/dispatcher.

State and persistence: none directly, but prototypes expose operations that mutate the filesystem, open-handle table, and command counters.

Dependencies and integration: includes `common.h` and `includes.h` for `HANDLE`, `DWORD`, `NTSTATUS`, and `ssize_t`.

Risks and test signals: the include cycle is tolerated by guards but is brittle. Prototype drift from `nbio.c` would produce compile warnings/errors; the declared `nb_lock` is currently stubbed out in implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/torture/include/proto.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/main.cpp -->
# sources/distributed-fs/openafs/src/WINNT/tests/winflock/main.cpp

Purpose: entry point and orchestration for the Win32 file-locking test program. It runs coordinated parent/child processes to validate sharing, byte-range locks, wait locks, reads, writes, unlocks, and lock escalation.

Important APIs and functions: `parse_cmd_line` handles `-d`, `-nr`, `-child`, `-p`, `-wS`, `-wP`, and `-wC`. `spawn_kids` starts a child copy of the executable. `run_tests` sequences test routines with parent/child synchronization macros. `create_sync_objects` and `free_sync_objects` manage named events and a log mutex. `_tmain` wires setup, child spawning, test execution, and cleanup.

Control flow: parent parses options, creates synchronization objects, starts a child, waits for child readiness, then both processes run the same test sequence. `PC_CALL` wraps routines that should run in coordinated parent/child phases; `PCINT_CALL` invokes tests that manage their own synchronization.

State and persistence: global booleans select test modes. Named local events `WinFLockChildEvent` and `WinFLockParentEvent` coordinate phases; `WinFLockLogFileMutex` serializes log blocks. Test files are created under `test_dir`.

Dependencies and integration: depends on `winflock.h`, `sync.cpp`, and `tests.cpp`, plus Win32 process/event/mutex APIs.

Risks and test signals: command-line construction uses a `MAX_PATH` buffer and does not quote `-d` values. `parse_cmd_line` documents `-wP <dir>` but does not consume a directory argument. Console `TEST:* PASS/FAILED` lines and synchronized parent/child log blocks are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/main.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/sync.cpp -->
# sources/distributed-fs/openafs/src/WINNT/tests/winflock/sync.cpp

Purpose: small synchronization and logging helper layer for the WinFLock parent/child test program.

Important APIs and functions: `_begin_log` and `_end_log` serialize log blocks with `mutex_logfile`. `_sync_begin_parent`, `_sync_end_parent`, `_sync_begin_child`, and `_sync_end_child` implement one-way phase handoffs using `event_child` and `event_parent`.

Control flow: parent-side sections begin logging immediately, then signal the child at end. Child-side sections wait for `event_child`, log and execute, then signal `event_parent`. The complementary macros in `winflock.h` wrap these functions with `if(!isChild)` or `if(isChild)` guards.

State and persistence: uses process-global `isChild`, event handles, and mutex handle. Logging is to `logfile`, currently `cout`.

Dependencies and integration: tightly coupled to `main.cpp` object creation and `tests.cpp` synchronization macros.

Risks and test signals: a missed event or unbalanced macro section can deadlock both processes. The absence of timeouts means hangs are diagnostic but not self-reporting. Correct output alternates `PARENT { ... }` and `CHILD { ... }` blocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/sync.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/tests.cpp -->
# sources/distributed-fs/openafs/src/WINNT/tests/winflock/tests.cpp

Purpose: implementation of Win32 file sharing and byte-range locking tests against a local or AFS-backed directory.

Important APIs and functions: `begin_tests` creates base and auxiliary files. `test_create` checks sharing violations and compatible sharing. `test_lock_prep` writes a 1 MiB deterministic page pattern. `testint_lock_excl_beof` and `testint_lock_excl_eeof` set and verify exclusive locks below and above EOF. `testint_lock_excl_rw_beof` checks read/write behavior in locked, unlocked, owned, and unowned regions. `testint_waitlock` uses overlapped `LockFileEx` to verify pending lock wakeups. `testint_unlock`, `testint_lock_escalation`, and `end_tests` clean up and validate unlock/escalation behavior.

Control flow: parent and child share the same file names and handles but execute different synchronized blocks. Page ranges are expressed with `PAGE_BEGIN`/`PAGE_LEN` at 4 KiB granularity. Many tests intentionally expect failure and treat `ERROR_SHARING_VIOLATION` or lock denial as pass conditions.

State and persistence: global `test_dir`, `fn_base`, `fn_aux`, `h_file_base`, and `h_file_aux` hold file state. Test files `FLTST000`, `FLTST001`, and `asyncft.dat` persist unless deleted externally.

Dependencies and integration: depends on `winflock.h` macros, `sync.cpp` handoffs, and Win32 `CreateFile`, `LockFile`, `LockFileEx`, `UnlockFile`, `UnlockFileEx`, `ReadFile`, `WriteFile`, and `FlushFileBuffers`.

Risks and test signals: some error handling logs warnings but returns success, so external parsing of `TEST:* FAILED` is more reliable than process exit alone. AFS redirector differences are surfaced through PASS/FAILED lines, last-error values, and deadlocks in wait-lock scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/tests.cpp -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/winflock.h -->
# sources/distributed-fs/openafs/src/WINNT/tests/winflock/winflock.h

Purpose: shared declarations and synchronization macros for the WinFLock test program.

Important APIs and types: includes Win32, TCHAR, iostream, assert, and `strsafe.h`; declares global test directory and synchronization handles; maps `logfile` to `cout`; declares all test functions; defines `PAGE_BEGIN` and `PAGE_LEN` for 4 KiB page ranges.

Control flow: macros `BEGINLOG`/`ENDLOG`, `SYNC_BEGIN_PARENT`/`SYNC_END_PARENT`, and `SYNC_BEGIN_CHILD`/`SYNC_END_CHILD` hide the event/mutex protocol implemented in `sync.cpp`.

State and persistence: no storage itself, but exposes shared globals defined in `main.cpp` and `tests.cpp`.

Dependencies and integration: included by all WinFLock translation units. Test function prototypes match the sequence in `run_tests`.

Risks and test signals: the synchronization macros rely on brace-style use and are easy to misuse. Because `logfile` is `cout`, mutex protection only serializes cooperating process output to the console stream.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/WINNT/tests/winflock/winflock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem.s -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_assem.s

Purpose: RS/6000 assembly helper file for AIX kernel integration.

Important APIs and functions: exports `get_toc`, which copies register 2 into return register 3 to expose the current TOC pointer, and `get_ret_addr`, which walks the caller stack frame to return the saved link register.

Control flow: each function is a short leaf routine followed by AIX traceback tags and descriptor csects.

State and persistence: no mutable state. It only observes processor registers and stack frame layout.

Dependencies and integration: used by `osi_config.c` during kernel import setup, especially `kluge_init`, which needs the TOC for `import_kvar`.

Risks and test signals: correctness depends on AIX calling conventions, stack frame layout, and descriptor format. Build/link success and successful kernel symbol import are the practical tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem32.s -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_assem32.s

Purpose: 32-bit variant of the AIX RS/6000 assembly helpers.

Important APIs and functions: exports `get_toc` and `get_ret_addr`, using `.long` descriptor entries for procedure descriptors and TOC pointers.

Control flow: `get_toc` returns r2; `get_ret_addr` loads the caller's saved stack pointer from r1 and then the caller's saved link register at offset 8.

State and persistence: no persistent state or side effects.

Dependencies and integration: linked into 32-bit AIX kernel/client builds that need TOC-aware import resolution.

Risks and test signals: tied to 32-bit AIX ABI assumptions. A wrong descriptor width would break calls before C code runs; successful module load and `kluge_init` import completion are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem32.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem64.s -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_assem64.s

Purpose: 64-bit variant of the AIX RS/6000 assembly helper routines.

Important APIs and functions: exports the same `get_toc` and `get_ret_addr` entry points as the generic/32-bit files, but uses `.llong` descriptor entries so function descriptors and TOC references are 64-bit wide.

Control flow: both routines are direct register/stack reads followed by branch return. The code path is intentionally minimal because it runs in kernel/module context.

State and persistence: none.

Dependencies and integration: consumed by 64-bit AIX builds of the OpenAFS kernel module, especially the dynamic kernel import code in `osi_config.c`.

Risks and test signals: relies on ABI-stable frame offsets and descriptor layout. Test signals are successful 64-bit link/load and correct import of kernel variables/functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_assem64.s -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_config.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_config.c

Purpose: AIX kernel module configuration and compatibility glue. It registers/unregisters the AFS GFS, pins code and locks, allocates the timeout callout table, initializes the OSI layer, and imports non-exported AIX kernel functions/variables through a "kluge" table.

Important APIs and functions: `afs_config` handles `CFG_INIT` and `CFG_TERM`; `kmem_alloc`, `kmem_free`, `VN_RELE`, and `VN_HOLD` provide common wrappers; `kluge_init` imports entries in `kfuncs` and `kvars`; wrappers such as `ufdalloc`, `fpalloc`, `ufdfree`, `ffree`, `iptovp`, `dev_ialloc`, `iget`, `iput`, `commit`, and debug lock wrappers call imported function pointers.

Control flow: on init, `afs_config` takes `AFS_GLOCK`, imports kernel symbols, pins the config routine, calls `gfsadd`, initializes `afs_callout_lock`, installs locked vnode ops, and calls `timeoutcf`. On termination it calls `gfsdel`, unpins resources where supported, and shrinks the callout table.

State and persistence: persistent kernel state includes `afs_gfs` registration, pinned lock storage, imported function pointers, imported kernel variables, and timeout table capacity.

Dependencies and integration: depends on `export.h` import helpers, `get_toc` assembly, AIX GFS/config APIs, timeout code, vnode ops, and global AFS locking.

Risks and test signals: symbol import is fragile across AIX kernel versions and 32/64-bit signatures. Failure modes are module load failure, bad function pointer calls, or leaked pinned resources. Test signals are successful `CFG_INIT`, mount availability, and clean `CFG_TERM`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_file.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_file.c

Purpose: AIX UFS cache-file access layer for OpenAFS disk cache operations.

Important APIs and functions: `osi_UFSOpen` opens a cache inode by device/inode and returns `struct osi_file`; `afs_osi_Stat` fetches size/mtime/atime; `osi_UFSClose` releases vnodes and may flush VM pages under page pressure; `osi_UFSTruncate` shrinks cache files; `afs_osi_Read` and `afs_osi_Write` call `gop_rdwr`; `osi_DisableAtimes` clears access-time updates; `afs_osi_MapStrategy` forwards buffer strategy calls; `shutdown_osifile` resets static credentials on cold shutdown.

Control flow: cache opens validate `cacheDiskType`, initialize a static credential, drop `AFS_GLOCK` around inode lookup, then store vnode/size/offset in `osi_file`. Reads and writes optionally seek by updating `afile->offset`, drop the global lock during VNOP I/O, and convert residuals to byte counts.

State and persistence: tracks static `afs_osi_cred`, `afs_osicred_initialized`, per-file vnode/offset/size/proc callback, and real UFS cache file contents.

Dependencies and integration: uses AIX inode helpers from `osi_inode.c`, `gop_rdwr` from `osi_misc.c`, VM helpers, AFS tracing/statistics, and global cache device/vfs state.

Risks and test signals: `osi_UFSOpen` panics on lookup failure; read retries mask transient `EFAULT`; write ENOSPC warns via AFS. Signals include cache read/write byte counts, trace events, ENOSPC warnings, and stable cache truncation behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_gcpags.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_gcpags.c

Purpose: AIX process-table traversal and credential extraction for garbage-collecting PAGs when `AFS_GCPAGS` is enabled.

Important APIs and functions: `afs_osi_TraverseProcTable` walks active process table entries and calls `afs_GCPAGs_perproc_func`. `afs_osi_proc2cred` maps another process's user area into the current address space and returns a static copy of its credential.

Control flow: traversal checks `afs_gcpags_procsize`, locks `proc_tbl_lock` on pre-AIX 5.1, skips unused/exiting states, validates PID index and nice range, then visits each process. Credential extraction locks process-private state, attaches the user area with `vm_att`/`xmattach`, copies `U_cred`, detaches, and returns the static credential.

State and persistence: updates global `afs_gcpags` error state on sanity failures. `afs_osi_proc2cred` uses a static `afs_ucred_t` overwritten on each successful call.

Dependencies and integration: depends on AIX `struct proc` layout, process locks, address-space APIs, and the OpenAFS PAG GC callback.

Risks and test signals: binary compatibility is fragile because process struct size/layout can differ from compile-time headers. The static credential return is not reentrant. Signals include successful PAG cleanup without PID/nice sanity errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_gcpags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_groups.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_groups.c

Purpose: AIX PAG and group-list manipulation for OpenAFS authentication state.

Important APIs and functions: legacy `setgroups` wrapper preserves an existing PAG across `osetgroups`; `setpag` creates or installs a PAG; AIX 5.1 `do_setpag` uses `kcred_setpag`; pre-5.1 helpers `afs_getgroups`, `copy_to_cred`, and `afs_setgroups` encode the PAG into the first two group IDs.

Control flow: `setpag` generates a PAG if requested, ensures room for two PAG groups on legacy AIX, stores `*newpag`, then either calls `do_setpag` or rewrites group arrays. `change_parent` controls whether the existing credential is modified or a duplicated current credential is installed with `crset`.

State and persistence: mutates process credentials and optionally shared parent credentials. On failure it sets user error with `setuerror`.

Dependencies and integration: uses OpenAFS PAG encoding helpers, AIX credential functions (`crref`, `crdup`, `crset`, `crfree`), and kernel PAG APIs on AIX 5.1.

Risks and test signals: group-list capacity can return `E2BIG`; parent credential sharing is subtle; AIX 5.1 errors are recovered from `getuerror`. Signals are successful `pagsh`/`klog -setpag`, retained PAG after `setgroups`, and correct token visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_groups.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_inode.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_inode.c

Purpose: AIX inode support for OpenAFS server/salvager style inode operations and cache inode lookup.

Important APIs and functions: `devtovfs` locates a mounted JFS vfs by device; `igetinode` validates and returns an inode/vnode; syscall wrappers `icreate`, `iopen`, and `iincdec` are generated through `SYSENT`; convenience `iinc` and `idec` adjust link counts.

Control flow: `SYSENT` wraps syscall bodies in `setjmpx`/`clrjmpx` and converts kernel exceptions to `uerror`. `igetinode` locates a vfs, rejects inode 0, locks JFS icache, calls imported `iget`, verifies nonzero link count and regular-file mode, and returns an associated vnode. `icreate` requires superuser, allocates a regular inode, stamps `VICEMAGIC` and vice fields, then releases the vnode. `iopen` creates a file descriptor over the vnode and opens it. `iincdec` validates `VICEMAGIC` and vicep1 before changing `i_nlink` and committing.

State and persistence: persists vice metadata in reserved inode fields, changes inode link counts, and records diagnostic globals `IGI_error`, `IGI_inode`, `IGI_nlink`, and `IGI_mode`.

Dependencies and integration: uses imported JFS functions from `osi_config.c`, macros from `osi_inode.h`, AIX vnode/file descriptor APIs, and superuser checks.

Risks and test signals: inode lock field offsets are version-sensitive; bad inode 0 handling could panic AIX; direct link-count mutation requires exact `VICEMAGIC` semantics. Signals include successful salvager/server inode syscalls and no `BAD_IGET` diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_inode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_inode.h -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_inode.h

Purpose: AIX inode metadata definitions needed by OpenAFS servers and salvager code.

Important APIs and types: defines `BAD_IGET`, `VICEMAGIC`, accessors `DI_VICEP3` and `I_VICE3`, maps dinode reserved fields to `di_vicemagic` and `di_vicep1` through `di_vicep4`, maps in-core inode fields to the dinode fields, and provides test/clear macros for vice magic.

Control flow: none.

State and persistence: defines how OpenAFS stores volume/file identity metadata in AIX JFS reserved inode fields. These fields are persistent on disk.

Dependencies and integration: consumed by `osi_inode.c` and any AIX code that interprets AFS special inodes.

Risks and test signals: reserved field usage is filesystem-layout sensitive; the comment notes `rsvrd[4]` is used for large-file size, yet `di_vicep4` maps there. Salvager consistency and correct `VICEMAGIC` detection are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_inode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_machdep.h -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_machdep.h

Purpose: AIX machine-dependent OSI definitions that adapt common OpenAFS kernel code to AIX types, locks, time, lookup, credentials, and process identity.

Important APIs and macros: defines `osi_ThreadUnique`, `afs_hz`, `osi_Time`, `afs_ucred_t`, `afs_proc_t`, `afs_bufferpages`, lookup macros, `get_ulimit`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `osi_procname`, and inline `osi_GetTime`.

Control flow: global lock macros assert ownership invariants before locking/unlocking and panic on misuse. `osi_GetTime` calls `curtime` and converts nanoseconds to microseconds.

State and persistence: no persistent storage, but lock macros protect global OpenAFS kernel state. `osi_Time` reads AIX `time`.

Dependencies and integration: included indirectly by `afs_osi.h`. Depends on AIX lock, sleep, time, and ulimit headers.

Risks and test signals: lock ownership assertions can panic if common code violates AIX expectations. `osi_procname` intentionally returns an empty string. Signals are successful lock initialization and absence of GLOCK ownership panics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_machdep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_misc.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_misc.c

Purpose: miscellaneous AIX OS interface helpers for GFS initialization, vnode I/O wrapping, vnode/gnode release, and superuser checks.

Important APIs and functions: `Afs_init` registers AFS VM buffer strategy with `vm_mount`; `gop_rdwr` builds a one-element `uio` and calls `VNOP_RDWR`; `aix_gnode_rele` unlinks an AFS vnode from its vfs list and frees its allocated gnode; `afs_suser` wraps AIX `suser` without setting errno.

Control flow: `gop_rdwr` zeroes `uio`/`iovec`, sets offset, segment flag, residual, and read/write mode, calls the AIX vnode op with `afs_osi_cred`, then reports residual back to the caller. `aix_gnode_rele` patches neighboring vfs-list links before freeing the gnode.

State and persistence: affects VM registration and in-memory vnode/gnode list membership. Does not directly persist data.

Dependencies and integration: used by `osi_file.c`, `osi_vm.c`, AIX vnode operations, and common AFS superuser checks.

Risks and test signals: `gop_rdwr` offset semantics are documented as safe only for regular non-append cases. Incorrect vnode unlinking can corrupt vfs vnode lists. Signals include stable cache I/O and clean vcache reclamation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_prototypes.h -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_prototypes.h

Purpose: AIX OSI prototype header for declarations not already covered elsewhere.

Important APIs and functions: declares `afs_aix_SetupPagRefCount(void)` under the `osi_groups.c` comment.

Control flow: none.

State and persistence: none in this header.

Dependencies and integration: included by AIX-specific OpenAFS files that need the PAG reference-count setup declaration.

Risks and test signals: the referenced function is not present in the listed `osi_groups.c`, so either it is compiled conditionally elsewhere or this header is stale. Build/link coverage is the key signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_prototypes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_sleep.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_sleep.c

Purpose: AIX sleep, timed sleep, wait-handle, and wakeup implementation for OpenAFS kernel code.

Important APIs and functions: `afs_osi_InitWaitHandle`, `afs_osi_CancelWait`, `afs_osi_Wait`, `afs_osi_Sleep`, `afs_osi_SleepSig`, `afs_osi_TimedSleep`, and `afs_osi_Wakeup`. `afs_getevent` maintains a hash table from event addresses to AIX event objects. `AfsWaitHack` clears timed waits from timer callbacks.

Control flow: waiters obtain an event record under `AFS_GLOCK`, assert wait on its condition, drop the global lock, block, then reacquire the lock. Timed sleeps allocate a `trb`, start it, block, stop/free it, and return `EINTR` only on interruption. Wakeup increments a sequence number and calls `e_wakeup` when waiters exist.

State and persistence: persistent in-kernel state is `afs_evhasht`, event refcounts, event sequence counters, and allocated pinned event records.

Dependencies and integration: uses AIX event and timer APIs, `pinned_heap`, global AFS lock assertions, and wait handles from common OpenAFS code.

Risks and test signals: `afs_getevent` reuses zero-refcount records but never frees them; timer allocation failure panics. Correct signals are absence of lost wakeups, expected timeout behavior, and no GLOCK misuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_sleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_timeout.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_timeout.c

Purpose: AIX compatibility implementation of BSD-style `timeout`, `untimeout`, and callout-table sizing using AIX timer request blocks.

Important APIs and functions: `timeout` schedules or replaces a callback; `untimeout` cancels a pending callback; `timeout_end` is the TRB callback trampoline; `timeoutcf` grows or shrinks the callout table.

Control flow: `timeout` converts ticks to seconds/nanoseconds, locks `afs_callout_lock` at interrupt priority, finds an existing matching callback or a free slot, stops any active TRB, initializes it, and starts it. `timeout_end` clears the slot under lock and then invokes the original function. `timeoutcf` allocates/frees `struct tos` plus `trb` entries, removing only inactive slots when shrinking.

State and persistence: in-memory `afs_callo` linked list tracks callout entries; each `tos` owns one `trb`, callback identity, and temporary type/p1 fields.

Dependencies and integration: initialized by `osi_config.c` via `timeoutcf(AFS_CALLOUT_TBL_SIZE)` and protected by `afs_callout_lock`.

Risks and test signals: table exhaustion asserts instead of recovering; cancellation loops retry when `tstop` races with active timers. Signals include successful callback execution/cancellation and clean table shrink during module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_timeout.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vcache.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_vcache.c

Purpose: AIX-specific vcache/vnode allocation, population, attachment, eviction, and hold support.

Important APIs and functions: `osi_TryEvictVCache` flushes eligible vcaches; `osi_NewVnode` allocates and optionally pins a `struct vcache`; `osi_PrePopulateVCache` clears it and allocates a companion `gnode`; `osi_AttachVnode` is a no-op hook; `osi_PostPopulateVCache` wires vnode ops, vfs, type, vfs list links, and gnode backpointer; `osi_vnhold` calls `VN_HOLD`.

Control flow: vcache allocation and population are staged so common code can fill AFS fields between pre/post hooks. Eviction requires zero references, no opens, and not `CUnlinkedDel`, then delegates to `afs_FlushVCache`.

State and persistence: mutates in-memory vcache, vnode, gnode, and `afs_globalVFS->vfs_vnodes` list membership. No disk state.

Dependencies and integration: uses `afs_ops` from AIX vnode operations, `afs_globalVFS` from `osi_vfsops.c`, and AIX pinning where available.

Risks and test signals: list insertion must be balanced by `aix_gnode_rele`; allocation failures return NULL. Signals include stable vnode lookup/reclamation and no corrupted vfs vnode chain.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vfs.h -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_vfs.h

Purpose: AIX vnode/vfs compatibility macro header for common OpenAFS code.

Important APIs and macros: maps access bits (`VREAD`, `VEXEC`, `VWRITE`), mode bits (`VSUID`, `VSGID`, `VSVTX`), copy helpers, block sizes, vnode flags, append mode, `VTOI`, `v_op`, `iunlock`, buffer function declarations, buffer field aliases, and `dbtob`. It also defines `enum vcexcl` when needed.

Control flow: none.

State and persistence: none directly.

Dependencies and integration: included by AIX vnode/misc code that expects more portable vnode names.

Risks and test signals: macro aliases must match AIX headers for the target release. Mismatches show up as compile failures or incorrect vnode operation dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vfsops.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_vfsops.c

Purpose: AIX VFS operation table and mount/root/stat/vget behavior for the AFS filesystem.

Important APIs and functions: `afs_mount`, `afs_unmount`, `afs_root_nolock`, `afs_root`, `afs_statfs`, `afs_sync`, `afs_vget`, `afs_aix_badop`, and exported `Afs_vfsops`.

Control flow: mount takes the AFS global lock if needed, rejects remounts and file-over-file mounts, initializes vfs fields/fsid, marks remote mount data, attempts root vnode setup, and registers iauth when configured. Root lookup initializes a request, checks AFS initialization, gets the root vcache, marks it `VROOT`, stores it in `afs_globalVp`, and assigns `vfs_mntd`. Unmount clears `afs_globalVFS` and calls cold shutdown. `afs_vget` converts a fileid to a vcache through `afs_osi_vget`.

State and persistence: `afs_globalVFS` and `afs_globalVp` hold process-wide mount/root state. Statfs returns fake free-space values, not persisted filesystem capacity.

Dependencies and integration: installed by `osi_config.c`, uses common AFS request/vcache/check-code paths, AIX VFS structs, and optional NFS exporter/iauth integration.

Risks and test signals: remount is intentionally rejected; root vcache caching must handle initialization races; statfs reports synthetic capacity. Signals include successful `/afs` mount/root lookup, `vget` by fileid, and clean cold unmount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vfsops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vm.c -->
# sources/distributed-fs/openafs/src/afs/AIX/osi_vm.c

Purpose: AIX VM/page-cache integration for OpenAFS vcache lifecycle, storeback, flush, smush, callback revocation, and truncate handling.

Important APIs and functions: `osi_VM_FlushVCache`, `osi_VM_StoreAllSegments`, `osi_VM_TryToSmush`, `osi_VM_FlushPages`, and `osi_VM_Truncate`.

Control flow: flush refuses busy vcaches, deletes any VM segment with `vms_delete`, releases credentials, and frees the AIX gnode. Storeback drops the vcache write lock and AFS global lock while calling `vm_writep` and `vms_iowait`, then reacquires locks and clears `CCore` fake-close state if present. Smush/flush/truncate call AIX VM page flush/release APIs across the file's segment range.

State and persistence: mutates `avc->segid`, `avc->vmh`, `avc->credp`, `avc->opens`, `avc->execsOrWriters`, `avc->linkData`, and vnode/gnode resources. Persistent data impact is indirect through page writeback or discarded dirty pages.

Dependencies and integration: called by common cache, flush, callback, and truncate paths; uses AIX VM APIs and `aix_gnode_rele`.

Risks and test signals: comments acknowledge consistency compromise around storeback to avoid AIX panics under load. Signals include no busy-vcache eviction, successful page writeback before store, and correct EOF truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/afs/AIX/osi_vm.c -->
