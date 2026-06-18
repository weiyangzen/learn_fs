# sources/distributed-fs/ceph-client/drivers/gpu/drm/hyperv/Makefile

Purpose: defines the Hyper-V DRM module object composition.

Important APIs/types: `hyperv_drm-y` includes driver, modeset, and protocol objects. `obj-$(CONFIG_DRM_HYPERV)` emits `hyperv_drm.o`.

Control flow: kbuild links `hyperv_drm_drv.o`, `hyperv_drm_modeset.o`, and `hyperv_drm_proto.o` when the Kconfig symbol is enabled.

State and persistence: no runtime state; build graph only.

Dependencies and integration points: mirrors the three-file architecture: bus/DRM registration, KMS plane/CRTC/connector setup, and VMBus protocol.

Risks: missing any object breaks probe, scanout, or host protocol.

Test signals: module build, exported internal symbol resolution, and load in a Hyper-V guest.
