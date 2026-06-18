## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/vlv_dpio_phy_regs.h

### Purpose

`vlv_dpio_phy_regs.h` is the Valleyview/Cherryview DPIO PHY register definition layer used by the i915 display PHY programming code. It does not execute logic; it names sideband register offsets and field encodings for VLV/CHV common, PLL, PCS, and TX register blocks.

### Important APIs, types, and functions

The public surface is preprocessor-only: base-address helpers such as `_VLV_PLL()`, `_CHV_PLL()`, `_VLV_PCS()`, `_VLV_TX()`, register macros such as `VLV_PLL_DW3()`, `VLV_PCS01_DW10()`, `CHV_CMN_DW14()`, and field helpers built from `REG_BIT`, `REG_GENMASK`, and `REG_FIELD_PREP`. Key fields cover PLL divisors (`DPIO_*_DIV`), calibration/lock bits, PCS reset/data-width/swing/de-emphasis controls, lane stagger/deskw, common-lane powerdown, and CHV buffer enable state.

### Control flow

There is no runtime control flow. Consumers compute a register offset, call `vlv_dpio_get()`, then access it through `vlv_dpio_read()`/`vlv_dpio_write()` from `vlv_sideband.c`. The macros are heavily used by `display/intel_dpio_phy.c` for PLL setup, HDMI/DP lane signal-level programming, power sequencing, and CHV/VLV PHY-specific read-modify-write sequences.

### State and persistence behavior

The header owns no software state. It describes persistent hardware PHY state in IOSF sideband registers: PLL divider programming, common lane powerdown, TX swing/de-emphasis, lane reset, lane skew/stagger, clock channel selection, and lock/frequency-lock indicators. Incorrect values can persist until the PHY is reprogrammed, power-gated, or reset.

### Dependencies

It depends on `intel_display_reg_defs.h` for `_PIPE()`, `REG_BIT`, masks, and field preparation helpers. Semantically it depends on DPIO sideband routing from `vlv_sideband.h` and on platform topology from `intel_dpio_phy.c`.

### Integration points

The primary integration point is the VLV/CHV display PHY implementation. The register constants are passed to `vlv_dpio_read()` and `vlv_dpio_write()` and are protected by `vlv_dpio_get()`/`vlv_dpio_put()` sideband access bracketing. They are independent from the MIPI DSI controller register map but share the same platform family and sideband access mechanism.

### Risks

Field mistakes here can misprogram the PHY without compiler errors. The VLV and CHV address formulas are similar but not interchangeable; using the wrong macro can target the wrong common lane or PLL channel. Some macros encode broadcast/group/per-lane views of related registers, so a consumer must intentionally choose whether programming should affect one lane, one channel group, or the broadcast aperture.

### Test signals

Useful validation signals are i915 display build coverage, HDMI/DP link training on VLV/CHV hardware, PHY power-cycle/resume tests, PLL lock checks, and register readback traces around `intel_dpio_phy.c` signal-level and reset sequences.
