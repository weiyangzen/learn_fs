# Research: sources/distributed-fs/ceph-client/include/linux/pci-ats.h

Purpose: `pci-ats.h` declares PCI Address Translation Service, Page Request Interface, and PASID helper APIs with config-dependent stubs.

Important APIs/types/functions: ATS functions include support query, enable, prepare, disable, queue depth, and page-alignment query. PRI functions include enable, disable, reset, PRG response PASID requirement, and support query. PASID functions include enable, disable, feature query, maximum PASIDs, and status.

Control flow and state: callers check support, configure queue/page-size parameters, enable translation or request features, and disable them during teardown. When the relevant kernel config is off, most APIs return `-ENODEV`, `-EINVAL`, false, or no-op so callers can compile while feature paths remain disabled.

Dependencies and integration points: depends on `linux/pci.h`; integrates with IOMMU/SVA, device drivers using PASID, PCI capabilities, and virtualization or accelerator drivers.

Risks and test signals: risks include enabling ATS without IOMMU support, PASID feature mismatch, queue-depth misuse, and callers ignoring stub errors. Tests should cover config-off stubs, capability discovery, enable/disable ordering, IOMMU interaction, reset behavior, and device removal cleanup.
