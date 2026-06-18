# sources/distributed-fs/ceph-client/drivers/regulator/gpio-regulator.c

Purpose: Implements a generic GPIO-programmable regulator. It maps a set of GPIO output bit patterns to discrete voltage or current states and registers either a voltage or current regulator.

Important APIs, types, and functions: `struct gpio_regulator_data` stores descriptor, GPIO descriptor array, state table, and current GPIO bitmask state. Voltage operations are `gpio_regulator_get_value()`, `gpio_regulator_set_voltage()`, and `gpio_regulator_list_voltage()`. Current operations use `gpio_regulator_get_value()` and `gpio_regulator_set_current_limit()`. DT parsing is handled by `of_get_gpio_regulator_config()`, and registration by `gpio_regulator_probe()`.

Control flow: Probe allocates state, obtains platform data or parses DT regulator constraints, GPIO initial states, `states` value/bitmask pairs, regulator type, startup delay, and optional `vin` input supply. It acquires each programming GPIO at its configured initial level, copies the state table, chooses the voltage or current ops table, derives the initial software state from GPIO flags, gets an optional nonexclusive enable GPIO, and registers the regulator. Setting voltage searches for the lowest state value within the requested range; setting current searches for the highest state value within range. Both then write each GPIO bit and update `data->state`.

State and persistence: The driver tracks only the last programmed GPIO bitmask in `state`. Actual output state is held by GPIO lines. Enable GPIO ownership is passed to the regulator core through `cfg.ena_gpiod`, while programming GPIOs stay devm-managed by this driver.

Dependencies and integration points: It integrates with platform devices, OF regulator constraints, GPIO descriptor APIs, regulator machine/OF helpers, and compatible `regulator-gpio`. It also preserves legacy DT ABI for undocumented `enable-at-boot`.

Risks and test signals: Test missing or malformed `states`, odd-length state arrays, voltage/current selection policy, zero GPIO counts, GPIO initial state derivation, active-low GPIO descriptor behavior, optional enable GPIO ownership, unknown regulator type warning/default, and `vin-supply` mapping. Duplicate state bitmasks or nonmonotonic state values can make get/list/set behavior surprising and should be validated in board data.
