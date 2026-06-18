# subset-b-003861 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/intel_idle.c -->
# sources/distributed-fs/ceph-client/drivers/idle/intel_idle.c

Purpose: native Intel `cpuidle` driver that replaces the generic ACPI processor idle path on Intel CPUs with MWAIT-based C-state entry. It builds a per-CPU-family idle-state table, optionally reconciles it with ACPI `_CST`, registers a `cpuidle_driver`, and programs CPU MSRs related to C-state demotion and C1E promotion.

Important APIs/types/functions: `struct idle_cpu` links x86 model IDs to C-state tables and policy flags. Entry callbacks are `intel_idle()`, `intel_idle_irq()`, `intel_idle_ibrs()`, `intel_idle_xstate()`, `intel_idle_s2idle()`, and `intel_idle_enter_dead()`. Initialization flows through `intel_idle_init()`, `intel_idle_cpuidle_driver_init()`, `intel_idle_init_cstates_icpu()`, `intel_idle_init_cstates_acpi()`, `intel_idle_cpu_online()`, and `intel_idle_cpu_init()`. Module parameters include `max_cstate`, `states_off`, `force_irq_on`, `ibrs_off`, ACPI switches, and `table`.

Control flow: `subsys_initcall_sync(intel_idle_init)` rejects disabled/unsupported cases, matches CPU tables through `intel_idle_ids` or MWAIT-only fallback, validates CPUID MWAIT capabilities, chooses native or ACPI state construction, allocates per-CPU devices, adjusts state latency/residency from the command line, registers the cpuidle driver, and installs a CPU hotplug online callback. State entry extracts the MWAIT hint from `state->flags`, optionally enables interrupts, disables/restores IBRS on SMT systems, or initializes FPU xstate before invoking MWAIT.

State and persistence: runtime state is held in the global `intel_idle_driver`, per-CPU `cpuidle_device` storage, `mwait_substates`, selected `icpu`, C-state tables copied into the driver, sysfs C1 demotion state, and MSR bits. Init-only tables disappear after boot, but chosen cpuidle states, module parameters, CPU hotplug registration, and MSR configuration persist. ACPI `_CST` is claimed through ACPI processor code when used.

Dependencies and integration: depends on x86 CPUID/MSR/MWAIT helpers, cpuidle core, CPU hotplug, tick broadcast, ACPI processor C-state support when enabled, scheduler SMT state, speculative-control helpers, FPU helpers, sysfs, and Intel family model identifiers. It integrates with `/sys/devices/system/cpu/cpuidle`, `/sys/module/intel_idle/parameters`, suspend-to-idle, CPU offline dead-state handling, and timer broadcast.

Risks: C-state tables encode hardware latency/residency policy and must match silicon behavior. Wrong MWAIT hints, off-by-default ACPI matching, or `CPUIDLE_FLAG_TIMER_STOP` decisions can break latency, timers, or power. MSR updates for auto-demotion/C1E are package-sensitive. `ibrs_off` and `force_irq_on` interact with mitigation and interrupt assumptions. Command-line table parsing mutates a copy but rejects non-monotonic values only after parsing.

Test signals: boot logs showing `intel_idle`, cpuidle sysfs state names/latencies, `powertop`/turbostat residency, CPU hotplug register/unregister behavior, suspend-to-idle wake behavior, non-ARAT timer broadcast coverage, ACPI `_CST` fallback on server parts, and targeted boots with `max_cstate`, `states_off`, `use_acpi`, `no_native`, and `table`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/idle/intel_idle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/Kconfig

Purpose: top-level Industrial I/O configuration menu. It exposes the `IIO` subsystem, optional core features such as buffers, triggers, configfs, software devices/triggers, triggered events, generic time-scale helper, backend framework, and then sources all IIO device-class submenus.

Important symbols: `IIO`, `IIO_BUFFER`, `IIO_CONFIGFS`, `IIO_GTS_HELPER`, `IIO_TRIGGER`, `IIO_CONSUMERS_PER_TRIGGER`, `IIO_SW_DEVICE`, `IIO_SW_TRIGGER`, `IIO_TRIGGERED_EVENT`, and `IIO_BACKEND`. It sources `drivers/iio/accel/Kconfig` plus ADC, DAC, IMU, gyro, light, pressure, trigger, and other sensor/actuator families.

Control flow: when `IIO` is disabled, all nested menus are hidden. Enabling `IIO_BUFFER` exposes buffer implementations. Enabling `IIO_TRIGGER` exposes trigger support and the trigger submenu. Driver Kconfigs under each source file select or depend on these core options, so this file is the root of the build-time dependency graph for IIO.

State and persistence: no runtime state. It persists only through generated kernel configuration and controls which objects are built into the kernel or modules.

Dependencies and integration: selects `DMA_SHARED_BUFFER` for buffer support and `CONFIGFS_FS` for configfs-backed software devices/triggers. It integrates the IIO core with Kbuild via `drivers/iio/Makefile` and with all child sensor driver menus.

Risks: hidden helper symbols must remain selected by their consumers; otherwise drivers may compile without required core support. Menu ordering and source paths are part of discoverability. Incorrect dependencies can expose impossible configurations or hide valid drivers.

Test signals: `make olddefconfig`, `make menuconfig`, allmodconfig/allnoconfig coverage, and representative module builds for buffered, triggered, configfs, and backend users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/Makefile

Purpose: Kbuild entry point for the Industrial I/O subsystem. It builds the core `industrialio` object and descends into every IIO device-class subdirectory.

Important entries: `obj-$(CONFIG_IIO) += industrialio.o`; `industrialio-y` contains `industrialio-core.o`, `industrialio-event.o`, and `inkern.o`; conditional components include `industrialio-buffer.o`, `industrialio-trigger.o`, and `industrialio-acpi.o`. Other feature modules include configfs, GTS helper, software device/trigger, triggered events, and backend objects.

Control flow: Kconfig symbols decide which object files participate in the build. `obj-y += accel/` and the other class directories force Kbuild to visit subdirectories so their own `obj-$(CONFIG_...)` entries can be evaluated.

State and persistence: no runtime state. The file persists build composition only.

Dependencies and integration: pairs with `drivers/iio/Kconfig` and the Linux Kbuild system. It integrates the core IIO object with optional buffer, trigger, ACPI, configfs, and backend implementation files and the full set of IIO driver families.

Risks: missing conditional object entries can produce unresolved symbols for selected Kconfig features. Removing a subdirectory from `obj-y` silently prevents all drivers below it from building even when symbols are enabled.

Test signals: compile with `CONFIG_IIO=y/m`, `CONFIG_IIO_BUFFER`, `CONFIG_IIO_TRIGGER`, `CONFIG_ACPI`, and allmodconfig; check that modules and built-in objects include the expected `industrialio-*` components.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/Kconfig

Purpose: accelerometer driver menu for IIO. It declares build symbols for many accelerometer families and their bus-specific frontends, with hidden core symbols for shared logic.

Important symbols: this subset centers on `ADIS16201`, `ADIS16209`, `ADXL313`, `ADXL313_I2C`, `ADXL313_SPI`, `ADXL345`, `ADXL345_I2C`, `ADXL345_SPI`, `ADXL355`, `ADXL355_I2C`, and `ADXL355_SPI`. The file also defines Bosch, NXP/Freescale, Kionix, ST, HID sensor, ChromeOS EC, Memsic, Murata, and other accelerometer options. Many bus frontends select `REGMAP_I2C` or `REGMAP_SPI`; buffered drivers select `IIO_BUFFER`, `IIO_TRIGGERED_BUFFER`, or `IIO_KFIFO_BUF`.

Control flow: visible bus-specific options select hidden shared core symbols such as `ADXL313`, `ADXL345`, `ADXL355`, `BMA220`, `BMA400`, or `MMA7455`. Dependencies prevent conflicting or impossible configurations, for example ADXL345 excludes `INPUT_ADXL34X` because compatible IDs are shared.

State and persistence: no runtime state. It controls generated `.config` values and module/built-in selection.

Dependencies and integration: consumed by `drivers/iio/accel/Makefile`. It integrates accelerometer drivers with SPI, I2C, ACPI/HID, regmap, IIO buffers, triggered buffers, and vendor common cores.

Risks: hidden core symbols must be selected by every frontend. Optional I2C/SPI selection patterns can accidentally build unwanted transports if dependencies are too broad. Shared-compatible exclusions must remain accurate to avoid driver binding conflicts.

Test signals: `olddefconfig`, `allyesconfig`, `allmodconfig`, single-symbol builds for each bus frontend, and binding/probe tests that verify only one compatible driver claims ADXL345-class devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/Makefile

Purpose: Kbuild object list for IIO accelerometer drivers.

Important entries: this subset maps `CONFIG_ADIS16201` to `adis16201.o`, `CONFIG_ADIS16209` to `adis16209.o`, `CONFIG_ADXL313` to `adxl313_core.o`, `CONFIG_ADXL313_I2C/SPI` to bus glue objects, `CONFIG_ADXL345` to `adxl345_core.o`, `CONFIG_ADXL345_I2C/SPI`, `CONFIG_ADXL355` to `adxl355_core.o`, and `CONFIG_ADXL355_I2C/SPI`. It also lists the remaining accelerometer drivers alphabetically and composes `st_accel-y` from ST core/buffer pieces.

Control flow: Kconfig symbols directly control object inclusion. Shared core objects are built when hidden core symbols are selected by a frontend.

State and persistence: no runtime state; the file is build metadata.

Dependencies and integration: pairs with `drivers/iio/accel/Kconfig`, Linux Kbuild, regmap-based frontend/core splits, and IIO sensor modules.

Risks: Makefile/Kconfig drift can produce selected symbols with no object, or objects with no reachable symbol. Alphabetical ordering is the local maintenance convention and helps avoid duplicate entries.

Test signals: module builds for each accelerometer symbol, link checks for namespace imports/exports, and allmodconfig coverage of core plus transport object combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adis16201.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adis16201.c

Purpose: SPI IIO driver for the Analog Devices ADIS16201 dual-axis inclinometer and accelerometer. It exposes supply, temperature, acceleration, auxiliary ADC, and inclination channels with calibration bias support.

Important APIs/types/functions: register definitions cover output, calibration, alarm, control, diagnostics, and command registers. `adis16201_read_raw()` handles raw conversions, scales, temperature offset, and calibration bias. `adis16201_write_raw()` writes accelerometer/inclinometer calibration bias. `adis16201_channels`, `adis16201_info`, `adis16201_data`, and `adis16201_probe()` define the IIO/ADIS contract.

Control flow: SPI probe allocates an IIO device, sets channels and direct mode, initializes the ADIS library with register metadata and timeout/status masks, sets up ADIS buffer/trigger support, runs `__adis_initial_startup()`, and registers the IIO device. Raw reads call `adis_single_conversion()` with `ADIS16201_ERROR_ACTIVE`; calibration reads/writes access the per-channel offset registers.

State and persistence: persistent state is the ADIS library private state in `struct adis`, device register configuration, calibration registers, and IIO registration. The driver itself stores no custom per-device state beyond `struct adis`.

Dependencies and integration: depends on SPI, IIO core, and `linux/iio/imu/adis.h`; imports namespace `IIO_ADISLIB`. The ADIS helper owns reset/self-test/status processing and triggered buffer setup.

Risks: scale and offset constants encode datasheet conversions. Calibration writes mask values to 12-bit accelerometer or 9-bit inclinometer width without range errors. Startup and self-test timing rely on 220 ms delays.

Test signals: SPI probe, `in_*_raw`, `in_*_scale`, `in_temp_offset`, calibration bias read/write, buffered capture via ADIS trigger, and diagnostic status messages for SPI/flash/power failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adis16201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adis16209.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adis16209.c

Purpose: SPI IIO driver for the Analog Devices ADIS16209 dual-axis digital inclinometer and accelerometer. It exposes supply, temperature, acceleration, auxiliary ADC, inclination, and rotation channels.

Important APIs/types/functions: register constants cover data outputs, null calibration, alarm, sample/filter, MSC control, status, and command registers. `adis16209_read_raw()` implements raw conversion, scale, temperature offset, and accelerometer calibration bias. `adis16209_write_raw()` writes accelerometer/inclinometer calibration registers. `adis16209_channels`, `adis16209_info`, `adis16209_data`, and `adis16209_probe()` wire the device to IIO and ADISLIB.

Control flow: probe allocates IIO storage for `struct adis`, sets channel table and direct mode, initializes the ADIS library, attaches ADIS buffer/trigger support, performs initial startup, then registers the IIO device. Raw reads are delegated to `adis_single_conversion()` and validated with `ADIS16209_ERROR_ACTIVE`.

State and persistence: state lives in the ADIS helper, device registers, and IIO registration. Calibration/null registers persist in hardware until changed or reset.

Dependencies and integration: depends on SPI, IIO core, and ADIS helper APIs; imports `IIO_ADISLIB`. The driver relies on ADIS helper scan-mode, buffer, reset, self-test, and diagnostic machinery.

Risks: `adis16209_addresses` leaves non-calibrated channels at address zero, so read/write paths must reject unsupported channel types first. Only accelerometer calibration bias is readable despite write accepting inclinometer. Unit conversions for inclination/rotation and temperature are fixed constants.

Test signals: probe/startup, raw channel reads, scale/offset sysfs values, accelerometer calibration bias, ADIS triggered buffer capture, and status handling for self-test, SPI, flash, and power faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adis16209.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313.h

Purpose: shared declarations for the ADXL312/ADXL313/ADXL314 IIO accelerometer core and its I2C/SPI frontends.

Important APIs/types: register macros define ID, soft reset, offsets, activity/inactivity thresholds, bandwidth, power, interrupt, data format, data axes, and FIFO registers. `enum adxl313_device_type`, `struct adxl313_data`, and `struct adxl313_chip_info` describe chip variants and runtime state. Exports include regmap access tables, `adxl313_is_volatile_reg()`, `adxl31x_chip_info[]`, and `adxl313_core_probe()`.

Control flow: bus drivers choose a chip info entry, create a regmap using exported access tables and volatile callback, then call `adxl313_core_probe()` with optional bus setup.

State and persistence: `struct adxl313_data` keeps the regmap, chip information, mutex-protected transfer buffer, watermark, and FIFO buffer. Hardware persists offsets, threshold/event configuration, ODR, power mode, interrupt mapping, and FIFO mode.

Dependencies and integration: depends on IIO type declarations and regmap users in the C files. It is the ABI between `adxl313_core.c`, `adxl313_i2c.c`, and `adxl313_spi.c`.

Risks: register definitions are shared by three variants with different ID/reset/range behavior, so chip info and access tables must remain synchronized. Buffer alignment matters for DMA-safe IIO transfers.

Test signals: compile/link namespace exports, I2C and SPI probe for all three variants, debugfs register access, raw reads, calibration bias, event configuration, and FIFO capture when interrupts exist.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_core.c

Purpose: shared IIO core for ADXL312/ADXL313/ADXL314 3-axis accelerometers. It implements register access policies, chip identity checks, raw acceleration, calibration bias, sampling frequency, activity/inactivity events, hardware FIFO buffering, interrupt handling, and common probe/setup.

Important APIs/types/functions: exported items are regmap access tables, `adxl313_is_volatile_reg()`, `adxl31x_chip_info[]`, and `adxl313_core_probe()`. Key internal functions include `adxl313_setup()`, `adxl313_read_raw()`, `adxl313_write_raw()`, event config/value helpers, `adxl313_set_watermark()`, FIFO setup/push/reset helpers, and `adxl313_irq_handler()`.

Control flow: core probe allocates an IIO device, initializes `adxl313_data`, sets channel/scan masks, performs optional soft reset and bus setup, checks IDs, configures full-resolution max range for variable-range chips, enables measurement, then either configures FIFO bypass when no `INT1`/`INT2` firmware IRQ exists or maps interrupts, seeds safe event defaults, sets up a kfifo buffer, and requests a threaded IRQ. IRQ handling reads `INT_SOURCE`, pushes activity/inactivity events, drains FIFO on watermark, and resets FIFO on unhandled/error conditions.

State and persistence: runtime state includes regmap cache, mutex, chip info, watermark, transfer buffer, and FIFO buffer. Device state persists in power control, data format, bandwidth, threshold, inactivity time, activity/inactivity control, interrupt map/enable, and FIFO registers.

Dependencies and integration: depends on regmap, firmware IRQ properties, IIO core/events/kfifo buffers, Linux bitfield helpers, and bus frontends. It exports namespace `IIO_ADXL313`.

Risks: event enable silently no-ops when thresholds or inactivity time are zero. Measurement is toggled around configuration; failure paths can leave measurement disabled in some intermediate register-write failures. `adxl313_set_watermark()` updates mode bits with the raw value before full FIFO stream setup, so FIFO register bit semantics must be preserved. Interrupt-less systems have no buffered capture path.

Test signals: ID warning paths, scale and ODR sysfs values, calibration bias bounds, activity/inactivity AC/DC events, watermark-triggered buffered reads, FIFO overrun recovery, and both INT1/INT2 firmware mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_i2c.c

Purpose: I2C transport driver for ADXL312/ADXL313/ADXL314. It creates variant-specific regmaps and delegates all IIO behavior to the ADXL313 core.

Important APIs/types/functions: `adxl31x_i2c_regmap_config[]` selects register access tables, volatile callback, max register, 8-bit register/value widths, and Maple regcache per chip type. Match tables are `adxl313_i2c_id` and `adxl313_of_match`. `adxl313_i2c_probe()` obtains `struct adxl313_chip_info`, initializes regmap, and calls `adxl313_core_probe()`.

Control flow: device matching provides chip info, probe creates an I2C regmap indexed by `chip_data->type`, reports regmap errors, then invokes the core with no extra setup callback.

State and persistence: the frontend has no private runtime state after probe. Regmap cache and hardware state are owned by the core and devm-managed resources.

Dependencies and integration: depends on I2C, OF matching, regmap I2C, and exported `IIO_ADXL313` symbols. Kconfig selects `ADXL313` and `REGMAP_I2C`.

Risks: `i2c_get_match_data()` must return non-NULL chip data; the code assumes it. Wrong match data type would index the regmap config array incorrectly.

Test signals: I2C and OF modalias binding for all three compatible strings, regmap initialization, core probe success, raw read over I2C, and module namespace import resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_spi.c

Purpose: SPI transport driver for ADXL312/ADXL313/ADXL314. It configures SPI mode/regmap access, handles 3-wire/I2C-disable setup, and delegates sensor behavior to the shared core.

Important APIs/types/functions: `adxl31x_spi_regmap_config[]` mirrors variant access tables and uses `read_flag_mask = BIT(7) | BIT(6)` for multi-byte reads. `adxl313_spi_setup()` writes 3-wire mode when requested and disables the I2C interface. `adxl313_spi_probe()` sets `SPI_MODE_3`, initializes regmap, and calls `adxl313_core_probe()`.

Control flow: probe forces mode 3 and calls `spi_setup()`, obtains match data, creates an SPI regmap, and passes `adxl313_spi_setup` to the core so bus-specific DATA_FORMAT/POWER_CTL bits are applied before common ID/range/measurement setup.

State and persistence: no frontend-private state persists. SPI mode, regmap cache, and bus-specific hardware bits persist through the device lifetime.

Dependencies and integration: depends on SPI, regmap SPI, device/OF match tables, and `IIO_ADXL313` exports. Kconfig selects `ADXL313` and `REGMAP_SPI`.

Risks: forcing `SPI_MODE_3` may conflict with board descriptions if they are wrong. `adxl313_spi_setup()` always disables I2C, which is required for SPI operation but must happen in the correct sequence. Multi-byte read flags are protocol-specific.

Test signals: SPI probe for ADXL312/313/314, 3-wire and 4-wire modes, regmap bulk reads of XYZ data, I2C-disable bit verification, and core event/FIFO behavior through SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl313_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345.h

Purpose: shared register and API header for ADXL345/ADXL375 IIO accelerometer core and I2C/SPI frontends.

Important APIs/types: register macros cover device ID, tap timing, activity/inactivity/free-fall thresholds, bandwidth, power, interrupt map/source, data format, axis data, and FIFO. Interrupt bit macros define overrun, watermark, free-fall, inactivity, activity, double tap, single tap, and data-ready. `struct adxl345_chip_info` carries name and scale. Exports are `adxl345_is_volatile_reg()` and `adxl345_core_probe()`.

Control flow: bus frontends create regmap instances and call `adxl345_core_probe()` with optional SPI setup and FIFO delay information.

State and persistence: header-defined hardware registers persist offsets, event thresholds, tap timing, bandwidth/range, power mode, interrupt routing, and FIFO configuration. Runtime state is private to the core C file.

Dependencies and integration: consumed by `adxl345_core.c`, `adxl345_i2c.c`, and `adxl345_spi.c`. It intentionally avoids including transport-specific headers.

Risks: ADXL345 and ADXL375 share much of the register model but use different scale constants. Compatible sharing with the older input driver is handled in Kconfig and must remain aligned with match tables.

Test signals: compile/link coverage, raw/scale/sample-frequency sysfs, tap/free-fall/activity events, FIFO buffer capture, and I2C/SPI probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_core.c

Purpose: shared IIO core for ADXL345 and ADXL375 accelerometers. It implements direct acceleration reads, scale/range and ODR control, calibration bias, activity/inactivity/free-fall events, single/double-tap events, FIFO buffering, interrupt handling, and common probe.

Important APIs/types/functions: exported functions are `adxl345_is_volatile_reg()` and `adxl345_core_probe()`. Key internal helpers include `adxl345_set_measure_en()`, ODR/range find/set helpers, activity/inactivity and tap config/value helpers, `adxl345_set_watermark()`, `adxl345_set_fifo()`, FIFO transfer/reset/push helpers, and `adxl345_irq_handler()`.

Control flow: core probe allocates IIO state, gets chip info from match data, seeds default tap and inactivity values, sets ODR to 200 Hz, range to 16g, disables interrupts, applies optional bus setup, enables full-resolution mode, validates device ID, enables measurement, installs a powerdown action, and either configures IRQ/FIFO/event defaults or FIFO bypass when no `INT1`/`INT2` IRQ is described. IRQ handling derives tap/activity axis direction, reads interrupt source, pushes IIO events, drains FIFO on watermark, and resets FIFO on errors/overrun.

State and persistence: `struct adxl345_state` stores chip info, regmap, SPI FIFO delay flag, watermark/FIFO mode, cached inactivity/tap parameters, and DMA-aligned FIFO buffer. Hardware registers persist offsets, thresholds, tap timing, range, ODR, interrupt routing, FIFO, and power state. A devm action disables measurement on teardown.

Dependencies and integration: depends on regmap, firmware IRQ properties, IIO core/events/kfifo buffers, units/bitfield helpers, and bus frontends. It exports namespace `IIO_ADXL345`.

Risks: `adxl345_write_raw()` disables measurement before validating all inputs and returns early on some errors without re-enabling measurement. Event enablement silently ignores invalid zero thresholds/timing. Range changes rescale thresholds and clamp to 1..255, which may surprise users. SPI FIFO delay is required above 1.5 MHz to satisfy FIFO pop timing.

Test signals: device ID rejection, scale/range and ODR sysfs lists, calibration bias, tap/double-tap timing constraints, activity/inactivity/free-fall events, FIFO watermark capture, overrun reset, no-IRQ bypass mode, and SPI high-speed FIFO reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_i2c.c

Purpose: I2C frontend for ADXL345 and ADXL375 accelerometers.

Important APIs/types/functions: `adxl345_i2c_regmap_config` defines 8-bit register/value access, volatile callback, and Maple regcache. `adxl345_i2c_info` and `adxl375_i2c_info` provide names and scale constants. Match tables cover I2C IDs, OF compatibles, and ACPI ID `ADS0345`. `adxl345_i2c_probe()` initializes regmap and calls the core.

Control flow: probe creates a devm I2C regmap, returns a dev_err_probe message on failure, and invokes `adxl345_core_probe(&client->dev, regmap, false, NULL)`. The `false` FIFO-delay flag reflects I2C timing being slow enough for FIFO pop requirements.

State and persistence: no I2C-private state persists after probe. Regmap and all sensor state are devm/core-owned.

Dependencies and integration: depends on I2C, regmap I2C, OF/ACPI matching, and `IIO_ADXL345` core exports. Kconfig excludes the older input driver and selects `ADXL345` plus `REGMAP_I2C`.

Risks: core obtains chip info via `device_get_match_data()`, so all match paths must carry the correct data pointer. ACPI match only names ADXL345 scale.

Test signals: I2C/OF/ACPI binding, regmap creation, core device ID validation, raw data reads, no FIFO delay behavior, and ADXL345/ADXL375 scale selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_spi.c

Purpose: SPI frontend for ADXL345 and ADXL375 accelerometers.

Important APIs/types/functions: constants cap SPI at 5 MHz and mark FIFO delay as needed above 1.5 MHz. `adxl345_spi_regmap_config` uses 8-bit register/value access, multi-byte read flags, volatile callback, and Maple regcache. `adxl345_spi_setup()` enables 3-wire SPI mode in DATA_FORMAT. Probe validates speed, initializes regmap, computes `needs_delay`, and calls the core.

Control flow: if `spi->max_speed_hz` exceeds 5 MHz, probe fails. Otherwise it creates an SPI regmap and invokes `adxl345_core_probe()` with a FIFO delay flag based on clock speed and an optional setup callback only when `SPI_3WIRE` is set.

State and persistence: frontend state does not persist beyond SPI mode/regmap setup. The core stores the FIFO delay flag and sensor state.

Dependencies and integration: depends on SPI, regmap SPI, OF/ACPI/SPI ID matching, and `IIO_ADXL345` exports. It imports the core namespace.

Risks: FIFO correctness depends on the speed threshold and `udelay(3)` in the core. 3-wire mode requires a DATA_FORMAT write before normal operation. Board files with excessive `max_speed_hz` are rejected.

Test signals: SPI binding for ADXL345/ADXL375, speed-limit failure, 3-wire setup, high-speed FIFO watermark reads with delay, raw/scale/ODR sysfs, and interrupt events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl345_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355.h

Purpose: shared declarations for ADXL355/ADXL359 IIO accelerometer core and I2C/SPI frontends.

Important APIs/types: `enum adxl355_device_type`, `struct adxl355_fractional_type`, and `struct adxl355_chip_info` describe device variant, part ID, acceleration scale, and temperature offset. Exports are readable/writeable regmap access tables, `adxl35x_chip_info[]`, and `adxl355_core_probe()`.

Control flow: bus frontends select chip info from match data, initialize a protocol-specific regmap using the access tables, then call the core probe.

State and persistence: this header defines no runtime state, but its chip-info constants drive persistent IIO scale/offset behavior and part-ID validation.

Dependencies and integration: includes regmap declarations and is included by `adxl355_core.c`, `adxl355_i2c.c`, and `adxl355_spi.c`.

Risks: ADXL355 and ADXL359 differ in part ID, acceleration range/scale, and temperature offset; incorrect match data produces wrong units even if register access works.

Test signals: namespace export/import, chip-info selection for both variants, I2C/SPI probe, raw/scale/offset sysfs, and triggered buffer setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_core.c

Purpose: shared IIO core for ADXL355 and ADXL359 low-noise 3-axis accelerometers. It implements ID/reset validation, raw acceleration and temperature reads, scale/offset/calibration bias, ODR and high-pass filter control, data-ready trigger support, and triggered buffers.

Important APIs/types/functions: exported symbols are `adxl355_readable_regs_tbl`, `adxl355_writeable_regs_tbl`, `adxl35x_chip_info[]`, and `adxl355_core_probe()`. Key internals are `adxl355_setup()`, `adxl355_set_op_mode()`, `adxl355_set_odr()`, `adxl355_set_hpf_3db()`, `adxl355_set_calibbias()`, `adxl355_read_raw()`, `adxl355_write_raw()`, `adxl355_probe_trigger()`, and `adxl355_trigger_handler()`.

Control flow: probe allocates IIO state, initializes standby mode and chip info, assigns channels and scan masks, runs setup, creates a triggered buffer, optionally registers a `DRDY` trigger, and registers the IIO device. Setup validates ADI/MEMS IDs, warns on unexpected part ID, snapshots shadow registers, repeatedly performs software reset until shadow registers match, disables data-ready output initially, computes HPF frequency table from ODR, and enters measurement mode. ODR/HPF/calibration writes switch to standby, update registers, then restore measurement.

State and persistence: `struct adxl355_data` stores chip info, regmap, device, mutex-protected op mode, ODR, HPF selection, cached calibration bias, computed HPF table, data-ready trigger, and DMA-aligned buffers. Hardware persists filter, offset, power, interrupt, and reset state.

Dependencies and integration: depends on regmap, IIO core, triggered buffer/trigger APIs, firmware IRQ named `DRDY`, unaligned big-endian access helpers, and bus frontends. It exports namespace `IIO_ADXL355`.

Risks: setup compares undocumented shadow registers after reset and can fail after five mismatches. Part-ID mismatch only warns, so wrong compatible data may still register with wrong scale. ODR/HPF/calibbias paths try to restore measurement after failures but preserve error returns. Trigger handler uses a shared buffer protected by the op-mode mutex.

Test signals: ID/reset success and shadow mismatch failure, raw 20-bit acceleration and temperature reads, scale/offset values for ADXL355 versus ADXL359, ODR and HPF available lists, calibration bias writes, DRDY-triggered buffer capture with timestamp, and operation without a DRDY IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_i2c.c

Purpose: I2C frontend for ADXL355 and ADXL359 accelerometers.

Important APIs/types/functions: `adxl355_i2c_regmap_config` uses 8-bit register/value access, max register `0x2F`, and core-exported readable/writeable access tables. Match tables cover I2C IDs and OF compatibles for `adi,adxl355` and `adi,adxl359`. `adxl355_i2c_probe()` selects chip data, creates regmap, and calls the core.

Control flow: probe rejects missing match data, initializes devm I2C regmap, reports regmap errors, then delegates to `adxl355_core_probe()`.

State and persistence: no frontend-private state persists. Regmap and IIO resources are devm-managed by the core/frontend combination.

Dependencies and integration: depends on I2C, regmap I2C, OF matching, and `IIO_ADXL355` exports. Kconfig selects `ADXL355`, `REGMAP_I2C`, `IIO_BUFFER`, and `IIO_TRIGGERED_BUFFER`.

Risks: missing or wrong match data causes either `-ENODEV` or incorrect scale/part validation. Access tables must match the 8-bit I2C protocol.

Test signals: I2C/OF binding for both variants, regmap initialization, core reset/ID validation, raw and triggered-buffer reads, and module namespace import resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_spi.c

Purpose: SPI frontend for ADXL355 and ADXL359 accelerometers.

Important APIs/types/functions: `adxl355_spi_regmap_config` models the SPI protocol with 7 register bits, 1 pad bit, 8 value bits, read flag `BIT(0)`, max register `0x2F`, and core-exported access tables. Match tables cover SPI IDs and OF compatibles. `adxl355_spi_probe()` selects chip data, initializes SPI regmap, and calls the core.

Control flow: probe gets match data through `spi_get_device_match_data()`, rejects missing data, creates a devm SPI regmap, reports regmap errors, and delegates to `adxl355_core_probe()`.

State and persistence: no frontend-private state persists beyond regmap/probe resources. Sensor state and buffers are core-owned.

Dependencies and integration: depends on SPI, regmap SPI, OF/SPI ID matching, and `IIO_ADXL355` exports. It imports namespace `IIO_ADXL355`.

Risks: SPI register framing differs from I2C; wrong `reg_bits`, `pad_bits`, or read flag would corrupt every register access. Missing match data fails probe with `-EINVAL`.

Test signals: SPI binding for both variants, register read/write sanity, core setup and shadow-register reset, DRDY trigger operation, raw sysfs reads, and buffered capture.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl355_spi.c -->
