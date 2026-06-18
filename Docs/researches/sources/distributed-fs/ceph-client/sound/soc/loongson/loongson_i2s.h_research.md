# sources/distributed-fs/ceph-client/sound/soc/loongson/loongson_i2s.h

## Purpose
Defines Loongson I2S register offsets, control bits, DMA data structures, and shared private device state.

## Important APIs, Types, And Functions
Macros describe common registers (`LS_I2S_VER`, `CFG`, `CTRL`, RX/TX data), revision-specific `CFG1`, PCI DMA order registers, and I2S control bits. `struct loongson_dma_data` stores direct DMA device address, order register, and IRQ. `struct loongson_i2s` stores device, DMA data unions for dmaengine or custom DMA, regmap, MMIO base, revision, clock rate, and sysclk. It declares `loongson_i2s_pm` and `loongson_i2s_dai`.

## Control Flow, State, And Persistence
No control flow. The structures persist across probe and stream operations in both PCI and platform front ends.

## Dependencies And Integration Points
Used by `loongson_i2s.c`, `loongson_i2s_pci.c`, `loongson_i2s_plat.c`, and `loongson_dma.c`. The unions allow one common DAI to serve generic dmaengine and custom descriptor DMA paths.

## Risks And Test Signals
Risks include union misuse between front ends, register max ranges that differ by front end, and ABI dependence on specific hardware bit positions. Test signals are builds and runtime tests for both PCI and platform drivers, including DMA data correctness.
