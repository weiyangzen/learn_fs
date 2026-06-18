# sources/distributed-fs/ceph-client/drivers/iommu/of_iommu.c

## Purpose
`of_iommu.c` provides device-tree helpers for the IOMMU core. It translates `iommus` and `iommu-map` properties into device fwspec data, invokes provider-specific `of_xlate()` callbacks, simulates device probing when needed, and provides reserved-region parsing from reserved-memory `iommu-addresses`.

## Important APIs, Types, and Functions
The primary exported functions are `of_iommu_configure()` and `of_iommu_get_resv_regions()`. Internal helpers include `of_iommu_xlate()`, `of_iommu_configure_dev_id()`, `of_iommu_configure_dev()`, `of_pci_iommu_init()`, `of_iommu_configure_device()`, `of_pci_check_device_ats()`, and `iommu_resv_region_get_type()`.

## Control Flow and State
`of_iommu_configure()` serializes against `iommu_probe_device_lock` so `dev->iommu` and fwspec state stay stable. It exits early if a fwspec already exists, records whether `dev->iommu` was initially present, and then configures PCI devices through DMA aliases and `iommu-map`, or non-PCI devices through repeated `iommus` phandles. On errors it frees the fwspec or device IOMMU state depending on whether the device had existing IOMMU state. If configuration succeeds outside the normal probe-device path, it invokes `iommu_probe_device()`.

Reserved-region parsing walks `memory-region` phandles, optionally parses a physical `reg`, then reads `iommu-addresses` tuples. Tuples matching the device node become `iommu_resv_region` entries. If the IOVA region exactly maps the physical region, it is direct; otherwise it is a reserved-only region. DMA-coherent devices get `IOMMU_CACHE` in the protection flags. No durable storage is used; all state is fwspec/device memory and list entries.

## Dependencies and Integration Points
The file integrates with OF core, OF address translation, OF PCI aliasing, fsl-mc headers, PCI ACS requests, module ownership for provider ops, the private IOMMU probe lock, fwspec allocation/free, and reserved-memory bindings.

## Risks and Test Signals
Risks include cleanup asymmetry between pre-existing and newly allocated `dev->iommu`, provider module lifetime around `of_xlate`, PCI alias handling, `iommu-map-mask` translation, reserved-memory tuples with missing or malformed `reg`, zero-length reservations, and non-direct physical-to-IOVA mapping warnings. Test signals include PCI and platform OF devices, EPROBE_DEFER propagation, repeated configure calls, ATS flag setting, reserved-memory direct and reserved cases, and disabled IOMMU provider nodes.
