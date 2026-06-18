# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-hfpll.c

## Purpose
Implements legacy Qualcomm HFPLL clock ops. It initializes integer-mode PLL parameters, handles enable/disable sequencing, clamps and programs integer L rates, selects a low/high VCO through a user register, and validates bootloader-enabled PLL state.

## Important APIs, Types, And Functions
Exports `clk_ops_hfpll`. Internal helpers include `__clk_hfpll_init_once()`, `__clk_hfpll_enable()`, `clk_hfpll_enable()`, `__clk_hfpll_disable()`, `clk_hfpll_disable()`, `clk_hfpll_determine_rate()`, `clk_hfpll_set_rate()`, `clk_hfpll_recalc_rate()`, `clk_hfpll_init()`, and `hfpll_is_enabled()`.

## Control Flow
Initialization writes config, M=0, N=1, optional user/VCO bits, optional L value, and droop values once. Enable clears bypass, waits, deasserts reset, polls lock status or delays, then enables output under the PLL spinlock. Set-rate disables the PLL if it is currently enabled, selects VCO based on rate, writes L, and re-enables if needed. Init detects a bootloader-enabled PLL and disables/reinitializes it if the lock bit is inconsistent.

## State And Persistence
`struct clk_hfpll` stores a const hardware data pointer, `init_done`, embedded `clk_regmap`, and a spinlock. Hardware state persists in mode, L/M/N, user, droop, config, and status registers. The software `init_done` flag prevents rewriting defaults on every enable.

## Dependencies And Integration Points
Depends on regmap, CCF, spinlocks, delay/poll helpers, and descriptor definitions from `clk-hfpll.h`. SoC drivers instantiate `clk_hfpll` objects with `hfpll_data` register maps and register them through the CCF.

## Risks And Edge Cases
Rate programming assumes integer multiples of the parent and no active downstream consumers. The lock poll condition treats status bits according to platform-provided polarity, so bad `lock_bit` data can cause false success or timeout. `__clk_is_enabled()` is used under the lock, reflecting CCF state rather than raw hardware users.

## Test Signals
Enable sequencing, bootloader-enabled locked and unlocked cases, VCO bit selection around `low_vco_max_rate`, min/max rate clamping, set-rate while enabled, and droop/config writes are useful tests.
