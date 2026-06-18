# subset-b-009361 research

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mmap.c -->
## sources/test-tools/stress-ng/core-mmap.c

Purpose: implements mmap utility routines used by stress-ng memory stressors: page-fill/check patterns, anonymous shared mappings, forced unmapping, Linux pagemap statistics, page population, and deliberate physical-page fragmentation.

Important APIs/functions: `stress_mmap_set`, `stress_mmap_check`, `stress_mmap_set_light`, `stress_mmap_check_light`, `stress_mmap_populate`, `stress_mmap_anon_shared`, `stress_munmap_force`, `stress_mmap_stats`, `stress_mmap_stats_sum`, `stress_mmap_stats_report`, `stress_mmap_populate_forward`, `stress_mmap_populate_reverse`, and `stress_mmap_discontiguous`. The x86 `rep stosq` fast path is compiled when the build detects support and is not ILP32.

Control flow: fill/check helpers iterate page-by-page while honoring `stress_continue_flag()`. `stress_mmap_populate` first tries `MAP_POPULATE`, then falls back to ordinary `mmap`, manually touching anonymous pages. `stress_munmap_force` retries `munmap` on low-memory failures and has special handling for huge-page length mismatches by consulting `/proc/<pid>/smaps`. `stress_mmap_stats` scans `/proc/self/pagemap` one page at a time and derives present, swapped, dirty, exclusive, null, unknown, and physically contiguous counts.

State/persistence: no durable state; it mutates mapped memory, `errno`, and stress-ng metrics. Kernel state is observed through procfs and changed through mmap, munmap, mprotect, madvise, and optional SysV shared memory on Fiwix.

Dependencies/integration: depends on `stress-ng.h`, CPU/cache helpers, `core-mmap.h`, `core-put.h`, random MWC generation, memory-page-size helpers, metrics, Linux procfs, and platform feature macros.

Risks: assumes buffer alignment and sizes suitable for 64-bit/page stepping; pagemap access can be permission restricted; huge-page detection is Linux-specific; manual population can fault or SIGBUS if used on unsuitable file mappings; `STRESS_MMAP_REPORT_FLAGS_UKNOWN` preserves a misspelled public flag name.

Test signals: validate mmap stressors with write-check and page-in paths, huge-page unmap cases, Linux/non-Linux builds, restricted `/proc/self/pagemap`, short mappings, read-only mappings, and metric emission for all report flags.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mmap.h -->
## sources/test-tools/stress-ng/core-mmap.h

Purpose: public interface for mmap helpers and page-stat reporting used by memory-oriented stressors.

Important APIs/types: defines `stress_mmap_stats_t`, report flag constants for mapped/present/swapped/dirty/exclusive/unknown/null/contiguous pages, and declarations for the mmap set/check/populate/unmap/stat helpers. It also provides `stress_mmap_stats_clear` as a zeroing inline.

Control flow: the header has no runtime flow beyond the inline clear helper. It establishes the contract that callers allocate and pass `stress_mmap_stats_t` and choose report flags for `stress_mmap_stats_report`.

State/persistence: no state; the struct is caller-owned and accumulated through `stress_mmap_stats_sum`.

Dependencies/integration: relies on `stress_args_t`, `uint8_t`, `size_t`, `off_t`, `memset`, `WARN_UNUSED`, and the implementation in `core-mmap.c`. The flag names are consumed by stressors that publish memory metrics.

Risks: public flag spelling includes `STRESS_MMAP_REPORT_FLAGS_UKNOWN`, so correcting it would break callers unless aliased. Callers must provide valid mappings and lengths compatible with the implementation's page stepping.

Test signals: compile consumers with all flags, check zeroing through `stress_mmap_stats_clear`, and verify warning attributes catch ignored results for mapping/stat functions.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mmap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-module.c -->
## sources/test-tools/stress-ng/core-module.c

Purpose: wraps Linux kernel module load/unload behavior for module stressors, with stubs on unsupported platforms.

Important APIs/functions: `stress_module_load`, `stress_module_unload`, and internal `stress_module_unload_mod_and_deps`. When libkmod and Linux support exist, it uses `kmod_new`, `kmod_module_new_from_lookup`, `kmod_module_probe_insert_module`, dependency traversal, refcount checks, and `kmod_module_remove_module`.

Control flow: load creates a kmod context, resolves an alias to module list entries, then probes/inserts each module. `EEXIST` is treated as success with `already_loaded=true`. Unload exits early for modules that preexisted, skips built-ins, logs busy modules, and recursively removes dependency modules with zero refcount.

State/persistence: affects persistent kernel module state by loading and removing modules. Tracks only the caller-provided `already_loaded` boolean in process memory.

Dependencies/integration: included by stressors that exercise kernel module paths. It depends on `core-module.h`, `stress-ng.h`, libkmod headers/library, Linux, logging helpers, and build-time `HAVE_LIBKMOD_H`/`HAVE_LIB_KMOD`.

Risks: module operations require privileges and can affect the running kernel. Recursive dependency unload must avoid removing modules that other users still need; refcount checks reduce but do not eliminate race risk. Unsupported builds return `-1` and log debug messages, so callers must tolerate absence.

Test signals: build with and without libkmod, try loading an already loaded module, load failure paths, no-unload cleanup paths, built-in module lookup, dependency refcount behavior, and unprivileged execution.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-module.h -->
## sources/test-tools/stress-ng/core-module.h

Purpose: declares the module load/unload interface for stressors.

Important APIs/types: `stress_module_load(name, alias, options, already_loaded)` and `stress_module_unload(name, alias, already_loaded)`.

Control flow: none in the header; it documents by signature that load reports whether the module was already present and unload can skip preexisting modules.

State/persistence: no local state, but the declared APIs can change kernel module state.

Dependencies/integration: included by module stressor code and implemented by `core-module.c`. Requires `bool` via the common stress-ng include chain.

Risks: callers must preserve the `already_loaded` value from load to unload or they may remove modules that were present before the test.

Test signals: compile users across libkmod and stub builds, and verify callers handle negative return values.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-module.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mounts.c -->
## sources/test-tools/stress-ng/core-mounts.c

Purpose: enumerates mount points into a caller-provided array for filesystem-related stressors.

Important APIs/functions: public `stress_mount_get` and `stress_mount_free`, plus internal `stress_mount_add`.

Control flow: `stress_mount_get` has platform-specific implementations. BSD-like systems with `getmntinfo` copy `f_mntonname` entries. Systems with `getmntent` read `/etc/mtab` and fall back to `/` if it cannot open. Other platforms provide a small static fallback list `/`, `/dev`, `/tmp`. `stress_mount_free` frees all duplicated strings and clears array slots.

State/persistence: allocates duplicated mount strings that callers must release. It does not persist data or modify mounts.

Dependencies/integration: depends on mount headers selected by feature macros, `shim_strdup`, `shim_memset`, and consumers that need candidate filesystem roots.

Risks: `/etc/mtab` can be stale or absent; fallback lists may include unavailable paths; allocation failure silently drops entries; `max` must match the actual array size.

Test signals: test getmntinfo, getmntent, and fallback builds; simulate unreadable mount table; verify `stress_mount_free` handles partial allocation and repeated cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mounts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mounts.h -->
## sources/test-tools/stress-ng/core-mounts.h

Purpose: exposes mount enumeration helpers.

Important APIs/types: declares `stress_mount_get(char *mnts[], int max)` and `stress_mount_free(char *mnts[], int n)`.

Control flow: no header flow; callers request up to `max` mount strings and later free the returned count.

State/persistence: no global state. Ownership of allocated strings transfers to the caller.

Dependencies/integration: implemented by `core-mounts.c` and used by filesystem stressors needing mount candidates.

Risks: caller must not pass an undersized array and must free exactly the count returned.

Test signals: compile consumers and run ownership/leak checks around get/free pairs.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mounts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mwc.c -->
## sources/test-tools/stress-ng/core-mwc.c

Purpose: implements stress-ng's fast multiply-with-carry pseudorandom generator and helpers for random buffers, strings, and bounded values.

Important APIs/functions: `stress_mwc_reseed`, `stress_mwc_seed_set/get/default`, `stress_mwc32/64/16/8/1`, fallback `stress_mwc*modn`, `stress_rndbuf`, `stress_rndstr`, and `stress_uint8rnd4`.

Control flow: reseeding honors explicit `--seed`, deterministic `--no-rand-seed`, or mixes auxiliary vector randomness, time, process IDs, load average, resource usage, CPU/memory/filesystem/kernel traits, machine ID, and current time; it then warms the generator. Sub-word getters cache slices of 32-bit output. Buffer/string helpers stream bytes or base64url-safe characters. Fallback bounded generators use mask-and-reject loops when fast reduction is not used in the header.

State/persistence: single file-static `mwc` state with cached 16/8/1-bit fragments. Seed changes flush caches. The generator is not cryptographic and not thread-local.

Dependencies/integration: depends on global `g_opt_flags`, settings, machine/system helper functions, bit operations, endian detection, and common attributes. Many stressors use this as their random source.

Risks: global mutable state is not synchronized for concurrent threads; deterministic runs depend on seed handling and cache flushing; random filenames rely on the restricted alphabet; modulo helpers differ by compile-time fast-reduction support.

Test signals: deterministic seed regression, cache flush behavior after seed changes, endian behavior in `stress_uint8rnd4`, bounded output ranges, null buffer handling, and filename-safe string generation.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-mwc.h -->
## sources/test-tools/stress-ng/core-mwc.h

Purpose: public random-number interface and inline fast bounded reduction helpers.

Important APIs/types: declares seed and MWC output functions, random buffer/string helpers, and provides inline `stress_mwc8modn`, `stress_mwc16modn`, `stress_mwc32modn`, `stress_mwc64modn`, and `stress_mwcsizemodn`.

Control flow: when `HAVE_FAST_MODULO_REDUCTION` is defined, bounded helpers use multiply-high reduction; 64-bit reduction additionally requires `HAVE_INT128_T`. Otherwise declarations bind to fallback implementations in `core-mwc.c`.

State/persistence: no header state, but all APIs operate on `core-mwc.c`'s process-global generator state.

Dependencies/integration: included widely by stressors and core helpers; depends on `stdint.h`, `core-attribute.h`, `SIZE_MAX`, and build feature macros.

Risks: comments say range is inclusive but fast reduction returns values in `[0,max)`, so callers must understand existing convention. No zero guard exists in fast inline functions, making `max==0` a degenerate always-zero case.

Test signals: compile both int128 and non-int128 paths, assert bounded range for multiple max values, and check 32-bit versus 64-bit `size_t` selection.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-mwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-net.c -->
## sources/test-tools/stress-ng/core-net.c

Purpose: common network helper implementation for domain parsing, socket address construction, interface lookup, port reservation, checksum calculation, and port wraparound.

Important APIs/functions: `stress_net_interface_exists`, `stress_net_port_set`, `stress_net_domain`, `stress_net_domain_set`, `stress_net_sockaddr_if_set`, `stress_net_sockaddr_set`, `stress_net_sockaddr_port_set`, `stress_net_reserve_ports`, `stress_net_release_ports`, `stress_net_ipv4_checksum`, and `stress_net_port_wraparound`.

Control flow: domain helpers map textual `ipv4`, `ipv6`, and `unix` values to address families. Socket setup uses static address structs per family and optionally copies an interface address from `getifaddrs`; otherwise it uses any or loopback addresses. Port reservation builds a local busy-port bitmap from `/proc/net/*` on Linux, then locks `g_shared->net_port_map` while scanning for a free single port or contiguous range.

State/persistence: uses shared process state `g_shared->net_port_map.allocated` protected by a lock. Static sockaddr storage is overwritten by each call. Unix socket paths are derived under `/tmp`.

Dependencies/integration: depends on `core-net.h`, `core-lock.h`, bit macros, parse-option helpers, sockets, `getifaddrs`, procfs, and stressor shared memory.

Risks: static sockaddr buffers are not reentrant; port reservation can race external processes after scanning; `/proc/net` parsing is Linux-specific and best-effort; release does not take the allocation lock; AF_UNIX path construction assumes `/tmp`.

Test signals: IPv4/IPv6/Unix address generation, interface-specific binding, invalid domains, busy-port detection, contiguous reservations, concurrent stressors, checksum vectors, and wraparound for negative/overflowed ports.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-net.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-net.h -->
## sources/test-tools/stress-ng/core-net.h

Purpose: defines networking constants and helper declarations shared by socket-based stressors.

Important APIs/types: domain masks (`DOMAIN_INET`, `DOMAIN_INET6`, `DOMAIN_UNIX`, combined masks), address selectors (`NET_ADDR_ANY`, `NET_ADDR_LOOPBACK`), port ranges, default stressor port bases, and declarations for domain, sockaddr, reservation, release, checksum, and wraparound helpers.

Control flow: no runtime flow. The constants encode the stress-ng high-port allocation convention starting at 49152.

State/persistence: no state in the header; reservation APIs affect shared runtime port allocation state in `core-net.c`.

Dependencies/integration: includes `<sys/socket.h>` and `core-attribute.h`, and relies on `stress_args_t` from the common include chain.

Risks: default port offsets must remain non-overlapping and within range; adding a network stressor requires coordinated option IDs and port defaults.

Test signals: compile all socket stressors, verify default port constants stay within `MIN_STRESS_PORT..MAX_STRESS_PORT`, and test `WARN_UNUSED` callers.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-net.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-nt-load.h -->
## sources/test-tools/stress-ng/core-nt-load.h

Purpose: conditionally exposes non-temporal load intrinsics for stressors that measure cache-bypassing memory access.

Important APIs/types: inline `stress_nt_load128`, `stress_nt_load64`, `stress_nt_load32`, and `stress_nt_load_double`, each paired with a `HAVE_NT_LOAD*` macro when available.

Control flow: compile-time feature checks gate each inline implementation. All available implementations use `__builtin_nontemporal_load`.

State/persistence: no state; the helpers read from caller-provided addresses.

Dependencies/integration: relies on compiler feature macros, fixed-width integer types, `__uint128_t` availability, and the `ALWAYS_INLINE` attribute from the common include path.

Risks: no fallback functions are provided; callers must guard use with the `HAVE_NT_LOAD*` macros. Alignment and hardware semantics are caller/compiler responsibilities.

Test signals: compile with Clang/GCC feature matrices, verify macro presence controls users, and run memory stressors on architectures without non-temporal load support.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-nt-load.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-nt-store.h -->
## sources/test-tools/stress-ng/core-nt-store.h

Purpose: conditionally exposes non-temporal store intrinsics for 128-bit, 64-bit, 32-bit, and double writes.

Important APIs/types: inline `stress_nt_store128`, `stress_nt_store64`, `stress_nt_store32`, and `stress_nt_store_double`, plus `HAVE_NT_STORE*` macros. Implementations select Clang builtins, GCC x86 builtins, or Intel intrinsic forms depending on detected features.

Control flow: preprocessor branches choose the best available store implementation by type and architecture; unsupported combinations emit no helper and no availability macro.

State/persistence: no state; helpers write caller-provided memory and may bypass cache hierarchy depending on platform semantics.

Dependencies/integration: depends on `core-arch.h`, optional `<immintrin.h>`/`<xmmintrin.h>`, SSE/x86_64 feature macros, `HAVE_INT128_T`, and compiler builtin detection.

Risks: callers must guard by availability macros, provide suitable alignment, and apply any required ordering/fence semantics outside these helpers. The double GCC path type-puns through a pointer to avoid warnings, which remains ABI-sensitive.

Test signals: compile across Clang/GCC/ICC and x86/non-x86 targets, check guarded users, and run cache/memory stressors that validate written values after non-temporal paths.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-nt-store.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-numa.c -->
## sources/test-tools/stress-ng/core-numa.c

Purpose: provides NUMA node discovery, node-mask allocation, memory-policy binding, and random page placement helpers.

Important APIs/functions: `stress_numa_count_mem_nodes`, `stress_numa_mask_nodes_get`, `stress_numa_next_node`, `stress_numa_mask_alloc/free`, `stress_numa_randomize_pages`, `stress_numa_nodes`, `stress_set_mbind`, and `stress_numa_mask_and_node_alloc`.

Control flow: node discovery parses `Mems_allowed` from `/proc/self/status` backwards because Linux lists least-significant nodes last. Mask allocation sizes bitmaps by discovered max node. On Linux with mempolicy syscalls, randomization divides a buffer into bounded chunks and calls `mbind(MPOL_BIND|MPOL_MF_MOVE)` for runs of pages assigned to random allowed nodes. `stress_set_mbind` parses comma/range syntax and applies `set_mempolicy`. Unsupported builds provide no-op or failure stubs.

State/persistence: caches node count in `stress_numa_nodes`; allocates caller-owned masks; changes process memory policy and can migrate pages.

Dependencies/integration: uses Linux procfs and mempolicy syscalls through shim wrappers, MWC random numbers, option settings, bit macros, and stressor instance metadata.

Risks: parser exits the process on invalid `--mbind`; procfs parsing is Linux-specific; page migration can fail silently in randomization; chunk size heuristics trade coverage for setup cost; cached node count can stale after hotplug.

Test signals: single-node and multi-node systems, cgroup/cpuset restricted mems, invalid range syntax, unsupported builds, page migration permissions, and stressors with NUMA flags.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-numa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-numa.h -->
## sources/test-tools/stress-ng/core-numa.h

Purpose: public NUMA support contract and fallback memory-policy constants.

Important APIs/types: `stress_numa_mask_t` describes discovered node count, maximum nodes, allocated bitmask, mask size, and element count. The header defines missing `MPOL_*` and `MPOL_F/MF_*` constants and declares all NUMA helper functions.

Control flow: no header runtime flow. Constants allow code to compile on headers that lack newer memory-policy values.

State/persistence: no header state; declared APIs may allocate masks, cache node counts, and set process memory policy.

Dependencies/integration: optionally includes `<linux/mempolicy.h>` and relies on `stress_args_t`, bool, and size types from the common include chain.

Risks: fallback constants must match kernel ABI values; mask size fields are easy to misuse because bits and bytes are both represented.

Test signals: compile against old and new Linux headers, verify mask allocation/free ownership, and check callers clear feature flags when allocation fails.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-numa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-opts.c -->
## sources/test-tools/stress-ng/core-opts.c

Purpose: central GNU long-option registry for the stress-ng command-line parser.

Important APIs/types: defines `const struct option stress_long_options[]`, mapping option names to `stress_op_t` enum values and argument requirements. Entries cover global flags, stressor selectors, and per-stressor tuning options.

Control flow: no algorithmic flow beyond the sentinel `{ NULL, 0, NULL, 0 }`. Runtime parsing elsewhere passes this table to getopt-style logic and receives enum IDs.

State/persistence: immutable static command-line metadata. It does not store parsed values.

Dependencies/integration: depends on `stress-ng.h`, `core-opts.h`, `getopt.h`, and many feature macros that conditionally expose options such as `--perf`, `--pipe-size`, `--syslog`, and `--vm-populate`.

Risks: table and `stress_op_t` enum must stay synchronized; duplicate or mismatched option IDs would route parsing incorrectly; conditional entries affect CLI availability by build platform; argument-required flags must match downstream parser expectations.

Test signals: automated `--help`/`--stressors` output, option parsing smoke tests for representative stressors, duplicate-name detection, feature-gated build matrices, and verifying every enum referenced here exists in `core-opts.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-opts.h -->
## sources/test-tools/stress-ng/core-opts.h

Purpose: defines global option flag bits and the complete command option enum namespace.

Important APIs/types: `OPT_FLAGS_*` bit masks for global behavior such as metrics, randomization, verify, OOM handling, perf, taskset, dry-run, progress, and build info; `OPT_FLAGS_MINMAX_MASK` and `OPT_FLAGS_AGGRESSIVE_MASK`; declaration of `stress_long_options`; and the `stress_op_t` enum covering short options and long-only IDs.

Control flow: no runtime flow. Enum values form the dispatch contract consumed by command-line parsing and stressor option tables.

State/persistence: no direct state, but flag bits are stored in global `g_opt_flags` elsewhere.

Dependencies/integration: includes `<unistd.h>` and `<getopt.h>`, relies on `STRESS_BIT_ULL`, and must align with `core-opts.c`, parser switch logic, stressor option tables, and documentation/help generation.

Risks: only 64 global flag bits are available; enum churn can break serialized assumptions or switch cases; conditional options in `core-opts.c` still need enum IDs here; names are a large manual registry with high typo/duplication risk.

Test signals: compile all stressor option tables, run option-registry consistency checks, exercise short option aliases, and validate global flags through CLI integration tests.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-opts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-out-of-memory.c -->
## sources/test-tools/stress-ng/core-out-of-memory.c

Purpose: manages OOM-killer adjustment and provides a retrying child-process wrapper for stressors expected to exhaust memory.

Important APIs/functions: `stress_process_oomed`, `stress_set_oom_adjustment`, and `stress_oomable_child`, with Linux, FreeBSD, and stub variants.

Control flow: Linux OOM detection scans `/dev/kmsg` for OOM messages mentioning the child PID. Adjustment writes `/proc/self/oom_score_adj`, falling back to `/proc/self/oom_adj`. The child wrapper optionally bypasses for `--oom-no-child`; otherwise it forks, marks the child OOM-killable, optionally drops capabilities, invokes the stressor callback, and the parent restarts on OOM SIGKILL, SIGSEGV, or SIGBUS unless `--oomable` changes OOM into accepted success.

State/persistence: mutates process OOM score/protection, child process lifecycle, `args->stats->s_pid.oomable_child`, and `args->bogo.possibly_oom_killed`. It can remove stressor temporary directories after accepted OOM.

Dependencies/integration: uses global flags/timeouts, signal helpers, capability dropping, process state reporting, kill helpers, filesystem cleanup, and platform OOM APIs.

Risks: `/dev/kmsg` may be unreadable; OOM attribution is heuristic; repeated fork under memory pressure can loop until timeout/continue flag; `WEXITSTATUS` is used after non-signaled statuses and should only be trusted for normal exits; changing OOM scores requires permissions.

Test signals: Linux privileged/unprivileged runs, `--oomable`, `--oom-no-child`, `--no-oom-adjust`, child SIGBUS/SIGSEGV restart, wait interruption escalation, timeout handling, and FreeBSD/stub builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-out-of-memory.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-out-of-memory.h -->
## sources/test-tools/stress-ng/core-out-of-memory.h

Purpose: declares OOM adjustment and OOM-tolerant child execution helpers.

Important APIs/types: `stress_oomable_child_func_t` callback type, `stress_process_oomed`, `stress_set_oom_adjustment`, and `stress_oomable_child`.

Control flow: header only establishes that wrapped stressor callbacks receive `stress_args_t *` and opaque context and return an exit status.

State/persistence: no header state; declared functions manipulate process OOM settings and child lifecycle.

Dependencies/integration: includes `stress-ng.h` for `stress_args_t`, `pid_t`, bool, and OOM wrapper flags supplied elsewhere.

Risks: callbacks must be safe to run in a forked child and must not rely on parent-only state after fork.

Test signals: compile stressors using the callback type and verify wrapper flags are passed consistently.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-out-of-memory.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-parse-opts.c -->
## sources/test-tools/stress-ng/core-parse-opts.c

Purpose: implements typed option parsing, range validation, unit scaling, percentage conversion, method lookup, domain/port parsing, and storage into the stress-ng settings system.

Important APIs/functions: range checkers, numeric getters for signed/unsigned integer widths, `stress_get_uint64_scale`, byte/time/percentage helpers, `stress_get_int32_instance_percent`, `stress_parse_opt`, and `stress_unimplemented_method`.

Control flow: scalar parsers validate signs and digits, parse with `sscanf`, and on errors print to stderr then `longjmp(g_error_env, 1)`. Byte parsing handles suffixes and cache-size tokens like `LLC`/`L<n>`. Percent parsing scales by max and instance count. `stress_parse_opt` switches on `stress_type_id_t`, converts `opt_arg`, checks min/max, and calls `stress_setting_set`; methods iterate a supplied method-name callback; callbacks can supply a dynamic type/value.

State/persistence: writes parsed values into the settings subsystem. It relies on global error jump state and reads system CPU/cache/memory/filesystem data for derived values.

Dependencies/integration: depends on `core-parse-opts.h`, settings, CPU cache helpers, network helpers, global `optarg` for one CPU-percent branch, and stress-ng type IDs.

Risks: callers must establish `g_error_env`; suffix multiplication can overflow silently; `TYPE_ID_INT32_CPU_PERCENT` uses global `optarg` instead of local `opt_arg`; filesystem percent helper currently scales against 100 rather than actual filesystem space; parser exits control flow non-locally.

Test signals: fuzz numeric strings, min/max boundaries, suffixes, cache-size tokens, percent semantics, method choices, callbacks, domain/port parsing, and longjmp recovery.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-parse-opts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-parse-opts.h -->
## sources/test-tools/stress-ng/core-parse-opts.h

Purpose: public typed option parsing contract for stressor-specific options.

Important APIs/types: `stress_opt_t` option descriptor, `END_OPT` sentinel, `stress_scale_t`, declarations for all scalar parsers, range checkers, scaling helpers, and `stress_parse_opt`.

Control flow: no header flow; option tables terminate with `END_OPT` and are interpreted by `stress_parse_opt`.

State/persistence: no header state; parsed results are persisted in the settings subsystem by implementation functions.

Dependencies/integration: includes `core-attribute.h` and `core-setting.h`, and uses `stress_type_id_t` plus standard integer types.

Risks: descriptor `data` is untyped and must match `type_id` expectations; min/max are unsigned even for signed types, requiring careful casts in callers; `END_OPT` must remain in sync with parser sentinel logic.

Test signals: compile stressor option tables, static checks for sentinel termination, and parser tests for every `TYPE_ID_*` used by stressors.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-parse-opts.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf-event.c -->
## sources/test-tools/stress-ng/core-perf-event.c

Purpose: small compile unit that includes Linux perf event definitions when available.

Important APIs/types: does not define runtime APIs; conditionally includes `<linux/perf_event.h>` after `config.h`.

Control flow: none beyond preprocessor gating.

State/persistence: no state.

Dependencies/integration: exists to participate in build/config checks around `HAVE_LINUX_PERF_EVENT_H` and the local `core-perf-event.h` include used by `core-perf.c`.

Risks: its value is build-system oriented; missing or incompatible kernel headers should be caught at compile time.

Test signals: build on Linux with perf headers and on systems without them.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf.c -->
## sources/test-tools/stress-ng/core-perf.c

Purpose: implements optional Linux perf counter collection and reporting for stressor runs.

Important APIs/functions: `stress_perf_init`, `stress_perf_open`, `stress_perf_enable`, `stress_perf_disable`, `stress_perf_close`, and `stress_perf_stat_dump`. Internal helpers resolve tracepoint IDs, wrap `perf_event_open`, sanitize YAML labels, scale per-second values, and compute relative metrics.

Control flow: when perf support is compiled in, `stress_perf_init` resolves tracepoint configs from `/sys/kernel/debug/tracing/events/*/id`. `stress_perf_open` initializes per-counter fds and opens every resolved hardware/software/tracepoint event for the current process with inheritance. Enable/disable use perf ioctls. Close reads counters plus time enabled/running and scales multiplexed values. Dump aggregates per-stressor instance counters, prints human-readable rates and relative ratios, and writes YAML.

State/persistence: per-stressor `stress_perf_t` stores fds/counters. Shared `g_shared->perf.no_perf` suppresses repeated failed attempts behind a lock. No durable persistence except YAML/log output.

Dependencies/integration: Linux `perf_event_open`, perf_event headers, syscall support, `core-perf.h`, `core-lock.h`, stressor stats lists, logging/YAML helpers, locale formatting, and kernel debugfs/procfs.

Risks: perf permissions commonly block unprivileged users; tracepoint paths vary by kernel; many fds can be opened per stressor; static formatting buffers are not thread-safe; duration zero affects per-second YAML; unsupported builds compile out the implementation.

Test signals: privileged/unprivileged perf runs, high `perf_event_paranoid`, missing debugfs tracepoints, counter multiplex scaling, YAML output, multi-instance aggregation, and no-perf fallback messaging.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf.h -->
## sources/test-tools/stress-ng/core-perf.h

Purpose: public perf statistics types and API declarations, compiled only when perf support is available.

Important APIs/types: `STRESS_PERF_STATS`, `STRESS_PERF_INVALID`, `STRESS_PERF_MAX`, `stress_perf_stat_t`, `stress_perf_t`, and declarations for perf open/enable/disable/close/dump/init.

Control flow: preprocessor gates the entire API on pthread, Linux perf header, and `__NR_perf_event_open` availability.

State/persistence: `stress_perf_t` is caller-owned per stressor instance and stores file descriptors plus final counters.

Dependencies/integration: included by stats structures and `core-perf.c`; requires Linux perf build features and stress-ng list/stat types.

Risks: code using perf APIs must be inside the same `STRESS_PERF_STATS` guard; `STRESS_PERF_MAX` must cover the implementation table size.

Test signals: compile with and without perf support, validate structure initialization, and assert the event table never exceeds `STRESS_PERF_MAX`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-perf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-personality.c -->
## sources/test-tools/stress-ng/core-personality.c

Purpose: build compatibility unit for Linux process personality support.

Important APIs/types: does not define functions; conditionally includes `<sys/personality.h>` when Linux and header support are detected.

Control flow: none beyond preprocessor selection.

State/persistence: no state and no runtime side effects.

Dependencies/integration: depends on `config.h` feature detection. It likely ensures the generated config and build environment can compile personality-related stressor support.

Risks: because it has no exported symbol, its utility depends on build-system expectations; unsupported systems should compile with the include omitted.

Test signals: build on Linux with and without personality header detection and confirm personality stressor files provide actual runtime behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-personality.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-pragma.h -->
## sources/test-tools/stress-ng/core-pragma.h

Purpose: centralizes compiler pragma wrappers for optimization, warning suppression, and loop unrolling.

Important APIs/types: `STRESS_PRAGMA`, `STRESS_PRAGMA_PREFETCH`, `STRESS_PRAGMA_NOPREFETCH`, optional `STRESS_PRAGMA_NO_HARD_DFP`, diagnostic push/pop/warn-off macros, `STRESS_PRAGMA_WARN_CPP_OFF`, `PRAGMA_UNROLL_N`, and `PRAGMA_UNROLL`.

Control flow: compile-time branches select pragma spellings by compiler family/version and feature macros. Unsupported compilers receive empty macros.

State/persistence: no runtime state.

Dependencies/integration: consumed across code that needs local diagnostic suppression or optimization hints. Relies on config macros such as `HAVE_PRAGMA`, `HAVE_COMPILER_CLANG`, `HAVE_COMPILER_GCC_OR_MUSL`, `NEED_CLANG`, and `NEED_GNUC`.

Risks: incorrect compiler/version detection can emit unsupported pragmas or fail to suppress warnings; empty fallback means performance hints silently disappear; warning-off macros can hide real diagnostics in wrapped code.

Test signals: compiler matrix builds for GCC, Clang, ICC, and musl-style configurations; warning-clean builds around wrapped third-party/system includes; and loop-unroll pragma smoke builds.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-pragma.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-prime.c -->
## sources/test-tools/stress-ng/core-prime.c

Purpose: provides simple 64-bit prime testing and prime selection helpers used for stride values, especially file-name or traversal patterns.

Important APIs/functions: `stress_prime64_check`, `stress_prime64_next_get`, and `stress_prime64_get`.

Control flow: primality handles small values, rejects divisible-by-2/3 cases, then tests `6k +/- 1` factors up to `sqrt(n)+1`. `stress_prime64_get` searches up to 2000 odd candidates above `n` for a prime that does not divide `n`, falling back to the largest 64-bit prime. `stress_prime64_next_get` is similar but uses a static rolling candidate so repeated calls vary the returned prime and falls back to 1009.

State/persistence: `stress_prime64_next_get` keeps a file-static `p` across calls; no durable state.

Dependencies/integration: uses `stress_continue_flag`, `shim_sqrt`, and common branch/attribute macros.

Risks: static `p` is not thread-safe; search can stop early when stress-ng is terminating; double sqrt can be imprecise near very large values though the loop is conservative; fallback behavior differs between next/get variants.

Test signals: known prime/composite vectors, small n values, very large values near `UINT64_MAX`, repeated next-call uniqueness, stop-flag behavior, and concurrent callers if used from threads.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-prime.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-prime.h -->
## sources/test-tools/stress-ng/core-prime.h

Purpose: declares 64-bit prime helpers.

Important APIs/types: `stress_prime64_check`, `stress_prime64_next_get`, and `stress_prime64_get`.

Control flow: no header runtime flow; attributes mark pure-ish checking and warn on ignored results.

State/persistence: no header state; `stress_prime64_next_get` has implementation-static state.

Dependencies/integration: includes `stress-ng.h` for integer types and attributes. Used by code needing stride values not sharing factors with a target.

Risks: callers expecting deterministic `stress_prime64_next_get` must account for its static rolling state.

Test signals: compile users and verify ignored result warnings where supported.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-prime.h -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-processes.c -->
## sources/test-tools/stress-ng/core-processes.c

Purpose: dumps currently running stress-ng-related processes on Linux for diagnostics.

Important APIs/functions: `stress_processes_dump`, with internal Linux-only `stress_processes_dump_filter`.

Control flow: Linux implementation scans `/proc` for numeric entries, computes PID column width, reads each process `cmdline`, filters to commands containing `stress-ng`, reads owner and `/proc/<pid>/status` for parent PID and state, then logs a compact process line. Non-Linux builds provide an empty function.

State/persistence: no persistent state. It allocates a scandir list, reads procfs, resolves usernames through passwd database unless statically built, and logs diagnostic output.

Dependencies/integration: depends on procfs, `scandir`, `alphasort`, filesystem read helpers, logging, `getpwuid`, and common shim functions.

Risks: proc entries can disappear while being read; command substring filtering may match helper commands containing `stress-ng`; static buffers truncate long cmdlines; `getpwuid` may be unavailable in static builds.

Test signals: Linux diagnostic runs with multiple stress-ng children, disappearing-process races, static build ownership output, non-Linux no-op build, and long command-line handling.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-processes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/core-processes.h -->
## sources/test-tools/stress-ng/core-processes.h

Purpose: declares the process diagnostic dump helper.

Important APIs/types: `stress_processes_dump(void)`.

Control flow: no header flow.

State/persistence: no state; implementation only logs diagnostics.

Dependencies/integration: included by code paths that want a process snapshot, especially failure or status reporting paths.

Risks: callers should treat it as best-effort and platform-dependent.

Test signals: compile all callers and exercise diagnostic output on Linux and no-op behavior elsewhere.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/core-processes.h -->
