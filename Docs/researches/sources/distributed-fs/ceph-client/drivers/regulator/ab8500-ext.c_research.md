# sources/distributed-fs/ceph-client/drivers/regulator/ab8500-ext.c

Purpose: supports AB8500 external fixed-voltage regulators, especially `VextSupply3`, through the regulator framework. It controls high-power, low-power, hardware-request, and off modes by updating AB8500 bank/register bitfields.

Important APIs and data: `ab8500_ext_regulator_info` stores descriptor data, register update location, masks, current mode value, and mode-specific values. `ab8500_ext_regulators[]` provides fixed-voltage constraints and consumer supply metadata. Regulator ops include enable, disable, is-enabled, set/get mode, set voltage validation, and fixed-voltage listing. `ab8500_ext_regulator_probe()` registers all three supplies.

Control flow: probe obtains the parent `ab8500`, applies a revision quirk for AB8500 2.x by inverting VextSupply3 LP/HP values, then iterates through all external regulator info entries. Each entry gets its device pointer, optional config from init-data driver data, regulator config, and devm registration. Enable selects HP if hardware request mode is required, otherwise the current requested mode. Disable selects hardware-request mode if configured, otherwise off. Set-mode updates hardware only when enabled and not forced by hardware request, then records the desired mode in `update_val`.

State and persistence: mode preference is held in mutable `update_val` fields in static regulator info. Hardware state persists in AB8500 registers until changed or reset. No file or firmware persistence is used.

Dependencies and integration: depends on `AB8500_CORE`, ABx500 register accessors, AB8500 revision helpers, platform driver name `ab8500-ext-regulator`, regulator constraints, and Makefile pairing with `ab8500.o` under `REGULATOR_AB8500`.

Risks: static mutation of regulator info and revision quirk is global, so multiple AB8500 instances would share modified state. `set_voltage` only accepts exact fixed constraints and does not use selectors. Hardware-request mode can make software disable mean "HW controlled" rather than off. Null constraint or info pointers return errors.

Test signals: AB8500 2.x VextSupply3 inversion, enable/disable register writes for HW-request and normal configs, mode changes while enabled/disabled, fixed-voltage list/set validation, missing parent rejection, and consumer supply linkage for SIM voltage.
