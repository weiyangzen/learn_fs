<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig

Purpose: Defines the Rust `DRM_TYR` option for ARM Mali CSF-based GPU experimentation.

Important APIs/types/functions: The option is tristate, depends on `DRM=y`, `RUST`, `ARM || ARM64 || COMPILE_TEST`, `!GENERIC_ATOMIC64`, and `COMMON_CLK`, and defaults to `n`. Help text states it targets Mali/Immortalis Valhall Gxxx CSF GPUs, excluding non-CSF G68/G78, and warns that it is work in progress.

Control flow: Enabling this option allows kbuild to compile the Rust `tyr` module.

State and persistence: Build-time metadata only.

Dependencies and integration points: Captures Rust kernel support, DRM built-in requirement, clock support, and architecture constraints tied to IOMMU page-table assumptions.

Risks and test signals: Build tests should cover Rust-enabled ARM64 and `COMPILE_TEST` configs, plus disabled cases where `DRM` is modular or Rust is unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/Kconfig -->
