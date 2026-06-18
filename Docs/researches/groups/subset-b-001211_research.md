# subset-b-001211 research

This grouped report covers Intel SpeedStep and SoC/virtual CPUFreq drivers plus CPUIdle framework build files and platform idle back ends. Each file section is delimited for reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-centrino.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-centrino.c

Purpose: implements the legacy x86 CPUFreq driver for Intel Enhanced SpeedStep on Pentium M/Centrino-era CPUs. It exposes a `cpufreq_driver` named `centrino` that programs `MSR_IA32_PERF_CTL`, reads `MSR_IA32_PERF_STATUS`, and uses conservative CPU model/stepping/table matching before allowing voltage/frequency transitions.

Important APIs and functions: `centrino_init()` checks `x86_match_cpu()` against EST-capable families/models and registers the driver. `centrino_cpu_init()` validates Intel vendor and `X86_FEATURE_EST`, restricts operation to CPU0, enables `MSR_IA32_MISC_ENABLE_ENHANCED_SPEEDSTEP` if needed, installs a Banias/Dothan/P4HT frequency table through `policy->freq_table`, and sets a 10 us latency. `extract_clock()` decodes either multiplier bits or table `driver_data`, `get_cur_freq()` reads current/fallback MSRs, and `centrino_target()` writes the selected low 16 PERF_CTL bits to all CPUs in the policy domain.

Control flow and state: static CPU ID/model tables map model strings to frequency/voltage operating points when `CONFIG_X86_SPEEDSTEP_CENTRINO_TABLE` is enabled. Per-CPU pointers `centrino_model` and `centrino_cpu` cache the matched table and CPU ID. Target changes allocate a temporary cpumask, choose an online CPU for shared domains, preserve reserved PERF_CTL bits, and attempt best-effort rollback if a multi-CPU write path fails after partial coverage.

Dependencies and integration points: depends on x86 MSR helpers, CPU feature matching, the CPUFreq table verifier, late init registration, and old Intel CPU model strings. It integrates only through CPUFreq, not ACPI; unsupported tables intentionally suggest `acpi-cpufreq`.

Risks and test signals: risks include exact ASCII model-name matching, CPU0-only init on systems with unusual topology, stale voltage tables, transient PERF_STATUS values, and limited rollback semantics where `oldmsr` may already contain the requested value. Test signals include driver refusal on unsupported CPUs, correct `cpufreq-info` table entries for supported Banias systems, successful EST enable bit persistence, `get` reporting nonzero rates during thermal transitions, and PERF_CTL writes matching table `driver_data`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-centrino.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-ich.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-ich.c

Purpose: provides the Intel SpeedStep CPUFreq driver for mobile Intel processors controlled through ICH2-M/ICH3-M/ICH4-M southbridge power-management registers. It exposes two states, `SPEEDSTEP_HIGH` and `SPEEDSTEP_LOW`, through a CPUFreq table.

Important APIs and functions: `speedstep_detect_processor()` and `speedstep_get_freqs()` come from `speedstep-lib`. Local setup finds the ICH LPC/PM PCI device in `speedstep_detect_chipset()`, enables SpeedStep registers in PCI config offset `0xa0`, reads PMBASE from config offset `0x40`, and uses `speedstep_set_state()` to toggle bit 0 at `pmbase + 0x50` while temporarily disabling bus-master arbitration at `pmbase + 0x20`. `speedstep_cpu_init()` discovers low/high rates by executing the transition callback on a policy CPU; `speedstep_target()` uses `smp_call_function_single()` to run transitions on an online sibling.

Control flow and state: global state includes the retained PCI device pointer, detected processor enum, PMBASE, and the two-entry frequency table. SMP policy masks are narrowed to topology siblings. Frequency reads are executed on the target CPU through `get_freq_data()` because MSR-derived speed detection is CPU-local.

Dependencies and integration points: depends on Intel PCI IDs, raw port I/O, x86 CPU matching, the shared SpeedStep library, and CPUFreq generic table verification. Module init registers only after CPU, chipset, activation, and PMBASE discovery succeed; exit releases the PCI reference and unregisters CPUFreq.

Risks and test signals: risks include dangerous raw chipset programming, missing `pci_dev_put()` on the `speedstep_find_register()` failure path after chipset detection, fixed offsets for legacy southbridges, Dell Inspiron host-bridge exclusion fragility, and no transition error propagation from the asynchronous target wrapper. Test signals include PMBASE logging, successful low/high frequency discovery with measured latency, no lockups on excluded 82815 revisions, correct sibling policy masks, and pmbase state bit matching the requested CPUFreq index after transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-ich.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.c

Purpose: supplies shared Intel SpeedStep v1/v2 helpers for legacy CPUFreq drivers. It detects supported mobile Pentium III/Pentium 4 processors, decodes current frequencies from MSRs, and probes the two SpeedStep rates by executing a caller-supplied state transition callback.

Important APIs and functions: `speedstep_get_frequency()` dispatches to `pentium3_get_frequency()`, `pentiumM_get_frequency()`, `pentium_core_get_frequency()`, or `pentium4_get_frequency()`. `speedstep_detect_processor()` uses `boot_cpu_data`, CPUID EBX, model IDs, platform MSRs, and optional `relaxed_check` to distinguish mobile SpeedStep-capable processors. `speedstep_get_freqs()` records the current speed, switches to low then high state with interrupts and preemption disabled, measures transition latency with `ktime_get()`, restores the previous state when needed, and exports low/high kHz values.

Control flow and state: the library is mostly stateless, with only the optional `relaxed_check` module parameter. Frequency decoding is table-driven for PIII multipliers/FSB values and switch-driven for Pentium M/Core/P4 FSB encodings. `speedstep_get_freqs()` serializes with local IRQ/preemption control because the transition callback may be chipset or SMI sensitive.

Dependencies and integration points: depends on x86 MSR access, CPUID helpers, `cpu_khz`, CPUFreq definitions, and callers that provide safe `set_state(SPEEDSTEP_LOW/HIGH)` callbacks. It exports GPL symbols used by `speedstep-ich` and `speedstep-smi`.

Risks and test signals: risks include undocumented CPU heuristics, fallback to measured `cpu_khz` for early P4, potentially long interrupts-off windows while probing transitions, inexact latency safety clamping, and the relaxed capability knob admitting unsafe hardware. Test signals include nonzero decoded frequency on every supported enum, correct rejection of desktop Coppermine/Celeron cases, low/high rates differing, latency clamped to sane bounds, and successful symbol linkage for both consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.h

Purpose: declares the shared SpeedStep processor IDs, binary state constants, and exported helper prototypes consumed by legacy Intel SpeedStep CPUFreq drivers.

Important APIs and types: `enum speedstep_processor` identifies auto-detected PIII/P4-M processors and frequency-decodable non-autodetected Pentium M/P4D/Core values. `SPEEDSTEP_HIGH` is state 0 and `SPEEDSTEP_LOW` is state 1, matching the CPUFreq table indices used by the ICH and SMI drivers. Prototypes expose `speedstep_detect_processor()`, `speedstep_get_frequency()`, and `speedstep_get_freqs()`.

Control flow and state: this header has no runtime state; it fixes the ABI contract between transition-capable drivers and the library. Callers pass a `set_state()` callback to `speedstep_get_freqs()`, which probes both hardware states.

Dependencies and integration points: integrates only with `speedstep-lib.c` and SpeedStep CPUFreq drivers. It assumes consumers include CPUFreq-visible types before or alongside it.

Risks and test signals: risks include the semantic dependency that high/low constants equal table indices, stale enum values for obsolete x86 CPUs, and comments referring to an older callback signature. Test signals are clean compile for both consumers, CPUFreq index 0 mapping to high state, and no enum mismatches in detection switch statements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-lib.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-smi.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-smi.c

Purpose: implements a legacy Intel SpeedStep CPUFreq driver that controls mobile Pentium III systems through an IST/SMI BIOS interface. It can obtain SMI port/command/signature from BIOS `ist_info` or module parameters.

Important APIs and functions: `speedstep_smi_ownership()` requests BIOS interface ownership via inline x86 `out` to the SMI port. `speedstep_smi_get_freqs()` asks BIOS for low/high MHz when the event field indicates a safe implementation, otherwise init falls back to `speedstep_get_freqs()`. `speedstep_set_state()` issues `SET_SPEEDSTEP_STATE` SMI commands with up to five retries and interrupt-enabled waits between failed attempts. CPUFreq hooks are `speedstep_cpu_init()`, `speedstep_target()`, `speedstep_get()`, and `speedstep_resume()`.

Control flow and state: global state stores `smi_port`, `smi_cmd`, `smi_sig`, detected processor enum, and a two-entry frequency table. Init filters x86 IDs, narrows supported processors to PIII variants, validates or fills SMI parameters, then registers the CPUFreq driver. Policy init is CPU0-only and reacquires SMI ownership on resume.

Dependencies and integration points: depends on `asm/ist.h`, inline 32-bit register conventions around SMI calls, module parameters, the shared SpeedStep library, CPUFreq table verification, and KVM-unrelated bare-metal BIOS behavior.

Risks and test signals: risks include firmware hangs on early systems, raw inline assembly assumptions, SMI calls under preemption/IRQ constraints, module parameter spoofing of signature, fallback probing that toggles real CPU states, and `speedstep_get()` returning `-ENODEV` through an unsigned return type for nonzero CPUs. Test signals include ownership result zero, sane BIOS-provided MHz values, fallback low/high probing success when BIOS call is disabled, retries resolving transient DMA-related failures, and resume reacquiring ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/speedstep-smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sti-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sti-cpufreq.c

Purpose: prepares STMicroelectronics STiH407/STiH410/STiH418 CPU OPP selection before launching the generic `cpufreq-dt` platform device. It selects OPP variants by SoC major/minor version, process code, and substrate code read from syscon registers.

Important APIs and functions: `sti_cpufreq_fetch_syscon_registers()` obtains `st,syscfg` and `st,syscfg-eng` regmaps. `sti_cpufreq_fetch_major()`, `sti_cpufreq_fetch_minor()`, and `sti_cpufreq_fetch_regmap_field()` read version and DVFS bitfields. `sti_cpufreq_set_opp_info()` builds a `dev_pm_opp_config` with `supported_hw` and a `prop_name` such as `pcode0`, then calls `dev_pm_opp_set_config()`. `sti_cpufreq_init()` gates by machine compatible, validates CPU0 OPP-v2, and always registers `cpufreq-dt` after the voltage-scaling attempt.

Control flow and state: a single static `ddata` holds CPU device and syscon regmaps. Missing hardware info offset falls back to default version bits; failed pcode/substrate/major/minor reads mostly degrade to defaults except syscon acquisition failure. The OPP token is not stored for later cleanup because this is an init-only platform setup path.

Dependencies and integration points: depends on DT properties `operating-points-v2`, `st,syscfg`, and `st,syscfg-eng`, ST machine compatibles, regmap fields, OPP supported-hw/prop-name filtering, and generic `cpufreq-dt`.

Risks and test signals: risks include `dev_err(ddata.cpu, ...)` after `get_cpu_device(0)` returns NULL, no unregister path for the OPP config token or created platform device, defaulting that may expose conservative but unexpected OPPs, and only STiH407 field layout support. Test signals include syscon phandle reads, debug pcode/version values, OPP table filtered by `opp-supported-hw` and named voltages, and `cpufreq-dt` binding even when voltage scaling is skipped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sti-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sun50i-cpufreq-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sun50i-cpufreq-nvmem.c

Purpose: reads Allwinner sun50i speed-bin efuses and configures CPU OPP filtering before instantiating `cpufreq-dt`. It handles H6, A100, H616/H618/H700 style OPP descriptors.

Important APIs and functions: efuse translators `sun50i_h6_efuse_xlate()`, `sun50i_a100_efuse_xlate()`, and `sun50i_h616_efuse_xlate()` map raw nvmem bits to speed grade indexes. `sun50i_cpufreq_get_efuse()` locates CPU0's OPP descriptor node, matches its compatible, reads the unnamed nvmem cell, converts little-endian data, and returns a speed bin. `dt_has_supported_hw()` checks whether OPP children contain `opp-supported-hw`. Probe allocates per-CPU OPP config tokens, sets `supported_hw` only when needed, sets a `prop_name` like `speed2`, applies the config to all present CPUs, then registers `cpufreq-dt`.

Control flow and state: module init first verifies machine compatibility, registers a platform driver, then creates a matching platform device so probe can defer on nvmem. Global platform-device pointers are used for cleanup. Per-probe state is the `opp_tokens` array stored in drvdata and cleared on remove.

Dependencies and integration points: depends on NVMEM cells under OPP tables, OPP-v2 descriptors, optional SMCCC SoC revision for H616 bin interpretation, CPU devices for all present CPUs, and generic `cpufreq-dt`.

Risks and test signals: risks include treating unknown bins as slowest, skipping `supported_hw` when DT lacks it but still selecting named properties, partial OPP config cleanup across possible/present CPU mismatch, a global `cpufreq_dt_pdev`, and H616 revision behavior depending on SMCCC discovery availability. Test signals include nvmem probe deferral, warning on unknown H616 bins, OPPs filtered to expected speed grade, all present CPUs receiving tokens, and clean remove unregistering `cpufreq-dt` and clearing configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sun50i-cpufreq-nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra124-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra124-cpufreq.c

Purpose: prepares Tegra114/Tegra124/Tegra210 CPU clocking for generic `cpufreq-dt` by switching the CPU clock source to DFLL and handling suspend/resume clock parent transitions.

Important APIs and functions: probe obtains CPU0 OF node, CPU device, and clocks named `cpu_g`, `dfll`, `pll_x`, and `pll_p`. `tegra124_cpu_switch_to_dfll()` aligns DFLL rate with the current CPU clock, temporarily reparents CPU to PLLP, enables DFLL, then reparents CPU to DFLL. `tegra124_cpufreq_suspend()` reparents CPU to safe PLLP and disables DFLL; resume reenables DFLL and reparents back, calling `disable_cpufreq()` on failure. Successful probe registers `cpufreq-dt` via `cpufreq_dt_pdev_register()`.

Control flow and state: a private devm-allocated struct holds clock handles and the `cpufreq-dt` platform device. Module init gates by Tegra machine compatible, registers a platform driver, then creates a synthetic platform device to allow probe deferral.

Dependencies and integration points: depends on CCF clocks named in CPU0 DT, DFLL/regulator readiness, OPP data consumed by `cpufreq-dt`, system sleep PM ops, and the local `cpufreq-dt.h` helper.

Risks and test signals: risks include manual `clk_put()` handling despite devm allocation of the container, unused `pllx_clk` except for lifetime acquisition, no rollback from successful DFLL switch if `cpufreq-dt` registration fails, and resume disabling cpufreq globally on DFLL reparent failure. Test signals include clock lookup deferral, CPU parent switching sequence observable in clk debugfs, cpufreq-dt registration, suspend using PLLP 408 MHz, and resume restoring DFLL without frequency loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra124-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra186-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra186-cpufreq.c

Purpose: implements a Tegra186 CPUFreq driver that reads BPMP firmware voltage/frequency hints, writes per-core EDVD registers to request CPU frequency/voltage, and optionally scales DRAM bandwidth through OPP/interconnect data.

Important APIs and functions: `tegra_cpufreq_bpmp_read_lut()` sends `MRQ_CPU_VHINT` through BPMP using coherent DMA, filters valid `ndiv` entries, stores EDVD `driver_data`, and computes kHz rates. `tegra186_cpufreq_probe()` maps the EDVD MMIO resource, reads LUTs for two clusters, initializes cores to each cluster's max EDVD value, enables optional ICC scaling if CPU0 has OPP/interconnect paths, and registers `tegra186_cpufreq_driver`. Driver hooks include `tegra186_cpufreq_init()`, `tegra186_cpufreq_set_target()`, and `tegra186_cpufreq_get()`.

Control flow and state: static CPU metadata maps logical CPUs to BPMP cluster IDs and EDVD offsets. Runtime data stores MMIO base, per-cluster LUT/ref clock/divisor, and an `icc_dram_bw_scaling` flag. Policy init groups CPUs by BPMP cluster and either builds a DT OPP-filtered table or falls back to the BPMP LUT.

Dependencies and integration points: depends on Tegra BPMP firmware ABI, platform MMIO resource, CPU OPP-v2/interconnect support, CPUFreq generic table verification, and per-policy governors. `driver_data` is stored globally in the cpufreq driver.

Risks and test signals: risks include global driver data for one device instance, allocated OPP-derived frequency tables not explicitly freed, ICC scaling being disabled globally after one failure, policy init loops over `ARRAY_SIZE(tegra186_cpus)` rather than dynamic CPU count, and no readback after EDVD writes. Test signals include BPMP LUT nonempty for both clusters, EDVD registers initialized to max, policy masks matching Denver/A57 clusters, `get` rate matching `ref_clk_khz * ndiv / div`, and OPP/ICC fallback message only when DT data is missing or invalid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra186-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra194-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra194-cpufreq.c

Purpose: implements CPUFreq for Tegra194, Tegra234, and Tegra238 CCPLEX CPUs using BPMP-provided NDIV limits, per-core NDIV request registers or system registers, counter-based speed reconstruction, and optional OPP/interconnect bandwidth scaling.

Important APIs and functions: SoC ops abstract counter reads, CPU/cluster ID extraction, and NDIV get/set. Tegra194 uses system registers `s3_0_c15_c0_4/5`; Tegra234/Tegra238 use MMIO scratch frequency and ACTMON counter registers. `tegra_cpufreq_bpmp_read_lut()` sends `MRQ_CPU_NDIV_LIMITS`, constructs a frequency table stepped around 50 MHz, and stores NDIV in `driver_data`. `tegra194_calculate_speed()` samples core/reference counters on a per-CPU workqueue, while `tegra194_get_speed()` reconciles measured frequency with the last requested NDIV table entry. Target writes NDIV to all CPUs in the policy and optionally calls `dev_pm_opp_set_opp()`.

Control flow and state: probe validates match data, optionally maps MMIO, allocates LUT and CPU topology arrays, creates `read_counters_wq`, reads BPMP LUTs for all clusters, stores per-CPU physical IDs from MPIDR, probes optional OPP/ICC support, and registers the CPUFreq driver. Policy init groups CPUs by cluster width, uses a BPMP LUT or DT OPP-filtered copy, and sets 300 us transition latency. Exit removes dynamic OPP data.

Dependencies and integration points: depends on BPMP firmware, ARM MPIDR topology, per-SoC system registers or CCPLEX MMIO, CPUFreq cooling, OPP-v2/interconnect APIs, hotplug online/offline callbacks, and workqueue execution on target CPUs.

Risks and test signals: risks include `tegra194_get_cpu_ndiv()` passing `&ndiv` instead of `ndiv` to `smp_call_function_single()`, 32-bit multiplication overflow in counter rate calculation before widening, global workqueue/driver-data assumptions, missing cleanup for some OPP-derived tables, and cluster geometry errors causing wrong scratch offsets. Test signals include BPMP returning NULL only for absent clusters, per-CPU `cpuid/clusterid/freq_core_reg` matching MPIDR, measured speed within `MAX_DELTA_KHZ` of requested table rates, CPUFreq cooling registration, and ICC scaling disabling itself after OPP set failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra194-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra20-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/tegra20-cpufreq.c

Purpose: configures Tegra20/Tegra30-era OPP supported-hardware masks from fuse-derived process and speedo IDs, then instantiates `cpufreq-dt`.

Important APIs and functions: `cpu0_node_has_opp_v2_prop()` validates CPU0 OPP-v2 presence. Probe computes two `versions[]` words from `tegra_sku_info`: Tegra20 uses CPU process and SoC speedo IDs; later matching platforms use CPU process and CPU speedo IDs. It calls `dev_pm_opp_set_supported_hw()` for CPU0 and registers cleanup through `devm_add_action_or_reset()`, then creates a `cpufreq-dt` platform device with devm unregister action.

Control flow and state: no persistent driver-private state is needed; devm cleanup stores the OPP token and platform device. The platform driver binds to a synthetic `tegra20-cpufreq` device provided elsewhere via platform alias.

Dependencies and integration points: depends on Tegra common/fuse SKU data, CPU0 OPP-v2 DT, OPP supported-hw filtering, and generic `cpufreq-dt`.

Risks and test signals: risks include only configuring CPU0, hard dependence on updated DT, assumptions about speedo field semantics across Tegra generations, and action data casting the OPP token through `void *`. Test signals include hardware version log matching fuse values, supported OPPs filtered to expected process/speedo rows, `cpufreq-dt` device creation, and devm cleanup clearing OPP config on probe failure or unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/tegra20-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/ti-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/ti-cpufreq.c

Purpose: selects TI CPU OPPs by SoC revision and eFuse speed grade, then launches `cpufreq-dt`. It supports AM33xx/AM43xx/DRA7/OMAP3 and newer K3 AM62 family variants with SoC-specific eFuse translation.

Important APIs and functions: `ti_cpufreq_soc_data` describes register offsets, masks, translations, regulator names, and compatibility quirks. Translators such as `amx3_efuse_xlate()`, `dra7_efuse_xlate()`, `omap3_efuse_xlate()`, `am625_efuse_xlate()`, and AM62 variants convert raw bins into OPP supported-hw bitmasks. `ti_cpufreq_get_efuse()` and `ti_cpufreq_get_rev()` read syscon or fallback MMIO for older OMAP quirks. `ti_cpufreq_probe()` gets CPU0 OPP node, syscon, computes the two-version array, optionally supplies multi-regulator names, calls `dev_pm_opp_set_config()`, and registers `cpufreq-dt`.

Control flow and state: init uses `of_machine_get_match()` and `platform_device_register_data()` to pass the matched SoC data to a built-in platform driver. Probe uses devm allocation for context but does not store it after setup. Missing OPP-v2 falls through so legacy tables can be tried by `cpufreq-dt`.

Dependencies and integration points: depends on SoC DT compatibles, CPU0 OPP-v2 `syscon` phandle, sys_soc matching for K3 revision handling, OPP supported-hw and regulator-name configuration, and generic `cpufreq-dt`.

Risks and test signals: risks include no OPP config token cleanup, hard-coded fallback `ioremap()` for OMAP3 control registers, K3 revision hard-coded to 0x1, broad eFuse translation fallthrough semantics, and `platform_device_register_simple("cpufreq-dt")` return value ignored. Test signals include revision/eFuse values matching silicon docs, OPP tables filtered to available speed grades, multi-regulator names applied on DRA7/OMAP36xx, legacy DT path still registering cpufreq-dt, and syscon single-register quirk working for AM625.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/ti-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/vexpress-spc-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/vexpress-spc-cpufreq.c

Purpose: provides CPUFreq support for ARM Versatile Express SPC big.LITTLE systems, including optional b.L switcher mode where logical CPUs may migrate between physical A15 and A7 clusters and use a merged virtual frequency table.

Important APIs and functions: `ve_spc_cpufreq_init()` initializes per-policy cluster masks, OPP frequency tables, clocks, and transition latency. `_get_cluster_clk_and_freq_table()` validates OPP count, builds cluster tables, and obtains CPU clocks. `merge_cluster_tables()` combines big and little tables using A7 virtual frequency scaling. `ve_spc_cpufreq_set_rate()` serializes per-cluster clock changes, updates per-CPU last requested/physical cluster state in switcher mode, calls `bL_switch_request()` when clusters change, and rebalances the old cluster clock. The driver supports energy model registration through `cpufreq_register_em_with_opp`.

Control flow and state: global arrays hold two cluster clocks and tables plus a virtual table slot. `cluster_usage` reference-counts table/clock lifetimes, `physical_cluster` and `cpu_last_req_freq` are per-CPU, and `cluster_lock[]` protects clock updates. Probe detects b.L switcher state, toggles cooling-device support, registers CPUFreq, and registers a switcher notifier that unregisters/reregisters CPUFreq around switcher mode changes.

Dependencies and integration points: depends on platform-specific SPC OPP initialization, CCF CPU clocks, topology physical package IDs, optional `CONFIG_BL_SWITCHER`, CPUFreq governors, OPP tables, and ARM big.LITTLE switcher callbacks.

Risks and test signals: risks include many global resources with complex unregister paths, switcher mode assumptions that init starts on A15, virtual A7 frequency shift conventions, clock readback workaround indicating possible hidden CCF failures, and incomplete cleanup if some present CPU device lookup fails mid-loop. Test signals include cluster-specific OPP tables, merged table sorted without duplicate big rates, clock rates matching requested actual rates, physical cluster migration at threshold crossings, notifier unregister/register cycles, and policy masks matching sharing CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/vexpress-spc-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/virtual-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/virtual-cpufreq.c

Purpose: implements a paravirtual CPUFreq driver for `qemu,virtual-cpufreq` MMIO devices. It lets guest vCPUs read available performance values, write requested performance, group policies by host-provided performance domains, and provide a virtualization-specific frequency-invariance source.

Important APIs and functions: MMIO offsets expose current performance, requested performance, performance table length/selection/readback, and performance domain. Probe maps the resource and validates each possible CPU's table length. `virt_cpufreq_get_freq_info()` either creates a discrete CPUFreq table or sets continuous min/max limits when the table length is one. `virt_cpufreq_get_sharing_cpus()` groups CPUs with equal `perf_domain`. Target and fast-switch paths write `REG_SET_PERF_STATE_OFFSET`; the slow target wraps writes in CPUFreq transition notifications. `virt_scale_freq_tick()` reads current performance and updates `arch_freq_scale` through `topology_set_scale_freq_source()`.

Control flow and state: a global MMIO base and per-CPU table length are retained. Policy init sets `dvfs_possible_from_any_cpu = false` to force host-visible writes from the affected vCPU thread, enables fast switch, and installs the virtual scale-frequency source. Exit clears the source and frees any allocated table.

Dependencies and integration points: depends on platform DT compatible, arch topology frequency scaling, CPUFreq core fast-switch/transition APIs, scheduler capacity constants, and host/VMM emulation of the documented register layout.

Risks and test signals: risks include global base pointer for a single device, no explicit locking around table select/read register pairs, freeing `policy->freq_table` even in one-entry continuous mode where it remains NULL, reliance on host current-perf units matching max performance, and rejecting table lengths above 64. Test signals include MMIO region per-CPU stride correctness, policy sharing masks matching perf_domain values, fast-switch writes from the target vCPU, `arch_freq_scale` changing with host current performance, and correct behavior for both discrete and continuous performance tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/virtual-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/Kconfig

Purpose: defines top-level CPU idle configuration symbols, governor choices, architecture submenus, and the haltpoll driver option.

Important APIs and symbols: `CPU_IDLE` enables the generic framework and selects default governors based on tick configuration. Governor symbols include `CPU_IDLE_GOV_LADDER`, `CPU_IDLE_GOV_MENU`, `CPU_IDLE_GOV_TEO`, and `CPU_IDLE_GOV_HALTPOLL`. `DT_IDLE_STATES` and `DT_IDLE_GENPD` enable DT idle-state and generic PM domain parsing support. Architecture submenus source ARM, MIPS, POWERPC, and RISC-V Kconfig fragments. `HALTPOLL_CPUIDLE` depends on x86 KVM guests and selects the haltpoll governor. `ARCH_NEEDS_CPU_IDLE_COUPLED` marks platforms needing coupled idle support.

Control flow and state: Kconfig has no runtime state but controls which core objects, governors, and platform drivers build. Defaults bias CPU idle on for ACPI and pSeries and select a suitable governor based on `NO_HZ`/`NO_HZ_IDLE`.

Dependencies and integration points: integrates with arch-specific Kconfig files under `drivers/cpuidle/`, generic PM domains, KVM guest hints, and Makefile object selection.

Risks and test signals: risks include wrong default governor selection for unusual tick configurations, haltpoll only being available for x86 KVM guests, and architecture submenu symbols hiding platform drivers if arch dependencies are not met. Test signals are expected `.config` symbol selection, correct object inclusion in `drivers/cpuidle/Makefile`, and boot logs showing the intended cpuidle governor/driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/Makefile -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/Makefile

Purpose: maps CPU idle Kconfig symbols to framework, governor, DT helper, and platform driver objects.

Important build flow: core objects `cpuidle.o`, `driver.o`, `governor.o`, `sysfs.o`, and `governors/` always build within the directory. Optional objects include `coupled.o`, `dt_idle_states.o`, `dt_idle_genpd.o`, `poll_state.o`, and `cpuidle-haltpoll.o`. ARM, MIPS, POWERPC, and RISC-V driver objects are selected from their platform symbols, including the files in this group such as `cpuidle-arm.o`, `cpuidle-psci.o`, `cpuidle-powernv.o`, and `cpuidle-pseries.o`.

State and persistence behavior: no runtime state; it determines link-time availability. It also disables branch profiling for this directory when trace branch profiling is configured because idle code can include noinstr-sensitive paths.

Dependencies and integration points: depends on Kconfig symbols generated from top-level and arch-specific menus. Platform init code relies on the selected objects to register drivers at initcall time.

Risks and test signals: risks include missing object selection causing silent platform idle fallback to arch default idle, branch profiling incompatibility if flags are not applied, and stale platform symbols after Kconfig moves. Test signals are clean links for representative ARM/MIPS/POWERPC/RISC-V configs and expected cpuidle driver registration on boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/coupled.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/coupled.c

Purpose: provides the generic coordination engine for coupled CPU idle states, where multiple CPUs must enter a shared low-power state together because of cluster, cache, interrupt-controller, or hardware sequencing constraints.

Important APIs and functions: exported/visible helpers include `cpuidle_coupled_parallel_barrier()`, `cpuidle_state_is_coupled()`, `cpuidle_coupled_state_verify()`, `cpuidle_enter_state_coupled()`, `cpuidle_coupled_register_device()`, and `cpuidle_coupled_unregister_device()`. Internal helpers maintain combined waiting/ready counts, requested state per CPU, poke IPIs through per-CPU `call_single_data_t`, and hotplug prevent/allow transitions.

Control flow and state: each `struct cpuidle_coupled` tracks the coupled CPU mask, requested state array, atomic combined ready/waiting counts, abort barrier, online count, refcount, and prevent flag. Entry has a waiting phase where CPUs use the safe state until all are waiting, a ready phase where all CPUs commit to enter, a pending-poke abort check to avoid lost interrupts, then a simultaneous call into the deepest mutually requested state. CPU hotplug callbacks prevent coupled entry while online masks change and update `online_count`.

Dependencies and integration points: depends on `cpuidle_device.coupled_cpus`, `safe_state_index`, `CPUIDLE_FLAG_COUPLED`, CPU hotplug states, SMP call-function machinery, cpuidle core locks/devices, and platform drivers that provide synchronized low-level idle entry.

Risks and test signals: risks include delicate atomic bit packing, potential refcount bug in unregister where `kfree()` occurs when refcount remains nonzero, global poke masks shared across coupled sets, busy spinning while interrupts are disabled, and strong assumptions about platform enter functions returning with IRQs disabled or safe to reenable. Test signals include coupled state verification rejecting bad safe state, all CPUs entering target state together, poke masks clearing without deadlock, hotplug blocking coupled entry, and no lost wakeups under interrupt storms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/coupled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-arm.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-arm.c

Purpose: generic ARM/ARM64 DT-based cpuidle driver. It registers a per-CPU cpuidle driver with architectural WFI plus DT-described idle states that enter through ARM CPU operations.

Important APIs and functions: `arm_enter_idle_state()` calls `CPU_PM_CPU_IDLE_ENTER(arm_cpuidle_suspend, idx)`. `arm_idle_init_cpu()` duplicates the template driver, sets `drv->cpumask` to one CPU, parses DT idle states starting at index 1 with `dt_init_idle_driver()`, calls `arm_cpuidle_init(cpu)`, registers the driver, and registers cpuidle cooling. `arm_idle_init()` iterates present CPUs and rolls back previously registered drivers on failure.

Control flow and state: the template driver contains state 0 WFI. Per-CPU driver allocations are heap objects retained by cpuidle until unregister. DT idle states must exist beyond WFI or init fails with `-ENODEV`.

Dependencies and integration points: depends on `arm,idle-state` DT nodes, arch `arm_cpuidle_suspend/init`, CPU PM wrappers, cpuidle cooling, and device initcall ordering after CPU devices exist.

Risks and test signals: risks include all-present-CPU rollback freeing drivers only for CPUs before the failure point, `-ENXIO` treated as nonfatal but still no driver for that CPU, no runtime remove path, and DT-only behavior refusing WFI-only systems. Test signals include parsed DT state count, per-CPU cpumasks, arch backend init success or acceptable `-EOPNOTSUPP`, cpuidle cooling registration, and idle state entry reaching the platform CPU ops suspend path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-at91.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-at91.c

Purpose: registers AT91 ARM cpuidle states for simple WFI and WFI plus RAM self-refresh.

Important APIs and functions: `at91_cpuidle_probe()` stores a platform-data standby callback in `at91_standby` and registers `at91_idle_driver`. `at91_enter_idle()` invokes that standby callback and returns the selected index. State 0 uses `ARM_CPUIDLE_WFI_STATE`; state 1 is named `RAM_SR` with 10 us exit latency and 10000 us target residency.

Control flow and state: global state is the function pointer supplied by platform data. There is no remove path because the driver is built-in. The second state delegates all hardware sequencing to the platform callback.

Dependencies and integration points: depends on an AT91 platform device named `cpuidle-at91`, valid platform data, ARM cpuidle helpers, and cpuidle core registration.

Risks and test signals: risks include no NULL check for `at91_standby`, no DT parsing in this file, fixed latency/residency values, and no unregister path. Test signals include platform callback invocation on state 1, WFI state availability, DDR self-refresh observed in platform power registers, and no crash when the platform device binds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-at91.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-big_little.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-big_little.c

Purpose: registers separate ARM big and LITTLE cpuidle drivers for MCPM-based Cortex-A15/A7 systems such as Versatile Express TC2 and Google Peach.

Important APIs and functions: `bl_powerdown_finisher()` programs the MCPM entry vector and calls `mcpm_cpu_suspend()` from a notrace suspend finisher. `bl_enter_powerdown()` wraps `cpu_suspend()` with `cpu_pm_enter/exit`, `ct_cpuidle_enter/exit`, and `mcpm_cpu_powered_up()`. `bl_idle_driver_init()` builds driver cpumasks by CPU part ID. `bl_idle_init()` verifies machine compatibility and MCPM availability, parses DT idle states at index 1, and registers LITTLE then big drivers.

Control flow and state: two static driver templates define WFI plus a powerdown C1 state, with different default latency/residency values for A7 and A15. Runtime state is limited to allocated cpumasks assigned to each driver.

Dependencies and integration points: depends on MCPM, ARM suspend, CPU part ID helpers, DT `arm,idle-state`, and CPU PM/RCU idle context tracking.

Risks and test signals: risks include hard-coded Cortex-A7/A15 part differentiation, cpumask leaks on full success because there is no remove path, reliance on platform-specific MCPM back ends for cluster shutdown policy, and default latency values being platform-specific. Test signals include machine compatible gating, cpumasks containing only matching cores, DT override of state data, successful CPU suspend/resume through MCPM, and rollback freeing cpumasks on registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-big_little.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-calxeda.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-calxeda.c

Purpose: registers Calxeda Highbank cpuidle states for ARM WFI and PSCI-based CPU power gating.

Important APIs and functions: `calxeda_idle_finish()` calls `psci_ops.cpu_suspend()` with a fixed PSCI 0.2 power-down state and `cpu_resume` physical address. `calxeda_pwrdown_idle()` wraps `cpu_suspend()` with `cpu_pm_enter/exit`. The platform driver's probe registers `calxeda_idle_driver`.

Control flow and state: the driver is static and contains WFI plus `PG` power-gate state. No private mutable state is kept.

Dependencies and integration points: depends on PSCI operations being initialized, ARM suspend/resume code, CPU PM notifiers, and a platform device named `cpuidle-calxeda`.

Risks and test signals: risks include no check that `psci_ops.cpu_suspend` is present, fixed PSCI power-state encoding, no unregister path, and minimal error handling from `cpu_suspend()`. Test signals include state 1 invoking PSCI suspend, CPU resume reaching `cpu_resume`, PM notifiers firing, and cpuidle registration only on expected platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-calxeda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-clps711x.c

Purpose: implements the CLPS711X cpuidle driver with a single HALT state backed by an MMIO write.

Important APIs and functions: probe maps the first platform resource into global `clps711x_halt` and registers `clps711x_idle_driver`. `clps711x_cpuidle_halt()` writes `0xaa` to the mapped HALT register and returns the selected index.

Control flow and state: the only runtime state is the global MMIO pointer managed by devm. The driver has one state with exit latency 1 and no separate WFI fallback state.

Dependencies and integration points: depends on a platform device named `clps711x-cpuidle`, MMIO resource mapping, and cpuidle core registration via `builtin_platform_driver_probe`.

Risks and test signals: risks include global MMIO pointer for a single device, no explicit target residency, no unregister path, and the assumption that a write to the HALT register is sufficient and safe in cpuidle context. Test signals include successful resource mapping, HALT register write on idle entry, wakeup from interrupts, and registration of exactly one state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-cps.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-cps.c

Purpose: implements MIPS CPS cpuidle states: coherent wait, non-coherent wait, core clock gating, and core power gating, adapting the available state count to CPS PM support.

Important APIs and functions: `cps_nc_enter()` maps the selected cpuidle index to `enum cps_pm_state`, prevents deeper-than-noncoherent states for CPUs sibling to core 0, wraps power-gated entry in `cpu_pm_enter/exit`, and calls `cps_pm_enter_state()`. `cps_cpuidle_init()` trims state count based on `cps_pm_support_state()`, marks states coupled when `coupled_coherence` requires it, registers the driver, initializes each per-CPU `cpuidle_dev`, optionally sets `coupled_cpus`, and registers devices.

Control flow and state: per-CPU devices live in `per_cpu(cpuidle_dev)`. Driver state count is reduced from deepest to shallowest depending on hardware. Error cleanup unregisters all possible CPU devices and the driver.

Dependencies and integration points: depends on MIPS idle macros, CPS PM support, optional `ARCH_NEEDS_CPU_IDLE_COUPLED`, `cpu_sibling_map`, and CPU PM notifiers for power-gated states.

Risks and test signals: risks include special casing core 0 rather than dynamically ensuring one core remains alive, BUG on invalid index, coupled-state correctness relying on external `coupled_coherence`, and static per-CPU device registration for all possible CPUs. Test signals include boot log limited-state messages, state flags gaining `CPUIDLE_FLAG_COUPLED` on affected systems, successful cpuidle device registration per CPU, and correct refusal to power-gate the last essential sibling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-cps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-exynos.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-exynos.c

Purpose: registers Samsung Exynos cpuidle states, using a coupled idle flow on Exynos4210/Exynos3250 SMP systems and a CPU0-only AFTR low-power state on other supported systems.

Important APIs and functions: `exynos_enter_coupled_lowpower()` calls platform `pre_enter_aftr()`, synchronizes CPUs with `cpuidle_coupled_parallel_barrier()`, runs CPU-specific powerdown or AFTR entry callbacks, synchronizes again, and calls `post_enter_aftr()`. `exynos_enter_lowpower()` falls back to safe WFI unless only CPU0 is online, then calls the platform AFTR entry function. Probe selects the coupled or noncoupled driver based on SMP and machine compatible.

Control flow and state: globals hold `exynos_cpuidle_pdata`, `exynos_enter_aftr`, and the coupled barrier atomic. Driver state 0 is WFI; state 1 is C1 powerdown, with `CPUIDLE_FLAG_COUPLED | CPUIDLE_FLAG_TIMER_STOP` in the coupled variant.

Dependencies and integration points: depends on platform data callbacks from Exynos platform code, ARM suspend helpers, coupled cpuidle support, and cpuidle registration with `cpu_possible_mask` for coupled systems.

Risks and test signals: risks include platform data not being validated, AFTR state only safe for CPU0 when other CPUs are offline, fixed latency/residency values, and coupled barrier correctness depending on both CPUs reaching callbacks. Test signals include coupled driver selected on Exynos4210/3250 SMP, fallback WFI when secondary CPUs are online for noncoupled mode, pre/post callbacks paired, and no CPU stuck at coupled barriers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-exynos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-haltpoll.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-haltpoll.c

Purpose: provides the haltpoll cpuidle driver for x86 KVM guests, intended to work with the haltpoll governor by polling briefly before architectural idle.

Important APIs and functions: `haltpoll_init()` refuses to load when `idle=` overrides are present, requires KVM paravirt plus `KVM_HINTS_REALTIME` unless `force=1`, initializes the poll state, registers the driver, allocates per-CPU devices, and registers CPU hotplug callbacks. `default_enter_idle()` clears polling state and calls `arch_cpu_idle()` if no reschedule is pending. Hotplug callbacks register/unregister devices and call `arch_haltpoll_enable/disable()`.

Control flow and state: state 0 is initialized as the polling state by `cpuidle_poll_state_init()`, and state 1 is architecture idle. Global state stores the percpu device allocation and dynamic hotplug state ID.

Dependencies and integration points: depends on x86 KVM guest paravirtual hints, the haltpoll governor, CPU hotplug framework, arch haltpoll hooks, and scheduler polling flags.

Risks and test signals: risks include force-loading on unsuitable guests, no driver load if boot idle override is set, per-CPU registration failures leaving module init failed, and energy/performance sensitivity to haltpoll governor tuning. Test signals include KVM hint detection, governor `haltpoll` selected, per-CPU devices registered on online, arch haltpoll enabled, and module exit removing hotplug state and freeing percpu devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-haltpoll.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-kirkwood.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-kirkwood.c

Purpose: registers Marvell Kirkwood cpuidle states for WFI and WFI with DDR self-refresh.

Important APIs and functions: probe maps the DDR operation register resource into `ddr_operation_base` and registers `kirkwood_idle_driver`. `kirkwood_enter_idle()` writes `0x7` to the DDR operation register, executes `cpu_do_idle()`, and returns the selected index. Remove unregisters the driver.

Control flow and state: global state is the devm-managed DDR operation MMIO pointer. The driver exposes state 0 WFI and state 1 `DDR SR` with 10 us latency and 100000 us target residency.

Dependencies and integration points: depends on a platform device named `kirkwood_cpuidle`, ARM cpuidle helpers, and the SoC DDR self-refresh register semantics.

Risks and test signals: risks include global MMIO pointer, fixed magic value `0x7`, long target residency assumptions, and no CPU PM notifier wrapping. Test signals include successful resource map, DDR self-refresh request before WFI, wakeup from interrupts, and unregister on module/platform removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-kirkwood.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-mvebu-v7.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-mvebu-v7.c

Purpose: provides cpuidle drivers for Marvell Armada XP, Armada 370, and Armada 38x v7 SoCs using a platform-provided suspend callback.

Important APIs and functions: `mvebu_v7_enter_idle()` wraps the suspend callback in `cpu_pm_enter/exit` and `ct_cpuidle_enter/exit`, passes a boolean `deepidle` when the selected state has `MVEBU_V7_FLAG_DEEP_IDLE`, and returns either the error or state index. Probe selects one of three static driver tables through platform-device ID `driver_data` and stores the platform suspend callback.

Control flow and state: global `mvebu_v7_cpu_suspend` points to platform low-level code. Armada XP has WFI, CPU idle, and deep idle; Armada 370 has WFI plus deep idle; Armada 38x has WFI plus idle. State flags include RCU idle and a private deep-idle bit.

Dependencies and integration points: depends on platform devices with IDs `cpuidle-armada-xp`, `cpuidle-armada-370`, or `cpuidle-armada-38x`, valid platform_data callback, ARM CPU PM tracking, and cpuidle core.

Risks and test signals: risks include no validation of the suspend callback, a typo-like driver name `cpuidle-mbevu`, fixed latency/power values, and no runtime unregister path for built-in driver. Test signals include correct platform ID selecting the expected state table, deepidle boolean matching state flags, CPU PM notifiers firing, and suspend callback returning zero for successful idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-mvebu-v7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-powernv.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-powernv.c

Purpose: registers PowerNV cpuidle states from OPAL/platform idle descriptors, always including snooze and conditionally adding nap, fastsleep, and stop states with acceptable latency.

Important APIs and functions: `snooze_loop()` polls with low SMT priority until reschedule or timeout. `nap_loop()`, `fastsleep_loop()`, and `stop_loop()` enter PowerNV idle mechanisms via `power7_idle_type()` or `arch300_idle_type()`. `powernv_add_idle_states()` filters `pnv_idle_states` by supported flags, latency threshold, PSSCR validity, tick oneshot support, and timebase-stop behavior. `powernv_cpuidle_driver_init()` copies enabled states into the driver and sets `drv->cpumask = cpu_present_mask`. CPU hotplug callbacks enable/disable cpuidle devices.

Control flow and state: static state includes the driver, powernv state table, stop PSSCR table, max state count, snooze timeout configuration, and `cpuidle_state_table`. Probe only succeeds on OPAL firmware without idle override. Snooze timeout uses the next enabled state's target residency when possible.

Dependencies and integration points: depends on PowerNV OPAL firmware, `pnv_idle_states`, PSSCR stop metadata, timebase ticks, runlatch management, tick oneshot for timer-stop states, and CPU hotplug.

Risks and test signals: risks include filtering out high-latency firmware states, special handling when present CPUs differ from possible CPUs, conditional absence of timer-stop states without `CONFIG_TICK_ONESHOT`, snooze polling overhead, and platform firmware validity of stop states. Test signals include discovered states logged/visible under cpuidle sysfs, snooze timeout enabled when deeper states exist, stop states carrying expected PSSCR values, hotplug disable/enable transitions, and no registration when `cpuidle_disable` is set or OPAL is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-powernv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci-domain.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci-domain.c

Purpose: builds generic PM domains for PSCI CPU idle hierarchical topology, allowing cpuidle to coordinate shared domain states through genpd and PSCI OS-initiated mode when available.

Important APIs and functions: `psci_pd_init()` allocates a genpd from DT idle domain states with `dt_idle_pd_alloc()`, sets CPU/IRQ-safe flags, configures power-off behavior depending on OSI support, initializes genpd with `pm_domain_cpu_gov` when states exist, and registers an OF provider. `psci_pd_power_off()` calls `psci_set_domain_state()` with the selected domain state data. Probe scans PSCI child nodes with `#power-domain-cells`, initializes providers, links topology with `dt_idle_pd_init_topology()`, and calls `psci_set_osi_mode()`.

Control flow and state: a global list tracks provider nodes for reverse-order cleanup on failure. In PC mode domains are marked always-on; in OSI mode they can power off and active wakeup is enabled, with PREEMPT_RT forcing runtime PM always-on outside system suspend.

Dependencies and integration points: depends on DT `arm,psci-1.0`, DT idle genpd helpers, PSCI OSI support, generic PM domains, runtime PM, and `cpuidle-psci.c` domain-state handoff.

Risks and test signals: risks include genpd cleanup using plain `kfree()` rather than full `dt_idle_pd_free()` after provider removal, OSI mode failure tearing down all domains, topology requiring correctly nested DT power domains, and PREEMPT_RT limiting runtime idle use. Test signals include provider creation for every CPU power-domain node, topology links in genpd debugfs, log line selecting OSI or PC mode, `psci_pd_power_off()` setting per-CPU domain state, and cleanup on malformed topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci-domain.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.c

Purpose: implements the ARM PSCI cpuidle driver, parsing DT idle states into PSCI suspend parameters and optionally integrating hierarchical CPU power domains for OSI-mode shared states.

Important APIs and functions: `psci_enter_idle_state()` enters a per-CPU PSCI state through `CPU_PM_CPU_IDLE_ENTER_PARAM_RCU(psci_cpu_suspend_enter, ...)`. Domain-aware entry `__psci_enter_domain_idle_state()` wraps CPU PM, genpd runtime/system suspend, optional domain state override, PSCI suspend, tracepoints, rejection accounting, and domain state cleanup. `psci_dt_parse_state_node()` validates `arm,psci-suspend-param`. `psci_idle_init_cpu()` checks CPU enable-method `psci`, allocates a per-CPU driver with WFI state 0, parses DT idle states, initializes per-CPU PSCI state arrays/topology, registers cpuidle, and registers cooling.

Control flow and state: per-CPU `psci_cpuidle_data` stores the PSCI state array and optional attached PM-domain device. Per-CPU `psci_domain_state` carries the domain-selected state for the next idle entry. Global `psci_cpuidle_use_syscore` triggers syscore suspend/resume handling. A faux device owns devm allocations for all per-CPU driver setup.

Dependencies and integration points: depends on DT `arm,idle-state` nodes, CPU `enable-method = "psci"`, initialized `psci_ops.cpu_suspend`, PSCI power-state validation, DT idle genpd attachment, genpd runtime PM, CPU hotplug, syscore ops, trace events, and cpuidle cooling.

Risks and test signals: risks include hierarchical topology limited to OSI, deepest CPU state being reused to trigger domain selection, global syscore flag reset in per-CPU deinit, rollback assuming previous CPUs have registered cpuidle devices, runtime PM differences on PREEMPT_RT, and failure if any present CPU lacks matching PSCI idle states. Test signals include DT suspend params logged, invalid params rejected, per-CPU drivers registered with WFI plus DT states, genpd attached devices for OSI topology, trace_psci_domain_idle events, CPU hotplug PM runtime get/put balance, and domain rejection counters incrementing on failed suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.h -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.h

Purpose: declares the cross-file PSCI cpuidle helpers shared by the PSCI CPU idle driver and PSCI CPU power-domain driver.

Important APIs and types: forward declarations cover `struct device_node` and `struct generic_pm_domain`. `psci_set_domain_state()` lets a genpd power-off callback publish the selected domain state to the current CPU's PSCI idle entry path. `psci_dt_parse_state_node()` parses and validates a DT idle-state node into a PSCI suspend parameter.

Control flow and state: the header has no state; it defines the narrow contract that connects `cpuidle-psci-domain.c` to per-CPU state in `cpuidle-psci.c`.

Dependencies and integration points: depends on `u32` from included kernel types in the including C files and on PSCI driver implementation details.

Risks and test signals: risks include no standalone include of `<linux/types.h>`, so compile success depends on including files having already provided `u32`; API misuse would set domain state outside the intended current-CPU idle path. Test signals are successful compilation of both PSCI files and domain idle entries observing the state selected by genpd.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-pseries.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-pseries.c

Purpose: registers pSeries PowerPC guest cpuidle states for shared and dedicated SPLPAR partitions, using snooze polling and hypervisor cede operations.

Important APIs and functions: `snooze_loop()` polls with low SMT priority until reschedule or timeout. `check_and_cede_processor()` prepares IRQ state and calls `cede_processor()`. `dedicated_cede_loop()` sets `donate_dedicated_cpu` and a cede latency hint in the LPPACA before ceding; `shared_cede_loop()` simply cedes. Extended cede parsing uses RTAS `ibm,get-system-parameter` token 45 to inspect firmware latency records, and `fixup_cede0_latency()` uses the minimum nonzero extended latency as a proxy for CEDE(0). Probe selects shared or dedicated state tables by firmware feature and partition type, then registers cpuidle and hotplug enable/disable callbacks.

Control flow and state: global state includes the selected state table, max state count, snooze timeout, extended cede records, and cede latency hints. Dedicated tables contain snooze and CEDE; shared tables contain snooze and Shared Cede. Snooze timeout is derived from the next state's target residency.

Dependencies and integration points: depends on pSeries firmware SPLPAR, LPPACA fields, RTAS, hypervisor cede wrappers, timebase conversions, runlatch/SMT priority helpers, and CPU hotplug.

Risks and test signals: risks include RTAS payload fixed to 16 records, cede latency fixup only on POWER10/arch 3.1 paths, IRQ state subtleties around H_CEDE returning with interrupts enabled, polling overhead in snooze, and no registration outside SPLPAR. Test signals include correct shared/dedicated table selection, RTAS latency parsing logs, CEDE exit latency adjusted when firmware data exists, LPPACA donate flag restored after idle, and hotplug disabling cpuidle devices for dead CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-pseries.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-qcom-spm.c -->
# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-qcom-spm.c

Purpose: registers Qualcomm SPM-backed ARM cpuidle states for CPUs with `qcom,saw` power controllers, using SCM warm boot setup and SPM low-power mode programming.

Important APIs and functions: `qcom_pm_collapse()` calls `qcom_scm_cpu_power_down(QCOM_SCM_CPU_PWR_DOWN_L2_ON)` and returns failure if the CPU did not power down. `qcom_cpu_spc()` programs SPM `PM_SLEEP_MODE_SPC`, calls `cpu_suspend()`, then resets SPM mode to standby. `spm_enter_idle_state()` wraps that path in `CPU_PM_CPU_IDLE_ENTER_PARAM()`. `spm_cpuidle_register()` finds a CPU's `qcom,saw` phandle, obtains the SPM platform device and drvdata, copies a template driver with a per-CPU cpumask, parses DT idle states compatible with `qcom,idle-state-spc`, and registers cpuidle. Probe verifies SCM availability, sets warm boot address to `cpu_resume_arm`, and registers each present CPU that has SPM.

Control flow and state: each registered CPU gets a devm-allocated `cpuidle_qcom_spm_data` containing the copied driver and SPM pointer. The init function registers a platform driver and only creates the synthetic platform device if at least one available CPU SAW node exists.

Dependencies and integration points: depends on Qualcomm SCM, `soc/qcom/spm` driver data, CPU DT `qcom,saw` phandles, DT idle-state parsing, ARM suspend/resume, CPU PM notifiers, and cpuidle core.

Risks and test signals: risks include partial registration continuing after per-CPU failures, no unregister path for successfully registered per-CPU drivers, dependence on SCM warm boot address setup before any idle entry, SPM mode reset being required to avoid accidental powerdown from generic WFI, and probe deferral until SCM is available. Test signals include SCM warm boot setup success, SPM drvdata present for SAW nodes, per-CPU cpuidle drivers with parsed SPC states, SPM mode returning to standby after idle, and power collapse returning through CPU resume on wake.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-qcom-spm.c -->
