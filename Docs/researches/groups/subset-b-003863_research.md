# subset-b-003863 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-core.c

Purpose: shared Bosch BMC150/BMA2xx/BMI055 accelerometer core for the IIO subsystem. Bus-specific modules pass a `regmap`, IRQ, device type hint, optional name, and block-read capability into `bmc150_accel_core_probe()`, while this file owns chip reset/probing, channel tables, scale/sample-frequency handling, runtime PM, triggered buffers, hardware FIFO, mount matrix support, and rate-of-change motion events.

Important APIs, types, and functions: exports `bmc150_regmap_conf`, `bmc150_accel_core_probe()`, `bmc150_accel_core_remove()`, and `bmc150_accel_pm_ops` in namespace `IIO_BMC150`. It uses `struct bmc150_accel_data` from the header, local `struct bmc150_accel_chip_info` and `struct bmc150_scale_info`, IIO `read_raw`/`write_raw`/event callbacks, `iio_triggered_buffer_setup_ext()`, `devm_request_threaded_irq()`, regulator bulk APIs, PM-runtime APIs, and regmap reads/writes. Key helpers include `bmc150_accel_chip_init()`, `bmc150_accel_set_mode()`, `bmc150_accel_set_bw()`, `bmc150_accel_set_scale()`, `bmc150_accel_get_axis()`, `bmc150_accel_set_interrupt()`, trigger setup/reenable helpers, and FIFO flush/transfer helpers.

Control flow: probe allocates an IIO device, reads ACPI or firmware mount orientation, enables `vdd`/`vddio`, resets the chip, verifies chip ID, selects chip-specific channels and scale table, configures default normal mode, 125 Hz bandwidth, 4g range, slope event defaults, and latched interrupts. It then installs triggered buffer support, optionally requests a threaded IRQ, maps INT1/INT2 interrupt roles, registers IIO triggers, enables PM runtime with autosuspend, and registers the IIO device. Direct reads power the device through runtime PM, bulk-read little-endian axis registers, sign-extend according to per-chip realbits, and refuse direct accel reads when the IIO buffer is enabled. Triggered-buffer mode reads a 3-axis frame on data-ready. FIFO mode programs watermark interrupt and FIFO registers, flushes count-tagged samples from `BMC150_ACCEL_REG_FIFO_DATA`, demuxes active channels, and reconstructs timestamps from successive interrupt or flush timestamps.

State and persistence: persistent driver state lives in `struct bmc150_accel_data`: cached bandwidth bits, range register value, slope threshold/duration, event enable flag, watermark/FIFO mode, interrupt user atomics, trigger enabled flags, timestamp pair, mount matrix, regulators, and optional ACPI second-device/resume callback. Hardware configuration persists in sensor registers and is restored by runtime/system resume paths where needed. Remove unregisters the IIO device, disables runtime PM, unregisters triggers, cleans up buffers, puts the chip in deep suspend, and disables regulators.

Dependencies and integration points: Linux IIO core, IIO events/triggers/buffers/sysfs, regmap, regulators, ACPI/property mount matrices, PM runtime, IRQ framework, and the BMC150 I2C/SPI wrappers. ACPI integration handles BOSC0200/DUAL250E orientation and labels. Risks include interrupt reference-count imbalance on failed enable/disable, timestamp approximation jitter in FIFO mode, board descriptions that omit correct INT names, firmware with misleading ACPI IDs, and register updates that must happen while synchronized by `data->mutex`. Test signals include successful chip ID detection, sysfs raw/scale/sample-frequency values, unavailable direct reads while buffering, trigger registration, FIFO watermark flush behavior, event enable/value paths, runtime suspend/resume transitions, regulator cleanup, and ACPI mount matrix/dual-accelerometer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-i2c.c

Purpose: I2C transport wrapper for the BMC150-family core. It creates an I2C regmap, determines the name/type hint from the I2C ID table when available, detects whether block reads are supported, and delegates all sensor behavior to `bmc150_accel_core_probe()`.

Important APIs and flow: `bmc150_accel_probe()` calls `devm_regmap_init_i2c()`, computes `block_supported` from adapter functionality, passes `client->irq` and metadata into the core, and then optionally instantiates ACPI dual-accelerometer children for BOSC0200/DUAL250E style devices when probe was not matched by a normal I2C ID. `bmc150_accel_remove()` removes any ACPI-created second client before calling the core remove routine. The driver publishes I2C, ACPI, and OF match tables and imports namespace `IIO_BMC150`.

State, dependencies, and risks: persistent bus-specific state is mostly ACPI child-device state stored inside the core `bmc150_accel_data`, including `second_device`, delayed resume work, and the resume callback. The DUAL250E path calls an ACPI DSM to force keyboard/touchpad reenable after boot or resume and schedules delayed work from the core resume callback. Risks are firmware-specific: duplicate BOSC0200 IDs can belong to other Bosch chips and rely on the core chip-ID rejection path, ACPI DSM calls intentionally use a raw buffer despite warning-prone firmware expectations, and child-client creation must avoid recursive duplicate setup. Test signals include I2C regmap creation, ID/OF/ACPI matching, block-read capability toggling FIFO support, dual-client creation/removal, delayed resume work cancellation, and proper handoff to core PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-spi.c

Purpose: SPI transport wrapper for BMC150-family accelerometers. It initializes a SPI regmap using the shared BMC150 regmap config and delegates probe/remove/PM behavior to the core.

Important APIs and flow: `bmc150_accel_probe()` obtains the SPI device ID when present, derives optional name and `enum bmc150_type`, initializes `devm_regmap_init_spi()`, then calls `bmc150_accel_core_probe(&spi->dev, regmap, spi->irq, type, name, true)`. The SPI wrapper always declares block/FIFO-style reads supported. Remove calls `bmc150_accel_core_remove()`. It provides ACPI and SPI ID tables and binds the core PM ops in `struct spi_driver`.

State, dependencies, risks, and tests: all meaningful sensor state belongs to the core, while this file owns only bus binding and match metadata. It depends on SPI, regmap, module SPI registration, ACPI matching, and namespace import `IIO_BMC150`. Risks are limited to incorrect ID driver data, regmap setup failure, and SPI boards without an IRQ losing trigger/event/FIFO interrupt features. Test signals are module autoload from SPI/ACPI IDs, regmap initialization, core probe success, IRQ propagation, and core remove on driver unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel.h

Purpose: shared interface and private state contract between the BMC150 core and its I2C/SPI transport modules. It declares exported core entry points, PM ops, the regmap config, chip type hints, interrupt/trigger IDs, and the core state structure.

Important types: `enum bmc150_type` currently distinguishes unknown chips from `BOSCH_BMC156` when the board ID can be trusted. `struct bmc150_accel_interrupt` stores per-interrupt mapping plus an atomic user count. `struct bmc150_accel_trigger` links an IIO trigger to the shared data, setup callback, interrupt ID, and enabled state. `struct bmc150_accel_data` holds the regmap, IRQ, regulators, trigger and interrupt arrays, mutex, FIFO mode/watermark, direct-read and scan buffers, bandwidth/range/event settings, timestamp pair, chip info pointer, optional ACPI second I2C client/resume work, and mount matrix.

Integration and risks: the header exposes a stable namespace boundary for bus modules and makes the bus files dependent on IIO core, regulator descriptors, mutexes, atomics, and workqueues. Because transport files store ACPI child-device state in `bmc150_accel_data`, changes to this structure can affect both normal core behavior and I2C-specific resume handling. Test signals are successful compilation of both transports, namespace imports, PM op linkage, and correct layout/alignment for scan buffers with timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmc150-accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-core.c

Purpose: shared IIO core for Bosch BMI085/BMI088/BMI090L accelerometer functions. It is a simpler direct-mode accelerometer/temperature driver than BMC150: it does not implement FIFO or triggers here, but it handles chip reset/ID validation, scale and sample-frequency controls, raw axis/temp reads, regcache, and runtime PM power sequencing.

Important APIs and flow: exports `bmi088_regmap_conf`, `bmi088_accel_core_probe()`, `bmi088_accel_core_remove()`, and runtime PM ops in namespace `IIO_BMI088`. The regmap config marks volatile low registers and reset as volatile and uses `REGCACHE_MAPLE`. Probe allocates `struct bmi088_accel_data`, calls `bmi088_accel_chip_init()` which performs dummy reads needed for SPI, resets the chip, reads `WHO_AM_I`, selects chip info and scale table, then registers an IIO direct-mode device. `read_raw` powers up with `pm_runtime_resume_and_get()`, reads temp or axis registers, applies temp offset/scale or selected accel range scale, and puts the device back to autosuspend. `write_raw` validates scale/sample-frequency choices and updates `ACC_RANGE` or ODR bits.

State, dependencies, risks, and tests: persistent state is only regmap, selected chip info, and an aligned 2-byte transfer buffer. Hardware power state is controlled through `PWR_CTRL` and `PWR_CONF`; runtime suspend/resume performs the datasheet delay sequence. The chip-ID logic falls back to the requested type if the ID is not in the table, while warning when the requested type differs from the detected index; this is tolerant but can hide board-description errors. Other risks include sample frequency setter accepting integer Hz only, no direct mutex around the shared buffer beyond IIO direct claims, and PM failures during sysfs access. Test signals include I2C and SPI dummy-read compatibility, chip ID warnings, direct raw reads, scale/sample frequency available lists, autosuspend delay behavior, and clean power-down on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-i2c.c

Purpose: I2C wrapper for BMI085/BMI088/BMI090L accelerometer core. It only handles bus regmap creation, match tables, and delegation to the shared core.

Important APIs and flow: `bmi088_accel_probe()` reads the I2C ID table entry with `i2c_client_get_device_id()`, initializes `devm_regmap_init_i2c()` with `bmi088_regmap_conf`, then calls `bmi088_accel_core_probe(&i2c->dev, regmap, i2c->irq, id->driver_data)`. Remove calls `bmi088_accel_core_remove()`. OF compatibles and I2C IDs map the supported chip names to `enum bmi_device_type`, and the driver attaches `bmi088_accel_pm_ops`.

State, dependencies, risks, and tests: no bus-local persistent state is stored. Dependencies are I2C, regmap, OF matching, PM ops, and namespace `IIO_BMI088`. Risk is mostly match-data correctness; unlike OF entries, the probe assumes an I2C ID is present and uses its driver data. Test signals include module autoload from I2C/OF IDs, regmap creation failure path, core chip-ID validation, runtime PM callback linkage, and remove power-down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-spi.c

Purpose: SPI wrapper for BMI085/BMI088/BMI090L accelerometer core, including the custom SPI read behavior required by the chip protocol.

Important APIs and flow: implements a `struct regmap_bus` with `bmi088_regmap_spi_write()` and `bmi088_regmap_spi_read()`. Writes use `spi_write()`. Reads set bit 7 in the register address and insert a dummy byte before reading the value payload. Probe creates the regmap with `devm_regmap_init()`, passes SPI IRQ and ID driver data to `bmi088_accel_core_probe()`, and remove delegates to the core. OF and SPI ID tables cover the three chip variants.

State, dependencies, risks, and tests: the bus wrapper stores no persistent state, but the custom regmap bus is critical because generic SPI register reads would not satisfy the dummy-byte protocol. It depends on SPI, regmap, OF matching, PM ops, and namespace `IIO_BMI088`. Risks include read framing errors, incorrect ID match data, and absent IRQ being unused by this core today but still passed through. Test signals are regmap bus read/write transactions on SPI, dummy-read compatibility with core init, chip-ID reads after reset, and runtime PM callbacks through the SPI driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel.h

Purpose: public internal header connecting BMI088-family bus wrappers to the shared accelerometer core. It declares the chip type enum, shared regmap config, PM ops, and core probe/remove routines.

Important contract: `enum bmi_device_type` has `BOSCH_BMI085`, `BOSCH_BMI088`, `BOSCH_BMI090L`, and `BOSCH_UNKNOWN`; the bus wrappers pass these values from ID tables to the core. The exported functions accept a `struct device`, `struct regmap`, IRQ, and type. PM ops are exported so wrappers can bind the same runtime suspend/resume behavior.

Integration and risks: this header is the namespace boundary for `IIO_BMI088`. A mismatch between enum order and the core chip-info table would select wrong scale/name defaults, so ID table changes should be reviewed with the core table. Test signals include compilation of both wrappers, namespace imports, correct ID-to-type mapping, and PM op linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bmi088-accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/cros_ec_accel_legacy.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/cros_ec_accel_legacy.c

Purpose: platform IIO driver for older Chrome OS EC accelerometer exposure. It uses the Chrome EC memory-mapped or legacy host-command interface rather than a sensor-specific I2C/SPI register map and presents accelerometer channels through IIO sysfs and triggered buffers supplied by the common cros-ec sensors core.

Important APIs and flow: `cros_ec_accel_legacy_probe()` allocates an IIO device, calls `cros_ec_sensors_core_init()`, chooses `cros_ec_sensors_read_lpc` when EC readmem exists or `cros_ec_accel_legacy_read_cmd()` otherwise, configures legacy accel channels, adjusts display-lid signs, and registers through `cros_ec_sensors_core_register()`. `cros_ec_accel_legacy_read_cmd()` sends `MOTIONSENSE_CMD_DUMP`, preserves `sensor_num`, and copies selected axes with sign correction. `read_raw` handles raw, fixed scale, fake calibration bias, and fixed 10 Hz sample frequency, delegating other masks to `cros_ec_sensors_core_read()`. `write_raw` accepts calibration-bias writes as no-ops for script compatibility.

State, dependencies, risks, and tests: state lives in `struct cros_ec_sensors_core_state`, including command lock, EC command buffers, sign array, sensor metadata, and common attributes. Dependencies are platform device registration, Chrome EC commands/proto, cros-ec sensors core, IIO buffers, and kfifo/trigger helpers. Risks include legacy assumptions of only two sensors in dump responses, fixed 10 Hz/10-bit-per-g scaling, axis remapping/inversion required for HTML5 convention, and no real calibration storage. Test signals are raw reads through both LPC and command paths, locked command access, lid label sign inversion, fixed scale/sample-frequency sysfs values, no-op calibration writes, and platform alias autoload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/cros_ec_accel_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/da280.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/da280.c

Purpose: simple direct-mode I2C IIO driver for MiraMEMS DA217/DA226/DA280 accelerometers. It exposes raw X/Y/Z data, with DA226 using only two channels, and a fixed acceleration scale.

Important APIs and flow: probe reads `DA280_REG_CHIP_ID`, validates `DA280_CHIP_ID`, gets match data for name and channel count, allocates an IIO device, enables the sensor by writing `DA280_REG_MODE_BW`, installs a devm cleanup action to disable it, and registers the IIO device. `da280_read_raw()` reads a word from the channel address, treats the 14-bit value as a 16-bit word with low two bits unused, sign-shifts it, and returns fixed nanometer-scale data. System sleep PM calls `da280_enable(false/true)`.

State, dependencies, risks, and tests: persistent state is only the I2C client pointer plus match-data selected channel count/name. Dependencies are I2C SMBus word and byte operations, ACPI/I2C ID matching, and IIO direct mode. Risks include endianness assumptions around `i2c_smbus_read_word_data()`, the single chip ID shared across variants, missing match data causing probe rejection, and no runtime PM or buffering. Test signals include chip-ID rejection, DA226 two-channel registration, raw sign extension, fixed scale value, suspend/resume enable writes, and devm disable on probe failure/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/da280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/da311.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/da311.c

Purpose: direct-mode I2C IIO driver for the MiraMEMS DA311 3-axis accelerometer. It performs a vendor-derived initialization sequence across banked registers, exposes raw acceleration, and supports simple system sleep power toggling.

Important APIs and flow: `da311_probe()` validates the chip ID, allocates state, initializes IIO metadata, calls `da311_reset()`, enables measurement, installs `da311_disable()` as cleanup, and registers the IIO device. `da311_register_mask_write()` handles bank selection for addresses above 0xff, optional read-modify-write masking, write to low 8-bit address, and return to bank 0. `da311_reset()` performs soft reset and writes a static initialization table. `da311_read_raw()` reads channel words, shifts 12-bit data out of 16-bit storage, and returns fixed scale.

State, dependencies, risks, and tests: persistent state is the I2C client pointer; the hardware state is initialized from the static register table and the enable bit in `TEMP_CFG_REG`. Dependencies are SMBus byte/word operations and IIO direct mode. Risks include fragile bank switching if an error leaves the chip in bank 1, vendor magic constants that need hardware validation, endian/sign assumptions in word reads, and no buffer/interrupt path. Test signals include chip-ID match, reset sequence success, banked register writes returning to bank 0, raw axis sign extension, fixed scale, system suspend/resume, and devm cleanup disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/da311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard06.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/dmard06.c

Purpose: direct-mode I2C IIO driver for Domintech DMARD05/DMARD06/DMARD07 accelerometers with a temperature channel. It validates chip IDs, exposes byte-sized axis and temperature reads, and supports system sleep powerdown/normal modes.

Important APIs and flow: probe checks full I2C functionality, allocates the IIO device, reads `DMARD06_CHIP_ID_REG`, validates one of three IDs, stores the chip ID, sets channel metadata, and registers via devm. `dmard06_read_raw()` reads a byte from the channel address, sign-extends bit 7, applies chip-specific shifts or halves, returns accel scale depending on chip generation, and returns a fixed temperature offset. PM suspend writes `DMARD06_MODE_POWERDOWN`; resume writes `DMARD06_MODE_NORMAL`.

State, dependencies, risks, and tests: state contains the I2C client and chip ID. Dependencies are I2C SMBus byte operations, OF/I2C matching, and IIO direct mode. Risks include very compact 8-bit data precision, chip-specific scaling branches that must match hardware, probe not explicitly setting normal mode before first read, and no runtime PM or buffering. Test signals are chip ID validation for all three IDs, raw axis/temp sysfs reads, scale/offset values, suspend/resume register writes, and OF/I2C module matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard09.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/dmard09.c

Purpose: minimal I2C IIO driver for the Domintech DMARD09 3-axis accelerometer. It validates the chip ID and exposes direct raw axis reads through a required block-read sequence.

Important APIs and flow: probe allocates state, reads `DMARD09_REG_CHIPID`, rejects non-`0x95` devices, sets direct-mode IIO channels, and registers the device. `dmard09_read_raw()` reads an 8-byte block starting at `DMARD09_REG_STAT` because individual axis registers are cached/stale, extracts little-endian axis data at per-channel offsets, drops lower three bits by shifting, sign-extends, and returns integer raw values.

State, dependencies, risks, and tests: state is just the I2C client pointer. Dependencies are I2C block read support, unaligned little-endian helpers, and IIO direct mode. The channel spec advertises scale but `read_raw` only implements raw, so scale reads return `-EINVAL`; that is a visible behavioral gap. Other risks are missing PM handling, reliance on block read from status, and no OF/ACPI table. Test signals include chip ID rejection, full block-read raw extraction for all axes, behavior of scale sysfs if exposed, and module autoload from I2C ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard09.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard10.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/dmard10.c

Purpose: direct-mode I2C IIO driver for Domintech ARD10/DMARD10 accelerometer. It performs a multi-step reset/OTP/configuration sequence, exposes raw acceleration and fixed scale, and shuts the chip down on cleanup or suspend.

Important APIs and flow: probe validates two power-on reset marker registers (`STADR` and `STAINT`), allocates an IIO device, calls `dmard10_reset()`, installs `dmard10_shutdown_cleanup()`, and registers. `dmard10_reset()` writes power reset, a multi-byte ACTR mode sequence, oscillator enable, AFE/clock/interrupt/tap parameters, and active mode. `dmard10_read_raw()` reads 8 bytes from `DMARD10_REG_STADR` because individual axes read as zero, selects a 16-bit little-endian slot, sign-extends bit 12, and returns fixed nanoscale. Suspend uses `dmard10_shutdown()`; resume reruns reset.

State, dependencies, risks, and tests: persistent state is the I2C client pointer. Dependencies are SMBus byte/block operations, raw `i2c_master_send()` sequences, and IIO direct mode. Risks include vendor magic initialization, no chip ID beyond reset marker values, interpreting shutdown `i2c_master_send()` byte count as success even if partial positive counts occur, and no buffering/runtime PM. Test signals include marker register validation, reset sequence success, raw reads from the block path, fixed scale, cleanup shutdown, and suspend/resume reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/dmard10.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-core.c

Purpose: shared IIO core for NXP FXLS8962AF/FXLS8964AF/FXLS8967AF/FXLS8974CF accelerometers. It handles chip identification, mount matrix, regulator enable, runtime PM, raw accel/temp reads, scale and ODR controls, threshold events, interrupt routing, wakeup integration, and hardware FIFO buffering.

Important APIs, types, and functions: exports `fxls8962af_i2c_regmap_conf`, `fxls8962af_spi_regmap_conf`, `fxls8962af_core_probe()`, and `fxls8962af_pm_ops` in namespace `IIO_FXLS8962AF`. `struct fxls8962af_data` holds regmap, selected chip info, scan buffer, timestamps, orientation, IRQ, watermark, event mask, and threshold values. Key helpers include `fxls8962af_reset()`, `fxls8962af_active()/standby()`, `fxls8962af_update_config()`, scale/ODR setters and readers, event threshold/config helpers, FIFO mode/transfer/flush helpers, `fxls8962af_irq_setup()`, and system/runtime PM callbacks.

Control flow: probe allocates an IIO device, reads mount matrix, enables `vdd`, reads `WHO_AM_I`, selects chip info, resets the chip and waits for boot status, optionally configures IRQ polarity/pin/open-drain properties and a kfifo buffer, enables runtime PM autosuspend, optionally enables wakeup, and registers the IIO device. Raw reads temporarily power the chip if inactive, read temp or accel registers, and sign-extend by channel realbits. Configuration changes use standby-active sequencing because several control registers cannot be changed while active. Buffer enable powers the chip, disables active mode, enables buffer interrupt, sets FIFO watermark/mode, and reactivates. IRQ handling reads interrupt status and dispatches either FIFO flush or threshold-event reporting.

State, dependencies, risks, and tests: persistent state is mostly in `fxls8962af_data`; thresholds are cached and mirrored in hardware, event enable bits keep the device powered when needed, timestamps are reconstructed during FIFO flush, and runtime/system PM toggles active/standby rather than regulator state. Dependencies are regmap, regulators, device properties, IRQ trigger type, IIO buffers/events, PM runtime, and I2C/SPI wrappers. Risks include correct active/standby sequencing, small FIFO overflow, timestamp approximation, `wakeup-source` interactions disabling buffer during suspend, I2C errata E3 requiring per-sample reads for FXLS8962AF, and event reporting code that maps Y/Z threshold events to `IIO_MOD_X` in the visible source. Test signals include WHO_AM_I matching, reset boot poll, scale/ODR available lists, direct read while inactive, threshold read/write and enable/disable, IRQ polarity/open-drain setup, FIFO watermark flush including overflow, I2C errata path, wakeup suspend/resume, and runtime autosuspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-i2c.c

Purpose: I2C transport wrapper for NXP FXLS8962AF-family accelerometers. It sets up I2C regmap access and delegates all behavior to the shared core.

Important APIs and flow: `fxls8962af_probe()` initializes `devm_regmap_init_i2c()` with `fxls8962af_i2c_regmap_conf` and calls `fxls8962af_core_probe(&client->dev, regmap, client->irq)`. The I2C ID table includes four enum values, while the OF table lists `nxp,fxls8962af` and `nxp,fxls8964af`. PM ops are imported from the core.

State, dependencies, risks, and tests: this file has no local persistent state. Dependencies are I2C, regmap, OF/I2C matching, and namespace `IIO_FXLS8962AF`. Core chip identification, not ID driver data, decides the exact variant, so table enum values are currently used for module metadata rather than passed to probe. Risks include OF coverage lagging the I2C ID table and I2C-specific FIFO erratum behavior depending on `i2c_verify_client()` in the core. Test signals include regmap creation, module autoload from I2C/OF IDs, IRQ propagation, core WHO_AM_I matching, and PM callback linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-spi.c

Purpose: SPI transport wrapper for NXP FXLS8962AF-family accelerometers. It creates the SPI regmap and hands the device to the common core.

Important APIs and flow: `fxls8962af_probe()` calls `devm_regmap_init_spi()` with `fxls8962af_spi_regmap_conf`, which uses 8 register bits, 8 pad bits, and 8 value bits, then calls `fxls8962af_core_probe(&spi->dev, regmap, spi->irq)`. The driver publishes OF and SPI ID tables for FXLS8962AF/FXLS8964AF and attaches core PM ops.

State, dependencies, risks, and tests: no SPI-local state is stored after probe; the core owns lifecycle and IIO behavior. Dependencies are SPI, regmap, OF/SPI matching, PM, and namespace `IIO_FXLS8962AF`. Risks are mainly protocol framing through `pad_bits`, ID-table coverage that omits newer variants present in the core/I2C table, and absent IRQ limiting event/FIFO support. Test signals include SPI regmap read/write framing, WHO_AM_I matching, IRQ propagation, core buffer/event behavior on SPI, and module autoload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af.h

Purpose: internal shared header for FXLS8962AF-family bus wrappers and core. It defines variant enum constants and declares exported core probe, PM ops, and bus-specific regmap configs.

Important contract: the anonymous enum lists `fxls8962af`, `fxls8964af`, `fxls8967af`, and `fxls8974cf` for ID-table driver data. The core probe does not currently take this enum, instead identifying the device from `WHO_AM_I`. The header also declares both I2C and SPI regmap configs because SPI requires extra pad bits.

Integration and risks: this header is the namespace boundary for `IIO_FXLS8962AF`. Since wrappers may expose variants not present in all match tables, table updates should be synchronized with core chip-info entries and this enum. Test signals are successful compilation of both wrappers, namespace import/export, regmap config linkage, and PM op use by bus drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/fxls8962af.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/hid-sensor-accel-3d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/hid-sensor-accel-3d.c

Purpose: HID sensor hub platform driver exposing 3D accelerometer and gravity usages as IIO devices. It translates HID report descriptors and callbacks into IIO raw reads, sample frequency/hysteresis controls, and buffered samples.

Important APIs and flow: probe receives `struct hid_sensor_hub_device` as platform data, allocates `struct accel_3d_state`, selects accelerometer or gravity channel templates by HID usage, parses common HID sensor attributes, duplicates mutable channel specs, parses per-axis report attributes, formats scale, sets up HID sensor trigger support, registers the IIO device, and registers hub callbacks. `accel_3d_read_raw()` powers the sensor for synchronous raw reads and fetches the requested HID attribute. `accel_3d_write_raw()` writes sampling frequency or hysteresis through common helpers. `accel_3d_capture_sample()` stores axis or timestamp values from reports; `accel_3d_proc_event()` pushes the assembled scan buffer when data-ready is set.

State, dependencies, risks, and tests: state includes HID callback registration, common attributes, per-axis attribute info, scale formatting fields, offset, timestamp, and a u32 scan buffer with aligned timestamp. Dependencies are HID sensor hub APIs, common HID IIO trigger/PM helpers, platform driver registration, and IIO buffers. Risks include raw casts from HID report bytes to `u32`/`int64_t`, dynamic scan bit sizes capped to 32-bit storage, timestamp fallback when no HID timestamp arrives, and correct cleanup ordering between callback removal, IIO unregister, and trigger removal. Test signals include platform IDs `HID-SENSOR-200073` and `HID-SENSOR-20007b`, descriptor parsing for all axes, raw synchronous reads, scale/offset/frequency/hysteresis sysfs, buffered sample delivery with timestamps, and PM through `hid_sensor_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/hid-sensor-accel-3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-i2c.c

Purpose: I2C wrapper for the ROHM/Kionix KX022A/KX132/KX134 accelerometer core. It requires an IRQ, selects chip-specific metadata from match data, creates the regmap, and delegates to `kx022a_probe_internal()`.

Important APIs and flow: `kx022a_i2c_probe()` rejects devices with no IRQ, obtains `const struct kx022a_chip_info *` from I2C/OF match data, initializes `devm_regmap_init_i2c()` with the chip-specific regmap config, then calls the shared probe. ID and OF tables map five chip names to exported chip-info structures. The driver uses asynchronous probe preference and imports namespace `IIO_KX022A`.

State, dependencies, risks, and tests: no local state persists beyond devm regmap registration. Dependencies are I2C, regmap, IRQ firmware description, I2C/OF match-data plumbing, and the shared KX022A core. Risks include hard failure on missing IRQ even for direct-read-only use cases, match data being mandatory, and regmap config differing by chip family. Test signals include module autoload, no-IRQ rejection, match-data selection for each compatible, regmap initialization, and shared probe success.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-spi.c

Purpose: SPI wrapper for the ROHM/Kionix KX022A/KX132/KX134 accelerometer core. It mirrors the I2C wrapper but initializes a SPI regmap.

Important APIs and flow: `kx022a_spi_probe()` rejects missing IRQ, obtains chip info with `spi_get_device_match_data()`, creates `devm_regmap_init_spi()` using the chip-specific config, and delegates to `kx022a_probe_internal()`. SPI ID and OF tables cover the same five supported chip-info structures as I2C, and the driver prefers asynchronous probe.

State, dependencies, risks, and tests: all device state is in the core. Dependencies are SPI, regmap, IRQ configuration, OF/SPI match data, and namespace `IIO_KX022A`. Risks include mandatory IRQ requirement, chip-info mismatch with SPI ID/compatible, and protocol support depending on generic regmap SPI behavior. Test signals include SPI/OF autoload, no-IRQ failure, regmap setup, chip-info-specific WHO_AM_I validation in the core, and trigger/FIFO operation over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.c

Purpose: shared ROHM/Kionix accelerometer core for KX022A, KX132-1211, KX134-1211, KX132ACR-LBZ, and KX134ACR-LBZ devices. It provides direct raw reads, scale/ODR controls, mount matrix, data-ready trigger support, IRQ-driven hardware FIFO, chip-specific register maps, and shared probe for I2C/SPI wrappers.

Important APIs, types, and functions: exports five `struct kx022a_chip_info` instances and `kx022a_probe_internal()` in namespace `IIO_KX022A`. `struct kx022a_data` stores regmap, chip info, trigger, device, orientation, timestamps, IRQ routing registers, state bits, ODR period, mutex, watermark, dynamically allocated FIFO buffer, direct buffer, and scan buffer. Major helpers include regmap access tables for KX022A-like and KX132-like chips, `kx022a_chip_init()`, `__kx022a_turn_on_off()`, raw read/write and available-list functions, FIFO byte-count providers, FIFO enable/disable/flush, IRQ handlers, trigger state handling, and buffer setup ops.

Control flow: bus probe creates a regmap, then `kx022a_probe_internal()` obtains regulators, reads WHO_AM_I, selects INT1 or INT2 by firmware IRQ name, initializes state and IIO metadata, reads mount matrix, turns the sensor off for configuration, soft-resets and waits for reset completion, reinitializes regcache, sets 16-bit buffer resolution, configures interrupt pin polarity/type/routing, turns the sensor on, installs triggered-buffer support with FIFO sysfs attributes, allocates/registers a data-ready trigger, requests a threaded IRQ, and registers the IIO device. Direct reads claim direct mode and bulk-read one axis. Scale/ODR writes also claim direct mode and require temporarily disabling the sensor. FIFO mode is enabled for non-triggered buffered capture; data-ready trigger mode reads one frame per trigger and does not use the hardware FIFO.

State, dependencies, risks, and tests: state is guarded by `data->mutex` during power/config/FIFO operations; `state` distinguishes sample and FIFO modes, `trigger_enabled` blocks FIFO conflicts, and FIFO timestamps use either previous interrupt deltas or cached ODR for the first flush. Dependencies are regmap with volatile/precious/no-increment rules, regulators `io-vdd` and `vdd`, named firmware IRQs, IIO triggers/buffers/sysfs, and device properties for mount matrix. Risks include mandatory IRQ, delicate turn-off-before-config sequencing, dynamic FIFO buffer allocation/free under error paths, timestamp corruption if user flush races IRQ, KX022A full FIFO byte-count special case (`255` means 258 bytes), and reserved-register protection varying by chip. Test signals include WHO_AM_I warnings, reset poll and regcache reinit, INT1/INT2 routing, direct raw/scale/ODR sysfs, direct-write rejection during buffering, trigger enable/disable, FIFO watermark attributes, FIFO flush count/timestamps, and cleanup after buffer disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.h

Purpose: shared register and chip-info contract for the KX022A-family core and I2C/SPI wrappers. It defines KX022A/KX132 register addresses, bit masks, device IDs, FIFO sizes, and the `struct kx022a_chip_info` abstraction used to handle multiple related chips with one core.

Important types and constants: the header defines IDs for KX022A, KX132ACR-LBZ, KX134ACR-LBZ, KX132-1211, and KX134-1211; control bits such as software reset, PC1, data-ready, range select, ODR, FIFO enable, watermark, and interrupt config; and `struct kx022a_chip_info` fields for chip name, regmap config, scale table, channels, FIFO length, register addresses, interrupt registers, output register, and FIFO byte-count callback.

Integration, risks, and tests: wrappers use exported chip-info objects for match data and pass them to `kx022a_probe_internal()`. Any register definition error propagates into core behavior across both I2C and SPI. One visible risk is macro alias fragility around interrupt polarity definitions, so compile coverage is important. Test signals include successful compilation for all chip-info users, correct match-data pointer resolution, WHO_AM_I comparison against header IDs, FIFO length/watermark limits, and scale table sizing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kionix-kx022a.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxcjk-1013.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kxcjk-1013.c

Purpose: I2C IIO driver for a broad Kionix accelerometer family including KXCJK1013, KXCJ91008, KXTJ21009, KXTF9, and KX023-1025. It supports direct raw reads, scale and ODR controls, threshold/motion events, data-ready and motion triggers, triggered buffers, ACPI orientation quirks, regulators, and runtime PM.

Important APIs, types, and functions: key structures include `struct kx_chipset_regs`, `struct kx_chipset_info`, ODR startup tables, ODR maps, and `struct kxcjk1013_data`. The driver uses `kxcjk1013_chip_init()` for standby/configuration/operation setup, `kxcjk1013_set_mode()`, `kxcjk1013_set_range()`, `kxcjk1013_set_odr()`, `kxcjk1013_get_acc_reg()`, IIO raw/event callbacks, trigger setup callbacks, IRQ top/thread handlers, and system/runtime PM callbacks. IIO metadata includes mount matrix ext info, scale/sample-frequency sysfs attributes, a threshold event spec, and scan masks for three axes.

Control flow: probe allocates state, reads platform or firmware orientation, enables `vdd`/`vddio`, waits for power-up, selects chipset info from I2C ID or ACPI data, performs ACPI KIOX010A DSM laptop-mode handling when needed, initializes chip standby mode, 12-bit resolution, 4g range, ODR cache, interrupt polarity, KX023 routing, and operation mode. If an IRQ is available and the ACPI type is not SMO8500, it requests a threaded IRQ, allocates/registers data-ready and motion triggers, and sets the IIO device's default trigger. It then sets up a triggered buffer, enables PM runtime autosuspend, and registers the device. IRQ top half timestamps and polls the active trigger; the thread reports motion events and acknowledges interrupts. Runtime reads power the device on/off around direct raw access.

State, dependencies, risks, and tests: persistent state tracks client, triggers, orientation, mutex, scan buffer, ODR bits, range, wake threshold/duration, interrupt polarity, trigger/event enable flags, timestamp, and chipset register map. Dependencies include I2C SMBus block and byte operations, regulators, ACPI/OF/I2C match tables, IIO triggers/events/buffers, PM runtime, and optional platform data. Risks include many chip-specific register aliases, event and trigger sharing of one interrupt, `ev_enable_state` interactions with motion triggers, firmware-specific ACPI IDs/labels/DSM behavior, startup delay tables, and PM sequencing around autosuspend. Test signals include all ID/ACPI matches, mount matrix and labels for KIOX010A/KIOX020A, raw axis reads, scale/ODR set/get, unavailable sample-frequency strings per KXTF9 vs others, event threshold enable/value/period, trigger buffer samples, motion event direction reporting, SMO8500 no-IRQ-trigger path, and runtime/system suspend/resume restoring range and operation mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxcjk-1013.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-i2c.c

Purpose: I2C transport wrapper for the Kionix KXSD9 accelerometer common driver. It creates a small 8-bit regmap and delegates probe/remove/PM behavior to shared KXSD9 common code in `kxsd9.h`/its companion implementation.

Important APIs and flow: `kxsd9_i2c_probe()` builds a local `regmap_config` with max register `0x0e`, initializes `devm_regmap_init_i2c()`, and calls `kxsd9_common_probe(&i2c->dev, regmap, i2c->name)`. Remove calls `kxsd9_common_remove()`. OF and I2C ID tables expose `kionix,kxsd9` and `kxsd9`; PM ops are `kxsd9_dev_pm_ops`.

State, dependencies, risks, and tests: this wrapper stores no persistent state; the common KXSD9 driver owns IIO state and hardware behavior. Dependencies are I2C, regmap, the KXSD9 common namespace `IIO_KXSD9`, OF matching, and PM ops. Risks include transport/common contract drift, max-register mismatch with common code expectations, and regmap init failure. Test signals include I2C/OF autoload, regmap creation, common probe success with the passed device name, remove delegation, and PM callback linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-i2c.c -->
