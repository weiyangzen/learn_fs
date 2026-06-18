# sources/distributed-fs/ceph-client/drivers/gpu/drm/rockchip/dw-mipi-dsi2-rockchip.c

## Purpose
Implements Rockchip glue for the newer DesignWare MIPI DSI2 host, targeting RK3576 and RK3588 DSI2/DCPHY style controllers.

## Important APIs, Types, And Functions
Defines GRF field metadata through `struct dsigrf_reg` and `enum grf_reg_fields`, SoC data in `rockchip_dw_dsi2_chip_data`, and runtime state in `dw_mipi_dsi2_rockchip`. Major callbacks are DSI2 PHY ops, encoder atomic enable/check, host attach/detach, component bind/unbind, and probe/remove.

## Control Flow
Probe maps the host register block into a regmap, chooses chip data by MMIO base, obtains GRF and optional DCPHY, fills `dw_mipi_dsi2_plat_data`, and probes the DW DSI2 core. Host attach registers the component. Bind creates the DRM encoder, records endpoint ID, and binds the DSI2 core. Lane Mbps is calculated from pixel clock, bpp, lanes, and optional burst overhead, then converted into external PHY options. Atomic enable writes IPI color depth to GRF; atomic check fills Rockchip CRTC output mode, bus format, flags, and color space.

## State And Persistence
Stores selected format, lane Mbps, external PHY options, GRF data, and DW DSI2 core handle. GRF field writes persist IPI color-depth state for the hardware.

## Dependencies And Integration Points
Depends on `drm/bridge/dw_mipi_dsi2`, generic PHY MIPI DPHY config, syscon GRF, DRM OF helpers, media bus formats, and Rockchip CRTC state.

## Risks
`grf_field_write()` assumes the chip data has a valid `grf_regs` array for every enum field. Lane-rate units must stay consistent with the SoC max-bit-rate values. Only DPHY is exposed; CPHY/other DCPHY modes are not handled here.

## Test Signals
RK3576 and RK3588 probe by base address, external DCPHY configure/power, burst and non-burst lane-rate checks, RGB565/666/888 formats, and GRF color-depth programming during atomic enable.
