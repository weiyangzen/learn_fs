# sources/distributed-fs/ceph-client/drivers/gpio/gpio-amd-fch.c

## Purpose
This platform driver exposes GPIO pins on AMD G-series FCH hardware such as GX-412TC. It uses platform data to map logical GPIO lines to registers in the fixed FCH MMIO GPIO bank.

## Important APIs, types, and functions
`struct amd_fch_gpio_priv` stores the `gpio_chip`, MMIO base, platform data, and spinlock. `amd_fch_gpio_addr()` translates logical offsets through `pdata->gpio_reg[]`. GPIO operations are direction input/output, get direction, get, set, and a no-op request callback. Probe maps the fixed resource at `0xFED81500`.

## Control flow
Probe requires `struct amd_fch_gpio_pdata`, allocates state, fills line count and names from platform data, initializes callbacks and lock, maps the global MMIO resource, stores drvdata, and registers the chip. Each GPIO operation locks, reads the selected register, updates direction/write bits as needed, and writes it back.

## State and persistence behavior
State is in FCH MMIO registers. Direction uses bit 23, output write state uses bit 22, and input read state uses bit 16. No cache is maintained, and register changes persist until hardware reset or another agent modifies them.

## Dependencies and integration points
The driver depends on platform data from `gpio-amd-fch.h`, platform devices, fixed MMIO mapping, and gpiolib. It has no IRQ support in this file.

## Risks and edge cases
The fixed MMIO base assumes the platform data/device is created only for compatible systems. Incorrect `gpio_reg[]` mapping can access the wrong FCH registers. The request callback does not reserve or mux pins, so board code must ensure pins are safe for GPIO use.

## Test signals
Validate probe with platform data, correct line names/count, direction bit transitions, output bit writes, input read bit extraction via `FIELD_GET`, and rejection when platform data is missing.
