## sources/distributed-fs/ceph-client/drivers/pci/controller/pci-host-common.c

Purpose: Common library for simple ECAM/CAM PCI host controller drivers. It maps config space, initializes a generic host bridge, and provides a shared remove path.

Important APIs, types, and functions: `pci_host_common_ecam_create()` parses the first `reg` resource from OF, locates the bus range in `bridge->windows`, creates a `pci_config_window` with supplied `pci_ecam_ops`, and registers `pci_ecam_free()` via devm action. `pci_host_common_init()` calls `of_pci_check_probe_only()`, stores bridge drvdata, creates ECAM, assigns `bridge->sysdata`, ops, optional enable/disable callbacks, marks MSI domain support, and calls `pci_host_probe()`. `pci_host_common_probe()` gets match data as `pci_ecam_ops`, allocates a host bridge, and delegates init. `pci_host_common_remove()` stops and removes the root bus under rescan/remove locking.

Control flow: generic platform drivers provide only OF match data containing ECAM ops. Probe allocates bridge and calls common init; remove tears down the scanned bus.

State and persistence: volatile state includes devm-managed ECAM config window, host bridge drvdata, root bus, and bridge ops. No persistent state.

Dependencies and integration points: OF address and PCI parsing, PCI ECAM library, platform driver infrastructure, and host bridge core.

Risks: Requires a valid bus resource in `bridge->windows`; missing bus range returns `-ENODEV`. The cast from `ops->pci_ops` to `struct pci_ops *` assumes lifetime and constness are safe. MSI domain is unconditionally true for common hosts.

Test signals: generic ECAM/CAM host probes, malformed `reg` rejection, missing bus range rejection, ECAM free on probe failure/remove, and clean root bus removal.
