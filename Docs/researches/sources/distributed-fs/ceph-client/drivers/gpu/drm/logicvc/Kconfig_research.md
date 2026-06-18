# sources/distributed-fs/ceph-client/drivers/gpu/drm/logicvc/Kconfig

Purpose: defines the build-time configuration symbol for the Xylon LogiCVC DRM driver.

Important APIs/types/functions: `config DRM_LOGICVC` is tristate, depends on `DRM` and `OF || COMPILE_TEST`, and selects DRM client selection, KMS helper, DMA KMS helper, DMA GEM helper, `REGMAP`, and `REGMAP_MMIO`.

Control flow: no runtime flow. Kconfig controls whether the driver is built in, as a module, or omitted.

State and persistence: persists only in kernel configuration. It influences whether `logicvc-drm.o` is linked by the Makefile.

Dependencies and integration points: reflects actual source dependencies on device tree, regmap MMIO, DRM atomic/KMS, GEM DMA, and fbdev client setup.

Risks and test signals: missing selects would cause link or compile failures in minimal configs. Test with `COMPILE_TEST`, OF-enabled platform builds, module build, and allmodconfig-style coverage.
