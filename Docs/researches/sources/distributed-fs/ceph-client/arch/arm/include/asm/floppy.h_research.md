# sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/floppy.h` provides ARM legacy floppy I/O,
DMA, and virtual DMA compatibility definitions. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `fd_outb`, `fd_inb`, `fd_request_irq`, `fd_free_irq`, `fd_disable_irq`, `fd_enable_irq`,
`fd_dma_setup`, `fd_request_dma`, `fd_free_dma`, `fd_disable_dma`, `DMA_FLOPPYDISK`, `FDC1`,
`FLOPPY0_TYPE`, `FLOPPY1_TYPE`, `N_FDC`, `N_DRIVE`, `EXTRA_FLOPPY_PARAMS`; functions/prototypes:
`set_dma_mode`, `__set_dma_addr`, `set_dma_count`, `enable_dma`, `swap`. The file is 81 lines / 2289
bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. Interrupt-related declarations integrate with generic irqchip,
exception entry, and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU,
scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `floppy.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
