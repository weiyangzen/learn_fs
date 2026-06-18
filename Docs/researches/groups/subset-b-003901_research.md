# subset-b-003901 research

Grouped research for Linux IIO pressure and proximity drivers under `sources/distributed-fs/ceph-client/drivers/iio`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c

## Purpose
`hsc030pa_i2c.c` is the I2C transport wrapper for the Honeywell TruStability HSC/SSC pressure and temperature IIO driver. It does not implement conversion or IIO channel logic itself; it validates that the adapter supports plain I2C transfers and supplies a receive callback to the shared `hsc_common_probe()` core.

## Important APIs, types, and functions
The key hook is `hsc_i2c_recv(struct hsc_data *data)`, which sleeps for the HSC response time and reads `HSC_REG_MEASUREMENT_RD_SIZE` bytes into `data->buffer` with `i2c_transfer()`. `hsc_i2c_probe()` checks `I2C_FUNC_I2C` before calling the common Honeywell HSC probe. Match tables expose `honeywell,hsc030pa` for devicetree and `hsc030pa` for legacy I2C IDs.

## Control flow
Probe is entered by the I2C core, rejects adapters without raw I2C transaction support, then delegates all device allocation, channel setup, property parsing, and registration to the shared HSC core. Runtime reads in the core call the supplied receive function; the wrapper creates one read message with the client address, read flag, requested length, and the shared buffer.

## State and persistence behavior
This file owns no persistent state beyond the I2C driver's binding tables. Measurement bytes live in `struct hsc_data` owned by the core. Hardware state changes, if any, are performed by the common driver.

## Dependencies and integration points
It integrates Linux I2C, IIO through the common HSC core, module device tables, and the `IIO_HONEYWELL_HSC030PA` namespace. Its correctness depends on `hsc030pa.h` definitions and the common core's buffer lifetime.

## Risks
`msleep_interruptible()` return value is ignored, so signal-interrupted sleeps still attempt a read. A short successful transfer is converted to `-EIO`, but bus controllers with unusual behavior should be tested. The compatible string is shared with the SPI wrapper, so board descriptions must select the correct bus.

## Test signals
Build with the I2C HSC driver enabled, bind via devicetree and I2C ID, exercise adapters lacking `I2C_FUNC_I2C`, inject short and failed reads, and compare raw/processed pressure output against the shared core on real HSC/SSC hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c

## Purpose
`hsc030pa_spi.c` is the SPI transport wrapper for the Honeywell TruStability HSC/SSC pressure and temperature IIO driver. It provides a simple receive callback and leaves calibration, measurement decoding, and IIO registration to `hsc_common_probe()`.

## Important APIs, types, and functions
`hsc_spi_recv()` sleeps for `HSC_RESP_TIME_MS` then performs a `spi_read()` into the common `hsc_data` buffer. `hsc_spi_probe()` delegates to the common probe. SPI and OF match tables both advertise the `hsc030pa` device name or `honeywell,hsc030pa` compatible.

## Control flow
The SPI core invokes probe, which immediately calls the common HSC probe with `&spi->dev` and the receive callback. During direct-mode reads, the common core invokes `hsc_spi_recv()` to fetch the fixed-size measurement frame after the sensor response delay.

## State and persistence behavior
No wrapper-local mutable state is kept. The only runtime data is the common driver's buffer. SPI mode and speed are not forced in this wrapper, so they are expected to be correct from firmware or board setup.

## Dependencies and integration points
The file depends on Linux SPI, the common Honeywell HSC core namespace, and IIO infrastructure indirectly. It is loaded as a module SPI driver and imports `IIO_HONEYWELL_HSC030PA`.

## Risks
Unlike some SPI wrappers in this directory, this one does not constrain `spi->mode` or maximum speed, making devicetree or board data important. Interrupted sleep is ignored. A failed `spi_read()` propagates directly to IIO callers.

## Test signals
Probe through SPI ID and OF matching, verify SPI mode/speed combinations from board data, inject `spi_read()` failures, and compare sensor frame decoding with the I2C wrapper and common HSC tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/icp10100.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/icp10100.c

## Purpose
`icp10100.c` is an I2C IIO driver for InvenSense ICP-1010xx barometric pressure and temperature sensors. It performs command/response transfers with per-word CRC, reads OTP calibration, exposes pressure and temperature channels, supports selectable oversampling, and uses runtime PM to autosuspend the regulator-backed device.

## Important APIs, types, and functions
`struct icp10100_state` stores the I2C client, regulator, mutex, selected measurement mode, and four OTP calibration words. `struct icp10100_command` describes 16-bit commands, wait times, and response word counts. `icp10100_send_cmd()` is the central transfer helper and validates each response word with CRC8 polynomial `0x31`. `icp10100_init_chip()` checks the ID, reads calibration via OTP mode, and soft-resets. `icp10100_get_measures()` performs a mode-specific measurement under runtime PM. `icp10100_get_pressure()` applies the datasheet compensation formula. IIO callbacks implement raw/processed reads, oversampling availability, and oversampling writes.

## Control flow
Probe verifies plain I2C support, allocates an IIO device, gets and enables `vdd`, initializes the CRC table, validates the sensor ID, reads OTP coefficients, resets the chip, enables runtime PM with a two-second autosuspend delay, and registers the IIO device. A pressure read claims direct mode, resumes the device, sends the selected measurement command, waits for conversion, checks CRCs, converts raw pressure and temperature using the calibration LUT formula, then releases runtime PM. A temperature read uses the same measurement transaction but returns the raw temperature plus scale and offset attributes.

## State and persistence behavior
The persistent external state is the regulator-powered sensor. Driver state is `mode` for oversampling and `cal[]` captured at probe. Runtime PM toggles `vdd`; resume reenables the regulator and soft-resets the chip. The driver does not reread calibration after runtime resume, relying on stored OTP coefficients.

## Dependencies and integration points
It integrates I2C transfers, `crc8`, regulators, runtime PM, mutex serialization, and the IIO direct-mode ABI. OF and I2C tables bind `invensense,icp10100` / `icp10100`.

## Risks
The compensation path uses several 64-bit divisions and a final `uint32_t` pressure in mPa; boundary tests are important for extreme raw values. CRC errors map to `-EIO`, which is correct but can look like bus failure. Runtime resume only soft-resets, so any future stateful register configuration would need reapplication. Oversampling writes require power-of-two values and direct-mode claims; buffered extensions would need stronger locking.

## Test signals
Validate ID mismatch handling, CRC failure paths, OTP read sequence, regulator enable/disable, runtime suspend/resume, oversampling list and write validation for 1/2/4/8, and pressure compensation against datasheet vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/icp10100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.c

## Purpose
`mpl115.c` is the shared IIO core for Freescale/NXP MPL115A pressure and temperature sensors. It abstracts I2C and SPI register access behind `struct mpl115_ops`, reads factory coefficients, computes compensated pressure, exposes temperature raw/scale/offset, and optionally powers the sensor down through a shutdown GPIO using runtime PM.

## Important APIs, types, and functions
`struct mpl115_data` stores the device, mutex, coefficients `a0`, `b1`, `b2`, `c12`, optional shutdown GPIO, and bus ops. `mpl115_request()` starts a conversion and waits 3-4 ms. `mpl115_comp_pressure()` reads pressure and temperature ADC values and applies the Freescale AN3785 fixed-point formula. `mpl115_read_temp()` triggers and reads temperature. `mpl115_read_raw()` implements pressure processed values and temperature raw, scale, and offset. `mpl115_probe()` initializes the IIO device, calls bus-specific init, reads coefficients, configures runtime PM, and registers the device.

## Control flow
Bus wrappers call `mpl115_probe()` with a name and operations. The common probe allocates the IIO device, initializes the bus private state, reads four calibration words, gets optional `shutdown-gpios`, enables autosuspend when the GPIO is present, and registers two channels. Runtime pressure reads resume the device, request conversion, read both ADCs under the mutex, calculate kPa, then autosuspend. Temperature reads use the same conversion command but return the raw 10-bit temperature ADC.

## State and persistence behavior
Calibration coefficients are captured once at probe and retained in RAM. The only mutable driver state is the mutex-protected access sequence and runtime PM state. With a shutdown GPIO, runtime suspend drives shutdown high and resume drives it low with a 5-6 ms wake delay; without the GPIO the sensor stays powered.

## Dependencies and integration points
The core exports `mpl115_probe()` and `mpl115_dev_pm_ops` in the `IIO_MPL115` namespace for I2C and SPI wrappers. It depends on IIO, runtime PM, GPIO descriptors, and bus-supplied read/write callbacks.

## Risks
`pm_runtime_get_sync()` return values are not checked before bus access, so runtime PM failures could lead to stale or failed I/O. Coefficients are assumed valid and are not sanity checked. The TODO notes suspend synchronization; system suspend racing direct reads is a maintenance concern. The negative temperature scale must be preserved exactly for ABI compatibility.

## Test signals
Use known coefficient/raw examples to verify pressure compensation, test optional shutdown GPIO autosuspend/resume timing, inject bus read/write failures, verify temperature scale/offset output, and compile both I2C and SPI wrappers against the exported namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.h

## Purpose
`mpl115.h` is the private shared header connecting the MPL115 common core with its I2C and SPI bus wrappers. It defines the bus operation contract and exposes the common probe and PM ops.

## Important APIs, types, and functions
`struct mpl115_ops` provides `init`, `read`, and `write` callbacks. `mpl115_probe()` takes a device, IIO name, and ops table. `mpl115_dev_pm_ops` is exported for bus drivers to attach runtime PM behavior.

## Control flow
There is no executable control flow in the header. Bus wrappers implement the callbacks, pass them to `mpl115_probe()`, and reference `mpl115_dev_pm_ops` in their driver structures.

## State and persistence behavior
The header stores no state. It establishes that all per-device state is private to the common core or bus wrapper.

## Dependencies and integration points
It includes runtime PM declarations and depends on `struct device` from included kernel headers. The header is internal to the MPL115 driver family and not a userspace ABI.

## Risks
Changing callback semantics would affect both bus wrappers. The `init` callback is mandatory even when it is a no-op for I2C, so future wrappers must provide it.

## Test signals
Compile all MPL115 objects together, ensure namespace imports resolve, and verify both I2C and SPI wrappers still satisfy the operations contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c

## Purpose
`mpl115_i2c.c` is the I2C bus wrapper for the MPL115A2 pressure/temperature sensor. It supplies SMBus register access callbacks to the shared MPL115 core.

## Important APIs, types, and functions
`mpl115_i2c_read()` uses `i2c_smbus_read_word_swapped()` for 16-bit register reads. `mpl115_i2c_write()` uses `i2c_smbus_write_byte_data()` to issue conversion commands. `mpl115_i2c_probe()` checks `I2C_FUNC_SMBUS_WORD_DATA`, fetches the I2C ID name, and calls `mpl115_probe()`.

## Control flow
The I2C driver binds to `mpl115`, verifies adapter functionality, and delegates device initialization to the common core. Runtime reads and writes are callback-driven through the ops table.

## State and persistence behavior
No wrapper-local state is kept. All calibration, PM, and IIO state lives in the common `mpl115_data` object.

## Dependencies and integration points
It integrates Linux I2C/SMBus with the `IIO_MPL115` core and attaches `mpl115_dev_pm_ops` to the driver. The expected 7-bit address is documented as `0x60`.

## Risks
The functionality check covers word data but not byte-data writes explicitly; most SMBus-capable adapters provide both but adapter edge cases should be tested. Endianness relies on the swapped SMBus helper matching the sensor register layout.

## Test signals
Probe with adapters missing word-data support, verify coefficient reads and conversion commands on MPL115A2 hardware, and run runtime PM tests through the common shutdown GPIO path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c

## Purpose
`mpl115_spi.c` is the SPI bus wrapper for the MPL115A1 pressure/temperature sensor. It translates the common MPL115 register operations into SPI command sequences and delegates IIO behavior to the shared core.

## Important APIs, types, and functions
`struct mpl115_spi_buf` holds reusable TX/RX buffers. `mpl115_spi_init()` allocates that buffer and stores it as SPI driver data. `mpl115_spi_read()` performs a four-byte transfer containing two read commands and returns the two received data bytes. `mpl115_spi_write()` sends a two-byte write command/value pair. `mpl115_spi_probe()` calls `mpl115_probe()`.

## Control flow
On probe the common core invokes the wrapper's `init`, then reads coefficients through the SPI read callback. Runtime conversions use the write callback for `MPL115_CONVERT` and read callback for ADC data.

## State and persistence behavior
The wrapper keeps only the allocated SPI transfer buffer as device driver data. Calibration and PM state are common-core state.

## Dependencies and integration points
It depends on SPI synchronous transfers and the internal `IIO_MPL115` namespace. It shares the same driver name and IDs as the I2C wrapper but binds on the SPI bus.

## Risks
The driver does not force SPI mode or maximum speed, so firmware configuration must match the MPL115A1 requirements. The shared buffer is safe because the common core serializes sensor access with its mutex. Short SPI transfers are surfaced through `spi_sync_transfer()` return values only.

## Test signals
Exercise coefficient and ADC reads over SPI, verify the two-command read layout with a logic analyzer or mock controller, test bus errors, and compare processed pressure against I2C/common formula tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl115_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl3115.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl3115.c

## Purpose
`mpl3115.c` is an I2C IIO driver for the Freescale/NXP MPL3115A2 pressure and temperature sensor. It supports direct raw reads, sample-frequency programming, optional data-ready trigger, triggered buffers, and rising threshold events for pressure and temperature.

## Important APIs, types, and functions
`struct mpl3115_data` stores the I2C client, optional data-ready trigger, mutex, and cached `CTRL_REG1`/`CTRL_REG4` state. `mpl3115_request()` starts one-shot measurement and polls for `OST` clear. `mpl3115_read_info_raw()` reads 20-bit pressure or 12-bit signed temperature. `mpl3115_read_raw()`, `mpl3115_read_avail()`, and `mpl3115_write_raw()` implement raw, scale, and sampling-frequency ABI. `mpl3115_trigger_handler()` fills the scan buffer. IRQ code handles data-ready and threshold interrupts. Event callbacks enable/disable threshold IRQ bits and read/write threshold registers.

## Control flow
Probe validates `WHO_AM_I`, allocates the IIO device, resets the chip, sets 64x oversampling, optionally configures an INT1/INT2 IRQ from firmware, registers an IIO trigger when IRQ exists, installs the triggered buffer, and registers the IIO device. Direct reads claim direct mode, trigger one-shot conversion, read output registers, then release. When a data-ready interrupt fires, the IRQ handler polls the trigger; the trigger handler reads selected channels and pushes a timestamped buffer. Threshold interrupt bits push IIO events and read output registers to clear source bits.

## State and persistence behavior
`ctrl_reg1` and `ctrl_reg4` are cached mirrors used to coordinate active mode, data-ready IRQs, and threshold IRQs. Sampling frequency writes program `CTRL_REG2` directly. Threshold writes persist in target registers until reset. Suspend puts the device in standby; resume restores cached `CTRL_REG1`.

## Dependencies and integration points
The file uses I2C SMBus/block transfers, firmware IRQ names `INT1`/`INT2`, Linux IRQ trigger type, IIO events, triggers, and triggered buffers. OF binds `fsl,mpl3115`; I2C ID is `mpl3115`.

## Risks
`iio_triggered_buffer_setup()` and `iio_device_register()` are unmanaged while much of probe is devm-managed, so cleanup ordering is explicit. `mpl3115_config_interrupt()` rolls back `CTRL_REG1` on `CTRL_REG4` failure but does not restore failed partial threshold writes. The IRQ type must be rising or falling; bad firmware IRQ flags reject trigger support. Active-mode cache correctness is central to avoiding unwanted continuous measurements.

## Test signals
Verify WHOAMI rejection, one-shot timeout handling, pressure/temp raw scale, all sampling-frequency table entries, INT1 and INT2 polarity setup, trigger enable/disable transitions, threshold event enable/value paths, suspend/resume restoration, and buffer scans with one or both channels enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mpl3115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c

## Purpose
`mprls0025pa.c` is the shared core for Honeywell MicroPressure MPR pressure sensors. It supports I2C and SPI bus wrappers, regulator and reset GPIO control, devicetree pressure-range/transfer-function configuration, direct raw reads, scale/offset reporting, optional end-of-conversion IRQs, and triggered buffers.

## Important APIs, types, and functions
Transfer-function tables map Honeywell functions A/B/C to raw output min/max counts, and triplet tables map part-number pressure ranges to pascals. `mpr_reset()` toggles the optional reset GPIO. `mpr_read_pressure()` issues a sync conversion command, waits by IRQ completion or fixed delay, reads a four-byte frame, validates status bits, and extracts a 24-bit pressure count. `mpr_trigger_handler()` pushes pressure plus timestamp. `mpr_read_raw()` exposes raw count, scale, and offset. `mpr_common_probe()` parses properties, calculates scale/offset, requests EOC IRQ if present, configures regulator/reset, installs a triggered buffer, and registers the IIO device.

## Control flow
Bus wrappers call `mpr_common_probe()` with transport callbacks and an IRQ. Probe enables `vdd`, reads `honeywell,transfer-function`, then either `honeywell,pressure-triplet` or explicit `honeywell,pmin-pascal`/`pmax-pascal`, validates limits, computes the userspace ABI scale and offset, sets up optional EOC completion, resets the sensor, and registers the direct/buffered IIO device. Direct reads and triggered-buffer reads both lock `data->lock` around the command/wait/read sequence.

## State and persistence behavior
Driver state includes parsed pressure range, transfer-function selection, calculated ABI scale/offset, optional IRQ/completion, reset GPIO, and TX/RX buffers. The sensor's pressure range and transfer function are physical part characteristics, not programmable runtime state. No sampled values are cached except the temporary buffered channel struct.

## Dependencies and integration points
The core exports `mpr_common_probe()` in namespace `IIO_HONEYWELL_MPRLS0025PA`. It depends on IIO triggered buffers, completions, IRQs, GPIO descriptors, regulators, property APIs, unaligned big-endian helpers, and bus-supplied read/write ops.

## Risks
Property validation is critical: wrong transfer function or range yields misleading pressure conversion without obvious bus failure. If an EOC IRQ is declared but never fires, direct reads block up to one second and return `-ETIMEDOUT`. Status handling accepts only `MPR_ST_POWER`; memory/math error bits become `-EIO`, which is conservative. The scale calculation uses integer division and split nanounits, so regression tests need exact ABI values.

## Test signals
Cover all transfer functions, triplet and explicit pressure-range parsing, invalid property combinations, reset GPIO behavior, regulator failure, IRQ and polling measurement paths, busy/status-error frames, triggered buffer pushes, and I2C/SPI transport short-transfer failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h

## Purpose
`mprls0025pa.h` is the private contract shared by the Honeywell MPR common core and its I2C/SPI wrappers. It defines command constants, the runtime data structure, bus operations, and the exported common probe.

## Important APIs, types, and functions
Constants define measurement frame size and NOP/SYNC command packet lengths. `enum mpr_func_id` names transfer functions A, B, and C. `struct mpr_data` holds device pointers, ops, pressure configuration, scale/offset, reset GPIO, IRQ completion, scan buffer, and DMA-aligned RX/TX buffers. `struct mpr_ops` supplies bus read/write callbacks. `mpr_common_probe()` is the shared registration entry point.

## Control flow
There is no executable flow in the header. Bus wrappers fill `struct mpr_ops` and call `mpr_common_probe()`, while the core uses the fields defined here for locking, conversion, and IIO buffering.

## State and persistence behavior
The header describes per-device state but stores none. The DMA alignment annotation on `rx_buf` is part of the transport safety contract.

## Dependencies and integration points
It depends on kernel completion, mutex, IIO, and type definitions. It is internal to the MPR driver family and imported by both bus wrappers.

## Risks
Changing packet lengths, command values, or buffer sizes affects both transports. `struct mpr_data` exposes many core internals to wrappers, so wrappers can accidentally rely on layout details.

## Test signals
Compile both transport modules with the core, validate namespace exports, and run static checks for DMA alignment and buffer-size assumptions in I2C/SPI callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c

## Purpose
`mprls0025pa_i2c.c` is the I2C transport wrapper for the Honeywell MicroPressure MPR common driver. It implements the common read/write callbacks using I2C master send/receive.

## Important APIs, types, and functions
`mpr_i2c_read()` receives a requested byte count into `data->rx_buf`, rejecting counts larger than `MPR_MEASUREMENT_RD_SIZE` and short reads. `mpr_i2c_write()` sends the sync command packet from `data->tx_buf` with length `MPR_PKT_SYNC_LEN`. `mpr_i2c_probe()` checks adapter support and delegates to `mpr_common_probe()` with `client->irq`.

## Control flow
The I2C core binds by OF or I2C ID, probe checks functionality, and the common core performs all device setup. During measurement, the core calls `write(SYNC)` to start conversion and `read(NOP)` to fetch the status/data frame; the I2C wrapper ignores the command argument on reads because the bus protocol just receives.

## State and persistence behavior
No wrapper-local state is stored. It uses the common `mpr_data` TX/RX buffers and IRQ value.

## Dependencies and integration points
It integrates Linux I2C, devicetree `honeywell,mprls0025pa`, I2C ID `mprls0025pa`, and namespace `IIO_HONEYWELL_MPRLS0025PA`.

## Risks
The functionality check uses `I2C_FUNC_SMBUS_READ_BYTE` although the implementation uses `i2c_master_recv()`/`i2c_master_send()`, so adapter capability gating may be broader or narrower than ideal. Short transfers are handled as `-EIO`. The fixed sync length ignores the `unused` count parameter.

## Test signals
Use adapters with and without required functionality, inject short master send/receive results, verify IRQ propagation to the common core, and compare pressure reads with SPI on identical property configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c

## Purpose
`mprls0025pa_spi.c` is the SPI transport wrapper for Honeywell MicroPressure MPR sensors. It provides the common core with a full-duplex command/data transfer helper that satisfies the sensor's chip-select setup timing.

## Important APIs, types, and functions
`mpr_spi_xfer()` validates packet length, stores the command in `tx_buf[0]`, performs a dummy delayed transfer for at least 2.5 microseconds after chip select assertion, then transfers the requested packet with TX and RX buffers. `mpr_spi_ops` uses the same function for read and write. Probe delegates to `mpr_common_probe()` with the SPI IRQ.

## Control flow
The SPI driver binds by OF or SPI ID and calls the common probe. Measurement start and result read both become `spi_sync_transfer()` operations through `mpr_spi_xfer()`, with the command byte differing between SYNC and NOP.

## State and persistence behavior
No wrapper-specific persistent state exists. The wrapper uses common buffers and SPI device configuration supplied by firmware or board setup.

## Dependencies and integration points
It depends on Linux SPI, delayed SPI transfers, OF/SPI ID matching for `honeywell,mprls0025pa`, and the `IIO_HONEYWELL_MPRLS0025PA` namespace.

## Risks
SPI mode and maximum frequency are not forced here. The timing delay is encoded as an empty transfer; controller support for delay-only transfers should be covered. Because one helper implements both read and write, changes to packet-length semantics affect both measurement phases.

## Test signals
Verify chip-select delay with a controller or trace, inject `spi_sync_transfer()` failures, check packet overflow rejection, test IRQ and polling modes through the common core, and confirm board-configured SPI mode is compatible.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/mprls0025pa_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611.h

## Purpose
`ms5611.h` is the private interface for the MS5611/MS5607 pressure and temperature sensor family. It defines shared commands, oversampling descriptors, per-device state, bus callbacks, and the exported common probe.

## Important APIs, types, and functions
Command constants cover reset, ADC read, and PROM word read. `struct ms5611_osr` describes conversion delay, command, and oversampling ratio. `struct ms5611_state` stores the bus client pointer, mutex, selected pressure/temp OSR, PROM coefficients, bus operations, and the chip-specific compensation callback. `ms5611_probe()` is the common core entry point.

## Control flow
Bus wrappers allocate an IIO device with `struct ms5611_state`, fill reset/PROM/ADC callbacks and `client`, then call `ms5611_probe()` with the matched chip type. The core uses the state to reset, read PROM, validate CRC, and service direct/buffered reads.

## State and persistence behavior
The header describes RAM state only. PROM coefficients are copied into `prom[]` at probe; selected OSR pointers are mutable runtime state.

## Dependencies and integration points
It depends on IIO and mutex headers and is shared by I2C, SPI, and core files. The comment requiring `cmd` word alignment is important for the SPI wrapper's `spi_write_then_read()` usage.

## Risks
The function-pointer contract must remain synchronized with both bus wrappers. Changing `struct ms5611_osr` layout can break the documented SPI alignment assumption.

## Test signals
Compile I2C/SPI/core combinations, validate type selection for MS5611 vs MS5607, and run static checks for callback initialization before `ms5611_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c

## Purpose
`ms5611_core.c` is the shared IIO core for Measurement Specialties MS5611 and MS5607 pressure/temperature sensors. It reads and CRC-validates PROM calibration, applies chip-specific second-order compensation, supports separate pressure and temperature oversampling ratios, and exposes direct and triggered-buffer IIO reads.

## Important APIs, types, and functions
`ms5611_prom_is_valid()` implements the PROM CRC4 check. `ms5611_read_prom()` fills the coefficient array. `ms5611_temp_and_pressure_compensate()` and `ms5607_temp_and_pressure_compensate()` apply each chip's datasheet formula. `ms5611_read_raw()` returns processed pressure/temp, scale, and oversampling ratio. `ms5611_write_raw()` validates and changes OSR under direct-mode claim. `ms5611_trigger_handler()` pushes pressure, temperature, and timestamp. `ms5611_probe()` selects compensation, initializes OSR defaults, reads PROM, installs a triggered buffer, and registers IIO.

## Control flow
The bus wrapper allocates state and callbacks, then calls `ms5611_probe()`. Probe enables optional `vdd`, resets the chip, reads and validates PROM, sets up channels and buffer support, and registers. Runtime read paths lock the state mutex, use the bus callback to perform temperature and pressure ADC conversions at the selected OSRs, compensate, and format values. Buffered reads use the same measurement path from the trigger handler.

## State and persistence behavior
Persistent driver state includes PROM coefficients and current pressure/temp OSR pointers. OSR changes affect later conversions and are blocked while buffers are active by `iio_device_claim_direct()`. The hardware itself is reset during probe but not otherwise configured persistently by the core.

## Dependencies and integration points
The core exports `ms5611_probe()` in namespace `IIO_MS5611` and depends on regulators, IIO sysfs, triggered buffers, bus callbacks, and unaligned/endianness handling in wrappers.

## Risks
PROM CRC validation mutates `prom[7]` by masking the CRC nibble during the check; this mirrors common algorithm usage but is worth preserving intentionally. Compensation uses 64-bit arithmetic and second-order low-temperature corrections; incorrect sign/shift changes produce plausible but wrong data. OSR write path must remain direct-mode protected to avoid changing conversion timing during buffered acquisition.

## Test signals
Use datasheet coefficient/raw vectors for MS5611 and MS5607, corrupt PROM CRC tests, OSR read/write validation for all 256-4096 ratios, buffer scan tests, regulator failure injection, and I2C/SPI parity tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_i2c.c

## Purpose
`ms5611_i2c.c` is the I2C wrapper for MS5611/MS5607 sensors. It implements reset, PROM reads, and ADC conversion sequences using SMBus/I2C block operations, then delegates common IIO behavior to `ms5611_probe()`.

## Important APIs, types, and functions
`ms5611_i2c_reset()` writes the reset command byte. `ms5611_i2c_read_prom_word()` reads swapped 16-bit PROM words. `ms5611_i2c_read_adc()` reads three bytes and forms a big-endian 24-bit value. `ms5611_i2c_read_adc_temp_and_pressure()` issues temperature and pressure conversion commands with OSR-specific sleeps. Probe verifies adapter functionality, allocates IIO state, fills callbacks, and calls the core.

## Control flow
Probe binds by I2C or OF table, checks write-byte, read-word, and read-block support, initializes state callbacks, and passes matched driver data as chip type. Runtime conversions are serialized by the core mutex and call the wrapper conversion helper.

## State and persistence behavior
No extra wrapper state beyond `st->client` and callback assignments. OSR and PROM state live in the common `ms5611_state`.

## Dependencies and integration points
It depends on Linux I2C/SMBus, `get_unaligned_be24()`, OF compatibles `meas,ms5611` and `meas,ms5607`, and namespace `IIO_MS5611`.

## Risks
Conversion timing depends on the selected OSR delay and assumes `usleep_range()` margins are sufficient for all parts. Short block reads are not explicitly checked because the SMBus helper returns errors or byte count semantics; hardware/controller tests should cover this. OF match data does not carry type, so I2C IDs are important on non-enumerated paths.

## Test signals
Adapter capability rejection, reset command success/failure, PROM read endian tests, 24-bit ADC assembly, all OSR delays, and matching for both MS5611 and MS5607.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c

## Purpose
`ms5611_spi.c` is the SPI wrapper for MS5611/MS5607 sensors. It configures safe SPI parameters, implements reset/PROM/ADC callbacks, and delegates IIO registration and compensation to the common core.

## Important APIs, types, and functions
`ms5611_spi_reset()` sends the reset command. `ms5611_spi_read_prom_word()` uses `spi_w8r16be()`. `ms5611_spi_read_adc()` writes the read-ADC command and reads three bytes. `ms5611_spi_read_adc_temp_and_pressure()` issues temperature and pressure conversion commands via `spi_write_then_read()` and waits for OSR-specific conversion times. Probe sets SPI mode 0, caps speed at 20 MHz, calls `spi_setup()`, fills callbacks, and invokes `ms5611_probe()`.

## Control flow
The SPI core probes the device, the wrapper enforces bus settings, and the common core performs reset/PROM validation/registration. Runtime conversions call wrapper helpers in the sequence temperature conversion/read, pressure conversion/read.

## State and persistence behavior
Wrapper state is limited to `st->client = spi` and callback assignments. Common state owns coefficients and OSR selections.

## Dependencies and integration points
It depends on Linux SPI, OF/SPI IDs for `meas,ms5611` and `meas,ms5607`, unaligned big-endian ADC assembly, and namespace `IIO_MS5611`.

## Risks
The code relies on `&osr->cmd` being suitably aligned for `spi_write_then_read()`, as documented in the shared header. Board-provided `max_speed_hz` is only capped, not raised. Type selection comes from `spi_get_device_id()`, so OF-only binding must still map to a SPI ID.

## Test signals
Verify SPI mode/speed setup, PROM endian reads, ADC reads, all OSR conversion delays, MS5611/MS5607 ID matching, and bus error propagation into common direct and buffered reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5611_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5637.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5637.c

## Purpose
`ms5637.c` is an I2C IIO driver for Measurement Specialties MS5637-family pressure and temperature sensors, including MS5803, MS5805, MS5837, and MS8607 temp/pressure function. It reuses the common `ms_sensors` temperature/pressure helper library.

## Important APIs, types, and functions
`struct ms_tp_data` pairs an IIO name with hardware metadata. `ms5637_samp_freq[]` maps resolution index to sample-frequency ABI values. `ms5637_read_raw()` calls `ms_sensors_read_temp_and_pressure()` and returns processed temperature or pressure, or current sample frequency. `ms5637_write_raw()` selects resolution by frequency. Probe initializes `struct ms_tp_dev`, resets the sensor, reads PROM through `ms_sensors_tp_read_prom()`, and registers IIO.

## Control flow
Probe checks I2C functionality for word writes/reads and block reads, obtains match data from OF or I2C ID, allocates an IIO device, sets default resolution to the device's max resolution index, resets with command `0x1e`, reads PROM, and registers. Reads call into the common library, which performs conversion sequencing and compensation using `dev_data->hw` and `res_index`.

## State and persistence behavior
Mutable driver state is `res_index`, selected through the shared sampling-frequency attribute. PROM and hardware metadata live in `ms_tp_dev`. No runtime PM or caching is implemented in this file.

## Dependencies and integration points
It depends on I2C, IIO sysfs, mutexes, and `../common/ms_sensors/ms_sensors_i2c.h` under namespace `IIO_MEAS_SPEC_SENSORS`. It supports multiple OF compatibles and I2C IDs.

## Risks
Sampling-frequency values are an abstraction over resolution index, not autonomous continuous sampling. The write path does not claim direct mode because there is no buffer support, but concurrent sysfs reads rely on common-library locking. Match data is mandatory; missing ACPI/I2C data returns `-EINVAL`.

## Test signals
Probe each supported compatible, verify PROM read and CRC behavior through the common library, test all sample-frequency values up to each device's `max_res_index`, and compare processed pressure/temperature against known vectors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/ms5637.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c

## Purpose
`rohm-bm1390.c` is an I2C/regmap IIO driver for the ROHM BM1390 pressure sensor. It supports direct raw reads, scale reporting, optional IRQ-driven data-ready triggers, hardware FIFO buffering with watermarks, and temperature sampling alongside pressure.

## Important APIs, types, and functions
Regmap access tables mark volatile, precious, read-only, and no-increment ranges. `struct bm1390_data` stores timestamps, trigger, regmap, IRQ, state, watermark, trigger flag, sample buffer, and a mutex protecting FIFO/read sequences. `bm1390_chip_init()` powers/reset/releases the sensor and configures IIR filtering. `bm1390_read_data()` performs direct continuous-mode measurement. `__bm1390_fifo_flush()` drains the four-sample pressure FIFO, derives timestamps, and appends temperature if selected. Trigger and IRQ handlers coordinate data-ready and FIFO watermark operation. Probe initializes regmap, regulator, chip, buffer, optional trigger, and IIO registration.

## Control flow
Probe enables `vdd`, reads the part ID, allocates IIO state, initializes the chip, sets up the triggered buffer, and, if an IRQ exists, registers trigger and FIFO-capable info operations. Direct raw reads claim direct mode, start continuous measurement, sleep for the maximum measurement time, read the requested channel, and stop measurement. Software-buffer mode without an external trigger enables the hardware FIFO and WMI interrupt. Triggered mode uses DRDY interrupts to push one sample at a timestamp captured in the hard IRQ.

## State and persistence behavior
Driver state tracks whether the device is in single-sample or FIFO mode, whether the trigger is enabled, the configured watermark, and timestamp interpolation state. Regmap cache is reinitialized after reset. Hardware register configuration for IIR/filtering, FIFO enable, WMI/DRDY IRQs, and measurement mode persists until disabled or reset.

## Dependencies and integration points
It depends on I2C regmap, regulators, IIO triggers, triggered buffers, hardware FIFO callbacks, IRQs, and firmware-provided optional IRQ. OF compatible is `rohm,bm1390glv-z`.

## Risks
`bm1390_read_data()` returns `0` instead of `ret` after attempting to stop measurement, which means channel read errors in the switch path should be reviewed carefully. FIFO sequencing is delicate: accessing other registers mid-FIFO can drop samples, hence the mutex and explicit FIFO_LVL close read. Temperature is one value applied to all flushed pressure samples. IRQ-less devices cannot use FIFO buffering.

## Test signals
Test part-ID read, regulator failure, direct pressure/temp reads and scale values, trigger enable/disable, FIFO watermark values 2 and 3, FIFO level corruption handling, timestamp interpolation, IRQ-less mode, and regmap error injection during FIFO close and sample reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/rohm-bm1390.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/sdp500.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/sdp500.c

## Purpose
`sdp500.c` is an I2C IIO driver for Sensirion SDP500/SDP510 differential pressure sensors. It starts continuous measurement, reads three-byte samples, validates Sensirion CRC8, and exposes pressure raw plus scale.

## Important APIs, types, and functions
`struct sdp500_data` stores the device pointer. `sdp500_start_measurement()` sends command `0xf1`. `sdp500_read_raw()` receives two pressure bytes plus CRC, computes CRC8 polynomial `0x31`, returns the big-endian raw value, or returns scale `1/60`. Probe enables `vdd`, populates the CRC table, starts measurement, discards the first invalid sample, and registers IIO.

## Control flow
Probe powers the device, allocates IIO state, starts continuous measurement, drops one initial frame, and registers. Each raw read performs an `i2c_master_recv()` of exactly three bytes and validates the trailing CRC before returning raw pressure.

## State and persistence behavior
The sensor remains in its measurement mode after probe. The driver keeps no lock or cached value; state is limited to the device pointer and global CRC table. Power is devm-regulator managed.

## Dependencies and integration points
It depends on I2C master receive, CRC8 helpers, regulators, unaligned big-endian access, and IIO direct mode. OF compatible is `sensirion,sdp500`.

## Risks
There is no adapter functionality check and no serialization, so future extensions with configuration writes would need locking. The first sample discard ignores its return value. Raw value is treated unsigned despite differential pressure sensors often representing signed flow/pressure concepts; ABI expectations should be verified against the datasheet.

## Test signals
Validate CRC pass/fail paths, short reads, start-measurement failures, regulator errors, first-sample discard behavior, scale ABI, and real sensor readings for positive and negative differential pressure cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/sdp500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h

## Purpose
`st_pressure.h` is the shared header for STMicroelectronics pressure sensor core and bus drivers. It defines supported device names, enum IDs, default platform data, and buffer/trigger helper declarations.

## Important APIs, types, and functions
`enum st_press_type` names LPS001WP, LPS25H, LPS331AP, LPS22HB, LPS33HW, LPS35HW, LPS22HH, and LPS22DF variants. Device-name macros are used by I2C/SPI ID tables and settings lookup. `default_press_pdata` selects DRDY INT1 by default. When `CONFIG_IIO_BUFFER` is enabled, `st_press_allocate_ring()` and `st_press_trig_set_state()` are declared; otherwise the ring allocator is an inline no-op and trigger state is NULL.

## Control flow
The header has no runtime flow. Bus drivers include it for names and call declarations; the core uses the buffer declarations conditionally.

## State and persistence behavior
No state is stored in the header. `default_press_pdata` is a constant fallback object used during probe when no platform data exists and the sensor has DRDY support.

## Dependencies and integration points
It depends on `linux/iio/common/st_sensors.h` and is internal to the ST pressure driver family.

## Risks
Device-name macros must stay synchronized with settings tables and bus ID tables. Conditional buffer stubs affect build coverage across `CONFIG_IIO_BUFFER` combinations.

## Test signals
Compile with and without IIO buffer support, verify every device-name macro resolves in core settings and bus match tables, and check DRDY default behavior on IRQ-capable sensors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c

## Purpose
`st_pressure_buffer.c` provides triggered-buffer glue for ST pressure sensors using the generic ST sensors IIO helper layer.

## Important APIs, types, and functions
`st_press_trig_set_state()` forwards trigger enable/disable to `st_sensors_set_dataready_irq()`. Buffer setup ops enable the sensor in `postenable` and disable it in `predisable` through `st_sensors_set_enable()`. `st_press_allocate_ring()` installs a devm triggered buffer using the common `st_sensors_trigger_handler()`.

## Control flow
The core calls `st_press_allocate_ring()` during common probe. When a buffer is enabled, IIO calls the postenable hook to power/enable sampling. Trigger events are handled by the common ST trigger handler. Disabling the buffer powers the sensor down.

## State and persistence behavior
This file stores no state. It mutates hardware enable and data-ready IRQ state through the shared ST sensor data associated with the IIO device.

## Dependencies and integration points
It depends on IIO buffers/triggers and the generic ST sensors common helpers. It is compiled only when buffer support is enabled through the header declarations.

## Risks
Because enable/disable is delegated, regressions usually come from changes in common ST helper semantics. The ring setup uses the parent device for devm lifetime, so parent/child device lifetime must stay as designed.

## Test signals
Enable and disable buffered capture, verify data-ready IRQ masking, confirm sensor power transitions, and build with trigger/buffer configs toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c

## Purpose
`st_pressure_core.c` is the shared IIO core for multiple STMicroelectronics pressure sensors. It defines per-chip channel layouts, register settings, full-scale/ODR tables, data-ready interrupt metadata, raw/scale/offset/sample-frequency ABI, trigger ops, settings lookup, and the common probe sequence.

## Important APIs, types, and functions
Channel arrays describe pressure/temp scan layout for generic 24-bit pressure devices, LPS001WP, and LPS22HB-style parts. `st_press_sensors_settings[]` contains WAI IDs, supported names, output data rate registers, power bits, full-scale gains, block-data-update bits, data-ready IRQ registers, SPI mode bits, multiread behavior, and boot times. `st_press_get_settings()` maps a device name to settings. `st_press_read_raw()` delegates raw reads to `st_sensors_read_info_raw()` and returns pressure/temperature scale, offset, and ODR. `st_press_write_raw()` sets ODR. `st_press_common_probe()` verifies ID, initializes common ST sensor state, sets channels/fullscale/ODR, allocates ring/trigger, and registers IIO.

## Control flow
Bus wrappers configure transport-specific `st_sensor_data` and call `st_press_common_probe()`. The common probe verifies WAI, assigns channel tables, selects the first full-scale entry and first ODR, applies default DRDY platform data when appropriate, initializes the sensor through the common ST layer, installs buffered support, optionally allocates a trigger if an IRQ exists, and registers. Runtime sysfs reads either fetch raw data from the hardware or return computed ABI constants from current full-scale and ODR state.

## State and persistence behavior
Mutable state is mostly in `struct st_sensor_data`: current full-scale pointer, selected ODR, IRQ, transport, and common settings. ODR writes persist to hardware registers. Buffer enable and trigger state change sensor power and DRDY IRQs via common helpers. No sampled values are cached in this file.

## Dependencies and integration points
The core imports and exports the `IIO_ST_SENSORS` namespace and depends heavily on the generic ST sensors framework, IIO sysfs, debugfs reg access, triggered buffers, and bus wrappers. Supported devices include LPS331AP, LPS001WP, LPS25H, LPS22HB, LPS33HW, LPS35HW, LPS22HH, and LPS22DF.

## Risks
The settings table is the main risk surface: wrong WAI, ODR mask, BDU bit, multiread bit, or DRDY register silently breaks a whole variant. Temperature offset math is ABI-sensitive. The code casts away constness for channel/settings pointers to match common APIs. New variants must keep name tables, enum values, and settings synchronized.

## Test signals
Build all ST pressure variants, test WAI verification, ODR read/write for each table, raw/scale/offset ABI values, buffer enable/disable, DRDY trigger operation on INT1/INT2-capable parts, SPI multiread behavior, and debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c

## Purpose
`st_pressure_i2c.c` is the I2C bus wrapper for STMicroelectronics pressure sensors. It maps firmware/device names to shared settings, configures the generic ST I2C transport, enables power, and delegates to the common pressure core.

## Important APIs, types, and functions
OF match entries map ST compatibles to device-name strings. ACPI match includes `SNO9210` for LPS22HB. I2C IDs map names to `enum st_press_type`. `st_press_i2c_probe()` normalizes the device name, looks up settings with `st_press_get_settings()`, allocates `struct st_sensor_data`, calls `st_sensors_i2c_configure()`, enables power, and calls `st_press_common_probe()`.

## Control flow
The I2C core probes the device, name normalization reconciles firmware IDs, settings lookup selects the chip table, and the wrapper wires the I2C regmap/transfer functions through the ST common layer. The common core handles ID verification and IIO registration.

## State and persistence behavior
Wrapper state is the common `st_sensor_data` allocated as IIO private data. Power enable persists for the device lifetime subject to common ST power handling.

## Dependencies and integration points
It depends on Linux I2C, OF/ACPI/I2C ID matching, `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`.

## Risks
Name normalization and settings lookup must match the core settings table; an unsupported alias fails probe. Power enable happens before WAI verification, so probe failure paths rely on devm/common cleanup. ACPI support is much narrower than OF/I2C tables.

## Test signals
Probe every OF compatible and I2C ID, verify ACPI `SNO9210`, exercise unsupported names, inject I2C configure/power failures, and run common ST raw/buffer tests through I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c

## Purpose
`st_pressure_spi.c` is the SPI bus wrapper for STMicroelectronics pressure sensors. It maps SPI modalias/OF compatibles to common settings, configures the generic ST SPI transport, enables power, and invokes the common pressure core.

## Important APIs, types, and functions
OF match entries include both legacy `*-press` and newer single-chip compatible strings. `st_press_spi_probe()` normalizes `spi->modalias`, looks up settings, allocates `struct st_sensor_data`, calls `st_sensors_spi_configure()`, enables power, and calls `st_press_common_probe()`. SPI ID table includes modern names and legacy aliases.

## Control flow
The SPI core calls probe; the wrapper resolves the correct settings and transport configuration before delegating to the core for WAI verification, channel setup, triggers, buffers, and IIO registration.

## State and persistence behavior
No separate wrapper state exists beyond common `st_sensor_data`. Hardware power and transport configuration are managed through the generic ST layer.

## Dependencies and integration points
It depends on Linux SPI, OF/SPI ID matching, `st_sensors_spi_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`.

## Risks
SPI modalias normalization must preserve compatibility with legacy names. SPI bus mode/multiread behavior is encoded in the settings and generic ST SPI layer, so variant table errors surface as communication failures. Unsupported aliases fail early.

## Test signals
Probe all SPI IDs and OF compatibles, including legacy `lps25h-press` style aliases, inject SPI configure/power failures, and run common ST pressure direct and buffered tests over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/st_pressure_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/t5403.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/t5403.c

## Purpose
`t5403.c` is an I2C IIO driver for the EPCOS T5403 pressure and temperature sensor. It reads factory calibration coefficients, performs compensated pressure/temperature calculations, and exposes pressure integration time selection.

## Important APIs, types, and functions
`struct t5403_data` stores the I2C client, mutex, pressure conversion mode, and ten little-endian coefficients. `t5403_read()` issues temperature or pressure conversion commands and waits according to selected mode. `t5403_comp_pressure()` reads raw temperature and pressure and applies the application-note compensation polynomial. `t5403_comp_temp()` computes milli-Celsius. IIO callbacks expose processed pressure/temp and integration time.

## Control flow
Probe checks SMBus word/block functionality, validates the sensor's I2C address register, allocates IIO state, defaults pressure mode to standard, reads all calibration coefficients, and registers. Runtime pressure reads lock the device, take a temperature conversion, then a pressure conversion at the selected mode, calculate kPa, and unlock. Integration-time writes select one of four pressure conversion modes.

## State and persistence behavior
Calibration coefficients and selected pressure mode are stored in RAM. Mode changes affect later pressure reads but are not written to a persistent register except as part of each conversion command. The driver has no runtime PM and no buffer support.

## Dependencies and integration points
It depends on I2C SMBus word and block transactions, IIO sysfs attributes, mutexes, and little-endian coefficient handling. The module binds to I2C ID `t5403`.

## Risks
Coefficient block length is not checked against the expected full size when positive. Compensation uses chained integer arithmetic that can overflow if altered carelessly. There is no EOC IRQ support despite a TODO, so all reads sleep synchronously. Integration-time writes are locked, but reads of `data->mode` for reporting are not locked.

## Test signals
Validate address register detection, coefficient read failures, known compensation vectors, all integration-time values, unsupported integration times, I2C error propagation, and concurrent read/write stress.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/t5403.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.c

## Purpose
`zpa2326.c` is the shared IIO core for Murata ZPA2326 pressure and temperature sensors. It supports direct one-shot sampling, optional interrupt-assisted completion, internal hardware trigger/continuous sampling, triggered buffers, runtime PM, regulators, regmap validation helpers, and sample-frequency control.

## Important APIs, types, and functions
Register access validators `zpa2326_isreg_writeable/readable/precious()` are exported for bus regmaps. `struct zpa2326_private` stores timestamp, regmap, completion/result, optional trigger, wake flag, IRQ, current frequency, and `vref`/`vdd` regulators. Power helpers enable regulators, reset, sleep, and configure one-shot mode. FIFO helpers clear/dequeue pressure samples. IRQ handlers timestamp data-ready events and complete one-shot waits or poll the internal trigger. `zpa2326_sample_oneshot()`, `zpa2326_trigger_handler()`, buffer setup ops, trigger ops, read/write raw callbacks, and `zpa2326_probe()/remove()` form the core driver.

## Control flow
Bus wrappers provide a regmap, expected hardware ID, IRQ, and name. Core probe allocates IIO state, gets regulators, sets the default highest frequency, installs triggered buffer and optional trigger/IRQ, powers on, verifies device ID, configures one-shot mode, sleeps, initializes runtime PM, and registers. Direct raw reads resume/power the device, configure one-shot if needed, start conversion, wait by polling or IRQ completion, read pressure or temperature, then sleep/autosuspend. With the internal trigger, buffer enable starts continuous sampling at the selected frequency; IRQs drive trigger polling and buffer pushes. With external triggers, the trigger handler performs one-shot sampling per trigger.

## State and persistence behavior
Driver state includes current sampling frequency, IRQ availability, trigger pointer, wake flag, completion result, and regulator/runtime PM state. Hardware state transitions among powered off, enabled, one-shot, continuous, and sleep modes. The FIFO stores pressure only and is explicitly cleared when enabling buffers or after overruns. Removal unregisters IIO, disables runtime PM, sleeps the chip, and powers regulators off.

## Dependencies and integration points
The core exports symbols in namespace `IIO_ZPA2326` and depends on regmap, regulators, runtime PM, completions, IRQs, IIO triggers/buffers/sysfs, and bus-specific I2C/SPI wrappers.

## Risks
Power-state sequencing is complex: register access is limited while asleep, and IRQs can race trigger disable unless interrupts are masked as implemented. FIFO overrun handling intentionally keeps only the newest pressure sample and discards the rest. Continuous-mode frequency only matters when using the internal trigger. Error paths must sleep/power off even with dummy regulators. The `waken` flag is set to a pointer value as a boolean marker, which is unusual but intentional.

## Test signals
Validate register-access tables, regulator enable/disable failures, unexpected ID, runtime PM suspend/resume, direct one-shot with IRQ and polling, timeout paths, internal and external trigger buffering, FIFO overflow/clear, frequency writes for 1/5/11/23 Hz, and I2C/SPI wrapper parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.h

## Purpose
`zpa2326.h` is the private shared header for Murata ZPA2326 core and bus wrappers. It defines the register map, device ID, bit masks, exported regmap validators, common probe/remove APIs, and optional PM ops.

## Important APIs, types, and functions
Register constants cover reference pressure, device ID, resolution/configuration, control registers, interrupt source, thresholds, status, pressure output, and temperature output. `zpa2326_probe()` creates and registers the common IIO device from a parent device, name, IRQ, expected hardware ID, and regmap. `zpa2326_remove()` tears it down. `ZPA2326_PM_OPS` resolves to exported PM ops when `CONFIG_PM` is enabled.

## Control flow
There is no executable flow. I2C and SPI wrappers construct appropriate regmaps using the exported register validators, compute or pass expected hardware ID, and invoke the common probe/remove.

## State and persistence behavior
The header stores no state. It defines the hardware register and bit layout that controls the core's power, sampling, interrupt, and FIFO behavior.

## Dependencies and integration points
It forward-declares `struct device` and `struct regmap` and conditionally includes PM declarations. It is internal to the ZPA2326 driver family.

## Risks
Bit-mask or register changes are high risk because they affect both buses and the core's power/IRQ/FIFO sequencing. The PM macro must match bus driver expectations across `CONFIG_PM` builds.

## Test signals
Compile with I2C and SPI wrappers, with and without PM, and validate regmap readable/writeable/precious coverage against the datasheet and core access patterns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_i2c.c

## Purpose
`zpa2326_i2c.c` is the I2C bus wrapper for the Murata ZPA2326 pressure/temperature sensor. It creates an I2C regmap with the device's read flag semantics and delegates all IIO behavior to the common core.

## Important APIs, types, and functions
`zpa2326_regmap_i2c_config` uses 8-bit registers/values, shared readable/writeable/precious callbacks, max register `TEMP_OUT_H`, and `read_flag_mask = BIT(7)`. `zpa2326_i2c_hwid()` computes the expected ID because device ID bit 1 mirrors I2C address bit 0. Probe initializes regmap and calls `zpa2326_probe()`. Remove calls `zpa2326_remove()`.

## Control flow
The I2C core binds by `murata,zpa2326` or I2C ID, probe creates regmap, computes expected hardware ID from the client address, and hands control to the common driver. PM ops are supplied by the common core through `ZPA2326_PM_OPS`.

## State and persistence behavior
No wrapper-local runtime state is kept. Regmap and common IIO state are devm/core-managed.

## Dependencies and integration points
It depends on Linux I2C, regmap, OF/I2C ID tables, and namespace `IIO_ZPA2326`.

## Risks
The address-dependent ID check is unique to I2C and must match hardware strap behavior. Regmap read-flag configuration is critical; wrong flags make all reads fail or access wrong registers. Remove assumes common probe stored the IIO device as driver data.

## Test signals
Probe at both possible I2C addresses, verify expected ID bit handling, inject regmap init failure, test PM suspend/resume via bus driver, and run common direct/buffered tests over I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c

## Purpose
`zpa2326_spi.c` is the SPI bus wrapper for Murata ZPA2326 sensors. It configures SPI register access and bus timing, then delegates core IIO behavior to `zpa2326_probe()`.

## Important APIs, types, and functions
`zpa2326_regmap_spi_config` defines 8-bit reg/val access, shared register validators, max register, and read flags for read plus address auto-increment (`BIT(7) | BIT(6)`). `zpa2326_probe_spi()` initializes regmap, forces SPI mode 3, caps speed at 1 MHz, runs `spi_setup()`, and calls the common probe with fixed `ZPA2326_DEVICE_ID`. Remove calls `zpa2326_remove()`.

## Control flow
The SPI core probes, regmap is created, SPI electrical settings are enforced, and the common core powers, validates, configures, and registers the IIO device. PM ops come from the shared core.

## State and persistence behavior
No wrapper-specific state persists beyond the SPI configuration and regmap. The common core owns all sensor runtime state.

## Dependencies and integration points
It depends on Linux SPI, regmap, OF/SPI ID matching for `murata,zpa2326`, and namespace `IIO_ZPA2326`.

## Risks
Forcing mode/speed can fail if controller constraints or firmware conflict. The read flag includes auto-increment, which is necessary for bulk pressure/temp reads but must be correct for single reads too. Remove assumes successful common driver-data setup.

## Test signals
Verify mode 3 and 1 MHz cap, regmap reads/writes including bulk reads, probe ID mismatch, PM paths, and common one-shot/triggered-buffer behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/zpa2326_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig

## Purpose
`drivers/iio/proximity/Kconfig` defines configuration entries for IIO lightning, proximity, distance, PIR, SAR, time-of-flight, ultrasonic, and ChromeOS EC proximity drivers. It controls which source files are built and which framework dependencies are selected.

## Important APIs, types, and functions
The file contains Kconfig symbols such as `AS3935`, `CROS_EC_MKBP_PROXIMITY`, `D3323AA`, `HX9023S`, `IRSD200`, `ISL29501`, `LIDAR_LITE_V2`, `MB1232`, `PING`, `RFD77402`, `SRF04`, `SX_COMMON`, `SX9310`, `SX9324`, `SX9360`, `SX9500`, and `SRF08` in the read portion. Entries use `tristate`, `depends on`, `select`, and help text to express build and subsystem requirements.

## Control flow
Kconfig is declarative. The menu first groups the AS3935 lightning sensor under a lightning menu, then groups proximity/distance sensors. User or defconfig choices propagate dependencies to the build system and module list.

## State and persistence behavior
The selected symbols persist in the kernel `.config`, not at runtime. Hidden helper symbol `SX_COMMON` is selected by Semtech drivers.

## Dependencies and integration points
It integrates with the kernel Kconfig system, IIO buffer/trigger options, bus dependencies such as I2C/SPI/GPIOLIB, regmap selections, and ChromeOS EC dependencies. The corresponding `Makefile` uses these symbols to compile objects.

## Risks
Missing `select` lines cause link/build failures for drivers that use triggered buffers or regmap. Overly broad `select`s can force unwanted subsystems. Entries must stay synchronized with source files and Makefile object names.

## Test signals
Run Kconfig builds for each symbol as built-in and module, randconfig coverage for dependency edges, and verify every enabled symbol has a matching Makefile object and required helper selects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile

## Purpose
`drivers/iio/proximity/Makefile` maps proximity-related Kconfig symbols to the object files built by kbuild.

## Important APIs, types, and functions
Each `obj-$(CONFIG_...) += ...o` line ties a configuration symbol to a driver object. Entries include `as3935.o`, `cros_ec_mkbp_proximity.o`, `d3323aa.o`, `hx9023s.o`, `irsd200.o`, `isl29501.o`, `pulsedlight-lidar-lite-v2.o`, `mb1232.o`, `ping.o`, `rfd77402.o`, `srf04.o`, `srf08.o`, Semtech SX objects, `vcnl3020.o`, VL53Lx objects, and `aw96103.o`.

## Control flow
kbuild evaluates each line according to the final `.config`. Enabled built-in symbols add objects to the built-in archive; module symbols build loadable modules.

## State and persistence behavior
The file has no runtime state. Build outputs depend on `.config` state.

## Dependencies and integration points
It integrates with Kconfig symbols in the same directory and with source filenames. The comment asks maintainers to keep entries alphabetically ordered, although `AW96103` appears at the end.

## Risks
Symbol/object mismatches cause missing modules or build failures. Ordering comments can drift from reality. Adding a Kconfig entry without a Makefile line silently prevents compilation.

## Test signals
Build each symbol as `m` and `y`, run `make drivers/iio/proximity/`, and compare Kconfig symbols against Makefile entries for one-to-one coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/as3935.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/as3935.c

## Purpose
`as3935.c` is an SPI IIO driver for the AS3935 Franklin lightning sensor. It exposes estimated lightning distance as proximity data, provides sensitivity/noise attributes, uses an IRQ-delayed work path to classify events, and supports triggered buffers.

## Important APIs, types, and functions
`struct as3935_state` stores SPI device, IIO trigger, mutex, delayed work, last noise timestamp, tuning capacitor, noise floor register, scan buffer, and SPI buffer. `as3935_read()` and `as3935_write()` implement 2-byte SPI register access. Sysfs attributes expose `sensor_sensitivity` and recent `noise_level_tripped`. `as3935_read_raw()` returns raw or processed distance and scale. `as3935_event_work()` reads the interrupt cause after a delay, polling the trigger on lightning events or recording noise/disturber state. PM ops power down/up and recalibrate. `calibrate_as3935()` restores defaults, calibration, tuning capacitor, and noise floor.

## Control flow
Probe requires an IRQ, allocates IIO state, reads firmware properties `ams,tuning-capacitor-pf` and `ams,nflwdth`, creates an IIO trigger and triggered buffer, calibrates the chip, installs delayed work and IRQ handler, and registers IIO. Hardware interrupts schedule delayed work after about 3 ms so distance is updated. A lightning event polls the trigger; the trigger handler reads distance data and pushes it with a timestamp.

## State and persistence behavior
Driver state includes `noise_tripped` for a one-second sysfs indication, configured tuning capacitor/noise floor, and the trigger/work objects. Suspend sets the AFE power bit; resume clears it and recalibrates. Device register configuration persists until reset or recalibration.

## Dependencies and integration points
It depends on SPI, devm delayed work helpers, IRQs, IIO triggers/buffers, firmware properties, and PM sleep ops. OF compatible is `ams,as3935`.

## Risks
IRQ is mandatory, so polling-only deployments cannot use the driver. Sensor sensitivity writes overwrite the whole AFE register with `val << 1`, so preserving unrelated bits requires care. Event work ignores unknown interrupt causes. Tuning capacitor and noise floor property validation protect only upper bounds, not board-quality calibration.

## Test signals
Probe without IRQ, validate property bounds, exercise sensitivity and noise sysfs, simulate event/noise/disturber IRQ causes, verify delayed trigger push, suspend/resume recalibration, and SPI transfer error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/as3935.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/aw96103.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/aw96103.c

## Purpose
`aw96103.c` is an I2C/regmap IIO driver for Awinic AW96103/AW96105 capacitive SAR proximity sensors. It supports multiple proximity channels, raw differential readings, threshold/debounce/hysteresis event attributes, IRQ-driven proximity events, regulator power, reset/init sequencing, and asynchronous firmware or built-in register configuration loading.

## Important APIs, types, and functions
`struct aw96103` stores host IRQ enable mask, regmap, device, per-channel used/old-status state, max channel count, and enabled-channel mask. `struct aw_bin` describes parsed firmware configuration. Channel tables expose four AW96103 or six AW96105 proximity channels. `aw96103_read_raw()` reads per-channel diff registers scaled by 1024. Event callbacks read/write threshold, rising/falling debounce, hysteresis, and enable bits. Firmware helpers parse `aw96103_0.bin`, write register/value pairs, skip EEPROM-like registers, capture IRQ and scan masks, apply AW96103A compatibility fixups, and fall back to a large built-in default table. IRQ code decodes four threshold state bits per channel and pushes rising/falling IIO threshold events.

## Control flow
Probe allocates IIO state, gets chip info from match data, initializes a 16-bit/32-bit regmap, enables `vcc`, retries chip-ID read, soft-resets, waits for init-complete IRQ status, requests firmware asynchronously, initializes IRQ masking/handler, sets IIO channels/info/name, and registers. Firmware callback loads configuration or defaults, starts active scanning, enables host IRQs, and marks channels used according to `SCANCTRL0`.

## State and persistence behavior
Mutable state includes active channel flags, previous IRQ status per channel, host IRQ mask, and channel-enable mask from firmware/defaults. Threshold, debounce, hysteresis, scan enable, mode, and IRQ registers persist in hardware until reset. Because firmware loading is asynchronous, initial IIO registration can race with late configuration availability.

## Dependencies and integration points
It depends on I2C, regmap, regulators, firmware loading, IRQs, IIO events, unaligned little-endian parsing, and OF/I2C match data for AW96103/AW96105.

## Risks
Firmware parsing trusts offsets/length fields from the binary enough to iterate register records; malformed firmware can cause bad configuration attempts. `request_firmware_nowait()` means userspace may observe a device before configuration is loaded. The IRQ handler reads `IRQSRC` but does not use it beyond acknowledgement. Event enable writes immediately toggle scan bits and local `used` flags without locking. Unexpected chip IDs are logged but not rejected.

## Test signals
Test AW96103 and AW96105 channel counts, chip-ID retry/mismatch, reset/init timeout, firmware success/failure/default fallback, malformed firmware lengths, raw diff reads, threshold/debounce/hysteresis read/write, event enable toggles, IRQ status transitions, and regulator/regmap error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/aw96103.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c

## Purpose
`cros_ec_mkbp_proximity.c` is a platform IIO driver exposing the ChromeOS EC MKBP front-proximity switch as a proximity channel with optional threshold events.

## Important APIs, types, and functions
`struct cros_ec_mkbp_proximity_data` stores the EC pointer, IIO device, mutex, notifier block, last state, and event-enable flag. `cros_ec_mkbp_proximity_query()` sends `EC_CMD_MKBP_INFO` version 1 to fetch current switch state. `cros_ec_mkbp_proximity_parse_state()` extracts `EC_MKBP_FRONT_PROXIMITY`. `cros_ec_mkbp_proximity_push_event()` compares state changes and emits IIO threshold events when enabled. Notifier, read_raw, event config, resume, probe, and remove functions wire the driver into ChromeOS EC event delivery.

## Control flow
Probe obtains the parent `cros_ec_device`, allocates an IIO device, initializes `last_proximity` to unknown, registers IIO, and registers a blocking notifier on the EC event chain. Raw reads query the EC synchronously. MKBP switch notifications parse the event payload and push events on state changes. Resume queries current state and pushes an event if the state changed while suspended.

## State and persistence behavior
Runtime state is `last_proximity` and `enabled`, protected by a mutex. No hardware configuration is persisted by this driver; event enable only controls whether IIO events are emitted locally.

## Dependencies and integration points
It depends on ChromeOS EC command/protocol headers, platform devices, blocking notifier chains, IIO events/sysfs, and unaligned little-endian parsing. OF compatible is `google,cros-ec-mkbp-proximity`.

## Risks
Notifier registration is manual rather than devm-managed, making remove cleanup essential. Event direction maps proximity present to falling and absent to rising, which tests must preserve. If the IIO clock is not boottime, EC event timestamps are replaced with local IIO timestamps. Query size mismatches return `-EPROTO`.

## Test signals
Test EC query success, transport failures and wrong response sizes, notifier switch events, enable/disable event config, duplicate-state suppression, resume state reconciliation, timestamp mode behavior, and remove unregistering the notifier.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/cros_ec_mkbp_proximity.c -->
