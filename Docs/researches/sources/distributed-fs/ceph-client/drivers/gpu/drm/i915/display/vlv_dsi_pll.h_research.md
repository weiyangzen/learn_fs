## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dsi_pll.h

### Purpose

`vlv_dsi_pll.h` declares the DSI PLL control API used by VLV/CHV/BXT/GLK DSI code. It separates PLL computation, enable/disable, clock readback, clock reset, and assertion helpers from the main DSI encoder implementation.

### Important APIs, types, and functions

The VLV path exposes `vlv_dsi_pll_compute()`, `vlv_dsi_pll_enable()`, `vlv_dsi_pll_disable()`, `vlv_dsi_get_pclk()`, and `vlv_dsi_reset_clocks()`. The BXT/GLK path exposes `bxt_dsi_pll_compute()`, `bxt_dsi_pll_enable()`, `bxt_dsi_pll_disable()`, `bxt_dsi_get_pclk()`, `bxt_dsi_reset_clocks()`, and `bxt_dsi_pll_is_enabled()`. Assertion helpers are `assert_dsi_pll_enabled()` and `assert_dsi_pll_disabled()`.

### Control flow

There is only compile-time stub control flow. In non-i915 builds, `bxt_dsi_pll_is_enabled()` returns false and assertions do nothing. Real control flow is in `vlv_dsi_pll.c`.

### State and persistence behavior

The header stores no state. The declared functions operate on `struct intel_crtc_state::dsi_pll`, DSI clock fields, and hardware PLL registers.

### Dependencies

It includes `<linux/types.h>` for `u32`/`bool` and forward-declares `enum port`, `struct intel_crtc_state`, `struct intel_display`, and `struct intel_encoder`.

### Integration points

`vlv_dsi.c` depends on this API for mode compute and encoder power sequencing. Platform-specific PLL implementation details remain hidden behind the function pair naming.

### Risks

Wrong platform selection at call sites can program the wrong register block. Non-i915 stubs must remain harmless because they short-circuit state checks used before DSI register access.

### Test signals

Build coverage for i915 and non-i915 configurations, plus modeset tests that exercise both VLV and BXT function families.
