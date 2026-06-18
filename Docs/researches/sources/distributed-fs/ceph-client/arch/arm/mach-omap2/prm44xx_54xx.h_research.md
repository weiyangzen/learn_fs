# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/prm44xx_54xx.h

## Purpose
Declares the common OMAP4/OMAP5 PRM voltage controller/processor accessor APIs and PRM init function.

## APIs, Flow, And State
Exports `omap4_prm_vcvp_read(offset)`, `omap4_prm_vcvp_write(val, offset)`, `omap4_prm_vcvp_rmw(mask, bits, offset)`, and `omap44xx_prm_init(data)`. The implementation dynamically selects the device PRM instance through `omap4_prmst_get_prm_dev_inst()`.

## Dependencies And Integration
Includes `prcm-common.h`. Used by OMAP44xx and OMAP54xx PRM register headers and voltage/PM code that shares the OMAP4-style PRM programming model.

## Risks And Test Signals
The function names are OMAP4-prefixed but used for later SoCs; correctness depends on `device_inst_offset` in init data. Test signals are VP/VC register access on OMAP4 and OMAP5 and successful `omap44xx_prm_init()` registration.
