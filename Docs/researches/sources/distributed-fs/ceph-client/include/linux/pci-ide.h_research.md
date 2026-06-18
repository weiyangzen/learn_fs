# Research: sources/distributed-fs/ceph-client/include/linux/pci-ide.h

Purpose: `pci-ide.h` declares helpers for PCIe Integrity and Data Encryption key-management/stream setup, shared by low-level PCI and TSM drivers implementing IDE_KM.

Important APIs/types/functions: `enum pci_ide_partner_select` identifies endpoint, root port, and host-bridge stream pools. `struct pci_ide_partner` stores RID ranges, stream index, memory/prefetchable address associations, and setup/enable flags. `struct pci_ide_regs` holds computed RID/address association registers. `struct pci_ide` tracks endpoint device, partner settings, host bridge stream, stream ID, and sysfs name. APIs set host-bridge stream counts, resolve settings, allocate/free/register/unregister/setup/teardown/enable/disable/release streams, and provide a cleanup helper via `DEFINE_FREE`.

Control flow and state: callers allocate a stream descriptor, optionally adjust partner address ranges, register it, program setup, enable IDE, then disable/teardown/free on release. State tracks whether setup and enable occurred per partner so teardown can be conditional and ordered.

Dependencies and integration points: depends on PCI devices, host bridges, bus regions, TSM-established IDE flows, sysfs naming, and cleanup attributes. It integrates with `pci-tsm.h` link security and PCIe IDE capability programming.

Risks and test signals: risks include leaked stream IDs, mismatched RID/address association, enabling without setup, teardown omissions, and wrong default stream handling. Tests should cover allocation exhaustion, endpoint/root-port/host-bridge pairing, register conversion, setup/enable/disable ordering, cleanup helper behavior, and TSM-owned stream IDs.
