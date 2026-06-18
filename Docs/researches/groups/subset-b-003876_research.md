# subset-b-003876 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79124.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79124.c

## Purpose
This is the I2C IIO ADC and GPIO-output driver for the ROHM BD79124, an 8-channel 12-bit ADC whose pins can be muxed between ADC inputs and GPO outputs. It supports direct raw voltage reads, scale reporting from the `vdd` regulator, optional threshold events when an IRQ is wired, and GPIO registration for channels not claimed as ADC channels in firmware.

## Important APIs, types, and functions
The central state is `struct bd79124_data`, which owns the regmap, regulator-derived full-scale voltage, cached threshold limits, event monitor/suppression bitmaps, a delayed work item, mutex, and `gpio_chip`. The regmap uses 16-bit register addresses, 8-bit values, Maple cache, volatile result/status registers, and precious event flag registers. IIO entry points are `bd79124_read_raw()`, event config/value callbacks, and the `bd79124_info` table. GPIO integration is via `bd79124gpo_chip`, `bd79124gpo_set()`, `bd79124gpo_set_multiple()`, and `bd79124_init_valid_mask()`.

## Control flow
`bd79124_probe()` allocates the IIO device, initializes regmap and regulators, chooses event-capable or no-IRQ channel templates, allocates firmware-described channel specs with `devm_iio_adc_device_alloc_chaninfo_se()`, initializes hardware defaults, requests a threaded threshold IRQ when available, registers IIO, then registers any unused pins as GPOs. Raw reads lock the device, force auto-conversion mode, replace the auto-channel sequencer with a single channel, wait the documented conversion time, read the recent-result register pair, and restore the previous sequencer mask.

## State and persistence
Hardware state is mostly volatile but mirrored in regmap cache. Threshold values are cached in `alarm_r_limit[]` and `alarm_f_limit[]` because disabling one direction is implemented by writing an extreme threshold rather than a hardware enable bit. `alarm_monitored[]` tracks enabled event directions and `alarm_suppressed[]` tracks one-second rate-limit suppression. GPIO valid pins are captured once from the ADC channel allocation.

## Dependencies and integration points
The driver depends on I2C, regmap, regulator supplies `vdd` and `iovdd`, generic IIO ADC channel firmware helpers, IIO events, optional IRQ, and gpiolib. Firmware channel children decide which pins are ADCs; all remaining pins become GPIO outputs. IIO events are pushed with `iio_push_event()` from the threaded IRQ path.

## Risks
Event logic is subtle because the chip keeps IRQ asserted while a threshold condition persists, so suppression rewrites limits and delayed work later restores them. A notable risk is in `bd79124_enable_event()`: the rising-direction branch selects `data->alarm_f_limit[channel]` instead of the rising-limit cache before writing the high-limit register, which looks like a copy/paste bug. `bd79124gpo_set_multiple()` compares `all_gpos ^ *mask`, which rejects masks that are not exactly equal to the PINCFG state rather than checking only requested bits; this is intentional per the comment but should be regression-tested with partial masks. Raw reads temporarily disturb the auto-channel set, so restore failure can disable alarm monitoring.

## Test signals
Useful tests are probe with and without IRQ, firmware channel subsets that leave no GPIOs, all GPIOs, and mixed ADC/GPO pins, direct raw reads while alarms are enabled, threshold enable/disable and hysteresis sysfs paths, repeated threshold IRQ storm suppression and re-enable timing, regulator scale reporting, and `set_multiple()` with valid and invalid GPIO masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rohm-bd79124.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rtq6056.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rtq6056.c

## Purpose
This I2C IIO driver supports Richtek RTQ6056 and RTQ6059 power monitors. It exposes shunt voltage, bus voltage, power, and current channels, including raw values, scales, sample frequency, oversampling ratio, a shunt-resistor sysfs attribute, and triggered-buffer capture.

## Important APIs, types, and functions
`struct rtq6056_priv` stores the regmap, per-bitfield regmap fields, device variant data, shunt resistor, conversion times, and averaging state. `struct richtek_dev_data` abstracts RTQ6056 versus RTQ6059 differences: config defaults, bitfield layout, bus-voltage shift, calibration coefficient, averaging tables, channel table, and scale/averaging callbacks. Main IIO operations are `rtq6056_adc_read_raw()`, `rtq6056_adc_read_avail()`, `rtq6056_adc_write_raw()`, `rtq6056_adc_read_label()`, and `rtq6056_buffer_trigger_handler()`.

## Control flow
`rtq6056_probe()` checks SMBus word support, selects match data, initializes big-endian 16-bit regmap, verifies the manufacturer ID, allocates regmap fields, writes the variant default config, enables runtime PM, configures the shunt resistor from firmware or a 2000 uOhm default, sets up a triggered buffer, and registers IIO. Direct raw reads resume runtime PM, read the selected register, apply sign extension or bus-voltage shift, and autosuspend again. Writes are direct-mode guarded and adjust sampling frequency or averaging. Runtime suspend writes operation mode 0; resume restores continuous all-on mode and sleeps for the computed conversion latency.

## State and persistence
The driver persists user-visible sampling state in `vshuntct_us`, `vbusct_us`, and `avg_sample`, and persists shunt calibration by writing `RTQ6056_REG_CALIBRATION`. Register state can be lost on shutdown/suspend, but runtime resume only restores operating mode, not the full config; regmap is not configured with a cache here.

## Dependencies and integration points
It integrates with I2C SMBus, regmap, regmap-field, runtime PM, firmware property `shunt-resistor-micro-ohms`, IIO sysfs, and IIO triggered buffers. Device-tree compatibles select `richtek,rtq6056` or `richtek,rtq6059`.

## Risks
Runtime PM calls use `pm_runtime_get_sync()` without checking the return value in direct read and buffer paths, so failed resume could still attempt register IO. RTQ6059 fixed sample frequency rejects sample-frequency writes but still exposes sample-frequency reads from cached default timing. The shunt resistor calibration divides by user-provided resistance, with nonpositive values rejected but very large values potentially producing zero calibration. Triggered-buffer reads index `rtq6056_channels[bit]` rather than variant channels, but the channel order/address layout matches both variants.

## Test signals
Test vendor-ID rejection, both compatibles, sample-frequency and oversampling available lists, direct-mode write exclusion while buffered capture is active, shunt-resistor parsing and calibration register writes, runtime suspend/resume timing, sign extension on shunt/current, RTQ6059 bus-voltage shift, and triggered-buffer scan ordering with timestamps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rtq6056.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzg2l_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rzg2l_adc.c

## Purpose
This platform IIO driver supports Renesas RZ/G2L-family ADCs, including the RZ/G2L 8-channel variant and RZ/G3S 9-channel variant with a temperature input. It provides direct raw conversion reads and channel labels.

## Important APIs, types, and functions
`struct rzg2l_adc_hw_params` captures variant-specific sampling-period masks, default sampling values, interrupt masks, number of channels, comparator defaults, and optional ADIVC clock divider support. `struct rzg2l_adc` holds MMIO base, reset controls, parsed channel data, completion, mutex, and last conversion values. Key routines are `rzg2l_adc_conversion_setup()`, `rzg2l_adc_conversion()`, `rzg2l_adc_read_raw()`, `rzg2l_adc_isr()`, `rzg2l_adc_hw_init()`, and runtime/system PM callbacks.

## Control flow
Probe selects hardware parameters from the compatible, parses firmware channel children with `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, deasserts resets, enables runtime PM, initializes hardware, requests the conversion IRQ, and registers IIO. A raw read resumes the device, configures software-trigger select mode for one channel, programs channel selection and sampling period, enables channel-select-error and conversion interrupts, starts conversion, waits for completion, stops conversion, and returns `last_val[channel]` filled by the ISR.

## State and persistence
The driver stores only transient conversion results in `last_val[]`; most hardware configuration is reconstructed on each conversion or in `rzg2l_adc_hw_init()`. Runtime suspend powers down the analog block with `PWDWNB`; system suspend force-suspends PM and asserts resets. Resume deasserts resets, force-resumes PM, and reinitializes ADC registers.

## Dependencies and integration points
Dependencies include platform MMIO, reset controls named `adrst-n` and `presetn`, runtime PM, IRQ completion, IIO ADC firmware helpers, and device-tree compatibles `renesas,rzg2l-adc` and `renesas,r9a08g045-adc`.

## Risks
The timeout is extremely short (`usecs_to_jiffies(4)`), so low HZ configurations can make timeout semantics coarse and hardware latency assumptions fragile. Conversion setup returns `-EBUSY` if hardware reports busy. Channel-select error interrupts are acknowledged but do not complete the waiting conversion, so the caller times out. Since only direct reads are implemented, no buffered path exercises scan ordering.

## Test signals
Exercise probe on both variants, firmware channel validation above max channel count, voltage and temperature labels, raw read success, busy ADC behavior, timeout path that masks interrupts and stops conversion, reset/system PM resume reinitialization, and ADIVC programming only on variants that support it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzg2l_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzn1-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rzn1-adc.c

## Purpose
This platform IIO driver supports the Renesas RZ/N1 ADC controller, which can use ADC1, ADC2, or both internal ADC cores depending on which AVDD and VREF supplies are described. It exposes direct 12-bit raw voltage readings and scale based on each core's VREF.

## Important APIs, types, and functions
`struct rzn1_adc` owns the MMIO base, mutex, device pointer, and per-core VREF millivolt values. Static channel tables represent ADC1-only, ADC2-only, and combined ADC1+ADC2 layouts; scale is shared by type when only one core is present and separate per channel when both cores are present. Core routines are `rzn1_adc_power()`, `rzn1_adc_vc_setup_conversion()`, `rzn1_adc_read_raw_ch()`, `rzn1_adc_get_vref_mV()`, `rzn1_adc_set_iio_dev_channels()`, and `rzn1_adc_core_get_regulators()`.

## Control flow
Probe allocates IIO state, initializes the mutex, maps registers, enables `pclk` and `adc` clocks, probes optional regulator pairs for ADC1 and ADC2, chooses the IIO channel table, enables autosuspended runtime PM, and registers the device. A raw read maps IIO channels 0-7 to ADC1 VC channels and 8-15 to ADC2, resumes runtime PM with cleanup-guard helpers, configures a virtual channel, forces conversion, polls for hardware to clear the force bit, reads the selected data register, and returns the result.

## State and persistence
Persistent state is minimal: VREF values and selected channel table are fixed at probe. Hardware power-down state is controlled through runtime PM by writing `RZN1_ADC_CONFIG_ADC_POWER_DOWN` and polling `ADC_BUSY`. Virtual-channel setup is rewritten for each read.

## Dependencies and integration points
The driver integrates with platform MMIO, clocks named `pclk` and `adc`, optional regulators `adc1-avdd`, `adc1-vref`, `adc2-avdd`, and `adc2-vref`, runtime PM, and the IIO direct-mode API. The compatible is `renesas,rzn1-adc`.

## Risks
`rzn1_adc_read_raw_ch()` assigns `ret = IIO_VAL_INT` but returns `0`, relying on the caller to convert success to `IIO_VAL_INT`; this is harmless but misleading. If only one regulator of a core pair exists, the core is silently treated as unused after enabling the available AVDD, which should be checked against board expectations. Conversion polling uses a 100 us worst-case estimate with atomic polling, so clock assumptions matter.

## Test signals
Test all regulator-presence combinations, no-core probe failure, per-core scale values, channel mapping for ADC1 and ADC2, virtual-channel busy handling, conversion timeout and forced stop path, runtime PM power transitions, and invalid channel guard behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzn1-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzt2h_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/rzt2h_adc.c

## Purpose
This platform IIO driver supports the Renesas RZ/T2H and RZ/N2H ADC. It exposes firmware-selected voltage channels with raw reads and a fixed 1.8 V, 12-bit scale.

## Important APIs, types, and functions
`struct rzt2h_adc` contains MMIO base, device pointer, completion, mutex, parsed channels, and channel count. Main routines are `rzt2h_adc_read_single()`, `rzt2h_adc_calibrate()`, `rzt2h_adc_read_raw()`, `rzt2h_adc_parse_properties()`, and the runtime resume callback.

## Control flow
Probe parses channel child nodes through `devm_iio_adc_device_alloc_chaninfo_se()`, maps registers, enables runtime PM with autosuspend, requests the named `adi` IRQ, initializes IIO metadata, and registers the device. A raw read resumes runtime PM, locks the ADC, selects exactly one channel in `ADANSA0`, starts single conversion with interrupt enable, waits for completion for about one microsecond, reads the channel result register, stops conversion, unlocks, and autosuspends.

## State and persistence
The driver has no cached measurement state. It recalibrates on every runtime resume after a required post-module-stop delay. Calibration sets the calibration bit, polls ready, clears calibration, and rejects calibration-error status.

## Dependencies and integration points
It depends on platform MMIO, an IRQ named `adi`, runtime PM, IIO ADC firmware channel helpers, and `renesas,r9a09g077-adc` device-tree binding. There is no regulator or clock handling in this file, so those resources are assumed managed outside or not required by this binding.

## Risks
The conversion wait is based on a sub-microsecond datasheet value rounded to `usecs_to_jiffies(1)`, which may be too coarse or too short depending on scheduling and HZ. `max_channels` is computed during parsing but not used for validation beyond storage, so invalid high channel numbers rely on the helper's range. Frequent autosuspend can trigger repeated calibration cost.

## Test signals
Test valid and invalid firmware channels, raw reads for multiple channels under concurrency, timeout path cleanup, calibration timeout and error handling, IRQ completion, runtime resume recalibration, fixed scale reporting, and autosuspend behavior under repeated reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/rzt2h_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sc27xx_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/sc27xx_adc.c

## Purpose
This platform IIO driver supports Spreadtrum/Unisoc SC27xx PMIC ADC blocks. It exposes 32 voltage channels, raw or processed readings depending on channel, user-writable scale selector, and variant-specific calibration and voltage-ratio conversion.

## Important APIs, types, and functions
`struct sc27xx_adc_data` stores PMIC regmap, base offset, hardware spinlock, mutex, optional VREF regulator, per-channel scale array, and variant data. `struct sc27xx_adc_variant_data` provides module/clock register offsets, scale bit layout, calibration graphs, per-channel scale initialization, ratio callback, and special VREF behavior. Core functions are `sc27xx_adc_read()`, `sc27xx_adc_read_processed()`, `sc27xx_adc_convert_volt()`, `sc27xx_adc_scale_calibration()`, `sc27xx_adc_enable()`, and `sc27xx_adc_probe()`.

## Control flow
Probe obtains the parent PMIC regmap, local `reg` base, IRQ number, hardware spinlock, optional `vref` regulator for variants that need it, initializes default channel scales, enables module and clocks, calibrates big and small scale graphs from nvmem cells, registers cleanup, and registers the IIO device. Reads take a mutex, then `sc27xx_adc_read()` takes the hardware spinlock, optionally raises VREF to 3.5 V for SC2721 channels 30/31, enables ADC, clears IRQ, programs channel and scale, starts a 12-bit one-sample conversion, polls raw IRQ status, reads data, disables ADC, restores VREF, and unlocks. Processed reads convert raw ADC code through calibrated linear graphs and per-channel ratios.

## State and persistence
`channel_scale[]` is mutable through `write_raw()` and persists until driver unload. Calibration mutates the file-scope `big_scale_graph` and `small_scale_graph`, so graph values are shared process-wide after probe. Hardware is enabled for each read but PMIC module clocks remain enabled until devm cleanup.

## Dependencies and integration points
The driver integrates with parent PMIC regmap, nvmem calibration cells `big_scale_calib` and `small_scale_calib`, hardware spinlocks for cross-subsystem arbitration, optional VREF regulator, and compatibles for SC2731, SC2730, SC2721, and SC2720.

## Risks
Calibration cell read errors are not distinguished from valid zero data inside `sc27xx_adc_scale_calibration()`, so missing or failed nvmem may silently alter graph values. Shared global calibration graphs can be problematic if multiple variants probe with different calibration data. `write_raw()` accepts any scale integer and does not validate it against the variant mask. IRQ is fetched but conversions use polling, so interrupt wiring may not be exercised.

## Test signals
Test all compatibles, nvmem present/missing/error cases, processed voltage math for channels 1 and 5 plus ratio-scaled channels, SC2721 VREF switching on channels 30/31, hardware spinlock timeout, scale writes beyond valid range, ADC poll timeout cleanup, and module/clock cleanup on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sc27xx_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sd_adc_modulator.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/sd_adc_modulator.c

## Purpose
This is a generic sigma-delta modulator representation. It can either register a legacy one-channel hardware-buffer IIO voltage device or, when `#io-backend-cells` is present, register as an IIO backend for another frontend ADC/DFSDM-style consumer.

## Important APIs, types, and functions
`struct iio_sd_backend_priv` stores optional VREF regulator state and cached millivolt scale. Backend operations are `iio_sd_mod_enable()`, `iio_sd_mod_disable()`, and `iio_sd_mod_read()`, exported through `sd_backend_ops` and `sd_backend_info`. Legacy registration uses `iio_sd_mod_register()` with a one-bit unsigned voltage channel.

## Control flow
`iio_sd_mod_probe()` checks whether the firmware node declares backend cells. Without backend cells, it allocates and registers a legacy IIO device with one hardware-buffer channel. With backend cells, it allocates backend private data, obtains optional `vref`, caches the regulator voltage without enabling it, and registers the backend. Backend enable/disable toggles the optional regulator; backend `read_raw` returns scale or zero offset.

## State and persistence
The only persistent state is the cached VREF millivolt value and regulator pointer. Regulator power is intentionally not enabled at probe and is controlled by backend lifecycle callbacks. The legacy path has no private state.

## Dependencies and integration points
It depends on the IIO backend framework, regulator consumer API, platform device matching, and compatibles `sd-modulator` and `ads1201`. It imports the `IIO_BACKEND` namespace. In backend mode it is not the sampling engine; it supplies enable and scale/offset services to a consumer.

## Risks
If no VREF regulator is provided in backend mode, scale defaults to zero, which may be acceptable for board-specific consumers but is easy to misinterpret. The legacy `iio_info` is an empty declaration, so the legacy device is primarily a buffer endpoint and does not provide raw read callbacks. The source uses trailing semicolons after function definitions, harmless but unusual.

## Test signals
Test backend and legacy probe paths, optional VREF absent and present, regulator enable/disable balancing, scale and offset reads from a backend consumer, compatible fallback behavior for `ads1201`, and cleanup when regulator voltage read fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sd_adc_modulator.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sophgo-cv1800b-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/sophgo-cv1800b-adc.c

## Purpose
This platform IIO driver supports the Sophgo CV1800B SAR ADC. It exposes three voltage channels with raw conversion, fixed 3.3 V 12-bit scale, and computed sample frequency.

## Important APIs, types, and functions
`struct cv1800b_adc` stores completion, MMIO registers, mutex, clock, and optional IRQ. The key paths are `cv1800b_adc_start_measurement()`, `cv1800b_adc_wait()`, `cv1800b_adc_read_raw()`, `cv1800b_adc_interrupt_handler()`, and `cv1800b_adc_probe()`.

## Control flow
Probe allocates IIO state, enables the clock, maps registers, optionally requests an IRQ and enables ADC interrupts, initializes the mutex, programs startup/sample/clock-divider/compare cycle settings, and registers IIO. A raw read locks the ADC, clears the control register, starts one selected channel, waits either by polling busy status or by completion from IRQ, reads the channel result register, unlocks, checks the valid bit, and returns the 12-bit sample.

## State and persistence
Cycle timing configuration is programmed at probe and then read back for sample-frequency reporting. There is no runtime PM or cached conversion state. Completion is used only when an IRQ is available; otherwise polling is used.

## Dependencies and integration points
The driver depends on a platform MMIO resource, an enabled clock, optional IRQ, IIO direct mode, and compatible `sophgo,cv1800b-saradc`.

## Risks
There is no runtime PM or explicit ADC disable after conversion beyond writing control for the next read. If an IRQ is present, the code does not reinitialize the completion before each conversion, so a stale completion could allow an immediate read of an old or invalid sample after the first interrupt. Sample frequency calculation divides by the programmed cycle fields but does not guard against a zero clock rate.

## Test signals
Test both IRQ and polling modes, repeated IRQ-backed reads for stale completion behavior, invalid result bit handling, sample-frequency math from cycle settings, clock failure, timeout handling, and concurrent reads serialized by the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/sophgo-cv1800b-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/spear_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/spear_adc.c

## Purpose
This platform IIO driver supports the ST SPEAr ADC, primarily `st,spear600-adc`, with eight voltage channels, direct raw reads, scale reporting, and configurable sampling frequency.

## Important APIs, types, and functions
`struct spear_adc_state` stores register layout pointers for SPEAr3xx and SPEAr6xx views, clock, completion, mutex, current clock, sampling frequency, average sample count, VREF selection, and last value. Register abstraction helpers include `spear_adc_set_status()`, `spear_adc_set_clk()`, `spear_adc_set_scanrate()`, and `spear_adc_get_average()`. IIO operations are `spear_adc_read_raw()` and `spear_adc_write_raw()`.

## Control flow
Probe maps the register block, enables the clock, requests an IRQ, reads required `sampling-frequency` and optional `average-samples` and `vref-external` properties, resets/configures ADC registers, initializes completion, and registers IIO. A raw read locks the device, builds a status word containing channel, averaging, start, enable, and VREF selection, writes it, waits for ISR completion, returns the ISR-captured average value, and unlocks. Sampling-frequency writes validate the requested range and reprogram clock high/low counts.

## State and persistence
Sampling frequency and current derived ADC clock are cached in `sampling_freq` and `current_clk`. Average samples and external VREF are firmware-defined. Last conversion result is stored in `value` by the ISR. Hardware configuration is set at probe and adjusted only by sampling-frequency writes.

## Dependencies and integration points
It depends on platform MMIO, clock, IRQ, firmware properties, and IIO direct mode. The source keeps alternate register structs for different SPEAr layouts, but the match table only lists `st,spear600-adc`.

## Risks
`wait_for_completion()` in `spear_adc_read_raw()` has no timeout, so a missed IRQ can block indefinitely. Completion is initialized once and not reinitialized per conversion, which risks stale completions on repeated reads. `spear_adc_set_status()` always writes through the SPEAr6xx pointer, while some helpers branch by compatible for readback; this is acceptable for current match data but fragile if older compatibles are reintroduced.

## Test signals
Test missing required sampling-frequency property, sample-frequency writes at min/max/out of range, repeated raw reads, IRQ failure or missing completion behavior, internal versus external VREF scale, average-samples property effects, and register layout assumptions for compatible additions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/spear_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.c

## Purpose
This platform driver is the parent/core for STM32 ADC blocks. It owns shared registers, clocks, regulators, analog switch supplies, common IRQ demultiplexing, runtime PM, and child-device population for individual STM32 ADC IIO instances.

## Important APIs, types, and functions
`struct stm32_adc_priv` contains shared clock/regulator/syscfg resources, IRQ domain, compatible config, common IIO data, and saved common-control register state. `struct stm32_adc_priv_cfg` describes per-family common registers, clock selection, max rate, identification, syscfg capabilities, IRQ count, and ADC count. Important functions include `stm32f4_adc_clk_sel()`, `stm32h7_adc_clk_sel()`, `stm32_adc_irq_handler()`, `stm32_adc_irq_probe()`, `stm32_adc_core_hw_start()`, `stm32_adc_core_hw_stop()`, `stm32_adc_probe_identification()`, and runtime PM callbacks.

## Control flow
Probe maps the common register resource, obtains `vdda`, `vref`, optional `adc` and `bus` clocks, probes optional syscfg/booster/vdd analog-switch support, enables runtime PM, starts shared hardware, validates IP identification when required, reads VREF millivolts, selects a common ADC clock under the compatible-specific maximum, creates an IRQ domain and chained handlers, then populates child ADC nodes. Remove depopulates children, removes IRQ mappings, stops hardware, and disables PM.

## State and persistence
The core persists `common.rate`, `common.vref_mv`, `common.phys_base`, `nb_adc_max`, and `ccr_bak`. Runtime suspend backs up CCR, disables clocks/regulators/switch supplies, and runtime resume restores supplies, clocks, and CCR. Child drivers access `struct stm32_adc_common` through parent driver data.

## Dependencies and integration points
It integrates with regulators `vdda`, `vref`, optional `vdd` and `booster`, optional clocks `adc` and `bus`, syscon phandle `st,syscfg`, irqdomain/chained IRQ, runtime PM, and Open Firmware child population. Compatibles cover STM32F4, STM32H7, STM32MP1, and STM32MP13 ADC cores.

## Risks
Clock selection has strict duty-cycle and rate assumptions; missing mandatory clocks fail differently by family. Analog switch supply selection depends on measured voltages and optional syscfg/booster resources. IRQ demux only forwards EOC when the child has EOC interrupt enabled, so DMA users rely on hardware EOC clearing. Runtime PM failures can cascade to all children.

## Test signals
Test each compatible's clock-selection path, `st,max-clk-rate-hz` clamping, regulator failure unwinds, syscfg/booster/vdd combinations below and above 2.7 V, IPID and child-count validation, chained IRQ forwarding for EOC/OVR, runtime suspend/resume CCR restore, and child population/depopulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.h -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.h

## Purpose
This header defines the shared register map, bitfields, constants, and common data structure used by the STM32 ADC core parent and STM32 ADC child IIO driver.

## Important APIs, types, and functions
It defines the common block layout: ADC1 at offset 0, ADC2 at `0x100`, ADC3 at `0x200`, and common registers at `0x300`. It provides STM32F4, STM32H7, STM32MP1, and STM32MP13 register offsets and bit masks for status, interrupt enable, control, trigger selection, resolution, DMA mode, calibration, oversampling, common CCR/CSR, option registers, and hardware identification registers. The only type exported is `struct stm32_adc_common`, containing common MMIO base, physical base, analog clock rate, VREF millivolts, and a spinlock for common registers.

## Control flow
The header has no executable flow. Its definitions enable the parent core to configure shared clocks/IRQs/supplies and the child driver to program per-instance conversion, calibration, scan, oversampling, and internal-channel controls using family-specific register specs.

## State and persistence
`struct stm32_adc_common` is the shared runtime state passed from parent to child through platform driver data. Its `rate` and `vref_mv` values are established by the core and consumed by the child for sampling-time and scale calculations. Its spinlock serializes read-modify-write access to common registers such as CCR.

## Dependencies and integration points
The header depends only on kernel bitfield and bit macros. It is included by `stm32-adc-core.c` and `stm32-adc.c`, making it the contract between the parent MFD-like ADC core and individual ADC instance drivers.

## Risks
Because register masks encode multiple SoC generations, a wrong compatible-to-regspec pairing can write valid-looking bits to the wrong offset. Shared constants such as `STM32H7_DMNGT_MASK` intentionally overlap STM32MP13 DMA bits in the child driver, so future edits must preserve that compatibility assumption. `STM32_ADC_MAX_ADCS` constrains IRQ-domain and offset arrays to three instances.

## Test signals
Test coverage is indirect: build all STM32 ADC compatibles, verify register-spec offsets against datasheets, exercise common lock use under multiple child ADCs, and validate scale/sampling computations that consume `struct stm32_adc_common`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc.c

## Purpose
This is the STM32 ADC child IIO driver for individual ADC instances below the STM32 ADC core. It supports direct conversions, hardware-triggered buffered capture, optional DMA, differential inputs, internal channels, sampling-time setup, oversampling, debugfs register access, calibration, and runtime/system PM across STM32F4, STM32H7, STM32MP1, and STM32MP13 families.

## Important APIs, types, and functions
`struct stm32_adc` is the main state object: common parent data, instance offset, config, completion, PIO buffer, clock, IRQ, spinlock, conversion counts, resolution, trigger polarity, DMA resources, channel preselection/differential masks, sampling register images, calibration data, internal-channel map, and oversampling index. `struct stm32_adc_cfg` and `struct stm32_adc_regspec` provide family-specific operations and register layout. Key functions include `stm32_adc_single_conv()`, `stm32_adc_read_raw()`, `stm32_adc_write_raw()`, `stm32_adc_conf_scan_seq()`, `stm32_adc_set_trig()`, ISR/threaded ISR pair, DMA buffer callbacks, firmware channel parsers, `stm32h7_adc_prepare()`, self-calibration helpers, and PM callbacks.

## Control flow
Probe obtains parent common data, reads the instance `reg` offset, maps the per-instance IRQ supplied by the parent IRQ domain, obtains the optional per-instance clock, selects resolution, optionally requests DMA, parses either generic child channel nodes or legacy `st,adc-channels` properties, sets up triggered buffers, enables runtime PM, starts hardware, registers IIO, and creates calibration debugfs files. Direct raw reads claim direct mode, resume the parent device, program sampling registers and a one-channel sequence, disable external trigger detection, enable EOC IRQ, start conversion, wait for completion, stop conversion, disable IRQ, autosuspend, and return the sample. Buffered mode updates scan sequence, configures trigger mux, starts DMA or PIO IRQ collection, and pushes samples through IIO buffers.

## State and persistence
Resolution, oversampling index, trigger polarity, sampling-time register images, internal-channel enables, calibration factors, PCSEL/DIFSEL masks, and DMA buffers persist for the life of the device. Runtime suspend stops hardware and may power down/calibrate again on resume depending on family. H7-like variants save or restore linear calibration factors to avoid repeating full linear calibration after the first successful run.

## Dependencies and integration points
The driver depends on the STM32 ADC core's `struct stm32_adc_common`, IIO core, IIO triggers, STM32 timer/LPTIM trigger helpers, DMAengine, runtime PM, debugfs, nvmem cell `vrefint`, firmware channel descriptions, and family compatibles. It uses parent VREF for scale and parent physical base for DMA source address.

## Risks
This is a high-state driver with many SoC-specific register layouts. Risks include stale or missing `vrefint` calibration causing internal VREF channel omission, DMA residue/accounting errors in cyclic buffers, overrun recovery requiring buffer restart, trigger-name matching only for STM32 timer/LPTIM triggers, complex calibration restore paths, and raw processed VREF math dividing by the just-read sample without checking zero. Firmware parser behavior differs between legacy and generic bindings, so channel ordering and sampling times need careful compatibility testing.

## Test signals
Test each compatible's probe, direct raw reads, processed VREFINT with valid/missing/zero nvmem, differential scale/offset, oversampling available/write paths, trigger polarity and timer-trigger validation, PIO buffered mode with timestamps, DMA cyclic mode and watermarks, overrun threaded recovery, runtime and system suspend/resume with active buffers, legacy and generic firmware channel parsing, debugfs register access, and calibration save/restore on H7/MP1.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/stm32-adc.c -->
