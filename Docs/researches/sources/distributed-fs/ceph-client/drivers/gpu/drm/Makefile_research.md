# sources/distributed-fs/ceph-client/drivers/gpu/drm/Makefile

Purpose: builds the DRM core object, helper libraries, memory-management components, tests, and selected DRM drivers.

Important APIs/types/functions: composes `drm-y` from core atomic/auth/bridge/connector/CRTC/GEM/ioctl/modeset/prime/syncobj/vblank objects; conditionally adds client, compat, OF/PCI, debugfs, privacy, accel, panic, draw, QR, and RAS objects; builds KMS, DMA, SHMEM, TTM, VRAM, suballoc, GPUVM/GPUSVM, exec, and buddy helpers; descends into driver directories.

Control flow: Kbuild builds `drm.o` for `CONFIG_DRM`, helper composite objects for selected helper symbols, tests, and then selected hardware driver subdirectories. It also applies DRM-local warning flags, dynamic-debug defines, optional `-Werror`, and header self-test rules.

State/persistence: build-time state only.

Dependencies/integration: central integration point for DRM core, Kbuild, helper subsystems, memory managers, test directories, and all DRM hardware drivers.

Risks: object list and order errors produce unresolved symbols or config-specific build failures; W=1 and `CONFIG_DRM_WERROR` can make warnings fatal; header tests require self-contained headers.

Test signals: `make drivers/gpu/drm/`, allmodconfig, selected helper-only configs, `CONFIG_DRM_HEADER_TEST`, `CONFIG_DRM_WERROR`, and representative driver builds.
