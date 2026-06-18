# subset-b-003591 research

Grouped research for the DisplayPort AUX backlight, AUX register, HDCP, link training, MST, compliance test, and DP tunnel files under `sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.c

## Purpose
Implements eDP backlight control over DisplayPort AUX for i915. It selects between Intel's proprietary HDR/nits AUX backlight interface, the standard VESA eDP AUX backlight interface, and PWM fallback paths when AUX controls only part of the panel backlight behavior.

## Important APIs, types, and functions
- `intel_dp_aux_init_backlight_funcs()` is the exported initializer used by the backlight core to install either `intel_dp_hdr_bl_funcs` or `intel_dp_vesa_bl_funcs` in `panel->backlight.funcs`.
- `enum intel_dp_aux_backlight_modparam` mirrors `i915.enable_dpcd_backlight` modes: auto, off, on, force VESA, and force Intel.
- Intel HDR path: `intel_dp_aux_supports_hdr_backlight()`, `intel_dp_aux_hdr_setup_backlight()`, `intel_dp_aux_hdr_enable_backlight()`, `intel_dp_aux_hdr_set_backlight()`, `intel_dp_aux_hdr_get_backlight()`, `intel_dp_aux_hdr_disable_backlight()`.
- VESA path: `intel_dp_aux_supports_vesa_backlight()`, `check_if_vesa_backlight_possible()`, `intel_dp_aux_vesa_setup_backlight()`, `intel_dp_aux_vesa_enable_backlight()`, `intel_dp_aux_vesa_set_backlight()`, `intel_dp_aux_vesa_get_backlight()`, `intel_dp_aux_vesa_disable_backlight()`.
- Uses `struct intel_panel` state including `panel->backlight.edp.intel_cap`, `panel->backlight.edp.vesa.info`, luminance min/max/level, PWM helper callbacks, and VBT backlight type.

## Control flow
Initialization first evaluates the module parameter and VBT backlight type. In auto mode it probes Intel AUX only when VBT says the panel uses Display DDI/PWM style backlight and probes VESA directly when VBT advertises the VESA eDP AUX interface. Forced modes override this. The Intel proprietary interface is probed first because writing Intel OUI state can make broken VESA implementations stop responding correctly.

The Intel HDR probe waits for Intel source OUI, reads four bytes at the proprietary TCON capability block, checks interface version and nits brightness capability, and usually requires HDR static metadata from EDID unless the user forced the Intel path. Setup configures PWM when SDR brightness is not AUX-driven, sets min/max luminance from EDID luminance range or a default 0..512 range, writes panel luminance override, and snapshots the current level. Enable reads the current TCON control byte, chooses AUX or PWM brightness for the current HDR/SDR mode, fills HDR TCON bits, writes the control byte only if it changed, and writes content luminance metadata in HDR mode.

The VESA probe first accepts luminance-plus-smooth-brightness capable panels, otherwise requires both AUX enable and AUX brightness set support plus sane PWM bit count capability. Setup calls `drm_edp_backlight_init()`, initializes PWM if AUX does not cover enable or set operations, then derives user-facing brightness range and current enabled/level state from VESA info and current mode. Set/enable/disable combine DRM eDP AUX helpers with PWM fallback where needed.

## State and persistence
Runtime state is kept on the connector panel: chosen function table, Intel capability bits, VESA helper info, luminance support flag, min/max/level/enabled, and PWM state. It persists while the connector object lives and is refreshed by setup and enable calls. The file also writes sink-side DPCD registers that persist in the panel until changed or reset: Intel TCON control, brightness nits, content luminance, panel luminance override, and VESA backlight registers through DRM helpers.

## Dependencies and integration points
Depends on DRM DP AUX/DPCD helpers, DRM eDP backlight helpers, i915 panel/PWM helpers, EDID HDR/luminance metadata, VBT backlight type, `intel_dp_wait_source_oui()`, `intel_dp_in_hdr_mode()`, and connector color space/HDR metadata. Integrated through `intel_backlight.c`, which calls `intel_dp_aux_init_backlight_funcs()` before falling back to other backlight implementations.

## Risks
Panel firmware is known to misadvertise VESA support; the probe order and module parameter handling are compatibility-sensitive. Intel HDR nits control without EDID HDR metadata is intentionally disabled unless forced, so unknown panels can lose AUX backlight support without the module override. Several operations rely on short DPCD reads/writes where partial positive lengths are treated as failure in most but not all debug paths. Mixed PWM/AUX operation has edge cases around current mode detection, inversion, and min brightness semantics.

## Test signals
Useful signals include `drm_dbg_kms()` logs announcing Intel or VESA interface selection, DPCD/PWM control mode messages, range messages, and explicit DPCD read/write errors. Manual validation should cover panels with Intel-only AUX, VESA AUX, mixed AUX/PWM enable/set, HDR metadata present/missing, forced module parameters, suspend/resume, and brightness reads before enabling AUX brightness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.h

## Purpose
Declares the AUX backlight initializer used by the i915 display backlight code to install DisplayPort AUX backlight callbacks for an eDP connector.

## Important APIs, types, and functions
- Forward declares `struct intel_connector`.
- Exports `int intel_dp_aux_init_backlight_funcs(struct intel_connector *intel_connector);`.
- Uses a conventional include guard `__INTEL_DP_AUX_BACKLIGHT_H__`.

## Control flow
This header has no runtime control flow. It allows other display code, especially the backlight setup path, to call into `intel_dp_aux_backlight.c` without exposing Intel/VESA helper internals or the local module-parameter enum.

## State and persistence
No state is defined here. The declared initializer mutates connector panel backlight function pointers and state in the implementation file.

## Dependencies and integration points
Integrated by including it from `intel_dp_aux_backlight.c` and caller code such as `intel_backlight.c`. The narrow declaration keeps AUX backlight policy private to the implementation.

## Risks
The header is intentionally minimal. Any additional caller needing lower-level Intel or VESA helpers would require API expansion, which should be avoided unless there is a real shared use.

## Test signals
Build coverage is the primary signal. A missing or mismatched declaration would break callers at compile time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_backlight.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_regs.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_regs.h

## Purpose
Defines i915 MMIO register addresses and bit fields for DisplayPort AUX channel control and data registers across legacy ports, PCH AUX, VLV, Xe_LPD/Xe2_LPD USB-C AUX channels, and PICA power-well control.

## Important APIs, types, and functions
- Register address macros include `DP_AUX_CH_CTL()`, `VLV_DP_AUX_CH_CTL()`, `PCH_DP_AUX_CH_CTL()`, `XELPDP_DP_AUX_CH_CTL()`, and corresponding `*_DATA()` macros.
- Bit definitions cover AUX send/done/interrupt/error state, timeout selection, message size, precharge/sync fields, hardware test bits, AKSV select, and Xe_LPD AUX power request/status.
- `__xe2lpd_aux_ch_idx()` remaps non-USB-C AUX channels into the display version 20 register layout.
- `XE2LPD_PICA_PW_CTL` and its request/status bits describe PICA power-well control.

## Control flow
The file is declarative. Macro expansion selects the right MMIO address family based on AUX channel and, for Xe_LPD, display version. Callers use the generated register offsets in AUX transaction code and power management paths.

## State and persistence
No C state is stored. The macros address hardware registers whose contents are controlled by AUX transaction programming and power-well management elsewhere.

## Dependencies and integration points
Depends on `intel_display_reg_defs.h` for `_MMIO`, `_PORT`, `_PICK_EVEN_2RANGES`, `REG_BIT`, `REG_GENMASK`, and field helpers. It is an integration point for low-level AUX transfer code, HDCP AKSV AUX transactions, PSR/FEC/GTC AUX-related bits, and platform-specific power sequencing.

## Risks
Register selection is platform-sensitive. The Xe2 remapping helper can silently route to the wrong register if an invalid `aux_ch` is passed. Several bits have different meanings before and after Skylake or Icelake, so callers must only set fields valid for the target platform. Message size and timeout fields are critical for AUX transaction reliability.

## Test signals
Compile-time macro use catches syntax errors only. Runtime signals are AUX transfer success, timeout/error bits in `DP_AUX_CH_CTL`, platform bring-up logs, HDCP AUX behavior, eDP panel probing, and Type-C/USB-C AUX operation on display version 20 and newer hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_aux_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.c

## Purpose
Adapts the generic i915 HDCP engine to DisplayPort SST and MST transports. It implements HDCP 1.x and HDCP 2.2 message I/O over DP AUX, link-integrity checks, capability detection, and MST stream encryption hooks.

## Important APIs, types, and functions
- Exported entry point: `intel_dp_hdcp_init()`, which installs either the SST or MST `intel_hdcp_shim`.
- HDCP 1.x helpers read/write `An`, `Aksv`, `Bksv`, `Binfo/Bstatus`, `Bcaps`, `Ri'`, KSV FIFO, and `V'` parts over `drm_dp_dpcd_read/write()`.
- HDCP 2.2 message metadata is encoded in `struct hdcp2_dp_msg_data` and `hdcp2_dp_msg_data[]`, mapping message IDs to DP offsets, wait behavior, and read timeouts.
- HDCP 2.2 helpers include `intel_dp_hdcp2_write_msg()`, `intel_dp_hdcp2_read_msg()`, `intel_dp_hdcp2_wait_for_msg()`, `_intel_dp_hdcp2_get_capability()`, and `intel_dp_hdcp2_config_stream_type()`.
- MST-specific hooks include `intel_dp_mst_hdcp_stream_encryption()`, `intel_dp_mst_hdcp2_stream_encryption()`, remote capability reads through `connector->mst.port->aux`, and the `intel_dp_mst_hdcp_shim`.

## Control flow
For HDCP 1.x authentication, the shim writes `An`, triggers hardware-backed `Aksv` output by writing the Aksv DPCD address, reads receiver keys/status over AUX, detects repeaters via `Bcaps`, and checks link health from `DP_AUX_HDCP_BSTATUS`.

For HDCP 2.2, write operations strip the leading generic message ID because DP DPCD message windows do not include it, then write chunks bounded by `DP_AUX_MAX_PAYLOAD_BYTES`. Read operations wait for either a fixed timeout or CP_IRQ plus RXSTATUS readiness bits, optionally fetch receiver ID count first for repeater topology, read the message in AUX-sized chunks, enforce whole-message deadlines where configured, and restore the message ID into the caller buffer.

MST stream encryption toggles `TRANS_DDI_HDCP_SELECT`, waits for per-transcoder stream encryption status in HDCP or HDCP2 registers, and validates stream type fields around enable. MST HDCP2 link checks only perform port authentication checks for the connector marked as the repeater/authentication participant.

## State and persistence
Persistent state lives in `struct intel_hdcp` on the connector, including CP_IRQ counters, pairing state, repeater state, stream transcoder, and stream type data. This file updates `cp_irq_count_cached` after HDCP2 reads. Hardware state persists in HDCP/DDI registers and sink DPCD authentication windows until disabled or link reset.

## Dependencies and integration points
Depends on DRM HDCP constants/helpers, DP AUX/DPCD helpers, i915 HDCP core/shim interfaces, DDI register programming, `intel_de_wait_ms()`, MST topology AUX, and display version conditionals for stream status registers. Called from DP and MST connector initialization paths and later by the generic HDCP state machine.

## Risks
HDCP is timing-sensitive. Incorrect wait mode, CP_IRQ handling, partial AUX transfer handling, or message-size calculation can cause authentication failures. HDCP 2.2 receiver capability is retried because some monitors report bad first reads, so reducing retries can regress compatibility. MST stream encryption status differs by display generation, and wrong transcoder/pipe mapping can leave streams unencrypted or time out. The Aksv flow relies on the AUX transfer hook recognizing the DPCD address to emit secret hardware data.

## Test signals
Signals include HDCP enable success for DP SST and MST, CP_IRQ wait timeout debug logs, AUX read/write length failures, HDCP2 link status values such as reauth/link integrity/topology change, stream encryption timeout errors, and content-protection property transitions. Test matrices should include repeaters, MST branch devices, paired and unpaired HDCP2 receivers, and display version 30 stream-type status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.h

## Purpose
Declares the DisplayPort HDCP initialization API for i915 digital ports and connectors.

## Important APIs, types, and functions
- Forward declares `struct intel_connector` and `struct intel_digital_port`.
- Exports `int intel_dp_hdcp_init(struct intel_digital_port *dig_port, struct intel_connector *intel_connector);`.

## Control flow
No runtime control flow exists in the header. It exposes the implementation file's shim installation function to DP and MST connector setup code.

## State and persistence
No state is stored here. Calling the declared function initializes connector HDCP state through the generic `intel_hdcp_init()` path when the platform and connector type support it.

## Dependencies and integration points
Integrated by `intel_dp.c` for SST DP connectors and by `intel_dp_mst.c` for dynamically created MST connectors. The header intentionally hides all HDCP 1.x/2.2 transport helper details.

## Risks
The include guard name has a triple underscore suffix but is internally consistent. API expansion should remain cautious because the transport shim is meant to stay private.

## Test signals
Build coverage catches signature drift. Runtime validation belongs to `intel_dp_hdcp.c` through successful HDCP initialization and authentication.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_hdcp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.c

## Purpose
Implements DisplayPort link training for i915 across classic 8b/10b links, UHBR 128b/132b links, eDP, DP MST, and LTTPR repeater topologies. It also exposes debugfs controls for forcing link rates, lane counts, failures, and retraining.

## Important APIs, types, and functions
- Capability/probe APIs: `intel_dp_read_dprx_caps()`, `intel_dp_init_lttpr_and_dprx_caps()`, `intel_dp_lttpr_transparent_mode_enabled()`.
- Training setup APIs: `intel_dp_link_training_set_mode()`, `intel_dp_link_training_set_bw()`, `intel_dp_program_link_training_pattern()`, `intel_dp_set_signal_levels()`, `intel_dp_get_adjust_train()`.
- Training lifecycle: `intel_dp_start_link_train()` and `intel_dp_stop_link_train()`.
- 8b/10b phases: `intel_dp_link_training_clock_recovery()`, `intel_dp_link_training_channel_equalization()`, `intel_dp_link_train_all_phys()`.
- UHBR phases: `intel_dp_128b132b_link_train()`, `intel_dp_128b132b_lane_eq()`, `intel_dp_128b132b_lane_cds()`, `intel_dp_128b132b_intra_hop()`, `intel_dp_128b132b_sdp_crc16()`.
- Fallback/debug: `intel_dp_schedule_fallback_link_training()`, link-parameter reduction helpers, and `intel_dp_link_training_debugfs_add()`.

## Control flow
Before training, `intel_dp_start_link_train()` blocks HPD handling, reinitializes LTTPR/DPRX capabilities, programs link mode and bandwidth, then chooses either UHBR or 8b/10b training. LTTPR discovery reads common caps, avoids unsafe probing on old AUX-timeout platforms, preserves mode on active links, switches repeaters to non-transparent mode when safe, and reads per-PHY caps.

For 8b/10b, training walks LTTPRs from downstream to upstream and then the DPRX. Each PHY performs clock recovery with TPS1, repeated link-status reads, sink adjust-request handling, same-voltage and max-swing escape conditions, and then channel equalization with TPS2/3/4 based on source/sink capability. After each PHY it disables that PHY's DPCD training pattern; after all PHYs it idles source training.

For UHBR, the code waits for intra-hop AUX to clear, performs the LANEx_EQ_DONE sequence with TPS1 then TPS2 and TX FFE preset updates under loop/deadline limits, then performs the LANEx_CDS_DONE sequence with TPS2_CDS until interlane align and symbol lock are complete. On failure it leaves the source in TPS2 before disabling DPCD training to avoid stuck transcoder states.

After training failure, sequential failure counts gate whether a userspace modeset retry is scheduled. Fallback first tries max eDP params when appropriate, then reduces link parameters while respecting forced debugfs rate/lane settings and avoiding unsupported UHBR to non-UHBR fallback. `intel_dp_stop_link_train()` marks the link active, disables source training, waits for UHBR intra-hop cleanup, unblocks HPD, and schedules link-check work unless long HPDs are ignored or repeated sequential failures occurred.

## State and persistence
State is kept in `struct intel_dp`: DPCD caps, LTTPR common/per-PHY caps, `train_set[4]`, active link status, selected link rate/lane count, max fallback limits, forced debugfs values, retrain-disabled flag, failure counters, HOBL failure state, and VRR link mode state. Sink-side DPCD persists link coding, lane count, link rate, downspread/MSA ignore, training pattern, and lane signal level requests during training.

## Dependencies and integration points
Depends heavily on DRM DP helper functions for DPCD caps, LTTPR, link status, adjust requests, UHBR status checks, and training delays. Source-side programming is delegated through function pointers in `intel_dp` and encoder callbacks. It is invoked from DDI and legacy DP enable paths and feeds MST, compliance tests, hotplug/link-check work, and debugfs.

## Risks
This file is high risk because link training touches timing, hardware sequencing, sink quirks, repeaters, and fallback policy. Infinite-loop prevention, partial AUX read/write failures, display-generation training pattern support, LTTPR transparent mode changes on active links, UHBR deadlines, and forced debugfs settings are all compatibility-sensitive. The code intentionally tolerates training failures in some CI long-HPD-ignore cases, which can hide real link issues if used outside that context.

## Test signals
Core signals are `lt_dbg` and `lt_err` messages showing requested and programmed signal levels, link status dumps, selected TPS pattern, pass/fail per PHY, fallback parameter changes, and retrain disablement. Debugfs files `i915_dp_force_link_rate`, `i915_dp_force_lane_count`, `i915_dp_force_link_training_failure`, `i915_dp_force_link_retrain`, max rate/lane files, and retrain-disabled status provide directed test hooks. Validation should cover SST, MST, eDP, LTTPR docks, UHBR, forced fallback, HPD retry behavior, and suspend/resume retraining.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.h

## Purpose
Defines the public i915 DisplayPort link-training interface used by encoder enable paths, MST, compliance testing, and debugfs setup.

## Important APIs, types, and functions
- Declares DPRX/LTTPR capability APIs, link mode/bandwidth programming, adjust request calculation, source pattern/signal programming, start/stop training, link-status dump, UHBR SDP CRC enablement, and debugfs registration.
- Includes `drm_dp_helper.h` for `DP_RECEIVER_CAP_SIZE`, `DP_LINK_STATUS_SIZE`, and `enum drm_dp_phy`.
- Provides inline `intel_dp_training_pattern_symbol()` to strip `DP_LINK_SCRAMBLING_DISABLE` from a training pattern byte.

## Control flow
The header has no complex control flow. Its inline helper masks a programmed training pattern down to the TPS symbol value used for logging and comparisons.

## State and persistence
No state is stored here. The declared functions operate on `struct intel_dp`, `struct intel_crtc_state`, and atomic state objects maintained by the display core.

## Dependencies and integration points
Used by DDI enable/disable code, G4x DP code, MST bandwidth/probe paths, DP compliance testing, and DP tunnel resume capability reads. The exported surface is broad because link training spans hardware programming, sink DPCD state, and test/debug entry points.

## Risks
Signature changes have wide build impact. Any semantic change to `intel_dp_training_pattern_symbol()` can affect both classic and UHBR training pattern interpretation.

## Test signals
Compile-time coverage across DP, DDI, MST, and test code is the main header signal. Runtime signals are generated by the implementation file's link-training debug and error logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_link_training.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.c

## Purpose
Implements i915 DisplayPort Multi-Stream Transport support. It creates per-pipe virtual MST stream encoders, dynamic MST connectors, computes bandwidth/TU/PBN/DSC configuration, checks topology bandwidth in atomic state, and sequences MST stream enable/disable around payload allocation and transcoder programming.

## Important APIs, types, and functions
- Exported setup/state APIs: `intel_dp_mst_encoder_init()`, `intel_dp_mst_encoder_cleanup()`, `intel_dp_mst_source_support()`, `intel_dp_mst_active_streams()`, `intel_dp_mst_add_topology_state_for_crtc()`, `intel_dp_mst_atomic_check_link()`, `intel_dp_mst_crtc_needs_modeset()`, `intel_dp_mst_prepare_probe()`, `intel_dp_mst_verify_dpcd_state()`, `intel_dp_mtp_tu_compute_config()`.
- Encoder helpers: `mst_stream_encoder_create()`, `mst_stream_compute_config()`, `mst_stream_pre_enable()`, `mst_stream_enable()`, `mst_stream_disable()`, `mst_stream_post_disable()`, PLL enable/disable hooks, and config/readout wrappers.
- Connector helpers: `mst_topology_add_connector()`, `mst_connector_mode_valid_ctx()`, `mst_connector_atomic_check()`, `mst_connector_detect_ctx()`, EDID and registration helpers.
- Bandwidth helpers compute overhead, M/N, TU, PBN, DSC slice count, DPT bottleneck bpp, and hblank expansion quirks.

## Control flow
Initialization skips unsupported platforms and eDP, creates one fake MST encoder per pipe, attaches callbacks, and initializes the DRM MST topology manager with i915 callbacks. Topology callbacks dynamically allocate MST connectors, attach every stream encoder, copy properties from the primary SST connector where needed, read decompression DSC caps, detect hblank expansion quirks, and initialize HDCP for the new connector.

Atomic compute starts from maximum link limits, chooses uncompressed or DSC mode, computes local M/N and remote TU/PBN, aligns slots, requests DRM MST time slots, and reduces bpp or enables DSC if needed. Joined-pipe candidates are tried for large modes. Late compute designates the lowest-numbered active transcoder on the MST link as the master transcoder.

Atomic topology checks add related connectors/CRTCs when one stream needs a modeset, release old time slots, verify DSC changes that require all topology pipes to be recomputed, and ask DRM MST core to validate total bandwidth. On ENOSPC, i915 link-bandwidth limits are updated and `-EAGAIN` forces recompute.

Enable sequencing increments active stream count, powers the sink path, enables decompression and primary encoder only for the first stream, adds payload part 1, enables transcoder clock as required by generation/stream order, writes DSC PPS and MSA, enables transcoder function, sets VC payload allocation, waits for ACT, adds payload part 2, handles FEC workaround state, enables transcoder/vblank, and enables HDCP. Disable performs the reverse: disables HDCP/decompression, removes payload in two parts, clears payload allocation, disables VRR/transcoder/DSC/scaler, powers down the MST PHY path, disables infoframes and clocks, and post-disables the primary encoder for the last stream.

## State and persistence
State is stored in `intel_dp->mst`: topology manager, active stream count, stream encoder pointers, and probed link parameters. Each dynamic connector stores `connector->mst.dp`, `connector->mst.port`, DSC aux/quirk data, and current encoder binding. CRTC state stores MST master transcoder, DP M/N/TU, DSC/FEC state, joiner pipes, lane count, link rate, and DP tunnel refs. DRM MST topology state stores payload/time-slot allocations and pending CRTC masks.

## Dependencies and integration points
Depends on DRM MST helpers, atomic helpers, EDID, DP bandwidth helpers, i915 DDI/transcoder/scaler/audio/PSR/VRR/DSC/FEC/HDCP/link bandwidth code, and DP tunnel bandwidth accounting. It integrates with hotplug via topology callbacks and with userspace through dynamically registered DRM connectors and connector properties.

## Risks
MST has high interaction risk: all streams on a topology share link bandwidth and sometimes a master transcoder, so a change for one connector can require modesets and recomputation for others. Bandwidth math mixes local TU, remote PBN, DSC, FEC, SSC, hblank quirks, and hardware alignment requirements. Incorrect active-stream accounting can disable the primary encoder or link while streams remain active. Dynamic connector lifetime and MST port references must stay balanced. Payload part1/part2 ordering and ACT waits are hardware-visible and timing-sensitive.

## Test signals
Signals include MST topology connector creation/removal, EDID reads through MST AUX, mode validation failures, DSC fallback logs, slot/PBN/TU logs, DRM MST atomic ENOSPC paths, ACT status checks, active stream count logs, HDCP enablement, and long hotplug/MST DPCD state reset detection. Test coverage should include multi-monitor MST hubs, SST with sideband support, DSC and non-DSC modes, UHBR MST, payload removal, branch-device resets, and bandwidth oversubscription retries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.h

## Purpose
Declares the i915 DisplayPort MST interface used by DP initialization, atomic modeset code, link-bandwidth checks, tunnel integration, and stream mode computation.

## Important APIs, types, and functions
- Exposes MST encoder manager lifecycle, source-support query, active stream count, master/slave transcoder helpers, topology state addition, atomic link check, topology modeset need detection, probe preparation, DPCD state verification, and MTP/TU config computation.
- Forward declares i915 atomic, CRTC, digital port, DP, connector state, and link bandwidth structures.

## Control flow
No runtime control flow is implemented in the header. Callers use the declarations to enter MST setup, compute, and atomic validation paths implemented in `intel_dp_mst.c`.

## State and persistence
No state is stored here. The implementation operates on `intel_dp->mst`, DRM MST topology state, connector MST fields, and CRTC atomic state.

## Dependencies and integration points
The header is included by DP core, tunnel code, compliance test code, and display atomic/link bandwidth paths. It defines the local contract between generic DP code and MST-specific behavior.

## Risks
Because MST participates in atomic check and encoder lifecycle, API misuse can cause missing topology state, wrong bandwidth recomputation, or incorrect master transcoder logic. The exported `intel_dp_mtp_tu_compute_config()` is shared with SST-like MTP calculations, so callers must pass coherent bpp and DSC limits.

## Test signals
Build coverage catches signature drift. Runtime validation is through MST connector enumeration, atomic modeset success, bandwidth fallback, and master/slave transcoder behavior in the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_mst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.c

## Purpose
Implements DisplayPort compliance test handling for i915. It reads DP CTS requests from DPCD, stores requested test parameters, adjusts modeset link limits and pipe bpp for tests, programs PHY test patterns, handles short-pulse follow-up behavior, and exposes debugfs files for test state.

## Important APIs, types, and functions
- Exported APIs: `intel_dp_test_reset()`, `intel_dp_test_compute_config()`, `intel_dp_test_request()`, `intel_dp_test_phy()`, `intel_dp_test_short_pulse()`, `intel_dp_test_debugfs_register()`.
- Request handlers: `intel_dp_autotest_link_training()`, `intel_dp_autotest_video_pattern()`, `intel_dp_autotest_edid()`, `intel_dp_autotest_phy_pattern()`.
- PHY programming: `intel_dp_process_phy_request()`, `intel_dp_phy_pattern_update()`, `intel_dp_prep_phy_test()`, `intel_dp_do_phy_test()`.
- Debugfs files: `i915_dp_test_data`, `i915_dp_test_type`, and `i915_dp_test_active`.

## Control flow
Short-pulse handling in DP core calls `intel_dp_test_request()` when DPCD indicates a test request. The function reads `DP_TEST_REQUEST`, dispatches to the matching autotest handler, stores parsed parameters in `intel_dp->compliance`, sets `test_active` for tests that need userspace not to interfere, records `test_type` only on ACK, and writes `DP_TEST_RESPONSE`.

During modeset computation, `intel_dp_test_compute_config()` clamps pipe bpp for video-pattern tests and clamps link rate/lane count for link-training tests if the requested params remain valid after fallback limits. For PHY pattern tests, `intel_dp_test_phy()` acquires modeset locks with EDEADLK backoff, finds active DP pipes for the port, uses only the MST master transcoder on display version 12 and newer, reads sink link status, applies requested signal levels, writes DDI PHY pattern registers, updates DPCD lane training set, and calls DRM helper code to set the sink PHY test pattern.

Debugfs active writes iterate connected SST DisplayPort connectors, parse a decimal value, and only value `1` activates compliance testing. Debugfs data/type show the currently stored request data for the connected SST DP connector.

## State and persistence
All test state lives in `intel_dp->compliance`: `test_active`, `test_type`, requested link rate/lane count, video dimensions, bpc, EDID result, and PHY test parameters. PHY pattern programming persists in DDI test-pattern registers and sink DPCD until disabled or reprogrammed. `intel_dp_test_reset()` clears the compliance struct so later requests can be captured cleanly.

## Dependencies and integration points
Depends on DP DPCD test registers, DRM DP PHY test helpers, EDID state, i915 link training helpers, DDI register programming, modeset locking, MST master-transcoder helpers, hotplug events, and debugfs. DP core invokes request/short-pulse handling; mode compute invokes test config adjustment.

## Risks
Compliance code intentionally overrides normal mode/link decisions, so stale `test_active` or `test_type` can disturb regular operation. PHY tests use ad hoc modeset locking and direct register programming, with a FIXME noting they should be integrated into normal modesets. Debugfs iterates only SST DisplayPort connectors and skips MST encoders. The EDID path uses raw EDID access and reports checksum of the last extension block. Hardcoded custom and HBR2 compliance patterns are compatibility workarounds.

## Test signals
CTS equipment should observe ACK/NAK in `DP_TEST_RESPONSE`, correct checksum writes, requested link rate/lane count in subsequent modesets, correct color ramp/video bpc behavior, and expected PHY patterns. Kernel debug logs announce each request type and errors. Debugfs files expose active/type/data state for manual verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.h

## Purpose
Declares the DisplayPort compliance test interface for i915 DP core, link configuration, PHY testing, short-pulse handling, and debugfs registration.

## Important APIs, types, and functions
- Forward declares `struct intel_dp`, `struct intel_display`, `struct intel_crtc_state`, and `struct link_config_limits`.
- Declares reset, request dispatch, config adjustment, PHY execution, short-pulse handling, and debugfs registration functions.

## Control flow
The header has no runtime control flow. It exposes the compliance-test lifecycle to DP hotplug and modeset code while keeping request parsing and debugfs implementation private.

## State and persistence
No state is defined here. The functions operate on `intel_dp->compliance` state and display debugfs roots in the implementation.

## Dependencies and integration points
Included by DP core, MST code for PHY master-transcoder handling, and the implementation file. It includes `linux/types.h` for `bool`.

## Risks
The API lets callers affect modeset limits and PHY programming based on compliance state. Calls should remain limited to DP compliance paths to avoid leaking test behavior into normal operation.

## Test signals
Compile coverage catches signature mismatch. Runtime signals are debugfs file presence and compliance behavior implemented in `intel_dp_test.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.c

## Purpose
Integrates DRM DisplayPort tunnel support with i915 DP connectors and atomic modesets. It detects DP tunnels, manages bandwidth allocation mode, accounts per-stream tunnel bandwidth, coordinates inherited bandwidth on already-active pipes, and allocates or reduces bandwidth during atomic commits.

## Important APIs, types, and functions
- Tunnel lifecycle: `intel_dp_tunnel_detect()`, `intel_dp_tunnel_disconnect()`, `intel_dp_tunnel_destroy()`, `intel_dp_tunnel_suspend()`, `intel_dp_tunnel_resume()`, `intel_dp_tunnel_bw_alloc_is_enabled()`.
- Atomic state helpers: `intel_dp_tunnel_atomic_cleanup_inherited_state()`, `intel_dp_tunnel_atomic_add_state_for_crtc()`, `intel_dp_tunnel_atomic_check_state()`, `intel_dp_tunnel_atomic_compute_stream_bw()`, `intel_dp_tunnel_atomic_clear_stream_bw()`, `intel_dp_tunnel_atomic_check_link()`, `intel_dp_tunnel_atomic_alloc_bw()`.
- Manager lifecycle: `intel_dp_tunnel_mgr_init()` and `intel_dp_tunnel_mgr_cleanup()`.
- Private state: `struct intel_dp_tunnel_inherited_state` stores per-pipe `drm_dp_tunnel_ref` entries for bandwidth inherited outside a normal atomic state.

## Control flow
Detection skips eDP. If a tunnel already exists, the code updates its state and reports whether effective link bandwidth changed; on update error it destroys and recreates the tunnel. New tunnel detection uses the display-wide tunnel manager, enables bandwidth allocation mode when supported, allocates bandwidth for any already-active pipes, updates sink caps, and returns `1` when userspace should be notified of mode-list-relevant bandwidth changes.

Suspend disables bandwidth allocation mode and marks the tunnel suspended. Resume may read DPRX caps only to satisfy the Thunderbolt connection manager without overwriting cached caps, re-enables bandwidth allocation, allocates bandwidth for the resumed pipe, and logs/drop-rejects on error. MST resume allocation is noted as TODO.

Atomic compute records each stream's required rate in the DRM tunnel state and takes a tunnel ref in the CRTC state. Clearing stream bandwidth writes zero for the pipe and releases the ref. Connector atomic checks add group state for old/new CRTCs and inherited tunnel state when a tunnel was detected after a stream was already active. Link checks call DRM tunnel bandwidth validation and, on ENOSPC, reduce i915 bpp limits and return `-EAGAIN` for recompute. Commit allocation first decreases bandwidth for modeset streams whose required bandwidth dropped, then increases bandwidth for new requirements and queues a modeset retry if allocation fails on a connected sink.

## State and persistence
Long-lived state includes `display->dp_tunnel_mgr`, `intel_dp->tunnel`, `intel_dp->tunnel_suspended`, and per-CRTC `dp_tunnel_ref`. Atomic-only state includes DRM tunnel state, stream required bandwidth per pipe, and `state->inherited_dp_tunnels` refs. Sink/tunnel bandwidth allocation state persists in the external tunnel manager/device until disabled or reallocated.

## Dependencies and integration points
Depends on DRM `drm_dp_tunnel` helpers, i915 atomic state, DP link training capability reads, MST active-pipe helpers, link bandwidth reduction, connector detection, suspend/resume, and display commit paths. Call sites include DP detection, SST/MST compute config, connector atomic checks, display atomic cleanup, CRTC add-state, link bandwidth validation, and commit bandwidth allocation.

## Risks
Bandwidth accounting must stay balanced across detection on active links, normal atomic modesets, failures, and cleanup. Missing inherited tunnel cleanup leaks refs or leaves bandwidth allocated. Resume currently allocates only a single SST pipe and explicitly lacks MST support. Returning `1` from detect affects userspace notification behavior, so false positives can cause unnecessary reprobes and false negatives can hide mode changes. Allocation failure after atomic check is handled by retry work, which depends on accurate connected-sink detection.

## Test signals
Signals include DPTUN debug logs for detection, state update, bandwidth changes, initial per-stream allocations, inherited tunnel state, required stream bandwidth, allocation failures, suspend/resume, and manager creation. Tests should cover tunnel hotplug, bandwidth allocation unsupported, active-stream detection, atomic bpp reduction on ENOSPC, suspend/resume, disconnect cleanup, SST and MST interactions, and mode-list updates after tunnel bandwidth changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.h

## Purpose
Declares the i915 DP tunnel integration API and provides no-op inline fallbacks when DP tunnel support is not built for the active driver configuration.

## Important APIs, types, and functions
- Feature gate: enabled when `CONFIG_DRM_I915_DP_TUNNEL` with `I915` or `CONFIG_DRM_XE_DP_TUNNEL` without `I915` is set.
- Declares tunnel detect/disconnect/destroy/suspend/resume, bandwidth-allocation query, inherited state cleanup, stream bandwidth compute/clear, CRTC and connector atomic state checks, atomic link check, bandwidth allocation, and manager lifecycle.
- Fallbacks return neutral success for atomic operations, false for bandwidth allocation enabled, `-EOPNOTSUPP` for detect, and no-op for cleanup/lifecycle functions.

## Control flow
The header's conditional compilation chooses either real declarations or inline stubs. The stubs let the rest of i915/Xe display code call tunnel hooks unconditionally without scattering feature checks.

## State and persistence
No state is defined in the header. Real implementation state lives in `intel_dp->tunnel`, display tunnel manager fields, atomic inherited tunnel refs, and CRTC tunnel refs. Stub builds store no tunnel state.

## Dependencies and integration points
Uses `linux/errno.h` and `linux/types.h`, plus forward declarations for DRM connector state, modeset acquire context, i915 atomic/CRTC/display/DP structures, encoders, and link bandwidth limits. Integrated by DP detect, DP/MST compute, atomic check/cleanup, commit allocation, and display manager init/cleanup.

## Risks
The fallback for `intel_dp_tunnel_atomic_alloc_bw()` is typed as `int` while the real function is `void`; callers that ignore the return value compile in practice, but signature consistency is worth watching. Feature-gate mistakes can silently disable tunnel behavior and leave only no-op atomic accounting. Real callers must tolerate `-EOPNOTSUPP` from detect.

## Test signals
Builds with tunnel support enabled should link against `intel_dp_tunnel.c`; disabled builds should compile through the stubs and behave as if no tunnel is present. Runtime tunnel tests should confirm detection returns `-EOPNOTSUPP` only in stubbed builds and that atomic hooks remain harmless when unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp_tunnel.h -->
