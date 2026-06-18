# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-half-divider.c

## Purpose
Provides a Rockchip composite clock helper for divider formulas of `rate = parent * 2 / (2 * val + 3)`, optionally combined with mux and gate components.

## Important APIs, Types, and Functions
`clk_half_divider_recalc_rate()` reads and applies the half-divider formula. `clk_half_divider_bestdiv()` searches for the best divider and may ask the parent to round rates. `clk_half_divider_determine_rate()` updates requested and parent rates. `clk_half_divider_set_rate()` writes hiword or RMW fields. `rockchip_clk_register_halfdiv()` constructs a composite mux/divider/gate clock.

## Control Flow, State, and Persistence
Persistent state is allocated CCF mux, divider, and gate components owned by the composite clock. Runtime state is the hardware fields. Set-rate uses the supplied spinlock when present.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on CCF composite APIs, MMIO, `HIWORD_UPDATE()`, and SoC branch tables. Risks include overflow in search, invalid widths, nonideal parent rounding, and allocation cleanup gaps. Test round-rate/set-rate/recalc consistency, parent propagation, hiword and RMW writes, and branches with missing mux or gate parts.
