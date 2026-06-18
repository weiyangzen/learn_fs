# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm_mpu44xx.c

## Purpose
Implements the minimal OMAP4 PRCM_MPU register accessor layer and stores the local MPU PRCM base address for early code.

## APIs, Flow, And State
Exports `struct omap_domain_base prcm_mpu_base`, `omap4_prcm_mpu_read_inst_reg(inst, reg)`, `omap4_prcm_mpu_write_inst_reg(val, inst, reg)`, and `omap2_set_globals_prcm_mpu(prcm_mpu)`. Reads and writes use relaxed MMIO through `OMAP44XX_PRCM_MPU_REGADDR`. State is the global `prcm_mpu_base.va`, populated during early platform setup and later copied into the partition table by `omap_prm_base_init()`.

## Dependencies And Integration
Includes PRCM MPU register definitions and CM register bits. Used by PRM instance code to expose the PRCM_MPU partition beside the global PRM partition, enabling CPU-local power/reset/clock registers to be accessed through the common PRM instance path.

## Risks And Test Signals
The base setter is marked transitional; if not called or mapped before use, local MPU PRCM access fails. Test signals include successful CPU power state reads/writes, CPU reset context access, and OMAP4 suspend paths that touch PRCM_MPU.
