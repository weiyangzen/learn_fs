<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c

Purpose: implements an I2C RTC class driver for Ricoh R2025S/D, R2221TL, RS5C372A/B, RV5C386, and RV5C387A chips. It exposes time, alarm, voltage-low status, oscillator trim, offset adjustment, and optional proc/sysfs diagnostics.

Important APIs/types/functions: `struct rs5c372` stores the I2C client, RTC device, chip type, bus mode, cached 17-byte register buffer, and 12/24-hour flag. Key helpers are `rs5c_get_regs()`, `rs5c_reg2hr()`, `rs5c_hr2reg()`, `rs5c_oscillator_setup()`, `rs5c372_get_trim()`, `rs5c372_read_offset()`, and `rs5c372_set_offset()`. RTC ops include `read_time`, `set_time`, `read_alarm`, `set_alarm`, `alarm_irq_enable`, voltage `ioctl`, and offset callbacks.

Control flow: probe validates I2C/SMBus capabilities, identifies the chip from I2C or OF match data, reads all registers, detects the hour mode, performs oscillator setup after power loss, registers the RTC device, and creates trim/osc sysfs files when enabled. Time reads reject stopped oscillators using variant-specific status-bit polarity, then decode BCD fields into a 2000-2099 range. Time writes bulk-write time registers and clear warning bits. Alarm programming disables alarm A, writes minute/hour/day wildcard fields, and optionally re-enables alarm IRQs.

State and persistence: hardware persists time, alarm registers, control bits, oscillator stop/voltage flags, and trim register. Driver state caches the last register read and remembers bus style and hour mode. Offset programming writes the trim register and keeps RS5C372 XSL or R2221TL DEV semantics.

Dependencies and integration points: depends on I2C/SMBus block access, RTC core, BCD helpers, OF/I2C IDs, optional proc/sysfs RTC interfaces, and userspace `RTC_VL_READ`/`RTC_VL_CLR` ioctls.

Risks and test signals: `has_irq` is never set because IRQ registration is still a revisit item, so `alarm_irq_enable()` returns `-EINVAL` even though wake alarm registers can be programmed. Register cache values can be stale for offset reads unless refreshed by another operation. Variant-specific XSTP polarity is easy to regress. Test full I2C and SMBus-only adapters, all compatibles, oscillator-loss handling, voltage-clear ioctl, 12/24-hour conversion, alarm set/read with day wildcards, offset range limits, sysfs trim/osc output, and probe failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-rs5c372.c -->
