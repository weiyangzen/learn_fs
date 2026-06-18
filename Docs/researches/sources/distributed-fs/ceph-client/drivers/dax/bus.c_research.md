# sources/distributed-fs/ceph-client/drivers/dax/bus.c

Purpose: DAX bus and device-region management core. It registers the `dax` bus, allocates DAX regions and dev_dax instances, exposes sysfs controls for dynamic partitioning, and dispatches dev_dax devices to device, kmem, or fsdev drivers.

Important APIs/types/functions: `alloc_dax_region()`, `devm_create_dev_dax()`, `kill_dev_dax()`, `static_dev_dax()`, `dax_pgoff_to_phys()`, `__dax_driver_register()`, `dax_driver_unregister()`, `dax_bus_init()/exit()`, sysfs handlers for `create`, `delete`, `size`, `mapping`, `align`, `memmap_on_memory`, and mapping child devices.

Control flow and state: `dax_region_rwsem` protects region resource partitioning; `dax_dev_rwsem` protects dev_dax size/id/memmap state; `dax_bus_lock` protects dynamic driver ID lists. Dynamic regions can create seed devices, resize unbound devices, allocate multiple mapping ranges, and expose child `mappingN` devices. Static regions are mostly read-only and carry prebuilt pgmaps. Binding checks refuse zero-size or invalid-ID devices.

Dependencies and integration: depends on driver core, resource trees, memremap alignment, DAX pseudo-device core, sysfs, xarray-like IDA allocation, and HMEM/PMEM/CXL producers. It exports the main DAX construction and bus-registration APIs.

Risks and test signals: locking order, resize while bound, stale pgmap after unbind, range/resource leaks, dynamic ID lifetime, static-vs-dynamic mismatch, and sysfs parsing are high-risk. Test create/delete/resize/mapping/align/memmap sysfs, multi-range devices, driver rebinding, static PMEM devices, kmem type matching, no KMEM config fallback, and resource conflict handling.
