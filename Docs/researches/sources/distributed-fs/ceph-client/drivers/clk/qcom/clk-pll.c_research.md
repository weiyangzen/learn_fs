# sources/distributed-fs/ceph-client/drivers/clk/qcom/clk-pll.c

## Purpose
Implements older Qualcomm PLL clock operations using L/M/N/config/mode/status registers. It supports direct PLL clocks, vote clocks that enable a parent PLL through an enable bit, SR configuration helpers, and an SR2 variant with explicit status polling.

## Important APIs, Types, And Functions
Exports `clk_pll_ops`, `clk_pll_vote_ops`, `clk_pll_sr2_ops`, `clk_pll_configure_sr()`, and `clk_pll_configure_sr_hpm_lp()`. Internal helpers include `clk_pll_enable()`, `clk_pll_disable()`, `clk_pll_recalc_rate()`, `find_freq()`, `clk_pll_determine_rate()`, `clk_pll_set_rate()`, `wait_for_pll()`, `clk_pll_vote_enable()`, `clk_pll_configure()`, `clk_pll_sr2_enable()`, and `clk_pll_sr2_set_rate()`.

## Control Flow
Direct enable skips already-enabled or FSM-mode PLLs, clears bypass, delays, deasserts reset, waits a fixed lock delay, and enables output. Set-rate looks up a frequency table entry, disables if currently enabled, writes L/M/N/config fields, and re-enables. Vote clocks call the generic regmap enable helper on the vote clock and then poll the parent PLL status. SR helpers configure fields and optionally enable FSM mode with different mode-register offsets. SR2 enable polls a status bit instead of fixed delay.

## State And Persistence
Hardware registers persist mode, L/M/N, config, status, and optional post-divider fields. Software state is descriptor-only: `struct clk_pll` points to register addresses, status bit, post-divider parameters, and a frequency table.

## Dependencies And Integration Points
Depends on CCF, regmap, delay helpers, qcom common helpers, and `clk-regmap`. SoC-specific clock drivers use `clk_pll_configure_sr*()` during probe and register PLLs or votes with the exported ops.

## Risks And Edge Cases
Frequency changes are limited to table entries. Direct enable uses a fixed 50 us delay and may miss lock failures unless using SR2/status paths. Vote enable assumes its parent is the actual `clk_pll` object. FSM mode is deliberately skipped by direct enable/disable, so descriptors must align with hardware ownership.

## Test Signals
Frequency table lookup, recalc with and without fractional M/N and post-divider, direct enable/disable, SR/SR2 status polling, vote enable timeout, and FSM-mode skip behavior are useful coverage.
