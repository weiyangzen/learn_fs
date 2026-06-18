<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c -->
# sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c

Purpose: i.MX8M DDR controller devfreq driver. It uses NXP firmware SMC calls for DDR DVFS while keeping the Linux clock tree aligned with firmware-selected clock parents and rates.

Important APIs and control flow: probe queries firmware for supported frequency count and per-index metadata, gets DRAM core/pll/alt/apb clocks, loads DT OPPs, disables OPPs not reported by firmware, and registers a userspace-governed devfreq profile. `imx8m_ddrc_target()` resolves a requested OPP, skips no-op transitions, finds matching firmware frequency info, calls `imx8m_ddrc_set_freq()`, then verifies the resulting core clock. `imx8m_ddrc_set_freq()` obtains new mux parents by firmware-provided indexes, prepares/enables them, calls `imx8m_ddrc_smc_set_freq()`, updates Linux clock parents, refreshes the PLL rate, and drops temporary references. The SMC helper disables local IRQs and passes an online CPU mask encoded by CPU index.

State and persistence behavior: per-device state stores the devfreq profile/device, four clocks, firmware frequency count, and up to four firmware frequency descriptors. OPPs come from DT but are pruned dynamically according to firmware support.

Dependencies and integration points: depends on ARM SMCCC SIP service `0xc2000004`, clk provider internals for parent-by-index lookup, devfreq/OPP/userspace governor, and compatible `fsl,imx8m-ddrc`.

Risks and test signals: firmware-reported clock parent indexes must match Linux clock parent ordering; SMC failures are not directly reported by the firmware call wrapper; CPU mask encoding assumes CPU numbers fit byte slots in a 32-bit value; `clk_prepare_enable(NULL)` relies on common clock tolerance for optional parents. Test signals include firmware frequency enumeration, unsupported DT OPP disabling, successful high/low DDR transitions, clock parent/rate consistency after SMC, local IRQ-disabled switching behavior, and rejection of invalid firmware parent indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/devfreq/imx8m-ddrc.c -->
