# subset-b-006877 research

Grouped research report for the exact subset-b-006877 source manifest. Each section is delimited for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_poll_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_poll_test.c

## Purpose
Stress-tests pidfd readiness notifications by repeatedly creating a child, opening a pidfd, killing the child through pidfd_send_signal, and requiring poll() on the pidfd to report process death with POLLIN.

## Important APIs, Types, and Functions
`handle_alarm()` records a timeout, `main()` parses an optional iteration count, uses `sys_pidfd_open()`, `sys_pidfd_send_signal()`, `poll()`, `waitpid()`, and kselftest reporting helpers from `pidfd.h` and `kselftest.h`.

## Control Flow
For each iteration the parent forks a sleeping child, opens its pidfd, arms a 3 second SIGALRM, sends SIGKILL through the pidfd, blocks in `poll()`, validates exactly one POLLIN event, closes the pidfd, and reaps the child. Transient `fork()` EAGAIN retries the same iteration.

## State and Persistence
Only process-local state is used: the global `timeout`, a child process, and an open pidfd per loop. No durable state is written; zombie cleanup is explicit through `waitpid()`.

## Dependencies and Integration Points
Depends on pidfd syscalls exposed by `pidfd.h`, Linux signal/poll semantics, and the kselftest standalone binary convention. It integrates with the pidfd selftest target as a stress-style regression test.

## Risks and Test Signals
Main risk is flakiness from scheduler stalls or missing pidfd syscall support; failure signals include timeout, missing POLLIN, unexpected extra events, pidfd syscall errors, or failed reaping. A pass means pidfd poll death notification remained stable over the configured iteration count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_poll_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setattr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setattr_test.c

## Purpose
Verifies pidfs/pidfd file descriptors reject file metadata and execution operations that must not be supported on task handles.

## Important APIs, Types, and Functions
Defines `FIXTURE(pidfs_setattr)` with `child_pid` and `child_pidfd`; setup uses `create_child()` with `CLONE_NEWUSER | CLONE_NEWPID`; tests call `fchown()`, `fchmod()`, and `execveat(..., AT_EMPTY_PATH)`.

## Control Flow
The fixture creates a short-lived child and pidfd, each test performs one forbidden operation on the pidfd, and teardown waits for the child and closes the pidfd.

## State and Persistence
State is limited to the fixture child and pidfd. The test intentionally does not persist metadata because the expected behavior is rejection before any pidfs inode mutation.

## Dependencies and Integration Points
Uses `pidfd.h` syscall wrappers and `kselftest_harness.h` fixtures. It exercises the pidfs VFS operation table through generic libc/VFS APIs rather than pidfd-specific ioctls.

## Risks and Test Signals
Expected errno values are part of the contract: `EOPNOTSUPP` for chown/chmod and `EACCES` for exec. A regression could expose task handles as mutable/executable filesystem objects or produce incompatible errno values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setattr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setns_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setns_test.c

## Purpose
Exercises `setns()` with pidfds and pidfd-derived namespace file descriptors across user, mount, pid, uts, ipc, net, cgroup, and time namespaces, including invalid flags and exited-task handling.

## Important APIs, Types, and Functions
`ns_info[]` maps namespace names, clone flags, and pidfd namespace ioctls. The `current_nsset` fixture stores parent namespace fds, child namespace fds, pidfd-derived namespace fds, and child pidfds. Helpers include `switch_timens()`, `preserve_ns()`, and `in_same_namespace()`.

## Control Flow
Fixture setup captures the current namespace set, creates one exited child and two paused children in new namespaces where available, opens `/proc/<pid>/ns/*` fds, and derives namespace fds through pidfd ioctls. Tests cover invalid `setns()` flags, `ESRCH` on exited pidfd, incremental pidfd setns, incremental nsfd setns, pidfd-derived nsfd setns, one-shot pidfd setns with combined flags, namespace non-corruption between children, and invalid pidfd descriptors.

## State and Persistence
The test mutates the calling process namespace membership during individual tests and owns paused child processes until teardown. It persists no files, but it keeps many namespace fds open to compare inode/device identity and prevent namespace lifetime loss.

## Dependencies and Integration Points
Depends on clone/unshare/setns namespace support, `/proc/*/ns`, pidfd namespace ioctls from `pidfd.h`, socketpairs for child readiness, and `kselftest_harness.h`. It integrates deeply with pidfs namespace ioctl behavior and generic namespace APIs.

## Risks and Test Signals
Privilege and kernel-feature availability can skip paths through missing namespace files or `EOPNOTSUPP`. Risks include leaking changed namespaces across test cases, child cleanup failures, and false positives for pid namespaces because joining a pid namespace affects only future children; the code handles this by comparing the original pid namespace where appropriate.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_setns_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_test.c

## Purpose
Provides a broader pidfd regression binary for signal delivery, pid reuse safety, and pidfd poll behavior when thread-group leaders exec or exit while other threads exist.

## Important APIs, Types, and Functions
Important functions are `pidfd_clone()`, `send_signal()`, `send_signal_worker()`, `test_pidfd_send_signal_*()`, `poll_pidfd()`, `test_pidfd_poll_exec()`, `test_pidfd_poll_leader_exit()`, and `main()`. It uses `PIDFD_SELF_THREAD`, `PIDFD_SELF_THREAD_GROUP`, `CLONE_PIDFD`, epoll, pthreads, `mmap()` shared state, and namespace/mount syscalls.

## Control Flow
`main()` declares eight kselftest results, runs poll timing tests with pidfd and waitpid baselines, probes pidfd_send_signal support, sends SIGUSR1 to self and a worker thread, verifies signaling an exited process returns `ESRCH`, then attempts a pid-recycle scenario inside a new pid namespace to ensure old pidfds cannot signal a new task with the same numeric pid.

## State and Persistence
State includes global pidfd_send_signal support, thread-local signal observation, shared `child_exit_secs`, child namespaces, temporary proc remounting inside a child, and process/thread lifetimes. No durable files are created outside transient namespace mount changes.

## Dependencies and Integration Points
Depends on `pidfd.h`, kselftest, pthreads, epoll, clone, pid namespaces, procfs, and `/bin/sleep` for exec timing. It integrates user-visible pidfd semantics with scheduler/thread-group behavior.

## Risks and Test Signals
Timing windows are deliberate: poll must not report too early when a non-leader thread execs or when the leader exits while other threads run. Environment risks include missing pid namespaces, high `pid_max`, absent pidfd_send_signal, or scheduler delays outside the 3 to 5 second expected windows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_wait.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_wait.c

## Purpose
Validates `waitid(P_PIDFD, ...)` semantics for normal exit, stopped/continued/killed states, and nonblocking pidfds.

## Important APIs, Types, and Functions
Uses `ptr_to_u64()`, `sys_clone3()` with `CLONE_PIDFD | CLONE_PARENT_SETTID`, `sys_waitid()`, `sys_pidfd_send_signal()`, `fcntl()` flag checks, and three harness tests: `wait_simple`, `wait_states`, and `wait_nonblock`.

## Control Flow
`wait_simple` rejects non-child and non-pidfd descriptors, then waits on a clone3 child pidfd. `wait_states` drives a child through SIGSTOP, SIGCONT, a second stop, and SIGKILL via pidfd. `wait_nonblock` verifies `ECHILD` for non-child self pidfd, `EAGAIN` without WNOHANG for a live child, zero with WNOHANG, and normal behavior after clearing O_NONBLOCK.

## State and Persistence
State is per-test child process state plus pipe synchronization and pidfd file status flags. No persistent storage is used.

## Dependencies and Integration Points
Depends on clone3, pidfd_open with `PIDFD_NONBLOCK`, pidfd_send_signal, waitid pidfd support, and `kselftest_harness.h`.

## Risks and Test Signals
The tests encode precise errno/si_code expectations (`CLD_EXITED`, `CLD_STOPPED`, `CLD_CONTINUED`, `CLD_KILLED`). Kernels lacking nonblocking pidfd support are skipped via the local `SKIP`/`XFAIL` compatibility macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_xattr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_xattr_test.c

## Purpose
Checks pidfs extended-attribute behavior on pidfds, including multiple xattrs and persistence across task exit while a pidfd remains open.

## Important APIs, Types, and Functions
Defines `FIXTURE(pidfs_xattr)` with a child pid and pidfd. Tests call `fsetxattr()`, `fgetxattr()`, `flistxattr()`, and compare values stored under user xattr names.

## Control Flow
Setup creates a child in new user and pid namespaces. `set_get_list_xattr_multiple` writes multiple user xattrs, reads them back, and verifies the list buffer contains expected names. `set_get_list_xattr_persistent` writes an xattr, waits for child exit, then reads it again through the still-open pidfd.

## State and Persistence
The only persisted state is xattr data attached to the pidfs file object for the lifetime of the pidfd. The test confirms that data survives target process exit until descriptor cleanup.

## Dependencies and Integration Points
Depends on pidfs xattr support, Linux xattr syscalls, `create_child()`, and `kselftest_harness.h`. It integrates pidfs with generic VFS xattr APIs.

## Risks and Test Signals
Risks include xattr ordering/list formatting assumptions, namespace restrictions, and kernels/filesystems without pidfs xattr support. Failure signals are syscall errors, mismatched values, missing list entries, or loss of xattrs after reaping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/pidfd/pidfd_xattr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/Makefile

## Purpose
Registers the power_supply selftest shell program and its helper file with kselftest.

## Important APIs, Types, and Functions
`TEST_PROGS := test_power_supply_properties.sh` marks the executable test; `TEST_FILES := helpers.sh` installs the sourced helper; `include ../lib.mk` pulls in common kselftest build/install rules.

## Control Flow
The Makefile has no procedural logic beyond variable declaration and inclusion of the shared lib.mk.

## State and Persistence
No runtime state is stored. Build state is delegated to kselftest output directories.

## Dependencies and Integration Points
Integrates the shell test with the tools/testing/selftests harness so `make kselftest` can copy both the test and helper.

## Risks and Test Signals
Primary risk is omitting helper installation, which would make the shell test fail at source time. The test signal is successful kselftest discovery of one program and one support file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/helpers.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/helpers.sh

## Purpose
Provides KTAP-oriented shell helpers for validating power_supply sysfs files and uevent properties.

## Important APIs, Types, and Functions
Important functions are `calc`, `test_sysfs_prop`, `to_human_readable_unit`, `_check_sysfs_prop_available`, `test_sysfs_prop_optional`, `test_sysfs_prop_optional_range`, `test_sysfs_prop_optional_list`, `dump_file`, `__test_uevent_prop`, `test_uevent_prop`, and `test_uevent_prop_optional`.

## Control Flow
Helpers build paths under `$SYSFS_SUPPLIES/$DEVNAME`, check file existence/readability, compare exact values or ranges/lists, print reported values with optional unit conversion, and emit KTAP pass/fail/skip outcomes. Uevent helpers grep `POWER_SUPPLY_<PROP>=...` and dump the file on mismatch.

## State and Persistence
State is carried through shell globals `SYSFS_SUPPLIES` and `DEVNAME`; `IFS` is temporarily changed for comma-separated list validation and restored. No files are modified.

## Dependencies and Integration Points
Depends on `awk`, `grep`, `cat`, shell arithmetic, sysfs power_supply files, and KTAP helper functions sourced by the caller.

## Risks and Test Signals
Risks include numeric comparisons on nonnumeric sysfs values, exact string matching in uevent, and a fragile unit conversion display path. Failures are exposed as KTAP failures or skips for absent optional properties.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/helpers.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/test_power_supply_properties.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/test_power_supply_properties.sh

## Purpose
Validates the Linux power_supply userspace ABI by checking per-device sysfs property files and matching uevent fields.

## Important APIs, Types, and Functions
Uses `count_tests()` plus helper functions from `helpers.sh` and KTAP functions from `ktap_helpers.sh`. It inspects properties such as `type`, `online`, `present`, `status`, `capacity`, voltage/current/charge/power/energy fields, model/manufacturer/serial, technology, and scope.

## Control Flow
The script selects all devices under `/sys/class/power_supply` or one named argument, sets a KTAP plan of 33 checks per supply, verifies device existence, tests mandatory name/type uevent fields, then runs optional file/range/list checks for each known ABI property before `ktap_finished`.

## State and Persistence
Runtime state is shell variables for selected supplies, `DEVNAME`, and sampled sysfs property values. It performs read-only sysfs access.

## Dependencies and Integration Points
Depends on the power_supply class ABI, KTAP helpers, `helpers.sh`, and basic shell utilities. It is installed by the local Makefile as a kselftest program.

## Risks and Test Signals
Test risk is that the fixed `NUM_TESTS=33` must be updated when checks change. The voltage range checks intentionally catch unit-scaling bugs but may be too narrow for unusual hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/power_supply/test_power_supply_properties.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/Makefile

## Purpose
Top-level dispatcher for PowerPC selftest subdirectories and common library objects.

## Important APIs, Types, and Functions
Defines `SUB_DIRS`, `TARGETS`, `CFLAGS`, `GIT_VERSION`, `all`, `run_tests`, `emit_tests`, `install`, `clean`, and pattern recursion into child Makefiles; includes `../lib.mk`.

## Control Flow
Build flow exports `OUTPUT`, builds `lib/`, then recurses over target subdirectories. Test-run flow delegates to each child directory, and install/clean recurse similarly.

## State and Persistence
Build state lives under `$(OUTPUT)` and child output directories. No runtime state is managed here.

## Dependencies and Integration Points
Integrates all PowerPC selftest families with kselftest. `GIT_VERSION` embeds source revision metadata in builds that use it.

## Risks and Test Signals
Risks are recursive make ordering and missing child directories. Test signal is that every listed target can build/run through the shared kselftest interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/Makefile

## Purpose
Builds the PowerPC alignment selftests.

## Important APIs, Types, and Functions
`TEST_GEN_PROGS := copy_first_unaligned alignment_handler`; it includes `../../lib.mk` and `../flags.mk`, and adds `-m64` to `CFLAGS` for both generated programs.

## Control Flow
No custom targets are defined; lib.mk compiles the two C files and handles install/run integration.

## State and Persistence
No persistent state beyond build outputs.

## Dependencies and Integration Points
Depends on the PowerPC common flags and kselftest lib.mk. The generated programs depend on `../harness.c` and utility headers through normal build rules.

## Risks and Test Signals
Risk is that these tests require 64-bit PowerPC instruction support; compile or run failures point at architecture/toolchain mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/alignment_handler.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/alignment_handler.c

## Purpose
Tests the PowerPC alignment fault handler by comparing native aligned/cacheable instruction results with emulated cache-inhibited unaligned access results across integer, FP, VMX, VSX, and prefixed instructions.

## Important APIs, Types, and Functions
Key globals are `bufsize`, `debug`, `testing`, `gotsig`, `prefixes_enabled`, `cipath`, and `cioffset`. Important helpers are `sighandler()`, instruction-generating `TEST`/`TESTP` macros, `preload_data()`, `test_memcpy()`, `test_memcmp()`, `do_test()`, `can_open_cifile()`, feature-specific `test_alignment_handler_*()` functions, `usage()`, and `main()`.

## Control Flow
Main parses `-d`, optional cache-inhibited path and offset, installs SIGSEGV/SIGBUS/SIGILL handlers, detects prefixed-instruction support, then runs each feature group through `test_harness`. `do_test()` maps two cache-inhibited pages and two aligned memory buffers, runs a generated load/store sequence at offsets 0..15, compares emulated and native copies, and reports per-instruction pass/fail.

## State and Persistence
State includes signal-handler control flags, mapped cache-inhibited memory, allocated aligned buffers, and hardware capability checks. The program does not persist data, but it may touch a device such as `/dev/fb0` or a supplied cache-inhibited mapping.

## Dependencies and Integration Points
Depends on PowerPC instruction encodings, `utils.h` hardware capability helpers, `instructions.h` prefixed instruction macros, signal ucontext NIP adjustment, and kselftest harness semantics.

## Risks and Test Signals
Risks include needing real cache-inhibited memory, instruction availability by CPU/binutils, endian-specific cases, and signal handler correctness for 4-byte versus 8-byte prefixed instructions. Strong test signals are wrong data, unexpected signals, or skipped groups when hardware/path support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/alignment_handler.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/copy_first_unaligned.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/copy_first_unaligned.c

## Purpose
Verifies that an unaligned PowerPC `copy_first` instruction causes SIGBUS rather than silently succeeding.

## Important APIs, Types, and Functions
Defines `signal_action_handler()` to check `si_signo`, `si_code == BUS_ADRALN`, and `si_addr`; `setup_signal_handler()` installs it; `test_copy_first_unaligned()` emits `PPC_INST_COPY_FIRST` on an intentionally unaligned pointer.

## Control Flow
The test installs a SIGBUS handler, executes the unaligned instruction, and expects the handler to terminate with success. Reaching normal return is a failure.

## State and Persistence
No durable state. It uses process signal disposition and stack memory only.

## Dependencies and Integration Points
Depends on `instructions.h` raw instruction encoding, `utils.h` harness macros, and PowerPC copy/paste instruction support.

## Risks and Test Signals
Risk is running on hardware/kernel combinations without the expected copy instruction behavior. Test signal is process exit through the signal handler with matching address/code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/alignment/copy_first_unaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/Makefile

## Purpose
Builds PowerPC microbenchmark binaries for syscall, context-switch, fork, futex, mmap, and time-call costs.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS := gettimeofday context_switch fork mmap_bench futex_bench null_syscall`, `TEST_GEN_FILES := exec_target`, includes kselftest lib.mk and flags.mk, and applies pthread/no-pie/nostdlib/linker options where needed.

## Control Flow
Compilation is delegated to lib.mk; `exec_target` is a support binary for fork+exec workloads, while benchmark programs are executable selftest artifacts.

## State and Persistence
Build output state is under `$(OUTPUT)`; no runtime state here.

## Dependencies and Integration Points
Integrates benchmarks with the PowerPC selftest target while preserving special compile flags such as `-nostdlib` for `exec_target` and `-pthread` for threaded benchmarks.

## Risks and Test Signals
Risks are toolchain flag support and forgetting support-file generation. Test signal is successful build and runnable benchmark binaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/context_switch.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/context_switch.c

## Purpose
A configurable context-switch microbenchmark measuring pipe, sched_yield, or futex ping-pong between two threads or processes pinned to selected CPUs while optionally touching FP/vector/VDSO state.

## Important APIs, Types, and Functions
Important pieces are `touch()`, `start_thread_on()`, `start_process_on()`, signal handlers, `struct actions`, pipe/yield/futex setup and worker pairs, `sys_futex()`, custom `mutex_lock()`/`mutex_unlock()`, option parsing, and `main()`.

## Control Flow
Main selects mode and CPUs, disables unavailable Altivec/VSX touches, creates a process group, installs SIGUSR1 exit handling, runs the selected setup, starts two workers on target CPUs, and idles while SIGALRM prints per-second iteration deltas until timeout kills the group.

## State and Persistence
State includes global benchmark options, iteration counters, pipe fds or futex words, optional shared memory for process futex mode, CPU affinity, and process-group signal lifecycle. No persistent files are written.

## Dependencies and Integration Points
Depends on pthreads, CPU affinity APIs, futex syscall, SysV shared memory for process mode, PowerPC hwcap helpers, and Altivec/VSX compiler support.

## Risks and Test Signals
Risks include CPU affinity failures, busy-loop resource use, signal-driven termination, and benchmark noise from scheduler/load. Output lines are throughput signals rather than pass/fail assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/context_switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/exec_target.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/exec_target.c

## Purpose
Minimal exec target used by fork/exec microbenchmarks.

## Important APIs, Types, and Functions
Defines `_start()` directly and invokes the `exit` syscall with status 0 using `syscall(SYS_exit, 0)`.

## Control Flow
The program enters at `_start`, performs one syscall, and terminates without libc startup or teardown.

## State and Persistence
No mutable or persistent state.

## Dependencies and Integration Points
Built with `-nostdlib` by the benchmarks Makefile and launched by `fork.c` when measuring fork or vfork plus exec overhead.

## Risks and Test Signals
Risk is architecture/libc/syscall ABI mismatch. A successful exec returns quickly with exit code 0, isolating exec overhead from program initialization cost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/exec_target.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/fork.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/fork.c

## Purpose
Microbenchmarks thread creation, fork, vfork, and optional exec throughput on an optional CPU affinity.

## Important APIs, Types, and Functions
Important functions are `set_cpu()`, `start_process_on()`, `run_exec()`, `bench_fork()`, `bench_vfork()`, `bench_thread()`, signal handlers, `bench_proc()`, `usage()`, and `main()`.

## Control Flow
Main parses `--fork`, `--vfork`, `--exec`, `--timeout`, and `--exec-target`, optionally chdirs beside the executable for `exec_target`, pins CPU, creates a process group, starts a benchmark worker process, and prints per-second iteration deltas until timeout sends SIGUSR1.

## State and Persistence
State includes global mode flags, CPU choice, iteration counters, signal alarms, and child processes/threads. It writes no files.

## Dependencies and Integration Points
Depends on pthreads, fork/vfork/waitpid, execve of `./exec_target`, CPU affinity, and process-group signaling.

## Risks and Test Signals
Risks include runaway process creation on broken termination, inaccurate measurements under load, and requiring `exec_target` in the working directory for exec mode. Output throughput is the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/futex_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/futex_bench.c

## Purpose
Measures raw futex wait/wake syscall throughput in a tight loop.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `futex(...)` syscall macro, `test_futex()`, and `main()` using `test_harness()`.

## Control Flow
`test_futex()` records timebase start/end around `ITERATIONS` calls to `FUTEX_WAKE` on a stack word, then prints elapsed time through `printf()`.

## State and Persistence
No durable state; the futex word and timing data are process-local.

## Dependencies and Integration Points
Depends on Linux futex syscall, `utils.h` timebase helpers, and PowerPC kselftest harness.

## Risks and Test Signals
Risk is that this is a benchmark with broad timing variance; functional failure only occurs if the syscall path or harness fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/futex_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/gettimeofday.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/gettimeofday.c

## Purpose
Benchmarks repeated `gettimeofday()` calls, typically exercising VDSO time access.

## Important APIs, Types, and Functions
Defines `test_gettimeofday()` and `main()`, using `timebase_read()`/`timebase_delta()` helpers and `test_harness()`.

## Control Flow
The test loops a fixed number of `gettimeofday(&tv, NULL)` calls, measures elapsed timebase, prints timing, and returns success.

## State and Persistence
No persistent state; only local timing variables.

## Dependencies and Integration Points
Depends on libc `gettimeofday`, PowerPC timebase utilities, and the common harness.

## Risks and Test Signals
Risk is measurement noise. Failure signal is unusual syscall/library failure or harness failure, not a strict performance threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/gettimeofday.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/mmap_bench.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/mmap_bench.c

## Purpose
Benchmarks mmap/munmap or page-fault behavior over a large anonymous mapping.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `MEMSIZE`, `PAGE_SIZE`, `CHUNK_COUNT`, `usage()`, `test_mmap()`, and `main()` with an option to select faulting behavior.

## Control Flow
The benchmark maps memory, optionally touches one byte per chunk/page to fault it in, unmaps it, repeats for many iterations, and prints elapsed time via timebase helpers.

## State and Persistence
Process-local virtual memory mappings are repeatedly created and destroyed; no files are persisted.

## Dependencies and Integration Points
Depends on anonymous mmap, system page behavior, `getopt`, and PowerPC utility timing.

## Risks and Test Signals
Risks include memory pressure, assumptions about 64 KiB pages in constants, and benchmark variability. Failures are mmap/munmap errors or harness failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/mmap_bench.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/null_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/null_syscall.c

## Purpose
Measures overhead of simple syscalls and CPU soak loops using the timebase and processor frequency data.

## Important APIs, Types, and Functions
Important functions are `mftb()`, `sigalrm_handler()`, `cpu_soak_usecs()`, `get_proc_frequency()`, `do_null_syscall()`, `TIME()` macro, and `main()`.

## Control Flow
The program reads clock/timebase frequencies from proc/device-tree style sources, warms or soaks CPU using SIGALRM timing, then times repeated null-ish syscalls and prints cycle/time metrics.

## State and Persistence
State includes global frequency values, alarm-controlled `soak_done`, and local counters. It reads system information but writes no files.

## Dependencies and Integration Points
Depends on PowerPC timebase assembly, signals, syscalls, and platform frequency reporting.

## Risks and Test Signals
Risks are missing frequency files, timebase conversion error, and noisy benchmark output. Test signal is printed latency data rather than a pass/fail threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/benchmarks/null_syscall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/Makefile

## Purpose
Builds the `cache_shape` PowerPC selftest binary.

## Important APIs, Types, and Functions
`TEST_GEN_PROGS := cache_shape`; includes kselftest lib.mk and PowerPC flags.mk.

## Control Flow
No custom flow beyond common build/install/run rules.

## State and Persistence
No persistent state except build output.

## Dependencies and Integration Points
Integrates the cache auxiliary-vector validation test into the PowerPC target.

## Risks and Test Signals
Risk is only build integration; runtime semantics live in `cache_shape.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/cache_shape.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/cache_shape.c

## Purpose
Prints and validates cache shape auxiliary-vector entries exposed to userspace.

## Important APIs, Types, and Functions
Defines AT_* cache constants, `print_size()`, `print_geo()`, `test_cache_shape()`, and `main()`.

## Control Flow
`test_cache_shape()` reads cache size/geometry auxv values, prints human-readable cache size and line/associativity geometry, and is run through `test_harness()`.

## State and Persistence
Read-only process auxv state is used; no files are modified.

## Dependencies and Integration Points
Depends on ELF auxv definitions, libc auxv access, and PowerPC utility harness.

## Risks and Test Signals
Risk is platform variability or missing auxv entries. Test signal is successful decoding and printed cache topology information.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/cache_shape/cache_shape.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/Makefile

## Purpose
Builds validation binaries for copied kernel PowerPC memory/copy-user assembly loops under several implementations.

## Important APIs, Types, and Functions
Defines copy loop object groups, `TEST_GEN_PROGS`, per-target object dependencies, `EXTRA_SOURCES`, `CFLAGS`, `ASFLAGS`, and target-specific `-D COPY_LOOP=...` or `-D TEST_MEMMOVE=...` mappings.

## Control Flow
The Makefile compiles shared assembly implementations and links validation harnesses against selected loop symbols such as `test___copy_tofrom_user_base`, `test_memcpy`, `test_memmove`, and Power7 variants.

## State and Persistence
Build output contains test binaries and object files. No runtime state is controlled here.

## Dependencies and Integration Points
Integrates imported kernel assembly with local shim headers under `copyloops/asm` and common PowerPC flags.

## Risks and Test Signals
Risks include symbol-name mismatches, assembler feature support, and keeping copied kernel loops synchronized with required shims. Successful builds are prerequisite signals for the validation C tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/asm-compat.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/asm-compat.h

## Purpose
Intentionally empty compatibility shim used so copied kernel copyloop assembly can include kernel-style headers without pulling in the full kernel tree.

## Important APIs, Types, and Functions
No macros, types, or functions are defined in this snapshot.

## Control Flow
There is no control flow; the file only satisfies include-path resolution.

## State and Persistence
No state is held or persisted.

## Dependencies and Integration Points
Included by copied assembly files that expect `<asm/...>` headers. Its integration role is to make absence explicit and keep the selftest build minimal.

## Risks and Test Signals
Risk is silent build breakage if future copied assembly starts relying on real definitions from this header. The current test signal is successful assembly with an empty shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/asm-compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/feature-fixups.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/feature-fixups.h

## Purpose
Intentionally empty compatibility shim used so copied kernel copyloop assembly can include kernel-style headers without pulling in the full kernel tree.

## Important APIs, Types, and Functions
No macros, types, or functions are defined in this snapshot.

## Control Flow
There is no control flow; the file only satisfies include-path resolution.

## State and Persistence
No state is held or persisted.

## Dependencies and Integration Points
Included by copied assembly files that expect `<asm/...>` headers. Its integration role is to make absence explicit and keep the selftest build minimal.

## Risks and Test Signals
Risk is silent build breakage if future copied assembly starts relying on real definitions from this header. The current test signal is successful assembly with an empty shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/feature-fixups.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/kasan.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/kasan.h

## Purpose
Intentionally empty compatibility shim used so copied kernel copyloop assembly can include kernel-style headers without pulling in the full kernel tree.

## Important APIs, Types, and Functions
No macros, types, or functions are defined in this snapshot.

## Control Flow
There is no control flow; the file only satisfies include-path resolution.

## State and Persistence
No state is held or persisted.

## Dependencies and Integration Points
Included by copied assembly files that expect `<asm/...>` headers. Its integration role is to make absence explicit and keep the selftest build minimal.

## Risks and Test Signals
Risk is silent build breakage if future copied assembly starts relying on real definitions from this header. The current test signal is successful assembly with an empty shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/kasan.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/processor.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/processor.h

## Purpose
Intentionally empty compatibility shim used so copied kernel copyloop assembly can include kernel-style headers without pulling in the full kernel tree.

## Important APIs, Types, and Functions
No macros, types, or functions are defined in this snapshot.

## Control Flow
There is no control flow; the file only satisfies include-path resolution.

## State and Persistence
No state is held or persisted.

## Dependencies and Integration Points
Included by copied assembly files that expect `<asm/...>` headers. Its integration role is to make absence explicit and keep the selftest build minimal.

## Risks and Test Signals
Risk is silent build breakage if future copied assembly starts relying on real definitions from this header. The current test signal is successful assembly with an empty shim.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/processor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/ppc_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/ppc_asm.h

## Purpose
Provides local PowerPC assembly macro compatibility for copied kernel memory/copy-user loops.

## Important APIs, Types, and Functions
Defines register aliases, stack frame constants, `_GLOBAL*` wrappers that prefix symbols with `test_`, `CFUNC`, `PPC_MTOCRF`, `EX_TABLE`, feature-section no-op macros, and `DCBT_SETUP_STREAMS` as empty.

## Control Flow
No runtime control flow. Preprocessor expansion maps kernel assembly annotations and exception-table directives to forms accepted in the selftest binary.

## State and Persistence
No state is stored; generated symbols and sections affect build/link output only.

## Dependencies and Integration Points
Includes `<ppc-asm.h>` and is consumed by copyloop `.S` files. It is a critical integration layer between kernel assembly source style and userspace selftest linking.

## Risks and Test Signals
Risk is semantic drift from kernel macros, especially exception table and feature patching behavior. Build/link success plus validation tests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/asm/ppc_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_mc_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_mc_64.S

## Purpose
Imported PowerPC machine-check-tolerant copy routine variant used for userspace validation of copy loop behavior.

## Important APIs, Types, and Functions
Defines test-prefixed global copy symbols through `_GLOBAL`/`FUNC_START` macros and uses errno/exception table style fixups from local shims.

## Control Flow
Assembly copies memory in chunks with alignment/size handling and branches to fixup paths on faults, returning remaining byte counts or error-style results matching kernel copy semantics.

## State and Persistence
No persistent state; it mutates destination memory and registers for one call.

## Dependencies and Integration Points
Depends on local `linux/export.h`, `asm/ppc_asm.h`, `asm/errno.h`, and validation C callers in `copyloops`.

## Risks and Test Signals
Risks are exception-table fidelity and mismatch between kernel and userspace fault handling. `exc_validate` and copy validation binaries are the primary test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_mc_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_tofrom_user_reference.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_tofrom_user_reference.S

## Purpose
Simple byte-copy reference implementation for copy-to/from-user validation.

## Important APIs, Types, and Functions
Exports `copy_tofrom_user_reference` through `_GLOBAL`; it copies byte-by-byte from source to destination for the requested length.

## Control Flow
The loop decrements length, loads a byte, stores it, advances pointers, and returns zero remaining bytes on success.

## State and Persistence
Only caller-provided memory is modified; no persistent state.

## Dependencies and Integration Points
Uses local `asm/ppc_asm.h` and is linked with validation tests as a known-simple baseline.

## Risks and Test Signals
Risk is low; it is intentionally simple but may not model fault behavior. Test signal is matching output against optimized loops for nonfaulting cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copy_tofrom_user_reference.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_64.S

## Purpose
Imported generic 64-bit PowerPC `copy_to_user`/`copy_from_user` style loop implementation for validation.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_power7.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_power7.S

## Purpose
Power7-optimized copy-user loop implementation using cache/vector-aware copy strategies for validation.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/copyuser_power7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/mem_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/mem_64.S

## Purpose
Imported 64-bit PowerPC memory primitives such as memset/memmove-style routines for validation.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/mem_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_64.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_64.S

## Purpose
Generic 64-bit PowerPC memcpy implementation copied into the selftest harness.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_64.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_power7.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_power7.S

## Purpose
Power7-optimized memcpy implementation with larger block and alignment handling.

## Important APIs, Types, and Functions
Important exported symbols are produced through `_GLOBAL*`/`FUNC_START` macros and are renamed to `test_*` by local `ppc_asm.h`; the code uses alignment labels, unrolled load/store loops, and fixup/feature macros depending on the routine.

## Control Flow
Callers enter with destination, source, and length. The assembly handles small copies, alignment prologues, main unrolled loops, tail bytes, and in copy-user variants fault fixup paths that return uncopied byte counts.

## State and Persistence
No durable state; routines mutate caller-provided memory and registers. Some variants use stack frames or vector state according to the copied kernel implementation.

## Dependencies and Integration Points
Depends on local shim headers, copied kernel macro conventions, and validation programs built by the copyloops Makefile.

## Risks and Test Signals
Risks are architecture-specific instruction availability, exception fixup accuracy, and divergence from kernel source. Validation failures show as data mismatches, redzone corruption, or incorrect fault accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_power7.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/exc_validate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/exc_validate.c

## Purpose
Validates copy loop behavior when the source or destination faults near a protected page boundary.

## Important APIs, Types, and Functions
Defines `UCONTEXT_NIA`, `segv_handler()`, `setup_segv_handler()`, `do_one_test()`, `MAX_LEN`, `test_copy_exception()`, and `main()`; the tested function is supplied by `COPY_LOOP` macro at build time.

## Control Flow
The test maps memory with inaccessible guard pages, installs a SIGSEGV handler that advances NIP over expected faulting instructions, calls the copy loop for short lengths around page boundaries, and checks returned uncopied bytes and signal/fault behavior.

## State and Persistence
Uses temporary mappings and process signal state only; no persistence.

## Dependencies and Integration Points
Depends on mmap/mprotect, PowerPC ucontext layout, `utils.h`, and build-time `COPY_LOOP` binding to one assembly routine.

## Risks and Test Signals
Risks include incorrect instruction-length advancement and page-size assumptions. Test signals are unexpected SIGSEGV handling, wrong remaining length, or process failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/exc_validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/linux/export.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/linux/export.h

## Purpose
Stub Linux export header for userspace assembly builds.

## Important APIs, Types, and Functions
Defines `EXPORT_SYMBOL(x)`, `EXPORT_SYMBOL_GPL(x)`, and `EXPORT_SYMBOL_KASAN(x)` as empty macros.

## Control Flow
No control flow; macros erase kernel export annotations during preprocessing.

## State and Persistence
No state.

## Dependencies and Integration Points
Included by copied kernel assembly sources that retain export annotations.

## Risks and Test Signals
Risk is low; if future assembly needs export side effects, the stub would need updating. Current signal is successful preprocessing/linking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/linux/export.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_stubs.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_stubs.S

## Purpose
Provides minimal stub symbols expected by copied memcpy assembly.

## Important APIs, Types, and Functions
Defines `memcpy` and `backwards_memcpy` as functions that immediately return via `blr`.

## Control Flow
No copy work is performed; the stubs satisfy unresolved symbol references or alternate paths during validation builds.

## State and Persistence
No state is changed except return control flow.

## Dependencies and Integration Points
Depends on local `asm/ppc_asm.h` `FUNC_START` macro.

## Risks and Test Signals
Risk is that an exercised path may incorrectly hit a no-op stub; validation data mismatches would expose that.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memcpy_stubs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memmove_validate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memmove_validate.c

## Purpose
Validates a build-selected memmove implementation across overlapping source/destination offsets.

## Important APIs, Types, and Functions
Declares `TEST_MEMMOVE()`, constants `BUF_LEN` and `MAX_OFFSET`, `testcase_run()`, and `main()`.

## Control Flow
`testcase_run()` allocates buffers, initializes patterns, runs the selected memmove across many forward/backward overlap cases, compares against libc/reference expectations, and returns failure on mismatch.

## State and Persistence
Heap buffers are process-local and freed on exit; no persistent state.

## Dependencies and Integration Points
Depends on build-time `TEST_MEMMOVE` macro mapping, malloc, libc memmove/memcmp, and `test_harness()`.

## Risks and Test Signals
Risks include incomplete overlap coverage beyond configured offsets. Failure signal is any mismatched byte pattern.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/memmove_validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/stubs.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/stubs.S

## Purpose
Supplies no-op helper symbols needed by copied copy-user loops.

## Important APIs, Types, and Functions
Defines `enter_vmx_ops`, `exit_vmx_ops`, and `__copy_tofrom_user_base` as immediate-return functions.

## Control Flow
There is no operational control flow beyond `blr` returns.

## State and Persistence
No state is persisted or intentionally modified.

## Dependencies and Integration Points
Included in validation link sets to satisfy kernel helper references outside the tested code path.

## Risks and Test Signals
Risk is accidental execution of a no-op helper hiding missing behavior; validation mismatches or missing VMX setup would reveal issues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/stubs.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/validate.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/validate.c

## Purpose
General data-integrity validator for a build-selected copy loop.

## Important APIs, Types, and Functions
Defines size/redzone constants, `COPY_LOOP()` prototype, `do_one()`, `test_copy_loop()`, and `main()`. It uses `POISON` redzones and a VMX threshold constant.

## Control Flow
`test_copy_loop()` allocates source/destination buffers, fills redzones, iterates lengths and offsets, calls the selected copy loop, checks copied bytes and untouched guard regions, and runs via `test_harness()`.

## State and Persistence
All state is heap memory local to the process. No files are written.

## Dependencies and Integration Points
Depends on the Makefile selecting `COPY_LOOP`, libc allocation/string routines, and `utils.h` harness macros.

## Risks and Test Signals
Risks are bounded coverage (`MAX_LEN`, `MAX_OFFSET`) and implementation-specific thresholds. Test signals are data mismatch, nonzero return for nonfaulting copies, or redzone corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/copyloops/validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/Makefile

## Purpose
Builds DEXCR tests and helper utilities.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS := dexcr_test hashchk_test`, `TEST_GEN_FILES := lsdexcr chdexcr`, includes lib.mk and flags.mk, links each target with `dexcr.c`, and adds helper object dependencies.

## Control Flow
The Makefile compiles common DEXCR helper logic into both tests and standalone tools, then delegates run/install rules to kselftest.

## State and Persistence
Only build outputs are persisted.

## Dependencies and Integration Points
Integrates PR_PPC_DEXCR selftests into the PowerPC suite and builds user utilities for listing/changing DEXCR controls.

## Risks and Test Signals
Risk is stale target dependencies when adding helper functions. Successful build and test harness runs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/chdexcr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/chdexcr.c

## Purpose
Command-line helper to change editable DEXCR aspects through prctl controls.

## Important APIs, Types, and Functions
Important functions are `die()`, `help()`, `apply_option()`, and `main()`. It uses `aspects[]`, `pr_set_dexcr()`, and option strings from `dexcr.h`.

## Control Flow
Main parses aspect options, maps them through `apply_option()`, and applies set/clear/onexec controls with prctl; help displays supported aspect names.

## State and Persistence
State changes are per-process DEXCR control bits and optional on-exec inheritance settings. No files are written.

## Dependencies and Integration Points
Depends on `dexcr.c` helpers, PowerPC prctl DEXCR API, and common parse/report helpers from `utils.h`.

## Risks and Test Signals
Risks are user confusion over current versus on-exec controls and unsupported aspects. Signals are prctl errors or updated values visible via `lsdexcr`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/chdexcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.c

## Purpose
Common helper implementation for DEXCR tests and utilities.

## Important APIs, Types, and Functions
Implements `dexcr_exists()`, `pr_which_to_aspect()`, `pr_get_dexcr()`, `pr_set_dexcr()`, `pr_dexcr_aspect_supported()`, `pr_dexcr_aspect_editable()`, `hashchk_triggers()`, `get_dexcr()`, `await_child_success()`, `hashst()`, `hashchk()`, and `do_bad_hashchk()`.

## Control Flow
Helpers probe DEXCR SPR access under a SIGILL handler, wrap prctl get/set operations, read userspace/hypervisor/effective DEXCR SPR values, wait for children, and emit raw hash instructions for NPHIE/hashchk tests.

## State and Persistence
State includes temporary signal handlers/jump buffers and hardware/process DEXCR state read or modified by callers. Hash helpers mutate caller-provided memory.

## Dependencies and Integration Points
Depends on `reg.h` mfspr/mtspr macros, `dexcr.h` raw instruction encodings, prctl constants, signal handling, and `utils.h` failure helpers.

## Risks and Test Signals
Risks include longjmp from signal contexts, unsupported SPR emulation, and raw instruction encoding correctness. Test signals are skipped unsupported hardware, SIGILL behavior, and child wait assertions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.h

## Purpose
Shared DEXCR declarations, aspect metadata, and raw hash instruction encodings.

## Important APIs, Types, and Functions
Defines DEXCR bit macros, `PPC_RAW_HASHST`, `PPC_RAW_HASHCHK`, `struct dexcr_aspect`, `aspects[]`, `enum dexcr_source`, and prototypes for all DEXCR helper functions.

## Control Flow
No runtime control flow, but macro expansion emits raw instructions and aspect table iteration drives the utilities/tests.

## State and Persistence
The static `aspects[]` table is read-only process data. DEXCR state is accessed through declared helpers.

## Dependencies and Integration Points
Depends on prctl constants and `reg.h` bit helpers. Included by every DEXCR test/tool.

## Risks and Test Signals
Risk is aspect table drift from kernel ABI or incorrect bit numbering. Build failures or prctl/hash tests reveal mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr_test.c

## Purpose
Tests prctl get/set semantics for editable DEXCR aspects, including current value changes and on-exec inheritance.

## Important APIs, Types, and Functions
Important functions are `dexcr_prctl_onexec_test_child()`, `dexcr_prctl_aspect_test()`, wrapper tests for IBRTPD/SRAPD/NPHIE, and `main()`.

## Control Flow
For each supported/editable aspect the test rejects invalid set+clear combinations, sets and clears the current aspect, sets on-exec and clear-on-exec controls, combines current/onexec controls, then forks and execs itself to verify inheritance is applied only after exec.

## State and Persistence
Mutates the calling process DEXCR aspect controls and child inherited state. No files are persisted.

## Dependencies and Integration Points
Depends on `dexcr.c`, prctl DEXCR API, `/proc/self/exe` exec, fork/wait, and `test_harness()`.

## Risks and Test Signals
Risks include leaving aspect state changed for later tests and kernels with only partial aspect support. Signals include precise errno `EINVAL`, DEXCR SPR bit checks, and child success/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/dexcr_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/hashchk_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/hashchk_test.c

## Purpose
Tests DEXCR NPHIE and hashchk/hashst behavior, including signal delivery and key sharing/randomization across exec, fork, and clone.

## Important APIs, Types, and Functions
Important functions are `require_nphie()`, `hashchk_handler()`, `hashchk_detected_test()`, `fill_hash_values()`, `count_hash_values_matches()`, `hashchk_exec_child()`, `hashchk_exec_random_key_test()`, `hashchk_fork_share_key_test()`, `hashchk_clone_share_key_test()`, and `main()`.

## Control Flow
The suite enables NPHIE, verifies a bad hashchk raises SIGILL/ILL_ILLOPN, execs a child to compare hash keys, forks to ensure key sharing, and uses clone with shared VM to verify thread-like sharing.

## State and Persistence
State includes process DEXCR NPHIE controls, global hash buffer contents, signal jump state, pipes for child output, and temporary clone stack mappings.

## Dependencies and Integration Points
Depends on DEXCR helpers, raw hash instructions, prctl, signal handling, fork/exec/clone, mmap, and `test_harness()`.

## Risks and Test Signals
Risks are hardware support and security-sensitive key semantics. Strong signals are wrong SIGILL code, identical hashes after exec, differing hashes after fork/clone, or inability to enable NPHIE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/hashchk_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/lsdexcr.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/lsdexcr.c

## Purpose
Command-line utility that displays DEXCR, HDEXCR, effective DEXCR bits, and prctl aspect configuration.

## Important APIs, Types, and Functions
Functions include `print_list()`, `print_dexcr()`, `print_aspect()`, `print_aspect_config()`, and `main()`, using `aspects[]`, `get_dexcr()`, and prctl helper functions.

## Control Flow
Main probes DEXCR support, prints raw/effective bit state, iterates known aspects, and reports support/editability/current/onexec controls.

## State and Persistence
Read-only except for transient output; it does not modify DEXCR state.

## Dependencies and Integration Points
Depends on `dexcr.c`, `dexcr.h`, SPR accessors, and prctl DEXCR API.

## Risks and Test Signals
Risks are reporting stale/unknown aspects if ABI evolves. Test signal is diagnostic output useful for interpreting DEXCR test skips/failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dexcr/lsdexcr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/Makefile

## Purpose
Builds DSCR selftests for explicit SPR access, inheritance, sysfs defaults, and user-mode DSCR behavior.

## Important APIs, Types, and Functions
Defines seven `TEST_GEN_PROGS`, includes lib.mk and flags.mk, links each generated program with `../harness.c`, and adds pthread flags for threaded DSCR tests.

## Control Flow
Build flow is delegated to common kselftest rules with per-target dependencies for the shared harness.

## State and Persistence
Only build products are persisted.

## Dependencies and Integration Points
Integrates DSCR tests under the PowerPC target and ensures threaded tests link with pthread.

## Risks and Test Signals
Risk is missing harness dependency or pthread flags. Successful build and execution of all seven programs are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr.h

## Purpose
Shared DSCR constants and helpers for reading/writing privileged, problem-state, and sysfs default DSCR values.

## Important APIs, Types, and Functions
Defines `THREADS`, `COUNT`, `DSCR_MAX`, paths `DSCR_DEFAULT` and `CPU_PATH`, barriers `rmb/wmb`, `READ_ONCE`, inline `get_dscr()`, `set_dscr()`, `get_dscr_usr()`, `set_dscr_usr()`, plus `get_default_dscr()` and `set_default_dscr()`.

## Control Flow
Inline helpers directly emit SPR reads/writes; sysfs helpers parse or write hex values and exit on I/O failure.

## State and Persistence
DSCR SPR and system default DSCR sysfs state can be modified by callers. The header itself stores no durable state.

## Dependencies and Integration Points
Depends on `reg.h` SPR macros and `utils.h` read/write helpers. Included by all DSCR tests.

## Risks and Test Signals
Risks include modifying global sysfs default DSCR without restoration and requiring DSCR hardware support. Tests guard with `PPC_FEATURE2_DSCR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_default_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_default_test.c

## Purpose
Tests that changes to the system default DSCR propagate immediately and consistently to threads.

## Important APIs, Types, and Functions
Defines `dscr_default_lockstep_writer()`, `dscr_default_lockstep_test()`, `struct random_thread_args`, `dscr_default_random_thread()`, `dscr_default_random_test()`, and `main()`.

## Control Flow
The lockstep test alternates a writer changing `/sys/devices/system/cpu/dscr_default` with a reader checking privileged and user DSCR. The random test starts 100 threads, synchronizes with a barrier, and randomly updates/checks the default under an rwlock.

## State and Persistence
Mutates system-wide default DSCR and restores the original value in `main()` when DSCR is supported. Thread synchronization state is process-local.

## Dependencies and Integration Points
Depends on DSCR hwcap, sysfs default DSCR, pthread semaphores/rwlocks/barriers, CPU binding, and `test_harness()`.

## Risks and Test Signals
Risks are global system impact while running and restoration failure after abrupt termination. Failure signals are mismatched DSCR reads or synchronization/sysfs errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_default_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_explicit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_explicit_test.c

## Purpose
Tests explicit DSCR updates through privileged and problem-state SPR access across concurrent threads and yields.

## Important APIs, Types, and Functions
Defines `dscr_explicit_lockstep_thread()`, `dscr_explicit_lockstep_test()`, `struct random_thread_args`, `dscr_explicit_random_thread()`, `dscr_explicit_random_test()`, and `main()`.

## Control Flow
The lockstep test alternates two threads updating DSCR and checking both access paths. The random test launches many threads that set DSCR through privileged and user helpers, optionally yield, and recheck values.

## State and Persistence
Mutates per-thread/process DSCR state and temporarily records original default DSCR for restoration. No files other than sysfs default access via helper are intended to persist.

## Dependencies and Integration Points
Depends on DSCR hwcap, pthread synchronization, scheduler yield, `dscr.h`, and common harness.

## Risks and Test Signals
Risks include concurrency flakiness if DSCR context switching is broken. Test signals are mismatches between `get_dscr()` and `get_dscr_usr()` or unexpected thread failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_explicit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_exec_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_exec_test.c

## Purpose
Verifies DSCR inheritance across exec.

## Important APIs, Types, and Functions
Uses `do_exec()`, `dscr_inherit_exec()`, and `main()`, plus `get_dscr()`, `set_dscr()`, and command-line child mode.

## Control Flow
Parent sets a DSCR value, execs or forks/execs itself with the expected value encoded in argv, and child mode validates the inherited DSCR after exec.

## State and Persistence
Mutates process DSCR and uses argv as transient expected-state transport. No durable files are written.

## Dependencies and Integration Points
Depends on `/proc/self/exe` or self executable path behavior, DSCR hwcap, and `test_harness()`.

## Risks and Test Signals
Risks are exec path assumptions and DSCR support absence. Test signal is exact inherited value match after exec.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_exec_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_test.c

## Purpose
Tests DSCR inheritance across fork without exec.

## Important APIs, Types, and Functions
Defines `dscr_inherit()` and `main()` using DSCR helper accessors and fork/wait checks.

## Control Flow
The parent iterates DSCR values, forks children, and children verify inherited DSCR values before exiting with status.

## State and Persistence
Only per-process DSCR state and child exit status are used.

## Dependencies and Integration Points
Depends on DSCR hardware support, fork/wait, and common harness.

## Risks and Test Signals
Risks are context-switch or fork inheritance regressions. Signals are child exit failures or mismatched DSCR values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_inherit_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_test.c

## Purpose
Validates per-CPU DSCR default sysfs files against the system DSCR default.

## Important APIs, Types, and Functions
Important functions are `check_cpu_dscr_default()`, `check_all_cpu_dscr_defaults()`, `dscr_sysfs()`, and `main()`.

## Control Flow
The test writes several default DSCR values, walks CPU sysfs directories, reads each CPU default file, and verifies all online CPU entries reflect the expected value.

## State and Persistence
Mutates global DSCR default and restores original value in the test wrapper. Reads per-CPU sysfs state.

## Dependencies and Integration Points
Depends on `/sys/devices/system/cpu/dscr_default`, per-CPU sysfs layout, directory iteration, DSCR hwcap, and harness.

## Risks and Test Signals
Risks include system-wide default mutation and hotplug/sysfs races. Failures are per-CPU value mismatches or sysfs I/O errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_thread_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_thread_test.c

## Purpose
Checks that thread DSCR values follow sysfs default updates as expected.

## Important APIs, Types, and Functions
Defines `test_thread_dscr()`, `check_cpu_dscr_thread()`, `dscr_sysfs_thread()`, and `main()`.

## Control Flow
The test writes DSCR defaults, creates or binds execution to CPU contexts, and verifies thread-visible DSCR state matches expected default values.

## State and Persistence
Mutates and restores default DSCR; thread state is transient.

## Dependencies and Integration Points
Depends on DSCR sysfs, pthread/scheduler behavior through `dscr.h`, and harness utilities.

## Risks and Test Signals
Risks are global default mutation and scheduling races. Signal is any mismatch between expected and observed thread DSCR.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_sysfs_thread_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_user_test.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_user_test.c

## Purpose
Tests direct user/problem-state DSCR access.

## Important APIs, Types, and Functions
Defines `check_dscr()`, `dscr_user()`, and `main()` using problem-state `get_dscr_usr()`/`set_dscr_usr()` helpers.

## Control Flow
The test iterates DSCR values, writes through the user SPR accessor, reads them back, and validates string/argument parsing where applicable.

## State and Persistence
Mutates only the running process DSCR state.

## Dependencies and Integration Points
Depends on DSCR hwcap and user SPR access/emulation support plus common harness.

## Risks and Test Signals
Failure indicates user DSCR writes are not preserved or read back correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/dscr/dscr_user_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/Makefile

## Purpose
Registers EEH shell selftests and helper scripts with kselftest.

## Important APIs, Types, and Functions
`TEST_PROGS` lists `eeh-basic.sh`, `eeh-vf-aware.sh`, and `eeh-vf-unaware.sh`; `TEST_FILES := eeh-functions.sh`; includes `../../lib.mk`.

## Control Flow
No custom logic; kselftest handles install and execution.

## State and Persistence
No state here; runtime state is in sysfs/debugfs during shell tests.

## Dependencies and Integration Points
Integrates EEH recovery tests into the PowerPC selftest suite.

## Risks and Test Signals
Risk is high runtime impact from EEH injection, but this Makefile only exposes the scripts. Successful install must include the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-basic.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-basic.sh

## Purpose
Runs basic EEH injection/recovery against PCI devices that are safe and recoverable.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; uses `eeh_test_prep`, iterates `/sys/bus/pci/devices`, checks `eeh_can_break`, `eeh_can_recover`, and calls `eeh_one_dev`.

## Control Flow
After preparation, each eligible non-bridge/non-excluded PCI function is broken through debugfs, checked, waited for recovery, and logged.

## State and Persistence
Mutates hardware error state through EEH debugfs and may temporarily disrupt PCI devices. No files are intended to persist beyond sysfs/debugfs writes.

## Dependencies and Integration Points
Depends on PowerPC EEH support, mounted debugfs, PCI sysfs, and recovery-capable drivers.

## Risks and Test Signals
Risk is device disruption, especially drivers without recovery. Skip/fail/pass signals come from helper return codes and recovery timeout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-basic.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-functions.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-functions.sh

## Purpose
Shared shell library for EEH support detection, PE state checks, device break/recovery, and SR-IOV VF setup/cleanup.

## Important APIs, Types, and Functions
Defines `log`, `pe_ok`, `eeh_supported`, `eeh_test_prep`, `eeh_can_break`, `eeh_one_dev`, `eeh_has_driver`, `eeh_can_recover`, `eeh_find_all_pfs`, `eeh_enable_vfs`, and `eeh_disable_vfs`.

## Control Flow
Helpers check `/proc/powerpc/eeh`, verify debugfs controls, raise max freeze count, reject bridges/ahci/bad PE state, inject EEH errors, poll recovery up to `EEH_MAX_WAIT`, discover SR-IOV PFs, enable one VF per PF, and disable VFs afterward.

## State and Persistence
State is hardware/sysfs/debugfs state: EEH freeze counters, PE isolation/recovery state, and `sriov_numvfs` changes. No ordinary files are persisted.

## Dependencies and Integration Points
Depends on PCI sysfs, PowerPC EEH debugfs files, pseries RTAS indicators for SR-IOV, shell utilities, and kselftest skip code 4.

## Risks and Test Signals
Risks are substantial because it intentionally breaks PCI devices. The helper mitigates by skipping bridges, ahci, unsupported recovery, and bad initial PE states; failures are recovery timeout, missing controls, or unsafe device rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-functions.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-aware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-aware.sh

## Purpose
Tests EEH behavior for SR-IOV virtual functions whose drivers are EEH-aware.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; calls preparation, enables VFs, filters with `eeh_can_recover`, injects with `eeh_one_dev`, and disables VFs afterward.

## Control Flow
The script enables one VF per discovered PF, tests recoverable VFs, logs results, then tears VFs down.

## State and Persistence
Mutates `sriov_numvfs` and EEH state for selected devices.

## Dependencies and Integration Points
Depends on SR-IOV-capable hardware, pseries/platform support, EEH debugfs, and recovery-aware VF drivers.

## Risks and Test Signals
Risks are VF disruption and incomplete cleanup on abrupt exit. Signals are skip when no VFs, fail on unrecovered VF, and cleanup through `eeh_disable_vfs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-aware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-unaware.sh -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-unaware.sh

## Purpose
Tests EEH handling for SR-IOV VFs without driver recovery callbacks or awareness.

## Important APIs, Types, and Functions
Sources `eeh-functions.sh`; prepares EEH, enables VFs, selects cases based on recovery capability, invokes EEH injection, then disables VFs.

## Control Flow
Flow mirrors the VF-aware test but targets devices expected to exercise remove/reprobe or non-aware recovery paths.

## State and Persistence
Mutates VF enablement and EEH/debugfs device state.

## Dependencies and Integration Points
Depends on SR-IOV PF discovery, PCI sysfs, EEH debugfs, and helper filtering.

## Risks and Test Signals
Risks include device removal/reprobe side effects and cleanup failure. Test signal is whether the platform recovers or skips unsuitable VFs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/eeh/eeh-vf-unaware.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/flags.mk -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/flags.mk

## Purpose
Common compiler/linker flags for PowerPC selftests.

## Important APIs, Types, and Functions
Sets `GIT_VERSION`, appends include paths for `../include` and local `include`, enables warnings/debug/`-DGIT_VERSION`, and adds `-no-pie` linker mode.

## Control Flow
No control flow; included by child Makefiles before compilation.

## State and Persistence
No runtime state. Build commands inherit the variables.

## Dependencies and Integration Points
Integrates shared headers and version metadata across PowerPC selftests.

## Risks and Test Signals
Risk is compiler support for `-no-pie` or warning flags. Build output confirms compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/flags.mk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/harness.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/harness.c

## Purpose
Process-isolating test harness used by many PowerPC C selftests.

## Important APIs, Types, and Functions
Defines `KILL_TIMEOUT`, `run_test()`, `sig_handler()`, `test_harness_set_timeout()`, and `test_harness()`, and emits subunit results through `subunit.h` helpers.

## Control Flow
`test_harness()` installs timeout signal handling, forks the test function in a child, waits with timeout handling, kills hung children, and reports pass/fail/skip based on exit status and signals.

## State and Persistence
State includes global timeout configuration, child process state, signal alarms, and subunit output. No files are persisted.

## Dependencies and Integration Points
Depends on fork/wait/signal/alarm, `utils.h` result conventions, and `subunit.h` output formatting.

## Risks and Test Signals
Risks include masking child signal details or timeout races. Test signal is consistent subunit reporting and cleanup of hung tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/harness.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/basic_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/basic_asm.h

## Purpose
Shared PowerPC assembly macros for stack frames, load/store word size selection, immediates, and basic prologue/epilogue handling.

## Important APIs, Types, and Functions
Defines `PPC_LL`, `PPC_STL`, `PPC_STLU`, `LOAD_REG_IMMEDIATE`, ABI-specific `STACK_FRAME_*` offsets, `STACK_FRAME_PARAM`, `STACK_FRAME_LOCAL`, `PUSH_BASIC_STACK`, and `POP_BASIC_STACK`.

## Control Flow
No standalone flow; macros expand into assembly used by math/register tests.

## State and Persistence
No runtime state except generated stack frame layout in callers.

## Dependencies and Integration Points
Depends on `<ppc-asm.h>` and `<asm/unistd.h>`. Included by FPU/VMX/VSX assembly helpers.

## Risks and Test Signals
Risk is ABI offset mismatch between 32/64-bit or ELFv1/v2 conventions. Assembly tests expose broken save/restore or syscall frame handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/basic_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/fpu_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/fpu_asm.h

## Purpose
Assembly helper macros for preserving and loading nonvolatile FPU registers.

## Important APIs, Types, and Functions
Defines `PUSH_FPU`, `POP_FPU`, and declares/implements `load_fpu` macro entry behavior for f14-f31 style register setup.

## Control Flow
Macros save FPU registers to stack-relative slots and restore them around test assembly bodies.

## State and Persistence
State is caller stack storage and FPU register contents.

## Dependencies and Integration Points
Depends on `basic_asm.h` stack layout. Used by `math/fpu_asm.S`.

## Risks and Test Signals
Risk is corrupting nonvolatile FPU registers or stack offsets. FPU syscall/preempt/signal tests catch mismatches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/fpu_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/gpr_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/gpr_asm.h

## Purpose
Assembly helper macros for saving/restoring nonvolatile general purpose registers.

## Important APIs, Types, and Functions
Defines `__PUSH_NVREGS`, `__POP_NVREGS`, public push/pop variants, and `load_gpr` declaration/body macro support.

## Control Flow
Macros emit stores/loads for r14-r31 at stack offsets, including variants below FPU save areas.

## State and Persistence
State is stack save area and GPR contents.

## Dependencies and Integration Points
Depends on `basic_asm.h`. Used by register preservation and transactional-memory style tests.

## Risks and Test Signals
Risk is ABI register preservation breakage; tests using load/store GPR helpers expose corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/gpr_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/instructions.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/instructions.h

## Purpose
Raw instruction encoding helpers for PowerPC copy/paste and prefixed load/store instructions used when assemblers may not know mnemonics.

## Important APIs, Types, and Functions
Defines `PPC_INST_COPY*`, `PPC_INST_PASTE*`, prefix construction macros, base opcode constants, and convenience macros such as `PLBZ`, `PLD`, `PSTD`, `PLXSD`, `PSTXV0`, and related FP/VSX forms.

## Control Flow
No control flow; macros emit `.long` words through `stringify_in_c` for inline assembly.

## State and Persistence
No state is stored.

## Dependencies and Integration Points
Used by alignment and copy/paste tests to encode architecture-specific instructions independent of toolchain mnemonic support.

## Risks and Test Signals
Risk is incorrect bitfield construction causing SIGILL or testing the wrong instruction. Alignment/copy tests are the signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/instructions.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/pkeys.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/pkeys.h

## Purpose
PowerPC protection-key helper header for selftests that need pkey syscalls and AMR rights manipulation.

## Important APIs, Types, and Functions
Defines pkey rights constants, syscall numbers, bit masks, `pkey_set_rights()`, `sys_pkey_mprotect()`, `sys_pkey_alloc()`, `sys_pkey_free()`, `pkeys_unsupported()`, `siginfo_pkey()`, and `pkey_rights()`.

## Control Flow
Helpers wrap syscalls, modify AMR rights for a key, detect unsupported platforms, and decode pkey from siginfo layout.

## State and Persistence
Mutates per-thread AMR/pkey rights and memory protection state in callers; no files are persisted.

## Dependencies and Integration Points
Depends on `reg.h` AMR helpers, `utils.h`, mmap/pkey syscall ABI, and signal ABI.

## Risks and Test Signals
Risks include hard-coded syscall numbers/layout offsets and platform support variance. Pkey tests signal unsupported or mismatched fault metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/pkeys.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/reg.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/reg.h

## Purpose
Central PowerPC special-purpose register and bitfield helper header for selftests.

## Important APIs, Types, and Functions
Defines SPR numbers for PMU, DEXCR/HDEXCR, DSCR, TM, AMR, PVR, BESCR, MSR/TEXASR bits, VSX instruction encodings, `mfspr`/`mtspr` style macros, and prototypes for register save/load assembly helpers.

## Control Flow
No standalone flow; macros compile to SPR reads/writes and raw instruction words in callers.

## State and Persistence
Callers may mutate hardware/thread SPR state through macros; the header itself is static definitions only.

## Dependencies and Integration Points
Included broadly by DEXCR, DSCR, PMU, math, and register tests. Works with `lib/reg.S` implementations.

## Risks and Test Signals
Risk is ABI/SPR number drift or unsafe privileged SPR access. Hardware feature checks and signal handling in tests mitigate some cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/subunit.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/subunit.h

## Purpose
Small output helper for subunit-style PowerPC selftest reporting.

## Important APIs, Types, and Functions
Defines macros/functions for emitting test start, success, failure, skip, and error lines in a consistent format.

## Control Flow
No complex control flow; harness code calls these output helpers around child execution.

## State and Persistence
No state beyond stdout/stderr output.

## Dependencies and Integration Points
Integrated by `harness.c` for tests that use PowerPC custom harness rather than generic kselftest harness.

## Risks and Test Signals
Risk is reporting format drift affecting parsers. Test signal is readable subunit output from harnessed tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/subunit.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/utils.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/utils.h

## Purpose
Common C utility header for PowerPC selftests, providing result macros, parsing, binding, hardware capability checks, timing, and syscall helpers.

## Important APIs, Types, and Functions
Defines FAIL/SKIP macros, `ARRAY_SIZE`, binding constants, hardware capability predicates, timebase helpers, parsing/read/write helpers, perf/syscall wrappers, and signal-handler push/pop declarations used across tests.

## Control Flow
Most content is inline helpers/macros; callers use them to skip unsupported hardware, fail with messages, bind CPUs, read sysfs/proc numeric values, and measure time.

## State and Persistence
Some helpers mutate process affinity, signal handlers, or target sysfs files when called. The header itself persists no state.

## Dependencies and Integration Points
Included throughout PowerPC selftests and paired with `../utils.c` in targets that need non-inline implementations.

## Risks and Test Signals
Risk is that utility macros exit from deep call sites, so cleanup must be handled by callers. Test signals are consistent skip/fail behavior and correct feature detection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vmx_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vmx_asm.h

## Purpose
Assembly macros for saving/restoring and loading VMX/Altivec registers.

## Important APIs, Types, and Functions
Defines `PUSH_VMX`, `POP_VMX`, and `load_vmx` helper patterns for vector registers.

## Control Flow
Macros expand to vector store/load sequences around assembly tests.

## State and Persistence
State is caller stack save area and VMX register contents.

## Dependencies and Integration Points
Depends on `basic_asm.h` and is used by VMX math/preempt/signal tests.

## Risks and Test Signals
Risk is register corruption or requiring Altivec support. VMX tests catch mismatches or skip unsupported hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vmx_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vsx_asm.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vsx_asm.h

## Purpose
Assembly macros/helpers for loading and storing nonvolatile VSX registers.

## Important APIs, Types, and Functions
Defines `load_vsx` and `store_vsx` style helper sequences for vs20-vs31.

## Control Flow
Generated assembly copies VSX register contents to/from caller-provided buffers.

## State and Persistence
State is VSX register file and memory buffers supplied by callers.

## Dependencies and Integration Points
Depends on `basic_asm.h`; used by VSX-specific math tests.

## Risks and Test Signals
Risk is VSX availability and ABI register mapping. VSX preempt/signal tests provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/include/vsx_asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/lib/reg.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/lib/reg.S

## Purpose
Assembly implementation of common register load/store helpers declared in `include/reg.h`.

## Important APIs, Types, and Functions
Exports `load_gpr`, `store_gpr`, `store_fpr`, `loadvsx`, and `storevsx` via `FUNC_START`/`FUNC_END`.

## Control Flow
Each helper sequentially loads or stores a register class from/to caller-provided buffers: r14-r31 for GPRs, f0-f31 for FPR stores, and vs0-vs63 for VSX load/store.

## State and Persistence
Mutates register files and caller-provided memory only. No persistent state.

## Dependencies and Integration Points
Depends on `<ppc-asm.h>` and `reg.h` raw VSX load/store macros. Linked into PowerPC tests needing register state setup/inspection.

## Risks and Test Signals
Risk is ABI register numbering or buffer sizing mistakes. Downstream tests signal failures through register mismatch checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/lib/reg.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/Makefile -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/Makefile

## Purpose
Builds PowerPC math/register-state selftests for FPU, VMX, VSX, and MMA.

## Important APIs, Types, and Functions
Defines `TEST_GEN_PROGS`, includes lib.mk and flags.mk, links generated programs with `../harness.c`, adds `-O2 -g -pthread -m64 -maltivec`, and adds per-target assembly/source dependencies.

## Control Flow
The Makefile builds FPU targets with `fpu_asm.S`, VMX/VSX targets with their assembly helpers and `../utils.c`, and MMA with `mma.c`/`mma.S`.

## State and Persistence
Only build output is persisted.

## Dependencies and Integration Points
Integrates math context preservation tests into the PowerPC selftest tree.

## Risks and Test Signals
Risks are compiler support for Altivec/VSX/MMA flags and target dependency drift. Build success plus harness runs are the signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu.h

## Purpose
Small helper for generating varied floating-point test data.

## Important APIs, Types, and Functions
Defines `randomise_darray(double *darray, int num)`, which fills an array with random positive/negative integers squared or reciprocal values.

## Control Flow
The function loops over requested elements and writes deterministic-from-`random()` double values.

## State and Persistence
Mutates caller-provided arrays only.

## Dependencies and Integration Points
Included by FPU syscall/preempt/signal tests to seed expected register contents.

## Risks and Test Signals
Risk is division by zero if `random()` returns zero on a reciprocal path; in practice randomization is used for stress data, and failures would show as register comparison mismatch or FP exception behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_asm.S

## Purpose
Assembly routines that load, check, and preserve FPU registers across fork, preemption, and signal tests.

## Important APIs, Types, and Functions
Exports `check_fpu`, `check_all_fprs`, `test_fpu`, and `preempt_fpu`; uses `basic_asm.h` and `fpu_asm.h` save/restore macros.

## Control Flow
`check_all_fprs` compares f0-f31 against an expected double array. `test_fpu` loads FPRs, performs a fork syscall, returns the child pid to C, and checks registers. `preempt_fpu` loads FPRs, atomically decrements a start counter, loops checking registers while a running flag remains true, and restores state.

## State and Persistence
Mutates FPU registers, stack frame, shared counters, and fork child state. No files are written.

## Dependencies and Integration Points
Linked into `fpu_syscall`, `fpu_preempt`, and `fpu_signal` targets.

## Risks and Test Signals
Risks include ABI save/restore errors, use of scratch registers f30/f31 during checks, and syscall clobber assumptions. C tests report any nonzero return as register corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_asm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_denormal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_denormal.c

## Purpose
Regression test for POWER8 FPU denormal handling during conversion and process exit.

## Important APIs, Types, and Functions
Defines `test_denormal_fpu()` and `main()`. The test crafts a 32-bit denormal float bit pattern, converts it to double, and checks the expected renormalized 64-bit representation.

## Control Flow
Main runs the single test through `test_harness()`.

## State and Persistence
Only local FP variables are used; no persistent state.

## Dependencies and Integration Points
Depends on FPU behavior, libc `memcpy`, and PowerPC harness utilities.

## Risks and Test Signals
Risk is CPU/model-specific FP denormal behavior; failure indicates wrong result or potential kernel FP save/restore issues described by the file comment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_denormal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_preempt.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_preempt.c

## Purpose
Stress-tests whether FPU registers survive preemption across many worker threads.

## Important APIs, Types, and Functions
Defines `PREEMPT_TIME`, `THREAD_FACTOR`, thread-local `darray`, globals `threads_starting`/`running`, external `preempt_fpu()`, `preempt_fpu_c()`, `test_preempt_fpu()`, and `main()`.

## Control Flow
The test creates `online_cpus * 8` threads, each randomizes expected FP data and enters assembly checking loop. After all start, the main thread sleeps 60 seconds to allow preemption, clears `running`, joins workers, and fails on any nonzero worker result.

## State and Persistence
State is thread-local expected arrays, shared counters, and FPU register contents. No durable files.

## Dependencies and Integration Points
Depends on pthreads, `fpu_asm.S`, CPU scheduler preemption, and common harness.

## Risks and Test Signals
Risk is long runtime and scheduler-dependent coverage. Any register mismatch is a strong failure; a pass is stress evidence, not proof that preemption happened.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_preempt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_signal.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_signal.c

## Purpose
Checks that FPU register state is accurately represented in signal contexts while worker threads continuously validate registers.

## Important APIs, Types, and Functions
Defines `ITERATIONS`, `THREAD_FACTOR`, thread-local `darray`, `signal_fpu_sig()`, `signal_fpu_c()`, `test_signal_fpu()`, and `main()`, using external `preempt_fpu()`.

## Control Flow
Workers install a SIGUSR1 SA_SIGINFO handler, randomize FPU data, and enter the assembly checking loop. The main thread sends SIGUSR1 to every worker repeatedly, then stops workers and fails if either assembly checks or signal-context FP register comparisons failed.

## State and Persistence
State is thread-local expected FP arrays, global `bad_context`, shared counters, and signal handlers. No persistence.

## Dependencies and Integration Points
Depends on pthread signals, ucontext/mcontext FP register layout, `fpu_asm.S`, and harness utilities.

## Risks and Test Signals
Risks include signal delivery timing and scratch-register exclusions for f30/f31. Failure signals are nonzero worker return or `bad_context` true.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_syscall.c -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_syscall.c

## Purpose
Tests whether FPU registers survive syscall/fork paths under additional process activity.

## Important APIs, Types, and Functions
Defines external `test_fpu()`, global `darray`, `syscall_fpu()`, `test_syscall_fpu()`, and `main()`.

## Control Flow
`syscall_fpu()` randomizes FP data and calls assembly `test_fpu()` 1000 times; that assembly performs fork and validates FPRs in parent/child paths. `test_syscall_fpu()` forks additional processes to increase context switching and aggregates child results.

## State and Persistence
State includes global expected FP array and child process statuses. No files are written.

## Dependencies and Integration Points
Depends on `fpu_asm.S`, fork/wait, scheduler behavior, and PowerPC harness.

## Risks and Test Signals
Risks include high fork count and noisy failures if fork is resource-limited. Failure indicates FPU register corruption across syscall/fork or child status errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/fpu_syscall.c -->
