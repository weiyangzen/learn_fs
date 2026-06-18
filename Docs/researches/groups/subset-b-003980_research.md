# subset-b-003980 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c

Purpose: platform input driver for the iPAQ H3600 Atmel micro companion touchscreen subdevice. It exposes the companion chip's touchscreen messages as a simple single-touch `input_dev` with `ABS_X`, `ABS_Y`, and `BTN_TOUCH` ranges fixed to 0..1023.

Important APIs/types/functions: `struct touchscreen_data` stores the input device and parent `struct ipaq_micro`. `micro_ts_receive()` is the registered MFD callback and decodes 4-byte big-endian coordinate reports or zero-length release reports. `micro_ts_toggle_receive()` installs or removes `micro->ts` and `micro->ts_data` under `micro->lock`. `micro_ts_open()`, `micro_ts_close()`, `micro_ts_suspend()`, and `micro_ts_resume()` control callback registration, while `micro_ts_probe()` allocates and registers the input device.

Control flow: probe obtains the parent `ipaq_micro`, allocates state and input device, sets capabilities, registers the device, and stores driver data. The input open path enables message delivery; each MFD touchscreen message reports coordinates and touch state, then syncs. Close and suspend unregister the callback; resume reacquires the input mutex and only re-enables delivery when userspace has the input device open.

State and persistence: there is no persistent storage. Runtime state is limited to the input device and callback pointers in the shared `ipaq_micro` object. The callback pointer lifetime is protected by a spinlock, while input open/suspend coordination uses the input core mutex on resume.

Dependencies/integration: depends on the `ipaq-micro` MFD parent for transport and locking, Linux input core, platform driver binding `ipaq-micro-ts`, PM helpers, and big-endian coordinate decoding.

Risks and test signals: callback deregistration must race safely with parent MFD message dispatch and suspend. Test open/close cycles, suspend while open, resume while closed, zero-length release frames, malformed nonzero lengths, and removal of the parent MFD while the input node is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ipaq-micro-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs5xx.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs5xx.c

Purpose: I2C input driver for Azoteq IQS550, IQS572, and IQS525 projected-capacitance trackpad/touchscreen controllers. It initializes normal runtime mode, reports up to five multitouch contacts, exposes firmware/version information, and can flash vendor-exported firmware into device nonvolatile memory through a sysfs `fw_file` control.

Important APIs/types/functions: key structures are `iqs5xx_private`, `iqs5xx_dev_id_info`, `iqs5xx_status`, and `iqs5xx_touch_data`. Register access is via `iqs5xx_read_burst()`, `iqs5xx_read_word()`, `iqs5xx_write_burst()`, `iqs5xx_write_word()`, and `iqs5xx_write_byte()`, all aware of the device's communication-window behavior. Bootloader and firmware paths are `iqs5xx_reset()`, `iqs5xx_bl_cmd()`, `iqs5xx_bl_open()`, `iqs5xx_bl_write()`, `iqs5xx_bl_verify()`, `iqs5xx_fw_file_parse()`, `iqs5xx_update_firmware()`, and `iqs5xx_fw_file_write()`. Runtime/input paths include `iqs5xx_axis_init()`, `iqs5xx_dev_init()`, `iqs5xx_irq()`, `iqs5xx_open()`, `iqs5xx_close()`, `fw_info_show()`, and PM suspend/resume.

Control flow: probe allocates state, gets optional reset GPIO, initializes the device, then requests a threaded IRQ. Initialization reads product/version data, handles older A000 devices by opening the bootloader, reads export-file version, initializes input axes from controller resolution and touchscreen properties, acknowledges reset, enables watchdog/ATI/touch event mode, ends communication, and waits for ATI to complete. The IRQ handler reads a full status frame, reinitializes after unexpected reset, reports active slots using pressure, closes the communication window with `END_COMM`, and delays for RDY deassertion. Firmware update parses a nonstandard Intel HEX export, enters or opens bootloader mode, writes the parameter map in 64-byte blocks, asks the bootloader for CRC, verifies the custom area, resets, reinitializes, and registers input if the controller was previously bootloader-only.

State and persistence: runtime state tracks input device, reset GPIO, touchscreen transform properties, mutex, version/export metadata, and bootloader status. Firmware flashing changes controller nonvolatile memory; the driver treats `dev_id_info.bl_status == 0` as bootloader mode and hides some sysfs attributes when update is unsupported. Suspend/resume and open/close only write the runtime state register if the firmware is running.

Dependencies/integration: integrates with I2C, GPIO reset, firmware loader, sysfs device groups, Linux multitouch input, touchscreen property parsing, threaded IRQs, and OF/I2C IDs `azoteq,iqs550`, `azoteq,iqs572`, and `azoteq,iqs525`.

Risks and test signals: communication-window retry timing is central and should be tested on I2C adapters with and without clock-stretch tolerance. Firmware parsing tolerates vendor checksum quirks only for custom records; test malformed record sizes, EOF handling, out-of-range addresses, reset-less devices, A000 bootloader conversion, IRQs during forced bootloader entry, failed CRC/verify, and registration after successful firmware update. Runtime tests should cover unexpected reset reinitialization, suspend/resume while open, hidden sysfs attributes, touchscreen-size values at `0xffff`, and five-slot tracking with pressure zero releases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs5xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs7211.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs7211.c

Purpose: I2C driver for Azoteq IQS7210A, IQS7211A, and IQS7211E trackpad/touchscreen controllers. It converts devicetree/fwnode properties into controller register fields, configures communication mode, creates optional key and trackpad input devices, and reports two-contact multitouch plus gesture/button/ALP key events.

Important APIs/types/functions: device differences are encoded in `struct iqs7211_dev_desc` and `iqs7211_devs[]`; property-to-register mapping uses `struct iqs7211_prop_desc`, `iqs7211_props[]`, `struct iqs7211_reg_field_desc`, and the `reg_field_head` list. Event capability tables are `iqs7210a_kp_events`, `iqs7211a_kp_events`, and `iqs7211e_kp_events`. Core helpers include `iqs7211_hard_reset()`, `iqs7211_force_comms()`, `iqs7211_read_burst()`, `iqs7211_write_burst()`, `iqs7211_start_comms()`, `iqs7211_init_device()`, `iqs7211_parse_props()`, `iqs7211_parse_event()`, `iqs7211_parse_cycles()`, `iqs7211_parse_tp()`, `iqs7211_parse_alp()`, `iqs7211_parse_reg_grp()`, `iqs7211_register_kp()`, `iqs7211_register_tp()`, and `iqs7211_report()`.

Control flow: probe identifies the matched variant, opens the RDY GPIO as a pollable GPIO and IRQ source, shares RDY/MCLR for IQS7211E-style hardware when required, starts communication, reads version/export/trackpad configuration, parses top-level and child fwnodes for system, trackpad, button, ALP, gesture, keycode, RX/TX, and channel-cycle properties, registers requested input devices, writes synthesized register fields, starts ATI, and requests a threaded IRQ. Read/write helpers first wait for or force a communication window and retry on RDY races or `0xeeee` error words. IRQ reporting reads status/contact words, reinitializes after reset flags, logs ATI errors, reports multitouch slots, emits ALP/button states, tracks persistent hold/palm gesture bits in `gesture_cache`, and releases momentary gestures immediately.

State and persistence: persistent hardware configuration comes from firmware OTP defaults plus fwnode-specified register writes; the driver writes runtime controller registers at probe and after unexpected reset. Runtime state includes communication mode initialization/current mode, event mask, ATI start mask, parsed field list, RX/TX map, cycle allocations, export/version data, keycodes, contact count, touchscreen properties, and gesture cache. No host-side storage is written.

Dependencies/integration: depends on I2C, GPIO descriptors, `readx_poll_timeout`, fwnode/device property APIs, OF match data, input key and multitouch core, touchscreen common properties, sysfs `fw_info`, PM sleep ops, and the binding-compatible strings `azoteq,iqs7210a`, `azoteq,iqs7211a`, and `azoteq,iqs7211e`.

Risks and test signals: the largest risk is configuration synthesis: invalid register masks, duplicate channel assignments, unsupported properties for a variant, or incorrect forced-communication defaults can leave the controller unreachable. Test each compatible with and without reset GPIO, shared RDY/MCLR, forced-comms and clock-stretch paths, all child nodes, invalid RX/TX/channel arrays, `azoteq,num-contacts` absent/zero/two, gesture keycode mappings, hold/palm cache release behavior, unexpected reset reinitialization, ATI error flags, wakeup-source suspend behavior, and sysfs version formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/iqs7211.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c

Purpose: platform input driver for HP Jornada 710/720/728 touchscreens. It uses Jornada-specific SSP helper routines and a pen-up GPIO interrupt to sample three X and Y readings, average them, and report a resistive single-touch input device.

Important APIs/types/functions: `struct jornada_ts` stores the input device, pen GPIO, and sample buffers. `jornada720_ts_collect_data()` reads the low and packed high bits for three X and three Y samples from `jornada_ssp_byte()`. `jornada720_ts_average()` reconstructs and averages three 10-bit samples. `jornada720_ts_interrupt()` handles pen-up/down detection and sampling. `jornada720_ts_probe()` sets up GPIO, IRQ, absolute ranges, and input registration.

Control flow: probe obtains the `penup` GPIO, maps it to an IRQ, allocates the input device, requests a rising-edge IRQ, and registers the device. On interrupt, a high GPIO means pen up and emits `BTN_TOUCH=0`. Otherwise the driver starts SSP, sends `GETTOUCHSAMPLES`, verifies the dummy reply, collects and averages samples, reports touch coordinates, then ends SSP.

State and persistence: state is only current sample arrays and GPIO/input handles. There is no saved calibration or firmware state; fixed min/max ranges encode expected board calibration.

Dependencies/integration: depends on `mach/jornada720.h` board APIs (`jornada_ssp_start`, `jornada_ssp_inout`, `jornada_ssp_byte`, `jornada_ssp_end`), GPIO consumer API, platform binding `jornada_ts`, and Linux input core.

Risks and test signals: this is tightly board-specific and assumes SSP serialization is handled by the Jornada helpers. Test pen-up GPIO polarity, rising-edge-only release IRQ behavior, SSP failure/dummy response mismatch, high-bit reconstruction, fixed axis ranges against calibration, repeated pen-down samples if no falling-edge IRQ is present, and module coldplug aliasing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/jornada720_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c

Purpose: platform driver for the NXP LPC32xx built-in resistive touchscreen controller. It programs the controller for automatic four-sample X/Y acquisition, reports single-touch coordinates through the input core, and manages controller clocking on open/close and suspend/resume.

Important APIs/types/functions: `struct lpc32xx_tsc` holds input, MMIO base, IRQ, and clock. `tsc_readl()`/`tsc_writel()` wrap raw MMIO. `lpc32xx_fifo_clear()`, `lpc32xx_ts_interrupt()`, `lpc32xx_setup_tsc()`, `lpc32xx_stop_tsc()`, `lpc32xx_ts_open()`, `lpc32xx_ts_close()`, `lpc32xx_ts_probe()`, `lpc32xx_ts_suspend()`, and `lpc32xx_ts_resume()` make up the lifecycle.

Control flow: probe maps registers, gets the clock, allocates input, requests IRQ, registers input, and marks the device wake-capable. Open enables the clock, configures FIFO threshold/sample size/timing/ranges, clears stale FIFO entries, and enables automatic capture. The IRQ handler detects FIFO overrun, otherwise pops up to four samples, normalizes inverted 10-bit X/Y values, and reports the average of samples 2 and 3 if the fourth sample still says pen-down; otherwise it reports release. Close disables auto mode and the clock. PM either enables IRQ wake or stops/restarts the controller depending on wake capability.

State and persistence: the only persistent host state is device handles and whether the input device is enabled. Hardware registers are reprogrammed on every open/resume. FIFO contents are intentionally discarded on overflow and setup.

Dependencies/integration: integrates with platform resources, MMIO, clock framework, OF compatible `nxp,lpc3220-tsc`, Linux input, IRQ wake, and LPC32xx controller register layout.

Risks and test signals: the handler reads `rv[3]` even when fewer than four samples were collected, so pen-up short FIFO paths should be scrutinized. Test clock enable failure, FIFO overrun clearing, coordinate inversion/range, suspend with no users, wake-enabled suspend, register timing values, and IRQ behavior under noisy pen-up transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/lpc32xx_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c

Purpose: Mainstone/PXA machine-ops driver for accelerated continuous touchscreen sampling on Wolfson WM9705, WM9712, and WM9713 AC97 codecs. It plugs board-specific continuous-sampling callbacks into the generic `wm97xx` touchscreen driver.

Important APIs/types/functions: `struct continuous` and `cinfo[]` map codec IDs and requested `cont_rate` to codec continuous-mode codes and per-tick read counts. Module parameters `cont_rate`, `pen_int`, `pressure`, and `ac97_touch_slot` tune sampling, pen IRQ usage, pressure reads, and AC97 slot. Machine callbacks are `wm97xx_acc_pen_up()`, `wm97xx_acc_pen_down()`, `wm97xx_acc_startup()`, and `wm97xx_acc_shutdown()`, collected in `mainstone_mach_ops`. Probe/remove call `wm97xx_register_mach_ops()` and `wm97xx_unregister_mach_ops()`.

Control flow: startup validates the AC97 codec, chooses the nearest supported continuous speed, sets `wm->acc_rate` and slot, optionally obtains a touch GPIO and maps it as a pen IRQ, and configures WM9712/WM9713 codec GPIOs. During pen-down sampling, the driver drains AC97 MODR values, validates ADC selector tags for X/Y/pressure, reports coordinates and pressure, and returns `RC_PENDOWN | RC_AGAIN` until samples become stale or invalid. Pen-up flushes the AC97 slot FIFO differently for PXA27x and PXA3xx.

State and persistence: global module state stores selected speed index, optional GPIO descriptor, and module parameters. Runtime device state is held by the generic `wm97xx` object; no nonvolatile state is changed.

Dependencies/integration: depends on generic `wm97xx` input infrastructure, PXA AC97 helpers, PXA CPU detection, codec GPIO configuration, optional GPIO-backed pen IRQ, and platform driver name `wm97xx-touch`.

Risks and test signals: globals make multiple codec instances questionable. Test fallback from missing pen GPIO to polling, codec-specific GPIO setup, pressure disabled/enabled paths, stale sample detection through static `last/tries`, AC97 slot selection, PXA27x/PXA3xx FIFO flushes, and cleanup of `gpiod_irq` after startup failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mainstone-wm97xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/max11801_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/max11801_ts.c

Purpose: I2C driver for the Maxim MAX11801 resistive touchscreen controller in FIFO auto mode. It configures averaging/aperture/timing registers and reports single-touch X/Y plus `BTN_TOUCH`.

Important APIs/types/functions: `struct max11801_data` stores client and input device. `read_register()` and `max11801_write_reg()` wrap SMBus byte access with the controller's shifted register address convention. `max11801_ts_phy_init()` programs measurement averaging, setup, pullup, auto-mode period, aperture, and operation mode. `max11801_ts_interrupt()` reads status and FIFO data, decodes X/Y measurement tags and event tags, and reports touch or release. `max11801_ts_probe()` sets up input, hardware, threaded IRQ, and I2C/OF IDs.

Control flow: probe allocates state/input, sets fixed 12-bit ranges, initializes hardware immediately, requests a low-triggered threaded IRQ, and registers input. The IRQ handler confirms FIFO interrupt/overflow, reads a four-byte FIFO record, extracts tagged X and Y samples, verifies both half-records share the same event tag, and maps init/middle to touch-down, release to touch-up, and FIFO-end to no report.

State and persistence: no host-side persistent state exists beyond input/client handles. Controller configuration is written at probe and not restored on PM because the driver has no suspend/resume path.

Dependencies/integration: integrates with I2C/SMBus, input core, threaded IRQs, and OF compatible `maxim,max11801`.

Risks and test signals: no power-management or regulator handling means board code must keep the controller powered/configured. Test FIFO overflow handling, event-tag mismatch, invalid/missing X or Y tags, low IRQ polarity, boot-time probe before the chip is ready, and resume from system sleep on boards that power-cycle the controller.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/max11801_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mc13783_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mc13783_ts.c

Purpose: platform input driver for the Freescale MC13783 PMIC touchscreen ADC. It requests the PMIC touchscreen IRQ on input open, performs asynchronous ADC conversions through the `mc13xxx` MFD API, filters samples, and reports single-touch X/Y/pressure.

Important APIs/types/functions: `struct mc13783_ts_priv` stores input, PMIC handle, delayed work, sample array, and platform timing data. `sample_tolerance` controls coordinate rejection. `mc13783_ts_handler()` schedules conversion work. `mc13783_ts_work()` calls `mc13xxx_adc_do_conversion()`. `mc13783_ts_report_sample()` unpacks three X, three Y, and two contact-resistance samples, sorts triplets, filters by tolerance, and reports median coordinates and pressure. Open/close are `mc13783_ts_open()` and `mc13783_ts_close()`.

Control flow: probe requires platform data, allocates input/state, initializes delayed work, and registers the input device. Opening locks the PMIC, requests `MC13XXX_IRQ_TS`, enables touchscreen mode in `MC13XXX_ADC0`, and unlocks. The IRQ schedules immediate work; the work callback performs one conversion and reports a valid sample. While pressure is nonzero, reporting reschedules work at 50 Hz. Closing disables touchscreen mode, frees the PMIC IRQ, unlocks, and cancels work.

State and persistence: runtime state includes current samples and queued delayed work. No nonvolatile state is written, but PMIC ADC mode is modified while the input device is open.

Dependencies/integration: depends on the `mc13xxx`/MC13783 MFD API, platform data `mc13xxx_ts_platform_data`, delayed work, Linux input, and platform alias `mc13783-ts`.

Risks and test signals: delayed work races with close and IRQ teardown are the main lifecycle concern. Test missing platform data, IRQ request failure, ADC conversion failure, tolerance disabled/enabled, noisy coordinates, pressure zero release, repeated scheduling rate, and remove while work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mc13783_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/melfas_mip4.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/melfas_mip4.c

Purpose: I2C driver for MELFAS MIP4 touchscreen controllers. It queries controller identity and geometry, reports multitouch and optional touch keys, exposes firmware/hardware identity through sysfs, and supports sysfs-triggered firmware update using the MIP4 bootloader protocol.

Important APIs/types/functions: main state is `struct mip4_ts`; version/tail data are `struct mip4_fw_version` and packed `struct mip4_bin_tail`. I2C and discovery helpers are `mip4_i2c_xfer()`, `mip4_get_fw_version()`, and `mip4_query_device()`. Power/input paths are `mip4_power_on()`, `mip4_power_off()`, `mip4_enable()`, `mip4_disable()`, `mip4_report_keys()`, `mip4_report_touch()`, `mip4_handle_packet()`, and `mip4_interrupt()`. Firmware paths are `mip4_bl_read_status()`, `mip4_bl_change_mode()`, `mip4_bl_get_address()`, `mip4_bl_program_page()`, `mip4_bl_verify_page()`, `mip4_flash_fw()`, `mip4_parse_firmware()`, `mip4_execute_fw_update()`, and sysfs handlers for `update_fw`, `fw_version`, `hw_version`, `product_id`, and `ic_name`.

Control flow: probe checks plain I2C support, allocates input/state, gets optional chip-enable GPIO, powers the controller long enough to query product, firmware, resolution, node/key counts, protocol format, and event size, then powers it off until opened. It configures input axes, pressure, major/minor, MT slots, keycode storage, and a no-auto-enable threaded IRQ. Opening powers on and enables IRQ; closing disables IRQ, powers off, and clears all input slots/keys. IRQ handling reads packet-info size/alert, reads packet data, decodes each fixed-size packet by event format, reports key or touch events, and syncs. Firmware update requests `melfas_mip4_<product>.fw`, locks the input mutex, disables IRQ or powers on, parses the binary tail, enters bootloader, programs and verifies pages, exits bootloader, power-cycles, requeries device parameters, refreshes axis limits, and restores IRQ/power state.

State and persistence: runtime state caches product/IC names, firmware version, event format/size, geometry, ppm, key count/codes, wake IRQ flag, and a reusable packet buffer. Firmware update writes controller flash. Power state is tied to input open and suspend, with wake IRQ enabled when allowed.

Dependencies/integration: depends on I2C, firmware loader, GPIO CE, optional OF/ACPI IDs (`melfas,mip4_ts`, `MLFS0000`), input MT/key core, threaded IRQs, sysfs attribute groups, and PM wake IRQ support.

Risks and test signals: firmware flashing is high risk: page offsets are absolute into `fw->data`, retries are limited, and the code refreshes input parameters after flashing. Test malformed firmware tail, wrong tail marker/size, non-page firmware length, bootloader/main firmware type checks, page program/verify mismatch, IRQ disabled/open versus closed update paths, event formats 0/1/3, event size zero or unsupported, alert packets, key count bounds, suspend wake IRQ transitions, and CE GPIO power timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/melfas_mip4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c

Purpose: I2C touchscreen driver for the Renesas MIGO-R platform. It enables a simple page-based controller, reads event and coordinate bytes on a threaded IRQ, swaps axes, and reports single-touch input.

Important APIs/types/functions: `struct migor_ts_priv` stores client, input, and IRQ. `migor_ts_ena_seq` and `migor_ts_dis_seq` are controller enable/disable command pages. `migor_ts_isr()` reads one 16-byte page and reports `EVENT_PENDOWN`, `EVENT_REPEAT`, or `EVENT_PENUP`. `migor_ts_open()` and `migor_ts_close()` send enable/disable sequences. Probe/remove manually allocate/free input and IRQ resources; PM only toggles IRQ wake.

Control flow: probe allocates state/input, sets fixed axis ranges, requests a low-triggered threaded IRQ, registers input, and enables wakeup. Open sends the enable sequence. IRQ writes index zero, reads the 16-byte page, extracts X/Y from bytes 8..11 and event from byte 12, reports touch-down/repeat with X/Y swapped, or touch-up. Close disables the IRQ around the disable sequence.

State and persistence: state is only client/input/IRQ plus controller enabled state while the input device is open. No calibration or persistent device data is stored.

Dependencies/integration: depends on I2C master send/recv, threaded IRQs, input core, PM wake IRQ, and I2C ID `migor_ts`.

Risks and test signals: enable/disable sequences are hard-coded and error handling in close ignores disable failure. Test controller page format, axis swap and min/max calibration, IRQ masking during close, wake IRQ suspend/resume, I2C short transfers, and remove after input registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/migor_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mms114.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mms114.c

Purpose: I2C driver for MELFAS MMS114, MMS134S, MMS136, MMS152, and MMS345L touchscreen controllers. It manages regulators, configures older chips' resolution/threshold registers, reports multitouch and optional touch keys, and supports both modern touchscreen properties and legacy board properties.

Important APIs/types/functions: `struct mms114_data` stores client, input, regulators, touchscreen properties, chip type, thresholds, keycodes, and a write-only mode-control cache. `struct mms114_touch` is the packed event record. Register helpers are `__mms114_read_reg()`, `mms114_read_reg()`, and `mms114_write_reg()`. Runtime functions include `mms114_interrupt()`, `mms114_process_mt()`, `mms114_process_touchkey()`, `mms114_set_active()`, `mms114_get_version()`, `mms114_setup_regs()`, `mms114_start()`, `mms114_stop()`, `mms114_parse_legacy_bindings()`, and PM open/close/suspend/resume handlers.

Control flow: probe validates I2C, uses match data to select chip type, parses optional `linux,keycodes`, sets input capabilities, parses touchscreen properties or legacy `x-size`/`y-size` and inversion flags, converts fuzz values into firmware thresholds on older chips, gets `avdd` and `vdd` regulators, requests a no-auto-enable threaded IRQ, and registers input. Open enables regulators, waits 200 ms, reads version, configures older chip registers, and enables IRQ. IRQ reads packet size, chooses 6- or 8-byte event records by chip type, reads the information block, dispatches touchscreen or touchkey records, performs pointer emulation, and syncs. Suspend releases all slots before stopping power if the input is enabled.

State and persistence: register configuration is rewritten on every start for older chips; `cache_mode_control` mirrors the write-only mode register. No host-side persistent storage is used. Regulator power state follows input open and PM.

Dependencies/integration: depends on I2C, regulator framework, OF match data, touchscreen property parser, input MT/key core, threaded IRQs, and compatibles `melfas,mms114`, `melfas,mms134s`, `melfas,mms136`, `melfas,mms152`, and `melfas,mms345l`.

Risks and test signals: `mms114_setup_regs()` writes `props->max_x` into both X and Y low-resolution registers, which should be checked against hardware expectations. Test packet size divisibility and bounds against the stack `touch` array, write-only mode cache correctness, regulator unwind on setup failure, legacy property fallback, keycode truncation, suspend slot release, old/new chip event sizes, and fuzz-to-threshold translation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mms114.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/msg2638.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/msg2638.c

Purpose: I2C driver for MStar MSG2138 and MSG2638 touchscreens. It powers the controller with regulators/reset GPIO, validates raw event checksums, reports multitouch coordinates, and optionally maps capacitive touch keys from `linux,keycodes`.

Important APIs/types/functions: `struct msg_chip_data` selects per-compatible IRQ handler and maximum finger count. Packed wire formats are `msg2138_touch_event`, `msg2138_packet`, `msg2638_touch_event`, and `msg2638_packet`. Driver state is `struct msg2638_ts_data`. Main routines are `msg2638_checksum()`, `msg2138_report_keys()`, `msg2138_ts_irq_handler()`, `msg2638_ts_irq_handler()`, `msg2638_reset()`, `msg2638_start()`, `msg2638_stop()`, `msg2638_init_input_dev()`, probe, and PM handlers.

Control flow: probe validates I2C, obtains match data for MSG2138 or MSG2638, gets `vdd`/`vddio` regulators and reset GPIO, parses optional keycodes, requests a no-auto-enable threaded IRQ using the chip-specific handler, and registers the input device after touchscreen size validation. Open enables regulators, waits, resets the controller, and enables IRQ. MSG2138 IRQ reads a two-finger packet, checks checksum, treats the second packet as key bits if the first is all `0xff`, reports first absolute finger and second finger as delta from first. MSG2638 IRQ reads five raw packets, checks mode and checksum, and reports non-`0xff` contacts by index. Close/suspend disable IRQ and regulators.

State and persistence: runtime state stores regulators, reset GPIO, touchscreen transforms, max finger count, and keycodes. No firmware or persistent host state is written.

Dependencies/integration: depends on I2C, regulator bulk API, GPIO reset, input multitouch, touchscreen properties, property APIs, threaded IRQs, PM mutexing, and OF compatibles `mstar,msg2138` and `mstar,msg2638`.

Risks and test signals: handlers need to drop unused MT slots correctly when contacts disappear; MSG2138's delta second-finger format is easy to misinterpret. Test checksum failures, `0xff` release/key packets, required touchscreen-size properties, keycode truncation, regulator failure unwind, reset timing, MSG2638 non-raw modes, suspend/resume while opened, and coordinate transforms through `touchscreen_report_pos()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/msg2638.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c

Purpose: serio driver for MicroTouch/3M RS-232 touchscreens using the Format Tablet protocol. It assembles serial bytes into fixed five-byte touch frames or delimited response frames and reports single-touch coordinates.

Important APIs/types/functions: `struct mtouch` stores input, serio port, parser index, byte buffer, and physical path. `mtouch_interrupt()` receives bytes from serio. `mtouch_process_format_tablet()` decodes five-byte data frames using status/touch bits and 14-bit coordinates. `mtouch_process_response()` consumes `0x01 ... 0x0d` response frames but does not interpret them. `mtouch_connect()` allocates and registers the input device; `mtouch_disconnect()` tears it down.

Control flow: the serio core matches `SERIO_RS232/SERIO_MICROTOUCH`, connect allocates state/input, opens the serio port, and registers input. Each received byte is appended to `data[idx]`. If the first byte has the tablet status bit, a five-byte frame reports X, inverted Y, and touch state. If the first byte starts a response, bytes are consumed until carriage return or max length. Unknown first bytes are logged and leave synchronization to future bytes.

State and persistence: state is only the in-progress packet index and buffer. No device configuration is sent and no persistent state is stored.

Dependencies/integration: depends on serio bus/protocol IDs, Linux input core, RS-232 transport, and standard module serio registration.

Risks and test signals: parser resynchronization is minimal; a bad first byte can cause repeated debug logs until `idx` is reset by a recognized path. Test noisy serial streams, incomplete frames, response overflow, disconnect while bytes arrive, Y inversion, and coordinate range calibration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mtouch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c

Purpose: platform driver for Freescale MXS LRADC resistive touchscreen support. It reserves two virtual LRADC channels, programs plate switches and delay units, runs an IRQ-driven state machine for Y, X, pressure, and validation samples, then reports single-touch coordinates and pressure.

Important APIs/types/functions: `struct mxs_lradc_ts` tracks parent LRADC, MMIO base, input, current plate state, latest sample values, oversampling/delay settings, and spinlock. `struct state_info info[]` abstracts MX23/MX28 plate bits. Core functions include `mxs_lradc_setup_touch_detection()`, `mxs_lradc_prepare_y_pos()`, `mxs_lradc_prepare_x_pos()`, `mxs_lradc_prepare_pressure()`, `mxs_lradc_handle_touch()`, `mxs_lradc_ts_handle_irq()`, `mxs_lradc_ts_open()`, `mxs_lradc_ts_stop()`, and `mxs_lradc_ts_probe()`.

Control flow: probe reads parent LRADC data and OF properties for touchscreen wires, averaging count, averaging delay, and settling delay; resets the block; configures touchscreen type; requests three named IRQs; and registers input. Open enables touch-detect circuitry. A touch-detect IRQ disables touch detection, enables LRADC channel IRQ, and starts Y sampling. Subsequent channel IRQs read Y, read X, perform paired pressure conversion on channels 6/7, run a dummy validation delay, and only report if touch is still detected. If the pen remains down, the state machine loops to Y sampling; otherwise it emits release and re-enables touch detect.

State and persistence: runtime state is entirely in MMIO registers and the state-machine fields (`cur_plate`, `ts_valid`, coordinates, pressure). Hardware is reinitialized at probe/open and stopped on close; no nonvolatile state is used.

Dependencies/integration: depends on the MXS LRADC MFD parent, `linux/mfd/mxs-lradc.h` register definitions, OF properties (`fsl,lradc-touchscreen-wires`, `fsl,ave-ctrl`, `fsl,ave-delay`, `fsl,settling`), platform IRQ names, STMP reset helper, input core, and spinlock-protected IRQ handling.

Risks and test signals: pressure reading busy-waits until both channel IRQ bits are set, so hardware stalls can hang in IRQ context. Test MX23 and MX28 plate maps, 4-wire/5-wire setup, property bounds, IRQ mapping through `irq_of_parse_and_map()`, stop while state machine is mid-conversion, release validation on noisy panels, pressure divide-by-zero fallback, and interaction with buffered LRADC channels reduced by touchscreen use.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/mxs-lradc-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c

Purpose: I2C driver for Novatek NT11205 and NT36672A touchscreen controllers. It powers and resets the chip, reads a parameter block to discover size/touch count/IRQ type/chip ID, and reports multitouch slots from six-byte contact records.

Important APIs/types/functions: `struct nvt_ts_i2c_chip_data` holds expected chip ID; `struct nvt_ts_data` stores client, input, reset GPIO, regulators, touchscreen properties, max touches, and receive buffer. `nvt_ts_read_data()` performs register-addressed I2C reads. Runtime functions are `nvt_ts_irq()`, `nvt_ts_start()`, `nvt_ts_stop()`, PM suspend/resume, and `nvt_ts_probe()`.

Control flow: probe requires an IRQ, gets match data, obtains `vcc` and `iovcc`, powers the chip, gets reset GPIO, waits 100 ms, reads parameters at `0x78`, puts the chip back into reset and disables regulators, validates width/height/max touches/IRQ type/chip ID, creates input with parsed touchscreen properties, initializes MT slots, requests a no-auto-enable threaded IRQ with device-specified trigger type, and registers input. Open enables regulators, enables IRQ, and releases reset; close disables IRQ, asserts reset, and disables regulators. IRQ reads all touch records, validates slot and state, reports active/release state and transformed coordinates, then syncs.

State and persistence: state is volatile and power-gated; the chip is reset and regulators are off while the input device is closed. No persistent configuration is written.

Dependencies/integration: depends on I2C, regulator bulk API, reset GPIO, OF/I2C match data for `novatek,nt11205-ts` and `novatek,nt36672a-ts`, input MT core, touchscreen properties, and PM mutexing.

Risks and test signals: start enables IRQ before reset release, so interrupt timing around power-up should be tested. Validate parameter rejection paths, chip ID mismatch, unsupported buttons warning, max touch zero/out of range, IRQ trigger mapping, slot numbers starting at one, release records still carrying coordinates, regulator disable on probe errors, and suspend/resume while open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/novatek-nvt-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c

Purpose: platform driver for Motorola PCAP2 PMIC touchscreen ADC on EZX phones. It uses the PCAP MFD ADC async API and a delayed-work state machine to alternate pressure and XY reads, reporting single-touch coordinates and pressure.

Important APIs/types/functions: `struct pcap_ts` holds the PCAP handle, input device, delayed work, latest x/y/pressure, and ADC touchscreen read state. `pcap_ts_event_touch()` starts sampling from standby on PMIC touch IRQ. `pcap_ts_work()` programs touchscreen mode bits and starts ADC conversions. `pcap_ts_read_xy()` is the async ADC callback and drives pressure/XY/release transitions. Open/close are `pcap_ts_open()` and `pcap_ts_close()`, with PM callbacks writing low-power or current mode bits.

Control flow: probe allocates state/input, initializes read state to non-touchscreen, registers input, then requests the PCAP touchscreen IRQ. Open sets standby and schedules work to program mode. Touch IRQ switches to pressure mode and schedules immediate conversion. Pressure callback caches a usable pressure and switches to XY; XY callback either reports release and returns to standby when coordinates are out of range or reports X/Y/pressure and schedules the next pressure read after 20 ms. Close cancels work and programs non-touchscreen mode.

State and persistence: runtime state is the delayed work, last pressure, coordinates, and `read_state`. Hardware mode bits in the PCAP ADC block are modified while active or suspended. No nonvolatile state is written.

Dependencies/integration: depends on `ezx-pcap` MFD APIs (`pcap_set_ts_bits`, `pcap_adc_async`, `pcap_to_irq`), delayed work, platform driver binding `pcap-ts`, and Linux input core.

Risks and test signals: async ADC callbacks can race with close/remove unless work and PMIC callbacks are serialized by the MFD. Test remove while ADC callback is outstanding, pressure reliability filtering, release threshold at coordinate edges, suspend/resume restoring state, IRQ request after input registration failure unwinds, and sampling cadence under repeated touches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pcap_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c

Purpose: serio driver for PenMount RS-232 touchscreen protocols. It supports single-touch 9000/6000 packet formats and multitouch 3000/6250 formats, validates checksums where present, and reports input through absolute and multitouch events.

Important APIs/types/functions: `struct pm` stores input, serio, packet index/data, packet size, max contacts, slot cache, and parser function pointer. `struct mt_slot` stores per-contact x/y/active. Parser functions are `pm_parse_9000()`, `pm_parse_6000()`, `pm_parse_3000()`, and `pm_parse_6250()`. `pm_checkpacket()` validates six-byte checksum formats, `pm_mtevent()` emits MT slots plus pointer emulation, `pm_interrupt()` feeds bytes to the selected parser, and connect/disconnect manage serio and input lifetimes.

Control flow: connect chooses packet size, parser, product ID, coordinate max, and max contact count based on `serio->id.id`; initializes ABS axes and MT slots when needed; opens serio; and registers input. Each received byte is stored at the current index and passed to the parser. A parser verifies header bits and packet length, optionally validates checksum, decodes coordinates/touch/slot state, reports single-touch or updates a cached MT slot and emits all slots.

State and persistence: state is the packet buffer/index and cached multitouch slots. No controller configuration or persistent data is written.

Dependencies/integration: depends on serio `SERIO_PENMOUNT`, Linux input and MT core, and RS-232 packet formats for PenMount model families.

Risks and test signals: parser synchronization depends on header checks and does not scan for headers mid-packet. Test corrupted bytes, checksum failures, slot numbers for 3000/6250 staying below `maxcontacts`, disconnect during interrupt activity, MT pointer emulation, coordinate max by model, and packet size differences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/penmount.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pixcir_i2c_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/pixcir_i2c_ts.c

Purpose: I2C driver for Pixcir touchscreen controllers, including two-finger devices without hardware IDs and TangoC-style five-finger devices with hardware IDs. It configures power and interrupt modes, parses coordinate reports, manages optional GPIOs, and supports wakeup behavior.

Important APIs/types/functions: `struct pixcir_i2c_chip_data` describes max fingers and hardware-ID support. `struct pixcir_i2c_ts_data` stores client, input, ATTB/reset/enable/wake GPIOs, chip data, touchscreen properties, and a `running` flag. `pixcir_ts_parse()` reads and decodes reports, `pixcir_ts_report()` assigns/report slots, `pixcir_ts_isr()` drains reports while ATTB remains asserted, `pixcir_reset()`, `pixcir_set_power_mode()`, `pixcir_set_int_mode()`, `pixcir_int_enable()`, `pixcir_start()`, `pixcir_stop()`, PM callbacks, and `pixcir_i2c_ts_probe()` implement lifecycle.

Control flow: probe resolves chip data from OF or I2C ID, creates input, requires touchscreen size properties, initializes MT slots, gets ATTB and optional reset/wake/enable GPIOs, requests a falling-edge threaded IRQ, resets the controller, sets idle power mode, stops interrupt generation, registers input, and stores client data. Open enables optional power GPIO, configures level-touch active-low interrupt mode, sets `running` before enabling interrupt generation, and returns. The ISR loops while running: writes register index zero, reads a report sized by max fingers and ID support, transforms coordinates, reports slots by hardware ID or assigned positions, and exits once ATTB deasserts, emitting a final sync if needed. Stop disables interrupt generation, clears `running`, synchronizes IRQ, and disables optional enable GPIO. PM starts/stops the device differently depending on wakeup-source and input open state.

State and persistence: controller power mode is set to idle during probe; interrupt mode/generation and GPIO enable state follow input open and PM. Runtime state includes only chip description, touchscreen transform, GPIOs, and running flag.

Dependencies/integration: depends on I2C/SMBus, GPIO consumer API, input MT assignment helpers, touchscreen properties, IRQ synchronization, OF/I2C IDs (`pixcir,pixcir_ts`, `pixcir,pixcir_tangoc`, `pixcir_ts`, `pixcir_tangoc`), and PM wakeup policy.

Risks and test signals: `running` is shared between open/close and the threaded IRQ with barriers but no lock, so stop/ISR races should be tested. Test missing ATTB GPIO, optional GPIO polarity, no-size property rejection, hardware ID slot exhaustion, ATTB stuck low causing repeated reads, wakeup suspend when input is closed, failed interrupt disable on stop, reset timing, and active-low interrupt configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/pixcir_i2c_ts.c -->
