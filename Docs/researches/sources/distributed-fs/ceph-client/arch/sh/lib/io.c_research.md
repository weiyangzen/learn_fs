# sources/distributed-fs/ceph-client/arch/sh/lib/io.c

Purpose: implements raw repeated 32-bit I/O reads and writes for SH.

Important APIs: exported `__raw_readsl` and `__raw_writesl`.

Control flow: `__raw_readsl` reads `len` 32-bit values from an I/O address into a buffer with `__raw_readl`; `__raw_writesl` writes buffer values to the I/O address with `__raw_writel`.

State and persistence: mutates device MMIO state or destination memory according to caller direction; no internal state.

Dependencies and integration: depends on `linux/io.h` and is exported for drivers/modules using raw string I/O operations.

Risks: raw operations have no endian conversion or ordering beyond the raw accessor contract; drivers must add barriers if needed.

Test signals: driver I/O tests, MMIO emulation, and module symbol resolution for raw string accessors.
