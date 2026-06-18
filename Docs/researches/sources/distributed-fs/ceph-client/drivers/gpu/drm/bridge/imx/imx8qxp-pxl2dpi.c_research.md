# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pxl2dpi.c

### Purpose
`imx8qxp-pxl2dpi.c` implements an i.MX8QXP pixel-link-to-DPI DRM bridge. It selects which pixel-link stream feeds the block through SCU firmware, converts the 36-bit internal pixel-link bus to 24-bit DPI RGB output, and coordinates optional companion PXL2DPI instances for dual-link LVDS pipelines.

### Important APIs, Types, And Functions
`struct imx8qxp_pxl2dpi` stores the syscon regmap, bridge, optional companion bridge, SCU IPC handle/resource, negotiated input and output bus formats, and pixel-link selector value. Bridge callbacks are `imx8qxp_pxl2dpi_bridge_attach()`, `imx8qxp_pxl2dpi_bridge_destroy()`, `imx8qxp_pxl2dpi_bridge_atomic_check()`, `imx8qxp_pxl2dpi_bridge_mode_set()`, `imx8qxp_pxl2dpi_bridge_atomic_disable()`, and bus-format callbacks. Probe helpers `imx8qxp_pxl2dpi_find_next_bridge()`, `imx8qxp_pxl2dpi_set_pixel_link_sel()`, and `imx8qxp_pxl2dpi_parse_dt_companion()` interpret the graph and companion relationship.

### Control Flow
Probe allocates the bridge, gets the parent syscon regmap, obtains the SCU IPC handle, reads `fsl,sc-resource`, finds exactly one available output endpoint from port 1 and its downstream bridge, reads the available port 0 endpoint ID as `pl_sel`, optionally resolves a `fsl,companion-pxl2dpi`, enables runtime PM, and registers the bridge. Atomic check caches the negotiated input and output formats in the device. Mode set gets runtime PM, writes `IMX_SC_C_PXL_LINK_SEL` with `pl_sel`, programs `PXL2DPI_CTRL` as 24-bit RGB or 18-bit padded RGB666 based on output format, mirrors the negotiated bus formats into the companion instance if present, and directly calls the companion's mode_set. Atomic disable drops runtime PM and disables the companion.

### State, Persistence, And Dependencies
Persistent software state includes cached bus formats, `pl_sel`, SCU resource ID, and companion bridge reference. Hardware state persists in the parent syscon `PXL2DPI_CTRL` register and SCU pixel-link selection control until disabled or overwritten. Dependencies include SCU MISC controls, syscon/regmap, DRM bridge atomic helpers, DRM OF LVDS dual-link helpers, media-bus formats, runtime PM, and OF graph endpoint parsing.

### Integration Points
The bridge links a pixel-link source to a downstream DPI consumer, commonly an LDB or panel bridge. It advertises RGB888 1x24 and RGB666 padded 1x24 output and maps them to RGB888/RGB666 36-bit CPADLO input. Dual-link support is discovered by comparing the port 1 nodes of this bridge's downstream bridge and the companion's downstream bridge with `drm_of_lvds_get_dual_link_pixel_order()`.

### Risks
Mode programming continues after a runtime PM get failure and after SCU set_control failures. The companion bridge is driven through direct function calls, so missing callbacks or incompatible bridge types would break assumptions. Probe requires exactly one available endpoint per relevant port. `parse_dt_companion()` only checks that a dual-link pixel order exists; it does not store the order locally. The `__free(device_node)` pattern plus manual node handling needs careful review when backporting to kernels without cleanup attributes.

### Test Signals
High-value tests include RGB888 and RGB666 bus-format negotiation, port 0 endpoint IDs mapping to SCU pixel-link selection values, missing or multiple endpoints, SCU resource errors, downstream bridge deferral, dual-link companion detection, incompatible companion compatible strings, runtime PM balance across companion mode_set/disable, and syscon writes to `PXL2DPI_CTRL`.
