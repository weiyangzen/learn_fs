# sources/distributed-fs/ceph-client/arch/powerpc/boot/crt0.S

## Purpose
PowerPC boot-wrapper entry assembly. It self-relocates PIE-linked wrappers, flushes instruction/data caches, clears BSS, optionally switches stacks, calls `platform_init()`, then branches to the wrapper `start` routine. On ppc64 it also provides an Open Firmware call trampoline.

## Important APIs, Types, And Control Flow
`_zimage_start`/`_zimage_start_lib` compute the runtime base with `bcl/mflr`. The 32-bit path parses `_DYNAMIC`, locates RELA entries, applies `R_PPC_RELATIVE`, flushes text cache lines, clears BSS with stores, and optionally uses `_platform_stack_top`. The 64-bit path saves the PROM pointer, sets r2 TOC, processes `R_PPC64_RELATIVE`, flushes caches, clears BSS, and sets a 64-bit stack frame. Both paths call `platform_init` and branch to `start`. The ppc64 `prom` label saves registers/MSR, switches endian/firmware state through `rfid`, calls firmware via saved PROM entry, then restores state.

## State, Dependencies, Risks, And Tests
State includes relocated data, BSS, runtime stack pointer, TOC, saved PROM pointer, and the register/MSR frame for firmware calls. Dependencies include linker-provided symbols, relocation format, `ppc_asm.h`, cache-line assumptions, and platform wrapper ABI. Risks include relocation parser mismatch, BSS clearing wrong width, cache flush range errors, endian/MSR restore bugs, and stack-frame ABI violations. Test by booting PIE/non-PIE wrappers, ppc32 and ppc64 Open Firmware paths, custom platform stack configs, and firmware calls returning across endian boundaries.
