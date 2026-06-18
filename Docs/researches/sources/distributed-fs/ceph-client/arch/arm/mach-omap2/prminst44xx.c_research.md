# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.c

## Purpose
Implements partitioned PRM instance access for OMAP4-style PRM blocks, including PRM/PRCM_MPU base table population, device PRM instance selection, hardreset operations, and global warm reset.

## APIs, Flow, And State
State includes `_prm_bases[OMAP4_MAX_PRCM_PARTITIONS]` and `prm_dev_inst`. `omap_prm_base_init()` copies global PRM and PRCM_MPU bases into the partition array. `omap4_prmst_get_prm_dev_inst()` and `omap4_prminst_set_prm_dev_inst()` manage the device instance used by VP/VC and reset code. Register APIs read, write, and RMW `base + inst + idx`, with BUG_ON validation for invalid partition or missing mapping. Hardreset deassert clears status, clears reset control, and polls status via `omap_test_timeout()`. `omap4_prminst_global_warm_sw_reset()` sets `OMAP4430_RST_GLOBAL_WARM_SW_MASK` and reads back as an OCP barrier.

## Dependencies And Integration
Depends on PRM/PRCM MPU headers, partition IDs, OMAP4 reset bits, and SoC detection headers. Used by `prm44xx.c`, hwmod reset paths, VP/VC accessors, and platform reboot.

## Risks And Test Signals
BUG_ONs make missing base initialization fatal rather than recoverable. `prm_dev_inst` must be set before device-level accesses. Test signals are OMAP4+ hardreset assert/deassert, PRM reset control, partitioned reads for PRM and PRCM_MPU, and global warm reboot.
