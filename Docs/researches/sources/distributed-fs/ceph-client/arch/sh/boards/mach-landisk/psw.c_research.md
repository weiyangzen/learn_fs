<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c

## Purpose
LANDISK push-switch devices. It wires power and front-panel switches to the push-switch driver with platform_data and shared IRQ resource handling.

## Important APIs, Types, and Functions
- functions: psw_irq_handler, psw_init.
- assembly/entry labels: out.
- integration hooks: platform_add_devices, device_initcall.

## Control Flow
- The file is invoked by board setup or initcall paths and translates fixed board registers/GPIOs into kernel subsystem callbacks.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/io.h, linux/init.h, linux/interrupt.h, linux/platform_device.h, mach-landisk/mach/iodata_landisk.h, asm/push-switch.h.
- resource/data arrays: psw_power_resources, psw_usl5p_resources.
- Source-tree integration: mach-landisk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.

## Test Signals
- compile coverage plus boot-time subsystem probe messages are the available signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-landisk/psw.c -->
