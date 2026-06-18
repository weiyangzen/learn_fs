# Research: subset-b-003881

Grouped research for `subset-b-003881`. Each section preserves the source path in its title and is delimited for deterministic splitting into the mapped source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_core.c

Purpose: shared IIO core for the Sensirion SCD30 CO2, temperature, and relative-humidity sensor. Bus drivers supply a transport-specific `scd30_command_t`; this file owns regulator setup, reset, measurement timing, IIO channels, sysfs calibration attributes, buffering, IRQ/trigger behavior, suspend/resume, and module export of `scd30_probe()`.

Important APIs, types, and functions: `scd30_probe()` allocates `struct iio_dev`, fills `struct scd30_state`, enables `vdd`, resets the chip, optionally installs an IRQ-backed trigger, configures a triggered buffer, reads firmware version, sets the default 2 second interval, starts measurement, and registers the IIO device. `scd30_command_read/write()` wrap the bus callback. `scd30_read_meas()` converts three big-endian IEEE754 words into fixed-point CO2, millidegree C, and milli-percent humidity. `scd30_read_raw()`, `scd30_write_raw()`, `scd30_read_avail()`, and `scd30_write_raw_get_fmt()` implement direct IIO ABI for raw/processed values, pressure compensation output, sample frequency, and temperature calibration bias. Sysfs attributes expose sampling frequency availability, automatic self calibration, and forced recalibration.

Control flow: direct reads claim direct mode, wait for a measurement through IRQ completion or polling, read the measurement, then return the addressed channel. Triggered buffers either read from the own IRQ path or poll before pushing a packed scan plus timestamp. IRQ handling is split: hard IRQ polls the trigger if buffering, otherwise wakes the threaded handler that reads measurements and completes waiters. Suspend stops measurement and disables power; resume powers up and restarts measurement.

State and persistence: runtime state is only in `struct scd30_state`: pressure compensation, measurement interval, cached measurement array, completion, mutex, regulator, IRQ, bus private pointer, and command callback. Device calibration/settings are written to the sensor; this driver does not persist them outside hardware.

Dependencies and integration: depends on IIO core, triggered buffers, triggers, regulator framework, IRQ/completion primitives, and `scd30.h`. Imported by I2C and serdev transports via namespace `IIO_SCD30`.

Risks and test signals: float conversion and fixed-point scaling are central correctness points. IRQ enable/disable is deliberately balanced with `IRQF_NO_AUTOEN`; regressions show up as stuck reads or unbalanced IRQ warnings. Tests should cover direct reads while buffer enabled (`-EBUSY`), sample frequency range conversion, pressure/FRC bounds, suspend/resume restart, CRC/transport error propagation through the callback, and both IRQ and polling measurement paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_i2c.c

Purpose: I2C transport wrapper for the SCD30 core. It translates the abstract `enum scd30_cmd` command callback used by `scd30_core.c` into Sensirion I2C command words, argument framing, CRC8 protection, and separate send/receive transactions.

Important APIs, types, and functions: `scd30_i2c_cmd_lookup_tbl[]` maps core command ids to sensor command words. `scd30_i2c_xfer()` sends the command frame with `i2c_master_send()` and, when a response is expected, receives data with `i2c_master_recv()` because the device does not support repeated start. `scd30_i2c_command()` builds write frames with a big-endian argument and CRC byte, strips arguments for no-argument stop/reset commands, expands expected read length by one CRC byte per 16-bit word, validates received CRCs, and copies only payload bytes into the core response buffer. `scd30_i2c_probe()` checks `I2C_FUNC_I2C`, populates the CRC table, and calls `scd30_probe()`.

Control flow: probe is thin and delegates all IIO registration and power sequencing to the core. Runtime operations always enter via `state->command`; write commands send command plus optional argument, and read commands send command then receive response. Any short transfer or CRC mismatch returns `-EIO`.

State and persistence: this file keeps no per-device private state. The global CRC table is populated at probe. The I2C client, IRQ, name, and device are passed through to the core state.

Dependencies and integration: depends on Linux I2C, CRC8 helpers, unaligned big-endian accessors, and `scd30.h`. The OF compatible is `sensirion,scd30`; the PM ops come from the exported SCD30 core. It imports namespace `IIO_SCD30`.

Risks and test signals: the buffer maximum assumes current response sizes, so new commands need size review. CRC handling must match Sensirion polynomial 0x31 and initial value. Tests should exercise no-argument commands, write argument CRC construction, read payload deinterleaving, short send/recv failures, CRC mismatch, adapter functionality rejection, and operation with an IRQ supplied by firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_serial.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_serial.c

Purpose: serdev transport wrapper for the SCD30 core using the sensor's Modbus-like serial protocol. It provides framing, CRC16 validation, receive-buffer completion, serial-port setup, and delegates IIO behavior to `scd30_probe()`.

Important APIs, types, and functions: `struct scd30_serdev_priv` tracks a completion, current receive buffer, expected byte count, and accumulated count. `scd30_serdev_cmd_lookup_tbl[]` maps abstract core commands to serial register ids. `scd30_serdev_command()` builds read or write frames with device address 0x61, op code 0x03 or 0x06, register, count/value, and little-endian CRC16; it validates echoed write frames or read headers/CRC before copying payload. `scd30_serdev_receive_buf()` appends incoming bytes into the pending response and completes when the expected count arrives. `scd30_serdev_probe()` allocates private state, opens the serdev, sets 19200 baud, disables flow control, sets no parity, resolves optional firmware IRQ, and calls the shared core.

Control flow: all runtime transactions set `priv->buf`, `num_expected`, and `num`, write a frame, and wait up to 200 ms for receive completion. The serdev callback is asynchronous and only consumes bytes for an active transaction. Read measurement uses a larger word count while other reads request one word; stop/reset are encoded as writes of 1.

State and persistence: transport state is transient per transaction in `struct scd30_serdev_priv`; core state holds the private pointer and command callback. No persistent settings are stored by the transport.

Dependencies and integration: depends on serdev, firmware node IRQ lookup, CRC16, unaligned helpers, and `scd30.h`. It shares the same `sensirion,scd30` compatible and imports `IIO_SCD30`.

Risks and test signals: races around `priv->buf` and late bytes can corrupt the next transaction if locking in the core is bypassed; currently the core mutex serializes command use. Tests should cover partial receive completion, timeout, echoed write mismatch, read byte-count mismatch, CRC failure, unexpected op code, ignored unsolicited bytes, and probe behavior without an IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd30_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd4x.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/scd4x.c

Purpose: full I2C IIO driver for Sensirion SCD40/SCD41 CO2 sensors. It handles command transport, CRC8 framing, measurement polling, pressure and temperature compensation, automatic and forced calibration sysfs attributes, triggered-buffer capture, regulator power management, and PM stop/start.

Important APIs, types, and functions: `struct scd4x_state` holds the I2C client, mutex, and regulator. `scd4x_i2c_xfer()`, `scd4x_send_command()`, `scd4x_read()`, `scd4x_write()`, and `scd4x_write_and_fetch()` implement command sequencing and CRC. `scd4x_read_poll()` waits for `CMD_GET_DATA_READY` then reads three 16-bit measurements. `scd4x_read_raw()` exposes CO2 raw plus scale, temperature raw/scale/offset/calibbias, humidity raw/scale, and pressure compensation output. `scd4x_write_raw()` writes temperature offset or ambient pressure. Sysfs attributes expose automatic self calibration and forced recalibration. `scd4x_probe()` powers the device, stops any running measurement, sets up triggered buffering, starts measurement, registers cleanup, and registers the IIO device.

Control flow: many commands require measurement to be stopped, a 500 ms execution delay, and measurement restarted afterward. Measurement reads and data-ready queries are exceptions; ambient pressure can be written/read without stopping. Direct reads claim direct mode before polling. Buffer trigger handler reads a full measurement under the mutex and pushes CO2/temp/humidity plus timestamp.

State and persistence: only mutex, client, and regulator are cached. Calibration, pressure, and temperature offset live in the sensor after writes. The driver does not cache measurement interval; polling uses fixed one-second sleeps with six tries.

Dependencies and integration: depends on I2C, IIO buffers/triggers, CRC8 polynomial 0x31, regulator framework, and OF compatibles `sensirion,scd40` and `sensirion,scd41`.

Risks and test signals: stop/start sequencing around calibration is timing-sensitive and can leave the device stopped on error, though forced calibration tries to restart on failure. The `cmd` parameter to `scd4x_write_and_fetch()` is unused and currently hardwired to FRC. Tests should cover CRC mismatch, data-ready timeout restart, pressure range 700-1200 mbar, FRC failure value, buffer/direct-mode exclusion, regulator cleanup, and suspend/resume measurement restart.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/scd4x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sen0322.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sen0322.c

Purpose: simple regmap-backed I2C IIO driver for the DFRobot SEN0322 oxygen concentration sensor. It exposes one concentration channel with raw and scale values.

Important APIs, types, and functions: `struct sen0322` stores a regmap. `sen0322_read_data()` bulk-reads three BCD-like data bytes at register 0x03 and returns the value multiplied by 100 to avoid floating point. `sen0322_read_scale()` reads coefficient register 0x0a; calibrated devices use `coeff / 100000`, while uncalibrated devices fall back to factory atmosphere/reference current constants `209 / 120000`. `sen0322_read_raw()` dispatches IIO raw and scale requests. `sen0322_probe()` checks I2C functionality, allocates the IIO device, initializes an 8-bit register/8-bit value regmap, fills the single channel, and registers the device.

Control flow: runtime reads are synchronous regmap reads with no caching and no explicit locking beyond regmap internals. The only valid channel type is `IIO_CONCENTRATION`; unknown masks return `-EINVAL`.

State and persistence: the driver stores only the regmap pointer. Calibration coefficient persistence is entirely in the sensor. There is no power management, buffering, trigger, or mutable sysfs state.

Dependencies and integration: depends on I2C, regmap, and IIO direct mode. The OF compatible is `dfrobot,sen0322`; possible hardware addresses are documented as 0x70-0x73.

Risks and test signals: the scale calculation depends on the device coefficient convention and the raw-value x100 scaling matching userspace expectations. Tests should cover regmap read failures, uncalibrated coefficient zero fallback, calibrated coefficient path, raw byte conversion, unsupported channel/mask rejection, and probe failure when the adapter lacks basic I2C functionality.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sen0322.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp30.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp30.c

Purpose: I2C IIO driver for Sensirion SGP30 and SGPC3 gas sensors. It exposes processed IAQ values and raw gas-signal channels, verifies feature-set compatibility, and maintains a background IAQ measurement thread to satisfy the sensors' periodic-measurement requirements.

Important APIs, types, and functions: `struct sgp_data` holds client, mutex, IAQ kthread, feature set, command choices, measurement interval, and raw/IAQ buffers. `sgp_read_cmd()` sends a big-endian command, waits the specified duration, receives CRC-protected words, and calls `sgp_verify_buffer()`. `sgp_measure_iaq()` updates `iaq_buffer` and marks default versus valid IAQ readings after the initialization warm-up window. `sgp_iaq_threadfn()` issues IAQ init once, then repeatedly measures at the product interval. `sgp_read_raw()` exposes processed TVOC/eCO2 when the IAQ buffer is valid and raw ethanol/H2 signals. `sgp_check_compat()` decodes the feature-set product/generation/version fields and rejects engineering or unsupported devices. `sgp_probe()` reads feature set, initializes product-specific channels and commands, registers IIO, and starts the kthread.

Control flow: probe determines product data from OF/I2C match, reads feature set, validates it, registers the device, then starts the IAQ polling thread. Direct user reads use the most recent thread-produced IAQ buffer for processed values; raw SGP30 gas signals trigger immediate commands while SGPC3 ethanol reuses IAQ data.

State and persistence: IAQ buffer state is `EMPTY`, `DEFAULT_VALS`, or `VALID`; warm-up default readings return `-EBUSY`. No baseline or humidity compensation persistence is implemented, matching the file TODO.

Dependencies and integration: depends on I2C, CRC8, kthread, mutex, jiffies timing, and IIO direct mode. Compatibles are `sensirion,sgp30` and `sensirion,sgpc3`.

Risks and test signals: `kthread_run()` result is not checked with `IS_ERR`, so failed thread creation could leave no IAQ updates. Warm-up timing, command endian handling, and CRC validation are correctness-critical. Tests should cover feature-set rejection, default-value `-EBUSY`, thread shutdown in remove, CRC mismatch, raw-channel command selection, and product-specific channel layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp40.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp40.c

Purpose: I2C IIO driver for the Sensirion SGP40 gas sensor. It exposes raw resistance, output temperature and humidity compensation inputs, a resistance calibration bias, and a computed VOC index using integer math.

Important APIs, types, and functions: `struct sgp40_data` stores client, device, relative humidity, temperature, resistance calibration bias, and mutex. `sgp40_measure_resistance_raw()` converts stored humidity and temperature into sensor ticks, adds CRC8 for each word, sends command 0x260f, waits 30 ms, receives resistance ticks, and validates CRC. `sgp40_exp()` approximates exponentials in fixed point; `sgp40_calc_voc()` applies the documented logistic VOC-index estimate around `res_calibbias`. `sgp40_read_raw()` handles raw resistance/temp/humidity, processed VOC, and calibration bias. `sgp40_write_raw()` validates and updates temp, humidity, and bias. `sgp40_probe()` sets defaults of 50 percent RH, 25 C, and bias 30000, then registers the IIO device.

Control flow: every raw resistance or processed VOC read performs a live measurement. Compensation and bias reads/writes operate on driver state under the mutex. Processed VOC reads measure resistance first, then compute a fixed-point VOC result returned as integer plus micro.

State and persistence: temperature, humidity, and calibration bias are volatile driver state; they reset to defaults at probe and are not written to hardware. The sensor measurement itself is stateless apart from command timing.

Dependencies and integration: depends on I2C, CRC8 polynomial 0x31/init 0xff, mutex, IIO direct mode, and OF/I2C ids `sensirion,sgp40` / `sgp40`.

Risks and test signals: fixed-point exponential overflow control and VOC scaling are subtle. Tests should cover compensation bounds, bias bounds, CRC mismatch, send/receive short transfers, default compensation tick conversion, VOC monotonicity around the bias point, and concurrent writes during measurement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sgp40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.c

Purpose: shared IIO core for Sensirion SPS30 particulate matter sensors. Bus-specific I2C and serial files provide a `struct sps30_ops` table; this core owns IIO channels, measurement state, triggered-buffer support, fan-cleaning/sysfs controls, reset sequencing, and exported `sps30_probe()`.

Important APIs, types, and functions: `sps30_float_to_int_clamped()` converts big-endian IEEE754 non-negative PM values to fixed centi-units, clamped to the reliable 3000 ug/m3 limit. `sps30_do_meas()` lazily starts measurement after reset, calls `ops->read_meas()`, and converts requested float words. `sps30_do_reset()` calls transport reset and marks state `RESET`. `sps30_read_raw()` exposes processed PM1, PM2.5, PM4, and PM10 readings and shared scale. Sysfs attributes `start_cleaning`, `cleaning_period`, and `cleaning_period_available` call transport fan-cleaning and cleaning-period operations. `sps30_probe()` allocates the IIO device, initializes state and mutex, resets the chip, logs device info through the transport, registers stop-measure cleanup, sets up triggered buffer, and registers the device.

Control flow: direct PM reads request only enough measurement words for the target channel, while buffer capture always reads all four PM mass concentrations. Cleaning-period writes require a sensor reset before reads show the new value.

State and persistence: core state tracks only `RESET` versus `MEASURING`, mutex, device, transport private pointer, and ops. Cleaning period is persisted in sensor firmware, not cached by this core.

Dependencies and integration: depends on IIO buffer/triggered buffer, mutex, delays, and `sps30.h`. Exported in namespace `IIO_SPS30` for I2C and serdev transport modules.

Risks and test signals: lazy start means first measurement may pay setup cost and failures leave state reset. Float conversion assumes non-negative values and clamps high PM. Tests should cover all channel read lengths, trigger scan mask 0x0f, reset after cleaning-period write, fan-clean input validation, stop cleanup only when measuring, and transport error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.h -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.h

Purpose: private shared header that defines the transport contract between the SPS30 IIO core and its I2C/serial bus wrappers.

Important APIs, types, and functions: `struct sps30_ops` is the bus operation table: start/stop measurement, read measurement words, reset, fan cleaning, read/write auto-cleaning period, and show device information. `struct sps30_state` is the common runtime state shared with transport implementations: a mutex, parent device, measurement state integer, optional private pointer, and `ops`. `sps30_probe()` is declared as the single entry point for transport probes.

Control flow: transport drivers allocate any private bus state, fill an `sps30_ops` instance, then call `sps30_probe(dev, name, priv, ops)`. After that, the core calls the ops under its own mutex for IIO direct reads, sysfs controls, resets, and triggered-buffer reads.

State and persistence: this header documents that `priv` exists mainly for serdev because `dev` driver data is already used for the IIO device. Persistent hardware settings are accessed only through ops; the shared struct itself is volatile.

Dependencies and integration: includes only `linux/types.h` and forward-declares the state shape for chemical SPS30 modules. It is not a public UAPI header; it is a source-local contract under the chemical driver directory.

Risks and test signals: the ops table has no optional-operation markers, so transports must provide every function or the core will dereference NULL. Tests should verify that each transport's ops table is complete, that private state remains valid for the life of the IIO device, and that state changes are serialized by the core mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_i2c.c

Purpose: I2C transport implementation for the SPS30 core. It handles Sensirion I2C command words, CRC8-protected 16-bit word framing, measurement readiness polling, serial/version reporting, and a complete `struct sps30_ops` table.

Important APIs, types, and functions: `sps30_i2c_command()` builds command frames, adds CRC bytes for write arguments, expands read sizes for CRC bytes, validates incoming words, and strips CRC into the caller response. `sps30_i2c_xfer()` uses separate send/receive operations because repeated start is unsupported. Transport ops include `sps30_i2c_start_meas()` requesting big-endian IEEE754 output, `stop_meas()`, `reset()`, `read_meas()`, `clean_fan()`, cleaning-period read/write, and `show_info()`. `sps30_i2c_probe()` checks I2C functionality, populates the CRC table, and delegates to `sps30_probe()`.

Control flow: read measurement sleeps up to one second, checks the measurement-ready command, then reads the requested number of 32-bit float words. Reset sleeps 500 ms and sends a stop command as bus recovery after possible reset glitches. Probe does no IIO setup itself beyond delegating to the core.

State and persistence: there is no per-transport private state. The CRC table is global, and cleaning period persists in the device.

Dependencies and integration: depends on I2C, CRC8 polynomial 0x31, unaligned big-endian helpers, delays, and `sps30.h`. OF and I2C ids identify `sensirion,sps30` / `sps30`; namespace import is `IIO_SPS30`.

Risks and test signals: `sps30_i2c_command()` assumes even argument and response sizes. The read-measure path returns timeout if readiness is false after the fixed sleep. Tests should cover CRC mismatch, short transfers, reset recovery command, serial string NUL termination, firmware version logging, cleaning-period endian handling, and adapter capability rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_serial.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_serial.c

Purpose: serdev transport implementation for the SPS30 core using Sensirion's framed UART protocol. It handles byte stuffing, checksum, asynchronous frame receive, command validation, device info logging, and ops registration.

Important APIs, types, and functions: `struct sps30_serial_priv` stores receive completion, frame buffer, byte count, escape state, and done flag. `sps30_serial_prep_frame()` constructs frames with SOF/EOF 0x7e, address, command, length, escaped payload/checksum, and checksum over bytes after SOF. `sps30_serial_receive_buf()` waits for SOF, unescapes bytes, appends until EOF, and completes a frame. `sps30_serial_frame_valid()` checks minimum size, expected address/command, zero state byte, length, and checksum. Transport ops implement start/stop, reset, read measurement, fan cleaning, cleaning-period read/write, and serial/version info. `sps30_serial_probe()` configures serdev at 115200 baud, no flow control, no parity, then calls `sps30_probe()`.

Control flow: each command prepares and writes a frame, waits up to 20 ms for a completed response frame, validates it, and copies bounded response payload. Measurement reads sleep one second before issuing read; empty measurement responses become `-ETIMEDOUT`.

State and persistence: transport state is volatile per transaction in `struct sps30_serial_priv`; core state holds the private pointer. Cleaning period persists in the sensor.

Dependencies and integration: depends on serdev, completion, min/max helpers, IIO for retrieving `iio_priv()` in the receive callback, and `sps30.h`. It imports namespace `IIO_SPS30` and matches `sensirion,sps30`.

Risks and test signals: escape decoding returns zero for unknown escaped bytes and warns after replacing, so malformed frames should be tested. Timeout is short relative to serial scheduling. Tests should cover escaped SOF/EOF/data bytes, checksum failure, nonzero state, wrong command response, buffer cap behavior, empty measurement frame, and probe serial configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sps30_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sunrise_co2.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/sunrise_co2.c

Purpose: I2C IIO driver for the Senseair Sunrise 006-0-0007 CO2 sensor. It exposes CO2 and chip temperature readings, calibration trigger ext-info, and decoded error-status ext-info while handling the device's unusual wake-up/NAK I2C behavior through custom regmap bus operations.

Important APIs, types, and functions: `struct sunrise_dev` stores client, regmap, mutex, and whether wake-up NAKs may be ignored. `sunrise_regmap_read()` and `sunrise_regmap_write()` perform a wake-up SMBus transaction, delay, then execute the actual block read/write without regmap locking. `sunrise_read_byte/word()` and `sunrise_write_byte/word()` lock the I2C segment to preserve the wake-up session. Calibration helpers write calibration commands and poll status bits with `read_poll_timeout()`. Ext-info handlers implement factory and background calibration writes plus `error_status` and `error_status_available`. `sunrise_read_raw()` exposes CO2 raw/scale and temperature raw/scale. `sunrise_probe()` validates SMBus capabilities, initializes custom regmap, chooses `I2C_M_IGNORE_NAK` if protocol mangling is supported, and registers the IIO device.

Control flow: every register access wakes the sensor first, waits 0.5-1.5 ms, then performs the real operation while holding the adapter segment lock at the wrapper level. Calibration resets the status register, writes the command, then polls for a completion bit for up to 30 seconds.

State and persistence: only regmap/client/mutex/ignore_nak are stored in software. Calibration changes and error status live in hardware.

Dependencies and integration: depends on SMBus byte/block operations, optional protocol mangling, regmap custom bus, IIO ext-info, mutex, and time/poll helpers. OF compatible is `senseair,sunrise-006-0-0007`.

Risks and test signals: wake-up NAK handling is adapter-dependent; without protocol mangling logs may contain expected NAK noise. Calibration may block for a long time. Tests should cover adapters with/without `I2C_FUNC_PROTOCOL_MANGLING`, read/write error paths, byte/word endian conversion, calibration timeout, error bit formatting, and scale ABI values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/sunrise_co2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/vz89x.c -->
# sources/distributed-fs/ceph-client/drivers/iio/chemical/vz89x.c

Purpose: I2C/SMBus IIO driver for SGX Sensortech MiCS VZ89X and VZ89TE VOC sensors. It supports two device formats with different command/read sizes, validity checks, channel layouts, and resistance endianness.

Important APIs, types, and functions: `struct vz89x_data` stores client, chip descriptor, mutex, transfer callback, cached measurement buffer, validity flag, and last update time. `struct vz89x_chip_data` provides device-specific validity function, channels, command, read size, and write size. `vz89x_i2c_xfer()` uses a two-message I2C transfer; `vz89x_smbus_xfer()` is fallback via SMBus word write and byte reads. `vz89x_get_measurement()` enforces the one-Hz polling limit, refreshes the cache, and validates the frame. `vz89x_get_resistance_reading()` extracts 24-bit resistance as little- or big-endian depending on channel scan type. `vz89x_read_raw()` exposes raw concentration/resistance, resistance scale, and concentration offsets. `vz89x_probe()` selects I2C or SMBus transport based on adapter capabilities and registers IIO.

Control flow: user reads lock the device, refresh cached data only if at least one second has elapsed, then decode the requested channel from the cache. Invalid fresh readings return `-EAGAIN`; valid cached readings can be reused within the one-second window.

State and persistence: cache validity and timestamp are driver-local. No settings are written to hardware.

Dependencies and integration: depends on I2C core, SMBus fallback support, mutex, jiffies, and IIO direct mode. OF compatibles are `sgx,vz89x` and `sgx,vz89te`; I2C ids mirror those names.

Risks and test signals: VZ89X validity logic appears permissive for `VOC_short == 0`, matching the comment but worth regression testing. `i2c_transfer()` positive-but-not-2 returns a positive value instead of `-EIO`, so callers see a nonnegative failure as success only if exactly 2; currently `vz89x_get_measurement()` checks `<0`, making short positive transfers a risk. Tests should cover cache timing, both chip variants, invalid CRC/status, SMBus fallback, offsets/scales, and transfer count anomalies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/chemical/vz89x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/Kconfig

Purpose: top-level Kconfig aggregation point for IIO common helper modules. It does not define symbols itself; it sources each common subdirectory so helper libraries and sensor-hub bridges become visible under the IIO configuration tree.

Important entries: sourced submenus are `cros_ec_sensors`, `hid-sensors`, `inv_sensors`, `ms_sensors`, `scmi_sensors`, `ssp_sensors`, and `st_sensors`.

Control flow: Kconfig processing includes this file from the wider IIO Kconfig. Each `source` line delegates dependency expressions, help text, and tristate symbols to the subdirectory.

State and persistence: there is no runtime state. Build configuration state is carried by the symbols declared in the sourced files.

Dependencies and integration: path names assume the Linux kernel source layout `drivers/iio/common/...`. Adding or removing a common helper family requires updating this file and the common Makefile together.

Risks and test signals: ordering is simple but missing a source line hides a whole helper family from configuration. Test signals are `scripts/kconfig/conf` parsing without missing files and menu visibility for each subdirectory symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/Makefile

Purpose: top-level build dispatcher for IIO common helper modules. It includes subdirectories under `drivers/iio/common` so their own Makefiles can add objects based on Kconfig symbols.

Important entries: `obj-y` includes `cros_ec_sensors/`, `hid-sensors/`, `inv_sensors/`, `ms_sensors/`, `scmi_sensors/`, `ssp_sensors/`, and `st_sensors/`. A comment requires alphabetical order.

Control flow: kbuild descends into every listed directory because entries are unconditional `obj-y`; each subdirectory then gates actual object files with `CONFIG_*` symbols.

State and persistence: no runtime state. The file controls build graph inclusion only.

Dependencies and integration: must stay synchronized with `drivers/iio/common/Kconfig`. Since helper modules are shared by multiple sensor drivers, missing a directory prevents selected helper objects from building even if Kconfig enables them.

Risks and test signals: risks are stale ordering or missing directory entries when a helper family is added. Test signals are successful `make drivers/iio/common/` traversal, no kbuild unknown target errors, and all selected common objects appearing in build output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Kconfig

Purpose: Kconfig definitions for ChromeOS EC IIO sensor support. It exposes the shared core and three client drivers for contiguous 3-axis sensors, lid angle, and activity events.

Important symbols: `IIO_CROS_EC_SENSORS_CORE` depends on `SYSFS` and `CROS_EC_SENSORHUB`, and selects `IIO_BUFFER` plus `IIO_TRIGGERED_BUFFER`. `IIO_CROS_EC_SENSORS`, `IIO_CROS_EC_SENSORS_LID_ANGLE`, and `IIO_CROS_EC_ACTIVITY` all depend on the core.

Control flow: users select the core directly or indirectly through feature drivers. Build selection then maps to objects in the local Makefile.

State and persistence: no runtime state; it controls configuration availability and selected build dependencies.

Dependencies and integration: integrates ChromeOS EC sensorhub support with IIO buffering/trigger infrastructure. Help text describes physical 3D sensors, convertible lid-angle reporting, and virtual activity/proximity events.

Risks and test signals: dependency mistakes would allow building without EC sensorhub or buffer support. Test signals include Kconfig dependency resolution, module build for each symbol, and ensuring feature drivers cannot be enabled without `IIO_CROS_EC_SENSORS_CORE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Makefile

Purpose: kbuild rules for ChromeOS EC IIO common and client drivers.

Important entries: `cros-ec-sensors-core-objs` links `cros_ec_sensors_core.o` and `cros_ec_sensors_trace.o` into the core module. The feature objects are gated by `CONFIG_IIO_CROS_EC_SENSORS_CORE`, `CONFIG_IIO_CROS_EC_SENSORS`, `CONFIG_IIO_CROS_EC_SENSORS_LID_ANGLE`, and `CONFIG_IIO_CROS_EC_ACTIVITY`.

Control flow: selecting the core builds a composite object that includes both implementation and tracepoint definition; selecting client drivers builds standalone platform drivers that import the core exports.

State and persistence: no runtime state. It determines module composition and linkage boundaries.

Dependencies and integration: must align with local Kconfig symbols and source exports from `cros_ec_sensors_core.c`. Including tracepoint C in the core object ensures `CREATE_TRACE_POINTS` is compiled exactly once.

Risks and test signals: missing trace object causes unresolved trace symbols; mismatched object names break module builds. Test signals are module build, modpost symbol resolution, and tracepoint availability when the core is loaded.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_activity.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_activity.c

Purpose: platform IIO driver for ChromeOS EC activity sensors, including body detection proximity and significant-motion activity events. It uses the ChromeOS EC sensor core for host-command transport and IIO registration.

Important APIs, types, and functions: `struct cros_ec_sensors_state` embeds core state and dynamic channel metadata. `cros_ec_activity_sensors_read_raw()` reads body-detection state and returns inverted proximity semantics. `cros_ec_activity_read_event_config()` lists enabled activities; `cros_ec_activity_write_event_config()` enables/disables activity reporting. `cros_ec_activity_push_data()` translates EC activity FIFO data into IIO events with the correct channel index and event direction. `cros_ec_sensors_probe()` initializes core state, lists supported activities, builds one channel per supported activity plus timestamp, and registers with `cros_ec_sensors_core_register()`.

Control flow: probe asks the EC for all enabled/disabled activities, creates proximity or activity channels, attaches limited ext-info, then registers a FIFO push callback. Runtime reads and event config commands lock `core.cmd_lock`, set the relevant motion-sense subcommand, and call `cros_ec_motion_send_host_cmd()`. FIFO updates call back into `cros_ec_activity_push_data()` and emit IIO events rather than regular samples.

State and persistence: channel indexes for body detection and significant motion are cached in driver state. Activity enable state is stored by the EC and queried/written via host commands.

Dependencies and integration: depends on ChromeOS EC sensor core, platform data/proto commands, IIO events, and the EC sensorhub FIFO callback path.

Risks and test signals: unknown activity bits are warned and skipped; index handling must remain consistent when multiple activities are present. Tests should cover body detection raw inversion, event enable read/write, significant-motion event direction, unknown activities, no-activity `-ENODEV`, and FIFO event delivery with timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_activity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_lid_angle.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_lid_angle.c

Purpose: platform IIO driver for the ChromeOS EC lid-angle virtual sensor. It exposes a single angle channel plus timestamp and uses the common ChromeOS EC sensor core for host-command setup and registration.

Important APIs, types, and functions: `cros_ec_lid_angle_channels[]` defines an unsigned angle channel and software timestamp. `struct cros_ec_lid_angle_state` embeds the core state. `cros_ec_sensors_read_lid_angle()` sends `MOTIONSENSE_CMD_LID_ANGLE` and copies the EC response value. `cros_ec_lid_angle_read()` handles direct raw reads under `core.cmd_lock`. `cros_ec_lid_angle_probe()` initializes the core as a non-physical device, installs triggered-buffer capture using `cros_ec_sensors_capture`, sets the read callback, and registers the IIO device.

Control flow: direct reads and triggered-buffer captures both call the same `read_ec_sensors_data` callback. The generic core capture path reads active scan data and pushes timestamped buffers.

State and persistence: there is no mutable sensor state beyond core command buffers and callback pointers. The lid angle is computed by the EC and read on demand.

Dependencies and integration: depends on platform device ids for `cros-ec-lid-angle`, `cros_ec_sensors_core_init/register`, and IIO triggered-buffer support.

Risks and test signals: the driver assumes the EC command is available when the platform device exists. Tests should cover direct angle reads, triggered capture path, EC command failure warnings, channel scan layout, and probe cleanup on buffer setup failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_lid_angle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors.c

Purpose: platform IIO driver for ChromeOS EC contiguous 3-axis physical sensors: accelerometers, gyroscopes, and magnetometers. It builds per-axis IIO channels and delegates shared host-command, buffer, FIFO, and ext-info handling to the core.

Important APIs, types, and functions: `struct cros_ec_sensors_state` embeds core state and a four-channel array. `cros_ec_sensors_read()` handles raw axis reads, calibration bias/scale reads, range-derived scale, sample frequency via core fallback, and unit conversion for accel/gyro/mag. `cros_ec_sensors_write()` writes calibration bias/scale, sensor range, and sample frequency through the core. `cros_ec_sensors_probe()` initializes core state, builds X/Y/Z channels according to `core.type`, adds timestamp, chooses LPC shared-memory read for accel/gyro when available or host-command reads otherwise, and registers FIFO push support.

Control flow: all direct reads/writes lock `core.cmd_lock`, set motion-sense subcommands, and call `cros_ec_motion_send_host_cmd()` or core helpers. Buffer data can arrive from EC FIFO through `cros_ec_sensors_push_data()` or from software trigger capture through `cros_ec_sensors_capture()`.

State and persistence: cached calibration arrays, current range, and range-updated flag live in core state. Actual calibration, ODR, and range settings are stored by the EC.

Dependencies and integration: depends on ChromeOS EC sensorhub, IIO core/buffer APIs, and platform ids `cros-ec-accel`, `cros-ec-gyro`, `cros-ec-mag`.

Risks and test signals: scale conversions must match IIO units and EC raw ranges. LPC memory layout supports only accel/gyro as coded. Tests should cover each sensor type, calibration fallback on older ECs, range resume restore, direct reads with both LPC and command paths, sample frequency available list, FIFO push, and channel scan indexes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_core.c

Purpose: shared implementation for ChromeOS EC IIO sensor drivers. It initializes EC motion-sense command state, handles FIFO or triggered-buffer setup, provides common sysfs attributes, exports host-command helpers, supports shared-memory and command data reads, pushes FIFO data into IIO buffers, and provides PM restore behavior.

Important APIs, types, and functions: `cros_ec_sensors_core_init()` allocates command buffers, queries EC command version, reads sensor info for physical devices, sets labels, default calibration scale, frequency availability, FIFO capacity, and chooses FIFO or trigger buffer setup. `cros_ec_sensors_core_register()` registers IIO and optional sensorhub push callback with cleanup. `cros_ec_motion_send_host_cmd()` marshals `param`, executes `cros_ec_cmd_xfer_status()`, emits the tracepoint, and copies responses. `cros_ec_sensors_push_data()` maps EC FIFO samples into active IIO channels. `cros_ec_sensors_read_lpc()` safely reads shared memory using busy/sample-id checks; `cros_ec_sensors_read_cmd()` uses `MOTIONSENSE_CMD_DATA`. `cros_ec_sensors_capture()` is the generic trigger handler. Core read/write helpers implement sample frequency. Ext-info exports provide calibration and sensor id.

Control flow: client probes call core init, set channels and callbacks, then call core register. Runtime host commands are serialized by each client's `cmd_lock`. FIFO-capable systems use EC push callbacks and CLOCK_BOOTTIME timestamps; older systems use software triggers.

State and persistence: core state includes command buffer/response, EC pointer, sensor number/type, calibration arrays, sign vector, frequency list, FIFO size, current range, and callbacks. EC settings persist in firmware; driver state caches values for ABI reads and resume.

Dependencies and integration: depends on ChromeOS EC proto/sensorhub APIs, IIO buffers/triggers/kfifo, tracepoint header, platform data, and exported symbols consumed by cros EC client drivers.

Risks and test signals: command-version negotiation and response size handling are central. Shared-memory reads must avoid torn samples. FIFO timestamps are adjusted when IIO clock differs. Tests should cover version 2 versus 3 frequency data, FIFO and non-FIFO paths, register cleanup, cmd_readmem safe retries, ODR zero FIFO flush, report-latency sysfs, calibration ext-info, tracepoint emission, and resume range restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.c

Purpose: tracepoint definition unit for ChromeOS EC motion-sense host commands used by the IIO common core.

Important APIs, types, and functions: `TRACE_SYMBOL()` and `MOTIONSENSE_CMDS` provide symbolic names for motion-sense subcommands. Defining `CREATE_TRACE_POINTS` before including `cros_ec_sensors_trace.h` emits the actual tracepoint objects.

Control flow: this file is compiled into the `cros-ec-sensors-core` composite module. `cros_ec_motion_send_host_cmd()` in the core calls `trace_cros_ec_motion_host_cmd()`; the tracepoint implementation generated from this file formats events using the symbolic command table.

State and persistence: no runtime sensor state is owned here. Trace enablement and buffers are handled by the kernel tracing subsystem.

Dependencies and integration: must be linked exactly once with the trace header. The command list was generated from `include/linux/platform_data/cros_ec_commands.h`, so it depends on those enum names remaining valid.

Risks and test signals: if new motion-sense commands are added but not listed, traces print numeric fallbacks instead of useful symbols. Test signals are successful build with no duplicate tracepoint definitions and visible `cros_ec_motion_host_cmd` events under ftrace/perf when host commands are issued.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.h

Purpose: trace event declaration header for ChromeOS EC IIO sensor host-command tracing.

Important APIs, types, and functions: `TRACE_EVENT(cros_ec_motion_host_cmd, ...)` records the motion-sense command id, sensor id, data field, transfer return value, and response return field. `TP_printk` uses `__print_symbolic(..., MOTIONSENSE_CMDS)` to render command names. The bottom of the file sets `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` for `trace/define_trace.h`.

Control flow: normal includes declare the tracepoint; the companion `.c` file defines `CREATE_TRACE_POINTS` and includes this header to instantiate it. The core invokes the tracepoint after every EC motion host command transfer.

State and persistence: no driver state is stored. Trace records are transient tracing subsystem data.

Dependencies and integration: includes platform EC command/proto definitions and Linux tracepoint headers. It relies on `MOTIONSENSE_CMDS` being defined by the including C file before trace generation.

Risks and test signals: field extraction currently uses `param->sensor_odr` members for sensor id/data, which is most meaningful for ODR commands and may be less descriptive for other subcommands. Tests should verify trace compilation, trace output formatting for several subcommands, and no include-path breakage after source tree moves.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/cros_ec_sensors/cros_ec_sensors_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Kconfig

Purpose: Kconfig menu for shared HID Sensor IIO support. It defines the common attribute helper module and optional trigger/buffer helper module used by individual HID sensor drivers.

Important symbols: `HID_SENSOR_IIO_COMMON` depends on `HID_SENSOR_HUB` and selects `HID_SENSOR_IIO_TRIGGER` when `IIO_BUFFER` is enabled. `HID_SENSOR_IIO_TRIGGER` depends on `HID_SENSOR_HUB`, `HID_SENSOR_IIO_COMMON`, and `IIO_BUFFER`, and selects `IIO_TRIGGER` plus `IIO_TRIGGERED_BUFFER`.

Control flow: selecting common support builds `hid-sensor-iio-common`; buffer-enabled configurations also pull in trigger support. The menu is scoped as `Hid Sensor IIO Common`.

State and persistence: no runtime state. It controls buildability and dependency closure.

Dependencies and integration: ties HID sensor hub drivers to IIO common processing for shared attributes, power state, and trigger handling.

Risks and test signals: dependency loops are possible because common selects trigger while trigger depends on common; current conditions avoid this through Kconfig semantics. Test signals are valid menuconfig resolution, modules named as help text describes, and successful builds with and without `IIO_BUFFER`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Makefile

Purpose: kbuild rules for HID Sensor IIO common helper modules.

Important entries: `obj-$(CONFIG_HID_SENSOR_IIO_COMMON)` builds `hid-sensor-iio-common.o`, `obj-$(CONFIG_HID_SENSOR_IIO_TRIGGER)` builds `hid-sensor-trigger.o`, and `hid-sensor-iio-common-y` maps the composite common object to `hid-sensor-attributes.o`.

Control flow: Kconfig selections determine whether the attribute helper, trigger helper, or both are linked. The common object exports helper symbols used by concrete HID IIO drivers.

State and persistence: no runtime state. The file defines module boundaries and composite object membership.

Dependencies and integration: must match the Kconfig symbol names and the exported namespaces in the source files.

Risks and test signals: wrong composite naming would break module names expected by users and imports. Test signals are modpost export/import resolution and successful builds of HID sensor drivers that use these helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-attributes.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-attributes.c

Purpose: shared attribute and unit-conversion library for HID Sensor IIO drivers. It parses common HID feature reports, reads/writes sample frequency and hysteresis, formats IIO scale values, manages report latency metadata, and exports helpers in HID IIO namespaces.

Important APIs, types, and functions: `unit_conversion[]` maps HID usage/unit pairs to IIO scales. VTF helpers convert HID exponent/size encoded values to and from IIO integer/micro forms. Exported functions include `hid_sensor_read_poll_value()`, sample-frequency read/write helpers, raw hysteresis read/write helpers, `hid_sensor_format_scale()`, `hid_sensor_convert_timestamp()`, report-latency get/set, `hid_sensor_batch_mode_supported()`, and `hid_sensor_parse_common_attributes()`.

Control flow: concrete HID sensor probes call `hid_sensor_parse_common_attributes()` with usage id and sensitivity usage addresses. The helper discovers report interval, report state, power state, absolute/relative sensitivity, timestamp input report, and report latency fields through sensor hub attribute metadata. Runtime IIO read/write callbacks then use the exported helpers to access HID feature reports.

State and persistence: mutable common state lives in caller-owned `struct hid_sensor_common`: poll interval, hysteresis, report-latency fields, timestamp scale, and report/power attribute descriptors. HID device feature reports hold actual persistent sensor settings.

Dependencies and integration: depends on HID sensor hub APIs, IIO value conventions, units/time helpers, and exports namespaces `IIO_HID` and `IIO_HID_ATTRIBUTES`.

Risks and test signals: fixed-point conversions, exponent handling, and negative two's-complement VTF values are subtle. Tests should cover unit conversion for accel/gyro/pressure/temp/humidity/timestamp, sample frequency with millisecond and second units, unsupported units, hysteresis absolute/relative paths, report latency absence, timestamp scale defaults, and sensor_hub get/set failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-attributes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.c

Purpose: shared HID Sensor IIO trigger, buffer, FIFO-latency, and power-management helper. It allows concrete HID IIO drivers to set up kfifo buffers, expose hardware FIFO attributes when supported, maintain a trigger for userspace compatibility, and coordinate sensor power/reporting state with runtime PM.

Important APIs, types, and functions: `_hid_sensor_power_state()` opens/closes the HID sensor hub device, sets power/reporting feature values, manages `data_ready`, and waits after enabling based on poll interval. Exported `hid_sensor_power_state()` wraps runtime PM or direct power state. `hid_sensor_setup_trigger()` installs kfifo buffer ops, optional FIFO sysfs attributes, allocates/registers an IIO trigger, sets driver data, initializes delayed power-restoration work, and configures autosuspend. `hid_sensor_remove_trigger()` tears down runtime PM, work, and trigger. Buffer ops call power on/off around buffer enable. `hid_sensor_pm_ops` wires system/runtime suspend and resume.

Control flow: concrete drivers call setup after parsing common attributes. Buffer enable increments requested state and resumes the device; disable drops it. Resume schedules work to restore poll interval, hysteresis, report latency, and requested power state.

State and persistence: state is in caller-owned `struct hid_sensor_common`: trigger pointer, atomics, work item, latency, poll interval, hysteresis, and HID report descriptors. Feature settings are restored after PM transitions.

Dependencies and integration: depends on HID sensor hub, IIO kfifo buffers/triggers, runtime PM, workqueues, and imports `IIO_HID_ATTRIBUTES`.

Risks and test signals: atomic reference handling must avoid double close/open. `hid_sensor_remove_trigger()` unregisters manual trigger resources allocated outside devm. Tests should cover buffer enable/disable races, runtime PM on/off paths, autosuspend restore work, batch-mode FIFO attributes, setup failure unwind, and system suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.h

Purpose: small private header declaring the HID Sensor IIO trigger/power helper interface.

Important APIs, types, and functions: it forward-declares `struct hid_sensor_common` and `struct iio_dev`, exports `hid_sensor_pm_ops`, and declares `hid_sensor_setup_trigger()`, `hid_sensor_remove_trigger()`, and `hid_sensor_power_state()`.

Control flow: concrete HID IIO sensor drivers include this header when they need common buffer/trigger setup or PM operations. The implementation lives in `hid-sensor-trigger.c`.

State and persistence: the header owns no state; it describes operations that mutate caller-owned `struct hid_sensor_common` and IIO device state.

Dependencies and integration: includes PM headers because the exported PM ops and runtime PM behavior are part of the interface. It is internal to HID sensor IIO support, not a userspace ABI.

Risks and test signals: prototypes must stay synchronized with implementation and users. Test signals are successful builds of HID sensor drivers importing this header and modpost namespace resolution for the implementation exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/hid-sensors/hid-sensor-trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Kconfig

Purpose: Kconfig declaration for the common TDK-InvenSense timestamp helper library used by InvenSense IIO sensor drivers.

Important symbols: `IIO_INV_SENSORS_TIMESTAMP` is a hidden tristate with no prompt in this file. Device-specific drivers select it when they need the timestamp estimation helpers.

Control flow: users do not normally enable this directly. Kconfig selection by a concrete driver causes `inv_sensors_timestamp.o` to build.

State and persistence: no runtime state here; it controls helper-library availability.

Dependencies and integration: the helper is intended to be shared by InvenSense FIFO/timestamp-capable sensor drivers and is built from the local Makefile.

Risks and test signals: because the symbol is hidden, missing `select` lines in users produce unresolved references. Test signals are Kconfig coverage from all users and successful modpost for drivers importing `IIO_INV_SENSORS_TIMESTAMP` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Makefile

Purpose: kbuild rule for the TDK-InvenSense timestamp common module.

Important entries: `obj-$(CONFIG_IIO_INV_SENSORS_TIMESTAMP) += inv_sensors_timestamp.o`.

Control flow: selected Kconfig symbol directly builds one object file. There are no composite objects or subdirectories.

State and persistence: no runtime state in the Makefile.

Dependencies and integration: must match the hidden Kconfig symbol and the exported namespace in `inv_sensors_timestamp.c`.

Risks and test signals: the main risk is stale symbol naming if Kconfig or imports change. Test signals are successful build when a concrete InvenSense driver selects the helper and absence of unresolved namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/inv_sensors_timestamp.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/inv_sensors_timestamp.c

Purpose: common timestamp estimator for InvenSense sensors, especially FIFO devices where interrupt timing, sensor output data rate, chip clock jitter, and ODR changes must be reconciled into per-sample timestamps.

Important APIs, types, and functions: `inv_sensors_timestamp_init()` initializes chip parameters, jitter min/max, multiplier, period, and theoretical chip period accumulator. `inv_sensors_timestamp_update_odr()` records a pending ODR multiplier change and optionally applies it immediately when FIFO is off. `inv_sensors_timestamp_interrupt()` updates interrupt interval bounds, estimates chip period from sample count, initializes or aligns the next sample timestamp, and tolerates invalid intervals. `inv_sensors_timestamp_apply_odr()` applies pending ODR changes and recomputes timestamp alignment using FIFO period/count/sample index. Internal helpers update rolling accumulators, validate measured periods against jitter bounds, update chip period, and align timestamps toward interrupt timestamps.

Control flow: a concrete driver initializes once, calls update when ODR changes, calls interrupt on FIFO interrupts with sample count and timestamp, calls apply ODR at a known sample position, then advances `ts->timestamp` by `ts->period` while emitting samples.

State and persistence: all mutable state lives in caller-owned `struct inv_sensors_timestamp`: chip constants, min/max period, multiplier, pending multiplier, rolling chip-period accumulator, interrupt interval, current timestamp, and period. It is volatile runtime state.

Dependencies and integration: depends on math64/kernel helpers and the public IIO InvenSense timestamp header. Exports GPL namespace `IIO_INV_SENSORS_TIMESTAMP`.

Risks and test signals: period validation excludes boundary equality, so borderline jitter values are rejected. ODR changes while FIFO active return `-EAGAIN` if one is pending. Tests should cover initialization math, rolling average with empty slots, invalid interrupt intervals, first interrupt initialization, timestamp alignment drift, FIFO ODR change alignment, and zero sample count no-op.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/inv_sensors/inv_sensors_timestamp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Kconfig

Purpose: hidden Kconfig symbol for the Measurement Specialties common I2C helper library.

Important symbols: `IIO_MS_SENSORS_I2C` is a tristate without a prompt. Concrete MS/TE/HTU sensor drivers select it when they need shared reset, PROM, conversion, CRC, heater, battery, serial, humidity, temperature, or pressure helpers.

Control flow: selection enables the local Makefile to build `ms_sensors_i2c.o`.

State and persistence: no runtime state. It controls helper availability.

Dependencies and integration: meant for Measurement Specialties style I2C sensors under IIO. User drivers must include the local header and import the exported namespace.

Risks and test signals: missing select statements produce unresolved helper symbols. Test signals are Kconfig dependency closure and successful builds of all MS sensor drivers that include `ms_sensors_i2c.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Makefile

Purpose: kbuild rule for the Measurement Specialties common I2C helper object.

Important entries: `obj-$(CONFIG_IIO_MS_SENSORS_I2C) += ms_sensors_i2c.o`.

Control flow: the hidden Kconfig symbol controls direct object inclusion. There are no composite objects.

State and persistence: no runtime state.

Dependencies and integration: synchronized with `ms_sensors/Kconfig` and exported helper names in `ms_sensors_i2c.c`.

Risks and test signals: stale symbol names or missing object entry would break all dependent MS sensor drivers. Build tests should select a dependent driver and verify helper object linkage and namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.c

Purpose: shared I2C helper implementation for Measurement Specialties humidity/temperature and temperature/pressure sensors. It centralizes reset, PROM reads, ADC conversion reads, serial-number assembly, CRC checks, resolution/heater/battery sysfs helpers, humidity/temperature formulas, PROM CRC, and compensated pressure calculation.

Important APIs, types, and functions: exported helpers include `ms_sensors_reset()`, `ms_sensors_read_prom_word()`, `ms_sensors_convert_and_read()`, `ms_sensors_read_serial()`, `ms_sensors_write_resolution()`, `ms_sensors_show_battery_low()`, `ms_sensors_show_heater()`, `ms_sensors_write_heater()`, `ms_sensors_ht_read_temperature()`, `ms_sensors_ht_read_humidity()`, `ms_sensors_tp_read_prom()`, and `ms_sensors_read_temp_and_pressure()`. Internal CRC helpers validate HT/serial bytes and 112/128-bit PROM coefficient sets.

Control flow: concrete drivers pass their `ms_ht_dev` or `ms_tp_dev`. Conversion helpers send a command, sleep the resolution-specific conversion time, then read ADC bytes. HT functions lock around conversions, validate CRC, and apply datasheet formulas. TP functions read T and P ADCs, then apply first and second order compensation using PROM coefficients.

State and persistence: mutable state is in caller-owned structs: I2C client, mutex, resolution index, hardware PROM length/max resolution, and PROM coefficient cache. Resolution/heater bits are stored in sensor config registers.

Dependencies and integration: depends on I2C SMBus/master receive, IIO/sysfs conventions, delays, mutexes, and `ms_sensors_i2c.h`. Exports namespace `IIO_MEAS_SPEC_SENSORS`.

Risks and test signals: CRC algorithms and fixed-point compensation formulas are critical. Header declares `ms_sensors_show_serial()` but this file does not define it, so users must not expect it from this object. Tests should cover serial CRC/assembly, PROM CRC variants, conversion timeout/error paths, resolution bit encoding, heater validation, humidity clamp, low-temperature second-order compensation, and endian handling of ADC/PROM values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.h

Purpose: shared private header for Measurement Specialties I2C helper users. It defines common device-state structs and function prototypes exported by `ms_sensors_i2c.c`.

Important APIs, types, and functions: `struct ms_ht_dev` stores client, mutex, and resolution index for humidity/temperature devices. `struct ms_tp_hw_data` describes PROM length and maximum resolution index for temperature/pressure devices. `struct ms_tp_dev` stores client, mutex, hardware data, PROM coefficient array, and resolution index. Prototypes cover reset, PROM word reads, ADC conversion, serial read, resolution/heater/battery helpers, HT readings, PROM reading, and compensated temperature/pressure readings.

Control flow: concrete drivers initialize one of these structs, often during probe, call reset/read PROM or serial helpers, and use read helpers from IIO callbacks under the helper-managed locks.

State and persistence: the structs are caller-owned runtime state. PROM coefficients are cached in RAM after validation; sensor config bits persist in the device.

Dependencies and integration: includes I2C and mutex headers. It is internal to kernel drivers, not UAPI, and pairs with namespace exports from the C file.

Risks and test signals: the declared `ms_sensors_show_serial()` lacks a definition in the paired source file, so dependency analysis should verify no unresolved user. Tests should compile all include users, verify struct field initialization before helper calls, and ensure PROM array length matches `MS_SENSORS_TP_PROM_WORDS_NB`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ms_sensors/ms_sensors_i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Kconfig

Purpose: Kconfig menu for exposing ARM SCMI sensors as IIO devices.

Important symbols: `IIO_SCMI` is a tristate prompt depending on `ARM_SCMI_PROTOCOL` and selecting `IIO_BUFFER` and `IIO_KFIFO_BUF`. Help text states support for accelerometer and gyroscope sensors on SCMI-based platforms.

Control flow: selecting the symbol builds the SCMI IIO driver through the local Makefile.

State and persistence: no runtime state. It controls driver availability and required buffer support.

Dependencies and integration: integrates ARM SCMI protocol sensor discovery with the IIO subsystem. Kconfig indentation has spaces on some `depends/select/help` lines but remains semantically straightforward.

Risks and test signals: if buffer selections are wrong, probe would fail at kfifo setup. Test signals are Kconfig parse, module build under `ARM_SCMI_PROTOCOL`, and hidden/unavailable symbol when SCMI protocol support is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Makefile

Purpose: kbuild rule for the SCMI-to-IIO sensor bridge.

Important entries: `obj-$(CONFIG_IIO_SCMI) += scmi_iio.o`.

Control flow: selecting `IIO_SCMI` builds one driver object.

State and persistence: no runtime state.

Dependencies and integration: aligns with the SCMI Kconfig symbol and `module_scmi_driver()` implementation in `scmi_iio.c`.

Risks and test signals: stale symbol/object names would prevent SCMI IIO support from building. Test signals are successful object build and module alias generation for the SCMI device id table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/scmi_iio.c -->
# sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/scmi_iio.c

Purpose: bridge driver that exposes suitable ARM SCMI protocol sensors as IIO devices. It currently supports three-axis accelerometers and gyroscopes, with direct raw reads, sample frequency control/availability, buffered updates through SCMI notifications, scale handling, and raw-available ext-info.

Important APIs, types, and functions: `struct scmi_iio_priv` stores SCMI protocol ops/handle, sensor info, IIO device, mutex, buffer, notifier block, and frequency availability array. `scmi_iio_sensor_update_cb()` receives SCMI sensor-update events and pushes timestamped IIO buffers. Buffer ops enable/disable the SCMI sensor. `scmi_iio_set_odr_val()` converts IIO Hz/uHz to SCMI update interval fields; `scmi_iio_get_odr_val()` reverses that. `scmi_iio_read_channel_data()` temporarily enables the sensor and reads timestamped values for direct mode. Channel helpers map SCMI axis names/types to IIO modifiers/types and build data/timestamp channels. `scmi_alloc_iiodev()` allocates one IIO device per supported SCMI sensor and registers a notifier. `scmi_iio_dev_probe()` iterates discovered SCMI sensors and registers supported devices.

Control flow: probe obtains SCMI sensor protocol ops, scans all sensors, skips non-3-axis and unsupported unit types, allocates channels/frequency tables, sets up kfifo buffer, and registers IIO devices. Buffered operation enables the sensor and relies on notifier events; direct raw reads claim direct mode and perform an on-demand read.

State and persistence: per-sensor runtime state includes frequency availability, current SCMI config in firmware, and IIO buffer data. ODR and enable state are written to SCMI firmware.

Dependencies and integration: depends on SCMI protocol sensor ops, IIO kfifo buffers, notifier events, mutex, time/unit helpers, and `module_scmi_driver()`.

Risks and test signals: ODR conversion uses decimal string length to choose multiplier, which needs boundary tests. Direct read enables the sensor but if `reading_get_timestamped()` fails, the sensor disable path is skipped. Tests should cover segmented/list intervals, timestamped and non-timestamped notifications, accel/gyro type filtering, axis-name modifier parsing, scale exponents, raw_available formatting, direct-read failure cleanup, and multi-sensor probe returning at least one success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/scmi_sensors/scmi_iio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Kconfig

Purpose: Kconfig menu for Samsung Sensor Platform sensorhub support and its IIO common layer.

Important symbols: `IIO_SSP_SENSORHUB` is the SPI-backed Samsung sensorhub driver and selects `MFD_CORE`. `IIO_SSP_SENSORS_COMMONS` depends on `IIO_SSP_SENSORHUB` and selects `IIO_BUFFER` plus `IIO_KFIFO_BUF`; it builds common IIO support for SSP sensors.

Control flow: users enable the sensorhub first, then the IIO commons layer becomes available. The local Makefile maps these to `sensorhub` and `ssp_iio` objects.

State and persistence: no runtime state here. It defines build-time dependencies and menu visibility.

Dependencies and integration: ties SPI, MFD core, sensorhub transport, and IIO buffered sensor support together.

Risks and test signals: enabling commons without sensorhub would be invalid and is prevented by dependency. Test signals are Kconfig resolution, module names matching help text, and builds with SPI and MFD dependencies enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Makefile

Purpose: kbuild rules for Samsung Sensor Platform sensorhub transport and IIO common module.

Important entries: `sensorhub-objs := ssp_dev.o ssp_spi.o` builds the sensorhub composite module. `obj-$(CONFIG_IIO_SSP_SENSORHUB) += sensorhub.o` gates transport support. `obj-$(CONFIG_IIO_SSP_SENSORS_COMMONS) += ssp_iio.o` gates IIO commons.

Control flow: selecting the sensorhub builds the SPI/device core pieces; selecting commons builds the IIO adapter object that depends on the sensorhub interfaces.

State and persistence: no runtime state in the Makefile.

Dependencies and integration: must remain synchronized with Kconfig and declarations in `ssp.h` plus other SSP source files not in this work item.

Risks and test signals: composite object membership determines module linkage; removing `ssp_spi.o` or `ssp_dev.o` would break sensorhub operation. Test signals are successful build for each symbol and modpost resolution between `ssp_iio` and `sensorhub` symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp.h -->
# sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp.h

Purpose: internal header for Samsung Sensor Platform sensorhub core and IIO integration. It defines protocol constants, firmware/download states, message instruction ids, board-info structure, main `struct ssp_data`, and function prototypes shared by SSP transport and IIO code.

Important APIs, types, and functions: constants define device id, reset time, default polling delay, packet/header sizes, AP-to-SSP instruction ids, AP status commands, factory-test commands, ACK/NAK values, and message option bits. `struct ssp_sensorhub_info` describes firmware names/revision and magnetic calibration table. `struct ssp_data` is the central runtime object: SPI device, board info, watchdog timer/work, refresh work, shutdown/debug/time-sync flags, status counters, available/enabled sensors, firmware revision, AP resume state, delay/batch buffers, positions, firmware-download state, locks, GPIOs, pending list, IIO device table, enable refcount, and DMA-aligned header buffer. Prototypes cover pending-list cleanup, commands, instruction send, IRQ message processing, chip id, magnetic matrix, sensor scanning info, firmware revision, and refresh task queueing.

Control flow: SPI/device code owns `struct ssp_data`, handles low-level messages and watchdog/reset, while IIO sensor code uses the shared state to enable sensors, adjust delays, and receive samples. Instructions encode add/remove/change-delay/library/AP-status operations to the MCU.

State and persistence: this header describes extensive volatile runtime state plus cached firmware revision and calibration/matrix data. Firmware files and MCU state persist outside the driver.

Dependencies and integration: includes GPIO consumer, IIO SSP sensor definitions, IIO core, SPI, and delay helpers. It supports objects built from `ssp_dev.c`, `ssp_spi.c`, and `ssp_iio.c`.

Risks and test signals: protocol constants must match MCU firmware. `sensor_enable`, refcounts, pending list, and GPIO reset sequencing are high-risk concurrency areas. Tests should cover command ACK/NAK handling, pending-list cleanup on reset, watchdog refresh, firmware revision/scanning queries, GPIO availability, DMA alignment of header buffer, and sensor enable/delay bookkeeping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/common/ssp_sensors/ssp.h -->
