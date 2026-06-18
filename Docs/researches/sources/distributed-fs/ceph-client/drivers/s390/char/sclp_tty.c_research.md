<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c -->
## sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c

**Purpose:** `sclp_tty.c` implements the SCLP line-mode terminal driver, providing one real raw system tty backed by SCLP message output and SCLP operator-command input.

**Important APIs and functions:** It registers `sclp_tty_driver` with operations `open`, `close`, `write`, `put_char`, `flush_chars`, `write_room`, `chars_in_buffer`, and `flush_buffer`. Output helpers mirror console buffering: `sclp_tty_write_string()`, `__sclp_ttybuf_emit()`, `sclp_ttybuf_callback()`, and delayed `sclp_tty_timeout()`. Input parsing is in `sclp_tty_receiver()`, `sclp_eval_*()`, `sclp_get_input()`, `sclp_switch_cases()`, and `sclp_tty_input()`.

**Control flow, state, and persistence:** Init skips unsuitable VM/console combinations and systems without line mode, allocates DMA pages, registers SCLP input events, initializes a tty port, and registers tty `sclp_line`. Writes fill reusable SCLP buffers; `put_char()` accumulates small writes in a 512-byte static buffer until newline or flush. Inbound SCLP GDS event data is converted from EBCDIC, case-adjusted for z/VM, control-character processed, and pushed to the tty flip buffer with auto-newline behavior.

**Dependencies and integration:** It depends on `sclp_rw.c`, SCLP event registration for operator/priority message commands, tty core, `ctrlchar`, EBCDIC tables, timers, and global console detection.

**Risks and test signals:** Risks include static single-tty state, dropped input while closed, page exhaustion behavior, `sclp_tty_chars_count` lacking locking in some paths, GDS length trust, and VM case-switch semantics. Tests should cover tty open/close, write-room accounting, delayed flush, put-char buffering, input control chars, auto newline suppression, case delimiter handling, and driver skip conditions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/s390/char/sclp_tty.c -->
