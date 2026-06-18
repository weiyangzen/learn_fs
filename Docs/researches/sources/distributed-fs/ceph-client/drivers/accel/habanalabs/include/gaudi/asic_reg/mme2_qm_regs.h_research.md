# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/mme2_qm_regs.h

## Purpose

`mme2_qm_regs.h` is an auto-generated address map for the Gaudi MME2 QMAN block, marked as prototype `QMAN`. It exports 406 `mmMME2_QM_*` register constants from `mmMME2_QM_GLBL_CFG0` at `0x168000` through `mmMME2_QM_GLBL_MEM_INIT_BUSY` at `0x168D00`. The file gives the driver the addresses needed to configure, enable, doorbell, monitor, and debug MME2 command queues.

## Important APIs, types, and functions

There are no functions or types. The macro surface is the API and is organized like the common Gaudi QMAN register layout:

- `GLBL_*` registers configure global enable/stop/protection/error behavior, secure and non-secure properties, status, message enables, AXCACHE, error capture, and memory-init busy state.
- `PQ_*` registers configure four producer queues: base low/high, size, producer/consumer indices, config, AXI user fields, and status.
- `CQ_*` registers configure five completion queues and status/IFIFO fields.
- `CP_*` registers configure command processor message bases, LDMA offsets, fence counters/data, current instruction, barrier, status, debug, and AXI user fields.
- `ARB_*` registers configure arbitration, weighted round-robin, master/slave credit flow, choice queues, message properties, base addresses, state, and error status.
- `CGM_*`, `LOCAL_RANGE_*`, `CSMR_STRICT_PRIO_CFG`, `HBW_RD_RATE_LIM_*`, `LBW_WR_RATE_LIM_*`, and `IND_GW_APB_*` cover clock gating, local address ranges, strict priority, rate limiting, and indirect APB gateway access.

## Control flow

The header itself has no control flow. In `gaudi.c`, `gaudi_init_mme_qmans()` uses the MME2 QMAN address range as the north-west MME queue manager. It computes an offset from `mmMME2_QM_GLBL_CFG0 - mmMME0_QM_GLBL_CFG0`, initializes four upper command streams plus a lower CP stream, programs PQ bases/sizes/indices and CP message/LDMA registers through common MME QMAN helpers, and then enables the block with `WREG32(mmMME2_QM_GLBL_CFG0, QMAN_MME_ENABLE)`. Runtime doorbell selection maps `GAUDI_QUEUE_ID_MME_0_0` through `_0_3` to `mmMME2_QM_PQ_PI_0` through `_3`.

## State and persistence behavior

The macros are immutable build-time constants. The registers they name hold live queue-manager state: queue base DMA addresses, producer/consumer indices, command processor fence counters, completion queue state, arbiter credits, error-capture addresses, and protection/ASID properties. That state persists in hardware until reset, queue teardown, or explicit reprogramming. `GLBL_CFG0` enable bits and `GLBL_CFG1` stop/flush bits directly affect whether queued MME work can progress.

## Dependencies and integration points

This file is included via `gaudi_regs.h`. It integrates with `gaudi_masks.h`, which uses MME0 QMAN masks for shared bit layouts while MME2 supplies the instance-specific address range. `gaudi.c` uses these addresses for MME queue initialization, queue doorbells, QMAN power gating, MMU non-secure property programming through `gaudi_mmu_prepare_reg()`, and engine-idle/debug checks. It depends on common QMAN concepts shared by DMA, TPC, MME, and NIC QMAN generated headers.

## Risks

A wrong address can corrupt queue state, send doorbells to the wrong queue, or enable/stop the wrong QMAN instance. The producer-queue and command-processor offsets are regular enough that arithmetic users assume the generated order is stable; inserting or moving a register without matching hardware changes would break offset-based setup. The file lacks masks, so consumers must use compatible QMAN mask headers for bit packing. MME2/MME0 base-delta calculations also mean that base-address errors affect multiple queue IDs.

## Test signals

Build tests should verify include compatibility. Hardware or simulator tests should cover MME QMAN initialization, queue submission on all four MME2 streams, lower CP configuration, producer index doorbells, MME reset/stop/flush sequences, MMU ASID programming of `GLBL_NON_SECURE_PROPS_*`, and QMAN idle detection. Static checks can compare the normalized QMAN layout against other QMAN instances such as NIC0 QM0/QM1 and ensure exactly four PQ and five CQ families remain present.
