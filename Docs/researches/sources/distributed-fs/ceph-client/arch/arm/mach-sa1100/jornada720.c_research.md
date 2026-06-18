# sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/jornada720.c

## Purpose
This board file registers the HP Jornada 720 machine: static memory mappings, SA1111 companion resources, Epson S1D13xxx framebuffer platform data, flash partitions, GPIO lookups, serial policy, and machine descriptor callbacks.

## Important APIs, Types, and Functions
- Important functions/entry symbols: `jornada720_set_vpp`, `JORNADA720 (HP Jornada 720)`.
- Initcall hooks: `jornada720_init`.
- Static data/types: `s1d13xxxfb_regval s1d13xxxfb_initregs`, `s1d13xxxfb_pdata s1d13xxxfb_data`, `resource s1d13xxxfb_resources`, `platform_device s1d13xxxfb_device`, `gpiod_lookup_table jornada_pcmcia_gpiod_table`, `resource sa1111_resources`, `sa1111_platform_data sa1111_info`, `platform_device sa1111_device`, `platform_device jornada_ssp_device`, `resource jornada_kbd_resources`, `platform_device jornada_kbd_device`, `gpiod_lookup_table jornada_ts_gpiod_table`, `platform_device jornada_ts_device`, `map_desc jornada720_io_desc`, plus 3 more.
- Register/constant macro families: `EPSONFBLEN`(1), `EPSONFBSTART`(1), `EPSONREGLEN`(1), `EPSONREGSTART`(1), `SA1111REGLEN`(1), `SA1111REGSTART`(1), `TUCR`(1); examples: `TUCR_VAL`, `SA1111REGSTART`, `SA1111REGLEN`, `EPSONREGSTART`, `EPSONREGLEN`, `EPSONFBSTART`, `EPSONFBLEN`.

## Control Flow
Boot control flow is descriptor-driven: machine matching calls map/init/timer callbacks, static platform data is registered, DT children are populated where applicable, and late init or arch initcalls finish board-specific devices after core subsystems are ready.

## State and Persistence Behavior
State is kernel-resident and hardware-facing: static kernel data records board resources, register bases, cached flags, or callback tables; persistent hardware description is encoded as machine descriptors, platform devices, resources, and DT compatibles; in-memory locks serialize access to shared controller state. No user-space persistent files are written by this code.

## Dependencies and Integration Points
- Direct includes: `linux/init.h`, `linux/kernel.h`, `linux/tty.h`, `linux/delay.h`, `linux/gpio/machine.h`, `linux/platform_data/sa11x0-serial.h`, `linux/platform_device.h`, `linux/ioport.h`, `linux/mtd/mtd.h`, `linux/mtd/partitions.h`, `video/s1d13xxxfb.h`, `asm/hardware/sa1111.h`, `asm/page.h`, `asm/mach-types.h`, `asm/setup.h`, `asm/mach/arch.h`, `asm/mach/flash.h`, `asm/mach/map.h`, plus 3 more.
- Integrates with platform-device/resource registration and legacy board data handoff.
- Integrates with Linux IRQ domains/chained interrupt flow and board IRQ number definitions.
- Integrates with gpiolib lookup tables, GPIO chips, or board GPIO bit definitions.
- Integrates with AMBA PL080/PL08x DMA platform data and request-signal muxing.

## Risks
- incorrect register constants or bit masks can break boot, interrupt routing, reset, or low-power entry on real hardware.
- IRQ number/routing mistakes show up as lost interrupts or interrupt storms rather than compile failures.
- DMA request mux conflicts can silently route a peripheral to the wrong request line.

## Test Signals
- Compile with the platform enabled and run boot smoke tests for machine/DT compatibles covered by `jornada720.c`.
- Run `make ARCH=arm dtbs_check` for affected DTS files and confirm the expected machine compatible reaches this platform code at boot.
- Validate interrupt and GPIO paths with the attached devices that use the declared lines, watching `/proc/interrupts` and driver probe logs.
- Run DMA-using peripheral transfers and check that request-line allocation/release pairs do not conflict under concurrent users.

## Research Notes
- Read coverage: full file (12822 bytes, 381 lines).
- This is Linux ARM platform support code under `sources/distributed-fs/ceph-client`; it is kernel/architecture glue rather than distributed filesystem client logic.
