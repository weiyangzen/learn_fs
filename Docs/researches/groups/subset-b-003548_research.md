# Research: subset-b-003548

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c

## Purpose

This is the Cadence MIPI DSI host and DRM bridge implementation. It exposes one DPI input bridge to the DRM bridge chain and one MIPI DSI host to downstream DSI panels/bridges. It programs DSI link, D-PHY timing, video packetization, direct command transfer, interrupts, runtime PM, and platform wrapper callbacks.

## Important APIs, Types, And Functions

Important callbacks are `cdns_dsi_drm_probe()`, `cdns_dsi_attach()`, `cdns_dsi_transfer()`, and `cdns_dsi_bridge_atomic_pre_enable/post_disable/check()`. `struct cdns_dsi_bridge_state` stores computed `cdns_dsi_cfg` timing across atomic check and enable. `cdns_dsi_mode2cfg()`, `cdns_dsi_check_conf()`, `cdns_dsi_round_pclk()`, `cdns_dsi_init_link()`, and `cdns_dsi_hs_init()` are the core mode-to-hardware helpers.

## Control Flow

Probe maps registers, enables the APB clock long enough to validate the Cadence vendor ID, discovers FIFO depths, masks interrupts, initializes runtime PM, runs optional platform init, and registers the DSI host. A DSI peripheral attach resolves the downstream bridge through OF graph and only then adds the DPI input bridge. Atomic check forces negative syncs, rounds pixel clock through D-PHY validation, and stores converted DSI timing. Pre-enable resumes runtime PM, invokes wrapper enable, initializes link/PHY, waits for lanes ready, writes video timing/packet registers, configures timeouts and packet format, and enables the input interface. Post-disable shuts video/link bits down after the upstream DPI stream has stopped, invokes wrapper disable, powers down the PHY, and releases runtime PM.

## State And Persistence Behavior

Driver state is in `struct cdns_dsi`: mapped MMIO, host/bridge endpoints, FIFO depths, completion, clocks/reset, D-PHY handle, platform ops, and `link_initialized`/`phy_initialized` flags. There is no persistent storage; hardware state is rebuilt on probe, command transfer, and atomic enable. Direct commands synchronize through `direct_cmd_comp` and IRQ status bits.

## Dependencies And Integration Points

The file integrates Linux DRM bridge atomic state, MIPI DSI host ops, OF graph bridge discovery, generic PHY MIPI D-PHY helpers, clocks, reset controls, IRQ completions, and optional platform ops such as TI J721E. It requires atomic DRM devices and supports a single attached DSI device.

## Risks And Test Signals

Risks include incorrect byte timing overheads, clock rounding that the upstream CRTC cannot satisfy, missing runtime-PM unwind when pre-enable returns early, direct-command FIFO/RX length rejection, and color shifts if enable/disable order changes. Test signals are successful DSI panel attach, DCS read/write transfers, mode validation failures for illegal timings, runtime suspend/resume, IRQ completion for direct commands, and visual modeset/hotplug smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.h

## Purpose

This header defines the shared data model for the Cadence DSI core and its platform wrappers. It is the contract between the generic DSI host/bridge implementation and SoC-specific glue such as TI J721E.

## Important APIs, Types, And Functions

`struct cdns_dsi_output` records the attached `mipi_dsi_device`, downstream `drm_bridge`, and cached PHY options. `enum cdns_dsi_input_id` names SDI, DPI, and DSC inputs, though the core currently forces `CDNS_DPI_INPUT`. `struct cdns_dsi_cfg` stores horizontal DSI byte counts. `struct cdns_dsi_input` embeds the upstream DRM bridge. `struct cdns_dsi_platform_ops` provides `init`, `deinit`, `enable`, and `disable` wrapper hooks. `struct cdns_dsi` contains all runtime state.

## Control Flow

The header has no executable flow, but it shapes probe and atomic paths. The core fills clock/reset/PHY/MMIO fields at probe, stores attached output device information during DSI host attach, uses platform ops during probe and atomic enable/disable, and gates optional J721E wrapper MMIO through `CONFIG_DRM_CDNS_DSI_J721E`.

## State And Persistence Behavior

All state is in memory and device-managed where possible. The two booleans `link_initialized` and `phy_initialized` prevent redundant link/PHY bring-up across command transfers and modesets until post-disable clears them. The completion coordinates direct-command IRQs.

## Dependencies And Integration Points

The header depends on DRM bridge, DRM MIPI DSI, Linux completions, and generic PHY configuration types. Platform wrapper headers include this file to declare wrapper ops against the full `struct cdns_dsi`.

## Risks And Test Signals

Changing field layout or optional members can break wrapper builds or core assumptions. The core assumes one `input` and one `output`; extending to multiple DSI devices would require bridge-chain reconfiguration beyond this header. Build coverage with and without `CONFIG_DRM_CDNS_DSI_J721E` is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.c

## Purpose

This file implements the TI J721E wrapper operations for the generic Cadence DSI core. The wrapper selects and enables the SoC-specific DPI path feeding the Cadence DSI block.

## Important APIs, Types, And Functions

`cdns_dsi_j721e_init()` maps the second platform resource into `dsi->j721e_regs`. `cdns_dsi_j721e_enable()` writes `DSI_WRAP_DPI_0_EN` to the wrapper DPI control register. `cdns_dsi_j721e_disable()` clears that register. `dsi_ti_j721e_ops` exports those functions as `struct cdns_dsi_platform_ops`.

## Control Flow

The core driver obtains these ops from OF match data for `"ti,j721e-dsi"`. During probe, the wrapper maps its extra MMIO resource. During atomic pre-enable, before Cadence link/PHY programming, the wrapper enables DPI0. During post-disable, after the Cadence stream has been stopped, it resets the wrapper DPI control to defaults.

## State And Persistence Behavior

The only persistent runtime state is the extra MMIO pointer stored in `struct cdns_dsi`. Hardware state is a single wrapper register bit, restored to zero on disable. No clocks, resets, or allocations are owned here.

## Dependencies And Integration Points

This wrapper depends on the generic Cadence DSI core and platform resource index 1. It is selected only when `CONFIG_DRM_CDNS_DSI_J721E` is enabled and integrated through the core OF table.

## Risks And Test Signals

The hard-coded routing supports only the J721E configuration where DSS0 DPI2 feeds DSI DPI0. Wrong DT resource ordering or unsupported routing would produce a blank panel despite the Cadence core succeeding. Test with a J721E DSI panel should show wrapper enable before link start and clean disable on modeset teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.h

## Purpose

This header exposes the TI J721E Cadence DSI wrapper ops to the generic Cadence DSI core.

## Important APIs, Types, And Functions

It includes `cdns-dsi-core.h` and declares `extern const struct cdns_dsi_platform_ops dsi_ti_j721e_ops`.

## Control Flow

There is no executable flow. The core OF match table references `dsi_ti_j721e_ops` when the J721E wrapper is built, which lets the core call wrapper `init`, `enable`, and `disable` callbacks.

## State And Persistence Behavior

The header stores no state. It provides compile-time linkage between the platform wrapper translation unit and the core.

## Dependencies And Integration Points

It depends on the core header for the platform ops type. Its only integration point is the Cadence DSI OF match entry guarded by `CONFIG_DRM_CDNS_DSI_J721E`.

## Risks And Test Signals

Build failures with J721E enabled catch declaration mismatches. Link failures would indicate that the wrapper object was not compiled while the core expects `dsi_ti_j721e_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-dsi-j721e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.c

## Purpose

This is the Cadence MHDP8546 DisplayPort bridge driver. It loads the controller firmware, exposes a DRM bridge and DP AUX channel, handles HPD, EDID, DPCD access, link training, video framer programming, optional HDCP, and platform wrapper hooks.

## Important APIs, Types, And Functions

Core paths include `cdns_mhdp_probe/remove()`, `cdns_mhdp_attach/detach()`, `cdns_mhdp_atomic_check/enable/disable()`, `cdns_mhdp_transfer()`, `cdns_mhdp_link_up/down()`, `cdns_mhdp_link_training()`, `cdns_mhdp_configure_video()`, `cdns_mhdp_update_link_status()`, and `cdns_mhdp_wait_for_sw_event()`. Mailbox helpers serialize firmware commands with `mbox_mutex`; link and modeset state are protected by `link_mutex`; firmware/bridge attach races use `start_lock`.

## Control Flow

Probe enables the functional clock, maps main and optional SAPB registers, gets the DP PHY, initializes AUX, runtime PM, platform ops, firmware clock registers, IRQ, host caps, PHY, work items, firmware loading, optional HDCP, and the bridge. Firmware is loaded asynchronously, copied to IMEM, activated through mailbox, and then HPD interrupts are enabled if the bridge is attached. Atomic enable links up when plugged, runs platform enable, enables VIF clock, optionally starts HDCP, validates bandwidth, computes TU/line thresholds, writes DP MSA/framer registers, and caches the current mode. HPD work rereads events/status, retrains if needed, and notifies the bridge.

## State And Persistence Behavior

State includes host/sink/link capability structures, `link_up`, `plugged`, `bridge_enabled`, current mode in bridge state, `sw_events`, firmware `hw_state`, connector pointer, work items, and optional HDCP state. There is no disk persistence; firmware and hardware registers are reinitialized at runtime. Removal waits briefly for firmware readiness before sending standby.

## Dependencies And Integration Points

The driver depends on `cadence/mhdp8546.bin`, DRM DP helper APIs, DP AUX, generic DP PHY configuration, OF match data, runtime PM, threaded IRQs, and optional platform info such as TI J721E bus flags/ops. HDCP sidecar code uses `cdns_mhdp_wait_for_sw_event()`.

## Risks And Test Signals

Risks include asynchronous firmware races, mailbox timeouts, link-training fallback errors, stale connector pointer use in retry work, ignoring HDCP work cleanup in remove, and bandwidth checks before a trained link exists. Test signals are firmware keepalive/version logs, AUX DPCD/EDID reads, HPD events, successful CR/EQ training at lane/rate fallbacks, modeset retry on failed training, and DP display at expected color depth.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.h

## Purpose

This header defines MHDP8546 register offsets, firmware mailbox opcodes, DP link capability structures, platform hooks, bridge state, HDCP state, and the main device object shared by the core, HDCP, and J721E wrapper files.

## Important APIs, Types, And Functions

Key structures are `cdns_mhdp_link`, `cdns_mhdp_host`, `cdns_mhdp_sink`, `cdns_mhdp_display_fmt`, `mhdp_platform_ops`, `cdns_mhdp_bridge_state`, `cdns_mhdp_platform_info`, `cdns_mhdp_hdcp`, and `cdns_mhdp_device`. It declares `cdns_mhdp_wait_for_sw_event()`. Constants cover APB/mailbox registers, DP framer registers, mailbox modules, firmware name, HPD events, lane mapping, link training, and HDCP SW events.

## Control Flow

The header has no executable flow, but it encodes the control contract: core mailbox commands use module/opcode constants, video setup uses framer register macros, wrappers provide `init/exit/enable/disable`, and HDCP waits for SW events produced by the core IRQ handler.

## State And Persistence Behavior

`struct cdns_mhdp_device` centralizes all mutable runtime state: MMIO bases, clocks/PHY, AUX, bridge, link caps, DP sink/source caps, display format, HPD/link flags, locks, wait queues, work structs, firmware state, and HDCP fields. State is volatile and reconstructed on probe/firmware load/modeset.

## Dependencies And Integration Points

It depends on DRM DP helper, DRM bridge/connector, mutex/spinlock APIs, and forward declarations for clock/device/PHY. The HDCP and J721E files include it to access device state and shared constants.

## Risks And Test Signals

Register macro mistakes can silently misprogram hardware. Locking comments document important concurrency contracts; violations can race firmware callback, bridge detach, IRQ masking, or link training. Build coverage across core, HDCP, and J721E configs validates type visibility and optional integrations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.c

## Purpose

This file implements optional HDCP control for the MHDP8546 DisplayPort bridge using the secure APB mailbox. It negotiates HDCP 2.2 first where allowed, falls back to HDCP 1.4 for Type 0 content, updates connector content-protection state, and periodically checks link authentication.

## Important APIs, Types, And Functions

Public entry points are `cdns_mhdp_hdcp_init()`, `cdns_mhdp_hdcp_enable()`, and `cdns_mhdp_hdcp_disable()`. Internal helpers mirror the core mailbox helpers on `sapb_regs`, then implement status/config commands, receiver-ID validation, KM-stored response, authentication flows, retry checks, and property work.

## Control Flow

Enable takes `hdcp.mutex`, runs `_cdns_mhdp_hdcp_enable()`, tries HDCP 2.2 up to three times, falls back to HDCP 1.4 only for content type 0, marks content protection enabled, schedules property work, and starts delayed link checks. Authentication configures firmware, waits for SW events from the core IRQ path, validates receiver IDs, responds valid, and waits for auth completion. Check work retries authentication when status loses the auth bit. Disable marks content protection undesired, schedules property work, sends disable config, and cancels delayed checks.

## State And Persistence Behavior

State is in `mhdp->hdcp`: delayed work, property work, mutex, current DRM property value, and content type. Pairing/KM data structs exist in the header, but this implementation does not persist keys; it responds with no stored KM.

## Dependencies And Integration Points

It depends on `sapb_regs`, the core `mbox_mutex`, core SW event wait queue, DRM HDCP property values, and `mhdp->connector`. The core calls enable from atomic enable and disable from atomic disable.

## Risks And Test Signals

Risks include fixed-size receiver ID storage versus firmware-provided receiver count, returning `-1` instead of standard errno in many paths, connector lifetime races in work, and remove explicitly ignoring HDCP work cleanup. Test signals include content-protection property transitions, HDCP 2.2/1.4 negotiation logs, forced reauth after sink unplug, and absence of lingering work after bridge disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.h

## Purpose

This header defines the MHDP8546 HDCP mailbox protocol constants, status helpers, pairing/public-key data shapes, and public HDCP entry points.

## Important APIs, Types, And Functions

It defines receiver/status sizes, status bit extraction through `GET_HDCP_PORT_STS_LAST_ERR()`, HDCP configuration bits, HDCP transaction opcodes, content types, the periodic check interval, `struct cdns_hdcp_pairing_data`, `struct cdns_hdcp_tx_public_key_param`, and prototypes for `cdns_mhdp_hdcp_enable()`, `cdns_mhdp_hdcp_disable()`, and `cdns_mhdp_hdcp_init()`.

## Control Flow

There is no executable flow. The enums encode firmware message IDs used by the secure mailbox implementation; the public prototypes are called by the MHDP core during bridge enable, disable, and probe initialization.

## State And Persistence Behavior

The header describes key/pairing data layouts but does not store data. Runtime state lives in `struct cdns_mhdp_hdcp` from the core header.

## Dependencies And Integration Points

It includes `cdns-mhdp8546-core.h` for the device type and shared mailbox constants. It also implicitly depends on DRM HDCP content type constants consumed by the C file.

## Risks And Test Signals

Protocol enum ordering is firmware ABI sensitive. A mismatch can make HDCP commands syntactically valid but semantically wrong. Build coverage of HDCP-enabled MHDP and runtime authentication against HDCP 1.4 and 2.2 sinks are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.c

## Purpose

This file implements TI J721E wrapper support for the Cadence MHDP8546 DisplayPort/eDP block. It maps wrapper registers, selects the supported DPI-to-VIF routing, and exports required input bus flags.

## Important APIs, Types, And Functions

`cdns_mhdp_j721e_init()` maps resource index 1 to `mhdp->j721e_regs`. `cdns_mhdp_j721e_enable()` enables VIF0 and selects DPI2. `cdns_mhdp_j721e_disable()` clears the wrapper DSC config register to defaults. `mhdp_ti_j721e_ops` and `mhdp_ti_j721e_bridge_input_bus_flags` are consumed by the core OF match data.

## Control Flow

The core calls wrapper init during probe, wrapper enable during atomic enable before VIF clock/video programming, and wrapper disable during atomic disable after VIF clock shutdown. Bus flags are copied in the core atomic check so the upstream source samples on the correct edges with DE high.

## State And Persistence Behavior

State is limited to the extra MMIO pointer and wrapper register writes. The routing is not dynamic and is reset on disable.

## Dependencies And Integration Points

It depends on the MHDP core data structures, platform resource ordering, and `CONFIG_DRM_CDNS_MHDP8546_J721E`. The supported SST routing is DSS0 DPI0 to eDP DPI2 through VIF0.

## Risks And Test Signals

The disable path clears `DPTX_DSC_CFG` rather than `DPTX_SRC_CFG`, so wrapper routing reset assumptions should be checked against hardware docs. Test signals are correct J721E eDP output, stable sampling edges, and wrapper resource mapping success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.h

## Purpose

This header exposes the TI J721E MHDP8546 wrapper operations and bridge input bus flags to the generic MHDP core.

## Important APIs, Types, And Functions

It includes `cdns-mhdp8546-core.h`, forward-declares `struct mhdp_platform_ops`, and declares `mhdp_ti_j721e_ops` and `mhdp_ti_j721e_bridge_input_bus_flags`.

## Control Flow

There is no executable code. The core OF table references these externs when building J721E support, passing them through `struct cdns_mhdp_platform_info`.

## State And Persistence Behavior

The header stores no runtime state; it is compile-time linkage only.

## Dependencies And Integration Points

It depends on the core header for shared types and is integrated by the core only under `CONFIG_DRM_CDNS_MHDP8546_J721E`.

## Risks And Test Signals

Declaration/definition mismatches show up at build or link time. Runtime validation is indirect through the J721E platform match path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cadence/cdns-mhdp8546-j721e.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chipone-icn6211.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chipone-icn6211.c

## Purpose

This driver supports the Chipone ICN6211 MIPI DSI to RGB/DPI bridge. It can be controlled either as a MIPI DSI peripheral using generic DSI reads/writes through regmap, or over I2C while creating and attaching a DSI device to the upstream host.

## Important APIs, Types, And Functions

`struct chipone` tracks regmap, bridge, panel bridge, DSI device, regulators, enable GPIO, optional refclk, and control-interface mode. Core functions are `chipone_parse_dt()`, `chipone_common_probe()`, `chipone_dsi_probe()`, `chipone_i2c_probe()`, `chipone_dsi_host_attach()`, `chipone_dsi_attach()`, `chipone_atomic_pre_enable()`, `chipone_atomic_enable()`, `chipone_atomic_post_disable()`, and `chipone_configure_pll()`.

## Control Flow

Probe parses supplies, refclk, enable GPIO, and output panel bridge. DSI-control probe initializes a custom regmap bus over generic DSI packets, adds the bridge, and attaches the existing DSI device. I2C-control probe initializes I2C regmap, adds the bridge, finds the upstream DSI host from OF graph, registers a DSI child, and attaches it. Pre-enable powers supplies/refclk/GPIO. Mode set caches the adjusted mode. Enable validates chip IDs, selects I2C/DSI config password, writes active/porch/sync timing, DSI lane count, polarity, PLL setup, and final configuration. Post-disable turns power back off.

## State And Persistence Behavior

The cached display mode and refclk rate are stored in memory. Regmap uses MAPLE cache, while the chip is reprogrammed on each atomic enable. No nonvolatile state is written.

## Dependencies And Integration Points

It integrates DRM bridge chaining, DRM OF graph, MIPI DSI, I2C, regmap, regulators, GPIO, optional clock, media bus formats, and downstream panel bridges. It returns RGB888 input bus format to the upstream source.

## Risks And Test Signals

Risks include PLL search edge cases when no best divider is found, fixed DSI rates, optional regulator error handling that logs but continues on enable failures, and different lifetime paths for DSI-control versus I2C-control instances. Test signals are chip ID reads, valid DSI lane parsing, stable pixel clock, RGB panel output, and successful remove without leaking registered DSI devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chipone-icn6211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chrontel-ch7033.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chrontel-ch7033.c

## Purpose

This I2C driver programs a Chrontel CH7033 video encoder as a DRM bridge, primarily forwarding to a downstream bridge while optionally creating a connector when the caller does not request connector-less attachment.

## Important APIs, Types, And Functions

`struct ch7033_priv` stores regmap, next bridge, bridge, and connector. Important paths are `ch7033_probe/remove()`, `ch7033_bridge_attach/detach()`, `ch7033_bridge_mode_valid()`, `ch7033_bridge_mode_set()`, `ch7033_bridge_enable/disable()`, connector detect/get-modes helpers, and `ch7033_hpd_event()`.

## Control Flow

Probe finds the downstream panel/bridge on port 1, initializes I2C regmap, validates chip/revision IDs across register pages, and adds the bridge. Attach first attaches the downstream bridge with `NO_CONNECTOR`; if a connector is requested, it initializes local connector helpers, configures polling/HPD based on downstream ops, and attaches the encoder. Mode set switches register pages and writes a long power/timing/PLL/bypass sequence derived from the mode. Enable/disable toggle reset bits on page 4.

## State And Persistence Behavior

State is volatile in regmap and connector/bridge objects. No cached mode is kept; programming happens in mode_set. Register page selection is a hardware side effect and must be correct before writes.

## Dependencies And Integration Points

The driver depends on I2C regmap, DRM bridge/connector helpers, downstream bridge EDID/detect/HPD/DDC support, and OF graph. It uses fallback no-EDID modes when downstream EDID read fails.

## Risks And Test Signals

Risks include dense undocumented register sequences, register page mistakes, ambiguous operator precedence in polarity bit expressions, connector cleanup only when a connector was initialized, and strict mode limits below 1920x1080/165 MHz. Test signals are ID/revision probe success, EDID pass-through, HPD notification from downstream bridge, accepted 1024x768 fallback, and stable HDMI/VGA-style output across modesets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/chrontel-ch7033.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cros-ec-anx7688.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cros-ec-anx7688.c

## Purpose

This lightweight I2C DRM bridge represents a ChromeOS EC-managed ANX7688 HDMI-to-DisplayPort bridge. It validates device identity and, on newer firmware, filters modes by available DP bandwidth and lane count reported by EC registers.

## Important APIs, Types, And Functions

`struct cros_ec_anx7688` stores I2C client, regmap, bridge, and a `filter` flag. The key functions are `cros_ec_anx7688_bridge_probe/remove()` and `cros_ec_anx7688_bridge_mode_fixup()`.

## Control Flow

Probe allocates the bridge, initializes 8-bit regmap, bulk-reads vendor/device IDs, rejects unexpected IDs, reads firmware version, enables mode filtering for firmware 0.85 or newer, and adds the bridge. Mode fixup returns true unless filtering is enabled; then it reads bandwidth and lane count, validates maximum supported values, computes total 8b/10b DP bandwidth, computes required 8bpc RGB bandwidth from pixel clock, and rejects modes that exceed available bandwidth.

## State And Persistence Behavior

Runtime state is only the regmap and firmware-derived `filter` boolean. No hardware programming is performed by this driver.

## Dependencies And Integration Points

It integrates as a DRM bridge with legacy `.mode_fixup`, I2C regmap, and OF compatible `"google,cros-ec-anx7688"`. It assumes EC firmware owns actual ANX7688 configuration.

## Risks And Test Signals

Risks include accepting all modes on old firmware or zero bandwidth/lane reads, fixed 8bpc RGB bandwidth calculations, and no HPD/EDID handling in this file. Test signals are correct ID/version logs, rejection of oversized modes with new firmware, and compatibility with old firmware where filtering is intentionally disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/cros-ec-anx7688.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/display-connector.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/display-connector.c

## Purpose

This platform driver models physical display connectors as terminal DRM bridges. It supplies connector type, HPD, DDC/EDID, optional connector power, and bus-format pass-through for simple DT-described connectors.

## Important APIs, Types, And Functions

`struct display_connector` stores bridge, HPD GPIO/IRQ, power regulator, and HDMI DDC-enable GPIO. Main functions are `display_connector_probe/remove()`, `display_connector_attach()`, `display_connector_detect()`, `display_connector_edid_read()`, HPD IRQ handler, and bus-format forwarding helpers.

## Control Flow

Probe derives connector type from compatible and properties, handles DVI analog/digital and HDMI type variants, enables interlace/Y420 allowances, gets optional HPD GPIO/IRQ, DDC I2C adapter, DP/HDMI power supplies, and DDC-enable GPIO, enables power, sets bridge ops according to available HPD/DDC, and adds the bridge. Attach only supports `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. Detect prefers HPD GPIO, then DDC probe, then connector-type-specific unknown/disconnected fallback. Bus format helpers forward to the previous bridge if possible or return connector/fixed fallback formats.

## State And Persistence Behavior

State is static connector resources and enabled supply/DDC GPIO. There is no mode cache or persistent storage. Remove disables DDC/power, removes the bridge, and releases DDC adapter reference.

## Dependencies And Integration Points

It depends on platform OF match data, GPIO, IRQ, regulator, I2C adapter lookup, DRM bridge EDID/detect/HPD ops, and media bus formats. It supports composite, DVI, HDMI, S-Video, VGA, and DP compatibles.

## Risks And Test Signals

Risks include resource leaks if probe fails after enabling a regulator, DP detection requiring DPCD elsewhere, connector type property errors, and fallback bus formats that may hide negotiation bugs. Test signals are HPD IRQ notifications, EDID reads over DDC, correct detection semantics per connector type, and power rails toggling on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/display-connector.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/fsl-ldb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/fsl-ldb.c

## Purpose

This driver implements Freescale/NXP LDB LVDS bridge support for i.MX6SX, i.MX8MP, and i.MX93-style syscon-controlled LVDS blocks. It connects one or two LVDS channels to a panel bridge and programs data width, bit mapping, split mode, clocking, and analog LVDS control.

## Important APIs, Types, And Functions

`struct fsl_ldb` stores bridge, panel bridge, LDB clock, syscon regmap, device data, channel enable flags, and termination option. Core functions are `fsl_ldb_probe/remove()`, `fsl_ldb_atomic_enable/disable()`, `fsl_ldb_atomic_get_input_bus_fmts()`, `fsl_ldb_mode_valid()`, and `fsl_ldb_link_frequency()`.

## Control Flow

Probe selects device data from OF, gets the `ldb` clock and parent syscon regmap, inspects ports 1/2 to determine enabled channels and panel node, creates a panel bridge, validates dual-link pixel order, and adds the bridge. Atomic enable reads negotiated LVDS output bus format, retrieves adjusted mode from connector/CRTC state, sets LDB clock to pixel clock times 7 or 3.5 for dual-link, enables the clock, writes LDB control bits, and for newer blocks writes LVDS analog control with optional termination before enabling channels. Disable clears LVDS and LDB control registers and disables the clock.

## State And Persistence Behavior

Channel availability and termination are probe-time state; clock rate and registers are programmed per enable. No persistent storage exists.

## Dependencies And Integration Points

It depends on syscon regmap, common clock framework, OF graph, panel bridge helpers, DRM bridge atomic negotiation, media bus LVDS formats, and `drm_of_lvds_get_dual_link_pixel_order()`.

## Risks And Test Signals

Risks include unsupported even-odd dual-link order, falling back to SPWG24 when downstream format is absent, exact clock-rate mismatch warnings, and SoC-specific LVDS enable polarity differences. Test signals are accepted single/dual-link modes, correct LVDS bus format, clock programming at 7x or 3.5x pixel rate, and visible panel output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/fsl-ldb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Kconfig

## Purpose

This Kconfig file declares build-time options for i.MX DRM bridge drivers under `ARCH_MXC` or `COMPILE_TEST`.

## Important APIs, Types, And Functions

It defines symbols for the shared LDB helper, legacy i.MX bridge, i.MX8MP DW HDMI bridge, HDMI PAI/PVI helpers, i.MX8QM/QXP LDB and pixel-link blocks, PXL2DPI, and i.MX93 MIPI DSI. Dependencies include OF, COMMON_CLK, DRM_IMX, IMX_SCU, and selected/implied DRM/PHY/regmap helpers.

## Control Flow

There is no runtime flow. Kconfig choices control which objects the Makefile builds and which supporting frameworks are selected. `DRM_IMX8MP_DW_HDMI_BRIDGE` implies its PAI/PVI and HDMI PHY helpers rather than selecting all unconditionally.

## State And Persistence Behavior

The only state is kernel configuration. It persists in the built kernel config and determines which drivers and symbols exist.

## Dependencies And Integration Points

This file integrates the i.MX bridge subdirectory with the kernel config system and ensures module dependencies are available for each driver.

## Risks And Test Signals

Risks include missing `select` dependencies that cause link failures, overly broad `imply` choices that omit required runtime pieces in minimal configs, and helper visibility when consumers are modular. Test signals are `allyesconfig`, `allmodconfig`, `COMPILE_TEST`, and representative i.MX defconfig builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Makefile

## Purpose

This Makefile maps i.MX DRM bridge Kconfig symbols to object files.

## Important APIs, Types, And Functions

It builds `imx-ldb-helper.o`, `imx-legacy-bridge.o`, `imx8mp-hdmi-tx.o`, `imx8mp-hdmi-pai.o`, `imx8mp-hdmi-pvi.o`, `imx8qm-ldb.o`, `imx8qxp-ldb.o`, `imx8qxp-pixel-combiner.o`, `imx8qxp-pixel-link.o`, `imx8qxp-pxl2dpi.o`, and `imx93-mipi-dsi.o` based on their `CONFIG_DRM_*` symbols.

## Control Flow

There is no runtime flow. Kbuild evaluates each `obj-$(CONFIG_...)` assignment and includes the corresponding object in the built-in or module target.

## State And Persistence Behavior

The file has no runtime state. Build output state depends entirely on the selected kernel configuration.

## Dependencies And Integration Points

It integrates with the Kconfig file in the same directory and the parent DRM bridge build. Helper symbols exported by `imx-ldb-helper.o` must be built when selected by LDB consumers.

## Risks And Test Signals

Risks are mismatches between Kconfig symbol names and Makefile object rules, which show up as missing drivers or unresolved symbols. Build tests for each symbol as built-in and module are the main signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.c

## Purpose

This helper library factors common LVDS Display Bridge channel handling for i.MX LDB drivers. It manages channel discovery, bridge registration, common attach behavior, bus-format capture, and shared LDB control-bit updates.

## Important APIs, Types, And Functions

Exported functions include `ldb_channel_is_single_link()`, `ldb_channel_is_split_link()`, `ldb_bridge_atomic_check_helper()`, `ldb_bridge_mode_set_helper()`, `ldb_bridge_enable_helper()`, `ldb_bridge_disable_helper()`, `ldb_bridge_attach_helper()`, `ldb_init_helper()`, `ldb_find_next_bridge_helper()`, `ldb_add_bridge_helper()`, and `ldb_remove_bridge_helper()`.

## Control Flow

Platform drivers allocate per-channel bridges, set `ldb->channel[]`, then call `ldb_init_helper()` to get the parent syscon regmap and discover available channel child nodes. They call `ldb_find_next_bridge_helper()` to resolve downstream bridges, then `ldb_add_bridge_helper()` to publish only available channels. During atomic operations the helper records negotiated bus formats, sets split/data-width/JEIDA bits in `ldb_ctrl`, writes the control register on enable, and clears channel mode bits on disable.

## State And Persistence Behavior

Shared mutable state is `ldb->ldb_ctrl`, channel availability, child node pointers, link type, and bus formats. It is volatile driver state with syscon register writes on enable/disable.

## Dependencies And Integration Points

It depends on syscon regmap, OF child nodes with `reg`, DRM bridge chaining, media bus LVDS formats, and exported GPL symbols used by i.MX8QM/QXP LDB drivers.

## Risks And Test Signals

Risks include stale bits accumulating in `ldb_ctrl` across repeated mode sets, invalid child `reg` handling, and requiring `NO_CONNECTOR` attach. Test signals are dual/single-link channel discovery, downstream bridge resolution, correct SPWG/JEIDA bit programming, and module symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.h

## Purpose

This header defines the shared i.MX LDB control bits, channel/base structures, link-type enum, and helper prototypes used by platform-specific LDB bridge drivers.

## Important APIs, Types, And Functions

It defines LDB channel enable masks, split-mode, 24-bit width, JEIDA mapping, VSYNC polarity bits, `MAX_LDB_CHAN_NUM`, `enum ldb_channel_link_type`, `struct ldb_channel`, `struct ldb`, `bridge_to_ldb_ch()`, and prototypes for all exported helper functions.

## Control Flow

There is no executable flow. The definitions establish how platform drivers allocate channels, store private bridge state, and call common attach/mode/enable helpers.

## State And Persistence Behavior

The header describes volatile state fields such as `link_type`, `in_bus_format`, `out_bus_format`, `is_available`, and aggregate `ldb_ctrl`. Register persistence is handled by C-file helpers and platform drivers.

## Dependencies And Integration Points

It includes Linux device/OF/regmap headers and DRM atomic, bridge, device, encoder, and modeset helper headers. It is shared by `imx-ldb-helper.c` and SoC LDB drivers such as `imx8qm-ldb.c`.

## Risks And Test Signals

The bit definitions encode hardware ABI. Incorrect masks affect all helper users. Build tests with each LDB consumer and runtime validation of single/split link programming are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-ldb-helper.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-legacy-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-legacy-bridge.c

## Purpose

This file provides a small bridge for legacy i.MX device-tree display bindings that describe fixed `display-timings` instead of a proper panel driver.

## Important APIs, Types, And Functions

`struct imx_legacy_bridge` embeds a DRM bridge, fixed display mode, and bus flags. The exported factory `devm_imx_drm_legacy_bridge()` allocates and registers the bridge. `imx_legacy_bridge_get_modes()` exposes the fixed mode and bus flags.

## Control Flow

The factory reads a DRM display mode and bus flags from OF using `of_get_drm_display_mode()`, marks the mode as driver-provided, sets bridge OF node/type/ops, and registers the bridge with device-managed cleanup. Attach only allows `DRM_BRIDGE_ATTACH_NO_CONNECTOR`. Get-modes returns the fixed mode and copies bus flags to connector display info.

## State And Persistence Behavior

The fixed mode and bus flags are cached in the bridge object for the device lifetime. No hardware is programmed and no persistent storage exists.

## Dependencies And Integration Points

It depends on DRM bridge modes ops, OF display timing helpers, and exported GPL linkage through `<drm/bridge/imx.h>`. It is intended for older i.MX IPUv3 users.

## Risks And Test Signals

Risks include preserving obsolete bindings and rejecting connector-creating attach users. Test signals are successful fixed-mode enumeration, correct bus flags, and legacy DT displays working without a panel driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx-legacy-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pai.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pai.c

## Purpose

This component driver wires the i.MX8MP HDMI Parallel Audio Interface into the DW HDMI platform data so DW HDMI can enable and disable audio through SoC-specific registers.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi_pai` stores regmap and device. `imx8mp_hdmi_pai_enable()` programs watermarks, channel count, IEC958 or PCM field selection, and starts PAI. `imx8mp_hdmi_pai_disable()` stops it. `imx8mp_hdmi_pai_bind()` maps registers, creates clocked MMIO regmap, fills `dw_hdmi_plat_data` audio hooks, and enables runtime PM.

## Control Flow

Probe registers a component. The HDMI TX master calls bind through `component_bind_all()`, passing DW HDMI platform data. Audio enable resumes runtime PM, writes extended control and field selection based on channel/width/IEC958 parameters, then sets the enable bit. Disable clears enable and releases runtime PM.

## State And Persistence Behavior

State is in regmap, device pointer, and platform data callbacks. Audio hardware state is active only between DW HDMI audio enable and disable. No persistent storage exists.

## Dependencies And Integration Points

It depends on component framework, DW HDMI platform hooks, regmap MMIO with `apb` clock, runtime PM, and ALSA IEC958 bit definitions.

## Risks And Test Signals

Risks include width assumptions limited to 24/32-bit PCM, ignoring runtime PM failure by silently returning from enable, and relying on master bind ordering. Test signals are HDMI audio playback for PCM and IEC958, runtime PM usage counts balancing, and component bind with HDMI TX.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pvi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pvi.c

## Purpose

This bridge controls the i.MX8MP HDMI TX Parallel Video Interface. It sits before the next HDMI bridge and configures LCDIF mode plus input/output sync and data-enable polarities.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi_pvi` stores bridge, device, and MMIO base. Key functions are `imx8mp_hdmi_pvi_probe/remove()`, `imx8mp_hdmi_pvi_bridge_attach()`, `imx8mp_hdmi_pvi_bridge_enable/disable()`, and `imx8mp_hdmi_pvi_bridge_get_input_bus_fmts()`.

## Control Flow

Probe maps registers, finds the downstream bridge from port 1, enables runtime PM, copies downstream timings, and adds the bridge. Attach attaches the downstream bridge. Atomic enable resumes runtime PM, obtains adjusted mode and bus flags, sets LCDIF mode/enabled, mirrors HS/VS polarity to input and output bits, applies DE-high if required, and writes control. Disable clears control and releases runtime PM. Input bus format negotiation delegates to the next bridge.

## State And Persistence Behavior

State is volatile MMIO and next-bridge reference. There is no cached mode. Runtime PM brackets active video interface programming.

## Dependencies And Integration Points

It depends on OF graph, DRM bridge chaining, runtime PM, and downstream bridge timing or atomic bus flags. It is part of the i.MX8MP HDMI TX pipeline with DW HDMI.

## Risks And Test Signals

Risks include NULL assumptions around connector/CRTC state in enable, failing if no downstream bridge is ready, and returning NULL bus formats when next bridge lacks negotiation. Test signals are correct HDMI image polarity, DE handling, runtime PM balance, and bridge-chain attach order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-pvi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-tx.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-tx.c

## Purpose

This driver adapts the generic Synopsys DW HDMI bridge to the i.MX8MP HDMI TX block. It provides mode validation, PHY ops, optional component binding for the audio PAI block, and probe/remove glue.

## Important APIs, Types, And Functions

`struct imx8mp_hdmi` stores DW HDMI platform data, returned `dw_hdmi`, and pixel clock. Important functions are `imx8mp_hdmi_mode_valid()`, `im8mp_hdmi_phy_setup_hpd()`, `imx8mp_dw_hdmi_probe/remove()`, `imx8mp_dw_hdmi_bind/unbind()`, and system resume.

## Control Flow

Probe gets the pixel clock, fills DW HDMI platform data, and checks graph port 2 for the optional PAI component. Without PAI it probes DW HDMI immediately; with PAI it registers as component master and probes DW HDMI after child components bind. Mode validation rejects below 13.5 MHz, above 297 MHz, pixel clocks the generator cannot round within 0.5 percent, double-clocked modes, and interlaced modes. PHY setup releases PHY reset and delegates HPD handling to DW HDMI helpers.

## State And Persistence Behavior

State is in the private struct and DW HDMI core object. No hardware mode state is cached here; DW HDMI and PHY drivers manage detailed registers. Resume calls `dw_hdmi_resume()`.

## Dependencies And Integration Points

It depends on common clocks, component framework, DW HDMI bridge library, OF graph, and the Samsung HDMI PHY via forced vendor PHY ops. PAI integration is optional through graph port 2.

## Risks And Test Signals

Risks include mode rejection due to strict pixel-clock rounding, duplicate graph lookup in remove, no suspend work beyond resume, and dependency on component ordering for audio. Test signals are DW HDMI probe success, HPD detection, mode validation for common CEA/VESA modes, resume after system sleep, and HDMI audio when PAI is present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8mp-hdmi-tx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qm-ldb.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qm-ldb.c

## Purpose

This driver implements the i.MX8QM LVDS Display Bridge, also called pixel mapper, using the shared i.MX LDB helper plus LVDS PHY configuration. It supports single-link and odd-even dual-link LVDS output.

## Important APIs, Types, And Functions

`struct imx8qm_ldb_channel` extends `ldb_channel` with a PHY. `struct imx8qm_ldb` embeds `struct ldb`, channel pointers, pixel/bypass clocks, and active channel. Key paths are `imx8qm_ldb_probe/remove()`, `imx8qm_ldb_bridge_atomic_check()`, `imx8qm_ldb_bridge_mode_set()`, `imx8qm_ldb_bridge_atomic_enable/disable()`, bus-format negotiation helpers, and runtime resume.

## Control Flow

Probe allocates two bridge channels, gets pixel and bypass clocks, initializes the common LDB, validates available channels and dual-link odd-even order, gets per-channel LVDS PHYs, resolves downstream bridges, enables runtime PM, and adds bridges for available channels. Atomic check records bus formats and validates primary and, for split mode, slave PHY LVDS settings. Mode set resumes runtime PM, initializes/configures PHYs, sets clocks to adjusted pixel clock, programs sync polarity and data-width bits, then delegates common LDB control setup. Enable starts clocks, sets channel-to-DI routing, powers PHYs, and writes LDB control. Disable reverses helper control, PHY power, clocks, and runtime PM.

## State And Persistence Behavior

State includes active channel number, link type, cached `ldb_ctrl`, per-channel availability, bus formats, PHY handles, and clocks. Runtime resume resets the LDB control register to POR default. No persistent storage exists.

## Dependencies And Integration Points

It depends on `imx-ldb-helper`, DRM bridge atomic helpers, OF graph dual-link parsing, generic LVDS PHY API, syscon regmap, clocks, runtime PM, and media bus formats.

## Risks And Test Signals

Risks include only accepting odd-even dual-link order, accumulating control bits across mode sets, error paths that log but continue after PM/PHY/clock failures, and split-mode slave PHY configuration tied to `active_chno ^ 1`. Test signals are PHY validate/configure success, single and dual-link LVDS output, correct SPWG/JEIDA negotiation, runtime PM reset behavior, and clock/PHY balance on disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/imx/imx8qm-ldb.c -->
