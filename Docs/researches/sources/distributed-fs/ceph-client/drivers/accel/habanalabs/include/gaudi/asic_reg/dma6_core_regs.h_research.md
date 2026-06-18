# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma6_core_regs.h

## Purpose

`dma6_core_regs.h` is the generated register-offset header for Gaudi `DMA6_CORE`. It exports 67 `mmDMA6_CORE_*` macros in the `0x5C0000..0x5C0238` range, and `gaudi_blocks.h` maps `mmDMA6_CORE_BASE` at `0x7FFC5C0000ull`. DMA6 is part of the HBM DMA engine group.

## Important APIs, Types, And Register Groups

No executable APIs or types are defined. Register groups cover configuration/halt/enable, LBW outstanding controls, source and destination base addresses, transfer sizes/strides, commit, write-completion address/data/AWUSER, TE rows, protection and secure/non-secure properties, read/write outstanding/cache/user/inflight controls, rate limits, error configuration/cause/message payload, status, debug memory controls, and AXI/descriptor debug counters.

## Control Flow And State

The header has no control flow. HBM DMA code directly stalls DMA6 through `mmDMA6_CORE_CFG_1`, while initialization, transfers, status polling, and error handling use DMA0-relative offset arithmetic. `gaudi_init_dma_core()` configures error routing, protection, secure MMU bypass, and enable; `gaudi_dma_core_transfer()` writes source/destination/size and commits work.

Device state includes transfer descriptors, inflight counters, write-completion target, error cause, rate limits, debug data, and MMU/security properties. Reset restoration rewrites completion and AWUSER state for DMA6. `gaudi_mmu_prepare()` updates `mmDMA6_CORE_NON_SECURE_PROPS` during ASID preparation.

## Dependencies And Integration Points

`gaudi_regs.h` includes this file. Correct operation depends on `DMA_CORE_OFFSET` and the shared DMA core field definitions. DMA6 integrates with HBM DMA init/stall, reset restore, debugfs DMA transfer paths, idle reporting, and MMU context setup.

## Risks And Test Signals

Wrong offsets can corrupt DMA transfers, prevent halting during reset, or break ASID/security properties. `WR_AWUSER_31_11` restoration is a known sensitivity for HBM channels. Test signals include clean DMA6 HBM transfers, no timeout or error cause, idle status after stop/stall, reset restore preserving completion behavior, and MMU-enabled workloads running without DMA6 translation faults.
