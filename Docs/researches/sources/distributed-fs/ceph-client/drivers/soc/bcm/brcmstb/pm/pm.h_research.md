# sources/distributed-fs/ceph-client/drivers/soc/bcm/brcmstb/pm/pm.h

Purpose: shared constants and prototypes for Broadcom STB AON power management. It defines MMIO offsets, bit masks, and the assembly helper contracts used by C and assembly sources.

Important APIs/types/macros: AON offsets include `AON_CTRL_PM_CTRL`, `AON_CTRL_PM_INITIATE`, and `AON_CTRL_HOST_MISC_CMDS`; DDR/timer offsets include `DDR40_PHY_CONTROL_REGS_0_PLL_STATUS`, `DDR40_PHY_CONTROL_REGS_0_STANDBY_CTRL`, and timer registers. Power command masks include `PM_S2_COMMAND`, `PM_COLD_CONFIG`, `PM_WARM_CONFIG`, and method-1 variants. For MIPS, it declares `brcm_pm_do_s2(u32 *s2_params)`, `brcm_pm_do_s3(void __iomem *, int)`, and `s3_reentry`.

Control flow and integration: the header is included from `pm-mips.c`, `s2-mips.S`, and `s3-mips.S`, guaranteeing that C and assembly agree on register offsets and power-control bit encodings.

State and persistence: no state is owned here, but the constants define persistent side effects in AON SRAM/control registers and DDR PHY/timer blocks.

Dependencies and risks: depends on architecture-specific prototypes under `CONFIG_MIPS` and alternate declarations for non-MIPS assembly interfaces. Risks are ABI drift between the C callers and assembly helpers, especially if bit masks or offsets change without synchronized hardware validation.

Test signals: build coverage for both assembler and C inclusion, suspend/resume validation for every PM bit pattern, and power-off/warm-boot behavior matching AON register writes.
