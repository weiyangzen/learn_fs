# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_mme_qm_regs.h

Purpose: Defines the main DCORE0 MME queue-manager MMIO map for the QMAN prototype. It covers global config/status/error registers, producer queues, completion queues, command processors, fence counters, ARC queues, arbiter state, write64 bases, AWUSER messages, PQC status, and performance-counter configuration at 0x40CA000-0x40CAD70.

Important APIs/types/functions: Exports 517 `mmDCORE0_MME_QM_*` address macros. Dense families include four PQs, five CQs/CP lanes, four fence groups per lane, 64 arbiter availability/choice entries, and representative macros `mmDCORE0_MME_QM_GLBL_CFG0` (0x40CA000), `mmDCORE0_MME_QM_GLBL_CFG1` (0x40CA004), `mmDCORE0_MME_QM_GLBL_CFG2` (0x40CA008), `mmDCORE0_MME_QM_GLBL_ERR_CFG` (0x40CA00C), `mmDCORE0_MME_QM_GLBL_ERR_CFG1` (0x40CA010), and `mmDCORE0_MME_QM_PERF_CNT_CFG` (0x40CAD70).

Control flow: Queue setup code programs PQ/CQ base, size, pointer, command-processor, fence, and arbiter registers; firmware and hardware then consume queue entries and update status/counters.

State and persistence behavior: This header is stateless, but the named registers contain live queue-manager state: indices, credits, fences, errors, arbitration choices, and performance counters. Values are reset or reinitialized during device bring-up/recovery.

Dependencies and integration points: The header has only an include guard and preprocessor constants; consumers include it through the Gaudi2 ASIC register headers and use the constants with HabanaLabs register read/write, reset, security allowlist, diagnostics, or firmware setup paths. `gaudi2_security.c` references this block and individual CQ/CP/fence registers for privileged-region definitions. It also ties to ARC auxiliary and duplicate-engine headers.

Risks: Queue pointer, size, and fence address errors can deadlock command submission or corrupt completion handling. Security allowlists must include exactly the intended control/status windows.

Test signals: Queue-manager bring-up, command submission/completion tests, fence signaling, error interrupt injection, performance-counter readback, and security-region validation covering the CQ/CP/ARB address families.
