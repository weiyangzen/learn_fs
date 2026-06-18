# sources/distributed-fs/ceph-client/sound/soc/samsung/idma.h

## Purpose
Declares constants and the initialization hook for Samsung I2S internal DMA.

## Important APIs, Types, And Functions
Defines `LPAM_DMA_STOP`, `LPAM_DMA_START`, `MAX_IDMA_PERIOD`, `MAX_IDMA_BUFFER`, and prototype `idma_reg_addr_init(void __iomem *regs, dma_addr_t addr)`.

## Control Flow
No executable flow. `i2s.c` uses the prototype to hand MMIO base and low-power memory address to `idma.c`.

## State And Persistence
No state in the header.

## Dependencies And Integration Points
Depends on `dma_addr_t` and `void __iomem` types from including kernel headers. Couples the I2S controller driver to the IDMA PCM component.

## Risks And Edge Cases
The fixed buffer limits are compile-time constants and must match hardware/firmware low-power memory allocation expectations.

## Test Signals
Compile coverage and IDMA playback buffer/period limit validation.
