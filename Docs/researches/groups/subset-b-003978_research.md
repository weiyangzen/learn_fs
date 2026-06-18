# Research: subset-b-003978 touchscreen drivers

This grouped report covers the assigned Linux touchscreen source files under `sources/distributed-fs/ceph-client/drivers/input/touchscreen/`. Each section is delimited for deterministic reconciliation into the source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/colibri-vf50-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/colibri-vf50-ts.c

Purpose: `colibri-vf50-ts.c` is a platform driver for the Toradex Colibri VF50 4-wire resistive touchscreen. It drives the four touchscreen plates through GPIOs, samples four IIO ADC channels, computes X/Y and pressure, and exposes a single-touch `input_dev` with `ABS_X`, `ABS_Y`, `ABS_PRESSURE`, and `BTN_TOUCH`.

Important APIs, types, and functions: `struct vf50_touch_device` owns the platform device, input device, IIO channel array, four plate GPIOs, IRQ number, pressure threshold, and stop flag. `adc_ts_measure()` energizes a positive/negative plate pair, waits for settling, averages five raw IIO samples, then de-energizes the plates. `vf50_ts_enable_touch_detection()` grounds YM and switches pinctrl to idle so XM can be used as the pull-up based pen-detect input. `vf50_ts_irq_bh()` is the threaded IRQ worker and performs the repeated sampling loop. `vf50_ts_open()` and `vf50_ts_close()` arm and disarm touch detection for input users. Probe uses `iio_channel_get_all()`, `devm_add_action()`, named GPIO descriptors, `platform_get_irq()`, and `devm_request_threaded_irq()`.

Control flow: probe validates exactly four ADC channels, reads the `vf50-ts-min-pressure` DT property, allocates/registers input, obtains `xp`, `xm`, `yp`, and `ym` GPIOs, then requests a oneshot threaded IRQ. Open clears `stop_touchscreen`, configures idle pinctrl, enables YM, and waits for the pull-up to settle. The IRQ handler disables detection, switches pins to ADC mode, loops until stop or low pressure, measures X, Y, Z1, and Z2, computes a pressure-like value, drops the first sample after a pen-down, reports subsequent samples, and finally reports release and re-enables detection.

State and persistence: runtime state is only in memory: last measurement is local to the IRQ worker, and `stop_touchscreen` gates the sampling loop. There is no firmware, sysfs, NVM, or persistent calibration. Close uses a memory barrier plus `synchronize_irq()` so the threaded loop stops before GPIO/pinctrl cleanup.

Dependencies and integration points: the driver depends on IIO ADC channels, GPIO descriptor names, pinctrl default/idle states, a platform IRQ, and OF compatible `toradex,vf50-touchscreen`. It integrates with the input subsystem through open/close callbacks and with power/cleanup through devm-managed resources.

Risks: pressure calculation can divide by noisy small Z1 values, although the code guards Z1 and X above 64. Long `usleep_range()` calls occur inside the IRQ thread while a finger is held. Correct DT wiring is critical because the plate GPIO and ADC channel order are positional. If `vf50-ts-min-pressure` is mis-tuned, touches may be missed or releases delayed.

Test signals: useful checks include probing with exactly four ADC channels, verifying open/close pinctrl transitions, confirming pen-down IRQ triggers repeated reports, validating first-sample discard behavior, checking pressure threshold release, and testing close while a touch is active to confirm the IRQ thread exits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/colibri-vf50-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctma140.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctma140.c

Purpose: `cy8ctma140.c` is an I2C driver for Cypress CY8CTMA140/TMA140 multitouch controllers. It assumes firmware is already present in controller flash, reads up to four contacts from fixed-format I2C packets, and exposes a direct multitouch input device.

Important APIs, types, and functions: `struct cy8ctma140` holds the `input_dev`, touchscreen properties, `i2c_client`, two regulators (`vcpin`, `vdd`), and legacy previous-finger fields. `cy8ctma140_irq_thread()` sends command `CY8CTMA140_GET_FINGERS` then reads a 31-byte packet with `i2c_transfer()`. `cy8ctma140_report()` maps controller contact IDs to MT slots with `input_mt_get_slot_by_key()`, decodes big-endian X/Y and width, applies `touchscreen_report_pos()`, and reports `ABS_MT_TOUCH_MAJOR`. `cy8ctma140_init()` fetches firmware info. Power helpers bulk-enable/disable regulators, with simple PM ops around suspend/resume.

Control flow: probe allocates the state and input device, sets ABS capabilities and touchscreen properties, initializes four MT slots with `INPUT_MT_DIRECT | INPUT_MT_DROP_UNUSED`, obtains regulators, powers up with a 250 ms delay, registers a devm power-off action, requests a oneshot threaded IRQ, reads firmware info, then registers input. The IRQ path validates transfer count, drops packets marked invalid by bit 5 of `buf[1]`, validates finger count, and reports current contacts.

State and persistence: the only durable state is regulator power state and input slot tracking maintained by the input core. The driver reads firmware metadata but does not update firmware or persist settings. Suspend powers the controller down unless the device is wake-capable.

Dependencies and integration points: it depends on standard I2C transfers, regulator supplies named `vcpin` and `vdd`, DT compatible `cypress,cy8ctma140`, and touchscreen properties for axis ranges. The input integration is type-B multitouch; DT should provide required axis properties because the driver intentionally does not default X/Y maxima.

Risks: the packet parser relies on hard-coded offsets and split contact-ID nibbles, so firmware format mismatches can silently drop contacts. Probe requests the IRQ before registering input, so spurious early IRQs depend on hardware readiness. Touch-key bytes in the packet are not handled. Wakeup suspend leaves power on but no explicit wake IRQ programming is done here.

Test signals: validate regulator sequencing, firmware info read, invalid-packet suppression, contact ID to slot reuse, 1 to 4 finger reports, axis inversion/swap DT properties through `touchscreen_parse_properties()`, and suspend/resume both with and without `device_may_wakeup()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctma140.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctmg110_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctmg110_ts.c

Purpose: `cy8ctmg110_ts.c` is an older Cypress CY8CTMG110 I2C touchscreen driver. It reports single-touch absolute X/Y coordinates and `BTN_TOUCH`, supports an optional reset GPIO, and places the controller in and out of sleep across lifecycle events.

Important APIs, types, and functions: `struct cy8ctmg110` stores the input device, physical path, I2C client, and reset GPIO. `cy8ctmg110_power()` drives reset asserted/deasserted. `cy8ctmg110_write_regs()` and `cy8ctmg110_read_regs()` implement small I2C register transactions. `cy8ctmg110_touch_pos()` reads nine bytes starting at `CY8CTMG110_TOUCH_X1`, uses the ninth byte as finger count, and decodes big-endian X/Y. `cy8ctmg110_set_sleepmode()` writes wake/sleep timing values. IRQ, suspend, resume, and devm shutdown all delegate to these helpers.

Control flow: probe checks adapter support, allocates state and input, configures fixed coordinate ranges 0..759 and 0..465, requests an optional reset GPIO initially asserted, powers on and exits sleep mode, installs a devm shutoff action, requests a oneshot threaded IRQ, registers input, and stores client data. Each IRQ reads the current position and reports either release or one contact.

State and persistence: the driver keeps no persistent calibration or firmware state. Runtime state is the reset GPIO level, controller sleep mode, and input event state. Devm cleanup sleeps and resets the device.

Dependencies and integration points: it integrates with I2C, GPIO descriptors, threaded IRQs, PM sleep callbacks, and the legacy input ABS single-touch API. It has no OF match table in this file, only an I2C ID table named `cy8ctmg110`.

Risks: `cy8ctmg110_read_regs()` treats any nonnegative `i2c_transfer()` result as success, without checking that both messages completed. The functionality check asks for SMBus word reads even though the driver uses raw I2C transfers. Coordinates are fixed in code and not corrected through `touchscreen_parse_properties()`. `BUG_ON(len > 5)` is harsh for a helper that could return `-EINVAL`.

Test signals: exercise reset GPIO polarity, sleep/resume commands, IRQ read error handling, pen-up reporting when finger count is zero, fixed range reporting, and suspend/resume with wakeup disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cy8ctmg110_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp5.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp5.c

Purpose: `cyttsp5.c` is a self-contained I2C/regmap driver for Parade/Cypress TrueTouch Standard Product Gen5 controllers, such as `cypress,tt21000`. It speaks the controller's HID-like protocol, launches the application from bootloader mode, queries system information, reports multitouch and optional button events, and manages sleep/wake power commands.

Important APIs, types, and functions: `struct cyttsp5` owns the regmap, command completion, HID descriptor, sysinfo, command/input/response buffers, reset GPIO, input device, touchscreen properties, regulator supplies, and previous record count. `cyttsp5_read()` fetches a HID input frame length and then the full frame. `cyttsp5_write()` writes HID command frames using the low/high register address layout required by the device. `cyttsp5_validate_cmd_response()` validates bootloader/app responses, including SOP/EOP and CRC for bootloader replies. `cyttsp5_startup()` deasserts stale interrupt data, launches the app, reads the HID descriptor, fills touch-field descriptors, and requests sysinfo. `cyttsp5_handle_irq()` dispatches touch, button, and command response reports.

Control flow: I2C probe creates an 8-bit regmap and calls the generic `cyttsp5_probe()`. Probe obtains and enables `vdd`/`vddio`, allocates input, asserts and releases optional reset, requests a threaded IRQ, performs startup, parses optional `linux,keycodes`, parses touchscreen properties, enables key bits, and registers input with MT slots sized from sysinfo. Runtime IRQs read the input frame; touch frames extract contact count and per-contact fields using bit offsets, report slots by contact ID, transform positions through touchscreen properties, and sync the frame. Command frames copy to `response_buf` and complete `cmd_done`.

State and persistence: in-memory state includes the HID/system descriptors, parsed touch field metadata, key codes, previous touch count, and command response buffers. The driver does not persist settings or update firmware. Suspend/resume sends HID set-power commands unless the device is configured as a wake source.

Dependencies and integration points: it depends on I2C, regmap, CRC-ITU-T, regulators `vdd`/`vddio`, optional reset GPIO, input MT, `touchscreen_parse_properties()`, and optional DT `linux,keycodes`. It exposes an I2C driver named `cyttsp5` and an OF compatible for `cypress,tt21000`.

Risks: command synchronization relies on IRQ delivery; missing or masked IRQs cause timeouts during probe or PM. `cyttsp5_get_touch_axis()` assumes field sizes and masks derived from hard-coded report descriptor offsets rather than parsing a descriptor from hardware. Contact ID is used directly as an MT slot and must remain within initialized slot bounds. Sysinfo dimensions are used in major/minor conversion and can divide by zero if firmware reports bad lengths.

Test signals: probe should show successful bootloader launch, HID descriptor validation, sysinfo retrieval, and MT slot initialization. Runtime tests should include zero-touch frames, max-touch frames, button report IDs with configured keycodes, command timeout paths, suspend/resume power commands, and wakeup-enabled PM bypass.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp5.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.c

Purpose: `cyttsp_core.c` is the shared core for older Cypress TrueTouch Standard Product Gen3 controllers, used by the I2C and SPI transport drivers. It handles bootloader exit, operational/sysinfo mode setup, optional handshake flow control, input reporting, open/close power state, and PM.

Important APIs, types, and functions: the exported entry point is `cyttsp_probe(const struct cyttsp_bus_ops *bus_ops, struct device *dev, int irq, size_t xfer_buf_size)`. Low-level access is abstracted by `ttsp_read_block_data()` and `ttsp_write_block_data()`, which retry through bus ops up to `CY_NUM_RETRY`. Boot and mode helpers include `cyttsp_hard_reset()`, `cyttsp_soft_reset()`, `cyttsp_load_bl_regs()`, `cyttsp_exit_bl_mode()`, `cyttsp_set_sysinfo_mode()`, `cyttsp_set_sysinfo_regs()`, and `cyttsp_set_operational_mode()`. `cyttsp_irq()` reads touch packets and handles bootloader-ready completion. `cyttsp_report_tchdata()` maps up to four contacts into 16 MT slots.

Control flow: bus glue calls `cyttsp_probe()` with transport ops and buffer size. The core enables `vcpin` and `vdd`, gets optional reset GPIO, parses required `bootloader-key` plus optional timing/handshake properties, initializes input and MT slots, requests an initially disabled threaded IRQ, hard-resets the chip, powers it on through bootloader/sysinfo/operate sequencing, and registers input. Input open wakes the controller by reading registers and then enables IRQ. Close sends low-power mode and disables IRQ. Suspend/resume mirror open/close while holding the input mutex.

State and persistence: `struct cyttsp` stores bootloader data, sysinfo data, the latest XY data, BL completion, state enum, suspend flag, GPIO, handshake and timing properties, bootloader keys, and a transport-aligned transfer buffer. There is no persistence beyond device registers programmed during startup.

Dependencies and integration points: the core depends on the transport contract in `cyttsp_core.h`, regulators, optional reset GPIO, device properties, input MT, and `touchscreen_parse_properties()`. It exports `cyttsp_pm_ops` and `cyttsp_probe()` for I2C/SPI modules.

Risks: `bootloader-key` is required; missing firmware properties fail probe. IRQ is disabled/enabled manually and must remain balanced across soft reset/open/close/suspend paths. The touch report uses firmware-provided tracking IDs directly as MT slots, so malformed IDs over 15 could exceed the initialized bitmap/slot assumption. Recovering from unexpected bootloader mode during IRQ may leave the device idle if exit fails.

Test signals: verify I2C and SPI bus ops both reach `cyttsp_probe()`, required property handling, soft reset completion through IRQ, bootloader exit, sysinfo and interval programming, large-area/bad-packet release behavior, open/close IRQ balancing, and suspend/resume with an enabled input device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.h

Purpose: `cyttsp_core.h` defines the public data structures and transport interface for the older Cypress TTSP core. It is included by `cyttsp_core.c`, `cyttsp_i2c.c`, and `cyttsp_spi.c`.

Important APIs, types, and functions: `struct cyttsp_tch` represents one packed touch record with big-endian X/Y and 8-bit Z. `struct cyttsp_xydata` maps the operational report block, including host/status/mode bytes, four touch records, tracking ID nibbles, gesture fields, and active-distance register. `struct cyttsp_sysinfo_data` and `struct cyttsp_bootloader_data` map sysinfo and bootloader register layouts. `struct cyttsp_bus_ops` is the core transport abstraction with a Linux input bus type plus `read()` and `write()` callbacks. `enum cyttsp_state` separates idle, active, and bootloader-wait states. `struct cyttsp` is the core runtime object and ends with cacheline-aligned flexible `xfer_buf`. The header exports `cyttsp_probe()` and `cyttsp_pm_ops`.

Control flow: transport drivers allocate no core state directly; they provide bus ops and a transfer-buffer size to `cyttsp_probe()`. The core then uses the structures in this header as packed wire-format overlays for I2C/SPI reads.

State and persistence: the header declares only in-memory state. Its packed structs mirror volatile controller registers and reports, while persistent behavior is limited to values supplied by platform properties at probe.

Dependencies and integration points: the header depends on kernel device, regulator, module, type, and error headers. It is the stable contract between bus-specific modules and the common TTSP logic. `CY_NUM_RETRY` sets the transport retry policy used by the core.

Risks: packed wire structs require exact firmware/register layout compatibility. The flexible buffer is cacheline aligned and sized by bus drivers; an undersized bus-provided buffer would break transfer helpers. `extern const struct dev_pm_ops cyttsp_pm_ops` ties bus drivers to the core module's exported PM object.

Test signals: build coverage should include both I2C and SPI modules. Static checks should confirm packed layout sizes match datasheet expectations, and runtime tests should confirm bus ops receive a sufficiently sized `xfer_buf`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_i2c.c

Purpose: `cyttsp_i2c.c` is the I2C transport shim for the older Cypress TTSP core. It supplies `struct cyttsp_bus_ops` implementations that translate the core's 16-bit register accesses into the controller's I2C addressing convention.

Important APIs, types, and functions: `cyttsp_i2c_read_block_data()` builds a two-message I2C transfer: write low address byte, then read the requested length. `cyttsp_i2c_write_block_data()` prefixes the low address byte into the shared transfer buffer and writes the address plus payload. Both derive `client_addr` from the base I2C address ORed with bit 8 of the requested register. `cyttsp_i2c_probe()` checks `I2C_FUNC_I2C`, calls `cyttsp_probe()` with `CY_I2C_DATA_SIZE`, and stores the returned core pointer.

Control flow: module registration creates an I2C driver named `cyttsp-i2c`. Matching clients for `cypress,cy8ctma340` or `cypress,cy8ctst341` run the functionality check, instantiate the shared core, and inherit the core PM ops.

State and persistence: this file keeps no independent runtime or persistent state. The I2C client data points to the `struct cyttsp` allocated by the core.

Dependencies and integration points: it depends on the core header, Linux I2C and input bus constants, OF match data, and `pm_sleep_ptr(&cyttsp_pm_ops)`. The transfer buffer ownership remains in the core object.

Risks: the high register bit being encoded into the slave address is unusual and hardware-specific; adapters or board descriptions with incompatible address handling will fail transfers. Write length is limited by the 128-byte core buffer minus one address byte. Errors are detected by exact I2C message count.

Test signals: check probe on both compatible strings, read/write paths with registers below and above 0x100, transfer failure propagation, and PM callbacks through the shared core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_spi.c

Purpose: `cyttsp_spi.c` is the SPI transport shim for the older Cypress TTSP core. It formats full-duplex SPI command frames, validates synchronization acknowledgements, and delegates device lifecycle and input reporting to `cyttsp_core.c`.

Important APIs, types, and functions: `cyttsp_spi_xfer()` is the central transport helper. It builds a four-byte header (`0x00`, `0xff`, register, op), appends write data when needed, performs one or two `spi_transfer`s, and validates `0x62 0x9d` at `CY_SPI_SYNC_BYTE`. `cyttsp_spi_read_block_data()` and `cyttsp_spi_write_block_data()` wrap it for the core bus ops. `cyttsp_spi_probe()` forces 8 bits per word and SPI mode 0, runs `spi_setup()`, calls `cyttsp_probe()` with a double buffer sized for TX and RX, and stores driver data.

Control flow: matching SPI devices for `cypress,cy8ctma340` or `cypress,cy8ctst341` configure the SPI controller, instantiate the shared core, and use exported core PM callbacks. During reads, the first transfer clocks out the command header and the second reads payload bytes; writes combine header and payload in one full-duplex transfer.

State and persistence: no local persistent state exists. The transport uses the core-owned flexible transfer buffer split into write and read halves for each operation.

Dependencies and integration points: it depends on SPI core APIs, the TTSP core bus contract, OF matching, and the input bus type `BUS_SPI`. It provides `MODULE_ALIAS("spi:cyttsp")`.

Risks: only 8-bit, mode-0 SPI is supported. `cyttsp_spi_xfer()` logs but continues after `spi_sync()` errors to allow ACK validation, so callers see `-EIO` on bad ACK rather than the original error in many cases. Register arguments are only passed as one byte in the SPI header even though the core API uses `u16`. Transfers over 128 data bytes are rejected.

Test signals: validate SPI setup, read/write ACK checking, bad operation handling, overlength rejection, shared core probe success, and suspend/resume via `cyttsp_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/cyttsp_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9034-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9034-ts.c

Purpose: `da9034-ts.c` is a platform driver for the Dialog/Marvell DA9034 PMIC touchscreen interface. It uses DA903x MFD register access and notifier events to sample resistive touchscreen coordinates and report single-touch input events.

Important APIs, types, and functions: `struct da9034_touch` stores the parent DA9034 device, input device, delayed work, notifier, state machine state, sampling interval, inversion flags, and last X/Y. `da9034_event_handler()` is the state machine over `STATE_IDLE`, `STATE_BUSY`, `STATE_STOP`, and `STATE_WAIT`. Helpers manage pen detection (`detect_pen_down()`), TSI auto measurement (`start_tsi()`/`stop_tsi()`), coordinate reads (`read_tsi()`), and reports. `da9034_touch_open()` registers the MFD notifier and initializes ADC/TSI registers; close unregisters and powers down the ADC LDO.

Control flow: probe reads optional platform data for interval and axis inversion, initializes delayed work and notifier, allocates input, registers ABS_X/ABS_Y and `BTN_TOUCH`, and registers input. Open enables DA9034 pen-down and TSI-ready notifications, powers ADC LDO, writes TSI delay/skip registers, enters idle, and enables pen detect. A pen-down event starts auto TSI sampling; a TSI-ready event reads coordinates, stops TSI, delays 1 ms, manually checks pen state, then either reports/down schedules next sample or reports/up returns idle. Delayed work rechecks pen state and repeats sampling.

State and persistence: the driver keeps last X/Y and an explicit state machine. Hardware state is DA9034 ADC LDO, pen-detect bit, and auto TSI bit. There is no persistent storage or DT parsing in this file.

Dependencies and integration points: it depends on the DA903x MFD API, platform data `struct da9034_touch_pdata`, delayed work, input single-touch APIs, and a platform device named `da9034-touch`.

Risks: notifier registration errors after ADC LDO enable are not unwound in open. The state machine relies on simulated pen events after stopping TSI because hardware pen status is unreliable. Axis inversion uses `1024 - x`, which can produce 1024 while the declared max is 1023. No locking protects `state` between notifier and delayed work contexts.

Test signals: test pen-down to TSI-ready transitions, release detection after scheduled work, axis inversion, open failure paths, close while work is pending, ADC LDO enable/disable, and noisy quick tap behavior noted by the FIXME.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9034-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9052_tsi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9052_tsi.c

Purpose: `da9052_tsi.c` is a platform touchscreen driver for the Dialog DA9052 PMIC TSI block. It samples X/Y/Z pressure through DA9052 ADC registers and coordinates separate pen-down and TSI-ready IRQs.

Important APIs, types, and functions: `struct da9052_tsi` stores the DA9052 MFD pointer, input device, delayed pen work, stopped flag, and ADC-on flag. `da9052_ts_adc_toggle()` enables/disables continuous TSI conversion and mirrors `adc_on`. `da9052_ts_pendwn_irq()` masks pen-down, unmasks TSI-ready, enables ADC, and schedules polling work. `da9052_ts_datardy_irq()` reads and reports samples through `da9052_ts_read()`. `da9052_ts_pen_work()` polls pen status and on release disables ADC, reports release, clears events, and swaps IRQ masks. Probe configures GPIO mux, TSI timing/mode, LDO9 reference, IRQs, and input.

Control flow: probe allocates state and input manually, disables pen detect and ADC, requests DA9052 PENDOWN and TSIREADY IRQs, masks both, configures TSI hardware, registers input, and stores platform data. Input open clears `stopped`, enables PENDOWN, and enables the pen detect circuit. On pen-down IRQ the driver switches to data-ready sampling and schedules a 20 ms pen polling loop. Close stops polling, balances IRQ enable counts if ADC was active, disables ADC and pen detect.

State and persistence: runtime state is `stopped`, `adc_on`, delayed work, and DA9052 register/IRQ mask state. Removal restores LDO9 to `0x19`, frees IRQs, unregisters input, and frees memory. No persistent calibration exists.

Dependencies and integration points: it relies on DA9052 MFD register and IRQ APIs, platform device `da9052-tsi`, Linux input, delayed work, and PMIC register definitions.

Risks: probe uses non-devm allocation and manual unwind, so error paths must stay balanced. `da9052_ts_adc_toggle()` ignores register update errors but updates `adc_on` regardless. The pen polling work treats read errors as pen still down, which may keep polling indefinitely until close. The FIXME acknowledges unhandled IRQ issues on quick pen down/up sequences.

Test signals: validate GPIO/TSI register programming, pen-down IRQ mask transition, data-ready sample reporting, release polling and pressure-zero report, close with ADC active, IRQ balancing, removal restore of LDO9, and quick tap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/da9052_tsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/dynapro.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/dynapro.c

Purpose: `dynapro.c` is a serio driver for Dynapro RS-232 touchscreen packets, typically attached through `inputattach`. It decodes a three-byte packet into single-touch X/Y and touch state.

Important APIs, types, and functions: `struct dynapro` contains the input device, serio port, packet index, three-byte data buffer, and physical path. `dynapro_interrupt()` buffers bytes from serio, accepts frames whose first byte has the `0x80` response-begin bit, and calls `dynapro_process_data()`. `dynapro_process_data()` waits for three bytes, decodes 10-bit X/Y from packed high bits in byte 0 and low bytes in bytes 1/2, reports `BTN_TOUCH`, and syncs. `dynapro_connect()`/`dynapro_disconnect()` manage input and serio lifecycle.

Control flow: the serio ID table matches `SERIO_RS232` plus `SERIO_DYNAPRO`. Connect allocates state and input, sets ABS_X/ABS_Y ranges 0..0x3ff, opens the serio port, and registers input. Each interrupt stores a byte at `idx`, verifies the first buffered byte has the start bit, and resets `idx` after a complete report.

State and persistence: all state is transient packet assembly and input device registration. No hardware configuration, persistent storage, or PM behavior exists.

Dependencies and integration points: it depends on the serio subsystem, input single-touch ABS/key APIs, and external line-discipline or inputattach configuration to create a matching serio device.

Risks: synchronization is minimal: a bad first byte is logged but `idx` is not reset unless `dynapro_process_data()` completes, so repeated garbage could keep overwriting the same first byte path. The touch bit is reported as the raw masked value rather than normalized boolean, which input handles as nonzero but is less explicit. There is no checksum.

Test signals: feed aligned and misaligned three-byte packets, verify coordinate extraction, touch/release reports, serio open/register failure unwinds, and disconnect lifetime with `input_get_device()`/`input_put_device()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/dynapro.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/edt-ft5x06.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/edt-ft5x06.c

Purpose: `edt-ft5x06.c` is a full-featured I2C driver for EDT Polytouch and FocalTech FT5x06-family controllers. It supports several firmware variants (`EDT_M06`, `EDT_M09`, `EDT_M12`, `EV_FT`, and generic FT), multitouch reporting, regulator/GPIO sequencing, sysfs tunables, optional debugfs factory raw-data capture, and suspend modes.

Important APIs, types, and functions: `struct edt_ft5x06_ts_data` owns I2C/regmap state, input, touchscreen properties, regulators `vcc`/`iovcc`, reset/wake GPIOs, version-specific register addresses, tunable values, model strings, touch-data layout, debugfs buffers, and error counters. `edt_M06_i2c_read()`/`edt_M06_i2c_write()` implement the custom M06 protocol and CRC handling. `edt_ft5x06_ts_isr()` reads touch frames via regmap and reports MT slots by contact ID. Sysfs attribute helpers expose `gain`, `offset`, `threshold`, `report_rate`, model, firmware version, and M06 error counters. Debugfs helpers switch M06 factory/work modes and read raw matrix data. Identification and configuration are handled by `edt_ft5x06_ts_identify()`, `edt_ft5x06_ts_set_regs()`, `edt_ft5x06_ts_get_defaults()`, and `edt_ft5x06_ts_get_parameters()`.

Control flow: probe creates an initial regmap, looks up chip data for max touch points, enables I/O and core regulators in the required order, acquires reset/wake GPIOs, selects suspend mode, toggles wake/reset, allocates input, identifies firmware/model, possibly replaces regmap with an M06-specific one, reads/apply default parameters, optionally clamps/writes report rate, initializes MT slots, requests a threaded IRQ with DT trigger fallback, registers input, and prepares debugfs. IRQ reads the controller's current touch data frame, skips reserved/up events, handles M06 and EV_FT layout quirks, reports positions through `touchscreen_report_pos()`, and emits pointer emulation.

State and persistence: runtime state includes cached tunables, factory-mode flag, raw debug buffer, model/fw strings, touch layout fields, and cumulative CRC/header error counters. Tunables are written to controller registers and restored after power-off resume, but the driver does not persist them in nonvolatile storage. Suspend either does nothing, enters hibernate through PMOD, or powers off regulators with reset asserted depending on available GPIOs.

Dependencies and integration points: it depends on I2C, regmap including custom bus callbacks, regulator framework, GPIO descriptors, input MT, touchscreen properties, sysfs groups, debugfs, OF/I2C IDs for many chip variants, and asynchronous probe preference.

Risks: identification is heuristic for generic FT firmware and can select approximate register maps. Factory mode disables IRQ and allocates a potentially large raw buffer (`num_x * num_y * sizeof(u16)`). Some register writes/readbacks ignore errors in parameter fetch/restore. Touch IDs are used as MT slots and depend on firmware staying within `max_support_points`. Power-off suspend disables IRQ because the line may float; resume must restore registers correctly.

Test signals: verify each supported compatible/ID maps to correct max points, M06 CRC/header error paths, sysfs value bounds and factory-mode rejection, debugfs factory/work mode transitions, raw-data read sizing, report-rate clamping, regulator/GPIO reset timing, hibernate and power-off suspend/resume, EV_FT swapped coordinates, M06 bogus down event filtering, and multi-contact slot release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/edt-ft5x06.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/eeti_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/eeti_ts.c

Purpose: `eeti_ts.c` is an I2C driver for EETI touchscreen panels using the simple six-byte EETI report protocol. It reports single-touch X/Y, optional pressure, and `BTN_TOUCH`, with support for an optional attention GPIO.

Important APIs, types, and functions: `struct eeti_ts` stores the I2C client, input device, optional `attn` GPIO, touchscreen properties, mutex, and running flag. `eeti_ts_read()` receives six bytes and passes motion packets to `eeti_ts_report_event()`. `eeti_ts_report_event()` derives coordinate resolution from AD bits, normalizes coordinates to 11 bits, reports pressure if present, applies touchscreen properties, and syncs. `eeti_ts_isr()` drains events while running and while the attention GPIO remains asserted. `eeti_ts_start()`/`eeti_ts_stop()` control IRQ enablement for input open/close and PM.

Control flow: probe allocates state/input, sets ABS_X/Y/pressure ranges, parses touchscreen properties, obtains optional attention GPIO, requests a threaded IRQ, stops the device by disabling IRQ, and registers input. Open enables IRQ and optionally performs a catch-up read if the attention line is already asserted. Suspend stops the device if input is enabled and optionally enables IRQ wake; resume reverses that.

State and persistence: only `running` and the IRQ enable state persist during runtime. The mutex serializes ISR reads and start catch-up. There are no persistent settings or firmware operations.

Dependencies and integration points: it depends on I2C `i2c_master_recv()`, optional GPIO descriptor `attn`, input touchscreen properties, IRQ wake handling, and compatible `eeti,exc3000-i2c` for this older protocol path.

Risks: absent attention GPIO means the ISR reads exactly once and relies on level-triggered IRQ behavior for further data. The stop path disables IRQ after only a write memory barrier and does not wait for the threaded handler beyond IRQ core semantics. The driver cannot probe the device actively and trusts platform description.

Test signals: validate packet resolution normalization, pressure-present and pressure-absent reports, attention GPIO drain loop, open catch-up read after missed edge, suspend/resume wake IRQ behavior, and read-short/error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/eeti_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts.c

Purpose: `egalax_ts.c` is an I2C multitouch driver for EETI eGalax controllers. It handles the controller's 10-byte report packets, supports five contact slots, wakes the controller through a GPIO edge, and sends a firmware-version query during probe.

Important APIs, types, and functions: `struct egalax_ts` holds the I2C client and input device. `egalax_ts_interrupt()` retries `i2c_master_recv()` on `-EAGAIN`, filters non-multitouch report modes, decodes state, ID, down/up, X/Y/Z, and reports one MT slot update. `egalax_wake_up_device()` temporarily requests the `wakeup` GPIO as high, drives it low, switches it to input, and releases it. `egalax_firmware_version()` sends a fixed vendor command. PM callbacks send suspend command or wake through GPIO.

Control flow: probe allocates state/input, wakes the controller, sends the firmware command, initializes ABS and MT parameters, requests a oneshot threaded IRQ, and registers input. Each IRQ handles one point event and uses `input_mt_report_pointer_emulation()` after slot update. Suspend either enables IRQ wake or sends a 10-byte sleep command; resume disables wake or toggles the wakeup GPIO.

State and persistence: no persistent state is kept beyond input slots. The wakeup GPIO is not retained; it is requested only when a falling edge is needed. Firmware version is requested but not parsed or exposed.

Dependencies and integration points: it depends on I2C, GPIO descriptor `wakeup`, input MT, IRQ wake, OF compatible `eeti,egalax_ts`, and platform IRQ configuration.

Risks: only one contact update is present per packet, so correctness depends on controller sending all slot state changes. Slot ID validation uses `id > MAX_SUPPORT_POINTS`, allowing ID 5 while slots were initialized for IDs 0..4. Pressure `z` is decoded but no ABS_MT_PRESSURE parameter is initialized/reported. The firmware command return only confirms send success.

Test signals: test wake GPIO pulse, firmware command send, EAGAIN retry limit, ignoring mouse/vendor reports, valid/invalid ID handling, MT slot down/up transitions, suspend command, and wake-capable IRQ behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts_serial.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts_serial.c

Purpose: `egalax_ts_serial.c` is a serio driver for EETI eGalaxTouch serial touchscreens. It decodes five- or six-byte packets and reports single-touch absolute coordinates plus `BTN_TOUCH`.

Important APIs, types, and functions: `struct egalax` stores input, serio, packet index, six-byte buffer, and physical path. `egalax_interrupt()` accumulates bytes, validates the first byte start bit, chooses packet length based on the pressure bit, and calls `egalax_process_data()`. `egalax_process_data()` derives coordinate resolution from header bits, masks high coordinate bits, combines them with 7-bit low bytes, shifts to the declared 0..0x4000 range, reports touch and X/Y, and syncs. Connect/disconnect implement the usual serio lifecycle.

Control flow: the driver matches `SERIO_RS232` plus `SERIO_EGALAX`. Connect allocates state/input, sets EV_KEY/EV_ABS capabilities and 0..0x4000 ranges, opens serio, and registers input. Runtime interrupts parse frames; malformed start bytes reset the packet index.

State and persistence: only packet assembly state is held. There is no PM, configuration, pressure reporting, or persistence.

Dependencies and integration points: it depends on serio, input single-touch APIs, and external attachment of an eGalax protocol serio port.

Risks: packets with the pressure bit are accepted as six bytes but pressure data is ignored. There is no checksum. If a new start byte appears mid-frame with bit 7 set, it is stored as payload until the length completes rather than resynchronizing immediately.

Test signals: feed 5-byte and 6-byte frames with different resolution bits, verify coordinate scaling and touch bit, validate malformed start reset, connect failure unwinds, and disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/egalax_ts_serial.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ektf2127.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ektf2127.c

Purpose: `ektf2127.c` is an I2C multitouch driver for ELAN eKTF2127/eKTF2132/eKTF2232 controllers. It powers the controller with a GPIO, queries panel dimensions, handles two report formats, and reports up to five direct MT contacts.

Important APIs, types, and functions: `struct ektf2127_ts` holds the I2C client, input, power GPIO, touchscreen properties, and chip-specific status-bit shift. `ektf2127_parse_coordinates()` decodes the 5-touch report format. `ektf2127_report_event()` assigns slots by position using `input_mt_assign_slots()`. `ektf2127_report2_event()` handles a two-contact format with active bits in a status byte and chip-specific `status_shift`. `ektf2127_irq()` reads 21-byte packets and dispatches headers for report, noise, hello, calibration done, or unexpected data. `ektf2127_query_dimension()` sends request packets for width/height and parses responses.

Control flow: probe requires an IRQ, requests the `power` GPIO high, allocates input, reads and ignores an initial hello, queries max X/Y from the chip, configures ABS ranges and touchscreen properties, initializes five MT slots with direct/drop-unused/track flags, obtains match data, requests a threaded IRQ, stops the device until open, registers input, and stores client data. Open enables IRQ and drives power high; close disables IRQ and drives power low. PM wraps open/close behavior while holding the input mutex.

State and persistence: runtime state is power GPIO level, IRQ enabled state, and MT slots. No calibration data or firmware state is persisted. The queried dimensions configure input for this boot.

Dependencies and integration points: it depends on I2C, a mandatory `power` GPIO, threaded IRQs, OF/I2C match data for status shifts, and touchscreen DT properties for orientation correction.

Risks: power control is tied to input open/close; some hardware may need longer settle delays than the initial probe delay. Dimension query assumes a fixed four-byte response and subtracts one from parsed max. Report2 supports only two slots even though the driver initializes five. The IRQ handler reads a full 21-byte packet for every header, including shorter informational packets.

Test signals: test width/height queries, all three compatible IDs and status shifts, report and report2 packet decoding, noisy/hello/calibration packets, open/close power transitions, suspend/resume with input enabled, and over-count clamping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ektf2127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/elants_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/elants_i2c.c

Purpose: `elants_i2c.c` is a broad I2C driver for Elan touch panels (`EKTH3500` and `EKTF3624`). It initializes hardware, queries firmware/hardware and geometry data, reports 10-contact multitouch packets, exposes sysfs calibration/firmware-update/version attributes, handles recovery/IAP mode, and manages regulators/reset GPIO through suspend/resume.

Important APIs, types, and functions: `struct elants_data` owns I2C/input state, regulators `vcc33`/`vccio`, reset GPIO, version and geometry fields, touchscreen properties, driver state (`ELAN_STATE_NORMAL`, wait queue header, recalibration), chip ID, IAP mode, sysfs mutex, command completion, suspend power policy, and a DMA-safe packet buffer. Command helpers include `elants_i2c_send()`, `elants_i2c_read()`, and `elants_i2c_execute_command()`. Initialization includes software reset, fastboot, hello/recovery detection, version queries, and chip-specific geometry queries. Firmware update is implemented by `elants_i2c_fw_update()` and `elants_i2c_do_update_firmware()` using 132-byte pages and optional Remark ID validation. Event handling is in `elants_i2c_irq()`, `elants_i2c_event()`, and `elants_i2c_mt_event()`.

Control flow: probe rejects ACPI devices that are really I2C-HID, checks I2C functionality, allocates state, obtains regulators and reset GPIO, powers on if reset is available, verifies a device responds, initializes the controller, allocates/configures input using queried resolution/physical size, registers input, requests a threaded IRQ with trigger fallback, and returns. IRQ reads up to 169 bytes, handles recalibration completions, queue wait headers, single/normal multi-report frames, old/new EKTF3624 report formats, and command/hello responses. Suspend disables IRQ and either leaves wake-capable devices in idle, sends sleep while keeping power, or powers off. Resume resets/sends active/powers on and reinitializes as appropriate.

State and persistence: the driver maintains extensive volatile metadata and exposes firmware update/calibration actions through sysfs. Firmware update writes controller flash and is persistent on the device. Calibration is initiated and verified by response, with count readable through sysfs. `iap_mode` records operational versus recovery state and affects update flow.

Dependencies and integration points: it depends on I2C, firmware loader, regulators, reset GPIO, ACPI/OF/I2C matching, PM wake IRQ behavior, input MT, touchscreen properties, sysfs groups, and UUID DSM checks to avoid binding I2C-HID devices.

Risks: firmware update is high risk: it disables IRQ, validates firmware size but relies on hardware ACKs and optional Remark ID rules, and persistent flash writes can leave recovery mode on failure. Initialization deliberately returns success even if it sets recovery mode, so later functionality depends on sysfs update. Packet parsing supports multiple queue formats and must avoid stuck contacts; checksum mismatch only warns and drops event. Suspend can return `-EBUSY` in recovery mode. `elants_version_attribute_show()` dereferences `u16 *` from struct storage without endian conversion, acceptable locally but architecture-sensitive for display.

Test signals: test normal and recovery hello paths, all version queries, EKTH and EKTF geometry calculations, old/new report formats, queue wait/normal multi-report sequences, checksum rejection, calibration sysfs completion and timeout, firmware update success/failure/recovery flows, ACPI I2C-HID refusal, power-off and keep-power suspend/resume, and wake-capable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/elants_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/elo.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/elo.c

Purpose: `elo.c` is a serio driver for several Elo serial touchscreen protocols: 10-byte standard E271-2210, 6-byte legacy E281A-4002, 4-byte legacy E271-140, and 3-byte legacy E261-280. It reports single-touch ABS coordinates, `BTN_TOUCH`, and optional pressure.

Important APIs, types, and functions: `struct elo` stores input/serio, a command mutex, command completion, protocol ID, packet parser state, expected packet type, checksum, data buffer, response buffer, and physical path. `elo_process_data_10()`, `elo_process_data_6()`, and `elo_process_data_3()` parse the three supported protocol families. `elo_command_10()` sends 10-byte protocol commands with lead byte and checksum, waits for response/ACK, and copies response data. `elo_setup_10()` queries controller identity and configures pressure capability/ranges. `elo_connect()` selects parser setup based on `serio->id.id`.

Control flow: connect allocates state/input, opens serio, and for ID 0 sends an identity command before registering input; legacy IDs configure fixed ranges directly. Runtime `elo_interrupt()` dispatches each byte to the parser for the selected protocol. The 10-byte parser verifies lead byte, checksum, and expected packet type, reports touch packets, completes ACKs, and stores command responses.

State and persistence: parser state persists across bytes; 10-byte command state is synchronized by `cmd_mutex`, `cmd_done`, `expected_packet`, and `response`. The driver does not persist settings on hardware.

Dependencies and integration points: it depends on serio protocol `SERIO_ELO`, input APIs, `serio_pause_rx` scoped guard for command setup, and external serial attachment.

Risks: older protocols have limited validation and no checksums. The 10-byte command path waits one second but does not inspect the timeout result directly; it infers failure from `expected_packet`. The connect comment incorrectly mentions Gunze. ABS ranges are hard-coded and may not match every panel.

Test signals: test each protocol ID, 10-byte checksum and unexpected packet handling, ACK/identity command completion, pressure-capable standard devices, legacy pressure byte handling, 3-byte touch polarity, connect failure cleanup, and serial resynchronization after bad bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/elo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/exc3000.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/exc3000.c

Purpose: `exc3000.c` is an I2C multitouch driver for EETI EXC3000/EXC80Hxx/EXC81W32 controllers. It reports up to ten direct MT slots, supports model/firmware/type sysfs queries through vendor requests, and uses a timer to release contacts if a multi-frame read fails.

Important APIs, types, and functions: `struct exc3000_data` stores the client, device info, input, touchscreen properties, optional reset GPIO, release timer, two-frame buffer, vendor-event completion, and query mutex. `exc3000_read_frame()` sends a two-byte request and reads a 66-byte frame with length validation. `exc3000_handle_mt_event()` handles one or two frames depending on total slot count and reports contacts through `exc3000_report_slots()`. `exc3000_vendor_data_request()` sends a 68-byte vendor request, waits for the interrupt path to complete `wait_event`, and copies response data. Sysfs attributes expose firmware version, model, and type.

Control flow: probe selects device info from OF/ACPI/I2C ID, initializes timer/completion/mutex, asserts optional reset, enables optional `vdd`, releases reset after delays, allocates/registers input with device-specific max coordinate range, installs timer shutdown action, requests IRQ, then retries a model vendor query up to three times before storing client data. Interrupts read a frame and either complete vendor requests or process MT events. For more than five contacts, a second frame must follow with contact count zero.

State and persistence: state is transient input slots, vendor query completion, and a timer that syncs/release slots after errors. There is no persistent configuration or firmware update. Sysfs queries are live vendor requests.

Dependencies and integration points: it depends on I2C, optional reset GPIO, optional `vdd` regulator, input MT, touchscreen properties, sysfs device groups, OF/ACPI/I2C matching, and timer shutdown devm action.

Risks: probe registers input before IRQ request and before model query completion, so failures after input registration rely on devm/input cleanup. Vendor request completion uses the same data buffer as touch IRQs and is serialized only by `query_lock`, not against touch events. The error timer releases contacts only by syncing an empty MT frame after timeout, so users may see delayed releases. `i2c_master_send(client, "'", 2)` sends two bytes from a string literal including the NUL terminator, which is intentional-looking but nonobvious.

Test signals: validate single-frame and two-frame touch reports, invalid total slot handling and timer release, vendor sysfs requests, bootloader/app firmware version branch, reset/regulator sequencing, probe retry behavior, ACPI/OF device info selection, and malformed frame length rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/exc3000.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/fsl-imx25-tcq.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/fsl-imx25-tcq.c

Purpose: `fsl-imx25-tcq.c` is a platform input driver for the Freescale i.MX25 Touchscreen Conversion Queue connected to the i.MX25 ADC. It programs ADC queue items for a 4-wire resistive touchscreen, handles pen-detect/FIFO interrupts, averages samples, and reports single-touch X/Y.

Important APIs, types, and functions: `struct mx25_tcq_priv` holds queue and core regmaps, input device, mode, thresholds/timings, clock, IRQ, and device pointer. `imx25_setup_queue_cfgs()` programs ADC configurations for precharge, touch detect, X measurement, and Y measurement. `imx25_setup_queue_4wire()` lays out the queue and computes expected sample count. IRQ control helpers mask/unmask pen and FIFO IRQs, force queue start/stop, and reset FIFO. `mx25_tcq_create_event_for_4wire()` interprets FIFO samples and reports down/up/bounce. `mx25_tcq_irq()` is the top half and `mx25_tcq_irq_thread()` drains FIFO samples. `mx25_tcq_init()` computes debounce/settling counts from the ADC clock and programs queue control.

Control flow: probe maps the queue registers, parses DT (`fsl,wires` plus optional threshold/debounce/settling), creates a regmap, gets IRQ, allocates input, obtains parent TSADC core registers and clock, requests a threaded IRQ, and registers input. Input open enables the clock, initializes the queue, and arms touch detection. On pen detect, the top half masks pen IRQ, starts the queue, and enables FIFO IRQ. On FIFO ready, the thread reads aligned sample groups, validates pre/post touch measurements against the threshold, reports averaged coordinates or release, and either continues sampling or re-enables touch detection.

State and persistence: runtime state is programmed into memory-mapped ADC/TS registers and the clock enable state. No persistent configuration exists beyond DT defaults. Open/close gates the hardware clock and IRQ masks.

Dependencies and integration points: it depends on the i.MX25 TSADC MFD parent for `regs` and `clk`, MMIO regmap, OF compatible `fsl,imx25-tcq`, Linux input single-touch APIs, and platform resources.

Risks: only 4-wire mode is supported. FIFO sample grouping assumes counts are multiples of `sample_count` and drops partial groups. Invalid FIFO item IDs discard the whole event. Timing calculations depend on clock rate and can clamp silently at hardware limits. Parent TSADC data must be present and valid.

Test signals: validate DT parsing, unsupported wire count rejection, clock enable/disable, queue register programming, pen detect to FIFO interrupt transition, averaged coordinate reporting, release threshold behavior, bounce sampling continuation, FIFO overflow/underrun recovery, and close while queue is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/fsl-imx25-tcq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/fujitsu_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/fujitsu_ts.c

Purpose: `fujitsu_ts.c` is a serio driver for Fujitsu RS-232 serial touchscreens. It decodes five-byte packets and reports single-touch X/Y plus `BTN_TOUCH`.

Important APIs, types, and functions: `struct fujitsu` contains the input device, serio port, packet index, five-byte buffer, and physical path. `fujitsu_interrupt()` implements packet synchronization and decoding. `fujitsu_connect()`/`fujitsu_disconnect()` allocate, register, and tear down the serio/input device pair.

Control flow: the serio ID table matches `SERIO_RS232` with protocol `SERIO_FUJITSU`. Connect allocates state/input, sets BUS_RS232 IDs and 0..4096 ABS ranges, opens the serio port, and registers input. In the interrupt parser, byte 0 must have high nibble `0x80`; later bytes must not have bit 7 set. Once five bytes arrive, X and Y are decoded from two 7-bit bytes each, touch is reported as true unless the low two status bits equal `2`, the event is synced, and the packet index resets.

State and persistence: only the current packet buffer/index and registered input state exist. There are no hardware commands, persistent settings, or PM hooks.

Dependencies and integration points: it depends on serio, input single-touch APIs, and external serial attachment via the Fujitsu protocol ID.

Risks: there is no checksum, so valid-looking corrupted packets can be reported. The first status byte contains calibration/correction/button information, but only the low two bits are used for touch state. Mid-frame bytes with bit 7 set reset the parser and drop the byte rather than treating it as a new start byte.

Test signals: feed valid five-byte packets, garbage before start, high-bit payload resync cases, touch status values, coordinate max ranges, connect unwind paths, and disconnect lifetime handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/fujitsu_ts.c -->
