# subset-b-003874 research

Grouped research for the ADC driver sources listed in work item `subset-b-003874`. Each section is wrapped with the exact file-research markers expected by the reconciliation lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mp2629_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mp2629_adc.c

Purpose: this platform driver exposes the ADC block inside the MPS MP2629 charger MFD as an IIO direct-mode device. It provides battery/system/input voltage and battery/input current channels and registers IIO maps so the sibling `mp2629_charger` consumer can find named measurements.

Important APIs, types, and functions: `struct mp2629_adc` holds the parent regmap and device pointer. `MP2629_ADC_CHAN()` defines five simple channel specs with raw and type-shared scale information. `mp2629_read_raw()` reads one register through `regmap_read()`, masks the input-voltage status bit, and returns hard-coded per-channel scales. `mp2629_adc_probe()` obtains `struct mp2629_data` from the parent MFD, enables `MP2629_ADC_START | MP2629_ADC_CONTINUOUS`, registers IIO maps, and then registers the IIO device. `mp2629_adc_remove()` reverses IIO registration and clears continuous/start bits.

Control flow: probe is linear: allocate IIO state, bind the parent regmap, enable continuous ADC conversion, publish consumer maps, set channel metadata, and register with IIO. Raw reads are passive because conversions are already running. Error paths unregister maps and disable the ADC bits.

State and persistence: driver state is per-device and devm allocated. Persistent hardware state is limited to the ADC control register while the platform device is bound. There is no buffering, IRQ handling, runtime PM, or disk persistence.

Dependencies and integration points: it depends on the MP2629 MFD parent regmap, platform/OF binding `mps,mp2629_adc`, IIO core registration, and IIO machine maps consumed by charger code.

Risks: probe assumes the parent MFD driver data is valid. Raw reads trust continuously updated single-byte registers with no conversion-ready check. Remove and failure paths clear `START` separately from `CONTINUOUS`, so regmap failures during cleanup are ignored. Incorrect scales or register masks directly affect charger policy consumers.

Test signals: validate probe under the MP2629 MFD, IIO map lookup by the charger, raw reads for all five channels, scale values and `IIO_VAL_FRACTIONAL` current scaling, input-voltage masking, and cleanup that clears ADC enable bits on unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mp2629_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6359-auxadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6359-auxadc.c

Purpose: this driver exposes MediaTek PMIC AUXADC channels for several PMIC families, including MT6357, MT6358, MT6359, MT6363, and MT6373. It handles normal AUXADC voltage/current/temperature/resistance reads, battery impedance special cases, SPMI register-width differences, PMIC-specific channel tables, and optional external VIN channel selection.

Important APIs, types, and functions: `struct mt6359_auxadc` stores the regmap, chip descriptor, lock, and timeout recovery flag. `struct mtk_pmic_auxadc_chan` describes request/readiness registers, external selector state, averaging samples, and resistor ratios. `struct mtk_pmic_auxadc_info` selects channel arrays, register maps, reference voltage, PMIC bus mode, reset policy, and impedance callback. `mt6359_auxadc_sample_adc_val()` starts a request, waits for averaging, polls ready bits, and reconstructs 16-bit SPMI values when needed. `mt6359_auxadc_read_adc()` manages external selectors and unconditional stop. `mt6358_read_imp()` and `mt6359_read_imp()` implement impedance flows. `mt6359_auxadc_read_raw()` dispatches scale, normal reads, and impedance reads.

Control flow: probe picks match data, chooses the correct regmap parent for SPMI versus PMIC-wrapper devices, resets supported ADC blocks, then registers the chip-specific IIO channel table. Reads are serialized with `adc_dev->lock`; scale is computed from descriptor resistor ratios and chip VREF, while raw paths request conversion, wait/poll, stop conversion, mask to channel realbits, and update the timeout flag.

State and persistence: all mutable state is in the per-device structure and PMIC registers. `timed_out` persists across reads so a second timeout can trigger a reset on reset-capable PMICs. Energy or samples are not buffered in software.

Dependencies and integration points: it integrates with MT6397-style MFDs, SPMI MFD parents, Linux regmap, DT compatibles, MediaTek AUXADC dt-bindings, and IIO direct mode. External VIN channels depend on PMIC SDMADC selector bits and pullup settings.

Risks: register tables and channel descriptors must match each PMIC exactly; a wrong request or ready bit can hang reads. Stop failures can leave ADC sampling active and are only surfaced via later timeout recovery. SPMI high/low byte handling is easy to break. Impedance read paths use undocumented/partly unknown bits, so regressions need hardware validation. `no_reset` PMICs cannot recover from stuck ADCs through this driver.

Test signals: test every compatible's channel count, labels, scale math, normal raw conversions, SPMI byte reconstruction, external VIN selector cleanup, impedance VBAT/IBAT paths, repeated timeout reset behavior, and `-EOPNOTSUPP` on unsupported impedance channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6359-auxadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6360-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6360-adc.c

Purpose: this platform driver exposes the MT6360 PMU/charger ADC as an IIO direct-mode and triggered-buffer device. It provides voltage, current, temperature, and thermistor-reference channels using the parent regmap.

Important APIs, types, and functions: `struct mt6360_adc_data` stores the regmap, mutex, and per-channel last-off timestamps used to avoid stale samples. `mt6360_adc_read_channel()` selects a preferred channel, enables the ADC, waits long enough based on the previous off time, polls the report channel until it matches, reads the big-endian report value, then disables all per-channel enables and restores `NO_PREFER`. `mt6360_adc_read_scale()` provides per-channel scale values, including IBUS dependence on the input-current-limit register. `mt6360_adc_trigger_handler()` reads active scan channels sequentially into a timestamped buffer. `mt6360_adc_reset()` initializes idle wait and ADC enable state.

Control flow: probe obtains the parent regmap, allocates IIO state, initializes the lock, resets the ADC block, sets channel metadata, installs a triggered buffer, and registers the device. Direct and buffered reads share `mt6360_adc_read_channel()`, so the single hardware control path is serialized by `adc_lock`.

State and persistence: hardware state includes ADC enable bits, preferred channel, idle wait, and report registers. Software persists last-off timestamps to choose 25 ms versus 75 ms pre-wait. No data survives device removal.

Dependencies and integration points: it depends on the MT6360 parent MFD regmap, platform/OF compatible `mediatek,mt6360-adc`, IIO buffers, trigger consumer support, and charger registers for current scaling.

Risks: background ADC users for VBAT and TS can collide with requested channels, making the report-channel polling logic critical. Cleanup writes in `out_adc_conv` ignore failures. Buffered scans can be slow because each active channel performs a complete serialized conversion. Scale for IBUS depends on live charger configuration, so users must not cache it blindly.

Test signals: probe/reset, raw reads for all channels, report-channel mismatch timeout, interrupted sleep returning `-ERESTARTSYS`, IBUS scale below and above 400 mA AICR, temperature offset, triggered-buffer scans, and concurrent direct reads returning serialized values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6360-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6370-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6370-adc.c

Purpose: this platform driver exposes MT6370/RT5081-family charger ADC measurements through IIO. It supports charger voltage, bus/battery current, battery thermistor, and junction-temperature channels using synchronous one-shot conversions through the parent regmap.

Important APIs, types, and functions: `struct mt6370_adc_data` holds the regmap, device, ADC mutex, and vendor ID. `mt6370_adc_read_channel()` writes `MT6370_REG_CHG_ADC` with start and input-select bits, sleeps for conversion time, polls until the start bit clears, then reads the big-endian ADC result. `mt6370_get_vendor_info()` reads the vendor nibble and affects current scales. `mt6370_adc_read_scale()` adjusts IBUS and IBAT scales based on vendor and live AICR/ICHG register fields. `mt6370_adc_read_offset()` exposes the fixed temperature offset.

Control flow: probe gets the parent regmap, initializes state and mutex, reads vendor information, resets the ADC selector/start register to zero, then registers a direct-mode IIO device with fixed channel specs. All raw conversions take the ADC lock, so concurrent channel reads cannot interleave selector/start writes.

State and persistence: only the vendor ID is cached in software. Hardware state is the charger ADC control register and charger current-limit registers used for scale. There is no triggered buffer, interrupt handler, PM callback, or persistent storage.

Dependencies and integration points: it uses the MT6370 parent regmap, DT binding constants from `mediatek,mt6370_adc.h`, platform/OF binding `mediatek,mt6370-adc`, Linux bitfield helpers, and IIO direct mode.

Risks: conversion is delay/poll based; a stuck start bit returns an error after roughly three conversion windows. Scale values are coupled to charger current configuration and vendor ID, so wrong `DEV_INFO` decoding yields wrong current units. The offset helper returns `-20` for all channels even though only `TEMP_JC` advertises offset.

Test signals: validate vendor ID decoding for RT5081, RT5081A, MT6370, and fallback IDs; raw conversion success and timeout; scale changes across AICR/ICHG thresholds; label strings; temperature offset; and concurrent reads serialized by `adc_lock`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6370-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6577_auxadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mt6577_auxadc.c

Purpose: this platform driver supports MediaTek SoC AUXADC MMIO blocks. It exposes 16 voltage channels as processed millivolt readings and handles clock enable, power-down control, optional global-idle polling, and suspend/resume power management.

Important APIs, types, and functions: `struct mt6577_auxadc_device` stores MMIO base, main clock, mutex, and compatible quirks. `struct mtk_auxadc_compatible` controls whether sample calibration and global idle checks are used. `mt6577_auxadc_mod_reg()` performs read/modify/write on MMIO registers. `mt6577_auxadc_read()` clears a channel request, waits for the old ready bit to clear, sets the request bit, waits for sample timing, optionally polls global idle, then waits for ready and returns masked raw data. `mt6577_auxadc_read_raw()` converts raw 12-bit samples to millivolts using a 1500 mV full range.

Control flow: probe allocates the IIO device, maps registers, enables the `main` clock, checks the rate, stores match data, powers up the ADC by clearing PDN, registers a devm power-off action, and registers with IIO. Suspend sets PDN and disables the clock; resume enables the clock and powers up again.

State and persistence: software state is per-device and protected by a mutex during sampling. Hardware state includes request bits, ready bits, power-down bit, and clock state. There is no buffered mode or saved calibration table.

Dependencies and integration points: it depends on platform resources, clocks, MMIO polling helpers, device-property match data, OF compatibles for several MediaTek SoCs, and IIO direct mode.

Risks: calibration is currently a stub returning raw data, so compatibles with `sample_data_cali` do not apply real correction. The read path can return `-ETIMEDOUT` at three separate wait points. Clock-rate validation only rejects zero. Register offsets assume a fixed 0x04 stride across 16 channels.

Test signals: boot/probe for each compatible quirk, processed values on all channels, old-ready clear timeout, global-idle timeout on MT8173-style devices, suspend/resume reads, power-off devm action, and conversion scaling against known input voltages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mt6577_auxadc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mxs-lradc-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mxs-lradc-adc.c

Purpose: this is the general-purpose ADC child driver for Freescale/NXP MXS LRADC MFD hardware on i.MX23 and i.MX28. It supports direct raw reads, die-temperature calculation, configurable input range through divide-by-two, IRQ-driven completion, and triggered buffered sampling through LRADC delay channel 0.

Important APIs, types, and functions: `struct mxs_lradc_adc` carries the parent LRADC descriptor, MMIO base, completion, spinlock, trigger, scale table, and per-channel divider bitmap. `mxs_lradc_adc_read_single()` claims direct mode, maps the requested physical channel into virtual channel 0, configures divide-by-two, starts conversion, waits up to one second for IRQ completion, and reads `LRADC_CH(0)`. `mxs_lradc_adc_read_temp()` subtracts channel 8 from channel 9. Buffer setup functions map active scan channels to LRADC slots and delay triggers. `mxs_lradc_adc_validate_scan_mask()` rejects touchscreen/touchbutton-reserved channels and too many mapped channels.

Control flow: probe maps the child memory resource, resets the block, requests all named IRQs, initializes an IIO trigger and triggered buffer, computes scale availability for both divider states, initializes delay channel 0 and temperature sensing, then registers IIO. IRQ handling either completes direct reads or polls the trigger for buffered mode.

State and persistence: runtime state includes selected divide-by-two bits, active buffered channel mapping, delay channel programming, and completion state. Remove unregisters IIO, stops delay channel 0, cleans up the buffer, and unregisters the trigger.

Dependencies and integration points: it integrates with `linux/mfd/mxs-lradc.h`, parent LRADC SoC metadata, OF IRQ mapping, STMP reset helpers, IIO triggered buffers, and sysfs scale-available attributes.

Risks: direct and buffered modes are mutually exclusive via `iio_device_claim_direct()`. IRQ mapping uses parent OF IRQ indexes and named platform IRQs, so DT mistakes fail probe. Buffered mode assumes LRADC virtual channel ordering matches active scan order. Reserved touchscreen/touchbutton channel checks are essential to avoid stealing channels from sibling functions.

Test signals: direct reads on all valid voltage channels, temperature raw/scale/offset, scale write and readback for divider states, buffer enable/disable with multiple scan masks, rejection of reserved channels, timeout when IRQ never completes, and remove cleanup of trigger/buffer/hardware delay state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mxs-lradc-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nau7802.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/nau7802.c

Purpose: this I2C driver supports the Nuvoton NAU7802 two-channel 24-bit ADC. It exposes raw voltage, scale/gain selection, sample-frequency selection, optional interrupt-driven end-of-conversion handling, and polling fallback.

Important APIs, types, and functions: `struct nau7802_state` stores the I2C client, last sign-extended conversion, locks, VREF, conversion counter, sample-rate index, scale table, and completion. `nau7802_read_conversion()` reads three ADC bytes and sign-extends bit 23. `nau7802_sync()` toggles conversion synchronization through the CS bit. `nau7802_eoc_trigger()` handles level IRQs by checking CR, reading conversion data, and completing after `NAU7802_MIN_CONVERSIONS`. `nau7802_read_irq()` and `nau7802_read_poll()` implement the two wait strategies. `nau7802_read_raw()` selects channel and dispatches raw, scale, or sample-frequency reads.

Control flow: probe resets the chip, powers digital and analog sections, reads `nuvoton,vldo`, configures AVDD/LDO behavior, computes scale choices for gains, optionally requests a no-auto-enable threaded IRQ, defaults polling mode to 320 SPS, and registers two IIO channels. Raw reads lock the device, update channel/sample registers if needed, flush one conversion, then wait for enough conversions to avoid cross-channel settling artifacts.

State and persistence: `conversion_count` persists across reads until channel, gain, or sample rate changes. `last_value` is protected separately by `data_lock` because IRQ and read paths can access it. Hardware continuously converts once powered.

Dependencies and integration points: it depends on SMBus byte operations, optional client IRQ, firmware property `nuvoton,vldo`, IIO sysfs attributes, and OF/I2C IDs.

Risks: probe returns the raw PUCTRL value if PUR is not set, which may be a positive non-error value. IRQ mode requires a controller that supports level-high behavior; otherwise it falls back to polling. Scale selection compares only fractional nanovalues, assuming integer zero. VREF defaults to zero if firmware omits `nuvoton,vldo`, making scales unusable.

Test signals: reset/power-up, both channel reads after large input deltas, IRQ and polling modes, sample-frequency writes for all accepted values, gain/scale writes, sign extension of negative ADC codes, missing/invalid VLDO firmware behavior, and IRQ allocation failure fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nau7802.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nct7201.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/nct7201.c

Purpose: this I2C driver supports Nuvoton NCT7201 and NCT7202 voltage-monitor chips. It exposes raw VIN measurements, a fixed voltage scale, optional rising/falling threshold event configuration, and IRQ-driven alert events.

Important APIs, types, and functions: `struct nct7201_chip_info` stores two regmaps, channel count, and cached enable mask. Separate 8-bit and 16-bit regmap configurations model control/status versus VIN data/limit registers. `nct7201_read_raw()` reads a 16-bit VIN register and extracts bits 15:3. Event helpers read and write high/low limit registers and maintain `vin_mask` through `NCT7201_REG_CHANNEL_ENABLE`. `nct7201_init_chip()` resets the chip, waits for power-up, enables all model channels, reads back the mask, and starts monitoring. `nct7201_irq_handler()` reads interrupt status and pushes a generic threshold event.

Control flow: probe resolves model data, initializes both regmaps, calls chip initialization, sets channel metadata, optionally unmasks alerts and requests a threaded low-level IRQ, and registers the IIO device. Without an IRQ, the device exposes raw reads only through `nct7201_info_no_irq`.

State and persistence: the cached little-endian `vin_mask` reflects which VIN channels are enabled for monitoring and event configuration. Hardware monitoring runs continuously after START is set. Limit registers and channel-enable state persist while powered.

Dependencies and integration points: it uses I2C regmap, OF/I2C match data for model channel counts, IIO event APIs, and optional board IRQ wiring for alerts.

Risks: event enable mutates channel-enable state, so disabling an event also disables monitoring for that channel. The IRQ handler pushes a channel-0 either-direction event regardless of which VIN caused the interrupt. Endianness for `vin_mask` and bulk writes matters especially for 12-channel NCT7202. No explicit remove shutdown stops monitoring.

Test signals: probe both NCT7201 and NCT7202, raw reads from all channel registers, fixed scale, reset/power-up failure paths, high/low threshold read/write, channel-enable mask for 8 versus 12 channels, IRQ event emission, and no-IRQ mode hiding event operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nct7201.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/npcm_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/npcm_adc.c

Purpose: this platform driver exposes the ADC controller in Nuvoton NPCM7xx and NPCM8xx SoCs. It provides eight voltage channels, interrupt-driven single conversions, selectable internal/external reference voltage, and sample-frequency reporting.

Important APIs, types, and functions: `struct npcm_adc_info` describes data mask, internal reference, and resolution. `struct npcm_adc` stores MMIO registers, clock, wait queue, optional VREF regulator, reset control, lock, and interrupt status. `npcm_adc_isr()` acknowledges ADC interrupt status and wakes waiters. `npcm_adc_read()` selects a channel, starts conversion, waits up to 10 ms, resets the ADC block on stuck conversion, and returns masked data. `npcm_adc_read_raw()` serializes raw reads and returns scale from regulator voltage or internal VREF.

Control flow: probe allocates IIO state, maps MMIO, obtains reset and clock handles, computes sample rate from the existing divider, requests the IRQ, configures reference selection based on optional `vref`, initializes the wait queue, enables ADC and interrupt bits, starts conversion, and registers the IIO device. Remove unregisters IIO, clears ADC enable, disables the regulator, and disables the clock.

State and persistence: `int_status` is the wait condition for one conversion. Hardware state includes channel select, conversion bit, interrupt enable/status, reference select, reset line, and regulator state. No buffered data or persisted calibration exists.

Dependencies and integration points: it depends on platform MMIO resources, reset controller, clocks, optional regulator, IRQs, OF compatibles `nuvoton,npcm750-adc` and `nuvoton,npcm845-adc`, and IIO direct mode.

Risks: probe never calls `clk_prepare_enable()` before using or later disabling the clock, so clock-provider expectations should be checked against the wider tree. Timeout recovery resets the ADC and starts conversion but still returns `-ETIMEDOUT`. Optional regulator errors other than `-ENODEV` fail probe. Sample rate is read from boot-time divider state, not programmed by this driver.

Test signals: probe on both SoC data variants, external and internal reference modes, raw conversion completion IRQ, timeout/reset path, scale calculation with regulator voltage, sample-frequency reporting, concurrent user reads serialized by the mutex, and remove disabling ADC/regulator/clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/npcm_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nxp-sar-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/nxp-sar-adc.c

Purpose: this platform driver supports the NXP S32G2 SAR ADC. It provides eight 12-bit voltage channels, direct one-shot reads, configurable sample frequency, triggered buffers, software/cyclic-DMA buffering, calibration, and suspend/resume context restoration.

Important APIs, types, and functions: `struct nxp_sar_adc` stores MMIO and physical addresses, clock, completion, DMA channel and circular buffer, buffered channel list, VREF, and saved PM context. `nxp_sar_adc_set_enabled()` controls power-down state. `nxp_sar_adc_calibration()` powers the block, starts calibration, waits for completion/failure, and powers down. `nxp_sar_adc_read_channel()` enables one channel, unmasks IRQ, starts normal conversion, waits for completion, then disables everything. `nxp_sar_adc_dma_cb()` drains a cyclic DMA buffer into IIO buffers. Buffer pre/post enable functions select IRQ-triggered or software DMA behavior.

Control flow: probe maps registers, requests IRQ, enables the clock, initializes defaults instead of trusting reset values, calibrates, allocates coherent DMA memory, installs triggered-buffer callbacks, and registers IIO. Direct reads claim direct mode. Buffered reads enable active scan-mask channels, power the ADC, then either enable interrupts for trigger-driven reads or request/configure/start cyclic DMA for software buffers.

State and persistence: hardware state includes power, channel masks, interrupt masks, DMA masks, conversion timing, and NSTART/mode bits. Software tracks current direct channel, latest value, active buffered channels, DMA head/tail, and suspend-saved `inpsamp` and power state. There is no nonvolatile persistence.

Dependencies and integration points: it depends on platform resources, DMAengine cyclic slave support, IIO triggered buffers, clocks, PM sleep ops, OF compatible `nxp,s32g2-sar-adc`, and NXP register semantics.

Risks: DMA residue handling is subtle and guarded by comments about backend races. Calibration failure is logged but probe continues, so later accuracy may be degraded. Buffer mode must stop conversion before terminating DMA. Channel masks assume only group-0 channels 0-7 are usable despite timestamp index 32. Sample-frequency writes can divide by user-provided `val` without explicit zero rejection.

Test signals: direct reads, conversion timeout, calibration success and failure, sample-frequency read/write clamping, triggered-buffer scans, software DMA buffer enable/disable and residue edge cases, suspend/resume with active timing, and probe failures for missing IRQ/clock/DMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/nxp-sar-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/pac1921.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/pac1921.c

Purpose: this I2C driver supports the Microchip PAC1921 high-side power/current monitor. It exposes VBUS, VSENSE, derived current, and power channels, configurable gains through IIO scale writes, oversampling ratio, sampling frequency, overflow events, triggered buffers, shunt-resistor configuration, regulators, ACPI DSM parsing, and OF properties.

Important APIs, types, and functions: `struct pac1921_priv` stores regmap, VDD regulator, mutex, shunt value, gain/sample settings, overflow state, integration timing, current scales, and scan buffer. `pac1921_data_ready()` gates reads until the first integration after configuration finishes. `pac1921_check_push_overflow()` reads overflow status and emits enabled IIO threshold events. `pac1921_update_cfg_reg()` performs the READ-state/configure/re-enable-integration sequence and restarts validity timing. `pac1921_update_gain_from_scale()` maps scale writes to gain bits. `pac1921_init()` programs gains, filters, RIOV, free-run VPOWER mode, and integration enable.

Control flow: probe initializes regmap and mutex, reads shunt/label from ACPI or `shunt-resistor-micro-ohms`, computes current scales, enables VDD, waits for power-up, initializes hardware, installs a triggered buffer, and registers IIO. Raw reads and buffer scans lock the device, check data readiness, push overflow events, and read 10-bit result fields.

State and persistence: software tracks whether integration has started/completed, current gains, sample count, enabled overflow events, previous overflow flags, and mutable shunt-derived scales. Suspend disables integration, puts the chip to sleep, and disables VDD; resume reenables VDD and reinitializes registers.

Dependencies and integration points: it uses I2C regmap, regulator framework, IIO events/buffers, ACPI DSM GUID methods, OF property parsing, and PM sleep ops.

Risks: users can change shunt resistance at runtime, altering current/power scales without hardware validation. Reads return `-EBUSY` until the integration window elapses after init or configuration changes. Overflow events are edge-like in software based on previous flags and only checked during reads/buffer polls. ACPI DSM package shape is trusted.

Test signals: OF and ACPI probe paths, invalid shunt rejection, VDD enable/disable, first-read `-EBUSY` timing, scale write-to-gain updates, oversampling changes and sampling-frequency reporting, overflow event enable/push behavior, triggered-buffer scans, and suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/pac1921.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/pac1934.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/pac1934.c

Purpose: this I2C driver supports the Microchip PAC1931/PAC1932/PAC1933/PAC1934 multi-channel DC power/energy monitors. It dynamically builds IIO channels for active rails and exposes energy, power, voltage, current, average voltage/current, sample frequency, shunt attributes, ACPI/OF rail configuration, bidirectional measurements, periodic refresh, and cached register snapshots.

Important APIs, types, and functions: `struct pac1934_chip_info` stores channel configuration, shunts, labels, bidirectional flags, sample rate, delayed refresh work, and cached `struct reg_data`. `pac1934_chip_identify()` reads PID/MID/RID and selects channel count. `pac1934_acpi_parse_channel_config()` and `pac1934_fw_parse_channel_config()` populate active rails, shunts, labels, bipolar flags, and sample rate. `pac1934_chip_configure()` writes channel disable and bidirectional registers, configures sample rate, sends refresh, and schedules periodic refresh. `pac1934_reg_snapshot()` refreshes if requested, reads control and 76 bytes of measurement registers, decodes all enabled channels, and accumulates energy in software.

Control flow: probe identifies or falls back to match data, parses firmware, initializes the mutex, configures the chip, creates a dynamic set of six IIO channels per active physical channel, adds shunt sysfs attributes, takes an initial refresh/snapshot, and registers IIO. Reads call `pac1934_retrieve_data()`, which refreshes the cache only when it is older than 50 ms and keeps periodic refresh scheduled to avoid accumulator saturation.

State and persistence: cached measurement/control registers, accumulated per-second energy, shunt values, active/enabled energy flags, bidirectional flags, sample rate, labels, and refresh timestamp persist for the device lifetime. Delayed work periodically refreshes hardware and software cache; devm cleanup cancels it.

Dependencies and integration points: it uses raw I2C transfers and SMBus helpers, IIO direct mode/sysfs attributes, ACPI DSM UUID methods, firmware child nodes, Microchip PAC193x register layout, and system workqueues.

Risks: register layout has skipped addresses and block-read quirks, so offset math is fragile. Rev 2/3 bidirectional workaround must be preserved around refresh. Energy accumulation is software-maintained and clamped, so missed refreshes or wrong sample-rate shifts affect totals. Dynamic channel allocation depends on active-channel parsing; zero active channels would produce an unusable device. Runtime shunt writes change scales without reconfiguring hardware.

Test signals: identify each PAC193x variant, fallback compatible matching, ACPI and OF parsing, active-channel dynamic IIO layout, bipolar sign extension, refresh/cache timing, sample-rate writes, energy enable/reset behavior, shunt sysfs updates, delayed-work cancellation, and rev 2/3 refresh workaround.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/pac1934.c -->
