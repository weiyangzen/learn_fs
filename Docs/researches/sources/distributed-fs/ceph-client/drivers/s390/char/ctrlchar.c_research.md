# sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.c

Purpose: centralizes handling of special leading console input sequences for s390 terminals, converting `^c`, `^d`, `^z`, and optionally `^-<key>` sysrq sequences.

Important APIs/types/functions: `ctrlchar_handle()` inspects a short input buffer and returns `CTRLCHAR_NONE`, `CTRLCHAR_SYSRQ`, or a tty control character ORed with `CTRLCHAR_CTRL`. With `CONFIG_MAGIC_SYSRQ`, `schedule_sysrq_work()` schedules `ctrlchar_handle_sysrq()` using a static `sysrq_work`.

Control flow: terminal drivers call `ctrlchar_handle()` after converting input to ASCII. The function accepts two- or three-character buffers beginning with ASCII `^` or codepage-037 hat, maps control requests through `INTR_CHAR()`, `EOF_CHAR()`, and `SUSP_CHAR()`, or schedules sysrq work for `^-x`.

State and persistence behavior: only transient static sysrq work state exists. No persistent data.

Dependencies and integration points: used by 3215 and related terminal input paths; depends on tty special character settings, workqueues, and magic sysrq when enabled.

Risks and test signals: comment notes sysrq handling is racy because a single static work object/key is reused. Test all accepted lengths, EBCDIC hat variant, lowercase/uppercase control chars, nonmatching input passthrough, and concurrent sysrq sequences.
