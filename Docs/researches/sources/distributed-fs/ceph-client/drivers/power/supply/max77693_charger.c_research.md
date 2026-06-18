# sources/distributed-fs/ceph-client/drivers/power/supply/max77693_charger.c

Purpose: implements the Maxim MAX77693 charger platform subdriver. It exposes charger/battery state through a battery-type power supply and configures charger timers, top-off thresholds, constant voltage, system voltage, thermal regulation, battery overcurrent, and input voltage thresholds.

Important APIs/types/functions: `struct max77693_charger` holds the parent `max77693_dev`, registered supply, and DT/default configuration. Property helpers map charger detail, battery detail, online/present, input current limit, and fast-charge current registers. Sysfs attributes `fast_charge_timer`, `top_off_threshold_current`, and `top_off_timer` provide runtime tuning. `max77693_reg_init()` unlocks protected registers and applies safe defaults/DT settings.

Control flow: probe allocates state, parses OF properties or defaults, unlocks charger protection and initializes register fields, creates the three sysfs files, then registers the power supply. Property reads query parent MFD regmap registers and convert bit fields to power-supply enums or microamp values. Sysfs stores parse decimal input, validate/range-map it, and update the relevant register fields. Remove deletes created sysfs files.

State and persistence: configuration values are stored in hardware registers and may persist until PMIC reset. Software caches only the chosen boot configuration values; live sysfs reads fetch hardware state. No IRQ handling is present in this driver, so state changes are observed by polling property reads.

Dependencies and integration: depends on the MAX77693 MFD core/private register definitions, platform bus, power-supply core, regmap, and optional OF charger-node properties.

Risks: manual sysfs file creation has staged cleanup but is more error-prone than attribute groups. Several register writes rely on rounding down user values. The field `batttery_overcurrent` is misspelled but internally consistent. Lack of `power_supply_changed()` notifications means userspace may not get immediate charger-state events. Test signals include DT default validation, sysfs boundary tests, register-unlock failure handling, power-supply property mappings for all detail states, and probe cleanup after each sysfs/register failure.
