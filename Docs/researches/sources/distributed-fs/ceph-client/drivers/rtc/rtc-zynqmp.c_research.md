## sources/distributed-fs/ceph-client/drivers/rtc/rtc-zynqmp.c

Purpose: Implements RTC support for Xilinx Zynq UltraScale+ MPSoC. It handles seconds timekeeping, alarms, second/alarm interrupts, battery switch enable, and RTC offset calibration with fractional ticks.

Important APIs/types/functions: `struct xlnx_rtc_dev` stores RTC device, MMIO base, alarm/sec IRQs, optional clock, and calibration frequency. RTC callbacks are `xlnx_rtc_set_time`, `xlnx_rtc_read_time`, `xlnx_rtc_read_alarm`, `xlnx_rtc_set_alarm`, `xlnx_rtc_alarm_irq_enable`, `xlnx_rtc_read_offset`, and `xlnx_rtc_set_offset`. Probe and PM are `xlnx_rtc_probe`, `xlnx_rtc_suspend`, and `xlnx_rtc_resume`.

Control flow: Probe allocates RTC state, maps registers, clears stale alarm interrupt status, detects whether an alarm from previous boot is still in the future, requests named alarm and second IRQs, derives calibration frequency from optional clock or DT `calibration`, initializes calibration if empty, enables battery backup in `RTC_CTRL`, re-enables a valid retained alarm, marks wake-capable, and registers. Set-time writes time+1 to `RTC_SET_TM_WR` and clears the seconds status bit. Read-time checks whether a second tick has occurred; before it has, it reads `RTC_SET_TM_RD - 1`, otherwise `RTC_CUR_TM`. Alarm enabling clears stale alarm status in a bounded loop before enabling. Interrupt handling disables alarm interrupts after any asserted interrupt and reports AF for alarm status.

State and persistence: Hardware retains current time, set-time shadow, alarm, interrupt status/mask, calibration, and battery-enable state. Driver stores calibration frequency and IRQ IDs. Offset is represented as ppb by comparing programmed ticks to `freq` and optional fractional tick fields.

Dependencies/integration: Uses platform MMIO, named IRQ resources, OF compatible `"xlnx,zynqmp-rtc"`, common clock framework, RTC core offset API, PM wake APIs, and DT calibration fallback.

Risks: Resume unconditionally enables alarm IRQ for non-wakeup devices, even if no alarm was active before suspend. Fractional offset math truncates toward integer fractional ticks and must preserve negative offset adjustment. Alarm enable can time out clearing a sticky status bit.

Test signals: Immediate read after set_time, normal read after one tick, alarm IRQ one-shot behavior, stale pending alarm cleanup, retained alarm re-enable after boot, offset conversion positive/negative/fractional cases, invalid calibration >16-bit, and suspend/resume wake and non-wake modes.
