<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h -->
# sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h

## Purpose
`sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h` describes low-level controller registers and helper macros for `mach-loongson2ef/cs5536`. It is part of the Ceph client's vendored Linux MIPS architecture tree, so its main consumers are kernel architecture and board-support code rather than Ceph filesystem logic.

## Important APIs, Types, and Functions
The exported surface is 64 macros including `_CS5536_PCI_H`, `CS5536_ACC_INTR`, `CS5536_IDE_INTR`, `CS5536_USB_INTR`, `CS5536_MFGPT_INTR`, `CS5536_UART1_INTR`, `CS5536_UART2_INTR`, `PCI_BUS_CS5536`, `PCI_IDSEL_CS5536`, `CFG_PCI_VENDOR_ID`, `CS5536_VENDOR_ID`, `CS5536_ISA_DEVICE_ID`, `CS5536_IDE_DEVICE_ID`, `CS5536_ACC_DEVICE_ID`, `CS5536_OHCI_DEVICE_ID`, `CS5536_EHCI_DEVICE_ID`, `CS5536_ISA_CLASS_CODE`, `CS5536_IDE_CLASS_CODE`, `CS5536_ACC_CLASS_CODE`, `CS5536_OHCI_CLASS_CODE`, `CS5536_EHCI_CLASS_CODE`, `CFG_PCI_CACHE_LINE_SIZE`, `PCI_NONE_BIST`, `PCI_BRIDGE_HEADER_TYPE`, and 40 more; 0 structs: none; 0 enums: none; 15 callable helpers/prototypes: `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, `pci_isa_write_bar`, `pci_isa_read_bar`, `pci_isa_write_reg`, `pci_isa_read_reg`, and 1 more; 0 extern variables: none. These names form a C preprocessor and layout contract for downstream architecture code, board files, and low-level drivers.

## Control Flow
Control flow is concentrated in inline/prototype helpers such as `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, and 5 more. Callers include this header and execute the inline range checks, MMIO accessor wrappers, reset/timer calls, DMA start/stop helpers, or board accessors directly in their platform setup path.

## State and Persistence Behavior
The header itself persists no data, but its helpers touch hardware-visible state: MMIO mappings, I/O port byte order, DMA engine registers, timer/reset controls, RTC cells, IRQ enables, or allocation alignment. Any persistent effects are in hardware registers, firmware-provided memory, or kernel subsystem state owned by callers.

## Dependencies and Integration Points
Direct includes are `linux/init.h`, `linux/types.h`, `linux/pci_regs.h`. Major macro families are `PCI_IDE (6)`, `CS5536_IDE (5)`, `CS5536_ACC (4)`, `CFG_PCI (3)`, `CS5536_EHCI (3)`, `CS5536_ISA (3)`, `CS5536_OHCI (3)`, `PCI_EHCI (3)`. Typed contracts include no structs. Callable helpers or declarations include `cs5536_pci_conf_write4`, `cs5536_pci_conf_read4`, `pci_ehci_write_reg`, `pci_ehci_read_reg`, `pci_ide_write_reg`, `pci_ide_read_reg`, `pci_acc_write_reg`, `pci_acc_read_reg`, `pci_ohci_write_reg`, `pci_ohci_read_reg`, `pci_isa_write_bar`, `pci_isa_read_bar`, and 3 more. Integration is via the MIPS machine include selection, board setup code under `arch/mips`, and platform or bus drivers that consume these constants when registering devices or accessing MMIO. The main dependency class is platform drivers, PCI host setup, DMA/Ethernet descriptors, GPIO/pinctrl, memory controller setup, and board initialization.

## Risks
packed register structs and bit masks must match silicon manuals and expected endianness exactly; 64-bit, NUMA, or firmware-specific assumptions make cross-configuration compile testing important.

## Test Signals
build the affected MIPS defconfig/allmodconfig with this machine selected; run sparse/compile checks for include users after changing exported structs or prototypes; exercise DMA, Ethernet, and PCI traffic with descriptor/status error logging enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/include/asm/mach-loongson2ef/cs5536/cs5536_pci.h -->
