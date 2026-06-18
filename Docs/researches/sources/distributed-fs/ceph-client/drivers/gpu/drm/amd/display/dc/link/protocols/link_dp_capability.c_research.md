# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.c

## Purpose
`link_dp_capability.c` is the DP capability discovery, normalization, policy, and verification hub. It reads DPCD capability blocks, source/sink/vendor IDs, dongle and PCON data, DSC/FEC/DP2 capability registers, LTTPR details, cable IDs, USB4 tunneling data, eDP panel capabilities, PSR/replay/ALPM support, and then computes reported, maximum, preferred, selected, and verified link settings. It also contains link-training fallback policy and pre-training verification loops.

## Important APIs, Types, And Functions
- `struct dp_lt_fallback_entry` and `dp_lt_fallbacks[]` encode the DP fallback order from highest to lowest bandwidth for DP2/max-bandwidth fallback.
- `fail_safe_link_settings` is RBR x1 with no downspread, used when verification fails.
- Capability predicates: `is_dp_active_dongle()`, `is_dp_branch_device()`, `dp_is_fec_supported()`, `dp_should_enable_fec()`, `dp_is_128b_132b_signal()`, `dp_is_lttpr_present()`, `dp_is_sink_present()`.
- LTTPR helpers: `dp_parse_lttpr_repeater_count()`, `dp_get_closest_lttpr_offset()`, `dp_retrieve_lttpr_cap()`, `dp_get_lttpr_count()`.
- Link rate helpers: `link_bw_kbps_from_raw_frl_link_rate_data()`, `link_dp_get_encoding_format()`, `mst_decide_link_encoding_format()`, `dp_get_max_link_enc_cap()`, `dp_get_max_link_cap()`, `dp_get_verified_link_cap()`.
- Link selection: `link_decide_link_settings()`, `edp_decide_link_settings()`, `decide_edp_link_settings_with_dsc()`, `decide_fallback_link_setting()`.
- Detection: `detect_dp_sink_caps()`, `detect_edp_sink_caps()`, `dp_overwrite_extended_receiver_cap()`, `read_is_mst_supported()`.
- Source writes: `dpcd_set_source_specific_data()`, `dpcd_write_cable_id_to_dprx()`.
- Verification: `dp_verify_link_cap_with_retries()` and internal `dp_verify_link_cap()` train candidate settings, detect link loss, and update tracing.
- eDP support: `edp_get_alpm_support()`.

## Control Flow
`detect_dp_sink_caps()` calls `retrieve_link_cap()`. That path first configures extended AUX timeout for possible LTTPR, retrieves LTTPR caps, wakes the AUX channel on failure, configures LTTPR transparent mode when present, writes source-specific DPCD data, then reads receiver capability blocks with retry and optional extended receiver caps. It validates lane count, reads vendor IDs, MST support, downstream port/dongle details, DSC/FEC data, DPRX feature enumeration, DP2 rates/fallback formats/FEC1, max pixel rate, VESA Panel Replay caps, USB4 tunneling info, and cable IDs.

`detect_edp_sink_caps()` builds on `retrieve_link_cap()` and then reads eDP link-rate tables, backlight capabilities, eDP revision, PSR caps, ALPM caps, panel replay info, OLED emission rate, DRR granularity, MSO support, and eDP general cap 2.

`dp_get_max_link_cap()` intersects encoder capability with sink `reported_link_cap`, cable ID, LTTPR capability, UHBR13.5 availability, and debug policy such as `disable_uhbr`. `link_decide_link_settings()` then chooses settings based on stream signal: preferred DP settings, MST verified cap, virtual defaults, eDP ILR/DSC-aware search, or regular DP minimum-bandwidth search.

`dp_verify_link_cap_with_retries()` initializes trace state, optionally applies a USB-C combo PHY reset workaround, then repeatedly calls `dp_verify_link_cap()`. The verifier enables PHY, performs link training, checks HPD IRQ link-loss status after nominal success, records fail counts, disables PHY, and falls back through `decide_fallback_link_setting()` until success or fail-safe settings.

## State And Persistence
The file is state-heavy. It writes:
- `link->dpcd_caps` including DPCD rev, MST, dongle caps, branch/sink IDs, FEC/DSC, 128b/132b rates, fallback formats, replay, ALPM, PSR, LTTPR, cable ID, USB4 tunneling, and eDP-specific fields.
- `link->reported_link_cap`, `verified_link_cap`, `preferred_link_setting`, `cur_link_settings` indirectly through verification/training.
- `link->wa_flags` for keep-receiver-powered, MOT segment reset, DPIA forced TBT3 mode, and other quirks.
- `link->dprx_states.cable_id_written` after writing cable ID downstream.
- `link->dpia_bw_alloc_config` is read to adjust LTTPR max link/lane caps when USB4 bandwidth allocation is active.
- Source DPCD registers such as OUI, device ID, min horizontal blanking, total LTTPR count, and cable attributes.

## Dependencies And Integration Points
This file integrates nearly every DP protocol layer: `link_ddc` for AUX timeouts and retimer support, `link_dpcd` for DPCD access, `link_dp_dpia` for USB4 tunnel data, `link_dp_phy` and `link_dp_training` for verification, IRQ handler parsing for post-train link-loss checks, panel control for eDP brightness defaults, link detection/validation, encoder resource selection, link encoder configuration, DMUB USB-C cable ID commands, and GPIO DDC for sink presence.

## Risks And Edge Cases
- Capability discovery depends on many best-effort DPCD reads; partial failures may leave zeroed fields that alter policy.
- DP2/UHBR capability intersection is subtle: encoder, sink, cable, LTTPR, bandwidth allocation, and debug flags all lower link caps.
- `decide_fallback_link_setting()` has separate legacy and DP2 fallback policies; infinite-loop prevention relies on updating `max->link_rate` on EQ failures.
- eDP ILR and DSC selection must not pick unsupported link-rate-set indexes.
- `read_is_mst_supported()` applies preferred training overrides, so raw MST capability and policy are deliberately coupled.
- Workarounds for Retina panels, PCON FRL status, TBT3 compatibility mode, fixed-VS LTTPR count, and USB-C combo PHY reset are hardware-specific and regression-prone.
- `dp_is_sink_present()` has GPIO behavior and a debugger break when no DDC pin exists; it should not be used blindly for DPIA/no-pin cases.

## Test Signals
High-value tests include DP 1.1/1.2/1.4 and DP2 sinks, MST docks, PCON HDMI 2.1 adapters with FRL status, active VGA/DVI/HDMI converters, eDP panels with supported link rate tables and DSC, LTTPR chains including invalid counts, USB4 DPIA links with bandwidth allocation, USB-C cable ID success/failure, FEC/DSC enable policy, `disable_uhbr` and preferred setting overrides, link-cap verification fallback, HPD link-loss after training, and sink-present GPIO behavior.
