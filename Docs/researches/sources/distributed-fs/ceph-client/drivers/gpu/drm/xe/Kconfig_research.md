# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/Kconfig

Purpose: Defines build-time configuration for the Intel xe DRM driver and optional display, DP tunnel, GPU SVM, pagemap, and force-probe features.

Important APIs/types: `DRM_XE`, `DRM_XE_DISPLAY`, `DRM_XE_DP_TUNNEL`, `DRM_XE_GPUSVM`, `DRM_XE_PAGEMAP`, `DRM_XE_FORCE_PROBE`, plus debug/profile menus.

Control flow: Kconfig dependency resolution gates compilation and selects required kernel subsystems. The main driver depends on DRM/PCI and page-size constraints. Display support adds display dependencies; SVM/pagemap add device-private memory support; force-probe sets the default module parameter string.

State/persistence: Choices persist in `.config` and alter compiled objects, selected subsystems, and default module behavior.

Dependencies/integration: DRM helpers, TTM, scheduler, GPUVM/GPUSVM, display helpers, ACPI/video, HDA, CEC, MMU notifier, auxiliary bus, and Kconfig debug/profile files.

Risks/test signals: Surprising `select` chains, architecture/page-size limits, display module constraints, force-probe enabling unsupported hardware, and randconfig/allmodconfig/build matrix coverage.
