# sources/distributed-fs/ceph-client/arch/powerpc/boot/simple_alloc.c

Purpose: implements a small fixed-region malloc/free/realloc allocator used before the kernel is entered.

Important APIs/types/functions: types `alloc_info`, `alloc_info`, `alloc_info`, `alloc_info`; functions `simple_free`; assembly labels/symbols `err_out`; macros `ENTRY_BEEN_USED`, `ENTRY_IN_USE`. Source size is 151 lines / 3482 bytes.

Implementation notes: Allocation state is a static table with been-used and in-use flags; freed entries can be reused only if the requested size fits the original block, and realloc copies to a new block when growth is required.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: Persistent boot-wrapper state is the allocation table, next heap base, free-space counter, and platform_ops allocator hooks; it is intentionally not returned to firmware.

Dependencies and integration: Includes/dependencies: `stddef.h`, `types.h`, `page.h`, `string.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
