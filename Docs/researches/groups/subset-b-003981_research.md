# subset-b-003981 touchscreen driver research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c

## Purpose
`raspberrypi-ts.c` is a small platform input driver for the Raspberry Pi firmware-backed touchscreen interface. Instead of talking to a touchscreen controller over I2C/SPI, it allocates one coherent DMA page, passes the physical address to the VideoCore firmware with `RPI_FIRMWARE_FRAMEBUFFER_SET_TOUCHBUF`, and polls the firmware-maintained memory layout as a multitouch device.

## Important APIs, Types, And Functions
The main state is `struct rpi_ts`, which stores the platform device, input device, parsed `touchscreen_properties`, the coherent firmware register buffer, and a `known_ids` bitmask. `struct rpi_ts_regs` mirrors the firmware buffer: mode, gesture, number of points, and up to ten packed `rpi_ts_touch` entries. `rpi_ts_probe()` obtains the parent firmware node, calls `devm_rpi_firmware_get()`, allocates DMA memory, registers `rpi_ts_dma_cleanup()` with devres, configures the input axes, initializes ten `INPUT_MT_DIRECT` slots, installs `input_setup_polling()`, and registers the input device. `rpi_ts_poll()` is the runtime data path.

## Control Flow
Probe binds to `raspberrypi,firmware-ts`, registers the DMA buffer with firmware, then exposes a polled `BUS_HOST` input device. Each poll copies `struct rpi_ts_regs` from I/O memory, invalidates `num_points` by writing `99`, and ignores stale or empty data. It decodes X/Y, touch ID, and event type, reports active slots for down/contact events, computes releases from `known_ids & ~modified_ids`, syncs the MT frame, and stores the current active bitmask.

## State And Persistence
Driver state is volatile and devres-managed. The only persistent hardware-visible state is the DMA buffer address registered with firmware during probe; touch slot state is tracked in memory through `known_ids`. There is no firmware upload, sysfs state, suspend path, or file-backed persistence.

## Dependencies And Integration Points
The driver integrates with OF platform matching, Raspberry Pi firmware property calls, coherent DMA APIs, input polling, multitouch slot helpers, and touchscreen DT properties for axis transforms. Firmware must understand the shared-buffer ABI.

## Risks
The firmware buffer address is truncated to `u32`, so it assumes firmware-addressable DMA memory. Data validity depends on the `num_points` invalidation convention. Only down/contact events report coordinates; other event types are ignored. Because it is polled at 17 ms, latency and missed transient states are bounded by polling cadence.

## Test Signals
Useful validation includes successful probe without `Failed to set touchbuf`, `/proc/bus/input/devices` showing `raspberrypi-ts`, evtest/libinput reporting stable ten-slot MT events, DT axis inversion/swap behavior, and release events when fingers leave the panel.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raspberrypi-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c

## Purpose
`raydium_i2c_ts.c` drives Raydium I2C capacitive touchscreen controllers, including `raydium_i2c`, `rm32380`, ACPI `RAYD0001`, and OF `raydium,rm32380`. It handles power sequencing, banked I2C register access, bootloader/main firmware mode discovery, firmware updates, sysfs maintenance commands, interrupt-driven multitouch reporting, and system sleep.

## Important APIs, Types, And Functions
`struct raydium_data` holds the `i2c_client`, input device, `avdd`/`vccio` regulators, optional reset GPIO, queried `struct raydium_info`, sysfs mutex, report buffer, bank address, packet sizes, and boot mode. `raydium_i2c_send()` and `raydium_i2c_read()` implement the key transport rule: if an address exceeds one byte, an `RM_CMD_BANK_SWITCH` message and the data transfer are issued in one `i2c_transfer()` to avoid other devices interleaving on the shared bus. Initialization flows through `raydium_i2c_check_fw_status()`, `raydium_i2c_query_ts_bootloader_info()`, and `raydium_i2c_query_ts_info()`. Firmware update is split across bootloader helpers such as `raydium_i2c_enter_bl()`, `raydium_i2c_fw_write_page()`, `raydium_i2c_write_checksum()`, and `raydium_i2c_do_update_firmware()`.

## Control Flow
Probe verifies raw I2C capability, acquires regulators and reset GPIO, powers on, checks an SMBus byte transaction reaches a device, initializes boot/main mode, allocates a report buffer sized from controller metadata, creates a ten-slot direct MT input device with X/Y resolution, registers sysfs attributes, and requests a threaded IRQ. On IRQ, `raydium_i2c_irq()` ignores events while in bootloader recovery, reads a full packet from `data_bank_addr`, validates the trailing checksum, and calls `raydium_mt_event()` to report each contact's slot state, X/Y, pressure, and major/minor width.

## State And Persistence
The driver keeps controller metadata and boot mode in RAM. Firmware update is user-triggered by sysfs `update_fw`; it loads `raydium_<hw_ver>.fw`, writes flash pages, and reinitializes metadata. Sysfs also exposes `fw_version`, `hw_version`, `boot_mode`, and `calibrate`. Hardware state persists in controller flash after updates, while input/report state is volatile.

## Dependencies And Integration Points
It depends on the I2C core, firmware loader, regulator and GPIO consumer APIs, input MT, wake IRQ/sleep PM, ACPI/OF matching, and sysfs device groups. `device_may_wakeup()` selects between sleep command and full power-off during suspend.

## Risks
Bank switching is fragile by design; any future refactor to regmap would violate the driver's stated bus atomicity requirement. Firmware update disables IRQs but still depends on controller acknowledgments and correct package size/checksum. `raydium_i2c_power_on()` is effectively a no-op without reset GPIO, so board descriptions without GPIO may leave regulator sequencing to external firmware. Suspend refuses bootloader mode with `-EBUSY`.

## Test Signals
Test probe on I2C adapters with `I2C_FUNC_I2C`, read sysfs version/mode files, verify checksum warnings are absent under touch load, trigger calibration, exercise firmware update with valid and invalid firmware sizes, and check suspend/resume both with and without wakeup enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/raydium_i2c_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c

## Purpose
`resistive-adc-touch.c` is a generic platform driver for resistive touchscreens whose samples arrive through IIO channels rather than a dedicated touchscreen controller driver. It maps named ADC channels from firmware properties, converts raw X/Y and optional pressure data into input events, and starts/stops the IIO callback buffer on input open/close.

## Important APIs, Types, And Functions
`enum grts_ch_type` defines logical channels: X, Y, direct pressure, Z1, and Z2. `struct grts_state` stores X-plate resistance, pressure threshold, channel list/callback, input device, touchscreen transform properties, and a logical-to-IIO channel map. `grts_map_channel()` resolves entries in `io-channel-names`; `grts_get_properties()` validates required X/Y, optional direct pressure, or optional Z1/Z2 pressure calculation with `touchscreen-x-plate-ohms`. `grts_cb()` is the IIO callback that reads the sample array and reports input state. `grts_open()` and `grts_close()` start and stop `iio_channel_start_all_cb()` / `iio_channel_stop_all_cb()`.

## Control Flow
Probe obtains all IIO channels, requires `io-channel-names`, parses channel mapping and pressure configuration, allocates a `BUS_HOST` input device, sets ABS_X/ABS_Y and optional ABS_PRESSURE limits, parses touchscreen axis properties, registers the input device, then creates an all-channel IIO callback buffer. When userspace opens the input node, the callback buffer begins streaming. Each callback extracts X/Y, computes direct pressure or resistive pressure from Z1/Z2 and X-plate resistance, emits release if X/Y are zero or pressure is below threshold, otherwise reports transformed position, pressure, `BTN_TOUCH`, and sync.

## State And Persistence
All state is runtime-only. The driver persists no calibration or settings; thresholds and channel topology come from device properties at probe. The IIO callback object is devres-cleaned through `grts_disable()`.

## Dependencies And Integration Points
It integrates the IIO consumer callback API, generic device properties/OF, input core, and touchscreen property parsing. It expects channel ordering and names to match the sampled buffer layout.

## Risks
The code supports at most four channels and uses `GRTS_MAX_CHANNELS` as the sentinel. A misordered or incomplete `io-channel-names` property silently changes pressure behavior. Z1/Z2 pressure math avoids division by zero but depends on realistic plate resistance and sample ranges. Direct release detection treats `(x == 0 && y == 0)` as no touch, which can conflict with panels that can legitimately report origin.

## Test Signals
Validate DT bindings for required names, confirm IIO buffer starts only while the input device is open, observe releases below `touchscreen-min-pressure`, test Z1/Z2 pressure against known loads, and use evtest to confirm axis transforms and `BTN_TOUCH` transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/resistive-adc-touch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c

## Purpose
`rohm_bu21023.c` drives ROHM BU21023/BU21024 dual-touch resistive touchscreen controllers over I2C. It performs low-level register setup, loads controller firmware (`bu21023.bin`) on input open, applies manual calibration, exposes axis transform sysfs knobs, and reports up to two multitouch contacts from threaded IRQs.

## Important APIs, Types, And Functions
`struct rohm_ts_data` stores the `i2c_client`, input device, initialization flag, contact debounce counters, current finger count, and `COMMON_SETUP2` transform bits. `rohm_i2c_burst_read()` performs the controller's unusual two-step read under an I2C segment lock. `rohm_ts_device_init()` programs the register table, loads firmware with `rohm_ts_load_firmware()`, seeds calibration registers, enables interrupts, and powers the CPU. `rohm_ts_soft_irq()` reads position/touch registers, debounces 0/1/2 contact transitions using threshold arrays, assigns MT slots, and invokes `rohm_ts_manual_calibration()` on calibration request. Sysfs attributes `swap_xy`, `inv_x`, and `inv_y` update `COMMON_SETUP2` through `rohm_ts_update_setting()`.

## Control Flow
Probe requires an IRQ and adapter `master_xfer`, powers the controller CPU off, allocates state/input, configures two MT slots, requests a threaded IRQ, and registers the input device. The device is not fully initialized until the input node is opened; `rohm_ts_open()` calls `rohm_ts_device_init()` once and marks `initialized`. On close, `rohm_ts_power_off()` turns analog/CPU blocks off and clears `initialized`.

## State And Persistence
Runtime state includes debounce counters and the current axis transform bits. Sysfs writes persist only while the driver instance exists; if initialized, they are immediately written to hardware. Firmware is loaded from the kernel firmware interface into controller program memory; no kernel-side copy persists after load.

## Dependencies And Integration Points
The driver uses I2C SMBus plus low-level `__i2c_transfer()`, firmware loading, threaded IRQs, input MT slot assignment, input mutex guards for sysfs changes, and I2C device IDs. Unlike many modern touchscreen drivers, it does not parse DT touchscreen properties.

## Risks
Initialization is heavy and happens on open, so missing firmware makes the input device present but unusable. The burst read protocol depends on stop conditions and manual bus locking. Contact-count thresholds intentionally delay transitions, which can hide very short touches. Manual calibration modifies several registers and has rollback paths that still depend on successful I2C writes. Axis transform sysfs accepts any nonzero integer as true.

## Test Signals
Probe should reject missing IRQs. Opening the input device should load `bu21023.bin`, power the CPU, and enable coordinates. Test one- and two-finger transitions, calibration request interrupts, sysfs transform writes while opened and closed, close/open reinitialization, and missing/invalid firmware behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/rohm_bu21023.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/s6sy761.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/s6sy761.c

## Purpose
`s6sy761.c` is an I2C driver for Samsung S6SY761 touch controllers. It powers regulators, validates boot/application/firmware state, reads panel dimensions and device ID, exposes a `devid` sysfs file, and reports multitouch coordinates from the controller event stack.

## Important APIs, Types, And Functions
`struct s6sy761_data` stores the `i2c_client`, two regulators (`vdd`, `avdd`), input device, touchscreen properties, event buffer, device ID, and TX channel count. `s6sy761_power_on()` enables regulators, waits for boot, validates a boot-complete event, verifies application mode and firmware integrity, and enables touch functionality. `s6sy761_hw_init()` reads device ID and panel info. `s6sy761_irq_handler()` reads one event with `S6SY761_READ_ONE_EVENT`, optionally drains remaining events with `s6sy761_read_events()`, then dispatches to `s6sy761_handle_events()`.

## Control Flow
Probe checks required I2C/SMBus functionality, acquires regulators, registers `s6sy761_power_off()` as a cleanup action, initializes hardware, allocates and configures an input device, parses touchscreen properties, initializes MT slots using controller `tx_channel`, registers the input device, requests a low-triggered threaded IRQ, and enables runtime PM. Opening the input node writes `S6SY761_SENSE_ON`; closing writes `S6SY761_SENSE_OFF`.

## State And Persistence
State is runtime-only: `devid`, `tx_channel`, and event data are stored in RAM. The controller retains firmware/application state externally. Runtime suspend writes application sleep mode; runtime resume writes normal mode. System suspend disables IRQ and regulators; resume enables IRQ and powers on again.

## Dependencies And Integration Points
The driver integrates with I2C, SMBus block operations, regulator bulk APIs, threaded IRQs, input MT, touchscreen property parsing, sysfs device groups, runtime PM, system sleep PM, OF matching (`samsung,s6sy761`), and I2C IDs.

## Risks
The cleanup action calls `disable_irq()` even though it is registered before IRQ request; this relies on the cleanup path being reached after the client IRQ is meaningful and may be sensitive to probe failure ordering. Slot count uses TX channel count rather than the fixed max-finger constant. The probe checks `input_abs_get_max(ABS_X/Y)` after setting only MT axes, so the warning path appears mismatched to actual axes. Duplicate `ABS_MT_TOUCH_MAJOR/MINOR` setup is harmless but suspicious.

## Test Signals
Check boot failures for bootloader mode or bad firmware integrity, read `/sys/.../devid`, verify event-stack draining for multiple simultaneous events, test open/close sense commands, runtime PM sleep/normal mode transitions, and system suspend/resume power cycling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/s6sy761.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/silead.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/silead.c

## Purpose
`silead.c` drives Silead GSL/MSSL I2C capacitive touchscreen controllers. It handles firmware download, ACPI/platform firmware fallback, optional EFI min/max coordinate correction, optional pen input, home-button softbutton reporting, regulator/GPIO power, IRQ-driven touch reads, and suspend/resume recovery.

## Important APIs, Types, And Functions
`struct silead_ts_data` holds I2C client, optional power GPIO, touch and pen input devices, `vddio`/`avdd` regulators, firmware name, touchscreen properties, chip ID, slot assignment arrays, EFI coordinate bounds, pen capability/resolution, and pen debounce state. `silead_ts_setup()` powers and initializes the chip, calls `silead_ts_load_fw()`, starts firmware, and checks `SILEAD_STATUS_OK`. `silead_ts_load_fw()` first tries `firmware_request_nowarn()`, then `firmware_request_platform()` and optional `silead,efi-fw-min-max`. `silead_ts_read_data()` parses the 44-byte report and assigns MT slots; `silead_ts_handle_pen_data()` recognizes a special pen packet format.

## Control Flow
Probe verifies I2C block read/write support, allocates state, chooses a firmware name from ACPI/I2C ID or `firmware-name`, reads optional pen/home-button/stuck-controller properties, requires an IRQ, enables regulators for the life of the device because firmware is volatile, obtains optional power GPIO, runs setup, creates the touch and optional pen input devices, and requests a threaded IRQ. IRQs read one data block, clamp excessive touch count, optionally report pen state, otherwise filter softbutton pseudo-contacts, assign MT slots, report coordinates, report `KEY_LEFTMETA` when configured, and sync.

## State And Persistence
The controller loses firmware when powered down, so regulators remain enabled after probe. Suspend disables IRQ and uses the power GPIO to turn the controller off; resume powers on, resets, starts firmware, and reloads firmware only if the first status check fails. Kernel state includes firmware name, chip ID, coordinate correction, and pen-down debounce.

## Dependencies And Integration Points
The driver integrates with I2C SMBus block APIs, firmware loader including platform fallback, ACPI/OF matching, regulators, optional GPIO, input MT, touchscreen helpers, PM sleep ops, and device properties from touchscreen DMI/firmware descriptions.

## Risks
Firmware availability and correctness dominate reliability. EFI fallback can disable pen support and requires alternate min/max properties to keep coordinates calibrated. The stuck-controller workaround intentionally triggers an I2C failure to force bus recovery. Pen support uses packet heuristics and a six-report release debounce. In `silead_ts_request_pen_input_dev()`, the code assigns `data->input->id.bustype` rather than the pen input's bustype, which looks like a minor copy/paste defect.

## Test Signals
Test firmware lookup paths, EFI fallback min/max correction, probe on stuck-controller hardware, home-button softbutton events, pen down/up debounce, suspend/resume with and without firmware reload, and invalid touch counts above ten.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/silead.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c

## Purpose
`sis_i2c.c` drives SiS 9200-family I2C touch panels. It parses variable-length controller packets, validates CRC for touch reports, handles optional area/pressure/scan-time fields, supports multi-packet reports, and emits up to ten direct multitouch slots.

## Important APIs, Types, And Functions
`struct sis_ts_data` stores the I2C client, input device, optional attention/reset GPIOs, and a 64-byte packet buffer. `sis_read_packet()` receives one maximum-sized packet, validates length, determines report type, verifies CRC for touch packets, adjusts the contact count index for CRC/scan-time fields, and computes contact size from area/pressure flags. `sis_ts_report_contact()` maps controller contact IDs to input slots and reports slot state, X/Y, pressure, and touch major/minor. `sis_ts_handle_packet()` drains one or more packets until all contacts in the report are consumed.

## Control Flow
Probe allocates state, gets optional `attn` and `reset` GPIOs, toggles reset, allocates a `SiS Touchscreen` input device with 4095 X/Y, pressure, and area axes, initializes ten direct MT slots, requests a threaded IRQ, and registers input. On IRQ, the handler repeatedly calls `sis_ts_handle_packet()` while the optional attention GPIO remains asserted. A first packet's contact count becomes the remaining count; later tail packets must report zero contacts in their count field.

## State And Persistence
The driver holds no persistent settings. Packet parsing state is local to `sis_ts_handle_packet()`, and per-contact tracking is maintained by input MT slots keyed by controller contact ID. Optional reset is performed only at probe.

## Dependencies And Integration Points
It uses I2C `i2c_master_recv()`, CRC-ITU-T, GPIO consumer APIs, threaded IRQs, input MT helpers, OF matching (`sis,9200-ts`), and I2C IDs (`sis_i2c_ts`, `9200-ts`).

## Risks
The packet format is dense and variable; bad length/count indices can desynchronize parsing. Tail-packet logic assumes at most five contacts per non-all-in-one packet before continuation. The IRQ loop depends on attention GPIO polarity if present. There is no explicit I2C functionality check and no power-management path. `gpiod_set_value()` is used for reset rather than the cansleep variant, so reset GPIO provider constraints matter.

## Test Signals
Inject or capture packets with CRC errors, HIDI2C report IDs, area/pressure/scantime combinations, and multi-packet ten-contact frames. Validate attention GPIO drain behavior, reset timing, input slot reuse by contact ID, and release packets with status `SIS_STATUS_UP`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sis_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/st1232.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/st1232.c

## Purpose
`st1232.c` supports Sitronix ST1232 and ST1633 I2C touchscreen controllers. It reads firmware metadata and panel resolution, supports chip-specific finger count/Z-axis behavior, integrates optional touch overlays, and uses IRQ-driven multitouch reporting with low-latency PM QoS while contacts are active.

## Important APIs, Types, And Functions
`struct st_chip_info` captures model differences: `have_z`, max touch area, and max fingers. `struct st1232_ts_data` stores client, input device, touchscreen properties, PM QoS request, optional reset GPIO, chip info, touch-overlay list, read buffer, and firmware version/revision. `st1232_ts_read_data()` performs a two-message DMA-safe I2C read. `st1232_ts_wait_ready()`, `st1232_ts_read_fw_version()`, and `st1232_ts_read_resolution()` initialize metadata. `st1232_ts_parse_and_report()` decodes active contacts, applies touchscreen transforms, lets touch overlays consume mapped contacts, assigns MT slots, and syncs.

## Control Flow
Probe resolves chip info from OF or I2C ID, checks I2C and IRQ availability, allocates a read buffer sized to max fingers, obtains optional reset GPIO, powers the controller, registers a devres power-off action, waits for ready state, reads firmware version/revision, configures touch major if available, maps touch overlays, reads resolution from overlay or hardware, parses touchscreen properties, initializes MT slots, requests a threaded IRQ, registers input, and stores client data. IRQ reads coordinate registers, reports contacts, and adds/removes a 100 us ancestor resume-latency request when first contact appears or all contacts end.

## State And Persistence
Firmware version/revision are retained in RAM and exposed through read-only sysfs. The reset GPIO controls power state. PM QoS state is transient and must be removed when contact count returns to zero. No user-writable state or firmware upload exists.

## Dependencies And Integration Points
The driver uses I2C core, GPIO consumer APIs, input MT, `touch-overlay`, `touchscreen_parse_properties()`, dev_pm_qos, OF/I2C match tables, sysfs attributes, and simple sleep PM. Wake-capable devices keep power on during suspend.

## Risks
Low-latency PM QoS is removed only when an IRQ reports zero contacts; missed release events could leave the request active until suspend/remove paths resolve it. Z values for ST1232 are read from `read_buf[i + 6]`, which relies on the controller's packed report layout. Overlay processing can consume contacts before normal MT reporting, so overlay definitions need careful validation. There is no explicit remove hook for PM QoS if the device is unplugged while a request is active.

## Test Signals
Verify sysfs firmware values, ST1232 two-finger Z reporting, ST1633 five-finger no-Z behavior, overlay-mapped virtual keys, PM QoS add/remove on first/last contact, reset GPIO suspend/resume behavior, and error handling for not-ready status.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/st1232.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c

## Purpose
`stmfts.c` is an I2C driver for STMicroelectronics FTS touchscreens. It handles regulator sequencing, controller reset/sleep/calibration commands, event-stack parsing, optional hover and touch-key support, optional key LED regulator control, runtime/system PM, and several read-only/sysfs controls.

## Important APIs, Types, And Functions
`struct stmfts_data` stores client, input device, LED class device, mutex, touchscreen properties, `vdd`/`avdd` regulators, optional `ledvdd`, chip/config/firmware IDs, a 256-byte event buffer, command completion, and flags for keys, LED, hover, and running state. `stmfts_read_events()` uses raw I2C transfer to read 32 eight-byte events, bypassing SMBus block size limits. `stmfts_parse_events()` dispatches contact enter/motion/leave, hover, key, error, and controller-ready events. `stmfts_command()` writes a command and waits up to one second for IRQ parsing to complete `cmd_done`.

## Control Flow
Probe verifies I2C capabilities, allocates state, initializes mutex/completion, gets regulators, allocates input, parses touchscreen properties, configures MT/pressure/orientation/distance axes and optional `KEY_MENU`/`KEY_BACK`, requests the IRQ with `IRQF_NO_AUTOEN`, powers on the controller, registers cleanup, registers input, optionally registers an LED class device for touch-key backlight, enables runtime PM, and async suspend. `stmfts_power_on()` enables regulators, reads info, enables IRQ, issues system reset, sleep out, optional tuning, full calibration, then leaves the controller asleep until input open. Input open resumes runtime PM and enables sensing; close disables sensing/key/hover and runtime-suspends.

## State And Persistence
Driver state includes chip metadata, hover enable, running flag, LED state, and command completion state. Sysfs exposes chip/config/firmware IDs, status, and read/write `hover_enable`. LED state is controlled through the LED subsystem and optional `ledvdd`. Hardware tuning/calibration is performed at power-on but not persisted by this driver.

## Dependencies And Integration Points
It uses I2C, regulators, input MT, touchscreen helpers, IRQ completions, mutex guards, LED classdev, sysfs groups, runtime PM/system PM, and OF/I2C matching. Touch-key LEDs depend on a separate `ledvdd` regulator.

## Risks
Command completion depends on IRQ delivery while power-on is running; bad IRQ wiring can turn commands into one-second timeouts. System suspend powers off regulators even if runtime state says running. Event parsing calls `input_sync()` per contact, which is simpler but can produce more syncs than frame-oriented drivers. Optional LED setup failure is non-fatal and leaves `ledvdd = NULL`.

## Test Signals
Check sysfs identity/status files, command timeouts with IRQ disabled, hover enable toggles while opened and closed, touch-key and LED behavior when `touch-key-connected` is present, runtime PM open/close, and system suspend/resume reinitialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmfts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c

## Purpose
`stmpe-ts.c` is the touchscreen child driver for STMPE MFD devices with an integrated resistive touchscreen controller, especially STMPE811-compatible layouts. It configures the MFD ADC/touchscreen block, handles FIFO threshold interrupts, reports single-touch X/Y/pressure, and works around known FIFO/touch-detect quirks with delayed release polling.

## Important APIs, Types, And Functions
`struct stmpe_touch` stores the parent `struct stmpe`, input device, delayed work for release detection, device pointer, touchscreen properties, and ADC/touchscreen timing parameters. `stmpe_ts_get_platform_info()` reads DT properties such as sample time, ADC frequency, averaging, touch-detect delay, settling, Z fraction, and drive current. `stmpe_init_hw()` enables MFD touchscreen/ADC blocks, initializes common ADC state, configures TSC timing, FIFO threshold, and XYZ mode. `stmpe_ts_handler()` is the threaded IRQ path, and `stmpe_work()` emits release events after touch-detect settles.

## Control Flow
Probe obtains the parent MFD state, finds the named `FIFO_TH` IRQ, allocates state/input, reads platform tuning, initializes delayed work, requests the threaded IRQ, initializes hardware, configures `BTN_TOUCH`, ABS_X/ABS_Y/ABS_PRESSURE, parses touchscreen properties, and registers input. Opening the input device resets FIFO and enables TSC; closing cancels delayed work and disables TSC. The IRQ handler cancels pending release work, disables TSC, reads one XYZ sample, reports transformed position/pressure/down, resets FIFO, re-enables TSC, and schedules release polling 50 ms later.

## State And Persistence
State is volatile and bound to the MFD child. Platform tuning comes from DT and is applied at probe. The delayed work item is the main transient state used to convert touch-detect behavior into release events. Remove disables the touchscreen block.

## Dependencies And Integration Points
The driver depends on the STMPE MFD API (`stmpe_enable`, `stmpe_set_bits`, `stmpe_block_read`, ADC common init), platform IRQ resources, input core, touchscreen properties, delayed work, and platform driver binding.

## Risks
The driver explicitly works around silicon issues: FIFO may stop interrupting, touch-detect may deassert or stick. Release timing is heuristic. IRQ handler does not check all register-read return values before reporting. Remove disables only `STMPE_BLOCK_TOUCHSCREEN`, while probe enabled touchscreen and ADC blocks, so parent MFD lifetime assumptions matter.

## Test Signals
Validate DT tuning properties, open/close enable bits, FIFO reset on each IRQ, release generation after lift, behavior when FIFO contains no data, pressure range reporting, and MFD block enable/disable sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/stmpe-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c

## Purpose
`sun4i-ts.c` drives the Allwinner sun4i/sun5i/sun6i resistive touchscreen and temperature sensor block. It deliberately exposes reliable single-touch input only, while also registering hwmon and thermal-zone temperature interfaces for the shared ADC sensor.

## Important APIs, Types, And Functions
`struct sun4i_ts_data` stores the device, optional input device, MMIO base, IRQ, FIFO-ignore flag, last temperature sample, and temperature conversion coefficients. `sun4i_ts_irq()` handles both touch and temperature interrupts. `sun4i_ts_irq_handle_input()` reads X/Y FIFO samples, ignores the first sample after an up event, reports `BTN_TOUCH`, and handles releases. `sun4i_get_temp()` converts raw ADC temperature data into millidegrees using SoC-specific formulas. `sun4i_ts_probe()` configures MMIO registers, optional input, hwmon, and thermal.

## Control Flow
Probe sets temperature coefficients by compatible string, checks `allwinner,ts-attached`, optionally allocates a `BUS_HOST` input device, maps MMIO, requests IRQ, configures ADC clock/acquisition, touch sensitivity, filter type, temperature period, stylus debounce, and touch mode. It registers hwmon groups and a thermal OF zone, enables temperature IRQs, and registers input if a panel is attached. Input open enables temp/data/up IRQs and flushes FIFO; close leaves only temp IRQ enabled.

## State And Persistence
The driver maintains `ignore_fifo_data` to suppress stale coordinates after pen-up and `temp_data` initialized to `-1` until the first temperature IRQ. Register programming is redone only at probe; there is no PM callback in this file. Hardware state is disabled in remove.

## Dependencies And Integration Points
It integrates with OF platform matching, MMIO register access, input core, hwmon sysfs (`temp1_input`, `temp1_label`), thermal OF zones, and Allwinner-specific DT properties (`allwinner,ts-attached`, `allwinner,tp-sensitive-adjust`, `allwinner,filter-type`).

## Risks
Temperature conversion for some SoCs is based on approximate or external formulas and is documented as inaccurate. If no touchscreen is attached, only thermal/hwmon paths are active. FIFO handling assumes each data-pending interrupt has X followed by Y. The single-touch policy ignores hardware dual-touch because reported dual coordinates are considered unusable.

## Test Signals
Test with and without `allwinner,ts-attached`, verify hwmon and thermal reads after first IRQ, confirm first coordinate after release is ignored, exercise touch down/up interrupts, validate compatible-specific temp coefficients, and check remove disables interrupt masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sun4i-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c

## Purpose
`sur40.c` drives the Microsoft/Samsung SUR40 PixelSense USB device. It exposes two interfaces from one USB driver: a polled multitouch input device for blob/contact data and a V4L2 touch/video capture device for raw sensor frames, with controls for brightness, contrast, gain, and backlight/preprocessor behavior.

## Important APIs, Types, And Functions
The wire formats are `struct sur40_header`, `struct sur40_blob`, and `struct sur40_image_header`. `struct sur40_state` owns the USB device, input device, V4L2 device/video_device, vb2 queue, buffer list/spinlock, pixel format, controls, bulk input buffer, endpoint metadata, and device path. `sur40_command()`/`sur40_poke()` perform vendor control transfers. `sur40_report_blob()` converts blob geometry to input MT fields. `sur40_poll()` reads touch bulk packets from endpoint `0x86`, reports all blobs, then calls `sur40_process_video()` if V4L2 streaming is active. The vb2 and V4L2 operations implement buffer setup, streaming, format enumeration, and ioctls.

## Control Flow
Probe matches USB VID/PID, validates interface class/endpoints, allocates state and input, configures 64 MT slots, sets up input polling at 1 ms, allocates a bulk buffer, registers the input device, registers V4L2, initializes a DMA-SG vb2 queue, creates controls, and registers the video device. Input open initializes the SUR40 and enables polling; close marks V4L2 sequence stopped. Polling reads one or more touch packets until the blob count is satisfied, then optionally reads a video header plus a scatter-gather frame into the next queued vb2 buffer.

## State And Persistence
Runtime state includes control values, current V4L2 pixel format, buffer queue, sequence counter, and device `vsvideo` register byte. Module parameters set initial brightness/contrast/gain. Control writes are sent to device registers but not permanently written; comments warn against the permanent-write index because it previously corrupted EEPROM.

## Dependencies And Integration Points
It integrates with USB bulk/control APIs, input polling and MT, V4L2 device/control/ioctl frameworks, videobuf2 DMA-SG memory, spinlocks/mutexes, and module parameters. It registers as a USB driver for Microsoft `045e:0775`.

## Risks
The driver mixes input polling with video frame acquisition: video frames are pulled only when input polling runs. Bulk endpoint assumptions are strict (`endpoint[4]` must be `0x86`). SUR40 vendor commands are sensitive; the code documents EEPROM corruption risk from wrong control recipient/index. Video buffer error paths must always return queued buffers; streaming stop uses `sequence = -1`. Touch packet packet-id checks are intentionally disabled because video acquisition can disturb IDs.

## Test Signals
Validate probe on the correct interface, evtest/libinput with many blob contacts, V4L2 capability/format/frame interval enumeration, `mmap`/read/DMABUF streaming, control writes for brightness/contrast/gain/backlight, buffer underrun behavior, disconnect cleanup, and absence of EEPROM-permanent writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sur40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c

## Purpose
`surface3_spi.c` drives N-trig/Microsoft Surface 3 touch and pen reports over SPI. It creates two input devices, one direct multitouch touchscreen and one pen device with pen/rubber/stylus state, then decodes fixed-size interrupt-driven SPI packets.

## Important APIs, Types, And Functions
`struct surface3_ts_data` stores the SPI device, two reset GPIO descriptors, touch and pen input devices, current pen tool, and a cacheline-aligned 264-byte read buffer. Packed report structures represent finger and pen payloads. `surface3_spi_read()` reads a full packet. `surface3_spi_process()` checks the static header and dispatches by report type (`0xd2` touch, `0x16` pen). `surface3_spi_report_touch()` uses tracking IDs as MT slot keys; `surface3_spi_report_pen()` reports proximity, touch, stylus, rubber/pen tool switching, X/Y, and pressure.

## Control Flow
Probe configures SPI mode 0 and 8 bits/word, allocates state, gets two indexed reset/power GPIOs, toggles power true/false/true, registers touch and pen input devices with fixed Surface 3 coordinate ranges/resolutions, and requests a threaded IRQ. Each IRQ reads one full packet and parses it. Touch processing starts at byte 17 and scans up to 13 finger records until a status end marker. Pen processing reads a pen record at byte 15 and syncs the pen input device.

## State And Persistence
The driver holds only runtime state: reset GPIOs, current pen tool, and input slots. Power is controlled by two GPIOs. Suspend disables IRQ and powers off; resume powers on and enables IRQ. There is no firmware upload or sysfs state.

## Dependencies And Integration Points
It integrates with SPI core, ACPI matching (`MSHW0037`), GPIO consumer APIs, threaded IRQs, input MT, and simple sleep PM. It sets Microsoft vendor/product IDs manually on the input devices.

## Risks
The header mismatch path logs an error but does not return, so a packet with a bad header is still dispatched by `data[9]`. Fixed offsets and coordinate ranges are hardware-specific. `input_report_key(dev, BTN_TOUCH, st & 0x12)` passes a bitmask rather than a normalized boolean, relying on input core boolean semantics. Tool switching fakes proximity-out to change between pen and rubber.

## Test Signals
Test touch and pen report packets, header-corrupt packets, up to ten touch slots despite scanning 13 records, pen/rubber switching, suspend/resume GPIO sequencing, IRQ storm behavior, and ACPI enumeration on Surface 3 hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/surface3_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sx8654.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/sx8654.c

## Purpose
`sx8654.c` supports Semtech SX8650/SX8654/SX8655/SX8656/SX8657 I2C resistive touchscreen controllers. It configures channel masks and pen-trigger conversion, reports single-touch X/Y through the input core, and handles pen release either via hardware release IRQ or a timer fallback.

## Important APIs, Types, And Functions
`struct sx865x_data` describes per-chip command, channel mask, release IRQ support, IRQ mask register availability, and IRQ handler. `struct sx8654` stores input device, client, optional reset GPIO, optional spinlock/timer for release fallback, touchscreen properties, and chip data. `sx8650_irq()` handles SX8650 conversion-ready data with channel-tagged 12-bit samples and schedules a release timer. `sx8654_irq()` handles IRQ source bits for release and touch conversion on newer chips. `sx8654_open()` enters pen-trigger mode and enables IRQ; `sx8654_close()` disables IRQ, deletes timer if needed, and returns to manual mode.

## Control Flow
Probe validates SMBus read-word support, gets optional reset GPIO, resolves chip data from OF/I2C ID, initializes timer/spinlock if no release IRQ, allocates input with direct property and ABS_X/ABS_Y/BTN_TOUCH, parses touchscreen properties, resets the controller, writes channel mask and optional IRQ mask, configures conditional IRQ/filter settings, requests threaded IRQ with `IRQF_NO_AUTOEN`, and registers input. Runtime begins only when input is opened.

## State And Persistence
State is volatile. The timer represents inferred pen-up state for SX8650-like parts. Open/close reprogram the controller mode. No sysfs or firmware state exists.

## Dependencies And Integration Points
The driver uses I2C/SMBus, GPIO reset, threaded IRQs, timers, spinlocks, input/touchscreen helpers, OF match data, and I2C IDs for multiple SX865x variants.

## Risks
SX8650 release detection is heuristic: no interrupt means pen-up after 10 ms. IRQ handlers intentionally ignore invalid high-bit/`0xffff` samples but still may report zeros if channels are missing. The I2C functionality check covers read-word, while handlers also use byte writes and `i2c_master_recv()`. Reset without GPIO relies on soft reset register behavior.

## Test Signals
Validate each match-data variant, reset GPIO and soft-reset paths, open/close IRQ enable behavior, hardware release IRQ versus timer release, channel mask X/Y parsing, touchscreen property transforms, and invalid/short I2C receive handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/sx8654.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c

## Purpose
`ti_am335x_tsc.c` is the touchscreen child driver for TI AM335x TSC/ADC MFD hardware. It configures sequencer steps for 4/5/8-wire resistive panels, reads averaged coordinates and pressure from FIFO0, shares an IRQ with the ADC function, and supports wakeup from pen-down.

## Important APIs, Types, And Functions
`struct titsc` stores the MFD pointer, input device, IRQ, DT wiring/plate/charge settings, decoded pin/input mapping, step mask, pen state, and wake device. `titsc_parse_dt()` reads `ti,wires`, `ti,x-plate-resistance`, `ti,coordinate-readouts` (plus legacy misspelling), `ti,charge-delay`, and `ti,wire-config`. `titsc_config_wires()` decodes analog line/wire order. `titsc_step_config()` programs sequencer steps for Y samples, Z samples, X samples, charge config, FIFO threshold, and cached step enable bits. `titsc_irq()` handles pen down/up, end-of-sequence, and FIFO0 threshold data.

## Control Flow
Probe obtains the parent `ti_tscadc_dev`, allocates state/input manually, parses DT, requests the shared IRQ, enables wakeup, sets wake IRQ, clears/enables IRQ bits, configures wires/steps/FIFO threshold, creates an ABS_X/ABS_Y/ABS_PRESSURE plus `BTN_TOUCH` input device, and registers it. IRQ processing marks pen-down on hardware pen IRQ, confirms pen-up only when ADC FSM is at `ADCFSM_STEPID`, reads coordinates when FIFO0 threshold fires, computes pressure from X, Z1/Z2, and X-plate resistance, reports only pressure values within 12-bit range, acknowledges IRQs, and refreshes the sequencer cache after EOS.

## State And Persistence
State is runtime-only but hardware sequencer configuration persists while the MFD block remains powered. Remove clears step-enable bits for this driver's steps, unregisters input, frees IRQ, and clears wake IRQ. Suspend enables hardware pen wake if allowed; resume disables wake bits and reprograms steps/FIFO threshold.

## Dependencies And Integration Points
It depends on the TI TSCADC MFD header/functions, OF bindings, shared IRQ handling, PM wake IRQ helpers, input core, MMIO register access, and sorting helpers for coordinate filtering.

## Risks
Manual allocation/free paths have more cleanup surface than devm drivers. Pressure formula uses unsigned arithmetic with `z = z1 - z2`; unexpected Z ordering can underflow and be filtered only if above `MAX_12BIT`. DT wire configuration is strict and can fail probe. ADC and touchscreen share IRQ and sequencer resources, so step masks must remain coordinated with the MFD/ADC users.

## Test Signals
Test 4/5/8-wire DT configurations, coordinate-readout bounds and legacy property warning, pressure across light/heavy touches, shared ADC IRQ behavior, suspend wake from pen, remove step-mask cleanup, and resume reprogramming after power loss.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ti_am335x_tsc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c

## Purpose
`touchit213.c` is a serio RS232 input driver for the Sahara TouchIT-213 serial touchscreen protocol. It decodes five-byte packets into 11-bit X/Y coordinates plus touch state and registers a simple absolute single-touch input device.

## Important APIs, Types, And Functions
`struct touchit213` stores input device, serio port, current packet index, an unused checksum byte, five-byte packet buffer, and physical path. `touchit213_interrupt()` is the byte-by-byte parser. `touchit213_connect()` allocates state and input, sets BUS_RS232 IDs, configures ABS_X/ABS_Y ranges `0..0x07ff`, opens the serio port, and registers input. `touchit213_disconnect()` unregisters input, closes serio, clears driver data, and frees state.

## Control Flow
The serio core matches `SERIO_RS232` with protocol `SERIO_TOUCHIT213`. Incoming byte 0 must have the status-byte pattern `0x80` ignoring the touch bit; otherwise the parser resets to index zero. On the fifth byte, it combines byte pairs as `(msb << 7) | lsb`, reports X, Y, `BTN_TOUCH` from the low bit of byte 0, syncs, and resets the packet index.

## State And Persistence
Only the in-progress packet buffer and index are retained. No calibration, sysfs, firmware, or PM state exists. Input device lifetime is tied to serio connection lifetime.

## Dependencies And Integration Points
The driver integrates solely with the serio bus and input core. It uses the serio protocol ID to bind to line-discipline-created devices and reports BUS_RS232 identity.

## Risks
There is no checksum despite the `csum` member. A lost byte can desynchronize until a new valid status byte appears. The comments mention Touchright in the connect description, inherited from the older driver. Axis orientation/calibration is left to userspace.

## Test Signals
Feed valid and invalid five-byte sequences through serio, verify resync on bad first byte, confirm press and release packets, check 11-bit coordinate limits, and test connect/disconnect cleanup with input users open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchit213.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c

## Purpose
`touchright.c` is a legacy serio RS232 driver for Touchright serial touchscreens. It decodes fixed five-byte packets into 9-bit X/Y coordinates and reports absolute single-touch events through the input subsystem.

## Important APIs, Types, And Functions
`struct tr` stores input device, serio port, current packet index, five-byte packet buffer, and physical path. `tr_interrupt()` parses incoming bytes. `tr_connect()` allocates state/input, assigns BUS_RS232 IDs with vendor `SERIO_TOUCHRIGHT`, sets ABS_X/ABS_Y ranges `0..0x1ff`, opens the serio port, and registers the input device. `tr_disconnect()` unregisters input, closes serio, clears driver data, and frees memory.

## Control Flow
The serio driver binds to `SERIO_RS232` protocol `SERIO_TOUCHRIGHT`. For each byte, the parser stores it in `data[idx]`. If the first byte has the required status pattern `0x40` ignoring the touch bit, the index advances. Once five bytes are present, X is `(data[1] << 5) | (data[2] >> 1)`, Y is `(data[3] << 5) | (data[4] >> 1)`, touch state is bit 0 of byte 0, and the input frame is synced.

## State And Persistence
State is limited to packet assembly and input lifetime. The driver stores no calibration or persistent settings and has no PM hooks.

## Dependencies And Integration Points
It uses the serio bus, input core, module serio registration, and protocol IDs. It assumes userspace handles calibration/rotation if raw coordinate orientation differs from display orientation.

## Risks
If `data[0]` is invalid, `idx` does not advance but the current byte remains in slot zero, so resynchronization depends on a future byte matching the status pattern. There is no checksum or timeout-based packet reset. Coordinates are reported raw.

## Test Signals
Test valid press/release packet decoding, invalid leading-byte recovery, max/min coordinate values, serio open failure cleanup, and disconnect while the input device is referenced.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchright.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchwin.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchwin.c

## Purpose
`touchwin.c` is a serio RS232 driver for Touchwindow serial touchscreens. It handles a very small protocol where idle/release is represented by zero bytes and touches are represented by three nonzero bytes: X, Y, and a duplicate Y.

## Important APIs, Types, And Functions
`struct tw` stores input device, serio port, packet index, current touched flag, three-byte packet buffer, and physical path. `tw_interrupt()` is the protocol parser and reporter. `tw_connect()` allocates state/input, sets BUS_RS232 IDs with vendor `SERIO_TOUCHWIN`, configures 8-bit ABS_X/ABS_Y ranges, opens the serio device, and registers input. `tw_disconnect()` performs the inverse cleanup.

## Control Flow
The serio match table binds RS232 protocol `SERIO_TOUCHWIN`. Every nonzero byte is treated as part of a touch packet; the driver sets `touched`, appends the byte, and when three bytes are collected with byte 1 equal to byte 2, reports X from byte 0, Y from byte 1, `BTN_TOUCH = 1`, syncs, and resets the index. A zero byte after a touch reports `BTN_TOUCH = 0`, syncs, clears index, and clears `touched`.

## State And Persistence
Only the current packet index and `touched` boolean persist across interrupts. There are no persistent settings, calibration, firmware, sysfs, or power hooks.

## Dependencies And Integration Points
The driver depends on serio protocol enumeration and the input core. It reports raw coordinates and leaves scaling/calibration to userspace.

## Risks
Repeated nonzero noise can hold `touched` true and fill the packet buffer until a valid duplicate-Y packet is seen. If three bytes are collected but Y duplication fails, the code does not reset `idx`, so further nonzero bytes can index beyond `data[3]`; this is a notable parser robustness risk in malformed streams. There is no checksum.

## Test Signals
Test valid `X,Y,Y` touch packets, zero-byte release after a touch, streams of idle zeros, malformed nonzero streams with mismatched Y duplicate, coordinate bounds, and serio disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/touchwin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c

## Purpose
`tps6507x-ts.c` is the touchscreen child driver for TPS65070/073/731/732 PMICs with a 10-bit touchscreen ADC. It exposes a polled single-touch input device, reads pressure/X/Y through the parent MFD register operations, and returns the ADC to standby after each poll so the PMIC touch interrupt path remains usable.

## Important APIs, Types, And Functions
`struct tps6507x_ts` stores the device, input device, parent `struct tps6507x_dev`, physical path, current `ts_event`, minimum pressure threshold, and pen-down state. `tps6507x_read_u8()` and `tps6507x_write_u8()` wrap parent MFD callbacks. `tps6507x_adc_conversion()` selects a touchscreen channel, starts conversion, polls the start bit until completion, and reads the 10-bit result from two ADC result registers. `tps6507x_adc_standby()` restores standby and waits for `TPS6507X_REG_TSC_INT` to clear. `tps6507x_ts_poll()` is the input polling handler.

## Control Flow
Probe obtains parent PMIC data and board/platform touchscreen init data, allocates state/input, sets min pressure from platform data or default, configures BUS_I2C identity, ABS_X/ABS_Y/ABS_PRESSURE ranges `0..1023`, calls ADC standby, installs input polling, sets poll interval from platform data or 30 ms, and registers input. On each poll, pressure is read first. If pressure falls below threshold and the driver believed the pen was down, it reports release. If pressure is above threshold, it reads X and Y, reports down if needed, reports coordinates and pressure, syncs, marks pen down, then always returns the ADC to standby.

## State And Persistence
State is volatile. Board data supplies optional IDs, poll interval, and pressure threshold. The ADC mode is repeatedly changed during polling and restored to standby each time. There are no sysfs controls or PM hooks in this child driver.

## Dependencies And Integration Points
It integrates with the TPS6507x MFD API, legacy platform data (`tps6507x_board` and `touchscreen_init_data`), input polling, and platform-driver registration. It is not DT/property-driven in this file.

## Risks
Conversion polling is a busy loop without an explicit timeout; a stuck `START_CONVERSION` bit can hang the polling callback. Probe requires platform data and returns `-ENODEV` if absent. The driver ignores direct PMIC interrupts and relies on polling. ADC standby errors after a failed conversion are not surfaced to input users.

## Test Signals
Validate platform data presence/defaults, pressure threshold transitions, ADC channel reads for pressure/X/Y, standby after every poll, stuck conversion behavior, poll interval configuration, and input release when pressure drops below threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tps6507x-ts.c -->
