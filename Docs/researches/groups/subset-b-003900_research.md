# subset-b-003900 research

Grouped research for Linux IIO potentiostat and pressure sensor drivers. Each section is wrapped for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/lmp91000.c -->
# sources/distributed-fs/ceph-client/drivers/iio/potentiostat/lmp91000.c

Purpose: I2C Industrial I/O driver for TI LMP91000/LMP91002 digital potentiostats. It exposes one voltage channel for the electrochemical cell path and one processed temperature channel, using an external ADC supplied through IIO channel callbacks.

Important APIs, types, and functions: `struct lmp91000_data` stores the regmap, trigger, callback buffer, ADC channel, completion, selected channel, and scan buffer. `lmp91000_read_config()` parses `ti,tia-gain-ohm`, `ti,external-tia-resistor`, and `ti,rload-ohm`, unlocks configuration registers, programs TIA/load/reference registers, and relocks them. `lmp91000_read()` switches `MODECN`, polls the nested trigger, waits for `lmp91000_buffer_cb()`, and returns the captured ADC value. `lmp91000_read_raw()` maps IIO raw, processed temperature, scale, and offset requests. Probe builds the regmap, trigger, triggered buffer, IIO callback buffer, and IIO device.

Control flow: direct reads start the external ADC callback buffer, select the LMP91000 mode, optionally wait after switching to temperature mode, poll the nested trigger, and wait up to one second for the callback to complete. Buffered reads use `lmp91000_buffer_handler()` to force the 3-lead chemical measurement and push timestamped data. Temperature processing converts external ADC raw data to processed voltage, then uses `lmp91000_temp_lut` from `LMP91000_TEMP_BASE`.

State and persistence: runtime state is in memory only. Device configuration is held in hardware registers after probe. There is no persistent storage. Synchronization depends on one `completion` and the callback-selected buffer index; there is no explicit mutex around direct reads.

Dependencies and integration points: depends on I2C, regmap, IIO core, IIO triggered buffers, IIO consumer/callback channels, and firmware properties. It binds `ti,lmp91000` and `ti,lmp91002`. It sets an immutable trigger on the upstream ADC IIO device.

Risks: probe calls `iio_trigger_set_immutable(iio_channel_cb_get_iio_dev(data->cb_buffer), data->trig)` before `data->cb_buffer` is acquired, so this source as read has a high-risk initialization-order bug. `regmap_write()` results in `lmp91000_read_config()` are ignored after validation. Concurrent direct reads and buffered use can race through shared `chan_select`, `buffer`, and `completion`. Temperature LUT lookup is approximate and clamps only by array exhaustion. Error returns from `regmap_read/write` are collapsed to `-EINVAL`, losing bus error detail.

Test signals: exercise probe deferral when the ADC callback channel is unavailable, firmware property validation for supported and unsupported gain/load values, direct raw voltage and processed temperature reads, timeout when no callback completion occurs, triggered buffer capture, and remove path cleanup of callback buffers and triggers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/potentiostat/lmp91000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig

Purpose: Kconfig menu for IIO pressure sensor drivers. It declares selectable symbols, bus dependencies, hidden common core symbols, and helper selections for pressure, barometer, altimeter, humidity-capable, and HID pressure devices.

Important APIs, types, and functions: this is build metadata rather than C code. Key symbols for this subset are `ABP060MG`, `ABP2030PA`, `ABP2030PA_I2C`, `ABP2030PA_SPI`, `BMP280`, `BMP280_I2C`, `BMP280_SPI`, `IIO_CROS_EC_BARO`, `DLHL60D`, `DPS310`, `HID_SENSOR_PRESS`, `HP03`, `HP206C`, `HSC030PA`, `HSC030PA_I2C`, `HSC030PA_SPI`, and `ADP810`.

Control flow: user-visible bus symbols select hidden common cores where needed. `BMP280` selects bus helper modules conditionally on `I2C` and `SPI_MASTER`; ABP2 and MPR use hidden common cores selected by bus-specific drivers; HSC selects hidden I2C/SPI helpers based on available buses.

State and persistence: Kconfig choices persist in the kernel `.config` and determine which objects become built-in or modules. No runtime state is defined here.

Dependencies and integration points: integrates with the kernel build system, IIO buffer/trigger selections, regmap bus helpers, CRC support, HID sensor hub, ChromeOS EC sensor core, and bus subsystems. It also communicates module names through help text.

Risks: hidden core symbols must stay aligned with Makefile object names and exported namespaces. Conditional `select` can build bus modules unintentionally when a common symbol is enabled with both buses available. Help text and module names can drift from source files. Alphabetical-order comments are partly strained by late additions such as `ADP810`.

Test signals: use `make olddefconfig` and `make menuconfig` visibility checks, verify module dependency closure for I2C-only, SPI-only, and both-bus configs, run `scripts/kconfig/conf` warnings, and confirm selected symbols produce the objects listed in the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile

Purpose: kernel build mapping from pressure-driver Kconfig symbols to object files. It also composes multi-object core modules such as `bmp280.o` and `st_pressure.o`.

Important APIs, types, and functions: uses kbuild `obj-$(CONFIG_...) += ...` assignments and aggregate object variables. In this subset, `bmp280-objs := bmp280-core.o bmp280-regmap.o` links the core and regmap policy into one module, while `bmp280-i2c.o` and `bmp280-spi.o` are separate bus front ends. ABP2 and HSC have separate common and bus-specific objects.

Control flow: kbuild evaluates selected config symbols and builds the corresponding objects as built-in or modules. Object ordering here mostly follows driver names and config symbols.

State and persistence: this file affects compiled artifacts only. It has no runtime state, but it fixes module boundaries and symbol-resolution expectations.

Dependencies and integration points: integrates with Kconfig, module namespaces, exported common-probe symbols, and the IIO pressure directory. Any source file added to Kconfig must appear here to build.

Risks: mismatch between Kconfig symbols and object names causes silent missing drivers or unresolved exports. Multi-object modules must include all required implementation files, as with BMP280 core plus regmap. Hidden bus-helper symbols, such as `HSC030PA_I2C`, require object entries even when the source files are outside this work item.

Test signals: run targeted builds for the pressure directory, `make M=drivers/iio/pressure`, allmodconfig/modpost checks for unresolved symbols and namespace imports, and config matrix checks for I2C-only and SPI-only builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c

Purpose: I2C IIO pressure driver for Honeywell ABP pressure sensors. It supports many gage and differential part variants by mapping I2C IDs to pressure ranges and exposing a single pressure channel.

Important APIs, types, and functions: `enum abp_variant` and `abp_config[]` define supported part ranges in pascals. `struct abp_state` stores the I2C client, mutex, measurement-request length, scale, and offset. `abp060mg_get_measurement()` sends the measurement request, waits 40 ms, reads two 16-bit words, validates status/range bits, and returns raw pressure counts. `abp060mg_read_raw()` serves raw, offset, and scale. `abp060mg_init_device()` derives IIO scale and offset from the selected range.

Control flow: probe allocates the IIO device, detects whether SMBus quick is unavailable and therefore a dummy-byte request is needed, initializes model-specific conversion parameters, and registers the direct-mode device. Reads are serialized by a mutex.

State and persistence: only in-memory model parameters and mutex state are kept. No hardware configuration registers or persistent storage are used. The sensor is triggered per read and returns fresh counts.

Dependencies and integration points: depends on I2C and IIO core. It binds through the I2C ID table, not an OF table in this file. IIO ABI conversion relies on raw count plus offset and fractional scale.

Risks: `msleep_interruptible()` return is ignored, so interrupted sleeps can shorten conversion delay. `i2c_master_send()` and `recv()` positive short transfers are not checked. The psi conversion comments use approximate constants and one gage range appears to use `6985` for 1 psi rather than the usual 6895 pattern, so range table values deserve datasheet review. No device-tree compatible table limits firmware binding.

Test signals: validate each ID table entry maps to the expected min/max, test adapters with and without SMBus quick support, inject short I2C transfers and sensor status error bits, and compare raw/offset/scale conversions for gage and differential variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp060mg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c

Purpose: common IIO core for Honeywell ABP2 pressure and temperature sensors. It is bus-neutral and is used by I2C and SPI front ends through `struct abp2_ops`.

Important APIs, types, and functions: `abp2_range_config[]` and `abp2_triplet_variants[]` map Honeywell pressure triplets to pascal ranges. `abp2_get_measurement()` sends a sync command, waits by IRQ or fixed sleep, reads a NOP packet, and validates the ABP2 status byte. `abp2_read_raw()` exposes pressure and temperature raw values plus IIO scale/offset. `abp2_trigger_handler()` pushes pressure and temperature scans. `abp2_common_probe()` allocates the IIO device, enables `vdd`, parses pressure properties, computes pressure scale/offset, optionally requests an EOC IRQ, sets up a triggered buffer, and registers the device.

Control flow: direct and buffered reads both call `abp2_get_measurement()`. Direct reads decode 24-bit pressure from bytes 1..3 and temperature from bytes 4..6. Probe accepts either `honeywell,pressure-triplet` or explicit `honeywell,pmin-pascal` and `honeywell,pmax-pascal`; function A is the only transfer function present.

State and persistence: all state is in `struct abp2_data`: pressure limits, output limits, computed scale and offset, IRQ/completion, DMA-aligned RX/TX buffers, and scan buffer. No nonvolatile state is modified. The driver remembers computed conversion parameters until removal.

Dependencies and integration points: depends on IIO buffers/triggers, regulator framework, firmware properties, completion/IRQ support, and bus callbacks from `abp2030pa_i2c.c` or `abp2030pa_spi.c`. It exports `abp2_common_probe` in namespace `IIO_HONEYWELL_ABP2030PA`.

Risks: no mutex protects direct reads versus triggered-buffer reads through shared `rx_buf`, `tx_buf`, and completion. `data->function` defaults to zero, so only function A is effectively supported and no property controls it. Status validation accepts only `ABP2_ST_POWER`; latch-up and all other status anomalies become hard I/O errors. `p_scale` arithmetic multiplies by `NANO` and should remain reviewed for 64-bit bounds as ranges evolve.

Test signals: property parsing for known triplets, explicit pmin/pmax fallback, invalid ranges, IRQ timeout, polling fallback, busy status, bad status bytes, I2C/SPI transport short-transfer faults, and buffered scan layout with both channels active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h

Purpose: shared private header for the Honeywell ABP2 core and bus adapters.

Important APIs, types, and functions: defines `ABP2_MEASUREMENT_RD_SIZE`, `enum abp2_func_id`, `struct abp2_data`, `struct abp2_ops`, and the exported `abp2_common_probe()` prototype. `struct abp2_data` carries device pointer, bus ops, pressure limits, output transfer limits, computed pressure conversion fields, IRQ/completion, scan buffer, and DMA-aligned RX/TX buffers.

Control flow: the header establishes the inversion point between transport and core. Bus adapters only implement `read` and `write`; the core owns all measurement sequencing and IIO registration.

State and persistence: defines the complete runtime state layout for ABP2 devices. It contains no persistent state by itself. Buffer alignment uses `IIO_DMA_MINALIGN` to protect DMA-capable bus controllers.

Dependencies and integration points: includes Linux completion, IIO, and types headers. It is consumed by `abp2030pa.c`, `abp2030pa_i2c.c`, and `abp2030pa_spi.c`. Namespace imports in bus modules must match the exported common probe.

Risks: public-to-submodule coupling is tight; changing buffer sizes or scan layout affects both transports. Only function A is enumerated, limiting future ABP2 transfer-function support. `p_scale_dec` and `p_offset` types constrain conversion precision and range.

Test signals: compile all bus variants after structure changes, verify namespace/modpost output, and run static checks for buffer-size assumptions in bus callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c

Purpose: I2C transport adapter for the Honeywell ABP2 common IIO core.

Important APIs, types, and functions: `abp2_i2c_read()` receives up to `ABP2_MEASUREMENT_RD_SIZE` bytes into the core RX buffer and validates exact length. `abp2_i2c_write()` writes the command byte plus requested byte count from the core TX buffer and validates exact length. `abp2_i2c_probe()` checks `I2C_FUNC_I2C` and calls `abp2_common_probe()` with the adapter ops and `client->irq`.

Control flow: probe binds compatible or I2C ID `abp2030pa`, creates no state of its own, and delegates all runtime behavior to the core. Direct and buffered reads later enter this file only through the ops table.

State and persistence: transport state is the I2C client embedded in `data->dev`; no separate private data or persistent state exists.

Dependencies and integration points: depends on the I2C subsystem, OF/I2C ID matching, and namespace import `IIO_HONEYWELL_ABP2030PA`. Integrates with the ABP2 core's buffer and command lengths.

Risks: write transfers send `nbytes` bytes even though only `tx_buf[0]` is explicitly set by this function; the common core currently requests three bytes for sync, so stale bytes can be transmitted unless the sensor ignores them as expected. No retries are performed on short transfers or NACKs.

Test signals: I2C functionality rejection, exact-length read/write checks, IRQ and no-IRQ probe paths, and logic-analyzer verification of sync/NOP packet sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c

Purpose: SPI transport adapter for the Honeywell ABP2 common IIO core.

Important APIs, types, and functions: `abp2_spi_xfer()` bounds `nbytes`, puts the command in `tx_buf[0]`, and performs a full-duplex `spi_sync_transfer()` using the core RX/TX buffers. `abp2_spi_probe()` delegates to `abp2_common_probe()`. The OF and SPI ID tables both expose `honeywell,abp2030pa`/`abp2030pa`.

Control flow: all common measurement sequencing is owned by `abp2030pa.c`; this file supplies identical `read` and `write` callbacks because SPI command and response handling are full-duplex transfers.

State and persistence: no transport-private runtime state is stored. The SPI device is recovered from `data->dev`; buffers live in the common state.

Dependencies and integration points: depends on SPI core, OF/SPI ID matching, and ABP2 common-probe namespace import. It relies on board-level SPI mode/chip-select configuration.

Risks: `tx_buf` bytes after the command are not cleared in this function, so transfer padding can contain previous contents. There is no explicit SPI mode, bits-per-word, or max-speed validation. Full-duplex write semantics may differ from I2C command framing and should be checked against the datasheet for each command length.

Test signals: probe on SPI devices, transfer-size overflow, full-duplex command capture, bad status handling through the core, and module namespace/modpost validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/abp2030pa_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/adp810.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/adp810.c

Purpose: I2C IIO driver for the Aosong ADP810 differential pressure and temperature sensor.

Important APIs, types, and functions: `struct adp810_read_buf` models the packed 9-byte measurement payload: pressure, pressure CRC, temperature, temperature CRC, scale factor, scale CRC. `struct adp810_data` stores the I2C client and mutex. `adp810_measure()` sends the trigger command `0x37 0x2d`, waits 20 ms, reads the payload, and validates three CRC8 values with polynomial `0x31`. `adp810_read_raw()` exposes raw pressure/temperature and scale.

Control flow: every raw or scale read performs a fresh measurement under the mutex, then returns the relevant field. Probe initializes the mutex and registers a direct-mode two-channel IIO device.

State and persistence: no hardware configuration or persistent state is kept. The CRC table is global static state populated during measurement. Runtime state is limited to I2C client and mutex.

Dependencies and integration points: depends on I2C, CRC8, IIO core, `get_unaligned_be16()`, and OF/I2C IDs. Kconfig selects `CRC8`.

Risks: scale reads also trigger a full measurement, which is expensive and can fail even when callers only need metadata. `crc8_populate_msb()` runs on every measurement rather than once at init. There is no `i2c_check_functionality()` guard. The scale ABI for pressure returns the sensor-provided scale factor as an integer without documenting exact units in code.

Test signals: CRC failure injection for each field, short I2C transfer handling, read serialization under concurrent sysfs access, trigger timing tolerance, and raw/scale unit comparison with datasheet examples.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/adp810.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-core.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-core.c

Purpose: shared IIO core for Bosch BMP085/BMP180/BMP280/BME280/BMP380/BMP390/BMP580 pressure-family sensors. It owns calibration parsing, compensation math, direct reads, buffered reads, runtime PM, regulator/reset handling, and variant-specific chip descriptions.

Important APIs, types, and functions: `bmp280_common_probe()` is exported to bus adapters. `struct bmp280_chip_info` supplies variant callbacks, channels, regmap config, chip IDs, oversampling/filter/frequency tables, coefficients, triggers, and mode handlers. Key direct-read paths are `bmp280_read_raw_impl()`, `bmp280_write_raw_impl()`, and `bmp280_read_avail()`. Variant families include BMP/BME280 calibration and compensation, BMP380/BMP390 command and compensation code, BMP580 built-in-compensation reads and NVMEM access, and BMP180/BMP085 legacy EOC conversion code.

Control flow: bus drivers create a regmap and pass chip info to `bmp280_common_probe()`. Probe enables `vddd`/`vdda`, optional reset GPIO, verifies chip ID, runs preinit, applies chip config, reads calibration if needed, sets up triggered buffer and optional IRQ trigger, enters sleep, enables runtime PM, and registers the IIO device. Direct reads runtime-resume the chip, force a measurement, wait for conversion, call the variant read callback, apply coefficients for processed values, and autosuspend. Buffered operation enters normal mode on preenable and pushes compensated channel data from the variant trigger handler.

State and persistence: `struct bmp280_data` stores calibration values read once from device NVM, current oversampling/filter/frequency settings, current operating mode, regulators, completion for BMP085 EOC, optional trigger state, and DMA-aligned transfer buffers. BMP580 additionally registers an nvmem provider that can read and write three NVM rows; other calibration is read-only. Runtime PM persists selected settings in memory and reapplies chip config on resume.

Dependencies and integration points: depends on IIO core, IIO triggered buffers/triggers, regmap, regulators, runtime PM, optional GPIO reset, optional IRQ/fwnode properties, nvmem provider for BMP580, and bus-specific modules. It exports chip-info symbols and common probe in namespace `IIO_BMP280`.

Risks: this is a high-blast-radius core where conversion math, coefficient scaling, and endian handling differ per chip generation. `pm_runtime_get_sync()` return values are ignored in read/write paths. Some stack scan buffers are not zero-initialized in non-BME handlers, so padding review matters. BMP580 NVM write support exposes persistent device state and must be carefully permission-tested. Sampling-frequency availability lengths are stored as `ARRAY_SIZE(table) * 2`, which matches IIO list flattening but is easy to misuse. Optional IRQ trigger setup only runs when platform IRQ is positive.

Test signals: per-variant probe and chip-ID tests; coefficient parsing with known datasheet vectors; direct raw/processed reads; oversampling/filter/frequency write and rollback on config failure; runtime suspend/resume; triggered buffer scan layout; BMP085 EOC timeout; BMP380/BMP580 IRQ data-ready paths; BMP580 nvmem read/write; and allmodconfig namespace/modpost builds for I2C and SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c

Purpose: I2C bus front end for the Bosch BMP280-family common core.

Important APIs, types, and functions: `bmp280_i2c_probe()` obtains the matched `bmp280_chip_info`, initializes an I2C regmap from the chip-specific regmap config, and calls `bmp280_common_probe()`. OF and I2C ID tables map BMP085, BMP180, BMP280, BME280, BMP380, and BMP580 names to exported chip-info structures.

Control flow: all runtime operations after probe are delegated to the common core through regmap. The adapter passes `client->irq` so core code can configure BMP085 EOC or BMP380/BMP580 data-ready triggers when available.

State and persistence: no I2C-private state is allocated. The regmap and IIO state are devm-managed through the common probe.

Dependencies and integration points: depends on I2C, regmap I2C, PM ops from the core, and namespace `IIO_BMP280`. Kconfig selects this helper when BMP280 and I2C are enabled.

Risks: `id->name` is used for the IIO name, so OF-only devices still depend on an I2C ID being available from the client. There is no explicit I2C functionality check, relying on `devm_regmap_init_i2c()` and bus core behavior. Match table drift can cause a compatible to select the wrong compensation path.

Test signals: probe every compatible/ID mapping, verify IRQ forwarding, build as module with namespace import, and exercise regmap failure handling on unsupported adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c

Purpose: regmap access policy definitions for BMP180, BMP280, BME280, BMP380, and BMP580 register maps.

Important APIs, types, and functions: per-family `*_is_writeable_reg()` and `*_is_volatile_reg()` callbacks classify writable control registers and volatile data/status registers. Exported `regmap_config` objects define 8-bit registers/values, max register, RBTREE cache, and access callbacks for each family.

Control flow: bus adapters choose the chip-info regmap config; regmap then uses these callbacks to cache stable calibration/config registers while bypassing volatile sensor data and status. Write restrictions prevent unintended writes to read-only calibration/data registers.

State and persistence: regmap cache state is maintained by regmap at runtime. This file itself stores only static policy. BMP580 writeable NVM access registers are exposed so the core nvmem operations can program rows.

Dependencies and integration points: depends on regmap and register constants from `bmp280.h`. Exports configs in namespace `IIO_BMP280` to both I2C and SPI adapters through chip-info structures.

Risks: incorrect volatile classification can return stale pressure/temperature/status values; incorrect writeable classification can block required setup or permit unsafe writes. `max_register` must include undocumented registers used by workarounds or NVM operations. BMP580 exposes many control registers, increasing review burden.

Test signals: regmap cache behavior tests around repeated sensor reads, writes to allowed and disallowed registers, variant-specific probe smoke tests, and static review when adding new registers in `bmp280.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-regmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c

Purpose: SPI bus front end and custom regmap bus for BMP280-family sensors.

Important APIs, types, and functions: `bmp280_regmap_spi_write()` clears bit 7 for write commands and performs a two-byte SPI transaction. `bmp280_regmap_spi_read()` uses basic SPI read. `bmp380_regmap_spi_read()` handles BMP3xx/BMP5xx-style reads by discarding the first returned dummy byte. `bmp280_spi_probe()` selects the regmap bus based on `chip_info->spi_read_extra_byte`, initializes regmap, and calls `bmp280_common_probe()`.

Control flow: match tables map SPI/OF IDs to chip-info. Probe builds a regmap with either normal BMP280 or extra-byte BMP380 bus semantics, then hands off all IIO behavior to the core.

State and persistence: no SPI-private state persists beyond the devm regmap. Temporary read buffers are stack local.

Dependencies and integration points: depends on SPI, custom regmap bus callbacks, chip-info exports, common PM ops, and namespace `IIO_BMP280`.

Risks: write callback copies exactly two bytes from regmap data, so it assumes 8-bit register plus 8-bit value writes. `bmp380_regmap_spi_read()` limits reads to `BME280_BURST_READ_BYTES`, which must remain large enough for all SPI bulk reads using the extra-byte protocol. SPI mode and max speed are not validated in code. ID table includes `bmp181` alias mapping to BMP180 only on SPI.

Test signals: logic-analyzer verification of read/write command framing, BMP380/BMP580 dummy-byte reads, bulk read length rejection, all compatible mappings, and common-core runtime PM through SPI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280.h

Purpose: shared private interface and register map for BMP280-family bus adapters, regmap policy, and common core.

Important APIs, types, and functions: defines register addresses, bit masks, command values, chip IDs, skipped-value sentinels, calibration structures (`bmp180_calib`, `bmp280_calib`, `bmp380_calib`), `enum bmp280_op_mode`, runtime `struct bmp280_data`, and variant descriptor `struct bmp280_chip_info`. It declares exported chip-info instances, regmap configs, `bmp280_common_probe()`, and `bmp280_dev_pm_ops`.

Control flow: bus drivers consume chip-info and regmap declarations, while the core fills `struct bmp280_data` and calls callbacks declared through `struct bmp280_chip_info`. Register constants drive every variant's preinit, config, read, and interrupt path.

State and persistence: this header defines the complete common runtime state, including regulators, calibration union, current oversampling/filter/frequency settings, current op mode, optional trigger/EOC state, and DMA-aligned buffers. It also defines BMP580 NVM registers used for persistent writes in the core.

Dependencies and integration points: depends on device, regmap, regulators, IIO, and bitops APIs. It is the coupling point among `bmp280-core.c`, `bmp280-regmap.c`, `bmp280-i2c.c`, and `bmp280-spi.c`.

Risks: register definitions for five chip generations in one file make accidental cross-family reuse easy. `struct bmp280_chip_info` is large and callback-heavy; missing callbacks can crash common paths if a new variant is incomplete. Buffer union sizes must cover all regmap bulk reads. The public symbol declarations must match namespace exports and Kconfig/Makefile module boundaries.

Test signals: compile all translation units after any field/register changes, static assertions or review for buffer sizes, modpost namespace checks, and variant probe tests for each chip-info instance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/bmp280.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c

Purpose: IIO pressure driver for a barometer presented by the ChromeOS Embedded Controller sensor hub.

Important APIs, types, and functions: `struct cros_ec_baro_state` embeds `struct cros_ec_sensors_core_state` and owns a two-entry channel array for pressure plus timestamp. `cros_ec_baro_read()` handles raw pressure through `cros_ec_sensors_read_cmd()`, reads scale by sending `MOTIONSENSE_CMD_SENSOR_RANGE`, and delegates other attributes to `cros_ec_sensors_core_read()`. `cros_ec_baro_write()` updates the EC sensor range for scale writes and delegates other writes. `cros_ec_baro_probe()` initializes common EC sensor state, builds channel descriptors, and registers through `cros_ec_sensors_core_register()`.

Control flow: probe requires a parent `cros_ec_dev`, allocates IIO state, calls `cros_ec_sensors_core_init()`, configures a pressure channel when `state->core.type` is `MOTIONSENSE_TYPE_BARO`, appends a timestamp channel, sets `read_ec_sensors_data`, and registers callbacks. Runtime reads and writes hold `core.cmd_lock` while sending EC host commands.

State and persistence: state is EC-sensor runtime metadata, channel definitions, current range tracking, and IIO scan buffering in memory. Scale writes update EC sensor range and set `range_updated`/`curr_range`; persistence beyond runtime depends on EC firmware behavior.

Dependencies and integration points: depends on `IIO_CROS_EC_SENSORS_CORE`, ChromeOS EC command protocol, IIO kfifo/triggered buffer support, EC platform data, and platform-device ID `cros-ec-baro`. Integration is with the EC abstraction, not a specific pressure sensor datasheet.

Risks: behavior depends on EC firmware units and range semantics; scale is returned as `range / (10 << CROS_EC_SENSOR_BITS)` to produce kPa. Raw data is stored through a `u16` local cast to `s16 *`, so signedness and width must remain aligned with EC sensor format. Unknown motion sensor types abort probe. Range writes round up, which is intentional but can surprise exact-value tests.

Test signals: EC sensor enumeration with and without parent EC device, pressure raw/scale reads, scale writes and `curr_range` update, sample-frequency delegation, triggered buffer capture through `cros_ec_sensors_push_data`, suspend/resume through EC common PM ops, and comparison with EC firmware-reported units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/cros_ec_baro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c

Purpose: I2C IIO driver for All Sensors DLH low-voltage digital pressure sensors, with DLHL60D and DLHL60G variants.

Important APIs, types, and functions: `struct dlh_info` stores variant name, digital offset factor, and full-scale span. `struct dlh_state` stores client, variant info, optional interrupt completion, and RX buffer. `dlh_start_capture_and_read()` sends a single-shot command, waits by IRQ or delay, and reads seven bytes. `dlh_read_raw()` exposes raw, scale, and offset. `dlh_trigger_handler()` captures active channels into an IIO buffer.

Control flow: probe checks I2C functionality, gets match data, optionally requests a rising IRQ, initializes triggered buffers, and registers the IIO device. Direct reads claim direct mode, start a conversion, read pressure and temperature, and release direct mode. Buffered capture performs the same conversion flow from the trigger handler.

State and persistence: variant constants and optional IRQ mode persist in memory. No hardware configuration persists. The shared `rx_buf` is reused for direct and triggered reads, with direct reads protected by IIO direct-mode claim.

Dependencies and integration points: depends on I2C, IIO triggered buffers, OF/I2C match data, and optional device IRQ. Uses IIO scan definitions for 24-bit big-endian pressure/temperature fields stored in 32-bit slots with shift.

Risks: `i2c_master_recv()` only checks negative errors and not short positive reads. Interrupt timeout is only 5 ms, matching conversion time tightly. `mdelay()` is used for polling mode, which busy-waits. Status must equal `0x40`; other status variants are treated as busy. Buffered path does not include a timestamp channel in the channel table.

Test signals: DLHL60D/G scale and offset math, optional IRQ and polling modes, short-read injection, status-byte error handling, direct-read busy behavior while buffer enabled, and active-channel scan ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dlhl60d.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dps310.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/dps310.c

Purpose: I2C/regmap IIO driver for Infineon DPS310 pressure and temperature sensor. It supports processed pressure/temperature plus writable sampling frequency and oversampling ratio.

Important APIs, types, and functions: `struct dps310_data` stores regmap, mutex, calibration coefficients, last raw pressure/temp, and timeout-recovery flag. `dps310_get_coefs()` parses calibration registers. `dps310_startup()` configures pressure/temp measurement, waits for coefficients, reads them, and applies a temperature workaround. `dps310_ready()` polls ready bits and performs one reset/reinit recovery on timeout. `dps310_calculate_pressure()` and `dps310_calculate_temp()` implement compensation. `dps310_read_raw()` and `dps310_write_raw()` implement IIO ABI.

Control flow: probe initializes regmap, registers a reset action, starts continuous background measurements, and registers direct-mode IIO channels. Reads poll the relevant ready bit based on configured sample frequency, read 24-bit signed raw data, and compute processed values. Writes update precision/rate registers under the mutex.

State and persistence: calibration coefficients are cached in memory. Raw pressure/temp are cached for compensation, and pressure calculation may opportunistically refresh temperature if ready. Hardware settings persist in sensor registers while powered; remove/reset action resets the chip. Regmap uses RBTREE cache with volatile status/data registers.

Dependencies and integration points: depends on I2C, regmap I2C, IIO sysfs, mutexes, 64-bit math helpers, and ACPI ID `IFX3100`.

Risks: setters allow `val == 0`, then call `ilog2(0)`, which is invalid; oversampling/rate inputs should be powers of two in the 1..128 range. `dps310_calculate_pressure()` returns `-ERANGE` for negative compensated pressure and clamps high values to `INT_MAX`. Timeout recovery resets and reapplies startup once; repeated failures are suppressed by `timeout_recovery_failed`. Undocumented workaround registers require careful regression testing.

Test signals: calibration parsing with known bytes, processed temperature/pressure vectors, sampling/oversampling invalid input including zero and non-powers-of-two, timeout recovery path, reset action, regmap volatile/cache behavior, and ACPI/I2C probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/dps310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c

Purpose: IIO driver for HID Sensor Hub atmospheric pressure reports.

Important APIs, types, and functions: `struct press_state` contains HID callbacks, common HID sensor attributes, pressure attribute info, scan buffer, scale fields, offset, and timestamp. `press_parse_report()` discovers report metadata and scale. `press_read_raw()` handles raw pressure, scale, offset, sample frequency, and hysteresis. `press_write_raw()` updates sample frequency and hysteresis. `press_capture_sample()` stores incoming HID samples, and `press_proc_event()` pushes buffered samples.

Control flow: platform probe parses common attributes for HID usage `HID_USAGE_SENSOR_PRESSURE`, duplicates and adjusts channels according to descriptor size, sets up trigger support, registers the IIO device, and registers sensor-hub callbacks. Runtime raw reads power the sensor, request a synchronous raw value, and power it back down. Buffered events are callback-driven by the HID hub.

State and persistence: runtime state includes report metadata, scale/offset, latest sample, and latest timestamp. Sample frequency and hysteresis writes are delegated to HID common helpers and may persist according to hub behavior.

Dependencies and integration points: depends on HID sensor hub, HID IIO common/trigger helpers, platform device ID `HID-SENSOR-200031`, and namespace `IIO_HID`.

Risks: `press_capture_sample()` casts raw HID buffers directly to `u32`/`s64` without length or alignment checks in this file. Timestamp is reused until overwritten, so missing timestamp reports fall back to current IIO time only when zero. Correct scale depends entirely on HID descriptor metadata. Manual unregister/remove paths must stay aligned with non-devm registration.

Test signals: HID descriptor variations for sample size/sign, synchronous raw reads, buffer event ordering with and without timestamp reports, sample-frequency/hysteresis writes, suspend/resume via `hid_sensor_pm_ops`, and callback cleanup on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hid-sensor-press.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hp03.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hp03.c

Purpose: I2C IIO driver for Hope RF HP03 pressure and temperature sensor, which uses separate ADC and EEPROM I2C addresses.

Important APIs, types, and functions: `struct hp03_priv` stores the ADC client, mutex, XCLR GPIO, dummy EEPROM client, EEPROM regmap, and latest compensated pressure/temp. `hp03_update_temp_pressure()` reads calibration coefficients from EEPROM, toggles XCLR, performs pressure and temperature conversions, byte-swaps ADC words, and applies datasheet compensation. `hp03_read_raw()` exposes raw pressure/temp and scale.

Control flow: probe allocates IIO state, requests `xclr` GPIO, creates a dummy I2C EEPROM client at `0x50`, initializes an EEPROM regmap, and registers the IIO device. Every read updates both pressure and temperature under the mutex, then returns the requested channel.

State and persistence: latest pressure and temperature are cached in memory but refreshed on every read. EEPROM calibration is persistent on the sensor and read each time rather than cached. XCLR is driven high only during ADC sampling and cleared on error paths.

Dependencies and integration points: depends on I2C, regmap I2C, GPIO descriptors, and IIO core. It binds OF compatible `hoperf,hp03` and I2C ID `hp03`.

Risks: calibration EEPROM is read on every sysfs read, increasing I2C traffic and error surface. The compensation math uses many 32-bit intermediates and datasheet-specific shifts. No explicit I2C functionality check is present. The dummy EEPROM client assumes the fixed secondary address is free and reachable on the same adapter.

Test signals: XCLR GPIO behavior on success and failed ADC reads, EEPROM regmap read errors, known calibration/ADC compensation vectors, scale ABI checks, and secondary-address conflict handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hp03.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hp206c.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hp206c.c

Purpose: I2C IIO driver for HOPERF HP206C precision barometer and altimeter sensor.

Important APIs, types, and functions: `struct hp206c_data` stores mutex, client, and selected temperature/pressure oversampling indices. `hp206c_soft_reset()` resets the chip and enables compensation. `hp206c_wait_dev_rdy()` polls `DEV_RDY`. `hp206c_conv_and_read()` performs conversion, waits, polls readiness again, and reads a 20-bit value. `hp206c_read_raw()` exposes raw pressure/temp, scale, and oversampling ratio. `hp206c_write_raw()` chooses closest descending oversampling ratio.

Control flow: probe checks SMBus capabilities, allocates state, soft-resets the device, then registers direct-mode IIO channels. Reads are serialized under a mutex. Conversion command and wait time depend on channel and current OSR index.

State and persistence: selected OSR indices persist in driver memory. Hardware compensation is enabled during probe. No nonvolatile writes are performed.

Dependencies and integration points: depends on I2C SMBus byte, byte-data, and block-read operations; IIO sysfs attributes; `find_closest_descending()`; OF/I2C/ACPI matching.

Risks: `hp206c_attributes` exposes `sampling_frequency_available` even though the channel property is oversampling ratio, which may be confusing ABI naming. Defaults for OSR indices are zero because state is zeroed, selecting 4096. Readiness polling can wait up to roughly 160 ms before conversion and again after conversion. Soft-reset failure maps to `-ENODEV`, losing original error details.

Test signals: SMBus capability rejection, soft reset and compensation enable, raw 20-bit sign extension for temperature, OSR write selection for exact and in-between values, timeout in `DEV_RDY`, and ACPI/OF probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hp206c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c

Purpose: common IIO core for Honeywell TruStability HSC/SSC pressure and temperature sensors. Bus-specific files provide the receive callback.

Important APIs, types, and functions: `hsc_triplet_variants[]` and `hsc_range_config[]` map pressure triplets to pascal ranges. `hsc_func_spec[]` defines output ranges for transfer functions A, B, C, and F. `hsc_get_measurement()` calls the bus receive callback and validates status. `hsc_read_raw()` extracts 14-bit pressure and 11-bit temperature from the 4-byte frame and exposes scale/offset. `hsc_common_probe()` parses firmware properties, enables `vdd`, computes pressure conversion fields, sets up triggered buffer, and registers the IIO device.

Control flow: direct and buffered reads receive a four-byte measurement, check that status bits are zero, and decode fields from big-endian frame layout. Probe requires `honeywell,transfer-function` and `honeywell,pressure-triplet`; if the triplet starts with `NA`, it falls back to explicit pmin/pmax properties.

State and persistence: runtime state includes function, pressure limits, output min/max, computed scale and offset, latest validity flag, raw buffer, and scan buffer. No persistent storage is modified.

Dependencies and integration points: depends on IIO buffers/triggers, regulator framework, firmware properties, unaligned/bitfield helpers, and bus receive callbacks declared in `hsc030pa.h`. Exports `hsc_common_probe` in namespace `IIO_HONEYWELL_HSC030PA`.

Risks: no mutex protects shared `buffer` and `is_valid` between direct reads and triggered buffers. Pressure offset uses `IIO_VAL_INT_PLUS_MICRO` while scale uses nano precision; rounding should be verified for small ranges. `str_has_prefix(triplet, "NA")` accepts any `NA...` value for explicit range mode. Stale-data status maps to `-EAGAIN`, which callers may retry aggressively.

Test signals: all transfer functions, representative triplet mappings, explicit pmin/pmax mode, invalid status codes, direct versus buffered concurrency, scale/offset vectors from datasheet, regulator failure, and namespace/modpost builds with bus modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h -->
# sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h

Purpose: shared private header for Honeywell HSC/SSC common core and bus adapters.

Important APIs, types, and functions: defines `HSC_REG_MEASUREMENT_RD_SIZE`, `HSC_RESP_TIME_MS`, callback type `hsc_recv_fn`, `struct hsc_data`, `struct hsc_chip_data`, `enum hsc_func_id`, and exported `hsc_common_probe()`. `struct hsc_data` contains device pointer, chip metadata, receive callback, validity flag, pressure conversion fields, scan buffer, and DMA-aligned raw buffer.

Control flow: bus adapters implement only the receive callback and call `hsc_common_probe()`. The core uses `hsc_chip_data` to validate measurements and expose channels.

State and persistence: describes in-memory runtime state only. There is no persistent storage. Buffer alignment supports DMA-capable buses.

Dependencies and integration points: depends on Linux types and IIO declarations. It is consumed by common, I2C, and SPI HSC driver files; exported namespace must match bus module imports.

Risks: shared state has no lock field, so bus/core users must account for concurrency elsewhere. The measurement size and scan layout are hard-coded for this sensor family. Conversion field types mix `s64` values with `s32` decimal remainders, so precision changes need ABI review.

Test signals: compile I2C/SPI/common together, validate callback prototype compatibility, static checking for buffer-size assumptions, and namespace import/export checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/pressure/hsc030pa.h -->
