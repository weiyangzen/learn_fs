<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c

**Purpose:** This file implements the SCLP line-mode console used for printk output through the SCLP message interface.

**Important APIs and functions:** It registers a `struct console` named `ttyS` with `sclp_console_write()` and `sclp_console_device()`. Internal helpers manage page-backed `struct sclp_buffer` objects: `sclp_conbuf_emit()`, `sclp_conbuf_callback()`, `sclp_console_sync_queue()`, and `sclp_console_drop_buffer()`. `sclp_console_notify()` flushes output on panic and reboot.

**Control flow, state, and persistence:** Init runs at `console_initcall` when SCLP or VT220 console is selected. It initializes the SCLP read/write layer, allocates `sclp_console_pages` DMA pages, sets a delayed flush timer, registers panic/reboot notifiers, and registers the console. Write calls fill the current buffer through `sclp_write()`, emit full buffers, and schedule a 100 ms flush for partial lines. Output queues are serialized by `sclp_con_lock`; one buffer can be in flight while others wait.

**Dependencies and integration:** It depends on `sclp_rw.c`, the global console option macros, `sclp_tty_driver` for console-to-tty binding, panic/reboot notifiers, and SCLP core sync waits.

**Risks and test signals:** Risks include console lock recursion during panic, output loss when `sclp_console_drop` is enabled, blocking waits when no pages are available, and flush ordering across timer and notifier paths. Tests should check boot printk replay, delayed partial-line flush, full queue drop counter `sclp_console_full`, panic/reboot flush, and no registration when SCLP consoles are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_con.c -->
