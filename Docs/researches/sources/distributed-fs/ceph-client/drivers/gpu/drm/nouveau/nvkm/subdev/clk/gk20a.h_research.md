# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.h

## Purpose
Defines GK20A GPCPLL register constants, PLL parameter structures, clock object layout, and shared helper prototypes for GK20A-derived Tegra GPU clock drivers.

## Important APIs, types, and functions
Important types are `struct gk20a_clk_pllg_params`, `struct gk20a_pll`, and `struct gk20a_clk`. Inline helpers include `gk20a_pllg_is_enabled()` and `gk20a_pllg_n_lo()`. The header exposes GK20A PLL MNP read/write/calc and clock lifecycle hooks.

## Control flow
The header itself has no runtime flow. Its inline helpers read `GPCPLL_CFG` to test enable state and compute the low safe NDIV from minimum VCO, parent rate, and M divider.

## State and persistence
No independent state is stored here. The structures define persistent per-clock driver state and the register macros identify persistent GPCPLL hardware state.

## Dependencies and integration points
Consumed by `gk20a.c`, `gm20b.c`, `gp10b.c`, and devfreq code. It ties common NVKM clock domains to Tegra GPCPLL register programming.

## Risks
Bitfield masks and register offsets are the contract for all GK20A-family clock code. A bad mask in this header affects multiple generations and can corrupt PLL coefficients.

## Test signals
Compile coverage across GK20A, GM20B, GP10B, and devfreq users; runtime validation of PLL enable reads, NDIV low calculation, and programmed rate readback.
