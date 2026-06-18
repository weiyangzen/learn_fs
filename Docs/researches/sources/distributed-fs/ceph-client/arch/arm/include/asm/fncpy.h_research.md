# sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/fncpy.h` provides helpers for copying
functions to executable memory while preserving PC-relative execution assumptions. It is part of the
ARM kernel-architecture compatibility layer imported in the Ceph client source tree, so its direct
consumers are kernel architecture, MM, interrupt, driver, and board-support code rather than Ceph
protocol logic.

### Important APIs, Types, And Functions
macros: `FNCPY_ALIGN`, `fncpy`. The file is 82 lines / 2552 bytes, and the exported surface is
primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. Direct includes
are `linux/types.h`, `linux/string.h`, `asm/bug.h`, `asm/cacheflush.h`. It integrates with generic
Linux ARM architecture code through include-time contracts rather than a standalone translation
unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `fncpy.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; ensure all include
users still build with sparse/objtool-style diagnostics where available.
