<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c

## Purpose
`virtgpu_submit.c` implements `VIRTGPU_EXECBUFFER` submission parsing for virgl contexts, including command buffer copy, BO list lookup/locking, in-fence waits, syncobj timeline dependencies, out-fence fd creation, DRM fence events, command submission, and cleanup.

## Important APIs, Types, and Functions
The public function is `virtio_gpu_execbuffer_ioctl()`. Internal state is `struct virtio_gpu_submit` and `struct virtio_gpu_submit_post_dep`. Important helpers include `virtio_gpu_parse_deps()`, `virtio_gpu_parse_post_deps()`, `virtio_gpu_process_post_deps()`, `virtio_gpu_fence_event_create()`, `virtio_gpu_init_submit_buflist()`, `virtio_gpu_init_submit()`, `virtio_gpu_wait_in_fence()`, `virtio_gpu_lock_buflist()`, and cleanup/complete helpers.

## Control Flow
The ioctl requires virgl, validates flags and optional ring index against per-file context init, creates a context if needed, initializes submit state and optional out fence/event/fd, copies BO handles and command buffer from userspace, parses output syncobjs, waits and optionally records resettable input syncobjs, waits input fence fd, locks BO reservations, submits the command through `virtio_gpu_cmd_submit()`, notifies the host, installs the out fence fd, updates output syncobjs/timeline points, marks transferred ownership, and runs cleanup for remaining local references.

## State and Persistence Behavior
Submission state is transient. Host command execution and dma-fence completion persist asynchronously. Syncobjs are reset on cleanup after successful dependency parsing, and output syncobjs receive the submitted fence. Per-file ring fence contexts persist in `virtio_gpu_fpriv`.

## Dependencies and Integration Points
The file depends on DRM syncobj/timeline APIs, sync_file, dma-fence unwrap/wait, GEM object arrays from `virtgpu_gem.c`, command transport, UAPI execbuffer flags, and context/ring state initialized by context-init ioctl.

## Risks
Cleanup unconditionally resets parsed input syncobjs, so error ordering must match UAPI expectations. Out-fence allocation is conditional on several flags; callers expecting synchronization must request it or provide BO handles/syncobjs. Waiting foreign fences in ioctl can block. Ring-index event logic depends on `ring_idx_mask` semantics. User-provided strides are used with bounded copy but must remain validated by UAPI flag masks.

## Test Signals
Tests should cover invalid flags/rings, command copy faults, missing BO handles, reservation lock failures, in-fence fd waits, input syncobj reset behavior on success/failure, output syncobj timeline points, out-fence fd installation, DRM fence event delivery, and multi-ring submissions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_submit.c -->
