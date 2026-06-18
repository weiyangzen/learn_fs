<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h` describes low-level controller registers and helper macros for `mach-rc32434`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 278 macros including `_ASM_RC32434_PCI_H_`, `epld_mask`, `PCI0_BASE_ADDR`, `PCI_LBA_COUNT`, `PCI_MSU_COUNT`, `PCI_CTL_EN`, `PCI_CTL_TNR`, `PCI_CTL_SCE`, `PCI_CTL_IEN`, `PCI_CTL_AAA`, `PCI_CTL_EAP`, `PCI_CTL_PCIM_BIT`, `PCI_CTL_PCIM`, `PCI_CTL_PCIM_DIS`, `PCI_CTL_PCIM_TNR`, `PCI_CTL_PCIM_SUS`, `PCI_CTL_PCIM_EXT`, `PCI_CTL`, `PCI_CTL_PCIM_RR`, `PCI_CTL_PCIM_RSVD6`, `PCI_CTL_PCIM_RSVD7`, `PCI_CTL_IGM`, `PCI_STAT_EED`, `PCI_STAT_WR`, and 251 more; 3 structs: `pci_map`, `pci_reg`, `pci_msu`; 0 enums: none; 0 callable helpers/prototypes: none; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
The file is declarative: platform code casts MMIO bases or firmware memory to structs such as `pci_map`, `pci_reg`, `pci_msu` and then performs reads/writes through the documented fields and masks.

## State and Persistence Behavior
The file does not allocate storage. It defines the shape of hardware or firmware state that persists outside the header: memory-mapped registers, descriptor rings, NVRAM/boot parameter blocks, board-control registers, or platform data passed into registered devices.

## Dependencies and Integration Points
Direct includes are no direct includes. Major macro families are `PCI_CFGA (30)`, `PCI_CFG04 (18)`, `PCI_STAT (18)`, `PCI_STATM (18)`, `PCI_CTL (17)`, `PCI_PBAC (14)`, `PCI_DMAD (10)`, `PCI_LBAC (9)`. Typed contracts include `pci_map`, `pci_reg`, `pci_msu`. Callable helpers or declarations include no inline/prototype helpers. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; the file contains 278 macros, so broad edits have high review cost and should be grouped by register block or bit-field family; register or firmware structs must preserve field order, width, padding, volatility expectations, and endianness.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-rc32434/pci.h -->
