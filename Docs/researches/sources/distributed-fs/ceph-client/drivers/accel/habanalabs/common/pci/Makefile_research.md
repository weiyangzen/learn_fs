# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/common/pci/Makefile

Purpose: contributes the common Habanalabs PCI support object to the driver build.

Important APIs/types/functions: defines `HL_COMMON_PCI_FILES := common/pci/pci.o`. There are no runtime functions, variables, or generated artifacts in this Makefile.

Control flow: the parent Habanalabs build includes this variable when composing the complete module object list, causing `common/pci/pci.c` to be compiled into the driver.

State and persistence behavior: no runtime state or persistence; this is build metadata only.

Dependencies and integration points: depends on the surrounding kernel Kbuild fragments that collect `HL_COMMON_PCI_FILES`. It integrates `hl_pci_init()`, BAR mapping, ELBI, iATU, and DMA setup code into the Habanalabs module.

Risks and test signals: the only meaningful risk is build composition drift if `pci.o` is omitted or renamed. Test signals are kernel/module builds with Habanalabs enabled and link failures for common PCI symbols.
