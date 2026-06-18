# subset-b-003872 research

Grouped research for Linux IIO ADC sources under `sources/distributed-fs/ceph-client/drivers/iio/adc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ep93xx_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ep93xx_adc.c

## Purpose
`ep93xx_adc.c` is a direct-mode IIO voltage ADC driver for the Cirrus Logic EP93xx SoC ADC block. It exposes eight single-ended voltage channels with raw, scale, and offset attributes and deliberately polls conversion completion because reading the result register starts conversion and the hardware conversion-rate spacing makes IRQ mode impractical.

## Important APIs, types, and functions
- `struct ep93xx_adc_priv` stores the ADC clock, MMIO base, last selected channel, and a mutex that serializes channel switching and conversion.
- `ep93xx_adc_channels` defines the eight IIO voltage channels, including datasheet names for the touchscreen-style pins.
- `ep93xx_read_raw()` implements `IIO_CHAN_INFO_RAW`, `IIO_CHAN_INFO_OFFSET`, and `IIO_CHAN_INFO_SCALE`.
- `ep93xx_adc_probe()` allocates the IIO device, maps MMIO, gets and enables the clock, optionally programs the ADC clock from the parent, and registers the device.
- `ep93xx_adc_remove()` unregisters IIO and disables the clock.

## Control flow
Probe initializes `lastch` to `-1`, sets `INDIO_DIRECT_MODE`, assigns the fixed channel table, and enables the hardware clock. A raw read takes the mutex, switches channels only if needed, performs the software-lock write sequence with local IRQs disabled, waits for settling, triggers a conversion by reading `EP93XX_ADC_RESULT`, delays to stay under the maximum conversion rate, and then polls for `EP93XX_ADC_SDR` until a short timeout.

## State and persistence
The driver has no persistent storage. Runtime state is the selected channel cached in `lastch` and the clock/MMIO handles. Hardware state includes the switch register and ADC conversion engine. Scale and offset are fixed constants based on the expected 3.3 V supply and documented input range.

## Dependencies and integration points
This file integrates with the platform bus, device tree match `cirrus,ep9301-adc`, IIO direct mode, MMIO register access, the common clock framework, and high-resolution timer availability for conversion delays.

## Risks
- Channel switch unlock and write must be adjacent; interrupt masking is intentional.
- Without high-resolution timers the busy-wait delay path can consume a full CPU during back-to-back reads.
- The scale assumes a typical 3.3 V supply, not a regulator-measured reference.
- Timeout handling depends on jiffies after a fixed conversion delay, so timing regressions can be hardware-sensitive.

## Test signals
Build with the EP93xx ADC config, probe from DT, read all raw channels repeatedly, verify channel switching does not corrupt adjacent reads, and check scale/offset ABI values. Hardware tests should confirm maximum-rate reads do not trigger conversion timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ep93xx_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/exynos_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/exynos_adc.c

## Purpose
`exynos_adc.c` supports Samsung S3C, S5PV210, Exynos v1, Exynos v2, Exynos3250, Exynos4212/4412, and Exynos7 ADC blocks as direct-mode IIO voltage devices. It abstracts register-layout differences behind per-compatible callbacks for hardware init, shutdown, IRQ clearing, and conversion start.

## Important APIs, types, and functions
- `struct exynos_adc` stores variant data, MMIO base, optional PMU syscon regmap, clocks, IRQ, regulator, completion, result value, and a mutex.
- `struct exynos_adc_data` describes channel count, bit mask, clock/PHY needs, PMU offset, and operation callbacks.
- `exynos_adc_v1_init_hw()`, `exynos_adc_v2_init_hw()`, and `exynos_adc_exynos7_init_hw()` program prescalers, resolution, reset, interrupt enable, and optional ADC PHY power.
- `exynos_read_raw()` reports regulator-derived scale or starts a conversion and waits on `completion`.
- `exynos_adc_isr()` reads the result, clears the variant IRQ, and completes the conversion.
- Probe/remove and suspend/resume manage regulators, clocks, IRQ, IIO registration, and child device population.

## Control flow
Probe matches the DT compatible to an `exynos_adc_data`, maps registers, optionally finds `samsung,syscon-phandle`, gets `adc` and optional `sclk`, enables the `vdd` regulator, prepares/enables clocks, requests the IRQ, registers the IIO device, initializes hardware, and populates child nodes under the IIO device. A raw read serializes access with `lock`, reinitializes the completion, calls the variant `start_conv()`, waits up to 100 ms, and resets hardware on timeout.

## State and persistence
State is volatile: current conversion value, completion state, enabled clocks/regulator, PMU ADC PHY power, and configured ADC registers. There is no file-backed persistence. Suspend disables hardware and regulator power; resume re-enables and reinitializes the ADC.

## Dependencies and integration points
The driver uses platform devices, OF matching, IIO direct mode, Linux completions, IRQ handling, common clocks, regulator consumers, syscon/regmap for PMU PHY control, and `of_platform_populate()` for ADC child nodes such as touchscreen consumers.

## Risks
- `exynos_adc_get_data()` assumes an OF match exists; invalid binding paths can break probe.
- V1 and V2 register offsets overlap through macros, so callback/data mismatches would read or write the wrong registers.
- Resume returns immediately if clock enable fails after regulator enable, potentially leaving regulator enabled on the error path.
- Conversion timeout resets hardware while the mutex is held, which is correct but should be validated under IRQ loss.

## Test signals
Compile all Exynos/S3C variants, boot-test representative v1 and v2 SoCs, validate scale from `vdd`, read each exposed channel count per compatible, exercise suspend/resume, and test timeout behavior by masking IRQs or using fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/exynos_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/fsl-imx25-gcq.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/fsl-imx25-gcq.c

## Purpose
`fsl-imx25-gcq.c` is the IIO driver for the i.MX25 TSADC Generic Conversion Queue. It exposes eight voltage configurations for touchscreen and auxiliary inputs and lets firmware describe positive/negative references per configuration.

## Important APIs, types, and functions
- `struct mx25_gcq_priv` holds the regmap, completion, shared TSADC clock, IRQ, optional reference regulators, per-channel reference millivolts, and conversion mutex.
- `mx25_gcq_channels` defines channels `xp`, `yp`, `xn`, `yn`, `wiper`, and `inaux0..2`.
- `mx25_gcq_setup_cfgs()` initializes queue configuration registers and parses child-node `reg`, `fsl,adc-refp`, and `fsl,adc-refn` properties.
- `mx25_gcq_get_raw_value()` writes queue item 0, enables EOQ IRQ, starts one forced queue run, waits for completion, and reads FIFO data.
- `mx25_gcq_irq()` handles EOQ, disables the queue run, acknowledges status bits, and completes readers.

## Control flow
Probe maps MMIO, wraps it in a 32-bit regmap, initializes defaults, parses per-channel reference configuration, enables any referenced external regulators, enables the parent TSADC clock, requests the IRQ, and registers a direct-mode IIO device. `read_raw` uses the mutex for raw conversions and returns a scale of `channel_vref_mv / 2^12`.

## State and persistence
The driver programs the queue configuration registers at probe and stores per-channel reference voltage in memory. User reads do not persist state except for temporary queue item selection and queue-control bits. External regulators are enabled for the lifetime of the device through devm cleanup actions.

## Dependencies and integration points
It depends on the parent `mx25_tsadc` MFD data for the shared clock, `dt-bindings/iio/adc/fsl-imx25-gcq.h` for reference constants, regmap MMIO, regulators named `vref-yp`, `vref-xp`, or `vref-ext`, and a platform IRQ.

## Risks
- The shared clock is not owned by this child driver, so enable/disable sequencing must stay compatible with sibling TSADC users.
- Optional external references are required if firmware selects them; missing regulators correctly fail probe.
- Queue status is acknowledged broadly, so IRQ semantics must remain aligned with the MFD register definitions.
- `regulator_get_voltage()` errors are assigned into unsigned millivolt storage after setup; bad regulator implementations can lead to misleading scales.

## Test signals
Validate DT child-node parsing, invalid `reg` and reference values, internal and external reference scales, EOQ interrupt completion, timeout path, and shared-clock behavior with other TSADC functions enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/fsl-imx25-gcq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/gehc-pmc-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/gehc-pmc-adc.c

## Purpose
`gehc-pmc-adc.c` is an I2C IIO driver for a GE HealthCare PMC ADC protocol that exposes 16 voltage and 16 current channels. The device returns already-processed signed millivolt or milliampere values.

## Important APIs, types, and functions
- `struct pmc_adc` stores the I2C client.
- `pmc_adc_channels` creates voltage commands `0x10 | channel` and current commands `0x20 | channel`.
- `pmc_adc_read_raw_ch()` uses `i2c_smbus_read_word_swapped()` and sign-extends 16-bit values.
- `pmc_adc_read_raw()` handles `IIO_CHAN_INFO_PROCESSED`.
- `pmc_adc_fwnode_xlate()` maps two-cell firmware references, acquisition type plus channel number, to IIO channel indices.
- Probe enables four regulators, optionally enables an `osc` clock, checks protocol version command `0x01`, and registers the IIO device.

## Control flow
Probe bulk-enables `vdd`, `vdda`, `vddio`, and `vref`, enables optional oscillator clock, allocates the device, reads the protocol version, rejects non-`0x01` protocol, and registers 32 direct-mode channels. Reads perform one SMBus word read using the channel address as command.

## State and persistence
No mutable runtime state is persisted. Regulator and optional clock enablement live for the device lifetime. The protocol version check is probe-time state validation only.

## Dependencies and integration points
The driver integrates with I2C, regulator bulk helpers, optional common clock, IIO direct mode, and firmware IIO consumer mapping using GEHC-specific DT binding constants.

## Risks
- Values are trusted as processed units, so scaling or unit changes in firmware/protocol would break ABI expectations.
- There is no explicit mutex; I2C core serialization is relied on for simple command reads.
- Unsupported protocol versions fail probe, which is correct but requires firmware coordination.

## Test signals
Use an I2C stub or hardware to verify protocol version rejection, signed positive/negative values, all 32 channels, and fwnode references for voltage/current type plus channel number.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/gehc-pmc-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/hi8435.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/hi8435.c

## Purpose
`hi8435.c` is an SPI IIO driver for the Holt HI-8435 32-channel threshold detector. It exposes each channel as a raw voltage-like boolean input, supports threshold events, and provides a per-channel sensing mode enum for GND-open versus supply-open detection.

## Important APIs, types, and functions
- `struct hi8435_priv` stores the SPI device, mutex, event enable mask, previous event value, low/high thresholds for both sensing modes, and an aligned SPI write buffer.
- `hi8435_readb/readw/readl()` and `hi8435_writeb/writew()` implement the register protocol.
- `hi8435_read_raw()` reads the 32-bit status register and returns one channel bit.
- Event callbacks manage software event enablement and threshold read/write logic.
- `hi8435_sensing_mode` and `hi8435_ext_info` expose per-channel sensing mode through IIO enum ext info.
- `hi8435_trigger_handler()` reads status and pushes IIO threshold events for changed enabled channels.

## Control flow
Probe allocates the IIO device, gets an optional reset GPIO or performs software reset, initializes thresholds for both modes to avoid odd hysteresis lockup, sets all events enabled by default, installs triggered-event handling, and registers the device. Event enable snapshots current status into `event_prev_val`. Trigger handling compares current status with previous value and emits rising or falling threshold events.

## State and persistence
Software state includes `event_scan_mask`, `event_prev_val`, and cached threshold limits. Hardware state includes the PSEN sensing-mode register and threshold/hysteresis registers. Threshold writes enforce legal ranges and even hysteresis, then program the mode-specific hardware register. State does not persist across device reset.

## Dependencies and integration points
The driver uses SPI, optional GPIO reset, IIO events, IIO triggered events, IIO enum ext info, debugfs register access, and DT compatible `holt,hi8435`.

## Risks
- Threshold hardware can lock if hysteresis is odd; the driver contains specific correction logic that must not be simplified casually.
- Event enable/disable manipulates software masks without a mutex, so races with triggers are possible but bounded by word-sized bit operations.
- Probe ignores return values from reset/threshold initialization writes in a few places, which can hide early bus failures until registration or later reads.

## Test signals
Test software and GPIO reset paths, raw reads for all 32 bits, event enable/disable, rising/falling event direction, sensing-mode changes by 8-channel banks, threshold boundary validation, odd-hysteresis correction, and debugfs register reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/hi8435.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/hx711.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/hx711.c

## Purpose
`hx711.c` is a GPIO bit-banging IIO ADC driver for the Avia HX711 load-cell converter. It exposes channel A and B as 24-bit raw voltage channels, supports scale selection through gain, and supports triggered buffered reads.

## Important APIs, types, and functions
- `struct hx711_data` stores SCK and DOUT GPIO descriptors, gain state, mutex, scan buffer, data-ready delay, and configured clock frequency.
- `hx711_gain_to_scale` maps gain 128, 32, and 64 to pulse counts, scale values, and channel ownership.
- `hx711_cycle()` toggles PD_SCK with IRQs locally disabled while high to avoid accidental reset.
- `hx711_read()` clocks out 24 bits, applies offset-binary conversion with `^ 0x800000`, then sends gain-selection pulses.
- `hx711_reset_read()` combines reset, channel/gain selection, and read.
- `hx711_read_raw()`, `hx711_write_raw()`, and `hx711_trigger()` implement direct and buffered IIO access.

## Control flow
Probe gets `sck` output and `dout` input GPIOs, enables and reads `avdd`, computes nanovolt-scale values for each gain, reads optional `clock-frequency`, sets the default gain to 128, configures direct-mode channels plus timestamp, sets up a triggered buffer, and registers IIO. Reads and buffered triggers take the mutex, reset or synchronize the device, switch channel/gain if needed, and read samples by bit-banging.

## State and persistence
The HX711 gain/channel state is hardware state selected by the number of trailing SCK pulses after a read. The driver mirrors it with `gain_set` and `gain_chan_a`; reset returns hardware to gain 128. Scale writes change gain and may immediately consume a read to apply the hardware selection. There is no persistent storage.

## Dependencies and integration points
The driver integrates with platform/OF `avia,hx711`, GPIO descriptors, regulator voltage reading, IIO sysfs attributes for scale availability, and IIO triggered buffers.

## Risks
- Timing is critical: PD_SCK high for more than about 60 us resets the device, so local IRQ masking in `hx711_cycle()` is intentional.
- Scale table is global and updated at probe, which is safe for identical AVDD assumptions but can be surprising with multiple devices at different AVDD.
- `hx711_trigger()` pushes buffer data even if a channel read returns an error stored as a `u32`.
- Long ready waits can block readers for up to one second after reset/channel changes.

## Test signals
Validate GPIO timing with logic analyzer, raw reads on both channels, scale availability and scale writes, behavior after reset or DOUT stuck high, buffered two-channel scans, and multiple-device behavior with different AVDD regulators.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/hx711.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx7d_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/imx7d_adc.c

## Purpose
`imx7d_adc.c` is a direct-mode IIO ADC driver for the Freescale/NXP i.MX7D ADC. It exposes sixteen logical voltage channels, using four hardware conversion channels with interrupt-driven completion.

## Important APIs, types, and functions
- `struct imx7d_adc` holds MMIO, ADC clock, vref regulator, completion, mutex, current channel, last value, predivider, and feature configuration.
- `struct imx7d_adc_feature` stores predivider, averaging count, and core time unit.
- `imx7d_adc_hw_init()` powers up the ADC, enables channel interrupts, and programs sample rate.
- `imx7d_adc_channel_set()` configures the selected hardware channel for single conversion with averaging.
- `imx7d_adc_read_data()` extracts 12-bit results from shared A/B or C/D result registers.
- `imx7d_adc_isr()` completes reads and clears conversion or timeout status bits.

## Control flow
Probe maps registers, gets IRQ, clock, and `vref`, registers cleanup through `devm_add_action_or_reset`, initializes feature defaults, enables regulator and clock, programs hardware, requests the IRQ, and registers IIO. A raw read masks the requested logical channel to one of four hardware channels, configures it, waits up to 100 ms for completion, and returns the captured value.

## State and persistence
The driver stores sample-rate configuration and current channel in memory and programs ADC power, timing, averaging, and channel config registers. Runtime suspend powers the ADC down and disables clock/regulator; resume reverses this. No user-written persistent configuration is exposed.

## Dependencies and integration points
It uses platform/OF `fsl,imx7d-adc`, MMIO, IRQs, completions, common clocks, regulators, IIO direct mode, and simple device PM ops.

## Risks
- Only `chan->channel & 0x03` selects hardware channels, so the sixteen exposed logical channels map onto four hardware result lanes.
- Interrupt status clearing writes a modified status value; changes to write-one-to-clear semantics would be dangerous.
- Sample-rate values are fixed by feature defaults; no runtime setter is exposed.

## Test signals
Read all exposed channels, verify mapping to hardware inputs, check scale from `vref`, inspect sample frequency, exercise suspend/resume, and simulate conversion timeout status bits to confirm logging and clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx7d_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx8qxp-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/imx8qxp-adc.c

## Purpose
`imx8qxp-adc.c` is the direct-mode IIO driver for the NXP i.MX8QuadXPlus ADC. It exposes eight voltage channels and uses software-triggered single conversions with FIFO watermark interrupts.

## Important APIs, types, and functions
- `struct imx8qxp_adc` stores MMIO, peripheral and IPG clocks, `vref`, mutex, completion, and a small FIFO cache.
- `imx8qxp_adc_reset()` performs software reset and FIFO reset.
- `imx8qxp_adc_reg_config()` configures ADC power/reference, trigger 0, command low/high fields, averaging, and channel selection.
- `imx8qxp_adc_fifo_config()` sets FIFO watermark and interrupt enable.
- `imx8qxp_adc_read_raw()` uses runtime PM, configures a conversion, enables the ADC, writes `SWTRIG`, and waits for completion.
- Runtime PM callbacks enable/disable regulator and both clocks and reset or disable the ADC.

## Control flow
Probe maps resources, gets IRQ, `per` and `ipg` clocks, enables `vref`, prepares/enables clocks, requests the IRQ, resets hardware, registers IIO, and enables runtime autosuspend. A raw read resumes the device, locks, configures channel and FIFO, starts conversion, waits up to 100 ms, then returns `fifo[0]` and schedules autosuspend.

## State and persistence
Runtime state is limited to power/clock state, current register configuration, and last FIFO samples. There is no persistent setting beyond hardware registers. Runtime suspend powers down the ADC by disabling it, clocks, and regulator.

## Dependencies and integration points
The driver uses platform/OF `nxp,imx8qxp-adc`, MMIO, IRQs, completions, common clocks, regulator consumers, runtime PM autosuspend, and IIO debugfs register access.

## Risks
- `pm_runtime_get_sync()` return values are not checked; failed resume could still proceed into register access.
- IRQ handler trusts FIFO count up to hardware maximum; mismatched masks could overrun `fifo`.
- Conversion start and runtime PM put occur before timeout checks, so failure paths depend on autosuspend behavior.

## Test signals
Validate runtime PM resume/suspend, raw reads for all channels, FIFO count handling, scale from `vref`, sample frequency from `per` clock, debugfs register reads, and timeout behavior when the IRQ is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx8qxp-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx93_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/imx93_adc.c

## Purpose
`imx93_adc.c` supports the NXP i.MX93 ADC as a direct-mode IIO voltage device with eight channels. It performs probe-time ADC calibration, then uses normal one-shot conversions completed by the third platform IRQ.

## Important APIs, types, and functions
- `struct imx93_adc` holds MMIO, IPG clock, IRQ, vref regulator, mutex, and completion.
- `imx93_adc_power_down()` and `imx93_adc_power_up()` manage ADC power state and poll status.
- `imx93_adc_calibration()` configures calibration mode, starts calibration, waits up to 2 seconds, and logs calibration failure.
- `imx93_adc_read_channel_conversion()` configures normal channel mask, interrupt masks, one-shot mode, starts conversion, waits, and reads `PCDRn`.
- `imx93_adc_isr()` acknowledges EOC/ECH interrupts and reports unexpected bits.
- Runtime PM callbacks power down/up and manage clock/regulator.

## Control flow
Probe maps MMIO, gets IRQ index 2, obtains clock and regulator, enables them, requests IRQ, runs calibration, configures AD clock, registers IIO, and enables runtime autosuspend. A raw read resumes the device, locks, starts a one-shot normal conversion for the requested channel, waits for completion, reads the 12-bit result, unlocks, and autosuspends.

## State and persistence
The driver stores no user settings. Hardware state includes calibration results, AD clock selection, interrupt masks, channel mask, and power state. Runtime suspend powers the ADC down; runtime resume powers it up without rerunning calibration.

## Dependencies and integration points
It integrates with platform/OF `nxp,imx93-adc`, common clock, regulators, IRQs, Linux completions, runtime PM, and direct-mode IIO.

## Risks
- The code uses IRQ index 2 specifically; bindings must provide that conversion IRQ.
- Calibration timeout message says "2 min" although the timeout argument is 2 seconds.
- `pm_runtime_get_sync()` results are not checked before MMIO access.
- Unexpected interrupt bits return `IRQ_NONE` after clearing them, which can affect shared IRQ diagnostics.

## Test signals
Test calibration success/failure paths, channel conversions on all eight channels, EOC/ECH interrupt ack, runtime PM autosuspend/resume, regulator-derived scale, and removal while runtime PM is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/imx93_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ina2xx-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ina2xx-adc.c

## Purpose
`ina2xx-adc.c` is an IIO driver for TI INA219/220/226/230/231/236 current, voltage, and power monitors. It exposes raw and scaled shunt voltage, bus voltage, current, and power channels, configurable integration/averaging/gain where supported, a shunt-resistor sysfs setting, and a kthread-backed software buffer.

## Important APIs, types, and functions
- `struct ina2xx_config` describes chip defaults, register LSBs, calibration value, and chip family.
- `struct ina2xx_chip_info` stores regmap, capture thread, configuration state, shunt resistor, timing, gain/range, async-readout flag, lock, and scan buffer.
- `ina2xx_read_raw()` implements raw, scale, oversampling ratio, integration time, sample frequency, and hardware gain.
- `ina2xx_write_raw()` updates averaging, integration time, and INA219 hardware gain/range while rejecting writes when buffers are active.
- `ina2xx_set_calibration()` and `ina2xx_init()` program configuration and calibration registers.
- `ina2xx_capture_thread()` polls conversion-ready flags unless async readout is allowed, reads active channels, timestamps, and pushes buffers.
- `ina2xx_probe()` sets defaults from chip type and DT `shunt-resistor`, initializes regmap, configures the chip, installs kfifo buffer setup, and registers IIO.

## Control flow
Probe selects the chip from OF or I2C ID, initializes regmap with 16-bit registers, stores the shunt resistor, patches the default config with family-specific timing and gain fields, writes config/calibration, selects channel tables and IIO info, sets up a kfifo buffer, and registers the device. Direct reads read a single register and convert according to the requested mask. Buffered operation starts a kernel thread that synchronizes to conversion-ready flags and pushes scans until stopped.

## State and persistence
The device configuration register, calibration register, and power mode are hardware state. Driver state mirrors averaging, integration times, vbus range, shunt gain, shunt resistor, and async-readout mode. On remove the driver unregisters IIO and clears mode bits to power down the device. User changes are not persisted across reboot.

## Dependencies and integration points
The driver depends on I2C, regmap, IIO kfifo buffers, IIO sysfs attributes, OF `shunt-resistor`, kthreads, and register layouts for INA219-compatible and INA226-compatible families.

## Risks
- Buffered capture is software timed and may drop samples if the thread falls behind.
- `allow_async_readout` trades synchronization for fewer status reads; users can get repeated or skipped samples if enabled.
- Configuration writes are blocked while buffers are enabled, but sysfs attributes like shunt resistor are not tied to buffer state.
- Power-down on remove can fail and only warns.
- Scan channel signedness is mostly unsigned even for signed registers; consumers must account for scale/sign semantics.

## Test signals
Use regmap/I2C emulation for raw register decoding, scale math for each family, shunt resistor parsing, integration/gain bounds, buffer enable/disable thread lifetime, conversion-ready polling, async-readout mode, and remove-time powerdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ina2xx-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/industrialio-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/industrialio-adc.c

## Purpose
`industrialio-adc.c` provides a small exported helper for ADC drivers that describe channels in firmware child nodes. It allocates an array of single-ended `iio_chan_spec` entries from `channel` child nodes and their `reg` properties.

## Important APIs, types, and functions
- `devm_iio_adc_device_alloc_chaninfo_se()` is the sole exported function.
- It calls `iio_adc_device_num_channels(dev)` to count firmware-described channels.
- It uses `device_for_each_named_child_node_scoped(dev, child, "channel")` to iterate channel nodes.
- It copies a caller-provided template into each allocated channel spec and sets `chan->channel` from `reg`.
- It exports the symbol in namespace `IIO_DRIVER`.

## Control flow
The helper counts channels, returns `-ENOENT` when no channel nodes are present, devm-allocates the channel array, reads each child `reg`, optionally enforces `max_chan_id`, copies the template, stores the channel number, returns the allocated array through `cs`, and returns the number of channels.

## State and persistence
There is no persistent state. Allocated channel specs are devm-managed and freed at device detach.

## Dependencies and integration points
This helper integrates with firmware property APIs, IIO ADC helper APIs, devm allocation, and module namespace exports for ADC drivers that want common fwnode channel parsing.

## Risks
- The function assumes the count from `iio_adc_device_num_channels()` matches the later named-child iteration.
- It only sets `.channel`; drivers needing per-channel labels, differential pairs, or scan indices need additional processing.
- Returning `-ENOENT` for zero nodes is a contract callers must handle distinctly from empty-but-valid configurations.

## Test signals
Unit-test firmware nodes with no channels, missing `reg`, out-of-range `reg`, and valid sparse channel IDs. Check that template fields are preserved and devm cleanup occurs on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/industrialio-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ingenic-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ingenic-adc.c

## Purpose
`ingenic-adc.c` is an IIO ADC driver for Ingenic JZ47xx SoCs. It supports auxiliary and battery direct reads across several SoC variants and, on JZ4770-style parts, touchscreen scan channels through a software buffer.

## Important APIs, types, and functions
- `struct ingenic_adc_soc_data` captures variant-specific reference voltages, availability tables, channel tables, feature flags, and clock-divider initialization.
- `struct ingenic_adc` stores MMIO base, prepared clock, register lock, auxiliary lock, SoC data, and battery low-vref mode.
- `ingenic_adc_set_adcmd()` builds touchscreen conversion command sequences based on active scan mask.
- `ingenic_adc_capture()` enables an ADC engine, polls until hardware clears it, and temporarily disables command-select to avoid wrong VBAT reads.
- `ingenic_adc_read_raw()` and `ingenic_adc_write_raw()` expose raw/scale reads and battery reference-mode writes.
- `ingenic_adc_buffer_enable()` and `ingenic_adc_buffer_disable()` configure touchscreen scanning and clock lifetime.
- `ingenic_adc_irq()` reads touch data registers and pushes buffered samples.

## Control flow
Probe selects SoC data from OF, requests the IRQ, maps MMIO, gets a prepared ADC clock, enables it long enough to program clock dividers and passive hardware state, applies optional internal VBAT divider selection, disables the clock, sets IIO direct plus software-buffer modes, and registers the device. Direct reads enable the clock, serialize auxiliary channel selection, trigger the chosen engine, read result registers, and disable the clock. Buffer enable keeps the clock on and programs touchscreen command scanning until buffer disable.

## State and persistence
Driver state includes `low_vref_mode` and SoC data. Hardware state includes ADC engine enables, config bits for auxiliary selection, battery reference mode, command sequence, wait/same registers, interrupt mask/status, and clock dividers. User writes can change battery scale mode on supported SoCs; it is not persisted across reset.

## Dependencies and integration points
The driver uses platform/OF compatibles for JZ4725B/JZ4740/JZ4760/JZ4760B/JZ4770, MMIO, IRQs, common clocks, IIO direct and software buffer modes, fwnode xlate by channel ID, and SoC-specific ADC DT binding constants.

## Risks
- Direct auxiliary reads and buffered touchscreen scans share command/config registers; `lock` and `aux_lock` protect key paths but changes must preserve ordering.
- Clock divider calculations depend on parent clock rates falling within hardware ranges.
- Touch IRQ buffering pushes three 32-bit words based on scan mask pairs; consumer expectations must match scan layout.
- JZ4740 high battery reference uses a floating expression cast into integer constants, so exact scale ABI should be treated carefully.

## Test signals
Test each SoC data table, clock divider edge rates, direct aux/battery reads, battery scale availability and writes, fwnode xlate, buffer enable/disable register cleanup, touch IRQ samples for different scan masks, and internal-divider property handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ingenic-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/intel_dc_ti_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/intel_dc_ti_adc.c

## Purpose
`intel_dc_ti_adc.c` is an IIO GPADC driver for the Intel Dollar Cove TI PMIC. It exposes battery voltage and PMIC/battery/system temperature channels and registers IIO maps for battery consumers.

## Important APIs, types, and functions
- `struct dc_ti_adc_info` stores mutex, wait queue, parent PMIC regmap, calibration values, and conversion-done flag.
- `dc_ti_adc_channels` defines VBAT, PMICTEMP, BATTEMP, and SYSTEMP0.
- `dc_ti_adc_sample()` enables ADC, selects channel, delays per vendor timing, starts conversion, waits up to 5 seconds, reads 10-bit big-endian result, and disables ADC.
- `dc_ti_adc_raw_to_processed()` applies VBAT zero-scale and gain-error calibration and returns millivolt values.
- `dc_ti_adc_read_raw()` handles scale, raw, processed VBAT, and BATTEMP bias timing.
- Probe reads calibration register, registers default IIO maps, requests threaded IRQ, and registers IIO.

## Control flow
Probe gets the PMIC regmap from the parent MFD, requests the platform IRQ, initializes locking and wait queue, reads VBAT calibration nibbles, registers consumer maps for `chtdc_ti_battery`, and registers direct-mode IIO. Reads serialize on `lock`; battery-temperature reads enable external bias and wait 35 ms before conversion; all conversions are interrupt-notified through `conversion_done`.

## State and persistence
Runtime state includes calibration values and conversion flag. Hardware state includes ADC enable/start, channel select, and external BPTHEM bias. The driver clears start/enable after every sample and does not persist user settings.

## Dependencies and integration points
It integrates with Intel SoC PMIC MFD, regmap, platform IRQ, wait queues, IIO maps, and IIO direct mode.

## Risks
- The 5-second timeout is long for sysfs reads but required by vendor guidance.
- BATTEMP bias clear is attempted after sampling but errors are ignored.
- Processed values exist only for VBAT; callers requesting processed temperature get `-EINVAL` after conversion.
- Timing comments contain microsecond symbols from source comments; exact vendor timing should be preserved.

## Test signals
Test IRQ completion, timeout cleanup, VBAT raw/scale/processed math with signed calibration nibbles, BATTEMP bias enable delay and clear, IIO map consumers, and concurrent reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/intel_dc_ti_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/intel_mrfld_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/intel_mrfld_adc.c

## Purpose
`intel_mrfld_adc.c` is the IIO ADC driver for the Intel Merrifield Basin Cove PMIC. It exposes voltage, resistance, current, and temperature channels and maps them to battery and thermal PMIC consumers.

## Important APIs, types, and functions
- `struct mrfld_adc` stores the PMIC regmap, completion, and mutex.
- `mrfld_adc_requests` maps IIO channel index to PMIC ADC request bits.
- `mrfld_adc_single_conv()` clears pending ADC IRQ state, waits for GPADC not busy, writes request plus IRQ enable, waits for threaded IRQ completion, bulk-reads the result, then re-masks IRQs.
- `mrfld_adc_thread_isr()` completes conversions.
- `mrfld_adc_read_raw()` serializes raw conversions through `lock`.
- Probe registers default IIO maps for `bcove-battery` and `bcove-temp`.

## Control flow
Probe gets the parent PMIC regmap, allocates IIO state, initializes completion and mutex, requests a shared threaded IRQ, installs channel table and direct mode, registers IIO maps, and registers the device. Every raw read runs one PMIC conversion request and waits up to one second.

## State and persistence
The driver has only volatile completion and lock state. Hardware state includes PMIC IRQ masks, GPADC request bits, and result registers. It clears and restores interrupt mask bits around each conversion; no user configuration persists.

## Dependencies and integration points
It depends on Intel Basin Cove MFD register definitions, regmap, platform IRQ, IIO maps, completions, and IIO direct-mode ABI.

## Risks
- The request table and channel table must remain in exact index alignment.
- IRQ mask restoration uses broad `0xff` update values, which assumes existing PMIC mask semantics.
- On timeout or read failure the cleanup still re-masks interrupts, but conversion hardware may remain in an unknown state until PMIC clears busy.

## Test signals
Verify all nine channel request mappings, busy polling timeout, IRQ completion, big-endian result decoding, IIO maps, and concurrent reads through the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/intel_mrfld_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lp8788_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/lp8788_adc.c

## Purpose
`lp8788_adc.c` is the IIO ADC child driver for the TI LP8788 MFD. It exposes battery, charger, current, temperature, and auxiliary ADC channels and provides default IIO maps for the LP8788 charger driver.

## Important APIs, types, and functions
- `struct lp8788_adc` stores the parent `struct lp8788`, chosen IIO maps, and a mutex.
- `lp8788_scale` contains per-channel scale values in micro units.
- `lp8788_get_adc_result()` starts conversion for a channel, polls the done register up to five times, reads raw bytes, and assembles a 12-bit result.
- `lp8788_adc_read_raw()` handles raw and scale masks under the mutex.
- `lp8788_iio_map_register()` selects platform-provided maps or default charger maps.

## Control flow
Probe retrieves the parent MFD data, allocates IIO state, registers IIO maps, initializes the mutex, sets direct-mode channel metadata, and registers IIO. Raw reads write the channel/start command, wait 100 to 200 us between done checks, then read and decode the raw result.

## State and persistence
No user-modifiable persistent state exists. Conversion selection and start bits are transient hardware state. Map selection is stored in memory for the device lifetime.

## Dependencies and integration points
The driver depends on LP8788 MFD helpers (`lp8788_write_byte`, `lp8788_read_byte`, `lp8788_read_multi_bytes`), platform data for optional IIO maps, IIO map registration, and direct-mode IIO.

## Risks
- If the done bit never becomes set, the code still reads raw data after retries rather than returning timeout.
- Scale values are fixed table entries and must match the parent PMIC channel definitions.
- Raw read error mapping collapses any `lp8788_get_adc_result()` failure to `-EIO`.

## Test signals
Test all channel scales, raw byte decoding, conversion-done retry behavior including never-done cases, default and platform IIO maps, and parent MFD I/O error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lp8788_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lpc18xx_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/lpc18xx_adc.c

## Purpose
`lpc18xx_adc.c` is a simple direct-mode IIO driver for the NXP LPC18xx ADC. It supports eight 10-bit voltage channels through polling and explicitly does not support hardware triggers, burst mode, interrupts, or DMA.

## Important APIs, types, and functions
- `struct lpc18xx_adc` stores vref regulator, MMIO base, device, mutex, clock, and cached control-register value.
- `lpc18xx_adc_read_chan()` writes control bits for one channel and start-now, then polls the global data register for conversion done.
- `lpc18xx_adc_read_raw()` handles raw and scale attributes.
- Probe computes ADC clock divider against a 4.5 MHz target, powers the ADC with `PDN`, registers cleanup actions, and registers IIO.

## Control flow
Probe maps MMIO, gets an already-enabled clock, gets and enables `vref`, computes `cr_reg`, writes it to the control register, and registers a direct-mode IIO device. A raw read takes the mutex, writes the selected channel and start bit, polls for done with microsecond timeout, extracts the 10-bit sample, and returns it.

## State and persistence
The driver caches only the base control register. Hardware control register state is cleared through a devm cleanup action on detach. No user settings persist.

## Dependencies and integration points
It uses platform/OF `nxp,lpc1850-adc`, MMIO, common clocks, regulators, IIO direct mode, and `readl_poll_timeout()`.

## Risks
- Poll timeout is very short; slow clocks or wrong divider can cause read failures.
- Scale assumes `regulator_get_voltage()` succeeds; a negative value would be divided and returned as scale.
- Clock divider calculation uses `DIV_ROUND_UP(rate, target)` directly in the register field; hardware off-by-one expectations must match the manual.

## Test signals
Probe with representative clock rates, read all eight channels, verify poll timeout behavior, validate scale from vref, and confirm cleanup clears the control register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lpc18xx_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lpc32xx_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/lpc32xx_adc.c

## Purpose
`lpc32xx_adc.c` is a direct-mode IIO driver for the NXP LPC32xx 3-channel 10-bit ADC. It uses IRQ completion for conversions and optionally exposes scale when a `vref` regulator is available.

## Important APIs, types, and functions
- `struct lpc32xx_adc_state` stores MMIO base, clock, completion, optional vref regulator, mutex, and last value.
- `lpc32xx_read_raw()` enables the clock for each raw read, configures channel/reference selection, starts conversion, waits for ISR completion, disables the clock, and returns the cached value.
- `lpc32xx_adc_isr()` reads and masks the value register and completes the wait.
- Two channel tables exist: one with raw only and one with shared scale.

## Control flow
Probe maps MMIO, gets clock, requests IRQ, tries to get `vref`, selects the channel table based on regulator availability, initializes completion and mutex, and registers IIO. Raw conversion blocks indefinitely on `wait_for_completion()` until the IRQ fires.

## State and persistence
State is volatile: completion state, last ADC value, optional regulator pointer, and clock enablement during reads. Hardware selection and control registers are programmed per conversion. No persistent configuration exists.

## Dependencies and integration points
It uses platform/OF `nxp,lpc3220-adc`, MMIO, IRQs, completions, common clocks, optional regulator scaling, and IIO direct mode.

## Risks
- Raw reads have no timeout, so a missing IRQ can hang a userspace read.
- Missing `vref` silently removes scale ABI, which is deliberate but visible to consumers.
- The regulator is not enabled before reading voltage for scale; this relies on regulator framework behavior or an always-on reference.

## Test signals
Validate IRQ delivery, no-vref channel table, scale table with vref, channel selection constants, clock enable/disable per read, and behavior when conversion IRQ is lost.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/lpc32xx_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2309.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2309.c

## Purpose
`ltc2309.c` is an I2C IIO driver for Analog Devices/Linear Technology LTC2305 and LTC2309 SAR ADCs. It exposes single-ended and differential voltage channels with raw and scale attributes.

## Important APIs, types, and functions
- `struct ltc2309` stores device, I2C client, mutex, and reference voltage in millivolts.
- Channel enums encode datasheet address selections for LTC2305 and LTC2309.
- `ltc2309_read_raw_channel()` writes the DIN channel selection byte and reads two big-endian bytes, returning a 12-bit sample.
- `ltc2309_read_raw()` serializes raw reads and returns scale as `vref_mv / 2^12`.
- Probe selects chip info from OF/I2C match data and uses optional `vref` regulator voltage or the 4096 mV internal reference.

## Control flow
Probe allocates the IIO device, assigns chip-specific channel table, attempts to enable/read `vref`, falls back to internal reference only on `-ENODEV`, initializes the mutex, and registers IIO. Each raw read writes the channel command with unipolar mode and no sleep, then reads conversion data.

## State and persistence
The only stored state is `vref_mv`; channel selection is transient hardware state. No user settings persist.

## Dependencies and integration points
The driver uses I2C SMBus byte writes, I2C master receive, regulator optional enable/read helpers, OF compatibles `lltc,ltc2305` and `lltc,ltc2309`, and IIO direct mode.

## Risks
- Negative I2C errors from raw channel reads are converted to `-EINVAL`, losing detailed failure information.
- Differential channels are still commanded with unipolar bit set; this follows the current implementation but should be checked against datasheet expectations.
- `ltc2309->dev` points at the IIO device rather than the I2C device, which affects log attribution.

## Test signals
Test both chip channel tables, optional regulator fallback, command byte encoding for single-ended and differential channels, raw data shifting, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2309.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2471.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2471.c

## Purpose
`ltc2471.c` is an I2C IIO driver for LTC2471 and LTC2473 voltage monitors. LTC2471 is single-ended while LTC2473 is differential and exposes an offset.

## Important APIs, types, and functions
- `struct ltc2471_data` stores the I2C client.
- `ltc2471_get_value()` reads a two-byte big-endian conversion result.
- `ltc2471_read_raw()` returns raw data, scale, and differential offset.
- Separate single-ended and differential one-channel `iio_chan_spec` arrays encode ABI differences.

## Control flow
Probe checks plain I2C functionality, allocates IIO state, selects the channel spec from I2C ID driver data, performs one read to start/check conversion, and registers the direct-mode IIO device. Reads simply fetch the latest two-byte sample.

## State and persistence
There is no driver-maintained mutable state beyond the client pointer. The ADC conversion cycle is implicit in I2C reads; no settings persist.

## Dependencies and integration points
The driver uses I2C master receive, I2C device IDs, fixed internal reference scale, and direct-mode IIO.

## Risks
- There is no OF match table, so device-tree-only systems need I2C modalias support.
- Offset returns `-1250` for differential mode as an integer mV offset; consumers must combine it with scale correctly.
- A short I2C read is treated as `-EIO`, which is correct and should be preserved.

## Test signals
Test both IDs, initial probe read failure, raw big-endian decoding, scale for single-ended and differential modes, and offset availability only for LTC2473.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2471.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2485.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2485.c

## Purpose
`ltc2485.c` is an I2C direct-mode IIO driver for the LTC2485 delta-sigma ADC. It provides one signed voltage channel with raw readings and fixed 5 V reference scale.

## Important APIs, types, and functions
- `struct ltc2485_data` stores the client and `time_prev`, the last conversion timestamp.
- `ltc2485_wait_conv()` sleeps until the 147 ms conversion time has elapsed since the last transfer.
- `ltc2485_read()` reads four bytes, updates timestamp, and sign-extends the 25-bit result after shifting status bits.
- `ltc2485_read_raw()` handles raw and scale.
- Probe writes the default configuration byte and initializes conversion timestamp.

## Control flow
Probe checks I2C and SMBus write-byte support, allocates state, writes the default configuration, records current time, and registers IIO. A raw read waits as needed, performs an I2C four-byte receive, sign-extends the sample, and returns it.

## State and persistence
The driver tracks conversion timing with `time_prev`. Hardware configuration is set once at probe to default rejection/speed mode. No user settings persist.

## Dependencies and integration points
It uses I2C master receive, SMBus write byte, ktime, sleep delays, and IIO direct mode.

## Risks
- There is no mutex around `time_prev` and reads; concurrent reads can violate conversion timing.
- A short positive I2C read is returned as success from `ltc2485_read()` because only negative errors are checked.
- Scale is fixed to onboard 5000 mV, not regulator-derived.

## Test signals
Test conversion-delay enforcement, raw sign extension for positive and negative values, I2C error and short-read handling, default config write, and concurrent read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2485.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2496.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2496.c

## Purpose
`ltc2496.c` is the SPI transport wrapper for the LTC2496 ADC family. It plugs an SPI `result_and_measure` implementation into the shared LTC2497 core, exposing the common 32-channel IIO ABI for a 16-bit converter.

## Important APIs, types, and functions
- `struct ltc2496_driverdata` embeds `struct ltc2497core_driverdata` as its first member and stores the SPI device plus aligned TX/RX buffers.
- `ltc2496_result_and_measure()` sends `LTC2497_ENABLE | address`, receives three bytes, and decodes the 18-bit signed-style result into `*val`.
- `ltc2496_probe()` allocates IIO state, fills common callbacks and chip info, and calls `ltc2497core_probe()`.
- `ltc2496_remove()` delegates cleanup to `ltc2497core_remove()`.

## Control flow
The SPI driver matches `lltc,ltc2496`, stores SPI state, sets the shared core callback, and lets the common core handle channel table, vref regulator, conversion timing, IIO maps, and registration. Reads enter through the core and call this transport callback to combine result fetch and next-channel command.

## State and persistence
Transport state is limited to SPI buffers and device pointer. Shared conversion address, timestamp, mutex, and regulator state live in the embedded core data.

## Dependencies and integration points
It depends on the internal `ltc2497.h` core API, SPI synchronous transfer, IIO DMA buffer alignment, OF match data, and module namespace import/export for `LTC2497`.

## Risks
- The embedded common data must remain the first struct member for `container_of` assumptions.
- SPI decode subtracts `1 << 17`; changes to core resolution assumptions must stay consistent.
- Only OF match data provides chip info; non-OF SPI ID binding is not present.

## Test signals
Test SPI transfer contents and decode, probe with missing match data, shared-core vref failure cleanup, remove cleanup, and raw reads across single-ended and differential common channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2496.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497-core.c

## Purpose
`ltc2497-core.c` provides common IIO logic for LTC2496 SPI and LTC2497/LTC2499 I2C ADC drivers. It owns channel definitions, conversion timing, vref regulator handling, IIO map registration, and exported probe/remove helpers.

## Important APIs, types, and functions
- `ltc2497core_wait_conv()` enforces the 150 ms conversion time and detects when a previous automatic-mode result may still be valid.
- `ltc2497core_read()` performs the two-step conversion model: optionally start a measurement for a new address, wait, then fetch result and start the next conversion.
- `ltc2497core_read_raw()` serializes access and returns raw or regulator-derived scale.
- `ltc2497core_channel` defines 16 single-ended and 16 differential channel specs.
- `ltc2497core_probe()` initializes IIO metadata, primes the device, enables `vref`, registers maps, initializes timing/lock, and registers IIO.
- `ltc2497core_remove()` unregisters IIO, maps, and regulator.

## Control flow
Transport wrappers provide `result_and_measure()`. The core probe sends a default measurement command, enables the reference regulator, registers any platform IIO maps, records default address and timestamp, and registers the direct-mode IIO device. Raw reads lock, call timing logic, maybe prime the requested channel, fetch the completed result, and update `time_prev`.

## State and persistence
The core maintains `addr_prev`, `time_prev`, `ref`, chip resolution/name, mutex, and transport callback. Hardware conversion pipeline state is implicit: each result read also starts a new conversion. No settings persist across detach or power loss.

## Dependencies and integration points
It integrates with IIO direct mode, regulator consumers, platform IIO maps, sleepable conversion delays, exported namespace `LTC2497`, and transport-specific I2C/SPI wrappers.

## Risks
- Conversion timing is central; concurrent access is protected by mutex but interruptible sleeps can return `-ERESTARTSYS`.
- Initial `result_and_measure()` occurs before acquiring/enabling `vref`, which assumes the device can accept setup before reference is enabled or the regulator is already active.
- Common channel addresses must match both SPI and I2C transport command formats.

## Test signals
Test timing paths for fresh, stale, and same-address reads, interrupted sleep, vref scale for 16- and 24-bit variants, IIO map registration failure cleanup, and transport callback error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.c

## Purpose
`ltc2497.c` is the I2C transport wrapper for LTC2497 and LTC2499 ADCs. It uses the shared LTC2497 core to expose common IIO channels while handling I2C receive/write protocol and result decoding for 16- and 24-bit devices.

## Important APIs, types, and functions
- `struct ltc2497_driverdata` embeds common core data first, stores I2C client, receive size, and aligned 3/4-byte data buffer.
- `ltc2497_result_and_measure()` reads the previous conversion result when requested, decodes 16/24-bit two's-complement-like format, and writes the next address command when necessary.
- `ltc2497_probe()` checks I2C capabilities, obtains match chip info, computes receive size from resolution, and calls `ltc2497core_probe()`.
- `ltc2497_remove()` delegates cleanup to the shared core.

## Control flow
Probe binds either LTC2497 or LTC2499, sets up the transport callback and chip info, and invokes core registration. During reads the core calls `ltc2497_result_and_measure()`: if a value is requested, it receives the result, decodes it, and returns early when the requested address matches the already-started conversion; otherwise it writes a new conversion command.

## State and persistence
Transport state includes receive size and the DMA-aligned buffer. Common state for previous address, conversion timing, mutex, and vref lives in the embedded core. No user settings persist.

## Dependencies and integration points
It uses I2C master receive, SMBus write byte, unaligned big-endian helpers, OF/I2C ID match data, and the `LTC2497` core namespace.

## Risks
- The comment notes that changing address after a result read likely cannot work without a combined operation if the new conversion is not complete.
- Receive-size calculation must stay aligned with resolution and decode shifts.
- As with the SPI wrapper, common data must remain the first struct member.

## Test signals
Test LTC2497 and LTC2499 receive sizes, 3-byte and 4-byte decode math, same-address fast path, address-change write path, I2C functionality rejection, and shared-core cleanup on failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.h -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.h

## Purpose
`ltc2497.h` is the private shared header for the LTC2496/LTC2497/LTC2499 driver family. It defines command constants, conversion timing, common chip metadata, common driver state, and exported core entry points.

## Important APIs, types, and functions
- `LTC2497_ENABLE`, `LTC2497_CONFIG_DEFAULT`, and `LTC2497_CONVERSION_TIME_MS` define common protocol and timing constants.
- `struct ltc2497_chip_info` carries ADC resolution and optional ABI-preserving device name.
- `struct ltc2497core_driverdata` stores vref regulator, previous conversion time/address, mutex, chip info, and transport callback.
- `ltc2497core_probe()` and `ltc2497core_remove()` are declared for transport wrappers.
- `MODULE_IMPORT_NS("LTC2497")` imports the namespace used by core exports.

## Control flow
The header has no runtime control flow. It is included by the shared core and transport drivers so their embedded state layout and callback contract agree.

## State and persistence
It defines volatile runtime state but does not instantiate state. No persistent data exists.

## Dependencies and integration points
The header depends on the including C files to provide regulator, ktime, mutex, and IIO declarations through their includes. It binds the core and wrappers through the `LTC2497` symbol namespace.

## Risks
- The common data struct is embedded as the first member in transport structs; changing its layout or callback signature affects both wrappers.
- Header lacks include guards, relying on limited private include usage.
- Missing explicit type includes can become fragile if including C files change include order.

## Test signals
Build-test all three files together, validate namespace import/export, and check that transport structs still embed `ltc2497core_driverdata` first after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ltc2497.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1027.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max1027.c

## Purpose
`max1027.c` supports Maxim MAX1027/MAX1029/MAX1031 and MAX1227/MAX1229/MAX1231 SPI ADCs. It exposes voltage and temperature channels, direct reads, optional hardware-triggered operation through CNVST/EOC IRQ, and triggered buffered scans.

## Important APIs, types, and functions
- `struct max1027_chip_info` describes channel tables and available scan masks per device width/channel count.
- `struct max1027_state` stores chip info, SPI device, optional trigger, scan buffer, mutex, completion, and command register byte.
- Channel macros define 10-bit or 12-bit voltage channels and a temperature channel with big-endian scan types.
- `max1027_read_single_value()` configures one conversion, waits, reads result bytes, and returns raw.
- `max1027_configure_chans_and_start()` programs scan from channel 0 through the highest active channel, optionally including temperature.
- `max1027_handler()` either completes raw/trigger waits or polls the IIO trigger.
- `max1027_trigger_handler()` starts/waits/reads scans depending on trigger ownership.

## Control flow
Probe selects chip info from SPI ID, sets direct IIO metadata and available scan masks, allocates a scan buffer, installs triggered buffer support, optionally allocates and registers an IIO trigger if `spi->irq` exists, requests the EOC IRQ, resets the ADC, disables averaging, sets conversion-on-register-write mode, and registers IIO. Direct reads claim direct mode and serialize with the mutex. Buffered scans either use the device's own trigger or an external trigger path.

## State and persistence
State includes trigger mode, completion, command register byte, active scan mask, and buffer. Hardware state includes setup, averaging, reset, conversion mode, and scan command registers. The driver does not expose persistent configuration for averaging or reference mode.

## Dependencies and integration points
It uses SPI, optional IRQ, IIO direct mode, IIO triggers, triggered buffers, available scan masks, completions, and debugfs register access.

## Risks
- Available scan masks force scans from 0 to N; consumers requesting sparse channels still incur extra hardware reads.
- Temperature channel cannot be retrieved alone in buffered mode by mask design.
- Raw reads use wait timing even with IRQ because conversion-register mode may miss interrupts; this behavior is documented in-code.
- Scale assumes 2500 mV reference and fixed temperature scale.

## Test signals
Test all chip IDs/channel counts, direct voltage and temperature reads, scan-mask selection for sparse channels, IRQ and no-IRQ timing paths, own trigger state changes, external trigger handling, reset/averaging setup writes, and debugfs access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1027.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11100.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max11100.c

## Purpose
`max11100.c` is a direct-mode SPI IIO driver for the Maxim MAX11100 single-channel 16-bit ADC. It exposes raw samples and regulator-derived scale.

## Important APIs, types, and functions
- `struct max11100_state` stores the vref regulator, SPI device, and a DMA-aligned 3-byte receive buffer.
- `max11100_read_single()` reads three bytes, validates the leading byte is zero, and decodes the following big-endian 16-bit sample.
- `max11100_read_raw()` handles raw and scale; scale is `vref_mV / 65536`.
- Probe gets and enables `vref`, installs cleanup, and registers IIO.

## Control flow
Probe allocates state, assigns one voltage channel, obtains and enables `vref`, registers a devm regulator-disable action, and registers IIO. Raw reads are single SPI reads with protocol validation.

## State and persistence
Runtime state is limited to the regulator and receive buffer. No hardware configuration or persistent user settings are exposed.

## Dependencies and integration points
The driver uses SPI, regulator consumers, unaligned big-endian helpers, OF compatible `maxim,max11100`, and IIO direct mode.

## Risks
- There is no mutex; concurrent reads share the receive buffer.
- Dummy regulators returning `-EINVAL` from `get_voltage` make scale unavailable.
- Nonzero leading byte is treated as invalid data and returns `-EINVAL`.

## Test signals
Test raw SPI decode, invalid leading byte, regulator voltage scale, regulator enable cleanup, and concurrent sysfs read behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1118.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max1118.c

## Purpose
`max1118.c` supports Maxim MAX1117/MAX1118/MAX1119 dual-channel 8-bit SPI ADCs. It provides direct raw/scale reads and triggered buffered scans with a timestamp.

## Important APIs, types, and functions
- `struct max1118` stores SPI device, mutex, optional vref regulator, scan buffer, and DMA-aligned one-byte data buffer.
- `max1118_read()` uses zero-length SPI transfers with chip-select timing delays to select and convert channel 0 or 1, then reads one byte.
- `max1118_get_vref_mV()` returns fixed internal references for MAX1117/MAX1119 or regulator voltage for MAX1118.
- `max1118_read_raw()` handles raw and scale under lock.
- `max1118_trigger_handler()` reads all active channels and pushes a timestamped scan.

## Control flow
Probe allocates state, enables `vref` only for MAX1118, initializes IIO metadata, performs an initial channel 0 read to reset conversion/autoshutdown state, sets up a triggered buffer, and registers IIO. Direct and buffered reads serialize SPI transfers with the mutex.

## State and persistence
State is volatile: optional regulator, scan buffer, and SPI transaction state. The ADC enters AutoShutdown after conversion; probe primes channel 0. No user settings persist.

## Dependencies and integration points
The driver uses SPI transfer delays, regulator consumers for MAX1118, IIO triggered buffers, OF/SPI IDs, and IIO direct mode.

## Risks
- Channel selection relies on precise chip-select toggling via zero-length transfers; controller support must be validated.
- Buffered handler logs and skips push on read error but still completes the trigger.
- Fixed vref values depend on exact chip ID match data.

## Test signals
Test all three chip IDs, regulator path for MAX1118, channel 0 and channel 1 SPI transfer sequences, direct and buffered reads, scale values, and trigger cleanup after read failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1118.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11205.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max11205.c

## Purpose
`max11205.c` is an IIO driver for Maxim MAX11205A/MAX11205B 16-bit delta-sigma ADCs. It delegates conversion and buffered trigger handling to the generic IIO AD sigma-delta helper.

## Important APIs, types, and functions
- `struct max11205_chip_info` stores output data rate and name for A/B variants.
- `struct max11205_state` stores chip info, vref regulator, and embedded `struct ad_sigma_delta`.
- `max11205_read_raw()` delegates raw reads to `ad_sigma_delta_single_conversion()`, returns regulator-derived scale, and reports fixed sample frequency.
- `max11205_iio_info` uses `ad_sd_validate_trigger`.
- Probe initializes the sigma-delta helper, enables `vref`, sets up AD sigma-delta buffer/trigger, and registers IIO.

## Control flow
Probe allocates state, calls `ad_sd_init()`, obtains match data, configures one signed 16-bit big-endian voltage channel, enables `vref`, registers cleanup, sets up sigma-delta buffer and trigger support, and registers IIO. Raw reads go through the shared sigma-delta single-conversion path.

## State and persistence
State includes enabled regulator, chip data rate, and the sigma-delta helper state. No user configuration persists.

## Dependencies and integration points
The driver depends on SPI, regulator consumers, IIO AD sigma-delta helpers, trigger validation, OF/SPI match data, and namespace `IIO_AD_SIGMA_DELTA`.

## Risks
- `spi_get_device_match_data()` must provide chip info; missing data would lead to invalid dereference.
- Scale uses `MAX11205_BIT_SCALE` of 15 for a signed 16-bit channel, so changes must preserve ABI expectations.
- Most conversion behavior is in the shared sigma-delta helper, so regressions may appear outside this file.

## Test signals
Test A and B variant sample frequencies, regulator scale, raw single conversion through the sigma-delta helper, buffer/trigger setup, trigger validation, and missing/invalid match data handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11205.c -->
