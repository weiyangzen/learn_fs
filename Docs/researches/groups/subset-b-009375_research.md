# subset-b-009375 research

Grouped research report for stress-ng files under `sources/test-tools/stress-ng`. Each section preserves the source path in the title and is wrapped for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfork.c -->
# sources/test-tools/stress-ng/stress-mmapfork.c

Purpose: implements the `mmapfork` VM/scheduler stressor. It repeatedly forks many short-lived child processes, and each child sizes, maps, advises, touches, and unmaps shared anonymous memory to stress fork-time VM accounting, mmap population, memory advice, and child cleanup.

Important APIs/types/functions: `stress_mmapfork_info` registers options `mmapfork-bytes` and `mmapfork-procs`. `stress_mmapfork()` owns the worker loop, child fan-out, memory sizing via `sysinfo()`, optional `MADV_WIPEONFORK` verification, and SIGSEGV attribution. `stress_segvhandler()` exits with a stage-specific bitmask, `should_terminate()` detects parent death or stop requests, and `notrunc_strlcat()` builds a bounded debug reason string.

Control flow: the parent initializes optional wipe-on-fork test memory, synchronizes, then loops creating up to the configured child count. Each child installs failure/scheduler settings, checks `sysinfo()`, derives its per-child mapping length from free RAM, instances, and process count, then runs `stress_mmap_populate()`, optional `MADV_WILLNEED`, `memset`, optional `MADV_DONTNEED`, and `stress_munmap_force()`. The parent waits for children, kills leftovers on interruption, increments bogo operations, and reports any stage-specific SIGSEGV exits.

State and persistence: persistent state is limited to the optional wipe-on-fork page, child PID array, and static `segv_ret`. No filesystem state is created. Child mappings are anonymous and forcibly unmapped or released at exit.

Dependencies and integration: requires `sysinfo()` support; uses stress-ng process state, synchronization, kill/wait helpers, scheduler application, parent-death alarm, mmap helpers, settings, and memory usage reporting.

Risks and test signals: high process fan-out and memory pressure can trigger fork or mmap resource exhaustion. Correct behavior is child reaping without leaks, optional `MADV_WIPEONFORK` verification, bogo increments, and debug-only SIGSEGV stage counts rather than hard failure for expected pressure paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapfork.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaphuge.c -->
# sources/test-tools/stress-ng/stress-mmaphuge.c

Purpose: implements the `mmaphuge` VM stressor. It tries large anonymous and optional file-backed mappings with explicit huge-page flags and transparent huge-page-friendly sizes, touches and validates sparse strides, and then unmaps whole or partial huge mappings.

Important APIs/types/functions: `stress_mmaphuge_context_t` holds mapping descriptors, options, file descriptor, NUMA masks, and mmap stats. `stress_mmaphuge_setting_t` enumerates `MAP_HUGETLB`, huge-size encodings, and THP fallback sizes. `stress_mmaphuge_child()` performs mapping/touching/unmapping; `stress_mmaphuge()` prepares shared context, optional backing file, NUMA settings, OOM wrapper, metrics, and cleanup.

Control flow: setup allocates shared context plus the buffer descriptor array, optionally creates an unlinked 16 MiB temp file with `fallocate()`, and resolves `mmaphuge-mmaps`, `mmaphuge-file`, `mmaphuge-mlock`, and `mmaphuge-numa`. The child cycles through mapping settings, attempting file-backed maps before anonymous maps, checks low-memory conditions, writes and verifies sparse 64-page strides, optionally randomizes NUMA placement and mlocks mappings, toggles THP advice, gathers mmap stats, then tries partial end-page/start-range unmaps before force-unmapping the whole range if needed.

State and persistence: shared state is the context and accumulated `stress_mmap_stats_t`; filesystem state is an unlinked temporary file and temp directory removed at exit. Huge mappings are transient and are explicitly unmapped.

Dependencies and integration: gated by `MAP_HUGETLB`; integrates core mmap stats, NUMA helpers, OOM child execution, temp-file helpers, mlock, madvise, memory usage reporting, and stressor metrics.

Risks and test signals: huge-page availability is host-configuration-dependent, partial unmaps may fail on true huge pages, and file-backed huge maps can fail by filesystem/kernel policy. Useful signals are graceful skips on unsupported builds/resources, verified sparse contents, nonzero bogo operations, mmap stats reports, and cleanup of file descriptors/directories.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaphuge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapmany.c -->
# sources/test-tools/stress-ng/stress-mmapmany.c

Purpose: implements `mmapmany`, a VM stressor that creates as many small mappings as allowed, punches a hole in the middle page of each mapping, traverses proc map files, verifies surviving pages, and tears everything down.

Important APIs/types/functions: `stress_mmapmany_child()` is the OOM-wrapped worker. It uses `sysconf(_SC_MAPPED_FILES)` capped by `MMAP_MAX`, optional `mmapmany-mlock`, optional `mmapmany-numa`, and Linux-only `stress_mmapmany_read_proc_file()` to read `/proc/self/smaps` and `/proc/self/maps`.

Control flow: the child allocates a pointer table, optionally allocates NUMA masks, reports memory usage, synchronizes, then repeatedly maps three pages at a time. It optionally NUMA-randomizes and mlocks the mapping, writes two page-separated patterns, unmaps the middle page, and records the mapping. After the mapping phase it reads proc map files, verifies the first and third pages still contain the expected values, and force-unmaps all three page positions.

State and persistence: only the heap mapping table and optional NUMA masks persist within the process. No filesystem state is created. All mappings are anonymous and are cleaned at the end of each iteration.

Dependencies and integration: uses core mmap, NUMA, out-of-memory wrapper, memory usage reporting, bogo counters, and optional Linux proc interfaces.

Risks and test signals: the stressor can exhaust VMA counts, locked-memory limits, or memory. Verification catches accidental corruption of pages adjacent to an unmapped hole. Expected signals are resource skips under OOM, successful proc traversal, bogo increments per middle-page unmap, and no stale mappings after cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmapmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaprandom.c -->
# sources/test-tools/stress-ng/stress-mmaprandom.c

Purpose: implements `mmaprandom`, a broad VM stressor that randomly creates, mutates, queries, splits, joins, seals, forks, clones, and unmaps memory mappings. It exercises anonymous maps, file maps, memfd, `/dev/zero`, POSIX/System V shared memory, advice, protection, syncing, NUMA movement, and proc-map queries.

Important APIs/types/functions: `mr_node_t` describes each live/free mapping; `mr_ctxt_t` stores worker context, file descriptors, counters, page buffer, NUMA state, and pidfd. BSD red-black trees track used nodes by address, randomly selected nodes by generated `rand_id`, and free nodes by descriptor address. Operation dispatch is defined by `mr_funcs[]`, including `stress_mmaprandom_mmap_anon()`, `stress_mmaprandom_mmap_file()`, `stress_mmaprandom_munmap()`, shared-memory allocators, read/write/cache paths, `mremap`, `remap_file_pages`, `madvise`, `posix_madvise`, `mincore`, `msync`, `mlock`, `mprotect`, page split/join operations, clone/fork, NUMA movement, `process_madvise`, and proc info reads.

Control flow: `stress_mmaprandom()` allocates shared context, a shared I/O page, per-operation counters, a temporary file, memfd, `/dev/zero`, and a shared node array initialized into the free tree. It then repeatedly runs `stress_oomable_child()`. The child installs SIGSEGV/SIGBUS exit handlers, opens a pidfd, picks random operation functions until stop, increments bogo operations, and finally force-unmaps every tracked mapping. The parent reseeds between child runs and emits per-operation rates.

State and persistence: state is mostly shared anonymous mappings for context/counters/nodes plus temporary file descriptors. The temp file and POSIX shared-memory names are unlinked early. Mapping descriptors are recycled between free/used trees; child exit and explicit cleanup release mappings.

Dependencies and integration: requires BSD red-black tree macros; optionally uses Linux mempolicy, `process_madvise`, `mseal`, `clone`, `mremap`, `remap_file_pages`, System V/POSIX shm, procmap ioctl, file rw hints, cache flush, and many stress-ng mmap/madvise/NUMA helpers.

Risks and test signals: this intentionally explores kernel edge cases and invalid calls, so platform variation is expected. Key risks are stale tree entries after partial unmaps, file-backed expansion without backing store, unsafe operations on shared-memory mappings, and signal-prone protections. Signals are per-operation metrics, no child crashes outside handled SIGSEGV/SIGBUS paths, cleanup of all tracked mappings, and graceful unimplemented status when RB trees are unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaprandom.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaptorture.c -->
# sources/test-tools/stress-ng/stress-mmaptorture.c

Purpose: implements `mmaptorture`, a VM stressor that performs aggressive file-backed, anonymous, and POSIX shared-memory mapping churn with random offsets, sizes, advice, sync, protection changes, locking, remapping, forked cleanup, and signal recovery.

Important APIs/types/functions: `mmap_info_t` records active mappings, and `mmap_stats_t` accumulates page-level counters. Global `mmap_fd`, `mmap_data`, `mmap_bytes`, and shared `mmap_stats` support init/deinit and child execution. `stress_mmaptorture_init()` creates and maps the backing file, `stress_mmaptorture_child()` performs the torture loop, `stress_mmaptorture_sighandler()` recovers from SIGBUS/SIGSEGV via `siglongjmp`, and `stress_mmaptorture_msync()` probabilistically syncs pages.

Control flow: init sizes the backing file per instance, creates an unlinked temp file, truncates it, and maps the whole region. The child allocates scratch buffers and mapping slots, installs signal handlers, then repeatedly truncates/restores the backing file, writes through the primary map, optionally remaps file pages, creates up to 128 secondary mappings, applies random `fallocate`/hole-punch, file/SHM/anonymous mapping choices, VMA names, prefetch, NUMA movement, madvise, mincore, mlock, mprotect, msync, fixed-address negative tests, and occasional early unmaps. It may fork a child that mlockalls, drops advice, seals one mapping, and unmaps inherited mappings. Cleanup remaps smaller via `mremap`, resets advice/protection, unlocks, optionally removes pages, and advances backing-file offsets.

State and persistence: persistent state includes the unlinked temp file, global primary mapping, and shared stats until deinit. Secondary mappings and POSIX shm names are transient. Stats are reported as rates for mapped, synced, locked, protected, advised, remapped, retry, SIGBUS, and SIGSEGV pages.

Dependencies and integration: requires `siglongjmp`; optionally uses POSIX shm, `remap_file_pages`, `mremap`, NUMA, mlockall, mseal, fallocate hole punching, mincore, VMA naming, OOM wrapper, and stress-ng temp-file lifecycle.

Risks and test signals: the stressor intentionally triggers SIGBUS/SIGSEGV-prone races with truncated files and changing protections. Useful signals are recovered traps, page-rate metrics, absence of leaked child processes, cleanup of temporary directories, and graceful skip when initial mapping or signal support is unavailable.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mmaptorture.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-module.c -->
# sources/test-tools/stress-ng/stress-module.c

Purpose: implements the privileged `module` OS stressor. It repeatedly loads a kernel module with `finit_module()` and optionally unloads it with `delete_module()`, stressing kernel module loading paths and module metadata validation flags.

Important APIs/types/functions: `stress_module_supported()` requires `CAP_SYS_MODULE`. `get_modpath_name()` parses `/lib/modules/$(uname -r)/modules.dep` for either a user-selected `module-name` or default kernel self-test modules. `stress_module_open()` opens `.ko` files directly or decompresses `.ko.xz` through liblzma into an unlinked temp file. `stress_module()` handles options `module-no-unload`, `module-no-modver`, and `module-no-vermag`, validates the module fd with `fstat()`, and loops on `shim_finit_module()`.

Control flow: the stressor creates a temp directory, resolves module path/type, opens or decompresses the module, validates that it is a regular file, optionally removes any preloaded instance, synchronizes, then repeatedly calls `finit_module()` with requested kernel flags and unloads after successful loads unless disabled. Cleanup closes the module fd and removes the temp directory.

State and persistence: this mutates kernel module state. With default behavior it unloads after each successful load and attempts an initial unload; with `module-no-unload`, loaded module state may persist intentionally. Temporary decompression files are unlinked.

Dependencies and integration: Linux-only; depends on `linux/module.h`, `uname`, `modules.dep`, optional liblzma, capability helpers, core module syscall shims, temp-file helpers, and stress-ng synchronization.

Risks and test signals: requires powerful privileges and can affect the host kernel. Dependency modules are not resolved like `modprobe`, compressed formats other than `.xz` are skipped, and `module-no-unload` can leave state behind. Signals are capability skip, module path discovery, successful load bogo increments, and clean unload/close behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-monte-carlo.c -->
# sources/test-tools/stress-ng/stress-monte-carlo.c

Purpose: implements `monte-carlo`, a CPU/compute stressor that estimates mathematical constants and integrals using configurable random number generators and sample counts.

Important APIs/types/functions: `stress_monte_carlo_rand_info_t` maps RNG names to `rand`, `seed`, and `supported` functions. RNGs include MWC32/MWC64, LCG, PCG32, xorshift, and optional arc4random, getrandom, drand48, random, PPC DARN, and x86 RDRAND. `stress_monte_carlo_method_t` maps methods for `pi`, `e`, `exp`, `sin`, `sqrt`, and `squircle` to expected values. `stress_monte_carlo_by_method()` and `stress_monte_carlo_by_rand()` expand `all` selections and accumulate metrics/results.

Control flow: the stressor detects supported RNGs, initializes metrics/result matrices, reads options `monte-carlo-method`, `monte-carlo-rand`, and `monte-carlo-samples`, synchronizes, then repeatedly runs selected method/RNG combinations. Each method processes samples in bounded 16K chunks and exits early on global stop. On deinit it emits samples/sec metrics per method/RNG and debug comparisons of averages versus expected values.

State and persistence: RNG state is static for LCG, PCG32, xorshift, getrandom buffer index, and stress-ng MWC seeds. Metrics and result accumulators are stack-local. No external state is changed.

Dependencies and integration: uses libm wrappers, architecture RNG helpers, `getrandom`, option method enumeration, stress-ng metrics, bogo counters, and process synchronization.

Risks and test signals: estimates are stochastic and not verification failures; small sample counts can be inaccurate. RNG support varies by architecture and libc. Test signals are method/RNG option enumeration, nonzero samples/sec metrics, debug result summaries, and no divide-by-zero when stop occurs after partial sample processing.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-monte-carlo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mpfr.c -->
# sources/test-tools/stress-ng/stress-mpfr.c

Purpose: implements `mpfr`, a CPU/floating-point stressor for GMP/MPFR multi-precision arithmetic. It computes several constants and functions at configurable precision and verifies deterministic repeatability.

Important APIs/types/functions: `stress_mpfr_method_t` maps method names to functions. Implemented computations include Apéry's constant, cosine and sine sums, Euler's number, exponent/log sums, binary-search square root, Omega constant, and golden ratio. `stress_mpfr()` configures precision, runs each method twice from the same MWC seed, compares `mpfr_t` results, and reports per-method rates.

Control flow: after choosing `mpfr-precision` with minimize/maximize support, the stressor initializes two result variables, synchronizes, then loops through all methods while running. For each method it snapshots RNG seeds, computes into `r0`, restores seeds, computes into `r1`, increments bogo operations for each computation, and fails if `mpfr_cmp()` differs. Deinit clears MPFR variables/caches and emits metrics.

State and persistence: MPFR temporaries are local to each method and cleared before return; `mpfr_free_cache()` is called frequently and at deinit. Static metrics are reset per run. No external state is created.

Dependencies and integration: requires `gmp.h`, `mpfr.h`, and libmpfr. Uses stress-ng settings, RNG seed controls, timing, metrics, synchronization, and verification.

Risks and test signals: high precision can be CPU and memory intensive. The deterministic comparison relies on resetting stress-ng RNG seeds around methods that use randomness. Useful signals are no inconsistency failures, nonzero per-method computation rates, correct unimplemented path without MPFR/GMP, and cache cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mpfr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mprotect.c -->
# sources/test-tools/stress-ng/stress-mprotect.c

Purpose: implements `mprotect`, a VM/OS stressor that changes protection masks over shared pages from multiple processes and verifies that disallowed reads/writes fault rather than silently succeeding.

Important APIs/types/functions: `stress_mprotect_flags_t` names protection bits for diagnostics. `stress_flag_permutation()` generates all protection flag combinations from available `PROT_*` bits except exec. `stress_mprotect_mem()` installs SIGSEGV/SIGBUS handlers, randomly chooses pages/ranges, calls `mprotect()`, then probes read/write behavior. `stress_mprotect()` allocates shared memory, forks worker children, synchronizes them, and reaps them.

Control flow: the parent allocates a shared PID array and a small shared mapping, marks it mergeable, enables OOM killability, then forks up to seven child workers. Parent and children wait on stress-ng synchronization and run `stress_mprotect_mem()` concurrently against the same shared mapping. The loop randomly selects ranges at least one page long, tries up to ten protection combinations, increments bogo on successful changes, and uses signal recovery for expected protection faults. Parent kills/waits children and frees shared resources.

State and persistence: state is the shared mapping, generated protection flag array, and shared PID list. No filesystem state exists. Signal jump buffer is static per process.

Dependencies and integration: gated by `HAVE_MPROTECT`; uses stress-ng sync PID helpers, kill helpers, madvise mergeable, OOM adjustment, flag permutation, signal helpers, and optional `PROT_SEM`, `PROT_SAO`, growth flags.

Risks and test signals: concurrent protection changes can create timing-dependent faults, and some protection flags are platform-specific. Test signals are bogo increments, absence of unexpected readable/writable pages under disallowed flags, correct child cleanup, and unimplemented status without `mprotect()`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mprotect.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mq.c -->
# sources/test-tools/stress-ng/stress-mq.c

Purpose: implements `mq`, a POSIX message queue IPC stressor. It creates one queue, forks sender/receiver roles, exercises normal and timed send/receive paths, queue attributes, notification registration, and many invalid-call cases.

Important APIs/types/functions: `stress_msg_t` is the queue payload. `stress_mq_invalid_open()` probes invalid `mq_open()` attributes and cleans up if they unexpectedly succeed. `stress_mq()` owns queue sizing, creation, fork, parent sender loop, child receiver loop, verification, and cleanup. Optional Linux paths exercise `lseek`, `fstat`, invalid `mmap`, `poll`, and direct `read` on queue descriptors.

Control flow: setup determines `mq-size`, clamps it against `/proc/sys/fs/mqueue/msg_default` when available, retries smaller sizes on open failure, and computes an absolute timeout for timed operations. The receiver child optionally registers varied `mq_notify()` events, probes invalid opens/unlinks/descriptors, then alternates `mq_receive()` and `mq_timedreceive()` while validating priorities and optional per-priority message ordering. The parent periodically gets/sets attributes, sends messages with random priorities via `mq_send()` or `mq_timedsend()`, probes invalid descriptors/sizes/priorities, increments bogo operations, then kills the child and unlinks the queue.

State and persistence: the POSIX queue persists by name until explicitly unlinked; the stressor unlinks it at cleanup and removes any temporary invalid-open queue names. Parent/child verification counters are in process memory.

Dependencies and integration: requires `mqueue.h`, librt, and POSIX MQ support; uses affinity, fork retry, kill wait, scheduler settings, signal ignore, stress-ng settings and verification flags.

Risks and test signals: host MQ limits can cause resource skips, and timed calls depend on clock availability. Useful signals are successful queue create/unlink, bogo increments, optional ordered payload verification, expected skips for ENOSYS/ENOSPC, and no leaked queue names.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mremap.c -->
# sources/test-tools/stress-ng/stress-mremap.c

Purpose: implements `mremap`, a VM stressor that repeatedly shrinks and expands anonymous mappings, optionally moving them to fixed addresses, locking pages, randomizing NUMA placement, and verifying retained page contents.

Important APIs/types/functions: `rand_mremap_addr()` reserves and frees a random destination for `MREMAP_FIXED`. `try_remap()` wraps `mremap()` retry logic, timing metrics, optional `MREMAP_DONTUNMAP`, and optional mlock. `stress_mremap_child()` handles allocation, shrink/expand loops, advice, mincore touching, verification, invalid remap calls, and metrics. `stress_mremap()` runs the child under the OOM wrapper.

Control flow: the child computes per-instance `mremap-bytes`, enables optional `MAP_POPULATE`, resolves `mremap-mlock` and `mremap-numa`, then synchronizes. Each iteration maps the current maximum size, optionally NUMA-randomizes, applies random/mergeable advice, touches pages, verifies initial patterns, repeatedly halves the mapping down to one page, then doubles it back toward the target size. It tests invalid flags, invalid fixed destination, and zero new size before force-unmapping.

State and persistence: all state is process-local anonymous memory plus optional NUMA masks and accumulated timing/count metrics. No filesystem state is created.

Dependencies and integration: requires `mremap()` and glibc 2.4-compatible support; optionally uses `MREMAP_FIXED`, `MREMAP_DONTUNMAP`, mlock, NUMA helpers, mincore, madvise helpers, OOM wrapper, memory usage reporting, and verification flags.

Risks and test signals: address-space fragmentation and low memory can cause retries; `MREMAP_FIXED` support varies. Verification detects data loss across remaps. Signals are nanoseconds-per-call metrics, bogo increments per full shrink/expand cycle, no leaked mapping on stop, and graceful unimplemented/resource handling.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mremap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mseal.c -->
# sources/test-tools/stress-ng/stress-mseal.c

Purpose: implements `mseal`, a VM/OS stressor for Linux memory sealing. It verifies that sealed mappings reject operations that would alter, unmap, or replace them, while repeated sealing of mapped ranges succeeds.

Important APIs/types/functions: global `mapping`, `mapping_size`, and `no_mapping` provide the sealed range and an unmapped address range. `stress_mseal_supported()` probes `shim_mseal()` support before registration. Expectation helpers compare return values and errno. `mseal_funcs[]` dispatches negative tests for `madvise(MADV_DONTNEED)`, `mremap` resize/move, `munmap`, `mprotect`, fixed `mmap`, sealing unmapped pages, and positive tests for sealing first, last, and all mapped pages.

Control flow: support probing maps two pages read-only and seals them. Runtime ensures a mapping exists, creates and unmaps another two-page range to use as a known hole, synchronizes, then repeatedly runs all test functions. Positive `mseal()` calls are timed and counted; any unexpected result stops the loop. Deinit reports calls/sec and attempts to unmap the sealed mapping, ignoring the expected failure.

State and persistence: static globals persist during the stressor instance. Sealed memory may intentionally resist cleanup until process exit. No filesystem state is created.

Dependencies and integration: uses `core-shim` for `shim_mseal`, mmap helpers, optional madvise/mremap/mprotect/fixed mmap support, stress-ng supported callback, metrics, and synchronization.

Risks and test signals: the syscall is kernel-version dependent and has strict errno expectations. If the semantics change, tests may fail despite system correctness. Signals are support skip on `ENOSYS`, EPERM/ENOMEM matches for protected operations, successful repeated sealing of mapped pages, and nonzero mseal rate metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mseal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msg.c -->
# sources/test-tools/stress-ng/stress-msg.c

Purpose: implements `msg`, a System V message queue IPC stressor. It creates one active queue plus additional resource-pressure queues, sends and receives messages between parent and child, verifies FIFO ordering when possible, and exercises `msgctl`, `msgget`, `msgsnd`, and `msgrcv` edge cases.

Important APIs/types/functions: `stress_msg_t` contains `mtype` and a value/data payload. `stress_msg_get_stats()` exercises `IPC_STAT`, `IPC_SET`, `MSG_STAT_ANY`, `IPC_INFO`, `MSG_INFO`, and invalid `msgctl()` calls. `stress_msgget()` and `stress_msgsnd()` probe unusual invalid arguments. `stress_msg_receiver()` consumes messages with optional type filtering and verification; `stress_msg_sender()` produces messages, periodically reads stats and `/proc/sysvipc/msg`; `stress_msg()` owns queue lifecycle.

Control flow: setup reads `msg-types` and `msg-bytes`, allocates an array for extra queue IDs, creates the main private queue, probes unusual `msgget()` calls, and allocates more queues up to a per-instance cap. After synchronization it forks a receiver pinned near the parent CPU. The sender loop chooses message type, sends with occasional `IPC_NOWAIT`, handles full queues by retrying blocking, increments bogo, and periodically gathers stats. The receiver loops on `msgrcv()`, optionally peeks with `MSG_COPY`, retries expected empty/again errors, and verifies monotonically increasing payloads only when type filtering is disabled. Cleanup kills the child and removes all queues.

State and persistence: System V queues persist in the kernel until `IPC_RMID`; the stressor removes the main and extra queues on all cleanup paths. Per-process counters hold verification state.

Dependencies and integration: requires SysV IPC headers and message queue support; uses affinity, fork retry, kill/wait helpers, scheduler settings, proc reading on Linux, stress-ng settings, bogo counters, and `VERIFY_ALWAYS`.

Risks and test signals: queue limits can produce resource exits, typed receives break FIFO verification by design, and forgotten `IPC_RMID` would leak kernel IPC objects. Signals are created/deleted queue debug logs, ordered verification with `msg-types=0`, exercised stats paths, and cleanup of every allocated queue ID.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msync.c -->
# sources/test-tools/stress-ng/stress-msync.c

Purpose: implements `msync`, a VM/filesystem stressor that checks synchronization between a shared file mapping and its backing file in both writeback and invalidate directions, while also exercising invalid `msync()` calls.

Important APIs/types/functions: `stress_page_check()` verifies a page is filled with an expected byte pattern. `stress_sigbus_handler()` counts SIGBUS and returns through `siglongjmp`. `stress_msync()` sizes the mapped file, creates an unlinked temp file, maps it shared, maps a scratch read buffer, runs MS_SYNC/MS_INVALIDATE checks, and handles cleanup.

Control flow: setup installs SIGBUS recovery, resolves `msync-bytes`, creates a temp file, truncates it, maps the full region shared, and maps a one-page anonymous read buffer. Each loop picks a page-aligned offset, writes a random byte pattern in memory, calls `MS_SYNC`, reads the file, and verifies persisted data. It then writes another pattern, reads file data, calls `MS_INVALIDATE`, and verifies memory contents. It also probes invalid flag combinations, wrap-around addresses, zero-length no-op, and locked-page invalidate behavior.

State and persistence: filesystem state is an unlinked temp file and temp directory removed at exit. Static SIGBUS count persists for the process and is reported. Mappings are explicitly unmapped.

Dependencies and integration: requires `msync()`; uses stress-ng mmap populate, temp-file helpers, OOM adjustment, settings, memory usage reporting, shim msync/mlock/munlock, signal helpers, and verification.

Risks and test signals: filesystem semantics and FreeBSD behavior differ, SIGBUS can occur if backing storage changes, and `MS_INVALIDATE` on locked pages may return EBUSY. Signals are successful page comparisons, bogo increments, reported SIGBUS count if any, and cleanup of fd/mappings/temp directory.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msync.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msyncmany.c -->
# sources/test-tools/stress-ng/stress-msyncmany.c

Purpose: implements `msyncmany`, a VM stressor that maps the same single-page file many times, writes through one mapping, syncs and invalidates it, and verifies all aliases observe the same value.

Important APIs/types/functions: `stress_msyncmany()` creates an unlinked temp file and allocates one page. `stress_msyncmany_child()` maps the file repeatedly up to `_SC_MAPPED_FILES` capped by `MMAP_MAX`, stores mapping pointers, and performs the sync/alias verification loop under OOM handling.

Control flow: the parent creates a temp directory/file, unlinks the file, `fallocate()`s one page, then runs the child through `stress_oomable_child()`. The child allocates a mapping table, creates as many `MAP_SHARED` one-page mappings of fd offset zero as possible, synchronizes, writes a random pattern through the first mapping, calls `msync(MS_SYNC | MS_INVALIDATE)`, verifies every mapping reads the same pattern, and increments bogo operations. Cleanup unmaps all mappings, closes the inherited fd, and frees the table.

State and persistence: persistent state is the unlinked one-page file descriptor and the child mapping table. Temp directory and file descriptor are cleaned by parent and child paths; mappings are transient.

Dependencies and integration: requires `msync()`; uses temp-file helpers, `fallocate`, OOM wrapper, memory-low checks, VMA naming, and stress-ng synchronization.

Risks and test signals: VMA limits or low memory can prevent mappings, and alias coherence bugs show as mismatched patterns. Good signals are nonzero mapping count, successful `MS_SYNC | MS_INVALIDATE`, no more than a few verification failures before abort, and complete unmap/close cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-msyncmany.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mtx.c -->
# sources/test-tools/stress-ng/stress-mtx.c

Purpose: implements `mtx`, an ISO C11 mutex stressor using `threads.h` `mtx_t` operations from multiple pthread-created threads.

Important APIs/types/functions: global `mtx_t mtx` is the contended lock. `pthread_info_t` stores args, pthread handle, creation status, and lock timing/count data. `mtx_exercise()` repeatedly locks/unlocks the C mutex and records occasional timing. `stress_mtx()` configures `mtx-procs`, initializes/destroys the mutex, creates threads, joins them, and reports nanoseconds per lock.

Control flow: after option resolution and `mtx_init(mtx_plain)`, the stressor synchronizes, creates up to the requested number of pthreads, and waits while the global continue flag remains true. Each thread reseeds randomness, sleeps briefly, then loops locking the mutex, incrementing lock count and bogo operations, and unlocking it. Every thousandth lock uses the slower timed path. On stop, the parent joins all created threads, sums durations/counts, destroys the mutex, and emits metrics.

State and persistence: state is in-process only: one global mutex and per-thread info records. No filesystem or kernel IPC state persists beyond pthreads.

Dependencies and integration: requires pthread library, `threads.h`, `mtx_t`, `mtx_init`, and `mtx_destroy`; uses stress-ng pthread helpers, timing, bogo counters, settings, and process state.

Risks and test signals: platform C11 thread support varies, and returning early after no threads are created currently skips `mtx_destroy()`. Useful signals are successful thread creation, no `mtx_lock`/`mtx_unlock` failures, nanoseconds-per-mtx metrics, and unimplemented status on builds without C11 mutex support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mtx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-munmap.c -->
# sources/test-tools/stress-ng/stress-munmap.c

Purpose: implements `munmap`, a Linux VM stressor that parses the child process map list and unmaps eligible file-backed readable non-executable pages in a prime-stride order to create many VMA holes.

Important APIs/types/functions: `munmap_context_t` stores args, page shift, executable path, and timing counters. `stress_munmap_log2()` computes page-size shift, `stress_munmap_stride()` finds a prime stride, `stress_munmap_range()` unmaps pages and checks residency with `mincore`, `stress_munmap_child()` filters `/proc/$pid/maps`, and `stress_munmap()` runs repeated OOMable children.

Control flow: the parent allocates shared context, resolves `/proc/self/exe`, synchronizes, and repeatedly starts `stress_munmap_child()` through `stress_oomable_child()`. The child installs SIGSEGV/SIGBUS exit handlers, opens `/proc/$pid/maps`, optionally marks mappings `MADV_DONTDUMP` and pageout under aggressive mode, rewinds, then filters out anonymous, special, libc, `/dev/zero`, executable, non-readable, stress-ng executable, args, and context ranges. For eligible ranges it unmaps each page using a prime stride and records timing/count metrics.

State and persistence: shared context persists across child runs; child unmaps only its own address space. No filesystem state is modified beyond reading proc files.

Dependencies and integration: Linux-only; uses proc maps parsing, prime helper, mincore, mmap shared context, signal exit handlers, OOM wrapper, proc self exe helper, metrics, and bogo counters.

Risks and test signals: bad filtering can unmap critical libraries or data and crash the child, which is contained by the OOMable child boundary and signal handlers. Signals are successful child iterations, nanoseconds-per-page metrics, bogo increments, and no mincore evidence that unmapped pages remain resident.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-munmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mutex.c -->
# sources/test-tools/stress-ng/stress-mutex.c

Purpose: implements `mutex`, a pthread mutex/scheduler stressor. It creates multiple contending pthreads that repeatedly change scheduling priority, optionally move CPU affinity, lock/unlock a shared mutex, and measure lock latency.

Important APIs/types/functions: global `pthread_mutex_t mutex` is the contended lock. `pthread_info_t` stores priority limits, affinity setting, pthread handle, creation status, and metrics. Optional mutex attributes set `PTHREAD_PRIO_INHERIT` and a priority ceiling. `stress_mutex_exercise()` performs per-thread priority/affinity changes and lock/unlock; `stress_mutex()` handles option parsing, mutex initialization, CPU list setup, thread lifecycle, and metrics.

Control flow: setup installs SIGCHLD handling, reads `mutex-procs` and `mutex-affinity`, obtains SCHED_FIFO priority range, initializes the mutex with priority inheritance when supported, and optionally collects allowed CPUs. After synchronization it creates the requested pthreads. Each thread reseeds, sleeps briefly, repeatedly chooses a FIFO priority, calls `pthread_setschedparam()`, times occasional mutex lock calls, drops priority, optionally changes affinity, yields, increments bogo, and unlocks. On stop, the parent joins threads, destroys the mutex, frees CPU lists, and reports nanoseconds per mutex.

State and persistence: state is in-process pthread/mutex state plus optional CPU list memory. No filesystem or IPC state persists.

Dependencies and integration: requires POSIX priority scheduling, pthread mutex APIs, `pthread_setschedparam`, SCHED_FIFO priority queries, and optional pthread affinity. Uses stress-ng affinity helpers, signal helpers, settings, timing, and metrics.

Risks and test signals: real-time scheduling calls may fail without privileges but are intentionally ignored unless mutex operations fail. Affinity support is nonportable. Signals are successful thread creation, no lock/unlock failures, bogo increments, nanoseconds-per-mutex metrics, and unimplemented status on platforms without required pthread/scheduler support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-mutex.c -->
