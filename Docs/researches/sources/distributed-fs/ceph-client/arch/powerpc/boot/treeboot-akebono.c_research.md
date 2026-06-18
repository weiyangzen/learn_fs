# sources/distributed-fs/ceph-client/arch/powerpc/boot/treeboot-akebono.c

Purpose: initializes IBM Akebono treeboot images, detects DDR3 memory size, handles PIBS command-line MAC data, and patches FDT state.

Important APIs/types/functions: functions `ibm_akebono_detect_memsize`, `ibm_akebono_fixups`, `platform_init`; macros `SPRN_PIR`, `USERDATA_LEN`, `MAX_RANKS`, `DDR3_MR0CF`, `CCTL0_MCO2`, `CCTL0_MCO3`, `CCTL0_MCO4`, `CCTL0_MCO5`, `CCTL0_MCO6`. Source size is 159 lines / 3905 bytes.

Implementation notes: The code scans PIBS userdata for local-mac-addr, removes that token from the command line, reads DDR rank size from DCRs, disables broken SD high-speed mode, sets boot CPU ID, and initializes FDT/serial.

Control flow is platform_init first: establish stack/heap, capture loader metadata, initialize FDT or firmware dt_ops, install console and platform fixup callbacks, then common start() invokes those fixups before entering the kernel.

State and persistence: State is short-lived boot-wrapper global state: loader_info, platform_ops, console_ops, dt_ops, FDT properties, firmware board tables, MMIO register values, and heap allocations that live only until the kernel takes control.

Dependencies and integration: Includes/dependencies: `stdarg.h`, `stddef.h`, `types.h`, `elf.h`, `string.h`, `stdlib.h`, `stdio.h`, `page.h`, `ops.h`, `reg.h`, `io.h`, `dcr.h`, `4xx.h`, `44x.h`, and 1 more. Integration points are the common boot-wrapper operation tables, libfdt/Open Firmware backends, serial backends, linker-provided payload symbols, board firmware metadata, and platform-specific MMIO/register helpers.

Risks and test signals: Risks include incorrect firmware metadata interpretation, FDT property width/endian mistakes, bad heap sizing, console initialization failure, and board-specific MMIO side effects. Test signals are defconfig builds, bootwrapper link tests, FDT dump comparison before/after fixups, serial output, and target-board or emulator boot smoke tests.
