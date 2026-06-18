<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c

Purpose: exposes the four TPS65086 PMIC GPO bits as output-only GPIO lines.

Important APIs, types, and functions: `struct tps65086_gpio` holds a gpiochip and parent `struct tps65086`. GPIO callbacks implement output-only get_direction, reject direction_input, set initial output in direction_output, read back with `tps65086_gpio_get()`, and write with `tps65086_gpio_set()`.

Control flow: platform probe obtains parent MFD data, allocates state, copies a four-line template chip, sets the parent to the PMIC device, and registers it. GPIO writes update bits 4..7 of `TPS65086_GPOCTRL` via regmap.

State and persistence behavior: no driver cache; all state resides in the PMIC register map. GPIO operations sleep because regmap may use I2C/SPI.

Dependencies and integration points: depends on `linux/mfd/tps65086.h`, parent MFD driver setup, platform ID `tps65086-gpio`, regmap, and gpiolib.

Risks and test signals: line offsets are translated by `BIT(4 + offset)`, so any future line count change must revisit bit mapping. Input direction is intentionally unsupported. Test register read/write errors, output initial-value setting, readback of GPOCTRL bits, parent drvdata availability, and output-only direction rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65086.c -->
