# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/amdxdna_ubuf.h

Purpose: declares the AMD XDNA user-buffer dma-buf export helper.

Important API: `amdxdna_get_ubuf(struct drm_device *dev, u32 num_entries, void __user *va_entries)` takes a DRM device, a count of user VA entries, and a pointer to the entry array, returning a dma-buf or ERR_PTR.

Control flow: AMD XDNA GEM creation includes this header when handling create-BO requests backed by user virtual addresses. The helper returns a dma-buf that is imported through the normal prime-import path.

State and persistence: no header-owned state; implementation-owned pinned pages persist in the returned dma-buf until release.

Dependencies: DRM device and Linux dma-buf declarations.

Risks: callers must validate the surrounding UAPI table enough to pass the correct entry pointer and count. Returned dma-bufs hold long-term user page pins.

Test signals: compile integration with GEM, error pointer handling, and create-BO userptr coverage.
