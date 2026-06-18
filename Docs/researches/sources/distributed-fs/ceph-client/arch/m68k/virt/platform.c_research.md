# sources/distributed-fs/ceph-client/arch/m68k/virt/platform.c

## Purpose

supports the m68k virtual platform used by emulators, including bootinfo parsing, Goldfish timer,
platform devices, interrupts, and reboot hooks

## Important APIs, Types, and Functions

Source read size: 94 lines, 2365 bytes. Includes: `linux/platform_device.h`, `linux/interrupt.h`,
`linux/memblock.h`, `asm/virt.h`, `asm/irq.h`. Defined functions: `virt_virtio_init`,
`virt_platform_init`. Declared functions: `platform_device_register_simple`, `ARRAY_SIZE`,
`platform_device_unregister`. Key macros/defines: `VIRTIO_BUS_NB`. Types visible in this file:
`platform_device`.

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
