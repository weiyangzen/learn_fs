# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-infracfg.c

## Purpose
This file provides exported helpers to set and clear MediaTek infrastructure bus protection bits, plus an early MT8192 workaround disabling an unsupported GPU-to-ACP path.

## Important APIs, Types, and Functions
Exported functions are `mtk_infracfg_set_bus_protection()` and `mtk_infracfg_clear_bus_protection()`. `mtk_infracfg_init()` is a `postcore_initcall` that finds the MT8192 infracfg syscon and sets `MT8192_INFRA_CTRL_DISABLE_MFG2ACP`.

## Control Flow and State
The set/clear helpers write either update-style or set/clear-style protection registers, then poll `INFRA_TOPAXI_PROTECTSTA1` until bits are reflected. The initcall writes persistent hardware register state early in boot for MT8192 if the syscon exists.

## Dependencies and Integration Points
The code depends on regmap, syscon lookup, MediaTek infracfg public register definitions, and jiffies-derived timeout constants. Power domain and SoC drivers call the exported protection helpers when gating domains or buses.

## Risks and Test Signals
Risks include polling the wrong status register for SoCs with different ack locations and timeout behavior when a bus client is active. Test signals include power-domain on/off cycles, regmap poll timeouts, and MT8192 GPU stability without spurious ACP faults.
