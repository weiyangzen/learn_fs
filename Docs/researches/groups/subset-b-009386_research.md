# subset-b-009386 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-segv.c -->
# sources/test-tools/stress-ng/stress-vm-segv.c

## Purpose
`stress-vm-segv.c` implements the `vm-segv` stressor, whose purpose is to force child processes into invalid virtual-memory states and verify that they terminate with `SIGSEGV`. It stress-tests unmapping of executable text, nearby pages, stack pages, instruction-cache flushing paths, process creation, signal delivery, and parent-side wait/kill cleanup around intentionally broken children.

## Important APIs, types, and functions
- `stress_vm_segv()` is the registered stressor entry point in `stress_vm_segv_info`.
- `vm_unmap_child()` repeatedly tries large `munmap()` ranges starting from `stress_null_get()` while flushing a page-aligned address near the helper code.
- `vm_unmap_self()` unmaps the page containing itself and the previous page, except on Apple where this is avoided because children can hang.
- `vm_unmap_stack()` finds the page containing a stack variable, optionally marks it read-only with `mprotect()`, then unmaps it and the previous page.
- The stressor relies on `fork()`, `pipe()`, `read()`, `write()`, `shim_waitpid()`, `stress_kill_and_wait()`, `stress_set_oom_adjustment()`, `stress_make_it_fail_set()`, `stress_process_dumpable(false)`, `shim_clflush()`, and `shim_flush_icache()`.

## Control flow
The parent enters synchronized start, then repeatedly creates a pipe and forks. The child closes the read end, writes `MSG_CHILD_STARTED`, blocks `SIGSEGV`, applies stress-ng child settings, and tries increasingly aggressive unmaps: broad child address-space unmapping, self-code unmapping, then stack unmapping. If all attempts fail to fault, the child exits failure. The parent waits for the start token, waits for the child, increments bogo operations only when the child died from `SIGSEGV`, and always tries to terminate/reap the child. Fork failures go through `stress_redo_fork()` and return `EXIT_NO_RESOURCE` only when retrying is no longer appropriate.

## State and persistence
There is no persistent state. Per-worker state is limited to the parent loop, a pipe file descriptor pair, a child PID, and `test_valid`. Bogo operation count records observed `SIGSEGV` deaths. The child deliberately corrupts its own address space and exits with `_exit()` if it unexpectedly survives.

## Dependencies and integration points
The file integrates with stress-ng through `stress_vm_segv_info`, help text, `CLASS_VM | CLASS_MEMORY | CLASS_OS`, and `VERIFY_ALWAYS`. It depends on stress-ng wrappers for cache flush, signal/wait behavior, OOM adjustment, and process lifecycle. Platform guards avoid problematic cache flushes on some BSDs and avoid self-unmapping on Apple.

## Risks and edge cases
The stressor intentionally creates abnormal process state and may expose kernel, libc, or platform-specific behavior in `munmap()`, signal delivery, and instruction-cache coherency. If the child cannot write its start token, the parent kills it without treating the run as a valid test. If valid children never produce `SIGSEGV`, the stressor returns failure. Pipe and fork failures are treated as resource problems. The `mprotect()` and `munmap()` calls target stack/code-adjacent pages, so platform-specific hangs or nonstandard memory layouts are the main portability risks.

## Test signals
Expected success is at least one child that announces start and dies by `SIGSEGV`, causing bogo increments. Verification failure is reported as `no SIGSEGV signals detected` when a valid child ran but no `SIGSEGV` was observed. Additional signals are resource skips for pipe/fork failure and debug output when the pipe token is wrong.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-segv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-splice.c -->
# sources/test-tools/stress-ng/stress-vm-splice.c

## Purpose
`stress-vm-splice.c` implements `vm-splice`, a Linux pipe and virtual-memory stressor that exercises `vmsplice()` in both directions: memory to pipe and pipe to memory. It measures data throughput and call rate while checking that a small data pattern survives the pipe-to-memory path.

## Important APIs, types, and functions
- `stress_vm_splice()` is compiled when `HAVE_VMSPLICE` and `SPLICE_F_MOVE` are available; otherwise the stressor is registered as unimplemented.
- `opts[]` exposes `vm-splice-bytes` with `MIN_VM_SPLICE_BYTES`, `MAX_VM_SPLICE_BYTES`, and a default of `64 KiB`.
- It uses `stress_mmap_populate()` for the main iovec buffer and one page of check data, `stress_memory_anon_name_set()`, `pipe()`, `open("/dev/null")`, `vmsplice()`, `splice()`, `write()`, and `stress_metrics_set()`.
- Data verification uses a moving `checkval`, a prime increment from `stress_prime64_get()`, and `stress_mwc64()` initial seeding.

## Control flow
The stressor resolves total bytes from settings or maximize/minimize flags, divides the total by instance count, rounds down to a page multiple, maps the main buffer and one-page check buffer, creates a pipe, and opens `/dev/null`. After synchronized start, each loop first `vmsplice()`s the mapped buffer into the pipe and `splice()`s those bytes to `/dev/null`. It then writes one page containing an updated check value to the pipe, `vmsplice()`s from the pipe into the mapped buffer, verifies the first word when enough bytes were moved, updates metrics counters, and increments bogo operations. Every 1000 iterations it times the `vmsplice()` calls to reduce timing overhead.

## State and persistence
All state is per worker and in process memory: mapped buffers, pipe descriptors, `/dev/null` descriptor, moving check value, byte/call counters, duration counters, and return code. No state persists after cleanup. Mapped memory and file descriptors are released before returning.

## Dependencies and integration points
The stressor integrates through `stress_vm_splice_info`, classifies as `CLASS_VM | CLASS_PIPE_IO | CLASS_OS`, and uses `VERIFY_ALWAYS`. It depends on Linux `vmsplice()` semantics and `SPLICE_F_MOVE`. It also uses stress-ng memory-size option parsing, memory usage reporting, anonymous mapping naming, random buffer initialization, and harmonic-mean metrics.

## Risks and edge cases
Allocation size is adjusted per instance and at least one page, but the final `sz` is page-aligned down, so settings smaller than a page are normalized. Mapping failures skip as `EXIT_NO_RESOURCE`; pipe/open failures are failures. Runtime `vmsplice()`, `splice()`, or write errors break the loop, preserving any earlier data-check failure in `rc`. The data check only validates the initial word of the pipe-to-memory transfer, so it is a sentinel check rather than exhaustive data validation.

## Test signals
The main correctness signal is the check-value comparison after pipe-to-memory `vmsplice()`. Metrics report `MB per sec vm-splice rate` and `vm-splice calls per sec`. Build-time absence of `vmsplice()` or `SPLICE_F_MOVE` produces an unimplemented stressor with an explicit reason.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm-splice.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm.c -->
# sources/test-tools/stress-ng/stress-vm.c

## Purpose
`stress-vm.c` is the main anonymous virtual-memory stressor for stress-ng. It allocates per-worker memory, optionally changes mapping behavior, and applies a large catalog of memory access algorithms to exercise RAM, caches, TLBs, page residency, NUMA policy, non-temporal stores, direct stores, vector writes, rowhammer-like access, and verification of data patterns.

## Important APIs, types, and functions
- `stress_vm()` is the registered entry point in `stress_vm_info`; `stress_vm_child()` performs the allocation and method loop inside `stress_oomable_child()`.
- `stress_vm_func` is the common method signature. `stress_vm_method_info_t` maps method names to functions. `stress_vm_context_t` carries the selected method, per-worker byte count, shared bit-error counter, NUMA masks, `stress_mmap_stats_t`, mmap/munmap timing totals, and flags.
- Method implementations include moving inversion, modulo-X, walking-one/zero data and address tests, gray/grayflip, increment/decrement, prime-step operations, random set/sum, rotate-right, flip, one-zero/zero-one, galloping patterns, nybble increment, write/read bandwidth methods, rowhammer, mscan, cache stripe/line tests, non-temporal 128-bit write/read, forward/reverse patterns, LFSR32, and checkerboard.
- Optional architecture paths use `stress_ds_store64()`, `stress_nt_store64()`, `stress_nt_store128()`, `stress_nt_load128()`, compiler vector types, and x86 feature checks.
- Options include `vm-bytes`, `vm-discontiguous`, `vm-flush`, `vm-hang`, `vm-keep`, `vm-locked`, `vm-madvise`, `vm-method`, `vm-numa`, and `vm-populate`.

## Control flow
`stress_vm()` allocates shared context, discovers cache line size, resolves NUMA and method settings, scales `vm-bytes` by worker count, maps a shared bit-error page, synchronizes workers, and invokes `stress_oomable_child()`. `stress_vm_child()` reads runtime flags, constructs mmap flags, loops while `stress_continue_vm()` allows progress, maps or reuses a page-aligned anonymous buffer, applies population, madvise, optional NUMA randomization, optional discontiguous remapping, touches pages, and calls the selected memory method. Unless `vm-keep` is set, it gathers mapping stats, randomizes madvise again, and unmaps each iteration. On exit it unmaps any kept buffer, computes bogo rate, and returns resource or success status.

The default method `all` advances through the method table one method per call, skipping itself. Most methods write a deterministic or seeded pattern, optionally flush cache or touch pages, optionally inject synthetic bit errors when `INJECT_BIT_ERRORS` is enabled for testing, then verify and add to the shared bit-error count.

## State and persistence
Runtime state is process-local plus shared anonymous mappings. The shared context and bit-error page allow the oomable child path to report errors and mmap statistics to the parent. Static per-method variables such as offsets, seed values, and pattern counters intentionally vary subsequent passes. No persistent files are written. Final bogo count is shifted down by `VM_BOGO_SHIFT` to expose user-facing operations rather than raw memory-operation counts.

## Dependencies and integration points
This file is deeply integrated with stress-ng core helpers for option parsing, metrics, mmap population/statistics, madvise randomization, mincore page touching, cache details, cache flushing, NUMA masks, OOM child handling, signal handling, target clones, non-temporal load/store helpers, vector math support, and stressor registration. It is registered as `CLASS_VM | CLASS_MEMORY | CLASS_OS` with `VERIFY_OPTIONAL` and up to 12 metrics. Build-time feature guards adapt behavior for `madvise`, `mprotect`, `MAP_LOCKED`, `MAP_POPULATE`, Linux NUMA policy, x86 direct/non-temporal stores, vector math, and 128-bit support.

## Risks and edge cases
The stressor intentionally pushes memory pressure and can shrink `buf_sz` after repeated `ENOMEM`. Some methods assume useful alignment and sizes derived from page-aligned `vm_bytes`; very small mappings are normalized to at least `MIN_VM_BYTES`. `vm-hang 0` can intentionally sleep until externally stopped. Optional rowhammer and cache-flush paths are hardware sensitive. `vm-keep` changes lifecycle by reusing the same mapping, so stale method state and dirty pages are deliberate. A likely reporting defect exists in the munmap metrics block: `munmaps total` uses `context->mmap_count` instead of `context->munmap_count`. Verification is optional at the stressor level, but bit errors still force `EXIT_FAILURE` when the shared count is nonzero.

## Test signals
Correctness signals are per-method bit-error counts, `pr_fail()` messages from `stress_vm_check()` under verify mode, and the final shared `bit_error_count` failure. Operational signals include mmap/munmap total and duration metrics, mmap statistics for total/swapped/dirtied/contiguous pages, bogo operations scaled by `VM_BOGO_SHIFT`, skip messages for allocation/NUMA support failures, and method-selection debug output from instance zero.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vma.c -->
# sources/test-tools/stress-ng/stress-vma.c

## Purpose
`stress-vma.c` implements the `vma` stressor, which deliberately races many virtual-memory-area operations from multiple processes and pthreads. It targets kernel VMA management by repeatedly mapping, unmapping, protecting, locking, advising, syncing, reading `/proc` VMA views, touching unstable mappings, and optionally scanning pagemap information.

## Important APIs, types, and functions
- `stress_vma()` is the registered entry point when pthread support exists.
- `stress_vma_context_t` carries the stress-ng args, a candidate data address, and parent PID. `stress_thread_info_t` maps thread functions to instance counts. `stress_vma_metrics_t` is a shared metric block with padded counters for 13 metric slots.
- Core operations are `stress_vma_mmap()`, `stress_vma_munmap()`, `stress_vma_mlock()`, `stress_vma_munlock()`, `stress_vma_madvise()`, `stress_vma_mincore()`, `stress_vma_mprotect()`, `stress_vma_msync()`, `stress_vma_maps()`, `stress_vma_access()`, and optional `stress_vma_pagemap()`.
- `stress_mmapaddr_get_addr()` hunts for an unmapped 32-page address range by probing reads through a pipe and test-mapping pages with `MAP_FIXED | MAP_ANONYMOUS | MAP_SHARED`.

## Control flow
`stress_vma()` maps a shared page and a shared metrics area, synchronizes, then runs `stress_vma_child()` via `stress_oomable_child()`. The child creates `STRESS_VMA_PROCS` synchronized subprocesses. Each subprocess runs `stress_vma_loop()`, which repeatedly chooses a candidate address range, forks another child, and in that child starts a set of pthreads from `vma_funcs`. The thread mix has extra `mmap` and many `access` threads to increase races. Threads run for about 10 seconds, then the child cancels them; the parent also sleeps 10 seconds, clears the continue flag, and kills/reaps the forked child. The supervising child updates bogo operations from the shared mmap counter until global stop.

## State and persistence
State is shared anonymous memory for metrics and one shared page. `stress_vma_continue_flag` controls local thread/process loops. Metrics are intentionally racy counters, not synchronized exact values. The stressor creates no persistent files. `/proc/self/maps` and `/proc/self/pagemap` are read-only integration surfaces when available.

## Dependencies and integration points
The stressor integrates via `stress_vma_info`, `CLASS_VM`, help text, and `max_metrics_items = STRESS_VMA_MAX`. It depends on pthreads, fork synchronization helpers, OOM child handling, signal handlers for `SIGSEGV` and `SIGBUS`, mmap wrappers, kill helpers, scheduler settings, Linux `prctl(PR_SET_VMA_ANON_NAME)` for randomized VMA names, and optional Linux `PAGEMAP_SCAN`. It gracefully registers as unimplemented without pthread support.

## Risks and edge cases
This stressor intentionally causes unstable mappings and catches `SIGSEGV`/`SIGBUS`, so benign faults are expected. `stress_mmapaddr_get_addr()` uses `MAP_FIXED` during probes and must avoid text/heap ranges; incorrect address selection could disturb process memory, though the code probes and unmaps a page at a time. Many operations race against munmap/mprotect, so system-call failures are normal and ignored unless counted. Metric counters are racy by design. Thread cancellation while threads are in syscalls can leave partially updated counters but the process boundary contains damage.

## Test signals
Success is measured by nonzero operation rates for mmaps, munmaps, locks, protects, accesses, `/proc` map reads, signals, and optional pagemap scans. `stress_bogo_set()` mirrors mmap count. Failures are primarily resource skips for mapping shared structures or pthread unavailability; runtime VM syscall errors generally act as stress conditions rather than test failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vma.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vnni.c -->
# sources/test-tools/stress-ng/stress-vnni.c

## Purpose
`stress-vnni.c` implements the `vnni` stressor, exercising vector neural network style integer operations. It uses x86 VNNI/AVX intrinsics when available and generic scalar/vectorized fallbacks otherwise, then verifies results by checksumming deterministic input vectors.

## Important APIs, types, and functions
- `stress_vnni()` is the registered entry point in `stress_vnni_info`.
- `stress_vnni_method_t` maps method names, function pointers, capability checks, endian-specific expected checksums, and whether the method is intrinsic-only.
- Methods include `vpaddb`, `vpdpbusd`, and `vpdpwssd` in generic forms plus optional 128/256/512-bit intrinsic variants guarded by compiler, architecture, intrinsic, and target-clone feature macros.
- Capability helpers include `stress_avx512_bw_capable()`, `stress_avx_vnni_capable()`, `stress_avx512_vnni_capable()`, and `stress_always_capable()`.
- `stress_vnni_exercise()` performs 1024 calls of a selected method, records duration/count metrics, computes `stress_vnni_checksum()`, and compares to expected checksums.

## Control flow
The stressor catches `SIGILL`, initializes deterministic 256-byte `a_init`, `b_init`, and `c_init` buffers with fixed MWC seeds, reads `vnni-method` and `vnni-intrinsic`, computes method capability flags, and skips if the selected method or intrinsic-only request cannot run. After synchronized start, it either repeatedly exercises the selected method or calls `stress_vnni_all()` to iterate all capable non-`all` methods. The loop stops if checksum verification fails or global stress continuation ends. On exit it emits per-method operation-rate metrics for capable methods that ran.

## State and persistence
Global static buffers hold deterministic inputs and the latest result. `stress_vnni_data[]` stores per-method capability and metrics for the worker. `vnni_checksum_okay`, `avx_capable`, `vnni_intrinsic`, and `little_endian` are process-local flags. No persistent state is written.

## Dependencies and integration points
The file depends on stress-ng architecture and CPU feature helpers, target-clone macros, bit rotation, random byte initialization, signal handling for illegal instructions, metric collection, and optional `<immintrin.h>`. It is registered as `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE | CLASS_VECTOR`, exposes method and intrinsic options, and uses `VERIFY_ALWAYS`.

## Risks and edge cases
Intrinsic methods must only execute when CPU and compiler support match; feature checks plus `SIGILL` handling reduce but do not eliminate risk on unusual toolchains or virtualization. The generic fallback allows the stressor to run on systems without VNNI unless `--vnni-intrinsic` is required. Endian-specific checksums avoid false failures across byte order. Since results use global static buffers, this design assumes each stressor worker is a separate process rather than shared threads.

## Test signals
The strongest correctness signal is checksum equality after each 1024-call batch. Failure logs include method name, actual checksum, and expected checksum, then the stressor returns `EXIT_FAILURE`. Capability skips are reported for unavailable selected methods or intrinsic-only runs. Metrics report `<method> ops per sec` using harmonic mean.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-vnni.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-wait.c -->
# sources/test-tools/stress-ng/stress-wait.c

## Purpose
`stress-wait.c` implements the `wait` stressor, exercising process wait APIs while a child is repeatedly stopped and continued by another child. It targets wait-state transitions, signal interruptions, wait variants, and validation of `waitid()` status fields.

## Important APIs, types, and functions
- `stress_wait()` is the registered stressor except on GNU/Hurd, where it is disabled.
- `spawn()` forks a child and runs either `runner()` or `killer()`.
- `runner()` pauses until stopped/continued and exits when stress should stop.
- `killer()` repeatedly sends `SIGSTOP` and `SIGCONT` to the runner and uses `SIGUSR1`/`SIGALRM` to unblock or wake the parent when waits stall.
- `stress_wait_continued()` increments bogo operations for continued events when `WIFCONTINUED` is available.
- `syscall_shim_waitpid()` prefers the raw `waitpid` syscall when available.

## Control flow
After installing a `SIGUSR1` ignore handler and synchronizing, the stressor spawns a runner child and a killer child. The main loop cycles through `waitpid`, `wait`, optional `wait3`, optional `wait4` with several PID forms, invalid `wait4` calls, and optional `waitid`. It treats `EINTR` and `ECHILD` as expected race outcomes, but logs unexpected errors. `waitid()` results are checked for expected PID, signal number, status, and `si_code`. On shutdown it deinitializes state, kills/reaps the killer, then kills/reaps the runner.

## State and persistence
State is limited to the runner PID, killer PID, wait status values, optional `rusage`, and bogo count. No persistent files or shared memory are used. The killer observes parent progress through `stress_bogo_get(args)` and sends signals if the parent appears blocked too long.

## Dependencies and integration points
The stressor integrates through `stress_wait_info`, `CLASS_SCHEDULER | CLASS_OS`, and `VERIFY_ALWAYS`. It depends on stress-ng fork retry, kill/reap, signal, pause, scheduler-yield, and parent-death helpers. Build-time guards include GNU/Hurd disablement and optional wait-family APIs.

## Risks and edge cases
Race conditions are central: waits may consume state in a different API than expected, return `ECHILD`, or be interrupted. The `ABORT_TIMEOUT` path prevents indefinite blocking by signaling the parent. Heavy load can produce `waitid()` with `si_pid == 0`, which the code explicitly tolerates. Because multiple wait APIs observe the same child state, failures must distinguish real API errors from expected races.

## Test signals
Bogo increments primarily indicate observed continued events. Failure signals include unexpected errors from wait APIs, inconsistent `waitid()` PID/signo/status/code, and fork failures. The unimplemented path on GNU/Hurd documents a kernel assertion risk.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-wait.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-waitcpu.c -->
# sources/test-tools/stress-ng/stress-waitcpu.c

## Purpose
`stress-waitcpu.c` implements `waitcpu`, a CPU instruction stressor that repeatedly executes architecture-specific wait, pause, yield, barrier, or no-op instructions. It measures instruction rates and checks that wait-like instructions are not implausibly faster than `nop` on non-virtualized x86 systems.

## Important APIs, types, and functions
- `stress_waitcpu()` is the registered entry point.
- `stress_waitcpu_method_t` stores method name, function pointer, support probe, support flag, count, duration, and rate.
- Supported methods are built conditionally: generic `nop`; x86 `pause`, `tpause0/1`, `umwait0/1`; ARM `yield`; OpenRISC `psync`; PPC/PPC64 `yield`, `mdoio`, `mdoom`; RISC-V `pause`; Loong64 `dbar`.
- x86 waitpkg methods use `rdtsc`, `tpause`, `umonitor`, and `umwait` with adaptive static delay values.

## Control flow
At startup the stressor probes every compiled method, builds a string of supported instructions, and skips if none are supported. After synchronized start, it loops over supported methods, executing each 1000 times per pass, measuring elapsed time, accumulating counts/durations, and incrementing bogo operations. On exit it computes per-method rates, records metrics, and on x86 compares non-nop rates to `nop` when `/proc/cpuinfo` does not indicate a hypervisor.

## State and persistence
All state lives in the static method table and per-function static delay variables for waitpkg instructions. Counts, durations, and rates are reset at stressor start. There is no persistent state. `/proc/cpuinfo` is read only for the x86 sanity note.

## Dependencies and integration points
The file integrates via `stress_waitcpu_info`, `CLASS_CPU`, `VERIFY_ALWAYS`, and help text. It depends heavily on architecture-specific stress-ng assembly wrappers and CPU feature probes. Build-time guards keep unsupported instruction families out of the method table.

## Risks and edge cases
Some wait instructions require CPU feature support and may behave differently under virtualization or power-management settings. The code avoids hard failure for suspicious rates and emits an informational note instead. `nop` support depends on `HAVE_ASM_NOP`; if even that is absent and no arch-specific methods compile in, the stressor skips as no-resource. Static delay adaptation in `tpause`/`umwait` is intentionally process-local and approximate.

## Test signals
Metrics report `<instruction> ops per sec`. Instance zero logs the supported instruction list. On non-virtualized x86, an informational signal is emitted if a wait instruction rate exceeds `nop` by more than about 50 percent. Main failure mode is lack of supported instructions, returned as `EXIT_NO_RESOURCE`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-waitcpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-watchdog.c -->
# sources/test-tools/stress-ng/stress-watchdog.c

## Purpose
`stress-watchdog.c` implements the Linux `watchdog` stressor, exercising `/dev/watchdog` open/close and common watchdog ioctls while carefully trying to avoid leaving the hardware watchdog armed. It is marked pathological because misuse of watchdog devices can reboot systems.

## Important APIs, types, and functions
- `stress_watchdog()` is the entry point when `linux/watchdog.h` is available.
- `stress_watchdog_magic_close()` writes `"V"` to the watchdog descriptor to request magic close disablement on drivers that support it.
- `stress_watchdog_handler()` handles many fatal/interruption signals, performs magic close, and clears the global continue flag.
- The loop uses `open("/dev/watchdog", O_RDWR)`, `ioctl()` calls for `WDIOC_KEEPALIVE`, `WDIOC_GETTIMEOUT`, `WDIOC_GETPRETIMEOUT`, `WDIOC_GETTIMELEFT`, `WDIOC_GETSUPPORT`, `WDIOC_GETSTATUS`, `WDIOC_GETBOOTSTATUS`, and `WDIOC_GETTEMP`, plus `close()`.

## Control flow
The stressor installs the watchdog handler for a list of signals, checks `/dev/watchdog` existence and read/write access, and skips successfully if absent or inaccessible. It then synchronizes and repeatedly tries to open the device. If another worker or process holds it, it nanosleeps briefly and retries. Once open, it writes the magic close byte, issues supported keepalive/status/time/temp ioctls, validates that returned timeout/temp values are not negative when calls succeed, writes magic close again, closes the descriptor, yields, and increments bogo operations.

## State and persistence
The only cross-function state is static/global `fd` and `jmp_env`, plus the process continue flag. No persistent files are written, but the stressor interacts with a persistent kernel device whose state may outlive the process if magic close is unsupported or close fails.

## Dependencies and integration points
The stressor integrates via `stress_watchdog_info`, `CLASS_OS | CLASS_PATHOLOGICAL`, and `VERIFY_ALWAYS`. It depends on Linux watchdog UAPI headers and stress-ng signal helpers. Without `linux/watchdog.h`, it registers as unimplemented.

## Risks and edge cases
The major risk is arming a real watchdog and failing to disable it. The code mitigates this by checking permissions, writing `"V"` before and after ioctls, handling many signals, and closing the fd. However, not all drivers support magic close, and a crash between open and close could have hardware consequences. Multiple stressor instances contend on an exclusive device and may spin opening. Negative timeout/temperature values are treated as verification failures.

## Test signals
Successful bogo operations mean an open/ioctl/close cycle completed. Skips for missing or inaccessible `/dev/watchdog` return success rather than failure. Verification failures are negative timeout/pretimeout/timeleft/temperature values or close failure. Build-time absence of watchdog headers yields an unimplemented reason.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-watchdog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-wcs.c -->
# sources/test-tools/stress-ng/stress-wcs.c

## Purpose
`stress-wcs.c` implements the `wcs` stressor for libc wide-character string functions. It generates randomized wide strings and repeatedly calls comparison, copy, concatenation, search, length, collation, and transform APIs, optionally verifying basic semantic expectations.

## Important APIs, types, and functions
- `stress_wcs()` is the registered entry point when enough wide-character APIs are available.
- `stress_wcs_args_t` carries function pointer, method name, source/destination buffers, lengths, and failure flag.
- `stress_wcs_method_info_t` maps method names to wrapper functions and libc function pointers.
- `stress_wrndstr_case()` fills strings with randomized upper/lower alphabets that intentionally exclude `'+'` for search tests.
- Method wrappers cover `wcscasecmp`, `wcsncasecmp`, `wcslcpy` or `wcscpy`, `wcslcat` or `wcscat`, `wcsncat`, `wcschr`, `wcsrchr`, `wcscmp`, `wcsncmp`, `wcslen`, `wcscoll`, and `wcsxfrm`, depending on platform macros.
- `WCSCHK`/`wcschk()` report verification failures only when global verify mode is enabled.

## Control flow
The stressor selects a method from `wcs-method` or defaults to `all`, initializes buffers and metrics, generates `str1`, synchronizes, then loops while stress continues. Each iteration regenerates `str2` with alternating character case, calls the selected method wrapper, periodically times calls for metrics, swaps `str1`/`str2` and their lengths, and increments bogo operations. The `all` method rotates through all real methods one at a time, timing each method separately. At deinit it emits per-method calls-per-second metrics for methods with timing data and returns failure if any verification check failed.

## State and persistence
State is local stack buffers (`str1`, `str2`, `strdst`), the `info` struct, static metrics array, and a static rotating index in `stress_wcs_all()`. No persistent state is written. The random string content changes each iteration, while `str1`/`str2` swapping broadens input combinations.

## Dependencies and integration points
The file integrates via `stress_wcs_info`, `CLASS_CPU | CLASS_CPU_CACHE | CLASS_MEMORY`, `VERIFY_OPTIONAL`, method option parsing, and metric reporting. It depends on platform wide-char headers, optional BSD `wchar.h`, libc function availability macros, and stress-ng random and metrics helpers. Some methods are excluded for static builds, PCC, or m68k where appropriate.

## Risks and edge cases
Wide-character API availability varies significantly by libc and platform. The fallback between `wcslcpy`/`wcscpy` and `wcslcat`/`wcscat` changes exact semantics under the same stressor method slot. Verification checks are basic and assume generated strings differ as intended; the alphabets are designed to avoid accidental `'+'` hits and keep case classes distinct. Collation behavior can be locale-sensitive, so checks only require nonzero for different generated strings, not a specific order.

## Test signals
Verification failures set `info.failed` and produce `did not return expected result` messages under verify mode. Metrics report `<method> calls per sec`. If fewer than two methods are compiled in, the stressor delegates to `stress_unimplemented()`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-wcs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-workload.c -->
# sources/test-tools/stress-ng/stress-workload.c

## Purpose
`stress-workload.c` implements the `workload` stressor, which schedules bursts of configurable synthetic work within time slices. It is intended to exercise scheduler behavior, timing jitter, optional scheduler policies, POSIX message queues, pthread fan-out, and the shared workload-method engine from `core-workload`.

## Important APIs, types, and functions
- `stress_workload()` is the registered entry point in `stress_workload_info`.
- `stress_workload_t` stores a work item start offset and run duration. `stress_workload_bucket_t` records histogram buckets for observed slice offsets.
- `workload_dists[]` exposes cluster, even, poisson, random1, random2, and random3 timing distributions.
- Options include `workload-dist`, `workload-load`, `workload-method`, `workload-quanta-us`, `workload-sched`, `workload-slice-us`, and `workload-threads`.
- `stress_workload_set_sched()` applies optional scheduling policy, including Linux `SCHED_DEADLINE` through `sched_setattr` when available.
- `stress_workload_exercise()` generates and sorts work items, sleeps/yields until each scheduled offset, accounts observed start offset, runs `stress_workload_waste_time()`, and optionally dispatches work to pthreads via POSIX message queues.

## Control flow
The stressor reads settings, warns when quanta are below timer slack, maps a shared work buffer sized for the main worker plus any requested threads, optionally creates a POSIX message queue and pthread workers, validates quanta versus slice size, allocates a work-item array, initializes the offset histogram, applies scheduler policy, synchronizes, then repeatedly calls `stress_workload_exercise()`. Each exercise pass builds offsets according to the selected distribution, sorts by start time, runs/sends work at the scheduled times inside the slice, increments bogo per quanta, and sleeps to the end of the slice. On shutdown it reports the start-time histogram from instance zero, cancels/joins threads, closes/unlinks the message queue, and unmaps the buffer.

## State and persistence
State includes the mapped anonymous work buffer, heap-allocated work-item array, histogram counters, optional global `stress_workload_threads[]`, POSIX message queue name/descriptor, and per-thread buffers. The only kernel-persistent object is the message queue, which is unlinked during cleanup. No repository files are written.

## Dependencies and integration points
This stressor integrates with stress-ng scheduler option tables, workload method registry (`core-workload.h`), mmap helpers, madvise helpers, pthread helpers, POSIX mqueue support, timing wrappers, sorting wrapper, and metrics/debug output. It is registered as `CLASS_SCHEDULER | CLASS_OS` with `VERIFY_ALWAYS`.

## Risks and edge cases
Threaded mode requires pthreads, librt, POSIX mqueues, and mqueue headers; otherwise it falls back to single-process mode with an informational message. Message queue creation failure skips as no resource. Real-time scheduling may fail with `EPERM` and is tolerated. Invalid `workload-quanta-us > workload-slice-us` is a hard failure. Timing quality depends on kernel timer slack, scheduler policy, system load, and `stress_workload_waste_time()` behavior. Thread cancellation must occur after mqueue use to avoid leaking workers.

## Test signals
Bogo operations count scheduled quanta. Instance zero logs thread count and a histogram of observed work start times within the slice. Resource signals include mmap, mqueue, pthread, and calloc failures. Scheduler policy failures are informational except invalid priority range or quanta/slice settings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-workload.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-x86cpuid.c -->
# sources/test-tools/stress-ng/stress-x86cpuid.c

## Purpose
`stress-x86cpuid.c` implements the x86-only `x86cpuid` stressor, repeatedly executing many CPUID leaves and subleaves to stress the instruction, firmware/virtualization CPUID handling, and consistency of selected stable leaves.

## Important APIs, types, and functions
- `stress_x86cpuid()` is the entry point when `STRESS_ARCH_X86` is defined.
- `stress_cpuid_regs_t` defines an input `eax`, input `ecx`, and whether that leaf should be verified for stable output.
- `stress_cpuid_saved_regs_t` stores output register snapshots.
- `stress_cpuid_regs[]` contains a broad fixed leaf list covering standard, extended, hypervisor, AMD, Centaur, Xeon Phi, AVX10, topology, cache, power, SGX, RDT, and other CPUID spaces.
- `stress_x86cpuid_reorder_regs()` shuffles leaf order each pass using stress-ng random helpers.

## Control flow
After synchronized start, each outer loop shuffles the CPUID leaf list. For leaves marked `verify`, it first captures baseline output registers in table order. It then times 1024 sweeps over the shuffled leaf list, executing `stress_asm_x86_cpuid()` for each and incrementing bogo once per sweep. After the timed block, it re-executes verified leaves in table order and compares all four output registers to the saved baseline. The loop stops on verification failure or global stop, then reports nanoseconds per CPUID instruction.

## State and persistence
State is local to the worker: shuffled leaf array, saved register array, timing counters, and return code. No persistent state is written. The input leaf table is static const.

## Dependencies and integration points
The stressor integrates via `stress_x86cpuid_info`, `CLASS_CPU`, `VERIFY_ALWAYS`, and help text. It depends on stress-ng x86 assembly wrappers and pragma unrolling. Non-x86 builds register an unimplemented stressor with an explicit reason.

## Risks and edge cases
Some CPUID leaves can legitimately vary due to CPU hotplug, virtualization, microcode behavior, counters, or topology changes, so only selected leaves are verified. The leaf table includes unusual/vendor/hypervisor ranges; unsupported leaves should still return architecturally safe values, but hypervisors may emulate them inconsistently. Shuffling helps catch order-dependent emulation issues.

## Test signals
Failures are register mismatches on verified leaves, with logs naming input `eax`/`ecx`, actual register, and expected register. Metrics report `nanosecs per cpuid instruction`. Success requires all verified leaves remain stable for the run.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-x86cpuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-x86syscall.c -->
# sources/test-tools/stress-ng/stress-x86syscall.c

## Purpose
`stress-x86syscall.c` implements the Linux x86-64 `x86syscall` stressor, directly exercising the `syscall` instruction through hand-written inline-assembly wrappers for simple system calls. It measures syscall cost excluding test-loop overhead and verifies selected direct syscall results against libc wrappers.

## Important APIs, types, and functions
- `stress_x86syscall()` is the registered entry point on Linux x86-64 with non-PCC compilers.
- `stress_x86syscall_supported()` checks x86 CPU identity, `syscall` instruction support, and availability of at least one relevant `__NR_*` definition.
- Inline wrappers `x86_64_syscall0()`, `x86_64_syscall1()`, `x86_64_syscall2()`, and `x86_64_syscall3()` place arguments in Linux x86-64 syscall registers and execute `syscall`.
- Per-call wrappers include `getcpu`, `geteuid`, `getgid`, `getpid`, `gettimeofday`, `getuid`, and `time` when their syscall numbers exist.
- `x86syscall_check_x86syscall_func()` implements `x86syscall-func` filtering and validates requested names.

## Control flow
The stressor initially marks all compiled syscall wrappers enabled, applies optional function filtering, logs the selected list from instance zero, compacts enabled function pointers into an aligned local array, synchronizes, then loops calling each selected wrapper and adding the count to bogo operations. It times this real syscall phase. It then replaces function pointers with `wrap_dummy()`, runs a short overhead measurement loop, restores the original bogo count, and records nanoseconds per call excluding measured harness overhead plus the overhead metric itself. Finally it verifies direct `getpid`, `getgid`, `getuid`, `geteuid`, `time`, and `gettimeofday` results against libc where available.

## State and persistence
Static state consists of the syscall mapping table and `x86syscalls_exercise[]` selection flags. Runtime state includes local function pointer arrays and timing counters. No persistent state is written.

## Dependencies and integration points
The file integrates via `stress_x86syscall_info`, `CLASS_OS`, `VERIFY_ALWAYS`, `x86syscall-func` option parsing, and a `.supported` callback. It depends on Linux syscall numbers, x86-64 ABI register conventions, stress-ng CPU feature probes, timing helpers, metric reporting, and libc wrappers used for verification. Unsupported platforms register as unimplemented.

## Risks and edge cases
The inline wrappers set `errno` incorrectly for Linux negative syscall returns: they assign the negative return value directly rather than `-ret`, which can leave negative errno values. Most exercised calls should succeed, so this is mainly a risk for future failing wrappers. The support message says "Intel CPU" although the check is generic x86. Overhead subtraction can produce misleading negative or tiny values if timing noise exceeds syscall cost. Direct `time`/`gettimeofday` comparisons allow the direct syscall value to be equal or later than libc, but fail if it appears earlier.

## Test signals
Metrics report `nanosecs per call (excluding test overhead)` and `nanosecs for test overhead`. Verification failures compare direct syscall results with libc for PID/GID/UID/EUID and monotonic wall-clock expectations for time calls. Invalid `x86syscall-func` input prints the valid names and returns failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-x86syscall.c -->
