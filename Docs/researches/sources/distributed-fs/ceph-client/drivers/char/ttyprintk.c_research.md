<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c -->
# sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c

Purpose: Implements the `ttyprintk` pseudo TTY that lets userspace write lines into the kernel log with a configured printk priority and `[U]` prefix. It is useful for boot/service logging where userspace console messages should be interleaved with kernel messages.

Important APIs/types/functions: `struct ttyprintk_port` embeds `tty_port` plus a spinlock. `tpk_printk()` normalizes CR/LF handling, fragments overlong lines, and buffers partial lines. `tpk_flush()` emits the current line with `printk(TPK_PREFIX "[U] ...")`. `tpk_open()`, `tpk_close()`, `tpk_write()`, `tpk_write_room()`, `tpk_hangup()`, and `tpk_port_shutdown()` implement the TTY operations. `ttyprintk_console_device()` lets the registered console point at the tty driver.

Control flow: init allocates a one-line raw unnumbered TTY driver at `TTYAUX_MAJOR` minor 3, initializes and links the single tty port, registers the driver, and registers a console named `ttyprintk`. Writes take the port spinlock, feed bytes through `tpk_printk()`, flush on newline/CR or line-size overflow, and return the original count. Port shutdown flushes any trailing partial line.

State and persistence: global runtime state is the singleton `tpk_port`, `tpk_curr`, `tpk_buffer`, and `ttyprintk_driver`. Buffered partial text persists only until newline, overflow fragmentation, shutdown, or module exit.

Dependencies and integration: depends on the Linux TTY core, console registration, printk, and `CONFIG_TTY_PRINTK_LEVEL` for log priority. The device appears as a console-type TTY rather than a normal misc device.

Risks: `tpk_buffer` and `tpk_curr` are global for the single port, so locking must continue to cover all write/flush paths. Long-line fragmentation appends a backslash and flushes, which changes exact user text. `write_room()` advertises 4 KiB independent of the internal line buffer, relying on immediate formatting. Init error cleanup must destroy the tty port after driver allocation failures.

Test signals: open `/dev/ttyprintk`, write LF, CR, CRLF, partial lines, and lines longer than `TPK_STR_SIZE`; verify printk priority and `[U]` prefix, no interleaving under concurrent writes, flush on close/shutdown, and device/console registration/unregistration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ttyprintk.c -->
