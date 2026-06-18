<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cache.c -->
# sources/test-tools/stress-ng/stress-cache.c

## Purpose
Implements the `cache` stressor, a CPU cache stress test that walks the shared `g_shared->mem_cache` buffer with pseudo-random read, write, and mixed write operations. It optionally injects architecture cache operations such as prefetch, cache-line flush, write-back, fences, demote, and RISC-V CBO handling to create poor locality and exercise instruction support.

## Important APIs, Types, and Functions
The public integration point is `stress_cache_info`, classified as `CLASS_CPU_CACHE`, with command options in `opts`. `CACHE_FLAGS_*` define optional cache instructions and behavior, while `mask_flag_info_t` maps flags to user-visible names. `CACHE_WRITE_USE_MOD()` generates 256 specialized `stress_cache_write_mod_0xNN()` functions, indexed by `cache_mixed_ops_funcs`, so each bitmask can be compiled as a constant. `stress_cache_read()`, `stress_cache_write()`, `stress_cache_flush()`, `stress_cache_bzero()`, and `stress_cache_permute()` cover read/write loops, invalid cacheflush probes, RISC-V zeroing, and flag-order permutation. Signal handlers use `sigsetjmp`/`siglongjmp` to recover from SIGSEGV, SIGBUS, and SIGILL.

## Control Flow
`stress_cache()` gathers options, filters unavailable instructions using compile-time feature macros and runtime CPU probes, installs signal handlers, creates an intentionally invalid address, clears the shared cache buffer, waits at the stress-ng synchronization barrier, then cycles through mixed, read, and write phases until `stress_continue()` ends. Mixed mode either uses the active flag mask or walks permutations. Each loop optionally changes CPU affinity, flushes instruction/data cache ranges, periodically probes invalid cache operations, and records metrics.

## State and Persistence Behavior
Runtime state is process-local plus shared memory in `g_shared->mem_cache`. The stressor tracks current buffer offsets, active/disabled cache flags, per-mode metrics, CPU affinity state, and signal recovery state. It does not persist files. The only intentionally invalid memory state is a mapped then unmapped page used to test fault handling.

## Dependencies and Integration Points
Depends on stress-ng core APIs for settings, metrics, bogo accounting, signals, affinity, random numbers, CPU cache information, cacheflush shims, and architecture assembly wrappers from x86 and RISC-V headers. It integrates with global shared memory prepared by stress-ng's cache infrastructure and with the common option parser through `OPT_cache_*` entries.

## Risks and Edge Cases
Architecture instructions may be compiled in but unsupported by the current CPU, so SIGILL masking is required. Invalid cacheflush probes can fault and are guarded by longjmp. Affinity changes can fail or be constrained by cpusets. Some options are no-ops on unsupported builds, and permutation counts can explode with many flags. Incorrect mask filtering could select undefined instructions or misreport metrics.

## Test Signals
Useful signals are successful startup with reported active/ignored flags, no unhandled SIGILL/SIGBUS/SIGSEGV, nonzero "cache ops per second", read, and write metrics, and optional logs showing disabled flags rather than crashes. Verification should cover plain mode, `--cache-enable-all`, `--cache-permute`, and `--cache-no-affinity` on systems with and without cache instruction support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cachehammer.c -->
# sources/test-tools/stress-ng/stress-cachehammer.c

## Purpose
Implements the `cachehammer` stressor, which repeatedly applies cache and memory access primitives to pairs of addresses across shared cache memory, local anonymous mappings, a shared file-backed page, and intentionally invalid pages. It is designed to hammer cache coherency, prefetch, flush, write-back, architecture-specific cache instructions, and optional NUMA page movement.

## Important APIs, Types, and Functions
`stress_cachehammer_info` exposes the stressor with `init`, `deinit`, options, and per-method metrics. `stress_cachehammer_context_t` holds active buffers, page masks, method index, valid/trapped method bitsets, NUMA masks, and runtime flags. `stress_cachehammer_func_t` describes each hammer method with a name, permutation eligibility, validity predicate, and `hammer_func_t`. Methods include generic read/write/read-write variants, `clearcache`, x86 `clflush`, `clflushopt`, `clwb`, `cldemote`, prefetch variants, RISC-V `cbo_zero`, and PowerPC cache block operations when available.

## Control Flow
`stress_cachehammer_init()` creates a temporary directory and file containing one page for shared file-backed mappings; `deinit` removes it. `stress_cachehammer()` builds the valid method mask, optionally reduces it to permutation-capable operations, maps a local buffer, local page, bad page, and file page, installs signal handlers, then runs either random method selection or flag permutation. `stress_cachehammer_exercise()` chooses one of several address classes and invokes the active hammer method, updating per-method timing. Faulting methods are recorded in `ctxt.trapped` and skipped on later iterations.

## State and Persistence Behavior
The stressor creates a temporary `cachehammer` directory and `mmap-page` file for the lifetime of the run, then removes them in `deinit`. It keeps a global context because signal handlers need to mark the currently executing method. Memory state spans `g_shared->mem_cache.buffer`, anonymous local mappings, a shared file mapping, and optional NUMA masks. Metrics are stored per hammer method.

## Dependencies and Integration Points
Uses stress-ng core helpers for temp files, shared cache memory, random numbers, metrics, settings, signal handling, NUMA, and architecture feature checks. It depends on architecture assembly wrappers in generic, x86, RISC-V, and PowerPC headers, plus `msync`, `mmap`, and optional Linux memory policy support. Options are `cachehammer-method` and `cachehammer-numa`.

## Risks and Edge Cases
The method table can have more entries than a 32-bit mask can safely represent if extended without widening bitsets. Some valid predicates rely on runtime CPU probes; wrong probes can trigger SIGILL and method trapping. Temporary file setup failure skips the stressor. NUMA randomization must tolerate unavailable policy APIs or node masks. Bad-page probes intentionally risk faults, so signal recovery must stay correct.

## Test Signals
Expected evidence includes log output listing the selected method and available operations, nonzero per-operation `cache bogo-ops/sec` metrics, clean cleanup of the temporary file and directory, and disabled-operation logs after trapped signals rather than process termination. Exercise both `--cachehammer-method random` and `permute`, with and without `--cachehammer-numa`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cachehammer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cacheline.c -->
# sources/test-tools/stress-ng/stress-cacheline.c

## Purpose
Implements the `cacheline` stressor, which coordinates multiple processes to pound different byte offsets in shared cache-line storage. It verifies that repeated adjacent, atomic, bit, copy, read/write, and width-varied access patterns do not corrupt the targeted byte while creating cache-line contention.

## Important APIs, Types, and Functions
`stress_cacheline_info` registers the stressor, `init`/`deinit`, `cacheline-affinity`, and `cacheline-method`. `stress_cacheline_method_t` maps method names to `stress_cacheline_func` callbacks. Methods include `adjacent`, `copy`, `inc`, `rdwr`, `mix`, `rdfwd64`, `rdrev64`, `rdints`, `bits`, and optional `atomicinc`. `get_L1_line_size()` queries CPU cache metadata, while `stress_cacheline_next_idx()` uses a shared lock to allocate even byte offsets.

## Control Flow
Initialization creates a shared lock and resets the global cacheline index. `stress_cacheline()` installs SIGCHLD handling, gets a unique offset, computes how many child processes are needed to span the L1 line size across instances, optionally forks helpers, synchronizes them, and runs `stress_cacheline_child()` in parent and children. Each child repeatedly invokes the selected method and may rotate CPU affinity. Parent increments bogo operations.

## State and Persistence Behavior
State lives in `g_shared->cacheline`: a shared buffer, index, size, and lock. Per-run child PID arrays are mmaped only when helper processes are needed. The stressor does not create persistent files. Cleanup kills/waits helper processes, unmaps PID storage, and destroys the lock in `deinit`.

## Dependencies and Integration Points
Depends on stress-ng shared memory, locking, sync PID helpers, CPU cache discovery, affinity helpers, random functions, and memory barriers. It integrates with stress-ng method option parsing and process-state reporting, and uses architecture-independent volatile memory accesses to force cache traffic.

## Risks and Edge Cases
Incorrect L1 line-size detection falls back to 64 bytes, which may under- or over-cover unusual hardware. Fork failures or PID mmap failures skip or reduce coverage. The methods assume the shared buffer has enough cacheline-sized storage and that byte offsets remain distinct. Optional affinity calls can fail under cpuset or permission limits.

## Test Signals
Good signals are startup logs showing process count and L1 line size, nonzero bogo progress, no "cache line error" failures, and clean child reaping. Run at least `--cacheline-method all`, one individual method, and `--cacheline-affinity` on a system with multiple CPUs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cacheline.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cap.c -->
# sources/test-tools/stress-ng/stress-cap.c

## Purpose
Implements the `cap` stressor, which exercises Linux capability retrieval and setting APIs against known PIDs, the current worker, parent process, and numeric entries in `/proc`.

## Important APIs, Types, and Functions
`stress_cap_info` registers the stressor or an unimplemented stub when capability headers are unavailable. `stress_capgetset_pid()` wraps `capget()` and optional `capset()` using `_LINUX_CAPABILITY_VERSION_3` and `_LINUX_CAPABILITY_U32S_3`, then probes invalid versions and PIDs plus older capability versions when present. The stressor uses `struct __user_cap_header_struct` and `struct __user_cap_data_struct`.

## Control Flow
`stress_cap()` synchronizes, then loops through fixed PID checks, the current worker with `capset`, the parent PID, and all numeric `/proc` entries. Each `stress_capgetset_pid()` call tolerates ESRCH for non-required PIDs but reports unexpected failures. Bogo count increments inside the helper after each capability test sequence.

## State and Persistence Behavior
The file maintains no persistent state. Per-call capability structs are zeroed on the stack. It reads `/proc` directory entries but writes no files.

## Dependencies and Integration Points
Depends on Linux capability headers, `/proc`, stress-ng logging, sync, bogo, and unused PID helpers. `verify = VERIFY_ALWAYS` makes unexpected syscall behavior visible during stress-ng verification.

## Risks and Edge Cases
PID races are normal while iterating `/proc`; ESRCH handling must distinguish expected missing processes from required PIDs. `capset` can fail due to permissions. Build environments without `sys/capability.h` or version 3 capability definitions receive an unimplemented stressor.

## Test Signals
Successful runs should produce bogo operations without unexpected `capget` or `capset` failures. Test on a normal unprivileged Linux session and a privileged/root session to cover permission differences.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cgroup.c -->
# sources/test-tools/stress-ng/stress-cgroup.c

## Purpose
Implements the `cgroup` stressor, which repeatedly mounts cgroup v2, reads and writes controller files, moves a child process into and out of a subgroup, and unmounts the hierarchy.

## Important APIs, Types, and Functions
`stress_cgroup_info` registers the stressor with a `supported` callback requiring `CAP_SYS_ADMIN`. `stress_cgroup_mount()` forks a child for mount work. `stress_cgroup_child()` creates a temp mount point and mounts cgroup2 using either the modern `fsopen`/`fsconfig`/`fsmount`/`move_mount` path or `mount()`. Helpers handle mount-state detection from `/proc/mounts`, retrying unmounts, reading files, enabling controllers, and manipulating `cgroup.procs`.

## Control Flow
The parent synchronizes, forks a mount child, waits for completion, and restarts if the child appears OOM-killed. The child creates a realpath temp directory, mounts cgroup2, updates subtree controls, reads standard cgroup files, creates a `stress-ng-PID` subgroup with a busy child process, iterates a large table of controller values to read/write, then unmounts with retries and removes the temp directory.

## State and Persistence Behavior
State is temporary but privileged: a cgroup2 mount, subgroup directory, controller file writes, a forked workload process, and a temp directory. Cleanup attempts forced or repeated unmounts and directory removal. No intended persistent repository state is written.

## Dependencies and Integration Points
Depends on Linux cgroup v2, mount APIs, CAP_SYS_ADMIN, stress-ng temp filesystem helpers, file read/write helpers, process kill/wait helpers, scheduling, and memory-pressure helpers. Integrates with stress-ng support checks so it is skipped without privileges.

## Risks and Edge Cases
This stressor can affect kernel cgroup state and can trigger OOM conditions. Mount and unmount races require retry logic. Controllers vary by kernel configuration, so many reads/writes intentionally ignore failure. Cleanup failures can leave a mounted temp path if the kernel refuses unmount. Running without CAP_SYS_ADMIN skips.

## Test Signals
Useful signals include clean skip without privileges, successful mount/read/write/unmount cycles with bogo increments when privileged, no lingering mount at the temp realpath, and expected debug retry counts instead of fatal failures.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-cgroup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chattr.c -->
# sources/test-tools/stress-ng/stress-chattr.c

## Purpose
Implements the Linux `chattr` stressor, exercising ext-style inode attribute get/set ioctls over individual flags and generated flag permutations on a shared temporary file.

## Important APIs, Types, and Functions
`stress_chattr_info` exposes the stressor on Linux or an unimplemented stub elsewhere. `stress_chattr_flag_t` maps EXT2/EXT3/EXT4/NOCOW flag bits to chattr-style characters. `do_chattr()` opens the file, allocates/mmap's a page, reads original flags with `SHIM_EXT2_IOC_GETFLAGS`, clears and sets flags with `SHIM_EXT2_IOC_SETFLAGS`, verifies selected flag subsets when single-instance, probes illegal flags, and uses a signal handler to survive mmap write faults.

## Control Flow
`stress_chattr()` installs SIGSEGV/SIGBUS handlers, builds the supported mask, computes flag permutations, creates a temp directory shared by worker instances, then loops through each known flag plus one permutation. Unsupported filesystems return `EXIT_NOT_IMPLEMENTED` after all attempts fail. It records successful flag-set rate as a metric and removes the file and directory.

## State and Persistence Behavior
Creates a temporary directory and shared file derived from the parent PID. It changes inode attributes and writes to a file-backed mapping but restores/clears flags and unlinks the file on each helper pass and at cleanup. Runtime signal state is held in `jmp_env` and `do_jmp`.

## Dependencies and Integration Points
Uses Linux `ioctl`, stress-ng temp file helpers, flag permutation helper, signal handling, mmap/fallocate wrappers, fsync/unlink wrappers, metrics, and filesystem-type diagnostics. Multiple stressor instances intentionally contend on the same file.

## Risks and Edge Cases
Filesystem support differs widely; EOPNOTSUPP, ENOTTY, EPERM, and EINVAL are expected. Immutable or append-only flags can interfere with writes and cleanup if not cleared. Mmap writes may fault under certain attributes. Concurrent workers can observe non-deterministic flags, so strict verification is limited to one instance.

## Test Signals
Expected signals include either a clear "not supported on filesystem" skip or nonzero "successful chattr flags set per sec". There should be no lingering temp file with restrictive attributes. Test on ext-family filesystems and a non-supporting filesystem such as tmpfs if available.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chattr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chdir.c -->
# sources/test-tools/stress-ng/stress-chdir.c

## Purpose
Implements the `chdir` stressor, which creates many temporary directories and repeatedly exercises `chdir()` and `fchdir()` success and failure paths.

## Important APIs, Types, and Functions
`stress_chdir_info` registers options including `chdir-dirs`. `stress_chdir_info_t` stores each generated path, open directory fd, and mkdir status. The main `stress_chdir()` function handles directory creation, open fd collection, permission-denial probing, invalid path tests, cleanup, and the "chdir calls per sec" metric.

## Control Flow
The stressor chooses directory count from settings or minimize/maximize flags, allocates metadata, records the original cwd, creates a stress-ng temp directory, populates many child directories, then synchronizes. The run loop changes into each created path, randomly `fchdir()`s to another directory fd, changes to `/`, optionally removes permissions and probes access failure for non-root, returns to the original cwd, and then probes bad, non-directory, invalid-fd, empty, and overlong path cases.

## State and Persistence Behavior
Creates up to `chdir-dirs` temporary directories and holds open fds to them. It must always restore the original cwd before cleanup. Cleanup closes fds, removes each created directory, removes the temp root, frees path strings, and emits a tidy message if removal takes long.

## Dependencies and Integration Points
Depends on stress-ng temp filesystem helpers, capability checks for root, random generation, metrics, filesystem diagnostics, and option parsing. It integrates with stress-ng minimize/maximize behavior for resource scaling.

## Risks and Edge Cases
Large directory counts can hit memory, inode, link-count, or disk-space limits. Failing to restore cwd would break cleanup and later stressors. Permission-denial checks are skipped for root because root may bypass access mode. Concurrent filesystem pressure can cause ENOMEM/ENOSPC/EMLINK paths.

## Test Signals
Good signals include successful cleanup of all generated directories, nonzero chdir-rate metric, correct skip/no-resource behavior under low resources, and no unexpected failures for known invalid path probes.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chdir.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chmod.c -->
# sources/test-tools/stress-ng/stress-chmod.c

## Purpose
Implements the `chmod` stressor, repeatedly changing permission and special mode bits on a shared temporary file via `fchmod`, `chmod`, `fchmodat`, and `fchmodat2` paths.

## Important APIs, Types, and Functions
`stress_chmod_info` registers the stressor. The `modes[]` table is compiled from available `S_ISUID`, `S_ISGID`, sticky, and read/write/execute bits. `stress_chmod_check()` filters expected race or platform errors. `do_fchmod()` exercises fd-based mode changes plus an invalid fd. `do_chmod()` applies mode permutations and path-based variants including directory-fd calls and invalid path probes.

## Control Flow
`stress_chmod()` builds the full mode mask and permutations, creates a shared temp directory and file, opens the directory for `*at` calls, synchronizes workers, and loops through incremental masks over all modes. Each iteration calls fd and path variants, fsyncs the file, and increments bogo operations. Cleanup restores permissive mode, closes fds, unlinks the file, removes the directory, and frees permutations.

## State and Persistence Behavior
All state is temporary: one shared file per parent PID, one temp directory, one file fd, one directory fd, generated long path string, and mode permutation storage. No persistent state is intended after cleanup.

## Dependencies and Integration Points
Uses stress-ng temp path helpers, bad-fd helper, flag permutation helper, basename handling, shim wrappers for newer syscalls, metrics through bogo operations, and filesystem diagnostics. Multiple worker instances intentionally share the same target file.

## Risks and Edge Cases
Concurrent workers can remove or race on the same file, so ENOENT and ENOTDIR are treated as benign. Some platforms lack `fchmodat2` or have filesystem-specific errors such as EFTYPE. Large permutation sets add syscall volume. Cleanup must reset permissions before unlinking.

## Test Signals
Expected signals are sustained bogo operations, no unexpected chmod/fchmod errors, successful removal of the shared file, and coverage on systems both with and without native `fchmodat2`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chmod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chown.c -->
# sources/test-tools/stress-ng/stress-chown.c

## Purpose
Implements the `chown` stressor, exercising ownership changes on a shared temporary file through `fchown`, `chown`, and `lchown`.

## Important APIs, Types, and Functions
`stress_chown_info` exposes the stressor. `stress_chown_check()` ignores expected race/platform/permission errors. `do_fchown()` and `do_chown()` try combinations of current uid/gid, `(uid_t)-1`, `(gid_t)-1`, and root ownership probes when the worker lacks chown capability, restoring ownership if an unexpected root change succeeds.

## Control Flow
`stress_chown()` creates or opens a shared temp file, determines current uid/gid and whether effective uid is root, synchronizes, optionally queries `_PC_CHOWN_RESTRICTED`, then loops through fd, path, and lchown variants. It periodically fsyncs and increments bogo operations until stopped. Cleanup closes and removes the file and directory.

## State and Persistence Behavior
Runtime state is one temporary directory and file shared by worker instances plus an fd. It changes file ownership but restores or removes the file during cleanup. No repository state is persisted.

## Dependencies and Integration Points
Uses stress-ng temp file helpers, bad-fd helper, filesystem diagnostics, shim fsync/unlink/rmdir, process state, and bogo accounting. It integrates with normal worker synchronization so multiple instances contend on the same object.

## Risks and Edge Cases
Permissions dominate behavior: unprivileged users should see EPERM for root ownership, while root can perform more changes. Races with other instances can yield ENOENT. The retry loop for nonzero instances can return no-resource if the creator is delayed too long. Ownership changes on some filesystems may be restricted.

## Test Signals
Good signals are bogo progress without unexpected negative return codes, correct handling of EPERM for unprivileged users, and cleanup of the shared temp file. Run as both root and non-root when possible.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chown.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chroot.c -->
# sources/test-tools/stress-ng/stress-chroot.c

## Purpose
Implements the `chroot` stressor, testing valid and invalid `chroot()` behavior and checking for known escape patterns using `chdir("..")` and saved cwd file descriptors.

## Important APIs, Types, and Functions
`stress_chroot_info` registers the stressor with a `CAP_SYS_ADMIN` support check when `chroot()` is available. `chroot_shared_data_t` stores shared metrics, escape flags, root inode, and cwd fd. `do_chroot()` times successful `chroot()` calls and always follows with `chdir("/")`. Nine test functions cover valid chroot, bad pointers, long/nonexistent/file/device paths, huge paths, and two escape checks.

## Control Flow
`stress_chroot()` mmap's shared data, creates a temp chroot directory and a file target, stores a cwd fd, synchronizes, then repeatedly forks a child to run the next test function. The parent waits and fails on nonzero child status, increments bogo count on success, rotates through tests, reports escape methods from shared flags, records a chroot-rate metric, and cleans all temp objects.

## State and Persistence Behavior
Temporary state includes shared mmap metrics, global path buffers, a temp chroot directory, a file used for ENOTDIR checks, and an fd to the original cwd. Each actual `chroot()` happens in a forked child so the parent process remains outside the jail for continued testing and cleanup.

## Dependencies and Integration Points
Uses stress-ng capability checks, mmap helpers, temp file helpers, OOM/scheduling helpers in children, wait handling, metrics, and filesystem wrappers. It is only implemented on platforms with `chroot()`.

## Risks and Edge Cases
Requires high privilege and intentionally explores security-sensitive behavior. Children must chdir after chroot to avoid unsafe cwd semantics. Escape detection is informational but important. Some kernels/filesystems return EPERM/ENOENT instead of ENOTDIR for certain paths. Failure to isolate tests in children would trap the worker inside a chroot.

## Test Signals
Expected signals are skip without CAP_SYS_ADMIN, successful cycling through child tests when privileged, optional informational escape reports, nonzero "chroot calls per sec", and cleanup of temp directory/file.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chroot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chyperbolic.c -->
# sources/test-tools/stress-ng/stress-chyperbolic.c

## Purpose
Implements the `chyperbolic` compute stressor, repeatedly evaluating complex hyperbolic functions and verifying accumulated checksums for double, float, and long double variants.

## Important APIs, Types, and Functions
`stress_chyperbolic_info` registers the stressor, `chyperbolic-method`, and up to nine metrics. `stress_chyperbolic_method_t` maps names to function callbacks. Generated methods cover available `ccosh`, `ccoshf`, `ccoshl`, `csinh`, `csinhf`, `csinhl`, `ctanh`, `ctanhf`, and `ctanhl`. `stress_chyperbolic_exercise()` times each selected function and reports checksum failures.

## Control Flow
The stressor reads the selected method index, zeros method metrics, synchronizes, and repeatedly invokes either the selected method or `all`. Each function loops `STRESS_CHYPERBOLIC_LOOPS` times over a deterministic complex progression, accumulates a sum, increments bogo operations, and returns whether the sum exceeds its precision tolerance. On exit, per-method operation rates are emitted.

## State and Persistence Behavior
State is purely in-process: static metrics, deterministic loop constants, and current method selection. No files, shared memory, or kernel state are modified.

## Dependencies and Integration Points
Depends on `<complex.h>`, math functions and shim wrappers, stress-ng target-clone optimization macros, metrics, settings, sync, and method option parsing. If complex support is absent, it registers an unimplemented stressor.

## Risks and Edge Cases
Floating-point results vary with library, architecture, precision, and optimization, so tolerances differ by type. Long double precision is adjusted based on storage size. Compiler or libm bugs surface as checksum failures. The `all` method aggregates failures but only emits named failure details for nonzero indexes.

## Test Signals
Good signals are no checksum failure logs, nonzero per-method ops/sec metrics for compiled methods, and successful method selection for `all` and each individual complex hyperbolic function available on the platform.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-chyperbolic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clock.c -->
# sources/test-tools/stress-ng/stress-clock.c

## Purpose
Implements the `clock` stressor, broadly exercising POSIX clock, timer, nanosleep, adjtime, and Linux PTP clock-id paths, including expected invalid argument and permission failures.

## Important APIs, Types, and Functions
`stress_clock_info` registers the stressor when librt and clock APIs are available. `stress_clock_info_t` maps clock ids to names. Tables list clocks for `clock_gettime`/`clock_getres`, `clock_nanosleep`, and `timer_create`. Helpers include `stress_clock_name()`, `check_invalid_clock_id()`, `aux_clock_nonfatal_error()`, and `FD_TO_CLOCKID()`.

## Control Flow
`stress_clock()` seeds the random generator deterministically, synchronizes, then loops through thread CPU clock reads/set probes, invalid clock ids, getres/gettime for each known clock, invalid and permission-sensitive `clock_settime`, periodic invalid `clock_nanosleep`, `clock_adjtime` probes, POSIX timer create/set/get/delete cycles, and optional `/dev/ptp0` file-clock reads. Verification mode reports unexpected errors while known unsupported or permission-denied cases are tolerated.

## State and Persistence Behavior
No persistent state is written. The stressor creates short-lived POSIX timers and opens `/dev/ptp0` if present. It avoids repeatedly setting invalid time after one successful invalid-timespec probe to limit time drift risk.

## Dependencies and Integration Points
Uses stress-ng clock shims, capability checks, deterministic random utilities, optional poll/timex headers, POSIX timers, Linux file-descriptor clock ids, process-state reporting, and bogo accounting. It is `VERIFY_OPTIONAL` because platform clock behavior varies.

## Risks and Edge Cases
Clock availability varies by kernel and libc. Some clocks reject settime by design; unprivileged users should receive EPERM or EINVAL. Auxiliary clocks may be disabled. Timer creation can fail due to limits. Interacting with realtime clock APIs as root could affect system time if invalid-guard logic is wrong.

## Test Signals
Expected signals are sustained bogo operations, no unexpected verification failures, successful handling of unavailable clocks, and timer resources deleted each loop. Tests should include verify and non-verify modes and a system without `/dev/ptp0`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clone.c -->
# sources/test-tools/stress-ng/stress-clone.c

## Purpose
Implements the `clone` stressor, rapidly creating and reaping clone/clone3 children with many flag combinations while measuring clone latency and exercising namespace, unshare, and LDT-related paths.

## Important APIs, Types, and Functions
`stress_clone_info` registers the stressor with `clone-max`. `stress_clone_shared_t` holds shared metrics and racy booleans proving child invocation and wait success. `stress_clone_t` stores a PID and stack per tracked clone. `stress_clone_new()`, `stress_clone_head_remove()`, and `stress_clone_free()` manage active/free lists. `clone_func()` is the child callback; `stress_clone_child()` performs clone/clone3 loops; `stress_clone()` wraps the work in `stress_oomable_child()`.

## Control Flow
The top-level stressor maps shared state, creates a metrics lock, computes flag permutations, lowers OOM preference for the parent, synchronizes, then runs the clone workload in an OOM-able child. The workload allocates a large mapping, creates clones until `clone-max` or low memory, chooses either table flags or permutations, tries clone3 when available, falls back to clone, reaps head entries on failure or pressure, and drains all children on exit.

## State and Persistence Behavior
State includes shared metrics mmap, a process-local active/free clone list with mmaped descriptors and embedded stacks, optional flag permutation memory, and child processes. No files persist. Cleanup reaps clone children, frees descriptor mappings, frees permutations, destroys process memory by exit, and unmaps shared state.

## Dependencies and Integration Points
Uses Linux/Unix clone APIs and shim clone3, stress-ng locks, mincore/mmap/OOM helpers, flag permutation, memory-low checks, unshare/setns/modify_ldt shims, waitpid with `__WCLONE`, process state, and metrics. It integrates with stress-ng OOMable child handling using `STRESS_OOMABLE_DROP_CAP`.

## Risks and Edge Cases
Clone flag combinations can fail with EPERM/EINVAL by design. Avoiding `CLONE_VM` prevents parent memory corruption. clone3 may be absent and is disabled after ENOSYS. Low-memory behavior must reap promptly. Racy shared booleans are used only as sanity evidence. Some clone flags alter wait semantics, so `__WCLONE` handling is important.

## Test Signals
Good signals include nonzero bogo progress, "microsecs per clone" metric, no failure that children terminated before invocation, clean reaping under low `--clone-max`, and graceful behavior when clone3 or namespace flags are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-clone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-close.c -->
# sources/test-tools/stress-ng/stress-close.c

## Purpose
Implements the `close` stressor, creating races between the main worker and helper pthreads that duplicate, close, range-close, and otherwise manipulate many file descriptors.

## Important APIs, Types, and Functions
`stress_close_info` registers the stressor with `close-fds`. Global volatile `fd`, `dupfd`, and `max_delay_us` coordinate intentionally racy close targets. `stress_close_func()` is the helper thread that dup2s stderr into high fd slots, closes shared fds, tests advisory locks, random bad closes, and `close_range`. `stress_close()` creates helper threads and cycles through many fd-producing APIs.

## Control Flow
The main function starts three pthreads, creates a temp file for `faccessat` invalid-dirfd checks, synchronizes, then repeatedly opens a random fd source: sockets, `/dev/zero`, tmpfile, epoll, eventfd, fanotify, inotify, pipe, signalfd, userfaultfd, O_PATH, directory, shm, bad fd, proc fd, or stdin. It duplicates, probes ownership/access/stat paths, closes the fd while helpers race, verifies a second close fails with EBADF or EINTR, updates timing, and adjusts helper delay.

## State and Persistence Behavior
State is in-process and temporary: pthreads, shared volatile fd variables, optional POSIX shm name, a temporary file directory, and many short-lived file descriptors. Cleanup joins threads, closes temp fd, and removes the temp directory. No persistent files should remain.

## Dependencies and Integration Points
Depends on pthreads, stress-ng pthread wrappers, capability checks, bad-fd helpers, close_range shim, many optional Linux fd APIs, sockets, temp filesystem helpers, metrics, and signal mask handling. It registers an unimplemented stressor without pthread support.

## Risks and Edge Cases
The stressor intentionally races close operations, so fd reuse can make failures timing-sensitive. Some fd source APIs require kernel support or privileges and may fail. `close_range` flags vary. The second-close verification must tolerate EINTR. Threads block signals so the controlling thread handles termination.

## Test Signals
Expected signals include no "unexpectedly able to close the same file twice" failures, nonzero close-rate metric, clean pthread joins, and cleanup of temp files. Exercise low and high `--close-fds` values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-close.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-context.c -->
# sources/test-tools/stress-ng/stress-context.c

## Purpose
Implements the `context` stressor, using `getcontext`, `makecontext`, and `swapcontext` to bounce between three user-space contexts and measure context-switch rate.

## Important APIs, Types, and Functions
`stress_context_info` registers the stressor when `ucontext.h` and `swapcontext` are available. `chk_ucontext_t` wraps a `ucontext_t` with canary words. `context_data_t` stores each context, stack mapping, and expected canaries. `stress_context_init()` creates each context and stack. `stress_thread1/2/3()` form a circular swap chain and return to `uctx_main` when stopped.

## Control Flow
`stress_context()` allocates three context records, initializes stacks and canaries, sets `stress_max_ops` from requested bogo max, synchronizes, catches SIGSEGV, starts the chain with `swapcontext(&uctx_main, &context[0])`, then computes bogo operations from `context_counter`. After return, it verifies all canaries, records swapcontext calls per second, unmaps stacks and context data, and returns status.

## State and Persistence Behavior
State is process-local static/global: `uctx_main`, `context`, `context_counter`, and `stress_max_ops`. Stack and context storage are anonymous mmap allocations named for diagnostics. No files or persistent kernel objects are created.

## Dependencies and Integration Points
Depends on ucontext APIs, stress-ng mmap helpers, memory naming, signal handling, random canary generation, process state, metrics, and bogo accounting. It integrates with stress-ng's max-ops limit by scaling context switches to bogo units.

## Risks and Edge Cases
`ucontext` is deprecated or absent on some platforms. Stack size must be sufficient for the context functions. Canary checks detect memory clobbering around `ucontext_t`, but not arbitrary stack corruption. If `swapcontext` fails or a context never returns, cleanup and metrics are affected.

## Test Signals
Good signals are nonzero "swapcontext calls per sec", no canary-clobber failures, correct unimplemented behavior without ucontext support, and stable termination at both time-based and max-ops limits.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-context.c -->
