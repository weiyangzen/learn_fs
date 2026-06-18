# sources/distributed-fs/ceph-client/drivers/power/supply/da9150-charger.c

Purpose: provides DA9150 charger support through two power supplies, `da9150-usb` and `da9150-battery`, reporting charger input measurements, battery charge state, charger limits, health, and OTG/VBUS transitions.

Important APIs/types/functions: `struct da9150_charger` stores DA9150 core pointer, USB/battery supplies, currently online supply, USB PHY notifier/work, and IIO channels. Measurement callbacks read `CHAN_VBUS`, `CHAN_IBUS`, `CHAN_TJUNC`, and `CHAN_VBAT`; battery callbacks decode DA9150 status and charge-control registers. IRQ handlers cover `CHG_STATUS`, `CHG_TJUNC`, `CHG_VFAULT`, and `CHG_VBUS`.

Control flow: probe gets IIO channels, registers both supplies, samples initial VBUS state to decide which supply is online, optionally registers a USB2 PHY notifier for OTG boost switching, and requests charger IRQs. IRQs notify relevant supplies and update `supply_online` on VBUS changes. USB PHY ID events schedule work that switches DA9150 buck control between OTG and charging modes.

State and persistence: `supply_online` and last USB event are volatile driver state. Charge/OTG mode writes update DA9150 PMIC registers. Remove frees IRQs, unregisters the USB notifier, and cancels OTG work.

Dependencies and integration: depends on DA9150 MFD register helpers, DA9150 register definitions, IIO channels, Linux USB PHY notifier APIs, named platform IRQs, and the power-supply core.

Risks and test signals: this source snapshot duplicates a `POWER_SUPPLY_PROP_ONLINE` case and `remove()` frees IRQs without checking negative lookups. `cancel_work_sync()` is called even when no USB PHY initialized `otg_work`, so review init assumptions. Test missing IIO channels, each IRQ path, VBUS state transitions, OTG notifier cleanup, battery present/health mappings, and unit conversion from mV/mA/milli-Celsius to power-supply units.
