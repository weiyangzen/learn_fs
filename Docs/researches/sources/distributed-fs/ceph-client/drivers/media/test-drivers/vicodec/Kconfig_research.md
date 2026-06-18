# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vicodec/Kconfig

Purpose: Kconfig definition for the virtual codec driver.

Important APIs/types/functions: defines `CONFIG_VIDEO_VICODEC` as a tristate "Virtual Codec Driver". It selects `VIDEOBUF2_VMALLOC`, `V4L2_MEM2MEM_DEV`, and `MEDIA_CONTROLLER`.

Control flow: when enabled, it builds a virtual memory-to-memory codec that exposes stateful encoder, stateful decoder, and stateless decoder behavior implemented in the vicodec sources.

State and persistence: build-time only.

Dependencies and integration points: depends on `VIDEO_DEV`; selected symbols provide vb2 vmalloc buffers, V4L2 mem2mem scheduling, and media-controller integration expected by `vicodec-core.c`.

Risks: omitting selected dependencies would break compilation or runtime registration. The help text positions the driver as a test/reference device and recommends `N` for normal systems.

Test signals: Kconfig dependency resolution, module build as `m`, built-in build as `y`, and V4L2 compliance once loaded.
