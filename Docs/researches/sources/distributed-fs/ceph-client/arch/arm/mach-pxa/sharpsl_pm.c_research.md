# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/sharpsl_pm.c

Purpose: platform driver for Sharp Zaurus SL-C7xx/SL-Cxx00 battery, charger, APM, and suspend behavior. It turns board-specific callbacks from `struct sharpsl_charger_machinfo` into a common charger state machine, battery status reporting, offline charging during suspend, and sysfs/APM visibility.

Important APIs/types/functions: exports global `sharpsl_pm`, `sharpsl_battery_kick()`, `sharpsl_pm_led()`, battery threshold tables, and `sharpsl_pm_pxa_read_max1111()`. Internal work/timer/IRQ paths include `sharpsl_battery_thread()`, `sharpsl_charge_toggle()`, `sharpsl_ac_timer()`, `sharpsl_chrg_full_timer()`, `sharpsl_fatal_isr()`, `corgi_pxa_pm_enter()`, and `sharpsl_off_charge_battery()`.

Control flow: probe stores board callbacks, registers LED trigger, requests AC/battery GPIOs, wires IRQs, creates battery sysfs attributes, installs APM and suspend ops, then starts an AC debounce timer. Runtime alternates delayed work for battery sampling with timers/IRQs for AC and full-charge changes. Suspend enters PXA sleep, optionally schedules RTC wakeups for offline charging, and loops until board wakeup logic permits resume.

State and persistence: state is in global `sharpsl_pm`, delayed work, two timers, APM hook state, LED trigger state, and hardware RTC/PXA power registers. It persists no disk data; it mutates charger GPIOs, discharge lines, RTC alarm, and reset-source registers.

Dependencies and integration points: depends on PXA PM/RTC registers, MAX1111 ADC, GPIO IRQs, APM emulation, LED triggers, platform device data from board files such as `spitz_pm.c`, and `pxa_pm_enter()`. LCD backlight callbacks influence battery percentage thresholds.

Risks: high hardware risk because timing constants, blocking `mdelay()` loops, and GPIO polarity directly control charging. IRQ request errors are logged but do not abort probe, leaving degraded operation possible. Global mutable state is lightly serialized, so suspend/work/timer interactions are subtle. Offline charger loops can hide wakeup bugs and battery thresholds are board-calibrated constants.

Test signals: best signals are boot/probe logs, sysfs `battery_percentage`/`battery_voltage`, APM status, charger LED behavior, AC insertion/removal IRQs, full-charge IRQs, suspend/resume with AC present, and low/fatal battery wake-suspend paths. Unit testing would need mocked machinfo callbacks and jiffies/timer control.
