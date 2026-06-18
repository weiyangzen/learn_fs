<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c

Purpose: exposes five TPS65912 PMIC GPIO lines with input/output direction and value control.

Important APIs, types, and functions: `struct tps65912_gpio` stores gpiochip and parent PMIC pointer. GPIO callbacks are get_direction, direction_input, direction_output, get, and set. The template chip is five lines, dynamic base, sleeping.

Control flow: platform probe gets parent MFD data, allocates state, copies the template, points the chip parent at the PMIC device, and registers it. Direction_output writes the initial `GPIO_SET_MASK` value before setting `GPIO_CFG_MASK`; direction_input clears the config bit. Get reads `GPIO_STS_MASK`; set updates `GPIO_SET_MASK`.

State and persistence behavior: line state is fully in PMIC registers, with no software cache.

Dependencies and integration points: depends on `linux/mfd/tps65912.h`, parent regmap, platform ID `tps65912-gpio`, and gpiolib.

Risks and test signals: operations assume offset maps directly to `TPS65912_GPIO1 + offset`; line count must match hardware. Test direction read/write, initial output level ordering, get/set regmap failures, parent drvdata availability, and all five offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65912.c -->
