# subset-b-005196 research

Grouped source-tree-aligned research for subset B work item `subset-b-005196`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/interface.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/lib.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/lib.c

## Purpose

`lib.c` provides the RTC subsystem's date and time conversion utilities. It converts between POSIX `time64_t`, `ktime_t`, and `struct rtc_time`, computes month and year day counts, and validates user-visible RTC timestamps. These helpers are used by the shared RTC interface and by individual RTC drivers that expose register values as seconds.

## Important APIs, types, and functions

The exported helpers are `rtc_month_days()`, `rtc_year_days()`, `rtc_time64_to_tm()`, `rtc_valid_tm()`, `rtc_tm_to_time64()`, `rtc_tm_to_ktime()`, and `rtc_ktime_to_tm()`. `rtc_days_in_month[]` and `rtc_ydays[][]` provide static calendar tables. `rtc_time64_to_tm()` uses an arithmetic Gregorian conversion that works for large positive ranges and for times since at least 1900 by shifting to a March-based computational calendar.

## Control flow

Month and year-day helpers are direct table lookups with leap-year adjustment. `rtc_time64_to_tm()` first shifts seconds from the POSIX epoch to a non-negative day count relative to 0000-03-01, calculates century, year, month, day, weekday, and yday using integer arithmetic, then fills hour, minute, second, and `tm_isdst`. `rtc_tm_to_time64()` delegates to `mktime64()`. `rtc_ktime_to_tm()` rounds up if nanoseconds are non-zero before converting.

## State and persistence behavior

The file is stateless. It uses only constant lookup tables and caller-provided buffers. No hardware or persistent state is touched.

## Dependencies and integration points

It depends on `linux/rtc.h`, `linux/export.h`, `mktime64()`, `ktime_to_timespec64()`, `ktime_set()`, `is_leap_year()`, and integer division helpers. RTC drivers rely on these functions when converting BCD/calendar register sets to the common RTC ABI or when exposing second counters as wall-clock time.

## Risks and edge cases

`rtc_valid_tm()` rejects years before 1970 and years that overflow `INT_MAX - 1900`; callers dealing with pre-1970 hardware must set ranges and avoid validating unsupported values. `rtc_time64_to_tm()` stores `tm_yday` as `day_of_year + 1`, so consumers expecting the conventional zero-based `tm_yday` should review this behavior in context. `rtc_ktime_to_tm()` rounds nanoseconds upward, which is intentional for alarm deadlines but can surprise callers expecting truncation.

## Test signals

Test conversion round trips at leap days, century boundaries, 1970-01-01, 1999/2000, 2038-adjacent timestamps, very large future values, invalid month/day/hour/minute/second values, and ktime values with non-zero nanoseconds. Cross-check `rtc_month_days()` and `rtc_year_days()` against known leap-year tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/lib.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/nvmem.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/nvmem.c

## Purpose

`nvmem.c` is the RTC subsystem bridge for drivers that expose battery-backed RAM or EEPROM through the generic NVMEM framework. It provides one helper, `devm_rtc_nvmem_register()`, that lets an RTC driver register an NVMEM device tied to the RTC parent device and module owner.

## Important APIs, types, and functions

`devm_rtc_nvmem_register(struct rtc_device *rtc, struct nvmem_config *nvmem_config)` fills `nvmem_config->dev` with `rtc->dev.parent`, copies `rtc->owner`, enables `add_legacy_fixed_of_cells`, and calls `devm_nvmem_register()`. It returns `0`, a negative errno, or `-ENODEV` when no config is supplied.

## Control flow

The helper is linear: validate config, populate ownership and device fields, register with NVMEM, log an error if registration fails, and return `PTR_ERR_OR_ZERO()`.

## State and persistence behavior

This file does not manage storage itself. Persistence is provided by the underlying RTC hardware and the driver-supplied `reg_read` and `reg_write` callbacks in `struct nvmem_config`. Registration is devres-managed, so the NVMEM device is released with the parent.

## Dependencies and integration points

It depends on `linux/nvmem-consumer.h`, `linux/rtc.h`, `linux/err.h`, and `linux/types.h`. Drivers such as `rtc-abx80x.c` integrate by building an NVMEM config for SRAM and passing their `struct rtc_device`.

## Risks and edge cases

The helper mutates the caller's config, so drivers should not reuse the same static config across incompatible devices without care. NVMEM access semantics, locking, and bounds are entirely the responsibility of the driver's callbacks. Missing `nvmem_config` returns `-ENODEV`, which callers should treat as setup failure only if NVMEM is required.

## Test signals

Probe a driver with RTC-backed NVMEM and confirm `/sys/bus/nvmem/devices` appears, legacy fixed OF cells are available, reads and writes use the RTC parent device, module unload or device removal tears down the NVMEM device, and callback errors propagate to userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/nvmem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/proc.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/proc.c

## Purpose

`proc.c` implements the legacy `/proc/driver/rtc` view for the RTC subsystem. It exposes the selected hardware clock-to-system device's current time, date, alarm, IRQ state, frequency limits, and optional driver-specific proc output.

## Important APIs, types, and functions

`rtc_proc_add_device()` creates `driver/rtc` with `proc_create_single_data()` for the RTC selected by `CONFIG_RTC_HCTOSYS_DEVICE` or, without that option, `rtc0`. `rtc_proc_del_device()` removes it. `rtc_proc_show()` formats values with `%ptRt` and `%ptRd`, calls `rtc_read_time()` and `rtc_read_alarm()`, and invokes `ops->proc()` when present. `is_rtc_hctosys()` maps `rtc->id` to `rtcN` and compares with the configured hctosys device.

## Control flow

At RTC registration, the core can call `rtc_proc_add_device()`. If the device is the hctosys RTC, a proc entry is created. A read of `/proc/driver/rtc` calls `rtc_proc_show()`, which first prints the current RTC time/date if readable, then alarm and IRQ metadata if `rtc_read_alarm()` succeeds, then always prints `24hr: yes`, followed by any low-level driver's `proc` hook.

## State and persistence behavior

No durable state is stored here. The proc entry is a transient view over the live `struct rtc_device`. It reports in-memory class state such as `uie_rtctimer.enabled`, `pie_enabled`, `irq_freq`, and `max_user_freq`.

## Dependencies and integration points

It depends on `linux/proc_fs.h`, `linux/seq_file.h`, `linux/rtc.h`, and local `rtc-core.h`. It integrates with the RTC core registration/removal paths and with drivers that implement the optional `proc` callback, such as the AT91SAM9 RTT driver.

## Risks and edge cases

Only one global `/proc/driver/rtc` exists, so systems with multiple RTCs expose only the selected hctosys RTC. `NAME_SIZE` limits `rtcN` string construction to ten bytes; overly large IDs are ignored. Proc output may omit sections if read callbacks fail. The local `const struct rtc_class_ops *ops = rtc->ops` is dereferenced for `ops->proc`, so this path assumes a registered device with valid ops.

## Test signals

Boot with different `CONFIG_RTC_HCTOSYS_DEVICE` values and multiple RTCs, confirm only the intended RTC creates `/proc/driver/rtc`, compare time/alarm fields with `/dev/rtc` ioctls, verify optional `proc` driver output, and ensure removal unregisters the proc entry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/proc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm80x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm80x.c

## Purpose

`rtc-88pm80x.c` is the Marvell 88PM80x PMIC RTC driver. It exposes timekeeping through the RTC class using a 32-bit free-running counter plus a writable base stored in PMIC RTC registers, and supports a single alarm interrupt with wake capability.

## Important APIs, types, and functions

`struct pm80x_rtc_info` stores the parent MFD chip, regmap, RTC device, platform device, and IRQ. The `rtc_class_ops` methods are `pm80x_rtc_read_time()`, `pm80x_rtc_set_time()`, `pm80x_rtc_read_alarm()`, `pm80x_rtc_set_alarm()`, and `pm80x_rtc_alarm_irq_enable()`. `rtc_next_alarm_time()` maps hardware's time-of-day alarm style to the next occurrence within 24 hours. `rtc_update_handler()` acknowledges PMIC alarm bits and reports `RTC_AF`.

## Control flow

Probe validates platform data or device tree, gets the MFD regmap and IRQ, allocates the RTC, requests the PMIC IRQ through `pm80x_request_irq()`, sets `range_max = U32_MAX`, registers the RTC, selects the internal XO for power-down free running, and enables device wakeup. Reading time loads the writable base from `EXPIRE2_*`, reads the counter, adds them, and converts seconds to `rtc_time`. Setting time computes `base = requested - counter` and writes it back. Alarm programming disables alarm, computes current base and counter, normalizes requested time to the next daily occurrence, writes `EXPIRE1_*`, and updates alarm/clear/wakeup bits.

## State and persistence behavior

Persistent state is the PMIC counter, base registers, alarm compare registers, and `PM800_RTC_CONTROL` bits. Software state is limited to the per-device info struct and wake configuration. The base register makes wall-clock time survive as long as the PMIC backup domain and counter remain valid.

## Dependencies and integration points

The driver depends on the 88PM80x MFD core, `linux/regmap.h`, `linux/mfd/88pm80x.h`, platform data for `rtc_wakeup`, and RTC class APIs. PM suspend/resume delegates to `pm80x_dev_suspend()` and `pm80x_dev_resume()`.

## Risks and edge cases

Most `regmap_raw_read()` and write calls ignore return values, so bus errors may be reported as valid zero or stale times. Alarm setting only schedules the next occurrence of the requested hour/min/sec within 24 hours and does not preserve arbitrary date alarms. The remove path frees the PMIC IRQ manually, so probe failure paths must stay aligned with successful request points. Base plus counter arithmetic is 32-bit range-limited.

## Test signals

Test probe with and without platform data/OF node, read/set time across counter rollover boundaries, alarm enabled and disabled paths, wake from suspend, PMIC alarm and wakeup bit clearing, and failure injection for regmap operations if practical. Confirm the internal XO bit is set after registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm80x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm860x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm860x.c

## Purpose

`rtc-88pm860x.c` drives the RTC block in Marvell 88PM860x PMICs. Like the 88PM80x driver, it represents wall time as a free-running 32-bit counter plus a writable base, and it adds optional VRTC calibration using PMIC measurement hardware.

## Important APIs, types, and functions

`struct pm860x_rtc_info` holds the parent chip, selected I2C client, RTC device, delayed calibration work, IRQ, and configured VRTC target. RTC operations include `pm860x_rtc_read_time()`, `pm860x_rtc_set_time()`, `pm860x_rtc_read_alarm()`, `pm860x_rtc_set_alarm()`, and `pm860x_rtc_alarm_irq_enable()`. `calibrate_vrtc_work()` periodically samples VRTC, compares against the configured target voltage, adjusts `PM8607_RTC_MISC1`, and disables measurement when converged.

## Control flow

Probe allocates state, selects the primary or companion I2C client based on chip ID, requests the alarm IRQ, programs page address registers for the base value, reads optional `marvell,88pm860x-vrtc`, registers the RTC with `range_max = U32_MAX`, enables XO clock selection, starts VRTC measurement and delayed calibration, and enables wakeup. Read time bulk-reads the four base bytes through page registers, reads the counter, adds them, and converts to `rtc_time`. Set time writes a new base. Alarm operations convert between base-relative expiry and absolute seconds while toggling alarm enable, wakeup, and status bits.

## State and persistence behavior

Hardware persists counter, base, alarm, control, and VRTC trim state inside the PMIC. Software persists only the delayed work item and the selected `vrtc` target while the driver is loaded. Remove cancels calibration work and disables VRTC measurement.

## Dependencies and integration points

The driver uses the 88PM860x MFD helpers (`pm860x_bulk_read`, `pm860x_set_bits`, page-register access), OF parsing, platform IRQs, RTC class APIs, delayed work, and PM sleep hooks. Suspend/resume toggles a wakeup flag in the parent chip when wakeup is enabled.

## Risks and edge cases

Several PMIC access helpers are used without checking all return values. VRTC calibration is compiled in unconditionally by a local `#define`, so probe always enables measurement and delayed work. Alarm math assumes the target time is representable relative to the stored base; past alarms can underflow into a large unsigned delta. Device tree parsing failure silently defaults `vrtc` to 0, implying 2.7 V.

## Test signals

Validate time set/read, alarm set/read/IRQ, suspend wake flag behavior, remove cancellation of calibration work, OF VRTC values, and PMIC register writes for XO and measurement enable. Long-running tests should confirm calibration converges and disables measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm860x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm886.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm886.c

## Purpose

`rtc-88pm886.c` is a compact Marvell 88PM886 PMIC RTC driver. It supports only reading and setting wall-clock time using a 32-bit read-only counter plus a writable offset in spare registers.

## Important APIs, types, and functions

The RTC operations are `pm886_rtc_read_time()` and `pm886_rtc_set_time()`. Probe obtains the parent `struct pm886_chip`, stores its regmap as platform driver data, allocates an RTC device, assigns `pm886_rtc_ops`, sets `range_max = U32_MAX`, and registers it. The platform ID table matches `"88pm886-rtc"`.

## Control flow

Read time bulk-reads four bytes from `PM886_REG_RTC_SPARE1` into a `u32`, bulk-reads four bytes from `PM886_REG_RTC_CNT1`, adds the two values, and converts the result to `struct rtc_time`. Set time reads the current counter, subtracts it from the requested timestamp, and writes the resulting base offset back to the spare registers.

## State and persistence behavior

Persistent wall-clock state is the hardware counter plus spare-register base. There is no alarm, IRQ, wake, calibration, or NVMEM state in this driver. The base persists only to the extent that the PMIC spare registers are retained.

## Dependencies and integration points

It depends on the 88PM886 MFD header, regmap, platform devices, and RTC class APIs. It is integrated as an MFD child platform device rather than by direct OF matching.

## Risks and edge cases

The driver assumes regmap bulk transfers into `u32` match the PMIC register byte order and CPU representation expected by the hardware. It exposes only a 32-bit seconds range. No validity flag is checked, so backup loss or uninitialized spare registers may appear as valid time. Alarm feature bits should remain cleared by the RTC core because no alarm ops are supplied.

## Test signals

Test read/set round trips, persistence across PMIC reset states where spare registers are retained, 32-bit wrap boundary behavior, probe failure when the parent regmap is missing, and absence of alarm support in userspace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-88pm886.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-b5ze-s3.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-b5ze-s3.c

## Purpose

`rtc-ab-b5ze-s3.c` drives the Abracon AB-RTCMC-32.768kHz-B5ZE-S3 I2C RTC/alarm chip. It supports BCD calendar time, alarm interrupts, battery-low detection, oscillator-integrity checking, and a hybrid alarm implementation that uses Timer A for short second-precision alarms and normal alarm registers for longer minute-granularity alarms.

## Important APIs, types, and functions

`struct abb5zes3_rtc_data` stores the RTC device, regmap, IRQ, battery-low state, and `timer_alarm` selector. Important helpers include `abb5zes3_i2c_validate_chip()`, `_abb5zes3_rtc_read_time()`, `abb5zes3_rtc_set_time()`, `_abb5zes3_rtc_read_timer()`, `_abb5zes3_rtc_read_alarm()`, `_abb5zes3_rtc_set_timer()`, `_abb5zes3_rtc_set_alarm()`, `abb5zes3_rtc_set_alarm()`, `abb5zes3_rtc_check_setup()`, and `_abb5zes3_rtc_interrupt()`. `rtc_ops` wires read/set time, read/set alarm, and alarm IRQ enable.

## Control flow

Probe checks I2C capabilities, initializes regmap, validates fixed-zero register bits, allocates driver state, runs setup, allocates the RTC, optionally requests a shared threaded IRQ, configures wakeup, sets range 2000-2099, enables battery-low IRQ if safe, and registers. Setup disables clockout and timer outputs, disables existing alarms, enables RTC 24-hour mode, clears interrupt status, enables battery detection, and reports oscillator or battery failures. Alarm set first disables both normal alarm and timer interrupt. If the target is within 240 seconds and in the future, Timer A is programmed at 1 Hz; otherwise normal minute/date alarm registers are used.

## State and persistence behavior

Hardware persists BCD calendar registers, normal alarm registers, Timer A settings, control bits, oscillator status, and battery flags. Software state `timer_alarm` is required to know whether `read_alarm()` and `alarm_irq_enable()` should address Timer A or alarm registers. A driver reload can lose that distinction if hardware still has a timer-based alarm.

## Dependencies and integration points

The driver depends on I2C, regmap, BCD helpers, IRQ threading, OF compatible `"abracon,abb5zes3"`, RTC class APIs, and PM sleep wake IRQ enable/disable. It uses `device_init_wakeup()` only when an IRQ is available.

## Risks and edge cases

There appears to be a setup bug: the code attempts to disable alarm field matching by calling `regmap_update_bits()` on `ABB5ZES3_REG_CTRL2` with alarm-register enable-bit masks; those masks belong to alarm registers `0x0a` through `0x0d`, not CTRL2. Short-alarm state depends on volatile `timer_alarm`. Normal alarms have no seconds field and are limited to about one month. The IRQ handler disables battery-low interrupts because the flag cannot be cleared until battery replacement. Time reads return `-ENODATA` if oscillator integrity failed.

## Test signals

Test chip validation masks, set/read time in 24-hour mode, oscillator-stop reporting, battery-low startup and IRQ handling, normal alarms beyond 240 seconds, timer alarms under 240 seconds, suspend wake, and driver reload with a pending Timer A alarm. Static review should verify the alarm-disable register address in setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-b5ze-s3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-eoz9.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-eoz9.c

## Purpose

`rtc-ab-eoz9.c` drives the Abracon AB-RTCMC-32.768kHz-EOZ9 I2C RTC. It provides BCD timekeeping, optional alarm/wakeup support, trickle charger configuration from device tree, voltage-validity checks, and optional hwmon temperature reporting.

## Important APIs, types, and functions

`struct abeoz9_rtc_data` stores the RTC device, regmap, and optional hwmon device. Key routines are `abeoz9_check_validity()`, `abeoz9_reset_validity()`, `abeoz9_rtc_get_time()`, `abeoz9_rtc_set_time()`, `abeoz9_rtc_read_alarm()`, `abeoz9_rtc_set_alarm()`, `abeoz9_rtc_alarm_irq_enable()`, `abeoz9_rtc_irq()`, `abeoz9_trickle_parse_dt()`, `abeoz9_rtc_setup()`, and `abeoz9_hwmon_register()`. The optional hwmon read path exposes temperature input/min/max.

## Control flow

Probe validates I2C functionality, creates an 8-bit regmap, allocates data, runs setup, allocates the RTC, sets range 2000-2099, initially clears `RTC_FEATURE_ALARM`, requests IRQ if supplied, sets or clears feature bits based on IRQ and `wakeup-source`, registers the RTC, and then registers hwmon when enabled. Time reads first reject invalid data when power-on or voltage-drop flags are set. Set time writes seven BCD registers and clears validity flags. Alarm set clears pending AF, writes seconds/minutes/hours/day fields with alarm-enable bits, and then toggles AIE.

## State and persistence behavior

Hardware persists calendar, alarm, control, EEPROM trickle/temperature-enable bits, validity flags, and interrupt flags. Software state is minimal. The setup path writes CTRL1, clears interrupt registers, and updates EEPROM bits every probe, so probe can alter chip configuration.

## Dependencies and integration points

The driver depends on I2C, regmap, BCD, bitfield helpers, OF compatible `"abracon,abeoz9"`, RTC class APIs, `wakeup-source` firmware property, and optional hwmon. Alarm support is exposed only with an IRQ or wakeup-source.

## Risks and edge cases

The hour decode tests `ABEOZ9_HOURS_PM` as if it selects 12-hour mode and then tests the same bit again for PM; that should be checked against the datasheet. `ABEOZ9_REG_EEPROM_MASK` is `GENMASK(8, 0)` even though registers are 8-bit, which may be harmless through regmap but is suspicious. `abeoz9_rtc_setup()` overwrites interrupt control and EEPROM fields at probe. `read_alarm()` fills only sec/min/hour/mday; the common RTC layer may need to complete missing calendar fields.

## Test signals

Validate power-on and voltage-low invalid time rejection, setting time clears validity flags, alarm IRQ reports and clears AF, no-IRQ systems hide alarm/update interrupt support as expected, trickle resistor values map correctly, hwmon temperature conversion is correct, and probe does not unexpectedly erase board-required EEPROM bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab-eoz9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab8500.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab8500.c

## Purpose

`rtc-ab8500.c` is the RTC driver for the AB8500 PMIC. It exposes a minute-based PMIC clock with fractional seconds, minute-resolution alarms, wake IRQ support, and a sysfs calibration attribute.

## Important APIs, types, and functions

The RTC callbacks are `ab8500_rtc_read_time()`, `ab8500_rtc_set_time()`, `ab8500_rtc_read_alarm()`, `ab8500_rtc_set_alarm()`, and `ab8500_rtc_irq_enable()`. Calibration helpers `ab8500_rtc_set_calibration()` and `ab8500_rtc_get_calibration()` back the `rtc_calibration` sysfs attribute. `rtc_alarm_handler()` reports `RTC_AF`. Probe sets `RTC_FEATURE_ALARM_RES_MINUTE`, clears update interrupt support, sets a 24-bit-minute range, and enables `set_start_time` from year 2000.

## Control flow

Probe gets the named `ALARM` IRQ, performs an RTC supply test by setting and reading `RTC_STATUS_DATA`, initializes wakeup, allocates the RTC, requests the threaded IRQ, associates it as wake IRQ, adds the calibration sysfs group, and registers. Read time requests a latched read, polls until the read request bit clears, reads five time registers, combines 24-bit minutes and seconds counter ticks, and converts to `rtc_time`. Set time converts seconds to minutes plus fractional second counts and writes the same registers, then requests a write. Alarm operations read/write three minute alarm registers and toggle `RTC_ALARM_ENA`.

## State and persistence behavior

Persistent state is in AB8500 RTC registers: watch time, alarm minutes, status/control bits, calibration, and backup/supply status. The RTC class offset/range support is used to present a range starting at 2000 even though hardware stores a limited minute count.

## Dependencies and integration points

The driver depends on ABX500/AB8500 MFD register helpers, platform IDs, named platform IRQs, RTC class APIs, PM wake IRQ helpers, sysfs attributes, and OF/module platform binding.

## Risks and edge cases

Alarms have minute resolution only; seconds are discarded. The read-time poll exits after one second but does not explicitly return timeout if the request bit remains set, so stale reads may be possible. Calibration uses sign-magnitude conversion and rejects `-128`; sysfs parsing uses `sscanf`. Register access is interruptible and can fail at many points. Range expansion through `set_start_time` must stay aligned with the core interface behavior.

## Test signals

Test supply-failure detection, time read latch polling, set/read around minute boundaries, minute-resolution alarm rounding through the RTC core, wake IRQ from suspend, calibration sysfs read/write including limits `-127..127`, and error propagation from ABX500 register helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ab8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-abx80x.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-abx80x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ac100.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-ac100.c

## Purpose

`rtc-ac100.c` drives the RTC block in the X-Powers AC100 MFD and also registers three RTC-related clock outputs. It supports BCD timekeeping, full-date alarms, an alarm IRQ, and clock provider integration for the AC100 clock output pins.

## Important APIs, types, and functions

`struct ac100_rtc_dev` stores the RTC, regmap, IRQ, fixed 32 kHz clock, three `struct ac100_clkout` instances, and onecell clock data. Clock operations implement prepare/unprepare, parent selection, rate calculation, rate selection, and rate programming. RTC operations include `ac100_rtc_get_time()`, `ac100_rtc_set_time()`, `ac100_rtc_get_alarm()`, `ac100_rtc_set_alarm()`, and `ac100_rtc_alarm_irq_enable()`. `ac100_rtc_register_clks()` and `ac100_rtc_unregister_clks()` manage the clock provider.

## Control flow

Probe gets the parent AC100 regmap and IRQ, allocates the RTC, requests a shared threaded alarm IRQ, forces 24-hour mode, disables and clears pending alarm interrupts, registers the fixed 32 kHz clock and three output clocks, and finally registers the RTC. Time set validates the 1970-2069 range, writes seven BCD fields plus an update trigger, and sets the leap-year bit when applicable. Alarm set validates the same range, writes enabled match bits for sec/min/hour/day/month/year while disabling weekday matching, triggers update, and toggles interrupt enable. IRQ handling locks the RTC, reads status, reports `RTC_AF`, clears status, and disables alarm interrupts.

## State and persistence behavior

Hardware persists calendar, alarm, interrupt state, RTC control, and clock output control registers. Software state tracks registered clocks and the RTC device. Clock provider registration persists until remove, where the provider and fixed clock are unregistered.

## Dependencies and integration points

The driver depends on the AC100 MFD, regmap, RTC class, common clock framework, OF clock provider APIs, BCD helpers, and platform IRQs. It consumes the codec-side parent clock name from device tree and allows `clock-output-names` overrides.

## Risks and edge cases

`ac100_clkout_set_rate()` computes `(pre_div - 1)` even when pre-divider value is zero, which should be checked against expected divider encoding. The clock registration path unregisters the fixed clock on later failures but a missing second parent returns before that cleanup path, so fixed-clock cleanup should be reviewed. RTC range is limited to 2069. The IRQ handler returns handled even if no alarm bit was set. Weekday alarm matching is intentionally disabled.

## Test signals

Test time/alarm round trips for 1970, leap years, and 2069, alarm IRQ clearing and auto-disable, clock output parent/rate/enable operations for all three outputs, missing codec parent clock behavior, remove cleanup of clock provider, and regmap write ordering for update trigger bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-ac100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-amlogic-a4.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-amlogic-a4.c

## Purpose

`rtc-amlogic-a4.c` is the Amlogic A4/A5 RTC driver. It supports a 32-bit seconds counter, alarm0, digital second adjustment through the RTC offset API, optional Gray-coded counter storage, and clock source initialization from either 32 kHz or 24 MHz oscillators.

## Important APIs, types, and functions

`struct aml_rtc_config` flags SoC differences, currently `gray_stored` for A4. `struct aml_rtc_data` stores regmap, RTC device, IRQ, oscillator/system clocks, enabled state, and config. RTC callbacks are `aml_rtc_read_time()`, `aml_rtc_set_time()`, `aml_rtc_read_alarm()`, `aml_rtc_set_alarm()`, `aml_rtc_alarm_enable()`, `aml_rtc_read_offset()`, and `aml_rtc_set_offset()`. `gray_to_binary()` and `binary_to_gray()` translate counter storage for A4. `aml_rtc_init()` configures oscillator selection and masks alarms.

## Control flow

Probe maps MMIO through regmap, gets the alarm IRQ, validates the `"osc"` clock rate, enables `"sys"` clock, initializes the hardware, enables wakeup, requests the IRQ, sets range `0..U32_MAX`, and registers the RTC. If the RTC is disabled, read paths fail but `set_time()` first enables it and writes the initial counter. Alarm set enables alarm and unmasks interrupt before writing the alarm register. The IRQ handler clears the alarm register and interrupt status, then reports `RTC_AF`.

## State and persistence behavior

Hardware persists the RTC enable bit, counter, alarm register, oscillator selection, 24 MHz divider programming, interrupt mask/clear state, and second adjustment register. Software caches whether the RTC was enabled at initialization and the SoC config. Offset adjustments persist in `RTC_SEC_ADJUST_REG`.

## Dependencies and integration points

The driver uses platform MMIO, regmap, common clocks, OF match data for `"amlogic,a4-rtc"` and `"amlogic,a5-rtc"`, RTC class APIs, and PM sleep wake IRQ enable/disable.

## Risks and edge cases

`FIELD_GET(RTC_ADJ_VALID, reg_val)` uses a single-bit mask with the generic bitfield macro; this works if mask shape is accepted but is worth static checking. `aml_rtc_set_alarm()` ignores `alarm->enabled` and always enables/unmasks before programming; disable is handled only through `alarm_irq_enable()`. Offset calculation divides by `abs(offset)` and accepts only values that map into the 19-bit match counter. Disabled hardware returns `-EINVAL` on reads until time is set.

## Test signals

Test A4 Gray-coded and A5 binary modes, both oscillator rates, first `set_time()` enabling a disabled RTC, alarm set/read/disable/IRQ clear, suspend wake, offset read/set for positive, negative, zero, too-large, and non-divisor values, and register state after `aml_rtc_init()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-amlogic-a4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-armada38x.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-armada38x.c

## Purpose

`rtc-armada38x.c` drives Marvell Armada 38x and Armada 7K/8K RTC blocks. It supports seconds-counter timekeeping, one alarm, calibration offset, SoC bridge timing setup, and multiple hardware workarounds for unreliable access.

## Important APIs, types, and functions

`struct armada38x_rtc_data` abstracts SoC-specific bridge timing, register read workaround, interrupt clear/unmask, and alarm selection. `struct armada38x_rtc` stores mapped RTC and SoC registers, spinlock, IRQ, initialization state, and sampling buffer. RTC callbacks include `armada38x_rtc_read_time()`, `armada38x_rtc_set_time()`, `armada38x_rtc_read_alarm()`, `armada38x_rtc_set_alarm()`, `armada38x_rtc_alarm_irq_enable()`, `armada38x_rtc_read_offset()`, and `armada38x_rtc_set_offset()`. `rtc_delayed_write()` implements the erratum workaround.

## Control flow

Probe maps `"rtc"` and `"rtc-soc"` resources, gets the IRQ, allocates the RTC, requests the IRQ if available, configures wakeup or clears alarm support, updates MBUS bridge timing, assigns ops and `range_max = U32_MAX`, and registers. For Armada 38x, reads sample a register up to 100 times and return the most frequent value. Set time lazily resets uninitialized RTC state before writing. Alarm set writes the compare register and, if enabled, enables the corresponding IRQ and unmasks SoC interrupt routing. IRQ handling clears SoC ISR, disables the alarm IRQ, acknowledges RTC status, derives update/periodic flags if frequency bits were set, and reports to the RTC core.

## State and persistence behavior

Hardware persists time, alarm, IRQ config, correction register, status, and bridge timing registers. The driver keeps volatile `initialized` state to avoid repeated reset and a sampling buffer for read workarounds. Calibration persists in `RTC_CCR`.

## Dependencies and integration points

It depends on platform resources, OF compatibles `"marvell,armada-380-rtc"` and `"marvell,armada-8k-rtc"`, MMIO, spinlocks, RTC class APIs, and PM wake IRQ handling. The RTC offset API exposes hardware calibration in parts per billion.

## Risks and edge cases

The write path requires two dummy writes and a 5 us delay; missing that pattern can lose writes. The 38x read workaround assumes the most frequent sample is correct. Offset conversion is non-linear and clamps inputs to avoid division issues. `armada38x_rtc_set_offset()` writes without taking the driver's spinlock, unlike other register mutations. If IRQ request fails, alarm features are cleared but alarm registers still exist.

## Test signals

Test both compatibles, read consistency under ticking counter, reset path when `RTC_CONF_TEST` low bits are non-zero, alarm IRQ acknowledge and disable, wake from suspend, offset read/set over clamp limits and fine/coarse mode crossover, and bridge timing reprogramming on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-armada38x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-as3722.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-as3722.c

## Purpose

`rtc-as3722.c` is the RTC driver for AMS AS3722 PMICs. It provides BCD calendar read/set, alarm read/set, alarm IRQ enable/disable, and wakeup support through the AS3722 MFD.

## Important APIs, types, and functions

`struct as3722_rtc` stores the RTC device, device pointer, parent `struct as3722`, alarm IRQ, and software IRQ-enable flag. `as3722_time_to_reg()` and `as3722_reg_to_time()` convert six BCD registers relative to year 2000. RTC callbacks include `as3722_rtc_read_time()`, `as3722_rtc_set_time()`, `as3722_rtc_read_alarm()`, `as3722_rtc_set_alarm()`, and `as3722_rtc_alarm_irq_enable()`. `as3722_alarm_irq()` reports `RTC_AF`.

## Control flow

Probe allocates state, enables the RTC and alarm wakeup bits in `AS3722_RTC_CONTROL_REG`, marks the platform device wake-capable, registers the RTC with `devm_rtc_device_register()`, gets and requests the alarm IRQ, then disables the IRQ until an alarm is enabled. Setting an alarm first disables the IRQ, writes the six alarm BCD registers, and re-enables the IRQ if requested.

## State and persistence behavior

Hardware persists calendar, alarm, RTC enable, and alarm wakeup bits. Software `irq_enable` mirrors whether the IRQ line is enabled in Linux to avoid unbalanced `enable_irq()` and `disable_irq()` calls.

## Dependencies and integration points

The driver depends on the AS3722 MFD API (`as3722_block_read`, `as3722_block_write`, `as3722_update_bits`), platform IRQs, RTC class APIs, PM sleep wake IRQ operations, and the platform device name `"as3722-rtc"`.

## Risks and edge cases

The driver uses older `devm_rtc_device_register()` rather than allocate/register split. `read_alarm()` does not populate `enabled` or `pending`, so users may not see current enable state from readback. The IRQ handler reports alarms but does not acknowledge a PMIC status bit locally; that may be handled by the MFD IRQ layer and should be verified. Year values before 2000 are rejected.

## Test signals

Test enabling RTC control bits at probe, time set/read around 2000 boundary, alarm write/read and IRQ enable balancing, IRQ delivery through the MFD, suspend/resume wake IRQ, and userspace `RTC_ALM_READ` behavior for enabled/pending fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-as3722.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-asm9260.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-asm9260.c

## Purpose

`rtc-asm9260.c` drives the Alphascale ASM9260 SoC RTC. It exposes consolidated time registers, direct time-counter writes, full-field alarm registers, and alarm IRQ masking through the RTC class.

## Important APIs, types, and functions

`struct asm9260_rtc_priv` stores the device, MMIO base, RTC device, and AHB clock. RTC callbacks are `asm9260_rtc_read_time()`, `asm9260_rtc_set_time()`, `asm9260_rtc_read_alarm()`, `asm9260_rtc_set_alarm()`, and `asm9260_alarm_irq_enable()`. `asm9260_rtc_irq()` handles alarm/increment interrupt state and calls `rtc_update_irq()`.

## Control flow

Probe gets the alarm IRQ, maps MMIO, enables the AHB clock, resets/enables the RTC clock control if needed, clears counter increment interrupt state, masks alarms, registers the RTC, and requests a threaded IRQ. Read time reads consolidated registers CTIME0-2 and rereads if CTIME1 changes across the sample. Set time writes second as zero first to prevent cascading while updating year/month/day/wday/yday/hour/minute, then writes the actual second. Alarm set writes all alarm fields and sets `HW_AMR` to either all matches enabled or all masked.

## State and persistence behavior

Hardware persists current calendar counters, alarm registers, mask register, clock control, calibration, and general-purpose registers. Software only tracks MMIO/clock/RTC pointers. Remove masks alarms and disables the AHB clock.

## Dependencies and integration points

It depends on platform MMIO/IRQ resources, common clock API, RTC class APIs, and OF compatible `"alphascale,asm9260-rtc"`.

## Risks and edge cases

The IRQ handler reads and clears `HW_CIIR`, which is documented as the counter increment interrupt register, not the interrupt location register; this should be verified against hardware because alarm status may actually live in `HW_ILR`. `read_time()` returns `tm_mon` directly from hardware without subtracting one and `tm_year` directly without subtracting 1900, unlike normal RTC ABI expectations; set paths mirror that raw format. `read_alarm()` validates the raw alarm time and can fail if partial fields are used.

## Test signals

Test ABI-correct month/year values against real hardware, alarm IRQ status source and clear behavior, set/read time coherence across a second rollover, alarm mask enable/disable, clock disable on remove, and invalid alarm field handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-asm9260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-aspeed.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-aspeed.c

## Purpose

`rtc-aspeed.c` is the ASPEED AST2400/AST2500/AST2600 RTC driver. It provides simple MMIO read/set support for calendar time and has no alarm or interrupt support.

## Important APIs, types, and functions

`struct aspeed_rtc` stores the mapped base. RTC callbacks are `aspeed_rtc_read_time()` and `aspeed_rtc_set_time()`. The driver uses `RTC_TIME`, `RTC_YEAR`, and `RTC_CTRL` registers with `RTC_UNLOCK` and `RTC_ENABLE` bits.

## Control flow

Probe allocates state, maps the resource, allocates an RTC, sets ops and range 1900 through 3199-12-31, and registers. Read time first rejects disabled hardware, then reads `RTC_YEAR`, `RTC_TIME`, and `RTC_YEAR` again until the year register is stable. Set time encodes day/hour/min/sec and century/year/month, unlocks writes, writes time and year registers, then relocks with enable set.

## State and persistence behavior

Hardware persists time/year and control bits. The driver has no software state beyond the mapped base. Setting time ensures the hardware is enabled after programming.

## Dependencies and integration points

It depends on platform MMIO, OF compatibles for ASPEED AST RTCs, RTC class APIs, and the platform-driver-probe registration pattern.

## Risks and edge cases

There is no alarm, wake, validity, oscillator, or backup-loss check. The `year = tm->tm_year % 100` calculation relies on `tm_year` being years since 1900; for centuries after 1999 that still encodes the low two digits but deserves tests across century boundaries. Register fields are binary rather than BCD. Disabled RTC reads return `-EINVAL` until time is programmed.

## Test signals

Test read failure before enable, set/read round trips for 1900, 1999, 2000, 2099, 2100, and 3199, write unlock/enable behavior, stable read loop around rollover, and userspace absence of alarm ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-aspeed.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91rm9200.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91rm9200.c

## Purpose

`rtc-at91rm9200.c` drives the Atmel/Microchip AT91 RTC peripheral family. It provides BCD time/calendar registers, alarm registers, update synchronization, optional correction offset on newer variants, shared IRQ handling, and suspend wake event caching.

## Important APIs, types, and functions

`struct at91_rtc_config` selects shadow IMR and correction support. Global state tracks mapped registers, IRQ, slow clock, completions `at91_rtc_updated` and `at91_rtc_upd_rdy`, shadow interrupt mask, suspend state, and cached events. RTC callbacks include `at91_rtc_readtime()`, `at91_rtc_settime()`, `at91_rtc_readalarm()`, `at91_rtc_setalarm()`, `at91_rtc_alarm_irq_enable()`, and on SAMA5-class devices `at91_rtc_readoffset()` and `at91_rtc_setoffset()`.

## Control flow

Probe maps MMIO, enables the slow clock, forces 24-hour mode, disables all interrupts, requests a shared conditional-suspend IRQ, enables wake capability, selects ops based on correction support, sets range 1900-2099, registers the RTC, and enables second events so the update-ready completion can initialize. Setting time waits for update readiness, requests calendar/time update mode, enables ACKUPD IRQ, waits for acknowledgement, writes BCD time/calendar registers, clears second event, leaves update mode, and enables second-event IRQ again. IRQ handling reads status masked by IMR/shadow IMR, completes update waiters, clears status, reports or caches RTC events depending on suspend state.

## State and persistence behavior

Hardware persists time/calendar, alarm, mode/correction, interrupt masks, and status. Driver state is mostly global because this old driver assumes one device. During suspend, enabled alarm/second events are cached and replayed on resume if wake-capable.

## Dependencies and integration points

It depends on platform MMIO and IRQ, common clock API, BCD and bitfield helpers, completions, spinlocks, RTC class APIs, PM suspend helpers, and OF compatibles for AT91RM9200, AT91SAM9x5, SAMA5D4/D2, and SAM9X60.

## Risks and edge cases

Global singleton state prevents multiple independent instances. Shadow IMR is a workaround for unreliable IMR reads and must stay synchronized with IER/IDR writes. `at91_rtc_decodetime()` returns full year before the caller subtracts 1900; alarm year is intentionally invalid because hardware lacks it. Offset conversion has low/high correction modes and rejects large values. Shared IRQ and suspend caching require careful ordering to avoid lost wake events.

## Test signals

Test set-time synchronization with ACKUPD, alarm matching and readback with missing year, correction read/set on SAMA5-class compatibles, shadow IMR behavior, shared IRQ rejection when status is not ours, suspend wake caching and replay, and cleanup paths disabling interrupts and clocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91rm9200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91sam9.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91sam9.c

## Purpose

`rtc-at91sam9.c` implements an RTC using the AT91SAM9 real-time timer (RTT) plus a general-purpose backup register (GPBR). The RTT counter cannot be set directly, so wall-clock time is represented as GPBR base offset plus the RTT's seconds counter.

## Important APIs, types, and functions

`struct sam9_rtc` stores RTT MMIO, RTC device, interrupt mask, GPBR regmap and offset, IRQ, slow clock, suspend/cached-event state, and a spinlock. RTC callbacks are `at91_rtc_readtime()`, `at91_rtc_settime()`, `at91_rtc_readalarm()`, `at91_rtc_setalarm()`, `at91_rtc_alarm_irq_enable()`, plus `at91_rtc_proc()` for `/proc/driver/rtc`. Event helpers `at91_rtc_cache_events()` and `at91_rtc_flush_events()` manage IRQ delivery.

## Control flow

Probe gets the IRQ, maps RTT registers, resolves `atmel,rtt-rtc-time-reg` to a syscon GPBR and offset, enables the slow clock, checks the prescaler against the slow-clock rate, resets RTT and clears GPBR if needed, disables interrupts, allocates/registers the RTC with `range_max = U32_MAX`, and requests a shared conditional-suspend IRQ. Read time rejects unset GPBR (`0`) with `-EILSEQ`, reads the RTT counter twice to cross clock domains safely, adds the offset, and converts to `rtc_time`. Set time writes a new base, resets the RTT, and adjusts any pending alarm relative to the new base.

## State and persistence behavior

The GPBR base and RTT counter live in the backup power domain and are intended to survive low-power states. Alarm state is the RTT alarm register relative to the base, with `ALARM_DISABLED` as sentinel. Software caches interrupt events while suspended and flushes them on resume.

## Dependencies and integration points

The driver depends on platform MMIO/IRQ, syscon regmap, OF phandle arguments, slow clock API, RTC class APIs, `/proc` RTC hook, and PM wake handling. It matches `"atmel,at91sam9260-rtt"`.

## Risks and edge cases

If GPBR is zero, time is considered unset. Setting time adds one second before writing the base and resets RTT, a behavior that must match expected hardware latency. Changing time adjusts or disables existing alarms depending on whether the time jumps over them. Reading RTT status clears it, so only the IRQ handler may read `SR`. During suspend, increment interrupts are masked to avoid unwanted wakeups.

## Test signals

Test unset GPBR behavior, prescaler reinitialization, set/read time after RTT reset, alarm adjustment across forward and backward time changes, shared IRQ filtering, `/proc` update IRQ output, suspend wake by alarm but not by RTT increment, and persistence across backup-domain retention.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-at91sam9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-atcrtc100.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-atcrtc100.c

## Purpose

`rtc-atcrtc100.c` drives the Andes ATCRTC100 RTC. It exposes a day/hour/min/sec counter, hour/min/sec alarms, wake-capable alarm interrupts, and synchronization around the hardware `WRITE_DONE` status bit.

## Important APIs, types, and functions

`struct atcrtc_dev` stores RTC device, regmap, work item, alarm IRQ, and `alarm_en` software state. `atcrtc_check_write_done()` polls `RTC_STA.WRITE_DONE` before register writes. RTC callbacks are `atcrtc_read_time()`, `atcrtc_set_time()`, `atcrtc_read_alarm()`, `atcrtc_set_alarm()`, and `atcrtc_alarm_irq_enable()`. `atcrtc_alarm_isr()` handles alarm status and `atcrtc_alarm_clear()` disables alarm bits in process context.

## Control flow

Probe maps MMIO through regmap, verifies the hardware ID, gets IRQ index 1 for alarm, requests the IRQ, allocates the RTC, sets the alarm feature, enables wakeup and assigns the wake IRQ, initializes the deferred clear work, and registers. Set time converts POSIX seconds to a hardware day count plus h/m/s fields, waits for write-done before writing counter and again before enabling RTC. Set alarm disables current alarm, writes h/m/s fields, records whether the new alarm should remain enabled, and toggles alarm/wakeup bits. The ISR clears status, marks `alarm_en = false`, schedules work to clear control bits, and reports `RTC_AF`.

## State and persistence behavior

Hardware persists counter, alarm, control, status, and trim registers. Software state `alarm_en` prevents the deferred work from clearing a newly re-enabled alarm. The work item is volatile and should be flushed or naturally devres-cleaned with device removal.

## Dependencies and integration points

It depends on platform MMIO/IRQ, regmap polling, RTC class APIs, PM wake IRQ helpers, workqueues, and OF compatible `"andestech,atcrtc100"`.

## Risks and edge cases

The alarm supports only h/m/s and returns `-1` for day/month/year, relying on the RTC core to complete missing fields. The status test in the ISR checks `ALARM_INT`, a control-bit name reused as status bit, which should be checked against the hardware manual. Probe calls both `dev_pm_set_wake_irq()` and manual suspend/resume `enable_irq_wake()`/`disable_irq_wake()`, which can be redundant. Workqueue clearing races are mitigated by `alarm_en` but still need stress testing.

## Test signals

Test hardware ID rejection, write-done timeout handling, disabled RTC read returning `-EIO`, set/read time across large day counts, alarm set/read with missing date fields, alarm ISR plus deferred control clear, wake from suspend, and rapid alarm reprogramming while clear work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-atcrtc100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-au1xxx.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-au1xxx.c

## Purpose

`rtc-au1xxx.c` exposes the Au1xxx Time-Of-Year counter as an RTC. Counter 0 counts seconds from the Unix epoch using an external 32.768 kHz crystal and continues during sleep or powerdown when configured by firmware or board code.

## Important APIs, types, and functions

RTC callbacks are `au1xtoy_rtc_read_time()` and `au1xtoy_rtc_set_time()`. Probe checks counter control bits `SYS_CNTRL_E0` and `SYS_CNTRL_32S`, sets the TOY trim register to 32767 for a 1 Hz tick if needed, waits for hardware write access, allocates/registers the RTC, and sets `range_max = U32_MAX`.

## Control flow

Read time reads `AU1000_SYS_TOYREAD` through `alchemy_rdsys()` and converts seconds to `rtc_time`. Set time writes seconds to `AU1000_SYS_TOYWRITE`, then waits while `SYS_CNTRL_C0S` indicates a pending counter write. Probe waits for trim access through `SYS_CNTRL_T0S` with a large timeout and fails if access never becomes available.

## State and persistence behavior

Hardware persists the TOY counter and trim configuration in Au1xxx system registers. The driver has no private state beyond the registered RTC device. It assumes bootloader or board code has enabled and clocked the counters.

## Dependencies and integration points

It depends on Alchemy/Au1xxx architecture system register helpers from `<asm/mach-au1x00/au1000.h>`, platform devices, and RTC class APIs. It is registered with platform name `"rtc-au1xxx"`.

## Risks and edge cases

Set-time waits for up to about six seconds without a timeout in the final counter-write wait. Probe explicitly does not verify the actual 32 kHz clock quality because that would be too slow. There is no alarm or wake support. The range is limited to 32-bit seconds.

## Test signals

Test probe failure when counter status bits are absent, trim programming and timeout path, set/read round trips, behavior while counter write pending, persistence through sleep/powerdown, and absence of alarm ioctls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-au1xxx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bd70528.c -->
# sources/distributed-fs/ceph-client/drivers/rtc/rtc-bd70528.c

## Purpose

`rtc-bd70528.c` drives RTC blocks in ROHM BD71828, BD71815, and BD72720 PMICs. It supports BCD calendar read/set, alarm0 programming, alarm IRQ enable/disable, and conversion from 12-hour mode to enforced 24-hour mode at probe.

## Important APIs, types, and functions

Packed register-layout structs `bd70528_rtc_day`, `bd70528_rtc_data`, and `bd71828_rtc_alm` match PMIC register order. `struct bd70528_rtc` stores parent/regmap/device and chip-specific time/alarm register starts. Conversion helpers `tmday2rtc()`, `tm2rtc()`, and `rtc2tm()` preserve unrelated register bits while updating BCD fields. RTC callbacks are `bd70528_get_time()`, `bd71828_set_time()`, `bd71828_read_alarm()`, `bd71828_set_alarm()`, and `bd71828_alm_enable()`.

## Control flow

Probe determines the chip from the platform ID, sets register start addresses, gets named IRQ `"bd70528-rtc-alm-0"`, reads the hour register, converts the RTC to 24-hour mode by read/set if needed, enables wake capability, allocates the RTC, sets range 2000-2099, requests the threaded alarm IRQ, and registers. Time set/read bulk-transfer the register struct. Alarm set bulk-reads the full alarm block, updates `alm0`, toggles the alarm mask bit, and bulk-writes the block. Alarm read returns only time-of-day and wildcard date fields.

## State and persistence behavior

Hardware persists calendar, alarm blocks, mask bits, and hour mode. Software state records chip-specific register offsets. Probe may modify persistent time registers to convert 12-hour mode to 24-hour mode while preserving the represented time.

## Dependencies and integration points

The driver depends on ROHM MFD headers and regmap, platform IDs, named IRQs, RTC class APIs, and wake-capable device settings. It is an MFD child platform driver named `"bd70528-rtc"`.

## Risks and edge cases

The constant `BD718XX_ALM_EN_OFFSET` assumes a 14-byte offset between ALM0 start and mask for all supported chips; comments warn that adding new chips requires validation. `read_alarm()` intentionally sets date fields to `-1`, so core alarm completion is needed. The IRQ handler reports `RTC_PF` together with `RTC_AF`, which should be checked against intended userspace semantics. A typo in the error message says "reag".

## Test signals

Test all three chip IDs, 12-hour to 24-hour conversion, time set/read preserving reserved bits, alarm enable/disable mask offset, alarm IRQ reporting, wake capability, and wildcard alarm read behavior through the RTC core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/rtc/rtc-bd70528.c -->
