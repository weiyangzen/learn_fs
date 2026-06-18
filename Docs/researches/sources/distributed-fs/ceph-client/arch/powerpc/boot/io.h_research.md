# sources/distributed-fs/ceph-client/arch/powerpc/boot/io.h

Purpose: provides freestanding MMIO accessors, endian-aware loads/stores, and memory-ordering barriers for boot code.

Important APIs/types/functions: functions `in_8`, `out_8`, `in_le16`, `in_be16`, `out_le16`, `out_be16`, `in_le32`, `in_be32`, `out_le32`, `out_be32`, `sync`, `eieio`, `barrier`; macros `_IO_H`. Source size is 103 lines / 2168 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
