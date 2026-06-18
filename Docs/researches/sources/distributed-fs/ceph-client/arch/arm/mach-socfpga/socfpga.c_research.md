# sources/distributed-fs/ceph-client/arch/arm/mach-socfpga/socfpga.c

## Purpose
This file is the DT machine setup for SoCFPGA platforms, including reset-manager lookup, system manager/SDRAM base discovery, restart handling, and machine descriptors.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `socfpga_cyclone5_restart`, `socfpga_arria10_restart`, `SOCFPGA (Altera SOCFPGA)`, `SOCFPGA_A10 (Altera SOCFPGA Arria10)`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly; static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/irqchip.h`, `linux/of.h`, `linux/of_address.h`, `linux/reboot.h`, `linux/reset/socfpga.h`, `asm/mach/arch.h`, `asm/mach/map.h`, `asm/cacheflush.h`, `core.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- missing DT nodes, failed mappings, or resource conflicts leave platform devices partially unavailable.
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- compatible-string drift between DTS and machine/setup code prevents the intended initialization path from running.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `socfpga.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (2857 bytes, 119 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
