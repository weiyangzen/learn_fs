# sources/distributed-fs/ceph-client/drivers/iommu/dma-iommu.h

## Purpose
Public internal header for IOMMU drivers using the generic DMA-IOMMU glue. It declares the DMA setup, cookie, reserved-region, flush-queue, MSI, and forced-DAC interfaces when `CONFIG_IOMMU_DMA` is enabled and provides harmless stubs otherwise.

## Important APIs, Types, And Functions
Enabled declarations include `iommu_setup_dma_ops()`, `iommu_get_dma_cookie()`, `iommu_put_dma_cookie()`, `iommu_put_msi_cookie()`, `iommu_dma_init_fq()`, `iommu_dma_get_resv_regions()`, `iommu_dma_sw_msi()`, and `extern bool iommu_dma_forcedac`. Disabled stubs make setup and reserved-region helpers no-ops, return `-EINVAL` for flush queue init, and return `-ENODEV` for cookie/MSI setup.

## Control Flow
Drivers such as `arm-smmu.c` and `exynos-iommu.c` include this header to add generic reserved regions and DMA setup support. The actual control flow lives in `dma-iommu.c`; this header gates link-time availability and keeps non-DMA-IOMMU builds compiling.

## State And Persistence
The header itself stores no state. The only declared state is `iommu_dma_forcedac`, defined in `dma-iommu.c` and initialized by the early kernel parameter.

## Dependencies And Integration Points
It depends on `linux/iommu.h` and is consumed by IOMMU drivers and DMA mapping code. Its stub behavior is part of the build contract for configurations without `CONFIG_IOMMU_DMA`.

## Risks
Callers must handle `-ENODEV`/`-EINVAL` from stubs correctly. Adding new DMA-IOMMU APIs requires matching enabled declarations and disabled stubs to avoid configuration-specific build failures.

## Test Signals
Compile with `CONFIG_IOMMU_DMA=y` and disabled. Exercise drivers that call reserved-region helpers and DMA setup in both configurations and verify no unresolved symbols or ignored stub errors.
