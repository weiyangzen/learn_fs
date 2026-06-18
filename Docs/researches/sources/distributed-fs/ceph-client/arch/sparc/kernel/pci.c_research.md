# sources/distributed-fs/ceph-client/arch/sparc/kernel/pci.c

Purpose: Implements UltraSPARC PCI controller support around Open Firmware bus scanning, config-space pokes, PBM root-bus creation, resource claiming, MSI hooks, DMA quirks, and slot naming.

Important APIs/types/functions: Globals `pci_pbm_root` and `pci_num_pbms` track PBM controllers. `pci_config_read{8,16,32}()` and `pci_config_write{8,16,32}()` perform protected physical-bypass config accesses with `pci_poke_*` fault tracking. OF scan helpers include `pci_parse_of_flags()`, `pci_parse_of_addrs()`, `of_create_pci_dev()`, `of_scan_pci_bridge()`, `pci_of_scan_bus()`, `pci_scan_one_pbm()`, and `pci_bus_register_of_sysfs()`. Other exported/arch hooks include `pci_iobar_pfn()`, `pcibus_to_node()`, `pci_domain_nr()`, `arch_setup_msi_irq()`, `arch_teardown_msi_irq()`, `ali_sound_dma_hack()`, `pci_resource_to_user()`, `pcibios_device_add()`, and slot-name init helpers.

Control flow: Controller-specific PBM code calls `pci_scan_one_pbm()`, which creates a root bus with PBM resource windows, recursively creates PCI devices from OF child nodes, scans bridges, registers `obppath` sysfs files, claims firmware-assigned resources, and adds devices. Bridge scanning parses `bus-range` and `ranges`, with Simba fallback ranges when firmware omits them. Config accesses set global poke state so low-level fault handling can suppress failed reads.

State and persistence: Persistent state includes PBM lists/indexes, PCI device/resource trees, sysfs `obppath` files, slot objects, and global poke fault flags guarded by `pci_poke_lock`. MSI setup delegates to per-PBM callbacks.

Dependencies and integration points: It depends on OF platform devices produced by `of_device_64.c`, PBM internals from `pci_impl.h`, generic PCI core, MSI descriptors, IRQ subsystem, APB/Simba bridge definitions, IOMMU archdata, NUMA, and SR-IOV hooks.

Risks and test signals: Config poke globals are volatile and serialized only by `pci_poke_lock`; fault handling must respect `pci_poke_cpu`. Firmware quirks such as duplicate OF devices, bogus bridge sizes, missing Simba ranges, and ALI DMA masks are explicitly handled. Tests include PBM scan on UltraSPARC systems, absent-device config reads, bridge resource windows, duplicate OF node suppression, VGA legacy claims, MSI setup/teardown, ALI sound DMA quirk, SR-IOV VF archdata copy, user resource addresses, and slot-name creation.
