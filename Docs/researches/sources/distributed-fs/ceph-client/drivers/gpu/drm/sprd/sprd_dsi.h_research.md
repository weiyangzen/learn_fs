# sources/distributed-fs/ceph-client/drivers/gpu/drm/sprd/sprd_dsi.h

Purpose: shared DSI/DPHY type and helper declarations for the SPRD DRM DSI host and PLL implementation.

Important APIs and types: defines work mode, video burst mode, color coding, and PLL timing enums. `struct dphy_pll` stores calculated PLL configuration and frequency fields. `struct dsi_context` stores MMIO/regmap, PLL, videomode, mode flags, timing values, masks, and ACK options. `struct sprd_dsi` embeds the MIPI host, slave device pointer, DRM encoder, panel bridge, and context. Public functions are `dphy_pll_config()` and `dphy_timing_config()`.

Control flow: `sprd_dsi.c` owns runtime host/encoder operations; `megacores_pll.c` consumes `dsi_context` and `dphy_pll` to program PHY registers.

State and persistence: defines the persistent DSI state layout used across component bind, panel attach, encoder enable/disable, and host transfers.

Dependencies and integration: includes OF/device/regmap/videomode plus DRM bridge, connector, encoder, MIPI DSI, panel, and print APIs.

Risks: `encoder_to_dsi()` assumes the DRM encoder is embedded in `struct sprd_dsi`. Public enums contain spelling `COLOR_CODE_COMPRESSTION`, so external changes must preserve compatibility or update all references.

Test signals: compile integration between DSI and PLL files, and runtime checks that panel attach fills `slave` before enable.
