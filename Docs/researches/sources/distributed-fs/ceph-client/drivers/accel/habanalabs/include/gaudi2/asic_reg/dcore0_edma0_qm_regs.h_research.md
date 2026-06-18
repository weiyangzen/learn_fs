<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h

## Purpose
`dcore0_edma0_qm_regs.h` is the generated address map for the DCORE0 EDMA0 queue manager, prototype `QMAN`. It defines 517 register addresses in the 0x41CA000-0x41CAD70 range for global queue control, queue memory bases, CP/fence state, PQC, arbiters, ARC completion queues, completion queue CIs, address override/base windows, secure push, error routing, rate limits, indirect APB access, and performance counters.

## Important APIs, types, and functions
The file exports `mmDCORE0_EDMA0_QM_*` constants only. Register groups match the sibling mask header: `GLBL_*`, `PQ_BASE_*`, `PQ_SIZE`, `PQ_PI`, `CQ_*`, `CP_*`, `PQC_*`, `ARB_*`, `CSMR_STRICT_PRIO_CFG`, `ARC_CQ_*`, CQ IFIFO/CTL message bases and CI registers, `ADDR_OVRD`, `CP_CFG` and switch watchdogs, ARC and engine base/range registers, secure-push indicators, PQC status, SEI status/mask, global error address/data, L2H filters, local range, HBW/LBW rate-limit registers, indirect gateway APB registers, and free/idle performance counters.

## Control flow
The header supplies addresses for QMAN lifecycle code. Bring-up writes global config, queue base/size/PI registers, completion queue and CP parameters, arbiter policy, AXI/error settings, and base/range windows. Runtime command submission advances producer indices, while completion and interrupt paths read CQ/CP/fence/status registers. Recovery writes stop/flush bits, reads errors and current instruction state, drains arbiters, and reinitializes queues before re-enabling work.

## State and persistence behavior
Most registers represent persistent queue-manager state. Queue bases, indices, CP state, fence counters, arbiter credits, ARC CQ pointers, error configuration, and secure/local range settings can outlive a single command buffer and must be reset or rewritten during recovery. Some status/error registers are latched diagnostic state that should be captured before clearing.

## Dependencies and integration points
This file is inseparable from `dcore0_edma0_qm_masks.h`, EDMA0 queue setup, ARC auxiliary registers, EDMA0 core/context registers, AXUSER nonsecure attributes, and interrupt/error paths. Hardware register accessors use these absolute generated addresses to program the queue manager.

## Risks and edge cases
The biggest risks are lane count assumptions, stale queue pointers after reset, high/low base address mismatch, wrong pairing with mask macros, and failing to stop/flush all relevant PQF/CQF/CP/ARC_CQF components before reset. Arbiter credit and secure-push state are easy to miss in recovery.

## Test signals
Test signals include successful EDMA0 queue creation, command packet execution, completion delivery, fence operations, ARC CQ activity, arbiter fairness, secure push behavior, stop/flush/reset recovery, SEI/error interrupt injection, and performance counters that distinguish idle and active periods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_edma0_qm_regs.h -->
