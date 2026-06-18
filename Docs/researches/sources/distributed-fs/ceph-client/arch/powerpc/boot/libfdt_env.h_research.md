# sources/distributed-fs/ceph-client/arch/powerpc/boot/libfdt_env.h

Purpose: supplies the minimal libfdt environment, integer limits, endian conversion, and unaligned helpers for boot builds.

Important APIs/types/functions: macros `_ARCH_POWERPC_BOOT_LIBFDT_ENV_H`, `INT_MAX`, `UINT32_MAX`, `INT32_MAX`, `fdt16_to_cpu(x)`, `cpu_to_fdt16(x)`, `fdt32_to_cpu(x)`, `cpu_to_fdt32(x)`, `fdt64_to_cpu(x)`, `cpu_to_fdt64(x)`. Source size is 27 lines / 680 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`, `string.h`, `of.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
