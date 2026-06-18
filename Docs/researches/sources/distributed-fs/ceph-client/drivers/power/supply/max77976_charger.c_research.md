# sources/distributed-fs/ceph-client/drivers/power/supply/max77976_charger.c

Purpose: implements an I2C charger driver for the Maxim MAX77976. It detects the chip ID/revision, configures charger buck mode, and registers a USB power supply with status, charge type, health, online, charge-current, input-current, model, and manufacturer properties.

Important APIs/types/functions: `struct max77976` stores the client, regmap, and regmap fields. Field definitions cover version/revision, input-good, battery/charger detail states, mode, charge current, protected-write bits, and input current. `max77976_get_property()`, `max77976_set_property()`, and `max77976_property_is_writeable()` implement power-supply behavior. `max77976_detect()` validates chip identity, and `max77976_configure()` unlocks protected fields and sets charger-buck mode.

Control flow: probe allocates state, initializes regmap and all regmap fields, reads and validates chip ID plus version/revision, writes protection and mode configuration, and registers the power supply. Property reads use regmap fields for enum mapping and integer conversions. Writable current properties clamp requested microamp values to supported ranges and write scaled selectors.

State and persistence: software state is minimal and devm-managed. Hardware mode/current settings persist until PMIC reset or another writer changes them. No IRQ, workqueue, or cached status state is maintained.

Dependencies and integration: depends on I2C, regmap fields, OF/I2C matching, and power-supply core. It is standalone rather than an MFD subdriver.

Risks: `max77976_get_integer()` clamps `regval * mult`, which reports selector zero as the minimum even if hardware selector zero could mean a lower/special value. Setters silently clamp out-of-range current requests instead of rejecting them. The driver unlocks charge protection but does not relock after configuration. It has no change notifications. Test signals include chip ID mismatch, version/revision read failures, writeability and current-bound tests, mode register verification, and property mappings across all documented charger/battery detail values.
