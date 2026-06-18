# sources/distributed-fs/ceph-client/drivers/regulator/max5970-regulator.c

Purpose: implements regulator, hwmon, and fault-notifier support for MAX5970/MAX5978 hot-swap switch controllers. Each switch is a voltage regulator with voltage/current ADC telemetry and configurable UV/OV/OCP protections.

Important APIs/types/functions: `struct max5970_regulator` carries per-switch ADC ranges, shunt resistance, cached current limit, and shared regmap. `max5970_read()` and `max5970_is_visible()` back hwmon voltage/current inputs. `max597x_set_uvp()`, `max597x_set_ovp()`, and `max597x_set_ocp()` implement regulator protection callbacks. `max597x_irq_handler()` maps latched fault registers to regulator events and error flags.

Control flow: platform probe obtains the parent MFD regmap and I2C client, determines switch count from compatible string, allocates per-switch state, decodes ADC ranges, registers regulators, optionally registers hwmon, and attaches a regulator IRQ helper if the parent I2C IRQ exists.

State and persistence: per-switch state stores shunt micro-ohms from each regulator DT node and ADC scaling sampled at probe. Hardware registers hold enable, threshold, and fault latch state; latched faults are read and cleared in the IRQ path.

Dependencies and integration: depends on the MAX5970 MFD header/regmap, OF regulator parsing, optional hwmon, and regulator IRQ helpers.

Risks and test signals: current telemetry and OCP require `shunt-resistor-micro-ohms`; missing properties fail regulator parsing. UV/OV mode depends on POR soft straps, so unsupported severity returns `-EOPNOTSUPP`. Test ADC conversion math, MAX5970 versus MAX5978 switch counts, latched fault clearing, IRQ defer behavior, and OCP out-of-range handling.
