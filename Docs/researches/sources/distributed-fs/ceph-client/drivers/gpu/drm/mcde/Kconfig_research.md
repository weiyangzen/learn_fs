## sources/distributed-fs/ceph-client/drivers/gpu/drm/mcde/Kconfig

### Purpose

`mcde/Kconfig` exposes the ST-Ericsson MCDE DRM/KMS driver as `CONFIG_DRM_MCDE`, selecting the helper subsystems needed for MCDE display, DSI, bridges, panel bridges, KMS helpers, and DMA-backed GEM buffers.

### Important APIs, types, and functions

The file defines one tristate symbol, `DRM_MCDE`, with prompt text for the Multichannel Display Engine. It depends on DRM, CMA, ARM or compile-test builds, OF, and common clock support. It selects MFD syscon, DRM client selection, MIPI DSI, bridge, panel bridge, KMS helper, and GEM DMA helper support.

### Control flow

There is no runtime control flow. Kconfig resolution controls whether `mcde_drm.o` is built and whether the required helper symbols are available.

### State and persistence behavior

The symbol persists in kernel configuration and determines module or built-in availability. No runtime state is defined here.

### Dependencies

The dependencies match the driver’s use of DT platform probing, regulators/clocks, syscon PRCMU reset, CMA/DMA GEM framebuffers, MIPI DSI host/bridge APIs, and DRM atomic helpers.

### Integration points

`CONFIG_DRM_MCDE` drives the `mcde/Makefile` object selection. If built as a module, the help text says the module name is `mcde_drm`.

### Risks

Missing selected helpers would break linking or probing. The `ARM || COMPILE_TEST` dependency reflects platform reality; enabling on non-ARM only through compile testing may not provide runnable hardware.

### Test signals

Useful signals are `allyesconfig`/`COMPILE_TEST` build coverage, ARM DT boot with `ste,mcde`, and module build/load tests when configured as `m`.
