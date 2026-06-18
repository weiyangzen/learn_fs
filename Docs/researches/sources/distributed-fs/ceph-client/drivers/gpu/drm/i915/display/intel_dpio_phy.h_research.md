# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dpio_phy.h

## Purpose

`intel_dpio_phy.h` declares the DPIO PHY interface used by i915 display code. It exposes the PHY/channel enums and the platform-specific helpers implemented in `intel_dpio_phy.c` for BXT/GLK, VLV, and CHV display PHY programming. The header also provides no-op/static-inline fallbacks when the file is included without `I915`, allowing non-i915 build contexts to compile without pulling in DPIO implementation details.

## Important APIs And Types

`enum dpio_channel` defines `DPIO_CH0` and `DPIO_CH1`, matching the two possible channels inside dual-channel DPIO PHYs. `enum dpio_phy` defines `DPIO_PHY0`, `DPIO_PHY1`, and `DPIO_PHY2`, covering VLV/CHV/BXT/GLK mappings.

The BXT/GLK API includes `bxt_port_to_phy_channel()`, `bxt_dpio_phy_set_signal_levels()`, `bxt_dpio_phy_init()`, `bxt_dpio_phy_uninit()`, `bxt_dpio_phy_is_enabled()`, `bxt_dpio_phy_verify_state()`, `bxt_dpio_phy_calc_lane_lat_optim_mask()`, `bxt_dpio_phy_set_lane_optim_mask()`, and `bxt_dpio_phy_get_lane_lat_optim_mask()`.

The VLV/CHV mapping API includes `vlv_dig_port_to_channel()`, `vlv_dig_port_to_phy()`, `vlv_pipe_to_phy()`, and `vlv_pipe_to_channel()`.

The CHV API includes `chv_set_phy_signal_level()`, `chv_data_lane_soft_reset()`, `chv_phy_pre_pll_enable()`, `chv_phy_pre_encoder_enable()`, `chv_phy_release_cl2_override()`, and `chv_phy_post_pll_disable()`.

The VLV API includes `vlv_set_phy_signal_level()`, `vlv_phy_pre_pll_enable()`, `vlv_phy_pre_encoder_enable()`, `vlv_phy_reset_lanes()`, and `vlv_wait_port_ready()`.

## Control Flow And State

The header itself does not own runtime state. Its declarations are called by display modeset, encoder enable/disable, and PLL setup code. In `#ifdef I915` builds the declarations bind to the full implementation. In the fallback branch, all mutating operations become empty functions, status queries return safe defaults (`false` for enabled, `true` for verify), and mapping functions return PHY0/CH0.

The fallback behavior is intentionally compile-oriented, not hardware-functional. It prevents unresolved symbols in non-i915 contexts but does not represent usable DPIO operation.

## Dependencies And Integration Points

The header forward-declares `enum pipe`, `enum port`, `struct intel_crtc_state`, `struct intel_digital_port`, `struct intel_display`, and `struct intel_encoder` to avoid heavy includes. It includes only `<linux/types.h>` for fixed-width integer and boolean type availability.

The declarations are consumed by display PLL code, DDI/DP encoder enable paths, VLV/CHV power-gating code, and BXT PLL manager code. Because the enums are used across multiple files, changes to the enum ordering would affect register macro indexing and platform mapping logic.

## Risks And Edge Cases

The biggest header-level risk is semantic mismatch between fallback stubs and real implementation. A non-i915 build can compile but will silently skip all PHY programming. Another risk is adding new ports/PHYs without extending both the enum and implementation tables. Function signatures carry platform assumptions such as lane count, port clock, and `intel_crtc_state` contents; callers must compute these before invoking the PHY helpers.

## Test Signals

Build coverage should include both `I915` and non-`I915` include contexts. Runtime validation is indirect: successful modesets on VLV/CHV/BXT/GLK, absence of missing-case warnings in mapping helpers, and matching PHY state verification all confirm that callers and declarations stay aligned.
