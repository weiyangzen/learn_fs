# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/core/dc_link_exports.c

## Purpose

`dc_link_exports.c` is the public Display Core link API shim. Its file policy says it should be a single entrance to link functionality declared in DC public headers and should not add new functional behavior. Nearly every function forwards to `dc->link_srv` or `link->dc->link_srv`, with a few local convenience helpers for link lookup, eDP enumeration, I2C submission, and highest-encoding-format classification.

## Important APIs, Types, And Functions

- Link lookup and eDP enumeration: `dc_get_link_at_index`, `dc_get_edp_links`, `dc_get_edp_link_panel_inst`.
- Detection/status/capability exports: `dc_link_detect`, `dc_link_detect_connection_type`, `dc_link_get_status`, `dc_link_is_hdcp14`, `dc_link_is_hdcp22`, `dc_link_get_link_cap`, `dc_link_get_highest_encoding_format`, `dc_link_is_dp_sink_present`, `dc_link_is_fec_supported`, `dc_link_should_enable_fec`.
- Link resource map/DSC/link bandwidth: `dc_get_cur_link_res_map`, `dc_restore_link_res_map`, `dc_link_update_dsc_config`, `dc_link_bandwidth_kbps`, `dc_link_required_hblank_size_bytes`, `dc_link_dp_get_max_link_enc_cap`, `dc_link_decide_edp_link_settings`.
- I2C/AUX exports: `dc_get_oem_i2c_device`, `dc_is_oem_i2c_device_present`, `dc_submit_i2c`, `dc_submit_i2c_oem`, `dc_link_aux_transfer_raw`.
- DP test/training/trace exports: `dc_link_dp_handle_automated_test`, `dc_link_dp_set_test_pattern`, `dc_link_set_drive_settings`, `dc_link_set_preferred_link_settings`, `dc_link_set_preferred_training_settings`, `dc_dp_trace_*`, `dc_link_dp_mst_decide_link_encoding_format`, `dc_link_check_link_loss_status`, `dc_link_dp_allow_hpd_rx_irq`, `dc_link_dp_handle_link_loss`, `dc_link_dp_read_hpd_rx_irq_data`, `dc_link_handle_hpd_rx_irq`, `dc_link_decide_lttpr_mode`.
- Remote sink management: `dc_link_add_remote_sink`, `dc_link_remove_remote_sink`.
- eDP/embedded panel features: `dc_link_edp_panel_backlight_power_on`, backlight get/set functions, PSR setup/state/allow-active, Replay allow/state, PR enable/update/general command/state, T12 wait, ALPM support.
- HPD and bandwidth validation: `dc_link_get_hpd_state`, `dc_link_enable_hpd`, `dc_link_disable_hpd`, `dc_link_enable_hpd_filter`, `dc_link_validate_dp_tunneling_bandwidth`.

## Control Flow

Most functions are one-line pass-throughs. The common pattern is to extract `link->dc->link_srv` or `dc->link_srv` and call the corresponding service operation. Return values are returned unchanged.

Local control flow exists in a few helpers:

- `dc_get_link_at_index` returns NULL when `link_index >= MAX_LINKS`; otherwise it returns `dc->links[link_index]`.
- `dc_get_edp_links` iterates `dc->links[0..link_count)`, skips NULL entries, records every link whose `connector_signal == SIGNAL_TYPE_EDP`, and stops at `MAX_NUM_EDP`.
- `dc_get_edp_link_panel_inst` returns false for non-eDP links; otherwise it enumerates eDP links and counts how many precede the target pointer.
- `dc_is_oem_i2c_device_present` and `dc_submit_i2c_oem` return false when no OEM DDC service exists.
- `dc_link_set_drive_settings` first obtains current link resources into a local `struct link_resource`, then forwards drive settings with that resource.
- `dc_link_get_highest_encoding_format` inspects signal type, dongle type, and verified DP encoding to map to public `DC_LINK_ENCODING_*` values; non-DP/unsupported cases return `DC_LINK_ENCODING_UNSPECIFIED`.

## State And Persistence Behavior

This file owns no persistent state. It exposes and triggers stateful behavior owned by other subsystems:

- Detection, MST topology reset, DPRX state clear, link loss handling, link training preferences, HPD filters, FEC decisions, USB4 bandwidth allocation, PSR/Replay/PR state, ALPM support, and backlight control are all delegated to `link_srv`.
- I2C functions send commands through DDC pins and may affect external devices.
- Remote sink add/remove mutates link-managed sink lists through the service layer.
- `dc_get_edp_links` writes caller-provided output arrays and counts; `dc_get_edp_link_panel_inst` writes `inst_out`.

Because it is an API shim, it assumes passed `dc`, `link`, `pipe_ctx`, `ddc`, and output pointers are valid unless a local guard is explicitly present.

## Dependencies And Integration Points

The file includes `link_service.h` for the internal service interface and `dce/dce_i2c.h` for I2C helpers. It integrates public DC APIs with the `link_srv` implementation installed on `struct dc`.

Primary integration boundaries:

- Public display manager / DRM-facing DC callers use these `dc_link_*` exports.
- Link service implements the real DP, HDMI, eDP, AUX, HPD, HDCP, DSC, FEC, LTTPR, USB4, PSR, Replay, PR, ALPM, and bandwidth policies.
- Resource pool supplies `dc->links[]`, `link_count`, `oem_device`, and DDC pins.
- DCE I2C helpers perform OEM and per-link I2C transactions.

The file's policy makes it a stable facade: new public link functions should be declared in `dc.h`, documented there, and forwarded here to the service layer.

## Risks And Edge Cases

- `dc_get_link_at_index` checks `MAX_LINKS` but not `dc->link_count`, so callers can receive NULL or stale/uninitialized slots for indexes below `MAX_LINKS` but outside active count.
- `dc_submit_i2c` does not bounds-check `link_index` or null-check `dc->links[link_index]`, `link->ddc`, or `ddc->ddc_pin`; callers must validate before use.
- `dc_get_edp_link_panel_inst` returns true for an eDP link even if the pointer was not found in the enumerated eDP list; in that case `inst_out` ends as `edp_num`.
- Service table function pointers are assumed present. Any incomplete `link_srv` implementation can crash through a null function pointer.
- `dc_link_get_highest_encoding_format` has an empty HDMI branch and only classifies DP dongle/TMDS and DP 8b/10b or 128b/132b encodings; HDMI native links return unspecified here.
- The shim should not grow policy. Adding behavior here can split responsibility with `link_srv` and make public API behavior inconsistent.

## Test Signals

- API-level tests can mock `link_srv` and assert each export forwards the exact arguments and returns service results unchanged.
- Boundary tests should cover `dc_get_link_at_index` with `MAX_LINKS`, inactive slots, and valid links; eDP enumeration with NULL links and `MAX_NUM_EDP`; and `dc_get_edp_link_panel_inst` for non-eDP, found eDP, and missing eDP pointer.
- I2C tests should cover OEM-device absent/present and invalid per-link DDC inputs if the caller layer can provide them.
- Encoding tests should cover DP-to-DVI/HDMI dongles, DP 8b/10b, DP 128b/132b, non-DP signals, and native HDMI returning unspecified.
- Runtime signals are mostly service-layer logs/traces: DP trace initialization/logging state, LT timestamps/counts, link-loss counts, HPD IRQ results, FEC decisions, backlight/PSR/Replay/PR state, and bandwidth validation statuses.
