# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-currituck.c

Purpose: initializes IBM Currituck treeboot images, detects memory size, and patches PCI dma-ranges.

Important APIs/types/functions: functions `ibm_currituck_detect_memsize`, `ibm_currituck_fixups`, `platform_init`; macros `MAX_RANKS`, `DDR3_MR0CF`, `SPRN_PIR`. Source size is 115 lines / 2855 bytes.

Implementation notes: The code reads DDR rank size from DCRs, fixes /memory, updates every PCI dma-ranges size to match detected memory, sets boot CPU ID, and initializes FDT/serial.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`, `libfdt.h`. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
