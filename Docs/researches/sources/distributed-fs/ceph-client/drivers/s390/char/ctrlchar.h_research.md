# sources/distributed-fs/ceph-client/drivers/s390/char/ctrlchar.h

Purpose: declares the control-character helper API and return-code encoding used by s390 terminal drivers.

Important APIs/types/functions: declares `ctrlchar_handle()`, defines `CTRLCHAR_NONE`, `CTRLCHAR_CTRL`, `CTRLCHAR_SYSRQ`, and `CTRLCHAR_MASK`; with `CONFIG_MAGIC_SYSRQ`, defines `struct sysrq_work` and `schedule_sysrq_work()`.

Control flow: no standalone control flow. Callers mask `ctrlchar_handle()` results with `CTRLCHAR_MASK` and either inject the low byte into tty input, ignore sysrq, or process input normally.

State and persistence behavior: no state beyond the optional work struct type.

Dependencies and integration points: includes tty, sysrq, and workqueue headers; shared by console/tty drivers that want uniform s390 control sequence handling.

Risks and test signals: return values combine high-bit tags with low-byte characters, so callers must mask correctly. Compile with and without `CONFIG_MAGIC_SYSRQ`.
