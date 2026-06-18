# sources/distributed-fs/ceph-client/drivers/clk/sophgo/clk-cv18xx-ip.c

## Purpose
This file implements the non-PLL CV18xx clock classes: gates, dividers, bypass dividers, muxes, bypass muxes, dual-path multi-muxes, and audio fractional clocks. These `clk_ops` power the static clock objects declared in `clk-cv1800.c`.

## Important APIs, Types, And Functions
The exported operation tables are `cv1800_clk_gate_ops`, `cv1800_clk_div_ops`, `cv1800_clk_bypass_div_ops`, `cv1800_clk_mux_ops`, `cv1800_clk_bypass_mux_ops`, `cv1800_clk_mmux_ops`, and `cv1800_clk_audio_ops`.

Shared helpers include `div_helper_set_rate()`, `div_helper_get_clockdiv()`, `div_helper_determine_rate()`, `div_is_better_rate()`, and `mux_helper_determine_rate()`. Gate callbacks just set or clear the gate bit. Divider callbacks compute divider values with CCF divider helpers and handle hardware initial values via `DIV_FACTOR_SEL`. Mux callbacks read/write parent fields. Bypass variants treat parent index 0 as bypass/raw parent and parent index 1+ as divided/muxed paths. Multi-mux callbacks use two divider/mux register banks plus `parent2sel` and `sel2parent` lookup tables. Audio callbacks program M/N fractional registers for a fixed target rate using `gcd()`.

## Control Flow
Rate determination generally loops possible parents unless `CLK_SET_RATE_NO_REPARENT` is set. For each parent, a class-specific round function computes a candidate rate, and the best candidate is selected according to closest-rate or not-greater-than-target semantics. Set-rate writes divider fields under the shared spinlock. Parent changes on muxes write field registers; bypass classes set or clear bypass bits.

The multi-mux class has more complex flow: bypass forces parent 0 and raw parent rate; otherwise `clk_sel` selects one of two mux/divider banks. `mmux_set_parent()` sets bypass for oscillator/invalid paths, clears bypass for normal paths, toggles `clk_sel`, then writes the selected mux field. Audio set-rate computes `m = parent/2/gcd(parent/2, rate)` and `n = rate/gcd(parent/2, rate)`, writes M/N, then enables and updates the divider.

## State And Persistence
The class instances are static objects with descriptors for gate bits, divider fields, mux fields, bypass bits, and lookup tables. Persistent hardware state is in MMIO registers. The shared spinlock serializes most write paths, but some helper calls perform their own locked read-modify-write operations.

## Dependencies And Integration Points
The implementation depends on CCF divider/mux helpers, `clk_rate_request`, Linux MMIO, spinlocks, `gcd()`, and common CV18xx bit helpers. It integrates with the top-level CV1800 driver through macro-generated objects and `devm_clk_hw_register()`.

## Risks
`mmux_set_rate()` returns `parent_rate` when bypass is active even though the callback returns `int`, which is unusual and should be reviewed. `mmux_set_parent()` calls bit helpers that lock internally, then later takes the lock for mux-field writes; the overall parent transition is not atomic across bypass/selector/mux fields. Several paths rely on lookup tables being correct; an invalid parent index can trigger `BUG()` in `mmux_get_parent_id()`. Audio M/N calculations do not validate field-width overflow before writing.

## Test Signals
Exercise enable/disable/is_enabled for each class. Rate tests should cover fixed dividers, writable dividers, bypass active/inactive behavior, mux parent changes, multi-mux C906/A53 parent selections, and audio rate programming to 24.576 MHz. Concurrent parent/rate-change stress tests are especially useful for multi-mux paths.
