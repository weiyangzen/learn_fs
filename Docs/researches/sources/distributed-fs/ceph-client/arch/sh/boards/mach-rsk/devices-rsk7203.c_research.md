<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c -->
# sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c

## Purpose
RSK7203 extra devices. It registers SMSC911x Ethernet, GPIO LEDs, and GPIO keys through platform devices during device_initcall.

## Important APIs, Types, and Functions
- functions: rsk7203_devices_setup.
- integration hooks: platform_add_devices, device_initcall, gpio_request.

## Control Flow
- Early machine-vector callbacks and/or initcalls configure pins, register board info, and call platform_add_devices so subsystem drivers can bind to static resources.

## State and Persistence
- programs persistent hardware registers/GPIO levels that remain in effect after initialization.
- static platform/I2C/SPI/GPIO lookup data persists for driver probing.

## Dependencies and Integration Points
- headers: linux/init.h, linux/types.h, linux/platform_device.h, linux/interrupt.h, linux/smsc911x.h, linux/input.h, linux/gpio.h, linux/gpio_keys.h, linux/leds.h, asm/machvec.h.
- resource/data arrays: smsc911x_resources, rsk7203_gpio_leds, rsk7203_gpio_keys_table.
- Source-tree integration: mach-rsk; final consumers are SuperH machine vectors, Kbuild object selection, and platform subsystem drivers.

## Risks and Edge Cases
- hard-coded physical registers must match the exact board revision and bus width.
- pinmux/GPIO conflicts can break unrelated peripherals because most requests ignore errors.

## Test Signals
- board boot logs should show platform devices binding, correct resource ranges, and no GPIO/I2C/SPI registration failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sh/boards/mach-rsk/devices-rsk7203.c -->
