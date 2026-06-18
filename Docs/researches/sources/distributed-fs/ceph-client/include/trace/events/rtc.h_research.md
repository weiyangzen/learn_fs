# sources/distributed-fs/ceph-client/include/trace/events/rtc.h

Purpose: Defines RTC tracepoints for time/alarm read and set, IRQ frequency/state, alarm IRQ enablement, offset read/set, and RTC timer enqueue/dequeue/fire.

Important APIs/types/functions: `rtc_time_alarm_class` backs `rtc_set_time`, `rtc_read_time`, `rtc_set_alarm`, and `rtc_read_alarm`. Standalone events include `rtc_irq_set_freq`, `rtc_irq_set_state`, and `rtc_alarm_irq_enable`. `rtc_offset_class` backs `rtc_set_offset` and `rtc_read_offset`. `rtc_timer_class` backs `rtc_timer_enqueue`, `rtc_timer_dequeue`, and `rtc_timer_fired`.

Control flow: RTC core/drivers emit events when userspace or kernel callers read/set time or alarms, configure periodic IRQs, enable alarms, adjust offset calibration, or manipulate RTC timers.

State and persistence: No state is owned. It observes RTC time/alarm/timer state; actual persistence is in RTC hardware and driver-managed timers.

Dependencies and integration points: Depends on `linux/rtc.h` and tracepoints. It integrates with RTC class devices, alarmtimer, suspend wake alarms, and userspace `/dev/rtc`/sysfs operations.

Risks and test signals: Risks include time normalization errors, timezone/UTC confusion outside RTC core, alarm enable races, offset unit mistakes, and timer lifetime issues. Test read/set time, alarm wake from suspend, periodic IRQs, offset calibration, timer enqueue/dequeue/fire, invalid times, and RTC device removal.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/rtc.h` completely for this pass (206 lines, 3354 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/rtc.h_research.md`.
