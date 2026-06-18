# sources/distributed-fs/ceph-client/drivers/nvdimm/region.c

Purpose: Implements the generic NVDIMM region driver that activates regions, initializes badblocks, discovers/registers namespaces, creates seed devices, and forwards region events to children.

Important APIs and flow: `nd_region_probe()` warns when online CPUs are fewer than I/O lanes, calls `nd_region_activate()`, initializes region badblocks, populates badblocks from media ranges, registers namespaces, records active/total namespace counts, and creates BTT/PFN/DAX seed devices. `nd_region_remove()` unregisters children, clears seed pointers under the bus lock, drops badblock sysfs state, and invalidates CPU caches for disabled regions when supported. `nd_region_notify()` repopulates poison badblocks on `NVDIMM_REVALIDATE_POISON` and relays events to child devices.

State and persistence behavior: Runtime state includes `struct nd_region_data` driver data, seed device pointers, namespace counts, and `bb_state`. Persistent state is not modified directly; namespace discovery and badblock population read persistent label/poison state through libnvdimm.

Dependencies and integration points: Depends on `region_devs.c` activation and region types, namespace registration, badblocks, BTT/PFN/DAX seed creation, nvdimm bus locking, and child notification APIs.

Risks and test signals: Partial namespace registration is tolerated unless all registrations fail, so userspace must inspect namespace counts. Tests should cover activation failure, badblock sysfs absence, mixed namespace success/failure, removal while attributes are read, poison revalidation, and CPU cache invalidation behavior after disabling.
