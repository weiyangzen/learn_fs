# sources/distributed-fs/ceph-client/drivers/clk/bcm/clk-kona.c

## Purpose
Implements Broadcom Kona CCU runtime clock operations: protected register access, policy engine control, gate management, hysteresis initialization, trigger commits, divider rate math, selector parent switching, and common-clock callbacks for peripheral clocks.

## Important APIs, Types, And Functions
Externally visible symbols are `scaled_div_max`, `kona_peri_clk_ops`, and `kona_ccu_init`. Important internals include `__ccu_write_enable`, `__ccu_wait_bit`, `__ccu_policy_engine_start`, `__ccu_policy_engine_stop`, `policy_init`, `__gate_commit`, `clk_gate`, `hyst_init`, `__clk_trigger`, `divider_read_scaled`, `__div_commit`, `divider_write`, `clk_recalc_rate`, `round_rate`, `selector_read_index`, `__sel_commit`, `selector_write`, and the `kona_peri_clk_*` callbacks.

## Control Flow
All hardware writes occur under the CCU spinlock with the write-access password enabled. Initialization walks CCU clocks and applies policy masks, gates, hysteresis, dividers, pre-dividers, and selectors. Runtime enable/disable toggles software-managed gates. Rate changes compute a scaled divisor, enable the clock if needed, write divider bits, pulse the trigger, then restore the previous gate state. Parent changes follow the same enable, write selector, trigger, restore pattern.

## State And Persistence
The CCU tracks `write_enabled` and serializes accesses with `lock`. Clock descriptors cache intended gate enabled state, selector index, and scaled divider value. Hardware registers persist actual gate status, policy masks, divider fields, selector fields, and trigger completion state.

## Dependencies And Integration Points
Integrates with descriptors from `clk-kona.h`, validation/setup in `clk-kona-setup.c`, Linux common clock callbacks, and DT onecell providers. Consumers invoke it through `clk_prepare_enable`, `clk_set_rate`, and parent-selection APIs.

## Risks And Edge Cases
Polling failures on gate or trigger commits return `-EIO`. Cached software state is reverted after failed divider/selector commits, but hardware may already be partially changed. The code uses `BUG_ON` for impossible descriptor states. `determine_rate` intentionally ignores `CLK_SET_RATE_NO_REPARENT` and does not propagate rate changes to parents.

## Test Signals
Signals include successful policy stop/start, gate status polling, no-disable gate behavior, selector readback with sparse hardware values, variable and fixed divider rounding, rate changes while initially disabled, trigger timeouts, and parent search selecting the closest achievable rate.
