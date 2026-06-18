# sources/distributed-fs/ceph-client/arch/powerpc/boot/planetcore.c

Purpose: parses PlanetCore firmware key/value tables and applies board, MAC, memory, clock, and stdout fixups.

Important APIs/types/functions: functions `planetcore_prepare_table`, `planetcore_get_decimal`, `planetcore_get_hex`, `planetcore_set_mac_addrs`, `planetcore_set_stdout_path`. Source size is 130 lines / 2554 bytes.

Control flow follows direct helper calls from platform_init or start(); the code is freestanding and avoids kernel services except for the crypto files outside boot/.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdio.h`, `stdlib.h`, `ops.h`, `planetcore.h`, `io.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
