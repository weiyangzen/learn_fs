# Research: sources/distributed-fs/ceph-client/include/linux/pci-p2pdma.h

Purpose: `pci-p2pdma.h` defines PCI peer-to-peer DMA provider and mapping APIs so devices can use PCI BAR memory for direct device-to-device transfers when topology allows it.

Important APIs/types/functions: `struct p2pdma_provider` holds owner and bus offset. `enum pci_p2pdma_map_type` distinguishes none, unsupported, bus-address mapping, and host-bridge-allowed mapping. APIs initialize providers, add resources, compute distance, find P2P memory providers, allocate/free P2P memory and scatterlists, publish memory, parse/show sysfs enable state, query map type, update map state, compute per-page P2PDMA state, and map physical to bus addresses.

Control flow and state: a PCI device initializes P2PDMA resources, publishes BAR-backed memory, and clients choose a provider based on distance. DMA mapping paths call `pci_p2pdma_state()` for each page; if the page is P2PDMA, state is updated and a map type tells the DMA layer whether to use bus addresses, normal host-bridge mappings, or reject the transfer. Disabled builds return safe unsupported/null values.

Dependencies and integration points: depends on PCI core, device pages marked as P2PDMA, scatterlists, block devices, DMA mapping, sysfs attributes, and topology/host bridge allowlists.

Risks and test signals: risks include unsafe transfers across unsupported host bridges, wrong bus offset, published memory lifetime issues, scatterlist leaks, and callers ignoring `NOT_SUPPORTED`. Tests should cover topology distance, provider allocation/free, sysfs parsing, DMA map decisions, block/NVMe P2P paths, disabled-config stubs, and hot-remove cleanup.
