## sources/distributed-fs/ceph-client/drivers/gpu/drm/aspeed/Makefile

Purpose: build composition for the ASPEED GFX DRM driver.

Important entries are `aspeed_gfx-y := aspeed_gfx_drv.o aspeed_gfx_crtc.o aspeed_gfx_out.o` and `obj-$(CONFIG_DRM_ASPEED_GFX) += aspeed_gfx.o`. There is no runtime control flow or state.

Dependencies are the Kconfig symbol and the three object files that provide platform probe/sysfs/IRQ, simple display pipe/CRTC programming, and connector output. Integration risk is low but direct: adding a new source file or splitting functionality requires updating this list, and missing objects cause unresolved symbols such as `aspeed_gfx_create_pipe` or `aspeed_gfx_create_output`. Test signals are module build/link success and the resulting `aspeed_gfx` module containing all three implementation units.
