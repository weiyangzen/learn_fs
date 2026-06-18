<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c

**Purpose:** This file implements EBCDIC keycode handling for s390 console drivers. It clones the default EBCDIC keymaps/function strings per keyboard instance, translates keycodes into tty input, supports dead-key composition, handles Magic SysRq sequences, and implements a subset of VT keyboard ioctls.

**Important APIs and functions:** Public exports are `kbd_alloc()`, `kbd_free()`, `kbd_ascebc()`, `kbd_keycode()`, and `kbd_ioctl()`. Key handlers include `k_self()`, `k_dead()`, `k_fn()`, `k_spec()`, and `to_utf8()`. The ioctl helpers `do_kdsk_ioctl()` and `do_kdgkb_ioctl()` service keymap and function-string get/set commands.

**Control flow, state, and persistence:** `kbd_alloc()` deep-copies global EBCDIC maps, function tables, and accent table into `struct kbd_data`; later ioctl writes mutate only that instance. `kbd_keycode()` chooses one of maps 0, 1, 4, or 5 based on the keycode range, normalizes `KT_LETTER` to latin, interprets SysRq prefix state, dispatches key handlers, or emits UTF-8 for direct Unicode keysyms. Dead-key state is stored in `kbd->diacr` until the next character.

**Dependencies and integration:** It integrates with tty flip buffers via helpers in `keyboard.h`, Linux keyboard symbols, console maps, sysrq, and uaccess. Consumers attach `kbd_data->port` to the target tty port.

**Risks and test signals:** Risks include keymap bounds errors, racy tty ownership permission checks, missing null map handling for unexpected keycode ranges, incorrect `KBD_NR_TYPES` validation, and user-copy failures leaving partial ioctl changes. Test signals include default EBCDIC-to-ASCII mapping, dead-key combinations, function-key strings, SysRq prefix handling, ioctl permission checks, map allocation/free paths, and Unicode keysyms above 8 bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.c -->
