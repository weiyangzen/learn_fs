# subset-b-009371 research

Grouped research report for 18 stress-ng stressor implementations under `sources/test-tools/stress-ng`. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-goto.c -->
# sources/test-tools/stress-ng/stress-goto.c

## Purpose
`stress-goto.c` implements the `goto` CPU stressor, a branch-prediction and instruction-flow workload built around GCC-style labels-as-values. It starts workers that repeatedly jump through 1024 generated labels in forward, backward, or random direction and reports "million gotos per sec".

## Important APIs, Types, And Functions
The user-facing options are `goto-direction` and `goto-ops`; `stress_goto_direction()` maps method indices to `forward`, `backward`, and `random`. `MAX_LABELS` is 0x400. The `G(n)` macro emits each label body, increments every 64th label counter, and jumps through the active label table. `stress_goto()` builds `labels_forward` and `labels_backward` from the static `default_labels` table, selects the requested direction, drives the loop with `stress_continue()`, and records metrics. `stress_goto_info` registers the stressor as `CLASS_CPU` with `VERIFY_ALWAYS`.

## Control Flow
On supported compilers, startup initializes forward/backward transition arrays, reads the selected direction, waits at the stress-ng sync barrier, then enters label `L0x000`. Each full 1024-label pass increments the bogo counter. In random mode the active label array is switched between forward and backward using `stress_mwc1()` before each pass. On termination it checks sampled label counters against the bogo counter and computes gotos/second.

## State And Persistence
State is process-local: static label arrays, a static counter array, the global stress-ng bogo counter, and a metrics record. It writes no files and has no persistent external state.

## Dependencies And Integration Points
The implementation depends on `HAVE_LABEL_AS_VALUE`, compiler feature gates, stress-ng random/time/sync/metrics helpers, and compiler-specific optimization controls. It is unimplemented on PCC or compilers without labels-as-values.

## Risks
The generated label table is large and brittle: missing or misordered labels break the branch walk. Compiler optimization can be expensive, so clang/icx are forced to `OPTIMIZE0`. Verification only samples every 64th label, so small unsampled errors could escape. This stressor is non-portable C by design.

## Test Signals
Useful signals are successful build on GNU-label compilers, correct unimplemented fallback on unsupported compilers, valid parsing of all `goto-direction` methods, no counter mismatches in verify mode, and plausible "million gotos per sec" metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-goto.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-gpu.c -->
# sources/test-tools/stress-ng/stress-gpu.c

## Purpose
`stress-gpu.c` implements a headless GPU rendering stressor using GBM, EGL, and OpenGL ES 2. It renders colored triangles, optionally uploads textures each frame, drives fragment shader work through a configurable loop count, and samples GPU frequency when pthread support is available.

## Important APIs, Types, And Functions
Options include `gpu-devnode`, `gpu-frag`, `gpu-tex-size`, `gpu-upload`, `gpu-xsize`, and `gpu-ysize`. `compile_shader()` and `load_shaders()` create the GLES program from embedded vertex and fragment shaders. `get_config()`, `egl_init()`, and `gles2_init()` set up the GBM/EGL surface, context, attributes, texture buffer, and draw state. `stress_gpu_run()` performs texture uploads, clears, draws six vertices, and calls `glFinish()`. `stress_gpu_child()` performs the full setup/run/cleanup under `stress_oomable_child()`. `stress_gpu_supported()` checks that the render node opens.

## Control Flow
The child blocks `SIGALRM`, temporarily suppresses stderr noise from graphics stacks, disables Mesa shader cache/logging, reads options, opens the render node, creates GBM/EGL/GLES state, optionally starts a frequency-sampling pthread, waits at the sync barrier, then loops draw/upload/finish until alarm or stop. It increments bogo ops per rendered frame and records average GPU MHz when samples are available.

## State And Persistence
Global process state includes `program`, `display`, `surface`, GBM handles, `gpu_card`, and `teximage`. Environment variables alter Mesa runtime behavior. No persistent files are written by the stressor, but it reads `/sys/class/drm/cardN/gt_cur_freq_mhz`.

## Dependencies And Integration Points
The stressor is compiled only with EGL headers/libs, GLES2, GBM, and optional pthreads. It integrates with stress-ng OOM isolation, metrics, process state, signal, and settings helpers.

## Risks
Driver behavior varies widely; EGL/GBM setup failures should skip rather than fail. Cleanup is partial because GL/EGL objects are not explicitly destroyed before process exit. Global graphics state would be unsafe across threads, but stress-ng workers are separate processes. Large texture sizes can exhaust memory or hit GL limits.

## Test Signals
Build feature gating, successful skip on systems without `/dev/dri/renderD128`, shader compile/link success, GL error-free loops, restored stderr, valid `gpu-card` parsing, and nonzero frame/GPU-frequency metrics are the main signals.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-gpu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-handle.c -->
# sources/test-tools/stress-ng/stress-handle.c

## Purpose
`stress-handle.c` exercises Linux file-handle APIs by resolving `/dev/zero` with `name_to_handle_at()`, reopening it through `open_by_handle_at()`, and issuing valid and invalid handle operations.

## Important APIs, Types, And Functions
`stress_mount_info_t` stores parsed mount path and mount id pairs from `/proc/self/mountinfo`. `get_mount_info()` fills a fixed `MAX_MOUNT_IDS` array using `getline()` and `sscanf()`, and `free_mount_info()` releases duplicated paths. `stress_handle_child()` allocates and resizes `struct file_handle`, calls `name_to_handle_at()` first to discover handle size and then to fetch the handle, finds the matching mount fd, calls `open_by_handle_at()`, and exercises malformed flags, names, sizes, fds, and stale randomized handles. `stress_handle()` wraps the child in `stress_oomable_child()`.

## Control Flow
The parent parses mountinfo, waits at the sync barrier, and runs an OOM-isolated child. The child loops until `stress_continue()` is false: allocate file handle, request size expecting `EOVERFLOW`, resize, fetch handle, open the mount path for the returned mount id, try `open_by_handle_at()`, run negative syscall coverage, close descriptors, free memory, and increment bogo ops.

## State And Persistence
State is a static mount-info array and per-iteration heap allocations/fds. The file under test is `/dev/zero`; no files are created or persisted. Mount information is a snapshot from `/proc/self/mountinfo`.

## Dependencies And Integration Points
Feature gates require `name_to_handle_at`, `open_by_handle_at`, and `AT_FDCWD`. It uses stress-ng bad-fd generation, OOM isolation, sync, process state, and logging helpers.

## Risks
`open_by_handle_at()` commonly requires privilege and may return `EPERM`, which is intentionally nonfatal. Mountinfo parsing assumes stable field positions and unescaped paths. Mount topology can change between parsing and use. Allocation failures are tolerated by retrying.

## Test Signals
Expected signals are `EOVERFLOW` on the sizing call, graceful skip on `ENOSYS`, tolerated `EPERM`, no leaked fds across iterations, correct mount id lookup, and successful cleanup of mount path allocations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hash.c -->
# sources/test-tools/stress-ng/stress-hash.c

## Purpose
`stress-hash.c` benchmarks and validates many string hash implementations from stress-ng's `core-hash` helpers and optional xxHash. It measures hash throughput and a simple bucket-distribution chi-squared score.

## Important APIs, Types, And Functions
`stress_hash_stats_t` tracks duration, chi-squared score, and total hashes. `stress_bucket_t` contains 256 buckets and a 128-byte key buffer. `stress_hash_method_info_t` maps method names to callbacks. `stress_hash_generic()` generates an ASCII random buffer, hashes every suffix length from 127 down to 1, updates bucket counts, computes the distribution score, and optionally verifies a checksum. Method wrappers adapt functions such as adler32, Jenkin, Murmur3, PJW, djb2a, fnv1a, sdbm, crc32c, xor, mul/add, coffin, x17, loselose, Knuth, mid5, xorror, and optional `XXH64`.

## Control Flow
`stress_hash()` reads `hash-method`, zeroes global per-method stats, waits at the barrier, then repeatedly calls the selected method. Method `all` rotates through all concrete methods using a static index. On exit, instance zero prints per-method rates and chi-squared values for methods that ran.

## State And Persistence
State is process-local and in memory: static stats for each method, the static rotating index in `stress_hash_all()`, the stack bucket, and stress-ng random state. There is no external persistence.

## Dependencies And Integration Points
It depends on `core-hash.h`, endian detection, random buffer helpers, metrics/logging, and optional `xxhash.h` plus `libxxhash`. Verification is controlled by global stress-ng verify flags.

## Risks
Checksum constants are endian-sensitive for some methods and can break with algorithm changes, compiler issues, or different helper semantics. The `all` method's static index is not reset per invocation within a process. Chi-squared is a rough distribution signal, not a statistical test of full hash quality.

## Test Signals
Run every advertised `hash-method`, verify checksum pass on little- and big-endian targets, optional xxHash inclusion/exclusion, sane printed rates, and no failures under repeated `all` rotation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hdd.c -->
# sources/test-tools/stress-ng/stress-hdd.c

## Purpose
`stress-hdd.c` is a filesystem I/O stressor that creates a temporary file per worker, writes and reads it sequentially or randomly, optionally uses sync/direct/iovec/fadvise modes, verifies data patterns, and reports read/write throughput and extent counts.

## Important APIs, Types, And Functions
Options include `hdd-bytes`, `hdd-write-size`, `hdd-opts`, and `hdd-sleep`. `stress_hdd_opts_t` maps option strings to internal flags, exclusions, fadvise advice, and open flags. `stress_hdd_opts()` parses comma-separated modes and stores derived settings. `stress_hdd_write()` and `stress_hdd_read()` choose among `write`, `writev`, `pwritev`, `pwritev2`, `read`, `readv`, `preadv`, and `preadv2`. `stress_hdd_invalid_read()` and `stress_hdd_invalid_write()` exercise negative syscall paths. `data_value()` and `hdd_fill_buf()` produce deterministic verification data.

## Control Flow
`stress_hdd()` clamps sizes, derives per-instance file size, creates a temp directory and aligned buffer, waits at the barrier, then repeatedly opens/truncates/unlinks a temp file, applies fadvise, runs invalid I/O coverage, performs selected random/sequential writes, stats the file, performs selected reads with optional verification, records extent counts, closes the fd, and optionally sleeps. Aggressive mode cycles through individual hdd options when no explicit options are set.

## State And Persistence
The stressor creates temporary directories and files through stress-ng filesystem helpers and removes them before exit. Metrics accumulate read/write byte counts and durations in process memory. It may affect filesystem caches, allocation state, atime/mtime, and sync pressure while running.

## Dependencies And Integration Points
It depends on POSIX file APIs, optional vectored I/O, `posix_fadvise`, sync calls, `futimes`, aligned allocation, stress-ng temp-file helpers, extent probing, metrics, and global minimize/maximize/aggressive/verify flags.

## Risks
This stressor can consume significant disk space and I/O bandwidth. `O_DIRECT` alignment and filesystem support vary. Random writes can leave sparse/zero regions, handled specially by verification. Some filesystems return `ENOSPC`, `EDQUOT`, partial reads, or unsupported direct I/O. Option exclusions must stay consistent to avoid contradictory modes.

## Test Signals
Important signals are successful temp cleanup, correct option parsing/exclusion errors, valid data verification under sequential/random modes, tolerated `ENOSPC` retry behavior, no aligned-buffer faults with `O_DIRECT`/iovec, and populated read/write/combined throughput plus extent metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hdd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-heapsort.c -->
# sources/test-tools/stress-ng/stress-heapsort.c

## Purpose
`stress-heapsort.c` stresses CPU, cache, and memory by repeatedly heap-sorting arrays of 32-bit integers using either libc/BSD `heapsort()` when available or a local non-libc heapsort implementation.

## Important APIs, Types, And Functions
Options are `heapsort-size`, `heapsort-method`, and `heapsort-ops`. `heapsort_nonlibc()` implements heap construction and extraction using stress-ng sort copy/swap helpers. `stress_heapsort_methods[]` maps `heapsort-libc` and `heapsort-nonlibc` to function pointers. `stress_heapsort()` allocates data with `stress_mmap_populate()`, initializes and shuffles data through `core-sort`, sorts forward and reverse, verifies ordering when requested, and records comparison metrics.

## Control Flow
The stressor selects a method and array size, mmaps anonymous data, optionally installs a `SIGALRM` longjmp handler, initializes sorted data, waits at the sync barrier, then loops: shuffle, forward sort, optional ascending verification, reverse sort, optional descending verification, mangle data, reverse sort again, optional verification, and bogo increment. On alarm longjmp or stop it restores signal handling, sets deinit state, records metrics, and unmaps memory.

## State And Persistence
State is memory-only: the data mapping, comparison counters maintained by `core-sort`, local duration/count totals, and optional static signal-jump globals. It writes no files.

## Dependencies And Integration Points
It depends on stress-ng mmap/madvise/signal/sort helpers, optional libc/BSD heapsort availability, `HAVE_SIGLONGJMP`, and global verify/minimize/maximize flags.

## Risks
The non-libc implementation uses variable-length stack temporary storage sized by element size; current callers use 32-bit integers, keeping that safe. `siglongjmp` can bypass loop internals and requires careful restoration. Large sizes can create long O(n log n) runs and memory pressure. Libc heapsort semantics may differ by platform.

## Test Signals
Run both method choices when available, verify ascending/descending order under `--verify`, exercise min/max sizes, confirm `SIGALRM` exits cleanly, and check comparison-per-second and comparison-per-item metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-heapsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hrtimers.c -->
# sources/test-tools/stress-ng/stress-hrtimers.c

## Purpose
`stress-hrtimers.c` stresses high-resolution POSIX timers by forking child processes that create `CLOCK_REALTIME` timers delivering `SIGRTMIN` at high frequency. It can optionally adjust nanosecond delay to maximize timer rate.

## Important APIs, Types, And Functions
The option `hrtimers-adjust` enables adaptive delay. `stress_hrtimers_set()` fills an `itimerspec` from global `ns_delay`. `stress_hrtimers_handler()` increments the shared bogo counter under a stress-ng lock and cancels the timer when stopping, timeout, or pending interrupt is detected. `stress_hrtimer_process()` installs the realtime signal handler, creates/arms/deletes the timer, and adjusts delay based on `timer_getoverrun()`. `stress_hrtimers()` manages up to `PROCS_MAX` child processes.

## Control Flow
The parent installs SIGCHLD handling, allocates shared child pid records, creates a lock, forks eight children, waits at the global barrier, releases child barriers, then sleeps until stop. Each child waits on its per-pid barrier, applies scheduler/OOM settings, creates a timer, arms it, and periodically adjusts timing until `stress_continue()` becomes false. Parent teardown kills/reaps children and records signal rate.

## State And Persistence
Shared state includes global `s_args`, `timerid`, `time_end`, `ns_delay`, and a stress-ng lock. Child pid records are mmap-backed. No persistent state is written.

## Dependencies And Integration Points
Feature gates require librt timer APIs. Integration uses stress-ng process synchronization, locking, scheduler helpers, OOM adjustment, parent-death alarms, child reaping, bogo counters, and metrics.

## Risks
Signal handlers call a limited set of helper/shim functions and must preserve errno. Timer rates are scheduler and privilege sensitive; SCHED_RR may fail silently through the helper. Global timer state is per process after fork but would not be thread-safe. Resource exhaustion from timers should skip.

## Test Signals
Signals include successful skip on missing timer support, children start and reap cleanly, `hrtimers-adjust` changes delay without runaway, no stuck timers after stop, and plausible `hrtimer signals per sec` metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hrtimers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hsearch.c -->
# sources/test-tools/stress-ng/stress-hsearch.c

## Purpose
`stress-hsearch.c` exercises POSIX `hsearch()`-style hash table lookup or a local fallback implementation by inserting numeric string keys and repeatedly finding them.

## Important APIs, Types, And Functions
Options are `hsearch-size`, `hsearch-method`, and `hsearch-ops`. `stress_hsearch_method_t` maps method names to `hcreate`, `hsearch`, and `hdestroy` functions. The fallback uses `hash_table_t`, `hcreate_nonlibc()`, `hsearch_nonlibc()`, and `hdestroy_nonlibc()` with a prime-sized open-addressed table and a simple rotate/add hash. `stress_hsearch()` allocates keys, populates entries, scans finds, and optionally verifies returned data.

## Control Flow
The stressor selects libc or non-libc method, clamps size via stress-ng flags, creates a table with 25 percent slack, allocates key pointers, stringifies and inserts every index, waits at the sync barrier, then repeatedly finds all keys and verifies returned data when requested. Cleanup frees keys on Linux, frees the key array, destroys the hash table, and exits.

## State And Persistence
For fallback mode, `htable` and `htable_size` are static process-global state. Keys and table entries are heap allocations. There is no file or persistent state. Some platforms' `hdestroy()` ownership semantics differ, so cleanup intentionally avoids freeing keys except on Linux.

## Dependencies And Integration Points
It integrates with optional `<search.h>`, stress-ng prime checking, string duplication, memory diagnostics, process state, and verify/minimize/maximize flags.

## Risks
Libc `hsearch()` has process-global behavior on some systems, which can conflict if reused unexpectedly. Cleanup semantics differ across BSD/Linux. The fallback table uses index `0` as a sentinel and may degrade with clustering. Casting integer indices through `void *` assumes round-trip width is sufficient.

## Test Signals
Run libc and non-libc methods where exposed, verify finds for all inserted keys, exercise min/max table sizes, check low-memory behavior, and confirm platform-specific key cleanup does not double-free.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hsearch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hyperbolic.c -->
# sources/test-tools/stress-ng/stress-hyperbolic.c

## Purpose
`stress-hyperbolic.c` stresses libm hyperbolic functions by repeatedly evaluating `cosh`, `sinh`, and `tanh` in double, float, and long-double variants over fixed ranges, checking expected sums, and exporting per-function operation rates.

## Important APIs, Types, And Functions
`stress_hyperbolic_method_t` maps method names to callbacks. Methods include `cosh`, `coshf`, `coshl`, `sinh`, `sinhf`, `sinhl`, `tanh`, `tanhf`, `tanhl`, and `all`. Each method loops `STRESS_HYPERBOLIC_LOOPS` times with unroll pragmas and target clones, accumulates a sum through shim math functions, increments bogo ops, and returns whether the checksum exceeded tolerance. `stress_hyperbolic_exercise()` times one method and updates `stress_hyperbolic_metrics`.

## Control Flow
`stress_hyperbolic()` reads the selected method, zeroes metrics, waits at the barrier, repeatedly exercises the chosen method until stop or checksum failure, sets deinit state, then emits one metric per concrete method that ran. The `all` method iterates all concrete methods each pass.

## State And Persistence
State is in static metrics and stack accumulators. There is no external state or persistence.

## Dependencies And Integration Points
The file depends on stress-ng math shims, `core-put`, target-clone and pragma helpers, metrics, option parsing, and global process-state/sync helpers.

## Risks
Expected sums are tolerance-based and may vary across libm implementations, extended precision modes, compiler optimizations, and target clones. Each method increments bogo count internally, so `all` increments multiple times per outer loop. Long-double precision tolerance changes by `sizeof(long double)` but still may be platform-sensitive.

## Test Signals
Signals include successful verify-mode checks for every method, sane metrics named `<method> ops per second`, correct method selection, and no false checksum failures across supported architectures/libm variants.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-hyperbolic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-icache.c -->
# sources/test-tools/stress-ng/stress-icache.c

## Purpose
`stress-icache.c` stresses instruction-cache behavior by creating executable anonymous pages filled with return opcodes, repeatedly modifying cache-line-sized chunks of the executable code, flushing instruction caches, restoring execute permissions, and calling the generated functions.

## Important APIs, Types, And Functions
The option `icache-pages` controls the number of pages. `icache_madvise_nohugepage()` requests `MADV_NOHUGEPAGE` where available. `icache_mprotect()` wraps protection changes. `stress_icache_func()` performs the modify/flush/execute loop. `stress_icache()` allocates executable memory with `stress_mmap_populate()`, copies `stress_ret_opcode.opcodes` every 64 bytes, synchronizes workers, runs the loop, and unmaps pages. `stress_icache_info` uses `stress_asm_ret_supported` as the supported hook.

## Control Flow
After size selection and SIGSEGV catching, the stressor mmaps RWX pages, names the mapping, populates return stubs, reports memory use, waits at the barrier, and calls `stress_icache_func()`. The loop toggles page protections to RWX, bit-flips/restores words every 64 bytes with `shim_flush_icache()`, changes pages back to RX, calls each return stub, flushes cache, and increments bogo ops.

## State And Persistence
State is the anonymous executable mapping and local counters. No files are written. The stressor temporarily creates writable executable pages.

## Dependencies And Integration Points
It is gated to selected architectures with `HAVE_MPROTECT`, return-opcode support, cache flush shims, mmap helpers, signal handling, and stress-ng settings/metrics.

## Risks
W^X policies, SELinux, hardened kernels, or architecture restrictions can reject RWX mappings or protection changes. Self-modifying code can fault if cache flush semantics are wrong. Huge pages would undermine the intended page behavior, hence `MADV_NOHUGEPAGE`.

## Test Signals
Signals include supported-hook pass/fail, graceful skip on `mmap` or `mprotect` denial, no SIGSEGV during generated calls, correct page-count scaling, and observable instruction-cache misses under perf.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-icache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-icmp-flood.c -->
# sources/test-tools/stress-ng/stress-icmp-flood.c

## Purpose
`stress-icmp-flood.c` sends raw IPv4 ICMP echo packets to localhost to stress raw socket send paths, checksum generation, and loopback/network stack processing.

## Important APIs, Types, And Functions
Option `icmp-flood-max-size` enables randomized payloads up to the IPv4 packet limit; otherwise payloads are capped at 1000 bytes. `stress_icmp_flood_supported()` requires `CAP_NET_RAW`. `stress_icmp_flood()` opens `socket(AF_INET, SOCK_RAW, IPPROTO_RAW)`, enables `IP_HDRINCL` and `SO_BROADCAST`, prepares `struct iphdr` and `struct icmphdr`, fills random payload bytes, sends packets with `sendto()`, and records send and throughput metrics.

## Control Flow
After capability and feature checks, the stressor chooses payload limit, opens/configures the raw socket, sets destination/source to `127.0.0.1`, waits at the sync barrier, initializes IP/ICMP headers, then loops: choose payload length, update total length/id/sequence, perturb payload, compute ICMP checksum, send the packet, count failures or bytes, increment bogo ops, and advance sequence. Exit computes successful send rate, MB/sec, and percent success.

## State And Persistence
State is in the raw socket, stack packet buffer, counters, and local metrics. It writes no files but injects packets into the local network stack.

## Dependencies And Integration Points
It depends on Linux/Unix IP and ICMP headers, stress-ng capability checks, checksum helper `stress_net_ipv4_checksum()`, random data helpers, metrics, and verify flags.

## Risks
Requires root or `CAP_NET_RAW`; otherwise it must skip. Large randomized packets may fragment or fail. The packet buffer is stack-allocated near the maximum IP length. The code counts send failures but does not inspect receive behavior, so network-stack acceptance is inferred from `sendto()`.

## Test Signals
Signals include correct skip without capability, successful raw socket configuration, nonzero sendto calls/sec, reasonable success percentage, checksum correctness, and no stack/buffer overruns with max-size enabled.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-icmp-flood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-idle-page.c -->
# sources/test-tools/stress-ng/stress-idle-page.c

## Purpose
`stress-idle-page.c` stresses Linux idle page tracking by writing and reading chunks of `/sys/kernel/mm/page_idle/bitmap` while scanning through the bitmap.

## Important APIs, Types, And Functions
`bitmap_file` points to the kernel idle-page bitmap. `stress_idle_page_supported()` requires `CAP_SYS_RESOURCE`, effective root, and read access to the bitmap. `stress_idle_page()` opens the bitmap read-write, writes 64 `uint64_t` words of all ones to mark pages idle, seeks back, reads the same region, advances the offset, handles `ENXIO` by wrapping to zero, and increments bogo ops.

## Control Flow
On Linux, support checking is stricter than the compile gate. Runtime opens the sysfs bitmap, initializes the set buffer, waits at the sync barrier, then loops over seek/write/seek/read at the current offset. If the kernel reports `ENXIO`, scanning wraps to the start. A guard aborts if the seek position stops advancing.

## State And Persistence
The stressor mutates kernel idle-page tracking state via sysfs but creates no regular files. Local state is the bitmap fd, current offset, last offset, and stack buffers.

## Dependencies And Integration Points
It is Linux-only and depends on stress-ng capability checks, process state/sync helpers, and standard `open`, `lseek`, `read`, and `write`.

## Risks
Requires root and a kernel configured with idle page tracking. Writing the bitmap affects idle-page accounting for the running system. Offset handling must avoid infinite loops on short or non-advancing scans. Access failures should skip rather than fail.

## Test Signals
Expected signals are support skip without root/capability/sysfs file, successful read-write scans on configured kernels, wrap on `ENXIO`, bogo increments while advancing, and early abort if the offset stalls.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-idle-page.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-inode-flags.c -->
# sources/test-tools/stress-ng/stress-inode-flags.c

## Purpose
`stress-inode-flags.c` stresses filesystem inode flag and file-attribute interfaces by repeatedly toggling `FS_IOC_GETFLAGS`/`FS_IOC_SETFLAGS` and shimmed `file_getattr`/`file_setattr` flags on a temporary directory and file from several threads.

## Important APIs, Types, And Functions
`stress_data_t` shares directory fd, file fd, and filename. `inode_flags[]` and `attr_flags[]` collect available filesystem flags from `<linux/fs.h>`. `stress_inode_flags_ioctl()` reads current flags, sets or clears a requested bit pattern, then clears the bit. `stress_inode_flags_ioctl_sane()` resets flags to zero so cleanup can remove files. `stress_inode_flags_stressor()` iterates generated flag permutations, individual flags, file-attribute get/set operations, invalid filename/size paths, and bogo increments under a lock. `stress_inode_flags_thread()` runs the same worker function in pthreads.

## Control Flow
The stressor creates a counter lock, generates all flag permutations, makes a temp directory/file, opens directory and file descriptors, starts up to four pthread workers, waits at the barrier, and runs the stressor in the main thread until stop. Teardown stops threads, joins them, resets flags to sane values, closes fds, unlinks the temp file, removes the temp directory, frees permutations, and destroys the lock.

## State And Persistence
State includes shared fds, temp path, `keep_running`, generated permutations, and a lock. Temporary filesystem objects are removed. During execution, inode flags on those temp objects are intentionally changed.

## Dependencies And Integration Points
Requires pthreads, `libgen.h`, `FS_IOC_GETFLAGS`, `FS_IOC_SETFLAGS`, `O_DIRECTORY`, stress-ng flag permutation, temp filesystem helpers, shim file-attribute APIs, and bogo lock helpers.

## Risks
Some flags are privileged, immutable, filesystem-specific, or incompatible; failures are mostly ignored to maximize coverage. Forgetting final sane reset can leave an immutable/append-only temp file that cannot be removed. Thread workers share fds and global flags, so stop coordination and cleanup ordering matter.

## Test Signals
Signals include clean temp removal after runs, no stuck immutable files, successful threaded join, bogo count progress, tolerated unsupported flags, and invalid attribute calls returning harmless errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-inode-flags.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-inotify.c -->
# sources/test-tools/stress-ng/stress-inotify.c

## Purpose
`stress-inotify.c` exercises Linux inotify by creating temporary files/directories and verifying event delivery for access, modify, attrib, close, open, move, create, delete, delete-self, and move-self operations. It also probes invalid inotify operations for syscall coverage.

## Important APIs, Types, And Functions
`stress_inotify_t` maps each event helper to a description. `exercise_inotify1()`, `exercise_inotify_add_watch()`, and `exercise_inotify_rm_watch()` cover valid and invalid inotify API calls, masks, watch descriptors, `INOTIFY_IOC_SETNEXTWD`, bad fds, and non-inotify fds. `inotify_exercise()` is the common harness: it creates an inotify fd, adds a watch, invokes a file operation helper, waits with `select()`, checks bytes with `FIONREAD`, reads events, and matches flags/names. Helpers `mk_file`, `mk_dir`, `rm_file`, and `rm_dir` manage test objects.

## Control Flow
`stress_inotify()` creates a temp directory, reports nominal file usage, waits at the sync barrier, then repeatedly walks the `inotify_stressors[]` table. Each concrete event function sets up a scenario, invokes `inotify_exercise()`, and cleans up. The common harness waits up to 10 seconds for expected events and only treats timeouts as failures in verify mode.

## State And Persistence
The stressor creates and removes temporary files/directories under the stress-ng temp directory. Runtime state is fd/watch descriptors and stack event buffers. No persistent files should remain after cleanup.

## Dependencies And Integration Points
Requires glibc 2.9-era inotify APIs, `<sys/inotify.h>`, `select()`, optional epoll for negative tests, stress-ng bad-fd and temp-file helpers, and verify flags.

## Risks
Inotify event coalescing, filesystem latency, queue pressure, or resource limits can cause timeouts or `EMFILE`. Some match names in move helpers are broad, so verification relies on masks as well as names. Negative tests should not accidentally close/remove live descriptors. Cleanup must handle partially completed rename/delete scenarios.

## Test Signals
Run with and without `--verify`, confirm every compiled event helper can complete, observe retry on transient `EMFILE`, validate `FIONREAD` and event parsing, and ensure the temp directory is removed after errors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-inotify.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-insertionsort.c -->
# sources/test-tools/stress-ng/stress-insertionsort.c

## Purpose
`stress-insertionsort.c` stresses CPU, cache, and memory with a simple insertion sort over 32-bit integer arrays, using forward and reverse order passes to drive worst-case data movement and comparison work.

## Important APIs, Types, And Functions
Option `insertionsort-size` controls element count. `insertionsort_fwd()` sorts ascending and returns a comparison/move count approximation. `insertionsort_rev()` sorts descending. `stress_insertionsort()` allocates data with `stress_mmap_populate()`, names/collapses the mapping, installs an optional `SIGALRM` longjmp handler, initializes data through `core-sort`, repeatedly shuffles/sorts/verifies/mangles, and records comparison metrics.

## Control Flow
The stressor chooses size from settings or min/max flags, mmaps the data, initializes sort data, waits at the barrier, then loops: shuffle, ascending insertion sort, optional ascending verification, descending sort, optional descending verification, mangle data, descending sort again, optional verification, and bogo increment. Signal longjmp exits to cleanup if configured.

## State And Persistence
All state is memory-only: the anonymous data mapping, local duration/count totals, and optional signal-jump globals. It writes no files.

## Dependencies And Integration Points
It uses stress-ng mmap/madvise/signal/sort helpers, target-clone optimization, metrics, process state, and verify/minimize/maximize flags.

## Risks
Insertion sort is O(n^2); max size can run for a long time and heavily stress memory bandwidth. The reverse comparison counter expression can undercount in some cases but is used only for metrics. Signal longjmp must restore handlers and unmap memory. Verification is optional and linear.

## Test Signals
Signals include verify-mode ordering checks, clean SIGALRM exit, min/max size behavior, no mmap leak, bogo progress, and populated comparisons/sec and comparisons/item metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-insertionsort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-intmath.c -->
# sources/test-tools/stress-ng/stress-intmath.c

## Purpose
`stress-intmath.c` stresses signed integer arithmetic across multiple widths by generating add, subtract, multiply, divide, and modulo kernels for standard and optional `int_fast*_t` types. It reports per-method million-operations-per-second metrics and verifies repeatability.

## Important APIs, Types, And Functions
`stress_intmath_vals_t` holds initial values and per-operation result slots for 128-bit, fast, 64/32/16/8-bit types as available. Macros `STRESS_INTMATH_ADD`, `SUB`, `MUL`, `DIV`, and `MOD` generate optimized kernels. `stress_intmath_method_t` maps method names to operation counts and generated callbacks. `stress_intmath_methods[]` covers standard widths; `stress_intfastmath_methods[]` covers fast widths when available. `stress_intmath_exercise()` primes a result slot, runs the selected method, updates metrics, and logs verification failures.

## Control Flow
`stress_intmath()` reads `intmath-method` and `intmath-fast`, rejects fast mode if unavailable, selects the method table, seeds four initial random values, clears initialized flags and metrics, waits at the barrier, then loops. Method `all` walks every concrete method each pass; otherwise only the selected method runs. After stop, it emits one metric per method with nonzero duration.

## State And Persistence
State is stack-local arithmetic values plus static metrics and initialization flags. It has no external persistent state.

## Dependencies And Integration Points
It depends on compile-time integer type detection, optional `__int128_t`, stress-ng random helpers, option parsing, metrics, target-clone/pragmas, and global verify flags.

## Risks
The file intentionally exercises signed overflow-prone expressions; behavior can be compiler- and optimization-sensitive even though verification compares repeatability within the same run. Fast-integer method indices depend on availability. `opts` bounds for `intmath-method` are minimal because the callback enumerates methods dynamically. Metrics assume hard-coded operation counts per generated kernel.

## Test Signals
Signals include verify-mode repeatability across all generated methods, fast-mode skip or success by platform, no divide-by-zero, plausible per-method M-ops metrics, and successful builds with/without int128 and int_fast types.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-intmath.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-io-uring.c -->
# sources/test-tools/stress-ng/stress-io-uring.c

## Purpose
`stress-io-uring.c` stresses Linux io_uring setup, submission, completion, and many available opcodes against a small temporary file and mapped iovec buffers. It is run inside an OOM-isolated child.

## Important APIs, Types, And Functions
Options are `io-uring-entries`, `io-uring-rand`, and `io-uring-ops`. `stress_io_uring_file_t` stores file fds, path, iovecs, block sizing, and file size. `stress_io_uring_submit_t` stores SQ/CQ ring mappings, SQEs, fd, and sizes. `shim_io_uring_setup()` and `shim_io_uring_enter()` wrap raw syscalls. `stress_setup_io_uring()` creates rings and mmaps SQ/CQ/SQE areas. `stress_io_uring_submit()` fills an SQE via an opcode-specific setup function, advances the SQ tail, calls `io_uring_enter`, and increments bogo ops. `stress_io_uring_complete()` consumes CQEs and classifies tolerated errors. Opcode setup functions cover read/write, vectored I/O, fsync, nop, fallocate, fadvise, close, madvise, statx, sync_file_range, xattr, ftruncate, and async cancel when compiled.

## Control Flow
The child chooses entries based on CPU count or options, maps iovec structures and buffers, creates a temp directory/file path, sets up io_uring, waits at the barrier, initializes per-opcode user data as supported, then loops. Each iteration opens/truncates the temp file, optionally opens an `O_PATH` fd for statx, submits all or random opcode setup entries that remain supported, drains completions, periodically reads fdinfo, closes fds, and repeats. Cleanup cancels pending read/write ops when available, closes/unmaps rings, unmaps iovecs, unlinks the file, and removes the temp directory.

## State And Persistence
State includes mmap-backed ring buffers, mmap-backed iovec buffers, temp file path/fds, supported flags per opcode, and global `io_uring_rand`. Temporary files are removed.

## Dependencies And Integration Points
Requires Linux io_uring headers, raw syscall numbers, ring offset macros, `posix_memalign`, at least one supported opcode macro, stress-ng mmap/temp/OOM helpers, optional xattr/statx/madvise/fadvise support, and memory barriers.

## Risks
Kernel io_uring restrictions, seccomp, `EPERM`, missing opcodes, or low memory must skip. Ring-tail manipulation is low-level and sensitive to memory barriers. Some completion errors are intentionally tolerated; over-broad tolerance can hide regressions, while under-tolerance causes false failures on filesystem/kernel differences. Static buffers in xattr/statx setup are shared per process.

## Test Signals
Signals include correct skip on `ENOSYS`, `EPERM`, or oversized entries, successful ring mmap/unmap, opcode support downgrades on `EOPNOTSUPP`, no ring stalls under randomized order, clean temp cleanup, and bogo progress through submissions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-io-uring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-io.c -->
# sources/test-tools/stress-ng/stress-io.c

## Purpose
`stress-io.c` is stress-ng's legacy sync I/O stressor. It repeatedly writes to a temp file, calls `fsync`, `fdatasync`, global `sync`, and `syncfs` on the current directory and discovered mount points.

## Important APIs, Types, And Functions
`stess_io_write()` writes a random 32-bit value at offset zero when `syncfs` support is compiled. `stress_io()` creates a temp directory/file, unlinks the file while keeping it open, hints short file I/O, discovers mount points via `stress_mount_get()`, opens directory fds for each mount, and loops through sync operations. It uses a bad fd from `stress_fs_bad_fd_get()` to verify `syncfs` failure behavior.

## Control Flow
With `HAVE_SYNCFS`, setup creates a temp file and opens mount directories. After sync barrier, each iteration writes random data, alternates fsync/fdatasync ordering, calls global `shim_sync()`, writes again, calls `syncfs()` on the current directory and each mount fd, tolerates selected mount errors, checks that `syncfs` on a bad fd does not succeed, and increments bogo ops. Cleanup closes directory/mount/temp fds, frees mount strings, and removes the temp directory.

## State And Persistence
The temp file is unlinked after opening and removed with the temp directory. The stressor intentionally flushes system and filesystem state, affecting the host's I/O writeback behavior while running.

## Dependencies And Integration Points
It depends on stress-ng filesystem and mount helpers, `syncfs` when available, `shim_sync`, fd cleanup helpers, process state/sync, and verify-always registration.

## Risks
Global `sync()` and per-mount `syncfs()` can impose heavy host-wide I/O latency. Mount discovery may include filesystems where syncfs returns quota/space/interruption errors, which are tolerated. If `syncfs` is unavailable at runtime (`ENOSYS`), the loop still counts bogo ops.

## Test Signals
Signals include the legacy warning on instance zero, clean temp directory removal, bad-fd `syncfs` failure, tolerated mount errors, fd cleanup for all discovered mounts, and bogo count progress.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-io.c -->
