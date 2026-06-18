# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/link/hwss/link_hwss_hpo_fixed_vs_pe_retimer_dp.c

## Purpose

`link_hwss_hpo_fixed_vs_pe_retimer_dp.c` specializes HPO DP sequencing for fixed voltage swing/pre-emphasis retimer paths. It reuses HPO DP stream/audio/payload operations and DIO retimer helpers while overriding HPO test-pattern, lane-setting, and link-output behavior for vendor retimer programming.

## Important APIs, Types, And Functions

- `dp_hpo_fixed_vs_pe_retimer_set_tx_ffe()` maps per-lane FFE preset levels and no-deemphasis/no-preshoot masks into vendor register bytes and writes them through `configure_fixed_vs_pe_retimer()`.
- `dp_hpo_fixed_vs_pe_retimer_program_override_test_pattern()` programs a vendor SQ128-style square pattern sequence.
- `dp_hpo_fixed_vs_pe_retimer_set_override_test_pattern()` gates on 128b/132b support, translates square patterns to PRBS31 on the HPO encoder, programs vendor overrides, or deprograms previous overrides.
- `set_hpo_fixed_vs_pe_retimer_dp_link_test_pattern()` wraps the override and sleeps 50 ms after most pattern changes for retimer lock.
- `set_hpo_fixed_vs_pe_retimer_dp_lane_settings()` avoids source FFE changes during PHY test patterns and directly programs retimer FFE for square-pattern overrides.
- `enable_hpo_fixed_vs_pe_retimer_dp_link_output()` preprograms four-lane fixed-VS state before normal HPO DP output.

## Control Flow

The vtable inherits most HPO DP operations. On test-pattern programming, square patterns are handled by setting a PRBS31 source pattern and then writing a vendor retimer square pattern sequence. Non-square patterns may deprogram older custom/square overrides before falling back to HPO link encoder test-pattern programming. Lane settings branch on `pending_test_pattern` to avoid conflicting with active PHY pattern output.

## State And Persistence Behavior

There is no private state. The file mutates retimer register state over AUX/DDC, HPO link encoder state, HPO stream/audio state through inherited functions, and trace state. Behavior depends on `link->cur_link_settings.lane_count`, `pending_test_pattern`, `current_test_pattern`, chip caps, and LTTPR DPCD capabilities.

## Dependencies And Integration Points

It includes `link_hwss_hpo_dp.h`, its own header, and `link_hwss_dio_fixed_vs_pe_retimer.h`. DP training/test code reaches it through the selected HWSS vtable when the link uses HPO DP and the fixed-VS external path capability is present.

## Risks And Edge Cases

- Vendor FFE and test-pattern byte tables are opaque, order-sensitive, and only lightly validated.
- FFE preset `level` indexes a 16-entry table; upstream validation must keep levels in range.
- Retimer lock delay is skipped only for TPS2 training mode; timing-sensitive monitors may need coverage around other transitions.
- The lane-setting logic intentionally does not update HPO source FFE during PHY patterns, which can surprise callers expecting uniform behavior.

## Test Signals

Test DP 2.x fixed-VS HPO links with two and four lanes, square PHY patterns, PRBS/custom transitions, TPS modes, FFE preset changes, and link-training retries. AUX write traces and 50 ms pattern-lock behavior are important diagnostics.
