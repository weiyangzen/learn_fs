## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Kconfig

Purpose: Kconfig entry for the ASPEED BMC Graphics CRT DRM/KMS driver.

Important symbol is `DRM_ASPEED_GFX`, a tristate depending on DRM, OF, ASPEED architecture or compile testing, and MMU. It selects DRM client setup, KMS helpers, DMA GEM helpers, CMA/DMA_CMA when contiguous memory is available, and `MFD_SYSCON`.

Control flow is build-time only: enabling the symbol causes the Makefile to build `aspeed_gfx`. State/persistence is kernel configuration state and module selection. Dependencies mirror runtime needs: device tree matching, syscon regmap access, DMA-capable framebuffer memory, and simple KMS helpers.

Risks include missing reserved memory/CMA support on platforms that need contiguous scanout buffers, architecture coverage limited by DT/OF, and help text mentioning AST2500 even though the driver table also supports AST2400 and AST2600 compatibles. Test signals are `olddefconfig` selection, compile-test builds, module load on ASPEED DT systems, and successful dependency resolution.
