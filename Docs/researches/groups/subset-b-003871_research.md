# Research Group subset-b-003871

Grouped source-tree-aligned research for IIO ADC drivers under `sources/distributed-fs/ceph-client/drivers/iio/adc`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/at91-sama5d2_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/at91-sama5d2_adc.c

## Purpose
This is the modern Microchip/Atmel SAMA5D2-compatible ADC IIO driver, also covering SAMA7G5 through per-SoC register-layout and channel tables. It exposes voltage ADC channels, differential channels, optional touchscreen position/pressure channels, and an optional SAMA7G5 temperature channel through IIO direct reads and software-triggered buffers. It also supports external hardware trigger modes, optional RX DMA for buffered capture, runtime PM around the ADC clock, regulators for analog and reference supplies, and NVMEM-based temperature calibration.

## Important APIs, Types, And Functions
Core register indirection is carried by `struct at91_adc_reg_layout`, allowing SAMA5D2 and SAMA7G5 to use the same logic with different offsets and EOC register placement. `struct at91_adc_platform` describes channel arrays, max indexes, trigger count, oversampling masks, real bit widths, touch indexes, and temperature support. `struct at91_adc_state` is the persistent driver state: MMIO base, IRQ, clocks, regulators, vref voltage, current sample rate, selected trigger, direct-conversion waitqueue state, DMA state, touch state, temperature state, and a mutex protecting single conversions.

Important entry points are `at91_adc_probe()`, `at91_adc_remove()`, `at91_adc_read_raw()`, `at91_adc_write_raw()`, `at91_adc_interrupt()`, `at91_adc_trigger_handler()`, `at91_adc_buffer_prepare()`, `at91_adc_buffer_postdisable()`, `at91_adc_set_watermark()`, and the PM callbacks. Temperature handling is split through `at91_adc_temp_sensor_init()`, `at91_adc_temp_sensor_configure()`, and `at91_adc_read_temp()`. DMA is isolated behind `at91_adc_dma_init()`, `at91_adc_dma_start()`, `at91_adc_dma_size_done()`, `at91_adc_trigger_handler_dma()`, and `at91_adc_dma_disable()`.

## Control Flow
Probe allocates an IIO device, resolves SoC data from OF match data, optionally reads temperature calibration, initializes channel metadata, reads required device properties (`atmel,min-sample-rate-hz`, `atmel,max-sample-rate-hz`, `atmel,startup-time-ms`, optional `atmel,trigger-edge-type`), chooses a trigger descriptor, maps MMIO, requests the IRQ, enables `vddana`, `vref`, and `adc_clk`, enables runtime PM, resets/configures hardware, installs triggered-buffer support, and registers the IIO device.

Direct raw reads claim IIO direct mode, take `st->lock`, power the device with runtime PM, configure channel differential state through `COR`, enable the channel and EOC IRQ, start conversion, wait up to one second for `at91_adc_interrupt()` to fill `conversion_value`, scale for oversampling, sign-extend differential values, disable EOC/channel state, clear DRDY by reading `LCDR`, and autosuspend. Touch raw reads read already-latched touch registers only while `touching` is true. Temperature processed reads temporarily switch sample frequency/oversampling/track settings for accuracy, read VBG and VTEMP with `ACR_SRCLCH` toggled, then compute milli-Celsius from NVMEM calibration constants.

Buffered capture uses IIO triggered-buffer setup. Non-touch scan masks enable selected voltage channels and either handle DRDY IRQs with `at91_adc_trigger_handler_nodma()` or use DMA when a hardware trigger and watermark greater than one are configured. The non-DMA handler waits until all EOC bits in the active mask are set, reads channel registers, adjusts oversampling width, and pushes a timestamped scan. The DMA handler consumes cyclic DMA residue, adjusts each sample for oversampling, and synthesizes timestamps from the previous DMA timestamp and sample count. Touch buffering is a separate path: enabling a touch-only scan programs `TSMR`, pen debounce, and periodic trigger registers, then IRQ events schedule work to push position/pressure samples outside IRQ context.

## State And Persistence
There is no persistent on-disk state. Runtime state is held in `struct at91_adc_state`: current sample rate, oversampling ratio, selected trigger, DMA watermark/buffer index/timestamp, touch `touching` and cached X position, and temporary temperature saved settings. Hardware state is reset in `at91_adc_hw_init()` at probe and resume. Runtime PM gates `adc_clk`; system suspend disables active buffers, resets the ADC so pins are released, disables clock/regulators, and selects pinctrl sleep state. Resume restores pinctrl, regulators, clock, hardware configuration, and active buffer/trigger state.

## Dependencies And Integration Points
The driver integrates with the platform bus and OF compatibles `atmel,sama5d2-adc` and `microchip,sama7g5-adc`. It depends on IIO core, IIO triggered buffers, IIO triggers, DMAengine, NVMEM, pinctrl, regulators, clocks, runtime PM, and `dt-bindings/iio/adc/at91-sama5d2_adc.h`. Consumer-visible integration includes IIO raw/scale/processed/sample-frequency/oversampling sysfs attributes, optional FIFO watermark attributes for hardware-triggered DMA, fwnode channel translation, IIO trigger registration for external trigger modes, and callback-buffer-friendly touch samples.

## Risks And Test Signals
Key risks are hardware-state races between direct reads, buffers, touch mode, and PM; incorrect EOC register selection for SoCs with separate EOC registers; DMA residue/timestamp math when no full sample is available; divide-by-zero in touch scale/pressure paths; invalid NVMEM calibration length; and maintaining ABI gaps for SAMA5D2 differential channels. The `at91_adc_set_watermark()` path calls `at91_adc_buffer_prepare()` after changing DMA state, so buffer lifecycle tests should cover watermark changes while enabled and disabled. Test signals include successful probe with all required properties and regulators, raw reads timing out cleanly when IRQs do not arrive, oversampling values limited to advertised lists, buffer enable rejecting mixed touch and voltage masks, external-trigger non-DMA capture producing ordered scans, DMA capture with watermark greater than one, suspend/resume with an active buffer, and SAMA7G5 temperature reads with and without a valid `temperature_calib` NVMEM cell.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/at91-sama5d2_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/at91_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/at91_adc.c

## Purpose
This is the older Atmel AT91 ADC driver for AT91SAM9260, AT91SAM9RL, AT91SAM9G45, AT91SAM9X5, and SAMA5D3-style ADC blocks. It exposes board-selected voltage channels through IIO direct reads and, when touchscreen support is not enabled, IIO triggered buffers and IIO triggers. On SoCs with touchscreen support it can instead register an input device and reserve ADC channels for 4-wire or 5-wire touch reporting.

## Important APIs, Types, And Functions
`struct at91_adc_caps` is the central compatibility table: it describes touchscreen availability, TSMR support, filtering/sensitivity, startup tick calculation, channel count, resolution choices, trigger descriptors, and register offsets/masks. `struct at91_adc_state` keeps clocks, channel mask, IRQ, selected channel, conversion waitqueue, trigger array, vref, resolution, touchscreen configuration, and cached touchscreen coordinates.

The main functions are `at91_adc_probe()`, `at91_adc_remove()`, `at91_adc_read_raw()`, `at91_adc_channel_init()`, `at91_adc_trigger_init()`, `at91_adc_configure_trigger()`, `at91_adc_trigger_handler()`, `at91_adc_rl_interrupt()`, `at91_adc_9x5_interrupt()`, `at91_ts_hw_init()`, `at91_ts_register()`, and suspend/resume callbacks. Startup timing is abstracted by `calc_startup_ticks_9260()` and `calc_startup_ticks_9x5()`.

## Control Flow
Probe reads device-tree properties for channel mask, sleep mode, startup time, sample-hold time, vref, optional external triggers, optional low-resolution mode, and optional touchscreen wiring/pressure threshold. It resets the ADC, disables all IRQs, requests the correct IRQ handler based on TSMR support, enables both clocks, calculates prescaler/startup/sample-hold mode register fields, builds dynamic IIO channel specs from `atmel,adc-channels-used` minus channels reserved for touch, initializes waitqueue/mutex, then either sets up IIO triggered buffers and triggers or registers/configures the input touchscreen device. Finally it registers the IIO device.

Direct raw reads serialize on `st->lock`, enable the requested channel and EOC IRQ, start conversion, wait up to one second for the IRQ path to set `done`, then disables channel/IRQ and returns the captured value or timeout. Triggered buffer setup writes the trigger value, enables all active channels, enables DRDY, and allocates a scan buffer. On DRDY, `handle_adc_eoc_trigger()` either polls the IIO trigger for buffered capture or completes a direct conversion. The poll handler reads active channel registers, pushes the timestamped scan, acknowledges DRDY via `LCDR`, and reenables the IRQ.

Touchscreen handling has two IRQ implementations. The older AT91RL path toggles pen/NOPEN IRQs, period triggers, and debouncing in `MR`, discards the first buffered measurement, and reports previous coordinates through input events. The 9x5/TSMR path enables pen/NOPEN and X/Y/pressure ready IRQs, starts periodic sampling, validates pen contact through `PENS`, calculates X/Y/pressure, and reports `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, and `BTN_TOUCH`.

## State And Persistence
No persistent storage is used. State lives in `struct at91_adc_state` and in hardware registers. `channels_mask` is derived from DT and modified to reserve touch channels. Direct conversions use `done`, `last_value`, and `chnb`; buffer mode uses allocated `st->buffer`; touchscreen mode tracks sample period, pressure threshold, debounce exponent, previous coordinates, and a flag for delayed reporting. Suspend only selects pinctrl sleep state and disables `clk`; resume reenables it and restores default pinctrl, without a full hardware reinitialization.

## Dependencies And Integration Points
The driver integrates with OF platform devices matching `atmel,at91sam9260-adc`, `atmel,at91sam9rl-adc`, `atmel,at91sam9g45-adc`, `atmel,at91sam9x5-adc`, and `atmel,sama5d3-adc`. It uses IIO core, triggered buffers, IIO trigger APIs, input subsystem for touchscreen mode, clocks, pinctrl sleep/default states, IRQs, waitqueues, and DT properties. The vref is supplied as a DT millivolt property rather than a regulator.

## Risks And Test Signals
Risks include divergence between SoC register maps, DT misconfiguration of channel masks or vref, lack of regulator-based vref validation, trigger cleanup with sparse trigger arrays, direct reads racing with buffers because direct mode is not explicitly claimed, touchscreen mode disabling ADC triggered-buffer support entirely, and limited suspend/resume restoration. Test signals include probe failure for missing required DT properties, correct channel reservation for 4-wire and 5-wire touch, raw-read timeout behavior, trigger registration only when external triggers are allowed, buffer scans across active channel masks, pen/NOPEN event sequencing on both IRQ variants, and resolution/scale correctness for lowres/highres configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/at91_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/axp20x_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/axp20x_adc.c

## Purpose
This driver exposes ADC channels from several X-Powers PMIC families through IIO: AXP192, AXP20x/AXP209, AXP22x/AXP221, AXP717, and AXP813. The channels represent PMIC temperature, AC input, VBUS, battery voltage/current, GPIO/TS pins, VMID, backup battery, and similar PMIC measurements. It is a direct-mode regmap-backed IIO provider for sibling power-supply and charger drivers.

## Important APIs, Types, And Functions
`struct axp20x_adc_iio` holds the parent PMIC regmap and selected `struct axp_data`. `struct axp_data` supplies the per-chip `iio_info`, channel table, ADC enable register masks, optional sample-rate setter, and IIO consumer maps. Channel macros define `IIO_CHAN_INFO_RAW`, `SCALE`, and optional `OFFSET` support. Read paths are chip-specific: `axp192_adc_raw()`, `axp20x_adc_raw()`, `axp22x_adc_raw()`, `axp717_adc_raw()`, and `axp813_adc_raw()`. Scale and offset are split by chip and type; only AXP192/AXP20x GPIO offsets are writable.

## Control Flow
Probe obtains the parent `struct axp20x_dev`, allocates the IIO device, chooses `axp_data` from firmware match data or platform ID, binds channels and `iio_info`, enables ADC blocks by writing `adc_en1` and optional `adc_en2`, optionally programs 100 Hz sampling, registers IIO consumer maps, and registers the IIO device. Remove unregisters the IIO device/maps and clears ADC enable registers.

Raw reads use PMIC register helpers. Most chips use `axp20x_read_variable_width()` with 12-bit or 13-bit widths depending on current-channel quirks. AXP717 is special: several channels share a generic ADC data register, so `axp717_adc_raw()` first selects TS, die temperature, VMID, or backup-battery input in `AXP717_ADC_DATA_SEL`, bulk-reads two bytes, and extracts the 14-bit value. Scale and offset callbacks return fixed values based on datasheet channel type and chip family; temp channels have fixed offsets for older families.

## State And Persistence
The driver has minimal state: a regmap pointer and immutable chip data. Hardware ADC enable bits persist in the PMIC while the driver is bound and are cleared on error/remove. Writable GPIO offset state is stored in PMIC registers (`AXP192_GPIO30_IN_RANGE` or `AXP20X_GPIO10_IN_RANGE`) and therefore persists at hardware register level until changed or reset by PMIC/firmware.

## Dependencies And Integration Points
It depends on the AXP20x MFD core for regmap and register definitions, IIO core, IIO machine maps, Linux bitfield helpers, unaligned access helpers, platform bus, and OF/platform ID matching. IIO maps connect ADC labels to `axp20x-usb-power-supply`, `axp20x-ac-power-supply`, and `axp20x-battery-power-supply` consumers.

## Risks And Test Signals
Risks include enabling/disabling the full ADC mask without preserving firmware state, chip-specific raw width mistakes, AXP717 mux selection races if multiple consumers read generic data channels concurrently, missing scale/offset for channels explicitly marked unknown, and assuming `platform_get_device_id()` is valid for `indio_dev->name` even in firmware-matched contexts. Test signals include chip-specific channel count/name exposure, raw reads for 12/13/14-bit channels, GPIO offset read/write acceptance only for valid values, IIO map registration rollback clearing ADC enables, and remove clearing both enable registers where present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/axp20x_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/axp288_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/axp288_adc.c

## Purpose
This is the X-Powers AXP288 PMIC ADC driver used on Intel-era tablet platforms. It exposes six direct-mode IIO channels: TS pin temperature, PMIC temperature, GPADC/system temperature, battery charge current, battery discharge current, and battery voltage. It also registers IIO maps for AXP288 battery, charger, PMIC, and GPADC consumer drivers.

## Important APIs, Types, And Functions
`struct axp288_adc_info` stores the parent regmap, IRQ number, a mutex for serialized device access, and whether the TS pin is enabled. `axp288_adc_read_channel()` bulk-reads two PMIC bytes and assembles a 12-bit value. `axp288_adc_set_ts()` temporarily changes the TS current-source mode when reading the GPADC. `axp288_adc_initialize()` applies DMI quirks, detects TS enable state, sets TS current-source mode, and enables all non-TS ADC channels. `axp288_adc_read_raw()` is the IIO callback.

## Control Flow
Probe allocates an IIO device, gets the platform IRQ, obtains the parent AXP20x regmap, initializes ADC hardware, binds channels and IIO info, registers consumer maps, initializes the mutex, and registers the device with devm cleanup. Raw reads lock the mutex, switch TS current source to on-demand for GPADC reads when the TS pin is enabled, read the selected register pair, then restore the current source to always-on for TS before unlocking.

## State And Persistence
The driver intentionally leaves ADCs enabled across system suspend because disabling them can affect internal fuel-gauge behavior. State is limited to `ts_enabled` and the mutex. Firmware/DMI state matters: DMI overrides may modify TS bias current on known machines with broken firmware. The driver does not implement remove-time ADC disable because devm registration and the platform PMIC behavior assume always-on ADC support while bound.

## Dependencies And Integration Points
It depends on the AXP20x MFD regmap/register definitions, DMI matching, IIO core, IIO machine maps, and platform IDs. Consumer maps target `axp288-batt`, `axp288-pmic`, `axp288-gpadc`, and `axp288-chrg`.

## Risks And Test Signals
Risks include upsetting charger/fuel-gauge behavior by mishandling the TS current source, incomplete DMI quirk coverage, ignoring errors when restoring TS current-source mode after reads, and lack of scale/offset conversions. Test signals include successful DMI bias override on listed systems, GPADC nonzero readings when TS is enabled, TS current-source restore after failed and successful reads, all consumer maps present, and raw channel values assembled from the high nibble layout.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/axp288_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/bcm_iproc_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/bcm_iproc_adc.c

## Purpose
This driver exposes the Broadcom iProc static ADC as an eight-channel direct-mode IIO voltage device. The ADC shares register space and an interrupt line with touchscreen IP, so the driver uses syscon/regmap and shared IRQ filtering. Reads are snapshot conversions per channel with completion signaled by per-channel watermark interrupts.

## Important APIs, Types, And Functions
`struct iproc_adc_priv` holds the syscon regmap, ADC clock, mutex, IRQ number, selected channel/value, and completion. `iproc_adc_enable()` powers LDO/ADC/bandgap, enables the controller, and clears channel interrupt masks/status. `iproc_adc_do_read()` performs the snapshot conversion sequence. `iproc_adc_interrupt_thread()` filters shared interrupts and wakes the threaded handler only for ADC channel bits; `iproc_adc_interrupt_handler()` reads FIFO status/data and completes pending reads. `iproc_adc_read_raw()` exposes raw and fixed scale.

## Control Flow
Probe allocates the IIO device, initializes mutex/completion, looks up the `adc-syscon` regmap, gets the `tsc_clk`, gets the shared IRQ, disables AUXIN scan, requests a threaded shared IRQ, enables the clock, powers/configures the ADC, fills the IIO metadata, and registers the device. A raw read locks the mutex, records the channel, clears pending ADC/AUX status, configures the selected channel for snapshot mode with one round and watermark one, enables the per-channel watermark interrupt and top-level interrupt mask, retries the top-level mask write if hardware does not latch it, then waits up to two seconds for completion. On success it returns the low 16 bits of channel data; on failure it disables and clears interrupt state and dumps registers.

## State And Persistence
State is volatile: current channel/value and completion are used for a single in-flight read, protected by the mutex. Hardware power/controller state is enabled at probe and disabled at remove. No runtime PM is implemented, so the ADC clock remains prepared while bound.

## Dependencies And Integration Points
The driver depends on platform/OF compatible `brcm,iproc-static-adc`, syscon regmap via `adc-syscon`, the `tsc_clk` clock, shared IRQs, completions, IIO core, and regmap bit helpers. It provides eight `IIO_VOLTAGE` channels named `adc0` through `adc7` with scale `1800 / 2^10`.

## Risks And Test Signals
Risks include shared IRQ misclassification, stale channel data if completion arrives after timeout, interrupt mask write unreliability, no runtime clock gating, and a suspicious macro typo in `IPROC_ADC_CHANNEL_FULL_INTR_MASK` referencing `IPROC_ADC_IPROC_ADC_CHANNEL_FULL_INTR` though it is unused. Test signals include successful syscon lookup, read timeout cleanup, register dump on failure, IRQ filter returning `IRQ_NONE` for touchscreen-only events, raw reads on all eight channels, and scale reporting as fractional-log2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/bcm_iproc_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/berlin2-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/berlin2-adc.c

## Purpose
This Marvell Berlin2 driver exposes system-manager ADC channels through IIO. It provides raw voltage reads for external/reserved ADC inputs and a processed temperature channel using the integrated temperature sensor. It is direct-mode only and uses separate ADC and temperature-sensor IRQs.

## Important APIs, Types, And Functions
`struct berlin2_adc_priv` stores the parent syscon regmap, a mutex, waitqueue, `data_available`, and captured data. `berlin2_adc_read()` performs single ADC conversions. `berlin2_adc_tsen_read()` performs temperature-sensor conversions. `berlin2_adc_read_raw()` dispatches raw voltage and processed temperature reads. `berlin2_adc_irq()` and `berlin2_adc_tsen_irq()` capture data-ready values and wake waiters. `berlin2_adc_powerdown()` is a devm cleanup action.

## Control Flow
Probe gets the parent node regmap, requests named IRQs `adc` and `tsen`, initializes waitqueue/mutex, sets IIO metadata, powers the ADC by setting `BERLIN2_SM_CTRL_ADC_POWER`, registers a cleanup action to power it down, and registers the IIO device. A voltage read enables the channel interrupt, selects the ADC channel, starts conversion, waits up to one second for `data_available`, disables the interrupt, clears start, copies the latched data, and returns it. A temperature read enables TSEN interrupt, configures ADC rotate and TSEN trim/settling/start, waits similarly, stops TSEN, sign-adjusts the 12-bit-ish value when over 2047, and converts it to milli-Celsius.

## State And Persistence
There is no persistent state. `data_available` and `data` are shared by ADC and TSEN paths and serialized with `priv->lock`, preventing simultaneous reads. Hardware ADC power remains on while the driver is bound and is cleared by devm cleanup.

## Dependencies And Integration Points
The driver integrates with OF compatible `marvell,berlin2-adc`, platform named IRQs, parent syscon regmap, IIO core, and waitqueues. The channel table includes six voltage-ish channel numbers, one processed temperature channel, one reserved voltage channel, and a soft timestamp channel even though no buffer setup is provided.

## Risks And Test Signals
Risks include shared `data_available` state across two IRQ sources, raw channel table exposing reserved channels, no scale for voltage channels, reliance on parent-node syscon layout, and no explicit handling of interrupted waits beyond propagating negative return. Test signals include named IRQ availability, ADC power cleanup on probe failure/remove, raw conversion timeout, TSEN conversion formula sanity, and no cross-talk between concurrent voltage and temperature reads under the mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/berlin2-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/cc10001_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/cc10001_adc.c

## Purpose
This driver supports the Cosmic Circuits 10001 ADC as an eight-channel 10-bit voltage IIO device. It supports direct raw reads and triggered buffered scans. The ADC can be either private to this CPU, in which case the driver powers it up/down around conversions, or shared with another CPU, in which case reserved channels are removed and the ADC is kept powered.

## Important APIs, Types, And Functions
`struct cc10001_adc_device` stores MMIO base, ADC clock, vref regulator, scan buffer, shared-mode flag, mutex, and calculated timing delays. `cc10001_adc_power_up()`, `cc10001_adc_power_down()`, `cc10001_adc_start()`, and `cc10001_adc_poll_done()` implement the conversion protocol. `cc10001_adc_read_raw()` handles direct raw/scale reads. `cc10001_adc_trigger_h()` performs buffered scans. `cc10001_update_scan_mode()` allocates the scan buffer. `cc10001_adc_channel_init()` builds channel specs from the usable channel map.

## Control Flow
Probe builds an initial eight-channel mask, applies `adc-reserved-channels` if present and marks shared mode, enables the `vref` regulator, maps MMIO, enables the `adc` clock, computes nanosecond wait intervals from the clock rate, powers up immediately for shared mode, registers powerdown/regulator cleanup actions, builds IIO channels plus timestamp, initializes the mutex, sets up a triggered buffer, and registers the IIO device. Direct reads reject access while a buffer is enabled, lock, optionally power up, start one conversion, poll EOC and sampled-channel confirmation up to fixed retry counts, optionally power down, unlock, and return raw data or `-EIO`. Buffered scans lock, optionally power up, iterate active channels, start/poll each conversion, fill the allocated buffer, optionally power down, unlock, and push the scan only if all samples are valid.

## State And Persistence
State is volatile and mostly hardware-facing. The scan buffer is reallocated on scan-mode updates. Shared mode keeps the ADC powered for the driver's lifetime; private mode powers around each read/scan. The vref regulator and clock are enabled for the device lifetime via devm cleanup.

## Dependencies And Integration Points
The driver depends on OF compatible `cosmic,10001-adc`, MMIO resources, `adc` clock, `vref` regulator, IIO core, IIO triggered buffers, and optional DT `adc-reserved-channels`. Scale comes from the regulator voltage divided by `2^realbits`.

## Risks And Test Signals
Risks include polling-only conversion with fixed retry counts, possible buffer allocation churn in `update_scan_mode()`, shared-mode assumptions with another CPU, no IRQ completion path, and returning `-EBUSY` for direct reads whenever buffering is enabled. Test signals include reserved-channel masks reflected in sysfs, zero clock-rate probe failure, scale changes following vref voltage, direct reads for all unreserved channels, triggered scans with sparse masks, and invalid sample warnings when EOC or sampled-channel confirmation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/cc10001_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/cpcap-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/cpcap-adc.c

## Purpose
This Motorola CPCAP PMIC ADC driver exposes 18 IIO channels for battery temperature/voltage, VBUS, die temperature, system/battery currents, USB ID, bank1 auxiliary inputs, and two remuxed channels. It provides raw and processed reads, including calibration, phasing, temperature lookup, and conversion tables derived from older Motorola kernel behavior.

## Important APIs, Types, And Functions
`struct cpcap_adc` holds the PMIC regmap, device, vendor, IRQ, mutex, timing table, waitqueue, and completion flag. Channel behavior is encoded in `bank_phasing[]` and mutable `bank_conversion[]`; per-board timings come from `struct cpcap_adc_ato` match data. `cpcap_adc_calibrate()` and `cpcap_adc_calibrate_one()` populate calibration offsets. `cpcap_adc_setup_bank()`, `cpcap_adc_start_bank()`, and `cpcap_adc_stop_bank()` control conversions. `cpcap_adc_phase()` and `cpcap_adc_convert()` post-process readings. `cpcap_adc_read()` is the IIO callback.

## Control Flow
Probe requires OF match data for timing configuration, initializes state, gets the parent regmap and CPCAP vendor, requests the `adcdone` threaded IRQ, calibrates charge/system current channels, and registers the IIO device. The IRQ thread disables further ADC trigger interrupts, sets `done`, and wakes the waitqueue. For each raw or processed read, the driver initializes a request, locks, starts an immediate conversion with up to five 50 ms retry attempts, reads either the channel register or scaled bank result, restores default ADCC1/ADCC2 state, unlocks, and returns the value. Processed reads apply ST-specific die-temperature math for AD3 or generic phasing/conversion logic for other channels.

## State And Persistence
No files are persisted, but `bank_conversion[]` is global mutable state updated by calibration and by TI vendor reads. This means calibration offsets are shared across device instances, though CPCAP is effectively a singleton PMIC in expected systems. Runtime state includes the waitqueue `done` flag and register setup that is restored after each read. Calibration offsets depend on vendor and measured calibration registers.

## Dependencies And Integration Points
The driver depends on Motorola CPCAP MFD regmap/register definitions, `cpcap_get_vendor()`, platform named IRQ `adcdone`, OF compatibles `motorola,mapphone-cpcap-adc` and `motorola,mot-cpcap-adc`, IIO core, and IIO buffer headers even though no triggered buffer setup is registered. Channels use `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_PROCESSED`.

## Risks And Test Signals
Risks include sparse public documentation, global mutable calibration tables, retry/timeout behavior during ADC start, vendor-specific calibration differences, thermal lookup-table assumptions, and the base compatible without match data returning `-ENODEV`. Test signals include successful calibration offsets for non-TI vendors, TI path using ADCAL registers dynamically, processed battery/current voltage values within table min/max clamps, AD0 thermbias enable delay, timeout after repeated conversion attempts, and default register restoration after failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/cpcap-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/da9150-gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/da9150-gpadc.c

## Purpose
This Dialog DA9150 GPADC driver exposes GPIO, USB/battery/system voltage, bus current, battery temperature, and junction temperature measurements through IIO. It is a platform child of the DA9150 MFD and provides default IIO maps consumed by the DA9150 charger driver.

## Important APIs, Types, And Functions
`struct da9150_gpadc` stores the parent DA9150 device, local device pointer, mutex, and completion. `da9150_gpadc_irq()` completes conversions. `da9150_gpadc_read_adc()` selects a hardware mux channel, waits briefly for completion, reads result/status bytes, and assembles a 10-bit result. `da9150_gpadc_read_processed()`, `da9150_gpadc_read_scale()`, and `da9150_gpadc_read_offset()` implement channel conversions. `da9150_gpadc_read_raw()` is the IIO callback.

## Control Flow
Probe gets the parent `struct da9150`, initializes mutex/completion, requests named IRQ `GPADC`, registers IIO maps for charger channels, fills direct-mode IIO metadata, and registers the device. Reads validate channel number, then either perform processed/raw conversion or return scale/offset. `da9150_gpadc_read_adc()` locks, writes `DA9150_GPADC_MAN` with enable and mux selection, clears stale completion with `try_wait_for_completion()`, waits up to 5 ms, bulk-reads result registers, unlocks, checks the RUN bit for timeout, then combines LSB/MSB fields.

## State And Persistence
State is per-device and volatile. Completion objects can retain stale signals, explicitly consumed before each conversion. No remove callback is needed because all resources are devm-managed. Hardware conversion configuration is written per read.

## Dependencies And Integration Points
The driver depends on DA9150 MFD core/register helpers, platform named IRQ `GPADC`, IIO core, IIO machine maps, and charger consumers using map names `CHAN_IBUS`, `CHAN_VBUS`, `CHAN_TJUNC`, and `CHAN_VBAT`.

## Risks And Test Signals
Risks include ignoring the return value of `wait_for_completion_timeout()` and relying on the RUN bit for timeout detection, very short 5 ms wait budget, channel pairs with underscore hardware IDs, and mixed semantics where RAW and PROCESSED both call the processed helper for many channels. Test signals include timeout logging with RUN bit set, correct conversion formulas for GPIO/IBUS/VBUS/VSYS, scale/offset only for VBAT and junction temperature channels, and default charger map registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/da9150-gpadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/dln2-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/dln2-adc.c

## Purpose
This driver exposes the Diolan DLN-2 USB ADC adapter as an IIO voltage device. It supports direct reads, configurable sampling frequency, and triggered buffered capture driven by DLN2 firmware events. The hardware protocol is command-based through the DLN2 MFD transport rather than local MMIO.

## Important APIs, Types, And Functions
`struct dln2_adc` stores the platform device, fixed channel specs, port number, trigger channel, IIO trigger, mutex, cached sample period, and a compact demux table. Protocol helpers include `dln2_adc_get_chan_count()`, `dln2_adc_set_port_resolution()`, `dln2_adc_set_chan_enabled()`, `dln2_adc_set_port_enabled()`, `dln2_adc_set_chan_period()`, `dln2_adc_read()`, and `dln2_adc_read_all()`. Buffer flow is handled by `dln2_update_scan_mode()`, `dln2_adc_triggered_buffer_postenable()`, `dln2_adc_trigger_h()`, `dln2_adc_triggered_buffer_predisable()`, and `dln2_adc_event()`.

## Control Flow
Probe reads platform port data, sets 10-bit resolution, queries channel count and clamps to eight, builds channel specs plus timestamp, allocates/registers an immutable IIO trigger, sets up a triggered buffer, registers a DLN2 event callback for condition-met events, and registers the IIO device. Direct raw reads claim IIO direct mode, lock, enable the channel and ADC port, read `DLN2_ADC_CHANNEL_GET_VAL` twice to work around an initial zero after enabling, then disables the port and channel. Buffered mode enables all channels selected in `update_scan_mode()`, builds a demux plan from the fixed eight-value firmware layout into the active scan layout, enables the ADC port on buffer postenable, uses the first active channel as the periodic trigger source, and on each DLN2 event reads all channel values, demuxes active values, and pushes a timestamped scan.

## State And Persistence
State is volatile but spans buffer lifetime: enabled channels in firmware, ADC port enable, trigger channel, sample period in milliseconds, and demux mapping. `sample_period` is cached as milliseconds derived from requested frequency and clamped to 65535 ms; zero frequency maps to `UINT_MAX` then clamps when applied. Remove unregisters the IIO device and DLN2 event callback.

## Dependencies And Integration Points
The driver depends on the DLN2 MFD command/event transport, platform data for port selection, IIO core, immutable IIO triggers, triggered buffers, kfifo buffer support, and firmware event `DLN2_ADC_CONDITION_MET_EV`. It advertises fixed 3.3 V / 10-bit scale as `IIO_VAL_INT_PLUS_NANO`.

## Risks And Test Signals
Risks include firmware command failures leaving channels enabled, conflict masks when ADC pins are shared with other DLN2 functions, sample-period unit conversions with low frequencies, the event callback running from URB completion context and only polling the trigger, and demux assumptions around eight fixed values. Test signals include protocol short-response `-EPROTO`, conflict mask turning into `-EBUSY`, direct reads disabling channel/port on all error paths, sparse scan masks demuxing correctly, periodic event capture at configured sample frequencies, and cleanup unregistering the event callback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/dln2-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/envelope-detector.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/envelope-detector.c

## Purpose
This is a synthetic IIO ADC-like driver for an envelope detector built from an external DAC and comparator interrupt. It estimates the peak level of an alternating input signal by binary-searching DAC output levels and observing whether the comparator trips during a configurable interval. It exposes a single `IIO_ALTVOLTAGE` raw channel and forwards scale from the DAC.

## Important APIs, Types, And Functions
`struct envelope` holds comparator latch state protected by a spinlock, a read mutex, comparator IRQ and trigger polarities, the consumed DAC IIO channel, delayed work for compare timeout, `compare_interval`, `invert`, DAC maximum, binary-search bounds, and completion. `envelope_detector_comp_isr()` latches comparator events and disables the IRQ. `envelope_detector_comp_latch()` reads/clears the latch and carefully reenables/synchronizes IRQ state. `envelope_detector_setup_compare()` and `envelope_detector_timeout()` implement the binary search. `envelope_detector_read_raw()` exposes raw/scale reads. Extended attributes `invert` and `compare_interval` are implemented through sysfs ext_info.

## Control Flow
Probe allocates an IIO device, initializes locks/completion/delayed work, obtains the `dac` IIO channel, requests named IRQ `comp`, derives inverse IRQ trigger polarity, validates that the DAC channel type is voltage, reads the DAC raw maximum, and registers the IIO device. A raw read locks `read_lock`, initializes binary-search bounds based on invert mode, starts comparison setup, waits for completion, returns either a negative error latched into `level` or the found raw value adjusted for inversion. Each search step writes a safe DAC extreme, clears comparator latch, writes the candidate DAC level, schedules delayed work, and after the interval adjusts low/high based on latch state until adjacent bounds complete the search.

## State And Persistence
There is no persistent state. Runtime tunables are `invert` and `comp_interval`; both are mutable through IIO extended attributes and protected by `read_lock`. The comparator latch is one-bit state in `env->comp`; the ISR disables IRQs until the latch is consumed to avoid interrupt floods. The completion is reused across reads; the binary search completes when bounds differ by one or a DAC write fails.

## Dependencies And Integration Points
The driver depends on a DAC exposed as an IIO consumer channel named `dac`, a platform IRQ named `comp`, IRQ trigger configuration support for inversion, delayed work, completions, and IIO core. OF compatible is `axentia,tse850-envelope-detector`. The output scale is delegated to `iio_read_channel_scale()` on the DAC.

## Risks And Test Signals
Risks include waiting indefinitely because `wait_for_completion()` has no timeout, stale completion state if consecutive reads start after an error, IRQ polarity inversion not available on some interrupt controllers, DAC write failures being encoded through `env->level`, and comparator signals changing faster than `compare_interval`. Test signals include successful rejection of non-voltage DAC channels, presence of DAC max raw value, raw reads converging within `log2(dac_max)` delayed-work steps, invert toggling changing IRQ type and output mapping, compare interval rejecting values above 1000 ms, and no IRQ flood while reads are idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/envelope-detector.c -->
