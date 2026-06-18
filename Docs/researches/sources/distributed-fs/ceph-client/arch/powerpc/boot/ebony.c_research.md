# sources/distributed-fs/ceph-client/arch/powerpc/boot/ebony.c

Purpose: performs IBM Ebony 440GP boot-wrapper fixups, especially flash-bank selection and early board initialization.

Important APIs/types/functions: functions `ebony_flashsel_fixup`, `ebony_fixups`, `ebony_init`; macros `EBONY_FPGA_PATH`, `EBONY_FPGA_FLASH_SEL`, `EBONY_SMALL_FLASH_PATH`. Source size is 88 lines / 2294 bytes.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
