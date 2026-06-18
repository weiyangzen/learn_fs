<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c

Purpose: implements GPIO support for TPS65910/TPS65911 PMICs, including input/output mode, value access, and optional sleep-control setup from board data or Device Tree.

Important APIs, types, and functions: `struct tps65910_gpio` stores gpiochip and parent PMIC. GPIO callbacks are get, set, direction_output, and direction_input. `tps65910_parse_dt_for_gpio()` reads `ti,en-gpio-sleep` into parent board data when OF is enabled.

Control flow: subsys init registers the platform driver. Probe inherits the parent firmware node, allocates state, chooses `ngpio` based on `tps65910_chip_id()` (`TPS65910_NUM_GPIO` or `TPS65911_NUM_GPIO`), sets optional static GPIO base, parses DT board data if needed, programs `GPIO_SLEEP_MASK` for requested lines, then registers the gpiochip. Direction_output sets value before setting `GPIO_CFG_MASK`.

State and persistence behavior: no private line cache. PMIC registers hold value, status, direction, and sleep-control bits.

Dependencies and integration points: depends on TPS65910 MFD structures, regmap, platform data/OF properties, I2C client naming, and gpiolib.

Risks and test signals: `tps65910_gpio_get()` ignores the `regmap_read()` return value, so failed reads can produce stale/uninitialized results. DT parsing assumes `tps65910->of_plat_data` is available. Test chip variants, sleep property arrays, failed regmap operations, direction transitions, and platform-data versus OF base behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-tps65910.c -->
