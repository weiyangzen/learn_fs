# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw_hdmi-rockchip.c

## Purpose
Implements Rockchip-specific glue for the Synopsys DW HDMI bridge on RK3228, RK3288, RK3328, RK3368, RK3399, and RK3568.

## Important APIs, Types, And Functions
Uses `rockchip_hdmi_chip_data` and `rockchip_hdmi`. Important callbacks include DT parsing, mode validation, encoder mode-set/enable/atomic-check, generic PHY init/disable, RK3228/RK3328 HPD setup/read, component bind/unbind, and resume.

## Control Flow
Bind copies SoC platform data, sets Rockchip private data into DW HDMI platform data, finds possible CRTCs, parses GRF/clocks/regulators, gets optional HDMI PHY and PHY clock, applies RK3568 SDA/SCL masks, initializes encoder, and calls `dw_hdmi_bind()`. Encoder mode_set programs the reference clock to adjusted pixel clock. Encoder enable writes GRF LCDC/VOP mux for SoCs that need it. Mode validation checks max TMDS clock and whether ref/PHY clocks can round within 0.1%.

## State And Persistence
Stores GRF regmap, encoder, chip/platform data, ref/grf/hdmiphy clocks, optional PHY, and DW HDMI handle. GRF HPD voltage/mux and VOP mux writes persist in hardware.

## Dependencies And Integration Points
Depends on DW HDMI bridge APIs, DRM OF graph, syscon GRF, clock/regulator/PHY frameworks, Rockchip CRTC state, and HDMI infoframe support through DW HDMI platform data.

## Risks
Clock round-rate validation can reject modes on clock tree limitations. Some SoCs have special HPD voltage handling. Optional external PHY paths must balance `phy_power_on/off`. Bind manually cleans the encoder if `dw_hdmi_bind()` fails.

## Test Signals
Probe and modeset on every compatible, HPD voltage behavior on RK3228/RK3328, max TMDS enforcement, 594 MHz modes where supported, GRF VOP selection on RK3288/RK3399, regulator failures, and suspend/resume.
