# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma1_core_regs.h

## Purpose

`dma1_core_regs.h` is the auto-generated address map for the Gaudi DMA1 core block. It mirrors the DMA0 core register layout but starts at the DMA1 core base around `0x520000`. The driver uses it both as a concrete DMA1 address map and as evidence for deriving per-channel DMA core offsets.

## Important APIs, Types, and Constants

The header exports `mmDMA1_CORE_*` constants for the same DMA_CORE prototype groups as DMA0: enable/control, source/destination base registers, multi-dimensional transfer sizes and strides, commit, write completion, transfer engine rows, protection, secure/non-secure properties, read/write outstanding and AXI attributes, rate limiting, error config/cause/message, status, debug memory, debug counters, debug status, and descriptor IDs.

## Control Flow

The header has no executable control flow. In Gaudi code, `DMA_CORE_OFFSET` is computed as `mmDMA1_CORE_BASE - mmDMA0_CORE_BASE`, and most multi-channel programming uses `mmDMA0_CORE_* + dma_id * DMA_CORE_OFFSET`. Reset paths may also write concrete DMA1 registers, such as halting DMA1 core through `mmDMA1_CORE_CFG_1`. This means the DMA1 register map participates in both direct access and generalized per-channel addressing.

## State and Persistence Behavior

The registers hold DMA1 hardware configuration, transfer state, status, debug state, and errors. Configuration persists until reset/reprogramming, transfer descriptor registers are overwritten per DMA operation, and error/status registers reflect live or latched hardware state. The generated header itself should remain static and synchronized with the hardware database.

## Dependencies and Integration Points

This file pairs conceptually with the DMA0 core register and mask headers. It integrates with `gaudiP.h` offset derivation and with channel-generic initialization in `gaudi_init_dma_core()`. Because the field layout is shared with DMA0, DMA0 mask constants are applied to DMA1 register addresses. It also participates in reset, halt, scrubbing, memset, error routing, and queue-manager LDMA integration.

## Risks

If the DMA1 base or any DMA1 offset diverges from DMA0 unexpectedly, the `DMA_CORE_OFFSET` channel abstraction can misaddress every channel after DMA0. A generated-map mismatch can break DMA1 specifically or all DMA channels that rely on the derived offset. Since the mask file is DMA0-named but shared by prototype, a hardware layout difference between DMA0 and DMA1 would be dangerous.

## Test Signals

Validation should include direct readback of DMA1 control/status registers, successful DMA1 initialization through channel-generic code, DMA1 participation in DRAM scrubbing and memory copy/memset operations, correct halt/reset behavior via `mmDMA1_CORE_CFG_1`, and no DMA1-specific error-cause bits under normal transfers. Offset tests should confirm that DMA0 plus `DMA_CORE_OFFSET` reaches every DMA1 register defined here.
