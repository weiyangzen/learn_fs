# subset-b-003891 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c

Purpose: trigger, IRQ, and FIFO enablement support for the InvenSense MPU6050/MPU9x50 IIO driver. It decides which sensor engines feed the FIFO, arms data-ready interrupts, captures IRQ timestamps, and forwards raw data-ready and wake-on-motion events to IIO.

Important APIs/functions: `inv_mpu6050_prepare_fifo()` is exported to reset and arm/disarm the hardware FIFO. `inv_mpu6050_probe_trigger()` allocates the IIO trigger and threaded IRQ. Internal helpers include `inv_scan_query_mpu6050()`, `inv_scan_query_mpu9x50()`, `inv_mpu6050_set_enable()`, and the IRQ top/thread handlers.

Control flow: trigger enable queries the active scan mask, resumes runtime PM, switches off unneeded engines except WoM, enables selected engines, computes initial skip samples, resets FIFO, programs `fifo_en`, enables FIFO reads through `user_ctrl`, and sets data-ready interrupt enable. Trigger disable clears all FIFO-enable booleans, disables the data-ready interrupt, clears `fifo_en`, restores `user_ctrl`, and releases runtime PM. The hard IRQ stores `it_timestamp`; the thread acknowledges status where needed, pushes WoM events, and calls `iio_trigger_poll_nested()` for raw data-ready.

State and persistence: persistent state is in `struct inv_mpu6050_state`: `chip_config.*_fifo_enable`, `skip_samples`, `it_timestamp`, runtime PM state, FIFO/user-control register state, and WoM enablement. The code preserves `chip_config.user_ctrl` when disabling FIFO.

Dependencies and integration: depends on the MPU core header for register definitions and engine switching, regmap, runtime PM, IIO triggers/events, and `inv_sensors_timestamp_reset()`. It is called by the main MPU probe path after IRQ discovery.

Risks: `inv_mpu_data_rdy_trigger_set_state()` calls `inv_mpu6050_set_enable()` twice with the same state, which looks accidental and can double-run PM/FIFO transitions. MPU6000/6050 bypass interrupt-status reads by assuming data-ready. MPU9x50 magnetometer operation skips the first sample and depends on `magn_disabled` auxiliary-bus state. Error paths rely on autosuspend cleanup after partially enabled engines.

Test signals: IIO buffer enable/disable, runtime PM reference balance, FIFO reset and `fifo_en` programming, IRQ timestamp monotonicity, WoM event delivery, magnetometer first-sample skip, and trigger-only operation with no active scan mask.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/inv_mpu6050/inv_mpu_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c

Purpose: complete I2C IIO driver for Kionix KMX61, exposing accelerometer and magnetometer as two IIO devices with raw reads, scale/ODR sysfs, data-ready triggers, buffered capture, and accelerometer any-motion threshold events.

Important APIs/types/functions: `struct kmx61_data` stores shared I2C client, mutex, standby/power flags, range/ODR/wake settings, two `iio_dev` instances, and three triggers. Core helpers are `kmx61_set_mode()`, `kmx61_set_odr()`, `kmx61_set_scale()`, `kmx61_chip_init()`, `kmx61_setup_new_data_interrupt()`, `kmx61_setup_any_motion_interrupt()`, `kmx61_set_power_state()`, `kmx61_read_raw()`, event callbacks, trigger callbacks, `kmx61_probe()`, remove, and PM hooks.

Control flow: probe allocates shared driver data, creates separate accel and magn IIO devices, validates WHO_AM_I, initializes range/ODR/wake defaults, optionally requests one IRQ and allocates accel data-ready, magnetometer data-ready, and motion triggers, then registers both IIO devices with runtime autosuspend. Raw reads power the selected sensor, read a 16-bit SMBus word, sign-extend according to channel shift/realbits, and autosuspend. ODR and scale changes put both sensors in standby before writing configuration. IRQ top-half polls enabled triggers, while the threaded handler reads motion status bits, pushes per-axis rising/falling threshold events, resets the interrupt latch, and reads `INL`.

State and persistence: `acc_stby`/`mag_stby` mirror hardware standby; `acc_ps`/`mag_ps` track runtime PM logical users; `range`, `odr_bits`, `wake_thresh`, and `wake_duration` mirror configuration. Suspend forces both sensors to standby without updating saved standby state; resume restores saved standby bits. Runtime suspend updates standby state and runtime resume reconstructs standby from power-state booleans.

Dependencies and integration: depends on I2C SMBus byte/word access, IIO sysfs/events/triggers/triggered buffers, runtime PM, and an optional client IRQ. The driver has an I2C ID table for `kmx611021`.

Risks: most configuration requires both sensors in standby, so failures after entering standby can leave hardware disabled or software mirrors stale. `kmx61_set_power_state()` updates power booleans before runtime PM calls. Motion event config refuses threshold changes while enabled but trigger/event interactions share `motion_trig_on` and `ev_enable_state`. Buffer pushes do not include the pollfunc timestamp despite using `iio_pollfunc_store_time`.

Test signals: probe WHO_AM_I, accel and magn raw reads, scale and sampling-frequency writes across supported tables, runtime autosuspend/resume, three trigger enable states, any-motion threshold events per axis/direction, IRQ latch clearing, and remove/suspend restoring standby.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/kmx61.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi240.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi240.c

Purpose: Bosch SMI240 SPI IIO driver for a 6-axis IMU plus temperature. It implements the device's out-of-frame 32-bit SPI protocol through a custom regmap bus, exposes raw data and filter bandwidth settings, and supports triggered buffered capture.

Important APIs/types/functions: `struct smi240_data` contains regmap, accelerometer/gyro filter frequencies, built-in self-test count, capture mode, aligned IIO buffer, and aligned SPI frame buffer. Key functions are `smi240_crc3()`, `smi240_sensor_data_is_valid()`, custom regmap `read`/`write`, `smi240_soft_reset()`, `smi240_soft_config()`, `smi240_get_data()`, `smi240_trigger_handler()`, raw read/write callbacks, `smi240_init()`, and `smi240_probe()`.

Control flow: probe allocates the IIO device, installs custom regmap bus ops, stores the IIO device as SPI drvdata for bus callbacks, reads chip ID, soft-resets, writes soft configuration with default high bandwidth and self-test repetition count, sets channel metadata, registers a triggered buffer, and registers the IIO device. Regmap reads emit one request frame, then read the response in the next SPI frame and validate CRC/status bits. Filter writes update cached bandwidth, then reset and rewrite soft configuration because soft config is locked until reset. The trigger handler enables capture for the first frame, reads active channels from capture registers, disables capture after the first read, and pushes a timestamped scan.

State and persistence: filter frequencies and BIST count are software state mirrored into `SOFT_CONFIG`; capture mode changes how read request frames are encoded. The hardware soft config persists until hard or soft reset. The SPI frame buffer is DMA-aligned and reused for all regmap transactions.

Dependencies and integration: depends on SPI, regmap with 8-bit registers/16-bit native-endian values, IIO triggered buffers, unaligned/bitfield helpers, and OF/SPI IDs for `bosch,smi240`/`smi240`.

Risks: the out-of-frame SPI protocol requires chip-select toggling and exact request/response sequencing. CRC/status validation returns `-EIO` for protocol errors. `smi240_trigger_handler()` turns capture off inside the loop after the first channel read, so multi-channel capture correctness depends on device semantics for latched capture registers. Bandwidth writes are disruptive resets with long startup/self-test delays.

Test signals: CRC rejection tests, chip-ID read, soft-reset/config timing, bandwidth read/write for accel and gyro, raw temp/accel/gyro reads, triggered buffer scans with all channels enabled, and SPI bus traces showing two-frame reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi240.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig

Purpose: Kconfig entries for the Bosch SMI330 6-axis IMU core and I2C/SPI bus frontends.

Important symbols: hidden `SMI330` selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`; visible `SMI330_I2C` depends on `I2C`, selects `SMI330` and `REGMAP_I2C`; visible `SMI330_SPI` depends on `SPI`, selects `SMI330` and `REGMAP_SPI`.

Control flow: enabling either bus option pulls in the shared core and the relevant regmap backend. Module names in help text are `smi330_i2c` and `smi330_spi`.

State and persistence: no runtime state; this controls build-time object inclusion.

Dependencies and integration: integrates the new SMI330 driver with the IIO and regmap build system.

Risks: the hidden core has no prompt, so it must always be selected by a bus frontend. Missing IRQ dependency is acceptable because the core can operate in polling/direct mode.

Test signals: `allyesconfig`/module builds for I2C-only, SPI-only, both enabled, and both disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile

Purpose: object mapping for the Bosch SMI330 IMU driver.

Important entries: `obj-$(CONFIG_SMI330) += smi330_core.o`, `obj-$(CONFIG_SMI330_I2C) += smi330_i2c.o`, and `obj-$(CONFIG_SMI330_SPI) += smi330_spi.o`.

Control flow: Kconfig selections decide whether the shared core and each transport frontend are built in or as modules.

State and persistence: no runtime state.

Dependencies and integration: pairs with `Kconfig`; bus modules import the `IIO_SMI330` namespace exported by the core.

Risks: if a bus object were built without the core symbol, namespace/probe references would fail; Kconfig selection prevents that.

Test signals: kernel/module build with each SMI330 configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330.h

Purpose: shared public header between SMI330 bus frontends and the common core.

Important APIs/types: defines scan indexes for accelerometer X/Y/Z, gyro X/Y/Z, timestamp, and `SMI330_SCAN_LEN`. Declares exported `smi330_regmap_config` and `smi330_core_probe()`.

Control flow: I2C and SPI probes initialize a bus-specific regmap, then call `smi330_core_probe(dev, regmap)`.

State and persistence: no owned runtime state; scan indexes define the ABI between channel specs, buffer storage, and bus buffer sizing.

Dependencies and integration: includes IIO declarations and relies on forward-visible `struct device`/`struct regmap` usage through included kernel headers.

Risks: `SMI330_SCAN_LEN = SMI330_SCAN_TIMESTAMP` intentionally excludes the timestamp slot from hardware bulk reads; buffer sizes must preserve that convention.

Test signals: compile coverage by both bus frontends and buffer scans containing six data channels plus soft timestamp.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c

Purpose: shared Bosch SMI330 IIO core. It defines register layout, channels, attributes, raw data/config sysfs, interrupt/trigger handling, device initialization, and the exported core probe used by I2C and SPI frontends.

Important APIs/types/functions: `struct smi330_data` owns regmap, operation/IRQ config, trigger, and aligned buffer. `smi330_regmap_config` exports 8-bit registers and 16-bit little-endian values. Important functions include `smi330_get/set_sensor_config()`, `smi330_get_data()`, `smi330_read_avail()`, `smi330_read_raw()`, `smi330_write_raw()`, `smi330_soft_reset()`, trigger and IRQ handlers, `smi330_register_irq()`, `smi330_set_drdy_trigger_state()`, `smi330_dev_init()`, and `smi330_core_probe()`.

Control flow: core probe soft-resets, initializes IIO metadata, validates chip/error/POR status, puts accel and gyro into normal mode, attempts named firmware IRQ lookup for `INT1` then `INT2`, optionally creates a data-ready trigger, sets it as the default trigger, installs a triggered buffer, and registers the IIO device. Raw reads claim direct mode and read signed 16-bit samples. Config writes map user values to register fields and check the error register for accel/gyro config errors. Data-ready trigger enable maps accel and gyro DRDY onto the selected interrupt pin; the threaded IRQ reads status and polls the nested trigger; the poll handler bulk reads six data registers and pushes a timestamped buffer.

State and persistence: `cfg.op_mode` records polling vs data-ready, `cfg.data_irq` records selected interrupt output, and hardware config registers persist ODR/range/bandwidth/averaging/mode. Buffer storage is per-device and aligned by IIO helper macros.

Dependencies and integration: uses regmap, fwnode named IRQs, irq trigger-type inspection, optional `drive-open-drain` firmware property, IIO triggered buffers, and bus frontends importing namespace `IIO_SMI330`.

Risks: unknown chip IDs are informational rather than fatal, while fatal error/POR checks are fatal. `smi330_read_raw()` assigns `*val` twice in the temperature scale path. `smi330_write_raw_get_fmt()` returns micro format for non-scale integer controls even though callers pass integers. IRQ setup requires supported trigger types and named `INT1`/`INT2`; without IRQ the device remains usable through direct/polled reads.

Test signals: probe on I2C/SPI, POR/fatal-error handling, raw temp/accel/gyro reads, available attribute lists, writes for range/ODR/BW/averaging including error-register rejection, named IRQ discovery, data-ready buffer capture, and open-drain/level/edge IRQ configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c

Purpose: Bosch SMI330 I2C transport frontend. It adapts the device's I2C framing and dummy bytes into regmap operations and delegates all sensor behavior to `smi330_core_probe()`.

Important APIs/types/functions: `struct smi330_i2c_priv` stores the I2C client and a maximum-size receive buffer. `smi330_regmap_i2c_read()` performs a two-message register-address write plus read with two dummy bytes stripped. `smi330_regmap_i2c_write()` uses SMBus block write. `smi330_i2c_probe()` allocates private state, initializes custom regmap, and calls the core.

Control flow: probe constructs a `regmap_bus` over the private context. Read validates the requested size against the fixed receive buffer, issues `i2c_transfer()`, copies data after dummy bytes, and returns success. Write extracts the first byte as the register address and sends the remaining bytes as payload.

State and persistence: transport state is limited to `priv->i2c` and reusable `rx_buffer`; all device configuration lives in the core and hardware.

Dependencies and integration: depends on I2C, regmap custom bus, OF compatible `bosch,smi330`, I2C ID `smi330`, and namespace import `IIO_SMI330`.

Risks: `i2c_transfer()` success is not checked for a short positive transfer count; any nonnegative return is treated as success. Buffer size is tailored to the six-channel scan length plus dummy bytes, so larger future bulk reads would fail with `-EINVAL`.

Test signals: I2C probe, register reads with dummy-byte stripping, block writes of 16-bit little-endian values, scan-length bulk read, and OF/I2C modalias matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c

Purpose: Bosch SMI330 SPI transport frontend. It provides custom regmap bus operations for SPI framing and delegates sensor setup to the shared SMI330 core.

Important APIs/functions: `smi330_regmap_spi_read()` inserts one pad byte after the register address and uses `spi_write_then_read()`. `smi330_regmap_spi_write()` writes the regmap frame directly. `smi330_spi_probe()` creates the regmap with `read_flag_mask = 0x80` and calls `smi330_core_probe()`.

Control flow: SPI probe initializes regmap over the SPI device, then shared core handles reset, validation, IRQ, buffer, and IIO registration. Reads require a one-byte regmap register buffer, add a dummy byte, and read the requested value bytes.

State and persistence: no transport-private persistent state beyond the SPI device/regmap.

Dependencies and integration: depends on SPI, regmap custom bus, OF compatible `bosch,smi330`, SPI ID `smi330`, and namespace import `IIO_SMI330`.

Risks: read path rejects unexpected register-buffer sizes and logs through the SPI device. Protocol correctness depends on the read flag mask and dummy-byte behavior matching the hardware.

Test signals: SPI modalias/OF matching, read/write regmap traces, core probe via SPI, bulk data read, and module namespace resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/smi330/smi330_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig

Purpose: Kconfig for the ST LSM6DSx family IMU driver and its I2C, SPI, and I3C frontends.

Important symbols: `IIO_ST_LSM6DSX` is the shared core and depends on at least one of I2C/SPI/I3C, selecting IIO buffer, triggered buffer, and kfifo buffer support. `IIO_ST_LSM6DSX_I2C`, `_SPI`, and `_I3C` depend on the relevant bus and core, default to enabled when bus/core are enabled, and select matching regmap backends.

Control flow: selecting the core builds `st_lsm6dsx.o`; selecting frontends builds bus modules that call the exported core probe.

State and persistence: no runtime state; this controls build-time inclusion for a broad device list.

Dependencies and integration: integrates with IIO, regmap, I2C, SPI master, and I3C subsystem options.

Risks: the core depends on any bus but no frontend is strictly selected by the core; users can select core without an interface if defaults are overridden. The supported device list must stay in sync with match tables and core settings.

Test signals: config/build matrix for I2C, SPI, I3C, all buses, and no frontend; help text device names matching module aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile

Purpose: build rules for the ST LSM6DSx family.

Important entries: composite `st_lsm6dsx-y` contains `st_lsm6dsx_core.o`, `st_lsm6dsx_buffer.o`, and `st_lsm6dsx_shub.o`. Bus objects are `st_lsm6dsx_i2c.o`, `st_lsm6dsx_spi.o`, and `st_lsm6dsx_i3c.o`.

Control flow: `CONFIG_IIO_ST_LSM6DSX` builds the shared composite object; bus Kconfig symbols build transport modules separately.

State and persistence: no runtime state.

Dependencies and integration: aligns exported namespace `IIO_LSM6DSX` from the core with module imports in bus frontends.

Risks: core, FIFO, and sensor-hub code are always linked together; Kconfig must keep required buffer dependencies selected.

Test signals: module link for core plus each transport and namespace import/export resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h

Purpose: central type, constant, channel, and helper contract for the ST LSM6DSx core, FIFO buffer, sensor-hub, and bus modules.

Important APIs/types: defines device-name constants and `enum st_lsm6dsx_hw_id`; channel macros; register descriptor structs; ODR, full-scale, FIFO, timestamp, shub, event, and whole-device settings structs; sensor IDs; `struct st_lsm6dsx_sensor`; `struct st_lsm6dsx_hw`; exported PM ops and core/helper prototypes; locked regmap helper inlines; mount-matrix ext info; and `st_lsm6dsx_device_set_enable()` dispatching internal sensors vs external shub sensors.

Control flow: bus probes call `st_lsm6dsx_probe()`. Core allocates `st_lsm6dsx_hw` and per-sensor `iio_dev`/`st_lsm6dsx_sensor` objects based on settings tables. Buffer and shub code operate on shared masks, locks, and settings through this header.

State and persistence: `st_lsm6dsx_hw` persists device-wide regmap, IRQ, locks, suspend/enable/FIFO masks, timestamp gain, pattern sizes, event state, IIO device array, orientation, and aligned scan buffers. Each sensor stores ODR, FIFO ODR, gain, watermark, decimator, samples-in-pattern, timestamp reference, and external sensor metadata.

Dependencies and integration: depends on IIO, regulator, device property/platform data conventions, regmap through forward declarations, and common ST sensor platform data in users.

Risks: many behavior differences are data-driven by large settings tables, so incorrect register masks or IDs affect multiple files. The inline locked helpers serialize page-sensitive regmap accesses but callers that directly use regmap must manage page state. External sensors are represented in the same enable/FIFO masks as internal sensors, making ID boundaries important.

Test signals: compile coverage across core/buffer/shub/bus modules, all supported device IDs matching settings entries, mount-matrix ext info exposure, sensor enable dispatch for internal vs external IDs, and lockdep coverage around page/fifo/conf locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c

Purpose: hardware FIFO support for ST LSM6DSx devices. It configures FIFO ODR, decimators, watermarks, hardware timestamps, and reads both legacy pattern FIFOs and newer tagged FIFOs into IIO buffers.

Important APIs/functions: exported `st_lsm6dsx_update_watermark()`, `st_lsm6dsx_resume_fifo()`, `st_lsm6dsx_read_fifo()`, `st_lsm6dsx_read_tagged_fifo()`, `st_lsm6dsx_flush_fifo()`, `st_lsm6dsx_update_fifo()`, and `st_lsm6dsx_fifo_setup()`. Internal helpers compute decimator values, pattern sample counts, FIFO mode/ODR, timestamp reset, block reads, tagged sample routing, and buffer sysfs `sampling_frequency`.

Control flow: buffer preenable calls device-specific `update_fifo(sensor, true)`. `st_lsm6dsx_update_fifo()` under `conf_lock` optionally flushes existing FIFO, enables the sensor, programs FIFO ODR, recomputes decimators/SIP, updates watermark, resumes FIFO, and updates `fifo_mask`. IRQ handling in core calls the settings-selected read routine. Pattern FIFO reads status, rounds length to whole patterns, reads pattern chunks, reconstructs gyro/accel/ext samples and timestamp samples, discards settling samples, and pushes timestamped scans. Tagged FIFO reads tagged tuples, decodes source tags, updates timestamp on timestamp tags, and routes data tags to the correct IIO device.

State and persistence: updates `hw->fifo_mask`, `hw->sip`, `hw->ts_sip`, per-sensor `sip`, `decimator`, `samples_to_discard`, `watermark`, `hwfifo_odr_mHz`, and `ts_ref`. Hardware FIFO mode, watermark registers, decimator registers, and timestamp counter state persist until reconfigured or reset.

Dependencies and integration: depends on `st_lsm6dsx.h` settings callbacks and locks, regmap, IIO kfifo buffers, scan buffers in `st_lsm6dsx_hw`, and core IRQ dispatch.

Risks: pattern math is sensitive to ODR ratios, decimators, timestamp sample insertion, and ext sensor ordering. Watermark writes combine high-register existing bits with a 16-bit bulk write. The source has duplicated/extra braces and duplicate `case ST_LSM6DSX_EXT2_TAG` lines in the viewed copy, which are compile-risk signals if not masked by local context. FIFO flush ignores the return from the read routine and then bypasses FIFO.

Test signals: enabling/disabling accel, gyro, and external FIFO channels; watermark clamping and register values; FIFO ODR sysfs; pattern FIFO with mismatched ODRs; tagged FIFO source routing; timestamp reset rollover handling; samples-to-discard behavior; and IRQ-driven FIFO drain loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c

Purpose: shared ST LSM6DSx family core. It contains the per-chip settings table, WHO_AM_I validation, sensor allocation, raw/config/event sysfs, power/reset/timer/shub initialization, IRQ handling, buffer setup selection, mount-matrix handling, registration, and suspend/resume.

Important APIs/functions: exported `st_lsm6dsx_set_page()`, `st_lsm6dsx_check_odr()`, `st_lsm6dsx_sensor_set_enable()`, `st_lsm6dsx_set_watermark()`, `st_lsm6dsx_probe()`, and `st_lsm6dsx_pm_ops`. Internal functions include WHOAMI lookup, full-scale/ODR setters, oneshot reads, event read/write/config, shub/timer/device init, IIO allocation, event reporting, threaded IRQ, software-trigger handler, IRQ setup, software-buffer setup, regulator init, suspend, and resume.

Control flow: transport probe passes bus regmap, IRQ, and hardware ID. Core allocates `st_lsm6dsx_hw`, initializes locks/regulators/buffer, verifies ID and WAI against settings, allocates accel and gyro IIO devices, resets and initializes hardware, probes external shub sensors when enabled, configures IRQ and hardware FIFO if an IRQ exists, otherwise configures software-triggered buffers, reads ACPI `ROTM` or generic mount matrix, registers every present IIO device, and enables wakeup if requested. Raw reads temporarily enable the sensor, wait settling time, read data, and disable it. ODR/gain writes update cached state or registers. IRQ thread reports enabled motion/tap events then drains FIFO until empty or error.

State and persistence: device-wide masks track enabled, FIFO-enabled, suspended, and event-enabled sensors. Per-sensor cached `odr`, `hwfifo_odr_mHz`, `gain`, and `watermark` control later hardware programming. Suspend disables enabled sensors unless used as wake event sources and stores `suspend_mask`; resume re-enables them and resumes FIFO. Regulator enablement and reset/boot operations persist for the lifetime of the device.

Dependencies and integration: depends on extensive settings tables, regmap, regulators, IIO, IIO ACPI/generic mount matrix helpers, ST platform data, IRQ trigger type handling, FIFO helpers, sensor-hub helpers, and bus modules importing `IIO_LSM6DSX`.

Risks: settings-table drift is the main correctness risk because all chip variants share the same code. `st_lsm6dsx_read_raw()` in the viewed source contains a duplicated `return -EBUSY;` after the direct-claim check. Event enable logic keeps accelerometer powered while events are active and can interact with FIFO users. IRQ setup rejects unsupported trigger types. Reset flushes FIFO first to avoid IRQ-line/I3C mode races.

Test signals: probe for each supported HW ID/WAI, regulator failure handling, raw reads, ODR/gain sysfs, event threshold/tap configuration and reporting, IRQ polarity/open-drain setup, hardware FIFO and software-trigger modes, sensor-hub discovery, mount matrix from ACPI and firmware properties, wakeup-source suspend/resume, and FIFO resume after PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c

Purpose: I2C frontend for the ST LSM6DSx family. It matches many OF/ACPI/I2C IDs, creates an 8-bit regmap, resolves hardware ID, and calls the shared core probe.

Important APIs/functions: `st_lsm6dsx_i2c_probe()` obtains match data or I2C ID driver data, initializes `devm_regmap_init_i2c()`, and calls `st_lsm6dsx_probe()`. Match tables enumerate all supported names and ACPI IDs `SMO8B30` and `SMOCF00`.

Control flow: device-tree match data takes precedence; fallback is the I2C device ID table. A missing hardware ID fails with `-EINVAL`. Successful regmap creation delegates IRQ, ID, and regmap to the core.

State and persistence: no transport-private state; core stores driver data on the device.

Dependencies and integration: depends on I2C, regmap I2C, OF/ACPI modalias matching, PM ops from the core, and namespace import `IIO_LSM6DSX`.

Risks: if neither firmware match data nor I2C ID data is present, probe fails. The long device table must remain synchronized with core settings and Kconfig help text.

Test signals: I2C probe for each compatible/name, ACPI matches, regmap initialization failure handling, IRQ forwarding, PM suspend/resume through imported PM ops, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c

Purpose: I3C frontend for ST LSM6DSx devices with known manufacturer/part IDs.

Important APIs/functions: `st_lsm6dsx_i3c_ids` maps I3C IDs to `ST_LSM6DSO_ID` and `ST_LSM6DSR_ID`. `st_lsm6dsx_i3c_probe()` initializes an 8-bit regmap with `devm_regmap_init_i3c()` and calls `st_lsm6dsx_probe(dev, 0, id, regmap)`.

Control flow: I3C core matches IDs, probe creates regmap, and core handles the rest with IRQ set to 0, causing software-triggered buffer setup when hardware FIFO IRQ is unavailable.

State and persistence: no frontend runtime state beyond regmap/core state.

Dependencies and integration: depends on I3C device APIs, regmap I3C, core PM ops, and namespace import `IIO_LSM6DSX`.

Risks: probe assumes `i3c_device_match_id()` returns an ID because the driver was matched. Passing IRQ 0 means no hardware IRQ/FIFO drain path from this frontend. Only two I3C IDs are listed.

Test signals: I3C modalias matching, regmap I3C read/write, software-trigger buffer operation, and PM callback linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_i3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c

Purpose: embedded sensor-hub support for LSM6DSx devices. It uses the IMU's auxiliary I2C master to detect and drive external magnetometers, exposing them as additional IIO devices and optionally batching them into the IMU FIFO.

Important APIs/functions: exported `st_lsm6dsx_shub_read_output()`, `st_lsm6dsx_shub_set_enable()`, and `st_lsm6dsx_shub_probe()`. Internal helpers handle page-muxed shub register reads/writes, masked writes, master enable, one-shot slave reads/writes, external ODR/full-scale configuration, SLV channel setup, raw read/write callbacks, IIO allocation, external-device initialization, and WAI probing.

Control flow: core initializes shub hardware, then `st_lsm6dsx_shub_probe()` walks the external-device table, tries each supported I2C address/WAI through SLV0, allocates an external IIO device on success, and initializes BDU/temp compensation/offset cancellation. Raw reads enable the shub channel, wait based on slave ODR, read the external register, then disable it. FIFO enable configures SLV1..3 channels for enabled external sensors, sets slave ODR/power, and enables the shub master using accelerometer as trigger.

State and persistence: each external `st_lsm6dsx_sensor` stores slave address, external settings pointer, slave ODR, mirrored accel-side ODR, gain, watermark, and ID. Hardware state includes secondary-page registers, SLV channel descriptors, external sensor power/ODR registers, and master enable.

Dependencies and integration: depends on core page locking, accelerometer sensor as the shub trigger, ext sensor settings for LIS2MDL and LIS3MDL, FIFO batching code, and IIO sysfs/buffer callbacks.

Risks: page switching and shub master enable are timing-sensitive. The viewed source contains an extra standalone `}` after `st_lsm6dsx_shub_write_reg_with_mask()` and a duplicate `case IIO_CHAN_INFO_RAW`, both compile-risk signals if present in the actual build. `st_lsm6dsx_shub_config_channels()` uses `sensor->ext_info.addr` while iterating enabled current sensors, so multi-external routing is worth reviewing. Failures after enabling the master can leave external state partially configured.

Test signals: WAI detection for LIS2MDL/LIS3MDL addresses, shub one-shot raw reads, external sampling-frequency and scale writes, FIFO batching of external channels, page-lock correctness, sensor-hub disable property, and suspend/resume with external sensors enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_shub.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c

Purpose: SPI frontend for the ST LSM6DSx family. It matches OF/SPI IDs, creates an 8-bit SPI regmap, and delegates device handling to the shared core.

Important APIs/functions: `st_lsm6dsx_spi_probe()` gets `spi_device_id` driver data, initializes `devm_regmap_init_spi()`, and calls `st_lsm6dsx_probe(&spi->dev, spi->irq, hw_id, regmap)`. OF and SPI ID tables mirror the supported core device names.

Control flow: SPI device match selects a hardware ID, regmap abstracts bus access, and the core handles reset, registration, IRQ/FIFO, shub, and PM.

State and persistence: no transport-private runtime state beyond SPI/regmap/core state.

Dependencies and integration: depends on SPI master, regmap SPI, OF matching, core PM ops, and namespace import `IIO_LSM6DSX`.

Risks: the probe uses SPI ID driver data directly; OF-only devices still need modalias/ID association to provide the correct driver data in this implementation. Match tables must remain synchronized with core settings.

Test signals: SPI modalias and OF matching for each supported name, regmap read/write, IRQ forwarding, PM ops, and core probe over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig

Purpose: Kconfig for the ST LSM9DS0/LSM303D IMU wrapper and I2C/SPI bus frontends.

Important symbols: `IIO_ST_LSM9DS0` depends on I2C or SPI master plus SYSFS, excludes legacy `SENSORS_LIS3_*`, and selects shared ST accelerometer and magnetometer 3-axis cores. `IIO_ST_LSM9DS0_I2C` and `_SPI` depend on the bus and core, default with the bus/core, select ST sensor bus helpers and regmap backends.

Control flow: core symbol builds the wrapper that instantiates accel and magn common drivers; frontend symbols build transport-specific regmap/probe code.

State and persistence: no runtime state; it shapes build-time composition.

Dependencies and integration: integrates with the older `st_sensors` accel/magn common framework, SYSFS, regmap, I2C, and SPI.

Risks: mutually excluding LIS3 legacy drivers avoids duplicate ownership. SPI help text says "I2C interface" in the viewed copy, a documentation typo.

Test signals: config/build with I2C-only, SPI-only, both, and conflicts with LIS3 drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile

Purpose: build rules for the ST LSM9DS0 IMU wrapper.

Important entries: `obj-$(CONFIG_IIO_ST_LSM9DS0) += st_lsm9ds0.o`, composite `st_lsm9ds0-y := st_lsm9ds0_core.o`, plus transport objects for I2C and SPI.

Control flow: Kconfig determines whether the core wrapper and bus frontend modules are built.

State and persistence: no runtime state.

Dependencies and integration: bus frontends call the namespace-exported core probe and rely on selected ST sensor common modules.

Risks: minimal; object naming must match module import expectations and Kconfig selections.

Test signals: module link for core, I2C, and SPI configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h

Purpose: small shared header for ST LSM9DS0 bus wrappers and core.

Important APIs/types: `struct st_lsm9ds0` stores device pointer, resolved chip name, IRQ, child accel/magn IIO devices, and regulator pointers. `st_lsm9ds0_probe()` is declared as the shared core entry point.

Control flow: bus frontends allocate/fill `struct st_lsm9ds0`, initialize bus regmap, and call the shared probe.

State and persistence: runtime wrapper state holds references to the two IIO children and supplies. In the current core, regulators are enabled through bulk devm helpers rather than stored in the struct fields.

Dependencies and integration: forward-declares `device`, `regmap`, `regulator`, and `iio_dev`, keeping transport files decoupled from full headers.

Risks: unused regulator pointer fields may be legacy leftovers; callers must set `dev`, `name`, and `irq` before calling probe.

Test signals: compile coverage and successful use from both I2C and SPI frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c

Purpose: shared wrapper that exposes an LSM9DS0/LSM303D IMU as separate ST common accelerometer and magnetometer IIO devices over one regmap.

Important APIs/functions: `st_lsm9ds0_probe_accel()` finds ST accel settings by name, allocates accel IIO device, fills `struct st_sensor_data`, and calls `st_accel_common_probe()`. `st_lsm9ds0_probe_magn()` does the same with magnetometer settings and `st_magn_common_probe()`. Exported `st_lsm9ds0_probe()` enables regulators then probes both children.

Control flow: bus probe resolves a canonical device name and regmap, then core enables `vdd`/`vddio`, creates the accelerometer child, and creates the magnetometer child. Both children share the same regmap and IRQ.

State and persistence: persistent state is in the wrapper's `accel` and `magn` IIO device pointers and in each child `st_sensor_data`. Regulators are enabled for the device lifetime through devm bulk enable.

Dependencies and integration: depends on `linux/iio/common/st_sensors.h`, `st_accel_get_settings()`, `st_magn_get_settings()`, and the common ST accel/magn probe implementations. Exports namespace `IIO_ST_SENSORS`.

Risks: both child probes depend on the same `name` resolving in both accel and magn settings tables. A magnetometer probe failure after accelerometer probe relies on devm cleanup. Shared regmap access correctness is delegated to common ST sensor code.

Test signals: regulator enable, name resolution for `lsm303d-imu` and `lsm9ds0-imu`, accel and magn IIO registration, shared IRQ behavior, and namespace import from bus modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c

Purpose: I2C frontend for ST LSM9DS0/LSM303D IMUs.

Important APIs/functions: OF table maps `st,lsm303d-imu` and `st,lsm9ds0-imu` to common ST sensor names; ACPI table maps `ACCL0001`; `st_lsm9ds0_i2c_probe()` normalizes the device name with `st_sensors_dev_name_probe()`, allocates wrapper state, initializes an 8-bit regmap with `read_flag_mask = 0x80`, stores client data, and calls `st_lsm9ds0_probe()`.

Control flow: I2C probe prepares the shared wrapper and regmap, then core creates accel and magnetometer IIO children.

State and persistence: frontend stores `struct st_lsm9ds0` as I2C client data; runtime child state is owned by the core/common ST sensors.

Dependencies and integration: depends on I2C, regmap I2C, `st_sensors_i2c.h`, OF/ACPI/I2C matching, and namespace import `IIO_ST_SENSORS`.

Risks: correct name normalization is required before common settings lookup. Regmap read flag must match the chip protocol. No PM ops are defined in this wrapper; power handling is through devm regulator enable and common child drivers.

Test signals: I2C and ACPI probe, device-name normalization, regmap reads, accel/magn child registration, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c

Purpose: SPI frontend for ST LSM9DS0/LSM303D IMUs.

Important APIs/functions: OF and SPI ID tables cover `lsm303d-imu` and `lsm9ds0-imu`. `st_lsm9ds0_spi_probe()` normalizes `spi->modalias`, allocates wrapper state, initializes SPI regmap with `read_flag_mask = 0xc0`, stores driver data, and calls `st_lsm9ds0_probe()`.

Control flow: SPI probe resolves the common ST sensor name, creates bus regmap, and delegates child accel/magn setup to the core.

State and persistence: frontend stores wrapper state as SPI driver data; core/common sensor code owns the child devices and hardware configuration.

Dependencies and integration: depends on SPI, regmap SPI, `st_sensors_spi.h`, OF/SPI matching, and namespace import `IIO_ST_SENSORS`.

Risks: SPI uses a different read flag mask from I2C; wrong mask breaks register reads. OF match data is name-oriented while probe uses modalias normalization, so modalias/name consistency is important.

Test signals: SPI probe for both IDs, regmap read/write traces, child accel/magn registration, and module alias generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm9ds0/st_lsm9ds0_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c

Purpose: ACPI helper functions for IIO drivers. It reads Microsoft-style ACPI sensor mount matrices and provides a legacy helper for retrieving ACPI device names plus match data.

Important APIs/functions: exported `iio_read_acpi_mount_matrix()` evaluates an ACPI method such as `ROTM`, validates a 3-string package, parses each row as three integers, and fills `struct iio_mount_matrix` with canonical string pointers for `-1`, `0`, and `1`. Exported `iio_get_acpi_device_name_and_data()` matches the device against its driver's ACPI table, optionally returns `driver_data`, and returns `dev_name(dev)`.

Control flow: mount-matrix read silently returns false when the device has no ACPI handle or method; evaluation/format/value errors log and return false after freeing the ACPI buffer. The legacy name helper returns NULL for no ACPI handle or no match.

State and persistence: no persistent state. The orientation matrix stores pointers to string literals, not allocated row strings. ACPI evaluation buffer is freed before return.

Dependencies and integration: depends on ACPI core helpers, device model, IIO mount matrix type, export symbols, and is used by drivers such as `st_lsm6dsx_core.c` before falling back to generic firmware mount matrix parsing.

Risks: `sscanf()` only accepts integer triplets and rejects any non-orthogonal value outside -1/0/1. The `acpi_status` is logged with `%d`, which may not be ideal for all status representations. The name/data helper is explicitly documented as backward compatibility and should not be used by new drivers.

Test signals: ACPI devices with valid `ROTM`, missing method, malformed package count/type, invalid matrix values, dual-method callers such as `ROMK`/`ROMS`, and ACPI match data retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c -->
