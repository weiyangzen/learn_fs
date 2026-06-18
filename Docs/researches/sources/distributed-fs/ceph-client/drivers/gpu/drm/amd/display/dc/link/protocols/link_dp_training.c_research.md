# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training.c

## Purpose
`link_dp_training.c` implements generic DP link training helpers and top-level training orchestration. It converts link settings into DPCD encodings, chooses training patterns, configures LTTPR and channel coding, reads lane status/adjust requests, applies overrides, dispatches specialized training sequences for 8b/10b, 128b/132b, DPIA, auxless, and fixed-VS retimer cases, exits training mode, transitions to video idle, handles post-link-training adjustment, traces results, and retries/falls back when training fails.

## Important APIs And Functions
- Logging/conversion: `dp_log_training_result()`, `dp_initialize_scrambling_data_symbols()`, `dp_training_pattern_to_dpcd_training_pattern()`, `dp_get_nibble_at_index()`, `get_dpcd_link_rate()`, `dp_translate_training_aux_read_interval()`.
- Status checks: `dp_get_cr_failure()`, `dp_is_max_vs_reached()`, `dp_is_cr_done()`, `dp_is_ch_eq_done()`, `dp_is_symbol_locked()`, `dp_is_interlane_aligned()`, `dp_check_interlane_aligned()`, `dp_check_link_loss_status()`.
- DPCD status read/write: `dp_get_lane_status_and_lane_adjust()`, `dpcd_set_training_pattern()`, `dpcd_set_link_settings()`, `dpcd_set_lane_settings()`, `dpcd_set_lt_pattern_and_lane_settings()`, `dpcd_configure_channel_coding()`.
- Training policy: `dp_get_lttpr_mode_override()`, `override_training_settings()`, `decide_cr_training_pattern()`, `decide_eq_training_pattern()`, `dp_decide_lttpr_mode()`, `dp_decide_lane_settings()`, `dp_decide_training_settings()`.
- LTTPR control: `configure_lttpr_mode_transparent()`, internal non-transparent configuration, `dpcd_configure_lttpr_mode()`, `repeater_training_done()`.
- Hardware pattern control: `start_clock_recovery_pattern_early()`, `dp_set_hw_test_pattern()`, `dp_set_hw_training_pattern()`.
- Top-level flows: `dp_perform_link_training()` and `perform_link_training_with_retries()`.

## Control Flow
`dp_perform_link_training()` first selects training settings by encoding, applies caller/debug/BIOS overrides, exits any previous training mode, configures LTTPR mode, prepares FEC for 8b/10b, writes channel coding, and then dispatches to fixed-VS 8b/10b, normal 8b/10b, or 128b/132b training. It exits training mode again, aborts DPIA training if necessary, optionally transitions to video idle, performs post-LT adjustment/link-loss checks, logs the result, and increments debug failure count on failure.

`perform_link_training_with_retries()` is the commit-time retry loop. It may preconfigure the stream encoder for 8b/10b SST, enables PHY for each attempt, honors sink power-up delay, sets eDP ASSR/panel mode, handles aux-disabled training, chooses legacy DPIA training or consolidated generic training, records trace counters, updates MST DPIA verified bandwidth after success, disables PHY between attempts, detects unplug after aborts, and either retries original settings or falls back to lower bandwidth while checking whether stream bandwidth still fits.

Lane-status reads use DPRX addresses or per-LTTPR repeater addresses depending on `offset`. Lane adjustment decisions convert DPCD requests to hardware lane settings, optionally maximize settings across lanes when per-lane settings are disallowed, and apply override values.

## State And Persistence
The file mutates `link_training_settings`, `link->dpcd_caps.lttpr_caps.mode` and LTTPR aux intervals, `link->cur_link_settings` and lane settings through PHY helpers, `link->fec_state`, DPCD training/link/lane/channel-coding registers, trace counters/timestamps, `link->ctx->dc->debug_data.ltFailCount`, `link->verified_link_cap` for DPIA MST fallback outcomes, and eDP panel mode/ASSR state.

## Dependencies And Integration Points
It integrates with specialized training modules (`8b_10b`, `128b_132b`, auxless, DPIA, fixed-VS retimer), DPCD helpers, DP trace, DP PHY, DP capability encoding/FEC policy, eDP panel control, link detection/validation, link encoder configuration, resources, and DM helpers for MST bandwidth updates.

## Risks And Edge Cases
- DPCD training operations must avoid non-LT AUX transactions while training mode is active; the top-level sequence documents this requirement.
- `dp_check_dpcd_reqeust_status()` only treats failed DPCD requests as abort-worthy for DPIA.
- LTTPR non-transparent mode handling differs for 8b/10b and 128b/132b and clears the DPTX-to-DPIA hop aux interval in some cases.
- Post-LT adjustment only applies when supported and TPS4 is not used.
- Retry/fallback logic tracks `is_link_bw_low` and `is_link_bw_min`; mistakes can train a link that cannot carry the stream or loop too long.
- Several paths rely on debug/preferred overrides and hardware workarounds, so capability and training state can diverge intentionally.

## Test Signals
Test 8b/10b and 128b/132b training, DPIA consolidated vs legacy training, aux-disabled path, fixed-VS retimer training, LTTPR transparent/non-transparent/no-LTTPR modes, training pattern DPCD encodings, link-rate-set eDP training, lane status/adjust parsing for DPRX and repeaters, post-LT adjust requests, link-loss check after video idle, FEC ready/enable, retry and fallback behavior, unplug aborts, MST DPIA bandwidth updates, and debug/preferred overrides.
