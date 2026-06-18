# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu_frac.c

## Purpose
`ccu_frac.c` provides helper functions for PLLs with two hardware fractional output selections. It is used by multiplier and N/M clock classes when a requested exact fractional rate is supported.

## Important APIs, Types, And Functions
Important APIs are `ccu_frac_helper_is_enabled()`, `enable()`, `disable()`, `has_rate()`, `read_rate()`, and `set_rate()`, all exported in the `SUNXI_CCU` namespace.

## Control Flow
Callers first check feature support, then either read the select bit to return one of two rates or update the select bit under the shared CCU spinlock. `set_rate()` waits for the PLL lock after changing selection.

## State And Persistence
No software state is persisted. The fractional enable and select bits in the PLL register are the only state.

## Dependencies And Integration Points
It depends on CCF for names/debug, MMIO access, spinlocks, and `ccu_common`. It integrates with `ccu_nm` and `ccu_mult` descriptors carrying `CCU_FEATURE_FRACTIONAL`.

## Risks
The enable bit is active-low in this helper, so inverted semantics are easy to break. Only two exact rates are supported; unsupported rates must return `-EINVAL` so normal factor search can proceed.

## Test Signals
Test by requesting known fractional video/VE/ISP/audio PLL rates and checking clk-summary/readback, plus validating non-fractional rates still disable fractional mode.
