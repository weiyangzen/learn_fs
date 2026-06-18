# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8998.c

Purpose: implements MAX8998 and LP3974 PMIC RTC support with BCD time, alarm0, optional IRQ-domain alarm delivery, and an LP3974 delay workaround.

Important APIs and types: `struct max8998_rtc_info` stores parent PMIC, RTC client, RTC device, IRQ, and `lp3974_bug_workaround`. Conversion helpers are `max8998_data_to_tm()` and `max8998_tm_to_data()`. Alarm helpers are `max8998_rtc_stop_alarm()`, `max8998_rtc_start_alarm()`, and `max8998_rtc_alarm_irq_enable()`.

Control flow: probe registers the RTC first, maps alarm0 IRQ if the parent IRQ domain exists, requests a threaded IRQ, logs chip name, and enables LP3974 workaround based on platform data. Time operations bulk-read/write eight BCD registers. Alarm setup disables alarm0, writes eight alarm registers, optionally waits for the workaround, then writes an alarm config mask (`0x77` or `0x57`) if enabled.

State and persistence: time, alarm, configuration, and status are PMIC RTC registers. Software only tracks workaround and IRQ mapping. LP3974 workaround adds 2-second sleeps after writes.

Dependencies and integration: MAX8998 MFD helpers, parent platform data, IRQ domain, RTC class, BCD helpers, and platform IDs for MAX8998/LP3974.

Risks: `max8998_tm_to_data()` writes `tm_mon` directly rather than `tm_mon + 1`, which should be validated against chip conventions. If IRQ mapping/request fails, alarm feature bits are not cleared. The LP3974 workaround makes writes extremely slow. There is no PM wake handling despite alarm IRQ support.

Test signals: MAX8998 versus LP3974 platform IDs, month/year conversion round trips, no IRQ-domain behavior, IRQ request failure, alarm config mask difference, status pending read, and write delays under workaround mode.
