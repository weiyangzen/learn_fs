# subset-b-003877 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-adc.c

Purpose: child IIO ADC/audio driver for STM32 DFSDM filters. It turns DFSDM filter instances into either voltage ADC devices or DMIC/audio capture devices, configuring sigma-delta channels, sinc filter oversampling, regular/injected conversions, hardware triggers, DMA buffering, and optional SD-modulator backend consumers.

Important APIs/types/functions: `struct stm32_dfsdm_adc` stores the shared `struct stm32_dfsdm`, filter id, scan mask, oversampling, hardware consumer/backend handles, DMA buffers, audio callback, and conversion completion. Key routines are `stm32_dfsdm_compute_osrs()`, `stm32_dfsdm_channels_configure()`, `stm32_dfsdm_filter_configure()`, `stm32_dfsdm_start_conv()`, `stm32_dfsdm_adc_dma_start()`, `stm32_dfsdm_postenable()`, `stm32_dfsdm_single_conv()`, `stm32_dfsdm_read_raw()`, and exported audio-buffer callbacks `stm32_dfsdm_get_buff_cb()` / `stm32_dfsdm_release_buff_cb()`.

Control flow: probe gets the parent DFSDM core data, validates the filter `reg`, requests the filter IRQ, reads `st,filter-order` and optional filter0 sync, initializes audio or ADC channel layout, optionally allocates DMA, registers IIO, and populates an audio DAI child for DMIC mode. Direct raw reads enable any SD modulator consumer/backend, start the shared DFSDM, enable regular EOC IRQ, configure one channel, wait on completion, read `RDATAR`, postprocess sign/resolution, and stop everything. Buffered capture enables consumers/backends, starts the shared DFSDM, programs cyclic DMA from `RDATAR` or `JDATAR`, enables DMA requests, configures regular or injected conversion mode, and pushes data to IIO or an audio callback from the DMA completion.

State and persistence: persistent state is in the parent channel/filter arrays plus per-device oversampling, sample frequency, SPI frequency, scan mask, DMA buffer position, and callback pointers. Hardware state spans channel serial settings, channel enable bits, filter order/oversampling/fast mode, trigger selection, DMA enable bits, and conversion mode bits. Suspend disables active buffers; resume restores channel configuration and restarts active capture.

Dependencies and integration: depends on the STM32 DFSDM core exports, regmap, DMAengine, IIO direct/buffer/trigger APIs, STM32 timer and LPTIM trigger naming, IIO hardware consumers, IIO backend namespace, OF child-node bindings, and optional ASoC-facing buffer callbacks.

Risks: oversampling search is expensive but bounded and rejects ratios that exceed DFSDM output range. Injected continuous conversion is not supported unless synchronized or externally triggered. DMA callback bypasses normal IIO trigger services and must maintain cyclic-buffer indexing correctly. Backend enable failure unwinds only previously reached setup, so multi-backend error paths need coverage. A debug-looking `dev_err()` remains in SPI clock write path.

Test signals: probe both legacy and generic bindings, ADC and DMIC compatibles, internal/external SPI clock modes, single raw conversion timeout/IRQ paths, oversampling and sample-frequency writes, one-channel continuous DMA, multi-channel injected scan with trigger, timer trigger validation, backend scale/offset reads, suspend/resume with active buffer, and audio callback registration/release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-core.c

Purpose: parent STM32 DFSDM core driver. It maps the DFSDM register block, creates the shared regmap and channel/filter resource arrays, manages mandatory and optional clocks, handles runtime/system PM, and populates child filter devices such as `stm32-dfsdm-adc`.

Important APIs/types/functions: `struct dfsdm_priv` wraps the platform device, exported `struct stm32_dfsdm`, SPI clock-out divider, active-channel counter, and `dfsdm`/`audio` clocks. Important functions are `stm32_dfsdm_start_dfsdm()`, `stm32_dfsdm_stop_dfsdm()`, `stm32_dfsdm_parse_of()`, `stm32_dfsdm_probe_identification()`, probe/remove, and PM callbacks. Compatibility data selects fixed STM32H7 sizing or STM32MP1 identification-register probing.

Control flow: probe parses MMIO and clocks, computes optional `spi-max-frequency` divider, initializes a clocked MMIO regmap, validates IPID/HWCFGR on STM32MP1 or uses static H7 counts, allocates filter/channel arrays, enables clocks and runtime PM, then calls `of_platform_populate()` for children. `stm32_dfsdm_start_dfsdm()` increments an atomic active count and on the first user resumes runtime PM, chooses clock source, programs clock-out divider, and sets global DFSDMEN. Stop decrements the count and disables global interface and clock-out on the last user.

State and persistence: persistent software state is the regmap, physical base, discovered channel/filter counts, resource arrays, SPI master frequency, divider, and active user counter. Hardware state is global channel-0 clock source/divider/enable bits plus volatile filter result/status registers. Runtime suspend disables clocks; resume re-enables them.

Dependencies and integration: depends on OF platform population, regmap MMIO with clock support, Linux clock and runtime PM APIs, pinctrl sleep/default states, identification registers from `stm32-dfsdm.h`, and child drivers using the exported start/stop symbols.

Risks: the active count is decremented on stop and error paths, so mismatched child start/stop calls can underflow logical usage. STM32MP1 rejects unexpected child count compared with hardware filters. `spi-max-frequency` must be achievable by a divider in 2..256. Clock-unprepare balancing is subtle because regmap clock initialization prepares the `dfsdm` clock.

Test signals: probe H7 and MP1 compatibles, missing/optional audio clock, invalid IPID, child count greater than filter count, SPI clock divider rounding and out-of-range errors, concurrent child start/stop reference counting, runtime suspend/resume clock toggling, system suspend/resume pinctrl selection, and child depopulation on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm.h -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm.h

Purpose: shared STM32 DFSDM hardware contract for the core and ADC drivers. It defines channel/filter register offsets, bit masks, field helpers, identification registers, filter-order enums, software resource structures, channel clock-source enum, and the exported DFSDM global start/stop prototypes.

Important APIs/types/functions: macros cover `DFSDM_CHCFGR*`, `DFSDM_AWSCDR`, filter registers `DFSDM_CR1/CR2/ISR/ICR/JCHGR/FCR/*DATAR`, watchdog thresholds/status, and identification registers. `struct stm32_dfsdm_filter_osr`, `struct stm32_dfsdm_filter`, `struct stm32_dfsdm_channel`, and `struct stm32_dfsdm` are the main cross-file types. `enum stm32_dfsdm_sinc_order` and `enum stm32_dfsdm_spi_clk_src` encode filter and serial clock configuration.

Control flow: this header has no runtime execution, but it drives all register programming in the core and ADC files. The core uses identification and global channel fields to size and enable the peripheral; the ADC driver uses channel config, filter config, status, data, DMA, and trigger fields for conversion setup and result handling.

State and persistence: the header models persistent hardware state through register fields and persistent software state through `struct stm32_dfsdm`. Filter OSR entries cache computed IOSR/FOSR, shifts, resolution, and max sample values; channel entries cache serial input type/source/alternate input.

Dependencies and integration: depends on Linux bitfield helpers and is tightly coupled to STM32 DFSDM device-tree bindings and child IIO drivers. The exported prototypes allow child modules to coordinate shared global enable and runtime PM through the parent core.

Risks: register-layout and bitfield correctness is critical; a wrong mask affects every consumer. There are typo-like risks in helper definitions, notably ISR/ICR macros that must match actual use. The structures are shared mutable state without internal locking, so child drivers rely on IIO serialization and parent active-counting.

Test signals: compile-time inclusion by both DFSDM drivers, successful regmap updates for every macro field, correct filter base/address masking for all filter instances, channel count bounds checking, generated OSR programming values, and working exported symbol linkage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-dfsdm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stmpe-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stmpe-adc.c

Purpose: IIO direct-mode ADC and temperature driver for the STMPE811 MFD. It exposes enabled voltage channels plus one processed temperature channel, using STMPE MFD register helpers and conversion-completion interrupts.

Important APIs/types/functions: `struct stmpe_adc` stores the parent `stmpe`, mutex, channel table, completion, active channel, and latest value. Main functions are `stmpe_read_voltage()`, `stmpe_read_temp()`, `stmpe_read_raw()`, `stmpe_adc_isr()`, channel descriptor helpers, `stmpe_adc_init_hw()`, probe, and resume.

Control flow: probe requests ADC and optional temperature IRQs, builds the channel table from `st,norequest-mask`, initializes the ADC block and common STMPE811 ADC state, enables ADC interrupts for requested channels, clears stale status, and registers the IIO device. Voltage reads select one channel in `ADC_CAPT` and wait for its interrupt. Temperature reads write `TEMP_CTRL` to start one conversion and wait for the temperature IRQ path. The ISR verifies the relevant channel status, reads the big-endian data register, clears ADC status when needed, stores the value, and completes the waiter.

State and persistence: runtime state is the active channel, completion, and latest raw value. Hardware state persists in STMPE ADC block enable, ADC control registers initialized by the MFD helper, ADC interrupt enable/status, and temperature threshold/control registers. Resume reinitializes hardware but does not rebuild channels.

Dependencies and integration: depends on `linux/mfd/stmpe.h`, platform IRQ names `STMPE_ADC` and `STMPE_TEMP_SENS`, OF property parsing, IIO direct-mode read callbacks, and STMPE parent-provided block enable/reg access functions.

Risks: direct reads require interrupts; timeouts clear ADC status only for voltage channels. `norequest-mask` controls which ADC inputs are exposed and interrupt-enabled, so bad firmware can hide channels. Temperature conversion uses threshold interrupt behavior by programming zero threshold. The `clk` field is unused.

Test signals: probe with and without temp IRQ, `st,norequest-mask` channel exclusion, voltage raw reads for each enabled channel, temperature processed conversion, ADC timeout handling, irrelevant IRQ returning `IRQ_NONE`, 10-bit versus 12-bit scale, and resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stmpe-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sun20i-gpadc-iio.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/sun20i-gpadc-iio.c

Purpose: direct-mode IIO GPADC driver for newer Allwinner sunxi platforms such as D1, T113-S3, and R329. It provides raw voltage channels allocated from firmware ADC channel info and a fixed 1.8 V / 12-bit scale.

Important APIs/types/functions: `struct sun20i_gpadc_iio` holds MMIO registers, completion, last selected channel, and a read mutex. Key routines are `sun20i_gpadc_adc_read()`, `sun20i_gpadc_read_raw()`, `sun20i_gpadc_irq_handler()`, `sun20i_gpadc_alloc_channels()`, and probe.

Control flow: probe allocates an IIO device, parses channel descriptors via `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, enables the bus clock, deasserts reset with a devm cleanup action, requests IRQ, programs autocalibration and single-conversion work mode, then registers IIO. A raw read serializes access, programs channel enable and data IRQ when the channel changes, enables ADC conversion, waits up to 10 ms for data interrupt, reads the per-channel data register, and unlocks. IRQ clears all data interrupt status and completes the pending read.

State and persistence: persistent software state is the MMIO pointer and `last_channel` cache used to avoid repeated channel/IRQ programming. Hardware state includes selected channel mask, data interrupt enable, CTRL autocalibration/single-mode/ADC-enable bits, reset line, and clock enable.

Dependencies and integration: depends on platform MMIO/IRQ, clock and reset frameworks, firmware property-based IIO ADC channel allocation, IIO direct mode, and Allwinner compatible `allwinner,sun20i-d1-gpadc`.

Risks: IRQ handler completes on any data interrupt after clearing all status bits, so concurrent reads are correctly serialized by the mutex but spurious interrupts may complete a read early. ADC enable is not explicitly cleared after each read. Timeout assumptions rely on datasheet acquisition/conversion maximums. Only scale is fixed; no calibration result is surfaced.

Test signals: firmware-defined channel enumeration, channel-switch reads, timeout with masked IRQ, interrupt status clearing, reset assertion cleanup, clock-enable failure, fixed scale reporting, and repeated reads that use `last_channel`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sun20i-gpadc-iio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sun4i-gpadc-iio.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/sun4i-gpadc-iio.c

Purpose: IIO GPADC and thermal-sensor driver for older Allwinner A10/A13/A31 MFD devices and DT-only sun8i-a33 THS. It exposes voltage ADC channels and optionally a temperature channel/thermal zone, using runtime PM autosuspend to keep the thermal sampling cadence valid.

Important APIs/types/functions: `struct gpadc_data` contains SoC-specific temperature calibration and channel-select fields. `struct sun4i_gpadc_iio` stores regmap, completions, IRQ ids, ignore flags, calibration data, mutex, thermal zone, and MFD/DT mode flags. Main functions are `sun4i_prepare_for_irq()`, `sun4i_gpadc_read()`, `sun4i_gpadc_read_raw()`, FIFO/temp IRQ handlers, runtime PM callbacks, thermal `get_temp`, MFD/DT probe helpers, and remove.

Control flow: probe allocates IIO, selects DT-only or MFD setup, initializes regmap and channel tables, requests MFD virtual IRQs with `IRQF_NO_AUTOEN`, enables runtime PM autosuspend, optionally registers a thermal zone, and registers IIO. Voltage reads runtime-resume the parent, flush FIFO, switch to ADC/touchscreen mode and channel, enable the FIFO IRQ, wait for completion, copy `adc_data`, then disable IRQ and autosuspend. Temperature reads either read `TEMP_DATA` directly in no-IRQ DT mode or wait on the periodic temp IRQ. Runtime resume programs ADC clock/acquisition/filter and starts periodic temperature sampling; suspend disables ADC and temp sensor.

State and persistence: software state includes last sampled ADC/temp values, completion, interrupt numbers, ignore flags for request-time races, SoC calibration constants, and thermal registration state. Hardware state persists in CTRL0/CTRL1/CTRL3/TPR mode, channel-select, FIFO trigger/flush, temp period, and MFD interrupt routing.

Dependencies and integration: depends on `linux/mfd/sun4i-gpadc.h`, regmap, regmap IRQ controller, runtime PM, IIO maps for hwmon, thermal-of, platform IDs for MFD children, and OF compatible `allwinner,sun8i-a33-ths`.

Risks: mode switching requires fixed 10 ms and 100 ms delays; conversion latency can be high when thermal support is enabled. MFD children may lack their own OF node, so thermal registration intentionally uses the parent device. IRQs are enabled only around reads and races are handled by atomic ignore flags. Error paths after runtime PM setup must unregister IIO maps.

Test signals: MFD and DT-only probe paths, voltage raw reads on four channels, temp raw/scale/offset reads, thermal zone callbacks, IRQ-disabled polling/no-IRQ temp path, runtime autosuspend/resume timing, FIFO flush, channel switch settling delays, and cleanup of IIO maps on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sun4i-gpadc-iio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc081c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc081c.c

Purpose: I2C IIO driver for TI ADC081C/ADC101C/ADC121C single-channel ADCs. It supports direct reads and triggered buffering, with model-specific bit resolution and regulator-derived voltage scale.

Important APIs/types/functions: `struct adc081c` stores the I2C client, vref regulator, resolution bits, and an aligned scan buffer. `adc081c_read_raw()` handles raw and scale reads, `adc081c_trigger_handler()` pushes buffered samples, and `adc081c_probe()` validates SMBus word support, enables vref, sets channel metadata, and registers the triggered buffer.

Control flow: direct raw read performs `i2c_smbus_read_word_swapped()` from conversion register 0, masks 12 result bits, and right-shifts according to the model. Scale reads use `regulator_get_voltage()` and return mV divided by `2^bits`. The trigger handler reads the same conversion register and pushes the sample with a timestamp.

State and persistence: persistent state is minimal: model bit width, enabled vref regulator, I2C client, and scan storage. The ADC itself continuously provides conversion results from one register; no driver-side configuration is maintained.

Dependencies and integration: depends on SMBus word-data functionality, IIO direct/buffer/triggered-buffer APIs, regulator `vref`, OF/I2C/ACPI match tables, and `devm_add_action_or_reset()` for regulator disable.

Risks: triggered-buffer samples store the raw 12-bit register value without applying the direct-read right shift, relying on scan_type shift to describe layout. Probe fails without SMBus word support or vref. No locking is needed because there is no mutable bus command state, but direct and buffered reads can still contend on the adapter.

Test signals: all three model IDs, ACPI `ADC081C`, raw value shifts for 8/10/12-bit devices, vref scale, triggered buffer timestamped samples, missing regulator, SMBus functionality rejection, and regulator cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc081c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc0832.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc0832.c

Purpose: SPI IIO driver for TI ADC0831/ADC0832/ADC0834/ADC0838 8-bit ADCs. It exposes single-ended and differential channel combinations and supports triggered buffers.

Important APIs/types/functions: `struct adc0832` stores SPI device, vref regulator, mutex, mux-bit count, aligned scan buffer, and small TX/RX buffers. Core routines are `adc0831_adc_conversion()`, `adc0832_adc_conversion()`, `adc0832_read_raw()`, `adc0832_trigger_handler()`, and probe.

Control flow: probe chooses channel table and mux-bit width from the SPI ID, enables vref, installs a regulator cleanup action, sets up a triggered buffer, and registers IIO. Direct reads lock, emit the device-specific start/single-ended/differential/channel command, run a two-byte SPI transfer, and return the received 8-bit result. ADC0831 uses a special read-only two-byte transfer and skips the tri-state/leading-zero bits. Triggered buffering iterates active scan channels under the same mutex and pushes collected bytes plus timestamp.

State and persistence: persistent state is model selection, vref regulator state, mux width, shared SPI buffers, and mutex. Hardware has no long-lived register configuration; every conversion command encodes the selected channel/mode.

Dependencies and integration: depends on SPI, regulator `vref`, IIO direct and triggered-buffer APIs, OF/SPI IDs, and scan metadata for differential channels.

Risks: command bit packing depends on mux width and channel numbering; differential entries must match the datasheet's odd/sign and select bits. The triggered handler pushes the full maximum data buffer size rather than only populated bytes, depending on IIO scan alignment behavior. The driver does not call `iio_device_claim_direct()` for raw reads but uses its mutex to serialize command buffers.

Test signals: all four chip variants, single-ended and differential channel reads, ADC0831 special path, vref scale, triggered buffer with mixed active channels, SPI transfer failure handling, and regulator cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc0832.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc084s021.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc084s021.c

Purpose: SPI IIO driver for the four-channel TI ADC084S021. It performs pipelined SPI reads where the first 16-bit response is discarded and supports direct and triggered-buffer sampling.

Important APIs/types/functions: `struct adc084s021` owns the SPI message/transfer, vref regulator, mutex, scan buffer, TX command array, and RX buffer with one trash word. Core functions are `adc084s021_adc_conversion()`, `adc084s021_read_raw()`, trigger handler, buffer preenable/postdisable, and probe.

Control flow: probe sets fixed channel metadata, initializes one SPI message over reusable TX/RX buffers, gets vref, installs triggered buffer setup ops, and registers IIO. Direct raw read claims direct mode, enables vref, programs one channel command, runs the pipelined conversion, disables vref, shifts the 8-bit result out of the returned word, and releases direct mode. Buffer preenable builds commands for active channels, extends transfer length to include trash plus active responses, and enables vref; trigger handler reads all active channels with the prebuilt message and pushes the scan; postdisable restores single-channel transfer length and disables vref.

State and persistence: persistent state is reusable SPI message length, active command list, vref regulator, and scan buffer. Hardware configuration is per-transfer only; the regulator is kept on while buffers are active and toggled for direct reads.

Dependencies and integration: depends on SPI, IIO triggered buffers, regulator `vref`, and fixed 4-channel scan metadata with big-endian 16-bit storage and 4-bit shift.

Risks: conversion results are delayed by one SPI word, so transfer length and trash-word handling are critical. Direct scale returns vref in mV as `IIO_VAL_INT`, not fractional by resolution. Error handling must always release direct mode and disable regulator. The shared message length is mutable and protected by direct-mode/buffer state plus trigger mutex.

Test signals: raw reads for all four channels, active scan masks of different sizes, preenable/postdisable regulator transitions, pipelined response alignment, SPI failure path, and scale read with regulator voltage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc084s021.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc108s102.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc108s102.c

Purpose: SPI IIO driver for TI ADC108S102/ADC128S102-style 8-channel converters. It supports direct scans and triggered buffers with a one-command pipeline and uses either ACPI default reference voltage or a DT regulator.

Important APIs/types/functions: `struct adc108s102_state` stores SPI device, reference voltage in mV, ring/direct SPI messages and transfers, and aligned TX/RX command buffers. Important functions are `adc108s102_update_scan_mode()`, `adc108s102_trigger_handler()`, `adc108s102_scan_direct()`, `adc108s102_read_raw()`, and probe.

Control flow: probe resolves vref from ACPI default 5000 mV or `vref` regulator, initializes a two-word direct SPI message, sets fixed eight-channel IIO metadata, installs triggered buffer support, and registers IIO. Updating scan mode fills TX commands for active channels plus one dummy command and rebuilds the ring SPI message. Direct read claims direct mode, sends channel command plus dummy word, skips the dummy first response, masks the 12-bit sample, and returns it. Triggered buffer executes the ring message and pushes RX data after the dummy response.

State and persistence: persistent state is reference voltage and prebuilt SPI messages/buffers. Scan mode changes mutate the ring message length and TX command list. Hardware has no persistent channel register; each SPI command selects the next conversion.

Dependencies and integration: depends on SPI mode expected by the board, IIO triggered-buffer APIs, regulator framework for non-ACPI systems, ACPI ID `INT3495`, OF/SPI IDs, and scan metadata using big-endian 16-bit samples.

Risks: ADC108S102 is effectively 10-bit but represented as 12-bit with two zero LSBs. Pipeline alignment requires skipping the first response and appending a dummy command. ACPI boards assume a hard-coded 5 V reference. There is no explicit mutex around direct and buffer SPI buffers beyond IIO direct-mode claims and scan-mode setup ordering.

Test signals: direct reads for all eight channels, scan-mask message construction, triggered buffer response alignment, ACPI and regulator reference paths, scale reporting, SPI failures, and mixed active channel masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc108s102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc12138.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc12138.c

Purpose: SPI IIO driver for TI ADC12130/ADC12132/ADC12138 12-bit-plus-sign converters. It supports single-ended/differential channels, EOC IRQ completion, auto-calibration, acquisition-time programming, positive/optional-negative references, and triggered buffering.

Important APIs/types/functions: `struct adc12138` stores SPI device, model id, vref regulators, mutex, completion, acquisition time, and aligned buffers. Key functions are `adc12138_mode_programming()`, `adc12138_read_status()`, conversion start/read helpers, `adc12138_adc_conversion()`, `adc12138_read_raw()`, `adc12138_init()`, trigger handler, EOC IRQ handler, probe, and remove.

Control flow: probe selects the channel table by model, reads optional `ti,acquisition-time`, requests the SPI IRQ as rising EOC, enables conversion clock and references, runs auto-calibration and acquisition-time setup, then registers triggered buffering and IIO. Direct raw read locks, starts a conversion for the requested mux, waits up to 100 ms for EOC completion, issues a status/read command to retrieve previous conversion data, sign-extends the shifted 13-bit result, and unlocks. Triggered buffering pipelines active channels, reading each previous result while starting the next conversion, then reads the final result and pushes the scan.

State and persistence: persistent state includes acquisition-time mode, model-specific mux packing, enabled regulators, clock, completion, and shared SPI buffers. Hardware state includes calibration status, acquisition-time setting, and current/previous conversion pipeline.

Dependencies and integration: depends on SPI, EOC IRQ, clock framework, `vref-p` regulator, optional `vref-n`, IIO triggered buffers, and OF/SPI IDs.

Risks: conversion depends on an IRQ; missing or miswired EOC causes timeouts. ADC12130/12132 command packing shifts unused bits differently from ADC12138. Negative reference is optional but affects scale and offset. Auto-cal status is warned and rejected if still busy. Manual remove is needed because regulators and buffer setup are not fully devm-managed.

Test signals: all three model IDs, EOC interrupt completion, auto-calibration failure, acquisition times 6/10/18/34, raw single-ended and differential reads, vref-n present/absent scale and offset, triggered buffer sequencing, timeout path, and cleanup disabling regulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc12138.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc128s052.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc128s052.c

Purpose: simple SPI IIO driver for TI ADC128S052/ADC122S/ADC124S families and compatible ROHM BD7910x parts. It exposes 1, 2, 4, or 8 voltage channels with direct raw reads and fixed 12-bit scale from a reference/supply regulator.

Important APIs/types/functions: `struct adc128_configuration` describes channel table, reference regulator name, and auxiliary regulators. `struct adc128` stores SPI device, mutex, vref in mV, and an aligned two-byte command/result buffer. Core functions are `adc128_adc_conversion()`, `adc128_read_raw()`, and probe.

Control flow: probe selects configuration from OF/ACPI/SPI match data, reads/enables the reference regulator via `devm_regulator_get_enable_read_voltage()`, optionally bulk-enables extra regulators such as `iovdd`, initializes the mutex, and registers IIO. A raw read locks, writes a two-byte command with channel in the upper bits, reads a two-byte result, masks 12 data bits, and returns it. Scale returns cached reference mV over `2^12`.

State and persistence: persistent state is the selected static channel table, cached vref mV, enabled regulators, mutex, and shared SPI buffer. Hardware state is transaction-local; no configuration register is retained.

Dependencies and integration: depends on SPI, regulator and bulk-regulator helpers, IIO direct mode, OF/SPI/ACPI match tables, and cleanup-guard mutex style.

Risks: conversion uses separate `spi_write()` then `spi_read()`, matching the chip pipeline but relying on controller chip-select behavior suitable for the device. No triggered buffer is provided. Cached scale will not reflect later regulator voltage changes. Match data must be present for every supported ID.

Test signals: all TI and ROHM channel-count variants, ACPI `AANT1280`, auxiliary regulator enable for BD7910x, raw reads per channel, scale read, SPI error propagation, and concurrent sysfs reads serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc128s052.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc161s626.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc161s626.c

Purpose: SPI IIO driver for TI ADC141S626 and ADC161S626 one-channel differential ADCs. It supports direct raw reads, vdda-derived scale/offset, and triggered buffering.

Important APIs/types/functions: `struct ti_adc_data` stores IIO device pointer, SPI device, vdda regulator, read size, shift, and aligned read buffer. Core functions are `ti_adc_read_measurement()`, `ti_adc_trigger_handler()`, `ti_adc_read_raw()`, regulator cleanup, and probe.

Control flow: probe selects 14-bit two-byte or 16-bit three-byte read format from SPI ID, enables `vdda`, installs triggered buffer support, and registers IIO. Measurement reads either 16 or 24 bits big-endian, right-shifts for ADC161S626, sign-extends to the channel realbits, and returns the sample. Direct reads claim direct mode around the SPI transaction. Triggered buffer reads one measurement and pushes a 16-bit sample plus timestamp.

State and persistence: persistent state is model-specific read size/shift, enabled reference regulator, and shared read buffer. Hardware state is stateless from the driver's perspective; each SPI read returns the current conversion word.

Dependencies and integration: depends on SPI, unaligned big-endian helpers, regulator `vdda`, IIO direct and triggered-buffer APIs, OF/SPI IDs, and signed scan metadata.

Risks: `ti_adc_read_raw()` returns 0 rather than `-EINVAL` for unknown masks, which can hide invalid calls. ADC161S626 three-byte data path must shift by six bits to align the 16-bit result. Trigger scan uses `s16`, so it is appropriate only for the one-channel signed storage layout.

Test signals: both chip IDs, direct raw reads, triggered buffer samples, vdda scale, offset equal to mid-scale, two-byte versus three-byte SPI paths, SPI error handling, and invalid mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-adc161s626.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1015.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1015.c

Purpose: I2C/regmap IIO driver for ADS1015, ADS1115, and TLA2024 ADCs. It exposes four single-ended and four differential voltage channels, per-channel gain and data-rate controls, one-shot buffered scans, runtime PM, and comparator threshold events for chips that support ALERT/RDY.

Important APIs/types/functions: `struct ads1015_data` stores regmap, mutex, per-channel PGA/data-rate settings, active event channel/mode, thresholds, chip data, and `conv_invalid`. Main functions are `ads1015_get_adc_result()`, trigger handler, scale/data-rate setters, raw read/write callbacks, event read/write/config callbacks, event IRQ handler, buffer setup ops, firmware channel config parsing, conversion-mode control, probe/remove, and runtime PM callbacks.

Control flow: probe selects chip data, initializes threshold defaults, reads optional child-node `ti,gain`/`ti,datarate`, creates an I2C regmap with threshold registers only for comparator chips, sets up a one-hot triggered buffer, optionally configures ALERT/RDY IRQ polarity and requests event IRQ, switches to continuous conversion, enables runtime PM autosuspend, and registers IIO. Raw reads claim direct mode, resume PM, program mux/PGA/data rate and comparator queue if needed, wait for stale conversion periods after config changes, read conversion register, sign-extend, then autosuspend. Events program low/high threshold registers, enable comparator queue/mode, force a first conversion, and push IIO events from the IRQ after reading conversion to clear latch.

State and persistence: persistent state includes per-channel PGA/data rate, thresholds, comparator queue, active event channel, conversion mode, and stale-conversion flag. Hardware state persists in config and threshold registers and is switched to single-shot on runtime suspend/remove.

Dependencies and integration: depends on I2C regmap, runtime PM, IRQ trigger type, IIO events/buffers, one-hot scan validation, firmware child-node properties compatible with the older hwmon ABI, and OF/I2C IDs.

Risks: buffer and event mode are mutually exclusive and enforced through direct-mode claims plus event state. Conversion validity requires sleeping for old plus new data-rate periods after config changes. TLA2024 lacks comparator registers, so event paths are removed through chip info. Firmware channel config fallback silently defaults when no valid children are parsed.

Test signals: ADS1015/ADS1115/TLA2024 variants, scale and sample-frequency available lists, per-channel write/readback, raw reads after data-rate/mux changes, one-hot triggered buffers, runtime suspend/resume stale conversion handling, comparator rising/window events, IRQ polarity validation, threshold/period configuration, and remove power-down.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1015.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1018.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1018.c

Purpose: SPI IIO driver for ADS1018/ADS1118 ADCs with voltage and internal-temperature channels. It supports per-channel PGA/data-rate settings, direct one-shot reads, one-hot continuous buffered capture, and an optional data-ready trigger using a shared DRDY/MISO-style line.

Important APIs/types/functions: `struct ads1018` stores SPI device, optional trigger, DRDY GPIO/IRQ, per-channel config, chip info, reusable read message, and aligned buffers. Key routines are `ads1018_calc_delay()`, `ads1018_single_shot()`, raw read/write/available callbacks, trigger state helpers, buffer preenable/postdisable, IRQ handler, trigger handler, trigger setup, and probe.

Control flow: probe initializes channel defaults, builds a reusable read message, optionally creates a DRDY trigger from SPI IRQ or `drdy` GPIO, sets up triggered buffer ops, and registers IIO. Direct raw reads claim direct mode, write a one-shot config with selected mux/PGA/max data rate and optional temp mode, delay for worst-case conversion, read the conversion, shift/sign-extend, and return. Buffer preenable validates a one-hot scan, writes continuous conversion config for the selected channel, and buffer postdisable returns the chip to one-shot mode. Own-trigger enable locks the SPI bus and holds CS low so DRDY can signal; trigger handler reads with exclusive bus/held CS or plain SPI read for external triggers.

State and persistence: persistent state is per-channel PGA/data-rate arrays, optional trigger/IRQ, and SPI message buffers. Hardware state persists in the last written config: one-shot idle or continuous selected channel, data rate, PGA, temp mode, and pull-up/NOP validity bits.

Dependencies and integration: depends on SPI, optional GPIO descriptor and IRQ, IIO trigger/buffer APIs, one-hot scan validation, bitfield helpers, and OF/SPI IDs for ADS1018 and ADS1118.

Risks: DRDY line handling requires holding chip select and locking the SPI controller, so trigger enable/disable must be balanced. IRQ handler checks GPIO level to filter interrupts caused by SPI transfers. Direct reads always use the maximum data-rate delay, independent of per-channel configured rate. Only one channel can be buffered at a time.

Test signals: ADS1018 and ADS1118 gain/data-rate tables, voltage and temperature raw/scale reads, scale and sample-frequency writes/available lists, one-hot scan validation, continuous buffer capture with own and external triggers, DRDY GPIO/SPI IRQ paths, bus lock balancing, and postdisable one-shot config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1018.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1100.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1100.c

Purpose: I2C IIO driver for the single-channel ADS1100/ADS1000 ADC. It provides raw reads, gain-derived scale, sample-frequency control where supported, vdd regulator management, and runtime PM autosuspend.

Important APIs/types/functions: `struct ads1100_data` stores I2C client, vdd regulator, mutex, available scale table, cached config byte, and a flag for data-rate support. Important functions are `ads1100_set_config_bits()`, `ads1100_get_adc_result()`, scale/data-rate setters, availability/read/write callbacks, setup, cleanup actions, probe, and runtime PM callbacks.

Control flow: probe enables vdd, writes continuous 8 SPS setup, reads back conversion/config bytes to cache config and detect ADS1100 data-rate support, registers cleanup to return to single-shot and disable regulator, computes available scales from vdd, enables runtime PM, and registers IIO. Raw read claims direct mode, runtime-resumes, receives the 16-bit conversion, autosuspends, left-aligns the value according to resolution implied by data rate, and sign-extends. Scale writes convert requested fractional scale into PGA gain bits; sample-frequency writes update DR bits only if the chip supports them.

State and persistence: persistent state is cached config, gain/data-rate bits, vdd regulator state, scale table, and data-rate capability. Hardware state persists in the one-byte config register and continuous versus single-shot mode. Runtime suspend powers down conversion and disables vdd; resume re-enables vdd and writes continuous mode.

Dependencies and integration: depends on I2C master send/recv, regulator `vdd`, runtime PM, IIO direct callbacks and available-list ABI, firmware match IDs, and cleanup guard mutex style.

Risks: ADS1000-like devices may not support data-rate changes and are detected by readback behavior. Scale-setting arithmetic assumes vdd between 2.7 V and 5 V and scale below 1. Runtime power cycling relies on cached config being rewritten when continuous mode changes. `ads1100_set_config_bits()` treats successful `i2c_master_send()` byte counts as success without checking exact count.

Test signals: ADS1100 and ADS1000 probing, data-rate capability detection, raw reads at each data rate, scale available list from vdd, gain writes, runtime suspend/resume regulator transitions, single-shot cleanup on detach, and I2C error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1119.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1119.c

Purpose: I2C IIO driver for TI ADS1119. It supports firmware-described single-ended or limited differential channels, per-channel gain and data-rate controls, internal or external reference selection, direct single conversions including offset calibration reads, optional DRDY IRQ/trigger, buffered one-hot continuous capture, debugfs register access, reset GPIO, and runtime powerdown.

Important APIs/types/functions: `struct ads1119_state` stores completion, client, reset GPIO, optional trigger, per-channel configs, cached config, and vref. Important functions are `ads1119_upd_cfg_reg()`, `ads1119_reset()`, `ads1119_configure_channel()`, data-ready polling/reading, `ads1119_single_conversion()`, raw read/write/available callbacks, debugfs access, buffer setup ops, IRQ and trigger handlers, channel allocation, probe, and runtime suspend.

Control flow: probe enables AVDD/DVDD, obtains optional external vref or uses internal 2.048 V, gets reset GPIO, builds channels from child `single-channel` or `diff-channels` properties, installs triggered buffer, optionally requests IRQ and registers an own trigger, resets and initializes vref selection, enables runtime PM, registers powerdown cleanup, and registers IIO. Direct raw/offset reads claim direct mode, runtime-resume, configure mux/gain/data rate, optionally use shorted-input mux for offset, send START/SYNC, wait by DRDY completion or polling status, read swapped conversion data, sign-extend, and autosuspend. Buffered capture switches to continuous mode for one active channel, starts conversions, then reads data on trigger.

State and persistence: persistent state is cached config register, channel mux/gain/data-rate table, vref microvolts, completion, trigger, and reset method. Hardware state includes config register fields, conversion mode, selected mux/gain/rate, vref source, and powerdown state.

Dependencies and integration: depends on I2C SMBus byte/word commands, regulators `avdd`, `dvdd`, optional `vref`, optional reset GPIO, optional IRQ, IIO triggers/buffers/debugfs, runtime PM, and firmware child-node channel descriptions.

Risks: differential mapping supports only AIN0-AIN1, AIN1-AIN2, and AIN2-AIN3. If no IRQ is present, polling timeout is based on data rate and maximum DRDY timeout. The cached config must remain synchronized with debugfs writes, but debugfs writes do not update `cached_config`. Buffer preenable sets continuous mode before runtime resume; failures can leave mode changed.

Test signals: single-ended and differential child-node parsing, too-many/invalid channels, internal and external vref paths, reset GPIO and command reset, raw and offset conversions with IRQ and polling, gain/data-rate writes and available lists, one-hot buffered capture, own trigger IRQ behavior, debugfs register reads/writes, runtime powerdown, and timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1119.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads124s08.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads124s08.c

Purpose: SPI IIO driver for TI ADS124S06/ADS124S08 delta-sigma ADCs. It exposes 6 or 12 voltage channels, performs direct raw reads by programming the input mux and starting/stopping conversion, and supports triggered buffering over active channels.

Important APIs/types/functions: `struct ads124s_private` stores chip info, optional reset GPIO, SPI device, mutex, aligned scan buffer, and shared command/data buffer. Core functions are `ads124s_write_cmd()`, `ads124s_write_reg()`, `ads124s_reset()`, `ads124s_read()`, `ads124s_read_raw()`, trigger handler, and probe.

Control flow: probe allocates IIO, gets optional reset GPIO, selects chip info from SPI ID, initializes mutex, sets direct-mode channel table, installs triggered buffer support, resets the chip by GPIO or RESET command, and registers IIO. Direct raw read locks, writes `INPUT_MUX` to the requested channel, sends START, sends RDATA with NOP clocks through a two-transfer SPI sequence, reads a 24-bit big-endian result, sends STOP, returns the value, and unlocks. Triggered buffer repeats mux/start/read/stop for each active scan channel and pushes the aligned buffer with timestamp.

State and persistence: persistent state is chip variant, optional reset line, mutex, and command buffer. Hardware state includes selected input mux and conversion start/stop state; most configuration registers are otherwise left at reset defaults.

Dependencies and integration: depends on SPI, optional GPIO reset, unaligned big-endian helpers, IIO direct and triggered-buffer APIs, and OF/SPI IDs for ADS124S06/S08.

Risks: channel scan metadata declares unsigned 32-bit samples while `ads124s_read()` returns a 24-bit value without sign extension, which may not match bipolar ADC expectations. Trigger handler does not hold the mutex used by direct reads, relying on IIO mode exclusion. It does not wait on DRDY, so conversion timing depends on command/read behavior and device defaults. Optional reset GPIO errors are logged as info but not returned.

Test signals: ADS124S06 and ADS124S08 channel counts, raw reads across all channels, reset GPIO and command reset paths, mux register write failures, start/read/stop error handling, triggered buffer with multiple active channels, sign/format validation against hardware, and concurrent direct/buffer exclusion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads124s08.c -->
