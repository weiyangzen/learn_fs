# sources/distributed-fs/ceph-client/arch/powerpc/boot/wii.c

Purpose: initializes the Wii wrapper, enables EXI, probes USB Gecko, and trims MEM2 around mini firmware.

Important APIs/types/functions: types `mipc_infohdr`, `mipc_infohdr`, `mipc_infohdr`; functions `mipc_check_address`, `mipc_get_mem2_boundary`, `platform_fixups`, `platform_init`; assembly labels/symbols `out`, `out`, `out`; macros `HW_REG(x)`, `EXI_CTRL`, `EXI_CTRL_ENABLE`, `MEM2_TOP`, `FIRMWARE_DEFAULT_SIZE`. Source size is 153 lines / 3008 bytes.

Implementation notes: The wrapper validates mini IPC pointers in MEM2, obtains the firmware memory boundary when available, shrinks the second memory bank, enables EXI, and uses USB Gecko for early output.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stddef.h`, `stdio.h`, `types.h`, `io.h`, `ops.h`, `ugecon.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
