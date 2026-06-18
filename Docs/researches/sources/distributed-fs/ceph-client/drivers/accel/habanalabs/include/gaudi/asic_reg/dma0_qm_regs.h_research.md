# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_qm_regs.h

## Purpose

`dma0_qm_regs.h` is the auto-generated address map for the Gaudi DMA0 queue-manager block starting around `0x508000`. It gives symbolic offsets for global QMAN control, per-stream PQ/CQ registers, CP message/fence/debug registers, arbiter registers, clock-gating registers, rate-limit controls, indirect gateway registers, and error-capture registers.

## Important APIs, Types, and Constants

The exported constants are `mmDMA0_QM_*` addresses. The global region includes `GLBL_CFG0`, `GLBL_CFG1`, `GLBL_PROT`, `GLBL_ERR_CFG`, secure/non-secure props for streams 0 through 4, status, and message-enable registers. The PQ region has four primary queues with base low/high, size, PI, CI, config, ARUSER, and status. The CQ region has five completion queues with config, ARUSER, status, pointer, transfer-size, control, pointer/status mirrors, and FIFO counts. CP registers include four message base pairs for five CP streams, LDMA register offsets, fence data/counters, status, current instruction, barrier config, debug, and ARUSER/AWUSER. Arbiter and CGM blocks follow, then local range, strict priority, rate limit, AXCACHE, APB indirect gateway, global error address/write-data, and memory-init busy registers.

## Control Flow

The header has no executable logic. Gaudi queue initialization computes `dma_qm_offset = dma_id * DMA_QMAN_OFFSET`, and per-stream code adds `qman_id * 4` to the base stream-0 registers. It programs PQ bases and indices, CP LDMA offsets derived from DMA core addresses, CP message bases for monitor and sync-object areas, and barrier config. Per-QMAN setup writes error routing and global protection, while `gaudi_enable_qman()` writes `mmDMA0_QM_GLBL_CFG0 + dma_qm_offset` with an enable mask.

## State and Persistence Behavior

The mapped registers are persistent hardware state. Queue base/size/config registers persist until reprogrammed, PI/CI/status registers mutate as the queue runs, CP/fence/debug registers expose live command processor state, and error/arbiter registers persist fault or arbitration state. The generated header itself is static source and should not be hand-edited.

## Dependencies and Integration Points

This file pairs with `dma0_qm_masks.h` and uses the common QMAN descriptor ABI from `qman_if.h`. `gaudiP.h` derives `DMA_QMAN_OFFSET` from DMA0/DMA1 QMAN bases and derives CP LDMA offsets from DMA0 QMAN and DMA core addresses. The register map also integrates with sync manager monitor/SOB addresses, interrupt/GIC error routing, and reset/clock-gating code.

## Risks

Wrong addresses can corrupt queue state, break command submission, or make queue-manager faults impossible to diagnose. Because stream registers are laid out at 4-byte strides for many fields, off-by-one stream offsets can silently program the wrong queue. The map is also part of derived constants, so address drift affects DMA and CP command execution even outside direct QMAN writes.

## Test Signals

Signals include readback of QMAN base/size/PI/CI after initialization, command completion on all DMA QMAN streams, correct fence counter behavior, correct reset stop/flush behavior, working arbiter arbitration under concurrent streams, and expected global/arbiter error captures. Offset-derived tests should verify that `DMA_QMAN_OFFSET` and `qman_id * 4` addressing match the silicon register layout.
