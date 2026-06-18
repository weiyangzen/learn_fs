# sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/current.h` implements efficient current
task lookup through TPIDRPRW/TPIDRURO or stack masking depending on CPU and SMP configuration. It is
part of the ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so
its direct consumers are kernel architecture, MM, interrupt, driver, and board-support code rather
than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ASM_ARM_CURRENT_H`, `current`; types: `task_struct`; functions/prototypes:
`__builtin_thread_pointer`, `asm`, `__current`. The file is 65 lines / 1844 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
Caller-visible state is represented by `task_struct`. External state or implementation hooks include
`__current`. There is no userspace filesystem persistence in this file; persistence is either kernel
memory, CPU register state, hardware register state, or generated ABI values. Direct includes are
`asm/insn.h`. It integrates with generic Linux ARM architecture code through include-time contracts
rather than a standalone translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `current.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
