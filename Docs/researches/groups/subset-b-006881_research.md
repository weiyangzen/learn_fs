# subset-b-006881 research

Grouped research for Linux selftest files under proc, pstore, ptp, ptrace, and rcutorture. Each section is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-empty-vm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-empty-vm.c

Purpose: x86-only procfs VM accounting regression test for a ptrace-stopped process whose userspace mappings have been unmapped. It validates that `/proc/$pid/maps`, `numa_maps`, `smaps`, `smaps_rollup`, and `statm` handle an effectively empty mm without corrupt output or crashes.

Important APIs and functions: `protection_key_support()` probes `pkey_alloc/free`; `vsyscall()` classifies the unavoidable amd64 vsyscall VMA; `test_proc_pid_*()` readers assert exact or empty proc output; `parse_u64()` validates `statm` fields. It uses `fork`, `ptrace(PTRACE_TRACEME)`, `munmap`, `sigaction`, `waitpid`, `open/read`, and raw pkey syscalls.

Control flow: the parent probes vsyscall and pkeys, forks a child, and waits briefly while the child marks itself traceable and unmaps almost the entire userspace address range. The parent then reads each proc VM file and finally waits for the child's SIGSEGV stop.

State and persistence: no persistent state beyond transient child process state and procfs observations. Global variables cache detected vsyscall and pkey capabilities to select expected strings.

Dependencies and integration: depends on x86 address-space assumptions, procfs, ptrace availability, optional `CONFIG_NUMA`, optional `CONFIG_PROC_PAGE_MONITOR`, and optional pkeys. Non-x86 builds return kselftest skip code 4.

Risks and test signals: the deliberate `sleep(1)` is a timing compromise because the child cannot reliably signal after unmapping itself. Exact smaps strings are kernel-output-sensitive. Failures signal proc VM walkers mishandling empty mm state, vsyscall handling drift, or `statm` accounting regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-empty-vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-fsconfig-hidepid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-fsconfig-hidepid.c

Purpose: validates new mount API parsing for procfs `hidepid`. It checks that binary `hidepid` configuration is rejected while string values remain accepted.

Important APIs and functions: local wrappers call raw `fsopen()` and `fsconfig()` through `__NR_fsopen` and `__NR_fsconfig`. The test uses `FSCONFIG_SET_BINARY`, `FSCONFIG_SET_STRING`, and close.

Control flow: open a procfs fs context, attempt to set `hidepid` as binary integer 2, require `EINVAL`, then set `"2"` and `"invisible"` string values successfully.

State and persistence: only a transient fs context file descriptor is created. It is closed before exit and no mount is instantiated.

Dependencies and integration: depends on the new mount API and procfs fs_context support. It integrates with selftests as a direct assertion-style C program.

Risks and test signals: failures indicate accidental acceptance of binary hidepid input or broken string option parsing. Environments without fsopen support may fail rather than skip because the program asserts `fsopen("proc")` succeeds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-fsconfig-hidepid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-loadavg-001.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-loadavg-001.c

Purpose: verifies that the last PID field in `/proc/loadavg` is reported relative to the current PID namespace.

Important APIs and functions: uses `unshare(CLONE_NEWPID)`, `fork`, `waitpid`, `open`, `read`, and `lseek`. The parsing is deliberately minimal, checking the final `" 1\n"` and `" 2\n"` suffixes.

Control flow: the parent enters a new PID namespace and forks the namespace init. The child reads `/proc/loadavg`, requires last pid 1, forks and waits for one child, rewinds the fd, reads again, and requires last pid 2.

State and persistence: uses transient namespace process state only. The proc file descriptor is reused across reads.

Dependencies and integration: requires PID namespace support and permission to create one. `ENOSYS` or `EPERM` returns kselftest skip 4.

Risks and test signals: parsing assumes the last pid remains a one-digit suffix for this small namespace. Failure points to incorrect pid namespace scoping in loadavg or broken proc file seek/read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-loadavg-001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-maps-race.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-maps-race.c

Purpose: stress-tests `/proc/$pid/maps` and the `PROCMAP_QUERY` ioctl while a traced child concurrently mutates VMAs. It targets output tearing at page boundaries during VMA split, resize, and remap operations.

Important APIs and functions: kselftest fixtures manage a child with shared `struct vma_modifier_info`. Core helpers include `read_two_pages()`, `read_boundary_lines()`, `capture_mod_pattern()`, `query_addr_at()`, and VMA operations using `mmap`, `mprotect`, and `mremap`. It validates `struct procmap_query` returned by `ioctl(PROCMAP_QUERY)`.

Control flow: setup maps many alternating-protection VMAs in a child, opens `/proc/$child/maps`, captures the boundary crossing two pages, and locates VMAs that straddle that boundary. Each test first captures expected modified/restored patterns, then runs a timed loop where the child repeatedly mutates and restores VMAs while the parent reads boundary lines and queries VMAs.

State and persistence: process-shared anonymous memory holds synchronization locks, condition variable, current state, operation callbacks, and child mapping addresses. No persistent files are written.

Dependencies and integration: depends on pthread process-shared synchronization, procfs maps, anonymous mappings, `mremap` features including `MREMAP_DONTUNMAP`, and the kernel procmap ioctl ABI from `linux/fs.h`.

Risks and test signals: timing and page-boundary assumptions are central. It deliberately allows a small set of duplicated/restored-line patterns that are legal under concurrent modification. Failures signal torn maps iteration, wrong next-VMA handling, or `PROCMAP_QUERY` inconsistency under races.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-maps-race.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-multiple-procfs.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-multiple-procfs.c

Purpose: verifies that separately mounted procfs instances with different `hidepid` options are distinct superblocks/devices.

Important APIs and functions: uses `mkdtemp`, `mount("proc", ..., "hidepid=1")`, `mount("proc", ..., "hidepid=2")`, `stat`, `umount`, and `snprintf`.

Control flow: create two temporary directories, mount procfs with two hidepid modes, stat each mount's `meminfo`, unmount both, and assert the `st_dev` values differ.

State and persistence: creates temporary directories under `/tmp` and mounts procfs instances. The directories are not removed by this test, but mounts are unmounted.

Dependencies and integration: requires mount privilege and procfs. It is a simple assertion test rather than kselftest harness based.

Risks and test signals: may fail in unprivileged environments or when `/tmp` restrictions prevent mount points. A semantic failure means procfs option-specific mounts are incorrectly shared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-multiple-procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-net-dev-lseek.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-net-dev-lseek.c

Purpose: regression test that `/proc/net/dev` implements `lseek(fd, 0, SEEK_SET)` correctly and can be reread identically after rewind.

Important APIs and functions: uses `unshare(CLONE_NEWNET)` for deterministic network namespace contents, then `open`, `read`, `lseek`, `memcmp`, and assertions.

Control flow: create a fresh net namespace, read `/proc/net/dev` into `buf1`, seek to offset zero, reread into `buf2`, and assert both size and contents match.

State and persistence: transient network namespace only. No files are created.

Dependencies and integration: requires network namespace permission. `ENOSYS` and `EPERM` return skip code 4. It relies on loopback-only output being stable enough in a fresh netns.

Risks and test signals: does not validate field content, only seek semantics. A failure indicates proc net device seq-file rewind regression or nondeterministic content in the isolated namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-net-dev-lseek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pid-vm.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pid-vm.c

Purpose: x86_64 procfs VM layout test using a hand-built one-page ELF whose process unmaps all other VMAs. It validates `/proc/$pid/maps`, `smaps`, `smaps_rollup`, `statm`, and `PROCMAP_QUERY` against precise expectations.

Important APIs and functions: `make_private_tmp()` creates an isolated tmpfs; `make_exe()` builds an ET_EXEC ELF in an `O_TMPFILE`; `vsyscall()` detects amd64 vsyscall mode; raw payload code performs `munmap`, writes a pipe byte, then pauses. The parent uses `execveat(AT_EMPTY_PATH)`, `stat`, proc file reads, `memmem`, and `ioctl(PROCMAP_QUERY)`.

Control flow: setup private mount namespace and tmpfs, reserve fd 0 for child synchronization, create the tiny executable, fork/exec it, wait for the payload byte after unmapping, synthesize expected `/proc/$pid/maps` line from tmpfs device/inode, then verify all proc VM interfaces and ioctl query cases.

State and persistence: temporary executable exists only by fd and appears as deleted tmpfs path in maps. Global `pid` is killed by an `atexit` handler if still live.

Dependencies and integration: requires x86_64, tmpfs, mount namespace permission, `execveat`, proc page monitor files, and kernel headers containing `struct procmap_query`.

Risks and test signals: exact string formatting and fixed `MAPS_OFFSET` make the test sensitive to proc output format changes. Failures identify regressions in single-VMA accounting, deleted file names, vsyscall reporting, or procmap query matching and filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pid-vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pidns.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pidns.c

Purpose: kselftest harness for procfs `pidns=` mount option support through both legacy mount strings and new mount API fsconfig inputs. It also verifies PID namespace association cannot be reconfigured after procfs creation.

Important APIs and functions: uses namespace operations `unshare`, `setns`, `mount`, bind mount of `/proc/self/ns/pid`, `fsopen`, `fsconfig`, `fsmount`, `faccessat`, and kselftest `ASSERT_*` macros. `ASSERT_ERRNO_EQ` normalizes syscall negative errno handling.

Control flow: fixture stashes host mount and PID namespace fds, creates private tmpfs-backed `/tmp`, creates a dummy PID namespace in a child, bind-mounts its pidns fd, then returns to the host pidns. Tests mount proc using host and dummy pidns paths or fd and verify expected visibility. Reconfiguration tests require `EBUSY` and verify original view remains intact.

State and persistence: transient mount namespace with tmpfs under `/tmp`; bind-mounted namespace file and proc mount are discarded when returning to original mount namespace.

Dependencies and integration: requires new mount API, PID namespaces, mount namespaces, bind mounts, and privileges. Integrated with `kselftest_harness.h`.

Risks and test signals: environment privilege restrictions will fail setup. Semantic failures indicate procfs pid namespace selection or immutability regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-pidns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-isnt-kthread.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-isnt-kthread.c

Purpose: checks that a normal userspace process reports `Kthread: 0` in `/proc/self/status`.

Important APIs and functions: uses `open`, `read`, NUL termination, and `strstr`.

Control flow: read `/proc/self/status` into a 4 KiB buffer and assert the exact `Kthread:\t0\n` line is present.

State and persistence: no persistent state.

Dependencies and integration: depends on procfs status format including the Kthread field.

Risks and test signals: format changes can break the exact substring search. Failure means userspace task classification or `/proc/self/status` field emission is wrong.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-isnt-kthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-001.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-001.c

Purpose: validates strict parsing of `/proc/self/map_files/start-end` symlink names for a mapped file-backed VMA.

Important APIs and functions: helpers `pass()` and `fail()` wrap `readlink`. The test uses `/dev/zero`, `mmap(PROT_NONE, MAP_PRIVATE|MAP_FILE)`, and address formatting with `%lx`.

Control flow: create a one-page mapping, compute start/end addresses, require the exact canonical path to readlink successfully, and require malformed names with spaces, leading zeroes, and overflow-width prefixes to return `ENOENT`.

State and persistence: only a private mapping and open `/dev/zero` fd.

Dependencies and integration: requires `/proc/self/map_files` support and enough permission for self readlink.

Risks and test signals: fixed-size path buffers assume typical address lengths. Failure indicates lenient map_files dentry parsing or broken canonical symlink lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-002.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-002.c

Purpose: extends the map_files parser test to a low virtual address near `vm.mmap_min_addr`, catching boundary parsing and leading-zero behavior at small addresses.

Important APIs and functions: same `pass()` and `fail()` readlink helpers as the first test. Uses `mmap(MAP_FIXED)` in page increments below 1 MiB until a low address mapping succeeds.

Control flow: open `/dev/zero`, scan low addresses for a successful fixed one-page mapping, compute its canonical start/end, then require exact lookup success and malformed lookup `ENOENT`.

State and persistence: transient low-address mapping only.

Dependencies and integration: depends on system `mmap_min_addr` policy allowing some mapping below 1 MiB. Failure to map any low address is reported as test failure, not skip.

Risks and test signals: hardened systems may reject all requested low mappings. Semantic failures indicate map_files parser accepting noncanonical or overflowed address strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-map-files-002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-syscall.c

Purpose: verifies `/proc/self/syscall` reports the currently executing raw `read` syscall and its first arguments.

Important APIs and functions: `sys_read()` invokes `SYS_read` directly, avoiding libc wrappers. The test uses `open`, `snprintf`, `read`, `strncmp`, and errno-based skip on missing proc entry.

Control flow: open `/proc/self/syscall`, build the expected prefix containing syscall number, fd, target buffer pointer, and length, invoke raw read into that buffer, and compare the prefix.

State and persistence: no persistent state.

Dependencies and integration: depends on `/proc/self/syscall` support and architecture formatting of syscall arguments as hex. Missing file returns skip 4.

Risks and test signals: pointer formatting and syscall wrapper behavior are central. Failure points to stale or incorrectly formatted syscall reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-wchan.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-wchan.c

Purpose: verifies that reading `/proc/self/wchan` for the running task reports `0`.

Important APIs and functions: uses `open`, `read`, and skip-on-ENOENT behavior.

Control flow: open `/proc/self/wchan`, read exactly one byte into a small buffer, and require it to be ASCII `0`.

State and persistence: none.

Dependencies and integration: depends on `/proc/self/wchan` being enabled. Missing file returns kselftest skip 4.

Risks and test signals: exact single-byte expectation is format-sensitive. Failure means the current running userspace task is being attributed a wait channel incorrectly or the proc format changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-self-wchan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-subset-pid.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-subset-pid.c

Purpose: verifies that mounting procfs with `subset=pid` exposes only pid directories plus `/proc/self` and `/proc/thread-self`, hiding global proc entries like `cpuinfo`.

Important APIs and functions: `make_private_proc()` creates a private mount namespace and remounts `/proc`; `string_is_pid()` validates directory names. It uses `opendir`, `readdir`, `readlink`, `open`, and dirent type checks.

Control flow: unshare mount namespace, make mounts private, mount proc with `subset=pid`, iterate `/proc`, allow only `.`, `..`, `self`, `thread-self`, and numeric pid directory entries, then require `/proc/cpuinfo` readlink and open to fail with `ENOENT`.

State and persistence: remounts `/proc` only in a private namespace, so state is transient.

Dependencies and integration: requires mount namespace and procfs subset option support. `ENOSYS` or `EPERM` during unshare returns skip 4.

Risks and test signals: relies on dirent `d_type` being populated by procfs. Failures show subset filtering regressions or unexpected global entries leaking into a pid-only proc mount.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-subset-pid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-tid0.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-tid0.c

Purpose: stress test that `/proc/$pid/task` never contains a bogus task entry named `0` while a child rapidly creates and joins threads.

Important APIs and functions: uses `fork`, pthread `pthread_create`/`pthread_join`, `opendir`, `readdir`, `strcmp`, `alarm`, and signal handlers.

Control flow: child loops creating one thread at a time. Parent repeatedly scans `/proc/$child/task` for one second. If entry `"0"` appears, parent exits failure; otherwise SIGALRM exits success.

State and persistence: transient child process and thread churn only. `atexit` kills the child.

Dependencies and integration: depends on procfs task directory updates and pthread support.

Risks and test signals: one-second duration is probabilistic but focused on a historical race. Failure means proc task iteration exposed an invalid TID during thread lifecycle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-tid0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-001.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-001.c

Purpose: checks monotonicity between `/proc/uptime` boot time and `CLOCK_BOOTTIME` on a single running process.

Important APIs and functions: uses `proc_uptime()` and `clock_boottime()` from `proc-uptime.h`, `open`, and assertions on centisecond values.

Control flow: open `/proc/uptime`, capture initial proc and clock values, then loop until proc uptime advances by 100 centiseconds. Each iteration requires proc uptime monotonicity, clock monotonicity, and `CLOCK_BOOTTIME` not being behind `/proc/uptime`.

State and persistence: no persistent state, only local timestamp variables.

Dependencies and integration: depends on procfs uptime formatting and POSIX clock support.

Risks and test signals: scheduler delays are tolerated by monotonic comparisons. Failure indicates timekeeping regression or mismatch between proc uptime and boottime sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-002.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-002.c

Purpose: validates the same `/proc/uptime` and `CLOCK_BOOTTIME` monotonic relationship while the process tries to move across all CPUs.

Important APIs and functions: raw `sched_getaffinity` and `sched_setaffinity` syscalls size and set CPU masks. It reuses `proc_uptime()` and `clock_boottime()`.

Control flow: dynamically grow an affinity mask until `sched_getaffinity` succeeds, open `/proc/uptime`, then iterate every possible CPU bit, set affinity to that single CPU if possible, read both clocks, and assert monotonic relationships.

State and persistence: dynamically allocated affinity mask only.

Dependencies and integration: depends on CPU affinity syscalls, proc uptime, and clock boottime. Nonexistent CPUs are ignored by allowing setaffinity failure.

Risks and test signals: tests per-CPU timekeeping consistency. Failures indicate clock/proc uptime going backward or divergent boottime accounting across CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime-002.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime.h

Purpose: shared helpers for proc uptime tests, converting both `/proc/uptime` and `CLOCK_BOOTTIME` into centiseconds for direct comparison.

Important APIs and functions: `clock_boottime()` wraps `clock_gettime(CLOCK_BOOTTIME)`. `proc_uptime()` uses `pread(fd, ..., 0)` and `xstrtoull()` from `proc.h` to parse the first uptime field as seconds plus two decimal digits.

Control flow: helpers assert successful reads and strict expected formatting `seconds.xx idle...`; only the first field is converted.

State and persistence: stateless inline-style helper definitions included by C files.

Dependencies and integration: includes `proc.h`, `<time.h>`, and standard assertions. It assumes `/proc/uptime` always exposes two decimal digits.

Risks and test signals: exact parsing ignores locale and wider fractional precision. Any format change trips assertions in consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc-uptime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc.h

Purpose: common proc selftest helper header with raw PID/TID syscalls, string equality, strict unsigned integer parsing, and safe `readdir` handling.

Important APIs and functions: `sys_getpid()` and `sys_gettid()` call `SYS_getpid` and `SYS_gettid`; `streq()` wraps `strcmp`; `xstrtoull()` parses decimal strings and asserts no errno; `xreaddir()` clears errno and asserts `readdir` failures are real EOF.

Control flow: no standalone control flow; functions are static helpers included in multiple tests.

State and persistence: no persistent state.

Dependencies and integration: central utility for `/proc/self`, `/proc/thread-self`, `/proc/uptime`, and recursive proc read tests.

Risks and test signals: the strict parser asserts on unexpected leading characters and treats a single `0` specially. Misuse on signed or whitespace-prefixed values will abort callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/proc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/read.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/read.c

Purpose: broad procfs smoke test that recursively reads regular files, readlinks symlinks, seeks where available, and writes selected writable proc controls.

Important APIs and functions: `f_reg()` opens files `O_NONBLOCK`, calls `lseek`, and reads; `f_reg_write()` writes to `clear_refs` and `sysrq-trigger`; `f_lnk()` readlinks; recursive `f()` traverses directories using `xreaddir()`. `main()` verifies `/proc` filesystem type `0x9fa0`.

Control flow: open `/proc`, confirm it is procfs, recurse from level 0, validate `.` and `..`, then dispatch on dirent type. Specific writes are attempted for `/proc/sysrq-trigger` and per-process/per-task `clear_refs`; all other regular files are read.

State and persistence: may trigger sysrq help via `"h"` and clear refs for processes. It otherwise only reads live proc state.

Dependencies and integration: depends on procfs, dirent types, and permissions. It returns skip 4 if `/proc` cannot be opened.

Risks and test signals: broad traversal can encounter permission, lifetime, and blocking edge cases, so many open/read failures are tolerated. Assertions catch impossible dirent types or read sizes outside buffer bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/read.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/self.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/self.c

Purpose: verifies `/proc/self` readlink resolves to the caller's thread-group ID.

Important APIs and functions: uses `sys_getpid()` from `proc.h`, `snprintf`, `readlink`, `strlen`, and `streq`.

Control flow: format the current PID as decimal, read `/proc/self`, NUL-terminate the link target, and compare exactly.

State and persistence: none.

Dependencies and integration: depends on procfs self symlink behavior.

Risks and test signals: failure means `/proc/self` is resolving to the wrong pid namespace identity or formatting changed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-dcache.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-dcache.c

Purpose: verifies `/proc/net` follows the current network namespace after `setns()` even when `/proc/net/unix` was already cached in dcache.

Important APIs and functions: uses `unshare(CLONE_NEWNET)`, `socket(AF_UNIX)`, `fork`, pipe synchronization, `/proc/$pid/ns/net`, `setns`, and readback of `/proc/net/unix`.

Control flow: parent enters one netns and creates a UNIX socket as a distinguisher. Child enters a second netns and pauses. Parent opens child's netns fd, opens `/proc/net/unix` to pin old dentry, switches to child netns, kills child, and reads `/proc/net/unix`, requiring only the header line.

State and persistence: transient namespaces, socket, and child process. `atexit` kills the child if needed.

Dependencies and integration: requires network namespaces, UNIX sockets, proc net entries, and setns permission.

Risks and test signals: `CONFIG_UNIX` is required despite a FIXME. Failure indicates cached proc net dentries are not namespace-aware after setns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-dcache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-sysvipc.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-sysvipc.c

Purpose: verifies `/proc/sysvipc` follows the current IPC namespace after `setns()` despite a cached `/proc/sysvipc/shm` dentry.

Important APIs and functions: uses `unshare(CLONE_NEWIPC)`, `shmget` as a namespace distinguisher, `fork`, pipe sync, `/proc/$pid/ns/ipc`, `setns`, and exact header comparison for `/proc/sysvipc/shm`.

Control flow: parent enters IPC namespace and creates shared memory. Child enters another IPC namespace and pauses. Parent pins old `/proc/sysvipc/shm`, switches to child IPC namespace, kills child, and requires the shm file to contain only the architecture-dependent header.

State and persistence: transient IPC namespace and one SysV shm segment in the original namespace. `atexit` kills the child if still present.

Dependencies and integration: requires IPC namespaces, SysV shm, proc sysvipc support, and setns permission.

Risks and test signals: the created shm segment is not explicitly removed, relying on namespace/process lifecycle. Failure indicates stale dcache namespace lookup for sysvipc proc entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/setns-sysvipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/thread-self.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/proc/thread-self.c

Purpose: verifies `/proc/thread-self` resolves to `tgid/task/tid` for both the main thread and a cloned thread.

Important APIs and functions: helper `f()` uses `sys_getpid()`, `sys_gettid()`, `readlink`, and string comparison. `main()` uses `mmap` for a stack and `clone(CLONE_THREAD|CLONE_SIGHAND|CLONE_VM)`.

Control flow: validate in the main thread, allocate a stack, clone a side thread that validates and exits the process, then pause in main.

State and persistence: transient stack mapping and thread only.

Dependencies and integration: depends on procfs `thread-self`, raw clone threading semantics, and the shared signal/VM flags used.

Risks and test signals: the child calls `exit(0)`, terminating the process after success. Failure indicates wrong TID/TGID symlink resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/proc/thread-self.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/Makefile

Purpose: selftest makefile wiring for pstore tests. It declares normal test programs, auxiliary files, cleanup patterns, and a manual crash target.

Important APIs and functions: `TEST_PROGS` lists `pstore_tests` and `pstore_post_reboot_tests`; `TEST_FILES` ships `common_tests` and `pstore_crash_test`; `EXTRA_CLEAN` removes logs and uuid files. `run_crash` invokes the crash script.

Control flow: includes `../lib.mk` for kselftest behavior. `all` is empty because tests are shell scripts.

State and persistence: cleanup covers `logs/*` and `*uuid`, matching state generated by scripts across reboot.

Dependencies and integration: assumes a registered pstore backend and kselftest make infrastructure.

Risks and test signals: `run_crash` intentionally triggers a kernel panic through the script; it should not be part of casual automated runs unless reboot handling is prepared.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/common_tests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/common_tests

Purpose: shared shell library for pstore scripts, defining logging, result accounting, paths, UUID test identity, and backend detection.

Important APIs and functions: `errexit`, `absdir`, `show_result`, `check_files_exist`, and `operate_files`. It creates `LOG_DIR`, `LOG_FILE`, `REBOOT_FLAG`, `UUID`, and `TEST_STRING_PATTERN`; `prlog()` tees output to log.

Control flow: when sourced, it creates a timestamped log directory, logs test header and UUID, reads `/sys/module/pstore/parameters/backend`, logs kernel cmdline, and exits failure if backend detection failed.

State and persistence: creates logs under `logs/<timestamp>_<uuid>/`, writes `uuid` in consumer scripts, and uses `reboot_flag` to bridge crash and post-reboot phases.

Dependencies and integration: assumes pstore module parameters are visible and shell utilities like `date`, `tee`, `ls`, and `cat`.

Risks and test signals: because code executes on source, scripts sourcing it inherit immediate failure if pstore backend is absent. Logging paths are relative to the script directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/common_tests -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/config

Purpose: kselftest config fragment identifying kernel options needed for pstore tests.

Important APIs and functions: not executable code. It requests `CONFIG_MISC_FILESYSTEMS`, `CONFIG_PSTORE`, `CONFIG_PSTORE_PMSG`, `CONFIG_PSTORE_CONSOLE`, and modular `CONFIG_PSTORE_RAM`.

Control flow: consumed by kselftest/kernel config tooling rather than runtime scripts.

State and persistence: no runtime state.

Dependencies and integration: integrates with selftest config collection to help build kernels that expose pstore, pmsg, console, and ramoops backend capabilities.

Risks and test signals: `CONFIG_PSTORE_RAM=m` still requires module loading and backend registration at runtime. Missing backend will be caught by `common_tests`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_crash_test -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_crash_test

Purpose: destructive pstore phase that prepares state, then intentionally crashes the kernel so post-reboot tests can inspect persisted records.

Important APIs and functions: sources `common_tests`, writes `/proc/sys/kernel/sysrq` and `/proc/sys/kernel/panic`, moves `uuid` to `prev_uuid`, touches `reboot_flag`, syncs, then writes `c` to `/proc/sysrq-trigger`.

Control flow: after common backend checks, log intent, enable sysrq, configure panic reboot delay, preserve UUID, mark reboot expected, sync filesystems, and trigger crash.

State and persistence: writes `prev_uuid` and `reboot_flag` in the pstore test directory; relies on pstore backend preserving dmesg, console, and pmsg data across reboot.

Dependencies and integration: requires root, sysrq crash support, panic reboot, and a real pstore backend. It is invoked manually via `make run_crash`.

Risks and test signals: intentionally panics the system. Should only run on disposable or prepared hosts. Failure before crash prevents post-reboot phase from knowing a crash occurred.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_crash_test -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_post_reboot_tests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_post_reboot_tests

Purpose: post-reboot validation that pstore persisted crash records and the pre-crash pmsg UUID, then removes the records.

Important APIs and functions: sources `common_tests`; uses `grep /proc/mounts`, `mount -t pstore`, `check_files_exist`, `operate_files`, `grep_end_trace`, and `rm`.

Control flow: skip with code 4 if `reboot_flag` is absent, otherwise remove it, find or mount pstorefs, cd to mount point, verify `dmesg`, `console`, and `pmsg` files exist, check dmesg and console contain end-trace markers, check pmsg contains exactly one test string matching `prev_uuid`, then remove all backend records.

State and persistence: consumes `reboot_flag` and `prev_uuid`; deletes files from pstorefs after validation.

Dependencies and integration: requires pstorefs mount access and persisted crash data from `pstore_crash_test`.

Risks and test signals: exact oops marker matching and backend-specific file naming can vary. Cleanup deletes all `*-${backend}-*` records, which is intrusive on shared machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_post_reboot_tests -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_tests -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_tests

Purpose: pre-crash pstore validation that console and pmsg support are available and a unique pmsg string can be written for later recovery.

Important APIs and functions: sources `common_tests`, uses `dmesg | grep`, tests `/dev/pmsg0`, writes to `/dev/pmsg0`, and writes `uuid`.

Control flow: verify pstore console registration in dmesg, verify `/dev/pmsg0` exists, write `Testing pstore: uuid=<UUID>` to the pmsg device, record the UUID in the test directory, and exit accumulated result code.

State and persistence: creates `uuid` for `pstore_crash_test` to rename. Writes pmsg content intended to survive crash.

Dependencies and integration: requires pstore backend, pstore console, and pmsg device support.

Risks and test signals: dmesg pattern matching is broad but still format-sensitive. Failure means post-reboot pmsg validation cannot be meaningful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pstore/pstore_tests -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/Makefile

Purpose: kselftest makefile for PTP clock tests.

Important APIs and functions: adds `$(KHDR_INCLUDES)` to CFLAGS, builds generated program `testptp`, links with `-lrt`, and lists `phc.sh` as a shell test.

Control flow: includes `../lib.mk` to inherit selftest build/run rules.

State and persistence: no runtime state.

Dependencies and integration: depends on kernel UAPI headers for `linux/ptp_clock.h` and realtime library linkage.

Risks and test signals: the generated C tool is broad and hardware-dependent; the shell test requires an explicit PTP device argument and root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/phc.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/phc.sh

Purpose: shell functional tests for a PTP hardware clock using `phc_ctl`, covering set time, adjust time, and adjust frequency.

Important APIs and functions: `require_command`, `phc_sanity`, `check_err`, `log_test`, `tests_run`, `cleanup`, and test wrappers `settime`, `adjtime`, `adjfreq`. It parses `phc_ctl` output with `awk`.

Control flow: require root, require a device argument, require `phc_ctl`, verify the device, then run requested tests or all tests. Each test invokes `phc_ctl`, handles "Operation not supported" as skip, checks resulting integer seconds, logs status, and resets the clock in cleanup.

State and persistence: modifies the PTP clock's time and frequency, then attempts cleanup on every test and at exit.

Dependencies and integration: requires linuxptp `phc_ctl`, root, and a valid PHC device such as `/dev/ptp0`.

Risks and test signals: hardware and driver support determine skip/fail. Time checks assume command latency does not move integer seconds outside expected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/phc.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/ptpchmaskfmt.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/ptpchmaskfmt.sh

Purpose: helper to display PTP debugfs timestamp event queue filtering masks in hexadecimal form.

Important APIs and functions: reads integer tokens from a provided debugfs mask file and prints each with `printf '0x%08X '`.

Control flow: set `DEBUGFS_MASKFILE` to argument 1, iterate over all whitespace-separated integers in the file, print hex masks on one line.

State and persistence: read-only.

Dependencies and integration: expects bash, readable debugfs mask file, and numeric contents acceptable to printf.

Risks and test signals: unquoted command substitution intentionally splits whitespace but will also perform glob-like issues if file content is unusual. It is a formatting helper, not a validator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/ptpchmaskfmt.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.c

Purpose: userspace exerciser for the Linux PTP hardware clock ioctl and POSIX clock interfaces. It supports querying capabilities, setting and adjusting PHC time/frequency, timestamp events, periodic outputs, pin configuration, PPS, system/PHC offset measurements, cross timestamps, and event-channel masks.

Important APIs and functions: uses `linux/ptp_clock.h` ioctls including `PTP_CLOCK_GETCAPS`, `PTP_EXTTS_REQUEST{,2}`, `PTP_PIN_GETFUNC/SETFUNC`, `PTP_PEROUT_REQUEST2`, `PTP_ENABLE_PPS`, `PTP_SYS_OFFSET`, `PTP_SYS_OFFSET_EXTENDED`, `PTP_SYS_OFFSET_PRECISE`, `PTP_MASK_CLEAR_ALL`, and `PTP_MASK_EN_SINGLE`. Helpers include `get_clockid()`, `ppb_to_scaled_ppm()`, `pctns()`, `do_flag_test()`, and `usage()`.

Control flow: parse options, open the PTP device read-write or read-only, derive dynamic clockid from fd, then execute each requested operation sequentially. Many operations print perror on failure but continue to allow multi-operation diagnostics.

State and persistence: can modify PHC time, frequency, phase, pin functions, periodic outputs, PPS, and mask state. Channel mask mode waits for user input before exiting.

Dependencies and integration: depends on PTP char device support, kernel UAPI headers, libc time APIs, and often root or device permissions.

Risks and test signals: this is a manual diagnostic and not strictly pass/fail for every operation. Some options intentionally change clocks and may affect attached hardware. Output text is the primary signal for shell wrappers and users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.mk

Purpose: standalone makefile for building the `testptp` utility outside the kselftest `lib.mk` flow.

Important APIs and functions: defines `CC`, kernel header include path `-I$(KBUILD_OUTPUT)/usr/include`, `CFLAGS=-Wall`, `LDLIBS=-lrt`, `PROGS=testptp`, and clean targets.

Control flow: default `all` builds `testptp` from `testptp.o`; `clean` removes object; `distclean` removes object and executable.

State and persistence: build artifacts only.

Dependencies and integration: expects exported `KBUILD_OUTPUT` and optional `CROSS_COMPILE`.

Risks and test signals: unlike the kselftest Makefile, it does not include `KHDR_INCLUDES`; wrong header path can build against stale or missing PTP UAPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptp/testptp.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/Makefile

Purpose: kselftest makefile for ptrace ABI tests.

Important APIs and functions: sets `CFLAGS += -std=c99 -pthread -Wall $(KHDR_INCLUDES)` and builds `get_syscall_info`, `set_syscall_info`, `peeksiginfo`, `vmaccess`, and `get_set_sud`.

Control flow: includes `../lib.mk` for standard build and run behavior.

State and persistence: no runtime state.

Dependencies and integration: requires kernel headers exposing recent ptrace constants and pthread support.

Risks and test signals: some tests depend on ptrace permissions and architecture-specific syscall ABI behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_set_sud.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_set_sud.c

Purpose: tests ptrace get/set support for syscall user dispatch configuration on a stopped tracee.

Important APIs and functions: `sys_ptrace()` raw syscall wrapper; uses `PTRACE_TRACEME`, `PTRACE_GET_SYSCALL_USER_DISPATCH_CONFIG`, `PTRACE_SET_SYSCALL_USER_DISPATCH_CONFIG`, and `struct ptrace_sud_config`.

Control flow: fork child, child requests tracing and SIGSTOPs. Parent waits, gets default SUD config and expects dispatch off/zero fields, sets dispatch on with offset and len, gets it again, and verifies persistence.

State and persistence: configuration is held in the child task until it is killed at test end.

Dependencies and integration: requires kernel ptrace SUD support and kselftest harness.

Risks and test signals: kernels without the new ptrace request will fail. Failures indicate SUD config is not initialized, set, or returned correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_set_sud.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_syscall_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_syscall_info.c

Purpose: validates `PTRACE_GET_SYSCALL_INFO` semantics at signal stops, syscall-entry stops, and syscall-exit stops.

Important APIs and functions: raw `ptrace`, `PTRACE_TRACEME`, `PTRACE_SETOPTIONS(PTRACE_O_TRACESYSGOOD)`, `PTRACE_GET_SYSCALL_INFO`, `PTRACE_SYSCALL`, and `struct ptrace_syscall_info`. `kill_tracee()` and `LOG_KILL_TRACEE` keep failures from leaking children.

Control flow: child stops, then performs `chdir("")`, `gettid`, and `exit_group` with sentinel arguments. Parent iterates wait stops, verifies NONE info at SIGSTOP, verifies entry syscall numbers/args, verifies exit error/value for chdir and gettid, and resumes with `PTRACE_SYSCALL`.

State and persistence: only tracee process state and ptrace stop index.

Dependencies and integration: depends on architecture-independent syscalls plus architecture-specific `arch`, instruction pointer, and stack pointer reporting.

Risks and test signals: exact stop ordering is assumed. Failure points to ptrace syscall info size, op, arguments, return values, or trace option behavior regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/get_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/peeksiginfo.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/peeksiginfo.c

Purpose: tests `PTRACE_PEEKSIGINFO` for private and shared pending signal queues and selected error paths.

Important APIs and functions: raw `rt_sigqueueinfo`, `rt_tgsigqueueinfo`, and `ptrace`; `check_direct_path()` validates queued siginfo order/content; `check_error_paths()` validates unsupported flags and inaccessible output buffers using `mmap`.

Control flow: block `SIGRTMIN`, fork a sleeping child, enqueue ten process-wide and ten thread-directed real-time signals with distinct `si_code` and `si_int`, attach to child, read private queue one at a time and all at once, read shared queue in chunks of three, test error paths, then kill tracee.

State and persistence: pending signals on the child are the tested state.

Dependencies and integration: depends on realtime signals, ptrace attach permission, and memory protection faults.

Risks and test signals: signal queue limits or permission settings can affect setup. Failures indicate wrong queue selection, ordering, copying, or errno behavior for peeksiginfo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/peeksiginfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/set_syscall_info.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/set_syscall_info.c

Purpose: validates `PTRACE_SET_SYSCALL_INFO` by modifying syscall numbers, arguments, and exit results at ptrace syscall stops, then checking both kernel-reported state and tracee-observed behavior.

Important APIs and functions: uses `PTRACE_GET_SYSCALL_INFO`, `PTRACE_SET_SYSCALL_INFO`, `PTRACE_SYSCALL`, `PTRACE_O_TRACESYSGOOD`, `struct ptrace_syscall_info`, and architecture-aware `kernel_ulong_t`. Helpers `check_psi_entry()` and `check_psi_exit()` assert pre/post state.

Control flow: child performs a table of syscalls with expected original entries and expected mutated entries/exits. Parent traces each entry and exit stop, verifies original info, mutates fields, verifies changed info, resumes, and finally requires tracee exit 0 after observing changed syscall behavior.

State and persistence: ptrace-modified syscall state exists only during each stop. Pipes provide valid splice fds for one mutation case.

Dependencies and integration: relies on recent ptrace ABI and architecture details, including s390 syscall number masking and MIPS N32 argument width.

Risks and test signals: exact stop count and mutation semantics are strict. Failures identify broken settable syscall ABI, return-value rewriting, argument rewriting, or info reporting after mutation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/set_syscall_info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/vmaccess.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/vmaccess.c

Purpose: regression tests for `/proc/$pid/mem` and ptrace attach behavior while a multithreaded child is in a de_thread/exec transition with `cred_guard_mutex` held.

Important APIs and functions: kselftest harness tests `vmaccess` and `attach`; helper thread calls `ptrace(PTRACE_TRACEME)`. Uses `fork`, pthreads, `execlp`, open `/proc/$pid/mem`, `PTRACE_ATTACH`, `PTRACE_DETACH`, `kill(SIGCONT)`, and wait status checks.

Control flow: first test forks a child that creates a traced thread and execs `true`; parent sleeps, opens `/proc/$pid/mem`, closes it, and resumes child. Second test expects early `PTRACE_ATTACH` to fail with `EAGAIN`, observes an intermediate child exit, then later attaches to the execed sleep process and detaches cleanly.

State and persistence: transient child process/thread states only.

Dependencies and integration: depends on ptrace restrictions and timing around exec/de_thread.

Risks and test signals: `sleep(1)` timing is heuristic. Failures may signal deadlock regressions, incorrect EAGAIN handling, or task lifetime changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/ptrace/vmaccess.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/Makefile

Purpose: minimal makefile entry point to run a short rcutorture KVM test from the kernel top-level tree.

Important APIs and functions: `all` changes four directories up and invokes `tools/testing/selftests/rcutorture/bin/kvm.sh --duration 10 --configs TREE01`.

Control flow: single default target delegates everything to `kvm.sh`.

State and persistence: creates normal rcutorture result directories through the delegated script.

Dependencies and integration: assumes qemu/KVM tooling and rcutorture scripts are usable from the top-level Linux tree.

Risks and test signals: running `make` here can build kernels and launch qemu. Failures are surfaced by `kvm.sh` and its recheck scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config2csv.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config2csv.sh

Purpose: generates a CSV matrix of Kconfig options and boot parameters across rcutorture scenario files.

Important APIs and functions: reads `CFLIST` by default, expands literal `CFLIST` in arguments, strips comments/blank lines, includes `.boot` file tokens, and dynamically builds an awk script that sorts scenarios and config keys.

Control flow: validate output path, determine scenario list, create temp directory, emit awk assignments for scenario inclusion and option values, run awk to produce CSV, and copy it to requested output.

State and persistence: writes only the requested CSV; temp directory is removed by trap.

Dependencies and integration: designed to run in a config scenario directory. Requires awk with `asorti`, grep, sed, tr.

Risks and test signals: simplistic parsing treats non-`key=value` lines as `key=?`. It is for comparison/reporting, not config validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config2csv.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configNR_CPUS.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configNR_CPUS.sh

Purpose: estimates the CPU count required by a Kconfig fragment for scheduling rcutorture scenarios.

Important APIs and functions: checks `CONFIG_SMP=n`, extracts `CONFIG_NR_CPUS=`, otherwise falls back to `cpus2use.sh`.

Control flow: validate readable fragment, return 1 for UP config, return configured NR_CPUS if present, else call dynamic system CPU estimator.

State and persistence: read-only.

Dependencies and integration: called by `kvm.sh` and `kvm-test-1-run.sh` for batch packing and qemu `-smp` generation.

Risks and test signals: ignores boot-time `nr_cpus` and `maxcpus`; callers adjust those separately via `functions.sh`. Missing fragment exits with error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configNR_CPUS.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config_override.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config_override.sh

Purpose: merges a base Kconfig fragment with an override fragment so override assignments replace conflicting base assignments.

Important APIs and functions: validates both files, generates a pipeline of `grep -v` filters from override variable names, applies it to base, then appends override.

Control flow: create temp directory, convert override lines into shell pipeline text, run it against base, and concatenate override at the end.

State and persistence: writes merged config to stdout only.

Dependencies and integration: used by `kvm-test-1-run.sh` to layer CFcommon, scenario, and command-line Kconfig settings.

Risks and test signals: matching is line-prefix based on text before `=`, so malformed override lines can create bad grep patterns. Later settings always win by construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/config_override.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configcheck.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configcheck.sh

Purpose: verifies a built `.config` satisfies a requested config fragment and reports mismatches.

Important APIs and functions: `test_kconfig_enabled()` checks exact `VAR=value` presence; `test_kconfig_disabled()` treats missing variable or `VAR=n` as disabled. It strips quotes from `.config` and strips `#CHECK#` markers from template.

Control flow: stage config/template into temp files, generate shell checks for disabled options and enabled/non-n options, source those generated scripts, and print mismatch diagnostics.

State and persistence: read-only except temp files.

Dependencies and integration: called by `configinit.sh` and `kvm-recheck.sh`.

Risks and test signals: emits diagnostics but does not explicitly aggregate exit status beyond functions; consumers rely mostly on output presence. Quote stripping can hide meaningful quoted value differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configcheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configinit.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configinit.sh

Purpose: creates a kernel `.config` from a rcutorture config specification and verifies it against the specification.

Important APIs and functions: builds a sed-generated update script to remove conflicting existing config lines, optionally runs `make clean`, runs `$TORTURE_DEFCONFIG`, applies overrides, runs `make oldconfig`, and calls `configcheck.sh`.

Control flow: capture config spec and result dir, generate filters for `CONFIG_*` names, run defconfig, save original `.config`, create new `.config`, run oldconfig with default answers, then verify.

State and persistence: modifies the kernel tree `.config`; writes `Make.clean`, `Make.defconfig.out`, `Make.oldconfig.out`, and `Make.oldconfig.err` into result dir.

Dependencies and integration: used by `kvm-build.sh`; depends on kernel make variables like `TORTURE_KMAKE_ARG`.

Risks and test signals: directly mutates the source tree build config. It exits 0 even if `configcheck.sh` prints mismatches, so callers must inspect diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/configinit.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/console-badness.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/console-badness.sh

Purpose: filters kernel console output for warning, bug, stall, and RCU/KCSAN badness signatures while suppressing known benign lines.

Important APIs and functions: a grep pipeline selects patterns such as `WARNING:`, `BUG`, `Call Trace`, stalls, KCSAN reports, and `!!!`, then removes selected noisy warnings.

Control flow: reads stdin, outputs only suspicious lines not excluded by subsequent filters.

State and persistence: stateless stream filter.

Dependencies and integration: used indirectly by parse-console style tooling in the rcutorture suite.

Risks and test signals: pattern matching is heuristic. It can both miss new failure formats and flag expected test output if filters are stale.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/console-badness.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/cpus2use.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/cpus2use.sh

Purpose: estimates how many host CPUs rcutorture should use when no explicit count is available.

Important APIs and functions: honors `TORTURE_ALLOTED_CPUS`, otherwise counts processors in `/proc/cpuinfo`, optionally estimates idle CPUs via `mpstat`, and uses awk to choose at least one and at least 10 percent of CPUs.

Control flow: return configured allotment if present; compute CPU and idle counts; round up final CPU count.

State and persistence: read-only.

Dependencies and integration: fallback for `configNR_CPUS.sh` and scheduling logic.

Risks and test signals: `/proc/cpuinfo` processor count and `mpstat` field positions are platform/tool-version sensitive. Overestimation can overload hosts; underestimation reduces coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/cpus2use.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/functions.sh

Purpose: shared shell function library for rcutorture scripts, covering argument validation, boot-parameter/config helpers, qemu identification/argument generation, CPU and network qemu options, colored diagnostics, timing, and ftrace extraction.

Important APIs and functions: `checkarg`, `configfrag_boot_params`, `configfrag_boot_cpus`, `configfrag_boot_maxcpus`, `configfrag_hotplug_cpu`, `identify_boot_image`, `identify_qemu`, `identify_qemu_append`, `identify_qemu_args`, `identify_qemu_vcpus`, `specify_qemu_cpus`, `specify_qemu_net`, `print_bug`, `print_warning`, and `extract_ftrace_from_console`.

Control flow: sourced by many scripts; functions are invoked to normalize CLI validation, derive qemu command/image from built kernel architecture, append qemu CPU/net/serial arguments, and parse ftrace sections.

State and persistence: mostly stateless, but uses environment variables such as `TORTURE_QEMU_CMD`, `TORTURE_BOOT_IMAGE`, `TORTURE_QEMU_INTERACTIVE`, and `TORTURE_QEMU_MAC`.

Dependencies and integration: central integration point for `kvm.sh`, `kvm-test-1-run.sh`, recheck scripts, and rerun/remote tooling.

Risks and test signals: architecture detection depends on `file` output and explicit case lists. Argument helper quoting is simple, so callers must avoid whitespace-heavy paths and untrusted strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitter.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitter.sh

Purpose: injects randomized CPU scheduling jitter during torture runs by alternating sleep and spin on randomly selected CPUs.

Important APIs and functions: discovers hotpluggable and non-hotpluggable CPUs via sysfs, uses `taskset` to move itself, uses awk/gawk/date for random durations and elapsed-time checks.

Control flow: loop until duration expires or a sentinel file is removed. Each iteration selects an online CPU, sets affinity, sleeps a random microsecond duration, then spins for a random microsecond duration using a coarse time loop.

State and persistence: controlled by a `jittering` sentinel file; no persistent output unless taskset fails.

Dependencies and integration: launched by `jitterstart.sh` and stopped by `jitterstop.sh` around qemu batches.

Risks and test signals: a bug sets `endsecs=$startns` and `endns=$endns` before spin, making the first timecheck state odd until updated. Heavy jitter can perturb timing-sensitive tests by design.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitter.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstart.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstart.sh

Purpose: starts a requested number of background `jitter.sh` workers for a torture run.

Important APIs and functions: validates count and directory arguments, creates `${jittering_dir}/jittering`, loops from 1 to count, and backgrounds `jitter.sh` with remaining duration/sleep/spin arguments.

Control flow: intended to be sourced by generated run scripts so background jobs remain waitable by the caller.

State and persistence: creates the sentinel file used to keep jitter workers alive.

Dependencies and integration: called through `TORTURE_JITTER_START` generated by `kvm.sh` or transformed by `kvm-transform.sh`.

Risks and test signals: missing arguments exit with nonzero status. It assumes `jitter.sh` is on PATH.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstart.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstop.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstop.sh

Purpose: stops background jitter workers and waits for them to terminate.

Important APIs and functions: validates jitter directory, removes `${jittering_dir}/jittering`, then calls shell `wait`.

Control flow: intended to be sourced after qemu batch completion.

State and persistence: removes the sentinel file created by `jitterstart.sh`.

Dependencies and integration: used by generated `TORTURE_JITTER_STOP` commands.

Risks and test signals: `wait` waits for all background jobs in the current shell, so sourcing context matters. Missing directory argument exits 34.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/jitterstop.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kcsan-collapse.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kcsan-collapse.sh

Purpose: summarizes KCSAN reports across a result tree when a KCSAN run was requested.

Important APIs and functions: checks `TORTURE_KCONFIG_KCSAN_ARG`, finds all `console.log`, extracts `BUG: KCSAN:` lines, strips timestamps, counts unique reports, sorts by frequency, and writes `kcsan.sum`.

Control flow: exit immediately for non-KCSAN runs; otherwise process logs into a summary file in the result directory.

State and persistence: writes `$resultsdir/kcsan.sum`.

Dependencies and integration: called by `kvm-end-run-stats.sh`.

Risks and test signals: collapses only the headline line, not full stack traces, so distinct bugs with same headline may merge.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kcsan-collapse.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-again.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-again.sh

Purpose: reruns an existing rcutorture result directory, optionally changing boot arguments, duration, link/copy mode, remote mode, and output directory.

Important APIs and functions: parses options with `checkarg`, copies or reuses old run directory, removes old runtime artifacts, transforms each `qemu-cmd` via `kvm-transform.sh`, reconstructs batch commands from the old `scenarios` file, and calls `kvm-end-run-stats.sh`.

Control flow: validate kernel tree and old run, determine suite, set result directory, copy/link old run unless inplace, transform qemu commands, generate a run-batches script, optionally dryrun, otherwise execute batches from new rundir and summarize.

State and persistence: creates a new result directory or mutates old one for inplace modes; writes `re-run`, log, transformed qemu commands, and fresh console/qemu outputs.

Dependencies and integration: depends on old run metadata `scenarios` and `torture_suite`, plus qemu command comments.

Risks and test signals: inplace modes can overwrite prior run artifacts. Bootarg transformation assumes single-line qemu commands and simple whitespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-again.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-assign-cpus.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-assign-cpus.sh

Purpose: converts host NUMA/cache topology from sysfs into awk assignments used to distribute qemu CPU affinities.

Important APIs and functions: reads node/cpu/cache `shared_cpu_list` files, selects a cache index that groups CPUs, expands CPU lists with awk, and emits `cpu[node][idx]`, `nodecpus[node]`, and `numnodes`.

Control flow: validate sysfs directory shape; discover index list; choose first shared cache index if available; for each node, output sorted unique CPU assignments.

State and persistence: writes awk statements to stdout only.

Dependencies and integration: used by `kvm.sh` and `kvm-test-1-run-batch.sh`, consumed by `kvm-get-cpus-script.sh`.

Risks and test signals: missing sysfs details are emitted as awk comments with successful exit, causing affinity to be skipped rather than fatal. CPU list parsing assumes comma/range format.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-assign-cpus.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-build.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-build.sh

Purpose: builds a kernel suitable for rcutorture qemu execution from a config template.

Important APIs and functions: checks `TORTURE_STOPFILE`, appends initrd and virtio config options, calls `configinit.sh`, then runs `make -j(2*ncpus)` with `$TORTURE_KMAKE_ARG`. It scans build output for errors and warnings.

Control flow: validate config template, stage config, initialize `.config`, exit on config-init hard failure, build kernel, and reject nonzero make or suspicious output.

State and persistence: modifies/builds the kernel tree and writes `Make.out` plus configinit logs in result dir.

Dependencies and integration: called by `kvm-test-1-run.sh`; depends on generated `TORTURE_INITRD`.

Risks and test signals: treats many warnings in RCU paths as build errors. It can be expensive and mutates build artifacts in the working tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-build.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-end-run-stats.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-end-run-stats.sh

Purpose: appends end-of-run summary diagnostics and returns the recheck status.

Important APIs and functions: sources `functions.sh`, calls `kcsan-collapse.sh`, runs `kvm-recheck.sh`, tees output into run log, and prints elapsed duration via `get_starttime_duration`.

Control flow: validate result directory, establish start time, print summary header, collapse KCSAN reports, run recheck into temp output, append output and final status to log, exit with recheck code.

State and persistence: appends to `$rundir/log` and may create `kcsan.sum`.

Dependencies and integration: final step for `kvm.sh`, `kvm-again.sh`, and remote runs.

Risks and test signals: recheck status is authoritative. If recheck tooling misses a failure, this summary will report success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-end-run-stats.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-find-errors.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-find-errors.sh

Purpose: locates build and runtime diagnostics in an rcutorture result directory and opens them in an editor.

Important APIs and functions: scans `Make.out` for compile/link diagnostics, checks missing kernel artifacts, collects existing `console.log.diags`, and invokes `${EDITOR:-vi}`.

Control flow: validate directory, find build errors and write `.diags`, maybe invoke editor, skip console checks for build-only runs, then open console logs with diagnostics or report no errors.

State and persistence: creates `Make.out.diags` files and possibly other diagnostic files.

Dependencies and integration: used interactively and by `kvm-recheck.sh` with `EDITOR=echo` to count failures.

Risks and test signals: editor invocation is side-effectful and interactive by default. Pattern matching can mark warnings as errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-find-errors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-get-cpus-script.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-get-cpus-script.sh

Purpose: generates an awk helper script that allocates CPU affinity lists across NUMA/cache topology and optionally persists allocation state.

Important APIs and functions: validates CPU arrays and output directory, writes functions `gotcpus()`, `nextcpus(n)`, and `dumpcpustate()` into the output awk script.

Control flow: start awk `BEGIN`, append CPU topology assignments, append optional prior state, define helper functions, and write statefile path into `dumpcpustate()`.

State and persistence: can read and write a state file tracking current node and per-node CPU offsets.

Dependencies and integration: consumes `kvm-assign-cpus.sh` output; used in run batching for stable affinity rotation.

Risks and test signals: generated script is only valid if topology input is valid awk. State from one host topology should not be reused on another.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-get-cpus-script.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-lock.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-lock.sh

Purpose: extracts locktorture progress from a scenario result directory.

Important APIs and functions: greps `console.log` for `"Writes:  Total:"`, extracts acquisition/release count, reads `locktorture.shutdown_secs` from `qemu-cmd`, and computes per-second rate with awk.

Control flow: validate result dir, derive config name, print `-------` if no count, otherwise print count and optional rate.

State and persistence: read-only.

Dependencies and integration: invoked by `kvm-recheck.sh` when `TORTURE_SUITE=lock`.

Risks and test signals: log format changes can produce blank progress. It reports progress but does not detect correctness failures beyond absent output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-lock.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcu.sh

Purpose: extracts rcutorture progress, grace-period rate, final GP state, forward-progress signal, and reader-batch close-call diagnostics.

Important APIs and functions: sources `functions.sh`, greps `console.log` for `ver:`, `End-test grace-period state`, `rcu_torture_fwd_prog`, and `torture: Reader Batch`; computes rates with awk and emits bug/warning via `print_bug`/`print_warning`.

Control flow: validate dir, collect latest counters, print summary, then if reader batch close calls are present, compute normalized rate and create `console.log.rcu.diags` for nonzero close calls.

State and persistence: may write `console.log.rcu.diags`.

Dependencies and integration: suite-specific analyzer called by `kvm-recheck.sh` for rcu runs.

Risks and test signals: progress extraction is format-dependent. Close-call thresholding is heuristic and warns or bugs based on rate and count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale-ftrace.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale-ftrace.sh

Purpose: analyzes ftrace output for rcuscale grace-period performance when sufficient ftrace records are present.

Important APIs and functions: sources `functions.sh`, counts `rcu_exp_grace_period.*start`, then uses sed/grep/awk to pair start/end records, build distributions, detect lost messages, count piggybacking, and compute percentile durations.

Control flow: exit 10 if fewer than 100 start records. Otherwise parse ftrace lines, accumulate grace-period times, print histogram bucket size, distribution, averages, percentiles, maximum, total grace periods, batches, ratio, and lost count.

State and persistence: read-only.

Dependencies and integration: called first by `kvm-recheck-rcuscale.sh`; success suppresses printk-based fallback.

Risks and test signals: assumes ftrace line fields remain stable. Lost or reordered trace messages can reset pairing and affect statistics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale-ftrace.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale.sh

Purpose: analyzes rcuscale performance output, preferring ftrace data and falling back to printk-derived writer-duration records.

Important APIs and functions: calls `kvm-recheck-rcuscale-ftrace.sh`; fallback awk parses `-scale: ... gps: ... batches:`, `writer-duration`, and optional grace-period kthread CPU time.

Control flow: validate result dir and path, try ftrace analyzer, exit success if it works, else parse console log for durations and print histogram, average, min, percentiles, max, GP/batch ratio, and CPU time.

State and persistence: read-only.

Dependencies and integration: suite-specific recheck for rcuscale.

Risks and test signals: if neither ftrace nor printk format is present, it prints "No rcuscale records found???". It is performance summarization, not a strict failure detector by itself.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-rcuscale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-refscale.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-refscale.sh

Purpose: extracts refscale reader timing results from console output and summarizes distribution.

Important APIs and functions: awk detects the `Runs Time(ns)` table, collects numeric duration values, sorts with `asort`, and prints points, average, min, median, and max.

Control flow: validate dir, strip timestamps/carriage returns, parse the first timing table, and print computed summary.

State and persistence: read-only.

Dependencies and integration: suite-specific analyzer used by `kvm-recheck.sh` for refscale.

Risks and test signals: a typo-like statement `dataphase == 2` is a comparison, not assignment, so phase termination may not behave as intended. Format drift can result in no records.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-refscale.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-scf.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-scf.sh

Purpose: extracts scftorture handler invocation progress and rate from a scenario result directory.

Important APIs and functions: greps `console.log` for `scf_invoked_count ver:`, reads `scftorture.shutdown_secs` from `qemu-cmd`, and computes invocations per second.

Control flow: validate dir, print `-------` if no counter, otherwise print count plus optional rate.

State and persistence: read-only.

Dependencies and integration: used by `kvm-recheck.sh` when `TORTURE_SUITE=scf`.

Risks and test signals: output is purely progress-oriented. Missing or changed printk format produces no useful rate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck-scf.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck.sh

Purpose: top-level result validator for rcutorture runs. It checks build artifacts, suite-specific progress, config conformance, oldconfig errors, build diagnostics, console diagnostics, KCSAN summaries, and aggregate failure counts.

Important APIs and functions: finds scenario dirs by `Make.defconfig.out`, sources `functions.sh`, dispatches to `kvm-recheck-$TORTURE_SUITE.sh`, calls `configcheck.sh`, `parse-build.sh`, `parse-console.sh`, `kvm-find-errors.sh`, and uses `print_bug`.

Control flow: for each supplied result tree, iterate scenario dirs, read suite name, remove stale diags, run suite-specific analysis, handle qemu retval and console cases, validate configs, parse logs, then summarize KCSAN. After all dirs, run `EDITOR=echo kvm-find-errors.sh` on the last result and infer return code from diagnostic file counts.

State and persistence: creates/removes `.diags` files and may leave parse outputs such as `Warnings`.

Dependencies and integration: final validation path for `kvm-end-run-stats.sh`.

Risks and test signals: variable `ret` may remain unset on full success, which shells treat as exit 0. It evaluates only the last argument in final `kvm-find-errors.sh` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-recheck.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote-noreap.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote-noreap.sh

Purpose: prevents temporary remote result trees from being reaped during long remote rcutorture runs by periodically touching contained files.

Important APIs and functions: validates a directory argument, loops while it exists, runs `find "$pathname" -type f -exec touch -c {} \;`, sleeps 30 seconds.

Control flow: exit for missing/invalid path; otherwise maintain file mtimes until the directory disappears.

State and persistence: updates modification times of all regular files under the path.

Dependencies and integration: launched in remote per-batch scripts generated by `kvm-remote.sh`.

Risks and test signals: can mask age-based cleanup. It is intentionally noisy in filesystem metadata but suppresses output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote-noreap.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote.sh

Purpose: distributes rcutorture qemu run batches to remote systems after either building a fresh run locally or preparing a rerun from an old result directory.

Important APIs and functions: uses `kvm.sh --buildonly`, `kvm-again.sh --dryrun --remote`, tar packaging, ssh/scp-like streaming, generated `kvm-remote-N.sh` scripts, `checkremotefile()`, `startbatches()`, and final `kvm-end-run-stats.sh`.

Control flow: validate systems list, prepare local temp run directory, build or clone an old run, transform qemu commands for remote execution, package bin/res tree, verify ssh reachability, upload tarball to each system, launch batches on idle systems, wait for `remote.run` sentinels to disappear, collect logs and qemu artifacts back, and summarize.

State and persistence: writes `remote-log` into local oldrun, creates remote temp directories under `/tmp`, uses `remote.run` sentinels, and collects remote result files into local result tree.

Dependencies and integration: requires passwordless ssh, tar, shared script paths, qemu availability on remotes, and compatible `/tmp` behavior.

Risks and test signals: retry logic handles transient upload and ssh failures, but persistent failures can lose results. Remote cleanup removes the temp tree after collection. Quoting assumes simple paths generated by the scripts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-remote.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-series.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-series.sh

Purpose: runs a matrix of specified rcutorture configs across a git commit list, grouping results by config and commit. It is a lightweight comparative runner, not a replacement for bisect.

Important APIs and functions: resolves commits with `git log`, checks out each commit detached, invokes `kvm.sh --build-only`, queues successful builds, then runs them with `kvm-again.sh --link inplace-force` under CPU-budget batching.

Control flow: validate config and commit lists, save current branch, create series result directory, build every config/commit combination, gather qemu run list and CPU requirements, run successful builds concurrently within CPU limit, restore original checkout, print success/build-failure/runtime-failure summaries, and copy log to result tree.

State and persistence: changes git checkout during execution, creates `res/<datestamp>-series`, removes large kernel files for successful runs, and writes temp success/failure lists.

Dependencies and integration: requires clean enough git environment for checkout, qemu/KVM tooling, and rcutorture scripts.

Risks and test signals: destructive to current checkout state if interrupted before restoration. CPU batching is coarse and suppresses affinity to avoid stale affinity reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-series.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-batch.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-batch.sh

Purpose: runs one prepared batch of rcutorture scenarios whose kernels and qemu command files already exist.

Important APIs and functions: validates scenario names and directories, sources qemu-cmd comment settings, starts jitter, derives CPU affinity with `kvm-assign-cpus.sh` and `kvm-get-cpus-script.sh`, launches `kvm-test-1-run-qemu.sh` for each scenario, waits on `build.run` sentinel files, then stops jitter.

Control flow: mark each scenario as running, read shared qemu settings, start jitter, for each scenario generate/export affinity if enabled and background qemu run, busy-wait until all run sentinel files are gone, stop jitter, and log completion.

State and persistence: creates and removes `build.run` sentinels in scenario dirs; writes `kvm-test-1-run-qemu.sh.out`, `qemu-affinity`, and qemu outputs.

Dependencies and integration: used by `kvm-again.sh` and remote scripts.

Risks and test signals: busy-wait loop has no sleep and can consume CPU. Scenario name regex is restrictive. Failure signals appear in per-scenario output and later recheck.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-batch.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-qemu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-qemu.sh

Purpose: executes and monitors one prepared qemu command for a rcutorture scenario, enforcing duration, shutdown grace, stop requests, and hang killing.

Important APIs and functions: reads settings embedded as comments in `qemu-cmd`, rewrites qemu command with optional `taskset`, redirects output, records `qemu-pid`, monitors `console.log`, writes `qemu-retval`, and removes `build.run` when done.

Control flow: validate scenario dir and qemu-cmd, decorate command, start qemu in background, discover pid, optionally wait for gdb attach, monitor until qemu exits, duration expires, or STOP.1 appears. If still running, grant shutdown grace while console output advances, then kill on hang or stop request.

State and persistence: writes `console.log`, `qemu-pid`, `qemu-retval`, `qemu-affinity`, and `Warnings`; removes run sentinel.

Dependencies and integration: called by direct and batch run scripts.

Risks and test signals: tail-based progress heuristics can misclassify quiet shutdowns. Unknown pid prevents killing. Warnings file captures early completion, external termination, and hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run-qemu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run.sh

Purpose: builds or reuses one rcutorture scenario kernel, generates qemu command and bare-metal reproduction instructions, and optionally runs qemu.

Important APIs and functions: sources `functions.sh` and per-suite `ver_functions.sh`; `config_override_param()` layers config fragments; calls `kvm-build.sh`, `identify_qemu`, `identify_boot_image`, `configNR_CPUS.sh`, `configfrag_boot_*`, `specify_qemu_cpus`, `specify_qemu_net`, `identify_qemu_args`, `identify_qemu_append`, `per_version_boot_params`, `kvm-test-1-run-qemu.sh`, `parse-build.sh`, and `parse-console.sh`.

Control flow: create combined ConfigFragment from common, scenario, and command-line options; if rerun base has kernel, reuse it, otherwise build; coordinate `build.wait`/`build.ready`; compute qemu args and boot args; write bare-metal recipe and qemu-cmd with embedded settings; if build-only, stop, else run qemu and parse console.

State and persistence: writes ConfigFragment files, build logs, kernel images, `.config`, `bare-metal`, `qemu-cmd`, run logs, and sentinel files.

Dependencies and integration: central worker invoked by generated `kvm.sh` scripts.

Risks and test signals: mutates kernel build tree and relies on many environment variables. Quoting in qemu-cmd assumes simple argument structure. Build-only and rerun paths rely on consistent result directory naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-test-1-run.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-transform.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-transform.sh

Purpose: rewrites an existing single-line `qemu-cmd` for reruns by changing kernel image, serial console log, jitter directory, duration, and selected boot arguments.

Important APIs and functions: builds an awk program from replacement boot arguments, handles qemu-cmd comments for `seconds`, `TORTURE_JITTER_START`, and `TORTURE_JITTER_STOP`, and transforms `-serial`, `-kernel`, and `-append` fields.

Control flow: validate image, console log, jitter dir, and numeric duration; construct arrays of replacement boot args and parameters; run awk over stdin and emit transformed qemu-cmd to stdout.

State and persistence: no direct file writes except temp awk program; caller redirects output.

Dependencies and integration: used by `kvm-again.sh`.

Risks and test signals: assumes qemu command is one line with no whitespace in filenames. Bootarg replacement is parameter-name based and warns in comments about untrusted input.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm-transform.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm.sh

Purpose: main rcutorture KVM orchestration script. It parses user options, selects scenarios, packs builds/runs into CPU-aware batches, generates a run script, executes it, and records results.

Important APIs and functions: sources `functions.sh`, calls `mkinitrd.sh`, `configNR_CPUS.sh`, `configfrag_boot_cpus`, `configfrag_boot_maxcpus`, `kvm-assign-cpus.sh`, `kvm-get-cpus-script.sh`, `kvm-test-1-run.sh`, and `kvm-end-run-stats.sh`. It manages many environment variables such as `TORTURE_SUITE`, `TORTURE_MOD`, `TORTURE_ALLOTED_CPUS`, `TORTURE_BUILDONLY`, KASAN/KCSAN/GDB options, qemu args, memory, jitter, and shutdown grace.

Control flow: change to kernel top-level, parse options, optionally kill previous lock holders, acquire nonblocking flock, ensure initrd, load suite config list, expand repeated configs, compute CPU counts, greedily bin-pack scenarios, generate a shell script that builds scenarios in batch and runs qemu with optional jitter/affinity, provide dryrun views, or execute and save batches/scenarios metadata.

State and persistence: creates result directory `res/<datestamp>`, log, `torture_suite`, test id, per-scenario dirs, generated `batches` and `scenarios`, STOP file path, and many build/run artifacts. It holds `.kvm.sh.lock`.

Dependencies and integration: top-level interface for local rcutorture selftests, rerun tooling, remote tooling, and series tooling.

Risks and test signals: powerful script that builds kernels, runs qemu, changes `.config`, and consumes CPU. Argument validation is regex-based and quoting is simple. The generated script is the key artifact for debugging dryrun behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/kvm.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mkinitrd.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mkinitrd.sh

Purpose: creates the small initrd used by rcutorture qemu runs if it does not already exist.

Important APIs and functions: validates `tools/testing/selftests/rcutorture`, checks existing `initrd/init`, writes a temporary `init.c`, detects nolibc-supported architectures with the preprocessor, compiles static `init`, and removes source.

Control flow: if init exists, exit success. Otherwise create initrd directory, generate a simple infinite-loop init program that prints command line, sleeps, and burns small userspace time, compile with nolibc when supported or static glibc otherwise, and report success/failure.

State and persistence: writes `tools/testing/selftests/rcutorture/initrd/init` and temporarily `init.c`.

Dependencies and integration: called by `kvm.sh` unless `--no-initrd`; depends on compiler and optional `CROSS_COMPILE`.

Risks and test signals: uses shell redirection to create C source and can fail if static linking is unavailable. The generated init loops forever by design for qemu guest boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/rcutorture/bin/mkinitrd.sh -->
