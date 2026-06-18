# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-pll.c

## Purpose
This file implements CV18xx PLL clock operations for integral PLLs and fractional PLLs. It calculates rates from hardware fields, searches valid divider/programming combinations, writes PLL registers, handles power-down bits, and waits for lock.

## Important APIs, Types, And Functions
The exported operation tables are `cv1800_clk_ipll_ops` and `cv1800_clk_fpll_ops`. Integral helpers include `ipll_calc_rate()`, `ipll_recalc_rate()`, `ipll_find_rate()`, `ipll_determine_rate()`, `ipll_check_mode_ctrl_restrict()`, and `ipll_set_rate()`. Common PLL helpers include `pll_get_mode_ctrl()`, `pll_enable()`, `pll_disable()`, and `pll_is_enable()`.

Fractional helpers include `fpll_is_factional_mode()`, `fpll_calc_rate()`, `fpll_recalc_rate()`, `fpll_find_synthesizer()`, `fpll_find_rate()`, `fpll_determine_rate()`, `fpll_check_mode_ctrl_restrict()`, `fpll_set_rate()`, `fpll_get_parent()`, and `fpll_set_parent()`.

## Control Flow
Integral rate recalculation decodes pre-divider, divider, and post-divider fields and computes `parent * div / (pre * post)`. Integral set-rate searches all configured pre/div/post limits for the best rate not exceeding the target, computes mode and current-control fields, writes the masked PLL register under the shared lock, and waits for the lock status bit.

Fractional PLLs fall back to integral behavior when the synthesizer enable bit is clear. When fractional mode is active, recalculation reads the synthesizer set register and computes a rate using the fixed-point synthesizer factor. Set-rate searches PLL divider ranges and the synthesizer value, writes synthesizer and PLL registers under lock, then waits for lock. Fractional parent selection is modeled as parent index 0 for integral mode and 1 for fractional mode.

## State And Persistence
The PLL object stores register offsets, power-down bit, status bit, limit table, and optional synthesizer descriptor. Runtime state is in PLL control/status/synthesizer MMIO registers. Enabling clears the power-down bit; disabling sets it.

## Dependencies And Integration Points
The implementation uses CCF, Linux MMIO, spinlocks, `do_div`, limit descriptors from `clk-cv18xx-pll.h`, and common bit helpers. Top-level CV1800 clock declarations instantiate these PLL objects and mark critical PLLs.

## Risks
Several search functions ignore or do not propagate `-EINVAL` in callers; if no rate is found, set-rate may still proceed with zeroed programming. Fractional code indexes `pll->pll_limit[2]`, but the visible limit arrays in the top-level driver contain two entries, so this deserves immediate review for out-of-bounds access or missing fractional limit data. `fpll_find_synthesizer()` uses a binary-search-like loop where `trate` must be meaningful after loop exit; boundary behavior needs testing. Poll timeout only warns, allowing operation to continue after failed lock.

## Test Signals
Test integral PLL rate rounding across min/max limits and fractional PLL mode switching. Hardware tests should verify lock polling, power-down enable/disable, and measured output rates for MPLL/TPLL/A0PLL/DISPPLL/CAM PLLs. KASAN or UBSAN builds would be valuable for the fractional limit indexing risk.
