# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_arc_aux_regs.h

Purpose: Defines DCORE0 MME QM ARC auxiliary registers for run/halt, reset vector, debug mode, cluster identity, interrupts, scratchpads, ARC regions, DCCM queues, CID offsets, LBU/CBU counters, fork address masks, and upper-DCCM control at 0x40C8100-0x40C8920.

Important APIs/types/functions: Exports 284 `mmDCORE0_MME_QM_ARC_AUX_*` address macros. Repeated families include 16 software interrupts, 16 ARC region configs, eight scratchpads, eight DCCM queue descriptors, and representative macros `mmDCORE0_MME_QM_ARC_AUX_RUN_HALT_REQ` (0x40C8100), `mmDCORE0_MME_QM_ARC_AUX_RUN_HALT_ACK` (0x40C8104), `mmDCORE0_MME_QM_ARC_AUX_RST_VEC_ADDR` (0x40C8108), `mmDCORE0_MME_QM_ARC_AUX_DBG_MODE` (0x40C810C), `mmDCORE0_MME_QM_ARC_AUX_CLUSTER_NUM` (0x40C8110), and `mmDCORE0_MME_QM_ARC_AUX_MME_ARC_UPPER_DCCM_EN` (0x40C8920).

Control flow: Device bring-up and recovery request ARC halt/reset, configure memory regions and DCCM queues, then monitor acknowledgements, interrupts, and bus counters while QMAN firmware runs.

State and persistence behavior: The header is stateless; the hardware registers hold ARC processor state, queue metadata, scratch values, interrupts, and counters until firmware or reset changes them.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` explicitly references ranges in this header for protected access windows and ARC control.

Risks: Run/halt and reset registers affect firmware liveness. DCCM queue base/size/counter mistakes can break firmware communication, and security ranges must not expose more ARC control than intended.

Test signals: ARC boot/halt/reset tests, firmware queue communication, interrupt delivery, scratchpad preservation during expected flows, counter readback, and protected-mode access validation.
