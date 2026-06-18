# subset-b-003873 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11410.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max11410.c

Purpose: this is an SPI IIO driver for the Analog Devices MAX11410 24-bit ADC. It exposes firmware-described voltage channels, per-channel reference/input-mode configuration, raw reads, scale/offset, sampling frequency controls, notch filter sysfs controls, and triggered-buffer capture when an interrupt line is available.

Important APIs, types, and functions: `struct max11410_state` owns SPI, regmap, optional trigger, completion, lock, regulators, per-channel config, and DMA-aligned scan data. `struct max11410_channel_config` stores reference selection, signal path, gain, bipolar mode, VREF buffering, settling delay, and scale lists. Key functions are `max11410_parse_channels()`, `max11410_configure_channel()`, `max11410_sample()`, `max11410_read_raw()`, `max11410_write_raw()`, `max11410_read_avail()`, `max11410_trigger_handler()`, `max11410_buffer_postenable()`, `max11410_self_calibrate()`, and `max11410_probe()`.

Control flow: probe allocates the IIO device, initializes regmap, enables AVDD and optional VREF regulators, parses child nodes into IIO channels, configures an optional named GPIO interrupt, forces data format, sets up the triggered buffer, registers an IIO trigger when IRQ-backed, performs self and PGA calibration, then registers the device. Direct raw reads claim direct mode, lock state, configure mux/reference/PGA, start a single conversion, wait via IRQ completion or status polling, then read the 24-bit data register. Buffered capture configures the active one-hot channel and starts continuous conversion; interrupts either poll the trigger or complete direct reads.

State and persistence: runtime state is in `max11410_state` and per-channel config arrays. Hardware state persists in MAX11410 mux, control, PGA, filter, GPIO, calibration, and conversion registers; driver cleanup is devm-managed regulator actions. The mutex prevents sampling while channel config or sample rate changes are being applied.

Dependencies and integration points: the driver depends on SPI, regmap, regulators named `avdd`, `vref0p..2p`, `vref0n..2n`, firmware child nodes with `reg` or `diff-channels`, optional `adi,reference`, `adi,input-mode`, `bipolar`, `settling-time-us`, and VREF buffer properties. It integrates with IIO direct mode, IIO sysfs attributes, triggered buffers, IIO triggers, and optional firmware IRQ names `gpio0`/`gpio1`.

Risks and test signals: test probe with no channels, invalid channel indexes, missing reference regulators, both IRQ and polling paths, PGA scale writes, sample frequency availability after notch filter changes, and buffer enable/disable transitions. Risk areas are 24-bit big-endian reads into DMA-aligned storage, scale math depending on regulator voltage, interrupt-name requirements when `spi->irq` exists, and calibration failures blocking probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max11410.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1241.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max1241.c

Purpose: this SPI IIO driver supports the Maxim MAX1241 low-power 12-bit serial ADC. It exposes one voltage channel with raw and scale attributes, manages VDD/VREF supplies, and optionally toggles a shutdown GPIO around each conversion.

Important APIs, types, and functions: `struct max1241` stores SPI device, mutex, VREF regulator, optional shutdown GPIO, and DMA-aligned `__be16` sample storage. `max1241_read()` issues a zero-length SPI transfer with an 8 us delay to start conversion, followed by a 2-byte receive. `max1241_read_raw()` implements `IIO_CHAN_INFO_RAW` and `IIO_CHAN_INFO_SCALE`. `max1241_probe()` allocates/registers the IIO device and enables regulators.

Control flow: probe enables `vdd`, gets and enables `vref`, installs a cleanup action, acquires optional `shutdown` GPIO default-high, then registers a single direct-mode IIO voltage channel. Raw reads take the mutex, drive shutdown low if available, delay for wakeup, perform the SPI read, return shutdown high, decode bits `[14:3]` as a 12-bit value, and release the mutex. Scale is regulator voltage in mV over `2^12`.

State and persistence: the driver has no persistent software configuration beyond regulator and GPIO handles. Hardware state is transient: optional shutdown is asserted between reads, VREF is kept enabled for the lifetime of the device, and sample data is overwritten on each read.

Dependencies and integration points: it depends on the SPI subsystem, regulator framework (`vdd`, `vref`), optional GPIO descriptor `shutdown`, and IIO direct-mode sysfs. Device matching is via `maxim,max1241` OF compatible or `max1241` SPI ID.

Risks and test signals: verify bit alignment with known voltages, regulator-voltage error paths, operation with and without the shutdown GPIO, and SPI controller handling of zero-length delayed transfers. The main risk is timing sensitivity around conversion start and shutdown wakeup, because the driver assumes fixed 8 us conversion and 4 us wake delays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1241.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1363.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max1363.c

Purpose: this I2C IIO driver covers a large Maxim ADC family including MAX136x, MAX10xx, MAX11xx, MAX12xx, and MAX116xx variants. It supports direct raw/scale reads, triggered buffered scans, model-specific channel sets and scan modes, and threshold monitor events on MAX1361/MAX1363-style devices.

Important APIs, types, and functions: `struct max1363_chip_info` describes channels, modes, bit depth, internal VREF, and IIO callbacks. `struct max1363_state` caches setup/config bytes, current scan mode, monitor/event masks and thresholds, VREF voltage, bus send/recv operations, and scan buffer. Major functions include `max1363_match_mode()`, `max1363_set_scan_mode()`, `max1363_read_single_chan()`, `max1363_read_raw()`, `max1363_update_scan_mode()`, monitor/event handlers, `max1363_alloc_scan_masks()`, `max1363_initial_setup()`, and `max1363_probe()`.

Control flow: probe enables VCC, reads optional external VREF or uses chip internal VREF, selects I2C block transfers or SMBus byte helpers for 8-bit parts, allocates available scan masks from the mode table, sets initial setup/config bytes, installs triggered-buffer support, optionally requests an event IRQ, and registers the IIO device. Direct reads claim direct mode, lock, reject monitor mode, switch scan mode if needed, receive one or two sample bytes, and mask to chip resolution. Buffered scans select a scan mode matching the active mask and read all values in the trigger handler. Event enable updates cached masks, programs monitor thresholds, and the IRQ handler pushes threshold events.

State and persistence: the driver keeps setup/config bytes and event threshold masks in memory and mirrors them to device registers. `current_mode` is central state shared by direct reads and buffered capture. Monitor mode is mutually exclusive with direct and buffered flows. Regulator state is devm-managed.

Dependencies and integration points: integration is with I2C/SMBus, regulators `vcc` and optional `vref`, IIO direct mode, IIO buffers, kfifo triggered buffers, IIO events, OF and legacy I2C ID tables. The large static chip table maps compatibles to bit depth, channel arrays, scan modes, and internal reference values.

Risks and test signals: test every representative channel-count family, 8/10/12-bit devices, I2C and SMBus fallback, direct reads during active buffers, scan-mask rejection, event threshold programming, and IRQ event delivery. Risk areas are the broad static model table, mode/mask consistency, monitor-mode limitations, cached config synchronization, and partial bus transfers returning unexpected byte counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max1363.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max14001.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max14001.c

Purpose: this SPI IIO driver supports Analog Devices MAX14001/MAX14002 ADCs. It exposes one voltage channel with raw and scale attributes, handles the device's LSB-first 16-bit SPI framing, manages supplies and optional external reference, and clears the device memory-validation fault sequence.

Important APIs, types, and functions: `struct max14001_state` stores chip info, SPI, regmap, reference voltage, LSB-first capability, and cacheline-aligned TX/RX buffers. `max14001_read()` and `max14001_write()` implement custom framed register access. `max14001_write_single_reg()` performs the write-enable/write/write-disable sequence. `max14001_disable_mv_fault()` mirrors registers into verification registers. `max14001_read_raw()` provides ADC data and scale.

Control flow: probe allocates the IIO device, records whether the SPI controller supports `SPI_LSB_FIRST`, initializes a custom regmap, enables `vdd` and `vddl`, reads optional `refin` voltage or falls back to 1.25 V, sets the external-reference bit if needed, clears the memory-validation fault by writing verification registers, then registers the direct-mode IIO device. Raw reads regmap-read the ADC register; scale reports VREF mV over `2^10`.

State and persistence: software state is minimal after probe: VREF mV and SPI bit-order capability. Hardware state persists in configuration and verification registers, and all regmap writes go through the write-enable gate.

Dependencies and integration points: the driver depends on SPI, regmap with custom bus callbacks, regulators `vdd`, `vddl`, optional `refin`, and IIO direct mode. It integrates with debugfs register access through `debugfs_reg_access`, allowing register inspection and writes within regmap access tables.

Risks and test signals: verify both hardware `SPI_LSB_FIRST` and software `bitrev16()` paths, write-enable protection, external/internal reference scale, and memory-validation fault clearing. Risks include incorrect endian/bit reversal, incomplete verification-register writes, and regmap access tables accidentally blocking needed registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max14001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max34408.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max34408.c

Purpose: this I2C regmap IIO driver supports Maxim MAX34408 two-channel and MAX34409 four-channel 8-bit current monitors. It exposes current raw readings and scale based on per-channel sense resistor values.

Important APIs, types, and functions: `struct max34408_data` holds regmap, device, mutex, and `input_rsense` values. `struct max34408_adc_model_data` maps model name to channel arrays. `MAX34008_CHANNEL()` defines IIO current channels. `max34408_read_adc_avg()` temporarily writes the control register to the default averaging setting, reads a channel ADC register, and restores control. `max34408_read_raw()` returns raw and scale.

Control flow: probe obtains model data, initializes an 8-bit regmap, allocates the IIO device, reads child-node `maxim,rsense-val-micro-ohms` values into channel slots, disables alert and averaging by writing control register 0, selects the model channel table, and registers the device. Raw reads lock the device, save control, force default averaging, read the channel, restore control, and return the value. Scale computes max current from `10000 / rsense` with log2 denominator 8.

State and persistence: the only software configuration is the sense-resistor array and saved regmap pointer. Hardware control register state is temporarily modified for averaged reads and restored afterward.

Dependencies and integration points: it depends on I2C, regmap, firmware child nodes for sense resistors, and IIO direct mode. OF and I2C ID data select MAX34408 versus MAX34409 channel count.

Risks and test signals: test missing or zero sense-resistor properties, two- and four-channel variants, control-register restore after read failures, and scale reporting. The channel advertises `IIO_CHAN_INFO_OFFSET` but `read_raw()` does not implement offset, which is a user-visible ABI risk. The code also defines `MAX34408_DEFAULT_RSENSE` but does not apply it when firmware omits rsense values, so divide-by-zero behavior should be checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max34408.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max77541-adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max77541-adc.c

Purpose: this platform IIO child driver exposes ADC readings from the MAX77541 MFD PMIC. It provides VSYS, VOUT1, VOUT2 voltage channels and a temperature channel using the parent device regmap.

Important APIs, types, and functions: channel enums identify VSYS, VOUT1, VOUT2, and temperature. `max77541_adc_raw()` reads the channel's data register. `max77541_adc_scale()` derives voltage scale from fixed VSYS or the parent regulator range field `MAX77541_BITS_MX_CFG1_RNG`; temperature scale is fixed. `max77541_adc_offset()` supplies absolute-zero-derived temperature offset. `max77541_adc_probe()` obtains the parent regmap and registers the IIO device.

Control flow: the MFD core creates a `max77541-adc` platform device. Probe allocates a small private pointer to the parent regmap, configures direct-mode IIO metadata, assigns four static channels, and registers. Reads dispatch by mask: raw regmap reads channel data, scale computes per-channel units, and temp offset returns a fixed integer.

State and persistence: the ADC driver stores only a parent regmap pointer. Conversion data and range selection live in parent MAX77541 registers. There is no local locking, relying on regmap serialization and parent MFD ownership.

Dependencies and integration points: it depends on the MAX77541 MFD header/register definitions, platform bus, regmap, and IIO direct mode. Scale for VOUT channels is coupled to the M2 configuration register in the parent device.

Risks and test signals: test parent regmap availability, all range selections for VOUT scale, raw reads for each channel, and temperature offset/scale unit interpretation. Main risks are implicit parent configuration coupling and lack of explicit NULL check after `dev_get_regmap()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max77541-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max9611.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/max9611.c

Purpose: this I2C IIO driver supports MAX9611/MAX9612 high-side current-sense amplifiers with a 12-bit ADC. It exposes temperature, input/common-mode voltage, current-sense voltage, load current, and load power.

Important APIs, types, and functions: `struct max9611_dev` stores device, I2C client, mutex, and shunt resistance. `max9611_read_single()` programs the ADC mux, waits for conversion, and reads a big-endian word. `max9611_read_csa_voltage()` tries 1x, 4x, then 8x gain until a nonzero current-sense value appears. `max9611_read_raw()` implements raw, scale, offset, and processed readings. `max9611_init()` validates SMBus functionality and communication using die temperature.

Control flow: probe reads required `shunt-resistor-micro-ohms`, initializes the device, assigns static IIO channels, and registers. Raw temperature/input-voltage reads program the mux and decode shifted ADC values. Processed current-sense, current, and power paths dynamically select gain, subtract per-gain offsets, apply LSB tables, and divide by shunt resistance where needed.

State and persistence: software state is shunt resistance and a mutex. Hardware mux/control registers are changed for each read and reset during initialization. No buffered capture or persistent calibration is maintained.

Dependencies and integration points: it depends on I2C SMBus byte-write and word-read functionality, firmware match data for device name, the required shunt resistor property, and IIO sysfs attributes that expose shunt resistance for current and power calculations.

Risks and test signals: test invalid/missing shunt resistor, temperature sanity checks, all gain-selection paths, negative or zero current-sense values, and processed power overflow boundaries. Risks include returning `-EINVAL` instead of underlying bus errors in some read paths, gain autoselection ignoring saturation semantics, and arithmetic precision/overflow in power calculation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/max9611.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp320x.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mcp320x.c

Purpose: this SPI IIO driver supports many Microchip ADCs: MCP3001/2/4/8, MCP3201/2/4/8, MCP3301, and MCP3550/1/3 variants. It exposes raw voltage channels, differential channel variants, and scale from a VREF regulator.

Important APIs, types, and functions: `struct mcp320x_chip_info` defines channel table, resolution, and conversion time. `struct mcp320x` stores SPI messages/transfers, regulator, lock, chip info, and DMA-aligned TX/RX buffers. `mcp320x_channel_to_tx_data()` builds channel-select command bytes. `mcp320x_adc_conversion()` performs optional conversion-start timing, SPI transfer, and per-model bit extraction. `mcp320x_read_raw()` provides raw and scale.

Control flow: probe selects chip info from SPI ID, sets channel tables, builds SPI messages for single-channel RX-only or multi-channel TX/RX devices, applies special MCP355x conversion-start and wake/reset handling, enables `vref`, and registers direct-mode IIO. Reads lock, determine model, perform conversion for the selected channel and differential mode, decode raw bits or signed/overrange MCP355x data, then return scale as VREF mV over resolution bits.

State and persistence: persistent state is SPI message layout, chip info, VREF regulator, and mutex. MCP355x devices have conversion timing and possible shutdown/wakeup behavior; the probe performs two dummy conversions to stabilize them.

Dependencies and integration points: it depends on SPI, regulator `vref`, IIO direct mode, OF and SPI ID matching. Channel arrays encode single-ended and differential combinations used by sysfs.

Risks and test signals: test all supported resolutions, SPI CPOL modes for MCP355x 24/25-bit reads, differential channel selection bytes, regulator scale, overrange/underrange handling, and single-channel devices with no MOSI. Risks are model-specific bit alignment, ignored errors from dummy conversions, and conversion time constants for slow delta-sigma parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp320x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3422.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3422.c

Purpose: this I2C IIO driver supports Microchip MCP3421 through MCP3428 ADCs. It exposes one, two, or four voltage channels with raw values, scale, and shared sampling frequency controls.

Important APIs, types, and functions: `struct mcp3422` stores I2C client, device family ID, cached config byte, per-channel PGA settings, and a mutex. `mcp3422_update_config()` writes the config byte and updates the cache. `mcp3422_read()` receives 3 or 4 bytes depending on sample rate and sign-extends by resolution. `mcp3422_read_channel()` switches channel/PGA, waits one conversion interval, then reads. `mcp3422_write_raw()` changes per-channel scale or sample rate.

Control flow: probe checks raw I2C support, allocates state, selects channel table by ID, writes a default continuous-sampling config for channel 0, PGA x1, 240 SPS, and registers. Raw reads lock during channel switching and data read. Scale uses a static table indexed by sample rate and PGA. Sampling frequency writes map 240/60/15/3 SPS into config bits, with 3 SPS rejected for MCP3425-8 style IDs.

State and persistence: cached `config` mirrors device configuration, while `pga[]` stores desired gain per channel. Device configuration persists in continuous-sampling mode until changed. The mutex serializes reads and writes that alter channel, PGA, or sample-rate bits.

Dependencies and integration points: it depends on plain I2C transfers, IIO direct-mode attributes, and I2C/OF matching. Sysfs availability attributes expose valid sample rates and scales.

Risks and test signals: test channel switching delays at each sample rate, sign extension for 12/14/16/18-bit modes, per-channel PGA persistence, unsupported 3 SPS on relevant parts, and config-cache consistency after I2C errors. A minor ABI risk is `write_raw_get_fmt()` returning `IIO_VAL_INT_PLUS_MICRO` for sample frequency while writes actually accept integer Hz.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3422.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3564.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3564.c

Purpose: this SPI IIO driver supports the Microchip MCP346x/MCP356x and R variants. It exposes firmware-described differential/single-ended voltage channels, temperature and burnout-current controls, scale, calibration bias/scale, oversampling ratio, boost-current gain, and auto-zeroing sysfs controls.

Important APIs, types, and functions: `struct mcp3564_state` stores chip info, SPI, VREF, lock, hardware address, oversampling, hardware gain, scale tables, calibration state, boost/burnout/auto-zero modes, and labels. Low-level helpers build read/write/fast commands and transfer 8/16/24/32-bit register values. Key functions are `mcp3564_config()`, `mcp3564_parse_fw_children()`, `mcp3564_read_single_value()`, `mcp3564_read_raw()`, `mcp3564_write_raw()`, `mcp3564_read_avail()`, and `mcp3564_probe()`.

Control flow: probe allocates state and calls `mcp3564_config()`. Configuration reads the hardware address, identifies the chip from reserved registers or fallback compatible data, obtains external VREF or validates internal VREF availability, parses firmware child channels, performs unlock/reset/default-register programming, sets calibration defaults, scan/mux/IRQ/format/gain/oversampling/config bits, fills scale tables, selects IIO info based on internal-reference support, and registers. Raw voltage reads program the mux, send a fast start command, poll data-ready, and read ADCDATA. Writes update burnout current, calibration registers, oversampling, or hardware gain with mutex protection.

State and persistence: software caches most configurable device state to report attributes without rereading every register. Hardware state persists in CONFIG, MUX, calibration, SCAN, TIMER, IRQ, and LOCK-related registers. The device is direct-mode only; no buffer support appears in this file.

Dependencies and integration points: it depends on SPI, optional/external regulator `vref`, firmware child nodes with `reg` or `diff-channels` and optional labels, OF/SPI ID tables, and IIO ext_info/enums/sysfs attributes.

Risks and test signals: test chip ID fallback, internal-reference rejection on non-R parts, all channel-count variants, firmware channel bounds, data-ready timeout, scale/gain changes, burnout current writes, and calibration ranges. One code risk is the oversampling write path computes the closest new index but appears to program `adc->oversampling` rather than the new `tmp` value before updating the cache. Other risks are dynamic channel label lifetime, broad register initialization ordering, and returning `-EINVAL` instead of preserving read errors in raw conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3564.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3911.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3911.c

Purpose: this SPI IIO driver supports Microchip MCP3910/3911/3912/3913/3914/3918/3919 analog front-end ADCs. It exposes signed 24-bit voltage channels with raw, offset, scale, oversampling ratio, availability lists, and optional triggered-buffer capture via data-ready IRQ.

Important APIs, types, and functions: `struct mcp3911_chip_info` supplies channel tables and function pointers for register-layout differences. `struct mcp3911` stores SPI, lock, optional clock, device address, trigger, per-channel gains, chip info, scan buffer, and DMA-safe transfer buffers. Core helpers are `mcp3911_read()`, `mcp3911_write()`, `mcp3911_update()`, layout-specific config/offset/OSR/scale/raw functions, `mcp3911_read_raw()`, `mcp3911_write_raw()`, `mcp3911_trigger_handler()`, and `mcp3911_probe()`.

Control flow: probe reads optional external VREF and clock, parses `microchip,device-addr` or legacy `device-addr`, optionally toggles reset GPIO, runs chip-specific configuration, calculates scale table, initializes gains, sets IIO metadata, optionally creates a trigger and disabled IRQ for data-ready polling, sets up triggered buffer, and registers. Direct reads lock and dispatch through function pointers. Buffer reads issue a multi-byte read from channel 0 and copies active channel 24-bit samples into the scan buffer.

State and persistence: per-channel gains, device address, scale table, and config choices are cached in software. Device registers persist for clock source, VREF source, read mode, data-ready output mode, offset enable, gain, offset, and oversampling. IRQ state is controlled through trigger enable/disable.

Dependencies and integration points: the driver depends on SPI, regulators, optional clock, optional reset GPIO, OF/SPI match data, IIO direct mode, triggered buffers, and IIO triggers. It handles two register families through function tables rather than separate drivers.

Risks and test signals: test all chip variants, device addresses 0-3, external/internal VREF scale, external clock selection, reset timing, offset enable/write, scale and OSR availability, data-ready IRQ enable, and active-scan copying. Risks include global static scale table shared across devices with different VREFs, function-pointer/register-layout mismatches, and buffer RX length based on `num_channels - 1` including timestamp conventions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/mcp3911.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/men_z188_adc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/men_z188_adc.c

Purpose: this MCB bus IIO driver supports the MEN 16z188 ADC core. It exposes eight voltage channels with raw readings from memory-mapped registers.

Important APIs, types, and functions: `struct z188_adc` stores the requested memory resource and mapped base address. `z188_iio_read_raw()` reads a channel register, checks the oversampling error bit, and returns extracted data. `men_z188_config_channels()` enables automatic mode and configures all channels for voltage mode with gain bits cleared. `men_z188_probe()` maps resources, configures hardware, and registers IIO; `men_z188_remove()` unregisters and frees resources.

Control flow: probe allocates an IIO device, requests the `z188-adc` MCB memory resource, ioremaps it, configures channels, saves driver data, and registers. A raw read uses channel index times four as the register offset, checks `ADC_OVR`, extracts `ADC_DATA`, and returns `IIO_VAL_INT`. Remove reverses registration, iounmap, and MCB resource ownership.

State and persistence: the driver keeps only mapped resource state. Hardware configuration persists in the ADC control/config registers after probe until device removal or reset. There is no mutex, regulator, buffering, or runtime PM.

Dependencies and integration points: it depends on the MCB subsystem, MMIO accessors, IIO direct mode, and module namespace import `MCB`. Device matching uses MCB device ID `0xbc`.

Risks and test signals: test resource request/map failure paths, eight channel reads, oversampling error handling, and remove cleanup. A risk is the config loop using `addr + i` byte offsets while read channels use `chan * 4`; that should be checked against the hardware register map. Another risk is no serialization around MMIO reads/configuration, though the simple direct-read design may not require it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/men_z188_adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/meson_saradc.c -->
# sources/distributed-fs/ceph-client/drivers/iio/adc/meson_saradc.c

Purpose: this platform IIO driver supports Amlogic Meson SAR ADC blocks across Meson8 through S4 families. It exposes voltage channels, internal mux-derived voltage references, optional calibrated temperature sensor, raw and averaged reads, calibration bias/scale, labels, runtime hardware enable/disable, and suspend/resume.

Important APIs, types, and functions: `struct meson_sar_adc_param` holds SoC-specific register map, clock rate, resolution, temperature calibration parameters, BL30 integration, VREF and EOC quirks. `struct meson_sar_adc_priv` stores regmap, regulator, clocks, completion, lock, calibration, syscon, temperature calibration, and channel-7 mux state. Key functions include `meson_sar_adc_get_sample()`, `meson_sar_adc_enable_channel()`, sample-engine start/stop, BL30-aware lock/unlock, `meson_sar_adc_temp_sensor_init()`, `meson_sar_adc_init()`, `meson_sar_adc_hw_enable()`, `meson_sar_adc_calib()`, and probe/remove/PM callbacks.

Control flow: probe matches SoC data, maps MMIO through regmap, requests IRQ, obtains clocks/regulator, creates internal ADC clocks on older SoCs, reads optional temperature calibration from nvmem/syscon, selects channel table with or without temp, initializes registers, initializes mutex, enables hardware, calibrates against internal 25 percent and 75 percent VDD mux channels, then registers IIO. A read locks against BL30 firmware when needed, clears FIFO, sets averaging, maps the requested channel/mux/temp path, starts sample engine, waits for IRQ completion, validates FIFO count/channel, applies calibration, stops engine, and unlocks.

State and persistence: hardware state spans many ADC registers, channel muxes, averaging controls, clocks, VREF/bandgap, FIFO IRQ threshold, and optional temperature trim registers. Software persists calibration scale/bias, temperature coefficients, and mux selection. Suspend disables hardware and core clock; resume reenables them but does not rerun full calibration.

Dependencies and integration points: it depends on platform MMIO resources, regmap, IRQs, clocks, regulators, nvmem `temperature_calib`, optional HHI syscon, OF match data, and IIO direct mode. BL30 integration uses shared busy bits to coordinate ADC ownership with firmware.

Risks and test signals: test every SoC parameter set, internal clock creation path, BL30 lock timeout, IRQ/FIFO validation, temp-calibrated versus no-temp channel tables, calibration fallback, suspend/resume, and MPLL workaround registers. Risks include undocumented register bits, firmware coordination deadlocks, calibration depending on internal mux reads, and returning calibrated values clamped to resolution even if hardware data is stale or FIFO contains unexpected entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/meson_saradc.c -->
