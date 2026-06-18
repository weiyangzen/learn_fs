# sources/distributed-fs/ceph-client/include/uapi/linux/kd.h

## Purpose
`kd.h` exports Linux virtual-console keyboard/display ioctl numbers, font/palette structures, keymap structures, diacritic tables, keyboard modes, LED flags, and console font operations.

## Important APIs, Types, and Functions
The header defines ioctls for fonts (`GIO_FONT`, `PIO_FONT`, `GIO_FONTX`, `PIO_FONTX`, `KDFONTOP`), palette, sound/tone, LEDs, keyboard type/mode/meta/LED flags, keymap entries, function-key strings, diacritics, keycode translation, keyboard repeat, display mode, and low-level IO permissions. Structures include `consolefontdesc`, `unipair`, `unimapdesc`, `unimapinit`, `kbentry`, `kbsentry`, `kbdiacr`, `kbdiacrs`, `kbdiacruc`, `kbdiacrsuc`, `kbkeycode`, `kbd_repeat`, `console_font_op`, and `console_font`.

## Control Flow
Console tools issue ioctls on virtual terminals to query or mutate keyboard translation, LEDs, fonts, palette, display mode, and repeat behavior. The tty/vt subsystem applies changes to console state and hardware-facing display paths.

## State and Persistence
Most state is per virtual console or global vt keyboard/display state and persists until changed, console reset, module/device reset, or reboot. Font and mapping tables are mutable kernel memory.

## Dependencies and Integration Points
It includes `<linux/types.h>` and `<linux/compiler.h>`. Integration points include tty/vt, loadkeys, setfont, console display drivers, keyboard input, and legacy terminal tooling.

## Risks and Test Signals
Tests should cover ioctl numbers, privilege checks for dangerous IO operations, font buffer sizing, Unicode map limits, keyboard mode transitions, LED flag versus light state, diacritic table bounds, and 32/64-bit pointer fields in font operations.
