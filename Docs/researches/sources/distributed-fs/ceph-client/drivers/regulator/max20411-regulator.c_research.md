# sources/distributed-fs/ceph-client/drivers/regulator/max20411-regulator.c

Purpose: provides a single regulator for the MAX20411 high-efficiency step-down converter, with linear voltage selection, slew metadata, enable-time estimation, and an optional enable GPIO.

Important APIs/types/functions: `struct max20411` stores the local descriptor, regmap, and registered `regulator_dev`. `max20411_enable_time()` reads the programmed voltage selector and slew-rate register and computes microseconds from `max20411_slew_rates`. `max20411_ops` delegates voltage get/set/list to regmap helpers and exposes `.enable_time`.

Control flow: I2C probe allocates state, creates an 8-bit regmap, copies the static descriptor, obtains regulator init data from the device node, acquires an `"enable"` GPIO with `GPIOD_ASIS`, and registers the regulator.

State and persistence: the driver keeps only devm-managed probe state. Voltage and slew configuration persist in chip registers while powered. Enable GPIO lifetime is handed to the regulator core through `config.ena_gpiod`.

Dependencies and integration: uses I2C, regmap, GPIO descriptors, OF regulator init data, and regulator core. It binds through `maxim,max20411` and the `max20411` I2C ID.

Risks and test signals: probe fails if no regulator init data is parsed, which makes DT completeness mandatory. `gpiod_get()` is not devm-managed in the driver but is passed to the regulator core. Test voltage selector bounds, slew-rate-derived enable times, missing/invalid enable GPIO, and DT constraints mapping.
