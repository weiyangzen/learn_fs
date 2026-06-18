# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pcf8563.c

Purpose: implements the Philips/NXP PCF8563, Epson RTC8564, Micro Crystal RV8564, and PCA8565 I2C RTC driver with time, minute-resolution alarms, voltage-low reporting, optional clkout, and wakeup support.

Important APIs/types/functions: `struct pcf8563` stores the RTC, century polarity heuristic, regmap, and optional clkout. `pcf8563_rtc_read_time()` bulk-reads status/time registers, rejects low-voltage data, and updates `c_polarity`; `pcf8563_rtc_set_time()` writes BCD date/time and century bit using that polarity. `pcf8563_set_alarm_mode()`, `pcf8563_get_alarm_mode()`, `pcf8563_rtc_read_alarm()`, `pcf8563_rtc_set_alarm()`, `pcf8563_irq_enable()`, and `pcf8563_irq()` manage alarm enable/pending flags. `pcf8563_clkout_*()` registers a four-rate common-clock output.

Control flow: probe checks I2C functionality, initializes regmap, sets wake capability, puts the timer into low-frequency mode, clears status/interrupt flags, allocates the RTC, configures minute-resolution alarm and time range, requests a shared threaded alarm IRQ when available, enables alarm feature if IRQ or wakeup-source is present, registers the RTC, then registers clkout when common clock is enabled.

State and persistence: the chip stores BCD time, low-voltage flag, alarm registers, interrupt enables, timer control, and clkout state. The driver's only mutable policy state is `c_polarity`, inferred from the month century bit during reads and used during future writes.

Dependencies and integration: integrates with I2C, regmap, RTC class ops/ioctl, common clock, OF matching, IRQ threading, and wakeup-source. It disables update interrupts because the hardware interface does not provide the RTC core update IRQ feature.

Risks: century bit polarity is heuristic and can be wrong on boards where firmware uses the bit differently. Probe clears ST2 and timer settings unconditionally, which can disturb firmware-programmed modes. The IRQ handler re-enables alarm mode after handling AF, which preserves AIE while clearing AF but needs hardware validation. Test signals include LV invalid-time path, century rollover writes, minute-resolution alarm IRQ, clkout rate/enable operations, wakeup-source with and without IRQ, and RTC8564/PCA8565 compatible matching.
