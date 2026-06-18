# sources/distributed-fs/ceph-client/drivers/gpu/drm/clients/Makefile

Purpose: builds the DRM client library object and conditionally includes fbdev emulation and boot logger implementations.

Important entries: `subdir-ccflags-y += -I$(src)/..` lets client files include DRM internal headers from the parent directory. `drm_client_lib-y := drm_client_setup.o` is always included when `CONFIG_DRM_CLIENT_LIB` builds. `drm_client_lib-$(CONFIG_DRM_CLIENT_LOG) += drm_log.o` and `drm_client_lib-$(CONFIG_DRM_FBDEV_EMULATION) += drm_fbdev_client.o` add optional clients. `obj-$(CONFIG_DRM_CLIENT_LIB) += drm_client_lib.o` emits the final library object/module.

Control flow: Kconfig decides object composition; no runtime control exists here.

State and persistence: affects build artifacts only.

Dependencies and integration points: mirrors `clients/Kconfig` and the internal helper declarations in `drm_client_internal.h`.

Risks: object inclusion must stay synchronized with config guards in the internal header. Missing include path would break access to `drm_draw_internal.h`/DRM internals used by `drm_log.c`.

Test signals: builds for `DRM_CLIENT_LIB=m/y`, with and without `DRM_CLIENT_LOG` and `DRM_FBDEV_EMULATION`, and module symbol availability for exported setup functions.
