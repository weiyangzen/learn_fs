# sources/distributed-fs/ceph-client/drivers/usb/dwc3/dwc3-generic-plat.c

## Purpose
`dwc3-generic-plat.c` is a generic flattened platform wrapper for SoCs that embed a DWC3 core but need only common reset/clock handling plus small per-compatible hooks. It embeds `struct dwc3` and calls `dwc3_core_probe()` directly instead of populating a child `snps,dwc3` node.

## Important APIs, Types, and Functions
`struct dwc3_generic` stores the embedded core, bulk clocks, and reset array. `struct dwc3_generic_config` supplies optional `init()` and `dwc3_properties`. Platform hooks include `dwc3_eic7700_init()` for ESWIN HSP syscon programming and `dwc3_spacemit_k1_init()` for optional host VBUS regulator enable. Main functions are `dwc3_generic_probe()`, `dwc3_generic_remove()`, `dwc3_generic_suspend()`, `dwc3_generic_resume()`, and runtime PM wrappers.

## Control Flow
Probe allocates state, gets the MMIO resource, asserts/deasserts resets with a short delay, registers a devm reset-assert cleanup, enables all clocks with `devm_clk_bulk_get_all_enabled()`, fills `dwc3_probe_data` with `ignore_clocks_and_resets = true`, applies match-data properties and optional init hook, then calls `dwc3_core_probe()`. Remove calls `dwc3_core_remove()`. System suspend calls `dwc3_pm_suspend()` then disables bulk clocks; resume enables clocks then calls `dwc3_pm_resume()`. Runtime PM delegates to exported DWC3 runtime helpers.

## State and Persistence Behavior
State is the embedded `struct dwc3`, reset handle, and bulk clock array. Reset cleanup is devm-managed. No persistent storage exists. Platform syscon writes for EIC7700 and VBUS regulator state for Spacemit are live hardware state only.

## Dependencies and Integration Points
The file integrates reset arrays, bulk clocks, optional regulators, syscon/regmap, OF match data, and DWC3 core PM/probe APIs. Configured compatibles include Spacemit K1/K3, Freescale LS1028A with `gsbuscfg0_reqinfo`, ESWIN EIC7700, and StarFive JHB100.

## Risks
Because this wrapper tells the core to ignore clocks/resets, it must keep clock and reset sequencing correct for every compatible. `devm_clk_bulk_get_all_enabled()` couples acquisition and enable, so suspend/resume must match bulk clock state. Per-compatible init hooks are small but hardware-specific; syscon phandle argument count and offsets must match bindings. If `dwc3_core_probe()` partially initializes, unwind depends on devm and core error paths.

## Test Signals
Test probe/remove and system/runtime PM on each compatible, reset assertion at detach, host VBUS regulator behavior on Spacemit host mode, EIC7700 syscon bit programming, LS1028A GSBUSCFG0 request-info propagation, and clock state after repeated suspend/resume cycles.
