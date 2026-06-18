# sources/distributed-fs/ceph-client/arch/arm/mach-rpc/floppydma.S

Purpose: fast interrupt DMA copy routines for the RiscPC floppy controller.

Important APIs/types/functions: exposes input and output handler ranges such as `floppy_fiqin_start/end` and `floppy_fiqout_start/end` consumed by `dma.c`.

Control flow: FIQ handler copies data between floppy hardware FIFO and memory, updates the byte count register saved in FIQ regs, and returns quickly to minimize latency.

State and persistence: uses FIQ registers set by `floppy_enable_dma()` for count, buffer pointer, and controller base. No durable state.

Dependencies and integration points: installed via ARM FIQ framework by `dma.c` for virtual floppy DMA.

Risks: assembly must be reentrant only as FIQ context expects; wrong register convention corrupts transfer state. Buffer bounds rely on count from higher layers.

Test signals: floppy read/write data integrity, residue count, and FIQ claim/release behavior.
