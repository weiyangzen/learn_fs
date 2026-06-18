# sources/distributed-fs/ceph-client/drivers/rtc/rtc-abx80x.c

## Purpose

`rtc-abx80x.c` supports the Abracon AB08xx/AB18xx/RV1805 I2C RTC family. Beyond basic RTC time and alarms, it exposes oscillator/autocalibration sysfs controls, voltage-low ioctl support, optional trickle charger, optional watchdog, and 256 bytes of battery-backed NVMEM SRAM.

## Important APIs, types, and functions

`enum abx80x_chip`, `struct abx80x_cap`, and `abx80x_caps[]` describe supported parts and capabilities. `struct abx80x_priv` stores the RTC device, I2C client, and watchdog. RTC callbacks include `abx80x_rtc_read_time()`, `abx80x_rtc_set_time()`, `abx80x_read_alarm()`, `abx80x_set_alarm()`, `abx80x_alarm_irq_enable()`, and `abx80x_ioctl()`. Extra surfaces include `autocalibration` and `oscillator` sysfs attributes, `abx80x_setup_watchdog()`, and NVMEM callbacks through `abx80x_nvmem_xfer()`.

## Control flow

Probe reads the part ID block, enables 24-hour/write mode, applies RV1805-specific reserved-bit and leakage workarounds, autodetects generic ABX80X devices, optionally configures trickle charging, configures countdown timer control, allocates RTC state, registers watchdog and NVMEM if supported, requests a threaded IRQ if available, clears alarm feature if not, adds the calibration sysfs group, and registers the RTC. Read time checks oscillator failure when in XT mode, bulk-reads time registers, and converts BCD values. Set time writes BCD registers and clears oscillator failure. IRQ handling reports alarm and watchdog status and clears the status register.

## State and persistence behavior

Hardware persists calendar registers, alarm registers, status flags, oscillator configuration, trickle charging, watchdog setting, and SRAM. Software state is per-device plus watchdog registration. NVMEM reads and writes page through the EXTRAM address selector and SRAM window, so address selector state changes during access.

## Dependencies and integration points

The driver uses I2C SMBus block transfers, BCD and bitfield helpers, OF/I2C match data, RTC, watchdog, sysfs attribute groups, `devm_rtc_nvmem_register()`, and `RTC_VL_READ`/`RTC_VL_CLR` ioctls. Firmware properties `abracon,tc-diode` and `abracon,tc-resistor` configure trickle charging.

## Risks and edge cases

Alarm disable via `set_alarm()` only writes IRQ enable when enabling; callers rely on `alarm_irq_enable()` for later disable. NVMEM transfer uses `void *` pointer arithmetic, a GNU C extension. `RTC_VL_CLR` writes zero to the whole status register, clearing more than BLF. Oscillator failure is ignored in RC mode. Part mismatch detection is strict and can reject compatibles if IDs differ. Configuration-key sequences must be correct or oscillator/trickle writes fail.

## Test signals

Test each matched part ID, ABX80X autodetection, XT oscillator failure rejection and clearing, alarm IRQ with and without client IRQ, voltage-low ioctls, sysfs oscillator/autocalibration values, trickle charger DT validation, watchdog start/ping/stop/timeouts, and NVMEM reads/writes crossing 64-byte windows and SMBus block limits.
