# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dc_dp_types.h

## Purpose
`dc_dp_types.h` is the DisplayPort protocol contract layer for AMD DC. It defines DPCD register bitfield overlays, link-training enums, sink capability containers, compliance-test payloads, eDP PSR/ALPM/Panel Replay structures, DP tunneling over USB4 metadata, dongle capability models, and link-training trace state. It has no executable logic, but it is a critical ABI-like internal header because many parser, link-training, AUX, MST, DSC, PSR, and replay paths interpret raw DPCD bytes through these definitions.

## Important APIs, Types, And Data Contracts
The core link settings are `enum dc_lane_count`, `enum dc_link_rate`, `enum dc_link_spread`, `struct dc_link_settings`, and `struct dc_lane_settings`. These types encode legacy 8b/10b rates as DP multiplier values and UHBR rates directly in 10 Mbps units, so callers must not treat all enum values with one conversion rule. `struct dc_link_training_overrides` carries optional pointer overrides for swing, pre-emphasis, FFE, patterns, spread, MST, and FEC. The pointer-based design means the callee must check each override pointer before use.

DPCD byte overlays include `union dpcd_rev`, `union max_lane_count`, `union max_down_spread`, `union lane_status`, `union lane_align_status_updated`, `union dpcd_training_pattern`, and `union dpcd_training_lane`. These are used to map AUX reads/writes to bitfields for link training and HPD IRQ handling. `union hpd_irq_data` maps the 0x200-0x205 status block plus `LINK_SERVICE_IRQ_ESI0` into a seven-byte view.

Downstream and dongle support is modeled by `union dwnstream_portxcaps`, `union dp_downstream_port_present`, `enum dpcd_downstream_port_detailed_type`, `union hdmi_encoded_link_bw`, `union autonomous_mode_and_frl_link_status`, `struct dc_dongle_caps`, and `struct dc_dongle_dfp_cap_ext`. These feed DP-to-HDMI/DVI converter handling and FRL capability decisions.

DSC and FEC capabilities are represented by `union dpcd_fec_capability`, `union dp_fec_capability1`, `union dpcd_dsc_basic_capabilities`, `union dpcd_dsc_branch_decoder_capabilities`, and `struct dpcd_dsc_capabilities`. The DSC data is raw DPCD shaped and later decoded into `struct dsc_dec_dpcd_caps` from `dc_hw_types.h`.

Power and panel features are covered by `struct psr_caps`, `union edp_psr_dpcd_caps`, `struct edp_psr_info`, `union edp_alpm_caps`, Panel Replay unions, `struct dpcd_panel_replay_selective_update_info`, and sink extension caps. USB4 DP tunneling uses `struct dc_tunnel_settings`, `struct dpcd_usb4_dp_tunneling_info`, and register constants such as `DP_TUNNELING_CAPABILITIES`, `REQUESTED_BW`, and `DP_TUNNELING_STATUS`.

`struct dpcd_caps` is the aggregate sink/branch capability cache: it stores DPCD revision, lane/spread, eDP link rates, dongle and branch identity, FEC/DSC/LTTPR/adaptive-sync/USB4/replay/ALPM/HBlank expansion state, cable ID, and MSO-related fields.

## Control Flow And State
This header does not execute control flow. Its state is persisted by embedding its structures inside link objects, sink capability caches, training settings, and trace structures elsewhere in DC. State updates happen when AUX/DPCD readers fill the raw unions or decoded aggregates, and when link-training/replay/PSR code updates trace counters such as `struct dp_trace`.

## Dependencies And Integration Points
It includes `os_types.h` and `dc_ddc_types.h`, and it relies on DRM DP definitions when present while locally defining newer DPCD constants as compatibility fallbacks. Integration points include DP AUX handlers, link encoder training code, MST payload management, DSC policy, eDP PSR/Replay logic, USB4 DPIA bandwidth allocation, HDMI dongle probing, and compliance-test handlers.

## Risks
The largest risk is bitfield interpretation: C bitfield layout is compiler and endian sensitive, so this header assumes the kernel/compiler conventions used by AMD DC. Raw arrays are provided for many unions, which is safer when copying DPCD bytes but requires callers to avoid stale decoded fields. Link-rate enum semantics are mixed between legacy multipliers and UHBR absolute units. `struct dc_link_training_overrides` uses borrowed pointers whose lifetime is external. Several fallback register defines are temporary compatibility shims; mismatch with upstream DRM headers could cause duplicate or stale definitions.

## Test Signals
Good coverage comes from DP link-training success/failure across RBR/HBR/HBR2/HBR3/UHBR, HPD IRQ status decoding, MST payload activation, LTTPR repeater tests, DSC capability parsing, PSR/Panel Replay enablement, USB4 DPIA bandwidth allocation interrupts, DP-to-HDMI dongle probing, and compliance-test DPCD transactions. Static checks should also catch enum conversion errors and DPCD raw-size mismatches.
