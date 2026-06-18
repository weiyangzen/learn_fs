# subset-b-009379 research

Grouped source research for stress-ng files under `sources/test-tools/stress-ng`. Each section preserves the source path for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-regs.c -->
# sources/test-tools/stress-ng/stress-regs.c

Purpose: implements the `regs` CPU stressor, which keeps architectural general-purpose registers, and on x86 some SIMD registers, hot by repeatedly rotating values through explicit register variables. It is both a CPU power/register-pressure stressor and a verification pass for compiler register assignment support.

Important APIs/types/functions: `stress_regs_info` registers the stressor with `VERIFY_ALWAYS`, `CLASS_CPU`, and options `regs-bitflip` and `regs-ops`. `regs_check32()`, `regs_check64()`, and `regs_check128()` validate register values and clear `stress_regs_success` on mismatch. `stress_regs_exercise()` and `stress_regs_exercise_bitflip()` are implemented per architecture using `register ... __asm__("reg")` bindings; x86_64 also has `stress_regs_exercise_sse()` and `stress_regs_exercise_mmx()` guarded by CPU feature probes. `SHUFFLE_REGS16()` repeats the architecture-specific shuffle macro 16 times.

Control flow: `stress_regs()` selects the normal or bitflip function from `regs-bitflip`, synchronizes, detects x86 MMX/SSE support where applicable, and loops while `stress_continue()` and validation succeed. Each outer iteration calls the exercise function 1000 times with the current seed value, increments the seed, then records one bogo operation. Architecture blocks cover x86_64, x86_32, LoongArch64, HPPA, m68k, SH4, RISC-V, Alpha, PPC/PPC64, SPARC, MIPS, OpenRISC, ARM, and a generic fallback when no specialized block is compiled.

State and persistence: state is process-local and volatile: `stress_regs_success`, `stash32`, `stash64`, optional `stash128`, and optional x86 feature flags. No filesystem or kernel object state is persisted. The volatile stashes keep computed values observable so the compiler cannot remove the work.

Dependencies and integration points: requires GCC-or-musl compiler support at GCC 8 level and excludes clang/ICC/PCC/TCC for explicit register assignment reliability. It depends on `core-arch.h`, `core-cpu.h`, `core-put.h`, `core-target-clones.h`, stress-ng settings, sync, bogo counters, and stop flags. Builds without required compiler support expose `stress_unimplemented`.

Risks and test signals: highest risk is architecture/compiler ABI fragility because named registers can conflict with calling conventions or optimizer behavior. Verification failures print the register name and expected/actual value. Test signals are successful compilation on each supported architecture, bogo increments per 1000 shuffle rounds, clean stop on `stress_continue()`, and failure return when any register check trips.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-remap.c -->
# sources/test-tools/stress-ng/stress-remap.c

Purpose: implements the `remap` memory/OS stressor for Linux `remap_file_pages()`, repeatedly rearranging pages inside a shared anonymous mapping and verifying that virtual page order changes match the requested layout.

Important APIs/types/functions: `stress_remap_info` exposes `remap-mlock` and `remap-pages` options with `VERIFY_ALWAYS`. `stress_get_unmapped_addr()` reserves and releases an address to later exercise invalid remaps. `remap_order()` applies `remap_file_pages()` page by page, optionally wrapping each page with `mlock()`/`munlock()`. `check_order()` validates sentinel values at the first word of each page.

Control flow: `stress_remap()` resolves page count, forcing a power-of-two fallback when needed, maps the data array and an order array, seeds one marker per page, and optionally locks memory. It prepares one known unmapped address and one mapping with an intentionally unmapped following page for invalid-call coverage. After sync, each loop remaps pages in reverse order, randomized order, all-to-page-zero order, and forward order, checking after every phase. It also calls `remap_file_pages()` on invalid unmapped, out-of-range, flag, and protection combinations.

State and persistence: all state is anonymous shared memory plus optional mapped/unmapped probe ranges. It reports memory usage and mmap statistics, then unmaps all allocations. There is no filesystem persistence.

Dependencies and integration points: requires `HAVE_REMAP_FILE_PAGES` and excludes SPARC. It uses stress-ng memory mapping helpers, mmap stats, random number helpers, sync, settings, and metrics. Unsupported builds return `stress_unimplemented`.

Risks and test signals: `remap_file_pages()` is obsolete and may fail or be unsupported on newer kernels/libcs. Large page counts can hit memory or mlock limits. Verification checks catch incorrect page ordering; metrics report nanoseconds per page remap and mmap residency/dirty/swap/contiguity details.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-remap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rename.c -->
# sources/test-tools/stress-ng/stress-rename.c

Purpose: implements the `rename` filesystem stressor, moving a temporary file back and forth across per-instance temporary directories while also exercising `renameat()` and `renameat2()` error paths when available.

Important APIs/types/functions: `stress_rename_info` registers a `CLASS_FILESYSTEM | CLASS_OS` stressor with `VERIFY_ALWAYS`. `exercise_renameat()` probes bad directory descriptors and file-descriptor-as-directory errors. `exercise_renameat2()` tests invalid flags, invalid flag combinations, `RENAME_EXCHANGE`, `RENAME_NOREPLACE`, bad descriptors, and file descriptor misuse. `stress_basename()` extracts basenames without mutating paths.

Control flow: `stress_rename()` creates two temporary directories keyed by instance, opens a temp directory fd for `*at` variants, then synchronizes. The loop creates or recreates a file, renames it to directory two and back to directory one, optionally repeats with `renameat()`, and optionally repeats with `renameat2(RENAME_NOREPLACE)`. Failures unlink both candidate names and restart with a new file.

State and persistence: state is temporary filesystem content only: two directories, one live file name, and optional directory fd. Cleanup closes fds, unlinks current candidate names, and removes both temp directories.

Dependencies and integration points: uses stress-ng temp path helpers, bad fd helper, `shim_unlink()`, `shim_fsync()`, sync, and bogo counters. `EXERCISE_RENAMEAT` depends on `HAVE_RENAMEAT` and `O_DIRECTORY`; `EXERCISE_RENAMEAT2` also depends on `HAVE_RENAMEAT2` and `RENAME_NOREPLACE`.

Risks and test signals: filesystems differ on `renameat2()` flag support and error codes. The stressor treats unexpected success on invalid combinations as verification failure. Signals are bogo increments per successful rename, complete temp cleanup, and correct handling of transient rename/open failures by restarting rather than leaking files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rename.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-resched.c -->
# sources/test-tools/stress-ng/stress-resched.c

Purpose: implements `resched`, a scheduler stressor that spawns children at a range of nice levels and has them repeatedly yield while optionally cycling normal scheduling policies.

Important APIs/types/functions: `stress_resched_info` is `CLASS_SCHEDULER | CLASS_OS` and `VERIFY_ALWAYS`. `stress_resched_usr1_handler()` lets children signal parent shutdown on scheduler verification failure. `stress_resched_child()` performs yield loops, `sched_setscheduler()`, `sched_getscheduler()`, and `nice(1)` progression. `stress_resched_spawn()` owns child creation for a slot.

Control flow: `stress_resched()` derives the maximum nice slot from `RLIMIT_NICE`, maps a shared PID table and shared yield counters, installs a SIGUSR1 handler, synchronizes, then starts one child per nice slot. The parent waits for children; when one exits it respawns that slot unless a failure or stop condition occurs. Children loop from their slot niceness up to the maximum, performing 1024 yield batches and optional scheduler policy switches per level.

State and persistence: state is shared anonymous PID/counter memory and child processes. On shutdown the parent kills/waits all children, prints per-priority yield percentages for instance zero, unmaps shared memory, and returns failure if children failed.

Dependencies and integration points: requires `nice()`; richer policy coverage depends on POSIX/Linux scheduling and `sched_setscheduler()`. It uses stress-ng PID sync, kill/wait helpers, signal handling, scheduling settings, and bogo counters.

Risks and test signals: scheduler calls may fail under low privileges or platform policy restrictions. Verification checks that `sched_getscheduler()` matches successfully set normal policies. Useful signals include balanced child respawn, yield distribution debug output, no orphaned children, and `EXIT_NOT_IMPLEMENTED` path when nice support is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-resched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-resources.c -->
# sources/test-tools/stress-ng/stress-resources.c

Purpose: implements the `resources` stressor, which repeatedly forks children that allocate, access, and free many kinds of system resources through the shared `core-resources` helpers.

Important APIs/types/functions: `stress_resources_info` exposes `resources-mlock`, `resources-num`, and `resources-procs`. `stress_resources_alarm()` sends SIGALRM to all tracked child PIDs. `stress_resources()` drives process fan-out and calls `stress_resources_allocate()`, `stress_resources_access()`, and `stress_resources_free()`.

Control flow: the stressor resolves resource count and child count from settings/minimize/maximize flags, computes a free-memory floor, optionally enables `MCL_FUTURE`, maps a shared PID table, allocates the resource descriptor array, and synchronizes. Each loop initializes PID tracking, forks children until process count or memory floor is hit, and each child drops capabilities, applies scheduler settings, allocates resources, yields/accesses them, frees them, and exits. The parent reaps all forked children, sending SIGALRM and reporting slow cleanup when stopping.

State and persistence: state is transient process trees, resource descriptors, allocated kernel resources owned by children, and a shared PID table. Cleanup frees the descriptor array and unmaps PID state. No repository or durable filesystem state remains.

Dependencies and integration points: integrates with `core-resources`, `core-capabilities`, `core-out-of-memory`, `core-signal`, memory-limit helpers, pipe-size discovery, OOM adjustment, scheduler settings, and stress-ng sync/bogo accounting.

Risks and test signals: intentionally pressures process, memory, pipe, fd, IPC, and lock limits, so ENOMEM/fork failures and slow cleanup are expected. Test signals are no leaked children/resources, bogo increments per fork attempt, graceful memory-floor throttling, and successful cleanup even after stop signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-revio.c -->
# sources/test-tools/stress-ng/stress-revio.c

Purpose: implements `revio`, a reverse-I/O filesystem stressor that creates a temporary file, truncates it to a target size, and writes fixed-size blocks from high offsets toward low offsets with optional open, sync, timestamp, readahead, and `posix_fadvise()` modes.

Important APIs/types/functions: `stress_revio_info` exposes `revio-bytes` and callback option `revio-opts`. `stress_revio_opts()` parses comma-separated mode names and rejects incompatible advice combinations. `stress_revio_advise()` applies selected fadvise hints. `stress_revio_write()` performs the write plus optional `futimes()`, `fsync()`, `fdatasync()`, and `syncfs()`.

Control flow: `stress_revio()` reads configured flags, forces `REVIO_OPT_O_DIRECT`, sizes per-instance I/O, creates a temp directory, allocates a 4096-aligned 1024-byte buffer, and synchronizes. Each iteration optionally rotates through modes under aggressive mode, opens and unlinks a temp file, truncates it, applies fadvise, then writes at decreasing offsets using randomized stride gaps. It tracks extent counts and optionally performs `readahead()` after dropping cache advice.

State and persistence: filesystem state is temporary and unlinked early after opening, with the directory removed at the end. State includes the aligned buffer, option flags, iteration counters, and average extent metric.

Dependencies and integration points: depends on stress-ng filesystem temp helpers, file extent helpers, write-hint helper, random buffer generation, settings callbacks, and conditional libc/kernel APIs such as `posix_memalign`, `posix_fadvise`, `readahead`, and sync calls.

Risks and test signals: direct I/O alignment and filesystem support are common failure points; ENOSPC retries are expected. Signals include bogo increments per successful block write, geometric mean extent metric, correct rejection of invalid option strings, and cleanup of temp directories on all exits.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-revio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ring-pipe.c -->
# sources/test-tools/stress-ng/stress-ring-pipe.c

Purpose: implements `ring-pipe`, a pipe I/O stressor that creates a ring of nonblocking pipes and circulates buffers around the ring using either read/write or `splice()`.

Important APIs/types/functions: `pipe_fds_t` stores each pipe pair. `stress_pipe_non_block()` sets `O_NONBLOCK`. `stress_pipe_read()` and `stress_pipe_write()` wrap I/O with diagnostics. `stress_ring_pipe_info` exposes `ring-pipe-num`, `ring-pipe-size`, and `ring-pipe-splice`, with `VERIFY_NONE`.

Control flow: `stress_ring_pipe()` allocates a max-size buffer, pipe fd table, and pollfd table, creates as many pipes as possible up to the requested count, sets read fds in `poll()`, and falls back from splice if unavailable. After sync it seeds two pipes with data. The main loop polls for readable pipes; each readable pipe sends its data to the next pipe in the ring via `splice()` or read/write, tracking duration, bytes, and bogo operations.

State and persistence: state is process-local memory and kernel pipe fds only. Cleanup closes every created fd, frees arrays, unmaps the buffer, and reports metrics.

Dependencies and integration points: requires `poll.h` and `poll()`. Optional splice mode depends on `HAVE_SPLICE` and `SPLICE_F_MOVE`. It uses stress-ng mmap helpers, settings, sync, metrics, and random/stop helpers.

Risks and test signals: fd limits can reduce the requested pipe count, and nonblocking pipe I/O may encounter transient failures. Metrics report pipe read/write calls per second and MB/s written through pipes. Since verification is disabled, success is mainly absence of unexpected poll timeouts, I/O errors, and fd leaks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ring-pipe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rlimit.c -->
# sources/test-tools/stress-ng/stress-rlimit.c

Purpose: implements `rlimit`, an OS stressor that repeatedly sets resource limits and deliberately triggers limit-related faults/signals inside an OOM-manageable child.

Important APIs/types/functions: `stress_rlimit_info` is `CLASS_OS`, `VERIFY_ALWAYS`. `stress_limits_t` stores target and saved rlimit values for CPU, file size, address space, data, stack, and nofile when available. `stress_resource_id_t` enumerates resource IDs for get/set round trips. `stress_rlimit_handler()` long-jumps out of SIGSEGV/SIGXCPU/SIGXFSZ. `stress_rlimit_child()` performs the actual limit triggering.

Control flow: the parent installs signal handlers, creates an unlinked temp file, saves original limits, then runs `stress_rlimit_child()` through `stress_oomable_child()`. The child maps an alternate signal stack, synchronizes, repeatedly validates getrlimit/setrlimit for known resources, probes an invalid resource ID, sets tight limits, and randomly triggers file-size, address-space, data, stack, or fd exhaustion. Signals return through `sigsetjmp()` and increment bogo operations.

State and persistence: process state includes global jump control, signal handlers, an alternate stack, saved limits, and an unlinked temp file descriptor. Cleanup restores signal handlers, closes fds, removes the temp directory, and unmaps the signal stack.

Dependencies and integration points: requires `siglongjmp` support. It integrates with stress-ng mincore, mmap, OOM child handling, signal helpers, temp filesystem helpers, and shim rlimit abstractions.

Risks and test signals: signal/jump behavior is delicate, especially around stack and address-space exhaustion. Some platforms lack specific rlimits. Signals are expected SIGSEGV/SIGXCPU/SIGXFSZ recovery, bogo increments after trapped faults, no permanent parent limit corruption, and no temp file leakage.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rlimit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rmap.c -->
# sources/test-tools/stress-ng/stress-rmap.c

Purpose: implements `rmap`, a reverse-mapping memory stressor that maps overlapping windows from one backing file into many virtual addresses and has multiple child processes write/verify strided ownership patterns through them.

Important APIs/types/functions: `stress_rmap_info` exposes `rmap-procs`. `stress_rmap_touch()` writes pointer-derived check values at strides based on child index and verifies them. `stress_rmap_child()` iterates mappings in forward, reverse, random, and partial orders, optionally calling `msync()`. A shared `counter_lock` coordinates bogo increments across children.

Control flow: `stress_rmap()` configures child count, installs SIGCHLD handling, creates shared PID state and a lock, creates an unlinked temp backing file sized for staggered mappings, fallocates it, maps 64 overlapping 16-page windows with padding pages between them, then forks children. Children wait for parent sync, install SIGALRM exit handling, then loop touching assigned stripes across each mapping. The parent waits until the shared bogo condition stops, then kills/waits children.

State and persistence: state consists of an unlinked temp file, shared file-backed mappings, anonymous padding mappings, shared PID state, and the counter lock. Cleanup unmaps all windows and paddings, closes the fd, removes the temp directory, destroys the lock, and unmaps PID state.

Dependencies and integration points: uses `core-killpid`, `core-out-of-memory`, `core-signal`, `core-pragma`, temp filesystem helpers, `shim_fallocate()`, sync start lists, lock helpers, scheduler settings, and OOM adjustment.

Risks and test signals: overlapping writable mappings and multi-process verification can expose kernel rmap, writeback, or cache coherency issues. Risks include fork limits, fallocate failure, and child failure propagation. Test signals are no check-value mismatches, successful child termination, and correct cleanup of all mappings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rofs.c -->
# sources/test-tools/stress-ng/stress-rofs.c

Purpose: implements `rofs`, a read-only filesystem stressor that discovers or accepts read-only mount points, recursively scans them, and exercises metadata/read-only operations while checking that paths are not writable.

Important APIs/types/functions: `stress_rofs_info_t` stores directory entry metadata, lstat result, and writable flag. `stress_rofs_method_t` maps method names to per-file functions. Methods include lstat, statx, access, mmap read, random read, lseek including `SEEK_HOLE`/`SEEK_DATA`, xattr listing, flock, valid and invalid open/close, fsync, and filesystem ioctls. `stress_rofs_scandir()` drives recursion and metrics. `stress_rofs_info` exposes `rofs-dir`.

Control flow: `stress_rofs()` initializes metrics, validates an explicit `rofs-dir` if supplied, or scans mounts with `stress_mount_get()` and `statfs()` for `ST_RDONLY`, skipping `/sys`, configfs, and cgroup mounts. It logs selected paths, synchronizes, then rotates instances across paths. `stress_rofs_scandir()` opens a directory, rejects writable directories, snapshots entries into a linked list, runs every method over every entry, increments bogo once per directory scan, recurses into subdirectories, and fails if any entry was writable.

State and persistence: only in-memory linked lists, stat buffers, metric counters, and mount path arrays persist during execution. File descriptors and mappings are short-lived. No files are created; invalid write attempts must fail on the target filesystem.

Dependencies and integration points: integrates with Linux mount helpers, optional xattr headers, optional `statx`, `flock`, `statvfs/statfs`, ioctl definitions from `linux/fs.h`, stress-ng mmap helpers, metrics, settings, and path helpers.

Risks and test signals: read-only detection can race with remounts or permission changes, and access checks have TOCTOU exposure acknowledged in code. Device pseudo-files may reject operations differently. Metrics report per-method operation rates; failure signals include unexpected writability, unexpected writable mmap/open, or unexpected metadata/read errors not whitelisted.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rofs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rotate.c -->
# sources/test-tools/stress-ng/stress-rotate.c

Purpose: implements `rotate`, a CPU/integer stressor for rotate-left and rotate-right operations over 8, 16, 32, 64, and optionally 128-bit integer widths.

Important APIs/types/functions: `stress_rotate_func_t` is the per-method function type. Macro families `STRESS_ROTATE_HELPER` and `STRESS_ROTATE` generate helpers and verified wrappers around `shim_rol*()` and `shim_ror*()`. `stress_rotate_funcs[]` maps method names including `all`, `rol8`, `ror8`, through optional 128-bit methods. `stress_rotate_info` exposes `rotate-method`.

Control flow: `stress_rotate()` zeroes metrics, resolves the method, checks global verify mode, synchronizes, and repeatedly calls the selected method. Method `all` dispatches every concrete method. Each helper seeds four random values, runs `ROTATE_LOOPS` rounds on all four, stores checksums through `stress_put_*()` to prevent optimization, and returns elapsed time. Verification reruns with restored RNG seed and compares checksums.

State and persistence: state is process-local metric accumulators and RNG seed snapshots. No external state is created.

Dependencies and integration points: depends on `core-builtin` rotate shims, `core-put` anti-optimization sinks, stress-ng method option parsing, metrics, random number generation, and optional `__uint128_t` support.

Risks and test signals: compiler optimization can otherwise fold rotate loops, so checksum sinks are important. Verification catches inconsistent helper output. Metrics report rotate operations per second per concrete method; failure is a checksum mismatch or invalid method resolution.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rotate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rseq.c -->
# sources/test-tools/stress-ng/stress-rseq.c

Purpose: implements `rseq`, a Linux restartable-sequences stressor that repeatedly enters an intentionally long critical section and measures interruptions/aborts.

Important APIs/types/functions: `rseq_info_t` stores critical-section counts, interruption counts, and SIGSEGV count. `stress_rseq_get_area()` derives libc's rseq area from `__builtin_thread_pointer()` plus `__rseq_offset`. `rseq_test()` creates a `struct rseq_cs`, registers it in `rseq_area->rseq_cs`, checks CPU consistency, stalls, and records aborts. `stress_rseq_supported()` validates libc/kernel rseq availability.

Control flow: `stress_rseq()` maps shared stats, finds the rseq area, synchronizes, and runs `stress_rseq_oomable()` through the OOM wrapper. The child installs a SIGSEGV handler and loops 10,000 critical-section attempts per bogo operation, using `cpu_id_start` as the expected CPU. On exit the parent reports interruptions per billion rseq ops.

State and persistence: shared anonymous `rseq_info` preserves counts across OOM/SEGV child behavior; `rseq_area` is thread-local libc state. No filesystem state exists.

Dependencies and integration points: requires Linux rseq headers, `__NR_rseq`, `__rseq_offset`, syscall support, GCC/musl compiler support, built-in thread pointer, assembly NOP, and excludes clang/ICC/ICX. It uses stress-ng OOM child handling, mmap, metrics, and support probing.

Risks and test signals: rseq ABI layout and compiler label-address assumptions are fragile, so unsupported toolchains are excluded. Signals include support-skip messages for unreadable/disabled rseq area, interruption-rate metric, and no unexpected SIGSEGV escalation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rseq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rtc.c -->
# sources/test-tools/stress-ng/stress-rtc.c

Purpose: implements `rtc`, a Linux real-time-clock stressor that exercises `/dev/rtc`, `/sys/class/rtc/rtc0/*`, and `/proc/driver/rtc` read/ioctl interfaces.

Important APIs/types/functions: `stress_rtc_dev()` opens `/dev/rtc` and probes many RTC ioctls: time read/set echo, alarm read/set echo, wake alarm, AIE/UIE/PIE on/off, epoch, IRQ period, voltage-low, RTC params, select timeout, and illegal ioctl. `stress_rtc_sys()` reads standard sysfs RTC attributes. `stress_rtc_proc()` reads proc driver state. `stress_rtc_info` is `CLASS_OS`, `VERIFY_ALWAYS`.

Control flow: `stress_rtc()` synchronizes, then in each loop runs the device, sysfs, and proc probes while their respective paths remain viable. Missing paths disable that probe; if all are absent it skips with `EXIT_NO_RESOURCE`. Unexpected errors outside tolerated permission, busy, no-entry, interrupt, and unsupported cases fail the stressor. Successful full passes increment bogo.

State and persistence: persistent state is limited to static booleans suppressing repeated unavailable device opens and local probe-enable flags. The code attempts some setter ioctls only with values just read, but does not create files or durable repo state.

Dependencies and integration points: requires `linux/rtc.h`; optional branches use `select()`, newer RTC param structures, and many ioctl constants. It integrates with stress-ng file-read helpers, shim memset, sync, and diagnostics.

Risks and test signals: RTC devices often require privileges, may be busy, or may not exist in containers. Setter ioctls can be permission-sensitive. Signals are graceful skip on missing RTCs, bogo increments for successful probes, and failure only on unexpected kernel/user-space errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-schedmix.c -->
# sources/test-tools/stress-ng/stress-schedmix.c

Purpose: implements `schedmix`, a scheduler/interrupt stressor that forks multiple children, randomly changes scheduling policies and CPU affinities, and interleaves many small scheduling, sleep, syscall, semaphore, timer, and procfs workloads.

Important APIs/types/functions: `stress_schedmix_setaffinity()` best-effort pins a process to a CPU. `stress_schedmix_waste_time()` randomly selects one of many micro workloads: yields, nanosleeps, NOP loops, time reads, nice calls, prime lookup, getpid loops, fork/wait, rusage/times, pressure-file reads, semaphore contention with SIGSTOP/SIGCONT, select/pselect, membarrier, and affinity changes. `stress_schedmix_child()` changes scheduler policy and calls waste work. `stress_schedmix_info` exposes `schedmix-cpumix` and `schedmix-procs`.

Control flow: `stress_schedmix()` optionally discovers eligible CPUs, installs SIGXCPU ignore for deadline overrun, maps PID state, optionally maps a POSIX semaphore, resolves child count, forks children, and releases them after global sync. Each child may install a profiling timer, repeatedly selects a different scheduling policy from `stress_sched_types`, applies `sched_setscheduler()` or deadline `sched_setattr()`, tolerates common permission/unsupported errors, wastes time, increments bogo, and optionally changes CPU. The parent either pauses or randomly changes child affinity until stopped.

State and persistence: state is child processes, shared PID table, optional shared semaphore, optional CPU list, and profiling timer state. Cleanup destroys semaphore, kills/waits children, unmaps PID state, and frees CPU data.

Dependencies and integration points: depends on Linux/POSIX scheduling support, stress-ng scheduler type tables, affinity helpers, capabilities, mmap, killpid, prime, procfs discard helpers, optional POSIX semaphores, membarrier, select/pselect, and setitimer.

Risks and test signals: privilege-sensitive RT/deadline policies commonly fail with EPERM and are tolerated. The broad random workload makes reproduction harder but increases scheduler coverage. Signals are child exit status, no orphaned workers, bogo progress, and absence of unexpected scheduler syscall errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-schedmix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-schedpolicy.c -->
# sources/test-tools/stress-ng/stress-schedpolicy.c

Purpose: implements `schedpolicy`, a scheduler policy stressor that cycles or randomly selects available scheduling policies for the current process, probes `sched_*` error paths, and records per-policy schedule rates.

Important APIs/types/functions: `stress_schedpolicy_info` exposes `schedpolicy-cpumix` and `schedpolicy-rand`. The stressor uses `stress_sched_types[]` from core scheduling integration, `sched_setscheduler()`, `sched_getscheduler()`, `sched_getparam()`, `sched_setparam()`, and Linux `sched_getattr()`/`sched_setattr()` shims. Optional util-clamp handling is guarded by `USE_CLAMP`.

Control flow: `stress_schedpolicy()` allocates per-policy counters, optionally discovers CPUs, decides sequential versus random policy selection, synchronizes, and loops. For each policy it handles deadline attributes, normal policies, and FIFO/RR priorities, including invalid syscall probes. Successful sets optionally change CPU affinity and verify with `sched_getscheduler()` when the policy metadata says it is checkable. Periodic blocks exercise invalid get/setparam calls, bad PIDs, oversized attrs, invalid flags, and util-clamp value cycling.

State and persistence: state is process-local counters, util-clamp min/max tracking, CPU list, and timing. No filesystem state is created.

Dependencies and integration points: requires Linux/POSIX scheduling support and excludes unsupported OSes. It integrates with stress-ng capabilities checks for `CAP_SYS_NICE`, affinity helpers, scheduler metadata, unused-PID helper, metrics, sync, and stop flags.

Risks and test signals: behavior is heavily privilege and kernel-version dependent; EPERM/EINVAL/ENOSYS/E2BIG/EBUSY are expected in many branches. Verification failures occur when a successfully applied policy is not reflected by `sched_getscheduler()`. Metrics report schedules per second per policy.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-schedpolicy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sctp.c -->
# sources/test-tools/stress-ng/stress-sctp.c

Purpose: implements `sctp`, a network stressor that forks a client/server pair using SCTP sockets, sends variable-sized messages, verifies payload identity, and exercises many SCTP socket options.

Important APIs/types/functions: `stress_sctp_info` exposes `sctp-domain`, `sctp-if`, `sctp-max-size`, `sctp-port`, and `sctp-sched`. `stress_sctp_sockopts()` round-trips numerous `IPPROTO_SCTP` options through `getsockopt()`/`setsockopt()`, including RTO, association, init, NODELAY, peer params, events, max segment/burst, scheduler, auth/ECN/asconf, and UDP encapsulation where available. `stress_sctp_client()` connects and validates received PID payloads. `stress_sctp_server()` binds/listens/accepts and sends increasing message sizes.

Control flow: `stress_sctp()` resolves domain/interface/port/size/scheduler, verifies optional interface availability, installs SIGPIPE handling, reserves a per-instance port, synchronizes, and forks. The child client retries connect up to 100 times, subscribes to events, optionally sets scheduler, receives messages, and checks the embedded parent PID. The parent server binds, listens, sets reuse and optional nodelay/scheduler, accepts clients, sends messages from a minimum size to configured max size in 16-byte steps, exercises sockopts, and waits for client exit.

State and persistence: state is sockets, reserved port bookkeeping, SIGPIPE count, and optional AF_UNIX socket path cleanup. No durable files are intended.

Dependencies and integration points: requires `libsctp` and `netinet/sctp.h`; networking helpers build sockaddr values, reserve/release ports, wrap port ranges, and validate interfaces. It also uses affinity, signal, kill/wait, and scheduler helpers.

Risks and test signals: SCTP may be unavailable in kernels/containers, ports may be busy, and scheduler sockopts vary by kernel. Signals are skip on unsupported protocol or port reservation failure, bogo increments per successful send, client payload verification, sockopt coverage without fatal unexpected errors, and release of reserved ports.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sctp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seal.c -->
# sources/test-tools/stress-ng/stress-seal.c

Purpose: implements `seal`, a Linux memfd sealing stressor that creates sealable anonymous files and verifies that shrink, grow, write, execute, and future-write seals enforce expected permissions.

Important APIs/types/functions: `stress_seal_info` is `CLASS_OS`, `VERIFY_ALWAYS`. `stress_seal()` uses `shim_memfd_create()`, `ftruncate()`, `fcntl(F_GET_SEALS/F_ADD_SEALS)`, shared writable `mmap()`, `write()`, `fchmod()`, and optional `F_SEAL_EXEC`/`F_SEAL_FUTURE_WRITE`. Fallback defines cover seal constants and `MFD_ALLOW_SEALING`.

Control flow: the stressor allocates one page of write buffer, synchronizes, and loops. Each iteration creates a memfd with a randomized name, truncates to one page, confirms seal retrieval, adds `F_SEAL_SHRINK` and verifies shrink fails with EPERM, adds `F_SEAL_GROW` and verifies growth fails, maps the file writable and verifies `F_SEAL_WRITE` fails with EBUSY while mapped, unmaps, adds `F_SEAL_WRITE`, verifies writes fail, optionally adds exec/future-write seals and checks chmod/mmap behavior, then closes and increments bogo.

State and persistence: state is one anonymous buffer and per-iteration memfd file descriptors. Memfds are anonymous kernel objects and disappear on close. Cleanup unmaps the buffer and closes current fd paths.

Dependencies and integration points: requires Linux and `memfd_create()`. It uses stress-ng mmap, madvise, memory naming, sync, random naming, and diagnostics.

Risks and test signals: kernel support for newer seals varies, and writable mappings can legitimately cause EBUSY. Test signals are expected EPERM/EBUSY failures, successful bogo increments per complete memfd seal cycle, and no fd/mapping leaks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seccomp.c -->
# sources/test-tools/stress-ng/stress-seccomp.c

Purpose: implements `seccomp`, an OS security stressor that repeatedly forks children, installs seccomp BPF filters, and verifies allowed versus trapped syscalls.

Important APIs/types/functions: `stress_seccomp_info` provides a `supported` probe and `VERIFY_ALWAYS`. Static BPF programs include allow-all, allow-open/write/close/exit, allow-open/close/exit without write, and randomized filter storage. `stress_seccomp_supported()` forks a probe child to test `SECCOMP_SET_MODE_FILTER`. `stress_seccomp_set_huge_filter()` explores filter-size limits. `stress_seccomp_set_filter()` sets `PR_SET_NO_NEW_PRIVS`, exercises seccomp query operations, invalid ops, strict mode probes, `seccomp()` and `prctl(PR_SET_SECCOMP)` fallback. `stress_sigsys()` exits with `EXIT_TRAPPED`.

Control flow: `stress_seccomp()` synchronizes and loops. Each iteration randomly decides whether write should be allowed and whether to try a random filter, then forks. The child disables dumpability, installs a SIGSYS handler, tries a huge allow filter, installs the selected filter, opens `/dev/null`, writes `TEST\n`, closes, and exits. The parent waits and verifies that disallowed write exits through the SIGSYS path while allowed write does not die from SIGSYS.

State and persistence: state is static filter arrays and per-child seccomp state. Seccomp filters are process-local and die with the child. No filesystem changes occur beyond opening `/dev/null`.

Dependencies and integration points: requires Linux audit/filter/seccomp/prctl headers, `PR_SET_SECCOMP`, and `SECCOMP_SET_MODE_FILTER`. It integrates with shim seccomp, waitpid, process dumpability, signal helpers, random helpers, and bogo counters.

Risks and test signals: seccomp may require capabilities or be disabled; random BPF filters are retried with safe filters on install failure. Critical signals are support-skip correctness, expected `EXIT_TRAPPED` for blocked writes, no unexpected child failures, and bogo increments after each verified child.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-seccomp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-secretmem.c -->
# sources/test-tools/stress-ng/stress-secretmem.c

Purpose: implements `secretmem`, a Linux secret-memory stressor that uses `memfd_secret()` to allocate secretmem-backed mappings, punches holes by unmapping pages, and repeats under OOM-safe child handling.

Important APIs/types/functions: `secretmem_mapping_t` tracks a three-page mapping and bitmap of live pages. `stress_secretmem_supported()` probes `shim_memfd_secret(0)` and distinguishes ENOSYS from unreserved secretmem ENOMEM. `stress_secretmem_unmap()` unmaps first/third pages, then the middle page, updating bitmaps. `stress_secretmem_child()` owns the mapping loop. `stress_secretmem_info` sets a support probe and `CLASS_CPU`.

Control flow: `stress_secretmem()` runs the child through `stress_oomable_child()` quietly. The child allocates the mapping table, opens a secretmem fd, truncates it to `MAPPINGS_MAX * 3` pages, synchronizes, then loops mapping three-page windows at increasing offsets. For each mapping it optionally stops on low memory, marks all pages live, marks memory mergeable, touches all pages to allocate secret pages, unmaps the middle page to create a hole, increments bogo, and later calls `stress_secretmem_unmap()` for all touched mappings before repeating.

State and persistence: state is a secretmem fd, transient shared mappings, and an in-memory bitmap table. The fd is closed and the table freed on exit. No durable files are created.

Dependencies and integration points: requires Linux `__NR_memfd_secret`. It integrates with stress-ng OOM child handling, mmap force-unmap, madvise, low-memory checks, sync, and bogo counters.

Risks and test signals: secretmem requires kernel support and boot-time reserved memory, so skips are common. OOM behavior is intentional when secret pages are exhausted. Signals are support-probe skip messages, bogo increments per mapped/hole-punched region, and complete unmapping/close/free cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-secretmem.c -->
