# sources/distributed-fs/ceph-client/drivers/rtc/rtc-pic32.c

Purpose: implements the Microchip PIC32MZDA MMIO RTC driver with BCD time read/write, alarm interrupt support, wakeup capability, and clock gating around register access.

Important APIs/types/functions: `struct pic32_rtc_dev` holds the RTC, MMIO base, clock, alarm lock, IRQ, and alarm-clock reference state. `pic32_rtc_gettime()` and `pic32_rtc_settime()` read/write BCD byte registers. `pic32_rtc_getalarm()`, `pic32_rtc_setalarm()`, `pic32_rtc_setaie()`, and `pic32_rtc_alarmirq()` implement alarm controls. `pic32_rtc_setfreq()` configures alarm mask/chime mode, and `pic32_rtc_enable()` unlocks PIC32 syskey and enables/disables the RTC block.

Control flow: probe obtains the alarm IRQ, maps registers, gets/prepares the clock, enables the RTC block, marks wakeup capable, registers an RTC with a 2000-2099 range, configures periodic alarm frequency, requests the IRQ, and disables the clock after setup. Remove disables alarm IRQ and unprepares the clock.

State and persistence: time and alarm registers persist in RTC hardware while power is retained. Driver state tracks whether the clock must remain enabled for an armed alarm through `alarm_clk_enabled`. Alarm programming currently clears the time/date alarm registers rather than writing the requested alarm timestamp.

Dependencies and integration: depends on platform devices, OF compatible `microchip,pic32mzda-rtc`, MMIO accessors, PIC32 platform syskey helpers, common clock, RTC core, and IRQ handling.

Risks: `pic32_rtc_setalarm()` ignores `alrm->time` and writes zero to alarm time/date registers, so requested absolute alarms are not honored. It also calls `pic32_rtc_setaie()` while the clock is already enabled, causing nested enable/disable calls without prepare-count issues but with confusing lifetime. Reads only retry once when seconds equals zero, which may still race updates. Test signals include set/read time, alarm timestamp programming correctness, IRQ delivery and clock gating, probe failure cleanup, and wake from suspend on alarm.
