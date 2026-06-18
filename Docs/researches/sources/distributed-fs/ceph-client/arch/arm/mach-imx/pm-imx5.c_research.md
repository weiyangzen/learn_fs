# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx5.c

Purpose: i.MX51/i.MX53 CPU idle and suspend implementation, including i.MX53 OCRAM-assisted DDR self-refresh and pad-state handling.

Important APIs/types/functions: Defines `imx51_pm_init()`, `imx53_pm_init()`, `mx5_cpu_lp_set()`, `mx5_suspend_enter()`, `imx5_cpu_do_idle()`, `imx5_pm_idle()`, `imx_suspend_alloc_ocram()`, `imx5_suspend_init()`, `struct imx5_pm_data`, `struct imx5_cpu_suspend_info`, and i.MX53 pad config tables.

Control flow: Common init enables the `gpc_dvfs` clock, maps CCM/Cortex/GPC bases, installs `arm_pm_idle`, sets default `WAIT_UNCLOCKED_POWER_OFF`, initializes cpuidle, optionally copies low-level suspend code to OCRAM, then registers suspend ops. Suspend-to-mem sets STOP_POWER_OFF, flushes TLB/cache, clears EMPGC bits, and either calls OCRAM code or WFI; standby idles with the default state. The OCRAM setup allocates SRAM, copies assembly with `fncpy`, and prepares M4IF/IOMUXC pointers and pad-state descriptors.

State and persistence: Persistent kernel state includes mapped CCM/Cortex/GPC bases, OCRAM executable mapping, copied suspend function pointer, and saved pad-state descriptors inside OCRAM. Hardware state includes CLPCR low-power bits, Cortex platform LPC DSM bits, GPC SRPG controls, M4IF DDR self-refresh, and IOMUXC drive settings.

Dependencies and integration points: Depends on clocks, genalloc SRAM (`mmio-sram`), OF platform devices, `fncpy`, cache/TLB maintenance, TZIC wake synchronization, cpuidle, and `suspend-imx53.S` whose structure offsets must match the C struct.

Risks: High risk is C/assembly layout drift for `struct imx5_cpu_suspend_info`. Missing SRAM or mappings degrades DDR low-power support. Mapped regions are not fully unwound after success. Suspend relies on pad drive changes and DDR self-refresh polling; board-specific memory wiring can be sensitive.

Test signals: Build i.MX51/i.MX53 PM, confirm cpuidle registration, run standby and mem suspend with/without `mmio-sram`, and test DDR retention plus wake sources.
