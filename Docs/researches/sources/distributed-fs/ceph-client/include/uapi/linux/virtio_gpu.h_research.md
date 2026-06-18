# sources/distributed-fs/ceph-client/include/uapi/linux/virtio_gpu.h

Purpose: defines the virtio GPU device ABI for 2D scanout, cursor updates, 3D/Virgl contexts, capsets, EDID, resource UUIDs, blob resources, host-visible shared memory, and resource mapping.

Important APIs/types/functions: feature bits include VIRGL, EDID, RESOURCE_UUID, RESOURCE_BLOB, and CONTEXT_INIT. `virtio_gpu_ctrl_type` enumerates 2D commands, 3D commands, cursor commands, success responses, and error responses. Shared memory IDs include host-visible blob memory. Common command header `virtio_gpu_ctrl_hdr` carries type, flags, fence ID, context ID, and optional ring index. Other key structs include cursor position/update, rectangles, 2D and 3D resource creation, scanout setup, flush/transfer commands, backing memory entries, display info response, 3D context/resource/submit commands, capset queries/responses, EDID response, config events, resource UUID response, blob create/set-scanout/map/unmap commands, and map info response. Format enums define common framebuffer formats.

Control flow: the driver negotiates features, reads `virtio_gpu_config` for scanout/capset counts and display events, queries display info, creates resources, attaches guest memory backing, transfers data to/from host, sets scanout, flushes rectangles, and handles cursor commands on the cursor queue. 3D flow creates a context, attaches resources, submits command buffers, and queries capsets. Blob flow creates resources with guest/host memory modes, optionally maps/unmaps host-visible blobs, and can set scanout from blob resources. Fences in the common header order asynchronous completion.

State and persistence: device state includes scanout configuration, resources and attached backing memory, contexts, capsets, fences, display event bits, EDID blobs, UUIDs, blob map state, and cursor position/resource. Resources persist until unref/detach/reset; config events persist in `events_read` until cleared via `events_clear`.

Dependencies and integration: includes `linux/types.h`. It integrates with virtio transport, DRM virtio-gpu driver, framebuffer console, Mesa/Virgl/Venus/gfxstream userspace, dma-buf/resource sharing, EDID consumers, and VMM GPU backends.

Risks: resource IDs and context IDs are guest-selected but device-validated; stale or duplicate IDs return protocol errors. Backing memory entries are guest physical addresses/lengths and require correct DMA mapping. Fence/ring-index behavior depends on feature negotiation. Blob mapping cache mode must be honored by the guest. Scanout dimensions, strides, offsets, and formats must match resource layout or display corruption follows.

Test signals: 2D boot/fbcon tests, display-info and EDID tests, resource create/attach/transfer/flush/unref tests, cursor move/update tests, Virgl/capset rendering tests, blob map/unmap tests, fence ordering tests, display hotplug event tests, and ABI layout checks.
