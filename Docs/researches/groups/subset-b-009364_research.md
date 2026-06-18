# subset-b-009364 research

Grouped research report for selected stress-ng stressors under `sources/test-tools/stress-ng`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aio.c -->
# sources/test-tools/stress-ng/stress-aio.c

Purpose: `stress-aio.c` implements the `aio` stressor, which exercises POSIX asynchronous I/O via `aio_read`, `aio_write`, optional `aio_fsync`, signal notification, cancellation, and temporary-file backed read/write cycling. It is an I/O, interrupt, and OS stressor registered as `stress_aio_info`.

Important APIs/types/functions: the build-gated implementation requires `HAVE_LIB_RT`, `aio.h`, `aio_cancel`, `aio_read`, and `aio_write`. `stress_io_req_t` stores the request slot, last AIO status, `struct aiocb`, a 16-byte buffer, and a signal-delivery count. `aio_fill_buffer()` seeds deterministic data, `aio_signal_handler()` accounts `SIGUSR1` completions through `sigev_value.sival_ptr`, `aio_issue_cancel()` polls `aio_error()` and retries `aio_cancel()`, and `issue_aio_request()`/`issue_aio_sync_request()` initialize `aiocb` objects for read/write/fsync operations.

Control flow: `stress_aio()` reads `aio-requests` or applies maximize/minimize bounds, allocates the request array, creates a per-worker temp directory and file, installs a `SIGUSR1` `SA_SIGINFO` handler, submits initial writes for every slot, waits at the synchronized start barrier, then loops while `stress_continue(args)` is true. Each pass checks `aio_error()`, counts completed or canceled operations, and resubmits read, write, or final-slot fsync work. On hard AIO errors it jumps to cancellation and cleanup.

State and persistence behavior: persistent state is limited to the temporary file and directory, unlinked immediately after opening and removed at deinit. Runtime state lives in `io_reqs`, the process-wide `do_accounting` flag, the installed signal handler, per-request completion counters, and stress-ng metrics. The file descriptor receives a short read/write hint.

Dependencies and integration points: the stressor uses stress-ng option parsing, sync barriers, process-state tracking, temporary filesystem helpers, random selection via `stress_mwc1()`, bogo counters, metrics, and common exit-status mapping. It is exposed through the stressor table with `VERIFY_ALWAYS` and an unimplemented fallback when POSIX AIO support is absent.

Risks: signal accounting is global to the process and depends on `do_accounting` being disabled before cancellation; changes around handler lifetime or multiple stressors sharing `SIGUSR1` can skew metrics. Filesystem-specific `ENOSPC` is silently ignored for writes but other `aio_error()` values fail. Cancellation loops can delay teardown if a request remains `AIO_NOTCANCELED`.

Test signals: useful coverage includes builds with and without librt/AIO support, small and maximum `aio-requests`, filesystems returning `ENOSPC`, interruption during `aio_cancel()`, optional `aio_fsync` paths with `O_SYNC`/`O_DSYNC`, and metrics named `async I/O signals per sec` and `async I/O signals`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aiol.c -->
# sources/test-tools/stress-ng/stress-aiol.c

Purpose: `stress-aiol.c` implements the `aiol` stressor for the Linux native AIO syscall ABI. It stresses `io_setup`, `io_submit`, `io_getevents`/`io_pgetevents`, `io_cancel`, vector I/O opcodes, poll/fsync opcodes, and invalid syscall argument paths.

Important APIs/types/functions: `stress_aiol_info_t` owns aligned I/O buffers, `struct iocb` arrays, `struct io_event` arrays, iocb pointer arrays, per-request file descriptors, `iovec` entries, write results, the AIO context, and completion count. Shim wrappers call `__NR_io_setup`, `io_destroy`, `io_submit`, `io_getevents`, optional `io_cancel`, and optional `io_pgetevents` directly through `syscall()`. `stress_aiol_fill_buffer()` and `stress_aiol_check_buffer()` provide deterministic data verification. `stress_aiol_submit()` handles `EAGAIN` retries and optional `EINVAL` tolerance; `stress_aiol_wait()` drains completions with short absolute timeouts.

Control flow: `stress_aiol()` resolves `aiol-requests`, caps it against `/proc/sys/fs/aio-max-nr` divided by instances, allocates all arrays, deliberately tries invalid `io_setup(0)`, creates a Linux AIO context, opens a temporary file with `O_DIRECT` fallback, opens many descriptors to the same file, then enters the synchronized run loop. Each iteration submits and waits for async `PWRITE`, validates later `PREAD` data where the prior write succeeded, submits `PWRITEV` and `PREADV`, periodically exercises invalid `io_cancel`, `io_destroy`, `io_getevents`, `io_setup`, and `io_submit` calls, optionally submits invalid `IO_CMD_POLL`, and periodically tests `IO_CMD_FDSYNC` or `IO_CMD_FSYNC`.

State and persistence behavior: persistent filesystem state is a temp file unlinked after descriptors are opened and a temp directory removed on cleanup. Kernel state is the AIO context and outstanding requests. Local state includes per-request buffers, event results, write status, completion counters, and static retry suppression for unsupported `io_pgetevents` and sync opcodes.

Dependencies and integration points: the implementation is Linux-only through syscall numbers plus `libaio.h`, `clock_gettime`, optional `poll.h`, stress-ng temp file helpers, process states, sync barriers, memory allocation helpers, filesystem hints, random helpers, and metrics. It registers `aiol-requests`, `VERIFY_ALWAYS`, and an unimplemented reason when libaio/syscall support is missing.

Risks: buffer validation includes a suspicious bounds guard, `if (bufptr >= info.buffer + BUFFER_SZ) continue;`, which rejects buffers beyond the first 4 KB slot rather than beyond the full allocation; this means most read completions can skip verification. Resource capping relies on parsing one byte from `/proc/sys/fs/aio-max-nr`, so larger values can fall back to the default guess. Direct I/O alignment, filesystem support, and kernel opcode support vary widely.

Test signals: run on kernels with and without `io_pgetevents`, with small and large `aiol-requests`, on filesystems that reject `O_DIRECT`, under low `aio-max-nr`, and with verify enabled to catch read/write mismatches. Metrics are `async I/O events completed` and `async I/O events completed per sec`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aiol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-alarm.c -->
# sources/test-tools/stress-ng/stress-alarm.c

Purpose: `stress-alarm.c` implements the `alarm` stressor. It stresses `alarm()`, `sleep()`, signal interruption, fork/reap behavior, and optional semantic verification for large, zero, and random timeout values.

Important APIs/types/functions: test-result bits are split into sleep and alarm masks for `INT_MAX`, zero, and random durations. `stress_alarm_stress_bogo_inc()` blocks `SIGUSR1` around `stress_bogo_inc()` so the parent termination signal cannot interrupt the counter update. `stress_alarm()` is the main stressor entry point and installs a parent `SIGALRM` ignore handler.

Control flow: after the sync barrier, the stressor forks a child. The child installs `SIGUSR1` as an exit handler, enables failure-injection behavior, and loops over alarm/sleep scenarios: cancel pending alarms, schedule `alarm(INT_MAX)`, reschedule it to check returned remaining time, call `sleep(INT_MAX)` expecting interruption, test `alarm(0)` and `sleep(0)`, and test a random alarm/sleep pair. It records mismatches in an exit-status bitmask. The parent repeatedly sends `SIGALRM` to interrupt the child, then sends `SIGUSR1`, waits, and, when verify is enabled, reports the bitmask categories.

State and persistence behavior: the stressor stores no persistent files or shared memory. State is the forked child, process signal dispositions, the child's exit-code mask, and the bogo counter. `stress_make_it_fail_set()` is child-local.

Dependencies and integration points: it uses `core-signal.h`, stress-ng fork retry logic, sync barriers, process-state transitions, random delay generation, `shim_kill`, `shim_nanosleep_uint64`, `shim_sched_yield`, and optional verify mode. It is registered as `CLASS_SIGNAL | CLASS_INTERRUPT | CLASS_OS` with `VERIFY_OPTIONAL`.

Risks: using an exit status as a bitmask limits result width, though the current masks fit. Parent kill loops depend on `args->time_end` and `stress_continue(args)`; changes to time accounting could leave short runs with weak coverage. Signal handler interactions are central, so global signal changes elsewhere can break assumptions.

Test signals: verify-mode failures list exact failing cases such as `sleep(INT_MAX)`, `alarm(0)`, or `alarm($RANDOM)`. Regression tests should cover fork retry paths, immediate stop, signal delivery races, and platforms with different `sleep()` interruption semantics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-alarm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-apparmor.c -->
# sources/test-tools/stress-ng/stress-apparmor.c

Purpose: `stress-apparmor.c` implements the `apparmor` stressor, which exercises AppArmor profile, feature, kernel-interface, and parser-corruption paths. It is a privileged OS/security stressor.

Important APIs/types/functions: the build requires AppArmor library/header support and `sys/select.h`; it includes generated `apparmor-data.h` policy bytes. `stress_apparmor_shared_info_t` contains lock pointers and a shared failure counter. `stress_apparmor_supported()` checks `CAP_MAC_ADMIN`, `aa_is_enabled()`, `aa_find_mountpoint()`, and readable `profiles`. `stress_apparmor_read()` and `stress_apparmor_dir()` read AppArmor sysfs/proc-style files. `apparmor_spawn()` forks synchronized child workers. Worker functions are `apparmor_stress_profiles()`, `apparmor_stress_features()`, `apparmor_stress_kernel_interface()`, and `apparmor_stress_corruption()`.

Control flow: `stress_apparmor()` allocates shared PID tracking, shared lock/counter memory, two policy-data buffers, and counter/failure locks. It spawns four children, one per AppArmor function, then starts all children after the normal sync barrier. The parent sleeps in `select(0, ...)` or `pause()` while locked bogo accounting says the stressor should continue. Shutdown sends `SIGALRM` to children through `stress_kill_and_wait_many()`.

State and persistence behavior: global process state includes `apparmor_path`, `apparmor_run`, `data_copy`, `data_prev`, and `stress_apparmor_shared_info`. Children may load, replace, and remove the generated profile, and the corruption worker preserves the last accepted corrupted policy in `data_prev`. The final return code fails if the shared failure counter is nonzero. AppArmor policy state is intended to be removed by the kernel-interface worker, but concurrent load/remove races are expected.

Dependencies and integration points: depends on libapparmor (`aa_kernel_interface_*`, `aa_is_enabled`, `aa_find_mountpoint`), stress-ng capabilities, locks, shared mmap, sync PID lists, scheduler helpers, parent-death alarms, and signal handlers. It registers `VERIFY_ALWAYS` and a supported callback; unavailable builds use `stress_unimplemented`.

Risks: this stressor mutates kernel security policy and requires elevated capability, so stale policy cleanup and concurrent EEXIST/ENOENT handling are important. Corruption tests intentionally feed malformed policy data and rely on expected `EPROTO`, `EPROTONOSUPPORT`, `ENOENT`, or `EEXIST`. Static variables inside corruption helpers are per-process but not reset between worker runs.

Test signals: skip behavior should be tested without capability, without AppArmor, without accessible `/sys/kernel/security/apparmor`, and without headers. Functional signals include zero shared failures, proper cleanup of loaded `/usr/bin/pulseaudio-eg` policy, child shutdown on `SIGALRM`, and bogo progress from all four worker lanes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-apparmor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-atomic.c -->
# sources/test-tools/stress-ng/stress-atomic.c

Purpose: `stress-atomic.c` implements the `atomic` stressor for GCC/clang `__atomic` builtins over shared stress-ng atomic fields. It stresses atomic load/store, arithmetic, bitwise, clear, fetch, and memory-order variants over 8-, 16-, 32-, and optionally 64-bit integer types.

Important APIs/types/functions: many `SHIM_ATOMIC_*` macros wrap individual `__atomic_*` builtins when available and degrade to no-op otherwise. `DO_ATOMIC_OPS()` performs 64 counted operations per call across relaxed and acquire memory orders and validates a local store/add/sub/load sequence. `stress_atomic_uint8/16/32/64()` apply the macro to `g_shared->atomic` arrays with rotating static indexes. `atomic_func_info_t` records function, metric name, and required architecture width. `stress_atomic_exercise()` runs 1000 rounds per eligible type.

Control flow: `stress_atomic()` mmaps a shared `stress_atomic_info_t` array for three children plus the parent, initializes per-process metrics and sync PIDs, forks three child workers, releases all workers at the barrier, and runs the same exercise in the parent. It then collects child statuses, kills any still running children, aggregates durations/counts per type, and emits per-type atomic-op rates.

State and persistence behavior: no files are persisted. Shared state is the mmap metrics array plus the global `g_shared->atomic` storage being mutated concurrently. Per-function static indexes select different array slots and are process-local after fork. Metrics are aggregated after child reaping.

Dependencies and integration points: it uses stress-ng shared memory (`g_shared`), fork synchronization, kill helpers, process states, metric helpers, and compile-time feature checks for `__atomic` builtins. 128-bit support is explicitly disabled with `#undef HAVE_INT128_T`. GCC 11 NAND builtins are worked around with and/xor sequences to avoid a known lock-up.

Risks: macro fallback to `DO_NOTHING()` means partial compiler feature sets can produce weaker-than-expected coverage while still compiling if at least one atomic operation exists. The validation check only proves local unshared load/store behavior, not correctness of all concurrent operations. Static indexes assume the shared arrays have power-of-two sizes because they use mask wrapping.

Test signals: build matrix coverage across compilers and 32-/64-bit targets is important, especially GCC 11 NAND behavior and missing builtin configurations. Runtime signals include child exit failures, validation failures named by integer type, and metrics such as `uint64 atomic ops per sec`, `uint32 atomic ops per sec`, etc.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-atomic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-altstack.c -->
# sources/test-tools/stress-ng/stress-bad-altstack.c

Purpose: `stress-bad-altstack.c` implements the `bad-altstack` stressor. It deliberately installs invalid alternate signal stacks and provokes faults so the kernel's signal-stack handling kills or rejects child processes cleanly.

Important APIs/types/functions: the implementation requires `sigaltstack()`. Optional `getauxval(AT_SYSINFO_EHDR)` is used to test a VDSO-backed bad stack. Global stack mappings are `stack`, `zero_stack`, and optional `bus_stack`. `stress_bad_altstack_force_fault()` reads/writes through a chosen stack address. `stress_bad_altstack_signal_handler()` runs on the signal path, unmaps stacks, fills a large local array, and `siglongjmp`s back if the handler survived. `stress_bad_altstack_child()` tries invalid flags, too-small stacks, protected stacks, NULL/text/VDSO stacks, `/dev/zero` mappings, file mappings that can bus-error, and unmapped stacks.

Control flow: the parent maps the main alt stack, optional tmpfile-backed bus-error stack, and `/dev/zero` read-only stack, forces lazy `munmap` resolution, waits at the sync barrier, and repeatedly forks children. Each child installs signal handlers and performs several randomized bad-stack attempts. The parent waits; a child death by `SIGSEGV` is considered expected and increments bogo operations, `SIGKILL` can be handled as OOM depending on flags, and non-success exits fail the stressor.

State and persistence behavior: stack mappings are process address-space state only. Optional tmpfile mappings use `O_TMPFILE`; no named file is persisted. The child unmaps inherited global mappings in the signal handler; the parent cleans up remaining mappings at finish.

Dependencies and integration points: it uses stress-ng mmap, madvise, out-of-memory adjustment, signal wrappers, parent-death alarms, scheduler settings, temp paths, and process-state tracking. It registers `CLASS_VM | CLASS_MEMORY | CLASS_OS` with `VERIFY_ALWAYS` and an unimplemented fallback without `sigaltstack()`.

Risks: this code intentionally invokes undefined and architecture-specific fault behavior. Some BSD kernels can raise `SIGILL`; OpenBSD may reject stack setup and is treated as success. Unmapping globals from a signal handler is fragile but intentional. OOM-killer handling can hide true failures if the process is killed with `SIGKILL`.

Test signals: expected progress is repeated child `SIGSEGV` termination. Good coverage includes builds with and without `O_TMPFILE`, `MAP_STACK`, `mprotect`, VDSO auxv support, and `SIGXCPU`/`RLIMIT_CPU`, plus immediate-stop handling during fork loops.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-altstack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-ioctl.c -->
# sources/test-tools/stress-ng/stress-bad-ioctl.c

Purpose: `stress-bad-ioctl.c` implements the Linux `bad-ioctl` stressor. It discovers character/block devices under `/dev` and issues malformed read/write ioctl commands and invalid user pointers to exercise driver error paths without requiring device-specific knowledge.

Important APIs/types/functions: Linux, pthreads, and `_IOR` are required. `dev_ioctl_info_t` stores device paths in a binary tree, ignore state, current 16-bit ioctl type/number state, and per-thread exercised flags. `stress_bad_ioctl_dev_dir()` recursively scans `/dev`, skipping dot entries, many numbered sibling devices, and watchdog paths. `stress_bad_ioctl_rw()` maps two pages, unmaps the second to create boundary pointers, opens the selected device, and calls `ioctl()` with `_IOR` and optional `_IOW` commands using end-of-page, NULL, `PROT_NONE`, and read-only pointers. `stress_bad_ioctl_dir()` selects devices and advances ioctl command generation by `inc`, `random`, `random-inc`, or `stride`.

Control flow: the top-level stressor builds the device tree, syncs, then repeatedly forks a child. The child installs a `SIGSEGV` longjmp handler, creates a lock, marks itself OOM-killable, starts up to four pthreads that continuously call `stress_bad_ioctl_rw()`, and also walks the device tree in the controlling thread. The parent waits for the child and restarts while the stressor continues.

State and persistence behavior: persistent state is only the in-memory device tree and per-node command state. Child threads share global `lock` and `dev_ioctl_node`; each node tracks whether all threads have exercised it before advancing the ioctl command. No files are created.

Dependencies and integration points: integrates with stress-ng option parsing, pthread wrappers, lock helpers, try-open timeouts, signal longjmp, mapped guard pages (`args->mapped->page_none/page_ro`), OOM adjustment, and fork retry logic. It is registered as `CLASS_DEV | CLASS_OS | CLASS_PATHOLOGICAL`.

Risks: issuing arbitrary ioctls to real device drivers is inherently high risk; the code avoids watchdogs but still depends on drivers returning errors promptly. A 0.25-second threshold limits slow calls per device but cannot prevent all hangs. The tree scan only includes world/group-readable/writable directories, which reduces coverage on locked-down systems.

Test signals: test with all four `bad-ioctl-method` values, no accessible devices, devices that fail `open`, device calls that trigger `SIGSEGV`, pthread creation failures, and immediate stop. Failures appear as unexpected child exit or `caught an unexpected segmentation fault`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-ioctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-besselmath.c -->
# sources/test-tools/stress-ng/stress-besselmath.c

Purpose: `stress-besselmath.c` implements the `besselmath` CPU/floating-point stressor. It repeatedly calls available libc Bessel functions (`j*` and `y*` families for double, float, and long double) and verifies deterministic sums.

Important APIs/types/functions: `stress_besselmath_method_t` maps method names to functions. Each generated function such as `stress_besselmath_j0()`, `stress_besselmath_jnf()`, or `stress_besselmath_y0l()` runs `STRESS_BESSELMATH_LOOPS` iterations over incrementing inputs, accumulates a sum, stores the first-run result in a static variable, increments bogo operations, and returns true if later sums differ beyond `PRECISION` or `PRECISION_L`. `stress_besselmath_all()` dispatches all available methods through `stress_besselmath_exercise()`.

Control flow: `stress_besselmath()` selects `besselmath-method` defaulting to `all`, clears the method metrics, waits at the sync barrier, and loops until stopped or a selected method reports a mismatch. At deinit it emits per-method operation rates for methods that ran.

State and persistence behavior: there is no persistent file or kernel state. Static per-method first-run/result variables act as process-local reference baselines. `stress_besselmath_metrics[]` stores duration and call count for later metric reporting.

Dependencies and integration points: the stressor depends on `<math.h>`, stress-ng math shim functions (`shim_j0`, `shim_y0f`, etc.), compile-time `HAVE_*` checks per libc function, option method selection, process-state tracking, sync barriers, and metrics. If no supported Bessel functions are available it registers an unimplemented method selector and `stress_unimplemented`.

Risks: static reference sums assume deterministic libc behavior for the same process and floating-point environment; changes to rounding modes, libm vectorization, or architecture-specific precision can cause false positives. `all` does not report a method name in the first failure except through the nested nonzero index check.

Test signals: build coverage should include systems with only double functions, with float/long-double variants, and with none. Runtime tests should use individual methods and `all`, verify mismatch reporting, and check metrics like `j0 ops per second`, `ynf ops per second`, and long-double variants when present.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-besselmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bigheap.c -->
# sources/test-tools/stress-ng/stress-bigheap.c

Purpose: `stress-bigheap.c` implements the `bigheap` VM/OS stressor. It grows heap allocations with `malloc`, `calloc`, and `realloc`, optionally locks future mappings, writes and verifies pointer patterns, and runs inside an OOM-manageable child.

Important APIs/types/functions: options are `bigheap-bytes`, `bigheap-growth`, and `bigheap-mlock`. Phase constants name the current allocation/check stage and feed `stress_bigheap_phase()`. `stress_bigheap_segvhandler()` records fault signal data and longjmps out. `stress_bigheap_child()` owns allocation growth, low-memory avoidance, optional `malloc_trim()`, aggressive-mode extra realloc/calloc behavior, page/full-heap writes, optional verification, metrics, and cleanup. `stress_bigheap()` wraps the child with `stress_oomable_child()`.

Control flow: the child installs a SIGSEGV handler, resolves options with maximize/minimize behavior, rounds growth to page size, syncs, optionally `mlockall(MCL_FUTURE)`, then repeatedly grows or resets the allocation. When the configured byte limit or low-memory check is reached it frees and restarts from zero. Successful allocations are filled with their own addresses at page or pointer stride, optionally verified, and counted. Allocation failures reset size and continue unless a signal is caught.

State and persistence behavior: no files are persisted. State is heap memory, `phase`, fault metadata, last allocation address/end, and metrics for realloc calls. `malloc_trim(0)` may return heap pages to the allocator/system when available.

Dependencies and integration points: uses stress-ng OOM child handling, memory-free reporting, signal longjmp, process states, option parsing, `malloc_trim` feature checks, `mlockall`, and metrics. It registers `VERIFY_OPTIONAL` and is unimplemented without siglongjmp support.

Risks: pointer-pattern verification can fault if allocator metadata or overrun bugs are introduced, which is intentional but makes signal reporting critical. `bigheap_growth` is stored as `uint64_t` then rounded with page-size arithmetic; bounds and overflow should remain guarded by option parsing. OOM handling may mask allocation stress behavior depending on global flags.

Test signals: use low byte limits, high growth, aggressive mode, `bigheap-mlock`, verify mode, and OOM-avoid flags. Regression signals include SIGSEGV phase reports, verify mismatch messages, skip on allocation failure, and the `realloc calls per sec` metric.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bigheap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bind-mount.c -->
# sources/test-tools/stress-ng/stress-bind-mount.c

Purpose: `stress-bind-mount.c` implements the Linux `bind-mount` stressor. It repeatedly bind-mounts `/bin` onto a temporary directory, stats files through the mounted view, unmounts, and records mount/unmount latency.

Important APIs/types/functions: the stressor is gated on Linux bind-mount flags, `clone()` namespace constants, and capability checks for `CAP_SYS_ADMIN`. `stress_bind_mount_supported()` skips without the capability. `stress_bind_mount_child_handler()` clears the continue flag on `SIGALRM` and exits for other signals. `stress_bind_mount_exercise()` performs the mount using either modern `open_tree()`/`move_mount()` or legacy `mount(MS_BIND | MS_REC)`, validates visibility by comparing `lstat()` success under `/bin` and the bind target, retries `umount2(MNT_DETACH)` or `umount()`, and records metrics.

Control flow: `stress_bind_mount()` syncs, creates a temporary mount point, and repeatedly calls `stress_bind_mount_exercise()` until the stressor stops or an exercise fails. The exercise function installs handlers, sets a parent-death alarm, attempts one mount/unmount cycle per loop, increments bogo operations after unmount, and removes the path as a child-side safety cleanup.

State and persistence behavior: persistent state is a temporary directory and a transient mount. The directory is removed in both exercise and top-level cleanup. Mount state should be detached each iteration; stale mounts are the main persistence risk.

Dependencies and integration points: depends on stress-ng capability helpers, temp path helpers, filesystem stat helpers, signal wrappers, process-state transitions, and metrics. It is classified as filesystem, OS, and pathological, with `VERIFY_ALWAYS`.

Risks: requires elevated privilege and mutates mount namespace state. The compile-time gate mentions user/mount namespace clone constants but the code itself does not create a new namespace here, so running in the caller's namespace can be dangerous if cleanup fails. It assumes `/bin` exists and is suitable as the bind source.

Test signals: run with and without `CAP_SYS_ADMIN`, with `open_tree`/`move_mount` available and unavailable, on systems without `/bin`, and under forced `ENOSPC`, `EACCES`, or `ENOENT`. Metrics are `microsecs per mount` and `microsecs per umount`; stat failures across the bind target are reported.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bind-mount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-binderfs.c -->
# sources/test-tools/stress-ng/stress-binderfs.c

Purpose: `stress-binderfs.c` implements the privileged Linux `binderfs` stressor. It mounts binderfs, opens `binder-control`, creates many binder devices with `BINDER_CTL_ADD`, unlinks them, unmounts, and records mount/unmount latency.

Important APIs/types/functions: support depends on Linux Android binder and binderfs headers plus `CAP_SYS_ADMIN`. `stress_binderfs_supported()` probes binderfs by creating a temp directory and trying either the new mount API (`fsopen`, `fsconfig`, `fsmount`, `move_mount`) or legacy `mount("binder", ..., "binder")`. `stress_binderfs_umount()` retries `umount()` for up to 15 seconds on `EBUSY`, then exercises duplicate and invalid unmount calls. `stress_binderfs()` owns the main mount/device/unmount loop.

Control flow: after temp directory setup and sync, each iteration mounts binderfs at a generated path, opens `binder-control`, optionally loops over 256 `BINDER_CTL_ADD` calls naming devices `sng-N`, unlinks the created device paths, closes control, unmounts with retry, and increments bogo operations. Error handling distinguishes unsupported/no-resource skip cases (`ENODEV`, `ENOSPC`, `ENOMEM`, `EPERM`) from hard failures.

State and persistence behavior: state includes the temp directory, transient binderfs mount, binder-control file descriptor, and created binder device nodes. Cleanup removes the stress-ng temp directory and unmounts on normal paths; stale mounts/device nodes are the key persistence risk after abnormal termination.

Dependencies and integration points: integrates with stress-ng temp-dir helpers, capability checks, filesystem path building, process states, metrics, and kernel binderfs ioctls. It registers a supported callback and `VERIFY_ALWAYS`; unavailable builds register `stress_unimplemented`.

Risks: privileged filesystem mutation and binder device creation can consume kernel resources. The supported probe may leave a mount if an intermediate new-mount-api step succeeds but later cleanup misses a state transition. `stress_binderfs()` sets `rc = EXIT_SUCCESS` before `clean`, which can override a break from an unmount failure path after the loop.

Test signals: cover systems without binderfs, without capability, with new and old mount APIs, with `BINDER_CTL_ADD` defined and absent, and with busy mounts requiring retry. Metrics are `microsecs per mount` and `microsecs per umount`; failures include inability to open `binder-control` or timed-out unmount.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-binderfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitonicsort.c -->
# sources/test-tools/stress-ng/stress-bitonicsort.c

Purpose: `stress-bitonicsort.c` implements the `bitonicsort` CPU/cache/memory sort stressor for 32-bit integer arrays. It performs forward and reverse bitonic sorts and optional order verification.

Important APIs/types/functions: options include `bitonicsort-size`. `bitonicsort32_fwd()` and `bitonicsort32_rev()` implement compare/swap networks over the full array, updating global `bitonic_count`. Optional `stress_bitonicsort_handler()` uses `siglongjmp` on `SIGALRM` for graceful timeout escape. The main `stress_bitonicsort()` allocates data with `stress_mmap_populate()`, initializes/shuffles/mangles data through `core-sort`, and emits comparison metrics.

Control flow: after resolving size with maximize/minimize overrides, the stressor mmaps the data array, optionally installs the alarm longjmp handler, initializes sorted data, syncs, then loops. Each iteration shuffles data, forward sorts and verifies ascending order, reverse sorts and verifies descending order, mangles data, reverse sorts again, verifies, and increments bogo operations.

State and persistence behavior: no persistent state exists beyond the anonymous mapping. Runtime state includes the data array, `bitonic_count`, optional jump buffer flag `do_jmp`, and comparison/duration counters. The mapping is named and advised for collapse/hugepage behavior when supported.

Dependencies and integration points: depends on `core-sort` data generation/comparison helpers, mmap/madvise helpers, signal wrappers, option parsing, sync barriers, process states, and metrics. It is registered with `VERIFY_OPTIONAL`.

Risks: bitonic sort algorithms generally assume power-of-two element counts for full correctness, while `bitonicsort-size` is a byte-like numeric option without obvious power-of-two rounding. Non-power-of-two sizes may expose ordering issues. Longjmp cleanup must restore the previous alarm handler and unmap data.

Test signals: run minimum, default, maximum, and non-power-of-two sizes with verify enabled. Check forward/reverse order failure messages, timeout behavior via `SIGALRM`, skip on mmap failure, and metrics `bitonicsort comparisons per sec` and `bitonicsort comparisons per item`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitonicsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitops.c -->
# sources/test-tools/stress-ng/stress-bitops.c

Purpose: `stress-bitops.c` implements the `bitops` CPU/integer/compute stressor. It benchmarks and self-verifies common bit manipulation idioms against simpler baseline implementations.

Important APIs/types/functions: `stress_bitops_method_info_t` maps method names to functions. Methods include `abs`, `bswap`, `countbits`, `clz`, `ctz`, `cmp`, `log2`, `max`, `min`, `parity`, `pwr2`, `reverse`, `rnddnpwr2`, `rnduppwr2`, `sign`, `swap`, and `zerobyte`, plus rotating `all`. Conditional builtins include popcount, clz, ctz, parity, and bitreverse. `stress_bitops_callfunc()` measures a method and accumulates per-method metrics.

Control flow: `stress_bitops()` clears metrics, selects `bitops-method`, waits at the sync barrier, then repeatedly calls the selected method until failure or stop, incrementing bogo operations after each successful call. The `all` method delegates through `stress_bitops_callfunc()` to one concrete method per invocation, rotating through all non-`all` entries. At deinit, metrics are reported for methods that accumulated measured duration.

State and persistence behavior: no files or kernel objects are persisted. Runtime state is local arithmetic state, the static rotation index in `stress_bitops_all()`, and the global metrics array. `stress_put_uint32()` consumes sums to keep optimizing compilers from removing work.

Dependencies and integration points: the stressor uses stress-ng random number generation, target-clone annotations, architecture and builtin feature macros, option method selection, sync barriers, process states, and metrics. It registers `VERIFY_ALWAYS` and exposes `max_metrics_items`.

Risks: several methods rely on signed shifts, overflow-style wraparound, or compiler builtin semantics; cross-compiler and sanitizer builds may behave differently even when the stressor is valid for stress-ng's supported build modes. The top-level direct call path ignores the `count` returned by the selected method except for `all`, so metrics are primarily populated when `all` is selected.

Test signals: run every individual `bitops-method` plus `all`, across compilers with different builtin availability. Failures identify the method and mismatched values. Metrics are named `<method> mega-ops per second` for measured delegated calls.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bitops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-branch.c -->
# sources/test-tools/stress-ng/stress-branch.c

Purpose: `stress-branch.c` implements the `branch` stressor. It uses GCC labels-as-values and a large computed-goto table to produce hard-to-predict indirect branches.

Important APIs/types/functions: the implementation is gated on `HAVE_LABEL_AS_VALUE` and excludes PCC. `RESEED_JMP(n)` updates periodic counters, advances a linear congruential pseudo-random seed, selects the next label, and jumps to the previously selected label. `J(n)` expands each numbered label body. `stress_branch()` contains a 1024-entry static label table and 16 counters, one for every 64th label.

Control flow: after zeroing counters and passing the sync barrier, execution enters label `L0x000`. Each label reseeds and computed-gotos to the next selected label; `L0x000` also increments bogo operations, optionally yields on SH4, and checks `stress_continue(args)`. After stopping, the stressor validates that every sampled 64th label execution count falls within +/-10 percent of the bogo count when enough samples were collected.

State and persistence behavior: state is purely in-process: the seed, next-label pointer, bogo counter, and static counters array. There is no persistent storage or kernel state.

Dependencies and integration points: depends on compiler support for addressable labels, stress-ng process-state handling, bogo counters, architecture macros, and optional scheduler yield. It registers `CLASS_CPU` with `VERIFY_ALWAYS`; unsupported compilers get an unimplemented reason.

Risks: this source is tightly coupled to compiler extensions and optimizer behavior. The distribution check assumes the pseudo-random sequence and sampled labels stay proportional to bogo increments; changes to where bogo is incremented can cause false verification failures. Computed goto can be difficult for sanitizers, coverage tools, and non-GNU compilers.

Test signals: build with GCC/clang, verify unsupported fallback on compilers without labels-as-values, run enough operations to trigger the 10 percent distribution check, and cover SH4/QEMU yield behavior if relevant. Failure messages name the branch label index and expected counter range.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-branch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-brk.c -->
# sources/test-tools/stress-ng/stress-brk.c

Purpose: `stress-brk.c` implements the `brk` VM/OS stressor. It rapidly grows, shrinks, resets, and partly unmaps the process data segment through `brk()` and `sbrk()`.

Important APIs/types/functions: `brk_context_t` stores shared counts, durations, byte limits, and options (`brk-mlock`, `brk-notouch`). `stress_brk_supported()` probes `sbrk(0)` and `brk(current)` for `ENOSYS`. `stress_brk_page_resident()` optionally touches the newest page and marks it mergeable. `stress_brk_child()` performs the actual page-by-page expand/shrink/reset/unmap loop and verifies a pointer check value at the end of pages. `stress_brk()` allocates shared context and wraps the child in `stress_oomable_child()`.

Control flow: top-level setup resolves options, syncs, then runs the OOM-able child. The child records the starting program break, optionally `mlockall(MCL_FUTURE)`, and loops through phases: reset when over the byte limit, shrink back toward start, avoid low memory if requested, expand by one page for several iterations, call `brk()` on the current position, shrink one page, verify the stored sentinel, and occasionally force-unmap a page from the brk region.

State and persistence behavior: no filesystem state is persisted. Process memory state is intentionally mutated through the program break and forced unmaps. Shared mmap state holds metrics visible to the parent after child completion.

Dependencies and integration points: integrates with stress-ng shim wrappers for `brk`/`sbrk`, anonymous shared mmap, OOM child control, memory-low checks, non-temporal load support, madvise, mlock, process states, options, and metrics.

Risks: manipulating the process break can interact badly with malloc or libraries if future changes allocate in the same child loop. Forced unmap inside the brk region is pathological by design and can expose kernel/libc assumptions. `brk-notouch` changes residency and can hide page-fault behavior.

Test signals: cover unsupported `sbrk`/`brk`, low `brk-bytes`, `brk-mlock`, `brk-notouch`, OOM-avoid behavior, and sentinel verification failures. Metrics are `nanosecs per sbrk page expand` and `nanosecs per sbrk page shrink`; debug logs count out-of-memory, expands, and shrinks.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-brk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bsearch.c -->
# sources/test-tools/stress-ng/stress-bsearch.c

Purpose: `stress-bsearch.c` implements the `bsearch` CPU/cache/memory search stressor. It searches every element in a sorted 32-bit integer array using libc binary search, an internal binary search, or a ternary-search variant.

Important APIs/types/functions: `bsearch_func_t` abstracts libc-compatible search functions. `bsearch_nonlibc()` is a standard lower/upper binary search. `bsearch_ternary()` probes two midpoints and narrows thirds. `stress_bsearch_methods[]` conditionally includes libc `bsearch`, plus nonlibc and ternary implementations. `stress_bsearch()` owns allocation, repeated search, verification, and metrics.

Control flow: the stressor resolves `bsearch-method` and `bsearch-size`, rounds allocation up to a multiple of 8 elements, mmaps the data array, syncs, then loops. Each iteration initializes sorted data, resets sort comparison counters, searches for every element with the selected method and `stress_sort_cmp_fwd_int32`, optionally verifies the returned pointer/value, records duration and comparison count, and increments bogo operations.

State and persistence behavior: state is an anonymous mapped array and comparison counters managed by `core-sort`. No files or persistent kernel resources are used.

Dependencies and integration points: depends on optional `<search.h>`/`bsearch`, stress-ng mmap helpers, core sort initialization/comparison helpers, option method selection, process states, sync barriers, and metrics. It is `VERIFY_OPTIONAL`.

Risks: `bsearch_ternary()` uses `while (upper >= lower)` with unsigned `size_t`; if `mid1` is zero and `cmp1 < 0`, `upper = mid1 - 1` underflows. Sorted input and exact-key searches reduce exposure, but missing-key tests would be risky. Method names in help mention only two methods while the table includes `ternary`.

Test signals: run every method, minimum/default/maximum sizes, verify mode, and missing-key unit coverage for `bsearch_ternary()` if isolated. Metrics are `bsearch comparisons per sec` and `bsearch comparisons per item`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bubblesort.c -->
# sources/test-tools/stress-ng/stress-bubblesort.c

Purpose: `stress-bubblesort.c` implements the `bubblesort` CPU/cache/memory/hot sort stressor. It sorts 32-bit integer arrays using either an optimized bubble-sort pass or a naive swapped-loop implementation.

Important APIs/types/functions: `bubblesort_func_t` abstracts qsort-like sort functions. `bubblesort_fast()` tracks the last swap position and shortens the next pass. `bubblesort_naive()` performs full passes until no swaps occur. Both use `stress_sort_swap_func(size)` and the comparator supplied by `core-sort`. `stress_bubblesort_methods[]` exposes `bubblesort-fast` and `bubblesort-naive`; `stress_bubblesort()` handles option parsing, allocation, sorting, verification, and metrics.

Control flow: the stressor selects method and size, mmaps a 32-bit integer array, optionally installs a `SIGALRM` longjmp handler, initializes data, syncs, then loops. Each iteration shuffles data, sorts ascending and optionally verifies, sorts descending and verifies, mangles data, reverse-sorts again and verifies, and increments bogo operations. Comparison counts are collected through `stress_sort_compare_get()`.

State and persistence behavior: no persistent state is created. Runtime state is the anonymous mapping, selected method, optional jump state, comparison/duration counters, and process signal disposition. The mapping is named `bubblesort-data` and may be advised for collapse.

Dependencies and integration points: integrates with stress-ng mmap/madvise, signal wrappers, core sort helpers, option method selection, process states, sync barriers, and metrics. It registers `VERIFY_OPTIONAL` and classifier bits including `CLASS_HOT`.

Risks: bubble sort is intentionally expensive; maximum sizes can produce long iterations, making the `SIGALRM` escape path important. The help string for `bubblesort-method` appears to miss a closing bracket in the user-facing text. Longjmp paths must restore the prior alarm handler before cleanup.

Test signals: run both methods, verify mode, small/default/maximum sizes, forced alarm/timeout behavior, and mmap failure skip paths. Metrics are `bubblesort comparisons per sec` and `bubblesort comparisons per item`; order failures identify ascending or reverse sort errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bubblesort.c -->
