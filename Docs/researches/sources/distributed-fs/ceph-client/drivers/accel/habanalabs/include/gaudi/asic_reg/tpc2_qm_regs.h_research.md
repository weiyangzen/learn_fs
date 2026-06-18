# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/tpc2_qm_regs.h

## Purpose
`tpc2_qm_regs.h` is an auto-generated Gaudi ASIC register map for the TPC2 queue manager. It provides the symbolic offsets that bind TPC2 command queues, completion queues, command processors, security properties, arbitration, error reporting, clock gating, rate limiting, local range, and indirect gateway registers to the Gaudi driver. It is the TPC2-specific companion to the shared QMAN programming model used by all TPC engines.

## Important APIs, types, and functions
This header defines no functions or types. Its API surface is 407 `#define` constants guarded by `ASIC_REG_TPC2_QM_REGS_H_`. The register window starts at `mmTPC2_QM_GLBL_CFG0` (`0xE88000`) and ends at `mmTPC2_QM_GLBL_MEM_INIT_BUSY` (`0xE88D00`).

The main register groups are:
- Global configuration, protection, secure/non-secure properties, status, and message enable registers.
- Four producer queue register sets: base low/high, size, producer/consumer index, config, AXI user, and status.
- Five completion queue register sets: config, AXI user, status, pointers, transfer sizes, control, and FIFO counts.
- Command processor message bases, local DMA offsets, fence read-data/counters, status, current instruction, barrier config, debug, and AXI user attributes.
- Arbitration configuration, WRR weights, master credits, choice queue offsets, watchdog, message attributes, base registers, status, and error registers.
- Clock gating, local range, strict priority, HBW/LBW rate limits, AXCACHE, indirect APB gateway, global error address/data, and memory-init busy status.

## Control flow
The header is passive but central to TPC2 queue control. The queue-id mapping in `gaudi.c` maps `GAUDI_QUEUE_ID_TPC_2_0` through `GAUDI_QUEUE_ID_TPC_2_3` directly to `mmTPC2_QM_PQ_PI_{0..3}`, so these constants are the doorbells for TPC2 submissions. Reset code stops TPC2 QMAN by writing `mmTPC2_QM_GLBL_CFG1`; clock-gating code reaches the block through the TPC QMAN stride; MMU setup writes all five `mmTPC2_QM_GLBL_NON_SECURE_PROPS_*` registers.

Initialization usually programs TPC QMAN instances by starting from TPC0 symbols and adding a per-TPC offset. TPC2 must therefore match the QMAN prototype layout exactly, even where explicit TPC2 symbols are not named in the initialization loop.

## State and persistence
The header does not persist software data. It names persistent hardware queue-manager state: producer queue DMA base/size/index values, completion queue pointers, command processor fence and instruction state, arbitration credit tables, security attributes, error targets, local range, rate limits, and clock-gating state. These values are established during device initialization and context setup, then updated by command submission and hardware execution until reset or reinitialization.

## Dependencies and integration points
The file integrates with common Gaudi QMAN setup and command submission in `gaudi.c`, event handling through `GAUDI_EVENT_TPC2_QM`, async id mapping, MMU preparation, state dump data, and reset/stop paths. It depends on generated field masks and on the common TPC QMAN layout shared with TPC0, TPC1, TPC3, and later TPC instances.

## Risks and edge cases
- Doorbell offsets are user-visible indirectly through command submission. A bad `PQ_PI_*` value can make TPC2 workloads appear submitted while no hardware stream is actually rung.
- Queue-memory base and size registers must match the DMA allocations in `struct gaudi_internal_qman_info`; stale or wrong offsets can cause command fetches from invalid memory.
- TPC2-specific explicit symbols and loop-derived offsets must agree. Divergence can create split-brain behavior where initialization succeeds but doorbells, stop, or ASID setup target the wrong block.
- Error-message target registers affect fault delivery. Incorrect global error address/data symbols can hide TPC2 QMAN failures from firmware or report them as another engine.
- Arbitration and clock-gating controls are sensitive during reset; wrong values can leave queues busy or starved.

## Test signals
Positive signals include producer index updates on `GAUDI_QUEUE_ID_TPC_2_*`, completions/fence counters advancing, no `GAUDI_EVENT_TPC2_QM` faults under load, clean QMAN stop during reset, and successful ASID programming without TPC2 RAZWI. Negative signals include TPC2-only queue hangs, CP current instruction stuck after a doorbell, arbitration error causes, memory-init busy never clearing, or completion queues not matching the submitted stream.
