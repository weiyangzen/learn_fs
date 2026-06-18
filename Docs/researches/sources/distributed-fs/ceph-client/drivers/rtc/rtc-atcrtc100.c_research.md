# sources/distributed-fs/ceph-client/drivers/rtc/rtc-atcrtc100.c

## Purpose

`rtc-atcrtc100.c` drives the Andes ATCRTC100 RTC. It exposes a day/hour/min/sec counter, hour/min/sec alarms, wake-capable alarm interrupts, and synchronization around the hardware `WRITE_DONE` status bit.

## Important APIs, types, and functions

`struct atcrtc_dev` stores RTC device, regmap, work item, alarm IRQ, and `alarm_en` software state. `atcrtc_check_write_done()` polls `RTC_STA.WRITE_DONE` before register writes. RTC callbacks are `atcrtc_read_time()`, `atcrtc_set_time()`, `atcrtc_read_alarm()`, `atcrtc_set_alarm()`, and `atcrtc_alarm_irq_enable()`. `atcrtc_alarm_isr()` handles alarm status and `atcrtc_alarm_clear()` disables alarm bits in process context.

## Control flow

Probe maps MMIO through regmap, verifies the hardware ID, gets IRQ index 1 for alarm, requests the IRQ, allocates the RTC, sets the alarm feature, enables wakeup and assigns the wake IRQ, initializes the deferred clear work, and registers. Set time converts POSIX seconds to a hardware day count plus h/m/s fields, waits for write-done before writing counter and again before enabling RTC. Set alarm disables current alarm, writes h/m/s fields, records whether the new alarm should remain enabled, and toggles alarm/wakeup bits. The ISR clears status, marks `alarm_en = false`, schedules work to clear control bits, and reports `RTC_AF`.

## State and persistence behavior

Hardware persists counter, alarm, control, status, and trim registers. Software state `alarm_en` prevents the deferred work from clearing a newly re-enabled alarm. The work item is volatile and should be flushed or naturally devres-cleaned with device removal.

## Dependencies and integration points

It depends on platform MMIO/IRQ, regmap polling, RTC class APIs, PM wake IRQ helpers, workqueues, and OF compatible `"andestech,atcrtc100"`.

## Risks and edge cases

The alarm supports only h/m/s and returns `-1` for day/month/year, relying on the RTC core to complete missing fields. The status test in the ISR checks `ALARM_INT`, a control-bit name reused as status bit, which should be checked against the hardware manual. Probe calls both `dev_pm_set_wake_irq()` and manual suspend/resume `enable_irq_wake()`/`disable_irq_wake()`, which can be redundant. Workqueue clearing races are mitigated by `alarm_en` but still need stress testing.

## Test signals

Test hardware ID rejection, write-done timeout handling, disabled RTC read returning `-EIO`, set/read time across large day counts, alarm set/read with missing date fields, alarm ISR plus deferred control clear, wake from suspend, and rapid alarm reprogramming while clear work is pending.
