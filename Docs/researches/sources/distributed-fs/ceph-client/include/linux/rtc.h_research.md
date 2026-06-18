# sources/distributed-fs/ceph-client/include/linux/rtc.h

## Purpose
`rtc.h` is the generic in-kernel Real Time Clock class interface. It defines driver callbacks, RTC device state, alarm/timer helpers, timestamp limits, NVMEM/sysfs integration, and user-facing IRQ update plumbing.

## Important APIs, types, and functions
Core types are `struct rtc_class_ops`, `struct rtc_timer`, and `struct rtc_device`. Important functions include calendar helpers `rtc_month_days()`, `rtc_year_days()`, `rtc_valid_tm()`, `rtc_tm_to_time64()`, `rtc_time64_to_tm()`, `rtc_tm_to_ktime()`, `rtc_ktime_to_tm()`, inline `rtc_tm_sub()`, registration APIs `devm_rtc_device_register()`, `devm_rtc_allocate_device()`, `devm_rtc_register_device()`, time/alarm APIs `rtc_read_time()`, `rtc_set_time()`, `rtc_read_alarm()`, `rtc_set_alarm()`, `rtc_initialize_alarm()`, IRQ APIs `rtc_update_irq()`, `rtc_irq_set_state()`, `rtc_irq_set_freq()`, `rtc_update_irq_enable()`, `rtc_alarm_irq_enable()`, timer APIs `rtc_timer_init()`, `rtc_timer_start()`, `rtc_timer_cancel()`, offset APIs, inline `is_leap_year()`, and `rtc_bound_alarmtime()`.

## Control flow, state, and persistence
RTC drivers fill `rtc_class_ops`; the core serializes most callbacks with `ops_lock`. `rtc_device` owns cdev state, IRQ wait queues, async notification, timer queues for alarm/update/periodic emulation, feature bits, valid time range, alarm-offset limits, start/offset seconds, and optional UIE emulation state. Setting time uses `set_offset_nsec` to schedule bus writes close to the hardware tick. Persistent time/alarm/NVRAM state lives in the hardware; kernel state tracks registered class devices and emulated timers.

## Dependencies and integration points
It depends on device/class infrastructure, interrupts, cdev, poll, mutexes, timerqueue/hrtimer, workqueues, NVMEM provider support, sysfs groups, and UAPI RTC structs/ioctls. It integrates with `/dev/rtc*`, proc/sysfs, hctosys, alarm wakeups, nvmem cells, legacy IRQ emulation, and bus-specific RTC drivers.

## Risks and test signals
Risks include invalid calendar conversions, time-range overflow, slow-bus set-time skew, missed alarm bounds, IRQ/fasync races, UIE emulation drift, and driver callbacks sleeping or racing outside `ops_lock`. Test signals include leap-year/range tests, read/set time around century boundaries, alarm enable/disable and wakeup tests, periodic/update IRQ emulation, NVMEM registration, hctosys selection, and sysfs group coverage.
