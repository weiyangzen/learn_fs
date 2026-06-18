<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c

## Purpose
`msdi.c` implements a custom reset sequence for the OMAP2420 MSDI/MMC controller. The sequence powers the controller and sets a target clock divider before waiting for reset completion.

## Important APIs, Types, and Functions
The public function is `omap_msdi_reset(struct omap_hwmod *oh)`. Important constants include `MSDI_CON_OFFSET`, `MSDI_CON_POW_MASK`, `MSDI_CON_CLKD_MASK`, `MSDI_CON_CLKD_SHIFT`, and `MSDI_TARGET_RESET_CLKD`.

## Control Flow
The reset helper soft-resets the hwmod, reads `MSDI_CON`, powers the module, clears and writes the reset clock divider, then polls `SYSS_RESETDONE_MASK` using `omap_test_timeout()`. It warns on timeout and returns zero.

## State and Persistence Behavior
State is the MSDI controller's power and clock-divider bits plus reset state. No persistent data is written.

## Dependencies and Integration Points
It depends on OMAP hwmod accessors, reset constants from `common.h`/`prm.h`, and the `mmc.h` declaration. It integrates with OMAP2420 MMC hwmod reset callbacks.

## Risks
The function returns success even on timeout. Incorrect divider/power programming may prevent reset or leave the controller in an unexpected clock state. This code should remain limited to OMAP2420.

## Test Signals
Build `CONFIG_SOC_OMAP2420`, boot with MMC enabled, verify no reset timeout warning, and exercise card initialization, I/O, and suspend/resume. Confirm non-2420 builds use the stub from `mmc.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/msdi.c -->
