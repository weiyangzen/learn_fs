# sources/distributed-fs/ceph-client/include/linux/mfd/stm32-timers.h

## Purpose

This 186-line header defines STM32 general-purpose timer register offsets, bitfields, DMA/IRQ metadata, parent state, and an optional DMA burst read helper.

## Important APIs, Types, and Functions

It exports `TIM_*` register offsets and bit macros, capture/compare and DMA request helper macros, hardware configuration fields, maximum prescaler/input-capture constants, encoder mode values, break/dead-time helpers, `enum stm32_timers_dmas`, `enum stm32_timers_irqs`, `struct stm32_timers_dma`, `struct stm32_timers`, and `stm32_timers_dma_burst_read()` with an `-ENODEV` stub when the MFD is not reachable.

## Control Flow

No direct runtime flow except the inline stub. Child drivers configure timer registers through regmap, optionally request DMA burst reads, and use IRQ/DMA metadata populated by the parent.

## State and Persistence Behavior

Timer counter, prescaler, auto-reload, capture/compare, DMA, break, trigger, and status state persists in hardware. Driver-owned DMA state includes completion, lock, active channel, and channel array.

## Dependencies and Integration Points

It integrates STM32 timer MFD parent with PWM, counter, IIO trigger/capture, DMAengine, interrupt, and regmap consumers.

## Risks and Edge Cases

Feature availability varies by timer IP and MP25 hardware fields. DMA burst access must serialize through the DMA lock and respect timeout. Channel helper macros assume 1-based channel numbers.

## Test Signals

Build tests with and without `CONFIG_MFD_STM32_TIMERS`, DMA burst read tests, PWM/capture/encoder hardware tests, IRQ line mapping tests, and register macro bounds checks.
