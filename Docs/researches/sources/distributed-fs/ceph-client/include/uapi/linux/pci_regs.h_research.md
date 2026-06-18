# sources/distributed-fs/ceph-client/include/uapi/linux/pci_regs.h

Purpose: Defines standard PCI, PCI-X, PCIe, extended capability, CXL DVSEC, DOE, IDE, and related configuration-space register offsets, bit masks, and helper macros.

Important APIs/types/functions: Exports constants for conventional config space size, standard header fields, BARs, bridge/CardBus headers, capability IDs, PM, AGP, VPD, MSI/MSI-X, PCI-X, HyperTransport, PCI Express capabilities/control/status/link/slot/root/AER/VC/ACS/SR-IOV/ATS/PRI/PASID/TPH/DPC/PTM/L1SS/DOE/IDE, Enhanced Allocation, Resizable BAR, NPEM, DVSEC accessors, and CXL DVSEC register blocks. Helper-style macros include field extractors such as `PCI_DVSEC_HEADER1_VID(x)` and indexed offsets for IDE/CXL ranges.

Control flow: No runtime flow. PCI core, drivers, and userspace tools use these offsets and masks to read, write, decode, and validate PCI configuration space and capability lists.

State and persistence behavior: The header describes hardware configuration state. Writes by consumers can change device enablement, bus mastering, BARs, power states, MSI/MSI-X, PCIe link behavior, AER status, SR-IOV, DPC, PTM, IDE, or CXL memory enablement, but the header itself stores nothing.

Dependencies and integration points: It is included by `<linux/pci.h>` and many drivers/tools. Integrates with PCI core enumeration, pciutils, sysfs config access, hotplug, virtualization/IOMMU, CXL, DOE protocols, and security features such as ACS and IDE.

Risks: Register definitions must match evolving PCI-SIG specifications. Incorrect masks or offsets can cause device misconfiguration, broken enumeration, disabled interrupts, link instability, or security boundary failures. Some macros use bit-generation helpers expected from kernel-style includes, so userspace header installation must provide compatible definitions.

Test signals: Build broad PCI driver/userspace consumers, compare offsets against spec and pciutils decoding, run PCI config-space selftests, validate capability walking on real and virtual devices, test MSI/MSI-X and AER/DPC paths, and verify CXL/DOE/IDE definitions against supported hardware.
