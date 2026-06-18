# sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/nvkm/subdev/clk/gp10b.c

## Purpose
Implements GP10B Tegra clock control using the platform clock framework/BPMP instead of direct Nouveau PLL register programming, while retaining static GPU pstates and GK20A devfreq support.

## Important APIs, types, and functions
Exports `gp10b_clk_new()`. Core hooks are `gp10b_clk_init()`, `gp10b_clk_read()`, `gp10b_clk_calc()`, and `gp10b_clk_prog()`. The static `gp10b_pstates` table covers 114.75 MHz through 1.3005 GHz.

## Control flow
Constructor stores the Tegra clock pointer and initializes static pstate list heads. Init starts at the highest pstate to match the BPMP default, then initializes devfreq. Calculation rounds the requested GPC rate through `clk_round_rate()`, and programming applies it with `clk_set_rate()` before caching actual rate.

## State and persistence
State lives in `struct gp10b_clk`: common NVKM clock state, Tegra `struct clk *`, pending rounded rate, actual rate, and devfreq pointer. Persistent hardware programming is owned by the Tegra clock provider.

## Dependencies and integration points
Depends on Linux common clock framework, Tegra device glue, common NVKM pstate logic, and `gk20a_devfreq_init()`. It is selected for chipset `0x13b` in devfreq lookup.

## Risks
Rate rounding may select a frequency different from the static pstate target; devfreq and pstate reporting need to use the actual rate. This path assumes BPMP/platform clock firmware enforces safe voltage and PLL sequencing.

## Test signals
Clock-framework rate readback, devfreq OPP registration, boot at highest pstate, target transitions through every pstate, and suspend/resume behavior through the shared devfreq helpers.
