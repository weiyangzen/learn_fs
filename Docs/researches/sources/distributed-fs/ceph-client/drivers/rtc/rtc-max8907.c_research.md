# sources/distributed-fs/ceph-client/drivers/rtc/rtc-max8907.c

Purpose: implements the MAX8907 PMIC RTC child with regmap time/alarm access and a regmap-IRQ alarm0 interrupt.

Important APIs and functions: `struct max8907_rtc` references the parent MFD, RTC regmap, RTC device, and IRQ. `regs_to_tm()` and `tm_to_regs()` convert BCD register arrays. `max8907_rtc_read_time()`, `max8907_rtc_set_time()`, `max8907_rtc_read_alarm()`, and `max8907_rtc_set_alarm()` are RTC callbacks. `max8907_irq_handler()` clears alarm0 control and emits `RTC_AF`.

Control flow: probe obtains the parent `struct max8907`, registers the RTC, obtains alarm0 virtual IRQ from the parent's RTC irqchip, and requests a threaded IRQ. Time operations bulk-read/write eight registers. Alarm set disables alarm0, writes target registers, and writes control `0x77` when enabled.

State and persistence: time and alarm state live in MAX8907 RTC registers. The driver does not keep software alarm state; enable is read from alarm control bits.

Dependencies and integration: MAX8907 MFD, parent `regmap_rtc`, regmap IRQ virtual IRQ lookup, RTC class, BCD helpers, and platform child binding.

Risks: the driver lacks `.alarm_irq_enable`, so alarm enable is only through `set_alarm()`. Month conversion in `tm_to_regs()` uses `tm_mon + 1`, but other fields depend on normalized input. IRQ handler disables alarm control unconditionally after firing.

Test signals: time conversion including 12-hour mode reads, alarm set/read/IRQ, virtual IRQ lookup failure, missing parent regmap, and alarm control clearing after IRQ.
