# subset-b-003878 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1298.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1298.c

Purpose: SPI IIO ADC driver for the TI ADS1298 family, including ADS129x/ADS129xR identification, direct single-channel reads, and software-buffered sampling driven by DRDY interrupts.

Important APIs/types/functions: `struct ads1298_private` holds SPI, regmap, regulators, optional clock, trigger/buffer state, DMA-safe buffers, completion, and a DRDY/SPI busy counter. `ads1298_probe()` powers supplies, resets the chip, initializes regmap and IIO buffering, requests the DRDY IRQ, and registers the IIO device. `ads1298_read_raw()`, `ads1298_write_raw()`, `ads1298_update_scan_mode()`, `ads1298_buffer_postenable()`, `ads1298_buffer_predisable()`, and `ads1298_interrupt()` form the core IIO flow. `ads1298_reg_read()` and `ads1298_reg_write()` back a maple-cached regmap.

Control flow: probe asserts reset, enables `vref` if external, enables `avdd`, configures SDATAC, reads ID to choose name/channel count, enables test/reference config, prepares the `RDATA` SPI message, then registers a kfifo buffer. Direct reads claim direct mode, power the requested channel, enable single-shot mode, issue START, wait on completion from DRDY/SPI completion, then decode signed 24-bit data. Buffered mode powers channels according to the scan mask, starts continuous conversions, and uses DRDY to schedule asynchronous SPI reads.

State and persistence: hardware configuration lives in chip registers and regmap cache; runtime sample state is in `rx_buffer`, `bounce_buffer`, completion, and `rdata_xfer_busy`. No disk persistence. Regulator enables and buffer state are undone through devm actions and buffer predisable.

Dependencies and integration: depends on SPI, regmap, GPIO reset, regulators, optional clock, IIO kfifo buffer, and IRQ. DT compatible is `ti,ads1298`; SPI id is `ads1298`.

Risks: `rdata_xfer_busy > 2` means samples were lost during SPI overrun; direct reads rely on a 50 ms DRDY timeout; register access is forced to slow SPI timing; IRQ is mandatory. Test signals include probe/init failures, `CMD_START` errors, direct read timeout, sample-rate/scale sysfs values, debugfs register access, and buffered scans under high DRDY rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads1298.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131e08.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131e08.c

Purpose: SPI IIO driver for TI ADS131E04/E06/E08 simultaneous-sampling delta-sigma ADCs with direct reads, triggered buffers, per-channel DT configuration, data-rate control, PGA gain, mux, and reference setup.

Important APIs/types/functions: `struct ads131e08_state` stores chip info, SPI, trigger, clock, optional external `vref`, per-channel config, data rate, timing delays, completion, and DMA-safe transfer buffers. `ads131e08_alloc_channels()` parses child nodes with `reg`, `ti,gain`, and `ti,mux`. `ads131e08_initial_config()` resets, exits continuous mode, programs data rate/reference/channel registers, powers unused channels down, and performs offset calibration. `ads131e08_read_raw()`, `ads131e08_write_raw()`, `ads131e08_trigger_handler()`, and `ads131e08_interrupt()` expose IIO behavior.

Control flow: probe obtains match data, allocates channels from firmware children, requests a falling-edge DRDY IRQ, registers an own IIO trigger, configures a triggered buffer, enables optional external vref and required `adc-clk`, derives SPI decode/reset delays from the clock, then applies initial configuration. Direct reads claim direct mode, issue START, wait up to the settling window for completion, read an RDATA frame, stop conversion, and sign-extend the selected channel. Buffered reads either consume own-trigger DRDY data or poll manually for external triggers.

State and persistence: `data_rate`, `readback_len`, `vref_mv`, and `channel_config` mirror hardware register state. Calibration is requested at init but not persisted by the driver. Runtime results reside in `rx_buf` and `tmp_buf`; no nonvolatile state is written.

Dependencies and integration: SPI, regulator, clock, IIO trigger/triggered buffer, firmware child nodes, and IRQ. Compatible strings cover `ti,ads131e04`, `ti,ads131e06`, and `ti,ads131e08`.

Risks: missing IRQ or missing channel children prevents probe; invalid firmware gain/mux/vref values reject the device; 32/64 kSPS use 16-bit data packed into a fixed 24-bit scan format with special sign-extension logic. Test signals include sampling-frequency availability, scale with internal/external vref, buffered scan packing at all rates, debugfs register access, and offset-calibration timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131e08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131m02.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131m02.c

Purpose: direct-mode SPI IIO driver for TI ADS131M02/M03/M04/M06/M08 24-bit differential ADCs, with input CRC, output CRC verification, optional external reference, optional hardware reset, and clock-source handling.

Important APIs/types/functions: `struct ads131m_configuration` describes per-variant channels, reset ACK, external reference support, and crystal support. `struct ads131m_priv` holds reusable full-frame SPI buffers, optimized message, scale values, config pointer, and a mutex. Protocol helpers include `ads131m_tx_frame_unlocked()`, `ads131m_read_reg_unlocked()`, `ads131m_write_reg_unlocked()`, `ads131m_check_status_crc_err()`, and `ads131m_verify_output_crc()`. `ads131m_adc_read()` and `ads131m_read_raw()` expose IIO raw/scale reads.

Control flow: probe selects variant data, creates a full-frame SPI message sized to channel count, enables `avdd`/`dvdd` and optional `refin`, enables the clock, resets via reset-control or SPI RESET, configures CLOCK for external reference or `clkin`/`xtal`, and enables CCITT input CRC in MODE. Reads send a NULL+CRC frame, inspect STATUS for prior CRC errors, verify output CRC over response and channel words, then sign-extend a 24-bit channel word.

State and persistence: scale numerator/denominator and `use_external_ref` are derived at probe and kept in memory. Hardware state is MODE/CLOCK register configuration and CRC state. Buffers are shared and protected by `lock`; there is no buffered capture path and no persistent storage.

Dependencies and integration: SPI, regulators, reset controller, common clock framework, crc-itu-t, IIO direct mode, and OF/SPI match tables for all ADS131M variants.

Risks: the command protocol is pipelined, so every register operation is multi-cycle and must stay mutex-serialized; hardware reset bypasses reset ACK identity validation; CRC mismatch returns `-EIO` but prior input CRC errors are only logged during data reads. Test signals include reset ACK mismatch, WREG ACK mismatch, CRC error injection, external-ref scale math, unsupported `xtal` on smaller packages, and raw reads for every channel count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads131m02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7138.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7138.c

Purpose: I2C IIO driver for TI ADS7128/ADS7138 8-channel ADCs with auto sequencing, oversampling, sampling-frequency control, min/max/recent statistics, threshold events, and runtime PM conversion-mode switching.

Important APIs/types/functions: `struct ads7138_data` stores I2C client, `avdd` regulator, chip data, and a mutex for read-modify-write operations. Low-level helpers implement the device opcode protocol: block read/write, single write, set bit, and clear bit. IIO hooks are `ads7138_read_raw()`, `ads7138_write_raw()`, `ads7138_read_avail()`, event value/config accessors, `ads7138_event_handler()`, `ads7138_init_hw()`, and runtime suspend/resume callbacks.

Control flow: probe allocates IIO state, requests optional threaded IRQ, resets the chip, switches to auto mode, enables statistics and digital window comparator, enables all channels in auto sequence, starts sequencing, and registers IIO. Raw reads fetch the recent channel register pair; peak/trough read max/min registers. Writes program sampling frequency bits or OSR. Event configuration sets per-channel alert bits, and IRQ handling reads event flags, pushes rising/falling IIO events, then clears high/low flags.

State and persistence: conversion mode, OSR, sampling frequency, alert enables, thresholds, hysteresis, and statistics live in device registers. The driver keeps only the I2C client, regulator, chip metadata, and mutex in memory. Runtime PM changes conversion mode to manual/auto without persisting user settings.

Dependencies and integration: I2C, regulator framework, optional IRQ, IIO events, PM runtime macros, and OF/I2C IDs for `ti,ads7128` and `ti,ads7138`.

Risks: `indio_dev->num_channels` is always eight even though chip data has a channel count field; threshold value packing uses 12-bit threshold fields within two registers; event handler returns `IRQ_NONE` when no event flag is set, important for shared IRQs. Test signals include available frequency/OSR lists, threshold read/write boundaries, event IRQ push/clear behavior, runtime suspend/resume mode writes, and scale from `avdd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7138.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7924.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7924.c

Purpose: I2C regmap IIO direct-mode driver for the TI ADS7924 12-bit four-channel ADC, with firmware channel validation, optional reset GPIO, vref regulator support, and continuous auto-scan operation.

Important APIs/types/functions: `struct ads7924_data` keeps device, regmap, vref regulator, reset GPIO, mutex, and `conv_invalid` stale-sample flag. `ads7924_get_adc_result()` reads two auto-incremented result bytes and handles first-conversion delay. `ads7924_read_raw()` exposes raw and scale. `ads7924_set_conv_mode()`, `ads7924_reset()`, and `ads7924_probe()` perform device setup.

Control flow: probe validates child-node `reg` properties, initializes I2C regmap with writeable-register filtering, enables `vref`, resets by GPIO or reset register, switches through AWAKE into AUTO_SCAN, registers a devm cleanup to return to IDLE, programs minimum acquisition time and zero power-up time, marks the first conversion invalid, and registers IIO. A raw read locks the device, optionally waits one conversion window to avoid stale data, reads the channel result pair, right-shifts the 12-bit sample, and returns it.

State and persistence: configuration is held in mode, acquisition, power, and reset registers; `conv_invalid` is an in-memory guard after mode changes; no persistent storage. Regulator and idle-mode cleanup are device-managed.

Dependencies and integration: I2C regmap, optional reset GPIO, vref regulator, firmware child nodes, and IIO direct mode. Matches `ti,ads7924`.

Risks: the channel validation only checks that at least one valid child node exists while the IIO device still exposes all four static channels; mode transitions require an AWAKE intermediate state; first raw read after auto-scan start deliberately sleeps. Test signals include invalid child-node rejection, reset path coverage, stale-conversion delay, scale from regulator voltage, and regmap access errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7924.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7950.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7950.c

Purpose: SPI IIO driver for the ADS7950/7951/7952/7953/7954/7955/7956/7957/7958/7959/7960/7961 family, supporting 4/8/12/16 channel variants, 8/10/12-bit scan formats, triggered buffers, direct reads, and a four-line GPIO provider.

Important APIs/types/functions: `struct ti_ads7950_state` stores SPI messages, scan/direct transfer buffers, mutex, gpio_chip, vref regulator/default, and ADC/GPIO command bitmasks. `ti_ads7950_update_scan_mode()` builds pipelined manual-mode commands for active channels. `ti_ads7950_trigger_handler()` pushes buffered scans. `ti_ads7950_scan_direct()` performs the three-transfer pipeline for a single channel. GPIO methods manipulate command/config bitmasks and synchronize SPI writes.

Control flow: probe sets 16-bit SPI words and `SPI_CS_WORD`, selects chip info from match data, builds reusable ring and direct messages, enables vref or ACPI default voltage, sets up a triggered buffer, initializes manual/GPIO command registers, registers IIO, then registers the gpiochip. Direct raw reads send a manual channel command through the pipeline, verify the returned channel tag, and extract shifted sample bits. Buffered scans issue the prepared ring message and skip the first two pipeline words.

State and persistence: `cmd_settings_bitmask` and `gpio_cmd_settings_bitmask` mirror chip settings for range, GPIO data, direction, and output values. SPI buffers are shared under `slock`; no persistent storage. Remove unregisters GPIO/IIO/buffer and disables regulator.

Dependencies and integration: SPI, regulator, optional ACPI, IIO triggered buffer, and gpiolib. OF and SPI IDs cover the whole ADS795x/ADS796x family.

Risks: SPI conversion is pipelined, so scan buffers include dummy latency words; direct reads reject mismatched channel tags; GPIO reads temporarily change ADC command settings and then restore them. Test signals include all variant channel counts/bit widths, GPIO input/output direction, vref scale including range-doubling, triggered buffer layout, and cleanup on partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads7950.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8344.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8344.c

Purpose: compact SPI IIO direct-mode driver for the TI ADS8344 16-bit ADC, exposing eight single-ended channels and eight differential channel combinations.

Important APIs/types/functions: `struct ads8344` holds SPI, vref regulator, mutex, and small DMA-safe tx/rx buffers. Channel macros create single-ended and differential `iio_chan_spec` entries with raw and shared scale attributes. `ads8344_adc_conversion()` sends the control byte, waits for conversion, reads three bytes, and assembles the 16-bit result. `ads8344_read_raw()` handles raw and scale. `ads8344_probe()` enables vref and registers IIO.

Control flow: probe allocates IIO, initializes the mutex, assigns static channels, gets and enables `vref`, installs a devm regulator-disable action, and registers the IIO device. Raw reads lock the ADC, build a command from START, single-ended/differential mode, channel address, and internal clock bits, write one byte, delay 9 microseconds, read three bytes, then combine the serial response.

State and persistence: no cached hardware configuration beyond regulator enable. Shared transfer buffers are protected by the mutex. No persistent storage, IRQs, or buffered path.

Dependencies and integration: SPI, vref regulator, IIO direct mode, OF compatible `ti,ads8344`.

Risks: no SPI setup constraints are enforced in this driver; conversion timing is a fixed delay; differential channel mapping relies on address encoding in the static table. Test signals include single-ended and differential raw reads, scale from regulator voltage, mutex serialization under concurrent sysfs reads, and probe cleanup when vref enable fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8344.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8688.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8688.c

Purpose: SPI IIO driver for TI ADS8684/ADS8688 ADCs, with direct reads, triggered buffers, per-channel input-range programming through IIO scale/offset, and optional vref regulator.

Important APIs/types/functions: `struct ads8688_state` stores mutex, chip info, SPI, vref in mV, per-channel range, and aligned command/data buffers. `ads8688_read()` issues a manual-channel command followed by NOOP to retrieve the result. `ads8688_prog_write()` programs range registers. `ads8688_read_raw()`, `ads8688_write_raw()`, `ads8688_write_raw_get_fmt()`, and `ads8688_trigger_handler()` implement IIO behavior.

Control flow: probe reads optional `vref`, defaults to 4096 mV, selects 4- or 8-channel chip info, forces SPI mode 1, resets the device, initializes the mutex, configures a triggered buffer, and registers IIO. Direct raw reads lock, perform a two-transfer SPI transaction, and return the lower 16 bits. Scale/offset reads use `range[]`; writes validate supported combinations, write the channel range program register, then update cached range. Triggered scans iterate active channels and push a timestamped buffer.

State and persistence: `range[8]` mirrors range registers but starts at zero, matching reset default. Device range settings persist only until reset/power loss. Transfer buffers are shared under `lock`; no disk persistence.

Dependencies and integration: SPI, regulator helper, IIO triggered buffer, IIO sysfs attributes for available scale/offset, OF/SPI IDs `ads8684` and `ads8688`.

Risks: triggered handler calls `ads8688_read()` without taking `st->lock`, so concurrent range writes/direct reads may contend on shared buffers unless IIO serialization prevents it; invalid offset/scale combinations are rejected based on current cached range. Test signals include range changes for each legal scale/offset pair, default-vref fallback, buffered scan ordering, and reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-ads8688.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-lmp92064.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-lmp92064.c

Purpose: SPI regmap IIO driver for TI LMP92064 current/voltage monitor, exposing current and voltage channels with direct reads and triggered buffered acquisition.

Important APIs/types/functions: `struct lmp92064_adc_priv` stores shunt resistance, SPI, and regmap. The regmap config defines readable/writable register ranges over 16-bit register addresses and 8-bit values. `lmp92064_read_meas()` performs the required descending bulk read from highest data register. `lmp92064_read_raw()`, `lmp92064_trigger_handler()`, `lmp92064_reset()`, and `lmp92064_adc_probe()` are the main paths.

Control flow: probe sets up SPI/regmap, reads required `shunt-resistor-micro-ohms`, enables `vdd` and `vdig`, obtains optional reset GPIO, resets by GPIO or soft config writes, polls STATUS until OK, assigns two channels plus timestamp, sets a scan mask requiring both channels, configures a triggered buffer, and registers IIO. Direct reads read both measurement words and select current or voltage. Buffered reads read both and push them with timestamp.

State and persistence: shunt resistance is immutable in driver memory after probe. Hardware config is restored during reset; samples are latched only when all data registers are read in required order. No persistent storage.

Dependencies and integration: SPI regmap, regulators `vdd` and `vdig`, optional reset GPIO, required firmware shunt property, IIO triggered buffer.

Risks: measurement validity depends on reading four data bytes in descending register order; zero or oversized shunt value rejects probe; reset timing is conservative because datasheet readiness timing is vague. Test signals include status-poll timeout, shunt scale math, required two-channel scan mask, GPIO vs soft reset path, and regmap range enforcement.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-lmp92064.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tlc4541.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tlc4541.c

Purpose: SPI IIO driver for TI TLC3541/TLC4541 single-channel ADCs, supporting 14-bit and 16-bit variants in direct and triggered-buffer modes.

Important APIs/types/functions: `struct tlc4541_state` stores SPI, vref regulator, a fixed three-transfer SPI message, and aligned receive buffer. `struct tlc4541_chip_info` selects the channel layout. `tlc4541_trigger_handler()` runs the prepared SPI message and pushes timestamped data. `tlc4541_read_raw()` handles direct raw reads and scale. `tlc4541_probe()` sets up variant data, reset write, SPI message, regulator, buffer, and IIO registration.

Control flow: probe chooses TLC3541 or TLC4541 by SPI id, writes a reset/init byte, prepares a transfer sequence matching the device requirement for 24 clocks, conversion delay, and data readback, enables vref, sets up a triggered buffer, and registers IIO. Direct reads claim IIO direct mode, run the same SPI message, decode the big-endian sample by variant shift/realbits, and release direct mode.

State and persistence: no cached device settings except the prepared SPI message and regulator state. Samples are transient in `rx_buf`. Remove unregisters IIO, cleans up the buffer, and disables vref.

Dependencies and integration: SPI, regulator, IIO triggered buffer, OF/SPI IDs `ti,tlc3541` and `ti,tlc4541`.

Risks: probe ignores errors from the initial reset `spi_write`; the delay in the middle transfer is expressed as 3 nanoseconds although comments describe a 2.94 microsecond conversion period, so timing should be checked against SPI core semantics and hardware behavior. Test signals include raw decode for both bit widths, direct/buffer mutual exclusion, scale from vref, and failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tlc4541.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tsc2046.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tsc2046.c

Purpose: SPI IIO ADC driver for TI TSC2046 touchscreen controller ADC mode, exposing eight 12-bit voltage channels with direct reads, triggered buffers, per-channel settling/oversampling, and a PENIRQ-driven rate-limited trigger state machine.

Important APIs/types/functions: `struct tsc2046_adc_priv` stores SPI, trigger/hrtimer state, scan buffers, group layout, per-channel configuration, timing, vref, and locks. `tsc2046_adc_read_one()` performs direct oversampled reads. `tsc2046_adc_update_scan_mode()` builds grouped transfer layout for active channels. `tsc2046_adc_timer()`, `tsc2046_adc_irq()`, `tsc2046_adc_reenable_trigger()`, and `tsc2046_adc_set_trigger_state()` implement the reusable IRQ trigger.

Control flow: probe validates max SPI frequency, forces SPI mode 0, reads optional external vref or uses internal 2500 mV, parses child-node settling/oversampling values, performs a dummy read to discover effective speed, allocates maximum scan buffers, requests a disabled IRQ, registers an own trigger and triggered buffer, then sets it as default. Direct reads allocate temporary transfer arrays, skip settling samples, average oversamples, and power down on the last sample. Buffered scans use prebuilt grouped commands and average each group before pushing.

State and persistence: scan layout and timing are rebuilt on scan-mask changes; trigger state tracks shutdown/standby/poll phases under spinlock. Per-channel settings come from firmware and are in memory only.

Dependencies and integration: SPI, regulator helper, IIO trigger/triggered buffer, hrtimer, IRQ, firmware child nodes. Compatible is `ti,tsc2046e-adc`.

Risks: IRQ line is affected by channel switching, requiring careful disable/reenable sequencing; oversized settling/oversampling can exceed one page; `scan_interval_us - time_per_scan_us` assumes scan time does not exceed interval despite warning. Test signals include direct reads with custom settling/oversampling, IRQ trigger enable/disable, timer transitions, buffer overflow sizing, and vref fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti-tsc2046.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti_am335x_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/ti_am335x_adc.c

Purpose: platform IIO driver for the ADC block inside TI AM335x/AM437x TSCADC MFD, supporting direct reads, kfifo buffered reads via FIFO1 IRQ, optional cyclic DMA, shared step-engine coordination with touchscreen, and suspend/resume.

Important APIs/types/functions: `struct tiadc_device` stores MFD pointer, FIFO lock, channel-to-step mapping, DT delay/averaging arrays, DMA state, and sample buffers. `tiadc_step_config()` programs sequencer steps. `tiadc_read_raw()` performs single-channel conversions. Buffer ops (`tiadc_buffer_preenable/postenable/predisable/postdisable`) manage FIFO, step engine, DMA, and IRQs. `tiadc_irq_h()`, `tiadc_worker_h()`, and `tiadc_dma_rx_complete()` feed buffers.

Control flow: probe obtains the MFD device, parses `ti,adc-channels` and optional per-channel averaging/open/sample delays, configures steps, sets FIFO threshold, builds dynamic IIO channels, registers a kfifo buffer and shared IRQ, registers IIO, then tries to acquire DMA channel `fifo1`. Direct reads reject operation while buffer is enabled, wait for idle, flush FIFO1, trigger exactly the mapped step, poll FIFO count until data arrives, scan all FIFO entries for the requested step id, and mark ADC done. Buffered enable flushes FIFO, configures continuous steps for active scan channels, enables DMA or FIFO threshold IRQs, and caches step bits in the MFD sequencer.

State and persistence: channel mapping, delays, averages, active buffered step mask, total enabled channels, and DMA period metadata are in memory. Hardware sequencer/FIFO/DMA registers hold runtime state; no persistent storage.

Dependencies and integration: platform device from `ti_am335x_tscadc` MFD, MMIO registers, shared IRQ, DMA engine, IIO kfifo, OF properties, and PM sleep callbacks.

Risks: ADC and touchscreen share hardware and IRQs, so step-engine cache coordination is critical; DMA is requested after IIO registration and failure unregisters IIO only for non-ENODEV; `total_ch_enabled` is incremented during postenable and must be reset during predisable. Test signals include direct read timeout/no matching step, FIFO overrun recovery, DMA and non-DMA buffer paths, DT truncation warnings, and suspend/resume restoring buffered steps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ti_am335x_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/twl4030-madc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/twl4030-madc.c

Purpose: platform IIO driver for the TWL4030 MADC in TWL PMICs, exposing 16 channels for battery, charger, USB, temperature, and general ADC readings, with raw, averaged raw, and processed conversions.

Important APIs/types/functions: `struct twl4030_madc_request` describes conversion method, channel bitmap, averaging, raw/processed mode, and result buffer. `struct twl4030_madc_data` holds device, mutex, bias regulator, method requests, IRQ selection, and ISR/IMR register addresses. `twl4030_madc_conversion()` is the serialized conversion engine. `twl4030_madc_read_channels()` reads and optionally converts values. `twl4030_madc_threaded_irq_handler()` services MADC interrupts, though IIO reads use wait/polling.

Control flow: probe powers MADC, enables battery-type current generator, sets battery measurement bits, ensures MADC high-frequency clock is enabled, selects first or second IRQ registers from platform data/firmware, requests threaded IRQ, configures USB analog routing for MADC[3:6], enables `vusb3v1`, and registers IIO. Reads build a wait-mode request for SW1 or SW2, select channel bitmap and averaging registers, start conversion, poll CTRL for not-busy and EOC, then read channel registers.

State and persistence: a global `twl4030_madc` pointer gates exported conversion use. Active request state is kept per conversion method under mutex. Hardware state includes MADC power, current generators, MADC clock, USB routing, and selected channels. No disk persistence.

Dependencies and integration: TWL MFD I2C helpers, platform data or firmware node, regulator `vusb3v1`, IRQ, IIO direct mode, charger/USB TWL modules.

Risks: global singleton limits multiple instances; error paths must unwind current generator and power; processed conversions contain channel-specific battery current/temperature math and divider ratios; IRQ code services active requests even on I2C error. Test signals include raw/average/processed reads, timeout at 5 ms, first vs second IRQ selection, USB routing/regulator enable, and conversion of channels 1 and 10.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/twl4030-madc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/twl6030-gpadc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/twl6030-gpadc.c

Purpose: platform IIO driver for TWL6030/TWL6032 GPADC blocks, supporting calibrated raw/processed reads, different channel/register models per chip, conversion-completion IRQs, input routing setup, and suspend/resume module toggling.

Important APIs/types/functions: `struct twl6030_gpadc_platform_data` provides channel tables, ideal calibration data, start-conversion and channel-register functions, and calibration routine. `struct twl6030_gpadc_data` stores mutex, completion, calibration table, and platform data. `twl6030_calibration()` and `twl6032_calibration()` decode trim registers. `twl6030_gpadc_read_raw()` starts conversion, waits for completion, and returns raw or processed values.

Control flow: probe selects TWL6030 or TWL6032 match data, allocates calibration table, initializes completion/mutex, reads trim registers to calculate per-channel gain/gain-error/offset-error, requests threaded IRQ, unmasks GPADC EOC interrupts, enables the GPADC module, wires VBUS/ID/VBAT/backup/VAC measurement inputs through TWL modules, and registers IIO. Reads serialize on `lock`, start conversion using chip-specific register writes, wait up to 5 seconds for IRQ completion, then read the result register and apply calibration/voltage conversion for processed channels.

State and persistence: calibration coefficients are computed at probe from PMIC trim registers and stored in memory. Hardware module enable/routing persists until suspend/remove or PMIC reset. Completion state is reused for conversions; no disk persistence.

Dependencies and integration: TWL MFD I2C helpers, platform IRQ, TWL interrupt mask helpers, IIO direct mode, OF match data, PM sleep ops.

Risks: calibration lookup assumes ideal table entries align with exposed channels; some channels intentionally lack calibration and return raw code; timeout is long and interrupt-dependent; remove disables IRQ and unregisters but module routing is mostly left to PMIC state. Test signals include trim decoding for both chip families, processed voltage math, raw uncalibrated channels, IRQ timeout, suspend/resume GPADC toggle, and USB/input routing writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/twl6030-gpadc.c -->
