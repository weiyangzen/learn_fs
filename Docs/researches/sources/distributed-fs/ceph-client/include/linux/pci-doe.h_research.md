# Research: sources/distributed-fs/ceph-client/include/linux/pci-doe.h

Purpose: `pci-doe.h` exposes the PCIe Data Object Exchange mailbox API used by protocols such as discovery, CMA, secure sessions, and TSM/IDE flows.

Important APIs/types/functions: `struct pci_doe_mb` is opaque. Feature constants identify DOE discovery, CMA, and secure-session protocols. `pci_find_doe_mailbox()` locates a mailbox by vendor and type, and `pci_doe()` performs a request/response exchange with caller-provided buffers.

Control flow and state: a caller discovers an appropriate mailbox, then submits typed DOE messages. The implementation serializes mailbox access and copies responses into the caller buffer. State is in the opaque mailbox and PCI DOE capability registers.

Dependencies and integration points: depends on PCI device declarations and integrates with PCI capability scanning, SPDM/CMA, PCI TSM, IDE, and vendor-specific protocols.

Risks and test signals: risks include buffer size mismatch, mailbox busy/timeouts, protocol type confusion, and use after device removal. Tests should cover mailbox discovery, malformed response lengths, timeout/error paths, concurrent callers, and protocol-specific DOE exchanges.
