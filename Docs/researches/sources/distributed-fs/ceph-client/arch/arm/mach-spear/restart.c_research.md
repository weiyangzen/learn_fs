# sources/distributed-fs/ceph-client/arch/arm/mach-spear/restart.c

## Purpose
This file implements SPEAr restart by requesting a software reset through the miscellaneous system reset control register.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `spear_restart`.
- Register/constant macro families: `SPEAR13XX`(1); examples: `SPEAR13XX_SYS_SW_RES`.

## Control Flow
Runtime control flow is called from adjacent platform init code or driver callbacks. It generally maps hardware registers, updates control bits, registers platform data, then returns errors upward when required resources are absent.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: memory-mapped hardware registers are read or written directly. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/io.h`, `linux/amba/sp810.h`, `linux/reboot.h`, `asm/system_misc.h`, `spear.h`, `generic.h`.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `restart.c`.

## Research Notes
- Read coverage: full file (857 bytes, 33 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
