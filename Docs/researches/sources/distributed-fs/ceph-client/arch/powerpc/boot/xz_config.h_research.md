# sources/distributed-fs/ceph-client/arch/powerpc/boot/xz_config.h

Purpose: adapts the kernel XZ decompressor to the boot wrapper's freestanding environment.

Important APIs/types/functions: functions `swab32p`, `be32_to_cpup`, `be32_to_cpup`, `get_unaligned_be32`, `put_unaligned_be32`; macros `__XZ_CONFIG_H__`, `get_le32(p)`, `cpu_to_be32(x)`, `get_le32(p)`, `cpu_to_be32(x)`, `memeq(a, b, size)`, `memzero(buf, size)`, `DECOMPR_MM_H`, `memmove`. Source size is 57 lines / 1199 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`, `swab.h`, `../../../include/linux/xz.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
