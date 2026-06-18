# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme0_qm_regs.h

## Purpose
`mme0_qm_regs.h` is the auto-generated register address map for the Gaudi `MME0_QM` queue-manager block. It defines the MMIO addresses used to configure and inspect MME0's queue-manager global state, producer queues, completion queues, command processors, arbitration, clock gating, local range, rate limiting, indirect APB gateway, and global error capture. This is one of the core contracts behind MME command submission in the Gaudi driver.

## Important APIs, types, and functions
The header exports `mmMME0_QM_*` address macros. Important address groups are:
- Global QMAN registers: `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, secure/non-secure property registers, global status registers, and global message-enable registers.
- Producer queue registers for four PQs: `PQ_BASE_LO/HI_0..3`, `PQ_SIZE_0..3`, `PQ_PI_0..3`, `PQ_CI_0..3`, `PQ_CFG0/1_0..3`, `PQ_ARUSER_31_11_0..3`, and PQ status registers.
- Completion queue registers for five CQs: `CQ_CFG0/1_0..4`, `CQ_ARUSER_31_11_0..4`, CQ status, CQ pointer/size/control, pointer/size/control status, and IFIFO counts.
- Command processor registers for five CP lanes: message base address sets 0..3, LDMA offsets, fence read data and counts, CP status, current instruction, barrier config, debug, ARUSER, and AWUSER registers.
- Arbiter registers: configuration, choice queue push/head, WRR weights, master credits and credit increments, slave/master offsets, quiet period, watchdog, slave id, max inflight, AWUSER attributes, base addresses, state/status, error cause/message/drop, and credit status.
- Control tail: CGM config/status, local range base/size, CSMR strict priority, HBW/LBW rate limiters, AXCACHE, indirect APB gateway config/data/status, global error address/data, and memory-init busy.

There are no C functions or types.

## Control flow
The file does not execute code, but `gaudi.c` uses these symbols directly in MME QMAN initialization and runtime support. `gaudi_init_mme_qman()` writes queue base addresses, queue sizes, producer/consumer indices, CP LDMA offsets, error interrupt destination addresses/data, arbiter error message enables, arbiter watchdog timeout, global stop/protection settings, and monitor/SOB message base addresses. `gaudi_init_mme_qmans()` maps MME queue IDs to master QMAN blocks, initializes four upper queues and lower CP lanes, then writes `GLBL_CFG0` to enable MME QMANs. Doorbell logic selects `PQ_PI_0..3` as producer-index registers. Reset and stop paths clear or stop QMANs through `GLBL_CFG0/CFG1`, and idle reporting reads `GLBL_STS0` plus `CGM_STS`.

## State and persistence behavior
The addressed hardware registers hold MME QMAN runtime state. PQ base/size/PI/CI registers describe persistent queue buffers allocated by the driver; CP message bases point at sync-manager monitor and SOB registers; global error address/data persists as the configured interrupt message target; global security properties persist ASID/MMBP setup; arbiter and rate-limiter registers persist scheduling policy and timeout behavior. Status registers expose live queue, CP, arbiter, CGM, and memory-init state.

Software persistence is indirect: `struct gaudi_device.internal_qmans[]` owns the coherent PQ buffers whose DMA addresses are programmed through this register map. If these registers are reset, the driver must reinitialize them before command submission resumes.

## Dependencies and integration points
This header is included by `gaudi_regs.h` and paired with `mme0_qm_masks.h`. Important consumers include:
- `gaudi.c` for MME QMAN initialization, enable/disable, doorbells, idle checks, and error routing.
- `gaudi_security.c` for protection-bit setup over QMAN configuration/status/pointer windows.
- MMU setup code that calls `gaudi_mmu_prepare_reg()` on `GLBL_NON_SECURE_PROPS_0..4`.
- Common command-submission paths that rely on queue PI/CI and persistent queue configuration.

The register map is also used as a template for related MME QMAN blocks. Driver code computes offsets such as `mmMME2_QM_GLBL_CFG0 - mmMME0_QM_GLBL_CFG0` and `MME_QMAN_OFFSET` to reach other MME QMAN instances, so the MME0 layout defines the stride assumptions for more than one hardware block.

## Risks and edge cases
- Address stride assumptions are central. The driver adds queue-lane offsets of `qman_id * 4` and MME-block offsets to MME0 base symbols; any non-uniform register spacing breaks those calculations.
- The header defines four PQ lanes but five CP/CQ lanes. Initialization treats `qman_id < 4` differently from the lower CP lane; new code must preserve that distinction.
- Global error routing writes `GLBL_ERR_ADDR_*`, `GLBL_ERR_WDATA`, and arbiter error enables. Wrong addresses can drop or misroute hardware error interrupts.
- Doorbell code writes `PQ_PI_*`; a wrong PI address can make command submissions invisible or corrupt another queue lane.
- `GLBL_CFG1` stop/flush and `GLBL_CFG0` enable are shared global registers. Uncoordinated writes can stop active CP/PQ/CQ units.
- Protection-bit setup depends on the low bits and page grouping of these addresses. Register relocation can invalidate security masks.
- Indirect APB gateway registers expose secondary access semantics; polling must respect `IND_GW_APB_STATUS` ready/error fields.

## Test signals
Positive signals include successful allocation/programming of internal MME persistent queues, enabled `GLBL_CFG0` for master MME QMANs, command submission advancing PI/CI as expected, lower CP message paths generating sync-manager monitor/SOB writes, valid idle reports from `GLBL_STS0` and `CGM_STS`, clean reset/reinitialize cycles, and MMU ASID programming on non-secure property registers. Negative signals include MME command timeouts, stale PI/CI values, CP current instruction stuck, CP/PQ/CQ read errors, arbiter `CHOISE` watchdog or overflow errors, RAZWI interrupts from QMAN accesses, or protection faults during QMAN setup.
