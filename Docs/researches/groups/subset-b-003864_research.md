# subset-b-003864 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-spi.c

Purpose: SPI transport wrapper for the Kionix KXSD9 accelerometer. It adapts a `spi_device` to the shared KXSD9 IIO core by building an 8-bit regmap and delegating all sensor behavior to `kxsd9_common_probe()` and `kxsd9_common_remove()`.

Important APIs/types/functions: `kxsd9_spi_probe()` sets `SPI_MODE_0`, initializes `devm_regmap_init_spi()` with 8-bit registers/values and max register `0x0e`, then passes the regmap and SPI id name to the common driver. `kxsd9_spi_remove()` calls the common remove helper. Device matching is through `kxsd9_spi_id`, `kxsd9_of_match`, and `module_spi_driver()`. The module imports namespace `IIO_KXSD9`.

Control flow: probe is transport-only: configure SPI mode, allocate regmap, return probe failure on regmap errors, then transfer lifecycle ownership to the common IIO code. Remove performs no transport cleanup beyond common core teardown because regmap and allocations are devm-managed.

State and persistence: no private transport state is stored here. Runtime state, scale cache, regulators, triggered buffers, and PM state live in `kxsd9.c` private data.

Dependencies and integration points: depends on Linux SPI, regmap-SPI, OF matching, and `kxsd9.h`. It integrates with the accelerometer core through exported common functions and PM ops.

Risks: `spi_get_device_id(spi)->name` assumes an SPI id is present; OF-only instantiation still normally receives modalias/id support, but this is a transport assumption. SPI mode is overwritten unconditionally before regmap initialization.

Test signals: module build with namespace import resolution, SPI probe against `kionix,kxsd9`, regmap read/write traces, direct raw IIO reads, buffer enable/disable, and suspend/resume through `kxsd9_dev_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.c

Purpose: shared IIO implementation for the Kionix KXSD9 3-axis accelerometer and auxiliary voltage channel. It exposes raw acceleration, offset, selectable scale, mount matrix, triggered buffer capture, regulators, and runtime PM for transport wrappers.

Important APIs/types/functions: `struct kxsd9_state` holds `device`, `regmap`, mount matrix, VDD/IOVDD regulators, and cached full-scale bits. `kxsd9_common_probe()` and `kxsd9_common_remove()` are exported in namespace `IIO_KXSD9`. Raw access flows through `kxsd9_read_raw()` and `kxsd9_write_raw()`. Buffering uses `kxsd9_trigger_handler()` with `kxsd9_buffer_setup_ops`. Runtime PM is exported as `kxsd9_dev_pm_ops`.

Control flow: common probe allocates an IIO device, reads mount matrix, obtains regulators, initializes default 2g scale, powers the chip, installs a triggered buffer, registers IIO, and enables autosuspend. Raw reads resume the device, read big-endian 16-bit registers, shift to 12 valid bits, and return IIO-formatted values. Scale writes validate against the four micro-scale entries, update `CTRL_C`, and cache the selected FS bits. Power-up enables regulators, sets enable in `CTRL_B`, writes low-pass/motion/full-scale bits in `CTRL_C`, then waits 20 ms.

State and persistence: scale selection is cached in `st->scale` so power-up can restore it after runtime suspend. Hardware state is otherwise reprogrammed on resume. The triggered buffer reads X/Y/Z/AUX into a timestamp-aligned stack struct.

Dependencies and integration points: uses IIO direct mode, triggered buffers, regmap, regulators, runtime PM, mount matrix helpers, and transport wrappers from SPI/I2C files.

Risks: `pm_runtime_get_sync()` return values are ignored in raw and buffer paths. `kxsd9_common_probe()` calls `kxsd9_power_up(st)` without checking its return, so regulator or register failures can be masked until later operations. Remove cleans buffer before unregistering the IIO device, which is unusual compared with many IIO drivers and is worth regression-testing.

Test signals: scale availability and writes, raw axis/AUX reads, offset `-2048`, buffer scan mask `0x0f`, runtime autosuspend/resume restoring scale, regulator failure injection, and mount-matrix sysfs output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.h

Purpose: small shared header for KXSD9 transport drivers. It declares the common probe/remove entry points and exported runtime PM operations implemented by `kxsd9.c`.

Important APIs/types/functions: `kxsd9_common_probe(struct device *dev, struct regmap *map, const char *name)`, `kxsd9_common_remove(struct device *dev)`, and `extern const struct dev_pm_ops kxsd9_dev_pm_ops`. `KXSD9_STATE_RX_SIZE` and `KXSD9_STATE_TX_SIZE` are defined but unused by the listed SPI/common files.

Control flow: SPI and I2C wrappers include this header, initialize a bus-specific regmap, and delegate common IIO registration and teardown to these declarations.

State and persistence: no state is defined here; private state is intentionally hidden inside `kxsd9.c`.

Dependencies and integration points: includes Linux `device` and `kernel` headers but relies on an external declaration of `struct regmap`; the included source files already include regmap before this header.

Risks: because `struct regmap` is not forward-declared in this header, standalone include hygiene depends on prior includes. The unused RX/TX size macros may be legacy residue and should not be treated as current transport contract without checking users.

Test signals: all KXSD9 transport modules compile with namespace imports and PM ops linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/kxsd9.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mc3230.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mc3230.c

Purpose: I2C IIO driver for mCube MC3230 and MC3510C 3-axis accelerometers. It exposes three 8-bit signed acceleration channels, fixed scale per chip variant, mount matrix metadata, and simple suspend/resume mode switching.

Important APIs/types/functions: `struct mc3230_chip_info` carries name, chip id, product code, and scale. `struct mc3230_data` stores chip info, I2C client, and orientation. `mc3230_set_opcon()` edits mode bits, `mc3230_read_raw()` returns raw signed byte or fixed scale, and `mc3230_probe()/remove()` own IIO registration. Matching data is provided by I2C and OF tables.

Control flow: probe obtains match data, reads chip and product IDs but only logs mismatches, allocates the IIO device, wakes the chip with `MC3230_MODE_OPCON_WAKE`, reads mount matrix, and registers IIO. Remove unregisters and puts the chip into standby. System sleep PM mirrors remove/probe power state transitions.

State and persistence: persistent software state is the chip descriptor and orientation. Hardware operating mode is set to wake during runtime and standby during remove/suspend. No runtime PM or buffered capture is implemented.

Dependencies and integration points: depends on I2C SMBus byte operations, IIO direct mode, sysfs scale reporting, OF matching, and mount matrix helpers.

Risks: chip/product ID mismatch does not fail probe, so incorrect compatible strings can still bind. `mc3230_set_opcon()` read-modify-write has no lock, but the driver has no concurrent writers beyond PM/remove/raw access. MC3510C scale is empirical and may need board validation.

Test signals: I2C probe on both compatibles, raw sign extension for all axes, fixed scale values, mount matrix sysfs, suspend-to-standby/resume-to-wake, and behavior when ID registers return unexpected values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mc3230.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455.h

Purpose: shared interface between MMA7455 bus wrappers and the MMA7455 core IIO implementation.

Important APIs/types/functions: declares exported `mma7455_core_regmap`, `mma7455_core_probe(struct device *, struct regmap *, const char *)`, and `mma7455_core_remove(struct device *)`.

Control flow: I2C and SPI wrapper probes initialize transport regmaps with `mma7455_core_regmap`, pick a device name, then call `mma7455_core_probe()`. Remove paths call `mma7455_core_remove()`.

State and persistence: the header exposes no state; all runtime fields live in `struct mma7455_data` inside `mma7455_core.c`.

Dependencies and integration points: relies on Linux device/regmap types being available from includers. The exported symbols are in namespace `IIO_MMA7455`.

Risks: as with several small kernel headers, include hygiene is minimal and depends on source files including regmap/device headers first. API sequencing is implicit: callers must pass a valid regmap configured for MMA7455 register semantics.

Test signals: transport modules compile and load with `MODULE_IMPORT_NS("IIO_MMA7455")`, and both I2C/SPI probes can call the common core successfully.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_core.c

Purpose: common IIO core for Freescale MMA7455L/MMA7456 3-axis accelerometers in 10-bit mode. It provides raw acceleration, fixed 10-bit scale, sample frequency selection, and triggered-buffer reads for I2C and SPI transports.

Important APIs/types/functions: `struct mma7455_data` stores regmap and timestamp-aligned scan buffer. `mma7455_core_regmap` defines 8-bit registers through `MMA7455_REG_TW`. `mma7455_core_probe()` validates WHOAMI, enters measurement mode, sets up triggered buffer, and registers IIO. `mma7455_core_remove()` unregisters and returns to standby. `mma7455_drdy()`, `mma7455_read_raw()`, `mma7455_write_raw()`, and `mma7455_trigger_handler()` implement data access.

Control flow: direct raw reads reject access while the buffer is enabled, poll DRDY up to three times with 20 ms sleeps, bulk-read little-endian 16-bit channel data, sign-extend 10 bits, and return an integer. Triggered reads follow the same DRDY gate then bulk-read X/Y/Z into the scan buffer and push a timestamp. Sample frequency is encoded by `CTL1_DFBW`: reported as 125 or 250 Hz.

State and persistence: no software cache for sample frequency or mode is kept; state is held in device registers and the scan buffer. Probe writes measurement mode, remove writes standby.

Dependencies and integration points: IIO direct/buffer APIs, regmap, trigger consumer support, and bus wrappers via namespace exports.

Risks: `regmap_write()` to measurement mode in probe is not checked, which can allow later registration after a failed mode transition. DRDY polling is short and may fail on slow hardware. Unsupported features include 8-bit mode, interrupts, calibration, and events.

Test signals: WHOAMI mismatch path, 125/250 Hz read-write behavior, raw read blocked during buffer mode, triggered buffer samples in X/Y/Z order, standby on remove, and I2C/SPI transport parity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_i2c.c

Purpose: I2C transport wrapper for the MMA7455/MMA7456 shared core.

Important APIs/types/functions: `mma7455_i2c_probe()` initializes `devm_regmap_init_i2c()` using `mma7455_core_regmap`, obtains the I2C device id name when available, and delegates to `mma7455_core_probe()`. `mma7455_i2c_remove()` delegates teardown. Match tables cover `"mma7455"`, `"mma7456"`, `fsl,mma7455`, and `fsl,mma7456`.

Control flow: there is no sensor-specific logic in this file beyond regmap creation and name selection. Probe returns regmap errors directly, then the common core handles WHOAMI, mode setup, IIO registration, and buffers.

State and persistence: transport state is devm-managed and no private data is stored in this file.

Dependencies and integration points: Linux I2C, regmap-I2C, module matching, and the `IIO_MMA7455` namespace exported by `mma7455_core.c`.

Risks: OF-only devices may pass `name = NULL`; the common core assigns that to `indio_dev->name`, so user-visible naming depends on device-id availability in non-I2C-id paths. Runtime PM is not provided by the core or wrapper.

Test signals: I2C probe/remove, OF and legacy ID matching, regmap transaction success, common WHOAMI validation, and IIO raw/buffer behavior through this bus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_spi.c

Purpose: SPI transport wrapper for MMA7455/MMA7456 accelerometers using the shared core.

Important APIs/types/functions: `mma7455_spi_probe()` obtains the SPI id, creates a SPI regmap from `mma7455_core_regmap`, and calls `mma7455_core_probe()` with `id->name`. `mma7455_spi_remove()` calls the common remove helper. Matching is via `mma7455_spi_ids` and `module_spi_driver()`.

Control flow: probe is a straight transport bridge: create regmap, propagate errors, delegate sensor initialization and IIO registration to `mma7455_core.c`. Remove delegates all device state teardown to the common core.

State and persistence: no private transport state exists; regmap is devm-managed and common state is attached to the SPI device through `dev_set_drvdata()` in the core.

Dependencies and integration points: Linux SPI, regmap-SPI, common MMA7455 symbols in namespace `IIO_MMA7455`.

Risks: unlike the KXSD9 SPI wrapper, it does not explicitly set `spi->mode`; correct mode must come from board/controller configuration. `spi_get_device_id(spi)` is assumed non-NULL for naming.

Test signals: SPI modalias binding for both ids, regmap read/write correctness for this chip's SPI protocol, common WHOAMI path, raw reads, sample-frequency writes, triggered buffer operation, and standby on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7455_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7660.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma7660.c

Purpose: I2C IIO driver for the Freescale MMA7660FC 3-axis accelerometer. It exposes three signed 6-bit acceleration channels, fixed scale, mount matrix, and simple active/standby power control.

Important APIs/types/functions: `struct mma7660_data` stores I2C client, mutex, current mode, and orientation. `mma7660_set_mode()` read-modify-writes the MODE register. `mma7660_read_accel()` retries when the alert bit marks an unstable sample. `mma7660_read_raw()` handles raw and scale. Probe/remove and sleep PM manage IIO registration and standby transitions.

Control flow: probe allocates state, initializes the mutex and standby state, reads mount matrix, publishes IIO channels, switches to active mode, and registers the device. Raw reads lock around a retry loop, reject alert-bit samples up to five attempts, sign-extend bit 5, and return fixed nanounit scale. Remove unregisters then attempts standby, warning if it fails.

State and persistence: `data->mode` caches active/standby state to avoid redundant writes. Orientation persists in private state. No runtime PM or buffers are implemented.

Dependencies and integration points: I2C SMBus, IIO direct mode/sysfs, OF and ACPI matching, and system sleep PM.

Risks: mode cache can become stale if external actors modify the MODE register. The retry loop condition performs up to six reads because it tests `retries-- > 0`. No chip-id validation exists, so binding depends entirely on firmware/device tables.

Test signals: raw reads during stable and alert-bit conditions, scale sysfs, mount matrix, ACPI/OF matching, active mode on probe/resume, standby on suspend/remove, and timeout when alert never clears.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma7660.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma8452.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma8452.c

Purpose: full I2C IIO driver for Freescale/NXP MMA8451/2/3, MMA8652/3, and FXLS8471 accelerometers. It supports variant-specific resolution and scale, calibration bias, sample frequency, high-pass filter, oversampling, runtime PM with regulators, triggered buffers, data-ready IRQs, and motion/freefall/transient events.

Important APIs/types/functions: `struct mma8452_data` caches client, lock, mount matrix, `ctrl_reg1`, `data_cfg`, chip info, sleep delay, regulators, and scan buffer. `struct mma_chip_info` defines variant channels/scales/events. Core paths include `mma8452_read()`, `mma8452_read_raw()`, `__mma8452_write_raw()`, `mma8452_change_config()`, event read/write/config helpers, `mma8452_interrupt()`, `mma8452_trigger_handler()`, trigger setup, reset, probe/remove, and runtime PM callbacks.

Control flow: probe powers VDD/VDDIO, validates WHO_AM_I against match data, resets the chip, initializes scale/event defaults, configures IRQ routing if present, activates default 50 Hz sampling, sets up triggered buffer and optional trigger, enables runtime PM, registers IIO, then disables freefall mode by default. Register configuration changes enter standby under `data->lock`, write the target register, and restore active mode. Raw reads claim direct mode, wait for DRDY, resume runtime PM, read big-endian X/Y/Z block data, and sign-extend according to variant resolution.

State and persistence: `ctrl_reg1` and `data_cfg` are software shadows used across config writes and resume. Regulators are disabled during runtime suspend. Event enablement is in hardware registers, while chip capabilities are static table data.

Dependencies and integration points: I2C SMBus/block reads, firmware IRQ lookup, regulators, runtime PM, IIO events/triggers/buffers/debugfs, mount matrix, OF and I2C ids.

Risks: event power-state calls can enable runtime PM on event enable but some error/disable paths return before balancing puts. Runtime resume computes `1000 / mma8452_samp_freq[ret][0]`, relying on all table integer parts being nonzero. `mma8452_set_freefall_mode()` calls `mma8452_freefall_mode_enabled()` twice and can see inconsistent hardware if registers change externally.

Test signals: per-variant WHO_AM_I and channel resolution, scale/frequency/filter/oversampling writes, direct-read exclusion during buffers, data-ready trigger polling, transient/freefall/motion event sysfs and IRQ delivery, runtime autosuspend regulator toggles, reset timeout path, and suspend/resume preserving software-shadowed settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma8452.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551.c

Purpose: IIO driver for the Freescale MMA9551L intelligent motion-sensing platform. It exposes raw accelerometer channels through the shared AFE helpers and processed inclination channels with tilt threshold events delivered through GPIO-backed IRQs.

Important APIs/types/functions: `struct mma9551_data` stores I2C client, mutex, per-axis event enables, and four GPIO IRQs. `mma9551_read_incli_chan()` reads tilt angle/quadrant status and converts it to degrees. `mma9551_config_incli_event()` maps tilt status bits to GPIO pins via `mma9551_gpio_config()`. `mma9551_event_handler()` acknowledges tilt status and pushes IIO ROC events. Probe initializes firmware, GPIO IRQs, runtime PM, and IIO channels.

Control flow: probe allocates IIO state, gets name from I2C id or ACPI, reads version, enables the device, initializes mutex and channels, requests four GPIO IRQs, enables autosuspend, and registers IIO. Raw accel reads and processed inclination reads lock around shared-core mailbox operations and runtime PM transitions. Event enable powers the device, maps the relevant tilt angle flag to a GPIO pin, and records software event state; disable unmaps and schedules power-down.

State and persistence: event enable state is cached in `event_enabled[]`; GPIO mapping and sleep/wake state persist in MMA9551 application configuration until changed. Runtime/system PM toggles device state through the shared Sleep/Wake app.

Dependencies and integration points: depends on `mma9551_core.h` mailbox helpers, GPIO descriptors, threaded IRQs, IIO events, ACPI naming, I2C, and runtime PM.

Risks: `mma9551_read_event_config()` indexes `event_enabled[chan->channel2 - 1]`, assuming only X/Y/Z inclination channels call it. GPIO probe requires all four GPIO resources even though only three tilt axes are used. Some power-state failures during cleanup are ignored.

Test signals: ACPI/I2C probe, firmware version read, raw accel scale/path, inclination degree conversion for all quadrants, event threshold writes, GPIO IRQ mapping/unmapping, event delivery and acknowledgement by status read, runtime autosuspend/resume, and system sleep PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.c

Purpose: shared mailbox-command library for MMA955x intelligent sensor drivers. It implements the MMA955x application protocol over I2C and exports helpers for config/status byte/word transfers, GPIO routing, version reads, sleep/wake power state, accelerometer channels, and application reset.

Important APIs/types/functions: packed `mma9551_mbox_request`, `mma9551_mbox_response`, and `mma9551_version_info` model the wire format. `mma9551_transfer()` is the core write-then-poll-read transaction engine. Exported helpers include `mma9551_read_config_*`, `mma9551_write_config_*`, `mma9551_read_status_*`, `mma9551_update_config_bits()`, `mma9551_gpio_config()`, `mma9551_read_version()`, `mma9551_set_device_state()`, `mma9551_set_power_state()`, `mma9551_sleep()`, `mma9551_read_accel_chan()`, `mma9551_read_accel_scale()`, and `mma9551_app_reset()`.

Control flow: a transfer validates 12-bit offset, builds a mailbox request, writes it with `i2c_transfer()`, polls up to five times with 50 us delay for COCO, validates app id, error code, and response length, then copies output bytes. Word helpers convert big-endian mailbox payloads. GPIO config writes app id/bit selection and polarity. Device power uses Sleep/Wake app config bits; runtime PM wrapper delegates to kernel PM.

State and persistence: this file keeps no private state. It modifies persistent device application configuration and relies on callers to hold their per-device mutex, as documented on each exported helper.

Dependencies and integration points: Linux I2C, runtime PM, endian helpers, IIO channel definitions, and `mma9551_core.h` app ids/macros. Used by both MMA9551 and MMA9553 frontend drivers.

Risks: locking is entirely external, so any new caller that omits serialization can interleave mailbox commands. `i2c_transfer()` returning 0 is not treated as a short transfer failure. Response length validation compares two response fields, not requested output length directly.

Test signals: mailbox timeout/error-code/app-id mismatch injection, byte/word endian correctness, max mailbox length validation, GPIO polarity mapping for pins 6-9, runtime PM balance, accelerometer axis reads, and pedometer app reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.h

Purpose: public contract for MMA955x shared core helpers and application identifiers.

Important APIs/types/functions: defines app ids for VERSION, GPIO, AFE, TILT, SLEEP_WAKE, PEDOMETER, RSC, and NONE; reset mask `MMA9551_RSC_PED`; autosuspend delay; `enum mma9551_gpio_pin`; and the `MMA9551_ACCEL_CHANNEL(axis)` channel macro. It declares all exported mailbox, GPIO, power, accelerometer, sleep, and reset helpers implemented in `mma9551_core.c`.

Control flow: MMA9551 and MMA9553 frontend drivers include this header, define their IIO channels with the accel macro, and call exported helpers while holding their device mutex.

State and persistence: no state is stored here, but constants encode persistent firmware application registers and GPIO pin numbering used by device configuration.

Dependencies and integration points: depends on I2C client and IIO channel types from includers. Exported functions live in namespace `IIO_MMA9551`.

Risks: the channel macro assumes `IIO_ACCEL`, modifiers, and `IIO_CHAN_INFO_*` symbols are already included. The API comments requiring external locking are in the C file rather than enforced by type or lockdep.

Test signals: build coverage of both frontends, namespace import resolution, and compile-time validity of app ids, GPIO enum, and accel-channel macro.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9551_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9553.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mma9553.c

Purpose: IIO driver for the MMA9553L pedometer platform. It exposes accelerometer, steps, distance, velocity, energy, and activity channels, plus step/activity events, on top of the MMA9551 shared mailbox protocol.

Important APIs/types/functions: `struct mma9553_conf_regs` mirrors pedometer config words. `struct mma9553_data` stores client, mutex, cached config, event table, GPIO bit routing, step-count enable/cache, activity cache, and IRQ timestamp. Key functions include `mma9553_set_config()`, `mma9553_conf_gpio()`, `mma9553_init()`, `mma9553_read_raw()`, `mma9553_write_raw()`, event config/value handlers, gender enum helpers, `mma9553_irq_handler()`, and `mma9553_event_handler()`.

Control flow: probe initializes events, reads version and pedometer config to identify the app, clears GPIO routing, resets the pedometer app, writes default sleep/activity configuration, enables device state, requests optional threaded IRQ, enables runtime PM, and registers IIO. Reads of pedometer-derived data require either an enabled event or step counter so the device remains powered. Config writes update cached words, write hardware, set the CONFIG bit, then poll for firmware to clear it.

State and persistence: cached `conf` mirrors firmware config and is the source for sysfs reads. `events[]`, `stepcnt_enabled`, `stepcnt`, `activity`, and `gpio_bitnum` track software event routing and change detection. Hardware pedometer config persists until reset/rewrite.

Dependencies and integration points: shared MMA9551 core, I2C/ACPI, runtime PM, IIO events/sysfs enums, and optional IRQ line for GPIO6-routed pedometer status bits.

Risks: without IRQ, events can be enabled but no interrupt delivery occurs. `mma9553_read_status_word()` refuses data unless step counting or an event is enabled, which is intentional but easy to surprise userspace. Config polling only retries twice.

Test signals: pedometer app identification, default config writes, step-count enable power balancing, height/weight/gender/debounce/int-time sysfs, step and activity event routing through MRGFL/STEPCHG/ACTCHG bits, IRQ timestamp split handler, runtime/system PM, and app reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mma9553.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/msa311.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/msa311.c

Purpose: I2C IIO driver for the MEMSensing MSA311 3-axis accelerometer. It supports raw 12-bit acceleration, selectable full-scale and output data rate, runtime PM suspend/normal modes, debugfs register access, triggered buffers, and optional NEW_DATA interrupt trigger.

Important APIs/types/functions: `enum msa311_fields` and `msa311_reg_fields[]` define regmap-field access. `struct msa311_priv` stores regmap, field handles, device, lock, chip name, and optional trigger. Core functions include `msa311_get/set_odr()`, `msa311_set_pwr_mode()`, `msa311_get_axis()`, raw/read-avail/write paths, buffer pre/post hooks, trigger ops, IRQ thread, part-id/reset/chip-init/setup-interrupt helpers, probe, and runtime PM callbacks.

Control flow: probe allocates IIO state, initializes regmap and all fields, enables VDD, checks part id, soft-resets, enters normal mode, registers a devm powerdown action, enables runtime autosuspend, initializes range/interrupt/axis/ODR defaults, sets up triggered buffer and optional new-data trigger, autosuspends, and registers IIO. Raw reads and writes resume runtime PM, lock hardware access, perform regmap/field operations, then autosuspend. Buffer reads iterate active channels and push timestamped samples.

State and persistence: regmap uses MAPLE cache with volatile accelerometer/status registers. Runtime power mode is stored in hardware; software holds field handles and chip name. No explicit software cache for scale or ODR is kept.

Dependencies and integration points: I2C regmap/regmap-field, regulator `vdd`, runtime PM, IIO buffers/triggers/debugfs, OF/I2C matching, and units/string helper APIs.

Risks: `msa311_write_scale()` returns success when `val` is nonzero, which may silently accept invalid integral scales instead of `-EINVAL`. Low-power mode is defined but unsupported by `msa311_set_odr()`. NEW_DATA IRQ status is not read because the bit auto-clears, so interrupt validity relies on driver enable state.

Test signals: part-id warning path, reset and power-mode transitions, scale/ODR availability and writes, direct-read exclusion during buffers, runtime autosuspend with wait-for-next-data, triggered buffer channel masks, IRQ-backed new-data trigger, debugfs register access, and regulator failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/msa311.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mxc4005.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mxc4005.c

Purpose: I2C IIO driver for MEMSIC MXC4005/MXC6655/MDA6655 3-axis accelerometers. It provides raw 12-bit acceleration, selectable 2g/4g/8g scale, mount matrix, triggered buffer capture, optional data-ready trigger, and sleep PM state restoration.

Important APIs/types/functions: `struct mxc4005_data` stores device, mutex, regmap, optional trigger, orientation, scan buffer, trigger state, and cached control/interrupt mask registers. `mxc4005_read_axis/read_xyz()`, `mxc4005_read_scale()`, `mxc4005_set_scale()`, raw read/write handlers, trigger handler/ops, `mxc4005_chip_init()`, probe, suspend, and resume are central.

Control flow: probe creates regmap with readable/writeable filters, resets and masks interrupts, initializes mutex, reads ACPI `ROTM` or generic mount matrix, sets IIO metadata, installs a triggered buffer, optionally allocates a data-ready trigger and IRQ, then registers IIO. Trigger enable writes `INT_MASK1` and caches the mask. Buffer handler bulk-reads X/Y/Z big-endian data and pushes with pollfunc timestamp. Resume resets the chip, restores control and interrupt masks.

State and persistence: `control` is saved on suspend and restored after reset on resume. `int_mask1` and `trigger_enabled` mirror data-ready trigger configuration. Orientation persists in private state.

Dependencies and integration points: I2C regmap, IIO triggered buffers/triggers, ACPI/OF matching, mount matrix helpers, and system sleep PM.

Risks: `mxc4005_read_scale()` shifts the whole control register without masking before indexing, so unrelated high bits could reject scale reads. Direct raw reads check `iio_buffer_enabled()` but do not lock against concurrent scale writes. Chip ID is logged but not validated.

Test signals: scale writes/readback, raw sign extension, buffer scan order, data-ready IRQ falling edge trigger and reenable interrupt clear, mount matrix from ACPI and firmware properties, suspend/resume restoring scale and trigger mask, and reset timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mxc4005.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mxc6255.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/mxc6255.c

Purpose: minimal I2C IIO driver for MEMSIC MXC6255/MXC6225 orientation-sensing 2-axis accelerometers. It exposes signed 8-bit X/Y acceleration and a fixed 2g scale.

Important APIs/types/functions: `struct mxc6255_data` stores client and regmap. `mxc6255_read_raw()` handles raw register reads and fixed scale. `mxc6255_is_readable_reg()` constrains regmap reads. `mxc6255_probe()` initializes regmap, validates chip id, configures IIO channels, and registers the device.

Control flow: probe allocates the IIO device, creates an I2C regmap, fills private data, reads chip id register, checks low five bits against `0x05`, and registers IIO direct-mode channels. Raw reads use regmap, sign-extend bit 7, and return integer values.

State and persistence: no mutable software state beyond client/regmap pointers. The driver performs no power-management or mode setup; it assumes the device is readable after binding.

Dependencies and integration points: I2C, regmap, ACPI and I2C ids, and IIO direct mode.

Risks: no OF table is present. No PM callbacks exist. The chip-id mask accepts any upper bits, which may be intended but should be validated against hardware variants. No locking is used, but there are no write paths.

Test signals: ACPI/I2C binding for both ids, chip-id reject path, raw X/Y sign extension, fixed scale sysfs, and behavior across system suspend where platform power may reset the device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/mxc6255.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/sca3000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/sca3000.c

Purpose: SPI IIO driver for VTI SCA3000 accelerometer variants. It supports direct acceleration reads, optional temperature channel, scale/sample-frequency/low-pass controls, motion and freefall events, hardware FIFO buffering through kfifo, IRQ handling, and protected control-register access.

Important APIs/types/functions: `struct sca3000_state` owns SPI device, variant info, motion-detect use count, mutex, and DMA-aligned TX/RX buffers. `struct sca3000_chip_info` captures variant scale, temperature availability, mode frequencies, filter cutoffs, and nonlinear motion thresholds. Key paths include SPI read/write helpers, lock/unlock protected control register helpers, raw read/write handlers, event value/config handlers, FIFO ring setup, interrupt processing, clean setup, stop-all-interrupts action, and probe.

Control flow: probe selects variant info from SPI id match data, configures IIO channels, sets up a kfifo buffer, requests optional threaded IRQ, resets hardware into a predictable state, prints revision, registers an interrupt-disable cleanup action, and registers IIO. Direct accel reads reject access while motion-detect mode is active. Sample frequency derives from current measurement mode plus output divider. Low-pass writes switch measurement modes. IRQ handler reads interrupt status, drains FIFO half-full samples, and pushes freefall/motion events.

State and persistence: `mo_det_use_count` tracks how many axis motion events require motion-detect mode. Hardware mode, FIFO enable, interrupt masks, thresholds, and protected control registers persist in the chip until clean setup or cleanup modifies them. TX/RX buffers are reused under mutex for SPI transfers.

Dependencies and integration points: SPI synchronous transfers, IIO events, kfifo buffers, sysfs attributes, IRQ threading, devm cleanup actions, and variant match data.

Risks: motion detection stops normal acceleration acquisition and mode restoration assumes normal mode. FIFO sample pushing lacks timestamps. `sca3000_write_raw_samp_freq()` has an `if`/`if`/`else if` chain where the second `if` pairs with the `else`, so base/2 still falls through correctly only because base/4 is false; this deserves careful tests. Protected-register unlock sequencing is hardware-fragile.

Test signals: probe for all four variants, revision read, direct accel/temp reads, sample frequency and 3 dB filter mode changes, event threshold encode/decode, motion/freefall enable/disable transitions, FIFO enable/disable and half-full draining, IRQ status classification, clean setup clearing flash-backed state, and cleanup disabling interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/sca3000.c -->
