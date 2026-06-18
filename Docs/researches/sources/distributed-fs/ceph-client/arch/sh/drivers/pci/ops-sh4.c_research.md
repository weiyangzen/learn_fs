# sources/distributed-fs/ceph-client/arch/sh/drivers/pci/ops-sh4.c



Source read size: 105 lines, 2385 bytes.



Purpose: generic SH4/SH4A PCI configuration-space access for SH7751 and SH7780-family PCIC controllers.

Important APIs/types/functions: `sh4_pci_ops`, `sh4_pci_read()`, `sh4_pci_write()`, `CONFIG_CMD()`, global `pci_config_lock`, and weak `pci_fixup_pcic()`.

Control flow: read writes PCIPAR with type-1 config address, reads PCIPDR under raw spinlock, then extracts byte/word/dword fields. Write performs a read-modify-write for sub-dword sizes because PCIPDR only supports 32-bit accesses.

State and persistence: serializes hardware config access through `pci_config_lock`; writes mutate device/controller PCI config space.

Dependencies and integration points: used by SH7751/SH7780 host setup, board `pci_fixup_pcic()` overrides, and generic PCI enumeration.

Risks and test signals: unaligned subword writes rely on correct endian/shift math; weak fixup must be replaced on boards requiring PCIC setup. Test config byte/word/dword accesses and board-specific fixups.
