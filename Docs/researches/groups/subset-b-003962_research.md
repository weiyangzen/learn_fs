# subset-b-003962 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/sidewinder.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/sidewinder.c

Purpose: implements the Microsoft SideWinder gameport family driver, including 3D Pro, GamePad, Precision Pro, Force Feedback Pro, FreeStyle Pro, and Force Feedback Wheel variants. It discovers packet mode and device type, registers one or more input devices, and polls raw gameport timing data.

Important APIs/types/functions: `struct sw` stores the gameport, up to four `input_dev` objects, packet length/mode, type, device count, and error counters. Core routines are `sw_read_packet`, `sw_get_bits`, `sw_init_digital`, `sw_check`, `sw_parity`, `sw_parse`, `sw_read`, `sw_poll`, `sw_connect`, and `sw_disconnect`. Static tables define model names, axes, bit widths, buttons, and hat conversion.

Control flow: probe opens the gameport in raw mode, attempts normal packet reads, switches 3D Pro devices to digital mode when needed, reads an ID packet, guesses one-bit versus three-bit packet encoding, detects a model from packet length and ID length, configures input axes/buttons, and installs a 20 ms poll handler. Polling calls `sw_read`, which reads a packet, applies special 3D Pro recovery for repeated/truncated packets, parses model-specific fields, syncs input events, and adapts the optimized packet length. Persistent failures trigger reinitialization and ID reread.

State and persistence: all runtime state is in `struct sw`; there is no disk persistence. `fail`, `ok`, `reads`, and `bads` track link quality and drive reinitialization and optimization toggling. Input devices are allocated during connect and unregistered during disconnect.

Dependencies and integration: depends on the Linux input and gameport subsystems, IRQ-disabling timing loops, delays, jiffies helpers, and module gameport registration. It exposes `BUS_GAMEPORT` input devices with Microsoft gameport IDs.

Risks: timing constants are explicitly magic and fragile. Raw polling runs with interrupts disabled while sampling packets. Detection is packet-length heuristic based and can misclassify unknown hardware. 3D Pro recovery uses bit comparisons and buffer movement that need careful bounds reasoning. Reinitialization on noisy links can cause intermittent input loss.

Test signals: useful checks include module load/unload with real gameport hardware, `evtest` axis/button verification per SideWinder model, packet error counter observation under noisy input, 3D Pro analog-to-digital transition, and suspend/unplug style gameport lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/sidewinder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/spaceball.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/spaceball.c

Purpose: supports SpaceTec SpaceBall 1003/2003/3003/4000 FLX RS-232 controllers through the serio subsystem, decoding six-degree-of-freedom motion and button packets into input events.

Important APIs/types/functions: `struct spaceball` keeps the `input_dev`, packet index, escape state, packet buffer, and physical path. `spaceball_process_packet` decodes packet types. `spaceball_interrupt` assembles carriage-return-terminated packets and handles `^` escaping. `spaceball_connect` and `spaceball_disconnect` bind/unbind serio devices.

Control flow: serio matching accepts `SERIO_RS232` with `SERIO_SPACEBALL`. Connect validates the serio ID, allocates state and input device, configures buttons according to model, sets six axes, opens serio, and registers input. The interrupt handler buffers bytes until `0x0d`, unescapes encoded control bytes, and calls the packet decoder. `D` packets report six signed big-endian axes, `K` and `.` packets report normal or advanced buttons, and error packets are logged.

State and persistence: packet assembly state is transient in `idx`, `escape`, and `data`; no persistent configuration is stored. Device identity comes from serio IDs.

Dependencies and integration: depends on `serio`, Linux input, and `get_unaligned_be16`. It reports `BUS_RS232` devices with SpaceBall vendor/product metadata and standard ABS/BTN codes.

Risks: malformed packet lengths are silently ignored after `input_sync` for recognized paths. Packet buffering truncates after `SPACEBALL_MAX_LENGTH`, so bad framing can drop data until the next CR. Button capability setup varies by ID and could omit capabilities for incorrectly tagged adapters. No checksum is present.

Test signals: exercise with real or emulated SpaceBall serial frames, verify CR and escape decoding, validate six-axis signed ranges with `evtest`, test advanced 4000FLX button packets, and confirm disconnect frees serio/input state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/spaceball.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/spaceorb.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/spaceorb.c

Purpose: implements the SpaceTec SpaceOrb 360 and Avenger RS-232 controller driver, converting proprietary 6DOF motion, button, reset, and error packets into input events.

Important APIs/types/functions: `struct spaceorb` holds an input device, packet index, buffer, and phys string. `spaceorb_process_packet` validates XOR checksum and decodes packets. `spaceorb_interrupt` frames packets using the high bit as start indication. `spaceorb_connect` sets up six axes and six buttons.

Control flow: incoming bytes with bit 7 clear start a new packet; an existing buffered packet is processed before reset. All stored bytes are masked to 7 bits. The decoder rejects short packets and nonzero XOR checksums. Reset packets log device information. `D` packets XOR payload bytes with `"SpaceWare"`, unpack six 10-bit signed axes, report six buttons, and sync. `K` packets report buttons only; `E` packets log mapped device errors.

State and persistence: state is limited to the current receive buffer and index. There is no stored calibration or persistent configuration.

Dependencies and integration: uses the serio and input subsystems with `SERIO_SPACEORB` matching, `BUS_RS232` IDs, ABS_X/Y/Z/RX/RY/RZ axes, and `BTN_TL/TR/Y/X/B/A`.

Risks: malformed checksums and unexpected lengths are ignored without recovery beyond start-bit resynchronization. Axis unpacking is protocol-specific and tightly coupled to exact byte positions. Error reporting only logs device error bits. There is no debounce or rate limiting on valid input events.

Test signals: inject valid and corrupt frames into a serio test path, verify XOR rejection, reset/error log messages, signed axis conversion around the 0x200 sign bit, and button-only versus full data packet behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/spaceorb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/stinger.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/stinger.c

Purpose: supports the Gravis Stinger RS-232 gamepad by decoding fixed four-byte packets into two axes and ten buttons.

Important APIs/types/functions: `struct stinger` stores the input device, packet index, four-byte data buffer, and phys path. `stinger_interrupt` buffers incoming bytes. `stinger_process_packet` reports buttons and ABS_X/ABS_Y. `stinger_connect` and `stinger_disconnect` manage serio and input lifecycle.

Control flow: connect allocates state/input, assigns `BUS_RS232` IDs, declares `EV_KEY` and `EV_ABS`, sets key bits for A/B/C/X/Y/Z/TL/TR/START/SELECT, sets -64..64 axis ranges, opens serio, and registers input. The interrupt handler appends bytes until four are received, then decodes and resets the index. Decode pulls button bits from bytes 0 and 3 and combines high sign bits with bytes 1 and 2 for axes.

State and persistence: only the current four-byte packet index and data buffer persist between interrupts. No hardware configuration is written and no data persists beyond device removal.

Dependencies and integration: uses `SERIO_STINGER`, `module_serio_driver`, and standard Linux input key/axis reporting.

Risks: there is no explicit framing or checksum, so a dropped byte can desynchronize all following four-byte windows until external serio framing recovers. The driver assumes every four bytes are a complete packet. Allocation uses plain `kmalloc_obj`, so all fields initialized before use matter.

Test signals: validate packet-to-event mapping using synthetic four-byte streams, test lost-byte behavior, check axis bounds and flat value with `evtest`, and verify serio open/register failure unwinds cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/stinger.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/tmdc.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/tmdc.c

Purpose: implements the ThrustMaster DirectConnect/BSP gameport driver for several joystick/gamepad models, including two logical ports on one gameport.

Important APIs/types/functions: `struct tmdc` tracks the gameport, up to two `tmdc_port` instances, existence bitmask, and read/error counters. `struct tmdc_port` stores per-port input device, mode, axis/button tables, and names. Key functions are `tmdc_read_packet`, `tmdc_parse_packet`, `tmdc_poll`, `tmdc_setup_port`, `tmdc_connect`, and `tmdc_disconnect`.

Control flow: connect opens the gameport in raw mode, reads a 13-byte packet from one or both ports, records which ports exist, installs a 20 ms poll handler, and creates an input device for each present port. Packet reading disables interrupts, triggers the gameport, then samples two serial streams in parallel from upper status bits, honoring start/data/stop bits. Polling rereads both ports and compares the presence bitmask with the probed one. Per-port parsing verifies the mode byte, reports configured axes, handles model-specific hats, reports button groups, and syncs.

State and persistence: per-port model configuration is derived at probe from the packet ID/default byte and held in memory. `reads` and `bads` accumulate until disconnect. There is no persistent storage.

Dependencies and integration: depends on gameport raw polling, Linux input, delay/timing helpers, and model tables for ThrustMaster hardware. It exposes `BUS_GAMEPORT` devices and vendor `GAMEPORT_ID_VENDOR_THRUSTMASTER`.

Risks: raw timing and serial decode are sensitive to CPU/gameport timing. Unknown devices fall back to a generic model based on packet definition bits, which can overdeclare buttons. `tmdc_setup_port` formats phys with the loop variable after prior loops, which is worth checking in maintenance. Polling flags any transient packet read mismatch as bad.

Test signals: real hardware tests should cover one-port and two-port adapters, known model IDs, unknown device fallback, hat translation for M3DI/Attack Throttle, open/close polling start/stop, and bad packet counters under unplug/noise.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/tmdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/turbografx.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/turbografx.c

Purpose: supports TurboGraFX parallel-port joystick adapters, allowing up to seven configured gamepads per parport with 1-5 buttons.

Important APIs/types/functions: `struct tgfx_config` holds module parameter maps. `struct tgfx` stores the parport device, polling timer, input devices, names, phys paths, stick mask, usage count, parport number, and mutex. Key functions are `tgfx_timer`, `tgfx_open`, `tgfx_close`, `tgfx_attach`, `tgfx_detach`, `tgfx_init`, and `tgfx_exit`.

Control flow: module parameters `map`, `map2`, and `map3` select parport numbers and per-port button counts. Init refuses to load without configured devices and registers a parport driver. Attach claims only configured ports, registers an exclusive parport device, allocates state, creates input devices for valid joystick slots, and stores the instance globally. Opening the first input claims the parport, sets control lines, and starts a 10 ms timer. The timer selects each stick by writing data, reads status/control bits, reports two digital axes and up to five buttons, syncs, and reschedules itself. Closing the last user stops the timer and releases the port.

State and persistence: configuration comes from module parameters. Runtime state tracks active users and devices in memory only. No persistent hardware state remains after close except the port control value reset to zero.

Dependencies and integration: uses parport, timer_list, jiffies, mutex helpers, and Linux input. Devices are reported as `BUS_PARPORT`.

Risks: polling is timer based and assumes exclusive parport access. Invalid module maps prevent devices from appearing. Attach error unwinding must unregister already registered input devices. Electrical and CAVEAT parport control-bit behavior is adapter-specific.

Test signals: load with valid/invalid maps, verify each configured slot appears, check timer starts only on first open and stops on last close, confirm parport claim/release, and validate direction/button bit mapping with `evtest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/turbografx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/twidjoy.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/twidjoy.c

Purpose: treats the original RS-232 Handykey Twiddler chording keyboard as a joystick with 18 buttons and two tilt axes.

Important APIs/types/functions: `struct twidjoy_button_spec` maps packed button bit fields to Linux button codes. `struct twidjoy` stores input device, packet index, five-byte buffer, and phys string. `twidjoy_process_packet`, `twidjoy_interrupt`, `twidjoy_connect`, and `twidjoy_disconnect` implement decode and lifecycle.

Control flow: connect allocates a `BUS_RS232` input device, declares ABS_X/ABS_Y ranges, and sets every button listed in `twidjoy_buttons`. The interrupt handler uses packet MSB conventions to resynchronize: byte 0 has MSB clear and following bytes have MSB set. Once five bytes are buffered, processing combines two 7-bit chunks into button state, reports exactly one active button per multi-value row spec, unpacks signed 8-bit-ish X/Y tilt fields, reports negated X and positive Y, syncs, and resets.

State and persistence: only current packet assembly state persists. The driver does not store key chords, layouts, or calibration.

Dependencies and integration: depends on serio protocol `SERIO_TWIDJOY` and Linux input key/axis reporting. It intentionally does not integrate with the keyboard text input stack.

Risks: malformed MSB patterns are ignored or resync the stream. The button loop uses `bitmask` both as a mask and count, which works for masks 1 and 3 but is not a generic bitmap iterator. Tilt ranges are declared -50..50 even though decoded values can be wider, so userspace should observe actual clipping/normalization behavior.

Test signals: feed valid five-byte frames, test resync on wrong MSB bytes, verify one-of-three row button behavior, validate signed tilt decode, and confirm autorepeat is absent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/twidjoy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/walkera0701.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/walkera0701.c

Purpose: decodes a Walkera WK-0701 RC transmitter connected through a parallel port into joystick axes and one gear key.

Important APIs/types/functions: `struct walkera_dev` stores the 25-nibble frame buffer, IRQ timing, sampled ACK bit, input device, hrtimer, parport, and pardevice. Core functions are `walkera0701_irq_handler`, `timer_handler`, `walkera0701_parse_frame`, `walkera0701_open`, `walkera0701_close`, `walkera0701_attach`, and `walkera0701_detach`.

Control flow: attach binds only the configured `port` module parameter, requires a parport IRQ, registers an exclusive parport device with an IRQ callback, negotiates compatibility mode, initializes an hrtimer, allocates input, and registers axes. On open it claims the parport and enables IRQs. Each falling-edge IRQ measures pulse width since the last edge, cancels the sample timer, detects sync pulses, records binary high-bit and analog 3-bit values, and when 25 entries are available validates two CRC groups and reports decoded channels. The hrtimer samples ACK midway between binary pulse lengths.

State and persistence: this driver supports one global static device. Frame assembly, timing, ACK state, and sync counter persist in RAM while open. There is no persistent configuration apart from the module parameter.

Dependencies and integration: uses parport IRQ callbacks, hrtimer, ktime nanosecond timing, and Linux input. It reports `BUS_PARPORT` and ABS_X/Y/Z/THROTTLE/RUDDER/MISC plus `BTN_GEAR_DOWN`.

Risks: pulse-width constants and tolerances are hardware/timing sensitive. A global singleton prevents multiple devices. IRQ/timer races are handled by `hrtimer_try_to_cancel`, but resync is conservative. Parse code reports no `input_sync`, so consumers rely on subsequent events or may see batched state differently than expected.

Test signals: verify with real transmitter pulses, test sync recovery after malformed timings, validate CRC rejection, check IRQ enable/disable on open/close, observe reported axes and gear key through `evtest`, and confirm detach ignores nonmatching ports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/walkera0701.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/warrior.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/warrior.c

Purpose: supports the Logitech WingMan Warrior RS-232 joystick, including buttons, XY axes, throttle, hat, and spinner dial.

Important APIs/types/functions: `struct warrior` tracks input device, current packet index, expected packet length, data buffer, and phys path. `warrior_lengths` maps packet type to length. `warrior_interrupt` frames packets. `warrior_process_packet` decodes packet classes. Connect/disconnect provide serio lifecycle.

Control flow: bytes with the high bit set start a new packet and determine expected length from bits 4-6. A partially collected packet is processed before resync. When the expected length is reached, decode reports one of three supported packet classes: button data, XY-axis data, or throttle/hat/spinner data. The spinner uses `REL_DIAL`; other controls use ABS/KEY events. Connect sets `EV_KEY`, `EV_REL`, and `EV_ABS` capabilities and registers the input device.

State and persistence: only packet framing state persists across interrupts. No calibration or hardware settings are stored.

Dependencies and integration: uses `SERIO_WARRIOR`, Linux input, and standard serio module registration. It exposes `BUS_RS232`.

Risks: packet type lengths are table-driven and unknown types get zero length. There is no checksum. Processing a partial packet on a new high-bit byte can report stale/incomplete data if framing is noisy, though packet class checks limit some effects. Relative dial interpretation depends on exact signed bit packing.

Test signals: inject packet classes 1, 3, and 5, verify high-bit resync, test button/axis/hat/dial events, and validate no events for zero-length or unsupported packet types.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/warrior.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/xpad.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/xpad.c

Purpose: implements the USB Xbox controller driver for original Xbox, Xbox 360 wired, Xbox 360 wireless receivers, Xbox One/Series controllers, and many compatible third-party devices. It handles input decoding, optional force feedback, optional LED control, wireless presence, initialization packets, suspend/resume, and power-off behavior.

Important APIs/types/functions: `struct usb_xpad` is the central runtime state, containing USB/input devices, URBs, coherent input/output buffers, output packet queue, spinlock, mapping/type flags, wireless RCU pointer, work item, sequence counters, and power/init flags. Key functions include `xpad_probe`, `xpad_disconnect`, `xpad_irq_in`, `xpad_process_packet`, `xpad360_process_packet`, `xpad360w_process_packet`, `xpadone_process_packet`, `xpad_init_input`, `xpad_start_input`, `xpad_init_output`, `xpad_prepare_next_out_packet`, `xpad_irq_out`, `xpad_play_effect`, LED helpers, `xpad_suspend`, and `xpad_resume`.

Control flow: USB probe validates two interrupt endpoints, looks up vendor/product metadata, infers unknown controller type from interface descriptors, allocates DMA buffers and URBs, prepares output support, detects Xbox One Elite packet variants, and either starts the wireless receiver immediately or registers an input device. Input URB completion dispatches by controller type, reports keys/axes/triggers/dpad/paddles/profile/share data, then resubmits the URB. Output commands are serialized under `odata_lock`; Xbox One init packets take priority, then pending command/rumble/LED packets rotate through a small queue. Wireless receiver status packets schedule work to create or destroy the actual input device and use RCU to protect concurrent packet processing.

State and persistence: all state is in memory and tied to USB interface lifetime. Module parameters affect unknown-device dpad/trigger/stick mapping and wireless auto-poweroff. Output queue pending flags, serial numbers, delayed init state, wireless presence, and mode-button hold timestamp persist during runtime only.

Dependencies and integration: integrates with USB core, Linux input, optional `CONFIG_JOYSTICK_XPAD_FF`, optional `CONFIG_JOYSTICK_XPAD_LEDS`, LED class, IDA, RCU, workqueues, anchors, PM hooks, and USB quirks. The device ID table and USB match table are major integration surfaces.

Risks: large VID/PID tables must stay sorted and consistent with match macros. Packet offsets vary by controller generation, firmware, and mapping flags; share/paddle/profile offsets are especially fragile. Output URB concurrency relies on spinlock/anchor state. Wireless input creation/destruction depends on RCU and work flushing. Suspend can send poweroff while output URBs are being stopped. Unknown-device heuristics and module parameters may expose inappropriate capabilities.

Test signals: run USB plug/unplug, open/close, suspend/resume, and controller reconnect tests across original Xbox, 360 wired, 360 wireless, Xbox One, and Elite variants. Verify `evtest` mappings for dpad modes, triggers-as-buttons, stick suppression, share/profile/paddles. Exercise FF rumble and LED control when configured. Check Xbox One delayed init/announce behavior, wireless mode-button poweroff, and URB error paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/xpad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/zhenhua.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/zhenhua.c

Purpose: supports RC transmitters using the Zhen Hua five-byte serial protocol, such as Walkera Lama/EasyCopter transmitters, as four-axis joysticks.

Important APIs/types/functions: `struct zhenhua` contains input device, packet index, five-byte buffer, and phys path. `zhenhua_interrupt` frames and bit-reverses incoming bytes. `zhenhua_process_packet` reports ABS_Y, ABS_X, ABS_RZ, and ABS_Z. Connect/disconnect implement serio binding.

Control flow: the interrupt handler treats raw byte `0xef` as the synchronization marker, resets the index on it, ignores bytes until synchronized, stores `bitrev8(data)` for each packet byte, and processes once five bytes are collected. The decoder maps bytes 1-4 directly to four analog axes and syncs. Connect declares an ABS-only input device with 50..200 ranges for all four axes.

State and persistence: runtime state is only the packet buffer and index. No calibration or persistent settings exist.

Dependencies and integration: uses `SERIO_ZHENHUA`, `linux/bitrev.h`, serio registration, and Linux input. It reports `BUS_RS232` with fixed vendor/product placeholders.

Risks: comments mention sync `0xf7`, but code checks raw `0xef` before bit reversal; maintenance should preserve the raw-versus-reversed distinction. There is no validation that data bytes are in 50..200 after bit reversal. A missed sync byte drops reports until the next sync.

Test signals: verify sync on raw `0xef`, confirm bit reversal produces expected 0xf7/data values, test four axis reports through `evtest`, and feed out-of-range/misaligned bytes to confirm ignore/resync behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/zhenhua.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/Kconfig

Purpose: defines the kernel configuration menu for keyboard/input-key drivers under `drivers/input/keyboard`, including build choices, dependencies, selects, defaults, and help text.

Important APIs/types/functions: this is Kconfig metadata rather than C code. Key constructs are `menuconfig INPUT_KEYBOARD`, the `if INPUT_KEYBOARD` block, many `config KEYBOARD_*` tristate/bool entries, `depends on`, `select`, `default`, and module naming help text.

Control flow: enabling `INPUT_KEYBOARD` exposes the menu but does not itself build code. Individual options select drivers such as ADC ladder keys, ADP5520/5585/5588 keypads, Amiga/Atari/AT keyboards, GPIO/matrix keypads, I2C touch/key controllers, platform SoC keypads, ChromeOS EC keyboards, and others. Dependencies constrain options to required buses, MFD parents, architectures, OF, GPIO, I2C, MATRIXKMAP, or compile-test availability.

State and persistence: Kconfig selections persist in the kernel `.config` and control compilation as built-in, module, or disabled. This file itself has no runtime state.

Dependencies and integration: integrates with the top-level input Kconfig and the keyboard `Makefile`; each symbol is consumed by `obj-$(CONFIG_...)` rules. `select` entries pull common helpers such as `INPUT_MATRIXKMAP`, `SERIO`, `REGMAP_I2C`, `GPIOLIB`, `CRC8`, and `INPUT_VIVALDIFMAP`.

Risks: incorrect dependencies can allow compile failures or hide valid drivers. Overuse of `select` can force helper subsystems unexpectedly. Help text and module names must stay aligned with Makefile object names. Architecture defaults can change build coverage significantly.

Test signals: run Kconfig validation, randconfig/allmodconfig builds, targeted builds for early entries in this work item, and compare each `KEYBOARD_*` symbol against Makefile object mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/Makefile

Purpose: maps keyboard driver Kconfig symbols to object files compiled into the kernel or modules.

Important APIs/types/functions: this is Kbuild metadata using `obj-$(CONFIG_KEYBOARD_...) += ...o` assignments. It has no functions or runtime types.

Control flow: during kernel build, Kbuild expands each enabled `CONFIG_KEYBOARD_*` symbol and includes the matching object in the directory build. The file covers the drivers declared in Kconfig, including `adc-keys.o`, `adp5520-keys.o`, `adp5585-keys.o`, `adp5588-keys.o`, `amikbd.o`, `atkbd.o`, GPIO, matrix, many I2C/MFD keypad drivers, and SoC-specific key scanners.

State and persistence: the selected build state comes from `.config`; this Makefile does not persist runtime state. It determines whether objects are built-in, modular, or omitted.

Dependencies and integration: integrates directly with `drivers/input/keyboard/Kconfig`, module names referenced in help text, and source filenames in the same directory. Object spelling is the critical contract.

Risks: missing or stale object mappings break enabled Kconfig symbols. Symbol/object naming mismatches can confuse module help text and packaging. Since this file is broad build plumbing, unrelated edits can affect many architectures.

Test signals: build with `allmodconfig`, `allyesconfig`, and targeted configs for ADC/ADP/Amiga drivers; run `scripts/checkkconfigsymbols.py` style checks; verify each source file has a corresponding Kconfig-controlled object and each referenced object exists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adc-keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/adc-keys.c

Purpose: implements a polled input driver for buttons wired through a resistor ladder to an IIO voltage ADC channel.

Important APIs/types/functions: `struct adc_keys_button` maps threshold voltage to keycode. `struct adc_keys_state` stores the IIO channel, number of keys, last reported key, key-up voltage, and keymap. `adc_keys_poll` reads and reports state. `adc_keys_load_keymap` parses firmware child nodes. `adc_keys_probe` wires the platform device to input polling.

Control flow: probe obtains the `"buttons"` IIO channel, validates it is `IIO_VOLTAGE`, reads `keyup-threshold-microvolt`, loads child-node `press-threshold-microvolt` and `linux,code` entries, allocates input, declares key bits, enables autorepeat if requested, sets up polling, optionally applies `poll-interval`, and registers the input device. Polling reads processed millivolts, selects the closest configured key threshold, treats the key-up threshold as no key when closer, releases the previous key if it changed, reports the current key, syncs, and remembers it.

State and persistence: `last_key` persists between polls to emit releases. Firmware properties define the keymap and thresholds; no runtime settings persist outside memory.

Dependencies and integration: depends on platform devices, firmware properties/OF matching `"adc-keys"`, IIO consumer APIs, and input polling helpers.

Risks: nearest-threshold matching can misreport when voltages overlap or drift. Failed ADC reads force release by substituting key-up voltage. Multiple simultaneous buttons on a resistor ladder are not represented. Unit conversion divides microvolts by 1000, matching processed millivolt expectations.

Test signals: device-tree/property tests for missing thresholds/keycodes, IIO mock reads near each threshold and key-up voltage, ADC error injection, autorepeat flag checks, and `evtest` validation of press/release transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adc-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5520-keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5520-keys.c

Purpose: provides keypad support for Analog Devices ADP5520 PMIC MFD devices using platform data and the parent MFD notifier mechanism.

Important APIs/types/functions: `struct adp5520_keys` stores input device, notifier block, parent device, and keycode array. `adp5520_keys_report_event` reports press/release masks. `adp5520_keys_notifier` handles keypad press/release interrupts. `adp5520_keys_probe` configures hardware and input. `adp5520_keys_remove` unregisters the notifier.

Control flow: probe validates the platform ID and platform data, requires row/column masks, allocates input, copies the platform keymap, declares key capabilities and repeat, registers input, configures GPIO/keypad modes and pullups through ADP5520 MFD register helpers, then registers for key press and release interrupt notifications. The notifier reads low/high status registers twice to clear/collect latched bits, combines them into a keymask, and reports all affected keys as pressed or released.

State and persistence: keymap and parent pointer persist in driver memory. Hardware mode/pullup configuration is written at probe and notifier registration remains until remove.

Dependencies and integration: depends on `PMIC_ADP5520`, MFD register helpers (`adp5520_read`, `adp5520_set_bits`), platform data, Linux input, and platform driver registration.

Risks: platform data is mandatory; no firmware-node parsing exists. Register writes are OR-combined into `ret`, which reports generic `-EIO` after any failure. The notifier ignores read return values. Status read-twice clearing is hardware-specific and must not be simplified casually.

Test signals: board/platform-data tests for row/column masks and keymap size, simulated MFD notifier press/release masks, hardware register write failure injection, repeat capability checks, and notifier unregister on remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5520-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5585-keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5585-keys.c

Purpose: implements keypad support for ADP5585/ADP5589-family MFD devices, using firmware-described keypad pins, matrix keymaps, regmap setup, and parent event notifiers.

Important APIs/types/functions: `struct adp5585_kpad_chip` describes event ranges and matrix dimensions. `struct adp5585_kpad` stores chip info, notifier, input, keycode map, device, keypad pin bitmap, and row shift. Key functions are `adp5585_keys_parse_fw`, `adp5585_keys_validate_events`, `adp5585_keys_setup`, `adp5585_keys_ev_handle`, and `adp5585_keys_probe`.

Control flow: probe requires an IRQ-capable parent ADP5585 device, reads revision, allocates input, attaches the parent OF node, parses `adi,keypad-pins`, reserves pins against the parent `pin_usage` bitmap, derives effective rows/columns, builds the matrix keymap, optionally enables repeat, validates unlock/reset special events, writes keypad pin configuration registers through regmap, registers a blocking notifier for parent key events, and registers input. Event handling filters events to the chip key range, maps hardware event numbers to row/column scan codes, reports the mapped keycode with press state carried in notifier data, and syncs.

State and persistence: reserved keypad pins are tracked in the parent device until devm cleanup. Keymap, row shift, and bitmap persist in memory. Hardware pin configuration persists until device reset/reconfiguration.

Dependencies and integration: depends on MFD_ADP5585, regmap, matrix keypad helpers, firmware properties, parent blocking notifier chain, and Linux input.

Risks: keypad pin parsing must avoid collisions with other child functions; invalid special event keys are rejected only if they fall in key event ranges. Sparse row/column selections are supported but produce matrix dimensions up to the highest used row/column. Event notifier data is cast through `unsigned long`, so parent contract matters.

Test signals: firmware parsing tests for invalid/duplicate pins, sparse matrices, unlock/reset event validation, regmap write failures, parent notifier press/release events, and ADP5585 versus ADP5589 ID table coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5585-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5588-keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5588-keys.c

Purpose: supports ADP5588/ADP5587 I2C keypad and GPIO expander chips. It can operate as a matrix keypad, export unused pins as GPIOs, and optionally provide nested IRQs for GPIO events.

Important APIs/types/functions: `struct adp5588_kpad` stores I2C client, input, IRQ timing delay, matrix dimensions/keymap, unlock keys, GPIO-only mode, GPIO map, `gpio_chip`, cached GPIO registers, and a mutex. Core functions include I2C `adp5588_read/write`, GPIO operations, IRQ chip callbacks, `adp5588_gpio_add`, `adp5588_report_events`, `adp5588_thread_irq`, `adp5588_setup`, `adp5588_fw_parse`, `adp5588_probe`, remove, suspend, and resume.

Control flow: probe checks SMBus byte support, parses firmware matrix properties or marks GPIO-only mode, enables regulator, toggles optional reset GPIO, reads revision, registers input, configures keypad rows/columns/unlock keys, clears event FIFO/status, enables interrupts, exports unused pins as GPIOs, and requests a threaded IRQ when present. The hard IRQ timestamps arrival. The thread applies a silicon-revision delay if needed, reads interrupt status, drains key events, reports matrix keys or dispatches nested GPIO IRQs, syncs input, and clears status. GPIO operations update cached direction/output/pull registers under mutex and write through I2C.

State and persistence: keymap, matrix dimensions, unlock keys, cached GPIO direction/output/interrupt/pull registers, and IRQ masks persist in memory. Hardware configuration persists in chip registers until removal, reset, or power loss. Remove disables the main config register.

Dependencies and integration: depends on I2C SMBus, matrix keypad helpers, GPIO library, GPIO IRQ chip support, regulators, optional reset GPIO, pin config constants, PM sleep hooks, and input.

Risks: mixed keypad/GPIO mode has a broad surface: matrix pins must be excluded from GPIO export, nested IRQ mapping depends on `gpiomap`, and cached GPIO state must stay coherent with hardware. The pull-disable update path appears sensitive to bit operations. Early silicon delayed readout uses jiffies-derived delay converted into ktime/usleep logic. GPIO-only mode still registers an input device before setup is skipped.

Test signals: test keypad matrix events, GPIO get/set/direction/config, interrupt-controller mode with rising/falling nested IRQs, regulator/reset sequencing, early revision delayed readout, FIFO overflow logging, suspend/resume IRQ disable/enable, and GPIO-only firmware with no rows/columns.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/adp5588-keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/amikbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/amikbd.c

Purpose: implements the Amiga keyboard driver for Linux/m68k, reading CIAA serial keyboard scancodes and exposing them through the Linux input subsystem.

Important APIs/types/functions: `amikbd_keycode` maps Amiga scancodes to Linux keycodes when VT is enabled. `amikbd_init_console_keymaps` rewrites console keymaps to match Amiga scancode positions. `amikbd_messages` maps keyboard controller/error codes. `amikbd_interrupt` handles CIAA serial-port interrupts. `amikbd_probe` allocates/registers the input device and IRQ.

Control flow: probe allocates a devm input device, sets `BUS_AMIGA`, enables key and repeat events, marks scancodes 0..0x77 as keys, initializes console keymaps, configures CIAA serial direction/control, requests `IRQ_AMIGA_CIAA_SP`, registers input, and stores drvdata. On interrupt, the handler reads and inverts `ciaa.sdr`, toggles CIAA CRA bit 0x40 for the required 85 us handshake, derives press/release from bit 0, shifts to the scancode, reports normal keys or special CapsLock press+release toggle behavior, syncs, or logs controller messages for scancodes 0x78..0x7f.

State and persistence: there is no heap driver state beyond the input device. Console keymap modifications occur during init when VT support is present and persist in kernel keymap memory.

Dependencies and integration: depends on AMIGA architecture hardware headers, CIAA registers, Amiga IRQ definitions, platform driver probing, Linux input, and optional VT keyboard maps.

Risks: direct hardware register manipulation and microsecond handshake timing are architecture-specific. Console keymap rewriting is global and init-time only. CapsLock behavior intentionally emits a pulse rather than hold state. Error scancode logging indexes `amikbd_messages` and assumes only 0x78..0x7f error codes.

Test signals: Amiga hardware or emulator tests for key press/release, CapsLock toggle, controller error scancodes, CIAA handshake timing, VT keymap correctness, and platform probe/IRQ request failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/amikbd.c -->
