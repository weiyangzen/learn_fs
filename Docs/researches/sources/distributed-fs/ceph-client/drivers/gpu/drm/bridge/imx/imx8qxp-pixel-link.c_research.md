# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-link.c

### Purpose
`imx8qxp-pixel-link.c` implements the i.MX8QM/QXP display pixel-link bridge. It does not program local MMIO; instead it uses the i.MX SCU firmware MISC service to select a master address, enable master-valid signals, and enable stream synchronization for a display controller stream.

### Important APIs, Types, And Functions
`struct imx8qxp_pixel_link` stores the DRM bridge, SCU IPC handle, display controller ID, stream ID, sink resource, selected master address, and the SCU control IDs for address, enable, valid, and sync. SCU access is wrapped by `imx8qxp_pixel_link_enable_mst_en()`, `imx8qxp_pixel_link_enable_mst_vld()`, `imx8qxp_pixel_link_enable_sync()`, matching disable functions, and `imx8qxp_pixel_link_set_mst_addr()`. Bridge callbacks include attach, mode_set, atomic enable/disable, and bus-format callbacks. `imx8qxp_pixel_link_find_next_bridge()` selects an output port and downstream bridge.

### Control Flow
Probe allocates the bridge, gets the SCU IPC handle, reads `fsl,dc-id` and `fsl,dc-stream-id`, maps the display controller to `IMX_SC_R_DC_0` or `IMX_SC_R_DC_1`, assigns the stream-specific control IDs, disables all firmware controls to reset default state, finds a downstream bridge, stores driver data, and registers the bridge. Downstream selection scans output ports 1 through 4, chooses the first available port, then scans up to two endpoints. It initially selects the first available bridge but replaces it with one whose remote node has `fsl,companion-pxl2dpi`, making companion PXL2DPI preferred. Mode set writes the master address, atomic enable sets `mst_en`, `mst_vld`, and `sync`, and atomic disable clears them.

### State, Persistence, And Dependencies
The only local state is the selected bridge, stream parameters, and SCU control IDs. Persistent hardware/firmware state lives in SCU-managed display controller controls, not local registers. Dependencies include the i.MX SCU firmware API, `dt-bindings/firmware/imx/rsrc.h`, DRM bridge helpers, media-bus formats, and OF graph endpoints.

### Integration Points
This driver is a bridge-chain element between an i.MX display controller output and downstream pixel-combiner or PXL2DPI bridges. It passes RGB888/RGB666 36-bit bus formats unchanged from input to output. Firmware resource selection makes it SoC-control-plane sensitive: the bridge only works when SCU permissions and resource IDs match the display controller described in DT.

### Risks
The driver logs SCU control failures but many enable/disable helpers are void, so atomic enable can appear successful even when firmware programming failed. `find_next_bridge()` sets `mst_addr` from the chosen port ID, so DT port numbering is part of the ABI. It returns `-EPROBE_DEFER` if a selected remote bridge is unavailable and can replace an already referenced bridge with a companion, making reference management important. There is no runtime PM, so firmware state is only reset at probe and through bridge disable.

### Test Signals
Test DC0/DC1 and stream0/stream1 control mappings, SCU IPC deferral, unavailable output ports, companion PXL2DPI preference, failed SCU set_control responses, bus-format negotiation identity behavior, attach flag enforcement, and enable/disable sequencing with firmware traces showing address before valid/sync enable.
