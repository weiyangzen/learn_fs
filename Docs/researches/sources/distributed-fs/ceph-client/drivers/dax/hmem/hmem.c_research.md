# sources/distributed-fs/ceph-client/drivers/dax/hmem/hmem.c

Purpose: converts recorded HMEM soft-reserve resources into per-range `hmem` platform devices and dev_dax instances, while deferring CXL-described ranges to CXL when appropriate.

Important APIs/types/functions: module parameter `region_idle`, `dax_hmem_probe()`, `dax_hmem_flush_work()`, `__hmem_register_device()`, `hmem_register_cxl_device()`, `process_defer_work()`, `hmem_register_device()`, `dax_hmem_platform_probe()`, and module init/exit.

Control flow and state: init requests CXL modules when CXL DAX is enabled, creates an ordered workqueue, and registers platform drivers. The platform probe walks collected HMEM resources. For CXL-described resources, it waits for CXL discovery once and drops resources claimed by CXL regions; otherwise it allocates a memregion ID, creates an `hmem` platform device with `memregion_info`, and `dax_hmem_probe()` allocates a DAX region and dev_dax. `region_idle` creates zero-size seed devices instead of default full-size KMEM-eligible devices.

Dependencies and integration: depends on DAX bus, memregion allocator, platform devices, CXL region ownership checks, soft-reserve resource intersection helpers, workqueues, and module autoload.

Risks and test signals: CXL-vs-HMEM ownership race, deferred work lifetime, memregion ID cleanup, region_idle behavior, and IORESOURCE_DAX_KMEM flag selection are key. Test CXL soft-reserve ranges before/after CXL probe, non-CXL soft reserve, module unload with workqueue, region_idle seeds, and dev_dax creation failures.
