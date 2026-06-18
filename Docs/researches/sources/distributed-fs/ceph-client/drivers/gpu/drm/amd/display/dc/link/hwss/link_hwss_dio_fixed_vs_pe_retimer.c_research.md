# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dio_fixed_vs_pe_retimer.c

## Purpose

`link_hwss_dio_fixed_vs_pe_retimer.c` specializes DIO DP hardware sequencing for external fixed voltage swing/pre-emphasis retimer paths. It reuses the normal DIO stream/audio/MST operations but overrides DP link output and test-pattern programming to emit vendor LTTPR/retimer configuration sequences over AUX/DDC.

## Important APIs, Types, And Functions

- `dp_dio_fixed_vs_pe_retimer_lane_cfg_to_hw_cfg()` maps current lane count to vendor DP type bytes, returning `0xF2` for four lanes and `0x12` otherwise.
- `dp_dio_fixed_vs_pe_retimer_exit_manual_automation()` writes a sequence of vendor register payloads through `configure_fixed_vs_pe_retimer()` to restore automation.
- `set_dio_fixed_vs_pe_retimer_dp_link_test_pattern_override()` handles 128b/132b retimer overrides for 80-bit custom and D102 patterns, including deprogramming old overrides.
- `set_dio_fixed_vs_pe_retimer_dp_link_test_pattern()` wraps the override path and falls back to `dp_set_phy_pattern`.
- `enable_dio_fixed_vs_pe_retimer_program_4lane_output()` writes five vendor payloads before four-lane output.
- `enable_dio_fixed_vs_pe_retimer_dp_link_output()` preprograms four-lane retimer state before normal DIO DP output.
- `requires_fixed_vs_pe_retimer_dio_link_hwss()` checks `link->chip_caps` for `AMD_EXT_DISPLAY_PATH_CAPS__DP_FIXED_VS_EN`.

## Control Flow

The static vtable is mostly the DIO vtable. Only `enable_dp_link_output` and `set_dp_link_test_pattern` are replaced. On link enable, four-lane settings trigger vendor retimer programming before the normal DIO PHY enable path. On test-pattern setup, the override path first gates on 128b/132b LTTPR support and non-null params, then either translates supported patterns into hardware pattern requests plus retimer writes or deprograms previous overrides and lets the caller fall back to the base link encoder pattern.

## State And Persistence Behavior

The file does not store private state. It changes retimer hardware state through repeated `link_srv->configure_fixed_vs_pe_retimer(link->ddc, data, len)` calls. It also depends on `link->current_test_pattern`, `pending_test_pattern` managed elsewhere, `cur_link_settings.lane_count`, and `dpcd_caps.lttpr_caps`.

## Dependencies And Integration Points

It includes `link_hwss_dio.h`, its own header, and `link_enc_cfg.h`. It integrates with DIO helpers, DP CTS/test-pattern code, DP training, and the link HWSS selector. The vendor payload transport is exposed by the DDC service through `link_srv`.

## Risks And Edge Cases

- Vendor byte sequences are opaque and order-sensitive.
- The lane configuration TODO notes missing USB-C orientation handling.
- Fallback pattern programming assumes a valid `link_enc`; unlike base DIO, the wrapper path does not assert-check after resolving it before fallback use.
- Override deprogramming is tied to `current_test_pattern` classifications; stale pattern state can leave retimer state mismatched.
- The 80-bit custom override only accepts a specific ten-byte pattern.

## Test Signals

Exercise DP 1.x and DP 2.x fixed-VS links, two-lane and four-lane modes, supported and unsupported PHY patterns, transitions from square/custom/D102 back to video, and link training retries. AUX/DDC transaction logs and DP trace entries after pattern setup and link PHY enable are primary diagnostics.
