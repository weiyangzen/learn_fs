<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c

Purpose: PXA3xx syscore suspend/resume glue for the generic PXA MFP subsystem.

Important APIs/objects: defines `pxa3xx_mfp_syscore`, whose PM callbacks call `mfp_config_lpm()` on suspend and `mfp_config_run()` on resume. Resume also clears `ASCR_RDH` while preserving write-one-to-clear D-state bits.

Control flow: PXA3xx SoC init registers this syscore object. During system suspend, pin low-power configurations are applied; on resume, run configurations are restored before receivers are re-enabled.

State and persistence: no local arrays; state is maintained by the shared `linux/soc/pxa/mfp` subsystem and PXA3xx power registers.

Dependencies and integration: depends on `mfp-pxa3xx.h`, `pxa3xx-regs.h`, syscore PM, and PXA3xx SoC init.

Risks and test signals: low-power pin configuration may not be appropriate for all suspend states, as noted by the FIXME. Test suspend/resume with active-low chip selects, wake pins, and post-resume peripheral operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/mfp-pxa3xx.c -->
