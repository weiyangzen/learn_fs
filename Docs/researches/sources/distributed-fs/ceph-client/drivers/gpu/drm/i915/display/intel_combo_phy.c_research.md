# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.c

## Purpose
Initializes, verifies, powers lane subsets, and uninitializes Intel combo PHYs used by display ports. It handles process/voltage compensation programming, PHY master/slave quirks, platform-specific PHY_MISC availability, and lane power masks for DSI and non-DSI links.

## Important APIs and functions
Public APIs are `intel_combo_phy_init()`, `intel_combo_phy_uninit()`, and `intel_combo_phy_power_up_lanes()`. Internal logic includes `icl_get_procmon_ref_values()`, `icl_set_procmon_ref_values()`, `icl_verify_procmon_ref_values()`, `has_phy_misc()`, `icl_combo_phy_enabled()`, `ehl_vbt_ddi_d_present()`, `phy_is_master()`, `icl_combo_phy_verify_state()`, `icl_combo_phys_init()`, and `icl_combo_phys_uninit()`.

## Control flow
Init iterates all combo PHYs, skips already-verified PHYs, programs PHY_MISC/mux state when present, applies display version 12+ ODCC/DCC settings, writes process-monitor reference values, enables IREFGEN on master PHYs, sets `COMP_INIT`, and enables common-lane power-down control. Lane power updates compute a `PWR_DOWN_LN_*` mask from lane count, DSI status, and reversal before updating `ICL_PORT_CL_DW10`. Uninit walks PHYs in reverse, warns if PHY A state changed unexpectedly, powers down DE IO compensation where available, and clears `COMP_INIT`.

## State and integration
State persists entirely in combo PHY MMIO registers: COMP, CL, PCS, TX, and PHY_MISC. It depends on VBT port/DSI presence, platform flags, `intel_phy_is_combo()`, `intel_de` MMIO helpers, and register definitions. Encoders call the lane power API as link configuration changes.

## Risks and test signals
Risks include wrong process/voltage tables, incorrect VBT DDI-D mux choice on EHL/JSL, powering the wrong lanes under reversal, missing PHY_MISC quirks, and stale firmware-initialized PHY state. Test signals include boot/display bring-up on ICL/TGL/RKL/DG1/ADL-S/EHL/JSL, register state verification logs, link training stability, and suspend/resume uninit/init cycles.
