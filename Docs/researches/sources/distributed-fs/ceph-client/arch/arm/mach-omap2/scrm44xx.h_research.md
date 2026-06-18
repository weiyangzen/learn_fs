# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/scrm44xx.h

## Purpose
Defines OMAP44xx SCRM base address, register address macro, and CLKSETUPTIME fields.

## APIs, Flow, And State
`OMAP44XX_SCRM_REGADDR(reg)` maps SCRM registers. The header exposes `OMAP4_SCRM_CLKSETUPTIME` and its `DOWNTIME` and `SETUPTIME` masks/shifts. There is no runtime state.

## Dependencies And Integration
Used by PRCM/clock setup code through SCRM DT nodes and TI clock provider initialization. It complements PRM/CM register headers for OMAP4/5 SCRM partitions.

## Risks And Test Signals
Incorrect setup/downtime fields can affect system clock setup timing around low-power transitions. Test signals are clock provider initialization for `ti,omap4-scrm`/`ti,omap5-scrm` and stable suspend/resume clock behavior.
