# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ac100.c

## Purpose

`rtc-ac100.c` drives the RTC block in the X-Powers AC100 MFD and also registers three RTC-related clock outputs. It supports BCD timekeeping, full-date alarms, an alarm IRQ, and clock provider integration for the AC100 clock output pins.

## Important APIs, types, and functions

`struct ac100_rtc_dev` stores the RTC, regmap, IRQ, fixed 32 kHz clock, three `struct ac100_clkout` instances, and onecell clock data. Clock operations implement prepare/unprepare, parent selection, rate calculation, rate selection, and rate programming. RTC operations include `ac100_rtc_get_time()`, `ac100_rtc_set_time()`, `ac100_rtc_get_alarm()`, `ac100_rtc_set_alarm()`, and `ac100_rtc_alarm_irq_enable()`. `ac100_rtc_register_clks()` and `ac100_rtc_unregister_clks()` manage the clock provider.

## Control flow

Probe gets the parent AC100 regmap and IRQ, allocates the RTC, requests a shared threaded alarm IRQ, forces 24-hour mode, disables and clears pending alarm interrupts, registers the fixed 32 kHz clock and three output clocks, and finally registers the RTC. Time set validates the 1970-2069 range, writes seven BCD fields plus an update trigger, and sets the leap-year bit when applicable. Alarm set validates the same range, writes enabled match bits for sec/min/hour/day/month/year while disabling weekday matching, triggers update, and toggles interrupt enable. IRQ handling locks the RTC, reads status, reports `RTC_AF`, clears status, and disables alarm interrupts.

## State and persistence behavior

Hardware persists calendar, alarm, interrupt state, RTC control, and clock output control registers. Software state tracks registered clocks and the RTC device. Clock provider registration persists until remove, where the provider and fixed clock are unregistered.

## Dependencies and integration points

The driver depends on the AC100 MFD, regmap, RTC class, common clock framework, OF clock provider APIs, BCD helpers, and platform IRQs. It consumes the codec-side parent clock name from device tree and allows `clock-output-names` overrides.

## Risks and edge cases

`ac100_clkout_set_rate()` computes `(pre_div - 1)` even when pre-divider value is zero, which should be checked against expected divider encoding. The clock registration path unregisters the fixed clock on later failures but a missing second parent returns before that cleanup path, so fixed-clock cleanup should be reviewed. RTC range is limited to 2069. The IRQ handler returns handled even if no alarm bit was set. Weekday alarm matching is intentionally disabled.

## Test signals

Test time/alarm round trips for 1970, leap years, and 2069, alarm IRQ clearing and auto-disable, clock output parent/rate/enable operations for all three outputs, missing codec parent clock behavior, remove cleanup of clock provider, and regmap write ordering for update trigger bits.
