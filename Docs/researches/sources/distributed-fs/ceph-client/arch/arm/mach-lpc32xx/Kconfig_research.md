# sources/distributed-fs/ceph-client/arch/arm/mach-lpc32xx/Kconfig

Purpose: Kconfig entry for NXP LPC32xx ARM926 platforms.

Important APIs/types/functions: Defines `ARCH_LPC32XX`, depending on multi-v5 little-endian ARM, selecting AMBA, LPC32xx clocksource, ARM926T, GPIOLIB, and optional LPC32xx DMA mux with PL08x.

Control flow: No runtime flow; it controls build inclusion and subsystem availability.

State and persistence: No runtime state. Build state affects clocksource, AMBA, GPIO, CPU, and DMA support.

Dependencies and integration points: Integrates with PL08x DMA, clocksource driver, and the `mach-lpc32xx` objects.

Risks: Little-endian and ARM926 assumptions are mandatory; missing selected subsystems breaks early platform support.

Test signals: Config build with DMA enabled/disabled and boot LPC32xx DT.
