# sources/distributed-fs/ceph-client/include/uapi/drm/virtgpu_drm.h

## Purpose
This header defines the virtio-gpu DRM UAPI used by virtual GPU stacks such as virgl, venus, gfxstream, and cross-domain resource sharing. It covers resource creation, host transfers, command submission, fence fd and syncobj synchronization, capset queries, blob resources, host-visible memory, context initialization, and fence-signaled events.

## Important APIs and types
Core ioctls include `MAP`, `EXECBUFFER`, `GETPARAM`, `RESOURCE_CREATE`, `RESOURCE_INFO`, `TRANSFER_FROM_HOST`, `TRANSFER_TO_HOST`, `WAIT`, `GET_CAPS`, `RESOURCE_CREATE_BLOB`, and `CONTEXT_INIT`. `drm_virtgpu_execbuffer` carries flags, command pointer/size, BO handle array, fence fd in/out, ring index, and arrays of timeline-capable syncobjs. `drm_virtgpu_resource_create` describes classic 3D resources with target/format/bind/dimensions/levels/samples/stride. Transfer structs identify BO handles and 3D boxes. `drm_virtgpu_get_caps` fetches capsets such as VIRGL, VIRGL2, GFXSTREAM Vulkan, Venus, cross-domain, and DRM. `drm_virtgpu_resource_create_blob` adds guest, host3D, and host3D_guest blob memory with mappable/shareable/cross-device flags and optional creation command payload. `drm_virtgpu_context_init` passes context parameters such as capset ID, ring count, poll rings, and debug name.

## Control flow and state
Userspace queries feature params, initializes a context if supported, creates resources or blobs, maps host-visible resources when allowed, submits encoded host commands through execbuffer, performs explicit transfers to/from host for non-coherent resources, waits on resources, and queries capsets to size userspace protocol structures. Fence fd flags import/export native fences, while syncobj arrays provide more expressive wait/signal dependencies.

## State and persistence behavior
BO handles and resource handles persist as guest kernel objects tied to host resources. Blob IDs and host-visible mappings can represent host or cross-device shared state. Context parameters persist for the DRM context and influence command routing/rings/events. Fence fd and syncobj state persists outside individual ioctls and can be shared with other subsystems.

## Dependencies and integration points
The header depends on `drm.h`, virtio-gpu host protocols, DRM GEM, dma-fence fd synchronization, DRM syncobjs/timeline syncobjs, virglrenderer/Venus/gfxstream capsets, and host memory/resource transfer mechanisms. Userspace must respect advertised params before using blob, host-visible, cross-device, or context-init paths.

## Risks and test signals
Risks include host command buffer validation, capset size/version mismatches, resource transfer bounds, blob flag combinations, cross-device sharing security, ring index validation, fence fd leaks, and syncobj stride/count mistakes. Tests should cover every `GETPARAM` gate, classic and blob resource creation, map/resource-info behavior, transfer box bounds, execbuffer with fence fd in/out and ring index, timeline syncobjs, context debug-name params, capset query sizes, and event delivery for poll rings.
