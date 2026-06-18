# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gvt/dmabuf.h

Purpose: declares the GVT DMA-BUF plane-export data structures and public query/get/cleanup APIs.

Important APIs/types/functions: `struct intel_vgpu_fb_info` records guest framebuffer start GMA/GPA, DRM format and modifier, width, height, stride, size, cursor position/hotspot, and owning DMA-BUF object. `struct intel_vgpu_dmabuf_obj` records the owning vGPU, framebuffer info, `dmabuf_id`, kref, initial-reference flag, and list node. Public functions are `intel_vgpu_query_plane()`, `intel_vgpu_get_dmabuf()`, and `intel_vgpu_dmabuf_cleanup()`.

Control flow and state: no executable logic. The structures define the persistent bridge between VFIO plane queries and later fd export. Query creates or reuses `intel_vgpu_dmabuf_obj`; get converts it to a GEM/PRIME DMA-BUF; cleanup detaches list/IDR state when the vGPU is destroyed.

Dependencies and integration points: depends on Linux kref/list types, VFIO-facing implementation in `dmabuf.c`, GVT framebuffer decoders, and i915 GEM PRIME. Consumers use `dmabuf_id` as the handoff token between query and get ioctls.

Risks and test signals: lifetime is subtle because exported DMA-BUFs can outlive the vGPU; `vgpu` may become NULL and cleanup must handle orphaned objects. Test signals include correct kref behavior across query/get/close, stable metadata copied in `intel_vgpu_fb_info`, cursor hotspot sentinel handling, and no IDR/list leaks after cleanup.
