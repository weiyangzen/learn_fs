# sources/distributed-fs/ceph-client/drivers/media/platform/renesas/vsp1/vsp1_drm.h

Purpose: declares the private DRM/DU integration state for VSP1 display pipelines.

Important APIs and types: `struct vsp1_drm_pipeline` wraps a generic `vsp1_pipeline`, one cached partition, output width/height, BRx release coordination, optional UIF entity, CRC configuration, and DU completion callback/private data. `struct vsp1_drm` contains per-LIF pipelines, a mutex protecting BRU/BRS allocation, and per-RPF input crop/compose/zpos/color state. `to_vsp1_drm_pipeline()` converts from generic pipeline to DRM wrapper. `vsp1_drm_init()` and `vsp1_drm_cleanup()` are local lifecycle APIs.

Control flow role: `vsp1_drv.c` calls init/cleanup for non-UAPI display-oriented VSP instances. `vsp1_drm.c` fills and consumes the structures during DU setup and atomic updates.

State and persistence: this header defines the persistent state that survives across DRM atomic commits: selected output geometry, current input rectangles, z-order, color metadata, callback, CRC source, and BRx ownership flags.

Dependencies and integration: includes Linux mutex/wait/V4L2 types, the external media VSP1 API for DU config structures, and `vsp1_pipe.h`.

Risks and test signals: structure changes can break assumptions in both pipeline configuration and frame-end callbacks. Test dual-LIF devices, CRC toggling, writeback, disabled-input transitions, and concurrent atomic commits serialized by the DRM lock.
