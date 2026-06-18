# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_capability.h

## Purpose
`link_dp_capability.h` defines the public DP capability and link-setting API for display core link code. It hides direct `dc_link` capability layout behind functions that detect caps, select link settings, query verified and maximum caps, classify encoding formats, handle LTTPR, evaluate FEC, and verify link capability through training.

## Important APIs
- Detection: `detect_dp_sink_caps()`, `detect_edp_sink_caps()`, `dp_overwrite_extended_receiver_cap()`, `read_is_mst_supported()`.
- Capability queries: `dp_get_max_link_cap()`, `dp_get_max_link_enc_cap()`, `dp_get_verified_link_cap()`, `dp_is_sink_present()`, `dp_is_lttpr_present()`, `dp_get_lttpr_count()`.
- Encoding and training selection: `link_dp_get_encoding_format()`, `mst_decide_link_encoding_format()`, `dp_decide_training_settings()`.
- Policy: `link_decide_link_settings()`, `edp_decide_link_settings()`, `decide_edp_link_settings_with_dsc()`, `decide_fallback_link_setting()`.
- Feature predicates: `dp_is_fec_supported()`, `dp_should_enable_fec()`, `dp_is_128b_132b_signal()`, `is_dp_active_dongle()`, `is_dp_branch_device()`.
- LTTPR/cable/source DPCD helpers: `dp_retrieve_lttpr_cap()`, `dp_parse_lttpr_repeater_count()`, `dp_get_closest_lttpr_offset()`, `dpcd_write_cable_id_to_dprx()`, `dpcd_set_source_specific_data()`.
- Verification and conversion: `dp_verify_link_cap_with_retries()`, `link_bw_kbps_from_raw_frl_link_rate_data()`, `edp_get_alpm_support()`.

## Control Flow And Integration
Most DP link bring-up code uses this header before training: detect sink caps, compute max/verified cap, decide stream link settings, and choose training settings. It includes only `link_service.h`, so it forms a stable interface between protocol code and higher-level link detection/validation/commit code.

## State And Persistence
The functions declared here operate on `dc_link`, `dc_stream_state`, `pipe_ctx`, `link_resource`, and `dc_link_settings`. They populate persistent link capability fields and select runtime training/link settings.

## Risks And Test Signals
The header is broad and cross-coupled with `link_dp_training.h`; signature drift can break multiple protocol modules. Compile coverage should include DP, eDP, MST, DPIA, FEC, DSC, LTTPR, and DP2/UHBR builds, plus call sites that rely on the exported fallback and verification policies.
