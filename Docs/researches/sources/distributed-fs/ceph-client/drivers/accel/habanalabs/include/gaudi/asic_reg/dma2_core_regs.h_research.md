# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma2_core_regs.h

## Purpose

`dma2_core_regs.h` is the generated register-offset contract for the Gaudi `DMA2_CORE` block, prototype `DMA_CORE`. It defines 67 `mmDMA2_CORE_*` constants from `0x540000` through `0x540238`; `gaudi_blocks.h` identifies `mmDMA2_CORE_BASE` as `0x7FFC540000ull`. DMA2 is one of the HBM DMA engines in the driver reset and stop paths.

## Important APIs, Types, And Register Groups

The file exposes only macros. The register groups cover core enable/configuration (`CFG_0`, `CFG_1`, `LBW_MAX_OUTSTAND`), source and destination base addresses, multidimensional transfer sizes and strides for dimensions 0..4, `COMMIT`, write-completion data/address/AWUSER registers, tensor-engine row count, protection and secure/non-secure properties, read and write outstanding/cache/user/inflight tuning, read/write rate limit configuration, error configuration/cause/message payload registers, status registers, read debug memory access registers, and debug counters/status for HBW/LBW AXI and descriptors.

## Control Flow And State

The header has no executable code. Driver code creates DMA2 control flow by writing these offsets directly or through DMA0-relative arithmetic. `gaudi_init_dma_core()` initializes each DMA core by programming max outstanding reads, the H3-2116 `LBW_MAX_OUTSTAND` workaround, error message routing, protection bits, secure MMU bypass, and `CFG_0` enable. HBM reset code stalls DMA2 via `mmDMA2_CORE_CFG_1` with `DMA0_CORE_CFG_1_HALT_SHIFT`. `gaudi_dma_core_transfer()` uses the common core layout to program source/destination, size, and `COMMIT`, then polls `STS0` and checks `ERR_CAUSE`.

The state is device-resident. Transfer descriptors, inflight counters, error causes, rate limits, ASID/MMU properties, and debug memories persist in hardware until reset or driver writes. `gaudi_restore_dma_registers()` restores write-completion address/data and rewrites `WR_AWUSER_31_11` for DMA2 because HBM DMA channels can be modified by user SRAM-reduction flows. `gaudi_mmu_prepare()` writes `mmDMA2_CORE_NON_SECURE_PROPS` during ASID preparation.

## Dependencies And Integration Points

The header is pulled into `gaudi_regs.h`; users depend on matching shift/mask definitions from Gaudi field headers. Its address spacing participates in `DMA_CORE_OFFSET`, derived from DMA1 and DMA0 core bases in `gaudiP.h`. It integrates with HBM DMA initialization, engine idle diagnostics (`DMA_CORE_STS0`), debugfs DMA read fallback, MMU ASID programming, reset restoration, and stop/stall flows for HBM DMA channels.

## Risks And Test Signals

Offset drift is high risk because core registers trigger real DMA transactions. Misprogramming `SRC_BASE`, `DST_BASE`, `DST_TSIZE_0`, or `COMMIT` can corrupt memory; stale `NON_SECURE_PROPS` or AWUSER values can break address translation/security; wrong error-message registers can hide RAZWI conditions. Test signals include successful HBM DMA initialization, DMA2 idle detection, no timeout in `gaudi_dma_core_transfer()`, zero `ERR_CAUSE` after transfers, restored write completion behavior after reset, and correct ASID behavior under MMU-enabled contexts.
