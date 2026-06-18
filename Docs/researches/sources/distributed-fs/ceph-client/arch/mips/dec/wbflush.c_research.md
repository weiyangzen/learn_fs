# sources/distributed-fs/ceph-client/arch/mips/dec/wbflush.c

Purpose: selects and exports the correct DECstation write-buffer flush routine.

Important APIs: `wbflush_setup()` sets global function pointer `__wbflush`; exported `__wbflush` is used by generic MIPS barrier code. Private routines handle KN01/KN02 CP0 writeback buffer, DS5100 CP3 writeback buffer, or standard uncached-read flush through `__fast_iob()`.

Control flow and state: machine type selects a function pointer at init. KN210 temporarily enables CP3 in CP0 Status, waits on `bc3f`, then restores status.

Dependencies and integration: depends on `mips_machtype`, `CONFIG_CPU_HAS_WB`, and MIPS barrier semantics.

Risks and test signals: wrong flush routine can break MMIO ordering and data coherency. Test device I/O under load on each machine family, especially DS5100 and R2020/R3220 write-buffer systems.
