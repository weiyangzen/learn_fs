# subset-b-004230 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc.h -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc.h

Purpose: This header is the private Tegra210 EMC register and data contract for the Tegra210 external memory controller implementation. It defines the memory-controller register offsets, bit fields, timing-table layouts, refresh modes, runtime state object, inline MMIO helpers, and function prototypes used by the Tegra210 EMC clock-change/training code in sibling implementation files.

Important APIs/types/functions: `struct tegra210_emc_timing` is the central per-frequency timing table, carrying burst, trim, per-channel, VREF, MC, latency, training, and DRAM mode register values. `struct tegra210_emc` owns runtime state: MC pointer, clock, timing table selection, MMIO bases, channel count, DRAM topology, training and refresh timers, clock-change timing, debugfs limits, and the Tegra clock EMC provider. `struct tegra210_emc_sequence` abstracts silicon-revision sequencing with `set_clock` and `periodic_compensation`. Inline helpers `emc_writel`, `emc_readl`, channel variants, `ccfifo_writel`, and `div_o3` standardize register access and rounded division. Exported prototypes cover refresh changes, mode-register reads, clock changes, shadow bypass, timing update, DLL handling, power ramping, compensation, timing lookup/adjustment, and periodic compensation.

Control flow: Consumers load a `tegra210_emc_timing`, adjust or compensate it, program shadow/burst/trim registers through offsets from `struct tegra210_emc_table_register_offsets`, use sequence callbacks for revision-specific clock switching, and wait for hardware update status bits. Refresh and training timers can trigger later reprogramming.

State and persistence: No persistent storage is used. State is in live kernel structures and EMC hardware registers. The most sensitive state is `last`/`next` timing, refresh mode, training values, timers, clock-change delay, and debugfs min/max rate.

Dependencies and integration: Depends on Linux MMIO primitives, bit macros, timers, debugfs, Tegra MC structures, and `tegra210_clk_emc_provider`. It integrates with Tegra EMC sequence files such as `tegra210-emc-r21021.c` and shared Tegra memory-controller code.

Risks and test signals: Register-array sizes and enum indices must match firmware/device-tree timing blobs exactly; off-by-one errors can corrupt DRAM timing. Test signals include successful boot across supported DRAM types, clock-rate transitions under load, refresh derating, periodic training, suspend/resume, and absence of timeout logs from update or MRR paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-emc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-mc.h -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-mc.h

Purpose: This small private header names Tegra210 memory-controller register offsets used by Tegra210 MC/EMC code, especially latency allowance, PTSA, EMEM arbitration, refresh-per-bank, and dynamic hysteresis registers.

Important APIs/types/functions: The file exports no functions or types. Its API is the set of `#define` constants such as `MC_LATENCY_ALLOWANCE_*`, `MC_MLL_MPCORER_PTSA_RATE`, `MC_FTOP_PTSA_RATE`, `MC_EMEM_ARB_TIMING_RFCPB`, `MC_EMEM_ARB_REFPB_*`, `MC_PTSA_GRANT_DECREMENT`, and `MC_EMEM_ARB_DHYST_*`.

Control flow: There is no executable control flow. The constants are consumed by Tegra210 memory-controller programming paths when calculating latency allowance or applying MC arbitration/timing values during EMC frequency changes and MC initialization.

State and persistence: No state is stored in the header. The defined offsets address hardware state in MC registers, which persists only as programmed hardware configuration until reset or reprogramming.

Dependencies and integration: It includes `mc.h` for shared Tegra MC context and is aligned with Tegra210 register layout. It sits between raw hardware documentation and C code that writes MMIO through shared Tegra MC helpers.

Risks and test signals: The main risk is an incorrect offset silently programming the wrong register, which can cause display underruns, memory arbitration stalls, or failed frequency transitions. Test signals are successful Tegra210 boot, stable display/video/USB/storage clients under bandwidth pressure, and matching register dumps against the Tegra210 TRM or downstream reference values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210-mc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210.c

Purpose: This file describes the Tegra210 memory-controller SoC integration for the shared Tegra MC driver. It enumerates MC clients, SMMU software groups, display grouping, reset lines, interrupt masks, and the exported `tegra210_mc_soc` descriptor.

Important APIs/types/functions: The primary exported object is `const struct tegra_mc_soc tegra210_mc_soc`. Supporting tables include `tegra210_mc_clients`, `tegra210_swgroups`, `tegra210_groups`, `tegra210_smmu_soc`, `tegra210_mc_resets`, and `tegra210_mc_intmasks`. Each `struct tegra_mc_client` maps a DT binding client ID to a name, SWGROUP, SMMU enable bit, latency-allowance register field, and default LA value. Reset entries use `TEGRA210_MC_RESET`.

Control flow: This file has no probe function. At runtime the common Tegra MC core selects `tegra210_mc_soc`, registers clients/SMMU groups, initializes reset controls, programs interrupt masks, and routes faults through common `tegra30_mc_irq_handlers`. Client and reset tables are indexed by common code rather than traversed locally.

State and persistence: Static const tables define hardware topology and default configuration. Live state resides in the common MC driver and hardware registers. The table data is persistent for the lifetime of the kernel image.

Dependencies and integration: Depends on `dt-bindings/memory/tegra210-mc.h` and shared `mc.h`. It integrates with the Tegra SMMU, reset controller, interconnect/latency allowance logic, and shared Tegra20/Tegra30 register/IRQ helper sets.

Risks and test signals: Risks are table mismatches: wrong client IDs, LA fields, SWGROUP registers, reset bits, or interrupt masks can break DMA isolation, reset sequencing, or fault attribution. Test signals include IOMMU attach for all Tegra210 clients, working display/GPU/storage/video clients, correct MC fault logs, and reset-controller exercise for each listed hardware block.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra234.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra234.c

Purpose: This file provides the Tegra234 memory-controller SoC descriptor and bandwidth-management interconnect callbacks. It maps memory clients to BPMP bandwidth-manager IDs, Stream IDs, security/override registers, client traffic classes, interrupt masks, and the exported `tegra234_mc_soc`.

Important APIs/types/functions: `tegra234_mc_clients` is the central client table. `tegra234_mc_icc_set()` packages ICC bandwidth requests into `MRQ_BWMGR_INT` BPMP messages using `CMD_BWMGR_INT_CALC_AND_SET`, selecting ISO or NISO bandwidth by client type and passing peak bandwidth as the MC floor. `tegra234_mc_icc_aggregate()` sums average bandwidth and keeps maximum peak bandwidth, multiplying CPU-cluster peak requests by channel count. `tegra234_mc_icc_get_init_bw()` initializes ICC nodes to zero. `tegra234_mc_icc_ops`, `tegra234_mc_intmasks`, and `tegra234_mc_soc` connect these callbacks to shared MC code.

Control flow: Common Tegra MC registration consumes `tegra234_mc_soc`. ICC `set_bw` calls reach `tegra234_mc_icc_set()`, which skips self-links, no-ops if BPMP BWMGR is unsupported, validates BPMP availability, sends an MRQ, and converts BPMP failures into kernel errors. Interrupt handling uses common Tegra30 handlers with Tegra234 masks and register layout.

State and persistence: The file keeps only immutable tables. Dynamic state is in `struct tegra_mc`, BPMP firmware, ICC nodes, and hardware registers. Bandwidth decisions persist in BPMP/MC state until updated.

Dependencies and integration: Depends on Tegra234 DT bindings, Linux ICC, `linux/tegra-icc.h`, BPMP MRQ definitions, `soc/tegra/mc.h`, and shared `mc.h`. Integration points include BPMP firmware, memory-client SID programming, carveout handling, MC fault IRQs, and the interconnect framework.

Risks and test signals: Risks include stale BPMP IDs, incorrect client type classification, CPU cluster channel scaling mistakes, and unavailable BPMP references. Test signals include successful ICC path setup, BPMP bandwidth MRQs without `rx.ret` failures, working DMA isolation for SIDs, and correct reporting of MC decode/security/carveout faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra234.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264-bwmgr.h -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264-bwmgr.h

Purpose: This header assigns Tegra264 BPMP bandwidth-manager client IDs used by the Tegra264 MC interconnect implementation. The IDs bridge Linux memory-client descriptors to BPMP firmware's BWMGR interface.

Important APIs/types/functions: The file exports only preprocessor constants. IDs cover primary/debug clients, CPU clusters, display, VI, APE, VIFAL, GPU, EQOS, PCIe ports, SDMMC, NVDEC/NVENC/NVJPG, OFAA, XUSB, TSEC, VIC, APEDMA, SE, ISP, HDA, RCE, PVA, and NVPMODEL.

Control flow: There is no executable logic. `tegra264.c` stores these constants in each `struct tegra_mc_client.bpmp_id`; ICC bandwidth requests later pass them to BPMP in `MRQ_BWMGR_INT` messages.

State and persistence: No runtime state is stored. The numeric contract must remain stable with BPMP firmware and device-tree binding expectations.

Dependencies and integration: The header is included by `tegra264.c` and indirectly integrates with Linux ICC, Tegra BPMP firmware, and the Tegra MC client table. It is independent of generic kernel headers.

Risks and test signals: A wrong ID sends a bandwidth vote to the wrong firmware client, causing over-throttling or under-provisioning of an unrelated engine. Test signals include BPMP accepting all ICC requests, expected EMC frequency response under GPU/display/storage/network load, and no bandwidth-related underruns or timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264-bwmgr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264.c

Purpose: This file defines Tegra264 memory-controller topology, interconnect bandwidth handoff to BPMP, and custom fault interrupt decoding for MCF, hub, SBS, and channel interrupt sources. It exports `tegra264_mc_soc` for the shared Tegra MC driver.

Important APIs/types/functions: `tegra264_mc_clients` maps Tegra264 memory clients to BWMGR IDs and ICC traffic classes. `tegra264_mc_icc_set()` sends BPMP `MRQ_BWMGR_INT` calculate-and-set requests. `tegra264_mc_icc_aggregate()` sums average and maxes peak bandwidth. Fault handlers include `mcf_log_fault()`, `handle_mcf_irq()`, `hub_log_fault()`, `handle_hub_irq()`, hub-specific wrappers, `handle_generic_irq()`, `handle_sbs_irq()`, and `handle_channel_irq()`. `tegra264_mc_regs`, `tegra264_mc_intmasks`, and `tegra264_mc_irq_handlers` describe register layout, masks, priorities, and IRQ dispatch.

Control flow: ICC set calls follow the Tegra234-style BPMP path but use Tegra264 BWMGR IDs. MCF IRQ handling reads the broadcast common status, iterates active slices, decodes per-slice fault status/address/client/type, logs ratelimited errors, and clears slice interrupts. Hub IRQ handling reads a hubc global status, handles scrubber status, iterates hub interrupts, logs per-hub client/status/address, and clears hub/global status. SBS and channel handlers scan all MC channels for status and clear them.

State and persistence: The file is stateless beyond const tables. Runtime state lives in `struct tegra_mc`, hardware status registers, and BPMP firmware bandwidth state. IRQ handlers clear hardware-latched faults after logging.

Dependencies and integration: Depends on Tegra264 memory DT bindings, Tegra ICC, BPMP, `soc/tegra/mc.h`, shared `mc.h`, and `tegra264-bwmgr.h`. It integrates with shared Tegra186 MC ops and multi-interrupt MC registration.

Risks and test signals: Risks include wrong aperture mapping, status/address decoding, client ID masks, or failure to clear interrupts. Test signals include correct BPMP bandwidth votes, actionable MC fault logs with client/address/type, no IRQ storms after injected faults, and validation of hub/MC channel interrupt routing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra264.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30-emc.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30-emc.c

Purpose: This is the Tegra30 External Memory Controller platform driver. It loads EMC timing tables from device tree, coordinates safe DRAM timing changes during EMC clock transitions, exposes debugfs rate controls, provides an ICC provider for memory bandwidth requests, handles refresh-overflow interrupts, and participates in suspend/resume.

Important APIs/types/functions: `struct emc_timing` stores one frequency's EMC register data and mode/calibration fields. `struct tegra_emc` owns registers, IRQ, clock notifier, MC handle, timing state, debugfs limits, ICC provider, rate requests, and bad-state tracking. Key functions are `emc_prepare_timing_change()`, `emc_complete_timing_change()`, `emc_clk_change_notify()`, `emc_load_timings_from_dt()`, `emc_setup_hw()`, `emc_round_rate()`, `emc_request_rate()`, debugfs get/set handlers, `emc_icc_set()`, `tegra30_emc_interconnect_init()`, `tegra30_emc_init_clk()`, probe, suspend, and resume.

Control flow: Probe maps registers, gets the shared MC, configures hardware handshake/interrupt/debug state, optionally loads RAM-code-specific timings from DT, registers IRQ and clock notifier, initializes OPP/rate requests/debugfs, and registers ICC nodes. PRE_RATE_CHANGE disables the IRQ and programs shadow/timing/MC values, POST waits for clock-change completion and restores refresh/calibration/self-refresh settings, and ABORT marks unrecoverable state. ICC and debugfs requests converge on `dev_pm_opp_set_rate()`.

State and persistence: State is runtime only: timing arrays, current mode registers, debugfs min/max, requested min/max by source, `bad_state`, MRR errors, and hardware registers. DT timing data is read but not modified. Suspend takes exclusive clock-rate control and refuses a bad state; resume reinitializes hardware.

Dependencies and integration: Depends on Tegra clock callbacks, OPP, ICC, debugfs, shared Tegra MC, `of_memory`, JEDEC LPDDR helpers, and Tegra fuses for RAM code. It is a platform driver for `nvidia,tegra30-emc`.

Risks and test signals: Risks are high because incorrect ordering can hang memory. Test signals include boot with and without DT timings, repeated OPP rate changes under memory load, valid LPDDR MRR reads, refresh-overflow interrupt logging, debugfs min/max behavior, ICC bandwidth scaling, and suspend/resume without `bad_state` warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30-emc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30.c -->
# sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30.c

Purpose: This file defines Tegra30 memory-controller SoC data for the shared Tegra MC driver and implements Tegra30-specific interconnect latency tuning. It covers MC client tables, SMMU groups, reset lines, EMEM timing-register lists, interrupt masks, ICC callbacks, and the exported `tegra30_mc_soc`.

Important APIs/types/functions: Data tables include `tegra30_mc_emem_regs`, `tegra30_mc_clients`, `tegra30_swgroups`, `tegra30_groups`, `tegra30_smmu_soc`, `tegra30_mc_resets`, and `tegra30_mc_intmasks`. `tegra30_mc_tune_client_latency()` converts a client's peak bandwidth and FIFO size into latency-allowance ticks with special compensation for display and VI. `tegra30_mc_icc_set()` applies that tuning from ICC peak bandwidth. `tegra30_mc_icc_aggreate()` boosts ISO peak bandwidth before aggregation. `tegra30_mc_of_icc_xlate_extended()` tags default ISO clients.

Control flow: The common MC core consumes `tegra30_mc_soc`. ICC translation maps DT client IDs to ICC nodes and assigns ISO/default tags. ICC aggregation scales ISO requests, then `set` programs latency allowance registers. Reset, SMMU, interrupt, and EMEM timing tables are used by shared Tegra MC operations.

State and persistence: All local data is immutable except hardware LA registers programmed by `tegra30_mc_tune_client_latency()`. There is no file-backed persistence. Hardware configuration remains until later ICC updates or reset.

Dependencies and integration: Depends on Tegra30 memory DT bindings, shared `mc.h`, Linux device/OF helpers, and common Tegra MC/SMMU/reset/ICC code. It pairs with `tegra30-emc.c`, which drives EMC rates and timing changes.

Risks and test signals: Risks include incorrect FIFO sizes, LA register fields, ISO tagging, and the misspelled but internally wired `tegra30_mc_icc_aggreate` callback being overlooked during refactors. Test signals include display/VI underrun testing, ICC path creation from DT, client fault attribution, SMMU mapping tests, and reset-control validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/tegra/tegra30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-aemif.c -->
# sources/distributed-fs/ceph-client/drivers/memory/ti-aemif.c

Purpose: This platform driver configures Texas Instruments asynchronous EMIF chip-select timing and bus-width/extended-wait/select-strobe settings from device tree, then populates child devices behind the configured async bus.

Important APIs/types/functions: `struct aemif_cs_data` stores one chip select's timing and bus config. `struct aemif_device` stores MMIO base, enabled clock, clock rate in kHz, chip-select offset/count, chip-select data, and a configuration mutex. Exported APIs are `aemif_check_cs_timings()` and `aemif_set_cs_timings()`. Internal helpers include `aemif_calc_rate()`, `aemif_config_abus()`, `aemif_get_hw_params()`, `of_aemif_parse_abus_config()`, and `aemif_probe()`.

Control flow: Probe allocates state, enables the clock, derives kHz rate, applies DA850 chip-select offset when needed, maps registers, parses each child node's `ti,cs-*` properties while preserving unspecified hardware defaults, validates timing fields, programs config and timing registers for each CS, then calls `of_platform_populate()` on each child so dependent devices probe after timing is stable.

State and persistence: Runtime state mirrors chip-select settings and protects later exported timing updates with `config_cs_lock`. Hardware ACR registers hold programmed timings. No persistent file state exists.

Dependencies and integration: Depends on Linux clk, OF, platform-device population, MMIO, mutexes, and public `linux/memory/ti-aemif.h`. Compatible strings are `ti,davinci-aemif` and `ti,da850-aemif`. Child devices depend on this driver for safe bus timing before probe.

Risks and test signals: Risks include timing conversion overflow or off-by-one, invalid chip-select numbering, and assuming one user per CS during initial programming. Test signals include DT parse failures for invalid timings, register readback for each CS, successful probing of child NAND/NOR/FPGA devices, and exported timing changes under mutex without corrupting config bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-aemif.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-emif-pm.c -->
# sources/distributed-fs/ceph-client/drivers/memory/ti-emif-pm.c

Purpose: This driver loads TI AM33xx/AM43xx EMIF low-power routines into on-chip SRAM, prepares data/function tables used by suspend/resume code, configures an EMIF self-refresh erratum workaround, and exports helpers for other PM code to discover SRAM function addresses and current memory type.

Important APIs/types/functions: `struct ti_emif_data` owns SRAM code/data physical and virtual addresses, gen_pool handles, `struct ti_emif_pm_data`, and `struct ti_emif_pm_functions`. `ti_emif_alloc_sram()` allocates code/data SRAM and computes virtual suspend and physical resume addresses. `ti_emif_push_sram()` copies assembly code and PM data into SRAM with `sram_exec_copy()`. Exported functions are `ti_emif_copy_pm_function_table()` and `ti_emif_get_mem_type()`. Probe/remove and PM callbacks manage lifecycle.

Control flow: Probe maps EMIF registers, records physical base, writes the 8192-cycle self-refresh delay, allocates SRAM, copies code/data, and publishes the singleton `emif_instance`. Resume checks whether SRAM still contains the code and recopies if context was lost. Remove clears the singleton and frees pools.

State and persistence: `emif_instance` is global singleton state, so only one active EMIF instance is supported. SRAM contains executable PM code and data across low-power transitions unless SRAM context is lost. Hardware EMIF registers hold erratum delay settings.

Dependencies and integration: Depends on `linux/sram.h`, genalloc pools, `linux/ti-emif-sram.h`, platform resources, OF match data, and `emif.h`. It integrates with the ARM assembly in `ti-emif-sram-pm.S` and external PM code that copies the function table.

Risks and test signals: Risks include missing SRAM pools, wrong virtual/physical address choice for suspend versus resume, singleton misuse, and SRAM contents becoming stale after resume. Test signals include successful SRAM allocation/copy, exported function-table copy, correct DDR type from `ti_emif_get_mem_type()`, suspend/resume on AM335x/AM437x, and no EMIF self-refresh erratum symptoms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-emif-pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-emif-sram-pm.S -->
# sources/distributed-fs/ceph-client/drivers/memory/ti-emif-sram-pm.S

Purpose: This ARMv7 assembly file is the SRAM-resident low-level PM routine set for TI EMIF. It saves/restores EMIF context, enters/exits/aborts SDRAM self-refresh, reruns DDR3 hardware leveling, and reserves the SRAM data block used by the C driver.

Important APIs/types/functions: Entry points are `ti_emif_sram`, `ti_emif_save_context`, `ti_emif_restore_context`, `ti_emif_run_hw_leveling`, `ti_emif_enter_sr`, `ti_emif_exit_sr`, `ti_emif_abort_sr`, `ti_emif_pm_sram_data`, and `ti_emif_sram_sz`. Offsets come from `ti-emif-asm-offsets.h`; register constants come from `emif.h`.

Control flow: Save-context uses virtual EMIF/data addresses, stores common EMIF registers, and conditionally saves AM43xx extra registers plus a block of PHY control registers. Restore-context uses physical addresses, writes timing/refresh/PM/COS/OCP/PHY registers, restores ZQ config, and writes SDRAM config last for DDR2. Hardware leveling starts DDR3 read/write leveling and busy-waits for completion. Enter/exit/abort self-refresh manipulate PM control bits and wait for EMIF ready where needed.

State and persistence: Saved EMIF context is stored in SRAM data (`ti_emif_pm_sram_data`) and survives while SRAM does. The routines directly mutate EMIF hardware registers during low-power transitions when DDR may be unavailable.

Dependencies and integration: The file depends on ARM linkage/assembler conventions, generated asm offsets, and C-side copying/address setup from `ti-emif-pm.c`. It is called by platform PM code through the exported function table.

Risks and test signals: Risks include incorrect generated offsets, using virtual addresses after MMU-off, unbounded wait loops if EMIF never becomes ready, and missing AM43xx PHY registers. Test signals include assembly build with offset generation, SRAM copy size correctness, suspend/resume from DDR2 and DDR3, hardware-leveling completion, and abort path returning DDR to ready state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memory/ti-emif-sram-pm.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memstick/Kconfig

Purpose: This Kconfig file defines the top-level MemoryStick subsystem configuration menu and includes the core and host-driver Kconfig files when MemoryStick support is enabled.

Important APIs/types/functions: `menuconfig MEMSTICK` is a tristate option for Sony MemoryStick card support. `config MEMSTICK_DEBUG` enables debug logging by later Makefile flags. `source "drivers/memstick/core/Kconfig"` and `source "drivers/memstick/host/Kconfig"` include subordinate options.

Control flow: Kconfig dependency flow is simple: if `MEMSTICK` is disabled, neither core nor host options are visible. If enabled, developers can also enable debug and select specific core/host drivers.

State and persistence: Configuration state is stored in the kernel `.config`, not in this file at runtime. The options control which objects are built and whether `DEBUG` is defined.

Dependencies and integration: Integrates with the kernel Kconfig system and the corresponding `drivers/memstick/Makefile`. It is the entry point for MemoryStick block drivers and host controller options.

Risks and test signals: Risks are mostly build-configuration regressions, such as exposing drivers without the core or failing to propagate debug. Test signals include `olddefconfig`/menuconfig visibility, builds with `MEMSTICK=y`, `MEMSTICK=m`, and disabled, plus debug builds showing `-DDEBUG` in affected subdirs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memstick/Makefile

Purpose: This Makefile controls top-level MemoryStick subsystem compilation. It applies debug compiler flags and descends into core and host directories when `CONFIG_MEMSTICK` is enabled.

Important APIs/types/functions: `subdir-ccflags-$(CONFIG_MEMSTICK_DEBUG) := -DDEBUG` enables debug builds for subdirectories. `obj-$(CONFIG_MEMSTICK) += core/` and `obj-$(CONFIG_MEMSTICK) += host/` include the subsystem implementation and host drivers.

Control flow: Kbuild evaluates config symbols and includes both subdirectories for built-in or modular MemoryStick builds. If `MEMSTICK_DEBUG` is set, all compiled files below receive `-DDEBUG`.

State and persistence: There is no runtime state. Build output depends on `.config` and Kbuild's object traversal.

Dependencies and integration: Depends on top-level kernel Kbuild and Kconfig symbols from `drivers/memstick/Kconfig`. It integrates with `drivers/memstick/core/Makefile` and host Makefiles.

Risks and test signals: Risks include failing to build host drivers when the core is enabled, or debug flags not propagating. Test signals are `make drivers/memstick/` with `MEMSTICK=y/m`, disabled builds excluding the directory, and debug builds compiling with dynamic debug/dev_dbg support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/Kconfig

Purpose: This Kconfig file defines core MemoryStick policy and block-driver options under the top-level MemoryStick subsystem.

Important APIs/types/functions: `MEMSTICK_UNSAFE_RESUME` allows skipping normal removal/redetection across suspend, explicitly warning about data corruption risk. `MSPRO_BLOCK` enables the MemoryStick Pro block driver and depends on `BLOCK`. `MS_BLOCK` enables the older MemoryStick Standard block driver, also depending on `BLOCK`. Both block drivers imply `IOSCHED_BFQ`.

Control flow: These options are visible only when the parent `MEMSTICK` menu sources this file. Selected options drive object inclusion in `drivers/memstick/core/Makefile`.

State and persistence: Options persist in kernel configuration. Runtime behavior is affected by compiled-in code paths, especially unsafe resume policy in core/card handling.

Dependencies and integration: Integrates with block layer availability, BFQ scheduler hints, MemoryStick core bus code, and the two block driver source files compiled by the core Makefile.

Risks and test signals: The notable risk is `MEMSTICK_UNSAFE_RESUME`, which can corrupt data if cards are removed during suspend. Driver options also carry media compatibility risk: Standard and Pro cards require different drivers. Test signals include Kconfig dependency checks with `BLOCK=n`, building each driver as module/built-in, and suspend/resume tests with unsafe resume disabled and enabled only on fixed-media systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/Makefile -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/Makefile

Purpose: This Makefile maps MemoryStick core Kconfig symbols to compiled objects in the core directory.

Important APIs/types/functions: `obj-$(CONFIG_MEMSTICK) += memstick.o` builds the bus/core implementation. `obj-$(CONFIG_MS_BLOCK) += ms_block.o` builds the standard MemoryStick block driver. `obj-$(CONFIG_MSPRO_BLOCK) += mspro_block.o` builds the MemoryStick Pro block driver.

Control flow: Kbuild includes objects according to tristate values. If an option is modular, the corresponding object becomes part of a module; if built-in, it is linked into the kernel image.

State and persistence: There is no runtime state. Build products are determined by `.config`.

Dependencies and integration: Depends on symbols declared in `drivers/memstick/core/Kconfig` and on the top-level MemoryStick Makefile descending into `core/`.

Risks and test signals: Risks are build graph mistakes that omit core bus support or block drivers despite selected options. Test signals include all combinations of `MEMSTICK`, `MS_BLOCK`, and `MSPRO_BLOCK` as built-in/module where legal, plus module dependency checks ensuring block drivers can resolve exported core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/memstick.c -->
# sources/distributed-fs/ceph-client/drivers/memstick/core/memstick.c

Purpose: This is the Sony MemoryStick core bus driver. It registers the `memstick` bus and host class, manages host IDs, card detection/removal, request dispatch/retry helpers, card identification, PM callbacks, and driver registration APIs used by MemoryStick block/media drivers and host controller drivers.

Important APIs/types/functions: Exported APIs include `memstick_detect_change()`, `memstick_next_req()`, `memstick_new_req()`, `memstick_init_req_sg()`, `memstick_init_req()`, `memstick_set_rw_addr()`, `memstick_alloc_host()`, `memstick_add_host()`, `memstick_remove_host()`, `memstick_free_host()`, `memstick_suspend_host()`, `memstick_resume_host()`, `memstick_register_driver()`, and `memstick_unregister_driver()`. Core objects include the global freezable `workqueue`, `memstick_host_idr`, `memstick_host_lock`, `memstick_bus_type`, and `memstick_host_class`.

Control flow: Module init creates the workqueue, registers the bus, and registers the host class. Host drivers allocate/add hosts, which get an ID, device name, class device, power off, and scheduled detection. `memstick_check()` runs on the workqueue under host lock: power on, stop existing card, allocate/probe a temporary card, set RW register address, read ID, compare with existing card, register new card or unregister removed/changed card, then power off if no card remains. Request processing is callback-driven through `card->next_request`; host drivers call `memstick_next_req()` after each transfer and retries are applied on errors.

State and persistence: Runtime state is in host/card structures, IDR allocation, request retry counters, completions, and the workqueue. Sysfs exposes card `type`, `category`, and `class`; uevents publish the same IDs. No persistent storage is used.

Dependencies and integration: Depends on `linux/memstick.h`, driver core bus/class APIs, IDR, workqueues, completions, runtime PM, and host driver callbacks (`request`, `set_param`). Block drivers bind through `struct memstick_driver` ID tables.

Risks and test signals: Risks include races between removal and detection, request completion timeouts, reference-count imbalance around probe/remove, and data corruption if suspend policy assumes media did not change. Test signals include card insertion/removal churn, request retry behavior, sysfs/uevent ID correctness, runtime PM balance, host remove during pending work, and suspend/resume redetection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/memstick/core/memstick.c -->
