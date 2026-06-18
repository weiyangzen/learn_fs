# sources/distributed-fs/ceph-client/drivers/gpio/gpio-arizona.c

## Purpose
This platform driver exposes GPIO lines on Wolfson/Cirrus Arizona class MFD audio devices. It uses the parent regmap and runtime PM to handle cached register reads and persistent GPIO lines correctly.

## Important APIs, types, and functions
`struct arizona_gpio` stores the parent `struct arizona` and `gpio_chip`. Callbacks are `arizona_gpio_direction_in()`, `arizona_gpio_get()`, `arizona_gpio_direction_out()`, and `arizona_gpio_set()`. Probe selects `ngpio` from the parent chip type and uses optional pdata `gpio_base`.

## Control flow
Probe inherits the parent fwnode, allocates state, copies the chip template, chooses 5 or 2 GPIO lines based on Arizona variant, enables runtime PM, and registers the gpiochip. Input reads first check direction; for input pins they resume the parent, drop the regcache region, physically read the GPIO control register, and autosuspend again.

## State and persistence behavior
Direction and level are stored in parent GPIO control registers. Runtime PM state is adjusted for persistent lines: switching a persistent line to input releases runtime PM, while switching from input to output may resume the device. Regcache is explicitly dropped for live input reads.

## Dependencies and integration points
The driver depends on the Arizona MFD core, regmap/regcache, runtime PM, gpiolib persistent-line support, platform data, and platform device binding `arizona-gpio`.

## Risks and edge cases
Runtime PM failure paths must put references correctly. Cached registers cannot be trusted for input levels, hence the cache drop; missing this would report stale values. Unknown parent chip variants fail probe. Direction semantics depend on `ARIZONA_GPN_DIR` polarity.

## Test signals
Test variant-specific line counts, runtime PM reference behavior on persistent lines, cache-drop live input reads, output set/direction writes, gpio_base handling, and unknown variant rejection.
