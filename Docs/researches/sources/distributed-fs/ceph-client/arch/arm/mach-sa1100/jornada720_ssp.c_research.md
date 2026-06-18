# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720_ssp.c

## Purpose
This file implements Jornada 720-specific SSP helpers used to communicate with board-attached peripherals through the SA-1100 synchronous serial port.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `jornada_ssp_byte`, `jornada_ssp_inout`, `jornada_ssp_start`, `jornada_ssp_end`, `jornada_ssp_probe`, `jornada_ssp_remove`.
- Exported symbols: `jornada_ssp_reverse`, `jornada_ssp_byte`, `jornada_ssp_inout`, `jornada_ssp_start`, `jornada_ssp_end`.
- Static data/types: `platform_driver jornadassp_driver`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/delay.h`, `linux/errno.h`, `linux/init.h`, `linux/kernel.h`, `linux/module.h`, `linux/platform_device.h`, `linux/sched.h`, `linux/io.h`, `mach/hardware.h`, `mach/jornada720.h`, `asm/hardware/ssp.h`.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.

## Risks
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `jornada720_ssp.c`.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.

## Research Notes
- Read coverage: full file (4490 bytes, 203 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
