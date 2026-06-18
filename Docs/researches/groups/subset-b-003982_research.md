# subset-b-003982 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ts4800-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/ts4800-ts.c

## Purpose
`ts4800-ts.c` is a platform input driver for the Technologic TS-4800 board touchscreen. It polls two memory-mapped 12-bit coordinate registers and uses a syscon bit to enable or disable the board touchscreen block.

## Important APIs, Types, And Functions
`struct ts4800_ts` stores the input device, mapped register base, syscon regmap/bit, pen state, and debounce counter. `ts4800_parse_dt()` resolves the `syscon` phandle plus offset/bit arguments. `ts4800_ts_open()` and `ts4800_ts_close()` toggle the syscon enable bit. `ts4800_ts_poll()` reads X/Y registers, extracts the pen-down bit from X, inverts/shifts coordinates, and reports `BTN_TOUCH`, `ABS_X`, and `ABS_Y`.

## Control Flow
Probe parses DT, maps the platform MMIO resource, allocates a polled input device, configures absolute axes from 0 to `MAX_12BIT`, installs the poll callback at a 3 ms interval, and registers the input device. Open resets debounce state and enables the hardware. The poll callback suppresses the first down sample, reports coordinates while pressed, and reports release only after a prior down state.

## State And Persistence
All state is runtime-only: the syscon enable bit is hardware state, while `pendown` and `debounce` are in-memory filters. No calibration or persistent configuration is stored.

## Dependencies And Integration Points
The driver depends on platform resources, OF `technologic,ts4800-ts`, syscon/regmap, MMIO `readw()`, and the input polling helper.

## Risks
The syscon property must contain exactly the expected phandle, offset, and bit index. Coordinate decoding assumes the board register format with inverted upper 12 bits and pen-down in bit 0. There is no explicit PM hook, so correctness across suspend depends on input close/open or parent hardware handling.

## Test Signals
Test DT parse failures, syscon enable/disable errors, MMIO resource mapping, first-sample debounce, down/move/up event sequences, coordinate inversion boundaries, and close while pressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/ts4800-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2004.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2004.c

## Purpose
`tsc2004.c` is the I2C bus glue for the TI TSC2004 touchscreen controller. It delegates common touchscreen behavior to `tsc200x-core.c` and supplies I2C regmap and command transport.

## Important APIs, Types, And Functions
`tsc2004_input_id` identifies the input bus/product as I2C/TSC2004. `tsc2004_cmd()` constructs a TSC200x command byte with command and 12-bit mode bits and sends it with `i2c_smbus_write_byte()`. `tsc2004_probe()` calls `tsc200x_probe()` with the device IRQ, shared regmap config, and command callback.

## Control Flow
The I2C core matches either `"tsc2004"` or OF compatible `ti,tsc2004`. Probe creates the regmap through `devm_regmap_init_i2c()` and immediately transfers ownership of setup, input registration, IRQ handling, power, and PM to the shared core.

## State And Persistence
This file keeps no private runtime state. All mutable controller state is in the shared `struct tsc200x` allocated by the core. Bus-level state is limited to transient SMBus command writes.

## Dependencies And Integration Points
It depends on I2C, regmap, OF matching, `tsc200x_regmap_config`, `tsc200x_groups`, and `tsc200x_pm_ops`.

## Risks
Any bus-specific command formatting mistake affects scan start/stop without being visible in this wrapper. The file has no I2C functionality check of its own and relies on regmap/core failures for diagnostics.

## Test Signals
Test I2C and OF matching, SMBus command error propagation, missing IRQ rejection through the core, sysfs group visibility inherited from the core, and suspend/resume callback wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2004.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2005.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2005.c

## Purpose
`tsc2005.c` is the SPI bus glue for TI TSC2005 controllers. It configures SPI transfer parameters and delegates controller behavior to the shared TSC200x core.

## Important APIs, Types, And Functions
`tsc2005_input_id` identifies SPI/TSC2005. `tsc2005_cmd()` sends a single 8-bit command transfer using `spi_sync()`. `tsc2005_probe()` forces SPI mode 0, 8 bits per word, applies a default 10 MHz max speed when unset, runs `spi_setup()`, creates a SPI regmap, and calls `tsc200x_probe()`.

## Control Flow
The SPI driver matches OF compatible `ti,tsc2005` or alias `spi:tsc2005`. After bus setup, the shared core handles reset GPIOs, regulators, IRQs, input registration, ESD recovery, sysfs self-test, and PM.

## State And Persistence
This wrapper has no long-lived private state. Persistent runtime configuration lives in the SPI device settings and the core's `struct tsc200x`.

## Dependencies And Integration Points
It integrates SPI, regmap, OF matching, the shared TSC200x symbols, core PM ops, and core device groups.

## Risks
Boards with non-default SPI constraints may be affected by the default max speed. Command delivery is a raw one-byte SPI message; bus setup or chip-select timing errors surface only as core behavior failures.

## Test Signals
Test SPI setup failures, default speed assignment, command transfer error handling, OF/module alias matching, core probe failure paths, and suspend/resume through `tsc200x_pm_ops`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2005.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007.h

## Purpose
`tsc2007.h` defines the shared command constants, event structures, controller state, and helper prototypes for the TSC2007 input driver and its optional IIO extension.

## Important APIs, Types, And Functions
The command macros encode measurement, power, IRQ, and resolution modes, including `READ_X`, `READ_Y`, `READ_Z1`, `READ_Z2`, and `PWRDOWN`. `struct ts_event` carries raw X/Y/Z samples. `struct tsc2007` stores input/I2C handles, touchscreen properties, pressure and plate settings, GPIO/IRQ state, wait queue, platform callbacks, and `mlock` shared by input IRQ and IIO reads. Prototypes expose transfer, resistance, pendown, and IIO configuration helpers.

## Control Flow
The header is included by `tsc2007_core.c` and `tsc2007_iio.c`. Compile-time `CONFIG_TOUCHSCREEN_TSC2007_IIO` selects either real IIO registration or a no-op inline.

## State And Persistence
The header itself has no state, but defines all fields used to hold runtime-only configuration parsed from firmware or platform data. No field represents nonvolatile persistence.

## Dependencies And Integration Points
It depends on Linux input touchscreen properties, optional GPIO descriptors, I2C implementation details in the core, and optional IIO implementation.

## Risks
Macro encoding is central to both input and IIO paths; changing bit definitions can silently break hardware sequencing. `MAX_12BIT` may collide conceptually with other touchscreen headers but is guarded by file scope inclusion.

## Test Signals
Build with and without `CONFIG_TOUCHSCREEN_TSC2007_IIO`, verify command values against datasheet expectations, and test users of `struct tsc2007` across platform-data and firmware-property probe paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_core.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_core.c

## Purpose
`tsc2007_core.c` is an I2C input driver for TI TSC2007-style resistive touch controllers. It samples raw X/Y/Z values, computes touch resistance, reports input events, supports legacy platform data, and optionally exposes raw channels through IIO.

## Important APIs, Types, And Functions
`tsc2007_xfer()` performs SMBus word reads and fixes the controller's byte/nibble ordering. `tsc2007_read_values()` sequences Y, X, Z1, Z2, then powers down with pen IRQ enabled. `tsc2007_calculate_resistance()` computes resistance from X/Z values and `x_plate_ohms`. `tsc2007_soft_irq()` loops while pen is down, filters pressure by `max_rt`, reports transformed coordinates, and sleeps for `poll_period`. Probe helpers parse firmware properties or `tsc2007_platform_data`.

## Control Flow
Probe checks SMBus word support, allocates state and input device, parses properties, registers optional platform cleanup, requests a threaded IRQ, powers the chip down, registers input, then calls `tsc2007_iio_configure()`. Open enables IRQ and prepares pen IRQ mode; close sets `stopped`, wakes the wait queue, and disables the IRQ. The IRQ thread serializes ADC accesses with `mlock`, reports down samples, and emits a final release.

## State And Persistence
Settings such as fuzz, max resistance, poll period, plate resistance, and touchscreen transform are parsed once and kept in memory. `stopped` controls the IRQ thread, while callbacks or GPIO provide pendown state. No persistent storage is used.

## Dependencies And Integration Points
It uses I2C SMBus, input core, touchscreen property parsing, optional GPIO descriptors, firmware properties, legacy platform data, wait queues, threaded IRQs, and optional IIO.

## Risks
Without a pendown GPIO/callback, release detection falls back to zero pressure and may be hardware-sensitive. The IRQ is requested before input registration and disabled through `tsc2007_stop()`, so enable/disable balance matters. IIO reads and IRQ sampling share the ADC and depend on `mlock` for serialization.

## Test Signals
Test property validation for `ti,x-plate-ohms`, GPIO pendown and no-GPIO modes, pressure filtering, open/close IRQ balancing, I2C error paths, platform callbacks, input transforms, IIO-enabled builds, and repeated suspend-like close/open cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_iio.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_iio.c

## Purpose
`tsc2007_iio.c` adds an optional IIO direct-mode interface for TSC2007 raw ADC channels, touch resistance, pen state, and temperature inputs.

## Important APIs, Types, And Functions
`struct tsc2007_iio` links an IIO device to the existing `struct tsc2007`. `tsc2007_iio_channel[]` declares x, y, z1, z2, aux ADC, resistance, pen, temp0, and temp1 channels. `tsc2007_read_raw()` validates raw reads, serializes on `tsc->mlock`, issues the proper TSC2007 command sequence, computes resistance for channel 5, and powers down afterward. `tsc2007_iio_configure()` allocates and registers the IIO device with devm lifetime.

## Control Flow
The core calls `tsc2007_iio_configure()` after input registration. Each IIO read directly talks to the controller; it does not claim input device state, but it does take the ADC mutex shared with the input IRQ thread.

## State And Persistence
The IIO layer stores only a pointer to core state. It has no cache, no persistent settings, and reuses core calibration/resistance parameters.

## Dependencies And Integration Points
It depends on IIO direct mode, I2C command helpers from `tsc2007_core.c`, and the shared mutex in `struct tsc2007`.

## Risks
Individual `tsc2007_xfer()` errors are assigned into `*val` without a per-command negative return check, so failed reads can be reported as integer values. IIO reads can perturb pen IRQ power state, though the final `PWRDOWN` tries to restore it.

## Test Signals
Test all channel raw reads, invalid masks/channels, concurrent touch IRQ and IIO reads, I2C failure propagation expectations, and builds where the optional IIO config is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc2007_iio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.c

## Purpose
`tsc200x-core.c` implements the shared controller logic for TSC2004 and TSC2005 resistive touchscreen drivers. It manages regmap register access, scan start/stop, IRQ-driven samples, pen-up detection, ESD recovery, self-test, regulator/reset handling, and PM.

## Important APIs, Types, And Functions
`tsc200x_regmap_config` defines 8-bit register, 16-bit value, read/write flag, and writable-register constraints. `struct tsc200x` keeps device/regmap/input state, last raw sample, locks, pen-up timer, ESD work, reset GPIO, IRQ, and bus command callback. `tsc200x_irq_thread()` bulk-reads X/Y/Z data, validates ranges, computes pressure, and reports input. `tsc200x_start_scan()` writes CFR registers and sends normal command. `tsc200x_do_selftest()` verifies register write/read and hardware reset behavior.

## Control Flow
Bus wrappers call `tsc200x_probe()`, which validates IRQ/regmap/cmd callback, reads properties, allocates input state, configures reset GPIO and `vio` regulator, resets and stops scanning, requests a threaded IRQ, registers input, and initializes wakeup. Input open enables scanning and optional ESD work; close disables scanning, IRQ, timers, and work. The pen-up timer emits release if no fresh IRQ arrives within 40 ms.

## State And Persistence
Runtime state includes opened/suspended flags, pen state, last raw sample for stale-data filtering, ESD timing, wake IRQ state, and cached touchscreen properties. Hardware configuration is rewritten on each scan start. No nonvolatile data is modified.

## Dependencies And Integration Points
The core integrates with regmap, input/touchscreen properties, threaded IRQs, timers, delayed work, optional reset GPIO, regulator `vio`, firmware properties `ti,x-plate-ohms`, `ti,esd-recovery-timeout-ms`, and bus wrappers for I2C/SPI command transport.

## Risks
Pressure arithmetic is integer and range-sensitive. The self-test is visible only when a reset GPIO exists and temporarily disables the device. ESD work reschedules itself and must not race with close/suspend. `__tsc200x_disable()` uses IRQ/timer/work cancellation paths that require valid IRQ state.

## Test Signals
Test valid and invalid sample packets, stale first sample suppression, pressure bounds, timer-based release, ESD reset recovery, selftest sysfs, reset/regulator failures, wakeup-source suspend/resume, and concurrent open/close with IRQ activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.h -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.h

## Purpose
`tsc200x-core.h` provides register addresses, command bits, default tuning constants, and exported interfaces shared by TSC2004/TSC2005 wrappers and the TSC200x core.

## Important APIs, Types, And Functions
The header defines command byte bits (`TSC200X_CMD_*`), register selector values, configuration register defaults (`TSC200X_CFR0_INITVALUE`, `CFR1`, `CFR2`), masks, default fuzz/resistance values, SPI speed, and pen-up timeout. It declares `tsc200x_regmap_config`, `tsc200x_pm_ops`, `tsc200x_groups`, and `tsc200x_probe()`.

## Control Flow
Bus-specific drivers include this header, create a regmap using the shared config, and call `tsc200x_probe()` with a bus command callback. PM and sysfs groups are wired into bus driver structures through these declarations.

## State And Persistence
The header defines constants only. Runtime state is allocated in `tsc200x-core.c`; persistent storage is not involved.

## Dependencies And Integration Points
It is the contract between I2C/SPI wrappers and the common core, and implicitly encodes controller datasheet register layout.

## Risks
Register stride, command bits, and writable masks must remain synchronized with `tsc200x_regmap_config`. Constants are shared across both TSC2004 and TSC2005, so variant-specific behavior should not be added here without care.

## Test Signals
Build both bus drivers, validate regmap addresses/flags on hardware or emulation, verify PM group linkage, and check scan configuration writes match expected datasheet defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc200x-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc40.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc40.c

## Purpose
`tsc40.c` is a serio/RS232 input driver for TSC-10, TSC-25, and TSC-40 serial touchscreens. It parses fixed five-byte packets and reports single-touch absolute coordinates.

## Important APIs, Types, And Functions
`struct tsc_ser` stores serio/input handles, packet index, five-byte buffer, and physical path. `tsc_interrupt()` is the byte-at-a-time parser and resynchronizer. `tsc_process_data()` decodes 10-bit X/Y coordinates and reports `BTN_TOUCH`. `tsc_connect()` allocates devices, opens serio, and registers input; `tsc_disconnect()` reverses that setup.

## Control Flow
The serio core matches `SERIO_RS232` with protocol `SERIO_TSC40`. Incoming bytes are accumulated from a validated start byte. A start byte with pen-up bit clear emits release immediately. Invalid high bits in coordinate bytes reset the parser. A complete packet emits X/Y/down events.

## State And Persistence
Parser state is just `idx` plus the current data buffer. There is no calibration, persistent configuration, or PM state.

## Dependencies And Integration Points
It depends on the serio bus and input subsystem. It exposes a RS232 input device with 0..0x3ff X/Y axes.

## Risks
The parser reports down for every complete coordinate packet but only reports up from a specific first-byte condition. Noise can cause resynchronization drops. No pressure or debounce filtering is present.

## Test Signals
Test connect/open/register failures, valid packets, pen-up first-byte packet, malformed start and coordinate bytes, stream resynchronization, and disconnect during partial packet reception.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/tsc40.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/usbtouchscreen.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/usbtouchscreen.c

## Purpose
`usbtouchscreen.c` is a USB input driver supporting many legacy single-touch USB touchscreen protocols. It maps USB IDs to per-device packet parsers and initializers, then uses a common URB pipeline to report `BTN_TOUCH`, coordinates, and optional pressure.

## Important APIs, Types, And Functions
`struct usbtouch_device_info` describes coordinate ranges, report size, packet-length parser, data parser, init/exit hooks, and whether IRQ URBs run even when the input device is closed. `struct usbtouch_usb` stores DMA buffers, URB, input device, PM mutex, packet buffer, parser state, and current decoded sample. Device-specific functions decode eGalax, EasyTouch, PanJit, 3M/MicroTouch, ITM, eTurbo, Gunze, DMC, IRTOUCH, ET&T, IdealTEK, General Touch, GoTop, JASTEC, Zytronic, Nexio, Elo, and E2I protocols.

## Control Flow
Probe ignores HID-capable devices assigned to usbhid, finds interrupt or bulk IN endpoint, allocates coherent URB buffers, installs single or multipacket processing, runs optional allocation/init hooks, registers input, and optionally starts always-on URBs. `usbtouch_irq()` decodes successful URBs and resubmits. Open gets runtime PM and starts IO; close kills URBs when not always-on and drops remote wakeup. Suspend kills the URB, resume restarts when needed, and reset-resume reruns device init.

## State And Persistence
State includes input open status, runtime PM wakeup needs, multipacket buffer length, decoded X/Y/touch/pressure, and device-specific private data such as firmware revision or Nexio ACK URB. Module parameters `swap_xy` and `hwcalib_xy` alter reporting globally at runtime. No nonvolatile device storage is changed.

## Dependencies And Integration Points
It integrates USB core, input core, runtime autosuspend, USB control/bulk/interrupt messaging, optional sysfs firmware revision for 3M devices, and Kconfig-selected protocol blocks.

## Risks
Many protocol parsers trust packet sizes selected by device info; malformed devices can exercise edge cases in multipacket buffering. Always-on IRQ devices consume bandwidth and require careful disconnect/PM cleanup. Module-global axis/calibration parameters affect every bound device. Some init paths use vendor control transfers with legacy timing expectations.

## Test Signals
Test every enabled USB ID path, endpoint fallback from interrupt to bulk, multipacket framing and partial packets, open/close PM races, suspend/resume/reset-resume, disconnect during active URB, pressure reporting, axis swap/hw calibration parameters, Nexio ACK handling, and 3M firmware sysfs visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/usbtouchscreen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_i2c.c

## Purpose
`wacom_i2c.c` is an I2C input driver for Wacom EMR pen digitizers. It queries feature report 3 for device limits and reports stylus proximity, buttons, eraser, coordinates, and pressure from interrupt packets.

## Important APIs, Types, And Functions
`struct wacom_features` holds max X/Y/pressure and firmware version. `struct wacom_i2c` stores client/input, receive buffer, proximity state, and current tool. `wacom_query_device()` sends an I2C feature-report request and decodes little-endian feature fields. `wacom_i2c_irq()` receives a 19-byte report and emits `BTN_TOOL_PEN`, `BTN_TOOL_RUBBER`, `BTN_TOUCH`, stylus buttons, `ABS_X`, `ABS_Y`, and `ABS_PRESSURE`.

## Control Flow
Probe validates plain I2C support, queries features, allocates input state, configures axes and keys, requests a threaded IRQ, disables it until open, and registers input. Open enables the IRQ; close disables it. PM suspend disables the IRQ and resume enables it unconditionally.

## State And Persistence
Runtime state tracks whether a tool is in proximity and whether the current tool is pen or rubber. Device features are read at probe and used for input limits. No persistent configuration is written.

## Dependencies And Integration Points
It depends on I2C transfers, unaligned little-endian helpers, threaded IRQs, and input stylus event conventions.

## Risks
Resume enables IRQ even if the input device was closed before suspend, which may alter IRQ balance depending on PM path. The IRQ handler ignores short positive reads and treats all errors as handled. Feature version is stored in a `char`, though read as 16-bit.

## Test Signals
Test query transfer failures and short transfer detection, open/close IRQ balancing, pen versus eraser transitions, button/proximity reports, suspend/resume while closed and open, and malformed packet lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_w8001.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_w8001.c

## Purpose
`wacom_w8001.c` is a serio driver for Wacom W8001 serial penabled/touch devices. It can register separate pen and finger input devices, support one- or two-finger touch packets, and scale touch coordinates to pen coordinates when both capabilities exist.

## Important APIs, Types, And Functions
`struct w8001` stores pen/touch input devices, serio state, command completion, response/data buffers, packet lengths, maximum pen/touch dimensions, current tool type, open count, and mutex. `parse_pen_data()`, `parse_single_touch()`, `parse_multi_touch()`, and `parse_touchquery()` decode protocol packets. `w8001_command()` sends start/stop/query commands and optionally waits for a control response. Setup functions query pen and touch capabilities and initialize input axes/MT slots.

## Control Flow
Connect allocates state and both input devices, opens serio, stops/query-detects the controller, probes pen and touch support, registers whichever devices are present, and composes names based on capabilities. The interrupt parser accumulates serial bytes, validates leading bits, dispatches complete pen/touch/control/multitouch packets, and completes command queries. Open starts the device on the first opener; close stops it after the last input device closes.

## State And Persistence
State includes partial packet index, command response, open count shared by pen and touch devices, current tool classification, and learned maximum dimensions. No persistent hardware settings are stored.

## Dependencies And Integration Points
It uses serio, completions, input MT slot helpers, input absolute resolution metadata, and Wacom serial protocol IDs.

## Risks
Pen and touch devices share one serial stream and open count, so error paths must avoid double-free or premature stop. Tool disambiguation for eraser versus second stylus button is heuristic. Query timeouts return `-EIO`; noisy serial streams can desynchronize packet parsing.

## Test Signals
Test pen-only, touch-only, combined, and 2FG devices; command timeout paths; packet resynchronization; shared open/close ordering; eraser transition behavior; MT slot reporting; and connect failure unwinding after one device registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wacom_w8001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wdt87xx_i2c.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wdt87xx_i2c.c

## Purpose
`wdt87xx_i2c.c` is an I2C multitouch driver for Weida HiTech WDT87xx controllers. It reports up to ten contacts and exposes sysfs-triggered firmware/configuration update operations using vendor feature reports.

## Important APIs, Types, And Functions
`struct wdt87xx_sys_param` caches firmware/platform IDs, physical dimensions, scaling factor, logical max coordinates, and USB-style VID/PID. `struct wdt87xx_data` stores client, input, firmware mutex, parameters, and phys string. Descriptor/string/feature helpers implement the vendor protocol over I2C. Firmware helpers validate RIFF/WHIF chunks, unlock flash, erase/write 4 KiB pages, compare MISR checksums, relock, reset, and refresh parameters. `wdt87xx_ts_interrupt()` reads V1 touch packets and `wdt87xx_report_contact()` reports MT slots.

## Control Flow
Probe checks plain I2C, allocates state, reads system parameters from descriptors and strings, creates the MT input device, then requests a threaded IRQ. Sysfs `update_fw` and `update_config` request firmware files, validate them against the chip ID, lock `fw_mutex`, disable IRQ, load the selected chunk, reset, and refresh parameters. Suspend disables IRQ and sends idle/stop; resume waits, restarts reporting, and enables IRQ.

## State And Persistence
Runtime state includes cached controller parameters and firmware metadata. Firmware/config update paths persistently write controller flash. The driver caches no contact state beyond input MT tracking.

## Dependencies And Integration Points
It depends on I2C raw transfers, input MT, firmware loader files `wdt87xx_fw.bin` and `wdt87xx_cfg.bin`, ACPI ID `WDHT0001`, sysfs device attributes, unaligned access helpers, and system sleep PM.

## Risks
Firmware update is high-risk: malformed chunks, checksum mismatch, interrupted writes, or lock/start failure can leave the device unusable. Sysfs update stores ignore input text and trigger immediately. `wdt87xx_report_contact()` drops inactive contacts and relies on `INPUT_MT_DROP_UNUSED` for cleanup. Parameter-derived Y scaling can divide by physical width, so bad descriptor values matter.

## Test Signals
Test descriptor parsing, sysfs read attributes, IRQ packet parsing for valid/invalid contacts, firmware validation failures, page checksum retry logic, IRQ disable during update, suspend/resume command failures, ACPI matching, and recovery after reset/parameter refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wdt87xx_i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm831x-ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm831x-ts.c

## Purpose
`wm831x-ts.c` is a platform input driver for the touchscreen block inside WM831x PMICs. It alternates between pen-detect and data IRQ modes and reports X/Y plus optional pressure.

## Important APIs, Types, And Functions
`struct wm831x_ts` stores the input device, parent WM831x handle, data and pen-down IRQs, pressure enable, pen state, and work item used to re-enable the opposite IRQ after state transitions. `wm831x_ts_pen_down_irq()` enables data collection on pen down. `wm831x_ts_data_irq()` reads X/Y/Z registers, reports samples, detects release, disables data IRQ, and re-enables pen detect via work. Input open/close enable or shut down the touchscreen registers.

## Control Flow
Probe obtains parent MFD data and optional touch platform data, resolves IRQs, configures five-wire/current/rate bits, requests a no-auto-enable data IRQ and an enabled pen IRQ, initializes input axes, and registers input. During use, pen IRQ starts coordinate conversion; data IRQ reports until a sample lacks the pen-down bit, then returns to pen-detect mode.

## State And Persistence
Hardware register bits hold mode/rate/current configuration. Runtime `pen_down` selects which IRQ should be enabled. No persistent storage is used.

## Dependencies And Integration Points
It depends on the WM831x MFD core, WM831x IRQ mapping, optional platform data, direct register/bulk access helpers, workqueues, and input core.

## Risks
IRQ transition correctness is subtle because handlers disable IRQs and schedule work to re-enable the counterpart. Remove frees IRQs but does not flush pending work explicitly. Five-wire mode suppresses pressure even if platform data requested it.

## Test Signals
Test platform data overrides, direct versus mapped IRQs, pressure and five-wire modes, pen-down to data IRQ switching, release reporting, input close while pen is down, IRQ request failure unwinding, and remove with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm831x-ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9705.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9705.c

## Purpose
`wm9705.c` provides WM9705-specific touchscreen codec operations for the WM97xx core. It configures the AC97 digitizer, implements polling samples, optional pressure, AUX preparation, and continuous mode.

## Important APIs, Types, And Functions
Module parameters tune pressure current `pil`, pressure threshold, ADC delay, pen detect comparator `pdd`, and mask behavior. `wm9705_phy_init()` mutes shared AUX/VIDEO inputs and writes digitizer registers. `wm9705_poll_sample()` performs a polling ADC conversion with pen-down validation. `wm9705_poll_touch()` reads X/Y and optional pressure. `wm9705_acc_enable()` configures AC97 slot streaming for continuous mode. `wm9705_codec` exports callbacks to the core.

## Control Flow
The WM97xx core selects this codec by vendor ID and calls `phy_init()`. During input open, the core enables the digitizer and uses either polling callbacks or machine accelerated mode. AUX reads call `aux_prepare()` and restore the saved digitizer state afterward.

## State And Persistence
State is held in module parameters and cached core digitizer arrays `wm->dig`/`dig_save`. Register writes configure hardware only for the current boot/module lifetime.

## Dependencies And Integration Points
It depends on `linux/wm97xx.h`, AC97 register access wrappers from `wm97xx-core.c`, and optional machine acceleration callbacks.

## Risks
Module parameters are global and not per-device. Delay bounds are corrected at runtime. Polling timeout behavior depends on whether pen-detect is enabled. Continuous mode assumes valid machine ops and AC97 slot/rate configuration.

## Test Signals
Test parameter boundary values, pressure disabled/enabled, timeout and wrong-sample paths, AUX prepare/restore, continuous mode start/shutdown callbacks, and integration through the WM97xx core's input reader.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9705.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9712.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9712.c

## Purpose
`wm9712.c` implements WM9712-specific operations for the WM97xx AC97 touchscreen core, including four/five-wire setup, coordinate polling, optional pressure, GPIO mask support, and continuous mode.

## Important APIs, Types, And Functions
Module parameters control pull-up resistor `rpu`, pressure current `pil`, pressure threshold, sample delay, five-wire mode, mask mode, and coordinate polling. `wm9712_phy_init()` programs digitizer registers and optional GPIO4 mask. `wm9712_poll_sample()` reads single ADC samples with retry/pen validation. `wm9712_poll_coord()` reads combined coordinate mode. `wm9712_poll_touch()` selects coordinate or per-axis polling. `wm9712_acc_enable()` configures AC97 continuous streaming.

## Control Flow
The WM97xx core selects `wm9712_codec` by ID and calls codec callbacks from input open, poll work, AUX reads, and accelerated machine paths. If five-wire mode is enabled, pressure current is disabled because pressure is unsupported.

## State And Persistence
Module parameters and cached digitizer registers form runtime state. Hardware settings are rewritten during init, enable, AUX prepare/restore, and continuous-mode changes. No nonvolatile storage is changed.

## Dependencies And Integration Points
It integrates with the WM97xx core, AC97 register constants, machine ops for pre/post sample and acceleration, and GPIO configuration for mask mode.

## Risks
Global module parameters can conflict on systems with multiple codecs. `wm9712_poll_coord()` returns `0` on malformed channel tags, which the core treats separately from explicit flags. Five-wire and pressure options interact and must be validated together.

## Test Signals
Test four-wire/five-wire, pressure current modes, coordinate versus per-axis polling, mask GPIO programming, wrong-sample `RC_AGAIN`, continuous mode with and without machine ops, and suspend/resume through cached registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9712.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9713.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9713.c

## Purpose
`wm9713.c` provides WM9713-specific touchscreen operations for the WM97xx core. It handles the WM9713 digitizer register layout, optional five-wire panels, pressure current, polling and coordinate modes, and AC97 continuous mode.

## Important APIs, Types, And Functions
Module parameters mirror WM9712-style tuning for `rpu`, `pil`, pressure, delay, five-wire, mask, and coordinate mode. `wm9713_phy_init()` writes DIG1/DIG2/DIG3, stores the WM9713 misc register, and clears GPIO sticky state. `wm9713_dig_enable()` also manages the `AC97_EXTENDED_MID` power bit. `wm9713_poll_sample()` translates WM97xx ADC selectors into WM9713 selector bits. `wm9713_poll_coord()` and `wm9713_acc_enable()` implement combined polling and continuous streaming.

## Control Flow
The WM97xx core selects this codec from vendor ID, initializes physical registers, then uses callbacks during input open/close, delayed polling, AUX reads, suspend/resume, and optional acceleration. The codec-specific restore callback rewrites all three digitizer registers.

## State And Persistence
Runtime state is module parameters plus cached digitizer and misc registers in `struct wm97xx`. Hardware register state is restored by core PM paths. There is no persistent storage.

## Dependencies And Integration Points
It depends on WM97xx core exports, AC97 register access, and optional machine callbacks. It is the only codec in this set with extra power-bit handling in `AC97_EXTENDED_MID`.

## Risks
Selector translation is WM9713-specific and easy to break. Power bit toggling must align with core suspend/resume and AUX reads. Coordinate mode returns `0` on malformed sample tags. Global module parameters are not per-device.

## Test Signals
Test power-bit enable/disable, all module parameter interactions, sample selector validation, coordinate and per-axis polling, pressure disabled by five-wire mode, continuous mode, AUX prepare/restore, and resume register restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm9713.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm97xx-core.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm97xx-core.c

## Purpose
`wm97xx-core.c` is the common touchscreen/AUX/GPIO/battery core for Wolfson WM9705, WM9712, and WM9713 AC97 codecs. It detects the codec, selects codec-specific callbacks, registers input and child platform devices, reads touch samples, and manages PM.

## Important APIs, Types, And Functions
Exports include `wm97xx_reg_read()`, `wm97xx_reg_write()`, `wm97xx_read_aux_adc()`, GPIO get/set/config helpers, `wm97xx_set_suspend_mode()`, and machine-ops registration. `wm97xx_read_samples()` calls codec or machine sampling, filters out-of-range readings, reports input events, and adjusts poll interval. `wm97xx_ts_reader()` is the delayed work loop. `_wm97xx_probe()` validates vendor IDs, selects `wm9705_codec`, `wm9712_codec`, or `wm9713_codec`, initializes physical settings, caches GPIOs, and registers touch.

## Control Flow
The module registers both an AC97 bus driver and an MFD platform driver. Probe allocates `struct wm97xx`, detects codec ID, registers a touchscreen input device and `wm97xx-touch` child, then registers a battery child. Input open creates an ordered workqueue, enables digitizer/continuous mode, initializes delayed work, and requests pen IRQ if available. Close frees IRQ, cancels work, destroys the workqueue, and disables digitizer/continuous mode.

## State And Persistence
State includes digitizer and GPIO register caches, misc register, machine ops, pen state, suspend mode, delayed work interval, input device state, and child devices. Module parameters define input absolute ranges. No persistent storage is changed.

## Dependencies And Integration Points
It integrates AC97 bus ops, MFD platform data, WM97xx codec callback structs, input core, platform child devices for touch/battery, workqueues, IRQs, PM wakeup, and optional machine acceleration hooks.

## Risks
The core has complex lifetime interactions: IRQ allocation happens on input open, work rearms itself, and child platform devices are registered after input. `wm97xx_reg_read()` returns `-1` without an AC97 handle, which can look like register data. Suspend writes digitizer registers partly bypassing the cache. Machine ops can change sampling semantics substantially.

## Test Signals
Test all codec IDs and disabled-codec config paths, input open/close with and without IRQ, polling interval backoff, out-of-range filtering, AUX ADC timeout, GPIO helpers, battery child registration failure unwinding, AC97 and MFD probe/remove, suspend/resume with wakeup mode, and machine-op registration conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/wm97xx-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zet6223.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/zet6223.c

## Purpose
`zet6223.c` is an I2C multitouch driver for ZEITEC zet622x/zet6223 controllers. It powers the controller, queries dimensions and finger count, and reports direct MT slots from IRQ packets.

## Important APIs, Types, And Functions
`struct zet6223_ts` stores client, input, touchscreen properties, two regulators, max coordinates, and finger count. `zet6223_power_on()` gets/enables `vio` and `vcc` supplies and registers a power-off action. `zet6223_query_device()` sends `ZET6223_CMD_INFO` and decodes finger count and X/Y maxima. `zet6223_irq()` validates packet marker `0x3c`, reads finger bitmask, and reports active slots.

## Control Flow
Probe requires an IRQ, allocates state, powers on, queries device info, allocates input, parses touchscreen properties, initializes MT slots, requests a threaded IRQ, disables it until input open, then registers input. Open enables IRQ and close disables it.

## State And Persistence
Finger count and max coordinates are cached from the controller. Regulators remain managed through devm action. Contact lifetime is held by input MT slots; no persistent settings are stored.

## Dependencies And Integration Points
It depends on I2C master send/recv, regulator bulk APIs, input MT, touchscreen property parsing, OF/I2C matching, and threaded IRQs.

## Risks
`touchscreen_parse_properties()` is called after axis setup but the IRQ path reports raw `input_event()` coordinates rather than `touchscreen_report_pos()`, so axis inversion/swap properties may not be applied. Query failures prevent probe. IRQ open/close must remain balanced.

## Test Signals
Test missing IRQ, regulator failures, info command short reads, excessive finger count clamping, valid/invalid packet markers, MT slot cleanup for lifted fingers, touchscreen property transforms, and open/close IRQ balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zet6223.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zforce_ts.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/zforce_ts.c

## Purpose
`zforce_ts.c` is an I2C multitouch driver for Neonode zForce controllers. It implements the framed command/response protocol, configures resolution and scan frequency, reports up to two contacts, and supports wakeup-aware suspend.

## Important APIs, Types, And Functions
`struct zforce_ts` stores I2C/input handles, touchscreen properties, reset/interrupt GPIOs, suspend flags, boot/version fields, and command completion state. `zforce_send_wait()` sends a framed command and waits for the matching response. `zforce_start()` initializes, sets resolution, scan frequency, dual-touch config, requests data, and waits for calibration. `zforce_irq_thread()` drains packets while the level interrupt GPIO is active, handles notifications/responses, and completes commands. `zforce_touch_event()` reports MT slots and area/orientation.

## Control Flow
Probe obtains GPIOs using modern or legacy bindings, enables `vdd`, registers reset cleanup, initializes input axes from legacy properties plus touchscreen properties, requests IRQ, releases reset, waits for bootcomplete, queries status/version, stops the device, marks wakeup capable, and registers input. Input open starts the controller; close deactivates it. Suspend may start the device solely for wakeup, enable IRQ wake, or stop/disable IRQ when not a wake source; resume reverses that state.

## State And Persistence
Runtime state includes command wait/result, boot/version info, suspended/suspending flags, and input MT tracking. Hardware configuration is applied at each start. No persistent controller storage is changed.

## Dependencies And Integration Points
It uses I2C, GPIO descriptors, regulator `vdd`, input MT, touchscreen property parsing, completions, PM wakeup helpers, OF matching, and asynchronous probe preference.

## Risks
`zforce_send_wait()` assigns `ret = ts->command_result` but returns `0`, so nonzero command result payloads may not propagate as intended. Touch IDs are decremented before slot selection; invalid zero IDs would underflow. Level IRQ draining depends on optional GPIO state. Suspend has careful wakeup/event behavior and needs race testing.

## Test Signals
Test bootcomplete timeout, command response matching and timeout, nonzero command result propagation, packet framing errors, coordinate bounds, invalid touch IDs, open/close start-stop errors, wakeup and non-wakeup suspend/resume, legacy GPIO/property bindings, and reset cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zforce_ts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zinitix.c -->
# sources/distributed-fs/ceph-client/drivers/input/touchscreen/zinitix.c

## Purpose
`zinitix.c` is an I2C multitouch driver for Zinitix BT/AT touchscreen controllers. It controls regulators, performs the vendor power-on sequence, configures controller registers, reports up to five MT contacts, and optionally reports capacitive key events.

## Important APIs, Types, And Functions
`struct bt541_ts_data` stores client/input, touchscreen properties, regulators, mode, keycodes, version cache, and variant-specific icon status register. I2C helpers perform two-step register reads and little-endian writes. `zinitix_send_power_on_sequence()` sends vendor initialization commands. `zinitix_init_touch()` resets the controller, caches version data, chooses icon status register, programs resolution/finger count/buttons/mode/interrupt flags, and clears pending interrupts. `zinitix_ts_irq_handler()` reads `struct touch_event`, reports keys and per-finger MT events, then clears interrupt status.

## Control Flow
Probe checks I2C support, gets regulators with compatibility names for older DTs, requests a no-auto-enable threaded IRQ, parses optional `linux,keycodes`, initializes and registers input, validates `zinitix,mode` as mode 2, and leaves the device off until open. Open enables regulators, delays, performs power sequence and controller init, then enables IRQ. Close disables IRQ and regulators. Suspend/resume stop/start only if input is enabled.

## State And Persistence
Version information and icon register selection are cached after first init. Runtime power is regulator-backed. Controller configuration is rewritten on each start. No flash or nonvolatile state is changed.

## Dependencies And Integration Points
It integrates I2C, regulator bulk APIs, input MT, touchscreen properties, optional `linux,keycodes`, OF compatible table, IRQF_NO_AUTOEN, and system sleep PM.

## Risks
If `zinitix_start()` fails after regulators are enabled, the error path does not immediately disable them. The driver only supports touch mode 2. Many register constants are unused, indicating broader hardware features not implemented. IRQ handler always attempts to clear interrupt even after read failure.

## Test Signals
Test regulator naming fallback, power-on sequence failures and cleanup, required touchscreen size properties, keycode parsing limits, mode validation, version/icon-register selection, finger down/move/up and key events, interrupt clear on failures, and suspend/resume while input is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/touchscreen/zinitix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/vivaldi-fmap.c -->
# sources/distributed-fs/ceph-client/drivers/input/vivaldi-fmap.c

## Purpose
`vivaldi-fmap.c` provides a small exported helper for ChromeOS Vivaldi keyboard drivers to render the function-row physical map as a sysfs attribute string.

## Important APIs, Types, And Functions
`vivaldi_function_row_physmap_show()` takes `struct vivaldi_data`, iterates `function_row_physmap`, and formats each physical key code as two-digit uppercase hex separated by spaces with a trailing newline. The function is exported with `EXPORT_SYMBOL_GPL`.

## Control Flow
Callers pass their Vivaldi data and a sysfs buffer from an attribute show callback. If `num_function_row_keys` is zero, the helper returns zero bytes. Otherwise it accumulates output using `sysfs_emit_at()`.

## State And Persistence
The helper is stateless and only reads caller-owned data. It stores no persistent configuration.

## Dependencies And Integration Points
It depends on `linux/input/vivaldi-fmap.h`, sysfs formatting helpers, and module export infrastructure.

## Risks
The helper trusts that `function_row_physmap` has at least `num_function_row_keys` entries. Large maps must still fit the sysfs page-sized buffer, though `sysfs_emit_at()` is the correct bounded formatting primitive.

## Test Signals
Test zero-key output, single and multiple key formatting, spacing/newline behavior, buffer boundary behavior with large key counts, and GPL symbol linkage from a caller module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/vivaldi-fmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/interconnect/Kconfig

## Purpose
`drivers/interconnect/Kconfig` defines the build-time configuration menu for the Linux interconnect framework, provider families, clock-wrapper support, and KUnit tests.

## Important APIs, Types, And Functions
The top-level `menuconfig INTERCONNECT` enables generic on-chip interconnect management. Within that menu it sources provider Kconfigs for `imx`, `mediatek`, `qcom`, and `samsung`. `INTERCONNECT_CLK` enables clock-backed interconnect nodes and depends on `COMMON_CLK`. `INTERCONNECT_KUNIT_TEST` builds the framework KUnit suite and defaults on under `KUNIT_ALL_TESTS`.

## Control Flow
Kconfig evaluation exposes child provider menus only when `INTERCONNECT` is enabled. Selected symbols drive the companion Makefile to build core, provider, clock, and test objects.

## State And Persistence
This file defines compile-time configuration only. It does not manage runtime state or persistence.

## Dependencies And Integration Points
It integrates with the kernel Kconfig system, provider subdirectories, common clock framework, and KUnit.

## Risks
Provider source lines must stay synchronized with subdirectory Makefile entries. `INTERCONNECT_CLK` has no prompt text, so it is selected by other configs rather than normally user-enabled. Test defaulting depends on global KUnit policy.

## Test Signals
Test menu visibility with `INTERCONNECT=n/y`, provider config inclusion, `INTERCONNECT_CLK` dependency on `COMMON_CLK`, KUnit default behavior, and Makefile symbol consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/Makefile -->
# sources/distributed-fs/ceph-client/drivers/interconnect/Makefile

## Purpose
`drivers/interconnect/Makefile` maps interconnect Kconfig symbols to the generic framework objects, provider subdirectories, clock wrapper, and KUnit test object.

## Important APIs, Types, And Functions
`CFLAGS_core.o := -I$(src)` gives `core.o` access to local headers. `icc-core-objs` groups `core.o`, `bulk.o`, and `debugfs-client.o` into the `icc-core.o` composite object. `obj-$(CONFIG_INTERCONNECT*)` entries select the core, provider directories, `icc-clk.o`, and `icc-kunit.o`.

## Control Flow
During kbuild, enabled configuration symbols expand `obj-y` or `obj-m` entries. The core object is built when `CONFIG_INTERCONNECT` is enabled, provider directories are recursed when their symbols are set, and tests build when `CONFIG_INTERCONNECT_KUNIT_TEST` is enabled.

## State And Persistence
The file has no runtime state. It controls build artifacts only.

## Dependencies And Integration Points
It depends on kbuild composite object syntax and must match symbols defined by `drivers/interconnect/Kconfig` and provider subdirectory Kconfigs.

## Risks
Adding a provider in Kconfig without a Makefile entry, or vice versa, causes configuration/build drift. The local include path is specific to `core.o`, so other objects needing local headers would require their own flags or includes.

## Test Signals
Test all relevant config combinations, module versus built-in builds, provider directory recursion, KUnit object build, and clean builds after adding/removing provider symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/interconnect/Makefile -->
