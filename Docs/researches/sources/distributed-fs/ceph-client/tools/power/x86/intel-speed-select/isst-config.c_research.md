# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-config.c

## Purpose
`isst-config.c` is the main command-line controller for `intel-speed-select`. It parses global and feature-specific options, discovers CPU/package/die/punit topology, selects the correct platform backend through `isst_fill_platform_info()`, and dispatches user commands for perf-profile, base-freq, turbo-freq, core-power, turbo-mode, and OOB daemon mode. It is also the file with the most direct host state mutation: CPU online/offline writes, cpufreq min/max writes, cgroup v2 CPU isolation, topology cache creation, and output-file selection.

## Important APIs, Types, And Functions
The file defines `struct process_cmd_struct` for feature/command dispatch and a local `_cpu_map` table that maps logical CPUs to package, die, punit, and punit-local core ids. Public helpers exported through `isst.h` include `get_output_file()`, `is_debug_enabled()`, `debug_printf()`, `api_version()`, platform predicates such as `is_spr_platform()`, topology helpers such as `set_isst_id()`, `is_cpu_in_power_domain()`, `get_topo_max_cpus()`, `alloc_cpu_set()`, `free_cpu_set()`, `get_max_punit_core_id()`, `get_cpu_count()`, `find_phy_core_num()`, `set_cpu_mask_from_punit_coremask()`, cgroup helpers, and the power-domain iteration functions.

Key control functions are `cmdline()`, `process_command()`, `parse_cmd_args()`, `parse_cpu_command()`, `create_cpu_map()`, `for_each_online_power_domain_in_set()`, `for_each_online_target_cpu_in_set()`, `dump_isst_config()`, `set_tdp_level()`, `set_pbf_enable()`, `set_fact_enable()`, CLOS/core-power handlers, and `process_trl()`.

## Control Flow
`main()` sets `outf` to `stderr` and calls `cmdline()`. `cmdline()` checks privilege, reads CPU model via CPUID plus `/proc/cpuinfo` for the CascadeLake-N special case, verifies `/dev/isst_interface` except for CLX-N, fills platform info, parses global options, updates backend parameters, initializes topology, optionally forces CPUs online, caches topology, builds the CPU map, then either starts `isst_daemon()` for OOB mode or dispatches feature commands through `process_command()`.

Most feature commands follow the same pattern: validate command options, call `isst_ctdp_display_information_start()`, iterate either explicit target CPUs or one representative CPU per power domain, invoke `isst-core.c` wrapper APIs, print via `isst-display.c`, then call `isst_ctdp_display_information_end()`. The CLX-N path bypasses hardware feature toggles and synthesizes base-frequency data from cpufreq sysfs.

## State And Persistence Behavior
Global process state includes target CPU lists, `cpu_map`, cpumasks, parsed option values, CLOS parameters, output format, and platform info. Persistent host state is affected through `/var/run/isst_cpu_topology.dat`, `/sys/devices/system/cpu/cpu*/online`, cpufreq `scaling_min_freq` and `scaling_max_freq`, cgroup v2 directories under `/sys/fs/cgroup/<pkg>-<die>-<punit>`, and optionally the user-selected output file. `store_cpu_topology()` creates a binary cache to preserve topology after CPUs are offlined; `force_all_cpus_online()` removes it. `cpu_0_workaround()` isolates CPU 0 through cgroup v2 when sysfs hotplug is unavailable or explicitly requested.

## Dependencies And Integration Points
The file depends on Linux sysfs, cgroup v2, `/proc/cpuinfo`, CPUID, `/dev/isst_interface`, and the kernel `linux/isst_if.h` ABI. It integrates with `isst-core.c` for backend-neutral SST operations, `isst-display.c` for text/JSON rendering, `isst-daemon.c` for OOB/poll operation, and `hfi-events.c` through `isst_daemon()`. Backend selection depends on `isst_platform_info.api_version`, with API version 1 using mailbox and versions 2/3 using TPMI.

## Risks And Edge Cases
The code requires root for mutating commands but allows read-only operation if `/dev/isst_interface` can be opened. Hardware and kernel ABI assumptions are high-risk: missing sysfs nodes, unsupported CPU models, absent kernel modules, stale topology caches, and CPU hotplug limitations can all change behavior. Several operations intentionally modify system-wide policy, including cpufreq limits, CLOS associations, TRL MSR values, CPU isolation, and CPU online state. CPU lists are capped at 512 entries. JSON formatting state is shared globally through `isst-display.c`, so command flows must bracket output correctly. CLX-N support is intentionally limited and depends on model-name parsing.

## Test Signals
Useful tests include `intel-speed-select --version`, `--help`, `--info`, text and JSON `perf-profile info`, explicit `--cpu` parsing for single CPUs and ranges, invalid option handling, read-only invocation as non-root, and backend behavior on systems with and without `/dev/isst_interface`. Mutating tests should be isolated to suitable hardware or mocks for sysfs/ioctl paths, especially `set-config-level --online`, base-freq auto mode, turbo-freq auto mode, core-power CLOS configuration, and OOB poll mode.
