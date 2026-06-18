# subset-b-003961 research

Grouped research for joystick input drivers under `sources/distributed-fs/ceph-client/drivers/input/joystick`. Each section preserves the source path for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adc-joystick.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/adc-joystick.c

Purpose: Platform input driver for joysticks wired to IIO ADC channels. It supports either input-core polling via `iio_read_channel_raw()` or callback-buffer driven reporting from IIO scan data, with axis layout supplied by firmware child nodes.

Important APIs/types/functions: `struct adc_joystick` owns the input device, IIO channel list, optional IIO callback buffer, and flexible-array axis metadata. `struct adc_joystick_axis` stores an input ABS code and inversion flag. `adc_joystick_probe()` acquires all IIO channels, reads the optional `poll-interval`, allocates the variable-sized state object, configures axes, chooses polling or callback mode, and registers the input device. `adc_joystick_set_axes()` consumes child-node `reg`, `linux,code`, `abs-range`, `abs-fuzz`, and `abs-flat`. `adc_joystick_handle()` decodes scan buffers using channel `scan_index`, endian, shift, sign, storagebits, and realbits; `adc_joystick_poll()` performs raw channel reads.

Control flow: Probe requires a one-to-one match between child nodes and IIO channels. In polling mode, input polling reads each channel and reports configured ABS codes. In buffered mode, input open starts the IIO callback buffer and close stops it; the callback decodes all samples and calls `input_sync()`.

State and persistence: Runtime state is per device and devm/action managed. No persistent storage exists. Axis inversion is derived once from a reversed `abs-range` and then applied to every sample.

Dependencies and integration points: Integrates with platform bus, device properties/OF compatible `adc-joystick`, IIO consumer APIs, and the input polling/callback model. Buffered operation depends on channels having equal storage size and storagebits no larger than 16.

Risks: Firmware must provide correct child-node ordering and ranges; invalid or mismatched nodes fail probe. Buffered decode assumes all channels share storage size and only supports 8- or 16-bit storage. Inversion calls `adc_joystick_invert()` with loop index in the current tree, while ABS min/max are configured by ABS code, so non-contiguous ABS codes deserve review in tests.

Test signals: Probe with valid and invalid child-node counts; poll mode with `poll-interval`; callback mode with BE, LE, CPU endian and signed/unsigned scan types; reversed `abs-range`; open/close start-stop of IIO buffers; input event ranges matching DT-specified ABS codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adc-joystick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adi.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/adi.c

Purpose: Gameport driver for Logitech ADI digital joystick and gamepad family, including WingMan, ThunderPad, CyberMan, Formula, and related devices. It probes one or two device halves on a gameport and reports decoded axes, buttons, hats, and pads through input.

Important APIs/types/functions: `struct adi_port` represents one gameport and contains two `struct adi` streams. `struct adi` stores decoded device identity, packet length, axis/button counts, cached raw packet bytes, and input metadata. `adi_read_packet()` captures edge-timed serial data under IRQ-off timing. `adi_move_bits()` merges a two-stream packet mode. `adi_id_decode()` parses the identification packet. `adi_decode()` emits ABS/key events. `adi_init_digital()` sends the reset/init trigger sequence. `adi_connect()` owns probe, input allocation, calibration, poll setup, and registration.

Control flow: Connect opens raw gameport mode, initializes digital mode, reads an ID packet, optionally merges dual streams, decodes each half, creates input devices, performs a first data read, initializes ABS center/ranges, and registers devices. Once an input node is opened, the gameport poll handler repeatedly reads and decodes packets every 20 ms.

State and persistence: State is in `struct adi_port` and the two `struct adi` instances. It tracks packet decode failures with `bad` and `reads`, stores discovered device packet layout, and records center/range calibration from initial values. There is no persistence beyond module lifetime.

Dependencies and integration points: Uses gameport raw mode, input core, module gameport driver registration, and vendor/product IDs from the parsed ADI ID. Device-specific axis/button maps are static arrays selected by ID.

Risks: Timing is fragile and depends on low-latency gameport reads with interrupts disabled. The ID parser rejects unsupported POV layouts and packet lengths, so uncommon devices may fail. Axis/button table selection is hard-coded; malformed IDs could produce incomplete capabilities. Failure counters are not exported except indirectly by behavior.

Test signals: Attach known ADI devices in single and dual-stream modes; verify ID packet length validation, hat conversion, pad handling, and 8-bit versus 10-bit axes; exercise open/close polling; inspect warnings for short or unsupported packets; compare initial calibration against input ABS ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/adi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/amijoy.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/amijoy.c

Purpose: Linux/m68k Amiga joystick driver for up to two classic Amiga joystick ports. It samples Amiga custom chip/CIA registers on vertical blank interrupts and reports a two-axis digital stick plus trigger button per configured port.

Important APIs/types/functions: Module parameter `map` controls which of the two ports are active. Global `amijoy_dev[2]` holds input devices, `amijoy_used` counts open users, and `amijoy_mutex` serializes IRQ installation. `amijoy_interrupt()` reads `amiga_custom.joy0dat`/`joy1dat` and `ciaa.pra`, converts bit pairs into -1/0/1 ABS_X and ABS_Y, and reports `BTN_TRIGGER`. `amijoy_open()` requests `IRQ_AMIGA_VERTB`; `amijoy_close()` frees it on last user.

Control flow: Module init rejects non-Amiga machines, allocates one input device per enabled port, reserves the custom register memory region, sets capabilities, and registers inputs. Opening any device installs the shared VBL interrupt if needed. Interrupts report current state for enabled ports. Module exit unregisters inputs and releases regions.

State and persistence: Only global module state is kept: enabled map, open count, input device pointers, and static phys strings. No persistent state exists.

Dependencies and integration points: Tied to Amiga architecture headers and hardware registers, `IRQ_AMIGA_VERTB`, input core, and memory region reservation around Denise joystick registers.

Risks: Hardware-specific bit conversions are difficult to test off m68k Amiga. The keybit setup references `BTN_LEFT`/mouse button word while reporting `BTN_TRIGGER`, so capability consistency should be checked in this tree. Shared IRQ lifetime depends on balanced open/close counts.

Test signals: Boot on Amiga or emulator with `MACH_IS_AMIGA`; verify two-port `map` variations; open two devices concurrently and ensure a single IRQ request/free cycle; validate ABS_X/ABS_Y direction and trigger events against real register changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/amijoy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/analog.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/analog.c

Purpose: Generic analog joystick/gamepad gameport driver. It supports classic resistor-capacitor timed axes, cooked gameport mode, several CH Flightstick/FCS/Saitek extensions, two logical devices per port, and module-parameter type overrides.

Important APIs/types/functions: `struct analog_port` tracks gameport, two `struct analog` devices, detected axis mask, cooked/raw mode, calibration, button state, failure counts, and timing calibration. `analog_parse_options()` interprets `map=` strings or numeric masks. `analog_init_port()` tries raw mode first, calibrates timing, detects Saitek behavior, then falls back to cooked mode. `analog_init_masks()` derives device capability masks from detected axes and configured options. `analog_cooked_read()` measures axis discharge times; `analog_button_read()` reads normal/CHF/Saitek buttons; `analog_decode()` reports events.

Control flow: Module init parses options and registers a gameport driver. Connect allocates port state, initializes raw or cooked access, derives masks, installs a 10 ms poll handler, and registers one or two input devices. Polling alternates between full axis reads and cheaper button-only reads where possible, then decodes events for active logical devices.

State and persistence: Per-port state persists until disconnect. Initial axis values become calibration baselines and input ABS ranges. `bads` and `reads` accumulate and are logged at disconnect. Module parameters affect all ports, with FIXME comments noting incomplete per-port option handling.

Dependencies and integration points: Uses gameport raw/cooked modes, `gameport_calibrate()`, input core, `seq_buf` for names, high-resolution timekeeping, and module parameter arrays.

Risks: Timing depends on CPU/gameport behavior and can break under virtualization or heavy interrupt latency. Option parsing partly uses only `analog_options[0]`, so multiple ports may not be independently configurable. Auto-detection can misclassify non-analog devices. Calibration based on first sampled values can produce poor ranges if the stick is not centered.

Test signals: Raw and cooked gameport devices; `map=auto`, named masks, numeric masks, and bad strings; Saitek/CHF/FCS paths; two-device split; disconnect failure-rate logging; ABS min/max/fuzz/flat after centered and off-center probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/analog.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/as5011.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/as5011.c

Purpose: I2C input driver for Austria Microsystems AS5011 magnetic joystick, reporting X/Y axes and a joystick button. It is platform-data based and uses IRQs for both axis and button events.

Important APIs/types/functions: `struct as5011_device` stores input, I2C client, GPIO descriptor, button IRQ, and axis IRQ. `as5011_i2c_write()` and `as5011_i2c_read()` issue protocol-mangling I2C transfers. `as5011_configure_chip()` resets the chip, enables low-power interrupt-active mode, configures spinning inversion, writes threshold registers from `struct as5011_platform_data`, and clears an initial interrupt by reading resolution. `as5011_axis_interrupt()` reads X/Y interrupt result registers; `as5011_button_interrupt()` reads GPIO state.

Control flow: Probe requires platform data and an axis IRQ, checks I2C adapter functionality, allocates input/state, configures button GPIO and threaded IRQ, configures the chip, requests the axis IRQ, registers input, and stores client data. Remove frees IRQs, unregisters input, and frees state.

State and persistence: No persistent storage. Runtime state is allocated with manual `kmalloc` and cleaned by explicit remove/error paths. The chip configuration is programmed during probe, not on input open.

Dependencies and integration points: Depends on I2C protocol mangling/NOSTART, GPIO descriptor API, threaded IRQs, input core, and `linux/input/as5011.h` platform data.

Risks: No DT/ACPI property path is present; missing platform data fails probe. The file TODO notes power management is incomplete. I2C reads use special transfer flags that many adapters may not support. IRQs are active before input registration on part of the path, so race behavior around early interrupts should be considered.

Test signals: Platform data with threshold and IRQ flag variants; adapters without protocol mangling; button GPIO polarity; axis IRQ reading signed values and reporting -80..80; remove/error path IRQ cleanup; suspend/power behavior if platform powers the chip externally.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/as5011.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/cobra.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/cobra.c

Purpose: Gameport driver for Creative Labs Blaster GamePad Cobra devices, supporting up to two gamepads on one gameport.

Important APIs/types/functions: `struct cobra` stores the gameport, up to two input devices, read/failure counters, detected device bitmask, and phys names. `cobra_read_packet()` captures a 36-bit packet per device using raw gameport edge timing and aligns packets against magic bits. `cobra_poll()` validates current device presence against the detected bitmask and reports axes/buttons. `cobra_connect()` opens raw gameport mode, probes devices, rejects unsupported extension-bit devices, sets polling, and registers inputs.

Control flow: Connect reads initial packets to identify existing pads, filters unsupported devices, installs a 20 ms poll handler, and registers one input node per detected pad. Open/close start and stop gameport polling. Polling reads both packet streams, drops samples on presence mismatch, reports digital X/Y and 12 buttons, and syncs each input.

State and persistence: Per-port state tracks initial existence mask and counters. No persistent storage; all state is freed at disconnect.

Dependencies and integration points: Integrates with raw gameport API, input core, and Creative vendor ID constants.

Risks: Packet acquisition disables interrupts and assumes 45 us strobe timing. Device existence is fixed at connect, so hotplug-like changes on the port count as bad reads rather than dynamic registration. Unknown extension-bit devices are deliberately unsupported.

Test signals: One-pad and two-pad Cobra setups; unsupported extension bit warning; bad packet injection/failure counter changes; open/close polling; X/Y and every mapped button bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/cobra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/db9.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/db9.c

Purpose: Parallel-port driver for DB9-era controllers including Atari/Amiga/Commodore/Amstrad multisystem sticks, Sega Genesis pads, Saturn pads/DPP, and Amiga CD32 pads. Device type and parport number are configured through module parameters.

Important APIs/types/functions: `struct db9_config` holds module parameter args for up to three parports. `struct db9_mode_data` describes each mode: name, button map, pad count, axis count, bidirectional requirement, and data direction. `struct db9` stores input devices, timer, parport device, mode, open count, mutex, and phys strings. `db9_timer()` contains the per-mode polling/decoding state machine. Saturn helpers (`db9_saturn_write_sub()`, `db9_saturn_read_packet()`, `db9_saturn_report()`) implement multi-device Saturn protocols.

Control flow: Module init validates that at least one configured device exists, then registers a parport driver. Attach matches configured parport number, validates mode and bidirectional requirements, claims an exclusive pardevice model, allocates up to two input devices, sets capabilities, and registers them. Open claims the parport and starts the 100 Hz timer. The timer reads or clocks the selected protocol and reschedules itself. Close stops the timer and releases the port.

State and persistence: State is global per configured port in `db9_base[]`, with open count and timer state until detach. No persistent storage. Module parameters are the only configuration source.

Dependencies and integration points: Depends on parport, input core, timer API, and module params `dev`, `dev2`, and `dev3`. Some modes require tristate/bidirectional parport support.

Risks: Protocol timing and parport electrical behavior are hardware-sensitive. Module parameter mistakes can prevent load or bind the wrong port. Several modes multiplex power/control bits and can affect attached hardware if misconfigured. Saturn multitap reporting is capped by `DB9_MAX_DEVICES`.

Test signals: Parameter validation for missing type and invalid mode; parport without tristate in bidirectional modes; Genesis 3/5/6 button sequences; Saturn digital/analog/multitap packets; CD32 clocked buttons; open/close claim/release behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/db9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/fsia6b.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/fsia6b.c

Purpose: Serio driver for FlySky FS-iA6B iBus RC receiver, exposing 14 servo channels as ABS axes and optional discrete switch positions as buttons.

Important APIs/types/functions: `IBUS_SERVO_COUNT` fixes 14 channels. `fsia6b_axes[]` maps channels to ABS codes. `switch_config` module parameter supplies 14 characters, each 0-3, describing switch positions per channel. `struct ibus_packet` stores parser state, offset, rolling 16-bit input buffer, and channel values. `fsia6b_serio_irq()` implements SYNC/COLLECT/PROCESS byte parser and event reporting. `fsia6b_serio_connect()` validates switch config, sets axis ranges, opens serio, and registers input.

Control flow: Interrupt handler shifts each incoming byte into a 16-bit word. It waits for sync `0x4020`, skips one collect word, then records 14 channel words. Once complete, it reports all ABS channels, maps channel values above 1900 or below 1100 to switch states according to `switch_config`, syncs input, and returns to SYNC.

State and persistence: Per-device parser state persists across serial bytes. Switch configuration is module-global and read at connect. No persistent storage.

Dependencies and integration points: Uses serio RS232 protocol `SERIO_FSIA6B`, input core, and module parameter parsing.

Risks: There is no checksum validation visible in this parser, so line noise can produce false channel data once sync is acquired. `switch_config` is indexed for 14 channels; too-short strings would be unsafe if module parameter validation elsewhere does not enforce length. Thresholds are hard-coded for typical FS-i6 output.

Test signals: Valid iBus frames for all 14 channels; corrupted sync and partial frames; switch_config values 0,1,2,3 and invalid characters; channel threshold edges 1100/1900; serio disconnect cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/fsia6b.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/gamecon.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/gamecon.c

Purpose: Parallel-port adapter driver for several console controllers: NES, SNES, SNES mouse, N64, multisystem joysticks, PSX pads, and PSX DDR mats. It is entirely module-parameter configured and multiplexes up to five devices per parport.

Important APIs/types/functions: `struct gc_config` stores parport/pad-type parameter lists. `enum gc_type` identifies pad protocols. `struct gc` owns pardevice, pad array, timer, pad type counts, open count, parport number, and mutex. `gc_setup_pad()` allocates and configures each input device. Protocol paths include `gc_n64_read_packet()`/`gc_n64_process_packet()`/`gc_n64_play_effect()`, `gc_nes_read_packet()`/`gc_nes_process_packet()`, `gc_multi_process_packet()`, and `gc_psx_read_packet()`/`gc_psx_report_one()`.

Control flow: Init validates `map`, `map2`, or `map3`, then registers a parport driver. Attach matches configured parport, registers an exclusive pardevice, allocates the `struct gc`, and creates each requested pad. Open claims the parport and starts a 100 Hz timer. The timer runs protocol processors in a fixed order: N64 first, NES/SNES/SNES mouse, multisystem, then PSX. Close stops the timer and releases the parport.

State and persistence: Per-parport state lives in `gc_base[]`; per-pad state includes type, input device, and phys path. N64 force-feedback subdevice context stores pad index for rumble. No persistent storage exists.

Dependencies and integration points: Uses parport control/data/status lines, input core, input FF memless for N64 rumble, timers, and module parameters. `psx_delay` tunes PSX bit timing.

Risks: All protocols are timing-sensitive and share one polling timer, with comments noting N64 controllers are confused by reads for about 200 us. Misconfigured pad types can drive the wrong lines. N64 rumble sends long command sequences with interrupts disabled. PSX reads use the longest detected packet length across all pads and can be affected by weak responses.

Test signals: Module parameter validation and multiple parport instances; NES/SNES button maps; SNES mouse ID filtering and relative axes; N64 axes/buttons/rumble; PSX digital, analog, rumble, DDR reports; open/close parport claim behavior and timer rescheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/gamecon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/gf2k.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/gf2k.c

Purpose: Gameport driver for Genius Flight 2000 family digital joysticks, with support tables for several Genius device IDs.

Important APIs/types/functions: `struct gf2k` stores gameport, input device, counters, detected ID/packet length, and phys string. `gf2k_trigger_seq()` sends reset/digital trigger timing sequences. `gf2k_read_packet()` captures triplet-coded packet bits. `gf2k_get_bits()` extracts fields from the triplet buffer. `gf2k_read()` maps decoded axes, hats, and buttons to input events. `gf2k_connect()` probes, initializes, identifies, calibrates ranges, and registers the input device.

Control flow: Connect opens raw gameport mode, sends reset and digital sequences, reads an initial packet, decodes ID, checks support tables, installs 20 ms polling, performs an initial read to set ABS ranges, and registers input. Polling reads a packet of the expected length and either increments bads or reports decoded state.

State and persistence: Per-device state includes detected ID and counters. Axis ranges are calibrated from initial sampled values. No persistence.

Dependencies and integration points: Uses raw gameport timing, input core, static device tables, and Genius gameport vendor ID.

Risks: The visible tree forces `gf2k->id = 6` when `RESET_WORKS` is not defined, which can misidentify other devices. Timing sequences disable interrupts and rely on microsecond behavior. Supported-device tables contain zeros for unimplemented IDs, so detection may intentionally reject hardware.

Test signals: Known F-23/Flight2000 device path; packet read lengths; hat direction conversion; forced-ID behavior with other hardware; initial calibration; disconnect cleanup and failure counter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/gf2k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/grip.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/grip.c

Purpose: Gameport driver for Gravis/Kensington GrIP protocol devices, including GamePad Pro, Blackhawk Digital, Xterminator Digital, and Xterminator DualControl. It can manage two devices on one gameport.

Important APIs/types/functions: `struct grip` stores gameport, two input devices, detected mode per device, and counters. `grip_gpp_read_packet()` reads 24-bit GamePad Pro packets and rotates to sync pattern. `grip_xt_read_packet()` reads four CRC-protected chunks for Xterminator-style devices. `grip_poll()` decodes each supported mode into ABS/key events. `grip_connect()` probes both positions, selects mode, sets capabilities/ranges, and registers inputs.

Control flow: Connect opens raw gameport mode and probes each of two shifts for GPP or XT packets. It installs a 20 ms poll handler and creates one input per detected mode. Open/close start or stop polling. Each poll reads the packet type for each device and reports axes, hats, throttle/gas/brake, and buttons according to mode.

State and persistence: Per-port state records detected modes and read/failure counts only for module lifetime. No persistent data.

Dependencies and integration points: Raw gameport access, input core, Gravis vendor ID, mode-specific static ABS/button tables.

Risks: Packet timing and CRC sync are fragile. Device modes are fixed at connect; runtime device changes are not dynamically registered. Many magic constants map protocol bits to inputs, so regressions are likely without hardware-specific tests.

Test signals: Probe each supported mode; dual-device operation with shifts 4 and 6; CRC failure handling; ABS ranges for centered and analog axes; button table coverage; start/stop polling on open/close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/grip.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/grip_mp.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/grip_mp.c

Purpose: Gameport driver for the Gravis Grip Multiport hub, intended to support up to four 9-pin digital gamepads/joysticks through one gameport.

Important APIs/types/functions: `struct grip_mp` stores the gameport, four slot pointers, and read/failure counters. `struct grip_port` stores each slot input device, mode, registration flag, button/axis state, and dirty flag. `mp_io()` implements the low-level 28-bit multiport packet exchange and optional command sending. `multiport_io()` wraps it with IRQ-off timing. `dig_mode_start()` sends the magic digital-mode sequence. `get_and_decode_packet()` interprets slot/device packets. `register_slot()` creates an input device for a newly detected grip pad.

Control flow: Connect opens raw gameport mode, installs the poll handler, and calls `multiport_init()`. Initialization sends the digital-mode sequence and repeatedly consumes packets until slot state looks valid. Polling fetches up to four packets, decodes slot updates or resets, dynamically registers new grip pads, and reports dirty slots.

State and persistence: Slot state is intended to persist in four `struct grip_port` objects under `grip->port[]`, with dynamic registration flags and latest decoded state. No persistent storage exists.

Dependencies and integration points: Raw gameport timing, input core, Gravis vendor ID, and dynamic input registration during polling.

Risks: In this source snapshot, `struct grip_mp` contains four `struct grip_port *` pointers, but `grip_connect()` only allocates `struct grip_mp` and does not allocate or initialize the slot objects before helpers dereference `grip->port[slot]`. That is a high-severity null-pointer risk in `slots_valid()`, `get_and_decode_packet()`, and the post-init empty-slot check. Timing-sensitive packet exchange also disables interrupts and relies on exact handshakes.

Test signals: Basic probe should be tested first for null dereferences; then digital-mode init, slot add/remove packets, dynamic input registration, dirty-state reporting, and disconnect cleanup for every registered slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/grip_mp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/guillemot.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/guillemot.c

Purpose: Gameport driver for Guillemot digital interface protocol joysticks, currently table-driven for a Guillemot Pad.

Important APIs/types/functions: `struct guillemot_type` describes supported ID, ABS map, button map, hat presence, and name. `struct guillemot` stores gameport, input device, counters, selected type, packet length, and phys string. `guillemot_read_packet()` reads a 17-byte bitstream with start/strobe timeouts. `guillemot_poll()` validates packet delimiters `0x55` and `0xaa`, reports axes, hat, buttons, and syncs. `guillemot_connect()` probes ID bytes and registers the input.

Control flow: Connect opens raw gameport mode, reads one full packet, validates framing, matches `data[11]` against supported type table, installs a 20 ms poll handler, sets capabilities, and registers input. Polling repeats the packet read and reports events on valid frames.

State and persistence: Per-device state stores selected type and counters only. No persistent storage.

Dependencies and integration points: Raw gameport API, input core, Guillemot vendor ID, static type table.

Risks: Only one ID is supported. Timing is IRQ-off and sensitive to gameport speed. Disconnect log appears to print `reads`/`bads` in a misleading order in the message text. Invalid frames still call `input_sync()` without new events.

Test signals: Valid pad packet including delimiter bytes and ID; unknown ID warning; packet timeout path and bad counter; ABS range 0..255 and hat -1..1; open/close polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/guillemot.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Kconfig

Purpose: Kconfig entries for Logitech/Thrustmaster/Guillemot I-Force force-feedback joysticks and wheels. It defines the core driver and separate USB and RS232 transport options.

Important APIs/types/functions: `JOYSTICK_IFORCE` is a tristate core option depending on `INPUT && INPUT_JOYSTICK`. `JOYSTICK_IFORCE_USB` depends on `JOYSTICK_IFORCE && USB`. `JOYSTICK_IFORCE_232` depends on `JOYSTICK_IFORCE && SERIO`.

Control flow: Build configuration selects the core `iforce` module and optionally one or both transport modules. Help text tells users they must select at least one transport, but Kconfig does not enforce this with `select` or dependency logic.

State and persistence: No runtime state; it controls build-time availability.

Dependencies and integration points: Integrates with Linux input joystick Kconfig, USB, SERIO, and documentation references for `inputattach` and force feedback.

Risks: Users can enable the core without a transport and get no usable hardware path. Transport modules depend on the core but are built as independent objects in the Makefile.

Test signals: Kconfig combinations: core only, USB only with core, RS232 only with core, built-in/module mixes, and documentation visibility for RS232 setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Makefile -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Makefile

Purpose: Build rules for the I-Force core and transport drivers.

Important APIs/types/functions: `obj-$(CONFIG_JOYSTICK_IFORCE) += iforce.o` builds the core composite object. `iforce-y := iforce-ff.o iforce-main.o iforce-packets.o` defines its constituent source files. `obj-$(CONFIG_JOYSTICK_IFORCE_232) += iforce-serio.o` and `obj-$(CONFIG_JOYSTICK_IFORCE_USB) += iforce-usb.o` build transport modules.

Control flow: Kbuild composes `iforce.o` from force-feedback construction, core input initialization, and packet handling. USB and serio transports are separate module objects that include the shared header and call exported core functions.

State and persistence: No runtime state; build-only artifact.

Dependencies and integration points: Mirrors Kconfig symbols and exports from `iforce-main.c`, `iforce-packets.c`, and `iforce.h`.

Risks: Transport modules are separate from the core, so symbol export/import and module load ordering matter. Kconfig allows core without transports.

Test signals: Build all three symbols as built-in and modules; ensure `iforce.o` contains all core objects; modpost should resolve exported `iforce_init_device`, `iforce_send_packet`, and `iforce_process_packet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-ff.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-ff.c

Purpose: Force-feedback effect encoder for I-Force devices. It converts Linux `struct ff_effect` periodic, constant, spring, and damper effects into I-Force command packets and manages on-device effect parameter memory.

Important APIs/types/functions: Modifier builders include `make_magnitude_modifier()`, `make_period_modifier()`, `make_envelope_modifier()`, and `make_condition_modifier()`. Change detectors include `need_*_modifier()` and `need_core()`. `make_core()` sends the common effect core packet and restarts effects if requested. Public upload functions are `iforce_upload_periodic()`, `iforce_upload_constant()`, and `iforce_upload_condition()`.

Control flow: The input FF upload callback in `iforce-main.c` dispatches to one of these upload functions. Each upload function allocates or reuses resource chunks for needed modifiers, sends modifier packets, sets `FF_MOD*_IS_USED`, sends a core packet when core fields changed, and returns 0 for sent updates, 1 for no change, or a negative error.

State and persistence: Uses `iforce->device_memory` resource tree and each `core_effects[id]` resource/flag set. `mem_mutex` protects resource allocation and release. State persists while the input FF effect exists, then is freed by erase in `iforce-main.c`; no disk persistence.

Dependencies and integration points: Shared `iforce.h`, input FF effect structures, Linux resource allocator, I-Force command IDs, and `iforce_send_packet()`.

Risks: The file comments call out arithmetic right-shift assumptions in condition scaling. Resource allocation sizes and device memory limits can reject complex effects with `-ENOSPC`. Some unsupported condition types return `-1` rather than a specific errno. Effect replay count is not preserved when restarting after update.

Test signals: Upload/update/no-change for periodic waveforms, constant effects, spring/damper condition effects, envelope-only changes, memory exhaustion, erase/reupload cycles, and packet bytes for boundary magnitudes including values near `0x80`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-ff.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-main.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-main.c

Purpose: Core I-Force input device initialization and Linux force-feedback callbacks shared by USB and RS232 transports.

Important APIs/types/functions: Static tables map known vendor/product IDs to button, ABS, and FF capability arrays. `iforce_init_device()` allocates an input device, initializes wait queues/spinlocks/mutexes, queries the device, configures capabilities, creates the input FF device, and registers input. FF callbacks include `iforce_playback()`, `iforce_set_gain()`, `iforce_set_autocenter()`, `iforce_upload_effect()`, and `iforce_erase_effect()`. Open/close call transport `start_io()`/`stop_io()` and enable/disable FF.

Control flow: A transport allocates an enclosing transport struct, assigns `xport_ops`, and calls `iforce_init_device()`. Core initialization waits for query response, reads vendor/product/memory/effect counts, disables autocenter, matches a device table entry, sets input ranges, and registers callbacks. Uploads set an update bit until a status packet marks the relevant modifier memory ready.

State and persistence: `struct iforce` owns transmit ring state, effect memory resource tree, per-effect flags/resources, and synchronization primitives. This state lasts for the device lifetime. No persistent storage.

Dependencies and integration points: Exports `iforce_init_device()` for transport modules. Depends on input FF core, packet helper functions, unaligned access helpers, and transport operations from `iforce_xport_ops`.

Risks: Probe waits up to about five seconds for an ID response. Unknown devices fall back to generic joystick maps. `iforce_close()` waits for transmit completion after disabling FF; transport bugs can hang close. Duplicate or questionable device table entries should be tested against real hardware.

Test signals: USB and RS232 transport initialization; device query timeout; known and unknown VID/PID matching; FF effect upload/play/erase/status; open/close sequencing; memory size reported by packet B limiting effect resource allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-packets.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-packets.c

Purpose: Shared I-Force packet transmit queueing and inbound packet decoding for position, wheel, and FF status reports.

Important APIs/types/functions: `iforce_send_packet()` queues command ID, length, and data into the circular transmit buffer under spinlock, then starts transport transmission. `iforce_control_playback()` sends FF play/stop commands. `iforce_process_packet()` decodes inbound packet IDs. `iforce_report_hats_buttons()` maps packed hat/button bytes. `mark_core_as_ready()` clears effect update flags when status packets reference modifier memory addresses.

Control flow: Force-feedback and control paths call `iforce_send_packet()`, which appends to the ring and invokes `xport_ops->xmit()` when the ring was empty. Transport IRQ/completion paths call `iforce_process_packet()`. Packet ID 0x01 reports joystick axes/throttle/rudder/buttons, 0x03 reports wheel/gas/brake/buttons, and 0x02 reports FF status and effect update completion.

State and persistence: Uses `iforce->xmit` circular buffer, `xmit_flags`, per-effect flags, and input state. No persistence outside device lifetime.

Dependencies and integration points: Shared with both USB and serio transports via exported symbols; depends on input reporting APIs, wait queue wakeups from transport, and iforce device type maps.

Risks: `iforce_send_packet()` returns `-1` for buffer full rather than standard errno. Callers must ensure data length matches `LO(cmd)`. Status packet handling indexes `core_effects[i]` from packet data without visible bounds check on `i`, so malformed device data deserves scrutiny. Hat table has 16 entries but only first 8 initialized meaning invalid hat nibbles become zeroed axes.

Test signals: Transmit ring wraparound and full-buffer handling; packet IDs 0x01/0x02/0x03 with short and full lengths; FF status play/stop events; modifier-ready address matching; wakeups after transport completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-packets.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-serio.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-serio.c

Purpose: RS232/serio transport for I-Force devices. It frames outbound packets with serial start/checksum bytes, parses inbound serial packets, and bridges the shared I-Force core to the serio subsystem.

Important APIs/types/functions: `struct iforce_serio` embeds `struct iforce` and stores serio pointer plus receive parser state, command-response buffer, and data buffer. `iforce_serio_xmit()` drains the shared transmit ring to `serio_write()` with framing/checksum. `iforce_serio_get_id()` sends query packets and waits for a matching response. `iforce_serio_irq()` is the byte-wise receive parser. `iforce_serio_connect()` opens serio and calls `iforce_init_device()`.

Control flow: Connect allocates state, assigns transport ops, opens serio, and initializes the core input device. Outbound xmit starts when the core queue transitions from empty. Inbound IRQ waits for 0x2b start, packet ID, length, data, then either completes an expected command response or passes the packet to `iforce_process_packet()`.

State and persistence: Receive parser fields (`pkt`, `id`, `len`, `idx`, checksum accumulator, expected packet) persist across bytes. Core state is embedded. No persistent storage.

Dependencies and integration points: Serio RS232 protocol `SERIO_IFORCE`, input core via shared I-Force, wait queues for command response, and `module_serio_driver`.

Risks: The receive parser accumulates `csum` but does not visibly validate an incoming checksum byte in this snapshot. `iforce_serio_stop_io()` is a TODO and does not wait for final packets. Query response timeout is one second per command. Synchronous `serio_write()` under spinlock/IRQ-save context should be evaluated with serio backend behavior.

Test signals: Byte framing with valid/invalid start, ID, length, and checksum-like bytes; query timeout and wrong-ID response; write wakeup reentry; disconnect during transmit; core packet delivery after type is initialized.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-serio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-usb.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-usb.c

Purpose: USB transport for I-Force devices. It manages interrupt-in and interrupt-out URBs, vendor control queries, and bridges USB devices to the shared I-Force core.

Important APIs/types/functions: `struct iforce_usb` embeds `struct iforce` and stores USB device/interface, IRQ/out URBs, and aligned input/output buffers. `iforce_usb_probe()` validates endpoints, allocates URBs/state, fills interrupt URBs, and calls `iforce_init_device()`. `iforce_usb_xmit()`/`__iforce_usb_xmit()` drain the shared transmit ring to the interrupt-out URB. `iforce_usb_irq()` forwards inbound reports to `iforce_process_packet()`. `iforce_usb_get_id()` performs vendor control reads.

Control flow: USB probe requires endpoint 0 interrupt-in and endpoint 1 interrupt-out, initializes URBs, and registers the input device via core. Input open calls `start_io()`, which submits the interrupt-in URB. Outbound packets are submitted one at a time; completion calls `__iforce_usb_xmit()` to send the next packet. Disconnect unregisters input, frees URBs, and releases state.

State and persistence: Per-interface state stores URBs and transfer buffers; shared core state holds FF and transmit ring state. No persistent storage.

Dependencies and integration points: USB core, interrupt endpoints, vendor control messages, input/FF shared I-Force core, and static USB ID table.

Risks: Endpoint order is assumed rather than searched by direction beyond indexes 0 and 1. Inbound URB actual length should be at least one before using `data_in[0]` and `actual_length - 1`; malformed zero-length reports would be risky. Disconnect does not explicitly call transport stop before freeing URBs after input unregister, so lifetime relies on input close/unregister behavior.

Test signals: All USB IDs; endpoint order variants; control query timeout or wrong ID; URB resubmit after transient status; transmit ring wrap and multiple queued packets; disconnect during active input and FF playback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce-usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce.h -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce.h

Purpose: Shared definitions for I-Force core, FF effect memory tracking, transport operations, command IDs, transmit ring helpers, and exported function prototypes.

Important APIs/types/functions: `struct iforce_core_effect` tracks two modifier resource chunks and effect flags. `struct iforce_device` maps VID/PID to input capability arrays. `struct iforce_xport_ops` abstracts transport operations: `xmit`, `get_id`, `start_io`, and `stop_io`. `struct iforce` stores input device, device type, transport ops, transmit ring, wait queue, on-device memory resource, per-effect state, and memory mutex. Command macros define FF packet IDs and `XMIT_SIZE`/`XMIT_INC` manage the circular buffer.

Control flow: Transport modules embed `struct iforce`, assign `xport_ops`, and call `iforce_init_device()`. Core FF and packet code use the shared fields and macros to queue commands, parse responses, and manage effect resources.

State and persistence: Defines runtime state containers only. Effect flags persist for the lifetime of each uploaded input FF effect and device state. No disk persistence.

Dependencies and integration points: Linux input, module, spinlock, circular buffer, mutex, wait queue, and resource APIs. Exposes core functions to transport modules and references transport driver symbols.

Risks: The transmit buffer is fixed at 256 bytes; callers must manage backpressure. `XMIT_INC` macro mutates its argument and assumes power-of-two buffer size. The high-byte fixup macro and time scaling are protocol-specific and easy to misuse.

Test signals: Compile inclusion from all I-Force source files; ring wrap behavior with `XMIT_INC`; effect flag lifecycle; transport ops completeness for USB and serio.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/iforce/iforce.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/interact.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/interact.c

Purpose: Gameport driver for InterAct digital joystick/gamepad devices, specifically HammerHead/FX and ProPad 8 Digital.

Important APIs/types/functions: `struct interact_type` defines ID, ABS/button maps, product name, packet length, and count of 8-bit axes. `struct interact` stores gameport, input, counters, selected type, packet length, and phys string. `interact_read_packet()` reads up to 32 bits across three data streams from raw gameport edges. `interact_poll()` maps packets by type into axes and buttons. `interact_connect()` probes a signature and ID, configures input, and registers.

Control flow: Connect opens raw mode, reads a 64-bit probe window, validates header bytes, finds type by `data[2] >> 16`, installs a 20 ms poll handler, and registers input. Polling reads the type-specific length and decodes either analog-like HammerHead/FX axes plus hat/buttons or ProPad digital axes/buttons.

State and persistence: Per-device type and counters exist for module lifetime. No persistence.

Dependencies and integration points: Raw gameport API, input core, InterAct vendor ID constants, static type table.

Risks: Only two device IDs are accepted. Probe and polling depend on tight IRQ-off timing. `interact_read_packet()` stores parallel bit streams in three u32s; changes to packet length or stream interpretation can silently remap controls.

Test signals: Known HHFX and PP8D devices; unknown ID warning; short read bad counter; ABS ranges for 8-bit and digital axes; all mapped buttons; open/close polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/interact.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/joydump.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/joydump.c

Purpose: Diagnostic gameport driver that dumps raw or cooked gameport data transitions to the kernel log for debugging joystick protocols.

Important APIs/types/functions: `struct joydump` stores timestamp and data byte for one captured transition. `joydump_connect()` opens a gameport in raw mode or cooked fallback, captures up to 256 raw transitions over up to 10 ms after a trigger, and prints a formatted trace. `joydump_disconnect()` closes the gameport.

Control flow: On connect, the driver prints a start banner and speed. If raw open fails, it tries cooked mode, prints axes/buttons, and ends. In raw mode it allocates a capture buffer, disables interrupts, triggers the port, records changes and timestamps, restores interrupts, dumps the captured bit patterns, frees the buffer, and returns success.

State and persistence: No long-lived device state is stored in driver data. The only output is kernel log text.

Dependencies and integration points: Gameport raw/cooked APIs, printk logging, delay/timing loops, and module gameport driver registration.

Risks: It is intentionally invasive and log-heavy. Capturing with interrupts disabled for up to a 10 ms timeout can affect system latency. It does not register an input device, so it is a debugging tool rather than a normal driver.

Test signals: Raw-capable and cooked-only gameports; no-memory path; transition output format; disconnect closing the mode opened during connect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/joydump.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/magellan.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/magellan.c

Purpose: Serio RS232 driver for LogiCad3D Magellan and SpaceMouse six-degree-of-freedom controllers.

Important APIs/types/functions: `struct magellan` stores input device, current packet index, packet data buffer, and phys string. `magellan_interrupt()` accumulates bytes until carriage return. `magellan_process_packet()` decodes axis (`d`) and button (`k`) packets. `magellan_crunch_nibbles()` validates and strips encoded nibbles. `magellan_connect()` allocates input and opens serio.

Control flow: Connect creates an input device with six ABS axes and nine buttons, opens the serio port, and registers the input. The interrupt handler buffers serial bytes. On `\r`, it dispatches packet processing and resets the index. Axis packets must be 25 bytes and produce six signed 16-bit-ish values offset by 32768. Button packets must be 4 bytes and produce a 9-bit mask.

State and persistence: Packet assembly state persists across serial interrupts. No persistent storage.

Dependencies and integration points: Serio protocol `SERIO_MAGELLAN`, input core, RS232 devices configured externally.

Risks: Oversized packets are truncated by ignoring extra bytes until `\r`. Invalid nibble encoding silently drops packets. Axis range is configured as -360..360 but decoded values are much wider before input core filtering/clamping behavior, which should be verified.

Test signals: Valid `d` and `k` packets; malformed nibble bytes; packets without carriage return; disconnect during partial packet; ABS and key event ranges through evtest.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/magellan.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/maplecontrol.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/maplecontrol.c

Purpose: Sega Dreamcast Maple bus controller driver. It registers Dreamcast controller input devices and polls condition data through the Maple subsystem.

Important APIs/types/functions: `struct dc_pad` stores input device and Maple device. `dc_pad_callback()` decodes Maple condition response bytes into buttons, hats, triggers, and analog axes. `dc_pad_open()` starts periodic `maple_getcond_callback()` polling at `HZ/20`; `dc_pad_close()` stops it. `probe_maple_controller()` builds input capabilities from `function_data`. `remove_maple_controller()` unregisters input and clears callback state.

Control flow: Maple driver probe allocates pad/input, inspects function data bitfields to set key/ABS capabilities, configures axis ranges, registers input, and stores driver data. Opening input schedules Maple condition callbacks. Each callback decodes response buffer offsets 8..15 and reports events. Removal unregisters input and frees pad state.

State and persistence: Per-controller state includes input and Maple device pointers. Polling is active only while input is open. No persistent storage.

Dependencies and integration points: Dreamcast Maple bus, input core, Maple condition polling, and `MAPLE_FUNC_CONTROLLER`.

Risks: Callback assumes response buffer layout and sufficient length. Hat axis ranges are configured with min 1 and max -1 in this snapshot, which is unusual and should be tested. Capabilities depend on device-advertised function bits; bad firmware data may hide controls.

Test signals: Dreamcast controller probe; open/close callback scheduling; response buffer with each button/axis bit; function_data capability filtering; remove while callback is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/maplecontrol.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/n64joy.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/n64joy.c

Purpose: Platform driver for Nintendo 64 console controller ports, supporting up to four non-hotpluggable controllers through the N64 SI/PIF hardware.

Important APIs/types/functions: `struct n64joy_priv` stores aligned SI buffer, timer, mutex, input devices, MMIO register base, and open count. `struct joydata` overlays PIF response data with controller fields. `n64joy_exec_pif()` performs SI DMA write/read to PIF RAM with cache maintenance and IRQ-off critical section. `n64joy_poll()` reports buttons and signed X/Y axes. `n64joy_probe()` scans controllers at init and registers inputs.

Control flow: Module init uses `platform_driver_probe()`; probe maps SI registers, executes scan PIF commands, registers an input device for each connected controller ID, and returns `-ENODEV` if none found. Opening the first input starts a 16 ms timer; polling executes PIF commands and reports all registered controller states; closing the last input deletes the timer.

State and persistence: Controller presence is scanned once at init and stored in `n64joy_dev[]`. Open count controls timer lifetime. No module unloading support is provided; comments explain init memory is freed for an embedded RAM-constrained target.

Dependencies and integration points: Platform MMIO resource, N64 SI registers/PIF RAM physical address, cache maintenance functions, input core, timers, and mutex guards.

Risks: Busy-waiting SI status can hang if hardware stops responding. No hotplug support. `n64joy_opened` is `u8`, so many opens could overflow in theory, though input open counts are normally bounded by users. Direct hardware/cache operations are architecture-specific.

Test signals: N64 hardware or emulator with 0..4 controllers; scan ID validation; open/close timer count; SI DMA busy handling; axes signedness and button mapping; no-controller probe return.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/n64joy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/psxpad-spi.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/psxpad-spi.c

Purpose: SPI driver for PlayStation 1/2 joypads, with optional rumble force feedback under `CONFIG_JOYSTICK_PSXPAD_SPI_FF`.

Important APIs/types/functions: `struct psxpad` stores SPI device, input device, phys path, motor enable/levels, send buffer, and response buffer. `psxpad_command()` performs one synchronous SPI transfer. Optional FF helpers configure motors and implement `psxpad_spi_play_effect()`. `psxpad_spi_poll()` sends the poll command, decodes analog (`0xCE`) and digital (`0x82`) responses, and reports axes/buttons. `psxpad_spi_probe()` configures SPI mode/speed, input capabilities, polling, FF, runtime PM, and registration.

Control flow: Probe allocates state/input, sets ABS/key capabilities, initializes optional memless FF, forces SPI mode 3 at 125 kHz, sets polling at about 60 Hz, registers input, and enables runtime PM. Input open gets runtime PM; close puts it. Each poll optionally configures motors, fills command bytes with current motor levels, transfers, decodes response by controller mode, and syncs input.

State and persistence: Motor levels and enable flags persist in `struct psxpad` between polls. Runtime PM state is tied to input open/close. No persistent storage.

Dependencies and integration points: SPI core, input polling, runtime PM, optional input FF memless, and PSX protocol bit reversal.

Risks: Probe sets `spi->controller->min_speed_hz` and `max_speed_hz`, which mutates controller-wide constraints rather than only this device. `spi_set_drvdata()` is not visible before suspend uses `spi_get_drvdata()`, so suspend path should be verified. Motor configuration is called every poll when FF is enabled, adding traffic.

Test signals: Digital and analog controllers; rumble enabled/disabled builds; runtime PM open/close; suspend clearing motors; SPI setup failure; response modes other than `0xCE`/`0x82`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/psxpad-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/pxrc.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/pxrc.c

Purpose: USB input driver for PhoenixRC Flight Controller Adapter, exposing adapter channel data as ABS axes and one button.

Important APIs/types/functions: `struct pxrc` stores input, USB interface, interrupt URB, PM mutex, open flag, and phys path. `pxrc_probe()` finds the interrupt endpoint, allocates state, buffer, URB, input device, fills the URB, and registers input. `pxrc_usb_irq()` decodes 8-byte interrupt reports. `pxrc_open()` submits the URB; `pxrc_close()` kills it. Suspend/resume/reset callbacks coordinate URB lifetime under `pm_mutex`.

Control flow: Probe binds to VID/PID 1781:0898, locates the endpoint, prepares an interrupt-in URB, configures ABS ranges 0..255, and registers input. Opening the input submits the URB. Each successful URB completion reports axes/buttons and resubmits. Suspend/reset stop the URB if open and resume/post-reset resubmit.

State and persistence: Per-interface state tracks open status and URB. Buffer and input are devm-managed; URB is freed through a devm action. No persistent storage.

Dependencies and integration points: USB core, USB input ID helpers, input core, mutex guard helpers, PM/reset USB driver callbacks.

Risks: `pxrc_disconnect()` is empty because resources are devm-managed; correctness depends on input unregister/devres ordering during disconnect. Reports with `actual_length != 8` are ignored but still resubmitted. Open maps any submit failure to `-EIO`, losing specific errno.

Test signals: Correct VID/PID binding; endpoint missing path; 8-byte report mapping; short report ignore; suspend/resume/reset while open and closed; unplug during active URB.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/pxrc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/qwiic-joystick.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/qwiic-joystick.c

Purpose: I2C polling driver for SparkFun Qwiic Joystick, reporting two 10-bit axes and a thumb button.

Important APIs/types/functions: `struct qwiic_jsk` stores phys string, input device, and I2C client. `struct qwiic_ver` and `struct qwiic_data` model firmware version and data registers. `qwiic_probe()` reads firmware version, allocates state/input, configures ABS/button capabilities, sets input polling intervals, and registers. `qwiic_poll()` reads the data block and reports X/Y/thumb.

Control flow: Probe first reads version register 1 and rejects short reads. It then creates input with BUS_I2C, ABS_X/ABS_Y ranges 0..1023, `BTN_THUMBL`, and a 16 ms polling interval with 8..32 ms bounds. Poll reads register 3 as a block; only exact-size reads produce events.

State and persistence: Per-client state is devm-managed. No persistent storage. Firmware version is logged only at debug level.

Dependencies and integration points: I2C SMBus block reads, input polling, OF compatible `sparkfun,qwiic-joystick`, I2C ID table using `KBUILD_MODNAME`.

Risks: No interrupt mode; missed fast changes are possible at polling interval. Axis values are big-endian and shifted right by 6, so firmware layout changes would break scaling. Short reads are silently ignored during polling.

Test signals: Version read success/failure; data block endian/scaling; thumb active-low behavior; poll interval sysfs adjustments within bounds; OF and I2C ID binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/qwiic-joystick.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/sensehat-joystick.c -->
# sources/distributed-fs/ceph-client/drivers/input/joystick/sensehat-joystick.c

Purpose: Platform input driver for Raspberry Pi Sense HAT joystick buttons, using a parent regmap and IRQ to report five key states.

Important APIs/types/functions: `struct sensehat_joystick` stores platform device, input device, previous button bitmap, and parent regmap. `keymap[]` maps five bits to DPAD down/right/up/select/left. `sensehat_joystick_report()` reads register `0xf2`, diffs against previous state, reports only changed keys, syncs, and updates previous state. `sensehat_joystick_probe()` obtains the parent regmap, allocates input, sets key/repeat capabilities, registers input, and requests threaded IRQ.

Control flow: Probe sets up the input before requesting IRQ. Each IRQ reads current key state through regmap, computes `changes` with `bitmap_xor()`, reports each changed key according to the map, and syncs. Failed regmap reads return `IRQ_NONE`.

State and persistence: `prev_states` tracks last reported button bits. All memory/resources are devm-managed. No persistent storage.

Dependencies and integration points: Platform bus, OF compatible `raspberrypi,sensehat-joystick`, parent regmap from Sense HAT MFD, threaded IRQ, input core with key repeat.

Risks: Initial `prev_states` is zero, so keys already pressed before first IRQ will be reported as pressed on first interrupt but there is no initial sync at probe. `bitmap_xor()` is used on scalar `unsigned long` storage; this is valid for small bitmaps but should stay aligned with keymap length. Regmap errors drop the IRQ as unhandled.

Test signals: IRQ with each of five bits changing; simultaneous changes; regmap read error; initial pressed state; key repeat capability; OF binding and missing parent regmap.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/joystick/sensehat-joystick.c -->
