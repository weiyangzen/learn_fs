# subset-b-009374 research

Grouped research report for selected `sources/test-tools/stress-ng` memory, mmap, metadata, sleep, sort, and misalignment stressors. Each section preserves the exact source path and is wrapped for reconciliation into the source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memrate.c -->
# sources/test-tools/stress-ng/stress-memrate.c

Purpose: `stress-memrate.c` implements the `memrate` stressor, a memory bandwidth and cache exercising workload that measures read and write throughput over an anonymous buffer. It can run all methods or one selected method, optionally flush caches between methods, force physically discontiguous pages, and throttle read/write rates via `--memrate-rd-mbs` and `--memrate-wr-mbs`.

Important APIs/types/functions: the central types are `stress_memrate_context_t`, shared between parent and oomable child, `stress_memrate_stats_t`, and `stress_memrate_info_t`, the method table row carrying name, read/write class, unthrottled function, and rate-limited function. Macro families `STRESS_MEMRATE_READ`, `STRESS_MEMRATE_READ_RATE`, `STRESS_MEMRATE_WRITE`, `STRESS_MEMRATE_WRITE_RATE`, `STRESS_MEMRATE_WRITE_OP`, and `STRESS_MEMRATE_WRITE_OP_RATE` generate most benchmark functions. The method table includes scalar reads/writes, vector-width variants when `HAVE_VECMATH` or `HAVE_INT128_T` is present, x86 `rep stos*` write methods, non-temporal/direct-store methods, prefetch reads, and `memset`.

Control flow: `stress_memrate` allocates shared context and stats, reads settings, rejects invalid zero-rate combinations, rounds buffer size, synchronizes with other workers, then runs `stress_oomable_child`. The child maps the buffer with `stress_memrate_mmap`, initializes it with random 32-bit words, optionally calls `stress_mmap_discontiguous`, and loops until `stress_continue(args)` is false. In all-method mode it dispatches each table entry except `"all"`; otherwise it dispatches the selected method. `stress_memrate_dispatch` chooses disabled, unthrottled, or rate-limited execution based on the read/write rate setting, and `stress_memrate_dispatch_method` times the call and accumulates kbytes and duration.

State and persistence behavior: all runtime state is in anonymous/private mappings and shared anonymous mappings; no file-backed persistent state is created. The parent reads the shared stats after the oomable child exits, emits per-method metrics and geometric mean read/write rates, and reports aggregate mmap statistics including swapped and contiguous page signals. CPU feature-specific methods can mark a stat invalid when their required instruction support is absent.

Dependencies and integration points: this stressor uses stress-ng core mmap, madvise, CPU cache, vector math, x86 assembly, non-temporal store, OOM child, target-clone, and metrics helpers. It registers `stress_memrate_info` with classifier `CLASS_MEMORY`, option metadata, help text, and `max_metrics_items = SIZEOF_ARRAY(memrate_info) + 3`.

Risks: macro-generated loops assume the mapped buffer is sized and aligned for unrolled accesses; regressions in size rounding or method table ordering can cause overrun or misleading metric labels. Rate limiting uses sleep remainders based on target MB/s and can under- or over-throttle on clock jitter. Architecture-specific stores must be guarded correctly or SIGILL can terminate the child, so feature checks and `stress_signal_catch_sigill` are important. Very large `--memrate-bytes` values can trigger OOM behavior; the oomable wrapper intentionally contains that blast radius.

Test signals: run `stress-ng --memrate 1 --memrate-ops 1 --verify`, one selected scalar method such as `--memrate-method read64`, write-only and read-only throttled modes, and architecture-specific methods on capable hardware. Check that invalid `--memrate-rd-mbs 0 --memrate-wr-mbs 0` fails, disabled method/rate combinations fail early, metrics names match the method table, and mmap stats are reported.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memrate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memthrash.c -->
# sources/test-tools/stress-ng/stress-memthrash.c

Purpose: `stress-memthrash.c` implements the `memthrash` stressor, which creates pthreads that intentionally race over a shared 256 MiB-style matrix buffer (`MEM_SIZE = 1 << 28` with the current constants) using cache, TLB, memcpy/memset, atomic, NUMA, prefetch, and random-chunk access patterns.

Important APIs/types/functions: `stress_memthrash_context_t` carries the parent `stress_args_t`, selected method, CPU/thread counts, and optional NUMA mask. `stress_memthrash_method_info_t` defines the method table. Methods include `chunk1`, `chunk8`, `chunk64`, `chunk256`, `chunkpage`, `copy128`, `flip`, `flush`, `lock`, `matrix`, `memmove`, `memset`, `memset64`, `memsetstosd`, `mfence`, `numa`, `prefetch`, `random`, `reverse`, `spinread`, `spinwrite`, `swap`, `swap64`, `swapfwdrev`, and `tlb`, depending on compile-time feature guards. `stress_memthrash_find_primes` precomputes prime cache-line strides for TLB walking.

Control flow: `stress_memthrash` installs SIGCHLD handling, computes one or more pthreads per stressor based on online CPUs and instance count, allocates optional NUMA masks, selects the method, synchronizes, then runs `stress_oomable_child`. `stress_memthrash_child` allocates per-thread metadata, catches SIGALRM, repeatedly tries to mmap the global `mem` buffer, names/advises it, starts pthreads running `stress_memthrash_func`, then pauses until termination. Each pthread blocks process signals, sleeps briefly to stagger startup, and repeatedly invokes the selected method for matrix sizes from `1 << 20` up to `1 << 28`, incrementing bogo operations and yielding.

State and persistence behavior: state is process-local and intentionally shared by threads through the static `mem` pointer and `thread_terminate` flag. There is no persistent filesystem state. Signal state matters: SIGALRM sets `thread_terminate`, and threads rely on `stress_continue(args)` plus that flag to exit. NUMA method state is transient in `stress_numa_mask_t`.

Dependencies and integration points: the file depends on pthreads, stress-ng mmap/madvise, CPU cache, x86 assembly, non-temporal load/store, target clones, NUMA `mbind` wrappers, prime helpers, and OOM wrappers. It registers `stress_memthrash_info` as `CLASS_MEMORY`; if pthread support is absent it registers `stress_unimplemented`.

Risks: this stressor intentionally has data races and should not be evaluated with ordinary race-detector expectations. Feature-specific assembly and atomic paths must stay correctly guarded, especially on x86, ARM, PPC, and SH4. `stress_memthrash_all` uses a static method index, so concurrent use inside one process depends on benign shared progression. The global `mem` pointer and termination flag mean refactors must preserve the single-process multi-thread model. NUMA rebinding can fail or be expensive on constrained systems.

Test signals: run `stress-ng --memthrash 1 --memthrash-ops 1`, selected methods such as `--memthrash-method tlb`, `spinread`, `memset`, and `random`, and a multi-instance run that exercises thread count logging. Build variants with and without pthreads, NUMA, non-temporal operations, and x86 assembly should compile and expose the correct method list.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-memthrash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mergesort.c -->
# sources/test-tools/stress-ng/stress-mergesort.c

Purpose: `stress-mergesort.c` implements a CPU/cache/memory sort stressor over random 32-bit integers. It can use a platform libc/BSD `mergesort` when available or an internal non-libc merge sort implementation, and it optionally verifies sorted ordering under global verify mode.

Important APIs/types/functions: `mergesort_func_t` abstracts sort implementations. `stress_mergesort_method_t` backs the method option. `mergesort_copy4`, `mergesort_copy`, `mergesort_partition4`, and `mergesort_partition` implement the internal merge sort with a 4-byte optimized path. `mergesort_nonlibc` allocates a temporary left/right workspace with `stress_mmap_populate`. `stress_mergesort_handler` uses siglongjmp on platforms where SIGALRM interruption is supported.

Control flow: `stress_mergesort` selects the method, resolves `--mergesort-size` with minimize/maximize overrides, maps the data array, installs the SIGALRM jump handler, initializes sorted data, synchronizes, and loops. Each iteration shuffles data, forward sorts and optionally verifies ascending order, reverse sorts and optionally verifies descending order, mangles data, reverse sorts again, then increments the bogo counter. Metrics record comparisons per second and comparisons per item from `stress_sort_compare_get`.

State and persistence behavior: all data is anonymous memory (`mergesort-data` plus temporary workspace); no persistent state is written. Sort comparison counters are shared through stress-ng sort helpers for the current process. SIGALRM state is restored on normal and jump-based exit.

Dependencies and integration points: the stressor uses `core-sort`, `core-mmap`, `core-madvise`, `core-signal`, target clones, and stress-ng memory/metric helpers. It registers `stress_mergesort_info` with classifiers `CLASS_CPU_CACHE | CLASS_CPU | CLASS_MEMORY | CLASS_SORT | CLASS_HOT`, verify mode `VERIFY_OPTIONAL`, and options for method and size.

Risks: the recursive merge implementation can consume stack proportional to `log(n)` but temporary mmap size is `nmemb * size`; allocation failure returns a sort failure and is surfaced. Incorrect size handling in the generic partition path would corrupt memory. SIGALRM longjmp must not bypass cleanup. Verification only runs when global verify is enabled, so performance runs can hide ordering bugs until verify tests are used.

Test signals: run `stress-ng --mergesort 1 --mergesort-ops 1 --verify`, test `--mergesort-method mergesort-nonlibc`, test libc method on systems where present, and exercise `--mergesort-size` at min/default/max boundaries. Metrics should be nonzero for completed iterations.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mergesort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-metamix.c -->
# sources/test-tools/stress-ng/stress-metamix.c

Purpose: `stress-metamix.c` implements the `metamix` filesystem stressor, modeled after Lucene-like metadata and random access patterns. It creates files with many small writes at varying offsets, syncs and stats them, reads them back in checksum-derived order, optionally verifies checksums, and mmap-checks page-aligned extents.

Important APIs/types/functions: `file_info_t` records offset, data length, checksum, and validity for up to `METAMIX_WRITES` writes. `stress_metamix_cmp` sorts entries by checksum to randomize later read order. `stress_metamix_file` performs one complete file lifecycle. `counter_lock` coordinates bogo operation accounting across the parent and `METAMIX_PROCS` forked helper processes.

Control flow: `stress_metamix` installs SIGCHLD handling, mmaps a shared PID list, creates the counter lock, computes per-instance bytes, creates the temp directory, records filesystem type text for diagnostics, then forks 15 children. Each child waits for synchronized start and repeatedly calls `stress_metamix_file` while `stress_bogo_inc_lock` permits. The parent also runs the file workload, then reaps children with SIGALRM and cleans the temp directory, lock, and PID mapping.

State and persistence behavior: persistent state is intentionally temporary: one temp directory per stressor instance and per-iteration temp files that are unlinked at the end of `stress_metamix_file`. Checksums live only in stack `file_info`. `counter_lock` is a stress-ng shared lock; PID coordination is in an mmaped shared `stress_pid_t` array.

Dependencies and integration points: the file uses stress-ng filesystem temp helpers, hash helpers, mmap helpers, sort wrappers, process synchronization, kill/wait helpers, and scheduler application in children. It registers `stress_metamix_info` as `CLASS_FILESYSTEM | CLASS_OS` with optional verification and an `--metamix-bytes` option.

Risks: the write-size calculation casts `max_seek` through `uint8_t` for `stress_mwc8modn`, so very small `metamix_bytes` must stay above the enforced minimum. Partial writes break out and can leave fewer valid entries than `METAMIX_WRITES`, which later code handles through `n`. Filesystem behavior varies for `fdatasync`, `fsync` on directories, sparse regions, and mmap of holes. Any cleanup regression can leave temp files behind or orphan helper processes.

Test signals: run `stress-ng --metamix 1 --metamix-ops 1 --verify`, run on tmpfs and a disk filesystem, test small `--metamix-bytes 512`, and confirm no temp files remain. Verification should catch checksum or file-size mismatches; non-verify mode should still exercise stat/lstat, fdatasync, fsync, random reads, mmap reads, and unlink cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-metamix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-min-nanosleep.c -->
# sources/test-tools/stress-ng/stress-min-nanosleep.c

Purpose: `stress-min-nanosleep.c` measures the shortest observed `nanosleep` delays for requested sleeps from 0 ns through powers of two up to a configured maximum. It stresses scheduler/timer behavior and fails verification if measured sleep duration is shorter than requested.

Important APIs/types/functions: `nanosleep_delay_t` stores requested ns, min/max observed ns, count, sum, mean, and update state. `nanosleep_delays_t` stores per-instance arrays plus pid/start/finish flags in shared memory. `stress_min_nanosleep_sched` optionally applies a requested scheduler policy, including special handling for deadline scheduling, FIFO/RR priorities, and fallback policies. `stress_min_nanosleep_init` and `stress_min_nanosleep_deinit` allocate/free the shared delay table.

Control flow: initialization maps one `nanosleep_delays_t` per instance. Each worker reads `--min-nanosleep-max` and `--min-nanosleep-sched`, applies scheduling if possible, initializes delay slots for 0 and powers of two, synchronizes, then loops. For each delay, it measures `NANOSLEEP_LOOPS` calls using `clock_gettime(CLOCK_MONOTONIC)` before and after, records per-call min/max/sum, and increments bogo operations. Instance zero waits for other instances to finish, aggregates all delay rows, prints a table, reports too-short sleeps, and prints the minimum measured sleep.

State and persistence behavior: all state is shared anonymous memory in `delays`. There is no filesystem persistence. Instance zero may wait on sibling pids recorded in the shared table to make sure aggregation sees finished data.

Dependencies and integration points: the file depends on `clock_gettime`, `CLOCK_MONOTONIC`, `nanosleep`, scheduler helpers and shim scheduler attributes, cpuidle headers, mmap helpers, and stress-ng init/deinit hooks. It registers `stress_min_nanosleep_info` with `.init`, `.deinit`, scheduler/interrupt/OS classifiers, `VERIFY_ALWAYS`, and max/scheduler options; unsupported builds register unimplemented.

Risks: timing measurements are sensitive to clock resolution, scheduler priority privileges, virtualization, CPU power states, and signal interruption. The aggregation wait loop depends on child pid bookkeeping and can stall if start/finish flags are mishandled. Deadline/real-time scheduler attempts must remain best-effort because insufficient privilege is common.

Test signals: run `stress-ng --min-nanosleep 1 --min-nanosleep-ops 1`, repeat with `--min-nanosleep-max 1024`, and try scheduler policies available on the host. Verify output should show no “too short” rows; unsupported scheduler changes should log informational messages without failing the stressor.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-min-nanosleep.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mincore.c -->
# sources/test-tools/stress-ng/stress-mincore.c

Purpose: `stress-mincore.c` exercises the `mincore` syscall over mapped, file-backed, unmapped, random/linear, and deliberately invalid arguments. It validates expected success/failure behavior and measures nanoseconds per successful mapped-page `mincore` call.

Important APIs/types/functions: `stress_mincore_file` creates a temporary file, unlinks it immediately, fallocates one page, and returns the fd for file-backed mapping. `stress_mincore_expect` compares return values and errno against expectations while ignoring `ENOSYS`. `stress_mincore` owns the test loop and cleanup.

Control flow: the stressor reads `--mincore-random`, maps one anonymous page, creates/maps one file-backed page if possible, and creates then unmaps a page to preserve an unmapped address. After sync, it loops 100 address probes per bogo iteration. It calls `shim_mincore` on the moving address, on the resident anonymous page, on the file-backed page after writes and optional `msync`, on the unmapped page, and on invalid combinations such as zero length, misaligned address, NULL vec, invalid vector address, NULL address, and NULL/zero arguments. Linear mode increments the probe address by page size; random mode derives page-aligned addresses from MWC RNG and avoids repeating the same address.

State and persistence behavior: persistent filesystem state is limited to a temp directory and unlinked temp file fd, removed during cleanup. Runtime memory state includes anonymous/file mappings and one unmapped address. Metrics are local duration/count values reported as harmonic mean.

Dependencies and integration points: the file uses stress-ng temp-file helpers, `shim_mincore`, `shim_fallocate`, `shim_msync`, memory naming, metrics, and option metadata. It registers as `CLASS_OS | CLASS_MEMORY` with `VERIFY_ALWAYS`; unsupported builds register an unimplemented reason for missing `mincore`.

Risks: errno behavior for invalid `mincore` arguments varies across kernels/libc, and the code explicitly tolerates some alternatives such as `ENOMEM` for NULL/zero arguments. Random address probing can hit mapped regions and should not be treated as a hard failure except unexpected errno. Temp-file setup failure only disables file-backed coverage, not the whole stressor.

Test signals: run `stress-ng --mincore 1 --mincore-ops 1 --verify`, repeat with `--mincore-random`, and test on a system without `mincore` support if possible to verify `EXIT_NOT_IMPLEMENTED`. Metrics should include “nanosecs per mincore call”.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mincore.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-misaligned.c -->
# sources/test-tools/stress-ng/stress-misaligned.c

Purpose: `stress-misaligned.c` stresses CPUs and memory subsystems with misaligned reads, writes, increments, atomics, non-temporal stores, and direct-store variants across 16-, 32-, 64-, and optionally 128-bit widths. It detects architectures that fault or hang on specific methods and disables those methods dynamically.

Important APIs/types/functions: `stress_misaligned_method_info_t` stores method name, function pointer, disabled flag, and exercised flag. Method functions operate on a two-page buffer at offsets such as `+1`, `+63`, and `page_size - N` to cross alignment and page-boundary cases. Signal handlers `stress_misaligned_handler` and `stress_misaligned_timer_handler` use `siglongjmp` to recover from SIGBUS/SIGILL/SIGSEGV or timeout. `stress_misaligned_all` iterates all enabled methods, and `stress_misaligned_exercised` reports successful methods.

Control flow: `stress_misaligned` reads the selected method, installs fault handlers, optionally installs a POSIX timer that sends SIGRTMIN after 0.8 seconds, maps a two-page buffer, applies mergeable/NUMA page advice, enables all methods, synchronizes, then runs the selected method in a loop. If a method faults or times out, the current method is disabled and the sigsetjmp return path logs a skip message. Successful method calls mark the method exercised and increment bogo operations. Cleanup stops/deletes the timer, restores signal defaults, prints exercised methods, frees NUMA masks, and unmaps the buffer.

State and persistence behavior: all state is process-local static state plus the anonymous buffer. `current_method`, `handled_signum`, `use_timer`, and method disabled/exercised flags persist across the stressor call within the process and must be reset by `stress_misaligned_enable_all`. No filesystem state is created.

Dependencies and integration points: the file depends on core arch, x86 assembly, CPU feature helpers, non-temporal store/direct-store helpers, NUMA `mbind` support, mmap/madvise, target clones, and stress-ng signal wrappers. It registers with `CLASS_CPU_CACHE | CLASS_MEMORY`, `VERIFY_ALWAYS`, and a method option; without siglongjmp it registers unimplemented.

Risks: this code deliberately invokes undefined or hardware-specific misaligned behavior, so fault recovery and timer recovery are essential. Atomic operations are explicitly disabled on SH4 and older PPC/PPC64 compiler combinations due to known hazards. Non-temporal/direct-store methods must disable themselves when CPU feature checks fail. The timer is process-global static state and must be cleaned up to avoid later signal surprises.

Test signals: run `stress-ng --misaligned 1 --misaligned-ops 1 --verify`, test `--misaligned-method all`, scalar methods, atomic methods on supported toolchains, and non-temporal/direct-store methods on x86 hardware. Expected output may include skipped methods on strict-alignment architectures; unexpected value read-back messages should fail verification.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-misaligned.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mknod.c -->
# sources/test-tools/stress-ng/stress-mknod.c

Purpose: `stress-mknod.c` exercises `mknod` and, when available, `mknodat` by creating and deleting many temporary node paths plus optional character/block special devices based on real `/dev` device numbers.

Important APIs/types/functions: `stress_mknod_modes_t` defines supported file node mode rows for FIFO, regular file, named socket, and directory when macros are present. `stress_mknod_tidy` removes gray-code-named temp paths. `stress_mknod_find_dev` scans `/dev` for the first matching char/block device and copies `st_rdev`. `stress_mknod_check_errno` treats resource/permission/read-only/invalid errors as benign for stress purposes. `stress_do_mknod` randomly chooses `mknodat` or `mknod` and also probes a known bad fd path.

Control flow: `stress_mknod` validates that at least one mode exists, finds char and block device numbers if possible, creates a temp dir, optionally opens it as an `O_DIRECTORY` fd for `mknodat`, synchronizes, then loops. Each loop tries special char/block node creation if real devices were found, then creates up to `DEFAULT_DIRS` temp nodes with gray-code filenames and random modes, increments bogo operations on successful creation, tidies created paths, syncs, and repeats.

State and persistence behavior: filesystem state is temporary under the stress-ng temp directory. The stressor force-unlinks paths before and after operations and removes the temp directory on exit. It holds only a directory fd and local device ids; no persistent state is intended.

Dependencies and integration points: the file uses Linux-only `mknod`, optional `mknodat`, `basename`, stress-ng temp-file helpers, bad-fd helper, force unlink wrappers, and sync wrapper. It registers `stress_mknod_info` as `CLASS_FILESYSTEM | CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds register “only supported on Linux”.

Risks: permissions, capabilities, filesystem type, quotas, and read-only mounts strongly influence expected errors, so the ignored errno set is necessary. Creating special devices is sensitive and should only use copied device ids, not random ids. Cleanup must remain robust because some mode attempts, especially directories or sockets, may require different removal semantics; current cleanup uses unlink and force unlink paths.

Test signals: run `stress-ng --mknod 1 --mknod-ops 1 --verify` as an unprivileged user and, separately, on filesystems with limited mknod support. Confirm benign errors do not fail the stressor, unexpected errno is reported, and no temp paths remain.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mknod.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mlock.c -->
# sources/test-tools/stress-ng/stress-mlock.c

Purpose: `stress-mlock.c` exercises page locking and unlocking via `mlock`, optional `mlock2`, `munlock`, `mlockall`, and `munlockall`. It creates many small mappings, locks middle pages, unlocks and unmaps them, and probes invalid argument paths.

Important APIs/types/functions: `stress_mlock_pages` reads Linux `/proc/self/status` `VmLck` to track locked page count. `do_mlock` randomly chooses `mlock2` with `MLOCK_ONFAULT` or normal `mlock`, timing a sampled subset for metrics. `stress_mlock_max_lockable` derives the upper bound from `_SC_MEMLOCK`, `RLIMIT_MEMLOCK`, and `MLOCK_MAX`. `stress_mlock_misc` exercises invalid and unusual `mlock`, `munlock`, and `mlockall` calls. `stress_mlock_child` performs the main OOM-contained workload.

Control flow: `stress_mlock` delegates to `stress_oomable_child`. The child sizes and maps a pointer table, synchronizes, then repeatedly maps 3-page regions, tries invalid zero-length locks, locks the middle page, tags successful entries by setting the low bit in the page-aligned pointer, samples `/proc` locked-page counts, and increments bogo operations. It then unlocks tagged pages, tests bogus `munlock`, force-unmaps all regions, maps a second batch of single pages, calls `munlockall`, unmaps them, and repeats until `stress_continue`.

State and persistence behavior: all state is anonymous memory and kernel locked-page accounting. There is no filesystem persistence except optional `/proc` read access. Metrics accumulate nanoseconds per `mlock` and `munlock`; debug output can report max locked pages on Linux.

Dependencies and integration points: this stressor uses `core-madvise`, `core-mmap`, `core-out-of-memory`, memory limit helpers, lock/unlock shims, OOM wrappers, and metrics. It registers as `CLASS_VM | CLASS_OS` with `VERIFY_ALWAYS`; unsupported builds require `_POSIX_MEMLOCK_RANGE` and `HAVE_MLOCK`.

Risks: `RLIMIT_MEMLOCK`, capabilities, cgroup limits, and OOM pressure make `EAGAIN`, `EPERM`, and `ENOMEM` normal. The low-bit tagging scheme relies on page-aligned mmap pointers. `mlockall(MCL_FUTURE)` can affect later allocations if not followed by `munlockall`, so cleanup sequencing matters. Sampling `/proc/self/status` is Linux-specific and debug-only.

Test signals: run `stress-ng --mlock 1 --mlock-ops 1 --verify`, with and without `--oom-avoid`, and under small `RLIMIT_MEMLOCK`. Metrics should include nanoseconds per mlock call and, when unlocks occurred, nanoseconds per munlock call.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mlockmany.c -->
# sources/test-tools/stress-ng/stress-mlockmany.c

Purpose: `stress-mlockmany.c` stresses page locking by repeatedly forking many child processes that each mmap, touch, mlock/munlock, and then are killed/reaped. It is classified pathological because it can create many processes and pressure locked-memory and swap accounting.

Important APIs/types/functions: `stress_mlock_interruptible` and `stress_munlock_interruptible` lock/unlock in 16-page chunks while respecting `stress_continue(args)` and memory-low checks. `stress_mlockmany_child` is the OOM-contained main workload; `stress_mlockmany` wraps it with `stress_oomable_child`. The option `--mlockmany-procs` controls process fan-out with defaults based on stressor instances.

Control flow: the child drops capabilities to make OOM behavior more likely, derives process count, mmaps a shared PID array, gets `RLIMIT_MEMLOCK` or fallback lock size, synchronizes, then loops. For each cycle it initializes PID slots, tracks memory and swap limits, forks children until requested count, swap use, time, or failure stops it. Each forked child installs parent-death behavior, tries invalid `mlockall(0)`, calls `munlockall`, scales down mmap/lock sizes until successful, touches/advises pages, alternates munlock/mlock, tries zero and oversized lock/unlock calls, sleeps briefly, then exits when asked. Parent kills and waits for all children each cycle.

State and persistence behavior: state is transient process state, anonymous mappings, kernel locked-memory accounting, and shared PID mappings. No files are created. Swap free counters are used as a safety signal to stop forking if swap begins to be consumed.

Dependencies and integration points: the file depends on fork/wait, killpid helpers, capability dropping, madvise/mincore helpers, memory limit helpers, OOM adjustment, and `mlock` shims. It registers `stress_mlockmany_info` as `CLASS_VM | CLASS_OS | CLASS_PATHOLOGICAL`; missing `mlock` builds register unimplemented.

Risks: large `--mlockmany-procs` values can overwhelm process tables, scheduler, and memory lock limits; defaults scale by instance count but still may be high. Parent cleanup must kill and reap children reliably. Swap detection is heuristic and depends on `stress_memory_limits_get`. Dropping capabilities changes child behavior and should remain child-scoped.

Test signals: run `stress-ng --mlockmany 1 --mlockmany-ops 1 --mlockmany-procs 2`, then a default run on a safe test host. Check that children are reaped, no live child processes remain, and the unimplemented path compiles when `HAVE_MLOCK` is absent.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mlockmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmap.c -->
# sources/test-tools/stress-ng/stress-mmap.c

Purpose: `stress-mmap.c` is the broad `mmap`/`munmap` VM stressor. It exercises anonymous and file-backed mappings, optional `mmap2`, random mmap flags, `mprotect`, `madvise`, mergeable pages, mlock, NUMA placement, sync modes, fixed remapping, invalid mmap/munmap calls, and write-check verification.

Important APIs/types/functions: `stress_mmap_context_t` carries all option state, fd, mmap function pointer, mapping flags, generated protection/flag permutations, and NUMA masks. `stress_mmap_stressful` enables a bundle of expensive options. `mmap2_try` uses the Linux `__NR_mmap2` syscall for 4 KiB-aligned offsets and falls back to `mmap`. `stress_mmap_mprotect`, `stress_mmap_invalid`, `stress_mmap_index_shuffle`, `stress_mmap_fast_munmap`, `stress_mmap_slow_munmap`, and `stress_mmap_child` implement the workload.

Control flow: the parent initializes defaults, reads options, creates flag/protection permutation arrays, prepares an optional temp file and shared mapping fd, allocates optional NUMA masks, synchronizes, then runs `stress_oomable_child`. The child allocates bookkeeping arrays for page mapped status, page addresses, and shuffled indices. Each iteration maps the full region with random extra flags and address hints, handles SIGBUS via sigsetjmp, optionally touches/syncs file-backed memory, applies madvise/NUMA/mergeable/mlock/mprotect, records page addresses, write-checks data, optionally writes/reads through the fd, shuffles pages for page-level advice/protection, unmaps quickly or slowly, remaps pages at fixed addresses where supported, tests invalid unmaps and invalid mmap combinations, tries random protection and flag permutations, and exercises write-only-to-read-only and read-only-to-write-only transitions.

State and persistence behavior: anonymous state is in child mappings. File-backed mode creates a temp directory and unlinked temp file fd that is closed and removed on exit. Context and permutation arrays live in parent memory and are freed after child completion. SIGBUS jump state is static and reset after the loop.

Dependencies and integration points: the file uses core arch, mmap, mincore, madvise, NUMA, OOM, stress mmap light write/check helpers, filesystem temp helpers, metrics via bogo counts, and stressor option registration. It registers `CLASS_VM | CLASS_OS`, `VERIFY_OPTIONAL`, and falls back to unimplemented when `siglongjmp` is unavailable.

Risks: this stressor intentionally combines invalid flags and edge-case mappings, so errno portability is broad. Hugepage-related SIGBUS is expected in some container environments and must remain recoverable. `MAP_FIXED`/`MAP_FIXED_NOREPLACE` can clobber mappings if address checks regress. File-backed mode must keep the fd sized correctly and clean temp dirs. Flag permutation generation can create invalid combinations; failures should remain nonfatal probes.

Test signals: run `stress-ng --mmap 1 --mmap-ops 1 --verify`, `--mmap-file --mmap-write-check`, `--mmap-mprotect`, `--mmap-slow-munmap`, and `--mmap-stressful` on a disposable host. Check no temp dirs remain, write-check failures are reported only under data corruption, and SIGBUS recovery does not terminate the whole run.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapaddr.c -->
# sources/test-tools/stress-ng/stress-mmapaddr.c

Purpose: `stress-mmapaddr.c` stresses mapping at randomly chosen virtual addresses. It searches for apparently unmapped addresses using `mincore`, maps pages with random fixed/locked/populated options, validates residency, remaps or maps again, and tests `MAP_FIXED_NOREPLACE`.

Important APIs/types/functions: `page_fault` and `stress_fault_handler` detect unexpected SIGSEGV on mapped-page reads. `stress_mmapaddr_check` reads the page and verifies `mincore` residency. `stress_mmapaddr_get_addr` repeatedly samples page-aligned addresses under either 32-bit or full pointer masks until `mincore` reports `ENOMEM`, meaning unmapped. `stress_mmapaddr_child` owns the OOM-contained loop.

Control flow: `stress_mmapaddr` installs a SIGSEGV handler and runs `stress_oomable_child`. The child reads `--mmapaddr-mlock`, synchronizes, then repeatedly chooses a random address mask, finds an unmapped address, builds mmap flags, checks OOM avoidance, maps one read-only page at or near the address, applies mergeable advice and optional mlock, checks it, optionally maps/remaps another page, uses `mremap(MREMAP_FIXED | MREMAP_MAYMOVE)` to move the original page to a fresh address when supported, attempts a `MAP_FIXED_NOREPLACE` mapping over an existing address to force failure, unmaps, and increments bogo operations.

State and persistence behavior: all state is anonymous memory and the process-local `page_fault` flag. No files are created. The stressor expects transient mappings and force-unmaps all successful pages.

Dependencies and integration points: the file uses core madvise, mmap, OOM helpers, `shim_mincore`, optional `mremap`, `MAP_32BIT`, `MAP_FIXED_NOREPLACE`, and `mlock`. It registers `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, and the `--mmapaddr-mlock` option.

Risks: address-space layout and kernel overcommit policies can make random address sampling noisy. `mincore` may be unavailable (`ENOSYS`), causing the loop to stop. A global SIGSEGV handler can mask unexpected faults if not scoped carefully. Fixed mappings are inherently risky, but the file checks occupancy before use.

Test signals: run `stress-ng --mmapaddr 1 --mmapaddr-ops 1 --verify`, repeat with `--mmapaddr-mlock`, and test on systems with/without `MAP_FIXED_NOREPLACE` and `mremap`. Unexpected SIGSEGV or failed `mincore` on a mapped page should fail verification.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapaddr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapcow.c -->
# sources/test-tools/stress-ng/stress-mmapcow.c

Purpose: `stress-mmapcow.c` stresses copy-on-write and page unmapping behavior. It maps shared anonymous buffers of increasing size, dirties pages to force faults/COW-like costs, unmaps pages in multiple patterns, optionally forks to increase copying pressure, and can apply `MADV_FREE`, mlock-on-fault, and NUMA placement.

Important APIs/types/functions: option flags `MMAPCOW_FORK`, `MMAPCOW_FREE`, `MMAPCOW_MLOCK`, and `MMAPCOW_NUMA` control behavior. `stress_mmapcow_force_unmap` tries `MADV_DONTNEED`/`MADV_FREE` before unmapping the whole buffer after page unmap failures. `stress_mmapcow_modify_unmap` times the first write/page fault, fills a page, flushes cache data, optionally advises free, and unmaps the page. `stress_mmapcow_exercise` selects one of eight access/unmap patterns. `stress_mmapcow_child` loops and records metrics.

Control flow: `stress_mmapcow` reads options, enables only supported flags, allocates NUMA masks when requested, synchronizes, and runs the oomable child. The child starts with one page, calls `stress_mmapcow_exercise`, doubles buffer size after success, backs off after failed sizes, and reports nanoseconds per page modification plus max mmap size. Exercise patterns include forward, even/odd forward, prime stride, reverse, reverse even/odd, random mincore-checked pages, one random populated page then full unmap, and random mergeable/unmergeable advice with sequential unmap. Optional fork runs the same mapping in a child and waits for it.

State and persistence behavior: state is anonymous memory and optional global NUMA masks. No filesystem state is created. Buffer sizing state (`buf_size`, `failed_size`, `failed_count`, `max_buf_size`) persists only in the child loop.

Dependencies and integration points: the stressor depends on `madvise`, mmap, CPU cache flush helpers, NUMA, OOM, prime stride helpers, and metrics. It registers as `CLASS_VM | CLASS_OS` with `VERIFY_NONE`; without madvise it registers unimplemented.

Risks: partial page unmaps can fail under memory pressure because VMA splitting may allocate memory; the force-unmap path is essential. Fork mode multiplies pressure and must avoid running children during low memory. Reverse pointer loops over unsigned-like addresses require careful termination conditions. `VERIFY_NONE` means data correctness is not asserted, only syscall resilience and metrics.

Test signals: run `stress-ng --mmapcow 1 --mmapcow-ops 1`, then options `--mmapcow-free`, `--mmapcow-fork`, `--mmapcow-mlock`, and `--mmapcow-numa` on capable hosts. Debug output should show max mmap size, and no child processes or mappings should remain.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapcow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfiles.c -->
# sources/test-tools/stress-ng/stress-mmapfiles.c

Purpose: `stress-mmapfiles.c` recursively scans common system directories and mmaps many regular files read-only, then unmaps them while collecting mmap/munmap throughput and pages-per-mapping metrics. It can use shared mappings, populate pages, and randomize NUMA placement.

Important APIs/types/functions: `stress_mapping_t` stores an address/length pair. `stress_mmapfile_info_t` is shared between parent and child and contains metrics, option booleans, ENOMEM state, the mappings array, and optional NUMA masks. `stress_mmapfiles_dir` recursively maps files under a path. `stress_mmapfiles_child` drives scanning/unmapping over a fixed directory list.

Control flow: the parent maps shared info, initializes counters/options, allocates NUMA masks if requested, and runs an oomable child. The child allocates up to `MMAP_MAX` mapping slots, synchronizes, then repeatedly scans directories in rotating order (`/lib`, `/lib32`, `/lib64`, `/boot`, `/bin`, `/etc`, `/sbin`, `/usr`, `/var`, `/sys`, `/proc`). Each regular file is opened, sized, checked against OOM avoidance, mmapped read-only with private/shared/populate flags, optionally NUMA-randomized and touched for populate, recorded in the mapping table, and counted. After a scan pass, all recorded mappings are timed through `munmap` or force-unmapped.

State and persistence behavior: no files are created or modified. State is shared anonymous metric data plus a child-private heap mappings array. Mapped files are read-only; system directory traversal state is transient.

Dependencies and integration points: the file uses core mmap, NUMA, OOM, put helpers, directory type shims, memory metrics, and stress-ng metrics. It registers `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, and options for NUMA, populate, and shared mappings.

Risks: scanning `/proc` and `/sys` can encounter dynamic files, zero-length files, disappearing entries, and mapping failures; the code largely skips failures. Mapping huge numbers of files can hit `vm.max_map_count`, fd limits, or ENOMEM. Recursive traversal has no explicit symlink following but depends on directory type shims being accurate. Shared mapping of read-only files may behave differently across special filesystems.

Test signals: run `stress-ng --mmapfiles 1 --mmapfiles-ops 1`, repeat with `--mmapfiles-populate` and `--mmapfiles-shared`, and on NUMA systems with `--mmapfiles-numa`. Metrics should include file mmaps/munmaps per second, pages mmaped/munmapped per second, and pages per mapping.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfiles.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfixed.c -->
# sources/test-tools/stress-ng/stress-mmapfixed.c

Purpose: `stress-mmapfixed.c` stresses fixed-address mappings and fixed remaps across a descending address range. It maps small regions with random flags, verifies addresses are unmapped before use, optionally mlocks and NUMA-randomizes pages, and remaps regions to deterministic and random fixed addresses.

Important APIs/types/functions: `mmapfixed_info_t` carries `--mmapfixed-mlock`, `--mmapfixed-numa`, and optional NUMA masks. `stress_mmapfixed_is_mapped_slow` probes a region with chunked `mincore` calls. `stress_mmapfixed_is_mapped` first tries `msync` and falls back to mincore scanning. `stress_mmapfixed_child` performs fixed mapping/remapping.

Control flow: the parent reads options, allocates NUMA masks when requested, reports expected memory use, then runs an oomable child. The child starts at `MMAP_TOP` (`0x80000000` on 32-bit or `0x8000000000000000` otherwise), synchronizes, and loops. It chooses a 1-7 page size, randomizes flags including shared/private, locked, noreserve, populate, and fixed-noreplace when available, skips already mapped or low-memory regions, maps at the target address, applies NUMA/mlock/madvise, tries `mremap` to a nearby XOR-derived address, then attempts additional random fixed remaps while preserving a stored sentinel value. It force-unmaps and shifts the address down until `MMAP_BOTTOM`, then resets.

State and persistence behavior: all state is anonymous memory. NUMA masks are parent-owned and freed after the child. No filesystem state is created. The main safety state is address occupancy checking before fixed mappings.

Dependencies and integration points: the file uses core mmap, madvise, mincore/msync shims, NUMA, OOM, signal exit handler, and `mremap` when available. It registers as `CLASS_VM | CLASS_OS`, `VERIFY_ALWAYS`, with `--mmapfixed-mlock` and `--mmapfixed-numa`.

Risks: fixed mappings can overwrite existing mappings if occupancy detection is wrong or races with other allocations. `mincore`/`msync` detection is heuristic and can treat errors as unmapped. `mremap` fixed moves vary by kernel and address-space constraints. Sentinel verification catches remap data loss, but many failures are expected and skipped.

Test signals: run `stress-ng --mmapfixed 1 --mmapfixed-ops 1 --verify`, repeat with `--mmapfixed-mlock`, and on NUMA systems `--mmapfixed-numa`. A remap sentinel mismatch should fail; ordinary failed fixed mappings should not.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfixed.c -->
