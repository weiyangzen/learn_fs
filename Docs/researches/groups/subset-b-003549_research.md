# subset-b-003549 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-ldb.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-ldb.c

### Purpose
`imx8qxp-ldb.c` implements the DRM bridge for the i.MX8QXP LVDS Display Bridge and pixel mapper. It adapts a display controller pixel-link input into one active LVDS channel, supports SPWG/JEIDA output formats, and coordinates optional dual-link LVDS operation through a companion LDB bridge.

### Important APIs, Types, And Functions
The main state is split between `struct imx8qxp_ldb`, which owns the common `struct ldb`, clocks, active channel index, and optional companion bridge, and `struct imx8qxp_ldb_channel`, which extends `struct ldb_channel` with an LVDS PHY and display-interface ID. Important bridge callbacks are `imx8qxp_ldb_bridge_atomic_check()`, `imx8qxp_ldb_bridge_mode_set()`, `imx8qxp_ldb_bridge_atomic_pre_enable()`, `imx8qxp_ldb_bridge_atomic_enable()`, `imx8qxp_ldb_bridge_atomic_disable()`, bus-format callbacks, and `imx8qxp_ldb_bridge_mode_valid()`. Probe-time helpers include `imx8qxp_ldb_set_di_id()`, `imx8qxp_ldb_parse_dt_companion()`, and `imx8qxp_ldb_check_chno_and_dual_link()`.

### Control Flow
Probe allocates two channel bridge objects, fetches `pixel` and `bypass` clocks, initializes the shared LDB helper, requires exactly one available local channel, obtains that channel's `lvds_phy`, finds the next bridge, derives the DI ID from the upstream endpoint, parses a companion LDB if dual-link is described in devicetree, enables runtime PM, and registers the bridge. Atomic check delegates format/link validation to `ldb_bridge_atomic_check_helper()`, derives an LVDS PHY configuration from adjusted pixel clock and split-link state, validates it, and optionally calls the companion bridge check. Mode set gets runtime PM, initializes and configures the PHY, mirrors bus formats into the companion channel for split mode, sets both LDB clocks to the adjusted pixel clock, writes channel selection and VSYNC polarity into `ldb_ctrl`, lets the generic helper program format bits, updates HSYNC/VSYNC polarity in `SS_CTRL`, and propagates mode set to the companion. Pre-enable enables clocks, enable writes channel mode bits and powers the PHY, and disable powers the PHY off, exits it, disables clocks, propagates disable, and drops runtime PM.

### State, Persistence, And Dependencies
Persistent driver state is in devm-managed bridge/channel objects plus `ldb->ldb_ctrl`, the active channel number, DI ID, PHY pointer, and optional companion reference. Hardware state persists in the syscon-backed LDB control register, `SS_CTRL`, clock rates, and PHY programming until runtime resume or disable resets it. Dependencies include `imx-ldb-helper.h`, DRM bridge atomic helpers, DRM OF LVDS dual-link helpers, Linux PHY LVDS options, regmap, runtime PM, and devicetree graph endpoints.

### Integration Points
The driver integrates into a larger i.MX display pipeline through DRM bridge chaining and media-bus format negotiation. It consumes the upstream DI selected from port 0, drives a downstream panel or bridge found by the LDB helper, and can coordinate a second LDB via `fsl,companion-ldb` for odd/even dual-link LVDS. Runtime PM resume resets the LDB control register to power-on defaults before normal mode programming.

### Risks
Probe intentionally rejects more than one locally available channel, so DTs exposing both channels on one instance will fail. Companion handling calls bridge function pointers directly and assumes the companion bridge is an LDB-compatible object. `pm_runtime_get_sync()` errors are logged but mode programming continues, which can lead to register or PHY operations while power state is uncertain. Split-link correctness depends on channel number matching the odd/even pixel order. Clock and PHY configuration errors are mostly logged after mode_set starts rather than converted into atomic failures.

### Test Signals
Useful signals are DT probe with single-link channel 0 and channel 1, dual-link odd/even and even/odd companion layouts, invalid companion compatible strings, deferred companion bridge probe, mode validation around 150 MHz single-link and 170 MHz split-link limits, SPWG/JEIDA/RGB666 bus-format negotiation, PHY validate/configure failures, runtime suspend/resume register reset, and hot disable/enable cycles that verify clock and PHY balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-combiner.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-combiner.c

### Purpose
`imx8qxp-pixel-combiner.c` implements the i.MX8QM/QXP pixel combiner DRM bridge. In the current driver it primarily operates each channel in bypass mode, converting a 30-bit internal RGB bus into the 36-bit pixel-link bus and programming signal polarity, reset, and basic RGB data-format controls.

### Important APIs, Types, And Functions
`struct imx8qxp_pc` owns the MMIO base, APB clock, runtime PM device, and up to two `struct imx8qxp_pc_channel` bridges. Channel state stores the stream ID and back-pointer. Register helpers `imx8qxp_pc_read()`, `imx8qxp_pc_write()`, `imx8qxp_pc_write_set()`, and `imx8qxp_pc_write_clr()` use the hardware's set/clear windows. Main bridge callbacks are `imx8qxp_pc_bridge_attach()`, `imx8qxp_pc_bridge_mode_set()`, `imx8qxp_pc_bridge_atomic_disable()`, `imx8qxp_pc_bridge_mode_valid()`, and bus-format callbacks. Runtime PM callbacks reset or release the combiner via `PC_SW_RESET_REG`.

### Control Flow
Probe maps registers, gets the `apb` clock, enables runtime PM, and iterates available child channel nodes. For each channel, it validates `reg` as 0 or 1, allocates a bridge, finds the port 1 remote bridge, stores `stream_id`, and registers the bridge. Attach requires `DRM_BRIDGE_ATTACH_NO_CONNECTOR` and attaches the downstream bridge. Mode set gets runtime PM, temporarily enables the APB clock, programs HSYNC and VSYNC as active-low toward the pixel link, data-valid as active-high, enables first-frame VSYNC masking, selects RGB for the channel's pixel data format, sets bypass mode, and disables the APB clock. Atomic disable only drops runtime PM; runtime suspend performs full reset and runtime resume releases full reset.

### State, Persistence, And Dependencies
Driver state is devm-managed and per-channel. Hardware state is in the combiner MMIO registers and is lost or explicitly reset across runtime suspend. `mode_set()` takes a runtime PM reference that is later released by `atomic_disable()`, so bridge lifecycle and runtime PM are coupled. Dependencies include DRM bridge helpers, OF graph remote bridge lookup, media-bus format constants, APB clock control, runtime PM, and direct MMIO access.

### Integration Points
This bridge sits between the upstream display stream and downstream pixel-link bridge or other i.MX display bridge. It participates in DRM bus-format negotiation by accepting RGB888/RGB666 30-bit input formats and advertising 36-bit CPADLO output formats. It supports two independent channel nodes in devicetree, each with its own downstream bridge.

### Risks
The implementation only supports bypass and RGB, despite register definitions for combine and YUV modes. Runtime PM errors in mode_set are logged but do not stop register programming. Probe error cleanup removes channel 0 only for a narrow `i == 1` case and does not put a downstream bridge reference when later errors occur for the same channel. A failed APB clock enable is logged but writes still proceed. The maximum hdisplay check is a simple 2560 limit and does not validate total bandwidth or multi-stream combine modes.

### Test Signals
Test channel 0 and channel 1 DT probes, downstream bridge deferral, attach without `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, bus-format propagation for RGB888 and RGB666, hdisplay greater than 2560 rejection, runtime suspend/resume reset bits, repeated enable/disable PM balance, and register traces showing bypass, polarity, and first-frame mask programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-combiner.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-link.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-link.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pixel-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pxl2dpi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pxl2dpi.c

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qxp-pxl2dpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx93-mipi-dsi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx93-mipi-dsi.c

### Purpose
`imx93-mipi-dsi.c` provides the i.MX93 platform glue for the Synopsys DesignWare MIPI DSI host. It supplies mode validation, pixel-clock fixup, input bus-format selection, MIPI D-PHY PLL programming, D-PHY timing tables, and display-mux RGB mapping for the SoC media block.

### Important APIs, Types, And Functions
`struct imx93_dsi` owns clocks, media block regmap, DesignWare handle, platform data, cached D-PHY configuration, reference clock rate, and attached DSI pixel format. PLL support is organized around `struct dphy_pll_cfg`, `struct dphy_pll_vco_prop`, and `struct dphy_pll_hsfreqrange`. Key helpers are `dphy_pll_get_configure_from_opts()`, `dphy_pll_configure()`, `dphy_pll_init()`, `dphy_pll_power_off()`, `imx93_dsi_get_phy_configure_opts()`, `imx93_dsi_validate_mode()`, `imx93_dsi_validate_phy()`, `imx93_dsi_mode_valid()`, `imx93_dsi_mode_fixup()`, `imx93_dsi_phy_init()`, `imx93_dsi_get_lane_mbps()`, `imx93_dsi_phy_get_timing()`, and `imx93_dsi_host_attach()`.

### Control Flow
Probe obtains the media block regmap, `pix`, `phy_cfg`, and `phy_ref` clocks, validates that the D-PHY reference clock is between 2 MHz and 64 MHz, fills `dw_mipi_dsi_plat_data`, and calls `dw_mipi_dsi_probe()`. During mode validation, the driver first checks whether the pixel clock can be rounded within 0.5 percent when the last bridge offers detect and EDID, then computes default MIPI D-PHY options and verifies that a PLL M/N solution exists for the required lane rate. Mode fixup rounds the pixel clock and updates the adjusted mode. Lane-rate calculation stores `phy_cfg` for later PHY init. PHY init programs the `DISPLAY_MUX` RGB mapping based on the attached MIPI DSI format, initializes the PLL clock domain, writes PLL control registers from the calculated config and tables, enables the reference clock, and pulses `UPDATE_PLL`. Power-off clears PLL registers and disables ref/config clocks.

### State, Persistence, And Dependencies
State persists in the cached DSI format from host attach and the cached `union phy_configure_opts` from lane-rate calculation. Hardware state lives in media block mux and D-PHY PLL registers and the pixel/ref/config clocks. Dependencies include the DesignWare MIPI DSI bridge library, Linux MIPI D-PHY helpers, clk APIs, regmap syscon access, DRM mode helpers, and fixed databook-derived PLL and high-speed timing tables.

### Integration Points
The file is a platform adapter for `dw_mipi_dsi`: all bridge and host operation is mediated through DesignWare callbacks in `dw_mipi_dsi_plat_data`. It exposes max four data lanes, converts DRM media-bus formats to LCDIF input expectations, and validates modes against both display clock rounding and D-PHY PLL capability. It integrates with downstream panels through normal MIPI DSI device attach.

### Risks
`dsi->phy_cfg` is populated in `get_lane_mbps()`, so PHY init assumes the DesignWare core called that path for the active mode. PLL search uses integer rounding and picks the smallest frequency delta, making boundary rates important. Some `regmap_update_bits()` calls in mux setup ignore return values. `imx93_dsi_validate_mode()` assumes `drm_bridge_chain_get_last_bridge()` succeeds before checking ops. Clock enable failure in `dphy_pll_configure()` must be balanced carefully because ref clock is disabled only on later update failure or power-off. Unsupported DSI pixel formats leave mux `fmt` at zero.

### Test Signals
Useful tests are probe with invalid ref clock rates, mode validation at 80 Mbps and 2500 Mbps lane-rate edges, pixel-clock rounding outside +/-0.5 percent, RGB888/RGB666/RGB666_PACKED/RGB565 mux writes, D-PHY timing table boundaries, PLL M/N solution search with awkward reference clocks, DesignWare attach format propagation, and suspend/remove paths ensuring clocks are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx93-mipi-dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/inno-hdmi.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/inno-hdmi.c

### Purpose
`inno-hdmi.c` is a reusable DRM bridge library for Innosilicon HDMI transmitters. It initializes the HDMI block, manages PHY power and platform-specific PHY tables, exposes HDMI bridge operations including HPD, EDID, infoframes, and mode validation, and implements a small DDC I2C adapter backed by the controller's EDID FIFO.

### Important APIs, Types, And Functions
`struct inno_hdmi` stores the bridge, pclk/refclk, MMIO registers, optional GRF regmap, DDC adapter, I2C state, and platform data. `struct inno_hdmi_i2c` tracks DDC offsets, segment pointer, mutex, and EDID completion. The exported entry point is `inno_hdmi_bind()`. Important helpers include `inno_hdmi_find_phy_config()`, `inno_hdmi_i2c_init()`, `inno_hdmi_init_hw()`, `inno_hdmi_standby()`, `inno_hdmi_power_up()`, `inno_hdmi_setup()`, `inno_hdmi_config_video_timing()`, `inno_hdmi_config_video_csc()`, bridge EDID/detect/infoframe callbacks, IRQ handlers, and the `inno_hdmi_i2c_xfer()` adapter implementation.

### Control Flow
`inno_hdmi_bind()` validates platform PHY data, allocates the bridge object, maps registers, enables `pclk` and optional `ref`, initializes hardware, requests a threaded IRQ, configures bridge identity and operations, creates the DDC adapter, registers the bridge, and attaches it to the encoder. Hardware init releases digital and analog resets, selects clock/power defaults, enters standby, configures DDC based on refclk or pclk, and unmasks HPD. Atomic enable calls `inno_hdmi_setup()`, which mutes audio/video, sets HDMI or DVI mode from sink display info, writes external timing registers, configures CSC/output range using connector HDMI state, updates infoframes through DRM helpers, recalculates DDC timing from the TMDS character rate, unmutes, and powers the PHY up. Atomic disable enters standby. Hard IRQ handles EDID-ready completion and HPD status; the threaded IRQ emits a DRM HPD event.

### State, Persistence, And Dependencies
Software state is the bridge object, DDC adapter state, clock handles, and platform PHY configuration. Hardware state persists in controller registers for resets, video timing, CSC coefficients, packet buffers, PHY driver/pre-emphasis/power, DDC timing, and interrupt masks. Dependencies include DRM HDMI state helpers, DRM bridge helpers, DRM EDID/DDC, platform-specific `inno_hdmi_plat_data`, MMIO register access, Linux I2C adapter APIs, IRQ handling, and clk APIs.

### Integration Points
This file is not a standalone platform driver; SoC-specific drivers bind it by calling `inno_hdmi_bind()` with an encoder and platform PHY configuration. It exposes a connector type of HDMI-A, bridge HDMI operations for AVI infoframes, HPD detect, EDID read through its DDC adapter, and mode validation based on minimum TMDS rate, PHY table maximum, and optional refclk rounding tolerance.

### Risks
The DDC engine only supports EDID-style reads; arbitrary I2C messages are rejected or interpreted as EDID offset/segment writes. HDMI Vendor Specific InfoFrame operations warn once but do not implement VSI transmission. CSC programming only handles selected RGB and YCbCr444 paths. Mode setup assumes connector and CRTC state are available from the atomic state. PHY fallback uses a default config when no table entry matches during power-up, while mode_valid would reject the same clock earlier. DDC read waits only `HZ / 10`, so slow EDID transactions can fail with `-EAGAIN`.

### Test Signals
Test bridge bind with missing PHY tables, pclk/refclk failures, HPD high/low IRQs, EDID reads across block 0 and extension segments, DDC timeout and invalid write messages, min/max TMDS mode validation, refclk tolerance rejection, RGB full/limited CSC paths, AVI infoframe writes, standby/power-up register sequencing, and SoC platform `enable()` callbacks during timing setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/inno-hdmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6263.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6263.c

### Purpose
`ite-it6263.c` implements a DRM bridge for the ITE IT6263 LVDS-to-HDMI transmitter. It receives single- or dual-link LVDS input, configures LVDS input mapping and AFE settings, drives HDMI output, performs custom EDID reads over the chip DDC engine, and exposes HDMI bridge operations and infoframe programming.

### Important APIs, Types, And Functions
`struct it6263` stores HDMI and LVDS I2C clients/regmaps, the DRM bridge, downstream bridge, LVDS data mapping, dual-link state, and link swap state. Regmap callbacks define readable, writable, volatile, and banked HDMI register ranges plus a separate LVDS regmap. Important helpers are `it6263_parse_dt()`, `it6263_hw_reset()`, `it6263_lvds_set_i2c_addr()`, `it6263_lvds_config()`, `it6263_hdmi_config()`, `it6263_detect()`, `it6263_read_edid()`, bridge enable/disable, mode validation, input bus-format selection, TMDS validation, and HDMI infoframe callbacks.

### Control Flow
Probe allocates the bridge, creates the HDMI regmap on the primary I2C client, gets reset GPIO and required regulators, parses DT for LVDS data mapping, downstream bridge, and dual-link port order, performs hardware reset, programs the LVDS subaddress through HDMI registers, creates a dummy LVDS I2C client/regmap, initializes LVDS and HDMI blocks, and registers the bridge. Attach first attaches the downstream bridge with no connector; if the caller did not request no-connector, it creates a bridge connector and attaches it to the encoder. Atomic enable switches HDMI mode on, updates HDMI infoframes, configures HDMI AFE according to the adjusted pixel clock, pulses video reset, polls for stable input video with LVDS reconfiguration retries, releases AFE reset/power-down, clears AVMUTE, and enables repeated packets. Atomic disable mutes and powers down AFE.

### State, Persistence, And Dependencies
Software state is retained in the regmaps, bridge, downstream reference, LVDS mapping flags, and regulator/reset-managed resources. Hardware state persists in HDMI and LVDS register banks, including LVDS color depth/mapping/dual-link mode, HDMI reset, input RGB mode, GCP color depth, AFE controls, DDC state, and packet registers. Dependencies include DRM bridge connector helpers, DRM HDMI state helpers, DRM OF LVDS helpers, regmap bank selection, I2C dummy devices, GPIO reset, regulator bulk enable, and media-bus formats.

### Integration Points
The bridge consumes LVDS input formats `MEDIA_BUS_FMT_RGB888_1X7X4_JEIDA` or `MEDIA_BUS_FMT_RGB888_1X7X4_SPWG`, advertises HDMI-A output, supports HPD detect by polling `HPDETECT`, reads EDID with `drm_edid_read_custom()`, and forwards to a downstream bridge from DT port 2. It participates in HDMI atomic state through TMDS character-rate validation and AVI/HDMI infoframe callbacks.

### Risks
The chip lacks HPD interrupts, so detection is poll-driven. EDID reads depend on DDC polling and FIFO chunking; timeout or DDC error handling must be robust. `it6263_parse_dt()` rejects single-input port1 layouts and requires a valid `data-mapping`. Dual-link ordering affects `REG_LVDS_IN_SWAP`, so incorrect DT silently swaps pixels. Atomic enable tolerates unstable video after three retries with only a warning. Infoframe bulk writes assume the DRM helper-provided buffer is long enough for the chip register layout.

### Test Signals
Test single-link port0, dual-link odd/even and even/odd DTs, missing or invalid `data-mapping`, all required regulator failures, reset GPIO timing, LVDS dummy I2C creation, EDID reads including extension blocks and DDC error bits, TMDS rejection above 225 MHz and pixel clocks above 150 MHz, pclk-high AFE threshold at 80 MHz, bridge connector creation, and AVI/HDMI infoframe register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6263.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6505.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6505.c

### Purpose
`ite-it6505.c` implements a DRM bridge for the ITE IT6505 DisplayPort transmitter. It accepts DPI video input and drives a DisplayPort link, handling regulator/GPIO power sequencing, AUX transfers, EDID reads, DPCD capability parsing, link training, HPD/extcon events, HDCP 1.x authentication support, HDMI-codec audio programming, runtime PM, and debugfs controls.

### Important APIs, Types, And Functions
`struct it6505` is the central state object: DRM DP AUX, DRM bridge, regmap, regulators/reset GPIO, extcon state, connector status, link state, work items, DPCD cache, lane/rate/SSC/enhanced-frame choices, HDCP state, audio settings, cached EDID, debugfs root, and IRQ. Important clusters include low-level I/O wrappers `it6505_read()`, `it6505_write()`, `it6505_set_bits()`; AUX paths `it6505_aux_transfer()`, `it6505_aux_operation()`, and `it6505_aux_i2c_operation()`; link helpers `it6505_parse_link_capabilities()`, `it6505_link_training_setup()`, `it6505_link_start_auto_train()`, `it6505_link_start_step_train()`; HPD/IRQ handlers; bridge callbacks; runtime PM power on/off; audio helpers; and HDCP work functions.

### Control Flow
Probe allocates the bridge, initializes locks, requires an extcon provider, creates a banked I2C regmap, gets regulators and reset GPIO, parses DT lane-swap, AFE, lane-count, and max pixel-clock properties, requests a low-triggered threaded IRQ with `IRQF_NO_AUTOEN`, initializes work items and completions, creates debugfs, enables runtime PM, initializes the DP AUX object, and registers the bridge. Power-on enables regulators in order, toggles reset, marks the chip powered, resets logic, enables interrupts, programs defaults, turns lanes off, and enables IRQ. Extcon work powers the chip on/off based on `EXTCON_DISP_DP`. HPD interrupt reads DPCD on first connect, parses link capabilities, powers up the DP link, reads sink count, powers/terminates lanes, and resets video if needed; disconnect clears DPCD/EDID, stops HDCP/link training/audio/video, and powers lanes down. Atomic pre-enable gets runtime PM, atomic enable builds and sends AVI infoframe, updates phase/video reset state, enables interrupts, resets video, and powers up DP link. Video stable interrupts schedule link training; training tries hardware auto-train with retries, then software clock-recovery/channel-equalization training if supported.

### State, Persistence, And Dependencies
All register access is gated by `it6505->powered`; the driver uses `extcon_lock`, `mode_lock`, and `aux_lock` for concurrent extcon, detect, IRQ, and AUX paths. Persistent driver state includes cached DPCD, cached EDID, current link parameters, HDCP status and KSV/SHA1 buffers, audio format, extcon state, and debugfs hold/power knobs. Hardware state persists in IT6505 registers, DP sink DPCD, AUX state, link lanes, audio/video mute state, and HDCP engine state. Dependencies include DRM DP helpers, DRM EDID custom reading, DRM bridge HPD/detect/EDID ops, runtime PM, extcon, regmap, regulators, GPIO, threaded IRQs, workqueues, debugfs, SHA1, and `sound/hdmi-codec.h`.

### Integration Points
The driver exposes a DisplayPort connector bridge with detect, EDID, and HPD operations and registers a DP AUX channel on bridge attach. It relies on an extcon device for cable/orientation events and optional Type-C lane polarity, reports plug state to an HDMI codec callback, and obtains link limits from DT endpoint properties. It reads EDID over AUX I2C, reads/writes DPCD for link training and power management, and uses workqueues to decouple HPD, link training, HDCP, and extcon events from IRQ context.

### Risks
The driver is concurrency-heavy: extcon power transitions, bridge atomic callbacks, detect, AUX transfers, and IRQ work all interact with `powered` and cached DPCD/EDID. `it6505_read()` returns `-ENODEV` when unpowered, so any path that forgets runtime PM can fail indirectly. The DT parsing currently calls `of_node_put(ep)` before checking and using `ep`, which is a suspicious lifetime pattern. AUX native write verifies by reading back reversed data, so size and byte-order assumptions matter. HDCP repeater validation and SHA1 buffers are fixed-size and need strict downstream-count checks. Debugfs `force_power_on_off` can bypass normal extcon/runtime PM expectations. Link training fallback and retry state can be sensitive to branch devices with zero sink count.

### Test Signals
High-value tests include probe deferral for extcon/regulators/reset/IRQ, runtime PM power-on/off ordering, extcon connect/disconnect, Type-C lane swap property changes, bridge attach registering AUX, EDID cache fill/invalidations, AUX native/I2C read/write/defer/nack/timeout paths, DPCD parsing for lane count/rate/SSC/enhanced frame/HDCP, auto-training success/failure and step-training fallback, video FIFO reset IRQ paths, HPD IRQ branch sink-count changes, audio parameter validation and FIFO-error recovery, HDCP receiver and repeater flows, debugfs power/hold behavior, and suspend/resume while extcon work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6505.c -->
