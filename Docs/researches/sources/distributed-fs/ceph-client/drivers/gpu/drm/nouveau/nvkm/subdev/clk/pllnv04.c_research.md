# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/pllnv04.c

## Purpose
Implements NV04-era single-stage and double-stage PLL coefficient search used by legacy clock and devinit code.

## Important APIs, types, and functions
Exports `nv04_pll_calc()`. Internal helpers `getMNP_single()` and `getMNP_double()` search M/N/P or M1/N1/M2/N2/P combinations under BIOS voltage-controlled oscillator and input-frequency limits.

## Control flow
Single-stage search adjusts M constraints for older chips, iterates post-divider and M/N values, and tracks closest output. Double-stage search chooses a log2 post-divider, walks first-stage and second-stage ranges, applies fixed-gain and old-chip ratio constraints, and tracks the closest output. The public wrapper selects single or double search based on `vco2.max_freq` and caller-provided pointers.

## State and persistence
No persistent state. Outputs are raw coefficient fields later packed into PLL registers.

## Dependencies and integration points
Depends on BIOS PLL limits, chip version, and common NVKM logging. Used by `nv04.c`, `nv40.c`, `mcp77.c`, `nv50.c`, and devinit PLL paths.

## Risks
Legacy hardware quirks are embedded in search bounds. Incorrect max-M or VCO adjustments can produce coefficients that work on one chip family but not another.

## Test signals
Known-clock coefficient comparisons, display pixel-clock setup, memory PLL programming on NV3x/NV4x/NV50, and error logging when no acceptable values exist.
