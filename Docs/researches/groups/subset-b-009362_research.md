# Research Group subset-b-009362

This grouped report covers the stress-ng core files assigned to `subset-b-009362`. Each section is source-tree-aligned and bounded by the required reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-pthread.h -->
# sources/test-tools/stress-ng/core-pthread.h

Purpose: provides the small pthread-facing portability surface used by stressors that run helper threads or need a low-overhead lock abstraction. It depends on `stress_args_t` and the generated feature macros from `stress-ng.h`.

Important APIs/types/functions: `stress_pthread_args_t` packages a stressor argument pointer, per-thread private data, and a return code. `shim_pthread_spinlock_t` aliases either `pthread_spinlock_t` or `pthread_mutex_t`. The `shim_pthread_spin_*` macros map lock, unlock, init, and destroy operations to the selected primitive, while `SHIM_PTHREAD_PROCESS_SHARED/PRIVATE` track the compatible initializer argument.

Control flow: this is header-only. Compile-time feature checks choose real spinlocks when libpthread and spinlock support are present, excluding platforms called out as problematic, otherwise a mutex-backed implementation is selected.

State and persistence: no owned persistent state. Users own the lock object and any `stress_pthread_args_t` storage.

Dependencies/integration: used by resource allocation and stressors that need pthread wrappers without repeating platform guards. Risk is mostly semantic drift: the mutex fallback does not have spinlock performance or the same process-shared behavior, because the fallback shared/private macros are `NULL`.

Test signals: build matrix coverage across Linux/BSD-like pthread variants, plus stressors that initialize, lock, unlock, and destroy shim locks. Watch for compile failures when pthread feature macros are inconsistent.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-pthread.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-put.h -->
# sources/test-tools/stress-ng/core-put.h

Purpose: exposes tiny inline sinks that write values into global `g_put_val` so optimized stress loops can make computed values observable to the compiler. This prevents whole-loop dead-code elimination without introducing heavy I/O.

Important APIs/types/functions: `g_put_val` is the external sink object. `stress_put_bool`, integer width variants, optional `stress_put_uint128`, floating-point variants, and `stress_put_void_ptr` store the supplied value into the matching union/struct member.

Control flow: every helper is an `ALWAYS_INLINE` single assignment. The only conditional path is `HAVE_INT128_T`, which enables the 128-bit sink when supported.

State and persistence: all functions mutate the process-global `g_put_val`. The value is intentionally overwritten and not accumulated. There is no synchronization, so concurrent writers race by design as a compiler-observability sink rather than a correctness store.

Dependencies/integration: included by hot stressor code and relies on the definition of `stress_put_val_t` elsewhere in stress-ng. It integrates with benchmark loops where returning or printing values would distort the workload.

Risks: strict type matching matters because the helpers directly assign to typed members. Thread sanitizer-style tools may flag benign global data races. If `g_put_val` is removed or made local, optimizer behavior of many stressors can change.

Test signals: optimized builds should still retain loops that call these helpers. Compile with and without `__int128` support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-put.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-rapl.c -->
# sources/test-tools/stress-ng/core-rapl.c

Purpose: discovers Intel RAPL powercap domains on Linux/x86, samples energy counters, converts deltas to watts, and emits per-stressor RAPL summaries.

Important APIs/types/functions: `stress_rapl_domains_get` scans `/sys/class/powercap` for `intel-rapl*` entries with readable `energy_uj`, records sysfs names, display domain names, max energy range, and sorted list indexes. `stress_rapl_domains_free` releases the linked list. `stress_rapl_power_raplstat_get` and `stress_rapl_power_stressor_get` share `stress_rapl_power_get`; the latter copies per-domain values into `stress_rapl_t`. `stress_rapl_dump` prints harmonic-mean watts for each stressor instance set.

Control flow: discovery opens the powercap directory, filters non-RAPL entries, validates energy readability, normalizes package names, rejects duplicate display domains, then inserts domains in sorted order. Sampling reads `energy_uj`, handles zero readings by reusing the previous value, detects wraparound using `max_energy_range_uj`, and only updates power if at least 0.25 seconds elapsed and the computed watts are positive. Dumping iterates stressor list items, skips ignored runs, aggregates instance power readings by domain, and writes both info and YAML output.

State and persistence: per-domain previous energy/time/power is held in the linked list for two consumers: raplstat and per-stressor sampling. Sysfs is read-only; no persistent system configuration is changed.

Dependencies/integration: compiled only under `STRESS_RAPL` from Linux/x86 guards. Uses `stress_time_now`, `stress_capabilities_check`, logging/YAML helpers, and `stress_list_item_t` stats fields.

Risks: sysfs permissions often require root or powercap access. Domain indexing is capped by `STRESS_RAPL_DOMAINS_MAX`; extra domains are silently skipped in per-stressor copies/dumps. Harmonic mean suppresses zero/unavailable samples, so missing samples can bias output.

Test signals: systems with no RAPL, unreadable `energy_uj`, wraparound-capable counters, multi-domain packages, and YAML metrics runs. Mocked sysfs tests should verify duplicate-domain filtering and 0.25 second gating.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-rapl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-rapl.h -->
# sources/test-tools/stress-ng/core-rapl.h

Purpose: declares the RAPL measurement contract for Linux/x86 builds. It isolates RAPL-specific structs and functions behind the `STRESS_RAPL` feature gate.

Important APIs/types/functions: `STRESS_RAPL_DOMAINS_MAX` caps exported per-stressor arrays at 32. `stress_rapl_data_t` stores previous energy, previous sample time, and computed watts. `stress_rapl_domain_t` represents one sysfs powercap domain in a linked list. `stress_rapl_t` is the compact per-stressor stats payload with a read time and domain watts array. Public functions cover domain discovery/free, raplstat sampling, stressor sampling, and YAML/info dumping.

Control flow: no runtime logic in the header; inclusion depends on `__linux__` and `STRESS_ARCH_X86`.

State and persistence: describes mutable in-memory sampling state only. Callers own `stress_rapl_domain_t` list lifetime and embed/copy `stress_rapl_t` in stressor stats.

Dependencies/integration: includes `core-arch.h` and `stress-ng.h`, and uses `FILE` plus `stress_list_item_t` in declarations. It integrates with metrics collection and per-stressor statistics.

Risks: consumers must guard references with `STRESS_RAPL`; otherwise non-x86 or non-Linux builds will not see these types. The fixed domain array means the list can represent more domains than the compact stats object can export.

Test signals: compile both with and without Linux/x86 RAPL support; verify callers keep feature guards around struct fields and functions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-rapl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-resctrl.c -->
# sources/test-tools/stress-ng/core-resctrl.c

Purpose: parses the `--resctrl` option, records cache/bandwidth partitions, mounts or finds the Linux resctrl filesystem when supported, creates partition groups, and assigns stressor PIDs to partitions.

Important APIs/types/functions: `stress_partition_info_t` stores partition name, number, cache level, node, bitmask, and bandwidth. `stress_resctrl_info_t` maps stressor instance ranges to partitions. `stress_resctrl_parse` is the option parser. `stress_resctrl_init` prepares mount/groups. `stress_resctrl_set` applies a matching partition to a stressor instance PID. `stress_resctrl_deinit` removes groups, frees parser state, and unmounts only mounts created by stress-ng.

Control flow: parsing duplicates the option string and mutates delimiters in place. Partition clauses such as `p1=1:l3:fff:20,` are parsed first and stored in a linked list. Stressor clauses resolve names through `stress_stressor_find`, parse instance lists/ranges or `all`, require `@pN`, reject duplicate/overlapping instance ranges, and increment `stress_resctrls_added`. On supported Linux/ARM builds, init searches `/proc/mounts` for an existing resctrl mount; if none exists it creates a temporary mount point and mounts via new mount API or `mount(2)`. It then creates `stress-ng-pN` directories. Applying a PID writes schemata cache masks, memory bandwidth lines, and the PID to `tasks`.

State and persistence: global linked lists hold parsed partitions and per-stressor maps. Supported runs may create directories under an existing resctrl mount or create a temporary mounted filesystem. Deinit attempts to remove created partition directories and unmount/remove the temporary mount point.

Dependencies/integration: depends on `core-setting`, `core-stressors`, filesystem helpers, mount APIs, `stress_fs_temp_path_get`, and generated `STRESSORS` enumeration ordering.

Risks: feature is currently gated to Linux/ARM with mount headers despite the interface being generic. Parser requires partition definitions before references. Cleanup ignores many removal failures, so externally busy resctrl groups may remain. Schemata format assumptions can break on kernel resctrl variants.

Test signals: parser unit cases for partitions, missing delimiters, duplicate ranges, undefined partitions, `all`, and cache-level defaults. Runtime tests need root/capability-controlled resctrl environments and cleanup verification after failed mount/group creation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-resctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-resctrl.h -->
# sources/test-tools/stress-ng/core-resctrl.h

Purpose: declares the public resctrl lifecycle used by option parsing and stressor process startup.

Important APIs/types/functions: `stress_resctrl_parse` parses the raw option string and returns failure for invalid syntax. `stress_resctrl_set` assigns a stressor name/instance/PID to its configured partition. `stress_resctrl_init` prepares the resctrl filesystem state after parsing. `stress_resctrl_deinit` tears it down and frees parser state.

Control flow: the header itself has no logic. The parse/init/set/deinit sequence is the intended lifecycle; calling `set` before parse/init is harmless in unsupported/no-config builds but cannot apply partitions.

State and persistence: all state is private to the implementation. External callers only pass the option string and per-process identity.

Dependencies/integration: relies on stress-ng-wide definitions for `uint32_t`, `pid_t`, and `WARN_UNUSED`. Integrated by main option handling and child stressor startup.

Risks: callers must not assume resctrl is available just because parsing succeeded; unsupported builds accept calls but log that settings are ignored. The option buffer is not promised immutable by implementation, so callers should treat parse input as consumed.

Test signals: compile on unsupported platforms, parse invalid strings, and verify the public lifecycle does not crash when no resctrls were configured.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-resctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-resources.c -->
# sources/test-tools/stress-ng/core-resources.c

Purpose: allocates, lightly exercises, and frees many kernel and libc resource types to pressure resource accounting, cleanup paths, and limit handling in stressors.

Important APIs/types/functions: `stress_resources_allocate` creates up to `num_resources` entries of `stress_resources_t`. `stress_resources_access` touches/queries allocated resources. `stress_resources_free` releases everything. `stress_resources_init` seeds sentinel values. A small pthread helper sleeps so a live thread resource exists in the first entry.

Control flow: allocation starts by initializing sentinels, enabling KSM merge, checking memory limits, and sizing mlock allowance from `RLIMIT_MEMLOCK`. Each iteration rechecks the global continue flag and minimum free memory, then conditionally/randomly allocates memory (`calloc`, `sbrk`, `mmap`, `memfd`, `memfd_secret`), descriptors (`pipe`, `/dev/null`, eventfd, sockets, socketpair, userfaultfd, tmpfile), inotify, PTY pairs, pthread/mutex/C11 mtx, timers, semaphores, SysV/POSIX queues, pkeys, pidfds, and optional child processes. After the loop it punches holes in anonymous mappings by unmapping all but one page. Free mirrors every sentinel and closes/unmaps/destroys/removes/kills in-place. Access writes to memory regions and performs harmless `fcntl(F_GETFL)`/`kill(pid,0)` probes where available.

State and persistence: state is per-entry in the caller-provided array. Some resources have kernel persistence until explicitly removed, such as SysV semaphores/message queues and POSIX mqueues; the free path removes them. Temporary child processes sleep and are killed/waited on cleanup.

Dependencies/integration: heavy use of shim wrappers, `core-madvise`, `core-mincore`, `core-killpid`, pthread and optional OS headers. It integrates with stressors that want broad resource pressure without duplicating setup/cleanup logic.

Risks: partial allocation is expected, so sentinel correctness is critical. A notable cleanup dependency is the nested pidfd getfd close under pidfd close guards; if pidfd open failed but getfd somehow held a descriptor, cleanup would miss it. Random allocation means coverage is nondeterministic unless the RNG is controlled. `sbrk` allocations are recorded but not explicitly restored, so this intentionally perturbs process heap state.

Test signals: run under low limits, missing feature macros, interrupted continue flag, and `do_fork` true. Leak checks should include fd counts, SysV IPC objects, POSIX mqueue names, child process cleanup, and mapped-region counts before/after.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-resources.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-resources.h -->
# sources/test-tools/stress-ng/core-resources.h

Purpose: defines the cross-platform resource bundle used by `core-resources.c` and declares the allocate/access/free API.

Important APIs/types/functions: `stress_resources_t` has sentinel-backed fields for heap/mmap/sbrk memory, pipes, files, sockets, optional eventfd/memfd/userfaultfd/tmpfile, pthreads and locks, inotify, PTYs, timers, POSIX/SysV semaphores, message queues, pkeys, and pidfds. `stress_resources_allocate`, `stress_resources_access`, and `stress_resources_free` form the lifecycle.

Control flow: no runtime logic, but extensive `#if` gates ensure the struct layout only includes resources supported by the build.

State and persistence: the struct is caller-owned. Many fields represent live kernel resources that must be passed back to `stress_resources_free` for cleanup.

Dependencies/integration: includes socket, IPC, queue, semaphore, C11 thread, pthread, killpid, mmap, and syscall feature headers. It also defines `HAVE_USERFAULTFD` from `__NR_userfaultfd`.

Risks: ABI/layout differs by platform feature macros, so code must not serialize this struct or assume stable offsets. Callers must initialize via allocation helper or manually match sentinels before freeing.

Test signals: compile across feature combinations and assert that allocation/free can be called with zero resources, partial allocation, and interrupted runs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-resources.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sched.c -->
# sources/test-tools/stress-ng/core-sched.c

Purpose: centralizes scheduler policy names, option parsing, scheduler application, deadline scheduling support, and sched_ext status reporting.

Important APIs/types/functions: `stress_sched_types` lists available scheduler constants with user names and macro names. `stress_sched_name_get` maps policy to name. `stress_sched_set` validates priority and applies scheduler state. `stress_sched_parse` validates option strings. `stress_sched_settings_apply` reads stored settings for the current process. `stress_sched_ext_ops_get` reads the active sched_ext ops name from sysfs.

Control flow: `stress_sched_set` returns immediately for `UNDEFINED`. FIFO/RR policies validate priority against kernel min/max, defaulting to max under aggressive mode or midpoint otherwise. Deadline scheduling builds `shim_sched_attr`, reads `sched-period`, `sched-runtime`, and `sched-deadline` settings, uses defaults if no deadline is supplied, and calls `shim_sched_setattr`, returning `-E2BIG` specially for attribute-size mismatch. Other policies ignore explicit priorities and call `sched_setscheduler`. Unsupported platforms get a no-op shim implementation. `stress_sched_ext_ops_get` returns "unknown" by default, treats disabled/unreadable sched_ext as nonfatal, and truncates ops names after newline or repeated separators.

State and persistence: no private persistent state beyond constant scheduler table. It mutates kernel scheduling policy for the target PID, which persists until changed or process exit.

Dependencies/integration: uses `core-setting` to retrieve parsed global scheduler options, shim sched_attr syscalls, global `g_opt_flags`, and filesystem helpers for `/sys/kernel/sched_ext`.

Risks: setting real-time/deadline policies can fail due to permissions or resource limits. Deadline default values are embedded here and may not suit all kernels. `SCHED_EXT` is defined as 7 on Linux if absent, which enables parsing even on older headers but does not guarantee runtime support.

Test signals: parse all compiled policy names, apply quiet/nonquiet paths without privileges, mock `shim_sched_setattr` E2BIG, and test sched_ext sysfs disabled/enabled strings.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sched.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sched.h -->
# sources/test-tools/stress-ng/core-sched.h

Purpose: declares scheduler policy metadata and the public helpers for parsing and applying scheduler settings.

Important APIs/types/functions: `stress_sched_types_t` records numeric policy, user-facing name, macro name, and whether `sched_getscheduler` checks are expected. Public declarations expose the scheduler table/length, name lookup, setter, parser, settings applier, and sched_ext ops reader.

Control flow: header feature guards define syscall availability flags for `sched_getattr` and `sched_setattr`, and provide `SCHED_EXT` as 7 on Linux when headers do not define it.

State and persistence: no state in the header. Functions declared here can mutate process scheduler state at runtime.

Dependencies/integration: includes `core-attribute.h`, Linux sched/syscall headers where available, and uses `pid_t`, `bool`, and `ssize_t` from the common environment.

Risks: fallback definition of `SCHED_EXT` is numeric and Linux-specific; callers still need runtime error handling. Any new scheduler policy should be added to both the implementation table and tests.

Test signals: compile with old and new Linux headers, non-Linux platforms, and callers using `stress_sched_types_length` for option help.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sched.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-setting.c -->
# sources/test-tools/stress-ng/core-setting.c

Purpose: stores parsed stress-ng settings in a linked list, supports per-current-stressor lookup with global fallback, and provides sorted debug/user display.

Important APIs/types/functions: `stress_setting_free`, `stress_setting_show`, `stress_setting_dbg`, `stress_setting_set`, `stress_setting_global_set`, `stress_setting_get`, `stress_setting_set_true`, and `stress_setting_global_set_true`. `stress_setting_generic_set` is the central insert/update routine.

Control flow: setting writes validate non-null name/value, search for an existing `(stressor_name,name)` pair, allocate if missing, store `g_item_current`, mark globals by stressor name, and copy the typed value into a union. Strings are duplicated and previous string storage is freed on update. `stress_setting_get` walks from `setting_head`, starts paying attention once it reaches `g_item_current`, stops after leaving the current item unless the setting is global, and writes the requested value according to stored type. Percent-of-filesystem types are converted at lookup time using `stress_fs_size_get`. Display functions collect matching settings into arrays, sort by name with `shim_qsort`, and print formatted values.

State and persistence: private process-global `setting_head`/`setting_tail` own all settings until `stress_setting_free`. Values persist across stressor setup and child application within the process.

Dependencies/integration: relies on `g_item_current`, `g_opt_flags`, `stress_const_optdup`, size-format helpers, filesystem size helpers, logging functions, and the sort shim.

Risks: lookup behavior depends on insertion order and `g_item_current`; misordered settings can shadow or hide values. Error handling exits the process on programmer errors or allocation failure. There is no synchronization for concurrent mutation.

Test signals: set/get every `stress_type_id_t`, update string settings, global versus per-stressor precedence, percent conversion, sorted display, and freeing after repeated updates.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-setting.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-setting.h -->
# sources/test-tools/stress-ng/core-setting.h

Purpose: defines the typed setting model used to store parsed option values and declares the settings API.

Important APIs/types/functions: `stress_type_id_t` enumerates native numeric, byte-size, percentage, string, boolean, method, and callback setting categories. `stress_setting_t` is a linked-list node containing stressor identity, option name, optional pointer, type id, global flag, current item pointer, and a value union. API declarations cover freeing, showing, debugging, typed set/get, and boolean convenience setters.

Control flow: no runtime logic. The type id determines how implementation copies values, formats output, and converts percentages at lookup.

State and persistence: struct instances are implementation-owned once set. `TYPE_ID_STR` values are dynamically duplicated and freed by the settings subsystem.

Dependencies/integration: depends on `stress_list_item_t`, standard integer/size types, and stress-ng option parsing conventions. Many core modules query settings by string key, so names are integration contracts.

Risks: adding a new type requires updates in set, get, and show code. `TYPE_ID_CALLBACK` exists in the enum but is not actively handled by the current union switch logic.

Test signals: exhaustive switch coverage for enum values, especially byte percent variants and string ownership.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-setting.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-cache.c -->
# sources/test-tools/stress-ng/core-shared-cache.c

Purpose: allocates shared memory buffers sized to CPU data cache characteristics so stressors can coordinate cache- and cacheline-oriented workloads.

Important APIs/types/functions: `stress_shared_cache_alloc` determines and maps `g_shared->mem_cache.buffer` and `g_shared->cacheline.buffer`. `stress_shared_cache_free` unmaps them.

Control flow: allocation first normalizes NUMA node count and exits early to mapping if `g_shared->mem_cache.size` was already configured. It queries CPU cache details; on failure it defaults to `2 MiB * numa_nodes`. It clamps requested cache level to the detected maximum, finds a data cache at that level, and either sizes by selected cache ways or full cache size multiplied by NUMA nodes. It logs cache sizes, maps anonymous shared memory for the cache buffer and a separate per-process cacheline buffer, names mappings, and reports errors on mmap failure.

State and persistence: mutates fields under global `g_shared`. Shared anonymous mappings persist until explicit free or process exit.

Dependencies/integration: depends on CPU cache discovery, NUMA helpers, mmap naming/unmapping, `g_shared` layout, and warning/logging helpers. Stressors read these shared buffers for memory/cache activity.

Risks: if cache buffer mapping succeeds but cacheline mapping fails, the first mapping is not immediately unwound in the error path. Cache detection can be incomplete on unusual CPUs, causing default sizing. `stress_warn_once` suppresses repeated diagnostics.

Test signals: no-cache-info fallback, cache-level clamp, cache-way clamp, multi-NUMA sizing, mmap failure injection, and free after partial allocation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-cache.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-cache.h -->
# sources/test-tools/stress-ng/core-shared-cache.h

Purpose: declares shared cache buffer allocation and cleanup for stressors.

Important APIs/types/functions: `stress_shared_cache_alloc(const char *name)` initializes shared cache/cacheline buffers and returns 0 or failure. `stress_shared_cache_free(void)` releases them.

Control flow: no header logic beyond inclusion guards and `WARN_UNUSED` on allocation.

State and persistence: state is held in the global shared region, not exposed through this header.

Dependencies/integration: includes `stress-ng.h` for global types/macros and is called during stress-ng shared-memory setup/teardown.

Risks: callers should treat allocation as a process-wide setup step, not a per-stressor local allocation, because the implementation writes `g_shared`.

Test signals: compile and call lifecycle around stressors that expect `g_shared->mem_cache` and `g_shared->cacheline`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-cache.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-heap.c -->
# sources/test-tools/stress-ng/core-shared-heap.c

Purpose: provides a primitive shared-memory bump allocator used for data that needs process-shared lifetime without per-object free.

Important APIs/types/functions: `stress_shared_heap_init` maps the heap and creates a process-shared lock. `stress_shared_heap_malloc` allocates aligned chunks by advancing an offset. `stress_shared_heap_free` reports out-of-memory, unmaps the heap, destroys the lock, and clears state.

Control flow: init rounds requested metrics size up to a page, ensures at least one byte before rounding, clears shared-heap flags/list head, maps anonymous shared memory, names it, marks it mergeable, and creates a lock named `shared-heap`. On lock failure it unmaps and returns null. Allocation acquires the lock, checks remaining bytes, sets an out-of-memory flag on failure, aligns size to pointer width when advancing, releases the lock, and returns the previous offset address.

State and persistence: all allocator state lives under `g_shared->shared_heap`: heap pointer, size, offset, lock, list head, and out-of-memory flag. Allocations persist until whole-heap free; there is no individual free.

Dependencies/integration: uses `core-lock`, mmap helpers, madvise mergeable, page-size helper, and `g_shared`. It includes stressor enumeration only to derive maximum stressor context in related shared data.

Risks: no bounds hardening beyond size check; callers must request correct sizes and handle NULL. Offset is not reset in the shown init path except through global initialization assumptions, so repeated init without zeroed `g_shared` would be risky. No per-object destructor exists.

Test signals: initialize with zero and non-page sizes, concurrent allocation under lock, exhaustion flag/reporting, pointer alignment, and free after failed lock creation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-heap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-heap.h -->
# sources/test-tools/stress-ng/core-shared-heap.h

Purpose: declares the shared heap lifecycle and bump allocation interface.

Important APIs/types/functions: `stress_shared_heap_init(metrics_size)` returns an initialization token/pointer on success. `stress_shared_heap_malloc(size)` allocates from the shared heap. `stress_shared_heap_free()` tears the heap down.

Control flow: no runtime code. The API implies init-before-alloc and whole-heap-free teardown.

State and persistence: allocator state is hidden in `g_shared`; returned allocations remain valid until `stress_shared_heap_free`.

Dependencies/integration: includes `core-setting.h` for common stress-ng types/macros. Used by code that needs process-shared storage for metrics/strings.

Risks: callers cannot free individual allocations and must tolerate NULL on exhaustion.

Test signals: build users should verify all allocation paths happen after shared heap init and before free.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shared-heap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shim.c -->
# sources/test-tools/stress-ng/core-shim.c

Purpose: implements stress-ng's portability and syscall abstraction layer. It hides libc/kernel feature variation, normalizes some dangerous operations, and provides emulations where stressors need a behavior even when a direct syscall is missing.

Important APIs/types/functions: the file implements the large `shim_*` surface declared in `core-shim.h`. Common families include scheduler/yield, cache flush, file allocation/copy/sync, random/getcpu/gettid, NUMA and memory policy syscalls, mlock/madvise/mincore/statx, futexes, brk/sbrk, string helpers, pkeys, wait/pidfd, new mount API, xattrs, clocks/time, nice/autogroup, deletion wrappers, process/module/sysadmin syscalls, stat wrappers, dirent type emulation, ppoll, namespace/listns, and recent Linux syscalls.

Control flow: most wrappers prefer a libc function when reliable, fall back to `syscall(__NR_*)`, and finally call `shim_enosys`, which sets `errno=ENOSYS` and returns -1. Important exceptions are more behavioral: fallocate can retry without unsupported modes and emulate by writing zero buffers; `shim_posix_fallocate` chunks calls and returns EINTR if stress-ng is stopping; `shim_nanosleep_uint64` retries after EINTR while the continue flag remains set; `shim_waitpid` retries EINTR, sends SIGALRM during shutdown, and eventually force-kills long-stuck children; `shim_kill` refuses dangerous process-group/all-process/root pid cases; unlink/rmdir honor `OPT_FLAGS_KEEP_FILES` and force variants clear chattr flags before retrying; `shim_dirent_type` uses `lstat` if `d_type` is unavailable/unknown.

State and persistence: mostly stateless wrappers. A few functions use static/local persistent state: `shim_posix_fallocate` remembers when to use emulation, `shim_getlogin` returns a static username buffer, and `shim_nice_autogroup` writes `/proc/self/autogroup` while preserving errno. Some wrappers intentionally mutate kernel/process state: scheduling, memory policy, mount, xattr, clocks, modules, pkeys, nice value, filesystem objects, and process signaling.

Dependencies/integration: included broadly by stress-ng core and stressors. It depends on generated feature macros, architecture assembly helpers, CPU feature checks, filesystem helpers, global option flags, signal-name helpers, and continue/shutdown state.

Risks: this file is a compatibility hot spot; missing feature guards can break non-Linux builds. Emulations are semantically approximate and may be slow or alter files (`fallocate` writes zeros). Several wrappers intentionally bypass libc/VDSO to force syscalls for stress coverage. Recent syscalls guarded only by `__NR_*` may compile but fail at runtime with ENOSYS/EPERM.

Test signals: cross-platform compilation, syscall-absent ENOSYS behavior, stop-flag interruption for sleeps/fallocate/waitpid, keep-files behavior, xattr API differences on Apple/Linux, fallocate mode fallbacks, and safety checks around `shim_kill`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-shim.h -->
# sources/test-tools/stress-ng/core-shim.h

Purpose: declares the compatibility types, constants, structs, and `shim_*` API used throughout stress-ng to isolate OS/libc/kernel variation.

Important APIs/types/functions: the header defines fallback kernel typedefs, shim rlimit/priority/itimer types, `shim_loff_t`/`shim_off64_t`, directory type constants, many `SHIM_MADV_*`, `SHIM_POSIX_MADV_*`, and `SHIM_POSIX_FADV_*` constants, fallback structs for `clone3`, getcpu cache, futex waitv, linux dirents, sched_attr, statx, ustat, timex, pollfd, xattr args, file attrs, namespace IDs, and the complete extern surface for shim wrappers.

Control flow: no runtime code except `shim_unconstify_ptr`, which safely casts away const through a union for legacy APIs. Compile-time guards select native types or local struct definitions.

State and persistence: no owned state. It defines types passed to syscalls that may mutate kernel/process state through implementation functions.

Dependencies/integration: includes uio, poll, dirent, sched, resource, and many stress-ng attribute macros. Nearly every low-level stressor can include this header to avoid direct platform-specific syscall declarations.

Risks: fallback struct definitions must track kernel ABI layouts closely enough for syscall use. New constants can collide if system headers later define different values. The enormous API surface makes stale declarations a risk when implementation signatures change.

Test signals: compile on old/new Linux headers, BSD/macOS-like platforms, static builds, and with feature macros toggled. ABI-sensitive tests should call statx, sched_attr, futex_waitv, xattrat, and namespace wrappers where available.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-shim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-signal.c -->
# sources/test-tools/stress-ng/core-signal.c

Purpose: provides signal name formatting, generic handler installation/restoration, stop/exit handlers, longjump masking, SIGCHLD handling, and diagnostic SIGILL/SIGSEGV catchers.

Important APIs/types/functions: `stress_signal_name`, `stress_signal_str`, `stress_signal_longjump_mask`, `stress_signal_handler`, `stress_signal_sigchld_handler`, `stress_signal_default_handler`, `stress_signal_stop_stressing`, `stress_signal_restore`, `stress_signal_alrm_pending`, `stress_signal_exit_handler`, `stress_signal_ignore_handler`, `stress_signal_stop_flag_handler`, `stress_signal_catch_sigill`, and `stress_signal_catch_sigsegv`.

Control flow: name lookup checks realtime signal ranges then a static table. The generic handler lazily allocates one alternate signal stack with `stress_mmap_populate`, names it, installs it with `stress_stack_sigalt`, builds a `sigaction`, masks longjump-capable fatal signals for termination signals, sets `SA_NOCLDSTOP` and optionally `SA_ONSTACK`, then calls `sigaction`. Stop handlers clear the global continue flag and for alarms re-arm another alarm until workers notice. SIGCHLD handler finds args for the current PID and stops bogo counting. Diagnostic catchers use `SA_SIGINFO`, guard against recursion, print signal/address/si_code, dump nearby readable bytes, locate the mapping in `/proc/self/maps`, and `_exit(EXIT_FAILURE)`.

State and persistence: static signal-name buffers and the lazily allocated alt stack persist for process lifetime; comments acknowledge the stack leak. Installed handlers persist until restored or process exit.

Dependencies/integration: uses mmap, stack, memory-readable, logging, `stress_args_pid_find`, bogo-stop, continue flags, and Linux `/proc/self/maps` when available.

Risks: some diagnostic helpers use formatting and writes in signal context; they try to keep buffers small but are not purely async-signal-safe. The generic alt-stack allocation is process-global and leaked intentionally. `stress_signal_str` uses a static buffer, so concurrent calls overwrite it.

Test signals: install/restore handlers, pending ALRM detection, stop flag behavior, SIGCHLD helper, SIGILL/SIGSEGV diagnostics in child processes, and builds without `sigaltstack` or `/proc`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-signal.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-signal.h -->
# sources/test-tools/stress-ng/core-signal.h

Purpose: declares signal utility functions and macro implementations of siglongjmp wrappers needed for portability.

Important APIs/types/functions: declarations cover signal string/name lookup, longjump mask setup, handler install/restore, stop/exit/ignore/default handlers, SIGCHLD handler, SIGALRM pending query, SIGILL/SIGSEGV catchers, and siglongjmp wrappers. `stress_signal_siglongjmp` and `stress_signal_siglongjmp_flag` are macros rather than functions because some Cygwin builds fail when passing `sigjmp_buf` through a function.

Control flow: macro longjump wrappers ignore the signal value, call `siglongjmp`, and mark no-return; the flag variant returns if `*do_jmp` is false and clears it before jumping.

State and persistence: no header-owned state. Functions may install process signal handlers and affect global continue flags.

Dependencies/integration: includes `stress-ng.h` for signal, sigaction, sigset, sigjmp, and stress attributes. Used by stressors that recover from expected SIGSEGV/SIGBUS/SIGILL or need coordinated termination.

Risks: macros evaluate `do_jmp` pointer and jump environment directly; callers must ensure lifetime and volatile semantics. Static buffers in implementation mean string helpers are not thread-safe.

Test signals: Cygwin-compatible builds, longjump recovery stressors, handler restore paths, and fatal signal catchers in forked tests.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-signal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-smart.c -->
# sources/test-tools/stress-ng/core-smart.c

Purpose: captures S.M.A.R.T. attribute snapshots before and after a stress-ng run and reports disk attribute counters that changed.

Important APIs/types/functions: `stress_smart_start` and `stress_smart_stop` are public. Internal structs model packed SMART raw values, variable-length snapshots, and linked device entries. `stress_smart_data_read` issues the SG_IO SMART command. Diff helpers count and print changed attributes. Device helpers scan `/dev`, filter/sort candidate block devices, and maintain the linked list.

Control flow: when `OPT_FLAGS_SMART` is set and SCSI SG headers are available, start scans `/dev`, skips hidden names and names ending in digits, stats block devices, reads SMART data using a 12-byte ATA PASS-THROUGH command block, and stores successful snapshots. Stop rereads each device, counts changed raw `data` fields by matching attribute IDs, prints a table if any deltas exist, otherwise reports no devices or no changes, then frees all device/snapshot data. Unsupported builds print an availability note.

State and persistence: `smart_devs` is a static linked-list root holding begin/end snapshots between start and stop. The code reads devices but does not intentionally modify them.

Dependencies/integration: depends on SG_IO, SCSI headers, block devices under `/dev`, `shim_stat`, capability checks for root hints, logging, and global option flags.

Risks: device filtering is heuristic and may skip valid partitionless names ending in digits or include non-disk block devices. SMART reads may require root and can fail silently per device. Attribute raw layouts are vendor-specific, so deltas are useful signals but not full health interpretation.

Test signals: unsupported build path, no devices, non-root runs, SG_IO failure, changed mocked SMART attributes, memory cleanup of device lists, and formatting of known/unknown attribute IDs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-smart.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-smart.h -->
# sources/test-tools/stress-ng/core-smart.h

Purpose: declares the S.M.A.R.T. monitoring hooks used at run start and stop.

Important APIs/types/functions: `stress_smart_start(void)` captures initial disk attribute data when enabled. `stress_smart_stop(void)` captures final data, reports changes, and cleans up.

Control flow: no header logic. The intended lifecycle is start once before stressors and stop once after completion.

State and persistence: implementation keeps snapshots in static process memory between the two calls.

Dependencies/integration: included by main run orchestration around global option `--smart`.

Risks: callers should pair start/stop; calling stop without start is safe but only reports according to implementation state.

Test signals: compile with and without SCSI SG support and verify lifecycle is no-op/reporting as expected.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-smart.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sort.c -->
# sources/test-tools/stress-ng/core-sort.c

Purpose: supplies sort-related test data generation, swap/copy helpers, comparison counting, and a bundled Bentley-McIlroy quicksort fallback.

Important APIs/types/functions: `stress_sort_compare_reset/get` manage `stress_sort_compares`. `stress_sort_data_int32_init`, `shuffle`, and `mangle` create and perturb integer data. `stress_sort_swap_func` and `stress_sort_copy_func` choose optimized element-size helpers. `qsort_bm` implements fallback quicksort.

Control flow: data init generates monotonically increasing values using random deltas and an unrolled macro. Shuffle uses a linear congruential sequence and optimizes modulo with a bitmask for power-of-two lengths. Mangle flips high bits to reorder signed comparisons. Swap/copy dispatch returns exact-width helpers for 1/2/4/8 byte elements or byte loops otherwise. `qsort_bm` uses insertion sort below `THRESH`, median-of-three or pseudomedian pivoting for larger arrays, partitions equal elements to both ends, swaps equal partitions back to the center, and recursively sorts left/right partitions.

State and persistence: `stress_sort_compares` is a global aligned counter incremented by comparator functions in the header. Sorting mutates caller-provided arrays only.

Dependencies/integration: uses random generator `stress_mwc32`, pragma unroll macros, target clones, and header comparators. `shim_qsort` selects libc `qsort` or this fallback.

Risks: helper swap/copy functions assume suitable alignment for typed loads in exact-width variants. `stress_sort_data_int32_init` unroll macro assumes callers provide lengths compatible with the loop pattern used by stressors; arbitrary small non-multiple lengths would risk overrun. The global compare counter is not synchronized.

Test signals: sort correctness for many element sizes, duplicate-heavy arrays, small arrays under threshold, non-power-of-two shuffle, compare counter resets, and fallback builds without libc `qsort`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sort.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-sort.h -->
# sources/test-tools/stress-ng/core-sort.h

Purpose: declares sort helpers and defines inline comparator functions used by stressors and the fallback quicksort.

Important APIs/types/functions: swap/copy function pointer typedefs, data init/shuffle/mangle functions, comparison counter accessors, `stress_sort_swap_func`, `stress_sort_copy_func`, `qsort_bm`, `shim_qsort`, string comparator, and generated forward/reverse comparators for int8/int16/int32/int64/int.

Control flow: if libc `qsort` exists, `shim_qsort` calls it; otherwise it calls `qsort_bm`. Comparator macros load typed values, increment `stress_sort_compares`, and return conventional -1/0/1 ordering, with separate reverse variants.

State and persistence: comparators mutate global `stress_sort_compares`; no other state.

Dependencies/integration: includes inttypes and attributes; relies on `strcmp` and the `stress_sort_compares` definition in `core-sort.c`. Used broadly by sort stressors and settings display sorting.

Risks: comparator typed loads require correctly typed/aligned array elements. The compare counter creates global side effects and is not thread-safe.

Test signals: comparator ordering for equal/less/greater values, reverse ordering, string sorting, and shim selection with/without `HAVE_QSORT`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-sort.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-stack.c -->
# sources/test-tools/stress-ng/core-stack.c

Purpose: provides stack direction detection, alternative signal stack setup/sizing, stack-smash callback behavior, and optional backtrace dumping.

Important APIs/types/functions: `stress_stack_direction`, `stress_stack_top`, `stress_stack_sigalt_no_check`, `stress_stack_sigalt`, `stress_stack_sigalt_disable`, `stress_stack_sigstksz`, `stress_stack_minsigstksz`, `stress_stack_smash_check_flag_set`, and `stress_stack_backtrace`. A weak `__stack_chk_fail` override is compiled for selected GCC/musl builds.

Control flow: stack direction compares addresses of caller/local variables through a noinline helper. `stress_stack_top` offsets from the supplied region by 64 bytes depending on direction. Sigalt helpers wrap `sigaltstack`, with checked setup enforcing `STRESS_MINSIGSTKSZ`. Stack size helpers cache computed values, combining Linux `AT_MINSIGSTKSZ`, `sysconf`, compile-time `SIGSTKSZ`, and an absolute 64 KiB floor to account for architectures with large signal frames. The stack-smash override aborts with a message when reporting is enabled, otherwise exits silently. Backtrace uses `backtrace`/`backtrace_symbols` when available and flushes each line.

State and persistence: static cached signal stack sizes and `stress_stack_check_flag` persist. Alternative signal stack state is kernel thread state until disabled or replaced.

Dependencies/integration: uses auxv, execinfo, signal stack APIs, stress logging/fail helpers, and macros such as `STRESS_SIGSTKSZ`.

Risks: stack direction detection is compiler-sensitive, hence noinline/optimize0 safeguards. Weak `__stack_chk_fail` override changes process behavior on stack protector trips. Backtrace is best-effort and not safe for all signal contexts despite small buffers/flushes.

Test signals: stack direction on target architectures, sigaltstack setup below/above minimum, auxv/sysconf fallback values, stack-smash behavior in child process, and builds without execinfo/sigaltstack.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-stack.c -->
