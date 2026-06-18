# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm DP/DSI research for subset-b-003653

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.c

Purpose: This is the top-level Qualcomm MSM DisplayPort/eDP platform driver. It binds the DP device into the MSM DRM component graph, allocates AUX/link/panel/ctrl/audio submodules, maps the DP register regions, owns HPD state handling, and exports the DRM bridge callbacks implemented through `dp_drm.c`.

Important APIs and types: `struct msm_dp_display_private` is the persistent per-controller state: IRQ, controller id, runtime flags, DRM device, AUX/link/panel/ctrl/audio handles, cached mode, `struct msm_dp`, HPD event queue, mapped AHB/AUX/link/P0 register windows, and audio completion. `struct msm_dp_desc` maps SoC IO bases to controller ids and wide-bus capability. Exported entry points include `msm_dp_register()`, `msm_dp_unregister()`, `msm_dp_modeset_init()`, bridge callbacks, PSR/debug/snapshot helpers, audio completion helpers, and mode/mode-test accessors.

Control flow: probe selects an SoC descriptor by MMIO start, derives DP versus eDP from `aux-bus/panel`, maps either split or legacy register windows, creates submodules, enables runtime PM, requests IRQ, and adds a component directly for DP or after AUX-bus population for eDP. Component bind registers AUX, stores the display in `priv->kms->dp[id]`, and starts `dp_hpd_handler`. HPD IRQs enqueue plug, unplug, replug, or IRQ_HPD events. The thread serializes them through `event_mutex`, moves among disconnected, mainlink-ready, connected, disconnect-pending, and display-off states, runs runtime PM, powers PHY, reads DPCD/EDID, trains the link, and sends DRM HPD notifications. Atomic enable sets the cached mode, optionally retrains from display-off/eDP, enables stream, posts audio/PSR setup, and marks connected; post-disable tears down stream/link/PHY and releases runtime PM.

State and persistence: driver state is devm-managed except submodule put/free paths and EDID/audio handles owned by submodules. HPD events are a fixed ring protected by a spinlock, while display state transitions and register snapshots use `event_mutex`. Persistent booleans include `core_initialized`, `phy_initialized`, `link_ready`, `power_on`, `internal_hpd`, `psr_supported`, and audio support/enabled state. The module parameter `psr_enabled` gates PSR use.

Dependencies and integration: It depends on Linux component, runtime PM, DRM bridge/connector/EDID helpers, DP AUX-bus, PHY, MSM KMS, `dp_aux`, `dp_link`, `dp_panel`, `dp_ctrl`, `dp_audio`, and `dp_debug`. It integrates with external bridges/panel bridges, DRM HPD, HDMI audio notifications, self-refresh PSR, and MSM display snapshots.

Risks and test signals: The tightest risks are HPD race handling, ring overflow under interrupt storms, missing runtime PM puts on error paths in bridge enable, stale state after link-training failure, split-versus-legacy MMIO mapping regressions, eDP AUX-bus probe ordering, and unplug while audio is active. Test signals include DP/eDP hotplug/replug/unplug, IRQ_HPD link-status/test requests, branch-device sink-count transitions, EDID failure while disconnected, runtime suspend/resume, PSR enter/exit, audio prepare/shutdown completion, wide-bus/YUV420 modes, snapshot with power off, and multi-controller SoC IO selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.h

Purpose: This header defines the public DP display object shared with MSM KMS, bridge code, audio, and panel/encoder initialization. It is the stable contract around the private orchestration implemented in `dp_display.c`.

Important APIs and types: `struct msm_dp` carries the platform device, DRM device, connector, next bridge, audio handle, connector type, link/power/audio booleans, internal HPD state, eDP flag, and PSR flag. `DP_MAX_PIXEL_CLK_KHZ` caps mode validation at 675 MHz before wide-bus or YUV420 halving. Function declarations expose mode enumeration, test-pattern state, test bpp, audio start/complete signaling, PSR control, and debugfs initialization.

Control flow and state: This header does not implement flow, but its fields are read and written across probe/bind, HPD notification, atomic bridge enable/disable, audio callbacks, debugfs, and mode validation. `link_ready` drives connector detection; `power_on` gates duplicate enable/disable and snapshots; `audio_enabled` coordinates audio shutdown wait; `internal_hpd` suppresses external HPD notifications when the DP block owns HPD; `is_edp` switches bridge behavior and AUX-bus handling.

Dependencies and integration: It includes DRM connector types and `dp_audio.h`, tying the display object to DRM bridge connector setup and HDMI/DP audio helpers. It is included by `dp_drm.h` and other MSM display code that stores `kms->dp[id]`.

Risks and test signals: Because this structure is shared rather than opaque, field semantics must remain synchronized with `dp_display.c` and `dp_drm.c`. Tests should cover public state transitions: `link_ready` after HPD, `power_on` after atomic enable/disable, audio completion paths, eDP PSR state, and mode validation against `DP_MAX_PIXEL_CLK_KHZ`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_display.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.c

Purpose: This file adapts MSM DP/eDP display logic to DRM bridge and bridge-connector APIs. It separates DP-specific HPD/detect/audio operations from eDP self-refresh behavior while delegating actual hardware sequencing to `dp_display.c`.

Important APIs and functions: DP bridge ops include detect, atomic check, get modes, debugfs init, HPD enable/disable/notify, audio prepare/shutdown, and the generic atomic/mode callbacks exported by `dp_display.c`. eDP bridge ops wrap atomic enable/disable/post-disable to enter or exit PSR around CRTC self-refresh transitions and use a looser mode-valid path because panel drivers provide supported eDP modes. `msm_dp_bridge_init()` allocates `struct msm_dp_bridge`, sets bridge type and YUV420 capability, attaches DP audio metadata for external DP, registers and attaches the bridge, and optionally attaches `next_bridge`. `msm_dp_drm_connector_init()` creates a bridge connector and DP subconnector property for pluggable DP.

Control flow: During modeset init, `dp_display.c` calls `msm_dp_bridge_init()` then connector init. For DP, DRM detect reads `dp->link_ready`; get_modes returns cached EDID modes only after HPD. Atomic check rejects commits on HPD-capable bridges when unplugged to avoid disabling already-dead hardware. For eDP, atomic check marks connector self-refresh-aware if PSR is supported; atomic disable enters PSR when the new CRTC state requests self-refresh, exits PSR on disable from self-refresh, and skips full post-disable while self-refresh remains active.

State and dependencies: It uses `struct msm_dp` fields plus DRM atomic/bridge state. Dependencies are DRM bridge connector helpers, DRM atomic helpers, MSM KMS, DP audio, and DP display exports.

Risks and test signals: Risks include incorrect HPD rejection causing userspace modeset failures, eDP PSR entry/exit ordering, bridge attachment order with external panel bridges, and audio metadata only being set for external DP. Test with hotplug detect/get_modes, unplug while CRTC active, eDP self-refresh commits, external bridge attach, DP audio prepare/shutdown, and YUV420 mode allowance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.h

Purpose: This header is the DRM bridge interface for the MSM DP driver. It exposes the bridge wrapper type, connector creation, bridge initialization, and callbacks implemented across `dp_drm.c` and `dp_display.c`.

Important APIs and types: `struct msm_dp_bridge` embeds `struct drm_bridge` and points back to `struct msm_dp`. `to_dp_bridge()` performs `container_of` conversion. Declarations cover `msm_dp_drm_connector_init()`, `msm_dp_bridge_init()`, atomic enable/disable/post-disable, mode validation, mode set, HPD enable/disable, and HPD notify.

Control flow and integration: `dp_drm.c` allocates this bridge wrapper and installs either DP or eDP bridge functions. `dp_display.c` implements several declared callbacks because they require private display state and hardware sequencing. The header therefore forms a cross-file contract between generic DRM bridge glue and the DP display controller implementation.

Dependencies and state: It includes Linux types, DRM bridge, `msm_drv.h`, and `dp_display.h`. It does not own state but makes the `msm_dp` pointer reachable from DRM callbacks.

Risks and test signals: The main risk is signature drift between bridge funcs and exported implementations, especially as DRM bridge APIs evolve. Compile coverage is the primary signal, supplemented by runtime bridge attach, mode set, HPD callbacks, and eDP/DP split behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_drm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.c

Purpose: This file owns DisplayPort link-side sink communication over AUX: DPCD power management, automated compliance test parsing, sink-count/link-status processing, requested voltage/pre-emphasis adjustment, lane-map/link-rate DT parsing, and link object construction.

Important APIs and types: `struct msm_dp_link_private` wraps public `struct msm_dp_link`, AUX, DRM device, previous sink count, PSM mutex, current DPCD link status, and a private test request. Exported functions include `msm_dp_link_process_request()`, `msm_dp_link_send_test_response()`, `msm_dp_link_send_edid_checksum()`, `msm_dp_link_psm_config()`, `msm_dp_link_adjust_levels()`, `msm_dp_link_get_colorimetry_config()`, `msm_dp_link_reset_phy_params_vx_px()`, `msm_dp_link_get_test_bits_depth()`, and `msm_dp_link_get()`.

Control flow: HPD-high/IRQ paths call `msm_dp_link_process_request()`. It resets transient test state, reads sink count and link status, parses service IRQ/test request bytes, and classifies the sink request as EDID read, downstream-port change, link training, PHY test pattern, PSR error/capability change, link-status update, video pattern, or audio pattern. Link-training and PHY-test requests update public `link_params` so the controller can retrain at the sink-requested rate and lane count. PSM config writes DPCD `DP_SET_POWER` D0/D3 under a mutex. DT parsing chooses max lane count from endpoint or legacy `data-lanes`, creates a four-entry logical-to-physical lane map, and derives max link rate from endpoint `link-frequencies` with HBR2 default.

State and dependencies: Persistent public state includes LTTPR caps/count, sink request/test response, sink count, test video/audio structs, PHY params, link params, lane map, and device limits. It depends on DRM DP helper DPCD routines, OF graph helpers, and `dp_panel.h` validation helpers.

Risks and test signals: Risks include AUX read/write failures being flattened to `-EINVAL`, compliance tests with unsupported patterns, lane-map partial DT definitions, link-frequency conversion, PSR IRQ side effects, and link-status retrain classification. Test signals include DP CTS automated link/video/audio/EDID/PHY tests, branch-device sink-count changes, low-power DPCD transitions, multi-lane remapping, LTTPR-limited links, and voltage/pre-emphasis adjustment across all lanes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.h

Purpose: This header defines the public DP link model consumed by DP controller, panel, and display orchestration code.

Important APIs and types: `struct msm_dp_link_info` stores DPCD revision, active rate, supported eDP rates, rate-set index, lane count, and enhanced framing capabilities. `struct msm_dp_link_test_video`, `struct msm_dp_link_test_audio`, and `struct msm_dp_link_phy_params` capture automated-test data. `struct msm_dp_link` aggregates LTTPR caps/count, sink request/response, sink count, test structs, link params, lane map, max lane count, and max link rate. `msm_dp_link_bit_depth_to_bpp()` converts DP test bit depth values to RGB bpp. Public functions cover request processing, colorimetry, level adjustment, PSM, test response/checksum, and object creation.

Control flow and state: The header’s state is populated by `dp_panel.c` during DPCD sink-cap reads, by `dp_link.c` during HPD IRQ parsing, and by `dp_ctrl.c` during link training. `sink_request` is the main handoff from AUX parsing to display/controller code.

Dependencies and integration: It includes `dp_aux.h` and DRM DP helper definitions. It is included by DP display, panel, and control layers, so it forms the common contract for negotiated link capabilities and compliance-test parameters.

Risks and test signals: Risks are mainly ABI-like within the driver: changing enum/field semantics can break link training or compliance tests. Test with all supported lane counts/rates, 6/8/10 bpc test patterns, PHY pattern requests, and lane-map programming in the controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_link.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.c

Purpose: This file represents sink/panel capability and timing programming for MSM DP. It reads DPCD/EDID, derives link capabilities, chooses mode bpp, programs mainlink timing and P0 interface timing/test pattern registers, handles EDID test checksums, and manages VSC SDP for YUV420.

Important APIs and functions: Public functions include `msm_dp_panel_read_sink_caps()`, `msm_dp_panel_get_mode_bpp()`, `msm_dp_panel_get_modes()`, `msm_dp_panel_handle_sink_request()`, `msm_dp_panel_timing_cfg()`, `msm_dp_panel_init_panel_info()`, TPG config, DSC DTO clear, VSC SDP enable/disable, get, and put. Private state lives in `struct msm_dp_panel_private`, which wraps public `struct msm_dp_panel`, AUX, link, MMIO bases, and `panel_on`.

Control flow: On HPD high, display code calls `read_sink_caps()`. It reads DPCD, detects VSC SDP support, parses eDP 1.4 link-rate tables or falls back to MAX_LINK_RATE, applies DT and LTTPR rate/lane limits, notes enhanced framing, reads PSR caps, validates rate/lane/bw code, reads branch downstream info, and refreshes EDID. Mode validation and mode set call bpp selection, which lowers bpp in 6-bit steps until bandwidth fits. Stream enable calls `timing_cfg()`, which writes total/sync/active timing registers, toggles P0 wide-bus, optionally builds a DP 1.4 VSC SDP for YUV420, and marks the panel on. EDID automated tests send checksum plus response through `dp_link`.

State and dependencies: Persistent public state includes raw DPCD, downstream port bytes, link info, cached `drm_edid`, connector pointer, mode, PSR caps, video-test flag, VSC support, hardware revision, and max bandwidth code. It depends on DRM EDID/DP helpers, MMIO register constants, and `dp_utils` SDP parity packing.

Risks and test signals: Risks include EDID lifetime, branch-device unplug during EDID read, eDP supported-rate parsing versus `LINK_BW_SET`, LTTPR limits, incorrect YUV420/VSC SDP enablement, wide-bus toggling, mode bpp underflow, and test-pattern timing math. Test with DP/eDP DPCD variants, MST/branch sink counts, EDID failure, 420-only modes, PSR-capable eDP, TPG enable/disable, and DP CTS EDID/video-pattern requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.h

Purpose: This header defines the public DP panel/sink capability model and timing API used by display and controller code.

Important APIs and types: `struct msm_dp_display_mode` wraps a DRM mode with selected bpp, sync polarities, and YUV420 output flag. `struct msm_dp_panel_psr` stores PSR version/capabilities. `struct msm_dp_panel` stores DPCD, downstream ports, negotiated link info, cached EDID, connector, selected mode, PSR capabilities, video-test state, VSC support, hardware revision, and max bandwidth code. Inline helpers validate DP link rate and lane count. Public functions read sink capabilities, initialize mode info, configure timing, expose EDID modes, respond to sink requests, drive TPG, manage DSC DTO and VSC SDP, and allocate/free the panel object.

Control flow and state: `dp_display.c` populates and consumes this structure during HPD, mode validation, mode set, and stream enable. `dp_ctrl.c` relies on `link_info` and timing data for link training and stream setup. `dp_panel.c` owns EDID lifetime and mode-derived panel state.

Dependencies and integration: It includes DRM modes/MSM DRM, `dp_aux.h`, and `dp_link.h`, making it the sink-facing bridge between AUX/link negotiation and register programming.

Risks and test signals: Risks are shared mutable fields such as `drm_edid`, `video_test`, and `vsc_sdp_supported`. Compile and runtime testing should cover lane/rate validation, bpp selection, EDID mode enumeration, YUV420 SDP enablement, and PSR capability propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_panel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_reg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_reg.h

Purpose: This header is the DP controller register map and bitfield catalog used by MSM DP AUX, controller, panel, audio, PSR, SDP, TPG, DSC, and HDCP code.

Important contents: It defines offsets and masks for AHB/global registers (`REG_DP_HW_VERSION`, reset, PHY, clocks, interrupt status/masks), HPD block registers and interrupt bits, AUX transaction/data/status registers, mainlink control/configuration/training/timing registers, MISC colorimetry/VSC bits, lane mapping, ready/level/TU registers, audio packet/timing/infoframe registers, SDP generic/VSC registers, P0 interface timing and TPG registers, DSC DTO, PHY AUX interrupt registers, and DP HDCP/security offsets.

Control flow and integration: The constants are consumed by `dp_display.c` for IRQ status and snapshots, `dp_panel.c` for timing/VSC/TPG/DSC DTO programming, `dp_ctrl.c` for reset/link training/video enable/PSR, `dp_aux.c` for AUX/HPD programming, and `dp_audio.c` for audio packet setup. Register grouping mirrors the driver’s split MMIO windows: AHB, AUX, link, and P0.

State and persistence: The header has no runtime state, but its offsets define persistent hardware state layout. Because split and legacy MMIO mapping both use these offsets, offset errors have broad hardware impact.

Risks and test signals: Risks include SoC revision mismatches, incorrect bit masks during new hardware support, field overlap, and silent hardware hangs from wrong reset/clock/interrupt bits. Test signals are register snapshot sanity, AUX transactions, HPD IRQ ack/mask behavior, link training, audio playback, VSC SDP updates, TPG output, PSR interrupts, and HDCP register users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.c

Purpose: This file provides small DP utility routines for secondary data packet header parity and packing. Its current user is VSC SDP programming in `dp_panel.c`.

Important APIs and functions: `msm_dp_utils_get_g0_value()` and `msm_dp_utils_get_g1_value()` compute the two nibble transforms used by the DP SDP parity algorithm. `msm_dp_utils_calculate_parity()` processes either a byte or wider header value as nibbles and returns the parity byte. `msm_dp_utils_pack_sdp_header()` packs HB0-HB3 and their parity bytes into two 32-bit words using masks from `dp_utils.h`.

Control flow and state: The functions are pure and have no persistent state. `dp_panel.c` calls `pack_sdp_header()` before writing `MMSS_DP_GENERIC0_0/1`, then writes SDP payload words separately. The parity helper is intentionally isolated so SDP header packing stays consistent for future generic SDP users.

Dependencies and integration: It uses Linux types and `FIELD_PREP`/GENMASK definitions through the header. It depends on `struct dp_sdp_header` from DRM DP helpers.

Risks and test signals: The main risk is parity or packing bit-order regressions, which would make VSC SDP invalid and break YUV420 signaling. Unit-level signals can compare known HB values to expected parity and packed words. System signals include YUV420 modes on DP sinks requiring VSC SDP and DP analyzer/CTS SDP validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.h

Purpose: This header exposes SDP header parity/packing helpers and the bit masks used to pack four DP SDP header bytes plus parity into two hardware words.

Important APIs and types: It defines header/parity bit positions and GENMASK fields for HB0-HB3 and parity bytes, then declares `msm_dp_utils_get_g0_value()`, `msm_dp_utils_get_g1_value()`, `msm_dp_utils_calculate_parity()`, and `msm_dp_utils_pack_sdp_header()`.

Control flow and integration: The header is included by `dp_panel.c` to pack VSC SDP headers before MMIO writes. It includes Linux bitfield helpers and DRM DP helper definitions for `struct dp_sdp_header`.

State and risks: No state is owned here. The risk is that mask definitions must match the hardware word layout expected by the DP link block. Compile testing and runtime VSC SDP/YUV420 validation are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.c

Purpose: This is the MSM DSI platform driver and component glue. It creates the DSI host, finds the associated DSI PHY, registers with the global DSI manager, binds into MSM KMS, and exposes modeset/snapshot helpers.

Important APIs and functions: Public helpers include `msm_dsi_is_cmd_mode()`, `msm_dsi_get_dsc_config()`, `msm_dsi_wide_bus_enabled()`, `msm_dsi_register()`, `msm_dsi_unregister()`, `msm_dsi_modeset_init()`, and `msm_dsi_snapshot()`. Probe uses `dsi_init()`, which allocates `struct msm_dsi`, initializes the host, resolves the PHY from the `phys` phandle, and registers with `dsi_manager`. Component bind gets the external bridge for standalone or bonded-master DSI and stores the DSI pointer in `priv->kms->dsi[id]`.

Control flow: Driver registration also registers DSI PHY platform drivers. Probe tolerates `-ENODEV` as an absent port but otherwise propagates defers/errors. Attach/detach are component add/del wrappers called from host attach/detach. Modeset init initializes host modeset resources and skips connector creation for bonded slave links. Unbind frees TX buffers and removes KMS references. Destroy unregisters manager/host and releases the PHY device reference.

State and dependencies: `struct msm_dsi` persists device, host, PHY, optional TE source, next bridge, PHY device reference, PHY-enabled flag, and id. It depends on OF platform, DRM bridge lookup, MSM KMS, DSI host/manager/PHY APIs, and runtime PM ops implemented in `dsi_host.c`.

Risks and test signals: Risks include PHY probe deferral, reference leaks around `of_find_device_by_node`, missing next bridge on master links, bonded slave connector suppression, and cleanup ordering when host init partially fails. Test signals include standalone and bonded DSI probe, absent-panel probe, component bind/unbind, mode init for master/slave, command-mode detection, DSC/wide-bus accessors, and snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.h

Purpose: This header is the central public contract for MSM DSI core, manager, host, and PHY integration.

Important APIs and types: It defines DSI ids (`DSI_0`, `DSI_1`, `DSI_MAX`), PHY use cases for standalone/master/slave, `struct msm_dsi`, shared PHY timing and clock request structs, manager functions, host functions, and PHY driver/control functions. Host declarations cover command transfer, power, IRQ, mode, DSC checks, registration, clocks, TX buffers, snapshots, and test patterns.

Control flow and state: `struct msm_dsi` is the per-controller object shared across driver, manager, host, PHY, and KMS. The manager uses ids and PHY use cases for bonded configuration. Host functions take `mipi_dsi_host *`, allowing MIPI DSI core callbacks to use MSM-specific implementation through `container_of`.

Dependencies and integration: It includes platform/OF and DRM bridge/CRTC/MIPI DSI headers plus MSM display snapshot support. It is included by `dsi.c`, `dsi_manager.c`, `dsi_host.c`, `dsi_cfg.c`, and PHY code.

Risks and test signals: The header exposes a wide internal surface, so signature or state changes can affect multiple layers. Compile coverage is essential; runtime signals include host registration, panel attach/detach, command transfers, PHY enable/disable, bonded DSI, DSC/wide-bus, and mode validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.c

Purpose: This file maps DSI hardware versions to SoC-specific resource configuration and host operation tables. It is the compatibility matrix for regulators, bus clocks, register offset shifts, controller IO starts, and version-specific implementation callbacks.

Important APIs and data: Static `struct msm_dsi_config` entries cover APQ8064, MSM8974/APQ8084, MSM8916, MSM8976, MSM8994, MSM8996, MSM8998, SDM660, SDM845/QCM/SM variants, SC7280, SA8775P, SM8550, SM8650, and Kaanapali. Host ops select v2, 6G, 6G-v2, or 6G-v2.9 behavior for link clock setup/enable/disable, optional clock initialization, TX buffer allocation/access, DMA base lookup, and clock-rate calculation. `msm_dsi_cfg_get()` searches handlers from newest to oldest for an exact major/minor match.

Control flow: `dsi_host.c` reads hardware version registers, calls `msm_dsi_cfg_get()`, identifies controller id by matching the `dsi_ctrl` resource start against `io_start`, applies `io_offset`, gets regulators/clocks, and dispatches host behavior through the selected ops table.

State and dependencies: The file is static data with no runtime mutation. It depends on regulator bulk data types and host functions declared in `dsi.h`.

Risks and test signals: Risks include missing hardware version entries, wrong regulator loads, bus clock names, IO starts, or ops selection. A wrong `io_offset` shifts every register access. Test signals include probe across supported SoCs, regulator/clock acquisition, id detection for DSI0/DSI1, v2 versus 6G TX buffer behavior, OPP rate votes, and v2.9 clock reparenting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.h

Purpose: This header defines MSM DSI hardware version constants, resource configuration structures, operation tables, and the configuration lookup API.

Important APIs and types: It declares major versions for v2 and 6G, many 6G minor version constants from v1.0 through v2.10, `DSI_6G_REG_SHIFT`, `VARIANTS_MAX`, `struct msm_dsi_config`, `struct msm_dsi_host_cfg_ops`, `struct msm_dsi_cfg_handler`, and `msm_dsi_cfg_get()`. The ops table abstracts hardware-generation differences in clock control, TX buffer management, DMA base retrieval, and clock-rate calculation.

Control flow and integration: `dsi_host.c` calls the lookup after reading hardware version registers, then uses the returned config for regulators, bus clocks, IO start/id matching, register offset shift, and host operation dispatch.

State and risks: No runtime state is owned. Risks are version constant mismatch and callback contract drift. Compile testing and hardware probe on each supported generation are the primary signals, with additional coverage for optional `clk_init_ver` and `tx_buf_put` callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_cfg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_host.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_host.c

Purpose: This is the hardware-facing MSM DSI host implementation. It handles version detection, MMIO, regulators, clocks/OPP votes, runtime PM, MIPI DSI host registration, command DMA TX/RX, IRQ/error handling, timing and DSC programming, PHY clock requests, power sequencing, and snapshots/test patterns.

Important APIs and types: `struct msm_dsi_host` is the persistent host state: MIPI host base, platform/DRM devices, id, register base/size, supplies, bus/link clocks, rates, config handler, completions, mutexes/spinlock, error workqueue, TX buffers for GEM or coherent DMA, RX buffer, SFPB regmap, display mode, DSC pointer, attached device format/lanes/mode flags, lane swap, C-PHY flag, saved DMA command control, registration/power/enabled flags, and IRQ. Public APIs implement host init/destroy/register, modeset init, power on/off, enable/disable, command xfer prepare/restore/TX/RX/commit, IRQ control, PHY mode/reset/clock request, clock ops, TX buffer ops, mode setting, DSC checking, mode flags, snapshots, and TPG.

Control flow: Init parses DT endpoint lane map/TE source/SFPB, maps `dsi_ctrl`, enables runtime PM, reads version under AHB clock, selects config, identifies DSI id by MMIO start, applies register shift, gets regulators/clocks/OPP/IRQ, and creates workqueue/completions/locks. Panel attach stores channel/lanes/format/mode flags/DSC and component-attaches the DSI device. Bridge power-on enables PHY via the manager, then host power-on enables regulators, runtime PM, link clocks, pinctrl, timing setup, SW reset, and controller config. Enable toggles video or command mode. Command transfer prepares clocks and command mode, builds MSM command DMA packets, triggers one or both hosts via manager, waits on DMA completion, reads RDBK registers for RX, then restores state.

State and persistence: Mode copies are allocated and replaced in `set_display_mode()`. `power_on` and `enabled` gate command transfer and disable behavior. `dma_comp`/`video_comp` synchronize IRQ completions. `err_work_state` accumulates error classes until workqueue reset/re-enable. TX buffers persist for modeset lifetime; RX buffer is devm 4 KiB.

Dependencies and integration: It depends on Linux clocks, regulators, PM OPP, pinctrl, IRQs, DMA/GEM/VM, syscon/regmap, DRM DSC helpers, OF graph, MIPI DSI core, MSM GEM/KMS, generated DSI/SFPB register headers, DSI config, and DSI PHY.

Risks and test signals: High-risk areas include clock-rate math for DSC/bonded/C-PHY/wide-bus, v2 versus 6G buffer/DMA paths, command RX chunking and repeated-byte handling, IRQ ack/mask races, error reset during underflow, runtime PM imbalance, register shift/id detection, lane-map validation, and DSC parameter mutation. Test with video and command panels, long/short DCS reads, synchronized bonded DSI, DSC slice constraints, RGB101010, C-PHY, OPP table absent/present, suspend/resume, underflow/error IRQs, TPG, and snapshots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_host.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_manager.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_manager.c

Purpose: This file coordinates one or two DSI controllers as a DRM bridge-facing display output. It owns global DSI pairing state, bonded/synchronized DSI handling, PHY use-case sequencing, bridge power/mode callbacks, connector creation, and cross-host command synchronization.

Important APIs and types: `struct msm_dsi_manager` stores `dsi[2]`, bonded flag, sync-needed flag, and master link id. `struct dsi_bridge` wraps `drm_bridge` with a DSI id. Public APIs include connector init, command xfer, command trigger, register/unregister, TPG enable, and bonded/master queries. Private helpers parse OF `qcom,dual-dsi-mode`, `qcom,master-dsi`, and `qcom,sync-dual-dsi`, register hosts in correct order, enable/disable PHYs, and power bridge hosts.

Control flow: On manager register, a DSI instance is stored globally, OF pairing state is merged, and host registration is performed. Standalone mode sets PHY standalone and registers one host. Bonded mode waits for the other DSI, sets PLL master/slave use cases, registers slave host first, then master. DRM pre-enable on the master powers PHY/host(s), enables IRQs, then enables host(s). Post-disable disables hosts/IRQs, saves PHY PLL state, powers off host(s), and disables PHY when both sides are off. Mode set programs both hosts in bonded mode. Mode valid checks OPP availability for byte-clock rate then delegates DSC validation to host. Command transfer optionally prepares both hosts but only triggers when the synchronized master path runs.

State and dependencies: State is global, not per DRM device, so only one two-DSI group is represented. It depends on DRM bridge connector helpers, PM OPP, MSM KMS, DSI host/PHY APIs, and OF properties.

Risks and test signals: Risks include global state lifetime across unregister/reprobe, ordering assumptions that DSI1 is encoder master, bonded PHY enable rollback, synchronized command suppression on DSI0, missing external bridge on slave, and OPP mode validation edge cases. Test standalone DSI0/DSI1, bonded master/slave probe orders, sync-dual command writes, reads bypassing sync, panel prepare/unprepare command access, PHY PLL save/restore, and mode validation with/without OPP tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dsi/dsi_manager.c -->
