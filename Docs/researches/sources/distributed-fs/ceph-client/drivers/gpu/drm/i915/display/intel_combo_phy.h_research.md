# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_combo_phy.h

## Purpose
Declares the combo PHY lifecycle and lane power interface used by i915 display encoder code.

## APIs and integration
`intel_combo_phy_init()` and `intel_combo_phy_uninit()` manage global PHY setup/teardown. `intel_combo_phy_power_up_lanes()` adjusts active lane masks for a PHY using DSI flag, lane count, and lane reversal. The header depends on `enum phy`, `struct intel_display`, and `bool`.

## State, risks, and tests
The header owns no state but exposes functions that mutate PHY MMIO registers. Risks are misuse with non-combo PHYs or unsupported lane counts; the implementation emits missing-case diagnostics. Tests should cover link bring-up with 1/2/4 lane and DSI configurations.
