# sources/distributed-fs/ceph-client/drivers/regulator/tps6287x-regulator.c

Purpose: I2C regulator driver for TPS62870/871/872/873 PMIC buck regulators with pickable voltage ranges and programmable ramp rates.

Important APIs/types/functions: `tps6287x_reg` defines a single regulator using pickable linear ranges across four VRANGE settings, VSET as selector, CTRL2 as range selector, CTRL1 for enable/FPWM/ramp, and `range_applied_by_vsel`. `struct tps6287x_reg_data` stores an optional best range selected from init constraints. Custom functions implement best-range selection, mode mapping, and range-aware `map_voltage`.

Control flow: probe allocates `reg_data`, initializes regmap, reads OF regulator init data, chooses a best fixed range if constraints have `apply_uV` and fit in one range, registers the regulator, and stores `reg_data` on `rdev`. Voltage mapping uses the chosen range when available to avoid regulator-core picking a different range; otherwise it falls back to generic pickable range mapping.

State and persistence: persistent state is in VSET, CTRL1, and CTRL2. Driver state only records preferred range for voltage mapping. STATUS is volatile.

Dependencies and integration points: I2C, regmap, regulator core pickable linear range helpers, OF init constraints, and standard regulator mode constants.

Risks: `rdev->reg_data` is assigned after registration; callbacks during registration must not depend on it. If constraints are missing or not `apply_uV`, generic range picking may choose any valid range. `get_mode` masks read errors by returning 0.

Test signals: fixed-range and generic mapping paths, voltage mapping boundary checks, ramp-delay table programming, FPWM mode toggling, and compatibles for all four device IDs.
