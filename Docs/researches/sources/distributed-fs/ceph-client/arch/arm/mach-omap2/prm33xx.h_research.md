# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm33xx.h

## Purpose
Declares AM33xx PRM base address, register address macro, PRM instance offsets, key power/reset register offsets, and PRM init prototype.

## APIs, Flow, And State
`AM33XX_PRM_REGADDR(inst, reg)` maps PRM addresses through the AM33xx L4 wakeup IO window. Instance macros cover OCP socket, PER, WKUP, MPU, DEVICE, RTC, GFX, and CEFUSE. Register offsets include power state control/status for PER/WKUP/MPU/RTC/GFX/CEFUSE and device reset control. Declares `am33xx_prm_init()`.

## Dependencies And Integration
Includes `prcm-common.h` and `prm.h`. Used by AM33xx PRM implementation, clock/powerdomain tables, and assembly suspend code that references related CM/PRM layout.

## Risks And Test Signals
The header has both offset and resolved-address macros; call sites must choose register-offset macros for instance accessors and resolved addresses only for direct MMIO. Test signals are AM33xx PRM initialization, powerdomain callbacks, and reset control access.
