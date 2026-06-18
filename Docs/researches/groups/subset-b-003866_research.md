# Research: subset-b-003866

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4030.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4030.c

## Purpose
`ad4030.c` is a Linux IIO SPI driver for the Analog Devices AD4030, AD4630, AD4632, ADAQ4216, and ADAQ4224 precision ADC family. It exposes differential voltage channels, optional common-mode byte channels, calibration scale and bias registers, oversampling/averaging controls, and, when platform hardware supports it, a high-rate SPI offload/DMA capture path driven by a PWM conversion signal.

## Important APIs, Types, and Functions
The central state object is `struct ad4030_state`, which holds the SPI device, custom regmap, chip descriptor, CNV GPIO/PWM, voltage readings, averaging mode, current output mode, optional SPI offload trigger and DMA resources, PGA GPIOs, and cache-aligned transfer buffers. `struct ad4030_chip_info` describes each supported device variant: scan masks, normal and offload channel arrays, grade, precision, PGA support, hardware input count, timing, and maximum sample rate.

The channel macros `AD4030_CHAN_DIFF`, `AD4030_CHAN_CMO`, `AD4030_OFFLOAD_CHAN_DIFF`, and ADAQ variants build IIO channel specifications for normal and offload operation. `ad4030_iio_info` wires IIO callbacks for raw reads/writes, available attributes, debugfs register access, labels, current scan type, and scan-mode updates. `ad4030_buffer_setup_ops` validates scan masks for the regular triggered buffer path; `ad4030_offload_buffer_setup_ops` owns offload postenable/predisable.

Register access is unusual: `ad4030_spi_read()` and `ad4030_spi_write()` enter configuration mode with the `AD4030_REG_ACCESS` preamble, perform the SPI transfer through a custom `regmap_bus`, and exit configuration mode unless the command is a software reset. Key conversion helpers include `ad4030_set_mode()`, `ad4030_conversion()`, `ad4030_single_conversion()`, `ad4030_trigger_handler()`, and `ad4030_extract_interleaved()`.

## Control Flow
Probe allocates an IIO device, initializes the custom regmap, fetches matched chip data, enables supplies, waits for power stability, resets the ADC, warns on unexpected grade, configures optional ADAQ PGA state, configures the default data mode/lane mode, obtains the CNV GPIO, and registers either a normal triggered-buffer device or an offload-backed DMA buffer. If `devm_spi_offload_get()` returns `-ENODEV`, the driver falls back to direct GPIO/SPI conversion with differential and common-mode channels. If offload exists, it restricts channels to offload channel definitions, requests a SPI offload trigger and RX DMA channel, obtains a PWM, and configures a default conversion rate.

Direct reads claim IIO direct mode, set the output mode for the requested scan bit, pulse CNV one or more times according to the averaging ratio, wait device timing, perform `spi_read()`, optionally deinterleave dual-channel bit streams, and return either differential or common-mode data. Triggered buffers run the same conversion path from `ad4030_trigger_handler()` and push the cache-aligned receive union with a timestamp.

Offload buffers build a streaming SPI message in `ad4030_prepare_offload_msg()`, reject unsupported interleaved dual-channel lane mode, optimize the message, program the CNV PWM waveform, and enable the SPI offload periodic trigger. Disable reverses that sequence by disabling the trigger, PWM, and optimized message.

## State and Persistence
Runtime state is held in `ad4030_state`; no persistent storage is used. Hardware state persists in ADC registers for gain, offset, averaging, output mode, IO drive, and lane mode until reset. The driver mirrors important settings in memory: `avg_log2`, `mode`, `pga_index`, `scale_avail`, `offset_avail`, `cnv_wf`, and `offload_trigger_config`. `iio_device_claim_direct()` protects direct raw/configuration transactions from active buffers, while offload setup and teardown are coordinated through IIO buffer callbacks.

## Dependencies and Integration Points
The driver integrates with SPI, regmap, regulator, GPIO descriptor, PWM waveform, SPI offload, DMAengine-backed IIO buffers, IIO triggered buffers, and IIO scan-type switching. Device tree or ACPI matching selects one of the static chip descriptors. Power inputs include `vdd-5v`, `vdd-1v8`, `vio`, and either `ref` or `refin`; ADAQ variants also require a two-line `pga` GPIO array. Offload mode depends on platform SPI offload support, a periodic offload trigger, an RX stream DMA channel, and a CNV PWM.

## Risks and Edge Cases
The conversion-rate path is timing-sensitive: PWM rounding and SPI offload trigger validation must still satisfy CNV high time, cycle time, and quiet delay. Averaging changes both CNV pulse rate and effective sample fetch rate; mistakes here produce stale or early samples. Dual-channel interleaved output is manually deinterleaved; bit-order regressions would corrupt both channels. Common-mode channels are disallowed with averaging by scan-mask validation, so tests must cover that ABI behavior. The offload path explicitly rejects dual-channel interleaved lane mode because extra hardware would be required. PGA scale selection converts between gain, full-scale range, and GPIO index, which is vulnerable to unit mistakes. Regmap read/write wrappers have fixed maximum transfer sizes, so new registers or wider transactions must stay within `AD4030_SPI_MAX_XFER_LEN`.

## Test Signals
Useful validation signals include probe success with and without SPI offload; correct fallback to direct mode on `-ENODEV`; regulator and reset error propagation; debugfs register reads across config-mode entry/exit; raw read timing with CNV GPIO; dual-channel deinterleaving patterns; common-mode scan enable/disable; calibration scale/bias read-write round trips; oversampling ratios and sample frequency constraints; rejection of common-byte scans while averaging; ADAQ PGA scale availability; offload buffer enable/disable sequencing; and DMA buffer data width changes between normal and averaged scan types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4030.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4062.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4062.c

## Purpose
`ad4062.c` is a Linux IIO I3C driver for Analog Devices AD4060 and AD4062 ADCs. It exposes one voltage channel with direct raw conversion, triggered buffering, oversampling/burst averaging, calibration scale, threshold events, optional GPIO-controller support on unused GPO pins, runtime power management, and I3C in-band interrupt handling.

## Important APIs, Types, and Functions
`struct ad4062_state` is the driver state: matched chip descriptor, current operation mode, trigger work item, completion for conversion readiness, IIO trigger/device pointers, I3C device, regmap, event-mode flag, reference voltage, available sampling frequencies, GPO IRQ ownership flags, selected sampling/event frequencies, oversampling ratio, conversion transfer size/address, and a cache-aligned big-endian conversion buffer.

`struct ad4062_chip_info` differentiates AD4060 and AD4062 by channel scan types, production ID, and maximum averaging ratio. `AD4062_CHAN()` builds a channel exposing raw, scale, calibration scale, oversampling ratio, sample frequency, and threshold event ABI. The IIO callbacks are collected in `ad4062_info`; it also provides event attribute group files for monitor-mode event sampling frequency.

Major helpers are `ad4062_set_oversampling_ratio()`, `ad4062_calc_sampling_frequency()`, `ad4062_set_operation_mode()`, `ad4062_read_chan_raw()`, `ad4062_trigger_work()`, `ad4062_ibi_handler()`, `ad4062_request_irq()`, `ad4062_request_ibi()`, and `ad4062_gpio_init()`.

## Control Flow
Probe matches the I3C device ID, allocates an IIO device, enables regulators, initializes regmap, sets default sample mode and frequencies, soft-resets the ADC, validates production/vendor IDs, configures GPO0 as interrupt and GPO1 as data-ready, configures the reference source and default monitor value, requests optional named GPIO IRQs or enables IBI fallback bits, registers an IIO trigger, sets up the triggered buffer, enables runtime PM with autosuspend, requests I3C IBI, initializes optional GPIO-controller support, installs autocancel work, and registers the IIO device.

Direct raw read claims IIO direct mode, runtime-resumes the device, programs the current operation mode and conversion frequency, writes the conversion trigger address, waits up to one second for completion from a DRDY IRQ or IBI, reads the 32-bit conversion register, and returns the big-endian sample. Buffered capture enables runtime PM, refuses to start if threshold event monitor mode is active, programs operation mode, determines storage width from current scan type, primes the conversion address, and then lets trigger polling schedule `ad4062_trigger_work()`. That work reads a sample over I3C, pushes it to IIO buffers with timestamp, and retriggers conversions when no external GPO1 DRDY IRQ is present.

Threshold event mode is mutually exclusive with direct reads and buffers via `st->wait_event`. Enabling events enters monitor mode and pins runtime PM active; disabling events releases autosuspend. Event values and hysteresis are stored in max/min limit and hysteresis registers. Interrupt delivery can come from named GPO IRQs or I3C IBI.

## State and Persistence
Driver state tracks mode, oversampling ratio as a log2-like value, selected sampling and event frequency table indexes, whether threshold monitoring is active, and whether each GPO is consumed as an IRQ. Device registers persist ADC mode, averaging, threshold limits, monitor calibration value, interrupt configuration, power mode, and GPO modes until reset. Runtime PM writes low-power mode on suspend and clears it on resume; monitor mode and active buffers hold an extra PM reference.

## Dependencies and Integration Points
The driver depends on I3C device transfers and IBI, regmap over I3C, IIO direct mode/events/triggers/triggered buffers, runtime PM, completions, workqueues, firmware IRQ lookup by `gp0`/`gp1`, regulators `vio`, `ref`, `vdd`, and optional GPIO controller registration. It uses `devm_work_autocancel()` to prevent delayed work from surviving device teardown.

## Risks and Edge Cases
The oversampling state stores `ilog2(val)`, while public ABI presents powers of two; all sample frequency calculations must use that representation consistently. Direct raw reads time out after one second, so very slow oversampling/frequency combinations are intentionally unsuitable for single reads. Event monitor mode blocks raw/event threshold updates and buffer activation; missing this mutual exclusion would race address pointer and mode changes. The fallback from named IRQs to I3C IBI changes conversion trigger behavior, so both topologies need coverage. GPIO-controller mode must not expose pins already used as IRQ lines. Runtime PM acquire macros require careful early-return behavior to avoid use while suspended.

## Test Signals
Probe should be tested for AD4060 and AD4062 IDs, regulator reference fallback, vendor mismatch rejection, soft reset, IRQ-present and IBI-only topologies, trigger registration, runtime suspend/resume register writes, oversampling availability truncation for AD4060, scale changes between sample and burst-averaging scan types, calibration scale write enabling/disabling scaling, threshold value/hysteresis range checks, monitor-mode enable/disable PM references, buffer start rejection during event mode, and GPIO valid-mask behavior when GPO pins are reserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4062.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4080.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4080.c

## Purpose
`ad4080.c` is a Linux IIO SPI driver for the AD4080 through AD4088 ADC family. Unlike simple direct-read ADC drivers, it relies on an IIO backend for data capture, lane configuration, filter selection, and interface alignment while the SPI regmap path configures device registers and exposes IIO control attributes.

## Important APIs, Types, and Functions
`struct ad4080_state` holds the regmap, IIO backend, matched chip info, mutex, configured lane count, conversion clock rate, current filter type, and whether LVDS CNV mode is enabled. `struct ad4080_chip_info` describes each variant by name, product ID, channel bit width, scale table, channel count, and maximum LVDS conversion clock latency.

The IIO ABI is implemented by `ad4080_iio_info` with raw read/write and available callbacks. `ad4080_filter_type_enum` exposes `filter_type` as an IIO enum with values `none`, `sinc1`, `sinc5`, and `sinc5+pf1`. `ad4080_get_dec_rate()` and `ad4080_set_dec_rate()` read/write decimation bits; `ad4080_read_raw()` reports scale, sample frequency, and oversampling ratio; `ad4080_set_filter_type()` coordinates filter changes with the backend and device register. `ad4080_setup()` performs reset, ID readout, GPIO/filter-ready setup, backend lane setup, optional LVDS CNV configuration, and alignment.

## Control Flow
Probe allocates the IIO device, enables five supplies, initializes SPI regmap, gets matched chip data, initializes the mutex, installs IIO metadata, parses firmware properties, enables the `cnv` clock and records its rate, obtains and enables the IIO backend, requests a backend buffer, performs device setup, and registers the IIO device.

During setup, the driver resets the ADC, enables SDO, reads product ID, configures GPIO1 as filter-result-ready, sets backend lane count, and, when `adi,lvds-cnv-enable` is true, sets LVDS data transfer latency, optional two-lane LVDS mode, LVDS conversion enable, then calls `ad4080_lvds_sync_write()`. Alignment temporarily enables interface checking, asks the backend to align data with a timeout-like argument of 10000, logs success, and disables interface checking.

Read/write control flow is compact. Scale is derived from the channel realbits and fixed 6000 mV scale table. Sample frequency is the conversion clock divided by decimation and adjusted for compensated sinc5. Oversampling ratio is one when no filter is selected or the register decimation otherwise. Filter and decimation setters hold `st->lock` and reject invalid combinations such as sinc5-family filters with decimation >= 512.

## State and Persistence
The driver mirrors only a small amount of mutable state in memory: lane count, clock rate, selected filter type, and LVDS CNV enablement. Persistent hardware state is in filter, interface, GPIO, LVDS, power, and reset-related registers. There is no software persistence beyond probe lifetime. The mutex protects multi-register transitions and consistency between backend filter state, device register state, and cached `filter_type`.

## Dependencies and Integration Points
Dependencies include SPI regmap, clock framework for `cnv`, regulator bulk enable for `vdd33`, `vdd11`, `vddldo`, `iovdd`, and `vrefin`, firmware properties `adi,num-lanes` and `adi,lvds-cnv-enable`, and the IIO backend namespace. The driver imports `IIO_BACKEND`, uses `devm_iio_backend_request_buffer()`, `devm_iio_backend_enable()`, `iio_backend_num_lanes_set()`, `iio_backend_filter_type_set()`, and `iio_backend_interface_data_align()`.

## Risks and Edge Cases
This driver is tightly coupled to backend behavior; register setup may succeed while capture still fails if lane count, LVDS CNV timing, or backend filter mode is mismatched. `ad4080_get_dec_rate()` returns an unsigned integer but can return a negative error encoded as a large value, while callers compare it with `< 0`; that deserves scrutiny because the signature can mask regmap read failures. Property parsing rejects lane counts outside 1-2, but chip descriptors include differing maximum LVDS latency values rather than lane limits. The author string is missing a closing parenthesis in `MODULE_AUTHOR`, a low-risk metadata defect. Product ID mismatch logs info instead of failing, so compatible binding mistakes may still register a device.

## Test Signals
Validation should cover all chip IDs and bit widths, supply failures, invalid/missing `adi,num-lanes`, CNV clock rate reporting, backend acquisition/buffer/enable failures, product ID mismatch logging, filter enum get/set synchronization with backend calls, decimation availability shortening for sinc5-family filters, sample frequency math for each filter, LVDS CNV enable and two-lane register bits, interface alignment success/failure, and debugfs register access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4080.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4130.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4130.c

## Purpose
`ad4130.c` is a Linux IIO SPI driver for the Analog Devices AD4130 low-power precision ADC. It builds channels from firmware child nodes, supports per-channel differential input configuration, excitation currents, burnout current, reference selection, PGA scale, digital filter type and sample frequency, direct single-sample reads, FIFO-backed buffered capture, GPIO output on unused analog pins, and optional internal clock output.

## Important APIs, Types, and Functions
`struct ad4130_state` is large because it tracks regmap/SPI/clock/regulators, IRQ polarity, mutex/completion, generated IIO channels, per-channel setup, shared setup slots, pin-function ownership, VBIAS pins, scale tables, GPIO chip, internal clock provider, FIFO state, and cache-aligned SPI buffers.

The setup model is split across `struct ad4130_setup_info`, `struct ad4130_chan_info`, and `struct ad4130_slot_info`. Channels have desired setup data; hardware has only eight setup slots, so `ad4130_find_slot()`, `ad4130_write_slot_setup()`, and `ad4130_write_channel_setup()` link, reuse, or overwrite slots while avoiding slots used by enabled channels. `ad4130_filter_configs` defines filter-specific ODR conversion behavior and availability tables. `ad4130_info` exposes raw, scale, offset, sample frequency, filter ext-info, debugfs register access, scan-mode updates, and hardware FIFO watermark control.

Register IO is implemented through custom regmap callbacks `ad4130_reg_read()` and `ad4130_reg_write()` because registers have mixed 1-, 2-, and 3-byte widths described by `ad4130_reg_size[]`.

## Control Flow
Probe allocates the IIO device, initializes reset/completion/mutex/FIFO message templates, creates custom regmap, gets and enables `avdd`, `iovdd`, `refin1`, and `refin2`, performs an SPI soft reset by writing eight `0xff` bytes, parses firmware, programs hardware, sets up optional internal clock provider, computes scale tables, registers a GPIO chip for unused AIN2-AIN5 pins, sets up an IIO kfifo buffer with FIFO attributes, requests the threaded IRQ, caches normal and inverted IRQ trigger polarity, and registers the IIO device.

Firmware parsing selects the IRQ/int pin, external clock source/rate, internal reference voltage, bipolar mode, VBIAS pins, and one IIO channel per child node. Each channel requires `diff-channels`; optional properties configure excitation currents, excitation pins, burnout current, buffered reference inputs, and reference source. Pin validation prevents conflicts with special interrupt/clock pins and tracks pins used for differential inputs, excitation, and VBIAS.

Direct raw read claims direct mode, enables the requested channel, switches to continuous mode, waits for completion from the IRQ handler, returns to idle, reads `AD4130_DATA_REG`, disables the channel, and returns the sample. Buffered mode uses `update_scan_mode()` to enable selected channels and count them, then `ad4130_buffer_postenable()` enables FIFO watermark interrupts, inverts IRQ trigger polarity for FIFO mode, enables FIFO watermark mode, and enters continuous conversion. IRQ handling drains `effective_watermark * data_reg_size` bytes from FIFO and pushes aligned sets to IIO buffers. Predisable returns to idle, restores IRQ polarity, disables FIFO/watermark interrupt, and disables all channels.

## State and Persistence
Mutable in-memory state includes setup-slot ownership counts, channel enablement, current filter/PGA/FS/reference selections, scale tables, selected IRQ polarity, FIFO watermark/effective watermark, and pin ownership. Device registers persist ADC control, channel routing, setup slots, filter slots, VBIAS, GPIO outputs, FIFO mode/watermark, and channel enables until reset. The driver uses `st->lock` around setup-slot and FIFO/mode transitions, and `completion` to wait for direct conversion readiness.

## Dependencies and Integration Points
The driver depends on SPI, custom regmap, regulator framework, firmware node child parsing, clocks, optional clock provider registration, GPIO chip registration, IRQ trigger type handling, IIO kfifo buffers, and IIO ext-info enums. External bindings must provide regulators, an IRQ with rising or falling trigger, child nodes with differential channels, and valid reference/excitation settings. Optional `mclk`, `adi,ext-clk-freq-hz`, `adi,bipolar`, `adi,vbias-pins`, and `clock-output-names` alter setup behavior.

## Risks and Edge Cases
The setup-slot allocator is the highest-risk logic: eight hardware setup slots must be shared across up to sixteen channels, and changing a disabled channel can unlink or overwrite slots used by other disabled channels. The direct read path must disable the channel after reads; errors before that point can leave channels enabled. FIFO watermark is specified in channel sets but programmed in samples; the driver rounds down to avoid unaligned FIFO frames. IRQ polarity is inverted only in FIFO mode, so invalid or missing trigger flags fail probe. Firmware pin validation allows some overlapping functional bits but rejects special-pin conflicts; binding mistakes can silently reserve scarce pins. In `ad4130_write_slot_setup()`, both excitation current fields use `AD4130_CONFIG_IOUT1_VAL_MASK`, which looks suspicious because an `IOUT2` mask exists and should be reviewed. The function name `ad4310_parse_fw()` appears to be a typo but is internally consistent.

## Test Signals
Testing should cover mixed-width regmap reads/writes, soft reset timing, firmware parsing errors for invalid clock/reference/current/pin/channel counts, scale table generation for each reference and bipolar mode, setup-slot reuse/overwrite under channel enable/disable scenarios, direct read timeout and cleanup behavior, filter-type changes preserving approximate ODR, sample-frequency to FS conversion boundaries, PGA scale writes, FIFO watermark rounding with multiple enabled channels, FIFO interrupt polarity switching, kfifo data grouping, GPIO valid-mask and set behavior, internal clock provider enable/disable, and regulator cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4130.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4134.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ad4134.c

## Purpose
`ad4134.c` is a compact Linux IIO SPI driver for the Analog Devices AD4134 four-channel ADC in minimum I/O mode. It exposes direct raw reads for four voltage channels and a shared scale derived from the `refin` regulator. Register access is wrapped with an SPI CRC byte, while sample data is read through virtual regmap addresses because conversion data is not memory-mapped in the actual register map.

## Important APIs, Types, and Functions
`struct ad4134_state` stores the SPI device, custom regmap, external system clock rate, ODR GPIO, reference voltage in millivolts, and cache-aligned transfer buffers. `AD4134_CHANNEL()` builds four simple IIO voltage channels with per-channel raw and shared scale attributes. `ad4134_regmap_config` uses custom `reg_read` and `reg_write` callbacks plus read/write access tables.

`ad4134_calc_spi_crc()` and `ad4134_prepare_spi_tx_buf()` implement the CRC-8 instruction/data wrapper. `ad4134_reg_write()` sends three-byte register writes and logs CRC mismatch from the echoed byte. `ad4134_register_read()` performs register reads. `ad4134_data_read()` handles virtual channel registers by clocking data for all four channels and keeping only the requested channel. `ad4134_min_io_mode_setup()` programs single-channel serialized output and duplicates DOUT0 onto SDO.

## Control Flow
Probe allocates an IIO device, sets static channel metadata, enables required and conditional supplies, selects an external clock source, deasserts optional reset, populates the CRC lookup table, initializes custom regmap, configures minimum I/O mode, programs 24-bit data frames, sets high-performance power mode, and registers the IIO device.

Raw reads pulse the `odr` GPIO high for at least the required gated DCLK high time, drive it low, then read the virtual channel register. The virtual read clocks three bytes from the SPI bus four times, once per channel, to avoid the device flagging an incomplete frame; only the requested iteration is returned. Scale returns `refin_mv / 2^(24 - 1)` as `IIO_VAL_FRACTIONAL_LOG2`.

## State and Persistence
The software state is minimal and lives only for the device lifetime. Hardware state persists in interface configuration, data packet configuration, power mode, and minimum-I/O routing registers. The driver does not implement buffered capture, events, calibration, or runtime PM. CRC mismatch handling is diagnostic only; failed CRC comparisons do not currently turn register transfers into errors.

## Dependencies and Integration Points
The driver depends on SPI, custom regmap, CRC8 helper, GPIO descriptor for `odr`, regulator framework, reset controller, clock framework, and IIO direct mode. Required regulators are `avdd5`, `dvdd5`, `iovdd`, and `refin`. Optional power topology uses `ldoin`; if absent, `avdd1v8`, `dvdd1v8`, and `clkvdd` are required. Clock selection expects exactly one external clock source and validates the resulting rate against 48 MHz, though it warns rather than fails on mismatch.

## Risks and Edge Cases
`ad4134_clock_select()` appears to request `"xtal"` twice and `"clkin"` twice, likely intending to use two distinct optional names but currently duplicating each lookup. It ORs the two clock rates, so if both clocks are present the result may not represent a real single source; the comment says only one should be provided. CRC mismatch is only logged at debug level and does not fail the transfer, which may hide communication corruption. `ad4134_data_read()` reads all channels for every raw read, so direct reads are slow and not suitable for high-rate sampling. The virtual regmap read range uses `AD4134_CH_VREG(AD4134_NUM_CHANNELS)` as an inclusive endpoint, which includes one address beyond the four valid channel indexes. Probe configures high-performance and 24-bit frame mode unconditionally; lower-power or alternate frame modes are not exposed.

## Test Signals
Validation should cover regulator topologies with and without `ldoin`, missing `refin`, optional reset deassertion failure, clock absence/presence/mismatch warnings, CRC table generation and transfer echo behavior, minimum-I/O register writes, ODR GPIO pulse on raw reads, virtual register reads for channels 0-3, out-of-range virtual register handling, scale calculation from regulator voltage, debugfs register reads/writes, and SPI error propagation during register and data transfers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad4134.c -->
