# sources/distributed-fs/ceph-client/arch/powerpc/boot/opal.c

Purpose: implements an OPAL console backend for PowerNV boot-wrapper output.

Important APIs/types/functions: types `opal`; functions `opal_con_open`, `opal_con_putc`, `opal_con_close`, `opal_init`, `opal_console_init`. Source size is 97 lines / 2284 bytes.

Implementation notes: OPAL console setup finds a raw OPAL console node, opens it, sends bytes through OPAL_CONSOLE_WRITE, and closes it through OPAL_CONSOLE_CLOSE.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `io.h`, `libfdt.h`, `../include/asm/opal-api.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
