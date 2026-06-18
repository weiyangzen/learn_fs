# sources/distributed-fs/ceph-client/drivers/bcma/host_pci.c

Purpose: implements the BCMA host adapter for Broadcom PCIe cards. It registers a PCI driver for supported Broadcom IDs, maps BAR0, provides BCMA core read/write operations over PCI BAR windows, scans/registers the BCMA bus, and exposes runtime PCI up/down and interrupt-routing controls to BCMA client drivers.

Important APIs and functions: `bcma_host_pci_switch_core()` programs `BCMA_PCI_BAR0_WIN` and a wrapper window, recording `bus->mapped_core`. `bcma_host_pci_provide_access_to_core()` uses fixed windows for chipcommon and PCIe cores and dynamic switching for others. The `bcma_host_pci_read/write{8,16,32}` and optional block I/O functions implement `struct bcma_host_ops`. `bcma_host_pci_probe()` owns PCI enablement, region request, BAR mapping, bus initialization, scan, and register. `bcma_host_pci_remove()` unwinds it. `bcma_host_pci_up()`, `bcma_host_pci_down()`, and exported `bcma_host_pci_irq_ctl()` are runtime integration hooks.

Control flow: PCI probe allocates a `bcma_bus`, enables and requests the PCI device, disables retry timeout, rejects non-PCIe cards, maps BAR0, initializes bus host fields and board info, scans cores, marks PCIe2 presence, registers BCMA devices, and stores bus drvdata. Remove unregisters BCMA devices before unmapping and disabling PCI resources. Suspend clears the mapped-core cache and delegates to `bcma_bus_suspend()`, while resume delegates to `bcma_bus_resume()`.

State and persistence: important state includes `bus->host_pci`, `bus->mmio`, `bus->host_is_pcie2`, `bus->mapped_core`, board vendor/type, and PCI drvdata. The interrupt mask in PCI config space is modified by `bcma_host_pci_irq_ctl()`.

Dependencies and integration points: Linux PCI driver core, module IDs, BAR ioread/iowrite APIs, optional `CONFIG_BCMA_BLOCKIO`, BCMA bus scan/register APIs from `main.c` and `scan.c`, and PCI/PCIe core runtime APIs from `driver_pci.c`/`driver_pcie2.c`.

Risks: window switching is global to the bus and protected only by expected upper-layer serialization; concurrent core accesses would be risky if host ops users do not serialize. Supported device IDs are static. Non-PCIe BCMA cards are rejected. Test signals include PCI probe/remove, suspend/resume, correct fixed/dynamic window access, IRQ mask toggling, and module alias matching for supported Broadcom IDs.
