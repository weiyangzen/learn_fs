# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-al.c

Purpose: Provides Amazon Annapurna Labs PCIe support in two forms: an ACPI ECAM quirk path for root-complex DBI access and a DT platform driver for Alpine/Graviton-style DWC host controllers with controller-specific config-window target-bus programming.

Important APIs and types: Under ACPI quirks, `struct al_pcie_acpi`, `al_pcie_init()`, and `al_pcie_map_bus()` implement `const struct pci_ecam_ops al_pcie_ops`. Under `CONFIG_PCIE_AL`, `struct al_pcie` stores DWC/root-port state, controller register base, ECAM size, revision, register offsets, and target-bus cache. Key functions are `al_pcie_rev_id_get()`, `al_pcie_reg_offsets_set()`, `al_pcie_target_bus_set()`, `al_pcie_conf_addr_map_bus()`, `al_pcie_config_prepare()`, `al_pcie_host_init()`, and `al_pcie_probe()`.

Control flow: The ACPI path obtains the root-complex DBI resource via `acpi_get_rc_resources()` and maps root-bus slot 0 accesses to DBI while all other buses use normal ECAM. The DT path maps the `config` and `controller` resources, marks native ECAM, runs DWC host init, detects controller revision from device ID bits, chooses register offsets, computes how many bus bits are represented in the ECAM address versus the controller target-bus register, programs the target-bus mask/value and secondary/subordinate bus numbers, and installs child config ops that update the target-bus register when crossing bus ranges.

State and persistence: Hardware state includes the controller outbound-control target bus and secondary/subordinate bus fields. Driver state caches revision-derived offsets, ECAM size, and current target-bus register value. ACPI state is kept in `cfg->priv`.

Dependencies and integration points: Depends on Linux PCI ECAM, ACPI root resources, optional `CONFIG_PCI_QUIRKS`, DWC host core, and DT resources. The platform driver delegates standard resource/iATU/link setup to `dw_pcie_host_init()` but overrides child config mapping.

Risks: Bus-number split logic depends on ECAM window size and 256-bus maximum assumptions; bad firmware resources can misroute config cycles. Revision detection only recognizes x4/x8/x16 encoded device IDs. The ACPI root bus filter intentionally rejects functions/devices other than slot 0, matching DWC root-port behavior. Incorrect target-bus cache updates would create intermittent config access failures.

Test signals: ACPI boot with `AMZN0001` root resources, DT boot on Alpine v2/v3, root-bus slot filtering, enumeration beyond one bus, target-bus register changes during config scans, revision-specific outbound-control offsets, large ECAM warning behavior, and config reads across secondary/subordinate ranges.
