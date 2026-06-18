# sources/distributed-fs/ceph-client/drivers/rtc/rtc-hym8563.c

Purpose: supports the Haoyu HYM8563 I2C RTC, including calendar read/write, minute-resolution alarms, optional interrupt wakeup, and optional common-clock output registration.

Important APIs/types/functions: `struct hym8563` stores the I2C client, RTC, and optional `clk_hw`. RTC methods include `hym8563_rtc_read_time()`, `hym8563_rtc_set_time()`, `hym8563_rtc_read_alarm()`, `hym8563_rtc_set_alarm()`, and `hym8563_rtc_alarm_irq_enable()`. `hym8563_init_device()` clears STOP, disables timer/alarm interrupts, and clears flags. Clock-out support is implemented through `hym8563_clkout_ops`.

Control flow: probe allocates the RTC, initializes the chip, requests a threaded low-level IRQ when present, enables wakeup if IRQ or `wakeup-source` exists, checks the validity bit, sets feature flags, optionally registers clkout, and registers the RTC. Setting time stops the clock, writes seven BCD registers, then restarts it. Alarm setup disables AIE, writes minute/hour/day/weekday alarm bytes with disable bits for wildcard fields, then restores requested enable state. IRQ clears the alarm flag under `rtc_lock()`.

State and persistence: time, alarm, validity flag, control bits, and clkout configuration persist in chip registers. Runtime state holds client/RTC/clkout wrapper.

Dependencies and integration: uses I2C SMBus block/byte operations, RTC core, common clock framework when enabled, OF matching (`haoyu,hym8563`), and PM sleep IRQ wake hooks.

Risks and test signals: century is intentionally ignored, limiting range to 2000-2099. The IRQ handler clears AF but does not call `rtc_update_irq()`, so alarm notification depends on RTC core polling/level behavior rather than explicit event reporting. Test invalid-clock reads, minute alarm semantics, wake suspend/resume, clkout rates/enable, no-IRQ feature behavior, and STOP handling on failed writes.
