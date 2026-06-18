<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h

## Purpose
`nic0_qm0_regs.h` is the auto-generated register map for NIC0 queue manager 0, a QMAN instance. It exposes the MMIO addresses used to configure NIC command queues, completion queues, command processors, arbitration, persistent queue cache, error reporting, and ARC-facing queue-manager status.

## Important APIs, types, and functions
The file exports register macros only. Major groups include `GLBL_*` configuration, status, protection, AXCACHE, and error registers; four persistent queue register sets (`PQ_BASE_*`, `PQ_SIZE_*`, `PQ_PI_*`, `PQ_CI_*`, `PQ_CFG*`, `PQ_STS*`); five completion queue register sets (`CQ_CFG*`, `CQ_PTR_*`, `CQ_TSIZE_*`, status and IFIFO); command-processor message bases, fences, barriers, predicates, current instruction, DMA offset, input data, and debug/credit registers; persistent queue cache registers (`PQC_HBW_*`, `PQC_LBW_*`, `PQC_SIZE_*`, `PQC_PI_*`, `PQC_CFG`, `PQC_SECURE_PUSH_IND`); and arbiter credit, weight, master/slave, fullness, and error registers.

## Control flow
No executable C flow exists. Runtime flow is imposed by queue-manager setup code: program global/protection settings, configure PQ and CQ base/size/control registers, initialize command-processor message and fence locations, configure PQC and arbiter policy, then unmask/handle errors and monitor status. Submission paths update producer indices and doorbell-related registers indirectly through QMAN mechanisms; debug/reset paths read `CP_CURRENT_INST_*`, `CP_STS_*`, CQ status, and arbiter state.

## State and persistence
The persistent state is hardware queue state. PQ/CQ base addresses and sizes describe host or device memory rings; PI/CI registers track queue progress; fence counters and command-processor status survive until reset or explicit reinitialization; arbiter credits and PQC entries track in-flight queue work. The header itself stores no state.

## Dependencies and integration points
It is included by `gaudi2_regs.h`. Generic queue-manager code relies on common offset macros in `gaudi2_regs.h` being derived from the PDMA QMAN layout and compatible with this NIC QMAN layout. It integrates with NIC command submission, collective networking, security/protection setup, interrupt/error handling, and reset diagnostics.

## Risks and test signals
Queue-register misprogramming can corrupt DMA-visible rings, wedge command processors, or report completions to the wrong CQ. Replication risk is high because NIC QM0 addresses are often used as the base pattern for other NIC QMs. Test signals include successful NIC queue bring-up, PI/CI movement under traffic, correct CQ completions, sane fence counters, no PQC secure-push/protection violations, and useful command-processor current-instruction data on forced queue hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/nic0_qm0_regs.h -->
