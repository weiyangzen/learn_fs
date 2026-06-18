# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm7xx.h

## Purpose
Defines DRA7xx PRM base address, PRM instance offsets, clockdomain offsets, and a CKGEN system clock select address.

## APIs, Flow, And State
`DRA7XX_PRM_REGADDR(inst, reg)` maps DRA7xx PRM registers. Instance offsets cover MPU, DSP1/DSP2, IPU, COREAON, CORE, IVA, CAM, DSS, GPU, L3INIT, L4PER, CUSTEFUSE, WKUPAON, EMU, EVE1-4, RTC, VPE, and DEVICE. `DRA7XX_CM_CLKSEL_SYS` exposes a CKGEN register address. This header is declarative.

## Dependencies And Integration
Includes `prcm-common.h`, shared OMAP4/5 PRM declarations, and `prm.h`. Used by DRA7xx PRM init data and PRM instance access.

## Risks And Test Signals
DRA7xx has many accelerator instances, so offset drift impacts hardreset/power management for DSP/IPU/EVE/IVA/GPU domains. Test signals are DRA7xx boot, device reset control, powerdomain transitions, and system clock select access.
