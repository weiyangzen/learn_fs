# sources/distributed-fs/ceph-client/drivers/power/supply/max77705_charger.c

Purpose: implements an I2C charger driver for MAX77705. It exposes a USB power supply with online, present, status, charge type, health, voltage/current, and writable current-limit properties, initializes charger policy from battery info, and handles CHGIN/AICL interrupts.

Important APIs/types/functions: `struct max77705_charger_data` is defined in the companion header and stores regmap fields, workqueue, battery info, and `power_supply`. `max77705_chg_get_property()`, `max77705_set_property()`, and `max77705_property_is_writeable()` implement the power-supply interface. `max77705_charger_initialize()` programs protected charger defaults. `max77705_aicl_irq()` reduces input current until AICL clears. `max77705_chgin_irq()` queues work that calls `power_supply_changed()`.

Control flow: probe allocates state, duplicates the regmap IRQ chip descriptor to attach driver data, initializes an I2C regmap at the charger register base, allocates all regmap fields, registers the power supply, installs the regmap IRQ chip, allocates an ordered workqueue and CHGIN work, initializes charger registers using `power_supply_get_battery_info()`, requests CHGIN and AICL threaded IRQs, enables charging, and registers a devm disable action. Property reads map INT_OK/detail fields and regmap fields to status/health/current/voltage values. Writable current properties clamp through `max77705_set_integer()`.

State and persistence: the driver stores battery-info pointer and current register-field handles. Hardware registers hold charger configuration. AICL IRQ handling mutates input-current limit dynamically; disable action clears charger enable on teardown.

Dependencies and integration: depends on MAX77705 private/register-field definitions, regmap IRQ, I2C, devm work helpers, battery-info data from firmware, and power-supply core.

Risks: `max77705_get_status()` returns `POWER_SUPPLY_CHARGE_TYPE_NONE` when charging is disabled, which is a status-property enum mismatch. Several `regmap_read()`/`regmap_field_read()` calls ignore errors in helper functions. AICL decrements the raw current-limit selector without checking for zero underflow. The health path may leave `*value` unchanged for the prequalification battery state. Test signals include regmap IRQ registration, AICL underflow protection, status enum correctness, missing battery-info fallback, property write clamping, CHGIN notification work, and teardown charger disable.
