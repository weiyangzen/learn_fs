<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h` describes low-level controller registers and helper macros for `mach-loongson2ef`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 10 macros including `__ASM_MACH_LOONGSON2EF_PCI_H_`, `LOONGSON_PCI_IO_START`, `LOONGSON_CPU_MEM_SRC`, `LOONGSON_PCI_MEM_DST`, `LOONGSON_PCI_MEM_START`, `LOONGSON_PCI_MEM_END`, `MMAP_CPUTOPCI_SIZE`; 0 structs: none; 0 enums: none; 0 callable helpers/prototypes: none; 1 extern variables: `loongson_pci_ops`. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative. It contributes preprocessor constants that are consumed by platform setup or drivers; runtime control flow happens in the including C/assembly files.

## State and Persistence Behavior
No mutable or persistent state is defined in this header. Its persistence is ABI-like: constants and declarations must remain consistent with board files, drivers, firmware tables, and silicon documentation.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `LOONGSON_PCI (7)`, `LOONGSON_CPU (1)`, `MMAP_CPUTOPCI (1)`, `_ (1)`. Typed contracts include no structs. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/pci.h -->
