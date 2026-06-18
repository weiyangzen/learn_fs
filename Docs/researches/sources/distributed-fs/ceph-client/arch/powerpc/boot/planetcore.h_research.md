# sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.h

Purpose: defines PlanetCore key identifiers and table structures shared by EP8248E/EP88xC wrapper code.

Important APIs/types/functions: macros `_PPC_BOOT_PLANETCORE_H_`, `PLANETCORE_KEY_BOARD_TYPE`, `PLANETCORE_KEY_BOARD_REV`, `PLANETCORE_KEY_MB_RAM`, `PLANETCORE_KEY_MAC_ADDR`, `PLANETCORE_KEY_FLASH_SPEED`, `PLANETCORE_KEY_IP_ADDR`, `PLANETCORE_KEY_KB_NVRAM`, `PLANETCORE_KEY_PROCESSOR`, `PLANETCORE_KEY_PROC_VARIANT`, `PLANETCORE_KEY_SERIAL_BAUD`, `PLANETCORE_KEY_SERIAL_PORT`, `PLANETCORE_KEY_SWITCH`, `PLANETCORE_KEY_TEMP_OFFSET`, `PLANETCORE_KEY_TARGET_IP`, `PLANETCORE_KEY_CRYSTAL_HZ`. Source size is 47 lines / 1554 bytes.

Runtime flow is in consumers; this file supplies constants, types, prototypes, and inline helpers that shape boot-wrapper or crypto behavior at compile time.

State and persistence: There is no standalone mutable state; consumers use the declarations to manipulate FDT properties, firmware handles, MMIO registers, linker symbols, or request-local crypto data.

Dependencies and integration: Includes/dependencies: `types.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include stale declarations, width/endian mismatches, duplicated macro names, or consumers assuming unavailable callbacks. Test signals are compile coverage across 32/64-bit PowerPC configs, sparse/objtool-style checks where applicable, and exercising the consumers that include this header.
