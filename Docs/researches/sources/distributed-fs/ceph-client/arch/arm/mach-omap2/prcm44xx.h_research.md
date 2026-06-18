# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prcm44xx.h

## Purpose
Defines PRCM partition IDs for OMAP4, OMAP5, and DRA7xx register spaces. These IDs select between PRM, CM, SCRM, and local MPU PRCM base mappings.

## APIs, Flow, And State
The file exports partition constants such as `OMAP4430_PRM_PARTITION`, `OMAP4430_CM1_PARTITION`, `OMAP4430_PRCM_MPU_PARTITION`, `OMAP54XX_CM_CORE_PARTITION`, and `DRA7XX_MPU_PRCM_PARTITION`. `OMAP4_MAX_PRCM_PARTITIONS` sizes the partition base array in `prminst44xx.c`. There is no executable flow or stored state.

## Dependencies And Integration
Used by `prminst44xx.c`, `prm44xx.c`, OMAP4/5/DRA register headers, and PRCM MPU accessors. The partition values index `_prm_bases[]` and therefore are part of the ABI between generated register data and low-level accessors.

## Risks And Test Signals
Partition IDs are described as arbitrary but must remain stable with the array sizing and invalid partition convention. Bad IDs cause BUG_ON failures or register writes to the wrong PRCM block. Test signals are OMAP4/5/DRA PRM access, hardreset operations, and VP/VC register access.
