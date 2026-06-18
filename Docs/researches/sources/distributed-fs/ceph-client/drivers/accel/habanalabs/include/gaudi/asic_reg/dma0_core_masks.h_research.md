# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_masks.h

## Purpose

`dma0_core_masks.h` is an auto-generated bit-field map for the Gaudi DMA0 core register block. It defines shifts and masks for enabling the DMA engine, programming transfers, configuring write completions, security properties, rate limits, errors, status, and debug registers.

## Important APIs, Types, and Constants

The file exports shift/mask pairs for every DMA0 core field. Important groups include `DMA0_CORE_CFG_0_EN` for core enable, `DMA0_CORE_CFG_1_HALT/FLUSH/SB_FORCE_MISS`, source and destination base/stride/transfer-size fields, `DMA0_CORE_COMMIT_*` fields for linear DMA, transpose, data type, memset, compression/decompression, write completion, and context ID, and write-completion address/data/AWUSER fields.

Security and protection fields include `DMA0_CORE_PROT_VAL`, `DMA0_CORE_PROT_ERR_VAL`, `DMA0_CORE_SECURE_PROPS_ASID/MMBP`, and `DMA0_CORE_NON_SECURE_PROPS_ASID/MMBP`. Error fields include `DMA0_CORE_ERR_CFG_ERR_MSG_EN`, `STOP_ON_ERR`, `ERR_CAUSE_*`, and error-message address/write-data fields. Status/debug fields include request counters, `DMA0_CORE_STS0_BUSY`, halt state, debug memory controls, descriptor counters, and FIFO/buffer fullness indicators.

## Control Flow

The header has no executable control flow. The masks are applied in driver initialization and runtime paths. `gaudi_init_dma_core()` uses the error config, protection, secure-props, and enable shifts to configure each DMA engine and sets workarounds such as LBW outstanding limits. DRAM scrubbing and device-memory memset paths write DMA0 core source/destination/size registers and set `DMA0_CORE_COMMIT_LIN` plus `DMA0_CORE_COMMIT_MEM_SET`, then poll `DMA0_CORE_STS0_BUSY`. Error handling reads and clears `DMA0_CORE_ERR_CAUSE`.

## State and Persistence Behavior

The masks describe mutable hardware state in DMA core registers. Transfer programming state is transient per operation. Configuration state such as enable, protection, secure properties, outstanding limits, rate limits, and error-message settings persists across DMA jobs until reset or reconfiguration. Error-cause and debug registers expose state that must be read and cleared by the driver.

## Dependencies and Integration Points

This file pairs with `dma0_core_regs.h` for addresses and is reused across DMA channels by adding `DMA_CORE_OFFSET` computed from DMA0 and DMA1 core base addresses. Gaudi code applies the same DMA0 field definitions to DMA1 and other channels because they share the DMA_CORE prototype. It also integrates with queue-manager command processing, since QMAN LDMA offset registers point into the DMA core register layout.

## Risks

Mask mistakes can misprogram DMA operations, a severe risk because DMA can read/write host and device memory. Context ID, ASID, MMBP, and protection fields are security-critical. The commit register has multiple independent operation modifiers, so accidental bit overlap can turn a copy into a memset, enable compression, or suppress expected completions. Busy polling and error handling depend on correct status and error masks.

## Test Signals

Tests should cover DMA core initialization readback, successful linear copy and memset operations, correct busy-bit transitions, RAZWI/error-message generation, stop-on-error behavior, and security-prop behavior for secured and non-secured channels. HBM scrubbing is a practical integration signal because it exercises source/destination/size/commit fields over every DMA channel and polls `STS0_BUSY`.
