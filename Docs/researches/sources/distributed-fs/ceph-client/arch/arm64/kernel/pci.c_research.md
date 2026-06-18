# sources/distributed-fs/ceph-client/arch/arm64/kernel/pci.c

Purpose: Supplies arm64 platform-independent raw PCI config access wrappers and optional NUMA node lookup.

Important APIs: `raw_pci_read()` and `raw_pci_write()` find the `pci_bus` by domain and bus, then delegate to the bus operations. Under `CONFIG_NUMA`, `pcibus_to_node()` returns `dev_to_node(&bus->dev)` and is exported.

Control flow and state: no persistent state. Missing buses return `PCIBIOS_DEVICE_NOT_FOUND`; otherwise operation return codes come from host bridge ops.

Dependencies and integration: depends on the PCI core, host bridge config access callbacks, domain/bus enumeration, and NUMA device topology. It is used by generic PCI code paths expecting arch raw accessors.

Risks and test signals: risks are null bus ops from malformed host controllers, incorrect domain lookup, and NUMA node mismatch. Test with PCI ECAM and non-ECAM host bridges, multi-domain systems, hotplug, and NUMA topology checks.
