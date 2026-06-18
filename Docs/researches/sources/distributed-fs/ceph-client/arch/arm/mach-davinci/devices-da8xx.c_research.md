# sources/distributed-fs/ceph-client/arch/arm/mach-davinci/devices-da8xx.c

Purpose: provides DA8xx shared peripheral base-address helpers.

Important APIs/types/functions: global `da8xx_syscfg0_base`, `da8xx_syscfg1_base`, static `da8xx_ddr2_ctlr_base`, and `da8xx_get_mem_ctlr()`.

Control flow: callers request the DDR2 controller base; the helper lazily maps `DA8XX_DDR2_CTL_BASE` once and returns the cached mapping.

State and persistence: SYSCFG mappings are initialized by SoC setup; the DDR2 controller mapping persists after first use.

Dependencies and integration: used by DA8xx PM/sleep code and board glue needing memory-controller registers.

Risks: lazy mapping can fail late if memory is constrained, and callers must handle NULL. The globals assume `da850_init()` or equivalent ran first for SYSCFG bases.

Test signals: DDR2 low-power suspend path, callers checking non-NULL memory controller mapping, and boot warnings for failed `ioremap()`.
