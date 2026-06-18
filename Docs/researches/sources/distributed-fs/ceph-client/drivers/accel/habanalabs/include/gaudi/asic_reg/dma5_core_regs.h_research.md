# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi/asic_reg/dma5_core_regs.h

## Purpose

`dma5_core_regs.h` is the generated register map for Gaudi `DMA5_CORE`. It defines 67 `mmDMA5_CORE_*` offsets from `0x5A0000` through `0x5A0238`, with `mmDMA5_CORE_BASE` at `0x7FFC5A0000ull`. The driver treats DMA5 as part of the PCI DMA group together with DMA0 and DMA1.

## Important APIs, Types, And Register Groups

The exported surface is macro-only. Register groups include core configuration/halt/enable, LBW outstanding control, source/destination base addresses, transfer sizes and strides, commit, write-completion address/data/AWUSER, tensor row count, protection and secure/non-secure properties, read/write outstanding/cache/user/inflight controls, rate limits, error cause/config/message registers, status, read debug-memory registers, and debug counters/status.

## Control Flow And State

The header has no executable code. DMA5 core control is performed either by direct macros in PCI stall paths (`mmDMA5_CORE_CFG_1`) or through common offset arithmetic. `gaudi_init_dma_core()` configures all DMA cores, while PCI DMA setup may assign DMA5 as one of the PCI engines. `gaudi_dma_core_transfer()` can use the same layout to execute direct DMA reads and polls core status/error registers.

Hardware state includes active transfer address/size/commit state, write completion target, inflight counters, rate-limit and cache settings, protection/security bits, debug memory, and error cause/message payloads. `gaudi_mmu_prepare()` writes `mmDMA5_CORE_NON_SECURE_PROPS`; reset restoration rewrites write-completion configuration and AWUSER for channels above DMA1, including DMA5.

## Dependencies And Integration Points

The header is included by `gaudi_regs.h` and depends on regular DMA core spacing used by `DMA_CORE_OFFSET`. It integrates with PCI DMA init/stall/disable paths, debugfs DMA transfers, engine idle diagnostics, reset restoration, and MMU ASID setup. Field masks and shifts are supplied by sibling generated headers, generally named for DMA0 core.

## Risks And Test Signals

Risks include corrupting host/device memory through wrong transfer register offsets, leaving the PCI DMA engine active during reset, incorrect write completion after reset, or failing MMU/security setup. Test signals are successful PCI DMA operation when DMA5 is assigned, no timeout in transfer polling, clean `ERR_CAUSE`, idle status after stop/stall, valid completion SOB writes after restore, and correct ASID behavior.
