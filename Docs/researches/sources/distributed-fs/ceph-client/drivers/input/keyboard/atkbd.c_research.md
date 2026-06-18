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
