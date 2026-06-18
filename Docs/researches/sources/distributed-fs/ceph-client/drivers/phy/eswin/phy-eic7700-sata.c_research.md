# sources/distributed-fs/ceph-client/drivers/phy/eswin/phy-eic7700-sata.c

## Purpose
This platform driver exposes the ESWIN EIC7700 SATA PHY as a single Generic PHY. It programs reference-clock routing, TX amplitude and pre-emphasis tuning, LOS detection, AXI low-power request bits, and MPLL settings before releasing reset.

## Important APIs, types, and functions
`struct eic7700_sata_phy` stores tuning arrays, reset, regmap, clock, and PHY handle. `eic7700_get_tuning_param()` reads optional DT arrays and defaults per-generation values. `eic7700_sata_phy_init()` enables the clock, writes control registers, deasserts reset, and polls `SATA_P0_PHY_READY`. `eic7700_sata_phy_exit()` asserts reset and disables the clock.

## Control flow
Probe maps a shared/overlapping resource with `devm_ioremap()`, initializes a 32-bit regmap, reads tuning properties, gets clock `phy`, gets reset controls, creates one PHY, and registers a simple provider. Init writes tuning and static setup values, waits briefly, deasserts reset, then polls readiness.

## State and persistence behavior
Tuning arrays persist from probe. Hardware register state persists until reset or reinit. If readiness polling fails, the clock is disabled but reset is not explicitly reasserted in that error path.

## Dependencies and integration points
The driver uses Generic PHY, regmap-mmio, clocks, reset controls, platform resources, and compatible `eswin,eic7700-sata-phy`. It intentionally shares the HSP clock/reset address region.

## Risks and test signals
DT tuning values are not range-checked before field packing. The overlapping mapping relies on current resource ownership. The ready timeout is short. Test default and custom tuning, SATA Gen1/2/3 links, timeout injection, reset/clock errors, repeated init/exit, and HSP coexistence.
