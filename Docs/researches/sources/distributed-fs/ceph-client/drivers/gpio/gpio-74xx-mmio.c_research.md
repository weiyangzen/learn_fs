# sources/distributed-fs/ceph-client/drivers/gpio/gpio-74xx-mmio.c

## Purpose
This platform driver exposes simple memory-mapped 74xx logic devices as GPIO chips. Device-tree compatible data describes whether the device is input-only or output-only and how many bits it provides.

## Important APIs, types, and functions
`struct mmio_74xx_gpio_priv` wraps `struct gpio_generic_chip` plus encoded flags. Match data combines `MMIO_74XX_DIR_IN` or `MMIO_74XX_DIR_OUT` with a bit count. GPIO callbacks are `mmio_74xx_get_direction()`, `mmio_74xx_dir_in()`, and `mmio_74xx_dir_out()`. Probe uses `devm_platform_ioremap_resource()`, `gpio_generic_chip_init()`, and `devm_gpiochip_add_data()`.

## Control flow
Probe reads match data, maps one MMIO data register region, initializes a generic GPIO chip with byte size derived from the bit count, then overrides direction callbacks to enforce fixed hardware direction. Output direction writes the requested value through the generic set path.

## State and persistence behavior
There is no private persistent state beyond match flags. Values live in the external latch or buffer hardware and generic GPIO state. Direction is fixed by compatible string and never changed in hardware.

## Dependencies and integration points
The driver depends on OF matching, platform MMIO resources, and `gpio-generic`. It integrates a family of TI 74xx-compatible parts into gpiolib without per-chip C implementations.

## Risks and edge cases
Using the wrong compatible can expose the wrong line count or direction. Input attempts on output-only parts and output attempts on input-only parts return `-ENOTSUPP`. The generic chip assumes a simple contiguous data register sized by the encoded bit count.

## Test signals
Verify each compatible reports the expected `ngpio` and fixed direction, input-only devices reject output direction, output-only devices reject input direction, and MMIO writes/readbacks match the external latch wiring.
