# sources/distributed-fs/ceph-client/drivers/tty/vt/keyboard.c

## Purpose
`keyboard.c` is the virtual terminal keyboard input engine. It registers the input-layer keyboard handler, translates input key events through console keymaps, emits bytes or UTF-8 to the active VC tty, manages keyboard modes and LEDs, implements dead-key/diacritic composition and Braille chords, exposes keyboard ioctls used by `vt_ioctl.c`, and supports notifier hooks for keyboard events.

## Important APIs, Types, And Functions
- Global per-console state lives in `kbd_table[MAX_NR_CONSOLES]`; `kbd` points at the active console's entry while processing.
- Handler dispatch is table-driven through `k_handler[]` for key symbol types and `fn_handler[]` for special VT functions.
- Public registration and lifecycle APIs include `register_keyboard_notifier()`, `unregister_keyboard_notifier()`, and `kbd_init()`.
- Input integration is through `kbd_handler` with `.event = kbd_event`, `.match = kbd_match`, `.connect = kbd_connect`, `.disconnect = kbd_disconnect`, and `.start = kbd_start`.
- Core event flow is `kbd_event()` -> `kbd_keycode()` -> keymap lookup/notifiers -> typed handler such as `k_unicode()`, `k_fn()`, `k_shift()`, `k_pad()`, `k_cur()`, or `k_csi()`.
- Ioctl helpers include `vt_do_diacrit()`, `vt_do_kdskbmode()`, `vt_do_kdskbmeta()`, `vt_do_kbkeycode_ioctl()`, `vt_do_kdsk_ioctl()`, `vt_do_kdgkb_ioctl()`, `vt_do_kdskled()`, `vt_do_kdgkbmode()`, and `vt_do_kdgkbmeta()`.
- VT integration helpers include `vt_reset_unicode()`, `vt_get_shift_state()`, `vt_reset_keyboard()`, `vt_get_kbd_mode_bit()`, `vt_set_kbd_mode_bit()`, `vt_clr_kbd_mode_bit()`, `vt_kbd_con_start()`, and `vt_kbd_con_stop()`.

## Control Flow And State
`kbd_init()` initializes each console with default LED flags, lock state, repeat/meta flags, and `VC_UNICODE` or `VC_XLATE` based on `default_utf8`, then registers the input handler and enables the LED tasklet. For each input event, `kbd_event()` takes `kbd_event_lock`, forwards raw MSC events to `kbd_rawcode()` when appropriate, and forwards key events to `kbd_keycode()`. After processing it schedules LED updates, pokes the blanked console, and schedules the VT console callback.

`kbd_keycode()` selects the foreground VC, handles raw and medium-raw modes, updates the global `key_down` bitmap, suppresses repeats when configured or when tty buffers are backed up, computes the effective shift/lock map, calls keyboard notifiers, and dispatches to Unicode or typed handlers. Cursor and CSI keys include modifier encoding through `csi_modifier_param()`. Dead keys store `diacr`; the next character passes through `handle_diacr()` and the global `accent_table`. Braille keys collect dot patterns and either emit Unicode Braille or act as dead chords.

## State And Persistence Behavior
State is runtime-only kernel state. Per-console `kbd_struct` entries hold mode flags, LED flags, lock/slock state, and keyboard mode. Global transient state includes `key_down`, `shift_down`, `shift_state`, `diacr`, `dead_key_next`, numeric keypad character assembly, repeat flag `rep`, LED state/cache, function-key string table contents, and the global diacritic table. Ioctls can mutate keymaps, function strings, keyboard mode, meta behavior, LEDs, and diacritics until reset or module/kernel lifetime ends.

## Dependencies And Integration Points
This file depends on the input subsystem, tty flip buffers, VT console state from `vt.c`, keymap data from `defkeymap`/`consolemap`, LED triggers or EV_LED injection, timers, tasklets, workqueues, notifiers, and user-copy helpers. It integrates with `vt.c` through mode-bit helpers, console switching, scrollback, blanking, SAK work, and `default_utf8`. It integrates with `vt_ioctl.c` through exported ioctl helpers and with `selection.c` indirectly through shift/mouse reporting.

## Risks And Edge Cases
Locking is split across `kbd_event_lock`, `led_lock`, and `func_buf_lock`; comments still call out locking review needs for LED updates. Raw mode emulation is architecture-specific and may warn for unrepresentable keycodes. Keymap mutation must validate type/value bounds and SAK permissions carefully. Function string replacement uses mixed static/kmalloc ownership tracked by a bitmap. `vt_get_shift_state()` and mode-bit reads are intentionally transient and not fully synchronized. Unicode mode is required for Braille patterns; otherwise input is rejected with a warning.

## Test Signals
Useful tests include input-handler registration, console typing in `K_XLATE`, `K_UNICODE`, `K_RAW`, `K_MEDIUMRAW`, and `K_OFF`, LED propagation on lock keys and tty stop/start, keymap get/set ioctls including invalid bounds, function-key string get/set, dead-key composition through both legacy and Unicode diacritic ioctls, modifier CSI sequences for cursor/function keys, Alt-numpad decimal/hex input, Braille chord input, VT switching hotkeys, SysRq/SAK behavior, and suspend of repeat under tty backlog.
