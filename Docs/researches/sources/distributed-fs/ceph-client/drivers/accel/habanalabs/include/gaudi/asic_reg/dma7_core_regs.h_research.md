# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma7_core_regs.h

## Purpose

`dma7_core_regs.h` is the generated register map for the Gaudi `DMA7_CORE` block. It provides 67 `mmDMA7_CORE_*` macros from `0x5E0000` through `0x5E0238`; `gaudi_blocks.h` maps `mmDMA7_CORE_BASE` at `0x7FFC5E0000ull`. DMA7 is an HBM DMA engine in the driver.

## Important APIs, Types, And Register Groups

The file defines no functions, structs, or enums. Its macro groups represent core config/halt/enable, LBW max outstanding, source and destination bases, source/destination size and stride registers, commit, write completion payload and address, TE row count, protection and security properties, read/write outstanding/cache/user/inflight tuning, read/write rate limits, error configuration/cause/message registers, status, debug memory access, and AXI/descriptor debug counters.

## Control Flow And State

The header has no executable control flow. DMA7 core behavior is driven through common DMA core offset arithmetic and direct HBM stall writes. `gaudi_init_dma_core()` configures the core, `gaudi_dma_core_transfer()` uses the shared register layout for programmed transfers, and HBM reset/stall code writes `mmDMA7_CORE_CFG_1`.

State persists in hardware registers: transfer address and geometry, commit state, inflight counters, completion writeback target, error cause, rate controls, debug memory, and MMU/security properties. Reset restoration rewrites completion and AWUSER registers for DMA7. `gaudi_mmu_prepare()` writes `mmDMA7_CORE_NON_SECURE_PROPS`.

## Dependencies And Integration Points

The header is aggregated by `gaudi_regs.h`. It depends on the common DMA core block layout and `DMA_CORE_OFFSET` in `gaudiP.h`; bit-level use depends on sibling shift/mask headers. Integration points include HBM DMA initialization and stall, DMA transfer helper paths, debugfs reads, engine idle reporting, reset restoration, and MMU ASID setup.

## Risks And Test Signals

Risk areas are incorrect transfer-control offsets causing corruption, failed halt during reset, lost write completions, hidden errors due to wrong error-message offsets, and MMU/ASID property drift. Test signals include successful DMA7 HBM transfers, no `gaudi_dma_core_transfer()` timeout, zero `ERR_CAUSE`, idle status after HBM stop/stall, valid completion restoration after reset, and correct operation under MMU-enabled contexts.
