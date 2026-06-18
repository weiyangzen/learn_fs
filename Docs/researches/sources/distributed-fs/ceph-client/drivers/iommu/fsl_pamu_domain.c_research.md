# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.c

## Purpose

`fsl_pamu_domain.c` connects PAMU LIODN programming to the Linux IOMMU API. It registers a PAMU `iommu_device`, creates unmanaged PAMU domains, attaches devices by programming their LIODNs, implements identity `iova_to_phys`, manages device/domain bookkeeping, and exposes the Freescale L1 stash configuration helper.

## Important APIs, Types, and Functions

- `struct fsl_dma_domain`: PAMU domain state with device list, stash ID, embedded `iommu_domain`, and lock.
- `struct device_domain_info`: per-device LIODN/domain link stored in `dev_iommu_priv`.
- `iommu_init_mempool`: allocates slab caches for domains and device links.
- `pamu_set_liodn`: disables, configures, and prepares a LIODN PAACE for a domain.
- `fsl_pamu_attach_device` and `fsl_pamu_platform_attach`: unmanaged attach and platform-domain detach behavior.
- `fsl_pamu_configure_l1_stash`: exported stash update path for existing domain LIODNs.
- `fsl_pamu_device_group`, `fsl_pamu_probe_device`: group and device admission callbacks.
- `fsl_pamu_ops`: Linux IOMMU ops registration.

## Control Flow

`pamu_domain_init` creates slab caches, adds `iommu0` sysfs state, and registers `fsl_pamu_ops`. Domain allocation only accepts `IOMMU_DOMAIN_UNMANAGED`, initializes an identity-like 64 GiB geometry, and defaults `stash_id` to `~0`. Device attach resolves PCI devices to their host controller parent, reads all `fsl,liodn` values, links each LIODN into the domain list, configures the PAACE under `iommu_lock`, then enables the LIODN. Platform-domain attach is used as a detach hook from unmanaged domains; it removes device references and disables LIODNs, but does not restore identity PAACE state.

## State and Persistence Behavior

Domain state persists in slab-allocated `fsl_dma_domain` objects. Attached device/LIODN links are kept on the domain list and, for the first LIODN, in `dev_iommu_priv`. `domain_lock` protects per-domain lists and stash updates, `device_domain_lock` protects `dev_iommu_priv`, and `iommu_lock` serializes hardware PAACE changes. PAACE state persists in PAMU tables owned by `fsl_pamu.c`.

## Dependencies and Integration Points

The file depends on Linux IOMMU core, OF LIODN properties, PowerPC PCI controller helpers, and the PAMU hardware functions from `fsl_pamu.c`. It integrates with platform devices, PCI host controllers, `iommu_group` assignment, and Freescale QMan portal code that calls the stash helper.

## Risks and Edge Cases

- The file contains explicit FIXME notes that PAMU does not fit the modern IOMMU API well: the unmanaged domain is not a true paging domain and detaching cannot restore identity mappings.
- `attach_device` does not check `kmem_cache_zalloc` failure before dereferencing `info`.
- LIODNs are read as big-endian device-tree cells but compared and passed as raw `liodn[i]` without `be32_to_cpup`, unlike `fsl_pamu.c`.
- `remove_device_ref` calls `list_del` while nested lock ordering crosses domain and device-domain locks.
- PCI grouping depends on controller version and initialization ordering between PAMU and FSL PCI.

## Test Signals

Test attach/detach of platform devices with one and multiple LIODNs, PCI devices behind partitionable and non-partitionable controllers, stash update after attach, missing/invalid `fsl,liodn`, domain free with attached devices, and IOMMU group reuse. Lockdep and fault-injection around slab allocation and PAACE programming would be especially valuable.
