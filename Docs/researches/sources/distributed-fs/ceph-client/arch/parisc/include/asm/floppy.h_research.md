# sources/distributed-fs/ceph-client/arch/parisc/include/asm/floppy.h

Purpose: supplies PA-RISC architecture glue for the legacy floppy driver, including DMA, virtual DMA, and platform I/O access assumptions.

Important APIs/types/functions: defines floppy DMA setup/teardown helpers, virtual DMA hooks, request/free DMA wrappers, and architecture-specific constants consumed by the generic floppy driver.

Control flow: the floppy driver requests DMA, programs controller transfers, handles virtual DMA fallbacks where required, and performs I/O through PA-RISC accessors.

State and persistence: DMA channel ownership and floppy controller state persist during transfers. Dependencies and integration: integrates with `dma.h`, `io.h`, SuperIO/legacy IRQ routing, and the generic floppy driver.

Risks and test signals: legacy DMA assumptions are fragile on non-PC PA-RISC hardware. Test with build coverage, floppy probe/no-probe boot paths, and real hardware transfer tests if available.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
