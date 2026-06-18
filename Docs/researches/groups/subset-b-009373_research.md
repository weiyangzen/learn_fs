# subset-b-009373 research

Grouped research report for stress-ng stressors under `sources/test-tools/stress-ng`. Each section preserves the source path in the title and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockbus.c -->
# sources/test-tools/stress-ng/stress-lockbus.c

Purpose: implements the `lockbus` CPU/cache/memory stressor. It repeatedly performs locked atomic memory operations against local and shared mappings, with optional split-lock activity on x86, to create cache-line, bus-lock, and memory-ordering pressure.

Important APIs/types/functions: the stressor is registered through `stress_lockbus_info`; options are `lockbus-bytes` and `lockbus-nosplit`. `stress_lockbus_init()` allocates a shared anonymous mapping and rounds the configured byte count to a two-page boundary; `stress_lockbus_deinit()` unmaps it. `stress_lockbus()` allocates a per-worker local mapping, installs SIGBUS/SIGILL handlers, probes misaligned and x86 split-lock behavior, optionally NUMA-randomizes pages, then loops over `MEM_LOCK`, `__atomic_*`/inline x86 `lock addl`, and optional compare-and-swap operations.

Control flow: initialization creates shared state before worker execution. A worker maps local data, tests whether unsupported misaligned/split locks trap or hang, synchronizes with other workers, then alternates random local/shared pointer selection with bursts of locked increments, locked no-op additions, and compare-and-swap pairs. Cleanup deletes timers and unmaps local memory.

State and persistence: persistent process state is limited to static capability flags (`do_misaligned`, `do_splitlock`, `do_sigill`) and the shared mapping. No filesystem state is created. Metrics report nanoseconds per memory lock operation.

Dependencies and integration: depends on `core-arch`, `core-mmap`, `core-numa`, compiler atomics or x86 inline assembly, `sigsetjmp`, and optional POSIX timers. It integrates with the stress-ng option registry, proc-state synchronization, NUMA helpers, memory usage accounting, and stressor metrics.

Risks: intentionally triggers SIGBUS/SIGILL on some systems and can hang old kernels without the timer escape. Split locks can be extremely slow or blocked by kernel policy. Incorrect pointer bounds would corrupt mapped memory, so page/size rounding and `CHUNK_SIZE` margins are key.

Test signals: successful build on supported architectures, skip path on unsupported atomics/siglongjmp, expected debug messages for enabled/disabled misaligned/split locks, no leaked mappings, and a nonzero lock-operation metric.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockf.c -->
# sources/test-tools/stress-ng/stress-lockf.c

Purpose: implements the `lockf` filesystem/OS stressor. It creates contention on byte-range advisory locks in a shared temporary file using `lockf()`, exercising blocking or nonblocking acquisition, unlock, and test paths.

Important APIs/types/functions: `stress_lockf_info_t` records a held lock offset; `stress_lockf_info_list_t` tracks active and reusable records. `stress_lockf_info_new()`, `stress_lockf_info_head_remove()`, and `stress_lockf_info_free()` maintain that list. `stress_lockf_unlock()` seeks to the oldest offset and unlocks it. `stress_lockf_contention()` repeatedly selects random offsets and calls `lockf(F_LOCK)` or `lockf(F_TLOCK)`. `stress_lockf()` owns temp file setup, child fork, synchronization, cleanup, and registration via `stress_lockf_info`.

Control flow: the worker creates a temp directory and a 64 KiB lock file, fills it with zeroed data, then forks a child pinned near the parent CPU. Parent and child both call the contention loop on the same file descriptor until the stressor stops. Held locks are capped at `LOCK_MAX`; when full, the oldest lock is released before acquiring another.

State and persistence: held lock metadata is per-process static list state with a free list for reuse. Temporary directory/file state is removed at shutdown. The child is killed and waited from the parent cleanup path.

Dependencies and integration: gated by `HAVE_LOCKF`. Uses stress-ng temp-file helpers, affinity helpers, fork retry/kill helpers, scheduler application, bogo counters, and `VERIFY_ALWAYS`.

Risks: `lockf` semantics vary over filesystems and are process-associated, so forked descriptor sharing and lock lifetime are important. Unlock failure aborts because retrying the same stale list head could loop forever. File creation races are expected and only non-`EEXIST` mkdir failures are fatal.

Test signals: valid runs show bogo increments under contention, deterministic cleanup of temp files, no growth beyond `LOCK_MAX`, and expected skip/unimplemented behavior when `lockf()` is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockmix.c -->
# sources/test-tools/stress-ng/stress-lockmix.c

Purpose: implements `lockmix`, a mixed advisory-lock stressor that exercises `flock`, POSIX record locks, `lockf`, and open-file-description locks when available. It is intended to find interactions and contention issues between lock implementations.

Important APIs/types/functions: compile-time feature macros enable lock families. `stress_lockmix_info_t` records offset, length, pid, and lock type for each held lock. List helpers allocate/recycle held-lock records. `stress_lockmix_unlock()` dispatches the correct unlock operation for the oldest record. Timer helpers use POSIX timers or `setitimer()` to bound blocking lock operations. `stress_lockmix_contention()` randomly chooses a lock type and byte range and records successful acquisitions.

Control flow: `stress_lockmix()` creates and fills a 1 MiB shared lock file, builds a weighted randomized lock-type table, starts a short timeout facility, synchronizes, forks a child, and runs the same contention loop in parent and child. On exit it deletes timers, kills the child if needed, frees lock records, closes/unlinks the file, and removes the temp directory.

State and persistence: in-process state is the held-lock linked list plus timer validity flags. Temporary filesystem state is removed. Lock records are intentionally popped before unlock syscalls so an unlock failure does not trap cleanup on one stale record forever.

Dependencies and integration: uses `flock`, `fcntl(F_SETLK/F_OFD_SETLK)`, `lockf`, timers, temp-file helpers, affinity, fork/kill helpers, and stress-ng synchronization. Registration uses `VERIFY_ALWAYS`.

Risks: mixing lock families can expose filesystem-specific behavior and blocking surprises. Timeout signals are ignored to interrupt long waits, but timer availability varies. OFD locks use `l_pid = 0`, while POSIX locks store `args->pid`; confusing these would weaken the test.

Test signals: startup should report enabled lock types, bogo operations should continue under contention, timeout timers should be deleted, temp files should be removed, and the unimplemented path should appear if no lock family is compiled in.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockmix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockofd.c -->
# sources/test-tools/stress-ng/stress-lockofd.c

Purpose: implements `lockofd`, a focused open-file-description locking stressor. It stresses Linux/OFD `fcntl()` lock operations over random byte ranges in a shared file.

Important APIs/types/functions: `stress_lockofd_info_t` stores offset and length for each held OFD lock. The list helpers mirror other lock stressors: allocate/reuse records, remove the head, and free active/free lists. `stress_lockofd_unlock()` issues `fcntl(fd, F_OFD_SETLK, F_UNLCK)`. `stress_lockofd_contention()` creates random write locks with `F_OFD_SETLK`. `stress_lockofd()` sets up the temp file, forks a contending child, and registers `stress_lockofd_info`.

Control flow: after creating a 1 MiB temp file, the stressor fills it, synchronizes, forks, and runs parent/child contention loops against the same file description. Each loop keeps at most `LOCK_MAX` held ranges, unlocking the oldest when the list is full. Failed lock attempts are normal and simply continue.

State and persistence: only the per-process lock list persists across iterations. Temporary file and directory are unlinked at shutdown. The child process is killed and waited during cleanup.

Dependencies and integration: gated by `F_OFD_GETLK`, `F_OFD_SETLK`, `F_OFD_SETLKW`, `F_WRLCK`, and `F_UNLCK`. Uses stress-ng temp-file, affinity, fork retry, scheduler, process-state, and kill helpers. Classified as filesystem/OS and always verified.

Risks: OFD lock support is Linux-specific and absent on older libc/kernel combinations. Since locks are tied to open file descriptions rather than process IDs, sharing descriptors across fork is intentional and must not be “simplified” away. As with related lock stressors, unlink/close cleanup must happen even after contention failures.

Test signals: build-time unimplemented path on missing OFD constants, successful file setup and removal, bogo increments while locks contend, and no retained lock records after parent/child exit.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lockofd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-logmath.c -->
# sources/test-tools/stress-ng/stress-logmath.c

Purpose: implements `logmath`, a CPU/floating-point stressor for logarithmic math functions. It exercises real and complex `log`, `logb`, `log10`, and `log2` variants across float, double, and long double forms where available.

Important APIs/types/functions: `stress_logmath_method_t` maps method names to function pointers. Individual `stress_logmath_*()` functions run `STRESS_LOGMATH_LOOPS` calls, accumulate a sum, and compare future runs with the first result using `PRECISION` or `PRECISION_L`. `stress_logmath_exercise()` times one method and updates per-method metrics. `stress_logmath_all()` iterates all concrete methods. Options use `logmath-method`; registration sets `VERIFY_ALWAYS` and reserves metric slots.

Control flow: the selected method defaults to `all`. After sync, the stressor repeatedly calls `stress_logmath_exercise()`. Any result drift beyond tolerance logs a failure and exits with failure. At deinit, it emits per-function operations-per-second metrics for all methods that ran.

State and persistence: each method uses static `first_run` and `result` variables as deterministic baselines. Metrics are static arrays reset at the start of each stressor run. No filesystem or kernel state is modified.

Dependencies and integration: depends on `<math.h>`, optional `<complex.h>`, stress-ng shim math wrappers, target clone optimization, pragma unrolling, option method lookup, and metrics. It compiles to `stress_unimplemented` if no supported log function exists.

Risks: platform libm differences, excess precision, compiler optimizations, and complex math availability can affect reproducibility. Static baselines are shared within the process, so changing loop inputs or precision thresholds requires care.

Test signals: method option enumeration, nonzero per-method metrics, failure messages on mismatched sums, and correct unimplemented option behavior on minimal libm builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-logmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-longjmp.c -->
# sources/test-tools/stress-ng/stress-longjmp.c

Purpose: implements `longjmp`, a CPU/hot stressor for `setjmp()`/`longjmp()` behavior. It repeatedly jumps out of leaf functions and checks that the saved jump buffer is not corrupting adjacent memory.

Important APIs/types/functions: `jmp_buf_check_t` wraps a timestamp, canary before the `jmp_buf`, the `jmp_buf`, and a canary after it. `stress_longjmp_sample_func()` records a timestamp then longjmps; `stress_longjmp_func()` longjmps without timing. `stress_longjmp()` runs the setjmp loop, validates canaries, tracks sampled timing, and registers metrics.

Control flow: after synchronization, `setjmp()` establishes the return point. The first jump in each 1000-call sample period records timing and increments bogo operations; the intervening jumps reduce timing overhead. The loop continues by calling one of the no-return jump functions until the global stop condition is false.

State and persistence: static state includes canaries, total sampled time, sample count, and `sample_counter`. There is no external state. The metric is nanoseconds per sampled longjmp call.

Dependencies and integration: relies on standard `jmp_buf`, stress-ng timing, bogo counters, process-state synchronization, and `VERIFY_ALWAYS`. The functions are marked `NOINLINE`, `NORETURN`, and low optimization to preserve call shape.

Risks: the stressor is intentionally sensitive to ABI/compiler behavior around nonlocal jumps and automatic variable clobbering. The canary check catches overwrites adjacent to `jmp_buf`, not all possible stack/register restoration issues.

Test signals: bogo operations increment, metrics appear when sample count is nonzero, no “memory corrupted before/after jmpbuf” failures, and no path reaches the post-`longjmp()` `_exit()` guards.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-longjmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-loop.c -->
# sources/test-tools/stress-ng/stress-loop.c

Purpose: implements `loop`, a privileged Linux loopback-device stressor. It creates backing files, attaches them to `/dev/loop*`, exercises loop ioctls, sysfs attributes, mmap I/O, direct I/O, status changes, capacity changes, and invalid ioctl paths.

Important APIs/types/functions: `stress_loop_supported()` requires `CAP_SYS_ADMIN`. `stress_loop()` owns the full device lifecycle. It uses `/dev/loop-control` ioctls such as `LOOP_CTL_ADD`, `LOOP_CTL_GET_FREE`, `LOOP_CTL_REMOVE`, device ioctls such as `LOOP_SET_FD`, `LOOP_CLR_FD`, `LOOP_GET_STATUS`, `LOOP_SET_STATUS`, `LOOP_GET_STATUS64`, `LOOP_SET_CAPACITY`, `LOOP_SET_BLOCK_SIZE`, `LOOP_SET_DIRECT_IO`, `LOOP_CHANGE_FD`, and `LOOP_CONFIGURE`.

Control flow: the stressor creates an unlinked backing file of `loop-bytes`, synchronizes, then repeatedly obtains or creates a loop device, opens it, attempts invalid backing fd association, associates the real backing file, reads sysfs loop attributes, writes and reads data, maps the loop device, applies status/flag operations, tests resize/block-size/direct-I/O/change-fd/configure paths, clears the association, removes the loop device, and increments bogo ops.

State and persistence: temporary backing files are unlinked early and directories are removed at exit. Kernel loop devices are removed with retries to handle `EBUSY`. Memory usage is reported from configured backing size.

Dependencies and integration: gated by `linux/loop.h` and loop ioctl constants. Integrates with capability checks, temp-file helpers, mincore/mmap helpers, memory accounting, and `VERIFY_ALWAYS`.

Risks: requires root-like privileges and mutates kernel loop-device state. Cleanup robustness matters because leaked loop devices can affect the host. Some intentionally invalid block sizes or ioctls may produce kernel warnings while being expected test coverage.

Test signals: skip without `CAP_SYS_ADMIN`, successful loop attach/detach/remove, no leaked `/dev/loopN`, valid handling of `EBUSY` retries, and bogo increments after each lifecycle pass.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-loop.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lsearch.c -->
# sources/test-tools/stress-ng/stress-lsearch.c

Purpose: implements `lsearch`, a CPU/cache/memory/search stressor for linear search and insertion. It compares libc `lsearch`/`lfind` with local non-libc and sentinel implementations.

Important APIs/types/functions: function pointer typedefs abstract `lfind` and `lsearch`. `lfind_nonlibc()` walks elements linearly; `lsearch_nonlibc()` appends absent keys. `lfind_sentinel()` temporarily copies the key into the last slot to avoid an end check during search, then restores the saved value. `stress_lsearch_cmp_int32()` increments the global sort-compare counter. `stress_lsearch()` configures size/method, allocates `data` and `root`, shuffles input, inserts, searches, verifies optional correctness, and emits metrics.

Control flow: each iteration shuffles the source array, populates the root array through the chosen `lsearch` implementation, resets comparison counters, times `lfind` over inserted elements, optionally verifies returned pointers/values, accumulates comparison count and item count, and increments bogo operations.

State and persistence: state is heap-allocated arrays for the run plus global sort comparison counters. No external state persists. Metrics report comparisons per second and comparisons per item.

Dependencies and integration: uses optional `<search.h>`, stress-ng sort helpers, method option lookup, maximize/minimize sizing, bogo counters, and optional verification.

Risks: the sentinel implementation mutates the final element while searching; restoration must be correct or verification will detect data corruption. Large `lsearch-size` values can consume significant memory and produce long O(n^2) work. The comparator returns nonzero rather than ordering, matching linear-search equality semantics.

Test signals: successful allocation or `EXIT_NO_RESOURCE`, method enumeration, optional verification with no missing/mismatched elements, and metrics with comparison rates.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lsm.c -->
# sources/test-tools/stress-ng/stress-lsm.c

Purpose: implements `lsm`, a Linux security-module syscall stressor. It exercises `lsm_list_modules`, `lsm_get_self_attr`, and negative `lsm_set_self_attr` cases.

Important APIs/types/functions: shim wrappers call `__NR_lsm_list_modules`, `__NR_lsm_get_self_attr`, and `__NR_lsm_set_self_attr` directly. `stress_lsm()` allocates a 32-page buffer, lists active LSM module IDs, fetches self attributes for available `LSM_ATTR_*` constants, scans returned `struct lsm_ctx` entries, and records call-rate metrics.

Control flow: after mapping and synchronization, each iteration calls `lsm_list_modules()` with valid arguments and then with invalid flags and NULL ids to check expected errors. It loops over supported attributes, calls `lsm_get_self_attr()`, classifies returned ids as undefined/reserved/defined, then exercises invalid attr, invalid context pointer, invalid flags, and an invalid negative `ctx_len` set operation.

State and persistence: state is the temporary mmap buffer and booleans recording which ID categories were observed. No LSM configuration is intentionally changed; `set_self_attr` is used with invalid data as a negative test.

Dependencies and integration: gated by Linux syscall numbers and `linux/lsm.h`. Uses stress-ng mmap helpers, timing/metrics, proc-state sync, and debug logging.

Risks: syscall availability depends on kernel version and config. Expected errno values are part of the test surface; future kernel ABI changes could make current negative checks too strict. Buffer walking must respect `ctx_end` because `ctx_len` is kernel-provided.

Test signals: skip on `ENOSYS`, failures when invalid calls unexpectedly succeed or return unexpected errno, rates for list/get calls, and debug output summarizing observed LSM ID classes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-madvise.c -->
# sources/test-tools/stress-ng/stress-madvise.c

Purpose: implements `madvise`, a VM/OS stressor for page advice, process advice, proc-map reads, mapping churn, and selected invalid-advice/error paths.

Important APIs/types/functions: `madvise_ctxt_t` carries mapping, size, proc paths, threading, and hardware-poison configuration. `stress_sigbus_handler()` recovers from SIGBUS via `siglongjmp`. `stress_random_advise()` chooses and validates advice, carefully limiting `MADV_HWPOISON`/`MADV_SOFT_OFFLINE`. `stress_madvise_pages()` applies advice sequentially and randomly across pages, reads `/proc/$pid/smaps` and `maps`, tests invalid advice/address cases, and handles locked-page cases. `stress_process_madvise()` exercises pidfd-based advice.

Control flow: the stressor maps a guard page, creates and unlinks a temp backing file, fills it, then repeatedly maps either file-backed or anonymous memory. It initializes/touches/randomizes pages, calls process-level advice, runs page advice from worker threads when pthreads exist, tests zero-size/invalid-size/invalid-advice calls, optionally checks `MADV_FREE` races, unmaps, tests unmapped/wrapped addresses, cycles through advice options on `NULL,0`, and increments bogo ops.

State and persistence: temporary backing file state is unlinked and directory removed. Static SIGBUS count and hardware-poison counters persist within the process. Metrics are mostly informational counts/logs rather than per-advice rates.

Dependencies and integration: depends on `madvise`, optional pthreads, pidfd/process_madvise shims, core madvise option tables, mincore, mmap, OOM adjustment, and temp-file helpers.

Risks: hardware poisoning is destructive to free memory and is deliberately opt-in and capped. `MADV_GUARD_INSTALL`, `MADV_HWPOISON`, and file-backed advice can raise SIGBUS or alter page contents. Expected invalid-call behavior varies by kernel.

Test signals: no unrecovered SIGBUS, bounded mmap retry count, optional MADV_FREE race log, skip on missing resources, and successful cleanup of mappings/files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-madvise.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-malloc.c -->
# sources/test-tools/stress-ng/stress-malloc.c

Purpose: implements `malloc`, a memory/VM/OS stressor for allocator churn. It mixes allocation, reallocation, freeing, aligned allocation APIs, optional page touching, mlock, trimming, cache flushing, zero-on-free, pthread concurrency, and OOM handling.

Important APIs/types/functions: `stress_malloc_info_t` stores allocation pointer and length. `stress_malloc_args_t` carries per-thread status. `stress_alloc_action()` records the current allocator action for crash diagnostics. `stress_malloc_page_touch()` populates pages through writes or mincore helper. `stress_malloc_loop()` performs randomized allocate/free/realloc operations across `malloc_max` slots. `stress_malloc_child()` installs SIGSEGV recovery and starts optional pthreads. `stress_malloc()` configures options, creates the shared bogo counter lock, and runs the child through `stress_oomable_child()`.

Control flow: the outer stressor sets global allocation limits and options, then enters an OOMable child. The child synchronizes and runs one main allocation loop plus optional pthread loops. Each loop mmap-allocates its metadata table, randomly chooses a slot, frees or reallocates existing allocations, or creates new allocations via `calloc`, `posix_memalign`, `aligned_alloc`, `memalign`, `valloc`, or `malloc`. Verification stores the allocation address in the first word and checks it later.

State and persistence: allocator state is process heap plus an mmap metadata table. Static globals hold settings, current action, SIGSEGV jump flag, and thread-running flag. No filesystem state is created.

Dependencies and integration: requires `siglongjmp`; optionally uses pthreads, `malloc.h`, `mallopt`, `malloc_trim`, `malloc_usable_size`, mlock, cache flush, mincore, and stress-ng lock/OOM wrappers.

Risks: intentionally drives memory pressure and allocator fragmentation. SIGSEGV recovery is diagnostic, not a normal control path. Global settings are shared across pthreads, and metric increments use a lock to avoid counter races.

Test signals: optional verification catches pointer corruption and too-small usable sizes, OOM wrapper behavior is expected under pressure, no leaked metadata mapping, and bogo increments under mixed allocator operations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-malloc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-matrix-3d.c -->
# sources/test-tools/stress-ng/stress-matrix-3d.c

Purpose: implements `matrix-3d`, a CPU/FP/cache/memory stressor for cubic `N x N x N` float matrices. It stresses access-order effects and arithmetic kernels in both x-y-z and z-y-x traversal orders.

Important APIs/types/functions: `stress_matrix_3d_type_t` is `float`; `stress_matrix_3d_func_t` uses VLA arguments. Kernel pairs implement add, sub, trans, scalar mult/div, Hadamard product, Frobenius product, copy, mean, zero, negate, and identity. `matrix_3d_methods[]` maps names to xyz/zyx functions and includes the special `all` dispatcher. `stress_matrix_3d_exercise()` allocates matrices, initializes data, times kernels, optionally verifies by recomputation, and emits metrics.

Control flow: `stress_matrix_3d()` catches SIGILL, reads method/order/size options, page-rounds memory size, reports memory use for three matrices, synchronizes, and calls `stress_matrix_3d_exercise()`. The exercise function maps `a`, `b`, `r`, and optional verification matrix `s`; collapses huge pages when possible; initializes random data; repeatedly invokes the selected kernel; advances `method_all_index` for `all`; and unmaps in reverse allocation order.

State and persistence: static state tracks the current method and `all` index; metrics are reset each run. All matrix storage is anonymous mmap and is not persistent.

Dependencies and integration: requires compiler support for VLA function arguments and excludes PCC. Uses target clones, unroll pragmas, mmap/madvise helpers, signal SIGILL catch, method option lookup, memory accounting, and optional verification.

Risks: cubic memory growth is large; `MAX_MATRIX3D_SIZE` can be enormous. Some kernels rely on deterministic floating-point recomputation for verification, so compiler/CPU differences can matter. VLA support controls build availability.

Test signals: method enumeration, successful memory allocation or clear resource failure, optional verification without `memcmp` differences, per-method `matrix-3d ops per sec` metrics, and unimplemented path on unsupported compilers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-matrix-3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-matrix.c -->
# sources/test-tools/stress-ng/stress-matrix.c

Purpose: implements `matrix`, a 2D CPU/FP/cache/memory stressor for `N x N` float matrices. It exercises arithmetic kernels and contrasts x-y versus y-x traversal for cache behavior.

Important APIs/types/functions: `stress_matrix_type_t` is `float`; `stress_matrix_func_t` uses VLA matrix parameters. Kernels include product, add, sub, transpose, scalar multiply/divide, Hadamard, Frobenius, copy, mean, zero, negate, identity, and square. `matrix_methods[]` maps method names to xy/yx implementations. `stress_matrix_exercise()` performs mapping, initialization, kernel timing, optional shadow verification, metric emission, and cleanup.

Control flow: `stress_matrix()` catches SIGILL, reads `matrix-method`, `matrix-yx`, and `matrix-size`, page-rounds storage, reports memory for `a`, `b`, and `r`, synchronizes, and calls the exercise helper. The helper allocates matrices with anonymous mmap, hints collapse, initializes random scaled values, repeatedly executes the chosen kernel, optionally recomputes into `s` and compares, rotates through concrete methods for `all`, then emits per-method rates and a debug geometric mean.

State and persistence: only static method/metric state persists within the process. Matrix memory is anonymous and fully unmapped on exit.

Dependencies and integration: requires VLA argument support, and uses target clones, unroll pragmas, math `frexp`/`pow`, mmap/madvise helpers, method options, memory accounting, metrics, and optional verification.

Risks: large matrix sizes can exhaust memory, especially with verification’s fourth matrix. Floating-point deterministic comparison via `memcmp` assumes identical operations on the same inputs; changing kernels to use non-deterministic reductions would break verification. `stress_matrix_yx_negate()` ignores its input arguments in this source and writes `-a[i][j]` while `(void)a` appears, so edits should treat warnings carefully.

Test signals: successful method selection, memory-use report, no verification differences, per-method `matrix ops per sec` metrics, and unimplemented registration when VLA function arguments are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-matrix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mcontend.c -->
# sources/test-tools/stress-ng/stress-mcontend.c

Purpose: implements `mcontend`, a memory-contention stressor that pounds two mappings of the same backing page from multiple threads, using explicit barriers, cache flushes, optional x86 fences, and optional NUMA placement.

Important APIs/types/functions: `page_write_sync()` prepares a one-page backing file. `read64()` and `read64_lfence()` issue volatile reads with memory barriers and optional x86 `lfence`. `stress_memory_contend()` performs repeated writes, barriers, reads, `mfence`, cache-line flushes, and x86 `pause` sequences against two mappings. `stress_memory_contend_thread()` loops this work in helper pthreads and may change CPU affinity. `stress_mcontend()` sets up mappings, NUMA, locks memory, starts threads, and drives the main loop.

Control flow: the stressor creates a temp backing file, writes one page, maps it twice privately, optionally randomizes NUMA placement, mlocks both mappings, synchronizes, starts four helper threads, and runs contention locally while the helpers do the same. On each main iteration it may `msync()` mappings and increments bogo ops. Threads exit when the global continue flag clears.

State and persistence: global state includes blocked-signal set and optional CPU list. The backing file is unlinked and temp directory removed. Mappings are unmapped and CPU lists freed on exit.

Dependencies and integration: requires pthread support. Optional dependencies include sched affinity, Linux mempolicy, x86 assembly helpers, cache flush helpers, mmap, mlock, and temp-file helpers.

Risks: intentionally creates heavy cache-line bouncing and memory-order pressure. The two private mappings originate from the same file page but copy-on-write behavior may diverge after writes, which is acceptable for contention but important for interpretation. Affinity changes in helper threads are opportunistic.

Test signals: unimplemented without pthreads, successful creation of two mappings, helper thread joins, cleanup of temp directory, and bogo progress under cache/memory pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mcontend.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-membarrier.c -->
# sources/test-tools/stress-ng/stress-membarrier.c

Purpose: implements `membarrier`, a memory-barrier syscall stressor. It repeatedly queries supported membarrier commands and invokes each supported command from the main thread and helper threads.

Important APIs/types/functions: `membarrier_info_t` stores thread handle, return status, duration, and count. Fallback enums define membarrier command constants if headers are absent. `stress_membarrier_exercise()` calls `MEMBARRIER_CMD_QUERY`, iterates command bits, invokes supported commands with normal flags and optional `MEMBARRIER_CMD_FLAG_CPU`, and exercises illegal flags, illegal CPU ids, and one unsupported command. `stress_membarrier_thread()` loops the exercise function. `stress_membarrier()` initializes workers and aggregates metrics.

Control flow: the stressor first verifies the syscall exists and that shared/global command support is present. It initializes per-thread info, starts four worker pthreads, synchronizes, runs the same exercise loop in the main thread, stops workers, aggregates unsynchronized timing/count fields, emits calls-per-second metrics, and joins threads.

State and persistence: static state is only the thread keep-running flag and blocked-signal set. Per-thread metrics live on the stack. No external state persists.

Dependencies and integration: requires pthreads and `__NR_membarrier`; optionally uses `linux/membarrier.h`. Integrates with stress-ng shim syscall wrapper, process-state synchronization, metrics, and unimplemented registration.

Risks: the metric aggregation is intentionally racy to avoid lock overhead, so rates are approximate. Kernel support masks vary widely, and registration commands may be required for some expedited operations on some systems; this stressor simply tries supported bits and ignores many return values after query succeeds.

Test signals: skip on `ENOSYS` or missing shared command, failure if query unexpectedly fails later, bogo increments in main loop, joined helper threads, and nonzero `membarrier calls per sec` when commands execute.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-membarrier.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memcpy.c -->
# sources/test-tools/stress-ng/stress-memcpy.c

Purpose: implements `memcpy`, a memory/cache stressor and optional correctness harness for copy/move routines. It compares libc, compiler builtins, and naive implementations at several optimization levels.

Important APIs/types/functions: generated naive `memcpy` and `memmove` functions are created by `TEST_NAIVE_MEMCPY` and `TEST_NAIVE_MEMMOVE` macros. `memcpy_check_func()` and `memmove_check_func()` validate copied content and return value when verification is enabled; no-check variants remove that overhead. `stress_memcpy_libc()`, `stress_memcpy_builtin()`, and macro-generated stress methods run fixed copy/move sequences. `stress_memcpy_all()` rotates through methods. `stress_memcpy()` allocates buffers, selects a method, and loops.

Control flow: the stressor maps one buffer split into three 2048-byte regions, seeds one region, chooses verification wrappers based on global flags, resolves `memcpy-method`, synchronizes, then repeatedly performs a sequence of full, half, forward-overlap, and backward-overlap copies/moves for `MEMCPY_LOOPS` rounds per bogo operation.

State and persistence: static strings hold current stressor/method names for diagnostics; `memcpy_okay` stops the loop on verification failure. Mapped memory is anonymous and unmapped at exit.

Dependencies and integration: uses core mmap and target-clone support, compiler builtin detection, stress-ng method option lookup, verification flags, proc-state sync, and bogo counters.

Risks: only `memmove` is used for overlapping ranges; changing the sequence to use `memcpy` on overlap would introduce undefined behavior. Verification compares destination to source after each operation, so source/destination sequencing must remain intentional.

Test signals: optional verification failure messages identify method and mismatch type, method enumeration works for all variants, the mmap resource path returns `EXIT_NO_RESOURCE`, and bogo operations continue while `memcpy_okay` remains true.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memcpy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memfd.c -->
# sources/test-tools/stress-ng/stress-memfd.c

Purpose: implements `memfd`, an OS/memory stressor for `memfd_create()`, file growth, shared/private mappings, fallocate holes, lseek modes, close-range cleanup, optional NUMA placement, mlock, madvise, and a specific zap-PTE regression check.

Important APIs/types/functions: `flags[]` cycles memfd flag combinations. `stress_memfd_fill_pages_generic()` writes patterned 64-bit values at cache-line stride. `stress_memfd_check()` validates those patterns for the zap-PTE test. `stress_memfd_child()` contains the workload and runs under `stress_oomable_child()` via `stress_memfd()`.

Control flow: the child reads options, scales `memfd-bytes` per instance, allocates fd/map arrays, optionally prepares NUMA masks, builds unusual names, synchronizes, then repeatedly creates many memfds, truncates them, maps them shared, optionally mlocks/NUMA-randomizes/madvises, fills pages, punches holes and fallocates, exercises `lseek()` modes, unmaps, optionally performs the zap-PTE two-page truncate/pageout verification, closes fd ranges, tests invalid names/flags, cycles a valid flag combination, records timing, and increments bogo ops.

State and persistence: memfds are anonymous file descriptors and are closed every iteration. Arrays and NUMA masks are freed at exit. Metrics report nanoseconds per successful `memfd_create`.

Dependencies and integration: gated by `HAVE_MEMFD_CREATE`; optional dependencies include Linux memfd flags, madvise `MADV_PAGEOUT`, NUMA, mlock, close_range, fallocate, OOM wrapper, and SIGILL catch.

Risks: high fd counts can hit `EMFILE`/`ENFILE`; large mappings can trigger OOM. HugeTLB flags may fail depending on system configuration. The zap-PTE check is slow and kernel-version-specific. Invalid-name tests intentionally exercise failure paths.

Test signals: expected resource handling for fd/memory exhaustion, `VERIFY_ALWAYS`, no data mismatch in zap-PTE check, successful fd cleanup, and a nonzero memfd-create timing metric.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memfd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memhotplug.c -->
# sources/test-tools/stress-ng/stress-memhotplug.c

Purpose: implements `memhotplug`, a privileged Linux stressor for memory hotplug sysfs state transitions. It repeatedly writes removable memory blocks offline and online, optionally while creating anonymous mappings to catch mapping faults during hotplug activity.

Important APIs/types/functions: `stress_mem_info_t` stores memory block name and timeout status; `stress_memhotplug_metrics_t` stores online/offline timing. `stress_memhotplug_supported()` requires `CAP_SYS_ADMIN`. `stress_memhotplug_removable()` reads `/sys/devices/system/memory/memory*/removable`. `stress_memhotplug_mem_toggle()` writes `offline` then `online` to a block's `state` file with a profiling timer. `stress_memhotplug_mem_online()` restores a block. SIGSEGV recovery uses `stress_segv_handler()` and `siglongjmp`.

Control flow: the stressor installs SIGPROF/SIGSEGV handlers, opens the sysfs memory directory, counts removable blocks, stores their names, synchronizes, sets a jump recovery point, then loops over blocks. For each block it optionally maps memory, attempts offline with timeout detection, unmaps, attempts online, records durations, and increments bogo ops. If every block times out, it tries to online all blocks.

State and persistence: this stressor mutates kernel memory block state and must restore all tracked blocks online in cleanup. It frees duplicated sysfs names, unmaps optional mappings, restores the old SIGSEGV handler, and reports online/offline timing metrics.

Dependencies and integration: Linux-only, sysfs memory hotplug ABI, `CAP_SYS_ADMIN`, `setitimer`, signal helpers, capability checks, mmap helpers, and stress-ng metrics/options.

Risks: high-impact privileged operation; offlining memory can fail, stall, or disrupt workloads. Timeouts are remembered per block to avoid repeated delays. SIGSEGV handling exists because hotplug plus populate/touch can fault unexpectedly.

Test signals: skip without capability or removable entries, offline/online metrics when transitions succeed, debug count of unexpected SIGSEGVs, all blocks restored online, and no lingering custom signal handler.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memhotplug.c -->
