# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ds1685.c

Purpose: provides a feature-rich platform driver for Dallas/Maxim DS1685/DS1687-family RTCs and related DS17x85 devices. It handles direct or indirect register access, BCD or binary time modes, alarm interrupts, extended wake/kickstart/RAM-clear events, battery and serial sysfs attributes, optional proc output, nvmem, and an exported poweroff helper.

Important APIs/types/functions: hardware access is abstracted through `struct ds1685_priv` callbacks `read`/`write`, selected between `ds1685_read()`/`ds1685_write()` and indirect variants. Core RTC methods are `ds1685_rtc_read_time()`, `ds1685_rtc_set_time()`, `ds1685_rtc_read_alarm()`, `ds1685_rtc_set_alarm()`, and `ds1685_rtc_alarm_irq_enable()`. `ds1685_rtc_begin_data_access()`/`ds1685_rtc_end_data_access()` manage SET and bank switching. `ds1685_nvram_read()`/`ds1685_nvram_write()` expose banked NVRAM. `ds1685_rtc_poweroff()` programs auxiliary-battery wake/kickstart behavior and asserts power-off.

Control flow: probe consumes platform data, maps register resources, initializes access mode and callbacks, normalizes oscillator/data mode/DST/24-hour settings, checks batteries, clears pending interrupts, enables kickstart, allocates the RTC, requests an optional threaded IRQ, adds sysfs attributes, registers nvmem, and finally registers the RTC. The IRQ handler reads control B/C, reports periodic/alarm/update events to the RTC core, or dispatches extended events for kickstart, wake alarm, and RAM clear. Removal disables standard and extended interrupts.

State and persistence: persistent state includes time, alarms, control registers, NVRAM, serial number, and power/wake configuration stored by the chip. Runtime state includes access callbacks, register step, BCD mode, IRQ number, and platform callbacks for poweroff/wake/RAM-clear handling.

Dependencies and integration: integrates with platform data from `<linux/rtc/ds1685.h>`, RTC core locks, MMIO, nvmem, procfs, sysfs attribute groups, threaded IRQs, and exported symbol users of `ds1685_rtc_poweroff()`.

Risks and test signals: bank switching and NVRAM burst mode are error-prone, and the bank0 NVRAM write loop appears to write non-time bank0 bytes to `NVRAM_BANK0_BASE` without adding `pos`. The IRQ handler returns `IRQ_NONE` for extended-only events because `events` remains zero. Test direct and indirect access, BCD/binary conversions, 12-to-24-hour migration, banked NVRAM reads/writes, no-IRQ feature clearing, extended interrupts, sysfs/proc output, and poweroff callback behavior.
