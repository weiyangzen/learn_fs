# sources/distributed-fs/ceph-client/arch/powerpc/boot/ops.h

Purpose: defines the boot wrapper's central operation tables, loader metadata, device-tree helpers, console API, allocator API, and exported linker symbols.

Important APIs/types/functions: types `platform_ops`, `dt_ops`, `console_ops`, `serial_console_data`, `loader_info`; functions `getprop`, `setprop`, `setprop_str`, `del_node`, `free`, `exit`, `__attribute__`; macros `_PPC_BOOT_OPS_H_`, `BOOT_COMMAND_LINE_SIZE`, `MAX_PATH_LEN`, `MAX_PROP_LEN`, `setprop_val(devp, name, val)`, `dt_fixup_mac_addresses(...)`, `fatal(args...)`, `BSS_STACK(size)`. Source size is 259 lines / 7437 bytes.

Implementation notes: The important contracts are struct platform_ops, dt_ops, console_ops, serial_console_data, loader_info, the finddevice/getprop/setprop wrappers, dt_fixup declarations, simple_alloc_init, partial_decompress, and linker-provided payload symbols.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `string.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
