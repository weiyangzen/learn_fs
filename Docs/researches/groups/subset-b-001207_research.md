# subset-b-001207 cpufreq driver research

This grouped report covers the requested CPU frequency scaling source files. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-ut.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-ut.c

## Purpose

This module is an in-kernel unit-test harness for the AMD P-State driver. It validates platform prerequisites, driver enablement, CPPC performance/frequency data, EPP sysfs behavior, mode transitions, and the dynamic frequency-attribute set exposed by `amd-pstate.c`.

## Important APIs, types, and functions

`struct amd_pstate_ut_struct` maps test names to callbacks, with `test_list` allowing a comma-delimited module parameter filter. Test cases include `amd_pstate_ut_acpi_cpc_valid()`, `amd_pstate_ut_check_enabled()`, `amd_pstate_ut_check_perf()`, `amd_pstate_ut_check_freq()`, `amd_pstate_ut_epp()`, `amd_pstate_ut_check_driver()`, and `amd_pstate_ut_check_freq_attrs()`. It calls exported AMD pstate helpers such as `amd_pstate_get_status()`, `amd_pstate_update_status()`, `amd_pstate_get_mode_string()`, `store_energy_performance_preference()`, `show_energy_performance_preference()`, `amd_pstate_clear_dynamic_epp()`, and `amd_pstate_get_current_attrs()`.

## Control flow, state, and persistence

`amd_pstate_ut_init()` iterates the static test table at module load and skips tests not present in `test_list`. Most tests walk online CPUs via cpufreq policies and inspect per-policy `struct amd_cpudata`. The EPP test temporarily disables dynamic EPP, switches to active mode, writes all raw EPP values from 0 through 255, checks readback, then checks string preferences before restoring the original mode. The driver-transition test walks all mode pairs. The module stores no persistent state except transient mode/EPP changes that it tries to restore before returning.

## Dependencies and integration points

The test depends on ACPI CPPC, x86 CPPC MSRs, cpufreq policy access, AMD pstate private data from `amd-pstate.h`, and CPU feature detection. It integrates tightly with AMD pstate global mode switching and sysfs preference helpers, so failures are direct regression signals for the production driver.

## Risks and test signals

The test mutates global AMD pstate mode and per-policy EPP, so early exits can leave altered driver state if restore paths fail. It assumes policy driver data is `struct amd_cpudata` and that CPU0 is representative for EPP testing. Strong signals are successful module load logs for every case, valid CPPC perf ordering, frequency invariants matching policy limits, EPP roundtrips, and exact expected visibility of prefcore/EPP/floor-frequency attributes in passive, active, and guided modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate-ut.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.c

## Purpose

This is the AMD Processor P-State cpufreq driver. It uses ACPI CPPC data and either AMD CPPC MSRs or ACPI shared-memory CPPC calls to control performance limits, desired performance, boost, preferred-core ranking, energy-performance preference, floor performance, suspend/resume restoration, and runtime switching among disabled, passive, active EPP, and guided modes.

## Important APIs, types, and functions

The main global state is `current_pstate_driver`, `cppc_state`, `amd_pstate_prefcore`, `dynamic_epp`, and optional DMI `quirks`. Static calls select MSR or shared-memory backends for `amd_pstate_update_perf()`, `amd_pstate_set_epp()`, `amd_pstate_get_epp()`, `amd_pstate_cppc_enable()`, and `amd_pstate_init_perf()`. Important helpers include `freq_to_perf()`, `perf_to_freq()`, `amd_pstate_update_min_max_limit()`, `amd_pstate_update_freq()`, `amd_pstate_adjust_perf()`, `amd_pstate_init_freq()`, `amd_pstate_init_boost_support()`, `amd_pstate_init_prefcore()`, and `amd_pstate_set_floor_perf()`. It exports mode/status and EPP helpers used by the test module.

## Control flow, state, and persistence

`amd_pstate_init()` runs as a device initcall, checks AMD vendor, CPPC support, `_CPC`, existing cpufreq drivers, DMI quirks, boot parameters, default mode, and static-call backend selection before registering either `amd_pstate_driver` or `amd_pstate_epp_driver`. Per-CPU init allocates `struct amd_cpudata`, reads CPPC caps and current request state, computes frequency limits, enables CPPC, initializes boost/floor/perf caches, and registers QoS requests in passive/guided mode. Passive mode uses target/fast-switch/adjust_perf paths to program desired performance. Active mode uses `setpolicy`, keeps desired performance autonomous, and drives EPP plus min/max bounds. Mode changes are serialized by `amd_pstate_driver_lock` through `mode_state_machine`.

The persistent runtime state is mostly hardware CPPC request MSRs or shared-memory CPPC controls, cached in `amd_cpudata->cppc_req_cached`, `cppc_req2_cached`, and `perf`. Offline, suspend, and exit paths deliberately reset CPPC request and floor performance toward BIOS values so kexec and firmware handoff preserve sane minimums. Dynamic EPP registers a platform-profile device and optional power-supply notifier per CPU; cleanup removes those resources.

## Dependencies and integration points

The driver depends on ACPI CPPC (`cppc_*` APIs), x86 MSRs, AMD CPU feature helpers, DMI, cpufreq core, freq QoS, scheduler ITMT/preferred-core support, power-supply notifications, platform profile, tracepoints from `amd-pstate-trace.h`, and CPU subsystem sysfs. It provides global `/sys/devices/system/cpu/amd_pstate/*` controls and per-policy attributes such as max frequency, lowest nonlinear frequency, highest perf, prefcore ranking, EPP preferences, and floor frequency when supported.

## Risks and test signals

Risk centers on stale cached CPPC request values, incorrect static-call backend selection, mode transitions racing with cpufreq policies, firmware tables reporting invalid perf/frequency values, and restore paths that write inappropriate min/floor values around suspend or kexec. Preferred-core support must coordinate with AMD HFI and scheduler ITMT. Test signals include `amd-pstate-ut`, active/passive/guided mode switching through sysfs, cpufreq fast-switch behavior, boost toggling, suspend/resume and CPU hotplug, EPP behavior on AC/DC power, platform-profile changes, tracepoints, and validation that cpufreq limits remain within CPPC-derived min/max/nominal/highest values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.h

## Purpose

This header defines the shared private interface for AMD P-State implementation and its unit tests. It describes cached CPPC performance fields, APERF/MPERF sampling data, per-CPU AMD pstate driver data, mode values, and exported helper prototypes.

## Important APIs, types, and functions

`union perf_cached` packs CPPC performance capabilities and computed min/max limits into a u64-friendly cache. `struct amd_aperf_mperf` stores APERF, MPERF, and TSC samples. `struct amd_cpudata` is the central per-policy object: CPU id, QoS requests, CPPC request caches, perf cache, prefcore ranking, floor performance metadata, frequency limits, APERF/MPERF samples, boost/prefcore flags, EPP policy state, suspend state, power notifier, and platform-profile device state. `enum amd_pstate_mode` defines undefined, disable, passive, active, guided, and max sentinel modes.

## Control flow, state, and persistence

The header has no executable control flow. Its state definitions determine what `amd-pstate.c` allocates during policy init and what `amd-pstate-ut.c` inspects during tests. Fields such as `bios_min_perf`, `bios_floor_perf`, `cppc_req_cached`, and `cppc_req2_cached` are especially important for restoring firmware defaults and preserving sane state across hotplug, suspend, and kexec.

## Dependencies and integration points

The header depends on PM QoS and platform-profile definitions and forward-declares cpufreq/sysfs types where possible. It exposes `amd_pstate_get_status()`, `amd_pstate_update_status()`, EPP show/store helpers, `amd_pstate_clear_dynamic_epp()`, and `amd_pstate_get_current_attrs()` for the test module and other AMD pstate-adjacent code.

## Risks and test signals

Because this header exposes private structures outside the main driver, layout or semantic changes must be coordinated with `amd-pstate-ut.c`. Risks include stale comments, tests relying on fields that production code no longer maintains, and cache fields being read without appropriate synchronization. Test signals are successful AMD pstate build, module-test access to `struct amd_cpudata`, and no mismatch between documented perf ordering and runtime checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd-pstate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd_freq_sensitivity.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/amd_freq_sensitivity.c

## Purpose

This module adds AMD/Hygon processor feedback support to the ondemand governor's powersave-bias hook. It reads hardware frequency-sensitivity MSRs and biases non-CPU-bound workloads toward lower frequencies.

## Important APIs, types, and functions

`struct cpu_data_t` caches previous actual/reference counters and the previous frequency decision per CPU. `amd_powersave_bias_target()` is the registered ondemand hook. `amd_freq_sensitivity_init()` validates vendor, optional chipset/feature presence, MSR readability, and class code before registering the handler through `od_register_powersave_bias_handler()`. Exit unregisters it.

## Control flow, state, and persistence

On each governor decision, the hook reads `MSR_AMD64_FREQ_SENSITIVITY_ACTUAL` and `REFERENCE`, masks the class bits, handles wrap or zero-delta cases by keeping current frequency, computes sensitivity from counter deltas, compares it with `od_tuners->powersave_bias`, and may clamp the next target down to current, minimum, or the next lower table entry. Per-CPU state is only the prior counter snapshot and previous frequency choice; nothing persists across module unload or reboot.

## Dependencies and integration points

The module depends on x86 MSR access, AMD/Hygon CPU feature detection, PCI probing for older platforms, and internal ondemand governor interfaces in `cpufreq_ondemand.h`. It integrates only with the ondemand governor; other governors do not use this hook.

## Risks and test signals

Risks include reliance on internal governor data structures, counter wrap handling, integer sensitivity calculation, and platform detection that may exclude valid hardware or include broken firmware. Test by loading on supported AMD/Hygon systems, verifying the handler registers, observing powersave-bias behavior under memory-bound versus CPU-bound workloads, and checking no divide-by-zero or invalid frequency-table index occurs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/amd_freq_sensitivity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/apple-soc-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/apple-soc-cpufreq.c

## Purpose

This driver controls CPU cluster DVFS performance states on Apple SoCs. It uses device-tree performance domains to find a cluster MMIO register block, converts OPP levels to Apple p-state indexes, and implements cpufreq target and fast-switch operations.

## Important APIs, types, and functions

`struct apple_soc_cpufreq_info` describes SoC-specific p-state bit layouts and maximum p-state values for S5L8960X, T8103, T8112, and fallback compatibles. `struct apple_cpu_priv` stores the CPU device, mapped register base, and SoC info. Key functions are `apple_soc_cpufreq_find_cluster()`, `apple_soc_cpufreq_init()`, `apple_soc_cpufreq_get_rate()`, `apple_soc_cpufreq_set_target()`, and `apple_soc_cpufreq_fast_switch()`.

## Control flow, state, and persistence

Module init only registers the cpufreq driver on `"apple,arm-platform"`. Policy init loads OPPs from DT, resolves the performance-domain phandle, maps the cluster registers, marks sharing CPUs, builds a cpufreq table, and stores each OPP level in `driver_data` as the p-state. Target waits for `APPLE_DVFS_CMD_BUSY` to clear, writes PS1 and optionally PS2 fields plus the SET bit, and returns immediately. Current frequency reads the current p-state field from status when known, otherwise falls back to the command register. Hardware register state persists until firmware or reset changes it; driver state is per-policy allocated data and OPP table state.

## Dependencies and integration points

The driver depends on device-tree CPU OPP tables, `performance-domains`, MMIO mapping, OPP sharing, cpufreq generic table verification, cooling-device integration, software boost, energy-model registration through OPP, and generic suspend handling. It is blocklisted from generic `cpufreq-dt` platform-device creation so it can own Apple-specific DVFS registers.

## Risks and test signals

Risks include SoC-specific bitfield mistakes, fallback status reads not reflecting boost limits, mapping the wrong performance-domain node, OPP level values exceeding known p-state fields, and transition timeout failures. Test signals are successful policy creation per cluster, correct p-state readback for every OPP, fast-switch operation, suspend frequency selection, EM registration, thermal cooling registration, and stable frequency changes on supported Apple SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/apple-soc-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/armada-37xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/armada-37xx-cpufreq.c

## Purpose

This Armada 37xx helper programs north-bridge DVFS and optional AVS voltage tables, creates OPPs for the supported CPU load levels, and then registers a `cpufreq-dt` platform device to provide normal cpufreq operation.

## Important APIs, types, and functions

`struct armada37xx_cpufreq_state` stores the `cpufreq-dt` device, CPU device, PM regmap, and suspend snapshots. `struct armada_37xx_dvfs` maps base CPU frequencies to four divider values and calculated AVS values. Important helpers include `armada_37xx_cpu_freq_info_get()`, `armada37xx_cpufreq_dvfs_setup()`, `armada37xx_cpufreq_avs_configure()`, `armada37xx_cpufreq_avs_setup()`, `armada37xx_cpufreq_enable_dvfs()`, `armada37xx_cpufreq_disable_dvfs()`, and suspend/resume callbacks passed through `cpufreq_dt_platform_data`.

## Control flow, state, and persistence

The late initcall locates syscon regmaps for peripheral clock, north-bridge PM, and optionally AVS, disables DVFS, gets CPU0's clock parent rate, selects the matching divider profile, calculates AVS values, programs VSET registers, programs all four load-level register fields, adds dynamic OPPs with frequencies and voltages, enables hardware DVFS, and registers `cpufreq-dt`. Suspend saves NB DVFS registers; resume disables DVFS, restores saved load/config registers, and writes `NB_DYN_MOD` last because it re-enables DVFS and makes other fields read-only. Runtime persistence is hardware NB/AVS register state plus dynamically added OPPs.

## Dependencies and integration points

The driver depends on syscon/regmap compatibles for Armada 3700 clock, PM, and AVS blocks, CPU clocks, OPP core, and the generic `cpufreq-dt` driver. It integrates with `cpufreq-dt` by creating the platform device and supplying suspend/resume hooks.

## Risks and test signals

Risk areas are unsupported parent clock rates, AVS voltage calculation edge cases, DVFS enable ordering, missing AVS syscon behavior, and failure cleanup that must remove only OPPs already added. Test signals include OPP table contents for four load levels, correct voltage values for 600/800/1000/1200 MHz bases, frequency switching through `cpufreq-dt`, suspend/resume register restoration, and no CPU lockups when transitioning from lower load levels back to L0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/armada-37xx-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/armada-8k-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/armada-8k-cpufreq.c

## Purpose

This Armada 8K helper synthesizes OPP tables from CPU clock rates and registers `cpufreq-dt`. It supports Marvell AP806/AP807 CPU clock compatibles and assumes valid operating points are the nominal clock divided by 1, 2, 3, and 4.

## Important APIs, types, and functions

`opps_div[]` defines the synthetic dividers. `struct freq_table` tracks each CPU device and dynamically added frequencies so exit/error paths can remove them. `armada_8k_get_sharing_cpus()` groups CPUs sharing the same clock, `armada_8k_add_opp()` adds per-cluster OPPs, `armada_8k_cpufreq_free_table()` cleans them up, and `armada_8k_cpufreq_init()` performs discovery and `cpufreq-dt` platform-device registration.

## Control flow, state, and persistence

Module init checks for an available matching CPU clock node, allocates a table sized by possible CPUs, and iterates a cpumask of unprocessed CPUs. For each cluster representative, it gets the CPU clock, adds four OPPs based on the current clock rate, identifies all CPUs sharing that clock, marks OPP sharing, removes those CPUs from the work mask, and finally registers a `cpufreq-dt` platform device. State is dynamic OPP entries, sharing masks in OPP core, and the registered platform device; exit unregisters the device and removes tracked OPPs.

## Dependencies and integration points

The driver depends on OF CPU clock nodes, the common clock framework, OPP core, cpumask topology, and `cpufreq-dt`. It is a setup layer rather than the runtime cpufreq policy implementation.

## Risks and test signals

Risks include assuming only integer divider OPPs are valid, treating current boot rate as nominal maximum, incomplete cleanup if OPP addition fails mid-cluster, and bad sharing masks if clock providers do not compare as expected. Test by booting AP806/AP807 systems, checking dynamic OPP tables per cluster, validating `cpufreq-dt` registration, switching through all divider rates, and unloading if modular to confirm OPP cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/armada-8k-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/bmips-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/bmips-cpufreq.c

## Purpose

This driver provides cpufreq support for Broadcom BMIPS5000/BMIPS5200 MIPS SoCs by changing CPU clock divider bits in the Broadcom mode register. It builds a frequency table from the high-precision timer frequency and a platform-specific multiplier.

## Important APIs, types, and functions

`struct cpufreq_compat` binds CPU compatible strings to BMIPS type, clock multiplier, and number of frequency entries. `bmips_cpufreq_get_freq_table()` allocates descending divide-by-two entries. `bmips_cpufreq_get()` reads `read_c0_brcm_mode()`, extracts the divider, and returns kHz. `bmips_cpufreq_target_index()` writes divider state through `change_c0_brcm_mode()`. `bmips_cpufreq_driver_init()` detects a supported CPU node and registers the cpufreq driver.

## Control flow, state, and persistence

At module init, the driver scans for supported CPU compatibles and stores the selected static compatibility entry in global `priv`. Policy init allocates and installs the table, using `cpufreq_generic_init()` with a fixed transition latency. Runtime target operations use the table entry's `driver_data` as the divider. Exit frees the per-policy frequency table. Persistent state is only the CPU mode-register divider until reset or another writer changes it.

## Dependencies and integration points

The driver depends on MIPS `mips_hpt_frequency`, Broadcom C0 mode register helpers, OF CPU compatible nodes, and cpufreq generic frequency-table handling. It has no regulator or OPP integration.

## Risks and test signals

Risks include incorrect HPT-to-CPU multiplier assumptions, unsupported BMIPS variants sharing compatible strings, direct mode-register manipulation on SMP systems, and no explicit locking beyond cpufreq serialization. Test signals are a correct frequency table, initial frequency matching hardware divider, successful transitions across all divide-by-two entries, and stable timer/accounting behavior after divider changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/bmips-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/brcmstb-avs-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/brcmstb-avs-cpufreq.c

## Purpose

This Broadcom STB driver exposes AVS firmware-controlled DFS/DVFS to cpufreq. The firmware running on a co-processor owns voltage and frequency changes; the Linux driver serializes mailbox commands, discovers supported P-states, and reports AVS status through cpufreq attributes.

## Important APIs, types, and functions

`struct private_data` stores mailbox MMIO, interrupt MMIO, completion, semaphore, saved PMAP, device pointer, and host IRQ. `struct pmap` represents firmware mode and PLL mapping parameters. The command core is `__issue_avs_command()`, with wrappers for PMAP and P-state get/set. Discovery and lifecycle helpers include `brcm_avs_is_firmware_loaded()`, `brcm_avs_get_freq_table()`, `brcm_avs_prepare_init()`, `brcm_avs_prepare_uninit()`, `brcm_avs_cpufreq_init()`, `brcm_avs_suspend()`, and `brcm_avs_resume()`.

## Control flow, state, and persistence

Probe maps the AVS CPU data and interrupt register regions, requests the optional host interrupt, verifies firmware magic and command support, stores the platform device in `brcm_avs_driver.driver_data`, and registers cpufreq. Policy init builds the frequency table by saving the current P-state, iterating P0 through P4, setting each P-state, reading back mailbox frequency, restoring the original P-state, enabling AVS, and setting `policy->cur`. Runtime target calls set a firmware P-state. Suspend saves PMAP and current P-state then sends S2 enter; resume sends S2 exit and restores PMAP, tolerating already-set maps. The semaphore serializes mailbox access, while completion or polling waits for firmware command completion.

## Dependencies and integration points

The driver depends on device-tree compatible regions `brcm,avs-cpu-data-mem` and `brcm,avs-cpu-l2-intr`, a named `sw_intr` interrupt when available, MMIO mailbox protocol, cpufreq generic table verification, and firmware support for AVS DVFS commands. It exports read-only cpufreq attributes for pstate, mode, pmap, voltage, and frequency.

## Risks and test signals

Risks include mailbox timeout handling, accidental out-of-range parameter counts, command races if semaphore handling regresses, firmware not loaded, frequency-table discovery causing visible temporary p-state changes, and resume PMAP mismatch. Test signals include firmware magic validation, successful P-state enumeration, interrupt and polling command completion, cpufreq transitions, suspend/resume restore, and meaningful `brcm_avs_*` sysfs attribute output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/brcmstb-avs-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cppc_cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cppc_cpufreq.c

## Purpose

This generic ACPI CPPC cpufreq driver maps cpufreq frequency requests to CPPC performance controls. It also supports optional scheduler frequency invariance from CPPC feedback counters, boost, CPPC sysfs controls, shared performance domains, and an artificial energy model on heterogeneous ARM64 systems.

## Important APIs, types, and functions

The driver uses `struct cppc_cpudata` from ACPI CPPC core as policy private data. Core paths are `cppc_cpufreq_get_cpu_data()`, `cppc_cpufreq_cpu_init()`, `cppc_cpufreq_set_target()`, `cppc_cpufreq_fast_switch()`, `cppc_cpufreq_update_perf_limits()`, `cppc_cpufreq_get_rate()`, `cppc_cpufreq_set_boost()`, and `cppc_cpufreq_cpu_exit()`. With `CONFIG_ACPI_CPPC_CPUFREQ_FIE`, `struct cppc_freq_invariance`, `cppc_scale_freq_tick()`, PCC work handling, and `topology_set_scale_freq_source()` update `arch_freq_scale`. Sysfs attributes include frequency-domain CPUs, auto-select, auto activity window, EPP value, and perf-limited.

## Control flow, state, and persistence

Late init requires valid ACPI `_CPC`, initializes FIE and efficiency-class data, then registers the cpufreq driver. Policy init allocates CPPC data, reads `_PSD`, performance caps, and current perf controls, sets policy min to lowest nonlinear and max to highest or nominal depending on boost, applies sharing masks for `CPUFREQ_SHARED_TYPE_ANY`, enables fast-switch when CPPC permits it, programs desired perf to highest, and starts FIE for the policy. Target/fast-switch convert requested kHz to desired performance, recompute min/max performance bounds from policy limits, and call `cppc_set_perf()`. Get-rate samples feedback counters twice and falls back to desired perf when counters are invalid or idle. Exit lowers desired perf to lowest and frees CPPC data.

## Dependencies and integration points

The driver depends on ACPI CPPC methods, ACPI processor IDs, `_PSD`, scheduler topology frequency-scale hooks, optional PCC-safe kthread work, cpufreq core, CPU hotplug semantics, and optional ARM64 energy model registration from MADT GICC efficiency classes. It is the generic fallback for systems exposing standards-based CPPC rather than vendor-specific drivers like AMD pstate.

## Risks and test signals

Risks include CPPC firmware returning zero or inconsistent counters, sleeping PCC accesses from tick context, shared-domain policy misclassification, boost max updates not refreshing limits by themselves, artificial EM cost modeling inaccuracies, and sysfs writes that alter autonomous selection or EPP unexpectedly. Test signals include successful policy creation from `_CPC/_PSD`, frequency requests reflected in CPPC desired perf, correct frequency-invariance values under load, cpufreq boost toggling, sysfs read/write behavior, CPU hotplug cleanup, and suspend/idle cases where get-rate falls back cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cppc_cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c

## Purpose

This file decides whether to create the generic `cpufreq-dt` platform device from device tree. It preserves legacy allowlisted machines, supports automatic creation for CPU0 OPP v2 bindings, and blocks machines that need specialized cpufreq drivers.

## Important APIs, types, and functions

The main data is `allowlist[]` and `blocklist[]` of root compatible strings. `cpu0_node_has_opp_v2_prop()` checks whether CPU0 has `operating-points-v2`. `cpufreq_dt_platdev_init()` performs the policy decision and calls `platform_device_register_data()` with optional `struct cpufreq_dt_platform_data`.

## Control flow, state, and persistence

At core init, the file first checks the allowlist and carries match data into platform data when present, such as per-policy governor support for RK3399. If not allowlisted, it creates the device when CPU0 has OPP v2 and the root compatible is not blocklisted. Otherwise it returns `-ENODEV`. The only lasting state is the registered platform device; this file has no remove path because it is built as an init helper.

## Dependencies and integration points

It depends on OF machine matching, CPU device-tree nodes, platform-device registration, and the `cpufreq_dt_platform_data` contract from `cpufreq-dt.h`. It integrates with many SoC-specific cpufreq drivers by explicitly not creating `cpufreq-dt` for platforms that need custom handling, including Apple, MediaTek, NVIDIA Tegra, Qualcomm, TI, and others.

## Risks and test signals

Risks include allowlist/blocklist drift, incorrect automatic creation on platforms whose OPP v2 data still requires custom voltage/clock sequencing, and missing creation for legacy OPP v1 systems. Test signals are exactly one cpufreq driver binding per platform, successful `cpufreq-dt` creation on allowlisted or unblocked OPP v2 machines, and absence of conflicts on blocklisted platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt-platdev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.c

## Purpose

This is the generic device-tree OPP cpufreq driver. It builds cpufreq policies from CPU clocks, regulators, and OPP tables, then changes CPU rate through the OPP core.

## Important APIs, types, and functions

`struct private_data` stores the CPU device, sharing CPU mask, cpufreq table, static-OPP flag, regulator token, and list node. Important functions are `dt_cpufreq_early_init()`, `cpufreq_init()`, `set_target()`, `dt_cpufreq_release()`, `dt_cpufreq_probe()`, `dt_cpufreq_remove()`, and exported `cpufreq_dt_pdev_register()`. `find_supply_name()` handles `cpu-supply` and legacy `cpu0-supply`.

## Control flow, state, and persistence

Probe pre-initializes every present CPU so errors such as regulator or OPP probe deferral happen before registering cpufreq. Early init skips CPUs already covered by another private data entry, allocates a sharing mask, sets OPP regulators, obtains sharing from OPP v2 or legacy OPP state, adds static OPP tables for all shared CPUs, checks that the OPP table is non-empty, initializes a cpufreq table, and links the private data. Policy init finds the relevant private data, gets the CPU clock, copies the sharing mask to `policy->cpus`, installs the cpufreq table, sets suspend frequency and transition latency, and enables any-CPU DVFS. Target calls `dev_pm_opp_set_rate()` with selected frequency in Hz. Remove unregisters cpufreq and releases tables, static OPPs, regulators, masks, and list nodes.

## Dependencies and integration points

The driver depends on CPU device nodes, common clock framework, OPP core, regulator framework, cpufreq generic table verification, thermal cooling device registration, energy-model registration with OPP, software boost, and optional platform data for governor-per-policy, suspend/resume, and intermediate target hooks. It is instantiated either by `cpufreq-dt-platdev.c` or explicit platform-device registration from SoC setup drivers.

## Risks and test signals

Risks include incorrect OPP sharing masks, regulator naming compatibility, duplicated OPP table initialization, static versus dynamic OPP cleanup mistakes, and global driver callback mutation from platform data affecting all instances. Test signals include successful probe deferral behavior, valid frequency tables, regulator voltage changes through OPP, correct shared policies, cooling and EM registration, suspend frequency behavior, and clean remove/unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.h

## Purpose

This header defines the small platform-data interface used by `cpufreq-dt` setup helpers and declares the helper for registering a `cpufreq-dt` platform device.

## Important APIs, types, and functions

`struct cpufreq_dt_platform_data` carries optional behavior: `have_governor_per_policy`, `get_intermediate`, `target_intermediate`, `suspend`, and `resume`. `cpufreq_dt_pdev_register()` is exported by `cpufreq-dt.c` for code that wants to instantiate the generic driver under a parent device.

## Control flow, state, and persistence

The header has no runtime flow. Its fields are consumed at `dt_cpufreq_probe()` time to mutate the generic cpufreq driver callbacks and flags before registering the driver. Because the callbacks live in a global `cpufreq_driver`, platform data effectively influences the singleton driver instance.

## Dependencies and integration points

The header depends only on Linux types and forward-declares `struct cpufreq_policy`. It is included by `cpufreq-dt.c`, `cpufreq-dt-platdev.c`, and platform setup drivers such as Armada 37xx.

## Risks and test signals

Risks include adding platform-data fields without updating the singleton driver mutation logic, and assuming multiple independent `cpufreq-dt` instances can carry different callbacks at the same time. Test signals are successful compilation of users, correct suspend/resume hook invocation for platform helpers, and no callback leakage across incompatible platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-dt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-nforce2.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-nforce2.c

## Purpose

This legacy x86 cpufreq driver changes front-side bus frequency on NVIDIA nForce2 chipsets by programming reverse-engineered PLL registers. It is explicitly risky hardware-control code and only supports CPU0.

## Important APIs, types, and functions

Global state includes `nforce2_dev`, module parameters `fid` and `min_fsb`, and computed `max_fsb`. Key helpers are `nforce2_calc_fsb()`, `nforce2_calc_pll()`, `nforce2_write_pll()`, `nforce2_fsb_read()`, `nforce2_set_fsb()`, `nforce2_get()`, `nforce2_target()`, `nforce2_verify()`, `nforce2_cpu_init()`, and `nforce2_detect_chipset()`.

## Control flow, state, and persistence

Module init finds the nForce2 PCI device and registers a cpufreq driver. CPU init reads current FSB, derives CPU multiplier from `cpu_khz` if `fid` was not supplied, reads boot FSB as the maximum, derives a safe minimum when absent, and sets policy min/max. Target converts requested CPU kHz to FSB, emits transition notifications, and calls `nforce2_set_fsb()`. The setter initializes PLL registers if needed, enables writes, walks the FSB one MHz at a time toward the target, writes calculated PLL values to all 64 PLL registers, and finally writes an address value. Hardware PLL state persists until reboot or another writer changes it.

## Dependencies and integration points

The driver depends on PCI config-space access to NVIDIA nForce2 devices, `cpu_khz`, cpufreq transition notifications, and module parameters for multiplier/minimum FSB tuning. It has no OPP, regulator, ACPI, or clock-framework integration.

## Risks and test signals

The file itself warns that FSB changing may crash or cause data loss. Risks include bad reverse-engineered PLL calculations, incorrect CPU multiplier inference, unsafe FSB bounds, ignored target failure in `nforce2_target()` transition completion, lack of IRQ disabling despite comments, and platform instability while stepping the bus. Test only on expendable supported hardware: verify detected PCI revision, current and boot FSB reads, conservative min/max policy, small incremental transitions, and system stability under disk and memory load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/cpufreq-nforce2.c -->
