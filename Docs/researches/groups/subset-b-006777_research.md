# subset-b-006777 Research

Grouped research report for the Intel x86 power tooling files in this work item. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-config.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-config.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-mbox.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-mbox.c

## Purpose
`isst-core-mbox.c` implements the `struct isst_platform_ops` backend for API version 1 platforms that expose Intel Speed Select controls through mailbox, MSR, and selected MMIO operations. It translates the generic operations used by `isst-core.c` into `ISST_IF_MBOX_COMMAND`, `ISST_IF_IO_CMD`, and MSR ioctl calls, decodes mailbox response bitfields into common SST data structures, and writes uncore frequency sysfs settings when applying performance levels.

## Important APIs, Types, And Functions
The exported entry point is `mbox_get_platform_ops()`, returning a static `mbox_ops` table. The low-level command paths are `_send_mbox_command()` and `_send_mmio_command()`. Backend parameter state is controlled by `mbox_update_platform_param()` for `ISST_PARAM_MBOX_DELAY` and `ISST_PARAM_MBOX_RETRIES`. Feature readers include `mbox_read_pm_config()`, `mbox_get_config_levels()`, `mbox_get_ctdp_control()`, `mbox_get_tdp_info()`, `mbox_get_pwr_info()`, `mbox_get_coremask_info()`, `mbox_get_get_trl()`, `mbox_get_get_trls()`, `mbox_get_trl_bucket_info()`, `mbox_get_pbf_info()`, and `mbox_get_fact_info()`. Mutators include `mbox_set_tdp_level()`, `mbox_set_pbf_fact_status()`, `mbox_pm_qos_config()`, `mbox_set_clos()`, and `mbox_clos_associate()`.

## Control Flow
Generic calls from `isst-core.c` enter through the ops table. Most mailbox operations build a command, subcommand, parameter, and request-data value, call `_send_mbox_command()`, then unpack the response into `isst_pkg_ctdp`, `isst_pkg_ctdp_level_info`, `isst_pbf_info`, `isst_fact_info`, or `isst_clos_config`. `_send_mbox_command()` handles optional delay, opens `/dev/isst_interface`, retries ioctl failures, and returns response data. For non-SKX CLOS reads/writes other than PM QoS config, `_send_mbox_command()` routes to `_send_mmio_command()` using PM QoS/CLOS/PQR offsets instead of mailbox commands.

## State And Persistence Behavior
Backend process state is limited to `mbox_delay` and `mbox_retries`. Hardware state can be changed by CONFIG_TDP set-level and set-control commands, CLOS PM QoS configuration, CLOS parameter writes, PQR association writes, PM config writes, and TRL MSR changes initiated through shared core helpers. `_set_uncore_min_max()` persists uncore min/max frequency choices to `/sys/devices/system/cpu/intel_uncore_frequency/package_%02d_die_%02d/*_freq_khz`.

## Dependencies And Integration Points
The file depends on `linux/isst_if.h`, `/dev/isst_interface`, mailbox and IO kernel modules, `isst-core.c` wrappers for MSR access, display error helpers, topology helpers such as `set_cpu_mask_from_punit_coremask()` and `find_phy_core_num()`, and platform predicates from `isst-config.c`. It supplies frequency-display semantics: mailbox values normally use `DISP_FREQ_MULTIPLIER` of 100, while EMR expands TRL level names to `level-N`.

## Risks And Edge Cases
Mailbox bitfield decoding is platform-specific. Several failure paths return zeroed data to keep legacy platforms usable, notably config-level fallback where dynamic SST is absent. `_send_mbox_command()` exits on `ENOTTY`, so missing kernel modules are fatal. CLOS routing differs between SKX and newer platforms, which risks mismatched logical core ids if topology mapping is wrong. Uncore sysfs path names are assumed to match package/die formatting. `mbox_pm_qos_config()` refuses to disable core-power while turbo-freq remains enabled. EMR has five TRL levels; other mailbox platforms expose three named levels.

## Test Signals
Backend tests should validate mailbox command packing, retry/delay behavior, CLOS MMIO fallback selection, bitfield decoding for config levels, TDP info, PBF masks, FACT buckets, and PM QoS enable/disable transitions. Hardware or ioctl mocks should cover ENOTTY handling, failed mailbox reads, locked TDP set-level, invalid FACT bucket handling, and uncore sysfs write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-mbox.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-tpmi.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-tpmi.c

## Purpose
`isst-core-tpmi.c` implements the `struct isst_platform_ops` backend for TPMI-based Intel Speed Select platforms, used by API versions 2 and 3. It maps generic SST operations onto typed `linux/isst_if.h` ioctl payloads for performance levels, base frequency, turbo frequency, core-power state, CLOS parameters, CLOS association, and TPMI instance discovery.

## Important APIs, Types, And Functions
The exported entry point is `tpmi_get_platform_ops()`, returning `tpmi_ops`. `tpmi_process_ioctl()` is the common ioctl helper and debug printer. Feature readers include `tpmi_read_pm_config()`, `tpmi_get_config_levels()`, `tpmi_get_ctdp_control()`, `tpmi_get_tdp_info()`, `tpmi_get_pwr_info()`, `tpmi_get_coremask_info()`, `tpmi_get_get_trls()`, `tpmi_get_trl_bucket_info()`, `tpmi_get_pbf_info()`, `tpmi_get_fact_info()`, `tpmi_get_clos_information()`, `tpmi_pm_get_clos()`, and `tpmi_clos_get_assoc_status()`. Mutators include `tpmi_set_tdp_level()`, `tpmi_set_pbf_fact_status()`, `tpmi_adjust_uncore_freq()`, `tpmi_pm_qos_config()`, `tpmi_set_clos()`, and `tpmi_clos_associate()`.

## Control Flow
Every public operation fills a kernel ABI structure with `socket_id` and `power_domain_id` from `struct isst_id`, then calls `tpmi_process_ioctl()`. Performance-level reads start with `ISST_IF_PERF_LEVELS` to populate package-level state and then use `ISST_IF_GET_PERF_LEVEL_INFO` and related mask/fabric ioctls for level details. Feature enable/disable writes call `ISST_IF_PERF_SET_FEATURE`, then poll `isst_get_ctdp_control()` up to five times to confirm the requested PBF or FACT state. Core-power and CLOS setters intentionally loop across all valid punit instances in the package because the code treats those settings as package-scoped.

## State And Persistence Behavior
This file has little internal state; `tpmi_update_platform_param()` is currently a no-op. Hardware state changes occur through TPMI ioctl set operations for performance level, feature state, core-power enable/type, CLOS parameters, and CLOS associations. `tpmi_adjust_uncore_freq()` reads TPMI fabric frequencies, then `_set_uncore_min_max()` scans `/sys/devices/system/cpu/intel_uncore_frequency/` for entries with matching `domain_id` and `package_id` and writes min/max frequency files.

## Dependencies And Integration Points
The file depends on `/dev/isst_interface`, the TPMI-capable `linux/isst_if.h` ABI, topology helpers from `isst-config.c`, common validation and wrapper logic from `isst-core.c`, and display/error helpers. Unlike the mailbox backend, frequency values are exposed in MHz and `tpmi_get_disp_freq_multiplier()` returns 1. TRL levels are named `level-0` through `level-7`.

## Risks And Edge Cases
The backend returns `-1` for many ioctl failures without detailed errno propagation, so callers generally get generic command failure. `tpmi_get_get_trl()` has a `FIX ME` and always returns level 0 ratios, which can hide requested-level differences. `tpmi_get_pwr_info()` is a stub that reports zero min/max power. API version differences affect how PBF/FACT support bits are interpreted. Package-wide loops temporarily mutate `id->punit` and must restore it on all paths. Uncore sysfs discovery skips entries whose metadata cannot be read, and failures are mostly silent.

## Test Signals
Important tests include ioctl payload construction for each operation, API v2 versus v3 support-mask handling, valid-mask filtering in `tpmi_is_punit_valid()`, package-wide CLOS/core-power loops, feature enable polling success and timeout, punit CPU mask conversion, and uncore sysfs matching by package/domain ids. Regression tests should pin the known `tpmi_get_get_trl()` level-0 behavior until fixed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core-tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core.c

## Purpose
`isst-core.c` is the backend-neutral core layer for Intel Speed Select operations. It selects the platform ops table, validates callback availability, exposes wrapper functions for the CLI and daemon, performs common feature validation, owns shared MSR helper operations, and assembles full processed `isst_pkg_ctdp` data by combining level, PBF, FACT, power, core-mask, bucket, and TRL information.

## Important APIs, Types, And Functions
The central state is the static `struct isst_platform_ops *isst_ops`. `isst_set_platform_ops()` selects mailbox ops for API version 1 and TPMI ops for API versions 2 and 3. `CHECK_CB()` enforces callback presence. Nearly every public `isst_*` function delegates to the selected backend: `isst_read_pm_config()`, `isst_get_ctdp_levels()`, `isst_get_ctdp_control()`, `isst_get_tdp_info()`, `isst_get_pwr_info()`, `isst_get_coremask_info()`, `isst_get_pbf_info()`, `isst_get_fact_info()`, CLOS helpers, and feature setters. Shared MSR operations include `isst_send_msr_command()`, `isst_get_trl()`, `isst_set_trl()`, `isst_set_trl_from_current_tdp()`, and `isst_get_config_tdp_lock_status()`.

## Control Flow
The CLI calls `isst_set_platform_ops()` during initialization. Subsequent commands use wrapper APIs, so command code is independent of mailbox versus TPMI details. `isst_get_process_ctdp()` is the primary aggregation flow: read package levels, validate the requested level, iterate each applicable TDP level, fetch control state, optionally fetch PBF and FACT details, apply SKX fallback when perf-profile is not enabled, otherwise fetch TDP, power, core mask, TRL bucket, and TRL ratio data. `isst_get_process_ctdp_complete()` frees cpumasks allocated during that aggregation.

## State And Persistence Behavior
Internal persistent process state is just the selected ops pointer. Host state changes are delegated to backends or the MSR helper. `isst_set_trl()` writes MSR 0x1AD, defaulting zero input to all-ones. `isst_set_trl_from_current_tdp()` can reconstruct MSR TRL values from the current TDP level and account for mailbox versus TPMI frequency units. `isst_get_config_tdp_lock_status()` reads MSR 0x64b bit 31.

## Dependencies And Integration Points
The file is the integration point between `isst-config.c` command flows and the backend implementations. It also uses display helpers for validation failures, topology/cpufreq helpers for fallback behavior, and `/dev/isst_interface` with `ISST_IF_MSR_COMMAND` for MSR access. Its data structures are declared in `isst.h`.

## Risks And Edge Cases
`CHECK_CB()` exits the process on invalid ops instead of returning an error, so initialization order matters. Some wrapper functions allocate cpumasks before backend calls; callers must free them on success paths, and some error paths can be hard to audit. `isst_get_process_ctdp()` continues past some level-control failures but returns immediately for later fetch failures, so partial data behavior differs by stage. The SKX fallback path uses cpufreq base frequency and MSR TRL when perf-profile is disabled. Frequency unit conversion for TRL writes is subtle because mailbox ratios use 100 MHz units while TPMI reports MHz.

## Test Signals
Tests should cover ops selection by API version, invalid API rejection, callback guard behavior, MSR command packing, PBF/FACT level validation, `isst_get_process_ctdp()` with all-level and single-level requests, SKX disabled-perf-profile fallback, cpumask allocation/free expectations, and TRL conversion in `isst_set_trl_from_current_tdp()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-daemon.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-daemon.c

## Purpose
`isst-daemon.c` implements the OOB daemon/polling support for `intel-speed-select`. Its job is to detect performance-level changes made by an out-of-band agent and apply matching CPU online/offline or cgroup isolation changes so the OS CPU availability matches the active SST performance profile.

## Important APIs, Types, And Functions
The exported functions are `isst_daemon()` and `process_level_change()`. Internal state is stored in `per_package_levels_info[MAX_PACKAGE_COUNT][MAX_DIE_PER_PACKAGE][MAX_PUNIT_PER_DIE]` and matching timestamp array `per_package_levels_tm`. `init_levels()` initializes level state to `-1`. `poll_for_config_change()` iterates online power domains through `for_each_online_power_domain_in_set()`. `daemonize()` performs fork/session setup, PID file creation, and lock acquisition. `signal_handler()` exits and calls `hfi_exit()`.

## Control Flow
`isst_daemon()` installs signals or daemonizes depending on flags, initializes remembered levels, and chooses between HFI event mode and polling mode. If no poll interval is supplied, it calls `hfi_main()` and returns an error message instructing the user to specify a poll interval. In poll mode it sleeps for `poll_interval` seconds and calls `poll_for_config_change()` until termination. Each power domain enters `process_level_change()`, which rate-limits checks to at most once every two seconds per package/die/punit, reads current TDP level, ignores locked configs and unchanged levels, fetches the core mask for the current level, and then either isolates non-enabled CPUs with cgroup v2 or hotplugs CPUs online/offline through sysfs.

## State And Persistence Behavior
Process state tracks the last observed level and last check timestamp per power domain. Persistent host effects include PID file `/tmp/hfi-events.pid`, daemon working directory `/tmp/`, optional cgroup v2 partition changes, and CPU hotplug writes through `set_cpu_online_offline()`. The signal handler sets `done` but also exits immediately for SIGINT/SIGTERM after `hfi_exit()`.

## Dependencies And Integration Points
This file depends heavily on APIs exported by `isst-config.c` and `isst-core.c`: topology iteration, current-level reads, core-mask reads, cgroup helpers, and CPU online/offline writes. It also integrates with `hfi-events.c` via `hfi_main()` and `hfi_exit()`. It shares all hardware/backend dependencies of the selected platform ops.

## Risks And Edge Cases
Running as a daemon can close standard file descriptors before later code writes diagnostics. `daemonize()` uses a single PID file path and lock, so concurrent daemons should fail but stale lock behavior depends on OS cleanup. The level timestamp array prevents rapid repeated work but may also suppress legitimate quick changes. `process_level_change()` assumes `pkg`, `die`, and `punit` are valid array indexes. CPU hotplug and cgroup operations can disrupt workloads and require root. HFI mode currently reports that a poll interval must be specified after trying `hfi_main()`.

## Test Signals
Tests should cover initial level tracking, unchanged-level no-op behavior, locked-config no-op behavior, poll loop dispatch, cgroup fallback to hotplug, signal handling, PID lock contention, and rate limiting. On real hardware, observe that changing SST level causes the enabled core mask to be applied exactly once per level change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-daemon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-display.c -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-display.c

## Purpose
`isst-display.c` centralizes text and JSON rendering for `intel-speed-select`. It formats package/die/powerdomain/CPU hierarchy, performance-profile details, base-frequency and turbo-frequency properties, core-power CLOS data, command results, errors, and TRL values. It is intentionally presentation-only but it influences command correctness because JSON state must be opened and closed in the right order.

## Important APIs, Types, And Functions
Public rendering functions include `isst_ctdp_display_information_start()`, `isst_ctdp_display_information_end()`, `isst_ctdp_display_information()`, `isst_ctdp_display_core_info()`, `isst_pbf_display_information()`, `isst_fact_display_information()`, `isst_clos_display_information()`, `isst_clos_display_clos_information()`, `isst_clos_display_assoc_information()`, `isst_display_result()`, `isst_display_error_info_message()`, and `isst_trl_display_information()`. Internal helpers `printcpulist()` and `printcpumask()` convert cpumasks; `format_and_print_txt()` and `format_and_print()` implement text/JSON indentation and object closure; `print_package_info()` emits the scope header.

## Control Flow
Callers normally bracket a command with `isst_ctdp_display_information_start()` and `_end()`. Within the bracket, each display function calls `print_package_info()` to enter the scope, emits nested fields through `format_and_print()`, and closes back to the package level. `isst_ctdp_display_information()` walks processed TDP levels, prints CPU counts, masks, ratios, base frequencies, uncore and memory frequencies, feature support/enabled state, thermal/power properties, TRL buckets, and nested PBF/FACT details. PBF and FACT standalone commands use the same internal helpers at a different base indentation.

## State And Persistence Behavior
The file has no external persistence, but it keeps formatting state in static variables `last_level`, `start`, and error index counters. Output goes to the `FILE *` supplied by callers or returned by `get_output_file()` for errors. The JSON mode is manually assembled by tracking indentation levels and recent levels, not by a JSON library.

## Dependencies And Integration Points
It depends on `out_format_is_json()`, `api_version()`, platform predicates, frequency multiplier and TRL level-name helpers, CPU topology size, `get_cpu_count()`, and standard `cpu_set_t` macros. The data being printed comes from structures declared in `isst.h` and populated by `isst-core.c` backends.

## Risks And Edge Cases
Manual JSON generation is fragile: missing start/end calls, unexpected level jumps, or error messages outside active output can produce invalid JSON. `printcpumask()` allocates a temporary integer mask and silently returns on allocation failure. Several buffers are fixed-size and can truncate long CPU lists on very large systems. Frequency formatting depends on backend multipliers, so incorrect ops selection yields wrong units. Some output field names vary by platform/API, which tests need to account for.

## Test Signals
Snapshot tests should exercise text and JSON output for platform scope, single CPU scope, API v1 and API v2+ package labels, PBF, FACT with bucket filtering and AVX filtering, CLOS info/config/association, result success/failure, errors both inside and outside display brackets, empty cpumasks, and large CPU masks. JSON output should be parsed by a JSON parser in tests, not only compared as text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst-display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst.h -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst.h

## Purpose
`isst.h` is the shared contract for the Intel Speed Select user-space tool. It collects system includes, local bit macros, mailbox command constants, topology limits, core data structures, the backend ops interface, and cross-file function declarations used by the CLI, core abstraction, backends, display code, daemon, and HFI integration.

## Important APIs, Types, And Functions
The key identity type is `struct isst_id`, which represents a logical CPU plus package, die, and punit power-domain coordinates. Feature data types include `struct isst_clos_config`, `struct isst_pbf_info`, `struct isst_fact_bucket_info`, `struct isst_fact_info`, `struct isst_pkg_ctdp_level_info`, and `struct isst_pkg_ctdp`. `struct isst_platform_ops` is the backend vtable and includes callbacks for frequency units, TRL names, punit validity, PM config, perf-profile levels, TDP details, power data, core masks, TRL ratios/buckets, PBF/FACT get/set, uncore adjustment, and CLOS/core-power operations.

The header declares common APIs from `isst-config.c`, wrapper APIs from `isst-core.c`, rendering APIs from `isst-display.c`, daemon/HFI APIs, backend factory functions, and cgroup helpers.

## Control Flow
At runtime, `isst-config.c` initializes platform state and calls `isst_set_platform_ops()`. `isst-core.c` then uses `struct isst_platform_ops` declarations from this header to delegate to either `mbox_get_platform_ops()` or `tpmi_get_platform_ops()`. Data flows from backend-specific ioctls into header-defined structures, then to display functions and command-specific policy code.

## State And Persistence Behavior
The header itself stores no state, but it defines the structure fields that carry mutable command state. Several structures contain `cpu_set_t *` members and `core_cpumask_size`; ownership is shared by convention, with allocation through `alloc_cpu_set()` and cleanup through `free_cpu_set()` or `isst_get_process_ctdp_complete()`.

## Dependencies And Integration Points
The file depends on Linux and GNU interfaces: `sched.h` CPU sets, `sys/ioctl.h`, `cpuid.h`, `dirent.h`, and `linux/isst_if.h`. Its constants mirror mailbox command encodings and resource limits used by both mailbox and TPMI code. It is the single include that lets separate implementation files share platform predicates, topology helpers, display functions, backend factories, and daemon entry points.

## Risks And Edge Cases
The header mixes public declarations, backend ABI constants, and utility macros, so any change has broad rebuild and behavioral impact. `BIT(x)` uses `1 << x`, which is not safe for large bit positions unless callers use `BIT_ULL()`. Fixed limits such as `MAX_PACKAGE_COUNT`, `MAX_DIE_PER_PACKAGE`, `MAX_PUNIT_PER_DIE`, `ISST_MAX_TDP_LEVELS`, and bucket counts must match hardware/kernel ABI expectations. Several function declarations use raw pointers and ownership conventions without type-level enforcement.

## Test Signals
Compile-time tests should cover all translation units with warnings enabled. ABI-sensitive tests should validate that structure fields are populated consistently by both backends and displayed correctly. Static analysis should watch for mismatched `alloc_cpu_set()`/`free_cpu_set()` use, invalid bit macro widths, and array indexing by package/die/punit values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel-speed-select/isst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel_pstate_tracer/intel_pstate_tracer.py -->
# sources/distributed-fs/ceph-client/tools/power/x86/intel_pstate_tracer/intel_pstate_tracer.py

## Purpose
`intel_pstate_tracer.py` is a Python 3 utility for collecting, parsing, and plotting Linux `power/pstate_sample` trace data for debugging and tuning the `intel_pstate` driver. It can either parse an existing trace file or enable tracing for a requested interval, then generate CSV files and many PNG graphs under `results/<testname>/`.

## Important APIs, Types, And Functions
The script is procedural. Constants `C_CPU` through `C_COMM` define CSV column indexes used by gnuplot commands, and `MAX_CPUS` caps supported CPUs at 256. Plot functions generate per-CPU and all-CPU graphs for P-state, performance busy, scaled busy, IO boost, durations, loads, frequency, and TSC sanity data. `common_gnuplot_settings()` and `set_4_plot_linestyles()` configure Gnuplot. Data functions include `store_csv()`, `split_csv()`, `cleanup_data_files()`, and `read_trace_data()`. Trace-control functions are `clear_trace_file()`, `enable_trace()`, `disable_trace()`, `set_trace_buffer_size()`, and `free_trace_buffer()`. `fix_ownership()` gives outputs back to the sudo caller when applicable.

## Control Flow
The `__main__` block parses getopt options for existing trace file, interval collection, CPU mask, test name, and buffer memory. It creates `results/<testname>`, writes a CSV header, optionally clears tracing, sets buffer size, enables the `pstate_sample` event, sleeps for the interval, disables tracing, then parses `/sys/kernel/tracing/trace` or the provided trace file. `read_trace_data()` reads the whole file, regex-matches pstate sample lines, computes elapsed time, load, duration, frequency in GHz, and TSC-derived GHz, appends rows to `cpu.csv`, splits the master CSV into per-CPU CSVs, and finally plotting functions render PNGs with Gnuplot.

## State And Persistence Behavior
Global state tracks sample number, per-CPU last timestamp, start time, current max CPU, graph-data presence, test name, and trace file path. Persistent outputs are directories and files under `results/<testname>/`: `cpu.csv`, `cpuNNN.csv`, and PNG graphs. When interval mode is used, the script mutates tracing sysfs state under `/sys/kernel/tracing/`, including event enablement, trace buffer size, and trace contents. SIGINT cleanup disables tracing, clears the trace file, and frees the buffer if interval mode is active.

## Dependencies And Integration Points
The script requires Python 3, `Gnuplot`, `numpy`, Linux tracing, and shell tools invoked via `subprocess.check_output()` and `os.system()`. It expects trace lines emitted by the kernel `power:pstate_sample` event with fields such as `core_busy`, `scaled`, `from`, `to`, `mperf`, `aperf`, `tsc`, `freq`, and optional `io_boost`.

## Risks And Edge Cases
The parser reads the full trace file into memory and uses a long regex tied to trace formatting. CPU ids beyond 255 are not supported. `split_csv()` uses shell `grep` with formatted CPU names and can be sensitive to shell environment. Existing test directories abort reruns. Test names are used as directory names and in gnuplot titles; help text warns against underscores for plot rendering but there is no strict sanitization. Tracing sysfs writes require root and can leave tracing enabled if the process is killed outside SIGINT handling. Bare `except` blocks hide specific IO failures.

## Test Signals
Tests should include parsing a small canned trace with and without `io_boost`, CPU mask filtering, per-CPU split output, no-data failure, existing test directory failure, option validation, and plot command generation with mocked `Gnuplot`. Integration tests on a tracing-enabled kernel should verify interval cleanup restores buffer size and disables the event after normal completion and SIGINT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/intel_pstate_tracer/intel_pstate_tracer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/turbostat/Makefile -->
# sources/distributed-fs/ceph-client/tools/power/x86/turbostat/Makefile

## Purpose
The `turbostat/Makefile` builds, installs, cleans, and packages the `turbostat` x86 power diagnostic tool. It is a compact standalone build recipe that supports out-of-tree output through `O=`, cross-compilation through `CROSS_COMPILE`, install prefix staging through `PREFIX` and `DESTDIR`, and snapshot tarball creation for distributing `turbostat` with the required kernel header fragments.

## Important Targets And Variables
Core variables are `CC=$(CROSS_COMPILE)gcc`, `BUILD_OUTPUT=$(CURDIR)` or `$(O)`, `PREFIX?=/usr`, `DESTDIR?=`, `DAY=$(shell date +%Y.%m.%d)`, and `SNAPSHOT=turbostat-$(DAY)`. The explicit target `turbostat : turbostat.c` relies on the pattern rule `%: %.c`, which creates `$(BUILD_OUTPUT)` and links with `-lcap -lrt`. `override CFLAGS` appends optimization, warnings, include paths, file-offset support, fortify, and preprocessor definitions pointing to kernel headers. Phony targets are `clean`, while `install` and `snapshot` are regular make targets.

## Control Flow
`make turbostat` compiles `turbostat.c` into `$(BUILD_OUTPUT)/turbostat`. `make clean` removes the built binary and current snapshot archive. `make install` builds first, then installs the binary into `$(DESTDIR)$(PREFIX)/bin` and the manual page into `$(DESTDIR)$(PREFIX)/share/man/man8`. `make snapshot` builds, creates a dated snapshot directory, copies source/man/build files and `intel-family.h`, transforms `msr-index.h` to use local generated `bits.h`, writes minimal local `bits.h` and `build_bug.h`, generates a snapshot Makefile with local header definitions, appends the original Makefile with kernel-header definition lines removed, and tars the snapshot.

## State And Persistence Behavior
Build outputs are written to `$(BUILD_OUTPUT)`, which defaults to the source directory but can be redirected with `O=...`. Installation writes under `DESTDIR/PREFIX`. Snapshot state is written into `turbostat-YYYY.MM.DD/` and `turbostat-YYYY.MM.DD.tar.gz` in the current directory, with previous same-day snapshot directories removed first.

## Dependencies And Integration Points
The build depends on a C compiler, kernel include paths relative to the tool directory, libcap, librt, and the `turbostat.8` man page. The snapshot target integrates selected Linux headers into a distributable local include set so the snapshot can build outside the full kernel tree.

## Risks And Edge Cases
`override CFLAGS +=` means caller-supplied CFLAGS are augmented rather than replacing the Makefile requirements, which is usually desirable but can surprise packaging. The generic `%: %.c` rule can build any C source in the directory, not only turbostat. Snapshot naming is date-based, so repeated snapshots on the same day overwrite the directory and archive. Relative kernel header paths assume the source tree layout remains unchanged. Snapshot header generation uses shell `echo` and `sed` commands whose quoting is important.

## Test Signals
Run `make clean`, `make turbostat`, `make O=/tmp/turbostat-build turbostat`, `make install DESTDIR=/tmp/pkg PREFIX=/usr`, and `make snapshot` in a full kernel source tree. Verify the linked binary exists in `BUILD_OUTPUT`, install paths are correct, and the snapshot tarball contains generated `bits.h`, `build_bug.h`, transformed `msr-index.h`, `intel-family.h`, source, man page, and a self-contained Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/x86/turbostat/Makefile -->
