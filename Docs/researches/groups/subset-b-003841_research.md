# Research: subset-b-003841

This grouped report covers the exact source files assigned to `subset-b-003841`. Each section preserves the source path in the title and is bounded by reconciliation markers for deterministic splitting into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83793.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83793.c

## Purpose
This driver supports the Winbond W83793 hardware monitor over I2C. It exposes voltage, fan tachometer, PWM, temperature, alarm, beep, VID, SmartFan, chassis intrusion, and watchdog controls through hwmon sysfs attributes and a legacy watchdog miscdevice. The chip has banked register addressing, optional subclients, dynamic pin muxing, and many optional channels determined at probe.

## Important APIs, Types, And Functions
- `struct w83793_data` is the central state object. It stores the hwmon device, update mutex, bank selector cache, per-channel cached registers, feature bitmasks (`has_fan`, `has_pwm`, `has_temp`, `has_vid`), and watchdog lifetime fields.
- `w83793_read_value()` and `w83793_write_value()` are the bank-aware SMBus byte accessors. Callers normally hold `update_lock`, except during initialization.
- Conversion helpers include `FAN_FROM_REG()`, `FAN_TO_REG()`, `TEMP_FROM_REG()`, `TEMP_TO_REG()`, `TIME_FROM_REG()`, and `TIME_TO_REG()`.
- Sysfs callbacks cover voltage (`show_in()`, `store_in()`), fans (`show_fan()`, `store_fan_min()`), PWM (`show_pwm()`, `store_pwm()`), temperature (`show_temp()`, `store_temp()`), temperature type (`show_temp_mode()`, `store_temp_mode()`), SmartFan setup/control/curves, alarms, beeps, VID, and chassis clear.
- Watchdog callbacks include `watchdog_open()`, `watchdog_close()`, `watchdog_write()`, `watchdog_ioctl()`, `watchdog_enable()`, `watchdog_disable()`, `watchdog_trigger()`, and `watchdog_set_timeout()`.
- Driver entry points are `w83793_detect()`, `w83793_probe()`, `w83793_remove()`, and `module_i2c_driver(w83793_driver)`.

## Control Flow
Detection verifies SMBus byte support, vendor ID, I2C address, and chip ID. Probe allocates `w83793_data`, sets the initial bank, creates subclient dummy devices if needed, starts monitoring, reads multifunction pin registers, derives the active fan/PWM/temp/VID channel masks, creates common and conditional sysfs files, registers an hwmon device, enables watchdog registers, disables the watchdog initially, and registers a misc watchdog device on the first available minor.

Normal sysfs reads call `w83793_update_device()`, which refreshes volatile readings at most every two seconds. That function also calls `w83793_update_nonvolatile()` when stale or invalid. Writes parse userspace values, clamp or convert them to register units, update the hardware register, and mirror the cached field while holding `update_lock`.

Watchdog open locates the matching `w83793_data` from a global list guarded by `watchdog_data_mutex`, enforces single-open semantics with `watchdog_is_open`, increments the kref, enables the watchdog, and stores the data pointer in `filp->private_data`. Close disables only after a magic close if `nowayout` permits; otherwise it pings the watchdog and logs an unexpected close. Reboot notifier disables registered watchdogs on shutdown/halt.

## State And Persistence
Sensor state is cached in RAM with two cadences: volatile readings refresh every two seconds and nonvolatile limits/configuration refresh every 300 seconds or after invalidation. Hardware settings written through sysfs persist in chip registers according to the chip's behavior; the driver does not maintain backing storage across unload. The bank register cache (`data->bank`) is a correctness-sensitive optimization. Watchdog state has additional lifetime management through `kref`, a global list, and `data->client = NULL` on detach to stop file operations from touching removed I2C clients.

## Dependencies And Integration Points
The file integrates with the I2C hwmon class, legacy hwmon sysfs helpers, `hwmon_device_register()`, VID helpers, Linux miscdevice watchdog ABI, reboot notifier API, SMBus byte-data transfers, and optional I2C dummy subclients. Module parameters (`reset`, `timeout`, `nowayout`, `force_subclients`) affect initialization and watchdog behavior.

## Risks
- The watchdog path is legacy and hand-rolled rather than using the modern watchdog core, so lifetime, locking, and misc minor allocation are more error-prone.
- `watchdog_open()` assumes the misc minor lookup finds data before calling `test_and_set_bit()`. Its comment says this should always be true, but a broken list/minor invariant would be dangerous.
- Banked register access relies on the assumption that no external actor changes the bank selector.
- Large sysfs attribute arrays use encoded indices and bit offsets; ordering mistakes can silently expose the wrong alarm/beep/channel.
- The cleanup path removes many possible files unconditionally, which is tolerated by sysfs helpers but requires careful maintenance when attributes change.

## Test Signals
Useful validation includes I2C detection with known W83793 IDs, sysfs enumeration for channel masks from multiple pin mux configurations, read/write conversion tests for voltages/fan limits/PWM/temperature thresholds, cache invalidation after chassis clear, watchdog open/close/magic-close/ioctl behavior, unload while watchdog is open, and reboot notifier behavior. Static analysis should focus on array index encodings, lock ordering between `watchdog_data_mutex`, misc registration, and `watchdog_lock`, and banked register access under `update_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83793.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83795.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83795.c

## Purpose
This I2C hwmon driver supports Nuvoton/Winbond W83795G and W83795ADG chips. It exposes up to 21 voltage inputs, 14 fans, 8 PWMs, 6 analog temperatures, 8 DTS temperatures, alarms, beeps, intrusion status, temperature-source routing, and optional SmartFan IV/fan-control attributes.

## Important APIs, Types, And Functions
- `enum chip_types` distinguishes `w83795g` and `w83795adg`, mainly affecting PWM count and beep/OVT pin capabilities.
- `struct w83795_data` stores cached sensor values, feature masks (`has_in`, `has_fan`, `has_temp`, `has_dts`, `has_pwm`), bank state, clock input frequency, PWM/fan-control config, alarms, beeps, and cache validity flags.
- `w83795_set_bank()`, `w83795_read()`, and `w83795_write()` implement banked SMBus access.
- `w83795_update_device()` refreshes volatile readings and alarms; `w83795_update_limits()` refreshes limits/beeps; `w83795_update_pwm_config()` lazily reads slower PWM and SmartFan configuration.
- Sysfs callbacks cover alarm/beep, chassis clear, fan input/min, PWM output/frequency/enable/mode, temperature-source selection, fan targets/tolerance, temperature limits, DTS limits, voltage limits, and optional fan-control setup.
- `w83795_handle_files()` centralizes conditional creation/removal of sysfs files.

## Control Flow
Detection checks SMBus support, bank register shape, vendor ID, device ID, I2C address, and chip subtype. Probe allocates data with devm, initializes monitoring, reads voltage/fan/temp/DTS/pin configuration registers, derives capability masks, computes CLKIN, determines W83795G versus ADG behavior, determines beep availability, creates the conditional sysfs surface, marks dynamic voltage limits read-only on W83795G when VID controls them, and registers the hwmon device.

Runtime reads enter either `w83795_update_device()` or `w83795_update_pwm_config()`. The main cache refreshes every two seconds and includes sensor values, dynamic voltage limits, fan counts, temperatures, DTS values, PWM outputs, intrusion state, and alarms. Limit and PWM-configuration caches are separate so stable register groups are not reread on every sensor read. Writes update the hardware register and cache under `update_lock`.

## State And Persistence
The driver keeps three validity domains: volatile readings, limits/beeps, and PWM configuration. Hardware register writes change chip state directly; the driver mirrors writes in RAM but does not persist state outside hardware. Some voltage limit files become read-only when the chip derives limits dynamically from VID. The bank register cache is per device and must track all register access.

## Dependencies And Integration Points
It integrates with I2C hwmon class scanning, the legacy hwmon sysfs attribute API, `hwmon_device_register()`, SMBus byte data, optional `CONFIG_SENSORS_W83795_FANCTRL`, and the Linux sysfs permission API for dynamic limit files. It uses `find_closest_descending()` for PWM frequency selection and exposes standard libsensors-compatible names.

## Risks
- Many attributes are generated from multidimensional arrays, and comments warn that attribute ordering is used elsewhere in the code. Reordering can break indexing.
- `w83795_update_device()` reads `W83795_REG_VRLSB` repeatedly inside loops; correctness depends on chip latch semantics being compatible with that pattern.
- The detection path writes the bank selector to bank 0 to determine subtype, which is unusual for detection and must remain tightly justified.
- Optional fan-control support changes the number of exported temp/PWM attributes, so ABI coverage must be checked under both config modes.
- Dynamic VID limits require sysfs mode changes; failure leaves user-visible permissions inconsistent with hardware behavior.

## Test Signals
Test with both W83795G and W83795ADG IDs/configuration bits, with and without `CONFIG_SENSORS_W83795_FANCTRL`. Validate sysfs file creation for sparse feature masks, dynamic in0-in2 permissions, voltage LSB conversions, fan min 12-bit packing, PWM frequency round-trip behavior for all CLKIN values, DTS PECI/SB-TSI modes, alarm/intrusion clearing, and cleanup after partial file creation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83795.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83l785ts.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83l785ts.c

## Purpose
This compact I2C hwmon driver supports the Winbond W83L785TS-S single external temperature sensor. It exposes read-only `temp1_input` and `temp1_max` attributes.

## Important APIs, Types, And Functions
- `struct w83l785ts_data` stores the hwmon device, update mutex, cache validity, timestamp, and two signed 8-bit temperature register values.
- `w83l785ts_detect()` validates SMBus support, configuration/type register shape, Winbond manufacturer ID, and chip ID.
- `w83l785ts_read_value()` wraps SMBus byte reads with up to five retries and a caller-provided default value.
- `w83l785ts_update_device()` refreshes cached current and overtemperature values every two seconds.
- `show_temp()` converts signed register values to millidegrees Celsius through `TEMP_FROM_REG()`.

## Control Flow
The I2C core detects only address `0x2e`. Probe allocates device data, initializes the mutex, creates the two sysfs files, and registers the hwmon device. Reads call `w83l785ts_update_device()`, which retries hardware reads and preserves the previous cached value as the default if all retries fail after probe. Remove unregisters hwmon and removes the two attributes.

## State And Persistence
State is limited to a two-second software cache of current and max temperature. The driver does not write chip registers and assumes the chip is already started. Read failures after initial cache population can leave the previous value visible.

## Dependencies And Integration Points
The file uses I2C SMBus byte data, hwmon sysfs helpers, `hwmon_device_register()`, jiffies-based cache expiry, and devm allocation. It is an `I2C_CLASS_HWMON` scanning driver.

## Risks
- `temp1_max` is read-only, so users cannot adjust the overtemperature threshold through this driver.
- The `W83L785TS_REG_TEMP_OVER` comment says the register is uncertain, making threshold semantics less reliable.
- Detection relies on old-style probing and could conflict if another device responds similarly at the fixed address.
- Retry delays are small but occur under the update mutex and on sysfs reads.

## Test Signals
Validate detection against manufacturer/chip ID values, retry fallback on injected SMBus errors, signed negative temperature conversion, two-second cache behavior, and sysfs cleanup when the second attribute or hwmon registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83l785ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83l786ng.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/w83l786ng.c

## Purpose
This I2C hwmon driver supports the Winbond W83L786NG with three voltage inputs, two fan tachometers, two PWM outputs, two temperature channels, fan divisors, thermal cruise modes, and Smart Fan tolerance controls.

## Important APIs, Types, And Functions
- `struct w83l786ng_data` stores the I2C client, cache mutex, timestamp, voltage/fan/temp/PWM/tolerance register caches, fan divisors, PWM mode, and PWM enable state.
- `w83l786ng_read_value()` and `w83l786ng_write_value()` wrap SMBus byte data access.
- `w83l786ng_update_device()` refreshes all cached volatile and limit/config registers every 1.5 seconds.
- Conversion helpers include `FAN_TO_REG()`, `fan_from_reg()`, `TEMP_TO_REG()`, `temp_from_reg()`, `IN_TO_REG()`, `IN_FROM_REG()`, `DIV_FROM_REG()`, and `DIV_TO_REG()`.
- Sysfs callbacks implement in*_input/min/max, fan*_input/min/div, temp*_input/max/max_hyst, pwm*, pwm*_mode, pwm*_enable, and pwm*_tolerance.

## Control Flow
Detection checks SMBus byte support, verifies the config reset bit is not set, and matches Winbond manufacturer and W83L786NG chip ID. Probe allocates data, starts monitoring if needed, seeds fan minimum and divisor values, and registers a devm hwmon device with an attribute group. There is no explicit remove path because devm handles group/device teardown.

Sysfs reads refresh the cache if stale. Writes validate and convert userspace values, update the relevant register, and update cached state while holding `update_lock`. Changing fan divisors saves the old fan minimum in RPM units and rewrites fan minimum after the divisor update, preserving the user's threshold.

## State And Persistence
The driver maintains a 1.5-second RAM cache of all exposed register values. Register writes modify chip hardware state; there is no separate persistence. The `reset` module parameter can reset the chip during initialization. Fan divisor changes have coupled state because the divisor changes the interpretation of fan count and fan minimum registers.

## Dependencies And Integration Points
It integrates with the I2C hwmon class, devm hwmon group registration, legacy sensor attribute macros, and SMBus byte data. It exposes standard hwmon ABI names and uses a fixed scan list of `0x2e` and `0x2f`.

## Risks
- Fan divisor updates touch both the divisor register and fan minimum; mistakes can surprise users by changing threshold semantics.
- `w83l786ng_read_value()` returns an unsigned byte but does not check negative SMBus errors, so failed reads become truncated values.
- PWM register packing uses only low nibbles scaled to 0-255; high-nibble preservation is required on writes.
- The cache refresh reads limits/configuration as frequently as sensor values, which is simpler but costlier.

## Test Signals
Validate detection, reset/start-monitoring behavior, voltage scaling, signed temperature conversion, fan divisor round trips, fan minimum preservation across divisor changes, PWM mode/enable bit packing, tolerance nibble writes, and SMBus error behavior under fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/w83l786ng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/wm831x-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/wm831x-hwmon.c

## Purpose
This platform hwmon driver exposes auxiliary ADC readings from WM831x PMIC devices. It reports four generic AUX voltages, named system/USB/battery/wall/backup-battery voltages, PMIC chip temperature, and battery temperature as a voltage.

## Important APIs, Types, And Functions
- `input_names[]` maps WM831x AUXADC channel IDs to label strings.
- `show_voltage()` calls `wm831x_auxadc_read_uv()` and reports millivolts.
- `show_chip_temp()` calls `wm831x_auxadc_read()` and converts raw ADC code to millidegrees Celsius using the formula in the comment.
- `show_label()` prints channel labels.
- `wm831x_hwmon_probe()` gets the parent MFD `struct wm831x` and registers devm hwmon groups.

## Control Flow
The platform device is created by the WM831x MFD layer. Probe fetches the parent driver data and registers a fixed attribute group with `devm_hwmon_device_register_with_groups()`. Sysfs reads call into the PMIC AUXADC helpers directly; no driver-local cache is maintained.

## State And Persistence
The driver has no mutable runtime state beyond the hwmon registration. Values are live ADC reads. Labels are static. Any ADC calibration or power sequencing is delegated to the WM831x MFD/AUXADC layer.

## Dependencies And Integration Points
It depends on the WM831x MFD core and AUXADC APIs, platform-device binding `wm831x-hwmon`, hwmon sysfs groups, and standard sensor attribute helpers.

## Risks
- The chip temperature conversion is hard-coded; wrong raw-unit assumptions in the lower AUXADC helper would produce wrong millidegree output.
- Battery temperature is intentionally reported as voltage because external components determine conversion, so userspace must know board-specific thermistor scaling.
- No cache means frequent reads can trigger frequent ADC conversions.

## Test Signals
Validate MFD child probing, each AUXADC channel read path, label mapping, negative error propagation from AUXADC helpers, PMIC temperature conversion with known raw values, and hwmon group registration/teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/wm831x-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/wm8350-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/wm8350-hwmon.c

## Purpose
This platform hwmon driver exposes WM8350 PMIC AUXADC voltage channels for USB, battery, and line inputs, with labels.

## Important APIs, Types, And Functions
- `input_names[]` maps WM8350 AUXADC channel IDs to labels.
- `show_voltage()` calls `wm8350_read_auxadc()`, multiplies by `WM8350_AUX_COEFF`, and reports millivolts.
- `show_label()` prints the static channel label.
- `wm8350_hwmon_probe()` gets the MFD-provided `struct wm8350` from platform data and registers the hwmon group.

## Control Flow
Probe is invoked for the `wm8350-hwmon` platform device. It registers a static sysfs group with three voltage inputs and three labels. Sysfs reads perform direct AUXADC conversions through the WM8350 MFD/comparator API.

## State And Persistence
The driver has no local cache or persistent settings. All values are live readings from PMIC ADC hardware, and labels are compile-time constants.

## Dependencies And Integration Points
It depends on WM8350 MFD core/comparator headers, platform-device binding `wm8350-hwmon`, hwmon sysfs groups, and devm hwmon registration.

## Risks
- `show_voltage()` does not check for negative error returns before multiplying by `WM8350_AUX_COEFF`, so lower-level ADC errors may be converted into misleading values if the helper can fail with negative codes.
- Board-specific scaling beyond the PMIC coefficient is not represented.
- No cache may make rapid sysfs polling expensive.

## Test Signals
Validate platform data retrieval, voltage conversion for known raw ADC codes, negative ADC error behavior, label mapping, and devm hwmon group cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/wm8350-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/xgene-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/xgene-hwmon.c

## Purpose
This platform hwmon driver exposes APM X-Gene SoC telemetry provided by the SLIMpro management processor or ACPI PCC. It reports SoC temperature, CPU power, IO power, and a temperature critical alarm notification.

## Important APIs, Types, And Functions
- `struct xgene_hwmon_dev` owns mailbox/PCC channels, mailbox client callbacks, synchronization primitives, async message FIFO, work item, hwmon device pointer, alarm state, and PCC latency.
- `xgene_hwmon_rd()` sends a synchronous SLIMpro mailbox command and waits for a response.
- `xgene_hwmon_pcc_rd()` performs the ACPI PCC shared-memory command flow, rings the mailbox doorbell, waits for completion, and copies response words back.
- `xgene_hwmon_reg_map_rd()` reads management-processor sensor registers and rejects invalid data.
- `xgene_hwmon_get_cpu_pwr()`, `xgene_hwmon_get_io_pwr()`, and `xgene_hwmon_get_temp()` compose sensor-specific values.
- `xgene_hwmon_rx_cb()` and `xgene_hwmon_pcc_rx_cb()` route synchronous responses versus async notifications.
- `xgene_hwmon_evt_work()` drains async messages and updates alarm state through `xgene_hwmon_tpc_alarm()`.

## Control Flow
Probe allocates context, initializes locks/completion/FIFO/work, configures the mailbox client, and selects OF mailbox mode when ACPI is disabled or PCC mode when ACPI is active. PCC probing reads the `pcc-channel` property, requests the PCC mailbox channel, verifies IRQ-based txdone support, and computes a timeout from PCC latency. The driver then registers a fixed hwmon group and schedules work in case messages arrived before registration completed.

Sysfs reads build a command message and synchronously query the remote processor. Power reads fetch whole-watt and milliwatt registers, combine to milliwatts, and report microwatts. Temperature reads sign-extend the raw register and report millidegrees Celsius. Async power-management messages are queued in a kfifo from callbacks and processed in workqueue context; TPC alarm messages update `temp_critical_alarm` and notify sysfs.

## State And Persistence
The driver stores only transient synchronization state and the latest critical alarm boolean. There is no telemetry cache; every input read performs a mailbox/PCC transaction. Async messages persist only until drained from the fixed-size FIFO. PCC command state lives in ACPI shared memory during each transaction.

## Dependencies And Integration Points
It integrates with platform devices, OF compatible `apm,xgene-slimpro-hwmon`, ACPI IDs `APMC0D29`/`APMC0D8A`, ACPI PCC, mailbox framework, kfifo, workqueues, hwmon sysfs groups, and sysfs notification. It uses endianness-safe PCC shared-memory accesses and mailbox callbacks for both synchronous and asynchronous data.

## Risks
- The async FIFO is fixed at 16 messages and `kfifo_in_spinlocked()` return values are not checked, so notifications can be dropped under burst load.
- Synchronous request matching accepts several message shapes; unexpected remote firmware behavior could complete the wrong waiter.
- PCC timeout is an arbitrary multiplier of nominal latency, so slow firmware can produce false timeouts.
- `xgene_hwmon_rx_ready()` checks readiness with `IS_ERR_OR_NULL(ctx->hwmon_dev)` and `!resp_pending`; early async messages are queued, but lifecycle races around remove rely on callback quiescing from mailbox teardown.
- No telemetry cache means sysfs polling can stress firmware/mailbox paths.

## Test Signals
Validate both OF SLIMpro and ACPI PCC probe paths, missing `pcc-channel`, mailbox request failures, PCC without IRQ txdone, timeout/error responses, invalid sensor data bit handling, signed negative temperature conversion, power unit conversion, async TPC alarm notification and sysfs_notify, FIFO overflow behavior, and remove ordering with pending work/callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/xgene-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/yogafan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/yogafan.c

## Purpose
This platform hwmon driver exposes fan RPM readings for selected Lenovo Yoga, Legion, and IdeaPad laptops by evaluating ACPI EC methods matched through DMI. It applies a passive first-order lag and slew-rate limiter to smooth low-resolution EC tachometer samples.

## Important APIs, Types, And Functions
- `struct yogafan_config` describes a DMI-specific multiplier, expected fan count, and ACPI method paths.
- `struct yoga_fan_data` stores resolved ACPI handles, per-fan filtered values, per-fan last sample time, multiplier, and active fan count.
- `apply_rllag_filter()` implements raw-RPM sanitation, sampling interval gating, autoreset after long gaps, first-order lag, and slew limiting.
- `yoga_fan_read()` evaluates the ACPI method for a channel, applies scaling/filtering, and returns `hwmon_fan_input`.
- `yoga_fan_is_visible()` exposes only active fan channels.
- `yoga_fan_init()` registers the platform driver and a simple platform device only on matching DMI systems.

## Control Flow
Module init checks DMI first, registers the platform driver, and creates a platform device named `yogafan`. Probe finds the first matching DMI configuration, allocates state, resolves each configured ACPI EC path, counts only successfully resolved handles, and registers a hwmon device with `hwmon_chip_info`. Runtime fan reads evaluate the channel's ACPI object and pass the scaled raw RPM through the filter before returning it.

## State And Persistence
The only mutable state is per-fan filter state: `filtered_val[]` and `last_sample[]`. It is updated lazily on userspace reads, so there is no background polling and no persistence across unload. If raw RPM is below `RPM_FLOOR_LIMIT`, the output snaps to zero. If sampling gaps exceed `MAX_SAMPLING`, the filter resets to raw RPM.

## Dependencies And Integration Points
The driver integrates with DMI matching, ACPI handle lookup and integer evaluation, the modern hwmon `read`/`is_visible` API, platform driver/device registration, `ktime_get_boottime()`, and 64-bit division helpers. It supports up to eight fan channels in the static hwmon channel descriptor.

## Risks
- ACPI method paths are hard-coded per broad DMI product family, so firmware naming variations can leave supported systems without fans or expose only a subset.
- The filter is read-driven; sparse or very frequent polling changes smoothing behavior by design.
- No explicit locking protects filter state. Concurrent sysfs reads of the same fan can race updates.
- `fan_count` can be less than the configured count if handles fail; visibility handles this, but unexpected DMI matches may hide hardware.

## Test Signals
Validate DMI matching for Yoga/Legion/IdeaPad, ACPI handle discovery for each configured path, behavior when no handles resolve, raw 8-bit multiplier versus 16-bit dual-fan configs, filter reset on first/late sample, minimum sampling suppression, slew-rate limiting, zero snap behavior, and concurrent read race detection with lockdep/KCSAN if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/yogafan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/Kconfig

## Purpose
This Kconfig file defines the generic hardware spinlock framework menu and platform-provider options for OMAP, Qualcomm, Spreadtrum, STM32, and Allwinner sun6i-compatible hardware spinlock blocks.

## Important APIs, Types, And Functions
This is declarative Kconfig rather than C code. Key symbols are `HWSPINLOCK`, `HWSPINLOCK_OMAP`, `HWSPINLOCK_QCOM`, `HWSPINLOCK_SPRD`, `HWSPINLOCK_STM32`, and `HWSPINLOCK_SUN6I`.

## Control Flow
When `HWSPINLOCK` is enabled, the submenu exposes provider selections. Each provider has architecture or `COMPILE_TEST` dependencies. Qualcomm also selects `MFD_SYSCON`, matching its driver's ability to use syscon regmaps.

## State And Persistence
The file affects build-time configuration only. It does not create runtime state, but selected symbols determine which objects are linked and which modules can register hardware spinlock banks.

## Dependencies And Integration Points
The symbols gate the Makefile entries in the same directory. They also align with platform DT/SoC support: OMAP/TI, Qualcomm, Spreadtrum, STM32MP157, and Allwinner sun6i-class SoCs.

## Risks
- Missing architecture dependencies could expose drivers where required subsystems are unavailable.
- Too-strict dependencies could block useful compile testing or cross-platform builds.
- The core `HWSPINLOCK` is a bool, while providers are tristate, so module combinations depend on Kbuild behavior around built-in core versus modular providers.

## Test Signals
Run Kconfig matrix builds for each provider as built-in and module where allowed, plus `COMPILE_TEST`. Confirm Qualcomm pulls `MFD_SYSCON`, and that disabling `HWSPINLOCK` hides all provider options and omits the core object.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/Makefile

## Purpose
This Makefile maps hardware spinlock Kconfig symbols to the core framework object and provider driver objects.

## Important APIs, Types, And Functions
There are no functions. Build targets are `hwspinlock_core.o`, `omap_hwspinlock.o`, `qcom_hwspinlock.o`, `sprd_hwspinlock.o`, `stm32_hwspinlock.o`, and `sun6i_hwspinlock.o`.

## Control Flow
Kbuild includes `hwspinlock_core.o` when `CONFIG_HWSPINLOCK` is enabled, and includes each provider object when the corresponding provider symbol is enabled.

## State And Persistence
This file only controls build outputs. It creates no runtime state.

## Dependencies And Integration Points
It directly consumes the symbols from `drivers/hwspinlock/Kconfig`. The provider objects depend on the exported registration/request APIs from `hwspinlock_core.o`.

## Risks
- If a provider is enabled without the core object, linking would fail; the Kconfig nesting prevents that.
- Adding a provider requires updating both Kconfig and this Makefile.

## Test Signals
Validate `obj-y`/`obj-m` output with representative configs, especially built-in core with modular providers and all providers disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_core.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_core.c

## Purpose
This file implements the generic Linux hardware spinlock framework. It registers provider banks, maps global lock IDs to `struct hwspinlock` objects, lets clients request/free locks, wraps platform `trylock`/`unlock` operations with local locking and memory barriers, provides DT translation helpers, and offers devm-managed registration/request APIs.

## Important APIs, Types, And Functions
- Global registry: `RADIX_TREE(hwspinlock_tree)` maps lock IDs to lock objects; `HWSPINLOCK_UNUSED` radix-tree tag marks available locks; `hwspinlock_tree_lock` serializes mutations.
- Lock operations: `__hwspin_trylock()`, `__hwspin_lock_timeout()`, `__hwspin_unlock()`, and `hwspin_lock_bust()`.
- OF helpers: `of_hwspin_lock_get_id()` and `of_hwspin_lock_get_id_byname()`.
- Provider APIs: `hwspin_lock_register()`, `hwspin_lock_unregister()`, `devm_hwspin_lock_register()`, and `devm_hwspin_lock_unregister()`.
- Client APIs: `hwspin_lock_request_specific()`, `hwspin_lock_free()`, `devm_hwspin_lock_request_specific()`, and `devm_hwspin_lock_free()`.

## Control Flow
Providers allocate a `struct hwspinlock_device` with an array of locks and call `hwspin_lock_register()`. The core initializes each local spinlock, sets the bank pointer, inserts each lock into the radix tree, and tags it unused. Clients request a lock by ID; the core checks existence and unused tag, gets the provider module, runtime-resumes the provider device, clears the unused tag, and returns the lock. Freeing reverses the runtime PM/module reference and sets the unused tag.

Lock acquisition first optionally takes a local spinlock according to the selected mode (`HWLOCK_IRQSTATE`, `HWLOCK_IRQ`, normal, raw, or in-atomic), then calls the provider's `trylock()`. On failure it undoes local locking and returns `-EBUSY`; on success it issues `mb()`. Timeout locking loops until success or timeout, using `udelay()` for `HWLOCK_IN_ATOMIC` and optional provider `relax()`. Unlock issues a memory barrier before provider `unlock()`, then releases the local spinlock according to mode.

## State And Persistence
The registry persists while the module/core is loaded. Lock allocation state is encoded solely in the radix-tree unused tag. Runtime PM state and module reference counts are held only while a client has requested a lock, not merely while the provider exists. No lock ownership persists across unregister; unregister fails if any lock is still requested.

## Dependencies And Integration Points
The core depends on radix tree, spinlocks, mutexes, PM runtime, module ownership, OF phandle parsing, and provider callbacks defined in `hwspinlock_internal.h`. Public wrappers in `<linux/hwspinlock.h>` call the exported internal functions here.

## Risks
- `hwspin_lock_register_single()` computes `ret` from `radix_tree_insert()` but returns `0` even on insertion failure because it falls through `out` with a constant return. That can hide duplicate-ID or allocation failures and leave partial registration inconsistent.
- Lock request/free correctness depends on the radix-tree tag meaning "unused"; any path that forgets to update it breaks allocation and unregister safety.
- `HWLOCK_RAW` and `HWLOCK_IN_ATOMIC` skip local spinlock protection, pushing serialization responsibility to callers.
- Timeout arithmetic converts milliseconds to jiffies; very small timeouts in non-atomic mode are coarse.
- OF lookup iterates the radix tree under RCU while provider unregister uses the tree mutex; the code follows radix-tree RCU patterns but should be stress-tested with probe/remove races.

## Test Signals
Test provider registration/unregistration, duplicate ID handling, allocation failure injection in radix-tree insert, request/free reference and PM runtime accounting, unregister while locks are requested, all lock modes including IRQ save validation, timeout paths, provider `relax()` calls, bust support/no-support, OF ID and name translation including `-EPROBE_DEFER`, and devm cleanup ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_internal.h -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_internal.h

## Purpose
This internal header defines the provider-facing hardware spinlock structures and callback contract used by the core and all platform provider drivers.

## Important APIs, Types, And Functions
- `struct hwspinlock_ops` defines provider callbacks: mandatory `trylock()` and `unlock()`, optional `bust()` and `relax()`.
- `struct hwspinlock` represents a single lock, with owning bank, local spinlock, and provider private pointer.
- `struct hwspinlock_device` represents a bank, with device pointer, ops, base ID, number of locks, and a flexible lock array.
- `hwlock_to_id()` computes the global ID from a lock pointer and bank base ID.

## Control Flow
Provider drivers allocate a `hwspinlock_device` large enough for all locks, fill each lock's `priv`, and register the bank with the core. The core fills the bank metadata and uses `hwlock_to_id()` for registry and client operations.

## State And Persistence
The structures define in-memory runtime state only. `priv` is owned by providers and usually points to MMIO addresses, regmap fields, or provider-specific lock resources.

## Dependencies And Integration Points
The header is included by `hwspinlock_core.c` and provider drivers. It depends on Linux spinlock and device types and complements the public `<linux/hwspinlock.h>` API.

## Risks
- `hwlock_to_id()` assumes `hwlock` points inside `bank->lock[]`; invalid pointers produce undefined IDs.
- Provider `trylock()` and `unlock()` must not sleep, but the type system cannot enforce that.
- The flexible array requires correct `struct_size()` allocation by providers.

## Test Signals
Provider compile tests should verify correct allocation sizes, `priv` initialization for every lock, base ID calculations, and static analysis for sleeping calls inside provider callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/hwspinlock_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/omap_hwspinlock.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/omap_hwspinlock.c

## Purpose
This provider driver registers TI OMAP/AM/K3 hardware spinlock blocks with the generic hwspinlock framework.

## Important APIs, Types, And Functions
- Register layout constants include `SYSSTATUS_OFFSET`, `LOCK_BASE_OFFSET`, and `SPINLOCK_NUMLOCKS_BIT_OFFSET`.
- `omap_hwspinlock_trylock()` acquires a lock by reading its register and checking for `SPINLOCK_NOTTAKEN`.
- `omap_hwspinlock_unlock()` releases by writing zero.
- `omap_hwspinlock_relax()` delays 50 ns while polling.
- `omap_hwspinlock_probe()` maps MMIO, enables runtime PM, determines lock count, initializes per-lock MMIO pointers, and registers the bank.

## Control Flow
Probe maps the resource, enables runtime PM, resumes the device to read `SYSSTATUS`, then puts it so runtime PM can gate the module when no locks are requested. The high SYSSTATUS bits encode a one-hot lock-bank count; the driver validates it and multiplies by 32 to get the number of locks. Each lock's `priv` points at its lock register. The provider is registered at base ID 0 during a `postcore_initcall`.

## State And Persistence
State consists of the hwspinlock bank and per-lock MMIO addresses. Runtime PM state is managed by the core while locks are requested. The hardware lock state lives in the SoC lock registers.

## Dependencies And Integration Points
The driver depends on platform MMIO resources, OF compatibles `ti,omap4-hwspinlock`, `ti,am64-hwspinlock`, `ti,am654-hwspinlock`, runtime PM, and the hwspinlock core.

## Risks
- The lock count decode accepts only one bit in the low nibble after shifting and `i <= 8`; wrong SYSSTATUS interpretation prevents probe.
- Base ID is fixed at 0 and only one block is supported.
- Read-to-lock semantics are hardware-specific and must not be "optimized" into ordinary status reads elsewhere.

## Test Signals
Validate probe on supported compatibles, SYSSTATUS lock-count variants, invalid count rejection, runtime PM transitions, trylock/unlock register semantics, relax callback use during timeout, and early boot registration ordering for board reservations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/omap_hwspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/qcom_hwspinlock.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/qcom_hwspinlock.c

## Purpose
This provider driver exposes Qualcomm hardware mutex blocks as 32 generic hwspinlocks. It supports both syscon-backed regmaps and direct MMIO regmaps for several Qualcomm mutex layouts.

## Important APIs, Types, And Functions
- `struct qcom_hwspinlock_of_data` describes offset, stride, and optional MMIO regmap configuration.
- `qcom_hwspinlock_trylock()` writes the APPS processor owner ID and reads back the owner to confirm acquisition.
- `qcom_hwspinlock_unlock()` verifies ownership and writes zero.
- `qcom_hwspinlock_bust()` clears a lock only when the current owner matches a caller-provided ID.
- `qcom_hwspinlock_probe_syscon()` parses a `syscon` phandle plus offset/stride cells.
- `qcom_hwspinlock_probe_mmio()` maps MMIO and creates a regmap from match data.
- `qcom_hwspinlock_probe()` allocates regmap fields for all 32 locks and registers the bank.

## Control Flow
Probe first tries the syscon path; if the phandle is absent it falls back to direct MMIO using compatible-specific offset/stride/config. For each lock it creates a full 32-bit `regmap_field` at `base + i * stride` and stores it in `lock[i].priv`. The provider registers 32 locks at base ID 0 during `postcore_initcall`.

## State And Persistence
The bank stores per-lock `regmap_field` handles. Hardware ownership is encoded as a processor ID in each mutex register. The driver uses APPS processor ID 1 for acquisition and release.

## Dependencies And Integration Points
It depends on platform devices, OF match data, syscon/regmap, optional MMIO resources, `MFD_SYSCON` from Kconfig, and the hwspinlock core.

## Risks
- Ownership ID is hard-coded to `QCOM_MUTEX_APPS_PROC_ID`; platforms with different APPS IDs would fail or mis-own locks.
- Unlock logs an error if not owner but still writes zero, which can clear another owner's lock.
- Syscon property parsing requires offset and stride in cells 1 and 2; malformed bindings fail probe.
- Base ID 0 and fixed 32-lock count assume one mutex bank instance.

## Test Signals
Validate syscon and MMIO probe paths, all compatible offset/stride values, regmap field allocation failures, trylock ownership readback, unlock when owned/not owned, bust matching and non-matching owner IDs, duplicate provider registration behavior, and postcore registration timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/qcom_hwspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/sprd_hwspinlock.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/sprd_hwspinlock.c

## Purpose
This provider driver registers Spreadtrum hardware spinlock blocks with 32 token registers and optional user/master ID recording.

## Important APIs, Types, And Functions
- `struct sprd_hwspinlock_dev` contains MMIO base, enable clock, and embedded `hwspinlock_device`.
- `sprd_hwspinlock_trylock()` reads the token register; zero means acquired. On failure it reads the master/user ID register and logs the owner.
- `sprd_hwspinlock_unlock()` writes the magic not-taken value `0x55aa10c5`.
- `sprd_hwspinlock_relax()` delays 10 ns while polling.
- `sprd_hwspinlock_probe()` maps MMIO, enables the clock, enables user ID recording, initializes token addresses, and registers 32 locks.

## Control Flow
Probe requires an OF node, allocates the provider structure with room for 32 locks, maps the register block, gets and enables the `enable` clock, registers a devm cleanup action, writes `HWSPINLOCK_USER_BITS` to `RECCTRL`, stores each token register address in `lock->priv`, sets drvdata, and registers the bank at base ID 0.

## State And Persistence
Runtime state is the enabled clock, MMIO base, and bank. The hardware records ownership information when configured. The cleanup action disables the clock on driver detach or probe failure.

## Dependencies And Integration Points
It depends on OF platform probing, an `enable` clock, MMIO resources, devm actions, and the hwspinlock core. Compatible string is `sprd,hwspinlock-r3p0`.

## Risks
- Failure logging in `trylock()` can be noisy because every unsuccessful poll may emit a warning with owner ID.
- Base ID and lock count are fixed, limiting multi-bank support.
- The hardware-specific token semantics are non-obvious: read zero for success and write a magic value for unlock.

## Test Signals
Validate clock acquisition/cleanup, RECCTRL write, token address mapping, trylock success/failure owner reporting, unlock magic write, timeout polling with relax, OF-only probe rejection, and devm unwind on registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/sprd_hwspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/stm32_hwspinlock.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/stm32_hwspinlock.c

## Purpose
This provider driver exposes STM32 hardware semaphores as 32 generic hardware spinlocks.

## Important APIs, Types, And Functions
- `struct stm32_hwspinlock` stores the semaphore clock and embedded hwspinlock bank.
- `stm32_hwspinlock_trylock()` writes lock bit plus core ID and succeeds only if the register reads back the same value.
- `stm32_hwspinlock_unlock()` writes the core ID without the lock bit.
- `stm32_hwspinlock_relax()` delays 50 ns.
- Runtime PM callbacks disable and enable the semaphore clock.
- `stm32_hwspinlock_probe()` maps MMIO, enables the `hsem` clock, initializes runtime PM, stores per-lock register addresses, and registers the bank.

## Control Flow
Probe maps the register block, allocates the bank, gets/prepares/enables the clock, marks the device runtime-active, registers a devm cleanup action for runtime PM and clock teardown, fills 32 `priv` MMIO pointers, and calls `devm_hwspin_lock_register()`. Registration is performed from `postcore_initcall`.

## State And Persistence
The driver stores only clock and bank state. Runtime PM gates the clock according to core request/free activity. Hardware lock ownership is encoded in each semaphore register using lock bit and core ID.

## Dependencies And Integration Points
It depends on platform MMIO, OF compatible `st,stm32-hwspinlock`, clock `hsem`, runtime PM, and the hwspinlock core.

## Risks
- `STM32_MUTEX_COREID` is hard-coded as bit 8, so the driver assumes a fixed Linux core/processor identity for ownership.
- Runtime PM cleanup calls `pm_runtime_get_sync()` without checking its return, which is common in cleanup but can hide suspend/resume errors.
- Base ID and 32-lock count are fixed.

## Test Signals
Validate clock enable/disable, runtime suspend/resume, trylock readback semantics, unlock write, registration failure cleanup, OF matching, and early registration availability for clients.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/stm32_hwspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/sun6i_hwspinlock.c -->
# sources/distributed-fs/ceph-client/drivers/hwspinlock/sun6i_hwspinlock.c

## Purpose
This provider driver registers Allwinner sun6i-compatible hardware spinlock blocks with the generic hwspinlock framework. It also exposes a debugfs file reporting the detected lock count when debugfs is enabled.

## Important APIs, Types, And Functions
- `struct sun6i_hwspinlock_data` stores the bank pointer, reset control, AHB clock, debugfs dentry, and detected lock count.
- `sun6i_hwspinlock_trylock()` acquires by reading the lock register and checking for zero.
- `sun6i_hwspinlock_unlock()` releases by writing zero.
- `sun6i_hwspinlock_debugfs_init()` creates `sun6i_hwspinlock/supported` under debugfs when configured.
- `sun6i_hwspinlock_probe()` handles reset/clock setup, decodes lock count from `SYSSTATUS`, initializes per-lock MMIO addresses, registers cleanup, and registers the bank.

## Control Flow
Probe maps MMIO resource 0, allocates private data, gets the `ahb` clock and reset, deasserts reset, enables the clock, decodes `num_banks` from bits 28 and above of `SYSSTATUS`, maps values 1..4 to 32..256 locks, allocates a flexible bank for that count, fills lock register addresses, initializes debugfs, installs a cleanup action, sets drvdata, and registers the bank with base ID 0.

## State And Persistence
State includes clock/reset enablement, debugfs entry, dynamic lock count, and lock MMIO pointers. Cleanup removes debugfs, disables the clock, and asserts reset. Hardware lock state is volatile in the lock registers.

## Dependencies And Integration Points
It depends on platform MMIO resources, OF compatible `allwinner,sun6i-a31-hwspinlock`, reset controls, AHB clock, optional debugfs, and the hwspinlock core.

## Risks
- Lock count decoding works around inconsistent datasheets; future SoCs may encode unsupported values.
- No `relax()` callback is provided, so timeout loops use only the core's retry behavior.
- Debugfs creation failure is non-fatal and normalized to NULL, so diagnostics may silently be absent.
- Fixed base ID 0 assumes a single bank per SoC.

## Test Signals
Validate reset/clock sequencing, SYSSTATUS decode for 32/64/128/256 locks and invalid values, debugfs supported count, devm cleanup on each failure point, trylock/unlock semantics, and registration with dynamic lock counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwspinlock/sun6i_hwspinlock.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/Kconfig

## Purpose
This top-level Kconfig file creates the `HW tracing support` menu and includes hardware tracing subsystem Kconfig files for STM, Intel TH, and PTT.

## Important APIs, Types, And Functions
This is declarative Kconfig. It sources `drivers/hwtracing/stm/Kconfig`, `drivers/hwtracing/intel_th/Kconfig`, and `drivers/hwtracing/ptt/Kconfig`.

## Control Flow
When Kconfig processes this file, it opens a menu, sources the three tracing subsystem configurations, and closes the menu. It does not directly define a symbol.

## State And Persistence
Only build-time menu organization is affected. Runtime state is created by whichever sourced tracing drivers are enabled.

## Dependencies And Integration Points
It integrates with the broader drivers Kconfig hierarchy and delegates all actual symbol definitions to child Kconfig files.

## Risks
- CoreSight is not sourced here in this tree version, so it must be included elsewhere or it will be absent from the top-level hwtracing menu.
- A bad source path breaks Kconfig parsing for the whole menu.

## Test Signals
Run menuconfig/listnewconfig to confirm STM, Intel TH, and PTT options appear under hardware tracing support, and verify CoreSight inclusion from the expected parent if required by this source tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Kconfig

## Purpose
This Kconfig file defines the Arm CoreSight tracing framework and its component drivers, including links, sinks, sources, trace buffers, CTI/CTM, STM integration, TPDM/TPDA, TNOC, dummy devices, and KUnit tests.

## Important APIs, Types, And Functions
This is declarative Kconfig. Major symbols include `CORESIGHT`, `CORESIGHT_LINKS_AND_SINKS`, `CORESIGHT_LINK_AND_SINK_TMC`, `CORESIGHT_CATU`, `CORESIGHT_SINK_TPIU`, `CORESIGHT_SINK_ETBV10`, `CORESIGHT_SOURCE_ETM3X`, `CORESIGHT_SOURCE_ETM4X`, `ETM4X_IMPDEF_FEATURE`, `CORESIGHT_STM`, `CORESIGHT_CTCU`, `CORESIGHT_CPU_DEBUG`, `CORESIGHT_CPU_DEBUG_DEFAULT_ON`, `CORESIGHT_CTI`, `CORESIGHT_CTI_INTEGRATION_REGS`, `CORESIGHT_TRBE`, `ULTRASOC_SMB`, `CORESIGHT_TPDM`, `CORESIGHT_TPDA`, `CORESIGHT_DUMMY`, `CORESIGHT_KUNIT_TESTS`, and `CORESIGHT_TNOC`.

## Control Flow
`menuconfig CORESIGHT` gates the rest of the file. The framework depends on ARM or ARM64, and OF or ACPI, and selects AMBA, perf events, and configfs support. Child symbols add component-specific dependencies and select related support where needed, such as ETM sources selecting links/sinks, ETM4 selecting `PID_IN_CONTEXTIDR`, STM selecting the generic `STM` subsystem, TPDM selecting TPDA, and KUnit tests defaulting under `KUNIT_ALL_TESTS`.

## State And Persistence
The file affects build-time symbol selection. Runtime CoreSight topology, trace sessions, sysfs/configfs state, perf integration, and device registrations are implemented by the object files selected here.

## Dependencies And Integration Points
It ties CoreSight to ARM/ARM64, OF/ACPI firmware descriptions, AMBA bus support, perf, configfs, debugfs for CPU debug, KUnit for tests, and component-specific dependencies such as TMC for CATU/CTCU and ETM4 for TRBE.

## Risks
- Symbol dependency mistakes can produce unusable trace topologies, such as sources without viable links/sinks or sinks without the framework.
- Several options are tristate and interdependent; module/built-in combinations need link and runtime testing.
- `CORESIGHT_CTI_INTEGRATION_REGS` intentionally exposes integration registers that can leave devices inconsistent, so it should remain gated and documented.
- `CORESIGHT_CPU_DEBUG_DEFAULT_ON` changes boot-time debug behavior and must be treated as a policy-sensitive option.

## Test Signals
Validate Kconfig combinations for ARM and ARM64, OF-only and ACPI-enabled builds, modular and built-in component combinations, ETM3 exclusion on ARM64, ETM4/TRBE dependencies, KUnit selection defaults, and that Makefile object selection matches every visible symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Makefile

## Purpose
This Makefile builds the CoreSight framework and component drivers selected by CoreSight Kconfig symbols, while enabling an elevated warning set for this subdirectory.

## Important APIs, Types, And Functions
There are no runtime functions. Important build aggregates include `coresight-y`, `coresight-tmc-y`, `coresight-etm3x-y`, `coresight-etm4x-y`, `coresight-cti-y`, and `coresight-ctcu-y`. It also sets `CFLAGS_coresight-stm.o := -D__DISABLE_TRACE_MMIO__`.

## Control Flow
Kbuild adds warning flags through `subdir-ccflags-y`, conditionally adds supported compiler warning flags through `cc-option`, and maps each `CONFIG_CORESIGHT_*` symbol to either a single object or a multi-object module. The base `CONFIG_CORESIGHT` target builds the core framework pieces, including platform, sysfs, syscfg/configfs, perf, trace ID, and preloaded configurations.

## State And Persistence
The file only controls compilation and linking. It does not define runtime state, but its object grouping determines module boundaries and which init/exit paths are linked together.

## Dependencies And Integration Points
It consumes symbols from `drivers/hwtracing/coresight/Kconfig`. It integrates with the kernel build system's per-directory CFLAGS, compiler feature probing, composite object syntax, and CoreSight component source files.

## Risks
- Kconfig/Makefile drift can leave a visible config symbol with no object or an object built under the wrong symbol.
- Stricter warning flags can break builds on compiler versions not covered by `cc-option`; unconditional flags must remain broadly supported.
- Composite object membership controls module contents, so missing a source file can produce runtime registration gaps even when the module builds.
- The STM-specific `__DISABLE_TRACE_MMIO__` define changes instrumentation behavior and must stay limited to `coresight-stm.o`.

## Test Signals
Run build matrix checks for each CoreSight symbol, `W=1` style warning coverage, GCC and Clang support for conditional flags, module contents for composite targets, and KUnit build inclusion under `CONFIG_CORESIGHT_KUNIT_TESTS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwtracing/coresight/Makefile -->
