# sources/distributed-fs/ceph-client/drivers/cxl/pmem.c

Purpose: CXL persistent-memory bridge to libnvdimm. It registers CXL NVDIMM bridge, NVDIMM, and PMEM-region CXL bus drivers, implements LSA label commands through the CXL mailbox, exposes DIMM metadata, and creates libnvdimm PMEM regions from CXL PMEM regions.

Important APIs/types/functions: `devm_cxl_add_nvdimm_bridge()`, `cxl_nvdimm_probe()`, `cxl_pmem_get_config_size()`, `cxl_pmem_get_config_data()`, `cxl_pmem_set_config_data()`, `cxl_pmem_ctl()`, `cxl_nvdimm_bridge_probe()`, `cxl_pmem_region_probe()`, `detach_nvdimm()`, and the three CXL drivers registered in `cxl_pmem_init()`.

Control flow and state: NVDIMM probe reserves exclusive CXL commands, arms dirty-shutdown tracking, builds nvdimm command masks, and creates a libnvdimm DIMM with CXL attributes/security ops. Bridge probe registers a libnvdimm bus with `ndctl` callback. PMEM region probe inserts a persistent-memory iomem resource, derives NUMA/target node, builds mappings from CXL memdevs/nvdimms, validates serial numbers, computes an interleave-set cookie, and creates an `nd_region`.

Dependencies and integration: depends on libnvdimm, ndctl payloads, CXL mailbox LSA/security/dirty-shutdown helpers, iomem resources, NUMA node helpers, async driver core, and CXL region objects.

Risks and test signals: label-size bounds, flex allocation, mailbox failures, missing nvdimm driver data, invalid serial numbers, dirty-shutdown visibility, and bridge teardown invalidation are key risks. Test GET/SET LSA, exclusive command blocking, dirty shutdown paths with/without GPF DVSEC, PMEM region creation for multi-way mappings, nvdimm-bus unregister, platform PMEM disable, and security op interop.
