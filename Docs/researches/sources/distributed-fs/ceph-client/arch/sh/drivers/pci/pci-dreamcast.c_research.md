# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/pci-dreamcast.c



Source read size: 97 lines, 2339 bytes.



Purpose: initializes and registers the Dreamcast GAPSPCI host bridge for the Sega Broadband Adapter.

Important APIs/types/functions: `gapspci_init()`, `dreamcast_pci_controller`, GAPSPCI resource windows, register handshake at `GAPSPCI_REGS`, and BBA config initialization.

Control flow: verifies the bridge ID string, performs a magic unlock/handshake, programs DMA window registers, enables the bridge and BBA config registers, then registers one PCI controller.

State and persistence: GAPSPCI bridge registers, BBA config space, resource reservations, and controller registration persist after arch init.

Dependencies and integration points: depends on Dreamcast `mach/pci.h`, `gapspci_pci_ops`, `fixups-dreamcast.c`, and SH PCI core.

Risks and test signals: undocumented magic values and busy-wait timing are hardware-specific; only the BBA is supported. Test boot with and without BBA, bridge ID mismatch, and resource fixup/DMA coherent allocation.
