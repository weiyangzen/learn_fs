# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-sh7751.c



Source read size: 179 lines, 5343 bytes.



Purpose: low-level PCI host controller initialization for SH7751/SH7751R.

Important APIs/types/functions: `sh7751_pci_init()`, `__area_sdram_check()`, `sh7751_pci_controller`, `sh7751_pci_map`, `pci_fixup_pcic()`, and SH7751 BCR/WCR/MCR/PCICONF registers.

Control flow: verifies controller vendor/device ID, enables PCI access in BCR, wakes clocks, clears powerdown IRQs, sets command/class/window registers, mirrors SDRAM timing into PCIC registers, applies board fixups, marks central-function init complete, and registers the controller.

State and persistence: PCIC registers, BSC mirror registers, memory/I/O windows, and PCI controller resource state persist for runtime PCI.

Dependencies and integration points: depends on `pci-sh4.h`, SH7751 register definitions, board `pci_fixup_pcic()` implementations, and generic SH PCI core.

Risks and test signals: SDRAM area validation and one-to-one window assumptions are strict; wrong BCR/WCR values can break memory or PCI. Test SH7751 boards, resource windows, config cycles, and board fixup variants.
