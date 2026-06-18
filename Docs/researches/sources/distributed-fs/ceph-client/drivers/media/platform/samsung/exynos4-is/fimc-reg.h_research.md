# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos4-is/fimc-reg.h

## Purpose
Defines Samsung FIMC register offsets, bit fields, SYSREG writeback bits, and register helper prototypes.

## Important APIs, Types, and Functions
Key definitions cover source format, crop offsets, global control, output/input DMA addresses and offsets, target format, scaler, status, capture control, effects, tiled DMA parameters, CSI image format, and output DMA sequence mask. The inline `fimc_hw_set_dma_seq()` writes `FIMC_REG_CIFCNTSEQ`.

## Control Flow
The header supplies the constants used by `fimc-reg.c` and higher-level capture/M2M code to reset hardware, select camera sources, configure scaler/DMA paths, activate capture, and query active frame indices.

## State and Persistence
No software state is defined here; all constants describe volatile hardware register state. Register state must be rebuilt by callers when hardware is reset or resumed.

## Dependencies and Integration Points
Includes `fimc-core.h` for core device/context types and is consumed by FIMC capture, M2M, and media writeback integration.

## Risks and Edge Cases
Many masks encode limited 11- to 12-bit width/height fields, so out-of-range geometry corrupts adjacent bits if not bounded earlier. Some declarations, such as `fimc_hw_en_irq()`, are present without an implementation in this file, so link coverage depends on other compilation units or dead code.

## Test Signals
Compile all FIMC configurations, compare register constants with SoC manuals, validate sequence masks for four versus 32 output buffers, and trace capture enable/disable bit transitions.
