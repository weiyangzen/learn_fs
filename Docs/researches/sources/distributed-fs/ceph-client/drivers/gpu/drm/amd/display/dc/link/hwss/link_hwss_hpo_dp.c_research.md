# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_dp.c

## Purpose

`link_hwss_hpo_dp.c` implements link HWSS operations for HPO DP, the high-performance DP path used for 128b/132b DP 2.x style links. It programs HPO stream and link encoders, HPO-specific payload throttling, hblank symbol width, DP link PHY, MST allocation, and DP audio.

## Important APIs, Types, And Functions

- `set_hpo_dp_throttled_vcp_size()` programs VCP size on the HPO link encoder for a stream encoder instance.
- `set_hpo_dp_hblank_min_symbol_width()` derives hblank minimum symbol width from timing hblank, pixel clock, link bandwidth, and throttled VCP size.
- `setup_hpo_dp_stream_encoder()` enables an HPO stream encoder and maps it to an HPO link encoder.
- `reset_hpo_dp_stream_encoder()` disables the HPO stream encoder.
- `setup_hpo_dp_stream_attribute()` programs timing/colorimetry/DSC stream attributes and records a DP trace point.
- `enable_hpo_dp_link_output()` gates the symclk32 root clock on and enables link PHY using the legacy link encoder transmitter and HPD source.
- `disable_hpo_dp_link_output()` disables link, PHY, and clock gating.
- Static test-pattern and lane-setting helpers program HPO link test patterns and FFE.

## Control Flow

The vtable is HPO-specific for stream, link, audio, payload, and test operations. Enable flow checks `link_res->hpo_dp_link_enc`, turns on DCCG root clock gating if supported, and calls `enable_link_phy()`. Disable flow calls `link_disable()`, `disable_link_phy()`, and turns off the clock gate. The hblank helper guards division by checking effective DP bandwidth first.

## State And Persistence Behavior

The file mutates HPO stream encoder state, HPO link encoder state, DCCG clock gating state, audio packet state, and DP trace state. It relies on caller-owned `pipe_ctx->link_res` and `pipe_ctx->stream_res` assignments.

## Dependencies And Integration Points

It includes `dm_helpers.h`, `core_types.h`, `dccg.h`, and `clk_mgr.h`. DPMS payload code calls its vtable extensions for SST/MST 128b/132b allocation, throttled VCP, hblank symbol width, test patterns, and FFE.

## Risks And Edge Cases

- Missing HPO link encoder logs and returns, leaving higher layers responsible for failure handling.
- Hblank symbol width uses timing arithmetic with `pix_clk_100hz`; malformed timing can underflow hblank or divide badly if not validated.
- Lane settings use only `lane_settings[0].FFE_PRESET.raw`, assuming uniform FFE for the HPO encoder.
- `disable_hpo_dp_link_output()` indentation suggests nested operations but all are under the null check; functional behavior is still straightforward.

## Test Signals

Exercise DP 2.x SST and MST, DSC on HPO, VCP throttling, hblank symbol width updates, audio enable/disable, test patterns, FFE changes, and link output disable. Watch DCCG clock gate transitions and DP trace source sequence markers.
