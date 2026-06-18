# sources/distributed-fs/ceph-client/arch/powerpc/boot/mktree.c

Purpose: converts an ELF zImage into the treeboot image format with a compact binary header.

Important APIs/types/functions: types `boot_block`, `stat`; functions `main`; macros `IMGBLK`. Source size is 151 lines / 3620 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `fcntl.h`, `stdio.h`, `stdlib.h`, `string.h`, `sys/stat.h`, `unistd.h`, `netinet/in.h`, `inttypes.h`, `stdint.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
