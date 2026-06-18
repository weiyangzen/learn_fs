<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h

## Purpose
Defines CPU-family cacheline sizing, cache-control register addresses, cache mode bits, and cache-array address constants.

## Important APIs, Types, And Functions
Key macros/constants include `__ASM_CPU_SH3_CACHE_H`, `L1_CACHE_SHIFT`, `SH_CACHE_VALID`, `SH_CACHE_UPDATED`, `SH_CACHE_COMBINED`, `SH_CACHE_ASSOC`, `SH_CCR`, `CCR_CACHE_CE`, `CCR_CACHE_WT`, `CCR_CACHE_CB`, `CCR_CACHE_CF`, `CCR_CACHE_ORA`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`, `CCR_CACHE_ENABLE`, `CCR_CACHE_INVALIDATE`, `CCR3_REG`, `CCR_CACHE_16KB`, plus 1 more. Register or hardware-address constants include `SH_CCR`, `CACHE_OC_ADDRESS_ARRAY`, `CACHE_PHYSADDR_MASK`, `CCR3_REG`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
Kconfig-sensitive paths mention `CONFIG_CPU_SUBTYPE_SH7705`, `CONFIG_CPU_SUBTYPE_SH7710`, `CONFIG_CPU_SUBTYPE_SH7720`, `CONFIG_CPU_SUBTYPE_SH7721`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 40 lines, 1134 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/cache.h -->
