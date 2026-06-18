# sources/distributed-fs/ceph-client/arch/powerpc/boot/of.h

Purpose: declares Open Firmware handles, PROM call wrappers, endian conversion, and OF dt_ops entry points.

Important APIs/types/functions: macros `_PPC_BOOT_OF_H_`, `cpu_to_be16(x)`, `be16_to_cpu(x)`, `cpu_to_be32(x)`, `be32_to_cpu(x)`, `cpu_to_be64(x)`, `be64_to_cpu(x)`, `cpu_to_be16(x)`, `be16_to_cpu(x)`, `cpu_to_be32(x)`, `be32_to_cpu(x)`, `cpu_to_be64(x)`, `be64_to_cpu(x)`, `PROM_ERROR`. Source size is 47 lines / 1199 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `swab.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
