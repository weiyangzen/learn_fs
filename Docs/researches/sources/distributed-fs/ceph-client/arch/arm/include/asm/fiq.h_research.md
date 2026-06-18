# sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fiq.h` declares fast interrupt ownership,
handler installation, register save state, and enable/disable interfaces. It is part of the ARM
kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
types: `fiq_handler`; functions/prototypes: `claim_fiq`, `release_fiq`, `set_fiq_handler`,
`enable_fiq`, `disable_fiq`, `__set_fiq_regs`, `__get_fiq_regs`. The file is 57 lines / 1391 bytes,
and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
IRQ/FIQ helpers are normally used from early boot, interrupt entry, or low-level driver paths where
callers must already understand local interrupt state.

### State, Persistence, And Dependencies
Caller-visible state is represented by `fiq_handler`. External state or implementation hooks include
`claim_fiq`, `release_fiq`, `set_fiq_handler`, `enable_fiq`, `disable_fiq`, `__set_fiq_regs`,
`__get_fiq_regs`. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/ptrace.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Interrupt-related declarations integrate with
generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fiq.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
callers must preserve interrupt-state assumptions and avoid using low-level helpers from preemptible
or wrong-context paths.

### Test Signals
exercise boot, interrupt entry/exit, and irqchip paths; ensure all include users still build with
sparse/objtool-style diagnostics where available.
