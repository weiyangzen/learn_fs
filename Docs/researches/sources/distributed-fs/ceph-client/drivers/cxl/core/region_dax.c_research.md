# sources/distributed-fs/ceph-client/drivers/cxl/core/region_dax.c

Purpose: creates a lightweight `cxl_dax_region` child device for committed CXL RAM regions that should be handed to the DAX/hmem path instead of becoming directly managed System RAM.

Important APIs and control flow: `cxl_dax_region_alloc()` verifies under `cxl_rwsem.region` that the parent region is committed, allocates `struct cxl_dax_region`, snapshots the parent HPA range, initializes a CXL bus device with type `cxl_dax_region_type`, and parents it to the `cxl_region`. `devm_cxl_add_dax_region()` names the child `dax_region%d`, adds it to the device model, and registers `cxlr_dax_unregister()` as a devres action on the parent region. `to_cxl_dax_region()` is exported for consumers.

State and persistence behavior: the child persists only a pointer back to the parent region and a snapshot of the committed HPA range. It has no independent target list or decoder state. Release frees the small allocation; devres unregister ties its lifetime to the parent region driver binding.

Dependencies and integration points: depends on CXL core device typing and base attributes from `port.c`, region state from `region.c`, and downstream DAX/hmem consumers that match `CXL_DEVICE_DAX_REGION`. It is invoked from `cxl_region_probe()` for RAM regions when the range is not already online as System RAM.

Risks and invariants: allocation assumes committed region parameters are stable while the region driver is bound. If region state changes, the parent driver is expected to be released before reset, which unregisters the DAX child. Since the range is a snapshot, later mutation without driver release would create stale DAX metadata.

Test signals: committed RAM region probe should produce `dax_regionN` with correct HPA range and CXL modalias. Uncommitted regions should fail with `-ENXIO`. Parent region unbind/reset/delete should unregister the child. System RAM overlap tests should confirm `region.c` suppresses this path before calling into this file.
