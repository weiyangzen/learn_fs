# subset-b-003833 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7802.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct7802.c

Purpose: I2C hwmon driver for the Nuvoton NCT7802Y. It exposes local, RTD, PECI, voltage, fan tachometer, PWM, SmartFan curve, alarm, and beep controls through classic hwmon sysfs attributes.

Important APIs/types/functions: `struct nct7802_data` owns the regmap, multi-byte access lock, and voltage alarm cache. Key paths are `nct7802_read_temp()`, `nct7802_read_fan()`, `nct7802_read_voltage()`, write helpers for limits and PWM, visibility callbacks for temp/in/fan groups, `nct7802_detect()`, `nct7802_configure_channels()`, `nct7802_init_chip()`, and `nct7802_probe()`.

Control flow: probe allocates state, initializes I2C regmap with a maple cache, enables ADC and VCC/Vcore monitoring, applies optional device-tree channel mode configuration, then registers grouped hwmon attributes. Reads convert packed register formats into millidegrees, millivolts, and RPM. Writes clamp user values, convert to register units, and update split LSB/MSB fields under `access_lock`.

State and persistence: persistent state is mostly hardware registers; software keeps only mutexes and `in_status`, a validity/status cache for voltage alarms because the voltage SMI status register is clear-on-read and directionless. Regmap caches nonvolatile registers while early status and PWM registers are volatile.

Dependencies and integration: depends on I2C, regmap, hwmon sysfs helpers, OF child nodes named `channel`, and NCT7802 register layout. It probes common hwmon I2C addresses and publishes a hwmon device named from the I2C client.

Risks: bank 0 is assumed for detection; visibility depends on live mode registers; voltage alarm synthesis can lag until the next clear-on-read status change; multi-register updates are not atomic to hardware; RTD3 only supports thermistor mode; PWM channel 0 read-only auto-point value is represented by synthetic `255`.

Test signals: successful detection at 0x28-0x2f, sysfs visibility matching `REG_MODE`/PECI/fan enable bits, voltage alarm cache behavior across threshold crossings, limit round-trip conversions, fan stopped/no-limit cases, and OF channel configuration for voltage, thermistor, thermal-diode, and disabled local sensor modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7802.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7904.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nct7904.c

Purpose: I2C hwmon and watchdog driver for the Nuvoton NCT7904D. It supports up to 20 voltage inputs, 12 fans, 4 PWM outputs, local/external/DTS temperature sources, alarms, limits, and a minute-granularity software watchdog.

Important APIs/types/functions: `struct nct7904_data` stores the I2C client, watchdog device, selected bank, enabled sensor masks, fan modes, DTS mode, and cached alarm bits. Access is through `nct7904_bank_select()`, `nct7904_read_reg*()`, `nct7904_write_reg()`, typed hwmon `read`/`write`/`is_visible` callbacks, watchdog ops, `nct7904_detect()`, and `nct7904_probe()`.

Control flow: probe reads control registers to derive channel masks, resolves overlapping voltage and thermal-diode/thermistor modes, detects PECI/TSI DTS support, records current fan control modes, clears SMI status registers, registers hwmon info, then registers the watchdog. Runtime hwmon callbacks bank-switch and read/write split register encodings for voltage limits, fan minimum count thresholds, temperatures, PWM output, and alarms.

State and persistence: `bank_sel` is a software cache of the hardware bank register. Fan and voltage alarm arrays latch clear-on-read SMI bits until the relevant sysfs alarm is consumed. Watchdog timeout state is mirrored in `wdt->timeout` and in the hardware minute timer.

Dependencies and integration: depends on SMBus byte access, the hwmon `hwmon_chip_info` API, watchdog core, and I2C class probing at 0x2d/0x2e. Sensor visibility is data-driven from chip enable/mode registers.

Risks: no mutex protects `bank_sel` or multi-step split writes, so concurrent sysfs reads/writes could interleave bank changes. Alarm logic is software-latched and clears bits on read. Watchdog ping must stop, reload, and restart the timer because hardware cannot refresh an active timer. Timeout values are truncated to whole minutes.

Test signals: probe mask decoding, bank-switch correctness under concurrent sysfs access, voltage/fan limit round trips, alarm latching and consumption, PECI versus TSI temp type reporting, watchdog start/stop/ping/set-timeout, and detection rejection for wrong IDs or bank register values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nct7904.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/npcm750-pwm-fan.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/npcm750-pwm-fan.c

Purpose: platform hwmon, thermal cooling, PWM, and fan tachometer driver for Nuvoton NPCM7xx/NPCM8xx SoCs. It exposes PWM duty controls and fan RPM readings based on memory-mapped PWM and fan timer blocks.

Important APIs/types/functions: `struct npcm7xx_pwm_fan_data` owns MMIO bases, clocks, IRQs, channel presence maps, timer, fan sample state, cooling devices, and SoC channel limits. Key functions include `npcm7xx_pwm_config_set()`, `npcm7xx_fan_polling()`, `npcm7xx_fan_start_capture()`, `npcm7xx_fan_compute()`, `npcm7xx_fan_isr()`, hwmon callbacks, PWM/fan init helpers, cooling ops, `npcm7xx_en_pwm_fan()`, and probe.

Control flow: probe maps `pwm` and `fan` resources, obtains clocks, initializes PWM modules to about 25 kHz, initializes fan capture timers, requests eight fan module IRQs, parses each DT child for `reg`, optional `cooling-levels`, and `fan-tach-ch`, registers hwmon, then starts a 200 ms timer if any fan is present. The timer rotates through fan modules, arms capture, and ISR updates averaged counts or zeroes on timeout.

State and persistence: state is in MMIO registers plus `fan_dev[]` sample flags/counts and `pwm_present`/`fan_present` bitmaps. Thermal cooling state records current level and maps it to PWM duty. No suspend persistence is implemented.

Dependencies and integration: depends on platform resources, OF child configuration, clocks, IRQs, timer API, hwmon, and thermal cooling registration. Compatible data selects 8 or 12 PWM channels.

Risks: IRQ module calculation assumes contiguous IRQ numbers (`irq - fan_irq[0]`). Timer setup is inside a loop but only one timer exists. PWM writes and thermal writes are not locked against each other. DT validation for PWM port and tach indices is limited. Removing devres resources does not explicitly delete the active timer.

Test signals: DT parsing with multiple fans per PWM, IRQ capture and timeout RPM behavior, PWM duty read/write, cooling-level transitions, clock-derived frequency logs, NPCM750 versus NPCM845 channel visibility, and remove/unbind timer behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/npcm750-pwm-fan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nsa320-hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nsa320-hwmon.c

Purpose: simple platform hwmon driver for ZyXEL NSA320 boards. It bit-bangs three GPIOs connected to a Holtek MCU that reports chassis fan speed and system temperature.

Important APIs/types/functions: `struct nsa320_hwmon` stores the GPIO descriptors, cached 32-bit MCU word, last update time, and `update_lock`. `nsa320_hwmon_update()` performs the GPIO protocol. `temp1_input_show()`, `fan1_input_show()`, and `label_show()` expose hwmon attributes. Probe obtains `act`, `clk`, and `data` GPIOs and registers attribute groups.

Control flow: sysfs reads call `nsa320_hwmon_update()`. The update path returns cached data for one second, otherwise asserts the active line, waits 100 ms, clocks 32 bits MSB-first with 100-200 us half-periods, deasserts active, validates the magic byte, and caches the word. Temperature is low 16 bits in tenths of a degree and fan speed is the next byte in hundreds of RPM.

State and persistence: only a one-second in-memory cache persists between reads. GPIO levels are initialized through descriptor flags and toggled directly. Invalid reads do not replace the previous cached value.

Dependencies and integration: depends on OF compatible `zyxel,nsa320-mcu`, gpiolib consumer descriptors named `act`, `clk`, and `data`, jiffies, and classic hwmon sysfs groups.

Risks: timing margins are hardware-specific and deliberately long; the protocol resembles SPI but cannot use standard SPI timing. `MAGIC_NUMBER` must remain below 0x80 because errors are negative. Failed reads return `-EIO` encoded through signed `s32`, while `mcu_data` is unsigned in storage.

Test signals: GPIO waveform timing, magic-byte rejection, one-second cache behavior, correct temp/RPM scaling, probe deferral or failure for missing GPIOs, and operation on real NSA320 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nsa320-hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ntc_thermistor.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/ntc_thermistor.c

Purpose: generic platform hwmon driver for NTC thermistors connected through an IIO voltage ADC and a configured resistor divider. It converts ADC voltage to thermistor resistance and then to temperature using built-in compensation tables.

Important APIs/types/functions: `struct ntc_compensation` and `struct ntc_type` model sorted resistance/temperature tables. `struct ntc_data` stores electrical parameters, connection orientation, IIO channel, and table selection. Core functions are `ntc_adc_iio_read()`, `get_ohm_of_thermistor()`, `lookup_comp()`, `get_temp_mc()`, `ntc_read()`, `ntc_thermistor_parse_props()`, and probe.

Control flow: probe gets an IIO voltage channel, reads `pullup-uv`, `pullup-ohm`, `pulldown-ohm`, and `connected-positive`, validates the divider, selects a table from OF/platform match data, and registers hwmon. Reads fetch processed voltage, fall back through raw conversion and a 12-bit assumption if needed, compute resistance for positive or ground-connected divider topologies, reject out-of-range values, binary-search the descending table, and linearly interpolate millidegrees Celsius.

State and persistence: configuration is immutable after probe. No periodic cache is kept; every `temp1_input` read samples the IIO channel. The only persistent state is the selected table and electrical parameters.

Dependencies and integration: depends on IIO consumer APIs, firmware properties, fixed-point interpolation, and hwmon chip info. Compatible strings cover EPCOS, Murata, Samsung, and deprecated `ntc,*` aliases.

Risks: fallback raw conversion assumes a 12-bit ADC and Vref equal to pullup voltage. Divider equations can saturate to `UINT_MAX` for zero divisors. Compensation tables must remain sorted by descending resistance. A zero or rail ADC reading is treated as no data.

Test signals: property validation failures, ADC processed/raw fallback paths, both connection orientations, interpolation at table points and between points, out-of-range resistance rejection, and `temp1_type` reporting thermistor type 4.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/ntc_thermistor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken2.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken2.c

Purpose: HID hwmon driver for NZXT Kraken X42/X52/X62/X72 coolers. It exposes coolant temperature, fan speed, and pump speed from asynchronous USB HID status reports.

Important APIs/types/functions: `struct kraken2_priv_data` stores HID/hwmon devices, last parsed temperature/RPM values, and update jiffies. Main entry points are `kraken2_raw_event()`, `kraken2_read()`, `kraken2_read_string()`, `kraken2_probe()`, and `kraken2_remove()`.

Control flow: probe parses HID descriptors, starts HID hardware with hidraw enabled, opens the device so input reports flow, and registers hwmon. The raw-event hook accepts report id `0x04` with at least seven bytes, converts coolant temperature as integer plus tenths, parses big-endian fan and pump RPM fields, and refreshes `updated`. Hwmon reads return cached values only if a recent report arrived within the two-second validity window.

State and persistence: no hardware configuration is changed. Cached sensor data persists in memory until stale; `updated` is initialized in the past so initial reads return `-ENODATA` until a real report arrives.

Dependencies and integration: depends on HID, hidraw coexistence, hwmon chip info, jiffies, and unaligned big-endian helpers. The HID id table matches NZXT vendor 0x1e71 product 0x170e.

Risks: there is no locking around raw-event writes and sysfs reads, relying on naturally aligned scalar updates. The device cannot answer status Get_Report requests, so missing asynchronous reports make readings unavailable. Temperature fractional interpretation is inferred from observed firmware behavior.

Test signals: HID probe/open/remove, report parsing with correct ID and size, stale-data `-ENODATA`, hidraw coexistence with userspace tools, label strings, and endian-correct RPM values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken3.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken3.c

Purpose: HID hwmon driver for NZXT Kraken X53/X63/X73, Z53/Z63/Z73, and 2023/Elite coolers. It reports coolant temperature, pump/fan speeds, PWM duty, manual and curve controls, firmware debugfs data, and reset-resume reinitialization.

Important APIs/types/functions: `struct kraken3_data` owns HID state, hwmon/debugfs devices, command buffer, completions, locks, per-channel control info, sensor values, device kind, firmware version, and fault state. Important functions include `kraken3_write_expanded()`, `kraken3_read_x53()`, `kraken3_read_z53()`, `kraken3_read()`, `kraken3_write_curve()`, `kraken3_write_fixed_duty()`, `kraken3_write()`, curve sysfs store helpers, `kraken3_raw_event()`, init/firmware helpers, debugfs setup, probe, remove, and reset-resume.

Control flow: probe opens HID, classifies product kind, allocates a 64-byte output buffer, initializes locks/completions, sends interval and init commands, requests firmware version, registers hwmon with extra curve attributes, and creates debugfs if firmware is known. X-series receives periodic status asynchronously; Z-series/2023 reads explicitly send a status request and wait for the raw-event completion. PWM writes program a 40-point curve; manual duty is represented by a flat curve with 100 percent at the critical point.

State and persistence: in-memory state tracks last reported duty, fixed duty, curve points, mode, firmware, fault flag, and freshness. Hardware state persists in the cooler after output reports. Resume replays initialization but does not reconstruct all user curves.

Dependencies and integration: depends on HID, hwmon, extra hwmon-sysfs attributes, completions, mutexes, spinlocks, debugfs, and product-specific report layouts.

Risks: report layouts are reverse engineered and product-dependent. Fault reports with `0xff` temperature bytes suppress readings. X-series cannot request fresh status, so stale data blocks reads. Concurrency between hidraw/user sysfs/report completions is delicate. Pump duty is clamped to 20 percent minimum except forced 100 percent for off mode.

Test signals: product-ID kind mapping, init and firmware command success, X-series first-report wait, Z-series request/response path, stale timeout handling, fault report handling, PWM enable transitions 0/1/2, curve attribute visibility, debugfs firmware output, and reset-resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-kraken3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-smart2.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-smart2.c

Purpose: reverse-engineered HID hwmon driver for NZXT Smart Device v2 and RGB & Fan Controller devices. It exposes three fan channels with RPM, PWM duty/mode/enable, voltage, current, labels, and update interval control.

Important APIs/types/functions: packed report structs model fan configuration, status, and set-speed output reports. `struct drvdata` stores HID/hwmon handles, cached fan telemetry, received flags, waitqueue, mutex, update interval, and output buffer. Key functions are `handle_fan_config_report()`, `handle_fan_status_report()`, hwmon read/write/string callbacks, `send_output_report()`, `set_pwm()`, `set_pwm_enable()`, update interval conversion helpers, `init_device()`, raw-event, reset-resume, probe, and remove.

Control flow: probe parses and opens HID, starts I/O, sends fan detection and update interval commands, then registers hwmon. Raw events parse config report `0x61` and status report `0x67` for speed or voltage data. Hwmon reads wait on report-backed flags with the waitqueue lock held so fancontrol sees coherent initial PWM/fan values. Writes serialize output reports with a mutex and optimistically update cached PWM duty after successful writes.

State and persistence: cached telemetry and fan type live in memory and are reset on resume before reinitialization. Device state includes update interval and commanded fan duty. `fan_config_received` gates status acceptance because fan detection can reset PWM values.

Dependencies and integration: depends on HID/hidraw coexistence, hwmon chip info, wait queues, spinlocks, mutexes, unaligned little-endian helpers, and NZXT USB IDs.

Risks: report formats are reverse engineered and include unknown static fields. Waiting sysfs reads can block until reports arrive. `pwm_enable` writes are mostly compatibility shims and only accept the current expected value. PWM values are scaled between 0-255 and 0-100 percent, preserving nonzero positive duty.

Test signals: fan-detect handshake, speed and voltage report parsing, blocking-read wakeups, PWM write immediate readback, update interval conversion, unexpected fan type warnings, resume flag reset and reinit, and all listed product IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/nzxt-smart2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/Kconfig

Purpose: Kconfig definitions for IBM On-Chip Controller hwmon support.

Important symbols: `SENSORS_OCC_P8_I2C` enables the POWER8 I2C BMC transport and depends on `I2C`; `SENSORS_OCC_P9_SBE` enables POWER9/P10 SBE/FSI transport and depends on `FSI_OCC`; both select hidden common symbol `SENSORS_OCC`.

Control flow: selecting either transport builds the common OCC hwmon core plus the selected bus frontend. Help text documents that these drivers run on a BMC connected to the POWER processor, not on the host processor itself.

State and persistence: no runtime state; it controls build-time inclusion and module names `occ-p8-hwmon` and `occ-p9-hwmon`.

Dependencies and integration: integrates OCC with the hwmon Kconfig tree, I2C, and FSI OCC infrastructure.

Risks: common code is hidden and selected only by frontends, so new transport symbols must also select `SENSORS_OCC`. Missing dependency updates would surface as build failures.

Test signals: `olddefconfig`, modular and built-in builds for each frontend, and dependency-disabled configs where symbols are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/Makefile -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/Makefile

Purpose: object composition for OCC hwmon modules.

Important entries: `occ-hwmon-common-objs := common.o sysfs.o`, `occ-p8-hwmon-objs := p8_i2c.o`, and `occ-p9-hwmon-objs := p9_sbe.o`. Object inclusion follows `CONFIG_SENSORS_OCC`, `CONFIG_SENSORS_OCC_P8_I2C`, and `CONFIG_SENSORS_OCC_P9_SBE`.

Control flow: the Kconfig-selected common module links shared polling, parsing, dynamic sysfs, and status sysfs code, while each transport module links only its bus-specific command sender.

State and persistence: no runtime state; it controls link structure.

Dependencies and integration: ties the hidden common symbol to shared implementation files and the public frontend symbols to their transport objects.

Risks: if a frontend references common exported symbols without `SENSORS_OCC`, link errors occur; current Kconfig selects avoid that.

Test signals: build with common plus P8, common plus P9, both frontends, and all disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.c

Purpose: shared OCC hwmon implementation. It sends poll and power-cap commands through a transport callback, parses OCC poll responses, dynamically creates sensor sysfs attributes, rate-limits updates, tracks communication/safe-state errors, and registers/unregisters the hwmon device.

Important APIs/types/functions: transport-facing exports are `occ_setup()`, `occ_shutdown()`, `occ_active()`, and `occ_update_response()`. Internals include OCC sensor format structs, `occ_poll()`, `occ_set_user_power_cap()`, typed show functions for TEMP/FREQ/POWR/CAPS/EXTN versions, `occ_init_attribute()`, `occ_setup_sensor_attrs()`, and `occ_parse_poll_response()`.

Control flow: `occ_setup()` initializes the mutex, installs the status sysfs group, and optionally activates. Activation polls once, parses block headers, allocates a flat dynamic attribute array based on sensor versions/counts, and registers hwmon groups. Later sysfs reads call `occ_update_response()`, which polls at most once per second and otherwise reuses the last transport error. Power cap writes send command type `0x22`.

State and persistence: `struct occ` holds the last full response, parsed sensor pointers into that response, dynamic attributes, active flag, error counters, safe-state timestamp, and previous status values used by `sysfs.c`. Sensor topology is parsed once and assumed stable. Hardware power cap persists in OCC firmware.

Dependencies and integration: depends on the transport-provided `send_cmd`, hwmon sysfs helpers, common OCC response layout, jiffies, mutexes, unaligned big-endian access, and `occ_sysfs_poll_done()`.

Risks: parsed sensor data pointers point inside `occ->resp`, which is overwritten on every poll but layout is assumed unchanged. Dynamic attribute counts rely on known sensor versions; unsupported versions are hidden. Safe-state becomes fatal only after one minute. Error is promoted only after repeated transfer failures. The poll command checksum fields are zeroed and presumably handled by lower layers/OCC.

Test signals: activation with and without `ibm,no-poll-on-init`, each sensor version's attribute count and units, OCC safe-state timeout, repeated transfer error threshold, power cap writes, unsupported sensor block handling, response size validation, and hwmon unregister on deactivate/shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.h -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.h

Purpose: shared ABI and data model for OCC hwmon common code, status sysfs, and P8/P9 transport frontends.

Important APIs/types: `struct occ_response`, poll response headers, sensor block headers, `struct occ_sensor`, `struct occ_sensors`, dynamic `struct occ_attribute`, and central `struct occ`. Public functions are `occ_active()`, `occ_setup()`, `occ_setup_sysfs()`, `occ_shutdown()`, `occ_shutdown_sysfs()`, `occ_sysfs_poll_done()`, and `occ_update_response()`.

Control flow: frontends embed `struct occ`, fill `bus_dev`, `powr_sample_time_us`, `poll_cmd_data`, and `send_cmd`, then call `occ_setup()`. Common code and sysfs callbacks use the response and parsed sensor pointers stored here.

State and persistence: `struct occ` persists the response buffer, parsed sensor metadata, command callback, update cadence, lock, hwmon/sysfs attribute storage, active/error state, last safe-state time, and previous status fields for notifications.

Dependencies and integration: includes hwmon-sysfs, mutex, and sysfs definitions and forward-declares `struct device`. Transport code depends on this header as the common contract.

Risks: `OCC_RESP_DATA_BYTES` fixes the maximum response buffer; all packed structs must match OCC firmware. `void *data` points into mutable response storage, so consumers must hold or refresh through common locking.

Test signals: compile coverage across common/sysfs/P8/P9 modules, packed layout compatibility with firmware responses, and lifecycle of embedded `struct occ` in both transports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/p8_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/p8_i2c.c

Purpose: POWER8 OCC transport frontend using a BMC I2C connection to access on-chip control bridge SCOM registers and exchange OCC commands through SRAM windows.

Important APIs/types/functions: `struct p8_i2c_occ` embeds `struct occ` with an I2C client. Low-level helpers are `p8_i2c_occ_getscom()`, `p8_i2c_occ_putscom()`, `p8_i2c_occ_putscom_u32()`, `p8_i2c_occ_putscom_be()`, and transport callback `p8_i2c_occ_send_cmd()`. Probe/remove bind this transport to common OCC setup/shutdown.

Control flow: `send_cmd` writes the OCC command SRAM address to OCB, writes the big-endian command through `OCB_DATA3`, triggers data attention through `OCB_DATA1`, then repeatedly reads the response SRAM header until return status is no longer command-in-progress or a one-second timeout expires. It maps OCC response status to Linux errors, validates response length, and fetches remaining 8-byte chunks.

State and persistence: persistent state is the embedded OCC object and I2C client. Common code stores the response and active/error state. Hardware state includes selected OCB address and OCC command processing.

Dependencies and integration: depends on I2C transfers, FSI OCC response status constants, scheduler timeout, unaligned big-endian access, and OF compatible `ibm,p8-occ-hwmon`. Probe sets 250 us power sample time and poll command data `0x10`.

Risks: SCOM address shifting and endian conversions are subtle. The polling loop uses interruptible sleep without checking pending signals. It assumes response chunks can be fetched sequentially by repeated reads. Partial I2C sends are treated as `-EIO`.

Test signals: P8 BMC I2C communication, command-in-progress timeout, all OCC response status mappings, response length bounds, multi-chunk response reads, OF match probe, and clean common shutdown on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/p8_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/p9_sbe.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/p9_sbe.c

Purpose: POWER9/POWER10 OCC transport frontend using the SBE FIFO/FSI OCC interface. It also exposes SBE FFDC binary data after transport errors.

Important APIs/types/functions: `struct p9_sbe_occ` embeds `struct occ` and stores SBE parent device, FFDC buffer state, error flag, and lock. Key functions are `ffdc_read()`, `p9_sbe_occ_save_ffdc()`, transport callback `p9_sbe_occ_send_cmd()`, probe, and remove.

Control flow: `p9_sbe_occ_send_cmd()` calls `fsi_occ_submit()` up to three times for checksum errors (`-EBADE` with no FFDC), preserving original response length between attempts. If the transport returns FFDC data, it saves the first unread FFDC buffer and notifies the binary sysfs file. It then maps OCC return status to Linux errors. Probe initializes common OCC parameters, calls `occ_setup()`, maps `-ESHUTDOWN` to `-ENODEV`, and creates read-only `ffdc`.

State and persistence: FFDC data persists in memory until userspace reads through the buffer; once the read position reaches `ffdc_len`, `sbe_error` clears. Common OCC state stores sensors and hwmon lifecycle. `sbe` is nulled before shutdown on remove and FFDC memory is freed.

Dependencies and integration: depends on platform bus, parent FSI OCC device, `fsi_occ_submit()`, sysfs binary attributes, vmalloc helpers, and compatibles `ibm,p9-occ-hwmon` and `ibm,p10-occ-hwmon`. Probe sets 500 us power sample time and poll command data `0x20`.

Risks: only the first outstanding FFDC is preserved until read. FFDC allocation can fail and silently drop payload length. Common setup may be skipped when host is shut down. Return-status handling duplicates P8 mapping and must track OCC constants.

Test signals: successful P9/P10 FSI probe, checksum retry behavior, FFDC save/read/clear and sysfs notify, host-shutdown probe mapping, OCC status mappings, binary file cleanup, and common shutdown/free path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/p9_sbe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/hwmon/occ/sysfs.c

Purpose: common non-hwmon control/status sysfs group for OCC devices. It exposes OCC active state, master status, throttling/error indicators, state/mode/IP status, OCC count, GPU throttle bits, and transfer error state.

Important APIs/types/functions: `occ_active_store()` toggles common activation. `occ_sysfs_show()` reads indexed status attributes from the latest poll response. `occ_error_show()` returns `occ->error`. `occ_sysfs_poll_done()` sends sysfs notifications when selected status bits change. `occ_setup_sysfs()` and `occ_shutdown_sysfs()` create/remove the group.

Control flow: setup creates attributes directly on `occ->bus_dev->kobj`, separate from the hwmon device. Reads poll through `occ_update_response()` when active; inactive reads return `0` for `occ_active` and `-ENODATA` values for status-like attributes. After every poll, common code calls `occ_sysfs_poll_done()`, which compares current header fields with previous cached fields and calls `sysfs_notify()` for changed error-relevant attributes.

State and persistence: previous status/error fields live in `struct occ` and are updated after each poll. The sysfs group persists for the transport device lifetime, even while hwmon sensor attributes can be inactive.

Dependencies and integration: depends on sysfs, hwmon sensor-device attributes for indexed control files, bitops, hweight, and `common.h` response layout. `occ_active` bridges userspace activation to `occ_active()`.

Risks: `occ_error_show()` ignores the return value of `occ_update_response()` and reports the stored error. Notifications are intentionally absent for `occ_state`, so listeners must poll it. Inactive status attributes return a negative integer string rather than a read error, except invalid indices.

Test signals: sysfs group creation/removal, active toggling, inactive reads, changed-bit notifications for master/DVFS/memory/quick-drop/VDD/GPU/IP/mode/error, OCC count behavior on master versus non-master, and interaction with common polling rate limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/hwmon/occ/sysfs.c -->
