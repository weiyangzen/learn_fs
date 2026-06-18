# sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/edac.h` provides ARM EDAC hooks for memory
error reporting integration. It is part of the ARM kernel-architecture compatibility layer imported
in the Ceph client source tree, so its direct consumers are kernel architecture, MM, interrupt,
driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `ASM_EDAC_H`. The file is 38 lines / 995 bytes, and the exported surface is primarily an
include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
DMA-visible state depends on cache cleanliness, bus mappings, and device/platform data owned by the
DMA mapping or driver layers. There is no userspace filesystem persistence in this file; persistence
is either kernel memory, CPU register state, hardware register state, or generated ABI values. It
integrates with generic Linux ARM architecture code through include-time contracts rather than a
standalone translation unit. DMA paths integrate with cache maintenance, IOMMU, scatterlist, and
device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `edac.h`. In the
distributed filesystem tree this matters indirectly: the Ceph client can only rely on networking,
page cache, DMA, fault handling, and scheduler primitives if these architecture hooks compile and
behave correctly for the target ARM kernel configuration.

### Risks
inline assembly constraints, clobbers, and instruction availability must match the selected ARM
architecture level.

### Test Signals
cross-build the relevant ARM architecture levels and disassemble key helpers; run DMA mapping,
scatterlist, and noncoherent-device tests; ensure all include users still build with sparse/objtool-
style diagnostics where available.
