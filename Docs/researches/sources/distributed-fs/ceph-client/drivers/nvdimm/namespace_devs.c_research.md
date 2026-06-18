# sources/distributed-fs/ceph-client/drivers/nvdimm/namespace_devs.c

## Purpose
`namespace_devs.c` implements NVDIMM namespace device creation, discovery from labels, namespace sysfs attributes, DPA allocation changes, UUID/label updates, claim-class selection, page-map policy, and seed-device creation for namespace/BTT/PFN/DAX provisioning. It translates DIMM labels and region mappings into `nd_namespace_pmem` or `nd_namespace_io` devices.

## Important APIs, Types, And Functions
Public functions include `nd_is_uuid_unique()`, `pmem_should_map_pages()`, `pmem_sector_size()`, `nvdimm_namespace_disk_name()`, `nd_dev_to_uuid()`, `__reserve_free_pmem()`, `release_free_pmem()`, `__nvdimm_namespace_capacity()`, `nvdimm_namespace_capacity()`, `nvdimm_namespace_locked()`, `nvdimm_namespace_common_probe()`, `devm_namespace_enable()`, `devm_namespace_disable()`, `nd_region_create_ns_seed()`, `nd_region_create_dax_seed()`, `nd_region_create_pfn_seed()`, `nd_region_create_btt_seed()`, and `nd_region_register_namespaces()`.

Major internal flows include namespace sysfs stores for `alt_name`, `size`, `uuid`, `sector_size`, `holder_class`, and `force_raw`; DPA allocation helpers `scan_allocate()`, `grow_dpa_allocation()`, `shrink_dpa_allocation()`, and `merge_dpa()`; label scanning helpers `create_namespace_pmem()`, `scan_labels()`, and `create_namespaces()`; and active label lifecycle helpers `init_active_labels()` / `deactivate_labels()`.

## Control Flow
Region activation calls `nd_region_register_namespaces()`. It locks the bus, initializes active labels for each mapping by taking `nvdimm_drvdata` references and incrementing DIMM busy counts, determines namespace type, and creates either a direct I/O namespace or label-derived pmem namespaces. Each created device gets an ID/name, lockdep class, and async registration; the first registered namespace becomes the region seed.

Label scanning starts from mapping 0, skips labels outside the mapping, detects conflicting extents with the same UUID, and calls `create_namespace_pmem()`. That function validates interleave-set cookies, checks every mapping has exactly one compatible label at each position, validates DPA ranges against NFIT mappings, moves selected labels to the front of each mapping list, copies UUID/name/LBA/claim class from position 0, sums raw sizes, and sets the namespace resource. If no labels are discovered, it publishes a zero-sized pmem namespace for userspace provisioning.

Sysfs mutation paths take the device lock and bus lock, wait for probe idleness where needed, reject active drivers or claims, mutate in-memory namespace fields or DPA resources, then call `nd_namespace_label_update()` to persist label changes. Size changes allocate or free per-DIMM DPA across mappings with alignment checks and may unregister non-seed zero-sized namespaces.

## State And Persistence Behavior
Namespace runtime state includes namespace device objects, UUIDs, alternate names, LBA sizes, resources, claim class, force-raw flag, and region seed pointers. Persistent state is updated through label writes in `label.c` whenever size, UUID, name, sector size, or holder class changes on pmem namespaces.

DPA allocations are represented as volatile resources under each DIMM's `ndd->dpa`, named by label ID. Size growth scans valid free holes, respects region alignment and contiguity, and can grow adjacent existing resources. Shrink scans from the end and frees or adjusts resources. `nd_namespace_pmem_set_resource()` converts DPA allocation offsets back to SPA resource ranges for the namespace device.

`force_raw` changes runtime mapping policy but is just a namespace field in this file. `pmem_should_map_pages()` decides whether raw pmem should use struct-page backed memremap based on config, region flags, BTT/PFN exclusions, force-raw, system RAM overlap, and architecture memremap mode.

## Dependencies And Integration Points
The file integrates with label APIs, DIMM DPA resource APIs, region/interleave metadata, BTT/PFN/DAX seed creation, claim attach/probe helpers, PMEM mapping policy, Linux sysfs/device core, IDA allocation, badblock-aware namespace enabling, and the NVDIMM bus lock. It is a central bridge between persistent labels and user-visible namespace devices.

## Risks And Edge Cases
Provisioning is highly lock-sensitive: UUID uniqueness and DPA resource trees require the bus lock. Namespace mutation while a driver or claim is active is rejected to avoid changing backing storage under users. Rename is blocked if old labels already exist in active label lists because updating UUIDs in place could lose the namespace. Mixed label versions across mappings can make BTT claim-class selection fail. Alignment errors often manifest as zero available capacity or `-EINVAL`.

Label scan tolerates alternate interleave-set cookies for compatibility but rejects missing positions, duplicate UUIDs, invalid DPA ranges, and conflicting extents. Zero-size namespaces are used as seeds, so tests must distinguish seed deletion behavior from ordinary namespace deletion.

## Test Signals
Tests should cover namespace discovery from complete and incomplete label sets, alternate-cookie acceptance, conflicting extents, DPA range validation, zero-label seed creation, namespace size grow/shrink/delete, UUID uniqueness and rename blocking, holder-class persistence for BTT/PFN/DAX, BTT v1/v2 claim-class selection from label versions, sector-size updates, force-raw mode, `pmem_should_map_pages()` policy branches, locked DIMM rejection, and region namespace registration partial failures.
