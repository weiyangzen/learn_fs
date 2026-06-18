# subset-b-006775 Research

Grouped research report for the requested cpupower and pm-graph source files.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.c

## Purpose
Implements the cpupower powercap/RAPL library layer. It discovers the intel-rapl powercap hierarchy under `/sys/devices/virtual/powercap`, reads zone names and capability flags, exposes energy/power counters, and provides a recursive walker used by both `powercap-info` and the RAPL monitor.

## Important APIs, Types, and Functions
Key entry points are `powercap_get_enabled`, `powercap_get_driver`, `powercap_init_zones`, `powercap_read_zone`, `powercap_walk_zones`, and the 64-bit readers `powercap_get_energy_uj`, `powercap_get_power_uw`, `powercap_get_max_energy_range_uj`, and `powercap_get_max_power_range_uw`. Internal helpers `sysfs_read_file`, `sysfs_get_enabled`, and `sysfs_powercap_get64_val` hide low-level open/read parsing.

## Control Flow, State, and Persistence
`powercap_init_zones` first requires `/intel-rapl/enabled` to read as enabled, allocates a root `powercap_zone`, seeds `sys_name` as `intel-rapl/intel-rapl:0`, and calls `powercap_read_zone`. `powercap_read_zone` opens the zone directory, reads its `name`, marks whether energy/power files can be read, scans child `intel-rapl:*` directories, allocates child structs, links parent/children pointers, and recurses with tree depth tracking. State is entirely live sysfs data plus heap-allocated zone trees; no persistent storage is written. `powercap_set_enabled` and `powercap_zone_set_enabled` are stubs returning success without writing sysfs.

## Dependencies and Integration Points
Depends on Linux powercap sysfs, the `powercap.h` struct contract, libc directory/stat APIs, and callers in `utils/powercap-info.c` and `utils/idle_monitor/rapl_monitor.c`. The code is intentionally hardwired to intel-rapl even though powercap is a generic kernel class.

## Risks and Test Signals
Path construction uses fixed 255-byte buffers with unchecked `strcat` in several places, so deep or unexpected sysfs names could overflow despite some checks. `stat(dent->d_name)` is relative to cwd before falling back to `fstatat`, which is harmless but odd. Child allocation failures can leak already-built subtrees, and no destructor is provided. Validate with systems where RAPL is enabled/disabled, nested package/core/uncore zones, missing energy files, artificially long names, and `cpupower powercap-info` plus `cpupower monitor -m RAPL` smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.h

## Purpose
Defines the public cpupower powercap/RAPL interface and the in-memory zone tree representation consumed by powercap reporting and monitoring code.

## Important APIs, Types, and Functions
Important constants are `PATH_TO_POWERCAP`, `PATH_TO_RAPL`, `POWERCAP_MAX_CHILD_ZONES`, `POWERCAP_MAX_TREE_DEPTH`, `MAX_LINE_LEN`, and `SYSFS_PATH_MAX`. `struct powercap_zone` stores printable `name`, sysfs-relative `sys_name`, tree depth, parent pointer, up to 10 children, and bitfields advertising available `power_uw` and `energy_uj` counters. Function declarations cover discovery, walking, enabled-state reads/writes, driver lookup, and 64-bit counter reads.

## Control Flow, State, and Persistence
This header has no runtime control flow. It defines the heap object layout filled by `powercap.c`; callers retain raw pointers into that tree and there is no ownership helper for freeing it. State is bounded by static constants, which influence recursive discovery and report indentation.

## Dependencies and Integration Points
Included directly by `powercap.c`, `powercap-info.c`, and `rapl_monitor.c`. The interface maps Linux powercap sysfs files into a generic-looking API, but the paths and comments reflect an intel-rapl-only implementation.

## Risks and Test Signals
The fixed child and path limits can truncate future hardware topologies. The write APIs are declared even though current implementations are no-ops, which can mislead callers. Tests should compile all users against this header, verify struct field assumptions in RAPL monitor/reporting, and exercise a zone tree at the maximum child/depth boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/lib/powercap.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/builtin.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/builtin.h

## Purpose
Declares the subcommand entry points linked into the `cpupower` command dispatcher.

## Important APIs, Types, and Functions
Exports prototypes for `cmd_set`, `cmd_info`, `cmd_freq_set`, `cmd_freq_info`, `cmd_idle_set`, `cmd_idle_info`, `cmd_cap_info`, `cmd_cap_set`, and `cmd_monitor`. Each follows the `argc, argv` command-main convention expected by `utils/cpupower.c`.

## Control Flow, State, and Persistence
The file carries no state. Its control role is compile-time coupling: adding or removing a subcommand requires keeping this header, the concrete command source, and the `commands[]` dispatch table synchronized.

## Dependencies and Integration Points
Integrated by `cpupower.c` and implemented across `cpufreq-*`, `cpuidle-*`, `cpupower-*`, `powercap-info.c`, and `idle_monitor/cpupower-monitor.c`.

## Risks and Test Signals
Several implementation files define parameters as `char **argv` while this header declares `const char **argv`, which relies on permissive C compilation and can produce warnings. Build tests should compile the full utility with strict warnings and invoke `cpupower help` to confirm command table/prototype coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/builtin.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-info.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-info.c

## Purpose
Implements `cpupower frequency-info`, reporting cpufreq driver, policy, limits, current frequency, governors, related/affected CPUs, statistics, boost state, EPP, latency, and AMD pstate performance capabilities.

## Important APIs, Types, and Functions
Important helpers include `count_cpus`, `proc_cpufreq_output`, `print_duration`, `get_boost_mode_x86`, `get_boost_mode_generic`, `get_freq_kernel`, `get_freq_hardware`, `get_hardware_limits`, `get_driver`, `get_policy`, `get_available_governors`, `get_affected_cpus`, `get_related_cpus`, `get_freq_stats`, `get_epp`, `get_latency`, `get_perf_cap`, `debug_output_one`, and command entry `cmd_freq_info`.

## Control Flow, State, and Persistence
`cmd_freq_info` parses exactly one output-specific option, with `--human` and `--no-rounding` as modifiers. If no CPU mask was supplied it selects global `base_cpu`; `--proc` rejects `--cpu`. It iterates selected CPUs, skips offline CPUs using sysfs, and invokes the selected getter. The default debug mode aggregates many getters. The file reads live sysfs/MSR data only and persists nothing.

## Dependencies and Integration Points
Depends on libcpupower cpufreq APIs, `helpers/sysfs.h`, global CPU masks and `cpupower_cpu_info` from `helpers.h`, MSR/AMD helper routines, and gettext macros. It integrates with main option parsing through `builtin.h` and global `cpus_chosen`.

## Risks and Test Signals
Linked-list cleanup is fragile because some loops advance list pointers before calling put functions, potentially losing the head if the put routine expects it. `get_freq_stats` divides by `total_time` without an explicit zero guard. Hardware frequency and boost queries require root/MSR support on many systems. Validate option exclusivity, offline CPU handling, sysfs-only non-x86 behavior, AMD pstate output, Intel turbo ratio output, and `--proc` compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-set.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-set.c

## Purpose
Implements `cpupower frequency-set`, changing cpufreq minimum, maximum, governor, or fixed userspace frequency for selected CPUs.

## Important APIs, Types, and Functions
Key pieces are option table `set_opts`, `string_to_frequency` for parsing units from Hz through THz into kHz, `do_new_policy`, `do_one_cpu`, and `cmd_freq_set`. The command uses `cpufreq_set_frequency`, `cpufreq_modify_policy_min/max/governor`, `cpufreq_get_policy`, `cpufreq_set_policy`, and related-CPU discovery APIs.

## Control Flow, State, and Persistence
Parsing rejects duplicate options, invalid units, and mixing fixed `--freq` with policy options. With no global `--cpu` mask it sets all CPUs. With `--related`, it expands the selected bitmask to CPUs returned by `cpufreq_get_related_cpus`. It snapshots online/offline state with `get_cpustate`, applies each change only to online selected CPUs, and reports skipped offline CPUs. All state changes are kernel/sysfs cpufreq policy writes; no repository files are persisted.

## Dependencies and Integration Points
Depends on libcpupower cpufreq and cpuidle headers, global bitmasks from `cpupower.c`, and helper output routines. It is root-gated by the main dispatcher.

## Risks and Test Signals
Frequency parsing is hand-rolled and sensitive to rounding, leading zeros, multiple decimal points, and buffer length. Related-CPU list iteration may lose the original head before freeing depending on lib API expectations. Setting all CPUs can partially succeed before a later CPU fails. Test with unit-suffixed frequencies, duplicate options, offline CPUs, related policy domains, unavailable userspace governor, and invalid governor names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpufreq-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-info.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-info.c

## Purpose
Implements `cpupower idle-info`, reporting cpuidle driver/governor and per-CPU idle state names, descriptions, latency, residency, usage, and accumulated time.

## Important APIs, Types, and Functions
Important functions are `cpuidle_cpu_output`, `cpuidle_general_output`, `proc_cpuidle_cpu_output`, `cpuidle_exit`, and `cmd_idle_info`. It calls libcpuidle APIs such as `cpuidle_state_count`, `cpuidle_state_name`, `cpuidle_state_desc`, `cpuidle_state_latency`, `cpuidle_state_residency`, `cpuidle_state_usage`, `cpuidle_state_time`, `cpuidle_get_driver`, and `cpuidle_get_governor`.

## Control Flow, State, and Persistence
`cmd_idle_info` parses `--silent` and `--proc`, rejects multiple output modes, defaults the CPU mask to `base_cpu`, prints general driver/governor data for normal mode, then loops selected CPUs and skips offline entries. `--proc` emits a legacy `/proc/acpi/processor`-style layout. The file only reads sysfs-backed cpuidle state and does not persist data.

## Dependencies and Integration Points
Depends on libcpuidle, `helpers/sysfs.h`, global CPU mask/base CPU state, and gettext helpers. It shares selection semantics with other cpupower subcommands.

## Risks and Test Signals
`cpuidle_exit(int fail)` ignores its argument and always exits failure, which is acceptable only for current error paths. The hard-coded `max_allowed_cstate` in proc output is synthetic. Validate kernels without cpuidle, offline CPUs, disabled-state visibility, silent mode, proc compatibility output, and memory ownership for returned state strings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-set.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-set.c

## Purpose
Implements `cpupower idle-set`, enabling or disabling cpuidle states by explicit state index, by maximum latency threshold, or by enabling all disabled states.

## Important APIs, Types, and Functions
Key API is `cmd_idle_set`; options are `--disable`, `--enable`, `--disable-by-latency`, and `--enable-all`. It uses `cpuidle_state_count`, `cpuidle_is_state_disabled`, `cpuidle_state_latency`, and `cpuidle_state_disable` plus global CPU state helpers.

## Control Flow, State, and Persistence
The command parses exactly one action. With no selected CPU mask it targets all CPUs, snapshots online/offline state, skips offline CPUs, and for each online CPU applies the requested state mutation. The latency mode disables enabled states whose latency is at or above the threshold and re-enables disabled states below the threshold. Persistence is entirely through kernel cpuidle sysfs `disable` files.

## Dependencies and Integration Points
Depends on libcpuidle/libcpufreq headers, global bitmask state, and helper routines from `helpers.h`. The main dispatcher requires root for this command.

## Risks and Test Signals
No action defaults to the `default` switch branch and exits as invalid; callers must pass one mutation option. Error handling reports per-state failures but often continues, so partial changes are possible. Test invalid numeric arguments, unsupported disable files, threshold boundary behavior, offline CPUs, and all-state re-enable on kernels with mixed disabled states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpuidle-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-info.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-info.c

## Purpose
Implements the generic `cpupower info` command, currently focused on Intel energy performance bias reporting.

## Important APIs, Types, and Functions
Important pieces are option table `set_opts`, `print_wrong_arg_exit`, and `cmd_info`. The only supported option is `--perf-bias`/`-b`, which calls `cpupower_intel_get_perf_bias` after checking root privileges and `CPUPOWER_CAP_PERF_BIAS`.

## Control Flow, State, and Persistence
The command rejects POWER machines by uname, initializes locale, parses options, defaults the selected CPU mask to `base_cpu`, then iterates selected online CPUs and prints `perf-bias`. It reads `/sys/devices/system/cpu/cpuX/power/energy_perf_bias` via helper code and does not persist anything.

## Dependencies and Integration Points
Depends on `helpers/helpers.h`, `helpers/sysfs.h`, global CPU masks, global `cpupower_cpu_info`, and the main dispatcher. It complements `cpupower-set.c` for the write side.

## Risks and Test Signals
The default `params.params = 0x7` does not correspond to only defined bitfields and then early returns when `perf_bias` is not set, making default `cpupower info` effectively a no-op. Test unsupported architectures, non-root invocation, CPUs offline, unsupported perf-bias capability, and successful per-CPU reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-set.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-set.c

## Purpose
Implements the generic `cpupower set` command for performance bias, energy performance preference, AMD pstate mode, and turbo/boost toggles.

## Important APIs, Types, and Functions
Key entry point is `cmd_set`. Options are `--perf-bias`, `--epp`, `--amd-pstate-mode`, `--turbo-boost`, and alias `--boost`. It calls `cpupower_intel_set_perf_bias`, `cpupower_set_epp`, `cpupower_set_amd_pstate_mode`, `cpupower_set_intel_turbo_boost`, and `cpupower_set_generic_turbo_boost`.

## Control Flow, State, and Persistence
After rejecting POWER machines and parsing options, command-level settings such as AMD pstate mode and turbo boost are applied once. Then, with no selected CPU mask, it targets all CPUs and iterates online selected CPUs for per-CPU perf-bias and EPP writes. State changes persist in kernel sysfs/MSR-backed interfaces until changed by the kernel, firmware, or later user commands.

## Dependencies and Integration Points
Depends on global CPU vendor/capability discovery, sysfs helpers, bitmask helpers, and root gating in the main dispatcher. The boost path integrates Intel-specific `intel_pstate/no_turbo` with a generic `/sys/devices/system/cpu/cpufreq/boost` fallback.

## Risks and Test Signals
Partial updates are possible if one CPU write fails after previous CPUs succeeded. AMD mode validation only checks vendor and string length, leaving mode validity to sysfs. The `--boost` alias shares the same short option as `--turbo-boost`. Test range validation, invalid EPP/mode strings, Intel and generic boost paths, offline CPUs, and mixed CPU masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower-set.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower.c

## Purpose
Provides the `cpupower` top-level executable: global option parsing, command dispatch, CPU mask setup, root checks, CPU capability discovery, version/help, and optional MSR module loading.

## Important APIs, Types, and Functions
Important globals are `cpupower_cpu_info`, `run_as_root`, `base_cpu`, `cpus_chosen`, `online_cpus`, and `offline_cpus`. The command table maps command names to functions from `builtin.h` and records whether root is required. Key functions are `print_help`, `print_man_page`, `cmd_help`, `print_version`, `handle_options`, and `main`.

## Control Flow, State, and Persistence
`main` allocates bitmasks sized by configured processors, strips global options, selects the subcommand, initializes locale, rewrites `cmd --help` into `help cmd`, finds `base_cpu` via `sched_getcpu`, populates CPU info, optionally `modprobe`s `msr` on x86_64 root runs, then dispatches the matching command after checking root requirements. It frees global bitmasks only after successful dispatch; unknown commands exit after printing help.

## Dependencies and Integration Points
Depends on all subcommand objects, helper bitmask and CPU info APIs, gettext package macros, `/proc/cpuinfo`, `/dev/cpu/*/msr`, and man pages named `cpupower[-subcommand]`.

## Risks and Test Signals
`handle_options` only recognizes global options before the command; later global-looking options belong to subcommands. `system("modprobe msr")` is a privileged side effect. Allocation failures for bitmasks are not checked before use. Test help/version flows, CPU list parsing including `all`, non-root root-required commands, systems without `/dev/cpu/*/msr`, and unknown command behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/cpupower.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/amd.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/amd.c

## Purpose
Contains x86 AMD/Hygon helper logic for decoding hardware P-states, boost state counts, and AMD pstate performance/frequency data for cpupower reports.

## Important APIs, Types, and Functions
Important elements are `union core_pstate`, `get_did`, `get_cof`, `decode_pstates`, `amd_pci_get_num_boost_states`, `amd_pstate_boost_init`, and `amd_pstate_show_perf_and_freq`. It reads MSRs `MSR_AMD_PSTATE_LIMIT`/`MSR_AMD_PSTATE*`, PCI D18F4 boost registers, cpufreq sysfs AMD pstate files, and ACPI CPPC values.

## Control Flow, State, and Persistence
`decode_pstates` checks AMD hardware pstate capability, reads the pstate limit, folds in boost states, reads each pstate MSR, skips disabled entries, and computes MHz based on family-specific FID/DID formats. AMD pstate boost support compares highest and nominal performance, then active state compares cpufreq max with AMD pstate max. The file keeps no persistent state.

## Dependencies and Integration Points
Depends on x86-only CPUID capabilities in `cpupower_cpu_info`, `read_msr`, libpci helpers, cpufreq sysfs access, and `acpi_cppc.h`. It feeds `frequency-info --boost` and AMD pstate performance output.

## Risks and Test Signals
Family-specific bitfield decoding is brittle for new CPU families. PCI access assumes domain/bus/slot/function layout used by older AMD platforms. Missing MSR or sysfs access causes feature output to disappear. Validate on pre-family-17h, family 17h+, family 1Ah+, AMD pstate enabled systems, Hygon systems, and non-x86 builds where the file is excluded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/amd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.c

## Purpose
Provides a small embedded CPU bitmask implementation used for cpupower CPU selection and online/offline CPU reporting.

## Important APIs, Types, and Functions
Public APIs are `bitmask_alloc`, `bitmask_free`, `bitmask_setbit`, `bitmask_setall`, `bitmask_clearall`, `bitmask_isallclear`, `bitmask_isbitset`, `bitmask_first`, `bitmask_last`, `bitmask_next`, `bitmask_parselist`, and `bitmask_displaylist`. Internal helpers implement word layout, token scanning, and range emission.

## Control Flow, State, and Persistence
Masks are heap allocated as arrays of unsigned long sized by bit count. Parsing clears the mask first, accepts comma-separated numbers/ranges with optional stride, rejects out-of-range and malformed terms, and leaves the mask clear on error. Display collapses consecutive set bits into ranges. State lives only in caller-owned heap objects.

## Dependencies and Integration Points
Used by `cpupower.c`, frequency/idle setters, monitor filtering, and helper CPU state routines. The layout intentionally follows kernel affinity bitmask word ordering rather than byte arrays.

## Risks and Test Signals
`while (p = q, q = nexttoken(...), p)` relies on assignment in condition and can trigger warnings. A stride of zero is not explicitly rejected and can create an infinite loop for input like `0-3:0`. Allocation users often do not handle NULL. Test parser success/failure cases, stride zero, max CPU boundary, display buffer truncation, and empty masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.h

## Purpose
Declares the local bitmask type and operations used throughout cpupower for CPU lists.

## Important APIs, Types, and Functions
Defines `struct bitmask` with a bit count and unsigned-long storage pointer, plus allocation, free, mutation, query, parsing, and display prototypes.

## Control Flow, State, and Persistence
The header has no runtime flow. It exposes ownership rules implicitly: callers allocate masks, pass them to helpers, and must free them. Parser/display semantics are defined by `bitmask.c`.

## Dependencies and Integration Points
Included by the top-level dispatcher and most CPU-selection-aware subcommands. It avoids depending on external libbitmask availability.

## Risks and Test Signals
Because the struct is public, callers could mutate internals directly. Tests should build all users and cover ABI expectations for parser and display formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/bitmask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/cpuid.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/cpuid.c

## Purpose
Extracts CPU vendor/family/model/stepping and cpupower capability bits from `/proc/cpuinfo` and CPUID.

## Important APIs, Types, and Functions
Exports CPUID register helpers `cpuid_eax`, `cpuid_ebx`, `cpuid_ecx`, `cpuid_edx` on x86 and `get_cpu_info` on all builds. It sets capability bits including invariant TSC, APERF/MPERF, AMD CPB, Intel perf bias, turbo ratio support, Sandy/Ivy Bridge classification, AMD RDPRU, AMD hardware pstate, AMD pstate definition, CPB MSR, and AMD pstate driver active.

## Control Flow, State, and Persistence
`get_cpu_info` initializes fields to unknown, reads `/proc/cpuinfo` until it reaches global `base_cpu`, fills identity fields, then augments capabilities with CPUID leaves. AMD pstate active state masks out older AMD boost/pstate capability paths so later code prefers amd-pstate sysfs/CPPC behavior. No persistent state is written; the caller stores results in global `cpupower_cpu_info`.

## Dependencies and Integration Points
Depends on `/proc/cpuinfo`, GCC `<cpuid.h>` on x86, global `base_cpu`, and helper `cpupower_amd_pstate_enabled`. Its output drives frequency info, boost control, monitor registration, and MSR/PCI logic.

## Risks and Test Signals
Parsing is x86 `/proc/cpuinfo` format specific and has no CPUID-only fallback if procfs is missing. New Intel models may not get turbo ratio classification until tables are updated. Test Intel, AMD, Hygon, non-x86, missing `/proc/cpuinfo`, AMD pstate enabled/disabled, and offline base CPU scenarios.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/cpuid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/helpers.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/helpers.h

## Purpose
Central utility header for cpupower internationalization, global process state, CPU capability declarations, x86-only MSR/PCI/AMD helper declarations, non-x86 stubs, and common CPU-state output helpers.

## Important APIs, Types, and Functions
Key definitions include `_`/`N_` gettext macros, global `run_as_root`, `base_cpu`, `cpus_chosen`, `online_cpus`, `offline_cpus`, `enum cpupower_cpu_vendor`, `CPUPOWER_CAP_*` flags, `CPUPOWER_AMD_CPBDIS`, `MAX_HW_PSTATES`, `struct cpupower_cpu_info`, and prototypes for CPU info, boost, MSR, PCI, AMD pstate, CPUID, CPU state, and `print_speed`.

## Control Flow, State, and Persistence
This file has compile-time control flow through x86 vs non-x86 sections. On non-x86, hardware-specific functions are inline stubs returning failure or zero so generic code can compile while features degrade gracefully. It declares process-wide state owned by `cpupower.c`.

## Dependencies and Integration Points
Included by nearly every cpupower utility source and monitor. It bridges libcpupower headers, libpci, gettext, and platform-specific helper implementations.

## Risks and Test Signals
Global state makes commands non-reentrant and hard to test in isolation. The unconditional `extern int be_verbose` appears even outside DEBUG after a static inline dprint definition, which can confuse strict builds. Test x86 and non-x86 compilation, DEBUG/NLS combinations, and command behavior when hardware helper stubs are active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/misc.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/misc.c

## Purpose
Implements miscellaneous cpupower helpers for boost support/control, Intel perf bias, EPP, AMD pstate mode detection/control, CPU online/offline mask population, and human-readable frequency printing.

## Important APIs, Types, and Functions
Important APIs are `cpufreq_has_x86_boost_support`, `cpupower_set_intel_turbo_boost`, `cpupower_intel_get_perf_bias`, `cpupower_intel_set_perf_bias`, `cpupower_set_epp`, `cpupower_set_amd_pstate_mode`, `cpupower_amd_pstate_enabled`, `cpufreq_has_generic_boost_support`, `get_cpustate`, `print_online_cpus`, `print_offline_cpus`, `print_speed`, and `cpupower_set_generic_turbo_boost`.

## Control Flow, State, and Persistence
Boost support is selected from CPU capability flags: AMD CPB via MSR or PCI, AMD pstate via sysfs/CPPC, Intel IDA via `intel_pstate/no_turbo`, otherwise generic `/sys/devices/system/cpu/cpufreq/boost`. Per-CPU writes target sysfs files. CPU-state helpers clear and repopulate global masks from `cpus_chosen`. No files are created, but sysfs writes change live kernel policy.

## Dependencies and Integration Points
Depends on `helpers.h`, `helpers/sysfs.h`, cpufreq APIs, `cpupower_intern.h` for sysfs read/write helpers, MSR helpers, AMD helpers, and global CPU info/masks.

## Risks and Test Signals
Several mallocs in print helpers are not freed, though command lifetime is short. `print_speed` with rounding disabled has no branch for exactly 1000 or 1000000 kHz edge values. Sysfs writes use fixed buffer lengths rather than string length. Validate Intel/generic boost paths, AMD pstate mode, EPP writes, offline CPU reporting, and frequency formatting boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/misc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/msr.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/msr.c

## Purpose
Provides x86 MSR read/write helpers and Intel turbo ratio lookup for cpupower.

## Important APIs, Types, and Functions
Key APIs are `read_msr`, `write_msr`, and `msr_intel_get_turbo_ratio`. The code knows MSR constants for perf status, misc enables, and Nehalem turbo ratio limit, though only the turbo ratio constant is used here.

## Control Flow, State, and Persistence
`read_msr` and `write_msr` open `/dev/cpu/<cpu>/msr`, seek to the MSR index, transfer an unsigned long long, close the descriptor, and return 0 or -1. `msr_intel_get_turbo_ratio` checks `CPUPOWER_CAP_HAS_TURBO_RATIO` before reading `MSR_NEHALEM_TURBO_RATIO_LIMIT`. No persistent state is kept, but writes would mutate processor MSR state.

## Dependencies and Integration Points
Depends on x86 builds, global `cpupower_cpu_info`, the kernel `msr` driver, root privileges for many MSRs, and callers in boost/frequency/monitor code.

## Risks and Test Signals
Uses `lseek(..., SEEK_CUR)` on a fresh descriptor, equivalent to absolute from zero but less explicit than `SEEK_SET`. Errors do not preserve detailed errno for callers. Test missing msr module, non-root access, nonexistent CPUs, unsupported MSRs, and turbo ratio reporting on supported Intel models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/pci.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/pci.c

## Purpose
Wraps libpci initialization and filtering for cpupower AMD hardware helpers and monitors.

## Important APIs, Types, and Functions
Exports `pci_acc_init` and `pci_slot_func_init`. `pci_acc_init` allocates a `pci_access`, configures a filter for domain/bus/slot/function/vendor/device where -1 means wildcard, initializes/scans the bus, and returns the first matching `pci_dev`. `pci_slot_func_init` targets root domain/bus by slot/function.

## Control Flow, State, and Persistence
The returned `pci_dev` remains owned by the `pci_access` object returned through `pacc`; callers must call `pci_cleanup`. If no device matches, the helper cleans up and returns NULL. No persistent data is written.

## Dependencies and Integration Points
Depends on libpci and x86-only compilation. Used by AMD boost-state and family 12h/14h idle monitor code.

## Risks and Test Signals
Only the first matching device is returned. The root-domain helper assumes domain 0/bus 0, which is not universal. Test systems with missing PCI access, nonzero domains, multiple matching devices, and callers correctly cleaning up `pci_access`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.c

## Purpose
Implements cpupower sysfs helpers for CPU online state, cpuidle per-state attributes, cpuidle driver/governor strings, and legacy scheduler tunable stubs.

## Important APIs, Types, and Functions
Important APIs are `sysfs_read_file`, `sysfs_is_cpu_online`, `sysfs_idlestate_file_exists`, `sysfs_idlestate_read_file`, `sysfs_is_idlestate_disabled`, `sysfs_idlestate_disable`, `sysfs_get_idlestate_latency`, `sysfs_get_idlestate_usage`, `sysfs_get_idlestate_time`, `sysfs_get_idlestate_name`, `sysfs_get_idlestate_desc`, `sysfs_get_idlestate_count`, `sysfs_get_cpuidle_governor`, `sysfs_get_cpuidle_driver`, `sysfs_get_sched`, and `sysfs_set_sched`.

## Control Flow, State, and Persistence
Helpers build paths under `/sys/devices/system/cpu/`, read numeric/string files, trim string newlines, and write `disable` values for idle states. `sysfs_is_cpu_online` treats missing `cpuX/online` as online for kernels without CPU hotplug. `sysfs_get_idlestate_count` counts contiguous `stateN` directories. Scheduler helpers return `-ENODEV`, reflecting removed or unsupported knobs. State changes are limited to cpuidle disable sysfs writes.

## Dependencies and Integration Points
Depends on Linux CPU/cpuidle sysfs layout and is used by libcpuidle wrappers, idle/frequency commands, and helper CPU state routines.

## Risks and Test Signals
`sysfs_idlestate_disable` writes `sizeof(disable)` bytes from a text buffer, which can include extra NUL bytes instead of string length. Numeric parsing does not always reset errno. State counting assumes contiguous indices. Test hotplug/no-hotplug kernels, missing cpuidle, unsupported disable files, read-only sysfs, current_governor_ro fallback, and string allocation/free behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.h

## Purpose
Declares sysfs constants and cpupower helper functions for CPU online and cpuidle state access.

## Important APIs, Types, and Functions
Defines `PATH_TO_CPU`, `MAX_LINE_LEN`, and `SYSFS_PATH_MAX`, plus prototypes for file reads, idlestate existence/read/disable/value/string access, cpuidle governor/driver getters, and scheduler getter/setter stubs.

## Control Flow, State, and Persistence
The header carries no runtime state. It defines the path and buffer-size contract used by `sysfs.c` and its consumers.

## Dependencies and Integration Points
Included by cpufreq info, cpuidle info, cpupower set/info, and helper code. The constants must stay compatible with sysfs path construction in implementations.

## Risks and Test Signals
Fixed path buffers are small for some constructed paths. The scheduler APIs are declared but unsupported by implementation. Build tests should cover all consumers and runtime tests should verify each declared function maps to an implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/topology.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/topology.c

## Purpose
This file is only a stub/header fragment for CPU topology parsing in this tree snapshot.

## Important APIs, Types, and Functions
It includes standard headers and `<cpuidle.h>` and contains comments describing helper structs for sorting `cpupower_topology.cpu_info`, but no functions or data definitions are present in the listed content.

## Control Flow, State, and Persistence
There is no executable control flow, state, persistence, or exported API in this file as provided.

## Dependencies and Integration Points
It appears related to topology APIs consumed by `cpupower-monitor.c`, likely implemented elsewhere in the cpupower library/source set. It depends on expected cpupower topology types from headers outside this file.

## Risks and Test Signals
Risk is mainly maintenance confusion: the file name implies topology implementation, but this snapshot contributes no behavior. Build tests should confirm no missing symbol expectations are assigned to this translation unit and that topology functionality is supplied by other files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/amd_fam14h_idle.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/amd_fam14h_idle.c

## Purpose
Implements a cpupower monitor plugin for AMD family 12h/14h package C-state counters and North Bridge P1 indication using PCI configuration registers.

## Important APIs, Types, and Functions
Important functions are `amd_fam14h_get_pci_info`, `amd_fam14h_init`, `amd_fam14h_disable`, `fam14h_nbp1_count`, `fam14h_get_count_percent`, `amd_fam14h_start`, `amd_fam14h_stop`, `is_nbp1_capable`, `amd_fam14h_register`, and `amd_fam14h_unregister`. The monitor exposes `!PC0`, `PC1`, `PC6`, and optional `NBP1` states.

## Control Flow, State, and Persistence
Registration requires AMD vendor and family 0x12 or 0x14, allocates per-CPU counter arrays, opens PCI slot 0x18 function 6, and reduces state count if NBP1 is unsupported. Start enables/zeros counters; stop reads counters, disables monitor bits, computes elapsed time, and warns on overflow. State is global static monitor storage plus live PCI counter state.

## Dependencies and Integration Points
Depends on libpci, cpupower CPU info, monitor framework callbacks, and root access. Results are printed by `cpupower-monitor.c` through `cstate_t` callbacks.

## Risks and Test Signals
PCI layout is family-specific and assumes one device. Registration leaks allocated arrays if PCI initialization later fails. Percentage math depends on 80 ns ticks and 32-bit overflow window. Test on matching AMD hardware, nonmatching CPUs, no PCI access, NBP1 capable/incapable systems, and long measurement overflow warning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/amd_fam14h_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpuidle_sysfs.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpuidle_sysfs.c

## Purpose
Implements a generic cpuidle sysfs monitor plugin named `Idle_Stats`, deriving idle residency percentages from per-state `time` counters.

## Important APIs, Types, and Functions
Key functions are `cpuidle_get_count_percent`, `cpuidle_start`, `cpuidle_stop`, `fix_up_intel_idle_driver_name`, optional POWER `map_power_idle_state_name`, `cpuidle_register`, and `cpuidle_unregister`. It fills a static `cpuidle_cstates` array and monitor descriptor `cpuidle_sysfs_monitor`.

## Control Flow, State, and Persistence
Registration uses `sched_getcpu` and assumes all CPUs expose the same number of idle states. It reads names/descriptions, normalizes some Intel and POWER labels, allocates previous/current two-dimensional counter arrays, and records state callbacks. Start snapshots `cpuidle_state_time`; stop snapshots again and computes elapsed microseconds. No persistent data is written.

## Dependencies and Integration Points
Depends on libcpuidle APIs, monitor framework globals including `cpu_count`, gettext/debug helpers, and CPU naming conventions from intel_idle/powerpc drivers.

## Risks and Test Signals
`CPUIDLE_STATES_MAX` is 10 but the code does not clamp `hw_states_num`, so CPUs exposing more states could overrun `cpuidle_cstates`. Allocation failures are unchecked. Offline or heterogeneous CPUs may produce invalid reads. Test many-state systems, POWER name mapping, Intel idle names, missing cpuidle sysfs, and selected CPU subsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpuidle_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.c

## Purpose
Implements `cpupower monitor`, the framework that registers available idle/power monitors, measures over an interval or child command, and prints topology-organized tabular results.

## Important APIs, Types, and Functions
Important globals are `all_monitors`, selected `monitors`, `avail_monitors`, `cpu_count`, `mode`, `interval`, `cpu_top`, and `wake_cpus`. Key functions include `timespec_diff_us`, `print_header`, `print_results`, `parse_monitor_param`, `list_monitors`, `fork_it`, `do_interval_measure`, `cmdline`, and `cmd_monitor`.

## Control Flow, State, and Persistence
`cmd_monitor` parses monitor options, obtains topology, defaults CPU mask to all CPUs, calls every compiled monitor `do_register`, filters root-required monitors for non-root users, optionally lists or filters monitors, then starts/stops measurements around either a sleep interval or an execed child command. Results are printed by invoking each state callback. It releases topology and monitor resources at exit; state is in process memory and hardware counters only.

## Dependencies and Integration Points
Depends on `idle_monitors.def`, monitor plugin descriptors, topology APIs from libcpupower, bitmask globals, helper CPU info/root state, and POSIX fork/exec/wait/signal APIs.

## Risks and Test Signals
`-i` is declared as requiring an argument in behavior but option string uses `i:` only if present? Here `+lci:m:` makes `-i` require an argument, but errors rely on getopt. Header formatting has fixed widths and can truncate names. Child command monitoring ignores signal-exit reporting. Test list mode, monitor filtering order, non-root filtering, interval and command modes, offline CPUs, multi-package topology, and wake-cpu affinity behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.h

## Purpose
Defines the monitor plugin ABI shared by `cpupower monitor` and all idle/power monitor implementations.

## Important APIs, Types, and Functions
Important definitions are `MONITORS_MAX`, `MONITOR_NAME_LEN`, architecture-dependent `CSTATE_NAME_LEN`, `CSTATE_DESC_LEN`, `enum power_range_e`, `cstate_t`, `struct cpuidle_monitor`, `timespec_diff_us`, `print_overflow_err`, and inline `bind_cpu`.

## Control Flow, State, and Persistence
The ABI represents each monitor as start/stop/register/unregister callbacks plus an array of states. Each state reports either a percentage or raw count through callback pointers. The header also defines affinity binding used by monitors needing per-CPU synchronized reads.

## Dependencies and Integration Points
Included by monitor framework and plugin files. It pulls in `idle_monitors.h`, scheduler affinity APIs, gettext through users, and global `cpu_count`.

## Risks and Test Signals
Fixed monitor/name/state widths drive UI layout and can truncate longer labels. Callback contracts are implicit, especially around allocation lifetime and CPU indexing. Test compilation of every monitor, non-x86 builds, and table formatting for maximum name lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/cpupower-monitor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/hsw_ext_idle.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/hsw_ext_idle.c

## Purpose
Implements a Haswell-specific monitor for package C8/C9/C10 residency MSRs.

## Important APIs, Types, and Functions
Key functions are `hsw_ext_get_count`, `hsw_ext_get_count_percent`, `hsw_ext_start`, `hsw_ext_stop`, `hsw_ext_register`, and `hsw_ext_unregister`. The monitor descriptor is `intel_hsw_ext_monitor` with states `PC8`, `PC9`, and `PC10`.

## Control Flow, State, and Persistence
Registration requires Intel family 6 model 0x45. It allocates per-CPU previous/current arrays and validity flags. Start reads state MSRs for each CPU then TSC; stop reads TSC then state MSRs; percentages are residency delta divided by TSC delta. State is in static heap arrays and MSR counters.

## Dependencies and Integration Points
Depends on x86 MSR access, CPU model detection, root privileges, and monitor framework callbacks. Complements the broader SandyBridge monitor on selected Haswell systems.

## Risks and Test Signals
Only model 0x45 is recognized, so other CPUs with these MSRs may not register. `is_valid[cpu] |= !read` can mark a CPU valid if either start or stop succeeds rather than requiring both. Test matching Haswell hardware, read failures, offline CPUs, non-root filtering, and percent sanity versus turbostat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/hsw_ext_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/idle_monitors.h -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/idle_monitors.h

## Purpose
Declares all monitor plugin symbols through the shared `idle_monitors.def` list.

## Important APIs, Types, and Functions
It temporarily defines `DEF(x)` to emit `extern struct cpuidle_monitor x_monitor;`, includes `idle_monitors.def`, undefines the macro, and declares `all_monitors[]`.

## Control Flow, State, and Persistence
There is no runtime state. The file ensures the plugin list used for extern declarations stays synchronized with the framework array construction in `cpupower-monitor.c`.

## Dependencies and Integration Points
Integrated by `cpupower-monitor.h` and `cpupower-monitor.c`; requires every monitor named in `idle_monitors.def` to provide a matching `struct cpuidle_monitor` object.

## Risks and Test Signals
Build failures surface if the def list and compiled plugin objects diverge. Test all configured architecture builds and monitor list output to verify each expected plugin registers or cleanly declines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/idle_monitors.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/mperf_monitor.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/mperf_monitor.c

## Purpose
Implements the x86 APERF/MPERF monitor named `Mperf`, reporting C0 percentage, Cx percentage, and average frequency in MHz.

## Important APIs, Types, and Functions
Important functions are `mperf_get_tsc`, `get_aperf_mperf`, `mperf_init_stats`, `mperf_measure_stats`, `mperf_get_count_percent`, `mperf_get_count_freq`, `mperf_start`, `mperf_stop`, `init_maxfreq_mode`, `mperf_register`, and `mperf_unregister`. It can read APERF/MPERF through AMD RDPRU or MSRs.

## Control Flow, State, and Persistence
Registration requires `CPUPOWER_CAP_APERF` and a max-frequency mode. It prefers invariant TSC as reference on Intel and some AMD systems, otherwise uses cpufreq hardware max. Start/stop snapshot timestamps, TSC, APERF, and MPERF per CPU; callbacks compute residency and average frequency from deltas. AMD may bind the process to each CPU before reads to reduce skew.

## Dependencies and Integration Points
Depends on MSR/RDPRU access, cpufreq hardware limits, CPU vendor/capability discovery, monitor framework globals, and root access unless RDPRU path is sufficient.

## Risks and Test Signals
Division by zero is possible if MPERF or TSC deltas are zero during very short measurements or failed reads. Validity tracking uses OR at stop, so partial reads may pass. Max-frequency fallback can fail without cpufreq. Test Intel/AMD, RDPRU-capable AMD, Xen/no MSR access, short intervals, offline CPUs, and comparison to known workload frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/mperf_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/nhm_idle.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/nhm_idle.c

## Purpose
Implements an Intel Nehalem/Westmere-style MSR residency monitor for core C3/C6 and package PC3/PC6.

## Important APIs, Types, and Functions
Key functions are `nhm_get_count`, `nhm_get_count_percent`, `nhm_start`, `nhm_stop`, `intel_nhm_register`, and `intel_nhm_unregister`. The monitor descriptor is `intel_nhm_monitor` with four states.

## Control Flow, State, and Persistence
Registration requires Intel vendor, invariant TSC, and APERF capability. It allocates per-CPU arrays, snapshots residency MSRs and a base-CPU TSC at start/stop, and reports each state as delta residency divided by TSC delta. State is in process heap arrays and hardware MSRs only.

## Dependencies and Integration Points
Depends on x86 MSR access, CPU capability discovery, root access, and monitor table integration.

## Risks and Test Signals
The model check is broad, so registration may occur on Intel CPUs where these exact MSRs are not meaningful, with failures masked by validity flags. Validity uses OR at stop. Test on known Nehalem/Westmere systems, newer Intel systems, no MSR access, multi-socket systems, and output bounds below 100 percent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/nhm_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/rapl_monitor.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/rapl_monitor.c

## Purpose
Implements a `cpupower monitor` plugin named `RAPL` that reports energy deltas for powercap zones exposing `energy_uj`.

## Important APIs, Types, and Functions
Important functions are `rapl_get_count_uj`, `powercap_count_zones`, `rapl_start`, `rapl_stop`, and `rapl_register`. It uses arrays `rapl_zones`, `rapl_zones_pt`, previous/current counts, and a maximum of 10 zones.

## Control Flow, State, and Persistence
Registration verifies intel-rapl driver availability and enabled state, initializes the powercap zone tree, walks it, and adds each energy-capable zone as a monitor state. Start and stop snapshot `energy_uj`; callbacks report the delta in microjoules. No persistent state is written, but it retains pointers to the allocated powercap tree for process lifetime.

## Dependencies and Integration Points
Depends on `powercap.c`, Linux powercap sysfs, monitor framework, and x86 build gating. Unlike MSR monitors it does not require root by descriptor flag.

## Risks and Test Signals
`powercap_count_zones` prints debug-looking `sys_name` and return values to stdout, which can corrupt monitor table output. Energy counter wrap handling is not implemented. `rapl_max_count` assignment appears wrong because it compares absolute current value before storing delta. Test with nested RAPL zones, more than 10 zones, counter wrap, disabled powercap, and normal `cpupower monitor -m RAPL` output cleanliness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/rapl_monitor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/snb_idle.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/snb_idle.c

## Purpose
Implements an Intel Sandy/Ivy/Haswell MSR residency monitor for core C7 and package PC2/PC7.

## Important APIs, Types, and Functions
Key functions are `snb_get_count`, `snb_get_count_percent`, `snb_start`, `snb_stop`, `snb_register`, and `snb_unregister`. The monitor descriptor is `intel_snb_monitor` with states `C7`, `PC2`, and `PC7`.

## Control Flow, State, and Persistence
Registration requires Intel family 6 and selected models for Sandy Bridge, Ivy Bridge, and Haswell. It allocates per-CPU arrays, snapshots state MSRs and TSC at start/stop, and computes percentages from residency deltas over TSC delta. State is per-process heap plus live MSR counters.

## Dependencies and Integration Points
Depends on model tables from CPU info, MSR access, root permission, and monitor framework integration.

## Risks and Test Signals
Model coverage is manually maintained. Validity OR behavior can hide one-sided read failures. Package counters may duplicate values for CPUs in the same package but are printed per selected topology row. Test supported/unsupported models, multi-package output, no MSR access, non-root filtering, and comparison with turbostat.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/idle_monitor/snb_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/powercap-info.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/powercap-info.c

## Purpose
Implements `cpupower powercap-info`, printing the loaded powercap driver and intel-rapl zone hierarchy with enabled state and available monitoring capabilities.

## Important APIs, Types, and Functions
Important functions are `powercap_print_one_zone`, `powercap_show`, `cmd_cap_info`, and placeholder `cmd_cap_set`. Option `--all` sets global `powercap_show_all`, but the current printer does not branch on it.

## Control Flow, State, and Persistence
`cmd_cap_info` parses options, then `powercap_show` checks driver and global enabled state, initializes the zone tree, and walks it printing each zone with indentation derived from tree depth. The command reads sysfs only. `cmd_cap_set` is a no-op returning success.

## Dependencies and Integration Points
Depends on `lib/powercap.c`, `powercap.h`, helper gettext macros, and cpupower dispatch. Integrates with RAPL monitor through the same zone discovery API.

## Risks and Test Signals
The printed string says energy is monitored in micro Joules as "Power", which is imprecise. No memory is freed for the zone tree. `--all` and cap set are not functional. Test no driver, disabled powercap, zones without enabled files, nested zones, and command output under non-root users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/powercap-info.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/version-gen.sh -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/version-gen.sh

## Purpose
Generates the version string used when building cpupower utilities.

## Important APIs, Types, and Functions
It checks for a kernel git repository three directories up, tries `git describe --abbrev=4 HEAD`, refreshes the index, appends `-dirty` when the worktree differs from HEAD, normalizes hyphens to dots, otherwise reads `VERSION`, `PATCHLEVEL`, `SUBLEVEL`, and `EXTRAVERSION` from the kernel Makefile. It strips an optional leading `v` and echoes the result.

## Control Flow, State, and Persistence
The script is side-effect light except `git update-index -q --refresh`, which refreshes git index stat information. It does not write output files directly; build rules capture stdout.

## Dependencies and Integration Points
Depends on POSIX shell, git when in a git checkout, grep/tr, expr, and being run from `tools/power/cpupower/` so relative paths resolve to the kernel root.

## Risks and Test Signals
Fallback `eval` of Makefile variables assumes trusted local Makefile content. Running from another directory returns wrong paths. Test in git and exported tarball trees, dirty worktree, annotated/non-v tags, and Makefile-only version fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/utils/version-gen.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/Makefile

## Purpose
Installs the pm-graph Python tools, configs, symlinks, and man pages; there is no build step because the tools are scripts.

## Important APIs, Types, and Functions
Important variables are `DESTDIR`, `BINDIR`, `MANDIR`, `LIBDIR`, `INSTALL`, and `INSTALL_DATA`. Targets are `all`, `install`, `uninstall`, and `help`.

## Control Flow, State, and Persistence
`all` prints that nothing is built. `install` first runs `uninstall`, creates `$(LIBDIR)/pm-graph` and config directories, installs `sleepgraph.py`, `bootgraph.py`, selected config files, creates `bootgraph` and `sleepgraph` symlinks in `$(BINDIR)`, and installs man pages. `uninstall` removes those paths and attempts to remove empty directories. Persistent state is the installed filesystem layout.

## Dependencies and Integration Points
Depends on `/usr/bin/install`, `ln`, `rm`, `rmdir`, Python source files, config files, and man pages in the same directory. It is used by package builds and `install_latest_from_github.sh`.

## Risks and Test Signals
`install: uninstall` can remove existing packaged files before reinstalling, which is risky with shared DESTDIR mistakes. Symlink targets assume `/usr/bin` to `/usr/lib` relative layout. `uninstall` removes all config files under the pm-graph config dir. Test `make DESTDIR=/tmp/pkg install`, symlink validity, uninstall idempotence, and packaging with non-default `LIBDIR`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/bootgraph.py -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/bootgraph.py

## Purpose
Implements BootGraph, a Python tool that captures or reprocesses Linux boot `dmesg` and optional function-graph ftrace logs, then emits an HTML boot timeline through shared `sleepgraph` library facilities.

## Important APIs, Types, and Functions
Important classes are `SystemValues` and `Data`. Major functions include `parseKernelLog`, `parseTraceLog`, `retrieveLogs`, `colorForName`, `cgOverview`, `createBootGraph`, `updateCron`, `updateGrub`, `updateKernelParams`, `doError`, and `printHelp`. The main block parses options for ftrace/callgraph, reboot automation, log replay, output, bootloader update, and utility commands.

## Control Flow, State, and Persistence
For a normal run it root-checks, optionally verifies ftrace, captures dmesg/ftrace into an output directory, parses initcall start/end messages into kernel/user phases, associates ftrace callgraphs with initcalls, generates timeline HTML/CSS/JS, stores hidden logs when requested, and writes result fields. Reboot mode mutates `/etc/default/grub`, runs grub update, installs an `@reboot` root cron entry, reboots, then cronjob mode restores cron/grub and disables tracing. Persistent effects can include output directories, result files, cron changes, grub changes, and ftrace state.

## Dependencies and Integration Points
Depends heavily on `sleepgraph.py` as `aslib`, Linux `/proc`, dmesg, debugfs/tracefs ftrace, grub tooling, crontab, root privileges, and standard Python modules. Installed by pm-graph Makefile as `bootgraph`.

## Risks and Test Signals
Bootloader/cron mutation is high risk and should be tested only in controlled environments. HTML generation embeds parsed names with limited escaping; dmesg log escaping omits semicolons. Parsing assumes initcall_debug log formats and stops after 120 seconds. Test replay mode with fixture dmesg/ftrace, no initcall data errors, manual reboot output, ftrace filter validation, grub restore paths, and output ownership under sudo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/bootgraph.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/custom-timeline-functions.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/custom-timeline-functions.cfg

## Purpose
Provides a sleepgraph configuration file for the custom timeline/dev kprobe override preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically enables dev timeline functions, disables callgraph, sets output suffix `custom`, and overrides both default timeline function sets with explicit x86_64 kprobe entries for suspend/resume milestones and selected device delay functions.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/custom-timeline-functions.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/example.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/example.cfg

## Purpose
Provides a sleepgraph configuration file for the full annotated example preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically documents broad sleepgraph settings, enables addlogs, sync, gzip, result output, and shows commented examples for runtime suspend, display, multi-run, command override, buffers, filters, and debug/callgraph tuning.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/example.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-callgraph.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-callgraph.cfg

## Purpose
Provides a sleepgraph configuration file for the S2 freeze full-callgraph preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: freeze` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses freeze mode, callgraph true, microsecond precision, minimum device/callgraph length of 1 ms, and warns output can exceed 30 MB.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-callgraph.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-dev.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-dev.cfg

## Purpose
Provides a sleepgraph configuration file for the S2 freeze dev timeline preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: freeze` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses freeze mode with `dev: true`, callgraph false, 1 ms device threshold, and millisecond timestamp precision.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze-dev.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze.cfg

## Purpose
Provides a sleepgraph configuration file for the generic S2 freeze preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: freeze` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses freeze mode with no dev/proc/callgraph extras, 0.001 ms device threshold, and millisecond precision.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/freeze.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-callgraph.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-callgraph.cfg

## Purpose
Provides a sleepgraph configuration file for the S1 standby full-callgraph preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: standby` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses standby mode, callgraph true, 1 ms thresholds, and microsecond precision.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-callgraph.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-dev.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-dev.cfg

## Purpose
Provides a sleepgraph configuration file for the S1 standby dev timeline preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: standby` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses standby mode with source-function/dev timeline enabled and callgraph disabled.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby-dev.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby.cfg

## Purpose
Provides a sleepgraph configuration file for the generic S1 standby preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: standby` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses standby mode with default-style low overhead tracing and no dev/callgraph/proc output.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/standby.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-callgraph.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-callgraph.cfg

## Purpose
Provides a sleepgraph configuration file for the S3 suspend-to-RAM full-callgraph preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses mem mode, callgraph true, maxdepth 5, microsecond precision, and low device threshold.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-callgraph.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-dev.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-dev.cfg

## Purpose
Provides a sleepgraph configuration file for the S3 suspend-to-RAM dev timeline preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses mem mode with `dev: true`, callgraph false, 1 ms device threshold, and millisecond precision.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-dev.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-x2-proc.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-x2-proc.cfg

## Purpose
Provides a sleepgraph configuration file for the S3 double-run process timeline preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses mem mode with process timeline enabled, `x2: true`, 1000 ms x2/pre/post delays, and output suffix `x2-proc`.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend-x2-proc.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend.cfg -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend.cfg

## Purpose
Provides a sleepgraph configuration file for the generic S3 suspend-to-RAM preset. It lets users run a repeatable power-management trace without spelling every command-line option manually.

## Important APIs, Types, and Functions
The active API is the `[Settings]` key/value contract consumed by `sleepgraph.py -config`. This file sets `mode: mem` plus common fields such as `verbose`, `output-dir`, `rtcwake`, `addlogs`, `srgap`, `proc`, `dev`, `x2`, delays, `mindev`, `callgraph`, `expandcg`, `mincg`, and `timeprec` as applicable. This preset specifically uses mem mode with no dev/proc/callgraph extras, rtcwake 15 seconds, low device threshold, and millisecond precision.

## Control Flow, State, and Persistence
There is no executable control flow in the config itself. At runtime sleepgraph parses these settings, configures suspend/resume capture, ftrace/kprobe/callgraph behavior, output naming, and optional log inclusion. Persistent effects are produced by sleepgraph: output directories, HTML, dmesg/ftrace logs, result files, and temporary ftrace settings.

## Dependencies and Integration Points
Depends on sleepgraph configuration parsing and Linux suspend modes. The mode must be supported by `/sys/power/state`; ftrace/dev/callgraph options depend on tracefs/debugfs and kernel symbols. Installed by the pm-graph Makefile for packaged presets.

## Risks and Test Signals
Config drift is the main risk: comments and sleepgraph parser defaults must stay aligned. Callgraph presets can produce very large output and heavy tracing overhead. Device/function presets can silently miss data when kernel symbol names change. Test with `sleepgraph.py -config <file> -manual` or replay-safe dry runs, verify output-dir expansion, supported suspend mode, ftrace availability, and resulting HTML/log generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/config/suspend.cfg -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/install_latest_from_github.sh -->
# sources/distributed-fs/ceph-client/tools/power/pm-graph/install_latest_from_github.sh

## Purpose
Convenience installer that clones the upstream Intel pm-graph repository into a temporary directory and runs `sudo make install` from that checkout.

## Important APIs, Types, and Functions
Important logic creates `OUT` with `mktemp -d`, defines `cleanup`, runs `git clone http://github.com/intel/pm-graph.git $OUT/pm-graph`, checks for `sleepgraph.py`, runs `sudo make install`, prints success/failure, invokes `sleepgraph -v` on success, and removes the temporary clone.

## Control Flow, State, and Persistence
The script mutates system installation paths through upstream `make install`, not the local repository. Temporary state is under the mktemp directory and is removed by `cleanup` on normal paths after clone validation/install. It does not use shell traps, so abrupt termination can leave the temp directory.

## Dependencies and Integration Points
Depends on network access, git, sudo privileges, make, the upstream repository layout, and the pm-graph Makefile. It bypasses the in-tree copy by installing latest upstream.

## Risks and Test Signals
Uses plain HTTP rather than HTTPS, creating integrity and interception risk. Variables such as `$OUT` are sometimes unquoted. No commit/tag pinning means installs are not reproducible. Test mktemp failure, clone failure, install failure, cleanup behavior, and prefer HTTPS or pinned revisions for production use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/pm-graph/install_latest_from_github.sh -->
