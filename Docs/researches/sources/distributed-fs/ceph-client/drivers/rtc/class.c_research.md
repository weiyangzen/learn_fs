# sources/distributed-fs/ceph-client/drivers/rtc/class.c

Purpose: RTC class core registration and managed device lifecycle. It allocates `struct rtc_device`, assigns IDs, initializes timers/queues/features, registers cdev/proc/sysfs-facing class devices, optionally sets system time from RTC, and handles suspend/resume time injection.

Important APIs, types, and functions: `rtc_class` is the exported class object. `rtc_device_release()` tears down timer queues, work, IDA, mutex, and memory. `devm_rtc_allocate_device()`, `__devm_rtc_register_device()`, and deprecated `devm_rtc_device_register()` are exported driver-facing APIs. `rtc_hctosys()` reads RTC and calls `do_settimeofday64()`. PM hooks `rtc_suspend()` and `rtc_resume()` track RTC/system deltas and inject sleep time. `rtc_device_get_offset()` computes range expansion offset from `start-year`.

Control flow: subsystem init registers the class and initializes char-device support. Drivers allocate a managed RTC device, set ops and ranges/features, then register it. Registration verifies ops, clears unsupported alarm feature, marks correction support, computes offset, reads existing alarm into RTC timer state, prepares the char device, adds cdev/device, adds proc entry, logs registration, optionally runs hctosys for the configured device, and installs a devm unregister action. Release removes pending timers and cancels IRQ work after device references drain.

State and persistence: runtime state includes IDA-assigned `rtcN`, feature bits, ops pointer, alarm/update/periodic timers, timerqueue, IRQ work, offset/start-year fields, and the global `rtc_hctosys_ret`. Actual time persists in RTC hardware; the class stores only kernel-side metadata. Suspend/resume stores global old RTC/system/delta snapshots for the configured hctosys device.

Dependencies and integration points: depends on RTC core interfaces from `rtc-core.h`, char device setup from `dev.c`, proc/sysfs/nvmem optional pieces, timekeeping APIs, OF aliases, device properties, PM, timerqueue, hrtimer, IDA, and devres. It is the central integration point for all chip drivers using `rtc_class_ops`.

Risks: hctosys assumes the configured device stores UTC and whole seconds; wrong devices can set system time badly. ID allocation honors OF aliases but falls back if an alias is unavailable. Offset calculation for limited-range hardware is subtle and must handle overflow/range mapping. Registration continues if char device creation fails by setting `RTC_NO_CDEV`, so tests must check degraded interface availability.

Test signals: allocate/register/unregister RTC devices, OF alias collisions, char-device failure path, alarm initialization from hardware, hctosys success/error and 32-bit range checks, start-year offset mappings, suspend/resume sleep-time injection, and feature bit exposure for alarm/correction/update interrupts.
