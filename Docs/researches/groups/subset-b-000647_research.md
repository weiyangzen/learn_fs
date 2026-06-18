# subset-b-000647 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mmdc.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mmdc.c

Purpose: i.MX MMDC memory-controller support with optional perf PMU exposure. It records DDR type, enables automatic MMDC power saving, and registers fixed-function memory-controller counters for i.MX6Q/i.MX6QP.

Important APIs/types/functions: `imx_mmdc_get_ddr_type()`, `imx_mmdc_probe()`, `imx_mmdc_perf_init()`, `mmdc_pmu_event_init/add/del/start/stop/read()`, `mmdc_pmu_timer_handler()`, `mmdc_pmu_offline_cpu()`, `struct mmdc_pmu`, `struct fsl_mmdc_devtype_data`, PMU event/format/cpumask sysfs attributes, and the `imx-mmdc` platform driver.

Control flow: Probe enables the optional IPG clock, maps the MMDC register block from DT, reads `MMDC_MDMISC` into global `ddr_type`, clears the `MMDC_MAPSR` power-saving disable bit, then initializes the perf PMU if `CONFIG_PERF_EVENTS` is enabled. Perf events are fixed to six hardware counters, reject sampling/per-task use, pin to one CPU, program optional AXI ID filtering, poll every second with an hrtimer because no counter interrupt exists, and migrate context on CPU hotplug.

State and persistence: Persistent hardware state is MMDC register configuration: power-saving enable, profile control, AXI ID selector, and live 32-bit counter values. Kernel process state includes global `ddr_type`, the `mmdc_ida` id allocator, cpuhp state, per-PMU active event slots, hrtimer, selected CPU mask, mapped MMDC base, and enabled clock. Remove unregisters PMU/cpuhp state, unmaps MMDC, disables the clock, and frees memory.

Dependencies and integration points: Depends on platform device/OF matching (`fsl,imx6q-mmdc`, `fsl,imx6qp-mmdc`), Linux perf PMU core, hrtimers, CPU hotplug, clocks, MMIO helpers, and i.MX PM code that consumes `imx_mmdc_get_ddr_type()` for suspend DDR handling.

Risks: `of_iomap()` is only `WARN_ON` checked before dereference, so malformed DT can crash. The module parameter name is `pmu_pmu_poll_period_us`, which appears accidental but is ABI once exposed. Concurrent events share one profile-control register, so group validation and add ordering are critical. The PMU relies on polling before 32-bit overflow and assumes counter wrap within the selected period. Error unwinding leaves the global cpuhp state installed once created.

Test signals: Build with and without `CONFIG_PERF_EVENTS`, boot on i.MX6Q/QP DT, verify `/sys/bus/event_source/devices/mmdc*/events`, run `perf stat -e mmdc0/total-cycles/`, offline the bound CPU, and suspend/resume to check DDR type remains available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mmdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx27.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx27.h

Purpose: Small i.MX27-specific physical address map header for legacy board and low-level code that needs fixed AIPI, SAHB1, and external memory-controller windows.

Important APIs/types/functions: Defines `MX27_AIPI_BASE_ADDR/SIZE`, `MX27_SAHB1_BASE_ADDR/SIZE`, `MX27_X_MEMC_BASE_ADDR/SIZE`, and `MX27_IO_P2V(x)`.

Control flow: There is no runtime control flow; including code expands constants into map descriptors, direct MMIO accessors, or legacy platform setup.

State and persistence: No mutable state. The values encode SoC physical layout and rely on the shared i.MX static virtual mapping macro.

Dependencies and integration points: Used with `mx2x.h`, `hardware.h`, and the ARM i.MX mapping setup for i.MX27-specific machine support.

Risks: Wrong base/size values break early MMIO, watchdog, clock, or memory-controller access before normal drivers can recover. Direct inclusion assumes `SZ_*` and `IMX_IO_P2V` are available through the includer.

Test signals: Compile coverage for i.MX27 and boot smoke tests that touch CCM, watchdog reset, and suspend paths are the useful signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx27.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx2x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx2x.h

Purpose: Common i.MX21/i.MX27 register, interrupt, and DMA request map for legacy platform code.

Important APIs/types/functions: Defines AIPI peripheral base addresses, AVIC and SAHB regions, fixed legacy IRQ numbers based on `NR_IRQS_LEGACY`, and fixed DMA request ids for UART, SSI, CSPI, SDHC, CSI, and external requests.

Control flow: No executable control flow. The header provides compile-time constants used by board files, platform data, and low-level drivers.

State and persistence: No runtime state. It persists SoC ABI assumptions about interrupt numbering and DMA request routing in source form.

Dependencies and integration points: Depends on `<asm/irq.h>` for `NR_IRQS_LEGACY`; integrates with AVIC interrupt setup, old non-DT platform devices, and DMA/client driver platform data.

Risks: The values are hard-coded SoC contract. Mismatched interrupt or DMA ids produce silent device malfunction, often as missing interrupts or broken DMA. Constants are not discoverable from DT, so legacy board users rely on them exactly.

Test signals: Build old i.MX2 configurations and exercise UART, SDHC, SSI, CSPI, DMA, and AVIC interrupt delivery on i.MX21/i.MX27 boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx2x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx31.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx31.h

Purpose: i.MX31-specific physical memory-window definitions for legacy machine setup.

Important APIs/types/functions: Defines AIPS1, SPBA0, AIPS2, AVIC, X_MEMC base/size pairs and `MX31_IO_P2V(x)`.

Control flow: No runtime flow; consumers use the constants for static IO mapping and early register access.

State and persistence: No mutable state. The file encodes the i.MX31 bus map as compile-time definitions.

Dependencies and integration points: Integrates with `mx3x.h`, `hardware.h`, map descriptors, AVIC setup, and legacy i.MX31 board code.

Risks: Bad constants break early boot, interrupt controller mapping, or memory-controller access. The file assumes surrounding includes provide `SZ_*` and `IMX_IO_P2V`.

Test signals: Compile i.MX31 platform support and boot with early console, interrupt, and memory-controller access enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx35.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx35.h

Purpose: i.MX35-specific physical memory-window definitions parallel to i.MX31 for legacy machine setup.

Important APIs/types/functions: Defines AIPS1, SPBA0, AIPS2, AVIC, X_MEMC base/size pairs and `MX35_IO_P2V(x)`.

Control flow: No executable flow; it is a constants-only header consumed by early platform code.

State and persistence: No runtime state. Values describe fixed SoC register apertures.

Dependencies and integration points: Integrates with `mx3x.h`, `mach-imx35.c`, `hardware.h`, and static mapping/early MMIO users.

Risks: Incorrect windows can prevent clock, interrupt, or memory-controller setup. It has no validation at runtime.

Test signals: Build and boot i.MX35 DT/legacy configurations, checking AVIC, timer, watchdog reset, and early console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx3x.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx3x.h

Purpose: Common i.MX31/i.MX35 memory map, peripheral base, chip-select, interrupt, and product signature definitions.

Important APIs/types/functions: Defines MX3x AIPS/SPBA/AIPS2 peripheral bases, L2CC, ROMP/AVIC, SDRAM and chip-select windows, X_MEMC sub-blocks, legacy interrupt numbers, and `MX3x_PROD_SIGNATURE`.

Control flow: No runtime flow; it supplies constants to early platform, board, and driver glue.

State and persistence: No mutable state. The header preserves the static virtual/physical layout assumptions for MX3x-era code.

Dependencies and integration points: Depends on `<asm/irq.h>` and integrates with i.MX31/i.MX35 machine descriptors, AVIC irq code, WEIM/NAND/SDRAM setup, and non-DT platform data.

Risks: Interrupt numbering and register windows are fragile hardware ABI. A mistake usually appears as stuck boot, broken serial/timer, or devices firing wrong IRQs. The map mixes virtual-address documentation with physical constants, so consumers must use the right conversion path.

Test signals: Build i.MX31/i.MX35 configurations and smoke boot with timer, UART, GPIO, SDMA, IPU, and watchdog paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mx3x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mxc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/mxc.h

Purpose: Shared private i.MX architecture helper header for CPU type tests, low-level read/write aliases, DDR type constant, and cross-file hooks.

Important APIs/types/functions: Defines `IMX_DDR_TYPE_LPDDR2`, inline `cpu_is_imx6*()` and `cpu_is_imx7d()` helpers, `struct cpu_op`, `tzic_enable_wake()`, external `get_cpu_op`, and `imx_readl/readw/writel/writew` aliases.

Control flow: No standalone runtime flow. The inline CPU tests compare `__mxc_cpu_type`; one helper is gated by `CONFIG_SOC_IMX6SL` to fold to false when unsupported.

State and persistence: No owned persistence. It exposes global CPU identification state from `soc/imx/cpu.h` and declares global hooks used by PM/frequency code.

Dependencies and integration points: Must be included through the guarded i.MX hardware header. Used by PM, IRQ, reset, and platform code that needs relaxed MMIO helpers or CPU-family branching.

Risks: The direct-include guard prevents misuse, but any stale `__mxc_cpu_type` classification changes PM register programming. Relaxed accessors need explicit ordering where hardware requires it.

Test signals: Compile coverage across i.MX6 variants; runtime validation comes from suspend, cpuidle, SMP boot, and TZIC wake behavior on the relevant SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/mxc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/platsmp.c

Purpose: SMP bring-up glue for i.MX SCU-based SoCs, i.MX7D, and LS1021A.

Important APIs/types/functions: Defines `imx_scu_map_io()`, `imx_smp_prepare()`, `imx_smp_ops`, `imx7_smp_ops`, `ls1021a_smp_ops`, `imx_boot_secondary()`, `imx_smp_init_cpus()`, `imx7_smp_init_cpus()`, and the exported diagnostic-register variable `g_diag_reg` consumed by secondary startup code.

Control flow: For classic i.MX, early code maps the SCU using CP15, SCU core count limits `cpu_possible`, prepare enables SCU and snapshots the diagnostic register, and secondary boot writes the jump address through SRC then enables the core. i.MX7 counts CPU DT nodes because its SCU does not report cores. LS1021A writes `secondary_startup` to DCFG scratch and wakes CPUs via IPI.

State and persistence: State is limited to static `scu_base`, the static SCU map descriptor, and `g_diag_reg`. Hardware state includes SCU enable, SRC boot vector/core enable written by other i.MX helpers, and LS1021A DCFG scratch register.

Dependencies and integration points: Depends on ARM SMP core, SCU helpers, DT CPU nodes, i.MX SRC helpers (`imx_set_cpu_jump`, `imx_enable_cpu`), hotplug callbacks (`imx_cpu_die/kill`), and LS1021A DCFG DT node.

Risks: `BUG_ON(!dcfg_base)` and assumptions about SCU/DT availability make malformed firmware fatal. The diagnostic-register replication relies on secondary code reading `g_diag_reg` coherently after `sync_cache_w`. CPU count mismatch can hide or expose nonexistent CPUs.

Test signals: Boot SMP on i.MX6/i.MX7/LS1021A, check secondary CPU online, CPU hotplug if enabled, and verify no bad `cpu_possible` count with DT changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx25.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx25.c

Purpose: Minimal i.MX25 suspend-to-memory registration.

Important APIs/types/functions: Defines `imx25_suspend_enter()`, `imx25_suspend_ops`, and `imx25_pm_init()`.

Control flow: Initialization installs suspend ops. Enter accepts only `PM_SUSPEND_MEM` and executes `cpu_do_idle()` when PM is enabled; unsupported states return `-EINVAL`.

State and persistence: No persistent software state beyond global suspend ops. Hardware state changes are whatever WFI/idle triggers on i.MX25.

Dependencies and integration points: Depends on Linux suspend core and ARM idle instruction; called from i.MX25 machine init.

Risks: This is shallow suspend support with no explicit wake/clock/memory sequencing. Platforms needing deeper retention depend on bootloader/SoC defaults and interrupt wake configuration.

Test signals: Build with `CONFIG_PM`, run `echo mem > /sys/power/state`, and validate wake sources and resume console.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx25.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx27.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx27.c

Purpose: i.MX27 suspend support that disables main/system PLL bits before WFI.

Important APIs/types/functions: Defines `mx27_suspend_enter()`, `mx27_suspend_ops`, and `imx27_pm_init()`.

Control flow: On suspend-to-mem, it finds and maps `fsl,imx27-ccm`, clears MPEN/SPEN in the CCM CSCR register, then executes `cpu_do_idle()`. Init installs suspend ops accepting only memory suspend.

State and persistence: Persists a modified CCM register value across idle/resume according to hardware behavior; no software state is cached. The mapped CCM address is not explicitly unmapped.

Dependencies and integration points: Depends on DT CCM node, i.MX relaxed accessors, Linux suspend core, and ARM idle path.

Risks: `BUG_ON(!ccm_base)` makes missing CCM fatal. `of_find_compatible_node()` result is not `of_node_put()` released and the mapping is not unmapped. Clearing PLL bits is board-sensitive and assumes wake/reset sequencing restores clocks correctly.

Test signals: Suspend/resume on i.MX27 hardware, verify clocks after resume, and check DT node presence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx27.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx5.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx5.c

Purpose: i.MX51/i.MX53 CPU idle and suspend implementation, including i.MX53 OCRAM-assisted DDR self-refresh and pad-state handling.

Important APIs/types/functions: Defines `imx51_pm_init()`, `imx53_pm_init()`, `mx5_cpu_lp_set()`, `mx5_suspend_enter()`, `imx5_cpu_do_idle()`, `imx5_pm_idle()`, `imx_suspend_alloc_ocram()`, `imx5_suspend_init()`, `struct imx5_pm_data`, `struct imx5_cpu_suspend_info`, and i.MX53 pad config tables.

Control flow: Common init enables the `gpc_dvfs` clock, maps CCM/Cortex/GPC bases, installs `arm_pm_idle`, sets default `WAIT_UNCLOCKED_POWER_OFF`, initializes cpuidle, optionally copies low-level suspend code to OCRAM, then registers suspend ops. Suspend-to-mem sets STOP_POWER_OFF, flushes TLB/cache, clears EMPGC bits, and either calls OCRAM code or WFI; standby idles with the default state. The OCRAM setup allocates SRAM, copies assembly with `fncpy`, and prepares M4IF/IOMUXC pointers and pad-state descriptors.

State and persistence: Persistent kernel state includes mapped CCM/Cortex/GPC bases, OCRAM executable mapping, copied suspend function pointer, and saved pad-state descriptors inside OCRAM. Hardware state includes CLPCR low-power bits, Cortex platform LPC DSM bits, GPC SRPG controls, M4IF DDR self-refresh, and IOMUXC drive settings.

Dependencies and integration points: Depends on clocks, genalloc SRAM (`mmio-sram`), OF platform devices, `fncpy`, cache/TLB maintenance, TZIC wake synchronization, cpuidle, and `suspend-imx53.S` whose structure offsets must match the C struct.

Risks: High risk is C/assembly layout drift for `struct imx5_cpu_suspend_info`. Missing SRAM or mappings degrades DDR low-power support. Mapped regions are not fully unwound after success. Suspend relies on pad drive changes and DDR self-refresh polling; board-specific memory wiring can be sensitive.

Test signals: Build i.MX51/i.MX53 PM, confirm cpuidle registration, run standby and mem suspend with/without `mmio-sram`, and test DDR retention plus wake sources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx6.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx6.c

Purpose: i.MX6 family low-power, suspend, standby-poweroff, and OCRAM DDR-retention setup.

Important APIs/types/functions: Defines `imx6_pm_ccm_init()`, `imx6q/dl/sl/sx/ul_pm_init()`, `imx6_set_lpm()`, `imx6_enable_rbc()`, `imx6_set_int_mem_clk_lpm()`, `imx6q_pm_enter()`, `imx6q_suspend_init()`, `struct imx6_cpu_pm_info`, SoC data tables, and standby poweroff callback.

Control flow: CCM init maps the CCM, forces CLPCR RUN mode, and optionally registers platform poweroff. Common PM init registers suspend ops, allocates OCRAM, maps MMDC/SRC/IOMUXC/GPC/PL310 bases by compatible string, snapshots DDR IO pad values, copies `imx6_suspend` to OCRAM read-only, and applies ERR007265 GPR workaround. Suspend standby programs STOP_POWER_ON and GPC pre/post hooks around WFI. Suspend-to-mem programs STOP_POWER_OFF, disables internal memory LPM, enables well-bias/RBC, preps GPC/anatop, calls `cpu_suspend()`, then restores SCU/anatop/GPC/RBC/well-bias/LPM.

State and persistence: State includes global `ccm_base`, executable OCRAM mapping, the OCRAM `imx6_cpu_pm_info` block with physical/virtual MMIO bases, DDR type, resume address, and saved MMDC IO pad values. Hardware state spans CCM CLPCR/CCR/CGPR, GPC interrupt masks, anatop, IOMUXC GPR, MMDC DDR self-refresh, SRC resume slots, and optional PL310 cache sync.

Dependencies and integration points: Depends on i.MX CPU type helpers, MMDC DDR type from `mmdc.c`, `suspend-imx6.S`, `resume-imx6.S`, genalloc SRAM, GPC/anatop helpers, ARM GIC/cpu_suspend, syscon regmap, PL310, and DT compatible strings for each SoC variant.

Risks: Very sensitive to C/assembly offset agreement and SoC data correctness. Missing OCRAM removes DDR LPM support. IRQ masking and ERR007265 workaround ordering are critical. `BUG_ON(!ccm_base)` and DT lookup failures can be fatal or degrade suspend. Standby poweroff is only available if DT property allows and global poweroff is unclaimed.

Test signals: Run standby/mem suspend on each i.MX6 variant, verify OCRAM allocation, DDR retention, wake IRQs, cpuidle, poweroff path, and build with/without PL310 and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx6.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx7ulp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx7ulp.c

Purpose: i.MX7ULP System Mode Controller low-power mode setup.

Important APIs/types/functions: Defines `imx7ulp_set_lpm()` and `imx7ulp_pm_init()`, plus SMC PMCTRL field constants for RUN/WAIT/STOP post-stop options.

Control flow: Init maps the `fsl,imx7ulp-smc1` node and programs RUN mode. `imx7ulp_set_lpm()` clears RUNM/STOPM/PSTOPO fields, selects PSTOP3 for run, PSTOP2 for wait, or PSTOP1 for stop, and writes SMC_PMCTRL.

State and persistence: Global state is `smc1_base`; hardware state is SMC PMCTRL low-power mode selection.

Dependencies and integration points: Depends on DT SMC node, i.MX ULP power-mode enum from common headers, and callers in cpuidle/PM paths.

Risks: `smc1_base` is only warning-checked; callers before successful init would dereference NULL. The helper does not serialize access or validate wake-source policy.

Test signals: Boot i.MX7ULP, verify init maps SMC, exercise cpuidle/low-power transitions for RUN/WAIT/STOP, and validate resume clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx7ulp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/resume-imx6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/resume-imx6.S

Purpose: Physical-address-safe i.MX6 CPU resume trampoline.

Important APIs/types/functions: Defines `v7_cpu_resume`, calls `v7_invalidate_l1`, optional `l2c310_early_resume`, then branches to generic `cpu_resume`.

Control flow: Resume starts from physical context after low-power wake, invalidates L1, restores early PL310 state when configured, and hands back to the ARM suspend framework.

State and persistence: No data state. It mutates CPU cache-controller state during resume.

Dependencies and integration points: Depends on ARMv7 assembler helpers, `cpu_resume`, optional L2X0 support, and the PM code that writes this symbol as the resume address.

Risks: Must remain physical-address safe; absolute data references would fail before MMU restoration. Cache ordering must match the suspend path.

Test signals: Suspend-to-RAM resume on i.MX6 with and without PL310, especially after OCRAM suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/resume-imx6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/src.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/src.c

Purpose: i.MX System Reset Controller support for reset-controller consumers and secondary CPU boot/resume registers.

Important APIs/types/functions: Defines `imx_src_init()`, `imx7_src_init()`, `imx_enable_cpu()`, `imx_set_cpu_jump()`, `imx_get_cpu_arg()`, `imx_set_cpu_arg()`, `imx_gpcv2_set_core1_pdn_pup_by_software()`, `imx_src_reset_module()`, and the `imx-src` platform driver.

Control flow: Early init maps SRC for i.MX51 or i.MX7D and clears warm-reset behavior where applicable. Reset-controller probe exposes five software reset lines for GPU/VPU/IPU/OpenVG/IPU2 by setting SCR bits and polling for auto-clear. SMP helpers write boot jump/argument GPRs and enable or reset cores; i.MX7D powers core1 through GPCv2 before toggling A7RCR1.

State and persistence: Global state includes `src_base`, `gpc_base`, `gpr_v2`, and `scr_lock`. Hardware state includes SRC SCR/A7RCR1/GPR boot slots, GPC CPU PGC software power-up/down requests, and reset bits.

Dependencies and integration points: Depends on reset-controller framework, DT compatible nodes, SMP CPU logical mapping, i.MX GPCv2, and `platsmp.c` callers.

Risks: Spinlock covers SRC writes but `imx_gpcv2_set_core1_pdn_pup_by_software()` is called under it and polls atomically, so timing matters. Missing SRC/GPC silently disables some paths. Reset timeout is fixed at 1s. The `fsl,imx51-src` match table is broad for later SoCs using compatible inheritance.

Test signals: Test reset-controller consumers, secondary CPU boot/hotplug on i.MX6/i.MX7, and timeout behavior with invalid reset ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq-ksym.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq-ksym.c

Purpose: Exports assembly SSI FIQ handler symbols for modular i.MX ASoC SSI support.

Important APIs/types/functions: Exports `imx_ssi_fiq_tx_buffer`, `imx_ssi_fiq_rx_buffer`, `imx_ssi_fiq_start`, `imx_ssi_fiq_end`, and `imx_ssi_fiq_base`.

Control flow: No runtime control flow beyond module symbol export table generation.

State and persistence: No owned state; the exported symbols refer to variables/labels in `ssi-fiq.S` patched or copied by SSI audio code.

Dependencies and integration points: Depends on `linux/platform_data/asoc-imx-ssi.h`, module symbol infrastructure, and the assembly FIQ handler.

Risks: The exported data symbols expose writable handler configuration ABI. Mismatches with the assembly labels or module users break FIQ audio transfer.

Test signals: Build modular SSI audio and confirm symbols resolve with `CONFIG_FIQ`/ASoC SSI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq-ksym.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq.S

Purpose: Fast interrupt handler for i.MX SSI audio FIFO service, designed to be copied into the FIQ vector.

Important APIs/types/functions: Defines global labels/data `imx_ssi_fiq_start`, `imx_ssi_fiq_end`, `imx_ssi_fiq_base`, `imx_ssi_fiq_rx_buffer`, and `imx_ssi_fiq_tx_buffer`; uses FIQ banked registers r8/r9 for ring offsets and sizes.

Control flow: On FIQ entry, the handler reads SSI base, checks TX FIFO-empty interrupt enable/status, writes four 16-bit samples from the TX buffer, advances/wraps r8, then checks RX FIFO-full interrupt enable/status, reads four 16-bit samples into the RX buffer, optionally skips AC97 slot 12 dummy words, advances/wraps r9, and returns with `subs pc, lr, #4`.

State and persistence: Persistent state is encoded in FIQ banked registers r8/r9 and the three patched word variables for SSI base/RX/TX buffers. Hardware state is SSI SIER/SISR/SACNT and FIFO reads/writes.

Dependencies and integration points: Depends on ARM FIQ mode, SSI register layout, ASoC SSI setup that patches exported symbols and initializes banked registers, and `ssi-fiq-ksym.c` for modular access.

Risks: Calling the label as a normal function is invalid. The handler assumes buffer size/offset packing in 16-bit halves and fixed FIFO transfer width. It has no locking, bounds checks beyond wrap logic, or cache management; setup must provide coherent buffers.

Test signals: Audio playback/capture stress with FIQ enabled, AC97 and non-AC97 modes, ring wrap tests, and underrun/overrun monitoring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/ssi-fiq.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx53.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx53.S

Purpose: i.MX53 OCRAM-resident low-level suspend routine that places DDR into M4IF self-refresh and changes/restores DDR pad drive settings.

Important APIs/types/functions: Defines `imx53_suspend` and `imx53_suspend_sz`; consumes `struct imx5_cpu_suspend_info` layout via hard-coded offsets.

Control flow: The routine saves r4-r7, saves each configured IOMUXC pad value, sets M4IF FDVFS and waits for FDVACK, applies low-power pad clear/set masks, executes WFI, restores pad values, clears FDVFS, waits for DDR self-refresh exit, restores registers, and returns.

State and persistence: State is the OCRAM pm-info block containing M4IF/IOMUXC bases, IO count, offsets, clear/set masks, and saved values. Hardware state includes M4IF MCR0 FDVFS/FDVACK and IOMUXC pad registers.

Dependencies and integration points: Depends on `pm-imx5.c` for OCRAM allocation and struct layout, ARM assembler/linkage, and i.MX53 memory-controller/IOMUXC register semantics.

Risks: Any C struct layout change without offset update breaks suspend. Infinite polling is possible if DDR self-refresh acknowledge never changes. Pad misconfiguration can prevent resume from DDR self-refresh.

Test signals: Suspend-to-RAM on i.MX53 with DDR retention, wake-source tests, and review offset consistency whenever `struct imx5_cpu_suspend_info` changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx53.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx6.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx6.S

Purpose: i.MX6 OCRAM-resident suspend/resume routine for DDR self-refresh, MMDC IO floating/restoration, RBC setup, and physical resume handoff.

Important APIs/types/functions: Defines `imx6_suspend` and macro `resume_mmdc`; consumes `struct imx6_cpu_pm_info` by hard-coded offsets and references `IMX_DDR_TYPE_LPDDR2`.

Control flow: Entry reads pm-info physical/resume/DDR fields, computes physical `resume` label, preloads TLBs, stores resume address and pm-info address in SRC GPRs, syncs L2, forces MMDC self-refresh, writes low-power IOMUXC settings for MMDC pads, masks/restores GPC interrupts around RBC counter enable, executes WFI, and restores MMDC if wake was pending. The `resume` label starts in physical mode, invalidates I-cache, enables I-cache/branch prediction, clears SRC GPRs, restores MMDC from physical bases, and returns to `v7_cpu_resume`.

State and persistence: State lives in the OCRAM pm-info block: physical/virtual bases, saved pad values, DDR type, and resume address. Hardware state spans SRC GPR1/GPR2, MMDC MAPSR/MPDGCTRL0, IOMUXC pad registers, GPC IMR1-4, CCM CCR, and cache controller state.

Dependencies and integration points: Depends on `pm-imx6.c`, `resume-imx6.S`, PL310 definitions, ARMv7 low-level suspend framework, MMDC DDR type from `mmdc.c`, and exact SoC pad offset tables.

Risks: This is one of the highest-risk files in the set. C/assembly layout drift, wrong pad offsets, broken LPDDR2 special handling, or bad physical/virtual base selection can hang resume. Poll loops have no timeout. It must remain physical-address safe after wake.

Test signals: Run mem suspend/resume on every supported i.MX6 variant and DDR type, test wake-pending path, LPDDR2 read-FIFO reset path, and inspect offsets after any C struct change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/suspend-imx6.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/system.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/system.c

Purpose: i.MX restart/watchdog reset support and optional PL310 prefetch tuning.

Important APIs/types/functions: Defines `mxc_restart()`, `mxc_arch_reset_init()`, optional `imx1_reset_init()`, and `imx_init_l2cache()`.

Control flow: Reset init stores watchdog MMIO base, gets/prepares `imx2-wdt.0` clock, and optionally adjusts the watchdog control bit for i.MX1. Restart enables the watchdog clock, writes the reset bit three times for i.MX6Q erratum ERR004346, waits, logs failure, then falls back to `soft_restart(0)`. L2 init finds `arm,pl310-cache`, maps it, and if disabled configures double linefill, instruction/data prefetch, and offset 15.

State and persistence: Global state is `wdog_base`, `wdog_clk`, and `wcr_enable`. Hardware state is watchdog control, watchdog clock, and PL310 prefetch registers.

Dependencies and integration points: Depends on ARM machine restart path, clock framework, i.MX relaxed 16-bit writes, DT PL310 node, and L2X0 definitions.

Risks: If watchdog base is not initialized, restart relies on fragile jump-to-zero fallback. Clock prepare/enable error handling is minimal. Triple writes are broad across platforms. PL310 tuning only occurs when cache is disabled and assumes register compatibility.

Test signals: Invoke reboot on supported boards and confirm hardware reset. Build/test `CONFIG_CACHE_L2X0` and validate PL310 register programming only on matching systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/system.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/tzic.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-imx/tzic.c

Purpose: TrustZone Interrupt Controller driver for older i.MX SoCs, including irqdomain/generic-chip setup, FIQ selection, suspend wake programming, and wake synchronization.

Important APIs/types/functions: Defines `tzic_init_dt()` via `IRQCHIP_DECLARE`, `tzic_handle_irq()`, `tzic_init_gc()`, optional `tzic_set_irq_fiq()`, optional suspend/resume callbacks, and `tzic_enable_wake()`.

Control flow: DT init maps TZIC, programs controller/priorities/sync, marks interrupts secure, disables all sources, allocates 128 legacy IRQ descriptors, creates a legacy domain, installs four generic chips of 32 IRQs, sets global IRQ handler, and initializes FIQ if enabled. IRQ handling loops over high-priority pending banks masked by security registers and dispatches each hwirq through the domain. Wake setup writes DSMINT and mirrors enabled IRQ masks into wake registers.

State and persistence: Global state is `tzic_base` and `domain`. Hardware state includes INTSEC, enable/clear, priority mask, sync, pending, wake, DSMINT, and optional FIQ security routing registers.

Dependencies and integration points: Depends on irqchip/irqdomain/generic-chip APIs, ARM `set_handle_irq`, optional FIQ support, i.MX relaxed IO, and PM users such as i.MX5 idle.

Risks: Missing DT mapping or descriptor/domain allocation is only `WARN_ON`, so later IRQs can fail badly. Wake programming is bank-wide and depends on generic-chip `wake_active`. `tzic_enable_wake()` returns `-EAGAIN` if DSMINT does not latch, so callers must handle idle failure.

Test signals: Boot with TZIC, test all 128 IRQ banks, FIQ routing, suspend wake sources, and `tzic_enable_wake()` behavior before deep idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/tzic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Kconfig

Purpose: Kconfig entry enabling Intel IXP4xx/XScale platform support.

Important APIs/types/functions: Defines `menuconfig ARCH_IXP4XX` with dependencies on `ARCH_MULTI_V5` and big-endian CPU mode, and selects XScale, GPIO, PCI, I2C, IRQ, timer, endian EHCI, appended DTB, and OF support.

Control flow: No runtime flow; it shapes the kernel configuration graph.

State and persistence: No runtime state. Build-time state selects platform objects and subsystem options.

Dependencies and integration points: Integrates with ARM multi-v5 builds, IXP4XX irq/timer drivers, GPIO, PCI, I2C, and USB EHCI endian handling.

Risks: Over-selecting dependencies can force subsystems into builds. Big-endian and appended-DTB assumptions reflect old bootloaders and can surprise generic kernels.

Test signals: Run `make ARCH=arm olddefconfig` with `ARCH_IXP4XX=y`, verify selected symbols, and boot DT on IXP4xx hardware/emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Makefile

Purpose: Build glue for IXP4xx platform support.

Important APIs/types/functions: Adds `ixp4xx-of.o` to `obj-y`.

Control flow: No runtime flow; Kbuild includes the DT machine descriptor when the directory is selected.

State and persistence: No state beyond build outputs.

Dependencies and integration points: Depends on the Kconfig selecting this machine directory and `ixp4xx-of.c` providing the machine descriptor.

Risks: If this file omits future platform objects, configured support silently lacks required init code.

Test signals: Compile an IXP4xx kernel and confirm `ixp4xx-of.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/ixp4xx-of.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/ixp4xx-of.c

Purpose: Device-tree machine descriptor for Intel IXP4xx SoC families.

Important APIs/types/functions: Defines `ixp4xx_of_board_compat[]` and `DT_MACHINE_START(IXP4XX_DT, ...)` with `.dt_compat`.

Control flow: At boot, ARM machine selection matches root DT compatible strings for ixp42x/43x/45x/46x and otherwise relies on common platform drivers selected by Kconfig.

State and persistence: No mutable state; compatibility table is `__initconst`-like static data.

Dependencies and integration points: Depends on ARM `DT_MACHINE_START` and DT roots using `intel,ixp42x`, `intel,ixp43x`, `intel,ixp45x`, or `intel,ixp46x`.

Risks: The descriptor provides no custom init hooks, so all required init must come from drivers. Missing board-specific compatible strings prevent machine selection.

Test signals: Boot DTs for each compatible family and check timer/irq/GPIO/PCI initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-ixp4xx/ixp4xx-of.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Kconfig

Purpose: Kconfig entry for TI Keystone ARMv7 SoCs.

Important APIs/types/functions: Defines `ARCH_KEYSTONE` with selections for GIC, ARM arch timer, Keystone timer/common clock, reset controller, SMP erratum 798181, DMA zone under LPAE, pinctrl, and generic PM domains.

Control flow: No runtime flow; it enables compile-time support and required subsystem symbols.

State and persistence: No runtime state. Build-time selections influence DMA, PM, timer, irq, clock, and reset behavior.

Dependencies and integration points: Integrates with ARM multi-v7, Keystone timer/clock drivers, PM clock domains, and LPAE DMA mapping.

Risks: Incorrect dependency/selects can produce unbootable images or bad DMA zones, especially with high physical memory under LPAE.

Test signals: Config build matrix for Keystone with/without LPAE, SMP, and PM; verify selected symbols match hardware requirements.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Makefile

Purpose: Build glue for TI Keystone platform support.

Important APIs/types/functions: Links `keystone.o` into the machine directory.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `ARCH_KEYSTONE` selecting the directory and `keystone.c` providing the DT machine descriptor.

Risks: Future Keystone platform hooks require adding objects here.

Test signals: Compile `ARCH_KEYSTONE=y` and verify `keystone.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/keystone.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-keystone/keystone.c

Purpose: TI Keystone2 machine support for PM runtime clock domains, high-memory physical-to-virtual fixups, DMA offset handling, and DT machine selection.

Important APIs/types/functions: Defines `keystone_init()`, `keystone_pm_runtime_init()`, optional `keystone_platform_notifier()`, `keystone_pv_fixup()`, PM domain/notifier objects, compatible tables, and `DT_MACHINE_START(KEYSTONE, ...)`.

Control flow: Init optionally registers a platform bus notifier when LPAE boots from high memory, then installs a pm-clock notifier for matching Keystone SoCs. PV fixup inspects memblock DRAM: no-op for low 32-bit memory, rejects outside the 16G high window, otherwise sets `arch_phys_to_idmap_offset` and returns the high-to-low offset. The LPAE bus notifier assigns DMA offset to non-DT devices.

State and persistence: Global kernel state touched includes `arch_phys_to_idmap_offset`, platform bus notifiers, PM clock domain notifier, and optional DMA offsets on devices. Hardware state is indirect through runtime PM clock operations.

Dependencies and integration points: Depends on memblock, ARM idmap setup, platform bus notifier, DMA direct ops, PM runtime/pm-clock, OF matching, and DT roots for Keystone families.

Risks: High-memory boot depends on exact physical windows. Non-DT device DMA offset handling only applies on BUS_NOTIFY_ADD_DEVICE and logs as errors even on success. PM clock notifier is global once matching node exists.

Test signals: Boot Keystone with low and high DRAM maps, validate DMA for legacy and DT devices, runtime PM clock gating, and idmap correctness under LPAE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-keystone/keystone.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/Makefile

Purpose: Build glue for NXP LPC18xx/43xx DT board support.

Important APIs/types/functions: Adds `board-dt.o` to `obj-y`.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on the LPC18xx machine directory being selected and `board-dt.c` providing the descriptor.

Risks: Missing additional objects would omit future platform hooks.

Test signals: Compile LPC18xx/43xx support and confirm `board-dt.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/board-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/board-dt.c

Purpose: Minimal DT machine descriptor for NXP LPC18xx/LPC43xx Cortex-M class SoCs.

Important APIs/types/functions: Defines `lpc18xx_43xx_compat[]` and `DT_MACHINE_START(LPC18XXDT, ...)`.

Control flow: Boot machine selection matches root compatibles `nxp,lpc1850`, `nxp,lpc4350`, or `nxp,lpc4370`; no custom init hooks are run.

State and persistence: No mutable state; only static compatible table.

Dependencies and integration points: Depends on ARM machine descriptor support and DT platform drivers for all devices.

Risks: No map/init callbacks means platform correctness depends entirely on generic/DT drivers. Missing compatible strings prevent boot selection.

Test signals: Boot matching DTs and verify timer/irq/serial are handled by drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc18xx/board-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Kconfig

Purpose: Kconfig entry for NXP LPC32xx ARM926 platforms.

Important APIs/types/functions: Defines `ARCH_LPC32XX`, depending on multi-v5 little-endian ARM, selecting AMBA, LPC32xx clocksource, ARM926T, GPIOLIB, and optional LPC32xx DMA mux with PL08x.

Control flow: No runtime flow; it controls build inclusion and subsystem availability.

State and persistence: No runtime state. Build state affects clocksource, AMBA, GPIO, CPU, and DMA support.

Dependencies and integration points: Integrates with PL08x DMA, clocksource driver, and the `mach-lpc32xx` objects.

Risks: Little-endian and ARM926 assumptions are mandatory; missing selected subsystems breaks early platform support.

Test signals: Config build with DMA enabled/disabled and boot LPC32xx DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Makefile

Purpose: Build glue for LPC32xx platform objects.

Important APIs/types/functions: Links `common.o`, `serial.o`, `pm.o`, `suspend.o`, and `phy3250.o`.

Control flow: No runtime flow; Kbuild composes the platform support files.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `ARCH_LPC32XX` and the listed C/assembly files.

Risks: Omitting `suspend.o` or `pm.o` would compile but remove suspend functionality; object order is simple but early init ordering is in the code.

Test signals: Compile LPC32xx and verify linked symbols for suspend and machine descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.c

Purpose: Common LPC32xx platform helpers for static IO mapping, unique ID reporting, IRAM size detection, and Ethernet PHY pin mode selection.

Important APIs/types/functions: Defines `lpc32xx_get_uid()`, `lpc32xx_return_iram()`, `lpc32xx_set_phy_interface_mode()`, `lpc32xx_map_io()`, and `lpc32xx_check_uid()` arch initcall.

Control flow: Map IO installs static AHB0/AHB1/FABAPB/IRAM mappings. UID reads four clock/power device ID registers and uses them for `system_serial_*` if unset. IRAM detection probes whether the second 128K bank aliases the first by temporary write/read. PHY mode updates MAC clock-control pin mux bits for MII or RMII.

State and persistence: Persistent state includes cached `iram_size` and global ARM `system_serial_low/high`. Hardware state includes static mappings and MAC pin selection register.

Dependencies and integration points: Depends on `lpc32xx.h` address macros, ARM `iotable_init`, system_info serial globals, and exported NXP misc API users.

Risks: IRAM probing writes to IRAM and assumes it is safe to modify/restore that location. `lpc32xx_set_phy_interface_mode()` treats every non-MII mode as RMII. Raw MMIO accesses depend on static mappings existing first.

Test signals: Boot LPC32xx, check printed UID/system serial, call IRAM helper from a user driver, and validate Ethernet pin mode on MII/RMII boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.h

Purpose: Private LPC32xx architecture declarations shared by platform files.

Important APIs/types/functions: Declares `lpc32xx_map_io()`, `lpc32xx_serial_init()`, `lpc32xx_get_uid()`, `lpc32xx_sys_suspend()`, and `lpc32xx_sys_suspend_sz`.

Control flow: No runtime flow; it provides prototypes for C and assembly integration.

State and persistence: No state, but it exposes the suspend assembly size symbol and UID access contract.

Dependencies and integration points: Used by `common.c`, `phy3250.c`, `pm.c`, and `suspend.S` integration.

Risks: Prototype/signature drift with the assembly symbol or PM caller breaks suspend copying. The suspend size is declared as `int` even though emitted as a word symbol.

Test signals: Compile all LPC32xx objects with warnings enabled; suspend path validates assembly symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/lpc32xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/lpc32xx.h

Purpose: Large LPC32xx SoC register map and bit-definition header for early platform code.

Important APIs/types/functions: Defines physical base addresses for AHB/FAB/APB/IRAM/IROM/EMC, clock/power register addresses and bit masks, interrupt/timer/UART/GPIO/USB register access macros, UART clock-mode helpers, and `IO_ADDRESS`, `io_p2v`, `io_v2p` static mapping macros.

Control flow: No executable flow; consumers expand these macros into raw MMIO accesses and map descriptors.

State and persistence: No mutable software state. The file encodes static virtual mapping and hardware register ABI assumptions.

Dependencies and integration points: Integrated across LPC32xx common, serial, PM, suspend, clocksource, GPIO, UART, USB, and miscellaneous drivers that include the SoC header.

Risks: The static `IO_ADDRESS` transform assumes address bits 20-23 are zero for all HW IO. A wrong bit mask or base impacts many low-level accesses. Heavy macro use bypasses typed regmap or DT resource validation.

Test signals: Build coverage across all LPC32xx users plus boot smoke covering serial, timers, GPIO, Ethernet, USB, PM, and suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/lpc32xx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/phy3250.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/phy3250.c

Purpose: LPC32xx DT machine descriptor and board-level auxiliary platform data for DMA/NAND on PHY3250-class systems.

Important APIs/types/functions: Defines PL08x slave channel data and callbacks, LPC32xx SLC/MLC NAND platform data, auxdata table, `lpc3250_machine_init()`, compatible table, and `DT_MACHINE_START(LPC32XX_DT, ...)`.

Control flow: Machine init runs serial setup then populates DT devices with auxdata binding PL080 DMA and NAND controllers to platform data. Machine descriptor also sets ATAG offset and static IO mapping.

State and persistence: Static platform data defines DMA request lines for SLC and MLC NAND and DMA bus settings. Hardware state changes occur through serial init and child driver probe using auxdata.

Dependencies and integration points: Depends on AMBA PL08x, LPC32xx NAND drivers, OF platform population, static IO mapping, and LPC32xx serial init.

Risks: Auxdata hard-codes physical addresses and device names; DT/address mismatches break platform data attachment. PL08x signal callbacks always return `min_signal` and do no release work.

Test signals: Boot LPC32xx DT, verify PL08x and SLC/MLC NAND get DMA filters/platform data, and check serial early setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/phy3250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/pm.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/pm.c

Purpose: LPC32xx suspend implementation that copies a low-level suspend routine into IRAM so DRAM can enter self-refresh while clocks stop.

Important APIs/types/functions: Defines `lpc32xx_pm_enter()`, `lpc32xx_pm_ops`, and `lpc32xx_pm_init()` arch initcall.

Control flow: PM init sets the EMC SDRAM self-refresh clock behavior and installs suspend ops. Enter allocates a backup of the IRAM target area, copies `lpc32xx_sys_suspend` into IRAM, flushes I-cache/cache, calls the IRAM routine, restores the original IRAM contents, and frees the backup.

State and persistence: State includes a temporary heap backup of the IRAM code area and global suspend ops. Hardware state includes EMC self-refresh mode bit and whatever `suspend.S` changes during halt.

Dependencies and integration points: Depends on `suspend.S` symbols, `lpc32xx.h` static mappings, Linux suspend core, cache maintenance, and kmemdup allocation.

Risks: If allocation fails suspend returns `-ENOMEM`. Copying over IRAM assumes no other critical IRAM user needs that range during suspend. Only mem suspend is advertised despite comments mentioning standby.

Test signals: Run suspend-to-mem, verify IRAM contents restore, DRAM retention, wake events, and behavior under memory pressure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/pm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/serial.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/serial.c

Purpose: LPC32xx standard/high-speed UART early setup and loopback erratum helper.

Important APIs/types/functions: Defines `lpc32xx_loopback_set()`, `lpc32xx_serial_init()`, `struct uartinit`, and UART init tables for UART3-6.

Control flow: Serial init enables UART clocks, disables autoclock by programming UART clock modes, sets pre-UART dividers, flushes RX FIFOs before and after clockmode programming, disables UART6 IrDA pulsing, and disables UART5 USB transparent routing. Loopback helper maps HS UART base to CLOOP bit and toggles it for an LPC3250 erratum workaround.

State and persistence: Hardware state includes UART clock registers, FIFO control/DLL accesses, UART control CLOOP/CTRL bits, IrDA bypass, and UART5 USB route. No persistent software state.

Dependencies and integration points: Depends on clock framework, static LPC32xx MMIO macros, serial core register definitions, and exported NXP misc users.

Risks: `clk_enable()` is called without prepare/error propagation or later disable. FIFO flush reads from UART registers and assumes clocks are live. Unknown high-speed UART bases trigger WARN.

Test signals: Boot with console on standard UARTs, test UART5/USB coexistence, UART6 IrDA bypass, and HS UART loopback erratum behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/suspend.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/suspend.S

Purpose: IRAM-executed LPC32xx low-level suspend routine that places SDRAM into self-refresh, disables HCLK PLL, enters halt, then restores clocks and SDRAM.

Important APIs/types/functions: Defines `lpc32xx_sys_suspend` and `lpc32xx_sys_suspend_sz`.

Control flow: The routine saves registers to a local IRAM stack, loads clock/power and EMC bases, waits for a DRAM busy-to-idle window, requests self-refresh and waits for acknowledge, enters direct-run mode, stops DDR clock, saves/disables HCLK PLL, sets stop mode until wake, restores PLL and waits for lock, restores run mode and DRAM clock, clears self-refresh, waits for EMC exit, restores registers, and returns.

State and persistence: State is saved register values in IRAM plus hardware clock/power, HCLK divider, HCLK PLL, and EMC self-refresh state. No DRAM access is allowed while clocks are unavailable.

Dependencies and integration points: Depends on `pm.c` copying this code to IRAM, `lpc32xx.h` register definitions, and ARM assembler/linkage.

Risks: Polling loops have no timeout. The PLL status wait condition is hardware-specific and any wrong bit interpretation can hang. The routine assumes the IRAM location and local stack are safe and that wake sources are configured before suspend.

Test signals: Suspend/resume on SDRAM and DDR LPC32xx boards, verify wake events, PLL lock, DRAM retention, and no corruption of original IRAM contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/suspend.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Kconfig

Purpose: Kconfig menu for MediaTek ARMv7 SoC families.

Important APIs/types/functions: Defines `ARCH_MEDIATEK` and SoC selections including `MACH_MT2701`, `MACH_MT6589`, `MACH_MT6592`, `MACH_MT7623`, `MACH_MT7629`, `MACH_MT8127`, `MACH_MT8135`, and `MACH_MT8173`, with selections for GIC, timers, SCPSYS, SMP, and platform drivers.

Control flow: No runtime flow; the symbols select which machine/SMP objects and subsystem drivers are built.

State and persistence: No runtime state. Build state gates generic MediaTek machine support and SMP availability.

Dependencies and integration points: Integrates with ARM multi-v7, GIC, arch timer, MediaTek SCPSYS, SMP, and DT roots.

Risks: Incorrect selects can enable SMP or power-domain assumptions on unsupported SoCs. Some symbols are grouped despite differing boot methods.

Test signals: Build configs for each MediaTek SoC and verify expected objects and power-domain/SMP dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Makefile

Purpose: Build glue for MediaTek ARM platform support.

Important APIs/types/functions: Always links `mediatek.o`; links `platsmp.o` when `CONFIG_SMP=y`.

Control flow: No runtime flow beyond Kbuild object selection.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MediaTek Kconfig and SMP configuration.

Risks: SMP boot support is absent from UP builds by construction; future SoC-specific files need explicit entries.

Test signals: Compile MediaTek kernels with SMP on/off and verify object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/mediatek.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/mediatek.c

Purpose: Generic MediaTek ARMv7 DT machine descriptor with early clock/timer initialization.

Important APIs/types/functions: Defines `mediatek_timer_init()`, the `mediatek_board_dt_compat[]` root-compatible list, and `DT_MACHINE_START(MEDIATEK_DT, ...)`.

Control flow: During `.init_time`, selected MT6589/MT7623/MT8135/MT8127 systems map the GPT6 control register at physical `0x10008060`, write `0x31` to enable/free-run GPT6 so the architectural timer clock is ungated, unmap it, then call `of_clk_init(NULL)` and `timer_probe()`. Machine selection matches MT2701, MT6572, MT6582, MT6589, MT6592, MT7623, MT7629, MT8127, or MT8135 root compatibles.

State and persistence: No persistent software state. Hardware state is limited to GPT6 clock/free-run enable on the older listed SoCs; clocksource state is registered by generic timer/clock drivers.

Dependencies and integration points: Depends on OF machine matching, fixed GPT6 physical register knowledge for older SoCs, common clock init, and clocksource timer probing.

Risks: `ioremap()` of GPT6 is not checked before `writel()`, so a mapping failure would crash during early boot. The hard-coded physical address and magic value are SoC-specific and bypass DT resources. SoCs not in the conditional rely entirely on normal DT timer/clock nodes.

Test signals: Boot each compatible family, confirm arch timer availability, and regression-test MT6589/MT7623/MT8135/MT8127 where GPT6 must be explicitly ungated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/mediatek.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/platsmp.c

Purpose: MediaTek secondary CPU boot support for TrustZone and non-TrustZone boot-info register protocols.

Important APIs/types/functions: Defines `struct mtk_smp_boot_info`, boot-info tables for MT8135/MT8127/MT2701, MT6572, MT6589, MT7623/MT6582/MT7629, `mtk_boot_secondary()`, `__mtk_smp_prepare_cpus()`, `mtk_tz_smp_prepare_cpus()`, `mtk_smp_prepare_cpus()`, and CPU method declarations for `mediatek,mt81xx-tz-smp` and `mediatek,mt6589-smp`.

Control flow: Prepare selects the boot-info table by root compatible, maps the boot register block either with `phys_to_virt()` for TrustZone-reserved SRAM or `ioremap()` for normal MMIO, then writes `secondary_startup_arm` to the SoC jump register. Boot validates the requested CPU has a nonzero magic key, writes that key to the per-core release register, and sends a wakeup IPI.

State and persistence: Global state is `mtk_smp_base` and `mtk_smp_info`. Hardware/firmware state includes the jump register and per-core release-key registers in reserved SRAM/MMIO; no persistent kernel-managed resource remains after boot.

Dependencies and integration points: Depends on DT root compatible strings, CPU method compatible strings, ARM SMP core, `secondary_startup_arm`, fixed boot-info addresses/register offsets, and TrustZone firmware/reserved-memory behavior for the TZ path.

Risks: CPU indexes are used as `cpu - 1` into fixed arrays and only support the encoded number of secondary cores. TrustZone mode assumes the physical boot-info area is already mapped/reserved so `phys_to_virt()` is valid. Missing or wrong compatible data leaves `mtk_smp_base` unset and secondary boot fails with `-EINVAL`.

Test signals: Boot SMP on each supported MediaTek SoC, validate CPU1+ online, and test both `mediatek,mt81xx-tz-smp` and `mediatek,mt6589-smp` DT CPU methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mediatek/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-meson/Kconfig

Purpose: Kconfig menu for Amlogic Meson ARMv7 platforms.

Important APIs/types/functions: Defines `ARCH_MESON` plus `MACH_MESON6`, `MACH_MESON8`, `MACH_MESON8B`, and `MACH_MESON8M2`, selecting GIC, arch timer, SMP, and Meson SMP support as appropriate.

Control flow: No runtime flow; it controls which Meson machine and SMP objects build.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7, GIC, timer, DT, and Meson-specific SMP code.

Risks: Selecting SMP support for families depends on matching firmware/register support; configuration mistakes show as secondary CPU boot failures.

Test signals: Build Meson6/8 variants and verify selected SMP/timer/irq symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-meson/Makefile

Purpose: Build glue for Meson ARM platform support.

Important APIs/types/functions: Always links `meson.o`; links `platsmp.o` for SMP builds.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on Meson Kconfig and `CONFIG_SMP`.

Risks: Missing object entries would omit platform hooks.

Test signals: Compile Meson with SMP on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/meson.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-meson/meson.c

Purpose: Generic Meson DT machine descriptor.

Important APIs/types/functions: Defines `meson_common_board_compat[]` and `DT_MACHINE_START(MESON, ...)`.

Control flow: ARM machine selection matches Meson6/8/8b/8m2 root compatibles; no custom init hooks are used.

State and persistence: No mutable state.

Dependencies and integration points: Depends on DT platform drivers and Meson Kconfig selections for irq/timer/SMP.

Risks: All initialization is delegated to drivers; missing compatible strings prevent machine selection.

Test signals: Boot each Meson compatible DT and verify timer/irq/devices initialize.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/meson.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-meson/platsmp.c

Purpose: Amlogic Meson SMP boot support for Meson8/8b/8m2 and Meson6 SCU-based systems.

Important APIs/types/functions: Defines Meson register offsets, `meson_smp_ops`, `meson8_smp_ops`, `meson_smp_prepare_cpus()`, `meson8_smp_prepare_cpus()`, `meson_boot_secondary()`, `meson8_boot_secondary()`, `meson_smp_map()`, and validation helpers.

Control flow: Prepare maps SCU and SRAM/sysctrl as needed, enables SCU, clears secondary CPU reset/address registers, and writes the boot address for Meson8. Boot for Meson8 writes `secondary_startup` into mailbox and wakes via SRAM/sysctrl registers; Meson6 toggles per-core reset through SCU/system registers and waits for secondary startup.

State and persistence: Global state includes mapped SCU, SRAM, and sysctrl bases plus validated physical resources. Hardware state includes SCU enable, CPU reset controls, boot mailbox, and power/clock bits.

Dependencies and integration points: Depends on DT nodes for SCU/SRAM/sysctrl, ARM SCU helpers, SMP core, and SoC-specific compatible strings.

Risks: Mapping/validation is critical because wrong SRAM/sysctrl resources mean writes to the wrong boot registers. CPU count assumptions and boot timeouts are platform-specific.

Test signals: Boot all secondary CPUs on Meson6/8 variants, check DT resource validation, and exercise CPU online/offline where supported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-meson/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Kconfig

Purpose: Kconfig menu for Socionext Milbeaut ARMv7 platforms.

Important APIs/types/functions: Defines `ARCH_MILBEAUT` selecting ARM GIC, and `ARCH_MILBEAUT_M10V` selecting `ARM_ARCH_TIMER`, `MILBEAUT_TIMER`, `PINCTRL`, and `PINCTRL_MILBEAUT`.

Control flow: No runtime flow; the symbols gate machine, timer, GIC, and pinctrl support at build time.

State and persistence: No runtime state. Build configuration determines whether Milbeaut M10V timer/pinctrl/SMP-related code can be linked.

Dependencies and integration points: Integrates with ARM multi-v7, the ARM GIC, Milbeaut timer driver, and Milbeaut pinctrl driver.

Risks: The top-level symbol only selects GIC; M10V-specific timer/pinctrl support requires the child symbol. A partial configuration can compile a kernel that matches the architecture but lacks board-critical drivers.

Test signals: Build `ARCH_MILBEAUT` with and without `ARCH_MILBEAUT_M10V`, check selected timer/pinctrl symbols, and boot a Milbeaut EVB DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Makefile

Purpose: Build glue for Milbeaut platform support.

Important APIs/types/functions: Links `platsmp.o` when SMP is enabled.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on `CONFIG_SMP` and Milbeaut Kconfig.

Risks: UP builds omit any Milbeaut SMP boot hooks.

Test signals: Compile Milbeaut SMP and non-SMP configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/platsmp.c

Purpose: Milbeaut M10V SMP and suspend support using a small SMP SRAM mailbox.

Important APIs/types/functions: Defines `m10v_smp_ops`, `m10v_boot_secondary()`, `m10v_smp_init()`, optional hotplug `m10v_cpu_die()`/`m10v_cpu_kill()`, `m10v_pm_ops`, `m10v_die()`, `m10v_pm_enter()`, and late `m10v_pm_init()`.

Control flow: SMP prepare maps `socionext,milbeaut-smp-sram`, logs boot CPU affinity, and fills four mailbox words with `KERNEL_UNBOOT_FLAG`. Boot resolves the logical CPU MPIDR to a hardware CPU id, writes `secondary_startup` physical address to that CPU mailbox, and sends a wakeup IPI. Hotplug die disables the GIC CPU interface, flushes coherency, and WFI; kill restores the mailbox flag. PM standby executes WFI; suspend-to-mem enters CPU PM, calls `cpu_suspend()` with `m10v_die()`, sets up reboot mappings, and jumps via physical `cpu_reset` to `cpu_resume` after wake.

State and persistence: Global state is mapped `m10v_smp_base` and a temporary `phys_reset` function pointer. Hardware state is the SMP SRAM mailbox and GIC CPU interface during hotplug/suspend.

Dependencies and integration points: Depends on DT SMP SRAM node, MPIDR affinity mapping, ARM SMP/hotplug/suspend frameworks, GIC CPU interface, idmap setup, and `socionext,milbeaut-evb` root compatible for PM registration.

Risks: Only four CPUs are supported. The code logs but otherwise ignores cluster for boot routing. Missing SRAM mapping makes SMP boot fail with `-ENXIO`. Suspend resume path is low-level and depends on physical reset/resume addresses being valid.

Test signals: Boot all CPUs on M10V, test CPU hotplug, standby and mem suspend on `socionext,milbeaut-evb`, and verify mailbox flags around offline/online.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-milbeaut/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Kconfig

Purpose: Kconfig menu for Marvell PXA/MMP ARMv5/v7 SoCs.

Important APIs/types/functions: Defines `ARCH_MMP` and SoC/machine symbols such as `CPU_PXA168`, `CPU_PXA910`, `CPU_MMP2`, `MACH_MMP_DT`, `MACH_MMP2_DT`, `MACH_MMP3_DT`, and `MACH_MMP2_DT`, selecting clocksource, irqchip, pinctrl, timers, SMP, and cpuidle pieces.

Control flow: No runtime flow; it controls build composition and dependencies for MMP platforms.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v5/v7, MMP timers, irq, pinctrl, clocksource, and DT machine descriptors.

Risks: A broad ARCH symbol spanning multiple CPU generations can select incompatible support if SoC symbols are mis-set.

Test signals: Build each MMP/PXA configuration and verify selected drivers/objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Makefile

Purpose: Build glue for Marvell MMP platform support.

Important APIs/types/functions: Builds `common.o`, `time.o`, DT board files, `mmp3.o`, and optional `platsmp.o` according to CPU/machine/SMP symbols.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MMP Kconfig symbols.

Risks: Incorrect object gating can include wrong machine descriptors or omit SMP/timer support.

Test signals: Compile matrix for PXA168/PXA910/MMP2/MMP3 and SMP on/off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/addr-map.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/addr-map.h

Purpose: Address-map helper definitions for MMP/PXA APB/AXI static mappings.

Important APIs/types/functions: Defines `APB_PHYS_BASE`, `AXI_PHYS_BASE`, sizes, virtual bases, `APB_VIRT_BASE`, `AXI_VIRT_BASE`, `APB_PHYS_BASE`, `AXI_PHYS_BASE`, `APBC_REG()`, `APMU_REG()`, `MPMU_REG()`, and `CIU_REG()` helpers.

Control flow: No executable flow; consumers expand macros into MMIO pointers.

State and persistence: No mutable state. Encodes static virtual mapping offsets and physical register windows.

Dependencies and integration points: Used by MMP common/time/platform code for early register access before full drivers bind.

Risks: Static mapping constants must match `iotable_init` descriptors. Wrong macros route clock/power writes to invalid addresses.

Test signals: Build and boot MMP/PXA boards, checking early timer/clock/interrupt setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/addr-map.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.c

Purpose: Common MMP/PXA static IO mapping and chip-id discovery.

Important APIs/types/functions: Defines exported `mmp_chip_id`, `mmp_map_io()`, and `mmp2_map_io()`.

Control flow: `mmp_map_io()` maps APB and AXI register windows with `iotable_init()` and immediately reads `MMP_CHIPID` from the CIU register into exported `mmp_chip_id`. `mmp2_map_io()` extends that setup by mapping the PGU/SCU window used by MMP2/MMP3-class cores.

State and persistence: Persistent kernel state is exported `mmp_chip_id`. Static hardware mappings cover APB, AXI, and optionally PGU/SCU device ranges.

Dependencies and integration points: Depends on `addr-map.h`, ARM static mapping, raw MMIO reads, and CPU type helpers consuming the chip id.

Risks: The chip-id read requires AXI mapping to be valid and happens very early. Wrong mapping constants affect every early MMP register access. There is no runtime DT resource validation for these static windows.

Test signals: Boot PXA168/PXA910/MMP2/MMP3 DT machines, verify chip-id-based CPU detection, and test early timer/clock code that uses APB/AXI mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.h

Purpose: Tiny MMP private declaration header.

Important APIs/types/functions: Declares shared init/map helpers used by DT board files.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates MMP common code with `mmp-dt.c`, `mmp2-dt.c`, and `mmp3.c`.

Risks: Prototype drift causes build or boot-time init omissions.

Test signals: Compile all MMP machine descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp-dt.c

Purpose: Device-tree machine descriptors for Marvell PXA168 and PXA910 boards.

Important APIs/types/functions: Defines `pxa168_dt_board_compat[]`, `pxa910_dt_board_compat[]`, `mmp_init_time()`, and two `DT_MACHINE_START` descriptors.

Control flow: Machine selection matches `mrvl,pxa168-aspenite` or `mrvl,pxa910-dkb`. Mapping uses `mmp_map_io()`. Time init optionally initializes Tauros2 cache, initializes clocks from DT, and probes timers.

State and persistence: No owned mutable state beyond static IO mapping and generic clock/timer/cache registration.

Dependencies and integration points: Depends on MMP common mapping, optional Tauros2 cache support, OF clock init, and clocksource probing.

Risks: The compatible lists are board-specific rather than broad SoC compatibles, so other DTs need explicit additions. Timer correctness depends on the DT timer node and the static APB mapping used by common code.

Test signals: Boot Aspenite and DKB DTs, verify Tauros2 when enabled, clock init, and timer interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp2-dt.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp2-dt.c

Purpose: Device-tree machine descriptor for Marvell MMP2 platforms.

Important APIs/types/functions: Defines `mmp_init_time()`, `mmp2_dt_board_compat[]`, and `DT_MACHINE_START(MMP2_DT, ...)`.

Control flow: Boot selection matches root compatible `mrvl,mmp2`, maps APB/AXI plus PGU through `mmp2_map_io()`, optionally initializes Tauros2 cache, initializes clocks from DT, and probes timers.

State and persistence: No owned runtime state beyond static mappings and generic cache/clock/timer registration.

Dependencies and integration points: Depends on MMP2 static mapping, optional Tauros2, OF clocks, and timer nodes.

Risks: The descriptor is minimal and delegates all device creation to DT drivers. Missing PGU/SCU mapping would break MMP2/MMP3-style early users.

Test signals: Boot MMP2 DT, check chip id, timer, clocks, and cache initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp2-dt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp3.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp3.c

Purpose: Device-tree machine descriptor for Marvell MMP3/PXA2128/Armada 620.

Important APIs/types/functions: Defines `mmp3_dt_board_compat[]` and `DT_MACHINE_START(MMP2_DT, "Marvell MMP3")` with PL310 auxiliary-control values.

Control flow: Boot selection matches `marvell,mmp3`, maps using `mmp2_map_io()`, and configures PL310 auxiliary control to enable full-line-of-zero/write allocate, data prefetch, and instruction prefetch with mask `0xc20fffff`.

State and persistence: No owned mutable state; hardware state includes L2 cache auxiliary settings applied by ARM cache init.

Dependencies and integration points: Depends on MMP2-style mapping, ARM L2X0 support, and the MMP3 DT compatible.

Risks: The machine symbol name reuses `MMP2_DT`, which is potentially confusing but compile-time legal. Cache aux settings are global for the machine and must match MMP3 PL310 behavior.

Test signals: Boot MMP3 DT, verify L2 cache aux register programming and early MMIO mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/mmp3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/platsmp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/platsmp.c

Purpose: MMP3 SMP boot support using the CIU software branch register and SCU.

Important APIs/types/functions: Defines `mmp3_boot_secondary()`, `mmp3_smp_prepare_cpus()`, `mmp3_smp_ops`, and CPU method `marvell,mmp3-smp`.

Control flow: Prepare enables the SCU at the statically mapped PGU/SCU base. Boot writes the physical `secondary_startup` address to `CIU_REG(0x24)`, which the boot ROM on the second core polls; no IPI is required.

State and persistence: Hardware state is SCU enable and the CIU software branch register. No persistent software state.

Dependencies and integration points: Depends on static PGU/SCU mapping from `mmp2_map_io()`, ARM SCU helpers, and the MMP3 boot ROM protocol.

Risks: Only the boot-ROM-polled branch register is programmed, so platforms with a different secondary-release protocol will fail. There is no timeout or CPU id validation beyond the caller.

Test signals: Boot MMP3 SMP, verify the second core enters Linux, and test that the `marvell,mmp3-smp` CPU method is present in DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/platsmp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/regs-timers.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/regs-timers.h

Purpose: MMP/PXA timer register and bit definitions.

Important APIs/types/functions: Defines timer register offsets and control/status bit masks used by `time.c`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates with the MMP clocksource/clockevent implementation.

Risks: Wrong offsets or bit definitions break scheduler ticks and delay calibration.

Test signals: Timer interrupt and clocksource tests on MMP/PXA platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/regs-timers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/time.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mmp/time.c

Purpose: MMP/PXA timer clocksource, sched_clock, and one-shot clockevent driver.

Important APIs/types/functions: Defines `timer_read()`, `mmp_read_sched_clock()`, `timer_interrupt()`, `timer_set_next_event()`, `timer_set_shutdown()`, `timer_config()`, `mmp_timer_init()`, `mmp_dt_init_timer()`, clockevent `ckevt`, clocksource `cksrc`, and `TIMER_OF_DECLARE(mmp_timer, ...)`.

Control flow: DT init gets and enables the timer clock if present, otherwise falls back to 6.5 MHz for PJ4 or 3.25 MHz, maps the IRQ and registers, configures timer 1 as free-running clocksource/sched_clock and timer 0 as a one-shot match clockevent. `timer_read()` triggers a CVWR latch and reads it after a small delay because direct CR reads have metastability issues. The interrupt clears match status, disables timer 0, and calls the clockevent handler.

State and persistence: Global state is `mmp_timer_base`, registered sched_clock/clocksource/clockevent objects, and requested timer IRQ. Hardware state includes TMR_CCR, CMR, PLCR, ICR, IER, match registers, CER, and CVWR latch.

Dependencies and integration points: Depends on `regs-timers.h`, OF clock/IRQ/address APIs, clocksource/clockevents core, sched_clock, and MMP CPU type helpers.

Risks: Clock fallback rates are hard-coded and must match silicon. Timer register programming uses raw MMIO and assumes the mapped timer is stable. Failure after enabling a clock or mapping can leak partial state. Bad CVWR handling breaks timekeeping.

Test signals: Boot with `mrvl,mmp-timer`, verify sched_clock monotonicity, clockevent interrupts, one-shot timer accuracy, and fallback-rate platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mmp/time.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Kconfig

Purpose: Kconfig entry for MStar/SigmaStar ARMv7 SoCs.

Important APIs/types/functions: Defines `ARCH_MSTARV7`, selecting ARM GIC, arch timer, and required platform support.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7, irq/timer, and MStar DT machine descriptor.

Risks: Incorrect irq/timer selections prevent basic boot.

Test signals: Build MStar V7 config and boot matching DT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Makefile

Purpose: Build glue for MStar V7 platform.

Important APIs/types/functions: Links `mstarv7.o`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Depends on MStar Kconfig.

Risks: Only one object is linked; future hooks require updates here.

Test signals: Compile with `ARCH_MSTARV7=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/mstarv7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mstar/mstarv7.c

Purpose: MStar/SigmaStar ARMv7 DT machine support, including a SoC-specific memory barrier and simple CPU1 release.

Important APIs/types/functions: Defines `mstarv7_mb()`, optional `mstarv7_boot_secondary()`, `mstarv7_smp_ops`, `mstarv7_init()`, root-compatible table, and `DT_MACHINE_START(MSTARV7_DT, ...)`.

Control flow: Machine init maps the `mstar,l3bridge` node and installs `soc_mb = mstarv7_mb`; the barrier toggles the L3 bridge flush trigger and polls status done using relaxed MMIO so it does not recurse into itself. SMP boot currently supports only CPU1: it maps `mstar,smpctrl`, writes the low/high 16-bit physical `secondary_startup_arm` address, writes unlock magic `0xbabe`, sends a wakeup IPI, and unmaps the control block.

State and persistence: Global state is `l3bridge` and the global architecture memory-barrier hook `soc_mb`. Hardware state includes L3 bridge flush/status registers and CPU1 SMP control boot/unlock registers.

Dependencies and integration points: Depends on DT nodes `mstar,l3bridge` and `mstar,smpctrl`, ARM heavy memory-barrier hook support selected by Kconfig, GIC/arch timer setup, and root compatibles for Infinity/Mercury families.

Risks: If L3 bridge mapping fails the code warns that DMA will be broken, because devices can see stale CPU writes. The barrier has no lock and can be reentered from interrupts. SMP supports only CPU1 and does not `of_node_put()` the SMP control node on the success path.

Test signals: Boot with Ethernet or other DMA devices to validate the custom barrier, run SMP CPU1 online tests, and check behavior when L3 bridge DT node is missing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mstar/mstarv7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Kconfig

Purpose: Kconfig entry for legacy Marvell MV78xx0 platforms.

Important APIs/types/functions: Defines `ARCH_MV78XX0` with selections for Feroceon/Sheeva CPU support, PCI, IRQ, timers, MPP, and board support.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with non-DT Marvell board files, PCIe, MPP, IRQ, and timer code.

Risks: Legacy non-DT platform selections can pull in board-specific assumptions and fixed mappings.

Test signals: Build MV78xx0 defconfig and boot known boards such as Buffalo WXL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Makefile

Purpose: Build glue for MV78xx0 platform.

Important APIs/types/functions: Links common, irq, mpp, pcie, and board setup objects according to config.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Depends on MV78xx0 Kconfig board symbols.

Risks: Missing an object can remove board init or core PCI/IRQ setup.

Test signals: Compile MV78xx0 board configs and inspect linked objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/bridge-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/bridge-regs.h

Purpose: MV78xx0 bridge-register address and bit definitions.

Important APIs/types/functions: Defines CPU/DDR/bridge register offsets used by common, IRQ, PCIe, and reset code.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Integrates with low-level MV78xx0 register access helpers.

Risks: Wrong offsets affect resets, interrupts, PCIe windows, and system identification.

Test signals: Boot smoke exercising IRQ, PCIe, and reset paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/bridge-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/buffalo-wxl-setup.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/buffalo-wxl-setup.c

Purpose: Board setup for Buffalo WXL NAS systems based on MV78xx0.

Important APIs/types/functions: Defines board init data for MPP pins, Ethernet, SATA, NAND/flash, buttons/LEDs, PCIe, and `MACHINE_START` style board registration.

Control flow: Board init configures MPP, registers platform devices, initializes PCIe/SATA/ethernet/flash/GPIO resources, and wires board-specific peripherals.

State and persistence: Persistent hardware state includes pin mux, registered platform devices/resources, MAC/flash/SATA setup, and GPIO defaults.

Dependencies and integration points: Depends on MV78xx0 common init, MPP, PCIe, legacy platform device APIs, and board bootloader machine ID.

Risks: Hard-coded resources and GPIOs are board-specific; applying to a variant can break storage/network/LEDs. Legacy board files lack DT validation.

Test signals: Boot Buffalo WXL, verify Ethernet, SATA disks, flash, LEDs/buttons, and PCIe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/buffalo-wxl-setup.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c

Purpose: Core MV78xx0 platform initialization: register maps, clocks/timers, device helpers, CPU/window setup, and restart/identify paths.

Important APIs/types/functions: Defines common init/map helpers and platform-device registration helpers used by board files.

Control flow: Early init maps SoC registers, identifies variant, sets up MBUS/DDR/windows, initializes timers/IRQ helpers, and exposes helpers for Ethernet/SATA/USB/PCIe/platform devices.

State and persistence: State includes static register mappings, SoC revision/id information, IO windows, and registered platform devices. Hardware state includes bridge/MBUS address decode and clocks.

Dependencies and integration points: Depends on Marvell common MBUS, Orion-style platform helpers, MV78xx0 headers, IRQ/timer/MPP/PCIe code, and legacy board files.

Risks: Legacy fixed resources are sensitive to SoC revision and bootloader state. Window setup errors break DMA or device MMIO. Without DT, board files must be exact.

Test signals: Boot multiple MV78xx0 variants, verify SoC ID, MBUS windows, timers, Ethernet/SATA/USB/PCIe, and reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.h

Purpose: Private MV78xx0 declarations shared by board/core files.

Important APIs/types/functions: Declares common init, map, device setup, PCIe, MPP, IRQ, and board helper functions.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates board setup files with `common.c`, `mpp.c`, `pcie.c`, and `irq.c`.

Risks: Prototype drift breaks legacy board builds or causes wrong init ordering.

Test signals: Compile all MV78xx0 board configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irq.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irq.c

Purpose: MV78xx0 interrupt-controller setup.

Important APIs/types/functions: Defines IRQ initialization and mask/unmask/chained handling helpers for MV78xx0 interrupt registers.

Control flow: Init maps/uses bridge interrupt registers, configures irq chips/domains or legacy descriptors, masks/unmasks sources, and dispatches pending interrupts.

State and persistence: Hardware state is interrupt mask/cause registers; software state is irq chip data/descriptor setup.

Dependencies and integration points: Depends on `irqs.h`, bridge regs, ARM irq core, and machine init.

Risks: Wrong mask/cause handling loses interrupts or causes storms. Legacy IRQ numbering must match board resources.

Test signals: Boot and exercise timer, GPIO, Ethernet, SATA, and PCIe interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irqs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irqs.h

Purpose: MV78xx0 fixed interrupt-number definitions.

Important APIs/types/functions: Defines IRQ constants for bridge, timers, GPIO, PCIe, Ethernet, SATA, USB, and other SoC blocks.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Used by board files and irq setup for legacy resource numbers.

Risks: Wrong numbers silently route devices to bad interrupts.

Test signals: Compile board resources and run interrupt smoke tests on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/irqs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.c

Purpose: MV78xx0 multi-purpose-pin configuration helper.

Important APIs/types/functions: Defines MPP setup tables/helpers for applying pin mux values.

Control flow: Board init passes MPP configs; helper writes mux registers through Marvell MPP common logic.

State and persistence: Hardware state is MPP/pinmux registers; software state is only transient config arrays.

Dependencies and integration points: Depends on `mpp.h`, Marvell MPP helpers, and board setup files.

Risks: Pinmux mistakes can disable storage, UART, GPIO, or network pins and are hard to diagnose.

Test signals: Board boot tests for all pin-dependent devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.h

Purpose: MV78xx0 MPP pin function definitions.

Important APIs/types/functions: Defines per-pin MPP function macros and helper declarations used by board files.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Integrates with `mpp.c` and board setup pin arrays.

Risks: Incorrect function encodings write wrong mux values.

Test signals: Compile board files and validate pin functions on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mpp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mv78xx0.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mv78xx0.h

Purpose: Main MV78xx0 SoC address map and helper macro header.

Important APIs/types/functions: Defines register base addresses, peripheral resources, window offsets, and conversion/access macros for MV78xx0 code.

Control flow: No runtime flow.

State and persistence: No mutable state.

Dependencies and integration points: Shared by common, IRQ, PCIe, MPP, and board setup code.

Risks: Incorrect base addresses break broad platform functionality.

Test signals: Boot tests covering early mapping, timers, IRQ, PCIe, and device resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/mv78xx0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/pcie.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/pcie.c

Purpose: MV78xx0 PCIe host-controller setup and link/resource handling.

Important APIs/types/functions: Defines PCIe initialization, link detection, resource/window setup, and platform registration helpers.

Control flow: Init enumerates available PCIe ports, configures address decode/windows, checks link state, and registers host bridges/resources.

State and persistence: Hardware state includes PCIe control/status and MBUS decode windows; software state includes PCI resources and port descriptors.

Dependencies and integration points: Depends on MV78xx0 common/bridge headers, PCI core, MBUS/window helpers, and board init.

Risks: PCIe windows and link detection are board/SoC sensitive. Wrong resources can break DMA or overlap other MMIO.

Test signals: Boot with PCIe devices, verify enumeration, config space access, DMA, and absent-link handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mv78xx0/pcie.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Kconfig -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Kconfig

Purpose: Kconfig menu for Marvell EBU SoCs including Armada 370/375/38x/39x/XP, Dove, and Kirkwood.

Important APIs/types/functions: Defines `ARCH_MVEBU`, `MACH_MVEBU_ANY`, `MACH_MVEBU_V7`, individual SoC symbols, and selects MBUS, irqchips, timers, SMP, PMSU, coherency, PM, and cache support as needed.

Control flow: No runtime flow; it controls build-time selection of shared and SoC-specific MVEBU support.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7/v5, Marvell MBUS, irq/timer/cache/PM/SMP drivers, and DT machine descriptors.

Risks: The menu spans old and newer SoCs with different coherency and PM behavior; wrong symbol combinations can build invalid boot paths.

Test signals: Build matrix for Armada/Dove/Kirkwood with SMP/PM options and verify selected objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Makefile

Purpose: Build glue for MVEBU platform objects.

Important APIs/types/functions: Links shared system-controller/soc-id, V7 board/coherency/PMSU/CPU reset/SMP/PM objects, and SoC-specific Dove/Kirkwood files according to config.

Control flow: No runtime flow.

State and persistence: No runtime state.

Dependencies and integration points: Depends on MVEBU Kconfig symbols and PM/SMP options.

Risks: Object gating controls critical boot paths; missing coherency/PMSU objects breaks SMP or suspend on Armada.

Test signals: Compile each MVEBU SoC config with SMP/PM combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/armada-370-xp.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/armada-370-xp.h

Purpose: Small Armada 370/XP SMP declaration header.

Important APIs/types/functions: Declares `armada_xp_secondary_startup()` and `armada_xp_smp_ops`.

Control flow: No runtime flow.

State and persistence: No state.

Dependencies and integration points: Integrates assembly secondary startup with C SMP ops.

Risks: Symbol mismatches break secondary CPU boot linkage.

Test signals: Compile Armada XP SMP and boot secondary CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/armada-370-xp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/board-v7.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/board-v7.c

Purpose: MVEBU ARMv7 DT machine initialization for Armada 370/375/38x/39x/XP.

Important APIs/types/functions: Defines board init, restart, L2/cache/coherency/PMSU integration, compatible tables, and DT machine descriptor.

Control flow: Machine init sets up SoC-specific services, coherency fabric, MBUS/device population, cpuidle/PM hooks, and restart path as appropriate before handing devices to DT.

State and persistence: State includes initialized coherency/PMSU/global platform hooks and registered platform devices. Hardware state includes MBUS/coherency/cache/restart controller setup.

Dependencies and integration points: Depends on MVEBU coherency, PMSU, CPU reset, system controller, OF platform population, L2 cache, and DT compatibles.

Risks: Init ordering is critical: coherency must be ready before DMA-heavy devices, and restart/PM hooks must match SoC. Missing DT nodes degrade features.

Test signals: Boot Armada V7 boards, verify DMA coherency, SMP, restart, cpuidle/suspend, and device population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/board-v7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.c

Purpose: MVEBU hardware coherency fabric support for Armada 370/375/38x/XP, including DMA coherency enablement and CPU coherent entry.

Important APIs/types/functions: Defines global `coherency_base`, `coherency_phys_base`, `set_cpu_coherent()`, `coherency_init()`, `coherency_available()`, SoC-specific init helpers, CPU/PCI notifiers, and low-level assembly hooks `ll_enable_coherency()`/`ll_add_cpu_to_smp_group()`.

Control flow: Init locates coherency fabric and CPU config nodes, maps registers, detects coherency type, enables fabric features for supported SoCs, and records physical base. CPU paths call low-level assembly to add CPUs to SMP/coherency groups. Late init installs DMA-coherent ops or notifiers, and PCI init can attach coherency notifier support.

State and persistence: Global state includes coherency bases, CPU config base, physical base, and notifier registration. Hardware state includes IO sync barriers, CPU config shared-L2 bits, coherency fabric target windows, and DMA coherency behavior.

Dependencies and integration points: Depends on OF address mapping, MBUS, DMA mapping ops, PCI, SMP platform helpers, `coherency_ll.S`, and MVEBU SoC ID detection.

Risks: Coherency misconfiguration causes data corruption, not just boot failure. SoC revision differences matter. Notifier ordering with device creation/PCI probing is subtle. Assembly helpers depend on global symbols being mapped/initialized.

Test signals: Stress DMA on Ethernet/SATA/PCIe/USB before and after SMP bring-up, test CPU hotplug, and verify coherent DMA ops on each Armada family.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.h

Purpose: Declarations for MVEBU coherency support shared with C and assembly.

Important APIs/types/functions: Declares `coherency_base`, `coherency_phys_base`, `set_cpu_coherent()`, `coherency_init()`, and `coherency_available()`.

Control flow: No runtime flow.

State and persistence: Exposes global coherency mapping/physical base state.

Dependencies and integration points: Used by board init, SMP/PM code, and `coherency_ll.S`.

Risks: Declaration/type drift breaks low-level assembly and SMP coherency entry.

Test signals: Compile MVEBU coherency and boot SMP/DMA workloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency_ll.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency_ll.S

Purpose: Low-level MVEBU coherency assembly routines run during early CPU bring-up and low-power transitions.

Important APIs/types/functions: Defines routines such as `ll_add_cpu_to_smp_group`, `ll_enable_coherency`, and related coherency toggles referenced by C code.

Control flow: Assembly accesses coherency fabric registers through global base/physical symbols, sets CPU membership/coherency bits, and returns to C/boot code.

State and persistence: Hardware state is coherency fabric CPU membership and enable bits; software state is implicit via global base symbols.

Dependencies and integration points: Depends on `coherency.c` globals, ARM assembler conventions, and Armada coherency register layout.

Risks: Must be safe in early/physical contexts and preserve required registers. Bad ordering can produce cache/DMA corruption.

Test signals: Boot secondary CPUs, hotplug, suspend/resume if relevant, and DMA stress after coherency enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/coherency_ll.S -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/common.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/common.h

Purpose: Shared MVEBU platform declarations.

Important APIs/types/functions: Declares `mvebu_restart()`, `mvebu_cpu_reset_deassert()`, `mvebu_pmsu_set_cpu_boot_addr()`, and related PM/SMP helpers depending on config.

Control flow: No runtime flow.

State and persistence: No owned state; exposes platform hooks.

Dependencies and integration points: Used by board, SMP, PM, and CPU reset files.

Risks: Prototype mismatches can break platform hook linkage.

Test signals: Compile all MVEBU variants with SMP/PM/restart options.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/cpu-reset.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/cpu-reset.c

Purpose: MVEBU per-CPU reset controller helper.

Important APIs/types/functions: Defines CPU reset/deassert helpers including `mvebu_cpu_reset_deassert()` and initialization over DT reset-controller registers.

Control flow: Init maps CPU reset registers, and callers deassert/reset secondary CPU lines during SMP boot or hotplug.

State and persistence: Global mapped reset base and hardware CPU reset state are the key state.

Dependencies and integration points: Depends on DT reset-controller/system-controller nodes, SMP boot code, and MVEBU common declarations.

Risks: Wrong CPU id/register bit mapping prevents secondary CPU boot or can reset the wrong core.

Test signals: Boot all CPUs and exercise CPU hotplug on Armada boards.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/cpu-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/dove.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/dove.c

Purpose: Marvell Dove DT machine support.

Important APIs/types/functions: Defines Dove init, compatible table, and `DT_MACHINE_START(DOVE_DT, ...)`.

Control flow: Init sets up MBUS and Tauros2/cache/PMU pieces as appropriate, then populates DT devices.

State and persistence: State includes machine descriptor and initialized cache/MBUS platform state.

Dependencies and integration points: Depends on Dove PMU, Tauros2 cache support, MBUS, and DT platform drivers.

Risks: Descriptor delegates most work to drivers; cache/MBUS init mismatches affect DMA/peripherals.

Test signals: Boot Dove DT and verify cache, MBUS devices, timer/irq, and restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/dove.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp-a9.S -->
# sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp-a9.S

Purpose: Cortex-A9 secondary CPU entry point for MVEBU Armada 375/38x style systems.

Important APIs/types/functions: Defines `mvebu_cortex_a9_secondary_startup`.

Control flow: The secondary entry fixes BE8 endianness when needed, calls `armada_38x_scu_power_up` to power/enable SCU-side CPU state, then branches to generic `secondary_startup`.

State and persistence: No data state. Hardware state is whatever `armada_38x_scu_power_up` changes before the generic secondary path.

Dependencies and integration points: Depends on `pmsu_ll.S` providing `armada_38x_scu_power_up`, ARM assembler conventions, and C SMP code programming this label as the boot address.

Risks: If the SCU power-up helper is missing or wrong, secondary CPUs may jump into Linux without required coherency/power state. The label must remain suitable as an early secondary entry point.

Test signals: Boot SMP on Armada 375/38x/39x Cortex-A9 systems and verify all secondary CPUs enter the kernel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-mvebu/headsmp-a9.S -->
