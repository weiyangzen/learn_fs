# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gm20b.c

## Purpose
Implements GM20B Tegra GPU clocking, including GK20A-compatible legacy mode for speedo 0 parts and noise-aware PLL/DVFS programming for speedo >= 1 parts.

## Important APIs, types, and functions
Key structures are `struct gm20b_clk`, `struct gm20b_pll`, and `struct gm20b_clk_dvfs`. Important functions include `gm20b_clk_new()`, `gm20b_clk_calc()`, `gm20b_clk_prog()`, `gm20b_clk_init()`, `gm20b_clk_init_dvfs()`, fused-parameter parsing, safe-fmax calculation, DVFS coefficient programming, and GM20B-specific PLL slide/program helpers.

## Control flow
Speedo 0 delegates to GK20A-style PLL programming with fewer pstates. Speedo >= 1 duplicates PLL parameter limits, clamps M for NAPLL operation, reads fuse calibration if available, computes safe minimum-voltage frequency, and initializes DVFS. Reclocking computes target PLL and voltage-derived DFS settings, optionally steps through a safe frequency before changing voltage-detection coefficients, then slides/programs the PLL to the final rate.

## State and persistence
State includes current and pending PLL/DVFS settings, current and target microvolts, fused ADC slope/offset, safe fmax, and GK20A base clock state. Hardware state spans GPCPLL, BYPASSCTRL_SYS, DVFS coefficient/calibration registers, fuse-derived settings, and devfreq counters.

## Dependencies and integration points
Depends on Tegra speedo/fuse data, NVKM volt tables, GK20A PLL helpers, devfreq, timer waits, and common pstate policy. It integrates with voltage sequencing in `clk/base.c` by computing new UV during `calc()`.

## Risks
Voltage/frequency ordering is safety-critical. Bad fused calibration, zero slope, or safe-fmax evaluation can put the PLL above the F/V curve during voltage changes. The code has fallback legacy mode only when NAPLL parameter clamping fails.

## Test signals
Speedo 0 and speedo >= 1 boot paths, fuse-present and calibration fallback logs, safe-fmax debug output, DVFS calibration timeout, pstate transitions across voltage increases/decreases, and devfreq governor behavior.
