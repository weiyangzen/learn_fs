<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/helpers.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/helpers.c

Purpose: shared helper implementation for Linux regulator drivers, especially regmap-backed regulators. It supplies exported operations for enable/disable/status, selector read/write, voltage/current/ramp mapping, bypass and discharge controls, and small consumer helpers.

Important APIs/types/functions: `regulator_is_enabled_regmap()`, `regulator_enable_regmap()`, `regulator_disable_regmap()`, `regulator_get_voltage_sel_regmap()`, `regulator_set_voltage_sel_regmap()`, pickable-range helpers, map/list-voltage helpers, current-limit helpers, `regulator_find_closest_bigger()`, and `regulator_set_ramp_delay_regmap()` are exported GPL symbols consumed by many regulator drivers.

Control flow: helper operations use descriptor fields in `struct regulator_desc` to translate framework calls into regmap reads or masked updates. Voltage mapping either iterates `list_voltage()`, uses linear descriptors, walks `linear_ranges`, or indexes voltage/current tables. Pickable range setting converts a global selector into a range selector plus local voltage selector and optionally toggles apply bits.

State and persistence: this file owns no persistent device state; it mutates hardware registers through `rdev->regmap`. Cached or policy state remains in the regulator core and device-specific drivers.

Dependencies and integration: depends on regmap, bit operations, linear range helpers, and regulator core descriptor contracts from `driver.h`. It is the common integration point for simple PMIC drivers in this subset.

Risks and test signals: descriptor masks must be nonzero and aligned because `ffs(mask)` drives shifts. `BUG_ON()` catches invalid descriptor setup in several paths. Tests should exercise table, linear, range, pickable-range, inverted-enable, apply-bit, current-limit, ramp-delay, and fixed-voltage descriptors under regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/helpers.c -->
