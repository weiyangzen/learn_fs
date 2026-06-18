# sources/distributed-fs/ceph-client/drivers/power/supply/max8971_charger.c

Purpose: implements an I2C charger driver for MAX8971. It registers a USB power supply with status, charge type, USB type, health, online/present, charge/input current controls, model/manufacturer, sysfs timer/top-off attributes, IRQ handling, and optional extcon-driven charger-type configuration.

Important APIs/types/functions: `struct max8971_data` stores regmap fields, extcon notifier/work, USB type, timer/top-off cached values, and presence. `max8971_get_property()`, `max8971_set_property()`, and `max8971_property_is_writeable()` implement the power-supply interface. `max8971_update_config()` unlocks protected registers and applies timer/top-off/restart settings. Attribute group `max8971_groups` exposes fast-charge timer, top-off current, and top-off timer. `max8971_extcon_evt_worker()` maps extcon charger types to current limits. `max8971_interrupt()` handles charger reset/presence IRQs.

Control flow: probe initializes regmap/regmap fields, registers the supply with attribute group, masks AICL IRQ, requests the threaded IRQ, optionally locates an extcon through the OF graph, registers an extcon notifier, and schedules initial charger-type work. IRQ handling reads/clears interrupt state, updates `present`, reapplies config after chip reset, and notifies the power supply. Extcon work sets USB type and charge/input current limits under charger-protection unlock. Resume wakes the IRQ thread to refresh state.

State and persistence: `present`, `usb_type`, and requested timer/top-off values are cached. Hardware registers hold current limits and timer/top-off configuration but may reset on plug events, so the IRQ path reapplies cached config. Extcon state is external.

Dependencies and integration: depends on I2C, regmap fields, extcon, OF graph links to a connector/charger detector, devm delayed work, PM resume hook, and power-supply core.

Risks: `fast_charge_timer_store()` subtracts 3 from an unsigned `hours`, then stores in `int`, so small inputs rely on wraparound behavior before disabling. Extcon worker returns without calling `power_supply_changed()`, so USB type/current changes may not notify. `present` is only updated by IRQ, so initial state before an interrupt may be false. Test signals include extcon states for SDP/DCP/CDP/FAST/SLOW, IRQ reconfiguration after reset, sysfs boundary values, resume-triggered state refresh, and writable current clamp behavior.
