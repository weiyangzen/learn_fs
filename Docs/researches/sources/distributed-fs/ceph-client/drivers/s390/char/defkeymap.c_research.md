# sources/distributed-fs/ceph-client/drivers/s390/char/defkeymap.c

Purpose: generated default EBCDIC keyboard map for s390 3270 keyboard handling, including plain/shift/control maps, function-key strings, and accent composition table.

Important APIs/types/functions: exports `ebc_plain_map`, `ebc_key_maps`, `ebc_keymap_count`, `ebc_func_buf`, `ebc_funcbufptr`, `ebc_funcbufsize`, `ebc_funcbufleft`, `ebc_func_table`, `ebc_accent_table`, and `ebc_accent_table_size`.

Control flow: no executable logic; consumers index tables to translate keycodes and function keys. The file is generated from `defkeymap.map` via `loadkeys --mktable`.

State and persistence behavior: static table state only. Function buffer pointers can be used by keyboard code for runtime keymap string management, but defaults are compiled in.

Dependencies and integration points: includes Linux keyboard/kd/kbd headers, diacritic structures, and local `keyboard.h`; consumed by s390 keyboard/3270 tty code.

Risks and test signals: manual edits would be overwritten by regeneration and can desynchronize with `defkeymap.map`. Test keyboard input translation, function keys, diacritic composition, and builds after regenerating the table.
