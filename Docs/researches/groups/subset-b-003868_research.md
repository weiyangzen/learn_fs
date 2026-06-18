# Research: subset-b-003868

Grouped research for Analog Devices ADC drivers under `sources/distributed-fs/ceph-client/drivers/iio/adc/`. Each section preserves the source path and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7173.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7173.c

Purpose: this SPI IIO driver supports the AD717x precision sigma-delta ADC family and AD411x front ends. It wraps the common `ad_sigma_delta` helper, dynamically builds IIO channel descriptions from firmware child nodes, handles voltage/current/temperature channels, exposes sysfs controls for calibration and filter type, registers optional GPIO outputs through `gpio-regmap`, and can expose the internal ADC clock as a common-clk provider.

Important APIs, types, and functions: `struct ad7173_device_info` describes per-chip IDs, channel counts, reference options, GPIO count, data widths, calibration support, and ODR tables. `struct ad7173_state` owns the `ad_sigma_delta` instance, channel array, regulator bulk, ADC/interface mode caches, IDA-backed setup-slot tracking, optional clock provider, and GPIO regmap. `ad7173_fw_parse_device_config()` enables references/supplies and clocking, then calls `ad7173_fw_parse_channel_config()` to validate `diff-channels`, `single-channel`, `common-mode-channel`, `adi,current-channel`, `bipolar`, and `adi,reference-select`. `ad7173_setup()` resets the device, checks ID, allocates config counters, calibrates all voltage channels, and disables reset-enabled channels. Runtime paths are `ad7173_read_raw()`, `ad7173_write_raw()`, `ad7173_update_scan_mode()`, `ad7173_set_channel()`, and `ad7173_load_config()`.

Control flow: probe allocates IIO state, selects match data, initializes IDA, sets SPI mode 3, initializes `ad_sigma_delta`, parses firmware, sets up triggered buffers, resets/calibrates hardware, registers IIO, then initializes GPIO outputs. On raw reads, the common sigma-delta helper performs a single conversion after `set_channel()` loads or reuses an ADC setup slot. Buffered reads call `update_scan_mode()` to preprogram all selected channels and reject invalid combinations.

State and persistence: register state is mirrored in `adc_mode` and `interface_mode`; channel configuration is cached per `struct ad7173_channel_config`. Config register slots are shared and evicted by a small LRU based on `config_usage_counter`; `live=false` forces reload after ODR/filter/reference changes. Regulator and GPIO cleanup use devm actions. No persistent storage exists beyond hardware registers and kernel in-memory state.

Dependencies and integration: this file depends on SPI, regulators named `vref`, `vref2`, and `avdd`, optional `ext-clk`/`xtal`, device-tree child channel descriptions, `ad_sigma_delta`, IIO triggered buffers/events, common-clk, `regmap`, and `gpio-regmap`. It imports `IIO_AD_SIGMA_DELTA`.

Risks: setup-slot eviction can invalidate buffered scans if too many unique channel configurations are selected; the driver mitigates by comparing assigned slots after programming. SINC3 buffered scans require all enabled channels to use SINC3 with the same divider. Reference validation depends on regulator voltages and dummy regulators can fail probe when a channel selects them. AD4111 open-wire detection temporarily rewrites comparison channel state and GPIO open-wire enable bits, so direct-mode exclusion is important. Firmware channel validation is strict around VINCOM/divider pairing and current-channel support.

Test signals: useful tests include probe with each compatible ID, invalid reference/channel firmware, raw voltage/current/temp scale and offset, sys calibration writes under direct mode, filter and sampling-frequency changes invalidating configs, buffered scan rejection for mismatched SINC3 setups or excessive unique configs, GPIO output registration, and AD4111 open-wire event generation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7173.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7191.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7191.c

Purpose: this SPI IIO driver supports the registerless AD7191 sigma-delta ADC. Because the part controls channel, temperature, PGA gain, and output data rate through GPIO pins rather than normal SPI registers, the driver combines `ad_sigma_delta` conversion handling with GPIO-driven configuration.

Important APIs, types, and functions: `struct ad7191_state` contains the `ad_sigma_delta` core, a mutex for state changes, GPIO arrays for ODR and PGA pins, GPIOs for temperature and channel select, vref-derived scale tables, available sample-frequency tables, and an optional master clock. `ad7191_set_channel()` maps the sigma-delta channel address bits onto `chan_gpio` and `temp_gpio`. `ad7191_set_mode()` asserts or deasserts chip select through `ad7191_set_cs()` because CS is wired to PDOWN. `ad7191_config_setup()` reads optional fixed firmware properties `adi,odr-value` and `adi,pga-value`; if absent, it requires two GPIOs for each selectable control. `ad7191_read_raw()`, `ad7191_write_raw()`, and `ad7191_read_avail()` expose raw conversion, scale, offset, and sample frequency.

Control flow: probe allocates an IIO device, initializes the mutex, sets fixed channel descriptors, initializes `ad_sigma_delta` with no-register callbacks, sets up the common sigma-delta buffer/trigger, enables `avdd`, `dvdd`, and `vref`, configures optional GPIO-controlled ODR/PGA selection, gets temp/channel GPIOs, optionally enables `mclk`, then registers IIO. Raw reads delegate to `ad_sigma_delta_single_conversion()`. Writes are direct-mode-only and choose a matching gain or ODR index before updating GPIO arrays.

State and persistence: all mutable software state is in `scale_index`, `samp_freq_index`, and GPIO output levels. Scale availability is computed once from `vref` and four fixed gain settings. If firmware pins a gain or ODR property, the corresponding GPIO array is absent and writes return `-EPERM`. The driver has no persistent storage.

Dependencies and integration: it relies on an interrupt-capable DOUT/RDY line through the sigma-delta helper, SPI bus locking because DOUT/RDY is dual-use with data output, GPIO descriptors, regulators, optional clock framework, and IIO direct and buffered conversion paths.

Risks: board wiring is critical: CS must control PDOWN and DOUT/RDY must be IRQ-capable. The static `scale_buffer` is shared storage but populated during setup while guarded by the instance mutex; multiple devices with different vref values could overwrite shared scale availability. Scale writes compare only the nanosecond fraction field, so duplicate or close values should be considered. If fixed firmware values are not in the supported arrays, the current loops leave index zero rather than failing, which can hide invalid properties.

Test signals: verify probe with GPIO-selectable and firmware-fixed ODR/PGA modes, missing or wrong GPIO counts, raw conversions for both differential voltage channels and temp, `scale_available` and `sampling_frequency_available`, `-EPERM` when trying to change fixed settings, CS/PDOWN behavior during single and continuous modes, and buffer operation with the sigma-delta trigger.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7191.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7192.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7192.c

Purpose: this SPI IIO driver supports the AD7190/AD7192/AD7193/AD7194/AD7195 precision sigma-delta ADC family. It provides register-backed channel selection, calibration, buffered conversion, sample-frequency and filter controls, clock selection/provider support, bridge switch control, and AD7195 AC excitation.

Important APIs, types, and functions: `struct ad7192_chip_info` selects chip ID, channel table, sigma-delta callbacks, IIO info, and optional firmware channel parser. `struct ad7192_state` caches `mode`, `conf`, `gpocon`, reference and AINCOM millivolts, scale/filter/OSR availability, clock selection, and per-channel system calibration mode. The `ad_sigma_delta_info` callbacks are `ad7192_set_channel()`, `ad7192_set_mode()`, `ad7192_append_status()`, and `ad7192_disable_all()`. `ad7192_setup()` resets the device, reads ID, initializes mode/config from firmware booleans, writes registers, calibrates channels, and precomputes scales and filter tables. `ad7192_read_raw()` and `__ad7192_write_raw()` implement raw, scale, offset, sample frequency, 3 dB filter frequency, and oversampling ratio.

Control flow: probe requires an IRQ, allocates IIO state, enables AINCOM/AVDD/DVDD/vref supplies, selects chip data, optionally parses AD7194 firmware channels, initializes the sigma-delta helper and triggered buffer, configures clocking, performs hardware setup and calibration, then registers the device. Direct writes claim IIO direct mode, update cached registers, write hardware, and recalibrate when gain changes.

State and persistence: the driver keeps authoritative cached copies of mode and configuration registers. Scale availability is derived from `int_vref_mv` and unipolar/bipolar resolution. Filter-frequency availability is recomputed when sample frequency, SINC3/chop, or AD7193 averaging changes. `syscalib_mode[]` stores the selected calibration mode per logical channel. No disk persistence is used.

Dependencies and integration: it integrates with SPI, IRQ-driven `ad_sigma_delta`, regulators, common-clk, IIO sysfs attributes/events/buffers, firmware properties including deprecated clock booleans, and child nodes for AD7194 channel definitions.

Risks: clock setup has multiple compatibility paths, so malformed `clock-names` or deprecated properties can produce unexpected fclk. Several register writes in `__ad7192_write_raw()` do not check return values before continuing. Gain changes recalibrate all channels and can be slow or fail mid-write. AD7194 dynamically parsed channels must fit encoded address constraints. Buffered scan update iterates only over eight bits, so it is coupled to the non-AD7194 channel-mask model.

Test signals: test ID mismatch warnings, absence of IRQ, regulator fallback from vref to AVDD, internal clock provider registration, gain/sample-frequency/filter/OSR read-write cycles, sys calibration ext_info, AD7195 AC excitation attribute, bridge switch attribute, AD7194 child-node parsing and invalid AIN rejection, and triggered buffer scan mask programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7192.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7266.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7266.c

Purpose: this SPI IIO driver supports AD7265/AD7266 dual simultaneous-sampling SAR ADCs. It provides direct reads and triggered-buffer reads for single-ended, pseudo-differential, and differential modes, with optional platform-data-controlled address GPIOs, range, and signedness.

Important APIs, types, and functions: `struct ad7266_state` holds SPI, reference voltage, prebuilt single-conversion SPI message, selected mode/range/fixed-address state, three address GPIOs, and DMA-aligned sample/timestamp storage. `ad7266_select_input()` maps an IIO channel address to GPIO address pins according to mode. `ad7266_read_single()` selects an input and runs the wake/convert/powerdown SPI message. `ad7266_read_raw()` returns raw samples, scale, and offset. `ad7266_trigger_handler()` reads two samples into the buffer and pushes them with a timestamp. Channel tables are generated by macros for signed/unsigned, fixed/non-fixed, and differential/non-differential variants.

Control flow: probe reads optional `vref`, falls back to the 2.5 V internal reference, consumes legacy platform data if present, gets address GPIOs when not fixed-address, selects the correct channel table, initializes the three-transfer direct-read SPI message, sets up a triggered buffer with wakeup/powerdown preenable/postdisable hooks, and registers IIO.

State and persistence: state is minimal and in-memory. The device is woken by any read of two or more bytes and powered down by a read below two bytes. The selected input is held by GPIO output levels when address pins are used. Direct and buffered reads use the same DMA-aligned sample storage.

Dependencies and integration: this driver depends on SPI, optional `vref` regulator, optional legacy `platform_data/ad7266.h`, GPIO descriptors for `ad0`, `ad1`, and `ad2`, and IIO triggered buffers.

Risks: the driver still depends on platform data for non-default configuration; without it, it assumes fixed address, VREF range, and differential mode. Address selection is skipped for fixed-address boards, so channel tables must match wiring. The trigger handler pushes the whole padded `data` structure size, which includes timestamp alignment by design but should be verified against scan bytes. Direct reads claim IIO direct mode, but GPIO selection and SPI conversion are otherwise simple and not independently locked.

Test signals: verify probe with and without platform data, regulator fallback, address GPIO failures, raw conversion sign extension for signed modes, scale/offset for VREF vs 2*VREF and differential modes, allowed scan masks for simultaneous pairs, buffer wakeup/powerdown hooks, and triggered buffer sample ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7266.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7280a.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7280a.c

Purpose: this SPI IIO driver supports the AD7280A lithium-ion battery monitoring system. It enumerates a daisy chain of monitoring devices, exposes per-cell voltage and auxiliary temperature channels, provides a total-cell-voltage channel, implements cell balancing controls, and pushes threshold events when an alert IRQ is wired.

Important APIs, types, and functions: `struct ad7280_state` stores SPI, dynamic channel array, chain and alert configuration, CRC table, oversampling/acquisition settings, threshold register caches, cell-balance masks, mutex, and DMA-aligned 32-bit TX/RX buffers. Protocol helpers include `ad7280_calc_crc8()`, `ad7280_check_crc()`, `ad7280_write()`, `ad7280_read_reg()`, `ad7280_read_channel()`, and `ad7280_read_all_channels()`. `ad7280_chain_setup()` resets and enumerates daisy-chain addresses. `ad7280_channel_init()` creates 12 channels per device plus a total-voltage channel. Ext-info handlers implement `balance_switch_en` and `balance_switch_timer`.

Control flow: probe parses thermistor termination, acquisition time, and optional last alert channel masking, builds CRC tables, caps SPI to 700 kHz mode 1, initializes control bits, enumerates the chain, computes scan count and delay, registers power-down cleanup, creates channels, optionally configures alert relay/static-high behavior and threaded IRQ, then registers IIO. Raw reads lock the device and either read one channel or all channels for total voltage. IRQ handling reads all channels and compares raw values against cached thresholds before pushing IIO events.

State and persistence: thresholds and cell-balance masks are cached in memory and written to device registers. `readback_delay_us` is derived from acquisition time, oversampling ratio, channel count, and chain length and is recalculated when oversampling changes. Runtime state does not persist across driver reload.

Dependencies and integration: it uses SPI, CRC8, firmware properties, optional IRQ, IIO events, and sysfs ext_info. It does not use the generic IIO triggered buffer path; reads are direct polled transactions.

Risks: protocol correctness depends on CRC, bitfield layout, reversed device address encoding, and exact daisy-chain sequencing. `ad7280_chain_setup()` returns `n - 1` when a zero frame terminates discovery, so early zero or CRC errors change chain size or fail probe. Alert IRQ events are generic voltage/temp events and do not encode the exact cell/aux channel that crossed a threshold. Threshold conversions clamp values and use integer math. Cell-balance writes update the software mask before the SPI write, leaving a stale cache if the write fails.

Test signals: test CRC rejection, chain enumeration for one through eight devices, invalid firmware acquisition/alert properties, raw per-channel and total-voltage reads, oversampling delay recalculation, threshold read/write conversions, balance switch and timer ext_info, IRQ alert path, and cleanup power-down writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7280a.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7291.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7291.c

Purpose: this I2C IIO driver supports the AD7291 8-channel 12-bit SAR ADC with temperature sensor. It exposes voltage and temperature raw reads, scale, temperature average, threshold configuration, and alert IRQ events.

Important APIs, types, and functions: `struct ad7291_chip_info` stores the I2C client, optional vref regulator, cached command register, active event voltage-channel mask, and mutex. `ad7291_i2c_read()` and `ad7291_i2c_write()` wrap SMBus word-swapped register access. `ad7291_event_handler()` reads temperature and voltage alert status, toggles `AD7291_ALERT_CLEAR`, and pushes IIO threshold events. `ad7291_read_event_value()`, `ad7291_write_event_value()`, `ad7291_read_event_config()`, and `ad7291_write_event_config()` handle threshold and hysteresis sysfs. `ad7291_read_raw()` handles voltage, temperature, average temperature, and scale.

Control flow: probe initializes state, sets command defaults for noise delay, always-on temperature sensing, and low-level IRQ polarity, optionally enables external vref and marks `AD7291_EXT_REF`, registers channels and info, resets the device, writes the cached command, optionally requests a threaded low-level IRQ, then registers IIO. Voltage raw reads are refused when autocycle/event mode is active; otherwise the driver selects only the requested channel in the command register and reads the voltage register.

State and persistence: the command register cache is the central state. `c_mask` tracks voltage channels enabled for events; when nonzero, autocycle is enabled and direct voltage reads return `-EBUSY`. Threshold registers live on the device and are not cached except through readback. Optional regulator lifetime is devm-managed with explicit disable action.

Dependencies and integration: it uses I2C SMBus word-swapped operations, optional vref regulator, IIO event interfaces, and optional IRQ. There is no buffered IIO integration.

Risks: event config for temperature always reports enabled even though voltage event state is mask-driven. `ad7291_threshold_reg()` maps falling threshold value to `DATA_HIGH` and rising to `DATA_LOW`, which is counterintuitive and should be checked against datasheet semantics. Direct voltage reads temporarily modify the command register without restoring the prior channel mask when not in autocycle. Event clearing writes are not checked for errors. The average temperature raw case indentation is misleading but functionally returns after the SMBus read.

Test signals: verify reset and command writes at probe, external/internal reference scale, direct voltage read exclusion during autocycle, event enable/disable mask updates and command register values, threshold and hysteresis limits for voltage/temp, IRQ status decoding and alert clear behavior, and no-IRQ operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7291.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7292.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7292.c

Purpose: this SPI IIO driver supports the AD7292 8-channel 10-bit ADC. It verifies the vendor ID, exposes raw and scale attributes, and selects between all single-ended channels or one differential pair plus remaining single-ended channels based on firmware child-node content.

Important APIs, types, and functions: `struct ad7292_state` stores SPI, vref in millivolts, a DMA-aligned 16-bit data word, and two command bytes. `ad7292_spi_reg_read()` reads top-level registers with the read flag. `ad7292_spi_subreg_read()` reads configuration-bank subregisters. `ad7292_single_conversion()` sends a channel conversion command followed by a conversion-result read with a 6 us delay. `ad7292_vin_range_multiplier()` reads sampling mode and VIN range subregisters to compute scale multiplier 1, 2, or 4. `ad7292_read_raw()` returns ADC data bits or scale.

Control flow: probe allocates IIO state, reads `AD7292_REG_VENDOR_ID` and requires `ADI_VENDOR_ID`, enables optional `vref` or falls back to the 1.25 V internal reference, sets basic IIO metadata, scans firmware children for a `diff-channels` boolean, selects the matching static channel table, and registers IIO.

State and persistence: the driver does not cache hardware configuration beyond `vref_mv`; range multiplier is recomputed from device subregisters on each scale read. Direct conversion uses shared small TX/RX buffers but there is no buffered mode and no explicit locking.

Dependencies and integration: it depends on SPI, optional regulator `vref`, firmware child nodes, and the IIO direct-mode read API. No IRQ, trigger, regmap, or event support is present.

Risks: differential-channel detection treats any child with a `diff-channels` boolean as selecting the differential table, without parsing which channels are described. The differential channel lacks a scale info mask while the single-ended macro includes scale, so scale visibility differs. Scale reads perform three SPI subregister reads and can fail with `-EPERM` for undefined AVDD sampling/range combinations. Probe rejects wrong vendor ID but reports negative SPI read errors as a wrong ID message. There is no direct-mode claim in `read_raw()`, so concurrent sysfs reads could share buffers if the IIO core permits parallel calls.

Test signals: verify vendor ID success/failure, regulator fallback, single-ended vs differential firmware selection, raw conversion command sequence and bit extraction, scale multiplier for all legal sampling/range combinations, undefined AVDD range returning `-EPERM`, and repeated concurrent raw/scale sysfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7292.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7298.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7298.c

Purpose: this SPI IIO driver supports the AD7298 ADC with eight voltage channels and an internal temperature sensor. It provides direct raw reads, scale/offset, and triggered buffered voltage scans.

Important APIs, types, and functions: `struct ad7298_state` holds SPI, optional vref regulator, external-reference command bit, ring and single-scan SPI transfers/messages, and DMA-aligned RX/TX buffers. `ad7298_update_scan_mode()` builds the repeated-conversion SPI ring message from the active scan mask. `ad7298_trigger_handler()` executes the ring message and pushes samples with a timestamp. `ad7298_scan_direct()` performs a direct voltage conversion using a three-transfer message. `ad7298_scan_temp()` enables temperature conversion and averaging, waits more than 100 us, then reads and sign-extends the result. `ad7298_read_raw()` exposes raw, scale, and temp offset.

Control flow: probe gets optional `vref`, enables it if present and sets `AD7298_EXTREF`, initializes IIO channel metadata, builds the default single-scan message, sets up a triggered buffer, and registers IIO. Buffered scans are prepared whenever the active scan mask changes. Direct reads claim IIO direct mode, then choose voltage or temp conversion path.

State and persistence: state is limited to the optional external-reference flag and prepared SPI messages. The ring message is reconstructed from the current scan mask; direct and buffered paths share TX/RX buffers but direct reads are excluded while buffers are active by `iio_device_claim_direct()`. Regulator enable is undone through a devm action.

Dependencies and integration: it uses SPI, optional regulator `vref`, ACPI ID `INT3494`, IIO direct mode, and IIO triggered buffers. There is no device-tree match table in this file, only SPI ID and ACPI.

Risks: `ad7298_trigger_handler()` pushes `sizeof(st->rx_buf)` rather than the active scan byte count; this relies on the buffer layout and scan mask handling tolerating the larger aligned storage. Temperature scale and offset depend on reference voltage and integer formulas. Ring transfers are capped by arrays sized for eight channels plus setup transfers, so scan-mask assumptions matter. The temp channel has `scan_index=-1` and is direct-only. `spi_sync()` return is named `b_sent` but treated as an error code.

Test signals: verify optional regulator enable/disable and internal reference fallback, direct voltage reads for each channel, direct temperature conversion timing and sign extension, scale/offset values, scan mask to command-bit mapping, triggered buffer sample count/order, ACPI matching, and buffer/direct exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7298.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7380.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7380.c

Purpose: this SPI IIO driver supports a broad AD738x/ADAQ438x family of simultaneous-sampling SAR ADCs. It handles two-, four-, and muxed eight-input variants, differential/pseudo-differential/single-ended scan layouts, oversampling with resolution boost, alert thresholds, optional hardware gain, multi-lane SDO wiring, and optional SPI offload DMA streaming.

Important APIs, types, and functions: `struct ad7380_chip_info` captures channel tables, offload tables, simultaneous channel count, mux capability, supplies, reference constraints, common-mode supplies, scan masks, timing, and maximum conversion rate. `struct ad7380_state` owns SPI, regmap, scan state (`ch`, `seq`, `resolution_boost_enabled`), SDO lane count, vref/vcm/gain arrays, normal/sequence/offload SPI messages, offload trigger, sample-frequency range, DMA scan buffer, and register TX/RX words. The custom regmap bus uses `ad7380_regmap_reg_read()` and `_write()`. Runtime paths include `ad7380_set_ch()`, `ad7380_update_xfers()`, `ad7380_read_direct()`, `ad7380_read_raw()`, `ad7380_set_oversampling_ratio()`, alert threshold accessors, and buffer setup callbacks.

Control flow: probe validates match data and SDO lane count, enables chip-specific supplies, resolves internal/external reference, reads pseudo-differential VCM regulators, parses optional ADAQ per-channel gains, initializes regmap, prepares normal and sequencer SPI messages, chooses normal triggered-buffer or SPI-offload DMA setup, hard-resets/configures the ADC, and registers IIO. In muxed parts, buffer preenable selects either CH bit or sequencer mode based on active scan mask. Offload mode uses offload channels without software timestamps and configures a periodic SPI offload trigger.

State and persistence: register defaults are cached with maple regcache, while volatile CONFIG2/ALERT are read live. Oversampling writes update OSR and RES bits, set `resolution_boost_enabled`, and soft-reset the oversampling block. Sequencer state is enabled only while buffers/offload are active and disabled on teardown. Sample frequency is stored in `offload_trigger_hz`; non-offload sample frequency is not exposed.

Dependencies and integration: it uses SPI, regmap, regulators, firmware properties and child nodes, IIO events, triggered buffers, DMA-engine buffers, and `spi_offload`. It imports `IIO_DMAENGINE_BUFFER`.

Risks: simultaneous sampling requires restrictive scan masks; muxed sequencer mode doubles offload trigger rate internally. Transfer lengths depend on current extended scan type and SDO lane count; mistakes affect buffer alignment. Alert thresholds are only 12 MSBs and are compared before oversampling, so conversions to/from raw values shift by current scan type. Offload mode mutates channel tables/count and requires compatible provider capabilities. Hardware-gain parsing accepts closest supported gain, not exact-only. Multi-lane stripe mode and `bits_per_word` above 16 need controller support.

Test signals: verify all compatible match data, invalid SDO lane counts, reference and VCM regulator paths, gain parsing, direct reads for normal and resolution-boost scan types, oversampling ratio read/write and soft reset, scan mask selection for simultaneous/muxed/sequence modes, alert enable and threshold conversion, triggered-buffer preenable/postdisable, SPI offload frequency range and DMA setup, and fallback when offload is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7380.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7405.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7405.c

Purpose: this platform IIO driver supports the AD7405 and ADuM7701/7702/7703 isolated sigma-delta modulators through an IIO backend rather than direct SPI/I2C register access. It exposes one differential voltage channel with scale, offset, sampling frequency, and oversampling ratio.

Important APIs, types, and functions: `struct ad7405_chip_info` provides the device name and full-scale millivolts. `struct ad7405_state` stores the IIO backend handle, chip info, reference clock frequency, and current decimation rate. `ad7405_set_dec_rate()` validates the 32..4096 decimation range, claims direct mode, calls `iio_backend_oversampling_ratio_set()`, then caches the new rate. `ad7405_read_raw()` computes scale, oversampling ratio, sample frequency, and bipolar offset. `ad7405_write_raw()` only supports oversampling-ratio writes. `ad7405_read_avail()` reports the decimation range.

Control flow: probe allocates IIO state, gets match data, enables `vdd1` and `vdd2`, enables the input clock and records its rate, sets channel metadata, obtains the default IIO backend, enables backend channel 0, requests a backend buffer, enables the backend, programs a default decimation rate of 256, and registers IIO.

State and persistence: `dec_rate` is the key mutable state and mirrors the backend oversampling configuration. `ref_frequency` is fixed at probe from the clock. There is no hardware register cache in this driver and no persistent storage. The backend owns data movement and buffering.

Dependencies and integration: it depends on platform-device matching through OF compatibles, regulators `vdd1`/`vdd2`, a clock, and the IIO backend framework. It imports `IIO_BACKEND`.

Risks: the channel definition uses `info_mask_shared_by_all = IIO_CHAN_INFO_SAMP_FREQ | BIT(IIO_CHAN_INFO_OVERSAMPLING_RATIO)`, where the sample-frequency term is not wrapped in `BIT()` like the other masks; this deserves review because IIO masks normally use bit positions. `ad7405_set_dec_rate()` rejects rates outside range but does not enforce the documented step from `ad7405_dec_rates_range`. Sampling frequency is integer rounded from clock/rate. Probe programs the backend before IIO registration, so backend availability and channel enablement are hard probe dependencies.

Test signals: verify all compatibles select the correct full scale, missing supplies/clock/backend fail cleanly, default decimation 256 is programmed, oversampling read/write and available range, sampling frequency calculation from clock rate, scale and offset ABI values, backend buffer request/enable behavior, and direct-mode exclusion around decimation updates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7405.c -->
