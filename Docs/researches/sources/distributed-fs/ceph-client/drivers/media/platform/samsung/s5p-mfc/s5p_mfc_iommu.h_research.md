# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/s5p-mfc/s5p_mfc_iommu.h

Purpose: provides a tiny Exynos IOMMU availability helper for the MFC driver.

Important APIs and types: defines inline `exynos_is_iommu_available(struct device *dev)`. With `CONFIG_EXYNOS_IOMMU`, it includes `<linux/iommu.h>` and returns whether `dev_iommu_priv_get(dev)` is non-NULL. Without that config, it always returns false.

Control flow: MFC setup code can call this helper to choose IOMMU-aware memory behavior without scattering Kconfig conditionals through implementation files.

State and persistence: no local state. It observes device IOMMU private data configured by the kernel IOMMU subsystem.

Dependencies and integration points: depends on `struct device`, `dev_iommu_priv_get`, and the `CONFIG_EXYNOS_IOMMU` build option. It integrates platform-specific Exynos IOMMU discovery with common MFC allocation and DMA setup paths.

Risks: availability is inferred from private data presence, not from successful domain attachment or runtime DMA mapping behavior. Non-Exynos builds always see false even if a generic IOMMU exists.

Test signals: build with and without `CONFIG_EXYNOS_IOMMU`; boot on Exynos platforms with IOMMU enabled and disabled; and DMA mapping tests confirming the selected memory path is valid.
