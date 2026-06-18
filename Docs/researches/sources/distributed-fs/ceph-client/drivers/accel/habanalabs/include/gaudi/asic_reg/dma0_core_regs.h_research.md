# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma0_core_regs.h

## Purpose

`dma0_core_regs.h` is the auto-generated address map for the Gaudi DMA0 core block. It gives MMIO offsets for control, transfer descriptor, completion, protection, security, rate-limit, error, status, and debug registers starting at the DMA0 core region around `0x500000`.

## Important APIs, Types, and Constants

The header exports `mmDMA0_CORE_*` register offsets. The core programming sequence uses `CFG_0`, `CFG_1`, `SRC_BASE_*`, `DST_BASE_*`, multi-dimensional source/destination transfer-size and stride registers, `DST_TSIZE_0`, and `COMMIT`. Completion support uses `WR_COMP_WDATA`, `WR_COMP_ADDR_*`, and `WR_COMP_AWUSER_31_11`. Security/protection uses `PROT`, `SECURE_PROPS`, and `NON_SECURE_PROPS`. Runtime tuning and observability use read/write max outstanding, max size, AXCACHE/AXUSER, inflight counters, rate-limit config, error config/cause/message, `STS0`, `STS1`, and debug memory/status registers.

## Control Flow

The header is passive. In Gaudi code, DMA channel code computes `dma_offset = dma_id * DMA_CORE_OFFSET` and adds it to DMA0 addresses to target each channel. Initialization writes error-message routing, protection, secure props, and `CFG_0` enable. Scrubbing and memset paths write source/destination registers, size, and `COMMIT`, then poll `STS0` for `BUSY` to clear. Error paths read and clear `ERR_CAUSE`.

## State and Persistence Behavior

These addresses refer to device registers. Configuration registers persist across commands, descriptor registers hold the currently programmed DMA operation, status registers reflect live engine state, and error-cause registers persist fault state until cleared. The header itself is generated source and should not be edited manually.

## Dependencies and Integration Points

This file depends on the matching mask file for field definitions. It integrates with `gaudiP.h` offsets such as `DMA_CORE_OFFSET`, `QMAN_LDMA_SRC_OFFSET`, `QMAN_LDMA_DST_OFFSET`, and `QMAN_LDMA_SIZE_OFFSET`, which are derived from DMA0 addresses. Queue manager code uses those offsets to teach the CP where DMA core source, destination, and size registers live relative to the DMA core base.

## Risks

Incorrect address definitions can make every DMA channel write the wrong register. Because DMA1 and other channel offsets are derived from the DMA0/DMA1 layout, an incorrect DMA0 address or offset can break all channels, not just DMA0. Address drift also affects CP LDMA command execution through the QMAN offset constants.

## Test Signals

Useful signals are successful DMA channel enable, correct register readback after initialization, passing DRAM scrub and device-memory memset, expected error interrupt routing, and correct derived offsets in `gaudiP.h`. Hardware simulation can validate that `mmDMA0_CORE_* + dma_id * DMA_CORE_OFFSET` lands on matching registers for all DMA channels.
