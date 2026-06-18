# sources/distributed-fs/ceph-client/arch/powerpc/boot/ps3.c

Purpose: implements PS3 boot-wrapper console, command-line, memory repository, vector-copy, and platform init logic.

Important APIs/types/functions: functions `prep_cmdline`, `ps3_console_write`, `ps3_exit`, `ps3_repository_read_rm_size`, `ps3_copy_vectors`, `platform_init`. Source size is 139 lines / 3090 bytes.

Implementation notes: The platform copies reset vectors for the PS3 loader, reads LV1 repository memory sizing, writes through hypervisor console calls, handles a PS3-specific command line, and exits via hypervisor calls.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
