# sources/distributed-fs/ceph-client/include/uapi/linux/keyboard.h

## Purpose
`keyboard.h` defines virtual-console key symbol encoding, key types, modifier groups, function-key values, keypad/dead/accent/cursor/lock/braille/CSI symbols, and related table limits.

## Important APIs, Types, and Functions
`K(t,v)` packs key type and value; `KTYP` and `KVAL` unpack them. Modifier groups include shift, altgr, ctrl, alt, left/right variants, and caps shift. Key types include latin, function, special, keypad, dead key, console switch, cursor, shift, meta, ASCII, lock, letter, sticky lock, second dead-key set, braille, and CSI. The file enumerates `K_F1` through `K_F245` plus special actions, keypad keys, dead diacritics, cursor keys, lock symbols, braille dots, CSI escape keys, and table limits such as `NR_KEYS`, `MAX_NR_KEYMAPS`, `MAX_NR_FUNC`, and `MAX_DIACR`.

## Control Flow
Console keymap tools and the vt keyboard layer encode/decode key symbols with these macros. When key events arrive, the kernel consults keymaps indexed by modifier state and emits characters, escape sequences, console actions, or special control behavior.

## State and Persistence
The mutable state is in kernel keymap/function-string/diacritic tables and modifier/lock state, controlled through `kd.h` ioctls. This header only defines encodings.

## Dependencies and Integration Points
It includes `<linux/wait.h>`. Integration points include vt keyboard code, loadkeys/dumpkeys, console switching, braille input, terminal escape generation, and keyboard ioctls.

## Risks and Test Signals
Tests should verify `K/KTYP/KVAL` packing, max table bounds, no overlap between key types, CSI sequence values, dead-key limits, and compatibility with existing keymap files. ABI risk is high because keymap binaries rely on numeric values.
