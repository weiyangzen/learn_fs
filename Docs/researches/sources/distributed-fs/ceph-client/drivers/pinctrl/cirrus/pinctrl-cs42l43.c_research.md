# sources/distributed-fs/ceph-client/drivers/pinctrl/cirrus/pinctrl-cs42l43.c

Purpose: Cirrus CS42L43 combined pinctrl and GPIO driver for codec pins, GPIO function selection, shutter routing, drive strength, and input debounce.

Important APIs/types/functions: `struct cs42l43_pin` holds gpiochip, regmap, device, and shutter lock state. Static pin/group/function tables define 15 pins and GPIO/ASP/PDM/I2C/SPI groups. `cs42l43_pin_set_mux()`, GPIO callbacks, and pinconf callbacks implement muxing and config.

Control flow: probe gets the parent MFD `cs42l43`, assigns regmap and `hw_lock`, configures gpiochip callbacks, optionally uses a child `pinctrl` fwnode, enables runtime PM, registers pinctrl, then registers the gpiochip. GPIO operations resume the device, access regmap, and release runtime PM.

State and persistence: mux, drive strength, debounce, GPIO direction/value/status, and shutter configuration live in codec registers. `shutters_locked` is immutable after probe and prevents shutter register writes when hardware lock is active.

Dependencies/integration: depends on `MFD_CS42L43`, cs42l43 register definitions, regmap, runtime PM, gpiolib, pinctrl, and generic pinconf. GPIOLIB pin ranges map the first three pins to GPIOs.

Risks: `cs42l43_gpio_set()` returns immediately on regmap update failure without `pm_runtime_put()`, risking a runtime-PM reference leak on that error path. Debounce semantics are coarse: any nonzero request maps to about 85 us. Shutter muxing is denied when locked.

Test signals: probe under MFD parent, validate GPIO get/set/direction with runtime PM tracing, set every supported drive strength, test debounce 0/nonzero, verify locked shutter requests return `-EPERM`, and inspect pinctrl debugfs groups/functions.
