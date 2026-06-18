<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h

## Purpose
`xe_exec.h` is the declaration header for user GPU command submission.

## Important APIs, types, and functions
It forward-declares `struct drm_device` and `struct drm_file`, and declares `int xe_exec_ioctl(struct drm_device *dev, void *data, struct drm_file *file);`.

## Control flow and integration points
There is no header-local control flow. DRM ioctl dispatch includes this function to handle user exec submissions. The implementation coordinates VM locking, sync parsing, job creation, and backend scheduling.

## State and persistence behavior
The header owns no state. The declared ioctl mutates VM fences, queue last fences, scheduler jobs, and user synchronization objects.

## Dependencies, risks, and test signals
Dependencies are DRM ioctl wiring and type declarations. Risks are signature mismatch with the ioctl table. Test signals are driver build and exec ioctl smoke/stress tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_exec.h -->
