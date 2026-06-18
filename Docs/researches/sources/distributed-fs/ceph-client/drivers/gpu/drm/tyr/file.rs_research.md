<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs

Purpose: Defines per-open DRM file data and implements the Panthor-compatible device-query ioctl for Tyr.

Important APIs/types/functions: `TyrDrmFileData` is an empty per-file struct. `impl drm::file::DriverFile` allocates it on open. `TyrDrmFileData::dev_query()` handles `DRM_PANTHOR_DEV_QUERY_GPU_INFO`; with `pointer == 0` it returns the required size, otherwise it writes `ddev.gpu_info` to the user pointer via `UserSlice`.

Control flow: Open allocates pinned file data. The ioctl validates query type, either reports size or copies the stored GPU info. Unknown query types return `EINVAL`.

State and persistence: Per-file state is currently empty; query data is read from the DRM device's stored `GpuInfo`.

Dependencies and integration points: Integrates Rust DRM file abstractions, UAPI Panthor structs, and safe user-copy helpers. It is registered by `driver.rs`.

Risks and test signals: Risks include not validating that user-provided size is sufficient before writing and only supporting one query type. Test with zero pointer size queries, valid copyout, invalid query type, too-small user buffers, and repeated opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/file.rs -->
