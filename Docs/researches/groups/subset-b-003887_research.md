# Research: subset-b-003887

This grouped report covers the requested IIO health, humidity, core-private, and ADIS IMU files. Each section is bounded by the exact reconciliation markers for source-tree-aligned splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe4404.c -->
# sources/distributed-fs/ceph-client/drivers/iio/health/afe4404.c

Purpose: Implements the TI AFE4404 I2C IIO driver for heart-rate and low-cost pulse-oximeter analog front ends. It exposes six 24-bit intensity ADC value channels, three LED current output channels, offset controls, gain/capacitance sysfs attributes, optional triggered buffering, and sleep PM.

Important APIs/types/functions: `struct afe4404_data` owns the regmap, regmap fields, regulator, optional IIO trigger, IRQ, and scan buffer. `afe4404_channels` is built from `AFE440X_INTENSITY_CHAN` and `AFE440X_CURRENT_CHAN` macros in `afe440x.h`. `afe4404_read_raw()` reads ADC registers, LED current fields, offset DAC fields, and current scale. `afe4404_write_raw()` writes offset DAC and LED current fields. `afe440x_show_register()` / `afe440x_store_register()` implement custom resistance and capacitance attributes using value tables. `afe4404_trigger_handler()` reads active channels and pushes timestamped scans. `afe4404_probe()` wires regmap, field allocators, regulator enable, reset/default register programming, optional IRQ trigger, triggered buffer, and IIO registration.

Control flow: probe allocates an IIO device, initializes an 8-bit register/24-bit value regmap, allocates all declared `reg_field`s, enables `tx_sup`, software-resets the device, writes datasheet timing defaults, then registers the IIO device. If `client->irq` is present, it creates an IIO trigger and requests the ADC-ready IRQ through `iio_trigger_generic_data_rdy_poll`. Direct sysfs reads go through regmap reads or regmap-field reads. Buffered capture iterates the active scan mask and reads matching value registers into `afe->buffer`.

State and persistence: Persistent driver state is in `struct afe4404_data` and the regmap cache (`REGCACHE_MAPLE`). Volatile ADC/result registers are explicitly marked so cached reads do not stale data. Hardware state includes programmed timing registers, LED current, offset DAC, TIA gain/capacitance, oscillator enable, and power-down bit. Suspend sets `AFE440X_CONTROL2_PDN_AFE` and disables the regulator; resume reverses that. Regulator disable is also registered as a managed cleanup action.

Dependencies and integration points: Depends on I2C, regmap, regulator framework, IIO direct mode, IIO triggered buffers, optional OF compatible `ti,afe4404`, and the local `afe440x.h` macros/register constants. The ADC-ready IRQ is integrated as an IIO trigger source. Userspace interacts through standard IIO raw/offset/scale files plus custom resistance/capacitance availability and per-channel settings.

Risks: Channel enum values start at 1 and are used directly as scan indices and array indices; the sentinel layout must remain aligned with the arrays. `afe4404_write_raw()` does not range-check raw LED current or offset DAC values beyond hardware field truncation. Suspend/resume failure after regulator enable/disable can leave partial power state. The custom attribute parser only accepts exact table entries. Buffered reads assume all active scan bits map into `afe4404_channel_values`.

Test signals: Build with `CONFIG_AFE4404`; probe with `ti,afe4404`, valid `tx_sup`, and optional IRQ. Verify sysfs raw reads, offset writes, LED current writes/scale, table-backed resistance/capacitance attributes, suspend/resume regulator behavior, and triggered buffer scans with multiple active intensity channels. Fault injection should cover regmap read/write failures and missing regulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe4404.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe440x.h -->
# sources/distributed-fs/ceph-client/drivers/iio/health/afe440x.h

Purpose: Shared private header for TI AFE440x health drivers. It centralizes common register addresses, bit definitions, IIO channel construction macros, table-backed sysfs helpers, and the custom attribute container used by the AFE4404 driver.

Important APIs/types/functions: Defines common AFE440x timing/result/control registers and control bits such as `AFE440X_CONTROL0_SW_RESET`, `AFE440X_CONTROL1_TIMEREN`, `AFE440X_TIAGAIN_ENSEPGAIN`, and `AFE440X_CONTROL2_PDN_AFE`. `AFE440X_INTENSITY_CHAN()` creates signed 24-bit IIO intensity scan channels with raw plus optional info masks. `AFE440X_CURRENT_CHAN()` creates output current channels with raw and scale. `struct afe440x_val_table` represents integer plus micro-fraction values. `AFE440X_TABLE_ATTR()` emits read-only availability attributes. `struct afe440x_attr`, `to_afe440x_attr()`, and `AFE440X_ATTR()` define writable table-backed device attributes whose show/store callbacks are implemented in the C driver.

Control flow: This file has no runtime code except macro-expanded sysfs show functions. Driver code supplies tables and callbacks; the macros expand into static attributes and channel specs that the IIO core registers through attribute groups and channel arrays.

State and persistence: No independent state is stored here. The generated `afe440x_attr` instances persist as static objects in consuming drivers and carry a regmap-field id plus lookup table metadata.

Dependencies and integration points: Requires IIO channel definitions and Linux bit macros through including C files. It is tightly coupled to AFE440x register layout and to callbacks named `afe440x_show_register` and `afe440x_store_register` in the consuming translation unit.

Risks: Macro coupling is implicit: `AFE440X_ATTR()` assumes callback names and table lifetimes exist in the includer. The table attribute macro writes `buf[len - 1] = '\n'`, so empty tables would underflow, though current tables are non-empty. Channel macros assign `.address` and `.scan_index` from the same `_index`, so enum values used by consumers must be valid scan positions.

Test signals: Compile consumers with sparse/W=1 to catch macro misuse. Validate generated sysfs availability text, channel scan types, and that all enum indices used by consuming drivers align with channel arrays and lookup tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/afe440x.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/max30100.c -->
# sources/distributed-fs/ceph-client/drivers/iio/health/max30100.c

Purpose: I2C IIO driver for the Maxim MAX30100 heart-rate and pulse-oximeter sensor. It exposes buffered red/IR intensity channels from the hardware FIFO and a direct temperature channel.

Important APIs/types/functions: `struct max30100_data` stores I2C client, IIO device, lock, regmap, and two-channel big-endian scan buffer. `max30100_set_powermode()` toggles shutdown. `max30100_clear_fifo()` resets FIFO pointers. Buffer setup hooks power on and clear FIFO before enabling, and power down before disabling. `max30100_fifo_count()`, `max30100_read_measurement()`, and `max30100_interrupt_handler()` drain near-full FIFO data into IIO buffers. `max30100_led_init()` parses `maxim,led-current-microamp`. `max30100_chip_init()` configures pulse width, high-resolution 100 Hz SPO2 mode, HR+SPO2 mode, and FIFO interrupt. `max30100_read_raw()` handles temperature raw and scale.

Control flow: probe allocates an IIO device, configures kfifo buffering, creates a flat cached regmap with volatile status/FIFO/temp registers, powers the chip down, initializes LED current and SPO2 mode, requires an IRQ, requests a falling-edge threaded IRQ, then registers the IIO device. The IRQ handler locks, checks FIFO-ready status, reads one FIFO entry at a time with SMBus block reads, and pushes 4-byte red/IR samples.

State and persistence: Runtime state includes cached LED/config registers in regmap, the hardware FIFO, and the mutex-protected scan buffer. The chip is normally powered down until buffer enable. Direct temperature reads claim buffer mode and only run when the engine is available, then trigger conversion and sleep 35 ms.

Dependencies and integration points: Uses I2C/SMBus block transfers, regmap, IIO kfifo buffers, device properties for LED current and pulse width, and an external interrupt. OF compatible is `maxim,max30100`.

Risks: Probe fails without a valid IRQ; there is no polling fallback for optical channels. `max30100_fifo_count()` treats FIFO-ready as 15 entries but otherwise returns zero, so partial FIFO data is not drained unless the interrupt threshold fires. LED current property accepts only exact mapping values. `max30100_read_measurement()` returns raw SMBus error or byte-count mismatch, which can produce positive short-read returns in unusual adapters.

Test signals: Verify probe with and without `maxim,led-current-microamp` and `maxim,pulse-width-us`, invalid property rejection, IRQ-driven buffer capture with both scan channels enabled, temperature reads while buffer disabled/enabled, and power-down on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/max30100.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/max30102.c -->
# sources/distributed-fs/ceph-client/drivers/iio/health/max30102.c

Purpose: I2C IIO driver for MAX30102 pulse-oximeter/heart-rate sensors and MAX30105 optical particle sensors. It supports red/IR channels, optional green channel for MAX30105/MAX30101 match data, FIFO-buffered acquisition, temperature reads, and per-LED current properties.

Important APIs/types/functions: `struct max30102_data` stores chip id, regmap, I2C client, lock, raw FIFO buffer, and padded 18-bit processed buffer. `max30102_set_power()` and `max30102_set_powermode()` control shutdown and acquisition mode. Buffer hooks select HR+SPO2 or multi-LED mode from `active_scan_mask`. `max30102_read_measurement()` reads 3-byte samples per enabled LED and copies them into big-endian 32-bit scan slots. `max30102_led_init()` reads `maxim,red-led-current-microamp`, `maxim,ir-led-current-microamp`, and optional green property. `max30102_chip_init()` sets SPO2 ADC/rate/pulse and FIFO average/full interrupt. `max30102_read_raw()` exposes temperature raw/scale.

Control flow: probe selects channel table and scan masks from I2C id driver data, sets up kfifo buffering, initializes regmap, verifies part ID `0x15`, reads revision ID for debug, shuts down the chip, configures LEDs/SPO2/FIFO, requires an IRQ, installs a falling-edge threaded IRQ, and registers the IIO device. The IRQ handler computes the enabled LED count from the active scan mask, drains FIFO-ready samples, and pushes padded channel data.

State and persistence: Persistent runtime state is limited to chip id, regmap, mutex, and buffers. Hardware persists LED current, FIFO config, SPO2 config, slot assignment, and mode configuration. Temperature direct reads briefly power the device when the buffer is not running, then return it to shutdown.

Dependencies and integration points: Uses I2C SMBus block reads, regmap, IIO kfifo buffers, OF compatibles `maxim,max30101`, `maxim,max30102`, `maxim,max30105`, and I2C ids with chip-specific driver data. The interrupt line is mandatory for FIFO operation.

Risks: OF match entries do not carry data; the driver relies on `i2c_client_get_device_id()`, so modalias/id resolution must match for OF-created clients. Green channel is available only for chip ids mapped to `max30105`. FIFO count returns one sample when almost full, relying on the configured threshold. Current scaling simply divides microamps by 200 and allows any value up to register max rather than enforcing datasheet preferred values.

Test signals: Probe each id, verify part-ID rejection, validate active scan masks for two and three LED modes, buffer enable/disable mode programming, IRQ FIFO data layout, temperature read power behavior, and LED current property defaults/errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/health/max30102.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/Kconfig

Purpose: Kconfig menu for IIO humidity sensor drivers. It declares user-visible sensor options and hidden transport helpers for humidity devices under `drivers/iio/humidity`.

Important APIs/types/functions: User-visible configs include `AM2315`, `DHT11`, `ENS210`, `HDC100X`, `HDC2010`, `HDC3020`, `HID_SENSOR_HUMIDITY`, `HTS221`, `HTU21`, `SI7005`, and `SI7020`. Hidden helper configs `HTS221_I2C` and `HTS221_SPI` select regmap buses and depend on `HTS221`. Several entries select IIO buffer helpers, triggered buffers, CRC libraries, HID sensor common code, or measurement-specialties common I2C support.

Control flow: The menu has no runtime control flow. Its selections drive which objects the Makefile builds and ensure dependent common frameworks are available when a driver is enabled.

State and persistence: Kconfig choices persist in kernel `.config` and module build output. There is no runtime state.

Dependencies and integration points: Integrates humidity sensor support with I2C, GPIOLIB, HID sensor hub, SPI through HTS221 suboptions, CRC7/CRC8, and IIO buffer/trigger infrastructure. `HTS221` selects both transport helpers conditionally, depending on available I2C or SPI master support.

Risks: Incorrect `select` usage can force helper code without all runtime requirements. `DHT11` allows `COMPILE_TEST` without `GPIOLIB`, useful for build coverage but not runtime. HTS221 depends on `(I2C || SPI)` but selects `HTS221_SPI if (SPI_MASTER)`, so SPI-only configurations require SPI master symbols to align.

Test signals: Run `olddefconfig`/`allmodconfig`/`allyesconfig` build checks, verify module names match help text, and confirm selected helpers are built for each enabled driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/Makefile

Purpose: Build recipe for IIO humidity drivers. It maps Kconfig symbols to object files and composes the multi-object HTS221 core module.

Important APIs/types/functions: Direct `obj-$(CONFIG_...)` rules build one object per humidity driver. `hts221-y := hts221_core.o hts221_buffer.o` composes the main HTS221 module, while `hts221_i2c.o` and `hts221_spi.o` build transport modules. `ccflags-y` adds `drivers/iio/common/hid-sensors` include path for the HID humidity driver.

Control flow: Build-time only; Kbuild includes objects based on configuration.

State and persistence: The only persisted outcome is built-in or module object selection. No runtime state.

Dependencies and integration points: Integrates with Kbuild, Kconfig, HID sensor common headers, and the HTS221 exported namespace split between core and bus drivers.

Risks: Object names must stay synchronized with module names and Kconfig help. The HID include path is global to this subdirectory, so header name conflicts could affect future files.

Test signals: `make M=drivers/iio/humidity` with representative configs, especially HTS221 I2C/SPI module combinations and HID humidity builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/am2315.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/am2315.c

Purpose: I2C IIO driver for the Aosong AM2315 relative humidity and temperature sensor. It supports direct raw reads and triggered buffered scans with humidity, temperature, and timestamp.

Important APIs/types/functions: `struct am2315_data` stores the I2C client, mutex, and aligned scan storage. `struct am2315_sensor_data` carries one humidity and one temperature sample. `am2315_crc()` implements the datasheet CRC16. `am2315_ping()` wakes the device. `am2315_read_data()` sends the read command, waits 2-3 ms, receives eight bytes, verifies CRC, and decodes 16-bit raw values. `am2315_trigger_handler()` fills the scan buffer according to active channels. `am2315_read_raw()` exposes raw and scale.

Control flow: probe allocates an IIO device, initializes the mutex, sets two channels plus timestamp, installs a triggered buffer, and registers the device. Direct reads call `am2315_read_data()`. Triggered reads call the same acquisition path, then push selected channels with the poll timestamp.

State and persistence: Runtime state is only the mutex and scan buffer; measurements are not cached. Hardware is woken by a dummy SMBus byte read before each measurement and otherwise has no managed power state in this driver.

Dependencies and integration points: Uses I2C master send/recv, IIO triggered buffer helpers, and I2C id `"am2315"`. Userspace sees raw humidity/temp with scale `100`, meaning raw values are scaled externally by IIO conventions.

Risks: `am2315_read_data()` returns the receive byte count on success instead of zero, which callers accept because only negative is treated as failure. The mutex covers I2C transfer but not the CRC/decode phase. The driver assumes exactly eight bytes but only checks negative receive errors, not short positive reads. Temperature sign handling is not explicit despite AM2315 encoding sign in the high bit for negative values in some variants.

Test signals: Verify CRC rejection, short-read behavior, direct raw reads, triggered buffer with single and both channels, wake timing tolerance, and I2C transfer failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/am2315.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/dht11.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/dht11.c

Purpose: Platform/IIO driver for DHT11, DHT22, and compatible single-wire GPIO humidity/temperature sensors. It bit-decodes pulse widths captured by GPIO edge interrupts and exposes processed temperature and relative humidity.

Important APIs/types/functions: `struct dht11` stores GPIO, IRQ, completion, mutex, cached values, timestamp, edge count, and edge timing buffer. `dht11_handle_irq()` records edge timestamp/value pairs. `dht11_decode()` converts 40 data bits into humidity, temperature, and checksum, supporting DHT22 and DHT11 formats. `dht11_read_raw()` controls acquisition, caching, IRQ request/free, timeout, decode attempts, and returns processed values. `dht11_probe()` obtains the GPIO, maps IRQ, initializes IIO channels, and registers the device.

Control flow: A read uses cached data if it is younger than two seconds. Otherwise it checks clock resolution, pulls the GPIO low for 18-20 ms to start a transaction, switches to input, requests both-edge IRQs, waits up to one second for enough edges, frees the IRQ, optionally dumps dynamic debug edge timings, then tries decode offsets to account for extra/missing preamble edges.

State and persistence: Cached processed temperature/humidity and timestamp persist in `struct dht11`. `num_edges == -1` marks idle/no capture. The driver dynamically requests the IRQ only during reads and serializes sysfs reads with a mutex.

Dependencies and integration points: Uses GPIOD, platform device/OF compatible `dht11`, completions, kernel timekeeping, IIO direct mode, and dynamic debug for timing traces.

Risks: Correctness depends on system timer resolution; ambiguous 23-30 us resolution is warned and >34 us fails. Long cables or scheduling latency can distort pulse widths. IRQ allocation per read adds latency and failure opportunities. Processed units differ by sensor family: DHT22 uses centi-derived conversion, DHT11 milli units.

Test signals: Probe with interrupt-capable GPIO, verify first read and two-second cache behavior, exercise timeout with disconnected sensor, validate checksum rejection, inspect dynamic debug edge timings, and test under different timer resolutions or CPU load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/dht11.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/ens210.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/ens210.c

Purpose: I2C IIO driver for ScioSense ENS210 family temperature and humidity sensors, including ENS210/210A/211/212/213A/215 variants.

Important APIs/types/functions: `struct ens210_chip_info` captures name, part id, and conversion time. `struct ens210_data` stores client, chip info, and mutex. `ens210_crc7()` validates the 17-bit measurement payload. `ens210_get_measurement()` starts either temperature or humidity conversion, waits the variant conversion time, reads three data bytes, validates CRC and data-valid bit, and returns 16-bit raw. `ens210_read_raw()` provides raw, scale, and temperature offset. `ens210_probe()` checks adapter capabilities, enables `vdd`, resets the device, disables/re-enables low power around part-id read, and registers IIO.

Control flow: Direct reads are serialized by `data->lock`; each read starts a conversion with `ENS210_REG_SENS_START`, sleeps, optionally checks status, reads `T_VAL` or `H_VAL`, validates, and reports raw. Probe uses match data to choose variant parameters and logs but does not fail on part-id mismatch.

State and persistence: The only cached state is chip-info and mutex. Hardware is reset and returned to low-power mode after probe. Each sample is one-shot and not cached.

Dependencies and integration points: Requires SMBus byte data, byte, and I2C block transactions; selects CRC7 in Kconfig; uses regulator `vdd`; integrates through OF/I2C match data.

Risks: Part ID mismatch is informational, not fatal, so wrong compatibles can still bind. The status register is read after conversion wait but active bits are not checked. CRC function depends on endian handling of a masked value copied as bytes. No runtime PM is present despite low-power management.

Test signals: Validate all compatible/id match data, forced part-id mismatch log, CRC failure path, regulator failure path, raw temp/humidity reads, scale/offset values, and adapter capability rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/ens210.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc100x.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc100x.c

Purpose: I2C IIO driver for TI HDC1000/HDC1008/HDC1010/HDC1050/HDC1080 temperature and humidity sensors. It supports direct raw reads, integration-time configuration, heater control, and triggered dual-channel buffering.

Important APIs/types/functions: `struct hdc100x_data` stores client, lock, cached config, per-channel integration time, and aligned scan buffer. `hdc100x_update_config()` writes and caches configuration. `hdc100x_set_it_time()` maps requested integration time to resolution bits. `hdc100x_get_measurement()` starts one channel conversion and reads a big-endian word. `hdc100x_read_raw()` and `hdc100x_write_raw()` expose raw, scale, offset, integration time, and heater raw. Buffer hooks set/clear acquisition mode; `hdc100x_trigger_handler()` performs combined temp+humidity read and pushes timestamped data.

Control flow: probe checks I2C functionality, allocates IIO, initializes default integration times and config, sets channels and scan masks, installs triggered buffer callbacks, and registers the device. Direct reads claim direct mode, lock, start a measurement, wait integration time plus margin, and read the value. Buffered reads set acquisition mode and perform a dual read starting at the temperature register.

State and persistence: `data->config` mirrors `HDC100X_REG_CONFIG`; `adc_int_us[]` caches resolution-derived delays. Heater and acquisition mode persist in hardware until changed. No regulator or runtime PM state is managed.

Dependencies and integration points: Uses SMBus word/byte and raw I2C receive, IIO sysfs constants, triggered buffers, OF compatibles for the HDC100x family, and ACPI id `TXNW1010`.

Risks: Probe ignores return values from initial `hdc100x_set_it_time()` and config update, so hardware could start with unexpected defaults. Direct mode locking prevents conflict with buffers, but heater status reads do not require direct claim. Combined buffer read assumes both channels are active via scan mask. I2C short reads are not explicitly checked for exact byte count.

Test signals: Verify integration-time available/write/read, heater raw control, direct temp/humidity scaling/offset, buffer enable acquisition mode, triggered dual samples, ACPI/OF binding, and I2C failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc100x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc2010.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc2010.c

Purpose: I2C IIO driver for TI HDC2010/HDC2080 humidity and temperature sensors. It exposes raw and peak measurements plus heater control, using the device automatic measurement mode.

Important APIs/types/functions: `struct hdc2010_data` stores client, lock, cached measurement config, and DRDY/config register. `hdc2010_reg_translation` maps temperature and humidity channel addresses to primary and peak registers. `hdc2010_update_drdy_config()` writes and caches reset/DRDY/interrupt config bits. `hdc2010_get_prim_measurement_word()` and `hdc2010_get_peak_measurement_byte()` read samples. `hdc2010_read_raw()` handles raw, peak, scale, and temperature offset. `hdc2010_write_raw()` toggles heater. Probe enables automatic measurement mode and triggers measurements.

Control flow: probe checks I2C support, allocates IIO, configures channels, enables AMM at 5 Hz via `HDC2010_AMM`, writes measurement trigger/config, and registers the device. Remove unregisters and attempts to disable AMM. Direct reads claim direct mode, lock around I2C, then return primary 16-bit words or peak bytes scaled up to the same raw domain.

State and persistence: The driver caches `measurement_config` and `drdy_config`, including heater and AMM bits. Hardware automatic measurement mode persists while bound; remove disables AMM. There is no regulator or suspend/resume handling.

Dependencies and integration points: Uses SMBus word/byte data, IIO direct mode, OF compatibles `ti,hdc2010` and `ti,hdc2080`, and I2C ids.

Risks: `measurement_config` starts zero and only caches the driver-written value; pre-existing hardware config is not read. Probe uses unmanaged `iio_device_register()` and explicit remove, unlike many devm drivers. If measurement trigger write fails, AMM rollback is best-effort. Endianness relies on SMBus word behavior matching the device's little-endian register pair.

Test signals: Verify AMM enable/disable on probe/remove, raw and peak reads, heater raw writes and readback, scale/offset values, HDC2080 binding, and error handling for config writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc2010.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc3020.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc3020.c

Purpose: I2C IIO driver for TI HDC3020/HDC3021/HDC3022 humidity and temperature sensors. It supports raw, peak/trough, scale/offset, heater current, threshold event values/hysteresis, optional alert IRQ events, regulator/reset control, and system sleep PM.

Important APIs/types/functions: `struct hdc3020_data` stores client, optional reset GPIO, VDD regulator, and mutex. `hdc3020_write_bytes()` and `hdc3020_read_bytes()` implement command/data transfers with busy retries. `hdc3020_read_be16()` and `hdc3020_read_measurement()` validate CRC8-protected responses. `hdc3020_read_raw()`, `hdc3020_write_raw()`, and `hdc3020_read_available()` expose data and heater range. Threshold helpers convert between truncated packed threshold registers and micro-unit IIO event values. `hdc3020_read_thresh()` / `hdc3020_write_thresh()` implement event value and hysteresis. `hdc3020_interrupt_handler()` translates status alert bits into IIO events. `hdc3020_power_on()` / `power_off()` manage regulator, reset, status clear, and auto 10 Hz mode.

Control flow: probe verifies raw I2C transfer support, allocates IIO, initializes CRC table, gets VDD and optional reset GPIO, powers the chip, registers cleanup, optionally requests a threaded IRQ, and registers IIO. Raw reads lock and read the auto-measurement register. Event writes read current threshold and clear registers, modify the relevant temperature or humidity field while preserving the other, and write CRC-protected commands.

State and persistence: Driver state is minimal; most configuration lives in hardware. The sensor is kept in automatic 10 Hz mode while active. Heater setting, thresholds, and alert state persist in hardware until changed or power-cycled. Suspend powers off and resume powers on/restarts auto mode.

Dependencies and integration points: Uses I2C combined transfers, CRC8, regulator framework, optional reset GPIO, optional IRQ, IIO events, and OF/I2C ids for the HDC302x family.

Risks: `hdc3020_update_heater()` calls heater disable when `val == 0` but continues to program and enable the heater afterward, which may make a zero write ineffective. Busy retry loops use `mdelay()` and can block for up to about 100 ms per transfer. Threshold conversion truncates to hardware bit fields and uses scaled arithmetic with clamping, so round-trip exactness is limited. IRQ handler reads status without taking the main mutex.

Test signals: Verify CRC rejection, power-on/off sequencing with regulator/reset, raw/peak/trough reads, heater range and zero behavior, threshold value/hysteresis read/write for rising/falling temp/RH, IRQ event emission, suspend/resume, and no-IRQ operation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hdc3020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hid-sensor-humidity.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hid-sensor-humidity.c

Purpose: Platform driver that exposes HID sensor hub atmospheric humidity reports as an IIO humidity device with direct raw reads, buffered reports, sample frequency, hysteresis, scale, and offset.

Important APIs/types/functions: `struct hid_humidity_state` stores HID common attributes, humidity attribute metadata, scan buffer, scale components, precision, and value offset. `humidity_parse_report()` discovers report attributes and adapts channel realbits. `humidity_read_raw()` uses HID sensor hub helpers for raw value, scale, offset, sample frequency, and hysteresis. `humidity_write_raw()` updates sample frequency and hysteresis. `humidity_capture_sample()` stores incoming report data, and `humidity_proc_event()` pushes buffered samples when data-ready is set. `hid_humidity_probe()` allocates IIO, parses common attributes, sets up trigger, registers HID callbacks, and registers IIO.

Control flow: probe duplicates the static channel template so scan bits can be adjusted to report size, sets up the HID trigger, registers callbacks for humidity usage, then registers the IIO device. Direct raw reads temporarily power the HID sensor and perform a synchronous input attribute read. Asynchronous HID callbacks capture samples and push timestamped scans after complete report events.

State and persistence: State is per platform device and includes parsed HID report ids/scales and the latest buffered sample. HID common attributes own power, data-ready, sampling frequency, and hysteresis state through common HID sensor code.

Dependencies and integration points: Depends on HID sensor hub, `hid-sensor-trigger.h`, IIO buffers/triggers, platform id `HID-SENSOR-200032`, and namespace `IIO_HID`.

Risks: `humidity_capture_sample()` casts `raw_data` to `s32 *`; report sizes smaller than 32 bits rely on adjusted scan metadata and underlying alignment/packing behavior. Callback struct is static and has its `.pdev` field assigned during probe, so multiple devices may share mutable callback storage. Offset is stored but never explicitly initialized in this file.

Test signals: Test with HID humidity devices/report descriptors of different field sizes, direct raw reads with power state transitions, sample frequency/hysteresis writes, buffered trigger operation, multiple-device registration, and remove cleanup order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hid-sensor-humidity.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221.h -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221.h

Purpose: Private shared header for the ST HTS221 humidity/temperature driver family. It defines common state shared by core, buffer, I2C, and SPI modules and declares exported helpers.

Important APIs/types/functions: `enum hts221_sensor_type` indexes humidity and temperature sensors. `struct hts221_sensor` stores current averaging index plus calibration-derived slope and intercept. `struct hts221_hw` stores device name, `struct device`, regmap, optional trigger/IRQ, per-sensor calibration state, enabled flag, ODR, and aligned two-channel scan buffer. Declares `hts221_probe()`, `hts221_set_enable()`, `hts221_allocate_buffers()`, `hts221_allocate_trigger()`, and `hts221_pm_ops`.

Control flow: No executable control flow; it defines the ABI among HTS221 compilation units and the exported namespace used by transport modules.

State and persistence: Describes in-memory persistent state for HTS221 devices. Calibration slope/intercept and current averaging/ODR values are cached in `struct hts221_hw`.

Dependencies and integration points: Includes IIO definitions and forward-uses regmap/trigger/device types through included headers in C files. Shared by `hts221_core.c`, `hts221_buffer.c`, `hts221_i2c.c`, and `hts221_spi.c`.

Risks: Any change to `struct hts221_hw` affects all transport and buffer code. The exported helper names form the module namespace boundary, so symbol namespace updates must stay in sync with `MODULE_IMPORT_NS`.

Test signals: Compile HTS221 core with both I2C and SPI transports, including module namespace checks and PM ops references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_buffer.c

Purpose: Trigger and buffered capture support for the HTS221 driver. It configures the data-ready interrupt, allocates an IIO trigger, and reads humidity/temperature samples into the shared scan buffer.

Important APIs/types/functions: `hts221_trig_set_state()` toggles DRDY enable in CTRL3-like register `0x22`. `hts221_trigger_handler_thread()` checks status register and polls the IIO trigger when humidity data-ready is set. `hts221_allocate_trigger()` configures interrupt polarity/open-drain, requests threaded IRQ, allocates/registers trigger, and attaches it to the IIO device. Buffer hooks `hts221_buffer_preenable()` and `hts221_buffer_postdisable()` call `hts221_set_enable()`. `hts221_buffer_handler_thread()` bulk reads humidity and temperature registers and pushes timestamped data. `hts221_allocate_buffers()` installs the triggered buffer.

Control flow: During probe, core calls allocation only when IRQ is present. IRQ fires into a thread, status is read, and valid humidity-ready events call `iio_trigger_poll_nested()`. The triggered buffer poll function then reads both channel registers and notifies trigger completion.

State and persistence: Uses `hw->trig`, `hw->irq`, `hw->scan`, and `hw->enabled` via core helper. Hardware DRDY configuration persists in registers. Buffer enable powers/enables the sensor; postdisable disables it.

Dependencies and integration points: Depends on regmap, IIO trigger/triggered buffer, interrupt framework, optional platform data `st_sensors_platform_data`, device property `drive-open-drain`, and symbols from `hts221_core.c`.

Risks: `iio_dev->trig = iio_trigger_get(hw->trig)` is assigned even if trigger registration returns an error; error path relies on devm cleanup. IRQ type defaults to rising when unspecified/unsupported. The interrupt status check assumes humidity-ready implies both humidity and temperature samples are ready.

Test signals: Test IRQ polarity/open-drain properties, trigger registration, buffer enable/disable sensor power state, data-ready interrupt filtering, scan data order, and no-IRQ probe path in core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_buffer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_core.c

Purpose: Shared HTS221 humidity/temperature sensor core. It validates identity, powers the device, parses calibration data, exposes raw/scale/offset/ODR/oversampling sysfs, and delegates optional trigger/buffer setup.

Important APIs/types/functions: `hts221_odr_table` and `hts221_avg_list` define supported sample frequencies and oversampling ratios. `hts221_check_whoami()`, `hts221_update_odr()`, and `hts221_update_avg()` configure identity, ODR, and averaging. Calibration parsers compute per-sensor slope and intercept from factory registers. `hts221_get_sensor_scale()` and `hts221_get_sensor_offset()` translate calibration into IIO values. `hts221_read_oneshot()` enables the sensor, waits, reads a channel, and disables it. `hts221_read_raw()` / `write_raw()` expose IIO attributes under direct-mode claims. `hts221_probe()` initializes regulators, identity, BDU, ODR, calibration, averaging, optional buffers/triggers, and IIO registration.

Control flow: Bus-specific drivers pass a regmap to `hts221_probe()`. Core enables VDD, verifies `WHOAMI == 0xbc`, configures IIO channels, enables block data update, sets default 1 Hz ODR and mid-level averaging, parses humidity and temperature calibration, optionally installs buffering if IRQ exists, then registers the IIO device.

State and persistence: `struct hts221_hw` caches enabled state, ODR, current averaging indices, and calibration coefficients. PM suspend clears the enable bit; resume restores it only if the cached enabled flag was true. Direct one-shot reads toggle enable and update `hw->enabled`.

Dependencies and integration points: Uses regmap, regulator `vdd`, IIO direct mode, optional buffer/trigger helpers in `hts221_buffer.c`, exported namespace `IIO_HTS221`, and transport modules for I2C/SPI.

Risks: Calibration math divides by `(cal_x1 - cal_x0)` without explicit zero guard. `hts221_read_oneshot()` does not disable the sensor if the bulk read fails after enabling. Direct reads and writes rely on IIO direct-mode claim but do not use a separate mutex around regmap updates. ODR table labels 13 Hz while comment says 12.5 Hz, reflecting rounded IIO representation.

Test signals: Verify WHOAMI failure, regulator failure, calibration parsing with known fixtures, scale/offset outputs, ODR and oversampling available/write paths, one-shot read enable toggling including error injection, IRQ/no-IRQ probe, and suspend/resume restore.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_i2c.c

Purpose: I2C transport wrapper for the HTS221 core driver.

Important APIs/types/functions: `hts221_i2c_regmap_config` sets 8-bit registers/values and uses the HTS221 auto-increment bit as both read and write flag mask. `hts221_i2c_probe()` initializes an I2C regmap and calls the shared `hts221_probe()` with device, IRQ, client name, and regmap. Match tables include ACPI `SMO9100`, OF `st,hts221`, and I2C id `hts221`.

Control flow: I2C probe creates the regmap; on success all device initialization is delegated to core. Module registration is via `module_i2c_driver`.

State and persistence: No transport-private state beyond the devm regmap. Device runtime state is owned by core.

Dependencies and integration points: Depends on I2C, `REGMAP_I2C`, shared HTS221 symbols, PM ops from core, and namespace `IIO_HTS221`.

Risks: Auto-increment flag masks affect all regmap operations, so single register accesses must tolerate the flag. The transport does no functionality check itself.

Test signals: Probe over I2C with OF and ACPI ids, verify multi-byte calibration/data reads use auto-increment, and confirm PM callbacks resolve from the core module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_spi.c

Purpose: SPI transport wrapper for the HTS221 core driver.

Important APIs/types/functions: `hts221_spi_regmap_config` sets 8-bit registers/values, write auto-increment flag, and read flag combining SPI read plus auto-increment. `hts221_spi_probe()` initializes an SPI regmap and delegates to `hts221_probe()`. Match tables include OF `st,hts221` and SPI id `hts221`.

Control flow: SPI probe creates a regmap; all identity, calibration, IIO, and optional trigger setup is handled by core. Module registration is via `module_spi_driver`.

State and persistence: No SPI-private runtime state is stored; devm regmap and core-owned `struct hts221_hw` hold state.

Dependencies and integration points: Depends on SPI, `REGMAP_SPI`, shared HTS221 core symbols and PM ops, and namespace `IIO_HTS221`.

Risks: Correct SPI operation depends on read and auto-increment flags matching HTS221 protocol. The transport leaves mode/bits-per-word to SPI core/device setup and does not validate them.

Test signals: Probe over SPI with compatible/id match, verify multi-byte reads for calibration and buffer samples, and run suspend/resume with core PM callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/hts221_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/htu21.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/htu21.c

Purpose: I2C IIO driver for Measurement Specialties HTU21 humidity/temperature sensors and the humidity function of MS8607. It wraps common measurement-specialties helper routines.

Important APIs/types/functions: Uses `struct ms_ht_dev` from `ms_sensors_i2c.h` as private state. `htu21_read_raw()` returns processed temperature/humidity or current sample frequency. `htu21_write_raw()` maps requested sample frequency to a resolution index and calls `ms_sensors_write_resolution()`. Sysfs helpers expose sampling frequencies, battery-low status, and heater enable through common helper functions. `htu21_probe()` checks SMBus/I2C capabilities, allocates IIO, selects HTU21 two-channel or MS8607 humidity-only channel table, resets the chip, reads serial number, and registers IIO.

Control flow: Direct processed reads call common helpers for temperature/humidity. Sample frequency writes serialize through `dev_data->lock`, update `res_index`, and program resolution. Probe uses I2C id driver data to decide whether to suppress the temperature channel for MS8607.

State and persistence: Private state stores client, resolution index, and mutex. Hardware state includes resolution, heater, and reset defaults managed by common helpers. Serial number is read and logged but not persisted in driver state.

Dependencies and integration points: Depends on I2C, `IIO_MS_SENSORS_I2C`, common helper namespace `IIO_MEAS_SPEC_SENSORS`, OF/I2C ids `meas,htu21` and `meas,ms8607-humidity`.

Risks: OF match entries do not provide driver data, so OF-created MS8607 clients must still map to the correct I2C id data for humidity-only behavior. The sample frequency array is reverse-mapped by exact integer values only. Common helper behavior is a critical dependency not visible in this file.

Test signals: Probe HTU21 and MS8607 ids, verify channel set selection, processed temp/humidity reads, sample frequency writes/readback, heater and battery sysfs, reset/serial failure paths, and adapter capability rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/htu21.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/si7005.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/si7005.c

Purpose: I2C IIO driver for Silicon Labs Si7005 and compatible TH02 humidity/temperature sensors. It provides direct raw temperature and humidity plus scale/offset.

Important APIs/types/functions: `struct si7005_data` stores client, mutex, and cached config. `si7005_read_measurement()` writes the config start bit and optional temperature bit, polls status until ready, then reads a swapped 16-bit data word. `si7005_read_raw()` exposes raw, scale, and offset for humidity/temp. `si7005_probe()` checks SMBus word support, validates ID register against Si7005/Si7015 values, reads initial config, and registers IIO.

Control flow: Each raw read locks, starts conversion, sleeps/polls up to 50 times at 20 ms intervals, reads data, unlocks, and returns. Probe sets up a simple direct-mode IIO device with two channels.

State and persistence: Cached `data->config` preserves initial configuration bits and is reused when starting conversions. No runtime PM or regulator state. Measurements are not cached.

Dependencies and integration points: Uses I2C SMBus byte/word operations, IIO direct mode, OF compatible `silabs,si7005`, and I2C ids `si7005`/`th02`.

Risks: Poll timeout can block roughly one second per read. Only `I2C_FUNC_SMBUS_WORD_DATA` is checked, though byte-data operations are also used. TODOs note missing heater, fast mode, and processed compensation. Offset/scale are raw formula constants; no linearity compensation.

Test signals: Verify ID rejection, config cache use, temp/humidity raw conversion timing, timeout path, scale/offset outputs, TH02 binding, and adapter functionality mismatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/si7005.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/si7020.c -->
# sources/distributed-fs/ceph-client/drivers/iio/humidity/si7020.c

Purpose: I2C IIO driver for Silicon Labs Si7013/Si7020/Si7021 and TH06-compatible humidity/temperature sensors. It exposes raw temp/humidity, scale/offset, heater current setting, and a heater enable sysfs attribute.

Important APIs/types/functions: `struct si7020_data` stores client, mutex, cached user register, and heater register. `si7020_read_raw()` performs hold-master word reads for temp/RH, clamps humidity raw values, or returns heater current. `si7020_update_reg()` writes and caches masked register updates. `si7020_write_raw()` updates heater current range. `si7020_read_available()` reports heater range. `si7020_show_heater_en()` / `si7020_store_heater_en()` expose heater enable. Probe resets the device, initializes cached defaults, and registers IIO.

Control flow: Probe checks required SMBus ops, sends reset, waits 15 ms, allocates IIO, initializes channel tables and cached registers, and registers. Direct raw reads issue one SMBus word command per measurement. Heater current and enable writes are mutex-protected cached register updates.

State and persistence: Cached `user_reg` and `heater_reg` mirror driver-written values. The device is reset at probe, so defaults are assumed (`user_reg = 0x3A`, `heater_reg = 0`). There is no suspend/resume or regulator handling.

Dependencies and integration points: Uses I2C SMBus write byte/read word, IIO direct mode, OF compatible `silabs,si7020`, and ids `si7020`/`th06`.

Risks: The channel for heater current lacks `.output = true`, despite being writable through `write_raw`; userspace ABI may be less clear. Cached user/heater registers are not read back from hardware after reset. Sensor variants have extra capabilities not exposed. Hold-master reads can block the bus during conversion.

Test signals: Verify reset timing, temp/RH raw/scale/offset, humidity clamp boundaries, heater current available/write/read, heater enable sysfs, and error paths for SMBus failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/humidity/si7020.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/iio_core.h -->
# sources/distributed-fs/ceph-client/drivers/iio/iio_core.h

Purpose: Private header for Industrial I/O core internals. It declares core-only device types, buffer/file operation wrappers, ioctl handler registration, sysfs/channel helper functions, and event-interface helpers.

Important APIs/types/functions: `iio_device_type` identifies IIO devices. `struct iio_dev_buffer_pair` associates a device and buffer. `struct iio_ioctl_handler` is a list node plus ioctl callback, registered by `iio_device_ioctl_handler_register()` / `unregister()`. `__iio_add_chan_devattr()` and `iio_free_chan_devattr_list()` manage channel sysfs attributes. `iio_device_register_sysfs_group()` adds extra groups. `iio_format_value()` formats IIO values. Under `CONFIG_IIO_BUFFER`, wrapper declarations connect buffer poll/read/write operations and lifecycle helpers; otherwise inline stubs/null addresses are provided. Event helpers register/unregister/wake event sets and query enabled events.

Control flow: No implementation here; compile-time `CONFIG_IIO_BUFFER` selects real buffer hooks or inert stubs used by the core.

State and persistence: Defines structures that participate in core lists and file operations. It does not own state itself.

Dependencies and integration points: Internal to `drivers/iio`; individual drivers should not include it. Integrates IIO character device operations, sysfs creation, buffers, and events.

Risks: Because this is private core API, accidental driver inclusion can create brittle dependencies. Stub behavior under `!CONFIG_IIO_BUFFER` must preserve core build/runtime semantics. `IIO_IOCTL_UNHANDLED` is a positive sentinel distinct from negative errno and must be interpreted correctly by callers.

Test signals: Build IIO with and without buffer support, exercise ioctl handler registration order, channel sysfs creation/freeing, event set lifecycle, and buffer file operation wrappers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/iio_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/iio_core_trigger.h -->
# sources/distributed-fs/ceph-client/drivers/iio/iio_core_trigger.h

Purpose: Private IIO core header for trigger consumer registration and poll-function attach/detach helpers.

Important APIs/types/functions: When `CONFIG_IIO_TRIGGER` is enabled, declares `iio_device_register_trigger_consumer()`, `iio_device_unregister_trigger_consumer()`, `iio_trigger_attach_poll_func()`, and `iio_trigger_detach_poll_func()`. When disabled, provides stubs that return success or do nothing.

Control flow: Compile-time configuration chooses real trigger consumer infrastructure or no-op stubs. Implementations live elsewhere in the IIO core.

State and persistence: No direct state. Real implementations manage trigger consumer state and poll-function attachment relationships.

Dependencies and integration points: Internal to IIO core and trigger support. It bridges IIO devices, triggers, and `struct iio_poll_func`.

Risks: Stubs return success when trigger support is disabled, so higher-level code must ensure trigger-specific paths are not exposed in configurations where they cannot operate. The closing comment names `CONFIG_TRIGGER_CONSUMER`, while the guard uses `CONFIG_IIO_TRIGGER`, a minor documentation mismatch.

Test signals: Build with `CONFIG_IIO_TRIGGER=y/m/n`, exercise triggered-buffer setup, attach/detach ordering, and no-trigger builds for drivers selecting triggered buffers conditionally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/iio_core_trigger.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/Kconfig

Purpose: Kconfig menu for IIO inertial measurement unit drivers and the shared ADIS helper library.

Important APIs/types/functions: Declares ADIS IMU drivers (`ADIS16400`, `ADIS16460`, `ADIS16475`, `ADIS16480`, `ADIS16550`) with SPI dependencies and selections of `IIO_ADIS_LIB` and optionally `IIO_ADIS_LIB_BUFFER`. Includes subdirectory Kconfig files for BMI, BNO055, INV, SMI, and ST IMU families. Declares hidden/shared symbols `FXOS8700`, `IIO_ADIS_LIB`, and `IIO_ADIS_LIB_BUFFER`.

Control flow: Build-time only. Selections determine which modules and common libraries are compiled and whether triggered-buffer ADIS helpers are included.

State and persistence: Configuration persists in `.config` and module selection. No runtime state.

Dependencies and integration points: Integrates SPI, I2C, regmap transports, IIO buffers/triggers, CRC32 for some ADIS families, and nested Kconfig files.

Risks: ADIS drivers select buffer helpers only if `IIO_BUFFER`; direct-mode builds must still compile without buffer support. Alphabetical ordering is documented and should be preserved. Hidden library options must remain selected by all consumers of exported ADIS symbols.

Test signals: `allmodconfig`, `allyesconfig`, and targeted configs for ADIS with and without `IIO_BUFFER`; verify subdirectory Kconfig inclusion and module dependency resolution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/Makefile

Purpose: Kbuild rules for IIO IMU drivers and the common ADIS library.

Important APIs/types/functions: Maps ADIS and other IMU Kconfig symbols to objects. Builds `adis_lib.o` from `adis.o` plus optional `adis_trigger.o` and `adis_buffer.o` when `CONFIG_IIO_ADIS_LIB_BUFFER` is enabled. Recurses unconditionally into several IMU subdirectories with `obj-y +=`.

Control flow: Build-time object selection only.

State and persistence: No runtime state. Build products depend on Kconfig selections.

Dependencies and integration points: Integrates with ADIS namespace/library consumers, FXOS8700 core/transports, KMX61, SMI240, and nested IMU driver directories.

Risks: ADIS library object composition must match exported symbols used by selected drivers. Unconditional subdirectory traversal relies on child Makefiles to gate objects correctly.

Test signals: Build selected IMU modules, especially ADIS with buffer enabled/disabled, and verify module dependency metadata for `adis_lib`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/adis.c

Purpose: Shared SPI helper library for Analog Devices ADIS16xxx IIO devices. It implements paged register access, bit updates, debugfs access, IRQ control, status checking, reset/startup/self-test, single conversions, and `struct adis` initialization.

Important APIs/types/functions: `__adis_write_reg()` and `__adis_read_reg()` perform unlocked multi-byte SPI register transactions with optional page switching and configured delays. `__adis_update_bits_base()` read-modify-writes fields. `__adis_enable_irq()` toggles data-ready interrupt via device-specific callback, unmasked IRQ handling, or MSC control register. `__adis_check_status()` reads diagnostic status and logs per-bit messages. `__adis_reset()`, `adis_self_test()`, and `__adis_initial_startup()` establish known device state, including optional reset GPIO and product-id warning. `adis_single_conversion()` reads a channel and sign-extends/masks it. `adis_init()` validates config, initializes locks, SPI delay defaults, ops, current page, and IIO drvdata.

Control flow: Device drivers call `adis_init()` first, then startup and buffer setup helpers. Register read/write helpers select page if needed, build SPI message sequences, and update `current_page` after success. Startup prefers hardware reset GPIO if present; otherwise software reset, then self-test, optional IRQ disable, and optional product-id check.

State and persistence: `struct adis` stores SPI device, config, ops, current page, buffers, and `state_lock`. Hardware state includes selected page, diagnostic status, IRQ enable, reset/self-test side effects, and device registers.

Dependencies and integration points: Uses SPI core, GPIOD reset, IIO device drvdata, debugfs, and public ADIS headers. Exports symbols in `IIO_ADISLIB` / one reset symbol appears exported under `IIO_ADIS_LIB`.

Risks: Register helpers are explicitly unlocked; callers must use `state_lock` or `adis_dev_auto_scoped_lock`. Page cache correctness depends on all register access going through helpers. Namespace spelling inconsistency for `__adis_reset` export (`IIO_ADIS_LIB` vs `IIO_ADISLIB`) is notable. Product-id mismatch only warns. Self-test cleanup ignores errors when clearing non-autoclear self-test bits.

Test signals: Unit-style SPI mock tests for read/write sizes and paging, startup with/without reset GPIO, diagnostic bit logging, IRQ enable paths, single conversion sign extension, and build/module namespace checks for all ADIS consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16400.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/adis16400.c

Purpose: SPI IIO driver for a broad ADIS163xx/ADIS164xx IMU family including gyroscopes, accelerometers, magnetometers, temperature, voltage, pressure, inclinometer, auxiliary ADC, and buffered burst capture depending on variant.

Important APIs/types/functions: `struct adis16400_chip_info` captures variant channel table, ADIS library data, flags, scales, temperature calibration, and sample-frequency functions. `struct adis16400_state` stores variant, cached filter request, `struct adis`, and available scan mask. Debugfs helpers expose serial/product/flash count. Frequency helpers implement old ADIS16400 sample-period math and ADIS16334-style decimation. `adis16400_write_raw()` handles calib bias, low-pass filter, and sample frequency. `adis16400_read_raw()` handles raw conversion, scale, calib bias, temperature offset, low-pass frequency, and sample frequency. `adis16400_trigger_handler()` pushes burst buffer data, accounting for variants whose burst includes diagnostic status. `adis16400_probe()` initializes ADIS library, buffer/trigger, startup, power-off cleanup, IIO registration, and debugfs.

Control flow: Probe chooses variant from SPI id match data, assigns channels/info, optionally computes a single all-channel scan mask for burst-capable variants, initializes ADIS, sets up ADIS buffer/trigger, performs initial setup with SPI speed/mode adjustments and product-id validation, registers a managed stop action, then registers IIO. Direct raw reads use `adis_single_conversion()`. Sample frequency and filter writes lock ADIS state to avoid racing SPI register updates.

State and persistence: State includes variant, ADIS page/lock/buffers, filter integer, and available scan mask. Hardware persistent settings include sample period, filter averaging, calibration bias registers, IRQ enable, and sleep power-off on cleanup. Startup may change SPI max speed based on sample period and slow-mode flag.

Dependencies and integration points: Depends on SPI mode 3 devices, ADIS common library and buffer helpers, IIO triggered buffers, debugfs, and SPI id table mapping many product names to chip-info records.

Risks: Large variant matrix makes channel/register/scale mismatches easy. `sscanf(indio_dev->name, "adis%u\n", ...)` is used for product-id comparison and depends on naming format. Burst buffer handler copies a conservative length for diagnostic-status variants. Filter frequency cache `filt_int` is written but not used elsewhere. Probe is SPI-id centric; no OF table is present in this file.

Test signals: Probe each supported id at least by SPI mock, verify channel tables and scales, sample frequency read/write boundaries, low-pass filter math, calibration bias read/write, burst buffer layout for normal and diag-status variants, startup speed transitions, debugfs files, and cleanup power-off.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16400.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16460.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/adis16460.c

Purpose: SPI IIO driver for the Analog Devices ADIS16460 IMU. It exposes 32-bit gyroscope and accelerometer axes, 16-bit temperature, sample-frequency control, ADIS buffered/trigger support, and debugfs identifiers.

Important APIs/types/functions: `struct adis16460_chip_info` stores channel table and scale constants. `struct adis16460` stores chip info and shared `struct adis`. Debugfs helpers read serial, product id, and flash count. `adis16460_set_freq()` / `get_freq()` program/read decimation rate from a 2.048 MHz base. `adis16460_read_raw()` exposes raw conversions through ADIS helper, scale, temperature offset, and sample frequency. `adis16460_write_raw()` allows sample frequency writes. Channel macros create modified X/Y/Z gyro/accel channels and temperature. `adis16460_probe()` initializes ADIS, sets up buffer/trigger, runs startup, registers IIO, and installs debugfs.

Control flow: probe allocates IIO, assigns static chip info and channels, calls `adis_init()` with `adis16460_data`, sets up ADIS buffer/trigger with the common handler, runs `__adis_initial_startup()`, registers IIO, then creates debugfs entries. Direct reads go through ADIS single conversion or direct register reads for frequency.

State and persistence: Driver state is chip info plus ADIS state. Hardware state includes decimation rate, diagnostic status, data-ready IRQ behavior (`unmasked_drdy = true`), and startup/reset/self-test effects. No explicit remove action powers down the device.

Dependencies and integration points: Uses SPI, ADIS common library/buffer helpers, IIO, debugfs, OF compatible `adi,adis16460`, SPI id `adis16460`, and namespace `IIO_ADISLIB`.

Risks: Sample frequency write has no explicit lower bound beyond positive input; very low requested rates clamp divider to 2048. No direct locking around set/get frequency in this file, relying on ADIS helper functions' locking behavior or caller serialization. The OF match lacks `.data`, but this driver has only one variant. Debugfs reads access hardware live and can fail with SPI errors.

Test signals: Probe via SPI id and OF, verify startup product-id check, raw gyro/accel/temp reads, fractional scales, sample-frequency set/get edge values, buffer capture through ADIS common helpers, diagnostic status handling, and debugfs reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/adis16460.c -->
