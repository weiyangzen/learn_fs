# sources/distributed-fs/ceph-client/drivers/cxl/core/region_pmem.c

Purpose: creates a `cxl_pmem_region` bridge device for committed persistent CXL regions and connects it to the CXL NVDIMM bridge so the nvdimm subsystem can consume the region's endpoint mappings.

Important APIs and control flow: `cxl_pmem_region_alloc()` verifies committed state, allocates a flexible `struct cxl_pmem_region` sized for all targets, snapshots the HPA range and each endpoint mapping, finds the common `cxl_nvdimm_bridge` from the first memdev endpoint, stores a bridge reference in the parent region, and initializes the child device. `devm_cxl_add_pmem_region()` names and registers `pmem_region%d`, then under the bridge device lock registers a devres action on the NVDIMM bridge to unregister the pmem region. It also registers a parent-region devres action that releases the NVDIMM bridge reference and coordinates unregister if the region goes away first. `is_cxl_pmem_region()` and `to_cxl_pmem_region()` are exported.

State and persistence behavior: the pmem region snapshots committed endpoint mappings: memdev references, DPA starts, DPA sizes, and interleave positions. It pins each memdev until release. The parent region stores `cxlr->cxl_nvb` and `cxlr->cxlr_pmem` while the bridge is active. Device removal is coordinated through both the NVDIMM bridge and CXL region devres domains to handle either side disappearing first.

Dependencies and integration points: depends on region state from `region.c`, memdev/endpoint decoder helpers, `cxl_find_nvdimm_bridge()`, the CXL bus modalias model, and nvdimm bridge driver behavior. It is called by `cxl_region_probe()` for PMEM regions after optional EDAC setup.

Risks and invariants: the code assumes all targets in a region share the same CXL NVDIMM bridge because regions do not span root devices. Bridge locking is required when unregistering from either region or bridge context. Snapshotting under `cxl_rwsem.region` is necessary so target mappings cannot change while the child is built. Error paths must drop the bridge reference and clear `cxlr->cxl_nvb` to avoid stale pointers.

Test signals: committed PMEM region probe should create `pmem_regionN` with correct HPA range, mapping count, DPA starts/sizes, and positions. Missing bridge should return `-ENODEV`. Parent region deletion and NVDIMM bridge removal should both unregister the child without double-unregister. Memdev reference counts should balance across errors and normal release.
