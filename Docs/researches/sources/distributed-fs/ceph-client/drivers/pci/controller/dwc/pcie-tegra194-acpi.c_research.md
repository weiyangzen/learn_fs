## sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-tegra194-acpi.c

Purpose: ACPI ECAM quirk implementation for Tegra194 PCIe host controllers. It adapts an ACPI `pci_config_window` into separate config, iATU, and DBI regions and programs outbound iATU windows before non-root config accesses.

Important APIs, types, and functions: `struct tegra194_pcie_ecam` stores `config_base`, `iatu_base`, and `dbi_base`. `tegra194_acpi_init()` allocates that structure, assigns `cfg->win`, `cfg->win + SZ_256K`, and `cfg->win + SZ_512K`, and stores it in `cfg->priv`. `program_outbound_atu()` writes unrolled DWC outbound ATU registers for base, target, limit, type, and enable. `tegra194_map_bus()` routes root bus device 0 accesses to DBI, rejects other root slots and nonzero direct-child slots, programs CFG0 for the direct downstream device or CFG1 for deeper buses, and returns `config_base + where`. `tegra194_pcie_ops` exposes init/map/read/write via `pci_ecam_ops`.

Control flow: PCI core calls ECAM init during host creation. For each config access, `map_bus()` validates bus range and topology, programs ATU index 0 for the requested bus/device/function, then returns a window address used by generic config read/write.

State and persistence: state is in `cfg->priv` and transient iATU register programming. The same outbound region is reprogrammed per access. No persistent storage exists.

Dependencies and integration points: ACPI PCI host infrastructure, generic PCI ECAM ops, DesignWare iATU register definitions from `pcie-designware.h`, and PCI topology assumptions matching Tegra194 host layout.

Risks: ATU region 0 is shared across accesses and relies on PCI config serialization. Incorrect ACPI window layout breaks all offsets. The mapper deliberately filters unsupported slots, so firmware topology descriptions must match the one-device downstream assumption.

Test signals: ACPI boot should enumerate root port via DBI, discover the direct endpoint using CFG0, enumerate subordinate bridges using CFG1, reject invalid slots cleanly, and show stable config access under concurrent enumeration.
