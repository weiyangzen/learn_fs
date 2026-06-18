# subset-b-003865 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/sca3300.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/sca3300.c

Purpose: SPI IIO driver for Murata SCA3300 and SCL3300 industrial accelerometers. It exposes direct raw reads, scale and low-pass filter controls, triggered buffered samples, and SCL3300 inclinometer channels.

Important APIs/types/functions: `struct sca3300_chip_info` captures per-variant channel lists, scan masks, scale/frequency tables, operating modes, chip id, and angle support. `struct sca3300_data` stores the SPI device, a mutex, selected chip metadata, and DMA-aligned transfer buffers. `sca3300_transfer()` performs the two-phase SPI transaction with inverted CRC8 validation and return-status checking. `sca3300_read_reg()`, `sca3300_write_reg()`, `sca3300_set_op_mode()`, `sca3300_get_op_mode()`, `sca3300_read_raw()`, `sca3300_write_raw()`, `sca3300_read_avail()`, `sca3300_trigger_handler()`, `sca3300_init()`, and `sca3300_probe()` form the main control surface.

Control flow: probe allocates an IIO device, initializes the CRC table and mutex, performs a software reset, waits for settling, reads `WHOAMI`, selects the chip table entry, enables SCL3300 angle output when supported, configures channels and scan masks, sets up a triggered buffer, and registers the IIO device. Direct reads issue a register read for the channel address. Scale and low-pass writes select an operating mode, preserving current scale when changing filter frequency. Buffered capture iterates active channels, reads each register, and pushes a timestamped sample.

State and persistence behavior: driver state is devm-managed except for the chip operating mode held in hardware registers. Mode writes persist in the sensor until reset or later writes. The mutex serializes access to the shared TX/RX buffers and the command/status flow.

Dependencies and integration points: depends on SPI, CRC8, IIO direct and triggered-buffer APIs, `iio_pollfunc_store_time`, debugfs register access, and OF/SPI modalias binding for `murata,sca3300` and `murata,scl3300`.

Risks: CRC, return-status, and delayed two-transfer sequencing are central to correctness; changing SPI message structure can break the protocol. `sca3300_set_frequency()` can only select a mode that preserves the current scale, which may surprise callers. Error handling intentionally reads status after `-EINVAL`; treating that code as a plain failure would lose diagnostic recovery. Buffered data is read channel by channel rather than as one atomic hardware sample.

Test signals: build with SPI and IIO buffer support; bind both SCA3300 and SCL3300 ids; validate unknown chip-id rejection, CRC failure handling, raw reads, scale and low-pass available lists, mode changes, debugfs bounds, SCL inclinometer channels, and triggered-buffer samples with all active channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/sca3300.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/ssp_accel_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/ssp_accel_sensor.c

Purpose: Samsung Sensor Platform accelerometer IIO consumer driver. It exposes the sensorhub accelerometer as a three-axis IIO accelerometer with buffered data and writable sampling frequency.

Important APIs/types/functions: `ssp_accel_read_raw()` reports sampling frequency by reading the sensor delay through `ssp_get_sensor_delay()` and converting time to frequency. `ssp_accel_write_raw()` converts frequency to delay and calls `ssp_change_delay()`. `ssp_process_accel_data()` delegates packet decoding to `ssp_common_process_data()`. `ssp_accel_probe()` allocates and registers the IIO device, kfifo buffer, channel table, scan mask, and SSP consumer registration.

Control flow: the platform driver probes after the SSP sensorhub core creates the platform device. Probe allocates `struct ssp_sensor_data` as IIO private data, sets the process callback and sensor type, configures X/Y/Z plus timestamp channels, installs common buffer postenable/postdisable operations, registers the IIO device, and finally calls `ssp_register_consumer()` so the hub can deliver accelerometer frames.

State and persistence behavior: this file owns no hardware registers. Sampling period state lives in the SSP core and sensorhub firmware. The IIO private state stores only the process callback and sensor type. Buffer lifetime is devm-managed.

Dependencies and integration points: integrates with `linux/iio/common/ssp_sensors.h`, the local `ssp_iio_sensor.h` helpers, kfifo IIO buffers, and the parent SSP device found through `indio_dev->dev.parent->parent`.

Risks: the driver assumes a fixed parent-device hierarchy to find `struct ssp_data`; platform topology changes can break delay reads and writes. Data parsing size is fixed to `SSP_ACCELEROMETER_SIZE`, so hub ABI changes must be synchronized. Sampling-frequency writes log "enable fail" for all negative `ssp_change_delay()` returns, even if the failure is not an enable failure.

Test signals: build with SSP sensor support, instantiate `ssp-accelerometer`, verify three accelerometer channels plus timestamp, read and write `sampling_frequency`, enable/disable the kfifo buffer, and inject SSP frames to confirm `ssp_common_process_data()` pushes expected samples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/ssp_accel_sensor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel.h

Purpose: private header shared by the STMicroelectronics accelerometer core, buffer helper, and I2C/SPI transport wrappers.

Important APIs/types/functions: declares the canonical device-name strings used by the settings table and bus match tables, including LIS3DH, LSM303 variants, LIS2DW12, LIS3DHH, SC7A20, and IIS328DQ. When `CONFIG_IIO_BUFFER` is enabled it declares `st_accel_allocate_ring()` and `st_accel_trig_set_state()` and maps `ST_ACCEL_TRIGGER_SET_STATE` to the trigger callback; otherwise it provides a no-op ring allocator and a NULL trigger callback.

Control flow: no runtime control flow exists in the header. Its conditional declarations determine whether the common probe can allocate a triggered buffer and expose a data-ready trigger callback.

State and persistence behavior: no state is stored. The names in this header are contract values used by bus modalias matching and `st_accel_get_settings()`.

Dependencies and integration points: includes `linux/iio/common/st_sensors.h` and is included by `st_accel_core.c`, `st_accel_buffer.c`, `st_accel_i2c.c`, and `st_accel_spi.c`.

Risks: device-name strings must stay synchronized with Kconfig/module aliases, OF/ACPI/I2C/SPI id tables, and the settings table. A mismatch causes probe to fail with "device name not recognized." The `CONFIG_IIO_BUFFER` stubs mean builds without buffer support still compile, but trigger-specific behavior silently disappears.

Test signals: compile both buffered and non-buffered configurations, verify all bus id-table names resolve through `st_accel_get_settings()`, and run modpost/export checks for `IIO_ST_SENSORS` namespace users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_buffer.c

Purpose: triggered-buffer support for the shared ST accelerometer driver.

Important APIs/types/functions: `st_accel_trig_set_state()` enables or disables the common ST data-ready IRQ through `st_sensors_set_dataready_irq()`. `st_accel_buffer_postenable()` restricts enabled axes to the active scan mask and powers the sensor on. `st_accel_buffer_predisable()` powers the sensor off and restores all axes. `st_accel_allocate_ring()` installs a devm triggered buffer using the common `st_sensors_trigger_handler()`.

Control flow: when a buffer is enabled, IIO calls `postenable`, which programs the axis mask first and then enables the sensor. If enabling fails, it restores all axes before returning the error. When the buffer is disabled, IIO calls `predisable`, which powers the device off and re-enables all axes for direct reads. Trigger state changes go directly to the shared ST IRQ helper.

State and persistence behavior: no private state is stored in this file. It mutates device registers through shared ST sensor helpers for axis selection, power state, and data-ready IRQ state. The register settings persist until another helper call changes them.

Dependencies and integration points: depends on IIO buffer/triggered-buffer APIs and the ST common sensor helpers. The core probe calls `st_accel_allocate_ring()` and passes `ST_ACCEL_TRIGGER_SET_STATE` into trigger allocation when an IRQ is present.

Risks: active scan masks are represented as `indio_dev->active_scan_mask[0]`; this assumes the three accelerometer axes fit in the first mask word. Error recovery only restores axes when power-on fails, not if axis programming fails. Buffer state transitions depend on the common ST helper semantics for power and axis registers.

Test signals: enable buffers with all axes and subsets, verify axis-enable register programming, test power-on failure cleanup, disable buffers and confirm all axes are restored, and validate IRQ trigger enable/disable on boards with a data-ready interrupt.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_core.c

Purpose: common IIO core for a large family of ST-compatible accelerometers. It provides channel layouts, per-chip register settings, scale and sampling-frequency handling, mount-matrix support, trigger integration, and the common probe used by I2C and SPI wrappers.

Important APIs/types/functions: `st_accel_sensors_settings[]` is the main device database, mapping supported names and WAI ids to channel widths, output registers, ODR tables, power bits, axis-enable registers, full-scale gains, block-data-update bits, data-ready IRQ wiring, SPI mode bits, multiread flags, and boot delays. `st_accel_read_raw()` and `st_accel_write_raw()` implement raw, scale, and sampling-frequency IIO operations through shared ST helpers. `apply_acpi_orientation()` converts ST `_ONT` ACPI orientation packages to an IIO mount matrix. `st_accel_get_settings()` and `st_accel_common_probe()` are exported in the `IIO_ST_SENSORS` namespace.

Control flow: bus wrappers identify a chip by device name, configure bus access, power supplies, and call `st_accel_common_probe()`. The common probe verifies chip id, assigns channels, reads ACPI or generic firmware orientation, initializes default full-scale and ODR from the first table entries, initializes the sensor registers, allocates the ring buffer, optionally allocates a trigger when an IRQ exists, and registers the IIO device.

State and persistence behavior: `struct st_sensor_data` holds the selected settings table, current full-scale entry, current ODR, mount matrix, bus accessors, and IRQ data. Hardware registers retain configured ODR, power, full-scale, BDU, data alignment, axis, and IRQ settings until changed or reset.

Dependencies and integration points: depends on `linux/iio/common/st_sensors.h`, IIO sysfs/debugfs/trigger APIs, ACPI, firmware mount matrices, and the buffer helper in `st_accel_buffer.c`. It is consumed by both `st_accel_i2c.c` and `st_accel_spi.c`.

Risks: most behavior is table-driven, so a wrong mask, gain, WAI id, multiread flag, or IRQ bit affects a whole chip family. Some table comments mark guessed boot times or uncertain gains. `_ONT` translation is ST-specific and intentionally applies an extra matrix transform before generic mount-matrix fallback. The common code assumes three data channels plus timestamp.

Test signals: build all transports, probe every id-table name against expected settings, validate WAI verification including parts with no WAI register, check raw sign/shift for 8/12/16-bit layouts, verify available scale and ODR sysfs values, test ACPI `_ONT` and generic mount matrices, run triggered-buffer paths with data-ready IRQs, and use debugfs register access for bus read/write coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_i2c.c

Purpose: I2C transport wrapper for the shared ST accelerometer core.

Important APIs/types/functions: the OF match table maps many `st,*-accel` and compatible strings to canonical device names. The ACPI table handles `SMO8840` and `SMO8A90`. The I2C id table lists supported modalias names. `st_accel_i2c_probe()` normalizes the device name, looks up settings with `st_accel_get_settings()`, allocates the IIO device, stores the settings pointer, calls `st_sensors_i2c_configure()`, enables power, and delegates to `st_accel_common_probe()`.

Control flow: `module_i2c_driver()` registers the wrapper. Probe fails early on unknown names, allocation failure, bus configuration failure, or regulator/power failure. All sensor initialization, IIO registration, buffering, and trigger setup happen in the common core.

State and persistence behavior: the wrapper owns no independent runtime state beyond IIO private `struct st_sensor_data`. Power enable and register programming are delegated to shared ST helpers and the common probe.

Dependencies and integration points: depends on Linux I2C, OF/ACPI modalias matching, `st_sensors_i2c_configure()`, `st_sensors_power_enable()`, and exported common ST accelerometer symbols.

Risks: compatible strings and id-table names must match the header constants and settings table. `st_sensors_dev_name_probe()` mutates `client->name` based on firmware match data, so name length and firmware data correctness affect probe. Adding a new chip requires updates in the settings table, header, and this bus table.

Test signals: compile as module or built-in, instantiate through I2C id, OF, and ACPI paths, verify unknown names return `-ENODEV`, inject I2C configure and power failures, and confirm successful devices get the channel set and sysfs attributes from `st_accel_common_probe()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_spi.c

Purpose: SPI transport wrapper for the shared ST accelerometer core.

Important APIs/types/functions: the OF table maps supported SPI-compatible strings to canonical device names. The SPI id table lists modalias names. `st_accel_spi_probe()` normalizes `spi->modalias`, retrieves settings through `st_accel_get_settings()`, allocates the IIO device, records settings in `struct st_sensor_data`, configures SPI bus access via `st_sensors_spi_configure()`, enables power, and calls `st_accel_common_probe()`.

Control flow: `module_spi_driver()` registers the wrapper. Probe is intentionally thin: bus identification and access setup happen locally, while chip-id verification, channel assignment, register initialization, buffer setup, trigger setup, and IIO registration are delegated to the core.

State and persistence behavior: no wrapper-specific persistent state. The shared ST sensor state is allocated as IIO private data, and hardware register state is managed by the common core and ST helpers.

Dependencies and integration points: depends on SPI, OF modalias matching, `st_sensors_spi_configure()`, `st_sensors_power_enable()`, and the exported core functions in the `IIO_ST_SENSORS` namespace.

Risks: SPI support lacks ACPI matching unlike the I2C wrapper. Compatible strings need careful maintenance for old `*-accel` names and newer single-chip names. Some ST parts have bus-specific quirks such as SIM and multiread settings; incorrect settings-table values surface through this wrapper.

Test signals: compile with SPI support, bind through SPI id and OF compatible strings, validate unknown modalias rejection, inject SPI configuration and power failures, and run common ST raw, scale, ODR, and triggered-buffer tests over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/st_accel_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/stk8312.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/stk8312.c

Purpose: I2C IIO driver for the Sensortek STK8312 three-axis 8-bit accelerometer.

Important APIs/types/functions: `struct stk8312_data` stores the I2C client, mutex, range, sample-rate index, mode byte, optional data-ready trigger, trigger state, and aligned scan buffer. `stk8312_otp_init()` loads OTP trim data into AFE control. `stk8312_set_mode()`, `stk8312_set_interrupts()`, `stk8312_set_sample_rate()`, and `stk8312_set_range()` update hardware configuration, usually by entering standby first. `stk8312_read_raw()`, `stk8312_write_raw()`, `stk8312_trigger_handler()`, `stk8312_probe()`, remove, suspend, and resume implement the IIO lifecycle.

Control flow: probe allocates state, resets the sensor, sets default 400 Hz and +/-6 g, enters active interrupt mode, optionally requests an IRQ and registers an IIO trigger, installs a triggered buffer, and registers the IIO device. Direct raw reads reject active buffers, activate the sensor, read one axis, sign-extend it, and return to standby. Buffer enable powers active mode; disable returns to standby. Triggered capture bulk-reads all axes when possible or reads selected axes individually.

State and persistence behavior: `range`, `sample_rate_idx`, `mode`, and `dready_trigger_on` mirror hardware state. OTP initialization is rerun when entering active mode. Remove and PM suspend place the chip in standby; resume restores active mode based on cached mode bits.

Dependencies and integration points: depends on I2C SMBus byte/block access, IIO sysfs attributes, IIO triggered buffers, optional IRQ-backed data-ready triggers, and PM sleep callbacks.

Risks: range values are stored as one-based indices, so scale lookup depends on `range - 1`. Mode-changing helpers attempt to restore prior mode on configuration failures but some restore errors are ignored. OTP readiness polling has a fixed retry count and can make active transitions fail. Buffered partial-channel reads pass the scan bit as the register address, which matches X/Y/Z register values only because they are 0, 1, and 2.

Test signals: probe/reset success and failure paths, OTP timeout and zero-data rejection, raw reads while buffer is disabled/enabled, scale and sampling-frequency writes, IRQ trigger enable/disable, full and partial scan masks, remove cleanup, and suspend/resume standby/active transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/stk8312.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/stk8ba50.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/stk8ba50.c

Purpose: I2C IIO driver for the Sensortek STK8BA50 three-axis 10-bit accelerometer.

Important APIs/types/functions: `struct stk8ba50_data` stores the I2C client, mutex, range table index, sample-rate index, optional trigger, trigger state, and aligned scan buffer. `stk8ba50_set_power()` toggles suspend/normal mode. `stk8ba50_read_raw()` and `stk8ba50_write_raw()` implement direct raw reads, scale selection, and sample-rate selection. `stk8ba50_trigger_handler()` handles buffered capture, while probe/remove and PM callbacks manage lifecycle.

Control flow: probe allocates and initializes the IIO device, resets the chip, initializes default +/-2 g and 1792 Hz cached settings, enables and maps data-ready interrupts, optionally registers an IRQ-backed trigger, sets up the triggered buffer, and registers the IIO device. Direct raw reads power the chip on, read a word from the axis register, shift/sign-extend the 10-bit sample, and suspend the chip. Buffer enable powers normal mode and buffer disable suspends it. Triggered capture bulk-reads six bytes for all axes or reads selected axis words.

State and persistence behavior: range and sample-rate caches mirror the latest successful register writes. The power bit is toggled for direct reads, buffers, suspend, resume, and cleanup. Trigger registration is manual rather than devm for `iio_trigger_register()`, so remove and error paths unregister it explicitly.

Dependencies and integration points: depends on I2C SMBus word/block access, IIO buffers/triggers, optional ACPI id `STK8BA50`, I2C modalias `stk8ba50`, and PM sleep callbacks.

Risks: the channel macro has a suspicious comma after `BIT(IIO_CHAN_INFO_SCALE)` before `BIT(IIO_CHAN_INFO_SAMP_FREQ)`, so sampling-frequency mask exposure should be checked carefully. Probe enables data-ready interrupts even when no IRQ is present. `stk8ba50_set_power()` uses a boolean-like argument with inverted naming (`STK8BA50_MODE_NORMAL` is zero and clears the power bit). Direct-read errors are collapsed to `-EINVAL`, losing original I2C error codes.

Test signals: compile with warnings enabled, inspect IIO channel masks for sampling-frequency visibility, probe over I2C and ACPI, validate reset and interrupt register writes, raw read sign extension, scale/rate writes, full and partial buffered scans, trigger enable/disable, and suspend/resume power-bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/stk8ba50.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/88pm886-gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/88pm886-gpadc.c

Purpose: IIO GPADC driver for the Marvell 88PM886 PMIC. It exposes internal voltages, external GPADC resistance channels, ground/mic detection voltages, and internal temperature.

Important APIs/types/functions: `struct pm886_gpadc` stores the GPADC regmap. `pm886_gpadc_channels[]` defines voltage, resistance, and temperature IIO channels with per-channel LSB scaling in `address`. `gpadc_get_raw()` bulk-reads a big-endian 12-bit ADC value. `gpadc_set_bias()`, `gpadc_find_bias_current()`, and `gpadc_get_resistance_ohm()` enable bias currents and calculate resistance. `pm886_gpadc_read_raw()`, runtime PM callbacks, and `pm886_gpadc_probe()` complete the driver.

Control flow: probe obtains the parent PMIC and I2C client, creates a dummy I2C device for the GPADC page, initializes an 8-bit regmap, configures the IIO device, ties its fwnode to the parent, enables runtime PM with autosuspend, and registers the IIO device. Each read resumes the device, dispatches raw/scale/offset/processed handling, and autosuspends. Runtime resume enables the ADC block and all channels; runtime suspend disables the block.

State and persistence behavior: driver state is only the regmap pointer. Hardware state is runtime-managed: enabling the ADC and channels on resume, disabling the ADC block on suspend, and briefly enabling per-GPADC bias for resistance reads.

Dependencies and integration points: depends on the 88PM886 MFD core, I2C dummy page addressing, regmap, runtime PM, IIO direct mode, and PMIC register definitions in `linux/mfd/88pm886.h`.

Risks: resistance reads dynamically choose bias levels and reject voltages outside hard-coded empirical bounds; board differences can affect measurability. `gpadc_get_resistance_ohm()` tries to turn bias off even after failures but ignores that cleanup error. Temperature scale/offset reporting relies on IIO fractional semantics with absolute-zero offset. Runtime PM must be active for all register reads.

Test signals: probe with valid and failing dummy-page/regmap creation, raw voltage reads, processed resistance reads across bias levels, temperature raw/scale/offset reads, runtime suspend/resume register writes, autosuspend behavior, and regmap failure injection for bulk reads and bias programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/88pm886-gpadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/Kconfig

Purpose: Kconfig menu for IIO analog-to-digital converter drivers under `drivers/iio/adc`.

Important APIs/types/functions: defines `menu "Analog to digital converters"` and one `config` symbol per ADC helper/core/driver. Relevant symbols for this subset include `IIO_ADC_HELPER`, `88PM886_GPADC`, `AB8500_GPADC`, and `AD4000`. Many entries express bus and subsystem dependencies (`SPI`, `I2C`, `MFD_*`, `REGULATOR`, `COMMON_CLK`, `GPIOLIB`, `THERMAL`, `HAS_IOMEM`) and select IIO buffer, DMA, trigger, regmap, backend, and SPI offload helpers.

Control flow: Kconfig has no runtime flow, but controls build inclusion and dependency propagation. `88PM886_GPADC` depends on and defaults to the 88PM886 PMIC MFD. `AB8500_GPADC` is a built-in boolean depending on AB8500 core and regulator support. `AD4000` depends on SPI and selects IIO buffer, DMAengine buffer, triggered buffer, and SPI offload infrastructure.

State and persistence behavior: no runtime state. The selected symbols persist in kernel `.config` and determine which objects the Makefile builds.

Dependencies and integration points: consumed by the kernel Kconfig system and paired with `drivers/iio/adc/Makefile`. It coordinates helper symbols shared by multiple drivers, such as `AD_SIGMA_DELTA`, `AD7091R`, `AD7606`, `QCOM_VADC_COMMON`, `STM32_DFSDM_CORE`, and `IIO_ADC_HELPER`.

Risks: dependency mistakes can expose drivers without required APIs or hide valid build combinations. `select` can force helper subsystems on, so selected symbols must not have unmet direct dependencies. The file relies on approximate alphabetical ordering; misplaced entries complicate maintenance. Help text module names must match Makefile object names and actual module output.

Test signals: run `make olddefconfig` and targeted `allyesconfig`/`allmodconfig` builds, verify `CONFIG_88PM886_GPADC`, `CONFIG_AB8500_GPADC`, and `CONFIG_AD4000` produce expected objects, check unmet dependency warnings, and compare new entries against alphabetical order and Makefile additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/Makefile

Purpose: kernel build mapping from ADC Kconfig symbols to objects in `drivers/iio/adc`.

Important APIs/types/functions: contains `obj-$(CONFIG_...) += ...` assignments for each ADC driver or helper object. Relevant subset entries are `obj-$(CONFIG_88PM886_GPADC) += 88pm886-gpadc.o`, `obj-$(CONFIG_AB8500_GPADC) += ab8500-gpadc.o`, and `obj-$(CONFIG_AD4000) += ad4000.o`. Some symbols build multiple objects, such as LTC2496/LTC2497 sharing `ltc2497-core.o`, and Xilinx XADC using a composite `xilinx-xadc-y`.

Control flow: no runtime flow. During kbuild, enabled or modular config symbols expand into built-in or module object lists. The list is intended to remain alphabetically ordered when adding entries.

State and persistence behavior: no state beyond build outputs. The file determines which `.o` files are linked into vmlinux or modules.

Dependencies and integration points: paired with `Kconfig` symbols and source files in the same directory. It also integrates composite object definitions for multi-file drivers.

Risks: missing or misspelled object mappings make a visible Kconfig option build nothing or fail late. A mismatch between Kconfig help module names and object names confuses users. Shared-core object mappings must include all required objects under each dependent symbol.

Test signals: run targeted builds for `CONFIG_88PM886_GPADC`, `CONFIG_AB8500_GPADC`, and `CONFIG_AD4000` as built-in/module where applicable; run `make drivers/iio/adc/`; and verify new Kconfig entries have matching Makefile objects in alphabetical order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ab8500-gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ab8500-gpadc.c

Purpose: built-in IIO GPADC driver for ST-Ericsson AB8500/AB8540 PMICs. It arbitrates software and hardware ADC conversions for battery, charger, accessory, die-temperature, VBAT, VBUS, current, and board-defined channels.

Important APIs/types/functions: `enum ab8500_gpadc_channel` defines hardware and virtual channels. `struct ab8500_gpadc_chan_info` stores per-firmware-channel id, hardware-trigger mode, edge, averaging, and trigger timer. `struct ab8500_gpadc` stores parent device, AB8500 handle, channel table, completion, regulator, IRQs, and calibration data. `ab8500_gpadc_read()` performs conversion sequencing. `ab8500_gpadc_ad_to_voltage()` applies calibrated or interpolated conversion. `ab8500_gpadc_read_calibration_data()` decodes OTP calibration. `ab8500_gpadc_parse_channels()`, `ab8500_gpadc_read_raw()`, PM callbacks, probe, and remove complete the driver.

Control flow: probe parses child firmware nodes into IIO channels, requests software and optional hardware conversion IRQs, gets and enables `vddadc`, enables runtime PM, reads calibration data, registers the IIO device, and leaves the regulator under autosuspend. A read locates the channel, waits for the GPADC not busy, programs averaging and software or hardware trigger registers, enables required buffers/current paths, starts conversion or arms trigger timing, waits for completion IRQ, reads raw data registers, optionally reads a second IBAT conversion, disables GPADC, and releases runtime PM.

State and persistence behavior: calibration gain/offsets are cached for VMAIN, BTEMP, VBAT, and IBAT. Firmware channel definitions persist in devm memory. Runtime PM controls the ADC regulator. Hardware control registers are rewritten for each conversion and disabled afterward.

Dependencies and integration points: depends on AB8500 MFD register access (`abx500_*`), regulator framework, runtime PM, threaded IRQ completions, firmware child nodes, IIO fwnode xlate, and built-in platform-driver registration.

Risks: conversion is not protected by an explicit mutex; it relies on the GPADC busy bit and hardware arbitration, so concurrent consumers can contend. OTP decoding divides by calibration-code deltas without explicit zero checks. Error paths force-disable GPADC and drop PM, but cleanup writes can fail silently. Hardware-triggered double conversions are unsupported. Channel type mapping treats temperatures as voltage-like except current channels.

Test signals: DT child-node parsing and fwnode xlate, missing IRQ/regulator failures, software conversion success and timeout, hardware conversion on AB8500, busy-bit timeout, calibrated and fallback conversion math, IBAT double conversion, runtime PM regulator transitions, and AB8540-specific OTP paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ab8500-gpadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4000.c

Purpose: SPI IIO driver for Analog Devices AD4000-family high-speed SAR ADCs and related AD768x/AD769x/AD794x/AD798x/AD402x/ADAQ400x devices. It supports direct reads, triggered buffers, optional register access, optional span compression, optional hardware gain, and SPI offload DMA streaming.

Important APIs/types/functions: `struct ad4000_chip_info` describes per-device channel specs, register-access channel specs, offload specs, timing, hardware-gain support, and max sample rate. `struct ad4000_state` stores SPI device, optional CNV GPIO, prepared SPI messages, offload handles, sample-rate state, mutex, reference voltage, SDI wiring mode, span compression, gain, scale table, timing, and DMA-aligned buffers. Core functions include `ad4000_fill_scale_tbl()`, register read/write helpers, `ad4000_single_conversion()`, raw/read/write callbacks, offload buffer setup, mode-specific SPI message preparation, `ad4000_config()`, and `ad4000_probe()`.

Control flow: probe matches chip info, enables VDD/VIO and reference regulators, reads optional CNV GPIO, obtains optional SPI offload, sets up either DMA offload buffer or normal triggered buffer, parses `adi,sdi-pin`, prepares the correct SPI message for 3-wire or 4-wire wiring, configures register-capable devices when SDI is MOSI, initializes hardware gain and scale table, and registers the IIO device. Direct raw reads claim direct mode, pulse/transfer through the prepared message, decode endianness and sign, and release direct mode. Buffer reads use either IIO triggered polling or offload trigger/DMA.

State and persistence behavior: `span_comp`, `gain_milli`, `offload_trigger_hz`, scale table, and wiring mode live in driver state. Hardware config register writes persist span compression, high-Z mode, and turbo/offload mode. Prepared SPI messages are optimized once at probe.

Dependencies and integration points: depends on SPI, regulators, optional GPIO, IIO buffers, DMAengine buffer namespace, triggered buffers, SPI offload trigger/RX DMA, firmware properties, and OF/SPI id tables for many compatible devices.

Risks: wiring mode is critical: offload only supports the 3-wire VIO/default style and rejects `adi,sdi-pin = "cs"` or `"low"`. Offload samples omit soft timestamps and use CPU-endian packed words. Register access and span compression are only available when SDI is controllable through MOSI. Scale math combines reference voltage, sign bit width, hardware gain, and span compression; mistakes produce user-visible unit errors. Prepared SPI timing must satisfy each chip's conversion and quiet-time specs.

Test signals: build with and without SPI offload support, probe every OF/SPI id, validate regulator and reference failures, direct raw reads for 14/16/18/20-bit signed and unsigned devices, scale/offset and span-compression writes, `adi,gain-milli` selection for ADAQ parts, all `adi,sdi-pin` modes, triggered-buffer samples, offload DMA streaming and sample-frequency limits, and SPI timing/message validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4000.c -->
