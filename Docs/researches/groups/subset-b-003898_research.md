# subset-b-003898

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vl6180.c -->
## sources/distributed-fs/ceph-client/drivers/iio/light/vl6180.c

Purpose: I2C Industrial I/O driver for the STMicro VL6180 proximity, range, and ambient-light sensor. It exposes `IIO_LIGHT`, `IIO_DISTANCE`, and `IIO_PROXIMITY` channels with direct reads, configurable ALS gain/integration time, per-channel sample frequency, and an optional IRQ-backed triggered buffer.

Important APIs/types/functions: `struct vl6180_data` stores the I2C client, mutex, completion, trigger, ALS gain/integration-time cache, and range/ALS measurement rates. `struct vl6180_chan_regs` maps each IIO channel to its ready bit, start register, result register, and byte/word width. Low-level access is implemented by `vl6180_read()`, `vl6180_read_byte()`, `vl6180_read_word()`, `vl6180_write_byte()`, and `vl6180_write_word()` using 16-bit big-endian register addresses. Core IIO entry points are `vl6180_read_raw()`, `vl6180_write_raw()`, `vl6180_trigger_handler()`, `vl6180_buffer_postenable()`, `vl6180_buffer_postdisable()`, and `vl6180_probe()`.

Control flow: probe allocates an IIO device, initializes mutex state, validates `VL6180_MODEL_ID`, places the chip in hold mode, enables ALS/range ready interrupts, installs a triggered buffer, programs default range/ALS inter-measurement times, ALS integration time, and ALS gain, then registers the IIO device. Direct raw reads call `vl6180_measure()`, which starts a single-shot conversion, waits either for `client->irq` completion or by polling `VL6180_INTR_STATUS`, reads the selected value register, clears interrupt/error flags, and unlocks. Buffered mode starts continuous conversion for the first active channel and relies on the threaded IRQ to poll the device trigger, read active channels, push a timestamped scan, and clear interrupt flags.

State/persistence: configuration lives in chip registers plus cached `als_gain_milli`, `als_it_ms`, `als_meas_rate`, and `range_meas_rate`; no disk persistence exists. `VL6180_HOLD` protects register updates. Devm-managed allocation owns the IIO device, IRQ, trigger, and buffer. The driver has no runtime PM path.

Dependencies/integration: depends on Linux I2C and IIO core, sysfs attributes, trigger consumer, triggered buffer support, OF match `st,vl6180`, and I2C id `vl6180`. It integrates with the devicetree binding for interrupt wiring and with userspace through standard IIO raw, scale, integration-time, hardware-gain, sample-frequency, and buffered scan ABI.

Risks: `vl6180_read()` treats any non-negative `i2c_transfer()` result as success instead of requiring the full message count, so short transfers could be misinterpreted. Buffered enable/disable returns after the first active channel, so simultaneous multi-channel continuous start is not attempted. Sample-frequency writes cache `val` before validating I2C success. The driver comments still list threshold events and hardware buffering as TODOs, and no runtime PM means continuous mode can hold the device active while buffers are enabled.

Test signals: build with `CONFIG_VL6180` and IIO triggered-buffer support; probe should reject wrong model ID and create `in_illuminance_raw`, distance/proximity raw channels, gain/integration/sample-frequency attributes, and optional trigger when IRQ is present. Exercise direct reads with and without IRQ, buffered scans for each supported scan mask, writable ALS gain/integration/sample frequency, interrupt timeout paths, and register-hold behavior under concurrent sysfs writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/vl6180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/zopt2201.c -->
## sources/distributed-fs/ceph-client/drivers/iio/light/zopt2201.c

Purpose: I2C IIO driver for the IDT/Renesas ZOPT2201 ambient-light and UV-B sensor. It exposes ALS raw/scale, UV intensity raw/scale, UV index processed output, and a shared integration-time setting.

Important APIs/types/functions: `struct zopt2201_data` stores the client, mutex, gain, resolution, and measurement-rate selector. Static tables describe ALS/UVB gain-to-scale conversion, resolution-to-measurement-time conversion, and valid combined scale presets. The main functions are `zopt2201_enable_mode()`, `zopt2201_read()`, `zopt2201_read_raw()`, `zopt2201_write_raw()`, `zopt2201_set_resolution()`, `zopt2201_set_gain()`, the scale/integration-time availability show helpers, and `zopt2201_probe()`.

Control flow: probe verifies SMBus block-read capability, reads `ZOPT2201_PART_ID`, allocates an IIO device, sets default 100 ms measurement rate, 18-bit resolution, gain 3, and registers direct-mode channels. A read enables ALS or UVB mode, waits up to ten measurement periods for `MAIN_STATUS_DRDY`, reads a 24-bit little-endian data register block, disables the sensor by writing `MAIN_CTRL=0`, and returns the raw count. Processed UV index reads reuse UVB data and derive an integer UV index from raw count, gain, and resolution. Scale writes choose a predefined gain/resolution pair and program both registers under the mutex.

State/persistence: the driver caches gain/resolution/rate in memory and mirrors gain/resolution in device registers. It powers the light engine only during reads by toggling `MAIN_CTRL`; there is no runtime/system PM state beyond devm cleanup. No persistent storage is used.

Dependencies/integration: uses Linux I2C SMBus helpers, `linux/cleanup.h` guard mutexes, unaligned little-endian helpers, and IIO sysfs. It registers only an I2C id table (`zopt2201`) and no OF/ACPI match in this file.

Risks: interrupt support and raw ALS/UVB alternate modes are TODOs. `zopt2201_read()` does not disable `MAIN_CTRL` on timeout or data-read failure, so failure paths can leave measurement enabled until the next successful operation or reset. The scale write path changes resolution first and gain second; a gain write failure leaves a partially changed scale. `zopt2201_show_*_avail()` assumes at least one entry before replacing the trailing space with newline.

Test signals: compile with IIO and I2C support, verify probe rejects unsupported adapters and wrong part IDs, confirm all `_available` sysfs files match the static tables, read ALS/UVB/UV index at every resolution and scale preset, inject SMBus failures to check cleanup behavior, and confirm concurrent reads/writes are serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/zopt2201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig

Purpose: Kconfig menu for Linux IIO magnetometer and Hall-effect sensor drivers. It declares user-visible driver options, hidden shared-core symbols, bus-wrapper symbols, dependencies, selected helper subsystems, and module names for the magnetometer directory.

Important APIs/types/functions: this is declarative Kconfig, not C code. Key user-visible symbols include `AF8133J`, `AK8974`, `AK8975`, `ALS31300`, `BMC150_MAGN_I2C`, `BMC150_MAGN_SPI`, `MAG3110`, `HID_SENSOR_MAGNETOMETER_3D`, `MMC35240`, `MMC5633`, `IIO_ST_MAGN_3AXIS`, `INFINEON_TLV493D`, `SENSORS_HMC5843_I2C`, `SENSORS_HMC5843_SPI`, `SENSORS_RM3100_I2C`, `SENSORS_RM3100_SPI`, `SI7210`, `TI_TMAG5273`, and `YAMAHA_YAS530`. Hidden core symbols include `BMC150_MAGN`, `SENSORS_HMC5843`, and `SENSORS_RM3100`.

Control flow: menuconfig processing presents `menu "Magnetometer sensors"` and enables objects indirectly through selected symbols. Bus wrappers select shared cores and regmap backends: BMC150 I2C/SPI select `BMC150_MAGN`, HMC5843 I2C/SPI select `SENSORS_HMC5843`, and RM3100 I2C/SPI select `SENSORS_RM3100`. Several drivers select `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER` when buffered capture is implemented.

State/persistence: Kconfig choices are persisted in the kernel `.config`; no runtime state exists. Hidden symbols ensure shared core objects are built only when a supported bus front-end is enabled.

Dependencies/integration: integrates with the kernel build system, I2C/SPI/I3C/HID subsystems, regmap, IIO buffers/triggers, `GPIOLIB`, `OF`, `SYSFS`, `HID_SENSOR_HUB`, and ST sensor helper libraries. It also carries compatibility/deprecation policy such as `AK09911` selecting `AK8975`.

Risks: dependency drift can break builds if a driver starts using a helper without selecting or depending on it. Hidden shared-core symbols must stay aligned with `Makefile` object names and module namespace imports. Help text and module names must remain accurate for package builders.

Test signals: run `make olddefconfig`, `make menuconfig`, and targeted `make M=drivers/iio/magnetometer` for representative built-in/module combinations across I2C, SPI, I3C, HID, OF, and COMPILE_TEST configurations. Confirm every selected symbol produces the intended object list and all hidden cores are built when wrappers require them.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile

Purpose: kernel build manifest for IIO magnetometer drivers. It maps Kconfig symbols to object files and groups multi-object ST magnetometer core/buffer pieces.

Important APIs/types/functions: declarative `obj-$(CONFIG_...) += ...` entries build per-driver modules. Shared cores are represented by `bmc150_magn.o`, `hmc5843_core.o`, and `rm3100-core.o`, while bus front-ends build separate I2C/SPI objects. `st_magn-y := st_magn_core.o` and `st_magn-$(CONFIG_IIO_BUFFER) += st_magn_buffer.o` define a compound object.

Control flow: kbuild evaluates enabled symbols from `.config`, adds corresponding objects to the directory build, and produces modules or built-in objects. Ordering is mostly alphabetical as noted in comments, with blank lines grouping families.

State/persistence: no runtime state exists. Build outputs are determined entirely by Kconfig state and kbuild rules.

Dependencies/integration: integrates with the Kconfig file in the same directory, module namespace imports in bus wrappers, and object names expected by help text and packaging. It includes entries for drivers beyond this work item, so changes can affect the whole magnetometer subtree.

Risks: missing an object entry for a Kconfig option silently prevents a selected driver from building. Renaming a file without updating this manifest breaks module builds. Shared-core and bus-wrapper symbols must remain paired or wrappers will link without exported common code.

Test signals: run `make M=drivers/iio/magnetometer` under all relevant configs, including module and built-in combinations for BMC150, HMC5843, RM3100, and MMC5633 I2C/I3C. `scripts/checkkconfigsymbols.py` and modpost namespace checks should remain clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/af8133j.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/af8133j.c

Purpose: I2C IIO driver for the Voltafield AF8133J 3-axis magnetometer. It supports regulators, optional reset GPIO, mount matrix, runtime autosuspend, selectable 12G/22G scale, direct reads, and triggered buffers.

Important APIs/types/functions: `struct af8133j_data` holds the client, regmap, measurement mutex, orientation matrix, optional reset GPIO, `avdd`/`dvdd` bulk regulators, and current range register. Main paths are `af8133j_power_up()`, `af8133j_power_down()`, `af8133j_reset()`, `af8133j_product_check()`, `af8133j_take_measurement()`, `af8133j_read_measurement()`, `af8133j_read_raw()`, `af8133j_set_scale()`, `af8133j_trigger_handler()`, and runtime PM callbacks.

Control flow: probe creates the IIO device and regmap, obtains optional reset GPIO and required regulators, reads mount matrix, powers and resets the chip, checks product code, enables autosuspend, configures channels and triggered buffer, and registers the IIO device. Reads resume runtime PM, start a work-state measurement, poll `STATUS_ACQ`, return to standby, bulk-read three little-endian axes, mark last busy, and autosuspend. Scale writes either program the range immediately if active or cache the range for application during the next power-up/reset.

State/persistence: `data->range` is the persistent in-memory shadow of the selected range and is restored after hardware/software reset. Runtime PM powers down regulators and asserts reset during suspend; resume powers up and resets. No nonvolatile configuration is written.

Dependencies/integration: uses I2C, regmap, regulator bulk APIs, GPIO descriptors, runtime PM, IIO mount-matrix ABI, and IIO triggered buffers. Device matching is via OF compatible `voltafield,af8133j` and I2C id `af8133j`.

Risks: product-code mismatch is only warned and allowed so fallback compatibles work; this improves compatibility but can bind to incompatible devices. `af8133j_set_scale()` disables runtime PM around range updates and caches the new range even if an active register write fails. Triggered-buffer reads return no sample on runtime PM `-EACCES` during system sleep, which is intentionally quiet except for other errors.

Test signals: verify regulator/reset sequencing on probe, runtime suspend/resume, and remove; read raw X/Y/Z under direct and triggered-buffer paths; change both scale values while active and while autosuspended; validate mount-matrix ext_info; and confirm product-code warning behavior with fallback-compatible devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/af8133j.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8974.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8974.c

Purpose: I2C IIO driver for AK8974, AMI305, AMI306, and HSCDTD008A 3-axis magnetometers. It handles variant detection, regulators, runtime autosuspend, optional DRDY IRQ, direct reads, and triggered buffers.

Important APIs/types/functions: `struct ak8974` stores I2C client, mount matrix, regmap, `avdd`/`dvdd` regulators, detected variant/name, measurement lock, DRDY completion/IRQ flags, and scan buffer. Key functions include `ak8974_detect()`, `ak8974_selftest()`, `ak8974_reset()`, `ak8974_configure()`, `ak8974_trigmeas()`, `ak8974_await_drdy()`, `ak8974_getresult()`, `ak8974_measure_channel()`, `ak8974_fill_buffer()`, `ak8974_probe()`, and runtime PM callbacks.

Control flow: probe allocates the IIO device, reads mount matrix, enables regulators, starts runtime PM, initializes regmap, powers the chip, detects the variant from `WHOAMI`, optionally logs AMI firmware/serial/calibration data as device randomness, runs self-test but continues on failure, resets the device, selects 12-bit or 15-bit channels, sets up a triggered buffer, optionally requests a shared DRDY IRQ, registers the IIO device, and enables autosuspend. Reads resume the device, lock, trigger forced measurement, wait by IRQ completion or polling status, check interrupt-source overflow, bulk-read all axes, return the selected channel or push a full scan, and autosuspend.

State/persistence: runtime PM disables regulators and powers the chip off; resume reenables regulators, waits for power-on delay, powers on, and reapplies configuration. Detected variant and name persist in memory. Calibration values are read for logging/randomness but not used to transform samples.

Dependencies/integration: uses I2C, regmap with variant-sensitive writeable ranges, regulators, IRQ/completion APIs, runtime PM, IIO mount matrix, IIO buffers/triggers, OF compatibles `asahi-kasei,ak8974` and `alps,hscdtd008a`, and I2C ids for AMI/AK/HSCDTD variants.

Risks: self-test failure is logged but not fatal. IRQ trigger polarity depends on firmware/IRQ type and defaults to rising. Runtime PM setup has manual error unwinding rather than devm. Variant-sensitive `writeable_reg` looks up client data during regmap access, so client data must be set before writes that consult the callback. Buffered timestamps are taken after conversion rather than at DRDY.

Test signals: probe each supported `WHOAMI`, validate 12-bit versus 15-bit channel layouts and scales, test forced reads with and without DRDY IRQ, exercise overflow error handling, suspend/resume around reads, and ensure self-test failures do not block registration but are visible in logs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8974.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8975.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8975.c

Purpose: I2C IIO driver for Asahi Kasei AK8975-family compasses, including AK8963, AK09911, AK09912, AK09916, and AK09918. It exposes three magnetometer axes with per-axis calibration-derived scale, optional EOC GPIO/IRQ, reset GPIO, regulators, runtime PM, ACPI/OF/I2C matching, and triggered buffers.

Important APIs/types/functions: `struct ak_def` captures per-chip register addresses, masks, modes, data registers, range, and raw-to-gauss conversion function. `struct ak8975_data` stores chip definition, ASA calibration bytes, computed scales, GPIOs, wait queue, control-cache byte, mount matrix, regulators, and scan buffer. Key functions are `ak8975_power_on/off()`, `ak8975_who_i_am()`, `ak8975_set_mode()`, `ak8975_setup()`, the three conversion wait helpers, `ak8975_start_read_axis()`, `ak8975_read_axis()`, `ak8975_fill_buffer()`, `ak8975_probe()`, and runtime PM callbacks.

Control flow: probe obtains optional EOC and reset GPIOs, allocates IIO state, resolves the chip definition from match data, gets `vdd`/`vid`, powers the device, validates WIA registers, enters fuse-ROM mode to read ASA calibration, computes per-axis scale, sets up optional data-ready IRQ, configures channels and buffer, registers the device, and enables autosuspend. A read resumes runtime PM, locks, switches to single-measurement mode, waits for completion through IRQ, GPIO polling, or ST1 polling, reads one axis, reads ST2 to release the measurement latch and check error/overflow bits, unlocks, autosuspends, clamps to valid range, and returns raw data.

State/persistence: ASA bytes and calculated `raw_to_gauss[]` persist for the lifetime of the device. `cntl_cache` shadows the control register for mode writes. Runtime PM powers regulators/reset off during suspend and restores power-down mode on resume. No nonvolatile writes occur.

Dependencies/integration: uses I2C SMBus block helpers, GPIO descriptors, regulators, wait queues, runtime PM, IIO mount matrix, IIO triggered buffers, OF compatible table, ACPI table, and legacy I2C ids. The deprecated `AK09911` Kconfig symbol selects this driver.

Risks: `ak8975_read_axis()` calls `pm_runtime_get_sync()` but its error path returns before `pm_runtime_put_autosuspend()`, and triggered-buffer reads do not take runtime PM, so power-state coverage deserves testing. Unknown second WIA byte is logged but still accepted for register-compatible variants. Scale depends on fuse bytes read once; bad ASA data directly affects ABI scale. Failure during scale/power setup must unwind regulators correctly.

Test signals: test every match-table variant, WIA validation, ASA read/scales, EOC IRQ/GPIO/polling completion paths, ST2 overflow and data-error handling, runtime suspend/resume during direct and buffered reads, mount-matrix exposure, and all firmware naming paths including ACPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/ak8975.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/als31300.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/als31300.c

Purpose: I2C IIO driver for Allegro MicroSystems ALS31300 3-D linear Hall-effect sensors. It exposes temperature plus X/Y/Z magnetic axes, variant-dependent magnetic scale, runtime PM, a regulator, and triggered buffers.

Important APIs/types/functions: `struct als31300_variant_info` stores the factory sensitivity divisor for 500/1000/2000 gauss variants. `struct als31300_data` stores device, mutex, variant info, and 32-bit regmap. Important functions are `als31300_get_measure()`, `als31300_read_raw()`, `als31300_trigger_handler()`, `als31300_set_operating_mode()`, `als31300_probe()`, and runtime PM callbacks.

Control flow: probe allocates IIO state, initializes a mutex, resolves variant data from OF/I2C match, creates a 32-bit regmap, enables `vcc`, sets active mode, adds a managed power-down action, configures channels and scan masks, sets up a triggered buffer with timestamp storage, enables runtime autosuspend, and registers the IIO device. Reads resume runtime PM under the mutex, poll a two-register bulk read until `NEW_DATA` appears, extract 12-bit signed axes and 12-bit temperature from bitfields, autosuspend, and return raw, scale, or temperature offset.

State/persistence: runtime PM toggles the sensor between active and sleep modes; the regulator remains managed by devm enable. Variant sensitivity is fixed by compatible/id because the driver cannot read sensitivity at runtime. No EEPROM configuration is changed; comments state only default external-trigger EEPROM setup is supported.

Dependencies/integration: uses I2C, regmap with 8-bit registers and 32-bit values, regulator helper `devm_regulator_get_enable()`, runtime PM, `linux/units.h`, IIO buffers/triggers, and OF/I2C variant tables for `allegromicro,als31300-*`.

Risks: interrupt lines are documented in bindings but not implemented for events. EEPROM configuration is assumed rather than discovered, so boards with non-default EEPROM behavior may not work. `als31300_get_measure()` logs `ret` instead of `err` in one read-error message. Temperature and magnetic scale formulas should be checked against datasheet units.

Test signals: verify all three variants expose expected scale, direct reads for temp and axes, triggered scans with all four channels, runtime autosuspend transitions, failure injection for regmap bulk reads, and behavior on boards declaring interrupts that the driver currently ignores.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/als31300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c

Purpose: shared core driver for Bosch BMC150/BMC156/BMM150 magnetometers. Bus wrappers provide regmap transport; this core implements device initialization, compensation, IIO ABI, optional data-ready trigger, triggered buffer, regulators, mount matrix, and runtime/system PM.

Important APIs/types/functions: exported symbols are `bmc150_magn_regmap_config`, `bmc150_magn_probe()`, `bmc150_magn_remove()`, and `bmc150_magn_pm_ops`. `struct bmc150_magn_data` stores device, mutex, regmap, regulators, orientation, scan buffer, optional trigger, max ODR, and IRQ. Key internal functions include power-mode helpers, ODR/oversampling helpers, `bmc150_magn_compensate_x/y/z()`, `bmc150_magn_read_xyz()`, raw read/write handlers, trigger state/reenable handlers, `bmc150_magn_init()`, and buffer PM hooks.

Control flow: common probe allocates an IIO device, obtains `vdd`/`vddio`, reads mount matrix, initializes and validates chip id, programs the regular preset ODR/repetition counts, sets normal mode, configures IIO channels and optional IRQ-backed data-ready trigger, sets up the triggered buffer, enables runtime autosuspend, and registers. Direct reads resume runtime PM, read raw axes/RHALL and trim registers, apply Bosch integer compensation, return one axis, then autosuspend. Buffered reads keep power active between preenable/postdisable and push compensated XYZ data on trigger.

State/persistence: ODR, repetition counts, and power mode live in device registers; `max_odr` caches the valid ceiling derived from repetition settings. Runtime PM changes normal/sleep modes, while remove puts the device into suspend and disables regulators. Regmap uses RBTREE caching with volatile data/status registers.

Dependencies/integration: integrates with IIO core, sysfs, events include headers, triggered buffers, triggers, regmap, regulators, runtime PM, and bus-specific modules through exported namespace `IIO_BMC150_MAGN`. The mount matrix is exposed through IIO ext_info.

Risks: compensation formulas are dense fixed-point code from Bosch API and sensitive to trim read correctness and overflow sentinels. `bmc150_magn_show_samp_freq_avail()` assumes at least one frequency before replacing the final space. IRQ setup uses non-devm `request_irq()`/manual cleanup. Error paths after initialization should preserve regulator/power balance. Direct reads reject when the buffer is enabled.

Test signals: test I2C and SPI wrappers against this core, chip-id rejection, regulator failures, direct raw/scale/ODR/oversampling sysfs operations, max-ODR validation, data-ready IRQ trigger enable/disable/reenable, buffered scans, runtime suspend/resume, and mount-matrix output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h

Purpose: private shared header connecting BMC150 magnetometer bus wrappers to the common core implementation.

Important APIs/types/functions: declares exported `bmc150_magn_regmap_config`, exported `bmc150_magn_pm_ops`, `bmc150_magn_probe(struct device *dev, struct regmap *regmap, int irq, const char *name)`, and `bmc150_magn_remove(struct device *dev)`.

Control flow: no executable flow exists. I2C/SPI wrapper modules include this header, initialize a bus-specific regmap, and call the common probe/remove and PM ops declared here.

State/persistence: no state is stored in the header. It defines the compile-time contract for sharing the core's device-managed IIO state via `dev_set_drvdata()`.

Dependencies/integration: depends on `struct regmap_config`, `struct dev_pm_ops`, `struct device`, and `struct regmap` being available through included kernel headers in users of the header. It pairs with namespace exports/imports under `IIO_BMC150_MAGN`.

Risks: because this is a narrow internal ABI, any signature change must be applied to both wrappers and the core. The header does not include `<linux/device.h>` explicitly, so it relies on includers or included regmap headers for type declarations.

Test signals: compile both BMC150 I2C and SPI modules as built-ins and modules, and run modpost to ensure exported symbols and namespace imports resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c

Purpose: I2C bus front-end for the Bosch BMC150/BMC156/BMM150 magnetometer core.

Important APIs/types/functions: `bmc150_magn_i2c_probe()` creates an I2C regmap using the shared `bmc150_magn_regmap_config`, resolves the I2C id name when present, and calls `bmc150_magn_probe()`. `bmc150_magn_i2c_remove()` delegates to `bmc150_magn_remove()`. Match tables cover I2C ids `bmc150_magn`, `bmc156_magn`, `bmm150_magn` and OF compatibles `bosch,bmc150_magn`, `bosch,bmc156_magn`, deprecated `bosch,bmm150_magn`, and `bosch,bmm150`.

Control flow: module registration installs an `i2c_driver`; probe initializes regmap, forwards device/IRQ/name to the core, and remove tears down via the core. PM operations are the shared core PM ops.

State/persistence: this wrapper owns no sensor state beyond the devm regmap; core state is stored on the device by `bmc150_magn_probe()`.

Dependencies/integration: depends on I2C, regmap-I2C, the shared BMC150 core, and module namespace `IIO_BMC150_MAGN`. It is selected by `CONFIG_BMC150_MAGN_I2C`.

Risks: firmware-node probing can produce `name = NULL` when no I2C id is available, so user-visible `indio_dev->name` depends on enumeration path. The `MODULE_AUTHOR` string is missing a closing angle bracket, a metadata issue only.

Test signals: compile as module and built-in, probe each I2C id/OF compatible, verify IRQ forwarding to core, and confirm PM namespace/modpost checks are clean.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c

Purpose: SPI bus front-end for the Bosch BMC150/BMC156/BMM150 magnetometer core.

Important APIs/types/functions: `bmc150_magn_spi_probe()` initializes a SPI regmap with the shared `bmc150_magn_regmap_config`, gets the SPI device id, and calls `bmc150_magn_probe()`. `bmc150_magn_spi_remove()` calls `bmc150_magn_remove()`. The SPI id table supports `bmc150_magn`, `bmc156_magn`, and `bmm150_magn`.

Control flow: module registration installs a `spi_driver`; probe sets up transport and delegates all functional behavior to the shared core; remove delegates teardown. Unlike the I2C wrapper, this driver table does not attach the shared PM ops directly.

State/persistence: no independent runtime state beyond devm regmap; core state is attached to the SPI device.

Dependencies/integration: depends on SPI, regmap-SPI, BMC150 common core, and namespace import `IIO_BMC150_MAGN`. It is built by `CONFIG_BMC150_MAGN_SPI`.

Risks: no OF match table is present in this wrapper, so SPI devices need board/device-id enumeration unless another mechanism supplies ids. The shared regmap config has no SPI read flag override here; correctness depends on regmap-SPI framing matching the device protocol. `MODULE_AUTHOR` metadata is missing a closing angle bracket.

Test signals: compile and modpost namespace checks, instantiate SPI ids, verify regmap read/write over SPI, confirm core probe receives IRQ/name, and exercise remove cleanup after triggered-buffer use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/bmc150_magn_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c

Purpose: platform IIO driver that exposes HID Sensor Hub Compass 3D reports as magnetometer and rotation channels. It dynamically maps HID report attributes to IIO channels and buffered samples.

Important APIs/types/functions: `struct magn_3d_state` stores HID callbacks, common HID attributes for magnetic flux and rotation, per-usage attribute info, dynamically allocated IIO value buffer, per-channel value pointers, scale/offset metadata, and timestamp. Key functions are `magn_3d_read_raw()`, `magn_3d_write_raw()`, `magn_3d_proc_event()`, `magn_3d_capture_sample()`, `magn_3d_parse_report()`, `hid_magn_3d_probe()`, and `hid_magn_3d_remove()`.

Control flow: probe parses common HID sensor attributes for usage `HID_USAGE_SENSOR_COMPASS_3D`, clones them for rotation sensitivity handling, scans the report descriptor for supported magnetometer/heading/timestamp usages, allocates an exact channel array and aligned sample buffer, formats scale values, sets up a HID sensor trigger, registers the IIO device, and registers HID callbacks. Raw reads power the HID sensor, synchronously fetch a report value for the selected usage, and power down. Runtime callbacks capture each incoming sample into the per-channel buffer, convert HID timestamps when present, and on report event push a timestamped IIO buffer if data-ready is set.

State/persistence: channel layout and scale/offset metadata are derived from the HID report descriptor at probe and kept in memory. Sample values live in a dynamically allocated buffer; no hardware register state or persistent storage is owned here. Power and sampling/hysteresis configuration is managed through HID sensor common helpers.

Dependencies/integration: depends on HID sensor hub APIs, HID sensor common trigger/PM helpers, IIO direct mode and buffers, platform driver id `HID-SENSOR-200083`, and namespace `IIO_HID`.

Risks: raw sample extraction casts `raw_data` directly to `u32 *`/`s64 *`, so descriptor size/alignment assumptions matter. Channel count includes timestamp handling and value-buffer alignment logic that should be validated for sparse reports. Scale for rotation sensitivity has a separate lookup fallback and may be missing on some descriptors. Only channels present in the HID report are exposed, so userspace must tolerate variable layouts.

Test signals: test with HID devices exposing full and sparse Compass 3D reports, raw reads for each channel type, sample-frequency and hysteresis writes, trigger enable/disable, timestamp conversion, buffer pushes with and without HID timestamps, suspend/resume via `hid_sensor_pm_ops`, and malformed descriptor paths with no supported usages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hid-sensor-magn-3d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843.h -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843.h

Purpose: internal shared header for Honeywell HMC5843/HMC5883/HMC5883L/HMC5983 magnetometer core and bus wrappers.

Important APIs/types/functions: defines common register addresses (`CONFIG_REG_A/B`, `MODE_REG`, data output base, status, id range), `enum hmc5843_ids`, `struct hmc5843_data`, and prototypes for `hmc5843_common_probe()`, `hmc5843_common_remove()`, and exported `hmc5843_pm_ops`. `struct hmc5843_data` includes device, mutex, regmap, variant pointer, mount matrix, and big-endian scan buffer.

Control flow: no executable code. Bus wrappers include this header to share variant ids and call the common core.

State/persistence: no state is created here, but the struct layout defines the per-device state allocated by the core. Mode/configuration persistence is handled in core registers.

Dependencies/integration: includes Linux regmap and IIO headers and depends on the core's private forward declaration of `struct hmc5843_chip_info`. It pairs with namespace exports/imports under `IIO_HMC5843`.

Risks: changing register constants or enum ordering affects both I2C and SPI wrappers and the variant table in the core. The forward-declared variant type is intentionally opaque but ties the header to the core implementation.

Test signals: compile HMC5843 core plus both wrappers in module and built-in configurations, verifying prototypes, struct layout users, PM ops, and namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c

Purpose: shared IIO core for Honeywell HMC5843, HMC5883, HMC5883L, and HMC5983 magnetometers. It implements variant-specific channels, scale/frequency tables, measurement configuration enum, mount matrix, direct reads, triggered buffers, and sleep/resume handling.

Important APIs/types/functions: exported `hmc5843_common_probe()`, `hmc5843_common_remove()`, and `hmc5843_pm_ops` are consumed by bus wrappers. `struct hmc5843_chip_info` maps each variant to channels and scale/frequency tables. Main functions are `hmc5843_set_mode()`, `hmc5843_wait_measurement()`, `hmc5843_read_measurement()`, `hmc5843_set_meas_conf()`, raw read/write handlers, `hmc5843_trigger_handler()`, `hmc5843_init()`, and common PM callbacks.

Control flow: common probe allocates state, stores regmap/variant/mount matrix, configures IIO channels and scan masks, reads the 3-byte ID signature `H43`, sets normal measurement config, default sample rate and range gain, switches to continuous conversion, sets up triggered buffer, and registers the IIO device. Raw reads wait for data-ready then bulk-read three big-endian axes. Writes update sample-rate or range-gain bits after validating against variant tables. Triggered buffers use the same wait/read sequence and push the full scan.

State/persistence: chip mode, gain, rate, and measurement config live in device registers. Suspend sets sleep mode and resume restores continuous conversion, but other configuration remains in registers/regmap cache. Per-device orientation and variant pointer persist in memory.

Dependencies/integration: uses regmap supplied by I2C/SPI wrappers, IIO sysfs attributes, IIO enums/ext_info, triggered buffers, mount matrix, and module namespace `IIO_HMC5843`.

Risks: sample-rate and scale reads index tables directly from shifted register values without masking against table length, relying on valid hardware/config writes. `hmc5843_wait_measurement()` can block up to 150 * 20 ms. HMC5883/HMC5983 swap Y/Z channel ordering, which is ABI-visible. The core validates only the shared `H43` id bytes, not per-variant identity.

Test signals: test each variant id through I2C/SPI wrappers, scale/frequency read/write and availability files, measurement configuration enum including HMC5983 disabled mode, direct and buffered reads, Y/Z ordering, sleep/resume, and probe rejection when ID bytes differ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_i2c.c

Purpose: I2C transport wrapper for the HMC5843-family common magnetometer core.

Important APIs/types/functions: defines readable, writable, and volatile regmap ranges for the HMC5843 register window, `hmc5843_i2c_regmap_config`, `hmc5843_i2c_probe()`, and `hmc5843_i2c_remove()`. I2C ids and OF compatibles map names to `enum hmc5843_ids`.

Control flow: I2C probe creates a regmap with RBTREE cache and access tables, then calls `hmc5843_common_probe()` with id-derived variant and name. Remove calls `hmc5843_common_remove()`. Shared PM ops are attached to the driver.

State/persistence: wrapper state is devm regmap only; all sensor state is owned by common core.

Dependencies/integration: depends on I2C, regmap-I2C, IIO core, triggered buffer headers, shared HMC5843 core, OF matching, and namespace `IIO_HMC5843`.

Risks: `hmc5843_i2c_probe()` obtains variant data from the I2C id table, not `of_device_get_match_data()`, so pure OF enumeration must still provide compatible modalias/id behavior that yields a valid `i2c_device_id`. Access tables permit writes only through `MODE_REG`, matching core writes to config A/B and mode.

Test signals: compile with `CONFIG_SENSORS_HMC5843_I2C`, instantiate all I2C ids and OF compatibles, verify regmap access tables allow core initialization/config writes, test remove and suspend/resume, and check modpost namespace imports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c

Purpose: SPI transport wrapper for the Honeywell HMC5983 magnetometer using the shared HMC5843 core.

Important APIs/types/functions: defines SPI regmap access tables, `hmc5843_spi_regmap_config` with `read_flag_mask = 0xc0` for autoincrement reads, `hmc5843_spi_probe()`, and `hmc5843_spi_remove()`. The SPI id table supports `hmc5983` only.

Control flow: probe forces SPI mode 3 and max speed 8 MHz, calls `spi_setup()`, creates a SPI regmap, and delegates to `hmc5843_common_probe()` with HMC5983 variant data. Remove calls the common remove. PM uses shared `hmc5843_pm_ops`.

State/persistence: no wrapper-owned runtime state beyond the devm regmap and SPI bus settings.

Dependencies/integration: depends on SPI, regmap-SPI, IIO, HMC5843 common core, and namespace `IIO_HMC5843`. Built by `CONFIG_SENSORS_HMC5843_SPI`.

Risks: the driver overwrites `spi->mode` and `spi->max_speed_hz` before setup, which may surprise board configuration but matches device limits. No OF match table is present, so enumeration is via SPI ids. Regmap read flag/autoincrement correctness is central to multi-byte sample reads.

Test signals: compile and modpost namespace checks, instantiate `hmc5983` SPI, verify SPI mode/speed setup, confirm ID read and bulk data reads over regmap, and exercise common scale/frequency/buffer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/hmc5843_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mag3110.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mag3110.c

Purpose: I2C IIO driver for the Freescale/NXP MAG3110 3-axis magnetometer with temperature channel, sample-frequency control, calibration-bias registers, regulators, system sleep PM, and triggered buffers.

Important APIs/types/functions: `struct mag3110_data` stores I2C client, mutex, cached `CTRL_REG1`, calculated sleep value, `vdd`/`vddio` regulators, and scan buffer. Main functions include `mag3110_request()`, `mag3110_read()`, `mag3110_change_config()`, `mag3110_read_raw()`, `mag3110_write_raw()`, `mag3110_trigger_handler()`, `mag3110_probe()`, `mag3110_remove()`, and sleep PM callbacks.

Control flow: probe obtains and enables regulators, verifies `WHO_AM_I`, initializes cached control state and active/one-shot behavior depending on sampling period, writes control registers including magnetic auto-reset, sets up a triggered buffer, and registers the IIO device. Direct reads claim direct mode, trigger or wait for data-ready, bulk-read big-endian XYZ or temperature, and release direct mode. Configuration writes move the device to standby, wait for `SYSMOD` standby, write the selected register, and restore active mode when necessary.

State/persistence: `ctrl_reg1` and `sleep_val` shadow sampling configuration across writes and resume. Calibration bias is stored in device offset registers. Suspend places the device in standby and disables regulators; resume enables regulators and restores `CTRL_REG1`.

Dependencies/integration: uses I2C SMBus, regulators, IIO sysfs/buffers/triggers, direct-mode claiming, and OF compatible `fsl,mag3110`. It builds under `CONFIG_MAG3110`.

Risks: IRQ support, user offset refinements, oversampling, and full continuous-mode support are still TODOs. `mag3110_change_config()` always waits for standby even when the device was already inactive, increasing latency. Sample-frequency changes update cached state before the I2C write, so failed writes can desynchronize cache and hardware. Calibration-bias writes are not protected by the main config-change standby path.

Test signals: verify regulator sequencing, WHOAMI rejection, raw XYZ/temp reads, sample-frequency available values and writes, calibration-bias read/write bounds, active versus triggered one-shot timing, buffer scan masks `0x7` and `0xf`, suspend/resume restoration, and failure unwinding after regulator or buffer setup errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mag3110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc35240.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc35240.c

Purpose: I2C IIO driver for the MEMSIC MMC35240 3-axis magnetic sensor. It supports direct magnetometer reads, sampling-frequency selection, OTP-based axis compensation, regmap caching, and system sleep cache handling.

Important APIs/types/functions: `struct mmc35240_data` stores I2C client, mutex, regmap, selected resolution, OTP compensation coefficients, and scale divisors. Main functions are `mmc35240_init()`, `mmc35240_hw_set()`, `mmc35240_take_measurement()`, `mmc35240_read_measurement()`, `mmc35240_raw_to_mgauss()`, `mmc35240_read_raw()`, `mmc35240_write_raw()`, `mmc35240_probe()`, and PM callbacks.

Control flow: probe creates a regmap with flat cache, initializes resolution to slow 16-bit mode, registers IIO channel metadata, and calls init. Init reads product id for logging, performs SET then RESET coil operations with charge-pump refill delays, programs default bandwidth, reads six OTP bytes, and computes Y/Z compensation. Raw reads lock, trigger a measurement, poll status up to 100 times with 10 ms sleeps, bulk-read little-endian XYZ, convert axes into milli-gauss with null-field offset and OTP compensation, and return scale/sample-frequency as requested. Sample-frequency writes update bandwidth bits.

State/persistence: selected bandwidth lives in `CTRL1` and regmap cache; OTP compensation is kept in RAM. Suspend switches regmap to cache-only, and resume marks cache dirty, syncs `CTRL0..CTRL1`, then disables cache-only mode. There is no regulator/runtime PM support.

Dependencies/integration: uses I2C, regmap-I2C, IIO sysfs, OF compatible `memsic,mmc35240`, ACPI id `MMC35240`, and I2C id `mmc35240`.

Risks: the TODO lists offset, ACPI improvements, continuous mode, and PM, though simple sleep cache handling exists. Product id is not validated against a constant. Resume calls `regcache_sync_region()` before `regcache_cache_only(false)`, which should be checked against regmap expectations. Measurement timeout can take about one second.

Test signals: verify init SET/RESET timing, OTP compensation math, raw axis conversion at all four sampling frequencies, suspend/resume cache restoration, OF/ACPI/I2C matching, and timeout/error paths for status polling and regmap reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc35240.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc5633.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc5633.c

Purpose: MEMSIC MMC5633/MMC5603 IIO driver supporting both I2C and I3C transports in one file. It exposes X/Y/Z magnetic raw data, temperature raw/scale/offset, sampling-frequency control, regmap caching, and optional I3C HDR-DDR transfer mode.

Important APIs/types/functions: `struct mmc5633_data` stores regmap, optional `i3c_device`, and measurement mutex. Key functions include `mmc5633_init()`, `mmc5633_take_measurement()`, `mmc5633_is_support_hdr()`, `mmc5633_read_measurement()`, `mmc5633_get_raw()`, `mmc5633_read_raw()`, `mmc5633_write_raw()`, `mmc5633_read_avail()`, `mmc5633_common_probe()`, I2C/I3C probe functions, and sleep PM callbacks.

Control flow: common probe allocates IIO state, stores regmap/I3C handle, initializes mutex and channels, performs SET/RESET and default bandwidth programming, then registers the IIO device. Raw reads lock for a full measurement. In I3C HDR-DDR mode the driver issues private transfer commands to write `CTRL0`, poll status, and read long data; otherwise it writes measurement bits through regmap, polls `STATUS1`, and reads either temperature or the packed magnetic data block. `mmc5633_get_raw()` unpacks 20-bit big-endian magnetic samples or the aligned temperature byte. Sampling-frequency writes update `CTRL1` bandwidth bits.

State/persistence: bandwidth and control registers are cached by regmap MAPLE cache. Suspend switches regmap cache-only; resume marks dirty, syncs `CTRL0..CTRL1`, and exits cache-only. The optional I3C pointer determines whether HDR is attempted at runtime.

Dependencies/integration: uses I2C, I3C, regmap-I2C, regmap-I3C, IIO sysfs, iopoll helpers, unaligned helpers, OF compatibles `memsic,mmc5603`/`memsic,mmc5633`, I2C ids, and I3C manufacturer/device id table. The module uses `module_i3c_i2c_driver()`.

Risks: product id is read but not validated. The temperature SDR fallback writes into `buf + sz - 1` to match HDR alignment, which depends on callers providing `MMC5633_ALL_SIZE`. The packed 20-bit magnetic values are returned unsigned raw with no centering/offset conversion. Suspend/resume regcache ordering mirrors MMC35240 and should be validated.

Test signals: test I2C and I3C SDR/HDR devices, SET/RESET init, sampling-frequency read/write and read_avail, magnetic and temperature raw/scale/offset ABI, packed data unpacking, measurement timeouts, cache-only suspend/resume, and module registration for combined I3C/I2C builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/mmc5633.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c

Purpose: shared IIO core for PNI RM3100 3-axis geomagnetic sensors. Bus wrappers provide regmap transport; the core implements direct polling, optional IRQ/data-ready trigger, continuous buffered mode, sample-frequency control, cycle-count/scale management, and exported regmap access tables.

Important APIs/types/functions: exported symbols are `rm3100_readable_table`, `rm3100_writable_table`, `rm3100_volatile_table`, and `rm3100_common_probe()`. `struct rm3100_data` stores regmap, completion, interrupt flag, conversion time, scale, fixed scan buffer, optional data-ready trigger, and mutex. Key functions are `rm3100_wait_measurement()`, `rm3100_read_mag()`, `rm3100_get_samp_freq()`, `rm3100_set_cycle_count()`, `rm3100_set_samp_freq()`, raw read/write handlers, buffer preenable/postdisable, IRQ handlers, and `rm3100_trigger_handler()`.

Control flow: common probe allocates IIO state, sets up optional IRQ and trigger, installs a triggered buffer, reads `TMRC`, validates sample-rate index, initializes conversion timeout and cycle count/scale, and registers the IIO device. Direct reads claim direct mode, write the poll register for one axis, wait for DRDY via completion or status polling, bulk-read a 24-bit big-endian result, sign-extend, and return. Buffered mode writes CMM to enable active axes, IRQ or trigger handler bulk-reads packed result bytes, reshapes them to IIO 32-bit storage alignment, pushes timestamped buffers, and disables CMM after buffer shutdown.

State/persistence: sample rate is in `TMRC`, cycle count is in three CC registers, and `scale`/`conversion_time` are cached in memory. Frequency writes may change cycle count between 100 and 200 to keep 600 Hz valid and restart CMM if buffers are active. There is no PM implementation despite TODO.

Dependencies/integration: uses regmap supplied by I2C/SPI wrappers, IIO sysfs/buffer/trigger APIs, IRQ completions, unaligned big-endian helpers, and namespace `IIO_RM3100`.

Risks: no runtime/system PM. `rm3100_get_samp_freq()` indexes `rm3100_samp_rates[tmp - offset]` without range validation after probe, so corrupted registers can cause invalid indexing. Buffer handler has several scan-mask-specific byte reshaping paths that are easy to regress. IRQ thread clears interrupts by writing `POLL=0`, which may interact with concurrent measurements.

Test signals: test I2C and SPI wrappers, no-IRQ polling and IRQ completion paths, every sample-frequency value including cycle-count transitions, direct-mode exclusion during buffers, all supported scan masks, CMM restart when frequency changes while buffered, timeout paths, and modpost namespace exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-i2c.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-i2c.c

Purpose: I2C transport wrapper for the PNI RM3100 magnetometer core.

Important APIs/types/functions: defines `rm3100_regmap_config` using exported readable/writable/volatile tables, `rm3100_probe()`, OF match table `pni,rm3100`, and an `i2c_driver` named `rm3100-i2c`.

Control flow: I2C probe creates a regmap with 8-bit registers/values and RBTREE cache, then calls `rm3100_common_probe()` with device, regmap, and I2C IRQ. Module registration is via `module_i2c_driver()`.

State/persistence: no wrapper-owned state beyond devm regmap. The core stores all IIO and measurement state.

Dependencies/integration: depends on I2C, regmap-I2C, the shared RM3100 core/header, OF matching, and namespace import `IIO_RM3100`. Built by `CONFIG_SENSORS_RM3100_I2C`.

Risks: there is no I2C id table in this file, so matching is OF-centric. Probe returns raw `PTR_ERR()` from regmap init without `dev_err_probe()` logging. Runtime PM is absent because the core has no PM implementation.

Test signals: instantiate an OF `pni,rm3100` I2C device, verify IRQ forwarding and no-IRQ polling, run direct and buffered reads, and check namespace/modpost resolution for core symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c

Purpose: SPI transport wrapper for the PNI RM3100 magnetometer core.

Important APIs/types/functions: defines SPI `rm3100_regmap_config` with shared access tables and `read_flag_mask = 0x80`, `rm3100_probe()`, OF match table `pni,rm3100`, and `spi_driver` named `rm3100-spi`.

Control flow: probe forces SPI mode 0 and maximum speed 1 MHz, runs `spi_setup()`, creates a SPI regmap, and delegates to `rm3100_common_probe()` with SPI IRQ. Module registration is via `module_spi_driver()`.

State/persistence: the wrapper owns no sensor state beyond bus configuration and devm regmap; all data path state lives in the core.

Dependencies/integration: depends on SPI, regmap-SPI, RM3100 common core/header, OF matching, and namespace import `IIO_RM3100`. Built by `CONFIG_SENSORS_RM3100_SPI`.

Risks: probe overwrites board-provided SPI mode/speed to supported values. There is no SPI id table, so matching is OF-centric. Correct reads depend on the `0x80` read flag matching the bus protocol. No PM support is present.

Test signals: instantiate OF SPI devices, verify mode/speed setup, regmap reads/writes, IRQ forwarding, direct and buffered core paths, and module namespace checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100.h -->
## sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100.h

Purpose: private shared header for RM3100 bus wrappers and common core.

Important APIs/types/functions: declares exported regmap access tables `rm3100_readable_table`, `rm3100_writable_table`, and `rm3100_volatile_table`, plus `rm3100_common_probe(struct device *dev, struct regmap *regmap, int irq)`.

Control flow: no executable flow. I2C/SPI wrappers include the header, build a transport-specific regmap from the exported access tables, and call the common probe.

State/persistence: no stored state. The declarations define the compile-time contract for sharing core IIO state through the bus device.

Dependencies/integration: includes Linux regmap declarations and relies on kernel device declarations from includers or transitive headers. It is tied to module namespace `IIO_RM3100`.

Risks: signature or namespace changes require synchronized updates in core and wrappers. Missing explicit `<linux/device.h>` include can be fragile if include ordering changes.

Test signals: compile RM3100 core with I2C and SPI wrappers as modules and built-ins, and run modpost namespace/import checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/magnetometer/rm3100.h -->
