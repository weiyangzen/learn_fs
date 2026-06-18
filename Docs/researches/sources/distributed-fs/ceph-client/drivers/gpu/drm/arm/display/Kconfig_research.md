# sources/distributed-fs/ceph-client/drivers/gpu/drm/arm/display/Kconfig

Purpose: declares the ARM Komeda display driver configuration symbol.

Important APIs/types/functions: `config DRM_KOMEDA` is a tristate symbol for the ARM Komeda display processor. It depends on `DRM`, `OF`, and `COMMON_CLK`, and selects DRM client setup, KMS helpers, GEM DMA helpers, and videomode helpers.

Control flow: Kconfig uses this symbol to include the Komeda build and expose module selection. The help text documents D71 support and module name `komeda`.

State and persistence: no runtime state. It persists as `.config` and determines whether the platform driver and KMS module are compiled.

Dependencies/integration: sourced from `drivers/gpu/drm/arm/Kconfig`; consumed by ARM/display kbuild files.

Risks: dependencies are minimal; missing architecture or IOMMU constraints can leave runtime probe failures to the driver. Over-selecting helpers can increase build footprint but keeps link dependencies available. Test signals: Kconfig dependency traversal, module build with `m`, built-in with `y`, and COMPILE_TEST builds if the parent menu allows them.
