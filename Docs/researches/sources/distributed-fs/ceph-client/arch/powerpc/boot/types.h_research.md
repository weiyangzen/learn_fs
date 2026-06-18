# sources/distributed-fs/ceph-client/arch/powerpc/boot/types.h

Purpose: defines the boot wrapper's fixed-width integer aliases, bool compatibility, and small utility macros.

Important APIs/types/functions: macros `_TYPES_H_`, `ARRAY_SIZE(x)`, `min(x,y)`, `max(x,y)`, `min_t(type, a, b)`, `max_t(type, a, b)`, `true`, `false`. Source size is 52 lines / 1012 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stdbool.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
