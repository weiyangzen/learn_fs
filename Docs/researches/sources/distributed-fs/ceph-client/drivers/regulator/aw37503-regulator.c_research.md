# sources/distributed-fs/ceph-client/drivers/regulator/aw37503-regulator.c

Purpose: I2C regulator driver for the AWINIC AW37503 dual output device, exposing positive (`outp`) and negative (`outn`) 4.0 V to 6.0 V rails.

Important APIs/types/functions: `struct aw37503_regulator` stores per-output optional enable GPIO state. `aw37503_regulator_enable()`, `disable()`, and `is_enabled()` are GPIO-oriented, while voltage and active-discharge use regulator regmap helpers. `aw37503_of_parse_cb()` obtains per-regulator `enable` GPIOs from child nodes.

Control flow: probe initializes a regmap with an access table excluding holes, allocates chip state, then registers VPOS and VNEG descriptors. Each descriptor has its own voltage register and active-discharge bit in `AW37503_REG_APPS`. Enabling drives the GPIO high if present and disables hardware auto-discharge if constraints require active discharge off.

State and persistence: `ena_gpio_state` caches logical enable state when a GPIO is present; without GPIO, `is_enabled()` always reports enabled. Voltage and discharge are stored in chip registers.

Dependencies and integration: depends on I2C, regmap, regulator core, OF regulator child matching, and optional GPIO descriptors. Supply name is `vin` for both rails.

Risks and test signals: GPIO absence makes software unable to disable a rail but still report enabled. Active-discharge correction happens only on enable and depends on `rdev->constraints` being valid. Tests should cover both rails, GPIO probe defer and absent-GPIO paths, voltage selector limits, active discharge enable/disable, and regmap access-table holes.
