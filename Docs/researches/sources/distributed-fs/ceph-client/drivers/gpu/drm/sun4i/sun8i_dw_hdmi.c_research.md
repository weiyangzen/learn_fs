<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c

## Purpose

`sun8i_dw_hdmi.c` wraps the Synopsys DesignWare HDMI bridge for newer Allwinner SoCs. It binds a DRM TMDS encoder, powers/reset-enables the controller and regulator, obtains the companion Allwinner HDMI PHY, provides SoC mode limits, and registers both HDMI controller and PHY platform drivers from one module.

## Important APIs, Types, And Functions

Key functions are `sun8i_dw_hdmi_bind()`, `sun8i_dw_hdmi_unbind()`, `sun8i_dw_hdmi_encoder_mode_set()`, `sun8i_dw_hdmi_find_possible_crtcs()`, mode validators for A83T and H6, and module init/exit registering `sun8i_dw_hdmi_pltfm_driver` plus `sun8i_hdmi_phy_driver`. Quirks are in `struct sun8i_dw_hdmi_quirks`.

## Control Flow

Bind computes possible CRTCs directly or through TCON TOP port 4, gets reset, TMDS clock, and `hvcc` regulator, enables regulator/reset/clock, parses the `phys` phandle, obtains and initializes the Allwinner PHY, initializes a simple TMDS encoder, fills `dw_hdmi_plat_data` with mode validation/infoframe flags and PHY ops/config, then calls `dw_hdmi_bind()`. Mode set updates the TMDS clock rate from the selected CRTC clock. Unbind reverses DW-HDMI, PHY, clock, reset, and regulator state.

## State And Persistence Behavior

Persistent state is `struct sun8i_dw_hdmi`: TMDS clock, device, DW-HDMI handle, encoder, PHY pointer, platform data, regulator, quirks, and reset. Hardware state persists in controller reset/clock/regulator, DW-HDMI bridge registers, PHY state, and TCON TOP routing selected elsewhere.

## Dependencies And Integration Points

It depends on DRM bridge/dw_hdmi, component framework, OF graph, clocks/resets/regulator, `sun8i_hdmi_phy_*()` functions, and optional `sun8i_tcon_top` routing. It integrates with TCON channel 1 through possible CRTC masks and TCON TOP for R40/H6-like paths.

## Risks And Test Signals

Risks include CRTC discovery through TCON TOP, lifetime coupling between controller and PHY drivers, missing cleanup if `drm_simple_encoder_init()` return is ignored, mode clock caps differing by SoC, and regulator/reset ordering. Test A83T 297 MHz cap, H6 594 MHz cap and DRM infoframes, TCON TOP paths, probe deferral on PHY/CRTC, hotplug/modeset, and unbind failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun8i_dw_hdmi.c -->
