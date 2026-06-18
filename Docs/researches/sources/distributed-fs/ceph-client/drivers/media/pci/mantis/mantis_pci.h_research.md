# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_pci.h

- Purpose: Declaration header for Mantis PCI resource lifecycle.
- Important APIs/types/functions: `mantis_pci_init` and `mantis_pci_exit`.
- Control flow: Probe/remove call these around all higher-level subsystems.
- State and persistence: No state; operates on `struct mantis_pci`.
- Dependencies and integration points: Integrates `mantis_cards.c` with low-level PCI implementation.
- Risks: Header must stay synchronized with exported implementation.
- Test signals: Compile/link plus probe/remove tests.
