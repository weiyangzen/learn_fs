# subset-b-009372

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-iomix.c -->
# sources/test-tools/stress-ng/stress-iomix.c

Purpose: implements the `iomix` stressor, a mixed filesystem I/O workload that creates one temporary backing file per worker instance, preallocates it, unlinks it, then forks one child per available I/O behavior to hammer the same open file descriptor with reads, writes, mmap writes, syncs, inode-flag ioctls, cache operations, copy helpers, sendfile, cachestat, and readahead where supported.

Important APIs/types/functions: `stress_iomix_func` defines child workload functions; `stress_iomix_rnd_offset()` selects random file offsets; `stress_iomix_fsync_min_1Hz()` throttles `fsync`, `fdatasync`, and `sync`; `iomix_funcs[]` is the fan-out table. File APIs include `open`, `fallocate`, `lseek`, `read`, `write`, `mmap`, `msync`, `posix_fadvise`, `sync_file_range`, `copy_file_range`, `sendfile`, `readahead`, `ioctl(FS_IOC_*FLAGS)`, and the Linux `cachestat` syscall wrapper when available.

Control flow: `stress_iomix()` installs a SIGCHLD handler, mmaps shared child PID records, creates a shared bogo counter lock, resolves `iomix-bytes`, creates a temp directory and unlinked temp file, shrinks allocation on `EFBIG` or `ENOSPC`, then forks up to `SIZEOF_ARRAY(iomix_funcs)` children. Each child waits on stress-ng sync start, applies scheduler settings, runs its assigned I/O loop, and exits. The parent waits in `pause()` while the shared bogo counter remains below the stop condition, then kills and reaps children and removes resources.

State and persistence behavior: persistent filesystem state is intentionally temporary and unlinked; the live file survives only by descriptor reference. Runtime state is the shared fd offset, child PIDs in shared mmap, and the global `counter_lock`. Some child functions mutate file contents, inode flags, cache state, and file-cache hints; all should be discarded when the fd and temp directory are cleaned.

Dependencies and integration points: depends heavily on stress-ng filesystem, mmap, sync, signal, lock, random, and kill helpers. Compile-time feature gates tailor the workload to libc, kernel, and filesystem support. Registered as `CLASS_FILESYSTEM | CLASS_OS`, with `iomix-bytes` option and always-on verification.

Risks: children share a single file descriptor, so file offset races are part of the stress model. Filesystems may reject inode flags or preallocation; the code handles space exhaustion but treats many unexpected syscall failures as stressor failures. The mmap path uses `MAP_SHARED | MAP_ANONYMOUS` with a file descriptor, which is platform-sensitive. Cache dropping can block without sufficient privileges.

Test signals: run with multiple workers and `--verify`, vary `--iomix-bytes`, and cover low-space filesystems. Useful pass signals are no stale temp directories, all child PIDs reaped, no unexpected read/write/lseek/fallocate errors, bogo progress from multiple child workloads, and stable behavior on kernels with and without optional syscalls.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-iomix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ioport.c -->
# sources/test-tools/stress-ng/stress-ioport.c

Purpose: implements the x86 `ioport` stressor, exercising raw I/O port permissions and `inb`/`outb` transactions against selectable legacy ports such as POST `0x80`, VGA DAC red, and Bochs debug.

Important APIs/types/functions: `stress_ioport_opts_t` maps `in`, `out`, and `inout`; `stress_ioport_port_t` maps user-facing port names. `stress_ioport_supported()` probes `ioperm()`. `stress_ioport_ioperm()` verifies invalid `ioperm()` calls fail. The main loop uses `ioperm`, `inb`, `outb`, optional `/dev/port` `lseek`/`read`/`write`, and deprecated `iopl()` probes.

Control flow: the stressor reads option indexes, enables access to the selected port, optionally opens `/dev/port`, snapshots an initial byte, then sync-starts. Each iteration performs 32 reads and/or 32 writes depending on flags, pokes the same port through `/dev/port` when available, exercises invalid permission requests and `iopl` levels, increments bogo ops, and finally records nanoseconds per `inb` and `outb`.

State and persistence behavior: process I/O permission bits are enabled for one port and disabled on teardown. `/dev/port` writes can affect real hardware or emulated devices; the code restores only the sampled byte when using `/dev/port` and does not maintain persistent repo state.

Dependencies and integration points: gated to x86 builds with `sys/io.h` and I/O port support. Needs `CAP_SYS_RAWIO` or equivalent privilege. Registered as `CLASS_CPU` with always-on verification and option tables for stress-ng command parsing.

Risks: running on real hardware can have side effects because port I/O is not abstract. Permission failures are common and reported as skips in the support probe, but failures after option selection return stressor failure. Invalid `ioperm` tests assume failures; a permissive or unusual kernel could trip verification.

Test signals: verify skip behavior without raw I/O privilege, successful metrics with a safe VM port such as Bochs debug, and cleanup of `ioperm` permissions. Confirm invalid `ioperm` arguments do not unexpectedly succeed.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ioport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ioprio.c -->
# sources/test-tools/stress-ng/stress-ioprio.c

Purpose: implements `ioprio`, a Linux I/O-priority stressor that rapidly queries and changes process I/O priority classes while issuing vectored writes and syncs to a temporary file.

Important APIs/types/functions: the file relies on `core-io-priority.h` wrappers `shim_ioprio_get()` and `shim_ioprio_set()`, Linux `IOPRIO_WHO_*` selectors, `IOPRIO_PRIO_VALUE()`, and `pwritev()`. Constants set a small four-iovec write size and bounded temp-file footprint.

Control flow: `stress_ioprio()` creates an unlinked temp file, reports expected disk usage, sync-starts, then loops through process, process-group, and user `ioprio_get` calls. It exercises invalid selectors and IDs, fills four small buffers, writes randomly within a fixed range, fsyncs, attempts invalid `ioprio_set` calls, then applies idle, best-effort priorities 0-7, and realtime priorities 0-7 around more writes and fsyncs.

State and persistence behavior: file data is temporary and unlinked; the main side effect is repeated mutation of the current process I/O priority. The priority is not explicitly restored, so process teardown is relied on for cleanup.

Dependencies and integration points: compiled only when `ioprio_get`, `ioprio_set`, and `pwritev` are available. Uses stress-ng temp directory, settings, sync, random, and filesystem usage helpers. Registered as `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: realtime I/O priority may require privilege; the code tolerates `EPERM` and `EINVAL` but treats other errors as failures. Filesystems can return `ENOSPC` on `pwritev`, which is accepted. Behavior varies by scheduler and kernel configuration.

Test signals: run with and without privilege, verify no unexpected ioprio errors, temp directory cleanup, and bogo progress under `--verify`. Check that `ENOSPC`, `EPERM`, and unsupported priority classes are handled as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ioprio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ipsec-mb.c -->
# sources/test-tools/stress-ng/stress-ipsec-mb.c

Purpose: implements `ipsec-mb`, a compute stressor for Intel IPSec MB library job submission across CPU feature backends and crypto/integrity methods.

Important APIs/types/functions: compatibility macros normalize old and new IPSec MB names. `stress_ipsec_features_t` stores required feature bits, init function, support status, and metrics. Method functions cover SHA-512, AES-CBC named `des`, AES-CMAC, AES-CTR, HMAC-MD5, HMAC-SHA1, and HMAC-SHA512. Core helpers include `stress_job_get_next()`, `stress_job_check_status()`, `stress_jobs_done()`, and `stress_ipsec_call_func()`.

Control flow: support checks require x86-64, library headers, library linkage, and feature macros. `stress_ipsec_mb()` validates library version, allocates an `IMB_MGR`, detects CPU features, optionally narrows to one `--ipsec-mb-feature`, fills an aligned 8192-byte data block, then sync-starts. Each loop initializes each supported backend and invokes the selected method or `all`. Method functions allocate aligned outputs, populate job fields, submit jobs, flush completions, count successful jobs as bogo ops, and free buffers. Metrics are emitted per backend.

State and persistence behavior: all data is in process memory: manager state, random keys/IVs, output buffers, and per-feature stats. There is no filesystem persistence.

Dependencies and integration points: tied to Intel IPSec MB API, CPU feature detection, stress-ng settings and metrics, and target architecture gates. Registered as `CLASS_CPU | CLASS_INTEGER | CLASS_COMPUTE`.

Risks: library ABI/version differences are handled partly by macros but remain a compatibility risk. Some method names are historical or imprecise. The HMAC-SHA1 setup uses MD5 one-block helpers for ipad/opad hashes, which should be treated as intentional library stress rather than a correctness reference. Large `--ipsec-mb-jobs` values can allocate substantial memory.

Test signals: cover unsupported-library skip, feature filtering, `--ipsec-mb-method all`, large and minimal job counts, and metrics for each supported backend. Failure signals are incomplete job counts, non-completed job status, allocation failures, or crashes under specific CPU feature initializers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-ipsec-mb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-itimer.c -->
# sources/test-tools/stress-ng/stress-itimer.c

Purpose: implements `itimer`, an interval-timer stressor that drives high-frequency `SIGPROF` delivery via `setitimer()` and continuously samples all available interval timer types.

Important APIs/types/functions: global `s_args`, `rate_us`, and `time_end` are shared with the signal handler. `stress_itimer_set()` computes nonzero interval values, with optional random frequency jitter. `stress_itimer_handler()` increments bogo ops, checks timeout periodically, and cancels the profiling timer when stopping.

Control flow: the worker blocks `SIGINT`, selects `itimer-freq` with maximize/minimize overrides, installs a `SIGPROF` handler, sync-starts, programs `ITIMER_PROF`, and loops over `getitimer()` for all compiled `ITIMER_REAL`, `ITIMER_VIRTUAL`, and `ITIMER_PROF` entries until the stress framework stops. It reports failure if no SIGPROF signals were handled, then cancels the timer.

State and persistence behavior: state is process-local signal/timer state plus global counters. No filesystem persistence exists. The timer is explicitly disabled at shutdown and in the handler cancellation path.

Dependencies and integration points: requires `getitimer()` and `setitimer()`. Uses stress-ng settings, signal helpers, timing, bogo accounting, and process state transitions. Registered as `CLASS_INTERRUPT | CLASS_OS` with always-on verification.

Risks: very high requested frequencies are limited by kernel timer resolution and scheduling. Signal-handler work must remain async-signal safe enough for stress-ng expectations. Only `ITIMER_PROF` is actively programmed even though all available timers are queried.

Test signals: run default, minimized, maximized, and `--itimer-rand`; confirm bogo ops increase, timers are cancelled, and unsupported `ITIMER_PROF` returns `EXIT_NOT_IMPLEMENTED` rather than failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-itimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-jpeg.c -->
# sources/test-tools/stress-ng/stress-jpeg.c

Purpose: implements `jpeg`, a libjpeg compression stressor that generates synthetic RGB images and repeatedly compresses them to memory or `/dev/null`, measuring pixel throughput and compression ratio.

Important APIs/types/functions: image generators include `stress_rgb_plasma()`, `stress_rgb_noise()`, `stress_rgb_brown()`, `stress_rgb_gradient()`, `stress_rgb_xstripes()`, and `stress_rgb_flat()`. `stress_rgb_compress_to_jpeg()` wraps libjpeg setup, scanline submission, optional checksum calculation, and duration measurement. Options control width, height, quality, and image type.

Control flow: `stress_jpeg()` resolves dimensions and quality with maximize/minimize support, mmaps RGB and row-pointer buffers, seeds deterministic random state, generates the selected image once, reports memory usage, sync-starts, and loops compressing the same image. With `--verify`, it performs a second compression and checksum pass each iteration, though the checksums are only computed rather than compared in this file. Metrics are reported after the loop and buffers are unmapped.

State and persistence behavior: all image data and row pointers are anonymous memory. When `open_memstream()` exists, compressed bytes are held in a temporary malloc-backed stream and freed; otherwise output is `/dev/null`.

Dependencies and integration points: compile-gated on libjpeg headers and library. Uses stress-ng mmap, memory naming, metrics, deterministic PRNG, and optional verification flag. Registered as `CLASS_CPU | CLASS_COMPUTE`, verification optional.

Risks: maximum 4096x4096 RGB buffers can consume significant memory per worker. `open_memstream()` availability changes whether compressed size is meaningful. Libjpeg error handling uses the default error manager; fatal libjpeg errors may longjmp/exit depending on library behavior.

Test signals: verify each image type, min/max size and quality, optional verification mode, nonzero megapixels/sec metric, reasonable compression-ratio metric, and clean unmap/free behavior on allocation failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-jpeg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-judy.c -->
# sources/test-tools/stress-ng/stress-judy.c

Purpose: implements `judy`, a Judy array stressor that allocates sparse integer-indexed entries, searches them, deletes them, and records operation rates.

Important APIs/types/functions: `gen_index()` maps dense loop indexes to sparse `Word_t` keys. The Judy macros `JLI`, `JLG`, and `JLD` perform insert, lookup, and delete. Duration/count arrays track insert, find, and delete metrics.

Control flow: `stress_judy()` resolves `judy-size`, sync-starts, then for each iteration creates a fresh JudyL array. It inserts `n` generated indexes with stored values, scans all indexes to find entries and optionally verify stored values, deletes in reverse order, increments bogo ops, and repeats until stopped. On allocation failure it attempts to delete inserted nodes before aborting.

State and persistence behavior: state is contained in the in-memory Judy array and metrics counters. Each loop creates and destroys the array; no filesystem state exists.

Dependencies and integration points: compile-gated on `Judy.h` and libJudy. Uses stress-ng settings, random-free deterministic indexing, metrics, memory pressure messages, and optional verification flag. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY`.

Risks: large `judy-size` values stress allocator and may leave partially built arrays if an unexpected macro error path occurs. Verification is optional; without it the stressor mainly exercises library paths and reports rates.

Test signals: run default, min, max, and `--verify`; check insert/find/delete metrics, no Judy allocation errors, and correct `EXIT_NO_RESOURCE` or skip behavior when the library is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-judy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kcmp.c -->
# sources/test-tools/stress-ng/stress-kcmp.c

Purpose: implements `kcmp`, a Linux syscall stressor comparing kernel resources between parent and child processes, including files, VM, file tables, fs context, signal handlers, I/O context, SysV semaphores, and optionally epoll target descriptors.

Important APIs/types/functions: local `SHIM_KCMP_*` enum values mirror `linux/kcmp.h`. `SHIM_KCMP()` wraps `shim_kcmp()`. `KCMP` and `KCMP_VERIFY` macros centralize tolerated errors and verification expectations. Optional epoll setup uses `struct shim_kcmp_epoll_slot`.

Control flow: the stressor opens `/dev/null`, optionally reserves a TCP port and creates an epoll-watched socket, sync-starts, forks a child that waits in `pause()`, and the parent opens a second fd. The loop runs many `kcmp` comparisons across parent/child combinations, optional verification checks same-process comparisons return zero, then issues invalid type, fd, and pid calls. On stop it kills the child and closes resources.

State and persistence behavior: state is process and descriptor state only: `/dev/null` fds, optional socket and epoll fd, a child process, and reserved port bookkeeping. No persistent filesystem data is written.

Dependencies and integration points: requires the `kcmp` syscall; optional epoll path depends on epoll headers and glibc support. It uses stress-ng capability checks, networking helpers, bad-fd generation, fork retry, and kill helpers. Registered as `CLASS_OS`, verification optional.

Risks: `kcmp` often needs `CAP_SYS_PTRACE`; `EPERM` is treated as capability failure and aborts the loop. Namespace, Yama, and LSM policy can alter access. Epoll setup uses a fixed starting port via the stress-ng reservation helper.

Test signals: run as unprivileged and privileged users, with `--verify`, and on kernels with and without epoll target support. Confirm accepted errors are limited to expected `EINVAL`, `ENOSYS`, `EBADF`, and capability failure.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kcmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-key.c -->
# sources/test-tools/stress-ng/stress-key.c

Purpose: implements `key`, a Linux keyring stressor that creates, searches, reads, updates, links, unlinks, revokes, invalidates, and clears user keys in the process keyring.

Important APIs/types/functions: syscall wrappers `shim_add_key()`, `shim_keyctl()`, and optional `shim_request_key()` exercise keyutils operations. Constants bound each batch to 256 keys, short timeouts, and a large invalid description buffer. The main function tracks `keys_added` for metrics.

Control flow: after allocating a huge random description string, the worker sync-starts and repeatedly fills a key array. For each key index it tries several invalid `add_key()` variants, creates a valid `user` key, optionally sets timeout and searches. It then iterates created keys to describe, update, read, request, get security, chown, query capabilities, set permissions, link/unlink, revoke, and invalidate. It discards `/proc/keys` and `/proc/key-users` caches, issues an invalid `keyctl` command, increments bogo ops, invalidates leftovers, and clears the process keyring.

State and persistence behavior: keys are kernel keyring objects scoped to the process keyring and explicitly invalidated/cleared. The huge description is heap memory. No repository state persists.

Dependencies and integration points: gated on keyutils headers plus `add_key`, `keyctl`, and syscall support; `request_key` is optional. Uses stress-ng random strings, filesystem discard, settings, metrics, and process state. Registered as `CLASS_OS` with always-on verification.

Risks: permissions, key quotas, disabled keyrings, and LSM policy can cause `EPERM`, `EDQUOT`, `ENOMEM`, `EKEYEXPIRED`, or `ENOKEY`. The stressor treats permission or unimplemented syscalls as non-implemented skips but reports unexpected keyctl errors.

Test signals: validate skip on systems without key permissions, successful cleanup of process keyring, meaningful keys-per-second metric, and no quota leakage after forced stop.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-key.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kill.c -->
# sources/test-tools/stress-ng/stress-kill.c

Purpose: implements `kill`, a signal-delivery stressor that repeatedly calls `kill()` with real, zero, broadcast-like, invalid-signal, and invalid-pid combinations.

Important APIs/types/functions: `stress_kill()` installs a `SIGUSR1` ignore handler, forks an optional child, uses `kill()` for all probes, and records a harmonic mean metric for successful measured calls.

Control flow: the parent installs signal handling, forks a child that ignores `SIGUSR1` and waits until the parent disappears or stress stops, then sync-starts. The loop gradually reduces an initial sleep delay to avoid startup starvation, measures `kill(args->pid, SIGUSR1)`, `kill(args->pid, 0)`, and `kill(-1, 0)`, exercises illegal signals and pid values, signals the child with zero, stop/continue, and `SIGUSR1`, probes a racy unused pid, and increments bogo ops. Teardown sends `SIGKILL` to the child and waits.

State and persistence behavior: state is limited to parent/child process signal state and metrics. No filesystem persistence exists.

Dependencies and integration points: uses stress-ng signal helpers, process state tracking, unused pid helper, timing, and metrics. Registered as `CLASS_INTERRUPT | CLASS_SCHEDULER | CLASS_OS`, verification optional.

Risks: `kill(-1, 0)` behavior depends on permissions and process table state; verification can report failures on hardened or containerized systems. The child fork is intentionally not critical, so missing child coverage is possible under fork pressure.

Test signals: run with `--verify` under normal and containerized permissions, confirm no unexpected measured `kill` failures, child is reaped, and invalid calls do not affect process survival.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kill.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-klog.c -->
# sources/test-tools/stress-ng/stress-klog.c

Purpose: implements `klog`, a Linux kernel syslog interface stressor that reads kernel log buffers and exercises valid and invalid `klogctl` actions.

Important APIs/types/functions: action constants mirror Linux syslog commands. `stress_klog_supported()` probes `SYSLOG_ACTION_SIZE_BUFFER`. `stress_klog()` uses `shim_klogctl()` for buffer-size, read, open/close, unread-size, clear, console toggles, console level, and invalid command tests.

Control flow: support probing requires access to the kernel log. The worker determines buffer size, skips zero-sized logs, caps allocation at 4 MiB, sync-starts, then loops with a random read length. Each iteration tests invalid sizes and buffers, performs `READ_ALL`, validates it does not return more than requested, runs no-op open/close and size queries, optionally forces privileged actions to fail when lacking syslog/admin capability, tests invalid console levels and command type, and increments bogo ops.

State and persistence behavior: only a heap buffer is retained. Privileged clear/read-clear and console actions are only attempted when not capable, so normal runs avoid mutating kernel log state except for reads and no-op commands.

Dependencies and integration points: requires the `syslog` syscall or stress-ng klog shim and capability checks. Registered as `CLASS_OS`, always verified, with a support probe.

Risks: access to klog is commonly restricted by `dmesg_restrict`, capabilities, containers, or lockdown. Kernel logs can be large or concurrently changing, so return sizes are inherently racy.

Test signals: verify skip messaging without `CAP_SYSLOG`/`CAP_SYS_ADMIN`, successful bounded allocation, no over-read result, and accepted behavior across restricted and privileged systems.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-klog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kvm.c -->
# sources/test-tools/stress-ng/stress-kvm.c

Purpose: implements `kvm`, a `/dev/kvm` stressor that repeatedly creates a tiny VM, maps guest memory, creates one vCPU, runs a minimal architecture-specific guest loop, handles exits, and destroys all resources.

Important APIs/types/functions: `stress_kvm_open()` handles `/dev/kvm` access and skip reporting; `stress_kvm_supported()` probes availability. `kvm_kernel[]` contains tiny guest code for x86, ARM64, or RISC-V. Main KVM APIs include `KVM_CREATE_VM`, `KVM_SET_USER_MEMORY_REGION`, `KVM_CREATE_VCPU`, register setup ioctls, `KVM_GET_VCPU_MMAP_SIZE`, vCPU `mmap`, and `KVM_RUN`.

Control flow: after sync-start, each iteration opens `/dev/kvm`, optionally logs API version, creates a VM, mmaps one page of guest memory, registers it at the architecture physical base, optionally maps readonly MMIO memory for ARM/RISC-V, creates vCPU, copies guest code, initializes registers, maps `struct kvm_run`, and runs up to 1000 exits. x86 handles port I/O exits until a byte reaches `0xff`; ARM/RISC-V count MMIO exits. Success increments bogo ops before teardown.

State and persistence behavior: state is transient kernel VM/vCPU objects, anonymous memory mappings, fds, and guest register state. All are closed/unmapped each iteration.

Dependencies and integration points: gated to Linux with `linux/kvm.h` and supported architecture macros. Uses stress-ng capability checks, mmap, madvise, arch helpers, and process state. Registered as `CLASS_DEV | CLASS_OS`.

Risks: `/dev/kvm` availability, permissions, nested virtualization, architecture register ABI, and KVM API support vary widely. Error paths must close multiple partially initialized fds and mappings. ARM/RISC-V MMIO unmap uses page-size-sensitive cleanup and should be checked carefully.

Test signals: run in a VM host with KVM access, confirm skip without `/dev/kvm`, bogo increments only on successful guest exits, no fd/mmap leaks over repeated iterations, and no unexpected ioctl failures under `--verify`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-kvm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-l1cache.c -->
# sources/test-tools/stress-ng/stress-l1cache.c

Purpose: implements `l1cache`, a CPU L1 data-cache thrashing stressor that computes or discovers cache geometry, allocates an aligned buffer, and repeatedly reads/writes addresses chosen to evict L1 sets.

Important APIs/types/functions: `stress_l1cache_info_ok()` fills missing cache parameters from user options or Linux cache discovery. `stress_l1cache_info_check()` validates `size == ways * sets * line_size`. Method functions implement forward, reverse, and random access patterns, each with verification variants. `stress_l1cache_methods[]` maps option names to functions.

Control flow: the stressor reads `--l1cache-*` settings, selects a method and verification function, validates geometry, mmaps four times the cache size, optionally `mlock`s it, aligns a pointer by set size, reports memory, sync-starts, and loops invoking the method. Each method runs many read/write passes across twice the cache size and updates a static set index; verification variants read back expected byte values. The main loop adds `l1cache_sets` bogo ops per pass and unmaps on exit.

State and persistence behavior: only anonymous memory and static per-method set counters persist during the process. No filesystem state is written.

Dependencies and integration points: uses stress-ng CPU-cache discovery, mmap, madvise, memory usage, settings, and metrics helpers. Registered as `CLASS_CPU_CACHE`, verification optional.

Risks: incorrect cache geometry can cause ineffective stress or out-of-range alignment. Reverse loops use pointer comparisons that depend on careful unsigned address behavior. Verification may fail if the access pattern writes overlapping random locations in ways not expected by the deterministic seed reset.

Test signals: run with auto-detected geometry and explicit size/sets/ways/line-size combinations, all three methods, `--verify`, and `--l1cache-mlock`. Confirm invalid geometry fails cleanly and memory is unmapped.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-l1cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-landlock.c -->
# sources/test-tools/stress-ng/stress-landlock.c

Purpose: implements `landlock`, a Linux Landlock LSM stressor that creates rulesets, adds path-beneath rules with many access masks, restricts child processes, and recursively consumes Landlock resources.

Important APIs/types/functions: shim access macros provide fallback bit definitions for newer Landlock flags. `stress_landlock_ctxt_t` carries mask, active flag, filename, and base path. Syscall wrappers cover `landlock_create_ruleset`, `landlock_add_rule`, and `landlock_restrict_self`. `stress_landlock_get_access_mask()` discovers usable access bits.

Control flow: support probing creates a minimal ruleset. The main stressor builds a temp filename, discovers usable mask, forks a background child that recursively scans `/` and adds read-file rules where possible, sync-starts, then loops over cumulative and single access flag combinations. Each test forks an isolated child, creates a file, creates a ruleset, opens the temp path with `O_PATH`, adds a path-beneath rule, sets `PR_SET_NO_NEW_PRIVS`, restricts itself, and probes read/write opens before exiting.

State and persistence behavior: restriction state is confined to forked children because Landlock is irreversible for a task. Temporary files are unlinked after each child. Background traversal allocates and closes rulesets without applying them to the parent.

Dependencies and integration points: requires Linux Landlock headers, rule types, and syscalls plus `prctl`. Uses stress-ng fork retry, temp path, dirent, kill, and process state helpers. Registered as `CLASS_OS`.

Risks: Landlock support depends on kernel version and `lsm=landlock`. Recursive scanning of `/` can be expensive and permission noisy. Newer access bits are masked to `0xffff`, so future Landlock bits may not be covered.

Test signals: confirm skip when Landlock is unavailable, successful runs on enabled kernels, no leftover temp files, bounded failure count, and cleanup of the background ruleset-consuming child.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-landlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lease.c -->
# sources/test-tools/stress-ng/stress-lease.c

Purpose: implements `lease`, a filesystem lease stressor that alternates read and write leases while child breaker processes attempt nonblocking opens to trigger lease-break notifications.

Important APIs/types/functions: `lease_sigio` counts `SIGIO` signals. `stress_lease_handler()` increments it. `stress_lease_spawn()` creates breaker children. `stress_try_lease()` opens the file, loops until `F_SETLEASE` succeeds, reads current lease with `F_GETLEASE`, increments bogo ops, then unlocks with `F_UNLCK`.

Control flow: `stress_lease()` resolves `lease-breakers`, installs the SIGIO handler, creates a temp file, spawns breaker children, sync-starts, and loops through write-lease and read-lease attempts. Breaker children repeatedly open the same file with `O_NONBLOCK | O_WRONLY`, tolerating `EWOULDBLOCK` and `EACCES`, then query the lease and close. Teardown kills all breakers, unlinks the file, removes the temp directory, and records SIGIO interrupts per second.

State and persistence behavior: temporary file and directory are removed at exit. Runtime state includes active kernel leases, child processes, signal count, and open fds.

Dependencies and integration points: compile-gated on `F_SETLEASE`, `F_WRLCK`, and `F_UNLCK`. Uses stress-ng temp files, process state, fork retry, scheduler settings, kill helpers, and metrics. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: lease semantics are Linux/filesystem-specific and may require permission or local filesystem support. Unlock loops can spin on `EAGAIN`. Signal delivery is asynchronous, and `lease_sigio` is a plain `uint64_t` updated from a handler.

Test signals: vary breaker counts, run on filesystems with and without lease support, ensure breaker children are reaped, temp files removed, bogo ops advance, and SIGIO metric is plausible.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-lease.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-led.c -->
# sources/test-tools/stress-ng/stress-led.c

Purpose: implements `led`, a Linux sysfs LED stressor that enumerates `/sys/class/leds`, cycles trigger settings, sweeps brightness values, and restores original LED state.

Important APIs/types/functions: `stress_led_info_t` stores path, device name, original trigger, trigger list, original brightness, max brightness, and linked-list pointer. `stress_led_info_get()` discovers LED entries and captures state. `stress_led_exercise()` tokenizes trigger options and writes trigger/brightness files. `stress_led_info_free()` restores and frees the list.

Control flow: the worker reports lack of root privilege as informational, sync-starts, builds a randomized list of LED devices, and skips if none are usable. The loop walks each LED, sets each trigger token after removing bracket markers, sweeps brightness from zero to max in up to 16 steps, restores original brightness and trigger, increments bogo ops, and repeats until stopped.

State and persistence behavior: the stressor intentionally mutates sysfs LED trigger and brightness attributes, then restores captured values both after each LED exercise and during final free. State may persist visually or in sysfs if the process is killed outside normal cleanup.

Dependencies and integration points: Linux-only. Uses stress-ng file read/write helpers, dirent cleanup, random shuffling, capability check, and process state. Registered as `CLASS_OS`.

Risks: writing LED sysfs attributes can visibly alter hardware indicators. Not all triggers accept writes, and non-root runs may mostly read state. `orig_trigger` parsing depends on kernel bracket formatting.

Test signals: run on systems with no LEDs, read-only LEDs, and writable LEDs; verify original brightness/trigger restoration, no leaked list nodes, and no failure when individual LED entries lack expected files.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-link.c -->
# sources/test-tools/stress-ng/stress-link.c

Purpose: implements both hard-link `link` and symbolic-link `symlink` stressors through a shared link creation/removal engine, including optional directory fsyncs and symlink readback checks.

Important APIs/types/functions: `stress_link_generic()` receives either `link` or `symlink`, a function name, and sync option. `stress_link_unlink()` removes generated paths. `stress_mount_get()`/`stress_mount_free()` provide mount points for cross-device hard-link probes. `stress_link_info` and `stress_symlink_info` register separate stressors.

Control flow: the generic path creates a temp directory and source file, optionally opens the directory for sync, gathers mount points, sync-starts, and loops creating up to 8192 links. Symlink mode verifies `readlink` and optional `readlinkat` contents and lengths. Hard-link mode attempts cross-mount links to exercise `EXDEV` paths. The loop also probes `pathconf`, invalid `readlink` and `readlinkat` calls, optionally fsyncs the directory, removes generated links, increments bogo ops, and repeats.

State and persistence behavior: temp source file, generated links, optional external temp newpath, and temp directory are removed. Symlinks and hard links are transient but can be numerous during a loop.

Dependencies and integration points: uses stress-ng filesystem temp helpers, mount enumeration, builtin wrappers, settings, and metrics. Hard-link registration is disabled on Haiku; symlink remains registered. Both are `CLASS_FILESYSTEM | CLASS_OS` with always-on verification.

Risks: link limits, quota, minix-like unlink contention, cross-device behavior, and permission constraints produce many expected errors. If interrupted during unlink, cleanup speed can dominate runtime.

Test signals: run hard-link and symlink modes with sync options, on filesystems with low link limits and multiple mounts, and verify source/created links are fully removed and symlink readback catches path corruption.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-list.c -->
# sources/test-tools/stress-ng/stress-list.c

Purpose: implements `list`, a CPU/cache/memory search stressor for BSD `sys/queue.h` list families plus an internal singly-linked tail list.

Important APIs/types/functions: `list_entry_t` carries a value and a union of queue entry link fields. Compile gates define support for `CIRCLEQ`, `LIST`, `SLIST`, `STAILQ`, and `TAILQ`. Method functions insert all entries, search for every entry, remove all entries, and update per-method `stress_metrics_t`. `stress_list_all()` rotates across available methods.

Control flow: `stress_list()` resolves method and size, allocates entries, optionally installs a SIGALRM longjmp handler, initializes entry values, sync-starts, and loops invoking the selected method. After each pass it mutates every entry value with a random xor/rotate to perturb memory contents, increments bogo ops, and continues. On exit or signal jump it restores SIGALRM, emits searches-per-second metrics for methods with data, frees entries, and returns status.

State and persistence behavior: all list nodes are heap memory reused across iterations. Queue links are reset by each method. No filesystem state exists. Static rotation index in `stress_list_all()` persists per process.

Dependencies and integration points: depends on `sys/queue.h` macro availability and optional `sigsetjmp` support. Uses stress-ng settings, signal helpers, metrics, random, and process state. Registered as `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SEARCH`.

Risks: O(n^2) search behavior means max list size is intentionally expensive. `siglongjmp` from SIGALRM is used to escape long searches, so cleanup must tolerate partially modified lists. Queue macro availability differs across libc implementations.

Test signals: run each method and `all`, min/max sizes, and forced timeout. Expected signals are nonzero method metrics, no missing-entry failures, and clean SIGALRM restoration.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-list.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-llc-affinity.c -->
# sources/test-tools/stress-ng/stress-llc-affinity.c

Purpose: implements `llc-affinity`, a last-level-cache stressor that repeatedly changes CPU affinity while reading and writing an LLC-sized memory buffer, optionally flushing cache lines, locking memory, and randomizing NUMA placement.

Important APIs/types/functions: `cache_line_func_t` abstracts read/write loops. Specialized write functions cover 64-byte and arbitrary cache-line sizes, with optional x86 `clflush`/`clflushopt` and PPC `dcbst`. `stress_llc_affinity()` orchestrates CPU list discovery, cache-size selection, NUMA setup, function selection, affinity changes, memory traffic, and metrics.

Control flow: the stressor obtains allowed CPUs, catches SIGILL for optional assembly opcodes, reads options, discovers LLC size and line size if not specified, scales size by NUMA node count, mmaps a buffer at least as large as CPU count times page size or LLC size, optionally randomizes NUMA pages and `mlock`s memory, selects read/write functions, sync-starts, and loops setting affinity to the next CPU, reading the buffer, writing the buffer, and incrementing bogo ops.

State and persistence behavior: anonymous memory buffer, optional NUMA masks, CPU affinity mask, and metrics are process-local. CPU affinity is changed repeatedly and not explicitly restored before process exit.

Dependencies and integration points: requires `sched_setaffinity`. Integrates with stress-ng affinity, CPU cache discovery, NUMA, mmap, signal, target-clone, and architecture assembly helpers. Registered as `CLASS_CPU_CACHE`.

Risks: cache-size discovery can fail; assembly cache flush instructions may be unavailable despite compile support, hence SIGILL catch. NUMA page randomization and mlock can require resources. Static `val` counters inside target-cloned functions are not synchronized across workers, which is acceptable for stress but not correctness data.

Test signals: run with explicit and discovered sizes, clflush enabled/disabled, NUMA enabled where supported, mlock under limits, and many CPUs. Confirm metrics for read MB/s, write MB/s, and affinity changes/sec.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-llc-affinity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-loadavg.c -->
# sources/test-tools/stress-ng/stress-loadavg.c

Purpose: implements `loadavg`, a pthread fan-out stressor that creates many low-priority threads to raise scheduler load average, with optional Linux temp-file I/O to contribute blocked I/O load.

Important APIs/types/functions: `stress_loadavg_info_t` records thread handles and creation status. Volatile flags `keep_running_flag` and `keep_thread_running_flag` coordinate shutdown. `stress_loadavg_threads_max()` reads `/proc/sys/kernel/threads-max`. `stress_loadavg_func()` is the per-thread loop.

Control flow: the worker resolves `loadavg-max`, caps it to `threads-max` when known, divides per stress-ng instance, allocates thread records, optionally creates an unlinked temp file for Linux I/O, blocks SIGALRM and polls pending signals, sync-starts, then creates up to the per-worker thread limit. Threads nice themselves to 19, optionally seek/write one byte to the temp fd, increment bogo ops, yield, and stop on time or flags. The parent sleeps/yields until stop, clears the thread flag, joins created threads, closes/removes resources, and exits.

State and persistence behavior: runtime state is thread records, shared stop flags, optional temp fd, and process signal mask. The temp file is unlinked immediately and temp directory removed after close.

Dependencies and integration points: compile-gated on pthread support. Uses stress-ng pthread args, signal pending helper, temp filesystem helpers, settings, bogo ops, and process state. Registered as `CLASS_SCHEDULER | CLASS_OS`.

Risks: extremely high thread counts can exhaust process or system resources, so creation stops on `EAGAIN`. Blocking SIGALRM changes signal handling assumptions within the process. On Linux all threads share a single temp fd for optional writes.

Test signals: run min, default, and capped high `--loadavg-max`, check graceful handling of `EAGAIN`, all created threads joined, temp dir removed, and bogo ops from worker threads.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-loadavg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-locka.c -->
# sources/test-tools/stress-ng/stress-locka.c

Purpose: implements `locka`, an advisory file-lock contention stressor that has parent and child processes repeatedly acquire random byte-range write locks on a shared file and recycle old lock records.

Important APIs/types/functions: `stress_locka_info_t` stores offset, length, and pid for acquired locks. `stress_locka_info_list_t locka_infos` tracks active, tail, free-list, and length. `stress_locka_info_new()`, `stress_locka_info_head_remove()`, and `stress_locka_info_free()` manage records. `stress_locka_contention()` performs random `F_SETLK` lock attempts and unlocks older ranges via `stress_locka_unlock()`.

Control flow: `stress_locka()` creates a shared temp directory, opens a lock file, writes 1 MiB of zero-filled content, reports disk usage, sync-starts, forks a child pinned toward the parent CPU, and both parent and child run `stress_locka_contention()` on the inherited fd. Each contention loop limits active records to 1024 by unlocking the oldest, chooses random length and offset, attempts nonblocking `F_SETLK`, records successful locks, and increments bogo ops. Teardown kills the child, frees lock records, closes and unlinks the file, and removes the directory.

State and persistence behavior: the file and directory are temporary. Advisory locks live in kernel state associated with processes and fds. The active-lock list is process-local, so parent and child do not share lock bookkeeping.

Dependencies and integration points: compile-gated on POSIX `fcntl` lock commands and lock types. Uses stress-ng affinity, fork retry, kill helpers, temp filesystem, CPU discovery, scheduler settings, and process state. Registered as `CLASS_FILESYSTEM | CLASS_OS`.

Risks: because locks are advisory and process-scoped, inherited fd semantics and parent/child interactions are kernel-dependent. The file directory creation intentionally races across instances and tolerates `EEXIST`. Failed lock attempts are ignored to maximize contention.

Test signals: run multiple workers with `--verify`, confirm no stale lock file/directory, child is reaped, bogo ops advance under contention, and failures are limited to resource/fork or unexpected `fcntl` unlock errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-locka.c -->
