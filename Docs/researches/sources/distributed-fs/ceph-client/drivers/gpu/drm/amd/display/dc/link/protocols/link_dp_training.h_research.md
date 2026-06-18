# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.h

## Purpose
`link_dp_training.h` declares the generic DP link training interface and shared helper APIs used by specialized training implementations, PHY control, capability verification, and commit-time training loops.

## Important APIs
- Top-level training: `perform_link_training_with_retries()`, `dp_perform_link_training()`.
- Hardware patterns: `dp_set_hw_training_pattern()`, `dp_set_hw_test_pattern()`, `start_clock_recovery_pattern_early()`.
- DPCD training writes: `dpcd_set_training_pattern()`, `dpcd_set_lane_settings()`, `dpcd_set_link_settings()`, `dpcd_set_lt_pattern_and_lane_settings()`.
- DPCD training reads: `dp_get_lane_status_and_lane_adjust()`.
- LTTPR/channel coding: `dpcd_configure_lttpr_mode()`, `configure_lttpr_mode_transparent()`, `dpcd_configure_channel_coding()`, `repeater_training_done()`.
- Decision helpers: `dp_decide_training_settings()`, `dp_decide_lane_settings()`, `decide_cr_training_pattern()`, `decide_eq_training_pattern()`, `dp_decide_lttpr_mode()`, `dp_get_lttpr_mode_override()`, `override_training_settings()`.
- Status helpers: `dp_check_link_loss_status()`, `dp_is_cr_done()`, `dp_is_ch_eq_done()`, `dp_is_symbol_locked()`, `dp_is_interlane_aligned()`, `is_repeater()`, `dp_is_max_vs_reached()`, `dp_get_cr_failure()`, `dp_check_interlane_aligned()`.
- Conversion/timing: `get_dpcd_link_rate()`, `dp_hw_to_dpcd_lane_settings()`, `dp_wait_for_training_aux_rd_interval()`, `dp_training_pattern_to_dpcd_training_pattern()`, `dp_initialize_scrambling_data_symbols()`, `dp_translate_training_aux_read_interval()`, `dp_get_nibble_at_index()`, `dp_get_eq_aux_rd_interval()`, `dp_check_dpcd_reqeust_status()`.

## Control Flow And Integration
Specialized modules include this header to share DPCD conversion, status parsing, lane-setting decisions, and top-level type definitions. Higher-level code calls the retry or single-training entry points, while capability verification uses training helpers to validate link caps.

## State, Risks, And Test Signals
These declarations touch most DP training state: `dc_link`, `link_resource`, `pipe_ctx`, `link_training_settings`, DPCD registers, PHY patterns, and trace state. Risks are broad API coupling and misspelled exported names such as `dp_check_dpcd_reqeust_status()` that must remain ABI/source-compatible. Test signals include compile coverage for all specialized training modules and runtime coverage for lane status, DPCD writes, LTTPR offsets, training retries, and encoding-specific paths.
