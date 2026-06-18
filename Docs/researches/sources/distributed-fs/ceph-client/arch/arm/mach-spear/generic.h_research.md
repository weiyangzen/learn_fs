# sources/distributed-fs/ceph-client/arch/arm/mach-spear/generic.h

## Purpose
This private SPEAr header declares timer, map_io, L2 cache, restart, SMP startup, CPU hotplug, and DMA platform hooks shared by SPEAr platform files.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear_restart`, `spear13xx_secondary_startup`, `spear13xx_cpu_die`.
- Register/constant macro families: `__MA`(1); examples: `__MACH_GENERIC_H`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/dmaengine.h`, `linux/amba/pl08x.h`, `linux/init.h`, `linux/reboot.h`, `asm/mach/time.h`.
- Integrates with device tree matching, `of_*` helpers, and `of_platform_populate()`/machine descriptors where present.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.
- headers are broadly included, so macro changes have a large blast radius across legacy board code.

## Test Signals
- Compile-test all in-tree users with `make ARCH=arm` for the affected SA-1100/SPEAr/shmobile/SoCFPGA configs; header regressions are best caught by building every including board file.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (1049 bytes, 41 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
