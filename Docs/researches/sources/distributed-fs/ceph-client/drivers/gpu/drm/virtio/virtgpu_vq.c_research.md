# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_vq.c

## Purpose

`virtgpu_vq.c` is the virtio-gpu command transport layer. It allocates command buffers, submits scatter-gather descriptors to the control and cursor virtqueues, handles responses asynchronously from workqueue callbacks, emits fences, manages resource lifecycle commands, and exposes panic-path helpers for minimal framebuffer updates during `drm_panic`.

## Important APIs, types, and functions

The central local type is `struct virtio_gpu_vbuffer`, allocated from the `vgdev->vbufs` kmem cache by `virtio_gpu_alloc_vbufs()`, `virtio_gpu_get_vbuf()`, and panic-specific `virtio_gpu_panic_get_vbuf()`. Public command helpers include resource creation/destruction, scanout programming, 2D/3D transfers, context management, command submission, object attach/detach, cursor updates, UUID assignment, blob map/unmap, blob creation, and `SET_SCANOUT_BLOB`.

Queueing is handled by `virtio_gpu_queue_ctrl_sgs()`, `virtio_gpu_queue_fenced_ctrl_buffer()`, `virtio_gpu_queue_ctrl_buffer()`, `virtio_gpu_queue_cursor()`, and the panic variants. `virtio_gpu_dequeue_ctrl_func()` and `virtio_gpu_dequeue_cursor_func()` drain completed virtqueue buffers. Response callbacks update display modes, capset metadata/cache entries, EDID objects, object UUID state, and VRAM map state.

## Control flow and state

Command helpers allocate a vbuffer, fill little-endian virtio-gpu command structs, optionally attach outgoing data (`data_buf`, `data_size`) and object arrays, then submit descriptors. Control-queue submission waits for space under `ctrlq.qlock`, emits a fence only once the vbuffer position is known, adds fences to object reservations, records a sequence number, and increments `pending_commands`. `virtio_gpu_notify()` batches kicks by clearing `pending_commands` and calling `virtqueue_kick_prepare()`/`virtqueue_notify()`.

Completion flows from virtqueue callbacks `virtio_gpu_ctrl_ack()` and `virtio_gpu_cursor_ack()` into scheduled work. The control worker disables callbacks, reclaims all buffers, processes error/fence flags, invokes response callbacks, wakes queue waiters, frees object arrays later, and releases buffers. The cursor worker only traces and frees cursor vbuffers, then wakes waiters.

## Persistence and integration

The file mutates persistent in-memory driver state: scanout info, EDID pointers, capset cache entries, object `created`/`attached` flags, UUID states, VRAM `map_state`/`map_info`, queue sequence numbers, and wake queues. It integrates with virtio core, DRM EDID/KMS hotplug helpers, dma-mapping, GEM object arrays, virtio-gpu fences, blob resources, and tracepoints in `virtgpu_trace.h`.

## Risks and test signals

Key risks are queue-space deadlock, missed notifications, response callback races, stale object arrays, DMA sync errors for shmem transfers, scatterlist construction for vmalloc data, and panic-path GFP_ATOMIC assumptions. Error responses are ratelimited but many command helpers do not propagate queueing failures to callers. Test signals are mostly integration-level: boot/probe, resource creation, display hotplug/EDID, virgl/capset queries, PRIME UUID export, host-visible blob mmap, cursor movement, and panic display paths.
