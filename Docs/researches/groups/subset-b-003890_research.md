# Research Report: subset-b-003890

Grouped research for the InvenSense IIO IMU drivers under `sources/distributed-fs/ceph-client/drivers/iio/imu/`. Each section is source-tree-aligned and intended to split into its mapped per-file document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_gyro.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_gyro.c

Purpose: implements the gyroscope IIO child device for the ICM42600 family. It exposes 3-axis angular velocity plus a temperature scan channel, scale, sample-frequency, calibration-bias controls, debugfs register access through the core, hardware FIFO watermark/flush hooks, and timestamped buffer push.

Important APIs and functions: `inv_icm42600_gyro_init()` allocates/registers the IIO device and kfifo buffer; `inv_icm42600_gyro_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` implement the IIO ABI; `inv_icm42600_gyro_update_scan_mode()` enables gyro/temp and FIFO bits for buffered capture; `inv_icm42600_gyro_parse_fifo()` decodes shared FIFO packets. Scale tables differ for ICM42686 high-FSR parts. ODR tables map user Hz values to core enum values.

Control flow: direct raw reads claim direct mode, runtime-resume the parent, lock `st->lock`, enable low-noise gyro mode, read one big-endian axis register, reject `INV_ICM42600_DATA_INVALID`, then autosuspend. Scale and calibration writes also claim direct mode; ODR writes update `inv_sensors_timestamp`, reprogram gyro config, recompute FIFO period, and refresh watermark.

State and persistence: mutable state lives in shared `struct inv_icm42600_state` (`st->conf.gyro`, `st->fifo`, DMA buffer) and per-IIO `struct inv_icm42600_sensor_state` (scale table and timestamp state). Calibration bias is persisted in device offset registers, with packed 12-bit fields sharing bytes across axes.

Dependencies and integration: depends on `inv_icm42600_core.c` for power/config/debugfs, `inv_icm42600_temp.c` for temp raw ABI, `inv_icm42600_buffer.c` for FIFO mechanics, IIO kfifo helpers, runtime PM, regmap, and `IIO_INV_SENSORS_TIMESTAMP`.

Risks: offset packing preserves shared nibbles via read-modify-write, so locking and error handling are critical. ODR timestamp update can fail when buffers are active. FIFO parsing assumes packet decoder/temperature high-resolution conversion consistency. Test signals include IIO raw/scale/samp_freq/calibbias sysfs reads/writes, direct-mode rejection while buffered, FIFO watermark/flush behavior, invalid-data handling, and chip-specific scale lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_gyro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_i2c.c

Purpose: provides the I2C transport glue for ICM42600-family devices. It matches I2C/OF IDs, creates an 8-bit regmap using the shared ICM42600 regmap config, performs I2C-specific bus register setup, and enters `inv_icm42600_core_probe()`.

Important APIs and functions: `inv_icm42600_probe()` checks `I2C_FUNC_SMBUS_I2C_BLOCK`, extracts the chip enum from firmware match data, initializes regmap, and calls the core. `inv_icm42600_i2c_bus_setup()` configures interface registers: attempts to enable I3C spike filter without checking the return value because ACK can be affected, clears I3C-only mode, sets I2C/SPI slew rates to 12-36 ns, and disables the SPI side of the serial interface.

Control flow and state: no private persistent state is stored here. Probe delegates all runtime state to the core. The bus setup callback mutates hardware interface registers through `st->map` after core state exists.

Dependencies and integration: Linux I2C core, module device tables, device properties, regmap-I2C, and the exported ICM42600 core namespace. The driver registers as `inv-icm42600-i2c` and imports `IIO_ICM42600`.

Risks and tests: main risks are missing firmware match data, inadequate adapter functionality, and bus setup register writes that can leave the part inaccessible if wrong for the physical bus. Test signals include module autoload by OF/I2C IDs, probe rejection on adapters without block transfers, successful WHOAMI/core probe after bus setup, and absence of SPI contention after I2C setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_spi.c

Purpose: provides SPI transport glue for the ICM42600 family. It identifies supported SPI/OF devices, creates the SPI-specific regmap, configures bus interface registers, and delegates all sensor behavior to the shared core.

Important APIs and functions: `inv_icm42600_probe()` obtains chip match data, initializes `inv_icm42600_spi_regmap_config`, and calls `inv_icm42600_core_probe()`. `inv_icm42600_spi_bus_setup()` enables I3C-related interface bits, clears I3C-only mode, programs I2C/SPI slew rates for SPI operation, and disables the I2C bus path.

Control flow and state: this file is stateless beyond static match tables and module metadata. Hardware state is updated only during the bus setup callback. Runtime PM and IIO devices are owned by the core and children.

Dependencies and integration: Linux SPI core, regmap-SPI, OF/SPI module tables, and `IIO_ICM42600` namespace imports. It registers as `inv-icm42600-spi` with shared `inv_icm42600_pm_ops`.

Risks and tests: SPI has no ACK, so bus setup correctness and WHOAMI validation in the core are the main sanity checks. Test signals include OF/SPI module autoload, successful regmap reads through SPI, I2C path disabled after probe, slew-rate programming, and suspend/resume using the shared PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.c

Purpose: supplies the shared temperature raw/scale/offset IIO implementation used by the ICM42600 accel and gyro child devices.

Important APIs and functions: `inv_icm42600_temp_read_raw()` handles `IIO_CHAN_INFO_RAW`, `SCALE`, and `OFFSET` for `IIO_TEMP`. The internal `inv_icm42600_temp_read()` runtime-resumes the parent, locks shared state, enables temperature reporting through `inv_icm42600_set_temp_conf()`, bulk-reads the big-endian temperature register, and rejects `INV_ICM42600_DATA_INVALID`.

Control flow and state: temperature reads use shared `st->buffer` under `st->lock`. They do not create independent persistent state; hardware temp enablement is reflected through the core configuration. The scale and offset constants encode the datasheet formula `T C = temp / 132.48 + 25`, expressed as IIO milli-degree conversion data.

Dependencies and integration: depends on the ICM42600 core for temp configuration, runtime PM, regmap, IIO channel masks, and `inv_icm42600_temp.h` for channel declaration.

Risks and tests: the hardware marks temperature invalid when both accel and gyro are off; this file returns `-EBUSY`, which userspace must tolerate. Test signals include temp raw read while one motion sensor is active, invalid-data behavior when all sensors are off, correct scale/offset ABI, runtime PM balance, and concurrent buffered operation using the shared lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.h

Purpose: declares the reusable ICM42600 temperature IIO channel macro and raw-read function prototype used by sibling accel/gyro drivers.

Important APIs and types: `INV_ICM42600_TEMP_CHAN(_index)` expands to an `IIO_TEMP` channel with separate `RAW`, `OFFSET`, and `SCALE` info masks and a signed 16-bit scan slot. `inv_icm42600_temp_read_raw()` is exported within the driver object for channel dispatch from accel/gyro `read_raw()` handlers.

Control flow and state: this header has no runtime behavior or storage. Its main integration effect is ABI shape: any child including this macro exposes the same temp channel semantics and scan layout.

Dependencies and integration: includes `<linux/iio/iio.h>` and is consumed by `inv_icm42600_gyro.c`, the corresponding accel implementation, and `inv_icm42600_temp.c`.

Risks and tests: channel definition changes are ABI-visible and affect buffer layout. Test signals include verifying scan indices align with child channel arrays, temp raw/scale/offset sysfs files exist, and buffer record sizes match the child buffer structs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_temp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Kconfig

Purpose: defines kernel configuration symbols for the ICM45600 driver family and its I2C, SPI, and I3C transports.

Important entries: hidden `INV_ICM45600` selects `IIO_BUFFER`, `IIO_KFIFO_BUF`, and `IIO_INV_SENSORS_TIMESTAMP`. `INV_ICM45600_I2C`, `INV_ICM45600_SPI`, and `INV_ICM45600_I3C` are tristate user-visible transport options with bus dependencies and regmap selections. Help text lists supported ICM-45605/606/608/634/686/687/688-P/689 devices and module names.

Control flow and state: this is build-time configuration only. Selecting any transport pulls in the shared core object through `INV_ICM45600`.

Dependencies and integration: integrates with the IIO subsystem, regmap backends, and bus cores. It is paired with the local Makefile that builds the shared object plus transport modules.

Risks and tests: dependency mistakes cause link failures or unusable modules. Test signals include Kconfig visibility under relevant bus configs, all selected transports linking with `inv-icm45600.o`, module autoload metadata, and build coverage for I2C/SPI/I3C combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Makefile

Purpose: maps ICM45600 Kconfig symbols to kernel objects.

Important rules: `inv-icm45600.o` is built when `CONFIG_INV_ICM45600` is selected and contains `inv_icm45600_core.o`, `buffer.o`, `gyro.o`, and `accel.o`. Transport modules are separate: `inv-icm45600-i2c.o`, `inv-icm45600-spi.o`, and `inv-icm45600-i3c.o`.

Control flow and state: build-only; no runtime state. The object split enforces one shared core module namespace and bus-specific entry modules.

Dependencies and integration: must stay aligned with Kconfig symbols and exported namespaces (`IIO_ICM45600`). The core exports chip-info tables and probe/PM symbols used by transport modules.

Risks and tests: omitted object files cause unresolved symbols or missing IIO functionality. Test signals include `make M=drivers/iio/imu/inv_icm45600`, modpost namespace checks, and verifying each transport module imports the shared namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600.h

Purpose: central header for ICM45600-family state, chip descriptions, enums, register definitions, channel helpers, and cross-file prototypes.

Important types: `enum inv_icm45600_sensor_mode`, gyro/accel FSR enums, ODR enum, `struct inv_icm45600_sensor_conf`, shared `struct inv_icm45600_conf`, `struct inv_icm45600_chip_info`, global `struct inv_icm45600_state`, and per-child `struct inv_icm45600_sensor_state`. State includes lock, custom regmap, regulators, mount matrix, config cache, suspended modes, two IIO devices, chip info, interrupt timestamps, FIFO state, and DMA-aligned transfer buffer.

Important APIs: exported chip-info objects, scale tables, `inv_icm45600_core_probe()`, `inv_icm45600_set_accel_conf()`, `set_gyro_conf()`, temp read raw, debugfs, mount matrix, ODR-to-period, and child init/FIFO parse functions.

Integration: register definitions cover direct 8-bit registers and virtual 16-bit banked indirect registers. `INV_ICM45600_TEMP_CHAN()` defines little-endian temp scan slots. The header ties core, buffer, accel, gyro, and transport files together.

Risks and tests: ABI-sensitive channel macro and register constants must match datasheet endianness. State mutations rely on `st->lock`. Test signals include sparse/build checks, FIFO buffer layout validation, chip variant scale-table indexing, PM state restoration, and debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_accel.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_accel.c

Purpose: implements the accelerometer IIO child device for ICM45600 devices. It exposes 3-axis acceleration, temperature, scale, sample frequency, calibration bias, FIFO watermark/flush, and timestamped buffered data.

Important APIs and functions: `inv_icm45600_accel_init()` registers the child and kfifo, selects chip-specific scale tables, sets low-power accel clock behavior, and initializes timestamp state. `inv_icm45600_accel_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` provide IIO ABI. `inv_icm45600_accel_update_scan_mode()` enables accel/temp FIFO bits. `inv_icm45600_accel_parse_fifo()` decodes FIFO packets and pushes little-endian data.

Control flow: direct reads runtime-resume, lock, enable accel in the child-requested power mode, read little-endian axis registers, and reject invalid sentinel data. ODR writes convert user frequency to enum, update timestamp period, reprogram config if enabled, and refresh FIFO period/watermark. Calibration bias uses indirect SYS2 registers with 14-bit signed offsets converted between m/s^2 micro-units and raw steps.

State and persistence: per-child state stores scale table, length, power mode, and timestamp. Shared state stores current accel config and FIFO counts. Calibration writes persist in device offset registers.

Dependencies and risks: depends on core config helpers, buffer helpers, runtime PM, regmap, and timestamp library. Risks include scale index adjustment for non-high-FSR chips, low-power filter sanitization, active-buffer ODR transitions, and offset unit conversion. Test signals: raw/scale/frequency/calibbias sysfs, available lists, FIFO streaming with temp, watermark/flush, invalid-data paths, and chip variants with 16G versus 32G accel range.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.c

Purpose: owns shared FIFO setup, enable/disable sequencing, watermark computation, FIFO reads, packet decoding, parse dispatch, and hardware FIFO flush for ICM45600 accel/gyro children.

Important APIs and functions: `inv_icm45600_fifo_decode_packet()` identifies one-sensor versus two-sensor packets, temp, timestamp, and ODR-change flags. `inv_icm45600_buffer_set_fifo_en()`, `update_fifo_period()`, and `update_watermark()` maintain FIFO configuration. `inv_icm45600_buffer_ops` supplies IIO buffer preenable/postenable/predisable/postdisable callbacks. `inv_icm45600_buffer_fifo_read()`, `fifo_parse()`, `hwfifo_flush()`, and `buffer_init()` are used by IRQ handlers and child hwfifo hooks.

Control flow: preenable runtime-resumes and resets timestamp state. Postenable flushes FIFO, enables FIFO threshold/full IRQs, switches FIFO to stream mode, then enables FIFO interface writes. Predisable reverses stream mode and interrupts, with `fifo.on` as a reference count for the two child devices. Postdisable clears per-sensor FIFO enable bits, zeroes watermarks, powers the sensor off, sleeps for hardware stop time, and drops runtime PM.

State and persistence: `st->fifo` stores reference count, enabled sensor bits, effective watermarks, counts, total bytes, and DMA buffer. Hardware state persists in FIFO config, watermark, and interrupt enable registers.

Risks and tests: packet-size assumptions use the two-sensor packet size for reads/watermarks, extended headers are unsupported and stop parsing, watermark math depends on ODR periods being multiples, and regmap noinc reads may need sample-by-sample fallback. Test signals include simultaneous accel/gyro buffers, single-sensor buffers, overflow/full IRQ logging, flush counts, active suspend/resume, and regmap backends that reject large noinc reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.h

Purpose: declares FIFO state, sensor bit masks, packet data format, validity helper, and buffer API prototypes for the ICM45600 driver.

Important types and APIs: `INV_ICM45600_SENSOR_GYRO`, `ACCEL`, and `TEMP` are FIFO enable bits. `struct inv_icm45600_fifo` tracks FIFO reference count, enabled bits, period, requested/effective watermarks, byte count, sample counts, and data buffer. `struct inv_icm45600_fifo_sensor_data` stores little-endian x/y/z words. `inv_icm45600_fifo_is_data_valid()` rejects all-axis sentinel data. Prototypes expose packet decoding, IIO setup ops, init, enable, watermark, read, parse, and flush.

Control flow and state: no standalone control flow. It defines the state contract used by the core, buffer implementation, and accel/gyro parsers.

Dependencies and integration: relies on IIO, byteorder helpers, and a forward declaration of `struct inv_icm45600_state`. It is included by the core header and buffer users.

Risks and tests: structure field changes affect shared logic across IRQ and child devices. Endianness is little-endian unlike older ICM42600/MPU FIFO formats. Test signals include compile coverage, FIFO validity checks, buffer alignment/record sizing, and correct sample counts for packets containing only one sensor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_core.c

Purpose: shared core for ICM45600 devices. It wraps physical 8-bit regmaps with a 16-bit virtual register regmap, validates and resets chips, manages regulators/runtime PM/system sleep, owns common configuration, IRQ handling, temperature ABI, chip-info exports, and creation of accel/gyro child IIO devices.

Important APIs and functions: indirect-register helpers `inv_icm45600_ireg_read/write()` implement banked access with required delays. `inv_icm45600_set_accel_conf()` and `set_gyro_conf()` sanitize keep-values, force power mode based on ODR, write config/filter registers, and update `PWR_MGMT0`. `inv_icm45600_core_probe()` allocates state, enables regulators, reads mount matrix, creates custom regmap, sets up chip/FIFO/children/IRQ/runtime PM, and exports the probe entry. `inv_icm45600_temp_read_raw()` provides shared temp channel behavior.

Control flow: probe requires named `int1`, optional reset, WHOAMI check, default config, timestamp enable, FIFO init, child init, threaded IRQ, then autosuspend setup. IRQ top half timestamps both IIO devices; thread reads INT status, reads/parses FIFO on threshold/full, and warns on full. Suspend disables streaming and stores sensor modes; resume restores modes/FIFO stream; runtime suspend powers all sensors off and disables VDDIO.

State and persistence: `st->conf`, `st->suspended`, `st->timestamp`, `st->fifo`, regulators, and chip info are persistent driver state. Hardware config persists in PWR, config, filter, FIFO, interrupt, and offset registers.

Risks and tests: indirect register access uses shared buffer and precise delays; custom regmap must not recurse incorrectly. Reset differs by I3C path. FIFO stream restoration order matters. Test signals include I2C/SPI/I3C probe, WHOAMI mismatch handling, runtime PM cycles, system suspend with active buffers, temp reads with all sensors off, IRQ FIFO parsing, and debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_gyro.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_gyro.c

Purpose: implements the gyroscope IIO child device for ICM45600 devices, including direct reads, scale/frequency/calibration ABI, FIFO scan setup, hardware FIFO controls, and FIFO-to-IIO-buffer parsing.

Important APIs and functions: `inv_icm45600_gyro_init()` allocates/registers the IIO device and initializes timestamp state. `inv_icm45600_gyro_read_raw()`, `read_avail()`, `write_raw()`, and `write_raw_get_fmt()` implement IIO callbacks. `inv_icm45600_gyro_update_scan_mode()` enables gyro/temp FIFO routing. `inv_icm45600_gyro_parse_fifo()` consumes shared FIFO packets and pushes timestamped records.

Control flow: direct raw reads runtime-resume, lock, enable gyro using per-child `power_mode`, read little-endian axis data, sign-extend, and reject invalid sentinel values. Scale writes map user values to chip-specific FSR tables, with register index offset for non-high-FSR parts. ODR writes update timestamp periods and FIFO watermarks. Calibration bias converts rad/s nanounits into 14-bit signed indirect SYS1 offset registers.

State and persistence: per-IIO state stores scale table, power mode, and timestamp. Shared state stores current gyro config and FIFO counters. Offset registers persist calibration. FIFO parse uses timestamp helper ODR updates signaled in packet headers.

Dependencies and risks: depends on core config, indirect-register regmap, buffer helpers, runtime PM, and IIO timestamp library. Risks include unit conversion boundary handling, high-FSR/non-high-FSR index offsets, low-power versus low-noise mode coercion, and active-buffer ODR changes. Test signals include all IIO ABI files, calibbias min/max/step, FIFO streaming at multiple ODRs, single/dual sensor packets, hwfifo flush count, and suspend/resume with gyro buffer active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_gyro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i2c.c

Purpose: I2C transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_probe()` checks block I2C functionality, fetches `struct inv_icm45600_chip_info` from firmware match data, initializes an 8-bit regmap over I2C, and calls `inv_icm45600_core_probe(regmap, chip_info, true, NULL)`. Match tables cover all supported 456xx variants and pass chip-info pointers.

Control flow and state: no private runtime state. It asks the core to reset the chip on probe and uses no bus-specific setup callback.

Dependencies and integration: Linux I2C core, regmap-I2C, OF/I2C module tables, shared core PM ops, and `IIO_ICM45600` namespace. Module name is `inv-icm45600-i2c`.

Risks and tests: missing match data or unsupported adapter functionality aborts probe. Since the core requires `int1`, board descriptions must provide an interrupt. Test signals include OF/I2C autoload, chip-info pointer correctness, successful reset/WHOAMI in core, runtime PM through shared ops, and block-transfer functionality rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i3c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i3c.c

Purpose: I3C transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_i3c_probe()` creates an 8-bit I3C regmap, reads WHOAMI directly, matches it against the exported chip-info array, and calls `inv_icm45600_core_probe(regmap, matched_info, false, NULL)`. Static I3C IDs use vendor/extra-info matching.

Control flow and state: no private persistent state. It performs chip selection by WHOAMI rather than firmware-compatible data and tells the core not to soft-reset, which avoids disrupting I3C bus state during attach.

Dependencies and integration: Linux I3C device/master APIs, regmap-I3C, module I3C tables, shared PM ops via `pm_sleep_ptr`, and `IIO_ICM45600` namespace.

Risks and tests: the chip-info scan must stay synchronized with exported variants. WHOAMI read failures or unrecognized IDs abort probe. Core reset is disabled on I3C, so tests should verify default-state assumptions after hotjoin/enumeration. Test signals include I3C autoload, WHOAMI matching for each variant, no-reset probe success, FIFO IRQ operation, and system sleep callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_i3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_spi.c

Purpose: SPI transport module for ICM45600-family devices.

Important APIs and functions: `inv_icm45600_probe()` obtains chip-info match data from SPI/OF tables, initializes an 8-bit SPI regmap, and calls core probe with reset enabled plus `inv_icm45600_spi_bus_setup()`. The bus setup callback writes `DRIVE_CONFIG0` to select a 5 ns SPI slew rate.

Control flow and state: stateless bus glue. Transport-specific hardware mutation is limited to the slew-rate setup callback invoked from the core before/after reset.

Dependencies and integration: Linux SPI core, regmap-SPI, OF/SPI module tables, shared PM ops, exported chip-info objects, and `IIO_ICM45600` namespace. Module registers as `inv-icm45600-spi`.

Risks and tests: SPI probe relies on match data and has no bus ACK beyond regmap reads/WHOAMI in the core. Slew-rate settings can affect signal integrity. Test signals include SPI ID and OF autoload, successful WHOAMI after reset and bus setup, correct namespace imports, runtime PM cycles, and FIFO interrupts over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm45600/inv_icm45600_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Kconfig

Purpose: defines build configuration for the legacy InvenSense MPU6050/MPU6500/ICM206xx/IAM20680 IIO driver family.

Important entries: hidden `INV_MPU6050_IIO` selects IIO buffer, triggered buffer, and timestamp helper support. `INV_MPU6050_I2C` depends on I2C, selects I2C mux support and regmap-I2C, and covers MPU6050/9150, MPU6500/6515/6880/9250/9255, ICM206xx, and IAM20680 devices. `INV_MPU6050_SPI` depends on SPI master and selects regmap-SPI for the SPI-capable subset.

Control flow and state: build-time only. Selecting either bus pulls in the shared core/ring/trigger/aux/magnetometer code.

Dependencies and integration: integrates with IIO triggered-buffer infrastructure, timestamp helper, I2C mux for auxiliary bus, and regmap transports.

Risks and tests: Kconfig coverage must reflect actual bus support; MPU6050 itself is I2C while MPU6000 is SPI. Test signals include allmodconfig builds, transport module link tests, I2C mux symbols available for I2C builds, and modpost namespace checks for `IIO_MPU6050`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Makefile

Purpose: maps MPU6050-family Kconfig symbols to object files.

Important rules: shared `inv-mpu6050.o` includes `inv_mpu_core.o`, `inv_mpu_ring.o`, `inv_mpu_trigger.o`, `inv_mpu_aux.o`, and `inv_mpu_magn.o`. I2C transport module includes `inv_mpu_i2c.o` and `inv_mpu_acpi.o`; SPI transport includes `inv_mpu_spi.o`.

Control flow and state: build-only; it defines the module composition and separates common IIO logic from bus glue.

Dependencies and integration: must align with Kconfig symbols and exported namespace `IIO_MPU6050`. ACPI-specific helper is compiled into only the I2C module.

Risks and tests: missing trigger/ring objects would leave buffered capture unresolved; missing ACPI in I2C would break mux-client support on affected systems. Test signals include module builds for I2C-only, SPI-only, and both, plus modpost namespace/import validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_acpi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_acpi.c

Purpose: ACPI helper for creating secondary I2C client devices behind the MPU I2C mux/gate, mainly for platform-specific auxiliary sensors.

Important APIs and functions: `inv_mpu_acpi_create_mux_client()` inspects ACPI/DMI state and creates an I2C client on `st->muxc->adapter[0]`; `inv_mpu_acpi_delete_mux_client()` unregisters it. Under `CONFIG_ACPI`, ASUS T100TA-specific parsing reads ACPI method `CNF0`; generic processing extracts primary/secondary addresses from ACPI I2C resources. Stub functions are provided when ACPI is disabled.

Control flow and state: the helper stores the created client in `st->mux_client`. It first tries DMI-specific parsing, then falls back to secondary-address extraction for INV6XX-style ACPI nodes. No client is created when no secondary address exists.

Dependencies and integration: Linux ACPI, DMI, I2C ACPI resource parsing, I2C mux created by `inv_mpu_i2c.c`, and shared `inv_mpu6050_state`.

Risks and tests: ACPI package parsing is platform-specific and must avoid creating a duplicate client for the primary MPU address. `i2c_unregister_device(NULL)` behavior depends on caller only invoking delete after setup. Test signals include ASUS T100TA probe, generic ACPI secondary address creation, no-client path, ACPI-disabled build, and remove path cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.c

Purpose: implements internal MPU I2C-master transfers used to access auxiliary devices, especially AKM magnetometers embedded in MPU9x50 parts.

Important APIs and functions: `inv_mpu_aux_init()` configures the MPU I2C master clock and slave delays. `inv_mpu_aux_read()` programs SLV0 for a read, runs one master transfer, and reads external sensor data registers. `inv_mpu_aux_write()` programs SLV0 plus output data for a one-byte write. Internal `inv_mpu_i2c_master_xfer()` temporarily sets a 50 Hz divider, enables I2C master, waits one-and-a-half periods, disables it, restores the previous divider, disables SLV0, and checks NACK status.

Control flow and state: uses current `st->chip_config.user_ctrl` and `divider` as the baseline to restore after transfers. Initialization has a legacy MPU9150 level-shifter tweak.

Dependencies and integration: regmap, delay helpers, `inv_mpu_iio.h` register constants, and `inv_mpu_magn.c`. It is part of the shared MPU module, not a Linux I2C adapter itself.

Risks and tests: transfer error paths must restore sample rate, user control, and SLV0 state or the main FIFO rate/magnetometer state can be corrupted. Size is limited to 15 bytes. Test signals include magnetometer probe/read, NACK handling, divider restoration, level-shifter property behavior, and no regression to FIFO sampling rate after aux reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.h

Purpose: declares the MPU auxiliary I2C-master helper API.

Important APIs: `inv_mpu_aux_init()` configures the internal I2C master; `inv_mpu_aux_read()` reads up to 15 bytes from an auxiliary I2C device; `inv_mpu_aux_write()` writes one byte. All take `struct inv_mpu6050_state`, binding calls to the parent MPU register map.

Control flow and state: no runtime behavior; it defines the contract used by the magnetometer implementation.

Dependencies and integration: includes `inv_mpu_iio.h` for state and register definitions. Consumers are in the same shared MPU module.

Risks and tests: prototype changes ripple into magnetometer code. Test signals are compile/link coverage and magnetometer init/read success on MPU9150/9250/9255.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_aux.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_core.c

Purpose: shared core for the legacy MPU6050-family driver. It supports many MPU/ICM/IAM variants, exposes one IIO device with accel/gyro/temp/magnetometer channels as applicable, handles raw/scale/calibration sysfs, sampling frequency, Wake-on-Motion events, chip reset/config, regulator/runtime PM, system sleep, and channel/scan-mask selection.

Important APIs and functions: `inv_mpu_core_probe()` allocates IIO state, resolves orientation/IRQ/regulators, resets and configures the chip, initializes timestamp/magnetometer, sets bus-specific callbacks, runtime PM, triggered buffer/trigger, and registers the IIO device. `inv_mpu6050_switch_engine()` is the central sensor power-state transition function. `inv_mpu6050_read_raw()` and `write_raw()` implement direct IIO ABI. WoM helpers convert threshold units, configure low-power ODR/cycle mode, and expose IIO events.

Control flow: probe validates chip type and WHOAMI, resets hardware, powers down sensors to match software state, initializes FSR/LPF/sample divider/interrupt pin, optionally probes magnetometer, then selects channel tables and scan masks by variant. Direct reads claim direct mode, lock, runtime-resume, enable needed sensors, wait for valid samples, read big-endian registers, and autosuspend. Sampling-frequency writes update divider, timestamp ODR, LPF, magnetometer rate, and WoM threshold.

State and persistence: `struct inv_mpu6050_state` caches chip config, register map, regulators, trigger, timestamp state, FIFO buffer, magnetometer orientation/scales, mux state, suspend masks, and interrupt timestamp. Hardware persists FSR, LPF, divider, offsets, power bits, WoM thresholds, and FIFO settings.

Dependencies and risks: integrates regmap, IIO trigger/buffer, runtime PM, regulators, aux/magnetometer helpers, and transport setup callbacks. Risks include broad chip-variant conditionals, clock switching around gyro power, WoM wakeup suspend paths, channel ABI compatibility, and mutable global scan layouts. Test signals include raw/scale/calibbias/temp/frequency ABI, buffered capture with IRQ trigger, no-IRQ direct-only behavior, WoM event enable/value/wakeup, magnetometer-enabled/disabled paths, runtime autosuspend, and system suspend/resume with active buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_i2c.c

Purpose: I2C transport and auxiliary-bus mux glue for the MPU6050-family driver.

Important APIs and functions: `inv_mpu_probe()` checks SMBus block functionality, resolves chip type from OF/ACPI/I2C IDs, creates an 8-bit I2C regmap, and calls `inv_mpu_core_probe()` with `inv_mpu_i2c_aux_setup()`. After core probe it may allocate an I2C mux gate for the chip’s auxiliary bus and create ACPI secondary clients. `inv_mpu_remove()` tears down mux clients/adapters. `inv_mpu_i2c_aux_bus()` decides whether bypass/mux is exposed, and `inv_mpu_i2c_aux_setup()` enables bypass or disables internal magnetometer use when an `i2c-gate` node exists.

Control flow and state: transport owns no independent state but fills `st->muxc`, `st->mux_client`, and `st->magn_disabled` after core probe. The mux select callback is a no-op because bypass is enabled in chip registers.

Dependencies and integration: Linux I2C, I2C mux, regmap-I2C, OF/ACPI tables, `inv_mpu_acpi.c`, and shared core PM ops. It imports `IIO_MPU6050`.

Risks and tests: internal magnetometer support conflicts with external use of the auxiliary bus, so devicetree `i2c-gate` handling is compatibility-sensitive. Test signals include I2C/OF/ACPI autoload, bypass bit set for aux bus, mux adapter creation/removal, ACPI secondary client creation, and magnetometer disabled fallback channel table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h

Purpose: central header for the MPU6050-family driver. It defines register maps, supported chip enums, state/config structs, register constants, scan indices, filter/FSR enums, frequency macros, and cross-file prototypes.

Important types: `struct inv_mpu6050_reg_map` abstracts variant register addresses. `enum inv_devices` lists supported MPU/ICM/IAM parts. `struct inv_mpu6050_chip_config` caches current clock, FSR, LPF, enabled sensors, FIFO bits, divider, user control, and WoM threshold. `struct inv_mpu6050_hw` carries WHOAMI, name, register map, defaults, FIFO size, temp conversion, and startup times. `struct inv_mpu6050_state` is the global driver state for IIO, trigger, mux, orientation, regmap, timestamp, regulators, magnetometer, suspend masks, data buffer, and IRQ timestamp.

Important macros and APIs: sensor masks, register bit definitions, FIFO size constants, temp conversions, frequency/divider conversion helpers, scan indices, FSR/filter enums, and prototypes for FIFO, trigger, engine switching, ACPI, and core probe.

Integration: included by every MPU6050 source file and exported to transport modules. It encodes ABI-relevant scan indices and register semantics.

Risks and tests: changes affect all variants and can silently break scan layout, FIFO sizes, or PM logic. Test signals include all transport builds, channel scan-index validation, variant WHOAMI/default config selection, FIFO datum size calculations, and KABI-visible IIO sysfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_iio.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.c

Purpose: supports embedded AKM magnetometers on MPU9150/9250/9255 parts through the MPU auxiliary I2C master.

Important APIs and functions: `inv_mpu_magn_probe()` initializes aux master, verifies the AKM WHOAMI, reads fuse sensitivity adjustment values, configures SLV0 to read 7-byte data/status blocks, and configures SLV1 to trigger single measurements. `inv_mpu_magn_set_rate()` limits magnetometer sampling to 50 Hz by programming I2C master delay. `inv_mpu_magn_set_orient()` derives magnetometer mount matrix from the main chip orientation with x/y swap and z inversion for MPU9x50. `inv_mpu_magn_read()` validates aux NACK status and reads one axis from external sensor data registers.

Control flow and state: supported chips only; others are no-ops or `-ENODEV`. Probe computes `st->magn_raw_to_gauss[3]` from ASA fuse values and stores `st->magn_orient`.

Dependencies and integration: depends on `inv_mpu_aux.c`, shared state/register constants, and IIO mount matrix/scale callbacks in core. Channel tables in core expose magnetometer channels only when not disabled by aux-bus use.

Risks and tests: aux master setup must preserve main sample rate, byte swap/group settings must match AKM data layout, and orientation string negation uses devm allocations. Test signals include MPU9150 13-bit and MPU9250/9255 16-bit scale, magnetometer raw reads, NACK/error handling, sampling-rate delay updates, and orientation matrix correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.h

Purpose: declares magnetometer helper APIs and the scale helper for MPU9x50 embedded magnetometers.

Important APIs: `INV_MPU_MAGN_FREQ_HZ_MAX` caps magnetometer sampling at 50 Hz. `inv_mpu_magn_get_scale()` returns per-axis Gauss scale from `st->magn_raw_to_gauss[chan->address]` in micro units. Prototypes cover probe, rate update, orientation derivation, and raw read.

Control flow and state: header-only inline scale helper reads cached state; no independent storage.

Dependencies and integration: includes `inv_mpu_iio.h` and is consumed by `inv_mpu_core.c` and `inv_mpu_magn.c`.

Risks and tests: the scale helper assumes channel `address` indexes the 3-axis scale array; channel definitions must keep that consistent. Test signals include scale reads for X/Y/Z, compile coverage, and magnetometer channel ABI on supported variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_magn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_ring.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_ring.c

Purpose: triggered-buffer poll function for moving hardware FIFO samples into IIO buffers for the MPU6050-family driver.

Important APIs and functions: `inv_mpu6050_read_fifo()` is the IIO triggered buffer bottom half. Internal `inv_reset_fifo()` disables and re-enables FIFO via `inv_mpu6050_prepare_fifo()` and re-enables data-ready interrupts on failure.

Control flow: on trigger, lock shared state, compute bytes per datum from enabled accel/gyro/temp/magnetometer FIFO bits, read FIFO count, reset if near overflow, process only complete records, update timestamp state from pollfunc timestamp and current FIFO period, noinc-read FIFO data, skip configured startup samples, copy each packed record into a zeroed aligned buffer, pop timestamps, and push to IIO buffers. Always notifies trigger done.

State and persistence: uses `st->data` as the hardware FIFO read buffer, `st->chip_config.*_fifo_enable` for layout, `st->skip_samples` for startup discard, and `st->timestamp` for time reconstruction. Hardware FIFO state is reset on overflow.

Dependencies and integration: IIO triggered buffer, timestamp helper, regmap noinc reads, and trigger setup code outside this file.

Risks and tests: bytes-per-datum must match active scan mask and FIFO enable bits; overflow reset loses data but prevents stale packing. Test signals include buffered accel/gyro/temp/magn combinations, FIFO overflow warning/reset, startup sample skipping, timestamp monotonicity, and trigger completion on errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_ring.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_spi.c

Purpose: SPI transport glue for SPI-capable MPU6050-family devices, registered as `inv-mpu6000-spi`.

Important APIs and functions: `inv_mpu_probe()` resolves chip type from SPI ID or OF data, initializes an 8-bit SPI regmap, and calls `inv_mpu_core_probe()` with `inv_mpu_i2c_disable()` as bus setup. `inv_mpu_i2c_disable()` disables the chip’s I2C interface using either a dedicated I2C_IF register on ICM20602-style parts or the `USER_CTRL` I2C disable bit.

Control flow and state: stateless transport file. It mutates `st->chip_config.user_ctrl` when disabling I2C through `USER_CTRL`, keeping the cache aligned for later core operations.

Dependencies and integration: Linux SPI, regmap-SPI, OF/SPI/ACPI device tables, shared core PM ops, and `IIO_MPU6050` namespace. Supported IDs include MPU6000/6500/6515/6880/9250/9255 and multiple ICM/IAM parts.

Risks and tests: bus setup must disable I2C at the correct register for the variant or SPI operation may conflict. Probe must handle ID versus firmware match naming. Test signals include SPI/OF/ACPI autoload, successful WHOAMI after I2C disable, runtime PM, raw IIO reads over SPI, and buffered capture with IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_spi.c -->
