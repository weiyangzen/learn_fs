# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Kconfig

Purpose: declares configuration options for in-kernel DRM clients, including fbdev emulation and the DRM boot logger, and selects the default client.

Important symbols: `DRM_CLIENT_LIB` builds the library and selects KMS helper/FB core when fbdev emulation is enabled. `DRM_CLIENT_SELECTION` is selected by drivers that support default clients and pulls in `DRM_CLIENT_LIB` for fbdev/log. `DRM_CLIENT_SETUP` enables client selection plumbing. Under "Supported DRM clients", `DRM_FBDEV_EMULATION` enables legacy fbdev/fbcon support, selects `DRM_CLIENT` and setup, and defaults to `FB`; `DRM_FBDEV_OVERALLOC` controls fbdev buffer over-allocation percentage; `DRM_FBDEV_LEAK_PHYS_SMEM` is an expert escape hatch for legacy userspace requiring physical addresses. `DRM_CLIENT_LOG` enables an on-screen kernel log client and selects draw/font support. A choice selects `DRM_CLIENT_DEFAULT_FBDEV` or `DRM_CLIENT_DEFAULT_LOG`, producing string `DRM_CLIENT_DEFAULT`.

Control flow: these options determine which C files are compiled and which client `drm_client_setup()` starts by default; the runtime module parameter can override the default.

State and persistence: Kconfig values persist in kernel `.config` and built modules. `DRM_FBDEV_OVERALLOC` affects runtime framebuffer allocation size.

Dependencies and integration points: ties DRM core, KMS helper, framebuffer console, `drm_client_setup.c`, `drm_fbdev_client.c`, and `drm_log.c` together. Drivers select `DRM_CLIENT_SELECTION` to opt into the client framework.

Risks: enabling fbdev leaks legacy interfaces into modern KMS drivers. `DRM_FBDEV_LEAK_PHYS_SMEM` is explicitly dangerous and unsupported. Default choice affects boot/user experience, especially whether fbcon or only boot logs appear.

Test signals: Kconfig dependency resolution for fbdev/log/default choices, compile with only fbdev, only log, both, or neither, and boot-time behavior of `drm_client_lib.active=`.
