## sources/distributed-fs/ceph-client/drivers/input/keyboard/newtonkbd.c

Purpose: Apple Newton serial keyboard driver. It maps 7-bit Newton scancodes with a press bit into Linux key events through serio.

Important APIs/types/functions: `struct nkbd` stores the 128-byte keycode map, input device, serio port, and physical path. `nkbd_interrupt()` decodes incoming bytes using `NKBD_KEY` and `NKBD_PRESS`. `nkbd_connect()` allocates/registers input and opens serio; `nkbd_disconnect()` closes/unregisters/frees.

Control flow: connect copies the static keymap, sets `BUS_RS232` ids, marks all mapped keys and autorepeat, opens serio, and registers input. Runtime ignores unmapped scancodes except for `0xe7`, which logs end of initialization; mapped scancodes report `data & NKBD_PRESS` as key state and sync immediately.

State/dependencies/integration: no persistent state beyond the keymap and input/serio associations. Integration is via `module_serio_driver` with `SERIO_NEWTON`.

Risks and test signals: the keycode map uses byte-sized storage, but Linux keycodes here fit the selected values. Invalid initialization bytes are intentionally ignored. Test connect failure unwinding, press/release polarity, init-sequence logging, unknown scancodes, autorepeat bit, and disconnect ordering.
