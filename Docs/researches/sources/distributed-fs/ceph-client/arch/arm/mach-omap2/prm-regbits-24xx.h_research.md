# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm-regbits-24xx.h

## Purpose
Defines OMAP24xx PRM-specific bit shifts and masks for power state forcing, autoidle, external voltage control, clock output, emulation, wake dependencies, and reset sources.

## APIs, Flow, And State
This is a macro-only register bit header. Notable constants include `OMAP24XX_FORCESTATE_MASK`, `OMAP24XX_AUTOIDLE_MASK`, voltage level setup shifts, `OMAP2420_CLKOUT2_*`, `OMAP24XX_CLKOUT_*`, wake dependency bits for MPU-to-MDM/DSP, and reset source shifts used by `prm2xxx.c`.

## Dependencies And Integration
Includes `prm2xxx.h` and is consumed by OMAP2 PRM implementation, clockdomain sleep/wakeup control, and reset-source mapping.

## Risks And Test Signals
OMAP2 uses reversed power state encodings compared with later OMAP generations, so these constants must be paired with the conversion code in `prm2xxx.c`. Test signals are OMAP24xx idle, wake dependency behavior, clock output setup, and reset source reports.
