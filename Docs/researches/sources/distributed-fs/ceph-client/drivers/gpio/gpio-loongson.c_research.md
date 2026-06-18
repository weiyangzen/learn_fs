<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c

## Purpose
`gpio-loongson.c` is a legacy Loongson-2F/3A/3B GPIO driver using architecture-specific global registers. It registers a simple fixed-base gpiochip very early.

## Important APIs, types, and functions
The file uses `LOONGSON_GPIODATA` and `LOONGSON_GPIOIE` macros from architecture headers, protected by global `gpio_lock`. GPIO callbacks implement get, set, direction input, and direction output. `loongson_gpio_setup()` registers both the platform driver and a simple platform device.

## Control flow
Postcore init registers the driver and immediately creates a `loongson-gpio` platform device. Probe allocates a gpiochip, sets fixed base 0, line count based on CPU config, installs callbacks, and calls `gpiochip_add_data()`.

## State and persistence behavior
All state is in architecture GPIO registers. There is no managed remove path and no software cache. Input values are read from the upper half of `GPIODATA`, while output values are written to lower bits.

## Dependencies and integration points
This depends on Loongson architecture headers and CPU configuration. It is for older non-DT platforms and uses fixed GPIO numbering.

## Risks and edge cases
Fixed base 0 can conflict with other gpiochips. Probe uses `gpiochip_add_data()` instead of devm registration, and the created platform device is not retained for cleanup. The line count changes with build configuration.

## Test signals
Test early boot registration, GPIO direction/value operations on 2F and 3A/3B hardware, fixed numbering compatibility, and coexistence rules when the modern Loongson driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-loongson.c -->
