# sources/distributed-fs/ceph-client/include/drm/display/drm_dsc_helper.h

Purpose: helper declarations for deriving, packing, and dumping Display Stream Compression parameters.

Important APIs/types/functions: `enum drm_dsc_params_type`, `drm_dsc_dp_pps_header_init`, `drm_dsc_dp_rc_buffer_size`, `drm_dsc_pps_payload_pack`, `drm_dsc_set_const_params`, `drm_dsc_set_rc_buf_thresh`, `drm_dsc_setup_rc_params`, `drm_dsc_compute_rc_parameters`, `drm_dsc_initial_scale_value`, `drm_dsc_flatness_det_thresh`, `drm_dsc_get_bpp_int`, and `drm_dsc_dump_config`.

Control flow: drivers initialize a `drm_dsc_config`, set constants and thresholds, choose a preset for 4:4:4/legacy/4:2:2/4:2:0, compute dependent RC values, pack PPS payload, initialize the DP PPS header, and optionally dump the config.

State and persistence: no global state. Helpers mutate caller-provided config/PPS structures and compute values; persistence is the packed PPS sent to sinks.

Dependencies and integration points: `drm_dsc.h`, `struct drm_printer`, DP/eDP encoders, protocol converters, debug output, and sink capability selection.

Risks and test signals: wrong preset, invalid RC intervals, fractional bpp mistakes, and PPS mismatch are risks. Test known PPS vectors, all params types, DPCD RC buffer sizes, dump output, and bpp/bpc/slice boundaries.
