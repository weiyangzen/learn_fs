## sources/distributed-fs/ceph-client/drivers/input/keyboard/jornada680_kbd.c

Purpose: HP Jornada 620/660/680/690 platform keyboard driver. It polls SuperH GPIO/control registers to scan an 18-byte keyboard matrix and reports a fixed Jornada keymap.

Important APIs/types/functions: `struct jornadakbd` stores input, keymap, and old/new scan buffers. `jornada_scan_keyb()` drives PD/PE scan lines through raw hardware addresses and reads row bytes from PC/PF plus extra PG/PH bytes. `jornada_parse_kbd()` diffs old/new buffers and emits `MSC_SCAN` plus key events. `jornadakbd680_poll()` is the input polling callback.

Control flow: probe creates input, copies `jornada_scancodes`, sets polling with a 50 ms interval, registers key and MSC capabilities, and registers input. Runtime is entirely poll driven: each poll scans all matrix lines, compares with prior state, reports changed bits as active-low key states, syncs if needed, then saves the new scan.

State/dependencies/integration: state persists only in scan buffers and keymap. Dependencies are platform-device binding, input polling, architecture raw I/O helpers, and hard-coded SH register addresses.

Risks and test signals: hard-coded register addresses and timing make this driver platform-specific and fragile. The parser can report keycode 0 entries if unused positions change. Test boot on supported Jornada variants, active-low release handling, polling interval behavior, and no event spam when matrix is stable.
