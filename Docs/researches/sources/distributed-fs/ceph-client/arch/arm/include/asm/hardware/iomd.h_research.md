# sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/iomd.h` defines Acorn IOMD/IOMD2
register maps for timers, DMA, IRQs, video, sound, and keyboard hardware. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `iomd_readb`, `iomd_readl`, `iomd_writeb`, `iomd_writel`, `IOMD_CONTROL`, `IOMD_KARTTX`,
`IOMD_KARTRX`, `IOMD_KCTRL`, `IOMD_IRQSTATA`, `IOMD_IRQREQA`, `IOMD_IRQCLRA`, `IOMD_IRQMASKA`,
`IOMD_IRQSTATB`, `IOMD_IRQREQB`, `IOMD_IRQMASKB`, `IOMD_FIQSTAT`, `IOMD_FIQREQ`, `IOMD_FIQMASK`, and
91 more; functions/prototypes: `vram_half_sam`. The file is 182 lines / 4225 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
External state or implementation hooks include `vram_half_sam`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit.
Interrupt-related declarations integrate with generic irqchip, exception entry, and per-CPU irq
accounting code. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and device model
code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `iomd.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; run DMA mapping, scatterlist, and
noncoherent-device tests; ensure all include users still build with sparse/objtool-style diagnostics
where available.
