# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_dup_eng_regs.h

Purpose: Defines DCORE0 MME QM ARC duplicate-engine registers. The block maps duplicate TPC engine target addresses, NIC duplication controls, LBU addresses, dup mask/destination fields, and 64 ARC context-id offsets at 0x40C9000-0x40C96B0.

Important APIs/types/functions: Exports 276 `mmDCORE0_MME_QM_ARC_DUP_ENG_*` address macros, represented by `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_0` (0x40C9000), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_1` (0x40C9004), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_2` (0x40C9008), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_3` (0x40C900C), `mmDCORE0_MME_QM_ARC_DUP_ENG_DUP_TPC_ENG_ADDR_4` (0x40C9010), and `mmDCORE0_MME_QM_ARC_DUP_ENG_ARC_CID_OFFSET_63` (0x40C96B0). There are no functions or data types.

Control flow: Firmware or setup code configures duplicate-engine destinations and context offsets before queue-manager ARC traffic is replicated or routed.

State and persistence behavior: The macros are static. Hardware register state controls duplication/routing behavior and persists until reset or reconfiguration.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. It integrates with ARC firmware messaging, TPC/NIC routing, and the AXUSER attributes in the matching duplicate-engine AXUSER header.

Risks: Misprogrammed duplicate destinations or context offsets can route messages to the wrong engine. The 64-entry CID-offset array is sensitive to consistent indexing.

Test signals: Firmware routing tests, duplicate-engine traffic validation, CID-offset readback, security-region validation, and negative tests for disabled/invalid destination masks.
