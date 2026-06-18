# subset-b-006826 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/close_range_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/core/close_range_test.c

## Purpose

`close_range_test.c` is a kselftest harness program for Linux file descriptor table behavior around `close_range(2)`, `CLOSE_RANGE_UNSHARE`, `CLOSE_RANGE_CLOEXEC`, sparse fd tables, clone-shared file tables, and newer `fcntl()` query commands. It is regression-oriented: several cases reproduce syzkaller/bitmap bugs and verify the fd table remains internally consistent after range closing or close-on-exec marking.

## Important APIs, Types, and Functions

The file wraps `syscall(__NR_close_range, fd, max_fd, flags)` as `sys_close_range()` and uses `sys_clone3()` from `../clone3/clone3_selftests.h` with `CLONE_FILES` to create children sharing the parent's fd table. It uses `open()`, `dup2()`, `dup()`, `close()`, `fcntl(F_GETFL)`, `fcntl(F_GETFD)`, `F_DUPFD_QUERY`, `F_CREATED_QUERY`, `getrlimit()/setrlimit(RLIMIT_NOFILE)`, `waitpid()`, `WIFEXITED()`, and `WEXITSTATUS()`. Test definitions come from `kselftest_harness.h`.

## Control Flow

`core_close_range` opens 101 `/dev/null` descriptors, verifies invalid flag handling, checks duplicate-file queries, closes selected ranges, verifies gaps do not matter, and confirms single-fd closure. `close_range_unshare` and `close_range_unshare_capped` repeat range close logic in a `CLONE_FILES` child with `CLOSE_RANGE_UNSHARE`, ensuring the child gets a private table before mutation. `close_range_cloexec` and `close_range_cloexec_unshare` set `FD_CLOEXEC` over two ranges and then from fd 3 to `UINT_MAX`, including under a low soft `RLIMIT_NOFILE`.

The syzbot regressions build sparse tables with descriptors at low fd and fd 1000, then exercise `CLOSE_RANGE_CLOEXEC` with and without `CLOSE_RANGE_UNSHARE`. The bitmap corruption test opens descriptors 2 through 127, unshares and truncates at 64 in a child, then verifies `dup(0)` reuses fd 64 rather than seeing the secondary bitmap as full. `fcntl_created` verifies `F_CREATED_QUERY` distinguishes existing `/dev/null`, a newly created temporary file, and reopening that file.

## State and Persistence Behavior

The main state is process fd table state: open/closed slots, shared versus unshared `files_struct`, close-on-exec bits, and fd allocation bitmaps. The test also temporarily changes the process soft `RLIMIT_NOFILE` in CLOEXEC cases and creates/unlinks temporary `aaaa_N` files. Child processes exit with success/failure to report table state back to the parent.

## Dependencies and Integration Points

The test requires `close_range(2)`, `clone3(2)`, `/dev/null`, kselftest harness support, and Linux-specific fcntl commands that may return `EINVAL` on kernels that lack them. It integrates with the kernel core selftests and targets fs/file-table implementation details, clone fd-table sharing, and exec inheritance semantics.

## Risks and Edge Cases

The tests intentionally stress gaps, `UINT_MAX`/`~0U` bounds, low rlimits, duplicate descriptors sharing the same file object, duplicated descriptors clearing `FD_CLOEXEC`, and descriptor-table shrinking. They skip only selected unsupported syscall/flag cases; environments without `clone3` or enough fd capacity can fail rather than skip. The syzbot tests are sensitive to whether `CLOSE_RANGE_UNSHARE` should isolate the parent from child-side mutations.

## Test Signals

Pass signals are exact `fcntl()` visibility checks, `FD_CLOEXEC` bit checks, child exit code 0, `WCOREDUMP`-independent process exit validation, and successful `F_CREATED_QUERY` results. Failures point to fd closure leaks, lost close-on-exec flags, incorrect unshare semantics, sparse-table corruption, or wrong created-file tracking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/close_range_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/unshare_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/core/unshare_test.c

## Purpose

`unshare_test.c` is a focused regression test for `unshare(CLONE_FILES)` returning `EMFILE` when a shared fd table contains a descriptor above the current `fs.nr_open` limit. It validates kernel behavior when the global maximum open fd count is reduced after a process already holds a high-numbered descriptor.

## Important APIs, Types, and Functions

The test uses `/proc/sys/fs/nr_open`, `getrlimit()/setrlimit(RLIMIT_NOFILE)`, `dup2()`, `sys_clone3()` with `CLONE_FILES`, `unshare(CLONE_FILES)`, `waitpid()`, and kselftest harness assertions. `struct __clone_args` is imported from the clone3 helper.

## Control Flow

The test reads the current `nr_open`, writes a larger value, raises `RLIMIT_NOFILE`, duplicates stderr to `nr_open + 64`, then clones a child sharing file descriptors. The child restores the original `nr_open` before calling `unshare(CLONE_FILES)`, expecting `-1` and `errno == EMFILE`. On every early parent-side setup failure, the original sysctl value is restored before exiting.

## State and Persistence Behavior

The test mutates global `/proc/sys/fs/nr_open`, process rlimits, a high fd slot, and the shared file table. Restoring `nr_open` is critical because the sysctl is host-global. Child exit status persists the result back to the harness.

## Dependencies and Integration Points

It must run as a privileged user able to write `/proc/sys/fs/nr_open`, raise rlimits, use `clone3`, and call `unshare(CLONE_FILES)`. It covers core fdtable allocation and limit validation paths.

## Risks and Edge Cases

The largest risk is environmental: insufficient privilege can leave the test failing or partially changing limits if cleanup paths are interrupted. The interesting kernel edge is a descriptor valid under the old larger limit but invalid after lowering `nr_open`; successful unshare would indicate the kernel copied an fd table beyond the allowed maximum.

## Test Signals

Success is a child exit status of 0 after observing `unshare(CLONE_FILES) == -1` with `errno == EMFILE`. Any different errno, successful unshare, failed restoration, or failed high-fd duplication is a regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/core/unshare_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/Makefile

## Purpose

This Makefile builds and installs the coredump selftest programs and the `stackdump` helper script.

## Important APIs, Types, and Functions

It sets `CFLAGS += -Wall -O0 -g $(KHDR_INCLUDES) $(TOOLS_INCLUDES)`, declares `TEST_GEN_PROGS` as `stackdump_test`, `coredump_socket_test`, and `coredump_socket_protocol_test`, and declares `TEST_FILES := stackdump`.

## Control Flow

The kselftest `../lib.mk` infrastructure handles build and run rules. Additional dependencies link `coredump_test_helpers.c` into each generated C test binary.

## State and Persistence Behavior

The file itself has no runtime state. It persists build metadata and ensures the shared helper source is rebuilt into each executable.

## Dependencies and Integration Points

It integrates with kernel selftest build variables, exported kernel headers, tools headers, and the common kselftest library. The generated tests depend on coredump, pidfd, Unix socket, and fs mount APIs.

## Risks and Edge Cases

If the helper dependency is omitted or stale, individual tests may fail at link time or run against mismatched declarations. `-O0 -g` favors debuggability over optimization.

## Test Signals

Successful `make` should produce all three binaries and copy `stackdump` as a test file. Build failures indicate missing headers, helper compile errors, or lib.mk integration problems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/config

## Purpose

This kselftest config declares the kernel features required by the coredump socket and stackdump tests.

## Important APIs, Types, and Functions

It requests `CONFIG_COREDUMP=y`, `CONFIG_NET=y`, and `CONFIG_UNIX=y`.

## Control Flow

There is no executable control flow. Kselftest/kernel config tooling reads the symbols to determine whether the running or target kernel can support the tests.

## State and Persistence Behavior

The file persists feature requirements only. It does not mutate runtime state.

## Dependencies and Integration Points

`CONFIG_COREDUMP` enables core dump infrastructure, while `CONFIG_NET` and `CONFIG_UNIX` are needed for AF_UNIX socket-based core dump delivery and socketpair/listener setup.

## Risks and Edge Cases

Missing symbols should cause skip or configuration failure rather than misleading runtime failures. The config does not express pidfd or debugfs-style requirements used by some helper calls.

## Test Signals

An environment satisfying these symbols can run the coredump tests; absent symbols predict failures opening socket core patterns or invoking coredump paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_protocol_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_protocol_test.c

## Purpose

`coredump_socket_protocol_test.c` validates the extended coredump socket protocol selected by `@@/path` in `kernel.core_pattern`. It tests request/ack negotiation, coredump data delivery, reject/userspace modes, invalid ack handling, signal metadata exposure through pidfd info, and multiple concurrent crashing tasks.

## Important APIs, Types, and Functions

The file uses the shared coredump fixture and helpers from `coredump_test.h`: `set_core_pattern()`, `create_and_listen_unix_socket()`, `get_peer_pidfd()`, `get_pidfd_info()`, `read_coredump_req()`, `check_coredump_req()`, `send_coredump_ack()`, `read_marker()`, `open_coredump_tmpfile()`, and `process_coredump_worker()`. Kernel protocol types and constants come from `<linux/coredump.h>`, including `struct coredump_req`, `COREDUMP_KERNEL`, `COREDUMP_USERSPACE`, `COREDUMP_REJECT`, `COREDUMP_WAIT`, and `COREDUMP_MARK_*`.

## Control Flow

Each fixture setup saves `core_pattern` and creates a detached tmpfs for temporary core files. A server process binds `/tmp/coredump.socket`, signals readiness to the parent via a socketpair, accepts one or more coredump connections, validates peer pidfd coredump info, reads the request, sends an ack, and then either reads core bytes or expects no bytes depending on the ack.

The individual tests cover kernel-delivered core data, userspace-only ack, explicit reject, conflicting ack flags, unknown ack flags, too-small and too-large ack sizes, SIGSEGV and SIGABRT metadata, five sequential crashing coredumps, and five coredumps copied by forked epoll workers. Parent processes fork crashing children, open pidfds, wait for signal/core status, and validate `PIDFD_INFO_COREDUMP` fields.

## State and Persistence Behavior

The tests temporarily rewrite `/proc/sys/kernel/core_pattern`, create/unlink `/tmp/coredump.socket` and `/tmp/coredump.file`, create anonymous tmpfs files, and spawn crash children, coredump servers, and worker processes. `self->pid_coredump_server` tracks server lifetime for teardown. Runtime protocol state is carried on the accepted AF_UNIX connection.

## Dependencies and Integration Points

The tests require coredump socket support, AF_UNIX sockets, pidfd support including `SO_PEERPIDFD` and `PIDFD_GET_INFO`, tmpfs fsopen/fsmount helpers, and the kselftest harness. They integrate with kernel coredump plumbing, pidfd metadata, and the protocol ABI in `linux/coredump.h`.

## Risks and Edge Cases

The tests are sensitive to privilege because writing `core_pattern` is usually root-only. Timing matters around server readiness and crash completion. Protocol compatibility is checked using minimum sizes and masks, so kernel additions should not break request reading, but unsupported markers or size limits should be surfaced. Concurrent coredumps stress server serialization, pidfd reference handling, and worker fd ownership.

## Test Signals

Positive signals include successful request validation, expected marker receipt, non-empty core files for `COREDUMP_KERNEL`, no data for userspace/reject paths, correct `WCOREDUMP()` results, correct `coredump_signal` and `coredump_code`, and all worker/server exits with status 0. Failures isolate protocol negotiation, pidfd metadata, marker selection, data streaming, or concurrency regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_protocol_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_test.c

## Purpose

`coredump_socket_test.c` validates the simpler `@/path` coredump socket mode. It confirms kernel-originated coredump clients are distinguishable from normal userspace clients, coredump bytes can be captured over AF_UNIX sockets, missing or non-listening sockets suppress core dumps, invalid socket paths are rejected, and pidfd coredump signal/code metadata is correct.

## Important APIs, Types, and Functions

The file uses the coredump fixture from `coredump_test.h`, helper functions from `coredump_test_helpers.c`, `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `get_pidfd_info()`, `SO_PEERPIDFD`, `PIDFD_GET_INFO`, `PIDFD_INFO_COREDUMP`, `PIDFD_INFO_COREDUMP_SIGNAL`, and `PIDFD_INFO_COREDUMP_CODE`. It uses AF_UNIX `socketpair()`, `bind()`, `listen()`, `accept4()`, `connect()`, and normal file I/O to copy coredump bytes.

## Control Flow

The main socket test sets `core_pattern` to `@/tmp/coredump.socket`, starts a listener child, accepts the kernel coredump connection, checks `PIDFD_COREDUMPED`, copies bytes to `/tmp/coredump.file`, and verifies that file is non-empty. `socket_detect_userspace_client` connects a normal child to the same socket and checks that `PIDFD_COREDUMPED` is not set. `socket_enoent` and `socket_no_listener` verify missing and unlistened sockets do not produce coredumps. Signal tests crash by NULL dereference or `abort()` and verify SIGSEGV/SEGV_MAPERR or SIGABRT/SI_TKILL. `socket_invalid_paths` writes malformed `@`/`@@` patterns and expects `set_core_pattern()` failure.

## State and Persistence Behavior

The fixture saves/restores `/proc/sys/kernel/core_pattern`, creates a detached tmpfs, tracks the coredump server pid, and removes `/tmp/coredump.socket` and `/tmp/coredump.file` in teardown. Tests create pidfds and short-lived children; one userspace-client test kills a paused child via pidfd.

## Dependencies and Integration Points

It depends on root-level `core_pattern` writes, AF_UNIX socket support, pidfd metadata support, kselftest harness infrastructure, and `coredump_test_helpers.c`. It integrates directly with kernel core dump routing and pidfd coredump state.

## Risks and Edge Cases

The path validation tests are ABI-sensitive because they expect traversal, spaces, double-at misuse, and triple-at patterns to fail. `socket_no_listener` distinguishes a bound socket path without `listen()` from an active server. Coredump status can be affected by core ulimits or unrelated system policy if the environment blocks dumps.

## Test Signals

Pass signals include server exit status 0, non-empty core file only for true kernel coredumps, no created core file for userspace clients, `WCOREDUMP()` true or false as expected, pidfd coredump flags matching client type, and rejected invalid path writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_socket_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test.h

## Purpose

`coredump_test.h` is the shared declaration and fixture header for coredump selftests. It centralizes fixture state, helper prototypes, protocol helpers, and the server wait helper used by stackdump and socket tests.

## Important APIs, Types, and Functions

It defines `FIXTURE(coredump)` with `original_core_pattern`, `pid_coredump_server`, and `fd_tmpfs_detached`. It declares helpers for crashing child creation, detached tmpfs creation, socket listener setup, `core_pattern` writing, peer pidfd lookup, pidfd info reads, coredump request/ack protocol handling, temporary core-file opening, and epoll worker processing. `wait_and_check_coredump_server()` wraps `waitpid()` and harness assertions.

## Control Flow

There is no standalone test flow. Including tests instantiate setup/teardown functions and call helpers. The inline wait helper marks the server as gone by storing `-ESRCH`, then asserts normal exit status 0.

## State and Persistence Behavior

The fixture state is per-test and tracks persistent host modifications to `core_pattern`, coredump server lifetime, and a detached tmpfs fd that must be closed in teardown.

## Dependencies and Integration Points

It depends on `<linux/coredump.h>`, `kselftest_harness.h`, pidfd test helpers, and the implementation in `coredump_test_helpers.c`. It defines the contract that socket and stackdump tests rely on.

## Risks and Edge Cases

Fixture cleanup correctness is essential because a failed test can otherwise leave `core_pattern` changed or a server process alive. The helper assumes server success is represented by a normal exit code of 0.

## Test Signals

The header enables tests to report harness assertions consistently. `wait_and_check_coredump_server()` failure identifies coredump server-side protocol or copy failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test_helpers.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test_helpers.c

## Purpose

`coredump_test_helpers.c` implements the shared helpers for the coredump selftests: creating crash workloads, mounting detached tmpfs, setting `core_pattern`, accepting AF_UNIX coredump sockets, extracting pidfd metadata, parsing the coredump socket protocol, and copying core data safely.

## Important APIs, Types, and Functions

Important functions are `do_nothing()`, `crashing_child()`, `create_detached_tmpfs()`, `create_and_listen_unix_socket()`, `set_core_pattern()`, `get_peer_pidfd()`, `get_pidfd_info()`, `recv_marker()`, `read_marker()`, `read_coredump_req()`, `send_coredump_ack()`, `check_coredump_req()`, `open_coredump_tmpfile()`, and `process_coredump_worker()`. It uses `sys_fsopen()`, `sys_fsconfig()`, `sys_fsmount()`, `SO_PEERPIDFD`, `PIDFD_GET_INFO`, `O_TMPFILE`, `epoll`, and `MSG_WAITALL`.

## Control Flow

`crashing_child()` spawns 128 sleeping threads and deliberately dereferences NULL. Protocol reading peeks the request size, validates kernel size against `COREDUMP_ACK_SIZE_VER0` and `PAGE_SIZE`, reads the common part, and discards forward-compatible extra bytes. Ack sending can intentionally send smaller or larger structures to test kernel validation. `process_coredump_worker()` switches the coredump fd nonblocking, waits with edge-triggered epoll, drains available bytes into a core file, tolerates `ENOSPC` by continuing, and exits success at EOF.

## State and Persistence Behavior

Helpers create persistent kernel objects and fds: tmpfs mounts represented by fds, Unix socket filesystem entries, pidfds, temporary O_TMPFILE core files, and thread/process state. They write host-global `core_pattern`.

## Dependencies and Integration Points

The implementation depends on Linux fsopen/fsmount syscalls, AF_UNIX sockets, pidfd ioctls, coredump protocol structs, kselftest filesystem wrappers, and the helper declarations in `coredump_test.h`.

## Risks and Edge Cases

`read_coredump_req()` has a forward-compatibility discard path but must avoid blocking on wrong sizes; mismatches surface as protocol failures. `process_coredump_worker()` must close exactly its owned fds after fork. `set_core_pattern()` writes raw strings and relies on the caller to save/restore policy.

## Test Signals

Helper-level failure messages identify setup problems: socket bind/listen, pidfd retrieval, pidfd info ioctl, malformed request sizes/masks, marker mismatch, tmpfile creation, epoll/read/write failures, or worker exit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/coredump_test_helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump

## Purpose

`stackdump` is a shell helper used as a pipe-style `core_pattern` program. It records stack pointer values from every thread of a crashing process into a file.

## Important APIs, Types, and Functions

It accepts crashing process id and output path arguments, uses `mktemp`, iterates `/proc/$pid/task/*`, extracts each task id with `basename`, reads `/proc/$tid/stat`, and appends field 29 via `awk`.

## Control Flow

The script creates a temporary file, appends one stack pointer value per task, then atomically moves the temporary file to the requested output file.

## State and Persistence Behavior

It persists the final stack-value list at the supplied output path and leaves no intended temporary file after `mv`. It reads transient `/proc` task state while the kernel is invoking the pipe helper for a crashing process.

## Dependencies and Integration Points

It depends on procfs task directories, `/proc/<tid>/stat` field layout, POSIX shell tools, and `stackdump_test.c` setting `core_pattern` to invoke it with `%P`.

## Risks and Edge Cases

Task directories can disappear if process teardown races the script, and `/proc/<tid>/stat` parsing by whitespace is fragile if kernel stat layout changes. The script assumes field 29 is the stack pointer.

## Test Signals

The paired test expects the output file to exist, contain one nonzero stack pointer per thread plus the main task, and have exactly `1 + NUM_THREAD_SPAWN` lines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump_test.c

## Purpose

`stackdump_test.c` verifies that pipe-style coredump helpers can inspect all threads of a crashing process and read nonzero stack pointer values from procfs during coredump handling.

## Important APIs, Types, and Functions

The test uses the coredump fixture, `crashing_child()`, `readlink("/proc/self/exe")`, `dirname()`, writes `/proc/sys/kernel/core_pattern`, forks a crashing process, waits for `WCOREDUMP()`, then reads `stack_values` with `getline()` and `strtoull()`.

## Control Flow

Fixture setup saves the original `core_pattern` and creates detached tmpfs. The test computes the test binary directory, writes a pipe pattern invoking `stackdump %P stack_values`, forks a child that spawns 128 threads and crashes, waits for the coredump, polls up to 10 seconds for the output file, then validates every stack value is nonzero and the count equals `1 + NUM_THREAD_SPAWN`.

## State and Persistence Behavior

It temporarily rewrites host `core_pattern`, creates/removes `stack_values`, and uses many child threads. Teardown restores `core_pattern`, kills any leftover server pid, unlinks temporary files, and closes detached tmpfs.

## Dependencies and Integration Points

It depends on root-level core_pattern writes, procfs task visibility, the `stackdump` helper script installed next to the binary, and kselftest harness timeouts.

## Risks and Edge Cases

The test is race-sensitive around helper completion and procfs task state. System coredump policy, core ulimits, or missing script installation can prevent output creation. The expected thread count relies on all pthread creations succeeding.

## Test Signals

Success requires signaled child termination with core dump, output file creation, all stack values nonzero, and exact line count. Failures indicate pipe helper invocation, procfs stack reporting, or multithreaded coredump visibility regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/coredump/stackdump_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/Makefile

## Purpose

This Makefile wires the CPU hotplug shell test into kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := cpu-on-off-test.sh`, includes `../lib.mk`, and defines `run_full_test` to run the script with `-a` and print a pass/fail line.

## Control Flow

Kselftest infrastructure runs the script by default. The explicit `run_full_test` target performs full-scope online/offline cycling.

## State and Persistence Behavior

The Makefile has no runtime state; the script it invokes mutates CPU online sysfs state.

## Dependencies and Integration Points

It depends on the kselftest Makefile framework and a shell environment capable of running CPU sysfs writes as root.

## Risks and Edge Cases

`run_full_test` can offline all hotpluggable CPUs except one, which is more intrusive than the default limited test.

## Test Signals

Build/install success exposes `cpu-on-off-test.sh`; `run_full_test` reports pass when the script returns success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/cpu-on-off-test.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/cpu-on-off-test.sh

## Purpose

`cpu-on-off-test.sh` validates CPU hotplug sysfs control by offlining and onlining one CPU by default or all hotpluggable CPUs with `-a`.

## Important APIs, Types, and Functions

It uses `taskset`, `mount -t sysfs`, `/sys/devices/system/cpu/{online,offline,present}`, per-CPU `cpuN/online`, and helpers `hotpluggable_cpus()`, `cpu_is_online()`, `online_cpu()`, `offline_cpu()`, expectation wrappers, and all-CPU online/offline loops.

## Control Flow

`prerequisite()` requires root, pins the script to CPU0, locates sysfs, confirms CPU hotplug support, and records online/offline/present ranges. Default mode offlines and re-onlines `online_max`, then, if an offline CPU exists, onlines/offlines `present_max` and restores it online. Full mode onlines all offline CPUs, offlines all online hotpluggable CPUs except a reserve CPU, then onlines all again.

## State and Persistence Behavior

The script mutates CPU hotplug state by writing 0/1 to per-CPU `online` files. Default mode attempts to leave CPUs in their original state; full mode ends with all hotpluggable CPUs online. `retval` accumulates failures.

## Dependencies and Integration Points

It requires root, sysfs, more than one CPU, CPU hotplug support, and a shell with Bash features. It integrates with kernel CPU hotplug paths and kselftest skip code 4.

## Risks and Edge Cases

Offlining CPUs is intrusive and can disrupt workloads or tests pinned to affected CPUs. The parsing of CPU range strings uses simple suffix extraction and assumes common range forms. The `present_max` restoration path uses `online_cpu` without expectation checking at the end.

## Test Signals

Pass signals are successful writes and matching sysfs state checks after every online/offline operation. Failures report unexpected success/failure or wrong online/offline state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpu-hotplug/cpu-on-off-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/Makefile

## Purpose

This Makefile registers the cpufreq shell selftest suite with kselftest and lists helper files needed at runtime.

## Important APIs, Types, and Functions

It sets `TEST_PROGS := main.sh`, `TEST_FILES := cpu.sh cpufreq.sh governor.sh module.sh special-tests.sh`, and `EXTRA_CLEAN` for generated cpufreq/dmesg logs.

## Control Flow

The common `../lib.mk` handles installation and execution. `main.sh` is the only test program; the other shell files are sourced helpers.

## State and Persistence Behavior

The Makefile itself persists build/run metadata and cleanup targets. Runtime state is managed by the scripts.

## Dependencies and Integration Points

It integrates with kselftest and expects shell helpers to be copied beside `main.sh`.

## Risks and Edge Cases

If helper files are not listed in `TEST_FILES`, installed tests will fail at `source`. Cleanup only targets known log names.

## Test Signals

Successful kselftest packaging includes all helper scripts and cleans generated log artifacts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/config

## Purpose

This config declares kernel cpufreq features and governors needed by the cpufreq selftests.

## Important APIs, Types, and Functions

It requests `CONFIG_CPU_FREQ`, `CONFIG_CPU_FREQ_STAT`, and governors `POWERSAVE`, `USERSPACE`, `ONDEMAND`, `CONSERVATIVE`, and `SCHEDUTIL`.

## Control Flow

There is no executable flow; config tooling uses these symbols to determine expected kernel capability.

## State and Persistence Behavior

It persists only feature requirements.

## Dependencies and Integration Points

The shell tests expect `/sys/devices/system/cpu/cpufreq` policy directories, governor switching, stats, and optional module testing to align with these symbols.

## Risks and Edge Cases

The config does not guarantee hardware has a cpufreq driver or that every governor is available as a module/built-in. Tests still skip/fail based on runtime sysfs state.

## Test Signals

Kernels with these options should expose enough cpufreq functionality for basic and governor tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpu.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpu.sh

## Purpose

`cpu.sh` provides CPU enumeration and hotplug helper functions for the cpufreq tests.

## Important APIs, Types, and Functions

It defines include guards, sources `cpufreq.sh`, and implements `for_each_cpu()`, `for_each_non_boot_cpu()`, `offline_cpu()`, `online_cpu()`, `reboot_cpu()`, `reboot_cpus()`, `print_unmanaged_cpus()`, and `count_cpufreq_managed_cpus()`.

## Control Flow

Callers set `CPUROOT` and then use iteration helpers to invoke commands over `cpuN` directories. `reboot_cpus()` repeatedly offlines and onlines all non-boot CPUs. Counting and warning helpers inspect per-CPU `cpufreq` directories.

## State and Persistence Behavior

The script mutates CPU online state through `$CPUROOT/$cpu/online`. It reads cpufreq directory presence and maintains only shell-local include guard state.

## Dependencies and Integration Points

It is sourced by `main.sh`, `cpufreq.sh`, `governor.sh`, `module.sh`, and `special-tests.sh`. It depends on root permissions for hotplug writes and sysfs layout.

## Risks and Edge Cases

CPU enumeration uses `ls | grep "cpu[0-9].*"` and boot CPU filtering uses `cpu[1-9].*`, which can include multi-digit CPUs but assumes CPU0 is the only boot CPU to avoid. Hotplug failures propagate through shell command errors only if callers check them.

## Test Signals

Expected signals are printed online/offline actions, managed CPU counts, and warnings for CPUs without cpufreq directories.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpu.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpufreq.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpufreq.sh

## Purpose

`cpufreq.sh` implements cpufreq policy enumeration, sysfs read/write sanity tests, frequency shuffling, suspend/resume validation, and the default basic cpufreq test sequence.

## Important APIs, Types, and Functions

Key functions include `cpu_should_have_cpufreq_directory()`, `for_each_policy()`, `for_each_policy_concurrent()`, `read_cpufreq_files_in_dir()`, `update_cpufreq_files_in_dir()`, `find_current_freq()`, `set_cpu_frequency()`, `test_all_frequencies()`, `shuffle_frequency_for_all_cpus()`, `cpufreq_basic_tests()`, and `do_suspend()`. It reads/writes `$CPUFREQROOT/policy*/scaling_*` and `$SYSFS/power/state`.

## Control Flow

Basic tests count cpufreq-managed CPUs, warn about unmanaged CPUs, recursively read all cpufreq files, rewrite writable files with their current values except `scaling_setspeed`, hotplug non-boot CPUs five times, cycle all available frequencies under the userspace governor, and shuffle all governors. Suspend modes validate sysfs power state, optionally use `rtcwake`, and run basic tests after resume.

## State and Persistence Behavior

It mutates cpufreq governor, frequency, writable policy attributes, CPU online state, and optionally system sleep state. Governor backup/restore is delegated to `governor.sh`; logs are printed to stdout and captured by `main.sh`.

## Dependencies and Integration Points

It requires `CPUROOT`, `CPUFREQROOT`, and `SYSFS` set by `main.sh`, plus helpers from `cpu.sh` and `governor.sh`. It exercises cpufreq core sysfs ABI, governors, hotplug interactions, and suspend/resume integration.

## Risks and Edge Cases

Recursive file rewriting can trigger side effects in writable cpufreq knobs. Frequency tests require `scaling_available_frequencies` and userspace governor support. Suspend/hibernate paths are intrusive and platform-dependent. Shell tests compare numeric strings with `=` and assume common sysfs file availability.

## Test Signals

Success is a complete basic run without `ktap_exit_fail_msg` and with printed cpufreq/dmesg dumps. Failures indicate missing cpufreq management, write rejection, hotplug regressions, unavailable governors/frequencies, or suspend resume cpufreq breakage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/cpufreq.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/governor.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/governor.sh

## Purpose

`governor.sh` provides governor discovery, switching, file inspection, and restore helpers for cpufreq tests.

## Important APIs, Types, and Functions

It defines `find_gov_directory()`, `find_current_governor()`, `backup_governor()`, `restore_governor()`, `__switch_governor()`, `__switch_governor_for_cpu()`, `switch_governor()`, `switch_show_governor()`, `call_for_each_governor()`, and `shuffle_governors_for_all_cpus()`. Global `CUR_GOV` and `CUR_FREQ` store backup state.

## Control Flow

For each policy, callers back up the current governor and, if it is `userspace`, the current frequency. The script reads `scaling_available_governors`, switches to each governor, optionally dumps governor-specific tunables, and restores the original governor/frequency after the loop.

## State and Persistence Behavior

It mutates `scaling_governor` and sometimes `scaling_setspeed`. Backup state is held in global shell variables, so concurrent policy operations can overwrite backups if not used carefully.

## Dependencies and Integration Points

It depends on `$CPUFREQROOT`, `$CPUROOT`, cpufreq sysfs files, and helper functions from `cpufreq.sh`. It is used by basic tests, module tests, and special lockdep/race reproducers.

## Risks and Edge Cases

The backup variables are global rather than per-policy. `switch_show_governor()` assigns `cur_gov=find_current_governor` without command substitution, but this local value is not used for restore. Missing governor directories are reported as `INVALID` but still passed to recursive readers if callers do not guard.

## Test Signals

Pass signals are successful governor writes, readable governor tunables for dynamic governors, and restored original governor/frequency. Failures show unsupported governors or cpufreq policy state corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/governor.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/main.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/main.sh

## Purpose

`main.sh` is the cpufreq selftest entrypoint. It parses requested test mode, validates runtime prerequisites, runs the selected cpufreq scenario, captures logs, and emits KTAP output.

## Important APIs, Types, and Functions

It sources `cpu.sh`, `cpufreq.sh`, `governor.sh`, `module.sh`, `special-tests.sh`, and `../kselftest/ktap_helpers.sh`. Important functions are `helpme()`, `prerequisite()`, `parse_arguments()`, `do_test()`, `clear_dumps()`, and `dmesg_dumps()`.

## Control Flow

The script prints KTAP header, parses `-t`, `-o`, `-d`, and `-g`, sets a plan of 1, checks root/sysfs/cpufreq prerequisites, clears output files, pipes the selected test through `tee`, propagates failure from the pipeline, dumps cpufreq-related and full dmesg logs, then emits one passing KTAP test.

## State and Persistence Behavior

It initializes global `SYSFS`, `CPUROOT`, `CPUFREQROOT`, `FUNC`, `OUTFILE`, `DRIVER_MOD`, and `GOVERNOR_MOD`. It writes `${OUTFILE}.txt`, `${OUTFILE}.dmesg_cpufreq.txt`, and `${OUTFILE}.dmesg_full.txt`.

## Dependencies and Integration Points

It depends on root, sysfs, cpufreq sysfs, taskset, KTAP helpers, and all sourced scripts. It integrates with kselftest as the single `TEST_PROGS` executable for the cpufreq suite.

## Risks and Edge Cases

Most modes are intrusive: hotplug, governor shuffling, suspend/hibernate, and module insertion/removal can perturb a running system. If no CPU is cpufreq-managed, non-module modes fail. The script uses Bash pipeline status to preserve test failure after `tee`.

## Test Signals

The primary signal is one KTAP pass/fail for completion, with detailed stdout and dmesg artifacts for diagnosis. Mode dispatch failures produce `ktap_exit_fail_msg`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/main.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/module.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/module.sh

## Purpose

`module.sh` tests cpufreq driver and governor modules with insertion/removal, basic cpufreq operations, CPU hotplug interaction, and removal protection while a governor is in use.

## Important APIs, Types, and Functions

It defines `test_basic_insmod_rmmod()`, `module_driver_test_single()`, `module_driver_test()`, `find_gov_name()`, `module_governor_test_single()`, `module_governor_test()`, and `module_test()`. It calls `insmod`, `rmmod`, governor helpers, CPU hotplug helpers, and `cpufreq_basic_tests()`.

## Control Flow

Driver tests verify standalone insmod/rmmod, insert the driver and run basic tests, optionally offline non-boot CPUs before insertion and online them after insertion, then remove the driver and check cpufreq directories disappear. Governor tests insert a governor module, switch each policy to the new governor, attempt and expect `rmmod` failure while in use, restore the original governor, then unload. Combined tests exercise driver-before-governor and governor-before-driver orderings.

## State and Persistence Behavior

It mutates loaded kernel modules, CPU online state, cpufreq governor state, and policy sysfs layout. It uses current working directory module filenames passed by the user.

## Dependencies and Integration Points

It requires root, module unload support, cpufreq modules present as `.ko` files, and cpufreq sysfs availability. It integrates cpufreq core with module lifecycle and hotplug paths.

## Risks and Edge Cases

Module insertion/removal can fail if modules are built-in, absent, already in use, or have dependencies. The tests intentionally remove modules and offline CPUs, so they are unsuitable for shared production systems. Some failures are printed and returned rather than always hard-failing.

## Test Signals

Signals include successful insmod/rmmod cycles, successful basic cpufreq tests after insertion, failed governor module removal while active, restored governors, and absence of cpufreq directories after driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/module.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/special-tests.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/special-tests.sh

## Purpose

`special-tests.sh` contains targeted cpufreq regression and stress reproducers for governor switching lockdep reports, concurrent governor races, and CPU hotplug mixed with cpufreq file updates.

## Important APIs, Types, and Functions

It defines `__simple_lockdep()`, `simple_lockdep()`, `__concurrent_lockdep()`, `concurrent_lockdep()`, `quick_shuffle()`, `governor_race()`, `hotplug_with_updates_cpu()`, and `hotplug_with_updates()`. It writes `scaling_governor` and `scaling_min_freq`, reads governor tunables, and calls CPU reboot helpers.

## Control Flow

`simple_lockdep` switches each policy to `ondemand`, reads all ondemand files, then switches to `conservative`. `concurrent_lockdep` repeats that flow 101 times per policy in background. `governor_race` starts eight concurrent loops that rapidly tee `ondemand` and `userspace` into all policies. `hotplug_with_updates` reboots non-boot CPUs thousands of times while writing available frequencies into `scaling_min_freq`, then restores the old minimum.

## State and Persistence Behavior

The script heavily mutates governors, CPU online state, and minimum frequency settings. It launches background jobs and uses global sysfs paths set by `main.sh`.

## Dependencies and Integration Points

It depends on cpufreq policies supporting `ondemand`, `conservative`, and `userspace`, sudo availability for `quick_shuffle`, and CPU hotplug support. It integrates with lockdep and race detection via kernel logs rather than explicit assertions.

## Risks and Edge Cases

These tests are intentionally stressful and can destabilize cpufreq policy state or leave background jobs running until loops finish. `quick_shuffle` uses `sudo tee` despite the main script already requiring root. The script does not explicitly wait for all background jobs in every case.

## Test Signals

The primary signals are absence of kernel lockdep splats, warnings, hangs, or sysfs write failures during and after the stress loops. Dmesg captured by `main.sh` is important evidence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/cpufreq/special-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/Makefile

## Purpose

The DAMON Makefile builds helper binaries and registers sysfs, functionality, and regression tests for DAMON selftests.

## Important APIs, Types, and Functions

It declares `TEST_GEN_FILES += access_memory access_memory_even`, shared `TEST_FILES` for `_damon_sysfs.py`, `drgn_dump_damon_status.py`, and `_common.sh`, and many `TEST_PROGS` including sysfs ABI tests, quota tests, tried-region tests, reclaim/lru_sort tests, and regressions.

## Control Flow

`../lib.mk` builds C helpers and runs scripts. The generated C programs provide synthetic memory access patterns for the Python DAMON tests.

## State and Persistence Behavior

The Makefile persists test inventory and build-clean metadata. Runtime tests mutate DAMON sysfs and module parameters.

## Dependencies and Integration Points

It integrates with DAMON sysfs, DAMON paddr/vaddr, DAMON reclaim, DAMON LRU sort, and debug sanity features.

## Risks and Edge Cases

If helper Python files are not installed as `TEST_FILES`, many tests fail at import or drgn invocation. `EXTRA_CLEAN` only removes `__pycache__`.

## Test Signals

Successful build creates memory access helpers and exposes all DAMON scripts to kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_common.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_common.sh

## Purpose

`_common.sh` provides a minimal shared dependency check for DAMON shell tests.

## Important APIs, Types, and Functions

It defines `check_dependencies()`, which checks effective uid and exits with `$ksft_skip` if not root.

## Control Flow

Shell tests source this file, set `ksft_skip=4`, and call `check_dependencies` before sysfs/module operations.

## State and Persistence Behavior

The script has no persistent state; it only exits on failed prerequisite.

## Dependencies and Integration Points

It depends on callers defining `ksft_skip`. It is used by `sysfs.sh`, `lru_sort.sh`, `reclaim.sh`, and similar DAMON shell tests.

## Risks and Edge Cases

If a caller forgets to define `ksft_skip`, the exit code may be empty or wrong. It checks only root, not DAMON sysfs availability.

## Test Signals

Correct use causes non-root runs to skip instead of fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_common.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_damon_sysfs.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_damon_sysfs.py

## Purpose

`_damon_sysfs.py` is the Python object model used by DAMON tests to construct, stage, start, stop, commit, and query DAMON sysfs configurations under `/sys/kernel/mm/damon/admin`.

## Important APIs, Types, and Functions

Top-level helpers are `write_file()` and `read_file()`. The model includes `Kdamonds`, `Kdamond`, `DamonCtx`, `DamonAttrs`, `IntervalsGoal`, `DamonTarget`, `Damos`, `DamosAccessPattern`, `DamosQuota`, `DamosQuotaGoal`, `DamosWatermarks`, `DamosFilter`, `DamosFilters`, `DamosDests`, `DamosDest`, `DamosStats`, and `DamosTriedRegion`. Runtime operations include `start()`, `stop()`, `commit()`, `commit_schemes_quota_goals()`, `update_schemes_tried_regions()`, `update_schemes_tried_bytes()`, `update_schemes_stats()`, and `update_schemes_effective_quotas()`.

## Control Flow

On import, it locates sysfs in `/proc/mounts` and exits skip if DAMON admin sysfs is unavailable. Object `stage()` methods write nested sysfs files in dependency order: counts first, then generated child directories, then leaf attributes. `Kdamonds.start()` writes `nr_kdamonds`, starts each kdamond, stages contexts, turns state `on`, and reads pid. Update methods write command strings to `state` and then read generated stats/tried-region/effective-quota files back into Python objects.

## State and Persistence Behavior

The library mutates DAMON sysfs globally: number of kdamonds, contexts, targets, schemes, filters, quotas, watermarks, destinations, and runtime state. It stores mirrored values in Python object attributes such as `pid`, `stats`, `tried_regions`, `tried_bytes`, and `effective_bytes`.

## Dependencies and Integration Points

It depends on DAMON sysfs ABI, root permissions, and Python file I/O. Other DAMON tests import it as the canonical control API, making it the integration layer between test logic and kernel DAMON state.

## Risks and Edge Cases

Several constructors use mutable default lists/objects, which can share state across instances if tests reuse them unexpectedly. `DamosFilter.memcg_path` is assigned with a trailing comma, making it a tuple, although string formatting may hide the issue. All sysfs writes return string errors instead of exceptions, so callers must check every return.

## Test Signals

Failures from this module are error strings naming sysfs write/read failures. Successful use produces running kdamond pids and populated stats/tried-region/quota fields for higher-level assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/_damon_sysfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory.c

## Purpose

`access_memory.c` is a synthetic workload for DAMON tests. It allocates a configurable number of regions and touches each for a configurable duration, once or repeatedly.

## Important APIs, Types, and Functions

It defines `enum access_mode`, parses `<number> <size> <time_ms> [repeat]`, allocates `char **regions`, uses `malloc()`, `clock()`, `CLOCKS_PER_SEC`, and `memset()`.

## Control Flow

The program validates arguments, allocates region pointers and backing memory, then loops over regions. For each region it writes bytes until the requested per-region milliseconds elapsed. If mode is `repeat`, the region loop repeats forever.

## State and Persistence Behavior

It allocates anonymous process memory and continuously changes its contents. No files are written; process memory access patterns are observed externally by DAMON.

## Dependencies and Integration Points

DAMON Python tests launch this binary to produce predictable working sets for WSS, quota, and apply-interval tests.

## Risks and Edge Cases

There is no allocation failure handling and no cleanup before exit. Timing uses CPU `clock()` rather than wall time, which can vary with scheduling.

## Test Signals

The signal is external: DAMON should report tried bytes/regions corresponding to the touched region size and access cadence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory_even.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory_even.c

## Purpose

`access_memory_even.c` is a synthetic DAMON workload that allocates multiple regions and continuously accesses only even-numbered regions.

## Important APIs, Types, and Functions

It parses `<number> <size_bytes>`, allocates region pointers and regions with `malloc()`, and writes to even-indexed regions with `memset()`.

## Control Flow

After allocation, it enters an infinite loop over all regions. For indexes divisible by two, it writes `i` into the region; odd regions remain idle.

## State and Persistence Behavior

It keeps allocated anonymous memory alive and mutates half the regions indefinitely. No persistent files are written.

## Dependencies and Integration Points

DAMON tests use it to validate region counting and access-pattern detection where active/inactive regions should be distinguishable.

## Risks and Edge Cases

It does not check allocation failures and never exits naturally. Test callers must terminate it.

## Test Signals

DAMON tried regions and region-count bounds should reflect the configured number of regions, especially in `damon_nr_regions.py` and `damos_tried_regions.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/access_memory_even.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/config

## Purpose

This config declares DAMON features required by the DAMON selftest suite.

## Important APIs, Types, and Functions

It requests `CONFIG_DAMON`, `CONFIG_DAMON_SYSFS`, `CONFIG_DAMON_PADDR`, `CONFIG_DAMON_VADDR`, `CONFIG_DAMON_RECLAIM`, `CONFIG_DAMON_LRU_SORT`, and `CONFIG_DAMON_DEBUG_SANITY`.

## Control Flow

There is no runtime flow; kselftest config tooling consumes the symbols.

## State and Persistence Behavior

It persists only kernel capability requirements.

## Dependencies and Integration Points

These symbols match the sysfs model, physical/virtual address monitoring, reclaim/lru_sort module parameter tests, and debug sanity assertions used by the suite.

## Risks and Edge Cases

Having the config does not guarantee runtime root permissions, drgn availability, or idle kdamond state required by some tests.

## Test Signals

Kernels with these options should expose `/sys/kernel/mm/damon/admin` and module parameter files used by the suite.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damon_nr_regions.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damon_nr_regions.py

## Purpose

`damon_nr_regions.py` verifies DAMON keeps monitored region counts within configured `min_nr_regions` and `max_nr_regions`, including after online tuning.

## Important APIs, Types, and Functions

It uses `subprocess.Popen()` to run `access_memory_even`, `_damon_sysfs.Kdamonds`, `DamonCtx`, `DamonAttrs`, `DamonTarget`, `Damos`, `start()`, `commit()`, `stop()`, and `update_schemes_tried_regions()`.

## Control Flow

`test_nr_regions()` launches a process with a real region count, starts DAMON in `vaddr` mode with specified min/max region parameters, samples tried-region counts up to 10 times, and fails if any count falls outside bounds. `main()` tests min greater than real, max less than real, then starts with wide bounds, commits tighter bounds online, waits for merge, and verifies the new max is honored.

## State and Persistence Behavior

It starts/stops kdamond sysfs state and manages a child workload process. Region-count samples are held in memory and sorted for checks.

## Dependencies and Integration Points

It depends on `access_memory_even`, DAMON vaddr monitoring, sysfs commit support, and tried-region update commands.

## Risks and Edge Cases

Timing affects when real regions are discovered and merged. The script must terminate the workload on errors to avoid leaving a busy process. A slow system may need more time than the fixed sleeps.

## Test Signals

Pass messages report each region-bound scenario. Failures print collected counts or a specific online-tuned max violation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damon_nr_regions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_apply_interval.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_apply_interval.py

## Purpose

`damos_apply_interval.py` verifies DAMOS `apply_interval_us` changes how often a scheme is tried.

## Important APIs, Types, and Functions

It launches `access_memory`, creates two `Damos` schemes with the same access pattern but different `apply_interval_us`, then reads `DamosStats.nr_tried` through `_damon_sysfs.update_schemes_stats()`.

## Control Flow

The workload touches two 10 MiB regions for two seconds each. DAMON starts with two schemes: one using the aggregation interval by setting apply interval 0, and one using 10 ms. After the workload exits, the script compares `nr_tried` counts and expects the shorter interval scheme to be tried at least nine times more often.

## State and Persistence Behavior

It mutates DAMON sysfs runtime state and collects per-scheme stats in Python objects. The child process exits naturally after completing memory accesses.

## Dependencies and Integration Points

It depends on DAMOS stats, vaddr monitoring, and the access workload. It validates the sysfs `apply_interval_us` setting against runtime accounting.

## Risks and Edge Cases

The expected ratio is timing-sensitive and may be noisy on overloaded systems. The script does not explicitly stop kdamond at the end, relying on process/test cleanup behavior.

## Test Signals

Failure occurs if either scheme has zero tries or the try ratio is below 9. Success is silent exit 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_apply_interval.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota.py

## Purpose

`damos_quota.py` verifies DAMOS byte quota enforcement and quota-exceed accounting.

## Important APIs, Types, and Functions

It uses `access_memory`, `_damon_sysfs.DamosQuota`, `DamosAccessPattern`, `update_schemes_tried_bytes()`, and `update_schemes_stats()`. The quota is 1 MiB per 100 ms reset interval.

## Control Flow

The script runs a two-region access workload, starts a vaddr DAMON context with one matching scheme and a size quota, samples tried bytes and stats every 100 ms while the workload runs, sorts samples, and fails if any tried byte sample exceeds the quota or if `qt_exceeds` is lower than the number of samples exactly at the quota.

## State and Persistence Behavior

It starts kdamond, mutates DAMON scheme quota state, samples runtime stats, and terminates when the workload exits.

## Dependencies and Integration Points

It depends on DAMOS quota support, tried-bytes update support, stats accounting, and the access workload producing enough hot memory to hit quota.

## Risks and Edge Cases

Timing and workload variability can affect quota samples. The script does not explicitly call `kdamonds.stop()` at the end.

## Test Signals

Failures print quota-violating samples or mismatch between expected and reported quota exceed counts. Exit 0 means all observed tried bytes stayed within the configured quota.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota_goal.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota_goal.py

## Purpose

`damos_quota_goal.py` verifies user-input quota goals dynamically tune effective DAMOS quotas in the expected direction.

## Important APIs, Types, and Functions

It uses `_damon_sysfs.DamosQuotaGoal`, `DamosQuota`, `commit_schemes_quota_goals()`, and `update_schemes_effective_quotas()`. The goal metric is `user_input`.

## Control Flow

The script starts a vaddr stat scheme with one quota goal and reset interval 100 ms. While the workload runs, it cycles current values `[0, 15000, 5000, 18000]`, commits the quota goal, samples effective bytes before and after 0.5 seconds, and checks whether effective quota increased when current value is below target and decreased when above target, except when already at minimum 1 byte.

## State and Persistence Behavior

It mutates the quota goal's `current_value` in sysfs and stores `effective_bytes` in the goal object. It runs a short-lived memory workload.

## Dependencies and Integration Points

It depends on DAMOS quota goal sysfs support and the kernel's effective quota tuner.

## Risks and Edge Cases

The test assumes effective quota changes within 0.5 seconds and that initial effective bytes are nonzero. It is sensitive to tuner implementation details.

## Test Signals

It prints score and effective quota transitions. Failures indicate no change or a change opposite to expectation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_quota_goal.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_tried_regions.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_tried_regions.py

## Purpose

`damos_tried_regions.py` verifies DAMOS tried-region reporting produces a plausible number of regions for a synthetic even-region workload.

## Important APIs, Types, and Functions

It runs `access_memory_even`, starts `_damon_sysfs.Kdamonds` with `DamonCtx(ops='vaddr')`, one target, and a `stat` scheme, then calls `update_schemes_tried_regions()`.

## Control Flow

The script samples tried-region counts every 100 ms until it has more than 10 samples, sorts them, and uses the median-ish fifth sample as a stability check. It expects that value to be at least 14 for a 14-region workload.

## State and Persistence Behavior

It starts a kdamond and a child workload, stores sampled counts in memory, and terminates the workload before evaluating.

## Dependencies and Integration Points

It depends on DAMON vaddr monitoring, tried-region sysfs export, and the `access_memory_even` helper.

## Risks and Edge Cases

Region discovery is timing-sensitive and can undercount on slow or noisy systems. The failure path tries to join integer values directly, which may itself be buggy if reached.

## Test Signals

Success prints the 50th percentile count and expectation met. Failure indicates tried-region reporting did not expose enough regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/damos_tried_regions.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/drgn_dump_damon_status.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/drgn_dump_damon_status.py

## Purpose

`drgn_dump_damon_status.py` is a drgn script that reads live kernel DAMON structures for a kdamond pid and dumps selected fields as JSON for tests to compare against sysfs-staged configurations.

## Important APIs, Types, and Functions

It uses drgn helpers `find_task()`, `cast()`, `list_for_each_entry()`, and object field conversion helpers. Converters include `attrs_to_dict()`, `target_to_dict()`, `damos_access_pattern_to_dict()`, `damos_quota_to_dict()`, `damos_watermarks_to_dict()`, `damos_filter_to_dict()`, `scheme_to_dict()`, and `damon_ctx_to_dict()`.

## Control Flow

The script obtains a drgn program, parses `<kdamond pid> <file>`, reads `find_task(prog, pid).worker_private` as `struct kthread`, casts its `data` to `struct damon_ctx *`, converts one context to nested dictionaries/lists, and writes JSON to stdout or the requested file.

## State and Persistence Behavior

It does not mutate kernel state. It reads live kernel memory and persists a JSON snapshot if a filename is supplied.

## Dependencies and Integration Points

It depends on drgn, kernel debug type information sufficient for DAMON structs, Linux helper APIs, and stable internal DAMON struct field names. `sysfs.py` and `sysfs_no_op_commit_break.py` call it.

## Risks and Edge Cases

It is tightly coupled to internal kernel structs, including `worker_private` layout and DAMON field names. A typo checks `hugeapge_size` rather than `hugepage_size`, limiting that filter dump path. Missing drgn or debug symbols causes callers to fail or skip depending on wrapper logic.

## Test Signals

JSON output is compared against expected sysfs settings. Mismatches identify failed commit, wrong enum mapping, lost filters, quotas, attrs, targets, or schemes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/drgn_dump_damon_status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/lru_sort.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/lru_sort.sh

## Purpose

`lru_sort.sh` verifies the `damon_lru_sort` module parameter toggles a kdamond on and off.

## Important APIs, Types, and Functions

It sources `_common.sh`, checks `/sys/module/damon_lru_sort/parameters/enabled`, uses `pgrep kdamond`, and writes `Y` then `N` to the parameter.

## Control Flow

After root and file checks, it skips if another kdamond is already running. It enables LRU sort, expects exactly one kdamond, disables it, and expects zero kdamonds.

## State and Persistence Behavior

It mutates the global `damon_lru_sort` enabled parameter and process state by starting/stopping a kdamond.

## Dependencies and Integration Points

It depends on DAMON_LRU_SORT built as a module or exposing the parameter, and no preexisting kdamond.

## Risks and Edge Cases

Other DAMON users cause skip. A stale kdamond or delayed shutdown can make counts inaccurate.

## Test Signals

Success is one kdamond after enabling and zero after disabling; failures report not turned on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/lru_sort.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/reclaim.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/reclaim.sh

## Purpose

`reclaim.sh` verifies the `damon_reclaim` module parameter can start and stop a kdamond.

## Important APIs, Types, and Functions

It checks `/sys/module/damon_reclaim/parameters/enabled`, uses `pgrep kdamond`, and writes `Y`/`N`.

## Control Flow

After root/dependency checks, it skips if another kdamond exists, enables reclaim and expects one kdamond, disables reclaim and expects zero.

## State and Persistence Behavior

It mutates the global DAMON reclaim enabled parameter and resulting kdamond process state.

## Dependencies and Integration Points

It depends on DAMON_RECLAIM support and the module parameter ABI.

## Risks and Edge Cases

Concurrent DAMON users cause skip. Slow kdamond teardown can produce false failures.

## Test Signals

Pass is exact kdamond process count transitions 0 -> 1 -> 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/reclaim.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.py

## Purpose

`sysfs.py` verifies that DAMON sysfs configurations are committed to live kernel DAMON contexts, using drgn to compare internal structures against Python model objects.

## Important APIs, Types, and Functions

It defines many assertion helpers for watermarks, quota goals, quotas, migrate destinations, filters, access patterns, schemes, monitoring attrs, targets, contexts, and kdamonds. It uses `_damon_sysfs`, `drgn_dump_damon_status.py`, JSON loading, and `subprocess`.

## Control Flow

The script starts a minimal kdamond, dumps and asserts it, replaces the context with a complex configuration containing attrs, pageout scheme, quota goal, temporal goal tuner, watermarks, migrate destinations, core/ops filters, and commits it. It then commits a minimum context, stops, starts a vaddr context with three shell targets, marks one target obsolete, commits, removes it from the expected model, and asserts live state.

## State and Persistence Behavior

It mutates DAMON sysfs and kdamond live state, writes `damon_dump_output`, and spawns shell processes as monitoring targets. It stores expected state in Python objects.

## Dependencies and Integration Points

It depends on `_damon_sysfs.py`, drgn, kernel debug info, DAMON sysfs commit support, and internal DAMON struct layout. It integrates sysfs ABI with live in-kernel object verification.

## Risks and Edge Cases

Missing drgn turns into failure after starting kdamond. Enum mapping typos in test expectations can produce false failures when kernel enums change. The obsolete target case depends on shell process lifetime and commit ordering.

## Test Signals

Failures print unexpected field names and JSON dumps, making mismatched committed state visible. Success means sysfs-staged attrs, schemes, filters, quotas, destinations, and target obsolescence reached live DAMON structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.sh

## Purpose

`sysfs.sh` validates the shape, permissions, dynamic directory creation/removal, and selected input validation of the DAMON admin sysfs ABI.

## Important APIs, Types, and Functions

It defines assertion helpers `ensure_write_succ()`, `ensure_write_fail()`, `ensure_dir()`, `ensure_file()`, and per-subtree testers for ranges, tried regions, stats, filters, watermarks, weights, goals, quotas, access patterns, schemes, regions, targets, monitoring attrs, contexts, kdamonds, and the whole DAMON sysfs root.

## Control Flow

The script checks root, then walks `/sys/kernel/mm/damon/admin/kdamonds`. It writes count files such as `nr_kdamonds`, `nr_contexts`, `nr_targets`, `nr_schemes`, `nr_filters`, `nr_goals`, and `nr_regions` to create and remove child directories, checking expected files and permissions at each level. It also tests valid and invalid filter type writes.

## State and Persistence Behavior

It mutates DAMON sysfs topology by creating/removing kdamonds, contexts, targets, regions, schemes, filters, and goals. It does not intentionally start monitoring.

## Dependencies and Integration Points

It depends on DAMON sysfs ABI and root permissions. It gives low-level coverage for the file tree consumed by `_damon_sysfs.py`.

## Risks and Edge Cases

The script contains a likely typo `ensure_file "$context_dir/avail_operations" "exit" 400`, which may bypass intended existence checking. It also references `$dir` in one branch of `ensure_file()`. ABI permission changes will break assertions.

## Test Signals

Failures name the missing directory/file, permission mismatch, unexpected write success/failure, or dynamic directory lifecycle error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_memcg_path_leak.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_memcg_path_leak.sh

## Purpose

`sysfs_memcg_path_leak.sh` is a regression test for memory leaks when repeatedly writing DAMOS filter `memcg_path`.

## Important APIs, Types, and Functions

It uses DAMON sysfs, debugfs kmemleak at `/sys/kernel/debug/kmemleak`, and shell writes to configure one filter under one scheme.

## Control Flow

The script requires root, DAMON sysfs, and kmemleak. It creates one kdamond/context/scheme/filter, writes the same memcg path string 128 times, triggers `kmemleak` scan, and fails if the kmemleak report is non-empty.

## State and Persistence Behavior

It mutates DAMON sysfs and kmemleak scan state. It does not start kdamond monitoring.

## Dependencies and Integration Points

It depends on kmemleak being enabled and readable, plus DAMON filter sysfs support.

## Risks and Edge Cases

Existing kmemleak reports unrelated to this test can cause false failures. The script does not clear kmemleak before the repeated writes.

## Test Signals

Empty kmemleak output after scan is success; any report is printed and exits failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_memcg_path_leak.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_no_op_commit_break.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_no_op_commit_break.py

## Purpose

`sysfs_no_op_commit_break.py` verifies that committing an unchanged DAMON sysfs configuration does not alter live DAMON state, particularly for schemes with ops filters.

## Important APIs, Types, and Functions

It uses `_damon_sysfs`, `drgn_dump_damon_status.py`, JSON comparison, and a `Damos` scheme containing an `ops_filters` anon allow filter.

## Control Flow

The script starts a kdamond, dumps live DAMON status, calls `commit()` without changing the model, dumps status again, compares the two JSON objects for exact equality, and stops kdamond.

## State and Persistence Behavior

It starts/stops DAMON and writes `damon_dump_output` through the drgn helper. The expected state is the before/after JSON snapshot.

## Dependencies and Integration Points

It depends on drgn, DAMON sysfs commit, ops filters, and live structure dumping. It is a regression test for commit idempotence.

## Risks and Edge Cases

Exact JSON equality can fail if live fields legitimately change during runtime, even if config is unchanged. Missing drgn causes failure.

## Test Signals

Failure prints before and after JSON. Success means no-op commit preserved live DAMON context state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_no_op_commit_break.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_removed_scheme_dir.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_removed_scheme_dir.sh

## Purpose

`sysfs_update_removed_scheme_dir.sh` is a regression test ensuring update commands do not trigger kernel bugs after a scheme sysfs directory is removed while monitoring is active.

## Important APIs, Types, and Functions

It uses DAMON admin sysfs, `dmesg -C`, `dmesg | grep BUG`, scheme count writes, and kdamond state commands `on`, `update_schemes_stats`, `update_schemes_tried_regions`, and `off`.

## Control Flow

The script configures one vaddr context monitoring its own pid with one scheme, starts DAMON, sleeps briefly, removes the scheme by writing `nr_schemes=0`, issues stats and tried-regions update commands, checks dmesg for BUG after each, then stops DAMON.

## State and Persistence Behavior

It mutates DAMON sysfs topology and live kdamond state, and clears kernel logs at start.

## Dependencies and Integration Points

It depends on root, DAMON sysfs, vaddr monitoring, dmesg access, and kernel debug reporting of BUG splats.

## Risks and Edge Cases

Clearing dmesg is intrusive. Lack of dmesg permission can affect detection. The test detects BUG strings, not all possible warnings or memory errors.

## Test Signals

Success is no `BUG` in dmesg after both update commands. Failure prints the triggering dmesg.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_removed_scheme_dir.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_hang.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_hang.py

## Purpose

`sysfs_update_schemes_tried_regions_hang.py` is a regression reproducer for hangs while repeatedly updating DAMON tried bytes/tried region related state for a process with an access pattern that should not match.

## Important APIs, Types, and Functions

It launches `sleep 2`, starts `_damon_sysfs.Kdamonds` with a vaddr context and one scheme whose access pattern requires `nr_accesses=[200, 200]`, and repeatedly calls `update_schemes_tried_bytes()`.

## Control Flow

The script starts DAMON on the sleep process, then loops until the process exits, issuing tried-bytes update commands as fast as the loop permits. Any update error fails the test.

## State and Persistence Behavior

It mutates live DAMON state and polls a short-lived child process. No explicit stop is called after the child exits.

## Dependencies and Integration Points

It depends on DAMON vaddr and tried-bytes update support. It targets update-command liveness rather than content accuracy.

## Risks and Edge Cases

If the kernel hangs, the test stalls. The script does not sleep in the update loop, so it can be CPU-intensive for two seconds.

## Test Signals

Exit 0 after the sleep process exits indicates no hang or update error. Any printed update failure is a regression signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_hang.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_wss_estimation.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_wss_estimation.py

## Purpose

`sysfs_update_schemes_tried_regions_wss_estimation.py` verifies DAMON tried-bytes based working-set-size estimation is close to the synthetic workload size.

## Important APIs, Types, and Functions

It uses `access_memory` in repeat mode, `_damon_sysfs.Kdamonds`, `DamosAccessPattern`, `update_schemes_tried_bytes()`, and percentile/error calculations.

## Control Flow

`pass_wss_estimation()` runs a two-region workload for a given region size, starts vaddr DAMON with a hot/old access pattern, collects up to 40 tried-byte samples, stops DAMON, sorts samples, and checks 50th and 75th percentile errors are within 20 percent. `main()` tries region sizes from 10 MiB up to 160 MiB, accepting the first passing size because large TLBs can hide smaller working sets.

## State and Persistence Behavior

It starts/stops DAMON and workload processes for each attempted size and stores samples in memory.

## Dependencies and Integration Points

It depends on the access workload, DAMON vaddr sampling, tried-bytes updates, and architecture behavior around TLB/access tracking.

## Risks and Edge Cases

The test is inherently noisy and compensates by retrying larger working sets. It can consume up to hundreds of MiB and run repeated monitoring sessions.

## Test Signals

Success prints acceptable percentile errors for one size. Failure prints unacceptable samples for all attempted sizes and exits 1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/damon/sysfs_update_schemes_tried_regions_wss_estimation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/Makefile

## Purpose

This Makefile registers the device error log scanner as a kselftest program.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test_device_error_logs.py` and includes `../../lib.mk`.

## Control Flow

The kselftest framework runs the Python script.

## State and Persistence Behavior

No runtime state is stored by the Makefile.

## Dependencies and Integration Points

It integrates with devices selftests and common kselftest packaging.

## Risks and Edge Cases

If the Python script is not executable or dependencies are missing, the kselftest run fails.

## Test Signals

The Makefile succeeds when the script is installed/runnable by kselftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/test_device_error_logs.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/test_device_error_logs.py

## Purpose

`test_device_error_logs.py` scans `/dev/kmsg` for kernel error-or-worse messages tagged with `DEVICE=` and reports one failed KTAP test per affected device.

## Important APIs, Types, and Functions

It imports `ksft`, parses kmsg lines with `RE_log`, parses continuation tags with `RE_tag`, defines `PREFIX_ERROR = 3`, and implements `parse_kmsg()` and `generate_per_device_error_log()`.

## Control Flow

The script opens `/dev/kmsg`, switches it nonblocking, iterates available log lines, accumulates structured log dictionaries, groups logs whose priority prefix is <= 3 by `DEVICE`, then emits a KTAP plan equal to the number of devices with errors. Each such device produces a failed test and prints the messages; zero devices prints an informational message and a zero-test plan.

## State and Persistence Behavior

It reads kernel log state but does not clear or mutate it. Parsed logs are held in memory.

## Dependencies and Integration Points

It depends on `/dev/kmsg` readability, kernel device log tags, Python regex parsing, and `ksft` from the kselftest tree.

## Risks and Edge Cases

Existing historical kmsg errors can fail the test even if unrelated to the current run. Nonblocking iteration may miss logs written after the initial read. The last `current_log` is appended only when a new log line arrives, so the final log can be dropped.

## Test Signals

No device error logs is success with zero tests. Any device with error/critical logs is a failure named by device id and accompanied by messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/error_logs/test_device_error_logs.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/Makefile

## Purpose

This Makefile registers the discoverable-device probe test and board database with kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test_discoverable_devices.py`, `TEST_FILES := boards`, and includes `../../lib.mk`.

## Control Flow

Kselftest runs the Python probe script and installs the `boards` directory as data.

## State and Persistence Behavior

The Makefile itself has no runtime state.

## Dependencies and Integration Points

It integrates platform-specific YAML device descriptions with the devices selftest framework.

## Risks and Edge Cases

Missing `boards` data at install time makes the runtime script fail to find a matching board file.

## Test Signals

Successful packaging includes the Python script and board YAML directory.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/Dell Inc.,XPS 13 9300.yaml -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/Dell Inc.,XPS 13 9300.yaml

## Purpose

This board YAML describes expected discoverable PCI and USB devices for a Dell XPS 13 9300 system.

## Important APIs, Types, and Data Fields

It contains one top-level `pci-controller` with child PCI paths for USB controller, GPU, thermal, sensors, WiFi, SSD, SD card reader, and audio. The USB controller at `14.0` has `usb-version: 2` and child USB paths for camera and bluetooth with expected interface lists.

## Control Flow

The file is declarative. `test_discoverable_devices.py` selects it from DMI `sys_vendor,product_name`, recursively resolves paths in sysfs, and checks device and driver presence.

## State and Persistence Behavior

It persists expected hardware topology and has no runtime state.

## Dependencies and Integration Points

It depends on stable sysfs path topology for the Dell model and the board-file vocabulary implemented by the probe script.

## Risks and Edge Cases

Hardware revisions, firmware differences, disabled devices, or alternate USB routing can make expected paths absent. The top-level controller has no unique key, which is valid only because the machine is expected to have one PCI host controller.

## Test Signals

The probe script emits device existence and driver-binding test results for each leaf and USB interface named here.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/Dell Inc.,XPS 13 9300.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/google,spherion.yaml -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/google,spherion.yaml

## Purpose

This YAML describes expected discoverable devices for the Google Spherion Chromebook and documents the board-file schema.

## Important APIs, Types, and Data Fields

It defines a USB2 controller identified by `dt-mmio: 11200000` with camera and bluetooth USB devices, and a PCI controller identified by `dt-mmio: 11230000` with a WiFi device. Comments document keys: `type`, `dt-mmio`, `of-fullname-regex`, `usb-version`, `acpi-uid`, `devices`, `path`, `name`, and USB `interfaces`.

## Control Flow

The file is loaded when `/proc/device-tree/compatible` contains `google,spherion`. The probe script resolves controller identifiers and nested USB/PCI paths.

## State and Persistence Behavior

It is static expected topology data.

## Dependencies and Integration Points

It depends on devicetree-compatible naming, OF_FULLNAME/uevent metadata, and sysfs USB/PCI topology matching the board.

## Risks and Edge Cases

Board variants or disabled devices can cause false failures. `dt-mmio` must be unique enough to identify controllers; comments describe using regex when it is not.

## Test Signals

For each leaf, the probe script checks sysfs device existence and driver binding for the named device/interfaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/boards/google,spherion.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/test_discoverable_devices.py -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/test_discoverable_devices.py

## Purpose

`test_discoverable_devices.py` validates that expected board-specific PCI/USB devices exist in sysfs and are bound to drivers.

## Important APIs, Types, and Functions

It uses PyYAML, glob, os.walk, regexes, sysfs roots `/sys/devices` and `/sys/bus/usb/devices`, and `ksft`. Important functions include `find_pci_controller_dirs()`, `find_usb_controller_dirs()`, `get_dt_mmio()`, `get_of_fullname()`, `get_acpi_uid()`, `get_usb_version()`, `get_usb_busnum()`, `find_controller_in_sysfs()`, `path_to_dir()`, `find_in_sysfs()`, `check_driver_presence()`, `fill_meta_keys()`, `parse_device_tree_node()`, `count_tests()`, and `get_board_filenames()`.

## Control Flow

The script scans all PCI and USB controller directories, prints a KTAP header, selects a board YAML by devicetree compatible strings or DMI vendor/product, loads device trees, sets a plan based on leaf devices and USB interfaces, recursively resolves each controller/device path, and emits existence and driver-binding results.

## State and Persistence Behavior

It reads sysfs, DMI, and devicetree state without mutation. It builds in-memory controller lists and metadata pathnames for test names.

## Dependencies and Integration Points

It depends on board YAML files, PyYAML, kselftest `ksft`, sysfs PCI/USB topology, `uevent` metadata, DMI or devicetree identifiers, and driver symlinks.

## Risks and Edge Cases

Controller matching can return zero or multiple entries, both fail. `get_dt_mmio()` and `get_of_fullname()` walk parents until a match and may loop toward root if metadata is absent. USB interface globbing expects one interface directory. Board files can become stale as firmware or hardware variants change.

## Test Signals

Failures are named as missing sysfs entries, multiple matches, absent device paths, or missing driver symlinks. Success means every board-described leaf exists and is driver-bound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/devices/probe/test_discoverable_devices.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/Makefile

## Purpose

This Makefile registers the dm-verity keyring shell test with kselftest.

## Important APIs, Types, and Functions

It declares `TEST_PROGS := test-dm-verity-keyring.sh` and includes `../lib.mk`.

## Control Flow

The kselftest framework runs the shell script.

## State and Persistence Behavior

The Makefile has no runtime state; the script loads modules and creates devices.

## Dependencies and Integration Points

It integrates the dm-verity keyring test into the selftest tree.

## Risks and Edge Cases

The runtime script is privileged and destructive enough that accidental execution on a busy dm-verity system may fail module unload or device cleanup.

## Test Signals

Successful packaging makes the shell script available as the dm-verity selftest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/config

## Purpose

This config declares kernel features needed by the dm-verity keyring selftest.

## Important APIs, Types, and Functions

It requests device mapper, dm-verity as module, root hash signature verification, module unload, keyrings, asymmetric key types, X.509 parsing, PKCS#7 parsing, and system data verification.

## Control Flow

There is no executable flow; config tooling consumes the symbols.

## State and Persistence Behavior

It persists only required kernel configuration.

## Dependencies and Integration Points

The script relies on these features to load dm-verity with parameters, manage `.dm-verity` keyrings, add asymmetric certs, and verify PKCS#7 root-hash signatures.

## Risks and Edge Cases

Even with config support, runtime tools such as openssl, veritysetup, keyctl, losetup, and dmsetup must be present.

## Test Signals

Matching kernels should allow both unsealed and sealed keyring test modes to execute.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/test-dm-verity-keyring.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/test-dm-verity-keyring.sh

## Purpose

`test-dm-verity-keyring.sh` validates dm-verity `.dm-verity` keyring behavior in unsealed/signature-required mode and default sealed mode. It checks key upload, keyring sealing, multiple trusted keys, unknown/corrupt signature rejection, sealed-keyring rejection of new keys, and behavior of an empty inactive keyring.

## Important APIs, Types, and Functions

It uses `modprobe`, `dmsetup`, `veritysetup`, `keyctl`, `openssl`, `losetup`, `dd`, `/proc/keys`, `/sys/module/dm_verity/parameters/*`, PKCS#7 detached signatures, X.509 certs, loop devices, and temporary dm targets. Major functions include `cleanup()`, `find_dm_verity_keyring()`, `check_requirements()`, `load_dm_verity_module()`, `generate_named_key()`, `upload_named_key()`, `seal_keyring()`, `create_test_device()`, `create_verity_hash()`, `create_detached_signature()`, `activate_verity_device()`, `sign_root_hash_with_key()`, `test_multiple_keys()`, `test_corrupted_signature()`, `test_keyring_sealed_by_default()`, and `test_keyring_inactive_when_empty()`.

## Control Flow

`main()` creates a work directory, validates tools/root/module availability, loads dm-verity with `keyring_unsealed=1 require_signatures=1`, uploads three generated certs, seals the keyring, creates data/hash loop devices, formats verity metadata, verifies signatures from all trusted keys, verifies an unknown key fails, verifies sealed keyring rejects further keys, and tests truncated/corrupt/wrong-data signatures. It then cleans loop devices, reloads dm-verity with `keyring_unsealed=0 require_signatures=0`, checks the keyring is sealed by default, and verifies empty-keyring behavior.

## State and Persistence Behavior

The script mutates loaded kernel modules, module parameters, `.dm-verity` keyring contents/restrictions, loop devices, dm targets, temporary files, generated certs/keys/signatures, and dmesg visibility. `trap cleanup EXIT` removes dm targets, loop devices, and temp directories.

## Dependencies and Integration Points

It depends on root, module unload support, dm-verity keyring parameters, keyutils, OpenSSL `smime`, cryptsetup `veritysetup`, loop devices, and device mapper. It integrates kernel keyrings, asymmetric certificate parsing, PKCS#7 verification, and dm-verity table activation.

## Risks and Edge Cases

The script unloads/reloads `dm-verity`, which fails if any dm-verity target is in use. It parses `/proc/keys` and converts hex serials, which requires permission and stable output. Test signatures intentionally omit embedded certs (`-nocerts`), requiring keyring matching to work. The script uses `set -e` but many tests capture return codes carefully.

## Test Signals

Pass signals are successful activation with each trusted key, failed activation with unknown/truncated/corrupt/wrong signatures, failed key addition after sealing, expected activation behavior with empty sealed keyring, and final all-tests-passed summary. Failures identify keyring, signature, module, or dm target regressions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dm-verity/test-dm-verity-keyring.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/Makefile

## Purpose

This Makefile builds the dma-buf heaps selftest binary.

## Important APIs, Types, and Functions

It sets static optimized CFLAGS with exported kernel headers, declares `TEST_GEN_PROGS = dmabuf-heap`, and includes `../lib.mk`.

## Control Flow

Kselftest builds and runs the C program.

## State and Persistence Behavior

The Makefile has no runtime state.

## Dependencies and Integration Points

It integrates with dma-buf heaps and DRM/VGEM testing through the generated binary.

## Risks and Edge Cases

Static linking and `-O3` can expose toolchain/library availability issues on minimal systems.

## Test Signals

Build success creates the `dmabuf-heap` executable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/config

## Purpose

This config declares kernel support needed by the dma-buf heap selftest.

## Important APIs, Types, and Functions

It requests `CONFIG_DMABUF_HEAPS`, `CONFIG_DMABUF_HEAPS_SYSTEM`, and `CONFIG_DRM_VGEM`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

It persists feature requirements only.

## Dependencies and Integration Points

The C test needs `/dev/dma_heap/*` and optionally VGEM import via `/dev/dri/card*`.

## Risks and Edge Cases

VGEM absence causes import subtests to skip, while heap absence skips the whole test at runtime.

## Test Signals

Kernels with these symbols should expose at least the system heap and vgem importer for full coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/config -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/dmabuf-heap.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/dmabuf-heap.c

## Purpose

`dmabuf-heap.c` tests dma-buf heap allocation, mmap/write/sync behavior, optional VGEM import, zeroed allocation reuse, ioctl structure size compatibility, and invalid argument rejection for every heap under `/dev/dma_heap`.

## Important APIs, Types, and Functions

It uses `DMA_HEAP_IOCTL_ALLOC`, `DMA_BUF_IOCTL_SYNC`, `DRM_IOCTL_VERSION`, `DRM_IOCTL_PRIME_FD_TO_HANDLE`, `DRM_IOCTL_GEM_CLOSE`, `mmap()`, `munmap()`, and kselftest result helpers. Key functions are `open_vgem()`, `dmabuf_heap_open()`, `dmabuf_heap_alloc_fdflags()`, `dmabuf_sync()`, `test_alloc_and_import()`, `test_alloc_zeroed()`, `dmabuf_heap_alloc_older()`, `dmabuf_heap_alloc_newer()`, `test_alloc_compat()`, `test_alloc_errors()`, and `numer_of_heaps()`.

## Control Flow

`main()` opens `/dev/dma_heap`, sets a plan of 11 tests per heap, and for each heap runs allocation/import/sync, two zeroing tests at 4 KiB and 1 MiB, older/newer ioctl compatibility, and invalid fd/flag cases. The import path maps a 1 MiB buffer, writes patterns under sync start/end, imports to VGEM if available, writes again, and closes handles.

## State and Persistence Behavior

It allocates dma-buf fds from heaps, maps them shared, writes data patterns, imports to DRM handles, and closes fds/handles. No files are persisted.

## Dependencies and Integration Points

It depends on dma-buf heap device nodes, exported dma-heap/dma-buf headers, optional VGEM DRM device, and kselftest. It exercises heap allocator, dma-buf synchronization, and PRIME import integration.

## Risks and Edge Cases

Some error cleanup paths return before closing all resources in failure cases. Zeroing tests allocate 32 buffers and assume freed heap memory must be zeroed on reallocation. `numer_of_heaps()` assumes `opendir()` succeeded because `main()` checked once earlier.

## Test Signals

Passes include allocation/import, sync success, buffer zeroing at two sizes, old/new ioctl compatibility, and expected errors for invalid fd/heap flags/fd flags. Skips occur when VGEM is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/dmabuf-heaps/dmabuf-heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/Makefile

## Purpose

This Makefile builds the `udmabuf` driver selftest under the drivers/dma-buf selftest area.

## Important APIs, Types, and Functions

It sets `CFLAGS += $(KHDR_INCLUDES)`, declares `TEST_GEN_PROGS := udmabuf`, sets `top_srcdir ?=../../../../..`, and includes `../../lib.mk`.

## Control Flow

Kselftest builds the `udmabuf` C test. Although this work item maps only the Makefile and config, the generated program tests `/dev/udmabuf`.

## State and Persistence Behavior

The Makefile stores build metadata only.

## Dependencies and Integration Points

It integrates exported kernel headers and kselftest library rules for driver tests.

## Risks and Edge Cases

Incorrect `top_srcdir` can break include resolution in out-of-tree builds. Missing udmabuf support causes runtime skips rather than build failures.

## Test Signals

Build success produces the `udmabuf` executable for the selftest run.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/config -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/config

## Purpose

This config declares the kernel feature needed by the drivers/dma-buf udmabuf selftest.

## Important APIs, Types, and Functions

It requests `CONFIG_UDMABUF=y`.

## Control Flow

There is no executable flow.

## State and Persistence Behavior

It persists only the kernel configuration requirement.

## Dependencies and Integration Points

The generated `udmabuf` test expects `/dev/udmabuf` and UDMABUF ioctl support.

## Risks and Edge Cases

If UDMABUF is modular or absent despite the config expectation, the runtime test may skip or fail opening the device.

## Test Signals

With the symbol enabled, the udmabuf selftest can exercise create and create-list ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/dma-buf/config -->
