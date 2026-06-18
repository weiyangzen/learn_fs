# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-ebony.c

Purpose: initializes Ebony treeboot images and imports OpenBIOS MAC addresses into the FDT.

Important APIs/types/functions: functions `platform_init`; macros `OPENBIOS_MAC_BASE`, `OPENBIOS_MAC_OFFSET`. Source size is 29 lines / 695 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `44x.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
