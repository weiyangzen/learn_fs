# Research: subset-b-009217

This grouped report covers the requested Connectathon Cthon04 lock/special/tools files plus the Filebench ASLR build entries. Each source file is wrapped with the reconciliation markers required for splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/lock/tlock.c -->
# sources/test-tools/cthon04/lock/tlock.c

## Purpose
`tlock.c` is the Connectathon record-locking stress test. It exercises POSIX `fcntl()` byte-range locks or System V `lockf()` locks across a synchronized parent/child pair, including whole-file locks, single-byte ranges, end-of-file/large-offset ranges, lock splitting, process death, close semantics, optional mmap interaction, optional mandatory locking, CIFS exclusions, and lock/I/O rate measurements.

## Important APIs, Types, and Functions
Important entry points are `main()`, `initialize()`, `runtests()`, `test1()` through `test15()`, `test()`, `lockf2fcntl()`, `report()`, `read_testfile()`, `write_testfile()`, `rate()`, and `iorate()`. Compile-time switches include `USE_LOCKF`, `LARGE_LOCKS`, `LF_SUMMIT`, `MMAP`, `MACOSX`, and protocol/errno conditionals. Shared state includes `maxeof`, `testfile`, `testfd`, synchronization pipes, parent/child PIDs, counters, and error expectation globals.

## Control Flow and State
`main()` parses options, computes the test file path, creates three pipes, forks one child, and runs the selected test set for each pass. Tests alternate control between parent and child with one-byte pipe messages so one process can establish locks while the other probes, blocks, writes, kills a subchild, or verifies release behavior. The `test()` wrapper converts lock requests to either `lockf()` or `fcntl()` calls and records PASS/WARN/FATAL outcomes.

## Persistence and Dependencies
Persistent effects are limited to temporary `lockfile<pid>` files, child processes, pipes, optional memory mappings, and timing counters; `testexit()` attempts to unlink the file and kill/wait for the peer on failure. Dependencies: standard C/POSIX headers, `fcntl`, `lockf`, `lseek`, `ftruncate`, `fork`, `kill`, `wait`, `times`, `mmap` when enabled, NFS protocol-version assumptions, and the lock test Makefile.

## Integration Points, Risks, and Test Signals
Integration is through `lock/runtests` and the top-level Cthon lock suite. Risks are high around timing sleeps, platform-specific errno expectations (`EACCES` versus `EAGAIN`, `EOVERFLOW` versus `EINVAL`), destructive cleanup if `filepath` is wrong, unguarded pipe/fork failures, and mandatory locking assumptions that many modern systems ignore. Test signals are zero failures over all selected passes, expected warnings only for documented semantics differences, successful parent/child exclusion data checks, rate output, and clean unlink/child termination.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/lock/tlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/runcthon -->
# sources/test-tools/cthon04/runcthon

## Purpose
`runcthon` is a Bash orchestration script for running the Connectathon basic/general/special/lock tests against many NFS mount permutations. It mounts per-version/per-protocol directories, launches `./server` test runs in the background, captures logs under `/tmp`, waits between batches, and provides helper modes to create server-side directories or unmount prior runs.

## Important APIs, Types, and Functions
Important shell functions are `runtests()`, `umountall()`, and `mkdirs()`. Configuration variables include `SRV`, `serverdir`, `privatemnts`, `noudp`, `dokrb5`, `onlykrb5`, `nov4`, `dov41`, `dov42`, `nov2`, `onlyv3`, `onlyv4`, `minver`, `fsc`, `rdma`, `rdmaif`, `onlyrdma`, `nolcks`, and `port`.

## Control Flow and State
Option parsing sets feature flags, then loops over test letters `b g s l` unless locks are disabled. For each selected test it builds `mount` options for NFSv2/v3/v4/v4.1/v4.2, UDP/TCP/RDMA, optional Kerberos flavors, cachefiles (`fsc`), minor-version selection, and custom ports. Each invocation creates a mountpoint, runs `./server` in a subshell, logs failure output, unmounts if still mounted, and backgrounds the run before a batch `wait`.

## Persistence and Dependencies
State persists in created `/mnt` or `/mnt/<server>` mount directories, server-side `nfsv*` export directories, `/tmp/nfsv*` logs, live NFS mounts, and background `server` processes. Dependencies: Bash, `/proc/mounts`, `sudo umount`, `grep`, `awk`, `date`, `pkill`, local `./server`, NFS client mount options, RDMA port 20049 conventions, and external server export setup.

## Integration Points, Risks, and Test Signals
Integration is the highest-level Cthon launcher. Risks include unquoted variables, broad `pkill runcthon`/`pkill server` traps, a likely typo in `mkdirs()` using `$proto` while constructing `protos` for RDMA, racey log names, and root/sudo/mount privileges. Test signals are `Done` timestamps after each batch, absence of `.error` logs, no lingering `/proc/mounts` entries, and successful runs for every enabled protocol/security tuple.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/runcthon -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/Makefile -->
# sources/test-tools/cthon04/special/Makefile

## Purpose
This Makefile builds and distributes the Connectathon special-case filesystem test programs. It covers open-unlink/rename/chmod behavior, duplicate requests, exclusive create, negative seek, sparse files, truncate, idempotency, stat timing, directory cookies, large files, and free-space truncation.

## Important APIs, Types, and Functions
Key variables are `TESTS`, `DOSRUNFILES`, `DOSBUILDFILES`, `DESTDIR`, `COPYFILES`, `INCLUDES`, `SUBRS`, and `DEPS`. Targets include one executable rule for each C source, `../basic/subr.o`, `all`, `lint`, `clean`, `copy`, and `dist`.

## Control Flow and State
`all` builds every program and ensures `runtests` is executable. Most rules compile `$@.c` with inherited `$(CC) $(CFLAGS) $(LIBS)` from `../tests.init`; programs that use timing/tree helpers link `../basic/subr.o`. Distribution targets copy either binaries plus run files or full sources plus DOS/console build files into `DESTDIR`.

## Persistence and Dependencies
It persists compiler outputs, executable test binaries, and copied distribution trees; `clean` removes objects, test binaries, and several scratch names. Dependencies: `../tests.init`, `../tests.h`, `../basic/subr.o`, standard make, C compiler/libraries, and DOS/Win build artifact directories.

## Integration Points, Risks, and Test Signals
Integration is with `special/runtests` and top-level Connectathon builds. Risks include assuming source and binary names match, `DESTDIR=/no/such/path` unless overridden, copy/dist commands that remove files at the destination, no dependency tracking beyond the shared header/subr object, and platform-specific tests that compile but skip at runtime. Test signals are successful `make all`, executable `runtests`, clean `make copy DESTDIR=...`, and expected no-op skips for unsupported platform features.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/bigfile.c -->
# sources/test-tools/cthon04/special/bigfile.c

## Purpose
`bigfile.c` writes, syncs, closes, reopens, and verifies a large file to expose NFS and filesystem failures around dirty cache pressure, large-range commits, stale attributes, and ENOSPC/EDQUOT propagation. When compiled with `MMAP`, it repeats the exercise through shared mappings.

## Important APIs, Types, and Functions
Important functions are `main()`, `write_read()`, optional `write_read_mmap()`, `verify()`, `dump_buf()`, `io_error()`, and `testval()`. Runtime state is `file_size`, `filename`, `buffer_size`, and optional `pagesize`.

## Control Flow and State
`main()` accepts `-s size_in_MB`, creates/truncates the target, calls buffered I/O verification, optionally calls mmap verification, and unlinks the file. `write_read()` fills each 8192-byte buffer with a deterministic byte pattern, calls `fsync()`, closes/reopens, seeks every buffer offset, and verifies each block. The mmap path truncates, maps the whole file writable, fills page-sized regions, `msync()`s, unmaps, then maps each page read-only for verification.

## Persistence and Dependencies
Persistent state is the test file until final unlink or until non-space errors intentionally leave it for inspection; space/quota failures unlink before exit. Dependencies: POSIX file I/O, `fsync`, `ftruncate`, `mmap`/`msync`/`munmap` when enabled, `errno`, and `../tests.h` for legacy prototypes/macros.

## Integration Points, Risks, and Test Signals
Integration is the special large-file test. Risks include truncating/removing the named file, using `long`/`int` counts for large sizes, only testing whole buffer/page multiples, full-file mappings that may exceed address space, and treating ENOSPC as a warning while still returning failure. Test signals are no verify dump, successful reopen reads, clean unlink, and meaningful Warning/Error distinction on storage exhaustion.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/bigfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/bigfile2.c -->
# sources/test-tools/cthon04/special/bigfile2.c

## Purpose
`bigfile2.c` targets sparse-file behavior around the 2 GiB and 4 GiB offset boundaries. It writes five bytes spanning each boundary and checks that file size and data readback remain correct with either native 64-bit offsets or Large File Summit transitional APIs.

## Important APIs, Types, and Functions
Important macros are `_LARGEFILE64_SOURCE`, `HIGH_WORD()`, `LOW_WORD()`, `LSEEK`, `FSTAT`, and the `offset64`/`stat_info` typedefs. Main logic is in `main()` and `check_around()`.

## Control Flow and State
If neither `NATIVE64` nor `_LFS64_LARGEFILE` is available, `main()` reports a skip and exits success. Otherwise it opens the file with `O_SYNC` and `O_LARGEFILE` when needed, checks around `0x80000000`, truncates to zero, then checks around `0x100000000`. `check_around()` seeks to `where - 2`, writes bytes `0` through `4`, verifies `st_size` after every byte, seeks back, and verifies each byte value.

## Persistence and Dependencies
Persistent state is a sparse test file that is unlinked at normal completion; failures may leave a huge sparse file name on disk. Dependencies: Large-file libc interfaces, `open`, `lseek64`/`lseek`, `fstat64`/`fstat`, `ftruncate`, `O_SYNC`, and `../tests.h`.

## Integration Points, Risks, and Test Signals
Integration is the special large-offset suite. Risks include platform macro detection drift, opening a named file destructively, sparse allocation surprises on filesystems without holes, and printf formatting that manually splits offsets. Test signals are skip output on 32-bit-only platforms, correct `st_size` at both boundaries, byte readback without mismatch, and final unlink.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/bigfile2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/dupreq.mak -->
# sources/test-tools/cthon04/special/console/dupreq.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `DUPREQ.exe` variant for the Connectathon special `duplicate request/link-unlink test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\DUPREQ.C` source plus a prebuilt `SUBR.OBJ` helper.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/dupreq.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/excltest.mak -->
# sources/test-tools/cthon04/special/console/excltest.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `EXCLTEST.exe` variant for the Connectathon special `exclusive create test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\EXCLTEST.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/excltest.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/fstat.mak -->
# sources/test-tools/cthon04/special/console/fstat.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `FSTAT.exe` variant for the Connectathon special `filesystem file-count statfs probe`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\FSTAT.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/fstat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/holey.mak -->
# sources/test-tools/cthon04/special/console/holey.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `HOLEY.exe` variant for the Connectathon special `sparse hole readback test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\HOLEY.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/holey.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/negseek.mak -->
# sources/test-tools/cthon04/special/console/negseek.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `NEGSEEK.exe` variant for the Connectathon special `negative seek rejection test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\NEGSEEK.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/negseek.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/nfsidem.mak -->
# sources/test-tools/cthon04/special/console/nfsidem.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `NFSIDEM.exe` variant for the Connectathon special `NFS idempotency sequence`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\NFSIDEM.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/nfsidem.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/nstat.mak -->
# sources/test-tools/cthon04/special/console/nstat.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `NSTAT.exe` variant for the Connectathon special `single-file stat timing test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\NSTAT.C` source plus a prebuilt `SUBR.OBJ` helper.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/nstat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_chmod.mak -->
# sources/test-tools/cthon04/special/console/op_chmod.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `OP_CHMOD.exe` variant for the Connectathon special `open-file-after-chmod test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\OP_CHMOD.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_chmod.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_ren.mak -->
# sources/test-tools/cthon04/special/console/op_ren.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `OP_REN.exe` variant for the Connectathon special `open-file-after-rename-over-target test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\OP_REN.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_ren.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_unlk.mak -->
# sources/test-tools/cthon04/special/console/op_unlk.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `OP_UNLK.exe` variant for the Connectathon special `open-file-after-unlink test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\OP_UNLK.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/op_unlk.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/rename.mak -->
# sources/test-tools/cthon04/special/console/rename.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `RENAME.exe` variant for the Connectathon special `rename loop test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\RENAME.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/rename.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/rewind.mak -->
# sources/test-tools/cthon04/special/console/rewind.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `REWIND.exe` variant for the Connectathon special `rewind/truncate offset test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\REWIND.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/rewind.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/stat.mak -->
# sources/test-tools/cthon04/special/console/stat.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `STAT.exe` variant for the Connectathon special `recursive stat traversal`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\STAT.C` source plus a prebuilt `SUBR.OBJ` helper.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/stat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/stat2.mak -->
# sources/test-tools/cthon04/special/console/stat2.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `STAT2.exe` variant for the Connectathon special `many-files repeated stat benchmark`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\STAT2.C` source plus a prebuilt `SUBR.OBJ` helper.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/stat2.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/touchn.mak -->
# sources/test-tools/cthon04/special/console/touchn.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `TOUCHN.exe` variant for the Connectathon special `many-file create workload`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\TOUCHN.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/touchn.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/console/truncate.mak -->
# sources/test-tools/cthon04/special/console/truncate.mak

## Purpose
This Visual C++ NMAKE project builds the Win32 console `TRUNCATE.exe` variant for the Connectathon special `ftruncate extension test`.

## Important APIs, Types, and Functions
Important build macros include `CFG`, `OUTDIR`, `INTDIR`, `CPP_PROJ`, `BSC32_FLAGS`, `LINK32_FLAGS`, and `LINK32_OBJS`. It supports `Win32 Release` and `Win32 Debug`, emits `.exe`, `.pdb`, `.bsc`, `.obj`, and `.sbr` artifacts, and compiles the corresponding `..\TRUNCATE.C` source.

## Control Flow and State
The file defaults `CFG` to `Win32 Debug`, rejects unknown configurations, creates the selected output directory, compiles the C source with `_CONSOLE` and either `NDEBUG` or `_DEBUG`, builds browse information with `bscmake`, and links against the standard Win32 system libraries.

## Persistence and Dependencies
Persistent build state lives under `WinRel` or `WinDebug` and includes intermediate browser/debug files as well as the executable. Dependencies: Microsoft Visual C++ 2-era NMAKE syntax, `cl.exe`, `link.exe`, `bscmake.exe`, standard Win32 libraries, relative source paths, and in a few projects a previously built `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy Windows console builds shipped with the Cthon special tests. Risks include absolute historical source paths in some `SOURCE=` records, stale generated-project flags, no modern dependency discovery, case-sensitive path issues outside Windows, and missing `SUBR.OBJ` for projects that link helper code. Test signals are successful Debug/Release executable and `.bsc` generation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/console/truncate.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/dupreq.mak -->
# sources/test-tools/cthon04/special/dos/dupreq.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `DUPREQ.EXE` variant for the Connectathon special `duplicate request/link-unlink test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=DUPREQ`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\DUPREQ.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/dupreq.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/excltest.mak -->
# sources/test-tools/cthon04/special/dos/excltest.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `EXCLTEST.EXE` variant for the Connectathon special `exclusive create test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=EXCLTEST`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\EXCLTEST.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/excltest.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/fstat.mak -->
# sources/test-tools/cthon04/special/dos/fstat.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `FSTAT.EXE` variant for the Connectathon special `filesystem file-count statfs probe`.

## Important APIs, Types, and Functions
Important macros include `PROJ=FSTAT`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\FSTAT.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/fstat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/holey.mak -->
# sources/test-tools/cthon04/special/dos/holey.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `HOLEY.EXE` variant for the Connectathon special `sparse hole readback test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=HOLEY`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\HOLEY.C`, and a response-file link rule. The configured debug stack is `10240` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/holey.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/negseek.mak -->
# sources/test-tools/cthon04/special/dos/negseek.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `NEGSEEK.EXE` variant for the Connectathon special `negative seek rejection test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=NEGSEEK`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\NEGSEEK.C`, and a response-file link rule. The configured debug stack is `10240` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/negseek.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/nfsidem.mak -->
# sources/test-tools/cthon04/special/dos/nfsidem.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `NFSIDEM.EXE` variant for the Connectathon special `NFS idempotency sequence`.

## Important APIs, Types, and Functions
Important macros include `PROJ=NFSIDEM`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\NFSIDEM.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/nfsidem.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/nstat.mak -->
# sources/test-tools/cthon04/special/dos/nstat.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `NSTAT.EXE` variant for the Connectathon special `single-file stat timing test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=NSTAT`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\NSTAT.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/nstat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_chmod.mak -->
# sources/test-tools/cthon04/special/dos/op_chmod.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `OP_CHMOD.EXE` variant for the Connectathon special `open-file-after-chmod test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=OP_CHMOD`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\OP_CHMOD.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_chmod.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_ren.mak -->
# sources/test-tools/cthon04/special/dos/op_ren.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `OP_REN.EXE` variant for the Connectathon special `open-file-after-rename-over-target test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=OP_REN`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\OP_REN.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_ren.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_unlk.mak -->
# sources/test-tools/cthon04/special/dos/op_unlk.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `OP_UNLK.EXE` variant for the Connectathon special `open-file-after-unlink test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=OP_UNLK`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\OP_UNLK.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/op_unlk.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/rename.mak -->
# sources/test-tools/cthon04/special/dos/rename.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `RENAME.EXE` variant for the Connectathon special `rename loop test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=RENAME`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\RENAME.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/rename.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/rewind.mak -->
# sources/test-tools/cthon04/special/dos/rewind.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `REWIND.EXE` variant for the Connectathon special `rewind/truncate offset test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=REWIND`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\REWIND.C`, and a response-file link rule. The configured debug stack is `10240` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/rewind.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/stat.mak -->
# sources/test-tools/cthon04/special/dos/stat.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `STAT.EXE` variant for the Connectathon special `recursive stat traversal`.

## Important APIs, Types, and Functions
Important macros include `PROJ=STAT`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\STAT.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/stat.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/stat2.mak -->
# sources/test-tools/cthon04/special/dos/stat2.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `STAT2.EXE` variant for the Connectathon special `many-files repeated stat benchmark`.

## Important APIs, Types, and Functions
Important macros include `PROJ=STAT2`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\STAT2.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/stat2.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/touchn.mak -->
# sources/test-tools/cthon04/special/dos/touchn.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `TOUCHN.EXE` variant for the Connectathon special `many-file create workload`.

## Important APIs, Types, and Functions
Important macros include `PROJ=TOUCHN`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\TOUCHN.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/touchn.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/truncate.mak -->
# sources/test-tools/cthon04/special/dos/truncate.mak

## Purpose
This external Microsoft C/NMAKE DOS makefile builds the DOS `TRUNCATE.EXE` variant for the Connectathon special `ftruncate extension test`.

## Important APIs, Types, and Functions
Important macros include `PROJ=TRUNCATE`, `DEBUG`, `CFLAGS_D_DEXE`, `CFLAGS_R_DEXE`, `LFLAGS_*`, `LIBS_*`, `SBRS`, object rules for `..\TRUNCATE.C`, and a response-file link rule. The configured debug stack is `5120` bytes.

## Control Flow and State
The makefile selects debug or release compiler/link flags from `DEBUG`, removes stale `MSVC.BND`, compiles the source with `_DOS` and `DOS` defines, writes a `.CRF` response file, links against `oldnames` and `mlibce`, and optionally builds browser data with `bscmake`.

## Persistence and Dependencies
Persistent state includes `.OBJ`, `.SBR`, `.PDB`, `.CRF`, `.EXE`, and `.BSC` files in the DOS build directory. Dependencies: 16-bit/early Microsoft C tooling (`cl`, `link`, `bscmake`), DOS memory model flags, `..\tests.h`, `..\unixdos.h`, local runtime libraries under `..\..\lib`/`include`, and sometimes prebuilt or locally compiled `SUBR.OBJ`.

## Integration Points, Risks, and Test Signals
Integration is for legacy DOS distribution builds. Risks include obsolete `/AM` and `/G2` flags, hard-coded library paths, response-file fragility, case/path assumptions, and tests whose Unix semantics are skipped or altered on DOS. Test signals are a produced `.EXE` plus browse file and successful `run` target when the test is executable on DOS.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dos/truncate.mak -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/dupreq.c -->
# sources/test-tools/cthon04/special/dupreq.c

## Purpose
checks duplicate/lost replies for non-idempotent create/link/unlink sequences by repeatedly creating `name1`, hard-linking `name2`, then unlinking both names.

## Important APIs, Types, and Functions
`main()` parses `count name`, uses `creat()`, `link()`, `unlink()`, failure counters, and DOS/Win skip logic.

## Control Flow and State
A countdown loop performs create, link, unlink secondary, unlink primary, increments per-operation counters, and reports aggregate failures without aborting each iteration.

## Persistence and Dependencies
temporary `<name>1` and `<name>2` files are created and removed each pass. Dependencies: Unix hard links, POSIX file creation/unlink, and optional DOS/Win exclusion.

## Integration Points, Risks, and Test Signals
It integrates with the special idempotency tests. Risks are name collisions and unsupported hard links; signals are zero bad create/link/unlink counts.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/dupreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/excltest.c -->
# sources/test-tools/cthon04/special/excltest.c

## Purpose
tests whether `O_CREAT | O_EXCL` rejects duplicate creation after the first successful open.

## Important APIs, Types, and Functions
`main()` accepts optional count, uses `open()`, `unlink()`, `errno`, and expects `EEXIST` after pass zero.

## Control Flow and State
It unlinks `exctest.file`, loops count times, requires the first create to succeed and all later creates to fail with `EEXIST`.

## Persistence and Dependencies
persistent state is one scratch file that is not explicitly unlinked at success in this small test. Dependencies: POSIX open flags or platform-specific file headers.

## Integration Points, Risks, and Test Signals
Integration is exclusive-create validation. Risks are leaked `exctest.file`, permissions/umask influence, and missing close on created descriptors. Signal is `EEXIST` on every duplicate attempt.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/excltest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/freesp.c -->
# sources/test-tools/cthon04/special/freesp.c

## Purpose
verifies System V `fcntl(F_FREESP)` truncation semantics after writing several full buffers and a partial buffer.

## Important APIs, Types, and Functions
`main()`, `verify_size()`, `flock_t clear`, `F_FREESP`, `BUFSIZE`, `PARTIAL_BUF`, and `NUMBUFS` are key.

## Control Flow and State
When `F_FREESP` exists, it writes three 8192-byte buffers plus 42 bytes, verifies size, seeks to zero, clears from zero to EOF with `fcntl`, verifies zero length, closes, and unlinks. Without support it prints a skip.

## Persistence and Dependencies
state is `freesp.dat` or a supplied filename plus its file offset. Dependencies: System V file-space APIs, `fcntl`, `lseek`, and POSIX file I/O.

## Integration Points, Risks, and Test Signals
Integration is optional free-space/truncate testing. Risks are non-portability of `F_FREESP`, destructive filename handling, and relying on `lseek` as size. Signals are skip on unsupported platforms or exact size transition to zero.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/freesp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/fstat.c -->
# sources/test-tools/cthon04/special/fstat.c

## Purpose
prints total and free file-node counts from `statfs`/`statvfs` for a path, validating filesystem statfs availability.

## Important APIs, Types, and Functions
`main()` selects `struct statfs` or `struct statvfs` and calls `statfs()`, SVR3 `statfs(name,&fs,sizeof,0)`, or `statvfs()`.

## Control Flow and State
It accepts optional path, zeroes `f_files`/`f_ffree`, calls the platform API, and prints counts.

## Persistence and Dependencies
no lasting state; it only reads filesystem metadata. Dependencies: platform mount/statfs headers and `u_long` formatting.

## Integration Points, Risks, and Test Signals
Integration is the special filesystem-capacity probe. Risks are platform struct layout variation and DOS/Win skip. Signals are successful `total/free` output.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/fstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/holey.c -->
# sources/test-tools/cthon04/special/holey.c

## Purpose
creates a sparse file with alternating patterned data and holes, then verifies that data regions keep their pattern and hole regions read as zeroes.

## Important APIs, Types, and Functions
`main()` owns argument parsing, `Debug`, file constants, `MIN`, `L_INCR`, and buffer pattern generation.

## Control Flow and State
The program creates/reopens a file, writes data chunks and advances with `lseek()` for holes until `filesz` is reached, rewinds, optionally reopens read-only on BSD, then reads every data and hole span, checking integer patterns and zero-filled holes.

## Persistence and Dependencies
persistent state is `holeyfile`/`holefile` or a supplied file, intentionally left unless caller cleanup removes it. Dependencies: POSIX sparse-file semantics, `lseek`, `read`, `write`, `umask`, and binary open mode on DOS/Win.

## Integration Points, Risks, and Test Signals
Integration is sparse-file NFS validation. Risks include alignment assumptions when reading integers from char buffers, platform-specific hole size, and no final unlink. Signals are `Holey file test ok` and no non-zero hole bytes.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/holey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/negseek.c -->
# sources/test-tools/cthon04/special/negseek.c

## Purpose
ensures negative seeks are rejected by the filesystem/client path rather than allowing reads from invalid offsets.

## Important APIs, Types, and Functions
`main()` opens the supplied filename read-only with create, loops `lseek()` from 0 down to -9216, and reads after successful seeks.

## Control Flow and State
Any failed `lseek()` or `read()` is treated as expected enough to exit success after cleanup; if all negative seeks and reads succeed, the test exits failure.

## Persistence and Dependencies
state is the temporary named file, removed on both expected-failure and all-success paths. Dependencies: POSIX `lseek`, `read`, and legacy DOS/Win behavior.

## Integration Points, Risks, and Test Signals
Integration is invalid-offset testing. Risks are opening with `O_RDONLY|O_CREAT`, accepting a `read` failure as success even if `lseek` passed, and Windows skip. Signal is early error from negative seek/read with exit 0.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/negseek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/nfsidem.c -->
# sources/test-tools/cthon04/special/nfsidem.c

## Purpose
runs an idempotency sequence of mkdir, create, chmod, rename, link, symlink, unlink, rmdir, and failed lookup to catch lost or replayed NFS replies.

## Important APIs, Types, and Functions
`main()` builds path globals `DIR`, `FOO`, `BAR`, `SBAR`, `TBAR`, `LBAR`, message `str`, and uses `stat()` for type/mode/size validation.

## Control Flow and State
For each count, it creates a test tree, writes a message, chmods it, renames into a subdir, optionally hard-links and no-op renames, optionally symlinks, validates a selected path, removes all names and directories, and verifies the top directory no longer exists.

## Persistence and Dependencies
persistent state is the temporary tree, which may remain on failure; final exit code is current `errno`. Dependencies: POSIX directory/file/link/symlink APIs and platform support for hard/symbolic links.

## Integration Points, Risks, and Test Signals
Integration is NFS duplicate request/idempotency coverage. Risks are fixed-length path buffers, unsupported links signaled only by `EOPNOTSUPP`, BSD workaround, and cleanup breakage on partial failure. Signals are exit zero after all loops and final `ENOENT` lookup.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/nfsidem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/nstat.c -->
# sources/test-tools/cthon04/special/nstat.c

## Purpose
times repeated `stat()` calls against the program path to measure metadata lookup/cache behavior.

## Important APIs, Types, and Functions
`main()` uses `starttime()`, `endtime()`, `struct timeval`, `struct stat`, and a `stats` counter.

## Control Flow and State
It parses a count, loops `stat(argv[0])`, increments counters, computes elapsed seconds, and prints calls/sec plus msec/call.

## Persistence and Dependencies
no persistent filesystem changes. Dependencies: `../basic/subr.o` timing helpers through `../tests.h` plus `stat` headers.

## Integration Points, Risks, and Test Signals
Integration is metadata-rate testing. Risks are statting the executable instead of an arbitrary target and division-by-zero guard only for exact zero elapsed. Signals are successful timing output.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/nstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/op_chmod.c -->
# sources/test-tools/cthon04/special/op_chmod.c

## Purpose
checks that an already-open read/write file remains usable after its pathname is chmoded to no access.

## Important APIs, Types, and Functions
`main()`, helper `xxit()`, buffers `wbuf`/`rbuf`, `CHMOD_NONE`, `CHMOD_RW`, `tempnam()`, `chmod()`, `write()`, `read()`, and `system("ls")` are key.

## Control Flow and State
It creates a temp file, lists it, chmods it to no access, writes and rereads a fixed message through the open descriptor, compares data, restores permissions on DOS, unlinks, closes, and reports success.

## Persistence and Dependencies
state is a temp `nfs*` file and mode bits; cleanup differs on DOS/Unix. Dependencies: POSIX permission semantics, inherited open descriptors, `../tests.h` chmod masks.

## Integration Points, Risks, and Test Signals
Integration is open-file-after-permission-change validation. Risks include `tempnam()`, shelling out to `ls`, DOS-specific behavior, and no descriptor close before some failures. Signal is data compare ok and successful cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/op_chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/op_ren.c -->
# sources/test-tools/cthon04/special/op_ren.c

## Purpose
verifies writes through an open descriptor still work after another file is renamed over the open file name, covering NFS silly-rename style behavior.

## Important APIs, Types, and Functions
`main()`, `xxit()`, temp names `nfsa*`/`nfsb*`, `rename()`, `write()`, `read()`, `unlink()`, and close checks are key.

## Control Flow and State
It creates source A and open target B, renames A over B while B remains open, writes to B descriptor, rewinds, verifies data, unlinks the visible name, closes, verifies a second close fails, and exits with accumulated errors.

## Persistence and Dependencies
state is two temp names and the open file handle; failures may leave temp files. Dependencies: Unix rename/open descriptor semantics, `tempnam`, POSIX I/O, and SunOS/DOS skip conditionals.

## Integration Points, Risks, and Test Signals
Integration is open-renamed-file special testing. Risks are Unix-only semantics, command injection via temp names in `system("ls")`, and relying on old NFS behavior. Signals are rename success, data compare ok, and second close error.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/op_ren.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/op_unlk.c -->
# sources/test-tools/cthon04/special/op_unlk.c

## Purpose
tests that an open file continues to support I/O after its directory entry is unlinked.

## Important APIs, Types, and Functions
`main()`, `xxit()`, temp name creation, `unlink()`, `write()`, `lseek()`, `read()`, close/unlink error checks, and `CHMOD_RW` are key.

## Control Flow and State
It opens a temp file, unlinks it while open on Unix, writes/reads a fixed buffer through the descriptor, expects a second unlink to fail with `ENOENT` or `EACCES`, closes, and expects a second close to fail.

## Persistence and Dependencies
state is the open-but-unlinked inode and temp name; cleanup diverges for Windows. Dependencies: Unix open-unlink semantics and DOS/Win path restrictions.

## Integration Points, Risks, and Test Signals
Integration is open-unlinked-file validation. Risks include shelling out to `ls`, `tempnam()`, platform-specific expected errno, and possible leftover files on error. Signals are data compare ok, expected second unlink failure, and expected second close failure.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/op_unlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/rename.c -->
# sources/test-tools/cthon04/special/rename.c

## Purpose
renames a scratch file back and forth `n` times to stress repeated rename operations.

## Important APIs, Types, and Functions
`main()` parses count, creates `rename1`, and loops `rename("rename1","rename2")` then back.

## Control Flow and State
After initial creation, each iteration performs two renames and aborts with the current iteration on failure; cleanup unlinks both possible names.

## Persistence and Dependencies
persistent state is `rename1`/`rename2` only during the run. Dependencies: POSIX `open`, `rename`, `unlink` and legacy platform headers.

## Integration Points, Risks, and Test Signals
Integration is rename operation rate/reliability testing. Risks are fixed scratch names in cwd, a dead `cleanup:` label, and no fsync durability. Signal is completion without perror.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/rewind.c -->
# sources/test-tools/cthon04/special/rewind.c

## Purpose
checks that `ftruncate(fd,0)` after rewinding really resets file length and the next write produces a one-byte file.

## Important APIs, Types, and Functions
`main()` uses an 8192-byte buffer, writes three blocks, `lseek()`s to zero, truncates, writes one byte, and checks `SEEK_END` offset.

## Control Flow and State
It creates `test.file`, writes 24 KiB, rewinds, truncates to zero, writes one byte, seeks to end, and requires offset 1.

## Persistence and Dependencies
state is `test.file`; this program closes but does not unlink it. Dependencies: POSIX `open`, `write`, `lseek`, `ftruncate`, DOS/Win skip path.

## Integration Points, Risks, and Test Signals
Integration is truncate/offset handling. Risks are uninitialized buffer content, leaked scratch file, and no cleanup on failure. Signal is exit zero with final size one.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/rewind.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/stat.c -->
# sources/test-tools/cthon04/special/stat.c

## Purpose
recursively stats every entry in a directory tree and reports metadata call rate.

## Important APIs, Types, and Functions
`main()`, recursive `statit()`, `starttime()`, `endtime()`, `telldir()`, `seekdir()`, `opendir()`, `readdir()`, and `lstat()`/`stat()` are key.

## Control Flow and State
`statit()` stats a path, returns for non-directories, opens directories, chdirs into them, stats children, recurses into child directories after saving a telldir cookie, reopens `.` and seeks back, then chdirs up.

## Persistence and Dependencies
state changes include process current working directory and `stats` counter; no files are modified. Dependencies: directory stream APIs, timing helpers from `../basic/subr.o`, and SVR3/directs conditionals.

## Integration Points, Risks, and Test Signals
Integration is directory metadata traversal performance. Risks are cwd mutation, telldir/seekdir portability, symlink behavior differences, and divide by zero if elapsed is zero. Signals are complete traversal and calls/sec output.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/stat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/stat2.c -->
# sources/test-tools/cthon04/special/stat2.c

## Purpose
creates a directory full of numbered files and repeatedly stats them to measure metadata performance under a fixed working set.

## Important APIs, Types, and Functions
`main()` uses `mkdir()`, `chdir()`, `creat()`, `stat()`, `starttime()`, `endtime()`, `files`, `count`, and `stats`.

## Control Flow and State
It creates/chdirs into the supplied directory, creates `files` numbered files, times `count` passes over all file names with `stat()`, and prints aggregate calls/sec.

## Persistence and Dependencies
persistent state is the created directory and numbered files; no cleanup is performed. Dependencies: POSIX directory/file creation, stat, and timing helpers.

## Integration Points, Risks, and Test Signals
Integration is repeated metadata-cache testing. Risks are destructive name reuse, no cleanup, no close-error checking, and cwd mutation. Signal is all stat calls succeed and timing output matches `files * count`.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/stat2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/telldir.c -->
# sources/test-tools/cthon04/special/telldir.c

## Purpose
validates that `telldir()` cookies can be fed back to `seekdir()` to resume at the same directory entry.

## Important APIs, Types, and Functions
`file_info_t` records `inuse`, `cookie`, and remaining file count. Important functions are `alloc_file_info()`, `make_files()`, `walk_dir()`, `save_file_info()`, `check_file_info()`, `verify()`, and `cleanup()`.

## Control Flow and State
The program creates `telldir-test` with numbered files, opens it, walks entries while saving each pre-read cookie, then for each saved cookie seeks back and verifies the expected first file and remaining entry count.

## Persistence and Dependencies
persistent state is the scratch directory and `file_info` array; cleanup shells out `rm -rf telldir-test`. Dependencies: POSIX directory cookies, `calloc`, `creat`, `mkdir`, and `../tests.h` for `MAXPATHLEN`/prototypes.

## Integration Points, Risks, and Test Signals
Integration is directory cookie correctness testing. Risks are relying on directory order matching numeric names, unsafe `system("rm -rf")`, ignoring `.`/`..` while counting, and undefined behavior if filenames are unexpected. Signals are no missing info, no premature EOF, and zero exit.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/telldir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/touchn.c -->
# sources/test-tools/cthon04/special/touchn.c

## Purpose
creates `n` numbered files named `name<n>` down to `name1` as a simple create workload.

## Important APIs, Types, and Functions
`main()` parses count and repeatedly calls `creat()` with a formatted name.

## Control Flow and State
The loop decrements from the requested count, creating and immediately closing each file.

## Persistence and Dependencies
persistent state is all generated `name*` files; no cleanup is performed. Dependencies: POSIX `creat`, `close`, and `../tests.h` for portability.

## Integration Points, Risks, and Test Signals
Integration is create-count workload generation. Risks include fixed names, no close/create error checking, and no cleanup. Signal is exit zero after file creation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/touchn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/special/truncate.c -->
# sources/test-tools/cthon04/special/truncate.c

## Purpose
tests whether extending a file with `ftruncate()` through setattr-like semantics updates visible size correctly.

## Important APIs, Types, and Functions
`main()` uses `creat()`, `ftruncate()`, `stat()`, size checks for 0 and 10 bytes, and cleanup unlink.

## Control Flow and State
It creates `testfile`, truncates to zero and verifies size zero, truncates to ten and verifies size ten, closes, unlinks, and prints success.

## Persistence and Dependencies
state is `testfile` during the run. Dependencies: POSIX `ftruncate`, `stat`, and DOS/Win skip path.

## Integration Points, Risks, and Test Signals
Integration is special truncate/SETATTR validation. Risks are fixed scratch name and only checking size, not hole contents. Signal is `truncate succeeded`.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/special/truncate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tests.h -->
# sources/test-tools/cthon04/tests.h

## Purpose
`tests.h` is the shared portability and test helper contract for the Connectathon suite. It defines default test-tree dimensions, test directory paths, chmod masks, DOS/Windows compatibility includes, and prototypes for common timing and directory-tree helper routines.

## Important APIs, Types, and Functions
Important macros include `DOSorWIN32`, `ANSI`, `DNAME`, `FNAME`, `DDIRS`, `DLEVS`, `DFILS`, `TESTDIR`, `DCOUNT`, `CHMOD_MASK`, `CHMOD_NONE`, `CHMOD_RW`, `MAXPATHLEN`, `MAP_FAILED`, and `ARGS_()`. Declared helpers include `starttime()`, `endtime()`, `getparm()`, `dirtree()`, `rmdirtree()`, `testdir()`, `mtestdir()`, `complete()`, optional `strerror()`, `unix_chdir()`, and `error()`.

## Control Flow and State
There is no runtime control flow in the header. Preprocessor branches select Unix defaults or DOS/Win defaults, include `unixdos.h` where needed, and remap stdio streams for DOS/Windows redirected output.

## Persistence and Dependencies
No state is persisted directly, but the header declares external `Myname` and fixes constants used by many tests to create files, directories, and chmod modes. Dependencies: system errno headers, Windows/DOS headers when selected, `unixdos.h`, and helper implementations in `basic/subr.c`.

## Integration Points, Risks, and Test Signals
Integration is broad across basic, general, and special Cthon tests. Risks include global macro pollution, old K&R prototype support, path-length differences, a Unix default `TESTDIR` of `/mnt/nfstestdir`, and DOS stdio macro remapping. Test signals are successful cross-platform builds and consistent helper signatures for all suites.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/Makefile -->
# sources/test-tools/cthon04/tools/Makefile

## Purpose
This Makefile builds the Connectathon auxiliary network and directory tools: TCP/UDP ping clients and daemons, directory printers/dumpers, and portmapper tests.

## Important APIs, Types, and Functions
Key variables and targets are `TESTS`, `include ../tests.init`, `all`, individual compile rules for `tcp`, `tcpd`, `udp`, `udpd`, `dirdmp`, `dirprt`, `pmaptst`, `pmapbrd`, plus `lint`, `clean`, `copy`, and `dist`.

## Control Flow and State
`all` compiles every listed tool with inherited compiler flags and libraries. Comments document an alternate Linux `TESTS` set that omits unsupported `dirdmp`. `copy` installs built binaries to `DESTDIR`, while `dist` copies Makefile, README, and all C sources.

## Persistence and Dependencies
Persistent state is object files, tool binaries, and copied distribution files; `clean` removes objects and binaries. Dependencies: `../tests.init`, C compiler, RPC/socket libraries as needed, and a writable `DESTDIR` for copy/dist.

## Integration Points, Risks, and Test Signals
Integration is with manual/tooling support for Cthon network and directory diagnostics. Risks include the Linux dirdmp caveat requiring manual Makefile edits, no automatic header dependencies, and destructive overwrite in `copy`. Test signals are all listed binaries building and the client/server tools successfully exchanging messages.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/dirdmp.c -->
# sources/test-tools/cthon04/tools/dirdmp.c

## Purpose
dumps raw-ish directory buffer contents by bypassing normal `readdir()` formatting on platforms where `DIR` internals and `getdents`/`getdirentries` are accessible.

## Important APIs, Types, and Functions
`main()`, `print()`, `my_opendir()`, and `my_readdir()` are key; it manipulates `DIR` fields such as `dd_fd`, `dd_buf`, `dd_loc`, `dd_size`, and platform-specific buffer base fields.

## Control Flow and State
For each directory argument, it opens the directory file descriptor, allocates a `DIR`, fills buffers with `getdents` or `getdirentries`, prints location/inode/reclen/name data until EOF, and skips zero-inode entries.

## Persistence and Dependencies
state is allocated directory buffers and file descriptors, released by `closedir()` after printing. Dependencies: private libc `DIR` layout, platform macros for SVR/BSD/SunOS/Mac/OSF1, and low-level directory syscalls.

## Integration Points, Risks, and Test Signals
Integration is diagnostic only. Risks are extreme portability fragility, disabled Linux/AIX support, accessing libc internals, and possible memory leaks on some error paths. Signals are directory entry tables and EOF output.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/dirdmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/dirprt.c -->
# sources/test-tools/cthon04/tools/dirprt.c

## Purpose
prints directory entries using standard `opendir()`/`readdir()` plus `telldir()` cookies for easier inspection than `dirdmp`.

## Important APIs, Types, and Functions
`main()`, `print()`, and `my_opendir()` are key; output fields vary between SVR/Linux `d_ino` and BSD-style `d_fileno`/`d_namlen`.

## Control Flow and State
For each argument, it stats the path, verifies it is a directory, opens it, iterates entries, prints current `telldir()` and dirent metadata, then closes.

## Persistence and Dependencies
no persistent state beyond directory stream position. Dependencies: dirent APIs, stat headers, and platform `use_directs`/AIX conditionals.

## Integration Points, Risks, and Test Signals
Integration is a portable directory-cookie/display tool. Risks are AIX unsupported path, platform-specific dirent fields, and no usage diagnostics for missing args. Signals are per-entry printed cookies and metadata.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/dirprt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/pmapbrd.c -->
# sources/test-tools/cthon04/tools/pmapbrd.c

## Purpose
stress-tests portmapper broadcast RPC by sending repeated `PMAPPROC_CALLIT` broadcasts at a requested packet rate.

## Important APIs, Types, and Functions
Important types are `rmtcallargs`, `rmtcallres`, `XDR`, broadcast `sockaddr_in`, and result callback `resultproc_t`. Key functions are `main()`, `getbroadcastnets()`, `clnt_broadcast_time()`, `xdr_rmtcall_args()`, `xdr_rmtcallres()`, and `eachresult()`.

## Control Flow and State
It opens a UDP socket on port 3300, enables broadcast, discovers a broadcast address with interface ioctls, then loops `count` times calling a custom broadcast routine. That routine XDR-encodes a portmapper CALLIT request, sends it, waits with `select()` for a short timeout, decodes matching replies, and returns `RPC_TIMEDOUT` when no more replies arrive.

## Persistence and Dependencies
state includes static XDR buffers, selected broadcast address, socket binding, RPC auth handle, transaction id, and transient decoded replies. Dependencies: SunRPC headers/libraries, portmapper protocol, UDP sockets, interface ioctls, XDR, `select`, and broadcast-capable network configuration.

## Integration Points, Risks, and Test Signals
Integration is a network/portmapper diagnostic. Risks include old `select(32)` fd limit, raw fd-set casting, only one broadcast address, root/network policy restrictions, and RPC library portability. Signals are repeated `RPC_TIMEDOUT` completions without other client errors and visible broadcast rate output.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/pmapbrd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/pmaptst.c -->
# sources/test-tools/cthon04/tools/pmaptst.c

## Purpose
tests local portmapper registration by adding and removing a dummy program/version for UDP and TCP and showing `rpcinfo -p` before and after.

## Important APIs, Types, and Functions
`main()` uses `pmap_set()`, `pmap_unset()`, constants `PROG`, `VERS`, `UPORT`, `TPORT`, and shell command `rpcinfo -p`.

## Control Flow and State
It prints baseline rpcinfo, registers UDP mapping, prints, registers TCP mapping, prints, unregisters the program/version, prints again, and exits with the number of registration failures.

## Persistence and Dependencies
persistent state is temporary portmapper registrations until `pmap_unset()` succeeds. Dependencies: SunRPC portmap APIs, `rpcinfo`, shell, and a running local portmapper/rpcbind.

## Integration Points, Risks, and Test Signals
Integration is portmapper sanity testing. Risks include modifying global rpcbind state, fixed program number collisions, dependence on external `rpcinfo`, and permissions. Signals are visible mappings after set and removal after unset.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/pmaptst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/tcp.c -->
# sources/test-tools/cthon04/tools/tcp.c

## Purpose
is the TCP client for the simple Connectathon ping pair on port 3456.

## Important APIs, Types, and Functions
`main()` resolves a hostname with `gethostbyname()`, opens a TCP socket, connects, writes a fixed message, reads the echo, and validates the first byte was incremented by the daemon.

## Control Flow and State
The client requires one hostname, connects to `TCP_PORT`, writes `This is a test message!`, reads up to `BUFSIZ`, compares length and payload, and prints success or message error.

## Persistence and Dependencies
state is a single socket connection and local buffer. Dependencies: IPv4 sockets, DNS/hosts lookup, `tcpd.c` server behavior.

## Integration Points, Risks, and Test Signals
Integration is the basic TCP connectivity diagnostic. Risks include no timeout, obsolete `h_addr`, no explicit socket close, and partial write/read assumptions. Signals are `tcp ping to <host> ok`.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/tcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/tcpd.c -->
# sources/test-tools/cthon04/tools/tcpd.c

## Purpose
is the TCP daemon for the simple Connectathon ping pair on port 3456.

## Important APIs, Types, and Functions
`main()` creates a listening socket, binds `INADDR_ANY`, listens backlog 5, accepts forever, resolves client names, reads a buffer, increments the first byte, writes it back, sleeps, and closes.

## Control Flow and State
The server loops indefinitely accepting one connection at a time; for positive reads it mutates `buf[0]` and echoes the same byte count.

## Persistence and Dependencies
persistent state is the bound listening socket and repeated accepted sockets. Dependencies: IPv4 TCP sockets, reverse DNS, and client `tcp.c` expectations.

## Integration Points, Risks, and Test Signals
Integration is with `tcp.c`. Risks include no `SO_REUSEADDR`, single-threaded blocking loop, no signal cleanup, sleep-induced backlog pressure, and partial I/O assumptions. Signals are accept/read/write logs and successful client validation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/tcpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/udp.c -->
# sources/test-tools/cthon04/tools/udp.c

## Purpose
is the UDP client for the simple Connectathon ping pair on port 3457.

## Important APIs, Types, and Functions
`main()` resolves hostname, creates a datagram socket, `sendto()`s a fixed message, `recvfrom()`s a reply, and validates the first byte changed.

## Control Flow and State
It sends one datagram to `UDP_PORT`, waits indefinitely for one response, compares length and payload, and prints success or a message error.

## Persistence and Dependencies
state is one UDP socket and server address. Dependencies: IPv4 UDP sockets, name resolution, and `udpd.c` server behavior.

## Integration Points, Risks, and Test Signals
Integration is a UDP connectivity diagnostic. Risks include no timeout/retry, spoofable reply source after `recvfrom`, obsolete hostent fields, and datagram loss. Signal is `udp ping to <host> ok`.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/udp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/tools/udpd.c -->
# sources/test-tools/cthon04/tools/udpd.c

## Purpose
is the UDP daemon for the simple Connectathon ping pair on port 3457.

## Important APIs, Types, and Functions
`main()` creates a UDP socket, binds `INADDR_ANY`, loops on `recvfrom()`, reverse-resolves the sender, increments the first byte of each datagram, and `sendto()`s it back.

## Control Flow and State
The daemon handles one datagram at a time forever and echoes the same byte count after mutating byte zero.

## Persistence and Dependencies
persistent state is the bound UDP socket; no files are touched. Dependencies: IPv4 UDP sockets, reverse DNS, and client `udp.c`.

## Integration Points, Risks, and Test Signals
Integration is with `udp.c`. Risks include no `SO_REUSEADDR`, no shutdown path, blocking reverse DNS, and unauthenticated echo behavior. Signals are request logs and successful client validation.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/tools/udpd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/cthon04/unixdos.h -->
# sources/test-tools/cthon04/unixdos.h

## Purpose
`unixdos.h` supplies Unix-like typedefs, structs, and function prototypes for DOS/Windows builds of the Connectathon tests. It lets sources using Unix directory, timeval, statfs, and path APIs compile against the legacy DOS compatibility layer.

## Important APIs, Types, and Functions
Important definitions are `struct timeval`, `u_char`, `MAXPATHLEN`, `MIN()`, `fsid_t`, `struct statfs`, dummy `DIR`, simplified `struct dirent`, `MAXNAMLEN`, and `DIRSIZ()`. Declared functions include `gettimeofday()`, `unix_chdir()`, `lstat()`, `statfs()`, `opendir()`, `readdir()`, `rewinddir()`, `closedir()`, `seekdir()`, and `telldir()`.

## Control Flow and State
The header only selects declarations. It avoids redefining `timeval` if Winsock has already supplied one and gates some directory cookie declarations behind `_POSIX_SOURCE`.

## Persistence and Dependencies
No persistent state is created; it defines ABI-compatible shapes that external DOS support code must honor. Dependencies: DOS/Windows compatibility implementations, stat structs from other includes, and tests that include `tests.h` with `DOSorWIN32`.

## Integration Points, Risks, and Test Signals
Integration is the compatibility bridge for non-Unix builds. Risks include intentionally simplified `DIR` and `dirent` structures, `MAXNAMLEN` larger than the actual fixed `d_name[13]`, mismatch with real platform headers, and old-style prototypes. Test signals are successful DOS/Win builds and correct directory/stat behavior in the ported tests.
<!-- END_FILE_RESEARCH: sources/test-tools/cthon04/unixdos.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/Makefile.am -->
# sources/test-tools/filebench/Makefile.am

## Purpose
`Makefile.am` is the Automake build manifest for Filebench. It declares the generated parser header, subdirectories, the `filebench` executable, the complete source/header list, distribution extras, yacc/lex flags, conditional warning flags, and preprocessor definitions.

## Important APIs, Types, and Functions
Important Automake variables are `libdir`, `SUBDIRS`, `BUILT_SOURCES`, `bin_PROGRAMS`, `filebench_SOURCES`, `EXTRA_DIST`, `ACLOCAL_AMFLAGS`, `AM_YFLAGS`, conditional `AM_CFLAGS`, and `DEFS`.

## Control Flow and State
Automake expands this manifest into Makefile rules that build parser artifacts, compile all listed core modules plus cvar Mersenne Twister code, link `filebench`, recurse into `workloads` and `cvars`, and install workload library data under `@libdir@/filebench`.

## Persistence and Dependencies
Persistent build state includes generated parser files, objects, the `filebench` binary, and installed library/workload files. Dependencies: Autoconf/Automake, lex/yacc, generated `config.h`, Filebench source modules, and platform definitions such as `_LARGEFILE64_SOURCE` and `_GNU_SOURCE`.

## Integration Points, Risks, and Test Signals
Integration is the central build contract for Filebench. Risks include a long manually maintained source list, duplicate `config.h` in `filebench_SOURCES`, warning flags only under `GCC_USED`, and build failures if generated parser headers are stale. Test signals are `make distcheck`/Automake generation success and a linked `filebench` binary including `aslr.c`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/Makefile.am -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/aslr.c -->
# sources/test-tools/filebench/aslr.c

## Purpose
`aslr.c` provides Filebench startup support for disabling per-process address space layout randomization where the platform allows it. Filebench uses fixed `MAP_FIXED` mappings across fork/exec, so ASLR can cause mappings to overlap unrelated regions and crash workloads.

## Important APIs, Types, and Functions
The platform-specific implementation is `linux_disable_aslr()` when both `HAVE_SYS_PERSONALITY_H` and `HAVE_ADDR_NO_RANDOMIZE` are defined. The fallback is `other_disable_aslr()`. Both log through `filebench_log()` and are selected by `aslr.h`.

## Control Flow and State
On Linux-capable builds, the function calls `personality(0xffffffff)` and then `personality(0xffffffff | ADDR_NO_RANDOMIZE)`, logging an error if the second call returns `-1`. On unsupported platforms, the fallback logs a manual sysctl instruction rather than changing process flags.

## Persistence and Dependencies
Persistent effect is process personality state for the current process and descendants after exec; fallback changes no state. Dependencies: `config.h`, `<sys/personality.h>` when available, Filebench logging (`filebench.h`), and `aslr.h` inline dispatch.

## Integration Points, Risks, and Test Signals
Integration is early Filebench process setup before fixed mappings are used. Risks include preserving current personality bits incorrectly if the first call result is ignored, Linux-only behavior, broad manual sysctl advice, and relying on compile-time feature detection. Test signals are no ASLR-related workload crashes and either absence of the error log or the informational unsupported-platform log.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/aslr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/aslr.h -->
# sources/test-tools/filebench/aslr.h

## Purpose
`aslr.h` is the Filebench header-level dispatch wrapper for ASLR disabling. It exposes one inline `disable_aslr()` API while hiding whether the build uses Linux `personality()` support or a logging-only fallback.

## Important APIs, Types, and Functions
Important declarations are `linux_disable_aslr()`, `other_disable_aslr()`, and `static inline disable_aslr()`. The selection condition matches `aslr.c`: `HAVE_SYS_PERSONALITY_H && HAVE_ADDR_NO_RANDOMIZE`.

## Control Flow and State
Including code calls `disable_aslr()`, which returns the selected void helper. The header has no dynamic control flow beyond compile-time conditional selection.

## Persistence and Dependencies
No state is stored in the header; called implementation may change process personality on Linux. Dependencies: `filebench.h` for shared Filebench declarations/logging context and feature macros supplied by `config.h` transitively in source files.

## Integration Points, Risks, and Test Signals
Integration is any Filebench startup path that needs fixed-address mapping stability. Risks include including `<filebench.h>` with angle brackets, relying on macros being visible before this header, and a void function written with `return helper();`. Test signals are successful compilation on Linux and unsupported platforms and correct call routing to the expected implementation.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/aslr.h -->
