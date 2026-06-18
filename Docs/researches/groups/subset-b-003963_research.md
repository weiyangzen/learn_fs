# subset-b-003963 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.c

## Purpose

`applespi.c` is the MacBook/MacBook Pro SPI keyboard and touchpad driver. It switches Apple ACPI-attached input hardware from USB to SPI when needed, exchanges fixed 256-byte SPI packets with keyboard, touchpad, and info endpoints, registers a keyboard input device immediately, and registers the multitouch touchpad after receiving model information from the controller.

## Important APIs, Types, and Functions

- Protocol structs model the hardware ABI: `keyboard_protocol`, `tp_finger`, `touchpad_protocol`, `touchpad_info_protocol`, command payloads, `message`, and `spi_packet`.
- `struct applespi_data` holds SPI messages/transfers, input devices, command queue state, last keyboard state, touchpad dimensions, ACPI GPE/method handles, LED state, drain/suspend flags, and debugfs state.
- `applespi_send_cmd_msg()` serializes touchpad-info, multitouch-init, caps-lock LED, and keyboard-backlight commands into one pending write exchange.
- `applespi_notify()` is the ACPI GPE handler and queues async reads; `applespi_async_read_complete()` and `applespi_got_data()` validate and dispatch received packets.
- `applespi_handle_keyboard_event()` reports rollover keyboard state; `report_tp_state()` reports multitouch slots and click state.
- `applespi_probe()`, `applespi_remove()`, `applespi_suspend()`, `applespi_resume()`, `applespi_shutdown()`, and `applespi_poweroff_late()` bind the SPI, ACPI, PM, LED, EFI, debugfs, and input lifecycles.

## Control Flow

Probe rejects systems where the USB interface is already active, allocates transfer buffers, caches ACPI `SIEN`/`SIST` handles, enables SPI, creates the keyboard input device, installs/enables the ACPI GPE handler, queues touchpad setup, registers a keyboard-backlight LED class device, and exposes debugfs touchpad-dimension helpers. GPE delivery calls `applespi_notify()`, which queues a read. The read callback CRC-checks the packet, reassembles up to two packets, validates the inner message CRC and declared length, then dispatches keyboard reads, touchpad reads, or write responses. Write commands are serialized under `cmd_msg_lock`; completion reads a four-byte status and waits for the response GPE before allowing the next command.

## State and Persistence Behavior

Runtime state is mostly in `applespi_data`: last pressed keys and Fn state are retained to generate releases, touchpad slot positions persist between reports for input-mt assignment, `saved_msg_len` tracks multipart assembly, and desired/actual LED/backlight command state is held until hardware catches up. The driver persists keyboard backlight level through the EFI variable `KeyboardBacklightLevel`. Suspend/remove set drain flags, wait for active writes/reads, disable GPEs, and mark the device suspended; resume clears transient command/read/write state, re-enables SPI/GPE, and reinitializes multitouch mode.

## Dependencies and Integration Points

The driver integrates with SPI core async transfers, ACPI methods and GPEs (`APP000D`, `_GPE`, `SIEN`, `SIST`, optional USB-status methods), Linux input and multitouch, LED class, EFI runtime variables, debugfs, CRC16, unaligned helpers, and local `applespi.h`/`applespi_trace.h`. It uses module parameters for Fn behavior, ISO key swapping, Fn remapping, and touchpad dimensions.

## Risks and Edge Cases

The protocol parser depends on exact packet/message length, CRC, endian, and maximum-packet assumptions; malformed offsets or finger counts can otherwise corrupt message assembly or input reporting. Command writes are single-flight with a timeout heuristic, so lost response GPEs can delay LED/backlight updates. Touchpad registration runs from workqueue because SPI callbacks cannot sleep; events before registration are dropped. The touchpad model table has fallback dimensions for unknown models. The driver reads ACPI buffer properties as `u64 *`, so malformed firmware property sizes would be risky. Drain and suspend ordering must avoid deadlocks between callbacks, GPE completion, and `cmd_msg_lock`.

## Test Signals

Useful signals include probe on APP000D systems with USB disabled/enabled, ACPI method failures, GPE read storms, corrupted packet CRC/length/offset handling, two-packet touchpad reports, keyboard rollover overflow, Fn mode/remap/ISO translation, caps-lock LED events, backlight scaling and EFI save/restore, unknown touchpad models and dimension overrides, suspend/resume with in-flight reads or writes, remove during active GPEs, and tracepoint output for reads/writes/status/CRC failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.h -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.h

## Purpose

`applespi.h` is the shared local trace/protocol classification header for the Apple SPI keyboard/touchpad driver. It defines the event categories and packet directions used by `applespi.c` and `applespi_trace.h`.

## Important APIs, Types, and Functions

- `enum applespi_evt_type` assigns bit-valued categories for touchpad init commands, backlight commands, caps-lock commands, keyboard reads, touchpad reads, unknown reads, IRQ notification, and CRC failure.
- `enum applespi_pkt_type` names packet views as `PT_READ`, `PT_WRITE`, and `PT_STATUS`.

## Control Flow

The header has no runtime flow. `applespi.c` chooses an `applespi_evt_type` for the current command or received packet and passes it with an `applespi_pkt_type` to the tracepoint wrappers defined in `applespi_trace.h`.

## State and Persistence Behavior

It owns no state. Its enum values become part of tracepoint payloads and therefore influence userspace tracing interpretation.

## Dependencies and Integration Points

The file depends on `BIT()` being available before use; `applespi.c` includes kernel headers before it, and `applespi_trace.h` includes it before declaring tracepoint fields. It is private to the Apple SPI driver directory.

## Risks and Edge Cases

Changing enum numeric values can break trace consumers and `applespi_get_trace_fun()` assumptions. Because values are bit masks rather than dense small integers, callers should not use them as compact array indexes.

## Test Signals

Compile coverage with tracing enabled, tracepoint format inspection, and runtime traces for each event category are the main validation signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi_trace.h -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi_trace.h

## Purpose

`applespi_trace.h` declares ftrace tracepoints for Apple SPI keyboard/touchpad traffic. It lets developers capture raw read packets, command writes, write-status bytes, IRQ notifications, and CRC-failed buffers without adding ad hoc logging.

## Important APIs, Types, and Functions

- `DECLARE_EVENT_CLASS(dump_message_template)` records `evt_type`, `pkt_type`, dynamic byte buffer, and length.
- `DEFINE_DUMP_MESSAGE_EVENT()` instantiates packet-dump events for touchpad init, backlight, caps-lock, keyboard data, touchpad data, unknown data, and bad CRC.
- `TRACE_EVENT(applespi_irq_received)` records GPE/read IRQ notification.
- `TRACE_INCLUDE_PATH` and `TRACE_INCLUDE_FILE` point trace generation at this local header.

## Control Flow

When `CREATE_TRACE_POINTS` is defined in `applespi.c`, this header expands into tracepoint definitions. Runtime callers invoke the generated `trace_applespi_*()` helpers around SPI write, status, read, IRQ, and CRC-failure paths.

## State and Persistence Behavior

Tracepoints do not persist driver state. When enabled, they copy packet bytes into per-event tracing buffers, so the original SPI buffers can be reused after the trace call.

## Dependencies and Integration Points

The file depends on Linux tracepoint infrastructure, `linux/types.h`, `linux/tracepoint.h`, and local `applespi.h`. It integrates with ftrace/perf tooling and the raw packet parsing in `applespi.c`.

## Risks and Edge Cases

Tracing full 256-byte packets can expose input data and increase overhead if enabled during high-rate touchpad activity. The trace include path is relative to the kernel trace generator and can break if the driver is moved. The IRQ tracepoint currently prints only a newline, so consumers rely on fields rather than formatted text.

## Test Signals

Build with `CONFIG_TRACEPOINTS`, enable each applespi event under tracingfs, verify packet lengths and hex dumps, and confirm trace generation for bad CRC and GPE notification paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/applespi_trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/atakbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/atakbd.c

## Purpose

`atakbd.c` is the Atari m68k keyboard input-layer driver. Low-level ACIA protocol handling is done by Atari architecture code; this file maps Atari scancodes to Linux keycodes and reports key events through one `input_dev`.

## Important APIs, Types, and Functions

- `atakbd_keycode[]` is the static American-layout scancode-to-keycode table.
- `atakbd_interrupt()` is installed into `atari_input_keyboard_interrupt_hook` and reports key press/release events.
- `atakbd_init()` validates Atari hardware, initializes the architecture keyboard core, allocates/registers the input device, fills key capabilities, and installs the hook.
- `atakbd_exit()` removes the hook and unregisters the input device.

## Control Flow

Module init runs only on Atari systems with ST MFP hardware. After `atari_keyb_init()` succeeds, the input device is registered and the architecture keyboard interrupt path calls `atakbd_interrupt(scancode, down)`. The callback ignores mouse-like high scancodes and reports mapped key state plus `input_sync()` for normal keyboard scancodes.

## State and Persistence Behavior

The file has a global `atakbd_dev` pointer and a static mutable keycode table exposed to the input core. It does not debounce or persist key state itself; press/release state comes from the architecture keyboard layer.

## Dependencies and Integration Points

It depends on Atari-specific headers and symbols (`MACH_IS_ATARI`, `ATARIHW_PRESENT`, `atari_keyb_init`, `atari_input_keyboard_interrupt_hook`) plus Linux input core. It is tightly coupled to m68k Atari platform code rather than generic platform discovery.

## Risks and Edge Cases

Scancode `0` or unmapped table entries can report `KEY_RESERVED` if delivered. High scancodes are logged as unhandled and may include mouse data from the shared ACIA path. The global hook/device design assumes only one Atari keyboard and careful unload ordering.

## Test Signals

Boot/module-load on Atari hardware or emulator, keymap coverage including keypad/arrows/help/undo, repeated press/release delivery, high-scancode logging, unload/reload hook cleanup, and build coverage for m68k Atari configs are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/atakbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/atkbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/atkbd.c

## Purpose

`atkbd.c` is the core AT and PS/2 keyboard serio driver. It supports translated and raw Set 2, Set 3, one-way input-only variants, RS232 PS/2 converters, LEDs, repeat rate programming, scancode/keycode maps, platform quirks, sysfs reconfiguration, Vivaldi function-row metadata, and input event generation.

## Important APIs, Types, and Functions

- `struct atkbd` stores `ps2dev`, input device, keymap, force-release mask, protocol set, translated/write/extra/scroll/softraw/softrepeat flags, interrupt parser state, delayed event work, mutex, and Vivaldi metadata.
- Key tables include `atkbd_set2_keycode`, `atkbd_set3_keycode`, and `atkbd_unxlate_table`; special pseudo-keycodes implement scroll-wheel emulation.
- Receive path functions are `atkbd_pre_receive_byte()`, `atkbd_receive_byte()`, `atkbd_compat_scancode()`, `atkbd_need_xlate()`, and `atkbd_calculate_xl_bit()`.
- Hardware command helpers include `atkbd_probe()`, `atkbd_select_set()`, `atkbd_reset_state()`, `atkbd_activate()`, `atkbd_deactivate()`, `atkbd_set_leds()`, and `atkbd_set_repeat_rate()`.
- `atkbd_connect()`, `atkbd_reconnect()`, `atkbd_disconnect()`, and `atkbd_cleanup()` implement the serio lifecycle.
- Sysfs handlers adjust `extra`, `force_release`, `scroll`, `set`, `softrepeat`, and `softraw`; DMI callbacks install forced-release and scancode quirks.

## Control Flow

The serio core routes matching i8042/translated/RS232 ports to `atkbd_connect()`. Connect allocates state, opens the serio port, probes the keyboard ID when writes are possible, selects the scancode set, resets LEDs/repeat, parses firmware keymap/function-row properties, builds the input device, enables receive processing, activates the keyboard, and registers input. Incoming bytes pass through `ps2_interrupt` into the pre-receive and receive callbacks. The receive state machine handles prefixes, release markers, ACK/NAK/BAT/error bytes, translated-mode high-bit handling, force-release quirks, scroll pseudo-events, and normal `EV_KEY`/`MSC_SCAN` reporting. LED and repeat input events are deferred to delayed work because PS/2 commands cannot safely run from interrupt context. Sysfs changes disable receive, rebuild and swap input devices when capabilities change, then re-enable receive.

## State and Persistence Behavior

Per-keyboard state persists in `struct atkbd`; interrupt-only fields track multi-byte scancodes (`emul`, `release`, `xl_bit`), resend status, last code/time for repeat workaround, and error count. User-visible mutable state includes the keymap, force-release bitmap, sysfs feature flags, and function-row physmap. Module parameters set defaults. DMI quirk globals persist for all subsequently connected keyboards. Reconnect resets parser state and reprograms hardware LEDs/repeat.

## Dependencies and Integration Points

The driver integrates with serio, libps2 command handling, input core, DMI, firmware properties (`linux,keymap`, `function-row-physmap`), Vivaldi function-row helpers, workqueues, mutexes, and architecture/platform i8042 behavior. It exposes a serio driver named `atkbd` with sysfs attribute groups.

## Risks and Edge Cases

PS/2 devices and controllers vary widely: GETID, RESET_DIS, scancode set switching, extra LED commands, and translated mode can misbehave on specific laptops. Parser state can be confused by missing bytes, frame/parity errors, direct hardware access producing spurious ACK/NAK, or reconnect during multi-byte sequences. Sysfs reconfiguration swaps input devices and must avoid races with input events and delayed work. Forced-release quirks can mask real long-press behavior if applied incorrectly.

## Test Signals

Test translated and raw Set 2, Set 3, input-only ports, reconnect/resume, LED and repeat programming, sysfs toggles, keymap firmware overrides, DMI force-release quirks, OQO scancode fixup, spurious ACK/NAK/error counters, BAT-triggered reconnect, scroll emulation, softrepeat/softraw combinations, and unplug/remove while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/atkbd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/bcm-keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/bcm-keypad.c

## Purpose

`bcm-keypad.c` drives Broadcom memory-mapped keypad matrix hardware. It programs row/column scan dimensions, debounce filters, edge interrupts, pull mode, optional clocking, and reports matrix key changes through the input subsystem.

## Important APIs, Types, and Functions

- Register constants describe KPCR, KPIOR, KPEMR, status, mask, clear, and ISR offsets.
- `struct bcm_kp` stores MMIO base, IRQ, optional clock, input device, previous status words, dimensions, and precomputed register values.
- `bcm_kp_matrix_key_parse_dt()` parses matrix keypad properties and Broadcom-specific debounce/output/pull properties into register values.
- `bcm_kp_start()` and `bcm_kp_stop()` enable/disable clock, interrupts, edge modes, and the hardware block.
- `bcm_kp_isr_thread()` reads both status registers, reports changed keys, and syncs input.

## Control Flow

Probe allocates state/input, parses device-tree matrix and Broadcom properties, builds the keymap, maps registers, configures the optional `peri_clk`, stops the hardware into a known state, requests a threaded IRQ, and registers input. Input open starts hardware; close stops it. The IRQ thread clears interrupt status, diffs current status against `last_state`, converts changed bits to row/column scan codes, reports key state adjusted for pull mode, then calls `input_sync()`.

## State and Persistence Behavior

The driver persists register configuration in `struct bcm_kp`, keeps `last_state[2]` for edge-to-state conversion, and relies on input open/close to control clock and hardware enable. No nonvolatile state is used.

## Dependencies and Integration Points

It depends on platform bus, OF, matrix keypad helpers, optional common clock framework, MMIO accessors, threaded IRQs, and Linux input. Device-tree properties include matrix row/column/keymap data, `autorepeat`, `status-debounce-filter-period`, `col-debounce-filter-period`, `row-output-enabled`, `pull-up-enabled`, and optional `clock-frequency`.

## Risks and Edge Cases

`bcm_kp_start()` assigns `last_state[0]` from both SSR0 and SSR1, leaving `last_state[1]` apparently uninitialized for the second status register. Invalid row/column counts or debounce values can produce bad register programming. Pull-up inversion must match board wiring. Clock rate rounding failures and shared hardware state across open/close are important failure points.

## Test Signals

Exercise row/column sizes up to 8x8, both pull modes, row-output vs column-output wiring, debounce bounds, optional/no clock configurations, input open/close cycles, IRQs from SSR0 and SSR1, autorepeat property, and keymap correctness for every matrix position.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/bcm-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cap11xx.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/cap11xx.c

## Purpose

`cap11xx.c` is an I2C input and optional LED driver for Microchip CAP11xx capacitive touch sensors. It verifies chip identity, configures sensor thresholds/gain/sensitivity/signal guards from device tree, reports touch channels as keys, and exposes supported LED outputs through the LED class.

## Important APIs, Types, and Functions

- Register definitions and `cap11xx_regmap_config` describe the 8-bit regmap, defaults, and volatile registers.
- `struct cap11xx_priv` holds regmap, device/input, hardware model, LED descriptors, configuration arrays, and flexible keycode storage.
- `struct cap11xx_hw_model` captures product ID, channel count, LED count, and feature flags for CAP1106/CAP1126/CAP1188/CAP1203/CAP1206/CAP1293/CAP1298.
- `cap11xx_init_keys()` validates and writes DT configuration and keycodes.
- `cap11xx_thread_func()` clears the interrupt, reads sensor state, reports each key, and syncs input.
- `cap11xx_set_sleep()`, input open/close, and `cap11xx_init_leds()` control power and LED outputs.

## Control Flow

Probe gets match data, allocates per-channel state, initializes I2C regmap, checks product/manufacturer/revision registers, applies DT configuration, allocates input, sets key capabilities and IDs, initializes optional LEDs, puts the chip into deep sleep when no LEDs require it awake, registers input, and requests a threaded IRQ. Input open wakes the sensor; close re-enters deep sleep unless LEDs are present. IRQ handling deasserts interrupt in main control, reads `SENSOR_INPUT`, emits key states, and syncs.

## State and Persistence Behavior

Configuration values are cached in `cap11xx_priv` and written to chip registers during probe. Regmap caching covers nonvolatile register defaults while volatile status/input registers are read live. LED state is held by hardware output control and LED class callbacks. Deep sleep is runtime state tied to input open/close, except disabled when LEDs must remain functional.

## Dependencies and Integration Points

The driver integrates with I2C, regmap, OF matching, input, optional LED class, GPIO consumer include support, bitfield helpers, and device-tree properties such as `linux,keycodes`, `autorepeat`, `microchip,sensor-gain`, `microchip,irq-active-high`, `microchip,sensitivity-delta-sense`, `microchip,input-threshold`, `microchip,calib-sensitivity`, and `microchip,signal-guard`.

## Risks and Edge Cases

DT arrays must match model channel counts and value constraints. `microchip,sensitivity-delta-sense` writes a complemented field-prep value, so this path deserves hardware verification. LED child `reg` values must be within model LED count. If IRQ polarity is wrong or the interrupt is not deasserted before status read, reports may be stale. Deep sleep is skipped when LEDs exist, increasing power consumption.

## Test Signals

Test each supported product ID, invalid manufacturer/product detection, all DT property bounds, default and custom keycodes, autorepeat, IRQ press/release reporting, LED registration and brightness, deep sleep on open/close, LED-present sleep behavior, and regmap error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cap11xx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/charlieplex_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/charlieplex_keypad.c

## Purpose

`charlieplex_keypad.c` is a GPIO-polled charlieplex keypad driver. It scans shared GPIO lines by driving one line high at a time, reading the remaining lines, debouncing the detected matrix code, and reporting one active key at a time.

## Important APIs, Types, and Functions

- `struct charlieplex_keypad` stores input device, GPIO array, line count, settling time, debounce threshold/count, current code, and candidate code.
- `charlieplex_keypad_scan_line()` drives one output line, waits optional settling time, reads all lines, restores input mode, and returns a matrix scan code.
- `charlieplex_keypad_check_switch_change()` and `charlieplex_keypad_report_key()` implement debounce and release/press reporting.
- `charlieplex_keypad_probe()` parses polling/debounce/settling properties, builds a square keymap, sets polling, and registers input.

## Control Flow

Probe requires a nonzero `poll-interval`, defaults debounce to 5 ms, obtains `line` GPIOs as inputs, assigns consumer names, builds a keymap with `nlines` rows and columns, enables optional autorepeat, installs an input polling callback, and registers input. Each poll scans output lines until it finds an asserted input, then advances debounce state and emits release/press events once stable long enough.

## State and Persistence Behavior

The driver stores only volatile debounce and current-key state. GPIO directions change during each scan and are restored to input. It does not maintain persistent hardware configuration outside devm-managed GPIO descriptors.

## Dependencies and Integration Points

It integrates with platform/OF matching (`gpio-charlieplex-keypad`), GPIO descriptor arrays, matrix keypad keymap helpers, input polling, firmware properties, and optional `autorepeat`.

## Risks and Edge Cases

The scanner returns only the first detected asserted line pair, so simultaneous keys are not represented. `current_code` and `debounce_code` are initialized to `-1` while zero also means no key; report logic must avoid indexing negative codes. GPIO direction churn and settling time must match electrical characteristics. More than `MATRIX_MAX_ROWS` lines is rejected.

## Test Signals

Validate all line pairs, no-key transitions, debounce thresholds, simultaneous key behavior, zero and nonzero settling times, GPIO read errors, invalid/missing `poll-interval`, autorepeat, and keymap indexing for square matrices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/charlieplex_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/clps711x-keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/clps711x-keypad.c

## Purpose

`clps711x-keypad.c` drives the Cirrus Logic EP7209/CLPS711X keypad matrix using a syscon keyboard-scan register for columns and GPIOs for rows. It is a polled input driver for an 8-column matrix.

## Important APIs, Types, and Functions

- `struct clps711x_keypad_data` holds the syscon regmap, row count, row shift, and per-row GPIO state.
- `struct clps711x_gpio_data` stores a row GPIO descriptor and last column bitmap.
- `clps711x_keypad_poll()` asserts each column through `SYSCON1_KBDSCAN`, double-reads row GPIOs until stable, reports changed key states, and syncs input.
- `clps711x_keypad_probe()` obtains syscon/row GPIOs, parses poll interval, builds keymap, configures polling, and registers input.

## Control Flow

Probe looks up the `syscon` phandle, counts `row` GPIOs, allocates row state, gets each row GPIO as input, reads `poll-interval`, creates an input device, builds a matrix keymap with eight columns, sets all columns low, installs polling, and registers input. Polling iterates columns, asserts one scan code in syscon, reads every row twice for stability, compares against `last_state`, emits `MSC_SCAN` and key events for changes, deasserts columns, then syncs if anything changed.

## State and Persistence Behavior

Per-row `last_state` bitmaps persist across polls. Hardware column drive state is transient and reset low after every column. No nonvolatile state is used.

## Dependencies and Integration Points

The driver depends on platform/OF (`cirrus,ep7209-keypad`), syscon regmap, CLPS711X syscon definitions, GPIO descriptors, matrix keypad helpers, input polling, and `poll-interval`/`autorepeat` properties.

## Risks and Edge Cases

The double-read loop waits until two consecutive GPIO reads match; noisy hardware could spin for a long time, though `cond_resched()` mitigates scheduler impact. Missing or invalid `syscon`, row GPIOs, or poll interval prevents probe. Keycode zero entries suppress key reports but still track state changes.

## Test Signals

Test row counts, all eight columns, noisy GPIO simulation, poll interval parsing, autorepeat, keymap holes, syscon write failures, and repeated open/close/poll cycles under CPU load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/clps711x-keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cros_ec_keyb.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/cros_ec_keyb.c

## Purpose

`cros_ec_keyb.c` is the ChromeOS Embedded Controller keyboard driver. It consumes EC MKBP events for matrix keys, non-matrix buttons, switches, and sysrq, performs host-side deghosting and Fn-layer mapping, and registers one or two input devices.

## Important APIs, Types, and Functions

- `struct cros_ec_keyb` stores matrix geometry, ghost filter state, old matrix state, EC pointer, matrix and button/switch input devices, notifier, Vivaldi physmap, and Fn-layer state.
- `cros_ec_keyb_work()` is the EC event notifier for matrix, sysrq, button, and switch events.
- `cros_ec_keyb_process()` diffs matrix columns, applies optional ghost filtering, and emits changed keys.
- `cros_ec_keyb_process_key_fn_map()` implements a second keymap layer when `KEY_FN` and Fn mappings are present.
- `cros_ec_keyb_info()`, `cros_ec_keyb_register_bs()`, and `cros_ec_keyb_query_switches()` query EC-supported/current buttons and switches.
- `cros_ec_keyb_register_matrix()` parses matrix properties, builds normal plus Fn-layer keymap rows, computes valid keys, parses Vivaldi metadata, and registers input.

## Control Flow

Probe waits for a fully registered parent EC, allocates state, optionally registers the matrix keyboard, registers supported non-matrix buttons/switches, then registers a blocking notifier on the EC event chain and enables wakeup. Matrix events wake the device, validate event length against column count, then diff and report changed keys. Button/switch events are translated from EC bitmaps to `EV_KEY`/`EV_SW`. Sysrq events are forwarded to `handle_sysrq()`. Resume requeries switch state because switch events may be lost during suspend.

## State and Persistence Behavior

`old_kb_state` persists previous EC matrix bytes for edge detection. `valid_keys` persists the subset used by ghost filtering. Fn state tracks whether Fn is down and whether it was used in a combo so standalone Fn can be emitted only on release. Button/switch supported masks are not stored after registration; current switch state is queried on resume.

## Dependencies and Integration Points

The driver integrates with ChromeOS EC command/protocol APIs, EC event notifier chain, input core, matrix keypad helpers, Vivaldi function-row helpers, sysrq, ACPI match `GOOG0007`, OF compatibles `google,cros-ec-keyb` and `google,cros-ec-keyb-switches`, and firmware properties such as `keypad,num-rows`, `keypad,num-columns`, `linux,keymap`, `google,needs-ghost-filter`, and `function-row-physmap`.

## Risks and Edge Cases

Matrix columns are limited by EC protocol to 18. The ghost filter drops an entire matrix state when it detects ghosting, which can delay unrelated key changes. Fn-layer release logic depends on current input keybits, so keymap changes and dropped states must stay consistent. Buttons/switches-only ACPI/OF matches expect EC support and fail otherwise. Event-size mismatches are discarded.

## Test Signals

Test matrix events at valid and invalid lengths, ghosting combinations, Fn-only and Fn-combo behavior, runtime setkeycode changes, Vivaldi sysfs visibility, button/switch support masks, switch resume queries, sysrq forwarding, wakeup behavior during suspend, and deferred probe when the EC is not registered.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cros_ec_keyb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cypress-sf.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/cypress-sf.c

## Purpose

`cypress-sf.c` is an I2C driver for Cypress StreetFighter touchkey controllers. It powers the controller with two regulators, reads a button status register on IRQ, and reports configured keycodes.

## Important APIs, Types, and Functions

- `struct cypress_sf_data` stores the I2C client, input device, `vdd`/`avdd` regulators, keycode array, last keystate bitmap, and key count.
- `cypress_sf_irq_handler()` reads `CYPRESS_SF_REG_BUTTON_STATUS`, diffs against previous state, reports changed keys, syncs, and stores new state.
- `cypress_sf_probe()` reads optional `linux,keycodes`, applies defaults, enables regulators, registers input, and requests a threaded IRQ.
- Suspend/resume disable IRQ around regulator power-down/up.

## Control Flow

Probe allocates state, gets regulators, determines key count from `linux,keycodes` or defaults to two, reads keycodes or uses Back/Menu defaults, enables supplies with a devm cleanup action, registers input capabilities, then requests an IRQ thread. On interrupt, the thread reads one byte over SMBus, diffs the configured number of key bits, reports only changed states, and syncs.

## State and Persistence Behavior

`keystates` persists the last status byte for change detection. Regulators remain enabled while active and are disabled during suspend and devm cleanup. No nonvolatile state is used.

## Dependencies and Integration Points

It depends on I2C SMBus byte reads, regulator bulk APIs, input core, threaded IRQs, PM sleep ops, and OF compatible `cypress,sf3155`. The main firmware contract is `linux,keycodes`.

## Risks and Edge Cases

The status register is one byte, so more than eight configured keys would not be representable despite the dynamic key count. If reading keycodes fails for a count greater than two, only the first two defaults are initialized. IRQ is disabled before regulator shutdown, but wakeup behavior is not implemented. A negative SMBus read returns `IRQ_NONE`, which may matter for shared IRQ diagnostics.

## Test Signals

Test default and custom keycodes, key counts from one to eight, SMBus read failures, regulator get/enable/disable failures, suspend/resume IRQ ordering, repeated interrupts with unchanged state, and OF/I2C matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/cypress-sf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/dlink-dir685-touchkeys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/dlink-dir685-touchkeys.c

## Purpose

`dlink-dir685-touchkeys.c` supports the D-Link DIR-685 router's I2C Cypress MCU touchkey board. It maps a fixed set of front-panel touch bits to Linux keycodes and sets keypad backlight brightness during probe.

## Important APIs, Types, and Functions

- `struct dir685_touchkeys` stores device/client/input pointers, current key bitmap, and seven keycodes.
- `dir685_tk_probe()` allocates/registers the fixed input device, sends a brightness command, validates IRQ presence, and requests a threaded IRQ.
- `dir685_tk_irq_thread()` reads six bytes from I2C, extracts the big-endian key bitmap from bytes 4-5, diffs state, reports changed keys, and syncs.

## Control Flow

Probe initializes keycodes for up/down/left/right/enter/WPS/reserved, registers the input device, attempts to set brightness to maximum with a two-byte I2C write, and installs the IRQ thread. On IRQ, a six-byte message is read; changed bits among the fixed key set produce press/release reports.

## State and Persistence Behavior

`cur_key` persists the last 16-bit controller bitmap. Backlight brightness is written once at probe and not tracked afterward. No suspend/resume or nonvolatile state is implemented.

## Dependencies and Integration Points

The driver uses I2C master send/recv, input core, threaded IRQs, bitops, and OF/I2C matching for `dlink,dir685-touchkeys` / `dir685tk`.

## Risks and Edge Cases

The protocol is board-specific and assumes six-byte reads and key bits in the last two bytes. Short reads are handled but no recovery is attempted. `KEY_RESERVED` is cleared after capability setup for the unused seventh key. Missing IRQ fails probe after input registration, though devm/input cleanup will unwind on probe failure.

## Test Signals

Test six-byte read parsing, each mapped touchkey, simultaneous bits, short/failed reads, brightness write failure warning, missing IRQ, OF/I2C matching, and repeated press/release transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/dlink-dir685-touchkeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/ep93xx_keypad.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/ep93xx_keypad.c

## Purpose

`ep93xx_keypad.c` drives the Cirrus EP93xx 8x8 matrix keypad controller. It configures hardware debounce/prescale, decodes one-key or two-key capture registers, reports key state, and supports clock gating plus wake IRQ setup.

## Important APIs, Types, and Functions

- Register constants describe `KEY_INIT`, `KEY_DIAG`, and `KEY_REG` fields.
- `struct ep93xx_keypad` stores input, clock, debounce, prescale, MMIO base, 64-key keymap, last two active keys, IRQ, and enabled flag.
- `ep93xx_keypad_irq_handler()` decodes capture status and reports transitions for up to two simultaneous keys.
- `ep93xx_keypad_config()`, open/close, suspend/resume, probe, and remove manage hardware configuration, clocking, input registration, and wake IRQ.

## Control Flow

Probe obtains IRQ/MMIO/clock, reads optional debounce and prescale properties, builds an 8x8 keymap, requests the IRQ, registers input, stores drvdata, enables wakeup, and registers the IRQ as a wake source. Input open configures registers and enables the clock; close disables the clock. IRQ handling reads capture state and compares captured keys to `key1`/`key2` to emit releases for keys no longer present and presses for current keys.

## State and Persistence Behavior

The driver persists the keymap, last active keycodes, debounce/prescale values, and enabled flag in `struct ep93xx_keypad`. Clock state follows input open/close and PM. Wake IRQ registration persists until remove.

## Dependencies and Integration Points

It depends on platform/OF compatible `cirrus,ep9307-keypad`, MMIO, common clock framework, matrix keypad helpers, input core, PM sleep ops, and `dev_pm_set_wake_irq()`.

## Risks and Edge Cases

The hardware reports only up to two keys; larger combinations cannot be represented. Keycode zero handling can produce redundant reports if capture registers contain unmapped positions. Suspend uses `clk_disable()` while close uses `clk_disable_unprepare()`, so clock prepare/enable balance relies on open/PM ordering. Wake IRQ setup failures are warnings, not fatal.

## Test Signals

Test one-key, two-key, and no-key transitions; key replacement releases; debounce/prescale values; clock open/close/suspend/resume balance; wake from keypad IRQ; keymap holes; and probe failures for missing IRQ/MMIO/clock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/ep93xx_keypad.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/goldfish_events.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/goldfish_events.c

## Purpose

`goldfish_events.c` is the Goldfish emulator event-device driver. It imports an emulator-provided input device name, capability bitmaps, and ABS parameters from MMIO pages, then forwards triples of input events read from the device on IRQ.

## Important APIs, Types, and Functions

- Page/register constants define `REG_READ`, `REG_SET_PAGE`, `REG_LEN`, `REG_DATA`, `PAGE_NAME`, `PAGE_EVBITS`, and `PAGE_ABSDATA`.
- `struct event_dev` stores input device, IRQ, MMIO base, and flexible device name.
- `events_import_bits()` reads capability bitmaps from emulator pages into input bit arrays.
- `events_import_abs_params()` reads ABS min/max/fuzz/flat values.
- `events_interrupt()` reads type/code/value triples and emits `input_event()` plus sync.
- `events_probe()` maps MMIO, imports metadata/capabilities, requests IRQ, and registers input.

## Control Flow

Probe obtains IRQ and memory resource, maps 4 KiB, selects the name page to size/copy the device name, allocates input/state, imports capability pages for all major input event bitmaps, imports ABS params for enabled ABS codes, requests IRQ, and registers the input device. Each interrupt reads three consecutive MMIO words and forwards them directly to the input core.

## State and Persistence Behavior

The driver stores static imported capabilities and name in the input device. It does not track event state beyond what input core tracks. The emulator device controls all event values and page contents.

## Dependencies and Integration Points

It depends on platform bus, OF compatible `google,goldfish-events-keypad`, ACPI ID `GFSH0002`, MMIO raw access, IRQs, and Linux input. It is intended for Android/Goldfish virtual hardware.

## Risks and Edge Cases

MMIO-provided lengths are trusted enough to allocate/copy a name and import bitmap bytes; very large name lengths could inflate allocation. Events are forwarded without validating type/code against imported capabilities. Raw accessors assume emulator endian/order. Missing resources fail probe.

## Test Signals

Validate imported capabilities, ABS parameter ranges, name handling, IRQ event forwarding for key/rel/abs/sw/msc/led/snd/ff bits, malformed length pages, out-of-capability event triples, and OF/ACPI matching in emulator boots.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/goldfish_events.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys.c

## Purpose

`gpio_keys.c` is the interrupt-driven GPIO/IRQ button and switch driver. It supports GPIO-backed stateful keys, IRQ-only momentary keys, debounce, wakeup handling, optional separate wake IRQs, platform-data and firmware-node configuration, and sysfs disabling of eligible keys/switches.

## Important APIs, Types, and Functions

- `struct gpio_button_data` stores per-button platform data, input, GPIO, code pointer, debounce/release timers, work item, IRQ/wakeirq, wake trigger, lock, disabled/key/suspend flags, and debounce mode.
- `struct gpio_keys_drvdata` stores platform data, input device, disable mutex, keymap, and flexible button array.
- Sysfs helpers expose `keys`, `switches`, `disabled_keys`, and `disabled_switches`.
- `gpio_keys_setup_key()` configures GPIO/IRQ resources, debounce, wake triggers, input capabilities, cleanup actions, and interrupt handlers per button.
- `gpio_keys_gpio_isr()` handles GPIO-backed edge interrupts; `gpio_keys_irq_isr()` handles IRQ-only keys with synthetic release timers.
- PM helpers enable/disable wakeup and call platform enable/disable hooks.

## Control Flow

Probe obtains platform data or builds it from child firmware nodes, allocates state/input/keymap, loops over buttons to configure GPIOs or IRQ-only inputs, requests main and optional wake IRQs, registers input, and initializes device wakeup. Input open calls optional platform enable and reports current GPIO states; close calls optional disable. GPIO IRQs schedule debounce work/hrtimer, which reads the GPIO and emits current state. IRQ-only handlers emit press and either immediate or delayed release. Sysfs writes validate requested disabled codes and mask/unmask non-shared IRQs. Suspend either enables wake IRQ behavior or closes the input device; resume restores IRQs and reports current state.

## State and Persistence Behavior

Per-button state persists disabled status, key pressed state for IRQ-only buttons, debounce/release timers, software debounce mode, wake trigger type, and suspended flag. Driver-level keymap and platform data persist for the device lifetime. No nonvolatile state is used, but sysfs disabled masks persist until changed or driver removal.

## Dependencies and Integration Points

It integrates with platform bus, GPIO descriptor and legacy GPIO APIs, IRQ core, hrtimers/workqueues, input core, PM wakeup, OF/fwnode child properties, `linux/gpio_keys.h`, and `dt-bindings/input/gpio-keys.h`. It registers late via `late_initcall`.

## Risks and Edge Cases

Shared IRQ buttons cannot be disabled through sysfs. GPIO-backed wake trigger reconfiguration must be restored correctly on resume. IRQ-only buttons only support `EV_KEY` and synthesize releases, so debounce interval semantics differ from GPIO keys. Hrtimer debounce is used only for non-sleeping GPIOs. Platform enable/disable hooks and wake IRQ swapping can race with input open/close or suspend if ordering changes.

## Test Signals

Test GPIO and IRQ-only buttons, EV_KEY/EV_SW/EV_ABS types, debounce via hardware and software paths, sysfs disable/enable validation, shared IRQ behavior, wake-source and separate wakeirq suspend/resume, asserted/deasserted wake trigger actions, platform-data and fwnode parsing, initial state reporting, shutdown path, and remove with pending timers/work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys_polled.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys_polled.c

## Purpose

`gpio_keys_polled.c` is the polling variant of the GPIO keys driver for GPIO lines without usable interrupts. It reads button GPIOs at a configured interval, debounces them, and reports key, relative-axis, or absolute-axis events.

## Important APIs, Types, and Functions

- `struct gpio_keys_button_data` stores each GPIO descriptor, last state, debounce count, and threshold.
- `struct gpio_keys_polled_dev` stores input, device, platform data, seen-axis bitmaps, and per-button data.
- `gpio_keys_polled_get_devtree_pdata()` builds platform data from firmware child nodes.
- `gpio_keys_polled_poll()` handles debounce, reports events, resets unseen axes to zero, and syncs input.
- `gpio_keys_polled_probe()` parses platform/fwnode data, obtains GPIOs, sets capabilities, installs polling, registers input, and reports initial state.

## Control Flow

Probe requires `poll_interval`, allocates state/input, iterates configured buttons to reject wakeup requests, obtain GPIOs, derive debounce thresholds, set input capabilities and ABS ranges, installs the poll callback, registers the input device, and emits initial state. Each poll repeats previous state while debounce threshold is being reached; after that it reads GPIO state, reports changes or axis values, zeroes relative/absolute axes not seen in this poll, and syncs.

## State and Persistence Behavior

Per-button `last_state` and `count` persist across polls for debounce. `rel_axis_seen` and `abs_axis_seen` are transient per poll. Optional platform enable/disable hooks run on input open/close. No wake or nonvolatile state is supported.

## Dependencies and Integration Points

It uses platform bus, GPIO descriptor and legacy GPIO APIs, input polling, fwnode/OF compatible `gpio-keys-polled`, `linux/gpio_keys.h`, and properties such as `poll-interval`, `autorepeat`, `linux,code`, `linux,input-type`, `linux,input-value`, `debounce-interval`, and `label`.

## Risks and Edge Cases

Wakeup is explicitly unsupported and causes probe failure if requested. Missing `poll_interval` fails probe. Relative/absolute events are emitted only while active and reset to zero when not observed, so button value semantics must match the target input consumer. Debounce is poll-count based and can be coarse at long intervals.

## Test Signals

Test key, relative, and absolute button definitions; debounce intervals versus poll intervals; initial state reporting; missing/invalid GPIOs; wakeup rejection; platform enable/disable hooks; axis reset behavior; autorepeat; and fwnode plus legacy platform-data paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/gpio_keys_polled.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hil_kbd.c -->
# sources/distributed-fs/ceph-client/drivers/input/keyboard/hil_kbd.c

## Purpose

`hil_kbd.c` is a serio driver for HP-HIL keyboards, mice, tablets, and touchscreens. It queries HIL device records, configures an input device as either keyboard or pointer, parses packetized HIL bus data, and reports Linux input events.

## Important APIs, Types, and Functions

- `struct hil_dev` stores input/serio pointers, packet assembly buffer/index, raw ID/RSC/EXD/RNM records, command completion, pointer flag, axis/button metadata, and button map.
- `hil_dev_interrupt()` assembles four-byte `hil_packet` words from serio bytes and dispatches complete command responses or poll events.
- `hil_dev_handle_command_response()` stores IDD/RSC/EXD/RNM records and completes the waiting command.
- `hil_dev_handle_kbd_events()` decodes HIL keyboard chartypes and key sets.
- `hil_dev_handle_ptr_events()` decodes relative/absolute axes and buttons.
- `hil_dev_connect()` queries device records, selects keyboard or pointer setup, optionally enables keyboard autorepeat, and registers input.

## Control Flow

Connect allocates state/input, opens serio, sends four-byte HIL commands for IDD, RSC, RNM, and EXD, waiting for completions filled by interrupt parsing. Based on the DID type, it rejects unsupported combo devices, configures keyboard keybits/keymap or pointer axes/buttons, fills input IDs, enables HIL keyboard autorepeat when appropriate, and registers input. Incoming serio bytes are packed into HIL packets; command records complete setup waits, while poll records dispatch to keyboard or pointer event handlers and then reset packet assembly.

## State and Persistence Behavior

The packet assembly index and buffered packets persist between bytes. Device information records persist after connect and drive event decoding. Pointer button maps and axis capabilities persist for the device lifetime. Command completions synchronize setup commands with interrupt responses.

## Dependencies and Integration Points

It depends on the serio HIL MLC transport, `linux/hil.h` protocol definitions/keycode maps/locales, input core, completions, PCI vendor IDs for HP, and serio modaliases for HIL keyboard/mouse devices.

## Risks and Edge Cases

Malformed packets reset assembly and complete waiters defensively. Setup waits are killable but have no explicit timeout in this file, so missing responses can block until interrupted. Combo keyboard/pointer devices are unsupported. Axis/button parsing depends on IDD metadata and HIL packet count fields. Some optional tablet auto-adjust/mouse simulation behavior is compile-time disabled.

## Test Signals

Test keyboard chartypes Set1/Set2/Set3/ASCII/binary, pointer relative and absolute devices, multi-axis and alternate-axis packets, button maps including mouse middle/right swap, malformed packets, missing command responses, unsupported combo devices, RNM naming, disconnect during input activity, and serio modalias matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/keyboard/hil_kbd.c -->
