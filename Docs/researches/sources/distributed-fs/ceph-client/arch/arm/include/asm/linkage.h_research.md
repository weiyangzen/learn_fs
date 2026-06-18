# sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/linkage.h` adds ARM assembler linkage
annotations such as ENDPROC and alignment conventions. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `__ALIGN`, `__ALIGN_STR`, `ENDPROC`. The file is 12 lines / 216 bytes, and the exported
surface is primarily an include-time contract for other kernel files.

### Control Flow
This header mostly supplies constants, declarations, or compile-time glue; runtime flow is driven by
the C or assembly files that include it.

### State, Persistence, And Dependencies
The header itself has no storage or filesystem persistence; it contributes compile-time constants
and inline code. There is no userspace filesystem persistence in this file; persistence is either
kernel memory, CPU register state, hardware register state, or generated ABI values. It integrates
with generic Linux ARM architecture code through include-time contracts rather than a standalone
translation unit.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `linkage.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
the main risk is ABI drift: constants and prototypes must stay synchronized with the implementation
files that include this header.

### Test Signals
compile coverage across representative ARM configs; ensure all include users still build with
sparse/objtool-style diagnostics where available.
