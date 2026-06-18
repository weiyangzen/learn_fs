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
