# sources/distributed-fs/ceph-client/drivers/rtc/rtc-isl1208.c

Purpose: supports the ISL1208 family, including ISL1208/1209/1218/1219 and RAA215300 A0 variants. It provides RTC time, alarms, proc/sysfs trim and user data, small nvmem, tamper/event detection, timestamp reporting for ISL1219, and oscillator input selection.

Important APIs/types/functions: `struct isl1208_config` describes per-chip nvmem length, tamper, timestamp, and inverted oscillator bit quirks. `struct isl1208_state` stores RTC, config, and nvmem config. Low-level helpers `isl1208_i2c_read_regs()`/`isl1208_i2c_set_regs()` wrap SMBus block transfers. RTC operations call `isl1208_i2c_read_time()`, `isl1208_i2c_set_time()`, `isl1208_i2c_read_alarm()`, and `isl1208_i2c_set_alarm()`. `isl1208_rtc_interrupt()` handles alarm and tamper events. Sysfs exposes `atrim`, `dtrim`, `usr`, and optional `timestamp0`.

Control flow: probe validates reserved bits, selects config from match data, detects optional `xin`/`clkin` clocks and oscillator bit polarity, allocates RTC, reads status, configures oscillator, warns on power failure, enables tamper detection if supported, adds timestamp and trim/user sysfs groups, requests alarm and optional event IRQs, registers nvmem, and registers the RTC. Alarm IRQ handling works around delayed/NAK-prone status reads, reports alarm events, disables and clears ALM, and notifies timestamp sysfs on tamper.

State and persistence: time, alarm, trim registers, user bytes, tamper status, and timestamp registers are chip state. Runtime config selects feature exposure and nvmem size.

Dependencies and integration: depends on I2C/SMBus, RTC, nvmem, OF IRQ lookup, optional clocks, sysfs, procfs, and device/OF match data.

Risks and test signals: interrupt handler return paths can return negative I2C errors as `irqreturn_t` values in some failure cases. IRQ wake is enabled without a matching explicit disable path. Test each chip config, oscillator input selection including inverted bit, RTCF warning, alarm delayed-clear behavior, tamper/timestamp sysfs notification, nvmem sizes, trim decoding, and reserved-bit validation.
