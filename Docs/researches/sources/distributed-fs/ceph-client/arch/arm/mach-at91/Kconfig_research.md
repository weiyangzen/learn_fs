# sources/distributed-fs/ceph-client/arch/arm/mach-at91/Kconfig

Purpose: declares AT91/Microchip SoC family selection across ARMv4T/v5/v7/v7-M, including SAMA5, SAMA7, SAM9, SAMV7, LAN966, clocksource choices, PM, clock feature flags, and shared family symbols.

Control flow is Kconfig dependency/selection logic. It drives compilation of machine, PM, timer, clock, memory, pinctrl, interrupt, and secure PM support. Persistent runtime state is outside this file; this file defines which subsystems exist. Risks include dependency mismatches between SoC families, default clocksource choices with lower resolution, and feature flags not matching hardware blocks. Test signals are randconfig/defconfig build coverage, expected object selection in `mach-at91/Makefile`, and boot on representative AT91, SAM9, SAMA5, SAMA7, and SAMV7 DTs.
