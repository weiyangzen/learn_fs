# Research: subset-b-003888

Grouped research for Linux IIO IMU files under `sources/distributed-fs/ceph-client/drivers/iio/imu`. Each section preserves its source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16475.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16475.c

Purpose: SPI IIO driver for the ADIS16470/16475/16477/16465/16467/16500/16501/16505/16507/16575/16576/16577 IMU family. It exposes gyro, accel, temperature, and for some variants delta-angle/delta-velocity channels, with optional hardware FIFO support for ADIS1657x parts.

Important APIs, types, and functions: `struct adis16475_chip_info` carries channel tables, scale constants, sync-mode limits, feature flags, and embedded `struct adis_data`. `struct adis16475` holds the shared ADIS state, clock rate, burst32 state, LSB mode flags, sync mode, FIFO watermark, and aligned scan buffer. `adis16475_read_raw()` and `adis16475_write_raw()` implement raw reads, calibration bias, sampling frequency, scale, and 3 dB filter controls. `adis16475_update_scan_mode()` selects gyro/accel versus delta burst groups on devices with selectable burst data. `adis16475_trigger_handler()` and `adis16475_trigger_handler_with_fifo()` own buffered acquisition. `adis16475_probe()` initializes ADIS, configures IRQ polarity, sync mode, buffer/trigger, FIFO behavior, debugfs, and IIO registration.

Control flow: probe obtains match data, initializes `adis`, runs initial startup, configures the IRQ pin, configures internal or external sync, then selects either normal or FIFO buffer setup. Non-FIFO triggers perform one burst read, validate checksum, translate active scan bits into aligned IIO buffer data, then possibly toggle burst32 mode after the current sample. FIFO triggers read `FIFO_CNT`, prime the FIFO pop command, push all available samples, and finish with a non-pop read.

State and persistence: register state persists in device registers: decimation, filter, sync scale/mode, FIFO control, watermark, calibration bias, and burst32 enable. Driver state mirrors the selected clock rate, `lsb_flag`, `burst32`, and watermark. Debugfs exposes firmware, serial, product, and flash count but does not persist new host state.

Dependencies and integration: integrates with `linux/iio/imu/adis.h`, shared ADIS buffer and trigger helpers, SPI, clocks, firmware properties (`adi,sync-mode`), IRQ trigger type, IIO sysfs/debugfs, and module parameter `low_rate_allow`.

Risks: sync-scaled math can clamp requested sample rates, especially with low external clocks; `low_rate_allow` changes undersampling policy globally. Burst32 mode mutates SPI transfer length at runtime and must remain synchronized with decimation/FIR state. FIFO burst protocol is order-sensitive; any unexpected register access between FIFO pop/read phases can lose a sample. CRC/checksum errors drop samples. IRQ type validation differs between FIFO level interrupts and data-ready edge interrupts.

Test signals: probe each compatible variant through OF/SPI IDs; verify `sampling_frequency`, filter, calibration bias, FIFO watermark, and debugfs reads. Exercise scan masks for gyro/accel versus delta data, decimation/FIR transitions that toggle burst32, CRC failure injection, external clock sync modes, FIFO watermark interrupts, and buffer enable/disable flushing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16475.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16480.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16480.c

Purpose: SPI IIO driver for ADIS16375/16480/16485/16486/16487/16488/16489/16490/16495/16497/16545/16547 style IMUs. It covers gyro, accel, temperature, optional magnetometer, pressure, and optional delta angle/velocity burst data.

Important APIs, types, and functions: `struct adis16480_chip_info` captures channel layout, scale constants, filter tables, internal clock, decimation max, PPS support, sleep support, delta-burst support, and embedded `adis_data`. `struct adis16480` stores ADIS state, optional external clock, clock mode, sample clock, selected burst ID, and aligned data buffer. `adis16480_set_freq()` and `adis16480_get_freq()` manage decimation and PPS sync scaling. Calibration and filter paths are split across `adis16480_{get,set}_calibbias()`, `adis16480_{get,set}_calibscale()`, and `adis16480_{get,set}_filter_freq()`. `adis16480_trigger_handler()` performs page-safe burst reads and CRC32 validation.

Control flow: probe selects chip info by SPI ID, sets IIO channels and optional available scan masks, initializes ADIS, runs startup, optionally registers a sleep-count powerdown action, configures the data-ready pin, discovers optional `sync` or `pps` clocks, configures external clock function pins, then sets up ADIS buffer/trigger. Burst-capable chips use the custom handler; older chips use the generic ADIS handler.

State and persistence: device registers hold page-selected configuration, decimation, FIR bank enables, calibration bias/scale, DRDY pin selection/polarity, external sync mode, PPS sync scale, and sleep count. `st->burst_id` changes when ADIS16545/16547 scan masks switch between gyro/accel and delta data. `adis->current_page` is normalized before burst capture.

Dependencies and integration: uses ADIS library paging, SPI, Linux clock framework (`sync` and `pps`), fwnode IRQ lookup by DIO name, device property `adi,ext-clk-pin`, IIO debugfs, IIO triggered buffers, and CRC32.

Risks: OF match entries do not carry `.data`, so SPI ID matching is central to `driver_data`. Burst alignment depends on finding the transition from repeated burst IDs to system flags; wrong SCLK behavior or corrupted payloads can invalidate the sample. External clock pin conflicts with DRDY are warned but not prevented. PPS scaling clamps low rates unless `low_rate_allow` is set. Filter register bit packing differs per scan index and can regress per-axis configuration.

Test signals: test variant probe IDs, burst and non-burst capture, CRC failure handling, page reset before capture, DIO pin selection/polarity, optional sleep action, external `sync`/`pps` clocks, ADIS16545 scan-mask switching, calibration read/write widths, filter frequency enable/disable, and sample-frequency rounding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16480.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16550.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16550.c

Purpose: SPI IIO driver for the ADIS16550 IMU. It exposes temperature, gyro, accel, delta angle, and delta velocity channels and implements the device's newer 32-bit SPI protocol rather than relying on the default ADIS 16-bit register transfers.

Important APIs, types, and functions: `struct adis16550_chip_info` defines channels, scale constants, sync modes, and decimation limits. `struct adis16550` embeds ADIS state plus custom SPI transfers, command/response buffers, and burst buffer. `adis16550_spi_read()`, `adis16550_spi_write()`, `adis16550_spi_xfer()`, `adis16550_spi_msg_prepare()`, and `adis16550_spi_validate()` implement register access with CRC4 and state-vector validation. `adis16550_trigger_handler()` validates the burst header and CRC32 payload before pushing buffer data. `adis16550_config_sync()` configures optional external sync.

Control flow: probe allocates IIO state, wires custom `adis_ops`, prepares a two-transfer burst SPI message, enables `vdd`, initializes ADIS, performs startup, configures sync, installs buffer/trigger, registers IIO, and creates debugfs entries. Update-scan-mode chooses either gyro/accel or delta-angle/velocity burst command and writes the CRC4-protected command into the TX tail buffer.

State and persistence: persistent device settings include decimation, sync enable/mode/scale, FIR enables, calibration scale/bias, and command-triggered reset/self-test. Host state tracks selected clock rate, sync mode, and prepared burst command. Register writes validate readback, except command writes are exempt because command registers need not echo normal data.

Dependencies and integration: uses IIO ADIS library for lifecycle, status checking, buffer/trigger setup, and debugfs register access, but overrides ADIS read/write/reset operations. It depends on SPI, clock, regulator `vdd`, CRC32, bitfield helpers, and unaligned access helpers.

Risks: CRC4 and state-vector validation are mandatory for every register access; any protocol bit packing change can make the device unusable. `adis16550_config_sync()` appears to compare calculated `sync_scale` against 3000..4500 even though `sync_scale` is derived from clock division, so external scaled-sync edge cases deserve hardware review. Burst handler currently copies a fixed contiguous block for temperature plus six inertial channels; scan masks are constrained to full groups, so partial-scan expectations must not leak in. Regulator, clock, and ADIS startup ordering are all probe-critical.

Test signals: validate 16-bit and 32-bit register reads/writes, command reset exemption, CRC4/state-vector failures, burst CRC32 failure, both available scan masks, direct and scaled external clock modes, FIR frequency sysfs, calibration scale/bias, regulator failure, and debugfs metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16550.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_buffer.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_buffer.c

Purpose: shared ADIS16xxx IIO buffer helper. It builds SPI transfer messages for either burst-mode or per-channel register reads, provides a generic trigger handler, and exposes `devm_adis_setup_buffer_and_trigger_with_attrs()` for ADIS drivers.

Important APIs, types, and functions: `adis_update_scan_mode()` is exported in namespace `IIO_ADISLIB` and rebuilds `adis->xfer`, `adis->buffer`, and `adis->msg` for the active scan mask. `adis_update_scan_mode_burst()` builds a two-transfer burst request/read sequence. `adis_paging_trigger_handler()` forces paged devices back to page 0 before capture. `adis_trigger_handler()` is the default poll function. `devm_adis_setup_buffer_and_trigger_with_attrs()` wraps IIO triggered-buffer setup, optional ADIS trigger probing, and devm cleanup.

Control flow: each scan-mode update frees old transfer state, allocates new transfer and buffer memory, then either prepares a burst read or constructs one delayed 16-bit SPI transfer per enabled scan element plus a pipeline transfer. For non-burst 32-bit channels, it emits high-register then low-register reads. Trigger handling performs paging fixup if needed, runs `spi_sync()`, pushes the raw ADIS buffer with timestamp, and notifies trigger completion.

State and persistence: dynamically owns `adis->xfer`, `adis->buffer`, and `adis->msg` until the next scan-mode update or devm cleanup. It also mutates `adis->current_page` for paged devices. No persistent hardware settings are configured here except SPI read sequencing.

Dependencies and integration: used by ADIS IMU drivers through `linux/iio/imu/adis.h`; depends on SPI, IIO triggered buffer, trigger consumer, and `devm_adis_probe_trigger()` from `adis_trigger.c`.

Risks: allocation failures must leave `adis->xfer` and `adis->buffer` consistent. Active scan ordering and storage width determine wire command order; misdeclared channel metadata corrupts buffers. Burst callers that mutate `burst_extra_len` must keep transfer lengths synchronized. Paged devices must not capture from a nonzero page.

Test signals: exercise burst and non-burst scan-mode rebuilds, 16-bit and 32-bit channels, allocation-failure unwinds, repeated scan-mask changes, paged-device capture, default handler errors, and cleanup after managed device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_trigger.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_trigger.c

Purpose: shared trigger setup for ADIS16xxx IIO devices. It translates IIO trigger enable/disable calls into ADIS IRQ enable operations and validates/request IRQs for data-ready or FIFO-watermark lines.

Important APIs, types, and functions: `adis_data_rdy_trigger_set_state()` calls `adis_enable_irq()`. `adis_trigger_ops` exposes that callback to IIO. `adis_validate_irq_flag()` normalizes and validates IRQ trigger flags, including FIFO versus non-FIFO polarity requirements and `IRQF_NO_AUTOEN` for unmasked data-ready lines. `devm_adis_probe_trigger()` allocates, configures, requests, and registers the trigger.

Control flow: setup allocates a named trigger using the IIO device ID, stores `struct adis` as trigger private data, validates IRQ flags, requests either threaded IRQ for FIFO devices or normal IRQ for data-ready devices, then registers the trigger with devm cleanup. Runtime trigger state changes call back into the driver or generic ADIS IRQ enable path.

State and persistence: sets `adis->trig` and may mutate `adis->irq_flag` by adding default rising-edge behavior or `IRQF_NO_AUTOEN`. No hardware state persists here except what `adis_enable_irq()` toggles through the underlying ADIS ops.

Dependencies and integration: consumed by `adis_buffer.c` and ADIS drivers; depends on SPI IRQ presence, IIO trigger core, `iio_trigger_generic_data_rdy_poll`, and ADIS metadata flags `unmasked_drdy` and `has_fifo`.

Risks: wrong IRQ polarity is rejected differently for FIFO level-triggered devices versus edge-triggered non-FIFO devices. Missing IRQ defaults to no trigger setup at the caller layer. Unmasked DRDY lines require `IRQF_NO_AUTOEN` to prevent interrupts before the buffer path is ready.

Test signals: validate default IRQ flags, invalid edge/level combinations, FIFO threaded request path, non-FIFO request path, trigger enable/disable calling `adis_enable_irq()`, and probe behavior when IRQ request or trigger registration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis_trigger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Kconfig -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Kconfig

Purpose: Kconfig declarations for the Bosch BMI160/BMI120 IIO IMU driver family. It defines a hidden common core symbol and user-visible I2C/SPI transport symbols.

Important APIs, types, and functions: `config BMI160` is tristate and selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`. `config BMI160_I2C` depends on `I2C`, selects `BMI160` and `REGMAP_I2C`, and builds module `bmi160_i2c`. `config BMI160_SPI` depends on `SPI`, selects `BMI160` and `REGMAP_SPI`, and builds module `bmi160_spi`.

Control flow: selecting either bus driver automatically pulls in the common core and the correct regmap backend. The core itself has no prompt, so users normally enable transport-specific drivers.

State and persistence: no runtime state; build-time configuration only.

Dependencies and integration: integrates the BMI160 driver with IIO buffer infrastructure, triggered buffers, I2C/SPI subsystems, and regmap bus helpers.

Risks: help text mentions an external BMG160 magnetometer even though `bmi160_core.c` still marks magnetometer/FIFO support as TODO; this can overstate runtime capability. Enabling only `BMI160` directly is possible through dependency selection but provides no bus probe entry on its own.

Test signals: check allmodconfig/module builds, dependency resolution for I2C and SPI, and module names matching Makefile outputs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Makefile -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Makefile

Purpose: Kbuild mapping for BMI160 common core and bus transport modules.

Important APIs, types, and functions: `obj-$(CONFIG_BMI160) += bmi160_core.o`, `obj-$(CONFIG_BMI160_I2C) += bmi160_i2c.o`, and `obj-$(CONFIG_BMI160_SPI) += bmi160_spi.o`.

Control flow: when Kconfig selects a symbol, Kbuild compiles the corresponding object into the kernel or module. The transport modules import the `IIO_BMI160` namespace from the core.

State and persistence: build artifact selection only; no runtime state.

Dependencies and integration: must stay aligned with `Kconfig` and exported symbols in `bmi160_core.c`/`bmi160.h`.

Risks: stale object names would break module builds or namespace imports. Core can be built without transport if selected manually, which is harmless but non-probing.

Test signals: build each config permutation: core-only, I2C module, SPI module, and both buses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160.h -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160.h

Purpose: private shared header for BMI160 core and bus glue.

Important APIs, types, and functions: `struct bmi160_data` stores the regmap, trigger, two regulators (`vdd`, `vddio`), mount matrix, and aligned scan buffer. The header declares `bmi160_regmap_config`, `bmi160_core_probe()`, `bmi160_enable_irq()`, `bmi160_probe_trigger()`, and `bmi160_core_pm_ops`.

Control flow: I2C/SPI modules create a regmap, then call `bmi160_core_probe()`. Core exposes IRQ enable and trigger probe for internal trigger setup, while PM ops are shared by bus drivers.

State and persistence: defines host-side device state, including regulator handles and mount matrix read from firmware. The buffer is aligned to keep timestamps naturally aligned.

Dependencies and integration: includes IIO and regulator consumer APIs; expected to be included only by BMI160 implementation files.

Risks: buffer sizing assumes six 16-bit channels plus timestamp padding. Any future FIFO or magnetometer expansion must revisit this layout.

Test signals: compile both bus drivers, verify namespace exports, and run buffered captures with timestamp alignment checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_core.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_core.c

Purpose: common IIO core for Bosch BMI160/BMI120 over regmap. It provides accelerometer and gyroscope raw channels, scale and sample-frequency controls, triggered buffer capture, IRQ trigger setup, regulators, mount matrix, and runtime PM.

Important APIs, types, and functions: exports `bmi160_regmap_config`, `bmi160_core_probe()`, `bmi160_enable_irq()`, `bmi160_probe_trigger()`, and `bmi160_core_pm_ops`. Internal tables map sensor type to data/config/range/PMU registers, scale values, and ODR values. `bmi160_set_mode()`, `bmi160_set_scale()`, `bmi160_get_scale()`, `bmi160_set_odr()`, `bmi160_get_odr()`, and `bmi160_get_data()` back IIO raw access. `bmi160_trigger_handler()` reads active channels into the aligned buffer.

Control flow: core probe allocates IIO state, gets regulators, reads orientation, initializes the chip, registers cleanup, configures channel metadata and buffer setup, optionally discovers INT1/INT2 and configures trigger IRQ, then registers the IIO device. Chip init enables regulators, soft-resets, performs an SPI dummy read when needed, validates chip ID, and powers accel/gyro into normal mode. Cleanup suspends gyro/accel and disables regulators.

State and persistence: device registers persist PMU modes, ranges, ODRs, and interrupt routing. Host state tracks regmap, trigger, supplies, orientation, and scan buffer. Runtime PM suspends/resumes IIO triggering, not the chip PMU directly.

Dependencies and integration: relies on regmap, regulator bulk APIs, firmware IRQ names `INT1`/`INT2`, optional `drive-open-drain`, IIO mount matrix, IIO triggered buffers, and bus wrappers.

Risks: no hardware FIFO despite TODO; buffered reads loop individual active channels from the raw data window. IRQ configuration needs correct firmware trigger type and pin name. Chip ID mismatch is warned but not fatal after `bmi160_check_chip_id()` returns a failure, so compatible-but-unexpected silicon behavior should be reviewed. SPI mode requires dummy read after reset.

Test signals: regulator failure paths, chip ID reads for BMI120/BMI160, SPI dummy read, scale/ODR sysfs round trips, direct raw reads, buffered capture for all channels, INT1/INT2 IRQ polarity/open-drain combinations, trigger enable/disable, mount matrix, and runtime PM trigger suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_i2c.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_i2c.c

Purpose: I2C transport wrapper for the BMI160/BMI120 core driver.

Important APIs, types, and functions: `bmi160_i2c_probe()` initializes an I2C regmap with `bmi160_regmap_config`, chooses a device name from I2C ID or `dev_name()`, and calls `bmi160_core_probe(..., use_spi=false)`. Device tables include I2C IDs, ACPI IDs, and OF compatibles.

Control flow: the I2C subsystem matches the device, probe creates managed regmap state, then delegates all hardware initialization and IIO registration to the common core.

State and persistence: no transport-private state beyond managed regmap allocation. Runtime state lives in `struct bmi160_data` in the core.

Dependencies and integration: depends on I2C, regmap I2C, PM ops from the core, ACPI IDs including a documented firmware workaround for `10EC5280`, and OF compatibles `bosch,bmi120`/`bosch,bmi160`.

Risks: ACPI workaround intentionally binds incorrect firmware IDs to BMI160; platform validation is important to avoid stealing devices from a more specific driver. Regmap init failure prevents probe.

Test signals: probe through I2C, ACPI, and OF match paths; verify `use_spi=false` avoids dummy SPI read; test PM callbacks and namespace import.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_spi.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_spi.c

Purpose: SPI transport wrapper for the BMI160/BMI120 core driver.

Important APIs, types, and functions: `bmi160_spi_probe()` initializes SPI regmap with `bmi160_regmap_config`, chooses a name from SPI ID or device name, and calls `bmi160_core_probe(..., use_spi=true)`. It declares SPI IDs, ACPI IDs, OF compatibles, and a `spi_driver` with core PM ops.

Control flow: SPI match triggers probe, regmap is created, then core handles reset, the SPI-specific dummy read, chip init, buffers, triggers, and registration.

State and persistence: no transport-private persistent state; `use_spi=true` affects core initialization by causing a post-reset dummy read.

Dependencies and integration: depends on SPI, regmap SPI, BMI160 core namespace, ACPI IDs `BMI0120`/`BMI0160`, and OF compatibles.

Risks: the `MODULE_AUTHOR` string is missing a closing `>` in the source, cosmetic but visible in module metadata. SPI read semantics rely on generic regmap SPI being adequate for this device after the dummy read.

Test signals: SPI probe, regmap failure handling, dummy-read path, OF/ACPI/SPI ID matching, PM callbacks, and module metadata sanity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi160/bmi160_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Kconfig -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Kconfig

Purpose: Kconfig declarations for Bosch BMI260/BMI270 IIO IMU support.

Important APIs, types, and functions: hidden `config BMI270` selects `IIO_BUFFER` and `IIO_TRIGGERED_BUFFER`; `BMI270_I2C` depends on I2C and selects `REGMAP_I2C`; `BMI270_SPI` depends on SPI and selects `REGMAP_SPI`.

Control flow: enabling a bus transport selects the common core and required IIO/regmap infrastructure. Module names are `bmi270_i2c` and `bmi270_spi`.

State and persistence: build-time only.

Dependencies and integration: aligns with Makefile and the core/bus split; does not explicitly select firmware loading because `request_firmware()` support is kernel-wide.

Risks: users must install `bmi260-init-data.fw` or `bmi270-init-data.fw` at runtime even though Kconfig help does not mention firmware dependency.

Test signals: build I2C and SPI permutations and verify runtime firmware packaging in distro/module tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Makefile -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Makefile

Purpose: Kbuild object mapping for BMI270 common core plus I2C/SPI transport wrappers.

Important APIs, types, and functions: builds `bmi270_core.o` for `CONFIG_BMI270`, `bmi270_i2c.o` for `CONFIG_BMI270_I2C`, and `bmi270_spi.o` for `CONFIG_BMI270_SPI`.

Control flow: Kconfig-selected symbols determine whether objects are built in or as modules.

State and persistence: build artifact selection only.

Dependencies and integration: must match Kconfig symbols and namespace exports/imports under `IIO_BMI270`.

Risks: stale object mapping would break transport probes or leave exported chip-info symbols unresolved.

Test signals: compile core, each transport, and both transports as modules and built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270.h -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270.h

Purpose: private shared header for BMI260/BMI270 common core and bus wrappers.

Important APIs, types, and functions: `struct bmi270_chip_info` contains name, chip ID, and firmware filename. The header declares exported `bmi260_chip_info`, `bmi270_chip_info`, `bmi270_core_probe()`, and `bmi270_core_pm_ops`. It also declares `bmi270_regmap_config`, though the current bus files use local regmap configs instead.

Control flow: bus probes select a `chip_info` via match data, build a regmap, and call `bmi270_core_probe()`.

State and persistence: no state storage except chip descriptors referenced by bus drivers.

Dependencies and integration: includes regmap and IIO headers and exports symbols in the `IIO_BMI270` namespace.

Risks: `extern const struct regmap_config bmi270_regmap_config` is declared but not defined in the inspected files, so references to it would fail; current code avoids it. Firmware filename is part of chip identity and must remain accurate.

Test signals: compile both bus modules, verify exported chip descriptors resolve, and ensure no user references the undeclared regmap config symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_core.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_core.c

Purpose: common IIO core for Bosch BMI260/BMI270 six-axis IMUs. It supports accel, gyro, temperature, step counter, motion/no-motion events, triggered buffered accel/gyro capture, firmware/init-data loading, IRQ routing, and runtime PM.

Important APIs, types, and functions: exports `bmi260_chip_info`, `bmi270_chip_info`, `bmi270_core_probe()`, and `bmi270_core_pm_ops`. `struct bmi270_data` stores device/regmap/chip info, IRQ pin, trigger, mutex, step-enable state, DMA-safe scan buffer, and feature-register scratch. Feature access is through `bmi270_{read,write,update}_feature_reg()`. Raw IIO paths use `bmi270_{get,set}_scale()`, `bmi270_{get,set}_odr()`, `bmi270_get_data()`, and `bmi270_read_steps()`. Event paths use `bmi270_anymotion_event_en()`, `bmi270_nomotion_event_en()`, `bmi270_step_wtrmrk_en()`, and event value/config callbacks.

Control flow: core probe initializes mutex/state, validates chip ID, uploads firmware/init data, configures power and default ODR/BWP, sets IIO channels and available scan masks, probes optional INT1/INT2 trigger, installs triggered buffer, and registers IIO. IRQ thread reads status registers, polls the data-ready trigger for accel/gyro, and pushes IIO events for motion, no-motion, and step watermark. Buffer handler bulk-reads six accel/gyro words from `BMI270_ACCEL_X_REG`.

State and persistence: device state includes firmware-loaded feature engine, power control, ODR/range, interrupt mapping, feature pages, motion thresholds/durations, step counter enable/watermark/reset, and interrupt latch/polarity. Host state `steps_enabled` gates step watermark use and direct read/write paths use `iio_device_claim_direct()` to avoid buffered races.

Dependencies and integration: depends on regmap, request_firmware for `bmi260-init-data.fw`/`bmi270-init-data.fw`, IIO events, triggered buffers, firmware IRQ names `INT1`/`INT2`, `drive-open-drain`, and bus wrappers.

Risks: firmware file absence fails probe. Feature-register page switching and shared scratch require mutex coverage. `bmi270_enable_steps()` sets `steps_enabled = true` even when asked to write zero, so disable semantics are limited. `bmi270_validate_chip_id()` refuses BMI160 but may update chip info when actual ID differs from match data. Motion threshold scaling depends on current accel scale.

Test signals: firmware load success/failure, BMI160 rejection, BMI260/BMI270 chip switching, raw reads with direct-mode locking, scale/ODR available lists, buffered all-channel scan, INT1/INT2 edge/level/open-drain configuration, data-ready trigger polling, motion/no-motion event enable and values, step enable/read/reset/watermark, and runtime PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_i2c.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_i2c.c

Purpose: I2C transport wrapper for BMI260/BMI270 core.

Important APIs, types, and functions: local `bmi270_i2c_regmap_config` uses 8-bit register and value fields. `bmi270_i2c_probe()` obtains chip info from I2C/ACPI/OF match data, initializes an I2C regmap, and calls `bmi270_core_probe()`. Device tables provide I2C IDs, ACPI workarounds, and OF compatibles.

Control flow: matched I2C device supplies `chip_info`; probe fails with `-ENODEV` if match data is missing, then delegates to core for firmware load and IIO setup.

State and persistence: no transport-private runtime state beyond managed regmap.

Dependencies and integration: depends on I2C, regmap I2C, BMI270 core PM ops, ACPI IDs `BMI0160`/`BMI0260`, and OF compatibles `bosch,bmi260`/`bosch,bmi270`.

Risks: ACPI `BMI0160` is intentionally mapped to BMI260 for specific devices, while core rejects real BMI160 to avoid misbinding. Firmware files are still required after transport probe succeeds.

Test signals: I2C ID, OF, and ACPI match paths; missing match data; regmap init failure; BMI160 rejection in core; firmware load path; PM callback wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_spi.c -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_spi.c

Purpose: SPI transport wrapper for BMI260/BMI270 core, including custom regmap bus operations to handle the device's dummy byte on reads.

Important APIs, types, and functions: `bmi270_regmap_spi_read()` uses `spi_write_then_read()`. `bmi270_regmap_spi_write()` removes the pad byte used by regmap read framing before writing. `bmi270_regmap_bus` plugs these callbacks into `devm_regmap_init()`. `bmi270_spi_regmap_config` uses 8-bit regs/values, 8 pad bits, and read flag bit 7. `bmi270_spi_probe()` obtains chip info, creates regmap, and calls core.

Control flow: SPI match data selects BMI260/BMI270; custom regmap bus adapts transfer framing; core handles validation, firmware upload, IIO setup, and triggers.

State and persistence: no private state beyond managed regmap. The write callback mutates the regmap-provided transfer buffer to shift out the pad byte.

Dependencies and integration: depends on SPI, regmap, BMI270 core namespace/PM ops, and OF/SPI IDs. Unlike I2C, only OF and SPI IDs are declared in this file.

Risks: the write callback casts away const and modifies the data buffer, which is acceptable only if regmap passes mutable scratch. Dummy-byte handling must match BMI270 SPI timing; off-by-one framing would corrupt all register writes. `MODULE_DEVICE_TABLE` is absent for the SPI and OF tables in the inspected snippet, which may affect module autoload metadata.

Test signals: SPI read/write framing with dummy byte, regmap init failure, OF/SPI ID matching and autoload, firmware upload through SPI, and PM callback wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi270/bmi270_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Kconfig -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Kconfig

Purpose: Kconfig declarations for Bosch BMI323 IIO IMU support.

Important APIs, types, and functions: hidden `config BMI323` selects IIO buffer and triggered-buffer support. User-visible `BMI323_I2C` and `BMI323_SPI` depend on their bus subsystems, select the common core, and select the matching regmap backend.

Control flow: enabling a bus option builds/provides the core plus the relevant transport module. Module names are `bmi323_i2c` and `bmi323_spi`.

State and persistence: build-time only.

Dependencies and integration: aligns BMI323 with the same core/transport pattern as BMI160 and BMI270.

Risks: Kconfig does not describe optional FIFO/event behavior visible in `bmi323.h`; users only see generic six-axis support.

Test signals: Kconfig dependency checks and build permutations for I2C, SPI, and both.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Makefile -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Makefile

Purpose: Kbuild mapping for BMI323 common core and bus wrappers.

Important APIs, types, and functions: compiles `bmi323_core.o`, `bmi323_i2c.o`, and `bmi323_spi.o` according to `CONFIG_BMI323`, `CONFIG_BMI323_I2C`, and `CONFIG_BMI323_SPI`.

Control flow: selected Kconfig symbols determine built-in or module object inclusion.

State and persistence: build artifact selection only.

Dependencies and integration: must stay aligned with symbols exported by the BMI323 core and used by bus wrappers.

Risks: object naming drift breaks builds or module packaging.

Test signals: build core and each bus wrapper as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323.h -->
## Research: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323.h

Purpose: private shared header for the Bosch BMI323 IIO IMU driver. It defines register addresses, bit masks, conversion constants, FIFO limits, feature-engine constants, and core/bus interfaces.

Important APIs, types, and functions: key defines cover chip ID/status, accel/gyro/temp data registers, INT1/INT2 status and mapping bits, feature I/O registers, FIFO fill/data/config/control, interrupt pin control/latch registers, command/reset registers, extended feature registers for motion/no-motion, step counter, tap gestures, temperature conversion, FIFO frame sizing, and raw/micro conversion macros. It declares `bmi323_core_probe()`, `bmi323_regmap_config`, and `bmi323_core_pm_ops`.

Control flow: bus drivers use the exported regmap config and call `bmi323_core_probe()`. The core is expected to use the masks to configure sensors, feature engine, FIFO, interrupts, events, and buffered capture.

State and persistence: this header defines persistent register layout rather than storing state. Constants imply runtime state for feature engine enable, interrupt routing, FIFO watermark/full behavior, motion/tap thresholds and durations, step counter reset/watermark, and sensor ODR/range/mode.

Dependencies and integration: includes bit, regmap, and units helpers; pairs with Kconfig/Makefile for common core plus I2C/SPI wrappers. Dummy byte constants document different I2C/SPI read padding.

Risks: many masks are shared across feature data and interrupt mapping; wrong mask use could route events to the wrong pin or corrupt feature configuration. FIFO maximum is deliberately capped at 169 frames because the watermark fires one frame early; changing this risks FIFO overflow. Conversion macros use integer micro-unit math and need range validation in core code.

Test signals: chip ID validation, dummy byte handling by transports, accel/gyro/temp reads, FIFO watermark/full behavior at capped limits, interrupt mapping for data-ready/motion/no-motion/step/tap, feature-engine readiness timeout, temperature scale/offset, and conversion round trips for event thresholds/durations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/bmi323/bmi323.h -->
