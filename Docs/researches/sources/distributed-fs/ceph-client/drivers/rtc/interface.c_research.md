# sources/distributed-fs/ceph-client/drivers/rtc/interface.c

## Purpose

`interface.c` is the shared RTC class interface layer. It exports the common kernel-facing helpers for reading and setting time, reading and programming alarms, enabling update/alarm/periodic interrupts, delivering legacy `/dev/rtc` events, maintaining the RTC timerqueue, opening RTC class devices by name, and reading or setting clock offset. Low-level RTC drivers supply `struct rtc_class_ops`; this file serializes those callbacks, normalizes time/alarm semantics, and emulates behavior when hardware is limited.

## Important APIs, types, and functions

The exported API surface includes `rtc_read_time()`, `rtc_set_time()`, `__rtc_read_alarm()`, `rtc_read_alarm()`, `rtc_set_alarm()`, `rtc_initialize_alarm()`, `rtc_alarm_irq_enable()`, `rtc_update_irq_enable()`, `rtc_update_irq()`, `rtc_class_open()`, `rtc_class_close()`, `rtc_irq_set_state()`, `rtc_irq_set_freq()`, `rtc_timer_init()`, `rtc_timer_start()`, `rtc_timer_cancel()`, `rtc_read_offset()`, and `rtc_set_offset()`. Internal helpers `rtc_add_offset()` and `rtc_subtract_offset()` expand devices with limited hardware ranges using `rtc->offset_secs`, `start_secs`, `range_min`, and `range_max`. `rtc_timer_enqueue()`, `rtc_timer_remove()`, and `rtc_timer_do_work()` implement the timerqueue that backs alarms and update interrupts.

## Control flow

Read paths lock `rtc->ops_lock`, call the driver's operation, apply range/offset conversion, validate with `rtc_valid_tm()`, and emit tracepoints. Set paths validate user time, verify the configured range, subtract any hardware offset, temporarily disable update interrupt emulation if needed, call the low-level `set_time`, then schedule `irqwork` because changing time can expire queued timers. Alarm programming stores a normalized `aie_timer` deadline, optionally rounded down for minute-resolution hardware, and uses `rtc_timer_enqueue()` to program the earliest hardware alarm. Interrupt delivery is two stage: low-level drivers call `rtc_update_irq()`, which keeps the parent awake and schedules `irqwork`; `rtc_timer_do_work()` then expires due timers, calls timer callbacks such as `rtc_aie_update_irq()` or `rtc_uie_update_irq()`, and reprograms the next alarm.

## State and persistence behavior

The file maintains no global persistence, but it mutates `struct rtc_device` state: `ops_lock`, `timerqueue`, `aie_timer`, `uie_rtctimer`, `pie_timer`, `irq_data`, `irq_freq`, `pie_enabled`, `offset_secs`, and wakeup references. Hardware persistence remains in the low-level driver; this layer only translates between expanded class time and device range. The timerqueue is volatile kernel state and must be rebuilt or initialized at registration.

## Dependencies and integration points

It depends on `linux/rtc.h`, scheduler/module/workqueue infrastructure, hrtimers, timerqueue support, PM wakeup helpers, fasync/wait queues, tracepoints from `trace/events/rtc.h`, and optional `CONFIG_RTC_INTF_DEV_UIE_EMUL`. Low-level RTC drivers integrate by setting `rtc->ops`, feature bits such as `RTC_FEATURE_ALARM`, `RTC_FEATURE_UPDATE_INTERRUPT`, and `RTC_FEATURE_ALARM_RES_MINUTE`, and range fields before registration.

## Risks and edge cases

Alarm normalization is subtle. `__rtc_read_alarm()` fills missing fields from a stable before/after time sample and rolls day, month, or year forward, but unsupported wildcard forms still produce warnings or invalid alarms. `__rtc_set_alarm()` has a deliberate race check for alarms within the next second and may return `-ETIME`. Offset expansion must avoid overlapping expanded and native ranges. `rtc_update_hrtimer()` spins with `cpu_relax()` when an hrtimer callback is running, so callback locking must not deadlock. Low-level drivers that omit feature bits or callbacks will cause `-EINVAL` even if their hardware has partial support.

## Test signals

Useful tests include RTC class selftests for valid/invalid `rtc_time`, range min/max rejection, offset-expanded devices, alarms just in the past and one second in the future, minute-resolution alarms, update interrupt emulation, periodic interrupt frequency validation, driver removal with queued timers, and low-level drivers calling `rtc_update_irq()` from IRQ context. Tracepoints `rtc_read_time`, `rtc_set_time`, `rtc_read_alarm`, `rtc_set_alarm`, timer enqueue/dequeue/fire, and IRQ enable trace expected state transitions.
