# subset-b-003869 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7476.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7476.c

Purpose: SPI IIO driver for small single-channel SAR ADCs in the AD7466/AD7476/AD727x/AD7091R/AD7940, TI ADC081S/101S/121S, ADS786x, ROHM, LTC2314-14, and BD79105-compatible families. It presents one voltage channel plus a software timestamp and supports direct reads and triggered-buffer sampling.

Important APIs, types, and functions: `struct ad7476_chip_info` describes per-part bit width, channel scan layout, internal/reference supplies, VDRIVE, conversion-start requirements, and optional reset/pre/post conversion hooks. `struct ad7476_state` stores the SPI message/transfer, copied channel specs, optional `adi,conversion-start` GPIO, scale in mV, and DMA-aligned sample/timestamp buffer. Key functions are `ad7476_probe()`, `ad7476_read_raw()`, `ad7476_scan_direct()`, `ad7476_trigger_handler()`, `ad7091_convst()`, `bd79105_convst_enable()`, `bd79105_convst_disable()`, and `ad7091_reset()`.

Control flow: probe allocates an IIO device, resolves `spi_get_device_match_data()`, enables `vcc`, optionally reads `vref`, enables `vdrive`, requests conversion-start GPIO, copies chip channel templates, builds a single RX SPI message, installs a triggered buffer, optionally resets the chip, and registers the IIO device. Direct raw reads claim direct mode, run optional pre-conversion, perform `spi_sync()`, post-process the big-endian sample according to `scan_type.shift/realbits`, and return an integer. Triggered reads follow the same SPI message path and push the DMA-aligned buffer with a timestamp.

State and persistence behavior: no nonvolatile state is managed. Runtime state is regulator enablement, GPIO output level, `scale_mv`, copied IIO channel metadata, and the reusable SPI message. If a conversion-start GPIO exists, probe exposes raw reads for otherwise buffered-only AD7091-style templates.

Dependencies and integration points: depends on SPI, regulator, GPIO descriptor, IIO direct mode, IIO triggered buffers, and software timestamp channels. Device matching is SPI ID based. The data buffer is aligned for DMA-safe SPI controllers.

Risks: `ad7476_scan_direct()` returns immediately on SPI error before running `conversion_post_op`, which can leave BD79105 `CONVSTART` asserted after a failed direct read. Scale depends on correct regulator voltage or internal reference metadata. Channel shifts differ by family, so chip-info table mistakes silently corrupt readings. Optional AD7091 reset uses a one-byte SPI read and assumes that transfer is valid on all controllers.

Test signals: build the module with representative IDs; probe with external and internal reference configurations; verify raw read masking for 8/10/12/14/16-bit parts; test triggered buffer timestamps; test missing required BD79105 conversion GPIO; inject SPI errors around direct reads; verify regulator and GPIO cleanup through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7476.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.c

Purpose: shared IIO core for the AD7605/AD7606/AD7606B/AD7606C/AD7607/AD7608/AD7609/AD7616 simultaneous-sampling ADC family. Bus-specific SPI and parallel wrappers provide `struct ad7606_bus_ops`; this file owns chip tables, channels, conversion control, direct reads, triggered buffers, oversampling, scale/range selection, calibration, backend/offload setup, and suspend/resume.

Important APIs, types, and functions: exports chip descriptors such as `ad7606_8_info`, `ad7606b_info`, `ad7606c_16_info`, `ad7606c_18_info`, and `ad7616_info`, plus `ad7606_probe()`, `ad7606_reset()`, `ad7606_pwm_set_low()`, `ad7606_pwm_set_swing()`, and `ad7606_pm_ops`. The main state is `struct ad7606_state` from `ad7606.h`. Key internal paths include `ad7606_probe_channels()`, `ad7606_read_raw()`, `ad7606_write_raw()`, `ad7606_scan_direct()`, `ad7606_trigger_handler()`, `ad7606_interrupt()`, `ad7606_set_sampling_freq()`, `ad7606_write_scale_hw/sw()`, `ad7606_write_os_hw/sw()`, `ad7616_sw_mode_setup()`, and `ad7606b_sw_mode_setup()`.

Control flow: `ad7606_probe()` allocates and stores the IIO device, initializes the mutex and supplies, determines software mode, requests GPIOs, chooses an `iio_info` surface, optionally configures SPI offload, creates channels, resets the chip, sets up PWM or CONVST GPIO conversion control, configures IIO backend or IRQ-triggered buffer mode, installs hardware or software scale/oversampling callbacks, runs software-mode setup when requested or offload requires single DOUT, applies gain calibration, and registers the device. Direct reads start a conversion via GPIO or PWM, wait on BUSY completion or a fixed delay, read all channels through `bops->read_block()`, mask/sign-extend the selected channel, then return the conversion line low. Buffered IRQ mode lowers CONVST/PWM when BUSY falls, polls the trigger, reads a full block in the trigger handler, pushes timestamped data, and starts the next conversion. Backend/offload mode uses PWM swinging and backend/offload buffer callbacks instead of software demux.

State and persistence behavior: runtime state includes selected per-channel range, oversampling ratio, PWM period/duty, software-mode flag, calibration register values, channel metadata, GPIO output levels, and completion/trigger state. No persistent storage is written; programmed device registers are volatile and rebuilt on probe/reset. Suspend drives standby/range GPIOs when available and resume restores range and resets.

Dependencies and integration points: integrates with regulators (`avcc`, `vdrive`, optional `refin`), GPIO descriptors (`adi,conversion-start`, `reset`, `adi,range`, `standby`, `adi,first-data`, oversampling), PWM, IIO triggered buffers, IIO backend, bus ops from SPI/parallel wrappers, debugfs reg access in software mode, and firmware child nodes for bipolar/differential/rfilter channel properties.

Risks: channel count, storagebits, backend/offload, and scan mask handling vary by bus path. Software mode relies on `reg_read/reg_write` availability and valid register layouts. `ad7606_write_raw()` chooses closest scale/OSR rather than requiring exact user input. Direct reads are disabled with AXI backend. PWM fallback is allowed for backend/offload but rejected for normal non-backend use without CONVST GPIO. Calibration writes require direct-mode exclusion but still depend on chip-specific range arrays.

Test signals: build SPI and parallel wrappers against exported symbols; probe all major chip descriptors; exercise direct raw, triggered buffer, backend buffer, and offload buffer paths; verify scale/oversampling available lists; test firmware bipolar/differential validation; test calibration gain/offset/phase on AD7606B/C; test missing CONVST and missing PWM cases; test suspend/resume with standby GPIO; validate scan masks for backend/offload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.h -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.h

Purpose: private shared header for the AD7606 family core and bus-wrapper drivers. It defines register constants, chip metadata, per-channel state, the core runtime state, bus operation callbacks, bus-info pairing, exported probe/reset/PWM APIs, exported chip descriptors, and PM ops macro wiring.

Important APIs, types, and functions: `struct ad7606_chip_info` captures max sample rate, name, data width, channel count, setup callbacks, oversampling tables, reset delay, offload storage bits, and calibration support. `struct ad7606_chan_info` stores available scales, selected range, register offset, and gain resistor value. `struct ad7606_state` is the central per-device object shared by core and bus wrappers. `struct ad7606_bus_ops` abstracts backend config, offload config, block reads, software-mode config, register access, scan-mode updates, and SPI command encoding. Public functions are `ad7606_probe()`, `ad7606_reset()`, `ad7606_pwm_set_swing()`, and `ad7606_pwm_set_low()`.

Control flow: this file has no executable control flow, but it defines the contract used by `ad7606_spi.c` and `ad7606_par.c` to enter the common `ad7606_probe()` path. The core calls bus ops conditionally based on which callbacks are non-NULL.

State and persistence behavior: declares the in-memory state fields that persist for the device lifetime: supplies and GPIO-derived settings, oversampling/range state, backend pointer, completion, trigger, DMA-aligned scan buffers, offload flag, and bus-specific private data. Hardware register values are represented by `chan_info`, `oversampling`, and callback-selected write methods but are not stored persistently outside the device.

Dependencies and integration points: depends on IIO core declarations, IIO backend forward declarations through included users, PWM, GPIO, and bus-wrapper ownership. Register macros cover AD7616 range/oversampling and AD7606B/C range/calibration layouts.

Risks: any change to `struct ad7606_state` or `struct ad7606_bus_ops` impacts both SPI and parallel modules. Macro register encodings must stay synchronized with the core write paths. `AD760X_MAX_CHANNELS` bounds arrays for 16 physical channels; widening channel support would require structural changes.

Test signals: compile all AD7606 modules together and separately as modules; verify exported symbols and namespace imports; run sparse/build tests for struct field users; exercise AD7616 and AD7606B/C software-mode register writes that rely on the header macros.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_bus_iface.h -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_bus_iface.h

Purpose: small platform-data interface for AD7606 parallel/backend bus register access. It gives board/backend glue a way to provide register read/write functions when a parallel interface is paired with an IIO backend.

Important APIs, types, and functions: declares `struct iio_backend` and defines `struct ad7606_platform_data` with `bus_reg_read(struct iio_backend *back, u32 reg, u32 *val)` and `bus_reg_write(struct iio_backend *back, u32 reg, u32 val)`.

Control flow: no executable logic. `ad7606_par.c` fetches `st->dev->platform_data`, calls these callbacks from its `ad7606_bi_bops.reg_read/reg_write`, and returns callback results to the common core.

State and persistence behavior: no state is owned here. The callbacks operate on backend-owned state and volatile ADC registers.

Dependencies and integration points: integrates the AD7606 parallel wrapper with `linux/iio/backend.h` consumers while keeping the header independent via a forward declaration. It is a kernel-internal platform-data contract, not a userspace ABI.

Risks: the parallel wrapper assumes valid platform data when backend register access is used; missing callbacks can cause NULL dereferences if a backend configuration advertises software register access without this data. The interface has no capability discovery or locking, so the common core's direct-mode and mutex rules must be preserved by callers.

Test signals: compile `ad7606_par.c`; probe a backend-backed platform with callback data; exercise debugfs register access and software-mode scale/oversampling writes; test absent or failing backend callbacks in board glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_bus_iface.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_par.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_par.c

Purpose: platform/parallel-bus wrapper for the AD7606 family. It handles memory-mapped 8-bit or 16-bit sample reads and a newer IIO-backend-backed parallel path, then delegates all common ADC behavior to `ad7606_probe()`.

Important APIs, types, and functions: `ad7606_par_probe()` chooses chip info from firmware match data or platform IDs, selects backend bus ops when `io-backends` is present, maps the I/O resource for traditional parallel mode, and calls the core. `ad7606_par16_read_block()` and `ad7606_par8_read_block()` use `insw()`/`insb()` to read channel blocks. `ad7606_par_bus_setup_iio_backend()`, `ad7606_par_bus_update_scan_mode()`, `ad7606_par_bus_reg_read()`, and `ad7606_par_bus_reg_write()` implement backend bus ops.

Control flow: firmware-backed probe with `io-backends` bypasses IRQ/resource mapping and enters core probe with backend bus ops. Otherwise probe requires an IRQ and memory resource, maps it, then chooses 16-bit or 8-bit read ops based on resource size. Traditional reads optionally consume the first word/bytes, validate `adi,first-data` GPIO alignment, reset on mismatch, and read the remaining samples. Backend setup obtains and enables an IIO backend, requests a buffer, enforces PWM presence, sets sign-extension data format on every channel, and uses backend channel enable/disable in scan-mode updates.

State and persistence behavior: no independent persistent state beyond the memory base passed into `struct ad7606_state` and backend pointer stored by the core state. A first-data alignment failure resets the ADC but does not persist error state.

Dependencies and integration points: depends on platform devices, OF matching, memory-mapped I/O, GPIO for first-data validation through common state, IIO backend, `ad7606.h`, and `ad7606_bus_iface.h`. Imports `IIO_AD7606` and `IIO_BACKEND` namespaces.

Risks: backend register callbacks depend on valid `dev->platform_data`. Resource-size based 8-bit versus 16-bit selection is simple and may misclassify unusual mappings. First-data validation reads one sample before checking alignment, so error recovery discards that block. Backend mode requires PWM because conversion timing is not GPIO-driven.

Test signals: probe 8-bit and 16-bit memory resources; verify `frstdata` reset behavior; test backend `io-backends` path with channel scan masks; test missing IRQ/resource failures; test all compatible IDs against exported chip descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_par.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_spi.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_spi.c

Purpose: SPI-bus wrapper for AD7606-family devices. It supplies block-read, register-read/write, software-mode setup, scan-mask validation, and optional SPI offload/DMA streaming hooks to the common AD7606 core.

Important APIs, types, and functions: `struct spi_bus_data` stores SPI offload objects and optimized transfer state. `ad7606_spi_probe()` resolves a `struct ad7606_bus_info` and calls `ad7606_probe()`. Read paths are `ad7606_spi_read_block()`, `ad7606_spi_read_block14to16()`, and `ad7606_spi_read_block18to32()`. Register paths are `ad7606_spi_reg_read()`, `ad7606_spi_reg_write()`, `ad7616_spi_rd_wr_cmd()`, and `ad7606b_spi_rd_wr_cmd()`. Offload support is implemented by `ad7606_spi_offload_probe()`, buffer enable/disable callbacks, and SPI offload trigger ops.

Control flow: probe maps each compatible to chip info plus bus ops. Standard SPI reads transfer all channel samples and convert 16-bit big-endian data to CPU order, while AD7607 and AD7608/7609/7606C-18 use 14-bit or 18-bit transfers into 16/32-bit storage. Software-mode register access performs a command transfer followed by a data transfer for reads or one 16-bit command/data write. Offload probe is attempted by the core; if no offload provider exists it returns success without enabling offload, otherwise it registers a data-ready trigger, requests RX stream DMA, installs DMAengine buffer ops, and marks `st->offload_en`. Offload buffer enable optimizes an RX stream message, enables the data-ready trigger, and starts conversion PWM swing; disable stops PWM, disables trigger, and unoptimizes the message.

State and persistence behavior: per-bus offload state is devm-managed in `st->bus_data`. Register writes configure volatile ADC mode, single DOUT, ranges, and oversampling through the common core. Offload requires all physical channels in the scan mask because the DMA stream cannot demux partial channel sets.

Dependencies and integration points: depends on SPI core, SPI offload provider/consumer APIs, IIO DMAengine buffer, PWM helpers exported by the core, DT binding trigger event constants, and `ad7606.h`. It imports `IIO_AD7606` and `IIO_DMAENGINE_BUFFER`.

Risks: offload path has strict scan-mask semantics and assumes hardware-compatible storagebits. Register command encodings differ between AD7616 and AD7606B/C; wrong bus-info pairing breaks software mode. The standard `spi_read()` block conversion mutates the receive buffer in place. Offload failure unwinding must keep optimized messages and triggers balanced.

Test signals: run direct and buffered reads for 16/14/18-bit devices; exercise software-mode register reads/writes for AD7616 and AD7606B/C; test no-offload fallback, offload probe success, offload buffer enable/disable, and invalid partial scan masks; validate single-DOUT software setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7606_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7625.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7625.c

Purpose: platform IIO driver for high-speed LVDS ADCs AD7625, AD7626, AD7960, and AD7961. It requires an AXI ADC-style IIO backend and uses two PWMs to generate conversion and gated clock burst waveforms.

Important APIs, types, and functions: `struct ad7625_chip_info` captures part name, max sampling rate, timing spec, channel spec, power-down/bandwidth/reference capabilities. `struct ad7625_state` stores backend, reference clock rate, CNV and clk_gate PWMs, rounded waveforms, EN GPIO capabilities, reference voltage, and sampling frequency. Key functions are `ad7625_probe()`, `ad7625_set_sampling_freq()`, `ad7625_read_raw()`, `ad7625_write_raw()`, `ad7625_parse_mode()`, `ad7960_set_mode()`, `devm_ad7625_pwm_get()`, `devm_ad7625_regulator_setup()`, and buffer preenable/postdisable callbacks.

Control flow: probe allocates IIO state, rejects unsupported self-clocked mode, parses EN GPIO wiring and always-on properties into capability booleans, enables supplies and determines REF/REFIN/internal reference source, sets EN pins for valid reference/bandwidth mode, acquires/disables PWMs and the reference clock, registers a one-channel differential IIO device with backend buffer, sets default sampling frequency to max or 2 MSPS for narrow-bandwidth-only AD796x, and registers. Sampling-frequency writes claim direct mode, round CNV waveform period/duty and clk_gate burst duty/offset, store rounded waveforms, and update the exposed frequency. Buffer enable applies both waveforms; buffer disable disables both PWMs.

State and persistence behavior: runtime state is EN GPIO output mode, regulator enablement, PWM waveform settings, backend buffer ownership, selected vref, and last rounded sampling frequency. No persistent device registers are programmed; hardware mode is pin/PWM driven.

Dependencies and integration points: depends on platform devices, firmware properties, regulators `vio/vdd2/vdd1/ref/refin`, GPIO descriptors `en0` to `en3`, PWM waveform API, clock API, IIO backend, and LVDS backend documentation expectations.

Risks: valid reference modes depend on board wiring; invalid combinations are rejected but misdescribed firmware can select the wrong EN state. Sampling frequency is rounded through PWM capabilities, so requested and actual rates may differ. AD796x bandwidth mode limits maximum sample rate. Backend is mandatory; no direct raw data path exists. `ad7625_probe()` logs failure for initial sample rate setup but does not return that error before registering.

Test signals: probe each compatible with valid/invalid EN GPIO combinations; test REF, REFIN, and internal-reference cases; verify `adi,no-dco` rejection; inspect rounded PWM waveforms and exposed sample frequency; enable/disable backend buffers; test AD796x narrow versus wide bandwidth defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7625.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7766.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7766.c

Purpose: SPI IIO driver for AD7766/AD7767 sigma-delta ADC variants. It exposes one 24-bit signed voltage channel, software timestamp, scale from VREF, sample frequency from MCLK divided by part-specific decimation, and triggered-buffer capture from the data-ready IRQ.

Important APIs, types, and functions: `struct ad7766_chip_info` stores decimation factor for base, -1, and -2 variants. `struct ad7766` stores SPI, MCLK, optional powerdown GPIO, AVDD/DVDD/VREF supplies, trigger, SPI message, and DMA-aligned buffer. Main functions are `ad7766_probe()`, `ad7766_preenable()`, `ad7766_postdisable()`, `ad7766_read_raw()`, `ad7766_trigger_handler()`, and `ad7766_set_trigger_state()`.

Control flow: probe allocates IIO state, gets MCLK and three regulators, requests optional `powerdown` GPIO initially high, creates channel metadata, optionally allocates a private trigger when `spi->irq > 0`, requests the IRQ with `IRQF_NO_AUTOEN`, prepares a 3-byte RX SPI message into `data[1]` because the first byte is always zero, installs a triggered buffer with power preenable/postdisable hooks, and registers. Buffer preenable enables supplies, enables MCLK, and clears powerdown. Postdisable asserts powerdown, waits for the synchronous PD pin to be observed while the clock is still active, disables MCLK, and disables supplies. Trigger handler reads one sample and pushes it with the poll timestamp.

State and persistence behavior: runtime state is supply and clock enablement tied to buffer activity, powerdown GPIO level, trigger IRQ enablement, and reusable SPI message. No device registers or persistent configuration are managed.

Dependencies and integration points: depends on SPI, data-ready IRQ, regulator bulk API, clock API, optional GPIO, IIO trigger/triggered-buffer helpers, and direct-mode `read_raw()` for metadata only. Device IDs map AD7766/AD7767 variants to decimation factors.

Risks: no direct raw conversion is implemented, only scale and sample frequency. If no IRQ is present the device can still register but has no private trigger source. Power sequencing is buffer-scoped; consumers expecting always-on sampling must enable the buffer. The 3-byte transfer into `data[1]` relies on the channel scan layout having a zero leading byte.

Test signals: build/probe all six IDs; verify regulator and MCLK enable/disable around buffer start/stop; check IRQ enable/disable through trigger state; stream samples and confirm 24-bit big-endian alignment; validate scale using VREF and sample frequency using MCLK/decimation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7766.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7768-1.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7768-1.c

Purpose: SPI IIO driver for AD7768-1 and ADAQ7767/7768/7769 single-channel precision ADC modules. It supports direct reads, triggered buffers, optional SPI offload DMA streaming, configurable filters/oversampling/sample rate, optional PGA/AAF gain handling, optional chip GPIO controller, and optional VCM regulator output.

Important APIs, types, and functions: `struct ad7768_state` stores SPI, regmaps for 8-bit and 24-bit registers, VREF, MCLK, filter/OSR/sample-rate state, scale table, completion/trigger, sync/reset GPIOs, optional PGA GPIOs, optional GPIO chip, offload objects, labels, and PGA mutex. Key functions include `ad7768_probe()`, `ad7768_setup()`, `ad7768_configure_dig_fil()`, `ad7768_set_sinc3_dec_rate()`, `ad7768_set_freq()`, `ad7768_scan_direct()`, `ad7768_read_raw()`, `ad7768_write_raw()`, `ad7768_read_avail()`, `ad7768_trigger_handler()`, `ad7768_buffer_postenable/predisable()`, `ad7768_spi_offload_probe()`, VCM regulator ops, GPIO-chip ops, and PGA helpers.

Control flow: probe optionally requests MOSI idle high, initializes regmaps, reads VREF and MCLK, registers VCM regulator when supported, parses AAF gain, resets the ADC, configures continuous conversion and sync source, optionally exposes chip GPIOs, sets default SINC5 x32 filtering and 32 kSPS, initializes completion/mutex/PGA, reads labels, requests a disabled DRDY IRQ, then either configures SPI offload DMA or falls back to a triggered buffer. Direct reads enable the IRQ, wait for completion, disable IRQ, read the 24-bit ADC data register, and right-shift for OSR x8 16-bit precision. Buffered non-offload mode enters continuous-read mode and SPI-reads each DRDY sample; predisable exits continuous-read by reading ADC_DATA. Offload mode optimizes an RX stream transfer and uses SPI offload trigger/DMA.

State and persistence behavior: volatile device registers store conversion mode, filter, decimation, MCLK divider, GPIO state, VCM output, and continuous-read mode. Driver state caches OSR, filter type, sample frequency, available frequencies, scale table, PGA mode, AAF gain, and sync mode. Direct-mode claims protect register and GPIO operations from active buffers. PGA GPIO operations are serialized with `pga_lock`.

Dependencies and integration points: depends on SPI, regmap, regulators, MCLK, GPIO descriptor/chip APIs, optional SPI offload and DMAengine IIO buffer, IIO triggers/buffers/ext_scan_type, firmware `trigger-sources`, and DT binding trigger constants.

Risks: filter register values conflate filter type and decimation, so mapping tables must stay correct. OSR x8 changes precision and scan type, affecting scale and buffer layout. Offload and non-offload scan types have different endianness/storage. VCM regulator and GPIO-chip ops claim direct mode and can fail during active buffers. Sync source configuration has old `adi,sync-in-gpios` and newer `trigger-sources` paths. The default `ad7768_set_freq(st, 32000)` comment says 32000 kSPS but the value is 32000 SPS.

Test signals: verify ID-compatible probe for AD7768-1 and ADAQ variants; test SINC5/SINC3/wideband/SINC3+rej60 filter changes, OSR availability, sample frequency lists, and direct reads; test buffer enable/disable continuous-read exit; test SPI offload DMA with DRDY trigger; validate PGA scale writes, AAF gain firmware values, VCM regulator selectors, chip GPIO direction/value, and sync source variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7768-1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7779.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7779.c

Purpose: SPI IIO driver for AD7770, AD7771, and AD7779 eight-channel sigma-delta ADCs. It supports per-channel calibration scale/bias, sample-frequency programming, optional AD7771 filter enum, triggered SPI streaming, and optional IIO backend data capture with selectable data lanes.

Important APIs, types, and functions: `struct ad7779_state` stores SPI, chip info, MCLK, trigger/completion, sampling frequency, filter, optional backend, DMA-aligned data, SPI register buffers, and reset buffer. Main functions are `ad7779_probe()`, `ad7779_reset()`, `ad7779_conf()`, `ad7779_spi_read/write/write_mask()`, `ad7779_set_sampling_frequency()`, filter enum get/set, calibration get/set helpers, `ad7779_read_raw()`, `ad7779_write_raw()`, `ad7779_trigger_handler()`, `ad7779_setup_without_backend()`, `ad7779_setup_backend()`, `ad7779_set_data_lines()`, and PM suspend/resume.

Control flow: probe enables AVDD supplies, enables MCLK, obtains reset and mandatory start GPIOs, initializes CRC8, resets via GPIO or SPI 0xff stream, configures CRC, user mode, DCLK divider, reference mux, default sampling frequency, and start pulse. If `io-backends` is present it duplicates channel specs with CPU endianness, requests/enables the backend, sets lane count from `adi,num-lanes`, and adjusts output format/sample rate. Otherwise it creates a private trigger, requests a disabled IRQ, installs a triggered buffer, and sets DCLK divider for SPI mode. Buffer preenable enables SPI data output and the IRQ; postdisable disables IRQ and disables serial data. Trigger handler performs one SPI transfer for all eight 32-bit channel words and pushes timestamped data.

State and persistence behavior: driver caches `sampling_freq` and `filter_enabled`; device registers persist volatile calibration, SRC decimation, filter, DOUT format, CRC, power mode, and data-output enable until reset. PM suspend/resume toggles low/high power mode through a register bit.

Dependencies and integration points: depends on SPI, CRC8, GPIO reset/start lines, regulator bulk, MCLK, IIO trigger/triggered-buffer helpers, optional IIO backend, firmware `adi,num-lanes`, and standard IIO calibration/sample-frequency attributes.

Risks: `ad7779_set_sampling_frequency()` writes both integer and fractional SRC fields using `AD7779_REG_SRC_N_*` addresses; field/address mistakes affect rate accuracy. SPI register CRC has a special two-byte exception for `GEN_ERR_REG_1_EN`. `ad7779_read_raw()` checks `*val < 0` after assigning an unsigned sample frequency, which is ineffective. Backend setup changes scan endianness to CPU, so buffer consumers must match path. Calibration scale write uses `val2` as the micro gain input.

Test signals: test register CRC read/write and the special GEN_ERR register path; verify reset GPIO and SPI reset; stream all channels via IRQ path; stream via backend with 1/2/4 lanes; test AD7771 filter enum and max frequency constraints; read/write calibration registers; run suspend/resume; validate default and user sample rates.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7779.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7780.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7780.c

Purpose: SPI IIO sigma-delta driver for AD7170/AD7171 and AD7780/AD7781 ADCs. It uses the common `ad_sigma_delta` helper for conversion sequencing and exposes a single voltage channel with raw, scale, offset, and, for AD778x parts, sample-frequency/gain control through GPIO pins.

Important APIs, types, and functions: `struct ad7780_chip_info` stores channel layout, status-pattern validation bits, and whether the part is AD778x. `struct ad7780_state` stores AVDD regulator, powerdown/gain/filter GPIOs, current gain/ODR, cached vref, and embedded `struct ad_sigma_delta`. Key functions are `ad7780_probe()`, `ad7780_init_gpios()`, `ad7780_set_mode()`, `ad7780_read_raw()`, `ad7780_write_raw()`, and `ad7780_postprocess_sample()`.

Control flow: probe allocates IIO state, initializes sigma-delta helper, selects chip info, requests optional powerdown GPIO and AD778x gain/filter GPIOs, enables AVDD with devm cleanup, installs sigma-delta buffer/trigger support, and registers. The sigma-delta helper calls `ad7780_set_mode()` to drive powerdown for single/continuous versus idle modes, and `ad7780_postprocess_sample()` to reject error/pattern failures and update gain/ODR bits from raw sample status. Raw reads call `ad_sigma_delta_single_conversion()`. Scale reads query AVDD, update cached `int_vref_mv`, and return fractional log2 scale using current gain. Writes choose nearest gain/filter GPIO state using midpoint thresholds.

State and persistence behavior: state is GPIO-controlled power mode, gain, filter/ODR, cached VREF, and sigma-delta helper state. AD778x status bits update cached state after samples. No hardware registers are programmed because these parts are pin/status controlled in this driver.

Dependencies and integration points: depends on SPI, IRQ through sigma-delta helper, AVDD regulator, optional GPIO descriptors, IIO sysfs, and `IIO_AD_SIGMA_DELTA` namespace. Channel specs encode different realbits/word sizes and status pattern expectations.

Risks: scale writes depend on a prior scale read to populate `int_vref_mv`; otherwise cached VREF may be zero. `ad7780_write_raw()` returns success for unsupported masks after falling through the default case, so invalid writes for AD778x may silently no-op. Pattern/status validation must match bit layouts for AD717x versus AD778x. Optional gain/filter GPIOs default high when present.

Test signals: probe all four IDs; perform single conversions and check pattern/error rejection; test gain and sampling-frequency writes with GPIO observation; verify scale before and after VREF changes; test missing/optional GPIO paths; test sigma-delta buffer setup and IRQ conversions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7780.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7791.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7791.c

Purpose: SPI IIO sigma-delta driver for AD7787/AD7788/AD7789/AD7790/AD7791 ADCs. It exposes differential, single-ended, shorted, and supply-monitor channel layouts depending on part, with raw conversions, scale, offset, and optional sample-frequency programming.

Important APIs, types, and functions: `struct ad7791_chip_info` maps a part to channel specs and feature flags for filter, buffer, unipolar, and burnout support. `struct ad7791_state` embeds `ad_sigma_delta`, mode/filter registers, VREF regulator, and chip info. Key functions are `ad7791_probe()`, `ad7791_setup()`, `ad7791_set_channel()`, `ad7791_set_mode()`, `ad7791_read_raw()`, `ad7791_write_raw()`, and `__ad7791_write_raw()`.

Control flow: probe requires an IRQ, enables `refin`, initializes sigma-delta helper, selects IIO info based on filter support, sets up sigma-delta buffer/trigger, writes initial mode from platform data, and registers. Channel selection updates the sigma-delta communications register. Mode changes update the MODE register for continuous, single, idle, or powerdown. Raw reads delegate to `ad_sigma_delta_single_conversion()`. Scale uses the external VREF except for the AVDD monitor channel, which uses an internal 1.17 V reference multiplied by attenuation. Sample-frequency writes require direct mode, match one of eight fixed rates, update filter bits, and write the FILTER register.

State and persistence behavior: cached `mode` and `filter` mirror device registers for unipolar/buffer/burnout/rate configuration. VREF regulator remains enabled for device lifetime through devm cleanup. Platform data is consumed at probe only.

Dependencies and integration points: depends on SPI IRQs, `ad_sigma_delta`, `refin` regulator, platform data from `linux/platform_data/ad7791.h`, IIO triggered buffer support, and sample-frequency sysfs attributes.

Risks: this legacy driver depends on platform data and has no OF property parsing. `ad7791_no_filter_info` still exposes `write_raw`, so sample-frequency writes can be attempted even when the attribute group is absent. Platform data options are applied only if the chip flags support them. The channel macro prefix says AD7991, but it is local naming only.

Test signals: probe each ID with valid IRQ and platform data; verify buffer/unipolar/burnout effects on mode register; test raw conversions on each channel address; test scale/offset for bipolar and unipolar modes; test sample-frequency writes for filter-capable and non-filter parts; validate regulator cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7791.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7793.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7793.c

Purpose: SPI IIO sigma-delta driver for AD7785 and AD7792 through AD7799 precision ADCs. It supports multiple differential inputs, shorted calibration channels, temperature/supply monitor channels on some parts, scale/gain selection, sample-frequency selection, platform-configured references/bias/current sources, and internal calibration.

Important APIs, types, and functions: `struct ad7793_chip_info` maps device ID, channel table, feature flags, IIO info, and frequency table. `struct ad7793_state` stores chip info, cached MODE/CONF registers, computed `scale_avail`, and embedded `ad_sigma_delta`. Key functions are `ad7793_probe()`, `ad7793_setup()`, `ad7793_check_platform_data()`, `ad7793_set_channel()`, `ad7793_set_mode()`, `ad7793_calibrate_all()`, `ad7793_read_raw()`, `ad7793_write_raw()`, and `ad7793_read_avail()`.

Control flow: probe requires platform data and IRQ, initializes sigma-delta helper, selects internal or external VREF regulator, sets IIO metadata, sets up sigma-delta buffer/trigger, then runs setup. Setup validates platform data against chip feature flags, resets the serial interface, reads and verifies the ID register, constructs mode/config registers from platform settings, enters idle, selects channel 0, optionally programs excitation current routing, runs internal zero/full calibration across three channels, computes available scale values for gain settings, and registers. Raw reads use sigma-delta single conversion. Scale writes select a matching gain index, write CONF, and recalibrate. Sample-frequency writes update MODE rate bits.

State and persistence behavior: MODE and CONF are cached in memory and mirrored to device registers. Scale table is computed at probe from VREF, resolution, polarity, and gain. Calibration registers are updated by device calibration commands but not persisted across reset. Regulator enablement is devm-managed when external reference is used.

Dependencies and integration points: depends on SPI, IRQ, `ad_sigma_delta`, platform data from `linux/platform_data/ad7793.h`, optional `refin` regulator, IIO sysfs attributes, and per-device channel tables.

Risks: no platform data means probe failure, limiting firmware-based systems. ID checking uses a 4-bit ID that aliases AD7794/AD7795, so table correctness matters. Scale write matches only fractional nanounits and ignores `val`, which may reject equivalent representations. Gain changes trigger recalibration, which can be slow/fail. The macro `AD7793_REG_FULLSALE` appears misspelled but is not used.

Test signals: probe each supported ID with valid/invalid platform data; verify ID mismatch failure; test raw conversion on voltage/temp/supply channels; test scale availability and gain writes with recalibration; test sample-frequency tables including AD7797 restrictions; test internal versus external VREF; test excitation-current validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7793.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7887.c -->
## sources/distributed-fs/ceph-client/drivers/iio/adc/ad7887.c

Purpose: SPI IIO driver for AD7887, a 12-bit ADC with optional single- or dual-channel operation. It supports direct raw reads, triggered-buffer sampling, internal or external reference scaling, and platform-data selection of dual mode.

Important APIs, types, and functions: `struct ad7887_chip_info` stores internal VREF, single-channel specs, and dual-channel specs. `struct ad7887_state` stores SPI, optional VREF regulator, prepared SPI transfers/messages for CH0, CH1, and dual CH0+CH1 reads, selected ring message, command buffer, and DMA-aligned scan buffer. Key functions are `ad7887_probe()`, `ad7887_read_raw()`, `ad7887_scan_direct()`, `ad7887_ring_preenable()`, `ad7887_ring_postdisable()`, and `ad7887_trigger_handler()`.

Control flow: probe optionally enables external `vref`, selects chip info, builds command mode bits for standby, internal-reference disable, and optional dual mode, prepares SPI messages for CH0 and, in dual mode, CH1 and CH0+CH1 sequences, installs a triggered buffer, and registers. Direct raw reads claim direct mode, run the channel-specific SPI message, extract the big-endian 12-bit sample, and return it. Buffer preenable selects the SPI message based on active scan mask; CH1-only mode performs a dummy read to push the channel selection into hardware. Buffer postdisable performs a dummy CH0 read to restore default settings. Trigger handler executes the selected ring message and pushes timestamped data.

State and persistence behavior: runtime state is external regulator enablement, command bytes, prepared SPI messages, active ring message, and device channel-selection pipeline state. No persistent registers are stored; channel selection is driven by conversion command side effects.

Dependencies and integration points: depends on SPI, optional VREF regulator, legacy `ad7887_platform_data` for dual-channel enable, IIO direct mode, and IIO triggered buffer helpers.

Risks: active scan mask handling assumes the mask fits in one unsigned long and only covers CH0/CH1 combinations. CH1 command sequencing requires dummy transfers because channel selection takes effect in the following conversion. External-reference absence sets `AD7887_REF_DIS`, so board reference wiring must match firmware/platform data. There is no OF dual-mode property parsing in this driver.

Test signals: probe with and without external VREF; probe with platform dual mode enabled/disabled; direct-read both channels; enable buffers with CH0-only, CH1-only, and CH0+CH1 scan masks; verify dummy read restoration; validate scale from regulator and internal 2.5 V reference.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/adc/ad7887.c -->
