# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-inverter.c

## Purpose
Implements a simple Rockchip phase inverter clock. It exposes CCF phase operations for clocks whose hardware phase is either 0 or 180 degrees.

## Important APIs, Types, and Functions
`struct rockchip_inv_clock` stores hardware, register pointer, shift, flags, and lock. `rockchip_inv_get_phase()` returns 0 or 180 based on one bit. `rockchip_inv_set_phase()` accepts multiples of 180 and writes either with `HIWORD_UPDATE()` or RMW under lock. `rockchip_clk_register_inverter()` registers the phase-only clock.

## Control Flow, State, and Persistence
Hardware phase is one register bit. No cached phase exists. `CLK_SET_RATE_PARENT` lets rate requests propagate through the node.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on CCF phase APIs and MMIO. Risks include mapping 360 degrees to enabled inversion because `!!degrees` is used, wrong hiword flags, and missing lock in RMW mode. Test set/get at 0 and 180, rejection of 90 degrees, and register writes in hiword and RMW modes.
