# sources/distributed-fs/ceph-client/arch/powerpc/boot/fsl-soc.h

Purpose: declares the shared Freescale SoC clock and IMMR fixup helpers used by board wrappers.

Important APIs/types/functions: macros `_PPC_BOOT_FSL_SOC_H_`. Source size is 9 lines / 151 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
