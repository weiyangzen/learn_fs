# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1511.c

Purpose: implements a platform RTC driver for the Dallas DS1511 timekeeper, including calendar access, alarm interrupts, and the chip's battery-backed RAM as an nvmem provider. It also performs limited watchdog cleanup by zeroing the watchdog counters during probe, but does not expose a full watchdog device.

Important APIs/types/functions: `struct ds1511_data` stores the RTC, mapped I/O base, IRQ, and alarm lock. The `rtc_class_ops` methods are `ds1511_rtc_read_time()`, `ds1511_rtc_set_time()`, `ds1511_rtc_read_alarm()`, `ds1511_rtc_set_alarm()`, and `ds1511_rtc_alarm_irq_enable()`. Register helpers `rtc_read()` and `rtc_write()` use the global `ds1511_base` and `reg_spacing`. `ds1511_nvram_read()` and `ds1511_nvram_write()` expose 256 bytes of RAM through `devm_rtc_nvmem_register()`.

Control flow: probe maps the register resource, obtains an optional IRQ, enables the oscillator/update path, clears watchdog counters, checks low-battery status, allocates/registers the RTC, optionally requests a shared IRQ, and registers nvmem. Time reads and writes stop updates around BCD register access. Alarm writes program day/hour/min/sec match registers, update the timer interrupt enable bit, and clear pending flags by reading control A. The IRQ handler reads control A to clear the interrupt and reports `RTC_IRQF | RTC_AF`.

State and persistence: calendar, alarm, and NVRAM contents persist in DS1511 battery-backed hardware. Runtime-only state is limited to the platform data object, IRQ availability, locks, and global mapped base. Alarm support is cleared from RTC features when no IRQ is usable.

Dependencies and integration: depends on platform resources, MMIO byte access, RTC core, nvmem, BCD helpers, and optional IRQ delivery. `MODULE_ALIAS("platform:ds1511")` supports platform binding.

Risks and test signals: the global `ds1511_base` makes multiple instances unsafe despite per-device allocation. Time operations use the global `ds1511_lock`, while alarm operations use `ds1511->lock`; register access serialization is therefore split. Test with no IRQ, shared IRQ, low-battery flag, NVRAM reads/writes across boundaries, alarm delivery/disable, and read/write rollover while updates are disabled.
