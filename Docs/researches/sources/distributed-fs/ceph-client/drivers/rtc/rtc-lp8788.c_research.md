# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lp8788.c

Purpose: implements the TI LP8788 MFD RTC child, using parent LP8788 register helpers for time, two selectable alarms, wakeup, and optional alarm IRQ delivery.

Important APIs and functions: `struct lp8788_rtc` links the parent `struct lp8788`, RTC device, selected alarm, and mapped IRQ. Time conversion helpers are `_to_tm_wday()` and `_to_lp8788_wday()`. RTC callbacks are `lp8788_rtc_read_time()`, `lp8788_rtc_set_time()`, `lp8788_read_alarm()`, `lp8788_set_alarm()`, and `lp8788_alarm_irq_enable()`. `lp8788_alarm_irq_register()` maps the parent IRQ-domain alarm resource.

Control flow: probe obtains the parent LP8788, picks platform-data alarm selection or alarm 1, registers an RTC, and tries to map/request the alarm IRQ. Reads unlock/latch the RTC and bulk-read second through weekday registers. Setting time writes individual byte registers except weekday, which is read-only. Alarm operations use arrays to choose alarm 1 or alarm 2 base/enable/int masks.

State and persistence: time and alarm registers live inside the LP8788 PMIC. Driver state only tracks the chosen alarm and IRQ mapping. Weekday is bit-encoded in hardware; alarms store an alarm-enable bit in the weekday/en register slot.

Dependencies and integration: depends on `linux/mfd/lp8788.h`, the LP8788 IRQ domain, named platform IRQ resource `LP8788_ALM_IRQ`, parent register accessors, RTC class, and platform data for selecting alarm 1 versus alarm 2.

Risks: no alarm IRQ resource leaves timekeeping usable but `alarm_irq_enable()` returns `-EIO`. `_to_lp8788_wday()` assumes a valid nonzero `tm_wday`, while Linux weekdays are normally 0-6; zero would shift by -1. Year support is offset from 2000 and rejects pre-2000 dates only. The read path does not validate hardware fields.

Test signals: time set/read across 2000 boundary, weekday conversions, both alarm selections, missing IRQ resource, IRQ-domain mapping failures, interrupt enable register bit selection, and alarm IRQ delivery to `rtc_update_irq()`.
