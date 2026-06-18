# sources/distributed-fs/ceph-client/drivers/dax/bus.h

Purpose: public internal DAX bus header used by DAX region producers and DAX device drivers.

Important APIs/types/functions: DAX resource flags `IORESOURCE_DAX_STATIC` and `IORESOURCE_DAX_KMEM`, `alloc_dax_region()`, `struct dev_dax_data`, `devm_create_dev_dax()`, `enum dax_driver_type`, `struct dax_device_driver`, registration helpers, `kill_dev_dax()`, `static_dev_dax()`, HMEM platform wrapper, `dax_hmem_flush_work()`, and module alias macros.

Control flow and state: region producers allocate a `dax_region`, then create a `dev_dax` with optional pgmap/size/id/memmap-on-memory state. Drivers register with a type so the bus can match generic device-DAX, KMEM conversion, or FS-DAX-compatible drivers.

Dependencies and integration: depends on device, platform-device, range, and workqueue APIs. Included by DAX bus/core, PMEM, HMEM, CXL, device, fsdev, and kmem drivers.

Risks and test signals: type matching and resource flags control which driver binds by default; mistakes can turn reserved memory into System RAM unexpectedly or prevent device access. Test module alias matching, new_id/remove_id overrides, CXL/HMEM flush ordering, and static/dynamic device creation.
