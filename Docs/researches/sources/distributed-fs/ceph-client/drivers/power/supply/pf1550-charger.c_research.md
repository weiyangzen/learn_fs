
# sources/distributed-fs/ceph-client/drivers/power/supply/pf1550-charger.c

## Purpose
The PF1550 charger driver registers separate mains charger and battery power supplies for NXP/Freescale PF1550 PMIC charger hardware. It exposes online, battery status, charge type, health, presence, model, and manufacturer while configuring safe charger defaults from DT and monitored-battery data.

## Important APIs, Types, and Functions
`struct pf1550_charger` owns the parent PF1550 data, two power-supply handles, delayed work items for VBUS/charger/battery sense events, IRQ numbers, and configured voltage/current/thermal limits. Key helpers are `pf1550_get_charger_state()`, `pf1550_get_charge_type()`, `pf1550_get_battery_health()`, `pf1550_get_present()`, `pf1550_get_online()`, the three delayed work handlers, `pf1550_charger_irq_handler()`, `pf1550_charger_get_property()`, `pf1550_dt_parse_dev_info()`, `pf1550_reg_init()`, and `pf1550_charger_probe()`.

## Control Flow
Probe obtains parent MFD data/regmap, creates autocancel delayed work items, registers `pf1550-charger` and `pf1550-battery`, requests five platform IRQs, parses DT/default battery info, then initializes registers. IRQs are classified by stored virtual IRQ array and either log immediate conditions or schedule delayed sensing. Sensing work reads status registers, logs decoded charger/battery/VBUS events, and calls `power_supply_changed()` on VBUS attach/detach paths.

## State and Persistence
Runtime state is in the PF1550 registers and the `pf1550_charger` configuration fields. DT properties `nxp,min-system-microvolt` and `nxp,thermal-regulation-celsius`, plus `monitored-battery` constant charge voltage, are applied at probe. No userspace write path is provided.

## Dependencies and Integration Points
The driver depends on the PF1550 MFD header/regmap definitions, platform IRQ ordering, `power_supply_get_battery_info()`, and `devm_delayed_work_autocancel()`. It uses common sysfs/power_supply formatting for two descriptors and relies on the core for property visibility and uevents.

## Risks and Test Signals
Risk areas include exact PF1550 status-code mapping, delayed-work notification asymmetry, validation of supported voltage/thermal settings, and `power_supply_get_battery_info()` handling: `pf1550_reg_init()` turns charging on when battery info lookup fails, which should be checked against platform expectations. Tests should cover DT bounds, monitored battery data, IRQ scheduling, register write errors, status/health/presence sysfs values, and VBUS uevents.
