# subset-b-003896 research

Grouped research for Linux IIO light and UV sensor drivers under `sources/distributed-fs/ceph-client/drivers/iio/light`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/rohm-bu27034.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/rohm-bu27034.c

## Purpose
`rohm-bu27034.c` is an I2C IIO driver for the ROHM BU27034ANUC ambient light sensor. It exposes a processed illuminance channel plus two raw visible-band intensity channels and supports direct reads and software-buffered sampling.

## Important APIs, types, and functions
- `struct bu27034_data` stores the regmap, device pointer, serialization mutex, `struct iio_gts` gain/time-scale helper, optional buffer kthread, raw sample storage, and naturally aligned scan payload.
- `bu27034_channels` defines one `IIO_LIGHT` channel, two indexed `IIO_INTENSITY` channels, and a timestamp. `bu27034_scan_masks` permits buffered raw-pair scans and raw-pair-plus-lux scans.
- The IIO GTS tables `bu27034_gains` and `bu27034_itimes` model hardware gain and integration-time multipliers. `bu27034_get_scale()`, `bu27034_set_scale()`, and `bu27034_try_set_int_time()` keep scale, gain, and integration time coherent across both raw channels.
- `bu27034_calc_mlux()` implements the vendor lux formula using fixed-point helpers that avoid overflow in mixed gain/time cases.
- `bu27034_read_raw()`, `bu27034_write_raw()`, and `bu27034_read_avail()` implement the IIO direct-mode ABI.
- `bu27034_buffer_enable()`, `bu27034_buffer_thread()`, and `bu27034_buffer_disable()` implement software-buffered polling because the device has no data-ready interrupt.
- `bu27034_probe()` creates the regmap, enables `vdd`, validates the part ID, initializes IIO GTS, resets the chip, sets up the kfifo buffer, and registers the IIO device.

## Control flow
Probe initializes an RBTREE-cached regmap with volatile data/status ranges and read-only data/manufacturer registers, enables the regulator, reads `SYSTEM_CONTROL`, warns on unexpected part IDs, initializes the gain/time-scale model, resets the sensor, and registers direct plus software-buffer modes.

Direct raw intensity reads claim direct mode, lock the driver mutex, enable measurement, sleep for the active integration time, poll the `VALID` bit, and read the requested 16-bit channel. Direct lux reads enable measurement, wait for a valid two-channel sample, compute milli-lux from both raw channels, and then disables measurement. Scale and integration-time writes are refused while buffering through `iio_device_claim_direct()`.

Buffered mode enables measurement under the same mutex and starts a kernel thread. The thread sleeps until slightly before the expected conversion completion, polls the `VALID` bit, bulk-reads both raw channels, computes lux when requested by the active scan mask, and pushes the scan with an IIO timestamp. Predisable stops the thread before disabling measurements.

## State and persistence
Persistent external state is the chip register map: gain selectors, integration-time selector, measurement enable, and data/status bits. The driver keeps no nonvolatile settings. The regmap caches configuration registers but treats status and data as volatile. The mutex protects measurement enable, scale/time changes, and buffered/direct read exclusion. Reading `MODE_CONTROL4` clears the `VALID` bit, so validity checks are state-changing.

## Dependencies and integration points
The driver integrates with the I2C core, device properties, regulator framework, regmap, IIO core, IIO GTS helper namespace, kfifo software buffers, and kernel kthreads. Device-tree matching uses `rohm,bu27034anuc`; the module imports `IIO_GTS_HELPER`.

## Risks
- Scale changes can require changing integration time and compensating the other channel's gain. Regressions here can silently alter reported units.
- `VALID` reads clear data readiness, so extra status reads or debug paths can consume samples.
- The buffer thread uses sleep-plus-poll timing and can miss samples under scheduler delay; the code accepts that tradeoff.
- `bu27034_get_mlux()` returns before disabling measurement if data acquisition or lux calculation fails, leaving measurement enabled on some error paths.
- Fixed-point lux math has several overflow-avoidance branches; boundary tests are needed for max raw values and high gain ratios.
- Probe only warns on unknown part ID, so compatible-but-incorrect devices may still bind.

## Test signals
- Build with `CONFIG_ROHM_BU27034` and `CONFIG_IIO_GTS_HELPER` coverage.
- Direct-read tests should cover raw channels, lux computation, invalid channel masks, `-EBUSY` while buffering, and scale/int-time writes.
- Conversion tests should exercise all supported gains, all four integration times, ratio branch at `D1/D0 == 1.5`, zero raw values, and saturation-adjacent values.
- Buffer tests should verify scan mask layout, timestamp alignment, kthread start/stop, measurement disable on buffer teardown, and no direct-mode access while active.
- Hardware tests should confirm regulator handling, reset/cache reinit, and `VALID` polling behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/rohm-bu27034.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/rpr0521.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/rpr0521.c

## Purpose
`rpr0521.c` is an I2C IIO driver for the ROHM RPR-0521 ambient light and proximity sensor. It exposes one proximity channel and two intensity channels, supports scale, sampling-frequency, and proximity-offset controls, and optionally provides an IRQ-backed triggered buffer.

## Important APIs, types, and functions
- `struct rpr0521_data` holds the I2C client, regmap, state mutex, ALS/PXS enable flags, runtime-PM handoff flags, trigger pointer, IRQ timestamp, and aligned scan buffer.
- `rpr0521_channels` exposes proximity, ALS both-light, and ALS IR data. `rpr0521_available_scan_masks` enables all three channels together for buffered operation.
- `rpr0521_set_power_state()` coordinates runtime PM with channel enable/disable requests and keeps ALS/PXS state flags synchronized.
- `rpr0521_read_info_raw()`, `rpr0521_get_gain()`, `rpr0521_set_gain()`, `rpr0521_read_samp_freq()`, `rpr0521_write_samp_freq_common()`, and proximity-offset helpers implement the IIO direct ABI.
- `rpr0521_drdy_irq_handler()`, `rpr0521_drdy_irq_thread()`, `rpr0521_pxs_drdy_set_state()`, and `rpr0521_trigger_consumer_handler()` implement the physical interrupt to IIO trigger to buffer pipeline.
- Runtime PM hooks `rpr0521_runtime_suspend()` and `rpr0521_runtime_resume()` power off the chip, mark the regcache dirty, sync it, and re-enable requested channels.

## Control flow
Probe allocates the IIO device and regmap, initializes the mutex, validates manufacturer ID `0xe0`, sets the default 100 ms ALS/PXS measurement time, initializes runtime PM with autosuspend, and conditionally creates an IIO trigger and triggered buffer when an IRQ is supplied. The IIO device is then registered.

Direct reads claim direct mode, lock the driver, resume/power the needed ALS or PXS block, read the little-endian data register, and balance the runtime-PM reference. Scale writes update gain bitfields in `ALS_CTRL` or `PXS_CTRL`; sampling-frequency writes program one of the limited supported common ALS/PXS measurement-time modes; offset writes program the 10-bit proximity offset.

When buffering is enabled, preenable powers both ALS and PXS. Trigger enable programs proximity persistence for data-ready behavior and enables PS interrupt triggering. The top-half stores a timestamp and wakes the threaded handler, which confirms the interrupt status belongs to this chip and polls the IIO trigger. The consumer bulk-reads proximity, both ALS channels, and one extra byte that clears the interrupt, then pushes the scan.

## State and persistence
The driver mirrors sensor enable state in `als_dev_en` and `pxs_dev_en`; runtime-PM transition flags represent deferred enable/disable work across autosuspend. Register settings persist in the chip until reset or power loss. Regmap caches nonvolatile mode/control registers and treats most other registers as volatile. The scan buffer includes an intentional padding byte because the interrupt-clear read fetches seven bytes.

## Dependencies and integration points
The driver uses I2C, regmap, IIO direct mode, IIO triggers, triggered buffers, runtime PM, ACPI ID `RPR0521`, and optional physical IRQ wiring. Userspace sees standard IIO raw, scale, sampling-frequency, and offset attributes.

## Risks
- Runtime-PM reference balancing depends on paired `rpr0521_set_power_state()` calls; error exits in read paths are important.
- `rpr0521_poweroff()` reads the interrupt register to reset the pin state and may have side effects on status.
- The buffer path always enables both ALS and PXS even if users requested a subset.
- Sampling-frequency availability advertises only 2.5 and 10 Hz despite a larger hardware table; unsupported combinations are intentionally hidden.
- Some PM state flags are written before runtime-PM calls complete, so failures can leave driver mirrors requiring careful recovery.
- Buffered reads depend on a physical IRQ; without an IRQ the driver is direct-mode only.

## Test signals
- Compile with and without `CONFIG_PM` and with IIO triggered-buffer support.
- Probe tests should cover manufacturer-ID mismatch, missing IRQ, and IRQ-backed trigger registration.
- Direct-mode tests should validate gain tables, offset masking to 10 bits, common sampling-frequency writes, and balanced autosuspend on read failures.
- Buffer tests should check interrupt enable/disable register writes, timestamp source selection, scan layout, and interrupt-clear behavior.
- Runtime-PM tests should verify regcache dirty/sync, channel re-enable after resume, and full poweroff on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/rpr0521.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/si1133.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/si1133.c

## Purpose
`si1133.c` is an I2C IIO driver for the Silicon Labs SI1133 ambient light and UV index sensor. It exposes processed lux, raw white/IR/UV ADC mux channels, and shared scale, integration-time, and hardware-gain controls.

## Important APIs, types, and functions
- `struct si1133_data` stores the regmap, client, command mutex, response sequence counter, active channel-list mask, ADC sensitivity/config caches for six ADC slots, and a completion used by forced measurements.
- `si1133_command()` serializes command execution, handles response-sequence tracking, waits for IRQ completion for `SI1133_CMD_FORCE`, parses command errors, and resets the command counter after errors.
- `si1133_param_set()` and `si1133_param_query()` access the device's parameter RAM through `HOSTIN0`, `COMMAND`, and `RESPONSE1`.
- `si1133_measure()` configures ADC0 for the requested mux, sets channel list to ADC0, forces a measurement, and reads a signed 24-bit result.
- `si1133_get_lux()` enables a three-channel lux configuration, reads nine bytes from host outputs, and applies Silicon Labs polynomial coefficients to compute lux.
- `si1133_read_raw()` and `si1133_write_raw()` implement processed lux, raw intensity/UV, shared scale, integration time, and high-signal gain controls.
- `si1133_initialize()` resets the chip, disables autonomous mode, initializes the lux ADC channels, and enables IRQs for channel completion.

## Control flow
Probe allocates the IIO device, initializes the completion and regmap, validates part/revision/manufacturer registers, resets and configures the chip, requires a client IRQ, installs a shared threaded IRQ, and registers the IIO device. The interrupt handler reads `IRQ_STATUS`, verifies it matches the current scan mask, and completes the pending command waiter.

Direct raw reads use a command sequence rather than free-running sampling. For single-channel raw reads, ADC0 is retargeted to the requested mux and the channel list is reduced to bit 0. For processed lux, channels 1, 2, and 3 are programmed with fixed mux, postshift, sensitivity, and measurement-count settings; the driver forces a conversion and computes a lux value from high-visible, low-visible, and IR readings. Writes update ADC0 sensitivity/configuration parameters.

## State and persistence
The device parameter RAM contains the active ADC channel list, ADC muxes, post-processing, sensitivity, scale, and gain state. The driver mirrors ADC0 sensitivity and all configured ADC configs in arrays. `rsp_seq` tracks command-counter progress and is reset after explicit counter resets or command errors. `scan_mask` avoids unnecessary channel-list writes. The driver requires interrupts because forced measurement completion is represented as a completion signaled by the threaded IRQ.

## Dependencies and integration points
The driver depends on I2C, regmap access tables, IRQ delivery, completions, IIO core/sysfs helpers, unaligned 24-bit big-endian reads, and Silicon Labs command/parameter protocols. It exports direct-mode IIO channels only; there is no buffered path.

## Risks
- Missing or misconfigured IRQ makes the driver refuse probe, and forced commands time out if the interrupt status does not match `scan_mask`.
- `si1133_set_integration_time()` updates `data->adc_sens[adc]` but writes `ADCSENS(0)`, which is correct for the current ABI using ADC0 but fragile if extended.
- `find_closest()` in scale conversion chooses the nearest supported scale rather than requiring an exact string match.
- Lux polynomial math uses signed 24-bit values and fixed shifts; overflow and sign-extension boundaries need attention.
- Command sequencing is global and serialized. Any path that bypasses `si1133_command()` could desynchronize `rsp_seq`.
- `IRQ_STATUS` is marked precious in regmap, so careless extra reads can consume completion state.

## Test signals
- Probe tests should cover part-ID mismatch, IRQ absence, command reset timeout, and command-error parsing.
- Direct-read tests should verify all mux channels, lux branch selection above and below the ADC threshold, and signed 24-bit negative values.
- Sysfs tests should cover the advertised integration times, scale values, hardware-gain 0/1 validation, and invalid writes.
- IRQ tests should validate completion timeout behavior, shared IRQ `IRQ_NONE` return when status does not match, and recovery after command-counter reset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/si1133.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/si1145.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/si1145.c

## Purpose
`si1145.c` supports Silicon Labs SI1132 and SI1141/2/3/5/6/7 ambient light, IR, proximity, UV, temperature, and voltage sensors. It provides direct forced measurements, configurable gain/sample frequency, LED current outputs for proximity emitters, and optional IRQ-triggered buffered sampling.

## Important APIs, types, and functions
- `struct si1145_part_info` describes each supported part: expected part ID, IIO info table, channel array, LED count, and measurement-rate encoding.
- `struct si1145_data` stores client state, high-level and command locks, response sequence state, selected part info, active scan mask, autonomous-mode flag, trigger pointer, current measurement-rate register value, and scan buffer.
- `si1145_command()` serializes device commands and polls the response counter, handling invalid settings, overflow, unexpected counters, and command-counter reset.
- `si1145_param_set()` and `si1145_param_query()` access parameter RAM.
- `si1145_measure()` programs `CHLIST`, issues ALS or proximity force commands, and reads a 16-bit result.
- `si1145_read_raw()` and `si1145_write_raw()` implement raw reads, scale/offset/sample-frequency controls, and output LED current writes.
- `si1145_trigger_set_state()`, `si1145_buffer_preenable()`, and `si1145_trigger_handler()` implement autonomous measurement and buffered scans.

## Control flow
Probe selects the part table from the I2C ID, validates the hardware part ID, initializes locks, resets the chip, writes the hardware key, disables autonomous mode, initializes default sample frequency, LED currents, proximity and ALS ADC settings, and UV coefficients where applicable. It then sets up an IIO triggered buffer. If an IRQ exists, it creates and registers a trigger backed by the physical interrupt; otherwise buffered operation can still use polling/external trigger behavior.

Direct reads claim direct mode, program the channel list for the requested channel, force a measurement, tolerate conversion overflow as still producing a readable value, and read the channel register. Buffered preenable programs the channel list for the active scan mask. Trigger enable switches to autonomous PS/ALS mode, enables interrupts, writes the stored measurement rate, and starts automatic conversions. Trigger disable pauses automatic mode, clears measurement rate and interrupt enables, and marks autonomous false.

## State and persistence
Most configuration lives in device registers/parameter RAM and persists until reset. The driver mirrors `meas_rate`, `scan_mask`, and `autonomous` state. Sample-frequency writes update private state immediately and hardware only when autonomous mode is active. The response sequence counter is reset on protocol errors. Channel arrays encode per-part capability and LED output count.

## Dependencies and integration points
This driver uses raw I2C SMBus operations, IIO direct mode, IIO triggers, triggered buffers, sysfs constant attributes, optional IRQ wiring, and per-device I2C IDs. It integrates with several IIO channel types: intensity, proximity, temperature, voltage, UV index, and output current.

## Risks
- The part matrix is broad; channel arrays, LED count, and UV availability must match the actual chip ID.
- The command-counter protocol is sensitive to missed responses; after errors the next command must reset the counter.
- Direct and buffered paths both reprogram `CHLIST`; lock coverage is essential around autonomous mode.
- Only one AUX-backed channel can be buffered at a time; scan-mask validation enforces this.
- Sample-frequency conversion uses compressed or uncompressed measurement-rate encoding depending on part.
- Lux/UV/temperature offsets are hard-coded from datasheet assumptions and may need board-specific calibration outside this driver.

## Test signals
- Build and probe tests for each I2C ID should verify part-ID rejection and channel/LED exposure.
- Command tests should cover invalid-setting, overflow, timeout, and unexpected response counters.
- IIO tests should cover raw reads for ALS, IR, proximity, temp, voltage, UV, LED current writes, offset reads, and scale writes.
- Buffer tests should validate AUX scan-mask rejection, autonomous start/stop register writes, IRQ trigger registration, and no-IRQ polling mode.
- PM-like behavior should be checked indirectly by ensuring measurement rate and interrupts are zero when trigger is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/si1145.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25.h -->
# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25.h

## Purpose
`st_uvis25.h` is the shared private header for the STMicroelectronics UVIS25 ultraviolet sensor driver. It defines the common state object and exported core entry points used by both I2C and SPI bus glue.

## Important APIs, types, and functions
- `ST_UVIS25_DEV_NAME` defines the common IIO/device ID string `uvis25`.
- `struct st_uvis25_hw` carries the common core state: regmap, optional IIO trigger, enabled flag, and bus-provided IRQ number.
- `st_uvis25_probe(struct device *dev, int irq, struct regmap *regmap)` is the common probe function exported by the core and called by bus drivers after creating a regmap.
- `st_uvis25_pm_ops` is the exported sleep-PM operation table used by both bus drivers.

## Control flow
The header has no executable control flow. It establishes the contract that bus front-ends supply transport-specific regmap access and IRQ metadata, while `st_uvis25_core.c` owns identification, sensor initialization, IIO registration, triggered buffering, and PM.

## State and persistence
The only persistent state described here is the in-memory `st_uvis25_hw` structure. The `enabled` flag is a runtime mirror used by suspend/resume to restore the output data-rate enable bit when the device was active before suspend.

## Dependencies and integration points
The header depends on the IIO core type declarations and forward usage of `struct regmap` and `struct iio_trigger`. It is included by `st_uvis25_core.c`, `st_uvis25_i2c.c`, and `st_uvis25_spi.c`, forming the core/bus split.

## Risks
- Any fields added to `struct st_uvis25_hw` affect all bus implementations.
- The exported namespace must stay aligned with `MODULE_IMPORT_NS("IIO_UVIS25")` in the bus modules.
- The header does not include `linux/regmap.h`, relying on pointer-only use or other includes; adding inline accessors would require include updates.

## Test signals
- Build all three UVIS25 files together and as modules to catch namespace/export drift.
- Verify both I2C and SPI probes can pass their regmap and IRQ into the same `st_uvis25_probe()` contract.
- Suspend/resume tests should confirm `enabled` semantics are shared across transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_core.c

## Purpose
`st_uvis25_core.c` is the common IIO implementation for the ST UVIS25 UV index sensor. It validates device identity, exposes a processed UV index channel, supports one-shot direct reads, optional IRQ-triggered buffering, and sleep PM.

## Important APIs, types, and functions
- `st_uvis25_channels` defines one `IIO_UVINDEX` processed channel backed by the output register and a soft timestamp.
- `st_uvis25_check_whoami()` validates register `0x0f` against expected value `0xca`.
- `st_uvis25_set_enable()` toggles the ODR enable bit in `CTRL1` and mirrors it in `hw->enabled`.
- `st_uvis25_read_oneshot()` enables the device, waits 1.5 seconds, disables it, then reads the output register.
- `st_uvis25_read_raw()` claims direct mode and masks the IRQ line around one-shot reads to avoid stale data-ready interrupts.
- `st_uvis25_allocate_trigger()` configures interrupt polarity from `irq_get_trigger_type()`, requests the IRQ, allocates an IIO trigger, and registers it.
- `st_uvis25_buffer_preenable()`, `st_uvis25_buffer_postdisable()`, and `st_uvis25_buffer_handler_thread()` implement triggered buffered acquisition.
- `st_uvis25_probe()` is exported to bus drivers and performs common allocation, WHOAMI, boot/BDU initialization, optional buffer/trigger setup, and IIO registration.

## Control flow
Bus glue creates a regmap and calls `st_uvis25_probe()`. The core allocates an IIO device, stores it as driver data, fills `struct st_uvis25_hw`, checks WHOAMI, initializes IIO metadata, boots the sensor through `CTRL2`, waits two seconds, enables block-data-update, and, if an IRQ is present, sets up a triggered buffer and a trigger. Finally it registers the IIO device.

Direct reads disable the IRQ line when present, enable the sensor, wait for a conversion, disable the sensor, and read the UV output. IRQ-triggered operation leaves the sensor enabled while the buffer is active; the IRQ thread checks the status data-available bit and polls the trigger, and the buffer handler reads the one-byte UV output into an aligned scan structure.

## State and persistence
The `enabled` flag mirrors whether the sensor should be re-enabled after resume. Hardware configuration includes ODR enable, BDU, boot, and interrupt polarity. The driver does not persist calibration or thresholds. Suspend clears ODR unconditionally; resume restores ODR only if `hw->enabled` was true.

## Dependencies and integration points
The core uses regmap, IIO direct mode, IIO triggers, triggered buffers, IRQ trigger-type metadata, sleep PM, and the exported `IIO_UVIS25` namespace. It is transport-agnostic and relies on I2C/SPI glue for register access flags.

## Risks
- One-shot reads sleep for 1.5 seconds and block the IIO read path.
- IRQ masking around direct reads is required because the data-ready line cannot be disabled in the sensor map; removing it can leave a stuck active interrupt.
- `st_uvis25_allocate_trigger()` rejects unsupported IRQ trigger types, so firmware IRQ flags must be correct.
- The trigger stores `iio_dev` as drvdata but the IRQ request passes `hw`; both conventions must remain consistent with handlers.
- Resume only restores ODR, not a full sensor reinitialization; register retention assumptions matter.

## Test signals
- Probe tests should cover WHOAMI mismatch, boot/BDU write failures, no-IRQ direct-only mode, and unsupported IRQ polarity.
- Direct-read tests should verify `-EBUSY` while buffered, IRQ disable/enable balance, conversion delay behavior, and processed value format.
- Buffer tests should validate status-bit filtering, scan timestamp alignment, enable/disable hooks, and trigger notification completion.
- Suspend/resume tests should cover active and inactive sensor states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_i2c.c

## Purpose
`st_uvis25_i2c.c` is the I2C transport wrapper for the ST UVIS25 driver. It creates an I2C regmap with the device's auto-increment flag and delegates all sensor logic to `st_uvis25_probe()`.

## Important APIs, types, and functions
- `st_uvis25_i2c_regmap_config` uses 8-bit registers and values and sets both read and write auto-increment masks to bit 7.
- `st_uvis25_i2c_probe()` initializes the regmap with `devm_regmap_init_i2c()` and calls `st_uvis25_probe(&client->dev, client->irq, regmap)`.
- I2C and OF match tables bind `uvis25` and `st,uvis25`.
- The I2C driver uses `pm_sleep_ptr(&st_uvis25_pm_ops)` and imports the `IIO_UVIS25` namespace.

## Control flow
The I2C core matches an ID or device-tree compatible string, invokes probe, and the wrapper creates a managed regmap. If regmap initialization fails, probe reports the transport error. Otherwise, control transfers to the shared core, which handles WHOAMI, IIO registration, optional IRQ setup, and PM behavior.

## State and persistence
The wrapper owns no runtime state beyond the managed regmap. Sensor state is in the common `struct st_uvis25_hw` allocated by the core. Register writes persist only in the device until reset or power loss.

## Dependencies and integration points
This file integrates the common UVIS25 core with the Linux I2C subsystem, OF matching, module I2C driver registration, regmap-I2C transport, and shared sleep PM callbacks.

## Risks
- Incorrect auto-increment flags would corrupt multi-byte operations if the core later expands beyond single-byte reads.
- The wrapper assumes `client->irq` accurately represents the data-ready line; invalid IRQ metadata is rejected or handled in the core.
- Namespace import/export must stay aligned with the core.

## Test signals
- I2C probe tests should cover regmap initialization failure and successful delegation to core probe.
- OF and I2C ID modalias tests should verify `st,uvis25` and `uvis25` binding.
- PM build tests should ensure `st_uvis25_pm_ops` remains exported and usable from the I2C module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_spi.c

## Purpose
`st_uvis25_spi.c` is the SPI transport wrapper for the ST UVIS25 driver. It configures SPI regmap read/write command flags and delegates shared sensor behavior to `st_uvis25_probe()`.

## Important APIs, types, and functions
- `st_uvis25_spi_regmap_config` uses 8-bit registers and values, sets the SPI read flag bit, and enables auto-increment for both reads and writes.
- `st_uvis25_spi_probe()` initializes the managed SPI regmap and calls the common core probe with `spi->irq`.
- SPI and OF match tables bind `uvis25` and `st,uvis25`.
- The SPI driver registers with `module_spi_driver()`, uses shared sleep PM ops, and imports `IIO_UVIS25`.

## Control flow
The SPI bus invokes probe after ID or OF matching. The wrapper creates a regmap over the SPI device. Failure is logged and returned; success hands the device, IRQ, and regmap to the common UVIS25 core. The core then performs all identity, initialization, IIO, buffer, trigger, and PM setup.

## State and persistence
The SPI wrapper has no private persistent state. Managed regmap lifetime follows the SPI device. Runtime sensor state is held by the core's `struct st_uvis25_hw`.

## Dependencies and integration points
This file integrates the shared core with the SPI subsystem, SPI regmap transport, OF matching, and sleep PM. It is parallel to the I2C wrapper but uses SPI-specific read and auto-increment command bits.

## Risks
- SPI read/write flag masks are transport-critical; mistakes can address the wrong registers.
- Any future multi-byte core reads depend on the auto-increment bit being correct.
- The wrapper relies on the core's namespace export and PM symbol staying stable.

## Test signals
- SPI probe tests should cover regmap init failure and successful core delegation.
- Device-tree binding tests should verify `st,uvis25` resolves to this module on SPI buses.
- Bus transaction tests should confirm read flag and auto-increment behavior against hardware or regmap mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/st_uvis25_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/stk3310.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/stk3310.c

## Purpose
`stk3310.c` is an I2C IIO driver for Sensortek STK3013/STK3310/STK3311/STK3335-family ambient light and proximity sensors. It exposes raw light and proximity readings, scale and integration-time controls, proximity threshold events, and an optional board-provided near-level property.

## Important APIs, types, and functions
- `struct stk3310_data` stores the client, mutex, ALS/PXS enabled mirrors, `proximity-near-level`, event timestamp, regmap, and regmap fields for state, gains, integration times, interrupt enable, and flags.
- `stk3310_channels` defines one `IIO_LIGHT` and one `IIO_PROXIMITY` channel; the proximity channel has rising/falling threshold events and an `nearlevel` ext-info attribute.
- `stk3310_regmap_init()` creates the cached regmap and allocates bitfield views with `devm_regmap_field_alloc()`.
- `stk3310_read_raw()` and `stk3310_write_raw()` implement raw, scale, and integration-time IIO operations.
- `stk3310_read_event()`, `stk3310_write_event()`, and event config helpers manage proximity threshold registers and interrupt enable.
- `stk3310_irq_handler()` timestamps interrupts and `stk3310_irq_event_handler()` reads near/far direction, pushes an IIO event, and clears the interrupt flag.
- Suspend/resume uses `stk3310_set_state()` to enter standby and restore previously enabled ALS/PXS blocks.

## Control flow
Probe reads the optional `proximity-near-level` device property, initializes the regmap fields, fills IIO metadata, verifies the chip ID against a known list but only logs unknown IDs, enables both ALS and PXS, enables proximity interrupts, requests a threaded IRQ if available, and registers the IIO device. On failure after enabling the device, it returns the chip to standby.

Runtime raw reads use big-endian two-byte reads from ALS or proximity data registers. Scale and integration-time reads decode regmap fields into static tables. Writes search the same tables for exact values and update the corresponding bitfield. Proximity threshold writes validate the threshold against the current proximity gain before writing big-endian threshold registers.

## State and persistence
The sensor state register controls ALS/PXS enable bits; the driver mirrors enabled channels for resume. Gain, integration time, interrupt mode, and threshold registers live in hardware and regmap cache. Data and flag registers are volatile. `ps_near_level` is a read-only property-derived runtime value exposed through ext-info.

## Dependencies and integration points
The driver uses I2C, regmap/regmap-field, IIO events, sysfs constant attributes, device properties, optional ACPI/OF/I2C matching, IRQs, and sleep PM. It has no buffered data path.

## Risks
- Unknown chip IDs are accepted after an informational log, which can bind to register-incompatible variants.
- Threshold maximum depends on current proximity gain; changing gain after thresholds can make previously valid thresholds semantically odd.
- Event config writes a raw field value from a boolean state, while the init path writes `STK3310_PSINT_EN`; this assumes the field encoding matches simple enabled states.
- IRQ direction is inferred from `FLAG_NF`; stale or uncleared flags can invert event meaning.
- Raw reads do not explicitly power up the device if userspace reads while suspended outside normal PM ordering.

## Test signals
- Build and probe tests for all ID table names and OF compatibles.
- Raw/attribute tests should cover both channels, all scale and integration-time table entries, invalid values, and nearlevel property exposure.
- Event tests should cover rising/falling threshold read/write, gain-dependent max validation, interrupt enable/disable, IRQ timestamping, direction mapping, and flag clearing.
- PM tests should verify standby on suspend/remove and restoration of the last enabled ALS/PXS state on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/stk3310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tcs3414.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tcs3414.c

## Purpose
`tcs3414.c` is an I2C IIO driver for TAOS TCS3414/TCS3413/TCS3415/TCS3416 and compatible TCS3404 color sensors. It exposes red, green, blue, and clear 16-bit intensity channels with shared scale and integration-time controls and supports triggered buffered reads.

## Important APIs, types, and functions
- `struct tcs3414_data` stores the I2C client plus cached `control`, `gain`, and `timing` bytes.
- `tcs3414_channels` defines four modified `IIO_INTENSITY` channels and a timestamp channel.
- `tcs3414_req_data()` powers/enables ADC conversion, polls `ADC_VALID`, disables ADC, and reports readiness errors.
- `tcs3414_read_raw()` implements one-shot raw reads plus cached scale and integration-time reads.
- `tcs3414_write_raw()` validates and writes gain scale or integration time into cached register mirrors.
- `tcs3414_trigger_handler()` reads active color channels into an aligned scan payload for the triggered buffer.
- `tcs3414_powerdown()` and managed cleanup disable power and ADC on remove or failed probe.

## Control flow
Probe allocates the IIO device, reads the ID register, accepts known TCS3404/TCS341x ID ranges, powers the sensor, registers a managed powerdown action, writes the default 12 ms timing, reads the initial gain register, sets up a triggered buffer, and registers the IIO device.

Direct raw reads claim direct mode, request fresh data by enabling the ADC and polling the valid bit up to roughly 500 ms, read the requested 16-bit word register, and release direct mode. Buffered mode enables the ADC in `postenable`, reads active channels in the trigger handler without its own freshness wait, and disables ADC in `predisable`.

## State and persistence
The driver mirrors control, gain, and timing register values in memory and writes them to hardware on changes. Suspend powers down by clearing power and ADC bits but keeps the cached control value; resume writes the cached control back. There is no calibration state beyond gain and integration time.

## Dependencies and integration points
The driver depends on I2C SMBus byte/word operations, IIO direct mode, IIO triggered buffers, sysfs constant attributes, and sleep PM. It does not use regmap or IRQ-specific events.

## Risks
- No mutex protects cached `control`, `gain`, and `timing`, so concurrent sysfs writes, direct reads, buffering, and PM transitions rely on IIO core serialization but are not locally synchronized.
- Buffered trigger reads do not call `tcs3414_req_data()`, so trigger cadence must be compatible with integration timing.
- Direct reads enable and disable ADC for each channel, making four-channel userspace polling inefficient.
- Endianness depends on SMBus word read behavior while scan type declares CPU endianness.
- The driver has TODOs for sync, interrupt support, thresholds, and prescaler.

## Test signals
- Probe tests should cover accepted/rejected ID nibbles and managed powerdown after errors.
- Direct-read tests should validate data-ready timeout, gain scale table, integration-time table, and direct/buffer exclusion.
- Buffer tests should verify ADC enable/disable hooks, channel ordering, timestamp alignment, and behavior at different trigger rates.
- PM tests should confirm powerdown on suspend and cached-control restore on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tcs3414.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tcs3472.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tcs3472.c

## Purpose
`tcs3472.c` is an I2C IIO driver for TAOS/AMS TCS34721/23/25/27 color light sensors. It exposes clear, red, green, and blue intensity channels, gain and integration-time controls, threshold events on the clear channel, and triggered buffered sampling.

## Important APIs, types, and functions
- `struct tcs3472_data` stores the client, mutex, cached low/high thresholds, enable register, gain control, integration time, and interrupt persistence.
- `tcs3472_channels` defines four color intensity channels; only the clear channel has event specs.
- `tcs3472_req_data()` polls the status register for `AVALID`.
- `tcs3472_read_raw()` and `tcs3472_write_raw()` implement raw reads, calibration scale, and integration time.
- `tcs3472_read_event()`, `tcs3472_write_event()`, and event config helpers manage threshold values, event period, and interrupt enable.
- `tcs3472_event_handler()` handles hardware threshold IRQs, pushes an IIO event, and clears the interrupt through the special-function command.
- `tcs3472_trigger_handler()` reads active channels into a triggered-buffer scan after data-valid polling.

## Control flow
Probe validates the ID register, reads current control, integration time, and threshold registers, initializes persistence to one cycle, enables power and ALS while disabling ALS interrupts, sets up a triggered buffer, optionally requests a threaded shared IRQ for threshold events, and registers the IIO device. Remove unregisters IIO, frees the IRQ, cleans up the buffer, and powers down.

Direct raw reads claim direct mode, wait for valid data, read the requested color word, and release direct mode. Gain writes update the cached control register and hardware gain bits. Integration-time writes search all 256 possible ATIME encodings for an exact microsecond value. Event period writes choose the first persistence cycle whose period is at least the requested duration based on current integration time.

## State and persistence
The driver mirrors mutable hardware state in `struct tcs3472_data` and protects it with `lock` for events and power transitions. Threshold and persistence writes update both hardware and cache. `enable` tracks power, ADC, and interrupt-enable bits and is reused for suspend/resume.

## Dependencies and integration points
The file integrates with I2C SMBus operations, IIO direct mode, IIO events, triggered buffers, optional IRQs, and sleep PM. It uses manual buffer setup/cleanup and manual IRQ free rather than devm for those resources.

## Risks
- Threshold writes accept `int val` but hardware registers are 16-bit; out-of-range values are not explicitly rejected before SMBus word writes.
- Event period computation depends on current integration time; changing ATIME after setting period changes real interrupt latency while `apers` remains the same.
- Manual cleanup paths must keep IRQ and buffer teardown ordering correct.
- Event IRQ clearing ignores the return value of the special-function read.
- Direct reads and buffer reads share the device; only direct reads claim direct mode, while trigger handler uses the buffer path.

## Test signals
- Probe tests should validate ID `0x44` and `0x4d`, rejected IDs, and cleanup on buffer/IRQ/register failures.
- IIO tests should cover raw color reads, all gain values, representative ATIME values, invalid writes, and integration-time available formatting.
- Event tests should cover threshold read/write, period rounding, event enable toggling, IRQ event emission, and interrupt clear.
- PM tests should confirm power/ADC bits are cleared on suspend/remove and restored on resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tcs3472.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2563.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tsl2563.c

## Purpose
`tsl2563.c` is an I2C IIO driver for AMS/TAOS TSL2560/1/2/3 light sensors. It exposes processed lux, raw broadband and IR intensity channels, calibration scale controls, automatic gain/integration adjustment, and optional threshold events.

## Important APIs, types, and functions
- `struct tsl2563_chip` stores the mutex, client, delayed poweroff work, suspend flag, current gain-level table pointer, thresholds, interrupt register state, calibration coefficients, cover compensation, and cached ADC readings.
- `tsl2563_gainlevel_table` defines automatic gain/time ranges and normalized gain-time encodings.
- `tsl2563_get_adc()` powers/configures the chip when needed, reads both ADC channels, adjusts gain level based on broadband limits, normalizes readings to 400 ms/16x scale, caches values, and schedules delayed poweroff when interrupts are disabled.
- `tsl2563_adc_to_lux()` converts calibrated broadband/IR readings to lux using ratio-based coefficients.
- `tsl2563_read_raw()` and `tsl2563_write_raw()` implement processed/raw/calibration IIO access.
- Event helpers manage high/low thresholds and interrupt enable. `tsl2563_event_handler()` pushes threshold events and clears the hardware interrupt.
- PM hooks power off on suspend and reconfigure on resume.

## Control flow
Probe powers the chip enough to detect it, reads the ID, initializes defaults for thresholds, gain level, interrupt persistence, calibration, and optional `amstaos,cover-comp-gain`, requests an IRQ if present, writes timing/threshold configuration, starts delayed poweroff work, and registers the IIO device. If no IRQ exists, the IIO info table omits event callbacks.

Reads lock the chip. For lux and raw intensity, `tsl2563_get_adc()` returns cached values while suspended, otherwise ensures the device is powered, waits for integration as needed, reads both channels, possibly steps gain/time and retries, then normalizes ADC values. Processed lux applies per-channel calibration and cover compensation before lux conversion. Event enable powers and configures the chip, enables level interrupts, and prevents delayed poweroff while interrupts are active.

## State and persistence
Thresholds, interrupt persistence, calibration coefficients, gain-level pointer, cover compensation, and last ADC values are kept in memory. Timing and threshold hardware registers are programmed from this state. A delayed work item powers off the chip five seconds after reads when events are disabled. During suspend, the driver returns cached ADC data rather than doing I2C reads.

## Dependencies and integration points
The driver uses I2C SMBus, IIO direct mode and events, delayed work, device properties, IRQ trigger-type discovery, and sleep PM. Device-tree compatibles cover `amstaos,tsl2560` through `amstaos,tsl2563`.

## Risks
- `tsl2563_adjust_gainlevel()` increments/decrements a pointer within the gain-level table; boundary correctness depends on table min/max choices and ADC values.
- Lux conversion subtracts `ch1 * coeff` from `ch0 * coeff` using unsigned arithmetic; coefficient table ordering must prevent underflow effects for supported ratios.
- Reads while suspended return cached data, which may surprise users expecting a fresh sample.
- Calibration writes update only memory, not hardware, and accept any integer converted to fixed point.
- Delayed poweroff, event enable, remove, and suspend all manipulate power state and must remain synchronized.

## Test signals
- Probe tests should cover power detect, ID read logging, IRQ/no-IRQ info selection, and cover-comp-gain property parsing.
- Read tests should cover automatic gain-level stepping, normalized ADC values, lux ratio table boundaries, cached suspended reads, and delayed poweroff scheduling.
- Event tests should cover threshold read/write, interrupt enable/disable, IRQ clear, persistence defaults, and power retention while events are active.
- PM/remove tests should verify delayed work cancellation and final poweroff.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2563.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2583.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tsl2583.c

## Purpose
`tsl2583.c` is an I2C IIO driver for TAOS TSL2580/TSL2581/TSL2583 ambient light sensors. It exposes raw IR and broadband channels, processed lux, calibration bias/scale, integration-time controls, calibration target, manual calibration, and a configurable lux coefficient table.

## Important APIs, types, and functions
- `struct tsl2583_chip` stores the client, ALS mutex, current raw/lux readings, mutable ALS settings, integration time scale, and saturation threshold.
- `struct tsl2583_settings` contains ALS integration time, gain index, gain trim, calibration target, and a lux coefficient table with up to ten segments plus terminator.
- `tsl2583_defaults()` initializes operational defaults and the built-in lux table.
- `tsl2583_get_lux()` reads status/data registers, clears the ALS interrupt status bit, updates raw channel caches, handles saturation/darkness, selects a coefficient segment by channel ratio, and computes lux with time/gain trim.
- `tsl2583_als_calibrate()` derives `als_gain_trim` from a known target lux value.
- `tsl2583_set_als_time()`, `tsl2583_set_als_gain()`, and `tsl2583_chip_init_and_power_on()` program integration time, gain, interrupt-disable, and ADC enable.
- `tsl2583_read_raw()` and `tsl2583_write_raw()` wrap all IIO operations with runtime-PM get/put and the ALS mutex.

## Control flow
Probe verifies SMBus byte-data support, validates the chip ID high nibble, fills IIO metadata, enables runtime PM with autosuspend, registers the IIO device, and loads in-memory defaults. Runtime resume powers on, disables interrupts, programs integration time and gain, waits briefly, and enables ADC. Runtime suspend powers off. Reads and writes resume the device, perform the requested operation under `als_mutex`, and autosuspend afterward.

Processed lux and raw channel reads both call `tsl2583_get_lux()`, so raw reads also refresh and compute lux. If data is not marked valid, the function logs and returns the last cached lux. The lux-table sysfs store parses comma/space separated integer triples using `get_options()` and requires a final all-zero terminator.

## State and persistence
Most user-visible settings are in driver memory: gain trim, calibration target, lux coefficient table, chosen gain index, and requested integration time. Integration time, gain, interrupt disable, power, and ADC enable are programmed into hardware during runtime resume or writes. Runtime PM autosuspends after two seconds. `als_cur_info` caches the last raw and lux values.

## Dependencies and integration points
The driver uses I2C SMBus byte access, runtime PM, IIO direct mode, custom IIO device attributes, `get_options()` parsing, and OF/I2C matches for the TSL258x family. It does not implement hardware events or buffers.

## Risks
- Probe registers the IIO device before loading defaults; very early reads could see zeroed settings if userspace races registration.
- `tsl2583_get_lux()` treats invalid data as a successful return of the last lux value, which can hide freshness failures.
- The lux table parser accepts integers into a local array and bulk-copies them into typed structs; malformed but shape-valid tables can produce bad lux results.
- Runtime-PM get/put errors can mask otherwise valid read results, and write paths power the device even for purely in-memory settings.
- Calibration requires the device already powered, ADC enabled, and data valid; failures are common if invoked at the wrong time.

## Test signals
- Probe tests should cover SMBus functionality absence, chip-ID mismatch, runtime-PM initialization, and defaults availability after registration.
- Read tests should cover valid data, invalid-data cached return, saturation, zero broadband, ratio table termination, and gain/time trim math.
- Sysfs tests should cover integration-time bounds/multiples, calibscale values, calib bias writes, target writes, calibration success/failure, and lux-table parser validation.
- Runtime-PM tests should verify resume programming sequence, autosuspend poweroff, remove poweroff, and error handling on PM get/put.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2583.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2591.c -->
# sources/distributed-fs/ceph-client/drivers/iio/light/tsl2591.c

## Purpose
`tsl2591.c` is an I2C IIO driver for the TAOS/AMS TSL2591 high-sensitivity light-to-digital converter. It exposes raw IR and broadband channels, processed lux, shared integration-time and gain controls, runtime PM, and optional threshold events.

## Important APIs, types, and functions
- `struct tsl2591_als_settings` stores lower/upper thresholds, integration-time field, persistence field, and gain field.
- `struct tsl2591_chip` stores ALS settings, I2C client, ALS mutex, and event-enabled state.
- Conversion helpers map gain fields to multipliers, user integration times to register fields, and persistence cycles to literal counts.
- `tsl2591_wait_adc_complete()` sleeps for the integration time and polls `STATUS` for ALS-valid.
- `tsl2591_read_channel_data()` reads four ALS data bytes and returns raw channels or computes lux using integration time and gain.
- `tsl2591_set_als_gain_int_time()`, threshold setters, `tsl2591_set_als_persist_cycle()`, and `tsl2591_set_power_state()` program hardware from mirrored state.
- Raw/event IIO callbacks implement read/write, available lists, threshold values, event period, and event enable.
- `tsl2591_chip_off()` is a devm cleanup action that disables runtime PM and powers down the chip.

## Control flow
Probe checks SMBus byte-data functionality, allocates the IIO device, optionally requests an IRQ and selects the event-capable IIO info table, validates the device ID, initializes runtime PM with autosuspend, installs the managed chip-off action, loads default gain/time/threshold/persistence settings, clears any pending ALS interrupt, and registers the IIO device.

Reads resume the device, lock `als_mutex`, wait for ADC completion, bulk-read channel data, and return raw or processed values, then autosuspend. Writes update mirrored integration time or gain and program `CONTROL`. Event threshold writes adjust opposing thresholds when needed to maintain ordering. Enabling events pins runtime PM active and resume powers the device with ALS interrupt enable; disabling events drops the runtime-PM reference. The IRQ handler pushes an IIO threshold event and clears the ALS interrupt when events are enabled.

## State and persistence
The driver mirrors all mutable ALS settings in memory and writes them to hardware. Runtime PM powers the sensor on for reads and keeps it on while events are enabled. Threshold ordering is actively maintained by updating the opposite threshold if a new lower/upper value would cross it. `events_enabled` is the software gate for IRQ handling and PM retention.

## Dependencies and integration points
The driver depends on I2C SMBus byte/block access, runtime PM, IIO direct mode and events, OF matching, IRQs, `readx_poll_timeout()`, debug logging, and unaligned little-endian helpers. It has no buffered data path.

## Risks
- Lux calculation divides by broadband channel and counts-per-lux; zero channel 0 or very low integration/gain combinations can trigger divide faults or invalid results if not covered by hardware assumptions.
- `pm_runtime_get_sync()` return is ignored in `tsl2591_read_raw()`, so PM resume failures may lead to I2C access anyway.
- Event period conversion mixes seconds/microseconds and integration time; edge values need validation.
- Threshold setters update cached state before all I2C writes complete, so partial write failures can desynchronize cache and hardware.
- Event enable changes `events_enabled` before PM calls and does not propagate PM errors to userspace.

## Test signals
- Probe tests should cover SMBus capability failure, IRQ/no-IRQ info selection, device-ID mismatch, default programming, and managed cleanup.
- Read tests should cover raw IR/broadband, processed lux, all integration times and gain multipliers, ADC-valid timeout, and zero/saturation channel data.
- Event tests should cover threshold ordering adjustments, persistence period read/write, enable/disable PM reference behavior, IRQ ignored when disabled, and interrupt clear.
- Runtime-PM tests should verify autosuspend after reads and interrupt-enabled resume state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/light/tsl2591.c -->
