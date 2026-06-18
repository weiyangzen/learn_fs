# subset-b-003895 research

Grouped research for Linux IIO light, UV, color, and proximity drivers under `sources/distributed-fs/ceph-client/drivers/iio/light`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl76682.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/isl76682.c

## Purpose
`isl76682.c` is a direct-mode IIO I2C driver for the Renesas/Intersil ISL76682 ambient light sensor. It exposes one illuminance channel and one infrared intensity channel, both backed by the same 16-bit ALS/IR data registers and selected by programming the command register before a read.

## Important APIs, types, and functions
`struct isl76682_chip` holds the regmap, a mutex, the selected range, and a cached command byte. `struct isl76682_range` maps hardware range selectors to IIO scale values for visible and IR modes. `isl76682_get()` is the central acquisition helper: it enables continuous conversion, switches ALS versus IR mode, waits `ISL76682_CONV_TIME_MS` after command changes, then bulk-reads the two data bytes. `isl76682_read_raw()`, `isl76682_write_raw()`, and `isl76682_read_avail()` implement raw, scale, integration-time, and scale-available IIO callbacks. `isl76682_clear_configure_reg()` powers/configures the chip down to a known state and is also registered as a devm cleanup action.

## Control flow
Probe allocates an IIO device, initializes regmap with a small flat cache and volatile data registers, sets the default 1 klux range, clears the command register, registers reset cleanup, and publishes `isl76682_channels` in `INDIO_DIRECT_MODE`. Reads take the mutex, select the requested mode if necessary, possibly sleep for a conversion, and return the raw 16-bit sample. Scale writes validate that `val` is zero and `val2` exactly matches one of the per-channel scale entries, then update only the cached `range`; the actual command byte is written lazily on the next sample.

## State and persistence
The driver persists only in-memory range and command state plus the device command register. Hardware range/mode settings last until the next register write or reset; the driver does not store settings across reboot. The lock keeps command register updates, mode selection, and the range cache coherent. On remove or probe failure after action registration, the command register is cleared best-effort.

## Dependencies and integration points
The file integrates with the I2C core, OF matching for `isil,isl76682`, regmap, managed IIO registration, and the IIO direct-mode ABI for `in_illuminance_raw`, `in_intensity_raw`, scale attributes, and shared integration time. It uses `guard()`/`scoped_guard()` cleanup helpers for mutex handling.

## Risks
Scale changes are deferred until the next read, so userspace may observe the new scale before the device command register has been rewritten. `regmap_bulk_read()` reads directly into an `int *` buffer for two bytes, relying on the low bytes being populated as intended. If a command write fails, the cached command remains old; after cleanup failure it is deliberately forced to zero as a best-effort recovery assumption. The 100 ms sleep occurs under the mutex and can serialize concurrent readers.

## Test signals
Build with `CONFIG_ISL76682` or allmodconfig-style IIO coverage. Runtime tests should check both channels, all four ALS and IR scales, invalid scale rejection, fixed 90 ms integration time reporting, command rewrite after ALS/IR switching, and best-effort power-down on driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/isl76682.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/jsa1212.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/jsa1212.c

## Purpose
`jsa1212.c` is an IIO I2C/regmap driver for the JSA1212 ambient light and proximity sensor. It exposes direct raw ALS and proximity channels, plus ALS scale derived from the configured ALS range.

## Important APIs, types, and functions
`struct jsa1212_data` stores the I2C client, mutex, regmap, ALS range index, and booleans tracking whether ALS or proximity was enabled. `jsa1212_als_enable()` and `jsa1212_pxs_enable()` update the configuration register and mirror enable state. `jsa1212_read_als_data()` and `jsa1212_read_pxs_data()` enable a function, wait for output, read the data register(s), and disable the function. `jsa1212_read_raw()` routes IIO raw and scale reads. `jsa1212_chip_init()` programs proximity sleep/current defaults and ALS interrupt persistence. PM callbacks call `jsa1212_power_off()` and then restore previously enabled functions in `jsa1212_resume()`.

## Control flow
Probe allocates an unmanaged IIO device, initializes an RBTREE regmap with volatile data/status registers, seeds chip defaults, fills channel metadata, and registers the IIO device. Raw reads take the mutex, temporarily enable the requested block, sleep 200 ms for ALS or 100 ms for proximity, read data, then disable the block. Remove unregisters the IIO device and powers off both functional blocks. System suspend powers off; resume checks the cached enable booleans and re-enables functions that were logically active.

## State and persistence
Driver-visible state is the regmap cache, ALS range index, and enable booleans. The hardware is normally left disabled after each direct read, even though `als_en` or `pxs_en` may briefly become true during the helper. Configuration writes persist in the device until reset or power loss. The driver has no userspace write path for range, thresholds, or interrupts despite defining many register constants.

## Dependencies and integration points
The file integrates with I2C, ACPI match ID `JSA1212`, regmap caching, simple sleep PM, and the IIO direct-mode ABI. It uses raw sysfs-style IIO channels rather than triggered buffers or event support.

## Risks
`jsa1212_read_als_data()` returns the result of disabling ALS even if the preceding read failed, so an I/O error from the data read can be masked by a successful disable. The same pattern exists for proximity. The 12-bit ALS value is not explicitly masked after little-endian conversion. Resume semantics are weak because the read helpers disable blocks and update enable booleans, so cached "wanted" state may not represent a long-term user configuration. The TODO list notes missing interrupt, threshold, and range support.

## Test signals
Compile with IIO and PM enabled. Exercise ACPI/I2C probe, regmap init failure, raw ALS/proximity reads, sleep delays, power-off on remove/suspend, resume after a forced enabled state, ALS scale reporting, and negative tests for unsupported write/event attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/jsa1212.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/lm3533-als.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/lm3533-als.c

## Purpose
`lm3533-als.c` is the ALS child driver for the TI LM3533 MFD. It exposes ambient-light ADC readings, current-output mapper values for three output channels across five zones, zone threshold attributes, and threshold events through IIO.

## Important APIs, types, and functions
`struct lm3533_als` stores the parent `struct lm3533`, platform device, IRQ, interrupt-enabled flag, cached zone, and threshold mutex. `lm3533_als_get_adc()`, `_lm3533_als_get_zone()`, `lm3533_als_get_current()`, and `lm3533_als_read_raw()` implement raw/average ALS and current channel reads. Target-current helpers calculate `LM3533_REG_ALS_TARGET_BASE + 5 * channel + zone`. Threshold helpers read/write boundary registers, enforce falling <= raising with `thresh_mutex`, and expose hysteresis. `lm3533_als_isr()` clears the interrupt by reading zone info, updates the cached zone, and pushes an IIO threshold event. Probe configures platform-data input mode/resistor, optionally requests IRQ, enables ALS, and registers the IIO device.

## Control flow
The platform driver is created by the LM3533 MFD. Probe requires parent drvdata and `lm3533_als_platform_data`, builds the IIO channels, sets the parent device, initializes the zone cache, optionally disables and requests the shared IRQ, applies analog/PWM input setup, enables the ALS block, and registers IIO. Runtime raw reads use parent MFD read/update helpers. Sysfs event and extended attributes are backed by custom `device_attribute` wrappers rather than only standard event callbacks. Remove disables interrupt mode, unregisters IIO, disables ALS, and frees the IRQ.

## State and persistence
The LM3533 register map is the persistent hardware state. The driver caches only zone when interrupt mode is active and keeps threshold writes serialized. Current targets, thresholds, input mode, resistor selection, and ALS enable state are written directly to the parent device and remain until changed or reset. `LM3533_ALS_FLAG_INT_ENABLED` decides whether zone reads use the cached interrupt-updated value or poll hardware.

## Dependencies and integration points
This driver depends on the LM3533 MFD API (`lm3533_read`, `lm3533_write`, `lm3533_update`), platform data, platform-driver binding, IRQ support, IIO events, and legacy custom IIO sysfs attributes. It integrates the ALS mapper with backlight/current outputs through output current channels.

## Risks
Probe is platform-data-only and returns `-EINVAL` without it, limiting firmware-description flexibility. Interrupt enable changes update the local flag before the hardware write; error recovery clears the flag only for some cases. Threshold writes must preserve non-negative hysteresis, so tests need boundary-order coverage. IRQ handling always returns handled even if zone read failed. The custom attribute matrix is large and easy to regress during IIO ABI cleanups.

## Test signals
Build with LM3533 MFD and IIO event support. Probe tests should cover missing parent data, missing platform data, IRQ and no-IRQ paths, PWM versus analog setup, invalid resistor values, and enable failure cleanup. Runtime tests should cover raw/average ADC, output current per channel/zone, zone reads with and without interrupt mode, threshold ordering rejection, event enable toggling, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/lm3533-als.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltr390.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/ltr390.c

## Purpose
`ltr390.c` is an IIO I2C/regmap driver for the Lite-On LTR390 ALS and UV sensor. It exposes UV index and visible-light raw readings, scale, integration time, sampling frequency, threshold events, debugfs register access, and runtime PM.

## Important APIs, types, and functions
`struct ltr390_data` stores regmap, client, mutex, current ALS/UVS mode, gain, integration time, and IRQ power state. `ltr390_register_read()` reads 24-bit little-endian sample or threshold values. `ltr390_set_mode()` switches between ALS and UVS mode. `ltr390_do_read_raw()` implements raw, scale, integration-time, and sampling-frequency reads; `ltr390_read_raw()` wraps it in runtime PM. `ltr390_set_gain()`, `ltr390_set_int_time()`, and `ltr390_set_samp_freq()` program configuration fields. Event helpers read/write 24-bit thresholds, persistence period, and interrupt enable/channel select. `ltr390_interrupt_handler()` clears status and pushes a light or UV threshold event depending on cached mode.

## Control flow
Probe initializes regmap access tables, default gain/integration/mode state, verifies the high nibble of `PART_ID`, issues software reset, enables the sensor, registers a devm powerdown action, optionally requests a threaded IRQ, initializes autosuspend runtime PM, and registers IIO. Direct reads resume the device, lock around mode changes and register access, then autosuspend. Enabling an event resumes the device and holds it active while IRQs are enabled; disabling the last event releases the runtime PM reference.

## State and persistence
The driver keeps cached gain, integration time, mode, and IRQ-enabled state in RAM. Register configuration persists in hardware while powered. Runtime suspend clears the sensor enable bit; runtime resume sets it. `ltr390_powerdown()` disables interrupts if needed and clears sensor enable. Thresholds and persistence settings live in device registers.

## Dependencies and integration points
The file integrates with I2C, OF compatible `liteon,ltr390`, regmap access tables, PM runtime/system sleep callbacks, IIO event callbacks, direct-mode sysfs, and debugfs register access. It relies on `linux/unaligned.h` for 24-bit samples.

## Risks
`ltr390_read_event_config()` uses `FIELD_GET()` with a single-bit value rather than a mask expression, which deserves scrutiny. Threshold writes bulk-write three bytes from an `int` object, relying on host byte layout for little-endian register order. Event enable stores a PM runtime reference; failed paths after enabling IRQ state need careful balance. The interrupt handler chooses event type from cached `data->mode`, so concurrent mode changes can affect attribution.

## Test signals
Compile with PM, IIO events, and debugfs. Runtime tests should cover part ID warning, reset/enable path, raw ALS/UV reads, all gain/integration/frequency choices, invalid writes, threshold read/write byte order, event enable/disable PM balance, interrupt event attribution, runtime/system suspend, and debugfs reg access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltr390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltr501.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/ltr501.c

## Purpose
`ltr501.c` supports Lite-On LTR501/LTR559 ambient light plus proximity sensors and LTR301/LTR303 light-only variants. It exposes processed lux, raw ALS visible/IR intensity, raw proximity, scale, integration time, sampling frequency, threshold events, a proximity `nearlevel` property, and triggered buffers.

## Important APIs, types, and functions
`struct ltr501_chip_info` describes per-variant part ID, gain tables, active bits, channels, and IIO info with or without IRQ events. `struct ltr501_data` stores regmap, register fields, cached control bytes, sampling periods, locks for ALS/PS, and near-level property. `ltr501_calculate_lux()` converts visible/IR samples. `ltr501_drdy()` polls status readiness. Raw/procesed paths use `ltr501_read_als()`, `ltr501_read_ps()`, `ltr501_read_info_raw()`, and `ltr501_read_raw()`. `__ltr501_write_raw()` handles gain, integration time, and sampling frequency writes, including persistence count recalculation. Event helpers manage ALS/PS thresholds, interrupt enable fields, and persistence periods. `ltr501_trigger_handler()` fills IIO buffers; `ltr501_interrupt_handler()` pushes threshold events.

## Control flow
Probe creates regmap and regmap fields, enables `vdd`/`vddio`, identifies the variant from I2C ID or ACPI data, validates the hardware part ID high nibble, reads the optional `proximity-near-level` property, initializes active ALS/PS modes and persistence periods, requests IRQ if available, sets up a triggered buffer, and registers IIO. Direct raw reads claim direct mode to avoid buffer races. Buffer capture waits for data-ready bits for active scan channels and pushes selected samples with timestamps. Suspend powers down by clearing cached active bits; resume restores cached control bytes.

## State and persistence
Cached `als_contr` and `ps_contr` mirror control register state and are modified by gain writes. `als_period` and `ps_period` preserve requested event persistence periods across sampling-frequency changes. Regmap caches nonvolatile configuration while sample/status registers are volatile. Hardware settings persist until powerdown/reset, while regulators are managed by devm bulk enable.

## Dependencies and integration points
The driver integrates with I2C, OF, ACPI IDs, regulators, regmap fields, IIO direct mode, events, trigger consumers, triggered buffers, and device properties. It uses distinct info/channel tables to hide proximity support for LTR301/LTR303 and hide event callbacks when no IRQ is present.

## Risks
The variant matrix mixes light-only and proximity devices; wrong match data can expose nonexistent channels. `ltr501_write_raw()` updates cached control bytes before register writes and may leave cache optimistic on failure. Sampling-frequency writes roll back the rate if persistence update fails, but not every intermediate state is externally invisible. `ltr501_drdy()` can block up to about 2.5 seconds. Threshold bulk writes use an `int` object for two register bytes, so endian assumptions matter. `ltr501_show_*_scale_avail()` rewrites `buf[len - 1]`, assuming at least one printable scale.

## Test signals
Build with regulators, IIO buffers, and events. Probe tests should cover all four IDs, ACPI match data, regulator failure, part ID mismatch, IRQ/no-IRQ info selection, and near-level property. Runtime tests should cover processed lux math, raw channel ordering, gain tables including reserved LTR559 entries, integration-time constraints, sample frequency rollback, threshold/event period read/write, triggered buffer scans, suspend/resume powerdown, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltr501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltrf216a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/ltrf216a.c

## Purpose
`ltrf216a.c` is an IIO I2C/regmap driver for Lite-On LTRF216A and LTR308 ambient light sensors. It provides raw ALS counts, processed lux, integration-time selection, runtime PM, and chip-specific handling for optional clear-data registers and lux multipliers.

## Important APIs, types, and functions
`struct ltr_chip_info` indicates whether clear-data registers exist and which lux multiplier to use. `struct ltrf216a_data` stores regmap, client, chip info, current integration time/factors, gain factor, and a mutex. `ltrf216a_reset()`, `ltrf216a_enable()`, `ltrf216a_disable()`, and `ltrf216a_cleanup()` manage power state. `ltrf216a_set_int_time()` programs `ALS_MEAS_RES` and updates conversion factors. `ltrf216a_set_power_state()` wraps runtime PM references. `ltrf216a_read_data()` polls data-ready and reads 24-bit little-endian samples. `ltrf216a_get_lux()` combines PM, raw green data, and chip multiplier.

## Control flow
Probe allocates IIO state, initializes regmap with custom readable/writeable/volatile/precious callbacks, stores match data, resets the sensor, reinitializes the regmap cache, enables ALS, registers a cleanup action, enables runtime PM autosuspend, seeds default integration/gain factors, and registers IIO. Raw reads runtime-resume the device, lock around data read, then autosuspend. Processed reads lock, call the lux helper, and return a fractional value using gain and integration factors. Runtime suspend disables the sensor and switches regmap to cache-only; runtime resume syncs the cache and re-enables ALS.

## State and persistence
Integration time, integration factor, and gain factor are cached in RAM. Register settings are preserved by regmap cache while runtime-suspended and synchronized on resume. Hardware state is disabled during autosuspend and on cleanup. `MAIN_STATUS` is marked precious, preventing debug-style reads from accidentally clearing or altering status semantics.

## Dependencies and integration points
The driver integrates with I2C IDs, OF compatibles `liteon,ltr308`, `liteon,ltrf216a`, and `ltr,ltrf216a`, regmap cache-only runtime PM, IIO direct-mode attributes, and unaligned 24-bit helpers.

## Risks
`ltrf216a_get_lux()` does not call `ltrf216a_set_power_state(false)` if `ltrf216a_read_data()` fails, which can leak a runtime PM reference and leave the device active. The processed path nests PM control inside the mutex, while raw path takes PM before locking. Regmap callbacks consult `i2c_get_clientdata()` and chip info, so callback timing before clientdata initialization is important. The reset write intentionally ignores errors.

## Test signals
Compile with runtime PM and regmap. Runtime tests should cover LTR308 versus LTRF216A register visibility, all integration-time writes, raw and processed reads, data-ready timeout, runtime suspend/resume cache sync, cleanup disable, and the error path in `ltrf216a_get_lux()` for PM reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/ltrf216a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/lv0104cs.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/lv0104cs.c

## Purpose
`lv0104cs.c` is a direct IIO I2C driver for the ON Semiconductor LV0104CS ambient light sensor. It exposes processed lux plus calibration scale, measurement scale, and integration-time controls.

## Important APIs, types, and functions
`struct lv0104cs_private` stores the I2C client, mutex, and selected calibration/scale/integration indexes. Mapping tables encode calibration sensitivity values, measurement scale multipliers, and integration times. `lv0104cs_write_reg()` and `lv0104cs_read_adc()` use raw `i2c_master_send()`/`i2c_master_recv()` because the chip uses command bytes rather than a conventional register map. `lv0104cs_get_lux()` programs a measurement command, sleeps for the selected integration time plus margin, reads a big-endian 16-bit ADC value, sends sleep, and converts by the selected scale. Write helpers validate calibration/scale/time and update state or hardware.

## Control flow
Probe allocates IIO state, initializes defaults to unity calibration, 1x scale, and 200 ms integration time, writes the unity calibration command, fills one light channel, and registers IIO. Processed reads lock the device, perform a full one-shot measurement, then return integer-plus-micro lux. Calibration writes round to the nearest quantized calibration entry and immediately write the corresponding command; scale and integration writes only update cached indexes used by the next measurement.

## State and persistence
Calibration is programmed into hardware immediately and cached by index. Scale and integration time are driver-side command components that persist in RAM until changed; each measurement command carries the current values. The chip is put into sleep after successful measurement, but if ADC read fails the sleep command is skipped because the function returns immediately.

## Dependencies and integration points
The driver uses the I2C core directly, IIO sysfs attributes for available calibration/scale/integration lists, a single direct-mode light channel, and standard module I2C ID matching. It does not use regmap, PM runtime, events, or buffers.

## Risks
Measurement sleeps are conservative and block the mutex. Failed ADC reads can leave the device in measure mode. Calibration rounding uses integer micro values and rejects values outside the mapping range. `i2c_set_clientdata(client, lv0104cs)` stores private data rather than the IIO device, which is acceptable locally because there is no remove/PM path using it but differs from many IIO drivers. Available-list emitters assume non-empty tables before replacing the final space with newline.

## Test signals
Build with IIO and I2C. Runtime tests should cover command send/receive short transfers, processed lux conversion for all scale choices, calibration rounding around midpoint boundaries, integration-time validation and sleep path, sleep command after success, and behavior after injected ADC read failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/lv0104cs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/max44000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/max44000.c

## Purpose
`max44000.c` is an IIO I2C/regmap driver for the Maxim MAX44000 ambient light and infrared proximity sensor. It exposes raw light and proximity channels, an output LED current channel, light scale/integration controls, and triggered-buffer capture.

## Important APIs, types, and functions
`struct max44000_data` contains the regmap and a mutex. `max44000_read_alstim()`/`write_alstim()` and `max44000_read_alspga()`/`write_alspga()` access ALS timing and gain fields. `max44000_read_alsval()` reads the big-endian ALS word, handles overflow, and compensates raw counts for integration-time resolution loss. LED current helpers translate the sparse TX current encoding. `max44000_read_raw()`, `max44000_write_raw()`, and `max44000_write_raw_get_fmt()` implement the IIO ABI. `max44000_trigger_handler()` samples active ALS/proximity scan channels into the buffer.

## Control flow
Probe initializes regmap with explicit readable/writeable/volatile/precious registers and single-byte I/O, resets RX scaling bits while preserving undocumented high bits, sets a default LED current, configures main mode to ALS plus proximity with trim enabled, reads status to clear stale interrupt state, sets up a devm triggered buffer, and registers IIO. Direct reads lock around register sequences. Integration-time and scale writes choose the closest supported value using util-macro helpers rather than requiring exact user input.

## State and persistence
Most state lives in device registers and regmap cache. No separate cached configuration exists beyond regmap. The driver leaves the device in ALS+proximity mode after probe and does not implement runtime PM or explicit remove powerdown. Buffered reads use current register settings for scale/timing and LED current.

## Dependencies and integration points
The file integrates with I2C, ACPI ID `MAX44000`, regmap, IIO direct attributes, IIO triggered buffers, and trigger consumers. It exposes fixed available lists through IIO constant attributes.

## Risks
The regmap `max_register` is `MAX44000_REG_PRX_DATA`, even though readable/writeable callbacks list later trim registers, so those later registers are effectively outside the configured range. The probe intentionally writes undocumented CFG_RX high bits to one; changing that can break proximity. `max44000_read_alsval()` returns saturated max on overflow instead of an error. Scale/integration writes silently round to nearest supported value. No IRQ/event support exists despite threshold register definitions.

## Test signals
Build with IIO buffer support. Runtime tests should cover probe default writes, status clear, raw ALS/proximity/current reads, LED current sparse encoding and range errors, overflow handling, scale and integration rounding, triggered buffer active scan masks, and regmap access boundaries for registers above `PRX_DATA`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/max44000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/max44009.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/max44009.c

## Purpose
`max44009.c` is an IIO I2C driver for the Maxim MAX44009 ambient light sensor. It exposes processed illuminance, configurable integration time, threshold events, and optional IRQ delivery.

## Important APIs, types, and functions
`struct max44009_data` stores the client and mutex. `max44009_read_int_time()` and `max44009_write_int_time()` access the configuration timing bits and force manual mode for timing writes. `max44009_lux_raw()` decodes exponent/mantissa light data. `max44009_read_lux_raw()` uses a four-message `i2c_transfer()` sequence without stop bits between register address and byte reads to avoid disjoint readings. Threshold helpers convert between scaled lux values and the single-byte threshold register encoding. Event callbacks read/write threshold values and enable interrupts. `max44009_threaded_irq_handler()` reads interrupt status and pushes threshold events.

## Control flow
Probe allocates IIO state, stores the client, initializes the mutex, reads the config register to clear/verify basic access, optionally requests a shared falling-edge threaded IRQ, and registers IIO. Processed light reads perform raw exponent/mantissa acquisition and return a fixed fractional scale of 0.045 lux/count. Integration-time writes pick the closest descending timing entry and update config. Event enable writes the interrupt-enable register and sets the threshold timer to zero.

## State and persistence
The driver keeps no cached hardware configuration except the mutex-protected I2C operations. Integration time, manual mode, thresholds, and interrupt enable persist in device registers. There is no remove powerdown or runtime PM.

## Dependencies and integration points
This file uses raw SMBus byte operations for most registers and raw I2C transfers for lux bytes. It integrates with OF compatible `maxim,max44009`, IIO events, optional threaded IRQs, and IIO direct-mode sysfs attributes.

## Risks
`max44009_write_int_time()` uses `config &= int_time` rather than clearing and setting `MAX44009_CFG_TIM_MASK`, which likely preserves only bits common with the selected index and can corrupt configuration. Threshold fractional reverse scaling uses integer division order that drops fractional precision. Event enable is not direction-specific even though both rising and falling event specs expose enable bits. The IRQ handler treats any negative status read as truthy and would push an event on read error.

## Test signals
Compile with IIO events and IRQ support. Runtime tests should cover no-stop lux transfers, processed scaling, all integration-time writes and config bit preservation, threshold encode/decode boundaries, event enable/disable semantics for both directions, IRQ status read error injection, and no-IRQ operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/max44009.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/noa1305.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/noa1305.c

## Purpose
`noa1305.c` is an IIO I2C/regmap driver for the ON Semiconductor NOA1305 ambient light sensor. It exposes raw ALS counts, scale derived from integration time, and writable integration time.

## Important APIs, types, and functions
`struct noa1305_priv` stores the client and regmap. `noa1305_measure()` bulk-reads the little-endian ALS data word. `noa1305_scale()` and `noa1305_int_time()` read the integration-time register and map the low three bits to fractional scale or time arrays. `noa1305_read_avail()`, `noa1305_read_raw()`, and `noa1305_write_raw()` implement the IIO callbacks. Probe enables the `vin` regulator, validates the 16-bit device ID, powers on, resets, sets default 800 ms integration time, and registers IIO.

## Control flow
Probe initializes regmap, enables supply, stores client data, reads and checks device ID `0x0519`, writes power control on, writes reset, writes the default integration-time register, then exposes a single direct-mode light channel. Raw reads do not trigger a conversion command; they read the current ALS data registers. Integration-time writes require `val == 0` and an exact microsecond match from the advertised list.

## State and persistence
The driver has no mutex and no cached configuration; hardware registers and regmap provide state. The power-control register is set on during probe and not explicitly powered off on remove. Integration time persists in the device register while powered. The regulator is managed by devm get-enable.

## Dependencies and integration points
The file integrates with I2C, OF compatible `onnn,noa1305`, regmap, regulator `vin`, and basic IIO direct-mode sysfs attributes with available lists.

## Risks
There is no locking around integration-time writes versus scale/raw reads. No PM or remove powerdown means the sensor may remain powered until regulator teardown. The regmap config only declares writeable registers, leaving volatile/readable behavior to defaults. The module author string for Martyn Welch is missing a closing `>`, a metadata issue but visible in modinfo. Interrupt registers are defined but no event support is implemented.

## Test signals
Build with regulator and IIO. Runtime tests should cover missing regulator, ID read mismatch, power/reset/default writes, raw little-endian data conversion, scale/time mapping for every integration setting, exact-match rejection for unsupported times, and concurrent read/write behavior under stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/noa1305.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt3001.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/opt3001.c

## Purpose
`opt3001.c` is an IIO I2C driver for TI OPT3001 light sensors and OPT3002 intensity sensors. It supports single-shot direct reads, optional interrupt-assisted conversion completion, threshold events in continuous mode, and integration-time configuration.

## Important APIs, types, and functions
`struct opt3001_chip_info` parameterizes channel type, scale tables, conversion factors, and ID availability. `struct opt3001` stores client/device pointers, lock, IRQ conversion state, waitqueue, last result, chip info, integration time, mode, threshold mantissa/exponent caches, and `use_irq`. `opt3001_get_processed()` starts a single conversion, waits by IRQ or sleep/poll, reads result, restores low-limit threshold after end-of-conversion IRQ use, and converts exponent/mantissa to IIO units. `opt3001_set_int_time()`, event read/write/config helpers, `opt3001_configure()`, and `opt3001_irq()` implement the rest of the ABI.

## Control flow
Probe allocates state, selects match data, optionally reads manufacturer/device IDs, configures auto full-scale, shutdown mode, latched window comparison, polarity, mask/exponent threshold caches, registers IIO, and only then requests an IRQ if one is provided. Direct reads reject operation while continuous event mode is active. Event config switches the device between continuous sampling and shutdown. IRQ handling either pushes threshold events in continuous mode or captures single-shot result and wakes the waitqueue.

## State and persistence
The driver caches integration time, mode, threshold exponent/mantissa, last result, and IRQ synchronization flags. Threshold values are mirrored because the low-limit register is temporarily overwritten with the end-of-conversion enable magic during IRQ-assisted direct reads. Hardware mode persists until event config, read, remove, or reset changes it. Remove frees IRQ and forces shutdown.

## Dependencies and integration points
The driver integrates with I2C SMBus word-swapped transactions, OF and I2C IDs for OPT3001/OPT3002, IIO direct attributes, IIO events, IRQ threading, wait queues, and custom scale conversion tables.

## Risks
IRQ is requested after `devm_iio_device_register()`, so a registered device may be visible before IRQ-backed behavior is ready. `ok_to_ignore_lock` deliberately lets the IRQ thread bypass the mutex during single-shot reads; regressions here can deadlock or race threshold events. Direct reads are unavailable during continuous event mode. Low-limit threshold restoration after end-of-conversion use is critical; failures can leave event thresholds altered. The wait timeout always uses the long value in IRQ mode.

## Test signals
Build with IIO events. Runtime tests should cover OPT3001 and OPT3002 match data, ID read path, 100 ms and 800 ms integration times, IRQ and no-IRQ conversion completion, timeout handling, low-limit restoration, threshold conversion for both chip factors, event mode transitions, direct-read `-EBUSY` in continuous mode, and remove shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt3001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt4001.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/opt4001.c

## Purpose
`opt4001.c` is an IIO I2C/regmap driver for TI OPT4001 ambient light sensors. It supports package-specific lux conversion constants, processed illuminance reads, and configurable integration time in continuous mode.

## Important APIs, types, and functions
`struct opt4001_chip_info` supplies lux multiplier/divider constants and the IIO name for SOT-5x3 versus Picostar packages. `struct opt4001_chip` stores regmap, client, current integration-time index, and chip info. `opt4001_calculate_crc()` validates the sensor's 20-bit mantissa/exponent/counter payload. `opt4001_read_lux_value()` reads MSB/LSB result registers, checks CRC, applies exponent and package constants, and returns integer-plus-nano lux. `opt4001_set_conf()` programs auto range, conversion time, and continuous mode. Probe validates device ID, loads defaults, registers a power-off cleanup action, and registers IIO.

## Control flow
Probe enables `vdd`, initializes a big-endian 16-bit regmap, reinitializes cache, reads the device ID and warns on unexpected values, takes match data from I2C/OF, sets channels/name, loads default 800 ms continuous conversion, adds cleanup, and registers the device. Reads fetch the most recent continuous measurement. Integration-time writes require exact microsecond match in the available table, update `chip->int_time`, and rewrite the control register.

## State and persistence
The current integration-time index is cached in RAM and written to the control register. The device is left in continuous auto-range mode while active and powered down via cleanup on unbind/probe failure. Regmap caches nonvolatile control state; result registers are volatile.

## Dependencies and integration points
The driver integrates with I2C, OF compatibles `ti,opt4001-sot-5x3` and `ti,opt4001-picostar`, regulator `vdd`, regmap with big-endian 16-bit values, and direct-mode IIO attributes.

## Risks
`opt4001_power_down()` reads `OPT4001_DEVICE_ID` and then masks `OPT4001_CTRL_OPER_MODE_MASK` before writing `OPT4001_CTRL`; this appears to use the wrong source register for preserving control bits. There is no mutex around reads and integration-time writes. CRC mismatch returns `-EIO`, so userspace may see intermittent failures on torn or noisy reads. Device ID mismatch only warns, allowing operation on potentially incompatible devices.

## Test signals
Build with regulator and regmap. Runtime tests should cover both package compatibles and conversion constants, CRC success/failure, device ID warning, all integration-time writes, continuous-read behavior, cleanup powerdown register source correctness, and concurrent reads while changing integration time.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt4001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt4060.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/opt4060.c

## Purpose
`opt4060.c` is an IIO I2C/regmap driver for the TI OPT4060 RGBW color sensor. It exposes raw red/green/blue/clear intensity channels, derived illuminance, integration time, optional threshold events, an optional data-ready trigger, and triggered-buffer capture.

## Important APIs, types, and functions
`struct opt4060_chip` stores regmap, device, trigger, integration-time index, IRQ number, IRQ/event mutexes, completion, and threshold-active flags. `opt4060_calculate_crc()` validates 20-bit sample payloads. `opt4060_set_driver_state()` coordinates sampling mode and interrupt mode while claiming current IIO mode. `opt4060_trigger_new_samples()` starts one-shot conversion and waits by IRQ completion or polling `RES_CTRL`. `opt4060_read_raw_value()`, `opt4060_read_chan_raw()`, and `opt4060_calc_illuminance()` implement sample reads. Event helpers convert threshold register format, select the threshold channel, manage persistence period, and enforce that only one channel has active threshold events. Trigger and IRQ helpers wire data-ready interrupts to buffers and events.

## Control flow
Probe enables `vdd`, initializes a big-endian 16-bit regmap, validates/warns on device ID, chooses event-capable or no-event channel tables based on IRQ availability, loads defaults with min/max thresholds, auto-range, one-shot mode, quick wake, and latch, registers cleanup powerdown, sets up triggered buffer, optionally registers a device-owned data-ready trigger and threaded IRQ, then registers IIO. Direct raw and illuminance reads trigger fresh samples. If the driver-owned trigger and buffer are active, state is kept continuous with data-ready IRQs; otherwise direct reads and events switch between one-shot, continuous sampling, threshold IRQs, and all-channel IRQs as needed.

## State and persistence
The driver caches integration-time index and which threshold directions are active. Hardware threshold values, channel selection, fault count, control mode, and interrupt mode live in registers. Completion synchronizes one-shot reads when IRQ is available. Cleanup clears operating mode. Regmap caches configuration while sample/result registers are volatile.

## Dependencies and integration points
The file integrates with I2C, OF compatible `ti,opt4060`, regulator `vdd`, regmap, IIO events, IIO triggers, trigger consumers, triggered buffers, completions, mutex guards, and IIO current-mode claiming. It exposes events only when an IRQ is provided.

## Risks
`opt4060_writable_reg()` uses `reg >= OPT4060_THRESHOLD_LOW || reg >= OPT4060_INT_CTRL`; the second condition is redundant and the expression effectively marks every register from threshold-low upward writeable, including `DEVICE_ID`, unless other regmap handling blocks it. `opt4060_trigger_handler()` calls `opt4060_trigger_new_samples()` when `iio_trigger_validate_own_device()` returns true despite the comment saying external triggers need new samples; this condition should be verified. Event state allows only one threshold channel, so userspace must handle `-EBUSY`. Multiple state machines share IRQ configuration and sampling mode, making buffer/event/direct-read races the main maintenance risk.

## Test signals
Build with IIO events, triggers, buffers, and regmap. Runtime tests should cover IRQ and no-IRQ probe paths, CRC failures, direct raw and illuminance reads, all integration-time values, threshold encode/decode and period quantization, one-channel event exclusivity, event enable/disable state transitions, data-ready trigger buffering, external trigger behavior, timeout paths, and cleanup powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/opt4060.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/pa12203001.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/pa12203001.c

## Purpose
`pa12203001.c` is an IIO I2C/regmap driver for the TXC PA12203001 proximity and ambient light sensor. It exposes raw ALS and proximity readings plus ALS scale selection, with runtime PM used to autosuspend the chip after reads.

## Important APIs, types, and functions
`struct pa12203001_data` stores the client, lock, enable-state booleans, deferred-enable booleans for runtime resume, and regmap. `pa12203001_als_enable()` and `pa12203001_px_enable()` update CFG0 enable bits and cached booleans. `pa12203001_set_power_state()` coordinates requested ALS/proximity use with runtime PM and deferred enables. `pa12203001_read_raw()` reads ALS as a little-endian 16-bit word or proximity as one byte, bracketing access with power-state calls. `pa12203001_write_raw()` updates ALS full-scale range. `pa12203001_init()` writes default CFG/PSET registers, and PM callbacks power the chip down or apply deferred enables.

## Control flow
Probe allocates IIO state, initializes regmap with volatile ALS/proximity data ranges, writes default configuration, enables both ALS and proximity, marks runtime PM active, enables autosuspend with a 3 second delay, registers IIO, and powers down on failure. Raw reads request the relevant sensor block, read the data register(s), and put the device for autosuspend. Remove unregisters IIO, disables runtime PM, marks suspended, and powers down both blocks. System suspend disables both blocks; resume re-enables both. Runtime resume enables any block whose read path marked `*_needs_enable`.

## State and persistence
The driver keeps cached ALS/proximity enabled flags and deferred enable flags. Hardware CFG registers hold range and enable state. Runtime PM may leave the chip disabled while logical reads request it temporarily. Scale changes persist in CFG0. There is no interrupt/event support despite proximity/interrupt-related register fields.

## Dependencies and integration points
The file integrates with I2C, ACPI ID `TXCPA122`, regmap, runtime and system PM, direct-mode IIO attributes, and IIO constant available-scale sysfs.

## Risks
`pa12203001_set_power_state()` has subtle logic: when enabling ALS it checks `px_enabled`, and when enabling proximity it checks `als_enabled`, so deferred-enable behavior depends on the other channel state rather than the target channel alone. In read paths, errors after power-on jump to cleanup, but cleanup errors can mask original register-read failures. With `CONFIG_PM` disabled, `pa12203001_set_power_state()` is a no-op and reads assume the probe-enabled state remains. Scale writes read CFG0 but return `-EINVAL` for read errors rather than the actual I/O error.

## Test signals
Build with and without PM. Runtime tests should cover default register writes, raw ALS/proximity reads, scale read/write for all four ranges, autosuspend and runtime resume deferred-enable flags, system suspend/resume, remove powerdown, register-read error cleanup, and the cross-channel enable logic in `pa12203001_set_power_state()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/pa12203001.c -->
