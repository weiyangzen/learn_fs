# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gk20a.c

## Purpose
Implements Tegra GK20A GPU GPC clock control using the GPCPLL, static pstate table, dynamic NDIV sliding, PLL enable/disable sequencing, and devfreq initialization.

## Important APIs, types, and functions
Exports shared helpers declared in `gk20a.h`: `gk20a_pllg_read_mnp()`, `gk20a_pllg_write_mnp()`, `gk20a_pllg_calc_rate()`, `gk20a_pllg_calc_mnp()`, `gk20a_clk_read()`, `gk20a_clk_calc()`, `gk20a_clk_prog()`, `gk20a_clk_setup_slide()`, `gk20a_clk_fini()`, `gk20a_clk_ctor()`, and `gk20a_clk_new()`.

## Control flow
PLL calculation searches M/N/PL under VCO and input-frequency limits, preferring the lowest usable VCO and closest target. Programming tries an NDIV slide when M and PL are unchanged; otherwise it slides down to a safe low NDIV, programs MNP through bypass with output divider staging, re-enables and locks the PLL, then slides up. Init exits IDDQ, initializes GPC2CLK output, configures slide step parameters from the Tegra parent clock, programs the lowest pstate, and starts devfreq.

## State and persistence
State is in `struct gk20a_clk`: PLL params, cached target PLL, parent rate, conversion callbacks, and devfreq pointer. Hardware state persists in GPCPLL coefficient/config, NDIV slowdown, SEL_VCO, and GPC2CLK_OUT registers.

## Dependencies and integration points
Depends on Tegra platform clock rate, NVKM timer waits, the common clock pstate engine, and `gk20a_devfreq_init()`. Static pstates cover 72 MHz through 852 MHz with voltage IDs.

## Risks
Dynamic ramp completion has a 500 usec timeout, and fallback full programming still depends on PLL lock. Parent rates outside the known table fail init. Incorrect PL/div conversion would make reported and programmed rates diverge.

## Test signals
Boot init at lowest pstate, devfreq OPP registration, rate readback after every pstate, NDIV slide timeout logs, suspend/fini IDDQ behavior, and parent-rate validation on 12/12.8/13/19.2/38.4 MHz Tegra clocks.
