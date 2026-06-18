# sources/distributed-fs/ceph-client/drivers/dax/cxl.c

Purpose: CXL DAX-region consumer that turns CXL RAM regions into dev_dax devices, usually eligible for later conversion to System RAM by dax_kmem.

Important APIs/types/functions: `cxl_dax_region_probe()`, `cxl_dax_region_driver_register()`, `cxl_dax_region_init()/exit()`, and `cxl_dax_region_driver`.

Control flow and state: probe converts a `cxl_dax_region` HPA range into a DAX region using CXL region ID, derives target NUMA node from physical address, uses PMD alignment, marks the region `IORESOURCE_DAX_KMEM`, creates a dynamic dev_dax covering the whole range, and defaults `memmap_on_memory` to true. Init queues delayed registration on `system_long_wq` after flushing HMEM work to avoid racing soft-reserve fallback ownership.

Dependencies and integration: depends on CXL region objects, DAX bus APIs, NUMA helpers, and HMEM coordination.

Risks and test signals: race handling with HMEM fallback, NUMA fallback behavior, resource ownership, and default KMEM eligibility are key. Test CXL dynamic regions, CXL ranges also seen as soft-reserved, module load/unload with pending work, and dax_kmem binding after CXL DAX creation.
