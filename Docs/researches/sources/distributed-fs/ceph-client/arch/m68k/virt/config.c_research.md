# sources/distributed-fs/ceph-client/arch/m68k/virt/config.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 92 lines, 2146 bytes. Includes: `linux/reboot.h`, `linux/serial_core.h`,
`clocksource/timer-goldfish.h`, `asm/bootinfo.h`, `asm/bootinfo-virt.h`, `asm/byteorder.h`,
`asm/machdep.h`, `asm/virt.h`, `asm/config.h`. Defined functions: `virt_get_model`, `virt_reset`,
`virt_parse_bootinfo`, `virt_sched_init`, `config_virt`. Declared functions: `snprintf`. Types
visible in this file: `virt_booter_data`.

## Control Flow and Behavior

control flow starts from the machine config entry, which fills machdep callbacks, configures
IRQ/timer/console/reset hooks, parses bootinfo where needed, and registers platform devices

## State and Persistence

persistent state includes global machdep function pointers, board control register values, parsed
bootinfo data, timer/IRQ state, and platform-device registration records

## Dependencies and Integration Points

integrates with arch/m68k setup, bootinfo records, generic IRQ/time/reboot/platform-device
frameworks, and board-specific hardware headers

## Risks and Test Signals

incorrect callbacks or register programming can prevent console, timer, disk, or reset operation;
board defconfig builds, boot logs, timer ticks, interrupts, and reboot tests are signals
