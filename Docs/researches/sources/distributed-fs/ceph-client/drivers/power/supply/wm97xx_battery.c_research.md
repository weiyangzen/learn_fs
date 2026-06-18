# sources/distributed-fs/ceph-client/drivers/power/supply/wm97xx_battery.c

## Purpose
`wm97xx_battery.c` is a platform-data-driven WM97xx battery monitor. It reads optional battery voltage and temperature AUX ADC channels, tracks charge/discharge status through an optional GPIO, and exposes only properties supported by board data.

## Important APIs, Types, And Functions
Global objects include `bat_work`, `charge_gpiod`, `work_lock`, `bat_status`, dynamic `prop`, and `bat_psy`. `wm97xx_read_bat()` and `wm97xx_read_temp()` apply platform multipliers/dividers to AUX ADC readings. `wm97xx_bat_get_property()` serves supported properties. `wm97xx_bat_update()` samples the charge GPIO and emits change events. `wm97xx_chrg_irq()` and `external_power_changed` schedule work.

## Control Flow
Probe requires platform data and singleton device id `-1`, gets an optional charge GPIO, counts supported properties from platform fields, allocates the property array, initializes work, assigns a supplied or fallback battery name, registers the power supply, schedules an initial update, and requests a GPIO IRQ when present. Work updates status based on GPIO value; suspend flushes work and resume reschedules it. Remove frees the GPIO IRQ and cancels work.

## State, Persistence, And Dependencies
The driver uses file-scope singleton state, so it supports only one instance. No hardware state is written. It depends on WM97xx AUX ADC access through the parent, platform data, optional GPIO descriptor/IRQ, workqueues, and power-supply core.

## Integration Points
The platform driver name is `wm97xx-battery`; the parent must provide WM97xx core drvdata and `struct wm97xx_batt_pdata`. `use_for_apm` is enabled for legacy battery reporting.

## Risks
File-scope `bat_psy`, `charge_gpiod`, `bat_status`, and `prop` make multi-instance support impossible and can cause cross-device corruption if that assumption changes. The GPIO polarity is hard-coded as value 0 means charging. `request_irq()` is not devm-managed but remove does free it. `wm97xx_read_bat()`/`temp()` do not guard against zero divisors in platform data.

## Test Signals
Test with and without charge GPIO, all optional property combinations, ADC scaling and invalid divisors, GPIO IRQ status transitions, suspend/resume work behavior, singleton id rejection, missing platform data, and remove while work is pending.
