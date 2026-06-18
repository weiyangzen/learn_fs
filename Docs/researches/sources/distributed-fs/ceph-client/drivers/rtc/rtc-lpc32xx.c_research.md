# sources/distributed-fs/ceph-client/drivers/rtc/rtc-lpc32xx.c

Purpose: implements RTC support for LPC32xx SoCs using an up/down counter pair, match0 alarm, backup-domain initialization key, and suspend/freezer wake management.

Important APIs and functions: `struct lpc32xx_rtc` holds base, IRQ, software `alarm_enabled`, RTC device, and spinlock. RTC callbacks are `lpc32xx_rtc_read_time()`, `lpc32xx_rtc_set_time()`, `lpc32xx_rtc_read_alarm()`, `lpc32xx_rtc_set_alarm()`, and `lpc32xx_rtc_alarm_irq_enable()`. PM hooks include suspend/resume plus freeze/thaw.

Control flow: probe maps the RTC, initializes the backup domain only if the key register does not contain the load value, disables match0 otherwise, registers the RTC, then requests the IRQ if present. Setting time disables the counter, writes `UCOUNT` and the complementary `DCOUNT`, and restores control. Alarms write match0 and enable control bit when requested. The IRQ disables the alarm, moves match0 to `0xffffffff`, clears status, and reports `RTC_AF`.

State and persistence: hardware counter state can survive chip power cycles. The key register prevents reinitializing persistent domain state on later boots. Software `alarm_enabled` is needed across freeze/thaw because the hardware alarm bit is deliberately cleared.

Dependencies and integration: platform MMIO, optional platform IRQ, OF compatible `nxp,lpc3220-rtc`, RTC class APIs, spinlocks, and PM sleep callbacks.

Risks: no IRQ resource leaves alarms configurable but not wake-capable. Counter updates rely on the disable bit and lock ordering. The driver intentionally sets match0 to a far future value after an interrupt to avoid repeated firing. Freeze always disables the alarm and thaw restores only if software state says it was enabled.

Test signals: first-boot key initialization versus retained-state path, set/read epoch seconds, alarm one-shot behavior, IRQ absence, suspend wake enable/disable, hibernate freeze/thaw, and `UCOUNT/DCOUNT` consistency.
