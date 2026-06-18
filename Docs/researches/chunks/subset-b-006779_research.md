# sources/distributed-fs/ceph-client/tools/power/x86/turbostat/turbostat.c lines 9442-11720

## Scope

This chunk covers the end of `perf_l2_init()` and the late setup/runtime entry path of `turbostat.c`: CPU topology discovery, counter-buffer allocation, access checks, user-added MSR/perf/PMT counter registration, cpuidle sysfs counter probing, command-line parsing, resource-limit setup, and `main()`. It is a partial view of the file; many helper types, macros, global variables, formatting paths, and counter-reading callbacks are defined in earlier chunks.

## Purpose

The code in this range turns the earlier counter-reading machinery into a usable command-line tool. It discovers the CPUs that turbostat can monitor, builds topology and aggregation metadata, opens hardware/software telemetry sources, honors user-selected counters and CPU subsets, and selects one of the main execution modes:

- dump raw counters once with `--Dump`;
- list selected output headers with `--list`;
- measure a forked command between two snapshots;
- or enter the normal periodic `turbostat_loop()`.

The range is also where optional telemetry surfaces are attached to the common counter model: Linux perf events, sysfs cpuidle residency/count files, and Intel PMT MMIO telemetry.

## Important APIs, Types, and Functions

### Perf L2 setup

The first lines finish `perf_l2_init()`. For each allowed CPU, it opens a grouped pair of perf events for L2 references and hits. On hybrid systems it selects a PMU type and event pair according to the CPU's P-core, E-core, or L-core membership sets; on non-hybrid systems it uses the uniform PMU type. Failure to open either counter frees the L2 perf fd array and silently disables L2 reporting for this run. Success marks `BIC_L2_MRPS` and `BIC_L2_HIT` present.

Important dependencies visible here include `perf_model_support`, `perf_pmu_types`, `perf_pcore_set`, `perf_ecore_set`, `perf_lcore_set`, `fd_l2_percpu`, `open_perf_counter()`, `free_fd_l2_percpu()`, and the BIC enable/present bitsets.

### CPU topology and buffer setup

`dir_filter()` accepts directory names whose first byte is numeric, filtering `/dev/cpu`-style directory scans.

`set_thread_siblings()` allocates a per-CPU sibling set, reads `thread_siblings_list` from `/sys/devices/system/cpu/cpuN/topology`, assigns each sibling a `ht_id`, and fills `cpus[cpu].ht_sibling_cpu_id[]`. It returns the highest sibling index for sizing `topo.threads_per_core`.

`topology_probe(bool startup)` is the central topology builder. It:

- computes `topo.num_cpus` and `topo.max_cpu_num`;
- allocates `cpus`, `cpu_present_set`, `cpu_possible_set`, `cpu_effective_set`, `cpu_allowed_set`, and `cpu_affinity_set`;
- intersects present CPUs, cgroup-effective CPUs, and optional `--cpu` subset into `cpu_allowed_set`;
- sets process affinity to the allowed CPUs;
- reads hybrid type, package, die, L3, NUMA node, module, core, and sibling metadata for present CPUs;
- derives maxima and counts such as packages, cores per package, dies, L3 IDs, nodes per package, and threads per core;
- marks topology-related columns present when they are meaningful and not suppressed by summary mode;
- emits detailed topology diagnostics when debug is enabled.

`allocate_counters_1()` allocates one `thread_data`, one `core_data`, and one `pkg_data` for average counters. `allocate_counters()` allocates per-CPU, per-global-core, and per-package arrays for the even/odd sample sets and initializes sentinel IDs. `init_counter()` attaches a CPU to its thread slot and records the first allowed CPU for each core/package aggregation bucket. `initialize_counters()` initializes both even and odd sample sets for one CPU.

`allocate_output_buffer()`, `allocate_fd_percpu()`, and `allocate_irq_buffers()` allocate runtime buffers for formatted output, MSR/perf per-CPU fds, IRQ/NMI counters, and IRQ-column mapping. `topology_update()` recounts allowed CPUs, cores, and packages using the odd counter tree. `setup_all_buffers()` ties these pieces together during startup.

`set_master_cpu()` chooses the first allowed CPU. Later sysfs probes use this CPU as a representative online/allowed CPU.

### Access checks and initialization

`has_added_counters()` reports whether the user registered extra MSR/sysfs counters. `check_msr_access()` verifies MSR driver/permission state, and disables MSR-backed BICs when `--no-msr` or access failure is in effect. `check_perf_access()` similarly disables perf-backed BICs if instruction, LLC, or L2/L3 access is unavailable.

`perf_has_hybrid_devices()` caches whether Linux exposes separate `cpu_core` and `cpu_atom` perf PMUs. `added_perf_counters_init_()` initializes user-added perf counters for one linked list of `struct perf_counter_info`. It allocates an fd array per counter domain, maps CPU/core/package scope to a domain ID, translates user-facing `cpu` perf device names to `cpu_core` or `cpu_atom` on hybrid systems, reads perf type/config/scale from sysfs, and opens one fd per domain. `added_perf_counters_init()` applies this to thread, core, and package perf counters.

`turbostat_init()` is the top-level initialization sequence after command-line and cpuidle probing. It sets up buffers/topology, chooses the master CPU, checks MSR/perf access, processes CPUID/platform features, initializes built-in MSR/perf/RAPL/cstate/LLC/L2/user perf/PMT sources, populates CPU type in both counter buffers, presents IPC if perf instruction count is usable, and disables frequency/busy columns if a platform TSC tweak is required but unavailable.

### Intel PMT telemetry

`parse_telem_info_file()` opens a telemetry metadata file relative to a directory fd and scans one unsigned long.

`pmt_mmio_open()` searches `SYSFS_TELEM_PATH` for PMT telemetry directories matching a GUID, reads their `guid`, `size`, and `offset` metadata, mmaps their `telem` file, and appends `struct pmt_mmio` nodes to the global `pmt_mmios` list while preserving sysfs sequence order. `pmt_mmio_find()`, `pmt_get_counter_pointer()`, and `pmt_add_guid()` reuse or lazily open mapped PMT regions and select a sequence instance by GUID.

`pmt_find_counter()` looks up a PMT counter by name in a linked list. `pmt_get_scope_root()` returns the thread/core/package PMT counter list root in `sys`. `pmt_counter_add_domain()` ensures a counter has enough domain slots and stores the mapped counter address. `pmt_add_counter()` validates bit ranges and MMIO bounds, creates or reuses a named `struct pmt_counter`, checks that duplicate names have compatible type/scope/format/bit fields, and records the domain-specific counter pointer.

`pmt_init()` adds built-in PMT counters only when the related BICs are enabled. It tries Meteor Lake Die C6 PMT support and Clearwater Forest module C1E counters. The CWF path maps module-granular PMT values into CPU-scoped domains so every CPU in a module reports the shared module counter rather than zero.

### User-added counters and option parsing

`find_msrp_by_name()` locates an existing `struct msr_counter` by output name.

`add_counter()` registers an MSR or sysfs counter into the thread/core/package linked list in `sys`. It enforces `--no-msr` for MSR-backed counters, de-duplicates by name within scope, enforces maximum added-counter counts, initializes width/type/format/flags, and optionally attaches a `struct sysfs_path` to read a sysfs file instead of an MSR.

`make_perf_counter_info()` and `add_perf_counter()` register user-added perf counters into `sys.perf_tp`, `sys.perf_cp`, or `sys.perf_pp`; actual perf fd allocation is deferred to `added_perf_counters_init_()` after topology is known.

`parse_add_command_msr()` parses `--add` syntax for MSR, sysfs, and perf counters. It accepts tokens such as `msr0x...`, `msr...`, `/path`, `perf/device/event`, `u32` or `u64`, scope (`cpu`, `core`, `package`), type (`cycles`, `seconds`, `usec`, `raw` data behavior), format (`raw`, `average`, `delta`, `percent`), and an optional name. It creates a default column name when omitted.

`pmt_parse_from_path()` maps a direct telemetry sysfs directory path back to a PMT GUID and sequence number by comparing device/inode identity within `SYSFS_TELEM_PATH`. `parse_add_command_pmt()` handles `--add pmt,...` syntax, requiring a name, domain, offset, lsb/msb bit range, and either `guid`/`seq` or `path=...`. It validates format/type names and registers a required PMT counter with `pmt_add_counter()`.

`parse_add_command()` dispatches to PMT or MSR/sysfs/perf parsing. `is_deferred_add()`, `is_deferred_skip()`, and `verify_deferred_consumed()` support counter names that are parsed before discovery, then resolved later when cpuidle states are probed.

### cpuidle sysfs probing

`probe_cpuidle_residency()` scans `/sys/devices/system/cpu/cpu<master>/cpuidle/state*/name` from state 10 down to 0, normalizes state names such as `C1-HSW` to `C1%`, strips underscores, and adds `cpuidle/stateN/time` as a per-CPU sysfs counter when percent-idle output or deferred add requests require it.

`cpuidle_counter_wanted()` centralizes skip/add behavior for cpuidle count counters. `probe_cpuidle_counts()` adds per-CPU sysfs counters for `usage`, `above`, and `below` cpuidle files when `BIC_cpuidle` or deferred adds are active. It synthesizes names like `C1`, `C1+`, and `C1-` and avoids `below` for the deepest state and `above` for the shallowest state.

### Command line, resource limits, and main

`parse_cpu_command()` handles `--cpu`. Special values `core` and `package` switch output grouping, while numeric CPU sets are parsed into `cpu_subset`. It rejects mixing grouping keywords with explicit CPU masks.

`cmdline()` parses options in two passes. The first pass consumes `--no-msr` and `--no-perf` early so later `--add` validation can reject impossible counter requests. The second pass handles counter add/show/hide/enable options, CPU selection, dump/list/summary/quiet/debug modes, interval and iteration controls, output file selection, RAPL joules mode, TCC override, and version/help exits. It uses `getopt_long_only()` with short options and long aliases.

`set_rlimit()` raises `RLIMIT_NOFILE` to at least `MAX_NOFILE` for root, giving perf/MSR fd-heavy runs enough descriptor headroom.

`main()` initializes BIC groups, attempts to move itself into the root cgroup by writing `0\n` to `/sys/fs/cgroup/cgroup.procs`, parses options, optionally prints version and kernel command line, probes cpuidle counters, verifies deferred add/skip names, raises fd limits as root, initializes turbostat, records MSR sums, and dispatches into dump/list/fork/loop modes.

`fork_it()` is the command-measurement mode. It snapshots proc/sysfs files and even counters, forks and execs the target command in the child after broadening affinity, waits in the parent while ignoring interrupt/quit signals, snapshots odd counters after the child exits, computes deltas and platform deltas, formats average counters, prints elapsed wall time, flushes output, and returns the child exit status.

`get_and_dump_counters()` snapshots proc/sysfs files, reads odd counters once, dumps raw counters, and flushes stdout.

## Control Flow

Startup enters `main()`, initializes BIC metadata, parses the command line, and performs discovery that depends on user choices. cpuidle probing runs before `turbostat_init()` because it may create additional sysfs counters that need to be included in the later counter model. `turbostat_init()` then performs topology/buffer setup, access gating, platform discovery, and telemetry-source initialization in a fixed order where later probes depend on earlier topology and access decisions.

The topology path is front-loaded: `setup_all_buffers()` calls `topology_probe()`, allocates storage sized from topology, initializes even/odd counter structures for each proc CPU, and derives allowed topology counts. This makes subsequent counter init code domain-aware.

The runtime branch is selected only after all setup is complete. `--Dump` calls a one-shot raw dump. `--list` prints the current header selection. Remaining positional arguments are treated as a command to measure via `fork_it()`. With no positional command, control passes to the long-running sampling loop defined outside this chunk.

## State and Persistence Behavior

This chunk mutates process-global state heavily:

- topology globals (`topo`, `cpus`, CPU sets, allowed/effective/present counts);
- runtime buffer globals (`even`, `odd`, `average`, `output_buffer`, IRQ buffers, fd arrays);
- output and mode globals (`outf`, `quiet`, `debug`, `dump_only`, `list_header_only`, `summary_only`, interval/iteration settings);
- BIC enabled/present masks;
- user-added counter lists under `sys`, including MSR/sysfs, perf, and PMT linked lists;
- PMT MMIO mapping list `pmt_mmios`;
- deferred add/skip consumed bitmasks;
- process affinity and, when permitted, file-descriptor resource limits.

Persistent external effects are limited but important. The code reads sysfs/procfs extensively, opens and mmaps PMT telemetry files, opens perf events, may open MSR device files through helpers outside this chunk, writes `0\n` to `/sys/fs/cgroup/cgroup.procs` best-effort, and may write tool output to a user-specified file via `--out`.

## Dependencies and Integration Points

The chunk depends on Linux-specific APIs: `sched_setaffinity()`, dynamic CPU sets (`CPU_ALLOC`, `CPU_SET_S`, `CPU_ISSET_S`, `CPU_COUNT_S`), `/sys/devices/system/cpu`, `/sys/bus/event_source/devices`, PMT telemetry sysfs, perf event opening, `/proc/cmdline`, cgroup v2 `cgroup.procs`, `mmap()`, `fork()/execvp()/waitpid()`, and `getrlimit()/setrlimit()`.

It integrates with earlier/later turbostat internals through:

- BIC macros and lookup helpers for enabling, hiding, presenting, and printing columns;
- topology helpers such as `set_max_cpu_num()`, `for_all_proc_cpus()`, `mark_cpu_present()`, `update_effective_set()`, and `get_*_id()` functions;
- counter walking macros such as `for_all_cpus()` and `for_all_cpus_2()`;
- platform and CPUID probes (`process_cpuid()`, `counter_info_init()`, `probe_pm_features()`);
- telemetry initializers (`msr_perf_init()`, `linux_perf_init()`, `rapl_perf_init()`, `cstate_perf_init()`, `perf_llc_init()`, `perf_l2_init()`);
- formatting and output functions (`compute_average()`, `format_all_counters()`, `print_header()`, flush helpers);
- sampling loop `turbostat_loop()` outside this chunk.

## Risks and Edge Cases

- `topology_probe()` allocates CPU sets and topology buffers during startup without visible teardown in this range. Reinitialization/hotplug paths need to avoid leaks or stale pointers if this function is called after startup.
- CPU IDs are iterated up to `CPU_SUBSET_MAXCPUS` for user subsets and up to `topo.max_cpu_num` elsewhere; extremely sparse or high CPU IDs depend on these limits being consistent with earlier definitions.
- `set_thread_siblings()` allocates `put_ids` for each present CPU and fills `cpus[cpu].ht_sibling_cpu_id[ht_id]` without a visible bounds check against `MAX_HT_ID` in this chunk.
- `pmt_mmio_open()` has cleanup-sensitive paths. `loop_cleanup_and_break` closes `fd_pmt` even if `openat(..., "telem")` failed and left it `-1`, which is harmless but noisy if audited; early `break` paths can stop discovery on one malformed telemetry directory.
- PMT duplicate-name conflicts are fatal, so multiple `--add pmt` domains for the same name must match type, scope, bit range, and format exactly.
- `parse_add_command_msr()` token parsing is permissive and mutates the option string in place by replacing commas with NUL bytes. Any future caller must pass mutable storage.
- `parse_add_command_pmt()` parses `seq` with `%x`; this may surprise users expecting decimal sequence values.
- `cmdline()` resets `optind` to `0` between parsing passes, which is GNU-specific behavior.
- `probe_cpuidle_counts()` initializes `max_state` and `min_state` but does not update them in the shown range before using them to suppress `above`/`below`; either this is a logic bug in this chunk or depends on unavailable context not visible here. The result could include a deepest-state `below` counter or fail to suppress the shallowest-state `above` counter as intended.
- The best-effort write to `/sys/fs/cgroup/cgroup.procs` can fail in containers or non-root environments; the code logs with `perror()` but continues.
- Access checks disable whole BIC classes when perf/MSR is unavailable. Users requesting a hidden or added counter may see fatal validation for explicit impossible choices but quiet feature suppression for auto-detected ones.

## Test Signals

Useful test coverage for this chunk would include:

- `turbostat --version`, `--help`, `--list`, `--Dump`, `--quiet`, and `--out <file>` smoke tests.
- `--cpu` parsing tests for explicit masks, ranges, `core`, `package`, and invalid mixtures.
- `--add` parser tests for MSR decimal/hex, sysfs paths, perf `perf/device/event`, PMT `guid`/`seq`, PMT `path=...`, missing required PMT fields, invalid bit ranges, and duplicate-name conflicts.
- Non-root runs with missing MSR/perf access to verify BIC suppression and warning paths.
- Hybrid Intel systems where user-added `perf/cpu/event` counters are translated to `cpu_core` or `cpu_atom`.
- Systems with PMT telemetry sysfs to validate GUID sequence ordering, MMIO bounds checks, and CWF module-to-CPU PMT mapping.
- cpuidle systems with named states containing hyphens and underscores to validate normalized counter names and deferred add/skip consumption.
- Fork mode tests that verify elapsed time output, child exit status propagation, and counter delta reset detection.
- Large CPU-count systems to exercise CPU set allocation, fd-limit raising, topology aggregation, and first-CPU-per-core/package selection.
