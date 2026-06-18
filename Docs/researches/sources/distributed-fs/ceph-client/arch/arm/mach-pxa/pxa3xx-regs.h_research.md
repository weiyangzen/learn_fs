<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h

Purpose: PXA3xx register definitions for oscillator, power managers, wake, power modes, and application clocks.

Important definitions: `OSCC`, MPMU registers `PMCR/PSR/PSPR/PCFR/PWER/PWSR/PECR/DCDCSR/PVCR/PCMD`, application subsystem registers `ASCR/ARSR/AD*ER/AD*SR/AD*R`, wake-source bit masks `ADXER_*`, D-state config bits `ADXR_*`, PXA3xx power mode constants, and clock registers `ACCR/ACSR/AICSR/CKENA/CKENB/CKENC/AC97_DIV`.

Control flow and integration: PXA3xx PM, reset, MFP resume, IRQ wake, and clock init code use these direct register definitions.

State and persistence: hardware registers persist across runtime and low-power transitions; some bits are write-one-to-clear.

Dependencies: includes `pxa-regs.h`.

Risks and test signals: power/wake bits are central to suspend; incorrect masks can prevent wake or corrupt resume. Test PXA3xx standby/mem suspend, wake-source setup, RDH clearing, clock enable behavior, and reset status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/pxa3xx-regs.h -->
