# subset-b-009384 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sysinval.c -->
# sources/test-tools/stress-ng/stress-sysinval.c

## Purpose
Implements the `sysinval` stressor, a pathological OS test that drives raw `syscall()` with deliberately invalid argument combinations. It is broader than the pointer-only bad-address stressors: it enumerates many architecture/kernel syscall numbers, assigns semantic argument classes to each argument position, permutes invalid values, and learns which exact syscall/argument tuples crash, time out, or unexpectedly return success so later iterations can avoid repeating them.

## Important APIs, Types, And Functions
The central metadata is `stress_syscall_arg_t`, which stores syscall number, name, arity, and up to six argument bitmasks. Argument classes include pointers, fds, socket fds, directory fds, clock ids, flags, lengths, uid/gid/pid values, futex pointers, filenames, sockaddr pointers, and miscellaneous per-syscall enumerations. `stress_syscall_arg_values_t` maps each class to concrete invalid values through `arg_values[]`.

`stress_syscall_hash_table_t` is a shared hash table with a fixed pool of `stress_syscall_arg_hash_t` entries for crash, timeout, and zero-return tuples. `syscall_current_context_t` is shared parent/child state containing the active syscall, active arguments, counters, crash counts, skip counts, original cwd permissions, and a padded area to reduce accidental clobbering. `stress_syscall_hash()` hashes syscall plus six args, `hash_table_add()` records learned tuples, `syscall_do_call()` arms an interval timer and invokes raw `syscall()`, `syscall_permute()` recursively enumerates argument values, `stress_do_syscall()` forks the contained executor, and `stress_sysinval()` owns setup and cleanup.

## Control Flow
`stress_sysinval()` creates a temporary directory and an unlinked temp file, obtains a bad fd and optional AF_UNIX socket fd, maps shared exercised flags, the hash table, and current context, then maps four two-page regions with `PROT_NONE`, `PROT_WRITE`, `PROT_READ`, and `PROT_READ|PROT_WRITE`. The final page in each mapping is protected or unmapped, and the first page plus last-byte "small" pointers are installed into pointer, sockaddr, futex, and non-null pointer value arrays.

After the sync barrier, `stress_oomable_child()` runs `stress_sysinval_child()`, which repeatedly calls `stress_do_syscall()`. `stress_do_syscall()` forks a short-lived grandchild, marks shared memory read-only, disables stack-smash checks for this hostile workload, drops capabilities, installs fatal signal handlers plus an `ITIMER_REAL` handler, and either walks syscall records in natural or shuffled order. For each record it clears `current_context->args`, skips syscalls that exceeded `MAX_CRASHES`, and invokes `syscall_permute()`. The permutation code selects the value array for the current bitmask, assigns an argument, recurses to the next position, and calls `syscall_do_call()` when all arguments are populated. The parent waits for the grandchild; if the shared context still says `SYSCALL_CRASH`, it records that tuple in the shared hash and increments the per-record crash count.

## State And Persistence Behavior
Persistent state is intentionally limited to anonymous shared memory, open fds, protected mappings, and a temporary directory that is removed at exit. The hash table persists across grandchild crashes within the run, preventing repeated known-crashing or timed-out tuples. Zero-return tuples are cached in the child context and may be lost after a crash, which is acceptable because zero-return caching is only an optimization. The current working directory's mode and ownership are saved and restored after syscalls that may change them.

## Dependencies And Integration Points
The stressor requires `syscall.h`, raw `syscall()`, and excludes Apple and GNU/Hurd. It depends on stress-ng helpers for temp files, bad fds, OOMable children, capability dropping, signal installation, memory naming, scheduler application, parent-death alarms, and process dumpability. Compile-time `__NR_*` or `SYS_*` macros shape the syscall table, so coverage is architecture and libc dependent. It registers as `CLASS_OS | CLASS_PATHOLOGICAL`; there is no explicit verify mode.

## Risks And Test Signals
The main risk is containment failure: an invalid syscall may crash, hang, modify cwd permissions, leak a kernel object, or return success. The design mitigates this with dropped capabilities, fork isolation, signal exits, a 1 ms interval timer, crash hashing, temp-file unlinking, and cleanup of fds/mappings. The table also omits or comments out especially dangerous calls such as exit, reboot, exec, kill, clone, and some mount/kexec paths. Test signals are bogo counter progress from `current_context->counter`, debug percentages of unique syscalls exercised, crash/timeout/zero-return skip counts, absence of leaked children, successful cleanup of temporary directories and mappings, and graceful unimplemented registration on unsupported platforms.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sysinval.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tee.c -->
# sources/test-tools/stress-ng/stress-tee.c

## Purpose
Implements the `tee` stressor, which exercises Linux `tee()` by duplicating data between pipes without consuming the input pipe, then drains the original input through `splice()` into `/dev/null`. It validates basic pipe payload ordering while probing error paths such as invalid flags, self-tee, zero-length tee, pipe breakage, and memory pressure.

## Important APIs, Types, And Functions
`stress_tee_t` is the fixed pipe payload containing a length field and monotonically increasing counter. `stress_tee_spawn()` creates a pipe and forks a helper process around a supplied pipe function. `stress_tee_pipe_write()` continuously writes `stress_tee_t` records into the input pipe. `stress_tee_pipe_read()` reads full records from the output pipe and verifies `length` and `counter`. `exercise_tee()` issues focused `tee()` probes for invalid flags on kernels new enough to validate them, same-fd input/output, and zero length. `stress_tee()` orchestrates the helper processes and throughput metric.

## Control Flow
The main stressor installs a `SIGPIPE` stop handler, opens `/dev/null`, waits at the stress-ng sync barrier, spawns the writer helper for `pipe_in`, and spawns the reader helper for `pipe_out`. The parent closes unused pipe ends and loops while the stressor should continue. Most iterations call `tee(pipe_in[0], pipe_out[1], INT_MAX, 0)` without timing; every thousandth iteration measures duration and bytes for the MB/sec metric. Positive tee lengths are drained from `pipe_in[0]` to `/dev/null` with `splice(..., SPLICE_F_MOVE)` so the writer can continue. Each iteration then calls `exercise_tee()` and increments bogo ops.

## State And Persistence Behavior
All state is transient: two helper children, two pipes, `/dev/null`, and the static payloads in each process. There are no persistent files. Cleanup closes the parent pipe ends and kills/reaps both helpers. The helper writer and reader rely on the global stress continue flag and pipe errors to exit.

## Dependencies And Integration Points
The implemented path requires `tee()` and `SPLICE_F_NONBLOCK`; otherwise `stress_unimplemented` is exported. It uses stress-ng fork retry, kill/wait, scheduler, parent-death alarm, signal, metrics, and proc-state helpers. The stressor is classified as `CLASS_PIPE_IO | CLASS_OS | CLASS_SCHEDULER` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Pipe reads can return partial records, so the reader accumulates bytes until a full `stress_tee_t` is available. `EPIPE`, `EAGAIN`, and `EINTR` are expected in pipe-heavy shutdown paths, while other read/write/splice failures are reported. Kernel flag validation differs before Linux 4.10, so invalid-flag checking is version gated. Test signals include sustained bogo progress, verified reader counters, the "MB per sec tee rate" metric, correct handling of helper termination, and unimplemented registration when `tee()` is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tee.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-time-warp.c -->
# sources/test-tools/stress-ng/stress-time-warp.c

## Purpose
Implements the `time-warp` stressor, which repeatedly samples all available clock/time sources and detects clocks moving backwards or wrapping below their initial value. It distinguishes monotonic clocks, where any backward step is a verification failure, from wall-clock or CPU-time sources where backward movement is counted but only final wraparound below the starting point fails.

## Important APIs, Types, And Functions
`stress_time_warp_info_t` describes each source: getter function, clock id, name, and monotonic flag. `stress_time_t` stores initial and previous timestamps plus warp and failure counters. Wrapper getters adapt `gettimeofday()`, `time()`, and `getrusage()` to a `clock_gettime`-like signature. The `clocks[]` table conditionally includes `CLOCK_REALTIME`, coarse realtime, monotonic variants, boottime, CPU clocks, TAI, auxiliary clocks, plus libc time APIs. `stress_time_warp_timespec_fix()` normalizes nanoseconds, and `stress_time_warp_lt()` compares two `timespec` values.

## Control Flow
After synchronization, the stressor samples every configured clock into `ts_init` and `ts_prev`, marking a source failed only for unexpected errors other than unsupported-clock style errno values. The main loop reads every non-failed source, increments that source's `warped` count if the new value is less than the previous value, updates `ts_prev`, and increments bogo ops. On exit it checks that each final `ts_prev` is not below `ts_init`, then checks that all monotonic sources had zero backward steps.

## State And Persistence Behavior
All state lives in a stack array for the worker invocation. No files, timers, or persistent system state are created. The stressor is read-only against kernel timekeeping APIs.

## Dependencies And Integration Points
The implemented path needs at least one of `clock_gettime` with librt, `gettimeofday`, `time`, or `getrusage`. It uses stress-ng clock shims, synchronization, proc-state, and bogo helpers. Metadata registers `CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds export an unimplemented reason.

## Risks And Test Signals
Realtime clocks can legitimately move backwards because of administrator or NTP changes, so monotonic status is encoded per clock. `getrusage()` is represented as combined process CPU time and may not advance while idle. The comparison function normalizes out-of-range nanoseconds before testing, reducing false positives from wrapper calculations. Test signals are failure logs naming the specific clock, bogo progress from repeated reads, wraparound/warp counts at failure, and clean skip of clocks returning `EINVAL`, `ENOSYS`, or `ENODEV`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-time-warp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timer.c -->
# sources/test-tools/stress-ng/stress-timer.c

## Purpose
Implements the `timer` stressor, a POSIX timer signal workload that creates a `CLOCK_REALTIME` timer, drives it at a configured frequency, optionally randomizes the interval, counts timer signal bogo events, and verifies timer API behavior around overruns and settime failures.

## Important APIs, Types, And Functions
Global state includes `s_args`, `timerid`, `timer_settime_failure`, `timer_overruns`, `rate_ns`, `time_end`, and `timer_rand`. Options are `timer-freq` and `timer-rand`. `stress_timer_set()` converts the selected frequency into a nonzero `itimerspec`, adding +/-12.5 percent jitter when random mode is enabled. `stress_proc_self_timer_read()` exercises Linux `/proc/self/timers`. `stress_timer_handler()` is the `SIGRTMIN` handler that increments bogo ops, samples overruns with `timer_getoverrun()`, periodically checks timeout and `/proc/self/timers`, and cancels the timer on shutdown.

## Control Flow
`stress_timer()` masks `SIGINT`, resolves frequency with maximize/minimize handling, installs the realtime signal handler, creates a POSIX timer, synchronizes, starts the timer, and then sleeps in 10 ms chunks. Every 1024 parent loop iterations it deliberately calls `nanosleep()` with invalid timespec values and, in random mode, stops and re-arms the timer with a newly randomized interval. When the global continue flag clears, it disarms and deletes the timer, reports overruns in debug output, fails if any settime call failed, and on Linux reissues `timer_delete()` against the already deleted id to exercise that error path.

## State And Persistence Behavior
State is process-global because signal handlers need fast access to the active args and timer id. The only kernel object is a POSIX timer, deleted before exit. No files are created; `/proc/self/timers` is read opportunistically on Linux.

## Dependencies And Integration Points
The implemented path requires librt and `timer_create`, `timer_delete`, `timer_getoverrun`, and `timer_settime`. It integrates with stress-ng option parsing, signal wrappers, proc-state, bogo accounting, timing helpers, and metrics. It registers as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Very high configured frequencies can produce overruns, signal pressure, or resource failures; `EAGAIN`, `ENOMEM`, and `ENOTSUP` during creation become no-resource skips. Handler work is intentionally small but still calls timer APIs and stress-ng accounting, so signal-safety and errno restoration matter. Test signals include bogo events, overrun debug counts, absence of `timer_settime_failure`, graceful resource skips, and correct handling of `timer-rand` re-arming.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timerfd.c -->
# sources/test-tools/stress-ng/stress-timerfd.c

## Purpose
Implements the `timerfd` stressor, which opens many Linux timerfd file descriptors, arms them at a configured rate, waits for expirations through `poll()` or `select()`, reads expiration counters, and probes invalid timerfd operations.

## Important APIs, Types, And Functions
Options include `timerfd-fds`, `timerfd-freq`, and `timerfd-rand`. `stress_timerfd_clockids[]` selects from realtime, monotonic, and boottime clocks where available. `stress_timerfd_set()` builds a nonzero interval with optional jitter. The main `stress_timerfd()` function owns allocation of timerfd arrays, optional `pollfd` arrays, temporary non-timer file fd, timer creation, arming, readiness waiting, invalid syscall probes, fdinfo reads, and cleanup.

## Control Flow
The stressor resolves settings, computes `rate_ns`, creates a temporary directory and unlinked regular file for bad-fd timerfd probes, allocates fd arrays, and creates up to the configured number of timerfds. Non-realtime clock creation falls back to realtime if unsupported. It optionally probes `CLOCK_REALTIME_ALARM` without `CAP_WAKE_ALARM`, waits at the barrier, exercises `timerfd_create()` with invalid flags, and arms every valid timerfd. During the run it either builds an `fd_set` and calls `select()` or builds a compact `pollfd` array and calls `poll()`. Readable timerfds are read for their 64-bit expiration count, optionally queried with `timerfd_gettime()`, optionally re-armed in random mode, and counted as bogo ops.

## State And Persistence Behavior
Runtime state is limited to timerfd descriptors, one regular file descriptor, heap arrays, and a temporary directory. The temp file is unlinked immediately. All valid descriptors are closed and the directory is removed on exit. Timer intervals are kernel fd state only.

## Dependencies And Integration Points
The implemented path requires `sys/timerfd.h`, timerfd create/gettime/settime, and either `poll()` or `select()`. It uses stress-ng capability checks, bad fd generation, fdinfo reads, temp-file helpers, settings, metrics through bogo ops, and proc-state transitions. Metadata is `CLASS_INTERRUPT | CLASS_OS` and `VERIFY_ALWAYS`.

## Risks And Test Signals
Large fd counts can hit `EMFILE`, `ENFILE`, `ENOMEM`, or `FD_SETSIZE` limits. In `select` mode the code avoids fds beyond `FD_SETSIZE`; in `poll` mode it can scale higher but allocates more memory. Invalid gettime/settime calls against a bad fd and regular file fd are deliberately ignored. Test signals are successful creation of at least one timerfd, bogo increments from readable events, fdinfo exercise every `COUNT_MAX` loops, clean closure of all fds, and unimplemented registration when timerfd support is missing.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timerfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timermix.c -->
# sources/test-tools/stress-ng/stress-timermix.c

## Purpose
Implements the `timermix` stressor, a mixed timer signal workload that combines POSIX timers across available clock ids with interval timers (`setitimer`) where supported. It measures per-timer tick rates while forcing signal delivery through multiple timer mechanisms.

## Important APIs, Types, And Functions
`stress_timer_info_t` records POSIX timer clock id, name, timer id, and signal count. `stress_itimer_info_t` records `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF` ids, signal numbers, names, and counts. `stress_timermix_timer_set()` and `stress_timermix_itimer_set()` create nonzero periodic timers from default rates. `stress_timermix_timer_action()` handles `SIGRTMIN` POSIX timer signals, accounts the specific timer through `siginfo`, increments bogo ops, and adaptively throttles POSIX timer frequency. `stress_timermix_itimer_action()` handles interval timer signals and counts by signal number.

## Control Flow
At startup, the stressor installs `SA_SIGINFO` handlers, creates POSIX timers for every supported clock in `timer_info[]`, and installs handlers for each itimer signal. If no timer path is available it skips. After synchronization, it arms all created POSIX timers and all supported itimers, then the main thread repeatedly nanosleeps for 100 us and yields until stopped. Signal handlers drive almost all bogo activity. On exit or error, `stop_timers` disarms POSIX timers, deletes them, emits per-clock tick/sec metrics, disarms itimers, emits per-itimer tick/sec metrics, and sets deinit state.

## State And Persistence Behavior
State is process-global because asynchronous signal handlers update timer arrays and global rates. Kernel timer objects are deleted, and itimers are zeroed before exit. No files are created. Counts persist only until metrics are emitted.

## Dependencies And Integration Points
The file conditionally enables POSIX timers with librt timer APIs and `SA_SIGINFO`, and interval timers with `getitimer`/`setitimer` and `SA_SIGINFO`. It uses stress-ng timing, bogo accounting, proc-state, metrics, and scheduler yield helpers. It registers as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS`, `VERIFY_ALWAYS`, and exposes maximum metric items equal to enabled timer plus itimer counts.

## Risks And Test Signals
Signal load can overwhelm a system, so POSIX timer frequency is adaptively increased or decreased based on whether handler checks happen within a one-second window. Some clocks may reject timer creation and are skipped individually. Cygwin-specific `EINVAL` from unsupported virtual/prof itimers is tolerated. Test signals include per-clock and per-itimer tick/sec metrics, bogo progress from signal handlers, clean timer deletion, and no-resource skip when no timers can be created.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-timermix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tlb-numa.c -->
# sources/test-tools/stress-ng/stress-tlb-numa.c

## Purpose
Implements the `tlb-numa` stressor, a memory/TLB workload that combines CPU affinity changes, NUMA `mbind()` calls, pageout advice, shared mappings, and pthreads to provoke TLB shootdowns and inter-processor interrupts on NUMA-capable systems.

## Important APIs, Types, And Functions
`stress_tlb_numa_t` holds page size, mapping size, page pointer arrays, bogo lock, args, CPU count, NUMA masks, NUMA node mask, and option flags for disabling mbind or pageout. `stress_tlb_numa_shuffle_pages()` randomizes page traversal order. `stress_tlb_numa_change_cpu()` changes process/thread affinity to a random configured CPU and yields. `stress_tlb_numa_mmap()` wraps retrying `mmap()` and disables huge pages. `stress_tlb_numa_mbind()` optionally binds selected pages to a NUMA node. Three pthread bodies perform cross-page mbind/pageout, temporary mmap/pageout/munmap, and fragmented unmapping patterns.

## Control Flow
The entry point resolves `tlb-numa-entries`, optionally using detected x86 DTLB entries, scales entries per stressor instance, allocates two page pointer arrays and several NUMA masks, then maps two shared anonymous regions sized at two pages per TLB entry. It fills pages with non-identical data, unmaps every odd page, stores even-page addresses, shuffles both arrays, reports memory use, and starts three pthread workers. After sync it records starting TLB shootdown/IPI counters and loops mapping two temporary pages, touching them, changing CPU, optionally binding them to the next NUMA node, optionally pageout-advising them, and unmapping. After stop it records end counters, emits TLB shootdowns/sec and IPIs/sec when positive, cancels pthreads, unmaps fragmented pages, destroys the lock, and frees NUMA masks and arrays.

## State And Persistence Behavior
State is transient heap data, shared anonymous mappings, pthreads, NUMA masks, CPU affinity, and the bogo lock. No files persist. CPU affinity changes are per process/thread and end when the worker exits. NUMA page policy applies only to the temporary mappings.

## Dependencies And Integration Points
The implemented path requires `sched_setaffinity`, pthreads, and `__NR_mbind`; it includes NUMA, affinity, CPU cache, interrupt, mmap, OOM, and pthread helpers. Options are `tlb-numa-entries`, `tlb-numa-nombind`, and `tlb-numa-nopageout`. It registers as `CLASS_TLB | CLASS_MEMORY` with `VERIFY_NONE`.

## Risks And Test Signals
Systems without usable NUMA masks or mbind support skip. Thread cancellation happens without joining, which is acceptable for process teardown but means cleanup relies on cancellation points or process exit. High entry counts can allocate large shared mappings and pointer arrays. Test signals are memory usage reporting, positive TLB shootdown/IPI metrics on capable kernels, bogo progress via the shared lock, and clean no-resource skips for allocation or NUMA discovery failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tlb-numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tlb-shootdown.c -->
# sources/test-tools/stress-ng/stress-tlb-shootdown.c

## Purpose
Implements the `tlb-shootdown` stressor, a multi-process memory workload that repeatedly changes page protections, reads and writes shared mappings, calls `madvise()`/`msync()`, and rotates CPU affinity to force TLB shootdowns and IPIs.

## Important APIs, Types, And Functions
`stress_tlb_shootdown_read_mem()` and `stress_tlb_shootdown_write_mem()` read or write every cache line in selected pages, with writes followed by cache flushes. `stress_tlb_shootdown_mmap()` retries shared mapping allocation. `stress_tlb_shootdown_child()` is the worker process loop that alternates `mprotect()` states, whole-mapping reads/writes with a prime-derived stride, optional `MADV_DONTNEED` on anonymous and file-backed pages, and periodic CPU affinity changes. `stress_tlb_shootdown()` sets up shared mappings, forks workers, coordinates start, runs parent-side page invalidation, records interrupt counters, and cleans up.

## Control Flow
The stressor obtains eligible CPUs, maps shared PID synchronization slots, optionally creates an unlinked temporary file for a small shared file-backed mapping, and maps a 512-page shared anonymous region. It chooses between two and eight child processes based on CPU count, initializes per-child sync state, then forks children. Children apply scheduler settings, mark themselves OOM-killable, wait for release, pin to CPUs, and repeatedly mprotect/read/write/advice both shared regions. The parent waits at the global barrier, releases child sync, and loops issuing optional `MADV_DONTNEED`, synchronous `msync()`, Linux debugfs TLB flush ceiling read/write, and hugepage collapse/nohugepage advice. On termination it records TLB and IPI deltas, emits metrics, kills and reaps children, unmaps memory, removes temp storage, unmaps PID sync state, and frees CPU arrays.

## State And Persistence Behavior
Runtime state is shared anonymous memory, optional unlinked file-backed memory, child processes, temporary directory, and affinity state. The optional debugfs read/write targets `/sys/kernel/debug/x86/tlb_single_page_flush_ceiling` by writing back the same content, so it should not intentionally change the value. Temp files are unlinked and directories removed.

## Dependencies And Integration Points
The implemented path requires `sched_getaffinity` and `mprotect`. Optional blocks use `madvise`, `MADV_DONTNEED`, `MADV_COLLAPSE`, `MADV_NOHUGEPAGE`, file-backed mmap, and Linux debugfs. It uses stress-ng affinity, interrupts, sync-pid, temp-file, kill/wait, prime, cache, and memory usage helpers. It registers as `CLASS_TLB | CLASS_MEMORY` with `VERIFY_NONE`.

## Risks And Test Signals
The workload intentionally races permission changes and memory accesses across processes, so kernel and architecture behavior can vary. Debugfs may be absent or permission restricted and is ignored. Child fork failures reduce worker count rather than aborting. Test signals include positive TLB shootdowns/sec and IPIs/sec metrics, bogo progress in parent and children, clean child reap, and no leaked temp directory or mappings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tlb-shootdown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tmpfs.c -->
# sources/test-tools/stress-ng/stress-tmpfs.c

## Purpose
Implements the `tmpfs` stressor, which finds a writable tmpfs mount, creates an unlinked sparse file sized from available tmpfs space, and repeatedly maps, touches, syncs, unmaps, and remaps its pages to stress tmpfs-backed VM behavior.

## Important APIs, Types, And Functions
`mapping_info_t` stores per-page address and mapping state. `stress_tmpfs_context_t` passes file descriptor and size to the OOMable child. `stress_tmpfs_open()` scans mounts with `stress_mount_get()`, filters to tmpfs using `statfs()` and `TMPFS_MAGIC`, avoids sensitive mount prefixes, creates an unlinked temp file, and extends it to a page-aligned capped size. `stress_tmpfs_child()` performs the mmap/madvise/mincore/msync/xattr/unmap/remap workload. `stress_tmpfs()` opens the tmpfs file and runs the child under `stress_oomable_child()`.

## Control Flow
The child allocates a `mapping_info_t` array for every page in the tmpfs file, resolves `tmpfs-mmap-async` and `tmpfs-mmap-file`, and loops while running. Each iteration does random file reads/writes, optional xattr set/remove probes, `fsync()`, and a full-file shared mmap with optional random mmap flags such as hugepage, nonblock, or locked mappings. It may disable problematic populate/hugetlb flags after mmap failures. Once mapped, it optionally writes and `msync()`s the whole file, randomizes advice, touches pages with mincore helpers, writes verification data, optionally verifies it, then unmaps all pages in random order. If `MAP_FIXED` is available, it maps individual pages back in random order at original addresses, touches/advises/verifies them, optionally writes/syncs file-backed data, and finally unmaps all mapped pages.

## State And Persistence Behavior
The temp file is unlinked immediately and closed in both child and parent paths, so tmpfs space should be reclaimed even if the child exits early. Runtime state is the fd, per-page heap array, mappings, and xattrs that are removed if successfully created. No named file should persist.

## Dependencies And Integration Points
The stressor requires `sys/vfs.h` and `statfs()`. It uses stress-ng mount discovery, mmap, madvise, mincore, OOMable child, temp-file, memory, and optional xattr helpers. Options are `tmpfs-mmap-async` and `tmpfs-mmap-file`; verification is optional. It registers as `CLASS_MEMORY | CLASS_VM | CLASS_OS`.

## Risks And Test Signals
Tmpfs capacity can change under load; mmap failures are retried up to `NO_MEM_RETRIES_MAX`, and excessive failures stop the loop. `MAP_FIXED` remapping may fail and is tracked per page. Optional verification catches data pattern mismatches after mmap writes. Test signals include skip when no writable tmpfs is found, bogo increments per map/unmap cycle, optional verification failures, no persistent temp files, and successful cleanup after OOMable child exit.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tmpfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-touch.c -->
# sources/test-tools/stress-ng/stress-touch.c

## Purpose
Implements the `touch` stressor, which creates and removes many temporary regular files from multiple cooperating processes using either `open(O_CREAT)` or `creat()`. It stresses filesystem metadata operations, open flag handling, temp directory cleanup, and shared bogo counter locking.

## Important APIs, Types, And Functions
`touch_opts_t` maps option tokens to open flags such as direct, dsync, excl, noatime, sync, and trunc when available. `touch_method_t` maps `random`, `open`, and `creat` methods. `stress_touch_opts()` parses comma-separated `touch-opts` through a callback. `stress_touch_dir_clean()` removes leftover regular files from the stress temp directory. `stress_touch_loop()` creates a unique filename from the locked bogo counter, performs the selected file creation method, tolerates or reports selected errno values, closes the fd, and unlinks the file. `stress_touch()` creates children and coordinates start/stop.

## Control Flow
The stressor maps synchronization PID state for four child processes, creates a stress-ng lock named `counter`, resolves options, creates the temp directory, and forks four children. Children wait on per-pid sync, mark run state, enable failure injection, and run `stress_touch_loop()`. The parent waits at the global barrier, releases child sync, enters its own touch loop, then clears the continue flag. Cleanup kills/reaps children, scans and unlinks leftover regular files, removes the temp directory, destroys the lock, and unmaps PID sync state.

## State And Persistence Behavior
State includes a process-shared lock, child PIDs, a temporary directory, and transient files named from monotonically increasing bogo counters. Files are unlinked immediately after close and the directory cleaner catches leftovers after child termination. No intended files persist.

## Dependencies And Integration Points
The file uses stress-ng temp-file naming, process sync, locks, kill/wait, options, random selection, and proc-state helpers. It registers as `CLASS_FILESYSTEM | CLASS_OS`, `VERIFY_ALWAYS`, with `touch-method` and `touch-opts` settings.

## Risks And Test Signals
Some open flag combinations are expected to be unsupported on particular filesystems, especially `O_DIRECT`, `O_NOATIME`, and `O_EXCL` with collisions; selected errno values are logged as failures in the current implementation while other errors are silently ignored. The `creat` method ignores `touch-opts`, and instance zero logs that note. Test signals include bogo counter progress, temp directory cleanup, no leaked child processes, option parser rejection of unknown tokens, and behavior across open/creat/random methods.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-touch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tree.c -->
# sources/test-tools/stress-ng/stress-tree.c

## Purpose
Implements the `tree` stressor, a CPU/cache/memory/search workload that builds, searches, and tears down several tree structures over randomized 32-bit values. It covers local binary, AVL, B-tree, and treap implementations, plus BSD red-black and splay trees when available.

## Important APIs, Types, And Functions
`stress_tree_metrics_t` accumulates insert, find, remove durations and node counts per method. `stress_tree_method_info_t` maps method names to functions. Node types include `binary_t`, `avl_t`, `btree_t` plus `btree_value_t`, optional `rb_t`, optional `splay_t`, and `treap_t`, all covered by `union tree_node` for a shared allocation. `stress_rndu32()` is a fast deterministic generator for repeatable insert data. Method functions such as `stress_tree_binary()`, `stress_tree_avl()`, `stress_tree_btree()`, `stress_tree_treap()`, `stress_tree_rb()`, and `stress_tree_splay()` implement insert/find/remove cycles. `stress_tree_all()` runs every method except the `all` dispatcher.

## Control Flow
The entry point catches illegal instructions, resets metrics, resolves `tree-method` and `tree-size`, allocates a node array sized as `union tree_node`, and optionally installs a `SIGALRM` longjmp handler to escape long tree operations at timeout. After synchronization it repeatedly invokes the selected method while `rc` remains success and the stressor continues. Each method initializes nodes with the same random sequence, measures insertion, performs a mandatory forward find pass, optionally performs reverse and random find passes under verify mode, removes or resets the tree, updates metrics, and returns. On exit the stressor restores the alarm handler, emits per-method operations/sec metrics, computes a debug geometric mean across methods with data, frees nodes, and returns status.

## State And Persistence Behavior
All data is transient heap memory except B-tree internal nodes, which are allocated and freed per B-tree cycle. Optional BSD tree roots and metrics arrays are static process-local state. No files or kernel objects persist.

## Dependencies And Integration Points
Optional RB and splay support depends on `sys/tree.h` or `bsd/sys/tree.h`. The file uses stress-ng option parsing, target clone annotations, signal wrappers, timing, metrics, and sync helpers. It registers as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH` with `VERIFY_OPTIONAL`.

## Risks And Test Signals
Large `tree-size` values can allocate substantial memory and produce long operations, making the SIGALRM longjmp path important. Duplicate random values may reduce inserted node counts in some structures, but find checks search the original values according to each implementation's semantics. AVL balance-factor updates are subtle and covered by mandatory find checks. Test signals are method-specific metrics, optional verify failures naming the missing node, no B-tree allocation leaks, successful alarm interruption cleanup, and no-resource skip on node allocation failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tree.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-trig.c -->
# sources/test-tools/stress-ng/stress-trig.c

## Purpose
Implements the `trig` stressor, a floating-point compute workload that repeatedly evaluates trigonometric functions over deterministic ranges and verifies checksums against expected sums.

## Important APIs, Types, And Functions
`stress_trig_method_t` maps method names to function pointers. Individual methods cover double, float, and long-double `cos`, `sin`, and `tan`, plus `sincos` variants when available. Each method loops `STRESS_TRIG_LOOPS` times, accumulates a sum, increments bogo ops, and returns whether the checksum exceeds precision tolerance. `stress_trig_exercise()` times one method call, updates `stress_trig_metrics`, and logs checksum failure for non-`all` methods. `stress_trig_all()` invokes every concrete method.

## Control Flow
`stress_trig()` resolves `trig-method`, zeros metrics, synchronizes, and repeatedly exercises the selected method until stop or checksum failure. The `all` method calls all configured concrete functions in sequence. On exit it emits per-method operations/sec metrics based on loop count, call count, and accumulated duration.

## State And Persistence Behavior
State is limited to static per-method metric counters and stack-local floating point accumulators. There are no files or persistent system resources.

## Dependencies And Integration Points
The file depends on math functions through stress-ng shim wrappers, target clone annotations, put/metric helpers, and method option parsing. Optional `sincos`, `sincosf`, and `sincosl` support is compile-time gated. It registers as `CLASS_CPU | CLASS_FP | CLASS_COMPUTE` with `VERIFY_ALWAYS`.

## Risks And Test Signals
Checksum tolerances differ by precision and long-double representation, but libm, compiler, architecture, and optimization differences can still affect sums. Tangent uses a range near pi with a precomputed expected sum, so it is more sensitive than sine/cosine zero-sum checks. Test signals include checksum failure logs naming the method, bogo progress, method metrics, option enumeration for only compiled-in methods, and successful operation across float/double/long-double paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-trig.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tsc.c -->
# sources/test-tools/stress-ng/stress-tsc.c

## Purpose
Implements the `tsc` stressor, a CPU counter-read workload that repeatedly reads the architecture's time stamp or timebase counter and optionally verifies monotonic increase.

## Important APIs, Types, And Functions
Architecture-specific `rdtsc()` implementations cover LoongArch `rdtime`, RISC-V `rdtime`, x86 `rdtsc`, PowerPC `__ppc_get_timebase`, s390 `stck`, and SPARC tick. `stress_tsc_supported()` checks runtime support: RISC-V probes SIGILL recovery, x86 checks CPU identity and TSC feature flags, and other supported architectures return success. x86 optionally defines `lfence()` and `rdtscp` paths. Macros `TSCx32`, `TSCx32_verify`, `TSCPx32`, and lfence variants unroll counter reads 32 times. `stress_tsc_check()` verifies monotonicity with wraparound tolerance. `stress_tsc_generic()`, `stress_tsc_lfence()`, and `stress_tsc_rdtscp()` drive the selected read loop.

## Control Flow
After synchronization, `stress_tsc()` resolves `tsc-lfence` and `tsc-rdtscp`. Unsupported or non-x86-specific options log informational messages and fall back; `rdtscp` disables lfence when both are requested. If `tsc_supported` is true, it chooses verification based on global verify flags and calls the selected loop. Each loop measures elapsed wall time around four blocks of 32 reads, increments bogo ops once per 128 reads, and optionally checks the last read of each block against the previous saved counter. On exit it reports nanoseconds per time counter read.

## State And Persistence Behavior
State is process-local: support flags, optional RISC-V signal jump buffer, stack-local counters, and accumulated duration. No persistent system state or files are used.

## Dependencies And Integration Points
The file integrates with stress-ng architecture assembly helpers, CPU feature detection, signal wrappers, settings, sync, proc-state, bogo accounting, and metrics. It registers a `supported` callback, `CLASS_CPU`, `VERIFY_OPTIONAL`, and options for x86 lfence and rdtscp. Unsupported architectures export `stress_unimplemented`.

## Risks And Test Signals
Counters may be unavailable, trap, be virtualized poorly, or appear non-monotonic across CPU migration on broken systems. Verification tolerates high-bit wraparound but otherwise fails on non-increasing values. Serialized lfence and rdtscp paths measure different costs than plain reads. Test signals include skip messages for unsupported CPUs or disallowed RISC-V rdtime, monotonicity failure logs, nanoseconds/read metric, and option fallback messages for unsupported x86-specific modes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tsearch.c -->
# sources/test-tools/stress-ng/stress-tsearch.c

## Purpose
Implements the `tsearch` stressor, a libc tree-search workload that inserts shuffled 32-bit integers with `tsearch()`, searches them with `tfind()`, deletes them with `tdelete()`, and records comparison metrics.

## Important APIs, Types, And Functions
The stressor uses `search.h` APIs `tsearch`, `tfind`, and `tdelete`, plus stress-ng sort helpers for deterministic data initialization, shuffling, forward integer comparison, and comparison counting. The only option is `tsearch-size`, defaulting to 64 KB integers with min/max overrides.

## Control Flow
`stress_tsearch()` resolves size, allocates an `int32_t` array, waits at the sync barrier, initializes the data set, then loops while successful and running. Each iteration shuffles data, inserts every element into a fresh libc tree, aborts with cleanup if a tree node cannot be allocated, resets comparison counters, times a find pass across the array, optionally verifies that each found pointer exists and matches the requested value, accumulates comparison count and searched item count, deletes every inserted value, and increments bogo ops. On exit it emits comparisons/sec and comparisons/item metrics and frees the data array.

## State And Persistence Behavior
Data lives in heap memory, and the libc tree root is local to each loop iteration. Tree nodes allocated internally by `tsearch()` are released through `tdelete()` for inserted values. No files or kernel objects persist.

## Dependencies And Integration Points
The implemented path requires `search.h` and `tsearch()`. It uses stress-ng option parsing, sort data helpers, compare counters, timing, metrics, sync, and proc-state helpers. Metadata registers `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`, `VERIFY_OPTIONAL`; unsupported builds export an unimplemented reason.

## Risks And Test Signals
If insertion fails partway through, the code deletes values inserted so far and jumps to metric/cleanup handling. Duplicate values may cause `tsearch()` to return existing nodes, but the initialized data set is intended for searchable integer coverage. Verification checks pointer existence and value equality, but default non-verify runs primarily measure comparison behavior. Test signals include allocation skip/failure paths, optional element mismatch logs, bogo progress, comparisons/sec metric, comparisons/item metric, and clean unimplemented registration without libc support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-tsearch.c -->
