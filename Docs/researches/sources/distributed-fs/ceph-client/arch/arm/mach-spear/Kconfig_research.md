# sources/distributed-fs/ceph-client/arch/arm/mach-spear/Kconfig

## Purpose
This Kconfig fragment describes ST SPEAr3xx and SPEAr13xx ARM platform options, SMP/hotplug dependencies, and machine selections.

## Important APIs, Types, and Functions
- Kconfig symbols: `PLAT_SPEAR`, `ARCH_SPEAR13XX`, `MACH_SPEAR1310`, `MACH_SPEAR1340`, `ARCH_SPEAR3XX`, `MACH_SPEAR300`, `MACH_SPEAR310`, `MACH_SPEAR320`, `ARCH_SPEAR6XX`, `ARCH_SPEAR_AUTO`.

## Control Flow
Kconfig evaluation is declarative: selecting the platform symbol pulls in architecture, timer, clock, SMP, hotplug, and PM dependencies. No runtime code executes from this file, but the resulting `.config` decides which adjacent objects are compiled.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with clocksource/clock framework setup during early platform initialization.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-spear`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1909 bytes, 91 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
