# sources/distributed-fs/ceph-client/drivers/parisc/iommu.h

## Purpose
This header provides the PA-RISC bus-to-IOMMU lookup and abstracts CCIO/SBA resource and IOMMU hooks for platform bus drivers.

## Important APIs, Types, And Functions
`parisc_walk_tree()` returns the nearest `struct pci_hba_data` cached in a device’s `platform_data` or inherited from an ancestor. `GET_IOC()` returns the `struct ioc` IOMMU pointer stored in that HBA. The header declares or stubs `ccio_get_iommu()`, `ccio_request_resource()`, `ccio_allocate_resource()`, and declares `sba_get_iommu()`.

## Control Flow
Runtime lookup first checks `dev->platform_data`; if missing, it walks parent devices until an ancestor with HBA data is found, then caches that pointer back on the original device. DMA mapping paths call `GET_IOC()` to reach the correct controller. Resource-request users call CCIO helpers when configured or generic iomem resource insertion/allocation when CCIO support is absent.

## State And Persistence
The only mutation is caching inherited HBA data in `dev->platform_data`. That makes later DMA/resource lookups faster but assumes the device hierarchy and HBA association are stable.

## Dependencies And Integration Points
This file integrates PA-RISC PCI HBA data with IOMMU drivers, LBA/EISA/HP-PB resource management, and the generic DMA mapping code. It depends on Linux PCI resources and PA-RISC `parisc_device` declarations.

## Risks
Caching in `platform_data` can conflict with other code if a child device expects to own that field for unrelated data. `GET_IOC()` returns `NULL` when no HBA data is found, so DMA operations must handle that path. Stubbed CCIO helpers insert resources directly into `iomem_resource`, which changes behavior on non-CCIO builds.

## Test Signals
Signals include DMA mapping succeeding for PCI children whose HBA data is inherited from a bridge, CCIO-enabled and CCIO-disabled builds compiling, and resource requests landing under the expected parent tree.
