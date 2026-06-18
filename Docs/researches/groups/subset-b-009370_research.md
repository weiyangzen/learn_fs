# subset-b-009370 Research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fork.c -->
# sources/test-tools/stress-ng/stress-fork.c Research

Purpose: implements the `fork` and `vfork` stressors. They repeatedly create short-lived child processes, optionally apply extra VM pressure, and verify that fork failures are limited to expected resource exhaustion cases.

Important APIs/types/functions: `stress_fork_info` and `stress_vfork_info` register the stressors, help text, options, classifiers, and optional verification. `fork_info_t` records child PID and saved errno. `stress_fork_fn()` is the shared engine for both `fork()` and `shim_vfork()`. `stress_fork_shim_exit()` exits through `__NR_exit` before falling back to `_exit()`. Linux builds include `stress_fork_maps_reduce()`, which parses `/proc/self/maps` and applies `madvise()`, `mincore()`, or `munmap()` to selected shared libraries.

Control flow: `stress_fork()` reads `fork-max`, `fork-pageout`, `fork-unmap`, and `fork-vm`, resolves maximize/minimize defaults, disallows simultaneous `fork-vm` and `fork-unmap`, forces libc symbol binding, synchronizes workers, and calls `stress_fork_fn()`. With `fork-unmap`, it runs the core loop in a subprocess so aggressive unmapping does not corrupt the long-lived stress-ng worker. `stress_vfork()` reads `vfork-max`, synchronizes, and calls the same engine with `STRESS_VFORK`. The engine batches up to `fork_max` children, waits for them, increments bogo operations for successful reaps, and checks failure errno under verification.

State and persistence: all child process state is transient. `info` is a static aligned PID/error array local to the worker. `stress_fork_maps_reduce()` affects the current process address space only. No durable files are created.

Dependencies and integration: depends on stress-ng shims for settings, process state, synchronization, OOM adjustment, capability dropping, waits, vfork, memory advice, KSM, and logging. It is classified as scheduler/OS and integrated through the global stressor table via exported `stressor_info_t` objects.

Risks: `fork-unmap` is intentionally dangerous and Linux-specific; the code mitigates it by isolating the core loop in a child process. `/proc/self/maps` parsing and shared-library name filters can become stale. Verification accepts `EAGAIN` and `ENOMEM` but reports other fork errors, so platform-specific failures may be noisy. `vfork()` semantics require the child to exit immediately, which the code enforces.

Test signals: useful signals are bogo operation progress, optional verification failures for unexpected fork errno, and correct cleanup of child processes. Run coverage should include plain `fork`, `vfork`, `fork-vm`, `fork-pageout`, and isolated `fork-unmap` on Linux.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-forkheavy.c -->
# sources/test-tools/stress-ng/stress-forkheavy.c Research

Purpose: implements `forkheavy`, a scheduler/OS stressor that allocates many auxiliary resources and then rapidly forks and reaps many child processes, measuring fork latency under resource pressure.

Important APIs/types/functions: `stress_forkheavy_args_t` passes resource arrays, pipe size, and shared metrics into an OOMable child. `stress_forkheavy_t` and `stress_forkheavy_list_t` maintain active and free PID list nodes. `stress_forkheavy_new()`, `stress_forkheavy_head_remove()`, and `stress_forkheavy_free()` own that list. `stress_forkheavy_child()` performs the main fork/reap loop. `stress_forkheavy()` allocates resources/metrics and registers the OOMable execution. Options are `forkheavy-allocs`, `forkheavy-procs`, and `forkheavy-mlock`.

Control flow: the top-level stressor allocates a `stress_resources_t` array, maps shared metrics, creates a metrics lock, and invokes `stress_oomable_child(..., STRESS_OOMABLE_DROP_CAP)`. The child computes a minimum free-memory reserve, reads settings, optionally enables `MCL_FUTURE`, allocates resource pressure through `stress_resources_allocate()`, synchronizes with peer workers, then loops. If memory is not low and the active list is below `forkheavy-procs`, it appends a node, timestamps under the metrics lock, forks, updates metrics in the child, and exits. If fork fails or memory is low, it reaps the oldest child. Shutdown alarms and waits all remaining children, frees the PID lists, and releases allocated resources.

State and persistence: process state is in the per-worker global `forkheavy_list`, which is cleared before exit. Metrics live in shared anonymous memory and are reduced into a "microsecs per fork" harmonic metric. No files persist after the stressor.

Dependencies and integration: depends on core lock, mmap, OOM, and resource helpers. It uses stress-ng synchronization, settings, memory-limit checks, `stress_make_it_fail_set()`, bogo counters, and metrics.

Risks: high defaults can hit process limits, memory pressure, cgroup PID limits, or mlock restrictions. Metrics timing crosses a fork boundary and uses shared locking, so it is an approximate latency signal. The active list is global within the worker process; unexpected early exits before cleanup could leave children until parent death handling or alarms reap them.

Test signals: expected outputs are steady bogo progress and a nonzero microseconds-per-fork metric. Resource exhaustion should be handled by reaping rather than failing. Exercise minimize/maximize, explicit process limits, and `forkheavy-mlock` on systems with and without sufficient privileges.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-forkheavy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-error.c -->
# sources/test-tools/stress-ng/stress-fp-error.c Research

Purpose: implements `fp-error`, a VERIFY_ALWAYS floating-point stressor that exercises math-domain, range, exception, errno, and rounding behavior.

Important APIs/types/functions: `stress_fp_error_info` exports the stressor or an unimplemented placeholder when functional FP error support is unavailable. `stress_fp_clear_error()` resets `errno` and clears all FP exceptions. `stress_double_same()` compares normal, NaN, and infinity results. `stress_fp_check()` validates result value, expected errno, and expected `fenv` exceptions on supported Linux/compiler combinations, with a value-only fallback elsewhere. `SET_VOLATILE` forces runtime computation for selected expressions.

Control flow: the stressor synchronizes workers, then repeatedly clears the FP status and evaluates `log(-1)`, `log(0)`, `log2(-1)`, `log2(0)`, `sqrt(-1)`, inexact division, overflow addition, underflow `exp(-1000000)`, overflow `exp(DBL_MAX)`, and `fegetround()`. Each enabled block is compile-time gated by `EDOM`, `ERANGE`, and `FE_*` macros. Failures set `rc = EXIT_FAILURE`, but the loop continues until the normal stress-ng stop condition.

State and persistence: only per-thread/process floating-point status flags and `errno` are mutated. There is no durable state. Volatile locals are used to prevent constant folding.

Dependencies and integration: depends on `<math.h>`, `<fenv.h>`, `<float.h>`, architecture/compiler feature macros, stress-ng sync/state/logging, and bogo counters. It is classified CPU/FP and requires verification.

Risks: FP exception and errno behavior varies across libcs, architectures, soft-float builds, and compilers. The code explicitly excludes uClibc, ARC64, some Linux architectures, musl/ICC/PCC cases, and soft-float paths from stricter checks. `M_PI` availability is assumed through the project configuration.

Test signals: failures are `pr_fail()` messages describing expression, result, errno, and exception mismatch. Useful coverage includes glibc Linux with hardware FP for strict checking and non-Linux or alternate libc builds to confirm fallback behavior or unimplemented registration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-misc.c -->
# sources/test-tools/stress-ng/stress-fp-misc.c Research

Purpose: implements `fp_misc`, a VERIFY_ALWAYS CPU/FP/compute stressor for C floating-point comparison and classification macros across `float`, `double`, and `long double`.

Important APIs/types/functions: global test operands hold normal values, ordered variants, NaN, infinity, and zero for each precision. `stress_fp_misc_methods_t` maps a check function, metric name, and number of logical tests. The method table includes gated checks for `isgreater`, `isgreaterequal`, `isless`, `islessequal`, `islessgreater`, `isunordered`, `fpclassify`, `isfinite`, `isnormal`, `isnan`, `isinf`, and `signbit`. `stress_fp_misc_supported()` skips builds with no available macros.

Control flow: after catching SIGILL and zeroing metrics, the stressor initializes NaN/inf/zero constants, synchronizes, then repeatedly creates ordered random values for all three precisions. For every method, it runs the check 1000 times, accumulating duration and test count. A failed check jumps to `fp_fail`, where metrics are still emitted. Each check logs a detailed failure if a comparison or classification macro violates expected behavior with ordered values, NaN, infinity, or signed zero.

State and persistence: operand globals are process-local and overwritten each iteration. Metrics are stack-local and published at exit. There is no file or shared persistent state.

Dependencies and integration: depends on `<math.h>` macros, stress-ng random number generation, signal handling, sync, metrics, bogo counters, and feature gating. The stressor reports up to one metric per compiled method.

Risks: several diagnostic strings say "returned false" in branches where the code is checking an unexpected true result; this affects logs, not control flow. `stress_fp_misc()` currently returns `EXIT_SUCCESS` even after a check failure path, relying on `pr_fail()` and VERIFY_ALWAYS as the observable signal. Macro availability and behavior can vary by libc/compiler, and NaN signbit expectations may be implementation-sensitive.

Test signals: look for per-method ops/sec metrics and any `pr_fail()` messages. Regression tests should validate builds with and without each math macro family, plus platforms where `isinf` is disabled for PCC.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp-misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp.c -->
# sources/test-tools/stress-ng/stress-fp.c Research

Purpose: implements `fp`, a CPU/FP/compute stressor that performs reversible floating-point add, subtract, multiply, and divide loops across native and optional extended FP types.

Important APIs/types/functions: `fp_data_t` stores initialization values, result slots, addends, and multipliers for long double, double, float, and optional `__bf16`, `_Float16`, `_Float32`, `_Float64`, `__float80`, `__float128`/`_Float128`, and `__ibm128`. Macros `STRESS_FP_ADD/SUB/MUL/DIV` generate optimized target-cloned worker functions. `stress_fp_funcs[]` maps method names to functions and FP type IDs. `stress_fp_call_method()` dispatches a method, updates metrics, and optionally verifies by running a second result slot and comparing byte-identical results for supported types.

Control flow: `stress_fp()` catches SIGILL, allocates a small anonymous `fp_data` array, initializes all compiled FP fields with random but reversible operands, synchronizes, and repeatedly calls either a selected `fp-method` or `all`. On exit it emits Mfp-ops/sec metrics for each method with recorded counts and durations, then unmaps the data.

State and persistence: all FP data lives in a private anonymous mapping named `fp-data`. Metrics are static per-process arrays reset per invocation. No durable files are used.

Dependencies and integration: depends on architecture/compiler feature macros, stress-ng mmap/madvise/signal/metrics/random helpers, target clone attributes, and the settings method selector. It exports `stress_fp_info` with optional verification and `max_metrics_items`.

Risks: extended FP availability is compiler- and architecture-dependent; the source disables float80 under ICC and float128 on OpenBSD. Byte-for-byte verification may be sensitive to precision, padding, or interruption; the code avoids checking after a stop signal. Division loops check the global continue flag because they can be longer-running.

Test signals: expected signals are bogo progress, per-method Mfp-ops/sec metrics, SIGILL-safe behavior on unsupported instructions, and optional verification failures that identify method, FP type, element, and expected/got values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fpunch.c -->
# sources/test-tools/stress-ng/stress-fpunch.c Research

Purpose: implements `fpunch`, a filesystem/OS stressor that creates sparse files and has child processes repeatedly exercise `fallocate()` modes such as keep-size allocation, hole punching, zero range, collapse range, and insert range.

Important APIs/types/functions: `stress_fallocate_modes_t` describes each fallocate mode and whether pre/post writes or zero verification are required. `stress_punch_buf_t` holds write/read buffers. `stress_punch_pwrite()` abstracts `pwrite()` versus `lseek()+write()`. `stress_punch_check_zero()` verifies zeroed ranges. `stress_punch_action()` performs one operation and optional validation. `stress_punch_file()` loops across offsets and modes. `stress_fpunch()` handles temp file setup, sparse prepopulation, child orchestration, metrics, and cleanup.

Control flow: the top-level stressor clamps `fpunch-bytes`, divides work by instance count, maps a shared PID array and a private buffer, creates a temp directory/file, writes alternating data/hole extents backward, then forks four child workers. Children synchronize through `stress_sync_start_*`, install a SIGALRM exit handler, and call `stress_punch_file()` on the shared file descriptor or their own descriptor when `preadv/pwritev` support is absent. The parent releases children, sleeps for the configured timeout, kills/waits them, records extents per file, unlinks the file, and removes the temp directory.

State and persistence: the temporary file is unlinked during cleanup and the temporary directory is removed. PID synchronization state lives in an mmap allocated by stress-ng helpers. Static previous offset/size caching in `stress_punch_action()` is per process.

Dependencies and integration: requires `HAVE_FALLOCATE`; otherwise it registers as unimplemented. It uses stress-ng FS temp helpers, sync PID maps, kill/wait helpers, mmap/madvise, signal handling, and filesystem metrics.

Risks: fallocate mode support and alignment rules vary by filesystem, and many failures are intentionally ignored. Verification only checks zeroing for instance zero and selected offsets. Shared file descriptors can race on systems without positional I/O, so the code reopens per child in that case. Large defaults can consume real filesystem space depending on sparse-file behavior.

Test signals: bogo operations come from child fallocate loops; parent reports extents per file. Verify mode can report nonzero data after zero-range operations. Test across ext4/xfs/tmpfs and with constrained disk space.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fpunch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fractal.c -->
# sources/test-tools/stress-ng/stress-fractal.c Research

Purpose: implements `fractal`, a CPU/FP/compute stressor that renders Mandelbrot or Julia rows into a one-row buffer to stress floating-point computation and memory stores without producing an image.

Important APIs/types/functions: `fractal_info_t` stores bounds, step sizes, row buffer, dimensions, and iteration limit. `stress_fractal_method_t` maps method names to row functions and default parameters. `stress_fractal_mandelbrot()` and `stress_fractal_julia()` are optimized target-cloned row renderers with two-column unrolling and residual handling. `stress_fractal_get_row()` coordinates row assignment across instances using an atomic fetch-add when available, or a stress-ng lock fallback.

Control flow: `stress_fractal_init()` creates a shared lock and initializes `g_shared->fractal.row`; deinit destroys it. The stressor reads method, iteration, xsize, and ysize settings; maps a single row buffer; computes `dx/dy`; synchronizes; then repeatedly obtains a row and renders it until stopped. Bogo operations are incremented when row assignment wraps to zero. Metrics report points/sec and fractals/sec.

State and persistence: the only shared state is `g_shared->fractal.row` and its lock. Per-worker row data is an anonymous mapping and is discarded. No rendered image or file persists.

Dependencies and integration: depends on `g_shared` stress-ng shared state, lock helpers, mmap helpers, target clones, sync/state transitions, settings, and metrics. The stressor registers init/deinit callbacks and VERIFY_NONE.

Risks: the atomic row path can produce imperfect wrap behavior when the row counter overflows or when `ysize` does not divide the counter state exactly; the comment accepts this as benchmark noise. Large `xsize` values can request large row buffers. There is no output correctness verification.

Test signals: expected metrics are points/sec and fractals/sec, plus an informational line from instance zero describing method, dimensions, iterations, and complex-plane bounds. Test both methods, lock fallback builds, and extreme size/iteration settings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fractal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fsize.c -->
# sources/test-tools/stress-ng/stress-fsize.c Research

Purpose: implements `fsize`, a filesystem/OS VERIFY_ALWAYS stressor that validates file-size limit enforcement through `RLIMIT_FSIZE`, `fallocate()`, `ftruncate()`, and `SIGXFSZ`.

Important APIs/types/functions: `stress_fsize_handler()` records SIGXFSZ delivery. `stress_fsize_reported()` suppresses repeated messages for the same offset/type. `stress_fsize_boundary()` sets a file-size limit and tests allocation just below and at the boundary. `stress_fsize_max_off_t()` discovers the maximum signed `off_t`. `stress_fsize_info` exports either the stressor or an unimplemented placeholder when fallocate, RLIMIT_FSIZE, or SIGXFSZ support is missing.

Control flow: the stressor saves the original `RLIMIT_FSIZE`, computes a bounded maximum, installs the signal handler, creates and unlinks a temp file, synchronizes, then loops. Each iteration sets a small current limit, truncates to zero, confirms allocation up to the limit succeeds, confirms allocation beyond it fails with expected errors and raises SIGXFSZ, tests a random boundary, restores the original limit, then tests powers-of-two-minus-one offsets up to the max offset. It records SIGXFSZ signals per second at exit.

State and persistence: process resource limits are mutated and restored during each iteration. The temp file is unlinked immediately after opening and closed on exit. Signal counters are static process state.

Dependencies and integration: depends on stress-ng temp directory helpers, fallocate shim, signal handling, resource-limit APIs, bogo counters, metrics, and filesystem usage reporting.

Risks: resource limits are process-wide, so early fatal paths before restoration could affect the worker until process exit. Filesystem and kernel behavior around fallocate, ENOSPC, EINTR, and SIGXFSZ can vary. The signal counter is intentionally racy, acceptable for metrics but not exact.

Test signals: failures identify unexpected fallocate success, unexpected errno, missing/unexpected SIGXFSZ, or inability to truncate. A healthy run reports SIGXFSZ signals/sec and steady bogo progress. Coverage should include filesystems with and without fallocate support and constrained quota/space cases.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fsize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fstat.c -->
# sources/test-tools/stress-ng/stress-fstat.c Research

Purpose: implements `fstat`, a filesystem/OS stressor that repeatedly exercises `stat`, `lstat`, `statx`, and `fstat` against entries from a target directory, defaulting to `/dev`.

Important APIs/types/functions: `stress_stat_info_t` caches a path plus ignore bits and access state. `do_not_stat()` filters dangerous paths such as `/dev/watchdog`. `stress_fstat_check_buf()` detects stat buffers left unchanged. `stress_fstat_helper()` performs the actual stat/lstat/statx/fstat calls and intentional invalid calls. With pthread support, `stress_fstat_thread()` and `stress_fstat_threads()` run helper loops concurrently.

Control flow: `stress_fstat()` reads `fstat-dir`, opens it, caches directory entries into a linked list, fills the signal mask, synchronizes, then iterates the cache while work continues. For each path that has not failed all operation classes, it runs helper loops in the main thread and up to four pthreads, increments bogo count, and continues while at least one path remains usable. At the end it frees all cached paths.

State and persistence: cached path nodes are heap state in the worker and are freed at exit. Per-path ignore bits persist only during one stressor invocation to avoid repeated known failures. No files are modified.

Dependencies and integration: depends on pthread helpers, stress-ng statx/lstat/fstat shims, bad-fd generation, scheduling yield, settings, logging, and sync/state transitions. It is VERIFY_ALWAYS.

Risks: the default `/dev` tree can contain special devices whose open/stat behavior differs by privilege; the code avoids opening device files when effective UID is root and blocklists watchdog. Directory contents can change after caching. Threaded helpers share `stress_stat_info_t` ignore/access fields without locks, intentionally trading precision for stress.

Test signals: failures include unchanged stat buffers, unexpected helper errors, and directory-open failures. Useful tests include custom `fstat-dir` paths, non-root versus root behavior, pthread-disabled builds, and statx availability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-fstat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-full.c -->
# sources/test-tools/stress-ng/stress-full.c Research

Purpose: implements `full`, a device/memory/OS stressor that validates and exercises `/dev/full` behavior: writes fail with ENOSPC, reads return zeroes, and miscellaneous file operations behave consistently.

Important APIs/types/functions: `stress_full()` is the main stressor. Linux builds also define a `whences[]` table for rotating `lseek()` tests. `stress_full_info` registers VERIFY_ALWAYS or an unimplemented placeholder on unsupported platforms.

Control flow: the stressor maps a 4096-byte anonymous buffer, synchronizes, then repeatedly opens `/dev/full`. It writes and expects failure with `ENOSPC` except for transient `EAGAIN`/`EINTR`, reads and verifies the buffer is all zero, optionally tests `pread()` at a random offset, calls `fstat()`, tries read and write mappings plus `msync()`, rotates Linux `lseek()` calls over `SEEK_SET`, `SEEK_CUR`, and `SEEK_END`, exercises `FIONREAD` and `FIGETBSZ` ioctls when present, closes the fd, and increments bogo operations.

State and persistence: only the anonymous buffer and current fd are held. No persistent state is written. The device path is opened fresh each iteration and closed before the next loop.

Dependencies and integration: uses stress-ng mmap/madvise, zero-data checking, put helpers, fstat shim, metrics-free bogo accounting, and state transitions. The platform guard permits Linux, Sun, FreeBSD, and NetBSD, although the unimplemented reason text says Linux only.

Risks: `/dev/full` may be absent in containers or nonstandard systems; ENOENT becomes `EXIT_NOT_IMPLEMENTED`. mmap behavior for `/dev/full` can vary and failures are tolerated. The platform guard and unimplemented reason are slightly inconsistent.

Test signals: healthy runs produce bogo progress only. Failure logs identify incorrect write errno, nonzero read data, read/pread/fstat/lseek failures, or open failure. Test with `/dev/full` missing, container device policies, and Linux ioctl availability.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-full.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funccall.c -->
# sources/test-tools/stress-ng/stress-funccall.c Research

Purpose: implements `funccall`, a CPU stressor that exercises ABI argument passing for functions with one through nine arguments, including shallow and nested call chains across many scalar and optional FP/complex/decimal types.

Important APIs/types/functions: macros generate `stress_funccall_<type>_1..9()` and `stress_funcdeep_<type>_1..9()` functions. `stress_funccall_type()` generates a per-type exerciser that creates nine random inputs, repeatedly sums shallow and nested call results, stores values through `core-put` helpers, and verifies stable results. `stress_funccall_methods[]` maps selectable method names to generated functions. `stress_funccall_exercise()`, `stress_funccall_all()`, and `stress_funccall()` implement dispatch, metrics, and return status.

Control flow: top-level code zeroes metrics, reads `funccall-method`, synchronizes, then repeatedly exercises either the selected type or all compiled types until a check fails or stress-ng stops. At exit it emits per-type "function invocations per sec" harmonic metrics and returns failure if verification failed.

State and persistence: metrics are static per-process arrays reset at start. Generated functions update `g_put_val` through put helpers to prevent optimization from removing work. No durable state exists.

Dependencies and integration: depends on architecture/compiler feature gates, `<math.h>`, optional complex support, decimal and extended FP feature macros, `core-put`, random number helpers, sync/state/metrics, and method-option parsing. It is VERIFY_ALWAYS with `max_metrics_items`.

Risks: macro expansion is large and type availability is compiler-sensitive. Some optional types use `cmp_ignore`, so those methods measure call paths without semantic verification. s390 and SH4 disable selected hard-decimal/complex paths. Floating comparisons use relative tolerances after casting to double, which may hide precision-specific differences.

Test signals: failure logs identify the nested method whose return value changed. Metrics should appear for every compiled method except `all`. Build coverage should include compilers with and without complex, decimal, float16/32/64/80/128, and int128 support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funccall.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funcret.c -->
# sources/test-tools/stress-ng/stress-funcret.c Research

Purpose: implements `funcret`, a CPU stressor that exercises function return value copying and ABI return paths for small integers, floating types, optional extended types, and large structs.

Important APIs/types/functions: macros generate one-level, deep, and deeper return wrappers for each type. `stress_funcret_type()` generates per-type tests that initialize a value, pass it through generated return wrappers 1000 times, and verify that returned values remain stable. `stress_funcret_setvar()` randomizes object bytes. `stress_funcret_methods[]` maps method names to functions, including large `stress_uint8x32_t`, `stress_uint8x128_t`, and `stress_uint64x128_t` structures. `stress_funcret_exercise()` records timing and logs verification failures.

Control flow: `stress_funcret()` reads `funcret-method`, zeros metrics, synchronizes, and repeatedly exercises the selected method or `all` until failure or stop. On completion it emits per-method invocation-rate metrics and returns success only if verification never failed.

State and persistence: static metrics are process-local and reset per run. Test variables are stack-local. Generated wrappers intentionally copy through temporaries and clear inputs to force real return copying. No persistent state exists.

Dependencies and integration: uses stress-ng random bytes, memory shims, metrics, sync/state, method option parsing, and architecture/compiler feature macros. s390 decimal support is guarded by project pragmas; clang-disabled paths avoid unsupported decimal/extended return handling.

Risks: optional type coverage changes significantly by compiler and architecture. Floating comparison casts to double and uses tolerance, which is pragmatic but can miss some extended precision issues. The option key in `opts` is `"funcret_method"` while help advertises `funcret-method`; that mismatch is a potential CLI integration issue unless normalized elsewhere.

Test signals: failures report the selected function return method. Expected metrics are per-type function invocations/sec. Test with all compiled methods, selected large-struct methods, and compiler variants for decimal and extended FP returns.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-funcret.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-futex.c -->
# sources/test-tools/stress-ng/stress-futex.c Research

Purpose: implements `futex`, a Linux scheduler/OS/IPC stressor that repeatedly exercises futex wait and wake paths between a parent waker and child waiter.

Important APIs/types/functions: `stress_futex_wait()` wraps `shim_futex_wait()` and periodically tries `shim_futex_waitv()` when `FUTEX_32` and `CLOCK_MONOTONIC` are available, disabling waitv after errors or ENOSYS. `stress_futex()` forks the waiter, drives wake calls, and records timeout counts in `g_shared->futex.timeout[instance]`. `stress_futex_info` registers the stressor or an unimplemented placeholder without Linux futex support.

Control flow: after synchronization, the parent records its CPU and forks. Fork failures may retry through `stress_redo_fork()`. The parent loops calling `shim_futex_wake(futex, 1)` until stop, optionally verifying wake errors, then SIGALRMs and waits for the child. The child pins toward the parent CPU, applies scheduler settings, sets parent-death alarm behavior, and loops on short 5000 ns futex waits. Timeouts increment a shared counter and trigger periodic backoff sleeps after thresholds; non-timeout wakeups increment bogo operations. The child exits with failure if verify mode sees unexpected wait errors.

State and persistence: futex words and timeout counters live in stress-ng shared memory. The child process is transient and reaped. No durable state exists.

Dependencies and integration: depends on Linux futex headers and `__NR_futex`, stress-ng futex shims, CPU affinity helpers, shared state, fork retry logic, scheduler settings, and signal/wait helpers. Verification is optional.

Risks: futex waitv availability depends on kernel support and is dynamically disabled. Very fast timeout polling can consume CPU and trigger scheduler artifacts; the threshold backoff mitigates this. Parent/child status handling does not propagate child failure status beyond wait completion in the parent path.

Test signals: watch bogo progress, debug timeout counts, and optional verification errors for futex wait/wake. Test on kernels with and without `futex_waitv`, under CPU affinity constraints, and under fork pressure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-futex.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-get.c -->
# sources/test-tools/stress-ng/stress-get.c Research

Purpose: implements `get`, an OS stressor that cycles through many `get*` and related information syscalls/libc calls, including identity, process group, resource limit, time, filesystem, namespace, and system information APIs.

Important APIs/types/functions: `stress_get_func_t` is the method signature. `stress_get_funcs[]` contains the dispatch list. Helpers cover `getcwd`, ids/groups, `getpriority`, `getresuid/gid`, `getrlimit`, `ugetrlimit`, `prlimit`, `_sysctl`, `getrusage`, `getsid`, `gettid`, `getcpu`, `time`, `gettimeofday`, `uname`, `sysfs`, `statfs`, `statvfs`, `adjtimex`, `adjtime`, namespace listing, and more. `stress_segv_handler()` uses `siglongjmp` to recover from intentional fault probing.

Control flow: `stress_get()` reads `get-slow-sync`, checks time-setting capability, installs SIGSEGV recovery, caches mount paths, records PID and verify mode, synchronizes, then repeatedly selects a function either sequentially or from a time-derived synchronized index. Each selected helper performs valid and often intentionally invalid variants, reporting failures only for unexpected errors under verify rules. After the loop, it calls `getlogin()` once because that may reset alarms, deinitializes, and frees mount strings.

State and persistence: static indices inside helpers rotate through rlimit, priority, rusage, filesystem, and mount arrays. Mount strings are allocated by `stress_mount_get()` and freed at exit. `mypid`, `verify`, capability flags, and mount arrays are process-global. No durable state is written.

Dependencies and integration: depends on many platform headers and stress-ng shims for capabilities, mounts, time/syscalls, bad/racy PID generation, mapped guard pages, sync/state/logging, and options. It registers as unimplemented without `siglongjmp`.

Risks: behavior varies heavily by OS, libc, capabilities, namespace support, VDSO behavior, and deprecated syscall availability. Several helpers intentionally ignore errors to increase syscall coverage. Intentional invalid pointer/protected-page probes require reliable signal recovery.

Test signals: bogo progress indicates call cycling. Verify failures identify unexpected syscall errors or mismatched time/sysfs/getcwd/uname behavior. Test slow-sync with multiple workers, limited capabilities, container namespaces, and alternate libc/kernel combinations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-get.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getdent.c -->
# sources/test-tools/stress-ng/stress-getdent.c Research

Purpose: implements `getdent`, a filesystem/OS stressor that directly exercises Linux `getdents` and/or `getdents64` syscalls while recursively walking common system directories.

Important APIs/types/functions: `stress_getdents_func` abstracts old and 64-bit getdents readers. `getdents_funcs[]` holds compiled syscall variants. `stress_getdents_rand()` selects a variant randomly and disables it if it returns ENOSYS. `stress_getdents_dir()` and `stress_getdents64_dir()` open a directory, allocate a page-aligned-ish random buffer, issue invalid bad-fd and zero-size calls, then read entries and optionally recurse. `stress_gendent_offset()` performs byte-offset pointer movement.

Control flow: `stress_getdent()` synchronizes, then repeatedly scans `/proc`, `/dev`, `/tmp`, `/sys`, and `/run` with different recursion depths. Each directory reader opens the path, allocates a random buffer up to 256 KiB plus page rounding, times syscall calls, increments count and bogo operations for successful reads, walks returned records safely using `d_reclen`, and recurses into non-dot directories. On exit it reports nanoseconds per getdents call.

State and persistence: function pointers in `getdents_funcs[]` can be nulled after ENOSYS for the process lifetime. All buffers are heap-local and freed per directory call. No filesystem changes are made.

Dependencies and integration: depends on Linux syscall numbers, stress-ng getdents shims and dirent structs, bad-fd helper, filesystem path helpers, random buffer sizing, timing, metrics, sync/state, and verify registration.

Risks: direct parsing of kernel dirent records must guard bad `d_reclen`; the code breaks out on invalid records. Recursion over live pseudo-filesystems can race with disappearing directories. A negative errno is returned internally but the top-level stressor ultimately returns success unless no syscall variant remains.

Test signals: metric output is nanoseconds per getdents call. Failure logs occur when all syscall variants fail unexpectedly. Test on Linux architectures with only getdents64, with inaccessible pseudo-filesystem directories, and under concurrent filesystem churn.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getdent.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getrandom.c -->
# sources/test-tools/stress-ng/stress-getrandom.c Research

Purpose: implements `getrandom`, an OS/CPU stressor that reads kernel random data via `getrandom()` and, when available, `getentropy()`.

Important APIs/types/functions: `stress_getrandom_supported()` probes `shim_getrandom()` and skips ENOSYS systems. `getrandom_flags_t` maps flag values to names. `getrandom_flags[]` includes zero flags, Linux nonblocking/random/insecure combinations when available, intentionally invalid combinations such as insecure+random, and `~0U`. `stress_getrandom()` performs reads, handles expected transient/invalid errors, accounts bytes, and emits bit-rate metrics.

Control flow: after synchronization, the stressor loops over all flag entries while work continues. For each flag it calls `shim_getrandom()` into a stack buffer sized 256 bytes on OpenBSD/macOS or 8192 bytes elsewhere. `EAGAIN`, `EINTR`, and `EINVAL` are accepted for nonblocking or invalid flag cases. ENOSYS becomes `EXIT_NOT_IMPLEMENTED`; other errors are failures. Successful reads add returned byte counts. `getentropy(buffer, 1)` is also exercised when available. Bogo operations increment per flag iteration, and exit metrics report getrandom bits/sec.

State and persistence: all random data is stack-local and discarded. Only local duration/byte counters persist for the run. No files or global state are modified.

Dependencies and integration: depends on platform support for OpenBSD, Apple, FreeBSD, or Linux `__NR_getrandom`; optional `<linux/random.h>` flags; stress-ng syscall shims, support hooks, sync/state, and metrics.

Risks: flag semantics vary by kernel and libc. Invalid flag combinations are intentionally tolerated via `EINVAL`. `GRND_RANDOM` or early-boot entropy behavior can block or return `EAGAIN` depending on flags and OS. Large buffer sizes may change syscall cost across platforms.

Test signals: expected output is a getrandom bits/sec metric and no unexpected error logs. Test with Linux kernels supporting and lacking `GRND_INSECURE`, non-Linux supported platforms, and environments with constrained entropy or syscall filtering.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getrandom.c -->
