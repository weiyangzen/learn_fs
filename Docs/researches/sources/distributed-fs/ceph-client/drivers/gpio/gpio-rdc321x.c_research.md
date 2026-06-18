# sources/distributed-fs/ceph-client/drivers/gpio/gpio-rdc321x.c

## Purpose
This legacy platform driver exposes RDC321x southbridge GPIOs backed by PCI configuration-space registers. It supports two 32-bit register groups and uses platform data from the RDC321x MFD layer to find the southbridge PCI device and GPIO count.

## Important APIs, Types, and Functions
`struct rdc321x_gpio` contains the gpio chip, PCI device pointer, cached data registers, register offsets for control/data pairs, and a spinlock. `rdc_gpio_get_value()` reads through PCI config space after writing the cached selector value. `rdc_gpio_set_value_impl()` updates the cached output register and writes it. `rdc_gpio_config()` sets the line as GPIO and then writes the requested output value.

## Control Flow
`rdc321x_gpio_probe()` validates platform data, obtains named IO resources `gpio-reg1` and `gpio-reg2`, initializes register offsets, reads initial data register values into the cache, and registers the gpio chip. Direction input and direction output both call `rdc_gpio_config()`, with input passing a high value by convention.

## State and Persistence
The driver keeps `data_reg[2]` as a software shadow of the output/data register values because writes are done through PCI config space. It initializes the cache from hardware at probe but has no suspend/resume path.

## Dependencies and Integration Points
It depends on `linux/mfd/rdc321x.h` platform data, PCI config read/write APIs, platform named IO resources, and gpiolib. It uses a static GPIO base of 0, which reflects older board expectations.

## Risks
Direction handling is unusual: input configuration still writes a data value, and there is no separate `get_direction()`. PCI config operations are serialized only by the local spinlock, so any other southbridge user touching the same registers must coordinate externally. Fixed base 0 can collide on systems with other non-dynamic chips.

## Test Signals
Test initial cache loading, both register groups above and below GPIO 32, error propagation from PCI config reads/writes, output set/get consistency, and platform data/resource absence paths.
