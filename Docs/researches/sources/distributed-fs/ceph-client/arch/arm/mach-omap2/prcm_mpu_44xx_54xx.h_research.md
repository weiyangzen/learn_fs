# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu_44xx_54xx.h

## Purpose
Declares common PRCM_MPU access functions and the global PRCM_MPU base for OMAP44xx/54xx-style local MPU PRCM blocks.

## APIs, Flow, And State
Exports `prcm_mpu_base`, `omap4_prcm_mpu_read_inst_reg()`, `omap4_prcm_mpu_write_inst_reg()`, and `omap2_set_globals_prcm_mpu()`. These APIs abstract instance/register MMIO access while SoC-specific headers supply concrete offsets.

## Dependencies And Integration
Includes `prcm-common.h` outside assembly. Used by OMAP44xx, OMAP54xx, and DRA7xx PRCM MPU headers and implementation. It feeds `prminst44xx.c` partition setup through the shared `prcm_mpu_base`.

## Risks And Test Signals
The shared names are OMAP4-prefixed even when used by later SoCs, which can obscure SoC-specific register-layout differences. Test signals are compile coverage across OMAP4/5/DRA configs and successful local MPU PRCM register access.
