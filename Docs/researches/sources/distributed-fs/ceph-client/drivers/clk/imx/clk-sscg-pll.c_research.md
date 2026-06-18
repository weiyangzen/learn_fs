# sources/distributed-fs/ceph-client/drivers/clk/imx/clk-sscg-pll.c

## Purpose
Implements spread-spectrum-capable SSCG PLL clocks used by i.MX8M SoCs. It supports normal two-stage PLL mode, stage-1 bypass, stage-2 bypass, parent switching, rate search, prepare/unprepare, and lock polling.

## Important APIs, Types, And Functions
`struct clk_sscg_pll_setup` stores computed dividers, VCOs, output, reference rates, bypass mode, and error. `struct clk_sscg_pll` stores clock object, base, setup, and parent indexes. Search helpers include `clk_sscg_pll_find_setup()`, `clk_sscg_pll1_find_setup()`, `clk_sscg_pll2_find_setup()`, and divider lookup helpers for divr/divf/divq. Clock ops include `clk_sscg_pll_prepare()`, `clk_sscg_pll_unprepare()`, `clk_sscg_pll_recalc_rate()`, `clk_sscg_pll_set_rate()`, `clk_sscg_pll_get_parent()`, `clk_sscg_pll_set_parent()`, and `clk_sscg_pll_determine_rate()`. Exported factory is `imx_clk_hw_sscg_pll()`.

## Control Flow
Determine-rate first tries full bypass if parent can supply the target directly, then stage-1 bypass, then normal mode. Each mode constrains parent/reference/VCO/output ranges and searches divider combinations for an exact or closest output. Set-rate writes bypass bits and divider fields from the previously computed setup, then waits for lock unless bypassed. Recalc decodes current divider fields and bypass bits.

## State And Persistence Behavior
Hardware state is in `PLL_CFG0` and `PLL_CFG2`. The last computed setup is stored in the clock object and consumed by set-rate/parent operations. No PM state is saved in this file.

## Dependencies And Integration Points
Used by i.MX8MQ clock registration for SYS3, DRAM, and VIDEO2 PLLs. Depends on common clock framework, bitfield helpers, MMIO, lock polling, and exported factory use from `clk.h`.

## Risks
`set_parent()` ignores the requested index and applies `setup.bypass`, so it must follow determine-rate/setup calculations. Divider search ranges are large but bounded; closest-rate fallback depends on `fout_error` initialization. Bypass and lock semantics must match hardware or boot-critical PLLs can hang.

## Test Signals
Rate round/set/recalc tests for bypass2, bypass1, and normal modes; DRAM/SYS3/VIDEO2 boot clocks on i.MX8M; lock timeout testing; and parent switching through assigned clocks.
