# sources/distributed-fs/ceph-client/drivers/power/supply/cw2015_battery.c

Purpose: implements an I2C/regmap fuel-gauge driver for CellWise CW2013/CW2015 chips, exposing a `cw2015-battery` supply with capacity, voltage, status, time-to-empty, charge counters, and derived current.

Important APIs/types/functions: `struct cw_battery` stores regmap, workqueue, power supply, optional battery profile, cached readings, counters, poll interval, and alert level. `cw_init()` wakes/configures the gauge, uploads profile data when needed, and checks flash contents. `cw_get_soc()`, `cw_get_voltage()`, and `cw_get_time_to_empty()` read gauge registers. `cw_bat_work()` is the periodic polling path.

Control flow: probe parses `cellwise,battery-profile` and `cellwise,monitor-interval-ms`, initializes regmap, calls `cw_init()`, registers the power supply, retrieves optional battery info, creates an ordered workqueue, and schedules polling. The worker wakes/reset-recovers the gauge if sleeping, updates SoC/voltage/supply status/time-to-empty, notifies on changed values, and reschedules. Suspend cancels polling; resume schedules an immediate refresh.

State and persistence: battery profile and alert threshold can be written into gauge flash/config; runtime readings and stuck/error counters live in memory. The driver derives status from `power_supply_am_i_supplied()`, uses hysteresis to suppress charge/discharge spikes, resets after invalid SoC for 40 seconds, and resets if SoC is stuck while charging for 30 minutes.

Dependencies and integration: depends on I2C regmap, firmware properties, power-supply battery-info metadata, workqueues, and external charger supplies for `am_i_supplied`.

Risks and test signals: the source has suspicious config update code using `reg_val |= ~CW2015_ATHD(...)`, which can set unrelated bits, and duplicated log output in the worker. Test profile upload/replacement, no-profile behavior, invalid SoC reset, stuck-charge reset, voltage scaling, time-to-empty validity, suspend/resume, and missing battery-info fallbacks.
