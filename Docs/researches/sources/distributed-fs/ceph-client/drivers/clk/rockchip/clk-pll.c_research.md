# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-pll.c

## Purpose
Implements Rockchip PLL clock registration and operations for RK3036/RK3328-style, RK3066/RK3188/RK3288-style, RK3399-style, and RK3588-style PLLs. Each PLL appears behind a mux that can select slow input, normal PLL output, or deep/32 kHz input while the underlying PLL owns rate calculation, set-rate, enable, disable, and optional init-time sync.

## Important APIs, Types, and Functions
`struct rockchip_clk_pll` stores the real PLL hardware, public mux, notifier field, register base, lock status location, PLL type, flags, copied rate table, shared CRU lock, and provider context. `rockchip_pll_determine_rate()` selects a supported table rate. Layout-specific helpers read parameters, recalc rates, set parameters, wait for lock, and expose ops for RK3036, RK3066, RK3399, and RK3588 families. `rockchip_clk_register_pll()` creates the mux, copies the rate table, selects ops, registers the real PLL, and returns the mux clock.

## Control Flow, State, and Persistence
Rate changes are table-driven. Set-params reads current settings, may switch the mux from normal to slow mode, writes new divider/fraction fields, waits for lock, tries restoring old settings on failure, and returns the mux to normal. RK3066 lock polling uses GRF; other layouts poll local lock bits. Enable clears powerdown and waits for lock; disable sets powerdown. Init sync can reconcile bootloader-programmed PLLs with table values.

## Dependencies, Integration Points, Risks, and Test Signals
The file depends on CCF, regmap, MMIO, polling helpers, `HIWORD_UPDATE()`, and Rockchip provider/type/rate-table definitions. Risks include incomplete rate tables, lock timeouts, recursive restore failures, RK3328 parent-count differences, and RK3588 core/DDR special cases. Test determine/set/recalc consistency, lock timeout handling, init sync, powerdown bits, and mux switching during rate changes.
