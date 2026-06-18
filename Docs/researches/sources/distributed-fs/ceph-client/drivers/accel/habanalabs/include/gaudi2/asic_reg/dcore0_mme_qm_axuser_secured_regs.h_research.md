# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_axuser_secured_regs.h

Purpose: Auto-generated register definition header for the `AXUSER` hardware block. It exports macro constants over 0x40CAB00-0x40CAB4C.

Important APIs/types/functions: Exported constants include `mmDCORE0_MME_QM_AXUSER_SECURED_HB_ASID` (0x40CAB00), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_MMU_BP` (0x40CAB04), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_STRONG_ORDER` (0x40CAB08), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_NO_SNOOP` (0x40CAB0C), `mmDCORE0_MME_QM_AXUSER_SECURED_HB_WR_REDUCTION` (0x40CAB10), and `mmDCORE0_MME_QM_AXUSER_SECURED_LB_OVRD` (0x40CAB4C). No functions or C types are defined.

Control flow: None in this header; callers create runtime flow by using the macros in register accesses.

State and persistence behavior: Stateless compile-time metadata; hardware state lives in the addressed registers.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths.

Risks: Generated address drift or use of a wrong sibling block can misprogram hardware.

Test signals: Build coverage, register dump validation, and block-specific hardware smoke tests.
