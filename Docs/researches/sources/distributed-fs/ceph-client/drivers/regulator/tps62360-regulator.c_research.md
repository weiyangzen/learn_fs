# sources/distributed-fs/ceph-client/drivers/regulator/tps62360-regulator.c

Purpose: I2C regulator driver for TPS62360/361/362/363 processor-core buck regulators with optional GPIO-controlled VSET register selection.

Important APIs/types/functions: `struct tps62360_chip` stores regmap, descriptor, VSEL GPIOs, current VSET register, LRU table, voltage mask, and shutdown options. Core operations include custom get/set voltage selector, force-PWM set/get mode, generic linear list/map/time helpers, and `tps62360_shutdown` for output discharge. `find_voltage_set_register` implements the four-entry VSET LRU cache.

Control flow: probe identifies the chip from OF or I2C ID, parses platform/OF settings, configures voltage range/mask by chip variant, initializes regmap, obtains optional `vsel0` and `vsel1` GPIOs, initializes VSET LRU state, programs control/ramp defaults, derives ramp delay from `REG_RAMPCTRL`, then registers one buck regulator. Voltage setting either updates the current register or reuses a cached selector and switches GPIOs to select the requested VSET slot.

State and persistence: hardware registers persist selected voltages, force-PWM bits, ramp config, and discharge setting. Driver state tracks current VSET ID and per-slot selector values; this must stay synchronized with GPIO state.

Dependencies and integration points: I2C, OF/platform data, GPIO descriptors, regmap, regulator core, and shutdown callback.

Risks: the LRU cache is only valid when both VSEL GPIOs are present; partial GPIO availability falls back to one VSET register. `tps62360_shutdown` enables output discharge only if configured. Error log in regulator registration prints `id->name`, but `id` can be null for pure OF probe.

Test signals: all chip IDs, GPIO and no-GPIO selector changes, LRU reuse, force-PWM across all VSET registers, ramp-delay derivation, and shutdown discharge behavior.
