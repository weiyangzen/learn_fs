<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h -->
## sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h

**Purpose:** This header declares the s390 EBCDIC keyboard helper interface used by console and terminal drivers. It defines the instance state that connects key translation to a tty port and exposes the global default maps supplied elsewhere.

**Important APIs and types:** `struct kbd_data` stores a `tty_port`, per-instance key maps, function table, special function handlers, accent table, active diacritic, and SysRq state. Public functions are `kbd_alloc()`, `kbd_free()`, `kbd_ascebc()`, `kbd_keycode()`, and `kbd_ioctl()`. Inline helpers `kbd_put_queue()` and `kbd_puts_queue()` insert characters into the tty flip buffer and push immediately.

**Control flow, state, and persistence:** The header makes `struct kbd_data` the persistent per-console state object. The global `ebc_*` externs are templates; `keyboard.c` copies them so ioctls can mutate an instance without changing global defaults.

**Dependencies and integration:** It depends on tty, tty flip buffers, Linux keyboard definitions, and diacritic structures. The `MAX_NR_FUNC`, `MAX_NR_KEYMAPS`, and `NR_KEYS` constants are inherited from the kernel keyboard layer.

**Risks and test signals:** The main risks are consumers failing to initialize `kbd_data->port`, using handlers beyond `NR_FN_HANDLER`, or assuming the inline queue helpers batch output. Test signals are successful allocation, keycode delivery to the attached tty port, ioctl visibility of cloned maps, and clean free of all nested allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/keyboard.h -->
