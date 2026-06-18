# sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/dma.h` defines ISA-style DMA constants,
cache alignment requirements, DMA addressability checks, and old DMA-channel hooks. It is part of
the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its
direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than
Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `MAX_DMA_ADDRESS`, `ARCH_LOW_ADDRESS_LIMIT`, `DMA_MODE_MASK`, `DMA_MODE_READ`,
`DMA_MODE_WRITE`, `DMA_MODE_CASCADE`, `DMA_AUTOINIT`, `clear_dma_ff`, `set_dma_addr`, `NO_DMA`;
functions/prototypes: `raw_spin_lock_irqsave`, `raw_spin_unlock_irqrestore`, `set_dma_page`,
`request_dma`, `free_dma`, `enable_dma`, `disable_dma`, `dma_channel_active`, `set_dma_sg`,
`__set_dma_addr`, `set_dma_count`, `set_dma_mode`, `set_dma_speed`, `get_dma_residue`,
`arm_dma_zone_size`, `arm_dma_limit`, `dma_spin_lock`. The file is 149 lines / 4268 bytes, and the
exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `arm_dma_zone_size`, `arm_dma_limit`,
`dma_spin_lock`, `set_dma_page`, `request_dma`, `free_dma`, `enable_dma`, `disable_dma`, and 7 more.
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values.
Direct includes are `linux/spinlock.h`, `linux/scatterlist.h`, `mach/isa-dma.h`. It integrates with
generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Interrupt-related declarations integrate with generic irqchip, exception entry,
and per-CPU irq accounting code. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and
device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `dma.h`. In the
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
