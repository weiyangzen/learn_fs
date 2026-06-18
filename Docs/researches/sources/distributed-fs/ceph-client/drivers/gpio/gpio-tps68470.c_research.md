<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c

Purpose: exposes seven regular TPS68470 GPIOs plus three logic outputs used by camera/power sequencing, with optional I2C daisy-chain setup.

Important APIs, types, and functions: `struct tps68470_gpio_data` stores the parent regmap and gpiochip. GPIO callbacks are get, get_direction, set, direction_output, and direction_input. `tps68470_enable_i2c_daisy_chain()` configures GPIO1 and GPIO2 as inputs when the `daisy-chain-enable` property is present. Line names identify `gpio.0`..`gpio.6`, `s_enable`, `s_idle`, and `s_resetn`.

Control flow: probe obtains the parent regmap from drvdata, fills a ten-line sleeping gpiochip, registers it, then applies optional daisy-chain mode. Regular GPIOs use `TPS68470_REG_GPDO` and per-line control registers for direction; logic outputs use `TPS68470_REG_SGPO` and are always outputs.

State and persistence behavior: no cache is used. Direction, data, and special output state live in PMIC registers.

Dependencies and integration points: depends on TPS68470 MFD register definitions, regmap, platform child creation, device properties, and gpiolib.

Risks and test signals: error messages in `tps68470_gpio_get()` always print `TPS68470_REG_SGPO` even when reading regular GPIO data. Daisy-chain setup runs after gpiochip registration, so failure leaves a registered chip with probe failure unwind. Test regular versus logic-output offsets, direction rejection for logic outputs as inputs, daisy-chain property behavior, line names, and regmap error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps68470.c -->
