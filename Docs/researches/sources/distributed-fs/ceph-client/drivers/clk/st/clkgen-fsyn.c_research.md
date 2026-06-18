# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-fsyn.c

## Purpose
This file implements ST quad frequency synthesizer clock blocks. Each block has a PLL-like parent clock and up to four digital synthesizer channels with programmable `mdiv`, `pe`, `sdiv`, and optional `nsdiv` fields.

## Important APIs, Types, And Functions
`struct clkgen_quadfs_data` describes register fields and hardware polarity for a quadfs variant. `struct st_clk_quadfs_pll` models the block PLL, while `struct st_clk_quadfs_fsynth` models one output channel and caches the last programmed values. PLL ops are in `st_quadfs_pll_c32_ops`; channel ops are in `st_quadfs_ops`. Key math functions are `clk_fs660c32_vco_get_params()`, `clk_fs660c32_vco_get_rate()`, `clk_fs660c32_dig_get_params()`, and `clk_fs660c32_dig_get_rate()`. OF entries register variants `st,quadfs-pll`, `st,quadfs`, `st,quadfs-d0`, `st,quadfs-d2`, and `st,quadfs-d3`.

## Control Flow
`st_of_quadfs_setup()` maps the clock block registers, obtains the parent clock name, creates a private spinlock, registers a hidden PLL clock named from the node, then registers up to four channel clocks. PLL enable handles reset, bandwidth filter, ndiv programming, power-up polarity, and optional lock polling. Channel enable writes cached rate fields, exits standby, handles per-channel reset, and pulses the program-enable bit. `set_rate` computes best parameters and immediately programs them.

## State And Persistence
Hardware registers persist ndiv, standby, reset, enable, mdiv, pe, sdiv, and nsdiv state. The driver caches channel parameters so an enable after suspend or parent enable can reprogram hardware. The lock serializes selected field changes.

## Dependencies And Integration Points
It depends on `clkgen.h` register-field helpers, the common clock framework, OF address mapping, `clock-output-names` fallback for legacy bindings, and static names for known STiH D/C quadfs instances. Downstream display/audio/peripheral clocks consume the onecell channel provider.

## Risks
Frequency synthesis math is sensitive to overflow and rounding, though 64-bit arithmetic is used for the fractional path. Lock polling uses a jiffies timeout with busy wait. Some failures after partial registration leak early clocks. If hardware loses state and cached values were never initialized from a successful set or recalc, enable can restore zero parameters and produce a stopped output.

## Test Signals
Tests should cover valid and invalid PLL ranges, channel rate requests with expected rounded rates, enable/disable standby behavior, suspend/resume restoration, timeout handling when lock status never asserts, and functional consumers such as audio or display clocks.
