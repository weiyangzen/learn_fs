# sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/cmpxchg.h` implements ARM cmpxchg/xchg
primitives, including exclusive-access loops, pre-ARMv6 IRQ-protected fallbacks, and size dispatch.
It is part of the ARM kernel-architecture compatibility layer imported in the Ceph client source
tree, so its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code
rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `swp_is_buggy`, `arch_xchg_relaxed`, `arch_xchg`, `arch_cmpxchg_local`,
`arch_cmpxchg64_local`, `arch_cmpxchg_relaxed`, `arch_cmpxchg64_relaxed`; functions/prototypes:
`__bad_xchg`, `prefetchw`, `raw_local_irq_save`, `raw_local_irq_restore`, `__bad_cmpxchg`,
`cmpxchg_emu_u8`, `__generic_cmpxchg_local`, `__cmpxchg`. The file is 285 lines / 6463 bytes, and
the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses. Ordering-
sensitive helpers place barriers around the architectural operation so SMP, DMA, exception return,
or device-observable side effects occur in the required sequence. IRQ/FIQ helpers are normally used
from early boot, interrupt entry, or low-level driver paths where callers must already understand
local interrupt state.

### State, Persistence, And Dependencies
External state or implementation hooks include `__bad_xchg`, `__bad_cmpxchg`. There is no userspace
filesystem persistence in this file; persistence is either kernel memory, CPU register state,
hardware register state, or generated ABI values. Direct includes are `linux/irqflags.h`,
`linux/prefetch.h`, `asm/barrier.h`, `linux/cmpxchg-emu.h`, `asm-generic/cmpxchg-local.h`, `asm-
generic/cmpxchg.h`. It integrates with generic Linux ARM architecture code through include-time
contracts rather than a standalone translation unit. Barrier correctness depends on ARM memory-model
semantics and the generic Linux ordering APIs. Interrupt-related declarations integrate with generic
irqchip, exception entry, and per-CPU irq accounting code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `cmpxchg.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level; missing or misplaced barriers can create SMP, DMA, or device-ordering races that
are hard to reproduce; callers must preserve interrupt-state assumptions and avoid using low-level
helpers from preemptible or wrong-context paths.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run SMP, lockdep,
memory-ordering, and DMA stress tests; exercise boot, interrupt entry/exit, and irqchip paths;
ensure all include users still build with sparse/objtool-style diagnostics where available.
