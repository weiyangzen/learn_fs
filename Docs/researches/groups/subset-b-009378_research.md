# subset-b-009378 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prio-inv.c -->
# sources/test-tools/stress-ng/stress-prio-inv.c research

Purpose: implements the `prio-inv` stressor, a scheduler and pthread mutex test that creates three cooperating child processes to exercise priority inversion behavior under selectable scheduler policies and pthread mutex protocols.

Important APIs, types, and functions: the file defines option tables for `prio-inv-policy` and `prio-inv-type`, maps unavailable platform constants to negative sentinels, and exposes `stress_prio_inv_info`. Core state lives in a shared anonymous `stress_prio_inv_info_t` containing child accounting and a process-shared `pthread_mutex_t`. `stress_prio_inv_set_prio_policy()` wraps `sched_setscheduler()` and `setpriority()`, falling back from realtime policies to `SCHED_OTHER` on `EPERM`. `mutex_exercise()` locks/unlocks the shared mutex and increments bogo ops; `cpu_exercise()` samples user CPU time without taking the mutex.

Control flow: `stress_prio_inv()` mmaps shared state, resolves settings, validates unsupported/non-root policies, initializes a robust mutex with the requested protocol and priority ceiling, then forks three children. Child 0 and 2 contend on the mutex while child 1 burns CPU. The parent raises its own priority, waits for stress termination, signals all children with `SIGALRM`, waits for them, destroys pthread state, and compares runtime usage to warn about ineffective priority inheritance.

State and persistence: only transient anonymous shared memory and child processes are used; no files persist. Global `t_end` bounds child loops by the stress timeout.

Dependencies and integration: gated by POSIX priority scheduling, pthread mutex attribute APIs, `sched_*`, `setpriority`, and stress-ng helpers for settings, sync, signals, capabilities, and metrics. Integrated through stressor metadata with `CLASS_OS | CLASS_SCHEDULER` and `VERIFY_ALWAYS`.

Risks: realtime policy requests need privilege, robust/protocol attributes may be ignored or unsupported, and the code returns early in a few setup error paths without sharing the common unmap cleanup. Runtime comparison is heuristic and can be noisy on loaded systems.

Test signals: build-time unimplemented path, option parsing for all policy/type values, non-root fallback messages, child reap behavior, bogo increments, and the priority-inheritance warning are the main observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-prio-inv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-priv-instr.c -->
# sources/test-tools/stress-ng/stress-priv-instr.c research

Purpose: implements `priv-instr`, a CPU stressor that repeatedly executes architecture-specific privileged instructions from user mode and verifies that they trap instead of executing silently.

Important APIs, types, and functions: `op_info_t` names each instruction, stores its function pointer, and records whether it was invalid or trapped. Architecture blocks define inline assembly operations for ARM, Alpha, HPPA, LoongArch, m68k, MIPS, OpenRISC, PPC64, RISC-V, s390, SH4, SPARC, and x86 when supported by configure probes. `stress_sigsegv_handler()` and `stress_sigill_handler()` use `siglongjmp` recovery to advance through the instruction table. x86/PPC paths optionally allocate a page for address-taking privileged instructions such as `invlpg`, `lgdt`, or `tlbie`.

Control flow: `stress_priv_instr()` resets global counters, maps an optional scratch page, installs `SIGSEGV`, `SIGILL`, and `SIGBUS` handlers, clears trap flags, synchronizes with other workers, then enters a `sigsetjmp`-protected loop. Each iteration executes the current privileged op; the signal handler records duration and trap count, marks the op, advances `idx`, and jumps back. On normal termination it reports any instructions that did not trap and records nanoseconds per trap.

State and persistence: all state is process-global and transient: `idx`, timing accumulators, trap flags, and optional anonymous page memory. No persistent files or kernel state should remain.

Dependencies and integration: depends on architecture macros, assembly helper availability, `HAVE_SIGLONGJMP`, stress-ng signal wrappers, anonymous `mmap`, and metrics. It registers as `CLASS_CPU`, `VERIFY_ALWAYS`, or an unimplemented stressor when no supported instruction set exists.

Risks: signal recovery correctness is critical; a privileged instruction that does not trap could hang or alter privileged state on broken emulation. Globals mean only one worker process should manipulate its own private copy. Handler timing includes signal overhead and is not a pure instruction latency metric.

Test signals: successful runs should record at least one trap after more than one bogo op, expose per-op unhandled instruction messages if any instruction fails to trap, and skip cleanly on unsupported architectures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-priv-instr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-procfs.c -->
# sources/test-tools/stress-ng/stress-procfs.c research

Purpose: implements the `procfs` stressor, which aggressively traverses `/proc`, opens entries, performs reads, seeks, ioctls, polls, occasional writes, and special-case proc file exercises.

Important APIs, types, and functions: `stress_ctxt_t` carries worker arguments and writeability; `stress_proc_info_t` maps special proc paths to handlers. `stress_proc_self_mem()` validates `/proc/self/mem` against an anonymous mapping. Optional handlers exercise `/proc/mtrr` and `/proc/bus/pci` ioctls. `stress_proc_rw()` is the core per-file exerciser; `stress_proc_dir()` recursively scans directories; `stress_proc_rw_thread()` runs helper threads against the current shared path protected by a shim spinlock.

Control flow: `stress_procfs()` scans `/proc`, initializes a global `proc_path` and spinlock, starts four pthread reader loops, synchronizes, then iterates shuffled `/proc` entries and random process directories. For regular files and symlinks it publishes the path to helper threads and also calls `stress_proc_rw()` directly. Shutdown clears `proc_path`, cancels/join threads, destroys the spinlock, and frees scandir entries.

State and persistence: global `proc_path`, `mixup`, signal set, and spinlock coordinate transient thread activity. No persistent output is produced; all file operations target kernel virtual procfs entries and temporary buffers.

Dependencies and integration: gated by pthread support plus Linux or Cygwin. It uses `scandir`, `open`, `read`, `lseek`, `mmap`, `ioctl`, `poll`/`ppoll`, namespace ioctls, stress-ng filesystem helpers, capabilities, hashing, and randomization. Metadata classifies it as filesystem and OS.

Risks: `/proc` entries can block, disappear, or have side effects, so the code uses nonblocking opens, timeout thresholds, recursion depth limits, and skips char/block/fifo/socket reads. Concurrent access is intentionally racy and may expose kernel bugs; Cygwin and SH4 exclusions document known hazards.

Test signals: skip when `/proc` is unavailable, bogo increments during traversal, special-path exercise coverage, timeout paths, and absence of hangs or leaked helper threads are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-procfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pseek.c -->
# sources/test-tools/stress-ng/stress-pseek.c research

Purpose: implements `pseek`, a mixed process/thread filesystem stressor that writes and reads deterministic data at fixed or random offsets using both `lseek`+`read/write` and positional `pread/pwrite`.

Important APIs, types, and functions: shared `stress_peekio_info_t` stores the file descriptor, filesystem type, I/O size, randomization flag, and parent PID. `stress_peekio_proc_t` records each child or pthread worker's buffer, I/O mode, process identity, return code, and throughput counters. `data_value()` and `pseek_fill_buf()` generate offset/proc-specific data. `stress_pseek_write_offset()` and `stress_pseek_read_offset()` perform and verify I/O.

Control flow: `stress_pseek()` allocates a shared process table, clamps `pseek-io-size`, maps per-worker buffers, creates and unlinks a temp file, truncates it to the chunked working size, synchronizes, then starts workers 1..N-1 as alternating pthreads and forked children while worker 0 runs inline. Each worker loops write/read/yield over its assigned chunk until stopped or failure signals the parent. Cleanup kills/cancels workers, aggregates rates, closes/unlinks/removes temp storage, and unmaps buffers.

State and persistence: transient temp directory/file is unlinked after open, and anonymous mappings hold process tables and buffers. No persistent data should survive successful cleanup.

Dependencies and integration: uses stress-ng temp-file helpers, mmap, pthreads when available, fork/wait helpers, scheduler yield, metrics, and option handling. It registers as `CLASS_IO | CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`.

Risks: shared file offset mode is deliberately non-atomic and therefore not data-verified on reads; only positional mode verifies. ENOSPC is treated as graceful stop, but partial reads/writes are failures. Mixed process/thread access to a shared descriptor stresses kernel offset locking and filesystem behavior.

Test signals: write/read MB/sec metrics, data mismatch failures in positional mode, ENOSPC early exit, child/pthread return codes, and temp-dir cleanup are key signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pseek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pthread.c -->
# sources/test-tools/stress-ng/stress-pthread.c research

Purpose: implements `pthread`, a scheduler/OS stressor that repeatedly creates large batches of pthreads and exercises thread-related Linux APIs from each thread.

Important APIs, types, and functions: `stress_pthread_info_t` records pthread handle, creation status, index, and timing. Globals include a condition variable, mutex, spinlock, running flags, a thread count, and the static `pthreads[MAX_PTHREAD]` table. Thread bodies call robust-list syscalls, `tgkill`/`tkill`, optional x86 thread-area syscalls, `setns`, signal wait APIs, and `stress_pthread_tid_address()` for `PR_GET_TID_ADDRESS` and `set_tid_address`.

Control flow: `stress_pthread()` blocks `SIGALRM` and polls it through `stress_signal_alrm_pending()`, initializes synchronization primitives, optionally configures a priority-inheritance mutex, then loops creating up to `pthread-max` threads while holding the mutex. Threads start, increment `pthread_count` under a spinlock, wait on the condition variable until the parent broadcasts shutdown, exercise post-wait syscalls, and exit. The parent waits for all started threads or timeout, optionally sends `pthread_sigqueue`, broadcasts, joins, records startup latency, and repeats.

State and persistence: state is process-global and reset per batch; no files persist. Signal masks and global flags are intentionally process-scoped.

Dependencies and integration: requires pthread support and optionally futex robust-list, prctl, modify_ldt/thread-area, setns, and pthread signal queue support. It registers with scheduler and OS classes and `VERIFY_ALWAYS`.

Risks: `MAX_PTHREAD` is large, so resource exhaustion is expected and EAGAIN is accounted as a limited batch rather than a hard failure. The shared `pargs` object is reused during creation; thread code must copy or dereference quickly enough under local conventions. Cleanup depends on broadcast plus joins after stop flags.

Test signals: nanoseconds to start a pthread, percentage of configured pthreads created, robust-list/syscall failure logs, and successful destruction of synchronization primitives indicate coverage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pthread.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ptr-chase.c -->
# sources/test-tools/stress-ng/stress-ptr-chase.c research

Purpose: implements `ptr-chase`, a CPU cache and memory stressor that builds a large randomized graph of pointer pages and repeatedly follows random next pointers.

Important APIs, types, and functions: `stress_ptrs_t` is a 4 KiB node containing an array of pointers; its low pointer bit is reused as a visited marker. `stress_ptr_chase()` owns allocation, graph construction, traversal, verification-like coverage counting, and metrics.

Control flow: the stressor reads `ptr-chase-pages` with maximize/minimize overrides, allocates half the nodes from heap and half from anonymous mmap, builds a pointer index array, then fills every node slot with a random pointer to a different node. After sync, it starts at node zero and repeatedly selects a random slot, marks the pointer's low bit, masks it back to the real address, follows it, and increments bogo ops until stopped. It then scans all nodes to count marked pointers and records percent chased plus nanoseconds per pointer.

State and persistence: all state is transient heap or anonymous mappings. The low-bit marker mutates stored pointers, but the original address is recovered by masking because allocations are aligned.

Dependencies and integration: uses stress-ng mmap population, memory naming, random generators, metrics, and option parsing. It reports memory usage for instance zero and registers under CPU cache, CPU, memory, and search classes.

Risks: the default name says size but option is pages; very large maximize settings can request substantial memory. Correctness relies on pointer alignment leaving bit zero unused. The visited metric is probabilistic, not a full correctness proof.

Test signals: allocation skips, memory usage reporting, percent-pointers-chased metric, nanoseconds-per-pointer metric, and clean heap/mmap release are the observable signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ptr-chase.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ptrace.c -->
# sources/test-tools/stress-ng/stress-ptrace.c research

Purpose: implements `ptrace`, an OS stressor that traces a child process at syscall entry/exit boundaries and periodically exercises invalid ptrace requests.

Important APIs, types, and functions: `stress_syscall_wait()` drives `PTRACE_SYSCALL`, waits for the tracee, and detects syscall stops through `PTRACE_O_TRACESYSGOOD`. `stress_ptrace()` forks the tracee, configures ptrace options, loops tracing syscalls, and kills/reaps the child on exit.

Control flow: after synchronization, the parent forks. The child applies scheduler settings, calls `PTRACE_TRACEME`, stops itself with `SIGSTOP`, then repeatedly issues simple syscalls such as `getppid`, IDs, and `time`. The parent waits for the stop, sets ptrace options, then repeatedly resumes and waits for syscall stops. Every 512 iterations it calls ptrace with an invalid request and an invalid PID to exercise error paths. Termination kills and waits for the tracee.

State and persistence: only transient child process state and kernel tracing state exist. There are no files or persistent settings.

Dependencies and integration: gated by `HAVE_PTRACE`; uses fork/wait/kill stress-ng helpers, `stress_redo_fork`, scheduler application, and standard wait status macros. It is classified as `CLASS_OS` with `VERIFY_ALWAYS`.

Risks: systems with Yama, seccomp, containers, or existing tracers may reject ptrace. The stressor treats `ESRCH`, `EPERM`, and `EACCES` as skip-like traceability failures in several paths. Missing or delayed wait statuses can break tracing, so wait error handling is central.

Test signals: successful bogo increments per syscall stop, skip message when child cannot be traced, invalid ptrace calls not crashing the run, and reliable child cleanup indicate expected behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ptrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pty.c -->
# sources/test-tools/stress-ng/stress-pty.c research

Purpose: implements `pty`, an OS stressor that opens many pseudoterminal master/slave pairs and exercises terminal attributes, line discipline, queue, packet, and path configuration ioctls.

Important APIs, types, and functions: `stress_pty_info_t` stores follower name plus master/follower fds. `stress_pty()` opens `/dev/ptmx`, calls `ptsname`, `grantpt`, `unlockpt`, opens the slave side, performs a large set of `termios`, `termio`, and `ioctl` operations, then closes all pairs.

Control flow: the stressor allocates an array sized by `pty-max`, synchronizes, then loops opening as many PTYs as possible until resource errors or the configured limit. For each valid pair it reads `/proc` fdinfo, gets and sets terminal attributes, drains/flushes/flows the slave, gets and sets window size, line discipline, queue status, PTY lock/number/packet mode, input/output speeds, optional line discipline cycling, and pathconf values. It closes all descriptors each cycle and increments bogo ops.

State and persistence: only file descriptors and transient kernel PTY state are used. Any changed line discipline is restored to the original value before cleanup when that path runs.

Dependencies and integration: gated by `termios.h` and `ptsname`; optional blocks cover `termio.h` and many platform ioctl constants. It uses stress-ng fdinfo helpers and option parsing. It registers as `CLASS_OS`, `VERIFY_ALWAYS`.

Risks: opening up to 65536 PTYs can hit `EMFILE`, `ENOMEM`, `ENOSPC`, or driver limits; these are expected. Some ioctls may return `EINTR` and are tolerated, while other failures are treated as stressor failures. Line discipline cycling is restricted to instance zero and nonblocking mode because it can be disruptive.

Test signals: resource-limit breaks, ioctl failure logs, bogo count per open/exercise/close cycle, and no leaked fd growth are primary signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-pty.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-qsort.c -->
# sources/test-tools/stress-ng/stress-qsort.c research

Purpose: implements `qsort`, a CPU/cache/memory sort stressor that sorts arrays of 32-bit integers with either libc `qsort` or stress-ng's Bentley-McIlroy implementation.

Important APIs, types, and functions: `stress_qsort_method_t` maps method names to `qsort_func_t`; comparators and data initializers come from `core-sort`. `stress_qsort_verify_forward()` and `stress_qsort_verify_reverse()` check ordering when verification is enabled. A `SIGALRM` handler uses `siglongjmp` to escape long sort calls.

Control flow: `stress_qsort()` resolves size and method, mmaps the integer array, installs optional longjmp-based alarm handling, initializes deterministic sort data, synchronizes, then repeatedly shuffles, forward sorts, verifies, reverse sorts, verifies, mangles data, and sorts again. It tracks comparator count, sorted item count, duration, and bogo ops, then emits comparisons/sec and comparisons/item metrics.

State and persistence: array data is anonymous private memory; signal jump state is process-global and restored on exit. No persistent files are used.

Dependencies and integration: requires stress-ng mmap, madvise collapse, signal, sort helpers, target clone support, and optional libc `qsort`. It is `VERIFY_OPTIONAL` and classified as hot CPU/cache/memory/sort work.

Risks: asynchronous longjmp from signal context must restore the previous `SIGALRM` handler, and metrics can be skewed if interrupted. Verification is optional, so default runs mainly measure load unless `--verify` is set. Large arrays can pressure memory and caches.

Test signals: method selection log, optional ordering failures, signal interruption cleanup, comparisons metrics, and successful unmap are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-qsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-quota.c -->
# sources/test-tools/stress-ng/stress-quota.c research

Purpose: implements `quota`, a Linux OS stressor that locates mounted block devices and exercises quota control commands through `quotactl` and optionally `quotactl_fd`.

Important APIs, types, and functions: `stress_dev_info_t` associates mountpoints with `/dev` block device paths and skip state. `quotactl_status_t` accounts error categories. `do_quotactl_call()` randomly chooses `shim_quotactl_fd()` or classic `quotactl()`, disabling fd mode after `ENOSYS`. `do_quotas()` issues available `Q_GETQUOTA`, `Q_GETNEXTQUOTA`, `Q_GETFMT`, `Q_GETINFO`, `Q_GETSTATS`, `Q_SYNC`, and invalid argument probes.

Control flow: `stress_quota_supported()` requires `CAP_SYS_ADMIN`. `stress_quota()` reads mounts, scans `/dev` for block devices whose `st_rdev` matches mount `st_dev`, deduplicates devices, synchronizes, and loops over candidates. Devices that consistently return unsupported, read-only, not-block, or not-enabled statuses are skipped. Complete failure or privilege errors abort; otherwise bogo ops advance per pass.

State and persistence: only transient mount/device tables and duplicated device names are stored. Quota commands are read/sync oriented plus invalid probes; no intended persistent quota changes are made.

Dependencies and integration: Linux-only, requires `sys/quota.h` and at least one quota command macro. Uses stress-ng capabilities and mount helpers. Metadata includes supported callback, `CLASS_OS`, and `VERIFY_ALWAYS`.

Risks: requires elevated capability and real block-device/mount discovery; containers may expose no suitable devices. Error classification determines whether to skip or fail, so filesystem-specific errno behavior matters. `Q_SYNC` can have system-wide effects.

Test signals: capability skip, candidate device discovery, per-device skip transitions, quota error accounting, and bogo increments when devices are exercised.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-quota.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-race-sched.c -->
# sources/test-tools/stress-ng/stress-race-sched.c research

Purpose: implements `race-sched`, a scheduler/OS stressor that forks short-lived children while racing CPU affinity and non-realtime scheduler policy changes across the process tree.

Important APIs, types, and functions: `stress_race_sched_child_t` and `stress_race_sched_list_t` maintain active and recycled child records. Method tables select CPU movement patterns: all, next, previous, random, random increment, syncnext, and syncprev. `stress_race_sched_setaffinity()` wraps `sched_setaffinity` plus verification via `sched_getaffinity`; `stress_race_sched_setscheduler()` randomly chooses normal policies and verifies with `sched_getscheduler`.

Control flow: `stress_race_sched()` runs `stress_race_sched_child()` inside `stress_oomable_child`. The child obtains eligible CPUs, then loops setting its own affinity, forking until a child limit or low-memory condition, and applying random combinations of yield, affinity changes, scheduler changes, and list-wide exercise passes in both parent and children. It reaps old children opportunistically and drains all remaining children on exit.

State and persistence: global process-local child lists and CPU arrays are transient. No files or durable scheduler settings persist after children exit.

Dependencies and integration: gated by `sched_setaffinity`, POSIX/Linux scheduling, normal scheduler policy constants, and `sched_setscheduler`. Uses stress-ng affinity helpers, OOM avoidance, randomization, and oomable wrapper. Classified as scheduler and OS.

Risks: the code intentionally races process lifetime against scheduler operations, so `ESRCH` is tolerated but other errors fail. Child list management must avoid leaks during fork failure and low-memory reaping. CPU index zero is skipped by the `cpu_idx > 0` condition, which may reduce coverage on single-CPU systems.

Test signals: bogo ops per fork/exercise cycle, max fork depth through behavior, affinity/scheduler failure logs, OOM-avoidance reaping, and clean free of child lists/CPU arrays.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-race-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-radixsort.c -->
# sources/test-tools/stress-ng/stress-radixsort.c research

Purpose: implements `radixsort`, a CPU/cache/memory sort stressor for arrays of short random strings, using libc/BSD `radixsort` when available or a local stable counting-radix implementation.

Important APIs, types, and functions: `radixsort_func_t` abstracts the sort signature. `radix_count_sort()` performs a per-digit stable counting pass over 257 buckets. `radixsort_nonlibc()` computes string lengths and sorts from the last character to the first. `stress_radixsort_methods` exposes method selection; a reverse lookup table enables reverse ordering.

Control flow: `stress_radixsort()` selects method and size, allocates one contiguous text slab and a pointer array, installs optional `SIGALRM` longjmp recovery, initializes random fixed-size strings once, synchronizes, then repeatedly sorts forward, optionally verifies ascending order, sorts reverse with `revtable`, optionally verifies descending order, randomizes the first character of every string, and increments bogo ops.

State and persistence: all text and pointer data are heap allocations freed at exit. Signal jump state is process-global but restored. No files persist.

Dependencies and integration: depends on stress-ng random string generation, CPU cache helpers, signal wrappers, and optional BSD/libc radixsort. It is classified as CPU/cache/memory/sort and `VERIFY_OPTIONAL`.

Risks: local implementation uses `unsigned short` lengths, safe for 8-byte strings but not general-purpose long strings. Verification uses `strcmp`, so reverse-table sort must align with lexical expectations. Longjmp interruption must restore handlers and free allocations through the tidy path.

Test signals: method log, optional ordering failure messages, bogo progress, and clean fallback to nonlibc implementation where libc radixsort is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-radixsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ramfs.c -->
# sources/test-tools/stress-ng/stress-ramfs.c research

Purpose: implements `ramfs`, a privileged Linux stressor that repeatedly mounts ram-backed filesystems, exercises basic filesystem operations, optionally fills them, and unmounts with retry/error probes.

Important APIs, types, and functions: `stress_ramfs_supported()` requires `CAP_SYS_ADMIN`. `stress_ramfs_umount()` retries `umount`/`umount2(MNT_FORCE)` and then exercises invalid unmount calls. `stress_ramfs_fs_ops()` creates, stats, optionally fallocates/writes/fsyncs, symlinks, unlinks, mkdirs, and rmdirs inside the mount. `stress_ramfs_child()` performs mount cycles using modern `fsopen`/`fsconfig`/`fsmount`/`move_mount` when available or classic `mount()`.

Control flow: parent `stress_ramfs_mount()` synchronizes and repeatedly forks a child. The child creates a stress-ng temp directory, resolves it, alternates `ramfs` and `tmpfs`, mounts with size options, runs filesystem operations, unmounts, and increments bogo ops until stopped. Parent waits, treats OOM-like `SIGKILL` as restartable, and propagates failure/no-resource statuses.

State and persistence: uses a temporary directory as mountpoint and kernel mount namespace state. Cleanup aggressively unmounts and removes the temp directory; no files should persist.

Dependencies and integration: Linux-only with clone namespace macros and mount APIs; uses stress-ng capabilities, temp-dir helpers, signal handlers, fork retry, and scheduler settings. Classified as OS and `VERIFY_ALWAYS`.

Risks: requires mount privileges and can consume memory, especially with `ramfs-fill` or aggressive mode. Mount cleanup is critical; failures could leave mounts if the process is killed outside the cleanup path. OOM behavior is expected and partially handled.

Test signals: capability skip, mount/no-resource skip, filesystem operation failures, OOM restart debug, bogo count per mount cycle, and absence of leftover mountpoints.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ramfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-randlist.c -->
# sources/test-tools/stress-ng/stress-randlist.c research

Purpose: implements `randlist`, a memory stressor that builds a randomly ordered linked list of variable-sized items and repeatedly writes/verifies each node's data payload.

Important APIs, types, and functions: `stress_randlist_item_t` contains `next`, `dataval`, an allocation-type bit, and flexible payload data. `stress_randlist_free_item()` releases heap or mmap-backed nodes. `stress_randlist_exercise()` walks the list twice: first filling incrementing byte values, then optionally verifying payload integrity.

Control flow: `stress_randlist()` resolves item count, payload size, and compact mode. It allocates a temporary pointer array and either one compact heap block or individual nodes, occasionally using anonymous mmap for large item sizes. It shuffles the pointer array, links nodes in shuffled order, frees the pointer array, synchronizes, and loops exercising the list and incrementing bogo ops until stopped or verification fails.

State and persistence: all state is heap or anonymous mmap memory freed after the run. The list order is randomized per worker and there is no persistent output.

Dependencies and integration: uses stress-ng random generators, mmap population, prefetch builtin, memory-free reporting, and option parsing. It registers as `CLASS_MEMORY` with optional verification.

Risks: maximize options can request enormous item counts and may exhaust memory. Partial allocation cleanup paths must use the correct count and allocation mode. Verification only detects payload corruption after a fill pass; it does not validate list topology beyond successful traversal.

Test signals: allocation skip messages, heap/mmap allocation debug counts, optional data-check failure logs, bogo ops per full traversal, and clean release of compact or per-node allocations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-randlist.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawdev.c -->
# sources/test-tools/stress-ng/stress-rawdev.c research

Purpose: implements `rawdev`, a root-only I/O stressor that opens the raw block device backing the temp path and reads it with direct I/O using several access patterns.

Important APIs, types, and functions: `stress_rawdev_func` abstracts read methods. Method table entries include all, sweep, wiggle, ends, random, and burst. Each method uses `pread()` into an aligned mmap buffer and accumulates byte/duration metrics. `stress_rawdev_all()` rotates through all concrete methods and aggregates metrics.

Control flow: `stress_rawdev()` requires euid root, finds the mount device for the stress temp path, opens it, queries block count and sector size via `BLKGETSIZE` and `BLKSSZGET`, clamps block size, maps an aligned buffer, reopens with `O_DIRECT`, synchronizes, and repeatedly calls the selected access method. On exit it emits per-method MB/sec metrics, unmaps, closes, and frees metrics.

State and persistence: only transient file descriptors, buffer mapping, and metrics are used. Reads are non-mutating, so no persistent device changes are intended.

Dependencies and integration: gated by `sys/sysmacros.h`, block ioctls, and root. Uses stress-ng mount-device lookup, mmap, vmstat/metrics helpers, and option method parsing. Classified as `CLASS_IO`, `VERIFY_ALWAYS`.

Risks: reading raw devices can be disruptive on physical disks due to seek-heavy patterns and needs root. Device discovery may fail in containerized or non-block-backed temp paths. `O_DIRECT` alignment depends on mmap/page sizing and clamped block size.

Test signals: root skip, mount-device discovery skip, ioctl skip, selected method progress, per-method MB/sec metrics, and `pread` failure logs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawpkt.c -->
# sources/test-tools/stress-ng/stress-rawpkt.c research

Purpose: implements `rawpkt`, a Linux network stressor that sends and receives crafted Ethernet/IP/UDP frames over AF_PACKET raw sockets on loopback.

Important APIs, types, and functions: `stress_rawpkt_supported()` requires `CAP_NET_RAW`. `stress_rawpkt_sockopts()` exercises numerous `SOL_PACKET` getsockopt/setsockopt controls. `stress_rawpkt_client()` builds Ethernet, IPv4, and UDP headers and sends frames with `sendto()`. `stress_rawpkt_server()` receives AF_PACKET frames, filters for the expected loopback address/protocol/source port, optionally configures `PACKET_RX_RING` with TPACKET_V3, and records metrics.

Control flow: `stress_rawpkt()` reserves a per-instance port, queries loopback hardware address, IPv4 address, and interface index through `ioctl`, synchronizes, forks a client pinned near the parent CPU, and runs the server in the parent. The server loops receiving packets and increments bogo ops for matching UDP frames; the child loops sending incrementing IP IDs until stress stop. Parent kills/reaps the child at the end.

State and persistence: transient sockets, reserved port bookkeeping, and optional packet ring kernel buffers are used. No files persist.

Dependencies and integration: Linux packet sockets, UDP/IP headers, net ifreq ioctls, raw network capability, stress-ng network port reservation, affinity, signal, and checksum helpers. Classified as network and OS.

Risks: raw sockets require capabilities and may be blocked by container policy. Header fields must be byte-order correct; packet ring sizing requires a power-of-two option. Some sockopt calls intentionally use suspicious constants to exercise error paths and should ignore failures.

Test signals: capability skip, port reservation skip, loopback ioctl failures, receive MB/sec and packet metrics, bogo packet matches, and clean child termination.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawpkt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawsock.c -->
# sources/test-tools/stress-ng/stress-rawsock.c research

Purpose: implements `rawsock`, a Linux raw IPv4 socket stressor that sends self-addressed `IPPROTO_RAW` packets over loopback and verifies payload hashes on receive.

Important APIs, types, and functions: `stress_raw_packet_t` combines an IPv4 header, data counter, and hash. `stress_rawsock_init()` creates a shared stress-ng lock and resets `stop_rawsock`; deinit destroys it. The client waits until all instances mark ready in `g_shared->rawsock.ready`, sends hashed packets, and occasionally exercises `SIOCOUTQ`. The server receives packets, checks hash integrity, uses `SIOCINQ`, and records throughput.

Control flow: `stress_rawsock()` reserves a per-instance port and runs `stress_rawsock_child()` inside `stress_oomable_child`. That child forks a sender and runs the receiver in the parent. The sender applies affinity and scheduler settings, waits for readiness, then sends until stopped. The receiver opens a raw socket, increments shared readiness under lock, receives until stop, validates hashes, records MB/sec, waits for the child, and closes.

State and persistence: shared lock and `g_shared` readiness are runtime-only. Sockets and reserved ports are released on exit; no files persist.

Dependencies and integration: requires Linux `SOCK_RAW`, `IPPROTO_RAW`, `struct iphdr`, `CAP_NET_RAW`, stress-ng locks, OOM wrapper, port reservation, signal handlers, affinity, and hashing. Classified as network and OS.

Risks: global stop and shared readiness are cross-instance coordination points; incorrect lock handling would deadlock startup. Raw sockets may fail under containers. Hash validation catches payload corruption but not all IP header issues. ENOBUFS throttles the client rather than failing.

Test signals: capability skip, lock creation skip, reserved port logs, hash mismatch failures, MB/sec metric, and correct release of port/lock.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawsock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawudp.c -->
# sources/test-tools/stress-ng/stress-rawudp.c research

Purpose: implements `rawudp`, a Linux raw UDP socket stressor that crafts IPv4/UDP packets with `IP_HDRINCL`, sends them to a selected interface address, and verifies the embedded sender PID on receive.

Important APIs, types, and functions: `stress_rawudp_supported()` requires `CAP_NET_RAW`. `stress_rawudp_client()` creates a raw UDP socket per send iteration, sets `IP_HDRINCL`, fills IP and UDP headers plus PID payload, computes the IPv4 checksum, sends, and closes. `stress_rawudp_server()` binds a raw UDP socket, filters received packets by source address, protocol, and source port, verifies PID payload, and emits byte and packet rate metrics.

Control flow: `stress_rawudp()` optionally resolves `rawudp-if`, otherwise uses loopback, reserves a per-instance port, installs signal handling, synchronizes, forks a client pinned near the parent CPU, and runs the server in the parent until stopped. Parent kills/reaps the client and releases the port.

State and persistence: transient sockets and port reservations only; no persistent network configuration changes.

Dependencies and integration: Linux UDP/IP headers, raw socket support, inet helpers, stress-ng interface lookup, port reservation, affinity, checksum, signal, and kill helpers. Registers as network and OS with `VERIFY_ALWAYS`.

Risks: raw socket capability and container policies determine availability. The client opens/closes sockets rapidly, intentionally stressing allocation paths. PID payload verification assumes loopback/self-addressed traffic and may fail if unrelated raw UDP traffic matches filters.

Test signals: capability and port-reservation skips, interface fallback message, bind/socket failures, data-check failure logs, MB/sec and packets/sec metrics, and clean child reap.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rawudp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rdrand.c -->
# sources/test-tools/stress-ng/stress-rdrand.c research

Purpose: implements `rdrand`, a CPU stressor for hardware random-number instructions: x86 `rdrand`/optional `rdseed` and PPC64 `darn`.

Important APIs, types, and functions: architecture blocks define `rand64()` and optional `seed64()` wrappers using stress-ng assembly helpers. `stress_rdrand_supported()` validates CPU feature availability and sets `rdrand_supported`. `RAND64x32` and `SEED64x32` unroll instruction calls. `stress_rdrand_sane()` checks that repeated random reads change and reports unlikely repeats.

Control flow: `stress_rdrand()` resolves `rdrand-seed`, falls back if `rdseed` is unavailable, synchronizes, performs sanity checks, then loops over batches of heavily unrolled random reads. It samples nibbles from selected bit positions into 16 counters and advances bogo by batch count. After termination it emits million-random-bits metrics and checks whether bucket counts deviate more than 5 percent when enough samples exist.

State and persistence: only static per-process counters and support flag are used. There is no persistent state.

Dependencies and integration: depends on architecture detection, CPU feature helpers, assembly instruction wrappers, optional builtin CPU checks on PPC64, and stress-ng metrics/options. It registers supported callback, CPU class, and `VERIFY_ALWAYS`.

Risks: hardware RNG instructions can be unavailable, emulated poorly, or transiently fail in ways hidden by helper semantics. The distribution check is simple and may produce false failures on short or biased samples. `rdseed` is slower and may be less available.

Test signals: unsupported CPU skip, sanity failure for unchanged values, duplicate informational messages, million bits/read rate metrics, and poor-distribution failure logs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rdrand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-readahead.c -->
# sources/test-tools/stress-ng/stress-readahead.c research

Purpose: implements `readahead`, a Linux filesystem cache stressor that creates a deterministic temp file, issues `readahead()` calls over shifting offsets, reads data back, and optionally verifies contents.

Important APIs, types, and functions: offsets are generated by `stress_readahead_generate_offsets()` and perturbed by `stress_readahead_modify_offsets()`. `do_readahead()` calls Linux `readahead()` over the fixed offset set. The main function uses aligned `buffer_t` storage, `pwrite`, `pread`, `ftruncate`, optional `posix_fadvise(DONTNEED)`, and invalid readahead probes.

Control flow: `stress_readahead()` clamps total bytes, divides by instance count, creates a temp directory/file, allocates a 4096-byte aligned buffer, writes deterministic page-sized records, unlinks the file, checks size, synchronizes, then loops calling `readahead`, reading each offset, verifying expected values under `--verify`, dropping cache advice, exercising invalid fd/zero/write-only/large-size calls, and rotating offsets. Cleanup closes fds, frees the buffer, and removes the temp directory.

State and persistence: temp file is unlinked after open and temp directory is removed. Kernel page-cache state is intentionally affected but not persistent file content.

Dependencies and integration: Linux with glibc support, stress-ng temp-file helpers, pragma unrolling, filesystem usage accounting, optional `posix_fadvise`, and metrics through bogo ops. Classified as I/O and OS with optional verification.

Risks: setup can consume large disk space; ENOSPC causes a no-resource skip. Verification only covers successfully read 4 KiB chunks. `readahead()` behavior varies by filesystem and kernel, so invalid probes must ignore expected errors.

Test signals: free-space usage report, ENOSPC skip, readahead/read failure logs, first data-error details under verify, misread debug counts, and temp cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-readahead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-reboot.c -->
# sources/test-tools/stress-ng/stress-reboot.c research

Purpose: implements `reboot`, a Linux OS stressor that exercises invalid and namespace-contained reboot syscall paths without intending to reboot the host.

Important APIs, types, and functions: constants mirror Linux reboot magic values and command codes. `boot_magic` includes valid secondary magic values plus intentionally invalid values. With `clone`, `reboot_clone_func()` runs in a new PID and mount namespace and calls `shim_reboot()` with `POWER_OFF` across magic variants, exiting with `errno`.

Control flow: `stress_reboot()` records whether the process has `CAP_SYS_BOOT`, allocates a clone stack if supported, synchronizes, then loops. It optionally clones a PID namespace child and validates its reboot errno. It then calls `shim_reboot()` with incorrect magic for restart and software suspend, expecting `EINVAL` for capable users or `EPERM`/`EINVAL` for non-capable users. Non-capable runs also iterate all magic values for poweroff and validate permission-style failures. Bogo increments per loop.

State and persistence: only transient child namespaces and stack memory are used. The stressor intentionally avoids valid host reboot calls; no persistent files are touched.

Dependencies and integration: Linux `__NR_reboot`, optional `clone` with `CLONE_NEWPID | CLONE_NEWNS`, stress-ng capability checks, stack alignment, wait helpers, and syscall shim. Classified as OS and `VERIFY_ALWAYS`.

Risks: capability and namespace semantics vary by container; a privileged namespace reboot may have special behavior. The safety contract depends on invalid magic for host-level calls and isolated namespace use for poweroff-like calls. Incorrect errno expectations can create false failures across kernels.

Test signals: no-resource stack allocation skip, namespace child errno failures, permission skip for capable-but-denied cases, invalid-magic errno validation, and bogo increments without host reboot.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-reboot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-regex.c -->
# sources/test-tools/stress-ng/stress-regex.c research

Purpose: implements `regex`, a hot CPU stressor that repeatedly compiles and executes a suite of POSIX extended regular expressions against representative text samples.

Important APIs, types, and functions: `stress_posix_regex_t` pairs regex strings with human descriptions, including deliberately pathological expressions, numeric formats, IP/time/date patterns, and common encodings. `stress_regex_text` holds candidate input strings. `stress_regex_rate()` aggregates per-regex counters and durations. `stress_regex()` owns compile/execute loops and metric publication.

Control flow: the stressor initializes timing/count/failure arrays, synchronizes, then loops through every regex while stress continues. Failed regex compilation is reported once per instance-zero worker and skipped in later passes. Successful compilations update compile timing, then run `regexec` against every sample string and record timing/count for matches. `regfree` releases each compiled regex. If no regex compiles successfully, the loop exits. Final metrics report aggregate `regcomp`/`regexec` rates and per-pattern compile rates.

State and persistence: all state is stack arrays and transient `regex_t` objects freed each pass. There are no persistent side effects.

Dependencies and integration: gated by `<regex.h>` and POSIX regex APIs: `regcomp`, `regerror`, `regexec`, and `regfree`. Uses stress-ng timing, metrics, and bogo helpers. Classified as CPU and hot, with max metric count sized to regex table length plus aggregates.

Risks: pathological patterns can be expensive or implementation-dependent. Because failed compile patterns are skipped after first report, a platform with strict regex semantics may have reduced workload. `regexec` timing only counts successful matches, not failed match attempts.

Test signals: compile failure informational logs, aggregate compile/exec rates, per-regex compile metrics, and bogo increments per regex compile attempt.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-regex.c -->
