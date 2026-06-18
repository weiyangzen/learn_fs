# sources/distributed-fs/ceph-client/drivers/i3c/internals.h

Purpose: Private I3C core header shared by the public device API, master core, and controller drivers. It declares locked core helpers and provides FIFO helpers for 32-bit hardware FIFOs.

Important APIs/types/functions: Declares bus runtime PM helpers, bus normal-use locking, locked transfer/SETDASA/IBI helpers, and inline `i3c_writel_fifo()`/`i3c_readl_fifo()`.

Control flow: FIFO writes use `writesl()` for full words and one zero-padded tail word for remaining bytes. FIFO reads use `readsl()` for full words and copy a tail word into remaining bytes. Declared functions are implemented mainly in `master.c`.

State and persistence: No persistent structures are defined. FIFO helpers mutate MMIO FIFO state and preserve byte order on big-endian targets by using string I/O helpers.

Dependencies/integration: `linux/i3c/master.h`, `linux/io.h`, `device.c`, `master.c`, and controller drivers such as ADI, Cadence, and DesignWare.

Risks: Tail accesses require hardware FIFOs that tolerate full-word final reads/writes. Buffer sizes must match `nbytes`. The helper uses kernel-supported GNU C `void *` arithmetic.

Test signals: Non-multiple-of-four FIFO transfers on little and big endian systems; short-read handling; controller tests that verify no buffer overrun on reported payload lengths.
