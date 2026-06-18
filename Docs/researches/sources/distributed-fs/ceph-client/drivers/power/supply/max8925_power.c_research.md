# sources/distributed-fs/ceph-client/drivers/power/supply/max8925_power.c

Purpose: implements power-supply support for the MAX8925 PMIC. It registers separate AC, USB, and battery supplies, controls charger enable/current bits through the parent PMIC, reads battery/charger measurements through the ADC subclient, and handles PMIC charger IRQs.

Important APIs/types/functions: `struct max8925_power_info` stores parent chip, GPM/ADC I2C clients, supplies, online flags, platform configuration, and optional board `set_charger()` callback. `__set_charger()` toggles charger disable bit and board callback. `start_measure()` triggers ADC commands and reads 12-bit results. `max8925_ac_get_prop()`, `max8925_usb_get_prop()`, and `max8925_bat_get_prop()` expose supply properties. `max8925_charger_handler()` handles charger IRQs. `max8925_init_charger()` requests IRQs, samples boot state, disables charging, and programs top-off/fast-charge configuration.

Control flow: probe obtains platform/DT charger data from the parent, allocates state, registers AC/USB/battery supplies, copies platform settings, and initializes charger hardware/IRQs. IRQ handling reacts to adapter insert/remove, overvoltage, temp range, system-low, done, top-off, timer fault, and reset events, enabling/disabling charging as needed. Property reads query online flags, ADC voltage/current, and charger status register bits.

State and persistence: online flags and battery-present state are in memory and updated by IRQs/boot sampling. Charger enable, top-off threshold, and fast-charge current are hardware register state. Board-level charger callbacks may have side effects outside the PMIC.

Dependencies and integration: depends on the MAX8925 MFD core, platform data or DT child `charger` node, parent GPM/ADC I2C clients, manually requested PMIC IRQs, and power-supply core.

Risks: `REQUEST_IRQ` logs failures but does not abort, so the driver may run with partial event coverage. `max8925_deinit_charger()` frees an IRQ range regardless of which requests succeeded. ADC helper ignores write/read return values and can return stale zero-derived values. Battery current property comment says mA while power-supply convention expects microamps. Test signals include IRQ request failures, DT/platform pdata parsing, boot state detection, ADC conversion sanity, remove cleanup with partial IRQs, and charger enable/disable callback ordering.
