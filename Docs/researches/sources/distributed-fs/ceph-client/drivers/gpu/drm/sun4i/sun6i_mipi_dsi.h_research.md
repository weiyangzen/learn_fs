<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h

## Purpose

`sun6i_mipi_dsi.h` defines the private state and variant contract for the Allwinner DSI host plus helper conversions used by the DSI implementation and TCON CPU-interface path.

## Important APIs, Types, And Definitions

`SUN6I_DSI_TCON_DIV` defines the fixed TCON-to-DSI divider used by TCON channel 0 programming. `struct sun6i_dsi_variant` records `has_mod_clk` and `set_mod_clk`. `struct sun6i_dsi` embeds DRM connector/encoder, `mipi_dsi_host`, clocks, regmap, regulator, reset, D-PHY, device/panel/DRM pointers, and variant. Inline helpers convert host, connector, and encoder back to `struct sun6i_dsi`.

## Control Flow

The header has only inline container conversions. Runtime behavior is in `sun6i_mipi_dsi.c`; TCON mode setting uses `encoder_to_sun6i_dsi()` to get attached DSI device parameters.

## State And Persistence Behavior

The struct persists for the platform device lifetime. `device` and `panel` are mutable attachment state, while `drm` is set during component bind and cleared at unbind. Clock/reset/regulator/phy pointers define power state resources.

## Dependencies And Integration Points

It depends on DRM connector/encoder and MIPI DSI host declarations. It is included by DSI implementation and TCON code that needs DSI lane/format details for channel 0 CPU trigger setup.

## Risks And Test Signals

Risks include stale attached-device pointers across detach/unbind and variant flags that must match clock names in DT. Build all DSI/TCON paths and test attach/defer/detach, TCON mode programming, and variant-specific clock setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/sun4i/sun6i_mipi_dsi.h -->
