# sources/distributed-fs/ceph-client/drivers/pci/p2pdma.c

## Purpose
Implements PCI peer-to-peer DMA memory providers and consumers. It lets drivers expose BAR memory as ZONE_DEVICE pages, allocate/free peer memory, publish providers, choose compatible providers by topology distance, and expose a sysfs mmap allocator.

## APIs, Types, And Functions
Key types are `struct pci_p2pdma`, `struct pci_p2pdma_pagemap`, `struct p2pdma_provider`, and `struct pci_p2pdma_map_state`. Exported APIs include `pcim_p2pdma_init()`, `pcim_p2pdma_provider()`, `pci_p2pdma_add_resource()`, `pci_p2pdma_distance_many()`, `pci_p2pmem_find_many()`, allocation/free and scatterlist helpers, `pci_p2pmem_publish()`, `pci_p2pdma_enable_store()`, and `pci_p2pdma_enable_show()`.

## Control Flow
Provider initialization allocates `struct pci_p2pdma`, initializes an xarray cache, records MMIO BAR bus offsets, and registers devres cleanup. Adding a resource validates BAR/offset/size, creates a gen_pool and sysfs group, maps BAR memory with `devm_memremap_pages()` as `MEMORY_DEVICE_PCI_P2PDMA`, and adds it to the pool with page-map ref ownership. Allocation uses RCU to read `pdev->p2pdma`, allocates from the owner pool, and takes the page-map percpu reference. Topology checks find parent PCI devices, walk upstream bridges to common ancestors, account for ACS redirects, consult CPU support and host bridge whitelist rules, cache map types in an xarray, and return distance or unsupported.

## State And Persistence
State is runtime-only: `pdev->p2pdma` is RCU-protected, `gen_pool` tracks allocations, `p2pmem_published` controls discoverability, `map_types` caches client map decisions, and dev_pagemap/percpu refs guard page lifetime. Sysfs exposes `p2pmem/size`, `available`, `published`, and `allocate`.

## Dependencies And Integration
Depends on DMA mapping internals, `genalloc`, `memremap_pages`, dev_pagemap, percpu refs, xarray, PCI topology/ACS helpers, sysfs binary attributes, and scatterlist APIs. Consumers integrate through PCI P2PDMA public helpers and configfs/sysfs attribute parsers.

## Risks And Test Signals
High-risk areas are RCU lifetime, page refcount initialization for mmap, gen_pool owner refs, sysfs unmap ordering, ACS redirect decisions, stale xarray cached map types, random provider choice ties, and host bridge whitelist correctness. Test signals include adding/removing resources, mmap allocation/unmap, concurrent allocation during provider removal, scatterlist allocation/free, published provider discovery, unsupported non-PCI clients, ACS redirection warnings, cross-host-bridge systems, and fault injection for `memremap_pages`, sysfs creation, and gen_pool failures.
