# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-hisi.c

Purpose: This file implements HiSilicon HIP06/HIP07 "almost ECAM" PCIe configuration-space access. It supplies custom `pci_ecam_ops` for platforms where the Root Port's own config space is mapped through a separate RC base while downstream buses use regular ECAM.

Important APIs, types, and functions: `struct hisi_pcie` stores the Root Complex register base. Config accessors are `hisi_pcie_map_bus()`, `hisi_pcie_rd_conf()`, and `hisi_pcie_wr_conf()`. ACPI initialization is `hisi_pcie_init()` and exports `const struct pci_ecam_ops hisi_pcie_ops`. Device-tree platform initialization is `hisi_pcie_platform_init()` with `hisi_pcie_platform_ops` passed to `pci_host_common_probe()`.

Control flow: For config accesses on the root bus, map returns `pcie->reg_base + where` and read/write restrict access to slot 0 using the 32-bit generic accessors. For subordinate buses, map/read/write delegate to standard ECAM helpers. ACPI init allocates state, finds RC resources from a `HISI0081` ACPI device with matching segment, remaps config space, and stores it in `cfg->priv`. DT init maps `reg[1]` as the RC base and stores it in `cfg->priv`. The platform driver matches HIP06/HIP07 ECAM compatibles and delegates probe to the common PCI host driver.

State and persistence behavior: State is limited to `cfg->priv` and the remapped RC base for the lifetime of the PCI config window. There is no durable state and no DWC runtime resource sequencing in this file.

Dependencies and integration points: Integrates with Linux PCI ECAM, ACPI PCI root/resource quirks, `pci-host-common`, platform resources, and generic PCI config-space accessors. It does not include `pcie-designware.h` because it operates at the ECAM access layer rather than through the DWC host core.

Risks: Root bus slot filtering is essential; exposing nonzero devices on the root bus would create fake config devices. ACPI resource lookup must match the segment or config space maps the wrong controller. The root port requires 32-bit config accessors while downstream ECAM can use normal width accesses; mixing those paths can break config cycles. The code is compiled under conditional ACPI/DT Kconfig combinations, so declarations must remain guarded consistently.

Test signals: Test HIP06/HIP07 DT and ACPI boot, root bus slot 0 read/write, root bus nonzero slot returning device-not-found, downstream ECAM enumeration, ACPI segment matching, missing `reg[1]` failure, and common host probe integration.
