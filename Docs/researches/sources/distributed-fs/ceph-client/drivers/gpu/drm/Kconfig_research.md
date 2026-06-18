# sources/distributed-fs/ceph-client/drivers/gpu/drm/Kconfig

Purpose: main DRM configuration menu defining core DRM, helpers, debugging/panic features, memory-management helpers, and all individual DRM driver menus.

Important APIs/types/functions: defines `DRM`, `DRM_KMS_HELPER`, `DRM_CLIENT`, `DRM_TTM`, `DRM_EXEC`, `DRM_GPUVM`, `DRM_GPUSVM`, `DRM_BUDDY`, GEM helper options, `DRM_SCHED`, `DRM_PANIC*`, `DRM_RAS`, and sources vendor/SoC driver Kconfigs including ADP and amdgpu.

Control flow: selecting `DRM` enables shared infrastructure such as DMA-BUF, sync files, HDMI, I2C, KCMP, and VIDEO, then exposes helper libraries and driver menus under `if DRM`.

State/persistence: configuration only; selected symbols persist in `.config`.

Dependencies/integration: integrates DRM core with framebuffer emulation, KMS/display/panel/bridge helpers, GPU memory managers, RAS netlink, panic screen support, and many hardware drivers. `DRM_BUDDY` selects `GPU_BUDDY`.

Risks: bad dependencies/selects create invalid configs or helper build failures far from the changed symbol.

Test signals: allmodconfig/allnoconfig/allyesconfig plus targeted DRM helper, panic/RAS, ADP, and amdgpu configurations.
