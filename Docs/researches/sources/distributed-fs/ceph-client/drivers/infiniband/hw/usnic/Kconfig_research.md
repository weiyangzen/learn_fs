# sources/distributed-fs/ceph-client/drivers/infiniband/hw/usnic/Kconfig

Purpose: Kconfig entry enabling Cisco VIC usNIC verbs support as `INFINIBAND_USNIC`.

Important symbols: `INFINIBAND_USNIC` is a tristate "Verbs support for Cisco VIC". It depends on networking, Ethernet, INET, PCI, Intel IOMMU, and `INFINIBAND_USER_ACCESS`; it selects Cisco ENIC, Cisco net vendor support, and PCI SR-IOV.

Control flow: when selected, the kernel build includes the usNIC low-level RDMA driver for Cisco VIC 1240/1280-style devices. Without the dependencies, the driver is not offered.

State and persistence: no runtime state; it controls build configuration.

Dependencies and integration: integrates the RDMA driver with the Cisco ENIC netdev stack, PCI IOV, and user-access RDMA infrastructure. The Intel IOMMU dependency matches the driver's explicit IOMMU-domain memory mapping model.

Risks: the hard `INTEL_IOMMU` dependency excludes non-Intel IOMMU platforms even if generic IOMMU APIs could theoretically support them. Missing `INFINIBAND_USER_ACCESS` would break the uverbs-only design.

Test signals: `olddefconfig`, `allyesconfig`/module builds, dependency resolution with ENIC/PCI_IOV, and boot probe on VIC hardware with IOMMU enabled.
