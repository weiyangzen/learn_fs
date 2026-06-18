# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/protocols/link_dp_training_128b_132b.c

## Purpose
`link_dp_training_128b_132b.c` implements DP2 128b/132b training policy and sequences. It handles TX FFE preset lane settings, channel EQ done polling, CDS done polling, 128b/132b AUX read intervals, DP2-specific failure statuses, and default training settings for UHBR links.

## Important APIs And Functions
- `dp_perform_128b_132b_link_training()` is the exported DP2 training sequence.
- `decide_128b_132b_training_settings()` initializes `link_training_settings` for DP2/UHBR training.
- `dp_decide_128b_132b_lttpr_mode()` chooses non-transparent mode when LTTPRs are present.
- Internal `dpcd_128b_132b_set_lane_settings()` writes all DPCD lane preset settings starting at `DP_TRAINING_LANE0_SET`.
- Internal `dpcd_128b_132b_get_aux_rd_interval()` reads and converts the DP2 AUX read interval register.
- Internal channel EQ and CDS sequence functions poll status and enforce loop/time limits.

## Control Flow
`dp_perform_128b_132b_link_training()` optionally falls back to legacy 8b/10b training when `debug.legacy_dp2_lt` is set. Otherwise it writes link settings, performs channel EQ, then performs CDS. Channel EQ sends TPS1 over main link, writes TPS1 to DPCD, reads AUX interval and lane adjust, decides FFE presets, switches hardware to TPS2, writes TPS2 plus lane settings in one AUX transaction, then loops until channel EQ is done, loop count is exceeded, `LT_FAILED_128b_132b` appears, or an AUX read aborts. It then waits for EQ interlane alignment until timeout or failure.

The CDS sequence writes the CDS training pattern and loops until symbol lock plus CDS interlane alignment, DP2 LT failure, timeout, or AUX abort.

`decide_128b_132b_training_settings()` sets downspread policy, CR/EQ/CDS patterns, EQ and CDS timing limits, loop count limit, disallows per-lane settings, chooses LTTPR mode, and initializes DPCD lane settings from default hardware settings.

## State And Persistence
The file mutates `link_training_settings` fields, DPCD link settings, DPCD training pattern/lane registers, hardware training pattern and lane settings through generic PHY helpers, and reads DPCD lane/status/adjust/aux-interval fields. It reads `link->dpcd_caps.lttpr_caps.phy_repeater_cnt` to size CDS wait time and choose LTTPR behavior.

## Dependencies And Integration Points
It depends on generic training helpers, legacy 8b/10b training for debug fallback, DPCD helpers, DP PHY programming, and capability predicates for LTTPR presence. It is dispatched by `dp_perform_link_training()` whenever the selected link settings use 128b/132b encoding.

## Risks And Edge Cases
- DP2 timing depends on DPCD AUX interval values that can be as large as 256 ms; timeout constants need to match spec and LTTPR depth.
- Initial default FFE preset settings are zero unless overrides or lane adjust requests change them.
- Channel EQ and CDS split status conditions; a sink that reports partial progress can run until loop/time limits.
- Debug `legacy_dp2_lt` intentionally uses 8b/10b logic on DP2 settings and should remain test-only.
- All lane settings are written as the full `dpcd_lane_settings` array, not just active lanes.

## Test Signals
Test UHBR10/UHBR13.5/UHBR20 training, channel EQ done, EQ interlane timeout, CDS done, CDS timeout, LT_FAILED handling, AUX abort handling, FFE preset adjustment loops, LTTPR and no-LTTPR wait limits, debug legacy path, and integration with generic fallback/retry handling.
