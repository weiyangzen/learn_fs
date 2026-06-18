<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c

## Purpose

`sun8i_hdmi_phy.c` implements the Allwinner HDMI PHY companion for DW-HDMI systems. It initializes PHY register access, calibration, PLL/analog settings, HPD/DDC/CEC pin behavior, per-SoC DW-HDMI PHY ops or tables, and exposes the PHY instance to the DW-HDMI wrapper.

## Important APIs, Types, And Functions

Public APIs are `sun8i_hdmi_phy_get()`, `sun8i_hdmi_phy_init()`, `sun8i_hdmi_phy_deinit()`, and `sun8i_hdmi_phy_set_ops()`, plus exported `sun8i_hdmi_phy_driver`. Key internals include `sun8i_a83t_hdmi_phy_config/disable()`, `sun8i_h3_hdmi_phy_config/disable()`, `sun8i_hdmi_phy_unlock()`, `sun8i_hdmi_phy_init_a83t()`, `sun8i_hdmi_phy_init_h3()`, and `sun50i_hdmi_phy_init_h6()`. Variant tables cover A83T, H3, R40, A64, and H6.

## Control Flow

Probe maps PHY registers, creates regmap, gets bus/mod clocks, optional PLL parents, shared PHY reset, stores variant, and publishes drvdata. DW-HDMI bind calls `sun8i_hdmi_phy_get()` and `sun8i_hdmi_phy_init()`. Init deasserts reset, enables bus/mod clocks, optionally creates/enables a PHY clock, then runs the variant init sequence. H3-like init unlocks scrambled registers, powers/calibrates analog blocks, enables DDC pins, clears CEC to hardware control, and records `rcal`. Per-mode PHY ops program polarity and frequency-dependent PLL/analog values; A83T uses DW PHY I2C writes, while H3-like variants use native PHY registers. H6 supplies DW-HDMI MPLL/current/PHY tables instead of custom ops.

## State And Persistence Behavior

Persistent state is `struct sun8i_hdmi_phy` with clocks, regmap, reset, variant, and calibration value. Hardware state persists in analog/PLL/debug/REXT/CEC registers and optional PHY clock divider/parent until disabled or reset.

## Dependencies And Integration Points

It depends on platform/OF, regmap, clock/reset, delays, DW-HDMI PHY helpers, and the shared header. `sun8i_dw_hdmi.c` uses it to supply `dw_hdmi_plat_data` PHY ops/config and to initialize/deinitialize hardware.

## Risks And Test Signals

Risks include undocumented magic values, long sleeps in mode set, ignored calibration poll return, preserving clock parent/divider while rewriting PLL regs, variant-specific second PLL handling, and probe deferral if drvdata is not ready. Test all compatibles, 27/74.25/148.5/297/594 MHz modes, HPD/DDC/CEC behavior, PHY clock parent/divider, suspend/resume, and repeated mode switches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_hdmi_phy.c -->
