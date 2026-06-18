# sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/include/asm/kexec.h` defines ARM kexec architecture
limits, machine_kexec hooks, and crash relocation state. It is part of the ARM kernel-architecture
compatibility layer imported in the Ceph client source tree, so its direct consumers are kernel
architecture, MM, interrupt, driver, and board-support code rather than Ceph protocol logic.

### Important APIs, Types, And Functions
macros: `_ARM_KEXEC_H`, `KEXEC_SOURCE_MEMORY_LIMIT`, `KEXEC_DESTINATION_MEMORY_LIMIT`,
`KEXEC_CONTROL_MEMORY_LIMIT`, `KEXEC_CONTROL_PAGE_SIZE`, `KEXEC_ARCH`, `KEXEC_ARM_ATAGS_OFFSET`,
`KEXEC_ARM_ZIMAGE_OFFSET`, `ARCH_HAS_KIMAGE_ARCH`, `phys_to_boot_phys`, `boot_phys_to_phys`,
`page_to_boot_pfn`, `boot_pfn_to_page`; types: `kimage_arch`, `pt_regs`; functions/prototypes:
`memcpy`, `phys_to_idmap`, `idmap_to_phys`, `page_to_pfn`, `pfn_to_page`. The file is 83 lines /
2207 bytes, and the exported surface is primarily an include-time contract for other kernel files.

### Control Flow
Inline assembly or assembler-facing macros are the main execution path; callers expand these helpers
directly into privileged ARM instructions or carefully constrained memory accesses.

### State, Persistence, And Dependencies
Caller-visible state is represented by `kimage_arch`, `pt_regs`. DMA-visible state depends on cache
cleanliness, bus mappings, and device/platform data owned by the DMA mapping or driver layers. There
is no userspace filesystem persistence in this file; persistence is either kernel memory, CPU
register state, hardware register state, or generated ABI values. It integrates with generic Linux
ARM architecture code through include-time contracts rather than a standalone translation unit. DMA
paths integrate with cache maintenance, IOMMU, scatterlist, and device model code.

### Integration Points
The header is included by ARM architecture implementation files, board/platform code, low-level
drivers, and generic Linux subsystems that need the ARM-specific version of `kexec.h`. In the
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
