# sources/distributed-fs/ceph-client/drivers/power/supply/da9030_battery.c

Purpose: controls the Dialog DA9030 PMIC battery charger and exposes a battery power supply using PMIC ADC results, platform battery metadata, thresholds, PMIC notifier events, and optional debugfs diagnostics.

Important APIs/types/functions: `struct da9030_charger` stores PMIC master device, ADC snapshot, delayed monitor work, platform battery info, charge thresholds, charge setpoints, notifier, callbacks, and debugfs handle. `da9030_charger_check_state()` enforces charge enable/disable policy. `da9030_battery_get_property()` reports model/status/health/technology/design voltage/current/voltage. `da9030_battery_event()` handles PMIC events.

Control flow: probe validates platform data and charge setpoints, converts thresholds to register units, initializes PMIC ADC/threshold registers, starts periodic monitor work, registers a DA903x notifier for charger detect, VBAT monitor, charge over-current, and temperature events, registers the power supply, and creates debugfs. The monitor updates PMIC state, starts charging when a charger is present and VBAT is below the start threshold, stops charging on removal/full/voltage/temperature faults, and updates VBAT thresholds for restart/low handling.

State and persistence: runtime state tracks ADC readings, fault bits, charger detect, and whether charging is enabled. Threshold and ADC control writes program PMIC registers; no driver-owned persistent storage exists. Platform callbacks may trigger board-specific low/critical responses.

Dependencies and integration: depends on DA903x MFD register access/notifiers, platform data `da9030_battery_info`, Linux power-supply core, delayed work, and optional debugfs.

Risks and test signals: this snapshot duplicates `POWER_SUPPLY_PROP_VOLTAGE_MIN_DESIGN` in the property list and debugfs labels use some mismatched conversion helpers. Tests should cover platform-data rejection, notifier registration failures, charger plug/unplug events, thermal/voltage fault shutdown, monitor rescheduling, low/critical callbacks, debugfs reads, and remove-time charger disable.
