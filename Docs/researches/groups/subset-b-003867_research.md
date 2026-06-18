# subset-b-003867 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4170-4.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4170-4.c

## Purpose
`ad4170-4.c` is the SPI IIO driver for Analog Devices AD4170-4, AD4190-4, and AD4195-4 precision ADCs. It exposes voltage and internal temperature channels, direct single-shot reads, triggered buffers, optional GPIO-controller functionality, regulator/reference modeling, internal clock output registration, excitation-current setup for external sensors, and debugfs register access.

## Important APIs, types, and functions
The core state is `struct ad4170_state`, which holds the SPI/regmap handles, regulator-derived voltages, channel templates, setup-slot accounting, cached per-channel configuration, IRQ completion, buffer transfer state, clock provider state, pin-function bookkeeping, and optional `gpio_chip`. `struct ad4170_setup` mirrors one hardware setup slot: MISC, AFE, FILTER, FILTER_FS, OFFSET, and GAIN registers. `struct ad4170_chan_info` stores per-channel input range, cached setup, scale/offset tables, enable state, and assigned setup slot.

Register access is implemented through custom regmap callbacks, `ad4170_reg_read()` and `ad4170_reg_write()`, because register sizes vary and multibyte accesses use a two-byte instruction phase. `AD4170_ADC_CTRL_CONT_READ_EXIT_REG` is a virtual register used to send the continuous-read exit byte.

Setup sharing is managed by `ad4170_find_setup()`, `ad4170_write_setup()`, `ad4170_write_channel_setup()`, `ad4170_link_channel_setup()`, and `ad4170_set_channel_enable()`. IIO raw paths are `ad4170_read_raw()`, `ad4170_write_raw()`, `ad4170_read_avail()`, and `ad4170_update_scan_mode()`. The filter enum is exported as a per-channel ext_info attribute. GPIO support is implemented by `ad4170_gpio_*()` callbacks. Firmware parsing lives in `ad4170_parse_firmware()`, `ad4170_parse_channels()`, `ad4170_parse_channel_node()`, and helpers for references, ADC channel types, bridge/RTD/thermocouple excitation, vbias, clocks, and pin validation.

## Control flow
`ad4170_probe()` allocates the IIO device, initializes the mutex and custom regmap, enables and records regulators, performs a software reset, parses firmware, writes initial device configuration, initializes completion/IRQ/trigger when an IRQ is present, prepares an optimized SPI message for continuous reads, sets up the triggered buffer, and registers the IIO device.

Firmware parsing first selects clocking, writes `CLOCK_CTRL`, initializes current-source bookkeeping, maps the data-ready interrupt pin, applies optional `adi,vbias-pins`, parses channel child nodes, and optionally registers a GPIO controller. Each channel parse creates an IIO channel from a template, reads `reg`, sensor type, reference selection, channel inputs, polarity, and optional excitation settings, validates pin reuse, computes input range, and caches configuration. A temperature channel and timestamp channel are added when capacity allows.

Initial configuration fills sample-rate tables from `mclk_hz`, idles the ADC, writes setup defaults including default gain, writes channel maps, sets each channel to the default sample rate, fills scale/offset tables, disables all channels, and selects a shared data register. Direct reads claim direct mode, enable only the target channel, run single conversion mode, wait for IRQ completion or a computed settling timeout, read `DATA_24B`, sign-extend if needed, and disable the channel. Buffered reads enable scan-mask channels in sequential mode, enter continuous conversion plus continuous read, and the trigger handler reads one sample per active channel through the pre-optimized SPI message.

## State and persistence behavior
There is no disk persistence. Persistent runtime state is cached in `ad4170_state`: regulator voltages, clock mode, setup slot contents and use counts, per-channel setup, enabled-channel counts, scale/offset tables, current-source pin allocation, and GPIO/analog pin function masks. Hardware setup registers persist until reset or later writes. `st->lock` protects read-modify-write and multi-register configuration sequences, and direct-mode claims prevent concurrent buffered and direct conversion paths. The driver deliberately disables channels after single-shot and buffer disable operations to avoid stale sequencer state affecting later reads.

## Dependencies and integration points
The driver integrates with SPI, regmap, IIO direct mode, IIO triggered buffers, IIO triggers, GPIO controller, regulator consumer APIs, firmware node properties, and the common clock framework. Device tree properties drive channel definitions, references, bipolar mode, sensor type, excitation currents, vbias pins, GPIO-controller exposure, clock output, interrupt naming, and optional external clocks. It registers SPI and OF matches for `adi,ad4170-4`, `adi,ad4190-4`, and `adi,ad4195-4`.

## Risks and edge cases
Setup-slot sharing is complex: only eight hardware setups back up to sixteen channels, so bugs in unlinking, overwrite selection, or enabled-channel accounting can cause one channel's configuration to affect another. Pin-function bookkeeping must reject conflicts between analog input, vbias, current output, AC excitation, and GPIO export; missing validation could create invalid hardware drive configurations. The direct-read settling timeout is conservative but depends on `mclk_hz`; bad clock configuration can cause long waits or unstable reads. The continuous-read virtual register path is special and should be tested around buffer disable. In `ad4170_set_filter_type()`, the code clamps `setup->filter_fs` using `val` rather than the previous filter_fs value, which is suspicious because `val` is the filter enum, not a filter FS value. Negative regulator voltages are represented by negating positive regulator readings, which is explicitly a framework workaround and may misrepresent boards with unusual supplies.

## Test signals
Useful tests include probe with internal clock, external clock, and clock-output provider modes; regulator absence/defer/error paths; channel parsing for differential, pseudo-differential, temperature, weighscale, RTD, and thermocouple cases; invalid pin reuse and invalid reference selections; scale and sampling-frequency available lists; setup-slot reuse across more than eight channels; direct raw reads with and without IRQ; buffer enable/disable including continuous-read exit; scan masks where channel 0 is and is not included; GPIO valid-mask and direction/value operations; and debugfs register access for 1-, 2-, and 3-byte registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4170-4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4695.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4695.c

## Purpose
`ad4695.c` is the SPI IIO driver for AD4695, AD4696, AD4697, and AD4698 SAR ADCs. It supports direct single conversions, triggered buffered acquisition, optional SPI offload with DMA RX streaming, PWM-controlled CNV timing, voltage and temperature channels, per-channel input configuration, oversampling, calibration gain/offset, and register debug access.

## Important APIs, types, and functions
`struct ad4695_state` is the central state object. It owns the SPI device, optional `spi_offload`, offload trigger, 8-bit and 16-bit regmaps, reset/CNV GPIOs, optional CNV PWM, per-channel IIO specs, parsed `ad4695_channel_config`, reference/common-mode voltages, buffer SPI transfers, DMA buffer, conversion commands, raw data, and a small regmap bus scratch buffer. `struct ad4695_chip_info` captures chip name, max sample rate, acquisition time, and voltage input count. `struct ad4695_channel_config` stores high-Z, bipolar, pin pairing, common-mode voltage, and oversampling ratio.

The driver uses a custom `regmap_bus` (`ad4695_regmap_bus_reg_read()` / `ad4695_regmap_bus_reg_write()`) because the device has 16-bit register addresses over SPI and both 8-bit and 16-bit value spaces. `ad4695_set_single_cycle_mode()`, `ad4695_enter_advanced_sequencer_mode()`, and `ad4695_exit_conversion_mode()` control conversion state. `ad4695_buffer_preenable()` and `ad4695_trigger_handler()` handle normal triggered buffers. `ad4695_offload_buffer_postenable()` and `ad4695_offload_buffer_predisable()` implement the offload path. `ad4695_read_raw()`, `ad4695_write_raw()`, `ad4695_read_avail()`, and `ad4695_get_current_scan_type()` implement the IIO ABI.

## Control flow
`ad4695_probe()` allocates IIO state, loads match data, initializes sample-frequency ranges, creates both regmaps, requests optional CNV GPIO, enables supplies, chooses internal LDO or external VDD, chooses internal buffered reference or external REF, reads optional COM voltage, resets the chip through GPIO or software reset, enables address decrement/increment behavior needed by `regmap16`, configures LDO/reference bits, waits for the internal reference buffer if used, parses channel config, and then chooses either normal triggered-buffer setup or SPI offload setup.

Channel parsing first populates defaults for every voltage input, including high-Z enabled, OSR 1, raw/scale/calibration IIO attributes, scan index, and conversion command address. Child nodes override high-Z, bipolar mode, and common-mode pairing. Pairing may be REFGND, COM, or an even/odd differential pair; the even/odd case requires the common-mode channel to be the next odd channel and reads an `inN` regulator for the common-mode voltage. A temperature channel and timestamp channel are appended.

Direct raw reads claim direct mode, configure single-cycle conversion for the target channel, optionally pulse CNV GPIO, handle the temperature-channel extra conversion requirement, then send `EXIT_CNV_MODE` while receiving the conversion result. Normal buffers use advanced sequencer mode with slot 0 as an initial/discard conversion and one slot per enabled voltage channel; temperature is enabled through `TEMP_CTRL`. The trigger handler runs the optimized SPI message and pushes the DMA-aligned local buffer with timestamp. The offload path programs sequencer slots, requires at least two voltage channels, enables BUSY output, enables the SPI offload trigger, enters sequencer mode, and adjusts PWM duty cycle to meet CNV high time.

## State and persistence behavior
Runtime state is maintained in memory and chip registers. Channel configuration is mirrored in `channels_cfg`; OSR changes update both this cache and the hardware `CONFIG_IN` bits. Calibration gain and offset live in hardware registers and are read/written through `regmap16`. Sample frequency in offload mode is the PWM period divided by OSR; the driver reads hardware PWM state for reporting. `cnv_pwm_lock` serializes PWM changes between buffer enable/disable and sysfs writes. Direct-mode claims prevent register/configuration changes during active buffers.

## Dependencies and integration points
The driver depends on SPI, regmap, GPIO descriptors, regulators, PWM, IIO triggered buffers, IIO DMAENGINE buffers, SPI offload consumer/provider APIs, firmware child nodes, and dt-bindings constants from `adi,ad4695.h`. It imports the `IIO_DMAENGINE_BUFFER` namespace. It exposes OF and SPI IDs for AD4695/96/97/98 and adapts channel count and max sample/acquisition timing per chip.

## Risks and edge cases
Normal mode rejects a separate CNV GPIO because it currently assumes CNV is tied to SPI CS; offload mode requires CNV GPIO and PWM. The offload buffer path rejects fewer than two voltage channels, even if temperature is enabled, because it cannot discard sequencer data like the normal path. Exit-conversion sequencing is intentionally unusual because the command is only processed while reading a conversion; error unwinds must keep trigger disable before exit conversion to avoid spurious offload activity. `ad4695_read_raw()` initializes `cfg` only for voltage channels, so paths that reference it are carefully guarded by channel type. Calibration bias conversion depends on OSR-specific scaling and signed fractional handling, which needs boundary tests. Reference setup forbids disabling high-Z mode for the internal reference buffer.

## Test signals
Exercise probe with hardware reset and software reset, internal LDO and external VDD, internal buffered reference and external REF, optional COM supply, valid and invalid channel child nodes, even/odd pairing validation, bipolar rejection with REFGND, raw voltage and temperature reads, calibbias/calibscale read-write ranges, OSR read/write and scan type changes, PWM sample-frequency reads/writes, normal triggered buffer slot construction including temperature-only handling, SPI offload setup with too few channels, BUSY trigger pin selection, offload enable/disable unwind paths, and debugfs access across both 8-bit and 16-bit regmap ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4695.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4851.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4851.c

## Purpose
`ad4851.c` is an SPI IIO driver for the AD4851 through AD4858 and AD4858i data acquisition system ADC family. It does not locally stream samples through SPI; instead it configures the converter, controls the CNV PWM, and uses the IIO backend framework for data capture, channel enablement, data sizing, oversampling, and interface delay calibration.

## Important APIs, types, and functions
`struct ad4851_state` stores SPI, regmap, PWM CNV, IIO backend, mutex, chip info, optional power-down GPIO, reference-source flags, OSR, current conversion trigger rate, resolution-boost state, per-channel polarity, and cached scale lists. `struct ad4851_chip_info` describes product ID, max sample rate, resolution, max channel count, and the parser function used for 16-bit or 20-bit variants. `struct ad4851_scale` maps user-visible full-scale ranges to SOFTSPAN register values.

Key routines include `ad4851_setup()` for reset and device-control programming, `ad4851_set_sampling_freq()` for PWM period/duty configuration, `ad4851_set_oversampling_ratio()` for OSR register, backend OSR, backend data-size, packet format, resolution boost, and scale-cache updates, `ad4851_calibrate()` for backend I/O delay tuning with ADC test patterns, `ad4851_get/set_calibscale()`, `ad4851_get/set_calibbias()`, `ad4851_get/set_scale()`, `ad4851_parse_channels_common()`, and chip-specific `ad4857_parse_channels()` / `ad4858_parse_channels()`.

## Control flow
`ad4851_probe()` allocates IIO state, initializes the mutex, enables required supplies (`vcc`, `vdd`, `vee`, `vio`) and optional `vddh`, `vddl`, `vrefbuf`, and `vrefio`, gets optional `pd` GPIO and required PWM, loads chip info, initializes SPI regmap, sets an initial 1 MHz CNV trigger, registers PWM cleanup, resets and configures the ADC, populates IIO metadata, parses channels, fills scale tables, obtains and enables the IIO backend, requests a backend buffer, calibrates the backend interface, and registers the IIO device.

Device setup performs either a PD-pin global reset sequence or software reset, enables REFBUF/REFSEL bits based on optional supplies, selects single-instruction mode, enables SDO unless SPI 3-wire mode is used, logs product-ID mismatches, enables echo clock mode, and resets packet format. Channel parsing creates one IIO voltage channel per child node. It validates `reg`, assigns scan indices, marks differential channels when `diff-channels` is present, records `bipolar`, assigns signed scan type for bipolar channels, and sets default unipolar SOFTSPAN to 0-40 V for unipolar channels. For 20-bit devices, scan types are dynamic and switch between 20-bit normal and 24-bit resolution-boost modes.

Backend calibration writes deterministic test patterns per channel, enables backend channels, sweeps I/O delay taps for each lane, records pass/fail status, chooses the center of the longest passing delay range, disables channels, restores data size, and clears packet format. The number of lanes depends on backend interface type: one lane for serial LVDS and one per channel for serial CMOS.

## State and persistence behavior
No filesystem persistence exists. State is held in `ad4851_state` and in device/backend registers. The mutex protects consecutive regmap operations and shared state changes. The PWM remains enabled after probe and is disabled by a devm cleanup action. OSR changes can alter packet format, backend data size, resolution-boost state, and scale caches. Backend channel enable state follows IIO scan masks through `ad4851_update_scan_mode()`. Calibration writes test-pattern registers and backend I/O delays, then restores packet mode.

## Dependencies and integration points
The driver integrates with SPI regmap, regulator bulk/optional consumers, GPIO descriptors, PWM, IIO core, and `linux/iio/backend.h`. It imports `IIO_BACKEND`. Board firmware must supply channel child nodes and a compatible IIO backend. OF and SPI tables cover AD4851-AD4858 and AD4858i. The driver also uses backend APIs for buffer request, enable, channel enable/disable, oversampling ratio, data size, interface type, I/O delay, and lane status.

## Risks and edge cases
`ad4851_set_calibbias()` rejects negative values even though `ad4851_get_calibbias()` sign-extends offset registers, which may prevent users from writing valid negative calibration offsets. The calibration restore path unconditionally sets backend data size to 20, which is natural for 20-bit parts but should be scrutinized for 16-bit variants. `ad4851_find_opt()` depends on at least one failing/passing range pattern in backend status; no passing delay window returns `-ENOENT` and blocks probe. Bulk writes are intentionally avoided for offset registers because CS must toggle after each byte. PWM requested frequency is clamped to chip max, so users may read back a different effective rate. Product-ID mismatches are informational only and do not fail probe.

## Test signals
Test reset via PD GPIO and software reset, SPI 3-wire vs 4-wire SDO enable, optional reference supply bits, all chip IDs and resolution variants, channel parsing with max channels, bipolar and unipolar scale lists, dynamic scan type transition after OSR on 20-bit parts, backend interface type handling, calibration success and no-window failure, PWM sample-frequency read/write clamping, oversampling ratios from 1 to 65536, packet format changes, backend data-size calls, calibbias/calibscale byte ordering, scan-mask backend channel enable/disable, and behavior when product ID does not match.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4851.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.c

## Purpose
`ad7091r-base.c` is the shared IIO core for the AD7091R family used by bus-specific front ends. It implements channel reads, scale reporting, threshold event ABI, IRQ event handling, reference selection, common probe/registration, and exported register access policy helpers.

## Important APIs, types, and functions
The file exports `ad7091r_events`, `ad7091r_probe()`, `ad7091r_writeable_reg()`, and `ad7091r_volatile_reg()` in namespace `IIO_AD7091R`. The base state and chip/init descriptions are declared in the companion header. `ad7091r_set_channel()` writes the conversion channel mask and performs the required dummy result read for the one-conversion sequencer latency. `ad7091r_read_one()` reads a result and checks that the result channel ID matches the requested channel. `ad7091r_read_raw()` implements raw and scale. Event functions read/write threshold high, low, and hysteresis registers and enable or suppress alert generation. `ad7091r_event_handler()` converts alert-status bits into rising/falling IIO threshold events.

## Control flow
Bus drivers call `ad7091r_probe()` with an `ad7091r_init_info` and IRQ. The common probe allocates the IIO device, lets the bus driver initialize `st->map`, installs IIO info and direct mode, runs optional bus setup, selects IRQ-aware or no-IRQ chip info, enables alert generation and requests a threaded IRQ when an IRQ is present, wires channel metadata, configures optional external `vref` or internal reference, switches the part into command mode, and registers the IIO device.

Raw reads are serialized by `st->lock`. Only command mode allows raw reads; otherwise `-EBUSY` is returned. Scale reads use the external regulator voltage when available, otherwise the chip's internal reference millivolt value. Event config reads infer enabled state by comparing threshold registers with sentinel disabled values. Disabling events does not clear global alert enable; it writes high threshold to full scale or low threshold to zero so future alerts for that direction are suppressed.

## State and persistence behavior
The base layer caches the selected mode, optional regulator pointer, chip info, regmap pointer, GPIOs supplied by bus code, and small TX/RX buffers in `ad7091r_state`. Hardware state persists in CONF, CHANNEL, limit, hysteresis, and alert registers. The optional external regulator is enabled during probe and disabled by a devm action. There is no filesystem persistence.

## Dependencies and integration points
This file depends on IIO core/events, interrupt handling, regmap, regulators, cleanup guards, and the bus-specific `set_mode()` / `init_adc_regmap()` callbacks. It is consumed by `ad7091r5.c` and `ad7091r8.c`. It assumes chip info supplies channel arrays, default vref, result-channel-ID extraction, and mode-setting behavior.

## Risks and edge cases
The read path relies on result channel ID validation; bus drivers must supply the correct extractor width. Raw reads fail unless the part is in command mode, so future buffered/autocycle support would need explicit mode transitions. Event disable uses threshold sentinels and leaves alert enable set, so threshold writes after disable can re-enable practical alert behavior. `ad7091r_probe()` assumes `info_irq` is valid when IRQ is nonzero; bus init tables must populate it for IRQ-capable devices. Optional `vref` errors other than defer are treated as absent external reference and cause internal reference enable.

## Test signals
Test probe with and without IRQ, optional setup failure, regmap initialization errors, external vref and internal vref paths, regulator cleanup, raw reads in command and non-command modes, channel-ID mismatch returning `-EIO`, threshold read/write/config for rising/falling/hysteresis, alert IRQ event generation bits, and exported volatile/writeable reg helpers for RESULT and ALERT.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.h -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.h

## Purpose
`ad7091r-base.h` defines the shared register map, IIO channel macro, modes, state structure, chip descriptors, initialization contract, and exported symbols used by the AD7091R base driver and its I2C/SPI variants.

## Important APIs, types, and definitions
Register definitions cover result, channel, configuration, alert, per-channel low/high limits, and hysteresis. Result helpers extract conversion result bits and chip-family-specific channel IDs (`AD7091R5_REG_RESULT_CH_ID()` and `AD7091R8_REG_RESULT_CH_ID()`). Configuration bits include internal reference enable, alert enable, autocycle mode, and command mode. `AD7091R_CHANNEL()` builds a voltage channel with raw and shared scale info, optional event specs, indexed channel number, and 16-bit storage.

`enum ad7091r_mode` names sample, command, and autocycle modes. `struct ad7091r_state` is the private runtime state shared by the base and bus front ends: device, regmap, optional conversion/reset GPIOs, optional vref regulator, chip info, mode, mutex, and aligned 16-bit SPI buffers. `struct ad7091r_chip_info` supplies chip name, channel table, reference voltage, result-channel parser, and mode setter. `struct ad7091r_init_info` is the bus-driver handoff contract, containing IRQ/no-IRQ chip info, regmap config, regmap initializer, and optional setup callback.

## Control flow and integration
The header's contract is that bus-specific probe functions gather match data, initialize a bus-specific `ad7091r_init_info`, and call `ad7091r_probe()`. The base probe then calls `init_adc_regmap()` and optional `setup()` before using the chip info and callbacks to finish common IIO registration. Bus drivers also use `ad7091r_events` for IRQ-capable channel arrays and `ad7091r_writeable_reg()` / `ad7091r_volatile_reg()` in their regmap configs.

## State and persistence behavior
The header defines only in-memory state and hardware register constants. `ad7091r_state` stores runtime mode and bus resources. Hardware persistence is through ADC registers written by the base or bus driver; no filesystem state exists.

## Dependencies and integration points
It includes `linux/regmap.h` and forward-declares `struct device` and `struct gpio_desc`; it relies on IIO channel/event types being visible in including C files. It declares exported APIs in the `IIO_AD7091R` namespace and is included by both the base implementation and bus-specific drivers.

## Risks and edge cases
The shared state contains SPI-oriented TX/RX buffers even though the I2C variant does not need them; bus code must avoid assuming all fields are valid. The init contract has separate IRQ and no-IRQ chip info pointers; missing IRQ info on an IRQ-capable match will break common probe. `AD7091R_CHANNEL()` hardcodes voltage-channel info masks and 16-bit storage, so variants with different ABI needs would require a new macro or custom channel tables.

## Test signals
Header-level validation is mostly compile-time: ensure both bus drivers build against the exported prototypes and struct fields, regmap configs can call the access helpers, channel arrays compile with and without event specs, namespace imports are present in modules, and result-channel-ID macros match the data-sheet bit widths for AD7091R5 and AD7091R2/4/8 variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r-base.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r5.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r5.c

## Purpose
`ad7091r5.c` is the I2C front end for the AD7091R-5 four-channel 12-bit ADC. It supplies I2C regmap initialization, channel tables with and without threshold events, mode-setting behavior, chip info, and I2C/OF module registration while delegating common IIO behavior to `ad7091r-base.c`.

## Important APIs, types, and functions
The file defines `ad7091r5_channels_irq` and `ad7091r5_channels_noirq`, both built with `AD7091R_CHANNEL()` and differing only by event specs. `ad7091r5_set_mode()` maps `AD7091R_MODE_SAMPLE`, `AD7091R_MODE_COMMAND`, and `AD7091R_MODE_AUTOCYCLE` to CONF mode bits and updates `st->mode` after successful `regmap_update_bits()`. `ad7091r5_reg_result_chan_id()` uses the two-bit result channel ID macro. Two `ad7091r_chip_info` instances describe IRQ and no-IRQ operation, and `ad7091r5_regmap_init()` calls `devm_regmap_init_i2c()`.

## Control flow
`ad7091r5_i2c_probe()` obtains match data from I2C/OF tables and calls `ad7091r_probe(&i2c->dev, init_info, i2c->irq)`. The common probe initializes the regmap through `ad7091r5_regmap_init()`, selects the IRQ or no-IRQ channel table, configures reference handling and command mode, and registers the IIO device. The I2C driver itself has no raw-read logic, event handling, regulator management, or channel validation beyond its static tables.

## State and persistence behavior
Persistent runtime state is the shared `ad7091r_state` allocated by the base driver. This file mutates only `st->map` and `st->mode`. Hardware mode state is stored in `AD7091R_REG_CONF`; the regmap uses 8-bit register addresses and 16-bit values with base-provided writeable/volatile policies.

## Dependencies and integration points
The driver depends on I2C, regmap, IIO channel definitions, module infrastructure, and the `IIO_AD7091R` namespace. OF compatible is `adi,ad7091r5`; I2C ID is `ad7091r5`. It expects the base module APIs and event array to be available.

## Risks and edge cases
The mode setter updates cached mode only after the register write succeeds, which is correct but makes regmap errors visible as stale mode to the base read path. IRQ and no-IRQ chip info share the same name and vref, but only IRQ channels include events. The regmap config has no max register, so correctness depends on the base access policy and regmap/I2C behavior. Any future AD7091R-5 variant with different reference voltage or channel count needs separate chip info.

## Test signals
Test I2C probe through OF and legacy ID tables, absent match data returning `-EINVAL`, regmap init failures, IRQ and no-IRQ channel counts/event specs, mode transitions for sample/command/autocycle and invalid mode rejection, result channel extraction for channels 0-3, internal and external vref paths through the base probe, and module namespace import correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r8.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r8.c

## Purpose
`ad7091r8.c` is the SPI front end for AD7091R-2, AD7091R-4, and AD7091R-8 ADCs. It supplies SPI protocol glue, conversion-start/reset GPIO setup, channel tables for 2/4/8 channel variants, optional IRQ event channel tables for 4/8 channel variants, regmap configs, chip info, and SPI/OF module registration while using `ad7091r-base.c` for common IIO behavior.

## Important APIs, types, and functions
The file defines SPI command bit fields for register address, read/write flag, and data. `AD7091R_SPI_REGMAP_CONFIG()` creates variant-specific regmap configs with base volatile/writeable callbacks and a max register based on channel count. `ad7091r8_set_mode()` only updates cached mode because these SPI variants do not encode sample/command/autocycle mode in the shared CONF register. `ad7091r8_reg_result_chan_id()` extracts the three-bit channel ID.

`ad7091r_pulse_convst()` toggles the required conversion-start GPIO. `ad7091r_regmap_bus_reg_read()` performs a two-transfer SPI read, pulsing CONVST when reading RESULT, sending the register address in bits 15:11, then reading the 16-bit result. `ad7091r_regmap_bus_reg_write()` packs address, write flag, and 10-bit value into one big-endian 16-bit SPI word. `ad7091r8_gpio_setup()` requests required `convst` and optional `reset` GPIOs and releases reset after a small sleep.

## Control flow
`ad7091r8_spi_probe()` retrieves match data and calls the shared `ad7091r_probe()`. The base probe invokes `ad7091r8_regmap_init()` to build a custom regmap over the SPI bus and then `ad7091r8_gpio_setup()` to prepare CONVST/reset. Common probe then chooses IRQ or non-IRQ chip info, configures reference handling, calls the chip mode setter, and registers IIO. Raw reads from the base trigger `regmap_read(RESULT)`, which reaches this file's bus read callback and pulses CONVST immediately before the SPI read sequence.

## State and persistence behavior
The SPI front end stores `convst_gpio`, optional `reset_gpio`, and aligned TX/RX buffers in the shared state. The cached mode is maintained for the base read path but is not mirrored to a mode bit for these variants. Hardware configuration persists in ADC registers written through the custom regmap.

## Dependencies and integration points
The file depends on SPI, regmap custom bus APIs, GPIO descriptors, IIO channel definitions, and the `IIO_AD7091R` namespace. OF compatibles are `adi,ad7091r2`, `adi,ad7091r4`, and `adi,ad7091r8`; SPI IDs are `ad7091r2`, `ad7091r4`, and `ad7091r8`. AD7091R-4 and AD7091R-8 provide IRQ chip info; AD7091R-2 only provides no-IRQ chip info in this driver.

## Risks and edge cases
CONVST GPIO is required; probe fails if absent. Result reads pulse CONVST before every RESULT register access, including base dummy reads, so timing and GPIO polarity are critical. The write protocol masks data to ten bits even though the shared base treats register values as 16-bit; this matches the SPI framing but can surprise future code writing wider limit values. `ad7091r8_set_mode()` trusts the base mode model even though hardware behavior differs. IRQ match data for AD7091R-2 is absent, so an IRQ on that compatible would cause common probe to dereference missing IRQ chip info if not prevented by firmware expectations.

## Test signals
Test SPI probe for all three compatibles, missing CONVST GPIO, optional reset GPIO timing, custom regmap read/write packing, RESULT reads causing CONVST pulses, max-register limits for 2/4/8 channel devices, IRQ and no-IRQ channel tables, base raw reads in command mode, threshold events on 4/8 channel variants, and behavior when SPI transfers fail.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7091r8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7124.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7124.c

## Purpose
`ad7124.c` is the SPI IIO driver for AD7124-4 and AD7124-8 sigma-delta ADCs. It is built on the IIO `ad_sigma_delta` helper and supports direct conversions, triggered buffers, per-channel reference and filter configuration, shared hardware config-slot allocation, automatic and user-triggered calibration, internal/external clock selection, optional internal clock provider registration, debugfs controls, and voltage/temperature channels.

## Important APIs, types, and functions
`struct ad7124_state` embeds `struct ad_sigma_delta`, chip info, parsed logical channels, optional regulators for references, cached ADC control register, selected clock rate, config-slot use counts, default gain register value, and `enable_single_cycle`. `struct ad7124_channel` combines hardware input selection, logical slot, syscalib mode, and `struct ad7124_channel_config`. The config structure records reference, polarity, input buffers, vref, PGA bits, ODR selector, filter type, and calibration registers; equality determines whether channels may share one of the eight hardware config slots.

The sigma-delta hooks are `ad7124_set_channel()`, `ad7124_append_status()`, `ad7124_disable_one()`, `ad7124_disable_all()`, and `ad7124_set_mode()`. Config-slot management is handled by `ad7124_request_config_slot()`, `ad7124_release_config_slot()`, `ad7124_write_config()`, and `ad7124_prepare_read()`. IIO sysfs operations are implemented in `ad7124_read_raw()`, `ad7124_write_raw()`, `ad7124_read_avail()`, and ext_info helpers for system calibration and filter type. Probe helpers include `ad7124_parse_channel_config()`, `ad7124_soft_reset()`, `ad7124_check_chip_id()`, `ad7124_setup()`, and `ad7124_calibrate_all()`.

## Control flow
`ad7124_probe()` loads chip match data, allocates IIO state, enables single-cycle filtering by default, initializes `ad_sigma_delta`, parses channel firmware, requests and enables optional external reference regulators, soft-resets the ADC, validates chip ID and silicon revision, performs setup, installs sigma-delta buffer/trigger support, calibrates all voltage channels, registers the IIO device, and creates debugfs controls.

Channel parsing limits logical channels to 16, allocates IIO channel and private channel arrays, requires each child node to supply `reg` and `diff-channels`, validates input selections against AD7124-4/8 limits, records input mux bits, bipolar mode, reference select, and input buffer flags, then adds an internal temperature channel when there is room. Setup determines clock selection using legacy `mclk`, external `clocks`, internal clock, or internal clock-output provider mode. It sets full power by default, initializes `cfgs_lock`, resolves each channel's reference voltage, sets every config slot to unassigned, defaults filter type to sinc4 and requested ODR to 10 SPS, disables all channels, and writes the cached ADC control register.

During reads or scan-mode updates, the driver requests a matching or free hardware config slot, writes config/filter/offset/gain registers when needed, points the channel register at that slot, and enables the channel. Disabling a channel releases the slot and clears its channel register. Automatic probe calibration temporarily drops from full power to mid power because full-power calibration is unsupported, runs internal gain calibration when PGA > 1, runs internal offset calibration for voltage channels, reads resulting gain/offset values, and restores cached control state.

## State and persistence behavior
All state is in memory and hardware registers. The config-slot allocator tracks use counts so equal configurations can share hardware slots, and slot assignments are released on disable. Calibration results are cached per channel and written into the selected slot when that channel is prepared. `cfgs_lock` protects config data, slot use counts, and multi-register writes. The debugfs `enable_single_cycle` boolean changes future filter writes and exists only for testing. External regulators are enabled with devm cleanup actions.

## Dependencies and integration points
The driver depends on SPI, regulators, clocks/common-clock provider APIs, firmware child-node properties, debugfs, IIO core, IIO sysfs ext_info, and the `IIO_AD_SIGMA_DELTA` helper namespace. It exposes OF and SPI IDs for `adi,ad7124-4` and `adi,ad7124-8`. The sigma-delta helper owns much of the direct-conversion, trigger, status-byte, and reset-clock behavior.

## Risks and edge cases
Only eight hardware config slots exist; more than eight distinct active channel configurations return `-EUSERS`. Equal-config matching includes calibration values, so calibration changes can prevent sharing. Channel `reg` must be less than the number of child nodes, not just max channels, which enforces dense logical channel numbering. Post-filter sample-frequency values are fixed empirically for multichannel use and should be guarded by regression tests. Full-power calibration is worked around by changing cached power mode before calibration; any failure path must leave state coherent. Debugfs can disable single-cycle filter behavior, making sample rates differ from normal assumptions. The code assumes single conversions use config slot 0 when reading calibration results.

## Test signals
Test probe for AD7124-4 and AD7124-8, invalid chip ID and zero silicon revision, internal reference and external refin1/refin2/avdd references, missing regulator errors, legacy `mclk`, external clock, internal clock, and clock-provider modes, invalid `diff-channels` and sparse `reg` values, config-slot reuse and exhaustion, raw voltage and temperature reads through sigma-delta, scan-mode enable/disable, scale and offset calculations for bipolar/unipolar, ODR writes and filter-type changes, 3 dB frequency reads, automatic calibration at PGA 1 and >1, user system calibration modes, debugfs single-cycle toggling, and register debug access with size table bounds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7124.c -->
