# sources/distributed-fs/ceph-client/drivers/regulator/tps6286x-regulator.c

Purpose: Compact I2C regulator driver for TI TPS62864/866/868/869 buck converters.

Important APIs/types/functions: a single `regulator_desc` named `tps6286x` exposes SW under the `regulators` node. It uses regmap helpers for enable, disable, is-enabled, voltage selector access, and linear voltage listing. `tps6286x_set_mode`, `tps6286x_get_mode`, and `tps6286x_of_map_mode` map regulator fast mode to the FPWM bit and DT binding mode constants.

Control flow: probe initializes an 8-bit regmap with STATUS marked volatile, fills a minimal regulator config with OF node and regmap, and registers the single regulator. Runtime control is direct regmap bit manipulation in `CONTROL` for SW enable and FPWM, and selector updates in `VOUT1`.

State and persistence: no private state; hardware registers and regmap cache hold enable, mode, and voltage. STATUS is volatile and therefore not cached.

Dependencies and integration points: I2C, OF match table, dt-bindings for TPS62864 modes, regmap, and regulator framework.

Risks: `get_mode` returns 0 on regmap read failure, which is not a normal regulator mode and can hide bus errors from consumers. The descriptor is shared across all compatibles and assumes identical voltage range and control layout.

Test signals: probe for each compatible string, DT mode mapping, enable/disable bit state, voltage selector min/max, FPWM toggling, and simulated regmap read failure for mode reporting.
