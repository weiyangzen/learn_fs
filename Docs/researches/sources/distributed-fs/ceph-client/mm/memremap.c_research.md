<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memremap.c -->
# sources/distributed-fs/ceph-client/mm/memremap.c

## Purpose

`memremap.c` implements `memremap_pages()` and related helpers that map device or persistent memory ranges into the kernel page model as `ZONE_DEVICE` pages. It tracks PFN-to-`dev_pagemap` ownership, adds/removes device memory through memory-hotplug infrastructure, initializes device folios, and handles teardown once all page references drain. The complete 528-line file was read.

## Important APIs, Types, and Functions

Important APIs include `memremap_compat_align()`, `pgmap_pfn_valid()`, `memunmap_pages()`, `memremap_pages()`, `devm_memremap_pages()`, `devm_memunmap_pages()`, `get_dev_pagemap()`, `free_zone_device_folio()`, and `zone_device_page_init()`. Internal helpers include `pgmap_array_delete()`, `pfn_first()`, `pfn_end()`, `pfn_len()`, `pageunmap_range()`, `devm_memremap_pages_release()`, `dev_pagemap_percpu_release()`, and `pagemap_range()`. The central state is the global XArray `pgmap_array`, indexed by PFN and read under RCU.

## Control Flow

`memremap_pages()` validates the `dev_pagemap` range count, vmemmap shift, type-specific operations, owner fields, and page protections. It initializes a percpu reference, temporarily clears `pgmap->nr_range`, and maps each range through `pagemap_range()`. That helper rejects conflicting pgmaps at range boundaries, rejects System RAM overlaps, stores the pgmap over the PFN range in `pgmap_array`, tracks the PFN map, checks the hotplug mappable range, takes the memory hotplug lock, adds struct pages via `add_pages()` for private device memory or `arch_add_memory()` plus KASAN zero shadow for CPU-accessible memory, moves the range into `ZONE_DEVICE`, drops the hotplug lock, initializes the zone-device memmap, and pins the pgmap reference for non-private/non-coherent pages.

Teardown through `memunmap_pages()` kills the percpu ref, drops range-sized references for ordinary device memory, waits for completion, unmaps each range with `pageunmap_range()`, exits the percpu ref, and warns if altmap allocations remain. `pageunmap_range()` removes the PFN range from the zone, calls either `__remove_pages()` or `arch_remove_memory()`, removes KASAN shadow for CPU-accessible memory, untracks the PFN map, and clears the XArray entry after an RCU grace period.

## State and Persistence Behavior

`pgmap_array` persists the live PFN ownership map until unmap. `dev_pagemap->ref` gates removal against live pages, with `dev_pagemap_percpu_release()` completing teardown when the ref drains. `pgmap->altmap` tracks vmemmap allocations for devices that self-host struct pages. Zone-device pages carry `folio->pgmap` and type-specific fields such as DAX share counts. Device-managed mappings registered with `devm_memremap_pages()` persist until the owning device releases the devres action or `devm_memunmap_pages()` is called.

## Dependencies and Integration Points

This file integrates with memory hotplug, `ZONE_DEVICE`, sparsemem, KASAN zero shadow, pfnmap tracking, XArray/RCU lookup, percpu references and completions, devres, DAX, HMM/device-private and coherent memory, generic device memory, PCI peer-to-peer DMA, folio migration/free callbacks, memcg uncharge, swapops, page locking, and architecture direct-map creation/removal.

## Risks and Edge Cases

Device memory must not overlap System RAM or an existing `dev_pagemap`, and altmaps are unsupported for multiple ranges. Private memory is inaccessible to the CPU and intentionally skips direct-map creation; CPU-accessible types need KASAN zero shadow and arch mappings. Reference draining is central: removing mappings while pages are still live would corrupt `ZONE_DEVICE` users. `free_zone_device_folio()` has type-specific semantics; clearing stale mapping state is required for private/coherent pages but not for FS DAX or generic pages. `zone_device_page_init()` clears stale compound metadata and warns if drivers allocate after `memunmap_pages()`.

## Test Signals

Useful tests include DAX namespace map/unmap cycles, HMM private/coherent migration tests, PCI P2PDMA mapping tests, overlap/conflict rejection, invalid type/missing-ops validation, altmap allocation accounting, devres automatic cleanup, `get_dev_pagemap()` lookup under concurrent teardown, KASAN shadow add/remove coverage, and folio free paths for each `MEMORY_DEVICE_*` type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/mm/memremap.c -->
