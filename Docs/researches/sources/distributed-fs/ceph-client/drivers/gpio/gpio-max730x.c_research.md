<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c

## Purpose
`gpio-max730x.c` contains the shared GPIO implementation for Maxim MAX7300/MAX7301 28-line expanders, independent of whether the bus is I2C or SPI.

## Important APIs, types, and functions
The public helpers are `__max730x_probe()` and `__max730x_remove()`. GPIO callbacks include `max7301_direction_input()`, `max7301_direction_output()`, `max7301_get()`, `max7301_set()`, and internal `__max7301_set()`. State is stored in `struct max7301` fields such as `port_config`, `out_level`, `input_pullup_active`, callbacks, and mutex.

## Control flow
The bus wrapper allocates `struct max7301` and supplies read/write callbacks. Probe initializes the mutex, powers up the chip, applies platform base and pull-up mask, configures all 28 exported pins as inputs with default pull-up disabled unless requested, caches port configuration bytes, and registers the gpiochip. Remove powers down the chip.

## State and persistence behavior
`port_config[]` mirrors four pins per config register. `out_level` caches output values because output reads return the cached level. Hardware power state is changed on probe/remove.

## Dependencies and integration points
This core depends on wrapper-provided bus callbacks and optional `max7301_platform_data`. It exports GPL symbols used by MAX7300 I2C and MAX7301 SPI wrappers.

## Risks and edge cases
The first four chip pins are unused, so all GPIO offsets are shifted by four. Initialization writes every pin to input mode; board defaults can change at probe. The driver avoids forbidden zero config writes by seeding config bytes with `0xAA`; changing that can violate datasheet constraints.

## Test signals
Test all 28 offsets with +4 mapping, input pull-up platform mask, output cached get, direction register packing, power up/down register writes, and error propagation from bus callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max730x.c -->
