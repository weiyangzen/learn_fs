# sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi2.h

Purpose: platform interface for a newer DesignWare MIPI DSI2 core, similar to the DSI glue API but using regmap and exposing DPHY/CPHY plus PPI-width PHY interface details.

Important APIs/types/functions: `enum dw_mipi_dsi2_phy_type`, `struct dw_mipi_dsi2_phy_iface`, `struct dw_mipi_dsi2_phy_timing`, `struct dw_mipi_dsi2_phy_ops`, `struct dw_mipi_dsi2_host_ops`, `struct dw_mipi_dsi2_plat_data`, `dw_mipi_dsi2_probe`, `dw_mipi_dsi2_remove`, `dw_mipi_dsi2_bind`, and `dw_mipi_dsi2_unbind`.

Control flow: glue drivers provide regmap, lane limits, mode validation/fixup, bus-format callback, PHY callbacks, host callbacks, and private data; the common driver queries PHY interface/timing/rates and binds the bridge to an encoder.

State and persistence: no local state; runtime state is in opaque `struct dw_mipi_dsi2`, regmap-backed registers, PHY power state, and MIPI host attachments.

Dependencies and integration points: regmap, DRM bridge/atomic/modes, MIPI DSI devices, platform devices, panels, and SoC DPHY/CPHY drivers.

Risks and test signals: risks include CPHY/DPHY lane semantic mixups, PPI width mismatch, regmap range errors, and host attach cleanup bugs. Test both PHY types, max lane boundaries, format negotiation, escape clock setup, and driver unload.
