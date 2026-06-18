# subset-b-003903 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9500.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9500.c

Purpose: standalone IIO driver for the Semtech SX9500 capacitive proximity sensor. It exposes four indexed `IIO_PROXIMITY` channels, raw reads, shared sampling frequency, threshold events, and optional triggered-buffer capture.

Important APIs/types/functions: `struct sx9500_data` holds the I2C client, regmap, optional reset GPIO, trigger, completion, per-channel proximity/event state, and refcounts for data-ready, close/far, and channel users. `sx9500_read_proximity()` enables a channel and conversion-done IRQ, waits via completion or scan-period sleep, reads `SX9500_REG_USE_*`, then unwinds refcounts. `sx9500_write_event_config()`, `sx9500_push_events()`, `sx9500_trigger_handler()`, buffer pre/post hooks, probe/remove, and suspend/resume form the rest of the public behavior.

Control flow: probe allocates an IIO device, initializes regmap and optional ACPI GPIO mappings, hard/soft resets, writes default proximity-control registers, performs compensation, optionally registers IRQ/trigger, then registers a triggered buffer and IIO device. IRQ top-half polls the trigger when enabled and always wakes the thread. The threaded handler reads `IRQ_SRC`, pushes far/close events on status changes, and completes direct reads on conversion done.

State and persistence: all register/user state is guarded by `mutex`. Channel, data-ready, and close/far usage are reference-counted so direct reads, events, and buffers can share hardware enables. Suspend stores `PROX_CTRL0` in `suspend_ctrl0`, disables all sensors, and resume restores it. Defaults are reprogrammed only at init, not persisted by the driver.

Dependencies/integration: integrates with I2C, regmap RBTREE cache, GPIO descriptors, ACPI/OF matching, IIO events, IIO triggers, and triggered buffers. It predates the newer `sx_common` helper and duplicates much of that logic locally.

Risks and test signals: refcount underflow would corrupt channel enables if disable paths are called out of order; event disable error unwind partly relies on successful inverse operations. Test raw reads with and without IRQ, event enable/disable transitions, buffer enable failure unwind, suspend/resume while events are active, reset GPIO polarity, sample-frequency writes, and IRQ clearing on event-only and conversion-only interrupts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.c

Purpose: shared implementation for newer Semtech SAR/proximity IIO drivers. It centralizes IRQ handling, raw proximity reads, event configuration, channel enable management, triggered-buffer setup, reset/default programming, regulator enablement, and IIO registration.

Important APIs/types/functions: exports `sx_common_events`, `sx_common_read_proximity()`, `sx_common_read_event_config()`, `sx_common_write_event_config()`, and `sx_common_probe()` in namespace `SEMTECH_PROX`. The chip-specific interface is `struct sx_common_chip_info` plus `ops` callbacks for `read_prox_data`, `check_whoami`, `init_compensation`, `wait_for_sample`, and `get_default_reg`.

Control flow: `sx_common_probe()` allocates private data, creates regmap, enables `vdd`/`svdd`, validates identity, initializes the chip, registers an optional IRQ-backed trigger, sets up the triggered buffer, and registers the IIO device. Direct raw reads temporarily enable the channel and conversion-done IRQ, wait by completion or polling callback, read a big-endian sample via chip ops, sign extend, and disable temporary state. IRQ thread clears `IRQ_SRC`, emits threshold events from `reg_stat`, and completes conversions.

State and persistence: `chan_read` and `chan_event` bitmaps are the canonical channel enable state; `sx_common_update_chan_en()` writes the hardware enable register only when the union changes. `chan_prox_stat` suppresses duplicate proximity events. `trigger_enabled` gates top-half trigger polling. Register defaults are applied during init and may come from firmware properties through `get_default_reg`.

Dependencies/integration: depends on I2C regmap, regulator bulk enable, IIO events/triggers/buffers, and chip-specific wrappers that provide register layout and channel tables. It uses runtime-managed device resources and exports GPL namespace symbols for sibling modules.

Risks and test signals: direct reads drop the mutex while waiting and rely on bitmaps to reconcile concurrent buffer/event use. Test concurrent raw read plus event enable, no-IRQ polling callbacks, default register property handling, trigger enable/disable with active raw readers, event direction encoding, and failure unwind when disabling IRQ/channel after a read error.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.h -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.h

Purpose: public internal header for Semtech SAR/proximity common support. It defines the register/default abstractions, chip description contract, driver private state, exported helper APIs, and shared event specifications used by chip-specific drivers.

Important APIs/types/functions: `SX_COMMON_REG_IRQ_SRC` and `SX_COMMON_MAX_NUM_CHANNELS` define common limits. `struct sx_common_reg_default` represents a register default with an optional firmware property. `struct sx_common_ops` is the chip callback table. `struct sx_common_chip_info` names key registers, bit offsets, channel counts, channel specs, and `iio_info`. `struct sx_common_data` stores mutex, completion, I2C client, trigger, regmap, proximity/event/read bitmaps, suspend state, and aligned scan buffer.

Control flow: the header establishes that chip drivers call `sx_common_probe()` from their I2C probe and route their `read_raw` and event callbacks to `sx_common_read_proximity()` and shared event helpers. Chip-specific callbacks fill gaps such as WHOAMI checks and sample wait behavior.

State and persistence: no state is persisted by the header itself, but the structs define persistent runtime state for enabled channels, event channels, last proximity status, and suspend control. The static assertion keeps channel bitmaps within an unsigned long.

Dependencies/integration: includes IIO types, regulators, Linux types, and forward declarations for I2C/regmap objects. The exported `sx_common_events[3]` gives rising, falling, and enable/value/hysteresis threshold ABI definitions.

Risks and test signals: ABI compatibility depends on chip drivers matching `num_channels`, channel indexes, and bitmap assumptions. Test by compiling all Semtech users, checking namespace imports, validating scan buffer alignment, and exercising chips with fewer than four channels to ensure masks and offsets are correct.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vcnl3020.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/vcnl3020.c

Purpose: I2C IIO driver for the Vishay VCNL3020 proximity sensor. It exposes one proximity channel with raw on-demand measurement, sampling-frequency read/write, threshold values, threshold enable, optional IRQ event delivery, and a firmware LED-current property.

Important APIs/types/functions: `struct vcnl3020_data` keeps regmap, device pointer, revision, mutex, and a big-endian transfer buffer. `vcnl3020_init()` verifies product ID and applies `vishay,led-current-microamp`. `vcnl3020_measure_proximity()` performs on-demand conversion. `vcnl3020_enable_periodic()` and `vcnl3020_disable_periodic()` switch threshold capture on/off. `vcnl3020_read_event()` and `write_event()` access low/high threshold registers.

Control flow: probe initializes regmap and IIO state, checks identity, optionally requests a threaded IRQ, then registers the device. Raw reads lock hardware, reject reads while self-timed periodic mode is active, start one-shot conversion, poll `PS_RDY`, bulk-read result bytes, and return integer proximity. Event enable writes periodic measurement and threshold interrupt configuration; disable clears command, interrupt control, and status.

State and persistence: hardware mode is the main state. Periodic threshold mode blocks direct conversions and sampling-frequency changes. Threshold values, rate, and LED current live in device registers; no software cache is maintained beyond the transfer buffer and revision byte.

Dependencies/integration: uses I2C regmap, firmware properties, IIO events, and optional threaded IRQ. Sampling frequencies are table-indexed values written directly to `VCNL_PROXIMITY_RATE`.

Risks and test signals: `vcnl3020_handle_irq_thread()` tests ISR bits against `VCNL_ICR_THRES_EN`, which has the same bit value as low-threshold status but semantically names the control bit; event direction is always pushed as rising for channel 1. Test threshold high/low IRQs, raw reads while periodic mode is active, frequency validation, LED-current conversion, no-IRQ operation, and clearing ISR after events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vcnl3020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l0x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l0x-i2c.c

Purpose: I2C IIO distance driver for ST VL53L0X FlightSense time-of-flight sensors. It supports direct single-shot range reads, scale reporting in meters from millimeters, optional IRQ completion, optional triggered-buffer continuous mode, regulator/reset control, and model-ID probing.

Important APIs/types/functions: `struct vl53l0x_data` stores client, completion, VDD regulator, reset GPIO, and trigger. `vl53l0x_read_proximity()` starts a single measurement and waits by IRQ completion or polling. `vl53l0x_trigger_handler()` reads the 12-byte result block and pushes range plus timestamp. Buffer postenable/postdisable switch continuous/single mode.

Control flow: probe validates SMBus capabilities, reads model ID, enables power and reset, registers cleanup action, configures IIO channel metadata, and if IRQ exists, allocates trigger, configures GPIO interrupt mode, and sets up a triggered buffer. Direct raw read writes `SYSRANGE_START`, waits up to 100 ms, clears IRQ if needed, reads result bytes, and returns the big-endian millimeter value.

State and persistence: power state is managed for device lifetime by devm action. The sensor mode changes between single and continuous when the buffer is toggled. Completion is only initialized when IRQ is present. The driver does not cache range values or configuration beyond trigger/power handles.

Dependencies/integration: depends on I2C SMBus byte/block transfers, regulators, optional reset GPIO, IRQ trigger type, IIO direct mode, IIO triggers, and triggered buffers.

Risks and test signals: direct raw reads do not call `iio_device_claim_direct()`, so test interaction with enabled buffer mode. Validate IRQ and polling paths, partial block-read handling, clear-IRQ failures, buffer disable wait for final sample, model-ID mismatch logging, regulator/reset sequencing, and systems with no IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l0x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l1x-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l1x-i2c.c

Purpose: I2C regmap IIO driver for ST VL53L1X time-of-flight distance sensors. It loads ST default configuration, calibrates and starts continuous autonomous ranging, exposes raw distance and scale, and optionally provides IRQ-triggered buffered samples.

Important APIs/types/functions: `struct vl53l1x_data` holds regmap, completion, optional XSHUT reset, current distance mode, GPIO polarity, and IRQ number. Helpers read/write big-endian 16/32-bit registers, clear/start/stop ranging, initialize firmware, set short/long distance mode, set timing budget, compute inter-measurement period from oscillator calibration, and read proximity.

Control flow: probe enables VDD, deasserts optional reset, waits for boot, runs `vl53l1x_chip_init()` including firmware-status poll, model ID read, config blob write, initial VHV calibration cycle, and VHV register changes. It then configures long mode, 50 ms timing budget and period, starts ranging for the device lifetime, registers a stop action, and optionally installs trigger/IRQ/buffer support. Direct reads wait for the next ready sample by IRQ or GPIO-status polling, validate range status, read distance, and clear IRQ.

State and persistence: continuous ranging is persistent runtime state after probe. `distance_mode` influences timing-budget programming. `gpio_polarity` determines ready detection. No user-visible mutable config is exposed. Ranging is stopped only by devm cleanup.

Dependencies/integration: uses 16-bit-address regmap with volatile/readable tables, regulators, reset controls, IIO triggers/buffers, IRQ, bitfield helpers, and the ST Ultra Lite Driver configuration values embedded as a static blob.

Risks and test signals: because hardware runs continuously, failed IRQ clears can affect later reads. Test boot timeout, model-ID mismatch tolerance, IRQ and polling ready paths, invalid range status returning `-EIO`, trigger buffer with invalid samples, cleanup stop action, reset-control absence fallback, and timing-budget/inter-measurement writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/vl53l1x-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/resolver/Kconfig

Purpose: Kconfig menu for resolver-to-digital converter drivers under IIO. It declares AD2S90, AD2S1200/AD2S1205, and AD2S1210 build options.

Important APIs/types/functions: this file has no C APIs, but it controls module availability. `AD2S90` depends on SPI. `AD2S1200` depends on SPI and GPIOLIB or COMPILE_TEST. `AD2S1210` depends on SPI, COMMON_CLK, GPIOLIB or COMPILE_TEST, and selects REGMAP, IIO_BUFFER, and IIO_TRIGGERED_BUFFER.

Control flow: build configuration enters `menu "Resolver to digital converters"` and exposes tristate choices. Help text describes sysfs/direct access and module names.

State and persistence: selected symbols persist in kernel configuration and drive Makefile object inclusion. There is no runtime state.

Dependencies/integration: integrates with kernel Kconfig dependency resolution and with the resolver Makefile. AD2S1210's selected buffer/regmap dependencies match its implementation requirements.

Risks and test signals: dependency drift can break compile coverage if driver code gains a new subsystem requirement. Test `allyesconfig`, `allmodconfig`, and COMPILE_TEST builds, especially AD2S1210 with and without GPIO support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/resolver/Makefile

Purpose: build glue mapping resolver Kconfig symbols to object files.

Important APIs/types/functions: `obj-$(CONFIG_AD2S90) += ad2s90.o`, `obj-$(CONFIG_AD2S1200) += ad2s1200.o`, and `obj-$(CONFIG_AD2S1210) += ad2s1210.o`.

Control flow: Kbuild includes exactly the objects whose symbols are enabled as built-in or module.

State and persistence: no runtime state; output is determined by `.config`.

Dependencies/integration: must stay in sync with Kconfig symbol names and source filenames in this directory.

Risks and test signals: stale object names or missing entries silently omit drivers from builds. Test each symbol as `m` and `y`, and verify module filenames match Kconfig help.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1200.c -->
# sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1200.c

Purpose: SPI IIO direct-mode driver for Analog Devices AD2S1200/AD2S1205 resolver-to-digital converters. It exposes angle and angular velocity raw channels plus scale.

Important APIs/types/functions: `struct ad2s1200_state` stores mutex, SPI device, SAMPLE GPIO, RDVEL GPIO, and DMA-aligned receive word. `ad2s1200_read_raw()` implements raw and scale handling. Probe claims GPIOs, sets SPI speed to 8.192 MHz and mode 3, and registers the IIO device.

Control flow: raw reads lock, pulse SAMPLE low/high, set RDVEL according to requested channel, read two SPI bytes, decode 12-bit angle or signed 12-bit velocity, delay for sample pulse timing, and unlock. Scale is computed as radians per code for angle and approximately `2*pi` for velocity.

State and persistence: no cached measurement state. GPIO line values and SPI settings are configured at probe and manipulated per read under lock.

Dependencies/integration: depends on SPI, GPIO descriptors named `adi,sample` and `adi,rdvel`, and IIO direct mode. Device tree and SPI IDs cover AD2S1200 and AD2S1205.

Risks and test signals: timing is approximated with `udelay(1)`, much longer than the nanosecond minimum but safe. Test SPI mode/speed setup, GPIO polarity, concurrent angle/velocity reads, sign extension for velocity, and absence/misnaming of required GPIOs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1210.c -->
# sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1210.c

Purpose: full IIO driver for the Analog Devices AD2S1210 resolver-to-digital converter. It exposes position, velocity, excitation frequency, hysteresis, threshold/fault event attributes, debugfs register access, and triggered-buffer capture.

Important APIs/types/functions: `struct ad2s1210_state` holds SPI, SAMPLE GPIO, optional mode GPIO array, regmap, input clock, resolution, fixed/config mode, previous fault flags, sample/scan buffers, and SPI transfer buffers. Custom regmap callbacks switch to config mode and perform two-byte SPI register access. Core paths include `ad2s1210_single_conversion()`, `ad2s1210_push_events()`, threshold get/set helpers, `ad2s1210_reinit_excitation_frequency()`, `ad2s1210_trigger_handler()`, and setup helpers for properties, clocks, GPIOs, and regmap.

Control flow: probe reads `adi,fixed-mode` and `assigned-resolution-bits`, validates the clock, configures sample/mode/resolution/reset GPIOs, initializes regmap, programs control defaults, sets excitation frequency with soft reset and fault clearing, sets up triggered buffer, and registers the IIO device. Direct reads toggle SAMPLE, read position/velocity either via config registers or mode-specific SPI transfer, decode raw values, and push one-shot fault events. The trigger handler latches a sample and fills active scan channels similarly.

State and persistence: `prev_fault_flags` suppresses duplicate events and is cleared when the fault register is read or soft reset occurs. Mode GPIOs or fixed config mode determine whether runtime mode switching is possible. Resolution affects hysteresis and threshold scaling. Register state is hardware-resident and accessed under `lock`; regmap locking is disabled because the driver owns serialization.

Dependencies/integration: depends on SPI, COMMON_CLK, GPIO descriptors, regmap, IIO events/sysfs/debugfs, and triggered buffers. Firmware properties are mandatory for resolution and either fixed mode or mode GPIOs.

Risks and test signals: LOT low threshold writes can underflow if hysteresis exceeds high threshold; voltage threshold stores truncate by 38 mV. Fault reads clear hardware state, so debugfs/sysfs access can affect event behavior. Test all fixed/config and GPIO mode paths, resolution variants, excitation-frequency boundaries, parity error handling, triggered buffer with one or both scan channels, fault one-shot semantics, and invalid firmware combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s1210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s90.c -->
# sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s90.c

Purpose: minimal SPI IIO driver for the Analog Devices AD2S90 resolver-to-digital converter. It exposes one angular position channel with raw and scale values.

Important APIs/types/functions: `struct ad2s90_state` contains a mutex, SPI device, and DMA-aligned two-byte receive buffer. `ad2s90_read_raw()` reads and decodes a 12-bit angle. `ad2s90_probe()` validates max SPI speed and registers the direct-mode IIO device.

Control flow: probe rejects SPI clocks above 830 kHz, allocates IIO private state, initializes mutex, and publishes the angle channel. Raw reads lock, read two bytes over SPI, combine the upper 12 bits into an integer, unlock, and return `IIO_VAL_INT`. Scale is `2*pi / 2^12` via `IIO_VAL_FRACTIONAL_LOG2`.

State and persistence: only the shared receive buffer is mutable software state. There is no hardware configuration beyond SPI bus parameters supplied by board data.

Dependencies/integration: depends on SPI, IIO direct mode, OF/SPI IDs, and device-managed IIO registration.

Risks and test signals: max-speed validation assumes the controller's configured `max_speed_hz` is meaningful. Test clock rejection, two-byte read errors, raw bit extraction, scale ABI, and basic probe through OF and SPI ID tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/resolver/ad2s90.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/Kconfig

Purpose: Kconfig menu for IIO temperature sensor drivers. It includes the requested IQS620AT, LTC2983, Maxim thermocouple, HID temperature, MAX30208, MAX31856, MAX31865, and MCP9600 options plus other temperature drivers in the folder.

Important APIs/types/functions: no runtime APIs. Symbols declare bus and subsystem dependencies such as MFD_IQS62X, SPI, I2C, HID_SENSOR_HUB, REGMAP_SPI/I2C, IIO_BUFFER, IIO_TRIGGERED_BUFFER, and HID sensor common/trigger helpers.

Control flow: each tristate option controls whether the corresponding object can be built in or as a module. Help text names supported chips and module names.

State and persistence: selected options persist in kernel configuration and drive Kbuild. There is no runtime state.

Dependencies/integration: integrates with the temperature Makefile and with subsystem dependency selection. `MAXIM_THERMOCOUPLE` and `HID_SENSOR_TEMP` select buffer support because their drivers use triggered buffers.

Risks and test signals: dependency mismatch can produce compile failures or missing modules. Test all requested symbols under `m`, `y`, and COMPILE_TEST where applicable; compare module names with Makefile object names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/Makefile

Purpose: Kbuild mapping from IIO temperature Kconfig symbols to object files.

Important APIs/types/functions: requested mappings include `iqs620at-temp.o`, `ltc2983.o`, `hid-sensor-temperature.o`, `maxim_thermocouple.o`, `max30208.o`, `max31856.o`, `max31865.o`, and `mcp9600.o`. The file also maps MLX/TMP/TSYS drivers.

Control flow: Kbuild conditionally compiles each object based on the associated `CONFIG_*` symbol.

State and persistence: no runtime state; output is determined by kernel config.

Dependencies/integration: must stay synchronized with Kconfig symbols and source filenames. It is the final connection between selected options and built modules.

Risks and test signals: typos in object names or duplicated symbols can hide build coverage issues. Test requested temperature configs as modules and built-ins, and verify that each module name matches help text.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/hid-sensor-temperature.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/hid-sensor-temperature.c

Purpose: HID Sensor Hub platform driver that exposes environmental temperature as an IIO temperature device with raw, scale, offset, sampling frequency, hysteresis, trigger, and buffered samples.

Important APIs/types/functions: `struct temperature_state` combines HID common attributes, temperature report metadata, scan buffer, scale fields, and offset. `temperature_read_raw()` handles synchronous raw reads and common HID attributes. `temperature_capture_sample()` stores incoming HID samples; `temperature_proc_event()` pushes buffered data when the trigger marks data ready. Probe parses HID common attributes and report metadata, sets up trigger and callback registration.

Control flow: platform probe allocates IIO state, parses the HID temperature usage, duplicates channel specs so scan bits match descriptor size, computes scale, installs HID trigger, registers callbacks for the temperature usage, and registers IIO. Direct raw reads power the sensor on, fetch a synchronized raw value from the sensor hub, then power it off. Buffered flow captures samples as reports arrive and pushes on send-event callback.

State and persistence: common HID attributes track power/reporting state, sampling frequency, hysteresis, and data-ready atomics. The last captured sample is stored in `scan`. Scale and offset are computed once from report descriptors.

Dependencies/integration: depends on HID sensor hub, HID sensor common IIO helpers, platform devices named `HID-SENSOR-200033`, IIO buffers, and HID trigger support. Imports namespace `IIO_HID`.

Risks and test signals: `raw_data` is cast to `s32 *`, so descriptor size/endianness assumptions should match HID core behavior. Test report sizes, negative logical minimum handling, trigger enable/disable, raw reads around runtime power, callback cleanup on probe failure/remove, and sampling-frequency/hysteresis writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/hid-sensor-temperature.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/iqs620at-temp.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/iqs620at-temp.c

Purpose: platform IIO temperature child driver for the Azoteq IQS620AT MFD. It exposes one direct-mode temperature channel with raw, scale, and hardware-version-dependent offset.

Important APIs/types/functions: `iqs620_temp_read_raw()` reads `IQS620_TEMP_UI_OUT` via the parent regmap, returns scale 1000, and chooses offset `-100` or `-40` depending on `hw_num`. Probe gets `struct iqs62x_core` from the parent and stores it as IIO driver data.

Control flow: probe allocates an IIO device with no private allocation, attaches parent core data, fills channel/info/name fields, and registers. Raw read performs a little-endian 16-bit register read on demand.

State and persistence: no local mutable state; all hardware access goes through the MFD core regmap. Offset depends on immutable hardware number.

Dependencies/integration: depends on MFD_IQS62X platform data, regmap, and IIO direct mode. Module alias is `platform:iqs620at-temp`.

Risks and test signals: parent lifetime and regmap serialization are delegated to the MFD core. Test V2/V3 offset selection, endian conversion, parent-driver probe ordering, raw read errors, and IIO scale/offset ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/iqs620at-temp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/ltc2983.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/ltc2983.c

Purpose: SPI regmap IIO driver for Analog Devices LTC2983/LTC2984/LTC2986/LTM2985 multi-sensor temperature measurement systems. It supports thermocouples, RTDs, thermistors, diodes, sense resistors, direct ADC inputs, and active temperature sensors, with firmware-described channel assignment and custom sensor tables.

Important APIs/types/functions: `struct ltc2983_data` stores chip info, regmap, SPI, mutex, completion, generated IIO channels, parsed sensors, mux/filter config, custom table size, and DMA-aligned transfer buffers. `struct ltc2983_sensor` has polymorphic `fault_handler` and `assign_chan` callbacks. Factory functions parse each sensor type. `ltc2983_chan_read()` starts a conversion and reads result/fault bits. `ltc2983_parse_fw()`, `ltc2983_setup()`, `ltc2983_eeprom_cmd()`, suspend/resume, and probe drive lifecycle.

Control flow: probe allocates IIO/regmap state, parses child firmware nodes into sensor objects, enables VDD, releases reset, allocates IIO channel specs excluding rsense helpers, waits for device startup, writes global filter/mux config, assigns custom tables and channel registers, requests the conversion IRQ, optionally writes EEPROM, and registers IIO. Raw reads lock, start conversion for the selected sensor channel, wait up to 300 ms for IRQ completion, read the result register, validate the valid bit, run type-specific fault handling, sign-extend result data, and return scale based on temperature or voltage.

State and persistence: firmware-parsed sensor topology is stored for the device lifetime. Custom table offsets and `custom_table_size` manage shared table memory; resume reassigns channels without rebuilding IIO channels. EEPROM-capable parts can read stored config on setup and write after probe. Suspend writes sleep command; resume dummy-reads status then reconfigures.

Dependencies/integration: depends on SPI regmap with 24-bit command framing, IRQ completion, regulators, optional reset GPIO, firmware child nodes/references, IIO direct mode, and PM sleep ops. Chip info controls channel count, EEPROM, and active temperature support.

Risks and test signals: firmware parsing has many boundary conditions: duplicate channels, invalid differential channel numbers, bad reference handles, custom table overflow, unsupported excitation currents, and signed fixed-point conversion. Test all sensor families, custom/Steinhart tables, EEPROM read/write fallback, suspend/resume reassign, IRQ timeout, hard and soft fault masks, rsense exclusion from IIO channels, direct ADC scale, and max-channel differences between 20-channel and 10-channel parts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/ltc2983.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max30208.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/max30208.c

Purpose: I2C IIO direct-mode driver for the Maxim MAX30208 digital temperature sensor. It exposes one temperature channel with raw and scale.

Important APIs/types/functions: `struct max30208_data` stores I2C client and mutex. `max30208_request()` starts a conversion and polls temperature-ready status. `max30208_update_temp()` drains FIFO data and returns the latest word. `max30208_config_setup()` enables FIFO rollover. `max30208_read()` exposes raw and scale.

Control flow: probe allocates IIO state, resets the sensor, waits 50 ms, configures FIFO rollover, and registers. Raw reads lock, start conversion, wait up to 500 ms in 50 ms steps, inspect overflow/data count, read FIFO entries until the newest sample remains in `ret`, sign extend it, and return integer raw data. Scale is reported as 5.

State and persistence: FIFO rollover and reset state are hardware-resident. The mutex serializes conversions and FIFO draining. No sample cache is held.

Dependencies/integration: depends on I2C SMBus byte and swapped-word operations, ACPI/OF/I2C IDs, and IIO direct mode.

Risks and test signals: if FIFO count is zero but no overflow is present, no FIFO read occurs and a count value can be returned as data; hardware behavior may make that rare after a ready conversion. Test conversion timeout, FIFO overflow handling, multiple FIFO samples, sign extension, reset failure, scale ABI, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max30208.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max31856.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/max31856.c

Purpose: SPI IIO direct-mode driver for the Maxim MAX31856 thermocouple converter. It exposes thermocouple and cold-junction temperature channels, scale, thermocouple type, oversampling ratio, fault sysfs attributes, and notch filter frequency control.

Important APIs/types/functions: `struct max31856_data` stores SPI, thermocouple type, 50 Hz filter flag, and averaging exponent. `max31856_init()` programs CR0/CR1 for type, averaging, open-circuit detection, autoconvert, and filter. `max31856_thermocouple_read()` reads thermocouple or cold-junction registers and checks fault status. `read_raw`, `write_raw`, and sysfs show/store helpers implement ABI.

Control flow: probe reads optional `thermocouple-type`, validates supported types, initializes hardware, and registers IIO. Raw reads fetch three bytes for thermocouple or cold junction, shift/sign-adjust fixed-point data, then reads status and returns `-EIO` on open/over-under-voltage faults. Writes to oversampling or type update cached state and reinitialize hardware. Filter sysfs toggles 50/60 Hz and reinitializes.

State and persistence: cached type, averaging, and filter settings mirror CR registers and are rewritten on changes. There is no mutex around SPI/register access, so concurrent sysfs writes and reads rely on IIO/core serialization only where present.

Dependencies/integration: depends on SPI, device property thermocouple bindings, IIO sysfs, and direct mode.

Risks and test signals: missing locking can interleave `max31856_init()` with reads. `write_raw()` ignores init errors. Test type validation and runtime type writes, averaging rounding to power-of-two, fault attributes, open-circuit/OVUV read failures, 50/60 Hz filter changes, negative cold-junction values, and concurrent accesses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max31856.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max31865.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/max31865.c

Purpose: SPI IIO direct-mode driver for the Maxim MAX31865 RTD-to-digital converter. It exposes one temperature channel with raw and scale plus sysfs attributes for OV/UV fault and 50/60 Hz notch filter.

Important APIs/types/functions: `struct max31865_data` stores SPI, mutex, filter flag, three-wire flag, and DMA-aligned buffer. Helpers read/write SPI registers, enable/disable bias, run one-shot RTD conversion, initialize config, and handle sysfs filter/fault attributes.

Control flow: probe reads `maxim,3-wire`, initializes config with wiring and filter, and registers IIO. Raw reads lock, enable bias, wait 11 ms, set one-shot and clear faults, wait conversion time based on filter, read RTD MSB/LSB, shift out fault bit, disable bias, and return raw count. Filter writes validate 50/60, update cached flag, reinitialize config under lock.

State and persistence: `filter_50hz` and `three_wire` are cached software settings mirrored into the config register. Bias is enabled only during conversions and disabled afterward. Mutex protects conversion and config updates.

Dependencies/integration: depends on SPI, firmware property `maxim,3-wire`, IIO sysfs, and direct mode.

Risks and test signals: early returns in `max31865_rtd_read()` after enabling bias may leave bias on if later reads/writes fail before `disable_bias()`. Test error injection after bias enable, filter conversion delays, 2/3/4-wire configuration, fault status sysfs, raw scaling, and concurrent filter writes during reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/max31865.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/maxim_thermocouple.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/maxim_thermocouple.c

Purpose: shared SPI IIO driver for Maxim MAX6675 and MAX31855 thermocouple sensors. It supports direct raw reads, scale, thermocouple type reporting, and triggered-buffer capture.

Important APIs/types/functions: chip metadata in `struct maxim_thermocouple_chip` selects channel table, scan mask, read size, and status bit. `struct maxim_thermocouple_data` stores SPI, chip info, thermocouple type char, and aligned read/buffer union. `maxim_thermocouple_read()` decodes raw values; `maxim_thermocouple_trigger_handler()` pushes raw scan data.

Control flow: probe maps SPI ID to MAX6675 or MAX31855 metadata, allocates IIO, sets channels and scan masks, installs triggered buffer, warns on generic MAX31855 ID, and registers. Direct raw reads claim direct mode, perform a 2- or 4-byte SPI read, reject status-bit fault, shift and sign-extend the requested channel, and return integer raw. Buffer handler reads a whole frame and pushes it with timestamp.

State and persistence: there is no mutable hardware configuration. The shared buffer is used by both direct and triggered paths, with direct reads protected by IIO direct-mode claim but no explicit mutex.

Dependencies/integration: depends on SPI, IIO direct mode, IIO triggered buffers, OF/SPI IDs for generic and type-specific MAX31855 variants.

Risks and test signals: triggered buffer does not check status fault bits before pushing samples; consumers must interpret scan data. Test MAX6675 and MAX31855 frame decoding, type chars for specific IDs, deprecated generic warning, scan masks, direct-read/buffer exclusion, SPI short/error paths, and fault-bit behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/maxim_thermocouple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mcp9600.c -->
# sources/distributed-fs/ceph-client/drivers/iio/temperature/mcp9600.c

Purpose: I2C IIO driver for Microchip MCP9600/MCP9601 thermocouple EMF converters. It exposes hot- and cold-junction temperature channels, thermocouple type, scale, optional threshold events on up to four named alert IRQs, and alert threshold/hysteresis configuration.

Important APIs/types/functions: `struct mcp9600_data` stores client and thermocouple type. Static maps convert DT thermocouple types to chip register values and IIO chars. `mcp9600_channels` is a 16-entry channel table selected by present alert IRQ bitmap. `mcp9600_read_raw()`, event config/value helpers, `mcp9600_probe_alerts()`, and per-alert IRQ handlers implement behavior.

Control flow: probe obtains match chip info, reads and checks device ID, parses `thermocouple-type` defaulting to K, writes sensor config, probes named firmware IRQs `alert1` through `alert4`, programs alert polarity/channel/direction, requests threaded IRQs, selects the prebuilt channel spec combination matching available alerts, and registers IIO. Raw reads use swapped-word SMBus and sign extend. Alert IRQs read status, confirm the corresponding alert bit, and push a threshold event.

State and persistence: thermocouple type is cached and written once. Alert config is held in hardware registers; event enable and thresholds are read/written live. There is no driver mutex, so concurrent sysfs event writes can interleave SMBus transactions.

Dependencies/integration: depends on I2C SMBus, firmware IRQ names, IRQ trigger type, thermocouple DT bindings, and IIO events.

Risks and test signals: channel event availability changes based on which alert IRQs exist, so ABI differs per firmware. Test all alert bitmap combinations, hot/cold rising/falling routing, active-high polarity from IRQ type, threshold clamping and fixed-point writes for negative values, device ID mismatch warnings, invalid thermocouple type, and concurrent event config operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/temperature/mcp9600.c -->
