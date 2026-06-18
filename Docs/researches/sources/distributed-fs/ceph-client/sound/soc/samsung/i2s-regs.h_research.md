# sources/distributed-fs/ceph-client/sound/soc/samsung/i2s-regs.h

## Purpose
Defines Samsung I2S register offsets and bit fields used by the Samsung I2S and internal DMA drivers.

## Important APIs, Types, And Functions
Macro groups cover `I2SCON`, `I2SMOD`, FIFO control/status, prescaler, AHB internal DMA, transfer size/count, stream addresses, TDM/status registers, active/pause bits, format/clock selection fields, variant-specific Exynos bit positions, FIFO count extractors, and IDMA level interrupt controls.

## Control Flow
No executable flow. The macros are used by `i2s.c` for DAI control and by `idma.c` for internal DMA setup and interrupts.

## State And Persistence
No software state. The defined fields describe MMIO state saved/restored by `i2s.c` runtime PM and manipulated by IDMA.

## Dependencies And Integration Points
Consumed by Samsung I2S controller and IDMA component. It must match hardware layout variants referenced through per-variant offsets in `i2s.c`.

## Risks And Edge Cases
- Shared macros cover multiple hardware generations; callers must use variant offsets/masks correctly.
- FIFO count macros encode fixed bit widths and differ for secondary FIFO.
- IDMA macros are tightly coupled to the internal-DMA ring logic in `idma.c`.

## Test Signals
Compile coverage plus hardware register trace tests for I2S format, BCLK/RCLK, FIFO flush, active/pause, and IDMA interrupt behavior.
