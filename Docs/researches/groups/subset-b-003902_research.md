# subset-b-003902 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/d3323aa.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/d3323aa.c

Purpose: platform IIO driver for the Nicera D3-323-AA PIR proximity sensor. It exposes one `IIO_PROXIMITY` channel with high-pass and low-pass 3 dB filter frequency controls, hardware gain, and rising/falling threshold events. The device is configured through two GPIOs with bit-banged clock/data timing and powered by an exclusive `vdd` regulator.

Important APIs, types, and functions: `struct d3323aa_data` stores GPIOs, regulator, reset completion, configuration lock, cached filter/gain/threshold state, reset IRQ count, and detecting/configuring mode. `d3323aa_reset()` power-cycles the regulator and waits for two falling edges on `vout-clk`. `d3323aa_write_settings()` and `d3323aa_read_settings()` serialize/verify the device bitmap. `d3323aa_setup()` is the central reconfiguration path. IIO callbacks are `d3323aa_read_raw()`, `d3323aa_write_raw()`, `d3323aa_read_event()`, `d3323aa_write_event()`, and `d3323aa_read_avail()`.

Control flow: probe allocates an IIO device, initializes the mutex/completion, obtains `vdd`, `vout-clk`, and `data`, requests an edge IRQ on `vout-clk`, runs default setup, then registers the IIO device. Setup resets the sensor, writes the full bitmap including threshold, filter type, gain, and end pattern, reads it back, validates against a 1400 ms configuration window, switches GPIOs back to inputs, and marks the device detecting. The IRQ handler counts reset edges while configuring, then pushes threshold events with direction derived from the GPIO level.

State and persistence: the sensor has no normal register bus; all persistent hardware configuration is rewritten as a full bitmap on every setting change. The driver caches `lp_filter_freq_idx`, `filter_gain_idx`, and `detect_thresh` because any one sysfs write requires rewriting the whole configuration. `statevar_lock` serializes read/write/event paths and protects the cached state through the reset/reconfigure sequence. A devm cleanup disables `vdd` only if it is currently enabled.

Dependencies and integration points: integrates with platform/OF matching (`nicera,d3323aa`), GPIO descriptor APIs, regulator framework, IRQ handling, and IIO events. It depends on precise GPIO timing (`udelay(500)` for 1 kHz clock) and a working interrupt line on `vout-clk` for reset completion and runtime events.

Risks and test signals: test reset timing, interrupt edge counting, bitmap readback mismatch, all exposed filter/gain availability values, threshold bounds, interrupted waits, and regulator disable/enable balance. Risk areas are timing-sensitive bit banging, a full sensor reset on every sysfs write, ambiguous high-pass settings for filter types B/C, and event direction correctness when GPIO polarity changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/d3323aa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/hx9023s.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/hx9023s.c

Purpose: I2C regmap IIO driver for the TYHX HX9023S five-channel capacitive proximity/SAR sensor. It provides direct raw proximity reads, shared sample-frequency control, threshold events with per-channel near/far thresholds and debounce periods, and triggered-buffer capture when an IRQ-backed trigger is present.

Important APIs, types, and functions: `struct hx9023s_data` owns regmap, optional trigger, channel/event/read bitmaps, prox status cache, trigger flag, scan buffer, mutex, and `struct hx9023s_ch_data` for each channel. Key functions are `hx9023s_property_get()`, `hx9023s_ch_cfg()`, `hx9023s_sample()`, `hx9023s_update_chan_en()`, `hx9023s_get_proximity()`, event value/config callbacks, `hx9023s_trigger_handler()`, buffer preenable/postdisable callbacks, `hx9023s_cfg_update()`, and `hx9023s_probe()`.

Control flow: probe initializes regmap, parses child-node channel wiring from `single-channel` or `diff-channels`, enables `vdd`, checks device ID, programs channel mux registers, starts asynchronous firmware loading (`hx9023s.bin` or `firmware-name`), optionally registers a threaded IRQ and IIO trigger, sets up a triggered buffer, then registers the device. Firmware callback loads register/value pairs from the binary or falls back to `hx9023s_reg_init_list`, then syncs regcache. Direct reads claim direct mode, sample data under data lock, refresh proximity status, and return channel diff. IRQ top half polls the trigger if enabled and wakes the thread; the thread samples and pushes events for status bit transitions.

State and persistence: channel wiring, enable state, last proximity status, threshold caches, and selected data mux modes are held in `hx9023s_data`. Hardware state persists in HX9023S configuration registers, including channel enable, thresholds, debounce, sample period, data-lock, and raw/LP/diff selection. `mutex` serializes register groups used by event and buffer flows, while `hx9023s_data_lock()` freezes sensor data during multi-register sampling.

Dependencies and integration points: depends on I2C regmap with register access tables, regulator `vdd`, firmware loader, firmware child nodes, IIO events, IIO triggers, triggered buffers, and optional PM suspend/resume. Device matching uses `tyhx,hx9023s` OF and `hx9023s` I2C ID.

Risks and test signals: test with and without firmware file, invalid child channel indexes, single-ended versus differential channel properties, channel enable transitions when events and buffers overlap, sample-frequency conversion, per-channel threshold quantization in multiples of 32, IRQ and no-IRQ modes, and suspend/resume interrupt masking. Risk areas include async firmware configuration racing early userspace access, unvalidated channel pin numbers before indexing `conn_cs`, and event direction mapping from prox status bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/hx9023s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c

Purpose: I2C regmap IIO driver for the Murata IRS-D200 PIR proximity sensor. It exposes signed raw PIR data, sample frequency, low/high-pass filter controls, threshold events with running period/count controls, and an IRQ-backed triggered buffer for data-ready sampling.

Important APIs, types, and functions: `struct irsd200_data` stores the regmap, register fields, and device pointer. `irsd200_setup()` disables interrupts, sets active mode, clears count/status, and prepares the device. `irsd200_read_data()`, data-rate/filter/timer/count helpers, threshold helpers, `irsd200_irq_thread()`, `irsd200_trigger_handler()`, and `irsd200_set_trigger_state()` implement the IIO ABI.

Control flow: probe initializes regmap and six regmap fields, enables `vdd`, calls setup, requires a client IRQ, sets up a triggered buffer, requests a rising threaded IRQ, registers an IIO trigger, and then registers the device. Raw reads bulk-read two data bytes. Buffer enable via trigger ops toggles the data interrupt bit; IRQ thread polls the trigger for data interrupts and pushes threshold events for OR count threshold status, deriving rising/falling/either from upper/lower count fields before clearing status.

State and persistence: most state lives in device registers; the driver does not keep a mutex or software cache beyond regfield handles. Thresholds are quantized by 128, falling thresholds are represented as negative values, data rate writes sleep for 3 seconds to honor settling guidance, and count/timer constraints are enforced before writing `IRS_REG_NR_COUNT`.

Dependencies and integration points: depends on I2C regmap, regmap fields, `vdd` regulator, a mandatory IRQ, IIO events, IIO triggers, and triggered buffers. OF compatible is `murata,irsd200`.

Risks and test signals: test required IRQ failure, data interrupt buffering, threshold OR and AND-like event behavior, status clearing, data-rate settling, timer quantization, and count write rejection when timer is zero. A code risk is `irsd200_write_hp_filter()` comparing the truncated fractional digit to `irsd200_hp_filter_freq[idx][0]`, which works for 0.3/0.5 but is easy to break if the table changes. Lack of explicit locking also makes concurrent sysfs writes worth stressing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/irsd200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/isl29501.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/isl29501.c

Purpose: I2C SMBus IIO driver for the Renesas/Intersil ISL29501 time-of-flight sensor. It exposes distance, phase, output current, temperature, and ambient-light channels, plus integration time, sample frequency, calibration bias, emitter current scale, custom AGC/correction-coefficient ext_info files, and a triggered buffer for distance samples.

Important APIs, types, and functions: `struct isl29501_private` stores the I2C client, mutex, and RAM shadow of four correction coefficients. `isl29501_register_read()` and `isl29501_register_write()` abstract one- and two-byte registers. `isl29501_read_ext()`/`write_ext()` implement AGC gain/bias and phase correction ABI. `isl29501_get_raw()`, scale, bias, integration-time, sample-frequency, and write helpers back `isl29501_read_raw()` and `isl29501_write_raw()`. `isl29501_init_chip()` validates ID, resets registers/state machine, and starts acquisition.

Control flow: probe allocates the IIO device, records the client, initializes the mutex, resets and starts the chip, installs channel metadata and `isl29501_info`, sets up a triggered buffer, then registers. Reads dispatch by channel type to the register descriptor table. Writes update emitter DAC, integration period, sample period, current driver range, distance bias, or temperature bias. Triggered capture reads the distance register if enabled and pushes a timestamped scan.

State and persistence: hardware registers hold sampling, range, bias, calibration, and output data. Software shadows exact correction coefficients because the chip stores them as shared exponent plus 8-bit mantissas; writing one coefficient recomputes a common exponent and rewrites all nonzero mantissas. The mutex serializes SMBus register pairs but does not prevent users from reading while acquisition is being refreshed by hardware.

Dependencies and integration points: depends on I2C SMBus byte data operations, IIO sysfs/ext_info, IIO triggered buffers, and OF/I2C matching (`renesas,isl29501`, `isl29501`). It does not use regmap or runtime PM.

Risks and test signals: test chip ID mismatch, reset/acquisition commands, current scale range zero versus 1..15, integration-time exact matching, sample-frequency conversion bounds, correction coefficient exponent recomputation, and buffer capture. Risks include no direct-mode claim around raw reads, correction shadows being lost on driver reload, possible typo in the chip-ID error message expected value, and ignoring return from `isl29501_register_read()` inside trigger handler.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/isl29501.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/mb1232.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/mb1232.c

Purpose: I2C IIO driver for MaxBotix I2CXL-MaxSonar ultrasonic rangers, tested around the MB1232 family. It exposes one `IIO_DISTANCE` channel with raw range and centimeter scale, plus triggered-buffer capture.

Important APIs, types, and functions: `struct mb1232_data` stores the I2C client, mutex, optional completion/IRQ for ranging-done notification, and IRQ number. `mb1232_read_distance()` starts a range conversion, waits via optional IRQ completion or a 15 ms sleep, reads a big-endian 16-bit distance, and rejects negative signed results. `mb1232_trigger_handler()` and `mb1232_read_raw()` feed buffer and direct sysfs paths.

Control flow: probe checks SMBus read/write byte support, allocates/registers the IIO device, initializes the lock/completion, optionally obtains firmware IRQ 0 and requests a falling-edge IRQ, sets up a triggered buffer, then registers. Direct and triggered reads both call the same locked measurement sequence.

State and persistence: no persistent device configuration is cached; each read sends command `0x51` and receives the latest range. Optional IRQ state is only used as a completion source. The mutex ensures only one ranging cycle is active at a time.

Dependencies and integration points: depends on I2C/SMBus plus `i2c_master_recv`, optional firmware IRQ, IIO direct mode, and IIO triggered buffers. OF/I2C tables cover several MaxBotix compatibles and IDs.

Risks and test signals: test adapters with required SMBus functionality, no-IRQ sleep fallback, IRQ timeout, short or failed I2C receives, big-endian decoding, negative signed distance rejection, and buffer reads. Risk areas are accepting partial positive `i2c_master_recv()` byte counts as data, fixed 15 ms no-IRQ delay for all models, and treating high unsigned distances as negative because the local return type is `s16`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/mb1232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c

Purpose: platform IIO driver for Parallax PING and LaserPING single-GPIO ultrasonic/laser distance sensors. It exposes one direct-mode `IIO_DISTANCE` channel with raw millimeter distance and scale.

Important APIs, types, and functions: `struct ping_cfg` describes trigger pulse length, LaserPING error-code support, and timeout. `struct ping_data` stores the shared GPIO, mutex, timestamps, completions, IRQ number, and matched config. `ping_read()` drives the trigger pulse, switches the GPIO to input, dynamically requests both-edge IRQs, waits for rising/falling echo edges, computes pulse duration, filters timeout/error-code windows, and converts to millimeters. `ping_read_raw()` exposes raw and scale.

Control flow: probe selects match data, gets the `ping` GPIO as output-low, rejects sleepable GPIOs, and registers a direct-mode IIO device. Each read holds the mutex, toggles the output pulse, converts the GPIO to input, requests an IRQ for the measurement, waits for completions, frees the IRQ, restores output-low, and returns computed distance.

State and persistence: measurement state is transient timestamps and completions. There is no hardware register persistence. The mutex is essential because GPIO direction and the one-shot IRQ are shared mutable state.

Dependencies and integration points: depends on platform/OF matching (`parallax,ping`, `parallax,laserping`), non-sleeping GPIO descriptors, dynamic IRQ allocation, completions, and IIO direct sysfs.

Risks and test signals: test GPIO direction transitions, IRQ request/free on all error paths, rising/falling timeout behavior, LaserPING error pulse windows, out-of-range filtering, and repeated concurrent reads. Risks are per-read IRQ setup overhead, no temperature compensation, use of `gpiod_get_value()` in IRQ context, and rejecting sleepable GPIO controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/ping.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c

Purpose: I2C IIO driver for PulsedLight/ Garmin LIDAR-Lite v2/v3 distance sensors. It exposes one `IIO_DISTANCE` channel with raw centimeter counts and scale, supports triggered-buffer capture, and uses runtime PM to power the sensor down between measurements.

Important APIs, types, and functions: `struct lidar_data` holds the client, IIO device, selected transfer function, and I2C-vs-SMBus mode. `lidar_i2c_xfer()` uses a two-message I2C transfer with STOP after address write; `lidar_smbus_xfer()` emulates the device's required STOP behavior byte by byte. `lidar_get_measurement()` resumes runtime PM, starts acquisition, polls status, handles invalid/out-of-range status, reads the big-endian result, and autosuspends. `lidar_read_raw()` and `lidar_trigger_handler()` expose direct and buffered reads.

Control flow: probe selects raw I2C transfer when available or SMBus fallback otherwise, sets up the triggered buffer manually, registers the IIO device, initializes runtime PM as active, enables autosuspend, and idles the device. Removal unregisters IIO/buffer and disables runtime PM. Runtime suspend writes power control `0x0f`; resume writes `0` and waits 15-20 ms for settling.

State and persistence: software state is minimal: bus-transfer mode and runtime PM state. The sensor is explicitly acquired for each sample and may be powered down afterward. No calibration state is cached.

Dependencies and integration points: depends on I2C or SMBus byte operations, IIO direct mode, triggered buffers, and runtime PM. It matches `pulsedlight,lidar-lite-v2`, `grmn,lidar-lite-v3`, and I2C IDs.

Risks and test signals: test raw I2C and SMBus fallback, runtime suspend/resume timing, invalid status handling, status polling timeout, buffer cleanup on probe error, and direct read while buffers are active. Risks include no explicit mutex around measurements, fixed 10-poll acquisition window, and manual non-devm buffer/device registration requiring correct remove/error cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/pulsedlight-lidar-lite-v2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/rfd77402.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/rfd77402.c

Purpose: I2C SMBus IIO driver for the RF Digital RFD77402 time-of-flight distance sensor. It exposes one direct-mode `IIO_DISTANCE` channel with raw millimeter counts and scale, and supports either interrupt-driven or polling measurement completion.

Important APIs, types, and functions: `struct rfd77402_data` stores client, mutex, completion, and `irq_en`. `rfd77402_set_state()` sends command/state requests and validates power-mode status. `rfd77402_init()` configures IRQ mode, I2C debug/increment behavior, PMU setup, MCPU states, and datasheet magic ToF registers. `rfd77402_measure()` turns MCPU on, starts a single measure, waits for result, reads/validates result bits, and returns distance. PM callbacks call `rfd77402_powerdown()`/`rfd77402_init()`.

Control flow: probe reads and validates module chip ID (`0xad01` or `0xad02`), allocates IIO state, initializes mutex/completion, requests a threaded IRQ if provided, fills IIO metadata, initializes the device, registers a devm powerdown action, and registers IIO. Direct raw reads lock, run one measurement, and return the distance. The IRQ handler reads ICSR, checks `RESULT`, and completes the pending measurement.

State and persistence: hardware initialization persists in command/config/PMU registers until suspend or reset. The mutex serializes single-measure state transitions. On measurement error, the driver attempts to return the MCPU to off state; successful measurements leave state as dictated by the measurement path until later init/powerdown.

Dependencies and integration points: depends on I2C SMBus word/byte operations, optional IRQ, completions, `read_poll_timeout`, PM sleep callbacks, and IIO direct mode. Matching uses `rfdigital,rfd77402` and `rfd77402`.

Risks and test signals: test both IRQ and polling modes, chip ID rejection, state transition status mismatches, result error/valid bits, timeout handling, suspend/resume reinitialization, and cleanup powerdown. Risk areas are SMBus word endianness expectations, a polling timeout expression tied to ICSR reads, and lack of triggered-buffer support despite optional IRQ.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/rfd77402.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c

Purpose: platform IIO driver for SRF04-style two-GPIO ultrasonic distance sensors and MaxBotix MB1000-series LV devices. It exposes one direct-mode `IIO_DISTANCE` channel with raw millimeter distance and scale, with optional power GPIO managed by runtime PM.

Important APIs, types, and functions: `struct srf04_data` stores trigger/echo/power GPIOs, mutex, IRQ, edge timestamps, completions, chip config, and startup delay. `srf04_read()` optionally resumes power, emits the trigger pulse, waits for echo rising/falling IRQ completions, converts pulse width to millimeters, and filters impossible long ranges. Runtime PM callbacks drive the optional power GPIO.

Control flow: probe gets trigger output and echo input GPIOs, optional power GPIO and `startup-time-ms`, rejects sleepable echo GPIOs, converts echo to IRQ, requests both-edge IRQ, registers a direct-mode IIO device, and enables runtime PM if power is present. Each read resumes power if needed, locks, sends the trigger pulse, schedules autosuspend, waits for echo edges, computes distance, and unlocks.

State and persistence: persistent state is GPIO handles, optional power startup delay, and timestamps/completions for the latest measurement. There is no hardware register state. The mutex prevents overlapping trigger/echo cycles.

Dependencies and integration points: depends on platform/OF matching, GPIO descriptors, IRQs, completions, runtime PM, and IIO direct mode. Compatibles include `devantech,srf04` and MaxBotix `mb1000` through `mb1040`.

Risks and test signals: test with and without power GPIO, startup-time override, echo IRQ timeouts, long-range rejection, IRQ polarity, and remove-time runtime PM cleanup. Risks include autosuspending shortly after trigger while echo is still being measured, no temperature compensation, and inability to work with sleepable GPIO controllers for echo.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf04.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c

Purpose: I2C IIO driver for Devantech SRF02/SRF08/SRF10 ultrasonic rangers. It exposes one distance channel, triggered-buffer capture, and for SRF08/SRF10 adds custom sysfs attributes for maximum range and sensitivity.

Important APIs, types, and functions: `struct srf08_chip_info` provides sensitivity tables/defaults and range default. `struct srf08_data` stores client, sensitivity, range in mm, mutex, sensor type, and chip info. `srf08_read_ranging()` sends the ranging command, waits based on configured range, polls software revision until ready, then reads the first echo. `srf08_write_range_mm()` and `srf08_write_sensitivity()` program custom attributes. `srf08_trigger_handler()` and `srf08_read_raw()` expose buffer/direct reads.

Control flow: probe checks SMBus byte/word functionality, selects chip info by I2C ID driver data, initializes the IIO device, sets up triggered buffer, writes default range/sensitivity when supported, and registers. Direct and buffered reads run the same locked ranging command and centimeter-scale result path. SRF02 omits range/sensitivity attributes by using a smaller `iio_info`.

State and persistence: `range_mm` and `sensitivity` are driver caches because the hardware registers cannot be read back. These values also influence wait time before readiness polling. Hardware keeps range/gain settings after writes.

Dependencies and integration points: depends on I2C SMBus byte data, word reads, IIO direct mode, triggered buffers, and OF/I2C matching for SRF02/SRF08/SRF10.

Risks and test signals: test all three sensor types, default write failures, range parsing in 43 mm increments, sensitivity table validation, readiness polling failure, word-swapped echo decoding, and buffer direct interaction. Risks include no explicit direct-mode claim, buffer handler locking again only around push after `srf08_read_ranging()` already locked/unlocked, and fixed readiness polling assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/srf08.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9310.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9310.c

Purpose: I2C regmap IIO driver for Semtech SX9310/SX9311 capacitive proximity sensors. It exposes four proximity channels (CS0, CS1, CS2, combined), hardware gain, sample frequency, threshold/hysteresis/debounce events, and shared triggered/event infrastructure through `sx_common`.

Important APIs, types, and functions: this file supplies chip-specific registers, regmap access tables, channels, default register table, and `struct sx_common_chip_info`. Key functions are `sx9310_read_prox_data()`, `sx9310_wait_for_sample()`, gain/sample-frequency/event helpers, `sx9310_init_compensation()`, `sx9310_get_default_reg()`, `sx9310_check_whoami()`, PM suspend/resume, and `sx9310_probe()` which delegates to `sx_common_probe()`.

Control flow: `sx_common_probe()` handles common allocation, reset/default programming, IRQ/buffer/event setup, and IIO registration using callbacks from this file. Raw reads claim direct mode and call `sx_common_read_proximity()`, which uses this driver's sensor-select plus bulk-read operation. Event writes update threshold/hysteresis/debounce fields under the common mutex. Initial compensation temporarily enables all sensor channels, polls compensation status clear, then restores control. Suspend disables IRQ, saves channel-enable register, disables sensors and pauses; resume unpauses and restores saved control.

State and persistence: common state lives in `struct sx_common_data`; this file stores chip defaults and per-property transformations. Hardware persistence is in SX9310 registers for scan period, channel enables, gains, thresholds, debounce, SAR settings, and combined-channel configuration. Firmware properties such as `semtech,cs0-ground`, `semtech,combined-sensors`, `semtech,resolution`, `semtech,startup-sensor`, `semtech,proxraw-strength`, and `semtech,avg-pos-strength` alter default register programming.

Dependencies and integration points: depends on I2C regmap, firmware/ACPI/OF matching, `sx_common` exported namespace (`MODULE_IMPORT_NS("SEMTECH_PROX")`), IIO direct mode, IIO events, and PM sleep. Matching distinguishes SX9310 and SX9311 by WHOAMI and match data.

Risks and test signals: test WHOAMI rejection, all firmware default-property conversions, combined sensor modes, compensation timeout, event threshold code table, gain writes for channel groups, no-IRQ wait-for-sample path, and suspend/resume IRQ state. Risks include `ilog2()` on unvalidated property values, threshold register sharing between channel groups, and common-driver assumptions about IRQ availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9310.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9324.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9324.c

Purpose: I2C regmap IIO driver for the Semtech SX9324 four-phase capacitive proximity sensor. It exposes four proximity phases, sample frequency, hardware gain, threshold/hysteresis/debounce events, and a per-channel `setup` ext_info view of CS pin usage.

Important APIs, types, and functions: chip-specific data is packaged into `sx9324_chip_info` for `sx_common_probe()`. Important functions include `sx9324_phase_configuration_show()`, `sx9324_read_prox_data()`, `sx9324_wait_for_sample()`, raw/gain/sample/event callbacks, `sx9324_init_compensation()`, `sx9324_parse_phase_prop()`, `sx_common_get_raw_register_config()` for ACPI overrides, `sx9324_get_default_reg()`, and PM suspend/resume.

Control flow: probe delegates to `sx_common_probe()` with SX9324 regmap config and chip info. The common layer programs defaults, applies per-index default callbacks, initializes compensation by setting `COMPSTAT`, and registers IIO. Raw reads select `SX9324_REG_PHASE_SEL` then bulk-read the requested data register. Event threshold/hysteresis/debounce operations update proximity control registers, with threshold encoded as an approximate square-law register value. Suspend disables IRQ, saves enabled phases from `GNRL_CTRL1`, then writes zero; resume restores phases plus pause control and reenables IRQ.

State and persistence: `sx_common_data` holds runtime common state; this file defines hardware defaults and how firmware/ACPI properties mutate them. Hardware state includes phase pin configuration, AFE controls, analog gain, scan period, phase enable, proximity thresholds, advanced controls, offsets, and compensation status. Driver-cached suspend control preserves phase enable bits.

Dependencies and integration points: depends on I2C regmap, ACPI/OF properties, `sx_common`, IIO events/direct mode, and PM sleep. Properties include phase pin arrays (`semtech,ph0-pin` etc.), `semtech,cs-idle-sleep`, `semtech,int-comp-resistor`, resolution properties, precharge resistor, analog gain, startup sensor, average strength, proxraw strength, and ACPI raw register overrides named with HID plus register property.

Risks and test signals: test phase setup display, ACPI raw override naming, firmware property bounds, compensation timeout, event threshold round-trip, gain encoding, sample-frequency table, no-IRQ sample wait, and suspend/resume. Risks include duplicate macro definition for `RINT_LOWEST`, possible out-of-range phase pin values being masked silently, TODOs around threshold type and SAR support, and property `ilog2()` conversions without zero checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9324.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9360.c -->
# sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9360.c

Purpose: I2C regmap IIO driver for the Semtech SX9360 two-channel capacitive proximity sensor. It exposes reference and main proximity channels, labels, hardware gain, sample-frequency range, and threshold/hysteresis/debounce events on the main channel through `sx_common`.

Important APIs, types, and functions: the file defines SX9360 register maps, channels, defaults, and `sx9360_chip_info`. Key functions are `sx9360_read_prox_data()`, `sx9360_wait_for_sample()`, `sx9360_read_gain()`, `sx9360_read_samp_freq()`, `sx9360_set_samp_freq()`, event value/write helpers, `sx9360_read_label()`, `sx9360_init_compensation()`, `sx9360_get_default_reg()`, `sx9360_check_whoami()`, and PM suspend/resume.

Control flow: probe calls `sx_common_probe()`. Direct raw/gain reads claim direct mode and use common proximity read plus chip-specific register access. Sample frequency is stored as a big-endian two-byte divisor across `GNRL_CTRL1/2`, converted from/to oscillator frequency math. Compensation sets status bits and polls them clear. Suspend disables IRQ, saves phase-enable bits, and writes zero to disable phases; resume restores those bits and reenables IRQ.

State and persistence: runtime state is common `sx_common_data` plus suspend control. Hardware persists scan divisor, phase enables, AFE settings, gain/filter settings, threshold/debounce, reference correction, offsets, and data registers. Default register generation accepts properties for input precharge resistor, resolution, proxraw strength, and average positive strength.

Dependencies and integration points: depends on I2C regmap, `sx_common`, ACPI/OF/I2C match data (`STH9360`, `SAMM0208`, `semtech,sx9360`), IIO direct/event paths, and PM sleep. It imports the `SEMTECH_PROX` namespace.

Risks and test signals: test label output, sample-frequency range math and divisor zero handling, gain writes, event threshold square-root encoding, compensation timeout, firmware-property conversion, no-IRQ wait path, and suspend/resume with IRQ disabled. Risks include `sx9360_set_samp_freq()` arithmetic precision/overflow for extreme values, no explicit validation that hardware gain is one of the advertised powers of two before `ilog2()`, and event specs only on channel 1 while shared common state manages two channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/proximity/sx9360.c -->
