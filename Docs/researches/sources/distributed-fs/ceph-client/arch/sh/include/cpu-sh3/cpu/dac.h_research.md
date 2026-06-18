<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h -->
# sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h

## Purpose
Defines SH architecture declarations and macros for `dac` support in the Ceph client's vendored Linux source tree.

## Important APIs, Types, And Functions
Includes `linux/io.h`. Key macros/constants include `__ASM_CPU_SH3_DAC_H`, `DADR0`, `DADR1`, `DACR`, `DACR_DAOE1`, `DACR_DAOE0`, `DACR_DAE`. Register or hardware-address constants include `DACR`.

## Control Flow
Control flow is primarily compile-time selection plus boot-time consumption: SoC and CPU-family implementation files include these constants when registering clocks, IRQs, DMA channels, caches, timers, PFC state, or reset/watchdog handlers.

## State And Persistence
State is stored outside the header in CPU data, clock frameworks, interrupt controllers, timers, pin controllers, watchdog/RTC devices, or SoC platform code. Register address definitions here describe persistent hardware state but do not allocate storage.

## Dependencies And Integration Points
It directly depends on `linux/io.h`. Integration points are SH CPU subtype setup, interrupt-controller tables, clocksource/clock frameworks, DMA engines, pinmux, and board files.

## Risks And Edge Cases
Risks include wrong register addresses, IRQ event codes, transfer-size encodings, cache bit definitions, or subtype guards. Such errors often compile cleanly but break only on the affected SH board or CPU subtype.

## Test Signals
Useful signals are SH defconfig/allmodconfig builds, boot logs on each CPU subtype, clock/IRQ/DMA/watchdog/RTC driver probes, and hardware or QEMU smoke tests for subtype-specific register maps.

Source read size: 44 lines, 832 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/include/cpu-sh3/cpu/dac.h -->
