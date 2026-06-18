
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-ds4520.c

Purpose: registers an Analog Devices DS4520 I2C I/O expander as a gpio-regmap-backed GPIO controller.

Important APIs/types/functions: the file uses `ds4520_gpio_probe()`, `ds4520_regmap_config`, and `struct gpio_regmap_config`. Register offsets are `DS4520_PULLUP0`, `DS4520_IO_CONTROL0`, and `DS4520_IO_STATUS0`.

Control flow: probe reads the device `reg` property as a base offset, initializes an 8-bit I2C regmap, points gpio-regmap data, set, and output-direction bases at the DS4520 register windows, and registers the GPIO controller through `devm_gpio_regmap_register()`.

State and persistence behavior: state is entirely in DS4520 registers and regmap internals. There is no private cache, IRQ support, PM callback, or manual locking.

Dependencies and integration points: depends on I2C core, device properties, regmap, gpio-regmap, OF match `adi,ds4520-gpio`, and I2C id `ds4520-gpio`.

Risks: correct operation depends on the `reg` property because all register bases are computed from it. The driver relies on gpio-regmap default width/stride assumptions; any DS4520 variant with different line count or register layout would need explicit config. There is no device-id verification.

Test signals: probe with and without `reg`, I2C regmap initialization failures, GPIO input status reads, output/pullup writes, direction writes, and gpio-regmap registration.
