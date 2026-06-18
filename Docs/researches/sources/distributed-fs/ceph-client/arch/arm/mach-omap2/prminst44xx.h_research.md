# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prminst44xx.h

## Purpose
Declares OMAP4-style PRM instance accessors, device instance controls, hardreset helpers, global warm reset, and partition base initialization.

## APIs, Flow, And State
Defines `PRM_INSTANCE_UNKNOWN` and exposes `omap4_prmst_get_prm_dev_inst()`, `omap4_prminst_set_prm_dev_inst()`, `omap4_prminst_read_inst_reg()`, `omap4_prminst_write_inst_reg()`, `omap4_prminst_rmw_inst_reg_bits()`, `omap4_prminst_global_warm_sw_reset()`, hardreset assert/deassert/status APIs, and `omap_prm_base_init()`.

## Dependencies And Integration
Consumed by `prm44xx.c`, `prminst44xx.c`, voltage code, and OMAP4+ hwmod/powerdomain code. It is the public surface for partition-aware PRM access.

## Risks And Test Signals
The header intentionally exports low-level functions despite comments that this is not ideal, increasing the chance of direct register access bypassing higher-level locking or SoC checks. Test signals are compile coverage for OMAP4+ configs and hardreset/powerdomain users.
