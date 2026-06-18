# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh4.h



Source read size: 182 lines, 9591 bytes.



Purpose: common SH4 PCIC register definitions, register access helpers, and controller address-map structures shared by SH7751 and SH7780-family PCI code.

Important APIs/types/functions: SH4_PCICR/PCIINT/PCIAINT/DMA/config/I/O register offsets and bit masks, `struct sh4_pci_address_space`, `struct sh4_pci_address_map`, `pci_read_reg()`, `pci_write_reg()`, `sh4_pci_ops`, and `pci_fixup_pcic()` declaration.

Control flow: no direct flow; host-controller and ops files include this header to issue raw MMIO register accesses and interpret status/error bits.

State and persistence: constants map to live PCIC hardware state; inline helpers mutate controller registers.

Dependencies and integration points: conditionally includes SH7751 or SH7780-specific headers and depends on `asm/io.h`.

Risks and test signals: common offsets must match each CPU subtype include; wrong bit masks break reset, error handling, DMA, or config access. Test SH7751/SH7780 builds and PCI enumeration/error handling.
