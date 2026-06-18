# sources/distributed-fs/ceph-client/drivers/s390/char/sclp_vt220.c

Purpose: implements the s390 SCLP VT220 TTY and optional console backend, exposing `ttysclp0` and routing terminal input/output through SCLP VT220 event buffers.

Important APIs/types/functions: defines `struct sclp_vt220_request` and `struct sclp_vt220_sccb`; registers output/input `struct sclp_register` entries; implements tty operations `sclp_vt220_open`, `close`, `write`, `put_char`, `flush_chars`, `write_room`, `chars_in_buffer`, and `flush_buffer`; console support uses `sclp_vt220_con_write`, `sclp_vt220_notify`, and `sclp_vt220_con_device`.

Control flow: output pages sit on `sclp_vt220_empty`, become `sclp_vt220_current_request` while filling, move to `sclp_vt220_outqueue`, and are submitted with `sclp_add_request`. Completion callback inspects SCCB response codes, retries recoverable SCLP equipment checks once, returns the page to the empty queue, and starts the next queued request. Input SCLP event buffers distinguish session start/end/data, pass data to the tty flip buffer, and optionally interpret Ctrl-O as Magic SysRq.

State and persistence: all runtime state is in static queues, a tty port, a timer, and page-backed SCCBs guarded by `sclp_vt220_lock`; nothing is persisted. Console init and tty init share the SCLP registration/page pool through `sclp_vt220_init_count`.

Dependencies and integration: depends on `sclp.h`, `ctrlchar.h`, Linux tty/console APIs, panic/reboot notifiers, SCLP core request queues, `sclp_sync_wait`, and global console buffering knobs such as `sclp_console_pages`, `sclp_console_drop`, and `sclp_console_full`.

Risks: output paths may block in sync wait when buffers are exhausted unless `may_fail` is set; panic/reboot flushing deliberately avoids taking an already-held spinlock; buffer-drop behavior can lose console output when configured; malformed or unexpected SCLP response codes are mostly treated as completion after limited retry.

Test signals: boot with `console=ttysclp0`, interactive tty open/write/read, Magic SysRq over SCLP, panic/reboot flush tests, SCLP equipment-check retry tests, and stress of full output buffers with and without console dropping.
