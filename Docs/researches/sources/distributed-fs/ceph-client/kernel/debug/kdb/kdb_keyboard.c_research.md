# sources/distributed-fs/ceph-client/kernel/debug/kdb/kdb_keyboard.c

## Purpose
This file provides the i8042/PC keyboard polling backend for KDB. It reads raw keyboard controller registers while the debugger is active, translates scancodes into printable characters or KDB line-editing control codes, and cleans up ENTER release codes before returning control to the normal kernel input path.

## Important APIs, Types, And Functions
`kdb_get_kbd_char()` is the exported poll function. It uses `KBD_STATUS_REG`, `KBD_DATA_REG`, `KBD_STAT_OBF`, and `KBD_STAT_MOUSE_OBF`, tracks static shift/caps/ctrl state, reads `plain_map` and `key_maps`, and returns ASCII/control values. `kdb_kbd_cleanup_state()` drains pending ENTER/KP ENTER break sequences after KDB exits.

## Control Flow
The poller first refuses operation when i8042 or VT console use is disabled, or when the controller appears absent. It returns `-1` when no output byte exists, when the byte is mouse input, or when it only updates modifier state. It ignores key releases except for shift/control bookkeeping and ENTER cleanup. Printable keys come from the plain, shifted, or control keymap, while tab/delete/home/end/arrows are mapped to KDB control characters consumed by `kdb_read()`.

## State, Persistence, And Dependencies
Persistent in-memory state includes `kbd_exists`, `kbd_last_ret`, and static modifier variables in `kdb_get_kbd_char()`. `kbd_last_ret` tells cleanup whether KDB processed ENTER and should absorb the corresponding break code. Dependencies are low-level port I/O, Linux keyboard maps, KDB flags `NO_I8042` and `NO_VT_CONSOLE`, and optional LED toggling under `KDB_BLINK_LED`.

## Integration Points
When enabled, this function is registered in KDB's poll function chain and feeds `kdb_getchar()` in `kdb_io.c`. `kdb_main_loop()` calls `kdb_kbd_cleanup_state()` on exit through the private header abstraction.

## Risks
The cleanup loop spins until it sees the expected ENTER break scancode; unusual controller behavior or mashed-key cases can prolong debugger exit. Only a subset of keys is accepted, nonprintables are dropped, and the translation assumes PC set-1 style scancodes. Mouse bytes must be skipped correctly or they can corrupt KDB input.

## Test Signals
Use direct keyboard debugger entry, printable keys, shift/caps/control combinations, arrows/home/end/delete/tab/backspace, repeated ENTER, keypad ENTER, mouse activity during KDB, and exits after `go` to confirm no ENTER break leaks into the normal console.
