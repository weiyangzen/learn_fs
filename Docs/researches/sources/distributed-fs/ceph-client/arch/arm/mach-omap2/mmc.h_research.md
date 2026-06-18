<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h

## Purpose
`mmc.h` provides legacy OMAP MMC base/count definitions and a conditional prototype for the OMAP2420 MSDI reset helper.

## Important APIs, Types, and Functions
It defines `OMAP24XX_NR_MMC`, `OMAP2420_MMC_SIZE`, `OMAP2_MMC1_BASE`, and `OMAP4_MMC_REG_OFFSET`. It forward-declares `struct omap_hwmod`. If `CONFIG_SOC_OMAP2420` is enabled it declares `omap_msdi_reset()`, otherwise it provides an inline stub returning zero.

## Control Flow
No direct runtime control flow exists beyond the config-selected inline stub. Callers can invoke `omap_msdi_reset()` without wrapping their own OMAP2420 config conditionals.

## State and Persistence Behavior
No state is stored. The constants describe hardware address and register layout.

## Dependencies and Integration Points
It integrates with OMAP MMC/MSDI hwmod data and reset code in `msdi.c`. `OMAP1_MMC_SIZE` must be defined by included context in users.

## Risks
The stub can hide accidental use on unsupported SoCs. Wrong base or offset values break MMC register access. OMAP2420 MSDI reset behavior is special and must remain config-gated.

## Test Signals
Compile OMAP2420 and non-OMAP2420 configs. On OMAP2420, verify MMC reset and card detection; on other SoCs, confirm callers link against the stub without changing behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/mmc.h -->
