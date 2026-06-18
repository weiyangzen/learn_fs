# sources/distributed-fs/ceph-client/arch/powerpc/boot/epapr.c

Purpose: adapts ePAPR firmware entry state to boot-wrapper device-tree and console setup.

Important APIs/types/functions: functions `platform_fixups`, `epapr_platform_init`; macros `EPAPR_SMAGIC`, `EPAPR_EMAGIC`. Source size is 63 lines / 1752 bytes.

Implementation notes: The code checks ePAPR magic values, records loader-provided initrd and command line, initializes an FDT, and selects serial console support before common start().

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `ops.h`, `stdio.h`, `io.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
