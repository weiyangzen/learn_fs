# sources/distributed-fs/ceph-client/drivers/clk/rockchip/clk-mmc-phase.c

## Purpose
Implements Rockchip MMC sample/drive phase clocks. It models a fixed divide-by-2 rate plus phase controls built from 90-degree coarse steps and optional fine delay elements, with register access through either CRU MMIO or GRF regmap.

## Important APIs, Types, and Functions
`struct rockchip_mmc_clock` stores hardware, register or GRF location, shift, cached phase, and a rate-change notifier. `rockchip_mmc_recalc()` returns parent/2. `rockchip_mmc_get_phase()` decodes coarse and fine delay fields. `rockchip_mmc_set_phase()` computes fields and writes a hiword value. `rockchip_mmc_clk_rate_notify()` caches and restores phase around rate decreases. `rockchip_clk_register_mmc()` registers the clock and notifier.

## Control Flow, State, and Persistence
Phase is stored in hardware and cached transiently during rate-change notifications. On rate decreases, PRE stores the old phase and POST restores it. The initial `cached_phase` is not explicitly initialized before notifier use.

## Dependencies, Integration Points, Risks, and Test Signals
The helper depends on CCF phase/notifier APIs, regmap, MMIO, and MMC host tuning. Risks include approximate fine-delay math, restoration only on downward changes, uninitialized cached phase, and invalid parent rate. Test MMC tuning across rates, get/set phase round trips, CRU and GRF writes, notifier behavior, and high-speed sampling modes.
