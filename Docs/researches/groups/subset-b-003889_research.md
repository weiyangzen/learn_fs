# subset-b-003889 research

Grouped research for Linux IIO IMU drivers under `sources/distributed-fs/ceph-client/drivers/iio/imu`. Each section preserves the source path in its title and is bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_core.c

Purpose: shared IIO core for the Bosch BMI323 six-axis IMU. It exports `bmi323_core_probe()` and `bmi323_core_pm_ops` for bus wrappers, creates accelerometer, gyroscope, temperature, step counter, event, trigger, and FIFO-buffer interfaces, and hides register programming behind regmap.

Important APIs, types, and functions: `struct bmi323_data` is the persistent driver state: device/regmap, mount matrix, selected interrupt pin, trigger, state enum, FIFO timestamps, ODR caches, enabled feature-event bits, runtime-PM register snapshots, mutex, FIFO buffer, scan buffer, and step counter buffer. `bmi323_hw[]` maps accel/gyro to data and config registers plus scale tables. IIO channel macros build six 16-bit LE accel/gyro scan channels, a temperature channel, and an `IIO_STEPS` channel with a change event. The IIO ops are in `bmi323_info`: raw reads/writes, available values, FIFO watermark, and event config/value callbacks.

Control flow: probe obtains the parent regmap, enables `vdd`/`vddio`, initializes private state, soft-resets and validates the chip ID, enables the feature engine, applies default bandwidth and 25 Hz accel/gyro ODR, reads the mount matrix, registers an optional IRQ-backed trigger, sets up a triggered buffer with hardware FIFO attributes, registers the IIO device, then leaves FIFO disabled. Direct raw accel/gyro reads claim direct mode, check the error register, and read a single axis. Triggered-buffer reads bulk-read all six channels when possible or read selected axes one by one. FIFO mode requires matching accel/gyro ODRs, enables FIFO and watermark interrupt in postenabling, flushes frames in the IRQ thread, reconstructs timestamps from previous/current FIFO interrupt times, and pushes selected channels.

State and persistence behavior: the mutex protects private state and all extended-register access, which is critical because the BMI323 extended-register protocol cannot be interleaved with unrelated register traffic. `feature_events` mirrors enabled feature-engine bits for step, motion, no-motion, and tap events. `odrhz`/`odrns` mirror configured sample periods for validation and FIFO timestamps. Runtime suspend snapshots selected normal and extended registers, suspends triggering, soft-resets the chip to low power, and runtime resume reinitializes the device, restores extended then normal registers, flushes FIFO if active, checks errors, and resumes triggering.

Dependencies and integration points: depends on IIO core, IIO events, triggered buffers, triggers, regmap, regulators, firmware node IRQ properties, ACPI/DT mount matrix, and Bosch BMI323 register definitions from `bmi323.h`. Bus files provide the regmap and import the `IIO_BMI323` namespace. IRQ setup uses named `INT1`/`INT2`, trigger type, and `drive-open-drain`.

Risks and edge cases: extended-register helpers only check TX ready once and can return `-EBUSY`; callers must handle transient failures. Tap and step features require accel ODR >= 200 Hz; sysfs/event writes fail otherwise. FIFO timestamps are approximate and rely on interrupt timing and equal accel/gyro ODR. `bmi323_set_odr()` configures power mode before writing ODR and maps unsupported pairs to `-EINVAL`. IRQ handler returns `IRQ_NONE` on register or status errors, so lost events are possible under bus faults. Runtime resume restoration order and clearing `FEAT_IO0` are sensitive because active feature config must be cleared before modification.

Test signals: useful checks include successful probe/chip-id validation over both buses, raw accel/gyro/temp reads, scale/ODR/oversampling writes and available lists, event enable/value round trips for motion/tap/step watermark, rejection of tap/step at low ODR, triggered buffer scans with partial/all channel masks, FIFO watermark operation with equal ODR and rejection with mismatched ODR, IRQ event delivery for motion/tap/step/FIFO/DRDY, and runtime suspend/resume preserving event/FIFO configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_i2c.c

Purpose: I2C transport wrapper for BMI323. It implements BMI323-specific I2C regmap bus callbacks and delegates all sensor behavior to `bmi323_core_probe()`.

Important APIs, types, and functions: `struct bmi323_i2c_priv` holds the `i2c_client` and a receive buffer large enough for FIFO data plus two dummy bytes. `bmi323_regmap_i2c_read()` issues a two-message I2C transfer, then strips the BMI323-required two dummy bytes. `bmi323_regmap_i2c_write()` writes register-plus-payload through SMBus block write. `bmi323_i2c_regmap_config` is 8-bit register, 16-bit little-endian value, max `BMI323_CFG_RES_REG`.

Control flow: probe allocates transport private data, initializes a devm regmap with the custom bus, and calls the common core probe. Device matching is provided through ACPI `BOSC0200`, I2C ID `bmi323`, and OF compatible `bosch,bmi323`.

State and persistence behavior: no sensor state is kept here beyond the transport buffer and client pointer; runtime PM is delegated by referencing `bmi323_core_pm_ops` in the i2c driver.

Dependencies and integration points: depends on Linux I2C, regmap, module tables, and the exported BMI323 core namespace. The ACPI comment documents an identifier conflict with BMC150 and relies on the core chip-ID check/reset to reject non-BMI323 devices safely.

Risks and edge cases: `i2c_transfer()` success is not checked for a short positive transfer count, only negative errors; a partial positive transfer would still copy from the RX buffer. SMBus block write must support BMI323 payload sizes. Shared ACPI ID can cause attempted probes on other Bosch devices.

Test signals: verify I2C reads strip dummy bytes correctly, writes reach 16-bit little-endian registers, probe fails cleanly on non-BMI323 `BOSC0200`, and runtime suspend/resume callbacks from the core operate through the I2C regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_spi.c

Purpose: SPI transport wrapper for BMI323. It supplies a SPI regmap configuration and delegates the common IIO implementation to `bmi323_core_probe()`.

Important APIs, types, and functions: `bmi323_regmap_spi_read()` uses `spi_write_then_read()` with regmap-provided padding/read flag handling. `bmi323_regmap_spi_write()` mutates the regmap buffer by copying the register byte into the second byte, then sends from `data_buff + 1`; this accounts for the regmap pad byte used by the BMI323 SPI format. `bmi323_spi_regmap_config` uses 8-bit registers, 16-bit little-endian values, 8 pad bits, read flag bit 7, and max `BMI323_CFG_RES_REG`.

Control flow: SPI probe initializes the custom regmap on the SPI device, calls common probe, and device matching uses SPI ID `bmi323` plus OF compatible `bosch,bmi323`.

State and persistence behavior: no independent runtime state is kept in this file; runtime PM is inherited from `bmi323_core_pm_ops`.

Dependencies and integration points: depends on Linux SPI, regmap, module device tables, and the core BMI323 namespace. The SPI regmap contract must match the core's 16-bit register accesses and FIFO no-increment reads.

Risks and edge cases: the write callback edits the regmap-provided data buffer in place; this depends on regmap passing a mutable buffer with the expected pad byte layout. Any change in regmap formatting or BMI323 SPI command layout would break writes. Reads rely on `pad_bits` to handle the device dummy byte.

Test signals: probe over SPI, raw/config register reads and writes, FIFO burst reads, and runtime suspend/resume should be compared against I2C behavior. A focused SPI write test should confirm the address/payload bytes on the bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Kconfig

Purpose: Kconfig entries for Bosch BNO055 common, UART/serdev, and I2C drivers.

Important APIs, types, and functions: `BOSCH_BNO055` is a hidden tristate selected by bus drivers and selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`. `BOSCH_BNO055_SERIAL` depends on `SERIAL_DEV_BUS`, selects `REGMAP` and the common driver, and builds module `bno055_sl`. `BOSCH_BNO055_I2C` depends on `I2C`, selects `REGMAP_I2C` and the common driver, and builds `bno055_i2c`.

Control flow: users choose a bus-specific option; the selected common symbol ensures the shared IIO implementation is linked.

State and persistence behavior: no runtime state; this file controls build inclusion and dependency closure.

Dependencies and integration points: integrates the BNO055 folder with IIO buffering, triggered buffering, serdev, I2C, and regmap subsystems.

Risks and edge cases: serial selects only generic `REGMAP`, not `REGMAP_I2C`, because it implements a custom regmap bus. The help text names the serial module `bno055_sl`, while the Makefile builds object `bno055_ser.o`; packaging expectations should match generated module naming.

Test signals: Kconfig build matrix should cover common+I2C, common+serial with tracing on/off, module and built-in configurations, and dependency failures when I2C or serdev are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Makefile -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Makefile

Purpose: build rules for BNO055 common, serial, serial trace, and I2C objects.

Important APIs, types, and functions: `obj-$(CONFIG_BOSCH_BNO055) += bno055.o` builds the shared core. `obj-$(CONFIG_BOSCH_BNO055_SERIAL) += bno055_ser.o` composes `bno055_ser-y := bno055_ser_core.o` and adds `bno055_ser_trace.o` when `CONFIG_TRACING` is enabled. `CFLAGS_bno055_ser_trace.o := -I$(src)` lets `define_trace.h` locate the local trace header. `obj-$(CONFIG_BOSCH_BNO055_I2C) += bno055_i2c.o` builds the I2C wrapper.

Control flow: object inclusion follows Kconfig symbols; tracepoint compilation is conditional on tracing.

State and persistence behavior: no runtime state; affects module composition.

Dependencies and integration points: integrates Linux tracepoint build requirements with the serdev transport and ensures common core is linked separately from bus wrappers.

Risks and edge cases: missing the `-I$(src)` flag would break tracepoint generation because `TRACE_INCLUDE_PATH` is local. The serial module's trace object is optional, so code must compile both with and without `CONFIG_TRACING`.

Test signals: compile serial with `CONFIG_TRACING=y` and `n`, compile I2C-only, and verify module object names and symbol namespace imports resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.c

Purpose: shared IIO driver for Bosch BNO055 IMU/fusion sensor. It exports `bno055_regmap_config` and `bno055_probe()` for I2C and serial transports, exposes raw physical sensors, fused orientation/quaternion/linear acceleration/gravity, temperature, calibration data, fusion controls, debugfs firmware version, and triggered buffers.

Important APIs, types, and functions: `struct bno055_priv` stores regmap, clock, operation mode, burst-transfer threshold, mutex, UID, optional reset GPIO, software-reset policy, scan buffer, and debugfs dentry. `struct bno055_sysfs_attr` abstracts value tables, fusion-mode fixed values, hardware translations, and IIO return type. The common regmap uses page-window ranges through `BNO055_PAGESEL_REG`, MAPLE cache, readable/writeable/volatile callbacks, and virtual page-1 addresses via `BNO055_PG1()`. `bno055_probe()` performs chip/reset/init/register of IIO. `bno055_operation_mode_set()` centralizes transitions through config mode and resets algorithm state before entering fusion. `bno055_scan_xfer()` and `bno055_trigger_handler()` implement optimized buffered reads.

Control flow: probe allocates an IIO device, configures optional reset GPIO and clock, resets or warns if no reset path is available, reads chip ID/revision/UID, requests UID-specific calibration firmware then generic calibration firmware, initializes power/unit/calibration, enters fusion mode, registers cleanup to return to config mode, sets IIO channels/info, installs triggered buffer, registers the device, and creates debugfs. Raw reads lock the device, reject fusion-only channels when in AMG mode, and dispatch simple, quaternion, or temperature reads. Writes for LPF/range/ODR switch to config mode, write register fields, then return to AMG mode when applicable. Fusion sysfs controls switch among AMG, fusion without fast magnetometer calibration, and fusion with fast magnetometer calibration.

State and persistence behavior: `operation_mode` is the central state variable and affects channel readability, available values, writable configuration, offsets, and calibration status. Calibration data is volatile and is read as a single binary blob only after temporarily entering config mode. The driver caches UID in memory and uses firmware files named from UID or generic name. The regmap cache tracks paged registers but marks data/status/config-in-fusion/calibration as volatile.

Dependencies and integration points: depends on IIO core, triggered buffer, regmap, firmware loader, GPIO reset, optional external clock, debugfs, and bus wrappers supplying the regmap and `xfer_burst_break_thr`. Documentation is referenced for calibration file installation. The bus-specific threshold influences how many gaps the trigger handler bridges in one burst read.

Risks and edge cases: no reset GPIO and no software reset can leave unreliable state. Serial transport disables software reset because reset writes may not respond. Fusion mode auto-manages some hardware config, so setters become no-ops and available lists collapse to fixed values. Quaternion consumes four 16-bit words but one scan bit, so buffer transfer offset logic is subtle. Calibration blob reads require full length and position zero to avoid inconsistent partial data. The firmware-scale workaround for gyroscope depends on known firmware version 0x03/0x11 and warns otherwise.

Test signals: probe over I2C and serial, reset-path variants, UID-specific and generic calibration firmware loading, fusion enable/disable and fast calibration controls while buffers are active/inactive, raw reads for physical and fused channels in each mode, quaternion multi-value reads, calibration-status sysfs, calibration_data binary read requirements, debugfs firmware_version, trigger buffer scans with sparse masks and quaternion inclusion, and regmap page access through debugfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.h -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.h

Purpose: small shared header for BNO055 bus wrappers.

Important APIs, types, and functions: declares `bno055_probe(struct device *dev, struct regmap *regmap, int xfer_burst_break_thr, bool sw_reset)` and exports `bno055_regmap_config`. It forward-declares `struct device` and includes regmap/types.

Control flow: bus drivers include this header, create a regmap appropriate for the bus, and call the common probe with transport-specific burst threshold and software-reset capability.

State and persistence behavior: no state; it defines the boundary between transport files and common IIO code.

Dependencies and integration points: integrates I2C and serdev wrappers with `bno055.c` and the `IIO_BNO055` namespace.

Risks and edge cases: the `sw_reset` argument is part of a transport safety contract; passing true for serial would be unsafe because reset commands may not acknowledge.

Test signals: build checks for both bus wrappers and namespace imports; probe behavior should reflect the passed burst threshold and reset flag.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_i2c.c

Purpose: I2C bus wrapper for BNO055.

Important APIs, types, and functions: `bno055_i2c_probe()` initializes an I2C regmap using the common `bno055_regmap_config`, then calls `bno055_probe()` with `BNO055_I2C_XFER_BURST_BREAK_THRESHOLD` set to 3 and `sw_reset=true`. Match tables include I2C ID `bno055` and OF compatible `bosch,bno055`.

Control flow: I2C core matches a client, the wrapper creates regmap, then common probe handles all reset, calibration, IIO, buffer, and debugfs setup.

State and persistence behavior: no independent state; all persistent state is in `struct bno055_priv`.

Dependencies and integration points: depends on I2C and `REGMAP_I2C`, imports the common `IIO_BNO055` namespace, and advertises the I2C interface module.

Risks and edge cases: I2C burst threshold is low, so buffered sparse masks may split transfers more often than serial. Software reset is enabled for I2C, so reset command failure affects probe and fusion-mode transitions.

Test signals: successful I2C regmap setup, probe with hardware reset absent using software reset, OF/I2C matching, and buffered scan performance/correctness with gaps above and below threshold 3.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_core.c

Purpose: serdev/UART transport for BNO055, implementing the chip's serial register protocol as a custom regmap bus and delegating IIO behavior to the common BNO055 core.

Important APIs, types, and functions: `struct bno055_ser_priv` stores the expected command response, expected data length, response buffer, command status, mutex-protected command state, RX finite-state machine, stale-command marker, completion, and serdev pointer. `bno055_ser_send_cmd()` serializes read/write commands, handles stale interrupted commands, retries non-critical hardware failures up to five times, and waits for completion. `bno055_ser_receive_buf()` parses `0xEE` status packets and `0xBB` data packets, copies payload into the waiting regmap buffer, and reports status to `bno055_ser_handle_rx()`. Regmap callbacks are `bno055_ser_write_reg()` and `bno055_ser_read_reg()`.

Control flow: probe allocates transport state, binds serdev callbacks, opens the serial device, enforces 115200 baud, no parity, no flow control, initializes custom regmap, then calls `bno055_probe()` with serial burst threshold 22 and `sw_reset=false`. Command send splits bytes into two-byte chunks with 2-3 ms gaps to avoid BNO055 RX buffer overrun. Reads set the response buffer under lock before sending; RX completion wakes the waiting regmap call.

State and persistence behavior: the RX FSM tracks packet type, expected length, and bytes received across callbacks. `expect_response`, `response_buf`, and `cmd_status` are shared between the regmap thread and RX callback under `lock`. `cmd_stale` handles interrupted waits by waiting for prior command completion before issuing the next one. There is no persistent sensor state beyond transport synchronization; the common driver owns sensor mode/calibration.

Dependencies and integration points: depends on serdev, completions, mutexes, regmap custom buses, optional tracepoints from `bno055_ser_trace.h`, and the common `bno055_probe()`. Device matching uses OF compatible `bosch,bno055`.

Risks and edge cases: the serial protocol is fragile and timing-dependent; exceeding the chip's inter-byte tolerance or buffer capacity causes failures. Software reset is disabled because a successful reset may produce no response. RX malformed packets set critical status and can force `-EIO`. Interrupted reads leave stale state that must drain. `val_size` over 128 is rejected. The RX copy intentionally avoids writing when `response_buf` is NULL or would exceed expected length.

Test signals: serial probe with exact baud/parity, read/write register transactions, retry tracepoints under induced `STATUS_FAIL`, timeout behavior, interrupted command handling, malformed packet handling, stale response safety, common BNO055 probe over serial with reset GPIO present, and buffered scan bursts using threshold 22.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.c

Purpose: tracepoint instantiation unit for the BNO055 serial transport.

Important APIs, types, and functions: defines `CREATE_TRACE_POINTS` and includes `bno055_ser_trace.h`, causing the trace events declared in the header to be emitted exactly once when `CONFIG_TRACING` includes this object.

Control flow: no runtime logic beyond tracepoint registration generated by the tracing infrastructure.

State and persistence behavior: no driver state; tracepoint definitions are static instrumentation.

Dependencies and integration points: depends on the local trace header and the Makefile `-I$(src)` flag. It is conditionally linked into `bno055_ser` when tracing is enabled.

Risks and edge cases: if included in multiple translation units with `CREATE_TRACE_POINTS`, duplicate definitions would occur; this file prevents that by being the single instantiation.

Test signals: build with tracing enabled and verify `/sys/kernel/tracing/events/bno055_ser/*` events exist; build without tracing and ensure serial driver still compiles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.h -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.h

Purpose: trace event declarations for BNO055 serial communication.

Important APIs, types, and functions: declares `TRACE_SYSTEM bno055_ser` and events `send_chunk`, `cmd_retry`, `write_reg`, `read_reg`, and `recv`. Events capture byte chunks, read/write addresses, retry count, and received buffers using dynamic arrays and formatted hex output. It sets `TRACE_INCLUDE_PATH .` and `TRACE_INCLUDE_FILE bno055_ser_trace`, then includes `trace/define_trace.h` outside the include guard.

Control flow: serial core calls `trace_send_chunk()`, `trace_cmd_retry()`, `trace_write_reg()`, `trace_read_reg()`, and `trace_recv()` around protocol activity; when tracing is disabled these compile to low overhead stubs.

State and persistence behavior: no persistent state, but traced payloads can expose raw command/data bytes useful for postmortem protocol debugging.

Dependencies and integration points: integrates Linux tracepoint macros with the serial transport and requires the companion `.c` file for instantiation.

Risks and edge cases: dynamic trace arrays copy arbitrary transfer data, so high-frequency tracing can add overhead and expose calibration/sensor register bytes in trace logs. Header path configuration is fragile without the Makefile CFLAGS.

Test signals: enable each trace event during serial reads/writes and verify chunk lengths, retry numbers, and RX bytes match observed regmap operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bno055/bno055_ser_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700.h -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700.h

Purpose: shared declarations for FXOS8700 I2C/SPI wrappers and core.

Important APIs, types, and functions: exports `fxos8700_regmap_config` and declares `fxos8700_core_probe(struct device *dev, struct regmap *regmap, const char *name, bool use_spi)`.

Control flow: bus wrappers create a regmap, choose a device name and `use_spi` flag, and call the common core probe.

State and persistence behavior: no state; boundary header only.

Dependencies and integration points: integrates bus-specific files with the common FXOS8700 IIO driver.

Risks and edge cases: the `use_spi` parameter is currently not materially used in the core, so future SPI-specific behavior would need to respect this interface.

Test signals: compile both bus wrappers and confirm exported symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_core.c

Purpose: common IIO core for NXP FXOS8700 accelerometer plus magnetometer. It supports direct raw reads and sysfs scale/sample-frequency configuration over I2C or SPI; buffer, trigger, and IRQ support are explicitly TODO.

Important APIs, types, and functions: `struct fxos8700_data` holds regmap, unused trigger pointer, and a DMA-aligned three-axis BE16 buffer. `fxos8700_regmap_config` defines readable/writable register ranges and max NVM register. Channel definitions expose three accel and three magnetometer axes plus soft timestamp, but the device is direct-mode only. Helpers include `fxos8700_set_active_mode()`, `fxos8700_set_scale()`, `fxos8700_get_scale()`, `fxos8700_get_data()`, `fxos8700_set_odr()`, `fxos8700_get_odr()`, and `fxos8700_chip_init()`.

Control flow: core probe allocates an IIO device, saves regmap, validates WHO_AM_I against production/pre-production IDs, briefly activates sensors, puts the chip in standby, configures hybrid accel+mag mode with max oversampling, disables min/max threshold features, sets accel full scale to +/-8G, activates max ODR, registers cleanup to disable sensors, fills IIO metadata, and registers the direct-mode IIO device. Raw reads bulk-read all three axes from the relevant accel or mag output base to avoid data loss, then return the requested axis. Scale and ODR writes put the device in standby when needed, update config fields, and reactivate.

State and persistence behavior: the core does not maintain cached scale/ODR; it reads registers when asked. Active/standby state lives in `CTRL_REG1`, and cleanup disables both sensor modes. Magnetometer scale is fixed at 0.001 Gs; accelerometer scale is stored in `XYZ_DATA_CFG`. ODR is shared by accel and magnetometer in hybrid mode, and the comment notes effective ODR is halved when both sensors are active.

Dependencies and integration points: depends on IIO core/sysfs, regmap, bitfield helpers, and bus wrappers. The register access table constrains regmap operations to known FXOS8700 ranges.

Risks and edge cases: no mutex protects the shared `data->buf`, so concurrent raw reads from multiple sysfs paths could race; IIO direct read paths often serialize enough in practice but this is a consideration. `fxos8700_set_scale()` returns `-EINVAL` for invalid scale after it may have already put the chip in standby and does not restore active mode on that path. `sign_extend32(tmp, 15)` after shifting 14-bit accel samples may sign-extend from bit 15 rather than the 13-bit sample sign; behavior depends on arithmetic shift preserving sign. `use_spi` is unused. No buffer/trigger/IRQ path despite timestamp channel.

Test signals: probe ID validation, direct accel/mag raw reads, accel scale available/write/readback including invalid writes, magnetometer scale write rejection, ODR available/write/readback, cleanup disabling active mode, and concurrency testing for simultaneous raw reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_i2c.c

Purpose: I2C wrapper for NXP FXOS8700.

Important APIs, types, and functions: `fxos8700_i2c_probe()` initializes an I2C regmap with `fxos8700_regmap_config`, optionally takes the I2C ID name, and calls `fxos8700_core_probe()` with `use_spi=false`. Match tables include I2C ID `fxos8700`, ACPI `FXOS8700`, and OF compatible `nxp,fxos8700`.

Control flow: device match triggers regmap setup, then common core validation/configuration/registration.

State and persistence behavior: no independent state; all runtime behavior is in the core.

Dependencies and integration points: depends on I2C, regmap_i2c, ACPI/OF match tables, and common FXOS8700 exported symbols.

Risks and edge cases: if there is no I2C ID, the core falls back to default name `fxos8700`. Probe errors log with `dev_err` rather than `dev_err_probe`, so deferred-probe messaging may be less polished.

Test signals: I2C probe via OF, ACPI, and ID table; regmap read/write behavior; name assignment; and clean failure on regmap initialization errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_spi.c

Purpose: SPI wrapper for NXP FXOS8700.

Important APIs, types, and functions: `fxos8700_spi_probe()` initializes a SPI regmap with the common `fxos8700_regmap_config`, reads the SPI ID name, and calls `fxos8700_core_probe()` with `use_spi=true`. Match tables include SPI ID `fxos8700`, ACPI `FXOS8700`, and OF compatible `nxp,fxos8700`.

Control flow: SPI core matches the device, regmap is created, then the common core handles chip init and IIO registration.

State and persistence behavior: no independent state in the wrapper.

Dependencies and integration points: depends on SPI, regmap_spi, ACPI/OF matching, and common FXOS8700 core exports.

Risks and edge cases: the core currently ignores `use_spi`, so any FXOS8700 SPI-specific addressing/transfer quirks must be fully handled by generic regmap SPI or added later. Probe logs regmap failures with `dev_err`.

Test signals: SPI probe via ID/OF/ACPI, register access through regmap SPI, and parity with I2C for raw reads and config writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/fxos8700_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Kconfig

Purpose: Kconfig entries for the InvenSense ICM-426xx common core and I2C/SPI bus drivers.

Important APIs, types, and functions: hidden `INV_ICM42600` selects `IIO_BUFFER` and `IIO_INV_SENSORS_TIMESTAMP`. `INV_ICM42600_I2C` depends on I2C, selects common core and `REGMAP_I2C`, and builds `inv-icm42600-i2c`. `INV_ICM42600_SPI` depends on `SPI_MASTER`, selects common core and `REGMAP_SPI`, and builds `inv-icm42600-spi`.

Control flow: bus-specific selections pull in the shared multi-object ICM42600 driver and required timestamp/buffer infrastructure.

State and persistence behavior: no runtime state; controls build dependencies.

Dependencies and integration points: integrates the driver with IIO buffering and the shared InvenSense timestamp helper.

Risks and edge cases: because the common symbol is hidden, it is only built when a bus transport is selected. Missing timestamp helper support would break the common buffer path.

Test signals: build I2C-only, SPI-only, both, modules, built-ins, and dependency-disabled configs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Makefile -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Makefile

Purpose: object composition rules for ICM-426xx common and bus-specific modules.

Important APIs, types, and functions: `inv-icm42600.o` includes core, gyro, accel, temp, and buffer objects. I2C and SPI modules are separate wrapper modules built from `inv_icm42600_i2c.o` and `inv_icm42600_spi.o`.

Control flow: Kconfig symbols determine which composite objects are linked. The requested subset includes common header/core/accel/buffer, while the Makefile shows additional gyro/temp/bus files complete the full driver.

State and persistence behavior: no runtime state; build composition only.

Dependencies and integration points: ensures accel and buffer code can call gyro/temp symbols in the same common module and bus wrappers can import the common namespace.

Risks and edge cases: omitting gyro or temp objects would leave unresolved symbols used by buffer and accel. Module names use hyphenated object names while source files use underscores.

Test signals: full module link with all common objects, I2C/SPI wrapper link, and modpost namespace import checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600.h -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600.h

Purpose: central shared header for the InvenSense ICM-426xx driver family. It defines chip variants, register addresses/fields, configuration/state structures, timing constants, and cross-object APIs.

Important APIs, types, and functions: enums cover chips, bus slew rates, sensor modes, gyro/accel full-scale values including ICM42686-specific ranges, ODRs, and filters. `struct inv_icm42600_conf` stores current gyro/accel/temp config; `struct inv_icm42600_state` is the shared device state containing lock, chip/name/regmap, vddio regulator, IRQ, orientation, active config, suspended config, gyro/accel IIO devices, interrupt timestamps, APEX/WoM state, FIFO state, and DMA-aligned scratch buffer. `struct inv_icm42600_sensor_state` is per-IIO-device state for scale table, desired power mode/filter, and timestamp helper. The header declares regmap configs, PM ops, probe/init functions, sensor configuration setters, FIFO parser hooks, debugfs access, and WoM event helpers.

Control flow: bus wrappers call `inv_icm42600_core_probe()` with a chip ID and bus setup callback. Core initializes `struct inv_icm42600_state`, then gyro/accel/temp/buffer objects interact through the declared functions and shared state. FIFO decode/parse APIs bridge the common buffer code to the per-sensor parsers.

State and persistence behavior: the header documents the split between chip-global state and per-sensor IIO state. Runtime/system suspend stores prior sensor modes in `struct inv_icm42600_suspended`. APEX/WoM state persists threshold and enable flags. FIFO state persists enable bits, sample period, requested/effective watermarks, counters, and the 2080-byte FIFO buffer.

Dependencies and integration points: depends on regmap, mutex, regulators, IIO core, mount matrices, common InvenSense timestamp helper, and `inv_icm42600_buffer.h`. Register definitions span virtual banked addresses, FIFO configuration, interrupt routing, timestamp, interface, power, APEX/WoM, and calibration offset registers.

Risks and edge cases: many register fields are banked virtual addresses, so regmap range setup must match these constants. ODR enum values are not dense from zero and include reserved entries, so array indexing must respect `INV_ICM42600_ODR_NB`. Shared `st->buffer` is small and protected by `st->lock`; callers must hold the lock when using it across register operations.

Test signals: compile all common objects against the header, verify all chip IDs map to valid WHOAMI/default configs, exercise ODR-to-period mapping for every exposed ODR, and validate suspend/FIFO/APEX state interactions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_accel.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_accel.c

Purpose: accelerometer IIO device implementation for ICM-426xx. It exposes accel axes, temperature in the accel scan, scale, sample frequency, calibration bias, power-mode enum, hardware FIFO controls, and wake-on-motion events.

Important APIs, types, and functions: channel macros define three 16-bit BE accel channels, temp, timestamp, and an event-only ROC rising channel for WoM. `struct inv_icm42600_accel_buffer` is the userspace buffer layout: accel xyz, converted temp, timestamp. `inv_icm42600_accel_update_scan_mode()` turns on temp/accel and FIFO bits for active scans. `inv_icm42600_accel_read_sensor()` handles direct raw reads under runtime PM. Scale/ODR/calibration helpers convert between IIO ABI values and register encodings. WoM helpers convert ROC thresholds to the chip's 8-bit threshold, enable/disable APEX WoM, and push IIO events. `inv_icm42600_accel_init()` allocates/registers the accel IIO device. `inv_icm42600_accel_parse_fifo()` pushes decoded FIFO accel samples.

Control flow: initialization selects the scale table based on chip variant, defaults accel requested power mode to low-power/16x averaging, initializes timestamp helper with 32 kHz clock assumptions, sets IIO metadata, attaches kfifo buffer ops, registers the IIO device, and marks accel events wakeup-capable. Direct raw reads resume the parent device, enable accel if needed, read the selected axis register, reject invalid sentinel data, and autosuspend. Buffer enabling goes through common buffer ops; scan-mode setup enables temp and/or accel FIFO sources and waits for startup. FIFO parse loops through decoded packets, skips missing/invalid accel data, applies ODR updates to timestamp state, converts 8-bit FIFO temp to high-resolution format, and pushes buffer samples.

State and persistence behavior: per-accel state stores desired power mode/filter while the sensor is off; when on, actual mode is in `st->conf.accel`. ODR writes update timestamp period, reprogram accel config, recompute WoM threshold because ROC depends on sample frequency, and update FIFO period/watermark. Calibration bias is persisted in chip offset registers using packed 12-bit signed axis encodings. WoM enable increments `st->apex.on`, keeps accel powered, and pairs runtime PM get/put with event enable/disable.

Dependencies and integration points: depends on the core state/config functions, common buffer helpers, temp channel helpers from `inv_icm42600_temp.h`, IIO event/buffer/kfifo APIs, runtime PM, regmap, and `IIO_INV_SENSORS_TIMESTAMP`.

Risks and edge cases: power mode cannot be changed while accel is on and is constrained by ODR; unsupported combinations return `-EPERM`. `pm_runtime_get_sync()` return values are not always checked in direct read/write paths. ODR writes update WoM threshold even if WoM is disabled, so threshold register writes can fail during ordinary ODR changes. Offset register packing shares nibbles across axes and must preserve unrelated bits. WoM disable decrements `st->apex.on`; event state mismatches could underflow logically. FIFO temp is zeroed if missing, which may be ambiguous to users.

Test signals: raw accel/temp reads, scale lists and writes for normal and ICM42686 ranges, ODR lists and timestamp-period updates, calibration bias read/write per axis including bounds, power_mode enum validation, buffer enable/disable with accel+temp scan, FIFO parse with valid/invalid accel packets and ODR-change flags, hwfifo watermark/flush, WoM threshold conversion/readback, event enable/disable/wakeup, and runtime autosuspend behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_accel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.c

Purpose: shared FIFO and IIO buffer management for ICM-426xx gyro and accel IIO devices.

Important APIs, types, and functions: FIFO packet structs model one-sensor 8-byte and two-sensor 16-byte packets. `inv_icm42600_fifo_decode_packet()` decodes header flags into accel/gyro/temp/timestamp pointers and ODR-change bits. `inv_icm42600_buffer_set_fifo_en()` programs FIFO source bits. `inv_icm42600_buffer_update_watermark()` computes byte thresholds from gyro/accel requested watermarks and ODR-derived latency. `inv_icm42600_buffer_ops` wires preenable/postenable/predisable/postdisable into IIO kfifo setup. `inv_icm42600_buffer_fifo_read()`, `inv_icm42600_buffer_fifo_parse()`, and `inv_icm42600_buffer_hwfifo_flush()` read and push FIFO contents. `inv_icm42600_buffer_init()` configures FIFO count/endian/partial-read defaults.

Control flow: preenable resumes runtime PM and resets the selected sensor timestamp. Per-sensor `update_scan_mode` enables sensor FIFO bits. First postenabling enables FIFO threshold interrupt, flushes FIFO, enters stream mode, performs a dummy FIFO count read for a hardware workaround, and increments `fifo.on`; additional sensors only increment the reference count. Predisable decrements or, for the last user, bypasses FIFO, flushes it, and disables threshold interrupts. Postdisable clears FIFO bits and watermark for that sensor, may power off gyro/accel/temp, updates timestamp state, waits for stop/start delays, and autosuspends.

State and persistence behavior: `st->fifo.on` is a reference count shared by gyro and accel buffers. `st->fifo.en` mirrors FIFO source enable bits. Requested per-sensor watermarks are converted to effective per-sensor watermarks for timestamp correction. FIFO read resets counters, reads FIFO byte count, clamps to requested max or internal 2080-byte buffer size, reads no-increment FIFO data, and counts valid gyro/accel packets before parse. Parsing applies timestamp interrupts to each sensor and delegates packet pushing to per-sensor parsers.

Dependencies and integration points: integrates core regmap/power state, gyro and accel parser APIs, IIO buffer setup, runtime PM, and the InvenSense timestamp helper. IRQ handling in core calls FIFO read/parse on threshold interrupts; accel/gyro IIO `hwfifo_flush_to_buffer` calls the flush helper.

Risks and edge cases: watermark math relies on ODR periods being multiples and explicitly excludes problematic 500 Hz usage in the comment. If both requested watermarks are zero, update returns without programming threshold. FIFO decode returns 0 for empty-message packets, stopping loops. The first FIFO count read after reset workaround is required for correctness. Reference counting must remain balanced across two IIO devices. `pm_runtime_get_sync()` is not checked in preenable.

Test signals: buffer enable/disable ordering with one and two sensors, FIFO source bits for accel/gyro/temp combinations, watermark calculations for differing ODR/watermark values, FIFO read clamping and empty FIFO behavior, packet decode for empty/accel/gyro/both/invalid headers, IRQ threshold read/parse path, manual hwfifo flush counts, and runtime PM reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.h -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.h

Purpose: FIFO data structures, bit definitions, inline validators, and function declarations shared by ICM-426xx buffer, gyro, accel, and core code.

Important APIs, types, and functions: defines FIFO source bits `INV_ICM42600_SENSOR_GYRO`, `ACCEL`, and `TEMP`. `struct inv_icm42600_fifo` stores FIFO reference count, enabled sources, internal period, requested/effective watermarks, sample counters, and 2080-byte DMA-aligned data buffer. `struct inv_icm42600_fifo_sensor_data` is a packed xyz BE16 triplet. Inline helpers convert BE16 data and detect the invalid all-`-32768` sentinel. Declarations include packet decode, buffer setup ops, FIFO init, FIFO enable, watermark update, read, parse, and hwfifo flush.

Control flow: core owns `struct inv_icm42600_fifo` inside shared state; common buffer code mutates it; gyro/accel parsers consume decoded packets using the inline validity helpers.

State and persistence behavior: the FIFO struct persists configuration and the most recent FIFO read buffer/counters across the read/parse sequence. Effective watermarks are stored separately from user-requested watermarks because timestamp correction uses the effective values.

Dependencies and integration points: included by `inv_icm42600.h` and buffer/sensor implementations; exposes `inv_icm42600_buffer_ops` to IIO kfifo setup.

Risks and edge cases: all invalid-sentinel detection requires x, y, and z to equal `-32768`; partial invalid axes are treated as valid. The 2080-byte buffer assumes 2048-byte FIFO plus read cache margin and must match hardware limits and read code.

Test signals: unit-style packet validation, invalid sentinel handling, buffer size assumptions, and compile checks for all common objects using the declarations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_buffer.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_core.c

Purpose: shared core for InvenSense ICM-426xx IMUs. It defines regmap banking/cache behavior, chip identification/default configs, shared configuration setters, IRQ/FIFO/APEX dispatch, regulator and PM handling, and the exported `inv_icm42600_core_probe()`.

Important APIs, types, and functions: exports `inv_icm42600_regmap_config`, SPI-specific `inv_icm42600_spi_regmap_config`, `inv_icm42600_get_mount_matrix()`, `inv_icm42600_odr_to_period()`, config setters for accel/gyro/temp, WoM enable/disable helpers, debugfs register access, core probe, and PM ops. `inv_icm42600_hw[]` maps supported chips to WHOAMI/name/default config. `inv_icm42600_set_pwr_mgmt0()` centralizes power-mode writes and startup/stop delay calculation. `inv_icm42600_setup()` validates WHOAMI, resets the chip, applies bus setup, sets endian/low-power clock behavior, and writes default config.

Control flow: core probe validates chip enum, resolves INT1 or first IRQ and trigger type, allocates shared state, reads mount matrix, enables `vdd`, waits power-up, enables `vddio`, sets up chip registers, enables timestamp registers, initializes FIFO, creates gyro and accel IIO devices, registers threaded IRQ, and enables autosuspend runtime PM. The top IRQ handler captures timestamps for both IIO devices, then the thread handles APEX status events and FIFO status; on FIFO threshold it reads and parses FIFO data.

State and persistence behavior: `st->conf` mirrors active hardware sensor config and is updated only after successful writes. Suspend stores gyro/accel/temp state, disables FIFO streaming, optionally keeps accel/APEX on for wakeup, disables WoM or regulators when not wake-capable, and powers sensors off. Resume restores IRQ/regulator state, sensor modes/temp, WoM, timestamp state, and FIFO stream mode. Runtime suspend powers all sensors off and disables vddio; runtime resume reenables vddio and leaves sensors to IIO paths.

Dependencies and integration points: depends on regmap ranges for virtual banks, regulators, fwnode IRQs and `drive-open-drain`, IIO mount matrices, runtime PM, threaded IRQs, gyro/accel/temp/buffer objects, and bus setup callbacks from I2C/SPI wrappers. SPI regmap uses `use_single_write` because that bus does not support burst writes.

Risks and edge cases: probe requires an IRQ; no polling fallback exists. `inv_icm42600_set_gyro_conf()` contains unreachable `return 0` after its real return, harmless but dead code. Startup/stop sleeps can be deferred; callers must sleep after dropping locks when requested. Suspend wakeup path disables IRQ while enabling wake and keeps accel on; imbalance would affect resume. Runtime PM state and system suspend interact, with early returns if already suspended. FIFO full only warns and data is lost.

Test signals: chip WHOAMI validation for every supported variant, bus setup callback execution, endian/FIFO/timestamp register setup, IRQ polarity/open-drain configuration, FIFO threshold IRQ path, WoM event IRQ path, system suspend/resume with and without wakeup-enabled accel events, runtime autosuspend/resume, regulator sequencing, mount matrix exposure, and default config per chip including ICM42686 full-scale ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_icm42600/inv_icm42600_core.c -->
