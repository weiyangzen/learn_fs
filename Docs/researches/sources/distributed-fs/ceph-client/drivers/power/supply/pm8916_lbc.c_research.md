
# sources/distributed-fs/ceph-client/drivers/power/supply/pm8916_lbc.c

## Purpose
The PM8916 LBC driver controls the Qualcomm linear battery charger and exposes it as a USB power supply. It configures charger-safe voltage/current limits, reports USB online state and programmed charge limits, allows runtime charge current writes, and mirrors USB VBUS state through extcon.

## Important APIs, Types, and Functions
`struct pm8916_lbc_charger` stores extcon, charger power supply, battery info, regmap, four peripheral base registers, online state, and charge limit fields. Core functions are `pm8916_lbc_charger_probe()`, `pm8916_lbc_charger_probe_dt()`, `pm8916_lbc_charger_configure()`, `pm8916_lbc_charger_get_property()`, `pm8916_lbc_charger_set_property()`, and `pm8916_lbc_charger_state_changed_irq()`.

## Control Flow
Probe reads four `reg` entries, validates CHGR/BAT_IF/USB/MISC peripheral types, checks charger option, parses safe voltage/current DT values and writes safe registers, registers the power supply, loads battery info, allocates/registers extcon, requests `usb_vbus` IRQ, reads initial VBUS state, and configures charger max voltage/current from battery info and safe limits. IRQ reads USB real-time status, updates `online`, syncs extcon `EXTCON_USB`, and emits `power_supply_changed()`. The only writable property is constant charge current.

## State and Persistence
Online state and configured limits are cached in memory and reflected in PMIC registers. DT properties `qcom,fast-charge-safe-voltage` and `qcom,fast-charge-safe-current` define upper bounds; monitored-battery voltage sets the requested maximum. State is not persisted beyond PMIC/register lifetime.

## Dependencies and Integration Points
Dependencies include parent regmap, extcon provider, named IRQ `usb_vbus`, DT `reg` array of four peripheral bases, safe charge DT properties, monitored battery data, and the power_supply class. Extcon creates a secondary integration path for USB cable state.

## Risks and Test Signals
Risk areas include register type/order assumptions, clamping math for current/voltage, ignoring `dev_err_probe()` return when an external charger is detected, and proceeding after DT parse errors because probe logs but does not return on `pm8916_lbc_charger_probe_dt()` failure. Tests should cover type mismatch, invalid DT bounds, current write clamping, extcon/online updates, initial VBUS read, and register write failures.
