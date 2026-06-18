# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Kconfig

Purpose: declares `DRM_HYPERV`, the Hyper-V synthetic video DRM KMS driver option.

Important APIs/types: the tristate depends on DRM, PCI, and Hyper-V VMBus. It selects DRM client selection, KMS helper, and GEM shmem helper.

Control flow: when selected, the Hyper-V Makefile builds the driver objects into `hyperv_drm`.

State and persistence: build-time configuration only.

Dependencies and integration points: integrates with Hyper-V VMBus and a PCI stub for generation 1 VM support, plus DRM shmem/fbdev helpers.

Risks: help text notes `CONFIG_FB_HYPERV` should be unselected so the DRM driver is default. Dependency mismatch can leave the synthetic device without the intended KMS driver.

Test signals: build with `CONFIG_DRM_HYPERV=y/m`, boot in Hyper-V VM, and conflict behavior with Hyper-V framebuffer.
