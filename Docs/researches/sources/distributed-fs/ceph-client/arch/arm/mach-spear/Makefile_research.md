# sources/distributed-fs/ceph-client/arch/arm/mach-spear/Makefile

## Purpose
This Makefile selects SPEAr platform, clock/timer, DMA, restart, SMP, hotplug, and per-SoC board objects based on configuration.

## Important APIs, Types, and Functions
- Build rules: `obj-y -> restart.o time.o`, `obj-$(CONFIG_ARCH_SPEAR13XX) -> spear13xx.o $(smp-y)`, `obj-$(CONFIG_MACH_SPEAR1310) -> spear1310.o`, `obj-$(CONFIG_MACH_SPEAR1340) -> spear1340.o`, `obj-$(CONFIG_ARCH_SPEAR3XX) -> spear3xx.o`, `obj-$(CONFIG_ARCH_SPEAR3XX) -> pl080.o`, `obj-$(CONFIG_MACH_SPEAR300) -> spear300.o`, `obj-$(CONFIG_MACH_SPEAR310) -> spear310.o`, `obj-$(CONFIG_MACH_SPEAR320) -> spear320.o`, `obj-$(CONFIG_ARCH_SPEAR6XX) -> spear6xx.o`, `obj-$(CONFIG_ARCH_SPEAR6XX) -> pl080.o`.

## Control Flow
Build control flow is make-driven. Configuration symbols expand object lists, so later boot-time behavior appears only when the corresponding `obj-*` rule includes the source file in `built-in.a`.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Build configuration smoke test: enable the relevant platform symbols and run `make ARCH=arm olddefconfig` plus a build that descends into `sources/distributed-fs/ceph-client/arch/arm/mach-spear`.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (669 bytes, 26 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
