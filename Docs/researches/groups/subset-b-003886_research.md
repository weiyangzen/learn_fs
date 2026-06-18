# subset-b-003886 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adrf6780.c -->
# sources/distributed-fs/ceph-client/drivers/iio/frequency/adrf6780.c

## Purpose
SPI IIO driver for the Analog Devices ADRF6780 microwave up/downconverter. It exposes detector ADC reads, RDAC linearization scale, and I/Q phase trim controls through IIO altvoltage channels.

## Important APIs, Types, And Functions
`struct adrf6780_state` stores the SPI device, LO input clock, mutex, device-property booleans, and aligned 3-byte SPI buffer. Register helpers are `__adrf6780_spi_read`, `adrf6780_spi_read`, `__adrf6780_spi_write`, `adrf6780_spi_write`, and update-bits variants. IIO entry points are `adrf6780_read_raw`, `adrf6780_write_raw`, and `adrf6780_reg_access`. Probe uses `devm_iio_device_alloc`, `devm_clk_get_enabled`, `devm_add_action_or_reset`, and `devm_iio_device_register`.

## Control Flow
Probe allocates the IIO device, parses boolean firmware properties, enables the `lo_in` clock, initializes the mutex, performs reset and chip-ID validation, programs enable/LO/ADC-control bits, registers a cleanup action, then registers the IIO device. Raw ADC reads start and enable the ADC, wait 200-250 us, verify status, clear start, and read the final ADC output.

## State And Persistence
Persistent hardware state includes enable bits for VGA, LO, IF/IQ, detector, bias, sideband, and VDET selection plus writable linearize and phase trim registers. Software state caches only firmware-property defaults and protects the shared SPI buffer with a mutex. Cleanup disables all enable-register components.

## Dependencies And Integration Points
Depends on SPI, common clock framework, firmware properties, IIO direct-mode channels, debugfs register access through IIO, and device-tree `adi,adrf6780` plus SPI ID `adrf6780`.

## Risks
Invalid property combinations can program contradictory IF/IQ/LO modes without policy validation. ADC reads rely on fixed timing and a single status bit. Register writes accept raw user values with limited range masking by register fields. The source contains duplicated `default:` labels in `adrf6780_read_raw`, which is a compile-time warning/error signal depending on exact compiler parsing.

## Test Signals
Build with the ADRF6780 frequency driver enabled, probe with a valid `lo_in` clock and `adi,adrf6780` node, verify chip-ID read succeeds, read `in_altvoltage0_raw`, write/read linearize scale and I/Q phase sysfs attributes, and check debugfs register access plus cleanup powerdown on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/frequency/adrf6780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/Kconfig

## Purpose
Kconfig menu for IIO digital gyroscope drivers. It defines user-visible driver choices and hidden bus helper symbols for SPI, I2C, HID sensor hub, Samsung SSP, ST, ADIS, Bosch, NXP, InvenSense, and Analog Devices gyroscopes.

## Important APIs, Types, And Functions
Important symbols include `ADIS16080`, `ADIS16130`, `ADIS16136`, `ADIS16260`, `ADXRS290`, `ADXRS450`, `BMG160`, `BMG160_I2C`, `BMG160_SPI`, `FXAS21002C`, `FXAS21002C_I2C`, `FXAS21002C_SPI`, `HID_SENSOR_GYRO_3D`, `MPU3050`, `MPU3050_I2C`, `IIO_ST_GYRO_3AXIS`, `IIO_ST_GYRO_I2C_3AXIS`, `IIO_ST_GYRO_SPI_3AXIS`, and `ITG3200`.

## Control Flow
The menu gates compilation by bus and subsystem dependencies. Composite drivers select hidden transport symbols when the relevant bus is available, while ADIS, HID, and triggered-buffer-capable drivers select their helper libraries.

## State And Persistence
Kconfig selections persist in kernel build configuration and determine which objects and modules are built. No runtime state is stored here.

## Dependencies And Integration Points
Integrates with SPI, SPI_MASTER, I2C, I2C_MUX, SYSFS, HID_SENSOR_HUB, REGMAP, REGMAP_I2C, REGMAP_SPI, IIO_BUFFER, IIO_TRIGGERED_BUFFER, IIO_ADIS_LIB, IIO_ADIS_LIB_BUFFER, IIO_ST_SENSORS_CORE/I2C/SPI, and HID sensor common trigger support.

## Risks
Hidden bus helper symbols are selected from parent choices, so dependency mistakes can silently omit transport modules. The `BMG160` and `FXAS21002C` parent symbols select both bus shims when both buses are enabled, increasing module surface. `MPU3050` is hidden and depends on `MPU3050_I2C` for user selection.

## Test Signals
Run Kconfig dependency checks with common allmodconfig/allnoconfig fragments, verify expected modules are emitted from matching Makefile rules, and test that enabling each visible option pulls in its required regmap, buffer, and transport support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/Makefile

## Purpose
Build rules for IIO gyroscope drivers and composite modules.

## Important APIs, Types, And Functions
Rules map Kconfig symbols to objects: ADIS/ADXRS single-object drivers, `bmg160_core.o` plus bus shims, `fxas21002c_core.o` plus bus shims, `hid-sensor-gyro-3d.o`, composite `mpu3050.o`, composite `itg3200.o`, `ssp_gyro_sensor.o`, and composite `st_gyro.o` plus ST bus shims.

## Control Flow
Kbuild includes objects according to `obj-$(CONFIG_...)`. Composite module members are listed with `mpu3050-objs`, `itg3200-y`, `itg3200-$(CONFIG_IIO_BUFFER)`, `st_gyro-y`, and `st_gyro-$(CONFIG_IIO_BUFFER)`.

## State And Persistence
No runtime state. Build output determines module names and whether buffer helpers are linked into composite modules.

## Dependencies And Integration Points
Tightly coupled to `drivers/iio/gyro/Kconfig`; the module split must match exported symbols in core and bus files, including BMG160, FXAS21002C, MPU3050, ITG3200, and ST gyros.

## Risks
Kconfig/Makefile drift can create unresolved symbols or missing bus modules. Conditional buffer object inclusion means buffer APIs must stay guarded in headers and call sites.

## Test Signals
Compile with buffer enabled and disabled, compile with each bus backend as built-in and module, and confirm module names match Kconfig help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16080.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16080.c

## Purpose
Simple SPI IIO driver for ADIS16080 and ADIS16100 yaw-rate gyroscopes, exposing Z angular velocity, two auxiliary voltage inputs, and temperature.

## Important APIs, Types, And Functions
`struct adis16080_state` holds SPI device, chip scale info, mutex, and aligned 16-bit buffer. `adis16080_read_sample` performs the two-transfer SPI read sequence. `adis16080_read_raw` reports raw values, scale, and offsets. `adis16080_chip_info` differentiates ADIS16080 and ADIS16100 angular scale.

## Control Flow
Probe allocates an IIO device, initializes the mutex, selects chip info from `spi_device_id`, defines channels and direct mode, then registers via devm. Reads write the channel selector with `ADIS16080_DIN_WRITE`, clock a second transfer, and sign-extend 12-bit data.

## State And Persistence
No runtime configuration beyond selected channel commands and chip scale table. The only mutable software state is the shared SPI buffer protected by a mutex.

## Dependencies And Integration Points
Uses SPI, IIO direct mode, sysfs channel attributes, and SPI IDs `adis16080`/`adis16100`.

## Risks
No device-ID validation or startup sequence, so a wrong compatible device can register and return nonsense. Reads are direct-only and serialized but there is no buffered mode. Voltage/temp scaling is hardcoded from datasheet assumptions.

## Test Signals
Build/probe via SPI ID, read angular velocity, aux voltage, and temperature raw/scale/offset sysfs files, and compare scale differences between `adis16080` and `adis16100`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16080.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16130.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16130.c

## Purpose
SPI IIO driver for the ADIS16130 high-precision angular-rate sensor, exposing Z angular velocity and temperature.

## Important APIs, Types, And Functions
`struct adis16130_state` stores SPI device, buffer mutex, and aligned 4-byte transfer buffer. `adis16130_spi_read` issues a 24-bit read command. `adis16130_read_raw` supplies raw, scale, and offset information. Channels are `IIO_ANGL_VEL` and `IIO_TEMP`.

## Control Flow
Probe allocates the IIO device, assigns SPI data, initializes the mutex, configures channels and direct mode, and registers. Each raw read sends `ADIS16130_CON_RD | reg`, then extracts the 24-bit big-endian payload.

## State And Persistence
The driver does not program device mode registers despite defining mode/channel bits. State is limited to the SPI buffer and static scale/offset constants.

## Dependencies And Integration Points
Uses SPI and IIO direct mode. Device discovery is by SPI driver name or `spi:adis16130` module alias.

## Risks
No product-ID or channel-enable initialization is performed, so it assumes firmware or reset defaults are sufficient. Raw values are returned unsigned for a 24-bit device and rely on offset/scale for interpretation.

## Test Signals
Compile/probe as `adis16130`, read `in_anglvel_z_raw`, `in_temp_raw`, scale, and offset files, and validate SPI transfer size and byte ordering with known sensor output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16136.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16136.c

## Purpose
ADIS library-based SPI IIO driver for ADIS16133/16135/16136/16137 gyroscopes with angular velocity, temperature, sample frequency, calibration bias, low-pass filter, buffered capture, and debugfs identity data.

## Important APIs, Types, And Functions
`struct adis16136` wraps chip info and `struct adis`. Key functions include debugfs readers, `adis16136_set_freq`, `__adis16136_get_freq`, frequency sysfs handlers, `adis16136_set_filter`, `adis16136_get_filter`, `adis16136_read_raw`, `adis16136_write_raw`, `adis16136_initial_setup`, and `adis16136_stop_device`. Chip data is described by `struct adis16136_chip_info`, `ADIS16136_DATA`, timeout tables, and status error messages.

## Control Flow
Probe chooses variant data from SPI ID, initializes ADIS core, sets up ADIS buffer/trigger, runs startup and product-ID check, registers a stop action, registers the IIO device, and creates debugfs files. Raw reads delegate conversions to ADIS helpers; writes update offset/filter registers.

## State And Persistence
Hardware-persistent state includes sample-period, averaging filter, gyroscope offset, diagnostic/status registers, and sleep control. ADIS core manages locking, scan mode, burst/buffer setup, and diagnostic state. Debugfs exposes product ID, flash count, and serial/lot values.

## Dependencies And Integration Points
Depends on SPI_MASTER, `IIO_ADIS_LIB`, optional ADIS buffer support, IIO sysfs/debugfs, and the `IIO_ADISLIB` namespace.

## Risks
Filter selection depends on current sample frequency and divisors; invalid register values can index divisor tables. Product-ID mismatch is only a warning. The source includes an apparent duplicated `break` in the filter loop, worth catching in build review.

## Test Signals
Build with ADIS lib and buffers, probe each SPI ID, validate product-ID warning path, read/write sampling frequency and low-pass frequency, read/write calibration bias, enable buffered capture, and inspect debugfs serial/product/flash files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16136.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16260.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16260.c

## Purpose
ADIS library-based SPI IIO driver for ADIS16260-family programmable digital gyroscopes, including variants with inclination, supply, auxiliary ADC, temperature, calibration, sample-frequency, buffered capture, and diagnostics.

## Important APIs, Types, And Functions
`struct adis16260` holds variant info and ADIS state. Channel tables use ADIS channel macros. `adis16260_read_raw` and `adis16260_write_raw` implement scale, offset, calibration bias/scale, and sample frequency. `adis16260_stop_device`, `adis16260_probe`, `adis16260_data`, and status error tables integrate with ADIS core.

## Control Flow
Probe resolves variant from SPI ID, allocates IIO state, initializes ADIS core and ADIS buffer/trigger, performs initial startup, registers a sleep cleanup action, and registers the IIO device. Sample frequency writes compute the divisor, adjust SPI max speed for slow sample periods, and write the sample-period register under ADIS lock.

## State And Persistence
Mutable hardware state includes sample period, gyro offset, gyro scale, diagnostic registers, and sleep control. The driver changes `spi->max_speed_hz` based on selected sample rate. Variant tables persist scale/channel differences.

## Dependencies And Integration Points
Uses SPI, `IIO_ADIS_LIB`, optional ADIS buffer support, IIO direct mode, and SPI IDs for ADIS16250/251/255/260/265/266.

## Risks
Changing `spi->max_speed_hz` in write_raw can affect later transfers globally for the SPI device. Calibration ranges are limited but sample frequency accepts values that can divide poorly or underflow if not validated by callers. The source contains a duplicated assignment line in the CALIBSCALE path.

## Test Signals
Probe each variant ID, read all exposed channel raw/scale/offset values, write calibration bias/scale boundaries, change sampling frequency across slow/fast thresholds, enable buffers, and verify ADIS diagnostic error messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adis16260.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs290.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs290.c

## Purpose
SPI IIO driver for the dual-axis ADXRS290 gyroscope. It exposes X/Y angular velocity, temperature, low/high-pass filter controls, optional data-ready trigger, and triggered buffer capture.

## Important APIs, Types, And Functions
`struct adxrs290_state` stores SPI device, mutex, mode, cached filter indexes, trigger, and aligned scan buffer. Important functions include ID reads in probe, `adxrs290_set_mode`, `adxrs290_get_rate_data`, `adxrs290_get_temp_data`, filter get/set helpers, `adxrs290_read_raw`, `adxrs290_write_raw`, `adxrs290_read_avail`, debugfs reg access, trigger set/reenable callbacks, and `adxrs290_trigger_handler`.

## Control Flow
Probe validates ADI/MEMS/device IDs, switches to measurement mode with temperature sensor enabled, waits for transition, caches filter register values, sets up triggered buffer, optionally registers an IRQ-backed trigger, and registers the IIO device. Buffered reads bulk-read DATAX0 through temp into the scan buffer.

## State And Persistence
Hardware state includes power mode, temperature sensor enable, filter indexes, and data-ready output configuration. Software caches mode and filter indexes, so external debugfs writes can desynchronize sysfs-reported filter state.

## Dependencies And Integration Points
Depends on SPI, IIO buffers, triggered buffer, IIO triggers, optional device-tree `adi,adxrs290`, and an optional SPI IRQ for data-ready.

## Risks
Filter writes update cached indexes before the SPI write result is known, so failed writes can leave stale software state. Direct raw reads are guarded by `iio_device_claim_direct`; buffer users must handle `-EBUSY`. IRQ-free systems fall back to polling/no own trigger.

## Test Signals
Validate ID failure paths, read X/Y/temp raw and scale, enumerate available filter frequencies, write LPF/HPF legal and illegal values, run buffered capture with and without IRQ, and check standby cleanup on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs290.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs450.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs450.c

## Purpose
SPI IIO driver for ADXRS450/ADXRS453 digital-output gyroscopes, exposing Z angular velocity, temperature, quadrature correction, and optional calibration bias depending on variant.

## Important APIs, Types, And Functions
`struct adxrs450_state` holds SPI device, mutex, and aligned 32-bit TX/RX buffers. Key helpers are `adxrs450_spi_read_reg_16`, `adxrs450_spi_write_reg_16`, `adxrs450_spi_sensor_data`, `adxrs450_spi_initial`, `adxrs450_initial_setup`, `adxrs450_read_raw`, and `adxrs450_write_raw`.

## Control Flow
Probe allocates/registers the IIO device and then runs the datasheet startup handshake. The initial setup waits, issues check and no-check sensor-data commands, validates status bits, then reads fault registers. Register reads use a two-transfer SPI sequence with parity generation.

## State And Persistence
Hardware state is mostly read-only sensor data plus dynamic-null correction writes for ADXRS450 calibration bias. The driver has no runtime PM or cleanup power-down path. Software state is limited to protected SPI buffers.

## Dependencies And Integration Points
Depends on SPI and IIO direct mode. Supports SPI IDs `adxrs450` and `adxrs453` with variant-specific channel masks.

## Risks
Probe registers the IIO device before initial hardware setup, so a later startup failure leaves error flow reliant on devm cleanup after a short registration window. Startup response checks are strict and timing-sensitive. The source includes an apparent duplicate `return ret;` in setup.

## Test Signals
Probe both IDs, verify startup fault/status handling, read angular velocity and temperature raw/scale, read quadrature correction, write calibration bias on ADXRS450 and confirm ADXRS453 rejects it, and run SPI parity/fault injection if available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/adxrs450.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160.h -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160.h

## Purpose
Shared header for Bosch BMG160/BMI055/BMI088 gyroscope core and bus transport drivers.

## Important APIs, Types, And Functions
Declares `bmg160_pm_ops`, `bmg160_core_probe`, and `bmg160_core_remove`.

## Control Flow
Bus drivers include this header, construct a regmap, and call `bmg160_core_probe`; remove paths call `bmg160_core_remove`; driver structs reuse `bmg160_pm_ops`.

## State And Persistence
No state is stored in the header. It defines ownership boundaries between core and transports.

## Dependencies And Integration Points
Integrates Linux device, regmap, and PM ops concepts across `bmg160_core.c`, `bmg160_i2c.c`, and `bmg160_spi.c`.

## Risks
Any signature change must be applied to both bus shims. PM ops are externally visible without namespace scoping.

## Test Signals
Compile both I2C and SPI modules and verify exported core/remove/PM symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_core.c

## Purpose
Common IIO core for Bosch BMG160 and compatible BMI055/BMI088 gyroscopes, providing raw/temp reads, scale, sample frequency, low-pass filter, mount matrix, events, IRQ triggers, buffers, regulators, and runtime PM.

## Important APIs, Types, And Functions
`struct bmg160_data` stores regmap, triggers, mount matrix, mutex, scan buffer, range/filter/event state, IRQ, and trigger flags. Major functions cover chip init, mode/power control, bandwidth/filter/scale conversion, axis/temp reads, raw sysfs handlers, event handlers, any-motion and data-ready interrupt setup, buffer setup ops, trigger ops, `bmg160_core_probe`, `bmg160_core_remove`, and PM callbacks.

## Control Flow
Core probe enables regulators, reads mount matrix, resets and validates chip ID, initializes default bandwidth/range/interrupt latch mode, creates optional IRQ triggers, sets up triggered buffers, enables runtime PM autosuspend, and registers the IIO device. Raw writes temporarily resume the device for register writes. IRQ top half polls triggers and optionally wakes the threaded event handler.

## State And Persistence
Persistent device registers include power mode, range, bandwidth, interrupt mapping/enables, latch mode, slope threshold, and motion axis bits. Software caches selected DPS range, slope threshold, event enable state, trigger-enable state, and orientation. Runtime PM autosuspends after 2 seconds and remove enters deep suspend.

## Dependencies And Integration Points
Depends on regmap supplied by bus shims, regulators `vdd`/`vddio`, IIO events, triggered buffers, IIO triggers, runtime PM, and optional IRQ. Exports core probe/remove and PM ops for I2C/SPI modules.

## Risks
Event and trigger state interact through shared interrupt registers and need careful sequencing. Some table searches do not explicitly guard the "not found" index before indexing in filter helpers. The source includes apparent duplicated comment/`else` text in event paths that should be caught by compile tests.

## Test Signals
Probe over both buses with and without IRQ, verify chip-ID failure, read/write sample frequency, LPF, scale, temp and axes, enable buffer capture, enable data-ready and any-motion triggers, test event threshold busy behavior, and exercise runtime/system suspend and remove deep-suspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_i2c.c

## Purpose
I2C transport shim for BMG160-compatible gyroscopes.

## Important APIs, Types, And Functions
Defines an 8-bit regmap config, `bmg160_i2c_probe`, `bmg160_i2c_remove`, ACPI/I2C/OF match tables, and an `i2c_driver` using shared `bmg160_pm_ops`.

## Control Flow
Probe initializes an I2C regmap, chooses the IIO name from I2C ID or ACPI name, and delegates to `bmg160_core_probe` with client IRQ. Remove delegates to `bmg160_core_remove`.

## State And Persistence
No local device state beyond devm regmap allocation and driver data set by the core.

## Dependencies And Integration Points
Depends on I2C, REGMAP_I2C, BMG160 core exports, ACPI ID `BMG0160`, I2C IDs, and OF compatibles for BMG160/BMI055/BMI088.

## Risks
If neither I2C ID nor ACPI name is available, the core name can be NULL. Bus-specific regmap max register must stay aligned with core register use.

## Test Signals
Build as module, probe via I2C/ACPI/OF names, verify regmap init failure path, IRQ forwarding, PM ops attachment, and clean remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_spi.c

## Purpose
SPI transport shim for BMG160-compatible gyroscopes.

## Important APIs, Types, And Functions
Defines SPI regmap config, `bmg160_spi_probe`, `bmg160_spi_remove`, SPI/OF match tables, and a `spi_driver` with shared PM ops.

## Control Flow
Probe obtains SPI ID, initializes a SPI regmap, and delegates to `bmg160_core_probe` with SPI IRQ and ID name. Remove calls `bmg160_core_remove`.

## State And Persistence
No transport-owned runtime state aside from the devm regmap.

## Dependencies And Integration Points
Depends on SPI, REGMAP_SPI, BMG160 core exports, and OF/SPI IDs for BMG160/BMI055/BMI088.

## Risks
Probe assumes `spi_get_device_id` returns non-NULL and dereferences `id->name`. Regmap access flags are generic; any SPI read/write flag requirements must be represented by regmap defaults or future config updates.

## Test Signals
Build/probe via SPI IDs and OF compatibles, verify IRQ propagation to the core, exercise core sysfs and buffered paths over SPI, and test remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/bmg160_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c.h -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c.h

## Purpose
Shared register and field definition header for the NXP FXAS21002C gyroscope core and I2C/SPI bus drivers.

## Important APIs, Types, And Functions
Defines register addresses from status/output through control registers, `enum fxas21002c_fields` for regmap-field allocation, `fxas21002c_pm_ops`, `fxas21002c_core_probe`, and `fxas21002c_core_remove`.

## Control Flow
Bus drivers include the header for regmap limits and delegate all device behavior to core probe/remove. The core uses the enum order to allocate and index all `regmap_field` handles.

## State And Persistence
No state stored here; it defines the shared register contract and cross-module API.

## Dependencies And Integration Points
Integrates with Linux regmap, PM ops, and the `IIO_FXAS21002C` namespace exports.

## Risks
The enum order must remain synchronized with `fxas21002c_reg_fields`; adding fields without updating both sides breaks register access. Register max used by bus regmap configs depends on these definitions.

## Test Signals
Compile core and both bus modules; verify namespace imports and all field allocations succeed at probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_core.c

## Purpose
Common IIO core for the NXP FXAS21002C 3-axis gyroscope, providing raw temperature/axis reads, scale/range, ODR, LPF/HPF controls, optional data-ready trigger, triggered buffers, regulators, and runtime/system PM.

## Important APIs, Types, And Functions
`struct fxas21002c_data` tracks chip ID, mode/previous mode, mutex, regmap and fields, trigger, timestamp, IRQ, regulators, and scan buffer. Key functions include field conversion helpers, `fxas21002c_mode_get/set`, `fxas21002c_write`, PM get/put, temp/axis reads, ODR/filter/scale get/set, raw sysfs handlers, trigger handler and IRQ thread, chip init, trigger probe, regulator helpers, core probe/remove, and PM callbacks.

## Control Flow
Core probe allocates IIO state, allocates every regmap field, enables regulators, registers a power-disable action, validates chip ID, initializes standby mode and 200 Hz ODR, optionally sets up an IRQ-backed trigger, installs triggered buffer support, enables runtime PM autosuspend, then registers the IIO device. Writes that require standby/ready transitions go through `fxas21002c_write`.

## State And Persistence
Hardware state includes active/ready mode bits, ODR, LPF/HPF, range and double-range bit, interrupt routing/polarity, and regulator power. Software caches current and previous mode, timestamp from IRQ top half, and chip ID.

## Dependencies And Integration Points
Depends on regmap fields supplied by bus shims, regulators `vdd`/`vddio`, firmware IRQ properties including `INT1` and `drive-open-drain`, IIO triggers/buffers, runtime PM, and namespace exports for bus modules.

## Risks
Mode transitions and `prev_mode` are central; failures mid-write can leave the sensor in READY. `fxas21002c_regulators_get` uses `dev->parent`, so bus-device hierarchy matters. The trigger probe logs INT2 even after selecting INT1. The source includes a duplicated `*val = 0;` in HPF read.

## Test Signals
Probe over I2C and SPI, validate both chip IDs, read/write ODR, LPF, HPF, and scale including invalid ODR/filter combinations, enable buffered capture with IRQ, test rising/open-drain interrupt properties, and exercise runtime/system suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_i2c.c

## Purpose
I2C transport driver for FXAS21002C.

## Important APIs, Types, And Functions
Defines 8-bit I2C regmap config, `fxas21002c_i2c_probe`, `fxas21002c_i2c_remove`, I2C/OF match tables, and an `i2c_driver` importing `IIO_FXAS21002C`.

## Control Flow
Probe initializes regmap over I2C and delegates to `fxas21002c_core_probe` with IRQ and device name. Remove delegates to core remove.

## State And Persistence
No local runtime state beyond the devm regmap and driver binding.

## Dependencies And Integration Points
Depends on I2C, REGMAP_I2C, shared PM ops, `nxp,fxas21002c` compatible, and core namespace exports.

## Risks
Regmap config is minimal and assumes default I2C register semantics. The probe passes `i2c->name`, so naming must match userspace expectations and core channel naming.

## Test Signals
Build/probe via I2C ID and OF compatible, verify regmap init failures, IRQ forwarding, PM ops, and core sysfs behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_spi.c

## Purpose
SPI transport driver for FXAS21002C.

## Important APIs, Types, And Functions
Defines SPI regmap config, `fxas21002c_spi_probe`, `fxas21002c_spi_remove`, SPI/OF match tables, and a `spi_driver` importing `IIO_FXAS21002C`.

## Control Flow
Probe initializes SPI regmap, obtains SPI ID name, and delegates to `fxas21002c_core_probe`; remove calls `fxas21002c_core_remove`.

## State And Persistence
No local runtime state except regmap allocation and binding.

## Dependencies And Integration Points
Depends on SPI, REGMAP_SPI, shared PM ops, `nxp,fxas21002c` compatible, and core namespace exports.

## Risks
Probe assumes a non-NULL SPI ID. SPI-specific read/write flags are not customized in regmap config, so future protocol quirks need explicit config changes.

## Test Signals
Build/probe via SPI ID and OF compatible, verify IRQ forwarding, PM ops, and core raw/buffer sysfs behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/fxas21002c_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/hid-sensor-gyro-3d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/hid-sensor-gyro-3d.c

## Purpose
Platform IIO driver that exposes HID Sensor Hub 3D gyroscope reports as IIO angular velocity channels with scale, offset, sampling frequency, hysteresis, trigger, and buffered data.

## Important APIs, Types, And Functions
`struct gyro_3d_state` stores HID callbacks, common HID sensor attributes, per-axis attribute info, scan buffer, scale/offset, and timestamp. Key functions include channel bit adjustment, `gyro_3d_read_raw`, `gyro_3d_write_raw`, `gyro_3d_proc_event`, `gyro_3d_capture_sample`, `gyro_3d_parse_report`, probe, and remove.

## Control Flow
Probe parses common HID attributes, duplicates the channel table to adjust scan bit sizes from report descriptors, parses per-axis report fields and scale, sets up HID sensor trigger, registers the IIO device, then registers HID callbacks. Capture callbacks fill the scan buffer; event callback pushes a complete sample when data-ready is set.

## State And Persistence
Runtime state is HID-managed: sampling frequency, hysteresis, power state, report IDs, logical minima, scale, offset, and timestamp. No hardware registers are directly persisted by this file.

## Dependencies And Integration Points
Depends on HID_SENSOR_HUB, HID sensor IIO common trigger code, platform device ID `HID-SENSOR-200076`, IIO buffers, and HID usage IDs for angular velocity axes and timestamps.

## Risks
Raw sample extraction casts `raw_data` directly to `u32`/`s64`, so alignment and endian assumptions depend on HID core behavior. Callback registration occurs after IIO registration, so error cleanup must remove trigger and IIO device in order. Missing axis report info aborts probe.

## Test Signals
Use a HID sensor hub exposing usage `0x200076`, verify adjusted scan realbits, read raw/scale/offset/frequency/hysteresis, change frequency and hysteresis, enable buffered capture, and test callback removal on unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/hid-sensor-gyro-3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_buffer.c

## Purpose
Buffer and trigger support for the ITG3200 I2C gyroscope driver.

## Important APIs, Types, And Functions
Functions include `itg3200_read_all_channels`, `itg3200_trigger_handler`, `itg3200_buffer_configure`, `itg3200_buffer_unconfigure`, `itg3200_data_rdy_trigger_set_state`, `itg3200_probe_trigger`, and `itg3200_remove_trigger`.

## Control Flow
Core probe calls buffer configure and, when IRQ is present, trigger probe. Trigger setup allocates an IIO trigger, requests the data-ready IRQ, registers the trigger, and assigns it as default. Trigger handler bulk-reads temp and XYZ samples and pushes them with timestamp.

## State And Persistence
The trigger state toggles `ITG3200_IRQ_DATA_RDY_ENABLE` in the IRQ config register. Trigger allocation, IRQ registration, and default trigger reference are stored in `struct itg3200`.

## Dependencies And Integration Points
Depends on I2C transfer helpers from ITG3200 core/header, IIO triggered buffers, IIO triggers, and a hardware IRQ.

## Risks
Uses non-devm `iio_trigger_alloc`, `request_irq`, and cleanup, so error paths must stay exact. `itg3200_read_all_channels` returns raw `i2c_transfer` count, and the handler only treats negative as failure. No scan-mask selective reads; it always reads all channels.

## Test Signals
Probe with IRQ, enable/disable trigger, capture buffered samples, verify remove frees IRQ and trigger, and test buffer operation when no IRQ is configured.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_core.c

## Purpose
I2C IIO driver core for InvenSense ITG3200 3-axis gyroscope, exposing temperature, XYZ angular velocity, scale, offset, sample frequency, mount matrix, optional buffers, triggers, and sleep PM.

## Important APIs, Types, And Functions
Exports `itg3200_write_reg_8` and `itg3200_read_reg_8` for buffer code. Important functions include `itg3200_read_reg_s16`, `itg3200_read_raw`, `itg3200_write_raw`, reset, full-scale enable, initial setup, mount-matrix extension, probe/remove, suspend, and resume.

## Control Flow
Probe reads mount matrix, sets up IIO metadata, configures buffer and optional trigger, resets and validates device address register, enables full scale, initializes the mutex, and registers the IIO device. Sample-frequency writes read DLPF config, compute divider, and write sample-rate divisor under lock.

## State And Persistence
Hardware state includes reset, IRQ configuration, full-scale DLPF bits, power-management sleep, and sample-rate divisor. Software state includes I2C client, mount matrix, mutex, and optional trigger from the shared header.

## Dependencies And Integration Points
Depends on I2C, `linux/iio/gyro/itg3200.h`, optional IIO buffer object, OF compatible `invensense,itg3200`, and simple PM ops.

## Risks
The source shows a duplicated function declaration line for `itg3200_initial_setup`, which should fail compilation if present verbatim. `itg3200_read_reg_s16` sets the register auto-increment bit after filling the first I2C message buffer, so review byte ordering/address behavior carefully. Power management is marked TODO and only system sleep is implemented.

## Test Signals
Build with and without IIO_BUFFER, probe ID/address check, read temp and axes, read/write sample frequency, enable buffer and data-ready IRQ, suspend/resume, and validate mount matrix sysfs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/itg3200_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-core.c

## Purpose
Common IIO core for the InvenSense MPU-3050 gyroscope, providing raw temp/axis reads, calibration bias, scale, sample frequency, mount matrix, triggered buffers, FIFO-backed hardware IRQ trigger, regulators, OTP identity readout, and runtime PM.

## Important APIs, Types, And Functions
Uses `struct mpu3050` from `mpu3050.h`. Key functions include frequency and sampling setup, 8 kHz samplerate helper, raw read/write handlers, trigger handler with FIFO drain, buffer setup ops, mount matrix extension, `mpu3050_read_mem`, hardware init, power up/down, IRQ top/thread handlers, trigger state/probe, common probe/remove, and runtime PM callbacks.

## Control Flow
Common probe initializes defaults, reads mount matrix, gets regulators, powers up, validates chip and product IDs, reads OTP memory into randomness/logs, sets up triggered buffer, optionally registers IRQ trigger, enables runtime PM autosuspend, and registers IIO. Hardware trigger enable powers the device, resets/enables FIFO, starts sampling, clears IRQ, and enables raw-ready interrupts.

## State And Persistence
Software caches fullscale, low-pass filter, divisor, calibration offsets, trigger flags, IRQ polarity/latch/open-drain, FIFO footer state, hardware timestamp, regulators, and optional I2C mux pointer. Hardware state includes power, PLL, offset registers, DLPF/fullscale/sync, sample divider, FIFO, interrupt config, OTP memory, and sleep bit.

## Dependencies And Integration Points
Depends on regmap from transport, regulators `vdd`/`vlogic`, IIO triggered buffers/triggers, runtime PM, IRQ trigger properties, firmware mount matrix, and the I2C transport/mux layer.

## Risks
FIFO handling is complex and timestamp semantics intentionally fall back to zero for drained FIFO entries. Runtime PM and trigger enable paths must balance power references. Calibration and scale writes update cached state and are applied on next sampling start, not immediately. The source contains duplicated string/write_raw lines in read/info paths, worth build-checking.

## Test Signals
Probe chip/product IDs, verify OTP log, read/write calibration, scale, and sample frequency, raw-read temp/axes, enable external-trigger and hardware IRQ-trigger buffers, induce FIFO overflow, test IRQ polarity modes, and run runtime suspend/resume/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-i2c.c

## Purpose
I2C transport and bypass-mux driver for the MPU3050 common core.

## Important APIs, Types, And Functions
Defines `mpu3050_i2c_regmap_config`, mux select/deselect callbacks, `mpu3050_i2c_probe`, `mpu3050_i2c_remove`, I2C/OF match tables, and an `i2c_driver` using `mpu3050_dev_pm_ops`.

## Control Flow
Probe verifies I2C block functionality, initializes regmap, calls `mpu3050_common_probe`, then creates an optional locked/gated I2C mux whose select powers up the MPU and whose deselect releases runtime PM. Remove deletes mux adapters then calls common remove.

## State And Persistence
Transport state includes the devm regmap and optional `i2cmux` stored in common state. Runtime PM references are taken around bypass access.

## Dependencies And Integration Points
Depends on I2C, REGMAP_I2C, I2C_MUX, runtime PM, common MPU3050 core, OF compatibles `invensense,mpu3050` and deprecated `invn,mpu3050`.

## Risks
Mux allocation/add failures are deliberately non-fatal, so downstream devices may disappear while the gyro still works. Probe returns `-ENODEV` without I2C ID even if OF data exists. Bypass select depends on runtime PM being initialized by common probe.

## Test Signals
Probe over I2C, verify block functionality failure path, create/remove bypass mux, access a child bus through mux, exercise runtime PM during mux selection, and remove cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050.h -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050.h

## Purpose
Shared MPU3050 state and API header for common core and I2C transport.

## Important APIs, Types, And Functions
Defines `enum mpu3050_fullscale`, `enum mpu3050_lpf`, `enum mpu3050_axis`, `struct mpu3050`, `mpu3050_common_probe`, `mpu3050_common_remove`, and `mpu3050_dev_pm_ops`.

## Control Flow
Transport allocates regmap and calls common probe; common code fills `struct mpu3050`; I2C transport later reads `iio_priv` to attach an I2C mux and calls common remove during teardown.

## State And Persistence
The struct centralizes all persistent runtime state: device/regmap/lock, IRQ and trigger data, regulators, fullscale/LPF/divisor, calibration offsets, IRQ behavior flags, FIFO footer flag, hardware timestamp, orientation, and bypass mux pointer.

## Dependencies And Integration Points
Includes IIO, mutex, regmap, regulators, and I2C mux core declarations. Bridges `mpu3050-core.c` and `mpu3050-i2c.c`.

## Risks
Header state layout is shared across modules; changes can affect transport assumptions. Enum values are written into hardware bitfields, so reordering would be a behavior bug.

## Test Signals
Compile common and I2C modules, validate enum-to-register mappings through scale/frequency writes, and verify mux pointer lifecycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/mpu3050.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/ssp_gyro_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/ssp_gyro_sensor.c

## Purpose
Samsung Sensor Platform gyroscope IIO consumer driver exposing sensorhub gyroscope data as three angular velocity channels with kfifo buffering and sample-frequency control.

## Important APIs, Types, And Functions
Uses `ssp_sensor_data` and helper macros from SSP IIO common code. Key functions are `ssp_gyro_read_raw`, `ssp_gyro_write_raw`, `ssp_process_gyro_data`, `ssp_gyro_probe`, and buffer setup ops using common SSP postenable/postdisable.

## Control Flow
Probe allocates IIO state, sets SSP process callback/type, configures channels and scan mask, sets up a kfifo buffer, registers the IIO device, then registers as an SSP gyroscope consumer. Sample frequency reads/writes convert between SSP delay and IIO frequency.

## State And Persistence
Sensor delay is stored by the parent SSP data structure. This driver stores process callback/type in IIO private data and relies on devm cleanup for buffer/IIO registration.

## Dependencies And Integration Points
Depends on Samsung SSP common sensorhub, `ssp_iio_sensor.h`, IIO kfifo buffers, platform bus name `ssp-gyroscope`, and `IIO_SSP_SENSORS` namespace.

## Risks
Parent data is reached through `indio_dev->dev.parent->parent`, so device hierarchy changes can break it. `ssp_convert_to_time` return is used directly as delay even if conversion semantics change.

## Test Signals
Probe under an SSP parent, read/write sampling frequency, enable buffer, feed sensorhub frames through `ssp_process_gyro_data`, and confirm consumer registration happens after IIO setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/ssp_gyro_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro.h -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro.h

## Purpose
Shared header for STMicroelectronics IIO gyroscope core, buffer code, and I2C/SPI bus drivers.

## Important APIs, Types, And Functions
Defines device-name constants for supported ST gyro variants and declares buffer/trigger functions when `CONFIG_IIO_BUFFER` is enabled. Provides no-op ring allocation and NULL trigger state macro when buffers are disabled.

## Control Flow
Core and bus files use the constants for settings lookup and match tables. Buffer-enabled builds call `st_gyro_allocate_ring` and use `ST_GYRO_TRIGGER_SET_STATE`; non-buffer builds compile out those paths.

## State And Persistence
No stored state; it defines compile-time contracts and supported device names.

## Dependencies And Integration Points
Depends on ST sensor common types and IIO trigger declarations. Integrates `st_gyro_core.c`, `st_gyro_buffer.c`, `st_gyro_i2c.c`, and `st_gyro_spi.c`.

## Risks
Name constants must match Kconfig, bus ID tables, OF data, and settings table entries. Buffer guards must stay synchronized with Makefile conditional object inclusion.

## Test Signals
Compile with and without `CONFIG_IIO_BUFFER`; verify all device names resolve through settings lookup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_buffer.c

## Purpose
Triggered-buffer glue for ST gyroscope common driver.

## Important APIs, Types, And Functions
Exports `st_gyro_trig_set_state` and `st_gyro_allocate_ring`. Buffer setup ops are `st_gyro_buffer_postenable` and `st_gyro_buffer_predisable`.

## Control Flow
Postenable applies the active scan mask to hardware axes, enables the sensor, and restores all axes if enable fails. Predisable disables the sensor and restores all axes. Trigger state delegates data-ready IRQ enablement to ST sensor common code. Ring allocation uses `devm_iio_triggered_buffer_setup` with `st_sensors_trigger_handler`.

## State And Persistence
Hardware state affected here is axis-enable mask, sensor enable bit, and data-ready IRQ state. No file-local persistent state.

## Dependencies And Integration Points
Depends on IIO buffers/triggers and ST sensors common helpers such as `st_sensors_set_axis_enable`, `st_sensors_set_enable`, `st_sensors_set_dataready_irq`, and `st_sensors_trigger_handler`.

## Risks
Buffer enable failures can leave axes temporarily restricted if restore fails. Active scan mask assumptions must match the three-axis channel table. Built only when `CONFIG_IIO_BUFFER` is enabled.

## Test Signals
Enable buffers with different scan masks, verify axis mask programming and restore on disable, toggle trigger state, and test failure injection in sensor enable paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_core.c

## Purpose
Common STMicroelectronics 3-axis gyroscope IIO core supporting several L3G/LSM devices with shared channel definitions, per-chip settings, raw reads, scale/ODR writes, mount matrix, buffers, triggers, and debugfs register access.

## Important APIs, Types, And Functions
Important data includes `st_gyro_16bit_channels`, `st_gyro_sensors_settings`, and `gyro_pdata`. Key functions are `st_gyro_read_raw`, `st_gyro_write_raw`, `st_gyro_get_settings`, and `st_gyro_common_probe`. Trigger ops use ST common validation and optional buffer trigger set-state.

## Control Flow
Bus driver selects settings by device name, configures transport, powers the sensor, then calls common probe. Common probe verifies WHOAMI, sets channel count/table, reads mount matrix, initializes default fullscale/ODR, calls ST common sensor initialization, allocates ring buffer, optionally allocates trigger, and registers IIO.

## State And Persistence
State is mostly in `struct st_sensor_data`: sensor settings, current fullscale, ODR, mount matrix, IRQ, and transport-specific transfer functions. Hardware registers persist ODR, power, axis enable, fullscale, BDU, data-ready IRQ, SPI mode, and supported WHOAMI.

## Dependencies And Integration Points
Depends on `IIO_ST_SENSORS_CORE`, optional triggered buffers, ST common sensor helpers, bus-specific ST I2C/SPI configuration modules, sysfs attributes, and debugfs register access.

## Risks
Settings table entries are dense and must match actual device register maps; a bad WHOAMI/name mapping causes wrong ODR/fullscale programming. DRDY is fixed to INT2. Adding a device requires updating names, settings, and bus match tables together.

## Test Signals
Probe each supported name/WHOAMI, read raw axes and scale/ODR, write fullscale and sample frequency, inspect available sysfs attributes, enable buffers/triggers with IRQ, verify mount matrix, and test debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_i2c.c

## Purpose
I2C bus driver for STMicroelectronics gyroscopes using the shared ST gyro core.

## Important APIs, Types, And Functions
Defines OF match table, `st_gyro_i2c_probe`, I2C ID table, and `i2c_driver`. Uses `st_sensors_dev_name_probe`, `st_gyro_get_settings`, `st_sensors_i2c_configure`, `st_sensors_power_enable`, and `st_gyro_common_probe`.

## Control Flow
Probe normalizes device name from firmware/I2C, looks up settings, allocates IIO state, stores settings, configures I2C transfer layer, powers the sensor, and calls common probe.

## State And Persistence
Bus-local state is in allocated `st_sensor_data`; hardware power is enabled before common initialization.

## Dependencies And Integration Points
Depends on I2C, ST sensors common I2C helpers, OF compatibles for all supported ST gyro variants, and shared core exports.

## Risks
Name lookup is strict; mismatch between compatible data, client name, and settings table yields `-ENODEV`. No explicit remove function is present, relying on devm/common cleanup.

## Test Signals
Probe all I2C IDs/OF compatibles, verify transport configuration, power-enable failures, settings lookup failures, and common sysfs/buffer behavior over I2C.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_spi.c

## Purpose
SPI bus driver for STMicroelectronics gyroscopes using the shared ST gyro core.

## Important APIs, Types, And Functions
Defines OF match table, `st_gyro_spi_probe`, SPI ID table, and `spi_driver`. Uses `st_sensors_dev_name_probe`, `st_gyro_get_settings`, `st_sensors_spi_configure`, `st_sensors_power_enable`, and `st_gyro_common_probe`.

## Control Flow
Probe normalizes the SPI modalias, finds matching settings, allocates IIO state, configures SPI transfer layer, powers the sensor, and delegates registration to common probe.

## State And Persistence
Bus-local state is `st_sensor_data` with SPI transfer hooks and selected settings. Hardware power remains managed by ST common/devm cleanup paths.

## Dependencies And Integration Points
Depends on SPI, ST sensors common SPI helpers, OF/SPI IDs for supported variants, and shared core exports.

## Risks
Name/settings drift across OF table, SPI ID table, and settings table breaks probe. SPI-specific protocol details are delegated to ST common SPI configuration; future devices may need new settings.

## Test Signals
Probe all SPI IDs/OF compatibles, verify SPI transfer setup and power enable, exercise common raw/scale/ODR/buffer paths over SPI, and test bad modalias failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/gyro/st_gyro_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/health/Kconfig

## Purpose
Kconfig menu for IIO health sensors, currently heart-rate and pulse-oximeter AFEs/sensors.

## Important APIs, Types, And Functions
Defines visible symbols `AFE4403`, `AFE4404`, `MAX30100`, and `MAX30102`, with bus and helper selections.

## Control Flow
The menu groups health sensors under "Health Sensors" and "Heart Rate Monitors". Each symbol controls driver compilation and selects the required regmap/buffer support.

## State And Persistence
No runtime state; configuration persists in kernel build files and controls module availability.

## Dependencies And Integration Points
`AFE4403` depends on SPI_MASTER and selects REGMAP_SPI, IIO_BUFFER, and IIO_TRIGGERED_BUFFER. Other entries depend on I2C and select REGMAP_I2C plus buffer support.

## Risks
Help/module names must stay synchronized with Makefile. Missing IIO trigger/buffer selection would break driver builds or runtime buffered capture.

## Test Signals
Kconfig build combinations for SPI-only/I2C-only configs, allmodconfig, and module-name verification against Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/health/Makefile

## Purpose
Kbuild rules for IIO health sensor drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_AFE4403`, `CONFIG_AFE4404`, `CONFIG_MAX30100`, and `CONFIG_MAX30102` to their corresponding objects.

## Control Flow
Kbuild includes each object according to its Kconfig symbol.

## State And Persistence
No runtime state; build outputs persist as built-in objects or modules.

## Dependencies And Integration Points
Must remain aligned with `drivers/iio/health/Kconfig` and source filenames in the health directory.

## Risks
Adding or renaming a health driver requires Kconfig and Makefile updates together.

## Test Signals
Build each symbol as module and built-in; verify resulting module names and object inclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe4403.c -->
# sources/distributed-fs/ceph-client/drivers/iio/health/afe4403.c

## Purpose
SPI IIO driver for the TI AFE4403 heart-rate monitor and pulse-oximeter analog front end. It exposes ADC intensity channels, LED current controls, transimpedance resistance/capacitance attributes, optional IRQ trigger, buffered capture, regulator power, and sleep PM.

## Important APIs, Types, And Functions
`struct afe4403_data` stores SPI device, regmap, regmap fields, regulator, trigger, IRQ, and aligned buffer. Important functions include regmap-field attribute show/store, `afe4403_read` raw SPI read-mode helper, `afe4403_read_raw`, `afe4403_write_raw`, trigger handler, regulator disable action, default timing sequence, PM suspend/resume, and probe.

## Control Flow
Probe allocates IIO state, initializes 24-bit SPI regmap, allocates regmap fields, enables `tx_sup`, registers regulator cleanup, software-resets the AFE, writes default timing/control sequences, sets IIO channels/info, optionally allocates/registers IRQ trigger, sets up triggered buffer, and registers IIO. Raw intensity reads temporarily switch CONTROL0 into read mode, read a 24-bit ADC register, then switch back to write mode.

## State And Persistence
Hardware state includes timing registers, control bits, LED currents, TIA gain/capacitance fields, read/write mode in CONTROL0, PDN_AFE sleep bit, and regulator state. Software state stores regmap fields, trigger, and scan buffer.

## Dependencies And Integration Points
Depends on SPI_MASTER, REGMAP_SPI, IIO triggered buffers/triggers, regulator `tx_sup`, shared `afe440x.h` macros/registers, OF compatible `ti,afe4403`, and SPI ID `afe4403`.

## Risks
Read-mode toggling around SPI reads must be restored after errors; the trigger handler exits before restoring write mode if an active-channel read fails. Current raw writes do not range-check LED field values before regmap_field_write. The source includes a duplicated `case IIO_CURRENT:` label.

## Test Signals
Probe with regulator and optional IRQ, verify reset/default sequence writes, read all intensity raw channels, read/write LED current and scale, read/write resistance/capacitance attributes including invalid values, run triggered buffer capture, and test suspend/resume power-down/up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe4403.c -->
