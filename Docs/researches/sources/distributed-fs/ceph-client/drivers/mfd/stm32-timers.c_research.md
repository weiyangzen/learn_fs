# sources/distributed-fs/ceph-client/drivers/mfd/stm32-timers.c

## Purpose
`stm32-timers.c` is the MFD parent and shared helper provider for STM32 general-purpose timers. It exposes a clocked MMIO regmap, IRQ metadata, optional DMA channels, counter-width detection, and an exported DMA burst-read API for child drivers.

## Important APIs, Types, and Functions
The exported helper is `stm32_timers_dma_burst_read()`. DMA internals include `stm32_timers_dma_done()`, `stm32_timers_dma_probe()`, and `stm32_timers_dma_remove()`. Hardware probing uses `stm32_timers_get_arr_size()` and `stm32_timers_probe_hwcfgr()`. IRQ discovery uses `stm32_timers_irq_probe()`. Parent lifecycle is `stm32_timers_probe()` and `stm32_timers_remove()`.

## Control Flow
Probe maps registers, stores the physical base for DMA, creates a regmap using the `"int"` clock, gets the timer clock, detects counter width from HWCFGR/IPIDR or ARR write/readback fallback, discovers either a global IRQ or all four named IRQs, requests optional DMA channels, stores driver data, and populates child OF devices. Remove depopulates children before releasing DMA channels.

## State and Persistence
`struct stm32_timers` holds regmap, clock, maximum ARR, optional IP ID, IRQ array/count, and DMA state. DMA state includes channel array, active channel, completion, mutex, and physical base. Hardware timer and DMA registers are volatile. No persistent storage exists.

## Dependencies and Integration Points
It depends on STM32 timer headers, platform resources, regmap MMIO with clock support, DMAengine, OF child population, resets indirectly through included headers, and child PWM/counter/IIO drivers using parent data and exported DMA burst reads.

## Risks and Edge Cases
DMA burst read validates ranges but still depends on caller-provided DMA-safe buffers. It serializes one DMA burst at a time with a mutex and terminates DMA on all exits. IRQ configuration must be either one global IRQ or exactly all four named IRQs. HWCFGR IPIDR mismatch rejects unsupported hardware.

## Test Signals
Exercise global and split IRQ DT layouts, optional DMA absent and present, timeout and interruptible DMA completion paths, ARR-width fallback, STM32MP25 IPIDR validation, child depopulation before DMA release, and exported burst reads from child drivers.
