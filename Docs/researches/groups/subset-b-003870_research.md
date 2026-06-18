# Research Report: subset-b-003870

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7923.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7923.c

## Purpose
`ad7923.c` is an SPI IIO ADC driver for the AD7904/AD7914/AD7923/AD7924 and AD7908/AD7918/AD7928 families. It exposes 4-channel or 8-channel voltage inputs, direct raw reads, scale reporting from the `refin` regulator, and triggered-buffer capture. The driver programs the converter control register on each read or scan so each transfer selects the desired channel and keeps the ADC in normal operation with straight-binary output.

## Important APIs, Types, and Functions
The central private state is `struct ad7923_state`, holding the SPI device, regulator, cached control settings, prebuilt SPI messages/transfers, and DMA-aligned `rx_buf`/`tx_buf` buffers. `struct ad7923_chip_info` maps each chip ID to its channel table. `AD7923_V_CHAN`, `DECLARE_AD7923_CHANNELS`, and `DECLARE_AD7908_CHANNELS` construct IIO channel specs with unsigned big-endian 16-bit storage and chip-dependent realbits.

Important callbacks are `ad7923_read_raw()`, `ad7923_update_scan_mode()`, and `ad7923_trigger_handler()` through `ad7923_info`. `ad7923_scan_direct()` performs a single command/read sequence. `ad7923_get_range()` derives scale from `regulator_get_voltage()`, doubling the range unless `AD7923_RANGE` is selected. `ad7923_probe()` allocates the IIO device, parses `adi,range-double`, enables `refin`, configures default messages, sets up the triggered buffer, and registers the device.

## Control Flow
Probe selects chip metadata from `spi_get_device_id()`, establishes `st->settings`, builds a two-transfer direct-read message, enables the reference regulator, and registers the IIO device. Direct raw reads claim direct mode, send a write-control command for `chan->address`, read the returned 16-bit word, validate that the returned channel tag matches the requested channel, and extract the sample bits. Buffered mode is prepared in `ad7923_update_scan_mode()`, which rebuilds `ring_msg` for the active scan mask by first transmitting all channel-select commands and then reading one 16-bit result per active channel. The trigger handler runs that prebuilt SPI message and pushes the DMA-aligned receive buffer with a timestamp.

## State, Persistence, and Dependencies
Runtime state is in memory only: control settings, SPI message layouts, the active scan buffer layout, and reference regulator handle. No persistent storage is written. Dependencies are SPI, regulator framework, IIO direct mode, IIO triggered buffers, and firmware property access. The hardware state is restored only by probe-time configuration and per-transfer command writes.

## Integration Points
The driver binds by SPI IDs and OF compatibles. It integrates with IIO sysfs attributes for `raw` and `scale`, with triggered-buffer infrastructure for scans, and with the `refin` regulator for scale. The optional `adi,range-double` firmware property changes the ADC input range interpretation.

## Risks and Test Signals
Key risks are SPI controllers mishandling the command/read sequencing, incorrect `adi,range-double` configuration, regulator voltage errors changing scale, and scan masks exposing timestamp handling mistakes. The direct-read channel tag check is a useful test signal: wrong command timing or endian handling should return `-EIO`. Test by reading all raw channels, checking scale for both range modes, enabling triggered buffers for sparse and full scan masks, and verifying pushed samples are aligned and timestamped without stale channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7923.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7944.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7944.c

## Purpose
`ad7944.c` drives Analog Devices AD7944/AD7985/AD7986 PulSAR SAR ADCs. It supports pseudo-differential and fully differential devices, direct conversions, triggered-buffer capture, daisy-chain mode, optional TURBO handling, and a high-rate SPI offload path with DMA-backed IIO buffers. The driver maps device timing, resolution, signedness, maximum sample rate, and SPI topology into IIO channels and optimized SPI messages.

## Important APIs, Types, and Functions
`struct ad7944_adc` stores SPI mode, optimized normal and offload messages, SPI offload handles, sample-rate range, CNV/TURBO GPIOs, reference voltage, timing spec, chain-mode buffer, and DMA-aligned sample storage. `struct ad7944_chip_info` describes each chip. `AD7944_DEFINE_CHIP_INFO()` builds normal channels with timestamp and offload channels without timestamp but with `sampling_frequency`.

The SPI message constructors are `ad7944_3wire_cs_mode_init_msg()`, `ad7944_4wire_mode_init_msg()`, `ad7944_chain_mode_init_msg()`, and `ad7944_3wire_cs_mode_init_offload_msg()`. Runtime conversion is performed by `ad7944_convert_and_acquire()` and `ad7944_single_conversion()`. IIO callbacks include `ad7944_read_raw()`, `ad7944_read_avail()`, `ad7944_write_raw()`, trigger handler, and offload buffer pre/post enable operations.

## Control Flow
Probe reads chip match data and `adi,spi-mode`, validates SPI bits-per-word support for unusual widths, enables supplies, determines reference mode from `ref`/`refin`, validates CNV/TURBO configuration, and initializes the SPI message for default, single, or chain mode. Chain mode reads `#daisy-chained-devices`, allocates one voltage channel per device plus a timestamp, constructs a forced scan mask, and reads all devices in one transfer.

If no SPI offload provider exists, the driver uses standard IIO triggered buffers. The trigger handler toggles CNV for 4-wire mode through `ad7944_convert_and_acquire()`, then pushes either the single sample or chain buffer. If an offload exists, only single 3-wire mode is allowed. Probe gets a periodic offload trigger, initializes sample frequency, requests RX-stream DMA, installs an IIO DMA buffer, and prepares an offload message that reads the previous sample during conversion. Buffer enable asserts TURBO and enables the offload trigger; disable stops the trigger and clears TURBO.

## State, Persistence, and Dependencies
State is volatile and device-managed: GPIO levels, optimized SPI messages, selected sample frequency, chain buffers, and offload trigger state. Dependencies include SPI, SPI offload, DMAengine IIO buffers, regulator bulk APIs, GPIO descriptors, firmware properties, and IIO triggered buffers.

## Integration Points
The driver binds to `adi,ad7944`, `adi,ad7985`, and `adi,ad7986`. It exposes voltage raw/scale, and sample frequency only for offload channels. It integrates with board wiring through `adi,spi-mode`, `cnv-gpios`, `turbo-gpios`, `adi,always-turbo`, `ref`, `refin`, and `#daisy-chained-devices`.

## Risks and Test Signals
Risks center on timing and wiring assumptions: wrong CNV/CS topology, unsupported SPI word widths, invalid chain polarity (`SPI_CS_HIGH` and non-CPOL required), conflicting references, or enabling offload outside single mode. Test signals include successful probe under all three SPI modes, raw reads with sign extension for AD7986, scan-mask enforcement in chain mode, sample-frequency range validation, DMA streaming at offload rates, and TURBO GPIO state transitions around buffer enable/disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7944.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7949.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad7949.c

## Purpose
`ad7949.c` is an SPI IIO driver for AD7949, AD7682, and AD7689 14/16-bit SAR ADCs with 4 or 8 input channels. It provides direct raw voltage reads, scale reporting from internal or external references, debugfs register access, and device initialization for unipolar ground-referenced channel selection.

## Important APIs, Types, and Functions
`struct ad7949_adc_spec` captures channel count and resolution for each supported chip. `struct ad7949_adc_chip` keeps the mutex, regulator pointer, IIO/SPI handles, selected reference mode, resolution, cached configuration register, current channel, and transfer buffers for 16/14/8-bit SPI modes.

`ad7949_spi_write_cfg()` updates the cached configuration and writes it using the active SPI bits-per-word format. `ad7949_spi_read_channel()` implements the converter pipeline: write channel configuration up to twice when changing channels, then perform a read to retrieve the valid sample. `ad7949_spi_read_raw()` serves `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_SCALE`. `ad7949_spi_init()` writes the initial configuration and performs dummy conversions. `ad7949_spi_probe()` selects SPI word size, resolves reference source, enables regulators, initializes the chip, and registers IIO.

## Control Flow
Probe allocates the IIO device, selects channel count/resolution from the SPI ID, and chooses the best supported SPI word size in priority order: native resolution, 16 bits, then 8 bits. It parses `adi,internal-ref-microvolt` for 2.5 V or 4.096 V internal reference, then optionally switches to external buffered `vrefin` or unbuffered `vref`. External references are enabled only when selected.

Initialization writes a full configuration with overwrite, unipolar-ground input mode, selected reference, full bandwidth, sequencer disabled, and readback enabled. It then performs two dummy channel reads to settle the initial configuration. Later raw reads are serialized by `lock`, update the `INX` field, account for the ADC's N-2/N-1 pipeline latency, read the sample, shift or mask based on SPI word width, and update `current_channel`.

## State, Persistence, and Dependencies
The persistent runtime state is the cached `cfg`, `current_channel`, reference selection, resolution, and regulator enable state. There is no nonvolatile persistence. Dependencies are SPI, regulator framework, IIO direct mode, debugfs register access via IIO, firmware properties, and `FIELD_PREP()` bitfield helpers.

## Integration Points
Binding is via SPI IDs and OF compatibles for `adi,ad7949`, `adi,ad7682`, and `adi,ad7689`. IIO exposes per-channel raw reads and shared scale. Debugfs register access returns or overwrites the cached ADC configuration.

## Risks and Test Signals
The main behavioral risk is the converter pipeline: reads after channel changes require extra writes or stale samples may be returned. Other risks include unsupported SPI BPW, invalid internal reference property values, and incorrect external-reference selection. Test by reading alternating channels and confirming no cross-channel stale values, exercising all three SPI word-size paths where controller support allows, verifying scale under internal and external reference modes, and using debugfs access to confirm configuration writes preserve masked fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7949.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad799x.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad799x.c

## Purpose
`ad799x.c` supports the AD7991/AD7995/AD7999 and AD7992/AD7993/AD7994/AD7997/AD7998 I2C ADC families. It exposes direct voltage reads, triggered-buffer scans, optional threshold events for IRQ-capable variants, sampling-frequency controls for cycle-timer devices, reference-voltage scaling, and suspend/resume restoration.

## Important APIs, Types, and Functions
`struct ad799x_chip_info` and `struct ad799x_chip_config` define per-chip channel counts, channel specs, default configuration, event-capable versus no-IRQ IIO info, and whether an external `vref` is supported. `struct ad799x_state` holds the I2C client, selected config, regulators, mutex, ID, cached config, scan RX buffer, and transfer size.

Core helpers are `ad799x_write_config()`, `ad799x_read_config()`, and `ad799x_update_config()`, which abstract family-specific config storage and readback. `ad799x_scan_direct()` issues the appropriate I2C command for a single channel. `ad799x_update_scan_mode()` allocates the scan buffer and programs active channels for devices with config registers. Event support is implemented by `ad799x_read/write_event_config()`, `ad799x_read/write_event_value()`, `ad799x_event_handler()`, and frequency sysfs helpers.

## Control Flow
Probe selects IRQ or no-IRQ chip configuration depending on `client->irq`, enables `vcc`, optionally enables `vref` and sets `AD7991_REF_SEL`, populates the IIO device, writes the default config, initializes a triggered buffer, optionally requests a threaded alert IRQ, then registers IIO. Direct reads claim direct mode, lock the device, perform a single conversion, and extract sample bits according to the channel scan shift. Buffered scans compute the active-channel command in the trigger handler and read a block of two-byte samples into `rx_buf`.

Threshold events are available for IRQ configurations. Enabling an event sets the channel bit in the config word and globally controls `AD7998_ALERT_EN`. Threshold values are written to per-channel low/high/hysteresis registers. The event IRQ reads alert status, clears it, and pushes falling or rising IIO threshold events for channels encoded in the status byte. Suspend disables regulators; resume reenables them and rewrites the cached config.

## State, Persistence, and Dependencies
State includes cached config, selected chip config, regulator state, allocated scan buffer, and active transfer size. It is not persisted beyond driver lifetime, but resume uses `st->config` to resynchronize hardware. Dependencies include I2C SMBus operations, regulators, IIO events, IIO triggered buffers, sysfs attributes, mutexes, IRQ handling, and PM sleep ops.

## Integration Points
The driver binds via I2C IDs. IIO exposes raw/scale, buffers, optional threshold event attributes, and `sampling_frequency` attributes for event-capable configurations. The external `vref` regulator is optional for chips marked `has_vref`; otherwise scale uses `vcc`.

## Risks and Test Signals
Risks include inconsistent config caching across families with no readback, races between event configuration and buffer/direct reads, scan buffer reallocation failures, and resume failing to restore alert or channel selection. Test signals include raw reads across all channels, triggered scans for sparse masks, event threshold programming and IRQ event emission, frequency attribute round-trips for valid table values, regulator fallback from `vref` to `vcc`, and suspend/resume preserving configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad799x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad9467.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad9467.c

## Purpose
`ad9467.c` is a high-speed SPI control driver for multiple Analog Devices ADCs including AD9211, AD9265, AD9434, AD9467, AD9643, AD9649, and AD9652. It configures converter registers, exposes scale/sample-rate/calibration-bias controls, integrates with an IIO backend for data capture, and provides calibration/test-mode debugfs support for validating digital interface timing.

## Important APIs, Types, and Functions
`struct ad9467_chip_info` describes chip ID, channels, scale table, max rate, output mode, VREF mask, lane count, DCO capabilities, calibration test points, and offset range. `struct ad9467_state` holds chip info, SPI device, sample clock, backend, scale cache, calibration bitmap, optional powerdown GPIO, debugfs channel-test state, and a mutex.

SPI access is handled by `ad9467_spi_read()` and `ad9467_spi_write()`, with debugfs access through `ad9467_reg_access()`. Scale and offset are handled by `ad9467_get/set_scale()` and `ad9467_get/set_offset()`. Backend integration uses `ad9467_backend_testmode_on/off()`, `ad9467_update_scan_mode()`, and calibration helpers `ad9647_calibrate_prepare()`, `ad9467_calibrate_apply()`, `ad9467_find_optimal_point()`, and `ad9467_calibrate()`. Debugfs test-mode controls are implemented by `ad9467_chan_test_mode_read/write()` and `ad9467_debugfs_init()`.

## Control Flow
Probe allocates state, loads chip data, enables `adc-clk`, optional powerdown GPIO, performs reset, fills precomputed scale values, reads and verifies the hardware chip ID, chooses IIO info depending on available scales, obtains the IIO backend through the normal API or legacy `adi,adc-dev` lookup, requests backend buffer support, enables the backend, runs calibration if supported, registers IIO, then creates debugfs controls.

Reads return calibration bias, scale, or clock rate. Writes set calibration bias, select a scale by writing the VREF register and transfer-sync bit, or change sample rate. Sample-rate writes claim direct mode and trigger recalibration after `clk_set_rate()` when the rounded rate changes. Calibration switches the ADC to offset-binary PN9 test mode, enables backend PRBS checking, sweeps delay points, optionally repeats with inverted DCO/sample edge, chooses the midpoint of the longest valid run, applies the chosen delay, and restores normal test/output mode.

## State, Persistence, and Dependencies
State is volatile but hardware-facing: selected VREF/offset/sample clock, backend channel enablement, DCO delay or backend I/O delay, output mode, and debugfs test mode. Dependencies include SPI, clocks, GPIO reset/powerdown, IIO backend capabilities, debugfs, bitmap helpers, and IIO core controls.

## Integration Points
The driver binds by SPI IDs and OF compatibles. It relies on an IIO backend, often the ADI AXI ADC backend, for buffering, channel enablement, PRBS status, I/O delay, and debugfs status. It imports `IIO_BACKEND` and exposes backend-driven debug diagnostics.

## Risks and Test Signals
Major risks are backend/frontend mismatch, chip ID mismatch, broken delay clock returning invalid delay reads, calibration failing to find three valid points, and sample-rate changes without recalibration. Test by probing each compatible with expected chip IDs, reading and writing available scales, changing sample frequency while checking recalibration, enabling scan masks through the backend, dumping calibration maps, exercising PRBS debugfs modes, and verifying graceful behavior when backend capabilities are absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad9467.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad_sigma_delta.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad_sigma_delta.c

## Purpose
`ad_sigma_delta.c` is a shared support library for Analog Devices sigma-delta ADC drivers. It provides exported register access, reset, calibration, single-conversion, data-ready trigger, triggered-buffer, scan-mask validation, and optional SPI offload/DMA setup. Leaf drivers provide `struct ad_sigma_delta_info` callbacks and mode/channel operations while this file centralizes SPI sequencing and IIO integration.

## Important APIs, Types, and Functions
Exported APIs include `ad_sd_set_comm()`, `ad_sd_write_reg()`, `ad_sd_read_reg()`, `ad_sd_reset()`, `ad_sd_calibrate()`, `ad_sd_calibrate_all()`, `ad_sigma_delta_single_conversion()`, `ad_sd_validate_trigger()`, `devm_ad_sd_setup_buffer_and_trigger()`, and `ad_sd_init()`. Important internal helpers are `ad_sigma_delta_clear_pending_event()`, `ad_sd_disable_irq()`, `ad_sd_enable_irq()`, `ad_sd_buffer_postenable()`, `ad_sd_buffer_predisable()`, `ad_sd_trigger_handler()`, and `ad_sd_data_rdy_trig_poll()`.

The code relies on `struct ad_sigma_delta`, `struct ad_sigma_delta_info`, and `struct ad_sd_calib_data` from the public IIO ADC header. It uses DMA-aligned TX/RX buffers owned by the sigma-delta state, completion objects for conversion completion, a spinlock-protected IRQ-disable flag, and optional SPI offload handles.

## Control Flow
`ad_sd_init()` stores SPI/info pointers, derives slot count, validates that multi-slot devices provide `update_scan_mode()` and `disable_all()`, resolves the RDY IRQ or GPIO, optionally acquires SPI offload, and binds state to the IIO device. Register reads and writes build SPI messages with optional communications-register channel bits and optional register addressing.

Single conversion claims direct mode, selects the channel, locks the SPI bus, keeps CS asserted, clears stale pending events, starts single mode, enables RDY IRQ, waits for completion, reads the data register, disables IRQ, idles the converter, disables the channel, unlocks the bus, extracts sample bits, and runs postprocess. Buffered mode similarly locks the bus, builds an optimized sample message, configures slots, optionally appends status bytes for multi-channel sequencing, clears pending data, starts continuous mode, and either enables SPI-offload data-ready triggering or the software RDY IRQ. The trigger handler reads one conversion, validates appended channel status for multi-slot devices, assembles complete scans, pushes timestamps, and reenables RDY IRQ.

## State, Persistence, and Dependencies
State is runtime-only: bus lock flags, CS assertion, active slots, current slot, status-appended state, optimized SPI message, sample buffer, completion, IRQ disable flag, trigger, and optional offload trigger/DMA. Dependencies include SPI, SPI offload, IIO triggered buffers, DMAengine IIO buffers, GPIO RDY, IRQ handling, completions, spinlocks, and device-managed resource APIs.

## Integration Points
Leaf drivers call `ad_sd_init()` and `devm_ad_sd_setup_buffer_and_trigger()` and reuse `ad_sigma_delta_single_conversion()` for direct reads. The helper exports namespace `IIO_AD_SIGMA_DELTA` and imports `IIO_DMAENGINE_BUFFER`.

## Risks and Test Signals
Risks include stale RDY events before mode changes, shared RDY/MISO lines causing false interrupts, missing multi-slot callbacks, deadlocks around bus locking, status-channel desynchronization, and offload/non-offload divergence. Test signals include single conversion timeouts, calibration completion, multi-channel scans dropping desynced samples, scan-mask validation against slot count, RDY GPIO filtering, offload DMA setup, and correct cleanup on buffer disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad_sigma_delta.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ade9000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ade9000.c

## Purpose
`ade9000.c` is an SPI IIO driver for the ADE9000 polyphase energy-monitoring device. It exposes instantaneous current/voltage, RMS values, active/reactive/apparent power, energy accumulators, power factor, line frequency, calibration controls, waveform-buffer streaming, and voltage/current event interrupts for zero crossings, dips, and swells.

## Important APIs, Types, and Functions
`struct ade9000_state` stores reset completion, SPI mutex, waveform source/trigger/cache fields, SPI/regmap handles, optional input clock, transfer/message objects, a large DMA-aligned waveform buffer, and scratch buffers. Channel macros build a 33-channel IIO surface across phases A/B/C for current, voltage, RMS, power, energy, and power factor. Event tables map STATUS1 bits to IIO event codes.

Important functions include custom regmap bus accessors `ade9000_spi_read_reg()` and `ade9000_spi_write_reg()`, waveform functions `ade9000_configure_scan()`, `ade9000_iio_push_streaming()`, `ade9000_iio_push_buffer()`, IRQ threads `ade9000_irq0_thread()`, `ade9000_irq1_thread()`, `ade9000_dready_thread()`, raw/calibration/event callbacks, `ade9000_waveform_buffer_config()`, buffer setup ops, reset/setup helpers, optional `clkout` provider setup, and probe.

## Control Flow
Probe creates a custom regmap, initializes the mutex and reset completion, requests optional named IRQs (`irq0`, `irq1`, `dready`), enables optional input clock and optional `clkout`, enables `vdd`, installs a kfifo IIO buffer, resets the chip by GPIO or software bit, optionally selects external `vref`, writes the initialization register sequence, and registers IIO.

Raw reads handle line frequency through period registers, 64-bit energy through two-register bulk reads, power factor and direct measurement registers through regmap, and scale constants based on full-scale code values. Calibration writes route current/voltage/power gain and offset writes to phase-adjusted registers. Event config clears pending STATUS1, maps channel/type/direction to MASK1 bits, and also maintains waveform-trigger bits in `st->wfb_trg`. IRQ1 handles reset completion before normal event dispatch, then converts enabled status bits into IIO events and clears handled bits. Buffer preenable maps the active scan mask to one ADE9000 waveform-buffer mode, configures SPI reads from full or half waveform buffer, enables page-full interrupts, and starts waveform capture. IRQ0 pushes streaming pages and alternates half/full buffer addresses.

## State, Persistence, and Dependencies
Runtime state includes regmap cache, waveform source selection, active channel count, sample count, trigger bits, reset completion, IRQ masks, and enabled regulators/clocks. Dependencies include SPI, regmap, regulators, optional clocks/clock provider, GPIO reset, IIO kfifo buffers, IIO events, IRQs, completions, and firmware named IRQ/properties.

## Integration Points
The driver binds to `adi,ade9000`. It uses IIO ext-info for shared `filter_type`, debugfs reg access through IIO, optional `vref`, required `vdd`, named IRQs, optional reset GPIO, and optional `#clock-cells` clock output.

## Risks and Test Signals
Risks include register-width differences around `RUN`/`VERSION`, waveform scan masks unsupported by hardware, event bit mapping errors, reset completion depending on optional IRQ1, stale regmap cache for nonvolatile registers, and large waveform buffer memory/endianness assumptions. Test by validating raw/scaled reads for each channel class, 64-bit energy reads, calibration writes, event enable/readback/value thresholds, IRQ1 event delivery, buffer enable for each supported scan combination, IRQ0 half-buffer alternation, dready capture, reset with and without IRQ1, and reference/clock-provider configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ade9000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/adi-axi-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/adi-axi-adc.c

## Purpose
`adi-axi-adc.c` is a platform driver for Analog Devices AXI ADC FPGA IP cores. It registers an IIO backend that front-end ADC drivers can use for channel enablement, data formatting, DMA buffer allocation, calibration/status checks, sample-trigger polarity, I/O delay tuning, interface alignment, oversampling controls, and raw bus access for AD7606-style child devices.

## Important APIs, Types, and Functions
`struct axi_adc_info` describes expected HDL version, backend info, optional child-node support, and platform data. `struct adi_axi_adc_state` stores match info, MMIO regmap, device pointer, and a mutex for register sequences. Backend ops are grouped into generic AXI ADC, AD485x-specific, and AD408x-specific `struct iio_backend_ops` tables.

Important operations include `axi_adc_enable()/disable()`, `axi_adc_data_format_set()`, `axi_adc_data_sample_trigger()`, `axi_adc_iodelays_set()`, `axi_adc_test_pattern_set()`, `axi_adc_chan_status()`, `axi_adc_chan_enable()/disable()`, `axi_adc_interface_type_get()`, `axi_adc_num_lanes_set()`, DMA buffer request/free, debugfs register/status helpers, AD485x data size and oversampling functions, AD408x filter and data-align functions, and `ad7606_bus_reg_read/write()`.

## Control Flow
Probe maps MMIO, creates a 32-bit regmap, obtains match data and core clock, forces the core into reset, reads and validates the HDL major version, registers the selected IIO backend, and optionally instantiates a child platform device for the `adi,axi-ad7606x` binding. Enable deasserts MMCM reset, polls DRP lock, then releases core reset. Frontend drivers call backend ops to enable/disable channels, configure format sign extension or offset-binary handling, set PN test patterns, request DMAengine buffers, set I/O delays, read PN status, or align AD408x serial data.

The AD7606 bus helper temporarily switches the raw config bus into register mode: reads issue an address with the read bit, fetch `CONFIG_RD`, extract the low byte, then write zero to return to ADC mode; writes similarly encode address and value and restore ADC mode.

## State, Persistence, and Dependencies
State is MMIO hardware state plus the registered backend. There is no persistent storage. Dependencies include platform MMIO resources, clocks, regmap MMIO, IIO backend framework, IIO DMAengine buffers, child platform devices, firmware child nodes, and ADI AXI version helpers.

## Integration Points
This backend is consumed by front-end drivers such as `ad9467.c`. OF compatibles select generic `adi,axi-adc-10.0.a`, `adi,axi-ad408x`, `adi,axi-ad485x`, or `adi,axi-ad7606x`. It imports `IIO_BACKEND` and `IIO_DMAENGINE_BUFFER`, and supplies `ad7606_platform_data` for child bus access.

## Risks and Test Signals
Risks include HDL/driver version mismatch, failing DRP lock, delay-clock problems indicated by all-ones delay readback, incorrect lane count, concurrent raw bus operations without locking, DMA name mismatches, and child-node validation failures. Test by probing each compatible, checking version rejection, enabling/disabling the backend, requesting DMA buffers with default and custom `dma-names`, sweeping I/O delay taps, running PRBS status checks through a frontend, testing AD485x packet-size and oversampling paths, AD408x sync polling, and AD7606 child register reads/writes returning to ADC mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/adi-axi-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/aspeed_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/aspeed_adc.c

## Purpose
`aspeed_adc.c` is a platform IIO ADC driver for Aspeed AST2400, AST2500, AST2600 ADC0/ADC1, and AST2700 ADC0/ADC1 controllers. It exposes direct voltage channels, scale, sample frequency, offset compensation, optional battery-sensing mode, trim-data loading from syscon OTP fields, and controller clock-divider setup.

## Important APIs, Types, and Functions
`struct aspeed_adc_model_data` captures per-SoC capabilities: sample-rate range, fixed reference voltage, init-sequence polling requirement, prescaler need, battery-sensing support, scaler width, channel count, and trim location. `struct aspeed_adc_data` stores device/model pointers, MMIO base, clock hardware, reset control, vref, sample period, compensation value, and battery-sensing gain.

Important helpers are `aspeed_adc_channels_mask()`, `aspeed_adc_get_active_channels()`, `aspeed_adc_set_trim_data()`, `aspeed_adc_compensation()`, `aspeed_adc_set_sampling_rate()`, `aspeed_adc_read_raw()`, `aspeed_adc_write_raw()`, `aspeed_adc_reg_access()`, `aspeed_adc_vref_config()`, and probe. Channel tables cover 16 normal channels and an 8-channel battery-sensing variant where channel 7 has distinct offset handling.

## Control Flow
Probe allocates IIO state, maps MMIO, registers a fixed divide-by-2 clock from the DT parent, optionally registers a prescaler, registers the scaler divider, deasserts reset with managed cleanup, configures reference voltage from fixed model data, optional `vref`, or `aspeed,int-vref-microvolt`, loads trimming data from syscon, detects `aspeed,battery-sensing`, enables the scaler clock, sets the default 65 kS/s sampling rate, starts the engine in normal mode, optionally waits for `INIT_RDY`, computes compensation by enabling compensation sensing and averaging 16 samples from channel 0, enables all normal channels, and registers IIO.

Raw reads return 10-bit MMIO samples. For the battery channel on capable controllers, the driver temporarily enables channel 7 and battery-sensing mode, waits for settling, applies the configured divider gain, and restores the control register. Offset returns the computed compensation value, also gain-adjusted for battery sensing. Scale returns `vref_mv / 2^10`, and sample frequency is derived from the scaler clock divided by 12 conversion clocks. Writes allow only sample frequency changes; raw and scale writes return `-EPERM`.

## State, Persistence, and Dependencies
Runtime state includes clock-divider configuration, reset state, reference selection bits, trim register value, compensation value, sample period, channel-enable bits, and optional battery-sensing mode. Dependencies include platform MMIO, reset controls, clock provider/divider APIs, regulators, syscon regmap, OF properties, IIO direct mode, and debugfs register access.

## Integration Points
The driver binds to Aspeed OF compatibles for AST2400/2500/2600/2700 variants. It consumes optional `vref`, `aspeed,int-vref-microvolt`, and `aspeed,battery-sensing`, and looks up the global `syscon` node for trim fields.

## Risks and Test Signals
Risks include incorrect vref units or range handling, syscon lookup fragility, sample-rate divider rounding, compensation timing, battery channel control-register restoration, and channel-count differences between 16-channel and 8-channel controllers. Test by probing all model data variants, verifying sample-frequency set/get boundaries, checking scale for fixed/internal/external references, confirming compensation offset is stable, reading normal and battery channels, validating `INIT_RDY` timeout behavior, and using debugfs reg access only on aligned valid registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/aspeed_adc.c -->
