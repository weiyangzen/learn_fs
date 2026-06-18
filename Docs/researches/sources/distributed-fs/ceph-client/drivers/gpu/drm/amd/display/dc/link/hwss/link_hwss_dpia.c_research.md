# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_dpia.c

## Purpose

`link_hwss_dpia.c` implements a DIO-style HWSS variant for USB4 DPIA endpoints. It reuses DIO stream/audio sequencing but customizes DP link output, test-pattern behavior, lane settings, and MST allocation updates for tunneled DP over DPIA.

## Important APIs, Types, And Functions

- `update_dpia_stream_allocation_table()` totals MST slots, calls `dc_process_dmub_set_mst_slots()` for the DPIA link index, logs previous slots, then optionally updates the DIO link encoder table.
- `set_dio_dpia_link_test_pattern()` only forwards `DP_TEST_PATTERN_VIDEO_MODE`; other patterns are ignored for DPIA.
- `set_dio_dpia_lane_settings()` is intentionally a no-op.
- `enable_dpia_link_output()` uses `enable_dpia_output()` when pre-training or unified assignment is enabled, passing DDC hardware instance, SST/MST DIG mode, and FEC readiness. Otherwise it falls back to `enable_dio_dp_link_output()`.
- `disable_dpia_link_output()` mirrors the enable path with `disable_dpia_output()` or normal DIO disable.
- `can_use_dpia_link_hwss()` requires flexible DIG mapping and either assignment support or a resolved DIO link encoder.

## Control Flow

The vtable extension block is initialized before base entries to match `link_hwss.h` layout. Stream encoder, attributes, and audio all dispatch to base DIO helpers. Link enable/disable resolve the link encoder according to `unify_link_enc_assignment`; if DPIA-specific encoder hooks exist, they are used, otherwise errors are logged or base DIO behavior is used depending on configuration.

## State And Persistence Behavior

The file mutates DMUB/DPIA MST slot state via `dc_process_dmub_set_mst_slots()`, link encoder output state, DIO stream encoder state through reused DIO helpers, and DP trace milestones. It does not own durable state; the software allocation table is owned by the caller and passed in.

## Dependencies And Integration Points

It depends on `link_hwss_dpia.h`, `link_hwss_dio.h`, `link_enc_cfg.h`, DIO link encoder functions, DMUB slot programming, and DP FEC decision service hooks. It is selected for USB4 DPIA links by generic HWSS selection and is used by DPMS MST/SST payload management.

## Risks And Edge Cases

- `status` and `prev_mst_slots_in_use` in `update_dpia_stream_allocation_table()` are static, which is unnecessary and could confuse concurrency analysis.
- Non-video test patterns are silently ignored for DPIA.
- Lane settings are a no-op, so training paths must not rely on source-side lane adjustment through this vtable.
- Missing `enable_dpia_output` or `disable_dpia_output` hooks only logs errors in DPIA mode.
- Slot total uses `uint8_t`; the valid DP MST slot range fits, but future expansion would need review.

## Test Signals

Use DPIA SST and MST bring-up, MST slot allocation/deallocation, FEC-ready combinations, unified and non-unified link encoder assignment, and pre-training enabled/disabled modes. DMUB MST slot logs, DP trace events, and USB4/DPIA HPD scenarios are key diagnostics.
