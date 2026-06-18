# Research: sources/distributed-fs/ceph-client/tools/power/x86/turbostat/turbostat.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-006778`: lines 1-9441, `Docs/researches/chunks/subset-b-006778_research.md`
- `subset-b-006779`: lines 9442-11720, `Docs/researches/chunks/subset-b-006779_research.md`

## Chunk Research

### subset-b-006778: lines 1-9441

# sources/distributed-fs/ceph-client/tools/power/x86/turbostat/turbostat.c lines 1-9441

## Scope

This chunk covers the first 9,441 lines of the Linux `turbostat.c` implementation. It starts at the file header and includes the bulk of turbostat's platform model tables, built-in column definitions, counter data structures, MSR/perf/sysfs/PMT counter acquisition, delta and formatting logic, runtime sampling loop, CPU feature probing, power/thermal/idle diagnostics, RAPL and cstate setup, and LLC/L2 perf initialization up to the middle of `perf_l2_init()`.

The chunk ends before the later part of `perf_l2_init()` and before topology probing/allocation, dynamic `--add` parsing, PMT counter registration, command-line parsing, child command handling, and `main()`. Those later sections are needed for a complete per-file report, but the code here already defines most of the state model and measurement pipeline used by the rest of the file.

## Purpose

`turbostat` is a user-space x86 power and frequency observation tool. This chunk implements the core machinery for discovering which CPU/package counters are available, taking two snapshots of those counters, calculating deltas over a measurement interval, and printing per-system, per-package, per-core, and per-thread columns such as frequency, busy percentage, C-state residency, RAPL power/energy, thermal readings, IRQ/NMI/SMI counts, graphics residency/frequency, uncore frequency, LLC/L2 stats, and user-added MSR/perf/PMT counters.

The implementation is tightly coupled to Linux x86 hardware interfaces:

- `/dev/cpu/%d/msr` or Android-style `/dev/msr%d` for model-specific registers.
- `perf_event_open()` and `/sys/bus/event_source/devices/*` for perf PMU counters.
- `/proc/stat` and `/proc/interrupts` for CPU inventory and interrupt deltas.
- `/sys/devices/system/cpu`, `/sys/class/drm`, `/sys/class/powercap`, `/sys/class/intel_pmt`, and debugfs fallback paths for topology, cpuidle, graphics, RAPL, uncore, and PMT telemetry.
- CPUID leaves and x86 MSR definitions from the kernel headers included through build-time macros such as `MSRHEADER` and `INTEL_FAMILY_HEADER`.

## Important Types, Tables, and Globals

The top-level counter model is shared across built-in and dynamic counters:

- `enum counter_scope`, `enum counter_type`, `enum counter_format`, and `enum counter_source` describe whether a counter is CPU/core/package scoped, how it should be interpreted, how it should be printed, and whether data is sourced from perf or MSR access.
- `struct msr_counter` represents dynamic MSR or sysfs-added counters, including MSR number, sysfs paths, output name, width, type, format, flags, and linked-list membership.
- `struct perf_counter_info` represents dynamic perf counters, including perf device/event names, display metadata, scope, scale, and per-domain file descriptors.
- `struct pmt_mmio`, `struct pmt_counter`, and related PMT structs describe Intel PMT MMIO telemetry regions and per-domain counter pointers. This chunk includes PMT directory iteration, domain storage growth, width calculation, value masking, and reads; dynamic PMT registration continues after this chunk.
- `struct thread_data`, `struct core_data`, and `struct pkg_data` are the main snapshot records. They store timestamps, TSC/APERF/MPERF, cstate counters, IRQ/NMI/SMI, cache stats, thermal values, RAPL counters, graphics/SAM metrics, uncore frequency, and fixed-size arrays for added MSR/perf/PMT counters.
- `struct counters` groups thread/core/package arrays for `even`, `odd`, and `average` snapshots.
- `struct cpu_topology` and `struct topo_params` track CPU IDs, package/core/module/die/L3/node topology, SMT siblings, allowed/present CPUs, and aggregate counts. This chunk defines the structures and helper iteration contracts; the full topology population code is later.

Built-in columns are represented by `bic[]`, `enum bic_names`, and multiple `cpu_set_t` bitsets:

- `bic_present` says a column is supported by the current platform/probe state.
- `bic_enabled` says the user has not hidden the column.
- `DO_BIC()` requires both enabled and present; `DO_BIC_READ()` checks presence only.
- `bic_groups_init()` creates semantic groups such as topology, power, frequency, hardware idle, software idle, cache, other, and disabled-by-default columns. This is what powers `--show`, `--hide`, and named groups such as `power`, `idle`, `cache`, and `frequency`.

Platform capability state is driven by `struct platform_features` and `turbostat_pdata[]`. The feature table maps Intel VFM identifiers to support bits for Nehalem-style MSRs, config TDP, base clock, cstates, IRTL, module C6, extended C0 residency, turbo-ratio MSRs, perf-limit-reason MSRs, RAPL domains, AMD quirks, TCC offset width, and TSC/perf multipliers. `probe_platform_features()` selects the table based on CPUID family/model and AMD/Hygon RAPL feature bits.

Perf cache support is separately modeled by `struct perf_model_support` and `turbostat_perf_model_support[]`. It maps Intel models, including hybrid platforms, to L2 reference/hit perf event encodings for up to three PMU classes.

## Counter Descriptor Families

RAPL descriptors are defined by:

- `enum rapl_rci_index`, `struct rapl_counter_info_t`, `struct rapl_counter_arch_info`, and `rapl_counter_arch_infos[]`.
- Each architecture descriptor carries the feature mask, perf subsystem/event name, MSR, mask/shift, platform scale pointer, output BIC, compatibility scale, and flags such as platform-level counter or MSR-sum requirement.
- Intel and AMD variants are both present. Several user-facing columns share one underlying physical counter but differ by output unit, for example `PkgWatt` versus `Pkg_J`.

C-state descriptors are defined by:

- `enum ccstate_rci_index`, `struct cstate_counter_info_t`, `struct cstate_counter_arch_info`, and `ccstate_counter_arch_infos[]`.
- The table maps core C1/C3/C6/C7 and package PC2/PC3/PC6/PC7/PC8/PC9/PC10 to perf cstate events or residency MSRs.
- Flags control per-thread versus per-core collection and soft-C1 dependencies. `pkg_cstate_limit` gates package C-state MSR use.

APERF/MPERF/SMI are modeled through:

- `enum msr_rci_index`, `struct msr_counter_info_t`, `struct msr_counter_arch_info`, and `msr_counter_arch_infos[]`.
- `msr_perf_init()` decides whether APERF/MPERF and SMI are needed, opens perf equivalents where possible, and falls back to MSR reads.

Long-running RAPL reads use:

- `enum { IDX_PKG_ENERGY, ... IDX_COUNT }`, `struct msr_sum_array`, `idx_to_offset()`, `offset_to_idx()`, `idx_valid()`, `get_msr_sum()`, `update_msr_sum()`, and `msr_sum_record()`.
- A POSIX timer periodically accumulates 32-bit-wrapping RAPL MSRs so interval mode can report longer durations without losing wraparound information.

## Core Control Flow

The measurement pipeline in this chunk has three stages.

First, probes establish platform and counter availability:

- `process_cpuid()` reads vendor, family/model/stepping, hypervisor presence, microcode, invariant TSC, APERF/MPERF, DTS/PTM, turbo, HWP, EPB, SGX, hybrid CPU support, CPUID 0x15 TSC/crystal ratio, and CPUID 0x16 base/max/bus MHz. It selects `platform`, L2 perf model support, and marks basic columns such as IRQ, NMI, TSC MHz, temperatures, and package temperature as present.
- `probe_pm_features()` calls `probe_pstates()`, `probe_cstates()`, `probe_lpi()`, `probe_intel_uncore_frequency()`, `probe_graphics()`, `probe_rapl()`, and `probe_thermal()`, then decodes miscellaneous feature-control state when verbose output is enabled.
- `linux_perf_init()`, `msr_perf_init()`, `rapl_perf_init()`, `cstate_perf_init()`, `perf_llc_init()`, and `perf_l2_init()` allocate and open the perf/MSR resources used by snapshot reads. If perf is not available or a counter cannot be opened, the corresponding column is not marked present or is cleared.

Second, snapshots are collected:

- `snapshot_proc_sysfs_files()` captures `/proc/interrupts`, graphics sysfs values, and low-power-idle counters before per-CPU MSR/perf reads.
- `for_all_cpus()` and `for_all_cpus_2()` iterate allowed CPUs in topology order while accounting for SMT sibling handling. `for_all_cpus()` is defined earlier in this chunk and `for_all_cpus_2()` handles paired odd/even snapshots.
- `get_counters()` migrates the process to the target CPU, timestamps the snapshot, reads local TSC with `rdtsc()`, reads APERF/MPERF/SMI via `get_smi_aperf_mperf()`, reads LLC/L2 perf groups, instruction count, IRQ/NMI values, C-state counters, user-added thread counters, then conditionally reads core-scoped and package-scoped counters only on first thread/core representatives.
- Package collection includes extended C0 residency MSRs, low-power-idle sysfs snapshots, RAPL counters, package temperature, uncore frequency, graphics/SAM values, and dynamic package counters.

Third, snapshots are converted to printable interval data:

- `delta_thread()`, `delta_core()`, `delta_package()`, and `delta_platform()` transform a newer snapshot and an older snapshot into interval deltas. Raw and average-format dynamic counters are preserved rather than subtracted. C1 can be derived in software from TSC, MPERF, and deeper cstates when a dedicated C1 MSR is unavailable.
- `compute_average()` clears the average buffers, sums per-thread/per-core/per-package data via `sum_counters()`, and divides by `topo.allowed_cpus`, `topo.allowed_cores`, or `topo.allowed_packages` where appropriate.
- `print_header()` emits columns based on enabled/present BICs plus dynamic MSR/perf/PMT lists.
- `format_counters()` prints one summary, per-CPU, per-core, or per-package row, applying percentages, energy-to-watt conversion, MHz scaling, counter formatting, package-only/core-only filtering, and `--cpu` subset filtering.
- `format_all_counters()` controls header cadence, prints the average row, and then prints individual CPU rows unless summary-only mode is active.
- `flush_output_stdout()` and `flush_output_stderr()` drain the shared `output_buffer`.

`turbostat_loop()` ties the pieces together for interval mode. It installs signal handlers, tries to raise priority, takes an initial even snapshot, then alternates odd and even snapshots around sleeps. On CPU hotplug, cpuset effective changes, or selected recoverable snapshot errors it calls `re_initialize()`, which frees buffers and re-runs setup. Fatal negative return codes exit immediately. `SIGINT`, `q` on stdin, EOF on stdin, and `num_iterations` control loop termination.

## State and Persistence Behavior

Most state is in process-global variables and is rebuilt at startup or by `re_initialize()`. There is no repository or disk persistence in this chunk except normal output files opened elsewhere and kernel/sysfs/procfs state that turbostat reads.

Important mutable state includes:

- Column state in `bic_enabled` and `bic_present`, modified by defaults, user show/hide lists, probes, and failure fallbacks such as `bic_disable_msr_access()`, `bic_disable_perf_access()`, `free_fd_llc_percpu()`, and `free_fd_l2_percpu()`.
- Platform state in globals such as `platform`, `bclk`, `base_hz`, `tsc_hz`, `tsc_tweak`, `crystal_hz`, `valid_rapl_msrs`, RAPL unit scales, `pkg_cstate_limit`, `tj_max`, and vendor flags.
- Snapshot buffers `even`, `odd`, and `average`, with the older buffer reused to hold deltas after `delta_cpu()`.
- Per-CPU/per-domain file descriptors for MSR, perf instruction count, LLC, L2, RAPL, cstate, and dynamic perf counters.
- CPU sets for possible, present, allowed, effective cpuset-cgroup CPUs, affinity, requested subset, and hybrid PMU core classes.
- Dynamic counter linked lists in `sys.tp`, `sys.cp`, `sys.pp`, `sys.perf_*`, and `sys.pmt_*`; allocation and parsing continue later in the file.
- `per_cpu_msr_sum`, updated asynchronously by a POSIX timer thread to handle wrapping RAPL MSR accumulation.
- Graphics sysfs `FILE *` handles and cached values in `gfx_info[]`.

The code repeatedly mutates kernel-visible process state through `sched_setaffinity()` to migrate the measuring thread to each target CPU. It may attempt `/sbin/modprobe msr`, checks `CAP_SYS_RAWIO`, opens privileged MSR devices, opens perf events, and reads many sysfs/debugfs files. It does not write MSRs in this chunk, but it prints decoded hardware configuration that may be sensitive in diagnostics.

## Dependencies and Integration Points

This chunk depends on Linux and x86-specific APIs:

- Build-time macro includes for MSR and Intel family model constants.
- glibc/Linux system calls and headers for `sched_setaffinity`, `sched_getcpu`, `select`, `timer_create`, `timer_settime`, `perf_event_open`, `cap_get_proc`, `CPU_ALLOC`, `CPU_SET_S`, and `scandir`.
- `/dev/cpu/*/msr` or `/dev/msr*` access and `CAP_SYS_RAWIO` for MSR-backed counters.
- Perf event source sysfs layout for event `type`, `events/<name>`, `.scale`, and `.unit`.
- CPU topology sysfs files such as `thread_siblings`, `physical_package_id`, `die_id`, `cluster_id`, `core_id`, cache `index3/id`, and cgroup `cpuset.cpus.effective`.
- CPU idle and power sysfs/debugfs files, including cpuidle low-power-idle residency and `/dev/cpu_dma_latency`.
- Intel uncore frequency sysfs, both legacy package/die paths and clustered `uncore%02d` paths.
- i915/Xe DRM sysfs graphics residency and frequency paths.
- RAPL MSRs and `/sys/class/powercap` powercap domain files.
- Intel PMT sysfs telemetry roots under `SYSFS_TELEM_PATH`.

The rest of `turbostat.c` integrates with this chunk by allocating topology buffers, populating `cpus[]`, parsing `--show`, `--hide`, `--add`, `--cpu`, and output options, adding dynamic MSR/perf/PMT counters to the `sys` lists, running a child command mode, and invoking initialization and loop functions from `main()`.

## Notable APIs and Functions

Counter access:

- `get_msr_fd()`, `get_msr()`, `add_msr_counter()`, and `add_rapl_msr_counter()` encapsulate MSR device access and probing.
- `perf_event_open()` and `open_perf_counter()` wrap Linux perf setup.
- `read_perf_type()`, `read_perf_config()`, `read_perf_rapl_unit()`, and `read_perf_scale()` parse perf PMU sysfs metadata.
- `get_rapl_counters()`, `get_cstate_counters()`, `get_smi_aperf_mperf()`, `get_perf_llc_stats()`, `get_perf_l2_stats()`, and `perf_counter_info_read_values()` read active counter descriptors into snapshot records.
- `pmt_read_counter()` masks and shifts PMT MMIO values for a domain.

Probing and setup:

- `probe_platform_features()` and `init_perf_model_support()` select model-specific tables.
- `check_msr_driver()`, `check_msr_permission()`, and `has_perf_*_access()` decide whether privileged interfaces are usable.
- `probe_bclk()`, `probe_cst_limit()`, `probe_rapl()`, `probe_thermal()`, `probe_graphics()`, `probe_lpi()`, and `probe_intel_uncore_frequency()` discover feature availability and mark columns present.
- `linux_perf_init()`, `rapl_perf_init()`, `msr_perf_init()`, and `cstate_perf_init()` allocate source-specific read metadata and prefer perf over raw MSR where possible.

Formatting and calculations:

- `pct()` applies denominator and sanity checks, returning NaN for invalid percentages or values above 110 percent.
- `rapl_counter_get_value()` converts raw RAPL deltas to joules or watts.
- `delta_*()`, `sum_counters()`, and `compute_average()` implement interval math.
- `print_header()`, `format_counters()`, and `format_all_counters()` implement the output contract.

Diagnostics:

- `dump_*()` and `decode_*()` functions print CPUID, turbo ratio, pstate/cpuidle, power-control, RAPL, thermal, HWP, EPB, performance-limit, cstate-latency, and MSR decode information when not in quiet mode.

## Risks and Edge Cases

- The code is privilege- and hardware-dependent. MSR and many perf counters require root, `CAP_SYS_RAWIO`, permissive `perf_event_paranoid`, or specific kernel drivers. Probes must degrade cleanly when access is unavailable.
- CPU hotplug and cgroup cpuset changes are expected at runtime. `turbostat_loop()` restarts on detected changes, but stale file descriptors or partially reinitialized state are a recurring risk.
- The code migrates the process for each CPU sample. Affinity failures, isolated CPUs, container constraints, or invalid allowed CPU masks can make sampling fail or bias measurements.
- Many counters are not read atomically. Derived C1, package/core sums, and graphics/sysfs values can be skewed by collection order. The code has explicit guards for MPERF zero, TSC too slow, and percentages above 110 percent.
- RAPL energy registers can wrap. `DELTA_WRAP32()` and timer-based `per_cpu_msr_sum` mitigate 32-bit RAPL wrap, but asynchronous updates and platform-specific unit scaling are delicate.
- Buffer writes use `sprintf()` into a global `output_buffer`. The actual buffer sizing/allocation is outside this chunk, so wide dynamic counter sets or unexpectedly large output remain an integration risk.
- PMT helpers use `unsigned long` masks with shifts such as `1 << (msb + 1)` in `pmt_gen_value_mask()`. The `msb == 63` special case avoids one overflow path, but intermediate integer width and 32-bit builds should be treated carefully.
- `pmt_diriter_begin()` can leak or leave inconsistent iterator state if `opendir()` succeeds but `scandir()` fails; callers need to remove the iterator.
- `initialize_cpu_set_from_sysfs()` returns without closing the file on its successful path in this chunk, which is a file descriptor leak unless corrected elsewhere.
- Some failure handling clears BIC presence and frees fd arrays, but other paths `err()`/`exit()` immediately. Tests need to distinguish expected hard failures from optional-counter degradation.
- The chunk boundary cuts `perf_l2_init()` before all hybrid PMU branches are visible. The final per-file analysis must reconcile the continuation to assess L2 initialization fully.

## Test and Validation Signals

Build and static validation:

- Compile `turbostat.c` with the expected generated include macros for `MSRHEADER`, `INTEL_FAMILY_HEADER`, and `BUILD_BUG_HEADER`.
- Build with warnings enabled to catch format-string width mismatches, enum fallthrough omissions, pointer/integer conversions, and unchecked buffer formatting.
- Run static analysis around fd lifetime, `sprintf()` buffer sizes, PMT mask generation, and success-path close behavior.

Runtime capability tests:

- Run as root or with `CAP_SYS_RAWIO` on Intel and AMD systems and verify MSR-backed columns are present.
- Run unprivileged and with `--no-msr`/`--no-perf` to verify graceful degradation and clear warnings.
- Test with `perf_event_paranoid` settings that allow and deny hardware, msr, cstate, power, LLC, and L2 perf events.
- Test unsupported or force-loaded platforms to verify `probe_platform_features()` behavior.

Measurement tests:

- Compare `Avg_MHz`, `Busy%`, `Bzy_MHz`, and `TSC_MHz` against known CPU load changes.
- Validate RAPL watts versus joules mode and compare package/core/DRAM/GFX/PSYS values against powercap sysfs where available.
- Exercise package C-state limits and cpuidle output on platforms with and without C1 residency MSRs.
- Verify IRQ/NMI deltas against `/proc/interrupts`, graphics residency/frequency against DRM sysfs, and uncore frequency against sysfs.
- Exercise hybrid CPUs so perf PMU type selection and pcore/ecore/lcore CPU sets are used.

Resilience tests:

- Hotplug CPUs or change cgroup `cpuset.cpus.effective` while interval mode runs and verify `re_initialize()` restarts without crashing.
- Run with CPU subsets, package-only/core-only output, summary-only output, hidden/shown column groups, and dynamic counter combinations.
- Run for intervals long enough to cross RAPL wrap timing and compare timer-accumulated MSR-sum behavior.
- Send `SIGINT`, press `q`, close stdin, and use `num_iterations` to verify loop termination.

### subset-b-006779: lines 9442-11720

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
