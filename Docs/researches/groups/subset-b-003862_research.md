# Research: subset-b-003862

This grouped report covers Analog Devices ADXL367/ADXL372/ADXL380 accelerometer drivers and Bosch BMA180/BMA220/BMA400 accelerometer drivers under `sources/distributed-fs/ceph-client/drivers/iio/accel/`. Each section is source-tree aligned and wrapped for reconciliation into its per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.c

## Purpose

`adxl367.c` is the transport-independent IIO core for the Analog Devices ADXL367 low-power 3-axis accelerometer. It exposes accelerometer X/Y/Z channels, an internal temperature channel, an external ADC voltage channel, activity/inactivity threshold events, direct debug register access, and hardware FIFO buffered capture.

## Important APIs, Types, and Functions

The central state is `struct adxl367_state`, which keeps the regmap, transport `adxl367_ops`, device pointer, lock, selected ODR/range, cached activity thresholds and timers, FIFO set size/watermark, DMA-aligned FIFO/sample buffers, and small register write buffers. `adxl367_probe()` is the exported bus-facing entry point. Core configuration helpers include `adxl367_set_measure_en()`, `_adxl367_set_odr()`, `adxl367_set_range()`, threshold/time setters, FIFO mode/format/watermark setters, and temperature/ADC enable helpers.

The IIO surface is implemented by `adxl367_info`: `read_raw`, `write_raw`, `read_avail`, event config/value callbacks, `debugfs_reg_access`, `hwfifo_set_watermark`, and `update_scan_mode`. `adxl367_irq_handler()` reads status/FIFO count, pushes threshold events, and drains FIFO samples through the transport `read_fifo` callback.

## Control Flow

Probe allocates an IIO device, enables `vdd` and `vddio`, writes the reset code, waits for reset completion, validates the AD vendor ID, applies default setup, registers a kfifo buffer with hardware FIFO attributes, requests a threaded IRQ, and registers the IIO device. Setup programs default activity and inactivity thresholds, looped activity processing, 400 Hz ODR, activity/inactivity timers, then enters measurement mode.

Direct reads claim direct mode, optionally enable the temperature or ADC block, bulk-read a 16-bit sample, extract/sign-extend 14-bit data, and disable the auxiliary block again. Writes to scale or sampling frequency require direct mode and temporarily put the chip in standby because range/ODR changes affect active measurement behavior. Buffer enable configures the selected FIFO format from the active scan mask, enables auxiliary blocks when selected, enables FIFO watermark interrupts, switches FIFO to stream mode, and returns to measure mode; buffer disable reverses this sequence.

## State and Persistence Behavior

State is volatile and split between hardware registers and cached driver fields. The mutex protects driver fields and multi-register sequences. Range changes rescale cached activity thresholds and rewrite both thresholds. ODR changes rewrite activity and inactivity timer registers because timer periods depend on sample rate. FIFO watermark is cached as sample sets, while the hardware stores samples, so writes are converted through `fifo_set_size` and capped to the 511-sample hardware limit.

## Dependencies and Integration Points

The file depends on regmap, regulators, threaded IRQs, IIO core events, kfifo buffers, scan masks, sysfs FIFO attributes, and a small bus abstraction from `adxl367.h`. The actual FIFO read path is delegated to I2C/SPI wrappers because the command differs by transport.

## Risks

The standby/measure transitions are critical; early returns after disabling measurement may leave the device in standby if a later write fails. FIFO handling assumes valid scan masks and a nonzero `fifo_set_size`. `adxl367_push_fifo_data()` only drains when FIFO-full status is set, even though the interrupt is configured as watermark, so watermark semantics should be validated against hardware. Activity threshold/timer conversions silently clamp to hardware maxima. The typo-like enum name `ADCL367_ACT_REF_ENABLED` is harmless locally but easy to misread.

## Test Signals

Useful signals are successful regulator enable and device ID validation, sysfs raw/scale/offset/sample-frequency reads, rejection of invalid ODR/range values, event enable/value/period round-trips, FIFO watermark clamping, buffer enable for every advertised scan mask, IRQ delivery for activity/inactivity, FIFO sample ordering for X/Y/Z plus temp or ADC masks, and suspend-free unload with devm cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.h

## Purpose

`adxl367.h` is the private interface between the ADXL367 transport wrappers and the shared IIO core. It keeps bus-specific code out of `adxl367.c` while allowing the core to use a transport-specific FIFO command.

## Important APIs, Types, and Functions

`struct adxl367_ops` currently contains one callback, `read_fifo(void *context, __be16 *fifo_buf, unsigned int fifo_entries)`. `adxl367_probe()` is declared as the common probe entry and accepts a device, ops table, opaque bus context, regmap, and IRQ number.

## Control Flow

I2C and SPI probes allocate their bus state, create a regmap, construct an `adxl367_ops` table, and call `adxl367_probe()`. The core stores the context and calls `ops->read_fifo()` only from the IRQ FIFO drain path.

## State and Persistence Behavior

The header owns no state. It defines the callback contract: the context is transport-owned and remains valid for the lifetime of the devm-managed IIO device.

## Dependencies and Integration Points

The file includes `linux/types.h` for `__be16` and forward declares `struct device` and `struct regmap`. The exported probe symbol is namespaced as `IIO_ADXL367` in the core and imported by bus modules.

## Risks

Any extension of `struct adxl367_ops` must update both bus wrappers. The FIFO callback uses entry counts rather than byte counts; callers and implementations must preserve that unit.

## Test Signals

Build tests should verify both I2C and SPI wrappers compile against this header, import the namespace, and pass a non-null `read_fifo` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_i2c.c

## Purpose

`adxl367_i2c.c` is the I2C transport wrapper for the ADXL367 core. It supplies an 8-bit regmap and implements the special non-incrementing FIFO read used by buffered capture.

## Important APIs, Types, and Functions

`struct adxl367_i2c_state` stores the regmap pointer passed as transport context. `adxl367_i2c_read_fifo()` calls `regmap_noinc_read()` on FIFO data register `0x18`. `adxl367_i2c_probe()` allocates state, initializes the I2C regmap, and calls `adxl367_probe()`.

## Control Flow

Device matching happens through I2C ID `adxl367` or OF compatible `adi,adxl367`. Probe creates the regmap with `.readable_noinc_reg = adxl367_readable_noinc_reg`, stores it in the state object, and hands the client IRQ to the core.

## State and Persistence Behavior

The wrapper has no persistent hardware policy. State is devm-allocated and exists to bind regmap and callback context together.

## Dependencies and Integration Points

It depends on the I2C core, regmap, module device tables, and the `IIO_ADXL367` exported namespace. The core owns regulators, reset, events, and IIO registration.

## Risks

FIFO reads rely on the regmap no-increment path being used only for register `0x18`; if regmap configuration changes, FIFO burst semantics can break. The wrapper forwards `client->irq` directly, so board descriptions without an IRQ will fail in the common core because the core requests an IRQ unconditionally.

## Test Signals

Probe should create a regmap, bind by OF/I2C ID, call the common core, and drain FIFO data through `regmap_noinc_read()` with the expected byte count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_spi.c

## Purpose

`adxl367_spi.c` is the SPI transport wrapper for the ADXL367 core. It implements the chip's command-prefixed SPI register and FIFO protocol through a custom regmap bus and a FIFO callback.

## Important APIs, Types, and Functions

`struct adxl367_spi_state` stores the SPI device, preinitialized `spi_message` objects, transfer arrays, and DMA-aligned command buffers. `adxl367_read()`, `adxl367_write()`, and `adxl367_read_fifo()` are the custom regmap/FIFO operations. `adxl367_spi_probe()` builds the messages for write command `0x0A`, read command `0x0B`, and FIFO command `0x0D`, then calls the common probe.

## Control Flow

Probe allocates state, initializes three two-transfer SPI messages, creates a regmap with the custom bus, and invokes `adxl367_probe()` with the SPI IRQ. Register writes send command then address/data in a second transfer. Register reads send command/address then receive values. FIFO reads send the FIFO command then receive `fifo_entries * sizeof(__be16)` into the core buffer.

## State and Persistence Behavior

The wrapper caches only transfer descriptors and command bytes. Per-transfer lengths and data pointers are updated before each transaction while the common core serializes higher-level calls.

## Dependencies and Integration Points

It depends on SPI, regmap's custom bus API, IIO DMA alignment definitions, module tables, and the `IIO_ADXL367` namespace. Matching supports SPI ID and OF compatible `adi,adxl367`.

## Risks

The reusable `spi_message` objects assume no concurrent core calls mutate transfer descriptors at the same time; the core lock is therefore important. DMA alignment comments apply only to the command buffer explicitly aligned; transfer descriptors and RX buffers must continue to satisfy SPI controller requirements. Missing or invalid IRQs propagate to the common core.

## Test Signals

SPI logic is validated by probe, device ID read through command `0x0B`, reset write through command `0x0A`, FIFO burst command `0x0D`, and successful buffered capture without transfer length corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl367_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.c

## Purpose

`adxl372.c` is the shared IIO core for ADXL371 and ADXL372 high-g accelerometers. It provides direct acceleration channels, activity/inactivity threshold events, configurable ODR and bandwidth, optional FIFO buffered capture, and IIO trigger integration.

## Important APIs, Types, and Functions

`struct adxl372_chip_info` is instantiated for ADXL371 and ADXL372 with sample-rate tables, bandwidth tables, timer scales, maximum ODR, and FIFO support. ADXL371 disables FIFO due to a documented silicon FIFO alignment erratum. `struct adxl372_state` stores chip info, IRQ, regmap, data-ready and peak triggers, FIFO mode/format/axis mask, ODR/bandwidth, event timers, interrupt bitmask, watermark, FIFO buffer, and threshold mutex.

Important functions include `adxl372_setup()`, `adxl372_set_op_mode()`, ODR/bandwidth setters, activity threshold/time setters, `adxl372_configure_fifo()`, `adxl372_trigger_handler()`, event callbacks, buffer setup, and exported `adxl372_probe()`.

## Control Flow

Probe allocates the IIO device, stores chip data, sets direct mode plus software buffer support only when FIFO is supported, runs setup, optionally creates triggered buffers and triggers, then registers the device. Setup verifies device ID, resets the chip, enters standby, programs default 1 g activity and 100 mg inactivity thresholds, looped activity mode, max ODR, 3200 Hz bandwidth, 1 ms activity and 10 s inactivity timers, then enters full-bandwidth measurement mode.

Runtime raw reads claim direct mode and read 16-bit axis registers. Sample frequency writes choose the closest supported ODR, recalculate timer registers, and constrain bandwidth to not exceed half the ODR. Buffer enable maps the active scan mask to FIFO format, handles peak FIFO mode, clamps watermark by set size, enables FIFO-full interrupts, configures FIFO in standby, and resumes measurement. The trigger handler reads status and FIFO count, pushes threshold events, drains FIFO when full, optionally rearranges peak samples, and notifies trigger completion.

## State and Persistence Behavior

The driver caches ODR, bandwidth, event durations, FIFO mode and watermark, and interrupt enable bits. Hardware timer registers are recomputed when ODR changes because timing scale depends on ODR and chip variant. Threshold writes use a dedicated mutex to serialize high/low byte updates. FIFO configuration always transitions through standby.

## Dependencies and Integration Points

The core depends on regmap, IIO triggered buffers, IIO triggers, event APIs, no-increment FIFO reads, and chip-info data supplied by I2C/SPI wrappers. `adxl372_readable_noinc_reg()` is exported so bus regmaps can mark FIFO data as a no-increment register.

## Risks

`adxl372_write_raw()` does not claim direct mode before changing ODR or bandwidth, so buffered operation interactions depend on higher-level IIO usage discipline. The data-ready trigger set-state only ORs the FIFO-full bit when enabling and does not clear it when disabling. FIFO drain subtracts one sample set before reading to avoid overwrite ordering issues; underflow must be avoided by the FIFO-full status and configured watermark. `adxl372_get_fifo_enabled()` prints enum value rather than boolean, which is user-visible but intentional-looking legacy behavior.

## Test Signals

Tests should cover ADXL371 vs ADXL372 chip-info binding, FIFO disabled for ADXL371, direct raw reads and scale, ODR/bandwidth availability and Nyquist truncation, event threshold/timer reads and writes, trigger allocation only with IRQ, peak FIFO trigger mode, watermark clamping, and FIFO drain ordering for one-, two-, and three-axis scan masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.h

## Purpose

`adxl372.h` defines the private shared interface for ADXL371/ADXL372 I2C and SPI wrappers and the common IIO core.

## Important APIs, Types, and Functions

The header defines `ADXL372_REVID`, `struct adxl372_chip_info`, extern declarations for `adxl371_chip_info` and `adxl372_chip_info`, exported `adxl372_probe()`, and exported `adxl372_readable_noinc_reg()`. Chip info captures rate tables, timer conversion scales, maximum ODR, and whether FIFO is supported.

## Control Flow

Bus wrappers obtain match data pointing to one of the chip-info instances, create a regmap, and call `adxl372_probe()`. The common core uses chip info to choose IIO name, available rates, timer scaling, and FIFO capability.

## State and Persistence Behavior

The header owns no state, but its chip-info contract controls persistent runtime behavior such as disabling FIFO for ADXL371 and choosing timer units.

## Dependencies and Integration Points

It expects users to include Linux device/regmap declarations before or through included headers. Exported symbols are namespaced as `IIO_ADXL372` and imported by both bus modules.

## Risks

Changing chip-info fields affects both transports. Incorrect `num_freqs` or `max_odr` values would corrupt availability lists and timer conversion.

## Test Signals

Build coverage should ensure I2C and SPI modules resolve chip-info symbols, common probe, and FIFO no-increment helper under the `IIO_ADXL372` namespace.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_i2c.c

## Purpose

`adxl372_i2c.c` is the I2C wrapper for ADXL371/ADXL372. It creates the I2C regmap, selects chip-info match data, warns about early ADXL372 I2C revisions, and delegates the IIO device to the common core.

## Important APIs, Types, and Functions

`adxl372_regmap_config` uses 8-bit registers and values and marks FIFO data readable with no increment. `adxl372_i2c_probe()` fetches `struct adxl372_chip_info` from match data, initializes the regmap, reads `ADXL372_REVID`, emits a warning when revision is less than 3, and calls `adxl372_probe()`.

## Control Flow

Matching supports I2C IDs and OF compatibles for `adi,adxl371` and `adi,adxl372`. Probe is thin: all validation except the revision warning is performed by the common core.

## State and Persistence Behavior

The wrapper maintains no state beyond the devm-managed regmap. The revision read does not change hardware state.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, match-data plumbing, and the `IIO_ADXL372` namespace. It forwards `client->irq` so trigger/buffer support depends on board IRQ wiring.

## Risks

If match data is missing, the common core would receive a null chip-info pointer. The early-revision I2C warning is advisory only; the driver still binds, so bus-level failures may occur later.

## Test Signals

Expected validation includes both chip compatibles resolving to the right name/rate table, revision warning on mocked values below 3, FIFO no-increment reads, and correct behavior with and without IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_spi.c

## Purpose

`adxl372_spi.c` is the SPI wrapper for ADXL371/ADXL372. It configures the SPI regmap protocol and delegates all sensor behavior to `adxl372_probe()`.

## Important APIs, Types, and Functions

`adxl372_spi_regmap_config` uses 7 register bits, one pad bit, 8-bit values, read flag bit 0, and the shared FIFO no-increment helper. `adxl372_spi_probe()` obtains chip-info match data, initializes a SPI regmap, and calls the common core with `spi->irq`.

## Control Flow

SPI IDs and OF compatibles support both ADXL371 and ADXL372. Probe performs no device revision handling; chip ID reset and setup are common-core responsibilities.

## State and Persistence Behavior

The wrapper has no persistent private state. Hardware state is managed by the core through regmap.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, match data, and `IIO_ADXL372` symbol namespace import.

## Risks

SPI protocol correctness depends on the regmap configuration's register width, pad bit, and read flag. Missing match data or IRQ wiring will surface as common-core probe or trigger limitations.

## Test Signals

Tests should verify ID/OF matching for both chip variants, successful regmap reads/writes with the expected SPI framing, common probe invocation, and FIFO no-increment burst behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl372_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.c

## Purpose

`adxl380.c` is the shared IIO core for ADXL318, ADXL319, ADXL380, and ADXL382 accelerometers. It exposes accelerometer and temperature channels, configurable scale/sample rate/LPF/HPF/calibration bias, hardware FIFO buffering, threshold events, tap/double-tap gesture events, and chip-specific feature surfaces.

## Important APIs, Types, and Functions

`struct adxl380_chip_info` instances describe chip name, part ID family, scale table, sample-frequency table, temperature offset, low-power capability, and the IIO info table to expose. ADXL318/319 use `adxl318_info` without event callbacks; ADXL380/382 use `adxl380_info` with threshold and gesture events. `struct adxl380_state` stores regmap, device/chip info, lock, tap axis, range/ODR, FIFO set size/watermark, cached thresholds/timers/tap settings, IRQ/int-map selection, and dynamic LPF/HPF availability tables.

Major functions include measurement enable/disable, ODR/filter/range setters, activity/inactivity threshold and timer setters, tap configuration, FIFO sample programming, IRQ handler, raw/event callbacks, chip-info declarations, IRQ configuration, setup, and exported `adxl380_probe()`.

## Control Flow

Probe allocates the IIO device, defaults ODR to DSM, enables `vddio` and `vsupply`, calls setup, registers a kfifo buffer with FIFO attributes, then registers the device. Setup checks the AD vendor ID and part ID, differentiates ADXL380/382 through `MISC_0`, issues soft reset, enables all channels, selects streamed FIFO mode, enables all axes for activity/inactivity, configures a named INT0 or INT1 level-triggered interrupt, fills filter availability tables, and enters measurement mode.

Direct reads claim direct mode and bulk-read channel data. Writes update ODR, calibration bias, LPF, HPF, scale, thresholds, timers, and tap settings, usually by entering standby, writing registers, updating cached fields, and returning to measure mode. Buffer enable disables unselected channels, computes FIFO set size, clamps watermark, writes FIFO sample count, enables FIFO and watermark interrupt, and resumes measurement. The IRQ handler serializes status reads, pushes threshold/tap events, checks FIFO watermark, drains rounded FIFO entries with `regmap_noinc_read()`, and pushes samples to IIO buffers.

## State and Persistence Behavior

The mutex protects multi-register transactions and cached state. Activity/inactivity events can force ODR to VLP on low-power-capable chips when measurement is re-enabled. Range changes rescale cached thresholds and rewrite hardware threshold registers. LPF/HPF availability is derived from the current ODR and refreshed on ODR changes. Interrupt register addresses are selected at runtime from firmware-named `INT0` or `INT1`.

## Dependencies and Integration Points

The core depends on regmap, firmware properties for named IRQs, regulators, level-triggered threaded IRQs, IIO kfifo buffers, event sysfs attributes, no-increment FIFO reads, and chip info supplied by I2C/SPI wrappers. `adxl380_readable_noinc_reg()` is exported for bus regmap configs.

## Risks

`adxl380_write_tap_dur_us()` lacks the same explicit mutex guard used by nearby tap setters and can be called while its caller already holds the lock from the sysfs store path, making lock sequencing worth review. `adxl380_get_fifo_entries()` shifts the masked high bit expression and should be validated for correct 9-bit count extraction. `adxl380_samp_freq_avail()` returns success even if `adxl380_act_inact_enabled()` fails, which can hide register-read errors. Setup warns rather than fails on several ID mismatches, so the driver can bind to unexpected silicon. Interrupt configuration rejects edge-triggered IRQs and requires firmware names.

## Test Signals

Validation should cover all four chip compatibles, chip-info-specific event availability, regulator failures, missing/invalid INT0/INT1 firmware IRQs, level-high and level-low polarity programming, raw accel/temp reads, calibration bias sign extension, ODR-dependent LPF/HPF tables, low-power activity mode ODR restrictions, tap timing/value attributes, FIFO watermark and selected-channel buffering, and IRQ event plus FIFO delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.h

## Purpose

`adxl380.h` defines the private shared contract for ADXL318/319/380/382 bus wrappers and the common ADXL380-family IIO core.

## Important APIs, Types, and Functions

The header defines `enum adxl380_odr`, `struct adxl380_chip_info`, extern chip-info objects for ADXL318, ADXL319, ADXL380, and ADXL382, exported `adxl380_probe()`, and exported `adxl380_readable_noinc_reg()`. Chip info includes the IIO info pointer, so variants can expose different attribute/event sets.

## Control Flow

I2C and SPI wrappers resolve match data to a chip-info object, create a regmap, and pass both to `adxl380_probe()`. The common core then uses chip info to choose scales, rates, temperature offset, event support, low-power behavior, and IIO name.

## State and Persistence Behavior

The header has no mutable state. Its static chip-info declarations encode variant behavior for the lifetime of each bound device.

## Dependencies and Integration Points

The file includes regmap declarations and expects IIO/device types through users. Exported symbols use the `IIO_ADXL380` namespace.

## Risks

Because `struct adxl380_chip_info` contains fixed-size arrays, table size must stay aligned with `ADXL380_ODR_MAX` and the three range encodings. A wrong `.info` pointer would expose or hide event callbacks for a whole chip family.

## Test Signals

Build tests should verify both bus wrappers resolve all four chip-info symbols, common probe, and FIFO no-increment helper, and that each ID table entry passes the intended chip-info pointer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_i2c.c

## Purpose

`adxl380_i2c.c` is the I2C wrapper for ADXL318/319/380/382 devices. It creates the I2C regmap and delegates all device behavior to the shared core.

## Important APIs, Types, and Functions

`adxl380_regmap_config` uses 8-bit register and value fields plus the common no-increment FIFO helper. `adxl380_i2c_probe()` obtains chip data via `i2c_get_match_data()`, initializes the regmap, and calls `adxl380_probe()`.

## Control Flow

I2C IDs and OF compatibles cover `adi,adxl318`, `adi,adxl319`, `adi,adxl380`, and `adi,adxl382`. Probe is otherwise linear and devm-managed.

## State and Persistence Behavior

No wrapper-private state is stored. Hardware reset, regulators, IRQs, and IIO registration are all common-core responsibilities.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, match data, and the `IIO_ADXL380` namespace. Firmware still must provide named interrupts consumed by the common core.

## Risks

Missing match data would lead to a null chip-info pointer in the core. The wrapper has no fallback name from `i2c_device_id`; correct table data is therefore essential.

## Test Signals

Tests should bind each supported compatible, verify the matching chip name and attribute set, exercise FIFO no-increment reads, and confirm core error propagation for regulator or IRQ failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_spi.c

## Purpose

`adxl380_spi.c` is the SPI wrapper for ADXL318/319/380/382 devices. It configures the SPI regmap framing and passes variant chip data into the common core.

## Important APIs, Types, and Functions

`adxl380_spi_regmap_config` uses 7 register bits, one pad bit, 8-bit values, read flag bit 0, and the common FIFO no-increment helper. `adxl380_spi_probe()` gets chip data from SPI match data, initializes a SPI regmap, and calls `adxl380_probe()`.

## Control Flow

SPI ID and OF tables support all four chip variants. There is no wrapper-level ID read; the common core performs reset, ID checks, and setup.

## State and Persistence Behavior

The wrapper has no private runtime state. Regmap and core devm resources own all state.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, match data, and `IIO_ADXL380` namespace import.

## Risks

Protocol correctness depends on the 7-bit register plus pad-bit regmap layout and read flag. Any SPI controller limitation around no-increment FIFO transfers must be handled by regmap/SPI core behavior.

## Test Signals

Probe should work for all four IDs/compatibles, read expected chip ID through the core, expose chip-specific attributes, and handle FIFO reads through the no-increment register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/adxl380_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma180.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma180.c

## Purpose

`bma180.c` is a legacy I2C-only IIO driver for Bosch BMA023, BMA150, BMA180, BMA250, and SMB380 accelerometers. It exposes acceleration channels, optional temperature, scale, low-pass filter bandwidth, optional power-mode enum, mount matrix, direct reads, and IRQ-triggered buffered capture.

## Important APIs, Types, and Functions

`struct bma180_part_info` describes per-chip ID, channel layout, scale and bandwidth tables, temperature offset, register/mask locations, reset values, and chip-specific config/disable callbacks. `struct bma180_data` stores regulators, I2C client, trigger, part info, orientation, mutex, sleep state, selected scale/bandwidth, and power mode.

Core helpers include `bma180_get_data_reg()`, `bma180_set_bits()`, interrupt enable/reset helpers, sleep and EEPROM-write enable, bandwidth/scale/power setters, chip init/config/disable functions, IIO raw read/write callbacks, trigger handler, probe/remove, and PM suspend/resume.

## Control Flow

Probe allocates an IIO device, reads mount matrix, gets and enables `vdd`/`vddio` regulators with voltage constraints, waits for power-up, runs the chip-specific config callback, initializes channels and IIO info, optionally allocates/registers a data-ready trigger and IRQ, sets up a triggered buffer, and registers the IIO device. Remove unregisters IIO resources, disables the chip through the part callback, and disables regulators.

Raw reads claim direct mode, lock, reject reads while asleep, read temperature or word-sized axis data via SMBus, sign-extend according to channel type, and return IIO values. Scale and bandwidth writes lock and program chip-specific fields. The triggered buffer handler reads all active channels under the mutex and pushes a timestamped scan.

## State and Persistence Behavior

The driver mirrors selected bandwidth, scale, power mode, and sleep state in memory. Hardware settings persist until reset or remove/suspend. BMA180-specific setup enables EEPROM writing, disables wake-up, enables sample skip, and configures low-noise power mode; cleanup disables new-data interrupts, disables EEPROM writes, and sleeps the chip. PM suspend/resume toggles sleep state only.

## Dependencies and Integration Points

The driver depends on I2C SMBus operations, regulators, IIO sysfs and triggered buffer APIs, optional IRQs, mount matrix parsing, and legacy manual cleanup rather than fully devm-managed IIO registration. Matching is through I2C IDs and OF compatibles.

## Risks

`bma180_set_bits()` computes `reg_val` before checking whether the read failed, so a negative read value is masked into a byte before the function returns the error. Probe initializes the mutex after chip config, yet config paths do not use the mutex; later paths do. Error cleanup is manual and must stay balanced across trigger, buffer, chip, and regulator steps. The driver cannot support SPI despite some chips being physically capable. Suspend may race userspace reads unless IIO core access is quiesced.

## Test Signals

Test signals include successful binding for every ID/compatible, chip ID rejection, regulator voltage/enable failure handling, correct channel count per variant, scale/bandwidth available lists, raw accel/temp conversion, power-mode enum for BMA180/BMA250, trigger enable resetting interrupts, buffered scans with active masks, and remove/suspend/resume returning the chip to expected sleep states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma180.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220.h

## Purpose

`bma220.h` is the private interface shared by the BMA220 core and its I2C/SPI wrappers.

## Important APIs, Types, and Functions

The header defines watchdog register constants, extern regmap configs for I2C and SPI, exported PM ops, and `bma220_common_probe()`. The watchdog constants are used only by the I2C wrapper after common probe.

## Control Flow

Wrappers create a bus regmap from the exported config, call `bma220_common_probe()`, and optionally perform bus-specific post-probe setup such as I2C watchdog programming.

## State and Persistence Behavior

No mutable state is defined here. The exported regmap configs encode bus register addressing and writable-register policy.

## Dependencies and Integration Points

The header depends on PM and regmap declarations. Exported symbols use the `IIO_BOSCH_BMA220` namespace.

## Risks

Changing register constants or exported config names requires updates in all three BMA220 files. The guard macro lacks a trailing underscore consistency with some kernel styles but is local.

## Test Signals

Build coverage should prove both wrappers resolve regmap configs, PM ops, and common probe, and that I2C watchdog values remain valid for `BMA220_WDT_MASK`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_core.c

## Purpose

`bma220_core.c` is the shared IIO core for the Bosch BMA220 accelerometer. It exposes three 6-bit acceleration channels, scale and low-pass filter controls, direct debug register access, optional IRQ-triggered buffered capture, and suspend/resume support.

## Important APIs, Types, and Functions

The file defines BMA220 register constants, `struct bma220_data`, channel specs, scale and filter tables, scan masks, writable-register predicate, and exported I2C/SPI regmap configs. The core IIO callbacks are `bma220_read_raw()`, `bma220_write_raw()`, `bma220_read_avail()`, and `bma220_reg_access()`. Lifecycle and power helpers include `bma220_init()`, `bma220_power()`, `bma220_reset()`, `bma220_deinit()`, `bma220_common_probe()`, and exported PM ops.

## Control Flow

Common probe allocates the IIO device, stores regmap, enables regulators `vddd`, `vddio`, and `vdda`, reads chip ID, powers and resets the chip by register-read side effects, initializes the mutex, configures IIO metadata and scan masks, optionally allocates/registers an IIO trigger and threaded IRQ, registers a cleanup action to suspend the chip, sets up a triggered buffer, and registers the IIO device.

Direct reads lock and read one acceleration register, sign-extending the 6-bit shifted value. Writes lock and update range/filter registers after exact table matching. The IRQ handler reads interrupt flag register `IF1`, polls the nested trigger when DRDY is set, and the trigger handler bulk-reads X/Y/Z and pushes a timestamped scan.

## State and Persistence Behavior

The driver caches range index and LPF index after successful writes. Hardware power and reset are unusual: reading the suspend or soft-reset register transitions state, so helpers perform up to two reads and compare returned mode values. Devm cleanup powers the chip down; PM suspend/resume use the same read-triggered power helper.

## Dependencies and Integration Points

It depends on regmap, regulators, IIO triggered buffers/triggers, threaded IRQs, PM, and bus wrappers that provide correctly shifted regmap addressing. SPI uses read flag bit 7; I2C uses `reg_shift = -1` to map SPI-style names to I2C addresses.

## Risks

The register-read side effects in `bma220_power()` and `bma220_reset()` are non-obvious and easy to break if converted to normal writes. `bma220_trigger_handler()` returns `IRQ_NONE` on read error without notifying trigger done, which can leave a trigger path waiting. The chip ID mismatch logs informationally and continues rather than failing. The triggered buffer setup error is logged but not returned before `devm_iio_device_register()`, so buffer setup failure may still allow device registration.

## Test Signals

Tests should cover I2C and SPI regmap address mappings, regulator enable failures, power/reset read-state loops, exact scale/filter write matching, direct raw sign extension, DRDY interrupt polling, triggered buffer reads, suspend/resume, and fault injection for bulk-read failure in the trigger handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_i2c.c

## Purpose

`bma220_i2c.c` is the I2C wrapper for the BMA220 core. It creates an I2C regmap using the shared I2C mapping and enables the chip watchdog after common probe.

## Important APIs, Types, and Functions

`bma220_set_wdt()` updates `BMA220_REG_WDT` with a selected watchdog value. `bma220_i2c_probe()` initializes the I2C regmap, calls `bma220_common_probe()`, and then programs the watchdog to `BMA220_WDT_1MS`.

## Control Flow

Matching supports OF compatible `bosch,bma220` and I2C ID `bma220`. Probe fails on regmap or common-probe errors; watchdog programming is the final step.

## State and Persistence Behavior

No wrapper-private state is kept. The watchdog setting persists in hardware until reset or another write.

## Dependencies and Integration Points

It depends on I2C, regmap, bitfield helpers, PM ops imported from the BMA220 namespace, and the shared common probe.

## Risks

If common probe registers the IIO device successfully but watchdog programming fails, probe returns failure after side effects have occurred; devm cleanup should unwind resources, but hardware state sequencing should be tested. I2C address shifting depends entirely on the shared regmap config.

## Test Signals

Validation should include regmap creation, common-probe success, watchdog register update to 1 ms, PM callbacks attached to the driver, and OF/I2C table matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_spi.c

## Purpose

`bma220_spi.c` is the SPI wrapper for the BMA220 core. It creates a SPI regmap and delegates all sensor behavior to `bma220_common_probe()`.

## Important APIs, Types, and Functions

`bma220_spi_probe()` initializes the SPI regmap with `bma220_spi_regmap_config` and calls the common core with `spi->irq`. The file also declares SPI ID, ACPI ID `BMA0220`, and OF compatible tables.

## Control Flow

Probe is linear: create regmap, return a dev_err_probe failure if regmap init fails, otherwise call the common probe. The common core handles regulators, reset, triggers, PM, and IIO registration.

## State and Persistence Behavior

No wrapper-private state or hardware policy is stored in this file.

## Dependencies and Integration Points

It depends on SPI, regmap, module tables, ACPI/OF matching, shared PM ops, and `IIO_BOSCH_BMA220` namespace import.

## Risks

The SPI regmap config's read flag and writable-register constraints are owned by the core; wrapper regressions are mostly matching or regmap-init related. Formatting oddities in `.probe` and `.id_table` assignments are cosmetic.

## Test Signals

Tests should bind by SPI ID, OF, and ACPI IDs, verify common-probe invocation, direct register reads with SPI read flag bit 7, IRQ-triggered buffering, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma220_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400.h -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400.h

## Purpose

`bma400.h` defines shared BMA400 register constants, bit masks, enums, and exported interfaces used by the BMA400 core and I2C/SPI wrappers.

## Important APIs, Types, and Functions

The header covers chip ID, status, acceleration, temperature, FIFO, step counter, power/config, interrupt, generic activity interrupt, tap configuration, and command registers. It defines `enum bma400_generic_intr`, activity-data-source/reference-update/detection enums, scale limits, extern `bma400_regmap_config`, and `bma400_probe()`.

## Control Flow

Bus wrappers include this header, create regmaps using `bma400_regmap_config`, and pass device, regmap, IRQ, and name to the common probe. The core uses register constants for all direct, buffered, and event paths.

## State and Persistence Behavior

The header has no mutable state, but its constants encode hardware ABI. The register definitions control which bits are interpreted as event status, configuration, range, ODR, tap timing, and FIFO state.

## Dependencies and Integration Points

It depends on bit macros and regmap. Exported symbols are namespaced as `IIO_BMA400`.

## Risks

Incorrect masks in this header would affect multiple event and configuration paths. `BMA400_INT_STAT1_*` masks use bits above 8 while status is read as a 16-bit value in the core; callers must preserve that 16-bit interpretation.

## Test Signals

Build and runtime tests should verify both wrappers compile against this header, probe through the common core, and correctly decode step, tap, generic interrupt, range, ODR, and FIFO registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_core.c

## Purpose

`bma400_core.c` is the shared IIO core for the Bosch BMA400 accelerometer. It exposes acceleration, temperature, step count, activity classification, mount matrix, scale, sample frequency, oversampling ratio, triggered buffering, data-ready triggers, and events for step detection, activity, generic activity/inactivity magnitude, and single/double tap gestures.

## Important APIs, Types, and Functions

`struct bma400_data` stores device/regmap, mutex, orientation, power mode, cached sample frequency/OSR/scale, trigger, step/activity/event enable state, tap/generic event masks, and DMA-aligned buffer/status fields. `bma400_regmap_config` marks read-only and volatile registers and uses Maple cache. Important helpers include power/ODR/OSR/scale getters and setters, step enable/read, tap timing sysfs handlers, event enable/value callbacks, trigger set-state/handler, top-level interrupt handler, init, cleanup, and exported `bma400_probe()`.

## Control Flow

Probe allocates IIO state, runs `bma400_init()`, reads mount matrix, initializes the mutex, fills IIO metadata, optionally creates a trigger and threaded IRQ, sets up a triggered buffer, and registers the IIO device. Init enables `vdd`/`vddio`, validates chip ID `0x90`, wakes the chip to normal mode if needed, registers a power-down action, initializes availability tables, caches ODR/OSR/scale, configures INT1 as open drain, and selects the variable ODR filter data source.

Direct reads return processed temperature, steps, activity confidence, raw acceleration, ODR, scale, OSR, or step enable state. Writes set acceleration ODR, scale, OSR, or step enable. Event config writes program generic interrupt engines for rising/falling magnitude events, tap interrupt bits with a 200 Hz and normal-mode constraint, step event mapping, or activity event state. The IRQ handler reads 16-bit status, disables advanced interrupts on engine overrun, pushes tap/generic/step/activity events, and polls the nested trigger on data-ready status. The trigger handler bulk-reads acceleration and optional temperature and pushes a timestamped scan.

## State and Persistence Behavior

The driver keeps cached power mode, sample rate, oversampling ratio, scale, steps enabled, and event enable masks. Hardware settings persist until reset or cleanup. Power cleanup puts the device into sleep. Generic interrupts are initialized with all axes enabled, filtered data source, reference update mode, default threshold, and default duration before mapping/enable bits are set. Activity events depend on the step engine.

## Dependencies and Integration Points

The core depends on regmap with cache/volatile rules, regulators, IIO triggered buffers/triggers, IIO events, mount matrix parsing, IRQ status handling, and bus wrappers. It integrates with sysfs event attributes for tap timing/value availability and with the IIO activity and steps channel types.

## Risks

The TODO header is stale because events, interrupts, and steps are now implemented, which can mislead maintainers. `bma400_tap_event_en()` always updates the single-tap map bit before switching on the requested direction, so double-tap enable paths also touch single-tap mapping. The triggered buffer setup error is returned correctly here, unlike some older drivers, but the IRQ handler reads two status bytes into little-endian `data->status`; mask definitions must remain consistent. Advanced interrupt overrun disables all advanced interrupts and only logs an error, so user-visible event state may become stale. Tap events require normal mode and 200 Hz, which must be enforced in tests.

## Test Signals

Test coverage should include chip ID mismatch, regulator failures, wake-from-sleep sequencing, scale/ODR/OSR available lists and writes, raw and buffered accel/temp reads, step count and step event enable, activity confidence and activity events, generic rising/falling event threshold/period/hysteresis reads and writes, tap timing/value configuration, 200 Hz tap requirement, data-ready trigger polling, interrupt overrun disable behavior, and power-down cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_i2c.c

## Purpose

`bma400_i2c.c` is the I2C transport wrapper for the BMA400 core. It creates the I2C regmap and passes the client IRQ and device name into `bma400_probe()`.

## Important APIs, Types, and Functions

`bma400_i2c_probe()` obtains the I2C device ID, initializes `devm_regmap_init_i2c()` with the shared `bma400_regmap_config`, and calls `bma400_probe()`. The file declares I2C ID and OF compatible tables for `bosch,bma400`.

## Control Flow

Probe fails early if regmap creation fails. Otherwise all chip validation, regulator setup, event support, trigger setup, and IIO registration are performed by the common core.

## State and Persistence Behavior

The wrapper stores no private state. It forwards the name from the I2C ID to the core for `indio_dev->name`.

## Dependencies and Integration Points

It depends on I2C, regmap, module tables, and the `IIO_BMA400` namespace. The file comments document I2C address selection by SDO.

## Risks

`i2c_client_get_device_id()` assumes ID-table backed binding; OF-only binding behavior should be verified because the returned ID name is used. Regmap error reporting uses `dev_err()` plus raw `PTR_ERR()` rather than `dev_err_probe()`.

## Test Signals

Validation includes OF/I2C binding, regmap initialization, name propagation, common-probe chip ID validation, IRQ/no-IRQ operation, and sysfs/buffer/event behavior inherited from the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_spi.c

## Purpose

`bma400_spi.c` is the SPI transport wrapper for the BMA400 core. It implements the BMA400-specific SPI read quirk where the first returned byte is dummy data, then delegates to `bma400_probe()`.

## Important APIs, Types, and Functions

`bma400_regmap_spi_read()` uses `spi_write_then_read()` to read one extra byte and copies `result + 1` into the caller buffer. It restricts raw reads to two bytes with `BMA400_MAX_SPI_READ`. `bma400_regmap_spi_write()` calls `spi_write()`. `bma400_regmap_bus` supplies these callbacks and read flag bit 7. `bma400_spi_probe()` creates a custom regmap, performs an initial chip-ID read to discard potential garbage, then calls the common core.

## Control Flow

SPI probe obtains the SPI ID name, creates the custom regmap with device context, optionally logs failure to read the first chip ID, and calls `bma400_probe()`. The common core reads chip ID again after the dummy-read workaround.

## State and Persistence Behavior

No wrapper-private state persists beyond regmap. The initial chip-ID read is intentionally a bus synchronization side effect and does not configure the device.

## Dependencies and Integration Points

It depends on SPI, custom regmap bus callbacks, module tables, and the `IIO_BMA400` namespace. OF and SPI ID matching support `bosch,bma400` and `bma400`.

## Risks

The custom read path rejects reads larger than two bytes, so any future core bulk read over SPI that exceeds two bytes would fail. This is safe for current common-core uses but constrains expansion. The first chip-ID read logs an error but continues to common probe, which is reasonable for the dummy-read workaround but can duplicate failure noise.

## Test Signals

Tests should verify the dummy-byte discard, two-byte read limit, write path, first-read workaround, common probe chip ID validation, and all inherited IIO direct/buffer/event behavior over SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/accel/bma400_spi.c -->
