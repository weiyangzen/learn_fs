<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h

Purpose: common PXA3xx MFP definitions and thin compatibility wrappers.

Important definitions: `MFPR_BASE` and common `GPIOx_GPIO` macros for GPIO0-127 plus secondary GPIO pins. Inline wrappers `pxa3xx_mfp_read()`, `pxa3xx_mfp_write()`, and `pxa3xx_mfp_config()` delegate to the generic MFP API.

Control flow and integration: PXA300/PXA320 headers extend this file; SoC init maps MFPR base and address tables before board pin configuration.

State and persistence: no local state; MFPR state is external hardware programmed through generic MFP calls.

Dependencies: includes `linux/soc/pxa/mfp.h`.

Risks and test signals: wrapper comments discourage direct read/write in favor of config arrays. Test by applying common GPIO configs and validating MFPR contents via MFP helpers on PXA3xx.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.h -->
