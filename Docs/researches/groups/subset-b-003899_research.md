# subset-b-003899 Research

Grouped research for Linux IIO magnetometer, multiplexer, orientation, position, potentiometer, and potentiostat build files under `sources/distributed-fs/ceph-client/drivers/iio`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/si7210.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/si7210.c

## Purpose
I2C IIO driver for the Silicon Labs Si7210 Hall-effect magnetic sensor. It exposes one magnetic channel and one processed temperature channel through direct-mode IIO.

## Important APIs, Types, And Functions
`struct si7210_data` owns the regmap, I2C client, fetch mutex, regulator voltage, OTP-derived temperature coefficients, two scale calibration arrays, and current scale. `si7210_probe()` allocates and registers the IIO device. `si7210_device_init()` wakes the part, reads OTP calibration, enables auto-increment, and selects the 20 mT scale. `si7210_fetch_measurement()` serializes DSPSIG source selection and one-burst conversion. `si7210_read_raw()` provides raw magnetic counts, magnetic scale/offset, and processed temperature. `si7210_write_raw()` accepts only the two supported magnetic scales and delegates to `si7210_set_scale()`.

## Control Flow
Probe initializes regmap access tables, enables and reads `vdd`, configures IIO metadata, then initializes the chip. Measurements lock `fetch_lock`, choose magnetic or temperature DSP output through `DSPSIGSEL`, trigger `ONEBURST`, and bulk-read the two result bytes. Scale changes write six OTP calibration bytes into the A0-A5 coefficient registers.

## State And Persistence
Persistent calibration is read from OTP into RAM at probe. Runtime mutable state is `curr_scale` and coefficient registers. The driver does not maintain PM callbacks or buffered capture.

## Dependencies And Integration Points
Depends on I2C, regmap, regulator consumer APIs, IIO direct mode, and kernel fixed-point helpers. Device matching uses `"silabs,si7210"` and `"si7210"`.

## Risks And Test Signals
Temperature compensation uses integer arithmetic and `temp_gain / 2048`, which is integer-divided before scaling; regression tests should check expected processed temperatures. Wake relies on SMBus read returning `0xff`. Useful test signals are successful OTP reads, raw magnetic reads at both scales, invalid scale rejection, regulator voltage handling, and regmap access-table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/si7210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn.h -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn.h

## Purpose
Shared ST magnetometer header that names supported devices and declares buffer/trigger helpers used by the ST magnetometer core and bus glue.

## Important APIs, Types, And Functions
Defines public device-name strings such as `LSM303DLH_MAGN_DEV_NAME`, `LIS3MDL_MAGN_DEV_NAME`, `LIS2MDL_MAGN_DEV_NAME`, `IIS2MDC_MAGN_DEV_NAME`, and `LSM303C_MAGN_DEV_NAME`. Declares `st_magn_allocate_ring()` and `st_magn_trig_set_state()` when `CONFIG_IIO_BUFFER` is enabled. Provides a no-op `st_magn_allocate_ring()` and `NULL` trigger setter macro when buffering is disabled.

## Control Flow
This header contributes compile-time selection: buffered builds wire the core to real triggered-buffer setup, while non-buffered builds keep common probe working by returning success from the inline stub.

## State And Persistence
No runtime state. Its constants are the stable linkage between device-tree/modalias names and `st_magn_get_settings()` in the core.

## Dependencies And Integration Points
Includes `linux/iio/common/st_sensors.h` and is consumed by `st_magn_core.c`, `st_magn_buffer.c`, `st_magn_i2c.c`, and `st_magn_spi.c`.

## Risks And Test Signals
Adding a new ST magnetometer requires synchronized name additions here, bus ID tables, OF match tables, and core settings. Build coverage should include both buffered and non-buffered configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_buffer.c

## Purpose
Buffered capture support for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_trig_set_state()` toggles the common ST data-ready IRQ through `st_sensors_set_dataready_irq()`. `st_magn_buffer_postenable()` and `st_magn_buffer_predisable()` enable and disable the sensor around buffer use. `st_magn_allocate_ring()` installs a devm-managed triggered buffer using the common `st_sensors_trigger_handler`.

## Control Flow
The ST common probe calls `st_magn_allocate_ring()`. When userspace enables the IIO buffer, postenable powers measurements on; when disabled, predisable powers them off. Trigger state changes are delegated to common ST sensor IRQ handling.

## State And Persistence
No private state. It mutates device enable and data-ready IRQ state through `struct st_sensor_data` owned by the IIO device.

## Dependencies And Integration Points
Integrates IIO triggered buffers, IIO triggers, and `linux/iio/common/st_sensors.h`. It is conditional through declarations in `st_magn.h`.

## Risks And Test Signals
The buffer path relies on common ST helpers matching channel layout and scan ordering. Test buffer enable/disable, trigger attachment, IRQ toggling, and direct reads before and after buffered capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_core.c

## Purpose
Common STMicroelectronics magnetometer implementation for multiple LSM/LIS/IIS devices. It centralizes channel definitions, per-chip register settings, raw/scale/sample-frequency IIO operations, trigger configuration, and common probe.

## Important APIs, Types, And Functions
`st_magn_sensors_settings[]` is the key table, mapping supported device names to WAI IDs, channels, ODR registers, power bits, full-scale ranges, BDU, DRDY, SPI mode, multi-read behavior, and boot time. `st_magn_get_settings()` exports lookup by name. `st_magn_common_probe()` verifies the ID, assigns channels, reads mount matrix, initializes ST common sensor state, allocates ring/trigger resources, and registers the IIO device. `st_magn_read_raw()` and `st_magn_write_raw()` bridge IIO raw/scale/sample-frequency access to common ST helpers.

## Control Flow
Bus-specific drivers allocate an IIO device, set `sensor_settings`, configure I2C/SPI transport, enable power, then call `st_magn_common_probe()`. Common probe verifies WAI, picks the channel table, sets default full-scale and ODR, initializes the sensor using platform data/default DRDY pin, optionally allocates buffer and trigger, then registers with IIO.

## State And Persistence
State lives in `struct st_sensor_data`: current full scale, ODR, IRQ, mount matrix, and common transport fields. Hardware settings are volatile register programming; no nonvolatile writes.

## Dependencies And Integration Points
Depends heavily on `IIO_ST_SENSORS` helpers, IIO triggers, mount matrix parsing, and bus glue in `st_magn_i2c.c` and `st_magn_spi.c`. Exports symbols in namespace `IIO_ST_SENSORS`.

## Risks And Test Signals
Risks are table correctness: wrong endianness, output addresses, gain/gain2, WAI, or DRDY masks silently break specific parts. Test each supported family for ID verification, raw axis reads, Z-axis special gain where applicable, ODR/scale sysfs writes, mount-matrix exposure, and buffer trigger operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_i2c.c

## Purpose
I2C transport glue for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_of_match[]` maps ST magnetometer compatibles to names used by common settings. `st_magn_i2c_probe()` normalizes the I2C device name, looks up settings with `st_magn_get_settings()`, allocates `struct st_sensor_data`, configures I2C transport with `st_sensors_i2c_configure()`, enables power, and calls `st_magn_common_probe()`. `st_magn_id_table[]` provides legacy I2C modalias matching.

## Control Flow
Device bind enters the probe, validates that the name is recognized by the common settings table, configures common ST I2C access, enables regulators/power through ST helpers, then delegates all sensor setup to the common core.

## State And Persistence
No independent state beyond the allocated IIO private data. Persistent device identity is from OF/I2C tables; runtime sensor state is held by the common core.

## Dependencies And Integration Points
Uses `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and namespace `IIO_ST_SENSORS`. It is the bus endpoint for `st_magn_core.c`.

## Risks And Test Signals
Name-table mismatches cause `-ENODEV`. Test OF compatibles and I2C IDs for every name in the table, probe failure on unknown names, and power-enable error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_spi.c

## Purpose
SPI transport glue for the common ST magnetometer driver.

## Important APIs, Types, And Functions
`st_magn_of_match[]` lists SPI-capable ST magnetometers and maps compatibles to common device names. `st_magn_spi_probe()` normalizes `spi->modalias`, finds common settings, allocates IIO private ST state, configures SPI transport through `st_sensors_spi_configure()`, enables power, and calls `st_magn_common_probe()`. `st_magn_id_table[]` exposes SPI modalias support.

## Control Flow
The probe path mirrors I2C: identify settings, allocate IIO state, configure bus operations, enable power, and delegate to common probe. Older I2C-only parts are intentionally absent from the SPI ID table.

## State And Persistence
No persistent state. Runtime configuration and data-ready behavior are controlled by the common ST core and hardware registers.

## Dependencies And Integration Points
Depends on `linux/iio/common/st_sensors_spi.h`, ST common sensor helpers, and `st_magn_core.c`.

## Risks And Test Signals
Compatibility-string naming is subtle for single-chip vs multi-function devices. Test SPI modalias and OF matching, sensor ID verification through the SPI regmap path, and scale/ODR/buffer operations on each SPI-capable part.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/st_magn_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tlv493d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tlv493d.c

## Purpose
I2C IIO driver for the Infineon TLV493D-A1B6 low-power 3D magnetic sensor. It supports direct raw reads and triggered buffers for X/Y/Z magnetic axes plus temperature.

## Important APIs, Types, And Functions
`struct tlv493d_data` stores the I2C client, access mutex, operating mode, and the write-register shadow required by the device's byte-stream protocol. `tlv493d_init()` reads reserved fields and seeds `wr_regs`. `tlv493d_set_operating_mode()` edits shadow mode bits and writes the entire write register stream. `tlv493d_get_measurements()` resumes the device, polls until the temperature channel validity bits indicate fresh data, decodes 12-bit signed fields, and autosuspends. `tlv493d_trigger_handler()` pushes buffered scans.

## Control Flow
Probe allocates IIO state, enables `vdd`, chooses master-controlled mode, initializes the register shadow, registers channels and a triggered buffer, enables runtime PM, and registers the IIO device. Direct reads and trigger reads both call the same measurement routine.

## State And Persistence
The driver keeps a shadow of all writable bytes because writes must start at address zero and omit register addresses. Runtime PM switches between powerdown and the configured mode. No nonvolatile state is written.

## Dependencies And Integration Points
Uses raw I2C byte streams, regulator APIs, runtime PM, IIO triggered buffers, and `read_poll_timeout()`. Matches `"infineon,tlv493d-a1b6"`.

## Risks And Test Signals
The unusual bus protocol makes register-shadow correctness critical. Poll timing depends on the selected operating mode. Test initialization reserved-bit preservation, PM suspend/resume, direct and triggered reads, scan mask layout, scale/offset reporting, and I2C short/error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tlv493d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tmag5273.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tmag5273.c

## Purpose
I2C IIO driver for TI TMAG5273 low-power 3D Hall-effect sensors. It exposes temperature, X/Y/Z magnetic axes, angle, and magnitude in direct mode.

## Important APIs, Types, And Functions
`struct tmag5273_data` tracks device ID/version, generated device name, conversion averaging, magnetic scale range, selected angle plane, regmap, and a measurement mutex. `tmag5273_get_measure()` polls conversion status, bulk-reads temperature and axes, then reads angle and magnitude. `tmag5273_write_osr()` and `tmag5273_write_scale()` implement writable oversampling and magnetic range controls. `tmag5273_chip_init()` configures averaging, continuous mode, enabled channels, angle plane, scale range, and temperature. Runtime PM callbacks sleep and wake the device.

## Control Flow
Probe builds the regmap, enables `vcc`, wakes the chip with a dummy read, validates the TI manufacturer ID, powers continuous mode, registers a devm power-down action, enables runtime PM/autosuspend, reads the optional `ti,angle-measurement` property, initializes registers, then registers the IIO device. Raw reads resume the device, serialize a full measurement, autosuspend, and return the requested channel.

## State And Persistence
State is volatile hardware configuration plus in-memory `conv_avg`, `scale_index`, and `angle_measurement`. Runtime PM changes operating mode between continuous and sleep. No nonvolatile writes.

## Dependencies And Integration Points
Uses I2C regmap, runtime PM, regulator, device properties, IIO sysfs availability callbacks, and OF compatible `"ti,tmag5273"`.

## Risks And Test Signals
Device-version handling controls scale tables; unsupported versions are warned but still registered. `FIELD_PREP()` is used when extracting version, so version reporting deserves scrutiny. Test manufacturer/version reads, angle property values, OSR list enforcement, both scale ranges, autosuspend/resume, and conversion timeout handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/tmag5273.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/yamaha-yas530.c -->
# sources/distributed-fs/ceph-client/drivers/iio/magnetometer/yamaha-yas530.c

## Purpose
I2C IIO driver for Yamaha YAS530/YAS532/YAS533/YAS537 3-axis magnetometers. It implements device-specific calibration extraction, measurement conversion, runtime PM, mount matrix, and triggered-buffer capture.

## Important APIs, Types, And Functions
`struct yas5xx_chip_info` defines per-variant IDs, scale, temperature reference, volatile registers, and function pointers for measurement, calibration, offset measurement, and power-on. `struct yas5xx` stores chip info, calibration, hard offsets, mount matrix, regmap, regulators, optional reset GPIO, mutex, and scan buffer. `yas530_measure()` and `yas537_measure()` perform low-level conversions. `yas530_get_measure()` and `yas537_get_measure()` produce IIO-facing temperature and X/Y/Z values. Calibration readers decode OTP bitfields and program YAS537 trims. `yas5xx_probe()` orchestrates regulators, reset, ID check, calibration, power-on, offset discovery, buffer setup, IIO registration, and PM.

## Control Flow
Probe powers rails, waits for startup, releases optional reset, creates regmap, checks device ID, reads calibration, powers on with variant logic, measures hard offsets where applicable, sets up channels and triggered buffer, then enables runtime PM. Reads and trigger fills resume the device, call the selected `get_measure`, then autosuspend. Removal unregisters IIO/buffer resources, disables PM, asserts reset, and disables regulators.

## State And Persistence
Calibration is read from device OTP and retained in RAM; YAS537 trim registers are programmed from OTP. YAS530/YAS532 hard offsets are discovered by a binary-search-like coil measurement and stored in RAM/registers. Runtime PM resets power and re-runs `power_on()` on resume.

## Dependencies And Integration Points
Uses I2C regmap, regulator bulk APIs, optional GPIO reset, runtime PM, random input from calibration bytes, IIO mount matrix, triggered buffers, and OF/I2C match data.

## Risks And Test Signals
This file is calibration-heavy: bitfield extraction, version-specific math, and offset search are the main risk areas. Runtime resume does not re-read OTP or remeasure offsets, so verify register state after power cycling. Test all supported IDs, calibration blank warnings, direct reads, buffer scans, reset/regulator failure unwinds, mount matrix exposure, and PM suspend/resume correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/yamaha-yas530.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Kconfig

## Purpose
Kconfig menu and option for the IIO multiplexer driver.

## Important APIs, Types, And Functions
Defines `CONFIG_IIO_MUX` as a tristate option labeled "IIO multiplexer driver" and selects `MULTIPLEXER`.

## Control Flow
When enabled as built-in or module, the Makefile builds `iio-mux.o`. The help text documents the module name as `iio-mux`.

## State And Persistence
No runtime state; this controls compilation.

## Dependencies And Integration Points
Integrates the IIO mux driver with the kernel multiplexer framework through `select MULTIPLEXER`.

## Risks And Test Signals
Build tests should ensure enabling `IIO_MUX=m/y` pulls in mux consumer support and produces `iio-mux`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Makefile

## Purpose
Build rule for IIO multiplexer drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_IIO_MUX` to `iio-mux.o`.

## Control Flow
Kbuild includes the object only when the Kconfig option is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Tied directly to `drivers/iio/multiplexer/Kconfig`.

## Risks And Test Signals
Compile with `CONFIG_IIO_MUX=m` and `=y` to confirm object inclusion and module naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/iio-mux.c -->
# sources/distributed-fs/ceph-client/drivers/iio/multiplexer/iio-mux.c

## Purpose
Platform driver that exposes multiple logical IIO channels over one parent IIO channel selected through a mux-control provider.

## Important APIs, Types, And Functions
`struct mux` holds parent channel, mux control, child channel specs, ext_info wrappers, per-child cached ext_info values, cached state, and settle delay. `iio_mux_select()` selects the physical mux state, restores writable ext_info for the child if changing state, and updates cache. `mux_read_raw()`, `mux_read_avail()`, and `mux_write_raw()` forward IIO operations to the selected parent channel. `mux_read_ext_info()` and `mux_write_ext_info()` wrap parent ext_info. `mux_probe()` parses `channels`, optional `settle-time-us`, allocates a packed private area, configures child channels, and registers the IIO device.

## Control Flow
Probe gets the `"parent"` IIO channel and mux control, reads child labels, skips empty labels, copies parent channel capabilities/ext_info, validates state count against mux control states, and registers. Each read/write selects the desired state, forwards to the parent, then deselects.

## State And Persistence
`cached_state` avoids unnecessary ext_info restoration. Writable ext_info values are cached per child in devm memory so configuration follows logical channel selection. No nonvolatile state.

## Dependencies And Integration Points
Uses IIO consumer APIs, mux consumer framework, platform/OF compatible `"io-channel-mux"`, and device properties.

## Risks And Test Signals
Risks include missing locking around concurrent select/forward/deselect operations and ext_info cache lifetime/size. Test multiple children, empty channel labels, settle delays, parent scale/raw availability propagation, writable ext_info isolation per child, invalid state counts, and concurrent sysfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/multiplexer/iio-mux.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/orientation/Kconfig

## Purpose
Kconfig menu for HID orientation/inclinometer IIO drivers.

## Important APIs, Types, And Functions
Defines `HID_SENSOR_INCLINOMETER_3D` and `HID_SENSOR_DEVICE_ROTATION`. Both depend on `HID_SENSOR_HUB` and select common HID sensor IIO support, trigger support, and IIO buffering.

## Control Flow
Selecting either option enables the matching Makefile object. Device rotation exposes quaternion orientation; inclinometer exposes 3D tilt.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Connects HID sensor hub drivers to the IIO orientation directory.

## Risks And Test Signals
Build-test each option as module and built-in, ensuring required HID/IIO helper selections are sufficient.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/orientation/Makefile

## Purpose
Kbuild rules for IIO orientation drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_HID_SENSOR_INCLINOMETER_3D` to `hid-sensor-incl-3d.o` and `CONFIG_HID_SENSOR_DEVICE_ROTATION` to `hid-sensor-rotation.o`.

## Control Flow
Objects are built only when the corresponding Kconfig symbols are enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the orientation Kconfig file.

## Risks And Test Signals
Compile with each symbol independently to catch missing dependency selections.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-incl-3d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-incl-3d.c

## Purpose
HID sensor hub bridge exposing a 3-axis inclinometer as an IIO device with direct reads, sampling/hysteresis controls, and triggered buffered samples.

## Important APIs, Types, And Functions
`struct incl_3d_state` stores HID callbacks, common attributes, per-axis report metadata, scale/offset, timestamp, and scan buffer. `incl_3d_parse_report()` discovers X/Y/Z report fields and scale. `incl_3d_read_raw()` performs synchronous HID raw reads and reports scale, offset, sample frequency, and hysteresis. `incl_3d_write_raw()` updates sample frequency or hysteresis. `incl_3d_capture_sample()` stores incoming HID samples; `incl_3d_proc_event()` pushes scans when data is ready. `hid_incl_3d_probe()` wires common attributes, trigger, IIO registration, and HID callback registration.

## Control Flow
Probe parses HID common attributes and report fields, duplicates channel specs so scan bit widths can be adjusted from the descriptor, sets up the HID-trigger integration, registers IIO, then registers callbacks. Runtime HID callbacks capture individual fields and push a timestamped buffer on event.

## State And Persistence
State is entirely in RAM and comes from HID report descriptors and common attributes. No persistent writes; sample frequency/hysteresis writes go to HID sensor hub attributes.

## Dependencies And Integration Points
Depends on HID sensor hub, `hid-sensor-trigger.h`, IIO buffer support, and platform IDs for usage `HID-SENSOR-200086`.

## Risks And Test Signals
Risks include raw-data alignment casts, descriptor sizes larger than `u32`, callback ordering, and trigger cleanup ordering. Test direct reads, scale formatting, sample frequency/hysteresis writes, descriptor-derived bit widths, timestamp conversion, and callback removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-incl-3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-rotation.c -->
# sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-rotation.c

## Purpose
HID sensor hub bridge for device, relative, and geomagnetic orientation sensors, exposing quaternion rotation through IIO.

## Important APIs, Types, And Functions
`struct dev_rot_state` stores callbacks, common HID attributes, quaternion report info, scale/offset, timestamp, and a scan buffer containing four quaternion values plus two timestamps for ABI compatibility. `dev_rot_read_raw()` uses `read_raw_multi` to return four raw quaternion components. `dev_rot_parse_report()` discovers the quaternion report and adjusts channel repeat/bit width. `dev_rot_capture_sample()` copies quaternion samples and timestamp reports. `dev_rot_proc_event()` pushes buffered data with both correct and legacy timestamp positions.

## Control Flow
Probe chooses the IIO device name from HID usage, parses common attributes, duplicates and adjusts channel specs, sets up a HID trigger, registers IIO, and registers callbacks. Removal unregisters callbacks, IIO, and trigger. Buffered operation receives quaternion fields then pushes on a data-ready event.

## State And Persistence
No persistent state. Runtime state is descriptor-derived scale/report metadata and the most recent quaternion sample.

## Dependencies And Integration Points
Uses HID sensor hub, IIO buffer APIs, HID trigger common code, and platform IDs `HID-SENSOR-20008a`, `HID-SENSOR-20008e`, and `HID-SENSOR-2000c1`.

## Risks And Test Signals
The timestamp duplication is intentional ABI compatibility and should not be simplified casually. Test 16-bit and 32-bit quaternion report paths, multi-value raw reads, sampling/hysteresis writes, all three usage IDs, timestamp placement, and cleanup on callback registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/orientation/hid-sensor-rotation.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/position/Kconfig

## Purpose
Kconfig menu for linear/angular position IIO drivers.

## Important APIs, Types, And Functions
Defines `IQS624_POS` for Azoteq IQS624/625 angular position sensors and `HID_SENSOR_CUSTOM_INTEL_HINGE` for Intel custom HID hinge sensors.

## Control Flow
`IQS624_POS` depends on `MFD_IQS62X || COMPILE_TEST`. The HID hinge driver depends on `HID_SENSOR_HUB` and selects IIO buffer, triggered buffer, and HID sensor IIO helpers.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Connects platform/MFD and HID sensor implementations to the IIO position directory.

## Risks And Test Signals
Build-test both options independently and verify module names from help text match produced objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/position/Makefile

## Purpose
Kbuild rules for IIO position drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_HID_SENSOR_CUSTOM_INTEL_HINGE` to `hid-sensor-custom-intel-hinge.o` and `CONFIG_IQS624_POS` to `iqs624-pos.o`.

## Control Flow
Kbuild includes each object when the corresponding config symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the position Kconfig file.

## Risks And Test Signals
Compile with module and built-in variants for both symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/hid-sensor-custom-intel-hinge.c -->
# sources/distributed-fs/ceph-client/drivers/iio/position/hid-sensor-custom-intel-hinge.c

## Purpose
HID sensor hub bridge for Intel custom hinge sensors, exposing hinge, screen, and keyboard angles as IIO angle channels with labels.

## Important APIs, Types, And Functions
`struct hinge_state` stores common HID attributes, report metadata for three custom value fields, labels, callbacks, scale/offset, timestamp, and scan buffer. `hinge_parse_report()` discovers three custom report fields and adjusts channel realbits. `hinge_read_raw()` performs synchronous reads and exposes scale, offset, sample frequency, and hysteresis. `hinge_read_label()` returns `"hinge"`, `"screen"`, or `"keyboard"`. `hinge_capture_sample()` stores custom values and timestamps; `hinge_proc_event()` pushes buffered scans. `hid_hinge_probe()` wires all HID/IIO resources.

## Control Flow
Probe allocates IIO state, initializes labels, parses common HID attributes, duplicates channel definitions, parses report fields, sets up a trigger, registers HID callbacks, then registers the IIO device. Error paths remove callback/trigger resources in reverse order.

## State And Persistence
State is descriptor-derived and in RAM. Sample frequency/hysteresis writes are delegated to HID common attributes; no nonvolatile storage.

## Dependencies And Integration Points
Depends on HID sensor hub, IIO buffers, and HID trigger helpers. Platform ID is `HID-SENSOR-INT-020b`.

## Risks And Test Signals
Risks include hard-coded custom field ordering, raw casts from HID data, and callback/IIO registration order. Test three-channel label ABI, direct raw reads, buffered scans, timestamp conversion, sample frequency/hysteresis writes, and remove/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/hid-sensor-custom-intel-hinge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/iqs624-pos.c -->
# sources/distributed-fs/ceph-client/drivers/iio/position/iqs624-pos.c

## Purpose
Platform IIO driver for Azoteq IQS624/IQS625 angular position sensing through the IQS62x MFD core.

## Important APIs, Types, And Functions
`struct iqs624_pos_private` stores the MFD core pointer, IIO device, notifier block, mutex, event-enable flag, and cached angle. `iqs624_pos_angle_get()` reads the IQS624 degree output or IQS625 interval register. `iqs624_pos_angle_en()` unmasks the correct MFD event type depending on product. `iqs624_pos_notifier()` handles reset reinitialization and emits IIO change events on angle changes. IIO callbacks provide raw angle, scale, and event enable control.

## Control Flow
Probe gets the parent `iqs62x_core`, allocates IIO state, registers a notifier with the MFD event chain, installs a devm unregister action, and registers the IIO device. Event enable writes snapshot the current angle, update event masks, and cache enabled state. Notifier callbacks compare incoming angle/interval values and push IIO change events.

## State And Persistence
Driver state is RAM-only. Hardware event mask is changed when events are enabled/disabled and is restored after system reset events from the MFD notifier.

## Dependencies And Integration Points
Uses `linux/mfd/iqs62x.h`, regmap, blocking notifier chains, and IIO event APIs. Registers as platform driver `iqs624-pos`.

## Risks And Test Signals
Concurrency around event enable and notifier is protected by a mutex. Test IQS624 vs IQS625 product paths, scale derived from interval divisor, event enable/disable, reset notifier reinitialization, and notifier unregister devm action.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/position/iqs624-pos.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Kconfig

## Purpose
Kconfig menu for digital potentiometer IIO drivers.

## Important APIs, Types, And Functions
Defines tristate symbols for AD5110, AD5272, DS1803, MAX5432, MAX5481, MAX5487, MCP4018, MCP4131, MCP4531, MCP41010, TPL0102, and X9250. Dependencies select the required bus, mostly I2C or SPI; `TPL0102` selects `REGMAP_I2C`.

## Control Flow
Enabling a symbol causes the corresponding Makefile object to build. Help text names the produced module for each driver.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
This is the build-selection entry point for the potentiometer directory.

## Risks And Test Signals
Build-test all symbols as modules and built-ins, especially ordering and required bus/regmap dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Makefile

## Purpose
Kbuild object mapping for digital potentiometer drivers.

## Important APIs, Types, And Functions
Maps each Kconfig symbol to its `.o` file: `ad5110.o`, `ad5272.o`, `ds1803.o`, `max5432.o`, `max5481.o`, `max5487.o`, `mcp4018.o`, `mcp4131.o`, `mcp4531.o`, `mcp41010.o`, `tpl0102.o`, and `x9250.o`.

## Control Flow
Kbuild includes objects conditionally based on `obj-$(CONFIG_...)`.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the potentiometer Kconfig file.

## Risks And Test Signals
Build tests should confirm each module is emitted under the documented module name.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5110.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5110.c

## Purpose
I2C IIO driver for Analog Devices AD5110/AD5112/AD5114 digital potentiometers, including RDAC control, shutdown enable, EEPROM store, and tolerance-adjusted scale.

## Important APIs, Types, And Functions
`struct ad5110_cfg` defines max positions, resistance, and bit shift per variant. `struct ad5110_data` stores client, tolerance, enable state, mutex, config, and DMA-safe buffer. `ad5110_read()` and `ad5110_write()` serialize two-byte I2C command transfers. `ad5110_resistor_tol()` reads EEPROM tolerance and folds it into scale/offset calculations. `store_eeprom_show/store()` expose a sysfs attribute to read EEPROM wiper and persist RDAC to EEPROM. IIO callbacks expose raw, offset, scale, and enable.

## Control Flow
Probe sets default enabled state, resets RDAC from EEPROM, reads resistor tolerance, configures one output resistance channel, and registers IIO. Raw writes validate range and shift user positions into device encoding. Enable writes send shutdown commands.

## State And Persistence
EEPROM is read during probe and can be written through `store_eeprom`; RDAC is volatile unless stored. Driver caches tolerance and enable state.

## Dependencies And Integration Points
Uses I2C master transfers, IIO sysfs attributes, mutexes, and OF/I2C match data for variant config.

## Risks And Test Signals
EEPROM writes take time and wear nonvolatile storage. Test variant position shifts, tolerance sign handling, shutdown enable toggles, EEPROM store/read attribute, invalid raw values, and I2C short transfer handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5272.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5272.c

## Purpose
I2C IIO driver for Analog Devices AD5272/AD5274 digital potentiometers.

## Important APIs, Types, And Functions
`struct ad5272_cfg` defines max position, resistance, and shift for 10-bit or 8-bit variants. `ad5272_write()` and `ad5272_read()` implement the two-byte command framing. `ad5272_reset()` uses an optional reset GPIO or device reset command. Probe resets the part and enables RDAC writes through the control register. IIO callbacks expose raw and scale.

## Control Flow
Probe allocates IIO state, selects config from I2C ID data, resets the chip, writes `AD5272_RDAC_WR_EN`, then registers a single output resistance channel. Raw writes validate integer range and shift values for AD5274 devices.

## State And Persistence
The driver programs volatile RDAC state and does not expose EEPROM/50-TP programming. No cached wiper state.

## Dependencies And Integration Points
Uses I2C, optional GPIO reset, and OF/I2C match tables.

## Risks And Test Signals
The OF table stores enum values while probe uses I2C ID data, so OF-only probing should be checked. Test reset GPIO and command paths, write-enable failure, raw read/write at range boundaries, and 8-bit variant shifting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ad5272.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ds1803.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ds1803.c

## Purpose
I2C IIO driver for Maxim DS1803 dual digital potentiometers and DS3502 single potentiometer.

## Important APIs, Types, And Functions
`struct ds1803_cfg` captures wiper count, raw availability range, resistance, channel table, and chip-specific read callback. `ds1803_read()` bulk-receives both DS1803 wipers; `ds3502_read()` reads the IVR register. IIO callbacks expose raw, scale, writable raw, and raw availability.

## Control Flow
Probe selects config from match data, assigns the correct channel table/count, and registers IIO. Read and write paths use channel address to select the appropriate wiper register.

## State And Persistence
Driver has no cache. It writes device wiper registers; persistence depends on chip behavior outside this driver and no explicit EEPROM operation is exposed.

## Dependencies And Integration Points
Uses I2C SMBus byte-data writes and either I2C master receive or SMBus byte-data reads, depending on part.

## Risks And Test Signals
DS1803 read returns transfer length on success and the driver treats nonnegative as OK; short reads are not explicitly rejected. Test both channel counts, availability ranges, DS3502 register addressing, invalid writes, and bus error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/ds1803.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5432.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5432.c

## Purpose
I2C IIO driver for Maxim MAX5432-MAX5435 digital potentiometers.

## Important APIs, Types, And Functions
`struct max5432_data` stores the I2C client and nominal resistance from OF match data. The single IIO channel is an output resistance channel. `max5432_read_raw()` exposes scale only; `max5432_write_raw()` writes volatile wiper position using `MAX5432_CMD_VREG`.

## Control Flow
Probe reads resistance from `device_get_match_data()`, configures one channel, and registers IIO. Raw writes validate 0-31 and left-shift into D7-D3 as required by the device.

## State And Persistence
No readback/cache and no nonvolatile update. Writes target the active volatile register.

## Dependencies And Integration Points
Uses I2C SMBus byte-data writes and OF compatibles for resistance selection.

## Risks And Test Signals
There is no I2C ID table, so OF matching is the expected path. Test scale for 50k/100k variants, raw boundary values, invalid fractional writes, and behavior on systems without match data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5432.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5481.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5481.c

## Purpose
SPI IIO driver for Maxim MAX5481-MAX5484 single-channel digital potentiometers.

## Important APIs, Types, And Functions
`struct max5481_cfg` stores resistance; `struct max5481_data` stores SPI device, config, and aligned message buffer. `max5481_write_cmd()` frames write-wiper and nonvolatile copy commands. IIO callbacks expose scale and writable raw position.

## Control Flow
Probe selects config from OF or SPI ID, restores the wiper from nonvolatile memory with `COPY_NV_TO_AB`, registers a devm action to save the wiper to nonvolatile memory on teardown, and registers a single output resistance channel.

## State And Persistence
The driver intentionally copies NV to volatile at probe and volatile to NV on driver teardown. It does not cache the wiper or expose readback.

## Dependencies And Integration Points
Uses SPI, OF/SPI ID match tables, IIO direct mode, and devm cleanup actions.

## Risks And Test Signals
Automatic save on removal writes nonvolatile memory and may be surprising for tests or users. Test command framing for 10-bit values, restore/save commands, variant resistance selection, and raw range rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5481.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5487.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5487.c

## Purpose
SPI IIO driver for Maxim MAX5487/MAX5488/MAX5489 dual digital potentiometers.

## Important APIs, Types, And Functions
`struct max5487_data` stores SPI device and resistance. `max5487_write_cmd()` sends 16-bit command words. Two IIO output resistance channels map to wiper A and B. Read callbacks expose scale; write callbacks set volatile wiper positions.

## Control Flow
Probe allocates and registers an IIO device with two channels, restores both wipers from NV memory, and uses non-devm `iio_device_register()`. Remove unregisters IIO and attempts to copy both volatile wipers back to NV memory.

## State And Persistence
Volatile wiper changes are saved to nonvolatile registers during remove. No cached readback.

## Dependencies And Integration Points
Uses SPI, SPI ID table, and ACPI IDs for variant resistance selection.

## Risks And Test Signals
Command endianness depends on how the 16-bit command is laid out for SPI transfer. Nonvolatile save on remove may wear storage. Test restore/save behavior, both channels, ACPI/SPI IDs, raw range rejection, and remove warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/max5487.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4018.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4018.c

## Purpose
I2C IIO driver for Microchip MCP4017/MCP4018/MCP4019 single-wiper digital potentiometers.

## Important APIs, Types, And Functions
`struct mcp4018_cfg` stores nominal resistance. IIO callbacks read/write raw wiper values via SMBus byte operations and expose scale using `MCP4018_WIPER_MAX`.

## Control Flow
Probe verifies `I2C_FUNC_SMBUS_BYTE`, selects config from match data, creates one output resistance channel, and registers IIO.

## State And Persistence
No driver cache and no explicit nonvolatile operation. Wiper state is read directly from the device.

## Dependencies And Integration Points
Uses I2C SMBus byte transfers and broad OF/I2C match tables for resistance variants.

## Risks And Test Signals
Test adapter functionality rejection, all resistance variants, raw boundaries 0-127, readback after write, and OF/I2C match-data availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp41010.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp41010.c

## Purpose
SPI IIO driver for Microchip MCP41xxx/MCP42xxx volatile digital potentiometers.

## Important APIs, Types, And Functions
`struct mcp41010_cfg` defines name, wiper count, and resistance. `struct mcp41010_data` stores SPI device, config, mutex, cached wiper values, and transmit buffer. IIO callbacks expose cached raw values and scale; raw writes send two-byte SPI commands.

## Control Flow
Probe selects config from OF or SPI ID, initializes the mutex, uses one or two channels based on config, and registers IIO. Raw writes validate 0-255, serialize SPI transfer, and update the cache only on success.

## State And Persistence
The device has no readback path in this driver; raw reads return the software cache initialized to zero at probe. No nonvolatile state.

## Dependencies And Integration Points
Uses SPI and OF/SPI ID matching.

## Risks And Test Signals
Cache starts at zero and may not reflect hardware power-on state. Test one- and two-wiper variants, write/read cache consistency, SPI error not updating cache, scale reporting, and channel command bit selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp41010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4131.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4131.c

## Purpose
SPI IIO driver for a large family of Microchip MCP413x/414x/415x/416x/423x/424x/425x/426x digital potentiometers.

## Important APIs, Types, And Functions
`struct mcp4131_cfg` captures wiper count, max position, and resistance. `mcp4131_read()` performs full-duplex SPI read framing. IIO raw reads send a read command, check the command-error bit, and decode 8/9-bit values. Raw writes build the address/command bytes and write over SPI. Large OF and SPI ID tables map many resistance/family variants to configs.

## Control Flow
Probe selects config from OF or SPI ID, initializes the mutex, configures channel count, and registers IIO. Each raw access serializes SPI buffer use with `lock`.

## State And Persistence
No software cache. Reads query volatile wiper registers. A TODO notes EEPROM-capable models are not persisted by this driver.

## Dependencies And Integration Points
Uses SPI, IIO direct mode, and extensive OF/SPI device matching.

## Risks And Test Signals
Command-error interpretation is critical; tests should exercise invalid address/command responses if possible. Verify 128/256 max-position variants, one/two channels, read/write framing, OF vs SPI ID selection, and absence of EEPROM persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4131.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4531.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4531.c

## Purpose
I2C IIO driver for Microchip MCP45xx/MCP46xx one- and two-wiper digital potentiometers.

## Important APIs, Types, And Functions
`struct mcp4531_cfg` defines wiper count, raw availability range, and resistance for many variants. IIO callbacks read raw with `i2c_smbus_read_word_swapped()`, write raw with `i2c_smbus_write_byte_data()`, expose scale, and return raw availability ranges. ID and OF tables map many part/resistance suffixes to configs.

## Control Flow
Probe verifies `I2C_FUNC_SMBUS_WORD_DATA`, selects config, sets the channel count to one or two, and registers IIO. Raw operations compute a wiper address from `chan->channel << MCP4531_WIPER_SHIFT`.

## State And Persistence
No cache and no explicit EEPROM operation. Reads query device registers; writes set volatile wipers through the write command.

## Dependencies And Integration Points
Uses I2C SMBus word-data support and IIO direct-mode callbacks.

## Risks And Test Signals
The write command sends high address bits in the command byte and low bits as data; range tests should include 8- and 9-bit variants. Test SMBus functionality rejection, availability ranges, one/two channels, OF/I2C match-data selection, and readback after writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/mcp4531.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/tpl0102.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/tpl0102.c

## Purpose
I2C regmap IIO driver for TI TPL0102/TPL0401 and ON Semiconductor CAT5140 digital potentiometers.

## Important APIs, Types, And Functions
`struct tpl0102_cfg` stores wiper count, raw availability range, and resistance. `tpl0102_regmap_config` is a simple 8-bit register/value map. IIO callbacks read/write channel registers through regmap, expose scale, and return raw availability.

## Control Flow
Probe selects config from I2C ID data, initializes I2C regmap, configures one or two channels according to the variant, and registers IIO.

## State And Persistence
No software cache and no exposed high-impedance control despite the TODO. Wiper state is device register state.

## Dependencies And Integration Points
Depends on I2C and `REGMAP_I2C` selected by Kconfig. Uses I2C ID matching only in this source.

## Risks And Test Signals
Scale uses `avail[2] + 1`, unlike several other potentiometer drivers. Test each variant's channel count and range, regmap error propagation, raw boundary rejection, and scale denominator expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/tpl0102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/x9250.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiometer/x9250.c

## Purpose
SPI IIO driver for Renesas X9250 quad controlled potentiometers.

## Important APIs, Types, And Functions
`struct x9250_cfg` defines variant name and resistance. `struct x9250` stores SPI device, config, and optional write-protect GPIO. `x9250_write8()` and `x9250_read8()` frame device ID plus command bytes. Four IIO output resistance channels map to WCR0-WCR3.

## Control Flow
Probe enables `vcc`, `avp`, and `avn` regulators, waits for power-up, allocates IIO state, gets variant config and optional `wp` GPIO, then registers four channels. Raw writes deassert write protect, send the WCR write command, and reassert write protect.

## State And Persistence
Reads query wiper control registers. Writes update WCR state; the driver does not expose store/recall of nonvolatile data. Regulator enable is devm-managed by bulk helper.

## Dependencies And Integration Points
Uses SPI, regulator bulk get-enable, optional GPIO, OF/SPI IDs, and IIO availability ranges.

## Risks And Test Signals
The module description says ALSA SoC, likely copy/paste. Test regulator failure handling, power-up delay, optional write-protect polarity, all four channels, raw range 0-255, and scale for X9250T/X9250U.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiometer/x9250.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Kconfig

## Purpose
Kconfig menu for digital potentiostat drivers.

## Important APIs, Types, And Functions
Defines `CONFIG_LMP91000` for the Texas Instruments LMP91000 potentiostat driver. It depends on I2C and selects `REGMAP_I2C`, `IIO_BUFFER`, `IIO_BUFFER_CB`, and `IIO_TRIGGERED_BUFFER`.

## Control Flow
Enabling the option builds `lmp91000.o` via the Makefile. Help text documents module name `lmp91000`.

## State And Persistence
No runtime state; build-time selection only.

## Dependencies And Integration Points
Ensures the potentiostat driver has regmap and buffered IIO support.

## Risks And Test Signals
Build-test module and built-in configurations to confirm selected buffer dependencies cover the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Makefile

## Purpose
Kbuild rule for IIO potentiostat drivers.

## Important APIs, Types, And Functions
Maps `CONFIG_LMP91000` to `lmp91000.o`.

## Control Flow
Kbuild includes the object when the Kconfig symbol is enabled.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Pairs with the potentiostat Kconfig entry.

## Risks And Test Signals
Compile with `CONFIG_LMP91000=m/y` to verify object inclusion and module naming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/Makefile -->
