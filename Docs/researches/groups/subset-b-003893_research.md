# subset-b-003893 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/inkern.c -->
# sources/distributed-fs/ceph-client/drivers/iio/inkern.c

## Purpose

`inkern.c` is the in-kernel IIO consumer API implementation. It lets non-IIO kernel drivers discover producer channels by firmware references or board mapping tables, hold references to the backing `iio_dev`, and perform raw, processed, scale, min/max, write, ext-info, and label operations without going through userspace sysfs.

## Important APIs, Types, and Functions

- `struct iio_map_internal`, `iio_map_list`, and `iio_map_list_lock` store legacy `struct iio_map` consumer-to-provider mappings.
- `iio_map_array_register()`, `iio_map_array_unregister()`, and `devm_iio_map_array_register()` manage board maps.
- `fwnode_iio_channel_get_by_name()`, `iio_channel_get()`, `devm_iio_channel_get()`, `iio_channel_get_all()`, and their release/devm variants resolve single or all channels.
- `iio_read_channel_raw()`, `iio_read_channel_processed_scale()`, `iio_read_channel_attribute()`, `iio_read_avail_channel_attribute()`, min/max helpers, and write helpers dispatch into provider `iio_info` callbacks.
- `iio_multiply_value()` normalizes IIO value encodings for processed conversions and is exported to the IIO unit-test namespace.
- `iio_read_channel_ext_info()`, `iio_write_channel_ext_info()`, and `iio_read_channel_label()` expose channel extension metadata.

## Control Flow

Channel lookup prefers firmware: `iio_channel_get()` calls `fwnode_iio_channel_get_by_name()` for the consumer device, which matches `io-channel-names`, resolves `io-channels`, finds the producer on `iio_bus_type`, and translates the specifier via provider `fwnode_xlate` or the simple index translator. If direct node lookup returns `-ENODEV`, the code walks parents that advertise `io-channel-ranges`. Legacy fallback scans the global map list under `iio_map_list_lock`, grabs an IIO device reference, and optionally resolves the provider channel by datasheet name.

Reads and writes lock `to_iio_dev_opaque(...)->info_exist_lock` around provider callback access so unregister cannot race with consumers dereferencing `indio_dev->info`. Processed reads first prefer provider `IIO_CHAN_INFO_PROCESSED`, otherwise read raw, optionally add offset, multiply by scale, and apply the consumer scale argument.

## State and Persistence Behavior

Persistent state is the global mapping list, each `iio_channel`'s `indio_dev` reference, optional `consumer_data`, and selected `iio_chan_spec`. Devm helpers register cleanup actions so maps and acquired channels are released with the owner device. No readings are cached here; values are delegated to producer drivers.

## Dependencies and Integration Points

The file integrates with the IIO bus/core, firmware property APIs, `struct iio_info` provider callbacks, `iio_device_get()/put()`, device-managed cleanup, and legacy machine mapping via `<linux/iio/machine.h>`. It is the contract used by regulator, hwmon, thermal, power, and other kernel subsystems that consume IIO channels.

## Risks and Edge Cases

Firmware lookup distinguishes `-ENODEV`, `-ENOENT`, `-EINVAL`, and `-EPROBE_DEFER`; a wrong return path can accidentally suppress fallback or retry. `iio_channel_get_all()` must unwind partially acquired references on errors. The conversion path truncates some offset encodings before scaling. This source snapshot also shows suspicious duplicated statements/braces in `__fwnode_iio_channel_get_by_name()`, `iio_channel_release_all()`, and `iio_channel_read_max()`, which are compile or review signals rather than intended behavior.

## Test Signals

Use firmware and legacy-map tests for named, unnamed, parent-ranged, missing, and deferred channels. Exercise `read_raw`, `read_raw_multi`, processed conversion with offset/scale formats, available list/range min/max, devm cleanup, release-all unwind, ext-info buffer validation, and provider unregister racing with consumer reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/inkern.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/light/Kconfig

## Purpose

This Kconfig menu declares the build-time configuration surface for IIO light, color, UV, proximity, and related combo sensors. It maps each driver to its bus and helper dependencies, selects common IIO buffer/trigger/regmap/GTS support where needed, and provides module names for users and distributions.

## Important APIs, Types, and Functions

The file is declarative Kconfig rather than C code. The subset entries include `ACPI_ALS`, `ADJD_S311`, `ADUX1020`, `AL3000A`, `AL3010`, `AL3320A`, `APDS9160`, `APDS9300`, `APDS9306`, `APDS9960`, and `AS73211`. Important dependency selectors include `depends on I2C`, `depends on ACPI`, `select REGMAP_I2C`, `select IIO_BUFFER`, `select IIO_TRIGGERED_BUFFER`, `select IIO_KFIFO_BUF`, and `select IIO_GTS_HELPER`.

## Control Flow

Kernel configuration tools present the "Light sensors" menu. Selecting a tristate symbol controls whether the matching object in the directory Makefile is omitted, built-in, or compiled as a module. `select` clauses pull in helper infrastructure needed by the driver implementation, while `depends on` clauses hide entries when the required bus or parent subsystem is unavailable.

## State and Persistence Behavior

The persistent state is the generated kernel `.config` and module build result. There is no runtime state here, but incorrect dependencies persist into build failures or missing runtime functionality.

## Dependencies and Integration Points

This file integrates with `drivers/iio/light/Makefile`, the IIO core, I2C, ACPI, HID sensor hub support, MFD parents, regmap backends, triggered buffers, kfifo buffers, and the IIO gain-time-scale helper. Its ordering comment asks new entries to stay alphabetic, which keeps menu and Makefile maintenance predictable.

## Risks and Edge Cases

Kconfig `select` bypasses dependency checks of the selected symbol, so entries must only select helpers that are safe to force-enable. Missing `REGMAP_I2C`, buffer, trigger, or GTS selections can produce link failures or incomplete driver behavior. This snapshot contains minor text issues such as duplicated help lines in unrelated entries; those are not runtime bugs but are maintenance signals.

## Test Signals

Run representative `allyesconfig`, `allmodconfig`, and focused builds for each listed symbol as built-in and module. Verify module names match help text and Makefile object names, and run dependency-disabled configs such as no I2C or no ACPI to confirm symbols are hidden as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/light/Makefile

## Purpose

This Makefile maps each `CONFIG_*` light-sensor Kconfig symbol to the object file that should be built for that driver. It is the build-system companion to `drivers/iio/light/Kconfig`.

## Important APIs, Types, and Functions

The important constructs are `obj-$(CONFIG_SYMBOL) += object.o` assignments. For this subset, the mappings are `ACPI_ALS -> acpi-als.o`, `ADJD_S311 -> adjd_s311.o`, `ADUX1020 -> adux1020.o`, `AL3000A -> al3000a.o`, `AL3010 -> al3010.o`, `AL3320A -> al3320a.o`, `APDS9160 -> apds9160.o`, `APDS9300 -> apds9300.o`, `APDS9306 -> apds9306.o`, `APDS9960 -> apds9960.o`, and `AS73211 -> as73211.o`.

## Control Flow

Kbuild expands each `obj-y` or `obj-m` value according to the generated `.config`. Built-in objects are linked into the kernel image or parent built-in archive; module objects become individual loadable modules with names derived from the object basename.

## State and Persistence Behavior

The file has no runtime state. Its build output persists as generated `.o`, `.ko`, and built-in archive content. Ordering is maintained alphabetically by comment convention.

## Dependencies and Integration Points

It integrates directly with the Kconfig symbols in the same directory, Kbuild's recursive make logic, and module metadata emitted by each C file. Multi-object drivers in later entries, such as ST UVIS25 core plus bus wrappers, show how this directory handles split implementations.

## Risks and Edge Cases

A symbol/object mismatch silently omits a configured driver or tries to build a missing file. Alphabetic drift is low risk but increases merge conflicts. Whitespace differences, such as the `STK3310` line spacing, are cosmetic unless they hide a typo.

## Test Signals

Focused tests are build-only: enable each listed symbol as `m` and confirm the expected `.ko` exists, then enable as `y` and confirm built-in linkage. Cross-check Kconfig help module names against generated module names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/acpi-als.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/acpi-als.c

## Purpose

`acpi-als.c` exposes ACPI0008 ambient light readings through IIO. It currently supports illuminance via the ACPI `_ALI` method and provides both direct reads and a triggered buffer path driven by ACPI notifications.

## Important APIs, Types, and Functions

- `struct acpi_als` stores the ACPI companion, a mutex, and the private IIO trigger.
- `acpi_als_read_value()` evaluates ACPI integer methods such as `_ALI`.
- `acpi_als_read_raw()` returns `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_PROCESSED` for the single `IIO_LIGHT` channel.
- `acpi_als_notify()` receives `ACPI_ALS_NOTIFY_ILLUMINANCE` and polls the private trigger when the buffer uses that trigger.
- `acpi_als_trigger_handler()` reads `_ALI` and pushes `{s32 light, timestamp}`.
- `acpi_als_probe()` allocates the IIO device, trigger, triggered buffer, and ACPI notify handler; `acpi_als_remove()` unregisters the notify handler.

## Control Flow

Probe binds to ACPI ID `ACPI0008`, creates one light channel plus timestamp, registers a trigger, assigns it as the default trigger, sets up a triggered buffer, registers the IIO device, then installs the ACPI device notify handler. Direct sysfs reads call `_ALI` synchronously. Notification events only produce buffered samples when the IIO buffer is enabled and the device is using its own trigger.

## State and Persistence Behavior

The driver stores no calibration or cached sensor values. The mutex serializes trigger-handler reads. The ACPI notify registration persists from probe to remove, and devm resources handle IIO objects.

## Dependencies and Integration Points

It depends on ACPI evaluation/notification APIs, platform-device ACPI companion matching, IIO core, triggers, triggered buffers, and kfifo buffer support selected by Kconfig.

## Risks and Edge Cases

Only `_ALI` is implemented although ACPI0008 can describe chromaticity, color temperature, polling intervals, and response tables. Firmware evaluation failure becomes `-EIO`. Notifications are ignored when buffering is disabled or another trigger is active, which is correct but can surprise platform debugging.

## Test Signals

Test ACPI0008 probe, direct raw/processed reads, ACPI method failure, notification-driven buffer samples, timestamp population, unhandled notify events, and remove-time notify cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/acpi-als.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/adjd_s311.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/adjd_s311.c

## Purpose

`adjd_s311.c` is an I2C IIO driver for the Avago ADJD-S311-CR999 digital color sensor. It exposes 10-bit red, green, blue, and clear intensity channels with per-channel capacitor gain and integration-time controls plus triggered-buffer sampling.

## Important APIs, Types, and Functions

- `struct adjd_s311_data` stores the `i2c_client`.
- `adjd_s311_req_data()` starts a conversion by setting `GSSR`, polls for completion up to ten times with 20 ms sleeps, and returns `-EIO` on timeout.
- `adjd_s311_read_data()` requests fresh data and reads a 10-bit channel word.
- `adjd_s311_read_raw()` handles raw data, hardware gain from `CAP_*`, and integration time from `INT_*`.
- `adjd_s311_write_raw()` programs capacitor gain and integration registers with range validation.
- `adjd_s311_trigger_handler()` collects active scan channels into a four-channel 16-bit buffer.
- `ADJD_S311_CHANNEL()` defines modified RGB/clear IIO intensity channels.

## Control Flow

Probe allocates the IIO device, assigns channel definitions and direct mode, installs a triggered buffer, and registers the device. Every raw data read triggers a new sensor conversion before reading the selected data register. Buffered reads trigger one conversion, iterate only active scan bits, read each selected channel, and push a timestamped sample.

## State and Persistence Behavior

The driver has minimal software state. Hardware registers hold capacitor gain and integration values. There is no mutex around direct reads/writes, so serialization relies on IIO direct/buffer use rules and the I2C bus.

## Dependencies and Integration Points

It depends on I2C SMBus byte/word operations, IIO direct mode, triggered buffers, scan masks from active channels, and module I2C ID matching for `"adjd_s311"`.

## Risks and Edge Cases

The file notes missing calibration, offset mode, and sleep mode. Conversion polling can take about 200 ms before failing. Integration time is returned as a fractional micro value based on measurement rather than formal documentation. Concurrent direct writes while buffered sampling can alter gain or timing mid-stream.

## Test Signals

Test conversion timeout, 10-bit masking, per-channel gain writes outside and inside 0..15, integration writes outside and inside 0..4095, triggered buffers with partial scan masks, and probe/register behavior on SMBus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/adjd_s311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/adux1020.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/adux1020.c

## Purpose

`adux1020.c` supports the Analog Devices ADUX1020 photometric sensor as an IIO proximity device with LED current output control, sampling-frequency control, and threshold events.

## Important APIs, Types, and Functions

- `struct adux1020_data` stores the client, IIO device, mutex, and 16-bit regmap.
- `struct adux1020_mode_data` describes bytes, FIFO length, and interrupt mask per operating mode.
- `adux1020_chip_init()` validates chip ID `0x03fc`, soft resets, writes a default register sequence, flushes FIFO, selects LED reference, and masks interrupts.
- `adux1020_set_mode()`, `adux1020_flush_fifo()`, `adux1020_read_fifo()`, and `adux1020_measure()` implement polled proximity measurements.
- `adux1020_read_raw()` and `adux1020_write_raw()` expose proximity raw, proximity sampling frequency, and LED current.
- Event callbacks read/write thresholds and interrupt enable state; `adux1020_interrupt_handler()` pushes rising/falling proximity threshold events.

## Control Flow

Probe initializes regmap, mutex, default chip configuration, optional IRQ, then registers the IIO device. Direct proximity reads lock the device, switch to proximity mode, poll FIFO status with interrupts masked at the pin, read one FIFO word, clear mode interrupt state, and mask mode interrupts again. Enabling threshold events configures interrupt pin behavior, unmasks the selected rising/falling source, sets proximity mode, and later the IRQ handler decodes status bits into IIO events.

## State and Persistence Behavior

Runtime state is mostly in hardware registers. The mutex protects multi-register mode, rate, LED-current, and event changes. Threshold values persist in device registers. There is no runtime PM or explicit power-off path.

## Dependencies and Integration Points

The driver depends on I2C regmap with 8-bit registers and 16-bit values, IIO event callbacks, optional threaded IRQ support, and DT compatible `"adi,adux1020"`.

## Risks and Edge Cases

Only `ADUX1020_MODE_PROX_I` is supported despite enum values for other modes. The TODO notes missing triggered buffer support. Polling waits up to about one second. Incorrect interrupt masking can interfere with polled measurements. The default register sequence is large and opaque, so datasheet regressions need hardware validation.

## Test Signals

Test chip-ID rejection, default register writes, FIFO flush/read paths, sampling-frequency and LED-current available values, threshold bounds 0..65535, IRQ event delivery for ON/OFF bits, and operation without an IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/adux1020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3000a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/al3000a.c

## Purpose

`al3000a.c` is a compact I2C/regmap IIO driver for the Dyna Image AL3000A ambient light sensor. It exposes processed illuminance by mapping the sensor's 6-bit output code through a precomputed lux table.

## Important APIs, Types, and Functions

- `lux_table[]` maps output codes 0..63 to lux values.
- `struct al3000a_data` stores the regmap and `vdd` regulator.
- `al3000a_set_pwr_on()` enables the regulator and writes the system enable value.
- `al3000a_set_pwr_off()` disables the sensor and regulator through a devm cleanup and PM path.
- `al3000a_init()` powers on, registers cleanup, resets the sensor, and re-enables it.
- `al3000a_read_raw()` reads `AL3000A_REG_DATA`, masks `GENMASK(5,0)`, and returns processed lux.

## Control Flow

Probe allocates the IIO device, initializes an 8-bit regmap, obtains `vdd`, fills one `IIO_LIGHT` processed channel, initializes hardware, and registers the IIO device. Suspend powers off through the same helper used by cleanup; resume only powers on and does not repeat reset.

## State and Persistence Behavior

State is limited to regmap/regulator pointers. The current reading is not cached. Power state is controlled by hardware and devm/PM calls. The lux mapping is static.

## Dependencies and Integration Points

It uses I2C regmap, regulator framework, IIO direct mode, OF compatible `"dynaimage,al3000a"`, and I2C ID `"al3000a"`.

## Risks and Edge Cases

Resume does not reapply reset/config beyond enabling the part. The processed value depends entirely on a fixed lookup table, so any variant-specific calibration is outside this driver. Failed sensor-disable writes during cleanup are logged but cannot be recovered.

## Test Signals

Test regulator failures, reset/enable sequence, all 64 data codes mapping to table values, suspend/resume power writes, and devm cleanup on probe failure after power-on.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3000a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3010.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/al3010.c

## Purpose

`al3010.c` supports the Dyna Image AL3010 ambient light sensor over I2C. It exposes one raw illuminance channel and a writable scale representing four gain/range settings.

## Important APIs, Types, and Functions

- `al3010_scales[][]` and `AL3010_SCALE_AVAILABLE` define the scale ABI.
- `struct al3010_data` stores an 8-bit regmap.
- `al3010_set_pwr_on()`, `al3010_set_pwr_off()`, and `al3010_init()` enable the sensor and set the default range to `AL3XXX_RANGE_3`.
- `al3010_read_raw()` reads raw ALS data from `AL3010_REG_DATA_LOW` and scale from `AL3010_REG_CONFIG`.
- `al3010_write_raw()` validates a requested scale tuple and writes the matching gain field.

## Control Flow

Probe allocates the IIO device, initializes regmap, configures channel metadata and scale-available attributes, powers on the chip, programs default gain, and registers the device. Direct sysfs reads either fetch raw output or decode the current gain bits. PM suspend disables the sensor; resume enables it.

## State and Persistence Behavior

The driver keeps no cached scale; it reads the config register for scale queries. The hardware retains gain while powered unless reset externally. Devm cleanup powers off on driver detach or failed probe.

## Dependencies and Integration Points

It depends on I2C regmap, IIO sysfs attributes, simple sleep PM, OF compatible `"dynaimage,al3010"`, and I2C ID matching.

## Risks and Edge Cases

The code comments note no interrupt/threshold support and warn future interrupt support must disable IRQs before power-off. The raw read uses a single `regmap_read()` from the low data register even though the comment says output spans adjacent low/high registers; this is a key test/review signal for data width handling.

## Test Signals

Test all four scale values, invalid scale rejection, default range programming, raw data width behavior against hardware or regmap mocks, and suspend/resume with configured scale preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3320a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/al3320a.c

## Purpose

`al3320a.c` is an IIO I2C/regmap driver for the Dyna Image AL3320A ambient light sensor. It exposes raw illuminance and writable scale/gain settings, with default mean and wait timing configuration.

## Important APIs, Types, and Functions

- `al3320a_scales[][]` and `AL3320A_SCALE_AVAILABLE` define four lux-per-count ranges.
- `struct al3320a_data` stores the regmap.
- `al3320a_init()` powers on, registers power-off cleanup, writes default gain/range, mean time, and wait time.
- `al3320a_read_raw()` reads raw ALS data and decodes scale from `AL3320A_REG_CONFIG_RANGE`.
- `al3320a_write_raw()` maps a requested scale tuple back to the gain field.

## Control Flow

Probe initializes an IIO direct-mode device with one light channel and a scale-available attribute, sets up regmap, applies initial hardware configuration, and registers. Suspend disables the sensor via config register; resume re-enables it.

## State and Persistence Behavior

The software stores only the regmap pointer. The gain, mean time, wait time, and thresholds live in hardware registers. There is no cached event state because interrupt/threshold support is not implemented.

## Dependencies and Integration Points

It integrates with I2C regmap, IIO direct mode, sysfs constant attributes, sleep PM, OF compatible `"dynaimage,al3320a"`, ACPI ID `"CALS0001"`, and I2C ID `"al3320a"`.

## Risks and Edge Cases

Like AL3010, comments note future interrupt handling must avoid power-off races. The raw read comments describe two adjacent data bytes, but the implementation performs a single 8-bit regmap read from the low register. Threshold registers are defined in the map but unused.

## Test Signals

Test default config writes, scale read/write round trips, invalid scale rejection, ACPI and OF matching, raw data width against hardware expectations, and PM power toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/al3320a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9160.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/apds9160.c

## Purpose

`apds9160.c` supports the Broadcom APDS9160 combined ambient-light and proximity sensor. It exposes proximity, LED current, illuminance, and clear intensity channels, optional threshold events, ALS gain/time/scale controls, proximity gain/rate/cancellation controls, and DT-configured analog cancellation.

## Important APIs, Types, and Functions

- `struct apds9160_chip` stores the client, regmap, regmap fields, mutex, event enable flags, and cached ALS/PS configuration.
- Regmap defaults and access tables describe control, status, data, threshold, and cancellation registers.
- `apds9160_set_ps_rate()`, `apds9160_set_ps_gain()`, `apds9160_set_ps_current()`, and cancellation helpers program proximity behavior.
- `apds9160_set_als_int_time()`, `apds9160_set_als_scale()`, and gain/rate/resolution helpers keep ALS timing and scale coherent.
- `apds9160_read_raw()`, `apds9160_write_raw()`, `apds9160_read_avail()`, and `apds9160_write_raw_get_fmt()` implement IIO direct attributes.
- Event callbacks read/write 11-bit PS and 20-bit LS thresholds and enable per-channel interrupts.
- `apds9160_irq_handler()` reads status, clears interrupt flags, and pushes IIO threshold events.

## Control Flow

Probe enables `vdd`, initializes regmap, detects the part ID, allocates regmap fields, enables ALS/PS, writes default PS current/rate/resolution/gain/cancellation and ALS time/scale, applies optional `ps-cancellation-duration` and `ps-cancellation-current-picoamp`, chooses event-capable channels when an IRQ exists, and registers the IIO device. Raw reads bulk-read two proximity bytes or three ALS/clear bytes. Writes take the mutex and update hardware plus cached configuration.

## State and Persistence Behavior

Cached state mirrors hardware configuration for ALS interrupt enable, PS interrupt enable, ALS integration time/gain/scale, PS rate/current/gain, and digital cancellation level. Thresholds and analog cancellation live in registers. `devm_add_action_or_reset()` disables ALS/PS on teardown.

## Dependencies and Integration Points

The driver depends on I2C regmap, regmap fields, regulator `vdd`, IIO events/sysfs, unaligned little-endian helpers, optional firmware properties, OF compatible `"brcm,apds9160"`, and I2C ID `"apds9160"`.

## Risks and Edge Cases

Event support is absent when no IRQ is supplied. ALS scale availability changes with integration time. Cancellation current validation accepts only 60 nA to 276 nA in 2.4 nA steps and rounds during coarse/fine calculation. This source snapshot shows duplicated fields/statements and a duplicated `if` in the IRQ path, which should be treated as compile/review risks. The driver logs but accepts unknown part IDs.

## Test Signals

Test probe defaults, unknown ID logging, all available ALS/PS rates and gains, scale changes after integration-time changes, threshold bounds, IRQ event delivery for ALS and PS status bits, DT analog cancellation properties, no-IRQ channel table selection, and teardown disabling both sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9160.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9300.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/apds9300.c

## Purpose

`apds9300.c` is an IIO driver for the Avago APDS9300 ambient light sensor. It provides processed lux, raw broadband/IR intensity channels, optional threshold events, and simple power management.

## Important APIs, Types, and Functions

- `struct apds9300_data` stores client, mutex, power state, cached thresholds, and interrupt enable state.
- `apds9300_calculate_lux()` converts channel 0/channel 1 readings to lux using piecewise formulas and a precomputed ratio table.
- `apds9300_get_adc_val()`, threshold setters, interrupt state setter, and power setter wrap SMBus accesses.
- `apds9300_read_raw()` returns processed light or raw intensity.
- Event callbacks expose threshold values and interrupt enable state.
- `apds9300_interrupt_handler()` pushes a threshold event and clears the hardware interrupt.

## Control Flow

Probe powers the chip off then on, verifies the control register, disables interrupts, initializes the mutex and IIO metadata, optionally requests a threaded IRQ, and registers the IIO device. Direct light reads fetch both ADC channels under the mutex and compute lux. Threshold writes and interrupt toggles require the chip to be powered. Remove unregisters the device, disables interrupts, and powers off.

## State and Persistence Behavior

The driver caches `power_state`, low/high threshold values, and interrupt enable state in software after successful hardware writes. Threshold defaults are not read from hardware at probe. PM suspend/resume toggles power but does not explicitly restore interrupt or threshold registers.

## Dependencies and Integration Points

It uses I2C SMBus command/word operations, IIO event callbacks, optional threaded IRQs, and simple sleep PM. The module matches I2C ID `"apds9300"`.

## Risks and Edge Cases

Operations return `-EBUSY` when attempted while powered off. A resume that resets chip state externally could desynchronize cached thresholds and interrupt enable. The IRQ event reports `IIO_EV_DIR_EITHER` regardless of threshold side. Lux computation avoids divide-by-zero and clamps high IR ratios to zero.

## Test Signals

Test chip init control readback, power-off error paths, lux conversion branches for ratio ranges, threshold bounds above `0xffff`, IRQ clear behavior, no-IRQ info table selection, remove cleanup, and suspend/resume reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9306.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/apds9306.c

## Purpose

`apds9306.c` supports the Broadcom/Avago APDS-9306 and APDS-9306-065 ambient light sensors. It exposes ALS and clear raw channels, scale/integration-time/sampling-frequency controls using the IIO GTS helper, runtime PM, and optional threshold/adaptive-threshold events.

## Important APIs, Types, and Functions

- `struct part_id_gts_multiplier` selects scale multipliers for part IDs `0xB1` and `0xB3`.
- `struct apds9306_regfields` and `struct apds9306_data` hold regmap fields, mutex, GTS tables, and an IRQ/data-ready flag.
- `apds9306_init_iio_gts()` initializes gain/time/scale tables.
- `apds9306_read_data()` resumes the device, waits for data-ready or interrupt status, pushes missed threshold events, bulk-reads 24-bit data, and autosuspends.
- Integration-time and scale setters preserve effective scale by adjusting gain/time through GTS helper APIs.
- Event callbacks handle 20-bit thresholds, persistence period, adaptive threshold variance, channel selection, and runtime-PM references while interrupts are enabled.

## Control Flow

Probe creates regmap, allocates fields, enables `vdd`, selects event or no-event channel tables based on IRQ availability, initializes runtime PM, identifies the part for GTS scaling, programs default 100 ms/10 Hz/3x settings, registers cleanup and the IIO device, then drops the autosuspend reference. Direct raw reads claim direct mode, call `apds9306_read_data()`, and release direct mode. IRQ handling reads and clears status, emits threshold events, and sets `read_data_available` to unblock a concurrent polled read.

## State and Persistence Behavior

State includes the runtime PM active/suspended state, GTS tables, regmap field selections, and `read_data_available`. Event enable holds a runtime PM reference until disabled. Autosuspend delay is 5 seconds. Teardown disables adaptive thresholding, interrupts, and sensor power.

## Dependencies and Integration Points

The driver depends on I2C regmap, regmap fields, regulator `vdd`, runtime PM, IIO events/sysfs, unaligned 24-bit helpers, `IIO_GTS_HELPER`, and OF compatible `"avago,apds9306"`.

## Risks and Edge Cases

Only known part IDs get GTS multipliers; unknown IDs fail init. The code intentionally avoids software reset because it causes I2C bus errors. Concurrent status reads between IRQ and sysfs are coordinated by `read_data_available` but remain timing-sensitive. This snapshot shows duplicated lines in threshold get and part-ID error handling, which are review/build signals.

## Test Signals

Test both part IDs, GTS scale tables, integration-time changes that adjust gain, sample-frequency values from 0.5 Hz to 40 Hz, runtime suspend/resume, IRQ and polled-read races, threshold/adaptive event enable, no-IRQ operation, and autosuspend reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9306.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9960.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/apds9960.c

## Purpose

`apds9960.c` supports the Avago APDS9960 gesture/RGB/ALS/proximity sensor. It exposes proximity, four gesture FIFO channels, clear/RGB intensity channels, calibration bias, gain/scale, ALS integration time, threshold events, runtime PM, and a kfifo buffer for gesture samples.

## Important APIs, Types, and Functions

- `struct apds9960_data` stores regmap fields, cached event states, gains, integration time, gesture buffer, and calibration biases.
- Regmap tables mark volatile status/data/FIFO registers and precious RAM.
- `apds9960_set_calibbias()`, gain setters, and integration-time setter update registers and caches.
- `apds9960_read_raw()` and `apds9960_write_raw()` implement proximity, intensity, and calibration attributes while blocking direct reads during gesture mode.
- Event callbacks handle 8-bit proximity and 16-bit ALS thresholds and interrupt enables.
- `apds9960_read_gesture_fifo()`, buffer setup ops, and `apds9960_interrupt_handler()` implement buffered gesture capture.
- `apds9960_chip_init()` sets default enables, persistence, gesture FIFO threshold, and gesture enter/exit thresholds.

## Control Flow

Probe sets up the IIO device and kfifo buffer, initializes regmap and runtime PM, powers the device, allocates regmap fields, writes defaults, requires a valid IRQ, registers the threaded IRQ and IIO device, then autosuspends. Direct raw reads power the device around the register read and sleep one ALS integration cycle after resuming. Enabling event interrupts toggles regmap fields and runtime PM references. Enabling the gesture buffer enables gesture interrupt and engine; gesture IRQ drains FIFO records into the IIO buffer.

## State and Persistence Behavior

Software caches event enable flags, gain indices, ALS integration time, calibration biases, and whether gesture FIFO draining is running. Runtime PM controls the global power bit with 5 second autosuspend. Calibration writes update one or two offset registers depending on channel.

## Dependencies and Integration Points

It uses I2C regmap, regmap fields, runtime PM, IIO events, kfifo buffers, ACPI ID `"MSHW0184"`, OF compatible `"avago,apds9960"`, and I2C ID `"apds9960"`.

## Risks and Edge Cases

The driver requires an IRQ; without one probe fails. Gesture FIFO code is sensitive: the helper name has an `apds9660` typo, and the loop expression combines assignment/comparison in a way that deserves testing. This snapshot also shows duplicated regmap config/variable lines and duplicated gesture-mode checks. Direct reads return `-EBUSY` while gesture FIFO draining is active.

## Test Signals

Test probe with and without IRQ, runtime PM transitions, ALS/proximity gain and integration available values, calibration range `s8`, threshold bounds, event enable reference balance, gesture buffer enable/disable, FIFO drain ordering, and interrupt clear writes for ALS/proximity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/apds9960.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/as73211.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/as73211.c

## Purpose

`as73211.c` supports AMS AS73211 XYZ color sensors and AS7331 UVA/UVB/UVC ultraviolet sensors through one shared I2C IIO driver. It provides raw temperature and intensity channels, scale/offset/gain/integration/sampling-frequency controls, optional ready IRQ waiting, and triggered-buffer sampling.

## Important APIs, Types, and Functions

- `struct as73211_spec_dev_data` selects device-specific channel tables and intensity scale functions.
- `struct as73211_data` caches OSR/CREG registers, completion, mutex, available integration times, and device spec.
- `as73211_req_data()` starts a one-shot measurement, locks the I2C segment to avoid measurement noise, waits by IRQ completion or sleep, validates OSR status bits, and reports overflow/data errors.
- `as73211_intensity_scale()` and `as7331_intensity_scale()` return fractional nW-based scales adjusted by integration time and gain.
- `as73211_read_raw()`, `as73211_read_avail()`, and `_as73211_write_raw()` expose direct attributes.
- `as73211_trigger_handler()` performs one measurement and pushes either XYZ/UV only or temp plus channels.

## Control Flow

Probe matches AS73211 or AS7331, reads and resets OSR, verifies AGEN device/mutation IDs, caches config registers, computes available integration times, powers on, registers power-off cleanup, sets up a triggered buffer, optionally requests a READY IRQ, and registers the IIO device. Direct raw reads claim direct mode, request data, then read the selected output word. Writes claim direct mode, switch to config mode if necessary, update cached CREG bits, and write them back.

## State and Persistence Behavior

Cached OSR/CREG values mirror hardware and are protected by the mutex. `int_time_avail` is recomputed when sampling frequency changes. The completion is reinitialized for IRQ-backed measurements. Power state is stored in the OSR power-down bit and restored by sleep PM.

## Dependencies and Integration Points

The driver depends on I2C SMBus and raw I2C transfers, IIO triggered buffers, completions, firmware match data for AS73211/AS7331, optional IRQs, and simple sleep PM.

## Risks and Edge Cases

The measurement path intentionally locks the I2C segment; other bus users can delay sampling. Without an IRQ it sleeps for integration time plus margin. Overflows in buffered mode saturate intensity channels to `U16_MAX` but direct reads return errors. This snapshot includes duplicated comments and unusual switch brace layout that should be checked by build tests.

## Test Signals

Test both compatible strings, AGEN rejection, direct and buffered reads with and without READY IRQ, overflow/status error mapping, sampling frequency powers of two, gain powers of two, integration-time availability recomputation, scan masks, and suspend/resume power toggling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/as73211.c -->
