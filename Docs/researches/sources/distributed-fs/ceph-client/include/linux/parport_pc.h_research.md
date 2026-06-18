# Research: sources/distributed-fs/ceph-client/include/linux/parport_pc.h

Purpose: `parport_pc.h` provides PC-compatible parallel-port register definitions, private driver state, and inline I/O helpers used by the parport core when PC hardware is supported.

Important APIs/types/functions: register macros compute `DATA`, `STATUS`, `CONTROL`, `EPPADDR`, `EPPDATA`, `FIFO`, `CONFIGA/B`, and `ECONTROL` offsets. `struct parport_pc_private` stores control/ECR shadow state, writable masks, FIFO geometry, DMA buffer metadata, and port linkage. Inline operations include data read/write, control frobbing, data direction changes, control read/write, status read, and IRQ enable/disable. External APIs include resource claim/release, probe, and unregister.

Control flow and state: callers write data through `outb()` and read through `inb()`. Control register writes update a software shadow (`priv->ctr`) after masking by writable bits; direction bit changes route through `parport_pc_data_reverse()` or `_forward()`. IRQ enable/disable toggles the control interrupt bit. Debug builds can dump ECR/DCR/DSR state.

Dependencies and integration points: depends on `asm/io.h`, PC I/O port semantics, parport core structs, DMA addressing, printk, and UAPI control-bit definitions. It is included directly by `parport.h` for optimized PC-only dispatch.

Risks and test signals: risks include stale control shadow state, writing non-writable bits, unsafe direct I/O on absent hardware, DMA buffer lifetime issues, and legacy callers using bit 0x20 instead of direction helpers. Tests should cover register read/write emulation, ECR presence variants, IRQ toggling, resource claim/unclaim, probe failure, and debug-state output.
