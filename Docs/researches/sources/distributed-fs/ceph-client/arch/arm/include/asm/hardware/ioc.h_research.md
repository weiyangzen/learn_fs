# sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/hardware/ioc.h` defines Acorn IOC register
layout, timers, IRQ/FIQ masks, and keyboard/serial hardware constants. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `ioc_readb`, `ioc_writeb`, `IOC_CONTROL`, `IOC_KARTTX`, `IOC_KARTRX`, `IOC_IRQSTATA`,
`IOC_IRQREQA`, `IOC_IRQCLRA`, `IOC_IRQMASKA`, `IOC_IRQSTATB`, `IOC_IRQREQB`, `IOC_IRQMASKB`,
`IOC_FIQSTAT`, `IOC_FIQREQ`, `IOC_FIQMASK`, `IOC_T0CNTL`, `IOC_T0LTCHL`, `IOC_T0CNTH`, and 21 more.
The file is 69 lines / 1549 bytes, and the exported surface is primarily an include-time contract
for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state. Most behavior is selected through
preprocessor branches, so the actual compiled path depends heavily on `CONFIG_*`, CPU architecture
level, and board configuration.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit. Interrupt-related declarations integrate with generic irqchip, exception entry,
and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `ioc.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths; heavy preprocessor selection creates configuration-specific coverage gaps.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
