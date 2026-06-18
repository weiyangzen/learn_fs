# sources/distributed-fs/ceph-client/arch/powerpc/boot/ppc_asm.h

Purpose: provides register aliases and linkage macros for PowerPC boot assembly sources.

Important APIs/types/functions: macros `_PPC64_PPC_ASM_H`, `cr0`, `cr1`, `cr2`, `cr3`, `cr4`, `cr5`, `cr6`, `cr7`, `r0`, `r1`, `r2`, `r3`, `r4`, `r5`, `r6`, `r7`, `r8`, and 35 more. Source size is 97 lines / 2089 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: none or build-tool implicit dependencies. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
