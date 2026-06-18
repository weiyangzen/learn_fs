# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_masks.h

## Purpose
`mme0_qm_masks.h` is the auto-generated field mask and shift map for the Gaudi `MME0_QM` queue-manager block. It complements `mme0_qm_regs.h`: the register header names addresses, while this file names bit positions and masks for enabling/stopping/flushing queue-manager subblocks, configuring security properties, interpreting status and error bits, programming producer/consumer queues, command processors, arbitration, clock gating, range/rate controls, indirect APB access, and global error capture.

## Important APIs, types, and functions
The exported API is a set of `MME0_QM_*_SHIFT` and `MME0_QM_*_MASK` macros. Important groups include:
- Global enable/stop/flush/protection/error fields: `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, and `GLBL_ERR_CFG` cover PQF, CQF, CP, arbiter, error-message enable, and stop-on-error behavior.
- Secure and non-secure properties: per-queue `ASID` and `MMBP` fields for `GLBL_SECURE_PROPS_*` and `GLBL_NON_SECURE_PROPS_*`.
- Global status/error/message fields: idle, stopped, read errors, undefined command, stop op, message write error, WREG error, fence overflow/underflow, and message enable fields.
- PQ and CQ fields: base address, size, PI/CI, credit limit, max inflight, ARUSER, credit/free/inflight counts, empty/busy status, completion queue pointers, transfer size, and control.
- CP fields: message base address registers, LDMA offsets, fence read-data increments/counters, CP state, current instruction, barrier config, debug state, ARUSER/AWUSER attributes.
- Arbiter fields: master/slave configuration, WRR weights, credits, choice queues, watchdog, max inflight, error causes, error message enables, and credit status.
- CGM/range/rate/AXI/cache/indirect gateway/error-capture fields: clock gating status, local range, strict priority, read/write rate limiter, AXCACHE, APB gateway, and global error address/data.

There are no functions or data structures. Callers compose register values with these masks and shifts.

## Control flow
This header has no runtime control flow. It participates in driver control flow when Gaudi code writes MME QMAN registers. For example, initialization code builds global error configuration values using higher-level masks derived from these bit definitions, writes stop-on-error and message-enable behavior, configures protection trust, sets queue base/size/PI/CI values, and later checks idle or stopped status through masked status fields. Idle-check and reset paths use QMAN status fields to decide whether an MME master QMAN is quiescent.

## State and persistence behavior
The file owns no state. Its masks describe state stored in MME0 QMAN hardware registers. Enable, stop, flush, protection, security property, arbiter, clock-gating, rate-limiter, and queue pointer fields persist in hardware until reprogrammed or reset. Status and error fields reflect live hardware state; some error and dropped-status fields may be sticky until cleared by block-specific mechanisms.

The masks are persistent compile-time interpretation rules. If a mask is wrong, the driver may write the intended address but alter the wrong bits or misread valid hardware state.

## Dependencies and integration points
`mme0_qm_masks.h` is included by `gaudi_regs.h` and used with `mme0_qm_regs.h`. It integrates with Gaudi QMAN setup in `gaudi.c`, security and protection setup in `gaudi_security.c`, MMU ASID programming through `gaudi_mmu_prepare_reg()`, reset/idle flows, and error handling for RAZWI or arbiter failures.

The field layout also lines up with common QMAN logic used by DMA and TPC QMANs: PQF/CQF/CP naming, queue pointer fields, CP fence fields, arbiter fields, and clock-gating/status patterns are shared concepts across generated QMAN blocks. MME-specific consumers must still use the MME0 names and account for the MME0/MME2 master QMAN layout.

## Risks and edge cases
- Shift/mask errors are high impact because they do not change the register address, only the bits touched. Failures may appear as queue hangs, security faults, or missing interrupts.
- `GLBL_CFG0`, `GLBL_CFG1`, and `GLBL_STS0` pack PQF, CQF, CP, and arbiter fields into one register. Read/modify/write paths must preserve unrelated fields.
- Security properties expose ASID and MMBP fields for both secure and non-secure queues. Incorrect masking can route transactions through the wrong address space or bypass intended MMU behavior.
- Status field variants such as `GLBL_STS1` versus `GLBL_STS1_4` and `GLBL_MSG_EN` versus `_4` reflect different queue lanes; treating them as identical can miss lane-specific errors.
- Queue counters and credit fields are width-limited, commonly 16 bits or smaller. Larger software values must be range-checked before packing.
- Arbiter spelling in generated names uses `CHOISE`; consumers must match the generated spelling exactly.

## Test signals
Positive signals include successful MME QMAN initialization, expected `QMAN_MME_ENABLE` behavior, clean idle status after reset, no CP/PQ/CQ read errors, correct stop-on-error behavior when enabled, valid ASID programming after MMU setup, and working command submission through MME queues. Negative signals include stuck `PQ_BUSY` or `CQ_BUSY`, CP undefined-command or WREG errors, fence overflow/underflow bits, arbiter watchdog/overflow errors, RAZWI interrupts from QMAN transactions, unexpected clock-gating state, or idle checks that disagree with actual queue progress.
