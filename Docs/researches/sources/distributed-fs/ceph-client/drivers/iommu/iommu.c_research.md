# sources/distributed-fs/ceph-client/drivers/iommu/iommu.c

## Purpose
This is the central Linux IOMMU core implementation for device probing, IOMMU device registration, group construction, default domain management, DMA ownership, domain attach/detach, IOVA map/unmap helpers, reserved-region handling, PASID attachment, attach handles for IOMMUFD, PCI reset blocking, MSI preparation, and sysfs-visible group attributes.

## Important APIs, Types, And Functions
Core state includes the global `iommu_device_list`, `iommu_group_kset`, `iommu_group_ida`, `iommu_global_pasid_ida`, `iommu_def_domain_type`, `iommu_dma_strict`, and `iommu_cmd_line`.

`struct iommu_group` tracks the group kobject, device list, PASID xarray, mutex, default/blocking/current domains, ownership counters, reset recovery count, and optional driver data. `struct group_device` stores a device in a group plus reset-blocking state.

Registration and probing APIs include `iommu_device_register()`, `iommu_device_unregister()`, selftest-only bus registration helpers, `iommu_probe_device()`, `iommu_release_device()`, `bus_iommu_probe()`, and the bus notifier.

Group APIs include `iommu_group_alloc()`, `iommu_group_add_device()`, `iommu_group_remove_device()`, `iommu_group_for_each_dev()`, `iommu_group_get()`, `iommu_group_put()`, `iommu_group_id()`, `generic_device_group()`, `generic_single_device_group()`, `pci_device_group()`, and `fsl_mc_device_group()`.

Domain APIs include `iommu_paging_domain_alloc_flags()`, `iommu_domain_free()`, `iommu_attach_device()`, `iommu_detach_device()`, `iommu_attach_group()`, `iommu_detach_group()`, `iommu_iova_to_phys()`, `iommu_map_nosync()`, `iommu_map()`, `iommu_unmap()`, `iommu_unmap_fast()`, and `iommu_map_sg()`.

Ownership and default-domain APIs include `iommu_device_use_default_domain()`, `iommu_device_unuse_default_domain()`, `iommu_group_claim_dma_owner()`, `iommu_device_claim_dma_owner()`, `iommu_group_release_dma_owner()`, `iommu_device_release_dma_owner()`, and `iommu_group_dma_owner_claimed()`.

PASID and handle APIs include `iommu_attach_device_pasid()`, `iommu_replace_device_pasid()`, `iommu_detach_device_pasid()`, `iommu_alloc_global_pasid()`, `iommu_free_global_pasid()`, `iommu_attach_handle_get()`, `iommu_attach_group_handle()`, `iommu_detach_group_handle()`, and `iommu_replace_group_handle()`.

Other exports include fault reporting, reserved regions, firmware spec setup, default passthrough selection, page-table quirks, PCI reset IOMMU prepare/done, and optional software MSI preparation.

## Control Flow
Boot first creates `/sys/kernel/iommu_groups` via `iommu_init()` and registers IOMMU bus notifiers in `iommu_subsys_init()`. Default domain policy is selected from Kconfig, memory encryption, and early parameters `iommu.passthrough` and `iommu.strict`.

When an IOMMU driver registers, `iommu_device_register()` stores ops in the global list and probes supported buses. Device probe allocates `dev->iommu`, obtains firmware ops, takes the IOMMU module reference, calls `ops->probe_device()`, creates the sysfs IOMMU-device link, obtains a group from `ops->device_group()`, adds a `group_device`, creates default domains, direct reserved mappings, and DMA ops. Removal reverses sysfs links, driver release hooks, domain cleanup, module refs, and group refs.

Group creation allocates an ID, initializes kobjects/xarrays/mutexes, creates the `devices` kobject, and exposes `reserved_regions` and `type`. Adding a device creates bidirectional group sysfs links and records trace events. PCI grouping walks DMA aliases, ACS isolation boundaries, multifunction aliasing, and existing groups to preserve DMA isolation.

Default domain setup chooses a driver-requested, user-requested, or global domain type; allocates identity or paging domains; installs DMA cookies for DMA domains; maps `IOMMU_RESV_DIRECT` regions before attach; attaches the domain to all group devices; and restores/free old domains on failure. Sysfs `type` changes require admin/rawio privileges and usually require no owner.

Attach/detach flows are group-centric. `__iommu_group_set_domain_internal()` iterates every unblocked group device and calls `attach_dev`; on failure it reverts earlier devices to the old domain unless the caller marked the transition must-succeed. Detach returns the group to default or blocking domain depending on ownership.

Map/unmap flows validate paging domains, page-size bitmaps, alignment, and GFP flags. `iommu_map_nosync()` maps via generic page-table ops when a generic `pt_iommu` is present, otherwise calls domain ops in page-size batches, traces and debug-records mapped bytes, and unwinds partial maps. `iommu_map()` adds sync. Unmap uses gather state and syncs unless `iommu_unmap_fast()` delegates sync to the caller.

DMA ownership blocks ordinary DMA API use for exclusive owners such as VFIO/IOMMUFD. Claiming ownership allocates or reuses a blocking domain, attaches it, records `owner` and `owner_cnt`, and rejects mismatched owners or existing PASID attachments. Release restores the default domain once the last owner leaves.

PASID attach attaches a domain to the same PASID across all PASID-capable devices in a group, stores either a tagged domain pointer or attach handle in `group->pasid_array`, and rolls back partial device configuration. Replace reserves the xarray slot, optionally changes hardware PASID domains, and swaps in a new handle. Detach removes hardware PASID domains and erases the xarray entry.

PCI reset prepare/done temporarily attaches RID and PASID translations to the blocking domain while retaining `group->domain` and `pasid_array`, sets `gdev->blocked`, increments `recovery_cnt`, and restores domains after reset. Concurrent attach attempts are rejected while `recovery_cnt` is nonzero.

## State And Persistence
All state is in kernel memory: global IOMMU device lists, per-device `dev_iommu`, `iommu_fwspec`, groups, kobjects, xarrays, IDAs, domains, owner counters, PASID entries, and reset-blocking flags. Sysfs exposes but does not persist group and device topology. Early parameters affect boot-time default policy only. Map/unmap state lives in driver page tables and optional generic page-table structures.

## Dependencies And Integration Points
This file integrates with the Linux device model, bus notifiers, sysfs, PCI/ACS/PASID/ATS, MSI, DMA-IOMMU, firmware-node parsing, module ownership, tracepoints, debugfs, IOMMUFD internal attach handles, `uapi/linux/iommufd.h`, and low-level `struct iommu_ops`/`struct iommu_domain_ops` supplied by hardware drivers.

It is a major integration point for IOMMUFD: domains can carry `IOMMU_COOKIE_IOMMUFD`, handle-based group attach is exported in the `IOMMUFD_INTERNAL` namespace, PASID replace is exported there, and MSI preparation can dispatch to `iommufd_sw_msi()`.

## Risks
Lock ordering is critical: probe uses `iommu_probe_device_lock`, groups use `group->mutex`, PASID xarrays have their own lock for handle lookup, and some reset/PASID readers intentionally rely on synchronization comments. Races here can lead to use-after-free or stale hardware attachment.

Domain transition failure handling assumes drivers can always reattach known-good domains or blocking domains; a buggy driver can leave inconsistent hardware despite defensive warnings.

Default-domain changes and direct reserved mappings are security-sensitive: devices with firmware-required 1:1 mappings cannot be safely attached to blocking domains, and untrusted PCI devices are forced toward translated DMA.

PASID attach/replace stores lockless-visible attach handles. Callers must provide fresh handles and synchronize lifetime with attach/detach, otherwise PRI/fault paths can dereference invalid memory.

Mapping helpers rely on accurate `pgsize_bitmap`, `map_pages`, and `unmap_pages` behavior. Partial map accounting is essential; tests should check that `mapped` bytes reflect hardware state on errors.

PCI reset blocking warns about DMA-aliased siblings that may be prematurely unblocked; that path is explicitly noted as an unresolved risk in complex alias cases.

## Test Signals
Relevant signals include boot/probe tests across supported buses, sysfs group topology, default-domain selection under `iommu.passthrough` and `iommu.strict`, DMA-FQ transition through group `type`, VFIO/IOMMUFD ownership claim/release, PASID attach/replace/detach with mixed PASID-capable group members, PCI reset with ATS enabled, reserved-region direct mappings, MSI remapping through DMA and IOMMUFD cookies, and tracepoint output for group, attach, map, unmap, and fault events.

Unit or selftest coverage should exercise failure injection in domain allocation, attach, map, reserved region retrieval, xarray reservations, and group removal while ensuring no leaked domains, group refs, PASID entries, or sysfs links remain.
