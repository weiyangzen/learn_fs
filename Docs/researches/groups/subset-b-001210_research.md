# subset-b-001210 research

This grouped report covers Linux cpufreq drivers and support headers under `sources/distributed-fs/ceph-client/drivers/cpufreq`. Each file section preserves the source path and uses reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c

## Purpose

Implements CPU frequency scaling for 970FX/SMU based PowerMac G5 systems. It supports two operating points, high and low, using either SCOM register programming on SMU-era Neo2 systems or PowerMac platform functions on PowerMac7,2/7,3 and RackMac3,1.

## APIs, Types, And Functions

The cpufreq core entry points are `g5_cpufreq_cpu_init()`, `g5_cpufreq_target()`, and `g5_cpufreq_get_speed()` in `g5_cpufreq_driver`. Hardware-facing callbacks are selected through global function pointers `g5_switch_volt`, `g5_switch_freq`, and `g5_query_freq`. The SCOM path uses `g5_scom_switch_freq()` and `g5_scom_query_freq()` with PCR/PSR bitfields. The platform-function path uses `g5_pfunc_switch_freq()`, `g5_pfunc_switch_volt()`, and lookup of `pmf_function` handles.

## Control Flow

`g5_cpufreq_init()` locates CPU0's OF node and dispatches by machine compatible. Neo2 initialization validates CPU version, reads `power-mode-data`, discovers SMU FVT or VD-NAP platform functions, computes high/low frequencies from `clock-frequency`, synchronizes voltage and current mode, then registers the driver. PM72 initialization discovers the cpuid EEPROM and i2c clock node, resolves get/set/slewing platform functions, computes the low frequency from EEPROM ratios, synchronizes state, and registers.

## State And Persistence

Global state holds the two-entry `g5_cpu_freqs`, current mode `g5_pmode_cur`, OF-provided power mode data, SMU FVT data, and retained platform-function handles. The persistent hardware state is voltage and CPU clock mode in SMU/SCOM or i2c/platform-function controlled devices. `ppc_proc_freq` is updated after transitions. There is no unregister/remove path beyond module init registration.

## Dependencies And Integration Points

Depends on Open Firmware machine compatibles, PowerMac platform functions, SMU simple commands, `scom970_read/write`, PowerPC `ppc_proc_freq`, and the cpufreq table API. Integration is restricted to supported G5 machine families and CPU0-derived policy.

## Risks And Test Signals

Transition ordering is critical: voltage is raised before increasing frequency and lowered after decreasing frequency. Slewing wait loops poll for at most about 100 ms and only warn on timeout, so incomplete hardware transitions can still update software state. Test signals include boot logs naming frequency/voltage methods, correct high/low rates, SCOM PSR readback, platform-function slewing completion, and stable operation across repeated target changes and suspend/resume-style firmware state changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pmac64-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c

## Purpose

Provides cpufreq support for AMD K6-2+/K6-3+ PowerNow processors by changing the CPU multiplier through the K6 EPMR-enabled PowerNow I/O port.

## APIs, Types, And Functions

`powernow_k6_driver` supplies `init`, `exit`, `target_index`, `get`, and generic table verification. `clock_ratio` maps cpufreq indices to multiplier values, while `index_to_register` and `register_to_index` translate between table order and BVC register encoding. Module parameters `max_multiplier` and `bus_frequency` override frequency detection.

## Control Flow

`powernow_k6_init()` verifies AMD family/model support, reserves the fake PowerNow I/O window, and registers cpufreq. `powernow_k6_cpu_init()` only accepts CPU0, infers max multiplier from `cpu_khz` against `usual_frequency_table` unless overridden, computes FSB in 10 kHz units, fills the frequency table, and sets latency. Targeting validates the requested multiplier and calls `powernow_k6_set_cpu_multiplier()`.

## State And Persistence

Global `busfreq` and `max_multiplier` persist derived platform state. The hardware multiplier is read and changed by enabling `MSR_K6_EPMR`, accessing `POWERNOW_IOPORT + 0x8`, then disabling the port. During writes, interrupts are disabled, CR0 cache disable is set, and `wbinvd()` flushes cache while the processor may stop responding to inquiry cycles.

## Dependencies And Integration Points

Depends on x86 CPU matching, MSR access, I/O port reservation, `cpu_khz`, and the cpufreq frequency table core. It integrates only as a uniprocessor CPU0 driver.

## Risks And Test Signals

The driver is hazardous by design: wrong FSB or max multiplier parameters can produce invalid rates, and multiplier writes disable cache and interrupts. CPU exit attempts to restore the maximum multiplier. Test signals are successful I/O region reservation, correct multiplier readback from `get`, table invalidation above max multiplier, and stable transitions across every valid table entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c

## Purpose

Implements AMD K7 PowerNow frequency and voltage scaling using either BIOS PSB/PST tables or ACPI performance objects. It handles Athlon mobile-era FID/VID transitions and A0 stepping errata.

## APIs, Types, And Functions

Important types are local PSB/PST structs, ACPI control decoding, and the global `powernow_table`. `check_powernow()` probes CPUID capabilities, `powernow_decode_bios()` scans low BIOS memory for `AMDK7PNOW!`, `powernow_acpi_init()` builds state from ACPI, and `powernow_target()` writes FID/VID MSRs. `change_FID()` and `change_VID()` manipulate `MSR_K7_FID_VID_CTL` using bit layouts from `powernow-k7.h`.

## Control Flow

Late init registers the driver only if CPUID reports PowerNow capability. CPU init recalibrates `cpu_khz`, derives FSB from current FID, rejects non-CPU0 policies, then prefers BIOS PST unless DMI or `acpi_force` selects ACPI. BIOS tables are matched on CPUID, FSB, max FID, and start VID. ACPI states are translated to FID/VID pairs and may correct reported MHz values. The target path reads current FID, computes old/new rates, applies A0 interrupt masking when needed, then lowers frequency before voltage when going down or raises voltage before frequency when going up.

## State And Persistence

Global mutable state includes capability flags, FSB, min/max speeds, settling latency, `have_a0`, and allocated `powernow_table`; ACPI state is retained in `acpi_processor_perf` when used. Hardware state persists in K7 FID/VID MSRs. Exit unregisters ACPI performance data and frees the table.

## Dependencies And Integration Points

Uses x86 CPUID/MSR access, ACPI processor performance support, DMI blacklist matching, BIOS physical memory scanning, recalibration helpers, and cpufreq table verification. It optionally exposes ACPI BIOS limit handling.

## Risks And Test Signals

Malformed firmware tables can program unsafe FID/VID pairs; the driver contains explicit warnings and DMI disablement for known broken Acer BIOSes. Half multipliers are invalidated for A0/ACPI errata. Test signals include decoded PST/ACPI entries, SGTC calculation, min/max logs, current frequency read from `MSR_K7_FID_VID_STATUS`, and successful fallback from BIOS to ACPI on missing PST data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h

## Purpose

Defines the AMD K7 FID/VID control and status MSR layouts consumed by `powernow-k7.c`.

## APIs, Types, And Functions

`union msr_fidvidctl` maps control fields for target FID, VID, change command bits `FIDC`/`VIDC`, `FIDCHGRATIO`, and `SGTC`. `union msr_fidvidstatus` maps current, start, and maximum FID/VID fields from the status MSR. The unions expose both bitfield views and a 64-bit `val` for `rdmsrq()`/`wrmsrq()`.

## Control Flow

The header has no executable control flow. Callers read a status MSR into `msr_fidvidstatus`, derive current or limit fields, update `msr_fidvidctl.bits`, and write the combined value back to request hardware transitions.

## State And Persistence

No software state is stored here. The definitions describe persistent processor MSR state owned by hardware.

## Dependencies And Integration Points

Integrated only by the K7 PowerNow driver and the x86 MSR accessors. Field widths and ordering are part of the ABI between the driver and AMD hardware.

## Risks And Test Signals

Bitfield layout correctness is the main risk; any compiler/architecture mismatch or wrong field width would write unsafe voltage/frequency requests. Test signals come indirectly from K7 driver transitions: status reads must reflect requested `FID`/`VID`, and SGTC-controlled transitions must complete without hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c

## Purpose

Implements legacy AMD K8 Athlon64/Opteron PowerNow support for processors without hardware P-state support, using ACPI `_PSS` where possible and deprecated BIOS PSB tables as a uniprocessor fallback.

## APIs, Types, And Functions

The cpufreq driver `cpufreq_amd64_driver` provides async-notified target, get, init, exit, and ACPI BIOS limits. Per-policy/per-core state is `struct powernow_k8_data`. Core transition helpers are `core_voltage_pre_transition()`, `core_frequency_transition()`, `core_voltage_post_transition()`, and `transition_frequency_fidvid()`. Firmware table loaders are `powernow_k8_cpu_init_acpi()`, `find_psb_table()`, `fill_powernow_table()`, and `fill_powernow_table_fidvid()`.

## Control Flow

Late init rejects non-K8 CPUs and CPUs with `X86_FEATURE_HW_PSTATE`, requesting `acpi-cpufreq` instead. CPU init validates support on the target CPU, allocates state, loads ACPI or single-CPU PSB tables, computes transition latency, initializes the FID/VID MSR on the target CPU, sets the policy cpumask to the topology core mask, and stores the same data pointer for all CPUs in the policy. Targeting runs on the policy CPU with `work_on_cpu()`, checks the pending bit, refreshes current FID/VID, serializes with `fidvid_mutex`, decodes ACPI transition parameters for the selected state, and executes the three-phase transition.

## State And Persistence

Per-CPU `powernow_data` points at shared policy state containing current FID/VID, ACPI performance data, transition timing parameters, and the cpufreq table. Hardware state persists in `MSR_FIDVID_CTL` and `MSR_FIDVID_STATUS`. Exit unregisters ACPI performance data, frees the table and state, and clears per-CPU pointers for related CPUs.

## Dependencies And Integration Points

Depends on x86 CPUID, MSR access, topology core masks, ACPI processor performance, optional BIOS physical memory scanning, and cpufreq target execution on a specific CPU. It defers newer hardware to `acpi-cpufreq`.

## Risks And Test Signals

Transition correctness depends on pending-bit polling, voltage step limits, max VID/RVO validation, VCO FID stepping, and ACPI/PSB table sanity. Failures return `-EIO` or log detailed FID/VID mismatches. Test signals include "Found ... powernow-k8" init logs, ACPI `_PSS` decoding, PSB validation, `get` frequency from current FID, and stress transitions across low/high FID boundary cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h

## Purpose

Defines the state structure, MSR constants, FID/VID limits, ACPI control-field masks, and BIOS PSB/PST table layouts used by `powernow-k8.c`.

## APIs, Types, And Functions

`struct powernow_k8_data` stores CPU id, number of P-states, transition timing fields, current FID/VID, cpufreq table pointer, ACPI performance data, and associated core mask. `struct psb_s` and `struct pst_s` describe BIOS PowerNow table records. Constants cover `MSR_FIDVID_CTL`, `MSR_FIDVID_STATUS`, pending/status bits, low/high FID table rules, valid frequency/VID ranges, and `_PSS` control extraction masks. The header also forward-declares transition helpers shared within the C file.

## Control Flow

The header itself has no runtime flow. It constrains the K8 driver's ACPI and PSB parsing and the sequence of MSR writes during transitions.

## State And Persistence

No standalone persistent state exists in the header. It documents software state in `powernow_k8_data` and hardware-persistent FID/VID MSR fields.

## Dependencies And Integration Points

Integrated with ACPI processor performance structures, cpufreq tables, cpumasks, and x86 MSR operations. The PSB signature and version constants define compatibility with BIOS-provided tables.

## Risks And Test Signals

Incorrect masks or FID/VID bounds could make table validation unsound and allow unsafe MSR writes. Test evidence is indirect: K8 ACPI/PSB table loading must reject invalid VID/FID values, extended `_PSS` decoding must pick the expected fields, and transitions must leave `currfid/currvid` matching requested values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernow-k8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c

## Purpose

Provides cpufreq support for IBM/OpenPOWER bare-metal PowerNV systems using OPAL firmware P-state descriptions and POWER PMCR/PMSR special-purpose registers. It also tracks OCC throttling and POWER8 global-pstate ramp-down behavior.

## APIs, Types, And Functions

Global firmware data is held in `powernv_freqs`, `pstate_revmap`, and `powernv_pstate_info`. `struct global_pstate_info` tracks timer-based global pstate ramp-down per policy, while `struct chip` tracks per-chip throttle state and work. Main cpufreq callbacks are `powernv_cpufreq_cpu_init()`, `powernv_cpufreq_target_index()`, `powernv_fast_switch()`, `powernv_cpufreq_get()`, and `powernv_cpufreq_cpu_exit()`. Initialization uses `init_powernv_pstates()` and `init_chip_info()`.

## Control Flow

Module init requires OPAL firmware, reads `/ibm,opal/power-mgt` pstate min/max/nominal/turbo properties, builds the cpufreq table and reverse map, creates chip masks, enables software boost for WOF platforms, registers cpufreq, then registers reboot and OPAL OCC notifiers. Targeting converts table index to local/global pstate ids, checks throttling, optionally updates POWER8 global pstate ramp-down state, and sends `set_pstate()` to one CPU in the policy. Fast switch writes PMCR directly for the current CPU.

## State And Persistence

Persistent hardware state is PMCR/PMSR local, global, and max pstate fields. Software state includes global throttle booleans, per-chip counters exposed in sysfs `throttle_stats`, per-policy timers, reverse-map hashtable entries, and notifier registrations. Reboot notifier forces nominal pstate and suppresses non-nominal requests. Exit unregisters cpufreq/notifiers and cancels chip work.

## Dependencies And Integration Points

Depends on OPAL device-tree properties, firmware feature checks, PowerPC SPR access, OPAL OCC messages, reboot notifiers, sysfs cpufreq attributes, CPU/thread topology, and tracepoint `powernv_throttle`.

## Risks And Test Signals

Risks include invalid firmware pstate tables, stale reverse-map defaults to nominal, timer migration races, OCC throttle restoration, and fast-switch bypass of cached global pstate state. Test signals include pstate table logs, `cpuinfo_nominal_freq`, throttle stat counters, trace events on Pmax changes, PMCR/PMSR readback, reboot nominal transition, and POWER8 timer ramp-down behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h

## Purpose

Defines the `powernv_throttle` tracepoint used by the PowerNV cpufreq driver to report chip-level throttling and unthrottling events.

## APIs, Types, And Functions

The `TRACE_EVENT(powernv_throttle)` prototype accepts chip id, reason string, and Pmax value. It records `chip_id`, a dynamic string `reason`, and `pmax`, then formats them for tracing. `TRACE_SYSTEM` is set to `power`, and `TRACE_INCLUDE_FILE` points back to `powernv-trace`.

## Control Flow

The header is included with `CREATE_TRACE_POINTS` by `powernv-cpufreq.c`, generating tracepoint definitions. Runtime calls occur from `powernv_cpufreq_throttle_check()` when Pmax capping state changes.

## State And Persistence

The header stores no state. Trace buffers hold emitted events according to ftrace/perf configuration.

## Dependencies And Integration Points

Depends on Linux tracepoint infrastructure and must keep the include guard plus `trace/define_trace.h` outside the guard as required by trace event headers.

## Risks And Test Signals

The main risk is trace-header misuse causing duplicate or missing trace definitions. Test signals include a build with `CREATE_TRACE_POINTS`, visibility of `power:powernv_throttle`, and emitted events containing the chip id, reason, and Pmax during OCC/PMSR throttling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/powernv-trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c

## Purpose

Implements cpufreq for Intel/Marvell PXA25x and PXA27x SoCs using fixed frequency tables, the core clock, and optional VCC core voltage scaling.

## APIs, Types, And Functions

`struct pxa_freqs` stores kHz and regulator voltage bounds. Tables cover PXA255 run/turbo modes and PXA27x frequencies. `find_freq_tables()` selects the active table, `pxa_cpufreq_init_voltages()` discovers `vcc_core`, `pxa_set_target()` sequences voltage and `clk_set_rate()`, and `pxa_cpufreq_driver` exposes cpufreq callbacks.

## Control Flow

Module init gets the global `"core"` clock and registers the driver only for PXA25x/PXA27x. Policy init guesses or applies `pxa27x_maxfreq`, initializes voltage support, materializes cpufreq tables, invalidates PXA27x entries above max frequency, and selects the policy table. Targeting raises voltage before increasing frequency, sets the core clock rate, then lowers voltage after decreasing frequency.

## State And Persistence

Global state includes `pxa_cpufreq_data.clk_core`, optional `vcc_core`, module parameters, and generated tables. Hardware state persists in clock dividers/PLL state and regulator output. The driver does not release the clock in module exit.

## Dependencies And Integration Points

Depends on PXA CPU identification helpers, common clock API, optional regulator framework, cpufreq generic table verification, and module parameters for board-specific maximum frequency.

## Risks And Test Signals

The file warns that memory-bus changes require platform-specific timing notifiers, but the driver does not provide them. Downward voltage errors are ignored after a successful clock change. Test signals include generated table contents, rounded clock support, regulator availability logs, `clk_get_rate()` based `get`, and board stability for memory/flash timings at each frequency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa2xx-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c

## Purpose

Provides PXA3xx CPU frequency scaling by programming ACCR core and bus clock fields for PXA300/PXA310/PXA320 operating points.

## APIs, Types, And Functions

`struct pxa3xx_freq_info` stores CPU MHz, ACCR field values, DFI divider, and voltage metadata. Static tables describe PXA300 and PXA320 points. `setup_freqs_table()` allocates a cpufreq table, `__update_core_freq()` updates XL/XN and XSPCLK fields through `pxa3xx_clk_update_accr()`, and `__update_bus_freq()` updates memory/static bus selectors.

## Control Flow

Init registers only on PXA3xx. Policy init sets fixed min/max, chooses PXA300/PXA310 or PXA320 table, and installs it. Targeting only accepts CPU0, disables local IRQs, updates core PLL fields, then bus frequency fields, and restores IRQs.

## State And Persistence

Global pointers retain the selected operating-point array and allocated cpufreq table. Hardware state persists in ACCR and related clock registers. Voltage fields are descriptive in this driver and are not applied through regulators.

## Dependencies And Integration Points

Depends on PXA CPU identification, PXA clock helper `pxa3xx_clk_update_accr()`, `pxa3xx_get_clk_frequency_khz()`, and cpufreq table APIs.

## Risks And Test Signals

Clock register sequencing is interrupt-protected but lacks regulator handling despite voltage data. The global allocated table is not freed on driver exit. Test signals include correct CPU family detection, ACCR field readback for every operating point, current frequency from PXA clock helper, and stable memory/static bus operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/pxa3xx-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c

## Purpose

Drives Qualcomm CPUFreq HW/EPSS blocks that expose memory-mapped frequency domains, hardware LUTs, performance-state registers, optional interconnect/OPP scaling, CPU clocks, and LMh hardware throttling notifications.

## APIs, Types, And Functions

`struct qcom_cpufreq_soc_data` defines register offsets and LUT stride per hardware variant. `struct qcom_cpufreq_data` holds a domain MMIO base, throttle IRQ/work state, policy pointer, CCF `clk_hw`, and per-core DCVS flag. Key functions are `qcom_cpufreq_hw_read_lut()`, `qcom_cpufreq_hw_target_index()`, `qcom_cpufreq_hw_fast_switch()`, `qcom_lmh_dcvs_notify()`, `qcom_cpufreq_hw_cpu_init()`, and platform probe/remove.

## Control Flow

Platform probe gets `xo` and `alternate` clocks, checks CPU0 ICC paths, maps all frequency-domain resources, registers a CCF clock per domain, publishes an OF onecell clock provider, and registers cpufreq at postcore init. CPU policy init parses `qcom,freq-domain`, verifies hardware enable, detects per-core DCVS, builds related CPU mask, reads the LUT into dynamic OPP and cpufreq entries, and initializes optional LMh IRQ. Targeting writes a table index to the performance-state register, mirroring per-core offsets when required, and updates bandwidth through OPP if ICC scaling is enabled.

## State And Persistence

Persistent hardware state is MMIO performance state, DCVS control, current vote/domain state, and interrupt status. Software state includes domain array, dynamic OPPs, allocated frequency table, throttle work, IRQ affinity, and registered CPU clocks. CPU exit removes dynamic OPPs, OF OPP tables, LMh IRQ, and the table.

## Dependencies And Integration Points

Depends on platform resources, OF `qcom,freq-domain`, common clock, OPP, interconnect paths, IRQ handling, workqueues, architecture thermal pressure updates, and cpufreq cooling/boost/energy-model integration.

## Risks And Test Signals

The global `icc_scaling_enabled` is shared across policies and follows CPU0/LUT parsing assumptions. LMh IRQ flow alternates interrupt and polling and must avoid re-enabling during teardown. Test signals include LUT-derived OPP count, boost marking, performance-state MMIO writes, per-core DCVS writes, CPU clock rate reads, ICC bandwidth updates, LMh thermal pressure updates, and clean online/offline IRQ affinity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c

## Purpose

Configures Qualcomm CPU OPP selection from NVMEM speed-bin fuses, SMEM SoC ids, PVS names, and optional power domains, then instantiates the generic `cpufreq-dt` platform device.

## APIs, Types, And Functions

`struct qcom_cpufreq_match_data` describes SoC-specific version decoding and power-domain names. `struct qcom_cpufreq_drv` stores the selected `supported_hw` bitmask and per-CPU OPP/power-domain tokens. Version helpers cover simple speedbin, Kryo, Krait formats A/B, IPQ8064, IPQ6018, and IPQ8074. Probe/remove manage OPP config and `cpufreq-dt` registration.

## Control Flow

Module init matches the machine compatible, registers the platform driver, and creates a data-bearing platform device. Probe validates the CPU0 OPP descriptor compatible, allocates per-CPU state, reads NVMEM if required, computes `drv->versions` and optional `pvs_name`, then for each present CPU applies OPP config and attaches required performance domains. Finally it registers `cpufreq-dt`; remove unregisters it and clears OPP/domain state.

## State And Persistence

Global platform-device pointers track the wrapper and delegated `cpufreq-dt` device. Per-CPU state retains OPP config tokens and attached PM domain lists. Persistent hardware input is fuse/NVMEM and SMEM SoC identity; this driver does not change clocks directly.

## Dependencies And Integration Points

Depends on NVMEM cells, Qualcomm SMEM ids, DT OPP v2 compatible strings, OPP `supported_hw`/property-name selection, generic PM domains with required OPP links, and the `cpufreq-dt` driver.

## Risks And Test Signals

Wrong fuse decoding hides valid OPPs or exposes unsafe ones. Several fallbacks intentionally limit frequency for unknown SoC ids. Test signals include selected version bitmask, PVS property name, successful `dev_pm_opp_set_config()` on every CPU, attached performance domains, `cpufreq-dt` platform creation, and correct OPP availability under `/sys/devices/system/cpu`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qcom-cpufreq-nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c

## Purpose

Implements cpufreq for Freescale/NXP QorIQ SoCs by switching the CPU clock parent among available parent clocks.

## APIs, Types, And Functions

`struct cpu_data` stores parent clock pointers and the allocated frequency table. `get_bus_freq()` derives platform bus frequency from DT or a named clock for latency calculation. `set_affected_cpus()` finds CPUs sharing the same clock. `freq_table_redup()` invalidates duplicate rates and `freq_table_sort()` sorts entries descending.

## Control Flow

Platform probe refuses known erratum A-008083 clockgens, then registers cpufreq. Policy init gets the CPU node and CPU clock, enumerates its parents through `clk_hw`, builds a parent-indexed frequency table, removes duplicates, sorts it, computes shared CPUs, stores driver data, and sets transition latency to 12 platform clocks. Targeting sets the CPU clock parent based on the selected table entry.

## State And Persistence

Per-policy allocated state retains parent clock pointers and the frequency table until exit. Hardware state persists as the CPU clock parent selection. No direct register writes are performed here.

## Dependencies And Integration Points

Depends on OF CPU nodes, clock parents, `clk_set_parent()`, platform bus frequency properties/clocks, cpufreq cooling flag, and platform-device creation under name `qoriq-cpufreq`.

## Risks And Test Signals

The table assumes parent clock rates are valid and fixed enough for cpufreq policy use. Error paths collapse many failures to `-ENODEV`. Test signals include blacklist behavior, table ordering/deduplication, related CPU mask for shared clocks, transition latency, and parent-clock readback after target changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/qoriq-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c

## Purpose

Creates runtime OPPs for Raspberry Pi CPUs from firmware-backed clock min/max rates and delegates actual scaling to `cpufreq-dt`.

## APIs, Types, And Functions

The platform driver implements `raspberrypi_cpufreq_probe()` and `raspberrypi_cpufreq_remove()`. It uses `RASPBERRYPI_FREQ_INTERVAL` as the 100 MHz step when creating OPPs.

## Control Flow

Probe gets CPU0, obtains its clock, asks the clock provider for rounded minimum and maximum rates, creates zero-voltage OPPs every 100 MHz between them, and registers a `cpufreq-dt` platform device. On failure or remove it removes all dynamic OPPs and unregisters the delegated platform device.

## State And Persistence

The only driver-owned state is the global `cpufreq_dt` platform-device pointer and dynamic OPPs on CPU0. Persistent frequency behavior is owned by Raspberry Pi firmware/clock driver and `cpufreq-dt`.

## Dependencies And Integration Points

Depends on `clk-raspberrypi` availability, CPU0 device lookup, OPP core dynamic tables, and generic `cpufreq-dt`.

## Risks And Test Signals

The OPP list assumes 100 MHz granularity between rounded min and max; unusual firmware ranges could miss valid rates or include unsupported ones if rounding semantics change. Test signals include CPU0 clock probe deferral, dynamic OPP count, `cpufreq-dt` registration, and available frequencies matching firmware limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/raspberrypi-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs

## Purpose

Rust implementation of the generic `cpufreq-dt` driver. It builds OPP-backed cpufreq policies from DT/firmware nodes, CPU clocks, optional regulators, and OPP sharing data.

## APIs, Types, And Functions

`CPUFreqDTDevice` owns the OPP table, cpufreq table, cpumask, optional OPP config token, and CPU clock. `CPUFreqDTDriver` implements `opp::ConfigOps`, `cpufreq::Driver`, and `platform::Driver`. Helper functions discover exact `cpu0-supply`/`cpu-supply` regulator names.

## Control Flow

Policy init gets the CPU device, creates a cpumask, optionally configures regulator names, determines OPP sharing via `operating-points-v2` or legacy OPP sharing, loads OPPs from OF or existing dynamic tables, validates OPP count, applies fallback sharing to all CPUs if needed, sets transition latency and suspend frequency, installs the cpufreq table, sets the CPU clock, copies the final cpumask to the policy, and returns an `Arc` holding resources. Targeting looks up the selected table frequency and calls `opp_table.set_rate()`.

## State And Persistence

State is owned by the `Arc<CPUFreqDTDevice>` stored as policy data; RAII ownership keeps the OPP table, freq table, config token, cpumask, and clock alive while C cpufreq holds raw references. Online/offline are lightweight and intentionally preserve policy data. Hardware state is managed by OPP/clock/regulator frameworks.

## Dependencies And Integration Points

Integrates with Rust kernel abstractions for CPU devices, cpufreq, OPP, cpumasks, platform drivers, C strings, and OF matching on `operating-points-v2`. It registers energy model data through OPP and supports boost flags.

## Risks And Test Signals

Safety relies on lifetime assumptions around C-visible cpufreq table and clock references, documented with `unsafe` comments. Test signals include successful OF match, OPP loading or `EPROBE_DEFER`, correct sharing cpumask, regulator-name config, transition latency fallback, `opp_table.set_rate()` success, suspend frequency, and stable hotplug online/offline without freeing policy data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/rcpufreq_dt.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s3c64xx-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/s3c64xx-cpufreq.c

## Purpose

Implements Samsung S3C64xx cpufreq using the ARM clock and optional VDDARM regulator voltage ranges.

## APIs, Types, And Functions

`struct s3c64xx_dvfs` maps table voltage ranges. `s3c64xx_freq_table` contains supported frequencies and DVFS indices. `s3c64xx_cpufreq_config_regulator()` invalidates table entries unsupported by the regulator. `s3c64xx_cpufreq_set_target()` sequences voltage and clock rate changes.

## Control Flow

Driver init registers cpufreq. Policy init only accepts CPU0, gets `armclk`, tries to get `vddarm`, filters entries by regulator and clock `clk_round_rate()`, invalidates frequencies above boot rate if no regulator exists, then calls `cpufreq_generic_init()`. Targeting raises voltage before increasing clock, sets clock rate, and lowers voltage after decreasing clock; if post-downscale voltage fails, it attempts to restore the old clock.

## State And Persistence

Global `vddarm` and `regulator_latency` persist regulator state, while the static frequency table is modified in place to invalidate unsupported entries. Hardware state persists in clock and regulator settings.

## Dependencies And Integration Points

Depends on common clock, regulator framework, cpufreq generic initialization, and board-specific regulator naming.

## Risks And Test Signals

The static table is mutated globally and not restored on unload/reload. If no regulator is present, only frequencies no higher than boot are allowed. Test signals include unsupported clock/regulator entries becoming invalid, actual clock rate logs, transition latency including regulator estimate, and voltage rollback behavior on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s3c64xx-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c

## Purpose

Provides Samsung S5PC110/S5PV210 cpufreq by directly programming clock-controller and DMC memory-controller registers, regulators, and reboot/suspend-safe frequency behavior.

## APIs, Types, And Functions

Static tables describe five performance levels, per-level DVS voltages, and clock divider values. `s5pv210_set_refresh()` recomputes DMC refresh counters. `s5pv210_target()` is the central transition sequence. `check_mem_type()` restricts support to LPDDR/LPDDR2. Probe maps clock/DMC registers, gets regulators, and registers cpufreq.

## Control Flow

Probe obtains `vddarm`/`vddint`, maps the `samsung,s5pv210-clock` node and two DMC nodes, registers a reboot notifier, and registers cpufreq. Policy init gets `armclk`, DMC clocks, validates CPU0 and memory type, snapshots original DMC refresh values/rates, sets `suspend_freq`, and installs the table. Targeting serializes with `set_freq_lock`, rejects access after reboot lockout, raises voltages for upscaling, adjusts temporary DRAM refresh for bus changes, switches MFC/G3D and MSYS muxes around APLL changes, rewrites dividers and APLL PMS values, restores refresh counters, then lowers voltages for downscaling.

## State And Persistence

Global mapped bases, DMC clocks, regulators, DRAM refresh snapshots, mutex, and `no_cpufreq_access` persist for the built-in platform driver lifetime. Hardware state persists in PLL, mux, divider, MCS, ONEDRAM, DMC refresh, and regulator registers. Reboot notifier drives the CPU to 800 MHz and disables later access.

## Dependencies And Integration Points

Depends on OF node mapping, Samsung clock/DMC register layout, regulators, common clock lookup, reboot notifier, cpufreq generic suspend, and CPU0-only policy assumptions.

## Risks And Test Signals

This is high-risk sequencing: direct MMIO polling loops have no timeout, memory refresh changes must be correct, and only LPDDR/LPDDR2 are supported. Probe lacks a remove path because it is a built-in platform driver. Test signals include register mapping, DMC aliases, memory type, refresh counter readback, PLL lock/mux status completion, regulator changes, reboot transition to `SLEEP_FREQ`, and memory stability across L0/L4 transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/s5pv210-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c

## Purpose

Implements SA1110 CPU frequency scaling with SDRAM timing recalculation. It handles memory refresh/timing programming during PPCR clock changes for known SDRAM parts.

## APIs, Types, And Functions

`struct sdram_params` describes SDRAM timing, and `struct sdram_info` holds computed MDCNFG/MDREFR/MDCAS values. `sdram_calculate_timing()`, `sdram_update_refresh()`, and `sdram_set_refresh()` compute and apply memory timings. `sa1110_target()` performs the actual clock transition. `sa1110_find_sdram()` selects a timing profile from the module parameter or machine defaults.

## Control Flow

Arch init checks for SA1110, chooses SDRAM type from `cpu_sa1110.sdram=` or machine defaults, copies timing parameters, and registers cpufreq. CPU init installs the shared `sa11x0_freq_table`. Targeting calculates new SDRAM timings for the selected frequency, temporarily sets aggressive refresh, waits, disables interrupts, executes an aligned inline assembly block to program memory controller registers and PPCR without SDRAM accesses, restores interrupts, then updates refresh for the new frequency.

## State And Persistence

Global `sdram_params` stores selected memory timing. Hardware state persists in MDCNFG, MDREFR, MDCAS0-2, and PPCR. There is no module exit path because registration happens through `arch_initcall`.

## Dependencies And Integration Points

Depends on SA1100 machine headers, `sa11x0_freq_table`, `sa11x0_getspeed`, CPU revision checks, machine ID helpers, and direct memory controller registers.

## Risks And Test Signals

Incorrect SDRAM part selection can corrupt memory during transitions. The driver refuses no explicit unsupported SDRAM name by simply not registering. Test signals include selected SDRAM timing debug, CPU revision behavior for delayed latching, refresh counter values, successful transitions across table entries, and memory integrity under stress after frequency changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sa1110-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c

## Purpose

Provides cpufreq support for AMD Elan SC520 by toggling the CPU control register between 100 MHz and 133 MHz modes.

## APIs, Types, And Functions

`sc520_freq_table` contains the two hardware encodings. `sc520_freq_get_cpu_frequency()` reads the mapped CPUCTL register and decodes bits 1:0. `sc520_freq_target()` writes the selected encoding with interrupts disabled. `sc520_freq_driver` wires generic table verify, target, get, and init.

## Control Flow

Module init checks AMD family/model support, maps `MMCR_BASE + OFFS_CPUCTL`, and registers cpufreq. Policy init repeats capability checks, sets 1 ms latency, and installs the table. Targeting masks CPUCTL low bits and writes the selected value. Exit unregisters and unmaps.

## State And Persistence

The global `cpuctl` pointer stores the MMIO mapping. Hardware state persists in CPUCTL clock-speed bits.

## Dependencies And Integration Points

Depends on x86 CPU matching, fixed SC520 MMCR address, `ioremap`, and cpufreq table APIs.

## Risks And Test Signals

Only two encodings are valid; unexpected register values log an error and report 100 MHz. Test signals include MMIO mapping success, cpufreq table visibility, CPUCTL readback after target, and correct cleanup on module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sc520_freq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c

## Purpose

Implements cpufreq over ARM SCMI Performance Protocol domains, using firmware-provided OPPs, frequency set/get operations, fast channels when available, performance limit notifications, and energy-model data.

## APIs, Types, And Functions

`struct scmi_data` stores domain id, OPP count, CPU device, OPP sharing mask, limit notifier, and frequency QoS request. Main callbacks are `scmi_cpufreq_init()`, `scmi_cpufreq_set_target()`, `scmi_cpufreq_fast_switch()`, `scmi_cpufreq_get_rate()`, `scmi_cpufreq_exit()`, and `scmi_cpufreq_register_em()`. Helpers discover domain ids from `clocks` or `power-domains` and compute sharing CPUs.

## Control Flow

SCMI driver probe verifies the SCMI device is referenced by CPUs, obtains the performance protocol handle, optionally registers a dummy clock provider, and registers cpufreq. Policy init gets the CPU device/domain, allocates state and masks, finds SCMI and OPP sharing CPUs, adds firmware OPPs when not already present, builds a cpufreq table, sets any-CPU DVFS, latency, fast-switch support, transition delay, and a max-frequency QoS request, then subscribes to performance-limit notifications. Target and fast-switch send `perf_ops->freq_set()`, synchronous flag false or true respectively.

## State And Persistence

Per-policy state owns dynamic OPPs, cpufreq table, QoS limit request, notifier registration, and sharing mask. Firmware owns actual performance-domain state. Limit notifications update the policy max constraint through `freq_qos_update_request()`.

## Dependencies And Integration Points

Depends on SCMI Performance Protocol ops, OF CPU domain references, OPP framework, PM QoS, energy model, cpufreq cooling/boost, and optional common clock provider compatibility.

## Risks And Test Signals

`freq_set` for normal target is asynchronous, so observed frequency may lag requests. Incorrect domain-sharing discovery can duplicate OPPs or split policies. Test signals include SCMI protocol probe, generated OPP count, transition latency/rate limit, fast-switch availability, limit notification QoS updates, EM registration with power scale, and firmware `freq_get()` matching requested OPPs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scmi-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c

## Purpose

Implements cpufreq over the older ARM SCPI firmware interface, using SCPI-created OPPs and a firmware-backed CPU clock.

## APIs, Types, And Functions

`struct scpi_data` stores the CPU clock and CPU device. `scpi_cpufreq_init()` adds OPPs, determines sharing CPUs, builds a cpufreq table, gets the CPU clock, and configures policy state. `scpi_cpufreq_set_target()` calls `clk_set_rate()` and verifies the resulting rate. Probe gets `scpi_ops` and registers cpufreq.

## Control Flow

Platform probe obtains global SCPI ops, then registers the cpufreq driver. Policy init asks firmware to add OPPs for the CPU device, builds a shared policy mask from SCPI domain ids, marks OPPs shared, defers if OPPs are unavailable, allocates state, creates the frequency table, gets the CPU clock, sets any-CPU DVFS, latency, and disables fast switching. Exit releases clock, table, dynamic OPPs, and state.

## State And Persistence

Global `scpi_ops` is valid while the platform driver is registered. Per-policy `scpi_data` owns the clock reference and CPU device pointer. Firmware owns actual rate control state.

## Dependencies And Integration Points

Depends on `get_scpi_ops()`, SCPI domain ids, OPP framework, common clock, cpufreq energy-model registration with OPP, and platform-device binding `scpi-cpufreq`.

## Risks And Test Signals

Failure cleanup in init removes all dynamic OPPs, so partial policy setup must be tested. Target returns `-EIO` if the clock rate does not match the requested table frequency. Test signals include SCPI OPP creation, shared CPU mask, transition latency, clock get/set/readback, and successful cpufreq unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/scpi-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c

## Purpose

Provides generic SuperH cpufreq support using per-CPU clock framework objects, either with a clock-provided frequency table or rate rounding.

## APIs, Types, And Functions

Per-CPU `sh_cpuclk` stores CPU clock handles. `struct cpufreq_target` packages a policy and requested frequency for `work_on_cpu()`. `sh_cpufreq_get()`, `sh_cpufreq_target()`, `sh_cpufreq_verify()`, `sh_cpufreq_cpu_init()`, and `sh_cpufreq_cpu_exit()` implement the driver.

## Control Flow

Module init registers the driver. CPU init gets `"cpu_clk"` from the CPU device, installs its frequency table if present or derives min/max from `clk_round_rate()`. Targeting runs on the policy CPU, rounds the requested kHz to a supported Hz rate, verifies limits, emits cpufreq transition begin/end notifications, and calls `clk_set_rate()`.

## State And Persistence

The per-CPU clock reference is the main state. Hardware clock state persists in the SuperH clock framework. Exit releases the per-CPU clock.

## Dependencies And Integration Points

Depends on SuperH clock framework internals (`struct clk` frequency tables), CPU devices, `work_on_cpu()`, and cpufreq transition notification APIs.

## Risks And Test Signals

The target callback uses old-style `.target` rather than `.target_index` and disables automatic dynamic switching. `clk_set_rate()` return value is not propagated through transition end. Test signals include fallback min/max rounding, transition notifications, CPU-affine execution, and clock rate readback through `get`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sh-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c

## Purpose

Implements UltraSPARC-IIe cpufreq using Hummingbird ESTAR divider modes and memory refresh/self-refresh sequencing.

## APIs, Types, And Functions

`struct us2e_freq_percpu_info` stores per-CPU tables. `read_hbreg()` and `write_hbreg()` access physical bypass ASI registers. `frob_mem_refresh()` and `self_refresh_ctl()` manage memory refresh state. `us2e_transition()` encodes the hardware state machine for dividers 1, 2, 4, 6, and 8. cpufreq callbacks include `us2e_freq_get()`, `us2e_freq_target()`, init, and exit.

## Control Flow

Module init verifies spitfire TLB type plus manufacturer/implementation ids, allocates per-CPU tables, and registers cpufreq. CPU init builds rates from `sparc64_get_clock_tick()` divided by supported divisors. Targeting executes on the target CPU, reads current ESTAR, converts target index to divider bits, and calls `us2e_transition()` if the divisor changes. Exit forces divisor 1.

## State And Persistence

Software state is the allocated per-CPU frequency table array. Hardware state persists in ESTAR mode and Hummingbird memory control registers. Memory refresh counters are recomputed around divider changes.

## Dependencies And Integration Points

Depends on SPARC ASI physical bypass access, clock tick helpers, CPU implementation ids, and SMP single-CPU calls.

## Risks And Test Signals

There appears to be a table-construction bug in `us2e_freq_cpu_init()`: entries after index 2 repeatedly overwrite `table[2]`, then set `table[3]` as the end marker, making divisor 6/8 entries inaccessible. Test signals should include available frequency table inspection, ESTAR readback, memory refresh register values, self-refresh behavior for 1<->2 transitions, and forced full-speed exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us2e-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c

## Purpose

Implements UltraSPARC-III-family cpufreq by changing Safari config divider bits for divisors 1, 2, and 32.

## APIs, Types, And Functions

`struct us3_freq_percpu_info` holds a four-entry per-CPU table. `read_safari_cfg()` and `update_safari_cfg()` access `ASI_SAFARI_CONFIG`. `get_current_freq()` decodes divider bits. cpufreq callbacks are `us3_freq_get()`, `us3_freq_target()`, `us3_freq_cpu_init()`, and `us3_freq_cpu_exit()`.

## Control Flow

Module init verifies Cheetah/Cheetah+ TLB type and implementation ids, allocates per-CPU tables, and registers. CPU init fills rates from `sparc64_get_clock_tick()`. Targeting maps index to Safari divider bits and sends the update to the target CPU. Exit restores divisor 1.

## State And Persistence

State is limited to allocated per-CPU frequency tables. Hardware state persists in the Safari config divider field.

## Dependencies And Integration Points

Depends on SPARC CPU identification constants, ASI access, SMP single-CPU calls, and cpufreq generic table verification.

## Risks And Test Signals

The driver does no transition notification wrapping and assumes immediate divider changes. Test signals include table rates, Safari config readback, correct rejection on unsupported implementations, and full-speed restore on exit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/sparc-us3-cpufreq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c -->
# sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c

## Purpose

Provides cpufreq for ST SPEAr platforms using a DT-provided frequency table and CPU clock programming, with special parent-source selection for SPEAr1340.

## APIs, Types, And Functions

The global `spear_cpufreq` struct stores the CPU clock, transition latency, allocated table, and count. `spear1340_cpu_get_possible_parent()` selects a system clock source based on requested frequency. `spear1340_set_cpu_rate()` sets source rate and changes the parent of the CPU's system clock. `spear_cpufreq_target()` applies target rates.

## Control Flow

Platform probe gets CPU0's DT node, reads `clock-latency` and `cpufreq_tbl`, allocates a frequency table, gets `"cpu_clk"`, and registers cpufreq. Policy init installs the global table and transition latency. Targeting converts the table entry to Hz; on SPEAr1340 it chooses a possible parent, doubles the source rate, rounds it, sets the source rate, and switches parent. Other SPEAr variants directly set the CPU clock rate.

## State And Persistence

Global state retains the allocated frequency table and CPU clock. Hardware state persists in CPU clock rate and, for SPEAr1340, the parent of the CPU's system clock.

## Dependencies And Integration Points

Depends on OF CPU node properties `clock-latency` and `cpufreq_tbl`, common clock parent/rate APIs, machine compatible `st,spear1340`, and cpufreq generic initialization.

## Risks And Test Signals

There is no remove path freeing the table or clock. SPEAr1340 only supports hard-coded source ranges; unsupported rates return `-EINVAL`. Test signals include parsed DT table order, rounded source rates, parent selection at range boundaries, `clk_set_parent()` success, and `cpufreq_generic_get()` matching expected rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/cpufreq/spear-cpufreq.c -->
