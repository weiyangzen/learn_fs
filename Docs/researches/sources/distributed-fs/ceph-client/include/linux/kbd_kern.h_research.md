# sources/distributed-fs/ceph-client/include/linux/kbd_kern.h

## Purpose
Defines kernel-internal virtual terminal keyboard state and helpers for lock keys, LED state, keyboard mode, and console keyboard callbacks.

## Important APIs, Types, And Functions
`struct kbd_struct` stores lock state, sticky lock state, LED mode and flags, keyboard mode, and mode flags. Constants define virtual console lock bits, LED flags, modes such as `VC_XLATE`, `VC_RAW`, `VC_UNICODE`, and mode flags such as repeat and CRLF. APIs include `kbd_init()`, `setledstate()`, `set_console()`, `schedule_console_callback()`, `vt_set_leds_compute_shiftstate()`, and inline bit helpers for mode/LED/lock manipulation.

## Control Flow
Keyboard event processing reads and mutates `kbd_struct` according to keycodes, keymaps, ioctls, and console changes. Inline helpers set, clear, toggle, and test bitfields. LED updates may use `kbd_ledfunc`.

## State And Persistence
State is per-virtual-console keyboard mode and LED/lock configuration plus global function key and keymap tables. It persists while the console exists and changes through keyboard events or ioctls.

## Dependencies And Integration Points
Depends on TTY, interrupt, keyboard, and console infrastructure. Integrates with VT, keymaps, KDGETLED/KDSETLED ioctls, and hardware LED callbacks.

## Risks
The internal LED order must match externally visible `kd.h` LED constants. Bitfield width limits require valid flag values. Console callbacks and interrupt-context keyboard events require proper locking in implementation code.

## Test Signals
Signals include VT keyboard mode tests, raw/mediumraw/unicode translation, lock and sticky lock toggles, LED ioctls, console switching, function-key maps, and keyboard interrupt tests.
