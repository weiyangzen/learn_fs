# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc1_qm_regs.h

## Purpose
`tpc1_qm_regs.h` is an auto-generated Gaudi ASIC register map for the queue manager attached to TPC engine 1. It gives the driver symbolic offsets for global QMAN controls, security properties, producer and completion queues, command processors, fence counters, arbitration, error reporting, clock gating, local range, rate limiting, indirect gateway, and memory-init status. These constants are the hardware contract used by Gaudi command submission, queue initialization, doorbells, error handling, and reset paths.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC1_QM_REGS_H_`. The register window starts at `mmTPC1_QM_GLBL_CFG0` (`0xE48000`) and ends at `mmTPC1_QM_GLBL_MEM_INIT_BUSY` (`0xE48D00`).

The main register families are:
- `mmTPC1_QM_GLBL_CFG*`, `GLBL_PROT`, `GLBL_ERR_CFG`, `GLBL_SECURE_PROPS_*`, `GLBL_NON_SECURE_PROPS_*`, `GLBL_STS*`, and `GLBL_MSG_EN_*`: QMAN enable/stop, protection, status, error, message, and security/MMU setup.
- `mmTPC1_QM_PQ_*`: four producer queue base, size, producer index, consumer index, config, AXI user, and status register sets. These include the doorbell registers used by the driver for `GAUDI_QUEUE_ID_TPC_1_0` through `GAUDI_QUEUE_ID_TPC_1_3`.
- `mmTPC1_QM_CQ_*`: five completion queue config, pointer, transfer-size, control, status, and FIFO count register sets.
- `mmTPC1_QM_CP_*`: command processor message base registers, local DMA offsets, fence read-data/counter registers, CP status/current-instruction registers, barrier config, debug, and AXI user attributes.
- `mmTPC1_QM_ARB_*`: arbitration config, WRR weights, master credit tables, choice queue offsets, watchdog, message AXI attributes, base registers, state/status, and error reporting.
- `mmTPC1_QM_CGM_*`, local range, CSMR priority, HBW/LBW rate-limit, global AXCACHE, indirect APB gateway, and global error address/data registers.

## Control flow
The file itself has no runtime branches, but its constants are used throughout TPC1 queue-manager control flow. During TPC QMAN initialization, Gaudi code commonly programs QMANs using TPC0 base symbols plus a per-engine QMAN delta. TPC1 symbols provide that delta through expressions such as `mmTPC1_QM_GLBL_CFG0 - mmTPC0_QM_GLBL_CFG0` and `mmTPC1_QM_CGM_CFG - mmTPC0_QM_CGM_CFG`. This makes the TPC1 QMAN layout the reference for iterating over all TPC QMAN instances.

For explicit TPC1 queue operations, `gaudi_get_dma_desc_list_size()`/doorbell selection logic maps `GAUDI_QUEUE_ID_TPC_1_0` through `GAUDI_QUEUE_ID_TPC_1_3` to `mmTPC1_QM_PQ_PI_{0..3}`. Stop/reset code writes `mmTPC1_QM_GLBL_CFG1` with command-processor stop bits. MMU setup writes the five `mmTPC1_QM_GLBL_NON_SECURE_PROPS_*` registers for ASID propagation. Error setup uses global error address/data and arbitration error-message registers so QMAN RAZWI or arbitration failures can interrupt firmware/CPU paths.

## State and persistence
The header contains no software state. It names persistent hardware state in TPC1_QM: PQ base DMA addresses and indices, CQ pointers and transfer sizes, command-processor fence counters, current instruction pointers, barrier state, arbitration credits, security properties, error targets, and clock-gating configuration. The driver also keeps mirrored software state in `struct gaudi_internal_qman_info` for the persistent queue DMA buffers; these registers bind that software allocation to the hardware QMAN until reset or reinitialization.

## Dependencies and integration points
The header is included through the Gaudi generated register set and paired with field definitions from generated mask headers. Major consumers are `gaudi.c` TPC QMAN initialization, stop, clock-gating disable, command submission doorbells, MMU ASID setup, event/error mapping, and state dump support. Event ids `GAUDI_EVENT_TPC1_QM` and async-id maps identify faults from this block.

The QMAN register layout must remain compatible with common QMAN programming logic shared across DMA, MME, TPC, and NIC blocks. Driver code assumes four external/internal PQ streams plus one lower CP path for TPC QMANs, and it assumes the offset from TPC0 to TPC1 applies cleanly to the rest of the TPC QMAN fleet.

## Risks and edge cases
- TPC1 QMAN is a stride reference for all TPC QMAN loops. A wrong offset can corrupt programming for several engines, not only TPC1.
- Doorbell registers `PQ_PI_*` are directly exposed through queue-id mapping. An incorrect symbol causes submissions to ring the wrong stream or engine.
- Queue base/size registers bind DMA-coherent memory into hardware. Bad offsets or stale values can make the QMAN fetch commands from invalid host/device memory.
- Security registers `GLBL_NON_SECURE_PROPS_*`, `CP_*USER`, `PQ_*USER`, and `CQ_*USER` affect ASID and AXI attributes. Misprogramming can surface as RAZWI, data corruption, or isolation failures.
- Stop bits in `GLBL_CFG1` must be used with reset sequencing. Stopping CP/PQ/CQ at the wrong time can strand in-flight work and leave fence counters inconsistent.
- Arbitration credit/watchdog and error-message registers are low-level hardware controls. Incorrect values can hide QMAN hangs or flood error interrupts.

## Test signals
Positive signals include successful command submission on `GAUDI_QUEUE_ID_TPC_1_0` through `_1_3`, producer/consumer indices moving as expected, completion queues producing entries, TPC1 QMAN stop/reset completing, and absence of `GAUDI_EVENT_TPC1_QM` errors during workloads. Strong negative signals include QMAN RAZWI events, stuck `PQ_CI`/`PQ_PI`, unchanged CP current instruction after doorbells, fence counters not advancing, arbitration error causes, memory-init busy stuck, or failures that move with TPC1 queue-id mappings rather than with the workload itself.
