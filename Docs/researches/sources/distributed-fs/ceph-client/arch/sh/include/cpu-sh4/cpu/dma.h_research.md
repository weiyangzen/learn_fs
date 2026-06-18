<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h

## Purpose
Defines CPU-family DMAC base addresses and interrupt event mappings used by the SH DMA engine.

## Important APIs, Types, And Functions
Includes `linux/sh_intc.h`. Key macros/constants include `__ASM_CPU_SH4_DMA_H`, `DMTE0_IRQ`, `DMTE4_IRQ`, `DMTE6_IRQ`, `DMAE0_IRQ`, `SH_DMAC_BASE0`. Register or hardware-address constants include `__ASM_CPU_SH4_DMA_H`, `DMTE0_IRQ`, `DMTE4_IRQ`, `DMTE6_IRQ`, `DMAE0_IRQ`, `SH_DMAC_BASE0`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/sh_intc.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 17 lines, 355 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh4/cpu/dma.h -->
