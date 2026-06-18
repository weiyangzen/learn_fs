# subset-b-009380 research

Grouped research report for selected stress-ng stressors under `sources/test-tools/stress-ng`. Each section title preserves the exact source path and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seek.c -->
# sources/test-tools/stress-ng/stress-seek.c

Purpose: implements the `seek` stressor, which creates a temporary sparse file and repeatedly performs random `lseek`, read, write, optional hole-punch, and invalid seek operations. It stresses filesystem offset handling, sparse extent traversal, 32/64-bit seek paths, and error handling around unusual `whence` and offset values.

Important APIs/types/functions: `stress_seek`, `stress_shim_lseek`, `max_off_t`, `stress_fs_temp_dir_make_args`, `stress_fs_temp_filename_args`, `stress_fs_type_get`, `stress_setting_get`, `stress_metrics_set`, `lseek`, optional `lseek64`, `read`, `write`, `shim_fallocate`, `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, `SEEK_DATA`, `SEEK_HOLE`, and `FALLOC_FL_PUNCH_HOLE`.

Control flow: the stressor clamps `seek-size`, creates and immediately unlinks a temporary file, seeks near the requested end, writes one 512-byte block, then enters the synchronized run loop. Each iteration seeks to random offsets for a write and read, optionally verifies full read size, exercises end/current/data/hole seeks, optionally follows data/hole transitions, optionally punches an 8 KiB hole, and finally performs deliberately invalid seeks on a bad fd, invalid offsets, invalid `whence`, and out-of-range data/hole offsets.

State and persistence behavior: persistent state is limited to one unlinked temporary file descriptor whose blocks and holes change during the run; cleanup closes the descriptor and removes the temp directory. Static metric variables accumulate sampled seek latency and total seek count across the worker lifetime.

Dependencies and integration points: registered through `stress_seek_info` with `CLASS_IO | CLASS_OS`, optional verification, and `seek-size`/`seek-punch` options. It depends on stress-ng filesystem helpers, random generators, global option flags for minimize/maximize/verify, and platform feature macros for optional seek and fallocate behavior.

Risks and test signals: filesystem-specific behavior is intentionally variable, so `EINVAL`, unsupported data/hole seeking, and `EOPNOTSUPP` on punching are tolerated in selected paths. Real failures are unexpected read/write/seek errors, verify-mode short reads, leaked temp files, incorrect size clamping, or metrics that never observe successful seeks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sem-sysv.c -->
# sources/test-tools/stress-ng/stress-sem-sysv.c

Purpose: implements the `sem-sysv` stressor for System V semaphore creation, operation, metadata queries, invalid argument coverage, and multi-process contention. It stresses `semget`, `semop`, optional `semtimedop`, and many `semctl` commands against a shared semaphore set.

Important APIs/types/functions: `stress_semaphore_sysv_init`, `stress_semaphore_sysv_deinit`, `stress_semaphore_sysv_thrash`, `semaphore_sysv_spawn`, `stress_sem_sysv`, `stress_semun_t`, `semget`, `semctl`, `semop`, optional `semtimedop`, Linux `/proc/sysvipc/sem`, `stress_sync_s_pids_mmap`, `stress_sync_start_*`, and `stress_kill_and_wait_many`.

Control flow: initialization probes invalid `semget` cases, chooses an odd key to avoid core-resource collisions, creates a three-semaphore set, and initializes semaphore 0 to 1. `stress_sem_sysv` installs child handling, checks initialization, maps a PID table, spawns the configured number of children, releases them after the parent sync point, then waits until the run ends and kills/reaps them. Each child loops through timed or normal wait/signal operations, increments bogo ops, periodically reads proc info, exercises `IPC_STAT`/`IPC_SET`, `GETALL`, optional `SETALL`, Linux info/stat commands, value/count queries, invalid `semctl` commands, invalid `semop`/`semtimedop` arguments, and a direct `__NR_semctl` syscall when available.

State and persistence behavior: the shared semaphore id/key/init flag live in `g_shared->sem_sysv` across workers and are removed in deinit via `IPC_RMID`. Child state is process-local except for semaphore mutations and `SEM_UNDO` adjustments. `sem-sysv-setall` can intentionally perturb semaphore values, so it is option-controlled.

Dependencies and integration points: registered with `.init` and `.deinit`, `CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, always verify, and options `sem-sysv-procs` and `sem-sysv-setall`. It depends on System V IPC headers, stress-ng synchronization helpers, kill/reap helpers, and Linux-only proc/stat commands behind guards.

Risks and test signals: resource limits can cause skip/no-resource exits if the set cannot be created or PIDs cannot be mapped. Important signals are unexpected semaphore operation failures, semaphore leaks after deinit, hangs in child waits, incorrect handling of `semtimedop` availability, or invalid-argument probes accidentally mutating the live set beyond recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sem-sysv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sem.c -->
# sources/test-tools/stress-ng/stress-sem.c

Purpose: implements the POSIX `sem` stressor, using pthreads to contend on a local or process-shared `sem_t` with `sem_trywait`, `sem_timedwait`, `sem_wait`, `sem_post`, and `sem_getvalue`.

Important APIs/types/functions: `stress_sem_init`, `stress_sem_deinit`, `stress_sem_thrash`, `stress_sem`, `stress_sem_pthread_t`, `sem_init`, `sem_destroy`, `sem_getvalue`, `sem_trywait`, `sem_timedwait`, `sem_wait`, `sem_post`, `pthread_create`, `pthread_cancel`, `pthread_join`, and `stress_mmap_populate`.

Control flow: global init maps and initializes a process-shared semaphore for `--sem-shared`. The worker chooses thread count from settings/minimize/maximize and chooses shared mode from settings/aggressive mode. It initializes a local semaphore when not shared, synchronizes start, spawns pthreads, lets them loop through trywait/timedwait/wait modes, and later cancels/joins all successful threads while aggregating per-thread call counters.

State and persistence behavior: local semaphore state is per worker and destroyed at exit; shared semaphore state is a MAP_SHARED anonymous mapping named `shared-semaphore` and destroyed/unmapped by deinit. Each thread updates local metric counters and the common bogo counter after successful lock acquisition and post.

Dependencies and integration points: registered with init/deinit hooks, `CLASS_OS | CLASS_SCHEDULER | CLASS_IPC`, always verify, and `sem-procs`/`sem-shared` options. It depends on POSIX semaphores, pthread support, stress-ng mmap helpers, scheduler yielding, and global option flags.

Risks and test signals: failure modes include missing POSIX semaphore support, inability to allocate/init the shared semaphore, no threads created, unexpected semaphore API errors, and cancellation while updating bogo state. Test signals include nonzero call-rate metrics for each wait mode and successful cleanup of local or shared semaphores.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sendfile.c -->
# sources/test-tools/stress-ng/stress-sendfile.c

Purpose: implements the `sendfile` stressor, copying a preallocated temporary file to `/dev/null` using the kernel `sendfile` path and periodically probing invalid fd, offset, size, and mode combinations.

Important APIs/types/functions: `stress_sendfile`, `sendfile`, `shim_posix_fallocate`, `shim_fallocate`, `stress_fs_temp_dir_make_args`, `stress_fs_temp_filename_args`, `stress_fs_bad_fd_get`, `stress_metrics_set`, `open`, `close`, and `/dev/null`.

Control flow: the worker resolves `sendfile-size`, creates a temp directory and file, allocates the requested size, reopens it read-only, unlinks it, opens `/dev/null` writable, synchronizes start, and loops calling `sendfile(fdout, fdin, &offset, sz)`. Most calls are fast; every 1001st successful call contributes timing/byte metrics. Every 256 iterations it exercises invalid destination/source descriptors, negative offset, `(size_t)-1` size, zero-byte no-op, read-only destination, write-only source, and truncated reads.

State and persistence behavior: all durable state is a temporary unlinked file and `/dev/null` fd; temp directories are removed at exit. Metrics accumulate measured bytes/time for sampled calls and export MB/sec.

Dependencies and integration points: registered as `CLASS_PIPE_IO | CLASS_OS`, always verify, with `sendfile-size` option. It requires `<sys/sendfile.h>`, `sendfile`, and a glibc feature gate; otherwise it reports unimplemented.

Risks and test signals: expected skips include fallocate interruption/resource failure and runtime `ENOSYS`. Real failures are unexpected `sendfile` errors, failure to close descriptors/remove temp directories, or metrics staying at zero despite successful copies.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sendfile.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-session.c -->
# sources/test-tools/stress-ng/stress-session.c

Purpose: implements the `session` stressor, repeatedly creating child and grandchild processes that call `setsid`, validate `getsid`, exercise `vhangup`, and mix waited and orphaned process paths.

Important APIs/types/functions: `session_error_t`, `stress_session_error`, `stress_session_return_status`, `stress_session_set_and_get`, `stress_session_child`, `stress_session`, `setsid`, `getsid`, `fork`, `waitpid`, optional `wait4`, `pipe`, and `shim_vhangup`.

Control flow: the parent creates a pipe and synchronizes start. For each iteration it forks a child; the child closes the read end, creates a new session, forks a grandchild, and either waits for the grandchild or intentionally leaves it orphaned about 25 percent of the time. The grandchild also creates a session, calls `vhangup`, writes a success status, and exits. The parent reads a structured error from the pipe, waits for the child, reports failures, and increments bogo ops.

State and persistence behavior: state is transient process/session state plus a pipe-carried status structure. No filesystem persistence is created. Resource failures for grandchild fork are treated as successful no-resource pressure in the child path.

Dependencies and integration points: registered as `CLASS_SCHEDULER | CLASS_OS` with always verify. It depends on process creation, wait semantics, stress-ng process state reporting, and optional rusage collection through `wait4`.

Risks and test signals: risks include fork pressure, races around orphan reaping, pipe read ordering, and platform-specific `vhangup` behavior. Test signals are failures from `setsid`, `getsid`, mismatched session ids, fork/wait failures, or unexpected child exit statuses.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-session.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-set.c -->
# sources/test-tools/stress-ng/stress-set.c

Purpose: implements the `set` stressor, exercising a broad set of identity, process-group, hostname/domain, time, signal-mask, filesystem uid/gid, group-list, and resource-limit setter system calls with valid and invalid inputs.

Important APIs/types/functions: `stress_set`, `stress_rlimit_info_t`, `rlimit_resources`, `stress_capabilities_check`, `getrlimit`, `setrlimit`, `setsid`, `setgid`, `setuid`, `sethostname`, `setpgid`, `settimeofday`, `setpgrp`, `setgroups`, `setreuid`, `setregid`, `setresuid`, `setresgid`, `setfsgid`, `setfsuid`, `shim_sgetmask`, `shim_ssetmask`, `shim_setdomainname`, and `shim_stime`.

Control flow: the stressor snapshots existing resource limits, allocates hostname buffers, captures current hostname/domain context, synchronizes start, then loops through many setter APIs. It usually restores current values after valid calls and deliberately issues invalid or privilege-requiring calls to exercise error paths. It periodically checks that unprivileged `setreuid`/hard-limit raises do not unexpectedly succeed, and it calls `stime` only once to avoid repeated clock changes.

State and persistence behavior: it touches process credentials, groups, process group/session state, host/domain names, resource limits, and time APIs. Most calls use current values or restore snapshots; hostname/domain/time calls are guarded by capability expectations and error tolerance.

Dependencies and integration points: registered as `CLASS_OS`, always verify. It depends on capability checks (`SHIM_CAP_SYS_RESOURCE`, `SHIM_CAP_SETUID`, `SHIM_CAP_SYS_TIME`), platform headers for fsuid and groups, stress-ng shim wrappers, and saved rlimit state.

Risks and test signals: this is privilege-sensitive and can behave differently under root, containers, Cygwin, or restricted capabilities. Real signals include setters succeeding without required capability, unexpected errno values, inability to restore limits, allocation failure, or platform-specific setters changing global host/domain state.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shellsort.c -->
# sources/test-tools/stress-ng/stress-shellsort.c

Purpose: implements the `shellsort` CPU/cache/memory stressor, repeatedly shell-sorting arrays of 32-bit integers in forward and reverse order and optionally verifying sort correctness.

Important APIs/types/functions: `shellsort32`, `stress_shellsort`, `stress_shellsort_handler`, `stress_sort_data_int32_init`, `stress_sort_data_int32_shuffle`, `stress_sort_data_int32_mangle`, `stress_sort_cmp_fwd_int32`, `stress_sort_cmp_rev_int32`, `stress_sort_compare_get`, `stress_mmap_populate`, `stress_madvise_collapse`, `sigsetjmp`, and `siglongjmp` helpers.

Control flow: the worker resolves `shellsort-size`, maps the integer array, installs a SIGALRM recovery handler when `siglongjmp` is available, initializes the data, synchronizes start, then repeats shuffle/forward-sort, optional verify, reverse-sort, optional verify, mangle, reverse-sort again, optional verify, and bogo increment. It records comparison counts and elapsed time across all sort passes.

State and persistence behavior: state is one private anonymous mapping named `shellsort-data`, sort comparison counters maintained by core sort helpers, and local duration/count totals. The signal jump path restores the old SIGALRM handler and frees the mapping.

Dependencies and integration points: registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SORT | CLASS_HOT`, optional verify, with `shellsort-size` option. It integrates with core sort helpers, mmap/madvise helpers, and stress-ng signal recovery.

Risks and test signals: verify-mode ordering failures indicate comparator or sort corruption. Other signals are mmap failure, handler restoration bugs, interruption during sort, and metric sanity for comparisons/sec and comparisons/item.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shellsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shm-sysv.c -->
# sources/test-tools/stress-ng/stress-shm-sysv.c

Purpose: implements the System V shared memory stressor, creating, attaching, touching, advising, locking, querying, detaching, and removing multiple `shmget` segments per worker while also probing invalid SysV shm API combinations.

Important APIs/types/functions: `stress_shm_sysv`, `stress_shm_sysv_child`, `stress_shm_sysv_get_key`, `stress_shm_sysv_check`, `exercise_shmat`, `exercise_shmctl`, `exercise_shmget`, `stress_shm_metrics`, Linux `stress_shm_get_procinfo` and `stress_shm_sysv_linux_proc_map`, `shmget`, `shmat`, `shmdt`, `shmctl`, `IPC_RMID`, `IPC_STAT`, `SHM_LOCK`, `SHM_UNLOCK`, optional hugepage flags, and NUMA policy shims.

Control flow: the top-level worker computes per-instance byte and segment counts, aligns size to pages, synchronizes start, then repeatedly forks a child and listens on a pipe for allocated shm ids. The child chooses unused keys from a per-instance key range, exercises invalid `shmget` and `shmctl` cases, creates segments with random allowable flags, reports ids to the parent, attaches them, optionally locks memory, touches pages, msyncs/advises, verifies page-pattern contents, queries/sets metadata, optionally probes NUMA and Linux `/proc` map-files, forks a helper to detach/query, then detaches and removes all segments while reporting freed ids. The parent kills/reaps the child, handles OOM/SIGBUS restarts, and removes any segments still reported live.

State and persistence behavior: live SysV segments are kernel-persistent until `IPC_RMID`, so the pipe ledger is critical for cleanup after child death. Child-local arrays track addresses, keys, and ids. Metrics aggregate average nanoseconds per `shmget`, `shmat`, and `shmdt`.

Dependencies and integration points: registered as `CLASS_VM | CLASS_OS | CLASS_IPC`, always verify, with `shm-sysv-bytes`, `shm-sysv-mlock`, and `shm-sysv-segs` options. It uses stress-ng memory-limit/OOM helpers, scheduling helpers, Linux proc hooks, architecture guards, capability-sensitive locking, and System V IPC feature guards.

Risks and test signals: high maximize settings can trigger OOM and leave segments if parent reaping fails. Important signals are leaked shm ids, unexpected `shmget`/`shmat`/`shmdt` failures, memory check failures, bad handling of exhausted keys or ENOSPC, and incorrect skip/error classification for platform-specific commands.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shm-sysv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shm.c -->
# sources/test-tools/stress-ng/stress-shm.c

Purpose: implements the POSIX shared memory `shm` stressor, repeatedly creating named `shm_open` objects, sizing, mapping, touching, syncing, changing metadata, unlinking, and checking page contents.

Important APIs/types/functions: `stress_shm`, `stress_shm_posix_child`, `stress_shm_posix_check`, `stress_shm_msg_t`, `shm_open`, `shm_unlink`, `ftruncate`, `mmap`, `munmap`, `msync`, `fstat`, `fchmod`, `fchown`, `shim_fallocate`, `stress_mincore_touch_pages`, `stress_madvise_randomize`, and OOM adjustment helpers.

Control flow: the worker computes per-instance shared-memory bytes and object count, verifies `/dev/shm` writability on Linux, synchronizes start, and repeatedly forks a child. The child creates object names, opens/truncates/maps each object, reports names to the parent over a pipe, touches and optionally locks pages, forks a small helper to test inherited mappings, exercises fallocate modes, restores size, checks `fstat`, applies permission/ownership changes, verifies page-pattern memory, then unmaps/unlinks and reports freed names. The parent tracks names, kills/reaps the child, treats SIGKILL as possible OOM, restarts as needed, and unlinks any leftover objects.

State and persistence behavior: POSIX shm objects persist by name until `shm_unlink`, so the parent keeps a name ledger for cleanup after OOM or child death. Child state includes arrays of mapped addresses and names. No final durable files should remain.

Dependencies and integration points: registered as `CLASS_VM | CLASS_OS | CLASS_IPC`, always verify, with `shm-bytes`, `shm-mlock`, and `shm-objs` options. It depends on librt/POSIX shm support, stress-ng OOM handling, mmap/mincore/madvise helpers, filesystem access to `/dev/shm`, and global option flags.

Risks and test signals: risks are OOM restarts, `/dev/shm` mount/permission failures, leaked objects, shared-memory mapping behavior differences, and unsupported fallocate modes. Test signals include memory check failures, bad size from `fstat`, failed unlink/reporting, or unbounded restarts.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigabrt.c -->
# sources/test-tools/stress-ng/stress-sigabrt.c

Purpose: implements the `sigabrt` stressor, repeatedly generating child process aborts with and without an installed SIGABRT handler and validating that the expected handler path occurs.

Important APIs/types/functions: `stress_sigabrt_info_t`, `stress_sigabrt_handler`, `stress_sigabrt`, `stress_signal_handler`, `abort`, `shim_raise`, `fork`, `waitpid`, shared anonymous `mmap`, and SIGABRT status inspection.

Control flow: the worker installs a handler, maps shared signal state, synchronizes start, then forks one child per iteration. The child either installs the handler and calls `abort`, or restores the default handler and raises SIGABRT. The parent waits, verifies the child died from SIGABRT, verifies handler state according to the chosen mode, increments bogo ops, and records handler latency.

State and persistence behavior: shared MAP_SHARED state records whether the handler was enabled, whether it ran, start time, count, and latency. It is unmapped on exit and has no persistence beyond the worker.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on signal helper installation, fork/wait handling, stress-ng random selection, and process-shared anonymous memory.

Risks and test signals: failures are child not aborting, wrong signal status, handler not called when expected, handler called when default death was expected, fork pressure, or zero/invalid latency accounting.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigabrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigbus.c -->
# sources/test-tools/stress-ng/stress-sigbus.c

Purpose: implements the `sigbus` stressor, generating recoverable bus faults by accessing a file-backed mapping after truncating its backing file, with optional misaligned access attempts on architectures that may fault.

Important APIs/types/functions: `stress_bushandler`, `stress_sigbus`, `sigsetjmp`, `stress_signal_siglongjmp`, `sigaction`, `SA_SIGINFO`, `posix_fallocate`, `ftruncate`, `mmap`, `munmap`, `SIGBUS`, and fallback SIGSEGV handling.

Control flow: the worker creates and unlinks a temp file, allocates two pages, maps them shared, truncates the file to one page, installs SIGBUS and SIGSEGV handlers, synchronizes start, then repeatedly establishes a jump point. On the non-faulting path it sometimes attempts misaligned writes and always accesses the now-unbacked second page. On the signal-return path it optionally verifies signal number, fault address, and SIGBUS `si_code`, then increments bogo ops.

State and persistence behavior: state is an unlinked temp file, a two-page mapping, and global volatile signal info fields. Cleanup unmaps, closes the fd, and removes the temp directory.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify when `SA_SIGINFO` exists, and unimplemented without `siglongjmp`. It uses stress-ng filesystem helpers, mmap helpers, and platform guards for optional alignment-fault behavior.

Risks and test signals: platforms may deliver SIGSEGV rather than SIGBUS, which is tolerated. Failure signals include missing fault recovery, wrong fault address/code in verify mode, inability to create backing storage, or cleanup after repeated longjmp paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigchld.c -->
# sources/test-tools/stress-ng/stress-sigchld.c

Purpose: implements the `sigchld` stressor, generating and classifying SIGCHLD notifications from children that exit, stop, continue, or are killed.

Important APIs/types/functions: `stress_sigchld_handler`, `stress_sigchld`, `sigaction`, `SA_SIGINFO`, `CLD_EXITED`, `CLD_KILLED`, `CLD_STOPPED`, `CLD_CONTINUED`, `fork`, `kill`, `stress_kill_pid_wait`, and metrics counters.

Control flow: the worker installs a SIGCHLD siginfo handler, synchronizes start, then repeatedly forks a child that exits immediately. The parent sends SIGSTOP and SIGCONT when possible and then kills/waits for the child. The handler increments per-`si_code` counters and the worker sets bogo count from total SIGCHLD deliveries.

State and persistence behavior: all state is process-local volatile counters reset at worker start. Metrics export child-exited/killed/stopped/continued totals.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on signal siginfo semantics, fork/wait/kill helpers, and excludes strict `si_code` verification on OpenBSD.

Risks and test signals: signal coalescing and platform `si_code` behavior can reduce or alter counts. Failure is reported when SIGCHLDs are handled but none have recognized codes on conforming platforms, or when fork/handler installation fails.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigchld.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigfd.c -->
# sources/test-tools/stress-ng/stress-sigfd.c

Purpose: implements the Linux-style `sigfd` stressor, blocking a real-time signal, receiving it through `signalfd`, and verifying signalfd read records while a child queues signals.

Important APIs/types/functions: `stress_sigfd`, optional `shim_signalfd4`, `signalfd`, `sigprocmask`, `sigqueue`, `struct signalfd_siginfo`, `read`, `stress_fs_fdinfo_read`, `stress_affinity_change_cpu`, `stress_kill_pid_wait`, and SIGRTMIN.

Control flow: the parent blocks SIGRTMIN, exercises invalid `signalfd` calls, opens a real signalfd, synchronizes start, forks a child on the same CPU, and the child loops `sigqueue` to the parent with incrementing integer values. The parent reads signalfd records, optionally verifies the signal number, periodically reads `/proc` fdinfo, increments bogo ops, and kills the child on exit.

State and persistence behavior: signal mask changes are process-local; the signalfd is a transient fd closed at exit. Child state is only queued signal value progression.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify, and unimplemented without signalfd/sigqueue support. It integrates with CPU affinity and fdinfo helpers.

Risks and test signals: risks include SIGRTMIN availability, signal queue saturation (`EAGAIN` tolerated in child), incorrect mask setup, short reads, and leaked child/fd state. Verification catches unexpected signal numbers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigfpe.c -->
# sources/test-tools/stress-ng/stress-sigfpe.c

Purpose: implements the `sigfpe` stressor, generating integer division by zero, floating division by zero, and `fenv` exceptions, then recovering via `siglongjmp` and optionally verifying signal metadata.

Important APIs/types/functions: `stress_fpehandler`, `stress_sigfpe`, `stress_int_div_by_zero`, `stress_float_div_by_zero`, `feclearexcept`, `feraiseexcept`, `sigaction`, `sigsetjmp`, `siginfo_t`, `FPE_*`, `FE_*`, and SIGILL fallback handling for undefined division behavior.

Control flow: the worker installs handlers for SIGFPE and SIGILL, synchronizes start, cycles through a static list of exception scenarios, establishes a jump point, and either performs the faulting arithmetic/`feraiseexcept` or handles the signal-return path. In verify mode it compares `si_code` with the expected FPE code for SIGFPE and logs SIGILL variants once.

State and persistence behavior: state is global jump buffer, last signal number, optional copied siginfo, and a static index through the exception table. Floating-point exception flags are cleared after each fault and before exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify. It is disabled for uClibc and selected architectures or when `fenv.h`, `float.h`, or `siglongjmp` support is missing.

Risks and test signals: C arithmetic faults are undefined enough that SIGILL or no trap can occur on some platforms. Test signals are successful recovery and bogo increments, unexpected `si_code` in verify mode, handler install failure, or stale floating-point exception state.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigfpe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sighup.c -->
# sources/test-tools/stress-ng/stress-sighup.c

Purpose: implements the `sighup` stressor, generating SIGHUP through direct raise in a child and through terminal/job-control-like process-group orphan behavior, while measuring handler latency.

Important APIs/types/functions: `stress_sighup_info_t`, `stress_sighup_handler`, `stress_sighup_raise_signal`, `stress_sighup_process_group`, `stress_sighup_closefds`, `stress_sighup`, `fork`, `pipe`, `setpgid`, `kill`, `waitpid`, shared anonymous `mmap`, and SIGHUP handler helpers.

Control flow: the worker installs a SIGHUP handler, maps shared state, synchronizes start, and alternates randomly between two generation modes. Direct mode forks a child that installs the handler and raises SIGHUP. Process-group mode builds a child/grandchild pair with pipes for readiness, moves the grandchild to a process group, stops it, kills the intermediate parent, and waits for kernel SIGHUP delivery before cleanup. Successful iterations increment bogo ops and latency metrics.

State and persistence behavior: process-shared state stores signalled flag, child pid, timestamps, count, and latency. Pipes coordinate readiness and are closed in all local paths.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on fork, process group semantics, SIGSTOP/SIGHUP delivery, and stress-ng kill/wait helpers.

Risks and test signals: process-group SIGHUP behavior is timing-sensitive and OS-dependent. Failures include missing handler invocation, leaked stopped child, pipe coordination failure, wait failure, or latency state not updated.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sighup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigill.c -->
# sources/test-tools/stress-ng/stress-sigill.c

Purpose: implements the `sigill` stressor, executing architecture-specific illegal instructions, recovering via `siglongjmp`, and optionally verifying SIGILL siginfo codes.

Important APIs/types/functions: architecture-specific `stress_illegal_op`, `stress_sigill_handler`, `stress_sigill`, `sigaction`, `sigsetjmp`, `SIGILL`, optional SIGBUS handler registration, `ILL_*` code checks, and `stress_signal_siglongjmp`.

Control flow: compile-time architecture guards define one illegal instruction emitter. The worker synchronizes start, repeatedly establishes a jump point, verifies the prior signal on the return path, increments bogo ops, installs SIGILL and SIGBUS handlers, and calls the illegal-op function to trigger the next signal.

State and persistence behavior: global signal state records the last fault address, signum, code, and jump buffer. There is no persistent filesystem or IPC state.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify with `SA_SIGINFO`, and unimplemented unless the architecture has an illegal-op function plus SIGILL and siglongjmp support.

Risks and test signals: illegal instruction encodings vary by architecture and may produce SIGBUS or nonstandard codes. Test signals are repeated recovery, recognized `ILL_*` codes in verify mode, and correct unimplemented reporting when support is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigio.c -->
# sources/test-tools/stress-ng/stress-sigio.c

Purpose: implements the `sigio` stressor, using asynchronous I/O notification on a pipe to generate SIGIO while a child continuously writes data and the parent drains in the signal handler.

Important APIs/types/functions: `stress_sigio_handler`, `stress_sigio`, `pipe`, `fcntl` with `F_SETOWN`, `F_GETFL`, `F_SETFL`, `O_ASYNC`, `O_NONBLOCK`, optional `F_SETPIPE_SZ`, `read`, `write`, `select`, `stress_affinity_change_cpu`, and OOM/scheduler helpers.

Control flow: the worker maps two 4 KiB buffers, creates a pipe, sets pipe size where possible, sets the read fd owner, forks a writer child, then the parent installs SIGIO and enables async nonblocking reads. The handler increments async signal count and drains the pipe until `EAGAIN`, timeout, or stop. The parent idles with `select` and checks any handler-recorded read error, then disables SIGIO, kills the child, restores fd flags, closes fds, and unmaps buffers.

State and persistence behavior: global volatile state holds the read fd, buffer pointer, async signal count, end time, error, and args pointer. All fd and mmap state is transient and cleaned up at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without the required `fcntl` async flags. It integrates with CPU affinity, scheduler application, OOM adjustment, and stress-ng process state.

Risks and test signals: the handler performs non-async-signal-safe reads and bogo updates intentionally for stress coverage. Risks include missing SIGIO due to fd ownership quirks, EAGAIN/EINTR races, child write failures, and failure to restore file flags.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-signal.c -->
# sources/test-tools/stress-ng/stress-signal.c

Purpose: implements the `signal` stressor, directly exercising the legacy `signal()` API or raw `__NR_signal` syscall by swapping SIGCHLD dispositions and raising SIGCHLD.

Important APIs/types/functions: `stress_signal_count_handler`, `shim_signal`, `stress_signal`, `signal`, optional raw `syscall(__NR_signal)`, `shim_kill`, `SIG_IGN`, `SIG_DFL`, and SIGCHLD.

Control flow: after synchronization, each loop installs SIGCHLD ignore, checks that installation did not spuriously run the counter handler, installs the counter handler, raises SIGCHLD at self, waits for the counter to change, restores default disposition, checks again for spurious delivery, and sets bogo count from the signal counter.

State and persistence behavior: state is a single volatile counter and the process signal disposition for SIGCHLD. No persistent resources are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on syscall availability guards, stress-ng kill/yield wrappers, and standard signal disposition semantics.

Risks and test signals: legacy `signal` semantics vary between BSD/POSIX behavior. Failures include inability to install handlers, counter changes during disposition changes, failure to receive raised SIGCHLD, or incorrect restoration to default.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-signest.c -->
# sources/test-tools/stress-ng/stress-signest.c

Purpose: implements the `signest` stressor, recursively raising many different standard and real-time signals from within a signal handler to stress nested signal delivery and alternative signal-stack depth.

Important APIs/types/functions: `stress_signal_t`, `stress_signest_info_t`, `stress_signest_handler`, `stress_signest_ignore`, `stress_signest_shuffle`, `stress_signest_cmp`, `stress_signest`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `sigsetjmp`, `shim_raise`, `stress_signal_handler`, and `stress_signal_name`.

Control flow: the worker builds a deduplicated signal list from compile-time signals plus real-time signals up to `MAX_SIGNALS`, maps an alternative signal stack, installs handlers for all listed signals, synchronizes start, then repeatedly raises the first signal. The handler records stack depth and max nesting depth, increments bogo ops, marks the current signal handled, raises the next signal, and uses longjmp to escape on timeout or stop. Finish disables handlers, logs unique handled signals and stack-depth estimates, records nanoseconds per handled signal, disables altstack, and unmaps it.

State and persistence behavior: state is global signal arrays, counters for raised/handled signals, current signal index, jump buffer, and volatile `signal_info`. There is no persistent storage.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without siglongjmp. It depends on stress-ng stack helpers, signal-name helpers, sorting helpers, and platform signal availability.

Risks and test signals: nested signal recursion can exhaust or bypass alternative stacks, and not all signals are catchable or equally deliverable. Failure is no handled signals after raises, handler install failure, altstack allocation/setup failure, or runaway nested delivery requiring longjmp escape.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-signest.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigpending.c -->
# sources/test-tools/stress-ng/stress-sigpending.c

Purpose: implements the `sigpending` stressor, verifying blocked SIGUSR1 delivery appears in `sigpending` and disappears after unmasking.

Important APIs/types/functions: `stress_sigpending`, `sigemptyset`, `sigaddset`, `sigprocmask`, `sigpending`, `sigismember`, `shim_kill`, and `stress_signal_ignore_handler`.

Control flow: the worker installs a SIGUSR1 ignore handler, synchronizes start, then each iteration blocks SIGUSR1, sends SIGUSR1 to itself, checks pending membership, unblocks signals, checks SIGUSR1 is no longer pending, exercises invalid and no-op `sigprocmask` calls, and increments bogo ops.

State and persistence behavior: state is the process signal mask and local `sigset_t` values. No external resources persist.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on standard POSIX signal-mask semantics and stress-ng process state helpers.

Risks and test signals: failures indicate incorrect mask setup, signal delivery race, `sigpending` failure, missing pending SIGUSR1, or SIGUSR1 remaining pending after unmask.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigpending.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigpipe.c -->
# sources/test-tools/stress-ng/stress-sigpipe.c

Purpose: implements the `sigpipe` stressor, repeatedly writing to a pipe with the read end closed to generate EPIPE and SIGPIPE.

Important APIs/types/functions: `stress_sigpipe_handler_count_check`, `stress_sigpipe`, `pipe`, `write`, `close`, `stress_signal_handler`, `stress_signal_ignore_handler`, and `stress_bogo_inc`.

Control flow: the worker installs a SIGPIPE handler that increments bogo ops when max-ops is set, otherwise ignores SIGPIPE. It creates a pipe, closes the read end, synchronizes start, loops writing one byte to the write end, counts EPIPE errors, and after stopping verifies that repeated EPIPEs corresponded to at least one handled SIGPIPE.

State and persistence behavior: state is one pipe fd pair and a global args pointer. The write fd is closed at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on stress-ng signal helpers and pipe semantics.

Risks and test signals: if SIGPIPE is ignored or coalesced unexpectedly, bogo count may stay zero despite EPIPE. Failures include pipe creation failure, missing SIGPIPE delivery, or fd cleanup issues.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigpipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigq.c -->
# sources/test-tools/stress-ng/stress-sigq.c

Purpose: implements the `sigq` stressor, sending queued SIGUSR1 signals with payloads to a child that consumes them through `sigwaitinfo` and `sigtimedwait`.

Important APIs/types/functions: `stress_sigqhandler`, `stress_sigq_chld_handler`, optional `shim_rt_sigqueueinfo`, `stress_sigq`, `sigqueue`, `sigwaitinfo`, `sigtimedwait`, `sigprocmask`, `sigaction`, `SA_SIGINFO`, `fork`, and CPU affinity helpers.

Control flow: the parent installs SIGCHLD and SIGUSR1 handlers, synchronizes start, forks a child, and the child blocks SIGUSR1 then alternates between `sigwaitinfo` and `sigtimedwait`, verifying the queued integer payload and signal number. The parent repeatedly sends the configured payload with `sigqueue`, optionally probes Linux `rt_sigqueueinfo` invalid cases, increments bogo ops, sends a zero-valued termination notice, and reaps the child.

State and persistence behavior: state is queued signal payloads and a volatile `handled_sigchld` flag that can stop the run if the child exits. No durable resources are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS | CLASS_IPC`, always verify, and unimplemented without sigqueue/sigwaitinfo/SA_SIGINFO. It integrates with CPU affinity and raw syscall guards on Linux.

Risks and test signals: signal queue saturation, child early exit, payload corruption, and platform-specific realtime signal semantics are key risks. Failures include unexpected payload/signum, fork failure, or child exit with failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigrt.c -->
# sources/test-tools/stress-ng/stress-sigrt.c

Purpose: implements the `sigrt` stressor, spawning one child per real-time signal and measuring queue-to-wait completion latency across the SIGRTMIN..SIGRTMAX range.

Important APIs/types/functions: `stress_sigrt`, `stress_metrics_t`, `stress_sync_init_pids`, `sigqueue`, `sigwaitinfo`, `sigprocmask`, `stress_kill_and_wait_many`, shared `mmap`, and real-time signal bounds.

Control flow: the worker maps a shared metrics array sized by real-time signal count, allocates PID records, ignores all real-time signals in the parent, synchronizes start, then forks one child per real-time signal. Each child waits for all RT signals and records timing in the shared metrics slot indexed by received signal; it exits on a zero payload and can bounce a SIGRTMIN signal when given a pid payload. The parent loops sending each child its matching signal with a timestamp, increments bogo ops, sends termination notices, and reaps all children.

State and persistence behavior: shared anonymous metrics hold duration/count/t_start per RT signal; child processes hold signal masks. All state is unmapped/freed on exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without sigqueue/sigwaitinfo or RT signal bounds. It depends on stress-ng PID synchronization and kill/reap helpers.

Risks and test signals: systems with large RT ranges can spawn many children; signal queue pressure may return EAGAIN/EINTR. Test signals include successful child reaping, nonzero latency metric count, and absence of unexpected `sigqueue` failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigrt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigsegv.c -->
# sources/test-tools/stress-ng/stress-sigsegv.c

Purpose: implements the `sigsegv` stressor, generating recoverable segmentation-related faults from protected mappings, random invalid addresses, guard pages, VDSO bad pointers, and selected x86 privileged or malformed instruction cases.

Important APIs/types/functions: `stress_segvhandler`, `stress_sigsegv`, x86 helpers such as `stress_sigsegv_x86_trap`, `stress_sigsegv_x86_int88`, `stress_sigsegv_rdmsr`, `stress_sigsegv_misaligned128nt`, `stress_sigsegv_readtsc`, `stress_sigsegv_read_io`, optional `stress_sigsegv_vdso`, `mmap`, `madvise(MADV_GUARD_INSTALL)`, `sigaction`, `sigsetjmp`, `prctl(PR_SET_TSC)`, `stress_put_uint8`, and siginfo fields.

Control flow: the worker maps a read-only page and a PROT_NONE page, optionally installs a guard page, synchronizes start, and repeatedly installs SIGSEGV/SIGILL/SIGBUS handlers before setting a jump point. On the non-fault path it randomly chooses one of several fault generators: overlong x86 instruction trap, illegal interrupt, privileged MSR read, misaligned non-temporal store, disabled TSC read, I/O port read, VDSO call with bad pointer, write to read-only memory, read from PROT_NONE, guard-page access, or random masked-address read. On the signal-return path it optionally verifies expected fault address and signal/code before incrementing bogo ops.

State and persistence behavior: state is anonymous mappings plus global signal metadata and address-mask progression used to walk through invalid address widths. TSC reads are re-enabled on exit if disabled. No durable files are created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify with `SA_SIGINFO`, and unimplemented without siglongjmp. It depends heavily on architecture, Linux feature guards, CPU capability helpers, cache flush helpers, and mmap/madvise availability.

Risks and test signals: fault type and `si_addr` fidelity vary widely by architecture and kernel. Real failures are inability to recover from a fault, wrong unexpected signal in verify mode, address mismatch outside tolerated ranges, leaked mappings, or failing to restore PR_SET_TSC state.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigsegv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigsuspend.c -->
# sources/test-tools/stress-ng/stress-sigsuspend.c

Purpose: implements the `sigsuspend` stressor, waking child processes blocked in `sigsuspend` by repeatedly sending SIGUSR1 from the parent.

Important APIs/types/functions: `stress_sigsuspend`, `sigsuspend`, `sigprocmask`, `stress_signal_ignore_handler`, `stress_signal_stop_flag_handler`, `stress_lock_create`, `stress_bogo_inc_lock`, `fork`, `kill`, `waitpid`, and `stress_kill_pid_wait`.

Control flow: the worker installs SIGUSR1 ignore and SIGCHLD stop handlers, creates a shared counter lock, captures the old signal mask, synchronizes start, and forks up to four children. Each child loops in `sigsuspend(&mask)` and exits on unexpected errors or when locked bogo increment says stop. The parent loops over children, sending SIGUSR1 while updating the locked bogo counter, then reaps or kills children and destroys the lock.

State and persistence behavior: state is transient child PIDs, process signal masks, and a stress-ng lock named `counter`. No durable storage is created.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. It depends on stress-ng locking, kill/wait helpers, CPU affinity, and scheduler settings for children.

Risks and test signals: races around child exit versus signal send are expected. Failures include unexpected `sigsuspend` errors in children, fork failure, lock creation failure, premature child death, or bogo counter inconsistencies.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigsuspend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigtrap.c -->
# sources/test-tools/stress-ng/stress-sigtrap.c

Purpose: implements the `sigtrap` stressor, raising SIGTRAP either via `raise` or, on Linux x86, an `int $3` trap instruction, then measuring handler latency.

Important APIs/types/functions: `stress_sigtrap_handler`, `stress_sigtrap`, `shim_raise`, x86 inline `int $3`, `stress_signal_handler`, volatile counter/timestamp/duration state, and metrics export.

Control flow: the worker installs the SIGTRAP handler, synchronizes start, then loops randomly choosing an architecture trap path or `raise(SIGTRAP)`. The handler records elapsed time from the pre-raise timestamp and increments a counter; the worker mirrors that counter into bogo ops and validates that at least one raised trap was handled.

State and persistence behavior: all state is volatile process-local counters and timing variables. No external resources are allocated.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify. If SIGTRAP is not defined, the stressor reports unimplemented through a supported callback.

Risks and test signals: trap-instruction availability is platform-specific. Failures include no handled traps despite raises, handler installation failure, and nonsensical latency metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigtrap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigurg.c -->
# sources/test-tools/stress-ng/stress-sigurg.c

Purpose: implements the `sigurg` network stressor, generating SIGURG from TCP out-of-band data sent by a server and consumed by a client-side SIGURG handler.

Important APIs/types/functions: `stress_sigurg_handler`, `stress_sigurg_client`, `stress_send_error`, `stress_sigurg_server`, `stress_sigurg`, `socket`, `connect`, `bind`, `listen`, `accept`, `send(..., MSG_OOB)`, `recv(..., MSG_OOB)`, `ioctl(SIOCATMARK)`, `fcntl(F_SETOWN)`, `stress_net_reserve_ports`, and `stress_net_sockaddr_if_set`.

Control flow: the worker reserves a per-instance TCP port, installs SIGURG, synchronizes start, then forks a client. The client repeatedly connects to the server, sets itself as socket owner, loops checking the urgent mark and reading normal data while the handler receives out-of-band bytes. The parent server binds/listens, accepts connections, sends one-byte MSG_OOB payloads until stop or send error, then closes sockets, kills/reaps the client, and releases the port.

State and persistence behavior: global state holds args and the current client socket fd used by the SIGURG handler. Network sockets and reserved port state are transient and released at exit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_NETWORK | CLASS_OS`, verify none. It depends on TCP/IP socket support, `SIOCATMARK`, `F_SETOWN`, stress-ng network address helpers, port reservation, and SIGCHLD handling.

Risks and test signals: network behavior is timing-sensitive and can be affected by port conflicts, socket buffer pressure, and platform OOB semantics. Signals include connection retries exceeding limit, unexpected send/recv/ioctl failures, missing bogo increments from handler, or leaked reserved ports.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigurg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigvtalrm.c -->
# sources/test-tools/stress-ng/stress-sigvtalrm.c

Purpose: implements the `sigvtalrm` stressor, arming `ITIMER_VIRTUAL` with a 1 microsecond interval so CPU consumption generates SIGVTALRM signals.

Important APIs/types/functions: `stress_sigvtalrm_set`, `stress_sigvtalrm_handler`, `stress_sigvtalrm`, `setitimer`, `getitimer`, `ITIMER_VIRTUAL`, `SIGVTALRM`, `getrusage`, and bogo counter helpers.

Control flow: the worker installs a SIGVTALRM handler, synchronizes start, arms a virtual interval timer, then loops calling `getitimer` while CPU time advances. The handler increments bogo ops and cancels the timer when the run should stop. At exit the worker optionally verifies that a run with more than one second of user CPU handled at least one SIGVTALRM, then cancels the timer.

State and persistence behavior: state is a process virtual timer and global args pointer. The timer is explicitly zeroed during handler stop and deinit.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without `getitimer`, `setitimer`, `ITIMER_VIRTUAL`, or SIGVTALRM support.

Risks and test signals: timer granularity and implementation differ by OS. Failures include `setitimer` not implemented, no handled signals after sufficient CPU time, or a timer left running after stop.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigvtalrm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigxcpu.c -->
# sources/test-tools/stress-ng/stress-sigxcpu.c

Purpose: implements the `sigxcpu` stressor, repeatedly lowering CPU or realtime runtime limits to provoke SIGXCPU and verify delivery under resource-limit pressure.

Important APIs/types/functions: `stress_sigxcpu_handler`, `stress_sigxcpu_cpu_usage`, `stress_sigxcpu`, `getrlimit`, `setrlimit`, `RLIMIT_CPU`, `RLIMIT_RTTIME`, `SIGXCPU`, `getrusage`, and `shim_sched_yield`.

Control flow: the worker installs a SIGXCPU handler, snapshots CPU and realtime limits, synchronizes start, records initial CPU usage, then loops setting soft limits to zero and yielding. The handler increments bogo ops. On exit it ignores SIGXCPU and, in verify mode, reports failure if more than about 10 seconds of CPU runtime elapsed without any bogo increments.

State and persistence behavior: state is process resource limits and a global args pointer. The code snapshots limits but does not visibly restore them in this file, so the stressor relies on worker process lifetime/isolation for cleanup.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, optional verify, and unimplemented without SIGXCPU plus at least one relevant rlimit. It depends on rusage support for verification when available.

Risks and test signals: manipulating rlimits can affect the running worker and may fail under container policy. There is a likely typo in the `RLIMIT_RTTIME` snapshot path using `getrlimit(RLIMIT_CPU, &limit_rttime)`, which should be reviewed. Test signals are SIGXCPU bogo increments, `setrlimit` failures, and verify-mode no-signal reports.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigxcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigxfsz.c -->
# sources/test-tools/stress-ng/stress-sigxfsz.c

Purpose: implements the `sigxfsz` stressor, repeatedly setting low file-size limits and writing past them to generate EFBIG and SIGXFSZ.

Important APIs/types/functions: `stress_sigxfsz_handler`, `stress_sigxfsz`, `getrlimit`, `setrlimit`, `RLIMIT_FSIZE`, `SIGXFSZ`, `pwrite` or `lseek` plus `write`, temp-file helpers, and metrics export.

Control flow: the worker installs SIGXFSZ handler, reads current file-size limit, creates an unlinked temp file, synchronizes start, then each iteration chooses a random soft file-size limit, sets it, writes four bytes at that limit with `pwrite` or seek/write, increments bogo ops on EFBIG, and shrinks the random maximum if `setrlimit` returns EINVAL. It records SIGXFSZ signals/sec, ignores SIGXFSZ on exit, closes the fd, and removes the temp directory.

State and persistence behavior: state is process `RLIMIT_FSIZE`, an unlinked temp file, and volatile async signal count. The file is not durable after close.

Dependencies and integration points: registered as `CLASS_SIGNAL | CLASS_OS`, always verify, and unimplemented without SIGXFSZ or `RLIMIT_FSIZE`. It uses stress-ng temp filesystem helpers and optional `pwrite`.

Risks and test signals: resource-limit behavior varies under shells/containers. Risks include not restoring the original file-size limit in-process, repeated EINVAL reducing test range too far, missing SIGXFSZ despite EFBIG, or temp fd cleanup errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sigxfsz.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-skiplist.c -->
# sources/test-tools/stress-ng/stress-skiplist.c

Purpose: implements the `skiplist` stressor, building a probabilistic skip list of 32-bit values and verifying all inserted values can be found.

Important APIs/types/functions: `skip_node_t`, `skip_list_t`, `skip_list_random_level`, `skip_node_alloc`, `skip_list_init`, `skip_list_insert`, `skip_list_search`, `skip_list_ln2`, `skip_list_free`, and `stress_skiplist`.

Control flow: the worker resolves `skiplist-size`, computes maximum level as log2(size), synchronizes start, then each iteration initializes a list, inserts `n` Gray-code-like values `(i >> 1) ^ i`, searches for all of them, frees the list, and increments bogo ops. Allocation failures return no-resource, and missing search hits are hard failures.

State and persistence behavior: all state is heap allocated per iteration. The head node is circular at each level, nodes allocate their forward-pointer arrays adjacent to the node object, and `skip_list_free` walks level 1 to release all nodes.

Dependencies and integration points: registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, always verify, with `skiplist-size` option. It depends on stress-ng random generation for levels and global minimize/maximize flags.

Risks and test signals: risks include allocation pressure, off-by-one level handling, duplicate-value behavior, and `size_t` underflow in reverse level loops if invariants are broken. Test signals are successful search of every inserted value and complete freeing without leaks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-skiplist.c -->
