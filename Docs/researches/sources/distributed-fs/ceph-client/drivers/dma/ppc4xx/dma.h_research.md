# sources/distributed-fs/ceph-client/drivers/dma/ppc4xx/dma.h Research

## Purpose
`dma.h` describes the PPC440SPe DMA engine command descriptor format, DMA/I2O register maps, and bit definitions used by the ADMA driver. It is the low-level hardware contract for DMA0 and DMA1.

## Important APIs, Types, and Functions
There are no functions. Important constants include two DMA engines, two maximum destinations, FIFO sizes, FIFO enable bit, DMA priority settings, force-alignment configuration, UIC interrupt bits, I2O interrupt mask bits, CDB address/status masks, CDB opcodes (`MV_SG1_SG2`, `MULTICAST`, `DFILL128`, `DCHECK128`), cued XOR address markers, multiplier and RXOR region offsets, and SG role selectors.

`struct dma_cdb` is the 32-byte command descriptor block consumed by DMA0/DMA1. It carries attributes, opcode, SG1 source address, byte count, and SG2/SG3 destination or check operands. `struct dma_regs` maps the DMA engine MMIO region, including command/status FIFO ports and pointers, destination status, configuration, active command pointer, byte pointer registers, error address/status, operation, and FIFO-size register. `struct i2o_regs` maps the shared I2O block used for interrupt masking and FIFO base/size configuration.

## Control Flow
This header is declarative, but `adma.c` uses it throughout control flow. Probe programs `fsiz`, `cfg`, and `dsts` through `struct dma_regs`. Submit writes CDB physical addresses with `DMA_CDB_NO_INT` into the command FIFO. Completion reads status FIFO entries, masks physical addresses with `DMA_CDB_ADDR_MSK`, interprets `DMA_CDB_STATUS_MSK` for zero-sum failures, and clears DMA error status. RAID6 descriptor setup encodes cued XOR base/HB addresses, multipliers, and RXOR regions into the upper SG fields defined here.

## State and Persistence
The header defines hardware-visible state layout rather than persistent software state. CDB contents live in coherent DMA memory allocated by `adma.c`, while register fields persist in the device until reset, remove, or reconfiguration. I2O FIFO base programming points at the shared DMA FIFO backing buffer allocated during global initialization.

## Dependencies and Integration Points
It depends only on Linux fixed-width types. It is included by `adma.h`, and therefore by `adma.c`. It integrates with PPC440SPe hardware documentation, the I2O node discovered from device tree, and PowerPC register accessors used by the driver. The `CONFIG_440SP` conditional changes cued multiplier and region bit placement, so the same driver source can target PPC440SP and PPC440SPe variants.

## Risks and Edge Cases
The structures must match hardware offsets exactly. Any padding or field width mismatch would make MMIO and descriptor programming unsafe. The CDB address mask assumes 16-byte descriptor alignment. The conditional multiplier offsets are especially sensitive because RAID6 math correctness depends on encoding coefficients into the exact bits expected by the hardware. FIFO size constants are used to derive descriptor pool size and I2O FIFO backing size, so changes affect memory allocation and command FIFO capacity.

## Test Signals
Compile tests for PPC440SP/PPC440SPe configurations check the conditional constants. Runtime signals include correct DMA FIFO setup, successful CDB submission/completion, zero-sum status reporting, no DMA destination status errors, and RAID6 parity correctness across WXOR/RXOR paths.
