# sources/distributed-fs/ceph-client/arch/arm/mach-imx/pm-imx6.c

Purpose: i.MX6 family low-power, suspend, standby-poweroff, and OCRAM DDR-retention setup.

Important APIs/types/functions: Defines `imx6_pm_ccm_init()`, `imx6q/dl/sl/sx/ul_pm_init()`, `imx6_set_lpm()`, `imx6_enable_rbc()`, `imx6_set_int_mem_clk_lpm()`, `imx6q_pm_enter()`, `imx6q_suspend_init()`, `struct imx6_cpu_pm_info`, SoC data tables, and standby poweroff callback.

Control flow: CCM init maps the CCM, forces CLPCR RUN mode, and optionally registers platform poweroff. Common PM init registers suspend ops, allocates OCRAM, maps MMDC/SRC/IOMUXC/GPC/PL310 bases by compatible string, snapshots DDR IO pad values, copies `imx6_suspend` to OCRAM read-only, and applies ERR007265 GPR workaround. Suspend standby programs STOP_POWER_ON and GPC pre/post hooks around WFI. Suspend-to-mem programs STOP_POWER_OFF, disables internal memory LPM, enables well-bias/RBC, preps GPC/anatop, calls `cpu_suspend()`, then restores SCU/anatop/GPC/RBC/well-bias/LPM.

State and persistence: State includes global `ccm_base`, executable OCRAM mapping, the OCRAM `imx6_cpu_pm_info` block with physical/virtual MMIO bases, DDR type, resume address, and saved MMDC IO pad values. Hardware state spans CCM CLPCR/CCR/CGPR, GPC interrupt masks, anatop, IOMUXC GPR, MMDC DDR self-refresh, SRC resume slots, and optional PL310 cache sync.

Dependencies and integration points: Depends on i.MX CPU type helpers, MMDC DDR type from `mmdc.c`, `suspend-imx6.S`, `resume-imx6.S`, genalloc SRAM, GPC/anatop helpers, ARM GIC/cpu_suspend, syscon regmap, PL310, and DT compatible strings for each SoC variant.

Risks: Very sensitive to C/assembly offset agreement and SoC data correctness. Missing OCRAM removes DDR LPM support. IRQ masking and ERR007265 workaround ordering are critical. `BUG_ON(!ccm_base)` and DT lookup failures can be fatal or degrade suspend. Standby poweroff is only available if DT property allows and global poweroff is unclaimed.

Test signals: Run standby/mem suspend on each i.MX6 variant, verify OCRAM allocation, DDR retention, wake IRQs, cpuidle, poweroff path, and build with/without PL310 and suspend.
