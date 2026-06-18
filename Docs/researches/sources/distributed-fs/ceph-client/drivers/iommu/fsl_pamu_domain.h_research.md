# sources/distributed-fs/ceph-client/drivers/iommu/fsl_pamu_domain.h

## Purpose

`fsl_pamu_domain.h` defines the PAMU domain-private state structures shared by the domain implementation and nearby PAMU code.

## Important APIs, Types, and Functions

- `struct fsl_dma_domain`: list of attached device LIODNs, current stash ID, embedded `struct iommu_domain`, and a per-domain spinlock.
- `struct device_domain_info`: list node, device pointer, LIODN, and owning domain pointer for one device/LIODN association.

## Control Flow

The header does not implement logic. `fsl_pamu_domain.c` allocates these structures from slab caches, stores `device_domain_info` in the domain list and `dev_iommu_priv`, and uses `fsl_dma_domain` as the container for Linux IOMMU domains.

## State and Persistence Behavior

The structures represent all mutable domain-level PAMU state outside the hardware PAACE tables. They persist for the lifetime of a domain or device attachment and are released on detach/domain free.

## Dependencies and Integration Points

It includes `fsl_pamu.h`, so users inherit PAMU constants and Linux IOMMU dependencies. The embedded `iommu_domain` makes container conversion possible for IOMMU callbacks.

## Risks and Edge Cases

The header exposes raw list and lock fields with no helper API, so correctness depends on `fsl_pamu_domain.c` lock ordering. `device_domain_info` has one `liodn` field per object; multi-LIODN devices require multiple instances and only the first is stored in `dev_iommu_priv`.

## Test Signals

Structural tests are indirect: attach/detach paths should verify list integrity, `dev_iommu_priv` cleanup, multi-LIODN handling, and domain-free cleanup under lockdep.
