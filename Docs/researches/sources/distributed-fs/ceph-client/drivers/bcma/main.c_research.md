# sources/distributed-fs/ceph-client/drivers/bcma/main.c

Purpose: defines the BCMA Linux bus type and core lifecycle. It registers `struct bcma_device` objects discovered by the scanner, handles matching/probe/remove/uevent for BCMA drivers, initializes built-in cores in dependency order, exposes driver registration APIs, and wires module initialization for SoC and PCI hosts.

Important APIs and functions: `bcma_find_core_unit()` searches discovered cores by ID and unit. `bcma_wait_value()` polls core registers with timeout. `bcma_core_irq()` resolves IRQs for PCI, SoC MIPS, or OF-backed cores. `bcma_prepare_core()` initializes the embedded Linux device and DMA/IRQ fields. `bcma_init_bus()` assigns bus numbers and detects chip ID. `bcma_bus_register()` performs full scan, early chipcommon/PCI init, SPROM retrieval, core-specific initialization, and device registration. `bcma_bus_early_register()` is a non-sleeping early SoC variant. `__bcma_driver_register()` and `bcma_driver_unregister()` are exported for BCMA client drivers.

Control flow: full registration scans cores, initializes chipcommon early, initializes PCIe early for SPROM needs, populates OF children, registers NAND/QSPI early cores, retrieves SPROM, initializes chipcommon/chipcommon-B/MIPS/PCIe/PCIe2/GBIT common cores, then registers remaining externally driven cores. Unregister reverses GPIO, chipcommon-B, registered device, watchdog, and internal core state. Bus matching compares manufacturer, id, rev, and class against driver id tables with wildcard support.

State and persistence: global `bcma_bus_next_num` is protected by `bcma_buses_mutex`. Each bus owns a `cores` list, chipinfo, host fields, driver substructures, and Linux device registration flags. Per-core device lifetime is managed by `bcma_release_core_dev()`; mapped MMIO is unmapped there.

Dependencies and integration points: integrates with `scan.c`, `sprom.c`, chipcommon, MIPS, PCI/PCIe core drivers, GPIO/watchdog/flash platform devices, OF population, Linux driver core, and module init/exit. Host init functions are called for SoC always and PCI under `CONFIG_BCMA_HOST_PCI`.

Risks: registration ordering is critical because SPROM depends on early chipcommon/PCI and flash cores. Error handling logs many failures but may continue, e.g. missing SPROM. Device lifetime mixes registered and internally handled cores, making teardown sensitive. Test signals include module init, BCMA modalias generation, driver bind/unbind, suspend/resume callbacks, SPROM availability, and device-tree child matching.
