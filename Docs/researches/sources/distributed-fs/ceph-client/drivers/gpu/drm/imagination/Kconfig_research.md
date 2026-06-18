# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/Kconfig

Purpose: defines Kconfig entries for the Imagination PowerVR DRM driver and its KUnit tests.

Important symbols: `DRM_POWERVR` is a tristate driver for PowerVR Series 6 and later / IMG Graphics. It depends on 64-bit ARM64 or 64-bit RISC-V, DRM, MMU, PM, and a tautological POWER_SEQUENCING expression allowing either configuration. It selects DRM execution, GEM shmem, DRM scheduler, GPUVM, and firmware loader support. `DRM_POWERVR_KUNIT_TEST` enables driver KUnit tests when `DRM_POWERVR && KUNIT`, defaulting under `KUNIT_ALL_TESTS`.

Control flow and state: no runtime logic; configuration controls whether `powervr` and `pvr_test` objects are built.

Dependencies and integration: integrates with the DRM subsystem, firmware loading, scheduler, GPUVM, and KUnit. Module name is documented as `powervr`.

Risks: architecture gating excludes 32-bit and non-ARM64/RISC-V builds. Adding source features may require additional selected dependencies here.

Test signals: `allyesconfig`/module builds with `DRM_POWERVR`, and KUnit builds when `DRM_POWERVR_KUNIT_TEST` is enabled.
