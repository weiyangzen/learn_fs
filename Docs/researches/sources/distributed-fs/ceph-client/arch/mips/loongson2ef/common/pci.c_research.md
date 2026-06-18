<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c

Purpose: Sets up Loongson2EF PCI memory/IO resources, CPU-to-PCI mappings, and PCI-DMA hit windows.

Important APIs/types/functions: `setup_pcimap()` writes Loongson PCI map, base, hit selector, arbitration, and optional address-window registers. `loongson2ef_pcibios_init()` registers the `pci_controller`.

Control flow: Initializes CPU windows for PCI memory, maps PCI DMA from 2G to low memory, disables unused hit windows, applies deadlock/arbitration workarounds, sets `PCIBIOS_MIN_IO`, assigns `io_map_base`, and registers the controller.

State and persistence: Programs chipset registers and static `struct resource`/`pci_controller` state for the generic MIPS PCI layer.

Dependencies and integration: Uses `loongson_pci_ops` from platform PCI code and is called by `plat_mem_setup()`.

Risks: Hard-coded PCI window layout can conflict with unexpected firmware/device ranges. Legacy ISA IO starts at zero but allocation is protected only by `PCIBIOS_MIN_IO`.

Test signals: PCI bus enumeration should succeed, legacy IDE should retain ISA ports, and DMA-capable PCI devices should access low memory through the programmed hit window.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/pci.c -->
