# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_qm_regs.h

Purpose: generated main queue manager register map for `DCORE0_TPC0_QM` using the QMAN prototype. It exports 517 `mmDCORE0_TPC0_QM_*` constants from `0x400A000` to `0x400AD70`.

Important APIs/types/functions: macro-only API covering global config/status/error registers, AX cache/protection, four producer queues, five completion queues, CQ pointers/status/IFIFO, CP message base registers, fences and counts, barrier/LDMA offsets, command processor status/current instruction/predicate/debug/credits/input data, PQC HBW/LBW queues, arbitration masks/weights/credits/choice offsets, WR64 base address windows, ARC CQ pointer registers, inflight counters, error-message controls, and performance-counter configuration.

Control flow: none inside the header. It supports the external QMAN control path: configure queues, push work, track completion queues, handle fences/barriers, poll command processor state, respond to errors, and tune arbitration.

State and persistence behavior: this file maps most persistent state for the TPC queue manager. Registers track queue bases/sizes/PIs/CIs, completion pointers, fences, CP execution state, arbitration credits, protection, errors, and counters. State persists across queue operation until reset or reinitialization.

Dependencies and integration points: included by `gaudi2_regs.h`; referenced extensively by `gaudi2_security.c` for allowed register ranges and specific register access. Works with `dcore0_tpc0_qm_arc_aux_regs.h`, `dcore0_tpc0_qm_cgm_regs.h`, AXUSER non-secured registers, and the TPC CFG QM kernel/tensor/sync-object headers.

Risks: high blast radius. Wrong queue pointer/base macros can corrupt command submission. Completion queue mistakes can hang waits or lose completions. Error mask misconfiguration hides faults. Security allowlists must distinguish safe queue descriptors from privileged global/ARC controls.

Test signals: queue submission/completion tests, fence/barrier tests, CP error injection and reporting, security allowlist coverage, reset and idle tests, performance counter smoke tests, and register database diff validation.
