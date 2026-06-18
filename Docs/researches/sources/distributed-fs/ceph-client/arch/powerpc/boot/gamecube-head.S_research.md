# sources/distributed-fs/ceph-client/arch/powerpc/boot/gamecube-head.S

Purpose: sets up the Nintendo GameCube low-level entry path, MMU state, and handoff to C wrapper code.

Important APIs/types/functions: assembly labels/symbols `_zimage_start`, `_mmu_off`, `_mmu_on`. Source size is 106 lines / 2232 bytes.

Control flow begins at firmware-selected entry labels or helper symbols, establishes the calling convention/MMU/cache state required by C code or libgcc-compatible helpers, and branches or returns through PowerPC ABI registers.

State and persistence: State is early CPU register, stack, MMU/cache, timebase, or reset-vector state. Mistakes persist into C boot code or the kernel entry ABI.

Dependencies and integration: Includes/dependencies: `ppc_asm.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect entry ABI, stack/register clobbering, MMU/cache transition mistakes, broken reset overlay placement, and helper arithmetic edge cases. Test signals are cross-assembly, disassembly review, QEMU/firmware boot smoke tests, and ABI-focused unit tests where possible.
