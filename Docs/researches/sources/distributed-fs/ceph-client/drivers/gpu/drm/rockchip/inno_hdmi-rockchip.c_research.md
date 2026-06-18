# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/inno_hdmi-rockchip.c

## Purpose
Adds Rockchip platform glue for Innosilicon HDMI controllers on RK3036 and RK3128.

## Important APIs, Types, And Functions
Defines RK3036/RK3128 PHY config tables, `rockchip_inno_hdmi`, `inno_hdmi_rk3036_enable()`, encoder atomic check, component bind/probe/remove, and SoC-specific `inno_hdmi_plat_data`.

## Control Flow
Probe registers a component. Bind allocates state, fetches SoC platform data, optionally obtains GRF for RK3036 sync polarity programming, creates a TMDS encoder, adds helper funcs, delegates controller setup to `inno_hdmi_bind()`, then creates and attaches a bridge connector. RK3036 enable writes HSYNC/VSYNC polarity into GRF based on the display mode.

## State And Persistence
Keeps the Inno HDMI core pointer, device, GRF regmap, and embedded encoder. GRF polarity writes persist in SoC registers.

## Dependencies And Integration Points
Depends on `drm/bridge/inno_hdmi`, DRM bridge connector, DRM OF graph helpers, syscon GRF, and Rockchip CRTC state.

## Risks
Only RK3036 uses GRF polarity enable ops; RK3128 relies entirely on the bridge core and PHY config table. The local `inno_hdmi_connector_state` is defined but unused, which may indicate historical leftovers.

## Test Signals
Probe on RK3036/RK3128, bridge connector creation, CRTC defer when possible CRTCs are absent, RK3036 sync polarity changes, and HDMI mode output as P888.
