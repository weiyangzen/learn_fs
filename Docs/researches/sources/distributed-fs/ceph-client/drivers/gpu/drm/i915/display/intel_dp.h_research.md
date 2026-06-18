# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dp.h

## Purpose

`intel_dp.h` is the public interface for the i915 DisplayPort/eDP policy layer implemented primarily by `intel_dp.c`. It exposes connector lifecycle hooks, mode compute and validation helpers, link bandwidth/rate helpers, DSC/FEC helpers, sink power/control functions, SDP infoframe helpers, MST suspend/resume entry points, and small inline utilities used by adjacent i915 display modules.

The header is intentionally forward-declaration heavy. It avoids pulling large DRM/i915 structure definitions into every user, while still letting other display modules call into DP-specific functionality.

## Important APIs, Types, And Functions

The only type defined in the header is `struct link_config_limits`. It carries the candidate bounds used by DP mode computation:

- `min_rate` / `max_rate`: allowed link-rate range.
- `min_lane_count` / `max_lane_count`: allowed lane-count range.
- `pipe.min_bpp` / `pipe.max_bpp`: uncompressed DSC input or link output bpp in integer bpp units.
- `link.min_bpp_x16` / `link.max_bpp_x16`: compressed or uncompressed link bpp in 1/16 bpp fixed-point units.

Major function groups declared here:

- Connector and encoder lifecycle: `intel_dp_init_connector()`, `intel_dp_connector_sync_state()`, `intel_dp_encoder_flush_work()`, `intel_dp_encoder_suspend()`, `intel_dp_encoder_shutdown()`, `intel_dp_sync_state()`, and `intel_dp_initial_fastset_check()`.
- HPD/link state: `intel_dp_hpd_pulse()`, `intel_dp_link_check()`, `intel_dp_check_link_state()`, `intel_dp_get_active_pipes()`, `intel_dp_flush_connector_commits()`, `intel_digital_port_lock()`, `intel_digital_port_unlock()`, `intel_digital_port_connected()`, and `intel_digital_port_connected_locked()`.
- Mode compute: `intel_dp_compute_config()`, `intel_dp_compute_config_late()`, `intel_dp_audio_compute_config()`, `intel_dp_compute_config_limits()`, `intel_dp_compute_min_hblank()`, `intel_dp_sdp_min_guardband()`, and `intel_dp_limited_color_range()`.
- Link math and capabilities: `intel_dp_min_bpp()`, `intel_dp_output_format_link_bpp_x16()`, `intel_dp_link_bw_overhead()`, `intel_dp_link_required()`, `intel_dp_effective_data_rate()`, `intel_dp_max_link_data_rate()`, `intel_dp_config_required_rate()`, `intel_dp_link_symbol_size()`, `intel_dp_link_symbol_clock()`, `intel_dp_max_source_lane_count()`, `intel_dp_max_link_rate()`, `intel_dp_max_lane_count()`, `intel_dp_max_common_rate()`, `intel_dp_max_common_lane_count()`, `intel_dp_common_rate()`, `intel_dp_rate_index()`, `intel_dp_rate_select()`, `intel_dp_compute_rate()`, `intel_dp_link_config_index()`, `intel_dp_link_config_get()`, `intel_dp_link_params_valid()`, `intel_dp_set_link_params()`, and `intel_dp_reset_link_params()`.
- DSC/FEC and joiners: `intel_dp_has_dsc()`, `intel_dp_supports_fec()`, `intel_dp_supports_dsc()`, `intel_dp_mode_to_fec_clock()`, `intel_dp_bw_fec_overhead()`, `intel_dp_dsc_reset_config()`, `intel_dp_dsc_compute_config()`, `intel_dp_needs_8b10b_fec()`, `intel_dp_dsc_compute_max_bpp()`, `intel_dp_compute_min_compressed_bpp_x16()`, `intel_dp_mode_valid_with_dsc()`, `intel_dp_dsc_valid_compressed_bpp()`, `intel_dp_dsc_get_slice_count()`, `intel_dp_dsc_max_src_input_bpc()`, `intel_dp_dsc_min_src_input_bpc()`, `intel_dp_dsc_min_src_compressed_bpp()`, `intel_dp_dsc_bpp_step_x16()`, `intel_dp_has_joiner()`, `intel_dp_joiner_needs_dsc()`, `intel_dp_max_hdisplay_per_pipe()`, `intel_dp_dotclk_valid()`, `intel_dp_joiner_candidate_valid()`, and `for_each_joiner_candidate`.
- Sink controls: `intel_dp_set_power()`, `intel_dp_configure_protocol_converter()`, `intel_dp_sink_enable_decompression()`, `intel_dp_sink_disable_decompression()`, `intel_dp_get_dsc_sink_cap()`, `intel_dp_check_frl_training()`, `intel_dp_pcon_dsc_configure()`, `intel_dp_update_sink_caps()`, `intel_dp_dpcd_set_probe()`, `intel_dp_invalidate_source_oui()`, and `intel_dp_wait_source_oui()`.
- SDP/infoframes and display metadata: `intel_dp_needs_vsc_sdp()`, `intel_dp_set_infoframes()`, `intel_read_dp_sdp()`, `intel_dp_in_hdr_mode()`, `intel_dp_has_gamut_metadata_dip()`, and eDP backlight helpers.

`intel_dp_unused_lane_mask()` is the only inline helper. It returns a four-lane mask with active lanes cleared, useful when programming unused lane bits.

## Control Flow And Integration

The header defines the boundary other modules use to call DP functionality without needing the whole implementation. `intel_ddi`, encoder setup, MST, link training, PSR, HDCP, audio, VDSC, panel/backlight, and hotplug code all rely on these declarations.

The mode-set path typically flows from connector atomic checks into `intel_dp_compute_config()`, with other display modules then using computed CRTC state to program DDI, transcoders, audio, DSC PPS, and infoframes. HPD flows enter through `intel_dp_hpd_pulse()` and may call link retraining, MST handlers, or full detection. Sink power and decompression APIs are called from enable/disable sequences around modeset commits.

The `for_each_joiner_candidate` macro is a notable control helper: it iterates candidate joined-pipe counts from one through `I915_MAX_PIPES` and filters through `intel_dp_joiner_candidate_valid()`. Callers use it to evaluate normal, bigjoiner, and ultrajoiner modes without duplicating platform checks.

## State And Persistence Behavior

The header does not store state itself. Its API contracts mutate state owned by `struct intel_dp`, `struct intel_connector`, and `struct intel_crtc_state`. The comments in `struct link_config_limits` are important because they encode the units expected by compute helpers. Confusing integer bpp with Q4 fixed-point bpp would directly corrupt mode bandwidth decisions.

Duplicate declarations of `intel_edp_fixup_vbt_bpp()` and `intel_dp_supports_fec()` appear in the header. They are harmless for C compilation but are maintenance noise and can mislead readers scanning for API ownership.

## Dependencies

The header includes only `<linux/types.h>` and forward declares all DRM/i915 types it references. It uses `enum irqreturn` in a prototype without including the defining interrupt header in this file, relying on transitive includes from users or build context. The function signatures depend on DRM connector/encoder state, i915 atomic/CRTC/connector/encoder types, DP descriptor types, and i915 output-format/port/pipe enums.

## Risks And Test Signals

Risks are mostly API contract risks:

- Unit mismatches in `link_config_limits` can cause incorrect link validation or DSC bpp decisions.
- Callers must pass states that already have relevant connector/CRTC ownership and modeset locks where required by implementation.
- The broad header surface means changes in `intel_dp.c` prototypes can ripple through many i915 display modules.
- Duplicate prototypes should be cleaned carefully only if no generated/header-order dependencies exist.

Test signals include a full i915 build, allmodconfig-style include hygiene, compiler warnings for duplicate or missing declarations, and targeted rebuilds of users including DP, DDI, MST, PSR, HDCP, audio, and VDSC modules.
