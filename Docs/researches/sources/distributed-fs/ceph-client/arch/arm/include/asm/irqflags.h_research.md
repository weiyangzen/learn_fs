# sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/irqflags.h` implements local IRQ flag
save/restore and enable/disable using CPSR or CPS instructions. It is part of the ARM kernel-
architecture compatibility layer imported in the Ceph client source tree, so its direct consumers
are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol
logic.

### Important APIs, Types, And Functions
macros: `IRQMASK_REG_NAME_R`, `IRQMASK_REG_NAME_W`, `IRQMASK_I_BIT`, `arch_local_irq_save`,
`arch_local_irq_enable`, `arch_local_irq_disable`, `local_fiq_enable`, `local_fiq_disable`,
`local_abt_enable`, `local_abt_disable`, `arch_local_save_flags`, `arch_local_irq_restore`,
`arch_irqs_disabled_flags`. The file is 187 lines / 3969 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. IRQ/FIQ helpers
are normally used from early boot, interrupt entry, or low-level driver paths where callers must
already understand local interrupt state.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `asm/ptrace.h`, `asm-generic/irqflags.h`. It integrates with generic Linux ARM architecture code
through include-time contracts rather than a standalone translation unit. Interrupt-related
declarations integrate with generic irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `irqflags.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; exercise boot,
interrupt entry/exit, and irqchip paths; ensure all include users still build with sparse/objtool-
style diagnostics where available.
