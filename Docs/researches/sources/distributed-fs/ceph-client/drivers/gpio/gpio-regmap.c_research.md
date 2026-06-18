# sources/distributed-fs/ceph-client/drivers/gpio/gpio-regmap.c

## Purpose
This file implements the generic regmap-backed GPIO controller core used by MFDs and bus devices whose GPIO registers are accessible through `struct regmap`. It supports data, set, clear, direction-in, direction-out, fixed-direction, custom register/mask translation, and optional IRQ-domain integration.

## Important APIs, Types, and Functions
`struct gpio_regmap` stores parent device, regmap, gpio chip, register bases, stride/packing parameters, fixed output bitmap, optional regmap-irq data, translator callback, and caller driver data. Public APIs are `gpio_regmap_register()`, `gpio_regmap_unregister()`, `devm_gpio_regmap_register()`, and `gpio_regmap_get_drvdata()`. Core callbacks are `gpio_regmap_get()`, `gpio_regmap_set()`, `gpio_regmap_set_with_clear()`, direction getters/setters, and `gpio_regmap_simple_xlate()`.

## Control Flow
Registration validates the config, allocates state, copies register addresses, configures the gpio chip, determines `ngpio`, copies fixed output masks, defaults packing/stride/translator values, and registers with gpiolib. Optional `CONFIG_REGMAP_IRQ` support can create a regmap IRQ chip and then attach either that domain or a provided IRQ domain to the gpio chip. Unregister removes optional regmap IRQ state, the gpio chip, the bitmap, and the allocation.

## State and Persistence
The core itself keeps little mutable state except the fixed-direction output bitmap and registration metadata. GPIO state lives in regmap-backed hardware/cache. When data and set registers alias, reads use `regmap_read_bypassed()` and writes use `regmap_write_bits()` to avoid polluting or depending on stale cache state from input values.

## Dependencies and Integration Points
Consumers pass `struct gpio_regmap_config` from `<linux/gpio/regmap.h>`. The driver uses gpiolib, regmap, optional regmap-irq, firmware node data, and gpiolib generic request/free helpers. `chip->can_sleep` is derived from `regmap_might_sleep()`.

## Risks
Configuration validation is strict but caller-supplied register bases and translator callbacks determine correctness. `GPIO_REGMAP_ADDR_ZERO` must be used for a real zero register address because zero otherwise means absent. Direction support requires both data and set registers. Regmap cache semantics are subtle when input and output registers alias.

## Test Signals
Test input-only, output-only, data+set, set+clear, direction-in-base, direction-out-base, fixed-direction-output, custom translator, zero-address sentinel use, regmap-backed IRQ domain attachment, managed unregister cleanup, and sleeping versus non-sleeping regmaps.
