<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memremap.h -->
# sources/distributed-fs/ceph-client/include/linux/memremap.h

## Purpose
This header defines APIs and metadata for remapping physical memory into the kernel, especially ZONE_DEVICE/dev_pagemap memory such as DAX, private/coherent device memory, generic device memory, and PCI peer-to-peer DMA memory.

## Important APIs, types, and functions
`struct vmem_altmap` describes reserved/free pages used for vmemmap metadata. `enum memory_type` classifies ZONE_DEVICE usage. `struct dev_pagemap_ops` provides `folio_free`, `migrate_to_ram`, `memory_failure`, and `folio_split` callbacks. `struct dev_pagemap` tracks altmap, percpu ref, completion, type, flags, vmemmap shift, ops, owner, and one or more ranges. Helpers identify page types, access/set device-private data, query altmaps, vmemmap size, memory-failure support, and split callbacks. ZONE_DEVICE APIs include `zone_device_page_init`, `memremap_pages`, `memunmap_pages`, devm variants, `get_dev_pagemap`, `pgmap_pfn_valid`, and `memremap_compat_align`; disabled builds warn or return stubs.

## Control flow
Device-memory drivers fill `dev_pagemap`, map ranges with `memremap_pages()` or devm variant, and receive lifecycle callbacks as folios are freed, migrated, split, or hit by memory failure. Users identify page type with inline helpers and release mappings with `put_dev_pagemap()`/unmap paths.

## State and persistence
Runtime state includes page map ranges, percpu reference lifetime, completion, altmap allocation accounting, vmemmap order, owner pointer, and per-page `pgmap`/zone-device data. Device memory contents may persist depending on hardware, but mapping metadata is runtime.

## Dependencies and integration points
It depends on mm zones, ranges, resources, IO port definitions, percpu refcounts, completions, folios, devm resources, HMM, DAX, PCI P2PDMA, memory failure, and memory hotplug.

## Risks and test signals
Risks include missing `migrate_to_ram` for private memory, pinning semantics for coherent/device memory, altmap accounting errors, refcount leaks, invalid PFN checks, split callback propagation, and disabled ZONE_DEVICE fallback misuse. Test each memory type, map/unmap lifetime, altmap-backed vmemmap, folio split/free, migration to RAM, memory failure fallback, P2PDMA detection, and CONFIG_ZONE_DEVICE=n callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/memremap.h -->
