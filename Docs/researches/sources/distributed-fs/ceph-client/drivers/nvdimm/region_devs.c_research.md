# sources/distributed-fs/ceph-client/drivers/nvdimm/region_devs.c

Purpose: Defines NVDIMM PMEM/volatile region devices, their sysfs ABI, region creation/deletion helpers, interleave mapping metadata, flush handling, lane locking, and persistence-domain queries.

Important APIs and flow: `nvdimm_pmem_region_create()` and `nvdimm_volatile_region_create()` allocate `struct nd_region`, copy mappings, allocate per-CPU lanes, assign ids, install device attributes, and register the device. `nd_region_activate()` blocks overwrite-in-progress DIMMs, invalidates incoherent memory after security operations, allocates `nd_region_data`, maps flush hint addresses, and deduplicates identical flush pages. Sysfs exposes size, mappings, namespace type, seeds, available capacity, badblocks, read-only, alignment, resource, persistence domain, interleave set cookie, and mappingN attributes. `nvdimm_flush()` dispatches provider async flushes or `generic_nvdimm_flush()`; `nvdimm_has_flush()`, `nvdimm_has_cache()`, and `is_nvdimm_sync()` report persistence semantics.

State and persistence behavior: Runtime state includes mappings, `provider_data`, interleave set, flags, read-only state, alignment, badblocks, seed pointers, IDAs, and per-CPU lane counters. Persistent behavior centers on flush hints and platform persistence flags; the file does not write labels but exposes capacity and mapping data derived from persistent namespace metadata.

Dependencies and integration points: Integrates with libnvdimm bus locking, DIMM objects, namespace label helpers, memregion IDs, badblocks, `devm_nvdimm_ioremap()`, architecture cache invalidation, PMEM write barriers, BTT lane users, CXL region flags, and virtio async flush providers.

Risks and test signals: Flush hint mapping and duplicate suppression are hardware-facing and order-sensitive. Alignment changes affect future namespace allocation. Tests should cover no-flush/flush-hint/async-flush regions, security overwrite blocking, incoherent DIMM cache invalidation, read-only propagation to children, interleave mapping sysfs visibility, lane recursion, CXL preassigned ids, and region release cleanup.
