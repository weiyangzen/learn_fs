<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c

## Purpose
`virtgpu_ioctl.c` implements most userspace VirtIO GPU ioctls: map, getparam, resource create/info, 3D transfers, wait, capset query, blob resource creation, context initialization, and ioctl table registration.

## Important APIs, Types, and Functions
Important functions are `virtio_gpu_create_context()`, `virtio_gpu_map_ioctl()`, `virtio_gpu_getparam_ioctl()`, `virtio_gpu_resource_create_ioctl()`, transfer ioctls, `virtio_gpu_wait_ioctl()`, `virtio_gpu_get_caps_ioctl()`, `verify_blob()`, `virtio_gpu_resource_create_blob_ioctl()`, and `virtio_gpu_context_init_ioctl()`. The execbuffer ioctl is declared in `virtgpu_submit.c` but registered here.

## Control Flow
Getparam copies negotiated feature values to userspace. Resource create validates 2D-only constraints without virgl, allocates a fence, creates a host resource/GEM object, creates a handle, and returns resource/BO handles. Transfers look up object arrays, validate blob/stride rules, optionally create context and fences, enqueue host transfer commands, and notify. Get caps validates capset/version, reuses or fetches a cached capset, waits for response validity, then copies caps to userspace. Blob creation validates feature/flag/memory combinations, optionally submits host3D creation command data, creates guest or VRAM object, assigns UUID for cross-device use, and returns handles. Context init copies parameter array, validates capset/ring/mask/debug-name uniqueness, allocates fence contexts, creates the host context, and notifies.

## State and Persistence Behavior
The file mutates per-file `virtio_gpu_fpriv` context state, per-device capset cache, object/blob UUID state, and host resources. Userspace handles persist in DRM GEM tables; cap caches persist until release; submitted commands complete asynchronously through virtqueues/fences.

## Dependencies and Integration Points
It depends on UAPI `virtgpu_drm.h`, sync files, usercopy, DRM syncobj indirectly through submit, GEM objects, VirtIO GPU command helpers, response waitqueues, and feature flags initialized in KMS.

## Risks
Userspace input validation is extensive and security-sensitive: flags, sizes, capset IDs, ring masks, blob memory modes, and user pointers must be exact. `num_params * sizeof(...)` can overflow if type sizes change, though `num_params > 4` is checked after computing `len`. Resource creation error paths using `drm_gem_object_release()` need lifecycle scrutiny. Capset waits can time out and return `-EBUSY`.

## Test Signals
DRM ioctl fuzzing, getparam matrix tests, resource create invalid 2D/3D fields, blob flag/memory combinations, context-init duplicate and ring-mask cases, capset cache/timeouts, transfer stride/blob validation, and wait ioctl nowait/blocking behavior are key.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/virtio/virtgpu_ioctl.c -->
