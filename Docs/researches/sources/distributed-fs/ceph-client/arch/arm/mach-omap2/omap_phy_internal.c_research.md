# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_phy_internal.c

## Purpose
`omap_phy_internal.c` performs an early OMAP4430 USB PHY power-down workaround. The internal MUSB PHY is enabled after reset, and leaving it enabled can block core retention; this file powers it down until the USB driver needs it.

## Important APIs, Types, and Functions
The key function is `omap4430_phy_power_down()`, registered with `omap_early_initcall()`. It uses `cpu_is_omap44xx()`, `ioremap(OMAP443X_SCM_BASE, SZ_1K)`, `writel_relaxed(PHY_PD, ctrl_base + CONTROL_DEV_CONF)`, and `iounmap()`.

## Control Flow
During early OMAP init, the callback exits on non-OMAP44xx systems. On OMAP44xx, it maps the SCM control region, writes the `PHY_PD` bit into `CONTROL_DEV_CONF`, unmaps, and returns. Later USB/MUSB driver code owns re-enabling the PHY when needed.

## State and Persistence Behavior
The persistent state is a hardware control-module bit that powers down the PHY. No software state is stored after the early init call.

## Dependencies and Integration Points
It depends on `soc.h` and `control.h`, and indirectly on OMAP4 MUSB/TWL6030 USB integration. It affects PM core retention and USB driver bring-up ordering.

## Risks
Wrong SoC detection or register address can disable unrelated control bits. Removing the early power-down can cause core retention failures, while failing to let USB later re-enable the PHY breaks MUSB operation.

## Test Signals
Boot OMAP4430 with PM enabled and verify core retention is reachable before USB use. Then load/use MUSB and confirm USB still enumerates. Check for control-module ioremap failures and no suspend/resume regression.
