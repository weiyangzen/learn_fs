# sources/distributed-fs/ceph-client/drivers/clk/st/clkgen-pll.c

## Purpose
This file implements ST PLL providers for PLL3200 C32 and PLL4600 C28 clock generator blocks, including A9 PLL variants and output divider clocks.

## Important APIs, Types, And Functions
`struct clkgen_pll_data` defines field locations for powerdown, lock, ndiv/idf/cp, output dividers, gates, and optional switch-to-PLL control. `struct clkgen_pll` is the registered PLL clock state. `struct stm_pll` carries computed parameters. Core ops include `clkgen_pll_enable()`, `clkgen_pll_disable()`, `recalc_stm_pll3200c32()`, `set_rate_stm_pll3200c32()`, `recalc_stm_pll4600c28()`, and `set_rate_stm_pll4600c28()`. `clkgen_c32_pll_setup()` registers a PLL and its ODF composite outputs for several `CLK_OF_DECLARE` compatibles.

## Control Flow
Setup obtains the parent clock, maps the parent register base, detects critical flags, registers the PLL clock, then registers one or more ODF composite clocks made from divider plus gate primitives. Enable powers the PLL, polls the lock bit with `readl_relaxed_poll_timeout()`, and optionally switches a mux to PLL. Disable optionally switches away then powers down. Rate setting computes valid ndiv/idf and charge-pump values, disables the PLL, writes fields under the lock when present, then re-enables.

## State And Persistence
PLL configuration persists in hardware registers. The driver caches ndiv/idf/cp in `struct clkgen_pll` during set-rate. Global spinlocks protect A9 PLL/mux and C32 ODF updates. Non-A9 C32 ops expose fixed-rate behavior with recalc but no set-rate.

## Dependencies And Integration Points
The file depends on `clkgen.h` field helpers, common clock APIs, OF early registration, and the A9 mux lock shared with `clkgen-mux.c`. Compatible strings include `st,clkgen-pll0`, `st,clkgen-pll1`, `st,stih407-clkgen-plla9`, and `st,stih418-clkgen-plla9`.

## Risks
PLL math has narrow legal ranges and may return zero rates on invalid requests. A missing lock bit or bad field definition can stall enable until timeout. Error paths after PLL registration do not fully unwind. The `err:` path attempts to free `pll_name`, which is a clock-owned name pointer and not an allocation from this function.

## Test Signals
Tests should verify rate calculations for known parent rates, A9 PLL rate transitions, lock timeout failure, ODF gate/divider behavior, critical flag propagation, and boot operation on DTs using both legacy and named-output compatibles.
