<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h

Purpose: This private header exposes zPCI SR-IOV helper APIs with real declarations under `CONFIG_PCI_IOV` and no-op/error stubs otherwise.

Important APIs/types/functions: It declares or stubs `zpci_iov_remove_virtfn`, `zpci_iov_map_resources`, `zpci_iov_setup_virtfn`, and `zpci_iov_find_parent_pf`.

Control flow: Bus code includes this header unconditionally. With IOV enabled, VF setup/removal and resource mapping perform real work; without it, callers compile away VF support and `zpci_iov_setup_virtfn`/`find_parent_pf` report failure/NULL.

State and persistence: The header owns no state. Its stubs define behavior for configurations where SR-IOV is unavailable.

Dependencies and integration points: It depends on `struct pci_dev`, `struct zpci_bus`, and `struct zpci_dev`, and integrates `pci_bus.c` with `pci_iov.c` conditionally.

Risks and test signals: Stub return values must keep non-IOV builds safe: a zPCI VF in such a build should fail setup rather than being partially linked. Build tests should cover `CONFIG_PCI_IOV=y` and `n`; runtime tests should cover VF setup only on IOV builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_iov.h -->
