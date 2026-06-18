# sources/distributed-fs/ceph-client/arch/arm/mach-spear/hotplug.c

## Purpose
This file implements SPEAr13xx CPU hotplug shutdown by disabling coherency/cache state, executing WFI, and reporting spurious wakeups.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `cpu_enter_lowpower`, `cpu_leave_lowpower`, `spear13xx_do_lowpower`, `spear13xx_cpu_die`.

## Control Flow
The SMP path maps controller registers during early init, installs boot vectors or reset hooks for a target CPU, releases that CPU from reset or standby, waits for the common secondary startup path to report online, and optionally powers the CPU back down during hotplug or suspend.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: the file itself stores no runtime state beyond compile-time declarations. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/kernel.h`, `linux/errno.h`, `linux/smp.h`, `asm/cp15.h`, `asm/smp_plat.h`, `generic.h`.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with ARM SMP operations, secondary CPU startup, SCU/APMU/reset-manager logic, and CPU hotplug where enabled.

## Risks
- poll loops around hardware status can hang or add boot/suspend latency if clocks, reset bits, or DT register bases are wrong.
- power-management paths are hard to test under emulation and can lose resume context or cache coherency when sequencing changes.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `hotplug.c`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (1952 bytes, 101 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
