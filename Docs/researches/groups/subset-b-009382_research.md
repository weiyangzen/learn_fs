# subset-b-009382 Research

Grouped research for stress-ng source files under `sources/test-tools/stress-ng`. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stream.c -->
# sources/test-tools/stress-ng/stress-stream.c

## Purpose
Implements the `stream` stressor, a STREAM-inspired memory bandwidth, cache, floating-point, and memory-layout exerciser. It deliberately warns that results are not valid STREAM benchmark submissions; the goal is stressing read/write bandwidth, cache pressure, prefetch/non-temporal store paths, optional random indexing, and optional verification.

## Important APIs, Types, And Functions
The stressor exports `stress_stream_info` with `CLASS_CPU | CLASS_FP | CLASS_CPU_CACHE | CLASS_MEMORY`, optional verification, and options for discontiguous mappings, index depth, L3 size, madvise mode, mlock, and prefetch. `stress_stream_madvise_info_t` maps option names to `madvise()` constants. The large macro families generate copy, scale, add, and triad kernels for index depths 0 through 3, with prefetch variants and non-temporal store variants when available. `stress_stream_mmap()` allocates named anonymous buffers, optionally locks pages, and applies selected `madvise()`. `get_stream_L3_size()` discovers CPU cache size and scales it by NUMA node count. `stress_stream_init_index()` creates randomized permutation arrays, `stress_stream_exercise()` dispatches the selected kernel sequence, and `stress_stream_verify()` compares checksums across iterations using both numeric tolerance and byte-formatted fallback comparison.

## Control Flow
`stress_stream()` catches SIGILL for architecture-specific optimized paths, reads options, discovers or accepts L3 size, divides the working set across instances, rounds element count to an unroll-friendly multiple of eight, and allocates three double buffers plus optional index arrays. It seeds the pseudo-random generator, waits at the global stress-ng start barrier, optionally makes physical pages discontiguous, then repeatedly initializes data, runs the copy/scale/add/triad sequence selected by `stream-index`, verifies when requested, and increments bogo operations. At shutdown it reports read, write, and floating-point rates if runtime is long enough, collects mmap residency/swap/contiguity stats, and unmaps every buffer.

## State And Persistence
All durable state is in process memory: three stream buffers, up to three index arrays, checksum history, byte/op counters, elapsed-kernel time, and saved random seeds used to regenerate deterministic input data. There is no filesystem persistence. Optional mlock, discontiguous mapping, madvise, and mmap stats interact with kernel VM state and page placement, but all mappings are cleaned up before return.

## Dependencies And Integration Points
Depends on stress-ng core helpers for options, sync barriers, logging, metrics, random numbers, mmap stats, CPU cache discovery, NUMA count, signal handling, non-temporal stores, target clones, and compiler pragma feature gates. Kernel integration is through anonymous mmap, madvise, mlock, NUMA/cache topology discovery, and optional architecture-specific instruction support. The option parser exposes `stream-madvise` as a method list derived from compile-time available advice constants.

## Risks And Test Signals
Working-set sizing depends on cache detection; failures fall back to built-in defaults and can change pressure characteristics. `stream-index` 1 to 3 greatly increases memory footprint through index arrays. `stream-prefetch` is disabled with an info message when compiler support is missing. Optional non-temporal and target-clone paths can SIGILL on unsuitable CPUs, so the SIGILL catch is important. Useful test signals are successful allocation/unmap, bogo progress, checksum stability under `--verify`, nonzero rate metrics after runs longer than about 4.5 seconds, and mmap stats showing expected swapped/contiguous behavior. A code-review signal is that the final mmap stats block samples buffer `b` twice and never samples `c`, which may underreport one buffer's residency.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-strnum.c -->
# sources/test-tools/stress-ng/stress-strnum.c

## Purpose
Implements the `strnum` stressor, which repeatedly converts randomized numeric values to and from strings using libc conversion APIs. It stresses integer, unsigned integer, floating-point, scanning, formatting, and C23-style `strfrom*` paths while verifying that each conversion stays within exact or tolerance-based expectations.

## Important APIs, Types, And Functions
`stress_strnum_method_t` names each conversion method and points to a `stress_strnum_func_t`. The global aligned value/string pairs hold the current randomized int, long, long long, unsigned variants, float, double, and long double data. `stress_strnum_set_values()` refreshes those values and their canonical string forms. Method functions wrap `atoi`, `atol`, `atoll`, conditional `strtoul`, `strtoull`, `strtof`, `strtod`, `strtold`, `strfromf`, `strfromd`, `strfroml`, multiple `sscanf` forms, and `snprintf` forms. `stress_strnum_call_method()` times 1000 calls per bogo operation and updates per-method metrics. `stress_strnum_all()` runs every method except itself.

## Control Flow
`stress_strnum()` resolves `strnum-method`, waits at the global start barrier, clears per-method metrics, initializes random values, then loops until the stress-ng stop condition. Each loop invokes the selected method, marks failure if verification fails, refreshes random values every 1000 outer iterations, and increments bogo operations inside the method caller. After stopping, it emits call-per-second metrics for methods that accumulated timing data and sets deinit state.

## State And Persistence
State is process-local and held in static globals: current numeric values, canonical strings, and the metrics array. No filesystem or kernel object persists. The only cross-iteration state is refreshed random data and accumulated per-method timing/count values.

## Dependencies And Integration Points
Depends on stress-ng option handling, bogo counters, timing, metrics, random number generation, failure logging, sync barriers, and shim math helpers. Compile-time feature macros gate optional libc functions so the method table matches the target C library. The exported `stress_strnum_info` uses `VERIFY_ALWAYS`, CPU/compute/hot classification, and a method option callback.

## Risks And Test Signals
Floating-point checks use fixed tolerances and truncated string formats, so platform formatting or long-double precision differences can affect pass/fail behavior. Global static state means each worker has private process state, but this would not be thread-safe if reused differently. `strfrom*` comparisons intentionally compare only a truncated prefix around the decimal point, reducing false failures but also reducing strictness. Test signals are no `pr_fail()` conversion mismatches, populated per-method metrics, and successful operation of the `all` method across the compile-time enabled method table.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-strnum.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-swap.c -->
# sources/test-tools/stress-ng/stress-swap.c

## Purpose
Implements the `swap` stressor, which creates temporary swap files, writes valid and intentionally malformed swap headers, exercises `swapon()` and `swapoff()`, and optionally asks the kernel to page out this process's mappings. It is Linux/Unix swap-subsystem pressure rather than a generic memory allocator stressor.

## Important APIs, Types, And Functions
`stress_swap_info_t` models the Linux `SWAPSPACE2` header fields used by the stressor. `stress_swap_supported()` requires `CAP_SYS_ADMIN`. `stress_swap_self()` parses `/proc/self/maps` and uses `MADV_PAGEOUT` on suitable mappings. `stress_swap_zero()` writes page-sized zero blocks to establish the file. `stress_swap_set_size()` writes swap metadata, UUID, volume label, last page, bad-page count, and signature, optionally corrupting selected fields. `stress_swap_check_swapped()` tracks `/proc/vmstat` `pswpout` deltas for metrics. `stress_swap_clean_dir()` forcibly swapoffs and removes stale regular files in the stressor temp directory. `stress_swap_child()` owns the main swapon/swapoff loop and page-integrity checks.

## Control Flow
The public `stress_swap()` runs `stress_swap_child()` under `stress_oomable_child()` and performs final directory cleanup. The child decides whether `swap-self` is active, maps a reusable page, removes stale temp files, creates a temp directory and swap file, disables CoW on Linux filesystems where possible, and preallocates a maximum-size swap file. After the sync barrier it repeatedly chooses a random swap size, random swap flags, and occasionally a bad header mode. It writes the header, calls `swapon()`, maps anonymous memory sized to the current swap, writes per-page address sentinels, optionally pageouts the mapping and self mappings, verifies sentinel values, unmaps, then calls swapoff. It also probes invalid swapon/swapoff filenames and invalid flags before incrementing bogo operations.

## State And Persistence
Persistent state is intentionally temporary: a per-worker temp directory and swap file are created and unlinked/removed during cleanup. Kernel state may briefly include an active swap device, memory pages moved to swap, VM counters, and filesystem flags such as no-CoW. Cleanup paths close the file, unlink it, remove the temp dir, call swapoff on stale files, and unmap the page buffer. `stress_swap_check_swapped()` has a static previous counter within the process.

## Dependencies And Integration Points
Requires build support for `sys/swap.h` and `swap`; otherwise the exported stressor is `stress_unimplemented`. Runtime requires `CAP_SYS_ADMIN`, `swapon`, `swapoff` via `stress_memory_swap_off`, mmap, fallocate/write/lseek, `/proc/vmstat`, optional `/proc/self/maps`, Linux ioctls for no-CoW, madvise/pageout helpers, filesystem temp helpers, and OOMable child orchestration.

## Risks And Test Signals
This is privilege-sensitive and can fail because of missing capability, unsupported filesystem type, existing swapfile limits, low disk space, CoW filesystems, or kernels rejecting swap flags/header variants. Bad headers are expected to fail and should not be reported as stressor failures. Good headers failing with EPERM, EINVAL, EBUSY, or ENOSPC are handled specially. Test signals are bogo progress, no active swapfiles left behind, successful sentinel preservation after swap pressure, pages-swapped-out metric updates, and skip behavior on unsupported or underprivileged systems.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-swap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-switch.c -->
# sources/test-tools/stress-ng/stress-switch.c

## Purpose
Implements the `switch` stressor, which forces rapid context switches between a parent worker and a child using one of several synchronization methods: POSIX message queues, pipes, or System V semaphores. It measures approximate nanoseconds per context switch and can optionally pace switching to a requested frequency.

## Important APIs, Types, And Functions
`stress_switch_method_t` maps method names to implementations. `stress_switch_rate()` reports harmonic-mean nanoseconds per context switch. `stress_switch_delay()` dynamically adjusts nanosleep delay based on bogo count and target frequency. `stress_switch_pipe()` writes through a pipe while a child drains it, optionally using `pipe2(..., O_DIRECT)` and pipe-size tuning. `stress_switch_sem_sysv()` ping-pongs a SysV semaphore with `SEM_UNDO`. `stress_switch_mq()` creates a POSIX message queue with depth one and exchanges fixed-size messages. `stress_switch()` selects the default `pipe` method, applies options, computes delay and threshold, and dispatches the selected method.

## Control Flow
Each method creates its IPC primitive before the global sync barrier, forks a child after sync, moves the child toward the parent's CPU, applies scheduler settings, and then enters a parent/child synchronization loop. The parent increments bogo operations on each exchange, optionally invokes rate pacing, and exits when the stress-ng stop condition or IPC failure occurs. The child loops on the complementary receive/send or semaphore operation until stopped or broken pipe/queue/semaphore failure. The parent records the metric, closes/unlinks/removes IPC resources, kills/waits the child, and deinitializes state.

## State And Persistence
State is transient IPC resources plus one child process per worker. Pipes are anonymous file descriptors. SysV semaphores persist in the kernel until `semctl(..., IPC_RMID)` and are therefore explicitly removed. POSIX message queues persist by name until `mq_unlink()`, so the stressor uses a name containing stressor name, parent PID, and instance and unlinks it on exit. Bogo counters and static delay adjustment state remain process-local.

## Dependencies And Integration Points
Depends on stress-ng affinity, kill/wait, mmap, signal, scheduler, sync-barrier, timing, metric, and option helpers. POSIX message queue support requires `mqueue.h`, librt, and `HAVE_MQ_POSIX`; SysV semaphore support requires `HAVE_SEM_SYSV` and `key_t`; pipe method is the unconditional fallback. It also integrates with stress-ng method-option enumeration through `stress_switch_method()`.

## Risks And Test Signals
IPC setup can fail because of mqueue limits, SysV semaphore limits, fork pressure, pipe buffer tuning failure, or missing compile-time features. SysV key generation retries only 100 random keys. The rate metric divides by the counted exchanges, so premature zero-count failures would make results unreliable. `switch-freq` pacing uses bogo count and wall time, which is approximate under heavy scheduling pressure. Test signals are child cleanup, IPC resource cleanup, bogo progress, nonzero nanoseconds-per-context-switch metrics for the selected method, and no lingering message queues or semaphores.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-switch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sync-file.c -->
# sources/test-tools/stress-ng/stress-sync-file.c

## Purpose
Implements the `sync-file` stressor, which exercises `sync_file_range()` over an allocated temporary file using forward, reverse, random, bad-file-descriptor, bad-offset, and open-ended range patterns. It targets filesystem writeback and Linux-specific sync-range behavior.

## Important APIs, Types, And Functions
`sync_modes[]` enumerates available mode combinations, including wait-before/write, wait-before/write/wait-after, write-only, wait-only, and no-op. `stress_sync_allocate()` truncates the file, `fdatasync()`s it, and `fallocate()`s the requested size. `stress_sync_file()` owns option handling, temp-file creation, sync loops, negative-input probes, and cleanup. The exported `stress_sync_file_info` classifies the stressor as I/O, filesystem, and OS, with `VERIFY_ALWAYS`.

## Control Flow
The stressor chooses total bytes from `sync-file-bytes`, maximize/minimize flags, and instance count, ensuring each worker has at least 1 MiB. It creates a temp directory and file, sets short write hints, probes pathconf async/sync I/O values, unlinks the pathname while keeping the file descriptor open, then waits at the sync barrier. Each loop chooses a random sync mode, reallocates the file, walks forward over random 1 KiB to roughly 128 KiB chunks calling `shim_sync_file_range()`, exercises invalid fd/offset/count and a half-file open-ended sync, reallocates again, walks reverse, reallocates again, and performs random aligned 128 KiB syncs. It increments bogo operations after the three main phases.

## State And Persistence
State is an open but unlinked temporary file descriptor and its allocated blocks. The filename is removed early, and the temp directory is removed at shutdown, so the filesystem should not retain named artifacts. Runtime state includes selected byte counts, sync mode, offsets, and return code. ENOSPC during allocation is treated as a recoverable loop condition.

## Dependencies And Integration Points
Requires `HAVE_SYNC_FILE_RANGE`; otherwise it exports an unimplemented stressor. It uses stress-ng filesystem temp helpers, write-hint helper, `shim_fallocate`, `shim_fdatasync`, `shim_sync_file_range`, pathconf probes, random numbers, sync barrier, option handling, and filesystem type reporting for diagnostics.

## Risks And Test Signals
`sync_file_range()` is Linux-specific and can return ENOSYS through the shim even when compiled. Filesystems may reject fallocate, run out of space, or expose unusual behavior for unlinked open files. Reverse mode passes `sync_file_bytes - offset`, so the first call starts one byte past the last valid offset for nonzero sizes; errors there would be surfaced as reverse sync failures. Test signals are clean skip on ENOSYS, continued operation across ENOSPC, no named temp-file residue, bogo progress, and absence of `pr_fail()` messages from forward/reverse/random sync phases.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sync-file.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-syncload.c -->
# sources/test-tools/stress-ng/stress-syncload.c

## Purpose
Implements the `syncload` stressor, which makes all workers generate synchronized CPU load spikes followed by synchronized sleeps. The busy phase rotates through small operations that touch instruction issue, scheduler yield, fences, atomics, vector math, RNG, writes, square root, and fused multiply-add paths depending on architecture and compile-time support.

## Important APIs, Types, And Functions
`stress_syncload_op_t` is the operation function pointer type. The operation table includes no-op, repeated NOPs, x86 pause, ARM/PPC yield, scheduler yield, x86 RDRAND fallback, memory fences, barriers, spin loops, optional vector math, nice calls, spin writes, sqrt, optional atomic increment of `g_shared->syncload.value`, and FMA-like updates to global arrays. `stress_syncload_init()` stores the shared start time. `stress_syncload_gettime()` reads it. `stress_syncload()` handles timing, operation rotation, sleep, and bogo increments. The exported info installs `.init = stress_syncload_init`.

## Control Flow
The init hook records a shared start timestamp before workers run. Each worker catches SIGILL, reads maximum busy and sleep milliseconds, converts them to seconds, checks x86 RDRAND support, initializes FMA state, waits at the global sync barrier, then loops. Each iteration selects the next operation from the compile-time-built table, extends the shared timeout by the busy duration, repeatedly calls the operation until the timeout, extends by the sleep duration, nanosleeps until the sleep timeout when still ahead of time, and increments bogo operations. Because workers use the same initial timestamp and deterministic duration progression, their bursts align.

## State And Persistence
State is in memory only. Shared state includes `g_shared->syncload.start_time` and optional atomic `value`; process globals include the RDRAND capability flag and arrays used to keep optimized math stores visible. No files or kernel objects persist beyond normal scheduling and timing effects.

## Dependencies And Integration Points
Depends on stress-ng shared-state layout, init hooks, timing, option parsing, sync barriers, signal handling, CPU feature detection, asm helpers for x86/ARM/PPC, compiler target clones, vector-math support, put helpers, scheduler/yield shims, nanosleep shim, and bogo counters. Compile-time feature gates determine the final operation table.

## Risks And Test Signals
Architecture-specific instructions can raise SIGILL if feature detection or target dispatch is wrong, so the signal catch is part of correctness. Synchronized wall-clock timing can drift under scheduler starvation, making actual burst alignment approximate. The global operation state is process-local except for the shared atomic value. Test signals are bogo progress across workers, visible periodic load spikes, no SIGILL-induced failure on supported CPUs, and option bounds enforcing 1 to 10000 millisecond busy/sleep windows.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-syncload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sysbadaddr.c -->
# sources/test-tools/stress-ng/stress-sysbadaddr.c

## Purpose
Implements the `sysbadaddr` stressor, a broad OS syscall robustness exerciser that passes deliberately bad, unreadable, unwriteable, unaligned, boundary, unmapped, executable, and permission-mismatched pointers into many syscalls. It aims to expose kernel and libc wrapper handling problems without letting dangerous calls corrupt the main stress-ng process.

## Important APIs, Types, And Functions
`stress_bad_addr_t` pairs an address-generating function with resolved address and readability/writeability flags. `stress_sysbadaddr_state_t` is shared cursor/counter state containing syscall index, address index, bogo counter, and max operations. Address helpers generate unaligned static data, read-only page, null, text pointer, end-of-page pointer, max pointer, unmapped adjacent page, RX page, PROT_NONE page, write-only page, and write-exec page. `bad_syscalls[]` is a compile-time-gated table of wrappers covering filesystem paths, sockets, clocks, clone, execve, xattrs, LSM syscalls, stats, memory policy/migration, mlock/msync/mincore, pipes, polling/select, read/write/vector I/O, resource limits, time, uname, waits, and more. `stress_do_syscall()` forks a contained child to run one or more table entries. `stress_sysbadaddr_child()` iterates the table. `stress_sysbadaddr()` maps the protected pages and runs the child under OOMable/drop-cap handling.

## Control Flow
`stress_sysbadaddr()` allocates shared state, maps pages with PROT_READ, PROT_READ|PROT_WRITE over two pages, PROT_READ|PROT_EXEC, PROT_NONE, PROT_WRITE, and optionally PROT_WRITE|PROT_EXEC, then unmaps the second RW page so the end-of-page and adjacent-unmapped address classes are valid. It resolves each bad address, waits at the sync barrier, and invokes `stress_oomable_child()`. The worker child resets table cursors and repeatedly walks every syscall/address combination. For each candidate address it calls `stress_do_syscall()`, which forks a short-lived grandchild, installs fatal signal handlers, applies resource limits, marks shared memory read-only, drops capabilities, applies scheduler settings, and executes bad syscall wrappers while updating the shared counter until the table or max-ops limit is reached. The parent waits, kills on wait problems, copies the shared counter back to the bogo counter, and continues.

## State And Persistence
State is shared anonymous memory plus several anonymous mappings with specific protections. The shared cursor lets a crashing or signal-exiting grandchild resume near the next syscall/address combination instead of restarting the entire matrix. The stressor creates no persistent files, but many bad syscall probes temporarily open `/dev/null`, `/dev/zero`, stdin, current temp paths, directory fds, memfds, timers, clones, pipes, and other kernel objects; wrappers close or wait on objects they successfully create. Cleanup unmaps all pages and shared state, tolerating optional WX mapping failure.

## Dependencies And Integration Points
Depends heavily on stress-ng shim layers for portability across libc/kernel combinations: mmap helpers, capabilities, signals, kill/wait, OOMable children, madvise, CPU cache flushing, filesystem temp path helpers, memory policy/migration, getrandom, copy_file_range, xattrs, LSM syscalls, and scheduler settings. Compile-time feature macros determine which syscall probes are included. Runtime integration is intentionally kernel-facing and privilege-reducing: bad calls run after dropping capabilities and limiting CPU/process counts.

## Risks And Test Signals
The stressor intentionally provokes EFAULT, EINVAL, EPERM, signals, failed clones, failed execve, and syscall-specific errors; those are expected unless they escape containment. The broad table creates portability risk because some libc wrappers may validate arguments before entering the kernel while others may not. Resource leaks are the main hazard in wrappers that successfully create fds, timers, clone children, queues, or pipes before failing later. Shared cursor logic is important: if a bad call hangs, the ITIMER_REAL watchdog and signal handlers should terminate the grandchild; if cursor advancement stalls, parent-side checks advance indexes. Test signals are steady bogo/counter progress, no parent crash, no leaked child processes, successful cleanup of mappings, and graceful skips when shared mappings cannot be allocated. Absence of `.verify` and options means operational health is observed through continued execution and process containment rather than value assertions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-sysbadaddr.c -->
