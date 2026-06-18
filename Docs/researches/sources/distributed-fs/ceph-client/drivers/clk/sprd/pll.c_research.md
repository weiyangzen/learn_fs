# sources/distributed-fs/ceph-client/drivers/clk/sprd/pll.c

## Purpose
Implements adjustable Spreadtrum PLL clocks, including multi-register factor extraction, fractional rate calculation, PLL rate programming, ibias selection, and settle delays.

## Important APIs, Types, And Functions
Exports `sprd_pll_ops`. Key helpers are `sprd_pll_read`, `sprd_pll_write`, `pll_get_refin`, `pll_get_ibias`, `_sprd_pll_recalc_rate`, and `_sprd_pll_set_rate`. Bit-field macros (`pindex`, `pshift`, `pmask`, `pinternal_val`) interpret `struct clk_bit_field` descriptions.

## Control Flow
Rate recalculation allocates a config snapshot for all PLL registers, determines reference input, applies pre/post divider semantics, and computes integer or SDM fractional output. Rate setting allocates per-register masks/values, derives postdiv, DIV_S, SDM_EN, NINT, KINT, and IBIAS values, writes each changed register, verifies written bits, and delays if all writes matched.

## State And Persistence
PLL configuration persists in hardware registers. The driver stores factor metadata, register count, ibias threshold table, fractional constants, FVCO threshold, flag semantics, and delay.

## Dependencies And Integration Points
Depends on regmap, delay, slab allocation, and CCF. SoC PLL descriptors in SC9860/SC9863A provide the factor maps and ibias tables. PLL gates in `gate.c` often parent these PLLs.

## Risks And Edge Cases
Allocation failure returns parent rate or `-ENOMEM`. Read/write errors are mostly ignored except writeback comparison. `determine_rate` returns 0 without adjusting the request, so CCF may accept unsupported targets until set-rate quantizes them. Factor descriptions spanning registers must be exact, or rate math corrupts PLL programming. `do_div` mutates operands, so maintenance needs care.

## Test Signals
Hardware tests should verify PLL recalc against known register defaults, set-rate to representative integer and fractional targets, ibias field selection across thresholds, writeback verification failures, and required settle delays before consumers run.
