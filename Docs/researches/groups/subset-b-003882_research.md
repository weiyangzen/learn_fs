# subset-b-003882 research

Grouped research report for Linux IIO SSP common sensor hub code, ST sensor common helpers, and selected DAC drivers under `sources/distributed-fs/ceph-client/drivers/iio`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_dev.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_dev.c

## Purpose
`ssp_dev.c` is the Samsung SSP sensorhub SPI parent driver. It owns device-tree parsing, MFD child creation for SSP IIO consumers, MCU reset/firmware revision checks, MCU initialization, watchdog recovery, suspend/resume, and the exported sensor lifecycle APIs used by child accelerometer/gyroscope style drivers.

## Important APIs, types, and functions
- `struct ssp_instruction` is the packed payload used for sensor add/change-delay instructions: delay, batch latency, and batch option.
- `ssp_rinato_info` and `ssp_thermostat_info` bind compatible strings to firmware names, expected firmware revisions, and the magnetic calibration table.
- `sensorhub_sensor_devs` creates `ssp-accelerometer` and `ssp-gyroscope` MFD children.
- Exported `ssp_get_sensor_delay()`, `ssp_enable_sensor()`, `ssp_change_delay()`, `ssp_disable_sensor()`, and `ssp_register_consumer()` are the main child-driver interface under namespace `IIO_SSP_SENSORS`.
- `ssp_probe()` wires the SPI mode, locks, pending list, watchdog work/timer, threaded IRQ, firmware validation, and MCU initialization.
- `ssp_suspend()` and `ssp_resume()` notify the MCU about AP state and manage IRQ/watchdog state.
- `ssp_initialize_mcu()` verifies chip ID, pushes the magnetic matrix, reads available sensors and firmware revision, then asks the MCU to check dump state.

## Control flow
Probe parses GPIOs and matched sensorhub info, adds MFD children, configures SPI mode 1, initializes per-sensor delay/batch/status arrays, requests a falling-edge threaded IRQ, enables IRQ wake, checks firmware revision, and initializes the MCU. Sensor enable builds an `ssp_instruction` and either sends an add instruction, changes delay for a running sensor, or moves unknown states back to add state. Disable sends a remove instruction, clears `sensor_enable`, resets check state, and may stop the watchdog when the atomic enable refcount reaches zero. Watchdog timer periodically queues reset work if timeout or communication-failure counters exceed thresholds. Refresh work reinitializes the MCU after reset requests and then resynchronizes enabled sensors and last AP/resume state.

## State and persistence behavior
All state is in-memory in `struct ssp_data`: GPIO descriptors, SPI pointer, firmware download state, current firmware revision, available and enabled sensor bitmasks, per-sensor delay/batch/status arrays, sensor IIO device pointers, pending transport list, counters, watchdog timer/work, and last AP/resume state. No durable persistence is written; the driver relies on firmware files and DT properties as external configuration. `enable_refcount` controls watchdog lifetime across enabled sensors, and `check_status[]` tracks the MCU-side lifecycle of each sensor.

## Dependencies and integration points
This file integrates with Linux SPI, GPIO descriptor, IRQ, timer/workqueue, MFD, IIO, module OF matching, and PM frameworks. It depends on `ssp.h` for command constants, sensor types, `struct ssp_data`, and transport helpers implemented in `ssp_spi.c`. Child IIO devices call exported SSP APIs and register themselves through `ssp_register_consumer()`. Firmware identity is checked against `struct ssp_sensorhub_info` selected by `samsung,sensorhub-rinato` or `samsung,sensorhub-thermostat`.

## Risks and edge cases
- `ssp_enable_sensor()` increments `enable_refcount` on every call, including delay changes for already-running sensors; repeated enable/change paths must be balanced by disables or the watchdog can remain active.
- `ssp_disable_sensor()` decrements `enable_refcount` even if the sensor was not enabled, so unexpected child disable calls can underflow the logical count and disrupt watchdog state.
- Firmware mismatch currently fails probe with `-EPERM`; no download path is implemented here despite state names suggesting one.
- Refresh work resynchronizes all bits in `available_sensors`, which appears to mean physically available sensors rather than currently enabled sensors; this can enable more sensors than userspace requested if used as written.
- IRQ wake is enabled during probe and disabled in `ssp_enable_mcu(false)`/remove paths; IRQ wake balance and suspend failures need hardware testing.

## Test signals
Useful signals are successful probe logs for firmware revision and MCU ID, populated MFD children, IIO child registration through `ssp_register_consumer()`, successful enable/change/disable commands, IRQ packet delivery without timeout counter growth, watchdog reset behavior under forced communication failures, and suspend/resume AP-status commands with no unbalanced IRQ warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio.c

## Purpose
`ssp_iio.c` provides common IIO buffer callbacks and data processing for SSP child sensors. It allocates per-sensor scan buffers, maps buffer enable/disable to SSP MCU sensor enable/disable commands, and pushes MCU-provided samples into IIO buffers with reconstructed timestamps.

## Important APIs, types, and functions
- `ssp_common_buffer_postenable()` allocates `ssp_sensor_data.buffer` sized from `indio_dev->scan_bytes` and enables the sensor with its current SSP delay.
- `ssp_common_buffer_postdisable()` disables the SSP sensor and frees the allocated buffer.
- `ssp_common_process_data()` copies sensor payload bytes into the scan buffer, reads a little-endian 32-bit timestamp delta after the payload, and calls `iio_push_to_buffers_with_timestamp()`.
- All three functions are exported in namespace `IIO_SSP_SENSORS`.

## Control flow
IIO buffer setup for a child sensor calls postenable after scan layout is known. The code looks up the parent `ssp_data` via `indio_dev->dev.parent->parent`, allocates a DMA-capable buffer, then asks the SSP parent to enable the sensor. When the SSP IRQ parser receives bypass data, the child driver's `process_data` wrapper can call `ssp_common_process_data()`, which copies raw channel bytes and appends an absolute timestamp derived from the parent timestamp plus the MCU delta. Postdisable reverses the MCU enable and frees the temporary buffer.

## State and persistence behavior
The only persistent runtime state is `struct ssp_sensor_data::buffer`, allocated while the IIO buffer is enabled. The function relies on parent `ssp_data` for delays and transport. There is no file-backed state.

## Dependencies and integration points
This file depends on the IIO buffer/kfifo infrastructure, `linux/iio/common/ssp_sensors.h` for `struct ssp_sensor_data`, and `ssp_iio_sensor.h` for prototypes and conversion helpers. It integrates with `ssp_dev.c` exported sensor lifecycle calls and with `ssp_spi.c` packet delivery.

## Risks and edge cases
- If `ssp_enable_sensor()` fails in postenable, the allocated buffer is not freed before returning the error, which can leak per-enable memory.
- `ssp_common_process_data()` copies `len` bytes into `spd->buffer` without checking that `len <= indio_dev->scan_bytes`; it depends on caller-provided sensor sizes being correct.
- Timestamp delta is read from `buf + len`; callers must ensure the input frame contains the extra SSP time field.
- Parent lookup assumes a fixed MFD/IIO device hierarchy.

## Test signals
Enable an SSP child buffer and confirm allocation succeeds, the parent MCU receives an enable command, samples appear in the IIO buffer with plausible timestamps, and disable frees state and sends the remove command. Fault injection around enable failure should check for leaked `spd->buffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio_sensor.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio_sensor.h

## Purpose
`ssp_iio_sensor.h` is a local helper header for SSP IIO child drivers. It defines standard channel macros, a timestamp channel macro, common buffer/data prototypes, and sampling-frequency conversion helpers.

## Important APIs, types, and functions
- `SSP_CHANNEL_AG()` builds signed 16-bit little-endian modified accelerometer/gyroscope-style channel specs with shared sampling-frequency info.
- `SSP_CHAN_TIMESTAMP()` defines the mixed SSP/IIO 64-bit timestamp channel.
- `ssp_common_buffer_postenable()`, `ssp_common_buffer_postdisable()`, and `ssp_common_process_data()` are declared for child drivers.
- `ssp_convert_to_freq()` converts a delay in milliseconds to IIO integer plus micro fractional frequency.
- `ssp_convert_to_time()` converts IIO integer plus micro fractional frequency back to a millisecond delay.

## Control flow
This header has no runtime control flow outside the inline conversion routines. Child drivers include it to define channel arrays and implement read/write sampling-frequency handlers that translate between IIO frequency representation and SSP millisecond delays.

## State and persistence behavior
No state is stored here. Conversion helpers are pure functions over caller-provided values.

## Dependencies and integration points
The macros require IIO channel definitions and bit macros already available to including C files. The prototypes bind to `ssp_iio.c`; the conversion helpers support `ssp_dev.c` delay commands indirectly through child drivers.

## Risks and edge cases
- `ssp_convert_to_freq()` computes `fractional` from the scaled integer frequency before splitting integer and fractional parts; callers should verify the resulting IIO representation for non-divisible millisecond periods.
- `ssp_convert_to_time()` returns zero for a zero frequency, which a caller could pass through as a special/invalid delay unless validated.
- Channel macros are tailored to 16-bit signed LE data; sensors with different sample layouts need custom specs.

## Test signals
Unit-style checks for representative delays and frequencies are useful: 10 ms should map near 100 Hz, 100 ms near 10 Hz, zero should round-trip as zero. Child channel arrays should expose scan types and timestamp layout expected by IIO tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_iio_sensor.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_spi.c

## Purpose
`ssp_spi.c` implements the SSP AP-to-MCU transport protocol over SPI. It creates command/read/write messages, performs GPIO handshakes, manages pending asynchronous completions, handles threaded IRQ responses, parses MCU data frames, and exposes helper commands used by `ssp_dev.c`.

## Important APIs, types, and functions
- `struct ssp_msg_header` is the packed command header: command, length, options, and data.
- `struct ssp_msg` tracks transfer length/options, pending-list linkage, completion pointer, and DMA-capable buffer.
- `ssp_create_msg()`, `ssp_fill_buffer()`, `ssp_get_buffer()`, and `ssp_clean_msg()` manage message buffers.
- `ssp_do_transfer()` performs the AP/MCU GPIO handshake, writes the header, queues pending transfers, and waits for completion when needed.
- `ssp_irq_msg()` reads MCU response headers, matches pending messages, performs read/write payload phases, or parses MCU-to-AP data frames.
- Exported-to-driver helpers include `ssp_command()`, `ssp_send_instruction()`, `ssp_get_chipid()`, `ssp_set_magnetic_matrix()`, `ssp_get_sensor_scanning_info()`, `ssp_get_firmware_rev()`, and `ssp_clean_pending_list()`.

## Control flow
For AP-originated commands, callers create an `ssp_msg`, `ssp_do_transfer()` lowers the AP-MCU GPIO, writes the header, optionally appends the message to `pending_list`, raises the handshake line, and waits for the IRQ handler to complete the message. `ssp_irq_msg()` reads a small header from the MCU, decodes message type, matches AP read/write replies by options, transfers the payload, handles return-byte write completions, and completes waiters. For MCU-originated writes, it reads the full frame and calls `ssp_parse_dataframe()`, which dispatches bypass sensor data to registered IIO children, debug strings to logging, time-sync updates to parent timestamp state, and reset requests to refresh work.

## State and persistence behavior
Transport state lives in `struct ssp_data`: `comm_lock`, `pending_lock`, `pending_list`, header buffer, handshake GPIOs, `timeout_cnt`, `com_fail_cnt`, `time_syncing`, `timestamp`, and registered child IIO devices. No persistent storage is used. Pending messages are heap allocated per transfer and freed by the caller after completion; `ssp_clean_pending_list()` completes and unlinks outstanding entries during reset/removal.

## Dependencies and integration points
This file depends on SPI core APIs, GPIO descriptor handshakes, kernel completions, lists, mutexes, IIO child data callbacks, and SSP protocol definitions from `ssp.h`. It is tightly coupled to `ssp_dev.c` for lifecycle and refresh scheduling, and to child IIO drivers through `data->sensor_devs[]` and `struct ssp_sensor_data::process_data`.

## Risks and edge cases
- `ssp_offset_map` contains `SSP_UNIMPLEMENTED` entries set to `-1`; if an unimplemented sensor ID appears in bypass data, `idx += -1` can move the parser backward and corrupt parsing.
- `ssp_parse_dataframe()` does not reject unimplemented offsets before advancing, and it treats library data as `idx += len`, which jumps beyond the frame from the current index.
- `ssp_clean_pending_list()` completes pending messages but does not free them; this is correct for callers that own the message, but any unmatched ownership path would leak.
- `ssp_do_transfer()` increments `timeout_cnt` on handshake and completion failures but does not increment `com_fail_cnt`; watchdog behavior depends on other code updating communication failures.
- Matching pending messages only by `options` can be ambiguous if multiple in-flight messages share the same option bits.
- GPIO handshake timeout loops can sleep for roughly 1.5 seconds per state before failing.

## Test signals
Transport tests need real or emulated MCU behavior: WHOAMI read returns `SSP_DEVICE_ID`, firmware/scanning reads decode little-endian values, sensor add/remove instructions complete, MCU bypass frames deliver samples to the correct IIO device, dead/unmatched packets are drained and reported, and reset while transfers are pending wakes waiters without list corruption. Fuzzing `ssp_parse_dataframe()` with unknown sensor IDs and malformed lengths is especially valuable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Kconfig

## Purpose
This Kconfig file defines internal tristate symbols for the STMicroelectronics common IIO sensor helper modules: I2C transport, SPI transport, and core helper library.

## Important APIs, types, and functions
- `IIO_ST_SENSORS_I2C` selects `REGMAP_I2C`.
- `IIO_ST_SENSORS_SPI` selects `REGMAP_SPI`.
- `IIO_ST_SENSORS_CORE` controls the core helper object.

## Control flow
There is no runtime control flow. Sensor-specific drivers select these symbols to pull common support into the build.

## State and persistence behavior
Kconfig state is build configuration only; it does not create runtime state.

## Dependencies and integration points
The symbols integrate with the kernel build system and with the ST sensor Makefile. I2C/SPI helper symbols select the matching regmap backends so transport configuration files can call `devm_regmap_init_i2c()` or `devm_regmap_init_spi()`.

## Risks and edge cases
These symbols have no prompts and are meant to be selected, not user chosen. Missing selects in sensor-specific drivers will lead to unresolved ST helper symbols or missing regmap support.

## Test signals
Build coverage should verify ST sensor drivers selecting these symbols link correctly for built-in and module combinations, especially with `IIO_BUFFER` and `IIO_TRIGGER` enabled or disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Makefile

## Purpose
This Makefile maps ST common Kconfig symbols to kernel objects and composes the core `st_sensors` module from mandatory core code plus optional buffer and trigger helpers.

## Important APIs, types, and functions
- `obj-$(CONFIG_IIO_ST_SENSORS_I2C) += st_sensors_i2c.o`
- `obj-$(CONFIG_IIO_ST_SENSORS_SPI) += st_sensors_spi.o`
- `obj-$(CONFIG_IIO_ST_SENSORS_CORE) += st_sensors.o`
- `st_sensors-y := st_sensors_core.o`
- `st_sensors-$(CONFIG_IIO_BUFFER) += st_sensors_buffer.o`
- `st_sensors-$(CONFIG_IIO_TRIGGER) += st_sensors_trigger.o`

## Control flow
There is no runtime control flow. The build system includes buffer and trigger helper code only when the corresponding IIO framework features are enabled.

## State and persistence behavior
This file controls build artifacts only.

## Dependencies and integration points
It ties the Kconfig symbols to the common helper C files. Sensor-specific drivers depend on the exported namespace `IIO_ST_SENSORS` from the resulting modules.

## Risks and edge cases
If a sensor driver uses trigger or buffer helpers without depending on the matching IIO feature, symbols can be absent. Ordering is mostly conventional; comments ask that DAC entries elsewhere remain alphabetical, but this ST Makefile is small and direct.

## Test signals
Compile representative ST IIO drivers with `IIO_BUFFER=n/y` and `IIO_TRIGGER=n/y` to ensure optional helper symbols match feature availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_buffer.c

## Purpose
`st_sensors_buffer.c` implements a common triggered-buffer poll handler for ST sensor drivers. It reads active scan channels from regmap-backed data registers and pushes aligned samples with timestamps into IIO buffers.

## Important APIs, types, and functions
- `st_sensors_get_buffer_element()` iterates `indio_dev->active_scan_mask`, aligns the output pointer to each channel's storage size, and performs `regmap_bulk_read()` from channel addresses.
- `st_sensors_trigger_handler()` captures hardware or software timestamp, fills `sdata->buffer_data`, pushes it with `iio_push_to_buffers_with_timestamp()`, and notifies trigger completion.
- `st_sensors_trigger_handler()` is exported in namespace `IIO_ST_SENSORS`.

## Control flow
When a trigger fires, the handler selects `sdata->hw_timestamp` for the device's own hardware trigger, otherwise it uses `iio_get_time_ns()`. It reads every enabled scan channel in order, respecting realbits/shift-derived byte count and storage alignment, then pushes the aggregate buffer and completes the trigger.

## State and persistence behavior
The function uses `struct st_sensor_data::buffer_data` as scratch space and reads `hw_timestamp` when own-trigger mode is active. No durable state is changed.

## Dependencies and integration points
It depends on IIO trigger/buffer APIs, `struct st_sensor_data` from `linux/iio/common/st_sensors.h`, and a configured `regmap` supplied by `st_sensors_i2c.c` or `st_sensors_spi.c`.

## Risks and edge cases
- Buffer sizing relies on `ST_SENSORS_MAX_BUFFER_SIZE` and sensor channel definitions matching actual scan bytes.
- Failed `regmap_bulk_read()` returns `-EIO` without pushing data, but trigger completion still occurs.
- Correct alignment depends on each channel's `storagebits` being valid and nonzero.

## Test signals
Use an ST sensor with buffered capture enabled and verify channel ordering, alignment, endian interpretation, timestamps from hardware trigger vs software trigger, and graceful behavior when a regmap read fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.c

## Purpose
`st_sensors_core.c` is the central common library for STMicroelectronics IIO sensor drivers. It provides register field writes, debugfs register access, output-data-rate and full-scale configuration, power/regulator setup, data-ready interrupt routing, raw direct reads, device-name matching, Who-Am-I verification, and sysfs available-value formatting.

## Important APIs, types, and functions
- `st_sensors_write_data_with_mask()` wraps `regmap_update_bits()` with mask shifting.
- `st_sensors_debugfs_reg_access()` supports generic IIO debugfs register read/write.
- `st_sensors_set_odr()`, `st_sensors_set_enable()`, `st_sensors_set_axis_enable()`, `st_sensors_set_fullscale_by_gain()`, and internal full-scale helpers program common sensor settings tables.
- `st_sensors_power_enable()` enables optional `vdd` and `vddio` supplies.
- `st_sensors_init_sensor()` applies platform/firmware data, powers down the device, disables DRDY, sets full scale, ODR, BDU/DAS, open-drain interrupt mode, and all-axis enable.
- `st_sensors_set_dataready_irq()` controls DRDY routing and `hw_irq_trigger` state.
- `st_sensors_read_info_raw()` claims direct mode, powers the sensor, waits boot time, reads an axis, and powers down.
- `st_sensors_get_settings_index()`, `st_sensors_verify_id()`, `st_sensors_sysfs_sampling_frequency_avail()`, and `st_sensors_sysfs_scale_avail()` are exported helpers.

## Control flow
Sensor-specific probe code typically configures bus regmap, selects `sensor_settings`, then calls `st_sensors_init_sensor()`. Initialization parses `st,drdy-int-pin` and `drive-open-drain` firmware properties, validates DRDY pin support, disables the sensor and data-ready IRQ, programs current full-scale and ODR settings, enables BDU/DAS where available, configures open drain, and enables all axes. Runtime sysfs writes call ODR/full-scale/power helpers; direct raw reads temporarily enable the sensor under `odr_lock`.

## State and persistence behavior
State is stored in `struct st_sensor_data`: `regmap`, `sensor_settings`, `current_fullscale`, `enabled`, `odr`, `drdy_int_pin`, `int_pin_open_drain`, `edge_irq`, `hw_irq_trigger`, `hw_timestamp`, `buffer_data`, and `odr_lock`. Register writes persist in the sensor hardware until reset. No filesystem persistence is used.

## Dependencies and integration points
The file depends on IIO core, regmap, firmware/property APIs, regulators, mutexes, and ST shared structs from `linux/iio/common/st_sensors.h`. It is used by many ST accelerometer, gyro, magnetometer, pressure, and IMU drivers. Bus setup comes from the sibling I2C/SPI helper files, and trigger/buffer behavior comes from optional sibling files.

## Risks and edge cases
- `st_sensors_verify_id()` only warns on Who-Am-I mismatch and still returns success; this permits continued probing on unexpected silicon.
- `st_sensors_sysfs_sampling_frequency_avail()` and `st_sensors_sysfs_scale_avail()` write `buf[len - 1] = '\n'`; if no values are available, `len` is zero and this underwrites the buffer.
- `st_sensors_read_info_raw()` may leave the sensor enabled if `st_sensors_read_axis_data()` fails after enabling; the error path jumps to unlock without disabling.
- ODR and power registers can share the same field; `st_sensors_set_odr()` defers writes while disabled in that case, so tests must cover enable-after-ODR-change behavior.
- Firmware property `st,drdy-int-pin` values greater than 2 silently fall back to defaults rather than reporting invalid firmware.

## Test signals
Probe tests should cover regulator enable, name matching, Who-Am-I mismatch warning, init register writes, DRDY pin selection and open-drain configuration. Runtime tests should cover ODR changes while enabled/disabled, direct raw read cleanup on read errors, sysfs available strings for empty/non-empty tables, and data-ready IRQ enable/disable register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.h

## Purpose
`st_sensors_core.h` is a small local header for declarations shared inside the ST common implementation files.

## Important APIs, types, and functions
- Forward declares `struct iio_dev`.
- Declares `st_sensors_write_data_with_mask()`, which trigger code uses to program interrupt polarity and related fields.

## Control flow
No runtime control flow exists in this header.

## State and persistence behavior
No state is defined here.

## Dependencies and integration points
It connects `st_sensors_trigger.c` to the non-public helper implemented in `st_sensors_core.c` without exposing that prototype through the public ST sensors header.

## Risks and edge cases
The header intentionally exposes only one helper. Any additional cross-file local helper use would need to be declared here or moved to the public header if needed by sensor-specific modules.

## Test signals
Build coverage with `CONFIG_IIO_TRIGGER=y` is enough to validate this declaration remains consistent with the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_i2c.c

## Purpose
`st_sensors_i2c.c` provides the common I2C bus setup helper for ST IIO sensor drivers. It initializes an 8-bit register/8-bit value regmap and records I2C device identity/IRQ into the IIO device state.

## Important APIs, types, and functions
- `st_sensors_i2c_regmap_config` is the default 8-bit regmap.
- `st_sensors_i2c_regmap_multiread_bit_config` adds `read_flag_mask = 0x80` for sensors that require a multi-read bit.
- `st_sensors_i2c_configure()` creates the regmap, stores client data, sets `indio_dev->name`, and copies `client->irq` to `sdata->irq`.
- The configure helper is exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific I2C probe code allocates/configures its `iio_dev` and `st_sensor_data`, then calls `st_sensors_i2c_configure()`. The helper chooses the regmap configuration based on `sensor_settings->multi_read_bit`, initializes regmap, and binds the IIO device to the I2C client.

## State and persistence behavior
Runtime state stored here is `sdata->regmap`, `sdata->irq`, `indio_dev->name`, and I2C client driver data. No hardware registers are modified directly by this file.

## Dependencies and integration points
It depends on I2C core, regmap I2C, IIO core, and public `linux/iio/common/st_sensors_i2c.h`. Downstream core helpers use the regmap configured here.

## Risks and edge cases
The helper assumes `sdata->sensor_settings` is populated before call. Incorrect `multi_read_bit` metadata causes multi-byte reads to use the wrong register address protocol.

## Test signals
Probe an ST sensor over I2C with and without `multi_read_bit`, verify regmap reads use the expected read flag, client data points to the IIO device, and IRQ is propagated for trigger allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_spi.c

## Purpose
`st_sensors_spi.c` provides common SPI setup for ST IIO sensor drivers. It handles optional 3-wire SPI configuration, initializes an 8-bit register/8-bit value regmap with optional multi-read flag, and records SPI device identity/IRQ into IIO state.

## Important APIs, types, and functions
- `ST_SENSORS_SPI_MULTIREAD` is the `0xc0` read flag used when sensor metadata requires a multi-read bit.
- `st_sensors_is_spi_3_wire()` checks firmware property `spi-3wire` or legacy platform data.
- `st_sensors_configure_spi_3_wire()` writes the sensor SIM register when provided in settings.
- `st_sensors_spi_configure()` performs 3-wire setup, creates SPI regmap, binds driver data, names the IIO device, and stores the IRQ.
- The configure helper is exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific SPI probes call this after selecting `sensor_settings`. If 3-wire mode is requested and supported by settings, a two-byte SPI write configures the SIM register before regmap creation. The helper then chooses the regmap config based on `multi_read_bit`, initializes regmap, and records bus metadata.

## State and persistence behavior
The file may persistently change the sensor's SIM register for 3-wire mode. Runtime state set in memory includes `sdata->regmap`, `sdata->irq`, `indio_dev->name`, and SPI driver data.

## Dependencies and integration points
It depends on SPI core, property APIs, regmap SPI, IIO core, ST platform data, and public `linux/iio/common/st_sensors_spi.h`. `st_sensors_core.c` uses the configured regmap for all later sensor operations.

## Risks and edge cases
- If 3-wire is requested but `settings->sim.addr` is zero, the helper silently does nothing; that may be correct for devices auto-configured by wiring, but it can also mask unsupported 3-wire requests.
- Incorrect `multi_read_bit` metadata changes every bulk read protocol.
- The pre-regmap raw `spi_write()` for SIM setup bypasses regmap locking/cache behavior, which is appropriate at probe but should remain early-only.

## Test signals
Probe with firmware `spi-3wire`, legacy `spi_3wire`, and normal SPI configurations. Confirm SIM writes occur when expected, regmap uses `0xc0` read flag for multi-read devices, and IRQ/name fields are populated.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_trigger.c

## Purpose
`st_sensors_trigger.c` implements common data-ready trigger allocation and IRQ handling for ST sensors. It timestamps hardware IRQs, filters spurious/shared interrupts with sensor status registers, handles edge vs level IRQ behavior, and registers an IIO trigger for each device.

## Important APIs, types, and functions
- `st_sensors_new_samples_available()` checks the configured DRDY status register/mask, or returns true when no status register exists.
- `st_sensors_irq_handler()` is the top half that captures a timestamp and wakes the thread.
- `st_sensors_irq_thread()` polls the IIO trigger, handles spurious IRQs, and loops for missed edge-triggered samples.
- `st_sensors_allocate_trigger()` allocates/registers the trigger, configures active-low interrupt polarity when supported, requests the threaded IRQ, and attaches the trigger to the IIO device.
- `st_sensors_validate_device()` enforces trigger ownership.
- Both public helpers are exported in namespace `IIO_ST_SENSORS`.

## Control flow
Sensor-specific drivers call `st_sensors_allocate_trigger()` with trigger ops. The helper creates a trigger, examines the IRQ trigger type, may program active-low polarity through `st_sensors_write_data_with_mask()`, rejects edge IRQs without a DRDY status register, adds `IRQF_ONESHOT` for level IRQs, adds `IRQF_SHARED` for open-drain lines with status checking, requests the threaded IRQ, registers the trigger, and stores it on `indio_dev`. At runtime, top half timestamps and bottom half checks whether this sensor has data; if so it calls `iio_trigger_poll_nested()`.

## State and persistence behavior
It updates `struct st_sensor_data` fields `trig`, `hw_timestamp`, and `edge_irq`, and relies on `hw_irq_trigger` set by `st_sensors_set_dataready_irq()`. It may persistently program interrupt active-low bits in the sensor.

## Dependencies and integration points
This file depends on IIO trigger APIs, IRQ APIs, regmap reads, `st_sensors_core.h`, and ST settings structures. It integrates with `st_sensors_buffer.c` through the trigger handler and with `st_sensors_core.c` for DRDY enable/polarity configuration.

## Risks and edge cases
- Edge IRQ mode is rejected without a status register; board firmware must use level interrupts or provide correct status metadata.
- The edge-mode loop can behave like polling at very high sample rates, increasing IRQ thread CPU time.
- Open-drain shared IRQ is only enabled when a status register exists; otherwise shared interrupt setups can misattribute events.
- Unsupported IRQ trigger types are forced to rising edge, which may hide firmware mistakes until runtime.

## Test signals
Test rising/falling/high/low IRQ firmware configurations, open-drain shared IRQ behavior, edge-triggered missed-sample loop, spurious IRQ return paths, and validation that a trigger cannot be attached to a different IIO device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/st_sensors/st_sensors_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/Kconfig

## Purpose
This Kconfig menu declares build-time options for Linux IIO digital-to-analog converter drivers. The researched entries include AD3530R, AD3552R regular/high-speed/library, AD5064, AD5360, AD5380, AD5421, AD5446 SPI/I2C/common, and AD5449, plus many neighboring DAC options.

## Important APIs, types, and functions
- `AD3530R` depends on SPI and selects `REGMAP_SPI`.
- `AD3552R_HS` selects `AD3552R_LIB` and `IIO_BACKEND`.
- `AD3552R_LIB` is an internal shared-library symbol.
- `AD3552R` depends on `SPI_MASTER`, selects `AD3552R_LIB`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.
- `AD5064` supports SPI/I2C combinations through a compound dependency.
- `AD5360`, `AD5421`, and `AD5449` are SPI/SPI_MASTER drivers.
- `AD5380` supports SPI and I2C through regmap selections.
- `AD5446`, `AD5446_SPI`, and `AD5446_I2C` split common core from transport drivers.

## Control flow
There is no runtime control flow. User or defconfig choices select which DAC drivers and support libraries are compiled.

## State and persistence behavior
Only kernel build configuration state is represented.

## Dependencies and integration points
The symbols connect to `drivers/iio/dac/Makefile`, transport frameworks, regmap backends, IIO buffers, IIO backend, SPI offload, DMA buffers, regulators, GPIO, and platform architecture dependencies for other DACs in the menu.

## Risks and edge cases
- Compound dependencies such as `AD5064` and `AD5380` must avoid impossible module combinations when common code registers both SPI and I2C subdrivers.
- Internal library symbols (`AD3552R_LIB`, `AD5446`) are selected by front-end drivers; enabling code that imports their namespaces without the select will fail at link/load time.
- Comments require alphabetical ordering, but the Makefile has some historical ordering differences; new entries should be checked in both places.

## Test signals
Run build matrix coverage for selected drivers as built-in and modules, including `AD3552R_HS` with backend support, `AD3552R` with triggered buffers, `AD5064` with only SPI or I2C enabled, and `AD5446_SPI/I2C` namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/Makefile

## Purpose
This Makefile maps DAC Kconfig symbols to object files for the IIO DAC subsystem.

## Important APIs, types, and functions
- Researched object mappings include `ad3530r.o`, `ad3552r-hs.o`, `ad3552r-common.o`, `ad3552r.o`, `ad5064.o`, `ad5360.o`, `ad5380.o`, `ad5421.o`, `ad5446.o`, `ad5446-spi.o`, `ad5446-i2c.o`, and `ad5449.o`.
- Common/library objects are built through symbols such as `CONFIG_AD3552R_LIB` and `CONFIG_AD5446`.

## Control flow
There is no runtime control flow; the kernel build system includes objects according to Kconfig.

## State and persistence behavior
Build artifact selection only.

## Dependencies and integration points
The file is the build bridge between the DAC Kconfig menu and module objects. It also ensures shared common objects are available for transport-specific modules that import their exported namespaces.

## Risks and edge cases
- If a transport driver selects a common library but the Makefile omits the common object, namespace imports and symbols fail.
- The comment asks new entries to remain alphabetical; ordering should be reviewed when adding drivers, since existing entries around `AD5064` and `AD5446` are not strictly lexicographic by filename.

## Test signals
Compile each researched DAC symbol as `m` and `y`; verify expected module names and that common modules load before namespace importers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3530r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3530r.c

## Purpose
`ad3530r.c` is an SPI regmap IIO output driver for Analog Devices AD3530/AD3530R 8-channel and AD3531/AD3531R 4-channel 16-bit voltage-output DACs. It exposes raw writes/reads, scale, per-channel powerdown controls, optional internal/external reference handling, LDAC update control, and range-doubling setup.

## Important APIs, types, and functions
- `struct ad3530r_state` stores regmap, mutex, per-channel powerdown state, chip info, optional LDAC GPIO, reference voltage, and DMA-aligned transfer buffer.
- `struct ad3530r_chip_info` provides channel table, input register addressing callback, channel count, LDAC register, and internal-reference support flag.
- `ad3530r_dac_write()` writes a big-endian 16-bit channel input register and triggers hardware or software LDAC.
- `ad3530r_read_raw()` supports `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_SCALE`.
- `ad3530r_write_raw()` validates 16-bit raw values and writes them.
- Extended info exposes `powerdown` and `powerdown_mode`.
- `ad3530r_setup()` performs reset, range/reference configuration, normal operating mode setup, default powerdown modes, and LDAC GPIO acquisition.
- `ad3530r_probe()` creates regmap, enables supplies, reads optional `ref`, validates internal reference availability, sets IIO metadata, and registers the device.

## Control flow
Probe initializes regmap and mutex, selects chip info from SPI/OF match data, enables `vdd`/`iovdd`, reads optional external `ref`, rejects non-R variants without an external reference, resets the chip, applies optional `adi,range-double`, selects internal reference if needed, sets all output modes to normal, initializes per-channel powerdown defaults, and registers a direct-mode IIO device. Raw writes call `ad3530r_dac_write()`, which writes the input register and then toggles LDAC or sets the software LDAC bit.

## State and persistence behavior
Runtime state includes per-channel powerdown boolean/mode, vref in millivolts, chip info, and LDAC GPIO. DAC codes are read back from hardware input registers rather than cached. Hardware registers persist until reset; devm-managed regulators/GPIO/regmap clean up on detach.

## Dependencies and integration points
Depends on SPI, regmap SPI, regulator bulk enable, GPIO descriptors, firmware properties, IIO direct mode, sysfs extended info, and device/OF match tables. Kconfig selects `REGMAP_SPI`.

## Risks and edge cases
- `ad3530r_read_raw()` holds `st->lock` while reading; `ad3530r_dac_write()` also serializes writes, which is correct but can block sysfs operations behind slow SPI.
- Powerdown mode changes only update cached mode until `powerdown` is written; this is normal but should be documented for users.
- If `adi,range-double` is set, scale doubles with vref; wrong firmware property causes wrong output scaling.
- Non-R parts require external `ref`; missing regulator correctly fails probe.

## Test signals
Validate probe on R and non-R variants with/without `ref`, raw write and readback for each channel, hardware LDAC vs software LDAC update, `adi,range-double` scale change, and all three powerdown modes reflected in output operating mode registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3530r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-common.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-common.c

## Purpose
`ad3552r-common.c` provides shared model metadata and helper routines for the AD3541R/AD3542R/AD3551R/AD3552R DAC family. It is used by both the standard SPI driver and the high-speed IIO backend driver.

## Important APIs, types, and functions
- Exports `ad3541r_model_data`, `ad3542r_model_data`, `ad3551r_model_data`, and `ad3552r_model_data` in namespace `IIO_AD3552R`.
- `ad3552r_calc_custom_gain()` packs gain scaling and offset polarity/bit fields into the channel gain register value.
- `ad3552r_calc_gain_and_offset()` computes IIO scale and offset for standard or custom output ranges.
- `ad3552r_get_ref_voltage()` selects internal floating, internal 2.5 V output, or external vref input based on regulator/property state.
- `ad3552r_get_drive_strength()` validates `adi,sdo-drive-strength`.
- `ad3552r_get_custom_gain()` parses `custom-output-range-config` child node fields.
- `ad3552r_get_output_range()` parses and validates `adi,output-range-microvolt`.

## Control flow
Consumer drivers select model data by device match, then call common property helpers during setup. Output range parsing returns `-ENOENT` when optional range is missing, allowing consumers to choose custom-gain fallback where appropriate. Scale/offset computation derives IIO values from either model range tables or custom gain formulas.

## State and persistence behavior
The file itself is stateless except for constant model/range tables. It fills caller-owned `struct ad3552r_ch_data` and output parameters. It can enable/read a `vref` regulator through devm helper, so regulator lifetime is tied to the device.

## Dependencies and integration points
Depends on bitfield helpers, device property/fwnode APIs, regulator consumer APIs, and `ad3552r.h`. Exports are consumed by `ad3552r.c` and `ad3552r-hs.c`, both importing namespace `IIO_AD3552R`.

## Risks and edge cases
- `ad3552r_calc_custom_gain()` uses `FIELD_PREP(AD3552R_MASK_CH_OFFSET_BIT_8, abs(goffs))`; because the mask is a single bit, only the low packed bit selected by the mask is represented here while the low offset bits must be written separately by consumers.
- `ad3552r_get_custom_gain()` reads `adi,gain-offset` as `u32` then assigns to `s16`; negative firmware values require correct fwnode interpretation and range validation is absent.
- `ad3552r_get_drive_strength()` returns the raw property-read error for missing property, leaving callers to treat missing as optional.
- External vref tolerance is hard-coded to 2.5 V +/- 100 mV.

## Test signals
Property parsing tests should cover all legal output ranges for AD3542 and AD3552 tables, missing optional range, missing custom-gain child, invalid drive strength, external vref out of tolerance, and scale/offset calculations for bipolar/unipolar/custom ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.c

## Purpose
`ad3552r-hs.c` is the high-speed platform/IIO-backend variant of the AD354x/AD355x DAC driver. It configures a backend-assisted DSPI/QSPI DDR streaming path, exposes raw/scale/offset/sample-frequency IIO attributes, provides debugfs data-source controls, and sequences the DAC/backend between safe SPI-SDR register access and high-speed buffered streaming.

## Important APIs, types, and functions
- `struct ad3552r_hs_state` stores model data, reset GPIO, device, IIO backend, single-channel mode, channel calibration data, platform bus hooks, cached `INTERFACE_CONFIG_D`, and a mutex.
- Platform hooks in `struct ad3552r_hs_platform_data` perform backend bus register read/write and IO mode changes.
- `ad3552r_hs_buffer_postenable()` programs streaming loop length, DDR mode, target/bus DSPI/QSPI mode, backend data address/format, and enables data stream.
- `ad3552r_hs_buffer_predisable()` disables stream and unwinds to simple SPI SDR.
- `ad3552r_hs_setup()` resets, disables backend DDR, validates scratch pad, reads ID, clears reset status, sets reference/drive strength, parses channel nodes, and computes IIO scale/offset.
- `ad3552r_hs_reg_access()` backs debugfs register access with range checks.
- Debugfs files `data_source` and `data_source_available` switch backend external data vs internal ramp.
- `ad3552r_hs_probe()` obtains platform data and backend, requests backend buffer, runs setup, registers IIO device, initializes mutex, and creates debugfs entries.

## Control flow
Probe gets platform bus hooks, enables the backend, matches model data, configures IIO metadata and backend buffer, then initializes the DAC. Buffered enable validates active scan mask, disables single-instruction mode, programs stream loop length and DDR, switches target and bus to dual/quad high-speed mode, tells backend the data register address and format, and starts streaming. Buffered disable reverses the stream, bus mode, DDR bit, backend DDR, target mode, and single-instruction state so debugfs/raw register access works again.

## State and persistence behavior
The driver caches `config_d` because DDR mode cannot be read back. Channel range/gain data lives in `ch_data`. `single_channel` reflects the current active scan mask. Hardware state changes persist until predisable/reset: stream mode, transfer mode, DDR config, reference config, drive strength, output range/custom gain, and backend data source.

## Dependencies and integration points
Depends on platform driver core, IIO backend API, IIO buffers, debugfs, GPIO, firmware child nodes, `ad3552r-common.c` exports, and platform data callbacks from the backend bus provider. It imports namespaces `IIO_BACKEND` and `IIO_AD3552R`.

## Risks and edge cases
- In `ad3552r_hs_setup()`, after `ad3552r_get_ref_voltage(st->dev, &val)`, the code assigns `val = ret`; on success this programs reference selection as zero instead of the parsed value, likely ignoring external/internal-vref selection.
- Probe initializes `st->lock` after registering the IIO device and after debugfs-capable setup paths; debugfs is created after mutex init, but registered IIO callbacks could theoretically run before the mutex is initialized.
- Product ID mismatch only warns and continues, unlike the standard driver that fails probe.
- DDR mode disallows reads; any error unwind that fails to restore `config_d`/backend DDR can leave debugfs/raw reads unsafe.
- `ad3552r_hs_show_data_source_avail()` uses `PAGE_SIZE - len` with a 128-byte local buffer; current strings fit, but the bound is conceptually wrong.

## Test signals
Use backend simulation or hardware to test probe with external/internal vref, scratch-pad mismatch, ID mismatch, active scan masks for channel 0/channel 1/both, postenable error unwind at each backend step, predisable restoration, raw reads before/after streaming, debugfs data-source switching, and sample-frequency calculation from backend clock/lane count/realbits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.h

## Purpose
`ad3552r-hs.h` defines the platform-data contract between the AD3552R high-speed driver and its backend/bus provider.

## Important APIs, types, and functions
- Forward declares `struct iio_backend`.
- `enum ad3552r_io_mode` enumerates SPI, dual-SPI, and quad-SPI bus modes.
- `struct ad3552r_hs_platform_data` provides callbacks for bus register read/write, bus IO mode switching, and the sample data clock rate.

## Control flow
No runtime control flow exists here. The high-speed platform driver calls these callbacks during setup, raw access, streaming enable, and streaming disable.

## State and persistence behavior
The header defines no state itself; backend providers populate platform data with function pointers and clock metadata.

## Dependencies and integration points
It is included by `ad3552r-hs.c` and by whatever platform/backend glue instantiates the high-speed platform device. It also relies on the IIO backend abstraction.

## Risks and edge cases
The callback contract assumes bus providers can safely switch IO modes while the DAC target is sequenced by the driver. Incorrect callback ordering or wrong `bus_sample_data_clock_hz` directly affects streaming mode and reported sample frequency.

## Test signals
Compile backend providers against this header and validate callback invocation order during high-speed postenable/predisable and raw register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r-hs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.c

## Purpose
`ad3552r.c` is the standard SPI IIO driver for AD3541R/AD3542R/AD3551R/AD3552R voltage-output DACs. It supports direct raw read/write, enable/powerdown control, scale/offset reporting, triggered output buffers, reset and scratch-pad validation, product-ID validation, firmware child-node channel configuration, and LDAC hardware/software updates.

## Important APIs, types, and functions
- `struct ad3552r_desc` stores model data, mutex, reset/LDAC GPIOs, SPI device, per-channel data, dynamic channel specs, enabled mask, and channel count.
- `_ad3552r_reg_len()` determines 1/2/3-byte register accesses by address.
- `ad3552r_transfer()`, `ad3552r_write_reg()`, `ad3552r_read_reg()`, and `ad3552r_update_reg_field()` implement raw SPI register access.
- `ad3552r_read_raw()` and `ad3552r_write_raw()` implement raw DAC and enable attributes.
- `ad3552r_write_codes()` and `ad3552r_trigger_handler()` implement buffered output writes.
- `ad3552r_reset()`, `ad3552r_check_scratch_pad()`, `ad3552r_configure_device()`, and `ad3552r_init()` perform hardware setup.
- `ad3552r_probe()` allocates/registers the IIO device and triggered output buffer.

## Control flow
Probe selects model data from SPI/OF match, initializes the mutex, resets the chip, validates scratch-pad read/write, reads product ID, configures reference and drive strength, parses child channel nodes, configures standard or custom output range, computes scale/offset, selects active channels, powers down unused amplifiers, then registers a direct-mode IIO device with output triggered buffer support. Direct raw writes program channel DAC registers. Buffered writes pop scan data from the IIO output buffer and write one or both channel input registers followed by LDAC update.

## State and persistence behavior
Driver state tracks configured channels, range/gain-derived scale/offset, enabled channel bitmask, and optional GPIOs. Hardware state includes reset/config registers, reference selection, SDO drive strength, channel output ranges/custom gain registers, channel select, powerdown config, DAC/input registers, and LDAC state. No filesystem persistence is used.

## Dependencies and integration points
Depends on SPI, GPIO descriptors, IIO direct mode, IIO triggered output buffers, firmware child nodes, polling helpers, unaligned access helpers, and shared AD3552R library exports from `ad3552r-common.c`.

## Risks and edge cases
- `ad3552r_write_codes()` builds a padded local `buff` for 24-bit writes but calls `ad3552r_transfer(..., data, false)` instead of passing `buff`; this can send unpadded buffer data for the single/page write path.
- In `ad3552r_configure_device()`, `dac->ch_data[ch].range = val` stores the field-prepared register value, not the plain range index, for standard output ranges; subsequent scale/offset calculation indexes the range table with that value and can be wrong for channel 1.
- `ad3552r_reset()` writes `FIELD_PREP(AD3552R_MASK_ADDR_ASCENSION, val)` where `val` is the polled register value, not a boolean literal; this deserves review.
- Device child count is used as requested channel count, but duplicate `reg` child nodes are not explicitly rejected.
- Direct raw reads use 24-bit DAC register addresses but only return 16-bit values, matching meaningful data but requiring register-length care.

## Test signals
Test product-ID mismatch failure, standard range parsing for both channels, custom gain parsing, scale/offset for channel 1, raw writes/reads, enable bit toggling, triggered buffer output for single and both channel masks, LDAC GPIO and software LDAC paths, and SPI transfer bytes for padded 24-bit writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.h

## Purpose
`ad3552r.h` is the shared register/model header for the AD354x/AD355x DAC family. It defines register addresses, bit masks, channel constants, model IDs, model-data structures, channel calibration data, enumerations for output ranges and gain/reference selections, and prototypes exported by the common helper library.

## Important APIs, types, and functions
- Register definitions cover primary config/status/power/range/gain registers and secondary 16-bit/24-bit DAC/input/LDAC registers.
- Constants include channel masks, read bit/address mask, scratch-pad test values, gain scale, LDAC pulse timing, max channels/ranges, and SPI lane mode values.
- `enum ad3552r_id` maps expected product IDs.
- `struct ad3552r_model_data` describes model name, chip ID, number of hardware channels, range table, required range property, SPI lane count, and max register address.
- `struct ad3552r_ch_data` stores calculated scale/offset plus custom gain/range fields.
- Enums define gain scaling, vref selection, AD3542 output ranges, and AD3552 output ranges.
- Function prototypes expose output-range/custom-gain/ref/drive-strength parsing and scale/offset calculation.

## Control flow
No runtime control flow exists in this header. It drives register access and setup logic in `ad3552r.c`, `ad3552r-hs.c`, and `ad3552r-common.c`.

## State and persistence behavior
No state is allocated here. The structures define caller-owned runtime state and immutable model metadata.

## Dependencies and integration points
It depends on kernel bit macros and basic device/fwnode types through including C files. It is the key integration contract for the `IIO_AD3552R` namespace.

## Risks and edge cases
- Register length and descending-address semantics for secondary registers are subtle; misuse can produce byte-order or padding bugs.
- `AD3552R_MASK_CH_OFFSET_BIT_8` is defined as `BIT(8)` while several register writes are one byte wide in high-speed code; callers must split low/high offset bits correctly.
- `requires_output_range` differs between AD354x and AD355x model data, so firmware binding validation must be model-specific.

## Test signals
Compile both AD3552R drivers, validate masks with `FIELD_PREP()`/`FIELD_GET()` expectations, and compare generated register addresses for channel 0/1 16-bit and 24-bit regions against datasheet examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad3552r.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5064.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5064.c

## Purpose
`ad5064.c` is a combined SPI/I2C IIO driver for a large family of Analog Devices and LTC multi-channel voltage-output DACs. It abstracts several register-map layouts, raw DAC writes, cached readback for no-read devices, per-channel powerdown modes, internal/external reference handling, and transport-specific driver registration.

## Important APIs, types, and functions
- `enum ad5064_regmap_type` distinguishes old ADI, new ADI2, and LTC command layouts.
- `struct ad5064_chip_info` records shared/internal vref, channel specs, channel count, and register map type.
- `struct ad5064_state` stores device, chip info, regulators, per-channel powerdown/cache state, internal-vref flag, write callback, mutex, and DMA-safe transfer buffers.
- `ad5064_sync_powerdown_mode()` encodes powerdown commands per layout.
- `ad5064_read_raw()` reports cached raw values and scale from internal/external vref.
- `ad5064_write_raw()` validates and writes raw codes, updating `dac_cache`.
- `ad5064_request_vref()` obtains external regulators or enables internal reference through config command.
- `ad5064_probe()` is transport-neutral setup.
- `ad5064_spi_write()` and `ad5064_i2c_write()` encode transport transfers.

## Control flow
Module init registers the SPI subdriver, then the I2C subdriver, unwinding SPI if I2C registration fails. A bus-specific probe maps device ID to `ad5064_type` and calls common probe with a write callback. Common probe allocates IIO state, requests/enables references, configures metadata, initializes raw caches to midscale and powerdown mode to 1 kOhm, then registers the IIO device. Runtime writes use the layout-specific write callback; powerdown sysfs updates cached state and sends the powerdown command.

## State and persistence behavior
The driver caches raw DAC codes because chips do not support readback. It also caches per-channel powerdown booleans/modes and whether internal vref is used. Hardware state persists in DAC input/powerdown/config registers until reset. External regulators are enabled until devm cleanup action disables them.

## Dependencies and integration points
Depends on SPI and/or I2C core based on config, regulators, IIO direct mode/sysfs ext info, unaligned helpers, module init/exit, and chip ID tables. Kconfig allows building when either bus is available while avoiding broken module combinations.

## Risks and edge cases
- `ad5064_i2c_write()` treats any non-negative `i2c_master_send()` result as success; short writes are not detected.
- `ad5064_get_powerdown_mode()` reads cached state without locking, while setters lock; races are minor but visible to sysfs.
- Internal-reference setup assumes at most one external VREF connection for internal-vref chips.
- `ad5064_sync_powerdown_mode()` for LTC layout sets `val = 0` regardless of `pwr_down`; correctness depends on LTC command semantics and should be covered by hardware tests.

## Test signals
Build and probe both SPI and I2C variants, test all supported register-map layouts, verify raw cache updates and scale with shared vs per-channel vrefs, internal-vref fallback, powerdown mode commands, short I2C write fault injection, and module init unwind when one bus registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5360.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5360.c

## Purpose
`ad5360.c` is an SPI IIO driver for AD5360/61/62/63 and AD5370/71/72/73 multi-channel DACs. It supports 8 to 40 output channels, raw writes/readback, scale and offset reporting, calibration gain/bias, global powerdown, grouped offset registers, and multiple VREF supplies.

## Important APIs, types, and functions
- `struct ad5360_chip_info` defines channel template, channel count, channels per VREF group, and number of VREF regulators.
- `struct ad5360_state` stores SPI device, chip info, VREF regulators, cached control register, mutex, and DMA-safe transfer buffers.
- `ad5360_write_unlocked()` and `ad5360_write()` encode 24-bit SPI writes.
- `ad5360_read()` performs readback through the special function readback register and a two-transfer SPI sequence.
- `ad5360_update_ctrl()` maintains and writes the cached control register.
- `ad5360_write_raw()` handles raw, calibration bias/scale, and shared offset writes.
- `ad5360_read_raw()` reads back raw/calibration/offset and computes scale from VREF.
- `ad5360_alloc_channels()` dynamically expands channel specs per model.

## Control flow
Probe selects chip info from SPI ID, allocates IIO state, creates channel specs, requests and enables VREF regulators, registers the IIO device, and records cleanup in remove. Runtime raw/calibration writes encode command/address/value with shifts. Offset writes calculate the VREF group offset register and note that channels sharing a VREF share offset. Readback configures special function readback and clocks out the result with a second SPI transfer.

## State and persistence behavior
State includes enabled regulators, cached control register, dynamic channel array, and SPI transfer buffers. DAC, gain, offset, and control registers persist in hardware. Channel array is manually allocated and freed, not devm-managed.

## Dependencies and integration points
Depends on SPI, regulators, IIO direct mode, sysfs device attributes, mutexes, and manual remove cleanup. Device IDs select model-specific channel count/resolution/VREF topology.

## Risks and edge cases
- Dynamic channels are allocated with `kzalloc_objs()` and manually freed; every probe error path and remove path must stay balanced.
- Offset right/left shifts assume realbits are at least 14 where needed; current table satisfies this.
- Global powerdown is a device attribute, not per-channel ext info.
- Readback relies on SPI `cs_change` timing and two 3-byte transfers; controller quirks can affect it.

## Test signals
Hardware tests should cover all channel-count families, VREF regulator count/topology, raw/calibration readback, grouped offset side effects, global powerdown attribute, probe error cleanup after regulator enable, and remove disabling regulators/freeing channel specs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5360.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5380.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5380.c

## Purpose
`ad5380.c` is a shared SPI/I2C regmap IIO driver for AD5380/81/82/83/84 and AD5390/91/92 multi-channel DACs. It supports direct raw output, calibration gain/bias, scale based on internal or external VREF, powerdown state/mode, dynamic channels, and bus-specific regmap initialization.

## Important APIs, types, and functions
- `struct ad5380_chip_info` records channel template, channel count, and internal vref in millivolts.
- `struct ad5380_state` stores regmap, chip info, selected vref, powerdown flag, and mutex.
- `ad5380_write_dac_powerdown()` writes power-down/up special registers and caches `pwr_down`.
- `ad5380_get_powerdown_mode()`/`ad5380_set_powerdown_mode()` read/write control register mode bit.
- `ad5380_info_to_reg()` maps IIO raw/calibration info to data/offset/gain registers.
- `ad5380_write_raw()` and `ad5380_read_raw()` implement raw, calibration, and scale behavior.
- `ad5380_probe()` is bus-neutral setup with dynamic channel allocation, vref selection, control register programming, and IIO registration.
- SPI and I2C probe wrappers initialize regmap and call common probe.

## Control flow
Module init registers SPI and I2C subdrivers. Bus probe creates regmap using a 10-bit register/14-bit value config with cache. Common probe allocates IIO state, expands channel specs, determines internal/external VREF, writes the special control register with vref bits, then registers the IIO device. Runtime writes go through regmap; reads use regmap cache because readable/volatile callbacks return false.

## State and persistence behavior
State includes regmap cache, selected `vref` in mV, `pwr_down`, mutex, and devm-allocated channels. Hardware control/power/data/gain/offset registers persist until reset. If no external vref regulator exists, internal vref is enabled in the control register.

## Dependencies and integration points
Depends on SPI/I2C, regmap backends, regulators, IIO direct mode and sysfs extended info. Kconfig selects `REGMAP_I2C`/`REGMAP_SPI` as appropriate.

## Risks and edge cases
- Regmap config marks all registers non-readable and non-volatile; read paths may rely on cache rather than hardware readback.
- `ad5380_write_dac_powerdown()` sets `st->pwr_down = pwr_down` even if `regmap_write()` fails.
- Powerdown mode set/get is not protected by `st->lock`, unlike powerdown state.
- Scale uses `2 * st->vref`, so incorrect external regulator voltage directly misreports output scale.

## Test signals
Test SPI and I2C probe, internal-vref fallback, external vref scaling, raw/calibration writes and reads through regmap cache, powerdown mode bit, error injection for powerdown writes, and module init unwind when second bus registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5421.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5421.c

## Purpose
`ad5421.c` is an SPI IIO driver for the AD5421 loop-powered current-output DAC. It exposes current output raw/scale/offset/calibration attributes, temperature/current fault events, control-register management, platform-data current range selection, and optional fault IRQ handling.

## Important APIs, types, and functions
- `struct ad5421_state` stores SPI device, cached control register, current range, fault event mask, mutex, and DMA-safe transfer buffers.
- `ad5421_write_unlocked()`, `ad5421_write()`, and `ad5421_read()` implement 24-bit SPI register access/readback.
- `ad5421_update_ctrl()` maintains the control register cache and writes it.
- `ad5421_fault_handler()` reads fault status, restores control state, pushes IIO events, and polls until active fault bits clear.
- `ad5421_get_current_min_max()` and `ad5421_get_offset()` derive IIO scale/offset from configured current range.
- `ad5421_read_raw()`/`ad5421_write_raw()` expose raw DAC, calibration bias/gain, scale, and offset.
- Event config/value callbacks expose over-current, under-current, and over-temperature thresholds.

## Control flow
Probe allocates IIO state, initializes control bits to disable watchdog and enable auto fault readback, applies platform data for current range/external vref, writes the control register, requests a threaded high-level fault IRQ if present, and registers the IIO device. Runtime raw/calibration operations read/write registers. Fault IRQ reads status, reasserts control register, emits newly asserted enabled events, sleeps while fault-triggering bits remain active, and exits when cleared.

## State and persistence behavior
State includes cached control register, current range, and software `fault_mask`. Hardware DAC, gain, offset, control, and fault status registers persist until reset. Platform data, not firmware properties, controls current range and external vref.

## Dependencies and integration points
Depends on SPI, IIO events, optional IRQ, platform data header `linux/iio/dac/ad5421.h`, mutexes, and sysfs/IIO direct mode.

## Risks and edge cases
- `ad5421_fault_handler()` can sleep one second in a loop while fault bits remain active; a persistent fault can occupy the IRQ thread for a long time.
- Probe ignores the return value from initial `ad5421_update_ctrl()`, so failure to program the control register does not abort registration.
- No OF match table is provided; binding is via SPI modalias/platform data.
- `fault_mask` changes are protected by mutex for writes but read locklessly in the IRQ handler.

## Test signals
Test current range scale/offset for all platform ranges, raw/calibration read/write, initial control write failure injection, fault IRQ event enable masks, persistent fault polling behavior, and operation with no IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5421.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-i2c.c

## Purpose
`ad5446-i2c.c` is the I2C transport front-end for the AD5446 common single-channel DAC core. It supports AD5301/AD5311/AD5321 and AD5602/AD5612/AD5622 style I2C DACs by providing chip metadata and an I2C write callback.

## Important APIs, types, and functions
- `ad5622_write()` writes a 16-bit big-endian DAC word with `i2c_master_send_dmasafe()` and detects short writes.
- `ad5446_i2c_probe()` fetches chip info from I2C/OF match data and calls common `ad5446_probe()`.
- Chip info constants define 8/10/12-bit powerdown-capable channel specs using `AD5446_CHANNEL_POWERDOWN()`.
- I2C ID and OF tables map supported compatible strings to chip info.

## Control flow
The I2C driver probes, resolves chip info, and delegates all common IIO registration and reference handling to `ad5446_probe()`. Runtime raw/powerdown writes from the common core call `ad5622_write()`.

## State and persistence behavior
Transport-specific state is minimal and stored in the common `ad5446_state` transfer buffer. DAC/powerdown state is cached by `ad5446.c` and sent over I2C.

## Dependencies and integration points
Depends on I2C core, OF/device ID matching, and the `IIO_AD5446` namespace exported by `ad5446.c`. It imports that namespace.

## Risks and edge cases
- Probe uses `id->name` for `indio_dev->name`; if a device is matched only through OF without an I2C ID, `i2c_client_get_device_id()` must still be valid in this kernel path.
- All supported I2C variants use the same two-byte write callback; future variants with command bytes would need separate chip info.

## Test signals
Probe every I2C compatible, verify short writes return `-EIO`, raw writes produce expected big-endian 16-bit payloads with proper shifts, and common powerdown sysfs sends encoded powerdown words.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-spi.c

## Purpose
`ad5446-spi.c` is the SPI transport front-end for the AD5446 common single-channel DAC core. It supports many ADI and compatible TI SPI DACs with 16-bit or 24-bit write formats and per-chip channel/reference metadata.

## Important APIs, types, and functions
- `ad5446_write()` sends a 16-bit big-endian value over SPI.
- `ad5660_write()` sends a 24-bit big-endian value over SPI for AD5660/AD5662-like parts.
- `ad5446_spi_probe()` resolves match data and delegates to common `ad5446_probe()`.
- Numerous `struct ad5446_chip_info` constants define resolution, storage, shift, optional internal vref, powerdown support, and write callback.
- SPI ID and OF tables map ADI/TI compatible names to chip info.

## Control flow
Probe resolves chip info from match data and calls the common core. Runtime writes are routed through the chip-specific write callback selected in chip info. The common core handles IIO registration, raw validation, caching, powerdown, and scale.

## State and persistence behavior
Transport state is stored in the common `ad5446_state` DMA-aligned 16/24-bit buffer. Chip metadata is static. DAC and powerdown state are cached in the common core and written to hardware.

## Dependencies and integration points
Depends on SPI, OF/SPI ID matching, unaligned 24-bit writes, and exported common core namespace `IIO_AD5446`.

## Risks and edge cases
- `ad5446_spi_probe()` retrieves `id->name` even though match data comes from SPI/OF; OF-only instantiation still needs a valid SPI ID mapping.
- Many compatibles alias to similar chip info; scale/shift mistakes affect user-visible voltage conversion and wire format.
- 24-bit writes use `put_unaligned_be24()` into a 3-byte buffer, so buffer alignment and DMA safety rely on the union in common state.

## Test signals
Verify 16-bit and 24-bit SPI payloads for representative chips, internal-vref fallback variants, TI compatible aliases, powerdown-capable vs non-powerdown channel ext info, and common raw cache behavior while powered down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.c

## Purpose
`ad5446.c` is the transport-neutral common IIO core for AD5446-like single-channel voltage-output DACs. It provides raw value caching, scale reporting, powerdown sysfs controls, reference-voltage handling, and shared probe logic used by SPI and I2C front-ends.

## Important APIs, types, and functions
- `ad5446_ext_info_powerdown` exposes `powerdown` and `powerdown_mode`; it is exported in namespace `IIO_AD5446`.
- `ad5446_read_raw()` returns cached raw code and scale from `vref_mv`.
- `ad5446_write_dac_raw()` validates, shifts, caches, and writes raw values unless powered down.
- `ad5446_write_dac_powerdown()` toggles cached powerdown state and writes either encoded powerdown mode or cached DAC value.
- `ad5446_probe()` allocates IIO state, initializes mutex and powerdown mode, reads/enables `vcc` regulator or uses chip internal vref, and registers the IIO device.

## Control flow
Transport probe passes device name, chip info, and write callback to `ad5446_probe()`. The common probe sets channel metadata from chip info and determines scale. Runtime raw writes update `cached_val`; if powered down, they do not write hardware until powerdown is cleared. Powerdown writes encode selected mode above the DAC data bits or restore the cached raw value.

## State and persistence behavior
State includes `vref_mv`, `cached_val`, `pwr_down_mode`, `pwr_down`, mutex, and transfer buffer. Since many devices lack readback, raw reads report cache rather than hardware. Hardware state persists until reset; regulator enable is devm-managed.

## Dependencies and integration points
Depends on IIO core, regulators, mutex/cleanup guard helpers, and chip write callbacks supplied by `ad5446-spi.c` or `ad5446-i2c.c`. Exports the common probe and powerdown ext-info namespace for transports.

## Risks and edge cases
- Powerdown mode setters do not lock, while powerdown/raw writers do; racing sysfs writes can briefly use old/new modes unpredictably.
- If no `vcc` regulator exists and no internal vref is defined, probe fails; board descriptions must provide one.
- Cached raw state starts at zero unless set by userspace; if hardware powers up differently, initial raw read may not match hardware.

## Test signals
Test common probe with external and internal vref, raw cache behavior through powerdown cycles, scale for each resolution, powerdown mode encoding, and namespace linkage with both SPI and I2C modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.h -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.h

## Purpose
`ad5446.h` defines the shared interface between the AD5446 common core and its SPI/I2C transport front-ends.

## Important APIs, types, and functions
- `AD5446_CHANNEL()` and `AD5446_CHANNEL_POWERDOWN()` build single-channel IIO voltage output specs with optional powerdown ext info.
- `struct ad5446_state` stores common runtime state, device pointer, chip info, reference voltage, cached DAC value, powerdown mode/state, mutex, and DMA-aligned 16/24-bit transfer buffer.
- `struct ad5446_chip_info` defines channel spec, optional internal vref, and transport write callback.
- `ad5446_probe()` is declared for transport drivers.
- `ad5446_ext_info_powerdown` is declared for chip info that supports powerdown controls.

## Control flow
No runtime control flow exists in the header. Transport drivers instantiate chip info and call the common probe.

## State and persistence behavior
The header defines common state layout but does not allocate it. The transfer buffer union is aligned for DMA-safe bus writes.

## Dependencies and integration points
Depends on IIO channel types, mutex, and kernel integer types. It is included by `ad5446.c`, `ad5446-spi.c`, and `ad5446-i2c.c`.

## Risks and edge cases
The anonymous transfer-buffer union requires users to access `st->d16` or `st->d24` consistently. Chip info write callbacks must honor the channel shift/storage fields in the channel spec.

## Test signals
Compile both transports and verify channel macro expansion for 8/10/12/14/16-bit devices, with and without powerdown ext info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5446.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5449.c -->
# sources/distributed-fs/ceph-client/drivers/iio/dac/ad5449.c

## Purpose
`ad5449.c` is an SPI IIO driver for AD5415/AD5426/AD5429/AD5432/AD5439/AD5443/AD5449 current-output/voltage-output style DACs with one or two channels. It supports raw output writes, optional SDO readback, per-channel VREF regulators, and model-specific resolution/channel count.

## Important APIs, types, and functions
- `struct ad5449_chip_info` defines channel specs, channel count, and whether a control register/SDO is available.
- `struct ad5449` stores SPI device, chip info, VREF regulators, mutex, SDO availability, raw cache, and DMA-safe transfer words.
- `ad5449_write()` sends a 16-bit command/value word.
- `ad5449_read()` performs a two-transfer readback sequence.
- `ad5449_read_raw()` returns hardware readback when SDO exists or cached raw otherwise, and reports scale from the channel VREF regulator.
- `ad5449_write_raw()` validates raw code, writes load-and-update command, and updates cache.
- `ad5449_spi_probe()` requests/enables VREF regulators, configures IIO metadata, enables SDO for control-register chips, and registers the IIO device.

## Control flow
Probe maps SPI ID to chip info, requests `VREF` or `VREFA`/`VREFB` regulators, enables them, initializes IIO metadata and mutex, optionally writes control register zero and marks SDO available, then registers the IIO device. Remove unregisters IIO and disables regulators. Runtime raw writes use command codes derived from channel address; raw reads either issue a read command followed by NOOP or return cached last write.

## State and persistence behavior
State includes regulator handles, `has_sdo`, raw cache, mutex, and transfer buffers. Hardware DAC values and control register persist until reset. The raw cache is authoritative for chips without SDO.

## Dependencies and integration points
Depends on SPI, regulators, IIO direct mode, unaligned/endian helpers, and manual register/remove cleanup. It uses SPI IDs only, with no OF match table in this file.

## Risks and edge cases
- `ad5449_spi_probe()` ignores the return value of the control-register write that enables baseline SDO/control state.
- `has_sdo` is set based on `has_ctrl`; board-level SDO wiring is not separately described, so readback may fail if SDO is not physically connected.
- Raw cache is updated without holding `st->lock` around the cache assignment after `ad5449_write()` returns, so concurrent read/write can see stale values.
- Regulator enable uses manual cleanup; every registration error/remove path must disable supplies.

## Test signals
Test single and dual channel variants, VREF naming, raw write scaling for 8/10/12-bit models, SDO readback vs cache path, control write failure injection, regulator cleanup on IIO registration failure, and remove path regulator disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/dac/ad5449.c -->
