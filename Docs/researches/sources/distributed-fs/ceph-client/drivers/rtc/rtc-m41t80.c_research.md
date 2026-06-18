# sources/distributed-fs/ceph-client/drivers/rtc/rtc-m41t80.c

Purpose: supports the ST M41T80-family and Micro Crystal RV4162 I2C RTCs, including time, alarm IRQs, oscillator-failure and battery-low reporting, optional square-wave clock output, and optional legacy watchdog miscdevice support.

Important APIs and types: `struct m41t80_data` stores feature flags, I2C client, RTC device, and optional common-clock state. Feature bits describe halt, battery-low, square-wave, extra watchdog resolution, and alternate square-wave register placement. RTC callbacks include `m41t80_rtc_read_time()`, `m41t80_rtc_set_time()`, `m41t80_read_alarm()`, `m41t80_set_alarm()`, `m41t80_alarm_irq_enable()`, and `m41t80_rtc_proc()`. Optional clock methods are `m41t80_sqw_*`; optional watchdog methods are `wdt_ping()`, `wdt_disable()`, `wdt_ioctl()`, `wdt_open()`, and `wdt_release()`.

Control flow: probe validates I2C functionality, selects feature flags, allocates the RTC, optionally requests a threaded alarm IRQ, configures wakeup, clears HT and ST bits, registers watchdog and square-wave clock where enabled, and registers the RTC. Time reads reject oscillator failure, then bulk-read BCD date/time. Setting time writes BCD registers, preserves square-wave bits in the weekday register on alternate chips, and if OF was set, restarts the oscillator with a 4-second stabilization delay before clearing OF. Alarm setup clears AFE and AF, writes alarm fields while preserving SQWE, then optionally re-enables AFE.

State and persistence: date/time, flags, alarm, square-wave, and watchdog registers live in battery-backed RTC hardware. Software state tracks feature selection and optional clock rate/enable cache. The watchdog code uses static global `save_client`, `wdt_margin`, `wdt_is_open`, and `boot_flag`.

Dependencies and integration: depends on SMBus byte and I2C-block transactions, OF/I2C ID match data, RTC class, optional common clock provider, optional watchdog miscdevice and reboot notifier, wakeup-source property, and threaded IRQs.

Risks: OF and HT handling is device-specific and can delay set-time by seconds. Alarm IRQ support depends on either a physical IRQ or wakeup-source property; otherwise alarm features are cleared. The watchdog implementation is legacy, global, and only one client can be saved. Square-wave and alarm share `ALARM_MON` bits, so preserving SQWE is required to avoid side effects.

Test signals: all supported IDs and feature combinations, OF restart/clear failure, HT logging and clear, battery-low proc output, alarm IRQ flag clearing, wakeup-source without IRQ, square-wave rate selection and alternate register placement, watchdog open/ioctl/reboot notifier behavior, and I2C transfer errors.
