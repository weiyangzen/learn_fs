# subset-b-005809 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi.h

## Purpose
`dw_hdmi.h` is the public platform interface for the Synopsys DesignWare HDMI bridge driver. It lets SoC glue drivers describe bus formats, PHY tables, vendor PHY callbacks, audio callbacks, CEC policy, and mode validation around the common DW-HDMI core.

## Important APIs, types, and functions
Key types are `enum dw_hdmi_phy_type`, `struct dw_hdmi_mpll_config`, `struct dw_hdmi_curr_ctrl`, `struct dw_hdmi_phy_config`, `struct dw_hdmi_phy_ops`, and `struct dw_hdmi_plat_data`. Entry points include `dw_hdmi_probe`, `dw_hdmi_bind`, `dw_hdmi_unbind`, `dw_hdmi_remove`, `dw_hdmi_resume`, HPD/rx-sense helpers, HDMI codec setters, audio enable/disable, PHY I2C/register helpers, `dw_hdmi_bus_fmt_is_420`, and `dw_hdmi_to_plat_data`.

## Control flow
Glue drivers populate `dw_hdmi_plat_data`, then either probe standalone or bind through component framework with a DRM encoder. The common driver calls optional `mode_valid`, audio, `configure_phy`, and `phy_ops` callbacks while attaching the DRM bridge/connector, programming modes, handling HPD, and configuring audio. PHY helpers expose low-level sequences for common Synopsys PHY generations.

## State and persistence
The header owns no storage. Runtime state lives in the opaque `struct dw_hdmi` and platform private data. Persistent behavior is limited to hardware register state programmed by the implementation; callbacks must treat `priv_data`, `phy_data`, and `priv_audio` lifetimes as external contracts.

## Dependencies and integration points
It depends on DRM display mode/info types, DRM encoders, platform devices, regmap, media bus formats referenced in documentation, and `sound/hdmi-codec.h`. Integration points are SoC-specific HDMI glue, DRM bridge chains, HDMI codec audio, CEC, HPD/rx-sense handling, and optional vendor PHY implementations.

## Risks and test signals
Risks include mismatched PHY tables by pixel clock and color depth, callback lifetime errors, wrong input bus encoding, YCbCr 4:2:0 policy mistakes, audio parameter desynchronization, and HPD/rx-sense races. Test signals include bind/unbind and resume paths, mode validation across RGB/YUV/bpc combinations, audio plug and sample-rate changes, CEC disable handling, vendor and Synopsys PHY variants, and HPD force/disable/rxsense transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi_qp.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi_qp.h

## Purpose
`dw_hdmi_qp.h` declares the platform interface for the newer DesignWare HDMI QP bridge core, used by SoC glue drivers to bind encoder, PHY, IRQ, clock, color format, and bpc constraints into the common HDMI implementation.

## Important APIs, types, and functions
Important types are `struct dw_hdmi_qp_phy_ops` and `struct dw_hdmi_qp_plat_data`. The platform data supplies PHY callbacks, PHY private data, main and CEC IRQs, reference clock rate, supported `drm_output_color_format` bitmask, and maximum bpc. Public calls are `dw_hdmi_qp_bind`, `dw_hdmi_qp_suspend`, and `dw_hdmi_qp_resume`.

## Control flow
Glue code calls `dw_hdmi_qp_bind` with a platform device, encoder, and platform data. The common bridge uses callbacks for PHY init/disable/HPD setup, consumes IRQ and clock parameters, then registers into the DRM bridge path. Suspend and resume are explicit helpers called by platform PM code.

## State and persistence
No state is stored in the header. Runtime state is opaque in `struct dw_hdmi_qp`; persistent effects are only hardware register/PHY state established by the implementation and restored through resume.

## Dependencies and integration points
It integrates with DRM encoders/connectors, platform devices, device PM, HDMI CEC IRQ handling, PHY glue, and color format negotiation. The `supported_formats` and `max_bpc` fields feed HDMI mode checks and output format selection.

## Risks and test signals
Risks include inconsistent supported format masks, underdeclared bpc limits, wrong IRQ assignment, reference clock mismatches, and PHY HPD setup ordering. Test signals include bind failure paths, suspend/resume with connected sinks, CEC interrupt routing, HPD read/setup behavior, and modes spanning 8/10/12 bpc and supported color formats.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_hdmi_qp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi.h

## Purpose
`dw_mipi_dsi.h` defines the glue-driver contract for the Synopsys DesignWare MIPI DSI host/bridge core. It abstracts PHY timing, lane-rate calculation, escape clock discovery, optional host attach hooks, and DRM bridge format negotiation.

## Important APIs, types, and functions
The central structures are `struct dw_mipi_dsi_dphy_timing`, `struct dw_mipi_dsi_phy_ops`, `struct dw_mipi_dsi_host_ops`, and `struct dw_mipi_dsi_plat_data`. Public functions are `dw_mipi_dsi_probe`, `dw_mipi_dsi_remove`, `dw_mipi_dsi_bind`, `dw_mipi_dsi_unbind`, `dw_mipi_dsi_set_slave`, and `dw_mipi_dsi_get_bridge`.

## Control flow
Platform code supplies register base, maximum lanes, optional `mode_valid` and `mode_fixup`, input bus format negotiation, PHY ops, host ops, and private data. The common DSI driver probes once, binds to a DRM encoder later, calls PHY callbacks around enable/disable, and uses host callbacks when MIPI DSI devices attach or detach. Dual-DSI configurations can set a slave DSI instance.

## State and persistence
State is opaque in `struct dw_mipi_dsi`; the header stores none. Hardware state includes DSI controller registers, PHY power, lane timings, and host attachment state. No on-disk persistence exists.

## Dependencies and integration points
It depends on Linux I/O memory types, DRM bridge/atomic/connector/modes, MIPI DSI devices, and platform device infrastructure. It integrates display panels/bridges into encoder pipelines and delegates SoC PHY specifics through callbacks.

## Risks and test signals
Risks include bad lane Mbps calculations, wrong DPHY timing at high modes, format mismatch between upstream bridge and DSI output, attach/detach lifetime bugs, and dual-DSI ordering errors. Test signals include panel attach/detach, bridge atomic format negotiation, mode fixup, lane count boundaries, escape clock failures, and master/slave DSI enable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi2.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi2.h

## Purpose
`dw_mipi_dsi2.h` is the platform contract for a newer DesignWare MIPI DSI2 core. It mirrors the DSI glue model while adding regmap access and PHY interface description for DPHY versus CPHY and PPI width.

## Important APIs, types, and functions
Important types are `enum dw_mipi_dsi2_phy_type`, `struct dw_mipi_dsi2_phy_iface`, `struct dw_mipi_dsi2_phy_timing`, `struct dw_mipi_dsi2_phy_ops`, `struct dw_mipi_dsi2_host_ops`, and `struct dw_mipi_dsi2_plat_data`. Public APIs are `dw_mipi_dsi2_probe`, `dw_mipi_dsi2_remove`, `dw_mipi_dsi2_bind`, and `dw_mipi_dsi2_unbind`.

## Control flow
A glue driver provides a regmap, max data lanes, mode validation/fixup, bus format negotiation, PHY ops, host ops, and private data. The common driver queries PHY interface details, computes lane Mbps, obtains timing and escape clock data, handles host attach/detach, and binds the bridge to the DRM encoder.

## State and persistence
No state is declared directly. Runtime state lives in opaque `struct dw_mipi_dsi2`, regmap-backed registers, PHY state, and MIPI host attachment state. Persistence is limited to hardware state while powered.

## Dependencies and integration points
It depends on regmap, Linux types, DRM bridge/atomic modes, MIPI DSI devices, and platform devices. Integration is with SoC PHY drivers, panel/bridge chains, and atomic bus-format negotiation.

## Risks and test signals
Risks include confusing CPHY and DPHY lane semantics, PPI width mismatch, timing underflow, regmap range errors, and host attach cleanup on bind failure. Test signals include CPHY and DPHY modes, max lane boundaries, format negotiation, escape clock configuration, suspend/resume through users, and panel hotplug or driver unload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/dw_mipi_dsi2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/imx.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/imx.h

## Purpose
`imx.h` exposes a small helper for creating legacy i.MX DRM bridges from device tree nodes. It is a compatibility interface for older i.MX display pipelines that still need bridge objects around legacy components.

## Important APIs, types, and functions
The only public API is `devm_imx_drm_legacy_bridge(struct device *dev, struct device_node *np, int type)`, returning a managed `struct drm_bridge *`. It forward-declares `struct device`, `struct device_node`, and `struct drm_bridge`.

## Control flow
Callers pass a device, OF node, and bridge type. The implementation allocates/registers a devm-managed bridge and ties its lifetime to the device, so cleanup is automatic on driver detach.

## State and persistence
The header has no state. Bridge state is allocated by the implementation and device-managed; no persistence beyond runtime device lifetime exists.

## Dependencies and integration points
It integrates with device tree, devres-managed allocation, DRM bridge chains, and i.MX legacy display drivers.

## Risks and test signals
Risks include wrong type values, stale OF node assumptions, and lifetime misuse if callers store the returned bridge beyond the parent device. Test signals include device removal, probe deferral, invalid node handling, and legacy i.MX bridge attach order in a DRM pipeline.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/imx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/inno_hdmi.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/inno_hdmi.h

## Purpose
`inno_hdmi.h` declares the platform interface for an Innosilicon HDMI bridge. It lets SoC glue provide PHY configuration tables and optional enable hooks while the common bridge handles HDMI encoder integration.

## Important APIs, types, and functions
Key types are `struct inno_hdmi_plat_ops`, `struct inno_hdmi_phy_config`, and `struct inno_hdmi_plat_data`. The only public entry point is `inno_hdmi_bind(struct device *pdev, struct drm_encoder *encoder, const struct inno_hdmi_plat_data *plat_data)`.

## Control flow
Glue code supplies PHY configs keyed by pixel clock, a default PHY config, and optional `enable` callback. Binding attaches the common HDMI bridge to a DRM encoder and lets the implementation select PHY parameters when modes are enabled.

## State and persistence
The header carries no state. Opaque `struct inno_hdmi` state and platform-supplied config tables must remain valid as required by the implementation. Hardware register state persists only while the controller is powered.

## Dependencies and integration points
It depends on Linux types, DRM encoders, DRM display modes, and device infrastructure. It integrates with SoC HDMI PHY setup and DRM bridge/encoder attach.

## Risks and test signals
Risks include missing default PHY config, unsorted or incomplete pixel clock tables, incorrect pre-emphasis/voltage levels, and enable callback ordering bugs. Test signals include mode changes across PHY thresholds, bind failure cleanup, default config fallback, and HDMI sink plug/unplug behavior through the common driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/inno_hdmi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/mhl.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/mhl.h

## Purpose
`mhl.h` centralizes Mobile High-Definition Link protocol constants, device capability/status register offsets, interrupt bits, MSC command IDs, remote-control message codes, burst IDs, and MHL3 infoframe structures used by MHL bridge drivers.

## Important APIs, types, and functions
There are no functions. Important definitions include device capability registers `MHL_DCAP_*`, extended capability/status registers `MHL_XDC_*` and `MHL_XDS_*`, interrupt registers `MHL_INT_*`, MSC commands such as `MHL_WRITE_STAT`, `MHL_SET_INT`, `MHL_MSC_MSG`, and `MHL_WRITE_BURST`, MSC message types for RCP/RAP/RBP/UCP/USB/HID/BIST, burst IDs, packed burst payload structures, and `struct mhl3_infoframe`.

## Control flow
Drivers include this file to construct CBUS MSC transactions, parse device capabilities, react to interrupt/status changes, exchange remote-control messages, and pack MHL3 video/audio metadata. Control flow is protocol-driven in callers: read capability/status registers, handle interrupts, send MSC commands, then parse replies or burst payloads using these constants.

## State and persistence
The header has no mutable state. Protocol state lives in the MHL transmitter/receiver hardware and driver state machines. Packed structures define wire layout, so endianness and exact field size are persistent ABI concerns.

## Dependencies and integration points
It depends only on Linux fixed-width types and endian annotations. It integrates with DRM bridge drivers, CBUS/MHL controllers, HDMI-like infoframes, remote input handling, and MHL3 eMSC burst processing.

## Risks and test signals
Risks include bit definition drift from the MHL spec, packed-structure ABI mistakes, endian misuse for burst IDs/sizes, typo-compatible macro names, and unsupported message handling. Test signals include device capability parsing, HPD/path enable flows, interrupt decoding, RCP/RAP/RBP/UCP messages, write-burst payloads, MHL3 infoframe generation, and malformed responder replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/mhl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/samsung-dsim.h -->
# sources/distributed-fs/ceph-client/include/drm/bridge/samsung-dsim.h

## Purpose
`samsung-dsim.h` is the shared interface and state definition for Samsung DSIM MIPI DSI host/bridge support across Exynos and i.MX variants. It describes hardware capabilities, platform callbacks, transfer tracking, and the core `struct samsung_dsim`.

## Important APIs, types, and functions
Important definitions include state bits `DSIM_STATE_*`, `enum samsung_dsim_type`, `samsung_dsim_hw_is_exynos`, `struct samsung_dsim_transfer`, `struct samsung_dsim_driver_data`, `struct samsung_dsim_host_ops`, `struct samsung_dsim_plat_data`, and `struct samsung_dsim`. Public symbols are `samsung_dsim_probe`, `samsung_dsim_remove`, and `samsung_dsim_pm_ops`.

## Control flow
Platform drivers select `samsung_dsim_plat_data` and driver data for register offsets, clocks, PLL ranges, quirks, and host ops. Probe maps registers, resources, supplies, clocks, PHY, GPIO TE, and initializes host/bridge state. Transfers are queued on `transfer_list`, completed by IRQ/TE handling, and bridge state tracks enable/initialization/video-output availability.

## State and persistence
Runtime state is explicit in `struct samsung_dsim`: mode, register base, PHY, clocks, supplies, IRQ, TE GPIO, PLL/HS/escape rates, lane/format flags, swap settings, state bits, brightness property, transfer completion, lock-protected transfer list, driver/platform data, and private pointer. Hardware PLL/register state persists while powered and is restored by PM paths.

## Dependencies and integration points
It depends on GPIO, regulators, DRM bridge/atomic/MIPI DSI/OF helpers, clocks, PHY, completions, spinlocks, and platform devices. Integration points include DSI panels, DRM bridge chains, host registration, TE IRQs, and SoC-specific DSIM data tables.

## Risks and test signals
Risks include variant register offset mistakes, PLL bound errors, clock/supply ordering, transfer list races, broken FIFO status quirks, and Exynos versus i.MX behavior differences. Test signals include probe/remove, runtime/system PM, command and video mode panels, TE IRQ handling, transfer timeout paths, PLL rate calculation, lane swap properties, and all listed hardware types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/bridge/samsung-dsim.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/clients/drm_client_setup.h -->
# sources/distributed-fs/ceph-client/include/drm/clients/drm_client_setup.h

## Purpose
`drm_client_setup.h` exposes helpers for creating standard DRM client infrastructure, usually fbdev/client setup, with optional format or color-mode preferences. It also provides no-op stubs when client setup is disabled.

## Important APIs, types, and functions
The public APIs under `CONFIG_DRM_CLIENT_SETUP` are `drm_client_setup`, `drm_client_setup_with_fourcc`, and `drm_client_setup_with_color_mode`. Disabled builds provide static inline no-op versions. It forward-declares `struct drm_device` and `struct drm_format_info`.

## Control flow
Drivers call one of the setup helpers after DRM device initialization. Enabled builds create/configure clients according to the requested format/fourcc/color mode; disabled builds compile the call away, keeping driver code simple.

## State and persistence
The header has no state. Any client state is owned by the DRM client implementation and associated with the DRM device. There is no persistence beyond runtime device/client lifetime.

## Dependencies and integration points
It depends on Kconfig, Linux types, DRM devices, and format metadata. Integration points are display drivers that want generic client setup without open-coding fbdev/client details.

## Risks and test signals
Risks include drivers assuming setup happened in disabled builds, invalid fourcc/color modes, and setup timing before mode_config is ready. Test signals include builds with and without `CONFIG_DRM_CLIENT_SETUP`, default client creation, preferred fourcc selection, color-mode selection, and device unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/clients/drm_client_setup.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp.h

## Purpose
`drm_dp.h` is the core DisplayPort protocol registry header. It defines AUX request/reply codes, DPCD register addresses and bit fields, eDP features, MST sideband message constants, DSC/FEC/PSR/Panel Replay/PCON/CEC/HDCP/tunneling/LTTPR definitions, and SDP wire structures.

## Important APIs, types, and functions
There are no functions. Important types are `enum drm_dp_phy`, `struct dp_sdp_header`, `struct dp_sdp`, `enum dp_pixelformat`, `enum dp_colorimetry`, `enum dp_dynamic_range`, `enum dp_content_type`, and `enum operation_mode`. Important macro groups cover DPCD receiver caps, link training control/status, payload tables, eDP backlight/PSR, DSC and PCON DSC, HDCP offsets, CEC tunneling, USB4 DP tunneling, LTTPR addressing helpers, sideband request/reply IDs, and bandwidth/status sizes.

## Control flow
Callers use constants to form AUX DPCD transactions, train links, parse sink capabilities, configure eDP/PSR/Panel Replay/DSC/FEC/MST/PCON/HDCP/CEC/tunneling features, and pack or interpret secondary data packets. The header’s macro arithmetic maps logical LTTPR/FEC PHY selection to concrete DPCD offsets.

## State and persistence
No kernel state lives here. These constants describe wire-visible register state stored in DP sinks, branch devices, protocol converters, and repeaters. Packed SDP structures are ABI-sensitive byte layouts.

## Dependencies and integration points
It depends on Linux integer types and `BIT`/`GENMASK`-style macros through included kernel headers. It is included by DP helpers, MST helpers, HDCP, DSC, tunneling, CEC-over-AUX, and GPU DP drivers.

## Risks and test signals
Risks include spec-version gating mistakes, overlapping register meanings, wrong bit masks, endian/packing errors for SDP and HDCP data, and stale constants for newer DP revisions. Test signals include link training across 8b/10b and 128b/132b, MST sideband parsing, eDP PSR/backlight/Panel Replay, DSC/FEC negotiation, DP-to-HDMI PCON FRL/DSC, CEC tunneling, HDCP authentication, LTTPR topologies, and USB4 DP tunnel bandwidth events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_aux_bus.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_aux_bus.h

## Purpose
`drm_dp_aux_bus.h` defines a Linux bus abstraction for devices reachable over a DisplayPort AUX channel, commonly eDP panels. It lets drivers instantiate endpoint devices from device tree children under a DP AUX controller.

## Important APIs, types, and functions
Key types are `struct dp_aux_ep_device` and `struct dp_aux_ep_driver`. Helpers include `to_dp_aux_ep_dev`, `to_dp_aux_ep_drv`, `of_dp_aux_populate_bus`, `of_dp_aux_depopulate_bus`, `devm_of_dp_aux_populate_bus`, deprecated populate/depopulate endpoint wrappers, `dp_aux_dp_driver_register`, `__dp_aux_dp_driver_register`, and `dp_aux_dp_driver_unregister`.

## Control flow
A DP AUX provider registers/populates child endpoint devices, optionally with a `done_probing` callback. Endpoint drivers register using the helper macro and receive probe/remove/shutdown callbacks. Deprecated wrappers translate a no-child `-ENODEV` result into legacy success.

## State and persistence
Endpoint state lives in `struct dp_aux_ep_device` with an embedded device and AUX pointer. Bus/device lifetime is governed by device model and optional devm cleanup. No persistent storage exists.

## Dependencies and integration points
It depends on Linux device model, OF matching tables, modules, and `struct drm_dp_aux`. Integration points are eDP panel drivers, AUX controllers, device tree child nodes, and managed device cleanup.

## Risks and test signals
Risks include endpoint lifetime after AUX unregister, legacy wrapper behavior hiding absent children, missing owner module references, and shutdown ordering relative to panels. Test signals include OF child population, no-child `-ENODEV`, devm cleanup, endpoint driver probe/remove/shutdown, and AUX unregister while endpoints exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_aux_bus.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_dual_mode_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_dual_mode_helper.h

## Purpose
`drm_dp_dual_mode_helper.h` declares helpers and register definitions for DP++ dual-mode adapters and LSPCON level shifter/protocol converter devices accessed over the DDC I2C bus.

## Important APIs, types, and functions
It defines DP dual-mode register offsets for HDMI ID, adapter ID, OUI, device ID, revisions, TMDS clock, I2C speed, TMDS output enable, CEC pin control, and LSPCON mode registers. Enums are `enum drm_lspcon_mode` and `enum drm_dp_dual_mode_type`. APIs include raw `drm_dp_dual_mode_read/write`, adapter detection, max TMDS clock, TMDS output get/set, type naming, and LSPCON get/set mode.

## Control flow
Drivers probe the adapter through DDC, classify it as none/unknown/type1/type2/LSPCON, query TMDS limits, enable or disable TMDS output, and optionally switch LSPCON between level-shifter and PCON modes with timeout handling.

## State and persistence
The header has no local state. Adapter state resides in external dongle registers and may persist while powered. LSPCON mode and TMDS output state are hardware-visible side effects.

## Dependencies and integration points
It depends on Linux types, DRM device logging/context, and I2C adapters. It integrates DP connectors with HDMI/DVI downstream sinks, LSPCON HDMI 2.0 conversion, CEC enablement, and connector mode validation.

## Risks and test signals
Risks include unreliable DDC reads, ambiguous type1 DVI detection, incorrect max TMDS interpretation, LSPCON mode switch timeouts, and CEC pin-control assumptions. Test signals include passive DP++ dongles, type2 HDMI adapters, LSPCON LS/PCON switching, TMDS disable/enable, high TMDS mode validation, and failed or short I2C transactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_dual_mode_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_helper.h

## Purpose
`drm_dp_helper.h` declares the main DRM DisplayPort helper library: link-status parsing, link-training delays, DPCD/AUX access, DSC/FEC/backlight/quirk helpers, downstream port introspection, LTTPR support, CEC-over-AUX hooks, PHY compliance helpers, PCON FRL/DSC utilities, and bandwidth calculations.

## Important APIs, types, and functions
Key types are `struct drm_dp_vsc_sdp`, `struct drm_dp_as_sdp`, `struct drm_dp_aux_msg`, `struct drm_dp_aux_cec`, `struct drm_dp_aux`, `struct drm_dp_dpcd_ident`, `struct drm_dp_desc`, `enum drm_dp_quirk`, `struct drm_edp_backlight_info`, and `struct drm_dp_phy_test_params`. Important APIs span `drm_dp_dpcd_read/write`, byte/data wrappers, AUX init/register/unregister, link status checks, DSC sink helpers, downstream/connector property helpers, LTTPR helpers, CRC capture, descriptor/quirk helpers, eDP backlight, CEC stubs or hooks, PCON FRL/DSC helpers, and `drm_dp_vsc_sdp_pack`.

## Control flow
Drivers initialize `drm_dp_aux`, provide a hardware `transfer` callback, register its I2C-over-AUX adapter, read DPCD capabilities, train links using status/delay helpers, query downstream devices and quirks, configure DSC/FEC/PCON/backlight as needed, and unregister on teardown. Inline DPCD data helpers convert short transfers to `-EPROTO` and retry buggy multi-byte reads byte-by-byte.

## State and persistence
`struct drm_dp_aux` carries runtime state: name, DDC adapter, owning devices, CRTC, transfer mutex, CRC work/count, CEC adapter state, remote/powered/probe flags, and I2C NACK/defer counters. DPCD and hardware state live in sinks/branches. No on-disk persistence exists.

## Dependencies and integration points
It depends on delay, I2C, DRM connectors, DP constants, CEC, EDID, backlight, panels, seq_file/debug output, and Kconfig-gated helper features. It is a central integration layer between GPU DP drivers, eDP panels, MST, DP-to-HDMI converters, HDCP/CEC, and compliance tooling.

## Risks and test signals
Risks include AUX transfer callbacks violating reply-only mutation, powered-down endpoint handling, short-transfer bugs, stale DPCD caps, Kconfig stub assumptions, PCON FRL/DSC misconfiguration, and eDP backlight mode errors. Test signals include AUX native/I2C reads with NACK/defer/short responses, DPCD cap parsing, link training status, downstream HDMI/DVI/VGA/PCON adapters, LTTPR topologies, CEC-over-AUX enabled and disabled builds, backlight init/set/enable/disable, and PHY compliance patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_mst_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_mst_helper.h

## Purpose
`drm_dp_mst_helper.h` defines the DRM DisplayPort Multi-Stream Transport topology, sideband messaging, connector, and atomic payload-management API used by GPU drivers with MST-capable DP connectors.

## Important APIs, types, and functions
Important types include `struct drm_dp_mst_port`, `struct drm_dp_mst_branch`, sideband request/reply structs, `struct drm_dp_sideband_msg_tx/rx`, `struct drm_dp_mst_topology_cbs`, `struct drm_dp_mst_atomic_payload`, `struct drm_dp_mst_topology_state`, and `struct drm_dp_mst_topology_mgr`. APIs cover topology manager init/destroy/set MST, HPD IRQ handling, port detection, EDID read, PBN/slot calculations, payload add/remove parts, ACT status, topology dump, suspend/resume, MST DPCD read/write, connector registration hooks, atomic state access, timeslot allocation/release, DSC enablement, atomic checks, PHY power, stream encryption status, refcount helpers, and MST state iterators.

## Control flow
Drivers initialize a topology manager for an MST-capable connector, enable MST after sink capability detection, process HPD/ESI events, let workqueues probe branch/port topology via sideband messages, create connectors through callbacks, and use atomic helpers to allocate VCPI/time slots and program payloads in commit phases.

## State and persistence
Runtime state is extensive: topology/malloc krefs, branch/port lists, cached EDIDs, AUX endpoints, transfer queues, locks, work items, delayed-destroy lists, payload IDs, sink count, cached DPCD, atomic payload lists, PBN divisor, slot ranges, and optional reference history. State is in-memory only; hardware payload tables and branch topology persist only while connected/powered.

## Dependencies and integration points
It depends on DP helper, DRM atomic/private objects, fixed-point math, workqueues, mutexes, waitqueues, krefs, EDID, connectors, and optional reference debugging. Integration points are GPU drivers, DRM connector creation, MST sideband protocol, remote DPCD/I2C, DSC over MST, HDCP stream status, and modeset atomic checks.

## Risks and test signals
Risks include refcount lifetime bugs, lock-order inversions, sideband timeout/retry failures, stale topology after hotplug, atomic slot conflicts, DSC payload accounting errors, and async commit ordering around start slots. Test signals include branch hotplug/unplug storms, nested MST hubs, remote I2C EDID reads, payload add/remove commit sequences, suspend/resume, DSC over MST, failed sideband replies, reference-debug builds, and atomic bandwidth rejection paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_mst_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_tunnel.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dp_tunnel.h

## Purpose
`drm_dp_tunnel.h` declares helpers for DisplayPort tunneling over USB4-style transport, including tunnel detection, bandwidth allocation, IRQ handling, reference tracking, atomic bandwidth state, and manager lifecycle. It supplies `-EOPNOTSUPP` stubs when disabled.

## Important APIs, types, and functions
Important types are opaque `struct drm_dp_tunnel`, `struct drm_dp_tunnel_mgr`, `struct drm_dp_tunnel_state`, and concrete `struct drm_dp_tunnel_ref`. Enabled APIs include get/put/ref wrappers, detect/destroy, enable/disable bandwidth allocation, allocate/get/update bandwidth, set I/O error, handle IRQ, max DPRX rate/lane count, available bandwidth, name lookup, atomic state getters, stream bandwidth setters, group stream queries, bandwidth checks, required bandwidth, and manager create/destroy.

## Control flow
Drivers create a tunnel manager, detect tunnels through AUX, enable bandwidth-allocation mode, react to tunnel IRQs, assign per-stream bandwidth in atomic state, check aggregate bandwidth, then commit allocation requests to hardware. Disabled builds return safe unsupported values while preserving call sites.

## State and persistence
Tunnel lifetime is reference-tracked with optional ref tracker pointers. Runtime state lives in opaque tunnel/manager/state objects and hardware DPCD tunneling registers. Bandwidth allocations are runtime transport state, not persistent storage.

## Dependencies and integration points
It depends on DRM devices, DP AUX, DRM atomic state, Linux error pointers, errno, types, and ref tracking. It integrates with DP tunneling DPCD definitions in `drm_dp.h`, USB4 bandwidth allocation, and display atomic bandwidth validation.

## Risks and test signals
Risks include leaked tunnel refs, unsupported stubs masking missing Kconfig, stale I/O-error state, bandwidth unit mismatches, and atomic stream masks not matching hardware groups. Test signals include enabled and disabled builds, tunnel detect/destroy, IRQ status changes, allocation success/failure, multi-stream bandwidth checks, manager teardown with live refs, and max rate/lane reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dp_tunnel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dsc.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dsc.h

## Purpose
`drm_dsc.h` defines VESA Display Stream Compression constants, encoder configuration structures, 128-byte Picture Parameter Set wire layout, and the DP PPS infoframe container used to communicate DSC parameters.

## Important APIs, types, and functions
There are no functions. Important definitions include DSC buffer/rate-control constants, PPS packing bit shifts/masks, `struct drm_dsc_rc_range_parameters`, `struct drm_dsc_config`, `struct drm_dsc_picture_parameter_set`, and `struct drm_dsc_pps_infoframe`. The PPS structure is packed and uses big-endian fields for multi-byte wire values.

## Control flow
Drivers populate `drm_dsc_config`, helper code computes rate-control fields, then packs `drm_dsc_picture_parameter_set` and wraps it in `drm_dsc_pps_infoframe` for DP secondary data or protocol-converter programming before enabling compression.

## State and persistence
State is purely caller-owned configuration and packed metadata. The PPS byte layout is protocol-persistent for a stream; hardware encoder/decoder state is outside this header.

## Dependencies and integration points
It depends on `drm_dp.h` for `struct dp_sdp_header`. It integrates with DP/eDP DSC helpers, HDMI PCON DSC paths, encoder drivers, and sink capability parsing.

## Risks and test signals
Risks include endian mistakes, packed layout drift, invalid RC parameters, slice width/height mismatches, unsupported bpc/bpp/native 4:2:0 or 4:2:2 combinations, and PPS fields inconsistent with sink caps. Test signals include PPS byte-for-byte validation, DSC 1.1 and 1.2 configs, RGB/YCoCg/native modes, 8/10/12 bpc, slice count boundaries, and compressed stream enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dsc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dsc_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_dsc_helper.h

## Purpose
`drm_dsc_helper.h` declares helper functions for deriving, packing, and dumping Display Stream Compression parameters for DP/DSC encoders.

## Important APIs, types, and functions
`enum drm_dsc_params_type` selects parameter presets for DSC 1.2 4:4:4, legacy DSC 1.1 pre-SCR, DSC 1.2 4:2:2, and DSC 1.2 4:2:0. Functions include `drm_dsc_dp_pps_header_init`, `drm_dsc_dp_rc_buffer_size`, `drm_dsc_pps_payload_pack`, constant/default setters, RC threshold/setup/compute helpers, `drm_dsc_initial_scale_value`, `drm_dsc_flatness_det_thresh`, `drm_dsc_get_bpp_int`, and `drm_dsc_dump_config`.

## Control flow
Drivers create a `drm_dsc_config`, set constant fields and RC thresholds, select RC params by type, compute dependent RC values, pack the PPS payload, initialize the DP PPS header, and optionally dump the resulting config for debug.

## State and persistence
No global state exists. The helpers mutate caller-provided `drm_dsc_config` or PPS structures and return computed values. Persistent protocol state is the packed PPS sent to sinks.

## Dependencies and integration points
It depends on `drm_dsc.h` and `struct drm_printer`. It integrates with DP/eDP encoders, protocol converters, debug output, and sink capability selection.

## Risks and test signals
Risks include choosing the wrong preset for pixel encoding, invalid computed RC intervals, bpp fractional handling mistakes, and PPS pack mismatch. Test signals include known-good PPS vectors, each params type, RC buffer size from DPCD block-size fields, debug dump readability, and boundary bpp/bpc/slice configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_dsc_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp.h

## Purpose
`drm_hdcp.h` defines shared HDCP 1.x and HDCP 2.2 constants, register offsets, message IDs, timeout values, packed protocol message structures, SRM formats, and helper conversions used by HDMI/DVI and DisplayPort content-protection implementations.

## Important APIs, types, and functions
Important definitions include HDCP check periods, KSV/AN/Ri/Bstatus lengths, DDC offsets, HDCP 2.2 message IDs and field lengths, timeout macros, HDMI HDCP 2.2 register offsets, stream type constants, SRM constants, and content type values. Packed structures model HDCP2 messages such as `hdcp2_ake_init`, `hdcp2_ake_send_cert`, `hdcp2_lc_init`, `hdcp2_ske_send_eks`, repeater messages, `hdcp_srm_header`, and stream ID/type. Inline helpers convert 24-bit big-endian sequence numbers.

## Control flow
Authentication implementations use these definitions to compose and parse HDCP messages, poll readiness with protocol timeouts, process repeater KSV/receiver lists, manage stream types, and validate SRM revocation data. The inline sequence helpers support repeater stream management counters.

## State and persistence
The header has no mutable state. HDCP sessions maintain keys, nonces, sequence numbers, and authentication status in driver/hardware code. Packed structs define protocol-persistent byte layout and must not drift.

## Dependencies and integration points
It depends on Linux types and endian annotations. It integrates with DRM connector content-protection properties, DP DPCD HDCP offsets, HDMI DDC HDCP registers, SRM revocation handling, and HDCP 2.2 trusted execution or hardware engines.

## Risks and test signals
Risks include packed layout errors, timeout mismatches between HDMI and DP, endian mistakes in 24-bit sequence numbers, repeater count/depth mask errors, and fixed stream-count assumptions. Test signals include HDCP 1.4 and 2.2 authentication, repeater topologies, SRM revocation checks, Type0/Type1 streams, DP and HDMI transport paths, timeout handling, and sequence rollover rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp_helper.h

## Purpose
`drm_hdcp_helper.h` declares DRM helper functions for HDCP revocation checking and connector content-protection property management.

## Important APIs, types, and functions
The exported APIs are `drm_hdcp_check_ksvs_revoked`, `drm_connector_attach_content_protection_property`, and `drm_hdcp_update_content_protection`. It includes `drm_hdcp.h` and forward-declares `struct drm_device` and `struct drm_connector`.

## Control flow
Drivers attach the content protection property to a connector, run KSV revocation checks against SRM data during authentication or repeater validation, and update the connector property when protection state changes.

## State and persistence
The header owns no state. Connector properties live in DRM core state, while SRM/revocation information and HDCP authentication state live in the implementation and device.

## Dependencies and integration points
It depends on DRM devices/connectors and HDCP protocol definitions. It integrates HDCP engines with the DRM property model observed by userspace.

## Risks and test signals
Risks include stale userspace-visible protection state, missing content type property when HDCP 2.2 Type1 is required, and incorrect KSV count handling. Test signals include property attachment, authenticated/desired/undesired state transitions, revoked KSV lists, zero KSV count, and connector destruction while protection work is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdcp_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_audio_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_audio_helper.h

## Purpose
`drm_hdmi_audio_helper.h` declares DRM connector helpers for HDMI audio codec registration and plug notifications.

## Important APIs, types, and functions
The public APIs are `drm_connector_hdmi_audio_init` and `drm_connector_hdmi_audio_plugged_notify`. Initialization accepts a connector, HDMI codec device, connector HDMI audio callbacks, maximum I2S playback channels, supported I2S formats, SPDIF support, and sound DAI port.

## Control flow
HDMI bridge/connector drivers initialize audio support after connector setup, passing codec capabilities and callbacks. Hotplug or detect paths call the plugged notification helper to update audio users about sink presence.

## State and persistence
The header has no state. Audio state lives in connector private data and the HDMI codec component. Plug state is runtime only.

## Dependencies and integration points
It depends on Linux types, DRM connectors, HDMI audio callback definitions, devices, ALSA HDMI codec integration, I2S/SPDIF capability reporting, and hotplug handling.

## Risks and test signals
Risks include wrong channel/format capabilities, missing plug notifications, lifetime mismatch with codec device, and DAI port mismatches. Test signals include codec registration, HDMI hotplug/unplug, ELD/audio routing updates, I2S/SPDIF capability exposure, and connector cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_audio_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_cec_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_cec_helper.h

## Purpose
`drm_hdmi_cec_helper.h` defines the connector-level HDMI CEC helper interface for registering a CEC adapter, forwarding received messages, completing transmissions, and optionally registering a CEC notifier.

## Important APIs, types, and functions
The central type is `struct drm_connector_hdmi_cec_funcs`, with callbacks for hardware init, teardown, enable, logical address programming, and transmit. APIs include `drmm_connector_hdmi_cec_register`, `drm_connector_hdmi_cec_received_msg`, `drm_connector_hdmi_cec_transmit_done`, `drm_connector_hdmi_cec_transmit_attempt_done`, and Kconfig-gated `drmm_connector_hdmi_cec_notifier_register`.

## Control flow
Drivers register CEC support for a connector with hardware callbacks and available logical addresses. CEC core calls enable/log_addr/transmit through callbacks; IRQ or polling paths report received messages and transmit completion. The notifier helper is a no-op stub when disabled.

## State and persistence
No state lives in the header. Managed registration ties adapter lifetime to the DRM connector/device. CEC logical addresses and enable state are runtime hardware state.

## Dependencies and integration points
It depends on Linux types, DRM connectors, CEC messages/adapters, devices, managed DRM cleanup, and optional CEC notifier support. It integrates HDMI bridge drivers with the Linux CEC framework.

## Risks and test signals
Risks include callback ordering around init/uninit, transmit completion races, logical address programming failures, disabled notifier assumptions, and hotplug teardown while CEC work is pending. Test signals include adapter registration, enable/disable, multi-LA programming, received message delivery, transmit done and attempt done paths, notifier enabled/disabled builds, and connector removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_cec_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_helper.h

## Purpose
`drm_hdmi_helper.h` declares common HDMI helpers for AVI/HDR infoframe fields, content type, adjusted TMDS character clock computation, and ACR N/CTS audio clock recovery values.

## Important APIs, types, and functions
APIs are `drm_hdmi_avi_infoframe_colorimetry`, `drm_hdmi_avi_infoframe_bars`, `drm_hdmi_infoframe_set_hdr_metadata`, `drm_hdmi_avi_infoframe_content_type`, `drm_hdmi_compute_mode_clock`, and `drm_hdmi_acr_get_n_cts`.

## Control flow
HDMI drivers build infoframes from connector state, compute the TMDS character rate from mode, bpc, and output format, then derive ACR N/CTS for a sample rate. HDR metadata is copied into a DRM infoframe when connector state contains valid metadata.

## State and persistence
The header has no state. Generated infoframes are transient packets sent each modeset/frame as required by the hardware. Clock calculations are pure helper results.

## Dependencies and integration points
It depends on Linux HDMI infoframe definitions, DRM connector state, display modes, and output color formats. It integrates with HDMI bridge/encoder implementations and audio setup.

## Risks and test signals
Risks include wrong colorimetry/range/content fields, HDR metadata omissions, TMDS rate errors for YCbCr 4:2:0 or high bpc, and incorrect ACR values. Test signals include AVI/HDR infoframe validation, RGB/YUV formats, 8/10/12 bpc modes, audio sample rates, and sink compliance checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_state_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_state_helper.h

## Purpose
`drm_hdmi_state_helper.h` declares atomic connector helpers for HDMI-specific state reset, validation, infoframe update/clear, hotplug/force handling, and mode validation.

## Important APIs, types, and functions
The public APIs are `__drm_atomic_helper_connector_hdmi_reset`, `drm_atomic_helper_connector_hdmi_check`, `drm_atomic_helper_connector_hdmi_update_audio_infoframe`, `drm_atomic_helper_connector_hdmi_clear_audio_infoframe`, `drm_atomic_helper_connector_hdmi_update_infoframes`, `drm_atomic_helper_connector_hdmi_hotplug`, `drm_atomic_helper_connector_hdmi_force`, and `drm_hdmi_connector_mode_valid`.

## Control flow
Drivers use the reset helper to initialize HDMI connector state, run the check helper during atomic validation, update or clear audio/infoframes during commit, and call hotplug/force helpers when connector status changes. Mode validation applies HDMI connector constraints before accepting a mode.

## State and persistence
The header declares operations over DRM atomic connector state; it owns no storage. HDMI infoframe state is runtime connector/atomic state and hardware packet state.

## Dependencies and integration points
It depends on DRM atomic state, connectors, connector states, display modes, HDMI audio infoframes, and connector status. It integrates HDMI-specific policy into generic DRM atomic modesetting.

## Risks and test signals
Risks include state reset not matching connector defaults, missed infoframe updates after property changes, audio infoframe stale data, hotplug races, and invalid high-clock/color modes accepted. Test signals include atomic check failures, property changes affecting infoframes, audio enable/disable, hotplug and forced connectors, and HDMI mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_hdmi_state_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_scdc.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_scdc.h

## Purpose
`drm_scdc.h` defines HDMI 2.x Status and Control Data Channel register offsets and bit fields used to configure scrambling, TMDS bit clock ratio, read requests, lock/status flags, error counters, and sink identification.

## Important APIs, types, and functions
There are no functions. Important constants include `SCDC_SINK_VERSION`, `SCDC_SOURCE_VERSION`, update flags, `SCDC_TMDS_CONFIG` bits for scrambling and 1/40 clock ratio, scrambler status, read request config, channel lock/clock detect status, per-channel error counters, test read request controls, manufacturer OUI, device ID, hardware/software revisions, and manufacturer-specific region sizing.

## Control flow
HDMI drivers use these constants over DDC/I2C SCDC transactions to enable scrambling for high TMDS rates, set the 1/40 bit clock ratio, read lock/error status, and identify sink capabilities.

## State and persistence
No local state exists. SCDC registers are sink-side runtime state and may reset on hotplug, power loss, or mode changes.

## Dependencies and integration points
It is standalone and integrates through `drm_scdc_helper.h`, HDMI bridge/encoder mode-setting code, and DDC/I2C adapters.

## Risks and test signals
Risks include enabling scrambling without sink support, clock-ratio mismatches, stale status reads, error-counter interpretation mistakes, and sink-specific SCDC quirks. Test signals include HDMI 2.0 high TMDS modes, scrambling status polling, clock ratio set/clear, channel lock flags, CED error counters, and hotplug reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_scdc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_scdc_helper.h -->
# sources/distributed-fs/ceph-client/include/drm/display/drm_scdc_helper.h

## Purpose
`drm_scdc_helper.h` declares helper functions for reading and writing HDMI SCDC registers over DDC/I2C and for toggling scrambling and high TMDS clock ratio through a DRM connector.

## Important APIs, types, and functions
APIs are `drm_scdc_read`, `drm_scdc_write`, inline `drm_scdc_readb`, inline `drm_scdc_writeb`, `drm_scdc_get_scrambling_status`, `drm_scdc_set_scrambling`, and `drm_scdc_set_high_tmds_clock_ratio`.

## Control flow
Drivers call read/write wrappers for arbitrary SCDC register access or use connector helpers during modeset to enable/disable scrambling and set the TMDS 1/40 clock ratio. Byte helpers are convenience wrappers around bulk access.

## State and persistence
No header state exists. State lives in sink SCDC registers and connector/DDC context. Register values may be lost across hotplug or sink power transitions.

## Dependencies and integration points
It depends on Linux types, SCDC register definitions, DRM connectors, and I2C adapters. It integrates HDMI mode setting with sink-side SCDC control.

## Risks and test signals
Risks include short I2C transfers, connector lacking DDC, boolean helpers hiding detailed errors, scrambling status read failures, and wrong order relative to TMDS enable. Test signals include SCDC read/write error paths, high TMDS modes, scrambling status check, clock ratio set/clear, non-SCDC HDMI sinks, and hotplug after SCDC programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/display/drm_scdc_helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_accel.h -->
# sources/distributed-fs/ceph-client/include/drm/drm_accel.h

## Purpose
`drm_accel.h` defines the DRM accelerator device minor interface, default accelerator file operations, and core accelerator lifecycle hooks. It supports accelerator-class DRM drivers sharing GEM mmap/ioctl/read/poll/release behavior under the accel major.

## Important APIs, types, and functions
Constants are `ACCEL_MAJOR` and `ACCEL_MAX_MINORS`. Macros are `DRM_ACCEL_FOPS` and `DEFINE_DRM_ACCEL_FOPS`. Enabled builds expose `accel_minors_xa`, `accel_core_init`, `accel_core_exit`, `accel_set_device_instance_params`, `accel_open`, and `accel_debugfs_register`. Disabled builds stub most helpers and let `accel_core_init` return success.

## Control flow
Accelerator drivers define file operations with `DEFINE_DRM_ACCEL_FOPS`, point `drm_driver.fops` at them, and rely on accel core init to manage minors. Opening an accel node routes through `accel_open`; common DRM operations handle ioctl, release, poll, read, GEM mmap, and llseek. Debugfs registration is optional and Kconfig-gated.

## State and persistence
Global runtime state includes the `accel_minors_xa` xarray when enabled. Device instance parameters are set on kernel devices, and file state follows normal DRM file lifetime. No persistent storage exists.

## Dependencies and integration points
It depends on DRM file infrastructure, GEM mmap, xarray, device model, debugfs, and `CONFIG_DRM_ACCEL`. It integrates accelerator drivers into the DRM major/minor and file operation model.

## Risks and test signals
Risks include drivers sharing file-ops structures despite `THIS_MODULE`, missing `accel_open` in disabled builds if used directly, minor exhaustion, debugfs lifetime issues, and mmap/ioctl expectations differing from display DRM nodes. Test signals include enabled/disabled builds, module refcount on open, minor allocation up to limits, open/release/ioctl/mmap paths, debugfs registration, and device instance naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/drm/drm_accel.h -->
