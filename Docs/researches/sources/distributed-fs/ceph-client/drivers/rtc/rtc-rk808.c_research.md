# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rk808.c

Purpose: implements RTC support for Rockchip RK808-series PMICs, including RK809/RK817 register variants. It provides BCD time, alarm IRQs, wakeup support, and calendar translation for the PMIC's non-Gregorian November behavior.

Important APIs/types/functions: `struct rk_rtc_compat_reg` maps register offsets per PMIC generation; `struct rk808_rtc` stores regmap, RTC, compat regs, and IRQ. `rockchip_to_gregorian()` and `gregorian_to_rockchip()` translate between the hardware calendar, where November has 31 days, and normal Gregorian time using a 2016 anchor. `rk808_rtc_readtime()` snapshots shadow registers with GET_TIME, reads time, converts BCD, and translates. `rk808_rtc_set_time()` stops the RTC, writes converted hardware date, and restarts. `rk808_rtc_setalarm()` and `rk808_alarm_irq()` program and clear alarm IRQs.

Control flow: probe chooses RK817-style registers for RK809/RK817, obtains the parent regmap, starts the RTC and selects shadowed reads, clears status bits, marks wakeup capable, allocates the RTC, obtains/request the platform IRQ, then registers the RTC. Suspend/resume only toggles IRQ wake when device wakeup is enabled.

State and persistence: time, alarm, status, interrupt enable, and control bits live in the PMIC. The driver does not store persistent state; calendar conversion is deterministic and must match firmware or other software accessing the same RTC.

Dependencies and integration: depends on the RK808 MFD parent, regmap, RTC core, platform IRQ, BCD helpers, and PM sleep wake handling.

Risks: `rk808_rtc_set_time()` mutates the caller-provided `rtc_time` by converting it in place. If bulk write fails after STOP is set, the function returns without restarting the RTC. Firmware that does not implement the same November-31 conversion will disagree with Linux. Test signals include RK808 and RK817 register maps, shadow read timing, failed write after STOP, alarm IRQ/status clear, suspend wake, conversion around November/December, and interoperability with firmware dates.
