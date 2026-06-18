# sources/distributed-fs/ceph-client/drivers/rtc/rtc-nxp-bbnsm.c

Purpose: implements the NXP i.MX93 BBNSM RTC via a parent syscon regmap, using a 47-bit counter shifted to seconds plus a time-alarm register.

Important APIs/types/functions: `struct bbnsm_rtc` stores RTC device, syscon regmap, IRQ, and an unused clock pointer. `bbnsm_read_counter()` repeatedly reads MS and LS counter registers and converts `(msb << 17) | (lsb >> 15)` to seconds. RTC callbacks read/write time, read/write alarm, and toggle alarm IRQ/event enable. `bbnsm_rtc_irq_handler()` checks event bits, disables alarm, clears the event, and reports `RTC_AF`.

Control flow: probe allocates the RTC, resolves the parent's syscon regmap, gets IRQ 0, clears pending events, initializes wakeup and wake IRQ, requests a shared IRQ, sets range to U32 seconds, and registers. Read-time first verifies `RTC_EN` in `BBNSM_CTRL`, then reads the stable counter. Set-time disables RTC, writes seconds into the 47-bit counter split with 15 fractional bits, then re-enables. Set-alarm writes `BBNSM_TA` and delegates enable control to `bbnsm_rtc_alarm_irq_enable()`.

State and persistence: hardware persists control bits, interrupt enables, events, split RTC counter, and alarm time. Driver state has no cache. Alarm pending is read from `BBNSM_EVENTS`; enabled state is not reported by `read_alarm()`.

Dependencies and integration: depends on OF compatible `nxp,imx93-bbnsm-rtc`, parent syscon node, regmap, shared IRQ, wake IRQ helpers, and RTC class.

Risks and test signals: `bbnsm_read_counter()` initializes `time` from `tmp` and returns `time`, which can return the previous sample after timeout and ignores regmap read errors. `bbnsm_rtc_set_alarm()` comments "disable the alarm" but calls `regmap_update_bits(..., TA_EN, TA_EN)`, which appears to set the enable value with a narrow mask instead of using `TA_EN_MSK`. Most regmap operations ignore return values. Test counter stable-read timeout, disabled RTC read, set-time split encoding, alarm enable/disable bit masks, event clear write, regmap failure propagation gaps, wake IRQ setup, and U32 rollover.
