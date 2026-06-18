# sources/distributed-fs/ceph-client/drivers/pci/controller/cadence/Kconfig

Purpose: Cadence PCIe controller configuration menu for shared core infrastructure, host mode, endpoint mode, generic platform wrappers, and vendor-specific Cadence-based controllers.

Important symbols: `PCIE_CADENCE` is shared infrastructure; `PCIE_CADENCE_HOST` depends on OF, selects IRQ domains and shared core; `PCIE_CADENCE_EP` depends on OF and PCI endpoint; `PCIE_CADENCE_PLAT_HOST` and `_EP` select platform and relevant host/EP support. Vendor options include `PCI_SKY1_HOST` selecting HPA/Cadence host plus ECAM, `PCIE_SG2042_HOST`, and TI `PCI_J721E` with separate host and endpoint options selecting Cadence host/EP as needed.

Control flow/state: selected symbols drive `cadence/Makefile` multi-object modules for common core, host common/host/HPA, endpoint, platform wrapper, J721E, SG2042, and SKY1. Host and endpoint modes can be built independently when dependencies permit.

Dependencies/integration: integrates OF probing, PCI endpoint framework, IRQ domain support, Cadence common code, and architecture/vendor compile-test gates. Risks include host/endpoint symbol interactions, missing endpoint dependency in vendor EP choices, and subtle sharing between first/second generation Cadence HPA code. Test signals include host and EP build matrices, DT binding probe tests, endpoint framework registration, and vendor SoC boot enumeration.
